#!/usr/bin/env python3
"""Validate the public MAIOS Project Kernel distribution boundary."""

from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "package"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> int:
    manifest_path = PACKAGE / "MANIFEST.json"
    if not manifest_path.is_file():
        fail("package/MANIFEST.json is missing")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("contains_repokernel_source") is not False:
        fail("manifest must explicitly exclude RepoKernel source")
    if manifest.get("target_mode") != "new_repository":
        fail("this release must remain scoped to a new repository")
    if manifest.get("entrypoint") != "START_HERE.md":
        fail("unexpected entrypoint")

    required_root = (
        "LICENSE",
        "THIRD_PARTY_NOTICES.md",
        "README.md",
        "README.it.md",
    )
    for relative in required_root:
        if not (ROOT / relative).is_file():
            fail(f"{relative} is missing")

    declared = manifest.get("files")
    if not isinstance(declared, list) or not declared:
        fail("manifest file list is missing or empty")

    for relative in declared:
        path = PurePosixPath(relative)
        if path.is_absolute() or ".." in path.parts:
            fail(f"unsafe manifest path: {relative}")
        if not (PACKAGE / Path(*path.parts)).is_file():
            fail(f"declared package file is missing: {relative}")

    inventory_path = PACKAGE / "PACKAGE_INVENTORY.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if inventory.get("inventory_scope") != "all_payload_files_except_self":
        fail("unexpected package inventory scope")
    if inventory.get("excluded_paths") != ["PACKAGE_INVENTORY.json"]:
        fail("unexpected inventory exclusions")

    inventory_entries = inventory.get("files")
    if not isinstance(inventory_entries, list):
        fail("package inventory file list is missing")
    listed_paths: set[str] = set()
    for entry in inventory_entries:
        relative = entry.get("path")
        if not isinstance(relative, str):
            fail("invalid path in package inventory")
        path = PurePosixPath(relative)
        if path.is_absolute() or ".." in path.parts:
            fail(f"unsafe inventory path: {relative}")
        file_path = PACKAGE / Path(*path.parts)
        if not file_path.is_file():
            fail(f"inventoried package file is missing: {relative}")
        data = file_path.read_bytes()
        if len(data) != entry.get("bytes"):
            fail(f"inventoried byte count changed: {relative}")
        if hashlib.sha256(data).hexdigest() != entry.get("sha256"):
            fail(f"inventoried hash changed: {relative}")
        listed_paths.add(relative)

    actual_paths = {
        path.relative_to(PACKAGE).as_posix()
        for path in PACKAGE.rglob("*")
        if path.is_file() and path.name != "PACKAGE_INVENTORY.json"
    }
    if listed_paths != actual_paths:
        missing = sorted(actual_paths - listed_paths)
        stale = sorted(listed_paths - actual_paths)
        fail(f"inventory mismatch; unlisted={missing}, missing={stale}")
    if inventory.get("inventoried_file_count") != len(inventory_entries):
        fail("inventoried_file_count does not match inventory entries")
    if inventory.get("archive_file_count") != len(actual_paths) + 1:
        fail("archive_file_count does not match package payload")

    forbidden_names = {".env", "id_rsa", "id_ed25519"}
    forbidden_suffixes = {".pem", ".key", ".p12", ".pfx"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.name.lower() in forbidden_names:
            fail(f"credential-like file found: {path.relative_to(ROOT)}")
        if path.suffix.lower() in forbidden_suffixes:
            fail(f"credential-like file found: {path.relative_to(ROOT)}")

    private_source_markers = (
        "compiler.py",
        "validate_contract.py",
        "build_project_kernel.py",
    )
    package_names = {path.name for path in PACKAGE.rglob("*") if path.is_file()}
    leaked = sorted(set(private_source_markers) & package_names)
    if leaked:
        fail(f"possible RepoKernel source leaked: {', '.join(leaked)}")

    print(
        "OK: MAIOS Project Kernel "
        f"{manifest.get('version')} | {len(actual_paths) + 1} inventoried files | "
        "RepoKernel source excluded | new-project boundary preserved"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
