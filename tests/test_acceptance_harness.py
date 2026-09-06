from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers.acceptance_harness import (
    ACCEPTANCE_MANIFEST,
    FAKE_MANIFEST_IDS,
    FAKE_PROJECTION_IDS,
    FAKE_PROJECTION_TABLE,
    FAKE_RESULT_SCHEMA_KEYS,
    PUBLIC_REQUEST_BUDGET,
    TAMPER_CASES,
    FakeCutoverRunner,
    StrictFakeQwenObservation,
    build_obligation_gate,
    derive_gap_inventory,
    evaluate_tamper_matrix,
    make_result,
    projection_passes,
)


def test_manifest_is_finite_ordered_and_covers_c_and_d() -> None:
    identifiers = tuple(item.obligation_id for item in ACCEPTANCE_MANIFEST)
    assert identifiers == tuple(dict.fromkeys(identifiers))
    assert identifiers[0] == "C1.1"
    assert identifiers[-1] == "D9"
    assert {item.phase for item in ACCEPTANCE_MANIFEST} == {"C1", "C2", "C3", "C4", "C5", "D"}
    assert all(item.operation and item.expected_observations for item in ACCEPTANCE_MANIFEST)
    assert all(item.stop_dependency and item.evidence_key for item in ACCEPTANCE_MANIFEST)
    assert tuple(item.ordinal for item in PUBLIC_REQUEST_BUDGET) == tuple(range(1, 10))
    assert all(item.maximum == 1 and item.retries == 0 for item in PUBLIC_REQUEST_BUDGET)


def test_gap_inventory_is_source_derived_and_all_historical_signals_are_resolved() -> None:
    source = Path("scripts/gateway_accounting_rehearsal.py").read_text(encoding="utf-8")
    inventory = derive_gap_inventory(source)
    assert len(inventory) == 10
    assert all(not item.present_after_fix for item in inventory)


def test_obligation_gate_requires_complete_observed_passes() -> None:
    results = [
        make_result(item.obligation_id, status="PASSED", observed=True)
        for item in ACCEPTANCE_MANIFEST
    ]
    gate = build_obligation_gate("fake", results)
    assert gate.missing == ()
    assert gate.passed


def test_obligation_gate_is_fail_closed_for_missing_or_retry() -> None:
    result = make_result("C1.1", status="PASSED", observed=True)
    gate = build_obligation_gate("fake", [result], retry_count=1)
    assert gate.missing
    assert gate.first_failure == "retry_count_nonzero"
    assert not gate.passed


def test_runtime_projection_table_is_manifest_complete_and_schema_bounded() -> None:
    assert FAKE_PROJECTION_IDS == FAKE_MANIFEST_IDS
    assert len(FAKE_RESULT_SCHEMA_KEYS) == len(set(FAKE_RESULT_SCHEMA_KEYS))
    assert all(
        projection.proving_test_node_ids[0].endswith("test_projection_positive")
        and projection.proving_test_node_ids[1].endswith("test_projection_negative")
        for projection in FAKE_PROJECTION_TABLE
    )


@pytest.mark.parametrize("projection", FAKE_PROJECTION_TABLE, ids=lambda item: item.obligation_id)
def test_projection_positive(projection: object) -> None:
    source_keys = projection.source_observation_keys  # type: ignore[attr-defined]
    obligation_id = projection.obligation_id  # type: ignore[attr-defined]
    observations = {key: True for key in source_keys}
    assert projection_passes(obligation_id, observations)


@pytest.mark.parametrize("projection", FAKE_PROJECTION_TABLE, ids=lambda item: item.obligation_id)
def test_projection_negative(projection: object) -> None:
    source_keys = projection.source_observation_keys  # type: ignore[attr-defined]
    obligation_id = projection.obligation_id  # type: ignore[attr-defined]
    observations = {key: True for key in source_keys}
    observations[source_keys[-1]] = False
    assert not projection_passes(obligation_id, observations)


def test_strict_fake_observation_is_independent_of_gateway_rows() -> None:
    observation = StrictFakeQwenObservation()
    observation.record(
        {
            "model": "synthetic",
            "input": [{"type": "input_image", "image_url": "synthetic-image-a"}],
            "client_metadata": {
                "session_id": "session-a",
                "thread_id": "thread-a",
                "owner_id": "owner-a",
                "repository_id": "repository-a",
            },
            "tools": [{"type": "function", "name": "shell_command"}],
        }
    )
    observation.record(
        {
            "model": "synthetic",
            "input": [{"type": "input_image", "image_url": "synthetic-image-b"}],
            "client_metadata": {
                "session_id": "session-b",
                "thread_id": "thread-b",
                "owner_id": "owner-b",
                "repository_id": "repository-b",
            },
        }
    )
    facts = observation.snapshot()
    assert facts.call_count == 2
    assert facts.terminal
    assert facts.direct_gateway_rows == 0
    assert facts.image_counts == (1, 1)
    assert observation.isolation_negative_observed()


def test_cutover_runner_is_injectable_and_cleans_each_failure(tmp_path: Path) -> None:
    runner = FakeCutoverRunner(tmp_path / "cutover")
    assert runner.install()
    assert runner.rollback()
    assert runner.safe_facts()["backup_mode"] == "0700"
    assert runner.safe_facts()["backup_file_mode"] == "0600"
    for phase in runner.PHASES:
        failed = FakeCutoverRunner(tmp_path / phase)
        assert not failed.install(failure_phase=phase)
        assert not failed.installed
        assert not failed.rollback_incomplete


def test_cutover_runner_refuses_occupied_candidate_port(tmp_path: Path) -> None:
    runner = FakeCutoverRunner(tmp_path / "occupied", occupied_ports=(18031,))
    assert not runner.install()
    assert runner.events == ["refused_occupied_port"]


def test_tamper_matrix_requires_every_case_and_independent_pre_provider_counts() -> None:
    observations = {case: True for case in TAMPER_CASES}
    facts = evaluate_tamper_matrix(observations, provider_delta=0, accounting_delta=0)
    assert facts.complete

    incomplete = evaluate_tamper_matrix(
        {case: True for case in TAMPER_CASES[:-1]}, provider_delta=0, accounting_delta=0
    )
    assert not incomplete.complete

    circular = evaluate_tamper_matrix(observations, provider_delta=1, accounting_delta=1)
    assert not circular.complete


@pytest.mark.parametrize("bad_status", ["UNKNOWN", "PASS", ""])
def test_safe_result_rejects_open_status_vocabularies(bad_status: str) -> None:
    with pytest.raises(ValueError):
        make_result("C1.1", status=bad_status, observed=False)  # type: ignore[arg-type]
