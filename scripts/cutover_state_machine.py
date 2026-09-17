"""Cutover state machine (order 010-a, workstream D4; 011-a G1).

Pure, deterministic model of the cutover runbook in
docs/RELEASE-CUTOVER-RUNBOOK.md: three independent tracked states
(LOCAL / GATEWAY / CODEX), an ordered transition list T1..T9 with
fail-closed preconditions, the step-1 snapshot, and the complete inverse
(rollback) from every pre-final-switch failure point.

This module performs no I/O and no mutation: it is the mechanical
underpinning of the runbook and is exercised by
tests/test_cutover_state_machine.py. The ``--self-test`` CLI re-runs the
same deterministic assertions and prints one bounded JSON line.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, replace
from enum import StrEnum


class LocalServiceState(StrEnum):
    STOPPED = "stopped"
    READY = "ready"


class LocalListener(StrEnum):
    NONE = "none"
    LOOPBACK_18031 = "loopback_18031"
    LAN_18031_SIGNED = "lan_18031_signed"


class LocalBindingClass(StrEnum):
    """D1 binding law class of the local 18031 bind (order 011-a, G1).

    ``loopback_18031`` is the loopback-only bind (the only class legal
    without the full signed ingress contract); ``lan_18031_signed`` is the
    LAN-visible bind, legal only under ``service_bearer_signed_identity_v1``.
    """

    LOOPBACK_18031 = "loopback_18031"
    LAN_18031_SIGNED = "lan_18031_signed"


class LocalArtifactClass(StrEnum):
    PREVIOUS = "previous"
    RELEASE_CANDIDATE = "release_candidate"


class LocalConfigLabel(StrEnum):
    PREVIOUS = "previous"
    GATEWAY_INTEGRATED = "gateway_integrated"


class GatewayRouteBackend(StrEnum):
    DIRECT_UPSTREAM = "direct_upstream"
    ADAPTER_LOOPBACK_18031 = "adapter_loopback_18031"


class CodexProviderClass(StrEnum):
    PRE_CUTOVER = "pre_cutover_provider"
    GATEWAY_ENTRY = "gateway_entry"


@dataclass(frozen=True, slots=True)
class LocalState:
    artifact_sha256: LocalArtifactClass
    config_label: LocalConfigLabel
    binding_class: LocalBindingClass
    service_state: LocalServiceState
    listener: LocalListener


@dataclass(frozen=True, slots=True)
class GatewayState:
    route_backend: GatewayRouteBackend
    authority_sha: str
    signed_contract: bool


@dataclass(frozen=True, slots=True)
class CodexState:
    provider_class: CodexProviderClass


@dataclass(frozen=True, slots=True)
class CutoverState:
    local: LocalState
    gateway: GatewayState
    codex: CodexState
    cutover_performed: bool = False


class Transition(StrEnum):
    T1_CAPTURE_BASELINE = "t1_capture_baseline"
    T2_INSTALL_LOCAL_ARTIFACT = "t2_install_local_artifact"
    T3_START_CANDIDATE = "t3_start_candidate"
    T4_VERIFY_CANDIDATE = "t4_verify_candidate"
    T5_POINT_GATEWAY_TO_ADAPTER = "t5_point_gateway_to_adapter"
    T6_SWITCH_CODEX_PROFILE_TO_GATEWAY = "t6_switch_codex_profile_to_gateway"
    T7_FULL_PATH_SMOKE = "t7_full_path_smoke"
    T8_ROLLBACK_PROOF = "t8_rollback_proof"
    T9_FINAL_SWITCH = "t9_final_switch"


TRANSITION_ORDER = tuple(Transition)
# Mutating transitions strictly before the final switch; each one has an
# inverse used by rollback. T1 captures and T4/T7/T8 verify or are net-zero.
PRE_FINAL_MUTATORS = frozenset(
    {
        Transition.T2_INSTALL_LOCAL_ARTIFACT,
        Transition.T3_START_CANDIDATE,
        Transition.T5_POINT_GATEWAY_TO_ADAPTER,
        Transition.T6_SWITCH_CODEX_PROFILE_TO_GATEWAY,
    }
)


class TransitionError(Exception):
    """Fixed-class rejection; never carries state contents."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def preconditions(state: CutoverState, applied: frozenset[Transition]) -> None:
    """Fail-closed preconditions for the next transition in order."""
    expected_index = len([t for t in TRANSITION_ORDER if t in applied])
    next_transition = TRANSITION_ORDER[expected_index]
    if next_transition is Transition.T1_CAPTURE_BASELINE:
        if state.cutover_performed:
            raise TransitionError("baseline_capture_after_final_switch")
        return
    if next_transition is Transition.T2_INSTALL_LOCAL_ARTIFACT:
        if state.local.service_state is not LocalServiceState.STOPPED:
            raise TransitionError("local_service_must_be_stopped_for_install")
        return
    if next_transition is Transition.T3_START_CANDIDATE:
        if state.local.listener is not LocalListener.NONE:
            raise TransitionError("loopback_18031_must_be_free")
        if state.local.artifact_sha256 is not LocalArtifactClass.RELEASE_CANDIDATE:
            raise TransitionError("release_candidate_not_installed")
        return
    if next_transition is Transition.T4_VERIFY_CANDIDATE:
        if state.local.service_state is not LocalServiceState.READY:
            raise TransitionError("candidate_not_ready")
        return
    if next_transition is Transition.T5_POINT_GATEWAY_TO_ADAPTER:
        if state.local.service_state is not LocalServiceState.READY:
            raise TransitionError("candidate_not_ready")
        if state.gateway.route_backend is not GatewayRouteBackend.DIRECT_UPSTREAM:
            raise TransitionError("gateway_route_not_at_pre_cutover_target")
        return
    if next_transition is Transition.T6_SWITCH_CODEX_PROFILE_TO_GATEWAY:
        # D2: the explicit Codex profile switch happens before any full-path
        # smoke claim, and only once the Gateway route already targets the
        # adapter.
        if state.gateway.route_backend is not GatewayRouteBackend.ADAPTER_LOOPBACK_18031:
            raise TransitionError("gateway_route_not_pointing_at_adapter")
        if state.codex.provider_class is not CodexProviderClass.PRE_CUTOVER:
            raise TransitionError("codex_profile_not_at_pre_cutover_provider")
        return
    if next_transition is Transition.T7_FULL_PATH_SMOKE:
        if state.codex.provider_class is not CodexProviderClass.GATEWAY_ENTRY:
            raise TransitionError("codex_profile_not_switched_to_gateway")
        if state.gateway.route_backend is not GatewayRouteBackend.ADAPTER_LOOPBACK_18031:
            raise TransitionError("gateway_route_not_pointing_at_adapter")
        if state.local.service_state is not LocalServiceState.READY:
            raise TransitionError("candidate_not_ready")
        return
    if next_transition is Transition.T8_ROLLBACK_PROOF:
        return
    if next_transition is Transition.T9_FINAL_SWITCH:
        return
    raise TransitionError("unreachable_transition")  # pragma: no cover


def _mutate(
    state: CutoverState,
    transition: Transition,
    candidate_binding_class: LocalBindingClass = LocalBindingClass.LOOPBACK_18031,
) -> CutoverState:
    if transition is Transition.T2_INSTALL_LOCAL_ARTIFACT:
        return replace(
            state,
            local=replace(
                state.local,
                artifact_sha256=LocalArtifactClass.RELEASE_CANDIDATE,
                config_label=LocalConfigLabel.GATEWAY_INTEGRATED,
            ),
        )
    if transition is Transition.T3_START_CANDIDATE:
        listener = (
            LocalListener.LAN_18031_SIGNED
            if candidate_binding_class is LocalBindingClass.LAN_18031_SIGNED
            else LocalListener.LOOPBACK_18031
        )
        return replace(
            state,
            local=replace(
                state.local,
                service_state=LocalServiceState.READY,
                listener=listener,
                binding_class=candidate_binding_class,
            ),
        )
    if transition is Transition.T5_POINT_GATEWAY_TO_ADAPTER:
        return replace(
            state,
            gateway=replace(
                state.gateway, route_backend=GatewayRouteBackend.ADAPTER_LOOPBACK_18031
            ),
        )
    if transition is Transition.T6_SWITCH_CODEX_PROFILE_TO_GATEWAY:
        return replace(
            state, codex=replace(state.codex, provider_class=CodexProviderClass.GATEWAY_ENTRY)
        )
    if transition is Transition.T9_FINAL_SWITCH:
        return replace(state, cutover_performed=True)
    return state


def _inverse(
    state: CutoverState,
    transition: Transition,
    snapshot_binding_class: LocalBindingClass = LocalBindingClass.LOOPBACK_18031,
) -> CutoverState:
    if transition is Transition.T2_INSTALL_LOCAL_ARTIFACT:
        return replace(
            state,
            local=replace(
                state.local,
                artifact_sha256=LocalArtifactClass.PREVIOUS,
                config_label=LocalConfigLabel.PREVIOUS,
            ),
        )
    if transition is Transition.T3_START_CANDIDATE:
        # Rollback restores the step-1 binding class (order 011-a, G1).
        return replace(
            state,
            local=replace(
                state.local,
                service_state=LocalServiceState.STOPPED,
                listener=LocalListener.NONE,
                binding_class=snapshot_binding_class,
            ),
        )
    if transition is Transition.T5_POINT_GATEWAY_TO_ADAPTER:
        return replace(
            state, gateway=replace(state.gateway, route_backend=GatewayRouteBackend.DIRECT_UPSTREAM)
        )
    if transition is Transition.T6_SWITCH_CODEX_PROFILE_TO_GATEWAY:
        return replace(
            state, codex=replace(state.codex, provider_class=CodexProviderClass.PRE_CUTOVER)
        )
    return state


class CutoverRun:
    """One linear cutover attempt with fail-closed ordering and rollback.

    ``candidate_binding_class`` is the D1 binding class the candidate
    configuration binds at T3 (loopback by default; the LAN-visible signed
    variant requires the full signed ingress contract, checked at T3).
    """

    def __init__(
        self,
        snapshot: CutoverState,
        candidate_binding_class: LocalBindingClass = LocalBindingClass.LOOPBACK_18031,
    ) -> None:
        self.snapshot = snapshot
        self.candidate_binding_class = candidate_binding_class
        self.state = snapshot
        self.applied: list[Transition] = []

    def _expected_next(self) -> Transition:
        return TRANSITION_ORDER[len(self.applied)]

    def apply(self, transition: Transition) -> CutoverState:
        expected = self._expected_next()
        if transition is not expected:
            raise TransitionError("transition_out_of_order")
        preconditions(self.state, frozenset(self.applied))
        if transition is Transition.T3_START_CANDIDATE and (
            self.candidate_binding_class is LocalBindingClass.LAN_18031_SIGNED
        ):
            # D1: the LAN-visible bind is legal only under the full signed
            # ingress contract (the adapter configuration enforces the same
            # law fail-closed at startup).
            if not self.state.gateway.signed_contract:
                raise TransitionError("non_loopback_bind_requires_signed_ingress")
        self.state = _mutate(self.state, transition, self.candidate_binding_class)
        self.applied.append(transition)
        return self.state

    def apply_until(self, exclusive: Transition) -> CutoverState:
        """Apply transitions up to (not including) ``exclusive``."""
        while self._expected_next() is not exclusive:
            self.apply(self._expected_next())
        return self.state

    def rollback(self, failed_at: Transition) -> CutoverState:
        """Restore the complete step-1 snapshot after a failure at a
        pre-final transition (the failed transition itself is not applied)."""
        if failed_at is Transition.T9_FINAL_SWITCH:
            raise TransitionError("no_rollback_after_final_switch")
        for transition in reversed(self.applied):
            if transition not in PRE_FINAL_MUTATORS:
                continue
            self.state = _inverse(self.state, transition, self.snapshot.local.binding_class)
        # G1 mechanical proof: rollback restores the step-1 snapshot field by
        # field, including the step-1 local binding class.
        if self.state != self.snapshot:
            raise TransitionError("rollback_state_mismatch")
        return self.state


def canonical_snapshot(authority_sha: str) -> CutoverState:
    """The canonical pre-cutover snapshot used by the runbook and tests."""
    return CutoverState(
        local=LocalState(
            artifact_sha256=LocalArtifactClass.PREVIOUS,
            config_label=LocalConfigLabel.PREVIOUS,
            binding_class=LocalBindingClass.LOOPBACK_18031,
            service_state=LocalServiceState.STOPPED,
            listener=LocalListener.NONE,
        ),
        gateway=GatewayState(
            route_backend=GatewayRouteBackend.DIRECT_UPSTREAM,
            authority_sha=authority_sha,
            signed_contract=True,
        ),
        codex=CodexState(provider_class=CodexProviderClass.PRE_CUTOVER),
        cutover_performed=False,
    )


def self_test() -> dict[str, object]:
    """Deterministic assertions mirroring the pytest suite."""
    authority_sha = "1fccaa746df6cd44f1ddf8c2ec5cf6ea9f18b1cb"
    snapshot = canonical_snapshot(authority_sha)

    # Happy path: the full ordered run reaches the final switch.
    run = CutoverRun(snapshot)
    for transition in TRANSITION_ORDER:
        run.apply(transition)
    assert run.state.cutover_performed is True

    # D2: the full-path smoke requires the explicit Codex profile switch
    # (T6) to have happened before it is claimed.
    # (a) strict ordering: T7 while T6 is pending is out of order.
    ordered = CutoverRun(snapshot)
    ordered.apply_until(Transition.T6_SWITCH_CODEX_PROFILE_TO_GATEWAY)
    try:
        ordered.apply(Transition.T7_FULL_PATH_SMOKE)
    except TransitionError as exc:
        assert exc.code == "transition_out_of_order"
    else:
        raise AssertionError("smoke before profile switch was accepted")
    # (b) state precondition: even with T6 recorded applied, a state where
    # the profile was not switched rejects the smoke.
    unswitched = _mutate(snapshot, Transition.T5_POINT_GATEWAY_TO_ADAPTER)
    try:
        preconditions(
            unswitched,
            frozenset(TRANSITION_ORDER[:6]),
        )
    except TransitionError as exc:
        assert exc.code == "codex_profile_not_switched_to_gateway"
    else:
        raise AssertionError("smoke without profile switch was accepted")

    # Rollback from every pre-final failure point restores the full snapshot.
    for failed_at in TRANSITION_ORDER[:-1]:
        runner = CutoverRun(snapshot)
        runner.apply_until(failed_at)
        restored = runner.rollback(failed_at)
        assert restored == snapshot, (failed_at, restored)
        assert restored.local.listener is LocalListener.NONE

    # 011-a G1: the LAN-visible signed candidate class is tracked by every
    # mutating transition and the complete rollback table, and is rejected
    # without the full signed ingress contract.
    lan_run = CutoverRun(snapshot, LocalBindingClass.LAN_18031_SIGNED)
    for transition in TRANSITION_ORDER:
        lan_run.apply(transition)
    assert lan_run.state.cutover_performed is True
    assert lan_run.state.local.binding_class is LocalBindingClass.LAN_18031_SIGNED
    for failed_at in TRANSITION_ORDER[:-1]:
        runner = CutoverRun(snapshot, LocalBindingClass.LAN_18031_SIGNED)
        runner.apply_until(failed_at)
        restored = runner.rollback(failed_at)
        assert restored == snapshot, (failed_at, restored)
        assert restored.local.binding_class is LocalBindingClass.LOOPBACK_18031, failed_at
    unsigned = replace(
        snapshot,
        gateway=replace(snapshot.gateway, signed_contract=False),
    )
    lan_unsigned = CutoverRun(unsigned, LocalBindingClass.LAN_18031_SIGNED)
    lan_unsigned.apply(Transition.T1_CAPTURE_BASELINE)
    lan_unsigned.apply(Transition.T2_INSTALL_LOCAL_ARTIFACT)
    try:
        lan_unsigned.apply(Transition.T3_START_CANDIDATE)
    except TransitionError as exc:
        assert exc.code == "non_loopback_bind_requires_signed_ingress"
    else:
        raise AssertionError("LAN bind without the signed contract was accepted")
    # The rejected transition mutated nothing.
    assert lan_unsigned.state.local.listener is LocalListener.NONE
    assert lan_unsigned.state.local.binding_class is LocalBindingClass.LOOPBACK_18031

    # Post-final rollback is rejected.
    final = CutoverRun(snapshot)
    for transition in TRANSITION_ORDER:
        final.apply(transition)
    try:
        final.rollback(Transition.T9_FINAL_SWITCH)
    except TransitionError as exc:
        assert exc.code == "no_rollback_after_final_switch"
    else:
        raise AssertionError("post-final rollback was accepted")

    return {
        "ok": True,
        "transitions": len(TRANSITION_ORDER),
        "pre_final_mutators": len(PRE_FINAL_MUTATORS),
        "rollback_points_checked": len(TRANSITION_ORDER) - 1,
        "lan_rollback_points_checked": len(TRANSITION_ORDER) - 1,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.print_help()
        return 2
    print(json.dumps(self_test(), sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
