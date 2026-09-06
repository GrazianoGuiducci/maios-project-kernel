#!/usr/bin/env python3
"""Canonical deterministic MAIOS Project Kernel install lifecycle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable

try:
    from . import filesystem as filesystem_engine
except ImportError:  # generated runtime and installer carry the same source
    import maios_filesystem as filesystem_engine  # type: ignore[no-redef]


PLAN_SCHEMA = "maios.install-plan.v2"
RECEIPT_SCHEMA = "maios.installation-receipt.v3"
UNINSTALL_SCHEMA = "maios.uninstall-receipt.v2"
PENDING_SCHEMA = "maios.pending-installation.v3"


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
    filesystem_engine.write_json_atomic(path, value)


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


def require_external_output(path: Path, distribution: Path | None, target: Path) -> None:
    """Transient outputs must not mutate the verified input or the selected target."""
    forbidden = {target.resolve()}
    if distribution is not None:
        forbidden.add(distribution.resolve())
    candidates = set(Path(__file__).resolve().parents)
    if distribution is not None:
        candidates.update((distribution.resolve(), *distribution.resolve().parents))
    for candidate in candidates:
        if ((candidate / "release/PROJECTION.json").is_file()
                and (candidate / "src/maios_project_kernel/builder.py").is_file()):
            forbidden.add(candidate)
    lexical = Path(os.path.abspath(path))
    resolved = path.resolve()
    if any(lexical.is_relative_to(base) or resolved.is_relative_to(base) for base in forbidden):
        raise InstallerError("plan and receipt outputs must stay outside the distribution, source repository and target; use a temporary path")


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


def rendered_skill_entry(root: Path, source_relative: str) -> bytes:
    source = native(root, source_relative)
    if not source.is_file() or source.is_symlink():
        raise InstallerError(f"unsafe native skill source: {source_relative}")
    text = source.read_text(encoding="utf-8")
    if not text.startswith("---\n") or len(text.split("---", 2)) != 3:
        raise InstallerError(f"native skill source lacks metadata: {source_relative}")
    frontmatter = text.split("---", 2)[1]
    living_source = source_relative.removeprefix("payload/")
    safe_relative(living_source)
    return (
        "---" + frontmatter + "---\n\n"
        f"<!-- maios-knowledge-entry: {living_source} -->\n"
        "# Living competence entry\n\n"
        f"Read and exercise `{living_source}` from the project root.\n"
        "That project-owned body supplies the current knowledge, method and\n"
        "continuation; resolve its references and helpers from its directory.\n"
        "Return reusable learning to that living owner. If invocation or ownership\n"
        "changes, update this discovery entry too. Do not substitute the startup\n"
        "snapshot for the evolving method or claim to read an unavailable source.\n"
    ).encode("utf-8")


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
        is_skill = source_rel.endswith("/SKILL.md") and destination.endswith("/SKILL.md")
        data = rendered_skill_entry(root, source_rel) if is_skill else source.read_bytes()
        candidate = {
            "source": source_rel,
            "destination": destination,
            "sha256": digest_bytes(data),
            "bytes": len(data),
            "kind": "host_projection",
        }
        if is_skill:
            candidate["render"] = {"type": "live_skill", "source": source_rel}
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
        if has_unsafe_ancestor(target, relative.as_posix()):
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
    try:
        filesystem_engine.ensure_local(target, native(target, destination))
    except (ValueError, OSError):
        return True
    return False


def canonical_target(target: Path) -> Path:
    if filesystem_engine.is_link(target.expanduser()):
        raise InstallerError("target root must not be a symlink or junction")
    return target.resolve()


def current_receipt(target: Path) -> dict[str, Any] | None:
    target = canonical_target(target)
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
        require_valid_installation_receipt(value)
    except InstallerError:
        return None
    return value


def plan_digest(plan: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in plan.items() if key != "plan_digest"}
    return digest_bytes(canonical_bytes(unsigned))


def make_plan(root: Path, target: Path, mode: str, host: str) -> dict[str, Any]:
    root = root.resolve()
    if filesystem_engine.is_link(target.expanduser()):
        raise InstallerError("target root must not be a symlink")
    target = canonical_target(target)
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
    receipt_path = target / ".maios" / "receipts" / "install" / "CURRENT.json"
    if prior is None and (receipt_path.exists() or receipt_path.is_symlink()):
        blocked_reasons.append("invalid_current_installation_receipt")
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


def file_identity(value: os.stat_result) -> dict[str, int | str] | None:
    if not value.st_ino:
        return None  # no reliable file identity: recovery must preserve it
    # Windows exposes birth time separately; legacy ctime can differ between
    # descriptor and pathname observations even for the same newly created file.
    basis = "birthtime_ns" if hasattr(value, "st_birthtime_ns") else "ctime_ns"
    return {"device": value.st_dev, "inode": value.st_ino, "time_basis": basis,
            "time_ns": getattr(value, "st_" + basis)}


def create_file(base: Path, relative: str, data: bytes) -> dict[str, Any]:
    """Return evidence from the descriptor acquired by this exclusive creation."""
    destination = native(base, relative)
    if has_unsafe_ancestor(base, relative) or destination.is_symlink():
        raise InstallerError(f"unsafe creation destination: {relative}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                             getattr(os, "O_BINARY", 0), 0o644)
    except FileExistsError as exc:
        raise InstallerError(f"destination appeared after preview: {relative}") from exc
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
        identity = file_identity(os.fstat(stream.fileno()))
    # Failed or unrecorded writes remain uncertain; never unlink by path here.
    sha256 = digest_bytes(data)
    if (has_unsafe_ancestor(base, relative) or destination.is_symlink()
        or not destination.is_file() or digest_file(destination) != sha256
        or (identity is not None and file_identity(destination.stat()) != identity)):
        raise InstallerError(f"created file changed before recording: {relative}")
    return {"path": relative, "sha256": sha256, "file_identity": identity}


def copy_entry(root: Path, base: Path, entry: dict[str, Any]) -> dict[str, Any]:
    destination = native(base, entry["destination"])
    if has_unsafe_ancestor(base, entry["destination"]) or destination.is_symlink():
        raise InstallerError(f"unsafe destination changed after preview: {entry['destination']}")
    render = entry.get("render")
    if isinstance(render, dict) and render.get("type") == "host_state":
        data = rendered_host_state(root, render["host"])
    elif isinstance(render, dict) and render.get("type") == "live_skill":
        data = rendered_skill_entry(root, entry["source"])
    else:
        source = native(root, entry["source"])
        if not source.is_file() or source.is_symlink():
            raise InstallerError(f"unsafe package source changed after preview: {entry['source']}")
        data = source.read_bytes()
    if digest_bytes(data) != entry["sha256"]:
        raise InstallerError(f"package source changed after preview: {entry['source']}")
    return create_file(base, entry["destination"], data)


def update_baseline(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "maios.update-baseline.v1",
        "policy": ".maios/kernel/UPDATE_CONTINUITY.md",
        "configuration_schema": "maios.configuration-state.v3",
        "operating_schema": "maios.operating-state.v3",
        "plan_digest": plan["plan_digest"],
        "package_identity": plan["package_identity"],
        "files": [{key: entry[key] for key in ("source", "destination", "sha256", "bytes", "kind")}
                  for entry in plan["entries"]],
        "rule": "compare exact distributed base, local evolution and proposed source; preserve divergent local knowledge and state",
    }


def verify_update_baseline(receipt: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    plan = receipt.get("install_plan")
    try:
        if not isinstance(plan, dict):
            raise InstallerError("original install plan is missing")
        verify_plan(plan)
        for key in ("target", "mode", "host", "plan_digest", "package_identity"):
            if receipt.get(key) != plan.get(key):
                errors.append("baseline plan differs from receipt: " + key)
        destinations: set[str] = set()
        if not isinstance(plan.get("entries"), list):
            raise InstallerError("original plan entries must be a list")
        for entry in plan["entries"]:
            if not isinstance(entry, dict):
                raise InstallerError("original plan entry must be an object")
            safe_relative(entry["source"])
            safe_relative(entry["destination"])
            if entry["destination"] in destinations:
                errors.append("duplicate baseline destination")
            destinations.add(entry["destination"])
        if not destinations:
            errors.append("baseline has no files")
        partitions: list[set[str]] = []
        for key in ("creates", "preserves_identical"):
            paths = plan.get(key)
            if not isinstance(paths, list) or any(not isinstance(p, str) for p in paths):
                raise InstallerError("original plan " + key + " must be a path list")
            if len(paths) != len(set(paths)):
                errors.append("duplicate original plan path: " + key)
            partitions.append(set(paths))
        if partitions[0] & partitions[1] or partitions[0] | partitions[1] != destinations:
            errors.append("original plan ownership does not partition its destinations")
        if receipt.get("update_baseline") != update_baseline(plan):
            errors.append("update baseline differs from the original plan and package identity")
    except (InstallerError, KeyError, TypeError, ValueError) as exc:
        errors.append("invalid update baseline: " + str(exc))
    return {"schema": "maios.update-baseline-verification.v1", "valid": not errors, "errors": errors,
            "claim_boundary": "internal historical consistency, not a signature or proof against coordinated rewriting"}


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
        "install_plan": json.loads(json.dumps(plan)),
        "update_baseline": update_baseline(plan),
        "preserved_preexisting_identical": plan["preserves_identical"],
        "backup_root": backup_root,
        "installer_owned_backup_files": backed_up,
        "global_writes": [],
        "behavior_claimed": False,
        "recovery": "run the installed .maios/installer/installer.py uninstall command",
    }


def validate_installation_receipt(receipt: Any) -> dict[str, Any]:
    """Bind every consumer's ownership decisions to the retained original plan."""
    if not isinstance(receipt, dict):
        return {"schema": "maios.installation-receipt-validation.v1", "valid": False,
                "errors": ["installation receipt must be an object"], "baseline": None}
    baseline = verify_update_baseline(receipt)
    errors = list(baseline["errors"])
    if receipt.get("schema") != RECEIPT_SCHEMA:
        errors.append("unsupported installation receipt schema")
    if receipt.get("state") != "installed":
        errors.append("installation receipt must describe an installed result")
    if baseline["valid"]:
        try:
            expected = install_receipt(receipt["install_plan"], "installed")
            for key in ("installer_owned_files", "preserved_preexisting_identical",
                        "backup_root", "installer_owned_backup_files"):
                if key not in receipt or receipt[key] != expected[key]:
                    errors.append("installation receipt differs from original plan: " + key)
        except (KeyError, TypeError, ValueError) as exc:
            errors.append("invalid original plan ownership: " + str(exc))
    return {"schema": "maios.installation-receipt-validation.v1", "valid": not errors,
            "errors": errors, "baseline": baseline}


def require_valid_installation_receipt(receipt: Any) -> None:
    validation = validate_installation_receipt(receipt)
    if not validation["valid"]:
        raise InstallerError("invalid installation receipt: " + "; ".join(validation["errors"]))


def backup_identical(target: Path, plan: dict[str, Any],
                     record_created: Callable[[dict[str, Any]], None]) -> None:
    if plan["mode"] != "existing_repository" or not plan["preserves_identical"]:
        return
    for entry in install_receipt(plan, "pending")["installer_owned_backup_files"]:
        relative = entry["source_path"]
        source = native(target, relative)
        if has_unsafe_ancestor(target, relative) or source.is_symlink() or not source.is_file():
            raise InstallerError(f"pre-existing identical path changed after preview: {relative}")
        data = source.read_bytes()
        if digest_bytes(data) != entry["sha256"]:
            raise InstallerError(f"pre-existing content changed before backup: {relative}")
        record_created(create_file(target, entry["path"], data))


def pending_installation(plan: dict[str, Any]) -> dict[str, Any]:
    receipt = install_receipt(plan, "pending")
    return {
        "schema": PENDING_SCHEMA,
        "target": plan["target"],
        "plan_digest": plan["plan_digest"],
        "mode": plan["mode"],
        "host": plan["host"],
        "package_identity": plan["package_identity"],
        "attempt_id": uuid.uuid4().hex,
        "install_plan": json.loads(json.dumps(plan)),
        "planned_files": receipt["installer_owned_files"],
        "planned_backup_files": receipt["installer_owned_backup_files"],
        "created_files": [],
        "global_writes": [],
        "recovery": "run recover-pending against the exact target",
    }


def validate_pending_installation(target: Path, pending: Any) -> None:
    """Validate the complete journal before it can authorize a recovery effect."""
    if not isinstance(pending, dict) or pending.get("schema") != PENDING_SCHEMA:
        raise InstallerError("unsupported pending installation schema")
    try:
        plan = pending["install_plan"]
        if not isinstance(plan, dict):
            raise InstallerError("pending original plan must be an object")
        verify_plan(plan)
        expected = install_receipt(plan, "installed")
        require_valid_installation_receipt(expected)
        require_receipt_target(target, expected)
        if plan["mode"] != "existing_repository" or plan.get("status") != "ready":
            raise InstallerError("pending journal requires an original ready existing-project plan")
        for key in ("target", "plan_digest", "mode", "host", "package_identity"):
            if pending.get(key) != expected[key]:
                raise InstallerError("pending journal differs from original plan: " + key)
        for key, receipt_key in (("planned_files", "installer_owned_files"),
                                 ("planned_backup_files", "installer_owned_backup_files")):
            if pending.get(key) != expected[receipt_key]:
                raise InstallerError("pending journal differs from original plan: " + key)
        attempt = pending.get("attempt_id")
        if not isinstance(attempt, str) or uuid.UUID(hex=attempt).hex != attempt:
            raise InstallerError("invalid pending attempt identity")
        planned = {entry["path"]: entry for entry in
                   pending["planned_files"] + pending["planned_backup_files"]}
        records = pending.get("created_files")
        if not isinstance(records, list):
            raise InstallerError("pending created_files must be a list")
        seen: set[str] = set()
        for record in records:
            if not isinstance(record, dict) or set(record) != {"path", "sha256", "file_identity"}:
                raise InstallerError("invalid pending creation record")
            path = record["path"]
            if not isinstance(path, str) or path not in planned or path in seen:
                raise InstallerError("pending creation must identify one unique planned file")
            seen.add(path)
            if record["sha256"] != planned[path]["sha256"]:
                raise InstallerError("pending creation differs from planned content: " + path)
            identity = record["file_identity"]
            if identity is not None and (
                not isinstance(identity, dict) or set(identity) != {"device", "inode", "time_basis", "time_ns"}
                or identity["time_basis"] not in ("birthtime_ns", "ctime_ns")
                or any(type(identity[k]) is not int or identity[k] < 0 for k in ("device", "inode", "time_ns"))
                or not identity["inode"]
            ):
                raise InstallerError("invalid pending file identity: " + path)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise InstallerError("invalid pending installation: " + str(exc)) from exc


def begin_pending_installation(target: Path, pending: dict[str, Any]) -> None:
    validate_pending_installation(target, pending)
    create_file(target, ".maios/receipts/install/PENDING.json",
                (json.dumps(pending, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def record_pending_creation(target: Path, pending: dict[str, Any], record: dict[str, Any]) -> None:
    path = target / ".maios/receipts/install/PENDING.json"
    if has_unsafe_ancestor(target, ".maios/receipts/install/PENDING.json") or path.is_symlink():
        raise InstallerError("unsafe pending journal during creation recording")
    if read_json(path) != pending:
        raise InstallerError("pending journal changed before creation recording")
    candidate = json.loads(json.dumps(pending))
    candidate["created_files"].append(record)
    validate_pending_installation(target, candidate)
    write_json(path, candidate)
    pending.update(candidate)


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
        # Acquire before the cleanup handler: a competing stage is not ours.
        try:
            stage.mkdir(parents=True)
        except FileExistsError as exc:
            raise InstallerError(f"attempt staging path already exists: {stage}") from exc
        try:
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
    pending = pending_installation(plan)
    # An acquisition failure must never trigger recovery of another attempt.
    begin_pending_installation(target, pending)
    try:
        record_created = lambda record: record_pending_creation(target, pending, record)
        backup_identical(target, plan, record_created)
        for entry in plan["entries"]:
            if entry["destination"] not in plan["creates"]:
                continue
            record_created(copy_entry(root, target, entry))
        receipt = install_receipt(plan, "installed")
        if has_unsafe_ancestor(target, ".maios/receipts/install/CURRENT.json") or receipt_path.is_symlink():
            raise InstallerError("unsafe installation receipt path")
        if read_json(pending_path) != pending:
            raise InstallerError("pending journal changed before installation commit")
        write_json(receipt_path, receipt)
    except Exception as exc:
        recovery = recover_pending(target, expected_attempt=pending["attempt_id"])
        if not recovery["complete"]:
            raise InstallerError(
                "install failed and automatic recovery preserved changed or uncertain paths: "
                + str(recovery["preserved_changed"] + recovery["preserved_uncertain"])
            ) from exc
        raise
    # CURRENT commits the installation. A cleanup failure must not roll it back.
    if read_json(pending_path) != pending:
        raise InstallerError("installation committed but pending journal changed")
    try:
        pending_path.unlink()
    except OSError as exc:
        raise InstallerError("installation committed; use recover-pending to finish journal cleanup") from exc
    return receipt


def receipt_current_relation(target: Path, receipt: dict[str, Any]) -> str:
    """Relate a historical receipt to the installation presently governing target."""
    target = canonical_target(target)
    relative = ".maios/receipts/install/CURRENT.json"
    path = target / relative
    if has_unsafe_ancestor(target, relative) or path.is_symlink():
        return "current_invalid"
    if not path.exists():
        return "current_missing"
    current = current_receipt(target)
    if current is None:
        return "current_invalid"
    if any(receipt.get(key) != current.get(key)
           for key in ("target", "plan_digest", "package_identity", "install_plan")):
        return "current_mismatch"
    return "current"


def verify_installation(target: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    target = canonical_target(target)
    require_receipt_target(target, receipt)
    validation = validate_installation_receipt(receipt)
    relation = receipt_current_relation(target, receipt)
    results: list[dict[str, Any]] = []
    for entry in receipt["installer_owned_files"] if validation["valid"] else []:
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
        "verification_scope": "installer_owned_files",
        "target": str(target),
        "receipt_state": receipt.get("state"),
        "files": results,
        "missing": missing,
        "current_relation": relation,
        "files_present": not missing and validation["valid"],
        "installed": not missing and validation["valid"] and relation == "current",
        "baseline": validation["baseline"],
        "receipt_validation": validation,
        "valid": not missing and validation["valid"] and relation == "current",
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


def recover_pending(target: Path, expected_attempt: str | None = None) -> dict[str, Any]:
    target = canonical_target(target)
    path = target / ".maios" / "receipts" / "install" / "PENDING.json"
    if has_unsafe_ancestor(target, ".maios/receipts/install/PENDING.json") or path.is_symlink():
        raise InstallerError("unsafe pending installation receipt path")
    pending = read_json(path)
    validate_pending_installation(target, pending)
    if expected_attempt is not None and pending["attempt_id"] != expected_attempt:
        raise InstallerError("pending installation belongs to another attempt")
    receipt_path = target / ".maios/receipts/install/CURRENT.json"
    installation_retained = False
    if receipt_path.exists() or receipt_path.is_symlink():
        committed = load_receipt(target, None)
        if committed["install_plan"] != pending["install_plan"]:
            raise InstallerError("current installation belongs to another plan; preserve pending journal")
        installation_retained = True
    removed: list[str] = []
    preserved_changed: list[str] = []
    preserved_uncertain: list[str] = []
    missing: list[str] = []
    entries = [] if installation_retained else pending["planned_files"] + pending["planned_backup_files"]
    created = {record["path"]: record for record in pending["created_files"]}
    for entry in reversed(entries):
        relative = entry.get("path")
        if not isinstance(relative, str):
            raise InstallerError("pending installation contains an invalid path")
        candidate = native(target, relative)
        if has_unsafe_ancestor(target, relative) or candidate.is_symlink():
            preserved_changed.append(relative)
        elif not candidate.exists():
            missing.append(relative)
        elif relative not in created or created[relative]["file_identity"] is None:
            preserved_uncertain.append(relative)
        elif not candidate.is_file() or file_identity(candidate.stat()) != created[relative]["file_identity"]:
            preserved_uncertain.append(relative)
        elif digest_file(candidate) != entry["sha256"]:
            preserved_changed.append(relative)
        else:
            candidate.unlink()
            removed.append(relative)
            # Pre-existing empty directories do not become installer-owned.
    complete = not preserved_changed and not preserved_uncertain
    if complete and path.is_file():
        path.unlink()
    return {
        "schema": "maios.pending-installation-recovery.v3",
        "target": str(target),
        "source_plan_digest": pending.get("plan_digest"),
        "removed": sorted(removed),
        "preserved_changed": sorted(preserved_changed),
        "preserved_uncertain": sorted(preserved_uncertain),
        "already_missing": sorted(missing),
        "complete": complete,
        "installation_retained": installation_retained,
        "global_writes": [],
    }


def uninstall(target: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    target = canonical_target(target)
    require_receipt_target(target, receipt)
    require_valid_installation_receipt(receipt)
    relation = receipt_current_relation(target, receipt)
    if relation != "current":
        raise InstallerError("uninstall requires the valid current installation receipt: " + relation)

    def clean_empty_parents(path: Path) -> None:
        # Existing-target receipts record file ownership, not directory ownership.
        if receipt["mode"] == "new_repository":
            remove_empty_parents(path, target)

    removed: list[str] = []
    preserved_changed: list[str] = []
    missing: list[str] = []
    owned_entries = list(receipt.get("installer_owned_files", []))
    for entry in reversed(owned_entries):
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
            clean_empty_parents(path.parent)
    removed_runtime_cache: list[str] = []
    preserved_runtime_cache: list[str] = []
    cache_sources = {
        entry["path"]
        for entry in owned_entries
        if isinstance(entry, dict)
        and isinstance(entry.get("path"), str)
        and PurePosixPath(entry["path"]).suffix == ".py"
    }
    for source_relative in sorted(cache_sources):
        source_path = PurePosixPath(source_relative)
        cache_relative = (source_path.parent / "__pycache__").as_posix()
        cache_dir = native(target, cache_relative)
        if not cache_dir.exists():
            continue
        if has_unsafe_ancestor(target, cache_relative) or cache_dir.is_symlink():
            preserved_runtime_cache.append(cache_relative)
            continue
        if not cache_dir.is_dir():
            preserved_runtime_cache.append(cache_relative)
            continue
        cache_prefix = f"{source_path.stem}."
        for candidate in sorted(cache_dir.iterdir(), key=lambda item: item.name):
            if not (
                candidate.name == f"{source_path.stem}.pyc"
                or (
                    candidate.name.startswith(cache_prefix)
                    and candidate.name.endswith(".pyc")
                )
            ):
                continue
            relative = candidate.relative_to(target).as_posix()
            # A matching module name is not creation or ownership evidence.
            preserved_runtime_cache.append(relative)
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
            clean_empty_parents(path.parent)
    receipt_path = target / ".maios" / "receipts" / "install" / "CURRENT.json"
    if receipt_path.is_file() and not preserved_changed:
        receipt_path.unlink()
        clean_empty_parents(receipt_path.parent)
    result = {
        "schema": UNINSTALL_SCHEMA,
        "target": str(target),
        "source_plan_digest": receipt.get("plan_digest"),
        "removed": sorted(removed),
        "preserved_changed": sorted(preserved_changed),
        "already_missing": sorted(missing),
        "removed_runtime_cache": sorted(set(removed_runtime_cache)),
        "preserved_runtime_cache": sorted(set(preserved_runtime_cache)),
        "runtime_cache_ownership": "unrecorded_preserved",
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
    target = canonical_target(target)
    if not isinstance(receipt, dict) or receipt.get("schema") != RECEIPT_SCHEMA:
        raise InstallerError("unsupported installation receipt schema")
    receipt_target = receipt.get("target")
    if not isinstance(receipt_target, str) or Path(receipt_target).resolve() != target:
        raise InstallerError("installation receipt does not belong to the requested target")


def load_receipt(target: Path, explicit: Path | None) -> dict[str, Any]:
    target = canonical_target(target)
    if explicit is None and has_unsafe_ancestor(target, ".maios/receipts/install/CURRENT.json"):
        raise InstallerError("unsafe current installation receipt path")
    path = explicit or target / ".maios" / "receipts" / "install" / "CURRENT.json"
    if path.is_symlink():
        raise InstallerError("installation receipt must not be a symlink")
    value = read_json(path)
    require_receipt_target(target, value)
    require_valid_installation_receipt(value)
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
        output = getattr(args, "plan_out", None) or getattr(args, "receipt_out", None)
        if output is not None:
            require_external_output(output, root, args.target)
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
            return 0 if result["valid"] else 2
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
