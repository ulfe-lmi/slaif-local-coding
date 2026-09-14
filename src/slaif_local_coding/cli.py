"""Command-line entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

from . import __version__
from .app import create_app
from .config import load_settings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--version", action="store_true", help="print the package version and exit")
    args = parser.parse_args()
    if args.version:
        print(f"slaif-local-coding {__version__}")
        return
    settings = load_settings(args.config)
    uvicorn.run(
        create_app(settings),
        host=settings.server.listen_host,
        port=settings.server.listen_port,
        access_log=False,
    )


if __name__ == "__main__":
    main()
