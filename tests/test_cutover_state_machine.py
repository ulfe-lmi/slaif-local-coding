"""Mechanical cutover state-machine tests (order 010-a, workstream D4/H9-H11).

Synthetic, deterministic fixtures: the state model, the ordered transitions,
and the snapshot/restore assertions from scripts/cutover_state_machine.py.
No live profile, Gateway route, or service is touched.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cutover_state_machine  # noqa: E402

# The repository-only state-machine module is untyped for mypy (resolved at
# runtime via sys.path); its runtime values are used as Any here while every
# assertion below is explicit.
CutoverRun: Any = cutover_state_machine.CutoverRun
CodexProviderClass: Any = cutover_state_machine.CodexProviderClass
LocalListener: Any = cutover_state_machine.LocalListener
PRE_FINAL_MUTATORS: Any = cutover_state_machine.PRE_FINAL_MUTATORS
TRANSITION_ORDER: Any = cutover_state_machine.TRANSITION_ORDER
Transition: Any = cutover_state_machine.Transition
TransitionError: Any = cutover_state_machine.TransitionError
preconditions: Any = cutover_state_machine.preconditions


@pytest.fixture(scope="module")
def snapshot() -> Any:
    return cutover_state_machine.canonical_snapshot("65666f5886832034c52211fdd7604046557e6ada")


def test_transition_set_is_the_runbook_step_set() -> None:
    # The nine runbook steps map one-to-one onto the nine transitions.
    assert TRANSITION_ORDER == (
        Transition.T1_CAPTURE_BASELINE,
        Transition.T2_INSTALL_LOCAL_ARTIFACT,
        Transition.T3_START_CANDIDATE,
        Transition.T4_VERIFY_CANDIDATE,
        Transition.T5_POINT_GATEWAY_TO_ADAPTER,
        Transition.T6_SWITCH_CODEX_PROFILE_TO_GATEWAY,
        Transition.T7_FULL_PATH_SMOKE,
        Transition.T8_ROLLBACK_PROOF,
        Transition.T9_FINAL_SWITCH,
    )
    # H9: the explicit Codex profile switch is a first-class transition.
    assert Transition.T6_SWITCH_CODEX_PROFILE_TO_GATEWAY in TRANSITION_ORDER


def test_happy_path_reaches_final_switch(snapshot: Any) -> None:
    run = CutoverRun(snapshot)
    for transition in TRANSITION_ORDER:
        run.apply(transition)
    assert run.state.cutover_performed is True
    assert run.state.local.listener.value == "loopback_18031"
    assert run.state.gateway.route_backend.value == "adapter_loopback_18031"
    assert run.state.codex.provider_class is CodexProviderClass.GATEWAY_ENTRY


def test_transitions_reject_out_of_order_application(snapshot: Any) -> None:
    run = CutoverRun(snapshot)
    with pytest.raises(TransitionError, match="transition_out_of_order"):
        run.apply(Transition.T3_START_CANDIDATE)


def test_codex_profile_switch_precedes_full_path_smoke(snapshot: Any) -> None:
    # (a) Strict ordering: the smoke cannot be applied before the switch.
    run = CutoverRun(snapshot)
    run.apply_until(Transition.T6_SWITCH_CODEX_PROFILE_TO_GATEWAY)
    with pytest.raises(TransitionError, match="transition_out_of_order"):
        run.apply(Transition.T7_FULL_PATH_SMOKE)
    # (b) State precondition: even if the switch were recorded as applied, a
    # state where the profile was not actually switched rejects the smoke.
    unswitched = cutover_state_machine._mutate(snapshot, Transition.T5_POINT_GATEWAY_TO_ADAPTER)
    with pytest.raises(TransitionError, match="codex_profile_not_switched_to_gateway"):
        preconditions(unswitched, frozenset(TRANSITION_ORDER[:6]))


def test_gateway_route_must_target_adapter_before_profile_switch(snapshot: Any) -> None:
    run = CutoverRun(snapshot)
    run.apply_until(Transition.T5_POINT_GATEWAY_TO_ADAPTER)
    with pytest.raises(TransitionError, match="gateway_route_not_pointing_at_adapter"):
        preconditions(run.state, frozenset(TRANSITION_ORDER[:5]))


def test_rollback_restores_full_snapshot_from_every_pre_final_failure_point(snapshot: Any) -> None:
    for failed_at in TRANSITION_ORDER[:-1]:
        run = CutoverRun(snapshot)
        run.apply_until(failed_at)
        restored = run.rollback(failed_at)
        assert restored == snapshot, (failed_at, restored)
        # All three tracked state groups are restored, not merely one route.
        assert restored.local == snapshot.local, failed_at
        assert restored.gateway == snapshot.gateway, failed_at
        assert restored.codex == snapshot.codex, failed_at
        # No forgotten listener after any rollback.
        assert restored.local.listener.value == "none", failed_at


def test_every_pre_final_mutating_transition_has_a_defined_inverse(snapshot: Any) -> None:
    # H11: rollback is defined for every pre-final-switch failure point.
    pre_final = TRANSITION_ORDER[:-1]
    mutators_without_inverse = PRE_FINAL_MUTATORS - set(pre_final)
    assert mutators_without_inverse == frozenset()
    for transition in PRE_FINAL_MUTATORS:
        run = CutoverRun(snapshot)
        run.apply_until(transition)
        run.apply(transition)
        restored = run.rollback(transition)
        assert restored == snapshot, transition


def test_post_final_switch_rollback_is_rejected(snapshot: Any) -> None:
    run = CutoverRun(snapshot)
    for transition in TRANSITION_ORDER:
        run.apply(transition)
    with pytest.raises(TransitionError, match="no_rollback_after_final_switch"):
        run.rollback(Transition.T9_FINAL_SWITCH)


def test_start_requires_free_18031(snapshot: Any) -> None:
    occupied = cutover_state_machine.replace(
        snapshot,
        local=cutover_state_machine.replace(
            snapshot.local,
            listener=LocalListener.LOOPBACK_18031,
        ),
    )
    # Start with the port occupied (e.g. a forgotten pre-existing listener):
    run = CutoverRun(occupied)
    run.apply(Transition.T1_CAPTURE_BASELINE)
    run.apply(Transition.T2_INSTALL_LOCAL_ARTIFACT)
    with pytest.raises(TransitionError, match="loopback_18031_must_be_free"):
        run.apply(Transition.T3_START_CANDIDATE)


def test_self_test_cli_contract() -> None:
    facts = cutover_state_machine.self_test()
    assert facts["ok"] is True
    assert facts["transitions"] == 9
    assert facts["rollback_points_checked"] == 8
