"""Deterministically project the living source system into a distribution."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


PROJECTION_SCHEMA = "maios.release-projection.v2"
MANIFEST_SCHEMA = "maios.project-kernel-distribution.v2"
INVENTORY_SCHEMA = "maios.package-inventory.v2"
FIXED_TIMESTAMP = (2026, 8, 24, 0, 0, 0)


class BuildError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def source_identity_bytes(path: Path) -> bytes:
    """Return checkout-independent bytes for the source-tree identity."""
    data = path.read_bytes()
    if b"\x00" in data:
        return data
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"cannot read valid JSON: {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


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
        raise BuildError(f"unsafe projection path: {value}")
    return path


def native(root: Path, relative: str) -> Path:
    return root.joinpath(*safe_relative(relative).parts)


def source_tree_files(root: Path) -> list[Path]:
    excluded_roots = {".git", "package", "dist", ".pytest_cache", "__pycache__"}
    result: list[Path] = []
    for path in sorted(
        root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()
    ):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        top = relative.parts[0]
        if (
            any(part in excluded_roots for part in relative.parts)
            or top.startswith(".package.")
            or top.startswith(".dist.")
        ):
            continue
        if path.is_symlink():
            raise BuildError(f"source tree contains a symlinked file: {relative}")
        result.append(path)
    return result


def source_tree_digest(root: Path) -> str:
    rows = []
    for path in source_tree_files(root):
        data = source_identity_bytes(path)
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": digest_bytes(data),
                "bytes": len(data),
            }
        )
    return digest_bytes(canonical_bytes(rows))


def transformed_adapters(root: Path) -> dict[str, Any]:
    value = read_json(root / "adapters" / "ADAPTERS.json")
    result = json.loads(json.dumps(value))
    owner = result.get("semantic_owner")
    if not isinstance(owner, str):
        raise BuildError("adapter semantic_owner is missing")
    result["source_owner"] = owner
    result["semantic_owner"] = f"payload/{owner}"
    for adapter in result.get("adapters", []):
        for projection in adapter.get("projections", []):
            source = projection.get("source")
            if not isinstance(source, str):
                raise BuildError("adapter projection source is missing")
            projection["source"] = f"payload/{source}"
    return result


def distribution_files(package_dir: Path, include_inventory: bool = True) -> list[Path]:
    result = []
    for path in sorted(
        package_dir.rglob("*"),
        key=lambda item: item.relative_to(package_dir).as_posix(),
    ):
        if path.is_file():
            if not include_inventory and path.name == "PACKAGE_INVENTORY.json":
                continue
            result.append(path)
    return result


def render_distribution(root: Path, package_dir: Path) -> dict[str, Any]:
    root = root.resolve()
    if package_dir.expanduser().is_symlink():
        raise BuildError("distribution target must not be a symlink")
    package_dir = package_dir.resolve()
    if package_dir.exists() and any(package_dir.iterdir()):
        raise BuildError(f"render target must be absent or empty: {package_dir}")
    package_dir.mkdir(parents=True, exist_ok=True)

    projection_path = root / "release" / "PROJECTION.json"
    projection = read_json(projection_path)
    if projection.get("schema") != PROJECTION_SCHEMA:
        raise BuildError("unsupported release projection schema")
    if projection.get("version") != "2.0.0":
        raise BuildError("release projection version is not 2.0.0")

    destinations: set[str] = set()
    for item in projection.get("files", []):
        source_rel = item.get("source")
        destination_rel = item.get("destination")
        if not isinstance(source_rel, str) or not isinstance(destination_rel, str):
            raise BuildError("projection entries require source and destination")
        safe_relative(source_rel)
        safe_relative(destination_rel)
        if destination_rel in destinations:
            raise BuildError(f"duplicate projection destination: {destination_rel}")
        destinations.add(destination_rel)
        source = native(root, source_rel)
        if not source.is_file() or source.is_symlink():
            raise BuildError(f"projection source is missing or unsafe: {source_rel}")
        destination = native(package_dir, destination_rel)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    write_json(package_dir / "adapters" / "ADAPTERS.json", transformed_adapters(root))

    tree_sha256 = source_tree_digest(root)
    payload_count = len(
        [path for path in (package_dir / "payload").rglob("*") if path.is_file()]
    )
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "product": "MAIOS Project Kernel",
        "version": "2.0.0",
        "entrypoint": "install.py",
        "project_entrypoint": "payload/START_HERE.md",
        "target_modes": ["new_repository", "existing_repository"],
        "host_adapters": ["generic", "codex", "claude", "opencode", "hermes", "dsh"],
        "source_identity": {
            "owner": "maios-project-kernel repository",
            "tree_sha256": tree_sha256,
            "projection_sha256": digest_file(projection_path),
            "source_manifest_sha256": digest_file(root / "sources" / "SOURCE_MANIFEST.json"),
            "revision_claim": "content_addressed_source_tree",
        },
        "payload_file_count": payload_count,
        "distribution_file_count": len(distribution_files(package_dir)) + 2,
        "self_installation": {
            "preview_required": True,
            "exact_plan_apply": True,
            "conflict_refusal": True,
            "idempotency": True,
            "recovery": "remove_only_unchanged_installer_owned_bytes",
            "global_writes": [],
        },
        "competence_cultivation": {
            "state_owner": "payload/.maios/competences/INDEX.json",
            "protocol": "payload/.maios/kernel/COMPETENCE_CULTIVATION_PROTOCOL.md",
            "producer_self_approval": False,
            "behavioral_proof_separate": True,
        },
        "contains_repokernel_source": False,
        "contains_form_state": False,
        "contains_private_topology": False,
        "contains_lifecycle_hooks": False,
        "global_writes": [],
    }
    write_json(package_dir / "MANIFEST.json", manifest)

    inventory_rows = [
        {
            "path": path.relative_to(package_dir).as_posix(),
            "sha256": digest_file(path),
            "bytes": path.stat().st_size,
        }
        for path in distribution_files(package_dir, include_inventory=False)
    ]
    inventory = {
        "schema": INVENTORY_SCHEMA,
        "algorithm": "sha256",
        "files": inventory_rows,
    }
    write_json(package_dir / "PACKAGE_INVENTORY.json", inventory)
    return {
        "source_tree_sha256": tree_sha256,
        "package_file_count": len(distribution_files(package_dir)),
        "payload_file_count": payload_count,
    }


def inventory_errors(package_dir: Path) -> list[str]:
    errors: list[str] = []
    inventory = read_json(package_dir / "PACKAGE_INVENTORY.json")
    if inventory.get("schema") != INVENTORY_SCHEMA:
        return ["unsupported package inventory schema"]
    actual = {
        path.relative_to(package_dir).as_posix(): {
            "sha256": digest_file(path),
            "bytes": path.stat().st_size,
        }
        for path in distribution_files(package_dir, include_inventory=False)
    }
    declared_rows = [
        item for item in inventory.get("files", []) if isinstance(item, dict)
    ]
    declared = {
        item.get("path"): {"sha256": item.get("sha256"), "bytes": item.get("bytes")}
        for item in declared_rows
    }
    if len(declared) != len(declared_rows):
        errors.append("package inventory contains duplicate paths")
    if declared != actual:
        errors.append("package inventory does not exactly match distribution bytes")
    return errors


def verify_distribution(root: Path, package_dir: Path) -> dict[str, Any]:
    root = root.resolve()
    package_dir = package_dir.resolve()
    errors: list[str] = []
    required = {
        "install.py",
        "MANIFEST.json",
        "PACKAGE_INVENTORY.json",
        "payload/START_HERE.md",
        "payload/maios.py",
        "payload/.maios/installer/installer.py",
        "payload/.maios/runtime/kernel.py",
        "payload/.maios/runtime/operating.py",
        "payload/.maios/kernel/SYSTEM_KERNEL.md",
        "payload/.maios/kernel/COMPETENCE_CULTIVATION_PROTOCOL.md",
        "payload/.maios/competences/INDEX.json",
        "payload/.maios/schemas/RESULTANT_READBACK.schema.json",
        "payload/.maios/state/OPERATING_STATE.json",
        "payload/skills/maios-project-system/SKILL.md",
    }
    actual_names = {
        path.relative_to(package_dir).as_posix() for path in distribution_files(package_dir)
    }
    missing = sorted(required - actual_names)
    if missing:
        errors.append("missing required distribution files: " + ", ".join(missing))
    try:
        manifest = read_json(package_dir / "MANIFEST.json")
        if manifest.get("schema") != MANIFEST_SCHEMA:
            errors.append("unsupported distribution manifest schema")
        if manifest.get("version") != "2.0.0":
            errors.append("distribution version is not 2.0.0")
        if manifest.get("source_identity", {}).get("tree_sha256") != source_tree_digest(root):
            errors.append("manifest source tree identity is stale")
        if manifest.get("distribution_file_count") != len(actual_names):
            errors.append("manifest distribution_file_count is incorrect")
        actual_payload_count = len(
            [path for path in (package_dir / "payload").rglob("*") if path.is_file()]
        )
        if manifest.get("payload_file_count") != actual_payload_count:
            errors.append("manifest payload_file_count is incorrect")
        for flag in (
            "contains_repokernel_source",
            "contains_form_state",
            "contains_private_topology",
            "contains_lifecycle_hooks",
        ):
            if manifest.get(flag) is not False:
                errors.append(f"manifest must set {flag} false")
    except BuildError as exc:
        errors.append(str(exc))
    try:
        errors.extend(inventory_errors(package_dir))
    except BuildError as exc:
        errors.append(str(exc))

    try:
        adapters = read_json(package_dir / "adapters" / "ADAPTERS.json")
        adapter_ids = [item.get("id") for item in adapters.get("adapters", [])]
        if adapter_ids != ["generic", "codex", "claude", "opencode", "hermes", "dsh"]:
            errors.append("host adapter ids or order are incorrect")
        if adapters.get("semantic_owner") != "payload/skills/maios-project-system/SKILL.md":
            errors.append("host adapters do not point to the one packaged semantic owner")
        semantic_owner = adapters.get("semantic_owner")
        for adapter in adapters.get("adapters", []):
            adapter_id = adapter.get("id")
            if adapter_id == "generic":
                continue
            semantic_projections = [
                item
                for item in adapter.get("projections", [])
                if item.get("source") == semantic_owner
                and isinstance(item.get("destination"), str)
                and item["destination"].endswith("/maios-project-system/SKILL.md")
            ]
            if len(semantic_projections) != 1:
                errors.append(
                    f"host adapter {adapter_id!r} must project the one semantic owner exactly once"
                )
    except BuildError as exc:
        errors.append(str(exc))
    try:
        faculty_field = read_json(
            package_dir / "payload" / ".maios" / "kernel" / "FACULTY_FIELD.json"
        )
        families = faculty_field.get("families", [])
        permanent = [
            item for item in families if item.get("presence") == "permanent_silent"
        ]
        if faculty_field.get("open_world") is not True:
            errors.append("packaged faculty field must remain open_world")
        if len(families) < 12 or len(permanent) != 2:
            errors.append("packaged faculty field lost functional coverage or silent invariants")
    except BuildError as exc:
        errors.append(str(exc))
    try:
        configuration = read_json(
            package_dir / "payload" / "setup" / "CONFIGURATION_STATE.json"
        )
        if configuration.get("effect_authority") != "none":
            errors.append("initial configuration must not grant effect authority")
        competence_index = read_json(
            package_dir / "payload" / ".maios" / "competences" / "INDEX.json"
        )
        if competence_index.get("active") != {} or competence_index.get("history") != []:
            errors.append("initial competence index must not contain inherited project state")
        operating_state = read_json(
            package_dir / "payload" / ".maios" / "state" / "OPERATING_STATE.json"
        )
        if operating_state.get("schema") != "maios.operating-state.v1":
            errors.append("initial operating state schema is incorrect")
        if (
            operating_state.get("revision") != 0
            or operating_state.get("history") != []
            or operating_state.get("learning_relations") != []
        ):
            errors.append("initial operating state must not contain inherited project state")
    except BuildError as exc:
        errors.append(str(exc))

    forbidden_markers = (
        b".codex\\worktrees",
        b".codex/worktrees",
        b"MAIOS_CLIENT_SETUP",
        b"project_hook_kernel",
        b"hooks.json",
    )
    credential_names = {".env", "id_rsa", "id_ed25519", "credentials.json"}
    legacy_prefixes = (
        ".repokernel/",
        "meta-competences/",
        "assistant/",
        "skills/maios-project-faculty-router/",
        "skills/maios-setup-interviewer/",
        "skills/operate-maios-project-kernel/",
    )
    for path in distribution_files(package_dir):
        relative = path.relative_to(package_dir).as_posix()
        payload_relative = relative.removeprefix("payload/")
        if "__pycache__" in PurePosixPath(relative).parts or path.suffix.lower() in {
            ".pyc",
            ".pyo",
        }:
            errors.append(f"generated bytecode is forbidden in distribution: {relative}")
        if payload_relative.startswith(legacy_prefixes):
            errors.append(f"legacy package owner is forbidden: {relative}")
        if path.name.lower() in credential_names:
            errors.append(f"credential-like file is forbidden: {relative}")
        data = path.read_bytes()
        for marker in forbidden_markers:
            if marker in data:
                errors.append(f"private or contaminated marker in {relative}: {marker!r}")
        if path.suffix.lower() in {".md", ".json", ".py", ".txt"}:
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                errors.append(f"text file is not valid UTF-8: {relative}")
    return {
        "schema": "maios.distribution-verification.v2",
        "valid": not errors,
        "errors": errors,
        "package_file_count": len(actual_names),
        "source_tree_sha256": source_tree_digest(root),
    }


def deterministic_zip(package_dir: Path, output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in distribution_files(package_dir):
            name = source.relative_to(package_dir).as_posix()
            info = zipfile.ZipInfo(name, FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if source.suffix == ".py" else 0o644
            info.external_attr = (stat.S_IFREG | mode) << 16
            archive.writestr(info, source.read_bytes())
    return digest_file(output)


def promote_directory(staging: Path, target: Path) -> None:
    if staging.expanduser().is_symlink() or target.expanduser().is_symlink():
        raise BuildError("promotion paths must not be symlinks")
    staging = staging.resolve()
    target = target.resolve()
    if staging.parent != target.parent:
        raise BuildError("staging and target must share a parent for atomic promotion")
    backup = target.with_name(f".{target.name}.previous-{os.getpid()}")
    if backup.exists():
        raise BuildError(f"promotion backup already exists: {backup}")
    if target.exists():
        os.replace(target, backup)
    try:
        os.replace(staging, target)
    except Exception:
        if backup.exists() and not target.exists():
            os.replace(backup, target)
        raise
    if backup.exists():
        shutil.rmtree(backup)
