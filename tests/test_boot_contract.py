"""Boot contract (linger semantics) deterministic tests (order 010-a, F/H14).

Contract tests on the documented procedures plus safe read-only state
inspection. These tests never enable or disable linger and never mutate any
live user state; the host linger value is recorded as a baseline fact only.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOYMENT_DOC = REPO_ROOT / "docs" / "DEPLOYMENT.md"


def _load_boot_contract() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(
        "boot_contract", REPO_ROOT / "scripts" / "boot_contract.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load boot contract module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BOOT_CONTRACT = _load_boot_contract()


def test_linger_parse_and_classify_closed_classes() -> None:
    assert BOOT_CONTRACT.parse_loginctl_linger("Linger=yes") == "yes"
    assert BOOT_CONTRACT.parse_loginctl_linger("Linger=no") == "no"
    assert BOOT_CONTRACT.parse_loginctl_linger("SomethingElse=1\nLinger=no") == "no"
    assert BOOT_CONTRACT.parse_loginctl_linger("State=active") == "missing"
    assert BOOT_CONTRACT.parse_loginctl_linger("Linger=maybe") == "invalid"
    assert BOOT_CONTRACT.classify_linger("yes") == "mode_b_unattended"
    assert BOOT_CONTRACT.classify_linger("no") == "mode_a_login_only"
    assert BOOT_CONTRACT.classify_linger("other") == "unknown"


def test_deployment_doc_boot_contract_is_deterministic() -> None:
    doc = DEPLOYMENT_DOC.read_text(encoding="utf-8")
    # Supported appliance contract is unattended operation (mode B) with the
    # documented degraded mode A (login only) when linger is absent.
    assert "unattended operation" in doc
    assert "mode B" in doc
    assert "mode A" in doc
    assert "starts at login only" in doc
    # Documented, reversible, verified linger management for the appliance user.
    assert 'sudo loginctl enable-linger "$APPLIANCE_USER"' in doc
    assert 'sudo loginctl disable-linger "$APPLIANCE_USER"' in doc
    assert 'loginctl show-user "$APPLIANCE_USER" -p Linger' in doc
    assert "Linger=yes" in doc
    # Procedures manage linger explicitly (install/upgrade/rollback/uninstall).
    assert "restores the pre-procedure state" in doc
    # Baseline recorded only, not mutated by this objective.
    assert "not" in doc and "baseline" in doc


def test_inspect_returns_closed_classes_without_mutation() -> None:
    facts = BOOT_CONTRACT.inspect()
    assert set(facts) == {"user", "linger", "class"}
    assert facts["linger"] in ("yes", "no", "unavailable", "missing", "invalid")
    if facts["linger"] in ("yes", "no"):
        assert facts["class"] == (
            "mode_b_unattended" if facts["linger"] == "yes" else "mode_a_login_only"
        )
    else:
        assert facts["class"] == "unknown"


def test_inspect_baseline_is_recorded_not_mutated() -> None:
    # Read-only: two consecutive inspections agree (no state drift observed).
    first = BOOT_CONTRACT.inspect()
    second = BOOT_CONTRACT.inspect()
    assert first == second
    json.dumps(first)  # bounded, serializable facts only
