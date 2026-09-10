from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest

from tests.helpers.acceptance_harness import (
    ACCEPTANCE_MANIFEST,
    FAKE_MANIFEST_IDS,
    FAKE_PROJECTION_IDS,
    FAKE_PROJECTION_TABLE,
    FAKE_RESULT_SCHEMA_KEYS,
    PROTECTED_MANIFEST_IDS,
    PROTECTED_PROJECTION_IDS,
    PROTECTED_PROJECTION_TABLE,
    PUBLIC_REQUEST_BUDGET,
    TAMPER_CASES,
    BudgetController,
    DispatchContext,
    FakeCutoverRunner,
    RehearsalBudget,
    RunAccumulator,
    StrictFakeQwenObservation,
    build_obligation_gate,
    derive_gap_inventory,
    evaluate_tamper_matrix,
    make_result,
    projection_passes,
    projection_table_for,
    run_protected_mode_conformance,
    validate_projection_contract,
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


def test_protected_projection_table_is_complete_and_has_direct_fixture_source() -> None:
    assert PROTECTED_PROJECTION_IDS == PROTECTED_MANIFEST_IDS
    assert PROTECTED_PROJECTION_TABLE[-1].obligation_id == "C5.4"
    assert PROTECTED_PROJECTION_TABLE[-1].producer == "protected_fixture_snapshot_before_cleanup"
    validate_projection_contract("fake")
    validate_projection_contract("protected")


@pytest.mark.parametrize(
    "mutation",
    (
        lambda table: table[:-1],
        lambda table: table[:1] + (table[0],) + table[1:],
        lambda table: tuple(reversed(table)),
        lambda table: (
            table[:-1]
            + (
                table[-1].__class__(
                    "unknown", table[-1].source_observation_keys, "producer", ("a", "b")
                ),
            )
        ),
    ),
)
def test_projection_contract_rejects_missing_duplicate_reordered_and_unknown(
    mutation: object,
) -> None:
    table = tuple(mutation(projection_table_for("protected")))  # type: ignore[operator]
    with pytest.raises(ValueError, match="projection|duplicate"):
        validate_projection_contract("protected", table)


def test_budget_controller_enforces_admission_before_dispatch() -> None:
    now = [100.0]
    budget = RehearsalBudget(
        wall_seconds=5.0,
        operation_limits=(PUBLIC_REQUEST_BUDGET[0],),
        max_event_bytes=4,
        max_stream_bytes=6,
        max_concurrency=1,
    )
    controller = BudgetController(budget, clock=lambda: now[0])
    assert controller.admit("codex_turn_1", lifetime_id="test")
    assert not controller.admit("codex_turn_1", lifetime_id="test")
    assert controller.failure == "budget_operation_limit_exhausted"

    now[0] = 100.0
    expired = BudgetController(budget, clock=lambda: now[0])
    now[0] = 106.0
    assert not expired.admit("codex_turn_1", lifetime_id="test")
    assert expired.failure == "budget_deadline_exhausted"

    bounded = BudgetController(budget)
    assert bounded.admit("codex_turn_1", lifetime_id="test")
    assert bounded.activate_operation("codex_turn_1", phase="codex", ordinal=1, lifetime_id="test")
    assert bounded.admit_dispatch("compiler")
    assert bounded.begin_response()
    assert bounded.observe_event(4)
    assert not bounded.observe_event(3)
    assert bounded.failure == "budget_stream_limit_exhausted"


def test_dispatch_permission_is_explicit_per_operation_and_consumed() -> None:
    controller = BudgetController()

    assert not controller.admit_dispatch("inference")
    assert controller.failure == "budget_dispatch_permission_missing"

    controller = BudgetController()
    assert controller.admit("codex_turn_1", phase="codex", ordinal=1, lifetime_id="test")
    assert controller.activate_operation(
        "codex_turn_1", phase="codex", ordinal=1, lifetime_id="test"
    )
    assert controller.admit_dispatch("inference")
    controller.release_dispatch()
    assert not controller.admit_dispatch("inference")
    assert controller.failure == "budget_dispatch_permission_kind_mismatch"


def test_dispatch_permission_rejects_wrong_phase_and_cross_lifetime_reuse() -> None:
    controller = BudgetController()
    assert controller.admit("codex_turn_1", phase="codex", ordinal=1, lifetime_id="test")
    assert controller.activate_operation(
        "codex_turn_1", phase="codex", ordinal=1, lifetime_id="test"
    )
    controller.set_dispatch_context("codex_turn_1", "vision", 3, "test")
    assert not controller.admit_dispatch("inference")
    assert controller.failure == "budget_dispatch_context_mismatch"

    fresh_lifetime = BudgetController()
    assert not fresh_lifetime.admit_dispatch("inference")
    assert fresh_lifetime.failure == "budget_dispatch_permission_missing"


def test_dispatch_never_borrows_a_pending_next_operation() -> None:
    controller = BudgetController()
    assert controller.admit("codex_turn_1", lifetime_id="codex")
    assert controller.admit("codex_turn_2", lifetime_id="codex")
    assert controller.activate_operation(
        "codex_turn_1", phase="codex", ordinal=1, lifetime_id="codex"
    )
    for kind in ("compiler", "compiler", "inference"):
        assert controller.admit_dispatch(kind)
        controller.release_dispatch()
    assert not controller.admit_dispatch("inference")
    assert controller.failure == "budget_dispatch_permission_exhausted"


def test_dispatch_requires_the_currently_activated_operation_context() -> None:
    controller = BudgetController()
    assert controller.admit("codex_turn_1", lifetime_id="codex")
    assert controller.admit("codex_turn_2", lifetime_id="codex")
    assert controller.activate_operation(
        "codex_turn_1", phase="codex", ordinal=1, lifetime_id="codex"
    )
    assert not controller.admit_dispatch(
        "inference",
        context=DispatchContext("codex_turn_2", "codex", 2, "codex"),
    )
    assert controller.failure == "budget_dispatch_context_mismatch"


def test_readiness_permission_is_one_shot_bounded_and_retired() -> None:
    controller = BudgetController(
        RehearsalBudget(operation_limits=(), dispatch_plan=(), max_readiness_probes=1)
    )
    assert controller.admit_readiness(lifetime_id="candidate")
    assert controller.activate_readiness(lifetime_id="candidate")
    assert controller.admit_dispatch(
        "other", context=DispatchContext("readiness_probe", "candidate", 0, "candidate")
    )
    controller.release_dispatch()
    assert controller.safe_dict()["readiness_consumed_count"] == 1
    assert controller.safe_dict()["readiness_pending"] is False
    assert controller.dispatch_context() is None
    assert not controller.admit_readiness(lifetime_id="second")
    assert controller.failure == "budget_readiness_limit_exhausted"


def test_provider_preflight_permissions_are_endpoint_scoped_and_one_shot() -> None:
    controller = BudgetController(
        RehearsalBudget(operation_limits=(), dispatch_plan=(), max_provider_preflight_probes=2)
    )
    assert controller.admit_provider_probe("/health")
    assert controller.activate_provider_probe("/health")
    assert controller.dispatch_context() == DispatchContext(
        "provider_probe", "preflight", 0, "provider_preflight", "/health", "GET"
    )
    assert controller.admit_dispatch("other")
    controller.release_dispatch()
    assert controller.dispatch_context() is None
    assert controller.admit_provider_probe("/v1/models")
    assert controller.activate_provider_probe("/v1/models")
    assert controller.admit_dispatch("other")
    controller.release_dispatch()
    facts = controller.safe_dict()
    assert facts["provider_probe_consumed_count"] == 2
    assert facts["provider_probe_pending"] is False
    assert not controller.admit_provider_probe("/v1/responses")
    assert controller.failure == "budget_provider_probe_context_mismatch"


def test_dispatch_transition_requires_explicit_activation_and_records_new_context() -> None:
    controller = BudgetController()
    assert controller.admit("codex_turn_1", lifetime_id="codex")
    assert controller.admit("codex_turn_2", lifetime_id="codex")
    assert controller.activate_operation(
        "codex_turn_1", phase="codex", ordinal=1, lifetime_id="codex"
    )
    for kind in ("compiler", "compiler", "inference"):
        assert controller.admit_dispatch(kind)
        controller.release_dispatch()
    assert controller.activate_operation(
        "codex_turn_2", phase="codex", ordinal=2, lifetime_id="codex"
    )
    assert controller.admit_dispatch("inference")
    record = controller.safe_dict()["dispatch_records"][-1]  # type: ignore[index]
    assert record["operation"] == "codex_turn_2"
    assert record["ordinal"] == 2


def test_dispatch_rejects_stale_lifetime_and_expiry_between_operations() -> None:
    now = [0.0]
    budget = RehearsalBudget(wall_seconds=5.0)
    controller = BudgetController(budget, clock=lambda: now[0])
    assert controller.admit("codex_turn_1", lifetime_id="old")
    assert controller.activate_operation(
        "codex_turn_1", phase="codex", ordinal=1, lifetime_id="old"
    )
    controller.set_dispatch_context("codex_turn_1", "codex", 1, "new")
    assert not controller.admit_dispatch("inference")
    assert controller.failure == "budget_dispatch_lifetime_mismatch"

    now = [0.0]
    expired = BudgetController(budget, clock=lambda: now[0])
    assert expired.admit("codex_turn_1", lifetime_id="codex")
    now[0] = 5.0
    assert not expired.activate_operation(
        "codex_turn_1", phase="codex", ordinal=1, lifetime_id="codex"
    )
    assert expired.failure == "budget_deadline_exhausted"


def test_run_accumulator_preserves_primary_failure_and_counts_before_cleanup() -> None:
    accumulator = RunAccumulator("protected", candidate_sha="a" * 40, gateway_sha="b" * 40)
    accumulator.capture_observer(
        {
            "ready": False,
            "failure_class": "manual_unready",
            "compiler_attempted_count": 1,
            "compiler_dispatched_count": 1,
            "compiler_responded_count": 1,
            "compiler_completed_count": 1,
            "inference_attempted_count": 2,
            "inference_dispatched_count": 1,
            "inference_responded_count": 0,
            "inference_completed_count": 0,
        },
        phase="codex",
        ordinal=2,
    )
    accumulator.record_failure("provider_boundary_unobserved")
    accumulator.record_failure("serialization_failure")
    accumulator.record_cleanup(
        {"processes": True, "listeners": True, "database": True, "cache": True, "codex_home": True}
    )
    facts = accumulator.safe_dict()
    assert facts["mode"] == "protected"
    assert facts["first_failure"] == "observer_readiness_lost"
    assert facts["secondary_failures"] == ("provider_boundary_unobserved", "serialization_failure")
    assert facts["counts"]["inference_attempted"] == 2  # type: ignore[index]
    encoded = json.dumps(facts)
    assert "a" * 40 in encoded
    assert "b" * 40 in encoded
    assert "manual_unready" not in encoded


def test_run_accumulator_uses_semantic_terminal_facts_not_lifecycle_counts() -> None:
    accumulator = RunAccumulator("protected")
    accumulator.capture_observer(
        {
            "ready": False,
            "failure_class": "stream_validation_invalid",
            "inference_attempted_count": 1,
            "inference_dispatched_count": 1,
            "inference_responded_count": 1,
            "inference_completed_count": 1,
            "inference_terminal_valid_count": 0,
            "records": (
                {
                    "ordinal": 1,
                    "kind": "inference",
                    "terminal_valid": False,
                    "completed": True,
                    "normal_close": True,
                },
            ),
        },
        phase="codex",
        ordinal=2,
        lifetime_id="counterexample",
    )
    facts = accumulator.safe_dict()
    assert facts["first_failure"] == "stream_validation_invalid"
    assert facts["counts"]["inference_attempted"] == 1  # type: ignore[index]
    assert facts["counts"]["inference_completed"] == 1  # type: ignore[index]
    assert facts["counts"]["inference_terminal_valid"] == 0  # type: ignore[index]
    assert facts["terminal_classes"] == ("terminal_invalid",)
    assert "terminal_valid" not in facts["terminal_classes"]


def test_run_accumulator_preserves_unknown_and_incomplete_terminal_observations() -> None:
    accumulator = RunAccumulator("protected")
    accumulator.capture_observer(
        {
            "ready": True,
            "inference_attempted_count": 1,
            "inference_dispatched_count": 0,
            "inference_responded_count": 0,
            "inference_completed_count": 0,
        },
        phase="preflight",
        ordinal=0,
        lifetime_id="absent",
    )
    accumulator.capture_observer(
        {
            "ready": False,
            "failure_class": "cancelled",
            "inference_attempted_count": 1,
            "inference_dispatched_count": 1,
            "inference_responded_count": 1,
            "inference_completed_count": 0,
            "inference_terminal_valid_count": 0,
            "records": (
                {
                    "ordinal": 1,
                    "kind": "inference",
                    "terminal_valid": False,
                    "completed": False,
                    "normal_close": False,
                },
            ),
        },
        phase="codex",
        ordinal=1,
        lifetime_id="cancelled",
    )
    facts = accumulator.safe_dict()
    assert facts["terminal_classes"] == ("unknown", "terminal_incomplete")
    assert facts["first_failure"] == "cancelled"


def test_run_accumulator_sums_distinct_lifetimes_and_does_not_double_count_updates() -> None:
    accumulator = RunAccumulator("fake")
    valid_record = {
        "ordinal": 1,
        "kind": "inference",
        "terminal_valid": True,
        "completed": True,
        "normal_close": True,
    }
    accumulator.capture_observer(
        {
            "ready": True,
            "inference_attempted_count": 1,
            "inference_dispatched_count": 1,
            "inference_responded_count": 1,
            "inference_completed_count": 1,
            "inference_terminal_valid_count": 1,
            "records": (valid_record,),
        },
        phase="vision",
        ordinal=1,
        lifetime_id="first",
    )
    accumulator.capture_observer(
        {
            "ready": True,
            "inference_attempted_count": 1,
            "inference_dispatched_count": 1,
            "inference_responded_count": 1,
            "inference_completed_count": 1,
            "inference_terminal_valid_count": 1,
            "records": (valid_record,),
        },
        phase="vision",
        ordinal=1,
        lifetime_id="second",
    )
    accumulator.capture_observer(
        {
            "ready": True,
            "inference_attempted_count": 0,
            "inference_dispatched_count": 0,
            "inference_responded_count": 0,
            "inference_completed_count": 0,
            "inference_terminal_valid_count": 0,
            "records": (),
        },
        phase="vision",
        ordinal=1,
        lifetime_id="first",
    )
    facts = accumulator.safe_dict()
    assert facts["counts"]["inference_attempted"] == 2  # type: ignore[index]
    assert facts["counts"]["inference_terminal_valid"] == 2  # type: ignore[index]
    assert facts["all_lifetime_counts"] == facts["counts"]
    lifetime_counts = cast(dict[str, object], facts["lifetime_counts"])
    snapshots = cast(tuple[dict[str, object], ...], facts["snapshots"])
    assert set(lifetime_counts) == {"first", "second"}
    assert all(snapshot["lifetime_id"] in {"first", "second"} for snapshot in snapshots)
    assert facts["terminal_classes"] == ("terminal_valid", "terminal_valid")


def test_run_accumulator_retains_completed_phase_and_first_failure_context() -> None:
    accumulator = RunAccumulator("fake")
    accumulator.capture_observer(
        {
            "ready": True,
            "failure_class": None,
            "compiler_attempted_count": 1,
            "compiler_dispatched_count": 1,
            "compiler_responded_count": 1,
            "compiler_completed_count": 1,
            "inference_attempted_count": 1,
            "inference_dispatched_count": 1,
            "inference_responded_count": 1,
            "inference_completed_count": 1,
            "inference_terminal_valid_count": 1,
            "records": (
                {
                    "ordinal": 1,
                    "kind": "inference",
                    "completed": True,
                    "normal_close": True,
                    "terminal_valid": True,
                    "response_received_bytes": 100,
                    "response_accepted_bytes": 100,
                    "response_rejected_bytes": 0,
                    "response_rejected_chunk_count": 0,
                },
            ),
            "dispatch_budget": {
                "max_stream_bytes": 131072,
                "response_received_bytes_total": 100,
                "response_accepted_bytes_total": 100,
                "response_rejected_bytes_total": 0,
                "response_rejected_chunks_total": 0,
                "stream_bytes_total": 100,
            },
        },
        phase="codex",
        ordinal=2,
        lifetime_id="codex",
    )
    accumulator.capture_observer(
        {
            "ready": False,
            "failure_class": "budget_stream_limit_exhausted",
            "failure_context": {
                "kind": "inference",
                "operation": "vision_full",
                "phase": "vision",
                "ordinal": 3,
                "lifetime_id": "vision",
                "cause": "budget_stream_limit_exhausted",
            },
            "inference_attempted_count": 1,
            "inference_dispatched_count": 1,
            "inference_responded_count": 1,
            "inference_completed_count": 0,
            "inference_terminal_valid_count": 0,
            "records": (
                {
                    "ordinal": 1,
                    "kind": "inference",
                    "completed": False,
                    "normal_close": False,
                    "terminal_valid": False,
                    "response_received_bytes": 131073,
                    "response_accepted_bytes": 131072,
                    "response_rejected_bytes": 1,
                    "response_rejected_chunk_count": 1,
                },
            ),
            "dispatch_budget": {
                "max_stream_bytes": 131072,
                "response_received_bytes_total": 131173,
                "response_accepted_bytes_total": 131172,
                "response_rejected_bytes_total": 1,
                "response_rejected_chunks_total": 1,
                "stream_bytes_total": 131172,
            },
        },
        phase="vision",
        ordinal=3,
        lifetime_id="vision",
    )
    accumulator.record_failure("serialization_failure")
    accumulator.record_cleanup(
        {"processes": True, "listeners": True, "database": True, "cache": False}
    )
    facts = accumulator.safe_dict()
    assert facts["first_failure"] == "budget_stream_limit_exhausted"
    assert facts["first_failure_context"] == {
        "kind": "inference",
        "operation": "vision_full",
        "phase": "vision",
        "ordinal": 3,
        "lifetime_id": "vision",
        "cause": "budget_stream_limit_exhausted",
    }
    assert facts["counts"]["compiler_completed"] == 1  # type: ignore[index]
    assert facts["counts"]["inference_attempted"] == 2  # type: ignore[index]
    completed = cast(tuple[dict[str, object], ...], facts["completed_phases"])
    assert [(item["phase"], item["lifetime_id"]) for item in completed] == [("codex", "codex")]
    byte_evidence = cast(tuple[dict[str, object], ...], facts["response_byte_evidence"])
    vision_bytes = next(item for item in byte_evidence if item["lifetime_id"] == "vision")
    assert vision_bytes["responses"] == (
        {
            "ordinal": 1,
            "kind": "inference",
            "received_bytes": 131073,
            "accepted_bytes": 131072,
            "rejected_bytes": 1,
            "rejected_chunk_count": 1,
        },
    )
    assert facts["secondary_failures"] == (
        "observer_readiness_lost",
        "serialization_failure",
        "cleanup_failed",
    )


def test_run_accumulator_retains_bounded_semantic_phase_facts() -> None:
    accumulator = RunAccumulator("protected")
    accumulator.record_phase_facts(
        {
            "codex": {"status": "PASSED", "client_verification": {"status": "PASSED"}},
            "provider": {"request_class_classes": ("function_initial",)},
        },
        phase="codex",
        ordinal=2,
        lifetime_id="codex",
    )
    accumulator.capture_observer(
        {"ready": True, "failure_class": None},
        phase="codex",
        ordinal=2,
        lifetime_id="codex",
    )
    accumulator.record_phase_facts(
        {"raw_body": b"must-not-cross", "nested": {"value": "safe"}},
        phase="vision",
        ordinal=3,
        lifetime_id="vision",
    )
    facts = accumulator.safe_dict()
    checkpoints = cast(tuple[dict[str, object], ...], facts["phase_checkpoints"])
    codex = next(item for item in checkpoints if item["lifetime_id"] == "codex")
    assert codex["evidence_kind"] == "semantic"
    assert codex["phase_facts"] == {
        "codex": {"status": "PASSED", "client_verification": {"status": "PASSED"}},
        "provider": {"request_class_classes": ("function_initial",)},
    }
    encoded = json.dumps(facts)
    assert "must-not-cross" not in encoded
    assert "raw_body" in encoded


def test_protected_mode_conformance_is_injected_and_never_reads_credentials() -> None:
    calls: list[str] = []
    result = run_protected_mode_conformance(
        preflight=lambda: {"ready": True},
        candidate=lambda: {"ready": True},
        dispatch=lambda phase: {"direct_transport_observed": True, "terminal_observed": True},
        cleanup=lambda: {"complete": True},
        credential_hook=lambda: calls.append("credential"),
    )
    assert result["status"] == "FAILED"
    assert result["mode"] == "protected"
    assert result["credential_reads"] == 0
    assert result["credential_hook_not_called"] is True
    assert result["rows_serialized"] is True
    assert result["selected_rows_passed"] is False
    assert result["protected_acceptance"] is False
    projection_rows = cast(tuple[dict[str, object], ...], result["projection_table"])
    assert all(row["execution_status"] == "NOT RUN" for row in projection_rows)
    assert calls == []


def test_protected_mode_conformance_stops_after_first_failure_and_cleans_up() -> None:
    phases: list[str] = []

    def dispatch(phase: str) -> dict[str, object]:
        phases.append(phase)
        return {"direct_transport_observed": False}

    result = run_protected_mode_conformance(
        preflight=lambda: {"ready": True},
        candidate=lambda: {"ready": True},
        dispatch=dispatch,
        cleanup=lambda: {"complete": True},
    )
    assert result["status"] == "FAILED"
    assert result["first_failure"] == "provider_boundary_unobserved"
    assert result["later_dispatch_count"] == 0
    assert result["cleanup_snapshot_available"] is True
    assert phases == ["dispatch"]


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
