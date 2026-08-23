#!/usr/bin/env python3
"""Build a deterministic, installable MAIOS Project Kernel ZIP."""

from __future__ import annotations

import hashlib
import json
import stat
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "package"
DIST = ROOT / "dist"
FIXED_TIMESTAMP = (2026, 8, 23, 0, 0, 0)


def main() -> int:
    manifest = json.loads((PACKAGE / "MANIFEST.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    DIST.mkdir(exist_ok=True)
    output = DIST / f"maios-project-kernel-setup-v{version}.zip"

    sources: dict[str, Path] = {}
    for path in PACKAGE.rglob("*"):
        if path.is_file():
            sources[path.relative_to(PACKAGE).as_posix()] = path
    sources["LICENSE"] = ROOT / "LICENSE"
    sources["THIRD_PARTY_NOTICES.md"] = ROOT / "THIRD_PARTY_NOTICES.md"

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(sources):
            data = sources[name].read_bytes()
            info = zipfile.ZipInfo(name, FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, data)

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum = DIST / "SHA256SUMS.txt"
    checksum.write_text(f"{digest}  {output.name}\n", encoding="utf-8", newline="\n")
    print(f"{output}")
    print(f"SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
