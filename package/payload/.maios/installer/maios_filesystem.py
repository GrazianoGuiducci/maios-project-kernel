"""Shared local path confinement and exclusively owned atomic output."""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import tempfile
from typing import Any


def is_link(path: Path) -> bool:
    try:
        value = path.lstat()
    except FileNotFoundError:
        return False
    # st_reparse_tag is available on Windows in Python 3.10. Do not depend on
    # Path.is_junction (added in 3.12), or follow the entry to classify it.
    return stat.S_ISLNK(value.st_mode) or getattr(value, "st_reparse_tag", 0) in {
        getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003),
        getattr(stat, "IO_REPARSE_TAG_SYMLINK", 0xA000000C),
    }


def ensure_local(root: Path, path: Path) -> None:
    original_root = root if root.is_absolute() else Path.cwd() / root
    original_path = path if path.is_absolute() else Path.cwd() / path
    root = original_root.resolve()
    try:
        relative = original_path.relative_to(original_root)
    except ValueError:
        relative = original_path.relative_to(root)
    if ".." in relative.parts:
        raise ValueError(f"path contains parent traversal: {relative}")
    current = root
    for part in relative.parts:
        current = current / part
        if is_link(current):
            raise ValueError(f"project path contains a symlink or junction: {relative}")
    if not original_path.parent.resolve().is_relative_to(root):
        raise ValueError(f"project path parent escapes root: {relative}")


def _identity(value: os.stat_result) -> tuple[int, int, str, int]:
    basis = "birthtime_ns" if hasattr(value, "st_birthtime_ns") else "ctime_ns"
    return value.st_dev, value.st_ino, basis, getattr(value, "st_" + basis)


def _owned(path: Path, identity: tuple[int, int, str, int]) -> bool:
    try:
        value = path.lstat()
        return (not is_link(path) and stat.S_ISREG(value.st_mode)
                and bool(value.st_ino) and _identity(value) == identity)
    except OSError:
        return False


def write_bytes_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    parent = path.parent.resolve()
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.maios-tmp-", dir=parent)
    temporary = Path(name)
    identity = _identity(os.fstat(fd))
    try:
        # Use the exclusively acquired descriptor, never reopen the pathname.
        with os.fdopen(fd, "wb") as stream:
            fd = -1
            try:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            finally:
                identity = _identity(os.fstat(stream.fileno()))
        if path.parent.resolve() != parent or not _owned(temporary, identity):
            raise OSError("atomic output path changed; preserve uncertain temporary")
        os.replace(temporary, path)
    finally:
        if fd != -1:
            os.close(fd)
        if _owned(temporary, identity):
            temporary.unlink()


def write_text_atomic(path: Path, text: str) -> None:
    write_bytes_atomic(path, text.encode("utf-8"))


def write_json_atomic(path: Path, value: Any) -> None:
    write_text_atomic(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
