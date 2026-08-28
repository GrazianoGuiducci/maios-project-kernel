#!/usr/bin/env python3
"""Canonical deterministic MAIOS Project Kernel install lifecycle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


PLAN_SCHEMA = "maios.install-plan.v2"
RECEIPT_SCHEMA = "maios.installation-receipt.v2"
UNINSTALL_SCHEMA = "maios.uninstall-receipt.v2"
PENDING_SCHEMA = "maios.pending-installation.v2"


class InstallerError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InstallerError(f"cannot read valid JSON: {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.maios-tmp-{os.getpid()}")
    try:
        temporary.write_text(
            json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def rendered_host_state(root: Path, host: str) -> bytes:
    state = read_json(root / "payload" / ".maios" / "state" / "HOST_STATE.json")
    state["selected_adapter"] = host
    state["installation_state"] = "installed_files_unverified_by_host"
    return (
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def safe_relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or ".." in path.parts
        or "\\" in value
        or ":" in value
        or "\x00" in value
    ):
        raise InstallerError(f"unsafe package path: {value}")
    return path


def native(root: Path, relative: str) -> Path:
    return root.joinpath(*safe_relative(relative).parts)


def distribution_root() -> Path | None:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "MANIFEST.json").is_file() and (parent / "payload").is_dir():
            return parent
    return None


def verified_inventory_rows(root: Path) -> list[dict[str, Any]]:
    inventory = read_json(root / "PACKAGE_INVENTORY.json")
    if inventory.get("schema") != "maios.package-inventory.v2":
        raise InstallerError("unsupported package inventory schema")
    if inventory.get("algorithm") != "sha256":
        raise InstallerError("unsupported package inventory algorithm")

    rows = inventory.get("files")
    if not isinstance(rows, list):
        raise InstallerError("package inventory files must be a list")
    declared: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise InstallerError("package inventory contains an invalid row")
        relative = row["path"]
        safe_relative(relative)
        if relative == "PACKAGE_INVENTORY.json" or relative in declared:
            raise InstallerError(f"invalid or duplicate inventory path: {relative}")
        if not isinstance(row.get("bytes"), int) or not isinstance(row.get("sha256"), str):
            raise InstallerError(f"package inventory metadata is invalid: {relative}")
        declared[relative] = row

    actual: dict[str, Path] = {}
    for path in sorted(
        root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()
    ):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise InstallerError(f"package distribution contains a symlink: {relative}")
        if path.is_file() and relative != "PACKAGE_INVENTORY.json":
            actual[relative] = path
    if set(actual) != set(declared):
        missing = sorted(set(declared) - set(actual))
        unexpected = sorted(set(actual) - set(declared))
        raise InstallerError(
            f"package distribution differs from inventory; missing={missing}; unexpected={unexpected}"
        )
    for relative, row in declared.items():
        source = actual[relative]
        if source.stat().st_size != row["bytes"] or digest_file(source) != row["sha256"]:
            raise InstallerError(f"package inventory digest mismatch: {relative}")
    return [declared[key] for key in sorted(declared)]


def package_identity(root: Path) -> dict[str, Any]:
    manifest_path = root / "MANIFEST.json"
    inventory_path = root / "PACKAGE_INVENTORY.json"
    manifest = read_json(manifest_path)
    verified_inventory_rows(root)
    return {
        "product": manifest.get("product"),
        "version": manifest.get("version"),
        "manifest_sha256": digest_file(manifest_path),
        "inventory_sha256": digest_file(inventory_path),
        "source_identity": manifest.get("source_identity"),
    }


def adapter_projection(root: Path, host: str) -> list[dict[str, str]]:
    adapters = read_json(root / "adapters" / "ADAPTERS.json")
    by_id = {item["id"]: item for item in adapters.get("adapters", [])}
    if host not in by_id:
        raise InstallerError(f"unsupported host adapter: {host}")
    return list(by_id[host].get("projections", []))


def source_entries(root: Path, host: str) -> list[dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    payload_rows = [
        row for row in verified_inventory_rows(root) if row["path"].startswith("payload/")
    ]
    for row in payload_rows:
        source_rel = row["path"]
        source = native(root, source_rel)
        destination = source_rel.removeprefix("payload/")
        if not destination:
            raise InstallerError("package inventory contains an empty payload path")
        render: dict[str, str] | None = None
        if destination == ".maios/state/HOST_STATE.json":
            data = rendered_host_state(root, host)
            render = {"type": "host_state", "host": host}
        else:
            data = source.read_bytes()
        entries[destination] = {
            "source": source_rel,
            "destination": destination,
            "sha256": digest_bytes(data),
            "bytes": len(data),
            "kind": "host_state_projection" if render else "payload",
        }
        if render:
            entries[destination]["render"] = render
    for projection in adapter_projection(root, host):
        source_rel = projection["source"]
        destination = projection["destination"]
        safe_relative(source_rel)
        safe_relative(destination)
        source = native(root, source_rel)
        if not source.is_file():
            raise InstallerError(f"adapter source is missing: {source_rel}")
        data = source.read_bytes()
        candidate = {
            "source": source_rel,
            "destination": destination,
            "sha256": digest_bytes(data),
            "bytes": len(data),
            "kind": "host_projection",
        }
        existing = entries.get(destination)
        if existing and existing["sha256"] != candidate["sha256"]:
            raise InstallerError(f"adapter destination collision: {destination}")
        entries[destination] = candidate
    return [entries[key] for key in sorted(entries)]


def target_snapshot(
    target: Path, relevant_paths: Iterable[str] | None = None
) -> dict[str, Any]:
    if not target.exists():
        return {"state": "absent", "digest": digest_bytes(b"absent")}
    if not target.is_dir():
        return {"state": "not_directory", "digest": digest_bytes(b"not_directory")}
    rows: list[dict[str, Any]] = []
    if relevant_paths is None:
        paths = sorted(
            target.rglob("*"), key=lambda item: item.relative_to(target).as_posix()
        )
        scope = "whole_target"
    else:
        paths = [native(target, relative) for relative in sorted(set(relevant_paths))]
        scope = "projected_paths"
    for path in paths:
        relative = path.relative_to(target)
        if ".git" in relative.parts:
            continue
        if path.is_symlink():
            rows.append({"path": relative.as_posix(), "kind": "symlink"})
        elif path.is_file():
            rows.append(
                {
                    "path": relative.as_posix(),
                    "kind": "file",
                    "sha256": digest_file(path),
                    "bytes": path.stat().st_size,
                }
            )
        elif path.is_dir():
            rows.append({"path": relative.as_posix(), "kind": "directory"})
        else:
            rows.append({"path": relative.as_posix(), "kind": "absent"})
    return {
        "state": "directory",
        "scope": scope,
        "entries": rows,
        "digest": digest_bytes(canonical_bytes(rows)),
    }


def has_unsafe_ancestor(target: Path, destination: str) -> bool:
    current = target
    for part in safe_relative(destination).parts[:-1]:
        current = current / part
        if current.exists() and current.is_symlink():
            return True
    return False


def current_receipt(target: Path) -> dict[str, Any] | None:
    target = target.resolve()
    path = target / ".maios" / "receipts" / "install" / "CURRENT.json"
    if (
        has_unsafe_ancestor(target, ".maios/receipts/install/CURRENT.json")
        or path.is_symlink()
        or not path.is_file()
    ):
        return None
    try:
        value = read_json(path)
        require_receipt_target(target, value)
    except InstallerError:
        return None
    return value


def plan_digest(plan: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in plan.items() if key != "plan_digest"}
    return digest_bytes(canonical_bytes(unsigned))


def make_plan(root: Path, target: Path, mode: str, host: str) -> dict[str, Any]:
    root = root.resolve()
    if target.expanduser().is_symlink():
        raise InstallerError("target root must not be a symlink")
    target = target.resolve()
    identity = package_identity(root)
    entries = source_entries(root, host)
    creates: list[str] = []
    identical: list[str] = []
    conflicts: list[dict[str, str]] = []

    for entry in entries:
        destination = entry["destination"]
        target_path = native(target, destination)
        if has_unsafe_ancestor(target, destination):
            conflicts.append({"path": destination, "reason": "symlink_ancestor"})
        elif target_path.is_symlink():
            conflicts.append({"path": destination, "reason": "symlink_target"})
        elif not target_path.exists():
            creates.append(destination)
        elif not target_path.is_file():
            conflicts.append({"path": destination, "reason": "non_file_collision"})
        elif digest_file(target_path) == entry["sha256"]:
            identical.append(destination)
        else:
            conflicts.append({"path": destination, "reason": "divergent_content"})

    snapshot = target_snapshot(
        target,
        None if mode == "new_repository" else [entry["destination"] for entry in entries],
    )

    prior = current_receipt(target)
    exact_prior = bool(
        prior
        and prior.get("package_identity") == identity
        and prior.get("host") == host
        and prior.get("mode") == mode
    )
    nonempty = snapshot.get("state") == "directory" and bool(snapshot.get("entries"))
    blocked_reasons: list[str] = []
    idempotent = exact_prior and not creates and not conflicts
    if mode == "new_repository" and nonempty and not idempotent:
        blocked_reasons.append("new_repository_target_is_not_empty")
    if snapshot.get("state") == "not_directory":
        blocked_reasons.append("target_is_not_a_directory")
    if conflicts:
        blocked_reasons.append("target_conflicts_present")
    if (target / ".maios" / "receipts" / "install" / "PENDING.json").is_file():
        blocked_reasons.append("pending_install_recovery_required")

    status = "idempotent" if idempotent else "ready"
    if blocked_reasons:
        status = "blocked"
    plan: dict[str, Any] = {
        "schema": PLAN_SCHEMA,
        "status": status,
        "mode": mode,
        "host": host,
        "target": str(target),
        "package_identity": identity,
        "target_snapshot": snapshot,
        "entries": entries,
        "creates": creates,
        "preserves_identical": identical,
        "conflicts": conflicts,
        "blocked_reasons": blocked_reasons,
        "backup_policy": (
            "backup_preexisting_identical_paths_then_no_overwrite"
            if mode == "existing_repository"
            else "not_needed_empty_target_atomic_install"
        ),
        "recovery_policy": "remove_only_installer_created_bytes_that_remain_identical",
        "global_writes": [],
    }
    plan["plan_digest"] = plan_digest(plan)
    return plan


def verify_plan(plan: dict[str, Any]) -> None:
    if plan.get("schema") != PLAN_SCHEMA:
        raise InstallerError("unsupported install plan schema")
    if plan.get("plan_digest") != plan_digest(plan):
        raise InstallerError("install plan digest mismatch")
    if plan.get("mode") not in {"new_repository", "existing_repository"}:
        raise InstallerError("unsupported install mode")


def copy_entry(root: Path, base: Path, entry: dict[str, Any]) -> None:
    destination = native(base, entry["destination"])
    if has_unsafe_ancestor(base, entry["destination"]) or destination.is_symlink():
        raise InstallerError(f"unsafe destination changed after preview: {entry['destination']}")
    render = entry.get("render")
    if isinstance(render, dict) and render.get("type") == "host_state":
        data = rendered_host_state(root, render["host"])
    else:
        source = native(root, entry["source"])
        if not source.is_file() or source.is_symlink():
            raise InstallerError(f"unsafe package source changed after preview: {entry['source']}")
        data = source.read_bytes()
    if digest_bytes(data) != entry["sha256"]:
        raise InstallerError(f"package source changed after preview: {entry['source']}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor: int | None = None
    try:
        descriptor = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
            0o644,
        )
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = None
            stream.write(data)
    except FileExistsError as exc:
        raise InstallerError(
            f"destination appeared after preview: {entry['destination']}"
        ) from exc
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if destination.is_file() and not destination.is_symlink():
            destination.unlink()
        raise
    if digest_file(destination) != entry["sha256"]:
        raise InstallerError(f"copied byte mismatch: {entry['destination']}")


def install_receipt(plan: dict[str, Any], state: str) -> dict[str, Any]:
    owned = [
        {
            "path": entry["destination"],
            "sha256": entry["sha256"],
            "bytes": entry["bytes"],
            "kind": entry["kind"],
        }
        for entry in plan["entries"]
        if entry["destination"] in plan["creates"]
    ]
    by_destination = {entry["destination"]: entry for entry in plan["entries"]}
    backup_root = (
        f".maios/backups/{plan['plan_digest']}"
        if plan["mode"] == "existing_repository"
        and plan["preserves_identical"]
        else None
    )
    backed_up = [
        {
            "path": f"{backup_root}/{relative}",
            "sha256": by_destination[relative]["sha256"],
            "source_path": relative,
        }
        for relative in plan["preserves_identical"]
        if backup_root is not None
    ]
    return {
        "schema": RECEIPT_SCHEMA,
        "state": state,
        "mode": plan["mode"],
        "host": plan["host"],
        "target": plan["target"],
        "plan_digest": plan["plan_digest"],
        "package_identity": plan["package_identity"],
        "installer_owned_files": owned,
        "preserved_preexisting_identical": plan["preserves_identical"],
        "backup_root": backup_root,
        "installer_owned_backup_files": backed_up,
        "global_writes": [],
        "behavior_claimed": False,
        "recovery": "run the installed .maios/installer/installer.py uninstall command",
    }


def backup_identical(target: Path, plan: dict[str, Any]) -> None:
    if plan["mode"] != "existing_repository" or not plan["preserves_identical"]:
        return
    backup = target / ".maios" / "backups" / plan["plan_digest"]
    for relative in plan["preserves_identical"]:
        source = native(target, relative)
        if has_unsafe_ancestor(target, relative) or source.is_symlink() or not source.is_file():
            raise InstallerError(f"pre-existing identical path changed after preview: {relative}")
        destination = native(backup, relative)
        if has_unsafe_ancestor(target, destination.relative_to(target).as_posix()):
            raise InstallerError(f"unsafe backup destination: {relative}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if not destination.is_file() or digest_file(destination) != digest_file(source):
                raise InstallerError(f"backup destination conflict: {relative}")
            continue
        shutil.copyfile(source, destination)


def pending_installation(plan: dict[str, Any]) -> dict[str, Any]:
    receipt = install_receipt(plan, "pending")
    return {
        "schema": PENDING_SCHEMA,
        "target": plan["target"],
        "plan_digest": plan["plan_digest"],
        "mode": plan["mode"],
        "host": plan["host"],
        "package_identity": plan["package_identity"],
        "installer_owned_files": receipt["installer_owned_files"],
        "installer_owned_backup_files": receipt["installer_owned_backup_files"],
        "global_writes": [],
        "recovery": "run recover-pending against the exact target",
    }


def apply_plan(root: Path, plan: dict[str, Any]) -> dict[str, Any]:
    verify_plan(plan)
    if plan.get("status") == "blocked":
        raise InstallerError("blocked install plan cannot be applied")
    target = Path(plan["target"]).resolve()
    current = make_plan(root, target, plan["mode"], plan["host"])
    if current["plan_digest"] != plan["plan_digest"]:
        raise InstallerError("target or package changed after preview; create a new plan")
    if current["status"] == "idempotent":
        receipt = current_receipt(target)
        if receipt is None:
            raise InstallerError("idempotent target has no valid current receipt")
        return receipt

    receipt_path = target / ".maios" / "receipts" / "install" / "CURRENT.json"
    if plan["mode"] == "new_repository":
        stage = target.parent / f".{target.name}.maios-stage-{plan['plan_digest'][:12]}"
        if stage.exists():
            raise InstallerError(f"attempt staging path already exists: {stage}")
        try:
            stage.mkdir(parents=True)
            for entry in plan["entries"]:
                copy_entry(root, stage, entry)
            receipt = install_receipt(plan, "installed")
            write_json(
                stage / ".maios" / "receipts" / "install" / "CURRENT.json",
                receipt,
            )
            if target.exists():
                if any(target.iterdir()):
                    raise InstallerError("new target became non-empty during apply")
                target.rmdir()
            os.replace(stage, target)
            return receipt
        except Exception:
            if stage.exists():
                shutil.rmtree(stage)
            raise

    target.mkdir(parents=True, exist_ok=True)
    pending_path = target / ".maios" / "receipts" / "install" / "PENDING.json"
    if has_unsafe_ancestor(target, ".maios/receipts/install/PENDING.json") or pending_path.is_symlink():
        raise InstallerError("unsafe pending receipt path")
    write_json(pending_path, pending_installation(plan))
    try:
        backup_identical(target, plan)
        for entry in plan["entries"]:
            if entry["destination"] not in plan["creates"]:
                continue
            copy_entry(root, target, entry)
        receipt = install_receipt(plan, "installed")
        if has_unsafe_ancestor(target, ".maios/receipts/install/CURRENT.json") or receipt_path.is_symlink():
            raise InstallerError("unsafe installation receipt path")
        write_json(receipt_path, receipt)
        if pending_path.is_file():
            pending_path.unlink()
        return receipt
    except Exception as exc:
        recovery = recover_pending(target)
        if not recovery["complete"]:
            raise InstallerError(
                f"install failed and automatic recovery preserved changed paths: {recovery['preserved_changed']}"
            ) from exc
        raise


def verify_installation(target: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    target = target.resolve()
    require_receipt_target(target, receipt)
    results: list[dict[str, Any]] = []
    for entry in receipt.get("installer_owned_files", []):
        path = native(target, entry["path"])
        if has_unsafe_ancestor(target, entry["path"]) or path.is_symlink():
            state = "unsafe_path"
        elif not path.is_file():
            state = "missing"
        elif digest_file(path) == entry["sha256"]:
            state = "identical"
        else:
            state = "target_evolved"
        results.append({"path": entry["path"], "state": state})
    missing = [
        item["path"]
        for item in results
        if item["state"] in {"missing", "unsafe_path"}
    ]
    return {
        "schema": "maios.installation-verification.v2",
        "target": str(target),
        "receipt_state": receipt.get("state"),
        "files": results,
        "missing": missing,
        "installed": not missing,
        "behavior_claimed": False,
    }


def remove_empty_parents(path: Path, stop: Path) -> None:
    current = path
    while current != stop and current.is_dir():
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def recover_pending(target: Path) -> dict[str, Any]:
    target = target.resolve()
    path = target / ".maios" / "receipts" / "install" / "PENDING.json"
    if has_unsafe_ancestor(target, ".maios/receipts/install/PENDING.json") or path.is_symlink():
        raise InstallerError("unsafe pending installation receipt path")
    pending = read_json(path)
    if pending.get("schema") != PENDING_SCHEMA:
        raise InstallerError("unsupported pending installation schema")
    if Path(pending.get("target", "")).resolve() != target:
        raise InstallerError("pending installation target mismatch")
    removed: list[str] = []
    preserved_changed: list[str] = []
    missing: list[str] = []
    entries = list(pending.get("installer_owned_files", []))
    entries.extend(pending.get("installer_owned_backup_files", []))
    for entry in reversed(entries):
        relative = entry.get("path")
        if not isinstance(relative, str):
            raise InstallerError("pending installation contains an invalid path")
        candidate = native(target, relative)
        if has_unsafe_ancestor(target, relative) or candidate.is_symlink():
            preserved_changed.append(relative)
        elif not candidate.exists():
            missing.append(relative)
        elif not candidate.is_file() or digest_file(candidate) != entry.get("sha256"):
            preserved_changed.append(relative)
        else:
            candidate.unlink()
            removed.append(relative)
            remove_empty_parents(candidate.parent, target)
    complete = not preserved_changed
    if complete and path.is_file():
        path.unlink()
        remove_empty_parents(path.parent, target)
    return {
        "schema": "maios.pending-installation-recovery.v2",
        "target": str(target),
        "source_plan_digest": pending.get("plan_digest"),
        "removed": sorted(removed),
        "preserved_changed": sorted(preserved_changed),
        "already_missing": sorted(missing),
        "complete": complete,
        "global_writes": [],
    }


def uninstall(target: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    target = target.resolve()
    require_receipt_target(target, receipt)
    removed: list[str] = []
    preserved_changed: list[str] = []
    missing: list[str] = []
    for entry in reversed(receipt.get("installer_owned_files", [])):
        path = native(target, entry["path"])
        if has_unsafe_ancestor(target, entry["path"]) or path.is_symlink():
            preserved_changed.append(entry["path"])
        elif not path.exists():
            missing.append(entry["path"])
        elif not path.is_file() or digest_file(path) != entry["sha256"]:
            preserved_changed.append(entry["path"])
        else:
            path.unlink()
            removed.append(entry["path"])
            remove_empty_parents(path.parent, target)
    for entry in reversed(receipt.get("installer_owned_backup_files", [])):
        path = native(target, entry["path"])
        if has_unsafe_ancestor(target, entry["path"]) or path.is_symlink():
            preserved_changed.append(entry["path"])
        elif not path.exists():
            missing.append(entry["path"])
        elif not path.is_file() or digest_file(path) != entry["sha256"]:
            preserved_changed.append(entry["path"])
        else:
            path.unlink()
            removed.append(entry["path"])
            remove_empty_parents(path.parent, target)
    receipt_path = target / ".maios" / "receipts" / "install" / "CURRENT.json"
    if receipt_path.is_file() and not preserved_changed:
        receipt_path.unlink()
        remove_empty_parents(receipt_path.parent, target)
    result = {
        "schema": UNINSTALL_SCHEMA,
        "target": str(target),
        "source_plan_digest": receipt.get("plan_digest"),
        "removed": sorted(removed),
        "preserved_changed": sorted(preserved_changed),
        "already_missing": sorted(missing),
        "complete": not preserved_changed,
    }
    return result


def load_plan(path: Path) -> dict[str, Any]:
    value = read_json(path)
    if not isinstance(value, dict):
        raise InstallerError("install plan must be a JSON object")
    verify_plan(value)
    return value


def require_receipt_target(target: Path, receipt: Any) -> None:
    target = target.resolve()
    if not isinstance(receipt, dict) or receipt.get("schema") != RECEIPT_SCHEMA:
        raise InstallerError("unsupported installation receipt schema")
    receipt_target = receipt.get("target")
    if not isinstance(receipt_target, str) or Path(receipt_target).resolve() != target:
        raise InstallerError("installation receipt does not belong to the requested target")


def load_receipt(target: Path, explicit: Path | None) -> dict[str, Any]:
    target = target.resolve()
    path = explicit or target / ".maios" / "receipts" / "install" / "CURRENT.json"
    if path.is_symlink():
        raise InstallerError("installation receipt must not be a symlink")
    value = read_json(path)
    require_receipt_target(target, value)
    return value


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Install MAIOS Project Kernel")
    sub = result.add_subparsers(dest="command", required=True)

    preview = sub.add_parser("preview")
    preview.add_argument("--target", type=Path, required=True)
    preview.add_argument(
        "--mode", choices=("new_repository", "existing_repository"), required=True
    )
    preview.add_argument("--host", required=True, metavar="ADAPTER_ID")
    preview.add_argument("--plan-out", type=Path)

    apply = sub.add_parser("apply")
    apply.add_argument("--plan", type=Path, required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("--target", type=Path, required=True)
    verify.add_argument("--receipt", type=Path)

    remove = sub.add_parser("uninstall")
    remove.add_argument("--target", type=Path, required=True)
    remove.add_argument("--receipt", type=Path)
    remove.add_argument("--receipt-out", type=Path)
    recover = sub.add_parser("recover-pending")
    recover.add_argument("--target", type=Path, required=True)
    recover.add_argument("--receipt-out", type=Path)
    return result


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    try:
        root = distribution_root()
        if args.command in {"preview", "apply"} and root is None:
            raise InstallerError("preview/apply require the original distribution")
        if args.command == "preview":
            assert root is not None
            plan = make_plan(root, args.target, args.mode, args.host)
            if args.plan_out:
                write_json(args.plan_out, plan)
            print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if plan["status"] != "blocked" else 2
        if args.command == "apply":
            assert root is not None
            receipt = apply_plan(root, load_plan(args.plan))
            print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        if args.command == "verify":
            receipt = load_receipt(args.target, args.receipt)
            result = verify_installation(args.target, receipt)
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if result["installed"] else 2
        if args.command == "recover-pending":
            result = recover_pending(args.target)
            if args.receipt_out:
                write_json(args.receipt_out, result)
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if result["complete"] else 2
        receipt = load_receipt(args.target, args.receipt)
        result = uninstall(args.target, receipt)
        if args.receipt_out:
            write_json(args.receipt_out, result)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["complete"] else 2
    except InstallerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
