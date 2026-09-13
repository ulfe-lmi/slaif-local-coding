"""Self-tests for the strict current-peer fixture and runner predicates."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from scripts.gateway_contract import (
    CURRENT_FIXTURE,
    CheckoutFacts,
    ContractGateError,
    _write_github_outputs,
    enforce_test_result,
    load_peer_authority,
    network_denial_guard,
    validate_checkout_facts,
    validate_runtime_contract,
)
from scripts.gateway_contract import (
    TestRunResult as StrictTestRunResult,
)


def test_fixture_has_one_strict_current_authority() -> None:
    authority = load_peer_authority()
    assert authority.repository == "ulfe-lmi/slaif-api-gateway"
    assert len(authority.commit) == 40
    assert authority.server_module_id == "local-coding-v1"
    assert authority.client_module_version == "4"


def test_exact_checkout_facts_are_accepted(tmp_path: Path) -> None:
    authority = load_peer_authority()
    root = tmp_path.resolve()
    for relative in (
        "app/slaif_gateway/modules/servers/local_coding/contract.py",
        "app/slaif_gateway/modules/clients/codex_0149.py",
        "app/slaif_gateway/providers/streaming.py",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    facts = CheckoutFacts(
        root=root,
        head=authority.commit,
        origin=f"https://github.com/{authority.repository}.git",
        expected_paths=(
            "app/slaif_gateway/modules/servers/local_coding/contract.py",
            "app/slaif_gateway/modules/clients/codex_0149.py",
            "app/slaif_gateway/providers/streaming.py",
        ),
        clean=True,
    )
    validate_checkout_facts(facts, authority)


@pytest.mark.parametrize(
    ("change", "error"),
    (
        ("head", "gateway_sha_mismatch"),
        ("origin", "gateway_repository_mismatch"),
        ("root", "gateway_root_invalid"),
        ("clean", "gateway_checkout_dirty"),
    ),
)
def test_wrong_checkout_facts_fail_closed(tmp_path: Path, change: str, error: str) -> None:
    authority = load_peer_authority()
    root = tmp_path.resolve()
    for relative in (
        "app/slaif_gateway/modules/servers/local_coding/contract.py",
        "app/slaif_gateway/modules/clients/codex_0149.py",
        "app/slaif_gateway/providers/streaming.py",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    facts = CheckoutFacts(
        root=root,
        head=authority.commit,
        origin=f"https://github.com/{authority.repository}",
        expected_paths=(
            "app/slaif_gateway/modules/servers/local_coding/contract.py",
            "app/slaif_gateway/modules/clients/codex_0149.py",
            "app/slaif_gateway/providers/streaming.py",
        ),
        clean=True,
    )
    if change == "head":
        facts = replace(facts, head="0" * 40)
    elif change == "origin":
        facts = replace(facts, origin="https://github.com/other/repository")
    elif change == "root":
        facts = replace(facts, root=Path("/owned/gateway/../other").resolve())
    else:
        facts = replace(facts, clean=False)
    with pytest.raises(ContractGateError, match=error):
        validate_checkout_facts(facts, authority)


@pytest.mark.parametrize(
    "mutation",
    (
        {"unknown": True},
        {"commit": "not-a-sha"},
        {"server": {"module_id": "local-coding-v1"}},
    ),
)
def test_malformed_or_unknown_fixture_fails_closed(
    tmp_path: Path, mutation: dict[str, object]
) -> None:
    raw = json.loads(CURRENT_FIXTURE.read_text(encoding="utf-8"))
    raw.update(mutation)
    path = tmp_path / "authority.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ContractGateError):
        load_peer_authority(path)


@pytest.mark.parametrize(
    ("field", "output_field"),
    (
        ("repository", "repository"),
        ("commit", "commit"),
        ("server_module_id", "server_module_id"),
        ("server_module_version", "server_module_version"),
        ("replay_mode", "server_replay_mode"),
        ("client_module_id", "client_module_id"),
        ("client_module_version", "client_module_version"),
    ),
)
def test_github_output_rejects_newline_injection_for_every_fixture_value(
    tmp_path: Path, field: str, output_field: str
) -> None:
    authority = load_peer_authority()
    malicious = "safe\r\ninjected"
    if field == "repository":
        mutated = replace(authority, repository=malicious)
    elif field == "commit":
        mutated = replace(authority, commit=malicious)
    elif field == "server_module_id":
        mutated = replace(authority, server_module_id=malicious)
    elif field == "server_module_version":
        mutated = replace(authority, server_module_version=malicious)
    elif field == "replay_mode":
        mutated = replace(authority, replay_mode=malicious)
    elif field == "client_module_id":
        mutated = replace(authority, client_module_id=malicious)
    else:
        mutated = replace(authority, client_module_version=malicious)
    output = tmp_path / "github-output"
    with pytest.raises(ContractGateError, match=f"github_output_{output_field}_invalid"):
        _write_github_outputs(output, mutated)
    assert not output.exists()


def test_incompatible_runtime_fact_is_not_normalized() -> None:
    authority = load_peer_authority()
    facts = {
        "server_module_id": authority.server_module_id,
        "server_module_version": authority.server_module_version,
        "replay_mode": authority.replay_mode,
        "client_module_id": authority.client_module_id,
        "client_module_version": authority.client_module_version,
        "validator_class": "ResponsesStreamEventValidator",
        "profile_class": "ResponsesStreamValidationProfile",
    }
    with pytest.raises(ContractGateError, match="gateway_runtime_contract_mismatch"):
        validate_runtime_contract({**facts, "replay_mode": "legacy"}, authority)


def test_historical_objective_005_pin_remains_distinct() -> None:
    from tests.helpers.gateway_accounting_rehearsal import GATEWAY_MAIN_SHA

    authority = load_peer_authority()
    assert GATEWAY_MAIN_SHA == "5ea38325ef3a3ebc69524b4679b795fab0c52935"
    assert GATEWAY_MAIN_SHA != authority.commit


def test_strict_result_gate_rejects_skip_and_zero_collection() -> None:
    with pytest.raises(ContractGateError):
        enforce_test_result(
            StrictTestRunResult(collected=1, passed=0, skipped=1, failed=0, errors=0)
        )
    with pytest.raises(ContractGateError):
        enforce_test_result(
            StrictTestRunResult(collected=0, passed=0, skipped=0, failed=0, errors=0)
        )
    enforce_test_result(StrictTestRunResult(collected=2, passed=2, skipped=0, failed=0, errors=0))


def test_network_guard_trips_without_network() -> None:
    with network_denial_guard(), pytest.raises(RuntimeError) as caught:
        socket.create_connection(("127.0.0.1", 1), timeout=0.01)
    assert type(caught.value).__name__ == "NetworkAccessDenied"


def test_no_root_developer_contract_modules_skip_successfully() -> None:
    environment = os.environ.copy()
    environment.pop("SLAIF_GATEWAY_ROOT", None)
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-rs",
            "tests/test_gateway162_validator_factory.py",
            "tests/test_current_gateway_contract.py",
        ],
        cwd=Path(__file__).resolve().parents[1],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    output = f"{completed.stdout}\n{completed.stderr}".lower()
    assert completed.returncode == 0
    assert "skipped" in output
    assert "failed" not in output
