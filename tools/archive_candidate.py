#!/usr/bin/env python3
"""Prepare exact candidate bytes without creating a tag or release."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from maios_project_kernel import builder, filesystem  # noqa: E402


def archive_candidate(root: Path, package: Path, output: Path) -> dict:
    root, package, output = root.resolve(), package.resolve(), output.resolve()
    if output.is_relative_to(root):
        raise builder.BuildError("archive output must stay outside the source tree")
    verification = builder.verify_distribution(root, package)
    if not verification["valid"]:
        raise builder.BuildError("; ".join(verification["errors"]))
    version = builder.read_json(package / "MANIFEST.json")["version"]
    name = f"maios-project-kernel-{version}"
    filesystem.portable_path(name)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / (name + ".zip")
    # ZIP_STORED fixes bytes independently of platform/zlib version. Explicit
    # metadata avoids transferring checkout timestamps and host permissions.
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_STORED) as stream:
        for path in builder.distribution_files(package):
            relative = path.relative_to(package).as_posix()
            info = zipfile.ZipInfo(name + "/" + relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            stream.writestr(info, path.read_bytes())
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum_path = output / (name + ".sha256")
    with checksum_path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(f"{checksum}  {archive.name}\n")
    return {"archive": str(archive), "sha256": checksum, "checksum": str(checksum_path),
            "package_manifest_sha256": builder.digest_file(package / "MANIFEST.json"),
            "package_inventory_sha256": builder.digest_file(package / "PACKAGE_INVENTORY.json"),
            "source_tree_sha256": verification["source_tree_sha256"],
            "package_file_count": verification["package_file_count"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, default=ROOT / "package")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(archive_candidate(ROOT, args.package_dir, args.output_dir), indent=2))
        return 0
    except (builder.BuildError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
