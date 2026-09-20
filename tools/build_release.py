#!/usr/bin/env python3
"""Build MAIOS Project Kernel from the living source tree."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from maios_project_kernel.builder import BuildError, build_distribution  # noqa: E402


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--package-dir", type=Path, default=ROOT / "package")
    result.add_argument("--kernel-plan", type=Path,
                        help="Explicit compatibility: consume an identified historical GenerationPlan")
    result.add_argument("--kernel-plan-sha256",
                        help="Expected SHA-256 of canonical plan JSON, binding the selected result")
    result.add_argument("--source-only", action="store_true",
                        help="Compatibility alias for the normal direct source build")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        receipt = build_distribution(ROOT, args.package_dir,
                                     kernel_plan=args.kernel_plan,
                                     kernel_plan_sha256=args.kernel_plan_sha256,
                                     source_only=args.source_only)
        print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (BuildError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2



if __name__ == "__main__":
    raise SystemExit(main())
