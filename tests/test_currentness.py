"""018-e: original-API nonroot currentness overlay -- durable
known-synthetic controls over the ONE bounded pure derivation.

``derive_currentness_overlay`` is the single original-API surface
under this order: it takes the ACTUAL 018-d retained state, its
ACTUAL namespace and explicit currentness bounds, and derives the
pure nonroot path-frontier summary WITHOUT mutating the state,
WITHOUT advancing a revision, and WITHOUT any clock (frozen parent
evidence only; arrival, list order, IDs and digests never establish
freshness).  All fixtures are inline known-synthetic original
GraphRequests on BOTH read endpoints and BOTH admission modes; no
S runtime path dependency; no model, native, client or service
facility is started.

Locked law surface covered here: the version-chain law (a provably
NEWER anchored claim stales the older historical candidate with
PROVEN_CHANGE, a genuine revert makes the equal old content usable
again through the NEW witness, and an unissued new-bytes read keeps
the path in CONTENT_CONFLICT until a trusted receipt anchors it);
the equal incomparable witnesses law (equal bytes never manufacture
an edge and both witnesses stay on the maximal frontier); the
boundaryless group law (an opaque multi-member group stales only
with UNPROVEN_OWNERSHIP against a newer descendant, its untouched
members stay current-opaque, and the emitted row unit is reserved
BEFORE the row is constructed); and the privacy law (a forged
namespace is refused by the fresh validators without the serializer
echoing its private fields into a warning).  The remaining group
battery, the bound matrices, the immutability/privacy/no-host-IO
suites and the unrelated-path stability controls extend this module
under the same order.
"""

from __future__ import annotations

import builtins
import hashlib
import json
import os
import socket
import subprocess
import warnings
from pathlib import Path
from typing import Any, NoReturn

import pytest

from slaif_local_coding.constitution.bundles import currentness as currentness_module
from slaif_local_coding.constitution.bundles.bundle_admission import (
    observe_bundle_admission_batch,
)
from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
    AdmissionOutcome,
    BoundaryClass,
    make_bundle_admission_namespace,
)
from slaif_local_coding.constitution.bundles.bundle_proof_models import (
    BundleProofKind,
)
from slaif_local_coding.constitution.bundles.causal_history import (
    observe_causal_history,
    register_issuance,
    register_receipt,
    relation,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
    CausalHistoryNamespace,
    CausalHistoryOutcome,
    CausalHistoryState,
    CausalRelation,
)
from slaif_local_coding.constitution.bundles.currentness import derive_currentness_overlay
from slaif_local_coding.constitution.bundles.currentness_models import (
    CURRENTNESS_POLICY_VERSION,
    CurrentnessBounds,
    CurrentnessGroupRecord,
    CurrentnessLimitation,
    CurrentnessOutcome,
    CurrentnessOverlay,
    CurrentnessPathRecord,
    CurrentnessReason,
    CurrentnessResult,
    CurrentnessStatus,
    GroupPathRow,
    opaque_group_identity,
)
from slaif_local_coding.constitution.bundles.graph_observation import GraphRequest
from slaif_local_coding.constitution.bundles.observation_models import Limitation
from tests.test_causal_history import (
    ENDPOINTS,
    FINGERPRINT,
    IDENTITY,
    MODES,
    V1_BODY,
    V2_BODY,
    WORKSPACE,
    empty_state,
    make_ns,
    read_request,
    root_request,
    running_frame,
)

READ_CMD = "cat A.md"
READ_ARGS = json.dumps({"cmd": READ_CMD})


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class History:
    """A tiny original-API driver: tracks the EXACT (state,
    revision) pair and the accepted 018-d transitions over ONE
    namespace.  Refusals and replays are asserted at the call site
    through the raw transition, never through this helper."""

    def __init__(self, mode: AdmissionMode, endpoint: str) -> None:
        self.mode = mode
        self.endpoint = endpoint
        self.ns = make_ns(mode)
        self.state = empty_state(self.ns)
        self.revision = 0

    def boot_root(self) -> None:
        self.observe(root_request(), note="root")

    def observe(self, request: GraphRequest, *, note: str = "") -> CausalHistoryOutcome:
        transition = observe_causal_history((request,), self.ns, self.state, self.revision)
        assert transition.outcome is CausalHistoryOutcome.ACCEPTED, (
            note,
            transition.outcome,
            transition.diagnostics,
        )
        self.state, self.revision = transition.state, transition.revision_after
        return transition.outcome

    def read(self, cid: str, body: str, cmd: str = READ_CMD) -> str:
        self.observe(read_request(self.endpoint, cid, body, cmd), note=f"read:{cid}")
        return self.state.occurrences[-1].occurrence_id

    def issue(
        self,
        cid: str,
        frontier: tuple[str, ...],
        args: str = READ_ARGS,
        name: str = "exec_command",
    ) -> None:
        transition = register_issuance(
            self.state, self.ns, cid, self.endpoint, name, args, frontier, self.revision
        )
        assert transition.outcome is CausalHistoryOutcome.ACCEPTED, (
            cid,
            transition.outcome,
            transition.diagnostics,
        )
        self.state, self.revision = transition.state, transition.revision_after

    def receipt(
        self,
        cid: str,
        frontier: tuple[str, ...],
        args: str = READ_ARGS,
        name: str = "exec_command",
    ) -> None:
        transition = register_receipt(
            self.state, self.ns, cid, self.endpoint, name, args, frontier, self.revision
        )
        assert transition.outcome in (
            CausalHistoryOutcome.ACCEPTED,
            CausalHistoryOutcome.REPLAYED,
        ), (cid, transition.outcome, transition.diagnostics)
        self.state, self.revision = transition.state, transition.revision_after

    def overlay(self, bounds: CurrentnessBounds | None = None) -> CurrentnessOverlay:
        result = derive_currentness_overlay(self.state, self.ns, bounds)
        assert result.outcome is CurrentnessOutcome.OK, (result.outcome, result.diagnostics)
        assert result.state is self.state
        assert result.overlay is not None
        return result.overlay


def path_record(overlay: CurrentnessOverlay, path: str) -> CurrentnessPathRecord:
    for record in overlay.paths:
        if record.path == path:
            return record
    raise AssertionError(f"path {path} is not represented")


def group_record(
    overlay: CurrentnessOverlay, occurrence_id: str, group_index: int = 0
) -> CurrentnessGroupRecord:
    for record in overlay.groups:
        if record.occurrence_id == occurrence_id and record.group_index == group_index:
            return record
    raise AssertionError(f"group {occurrence_id}#{group_index} is not represented")


def row(group: CurrentnessGroupRecord, path: str) -> GroupPathRow:
    for record in group.path_rows:
        if record.path == path:
            return record
    raise AssertionError(f"row {path} is not represented in group {group.occurrence_id}")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_version_chain_revert_and_exact_replay(mode: AdmissionMode, endpoint: str) -> None:
    """v1 -> anchored v2 (PROVEN_CHANGE staleness of the historical
    candidate) -> an unissued REVERT read of the equal old v1
    content (CONTENT_CONFLICT, both maximal witnesses retained) -> a
    trusted receipt anchoring the revert under v2 (resolved at the
    new occurrence; the equal old v1 candidate becomes usable again
    through the new witness) -> exact old request replay (REPLAYED,
    identical overlay).  Chronology comes ONLY from the frozen parent
    evidence: v2 is provably newer only after the trusted frontier
    exists."""
    h = History(mode, endpoint)
    h.boot_root()
    v1 = h.read("v1-occ", V1_BODY)
    # Unissued siblings are never ordered.
    assert relation(h.state, h.ns, v1, v1) is CausalRelation.SAME
    h.issue("v2-occ", (v1, CAUSAL_ROOT_FACT))
    v2 = h.read("v2-occ", V2_BODY)
    assert relation(h.state, h.ns, v1, v2) is CausalRelation.BEFORE
    assert relation(h.state, h.ns, v2, v1) is CausalRelation.AFTER

    overlay = h.overlay()
    assert overlay.history_key == h.ns.history_key
    assert overlay.revision == h.state.revision
    assert overlay.workspace == WORKSPACE
    assert overlay.policy_version == CURRENTNESS_POLICY_VERSION
    assert overlay.bounds == CurrentnessBounds()
    path = path_record(overlay, "A.md")
    assert path.status is CurrentnessStatus.CURRENT_KNOWN
    assert path.known_digest == _sha(V2_BODY)
    assert path.opaque_identity is None
    assert path.reasons == ()
    assert path.witnesses == (v2,)
    assert path.overlapping_occurrences == tuple(sorted((v1, v2)))
    old = group_record(overlay, v1)
    assert old.boundary_class is BoundaryClass.PROVEN
    assert old.group_status is CurrentnessStatus.STALE
    old_row = row(old, "A.md")
    assert old_row.status is CurrentnessStatus.STALE
    assert old_row.reasons == (CurrentnessReason.PROVEN_CHANGE,)
    assert old_row.witnesses == (v2,)
    new = group_record(overlay, v2)
    assert new.group_status is CurrentnessStatus.CURRENT_KNOWN
    assert row(new, "A.md").status is CurrentnessStatus.CURRENT_KNOWN
    assert overlay.usable_occurrences == (v2,)
    assert overlay.emitted_reasons == 1

    # A genuine revert read of the EQUAL old v1 content, still
    # unissued, keeps the path conflicted: the new claim is
    # INCOMPARABLE, so no staleness and no newest selection is ever
    # inferred (the v2 digest and the reverted v1 digest are both
    # individually known and differ).
    v3 = h.read("v3-occ", V1_BODY)
    assert relation(h.state, h.ns, v2, v3) is CausalRelation.INCOMPARABLE
    conflicted = h.overlay()
    c_path = path_record(conflicted, "A.md")
    assert c_path.status is CurrentnessStatus.CONTENT_CONFLICT
    assert c_path.known_digest is None
    assert c_path.opaque_identity is None
    assert c_path.reasons == (CurrentnessReason.KNOWN_CONTENT_CONFLICT,)
    assert c_path.witnesses == tuple(sorted((v2, v3)))
    assert c_path.overlapping_occurrences == tuple(sorted((v1, v2, v3)))
    assert conflicted.usable_occurrences == ()
    for occurrence_id in (v1, v2, v3):
        blocked = group_record(conflicted, occurrence_id)
        assert blocked.group_status in (
            CurrentnessStatus.STALE,
            CurrentnessStatus.CONTENT_CONFLICT,
            CurrentnessStatus.OWNERSHIP_AMBIGUITY,
        )

    # A trusted receipt anchors the newer read under v2: the path
    # resolves at the NEW digest, the v2 group stales with
    # PROVEN_CHANGE, and the EQUAL old v1 group is current again
    # through the new witness (equality never manufactures an edge,
    # it only removes the staleness blocker).
    h.receipt("v3-occ", (v2, CAUSAL_ROOT_FACT))
    assert relation(h.state, h.ns, v2, v3) is CausalRelation.BEFORE
    resolved = h.overlay()
    r_path = path_record(resolved, "A.md")
    assert r_path.status is CurrentnessStatus.CURRENT_KNOWN
    assert r_path.known_digest == _sha(V1_BODY)
    assert r_path.witnesses == (v3,)
    assert row(group_record(resolved, v3), "A.md").status is CurrentnessStatus.CURRENT_KNOWN
    assert row(group_record(resolved, v1), "A.md").status is CurrentnessStatus.CURRENT_KNOWN
    v2_row = row(group_record(resolved, v2), "A.md")
    assert v2_row.status is CurrentnessStatus.STALE
    assert v2_row.reasons == (CurrentnessReason.PROVEN_CHANGE,)
    assert v2_row.witnesses == (v3,)
    assert resolved.usable_occurrences == tuple(sorted((v1, v3)))

    # The EXACT original v1 request replays as a pure no-op and the
    # derived overlay is byte-for-byte identical.
    before = resolved.model_dump()
    transition = observe_causal_history(
        (read_request(endpoint, "v1-occ", V1_BODY),), h.ns, h.state, h.revision
    )
    assert transition.outcome is CausalHistoryOutcome.REPLAYED
    assert transition.state is h.state
    assert h.overlay().model_dump() == before


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_equal_incomparable_witnesses_stay_on_the_frontier(
    mode: AdmissionMode, endpoint: str
) -> None:
    """Two unissued reads of EQUAL bytes never manufacture an edge:
    the path is CURRENT_KNOWN at that digest with BOTH witnesses on
    the maximal frontier, and both occurrences stay usable."""
    h = History(mode, endpoint)
    h.boot_root()
    first = h.read("eq-a-occ", V1_BODY)
    second = h.read("eq-b-occ", V1_BODY)
    assert relation(h.state, h.ns, first, second) is CausalRelation.INCOMPARABLE
    overlay = h.overlay()
    path = path_record(overlay, "A.md")
    assert path.status is CurrentnessStatus.CURRENT_KNOWN
    assert path.known_digest == _sha(V1_BODY)
    assert path.opaque_identity is None
    assert path.reasons == ()
    assert path.witnesses == tuple(sorted((first, second)))
    assert path.overlapping_occurrences == tuple(sorted((first, second)))
    for occurrence_id in (first, second):
        group = group_record(overlay, occurrence_id)
        assert group.boundary_class is BoundaryClass.PROVEN
        assert group.group_status is CurrentnessStatus.CURRENT_KNOWN
        assert row(group, "A.md").status is CurrentnessStatus.CURRENT_KNOWN
    assert overlay.usable_occurrences == tuple(sorted((first, second)))
    assert overlay.emitted_reasons == 0


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_boundaryless_group_stales_only_unproven_against_newer(
    mode: AdmissionMode, endpoint: str
) -> None:
    """A boundaryless ``cat A.md B.md`` group has unknown per-member
    attribution: against a provably NEWER anchored single-member
    read its A.md row stales with EXACTLY UNPROVEN_OWNERSHIP (never
    proven-change), its untouched B.md row stays CURRENT_OPAQUE, the
    group as a whole is STALE, and only the newer occurrence is
    usable.  The opaque identity is the versioned group-LOCAL shape
    recipe (boundary, ordered members, group digest, member
    digests) recomputable without the original coordinates."""
    h = History(mode, endpoint)
    h.boot_root()
    ab = h.read("ab-occ", "A-body\nB-body\n", cmd="cat A.md B.md")
    h.issue("a2-occ", (ab, CAUSAL_ROOT_FACT))
    a2 = h.read("a2-occ", V1_BODY)
    overlay = h.overlay()
    a_path = path_record(overlay, "A.md")
    assert a_path.status is CurrentnessStatus.CURRENT_KNOWN
    assert a_path.known_digest == _sha(V1_BODY)
    assert a_path.witnesses == (a2,)
    b_path = path_record(overlay, "B.md")
    assert b_path.status is CurrentnessStatus.CURRENT_OPAQUE
    assert b_path.known_digest is None
    assert b_path.opaque_identity is not None
    assert b_path.witnesses == (ab,)
    group = group_record(overlay, ab)
    assert group.boundary_class is BoundaryClass.BOUNDARYLESS
    assert group.members == ("A.md", "B.md")
    assert group.member_digests == (None, None)
    assert group.group_status is CurrentnessStatus.STALE
    a_row = row(group, "A.md")
    assert a_row.status is CurrentnessStatus.STALE
    assert a_row.reasons == (CurrentnessReason.UNPROVEN_OWNERSHIP,)
    assert a_row.witnesses == (a2,)
    b_row = row(group, "B.md")
    assert b_row.status is CurrentnessStatus.CURRENT_OPAQUE
    assert b_row.reasons == ()
    assert b_row.witnesses == ()
    assert group_record(overlay, a2).group_status is CurrentnessStatus.CURRENT_KNOWN
    assert overlay.usable_occurrences == (a2,)
    # The identity recomputes from the ACTUAL recipe inputs, with the
    # group (segment) digest read from the retained verbatim proof.
    ab_occurrence = next(
        occurrence for occurrence in h.state.occurrences if occurrence.occurrence_id == ab
    )
    segment = ab_occurrence.proof.segments[0]
    assert group.opaque_identity == opaque_group_identity(
        BoundaryClass.BOUNDARYLESS,
        ("A.md", "B.md"),
        segment.digest,
        (None, None),
        policy_version=CURRENTNESS_POLICY_VERSION,
        proof_version=h.ns.proof_version,
        observation_version=h.ns.observation_version,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_witness_membership_refuses_before_group_row_construction(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The emitted-row unit is reserved BEFORE the row is constructed.
    With the shared witness-membership ledger already exhausted by the
    claim, reverse-index and frontier charges (one proven read: three
    charged associations), the fourth unit must refuse with a fixed
    typed REFUSED_OVER_BOUND and the EXACT prior state before any
    GroupPathRow construction attempt -- a sentinel on the row
    constructor proves no construction is even attempted."""
    h = History(mode, endpoint)
    h.boot_root()
    h.read("solo-occ", V1_BODY)
    # The at-limit total derives cleanly (no quota widening: exactly
    # four charged associations for one proven read -- claim,
    # reverse-index, frontier witness, emitted row).
    assert h.overlay(CurrentnessBounds(max_witness_memberships=4)) is not None
    attempts: list[int] = []

    class UnexpectedRowConstruction(Exception):
        """Sentinel: the row constructor must never be reached."""

    def forbidden(*args: object, **kwargs: object) -> NoReturn:
        attempts.append(1)
        raise UnexpectedRowConstruction

    monkeypatch.setattr(currentness_module, "GroupPathRow", forbidden)
    result = derive_currentness_overlay(h.state, h.ns, CurrentnessBounds(max_witness_memberships=3))
    assert not attempts
    assert result.outcome is CurrentnessOutcome.REFUSED_OVER_BOUND
    assert result.diagnostics == (CurrentnessLimitation.WITNESS_MEMBERSHIPS_OVER_BOUND,)
    assert result.state is h.state
    assert result.overlay is None


IDENTITY_FIELDS = (
    "principal",
    "model_identity",
    "config_fingerprint",
    "lineage_id",
    "workspace",
)
CANARY = "synthetic-currentness-canary-4f1e"


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_forged_identity_fields_never_reach_a_warning(mode: AdmissionMode, endpoint: str) -> None:
    """A forged (unvalidated) namespace instance carrying a synthetic
    canary in ANY identity field is refused by the fresh actual-field
    validators BEFORE positive interpretation, and the validation path
    never serializes the unvalidated instance in a way that echoes its
    private fields into a warning: zero warnings, the canary appears
    nowhere in the result, and the EXACT prior state is preserved
    with no overlay."""
    h = History(mode, endpoint)
    h.boot_root()
    for field in IDENTITY_FIELDS:
        forged: CausalHistoryNamespace = h.ns.model_copy(update={field: [CANARY]})
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = derive_currentness_overlay(h.state, forged)
        assert result.outcome is CurrentnessOutcome.REFUSED_VERSION_CONFLICT, field
        assert result.diagnostics == (CurrentnessLimitation.VERSION_UNSUPPORTED,), field
        assert result.state is h.state
        assert result.overlay is None
        text = repr(result) + str(result)
        assert CANARY not in text, field
        for warning in caught:
            assert CANARY not in str(warning.message), (field, warning.message)


def _repeated_operand_request(n: int, endpoint: str) -> GraphRequest:
    """One original read request on the SELECTED endpoint carrying
    the earned-default ``n`` repeated A.md operands of ONE
    boundaryless group (the accepted 017 plan ceiling; the body is
    the exact concatenation of the n file contents)."""
    cmd = "cat " + " ".join(["A.md"] * n)
    body = "Version one body.\n" * n
    return read_request(endpoint, "dup-operand-occ", body, cmd)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_repeated_operand_identity_comparisons_are_charged(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Repeated operands keep one claim per member position: N
    claims on one path cost N*(N-1) charged identity-comparison
    work in the maximal-frontier dominance scan (duplicates count;
    no free quadratic string scan).  At the earned-default 32
    operands the measured total is exactly the 205 charged
    non-comparison units PLUS 32*31 = 992 charged comparisons =
    1197, so the pre-fix total of 205 -- which the old code still
    returned OK for -- now refuses with a fixed typed
    WORK_UNITS_OVER_BOUND and the EXACT prior state, while the
    at-limit budget still derives cleanly and EVERY group/member
    claim (32 member positions, boundaryless, unknown per-member
    digests) is retained unchanged."""
    h = History(mode, endpoint)
    h.boot_root()
    n = h.ns.observation_bounds.max_operands
    assert n == 32  # the earned-default operand ceiling
    request = _repeated_operand_request(n, endpoint)
    assert request.endpoint == endpoint  # the SELECTED endpoint is exercised
    h.observe(request, note="repeated-operand read")
    occurrence = h.state.occurrences[-1]
    assert occurrence.endpoint == endpoint
    assert occurrence.proof.endpoint == endpoint
    (segment,) = occurrence.proof.segments
    assert len(occurrence.proof.requested_members) == n
    assert segment.member_positions == tuple(range(n))
    assert segment.member_digest is None

    original_unit = currentness_module._CurrentnessLedger.unit
    charged = {"n": 0}

    def counting_unit(self: currentness_module._CurrentnessLedger) -> bool:
        charged["n"] += 1
        return original_unit(self)

    monkeypatch.setattr(currentness_module._CurrentnessLedger, "unit", counting_unit)
    result = derive_currentness_overlay(h.state, h.ns)
    assert result.outcome is CurrentnessOutcome.OK
    assert result.state is h.state
    overlay = result.overlay
    assert overlay is not None
    total = charged["n"]
    assert total == 205 + n * (n - 1) == 1197
    # All original group/member/hash claims survive: one
    # boundaryless group with all n member positions retained.
    group = group_record(overlay, occurrence.occurrence_id)
    assert group.boundary_class is BoundaryClass.BOUNDARYLESS
    assert group.members == ("A.md",) * n
    assert group.member_digests == (None,) * n
    assert group.opaque_identity == opaque_group_identity(
        BoundaryClass.BOUNDARYLESS,
        ("A.md",) * n,
        segment.digest,
        (None,) * n,
        policy_version=CURRENTNESS_POLICY_VERSION,
        proof_version=h.ns.proof_version,
        observation_version=h.ns.observation_version,
    )
    path = path_record(overlay, "A.md")
    assert path.status is CurrentnessStatus.CURRENT_OPAQUE
    assert path.opaque_identity is not None
    assert path.witnesses == (occurrence.occurrence_id,)
    assert overlay.usable_occurrences == (occurrence.occurrence_id,)

    # The pre-fix charged total (205) is no longer sufficient: the
    # N*(N-1) comparisons are charged work, not a free scan.
    pre_fix = derive_currentness_overlay(h.state, h.ns, CurrentnessBounds(max_work_units=205))
    assert pre_fix.outcome is CurrentnessOutcome.REFUSED_OVER_BOUND
    assert pre_fix.diagnostics == (CurrentnessLimitation.WORK_UNITS_OVER_BOUND,)
    assert pre_fix.state is h.state
    assert pre_fix.overlay is None
    # First-over and at-limit on the ACTUAL measured total.
    first_over = derive_currentness_overlay(
        h.state, h.ns, CurrentnessBounds(max_work_units=total - 1)
    )
    assert first_over.outcome is CurrentnessOutcome.REFUSED_OVER_BOUND
    assert first_over.diagnostics == (CurrentnessLimitation.WORK_UNITS_OVER_BOUND,)
    assert first_over.state is h.state
    assert first_over.overlay is None
    at_limit = derive_currentness_overlay(h.state, h.ns, CurrentnessBounds(max_work_units=total))
    assert at_limit.outcome is CurrentnessOutcome.OK
    assert at_limit.state is h.state
    assert at_limit.overlay is not None
    # The derived CONTENT is identical; only the caller's bound set
    # (and the scope key that binds it) differs.
    at_limit_content = {
        "paths": at_limit.overlay.paths,
        "groups": at_limit.overlay.groups,
        "usable_occurrences": at_limit.overlay.usable_occurrences,
        "emitted_reasons": at_limit.overlay.emitted_reasons,
        "revision": at_limit.overlay.revision,
        "history_key": at_limit.overlay.history_key,
    }
    default_content = {
        "paths": overlay.paths,
        "groups": overlay.groups,
        "usable_occurrences": overlay.usable_occurrences,
        "emitted_reasons": overlay.emitted_reasons,
        "revision": overlay.revision,
        "history_key": overlay.history_key,
    }
    assert at_limit_content == default_content


def framed_read_request(
    endpoint: str, cid: str, frame_text: str, cmd: str = READ_CMD
) -> GraphRequest:
    """One original rootless read request on EITHER endpoint with an
    explicit result frame (the zero-exit ``frame`` carrier of
    ``tests.test_causal_history`` for completed reads)."""
    if endpoint == "responses":
        payload: dict[str, object] = {
            "input": [
                {
                    "type": "function_call",
                    "call_id": cid,
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": cmd}),
                },
                {"type": "function_call_output", "call_id": cid, "output": frame_text},
            ]
        }
    else:
        payload = {
            "messages": [
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": cid,
                            "type": "function",
                            "function": {
                                "name": "exec_command",
                                "arguments": json.dumps({"cmd": cmd}),
                            },
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": cid, "content": frame_text},
            ]
        }
    return GraphRequest(payload=payload, endpoint=endpoint, context=None)


FAILED_FRAME = (
    "Chunk ID: synthetic\n"
    "Wall time: 0.0000 seconds\n"
    "Process exited with code 1\n"
    "Output:\nfailed-new\n"
)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_complete_empty_read_is_current_and_old_replay_does_not_revert(
    mode: AdmissionMode, endpoint: str
) -> None:
    """A completed read of an EMPTY file is CURRENT (not missing):
    the path resolves at the exact empty-source digest with the new
    occurrence as the only witness, the older group stales, and an
    exact replay of the older request is a pure no-op that does NOT
    revert the frontier (no clock, no newest-selection)."""
    h = History(mode, endpoint)
    h.boot_root()
    before = h.read("empty-before-occ", "old\n")
    before_occurrence = next(
        occurrence for occurrence in h.state.occurrences if occurrence.occurrence_id == before
    )
    assert before_occurrence.proof.source_text == "old\n"
    assert before_occurrence.proof.source_digest == _sha("old\n")
    h.issue("empty-after-occ", (before,))
    after = h.read("empty-after-occ", "")
    after_occurrence = next(
        occurrence for occurrence in h.state.occurrences if occurrence.occurrence_id == after
    )
    assert after_occurrence.proof.source_byte_length == 0
    assert after_occurrence.proof.segments[0].member_digest == _sha("")
    assert relation(h.state, h.ns, before, after) is CausalRelation.BEFORE
    overlay = h.overlay()
    path = path_record(overlay, "A.md")
    assert path.status is CurrentnessStatus.CURRENT_KNOWN
    assert path.known_digest == _sha("")
    assert path.opaque_identity is None
    assert path.witnesses == (after,)
    assert group_record(overlay, before).group_status is CurrentnessStatus.STALE
    old_request = read_request(endpoint, "empty-before-occ", "old\n")
    transition = observe_causal_history((old_request,), h.ns, h.state, h.revision)
    assert transition.outcome is CausalHistoryOutcome.REPLAYED
    assert transition.state is h.state
    assert h.overlay().model_dump() == overlay.model_dump()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_nonzero_result_never_creates_a_completed_claim(mode: AdmissionMode, endpoint: str) -> None:
    """A failed (nonzero-exit) original result retains NO completed
    occurrence: the read never creates a path claim, the EXACT prior
    state is preserved, and the current source stays current with its
    original witness."""
    h = History(mode, endpoint)
    h.boot_root()
    before = h.read("nonzero-before-occ", "old\n")
    h.issue("nonzero-after-occ", (before,))
    failed_request = framed_read_request(endpoint, "nonzero-after-occ", FAILED_FRAME)
    transition = observe_causal_history((failed_request,), h.ns, h.state, h.revision)
    assert transition.state is h.state
    assert all(occurrence.call_id != "nonzero-after-occ" for occurrence in h.state.occurrences)
    overlay = h.overlay()
    path = path_record(overlay, "A.md")
    assert path.status is CurrentnessStatus.CURRENT_KNOWN
    assert path.known_digest == _sha("old\n")
    assert path.witnesses == (before,)
    assert overlay.usable_occurrences == (before,)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_standalone_vs_isolated_opaque_group_are_equal(mode: AdmissionMode, endpoint: str) -> None:
    """Opaque group equality binds the GROUP-LOCAL semantic ownership
    shape: a standalone boundaryless ``cat A.md B.md`` (whole proof,
    group index 0, positions (0,1)) and the SAME group isolated after
    a separate proven C in a partitioned proof (group index 1,
    positions (1,2)) have the exact same group bytes, ordered members
    and unknown per-member attribution -- so the derived opaque
    identities are EQUAL despite different proof kinds, full-proof
    digests and global coordinates (no per-file hash or temporal
    edge is inferred).  Both occurrences stay witnesses of the
    CURRENT_OPAQUE path, and the retained original proof
    coordinates are unchanged."""
    h = History(mode, endpoint)
    h.boot_root()
    standalone = h.read("ab-standalone-occ", "A-body\nB-body\n", cmd="cat A.md B.md")
    isolated = h.read(
        "ab-isolated-occ",
        "C-body\nMARK\nA-body\nB-body\n",
        cmd="cat C.md && echo 'MARK' && cat A.md B.md",
    )
    standalone_proof = next(
        occurrence.proof
        for occurrence in h.state.occurrences
        if occurrence.occurrence_id == standalone
    )
    isolated_proof = next(
        occurrence.proof
        for occurrence in h.state.occurrences
        if occurrence.occurrence_id == isolated
    )
    standalone_ab = standalone_proof.segments[0]
    isolated_ab = isolated_proof.segments[1]
    # Original provenance preconditions (coordinates retained).
    assert standalone_proof.kind != isolated_proof.kind
    assert standalone_proof.source_digest != isolated_proof.source_digest
    assert standalone_ab.member_positions == (0, 1)
    assert isolated_ab.member_positions == (1, 2)
    assert standalone_ab.index == 0 and isolated_ab.index == 1
    assert standalone_ab.digest == isolated_ab.digest  # exact group bytes
    assert standalone_ab.member_digest is None
    assert isolated_ab.member_digest is None
    assert relation(h.state, h.ns, standalone, isolated) is CausalRelation.INCOMPARABLE
    overlay = h.overlay()
    standalone_group = group_record(overlay, standalone, 0)
    isolated_group = group_record(overlay, isolated, 1)
    assert standalone_group.boundary_class is BoundaryClass.BOUNDARYLESS
    assert isolated_group.boundary_class is BoundaryClass.BOUNDARYLESS
    assert standalone_group.opaque_identity == isolated_group.opaque_identity
    assert standalone_group.members == isolated_group.members == ("A.md", "B.md")
    assert standalone_group.member_digests == isolated_group.member_digests == (None, None)
    for path in ("A.md", "B.md"):
        record = path_record(overlay, path)
        assert record.status is CurrentnessStatus.CURRENT_OPAQUE, path
        assert record.known_digest is None
        assert record.opaque_identity == standalone_group.opaque_identity
        assert record.reasons == ()
        assert record.witnesses == tuple(sorted((standalone, isolated)))
        assert record.overlapping_occurrences == tuple(sorted((standalone, isolated)))
        assert row(standalone_group, path).status is CurrentnessStatus.CURRENT_OPAQUE
        assert row(isolated_group, path).status is CurrentnessStatus.CURRENT_OPAQUE
    # The separate proven C stays individually known and current.
    c_path = path_record(overlay, "C.md")
    assert c_path.status is CurrentnessStatus.CURRENT_KNOWN
    assert c_path.known_digest == _sha("C-body\n")
    assert c_path.witnesses == (isolated,)
    assert overlay.usable_occurrences == tuple(sorted((standalone, isolated)))


V3_BODY = "Version three body.\n"


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_initial_multiversion_forks_keep_every_witness(mode: AdmissionMode, endpoint: str) -> None:
    """Initial forks: two unissued sibling reads of different bytes
    keep the path in CONTENT_CONFLICT with BOTH witnesses; a
    descendant of BOTH resolves the path at its own digest and stales
    both siblings (PROVEN_CHANGE); a descendant of ONLY ONE leaves
    the other sibling as a retained conflicting witness (witnesses
    are never erased); and trusted receipts registered in REVERSED
    arrival order still yield chronology from the frozen edges only
    (the anchored child is provably newer, the path resolves at the
    newer digest)."""
    h = History(mode, endpoint)
    h.boot_root()
    s1 = h.read("sibling-one-occ", V1_BODY)
    s2 = h.read("sibling-two-occ", V2_BODY)
    assert relation(h.state, h.ns, s1, s2) is CausalRelation.INCOMPARABLE
    conflicted = h.overlay()
    c_path = path_record(conflicted, "A.md")
    assert c_path.status is CurrentnessStatus.CONTENT_CONFLICT
    assert c_path.reasons == (CurrentnessReason.KNOWN_CONTENT_CONFLICT,)
    assert c_path.known_digest is None
    assert c_path.witnesses == tuple(sorted((s1, s2)))
    assert conflicted.usable_occurrences == ()

    # A descendant of BOTH: both siblings stale, path at V3.
    h.issue("both-child-occ", (s1, s2, CAUSAL_ROOT_FACT))
    both_child = h.read("both-child-occ", V3_BODY)
    resolved = h.overlay()
    r_path = path_record(resolved, "A.md")
    assert r_path.status is CurrentnessStatus.CURRENT_KNOWN
    assert r_path.known_digest == _sha(V3_BODY)
    assert r_path.witnesses == (both_child,)
    assert r_path.overlapping_occurrences == tuple(sorted((s1, s2, both_child)))
    for sibling in (s1, s2):
        row_ = row(group_record(resolved, sibling), "A.md")
        assert row_.status is CurrentnessStatus.STALE
        assert row_.reasons == (CurrentnessReason.PROVEN_CHANGE,)
        assert row_.witnesses == (both_child,)
    assert resolved.usable_occurrences == (both_child,)

    # A descendant of ONLY s1: s2 stays a retained conflicting
    # witness (the frontier is never trimmed to the newest branch).
    h = History(mode, endpoint)
    h.boot_root()
    s1 = h.read("sibling-one-occ", V1_BODY)
    s2 = h.read("sibling-two-occ", V2_BODY)
    h.issue("one-child-occ", (s1, CAUSAL_ROOT_FACT))
    one_child = h.read("one-child-occ", V3_BODY)
    partial = h.overlay()
    p_path = path_record(partial, "A.md")
    assert p_path.status is CurrentnessStatus.CONTENT_CONFLICT
    assert p_path.reasons == (CurrentnessReason.KNOWN_CONTENT_CONFLICT,)
    assert p_path.witnesses == tuple(sorted((one_child, s2)))
    assert p_path.overlapping_occurrences == tuple(sorted((s1, s2, one_child)))
    assert row(group_record(partial, s1), "A.md").status is CurrentnessStatus.STALE
    other_row = row(group_record(partial, s2), "A.md")
    assert other_row.status is CurrentnessStatus.CONTENT_CONFLICT
    assert other_row.reasons == (CurrentnessReason.KNOWN_CONTENT_CONFLICT,)
    assert other_row.witnesses == (one_child,)
    assert partial.usable_occurrences == ()

    # Receipts in reversed arrival order: chronology still comes from
    # the frozen edges, never from registration order.
    h = History(mode, endpoint)
    h.boot_root()
    r1 = h.read("reverse-one-occ", V1_BODY)
    r2 = h.read("reverse-two-occ", V2_BODY)
    h.receipt("reverse-two-occ", (r1, CAUSAL_ROOT_FACT))
    h.receipt("reverse-one-occ", (CAUSAL_ROOT_FACT,))
    assert relation(h.state, h.ns, r1, r2) is CausalRelation.BEFORE
    assert relation(h.state, h.ns, r2, r1) is CausalRelation.AFTER
    ordered = h.overlay()
    o_path = path_record(ordered, "A.md")
    assert o_path.status is CurrentnessStatus.CURRENT_KNOWN
    assert o_path.known_digest == _sha(V2_BODY)
    assert o_path.witnesses == (r2,)
    assert row(group_record(ordered, r1), "A.md").status is CurrentnessStatus.STALE
    assert ordered.usable_occurrences == (r2,)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_boundaryless_group_laws_battery(mode: AdmissionMode, endpoint: str) -> None:
    """Boundaryless (opaque) group law battery: a shared-member
    boundaryless descendant stales the older group ONLY with
    UNPROVEN_OWNERSHIP (never proven-change); a new group with the
    SAME group bytes carries the SAME opaque identity and does not
    stale the equally evidenced older group (equality removes the
    blocker, it never manufactures an edge); and two INCOMPARABLE
    reversed-member boundaryless groups (AB vs BA) carry DIFFERENT
    opaque identities, leaving every shared path in
    OWNERSHIP_AMBIGUITY with both witnesses retained."""
    # AB -> AC: the OLDER boundaryless group claims (A, B); the
    # DESCENDANT boundaryless group claims (A, C).  Only A overlaps:
    # B stays the older group's maximal current component, C is the
    # new maximal current component, and the whole old AB is unusable
    # with its A component unproven-stale while its B row stays
    # current.
    h = History(mode, endpoint)
    h.boot_root()
    ab = h.read("ab-occ", "A-body\nB-body\n", cmd="cat A.md B.md")
    h.issue("ac-occ", (ab, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat A.md C.md"}))
    ac = h.read("ac-occ", "A2-body\nC2-body\n", cmd="cat A.md C.md")
    ab_occurrence = next(
        occurrence for occurrence in h.state.occurrences if occurrence.occurrence_id == ab
    )
    ac_occurrence = next(
        occurrence for occurrence in h.state.occurrences if occurrence.occurrence_id == ac
    )
    assert [member.normalized for member in ab_occurrence.proof.requested_members] == [
        "A.md",
        "B.md",
    ]
    assert [member.normalized for member in ac_occurrence.proof.requested_members] == [
        "A.md",
        "C.md",
    ]
    assert relation(h.state, h.ns, ab, ac) is CausalRelation.BEFORE
    overlay = h.overlay()
    a_record = path_record(overlay, "A.md")
    assert a_record.status is CurrentnessStatus.CURRENT_OPAQUE
    assert a_record.witnesses == (ac,)
    b_record = path_record(overlay, "B.md")
    assert b_record.status is CurrentnessStatus.CURRENT_OPAQUE
    assert b_record.witnesses == (ab,)
    c_record = path_record(overlay, "C.md")
    assert c_record.status is CurrentnessStatus.CURRENT_OPAQUE
    assert c_record.witnesses == (ac,)
    ab_group = group_record(overlay, ab)
    assert ab_group.boundary_class is BoundaryClass.BOUNDARYLESS
    assert ab_group.members == ("A.md", "B.md")
    assert ab_group.group_status is CurrentnessStatus.STALE
    a_row = row(ab_group, "A.md")
    assert a_row.status is CurrentnessStatus.STALE
    assert a_row.reasons == (CurrentnessReason.UNPROVEN_OWNERSHIP,)
    assert a_row.witnesses == (ac,)
    b_row = row(ab_group, "B.md")
    assert b_row.status is CurrentnessStatus.CURRENT_OPAQUE
    assert b_row.witnesses == ()
    assert group_record(overlay, ac).group_status is CurrentnessStatus.CURRENT_OPAQUE
    assert overlay.usable_occurrences == (ac,)

    # AB -> A -> new AB with the SAME group bytes.
    h = History(mode, endpoint)
    h.boot_root()
    ab = h.read("ab-occ", "A-body\nB-body\n", cmd="cat A.md B.md")
    h.issue("a-occ", (ab, CAUSAL_ROOT_FACT))
    a_single = h.read("a-occ", V1_BODY)
    h.issue("ab2-occ", (a_single, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat A.md B.md"}))
    ab2 = h.read("ab2-occ", "A-body\nB-body\n", cmd="cat A.md B.md")
    overlay = h.overlay()
    ab_group = group_record(overlay, ab)
    ab2_group = group_record(overlay, ab2)
    assert ab_group.opaque_identity == ab2_group.opaque_identity
    a_path = path_record(overlay, "A.md")
    assert a_path.status is CurrentnessStatus.CURRENT_OPAQUE
    assert a_path.opaque_identity == ab2_group.opaque_identity
    assert a_path.witnesses == (ab2,)
    b_path = path_record(overlay, "B.md")
    assert b_path.status is CurrentnessStatus.CURRENT_OPAQUE
    assert b_path.witnesses == (ab2,)
    # Equal evidence: the older group is NOT staled by the equal
    # newer group (the proven middle group is, with UNPROVEN only).
    for path in ("A.md", "B.md"):
        assert row(ab_group, path).status is CurrentnessStatus.CURRENT_OPAQUE
    middle_row = row(group_record(overlay, a_single), "A.md")
    assert middle_row.status is CurrentnessStatus.STALE
    assert middle_row.reasons == (CurrentnessReason.UNPROVEN_OWNERSHIP,)
    assert middle_row.witnesses == (ab2,)
    assert overlay.usable_occurrences == tuple(sorted((ab, ab2)))

    # AB vs BA with the SAME aggregate bytes: the retained group
    # digests are EQUAL but the ordered members are reversed, so the
    # versioned opaque identities are DISTINCT -> ownership ambiguity
    # on both shared paths with both witnesses retained (order is
    # bound; aggregate bytes alone never are).
    h = History(mode, endpoint)
    h.boot_root()
    ab = h.read("ab-occ", "x\ny\n", cmd="cat A.md B.md")
    ba = h.read("ba-occ", "x\ny\n", cmd="cat B.md A.md")
    assert relation(h.state, h.ns, ab, ba) is CausalRelation.INCOMPARABLE
    ab_occurrence = next(
        occurrence for occurrence in h.state.occurrences if occurrence.occurrence_id == ab
    )
    ba_occurrence = next(
        occurrence for occurrence in h.state.occurrences if occurrence.occurrence_id == ba
    )
    assert [member.normalized for member in ab_occurrence.proof.requested_members] == [
        "A.md",
        "B.md",
    ]
    assert [member.normalized for member in ba_occurrence.proof.requested_members] == [
        "B.md",
        "A.md",
    ]
    assert (
        ab_occurrence.proof.segments[0].digest
        == ba_occurrence.proof.segments[0].digest
        == _sha("x\ny\n")
    )
    overlay = h.overlay()
    ab_group = group_record(overlay, ab)
    ba_group = group_record(overlay, ba)
    assert ab_group.members == ("A.md", "B.md")
    assert ba_group.members == ("B.md", "A.md")
    assert ab_group.opaque_identity != ba_group.opaque_identity
    for path in ("A.md", "B.md"):
        record = path_record(overlay, path)
        assert record.status is CurrentnessStatus.OWNERSHIP_AMBIGUITY, path
        assert record.reasons == (CurrentnessReason.OWNERSHIP_AMBIGUITY,), path
        assert record.known_digest is None
        assert record.opaque_identity is None
        assert record.witnesses == tuple(sorted((ab, ba))), path
        for group in (ab_group, ba_group):
            other = ba if group.occurrence_id == ab else ab
            row_ = row(group, path)
            assert row_.status is CurrentnessStatus.OWNERSHIP_AMBIGUITY, (group, path)
            assert row_.reasons == (CurrentnessReason.OWNERSHIP_AMBIGUITY,), (group, path)
            # A row's witnesses are the BLOCKING other claims only.
            assert row_.witnesses == (other,), (group, path)
    assert overlay.usable_occurrences == ()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_partition_proven_and_mixed_ownership_laws(mode: AdmissionMode, endpoint: str) -> None:
    """Partition-proven law: a ``cat A.md && echo 'MARK' &&
    cat B.md`` read earns two individually proven single-member
    groups; a newer PROVEN descendant read with the SAME digest
    leaves the older row CURRENT_KNOWN (equality), a changed digest
    stales it with PROVEN_CHANGE.  Mixed-ownership law: a proven
    known read and an INCOMPARABLE boundaryless group sharing the
    path leave the path in OWNERSHIP_AMBIGUITY (known vs
    unattributed mix) with both retained."""
    # Proven + opaque incomparable mix on A.md.
    h = History(mode, endpoint)
    h.boot_root()
    proven_a = h.read("proven-a-occ", V1_BODY)
    ab = h.read("ab-occ", "A-body\nB-body\n", cmd="cat A.md B.md")
    assert relation(h.state, h.ns, proven_a, ab) is CausalRelation.INCOMPARABLE
    overlay = h.overlay()
    a_path = path_record(overlay, "A.md")
    assert a_path.status is CurrentnessStatus.OWNERSHIP_AMBIGUITY
    assert a_path.reasons == (CurrentnessReason.OWNERSHIP_AMBIGUITY,)
    assert a_path.known_digest is None
    assert a_path.opaque_identity is None
    assert a_path.witnesses == tuple(sorted((proven_a, ab)))
    proven_row = row(group_record(overlay, proven_a), "A.md")
    assert proven_row.status is CurrentnessStatus.OWNERSHIP_AMBIGUITY
    assert proven_row.reasons == (CurrentnessReason.OWNERSHIP_AMBIGUITY,)
    assert proven_row.witnesses == (ab,)
    ab_group = group_record(overlay, ab)
    ab_a_row = row(ab_group, "A.md")
    assert ab_a_row.status is CurrentnessStatus.OWNERSHIP_AMBIGUITY
    assert ab_a_row.witnesses == (proven_a,)
    assert row(ab_group, "B.md").status is CurrentnessStatus.CURRENT_OPAQUE

    # Partition-proven equal/changed descendants.
    h = History(mode, endpoint)
    h.boot_root()
    partition = h.read(
        "partition-occ", "A-content\nMARK\nB-content\n", cmd="cat A.md && echo 'MARK' && cat B.md"
    )
    partition_proof = next(
        occurrence.proof
        for occurrence in h.state.occurrences
        if occurrence.occurrence_id == partition
    )
    assert len(partition_proof.segments) == 2
    assert partition_proof.segments[0].member_digest == _sha("A-content\n")
    assert partition_proof.segments[1].member_digest == _sha("B-content\n")
    # Each proven segment is its OWN group: the A group is index 0,
    # the B group is index 1 (segment order, provenance only).
    h.issue("a-eq-occ", (partition, CAUSAL_ROOT_FACT))
    a_eq = h.read("a-eq-occ", "A-content\n")
    overlay = h.overlay()
    a_path = path_record(overlay, "A.md")
    assert a_path.status is CurrentnessStatus.CURRENT_KNOWN
    assert a_path.known_digest == _sha("A-content\n")
    assert a_path.witnesses == (a_eq,)
    a_group = group_record(overlay, partition, 0)
    b_group = group_record(overlay, partition, 1)
    assert a_group.members == ("A.md",)
    assert b_group.members == ("B.md",)
    assert row(a_group, "A.md").status is CurrentnessStatus.CURRENT_KNOWN
    assert row(b_group, "B.md").status is CurrentnessStatus.CURRENT_KNOWN
    assert a_group.group_status is CurrentnessStatus.CURRENT_KNOWN
    assert b_group.group_status is CurrentnessStatus.CURRENT_KNOWN
    assert overlay.usable_occurrences == tuple(sorted((partition, a_eq)))
    h.issue("a-ch-occ", (a_eq, CAUSAL_ROOT_FACT))
    a_ch = h.read("a-ch-occ", "A-CHANGED\n")
    overlay = h.overlay()
    a_path = path_record(overlay, "A.md")
    assert a_path.status is CurrentnessStatus.CURRENT_KNOWN
    assert a_path.known_digest == _sha("A-CHANGED\n")
    assert a_path.witnesses == (a_ch,)
    a_group = group_record(overlay, partition, 0)
    b_group = group_record(overlay, partition, 1)
    partition_row = row(a_group, "A.md")
    assert partition_row.status is CurrentnessStatus.STALE
    assert partition_row.reasons == (CurrentnessReason.PROVEN_CHANGE,)
    assert partition_row.witnesses == (a_ch,)
    assert a_group.group_status is CurrentnessStatus.STALE
    # The untouched B group of the same occurrence stays current.
    assert row(b_group, "B.md").status is CurrentnessStatus.CURRENT_KNOWN
    assert b_group.group_status is CurrentnessStatus.CURRENT_KNOWN
    eq_row = row(group_record(overlay, a_eq), "A.md")
    assert eq_row.status is CurrentnessStatus.STALE
    assert eq_row.reasons == (CurrentnessReason.PROVEN_CHANGE,)
    assert eq_row.witnesses == (a_ch,)
    assert overlay.usable_occurrences == (a_ch,)


REPEAT_CMD = "cat A.md && echo 'MARK' && cat A.md"


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_repeated_a_groups_same_occurrence_laws(mode: AdmissionMode, endpoint: str) -> None:
    """ONE completed read of ``cat A.md && echo 'MARK' && cat A.md``
    earns exactly ONE occurrence carrying TWO separately proven
    singleton A segments (member positions (0) and (1), members
    (A.md, A.md)).  The same occurrence's two groups never order each
    other (no self-clock): equal digests keep the path CURRENT_KNOWN
    with both groups retained and current, while differing digests put
    the path in CONTENT_CONFLICT and block BOTH groups (usable
    emptied)."""
    for equal in (True, False):
        h = History(mode, endpoint)
        h.boot_root()
        first = V1_BODY
        second = first if equal else V2_BODY
        h.read("ra", first + "MARK\n" + second, cmd=REPEAT_CMD)
        assert len(h.state.occurrences) == 1
        occurrence = h.state.occurrences[0]
        assert occurrence.endpoint == endpoint
        assert occurrence.proof.kind is BundleProofKind.PARTITIONED
        assert [m.normalized for m in occurrence.proof.requested_members] == [
            "A.md",
            "A.md",
        ]
        segments = occurrence.proof.segments
        assert [tuple(s.member_positions) for s in segments] == [(0,), (1,)]
        assert segments[0].member_digest == _sha(first)
        assert segments[1].member_digest == _sha(second)
        overlay = h.overlay()
        occ_id = occurrence.occurrence_id
        path = path_record(overlay, "A.md")
        assert path.witnesses == (occ_id,)
        assert path.overlapping_occurrences == (occ_id,)
        if equal:
            assert path.status is CurrentnessStatus.CURRENT_KNOWN
            assert path.known_digest == _sha(first)
            for group_index in (0, 1):
                group = group_record(overlay, occ_id, group_index)
                assert group.boundary_class is BoundaryClass.PROVEN
                assert group.group_status is CurrentnessStatus.CURRENT_KNOWN
                assert row(group, "A.md").status is CurrentnessStatus.CURRENT_KNOWN
            assert overlay.usable_occurrences == (occ_id,)
        else:
            assert path.status is CurrentnessStatus.CONTENT_CONFLICT
            assert path.reasons == (CurrentnessReason.KNOWN_CONTENT_CONFLICT,)
            assert path.known_digest is None
            for group_index in (0, 1):
                group = group_record(overlay, occ_id, group_index)
                assert group.boundary_class is BoundaryClass.PROVEN
                assert group.group_status is CurrentnessStatus.CONTENT_CONFLICT
                row_ = row(group, "A.md")
                assert row_.status is CurrentnessStatus.CONTENT_CONFLICT
                assert row_.reasons == (CurrentnessReason.KNOWN_CONTENT_CONFLICT,)
            assert overlay.usable_occurrences == ()


TRUNCATED_FRAME = (
    "Chunk ID: 3d4e5f\n"
    "Wall time: 0.6789 seconds\n"
    "Process exited with code 0\n"
    "Original token count: 512\n"
    "Output:\n"
    "Warning: truncated output (original token count: 512)\n"
    "Total output lines: 64\n"
    "\n"
    "head\ntail\n"
)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_delayed_outstanding_result_is_incomparable_not_latest(
    mode: AdmissionMode, endpoint: str
) -> None:
    """An issued-but-outstanding read acquires NOTHING until its result
    arrives.  When its result arrives LATE -- after a newer read from a
    different completed frontier has already completed -- the frozen
    issuance frontiers (root for the old, the middle B read for the
    new) make them INCOMPARABLE: the late arrival is never
    latest-wins and never stales the newer fact.  A genuine descendant
    of BOTH resolves the path, and a SHIFTED replay of the late old
    original (same call/result, unrelated user item prepended) is a
    pure REPLAYED no-op that preserves the exact state and overlay."""
    h = History(mode, endpoint)
    h.boot_root()
    h.issue("old-outstanding", (CAUSAL_ROOT_FACT,))
    assert h.state.occurrences == ()
    assert h.overlay().paths == ()
    middle = h.read("middle-occ", "middle-body\n", cmd="cat B.md")
    h.issue("new-completed", (middle, CAUSAL_ROOT_FACT))
    new = h.read("new-completed", "new-body\n")
    assert relation(h.state, h.ns, middle, new) is CausalRelation.BEFORE
    new_path = path_record(h.overlay(), "A.md")
    assert new_path.status is CurrentnessStatus.CURRENT_KNOWN
    assert new_path.known_digest == _sha("new-body\n")
    assert new_path.witnesses == (new,)
    old = h.read("old-outstanding", "old-body\n")
    assert relation(h.state, h.ns, old, new) is CausalRelation.INCOMPARABLE
    overlay = h.overlay()
    path = path_record(overlay, "A.md")
    assert path.status is CurrentnessStatus.CONTENT_CONFLICT
    assert path.reasons == (CurrentnessReason.KNOWN_CONTENT_CONFLICT,)
    assert path.known_digest is None
    assert path.witnesses == tuple(sorted((old, new)))
    assert path.overlapping_occurrences == tuple(sorted((old, new)))
    assert old not in overlay.usable_occurrences
    assert new not in overlay.usable_occurrences
    assert middle in overlay.usable_occurrences
    h.issue("merge-occ", (old, new, CAUSAL_ROOT_FACT))
    merge = h.read("merge-occ", "resolved-body\n")
    overlay = h.overlay()
    path = path_record(overlay, "A.md")
    assert path.status is CurrentnessStatus.CURRENT_KNOWN
    assert path.known_digest == _sha("resolved-body\n")
    assert path.witnesses == (merge,)
    assert set(overlay.usable_occurrences) == {middle, merge}
    assert group_record(overlay, old).group_status is CurrentnessStatus.STALE
    assert group_record(overlay, new).group_status is CurrentnessStatus.STALE
    field = "input" if endpoint == "responses" else "messages"
    original = read_request(endpoint, "old-outstanding", "old-body\n")
    items = original.payload[field]
    assert isinstance(items, list)
    shifted = GraphRequest(
        payload={field: [{"role": "user", "content": "synthetic unrelated text"}, *items]},
        endpoint=endpoint,
        context=None,
    )
    before = h.state
    prior = h.overlay()
    transition = observe_causal_history((shifted,), h.ns, before, h.revision)
    assert transition.outcome is CausalHistoryOutcome.REPLAYED
    assert transition.state is before
    assert h.overlay().model_dump() == prior.model_dump()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_pending_and_truncated_never_supersede_completed(
    mode: AdmissionMode, endpoint: str
) -> None:
    """A pending (RUNNING) result and a truncated result never create a
    completed occurrence or a path claim: the previously completed read
    stays current with its original witness, the exact retained
    non-acquiring result facts are honest (complete=False, the
    original 017 closed limitations), and the frontier never moves to
    the non-acquiring attempt."""
    h = History(mode, endpoint)
    h.boot_root()
    prior = h.read("prior-occ", V1_BODY)
    prior_path = path_record(h.overlay(), "A.md")
    assert prior_path.status is CurrentnessStatus.CURRENT_KNOWN
    assert prior_path.known_digest == _sha(V1_BODY)
    assert prior_path.witnesses == (prior,)
    h.issue("after-occ", (prior,))
    running = observe_causal_history(
        (framed_read_request(endpoint, "after-occ", running_frame(V2_BODY)),),
        h.ns,
        h.state,
        h.revision,
    )
    assert running.outcome is CausalHistoryOutcome.ACCEPTED
    assert running.state is not h.state
    assert all(occurrence.call_id != "after-occ" for occurrence in running.state.occurrences)
    running_result = next(
        result for result in running.state.results if result.call_id == "after-occ"
    )
    assert running_result.complete is False
    h.state, h.revision = running.state, running.revision_after
    result = derive_currentness_overlay(h.state, h.ns)
    assert result.outcome is CurrentnessOutcome.OK
    assert result.state is h.state
    running_overlay = result.overlay
    assert running_overlay is not None
    running_path = path_record(running_overlay, "A.md")
    assert running_path.status is CurrentnessStatus.CURRENT_KNOWN
    assert running_path.known_digest == _sha(V1_BODY)
    assert running_path.witnesses == (prior,)
    h.issue("trunc-occ", (prior,))
    truncated = observe_causal_history(
        (framed_read_request(endpoint, "trunc-occ", TRUNCATED_FRAME),),
        h.ns,
        h.state,
        h.revision,
    )
    assert truncated.outcome is CausalHistoryOutcome.ACCEPTED
    assert all(occurrence.call_id != "trunc-occ" for occurrence in truncated.state.occurrences)
    truncated_result = next(
        result for result in truncated.state.results if result.call_id == "trunc-occ"
    )
    assert truncated_result.complete is False
    for limitation in (Limitation.MALFORMED_WRAPPER, Limitation.PROCESS_TRUNCATED):
        assert limitation in truncated.observation_limitations
    h.state, h.revision = truncated.state, truncated.revision_after
    result = derive_currentness_overlay(h.state, h.ns)
    assert result.outcome is CurrentnessOutcome.OK
    assert result.state is h.state
    final_overlay = result.overlay
    assert final_overlay is not None
    final_path = path_record(final_overlay, "A.md")
    assert final_path.status is CurrentnessStatus.CURRENT_KNOWN
    assert final_path.known_digest == _sha(V1_BODY)
    assert final_path.witnesses == (prior,)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_unrelated_b_preserves_current_a_and_semantic_key(
    mode: AdmissionMode, endpoint: str
) -> None:
    """An unrelated B read does not change the A path record (identical
    status/digest/witnesses) and the ACTUAL accepted 018-c structural
    content key for the A read stays byte-identical: an unchanged
    semantic source never gains a new key from unrelated observations
    or history revisions."""
    h = History(mode, endpoint)
    h.boot_root()
    a_read = read_request(endpoint, "t6-a-occ", V1_BODY)
    h.observe(a_read, note="t6 A read")
    before = path_record(h.overlay(), "A.md")
    assert before.status is CurrentnessStatus.CURRENT_KNOWN
    assert before.known_digest == _sha(V1_BODY)
    admission_ns = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-history-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
    )
    before_snapshot = observe_bundle_admission_batch((root_request(), a_read), admission_ns)
    assert before_snapshot.outcome is AdmissionOutcome.COMPLETE
    entry = before_snapshot.entries[0]
    assert entry.key_record.member_occurrences == ("A.md",)
    assert entry.key_record.aggregate_source_digest == _sha(V1_BODY)
    before_key = entry.content_key
    b_read = read_request(endpoint, "t6-b-occ", "beta\n", cmd="cat B.md")
    h.observe(b_read, note="t6 B read")
    assert any(occurrence.call_id == "t6-b-occ" for occurrence in h.state.occurrences)
    after = path_record(h.overlay(), "A.md")
    assert after.model_dump() == before.model_dump()
    after_snapshot = observe_bundle_admission_batch((root_request(), a_read, b_read), admission_ns)
    assert after_snapshot.outcome is AdmissionOutcome.COMPLETE
    after_entry = next(
        e for e in after_snapshot.entries if e.key_record.member_occurrences == ("A.md",)
    )
    assert after_entry.content_key == before_key
    assert after_entry.key_record.aggregate_source_digest == _sha(V1_BODY)
    b_path = path_record(h.overlay(), "B.md")
    assert b_path.status is CurrentnessStatus.CURRENT_KNOWN
    assert b_path.known_digest == _sha("beta\n")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_mixed_known_conflict_and_ownership_blockers_retained(
    mode: AdmissionMode, endpoint: str
) -> None:
    """Two known-different incomparable singleton reads plus one
    incomparable boundaryless AB: the path is CONTENT_CONFLICT with
    ALL THREE maximal witnesses retained, and EACH singleton group row
    carries BOTH blockers at once (KNOWN_CONTENT_CONFLICT against the
    other known digest and OWNERSHIP_AMBIGUITY against the unattributed
    group) -- no last-writer shortcut, no dropped blocker."""
    h = History(mode, endpoint)
    h.boot_root()
    a1 = h.read("mixed-known-one", V1_BODY)
    a2 = h.read("mixed-known-two", V2_BODY)
    ab = h.read("mixed-opaque", "opaque-ab\n", cmd="cat A.md B.md")
    overlay = h.overlay()
    path = path_record(overlay, "A.md")
    assert path.status is CurrentnessStatus.CONTENT_CONFLICT
    assert path.known_digest is None
    assert path.opaque_identity is None
    assert path.witnesses == tuple(sorted((a1, a2, ab)))
    for occ in (a1, a2):
        row_ = row(group_record(overlay, occ), "A.md")
        assert row_.status is CurrentnessStatus.CONTENT_CONFLICT
        assert row_.reasons == (
            CurrentnessReason.KNOWN_CONTENT_CONFLICT,
            CurrentnessReason.OWNERSHIP_AMBIGUITY,
        )
        assert row_.witnesses == tuple(sorted(w for w in (a1, a2, ab) if w != occ))
    opaque_row = row(group_record(overlay, ab), "A.md")
    assert opaque_row.status is CurrentnessStatus.OWNERSHIP_AMBIGUITY
    assert opaque_row.reasons == (CurrentnessReason.OWNERSHIP_AMBIGUITY,)
    assert opaque_row.witnesses == tuple(sorted((a1, a2)))
    assert overlay.usable_occurrences == ()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_root_only_and_mixed_root_reads_are_scope_context(
    mode: AdmissionMode, endpoint: str
) -> None:
    """The root is immutable scope context, never a nonroot contender:
    a completed ``cat AGENTS.md`` read of the exact root bytes creates
    NO nonroot path record at all, and a boundaryless
    ``cat AGENTS.md A.md`` read keeps the A.md path current-opaque
    from the group without ever emitting an AGENTS.md row or record."""
    h = History(mode, endpoint)
    h.boot_root()
    assert h.state.root is not None
    root_text = h.state.root.root_text
    h.issue(
        "root-only-occ",
        (CAUSAL_ROOT_FACT,),
        json.dumps({"cmd": "cat AGENTS.md"}),
    )
    root_only = h.read("root-only-occ", root_text, cmd="cat AGENTS.md")
    root_only_occ = next(
        occurrence for occurrence in h.state.occurrences if occurrence.occurrence_id == root_only
    )
    assert [member.normalized for member in root_only_occ.proof.requested_members] == ["AGENTS.md"]
    assert root_only_occ.proof.segments[0].member_digest == _sha(root_text)
    overlay = h.overlay()
    assert overlay.paths == ()
    root_group = group_record(overlay, root_only)
    assert root_group.root_path == "AGENTS.md"
    assert root_group.members == ("AGENTS.md",)
    assert root_group.path_rows == ()
    h = History(mode, endpoint)
    h.boot_root()
    assert h.state.root is not None
    root_text = h.state.root.root_text
    h.issue(
        "root-mixed-occ",
        (CAUSAL_ROOT_FACT,),
        json.dumps({"cmd": "cat AGENTS.md A.md"}),
    )
    mixed = h.read("root-mixed-occ", root_text + "alpha\n", cmd="cat AGENTS.md A.md")
    mixed_occ = next(
        occurrence for occurrence in h.state.occurrences if occurrence.occurrence_id == mixed
    )
    assert [member.normalized for member in mixed_occ.proof.requested_members] == [
        "AGENTS.md",
        "A.md",
    ]
    assert mixed_occ.proof.segments[0].member_digest is None
    overlay = h.overlay()
    assert all(record.path != "AGENTS.md" for record in overlay.paths)
    a_path = path_record(overlay, "A.md")
    assert a_path.status is CurrentnessStatus.CURRENT_OPAQUE
    assert a_path.known_digest is None
    assert a_path.witnesses == (mixed,)
    mixed_group = group_record(overlay, mixed)
    assert mixed_group.boundary_class is BoundaryClass.BOUNDARYLESS
    assert mixed_group.root_path == "AGENTS.md"
    assert mixed_group.members == ("AGENTS.md", "A.md")
    assert [record.path for record in mixed_group.path_rows] == ["A.md"]
    assert overlay.usable_occurrences == (mixed,)


def _refused_over_bound(
    result: CurrentnessResult, state: CausalHistoryState, limitation: CurrentnessLimitation
) -> None:
    assert result.outcome is CurrentnessOutcome.REFUSED_OVER_BOUND
    assert result.diagnostics == (limitation,)
    assert result.state is state
    assert result.overlay is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_operational_bound_gates_at_limit_and_one_over(mode: AdmissionMode, endpoint: str) -> None:
    """Every new operational bound is exercised at its ACTUAL
    fixture-specific limit (OK) and one over (atomic typed refusal
    with the exact prior state and no partial overlay).  The work
    ceilings are shared-ledger pins: ONE budget covers the whole
    derivation including state validation (a fresh per-stage budget
    would allow a smaller total)."""
    h = History(mode, endpoint)
    h.boot_root()
    # Exactly ONE completed read.
    h.read("gate-one", V1_BODY)
    one = h.state
    assert len(one.occurrences) == 1
    assert one.occurrences[0].proof.segments[0].member_digest == _sha(V1_BODY)
    _refused_over_bound(
        derive_currentness_overlay(one, h.ns, CurrentnessBounds(max_work_units=1)),
        one,
        CurrentnessLimitation.WORK_UNITS_OVER_BOUND,
    )
    _refused_over_bound(
        derive_currentness_overlay(one, h.ns, CurrentnessBounds(max_work_units=18)),
        one,
        CurrentnessLimitation.WORK_UNITS_OVER_BOUND,
    )
    at_limit = derive_currentness_overlay(one, h.ns, CurrentnessBounds(max_work_units=19))
    assert at_limit.outcome is CurrentnessOutcome.OK
    assert at_limit.overlay is not None
    # Exactly TWO unissued same-path reads.
    h = History(mode, endpoint)
    h.boot_root()
    h.read("gate-two-1", V1_BODY)
    h.read("gate-two-2", V2_BODY)
    two = h.state
    assert len(two.occurrences) == 2
    _refused_over_bound(
        derive_currentness_overlay(two, h.ns, CurrentnessBounds(max_work_units=46)),
        two,
        CurrentnessLimitation.WORK_UNITS_OVER_BOUND,
    )
    at_limit = derive_currentness_overlay(two, h.ns, CurrentnessBounds(max_work_units=47))
    assert at_limit.outcome is CurrentnessOutcome.OK
    assert at_limit.overlay is not None
    _refused_over_bound(
        derive_currentness_overlay(two, h.ns, CurrentnessBounds(max_relation_pairs=3)),
        two,
        CurrentnessLimitation.RELATION_PAIRS_OVER_BOUND,
    )
    at_limit = derive_currentness_overlay(two, h.ns, CurrentnessBounds(max_relation_pairs=4))
    assert at_limit.outcome is CurrentnessOutcome.OK
    assert at_limit.overlay is not None
    # Exactly THREE unissued same-path reads (four emitted reason
    # entries: one path + one per singleton row).
    h = History(mode, endpoint)
    h.boot_root()
    h.read("gate-three-1", V1_BODY)
    h.read("gate-three-2", V2_BODY)
    h.read("gate-three-3", V3_BODY)
    three = h.state
    assert len(three.occurrences) == 3
    _refused_over_bound(
        derive_currentness_overlay(three, h.ns, CurrentnessBounds(max_work_units=81)),
        three,
        CurrentnessLimitation.WORK_UNITS_OVER_BOUND,
    )
    at_limit = derive_currentness_overlay(three, h.ns, CurrentnessBounds(max_work_units=82))
    assert at_limit.outcome is CurrentnessOutcome.OK
    assert at_limit.overlay is not None
    _refused_over_bound(
        derive_currentness_overlay(three, h.ns, CurrentnessBounds(max_diagnostics=3)),
        three,
        CurrentnessLimitation.DIAGNOSTICS_FULL,
    )
    at_limit = derive_currentness_overlay(three, h.ns, CurrentnessBounds(max_diagnostics=4))
    assert at_limit.outcome is CurrentnessOutcome.OK
    assert at_limit.overlay is not None
    # Two DISTINCT nonroot paths.
    h = History(mode, endpoint)
    h.boot_root()
    h.read("gate-paths-a", V1_BODY)
    h.read("gate-paths-b", "beta\n", cmd="cat B.md")
    paths_state = h.state
    assert len(paths_state.occurrences) == 2
    _refused_over_bound(
        derive_currentness_overlay(paths_state, h.ns, CurrentnessBounds(max_paths=1)),
        paths_state,
        CurrentnessLimitation.PATHS_OVER_BOUND,
    )
    at_limit = derive_currentness_overlay(paths_state, h.ns, CurrentnessBounds(max_paths=2))
    assert at_limit.outcome is CurrentnessOutcome.OK
    assert at_limit.overlay is not None
    # Two retained groups (one two-member read + one singleton).
    h = History(mode, endpoint)
    h.boot_root()
    h.read("gate-groups-wide", "A-body\nB-body\n", cmd="cat A.md B.md")
    one_group = h.state
    assert len(one_group.occurrences) == 1
    ok = derive_currentness_overlay(one_group, h.ns, CurrentnessBounds(max_groups=1))
    assert ok.outcome is CurrentnessOutcome.OK
    h.read("gate-groups-second", V2_BODY)
    two_groups = h.state
    assert len(two_groups.occurrences) == 2
    _refused_over_bound(
        derive_currentness_overlay(two_groups, h.ns, CurrentnessBounds(max_groups=1)),
        two_groups,
        CurrentnessLimitation.GROUPS_OVER_BOUND,
    )
    at_limit = derive_currentness_overlay(two_groups, h.ns, CurrentnessBounds(max_groups=2))
    assert at_limit.outcome is CurrentnessOutcome.OK
    assert at_limit.overlay is not None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_public_paths_perform_no_host_io(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every public currentness path -- the OK derivation and the
    foreign-scope / malformed-state / resource refusals -- performs no
    host IO: no file, socket, subprocess or path IO facility is
    touched after import/setup."""
    h = History(mode, endpoint)
    h.boot_root()
    h.read("io-occ", V1_BODY)
    h.read("io-occ-b", "beta\n", cmd="cat B.md")
    state = h.state
    attempts: list[str] = []

    def deny(name: str) -> Any:
        def fn(*args: object, **kwargs: object) -> object:
            attempts.append(name)
            raise AssertionError(f"unexpected IO facility: {name}")

        return fn

    monkeypatch.setattr(builtins, "open", deny("builtins.open"))
    monkeypatch.setattr(os, "open", deny("os.open"))
    monkeypatch.setattr(os, "stat", deny("os.stat"))
    monkeypatch.setattr(os, "lstat", deny("os.lstat"))
    monkeypatch.setattr(os, "chdir", deny("os.chdir"))
    monkeypatch.setattr(socket, "socket", deny("socket.socket"))
    monkeypatch.setattr(subprocess, "Popen", deny("subprocess.Popen"))
    monkeypatch.setattr(Path, "open", deny("Path.open"))
    monkeypatch.setattr(Path, "read_bytes", deny("Path.read_bytes"))
    monkeypatch.setattr(Path, "read_text", deny("Path.read_text"))
    ok = derive_currentness_overlay(state, h.ns)
    assert ok.outcome is CurrentnessOutcome.OK
    assert ok.overlay is not None
    foreign_ns = h.ns.model_copy(update={"history_key": "f" * 64})
    foreign = derive_currentness_overlay(state, foreign_ns)
    assert foreign.outcome is CurrentnessOutcome.REFUSED_FOREIGN_SCOPE
    assert foreign.overlay is None
    malformed = state.model_copy(update={"occurrences": state.occurrences * 2})
    mal = derive_currentness_overlay(malformed, h.ns)
    assert mal.outcome is CurrentnessOutcome.REFUSED_STATE_MALFORMED
    assert mal.overlay is None
    over = derive_currentness_overlay(state, h.ns, CurrentnessBounds(max_work_units=1))
    assert over.outcome is CurrentnessOutcome.REFUSED_OVER_BOUND
    assert over.overlay is None
    assert attempts == []


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_history_and_proof_inputs_unchanged_on_ok_and_refusals(
    mode: AdmissionMode, endpoint: str
) -> None:
    """The derivation never mutates its inputs: on the OK outcome the
    EXACT state object is returned and the deep dump plus every
    retained proof's exact bytes/digest/length are unchanged; on every
    refusal the exact input state is preserved with no partial
    overlay."""
    h = History(mode, endpoint)
    h.boot_root()
    h.read("imm-occ", V1_BODY)
    h.read("imm-occ-b", V2_BODY, cmd="cat B.md")
    state = h.state
    before = state.model_dump()
    proofs_before = [
        (
            occurrence.proof.source_text,
            occurrence.proof.source_digest,
            occurrence.proof.source_byte_length,
        )
        for occurrence in state.occurrences
    ]
    ok = derive_currentness_overlay(state, h.ns)
    assert ok.outcome is CurrentnessOutcome.OK
    assert ok.state is state
    assert state.model_dump() == before
    assert [
        (
            occurrence.proof.source_text,
            occurrence.proof.source_digest,
            occurrence.proof.source_byte_length,
        )
        for occurrence in state.occurrences
    ] == proofs_before
    foreign_ns = h.ns.model_copy(update={"history_key": "f" * 64})
    for result in (
        derive_currentness_overlay(state, foreign_ns),
        derive_currentness_overlay(state, h.ns, CurrentnessBounds(max_work_units=1)),
        derive_currentness_overlay(
            state.model_copy(update={"occurrences": state.occurrences * 2}), h.ns
        ),
    ):
        assert result.overlay is None
        assert result.outcome in (
            CurrentnessOutcome.REFUSED_FOREIGN_SCOPE,
            CurrentnessOutcome.REFUSED_OVER_BOUND,
            CurrentnessOutcome.REFUSED_STATE_MALFORMED,
        )
    assert state.model_dump() == before
    assert [
        (
            occurrence.proof.source_text,
            occurrence.proof.source_digest,
            occurrence.proof.source_byte_length,
        )
        for occurrence in state.occurrences
    ] == proofs_before


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_membership_blockers_and_charged_parent_edge_traversal(
    mode: AdmissionMode, endpoint: str
) -> None:
    """The exact ``max_witness_memberships`` unit formula is exercised
    at the real crossing on THREE known-different forks: 3 path-claim
    associations + 3 distinct overlapping (path, occurrence) index
    entries + 3 frontier witnesses + 3 group path rows + 6 distinct
    (group, path, witness) blocker associations = 18 charged units
    (cap 18 OK, 17 refuses).  Separately, the shared work budget covers
    the charged causal parent-edge traversals on an ACTUAL earned DAG:
    the exact issued two-occurrence chain fixture (call IDs
    chain-one/chain-two, three frozen parent links) costs 84 shared
    work units for the WHOLE derivation -- state validation including
    the retained issuances plus the charged closure walks -- versus
    the 47 of the same-count unissued pair (the extra units include
    the retained issuance facts and the charged parent-edge
    traversals): skipping the actual parent charges would lower this
    fixture's total and make the 83-unit refusal below fail."""
    h = History(mode, endpoint)
    h.boot_root()
    h.read("fork-one", V1_BODY)
    h.read("fork-two", V2_BODY)
    h.read("fork-three", V3_BODY)
    forks = h.state
    assert len(forks.occurrences) == 3
    _refused_over_bound(
        derive_currentness_overlay(forks, h.ns, CurrentnessBounds(max_witness_memberships=17)),
        forks,
        CurrentnessLimitation.WITNESS_MEMBERSHIPS_OVER_BOUND,
    )
    at_limit = derive_currentness_overlay(
        forks, h.ns, CurrentnessBounds(max_witness_memberships=18)
    )
    assert at_limit.outcome is CurrentnessOutcome.OK
    assert at_limit.overlay is not None
    h = History(mode, endpoint)
    h.boot_root()
    h.issue("chain-one", (CAUSAL_ROOT_FACT,))
    first = h.read("chain-one", V1_BODY)
    h.issue("chain-two", (first, CAUSAL_ROOT_FACT))
    second = h.read("chain-two", V2_BODY)
    chain = h.state
    assert len(chain.occurrences) == 2
    assert relation(h.state, h.ns, first, second) is CausalRelation.BEFORE
    assert len(chain.parent_links) == 3
    _refused_over_bound(
        derive_currentness_overlay(chain, h.ns, CurrentnessBounds(max_work_units=47)),
        chain,
        CurrentnessLimitation.WORK_UNITS_OVER_BOUND,
    )
    _refused_over_bound(
        derive_currentness_overlay(chain, h.ns, CurrentnessBounds(max_work_units=83)),
        chain,
        CurrentnessLimitation.WORK_UNITS_OVER_BOUND,
    )
    at_limit = derive_currentness_overlay(chain, h.ns, CurrentnessBounds(max_work_units=84))
    assert at_limit.outcome is CurrentnessOutcome.OK
    assert at_limit.overlay is not None
