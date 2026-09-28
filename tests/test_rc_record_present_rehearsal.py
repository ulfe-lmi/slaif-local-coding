"""Order 014-c, workstream C.3: ordinary CI runs the prepublication
record-present rehearsal at HEAD BEFORE publication.

The RC4 rejection proved that a stale ``0.1.0-rc3`` const in the
record-present state escaped every prepublication gate because ordinary CI
had no ``packaging/rc_record.json`` and the record-present branch ran only
after publication. This hook closes the gap permanently: the deterministic,
network-free rehearsal (``scripts/rc_record_present_rehearsal.py``)
exercises the full record-present/``rc_published`` validation path at the
candidate source on every CI run.

Regression anchor: the rehearsal MUST FAIL at the rejected RC4 image source
``601a7f9fae19869ad8e09f10fa994550368fd87c`` (stale ``candidate.rc_identifier``
const ``0.1.0-rc3`` in the record-present state) — the exact RC4 escape.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
REHEARSAL = REPO_ROOT / "scripts" / "rc_record_present_rehearsal.py"

# The rejected RC4 image source / workflow head (immutable; order 014-c).
RC4_SOURCE = "601a7f9fae19869ad8e09f10fa994550368fd87c"


def _run_rehearsal(source: str | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(REHEARSAL)]
    if source is not None:
        cmd += ["--source", source]
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=2400)


def test_record_present_rehearsal_passes_at_head() -> None:
    """The full record-present/``rc_published`` validation path must pass
    at the current candidate source before publication (order 014-c,
    WS-C.1/WS-C.3): candidate record/handoff/published-state provenance,
    the strict record/provenance/schema/docs/Docker-record gates, the
    candidate label/tag/version branch, and the tamper classes."""
    if shutil.which("uv") is None:
        pytest.fail("uv is required for the record-present rehearsal candidate build")
    proc = _run_rehearsal()
    assert proc.returncode == 0, (
        "record-present rehearsal FAILED at HEAD:\n"
        f"--- stdout ---\n{proc.stdout[-4000:]}\n"
        f"--- stderr ---\n{proc.stderr[-4000:]}"
    )
    assert "record-present rehearsal PASSED" in proc.stdout


def test_rehearsal_catches_rc4_stale_rc3_residue() -> None:
    """The rehearsal must have caught the RC3 hardcode at RC4 source
    ``601a7f9...`` (order 014-c, WS-C.3): the stale prior-RC const in the
    record-present state fails the candidate label/tag/version branch
    closed, before any gate suite or publication."""
    proc = _run_rehearsal(RC4_SOURCE)
    assert proc.returncode == 1, (
        "rehearsal unexpectedly PASSED at the rejected RC4 source "
        f"{RC4_SOURCE}:\n{proc.stdout[-2000:]}"
    )
    assert "record-present rehearsal FAILED" in proc.stderr
