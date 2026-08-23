#!/usr/bin/env python3
"""Install or remove selected lifecycle host projections safely."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

LIFECYCLE_ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = LIFECYCLE_ROOT / "MANIFEST.json"
RECEIPT_PATH = LIFECYCLE_ROOT / "INSTALLATION_RECEIPT.json"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _parent_conflict(target: Path, project_root: Path) -> bool:
    parent = target.parent
    while parent != project_root:
        if parent.exists() and not parent.is_dir():
            return True
        parent = parent.parent
    return False


def _projection_state(project_root: Path, projection: dict[str, Any]) -> dict[str, Any]:
    source = (project_root / str(projection["source"])).resolve()
    target = (project_root / str(projection["target"])).resolve()
    if not _inside(source, project_root) or not _inside(target, project_root):
        raise ValueError("projection escapes project root")
    expected = str(projection["sha256"])
    observed_source = _sha256_bytes(source.read_bytes())
    if observed_source != expected:
        raise ValueError(f"source hash mismatch: {projection['source']}")
    if _parent_conflict(target, project_root):
        state = "conflict"
        observed_target = None
    elif not target.exists():
        state = "absent"
        observed_target = None
    elif not target.is_file():
        state = "conflict"
        observed_target = None
    else:
        observed_target = _sha256_bytes(target.read_bytes())
        state = "identical" if observed_target == expected else "conflict"
    return {**projection, "state": state, "observed_target_sha256": observed_target}


def inspect(project_root: Path) -> dict[str, Any]:
    manifest = _load_json(MANIFEST_PATH)
    states = [_projection_state(project_root, item) for item in manifest.get("projections", [])]
    conflicts = [item["target"] for item in states if item["state"] == "conflict"]
    return {
        "schema": "repokernel.project-lifecycle-install-check.v1",
        "status": "blocked_conflict" if conflicts else ("already_installed" if states and all(item["state"] == "identical" for item in states) else "ready_to_install"),
        "project_root": str(project_root),
        "host_projections": manifest.get("host_projections", []),
        "projections": states,
        "conflicts": conflicts,
        "writes_performed": [],
    }


def _write_receipt(value: dict[str, Any]) -> None:
    RECEIPT_PATH.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _ensure_parent(target: Path, project_root: Path) -> list[Path]:
    missing: list[Path] = []
    parent = target.parent
    while parent != project_root and not parent.exists():
        missing.append(parent)
        parent = parent.parent
    if parent.exists() and not parent.is_dir():
        raise NotADirectoryError(parent)
    created: list[Path] = []
    for directory in reversed(missing):
        directory.mkdir()
        created.append(directory)
    return created


def _relative(path: Path, project_root: Path) -> str:
    return path.relative_to(project_root).as_posix()


def _remove_empty_directories(paths: list[Path], project_root: Path) -> tuple[list[str], list[str]]:
    removed: list[str] = []
    preserved: list[str] = []
    for path in sorted(set(paths), key=lambda item: len(item.parts), reverse=True):
        if not _inside(path, project_root) or path == project_root:
            raise ValueError("receipt directory escapes project root")
        if not path.exists():
            continue
        try:
            path.rmdir()
            removed.append(_relative(path, project_root))
        except OSError:
            preserved.append(_relative(path, project_root))
    return removed, preserved


def install(project_root: Path) -> dict[str, Any]:
    check = inspect(project_root)
    if check["conflicts"]:
        return check
    try:
        previous = _load_json(RECEIPT_PATH)
    except (OSError, ValueError, json.JSONDecodeError):
        previous = {}
    previously_created = {
        item.get("path"): item
        for item in previous.get("created", [])
        if previous.get("status") == "installed" and isinstance(item, dict)
    }
    previously_created_directories = [
        str(item)
        for item in previous.get("created_directories", [])
        if previous.get("status") == "installed" and isinstance(item, str)
    ]
    created: list[dict[str, str]] = []
    created_directories = list(previously_created_directories)
    writes_performed: list[str] = []
    directories_created_this_run: list[Path] = []
    files_written_this_run: list[dict[str, str]] = []
    unchanged: list[str] = []
    try:
        for item in check["projections"]:
            target = (project_root / item["target"]).resolve()
            if item["state"] == "identical":
                prior = previously_created.get(item["target"])
                if isinstance(prior, dict) and prior.get("sha256") == item["sha256"]:
                    created.append({"path": item["target"], "sha256": item["sha256"]})
                else:
                    unchanged.append(item["target"])
                continue
            source = (project_root / item["source"]).resolve()
            new_directories = _ensure_parent(target, project_root)
            directories_created_this_run.extend(new_directories)
            created_directories.extend(_relative(path, project_root) for path in new_directories)
            temporary = target.with_name(target.name + ".repokernel-new")
            try:
                temporary.write_bytes(source.read_bytes())
                os.replace(temporary, target)
            finally:
                if temporary.exists():
                    temporary.unlink()
            record = {"path": item["target"], "sha256": item["sha256"]}
            created.append(record)
            files_written_this_run.append(record)
            writes_performed.append(item["target"])
    except Exception:
        for item in reversed(files_written_this_run):
            target = (project_root / item["path"]).resolve()
            if target.is_file() and _sha256_bytes(target.read_bytes()) == item["sha256"]:
                target.unlink()
        _remove_empty_directories(directories_created_this_run, project_root)
        raise
    receipt = {
        "schema": "repokernel.project-lifecycle-installation-receipt.v1",
        "status": "installed",
        "project_root": str(project_root),
        "host_projections": check.get("host_projections", []),
        "created": created,
        "created_directories": sorted(set(created_directories)),
        "writes_performed": writes_performed,
        "left_unchanged_identical": unchanged,
        "conflicts": [],
        "activation_status": "pending_fresh_host_behavioral_test",
        "rollback_command": "python .repokernel/lifecycle/install.py --project-root . --uninstall",
    }
    _write_receipt(receipt)
    return receipt


def uninstall(project_root: Path) -> dict[str, Any]:
    receipt = _load_json(RECEIPT_PATH)
    if receipt.get("status") != "installed":
        return {"schema": "repokernel.project-lifecycle-uninstall-receipt.v1", "status": "nothing_to_uninstall", "removed": [], "preserved": [], "removed_directories": [], "preserved_directories": []}
    removed: list[str] = []
    preserved: list[str] = []
    for item in receipt.get("created", []):
        target = (project_root / str(item["path"])).resolve()
        if not _inside(target, project_root):
            raise ValueError("receipt target escapes project root")
        if target.is_file() and _sha256_bytes(target.read_bytes()) == item["sha256"]:
            target.unlink()
            removed.append(item["path"])
        elif target.exists():
            preserved.append(item["path"])
    directory_paths = [
        (project_root / item).resolve()
        for item in receipt.get("created_directories", [])
        if isinstance(item, str)
    ]
    removed_directories, preserved_directories = _remove_empty_directories(directory_paths, project_root)
    result = {
        "schema": "repokernel.project-lifecycle-uninstall-receipt.v1",
        "status": "uninstalled" if not preserved and not preserved_directories else "partial_preserved_target_content",
        "project_root": str(project_root),
        "removed": removed,
        "preserved": preserved,
        "removed_directories": removed_directories,
        "preserved_directories": preserved_directories,
    }
    _write_receipt({**result, "created": [], "created_directories": [], "activation_status": "not_installed"})
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--install", action="store_true")
    action.add_argument("--uninstall", action="store_true")
    args = parser.parse_args(argv)
    root = args.project_root.resolve()
    expected_lifecycle = (root / ".repokernel" / "lifecycle").resolve()
    if expected_lifecycle != LIFECYCLE_ROOT.resolve():
        raise ValueError("installer must run from the selected Project Kernel root")
    result = inspect(root) if args.check else (install(root) if args.install else uninstall(root))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 2 if result.get("status") == "blocked_conflict" else 0


if __name__ == "__main__":
    raise SystemExit(main())
