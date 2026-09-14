"""User-manager boot contract tooling (order 010-a, workstream F).

The supported appliance boot contract is unattended operation (mode B):
the appliance user has user-manager linger enabled, so the adapter user
service starts at boot without a login session. Without linger (mode A)
the service starts at login only (documented degraded mode). This module
parses and classifies linger state and performs a READ-ONLY inspection;
it never enables or disables linger (that is a documented, reversible,
human-authorized procedure step in docs/DEPLOYMENT.md).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

LINGER_VALUE_CLASSES = ("yes", "no")
LINGER_STATE_CLASSES = {
    "yes": "mode_b_unattended",
    "no": "mode_a_login_only",
}


def parse_loginctl_linger(text: str) -> str:
    """Parse ``loginctl show-user <user> -p Linger`` output (closed class)."""
    for line in text.splitlines():
        if line.startswith("Linger="):
            value = line.split("=", 1)[1].strip()
            if value in LINGER_VALUE_CLASSES:
                return value
            return "invalid"
    return "missing"


def classify_linger(value: str) -> str:
    """Map a linger value to the closed boot-contract state class."""
    return LINGER_STATE_CLASSES.get(value, "unknown")


def inspect(user: str | None = None, timeout: float = 10.0) -> dict[str, object]:
    """Read-only linger inspection for the appliance user (no mutation)."""
    if shutil.which("loginctl") is None:
        return {"user": user or "unknown", "linger": "unavailable", "class": "unknown"}
    target = user if user is not None else "$USER"
    resolved_user = target
    if target == "$USER":
        import os

        resolved_user = os.environ.get("USER", "unknown")
    try:
        result = subprocess.run(
            ["loginctl", "show-user", resolved_user, "-p", "Linger"],
            capture_output=True,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return {"user": resolved_user, "linger": "unavailable", "class": "unknown"}
    if result.returncode != 0:
        return {"user": resolved_user, "linger": "unavailable", "class": "unknown"}
    value = parse_loginctl_linger(result.stdout.decode("utf-8", "replace"))
    return {
        "user": resolved_user,
        "linger": value,
        "class": classify_linger(value),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--user", default=None, help="appliance user (default: current user)")
    args = parser.parse_args()
    if not args.inspect:
        parser.print_help()
        return 2
    print(json.dumps(inspect(args.user), sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
