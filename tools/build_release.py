#!/usr/bin/env python3
"""Build MAIOS Project Kernel from the living source tree."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from maios_project_kernel.builder import (  # noqa: E402
    BuildError,
    deterministic_zip,
    promote_directory,
    render_distribution,
    verify_distribution,
    write_json,
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--package-dir", type=Path, default=ROOT / "package")
    result.add_argument("--dist-dir", type=Path, default=ROOT / "dist")
    return result


def main() -> int:
    args = parser().parse_args()
    package_dir = args.package_dir.resolve()
    dist_dir = args.dist_dir.resolve()
    staging = package_dir.with_name(f".{package_dir.name}.staging")
    if staging.exists():
        if staging.is_symlink():
            print(f"ERROR: staging path must not be a symlink: {staging}", file=sys.stderr)
            return 2
        shutil.rmtree(staging)
    try:
        build = render_distribution(ROOT, staging)
        verification = verify_distribution(ROOT, staging)
        if not verification["valid"]:
            raise BuildError("; ".join(verification["errors"]))
        promote_directory(staging, package_dir)
        output = dist_dir / "maios-project-kernel-setup-v2.0.0.zip"
        archive_sha256 = deterministic_zip(package_dir, output)
        receipt = {
            "schema": "maios.build-receipt.v2",
            "version": "2.0.0",
            "source_tree_sha256": build["source_tree_sha256"],
            "package_file_count": build["package_file_count"],
            "payload_file_count": build["payload_file_count"],
            "archive": output.name,
            "archive_sha256": archive_sha256,
            "verification": verification,
        }
        write_json(dist_dir / "BUILD_RECEIPT.json", receipt)
        (dist_dir / "SHA256SUMS").write_text(
            f"{archive_sha256}  {output.name}\n", encoding="ascii", newline="\n"
        )
        print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (BuildError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    finally:
        if staging.exists():
            shutil.rmtree(staging)


if __name__ == "__main__":
    raise SystemExit(main())
