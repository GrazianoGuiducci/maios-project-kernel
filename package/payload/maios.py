#!/usr/bin/env python3
"""Generated project-local MAIOS Kernel deterministic helper."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / ".maios" / "runtime"))

from kernel import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
