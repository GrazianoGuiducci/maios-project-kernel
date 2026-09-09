#!/usr/bin/env python3
"""Form a maintained RepoKernel selection from exact source commits."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "src"))
from maios_project_kernel.selection import renew


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--compiler-root", type=Path, required=True)
    parser.add_argument("--compiler-commit", required=True)
    parser.add_argument("--review-date", required=True, help="Source selection date, YYYY-MM-DD")
    args = parser.parse_args()
    try:
        result = renew(ROOT, args.source_commit, args.compiler_root.resolve(), args.compiler_commit, args.review_date)
    except (ValueError, OSError, KeyError, ImportError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
