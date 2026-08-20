#!/usr/bin/env python3
"""Exact two-byte FIFO transport for the OAP handshake."""

from __future__ import annotations

import argparse
import os
import stat
import sys
from pathlib import Path

PAYLOAD = b"OK"


def require_fifo(path: Path) -> None:
    try:
        mode = path.stat().st_mode
    except FileNotFoundError as exc:
        raise SystemExit(f"FIFO missing: {path}") from exc
    if not stat.S_ISFIFO(mode):
        raise SystemExit(f"Not a FIFO: {path}")


def wait_for_ok(path: Path) -> None:
    require_fifo(path)
    fd = os.open(path, os.O_RDONLY)
    try:
        data = bytearray()
        while True:
            chunk = os.read(fd, 16)
            if not chunk:
                break
            data.extend(chunk)
            if len(data) > len(PAYLOAD):
                break
    finally:
        os.close(fd)
    if bytes(data) != PAYLOAD:
        raise SystemExit(
            f"Protocol error on {path}: expected hex 4f4b, received {bytes(data).hex()}"
        )


def send_ok(path: Path) -> None:
    require_fifo(path)
    fd = os.open(path, os.O_WRONLY)
    try:
        sent = 0
        while sent < len(PAYLOAD):
            sent += os.write(fd, PAYLOAD[sent:])
    finally:
        os.close(fd)
    if sent != len(PAYLOAD):
        raise SystemExit(f"Short FIFO write to {path}: {sent} bytes")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("wait", "send"):
        command = sub.add_parser(name)
        command.add_argument("--fifo", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "wait":
        wait_for_ok(args.fifo)
    else:
        send_ok(args.fifo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
