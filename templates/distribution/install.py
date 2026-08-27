#!/usr/bin/env python3
"""Generated MAIOS Project Kernel package-owned installer entry."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
IMPLEMENTATION = ROOT / "payload" / ".maios" / "installer"
sys.dont_write_bytecode = True
if sys.version_info < (3, 10):
    raise SystemExit("MAIOS Project Kernel requires Python 3.10 or later.")
sys.path.insert(0, str(IMPLEMENTATION))

from installer import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
