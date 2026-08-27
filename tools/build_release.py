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
    promote_directory,
    render_distribution,
    verify_distribution,
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--package-dir", type=Path, default=ROOT / "package")
    return result


def main() -> int:
    args = parser().parse_args()
    package_dir = args.package_dir.resolve()
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
        receipt = {
            "schema": "maios.package-build-receipt.v3",
            "version": "2.0.0",
            "source_tree_sha256": build["source_tree_sha256"],
            "package_file_count": build["package_file_count"],
            "payload_file_count": build["payload_file_count"],
            "verification": verification,
        }
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
