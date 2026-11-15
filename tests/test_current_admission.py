"""018-g: original-API current bundle admission -- durable
known-synthetic controls over the ONE bounded pure derivation.

``derive_current_admission`` is the single original-API surface under
this order: it takes the ACTUAL 018-d retained state, its ACTUAL
namespace and the NEW current-admission bounds plus the ACTUAL
supplied currentness/current-graph bounds, derives the accepted
018-f current graph (internally, same run) AND the current admission
entries with the canonical 018-c semantic keys, exact retained
source/provenance and the complete reverse member index.  Stale,
conflicting and ambiguous groups are excluded BEFORE entry planning
or copying.  All fixtures are inline known-synthetic original
GraphRequests on BOTH read endpoints and BOTH admission modes; no S
runtime path dependency; no model, native, client or service
facility is started.

Locked law surface covered here (order sections A-G):
  A. withdrawal and return follow the ACTUAL current suppliers:
     after a completed-EMPTY descendant Start the possessed current
     originals (B and C) stay honest but unadmitted; the EXACT old
     replay restores nothing; a genuinely descendant Start restores
     entries from the SAME retained originals with original
     witnesses; independent alternates (D) and the self-supporting
     certificate cycle (AB->C->B) withdraw/restore with them;
  B. partitioned proven A|B: a changed descendant A leaves B
     independently current in LEAN (greedy gains no isolated-region
     rule); all-current controls retain the whole-bundle truth
     table; an opaque AB with a changed descendant A stays
     indivisible (no B-only splice); mixed eligible/background,
     empty/Unicode/CRLF and repeated-operand content variants;
  C. opaque AB conservatively stales after a descendant singleton
     (even equal-looking), replay does not restore, a genuine
     descendant new AB restores the whole with BOTH same-byte
     compatible witnesses; equal incomparable witnesses all
     retained; unissued reversed equal-aggregate AB/BA ambiguity
     supplies nothing; a changed child of ONE of two concurrent
     equal groups cannot resolve while a genuine child of BOTH
     (the actual two-frontier) restores one whole keeping the
     OLDER compatible proof; the delayed unequal late result of a
     same-frontier issued call is a retained incomparable content
     conflict (the unrelated current read stays admitted), a
     genuine descendant of both resolves it, and the exact
     shifted replay is a no-op;
  D. exact canonical 018-c key equality for unchanged A after
     unrelated B and for call-ID/occurrence changes, exact
     inequality for changed source/ownership/mode, and exact old-C
     batch canonical key equality under ONE shared admission
     namespace for the root/whole/isolated/repeated/Unicode/
     empty-root original-API cases;
  E. the root entry retains the ACTUAL RootAnchor typed fields
     (the exact EMPTY root legal); a changed-bytes root refresh
     stays refused by 018-d with the exact state while the root
     row is retained; a SAME-BYTES proven root-path read is
     consistent and admits an AGENTS.md file entry alongside the
     unchanged anchor row; a partitioned root-compatible group
     admits its whole (the proven nonroot segment survives) while
     a root-competing one is refused; root-bearing opaque reads
     supply no file entries while the root row stays retained;
  F. complete reverse index over overlaps, duplicates and greedy
     background; width distinct paths versus ordered repeated
     members; exact scope/revision/state identity;
  G. every new/inherited cap at limit and first over on the ONE
     shared outer plus the independent F-subtree ceiling (the
     essential POSITIVE: F cap exactly F's cost, G total above it,
     full G succeeds), the per-entry inherited single-source cap
     over the actual partitioned aggregate via a coherent
     stricter-bound DIAGNOSTIC projection (actual F positive at
     the cap AND one below; G refuses typed with ZERO additional
     source touches beyond the positive F), the cumulative
     entry-source bytes counted once per distinct interned key
     (duplicate witnesses count owned bytes once while
     association attempts count before dedup), the source
     stale-region sentinels, the merge-witness reserve-before-copy
     sentinel (counted first copy over the actual witness list),
     the plan/assembly charged-walk thresholds, typed
     foreign/version/no-root/malformed refusals with the exact
     state, 130 retained observations legal under the default
     ceilings, private operational reprs and no host IO on every
     public path.
"""

from __future__ import annotations

import builtins
import json
import os
import pathlib
import socket
import subprocess
from collections.abc import Callable, Iterator
from typing import Any

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles import current_admission as _impl
from slaif_local_coding.constitution.bundles.bundle_admission import (
    observe_bundle_admission_batch,
)
from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
    AdmissionOutcome,
    BundleAdmissionBounds,
    make_bundle_admission_namespace,
)
from slaif_local_coding.constitution.bundles.causal_history import (
    observe_causal_history,
    register_issuance,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
    CausalHistoryNamespace,
    CausalHistoryOutcome,
    CausalHistoryState,
    make_causal_history_namespace,
)
from slaif_local_coding.constitution.bundles.current_admission import (
    derive_current_admission,
)
from slaif_local_coding.constitution.bundles.current_admission_models import (
    CurrentAdmission,
    CurrentAdmissionBounds,
    CurrentAdmissionEntry,
    CurrentAdmissionLimitation,
    CurrentAdmissionOutcome,
    CurrentAdmissionPathAssociation,
    CurrentAdmissionResult,
    CurrentAdmissionWitness,
    RetainedRootProvenance,
    current_admission_scope_key,
)
from slaif_local_coding.constitution.bundles.current_graph import (
    derive_current_graph,
)
from slaif_local_coding.constitution.bundles.current_graph_models import (
    CurrentGraphBounds,
    CurrentGraphLimitation,
    CurrentGraphOutcome,
)
from slaif_local_coding.constitution.bundles.currentness import (
    derive_currentness_overlay,
)
from slaif_local_coding.constitution.bundles.currentness_models import (
    CurrentnessBounds,
)
from slaif_local_coding.constitution.bundles.graph_models import GraphBounds
from slaif_local_coding.constitution.bundles.graph_observation import GraphRequest
from slaif_local_coding.constitution.bundles.observation_models import (
    EMPTY_SOURCE_SHA256,
)
from tests.test_causal_history import (
    ENDPOINTS,
    FINGERPRINT,
    IDENTITY,
    MODES,
    WORKSPACE,
    empty_state,
    read_request,
    root_item,
)
from tests.test_current_graph import (
    _coherent_rekeyed_ns,
    _sha,
    forge,
)

CANARY = "ZCANARYZ"  # sentinel path token for the privacy controls
READ_ARGS = json.dumps({"cmd": "cat A.md"})


def make_ns_adm(
    mode: AdmissionMode,
    bounds: BundleAdmissionBounds | None = None,
    graph_bounds: GraphBounds | None = None,
) -> CausalHistoryNamespace:
    """A coherent history namespace carrying ACTUAL admission
    bounds (the admission namespace key recomputed from them)."""
    from slaif_local_coding.constitution.bundles.causal_history_models import (
        make_causal_history_namespace,
    )

    admission = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-history-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
        bounds=bounds,
        graph_bounds=graph_bounds,
    )
    return make_causal_history_namespace(admission, "synthetic-history-lineage")


class Adm:
    """Original-API history driver for the admission derivation.

    Tracks the EXACT (state, revision) pair over ONE namespace and
    the accepted 018-d transitions; refusals and replays are
    asserted at the call site through the raw transition, never
    through this helper.  ``read`` asserts the EXACT earned
    occurrence facts (endpoint, tool, source bytes/digest, member
    normalization) BEFORE any admission oracle may run.  For
    partitioned commands the caller uses ``observe`` plus explicit
    segment preconditions (the retained source excludes the marker)."""

    def __init__(
        self,
        mode: AdmissionMode,
        endpoint: str,
        bounds: BundleAdmissionBounds | None = None,
        graph_bounds: GraphBounds | None = None,
    ) -> None:
        self.mode = mode
        self.endpoint = endpoint
        self.ns = make_ns_adm(mode, bounds, graph_bounds)
        self.state = empty_state(self.ns)
        self.revision = 0
        self._issued: dict[str, tuple[str, str]] = {}

    def boot_root(self, body: str = "Read `A.md` before changing code.") -> None:
        self.observe(
            GraphRequest(payload={"input": [root_item(body)]}, endpoint="responses", context=None),
            note="root",
        )
        assert self.state.root is not None
        assert self.state.root.root_text == body
        assert self.state.root.root_digest == _sha(body)
        assert len(self.state.occurrences) == 0
        assert self.revision == 1

    def observe(self, request: GraphRequest, *, note: str = "") -> CausalHistoryOutcome:
        transition = observe_causal_history((request,), self.ns, self.state, self.revision)
        assert transition.outcome is CausalHistoryOutcome.ACCEPTED, (
            note,
            transition.outcome,
            transition.diagnostics,
        )
        self.state, self.revision = transition.state, transition.revision_after
        return transition.outcome

    def read(self, cid: str, body: str, cmd: str = "cat A.md") -> str:
        before = len(self.state.occurrences)
        self.observe(read_request(self.endpoint, cid, body, cmd), note=f"read:{cid}")
        occurrences = self.state.occurrences
        assert len(occurrences) == before + 1, "exactly one new occurrence"
        occurrence = occurrences[-1]
        assert occurrence.call_id == cid
        assert occurrence.endpoint == self.endpoint
        assert occurrence.tool_name == "exec_command"
        if cid in self._issued:
            fingerprint, issued_name = self._issued[cid]
            assert occurrence.argument_fingerprint == fingerprint
            assert occurrence.tool_name == issued_name
            assert occurrence.anchored is True
        proof = occurrence.proof
        assert proof.endpoint == self.endpoint
        assert proof.source_text == body
        assert proof.source_digest == _sha(body)
        assert proof.source_byte_length == len(body.encode("utf-8"))
        assert proof.source_char_length == len(body)
        if "&&" not in cmd and cmd.startswith("cat "):
            assert tuple(m.normalized for m in proof.requested_members) == tuple(cmd.split()[1:])
        return occurrence.occurrence_id

    def issue(self, cid: str, frontier: tuple[str, ...], args: str = READ_ARGS) -> None:
        transition = register_issuance(
            self.state,
            self.ns,
            cid,
            self.endpoint,
            "exec_command",
            args,
            frontier,
            self.revision,
        )
        assert transition.outcome is CausalHistoryOutcome.ACCEPTED, (
            cid,
            transition.outcome,
            transition.diagnostics,
        )
        self.state, self.revision = transition.state, transition.revision_after
        issued = next(i for i in self.state.issuances if i.call_id == cid)
        self._issued[cid] = (issued.argument_fingerprint, issued.tool_name)

    def replay(self, request: GraphRequest) -> None:
        transition = observe_causal_history((request,), self.ns, self.state, self.revision)
        assert transition.outcome is CausalHistoryOutcome.REPLAYED, (
            transition.outcome,
            transition.diagnostics,
        )
        assert transition.state is self.state

    def admission(
        self,
        bounds: CurrentAdmissionBounds | None = None,
        graph_bounds: CurrentGraphBounds | None = None,
    ) -> CurrentAdmissionResult:
        return derive_current_admission(self.state, self.ns, bounds, None, graph_bounds)

    def admission_ok(self, **kwargs: Any) -> CurrentAdmission:
        result = self.admission(**kwargs)
        assert result.outcome is CurrentAdmissionOutcome.OK, (
            result.outcome,
            result.diagnostics,
        )
        assert result.state is self.state
        assert result.overlay is not None
        assert result.diagnostics == ()
        return result.overlay


def assert_admission_refused(
    result: CurrentAdmissionResult,
    state: Any,
    outcome: CurrentAdmissionOutcome,
    limitation: CurrentAdmissionLimitation,
) -> None:
    """A fixed typed whole-result refusal over the EXACT input
    state: no partial admission, one closed reason."""
    assert result.outcome is outcome, (result.outcome, result.diagnostics)
    assert result.diagnostics == (limitation,), result.diagnostics
    assert result.state is state
    assert result.overlay is None


def members_of(admission: CurrentAdmission) -> dict[tuple[str, ...], CurrentAdmissionEntry]:
    return {tuple(entry.key_record.member_occurrences): entry for entry in admission.entries}


def witness_ids(entry: CurrentAdmissionEntry) -> list[str]:
    return [w.occurrence_id for w in entry.witnesses]


def _witness_key(
    w: CurrentAdmissionWitness,
) -> tuple[str, int, int, int, tuple[int, ...]]:
    """The canonical witness retention order key (full coordinates)."""
    return (
        w.occurrence_id,
        w.request_index,
        w.call_position,
        w.result_position,
        w.segment_indices,
    )


def _smallest_ok(lo: int, hi: int, probe: Callable[[int], bool]) -> int:
    """Smallest cap in [lo, hi] with probe(cap) OK (probe monotone)."""
    assert probe(hi), "the upper bound must already be OK"
    while lo < hi:
        mid = (lo + hi) // 2
        if probe(mid):
            hi = mid
        else:
            lo = mid + 1
    assert probe(lo)
    return lo


# ---------------------------------------------------------------------------
# A: withdrawal, replay, return, alternates and the certificate cycle
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_withdrawal_and_restoration(mode: AdmissionMode, endpoint: str) -> None:
    """A: Root->Start; Start-v1->B; B->C; C->E.  A descendant
    COMPLETE-EMPTY Start-v2 withdraws the outgoing derivations: B and
    C stay possessed but UNADMITTED (no entry) while the empty Start
    itself is admitted; the EXACT old Start-v1 replay is a no-op that
    restores nothing; a genuinely descendant Start-v3 restores the
    entries from the SAME retained B/C originals (no new downstream
    acquisition; original witnesses kept)."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `Start.md` first.")
    start1 = h.read("c-start1", "See `B.md`.", cmd="cat Start.md")
    b_occ = h.read("c-b", "See `C.md`.", cmd="cat B.md")
    c_occ = h.read("c-c", "See `E.md`.", cmd="cat C.md")
    a1 = h.admission_ok()
    by1 = members_of(a1)
    assert set(by1) == {("Start.md",), ("B.md",), ("C.md",)}
    for path in ("Start.md", "B.md", "C.md"):
        entry = by1[(path,)]
        assert entry.width == 1
        assert entry.admitted_segments == (0,)
        assert entry.key_record.aggregate_source_digest == _sha(
            {"Start.md": "See `B.md`.", "B.md": "See `C.md`.", "C.md": "See `E.md`."}[path]
        )
    assert witness_ids(by1[("B.md",)]) == [b_occ]
    assert witness_ids(by1[("C.md",)]) == [c_occ]
    assert a1.entry_source_bytes == 3 * 11 + len(b"Read `Start.md` first.")

    # A completed EMPTY descendant withdraws Start's outgoing
    # derivations; B and C stay honest and unadmitted.
    h.issue("c-start2", (start1, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat Start.md"}))
    start2 = h.read("c-start2", "", cmd="cat Start.md")
    a2 = h.admission_ok()
    by2 = members_of(a2)
    assert set(by2) == {("Start.md",)}
    assert by2[("Start.md",)].key_record.aggregate_source_digest == EMPTY_SOURCE_SHA256
    assert by2[("Start.md",)].witnesses[0].occurrence_id == start2
    assert witness_ids(by2[("Start.md",)]) == [start2]
    assert a2.entry_source_bytes == len(b"Read `Start.md` first.")
    assert a2.emitted_admission_reasons == 1  # unadmitted current proofs

    # The EXACT original Start-v1 request replays as a pure no-op and
    # restores nothing: the derivation is byte-for-byte identical.
    h.replay(read_request(endpoint, "c-start1", "See `B.md`.", cmd="cat Start.md"))
    a2b = h.admission_ok()
    assert a2b.model_dump() == a2.model_dump()

    # A genuinely descendant Start-v3 restores the entries using the
    # SAME retained B/C originals: original witnesses kept, sources
    # unchanged, and the Start entry retains BOTH equal-byte current
    # witnesses (no reindexing, no lexical winner).
    h.issue("c-start3", (start2, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat Start.md"}))
    occurrences_before = len(h.state.occurrences)
    start3 = h.read("c-start3", "See `B.md`.", cmd="cat Start.md")
    a3 = h.admission_ok()
    by3 = members_of(a3)
    assert set(by3) == {("Start.md",), ("B.md",), ("C.md",)}
    assert witness_ids(by3[("B.md",)]) == [b_occ]
    assert witness_ids(by3[("C.md",)]) == [c_occ]
    assert sorted(witness_ids(by3[("Start.md",)])) == sorted([start1, start3])
    assert len(h.state.occurrences) == occurrences_before + 1
    # No downstream re-acquisition: B and C entries keep the ORIGINAL
    # retained proof objects (identity) and digests.
    b_proof = next(o.proof for o in h.state.occurrences if o.occurrence_id == b_occ)
    assert by3[("B.md",)].proof is b_proof
    assert by3[("B.md",)].key_record.aggregate_source_digest == _sha("See `C.md`.")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_alternates_and_certificate_cycle(mode: AdmissionMode, endpoint: str) -> None:
    """A: Root->Start and Root->D; Start-v1 reaches A/B; the opaque
    AB group targets C; C is ACQUIRED and references B -- a REAL
    self-supporting cycle AB->C->B.  The usable certificate admits C;
    Start-v2 reaching only A drops B and the certificate (NO
    self-bootstrap: C unadmitted); the independent Root->D->B
    alternate restores the certificate (C re-admitted from its SAME
    retained original); withdrawing D (completed empty) takes it
    with the alternate while the empty D itself is admitted."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `Start.md` and `D.md` first.")
    start1 = h.read("c-start1", "Read `A.md` and `B.md`.", cmd="cat Start.md")
    h.read("c-ab", "See `C.md` here.\n", cmd="cat A.md B.md")
    c_occ = h.read("c-c", "See `B.md` back.\n", cmd="cat C.md")
    a1 = h.admission_ok()
    by1 = members_of(a1)
    assert set(by1) == {("Start.md",), ("A.md", "B.md"), ("C.md",)}
    ab1 = by1[("A.md", "B.md")]
    assert ab1.width == 2
    assert [m.value for m in ab1.member_classes] == ["eligible", "eligible"]
    assert witness_ids(by1[("C.md",)]) == [c_occ]

    # Phase 2: Start-v2 reaches only A.  B's only remaining route
    # would be the self-supporting cycle, which the fresh root
    # closure refuses: C is unadmitted (unreachable).  B loses
    # ELIGIBILITY, not currentness: the opaque AB group stays
    # CURRENT, so LEAN drops the mixed whole while GREEDY retains it
    # with its changed authority vector (a distinct canonical key).
    h.issue("c-start2", (start1, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat Start.md"}))
    h.read("c-start2", "Read `A.md`.", cmd="cat Start.md")
    a2 = h.admission_ok()
    by2 = members_of(a2)
    if mode is AdmissionMode.LEAN:
        assert set(by2) == {("Start.md",)}
    else:
        assert set(by2) == {("Start.md",), ("A.md", "B.md")}
        ab2 = by2[("A.md", "B.md")]
        assert [m.value for m in ab2.member_classes] == [
            "eligible",
            "greedy_background",
        ]
        assert ab2.content_key != ab1.content_key
    assert ("C.md",) not in by2
    assert a2.emitted_admission_reasons == 1

    # Phase 3: the independent alternate Root->D->B restores B's
    # eligibility and the certificate: both-eligible AB authority/key
    # return, and C is re-admitted from its SAME retained original.
    h.read("c-d", "See `B.md`.", cmd="cat D.md")
    a3 = h.admission_ok()
    by3 = members_of(a3)
    assert set(by3) == {("Start.md",), ("D.md",), ("A.md", "B.md"), ("C.md",)}
    ab3 = by3[("A.md", "B.md")]
    assert [m.value for m in ab3.member_classes] == ["eligible", "eligible"]
    assert ab3.content_key == ab1.content_key
    assert witness_ids(by3[("C.md",)]) == [c_occ]

    # Phase 4: withdrawing the alternate (completed empty D) removes
    # B's eligibility and C; the empty D itself is admitted; greedy
    # returns to the mixed AB authority vector (lean drops it again).
    d_occ = h.state.occurrences[-1].occurrence_id
    h.issue("c-d2", (d_occ, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat D.md"}))
    h.read("c-d2", "", cmd="cat D.md")
    a4 = h.admission_ok()
    by4 = members_of(a4)
    assert by4[("D.md",)].key_record.aggregate_source_digest == EMPTY_SOURCE_SHA256
    if mode is AdmissionMode.LEAN:
        assert set(by4) == {("Start.md",), ("D.md",)}
    else:
        assert set(by4) == {("Start.md",), ("D.md",), ("A.md", "B.md")}
        ab4 = by4[("A.md", "B.md")]
        assert [m.value for m in ab4.member_classes] == [
            "eligible",
            "greedy_background",
        ]
        assert ab4.content_key == by2[("A.md", "B.md")].content_key
    assert ("C.md",) not in by4
    assert a4.emitted_admission_reasons == 1


# ---------------------------------------------------------------------------
# B: partitioned A|B independence, opaque indivisibility, variants
# ---------------------------------------------------------------------------


def _partition_fixture(h: Adm, seg_a: str, seg_b: str) -> str:
    """One partitioned proven A|B read on h.endpoint with EXACT
    earned occurrence/proof preconditions (the retained source
    excludes the marker bytes)."""
    before = len(h.state.occurrences)
    h.observe(
        read_request(
            h.endpoint,
            "c-p1",
            seg_a + "MARK\n" + seg_b,
            cmd="cat A.md && echo 'MARK' && cat B.md",
        ),
        note="read:c-p1",
    )
    occurrences = h.state.occurrences
    assert len(occurrences) == before + 1, "exactly one new occurrence"
    occurrence = occurrences[-1]
    assert occurrence.call_id == "c-p1"
    assert occurrence.endpoint == h.endpoint
    assert occurrence.tool_name == "exec_command"
    p1 = occurrence.occurrence_id
    proof = occurrence.proof
    assert proof.endpoint == h.endpoint
    assert proof.source_text == seg_a + seg_b
    assert proof.source_digest == _sha(seg_a + seg_b)
    assert proof.source_byte_length == len((seg_a + seg_b).encode("utf-8"))
    segments = proof.segments
    assert len(segments) == 2
    assert segments[0].member_positions == (0,)
    assert segments[0].member_digest == _sha(seg_a)
    assert segments[1].member_positions == (1,)
    assert segments[1].member_digest == _sha(seg_b)
    return p1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_partitioned_changed_a(mode: AdmissionMode, endpoint: str) -> None:
    """B: all-current partitioned A|B admits the complete whole
    bundle in BOTH modes; a changed descendant A then leaves, in
    LEAN, the independently current B SEGMENT of the SAME old proof
    (original witness, no splice) plus the new A singleton, while
    GREEDY gains NO isolated-region rule (new A singleton only)."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md` first.")
    seg_a, seg_b = "From A see `C.md`.\n", "From B see `D.md`.\n"
    _partition_fixture(h, seg_a, seg_b)
    whole = h.admission_ok()
    byw = members_of(whole)
    assert set(byw) == {
        (
            "A.md",
            "B.md",
        )
    }
    entry = byw[("A.md", "B.md")]
    assert entry.width == 2
    assert entry.admitted_segments == (0, 1)
    assert entry.key_record.aggregate_source_digest == _sha(seg_a + seg_b)

    p1 = h.state.occurrences[-1].occurrence_id
    h.issue("c-a2", (p1, CAUSAL_ROOT_FACT))
    a2 = h.read("c-a2", "A changed.\n")
    after = h.admission_ok()
    bya = members_of(after)
    if mode is AdmissionMode.LEAN:
        assert set(bya) == {("A.md",), ("B.md",)}
        assert witness_ids(bya[("A.md",)]) == [a2]
        b_entry = bya[("B.md",)]
        assert witness_ids(b_entry) == [p1]
        assert b_entry.admitted_segments == (1,)
        assert b_entry.key_record.aggregate_source_digest == _sha(seg_b)
        # The surviving B derivation keeps the ORIGINAL retained
        # proof by identity (no re-materialized proof).
        p1_proof = next(o.proof for o in h.state.occurrences if o.occurrence_id == p1)
        assert b_entry.proof is p1_proof
    else:
        assert set(bya) == {("A.md",)}
        assert witness_ids(bya[("A.md",)]) == [a2]
    assert ("A.md", "B.md") not in bya  # the old whole is dead in both modes


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_opaque_ab_indivisible(mode: AdmissionMode, endpoint: str) -> None:
    """B: an opaque AB (unissued, both members current) admits the
    WHOLE bundle in both modes; a changed descendant A stales the
    group -- it stays INDIVISIBLE: only the new A singleton is
    admitted, never a B-only splice, in either mode."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md` first.")
    a1, b1 = "Alpha bytes.\n", "Beta bytes.\n"
    before = len(h.state.occurrences)
    h.observe(read_request(h.endpoint, "c-ab", a1 + b1, cmd="cat A.md B.md"), note="ab")
    occurrences = h.state.occurrences
    assert len(occurrences) == before + 1, "exactly one new occurrence"
    occurrence = occurrences[-1]
    assert occurrence.call_id == "c-ab"
    assert occurrence.endpoint == h.endpoint
    proof = occurrence.proof
    assert proof.endpoint == h.endpoint
    assert proof.source_text == a1 + b1
    assert proof.segments[0].member_digest is None  # opaque: unknown attribution
    ab = h.state.occurrences[-1].occurrence_id
    whole = h.admission_ok()
    byw = members_of(whole)
    assert set(byw) == {("A.md", "B.md")}
    assert byw[("A.md", "B.md")].width == 2
    assert byw[("A.md", "B.md")].admitted_segments == (0,)

    h.issue("c-a2", (ab, CAUSAL_ROOT_FACT))
    a2 = h.read("c-a2", "Alpha v2.\n")
    after = h.admission_ok()
    bya = members_of(after)
    assert set(bya) == {("A.md",)}
    assert witness_ids(bya[("A.md",)]) == [a2]
    assert bya[("A.md",)].key_record.aggregate_source_digest == _sha("Alpha v2.\n")
    assert a2 in [w.occurrence_id for w in bya[("A.md",)].witnesses]
    assert ("B.md",) not in bya  # no splice of the old opaque group
    assert ("A.md", "B.md") not in bya
    assert after.emitted_admission_reasons == 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_mixed_background_and_conflict(mode: AdmissionMode, endpoint: str) -> None:
    """B: mixed eligible/background (root references A only): LEAN
    admits no whole and no background row; GREEDY admits the whole
    with its background authority vector.  Two differing current
    proven singletons for the same path block it in both modes."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` before changing code.")
    h.read("c-ab", "AA part.\nBB part.\n", cmd="cat A.md B.md")
    a1 = h.admission_ok()
    by1 = members_of(a1)
    if mode is AdmissionMode.LEAN:
        assert set(by1) == set()
    else:
        assert set(by1) == {("A.md", "B.md")}
        entry = by1[("A.md", "B.md")]
        assert [m.value for m in entry.member_classes] == ["eligible", "greedy_background"]
        # the background path is indexed with the same key
        assert "B.md" in [row.path for row in a1.path_associations]

    # Two differing current proven singletons for A: blocked in both.
    h2 = Adm(mode, endpoint)
    h2.boot_root("Read `A.md` before changing code.")
    h2.read("c-1", "")
    h2.read("c-2", "U\u00e9nicode \u00f6 body.\n")
    a2 = h2.admission_ok()
    assert members_of(a2) == {}
    assert a2.emitted_admission_reasons == 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_content_variants(mode: AdmissionMode, endpoint: str) -> None:
    """B: exact retained content variants -- the EMPTY singleton,
    Unicode and CRLF bytes are retained verbatim (digests/bytes
    exact), repeated operands stay ordered with distinct-path
    width 1, and a whole bundle with repeated operands admits once."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` before changing code.")
    h.read("c-e", "")
    a1 = h.admission_ok()
    by1 = members_of(a1)
    assert set(by1) == {("A.md",)}
    assert by1[("A.md",)].key_record.aggregate_source_digest == EMPTY_SOURCE_SHA256
    assert a1.entry_source_bytes == len(b"Read `A.md` before changing code.")

    h2 = Adm(mode, endpoint)
    h2.boot_root("Read `A.md` before changing code.")
    h2.read("c-u", "U\u00e9nicode \u00f6 body.\n")
    a2 = h2.admission_ok()
    by2 = members_of(a2)
    assert by2[("A.md",)].key_record.aggregate_source_digest == _sha("U\u00e9nicode \u00f6 body.\n")

    h3 = Adm(mode, endpoint)
    h3.boot_root("Read `A.md` before changing code.")
    h3.read("c-crlf", "Line one.\r\nLine two.\r\n")
    a3 = h3.admission_ok()
    by3 = members_of(a3)
    assert by3[("A.md",)].key_record.aggregate_source_digest == _sha("Line one.\r\nLine two.\r\n")
    assert h3.state.occurrences[-1].proof.source_byte_length == 22

    h4 = Adm(mode, endpoint)
    h4.boot_root("Read `A.md` before changing code.")
    body = "Body one.\nMARK\nBody one.\n"
    before = len(h4.state.occurrences)
    h4.observe(
        read_request(
            h4.endpoint,
            "c-rr",
            body,
            cmd="cat A.md && echo 'MARK' && cat A.md",
        ),
        note="rr",
    )
    occurrences = h4.state.occurrences
    assert len(occurrences) == before + 1, "exactly one new occurrence"
    occurrence = occurrences[-1]
    assert occurrence.call_id == "c-rr"
    assert occurrence.endpoint == h4.endpoint
    proof = occurrence.proof
    assert proof.endpoint == h4.endpoint
    assert proof.source_text == "Body one.\nBody one.\n"
    assert tuple(m.normalized for m in proof.requested_members) == ("A.md", "A.md")
    a4 = h4.admission_ok()
    by4 = members_of(a4)
    assert set(by4) == {("A.md", "A.md")}
    assert by4[("A.md", "A.md")].width == 1  # distinct paths determine width
    assert by4[("A.md", "A.md")].admitted_segments == (0, 1)
    assert len(by4[("A.md", "A.md")].witnesses) == 1


# ---------------------------------------------------------------------------
# C: equal witnesses, reversed equal-aggregate ambiguity, child laws,
#    equal-looking stale and replay no-restore
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_witnesses_and_reversal(mode: AdmissionMode, endpoint: str) -> None:
    """C: equal incomparable witnesses are ALL retained on ONE interned
    entry (the FIRST compatible proof is retained by identity -- never
    a newest-only winner); unissued reversed equal-aggregate AB/BA is
    ambiguous and supplies nothing; a genuine child of ALL owner
    occurrences resolves to the new reversed whole; a child of only
    ONE of two concurrent DIFFERING reversed groups cannot resolve
    the conflict."""
    # C1: two independent same-content reads from the root.
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    o1 = h.read("c-1", "A body one.\n")
    o2 = h.read("c-2", "A body one.\n")
    a = h.admission_ok()
    by = members_of(a)
    assert set(by) == {("A.md",)}
    entry = by[("A.md",)]
    # Both retained, in coordinate order (occurrence_id ordering).
    assert witness_ids(entry) == sorted([o1, o2])
    # The FIRST compatible proof is retained by identity (no
    # newest-only relabeling of the origin).
    first_proof = next(o.proof for o in h.state.occurrences if o.occurrence_id == o1)
    assert entry.proof is first_proof
    assert a.emitted_admission_reasons == 0

    # C2: unissued reversed equal-aggregate AB/BA -- ambiguous, nothing.
    h2 = Adm(mode, endpoint)
    h2.boot_root("Read `A.md` and `B.md` first.")
    x = "Same file bytes.\n"
    h2.read("c-ab", x + x, cmd="cat A.md B.md")
    h2.read("c-ba", x + x, cmd="cat B.md A.md")
    a2 = h2.admission_ok()
    assert members_of(a2) == {}
    assert a2.emitted_admission_reasons == 1
    assert [row.path for row in a2.path_associations] == ["AGENTS.md"]

    # C3: child of ALL owner occurrences resolves to the new reversed
    # whole (the old group stales conservatively; reasons account for
    # the withdrawn current proofs).
    h3 = Adm(mode, endpoint)
    h3.boot_root("Read `A.md` and `B.md` first.")
    h3.read("c-ab", x + x, cmd="cat A.md B.md")
    p1 = h3.state.occurrences[-1].occurrence_id
    before = h3.admission_ok()
    assert set(members_of(before)) == {("A.md", "B.md")}
    h3.issue("c-ba", (p1, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat B.md A.md"}))
    h3.read("c-ba", x + x, cmd="cat B.md A.md")
    after = h3.admission_ok()
    by3 = members_of(after)
    assert set(by3) == {("B.md", "A.md")}
    assert witness_ids(by3[("B.md", "A.md")]) == [h3.state.occurrences[-1].occurrence_id]
    assert by3[("B.md", "A.md")].key_record.aggregate_source_digest == _sha(x + x)
    assert after.emitted_admission_reasons == 1

    # C5: two concurrent DIFFERING reversed groups conflict; a child of
    # only ONE cannot resolve the concurrent conflict.
    h5 = Adm(mode, endpoint)
    h5.boot_root("Read `A.md` and `B.md` first.")
    h5.read("c-ab", x + x, cmd="cat A.md B.md")
    o1b = h5.state.occurrences[-1].occurrence_id
    y = "Different bytes here.\n"
    h5.read("c-ba", y + y, cmd="cat B.md A.md")
    conflict = h5.admission_ok()
    assert members_of(conflict) == {}
    assert conflict.emitted_admission_reasons == 1
    h5.issue("c-ba2", (o1b, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat B.md A.md"}))
    h5.read("c-ba2", x + x, cmd="cat B.md A.md")
    still = h5.admission_ok()
    assert members_of(still) == {}
    assert still.emitted_admission_reasons == 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_equal_looking_stale_and_replay(mode: AdmissionMode, endpoint: str) -> None:
    """C: an opaque AB group conservatively stales after a descendant
    singleton A whose bytes EQUAL the old opaque aggregate (even
    equal-looking); the EXACT old request replay is a no-op that
    restores nothing; a GENUINE descendant new AB issued from the
    current A restores the whole, keeping BOTH same-byte compatible
    witnesses (the old group and the new one) with the OLDER
    compatible proof retained by identity."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md` first.")
    a1, b1 = "Alpha bytes.\n", "Beta bytes.\n"
    h.read("c-ab", a1 + b1, cmd="cat A.md B.md")
    ab = h.state.occurrences[-1].occurrence_id
    whole = h.admission_ok()
    assert set(members_of(whole)) == {("A.md", "B.md")}
    h.issue("c-a2", (ab, CAUSAL_ROOT_FACT))
    a2 = h.read("c-a2", a1 + b1)  # new A bytes EQUAL the old aggregate
    after = h.admission_ok()
    by = members_of(after)
    assert set(by) == {("A.md",)}
    assert witness_ids(by[("A.md",)]) == [a2]
    assert by[("A.md",)].key_record.aggregate_source_digest == _sha(a1 + b1)
    assert ("B.md",) not in by and ("A.md", "B.md") not in by
    assert after.emitted_admission_reasons == 1
    # The EXACT old AB request replays as a pure no-op: nothing
    # restores (the old group stays staled, not merely unadmitted).
    h.replay(read_request(endpoint, "c-ab", a1 + b1, cmd="cat A.md B.md"))
    again = h.admission_ok()
    assert again.model_dump() == after.model_dump()

    # A GENUINE descendant new AB (issued from the current A)
    # restores the whole: the old same-byte AB group remains a
    # current COMPATIBLE witness alongside the new one (a same-byte
    # ancestor is not a proven change), and the OLDER compatible
    # proof is retained by identity (never a newest-only winner).
    h.issue("c-ab2", (a2, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat A.md B.md"}))
    ab2 = h.read("c-ab2", a1 + b1, cmd="cat A.md B.md")
    restored = h.admission_ok()
    by_r = members_of(restored)
    assert set(by_r) == {("A.md", "B.md")}
    entry_r = by_r[("A.md", "B.md")]
    wids_r = [w.occurrence_id for w in entry_r.witnesses]
    assert set(wids_r) == {ab, ab2}
    assert wids_r == sorted(wids_r)
    older_ab = next(o for o in h.state.occurrences if o.occurrence_id == ab)
    assert entry_r.proof is older_ab.proof
    assert entry_r.key_record.aggregate_source_digest == _sha(a1 + b1)
    assert restored.emitted_admission_reasons == 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_two_frontier_child_resolution(mode: AdmissionMode, endpoint: str) -> None:
    """C: TWO concurrent equal-aggregate reversed groups (AB and BA)
    from the same root are ambiguous and supply nothing; a changed
    child of ONLY ONE of them cannot resolve the concurrent conflict
    (the other group remains current); a genuine child of BOTH
    current groups -- the ACTUAL two-frontier resolution -- restores
    ONE whole with BOTH same-byte compatible witnesses retained
    (the OLDER compatible proof is retained by identity, never a
    newest-only winner)."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md` first.")
    x = "Same file bytes.\n"
    y = "Different bytes here.\n"
    o_ab = h.read("c-ab", x + x, cmd="cat A.md B.md")
    o_ba = h.read("c-ba", x + x, cmd="cat B.md A.md")
    amb = h.admission_ok()
    assert members_of(amb) == {}
    assert amb.emitted_admission_reasons == 1
    assert [row.path for row in amb.path_associations] == ["AGENTS.md"]

    # A changed child of ONE current group only: the concurrent
    # conflict of the other group remains unresolved.
    h.issue("c-o1", (o_ab, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat A.md B.md"}))
    o1 = h.read("c-o1", y + y, cmd="cat A.md B.md")
    one = h.admission_ok()
    assert members_of(one) == {}
    assert one.emitted_admission_reasons == 1

    # The genuine child of BOTH current groups resolves the
    # ambiguity to the new whole.
    h.issue("c-all", (o1, o_ba, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat B.md A.md"}))
    o_all = h.read("c-all", x + x, cmd="cat B.md A.md")
    after = h.admission_ok()
    by = members_of(after)
    assert set(by) == {("B.md", "A.md")}
    entry = by[("B.md", "A.md")]
    wids = [w.occurrence_id for w in entry.witnesses]
    # The same-byte older group stays a current COMPATIBLE witness
    # alongside the new whole (coordinate-sorted, distinct IDs).
    assert set(wids) == {o_ba, o_all}
    assert wids == sorted(wids)
    assert entry.key_record.aggregate_source_digest == _sha(x + x)
    older = next(o for o in h.state.occurrences if o.occurrence_id == o_ba)
    assert entry.proof is older.proof
    assert after.emitted_admission_reasons == 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_late_result_and_shifted_replay(mode: AdmissionMode, endpoint: str) -> None:
    """C: a delayed UNEQUAL old result of an issued call from the
    same completed frontier is a genuine retained occurrence, but
    INCOMPARABLE with the already-completed newer A -- a content
    conflict with BOTH unusable while the unrelated current B stays
    admitted (not whole-state-empty); a genuine descendant of BOTH
    conflicted reads (the actual merge frontier) resolves A to the
    new read; the exact SHIFTED replay (an unrelated user item
    prepended) is a pure no-op that reverts nothing."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md` first.")
    h.issue("c-old", (CAUSAL_ROOT_FACT,))
    h.issue("c-mid", (CAUSAL_ROOT_FACT,), json.dumps({"cmd": "cat B.md"}))
    mid = h.read("c-mid", "middle body.\n", cmd="cat B.md")
    h.issue("c-new", (mid, CAUSAL_ROOT_FACT))
    new_a = h.read("c-new", "new A body.\n")
    a1 = h.admission_ok()
    assert set(members_of(a1)) == {("A.md",), ("B.md",)}
    assert a1.emitted_admission_reasons == 0

    # The late, unequal old result: retained, but a concurrent
    # conflict -- A unadmitted, B (unrelated and current) stays.
    req_old = read_request(endpoint, "c-old", "old A body.\n")
    old_a = h.read("c-old", "old A body.\n")
    conf = h.admission_ok()
    by_c = members_of(conf)
    assert set(by_c) == {("B.md",)}
    assert by_c[("B.md",)].witnesses[0].occurrence_id == mid
    assert conf.emitted_admission_reasons == 1

    # A genuine descendant of BOTH conflicted reads resolves A.
    h.issue("c-merge", (old_a, new_a, CAUSAL_ROOT_FACT))
    merge = h.read("c-merge", "resolved body.\n")
    res = h.admission_ok()
    by_r = members_of(res)
    assert set(by_r) == {("A.md",), ("B.md",)}
    assert by_r[("A.md",)].witnesses[0].occurrence_id == merge
    assert by_r[("B.md",)].witnesses[0].occurrence_id == mid
    assert res.emitted_admission_reasons == 1

    # The exact shifted replay of the late old request: pure no-op,
    # the derivation stays byte-for-byte identical.
    field = "input" if endpoint == "responses" else "messages"
    filler = {"role": "user", "content": "synthetic unrelated preceding text"}
    shifted = GraphRequest(payload={field: [filler] + req_old.payload[field]}, endpoint=endpoint)
    h.replay(shifted)
    again = h.admission_ok()
    assert again.model_dump() == res.model_dump()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_known_equal_chain_resolution(mode: AdmissionMode, endpoint: str) -> None:
    """C: temporal preservation of TWO concurrent equal known A
    claims: the equal same-byte reads o1/o2 are retained as distinct
    witnesses under ONE key with the FIRST original proof (zero
    reasons); a changed child of ONE witness blocks A (root key
    unchanged, one candidate reason); a changed child of BOTH (the
    actual two-frontier) resolves A keeping the OLDER compatible
    changed read o3 AND the newer o4 with the FIRST compatible
    original proof p3 -- the actual E global maximal frontier is o4
    only, and the older same-content group o3 stays CURRENT_KNOWN
    compatible (never newest-only); the two REPLACED same-byte
    occurrences admit nothing in the resolved derivation (one
    retained candidate reason); the exact old replay rolls nothing
    back and retains the original proofs by identity."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md`.")
    o1 = h.read("witness-first", "Version one.")
    p1 = h.state.occurrences[-1].proof
    o2 = h.read("witness-alternate", "Version one.")
    p2 = h.state.occurrences[-1].proof
    equal = h.admission_ok()
    assert len(equal.entries) == 1
    e = equal.entries[0]
    assert {w.occurrence_id for w in e.witnesses} == {o1, o2}
    assert e.proof is p1
    assert e.key_record.member_occurrences == ("A.md",)
    assert e.proof.source_text == "Version one."
    assert p2.source_text == "Version one."
    assert e.key_record.aggregate_source_digest == _sha("Version one.")
    assert len(equal.path_associations) == 2
    assert equal.emitted_admission_reasons == 0

    # A changed child of ONE of the two equal witnesses cannot
    # resolve: A is blocked, the root key is unchanged.
    h.issue("witness-child-one", (CAUSAL_ROOT_FACT, o1))
    o3 = h.read("witness-child-one", "Version two.")
    p3 = h.state.occurrences[-1].proof
    blocked = h.admission_ok()
    assert blocked.entries == ()
    assert blocked.root_entry.content_key == equal.root_entry.content_key
    assert blocked.emitted_admission_reasons == 1
    assert blocked.admission_reasons == (CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,)

    # A genuine child of BOTH equal witnesses (the actual
    # two-frontier) resolves A.
    h.issue("witness-child-all", (CAUSAL_ROOT_FACT, o1, o2, o3))
    o4 = h.read("witness-child-all", "Version two.")
    resolved = h.admission_ok()
    assert len(resolved.entries) == 1
    fresh = resolved.entries[0]
    # The actual E frontier is o4 only, but the older same-content
    # changed read o3 stays CURRENT_KNOWN compatible: both witnesses
    # are retained with the FIRST compatible original proof.
    currentness = derive_currentness_overlay(h.state, h.ns)
    assert currentness.overlay is not None
    path = next(p for p in currentness.overlay.paths if p.path == "A.md")
    assert set(path.witnesses) == {o4}
    compatible = {
        g.occurrence_id
        for g in currentness.overlay.groups
        if g.group_status.value == "current_known"
    }
    assert compatible == {o3, o4}
    assert {w.occurrence_id for w in fresh.witnesses} == {o3, o4}
    assert fresh.proof is p3
    for gone in (o1, o2):
        assert gone not in {w.occurrence_id for w in fresh.witnesses}
    assert fresh.key_record.aggregate_source_digest == _sha("Version two.")
    assert fresh.content_key != e.content_key
    # The two REPLACED same-byte occurrences (o1/o2) admit nothing in
    # this derivation: the single fixed candidate reason is retained.
    assert resolved.emitted_admission_reasons == 1
    assert resolved.admission_reasons == (CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,)

    # The exact old replay rolls nothing back.
    prior = h.state
    h.replay(read_request(endpoint, "witness-first", "Version one."))
    assert h.state is prior
    replayed = h.admission_ok()
    assert [x.content_key for x in replayed.entries] == [fresh.content_key]
    assert len(h.state.occurrences) == 4
    assert h.state.occurrences[0].proof is p1
    assert h.state.occurrences[1].proof is p2


# ---------------------------------------------------------------------------
# D: exact canonical 018-c key equality/inequality laws
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_canonical_key_laws(mode: AdmissionMode, endpoint: str) -> None:
    """D: exact canonical key equality for changed call IDs (same
    content interns, ONE key) and for unchanged A after an unrelated
    B; exact inequality for changed source, AB/BA member order,
    A+A versus A ownership shapes, and the background->eligible
    authority-vector flip (distinct keys, actual records)."""
    # Changed call IDs: the same content under a new call ID interns
    # onto ONE entry with a distinct canonical key retained.
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    o1 = h.read("c-1", "Stable A body.\n")
    a1 = h.admission_ok()
    key1 = members_of(a1)[("A.md",)].content_key
    o2 = h.read("c-2", "Stable A body.\n")
    a2 = h.admission_ok()
    entry = members_of(a2)[("A.md",)]
    assert entry.content_key == key1
    # Both distinct occurrences retained; the witness ORDER is the
    # canonical full-coordinate order (here reducing to the sorted
    # occurrence IDs), never the acquisition order.
    assert set(witness_ids(entry)) == {o1, o2}
    assert witness_ids(entry) == sorted([o1, o2])
    assert entry.key_record.member_occurrences == ("A.md",)

    # Unrelated B: the unchanged A entry keeps its exact key record
    # and interned identity (B is not root-referenced: background in
    # greedy, unadmitted in lean -- A is untouched either way).
    h.read("c-b", "B body here.\n", cmd="cat B.md")
    a3 = h.admission_ok()
    entry3 = members_of(a3)[("A.md",)]
    assert entry3.content_key == key1
    # Same retained proof object and key record facts across
    # derivations (interning is per-derivation; the retained
    # originals are shared, never refabricated).
    assert entry3.proof is entry.proof
    assert witness_ids(entry3) == witness_ids(entry)

    # Changed source: the descendant A earns a DISTINCT key.
    h_cs = Adm(mode, endpoint)
    h_cs.boot_root("Read `A.md` first.")
    o1c = h_cs.read("c-1", "Stable A body.\n")
    key_c1 = members_of(h_cs.admission_ok())[("A.md",)].content_key
    h_cs.issue("c-a2", (o1c, CAUSAL_ROOT_FACT))
    a4 = h_cs.read("c-a2", "Changed A body.\n")
    after = h_cs.admission_ok()
    assert set(members_of(after)) == {("A.md",)}
    assert members_of(after)[("A.md",)].content_key != key_c1
    assert members_of(after)[("A.md",)].witnesses[0].occurrence_id == a4

    # AB/BA with the SAME aggregate bytes: distinct ordered member
    # occurrences give distinct canonical keys (separate scopes).
    x = "Same file bytes.\n"
    h_ab = Adm(mode, endpoint)
    h_ab.boot_root("Read `A.md` and `B.md` first.")
    h_ab.read("c-ab", x + x, cmd="cat A.md B.md")
    k_ab = members_of(h_ab.admission_ok())[("A.md", "B.md")].content_key
    h_ba = Adm(mode, endpoint)
    h_ba.boot_root("Read `A.md` and `B.md` first.")
    h_ba.read("c-ba", x + x, cmd="cat B.md A.md")
    k_ba = members_of(h_ba.admission_ok())[("B.md", "A.md")].content_key
    assert k_ab != k_ba
    # Same aggregate digest, different ownership shape.
    assert (
        members_of(h_ab.admission_ok())[("A.md", "B.md")].key_record.aggregate_source_digest
        == members_of(h_ba.admission_ok())[("B.md", "A.md")].key_record.aggregate_source_digest
        == _sha(x + x)
    )

    # A+A (ordered repeated members) versus A (singleton): distinct
    # keys even though the distinct-path width is 1 in both.
    h_rr = Adm(mode, endpoint)
    h_rr.boot_root("Read `A.md` first.")
    body = "Body one.\nMARK\nBody one.\n"
    h_rr.observe(
        read_request(
            h_rr.endpoint,
            "c-rr",
            body,
            cmd="cat A.md && echo 'MARK' && cat A.md",
        ),
        note="rr",
    )
    k_rr = members_of(h_rr.admission_ok())[("A.md", "A.md")].content_key
    # (the earlier "Stable A body." singleton key1 is a different
    # aggregate anyway; use a same-body singleton for the shape law:)
    h_s = Adm(mode, endpoint)
    h_s.boot_root("Read `A.md` first.")
    h_s.read("c-s", "Body one.\nBody one.\n")
    k_s = members_of(h_s.admission_ok())[("A.md",)].content_key
    assert k_rr != k_s

    # Background -> eligible: the authority-vector flip changes the
    # canonical key (greedy whole rows only; lean has no whole row
    # while mixed).
    # The root references A and D (so D can anchor B's independent
    # route); B itself is not root-referenced.
    h_bg = Adm(mode, endpoint)
    h_bg.boot_root("Read `A.md` and `D.md` first.")
    h_bg.read("c-ab", "AA part.\nBB part.\n", cmd="cat A.md B.md")
    if mode is AdmissionMode.GREEDY:
        k_bg = members_of(h_bg.admission_ok())[("A.md", "B.md")].content_key
        h_bg.read("c-d", "See `B.md`.", cmd="cat D.md")
        k_el = members_of(h_bg.admission_ok())[("A.md", "B.md")].content_key
        assert k_bg != k_el
        assert [
            m.value for m in members_of(h_bg.admission_ok())[("A.md", "B.md")].member_classes
        ] == ["eligible", "eligible"]
    else:
        assert members_of(h_bg.admission_ok()) == {}
        h_bg.read("c-d", "See `B.md`.", cmd="cat D.md")
        by_el = members_of(h_bg.admission_ok())
        assert set(by_el) == {("A.md", "B.md"), ("D.md",)}
        assert [m.value for m in by_el[("A.md", "B.md")].member_classes] == ["eligible", "eligible"]


#: (case label, root text, command, observed body) -- the actual
#: original-API root + read shapes for the old-C canonical equality
#: law (whole/isolated/repeated/Unicode/empty-root included).
OLD_C_CASES: tuple[tuple[str, str, str, str], ...] = (
    ("opaque-all", "Read `A.md` and `B.md`.", "cat A.md B.md", "Alpha.\nBeta.\n"),
    ("opaque-mixed", "Read `A.md`.", "cat A.md B.md", "Alpha.\nBeta.\n"),
    (
        "proven-all",
        "Read `A.md` and `B.md`.",
        "cat A.md && echo 'MARK' && cat B.md",
        "Alpha.\nMARK\nBeta.\n",
    ),
    (
        "proven-mixed",
        "Read `A.md`.",
        "cat A.md && echo 'MARK' && cat B.md",
        "Alpha.\nMARK\nBeta.\n",
    ),
    ("singleton", "Read `A.md`.", "cat A.md", "Alpha.\n"),
    ("loop-singleton", "Read `A.md`.", 'for f in A.md; do cat "$f" || exit 1; done', "srcA\n"),
    ("repeated", "Read `A.md`.", "cat A.md && echo 'MARK' && cat A.md", "Alpha.\nMARK\nAlpha.\n"),
    ("unicode-crlf", "Read `A.md`.", "cat A.md", "Alpha \u00e9\u4e2d.\r\n"),
    ("empty-root", "", "cat A.md", "Alpha.\n"),
)


@pytest.mark.parametrize("case", OLD_C_CASES, ids=[c[0] for c in OLD_C_CASES])
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_old_c_canonical_equality(
    case: tuple[str, str, str, str],
    mode: AdmissionMode,
    endpoint: str,
) -> None:
    """D: the NEW G canonical keys ARE the ACTUAL 018-c semantic
    keys: under ONE shared admission namespace, the old-C batch
    admission over the SAME actual original-API root + read requests
    and the new G derivation over the actual retained history agree
    on the exact ROOT key record, the exact file key-record mapping
    (content key to key record) and the reverse member index, and the
    G entries retain the ORIGINAL proof by identity.  A structural-
    equality-to-hit claim is never substituted for the actual old-C
    call."""
    label, root_text, cmd, body = case
    adm_ns = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-history-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
    )
    ns = make_causal_history_namespace(adm_ns, "synthetic-canonical-durable")
    requests = (
        GraphRequest(payload={"input": [root_item(root_text)]}, endpoint="responses", context=None),
        read_request(endpoint, f"c-{label}", body, cmd),
    )
    transition = observe_causal_history(requests, ns, empty_state(ns), 0)
    assert transition.outcome is CausalHistoryOutcome.ACCEPTED, (
        label,
        transition.outcome,
        transition.diagnostics,
    )
    state = transition.state
    assert len(state.occurrences) == 1
    occurrence = state.occurrences[0]
    assert occurrence.endpoint == endpoint and occurrence.proof.endpoint == endpoint
    old = observe_bundle_admission_batch(requests, adm_ns)
    assert old.outcome is AdmissionOutcome.COMPLETE, (label, old.outcome)
    new = derive_current_admission(state, ns)
    assert new.outcome is CurrentAdmissionOutcome.OK, (label, new.outcome, new.diagnostics)
    assert new.state is state and new.overlay is not None
    current = new.overlay
    assert old.root_entry is not None
    assert old.root_entry.key_record == current.root_entry.key_record, label
    old_records = {e.content_key: e.key_record for e in old.entries}
    new_records = {e.content_key: e.key_record for e in current.entries}
    assert old_records == new_records, label
    assert all(e.proof is occurrence.proof for e in current.entries), label
    old_rows = {row.path: set(row.content_keys) for row in old.path_associations}
    new_rows = {row.path: set(row.content_keys) for row in current.path_associations}
    assert old_rows == new_rows, label


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_mode_bound_key(mode: AdmissionMode, endpoint: str) -> None:
    """D: the canonical key binds the ACTUAL admission mode: the SAME
    history derived under the two modes yields distinct keys for the
    same admitted region."""

    def build(m: AdmissionMode) -> Adm:
        d = Adm(m, endpoint)
        d.boot_root("Read `A.md` first.")
        d.read("c-1", "Mode bound body.\n")
        return d

    a_lean = build(AdmissionMode.LEAN)
    a_greedy = build(AdmissionMode.GREEDY)
    k_lean = members_of(a_lean.admission_ok())[("A.md",)].content_key
    k_greedy = members_of(a_greedy.admission_ok())[("A.md",)].content_key
    assert k_lean != k_greedy


# ---------------------------------------------------------------------------
# E: root entry typed retention, empty root, refresh refusal, root-
#    bearing opaque exclusion
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_root_entry(mode: AdmissionMode, endpoint: str) -> None:
    """E: the root entry retains the ACTUAL RootAnchor typed fields
    exactly (no invented kind/status/envelope); the exact EMPTY root
    is legal; a changed-bytes root refresh stays refused by 018-d
    with the exact state while the root row is retained; a
    SAME-BYTES proven root-path read is CONSISTENT with the anchor
    (not a competing root) and admits an AGENTS.md file entry whose
    anchor row keeps its own distinct key; a partitioned
    root-compatible group admits its whole (the independently proven
    nonroot segment survives) while a root-competing read is refused
    outright; root-bearing opaque reads supply NO file entries
    (unproven root bytes) while the root row stays retained."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` before changing code.")
    a = h.admission_ok()
    root = a.root_entry
    anchor = h.state.root
    assert anchor is not None
    assert root.entry_class.value == "root_entry"
    assert root.root_text == anchor.root_text
    assert root.root_source_byte_length == anchor.source_byte_length
    assert root.root_digest == anchor.root_digest
    assert root.width == 1
    assert [m.value for m in root.member_classes] == ["eligible"]
    assert root.key_record.member_occurrences == ("AGENTS.md",)
    assert root.key_record.aggregate_source_digest == anchor.root_digest
    prov = root.root_provenance
    assert prov is not None
    assert prov.first_request_index == anchor.first_request_index
    assert prov.location == anchor.location
    assert prov.content_span == anchor.content_span
    assert prov.envelope_span == anchor.envelope_span
    assert prov.source_byte_length == anchor.source_byte_length
    assert prov.root_digest == anchor.root_digest
    assert prov.workspace == h.ns.workspace
    assert root.witnesses == ()
    root_row = next(r for r in a.path_associations if r.path == "AGENTS.md")
    assert root_row.is_root and root.content_key in root_row.content_keys

    # The exact EMPTY root is legal.
    h_e = Adm(mode, endpoint)
    h_e.boot_root("")
    a_e = h_e.admission_ok()
    assert a_e.root_entry.root_text == ""
    assert a_e.root_entry.root_source_byte_length == 0
    assert a_e.root_entry.root_digest == EMPTY_SOURCE_SHA256
    assert a_e.entry_source_bytes == 0

    # A root path REFRESH with changed bytes is a competing
    # effective root: refused by 018-d with the exact state kept;
    # the admission still retains the original root row.
    refused = observe_causal_history(
        (read_request(endpoint, "c-root", "New root.\n", cmd="cat AGENTS.md"),),
        h.ns,
        h.state,
        h.revision,
    )
    assert refused.outcome is CausalHistoryOutcome.REFUSED_ROOT_CONFLICT
    assert refused.state is h.state
    a2 = h.admission_ok()
    assert a2.root_entry.content_key == root.content_key
    assert next(r for r in a2.path_associations if r.path == "AGENTS.md").content_keys == (
        root.content_key,
    )

    # A SAME-BYTES proven root-path read is CONSISTENT with the
    # anchor (never a competing root): it is retained and admits an
    # AGENTS.md file entry whose aggregate is the anchor digest,
    # while the anchor's own key row stays distinct and unchanged.
    root_key = a2.root_entry.content_key
    h.read("c-rsame", anchor.root_text, cmd="cat AGENTS.md")
    a3 = h.admission_ok()
    by3 = members_of(a3)
    file_entry = by3[("AGENTS.md",)]
    assert a3.root_entry.content_key == root_key
    assert file_entry.key_record.member_occurrences == ("AGENTS.md",)
    assert file_entry.key_record.aggregate_source_digest == anchor.root_digest
    assert [m.value for m in file_entry.member_classes] == ["eligible"]
    assert file_entry.width == 1
    assert len(file_entry.witnesses) == 1
    assert file_entry.proof is h.state.occurrences[-1].proof
    root_row3 = next(r for r in a3.path_associations if r.path == "AGENTS.md")
    assert len(root_row3.content_keys) == 2
    assert set(root_row3.content_keys) == {root_key, file_entry.content_key}
    assert a3.emitted_admission_reasons == 0

    # A partitioned root-COMPATIBLE group admits its whole: the
    # independently proven nonroot segment survives alongside the
    # same-byte anchor segment.
    R0 = "Read `A.md` before changing code."
    h_p = Adm(mode, endpoint)
    h_p.boot_root(R0)
    before_p = len(h_p.state.occurrences)
    h_p.observe(
        read_request(
            endpoint,
            "c-rmix",
            R0 + "MARK\n" + "A body.\n",
            cmd="cat AGENTS.md && echo 'MARK' && cat A.md",
        ),
        note="read:c-rmix",
    )
    occ_mix = h_p.state.occurrences[-1]
    assert len(h_p.state.occurrences) == before_p + 1
    pmix = occ_mix.proof
    assert pmix.source_text == R0 + "A body.\n"
    assert [s.byte_length for s in pmix.segments] == [
        len(R0.encode()),
        len(b"A body.\n"),
    ]
    a_p = h_p.admission_ok()
    whole = members_of(a_p)[("AGENTS.md", "A.md")]
    assert [m.value for m in whole.member_classes] == ["eligible", "eligible"]
    assert whole.width == 2
    assert whole.key_record.aggregate_source_digest == _sha(R0 + "A body.\n")
    root_row_p = next(r for r in a_p.path_associations if r.path == "AGENTS.md")
    assert len(root_row_p.content_keys) == 2
    assert set(root_row_p.content_keys) == {
        whole.content_key,
        a_p.root_entry.content_key,
    }
    assert a_p.emitted_admission_reasons == 0

    # A partitioned root-COMPETING read (DIFFERENT root bytes) is a
    # competing effective root: refused outright, exact state kept.
    h_c = Adm(mode, endpoint)
    h_c.boot_root(R0)
    refused_c = observe_causal_history(
        (
            read_request(
                endpoint,
                "c-rbad",
                "X" * len(R0) + "MARK\n" + "A body.\n",
                cmd="cat AGENTS.md && echo 'MARK' && cat A.md",
            ),
        ),
        h_c.ns,
        h_c.state,
        h_c.revision,
    )
    assert refused_c.outcome is CausalHistoryOutcome.REFUSED_ROOT_CONFLICT
    assert refused_c.state is h_c.state

    # A root-bearing OPAQUE read supplies NO file entries (the root
    # bytes cannot be proven compatible with the RootAnchor) while
    # the root row stays retained.
    h_o = Adm(mode, endpoint)
    h_o.boot_root("Read `A.md` before changing code.")
    h_o.read("c-ro", "AGENTS bytes.\nA bytes.\n", cmd="cat AGENTS.md A.md")
    a_o = h_o.admission_ok()
    assert members_of(a_o) == {}
    assert a_o.emitted_admission_reasons == 1
    assert next(r for r in a_o.path_associations if r.path == "AGENTS.md").is_root


def _opaque_root_plus_b_fixture(mode: AdmissionMode, endpoint: str) -> Adm:
    """Root references A/B; the partitioned read carries an OPAQUE
    root+A group (boundaryless, unproven) followed by an
    independently proven B segment (the earned marker-excluded
    source; raw observe plus explicit segment preconditions)."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md`.")
    before = len(h.state.occurrences)
    h.observe(
        read_request(
            endpoint,
            "c-ro",
            "AGENTS plus A bytes.\n" + "MARK\n" + "B bytes.\n",
            cmd="cat AGENTS.md A.md && echo 'MARK' && cat B.md",
        ),
        note="read:c-ro",
    )
    assert len(h.state.occurrences) == before + 1
    occ = h.state.occurrences[-1]
    proof = occ.proof
    assert proof.source_text == "AGENTS plus A bytes.\nB bytes.\n"
    assert [s.byte_length for s in proof.segments] == [21, 9]
    assert [s.member_positions for s in proof.segments] == [(0, 1), (2,)]
    assert proof.segments[0].member_digest is None  # boundaryless opaque
    assert proof.segments[1].member_digest is not None  # proven B
    return h


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_opaque_root_plus_independent_segment(mode: AdmissionMode, endpoint: str) -> None:
    """E: a root-bearing OPAQUE group is indivisible and supplies no
    root text (unknown root bytes), while the independently PROVEN
    nonroot B segment of the SAME proof stays current: LEAN retains
    B only (zero reasons, root bytes plus B once), GREEDY gains no
    isolation rule and admits nothing from the proof (ONE
    candidate_unproven reason, root bytes only) -- the ROOT_ENTRY key
    stays unchanged in both, and the retained-root provenance is the
    exact typed RootAnchor field set (no invented kind/status/
    envelope)."""
    h = _opaque_root_plus_b_fixture(mode, endpoint)
    base = h.admission_ok()
    root_key = base.root_entry.content_key
    anchor = h.state.root
    assert anchor is not None
    a = h.admission_ok()
    by = members_of(a)
    prov = a.root_entry.root_provenance
    assert isinstance(prov, RetainedRootProvenance)
    assert set(RetainedRootProvenance.model_fields) == {
        "first_request_index",
        "location",
        "content_span",
        "envelope_span",
        "source_byte_length",
        "root_digest",
        "workspace",
    }
    assert prov.first_request_index == anchor.first_request_index
    assert prov.location == anchor.location
    assert prov.content_span == anchor.content_span
    assert prov.envelope_span == anchor.envelope_span
    assert prov.source_byte_length == anchor.source_byte_length
    assert prov.root_digest == anchor.root_digest
    assert prov.workspace == h.ns.workspace
    if mode is AdmissionMode.LEAN:
        assert set(by) == {("B.md",)}
        b = by[("B.md",)]
        assert len(b.witnesses) == 1
        assert b.witnesses[0].occurrence_id == h.state.occurrences[-1].occurrence_id
        assert b.witnesses[0].segment_indices == (1,)
        assert [m.value for m in b.member_classes] == ["eligible"]
        assert b.proof is h.state.occurrences[-1].proof
        assert a.emitted_admission_reasons == 0
        assert a.entry_source_bytes == len(b"Read `A.md` and `B.md`.") + 9
        assert a.entries_retained == 2
        assert {row.path: len(row.content_keys) for row in a.path_associations} == {
            "AGENTS.md": 1,
            "B.md": 1,
        }
    else:
        assert by == {}
        assert a.emitted_admission_reasons == 1
        assert a.admission_reasons == (CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,)
        assert a.entry_source_bytes == len(b"Read `A.md` and `B.md`.")
        assert a.entries_retained == 1
        assert {row.path: len(row.content_keys) for row in a.path_associations} == {
            "AGENTS.md": 1,
        }
    assert a.root_entry.content_key == root_key


# ---------------------------------------------------------------------------
# F: complete reverse index, width, exact scope/revision identity
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_reverse_index(mode: AdmissionMode, endpoint: str) -> None:
    """F: the reverse index is complete over overlaps (one member path
    mapped to ALL admitted keys), entries are sorted by distinct
    content key, and the derived admission binds the EXACT input
    scope/revision with the unchanged actual state and carried
    graph."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md`, `B.md` and `C.md` before changing code.")
    seg_a, seg_b, seg_c = "A part one.\n", "B part.\n", "C part.\n"
    p1 = _partition_fixture(h, seg_a, seg_b)
    h.issue(
        "c-p2", (p1, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat A.md && echo 'MARK' && cat C.md"})
    )
    h.observe(
        read_request(
            h.endpoint,
            "c-p2",
            seg_a + "MARK\n" + seg_c,
            cmd="cat A.md && echo 'MARK' && cat C.md",
        ),
        note="read:c-p2",
    )
    a = h.admission_ok()
    by = members_of(a)
    assert set(by) == {("A.md", "B.md"), ("A.md", "C.md")}
    rows = {row.path: row for row in a.path_associations}
    assert set(rows) == {"AGENTS.md", "A.md", "B.md", "C.md"}
    assert len(rows["A.md"].content_keys) == 2  # the overlap
    assert rows["A.md"].content_keys == tuple(
        sorted({by[("A.md", "B.md")].content_key, by[("A.md", "C.md")].content_key})
    )
    assert rows["B.md"].content_keys == (by[("A.md", "B.md")].content_key,)
    assert rows["C.md"].content_keys == (by[("A.md", "C.md")].content_key,)
    assert rows["AGENTS.md"].is_root
    assert not rows["A.md"].is_root
    # Entries sorted by distinct content key; root never repeated.
    keys = [e.content_key for e in a.entries]
    assert keys == sorted(keys)
    assert a.root_entry.content_key not in keys
    # Exact scope/revision identity over the unchanged actual state.
    assert a.history_key == h.ns.history_key
    assert a.revision == h.state.revision
    assert a.workspace == h.ns.workspace
    assert a.graph.history_key == a.history_key
    assert a.graph.revision == a.revision
    assert a.graph.root_digest == a.root_digest
    assert a.graph.scope_key == a.graph_scope_key


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_isolated_b_different_proof_coordinates(mode: AdmissionMode, endpoint: str) -> None:
    """F: the current proven partitioned A|B (B is segment 1) and the
    later SAME-BYTES standalone B (segment 0) intern ONE canonical B
    key retaining BOTH original witnesses at their OWN proof/group
    coordinates (1,) and (0,) -- canonical coordinate sort, not
    acquisition order -- with the FIRST compatible original proof
    retained and the copy budget counting the ONE key once; GREEDY
    keeps the whole mixed AB as an INDEPENDENT background entry
    alongside the standalone B (whose proof is the standalone read).
    The root reaches only B; A never earns a row in LEAN."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `B.md`.")
    seg_a, seg_b = "A part here.\n", "B part here.\n"
    before = len(h.state.occurrences)
    h.observe(
        read_request(
            endpoint,
            "c-p1",
            seg_a + "MARK\n" + seg_b,
            cmd="cat A.md && echo 'MARK' && cat B.md",
        ),
        note="read:c-p1",
    )
    assert len(h.state.occurrences) == before + 1
    occ_p1 = h.state.occurrences[-1]
    p1 = occ_p1.proof
    assert p1.source_text == seg_a + seg_b
    assert [s.byte_length for s in p1.segments] == [13, 13]
    assert [s.member_positions for s in p1.segments] == [(0,), (1,)]
    assert all(s.member_digest is not None for s in p1.segments)
    h.read("c-b2", seg_b, cmd="cat B.md")
    occ_p2 = h.state.occurrences[-1]
    p2 = occ_p2.proof
    assert p2.source_text == seg_b
    a = h.admission_ok()
    by = members_of(a)
    assert a.emitted_admission_reasons == 0
    assert a.admission_reasons == ()
    if mode is AdmissionMode.LEAN:
        assert set(by) == {("B.md",)}
        b = by[("B.md",)]
        assert len(b.witnesses) == 2
        seg_by_occ = {w.occurrence_id: w.segment_indices for w in b.witnesses}
        assert seg_by_occ == {
            occ_p2.occurrence_id: (0,),
            occ_p1.occurrence_id: (1,),
        }
        keys = [_witness_key(w) for w in b.witnesses]
        assert keys == sorted(keys)
        assert b.proof is p1  # FIRST compatible original proof
        assert [m.value for m in b.member_classes] == ["eligible"]
        # the copy budget counts the ONE distinct key once
        assert a.entry_source_bytes == len(b"Read `B.md`.") + 13
        assert a.entries_retained == 2
        assert {row.path: len(row.content_keys) for row in a.path_associations} == {
            "AGENTS.md": 1,
            "B.md": 1,
        }
    else:
        assert set(by) == {("A.md", "B.md"), ("B.md",)}
        whole = by[("A.md", "B.md")]
        assert len(whole.witnesses) == 1
        assert whole.witnesses[0].occurrence_id == occ_p1.occurrence_id
        assert whole.witnesses[0].segment_indices == (0, 1)
        assert [m.value for m in whole.member_classes] == [
            "greedy_background",
            "eligible",
        ]
        assert whole.proof is p1
        standalone = by[("B.md",)]
        assert len(standalone.witnesses) == 1
        assert standalone.witnesses[0].occurrence_id == occ_p2.occurrence_id
        assert standalone.witnesses[0].segment_indices == (0,)
        assert standalone.proof is p2
        # root + whole (A|B) + standalone B, once per distinct key
        assert a.entry_source_bytes == len(b"Read `B.md`.") + 26 + 13
        assert a.entries_retained == 3
        assert {row.path: len(row.content_keys) for row in a.path_associations} == {
            "A.md": 1,
            "AGENTS.md": 1,
            "B.md": 2,
        }


# ---------------------------------------------------------------------------
# G: resource domains, sentinels, typed refusals, hygiene, model law
# ---------------------------------------------------------------------------


class _RegionSentinel(str):
    """Counting stand-in for a retained source region: records every
    slice RANGE, single-index access and encode over the actual
    string, proving which regions the derivation touched (stale
    regions must be zero)."""

    ranges: list[tuple[int, int]] = []
    indices: list[int] = []
    encodes = 0

    def __getitem__(self, index: int | slice[Any, Any, Any]) -> str:  # type: ignore[override]
        if isinstance(index, slice):
            start, stop, _step = index.indices(len(self))
            _RegionSentinel.ranges.append((start, stop))
        else:
            _RegionSentinel.indices.append(index)
        return str.__getitem__(self, index)

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        _RegionSentinel.encodes += 1
        return str.encode(self, encoding, errors)

    @classmethod
    def reset(cls) -> None:
        cls.ranges = []
        cls.indices = []
        cls.encodes = 0


def _k1_fixture(mode: AdmissionMode, endpoint: str) -> Adm:
    """The shared resource fixture: partitioned A|B with a changed
    descendant A (lean retains the B segment, greedy only the new A).
    The partitioned read uses the raw observe with the
    marker-excluded earned preconditions (``Adm.read`` whole-body
    equality does not hold for partitioned commands)."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md` first.")
    p1 = _partition_fixture(h, "From A see `C.md`.\n", "From B see `D.md`.\n")
    h.issue("c-a2", (p1, CAUSAL_ROOT_FACT))
    h.read("c-a2", "A changed.\n")
    return h


def _rekeyed(
    mode: AdmissionMode,
    state: CausalHistoryState,
    bounds: BundleAdmissionBounds | None = None,
    graph_bounds: GraphBounds | None = None,
) -> tuple[CausalHistoryNamespace, CausalHistoryState]:
    """A coherent namespace under the SAME identity/workspace/mode
    with the named bound sets replaced, and the state rekeyed to its
    ACTUAL history key (a stale key would be foreign, not a cap)."""
    ns = make_ns_adm(mode, bounds, graph_bounds)
    return ns, state.model_copy(update={"history_key": ns.history_key})


def _scope_key_of(kw: dict[str, Any]) -> str:
    """Recompute the G scope key from a full field dict (the kernel
    argument order): coherent bound changes need the recomputed key,
    never a caller tag."""
    return current_admission_scope_key(
        kw["history_key"],
        kw["workspace"],
        kw["root_digest"],
        kw["contract_version"],
        kw["policy_version"],
        kw["admission_version"],
        kw["observation_version"],
        kw["graph_version"],
        kw["reference_version"],
        kw["proof_version"],
        kw["history_version"],
        kw["arguments_version"],
        kw["currentness_contract_version"],
        kw["currentness_policy_version"],
        kw["currentness_recipe_version"],
        kw["graph_contract_version"],
        kw["graph_policy_version"],
        kw["currentness_scope_key"],
        kw["graph_scope_key"],
        kw["admission_namespace_key"],
        kw["admission_scoped_key"],
        kw["bounds"],
        kw["currentness_bounds"],
        kw["graph_bounds"],
        kw["admission_bounds"],
        kw["proof_bounds"],
        kw["inherited_graph_bounds"],
        kw["observation_bounds"],
    )


def _rekeyed_ns_bounds(
    mode: AdmissionMode,
    state: CausalHistoryState,
    **bounds_updates: int,
) -> tuple[CausalHistoryNamespace, CausalHistoryState]:
    """A coherent namespace with ONE inherited admission bound field
    replaced (the key chain recomputed from the actual fields)."""
    return _rekeyed(mode, state, bounds=BundleAdmissionBounds(**bounds_updates))


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_total_work_bound(mode: AdmissionMode, endpoint: str) -> None:
    """G: the ONE shared outer total-work ceiling is honored at the
    EXACT at-limit threshold (smallest OK cap) and refuses with the
    shared fixed name plus the exact input state one unit below --
    the cap is targeted first, no earlier unrelated refusal."""
    h = _k1_fixture(mode, endpoint)
    state = h.state
    probe = lambda cap: (  # noqa: E731
        derive_current_admission(
            state, h.ns, bounds=CurrentAdmissionBounds(max_total_work_units=cap)
        ).outcome
        is CurrentAdmissionOutcome.OK
    )
    at_limit = _smallest_ok(1, 1048576, probe)
    ok = derive_current_admission(
        state, h.ns, bounds=CurrentAdmissionBounds(max_total_work_units=at_limit)
    )
    assert ok.outcome is CurrentAdmissionOutcome.OK
    assert ok.overlay is not None
    assert ok.overlay.work_units == at_limit
    assert_admission_refused(
        derive_current_admission(
            state,
            h.ns,
            bounds=CurrentAdmissionBounds(max_total_work_units=at_limit - 1),
        ),
        state,
        CurrentAdmissionOutcome.REFUSED_OVER_BOUND,
        CurrentAdmissionLimitation.TOTAL_WORK_UNITS_OVER_BOUND,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_f_subtree_cap(mode: AdmissionMode, endpoint: str) -> None:
    """G: the ACTUAL supplied F subtree ceiling is enforced
    INDEPENDENTLY on the same shared outer: the essential POSITIVE
    -- F cap exactly F's own cost with the G total above it -- the
    full derivation still succeeds (the G admission/output work
    charges the G total, not the F subtree); one unit below F's cost
    refuses with the shared fixed name and the exact state."""
    h = _k1_fixture(mode, endpoint)
    state = h.state
    probe = lambda cap: (  # noqa: E731
        derive_current_admission(
            state, h.ns, graph_bounds=CurrentGraphBounds(max_total_work_units=cap)
        ).outcome
        is CurrentAdmissionOutcome.OK
    )
    f_cost = _smallest_ok(1, 1048576, probe)
    ok = derive_current_admission(
        state, h.ns, graph_bounds=CurrentGraphBounds(max_total_work_units=f_cost)
    )
    assert ok.outcome is CurrentAdmissionOutcome.OK
    assert ok.overlay is not None
    # The full G work strictly exceeds the F subtree cost: the G
    # admission/output phase charged the G total after F returned.
    assert ok.overlay.work_units > f_cost
    assert_admission_refused(
        derive_current_admission(
            state,
            h.ns,
            graph_bounds=CurrentGraphBounds(max_total_work_units=f_cost - 1),
        ),
        state,
        CurrentAdmissionOutcome.REFUSED_OVER_BOUND,
        CurrentAdmissionLimitation.TOTAL_WORK_UNITS_OVER_BOUND,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_stage_work_bound(mode: AdmissionMode, endpoint: str) -> None:
    """G: the ADMISSION planning/output stage ledger (the ACTUAL
    inherited GraphBounds.max_work_units domain, distinct from F
    graph work) is targeted at its own at-limit threshold: below the
    threshold the stricter cap still passes the F stage (its cost is
    lower) and refuses with the G-own stage name and the exact
    state -- the unrelated F stage domain is preserved."""
    h = _k1_fixture(mode, endpoint)
    state = h.state

    def probe(cap: int) -> bool:
        ns, st = _rekeyed(mode, state, graph_bounds=GraphBounds(max_work_units=cap))
        return derive_current_admission(st, ns).outcome is CurrentAdmissionOutcome.OK

    at_limit = _smallest_ok(1, 65536, probe)
    ns_ok, st_ok = _rekeyed(mode, state, graph_bounds=GraphBounds(max_work_units=at_limit))
    assert derive_current_admission(st_ok, ns_ok).outcome is CurrentAdmissionOutcome.OK
    ns_over, st_over = _rekeyed(mode, state, graph_bounds=GraphBounds(max_work_units=at_limit - 1))
    assert_admission_refused(
        derive_current_admission(st_over, ns_over),
        st_over,
        CurrentAdmissionOutcome.REFUSED_OVER_BOUND,
        CurrentAdmissionLimitation.ADMISSION_WORK_UNITS_EXHAUSTED,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_entry_source_bounds(mode: AdmissionMode, endpoint: str) -> None:
    """G: the CUMULATIVE newly owned entry-source bytes are counted
    once per distinct interned entry at the exact at-limit threshold
    (duplicate-key witnesses count the owned bytes ONCE while the
    association attempts count before dedup); the per-entry cap is
    the ACTUAL inherited GraphBounds.max_single_source_bytes,
    targeted on the actual acquired partitioned A|B proof (two
    20-byte proven regions, 40-byte aggregate, short root) via an
    EXPLICIT coherent stricter-bound DIAGNOSTIC projection of the
    actual earned history (the state history key projected to the
    stricter namespace actual key -- NOT new acquisition under the
    stricter namespace, not authority): the ACTUAL F derivation is
    positive at the cap AND one below (each region fits), the G
    derivation is OK at the cap retaining the ORIGINAL proof by
    identity, and refuses one below with the exact typed name and
    the exact state, its COMPLETE source touch profile (slice
    ranges, index accesses, encodes -- including the internal F
    pass) equal to the positive F's profile (same-value sentinel;
    G's own admission work adds zero touches)."""
    # --- Cumulative domain: counted once per distinct key ---------
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md` first.")
    h.read("c-a", "A body.\n")
    h.read("c-b", "B body.\n", cmd="cat B.md")
    state = h.state
    root_bytes = len(b"Read `A.md` and `B.md` first.")
    total = root_bytes + len(b"A body.\n") + len(b"B body.\n")
    probe = lambda cap: (  # noqa: E731
        derive_current_admission(
            state,
            h.ns,
            bounds=CurrentAdmissionBounds(max_total_entry_source_bytes=cap),
        ).outcome
        is CurrentAdmissionOutcome.OK
    )
    at_limit = _smallest_ok(1, 16777216, probe)
    assert at_limit == total
    assert_admission_refused(
        derive_current_admission(
            state,
            h.ns,
            bounds=CurrentAdmissionBounds(max_total_entry_source_bytes=total - 1),
        ),
        state,
        CurrentAdmissionOutcome.REFUSED_OVER_BOUND,
        CurrentAdmissionLimitation.TOTAL_ENTRY_SOURCE_BYTES_OVER_BOUND,
    )

    # Duplicate-key witnesses: the newly owned entry bytes count
    # ONCE (one distinct content key), both distinct witnesses are
    # retained, and the association attempts count BEFORE dedup
    # (root + first A + duplicate A).
    hd = Adm(mode, endpoint)
    hd.boot_root("Read `A.md` first.")
    hd.read("c-a1", "Dup body.\n")
    o_dup1 = hd.state.occurrences[-1].occurrence_id
    hd.issue("c-a2", (o_dup1, CAUSAL_ROOT_FACT))
    hd.read("c-a2", "Dup body.\n")
    v_d = hd.admission_ok()
    assert v_d.entry_source_bytes == len(b"Read `A.md` first.") + len(b"Dup body.\n")
    by_d = members_of(v_d)
    assert set(by_d) == {("A.md",)}
    assert len(by_d[("A.md",)].witnesses) == 2
    assert v_d.reverse_association_attempts == 3
    assert next(r for r in v_d.path_associations if r.path == "A.md").content_keys == (
        by_d[("A.md",)].content_key,
    )

    # --- Per-entry inherited cap (diagnostic projection) ----------
    h_e = Adm(mode, endpoint)
    h_e.boot_root("Read `A.md` and `B.md`.")
    seg_a, seg_b = "A" * 20, "B" * 20
    h_e.observe(
        read_request(
            endpoint,
            "c-p1",
            seg_a + "MARK\n" + seg_b,
            cmd="cat A.md && echo 'MARK' && cat B.md",
        ),
        note="read:c-p1",
    )
    proof = h_e.state.occurrences[-1].proof
    assert proof.source_text == seg_a + seg_b
    assert [s.byte_length for s in proof.segments] == [20, 20]
    assert [s.member_positions for s in proof.segments] == [(0,), (1,)]
    assert proof.source_byte_length == 40
    root_anchor = h_e.state.root
    assert root_anchor is not None
    assert len(root_anchor.root_text.encode()) < 39
    # Baseline: the default namespace is positive.
    base = h_e.admission_ok()
    assert base.entry_source_bytes == len(root_anchor.root_text.encode()) + 40
    # AT-LIMIT (40): F positive; G OK, original proof retained by
    # identity.
    ns40, st40 = _rekeyed(mode, h_e.state, graph_bounds=GraphBounds(max_single_source_bytes=40))
    assert derive_current_graph(st40, ns40).outcome is CurrentGraphOutcome.OK
    g40 = derive_current_admission(st40, ns40)
    assert g40.outcome is CurrentAdmissionOutcome.OK
    assert g40.overlay is not None
    assert len(g40.overlay.entries) == 1
    assert g40.overlay.entries[0].proof is proof
    assert g40.overlay.entries[0].key_record.aggregate_source_digest == _sha(seg_a + seg_b)
    # FIRST-OVER (39): F STILL positive (each proven region fits);
    # G refuses typed over the exact state with ZERO additional
    # source touches beyond the positive F.
    ns39, st39 = _rekeyed(mode, h_e.state, graph_bounds=GraphBounds(max_single_source_bytes=39))
    assert derive_current_graph(st39, ns39).outcome is CurrentGraphOutcome.OK
    spy = _RegionSentinel(st39.occurrences[0].proof.source_text)
    st39s = st39.model_copy(
        update={
            "occurrences": (
                st39.occurrences[0].model_copy(
                    update={
                        "proof": st39.occurrences[0].proof.model_copy(update={"source_text": spy})
                    }
                ),
            )
        }
    )
    # FIRST-OVER (39): F STILL positive (each proven region fits);
    # G refuses typed over the exact state, and its COMPLETE source
    # touch profile -- slice ranges, single-index accesses and
    # encodes, including its internal F pass -- is EXACTLY the
    # positive F's profile: G's own admission work adds zero
    # touches (same-value sentinel; class counters reset between the
    # two profiles so no global count carries across cases).
    _RegionSentinel.reset()
    assert derive_current_graph(st39s, ns39).outcome is CurrentGraphOutcome.OK
    f_touches = (
        list(_RegionSentinel.ranges),
        list(_RegionSentinel.indices),
        _RegionSentinel.encodes,
    )
    _RegionSentinel.reset()
    assert_admission_refused(
        derive_current_admission(st39s, ns39),
        st39s,
        CurrentAdmissionOutcome.REFUSED_OVER_BOUND,
        CurrentAdmissionLimitation.ENTRY_SOURCE_BYTES_OVER_BOUND,
    )
    g_touches = (
        list(_RegionSentinel.ranges),
        list(_RegionSentinel.indices),
        _RegionSentinel.encodes,
    )
    assert g_touches == f_touches, (
        "G cap refusal must touch the source exactly like positive F",
        f_touches,
        g_touches,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_scanner_candidates_per_document_refusal(mode: AdmissionMode, endpoint: str) -> None:
    """G: the ACTUAL inherited per-document reference-candidate
    scanner cap is defended by the ACTUAL ordinary-phase scan
    (mid-derivation, after the root is accepted) via EXPLICIT
    coherent stricter-bound DIAGNOSTIC projections of the actual
    earned history (the state history key projected to the stricter
    namespace actual key -- NOT new acquisition under the stricter
    namespace, not authority): the earned A body references two
    distinct files, so at the cap of 2 BOTH the public F derivation
    and the G-composed derivation are OK (root one reference, A two
    references, each at-limit), and at 1 BOTH refuse the exact
    GRAPH_CANDIDATES_OVER_BOUND over the exact state with no
    overlay -- G maps the internal F refusal 1:1 and never emits a
    partial admission.  The mid-phase ordinary-phase return arm is
    the exact branch the private-seam refactoring repairs: a
    scan-limitation refusal must leave the shared F/G loop with a
    typed whole-result refusal, never a mixed-shape value."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    h.read("c-a", "See `B.md`. See `C.md`.\n")
    state = h.state
    ns2, st2 = _rekeyed(
        mode, state, graph_bounds=GraphBounds(max_reference_candidates_per_document=2)
    )
    f2 = derive_current_graph(st2, ns2)
    assert f2.outcome is CurrentGraphOutcome.OK
    g2 = derive_current_admission(st2, ns2)
    assert g2.outcome is CurrentAdmissionOutcome.OK
    assert g2.overlay is not None
    ns1, st1 = _rekeyed(
        mode, state, graph_bounds=GraphBounds(max_reference_candidates_per_document=1)
    )
    f1 = derive_current_graph(st1, ns1)
    assert f1.outcome is CurrentGraphOutcome.REFUSED_OVER_BOUND
    assert f1.diagnostics == (CurrentGraphLimitation.GRAPH_CANDIDATES_OVER_BOUND,)
    assert f1.state is st1
    assert f1.overlay is None
    g1 = derive_current_admission(st1, ns1)
    assert g1.outcome is CurrentAdmissionOutcome.REFUSED_OVER_BOUND
    assert g1.diagnostics == (CurrentAdmissionLimitation.GRAPH_CANDIDATES_OVER_BOUND,)
    assert g1.state is st1
    assert g1.overlay is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_inherited_admission_caps(mode: AdmissionMode, endpoint: str) -> None:
    """G: the ACTUAL inherited 018-c admission caps keep their own
    admission-output domains: distinct interned ENTRIES, charged
    member OCCURRENCEs and reverse-index association ATTEMPTS each
    at their exact at-limit threshold and one below (per-field
    fixtures so the targeted domain crosses FIRST, per-field schema
    hard maxima, coherent rekeyed namespaces, exact refusal names)."""
    # Root + A + B singletons: 3 distinct entries, 3 member
    # occurrences, 3 association attempts.
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md` first.")
    h.read("c-a", "A body.\n")
    h.read("c-b", "B body.\n", cmd="cat B.md")
    state = h.state

    def entries_probe(cap: int) -> bool:
        ns_c, st_c = _rekeyed_ns_bounds(mode, state, max_entries=cap)
        return derive_current_admission(st_c, ns_c).outcome is CurrentAdmissionOutcome.OK

    at_limit = _smallest_ok(1, 128, entries_probe)
    assert at_limit == 3
    ns_ok, st_ok = _rekeyed_ns_bounds(mode, state, max_entries=at_limit)
    assert derive_current_admission(st_ok, ns_ok).outcome is CurrentAdmissionOutcome.OK
    ns_over, st_over = _rekeyed_ns_bounds(mode, state, max_entries=at_limit - 1)
    assert_admission_refused(
        derive_current_admission(st_over, ns_over),
        st_over,
        CurrentAdmissionOutcome.REFUSED_OVER_BOUND,
        CurrentAdmissionLimitation.ENTRIES_OVER_BOUND,
    )

    def associations_probe(cap: int) -> bool:
        ns_c, st_c = _rekeyed_ns_bounds(mode, state, max_reverse_associations=cap)
        return derive_current_admission(st_c, ns_c).outcome is CurrentAdmissionOutcome.OK

    at_limit = _smallest_ok(1, 4096, associations_probe)
    assert at_limit == 3
    ns_ok, st_ok = _rekeyed_ns_bounds(mode, state, max_reverse_associations=at_limit)
    assert derive_current_admission(st_ok, ns_ok).outcome is CurrentAdmissionOutcome.OK
    ns_over, st_over = _rekeyed_ns_bounds(mode, state, max_reverse_associations=at_limit - 1)
    assert_admission_refused(
        derive_current_admission(st_over, ns_over),
        st_over,
        CurrentAdmissionOutcome.REFUSED_OVER_BOUND,
        CurrentAdmissionLimitation.REVERSE_ASSOCIATIONS_OVER_BOUND,
    )

    # Root + ONE partitioned whole AB: 2 distinct entries but 3
    # charged member occurrences (root + A + B) -- the member domain
    # crosses first below 3.
    h_m = Adm(mode, endpoint)
    h_m.boot_root("Read `A.md` and `B.md` first.")
    _partition_fixture(h_m, "A part.\n", "B part.\n")
    m_state = h_m.state

    def members_probe(cap: int) -> bool:
        ns_c, st_c = _rekeyed_ns_bounds(mode, m_state, max_member_occurrences=cap)
        return derive_current_admission(st_c, ns_c).outcome is CurrentAdmissionOutcome.OK

    at_limit = _smallest_ok(1, 1024, members_probe)
    assert at_limit == 3
    ns_ok, st_ok = _rekeyed_ns_bounds(mode, m_state, max_member_occurrences=at_limit)
    assert derive_current_admission(st_ok, ns_ok).outcome is CurrentAdmissionOutcome.OK
    ns_over, st_over = _rekeyed_ns_bounds(mode, m_state, max_member_occurrences=at_limit - 1)
    assert_admission_refused(
        derive_current_admission(st_over, ns_over),
        st_over,
        CurrentAdmissionOutcome.REFUSED_OVER_BOUND,
        CurrentAdmissionLimitation.MEMBER_OCCURRENSES_OVER_BOUND,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_many_retained_observations_legal(mode: AdmissionMode, endpoint: str) -> None:
    """G: MORE than 128 retained observations across many legal
    single-request batches stay legal under the DEFAULT ceilings
    (the public batch cap bounds ONE batch -- its 129-request
    refusal is the inherited 018-d law covered by test_causal_history
    -- not the retained history): one ACTUALLY acquired root-
    referenced A plus 129 unrelated off-graph Fi reads yield 130
    retained occurrences with exactly the root + A admitted, the
    original A proof/witness retained by identity, the unrelated
    sources excluded and the ONE stage-level candidate diagnostic
    emitted."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    a = h.read("retained-a", "A stable body.")
    p = h.state.occurrences[-1].proof
    for i in range(129):
        h.read(f"retained-extra-{i}", f"Unrelated source {i}.", cmd=f"cat F{i}.md")
    assert len(h.state.occurrences) == 130
    v = h.admission_ok()
    assert len(v.entries) == 1 and v.entries_retained == 2
    assert v.entries[0].key_record.member_occurrences == ("A.md",)
    assert v.entries[0].proof is p
    assert [w.occurrence_id for w in v.entries[0].witnesses] == [a]
    assert v.emitted_admission_reasons == 1
    assert {row.path for row in v.path_associations} == {"AGENTS.md", "A.md"}


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_stale_source_sentinel(mode: AdmissionMode, endpoint: str) -> None:
    """G: the STALE A region of the partitioned proof is never
    encoded and never sliced after the currentness mask (zero
    stale-region touches); the admitted B region is sliced a fixed
    small number of times (F region pass + G model region pass), the
    retained sentinel proof is kept by identity, and NO encode of
    the retained source text ever happens."""
    h = _k1_fixture(mode, endpoint)
    p1 = next(o.occurrence_id for o in h.state.occurrences if o.call_id == "c-p1")
    p1_occ = next(o for o in h.state.occurrences if o.occurrence_id == p1)
    assert p1_occ.proof.source_text == ("From A see `C.md`.\nFrom B see `D.md`.\n")
    a_len = len("From A see `C.md`.\n")
    b_len = len("From B see `D.md`.\n")
    sent = _RegionSentinel(p1_occ.proof.source_text)
    _RegionSentinel.reset()
    forged_proof = p1_occ.proof.model_copy(update={"source_text": sent})
    forged_occ = p1_occ.model_copy(update={"proof": forged_proof})
    state = h.state.model_copy(
        update={
            "occurrences": tuple(
                forged_occ if o.occurrence_id == p1 else o for o in h.state.occurrences
            )
        }
    )
    result = derive_current_admission(state, h.ns)
    assert result.outcome is CurrentAdmissionOutcome.OK
    a = result.overlay
    assert a is not None
    # Never an owned encode copy of the retained source.
    assert _RegionSentinel.encodes == 0
    # The STALE A region [0, a_len) is never sliced.
    for start, stop in _RegionSentinel.ranges:
        assert not (start < a_len and stop > 0), (
            "stale A region touched",
            _RegionSentinel.ranges,
        )
        assert (start, stop) == (a_len, a_len + b_len), (
            "only the admitted B region may be sliced",
            _RegionSentinel.ranges,
        )
    # ...and never single-indexed either.
    assert all(a_len <= i < a_len + b_len for i in _RegionSentinel.indices), (
        "index touches must stay inside the admitted B region",
        _RegionSentinel.indices,
    )
    if mode is AdmissionMode.LEAN:
        # F region pass + the G model region pass (fixture-specific).
        assert len(_RegionSentinel.ranges) == 2
        b_entry = members_of(a)[("B.md",)]
        assert b_entry.proof is forged_proof  # retained by identity
    else:
        # Greedy admits nothing from the old proof: only the F pass.
        assert len(_RegionSentinel.ranges) == 1
        assert ("B.md",) not in members_of(a)


def test_g_merge_witness_reserve_before_copy() -> None:
    """G: the witness-retention dedup over the FULL coordinate
    tuples reserves the linear work on BOTH ledgers BEFORE the first
    crossing copy/iteration over the actual retained witness list:
    an exhausted outer (or an exhausted stage) refuses with the
    exact limitation and the instrumented witness list is NEVER
    iterated (zero copies); a sufficient ledger performs exactly the
    first copy and retains the actual coordinate-sorted witnesses
    (n = 2 real witnesses from the SAME derivation).  The witness
    constructor normalizes str subclasses, so same-value hash
    instrumentation is not possible; the counting-iteration sentinel
    therefore targets the FIRST crossing copy over the actual
    witness list.  The same-value instrumentation is diagnostic
    only, never new authority; the input entry is never mutated."""
    h = Adm(AdmissionMode.LEAN, "responses")
    h.boot_root("Read `A.md` and `B.md` first.")
    h.read("c-1", "Merge body.\n")
    h.read("c-b", "B body.\n", cmd="cat B.md")
    a = h.admission_ok()
    entry = next(e for e in a.entries if e.key_record.member_occurrences == ("A.md",))
    assert len(entry.witnesses) == 1
    w1 = entry.witnesses[0]
    # A real second witness from the SAME derivation (the B entry).
    w2 = next(e for e in a.entries if e.key_record.member_occurrences == ("B.md",)).witnesses[0]
    witness = w2

    class _CountingWitnesses(tuple[Any]):
        """Same-value tuple stand-in whose __iter__ records every
        copy taken over the retained witness list."""

        iters = 0

        def __iter__(self) -> Iterator[Any]:
            _CountingWitnesses.iters += 1
            return super().__iter__()

    existing = entry.model_copy(update={"witnesses": _CountingWitnesses(entry.witnesses)})
    f_bounds = CurrentGraphBounds(max_total_work_units=1048576)
    # Exhausted OUTER (cap 1): the 1 + 2n reservation crosses before
    # any crossing copy or iteration.
    _CountingWitnesses.iters = 0
    outer = _impl._GOuter(f_bounds, CurrentAdmissionBounds(max_total_work_units=1))
    stage = _impl._GStage(GraphBounds())
    with pytest.raises(_impl._GOverflow) as excinfo:
        _impl._merge_witnesses(existing, witness, outer, stage)
    assert excinfo.value.limitation is (CurrentAdmissionLimitation.TOTAL_WORK_UNITS_OVER_BOUND)
    assert _CountingWitnesses.iters == 0
    # Exhausted STAGE (cap 1), sufficient outer: same pre-copy law
    # on the admission stage domain.
    _CountingWitnesses.iters = 0
    outer = _impl._GOuter(f_bounds, CurrentAdmissionBounds(max_total_work_units=1048576))
    stage = _impl._GStage(GraphBounds(max_work_units=1))
    with pytest.raises(_impl._GOverflow) as excinfo:
        _impl._merge_witnesses(existing, witness, outer, stage)
    assert excinfo.value.limitation is (CurrentAdmissionLimitation.ADMISSION_WORK_UNITS_EXHAUSTED)
    assert _CountingWitnesses.iters == 0
    # Sufficient ledger: exactly the FIRST copy over the retained
    # list, the actual coordinate-sorted witnesses retained (n = 2).
    _CountingWitnesses.iters = 0
    outer = _impl._GOuter(f_bounds, CurrentAdmissionBounds(max_total_work_units=1048576))
    stage = _impl._GStage(GraphBounds())
    merged = _impl._merge_witnesses(existing, witness, outer, stage)
    assert _CountingWitnesses.iters == 1
    assert len(merged) == 2
    assert [_witness_key(w) for w in merged] == sorted([_witness_key(w1), _witness_key(w2)])
    assert entry.witnesses == (w1,)  # the input entry is untouched


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_typed_refusals(mode: AdmissionMode, endpoint: str) -> None:
    """G: every early fence is a fixed whole-result typed refusal
    over the EXACT input state with no partial overlay: foreign
    history scope, coherent unsupported version (full key chain
    recomputed), no root, corrupted retained occurrences and a
    forged anchor."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    h.read("c-1", "A body.\n")
    state = h.state

    foreign = derive_current_admission(state, h.ns.model_copy(update={"history_key": "f" * 64}))
    assert_admission_refused(
        foreign,
        state,
        CurrentAdmissionOutcome.REFUSED_FOREIGN_SCOPE,
        CurrentAdmissionLimitation.FOREIGN_SCOPE,
    )

    version_ns = _coherent_rekeyed_ns(h.ns, {"history_version": "unsupported-synthetic/v99"})
    version_state = state.model_copy(update={"history_key": version_ns.history_key})
    assert_admission_refused(
        derive_current_admission(version_state, version_ns),
        version_state,
        CurrentAdmissionOutcome.REFUSED_VERSION_CONFLICT,
        CurrentAdmissionLimitation.VERSION_UNSUPPORTED,
    )

    no_root_state = empty_state(h.ns)
    no_root = derive_current_admission(no_root_state, h.ns)
    assert_admission_refused(
        no_root,
        no_root_state,
        CurrentAdmissionOutcome.REFUSED_NO_ROOT,
        CurrentAdmissionLimitation.ROOT_MISSING,
    )

    dup_state = state.model_copy(update={"occurrences": state.occurrences * 2})
    assert_admission_refused(
        derive_current_admission(dup_state, h.ns),
        dup_state,
        CurrentAdmissionOutcome.REFUSED_STATE_MALFORMED,
        CurrentAdmissionLimitation.STATE_MALFORMED,
    )

    anchor = state.root
    assert anchor is not None
    forged_state = state.model_copy(update={"root": forge(anchor, root_text=7)})
    assert_admission_refused(
        derive_current_admission(forged_state, h.ns),
        forged_state,
        CurrentAdmissionOutcome.REFUSED_STATE_MALFORMED,
        CurrentAdmissionLimitation.ROOT_MALFORMED,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_no_host_io(mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """G: every public current-admission path -- the OK derivation
    and the foreign-scope / no-root / malformed / forged-root /
    outer-overbound / coherent-unsupported-version refusals --
    performs no host IO: no file, socket, subprocess or path IO
    facility is touched after import/setup."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    h.read("io-1", "A body.\n")
    state = h.state
    attempts: list[str] = []

    def deny(name: str) -> object:
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
    monkeypatch.setattr(pathlib.Path, "open", deny("Path.open"))
    monkeypatch.setattr(pathlib.Path, "read_bytes", deny("Path.read_bytes"))
    monkeypatch.setattr(pathlib.Path, "read_text", deny("Path.read_text"))

    ok = derive_current_admission(state, h.ns)
    assert ok.outcome is CurrentAdmissionOutcome.OK
    assert ok.overlay is not None
    assert (
        derive_current_admission(state, h.ns.model_copy(update={"history_key": "f" * 64})).outcome
        is CurrentAdmissionOutcome.REFUSED_FOREIGN_SCOPE
    )
    assert (
        derive_current_admission(empty_state(h.ns), h.ns).outcome
        is CurrentAdmissionOutcome.REFUSED_NO_ROOT
    )
    anchor = state.root
    assert anchor is not None
    forged = derive_current_admission(
        state.model_copy(update={"root": forge(anchor, root_text=7)}), h.ns
    )
    assert forged.outcome is CurrentAdmissionOutcome.REFUSED_STATE_MALFORMED
    over = derive_current_admission(
        state, h.ns, bounds=CurrentAdmissionBounds(max_total_work_units=1)
    )
    assert over.outcome is CurrentAdmissionOutcome.REFUSED_OVER_BOUND
    version_ns = _coherent_rekeyed_ns(h.ns, {"history_version": "unsupported-synthetic/v99"})
    version = derive_current_admission(
        state.model_copy(update={"history_key": version_ns.history_key}), version_ns
    )
    assert version.outcome is CurrentAdmissionOutcome.REFUSED_VERSION_CONFLICT
    assert attempts == []


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_private_reprs(mode: AdmissionMode, endpoint: str) -> None:
    """G: the NEW G-owned operational representations never echo
    the private member paths (fixed placeholders, counts and
    digests only) in repr() or str() of the admission, its root
    entry, every file entry, every witness, the retained-root
    provenance and every reverse-index row, while the actual
    internal path fields stay unchanged."""
    h = Adm(mode, endpoint)
    h.boot_root(f"Read `{CANARY}A.md` first.")
    h.read("c-priv", f"See `{CANARY}B.md`.\n", cmd=f"cat {CANARY}A.md")
    a = h.admission_ok()
    records: list[Any] = [a, a.root_entry]
    records.extend(a.entries)
    for entry in (a.root_entry, *a.entries):
        records.extend(entry.witnesses)
    if a.root_entry.root_provenance is not None:
        records.append(a.root_entry.root_provenance)
    records.extend(a.path_associations)
    for record in records:
        for rendered in (repr(record), str(record)):
            assert CANARY not in rendered, rendered
    # The actual internal path fields stay unchanged.
    assert a.root_entry.key_record.member_occurrences == ("AGENTS.md",)
    assert a.entries[0].key_record.member_occurrences == (f"{CANARY}A.md",)
    assert [row.path for row in a.path_associations] == sorted(["AGENTS.md", f"{CANARY}A.md"])
    refused = derive_current_admission(h.state, h.ns.model_copy(update={"history_key": "f" * 64}))
    for rendered in (repr(refused), str(refused)):
        assert CANARY not in rendered, rendered


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_scope_key_binding(mode: AdmissionMode, endpoint: str) -> None:
    """G: the derivation scope key binds the ACTUAL versions and
    every effective bound set: each changed G/overlay/graph bound
    set yields a DISTINCT key, and a direct constructor with a
    forged scope key is refused (recomputed, never caller-asserted)."""
    h = Adm(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    h.read("c-1", "A body.\n")
    state = h.state
    base = h.admission_ok()
    k_base = base.scope_key
    e_result = derive_current_admission(
        state, h.ns, currentness_bounds=CurrentnessBounds(max_diagnostics=63)
    )
    assert e_result.outcome is CurrentAdmissionOutcome.OK
    assert e_result.overlay is not None
    e_overlay = e_result.overlay
    g_overlay = h.admission_ok(bounds=CurrentAdmissionBounds(max_diagnostics=63))
    f_overlay = h.admission_ok(graph_bounds=CurrentGraphBounds(max_total_work_units=1048575))
    assert k_base != e_overlay.scope_key
    assert k_base != g_overlay.scope_key
    assert k_base != f_overlay.scope_key
    # Derivation-only bound changes (successful E/F/G derivations)
    # bind the NEW scope key but NOT the compiler-semantic key
    # records: the root and every file key record stay byte-identical
    # under the changed derivation bounds (no cache-hit claim; the
    # semantic keys simply do not bind derivation bounds).
    for overlay in (e_overlay, g_overlay, f_overlay):
        assert overlay.scope_key != k_base
        assert overlay.root_entry.key_record == base.root_entry.key_record
        assert [x.content_key for x in overlay.entries] == [x.content_key for x in base.entries]
        for new_entry, old_entry in zip(overlay.entries, base.entries, strict=True):
            assert new_entry.key_record == old_entry.key_record
    # Inherited bound changes bind through the coherent ACTUAL
    # namespace key (the admission namespace key recomputed).
    ns_inh, st_inh = _rekeyed(mode, state, bounds=BundleAdmissionBounds(max_entries=127))
    inh = derive_current_admission(st_inh, ns_inh)
    assert inh.outcome is CurrentAdmissionOutcome.OK
    assert inh.overlay is not None
    assert inh.overlay.scope_key != k_base

    # A forged scope key cannot be retained by direct construction.
    kwargs = {name: getattr(base, name) for name in CurrentAdmission.model_fields}
    kwargs["scope_key"] = "0" * 64
    with pytest.raises(ValidationError):
        CurrentAdmission(**kwargs)
    # And the real fields recompute the bound key.
    kwargs["scope_key"] = k_base
    assert CurrentAdmission(**kwargs).scope_key == k_base


def test_g_model_negatives() -> None:
    """G: the NEW model invariants as direct constructor negatives:
    typed references refuse dict input, witnesses are sorted and
    deduplicated, admitted segments are linear-checked, entries are
    sorted by distinct content key, the root entry never carries
    witnesses, and reverse rows keep distinct content keys."""
    h = Adm(AdmissionMode.LEAN, "responses")
    h.boot_root("Read `A.md` and `B.md` first.")
    h.read("c-a", "A body.\n")
    h.read("c-b", "B body.\n", cmd="cat B.md")
    a = h.admission_ok()
    file_entry = a.entries[0]
    root_entry = a.root_entry
    witness = file_entry.witnesses[0]

    # Typed references refuse dict input (class check, not auth).
    with pytest.raises(ValidationError):
        CurrentAdmissionEntry(
            **{
                **{name: getattr(file_entry, name) for name in CurrentAdmissionEntry.model_fields},
                "key_record": {"not": "a record"},
            }
        )
    with pytest.raises(ValidationError):
        CurrentAdmission(
            **{
                **{name: getattr(a, name) for name in CurrentAdmission.model_fields},
                "root_entry": {"not": "an entry"},
            }
        )
    # Duplicate witnesses are refused (dedup invariant).
    with pytest.raises(ValidationError):
        CurrentAdmissionEntry(
            **{
                **{name: getattr(file_entry, name) for name in CurrentAdmissionEntry.model_fields},
                "witnesses": (witness, witness),
            }
        )
    # Unsorted/duplicate admitted segments are refused by the linear
    # adjacency law.
    with pytest.raises(ValidationError):
        CurrentAdmissionEntry(
            **{
                **{name: getattr(file_entry, name) for name in CurrentAdmissionEntry.model_fields},
                "admitted_segments": (1, 0),
            }
        )
    # The root entry never carries a fabricated read witness.
    with pytest.raises(ValidationError):
        CurrentAdmissionEntry(
            **{
                **{name: getattr(root_entry, name) for name in CurrentAdmissionEntry.model_fields},
                "witnesses": (witness,),
            }
        )
    # Entries must be sorted by distinct content key.
    if len(a.entries) >= 2:
        swapped = tuple(reversed(a.entries))
        with pytest.raises(ValidationError):
            CurrentAdmission(
                **{
                    **{name: getattr(a, name) for name in CurrentAdmission.model_fields},
                    "entries": swapped,
                }
            )
    # Reverse rows keep distinct content keys.
    row = next(r for r in a.path_associations if len(r.content_keys) == 1)
    with pytest.raises(ValidationError):
        CurrentAdmissionPathAssociation(
            scoped_key=row.scoped_key,
            path=row.path,
            content_keys=(row.content_keys[0], row.content_keys[0]),
            is_root=row.is_root,
        )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_admission_reason_retention(mode: AdmissionMode, endpoint: str) -> None:
    """G: the emitted admission reasons are RETAINED in the overlay:
    the unadmitted opaque-root proof carries the exact fixed
    candidate_unproven tuple with the emitted count bound to its
    length (result-level diagnostics empty, exact state identity),
    and the fully admitted history carries the EMPTY tuple
    (zero-reason control); a normal derivation emits at most ONE
    unique candidate reason.  Direct constructor negatives close the
    schema: mismatched count, first-over under a strict POSITIVE G
    cap (the at-cap construction with the coherent recomputed scope
    key stays accepted), the inherited admission cap in the SAME
    domain, and unsorted/duplicate reasons are all refused.  These
    constructor controls are schema-level evidence, distinct from
    public acquisition evidence."""
    # --- original API: unadmitted vs zero reasons -----------------
    h = _opaque_root_plus_b_fixture(mode, endpoint)
    state = h.state
    result = h.admission()
    assert result.outcome is CurrentAdmissionOutcome.OK
    assert result.state is state
    assert result.diagnostics == ()  # no derivation-level diagnostics
    a = result.overlay
    assert a is not None
    assert a.emitted_admission_reasons == len(a.admission_reasons)
    if mode is AdmissionMode.LEAN:
        assert a.admission_reasons == ()
        assert a.emitted_admission_reasons == 0
    else:
        assert a.admission_reasons == (CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,)
        assert a.emitted_admission_reasons == 1
        assert "CANDIDATE_UNPROVEN" in repr(a)  # caller-inspectable
    # zero-reason control on a fully admitted history
    h2 = Adm(mode, endpoint)
    h2.boot_root("Read `A.md` first.")
    h2.read("c-a", "A body.\n")
    a2 = h2.admission_ok()
    assert a2.admission_reasons == ()
    assert a2.emitted_admission_reasons == 0

    # --- direct constructor schema negatives (greedy: 1 reason) ---
    if mode is not AdmissionMode.GREEDY:
        return
    base_kw = {name: getattr(a, name) for name in CurrentAdmission.model_fields}
    # Mismatched count: the retained tuple is empty, the count says 1.
    with pytest.raises(ValidationError):
        CurrentAdmission(**{**base_kw, "admission_reasons": ()})
    # Strict POSITIVE at the G cap: exactly one reason with cap 1,
    # the scope key coherently recomputed.
    kw_strict = {**base_kw, "bounds": CurrentAdmissionBounds(max_diagnostics=1)}
    kw_strict["scope_key"] = _scope_key_of(kw_strict)
    strict_ok = CurrentAdmission(**kw_strict)
    assert strict_ok.admission_reasons == (CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,)
    # First-over the G cap: two reasons under cap 1.
    kw_over = {
        **kw_strict,
        "admission_reasons": (
            CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,
            CurrentAdmissionLimitation.ENTRIES_OVER_BOUND,
        ),
        "emitted_admission_reasons": 2,
    }
    kw_over["scope_key"] = _scope_key_of(kw_over)
    with pytest.raises(ValidationError):
        CurrentAdmission(**kw_over)
    # The INHERITED admission cap in the SAME domain (G cap stays 64).
    kw_inh = {
        **base_kw,
        "admission_bounds": BundleAdmissionBounds(max_diagnostics=1),
    }
    kw_inh["scope_key"] = _scope_key_of(kw_inh)
    with pytest.raises(ValidationError):
        CurrentAdmission(
            **{
                **kw_inh,
                "admission_reasons": (
                    CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,
                    CurrentAdmissionLimitation.ENTRIES_OVER_BOUND,
                ),
                "emitted_admission_reasons": 2,
            }
        )
    # Unsorted reasons (sorted dedup invariant).
    with pytest.raises(ValidationError):
        CurrentAdmission(
            **{
                **base_kw,
                "admission_reasons": (
                    CurrentAdmissionLimitation.ENTRIES_OVER_BOUND,
                    CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,
                ),
                "emitted_admission_reasons": 2,
            }
        )
    # Duplicate reasons.
    with pytest.raises(ValidationError):
        CurrentAdmission(
            **{
                **base_kw,
                "admission_reasons": (
                    CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,
                    CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,
                ),
                "emitted_admission_reasons": 2,
            }
        )
