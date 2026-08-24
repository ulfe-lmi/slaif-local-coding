#!/usr/bin/env python3
"""Atomically publish one finalized strategic order and the active pointer."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

ID_RE = re.compile(r"^[0-9]{3}-[a-z]{1,2}$")
FORBIDDEN_DRAFT_MARKERS = ("DRAFT UNTIL", "VERIFY:")


def atomic_write(path: Path, data: bytes, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(temp_name)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb", closefd=True) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            try:
                os.fsync(directory_fd)
            except OSError:
                pass
        finally:
            os.close(directory_fd)
    finally:
        temp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not ID_RE.fullmatch(args.id):
        raise SystemExit(f"Invalid OAP ID: {args.id}")
    repo = args.repo_root.resolve()
    source = args.source.resolve()
    if not (repo / ".git").exists():
        raise SystemExit(f"Not a Git checkout: {repo}")
    if not source.is_file():
        raise SystemExit(f"Order source missing: {source}")
    if not source.name.startswith(f"{args.id}-") or source.suffix != ".md":
        raise SystemExit("Order filename must start '<ID>-' and end '.md'")

    data = source.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit("Order must be UTF-8") from exc
    if not text.strip():
        raise SystemExit("Order is empty")
    for marker in FORBIDDEN_DRAFT_MARKERS:
        if marker in text:
            raise SystemExit(f"Order still contains non-final marker: {marker}")
    if args.id not in text[:500]:
        raise SystemExit("Order ID is not present near document start")

    orders = repo / "oap" / "orders"
    active = repo / "oap" / "active"
    existing = sorted(orders.glob(f"{args.id}-*.md"))
    target = orders / source.name
    if existing:
        if existing != [target] or not target.is_file() or target.read_bytes() != data:
            raise SystemExit(f"Conflicting order already published for {args.id}: {existing}")
        # Recovery case: a prior run published the exact order but was interrupted
        # before replacing active. Reusing identical immutable bytes is safe.

    if args.dry_run:
        print(f"would publish {source} -> {target}")
        print(f"would set {active} -> {args.id}")
        return 0

    if not target.exists():
        atomic_write(target, data)
    atomic_write(active, f"{args.id}\n".encode("ascii"))
    print(target)
    print(active)
    return 0


if __name__ == "__main__":
    sys.exit(main())
