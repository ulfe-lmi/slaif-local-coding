"""Durable original-API acceptance: inert current-root graph/admission
composition (018-i).

The A-H matrix of the activated 018-i order, over BOTH read
endpoints and BOTH modes wherever applicable, exercised on the
ACTUAL retained 018-h state and namespace earned through the
original public D/H APIs (bootstrap, issuance, observation,
receipt, selection).  No strategic-runtime dependency: known-
synthetic original API fixtures only, and every oracle asserts the
exact typed outcome, the exact input state identity, the original
proof/anchor/occurrence identities and the fixed closed
diagnostics.  Constructor-only negatives that are structurally
unreachable through the original public acquisition are labeled as
such and never substitute for public evidence.
"""

from __future__ import annotations

import hashlib
import json
import os
import socket
import subprocess
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles import (
    current_root_composition as crc,
)
from slaif_local_coding.constitution.bundles import (
    current_root_composition_models as crcm,
)
from slaif_local_coding.constitution.bundles.bundle_admission import (
    observe_bundle_admission_batch,
)
from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
    BoundaryClass,
    EntryClass,
    MemberClass,
    OwnershipGroup,
    make_bundle_admission_namespace,
)
from slaif_local_coding.constitution.bundles.bundle_proof_models import (
    ROOT_FILENAME,
    BundleProofBounds,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
    CausalHistoryLimitation,
    HistoryBounds,
    make_causal_history_namespace,
    validate_causal_history_state,
)
from slaif_local_coding.constitution.bundles.current_admission_models import (
    CurrentAdmissionBounds,
    CurrentAdmissionLimitation,
    CurrentAdmissionPathAssociation,
    CurrentAdmissionWitness,
    _canonical_entry_key,
)
from slaif_local_coding.constitution.bundles.current_graph_models import (
    CurrentGraphBounds,
)
from slaif_local_coding.constitution.bundles.current_root_composition import (
    _h_refusal,
    derive_current_root_composition,
)
from slaif_local_coding.constitution.bundles.current_root_composition_models import (
    CurrentRootComposition,
    CurrentRootCompositionAdmission,
    CurrentRootCompositionBounds,
    CurrentRootCompositionEntry,
    CurrentRootCompositionLimitation,
    CurrentRootCompositionOutcome,
)
from slaif_local_coding.constitution.bundles.currentness_models import (
    CurrentnessBounds,
)
from slaif_local_coding.constitution.bundles.graph_models import GraphBounds
from slaif_local_coding.constitution.bundles.graph_observation import GraphRequest
from slaif_local_coding.constitution.bundles.observation_models import (
    EMPTY_SOURCE_SHA256,
    ObservationBounds,
)
from slaif_local_coding.constitution.bundles.root_lineage import (
    bootstrap_root_lineage,
    observe_root_lineage,
    register_root_receipt,
    select_current_root,
)
from slaif_local_coding.constitution.bundles.root_lineage_models import (
    ROOT_LINEAGE_CONTRACT_VERSION,
    ROOT_LINEAGE_POLICY_VERSION,
    RootLineageBounds,
    RootLineageLimitation,
    RootLineageNamespace,
    RootLineageOutcome,
    RootLineageState,
    RootSelectionOutcome,
    RootSelectionResult,
    _lineage_key,
)
from tests.test_causal_history import (
    ENDPOINTS,
    FINGERPRINT,
    IDENTITY,
    MODES,
    ROOT_TEXT,
    WORKSPACE,
    read_request,
    root_request,
)
from tests.test_current_admission import _smallest_ok
from tests.test_root_lineage import (
    NEW_ROOT,
    ROOT_READ_ARGS,
    SIBLING_X,
    SIBLING_Y,
    SIBLING_Z,
    UNPROVEN_BODY,
    bootstrap,
    changed_root_envelope,
    envelope_fact,
    h_ns,
    issue,
    occurrences,
    read_fact,
    receipt,
    root_chain,
    rooted,
    shifted_root_envelope,
)

_L = CurrentRootCompositionLimitation
_OUT = CurrentRootCompositionOutcome


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def derive(
    state: RootLineageState, ns: RootLineageNamespace, **kwargs: Any
) -> CurrentRootComposition:
    return derive_current_root_composition(state, ns, **kwargs)


def i_members_of(
    admission: CurrentRootCompositionAdmission | None,
) -> dict[tuple[str, ...], CurrentRootCompositionEntry]:
    """The NEW current-root admission member mapping (the accepted G
    ``members_of`` shape over the I entry law)."""
    assert admission is not None
    return {tuple(entry.key_record.member_occurrences): entry for entry in admission.entries}


def h_bootstrap(ns: RootLineageNamespace, request: GraphRequest | None = None) -> RootLineageState:
    t = bootstrap_root_lineage((request or root_request(),), ns)
    assert t.outcome is RootLineageOutcome.ACCEPTED, t.diagnostics
    return t.state


def h_ns_ws(
    mode: Any,
    lineage: str,
    workspace: str,
    bounds: RootLineageBounds | None = None,
    graph_bounds: GraphBounds | None = None,
    observation_bounds: ObservationBounds | None = None,
) -> RootLineageNamespace:
    """An H scope over an ACTUAL D scope with an explicit workspace
    (the long-workspace resource reservations bind the actual
    workspace length, never a constant)."""
    admission = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-history-model",
        config_fingerprint=FINGERPRINT,
        workspace=workspace,
        mode=mode,
        graph_bounds=graph_bounds,
        observation_bounds=observation_bounds,
    )
    d = make_causal_history_namespace(admission, lineage)
    b = RootLineageBounds() if bounds is None else bounds
    data = d.model_dump()
    data.update(
        root_lineage_bounds=b,
        contract_version=ROOT_LINEAGE_CONTRACT_VERSION,
        policy_version=ROOT_LINEAGE_POLICY_VERSION,
        lineage_key=_lineage_key(
            d.history_key, ROOT_LINEAGE_CONTRACT_VERSION, ROOT_LINEAGE_POLICY_VERSION, b
        ),
    )
    return RootLineageNamespace(**data)


def root_request_ws(workspace: str, content: str = ROOT_TEXT) -> GraphRequest:
    """One legitimate Responses root envelope request for an explicit
    workspace (the header label carries the evidenced scope)."""
    item = {
        "role": "user",
        "content": [
            {
                "type": "input_text",
                "text": (
                    f"# AGENTS.md instructions for {workspace}\n\n"
                    f"<INSTRUCTIONS>\n{content}\n</INSTRUCTIONS>\n"
                ),
            }
        ],
    }
    return GraphRequest(payload={"input": [item]}, endpoint="responses", context=None)


def refreshed(
    state: RootLineageState,
    ns: RootLineageNamespace,
    call_id: str,
    endpoint: str,
    body: str,
    parent: str | tuple[str, ...] = CAUSAL_ROOT_FACT,
    args: str = ROOT_READ_ARGS,
    cmd: str = "cat AGENTS.md",
) -> RootLineageState:
    """ONE genuine issued read (the original H acquisition).

    ``args`` (the trusted issuance argument fingerprint) and ``cmd``
    (the observed read command) must match for the paired result to
    bind; the default pair is the ACTUAL root path read."""
    frontier = (parent,) if isinstance(parent, str) else tuple(parent)
    t = issue(state, ns, call_id, endpoint, frontier, args=args)
    assert t.outcome is RootLineageOutcome.ACCEPTED, t.diagnostics
    t2 = observe_root_lineage(
        t.state, ns, t.state.revision, (read_request(endpoint, call_id, body, cmd),)
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED, t2.diagnostics
    return t2.state


def nonroot_read(
    state: RootLineageState,
    ns: RootLineageNamespace,
    call_id: str,
    endpoint: str,
    body: str,
    cmd: str = "cat A.md",
) -> RootLineageState:
    t = observe_root_lineage(
        state, ns, state.revision, (read_request(endpoint, call_id, body, cmd),)
    )
    assert t.outcome is RootLineageOutcome.ACCEPTED, t.diagnostics
    return t.state


def assert_i_ok(r: CurrentRootComposition, state: RootLineageState) -> None:
    assert r.outcome is _OUT.OK, (r.outcome, r.diagnostics)
    assert r.state is state
    assert r.graph is not None
    assert r.admission is not None
    assert r.selected_root_provenance is not None
    assert r.selected_root_source_byte_length is not None
    assert r.selection is not None
    assert r.selection.outcome is RootSelectionOutcome.OK
    assert r.diagnostics in ((), (_L.ROOT_SOURCE_UNPROVEN,))
    assert r.graph.history_key == state.d_state.history_key
    assert r.graph.revision == state.d_state.revision
    assert r.admission.graph is r.graph
    assert r.admission.root_digest == r.graph.root_digest
    assert r.admission.root_entry.root_digest == r.graph.root_digest
    assert r.selected_root_provenance == r.admission.root_entry.root_provenance
    assert r.selected_root_source_byte_length == r.admission.root_entry.root_source_byte_length


def assert_i_refused(
    r: CurrentRootComposition,
    state: RootLineageState,
    outcome: CurrentRootCompositionOutcome,
    limitations: tuple[CurrentRootCompositionLimitation, ...],
) -> None:
    assert r.outcome is outcome, (r.outcome, r.diagnostics)
    assert r.state is state
    assert r.graph is None
    assert r.admission is None
    assert r.selected_root_provenance is None
    assert r.selected_root_source_byte_length is None
    assert r.diagnostics == limitations


def entry_field_data(entry: CurrentRootCompositionEntry, key_record: Any) -> dict[str, Any]:
    data = {name: getattr(entry, name) for name in CurrentRootCompositionEntry.model_fields}
    data["key_record"] = key_record
    return data


def admission_field_data(
    admission: CurrentRootCompositionAdmission | None, **overrides: Any
) -> dict[str, Any]:
    assert admission is not None
    data = {name: getattr(admission, name) for name in CurrentRootCompositionAdmission.model_fields}
    data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# A. Bootstrap / ENVELOPE / genuine refresh / replays
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_bootstrap_envelope_composition(mode: Any, endpoint: str) -> None:
    """A: the bootstrap H state composes to the ENVELOPE selected
    root: the exact retained anchor bytes/digest, the single first-
    class ROOT_ENTRY under the selected digest, the fresh current
    graph over the bootstrap supplier and NO file entries (no
    nonroot read was observed yet)."""
    ns, s0 = bootstrap(mode, "i-a-boot")
    r = derive(s0, ns)
    assert_i_ok(r, s0)
    assert r.selection is not None
    assert r.selected_root_provenance.kind == "envelope"  # type: ignore[union-attr]
    assert r.selected_root_source_byte_length == len(ROOT_TEXT.encode("utf-8"))
    assert r.graph.root_digest == sha(ROOT_TEXT)  # type: ignore[union-attr]
    root_nodes = [n for n in r.graph.nodes if n.path == ROOT_FILENAME]  # type: ignore[union-attr]
    assert len(root_nodes) == 1
    adm = r.admission
    assert adm is not None
    assert adm.root_entry.entry_class.value == "root_entry"
    assert adm.root_entry.root_text == ROOT_TEXT
    assert adm.root_entry.root_provenance.kind == "envelope"  # type: ignore[union-attr]
    assert adm.entries == ()
    assert adm.entries_retained == 1
    assert adm.entry_source_bytes == len(ROOT_TEXT.encode("utf-8"))
    rows = {row.path: row for row in adm.path_associations}
    assert set(rows) == {ROOT_FILENAME}
    assert rows[ROOT_FILENAME].is_root is True
    assert rows[ROOT_FILENAME].content_keys == (adm.root_entry.content_key,)
    # No partial state, no mutation, exact identity on every object.
    assert r.state is s0
    assert s0.revision == 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_genuine_refresh_read_composition(mode: Any, endpoint: str) -> None:
    """A: a genuine issued READ refresh re-selects the current root
    from the ACTUAL selected witness occurrence in the SAME D state:
    READ provenance re-binds occurrence/call/endpoint, the root entry
    carries the exact retained read bytes, and the original anchor,
    envelope fact and selection identity all stay unchanged."""
    ns, s0 = bootstrap(mode, "i-a-refresh")
    s2 = refreshed(s0, ns, "r1", endpoint, NEW_ROOT)
    occ = occurrences(s2, "r1")[0]
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    assert r.selected_root_provenance.kind == "read"  # type: ignore[union-attr]
    assert r.selected_root_provenance.occurrence_id == occ.occurrence_id  # type: ignore[union-attr]
    assert r.selected_root_provenance.call_id == "r1"  # type: ignore[union-attr]
    assert r.selected_root_provenance.endpoint == endpoint  # type: ignore[union-attr]
    assert r.selected_root_source_byte_length == len(NEW_ROOT.encode("utf-8"))
    assert r.graph.root_digest == sha(NEW_ROOT)  # type: ignore[union-attr]
    adm = r.admission
    assert adm is not None
    assert adm.root_entry.root_text == NEW_ROOT
    assert adm.root_entry.root_provenance.kind == "read"  # type: ignore[union-attr]
    # The selected root read is a proven same-bytes root-path read:
    # the accepted G law admits it as the ordinary AGENTS.md file
    # entry under the SELECTED governing digest (its anchor row
    # keeps its own distinct root-entry key); B.md is referenced
    # but never read, so it mints no entry.
    assert len(adm.entries) == 1
    root_read_entry = adm.entries[0]
    assert root_read_entry.key_record.member_occurrences == (ROOT_FILENAME,)
    assert root_read_entry.key_record.root_digest == sha(NEW_ROOT)
    assert root_read_entry.key_record.aggregate_source_digest == sha(NEW_ROOT)
    assert root_read_entry.proof is occ.proof
    assert ("B.md",) not in i_members_of(adm)
    # Original identities preserved by reference.
    assert s2.d_state.root is s0.d_state.root
    assert envelope_fact(s2) in s2.root_facts
    assert r.selection is not None
    assert r.selection.selected_source_digest == sha(NEW_ROOT)
    assert r.selection.witness_facts[0] is read_fact(s2, "r1")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_refresh_then_genuine_revert(mode: Any, endpoint: str) -> None:
    """A: v1 bootstrap -> descendant v2 -> genuine descendant v1
    revert: the composition follows the causal maximal authoritative
    fact (v1 READ provenance again) while the anchor stays immutable
    and both retained read facts stay in the H state."""
    ns, s0 = bootstrap(mode, "i-a-revert")
    anchor = s0.d_state.root
    assert anchor is not None
    s2 = refreshed(s0, ns, "r1", endpoint, NEW_ROOT)
    occ2 = occurrences(s2, "r1")[0]
    s5 = refreshed(s2, ns, "r2", endpoint, ROOT_TEXT, parent=occ2.occurrence_id)
    r = derive(s5, ns)
    assert_i_ok(r, s5)
    assert r.selected_root_provenance.kind == "read"  # type: ignore[union-attr]
    assert r.selected_root_provenance.call_id == "r2"  # type: ignore[union-attr]
    assert r.graph.root_digest == sha(ROOT_TEXT)  # type: ignore[union-attr]
    assert r.admission is not None
    assert r.admission.root_entry.root_text == ROOT_TEXT
    # The reverted read is a proven same-bytes root-path read: it
    # admits the ordinary AGENTS.md file entry under the reverted
    # governing digest (accepted G law); no other read exists.
    assert len(r.admission.entries) == 1
    reverted_entry = r.admission.entries[0]
    assert reverted_entry.key_record.member_occurrences == (ROOT_FILENAME,)
    assert reverted_entry.key_record.root_digest == sha(ROOT_TEXT)
    assert reverted_entry.key_record.aggregate_source_digest == sha(ROOT_TEXT)
    assert s5.d_state.root is anchor
    assert len(s5.root_facts) == 3
    assert r.selection is not None
    assert r.selection.witness_facts[0] is read_fact(s5, "r2")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_rootless_continuation_keeps_selection(mode: Any, endpoint: str) -> None:
    """A: rootless nonroot reads after a refresh are retained without
    promotion: the current root selection and the selected source
    stay exact, the previously referenced file entry is withdrawn
    (the new root no longer references it) and an unproven
    nonroot read emits the fixed admission reason, never authority."""
    ns, s0 = bootstrap(mode, "i-a-rootless")
    s1 = nonroot_read(s0, ns, "a1", endpoint, "Synthetic A body.\n", "cat A.md")
    r1 = derive(s1, ns)
    assert_i_ok(r1, s1)
    assert r1.admission is not None
    assert set(i_members_of(r1.admission)) == {(ROOT_FILENAME, "A.md"), ("A.md",)} or (
        ("A.md",) in i_members_of(r1.admission)
    )
    assert ("A.md",) in i_members_of(r1.admission)
    s2 = refreshed(s1, ns, "r1", endpoint, NEW_ROOT)
    s3 = nonroot_read(s2, ns, "c1", endpoint, "Unrelated bytes.", "cat C1.md")
    r3 = derive(s3, ns)
    assert_i_ok(r3, s3)
    assert r3.selected_root_provenance.call_id == "r1"  # type: ignore[union-attr]
    assert r3.graph.root_digest == sha(NEW_ROOT)  # type: ignore[union-attr]
    adm = r3.admission
    assert adm is not None
    by = i_members_of(adm)
    assert ("A.md",) not in by  # withdrawn: the new root does not reference A.md
    assert ("C1.md",) not in by  # unproven: referenced by no current supplier
    assert adm.emitted_admission_reasons == 1
    assert adm.admission_reasons == (CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,)
    assert r3.diagnostics == ()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_envelope_replays_after_refresh(mode: Any, endpoint: str) -> None:
    """A: exact-old, shifted-old and known-new envelopes all replay
    as exact prior-state no-ops after a genuine refresh, and the
    composition is byte-for-byte identical across the no-ops (no new
    facts, no selection change, no derived drift)."""
    ns, s0 = bootstrap(mode, "i-a-replay")
    s2 = refreshed(s0, ns, "r1", endpoint, NEW_ROOT)
    r1 = derive(s2, ns)
    for replay in (
        root_request(),
        shifted_root_envelope(),
        changed_root_envelope(NEW_ROOT),
    ):
        t = observe_root_lineage(s2, ns, s2.revision, (replay,))
        assert t.outcome is RootLineageOutcome.REPLAYED, t.diagnostics
        assert t.state is s2
    r2 = derive(s2, ns)
    assert r1.model_dump() == r2.model_dump()
    assert r2.state is s2


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_unknown_changed_envelope_refused_whole(mode: Any, endpoint: str) -> None:
    """A: an unknown changed envelope WITHOUT independent same-batch
    accepted root-read authority refuses the whole H transition with
    the EXACT prior state (the D layer replays; the H envelope-
    authority law refuses the composition); the prior state still
    composes OK with the unchanged selection."""
    ns, s0 = bootstrap(mode, "i-a-unknown")
    s2 = refreshed(s0, ns, "r1", endpoint, NEW_ROOT)
    unknown = "Unknown changed root body."
    t = observe_root_lineage(s2, ns, s2.revision, (changed_root_envelope(unknown),))
    assert t.outcome is RootLineageOutcome.REFUSED_ROOT_AUTHORITY
    assert t.state is s2
    assert t.diagnostics == (RootLineageLimitation.ENVELOPE_UNPROVEN,)
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    assert r.selected_root_provenance.call_id == "r1"  # type: ignore[union-attr]
    assert r.graph.root_digest == sha(NEW_ROOT)  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# B. Root edge withdrawal, cycle-only loss, alternates, restoration
# ---------------------------------------------------------------------------


def _start_read(
    state: RootLineageState,
    ns: RootLineageNamespace,
    call_id: str,
    endpoint: str,
    body: str,
) -> RootLineageState:
    return nonroot_read(state, ns, call_id, endpoint, body, "cat Start.md")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_withdrawal_and_restoration(mode: Any, endpoint: str) -> None:
    """B: Root->Start; Start-v1->B; B->C; C->E.  A descendant
    COMPLETE-EMPTY Start-v2 withdraws the outgoing derivations: B and
    C stay possessed but UNADMITTED; the exact old Start-v1 replay is
    a no-op that restores nothing; a genuinely descendant Start-v3
    restores the entries from the SAME retained B/C originals (no new
    downstream acquisition; original proof identity and witnesses
    kept)."""
    ns = h_ns(mode, "i-b-wd")
    s0 = h_bootstrap(ns, rooted("Read `Start.md` first."))
    s1 = _start_read(s0, ns, "c-start1", endpoint, "See `B.md`.")
    s1 = nonroot_read(s1, ns, "c-b", endpoint, "See `C.md`.", "cat B.md")
    s1 = nonroot_read(s1, ns, "c-c", endpoint, "See `E.md`.", "cat C.md")
    b_occ = occurrences(s1, "c-b")[0].occurrence_id
    c_occ = occurrences(s1, "c-c")[0].occurrence_id
    r1 = derive(s1, ns)
    assert_i_ok(r1, s1)
    by1 = i_members_of(r1.admission)
    assert set(by1) == {("Start.md",), ("B.md",), ("C.md",)}
    assert by1[("B.md",)].witnesses[0].occurrence_id == b_occ
    assert by1[("C.md",)].witnesses[0].occurrence_id == c_occ
    # The descendant EMPTY Start-v2 withdraws the outgoing derivations.
    start1_occ = occurrences(s1, "c-start1")[0].occurrence_id
    s2 = refreshed(
        s1,
        ns,
        "c-start2",
        endpoint,
        "",
        parent=start1_occ,
        args=json.dumps({"cmd": "cat Start.md"}),
        cmd="cat Start.md",
    )
    r2 = derive(s2, ns)
    assert_i_ok(r2, s2)
    by2 = i_members_of(r2.admission)
    assert set(by2) == {("Start.md",)}
    assert by2[("Start.md",)].key_record.aggregate_source_digest == EMPTY_SOURCE_SHA256
    assert (
        by2[("Start.md",)].witnesses[0].occurrence_id
        == occurrences(s2, "c-start2")[0].occurrence_id
    )
    assert r2.admission is not None
    # The withdrawn B/C reads stay retained but unadmitted: exactly
    # ONE fixed candidate_unproven reason (accepted G law).
    assert r2.admission.emitted_admission_reasons == 1
    assert r2.admission.admission_reasons == (CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,)
    # The exact original Start-v1 replay is a pure no-op.
    t = observe_root_lineage(
        s2, ns, s2.revision, (read_request(endpoint, "c-start1", "See `B.md`.", "cat Start.md"),)
    )
    assert t.outcome is RootLineageOutcome.REPLAYED
    assert t.state is s2
    r2b = derive(s2, ns)
    assert r2.model_dump() == r2b.model_dump()
    # The genuinely descendant Start-v3 restores from the SAME retained originals.
    start2_occ = occurrences(s2, "c-start2")[0].occurrence_id
    before = len(s2.d_state.occurrences)
    s3 = refreshed(
        s2,
        ns,
        "c-start3",
        endpoint,
        "See `B.md`.",
        parent=start2_occ,
        args=json.dumps({"cmd": "cat Start.md"}),
        cmd="cat Start.md",
    )
    r3 = derive(s3, ns)
    assert_i_ok(r3, s3)
    by3 = i_members_of(r3.admission)
    assert set(by3) == {("Start.md",), ("B.md",), ("C.md",)}
    assert by3[("B.md",)].witnesses[0].occurrence_id == b_occ
    assert by3[("C.md",)].witnesses[0].occurrence_id == c_occ
    assert len(s3.d_state.occurrences) == before + 1
    b_proof = next(o.proof for o in s3.d_state.occurrences if o.occurrence_id == b_occ)
    assert by3[("B.md",)].proof is b_proof
    assert by3[("B.md",)].key_record.aggregate_source_digest == sha("See `C.md`.")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_alternate_preservation(mode: Any, endpoint: str) -> None:
    """B: an independent surviving COMPLETE alternate keeps
    reachability after a withdrawal, while the cycle-only descendant
    (reachable only through the withdrawn edge) is lost.  Root
    references Start.md AND B.md directly; Start->C only."""
    ns = h_ns(mode, "i-b-alt")
    s0 = h_bootstrap(ns, rooted("Read `Start.md` and `B.md` first."))
    s1 = _start_read(s0, ns, "c-start1", endpoint, "See `C.md`.")
    s1 = nonroot_read(s1, ns, "c-b", endpoint, "B body.\n", "cat B.md")
    s1 = nonroot_read(s1, ns, "c-c", endpoint, "C body.\n", "cat C.md")
    r1 = derive(s1, ns)
    assert_i_ok(r1, s1)
    assert set(i_members_of(r1.admission)) == {("Start.md",), ("B.md",), ("C.md",)}
    start1_occ = occurrences(s1, "c-start1")[0].occurrence_id
    s2 = refreshed(
        s1,
        ns,
        "c-start2",
        endpoint,
        "",
        parent=start1_occ,
        args=json.dumps({"cmd": "cat Start.md"}),
        cmd="cat Start.md",
    )
    r2 = derive(s2, ns)
    assert_i_ok(r2, s2)
    by2 = i_members_of(r2.admission)
    assert set(by2) == {("Start.md",), ("B.md",)}  # C is cycle-only: lost
    assert by2[("B.md",)].witnesses[0].occurrence_id == occurrences(s2, "c-b")[0].occurrence_id
    assert r2.admission is not None
    # C.md stays retained but unadmitted (cycle-only): exactly ONE
    # fixed candidate_unproven reason (accepted G law).
    assert r2.admission.emitted_admission_reasons == 1
    assert r2.admission.admission_reasons == (CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,)


# ---------------------------------------------------------------------------
# C. Canonical keys against the independent original-C oracle
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_canonical_keys_vs_old_c_oracle(mode: Any, endpoint: str) -> None:
    """C: the I canonical keys ARE the ACTUAL 018-c semantic keys:
    under ONE shared admission namespace, the old-C batch admission
    over the SAME actual original-API root + read requests and the I
    derivation over the actual retained H history agree on the exact
    root key record, the exact file key-record mapping and the
    reverse member index, and the I entries retain the ORIGINAL proof
    by identity."""
    ns, s0 = bootstrap(mode, "i-c-oracle")
    s1 = nonroot_read(s0, ns, "c1", endpoint, "Synthetic file content.\n")
    r = derive(s1, ns)
    assert_i_ok(r, s1)
    # The ACTUAL 018-c admission namespace the I derivation re-derives
    # from the H scope: the identical actual identity/model/fingerprint/
    # workspace/mode fields (the D lineage ID is a history-level
    # identity, never an admission field).
    adm_ns = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-history-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
    )
    requests = (
        root_request(),
        read_request(endpoint, "c1", "Synthetic file content.\n"),
    )
    old = observe_bundle_admission_batch(requests, adm_ns)
    assert old.outcome.value == "complete"
    adm = r.admission
    assert adm is not None
    assert old.root_entry is not None
    assert adm.root_entry.key_record == old.root_entry.key_record
    old_records = {e.content_key: e.key_record for e in old.entries}
    new_records = {e.content_key: e.key_record for e in adm.entries}
    assert old_records == new_records
    occurrence = s1.d_state.occurrences[-1]
    assert all(e.proof is occurrence.proof for e in adm.entries)
    old_rows = {row.path: set(row.content_keys) for row in old.path_associations}
    new_rows = {row.path: set(row.content_keys) for row in adm.path_associations}
    assert old_rows == new_rows


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_changed_governing_root_changes_keys(mode: Any, endpoint: str) -> None:
    """C: unchanged nonroot source under a CHANGED governing root
    gets the correct changed governing key (the semantic key binds
    the selected root digest): the same retained A.md source has a
    DIFFERENT content key under v1 and v2 roots while its source
    digest stays exact."""
    v2 = "Read `A.md` and `B.md` after the refresh."
    ns, s0 = bootstrap(mode, "i-c-gov")
    s1 = nonroot_read(s0, ns, "a1", endpoint, "Synthetic A body.\n")
    r1 = derive(s1, ns)
    assert_i_ok(r1, s1)
    kr1 = i_members_of(r1.admission)[("A.md",)].key_record
    assert kr1.root_digest == sha(ROOT_TEXT)
    assert kr1.aggregate_source_digest == sha("Synthetic A body.\n")
    s2 = refreshed(s1, ns, "r1", endpoint, v2)
    r2 = derive(s2, ns)
    assert_i_ok(r2, s2)
    kr2 = i_members_of(r2.admission)[("A.md",)].key_record
    assert kr2.root_digest == sha(v2)
    assert kr2.aggregate_source_digest == sha("Synthetic A body.\n")
    assert kr1.content_key != kr2.content_key
    assert r2.graph.root_digest == sha(v2)  # type: ignore[union-attr]
    # B.md is referenced by the new root but never read: unproven.
    assert ("B.md",) not in i_members_of(r2.admission)
    assert r2.admission is not None
    # B.md was never READ, so it is a graph-availability fact, not a
    # retained unadmitted read candidate: no admission reason is
    # emitted (accepted G law: the reason names a proven unadmitted
    # candidate, an unread reference stays an availability state).
    assert r2.admission.emitted_admission_reasons == 0


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_equal_byte_witness_change_no_false_semantic_miss(mode: Any, endpoint: str) -> None:
    """C: equal-byte source/provenance WITNESS changes (a second
    equal-byte maximal read with a different occurrence/provenance)
    must not invent a semantic key change: the root entry content key
    and the governing digest are byte-identical across the two
    selections, and both original witness facts are retained."""
    ns, s0 = bootstrap(mode, "i-c-equal")
    s1 = refreshed(s0, ns, "r1", endpoint, NEW_ROOT)
    r1 = derive(s1, ns)
    assert_i_ok(r1, s1)
    assert len(r1.selection.witness_facts) == 1  # type: ignore[union-attr]
    key1 = r1.admission.root_entry.content_key  # type: ignore[union-attr]
    s2 = refreshed(s1, ns, "r2", endpoint, NEW_ROOT)
    r2 = derive(s2, ns)
    assert_i_ok(r2, s2)
    assert r2.graph.root_digest == sha(NEW_ROOT)  # type: ignore[union-attr]
    assert r2.admission.root_entry.content_key == key1  # type: ignore[union-attr]
    assert len(r2.selection.witness_facts) == 2  # type: ignore[union-attr]
    assert read_fact(s2, "r1") in s2.root_facts
    assert read_fact(s2, "r2") in s2.root_facts
    # Single first-class ROOT_ENTRY: equal maxima never split the root.
    assert (
        len(
            [
                e
                for e in (r2.admission.root_entry, *r2.admission.entries)  # type: ignore[union-attr]
                if e.entry_class.value == "root_entry"
            ]
        )
        == 1
    )


# ---------------------------------------------------------------------------
# D. Selection extrema through the composition
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_incomparable_siblings_conflict_no_fallback(mode: Any, endpoint: str) -> None:
    """D: differing incomparable maximal root reads are an explicit
    authoritative conflict: the composition carries the ACTUAL
    selection, refuses whole with NO selected source, NO ready
    graph/admission and NEVER a bootstrap fallback, on the EXACT
    input state."""
    ns, s0 = bootstrap(mode, "i-d-conflict")
    s2 = refreshed(s0, ns, "wx", endpoint, SIBLING_X)
    s4 = refreshed(s2, ns, "wy", endpoint, SIBLING_Y)
    r = derive(s4, ns)
    assert_i_refused(r, s4, _OUT.REFUSED_ROOT_CONFLICT, (_L.ROOT_CONFLICT,))
    assert r.selection is not None
    assert r.selection.outcome is RootSelectionOutcome.ROOT_CONTENT_CONFLICT
    assert r.selection.selected_source_digest is None
    assert len(r.selection.witness_facts) == 2
    assert r.state is s4


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_child_of_one_then_child_of_all_resolves(mode: Any, endpoint: str) -> None:
    """D: a child of ONE branch cannot causally dominate the other
    (the conflict persists with the two actual branch maxima); a
    genuine child of ALL branches -- actual ancestry, not equal
    bytes, not arrival order -- resolves to the SOLE maximal witness
    and the composition composes OK under it; every staled branch
    fact stays retained."""
    ns, s0 = bootstrap(mode, "i-d-child")
    s2 = refreshed(s0, ns, "wx", endpoint, SIBLING_X)
    occ_x = occurrences(s2, "wx")[0]
    s4 = refreshed(s2, ns, "wy", endpoint, SIBLING_Y)
    occ_y = occurrences(s4, "wy")[0]
    r_mid = derive(s4, ns)
    assert_i_refused(r_mid, s4, _OUT.REFUSED_ROOT_CONFLICT, (_L.ROOT_CONFLICT,))
    s6 = refreshed(s4, ns, "z1", endpoint, SIBLING_Z, parent=occ_x.occurrence_id)
    r1 = derive(s6, ns)
    assert_i_refused(r1, s6, _OUT.REFUSED_ROOT_CONFLICT, (_L.ROOT_CONFLICT,))
    assert r1.selection is not None
    assert len(r1.selection.witness_facts) == 2  # the z1 branch and the wy branch
    occ_z1 = occurrences(s6, "z1")[0]
    # z2 must be issued under BOTH the z1 occurrence AND the wy
    # occurrence: the issue() helper takes ONE frontier tuple.
    t7 = issue(s6, ns, "z2", endpoint, (occ_z1.occurrence_id, occ_y.occurrence_id))
    assert t7.outcome is RootLineageOutcome.ACCEPTED
    t8 = observe_root_lineage(
        t7.state, ns, t7.state.revision, (read_request(endpoint, "z2", SIBLING_Z, "cat AGENTS.md"),)
    )
    assert t8.outcome is RootLineageOutcome.ACCEPTED
    s8 = t8.state
    r2 = derive(s8, ns)
    assert_i_ok(r2, s8)
    assert r2.selected_root_provenance.call_id == "z2"  # type: ignore[union-attr]
    assert r2.graph.root_digest == sha(SIBLING_Z)  # type: ignore[union-attr]
    assert r2.selection is not None
    assert len(r2.selection.witness_facts) == 1
    assert r2.selection.witness_facts[0] is read_fact(s8, "z2")
    assert read_fact(s8, "wx") in s8.root_facts
    assert read_fact(s8, "wy") in s8.root_facts
    assert read_fact(s8, "z1") in s8.root_facts
    assert len(s8.root_facts) == 5


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_equal_byte_siblings_compatible(mode: Any, endpoint: str) -> None:
    """D: valid equal maxima stay compatible: ALL original witness
    facts are retained and the composition composes OK under the
    single governing root (one ROOT_ENTRY, never a second root)."""
    ns, s0 = bootstrap(mode, "i-d-equal")
    s1 = refreshed(s0, ns, "r1", endpoint, SIBLING_X)
    s2 = refreshed(s1, ns, "r2", endpoint, SIBLING_X)
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    assert r.graph.root_digest == sha(SIBLING_X)  # type: ignore[union-attr]
    assert r.selection is not None
    assert len(r.selection.witness_facts) == 2
    assert read_fact(s2, "r1") in s2.root_facts
    assert read_fact(s2, "r2") in s2.root_facts


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_delayed_older_receipt_keeps_current(mode: Any, endpoint: str) -> None:
    """D: a causally OLDER root read (observed unissued) ordered
    before the current one by ACTUAL issuance ancestry: the current
    read is the sole selected maximum; replaying the older original
    read is an exact no-op; the LATE matching older receipt earns
    older authority WITHOUT rolling the current selection back; all
    original proofs and the anchor stay exact."""
    ns, s0 = bootstrap(mode, "i-d-delayed")
    t1 = observe_root_lineage(
        s0, ns, s0.revision, (read_request(endpoint, "r1-old", UNPROVEN_BODY, "cat AGENTS.md"),)
    )
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    s1 = t1.state
    r1_occ = occurrences(s1, "r1-old")[0]
    # The current read's frozen frontier names BOTH the bootstrap
    # root fact (proven ancestry) and the older unissued read
    # occurrence (the older read is BEFORE the current one by the
    # actual frozen parent edge).
    s3 = refreshed(
        s1,
        ns,
        "r2-cur",
        endpoint,
        NEW_ROOT,
        parent=(CAUSAL_ROOT_FACT, r1_occ.occurrence_id),
    )
    r2_occ = occurrences(s3, "r2-cur")[0]
    r1 = derive(s3, ns)
    assert_i_ok(r1, s3)
    assert r1.selected_root_provenance.call_id == "r2-cur"  # type: ignore[union-attr]
    assert r1.selection is not None
    assert len(r1.selection.witness_facts) == 1
    # The original older read replays as an exact no-op.
    t4 = observe_root_lineage(
        s3, ns, s3.revision, (read_request(endpoint, "r1-old", UNPROVEN_BODY, "cat AGENTS.md"),)
    )
    assert t4.outcome is RootLineageOutcome.REPLAYED
    assert t4.state is s3
    # The late matching older receipt earns older authority...
    t5 = receipt(s3, ns, "r1-old", endpoint, (CAUSAL_ROOT_FACT,))
    assert t5.outcome is RootLineageOutcome.ACCEPTED
    s5 = t5.state
    assert read_fact(s5, "r1-old").authority is True
    assert read_fact(s5, "r2-cur").authority is True
    # ...yet the current read stays the SOLE selected maximum.
    r2 = derive(s5, ns)
    assert_i_ok(r2, s5)
    assert r2.selected_root_provenance.call_id == "r2-cur"  # type: ignore[union-attr]
    assert r2.graph.root_digest == sha(NEW_ROOT)  # type: ignore[union-attr]
    assert r2.selection is not None
    assert len(r2.selection.witness_facts) == 1
    assert r2.selection.witness_facts[0] is read_fact(s5, "r2-cur")
    assert occurrences(s5, "r1-old")[0].proof is r1_occ.proof
    assert occurrences(s5, "r2-cur")[0].proof is r2_occ.proof
    assert s5.d_state.root is s0.d_state.root
    assert len(s5.root_facts) == 3


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_late_nonroot_ancestor_authority(mode: Any, endpoint: str) -> None:
    """D: an UNISSUED nonroot read gives the ISSUED descendant root
    read no bootstrap ancestry until a LATE matching nonroot receipt
    lands: before it the composition selects the bootstrap with the
    fixed ROOT_SOURCE_UNPROVEN limitation surfaced EXACTLY; after it
    the re-derivation mints the descendant's authority and the
    composition follows it, with the anchor and the original root
    proof identity exact."""
    X = "Nonroot ancestor source."
    ns, s0 = bootstrap(mode, "i-d-late")
    anchor = s0.d_state.root
    assert anchor is not None
    t1 = observe_root_lineage(
        s0, ns, s0.revision, (read_request(endpoint, "late-x", X, "cat X.md"),)
    )
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    s1 = t1.state
    xocc = occurrences(s1, "late-x")[0]
    t2 = issue(s1, ns, "descendant-root", endpoint, (xocc.occurrence_id,))
    assert t2.outcome is RootLineageOutcome.ACCEPTED
    t3 = observe_root_lineage(
        t2.state,
        ns,
        t2.state.revision,
        (read_request(endpoint, "descendant-root", NEW_ROOT, "cat AGENTS.md"),),
    )
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    s3 = t3.state
    rocc = occurrences(s3, "descendant-root")[0]
    r1 = derive(s3, ns)
    assert_i_ok(r1, s3)
    assert r1.graph.root_digest == sha(ROOT_TEXT)  # type: ignore[union-attr]
    assert r1.selected_root_provenance.kind == "envelope"  # type: ignore[union-attr]
    assert r1.diagnostics == (_L.ROOT_SOURCE_UNPROVEN,)
    # The late matching nonroot receipt re-derives the authority.
    t4 = register_root_receipt(
        s3,
        ns,
        "late-x",
        endpoint,
        "exec_command",
        json.dumps({"cmd": "cat X.md"}),
        (CAUSAL_ROOT_FACT,),
        s3.revision,
    )
    assert t4.outcome is RootLineageOutcome.ACCEPTED
    s4 = t4.state
    r2 = derive(s4, ns)
    assert_i_ok(r2, s4)
    assert r2.selected_root_provenance.call_id == "descendant-root"  # type: ignore[union-attr]
    assert r2.graph.root_digest == sha(NEW_ROOT)  # type: ignore[union-attr]
    assert r2.diagnostics == ()
    assert read_fact(s4, "descendant-root").authority is True
    assert s4.d_state.root is anchor
    assert occurrences(s4, "descendant-root")[0].proof is rocc.proof
    assert read_fact(s3, "descendant-root").authority is False


@pytest.mark.parametrize("mode", MODES)
def test_d_no_selected_root_refusal_shape_constructor_only(mode: Any) -> None:
    """D (CONSTRUCTOR-ONLY, labeled): the closed result law accepts
    the authoritative no-selected-root refusal carrying the actual
    selection and no partial output.  Public acquisition always
    bootstraps an authoritative anchor, so the no_selected_root
    shape is structurally unreachable through the original public
    API; this is model-law evidence, not public evidence."""
    ns, s0 = bootstrap(mode, "i-d-noselect")
    sel = RootSelectionResult(
        outcome=RootSelectionOutcome.NO_SELECTED_ROOT,
        limitations=(),
        lineage_key=ns.lineage_key,
        revision=s0.revision,
    )
    r = CurrentRootComposition(
        outcome=_OUT.REFUSED_ROOT_CONFLICT,
        state=s0,
        selection=sel,
        diagnostics=(_L.ROOT_CONFLICT,),
    )
    assert r.state is s0
    assert r.graph is None
    assert r.admission is None
    assert r.selected_root_provenance is None
    # An OK result can never carry a no-selected-root selection.
    with pytest.raises(ValidationError):
        CurrentRootComposition(
            outcome=_OUT.OK,
            state=s0,
            selection=sel,
        )


# ---------------------------------------------------------------------------
# E. Current/old root reads, proven segments, root-bearing bundles
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_current_and_staled_root_reads(mode: Any, endpoint: str) -> None:
    """E: after a descendant refresh the OLD root read stays retained
    (staled, never deleted) while the composition selects the CURRENT
    root: the old read mints no root entry, the root entry carries
    the current read bytes, and the original proof identities are
    exact."""
    v3 = "Read `C.md` third."
    ns, s0 = bootstrap(mode, "i-e-cur")
    s1 = refreshed(s0, ns, "r1", endpoint, NEW_ROOT)
    occ1 = occurrences(s1, "r1")[0]
    s2 = refreshed(s1, ns, "r2", endpoint, v3, parent=occ1.occurrence_id)
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    assert r.selected_root_provenance.call_id == "r2"  # type: ignore[union-attr]
    assert r.graph.root_digest == sha(v3)  # type: ignore[union-attr]
    assert r.admission.root_entry.root_text == v3  # type: ignore[union-attr]
    # The CURRENT root read is a proven same-bytes root-path read:
    # it admits the ordinary AGENTS.md file entry under the current
    # digest (accepted G law); the OLD r1 read stays retained (never
    # deleted) but mints no CURRENT entry under the new digest.
    assert len(r.admission.entries) == 1  # type: ignore[union-attr]
    cur_entry = r.admission.entries[0]  # type: ignore[union-attr]
    assert cur_entry.key_record.member_occurrences == (ROOT_FILENAME,)
    assert cur_entry.key_record.aggregate_source_digest == sha(v3)
    assert cur_entry.proof is occurrences(s2, "r2")[0].proof
    # Authority is a DERIVED provenance property, not a selection
    # property: r1 was issued and anchored to the bootstrap, so its
    # re-derived flags stay True even though r2 now holds the causal
    # maximum.  "Staled" here means the old read no longer supplies
    # the current root; the fact is retained with its original proof
    # identity and its derived authority.
    assert read_fact(s2, "r1").authority is True  # retained, still proven
    assert read_fact(s2, "r1") in s2.root_facts
    assert read_fact(s2, "r2") in s2.root_facts
    assert occurrences(s2, "r1")[0].proof is occ1.proof


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_proven_matching_root_segment_whole_bundle(mode: Any, endpoint: str) -> None:
    """E: a proven AGENTS.md segment inside a larger bundle that
    AGREES with the current root source is a supported segmented
    ORDINARY proof: the whole bundle (both members independently
    CURRENT and eligible, the root segment proven compatible) is
    admissible in BOTH modes as ONE entry with both members and the
    segments proven; NO read root fact is minted, the bootstrap
    remains the current selection, and the root path is never a
    singleton file entry (its file entry keeps its own key under
    the selected digest)."""
    A_TEXT = "Alpha file text.\n"
    MARK = "PARTM"
    cmd = f"cat A.md && echo '{MARK}' && cat AGENTS.md"
    body = A_TEXT + MARK + "\n" + ROOT_TEXT
    ns, s0 = bootstrap(mode, "i-e-part")
    t1 = issue(s0, ns, "pm", endpoint, (CAUSAL_ROOT_FACT,), args=json.dumps({"cmd": cmd}))
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage(
        t1.state, ns, t1.state.revision, (read_request(endpoint, "pm", body, cmd),)
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED
    s2 = t2.state
    occ = occurrences(s2, "pm")[0]
    assert len(occ.proof.segments) == 2
    assert occ.proof.segments[0].member_digest == sha(A_TEXT)
    assert occ.proof.segments[1].member_digest == sha(ROOT_TEXT)
    assert not any(
        f.provenance.kind == "read" and f.provenance.call_id == "pm" for f in s2.root_facts
    )
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    assert r.selected_root_provenance.kind == "envelope"  # type: ignore[union-attr]
    assert r.graph.root_digest == sha(ROOT_TEXT)  # type: ignore[union-attr]
    adm = r.admission
    by = i_members_of(adm)
    assert set(by) == {("A.md", ROOT_FILENAME)}
    whole = by[("A.md", ROOT_FILENAME)]
    assert whole.proof is occ.proof
    assert whole.admitted_segments == (0, 1)
    assert whole.key_record.member_occurrences == ("A.md", ROOT_FILENAME)
    # the segments are proven with their own member digests
    assert occ.proof.segments[0].member_digest == sha(A_TEXT)  # type: ignore[union-attr]
    assert occ.proof.segments[1].member_digest == sha(ROOT_TEXT)  # type: ignore[union-attr]
    assert (ROOT_FILENAME,) not in by  # the root is never a singleton file entry


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_root_bearing_boundaryless_bundle_no_promotion(mode: Any, endpoint: str) -> None:
    """E: a BOUNDARYLESS root-bearing bundle whose root bytes AGREE
    with the current root is retained as an ordinary proof: the
    root-owned opaque region supplies NO root text and mints no root
    fact; the ROOT-BEARING OPAQUE group supplies NO entry at all in
    either mode (the accepted G truth-table exclusion; the fixed
    candidate_unproven reason is emitted); a genuinely newer
    independent A.md read (descendant of the bundle) later earns the
    current nonroot source from its OWN proven proof; the selection
    stays exact."""
    A_TEXT = "Alpha file text.\n"
    cmd = "cat A.md && cat AGENTS.md"
    body = A_TEXT + ROOT_TEXT
    ns, s0 = bootstrap(mode, "i-e-opaque")
    t1 = issue(s0, ns, "ob", endpoint, (CAUSAL_ROOT_FACT,), args=json.dumps({"cmd": cmd}))
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage(
        t1.state, ns, t1.state.revision, (read_request(endpoint, "ob", body, cmd),)
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED
    s2 = t2.state
    assert not any(
        f.provenance.kind == "read" and f.provenance.call_id == "ob" for f in s2.root_facts
    )
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    assert r.selected_root_provenance.kind == "envelope"  # type: ignore[union-attr]
    assert r.graph.root_digest == sha(ROOT_TEXT)  # type: ignore[union-attr]
    adm = r.admission
    # The root-bearing opaque group supplies NOTHING before entry
    # planning: no file entry in either mode, and the retained read
    # is the ONE fixed candidate_unproven reason (accepted G law).
    assert i_members_of(adm) == {}
    assert r.admission.admission_reasons == (CurrentAdmissionLimitation.CANDIDATE_UNPROVEN,)  # type: ignore[union-attr]
    # A genuinely newer independent A.md read (descendant of the
    # boundaryless bundle) earns the current nonroot source.
    ob_occ = occurrences(s2, "ob")[0]
    t3 = issue(
        s2,
        ns,
        "a1",
        endpoint,
        (ob_occ.occurrence_id,),
        args=json.dumps({"cmd": "cat A.md"}),
    )
    assert t3.outcome is RootLineageOutcome.ACCEPTED
    t4 = observe_root_lineage(
        t3.state, ns, t3.state.revision, (read_request(endpoint, "a1", A_TEXT, "cat A.md"),)
    )
    assert t4.outcome is RootLineageOutcome.ACCEPTED
    s3 = t4.state
    r3 = derive(s3, ns)
    assert_i_ok(r3, s3)
    assert r3.selected_root_provenance.kind == "envelope"  # type: ignore[union-attr]
    assert r3.graph.root_digest == sha(ROOT_TEXT)  # type: ignore[union-attr]
    assert not any(
        f.provenance.kind == "read" and f.provenance.call_id == "ob" for f in s3.root_facts
    )
    by3 = i_members_of(r3.admission)
    # The boundaryless root-owned group supplied NOTHING (its
    # unattributed root bytes can never be proven compatible); the
    # independently current eligible A.md read is admitted from its
    # OWN proven proof.
    assert set(by3) == {("A.md",)}
    assert by3[("A.md",)].proof is occurrences(s3, "a1")[0].proof
    assert by3[("A.md",)].key_record.aggregate_source_digest == sha(A_TEXT)
    assert (ROOT_FILENAME,) not in by3
    # The boundaryless bundle mints nothing by itself.
    by2 = i_members_of(adm)
    assert (ROOT_FILENAME,) not in by2
    assert by3[("A.md",)].proof is not occurrences(s3, "ob")[0].proof


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_competing_root_segment_refused_whole(mode: Any, endpoint: str) -> None:
    """E: a proven ISOLATED AGENTS.md segment that DISAGREES with the
    current root source is competing root evidence: the whole D
    candidate is atomically discarded with the EXACT prior state, no
    root authority is minted, and the prior state still composes OK
    (no partial output, no bootstrap fallback)."""
    A_TEXT = "Alpha file text.\n"
    COMPETING = "Competing root body.\n"
    MARK = "PARTM"
    cmd = f"cat A.md && echo '{MARK}' && cat AGENTS.md"
    body = A_TEXT + MARK + "\n" + COMPETING
    ns, s0 = bootstrap(mode, "i-e-compete")
    t1 = issue(s0, ns, "cp", endpoint, (CAUSAL_ROOT_FACT,), args=json.dumps({"cmd": cmd}))
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage(
        t1.state, ns, t1.state.revision, (read_request(endpoint, "cp", body, cmd),)
    )
    assert t2.outcome is RootLineageOutcome.REFUSED_ROOT_CONFLICT
    assert t2.state is t1.state
    assert t2.diagnostics == (RootLineageLimitation.COMPETING_ROOTS,)
    r = derive(t1.state, ns)
    assert_i_ok(r, t1.state)
    assert r.selected_root_provenance.kind == "envelope"  # type: ignore[union-attr]


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_i9_stale_root_segment_not_admitted(mode: Any, endpoint: str) -> None:
    """E (I9): after an issued v2 refresh, a descendant PROVEN
    A|AGENTS bundle containing the KNOWN OLD v1 root bytes grants no
    new root authority (H still selects v2) and I must NOT admit the
    stale root bytes as an eligible ordinary entry: the root
    compatibility filter uses the ACTUAL selected digest, never the
    bootstrap digest, while the lean nonroot segment still admits."""
    v2 = "Read `A.md` for the refresh."
    cmd = "cat A.md && echo 'ROOTSEP' && cat AGENTS.md"
    body = "Synthetic nonroot A.\nROOTSEP\n" + ROOT_TEXT
    ns, s0 = bootstrap(mode, "i-e-i9")
    s1 = refreshed(s0, ns, "fresh-root", endpoint, v2)
    root_fact = read_fact(s1, "fresh-root")
    t1 = issue(
        s1,
        ns,
        "mixed-old-root",
        endpoint,
        (root_fact.provenance.occurrence_id,),  # type: ignore[union-attr]
        args=json.dumps({"cmd": cmd}),
    )
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage(
        t1.state, ns, t1.state.revision, (read_request(endpoint, "mixed-old-root", body, cmd),)
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED
    s2 = t2.state
    sel = select_current_root(s2, ns)
    assert sel.outcome is RootSelectionOutcome.OK
    assert sel.selected_source_digest == sha(v2)
    assert not any(
        f.provenance.kind == "read" and f.provenance.call_id == "mixed-old-root"
        for f in s2.root_facts
    )
    occurrence = next(o for o in s2.d_state.occurrences if o.call_id == "mixed-old-root")
    assert len(occurrence.proof.segments) == 2
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    assert r.graph.root_digest == sha(v2)  # type: ignore[union-attr]
    adm = r.admission
    for entry in adm.entries:  # type: ignore[union-attr]
        if entry.proof is occurrence.proof:
            for pos in entry.admitted_segments:
                seg = occurrence.proof.segments[pos]
                members = [
                    occurrence.proof.requested_members[m].normalized for m in seg.member_positions
                ]
                assert "AGENTS.md" not in members or seg.member_digest == sha(v2), (
                    "the stale old root bytes must not be admitted as an ordinary member"
                )
    if mode is AdmissionMode.LEAN:
        assert ("A.md",) in i_members_of(adm)
    else:
        # Greedy admits NO isolated segment (accepted G law): the
        # whole A|AGENTS bundle is not admitted because its
        # root-bearing segment carries the stale root bytes, and no
        # new greedy isolation rule admits the A.md segment alone.
        assert ("A.md",) not in i_members_of(adm)
    # The selected root read itself is a proven same-bytes root-path
    # read: it admits the ordinary AGENTS.md entry under the SELECTED
    # digest (accepted G law) -- never the stale v1 root bytes.
    for entry in adm.entries:  # type: ignore[union-attr]
        for pos in entry.admitted_segments:
            seg = entry.proof.segments[pos]  # type: ignore[union-attr]
            members = [entry.proof.requested_members[m].normalized for m in seg.member_positions]  # type: ignore[union-attr]
            if "AGENTS.md" in members:
                assert seg.member_digest == sha(v2)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_i9_post_refresh_new_root_mixed_bundle_unreached(mode: Any, endpoint: str) -> None:
    """E (I9, DOCUMENTED LIMITATION -- whole-018 rework implication):
    after an issued refresh to a v2 root that references A.md, a
    descendant proven A|AGENTS bundle whose root bytes EQUAL the
    selected v2 digest is UNREACHABLE through the original public H
    acquisition: the retained D anchor is still the bootstrap
    envelope, so the changed root-path bytes are a competing-root
    refusal at the ACTUAL unmodified D/H boundary BEFORE the I
    derivation.  The refusal is atomic and exact (prior state, no
    new occurrence, no partial output) and the prior state still
    composes OK under the selected v2 root.  No old H public refusal
    is broadened here; the positive mixed-bundle-under-a-refreshed
    root stays a mandatory later-stage rework obligation."""
    v2 = "Read `A.md` for the refresh."
    cmd = "cat A.md && echo 'ROOTSEP' && cat AGENTS.md"
    body = "Synthetic nonroot A.\nROOTSEP\n" + v2
    ns, s0 = bootstrap(mode, "i-e-i9pos")
    s1 = refreshed(s0, ns, "fresh-root", endpoint, v2)
    root_fact = read_fact(s1, "fresh-root")
    t1 = issue(
        s1,
        ns,
        "mixed-new-root",
        endpoint,
        (root_fact.provenance.occurrence_id,),  # type: ignore[union-attr]
        args=json.dumps({"cmd": cmd}),
    )
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage(
        t1.state, ns, t1.state.revision, (read_request(endpoint, "mixed-new-root", body, cmd),)
    )
    # The unmodified D/H boundary refuses the changed root-path
    # bytes as competing-root evidence (the retained D anchor is the
    # bootstrap), atomically, with the EXACT prior state.
    assert t2.outcome is RootLineageOutcome.REFUSED_ROOT_CONFLICT
    assert t2.state is t1.state
    assert t2.diagnostics == (RootLineageLimitation.COMPETING_ROOTS,)
    assert not any(
        f.provenance.kind == "read" and f.provenance.call_id == "mixed-new-root"
        for f in t1.state.root_facts
    )
    assert not any(o.call_id == "mixed-new-root" for o in t1.state.d_state.occurrences)
    # The prior state still composes OK under the selected v2 root.
    r = derive(t1.state, ns)
    assert_i_ok(r, t1.state)
    assert r.graph.root_digest == sha(v2)  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# F. Native EXEC/poll, Unicode/CRLF, empty, unissued
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_native_exec_poll_completion(mode: Any, endpoint: str) -> None:
    """F: a supported native initial-EXEC/poll root chain earns a
    complete singleton root read: the composition selects the READ
    provenance over the full retained source, the producing poll
    stays bound to the ORIGINAL initial-EXEC owner, and the root
    entry carries the exact proven bytes."""
    part = "Read `B.md` for the refresh."
    ns, s0 = bootstrap(mode, "i-f-native")
    t1 = issue(s0, ns, "native1", endpoint, (CAUSAL_ROOT_FACT,))
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage(
        t1.state,
        ns,
        t1.state.revision,
        (root_chain(endpoint, "native1", part, poll_cid="native1p"),),
    )
    assert t2.outcome is RootLineageOutcome.ACCEPTED
    s2 = t2.state
    occ = occurrences(s2, "native1")[0]
    assert occ.proof.source_text == part
    assert read_fact(s2, "native1").authority is True
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    assert r.selected_root_provenance.call_id == "native1"  # type: ignore[union-attr]
    assert r.selected_root_source_byte_length == len(part.encode("utf-8"))
    assert r.graph.root_digest == sha(part)  # type: ignore[union-attr]
    assert r.admission.root_entry.root_text == part  # type: ignore[union-attr]


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_unicode_crlf_root_bytes(mode: Any, endpoint: str) -> None:
    """F: a Unicode/CRLF root refresh body is selected with the
    EXACT UTF-8 byte length (multi-byte characters counted by bytes,
    never characters) and the digest re-checked from the exact
    retained bytes."""
    body = "Read `B.md` — ünïcode\r\n second line."
    ns, s0 = bootstrap(mode, "i-f-unicode")
    s2 = refreshed(s0, ns, "r1", endpoint, body)
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    raw = body.encode("utf-8")
    assert r.selected_root_source_byte_length == len(raw)
    assert len(raw) != len(body)  # genuinely multi-byte
    assert r.graph.root_digest == sha(body)  # type: ignore[union-attr]
    assert r.admission.root_entry.root_text == body  # type: ignore[union-attr]
    assert r.admission.root_entry.root_source_byte_length == len(raw)  # type: ignore[union-attr]


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_empty_root_read_authoritative(mode: Any, endpoint: str) -> None:
    """F: an EMPTY root read is legal original evidence.  While
    unissued it is unproven (the envelope stays current with the
    fixed surfaced limitation); the valid matching LATE receipt
    makes the empty source authoritative and the composition selects
    sha(empty) with the zero-byte root entry, preserving the
    original proof and the anchor exactly."""
    ns, s0 = bootstrap(mode, "i-f-empty")
    t = observe_root_lineage(
        s0, ns, s0.revision, (read_request(endpoint, "de", "", "cat AGENTS.md"),)
    )
    assert t.outcome is RootLineageOutcome.ACCEPTED
    s1 = t.state
    occ = occurrences(s1, "de")[0]
    r1 = derive(s1, ns)
    assert_i_ok(r1, s1)
    assert r1.graph.root_digest == sha(ROOT_TEXT)  # type: ignore[union-attr]
    assert r1.selected_root_provenance.kind == "envelope"  # type: ignore[union-attr]
    assert r1.diagnostics == (_L.ROOT_SOURCE_UNPROVEN,)
    t2 = receipt(s1, ns, "de", endpoint, (CAUSAL_ROOT_FACT,))
    assert t2.outcome is RootLineageOutcome.ACCEPTED
    s2 = t2.state
    assert read_fact(s2, "de").authority is True
    r2 = derive(s2, ns)
    assert_i_ok(r2, s2)
    assert r2.selected_root_provenance.call_id == "de"  # type: ignore[union-attr]
    assert r2.selected_root_source_byte_length == 0
    assert r2.graph.root_digest == EMPTY_SOURCE_SHA256  # type: ignore[union-attr]
    assert r2.admission.root_entry.root_text == ""  # type: ignore[union-attr]
    assert r2.admission.root_entry.root_source_byte_length == 0  # type: ignore[union-attr]
    assert r2.diagnostics == ()
    assert occurrences(s2, "de")[0].proof is occ.proof
    assert s2.d_state.root is s0.d_state.root


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_unissued_root_read_unproven_retained(mode: Any, endpoint: str) -> None:
    """F: an unissued root read retains typed uncertainty: the
    source is retained as UNPROVEN (never selected), the bootstrap
    stays the current selection, and the fixed ROOT_SOURCE_UNPROVEN
    limitation is surfaced EXACTLY in the composition diagnostics
    (structural derivation, never a request-readiness claim)."""
    ns, s0 = bootstrap(mode, "i-f-unproven")
    s1 = observe_root_lineage(
        s0, ns, s0.revision, (read_request(endpoint, "un", UNPROVEN_BODY, "cat AGENTS.md"),)
    )
    assert s1 is not None
    r = derive(s1.state, ns)
    assert_i_ok(r, s1.state)
    assert r.selected_root_provenance.kind == "envelope"  # type: ignore[union-attr]
    assert r.graph.root_digest == sha(ROOT_TEXT)  # type: ignore[union-attr]
    assert r.diagnostics == (_L.ROOT_SOURCE_UNPROVEN,)
    assert read_fact(s1.state, "un").authority is False
    assert read_fact(s1.state, "un") in s1.state.root_facts


# ---------------------------------------------------------------------------
# G. Resource matrix: independent domains, at-limit/first-over
# ---------------------------------------------------------------------------


def _g_fixture(
    mode: Any, endpoint: str, tag: str, **ns_kwargs: Any
) -> tuple[RootLineageNamespace, RootLineageState]:
    ns = h_ns(mode, tag, **ns_kwargs)
    s0 = h_bootstrap(ns)
    s1 = nonroot_read(s0, ns, "g1", endpoint, "Synthetic G body.\n")
    return ns, s1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_i_total_at_limit_first_over(mode: Any, endpoint: str) -> None:
    """G: the NEW composition outer covers the ENTIRE operation (H
    + F + G + I glue): at the measured smallest accepting cap the
    derivation is OK, and ONE unit below it the whole result is
    refused with the fixed I name, the exact input state and NO
    partial graph/entries."""
    ns, s1 = _g_fixture(mode, endpoint, "i-g-itotal")

    def probe(cap: int) -> bool:
        return (
            derive(
                s1,
                ns,
                composition_bounds=CurrentRootCompositionBounds(max_total_work_units=cap),
            ).outcome
            is _OUT.OK
        )

    at_limit = _smallest_ok(1, 1048576, probe)
    r = derive(
        s1, ns, composition_bounds=CurrentRootCompositionBounds(max_total_work_units=at_limit - 1)
    )
    assert_i_refused(r, s1, _OUT.REFUSED_OVER_BOUND, (_L.TOTAL_WORK_UNITS_OVER_BOUND,))
    assert at_limit > 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_g_subtree_cap_independent_of_total(mode: Any, endpoint: str) -> None:
    """G: the accepted G total (F+admission subtree) binds beneath a
    LARGER whole cost: the G cap exactly at the measured F+admission
    cost succeeds while the I total has headroom, and ONE below it
    refuses with the G domain name (never a blanket label, never the
    I total name)."""
    ns, s1 = _g_fixture(mode, endpoint, "i-g-gtotal")

    def probe(cap: int) -> bool:
        return (
            derive(
                s1,
                ns,
                admission_bounds=CurrentAdmissionBounds(max_total_work_units=cap),
            ).outcome
            is _OUT.OK
        )

    at_limit = _smallest_ok(1, 1048576, probe)
    r = derive(s1, ns, admission_bounds=CurrentAdmissionBounds(max_total_work_units=at_limit - 1))
    assert_i_refused(r, s1, _OUT.REFUSED_OVER_BOUND, (_L.TOTAL_WORK_UNITS_OVER_BOUND,))


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_f_subtree_cap_independent_of_total(mode: Any, endpoint: str) -> None:
    """G: the ACTUAL supplied F ceiling counts only the F-subtree
    visits while the F phase is active: at the measured F cost the
    full derivation succeeds beneath a larger G/I total, and ONE
    below it refuses with the F domain name."""
    ns, s1 = _g_fixture(mode, endpoint, "i-g-ftotal")

    def probe(cap: int) -> bool:
        return (
            derive(s1, ns, graph_bounds=CurrentGraphBounds(max_total_work_units=cap)).outcome
            is _OUT.OK
        )

    at_limit = _smallest_ok(1, 1048576, probe)
    r = derive(s1, ns, graph_bounds=CurrentGraphBounds(max_total_work_units=at_limit - 1))
    assert_i_refused(r, s1, _OUT.REFUSED_OVER_BOUND, (_L.TOTAL_WORK_UNITS_OVER_BOUND,))


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_h_domain_cap_via_operation_override(mode: Any, endpoint: str) -> None:
    """G: the H-domain operation cap (the lineage operation override)
    keeps its OWN independent domain beneath the composition total:
    a STRICTER positive override at the measured H cost succeeds
    (the valid narrower/equal work control), and ONE below it
    refuses with the H domain name while I and G have headroom.  The
    override governs operation work fuel ONLY -- never retention
    (see the retention-cap namespace binding law below)."""
    ns, s1 = _g_fixture(mode, endpoint, "i-g-hdom")

    def probe(cap: int) -> bool:
        return (
            derive(s1, ns, lineage_bounds=RootLineageBounds(max_total_work_units=cap)).outcome
            is _OUT.OK
        )

    at_limit = _smallest_ok(1, 1048576, probe)
    r = derive(s1, ns, lineage_bounds=RootLineageBounds(max_total_work_units=at_limit - 1))
    assert_i_refused(r, s1, _OUT.REFUSED_OVER_BOUND, (_L.WORK_UNITS_OVER_BOUND,))


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_entry_source_caps(mode: Any, endpoint: str) -> None:
    """G: the entry source caps at limit/first-over.  (a) The
    inherited F single-source cap at the exact root length composes
    OK; (b) ONE byte wider, the H anchor preflight refuses BEFORE
    I (the inherited source-domain refusal -- I is structurally
    unreachable from that public input, labeled as such); (c) the
    G CUMULATIVE entry-source cap composes at limit and refuses
    first-over with the fixed G name; (d) CONSTRUCTOR-ONLY: a direct
    entry whose retained root text crosses its own key-record cap
    refuses before any owned encode (model law)."""
    raw = len(ROOT_TEXT.encode("utf-8"))
    # (a) at-limit F single-source positive.
    ns, s0 = _g_fixture(
        mode, endpoint, "i-g-src", graph_bounds=GraphBounds(max_single_source_bytes=raw)
    )
    r = derive(s0, ns)
    assert_i_ok(r, s0)
    # (b) first-over: the H bootstrap itself refuses (source domain).
    ns_over = h_ns(mode, "i-g-src-over", graph_bounds=GraphBounds(max_single_source_bytes=raw - 1))
    t = bootstrap_root_lineage((root_request(),), ns_over)
    assert t.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
    assert RootLineageLimitation.SOURCE_OVER_BOUND in t.diagnostics
    # (c) G cumulative at-limit / first-over.
    ns, s1 = _g_fixture(mode, endpoint, "i-g-srccum")
    raw1 = len(ROOT_TEXT.encode()) + len(b"Synthetic G body.\n")
    r_at = derive(
        s1, ns, admission_bounds=CurrentAdmissionBounds(max_total_entry_source_bytes=raw1)
    )
    assert_i_ok(r_at, s1)
    r_over = derive(
        s1, ns, admission_bounds=CurrentAdmissionBounds(max_total_entry_source_bytes=raw1 - 1)
    )
    assert_i_refused(r_over, s1, _OUT.REFUSED_OVER_BOUND, (_L.TOTAL_ENTRY_SOURCE_BYTES_OVER_BOUND,))
    # (d) CONSTRUCTOR-ONLY: the entry model's own preflight.
    entry = r_at.admission.root_entry  # type: ignore[union-attr]
    kr_over = entry.key_record.model_copy(
        update={"graph_bounds": GraphBounds(max_single_source_bytes=raw - 1)}
    )
    with pytest.raises(ValidationError):
        CurrentRootCompositionEntry.model_validate(entry_field_data(entry, kr_over))


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_h_retention_cap_binds_namespace_not_override(mode: Any, endpoint: str) -> None:
    """G (the named retention-cap law): the retained-state integrity
    binds the ACTUAL namespace retention policy INDEPENDENTLY of the
    operation override.  A genuine cap-1 namespace composes OK at
    its limit (bootstrap = 1 retained fact); a genuine wider-H state
    that reaches 2 facts under the SAME D scope, copied to the
    cap-1 lineage scope, refuses with the exact domain reason both
    by default AND under a wider lineage operation override (a wider
    override can never legitimize an impossible namespace state);
    the exact input state is preserved with no partial output."""
    # Root-fact count domain.
    ns_cap = h_ns(mode, "i-g-retf", bounds=RootLineageBounds(max_root_facts=1))
    ns_wide = h_ns(mode, "i-g-retf", bounds=RootLineageBounds())
    s_cap = h_bootstrap(ns_cap)
    assert len(s_cap.root_facts) == 1
    assert derive(s_cap, ns_cap).outcome is _OUT.OK  # genuine cap-1 positive
    s_wide = h_bootstrap(ns_wide)
    s_wide = refreshed(s_wide, ns_wide, "new-root", endpoint, NEW_ROOT)
    assert len(s_wide.root_facts) == 2
    assert s_wide.d_state.history_key == s_cap.d_state.history_key
    assert s_wide.lineage_key != s_cap.lineage_key
    assert derive(s_wide, ns_wide).outcome is _OUT.OK  # wider ns accepts 2 facts
    bad = s_wide.model_copy(update={"lineage_key": ns_cap.lineage_key})
    q = derive(bad, ns_cap)
    assert_i_refused(q, bad, _OUT.REFUSED_OVER_BOUND, (_L.ROOT_FACTS_OVER_BOUND,))
    q2 = derive(bad, ns_cap, lineage_bounds=RootLineageBounds())
    assert_i_refused(q2, bad, _OUT.REFUSED_OVER_BOUND, (_L.ROOT_FACTS_OVER_BOUND,))
    # Retained root source bytes domain.
    cap_bytes = 40  # 34 (ROOT_TEXT) + 15 (SIBLING_X) = 49 > 40
    ns_bcap = h_ns(
        mode, "i-g-retb", bounds=RootLineageBounds(max_retained_root_source_bytes=cap_bytes)
    )
    ns_bwide = h_ns(mode, "i-g-retb")
    s_bcap = h_bootstrap(ns_bcap)
    assert derive(s_bcap, ns_bcap).outcome is _OUT.OK  # 34 <= 40: genuine positive
    s_bwide = h_bootstrap(ns_bwide)
    s_bwide = refreshed(s_bwide, ns_bwide, "nr", endpoint, SIBLING_X)
    bad_b = s_bwide.model_copy(update={"lineage_key": ns_bcap.lineage_key})
    qb = derive(bad_b, ns_bcap)
    assert_i_refused(qb, bad_b, _OUT.REFUSED_OVER_BOUND, (_L.ROOT_SOURCE_BYTES_OVER_BOUND,))
    qb2 = derive(bad_b, ns_bcap, lineage_bounds=RootLineageBounds())
    assert_i_refused(qb2, bad_b, _OUT.REFUSED_OVER_BOUND, (_L.ROOT_SOURCE_BYTES_OVER_BOUND,))


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_batch_domain_cumulative_retention(mode: Any, endpoint: str) -> None:
    """G: the original per-batch max_requests domain versus
    cumulative retention: under an actual max_requests=2 namespace,
    TWO successive legal 2-request batches succeed (4 retained
    historical reads > the batch cap 2), and a 3-request batch
    refuses with the exact D domain reason and the EXACT prior
    state; the retained state still composes OK."""
    ns = h_ns(mode, "i-g-batch", graph_bounds=GraphBounds(max_requests=2))
    s0 = h_bootstrap(ns)

    def reqs(i: int) -> tuple[GraphRequest, ...]:
        return (read_request(endpoint, f"b{i}", f"Batch body {i}.\n", f"cat F{i}.md"),)

    t1 = observe_root_lineage(s0, ns, s0.revision, reqs(1) + reqs(2))
    assert t1.outcome is RootLineageOutcome.ACCEPTED
    t2 = observe_root_lineage(t1.state, ns, t1.state.revision, reqs(3) + reqs(4))
    assert t2.outcome is RootLineageOutcome.ACCEPTED
    assert len(t2.state.d_state.occurrences) == 4
    t3 = observe_root_lineage(t2.state, ns, t2.state.revision, reqs(5) + reqs(6) + reqs(7))
    assert t3.outcome is RootLineageOutcome.REFUSED_OVER_BOUND
    assert t3.diagnostics == (RootLineageLimitation.BATCH_OVER_BOUND,)
    assert t3.state is t2.state
    r = derive(t2.state, ns)
    assert_i_ok(r, t2.state)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_long_workspace_reservation(mode: Any, endpoint: str) -> None:
    """G: the model/namespace reservations are ACTUAL-work bounded
    in the workspace length (never a hidden constant): under a
    1024-character workspace the measured smallest accepting I
    total cap succeeds and ONE below it refuses (the long-workspace
    boundary including the entry namespace re-derivation and the
    closed bound fences)."""
    ws = "/work/" + "w" * 1018
    assert len(ws) == 1024
    ns = h_ns_ws(
        mode,
        "i-g-ws",
        ws,
        # the ACTUAL scope label (the workspace path) is part of the
        # root envelope: the inherited observation bound must admit
        # the 1024-byte label for the bootstrap to be genuine
        observation_bounds=ObservationBounds(max_label_bytes=2048),
    )
    s0 = h_bootstrap(ns, root_request_ws(ws))
    s1 = nonroot_read(s0, ns, "g1", endpoint, "Synthetic G body.\n")

    def probe(cap: int) -> bool:
        return (
            derive(
                s1,
                ns,
                composition_bounds=CurrentRootCompositionBounds(max_total_work_units=cap),
            ).outcome
            is _OUT.OK
        )

    at_limit = _smallest_ok(1, 1048576, probe)
    r = derive(
        s1, ns, composition_bounds=CurrentRootCompositionBounds(max_total_work_units=at_limit - 1)
    )
    assert_i_refused(r, s1, _OUT.REFUSED_OVER_BOUND, (_L.TOTAL_WORK_UNITS_OVER_BOUND,))


def test_g_diagnostics_ceiling_constructor_only() -> None:
    """G (CONSTRUCTOR-ONLY, labeled): the NEW composition
    diagnostics ceiling is closed 1..64 (stricter positives
    allowed, wider refused at construction), and a hostile over-cap
    diagnostics container refuses with ONE fixed private error
    before any item coercion.  The public first-over of the
    composition diagnostics cap is structurally unreachable (the
    surfaced set is closed and tiny); this is model-law evidence
    only."""
    with pytest.raises(ValidationError):
        CurrentRootCompositionBounds(max_diagnostics=65)
    assert CurrentRootCompositionBounds(max_diagnostics=1).max_diagnostics == 1
    assert CurrentRootCompositionBounds().max_diagnostics == 64
    ns, s0 = bootstrap(MODES[0], "i-g-diag")
    values = tuple(v.value for v in CurrentRootCompositionLimitation)[:65]
    with pytest.raises(ValidationError):
        CurrentRootComposition(
            outcome=_OUT.REFUSED_STATE_MALFORMED,
            state=s0,
            diagnostics=tuple(CurrentRootCompositionLimitation(v) for v in values),
        )
    r64 = CurrentRootComposition(
        outcome=_OUT.REFUSED_STATE_MALFORMED,
        state=s0,
        diagnostics=tuple(CurrentRootCompositionLimitation(v) for v in values[:64]),
    )
    assert len(r64.diagnostics) == 64


# ---------------------------------------------------------------------------
# H. Foreign/malformed/versions, I8 pre-dump fences, splices, privacy
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_h_foreign_and_version_refusals(mode: Any, endpoint: str) -> None:
    """H: foreign H scope (lineage key mismatch), foreign D scope
    (history key mismatch) and a COHERENT direct-constructed
    unsupported ACTUAL version each refuse whole with the exact
    typed outcome, the exact input state and no partial output --
    never relabelled as a root absence or a malformed label.  The
    actual version identity is bound into the H namespace scope
    (the accepted D revalidation recomputes the admission namespace
    from the actual fields on every construction), so a detached
    version tag that is merely coherently rekeyed cannot even
    CONSTRUCT a valid H scope: a fixed private refusal at scope
    construction, never a detached-tag bypass."""
    ns, s0 = bootstrap(mode, "i-h-foreign")
    s1 = refreshed(s0, ns, "r1", endpoint, NEW_ROOT)
    # Foreign H scope: a different lineage over the same D base.
    other = h_ns(mode, "i-h-foreign-other")
    r1 = derive(s1, other)
    assert_i_refused(r1, s1, _OUT.REFUSED_FOREIGN_SCOPE, (_L.FOREIGN_SCOPE,))
    # Foreign D scope: a different D lineage (history key mismatch).
    other_d = (
        h_ns(
            AdmissionMode(1) if mode.value == "lean" else AdmissionMode(0),
            "i-h-foreign-d",
            lineage=None,
        )
        if False
        else h_ns(mode, "i-h-foreign-d2")
    )
    assert other_d.history_key != ns.history_key or other_d.lineage_key != ns.lineage_key
    r2 = derive(s1, other_d)
    assert_i_refused(r2, s1, _OUT.REFUSED_FOREIGN_SCOPE, (_L.FOREIGN_SCOPE,))
    # Coherent unsupported ACTUAL version: the version is bound into
    # the actual carried D context, so the coherent rekey is refused
    # at H scope construction itself.
    data = ns.model_dump()
    data["admission_version"] = "admission-contract/v9"
    with pytest.raises(ValidationError):
        RootLineageNamespace(**data)
    # The coherent state still composes OK under the actual ns.
    assert derive(s1, ns).outcome is _OUT.OK


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_h_malformed_override_bounds(mode: Any, endpoint: str) -> None:
    """H: every bound override is fresh actual-field validated
    BEFORE any fuel is read from it (the CLOSED scalar fence runs
    before any serializer dump can walk an unexpected container,
    model_copy bypass included): a forged container field raises
    the fixed private ValueError (composition/F/G/E overrides) or
    refuses with the fixed typed MALFORMED_BINDING (the H-domain
    override), always on the EXACT input state."""
    ns, s0 = bootstrap(mode, "i-h-malformed")
    s1 = refreshed(s0, ns, "r1", endpoint, NEW_ROOT)

    def forged(cls: Any, field: str) -> Any:
        return cls().model_copy(update={field: {"x": 1}})

    for name, value in (
        ("composition_bounds", forged(CurrentRootCompositionBounds, "max_total_work_units")),
        ("graph_bounds", forged(CurrentGraphBounds, "max_total_work_units")),
        ("admission_bounds", forged(CurrentAdmissionBounds, "max_total_work_units")),
        ("currentness_bounds", forged(CurrentnessBounds, "max_work_units")),
    ):
        with pytest.raises(ValueError):
            derive(s1, ns, **{name: value})
    with pytest.raises(ValueError):
        derive(
            s1,
            ns,
            composition_bounds=CurrentRootCompositionBounds().model_copy(
                update={"max_diagnostics": True}
            ),
        )
    # The H-domain override keeps the fixed typed refusal.
    q = derive(
        s1,
        ns,
        lineage_bounds=RootLineageBounds().model_copy(update={"max_root_facts": {"n": 2}}),
    )
    assert_i_refused(q, s1, _OUT.REFUSED_STATE_MALFORMED, (_L.MALFORMED_BINDING,))
    # A bool scalar (integral-shape forgery) also refuses.
    with pytest.raises(ValueError):
        derive(
            s1,
            ns,
            composition_bounds=CurrentRootCompositionBounds().model_copy(
                update={"max_total_work_units": True}
            ),
        )
    # Every refusal kept the exact input state.
    assert derive(s1, ns).outcome is _OUT.OK


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_h_entry_bound_preflight_fence_before_first_dump(
    mode: Any, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """H (the named I8 pre-dump fence law): the accepted namespace-
    reconstruction helpers DUMP the key record's carried bound
    models while rebuilding their context.  A model_copy-forged
    bound field must refuse with the fixed private error BEFORE the
    first serializer traversal: a serializer sentinel on the four
    bound model_dump paths must fire on the genuine re-derivation
    (positive control) and stay UNCHANGED across every forged
    refusal (entry-level and admission-level, the root entry being
    the first namespace re-derivation of the admission pass)."""
    ns, s0 = bootstrap(mode, "i-h-fence")
    s1 = nonroot_read(s0, ns, "f1", endpoint, "Synthetic file content.\n")
    r = derive(s1, ns)
    assert_i_ok(r, s1)
    adm = r.admission
    entry = adm.root_entry  # type: ignore[union-attr]

    counts = {"n": 0}
    for cls in (
        __import__(
            "slaif_local_coding.constitution.bundles.bundle_admission_models",
            fromlist=["BundleAdmissionBounds"],
        ).BundleAdmissionBounds,
        BundleProofBounds,
        GraphBounds,
        ObservationBounds,
    ):
        original = cls.model_dump

        def counting(self: Any, *a: Any, _orig: Any = original, **kw: Any) -> Any:
            counts["n"] += 1
            return _orig(self, *a, **kw)

        monkeypatch.setattr(cls, "model_dump", counting)

    # Positive control: the genuine admission re-derivation DUMPS
    # the actual bound models (the sentinel must be able to fire).
    base = counts["n"]
    rebuilt = CurrentRootCompositionAdmission.model_validate(
        {n: getattr(adm, n) for n in CurrentRootCompositionAdmission.model_fields}
    )
    assert rebuilt.scope_key == adm.scope_key  # type: ignore[union-attr]
    assert counts["n"] > base
    kr = entry.key_record
    # Entry-level: dict bound, wrong-class bound and bool scalars all
    # refuse with the fixed error BEFORE any dump.
    for field, forged_value in (
        ("graph_bounds", {"max_depth": 16}),
        (
            "graph_bounds",
            __import__(
                "slaif_local_coding.constitution.bundles.bundle_admission_models",
                fromlist=["BundleAdmissionBounds"],
            ).BundleAdmissionBounds(),
        ),
        ("proof_bounds", kr.proof_bounds.model_copy(update={"max_segments": True})),
        ("observation_bounds", kr.observation_bounds.model_copy(update={"max_items": True})),
    ):
        before = counts["n"]
        with pytest.raises(ValidationError) as excinfo:
            CurrentRootCompositionEntry.model_validate(
                entry_field_data(entry, kr.model_copy(update={field: forged_value}))
            )
        message = str(excinfo.value)
        assert "key_record" in message and "bound" in message
        assert counts["n"] == before, "the fence must refuse before the first dump"
    # A COHERENT in-range scalar change (max_items=1 is a legal
    # value) is not a shape forgery: the closed fence passes and the
    # canonical-key binding refuses it instead (the re-derivation may
    # dump -- that is actual charged recipe work, not a fence
    # failure).  No forged bound may be retained either way.
    with pytest.raises(ValidationError) as excinfo:
        CurrentRootCompositionEntry.model_validate(
            entry_field_data(
                entry,
                kr.model_copy(
                    update={
                        "observation_bounds": kr.observation_bounds.model_copy(
                            update={"max_items": 1}
                        )
                    }
                ),
            )
        )
    assert "content key must bind" in str(excinfo.value)
    # Admission-level: a forged ROOT entry (the first namespace
    # re-derivation of the pass) refuses before ANY dump of the
    # admission path.
    # (The entry construction itself is refused above; the
    # admission-level fence is proven with an entry whose key record
    # was forged AFTER its own construction via model_copy -- the
    # bypass the admission pass must catch.)
    bypassed = entry.model_copy(
        update={"key_record": kr.model_copy(update={"admission_bounds": {"max_entries": 64}})}
    )
    before = counts["n"]
    with pytest.raises(ValidationError) as excinfo:
        CurrentRootCompositionAdmission.model_validate(
            admission_field_data(adm, root_entry=bypassed)
        )
    assert "must be the actual bound model" in str(excinfo.value)
    assert counts["n"] == before, "the admission fence must refuse before the first dump"
    # And the genuine admission still validates end-to-end.
    assert (
        CurrentRootCompositionAdmission.model_validate(
            {n: getattr(adm, n) for n in CurrentRootCompositionAdmission.model_fields}
        ).scope_key
        == adm.scope_key  # type: ignore[union-attr]
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_h_model_negative_splices_constructor_only(mode: Any, endpoint: str) -> None:
    """H (CONSTRUCTOR-ONLY, labeled): the I7/association model law
    refuses the named splices that the public acquisition cannot
    produce: a foreign admission-namespace context (coherently
    rekeyed principal), a later-state proof spliced into an earlier
    state, a detached stale scope key and a foreign selection
    splice.  These are model-law controls over the retained record
    shape, not public acquisition evidence."""
    ns, s0 = bootstrap(mode, "i-h-splice")
    s1 = nonroot_read(s0, ns, "p1", endpoint, "Synthetic file content.\n")
    r = derive(s1, ns)
    assert_i_ok(r, s1)
    adm = r.admission
    # (1) Foreign B-namespace context: the root entry key record's
    # principal changed -- the admission context can no longer
    # re-derive the ACTUAL input history key.
    foreign_kr = adm.root_entry.key_record.model_copy(  # type: ignore[union-attr]
        update={"principal": IDENTITY.principal + "0"}
    )
    foreign_entry = adm.root_entry.model_copy(update={"key_record": foreign_kr})  # type: ignore[union-attr]
    # Rebuild the entry with the changed canonical keys so that ONLY
    # the namespace context is the bad join (the entry itself stays
    # self-consistent by re-derivation under the foreign identity).
    from slaif_local_coding.constitution.bundles.bundle_admission import (
        _key_canonical,
    )
    from slaif_local_coding.constitution.bundles.current_admission_models import (
        _entry_admission_namespace,
    )

    fns = _entry_admission_namespace(foreign_kr)
    fk_record = foreign_kr.model_copy(
        update={
            "content_key": None,
        }
    )
    canonical = _key_canonical(
        fns,
        foreign_kr.root_digest,
        foreign_kr.authority_class,
        foreign_kr.member_occurrences,
        foreign_kr.member_classes,
        foreign_kr.aggregate_source_digest,
        foreign_kr.ownership_groups,
    )
    fk_record = foreign_kr.model_copy(update={"content_key": hashlib.sha256(canonical).hexdigest()})
    foreign_entry = adm.root_entry.model_copy(  # type: ignore[union-attr]
        update={"key_record": fk_record, "content_key": fk_record.content_key}
    )
    with pytest.raises(ValidationError):
        CurrentRootCompositionAdmission.model_validate(
            admission_field_data(adm, root_entry=foreign_entry)
        )
    # (2) A LATER proof spliced into the earlier state: the entry is
    # made SELF-CONSISTENT under the actual admission namespace (its
    # key record re-derives the canonical bytes from the later
    # proof's admitted region) AND under the J01/J02 exact
    # association law (the spliced entry keeps the actual selected
    # governing digest; its member path AGENTS.md row is remapped to
    # the COMPLETE key set; the original entry and every other row
    # keep their representing entries), so ONLY the result-level
    # input-state proof/witness join can refuse it: the later proof
    # object is not retained by the earlier input D state.
    s2 = refreshed(s1, ns, "r2", endpoint, "Later root body.")
    later_occ = occurrences(s2, "r2")[0]
    later_proof = later_occ.proof
    later_body = "Later root body."  # the exact r2 read body (no newline)
    adm_ns_actual = _entry_admission_namespace(adm.root_entry.key_record)  # type: ignore[union-attr]
    later_groups = (
        OwnershipGroup(
            group_index=0,
            member_occurrence_indices=(0,),
            boundary_class=BoundaryClass.PROVEN,
            group_digest=sha(later_body),
        ),
    )
    spliced_canonical = _key_canonical(
        adm_ns_actual,
        adm.root_digest,  # type: ignore[union-attr]
        EntryClass.FILE_BUNDLE_ENTRY,
        (ROOT_FILENAME,),
        (MemberClass.ELIGIBLE,),
        sha(later_body),
        later_groups,
    )
    spliced_key = hashlib.sha256(spliced_canonical).hexdigest()
    spliced_record = adm.root_entry.key_record.model_copy(  # type: ignore[union-attr]
        update={
            "authority_class": EntryClass.FILE_BUNDLE_ENTRY,
            "member_occurrences": (ROOT_FILENAME,),
            "member_classes": (MemberClass.ELIGIBLE,),
            "aggregate_source_digest": sha(later_body),
            "ownership_groups": later_groups,
            "content_key": spliced_key,
        }
    )
    spliced_entry = CurrentRootCompositionEntry(
        entry_class=EntryClass.FILE_BUNDLE_ENTRY,
        content_key=spliced_key,
        key_record=spliced_record,
        width=1,
        member_classes=(MemberClass.ELIGIBLE,),
        root_digest=adm.root_digest,  # type: ignore[union-attr]
        proof=later_proof,
        admitted_segments=(0,),
        witnesses=(
            CurrentAdmissionWitness(
                occurrence_id=later_occ.occurrence_id,
                request_index=later_proof.request_index,
                call_position=later_proof.call_position,
                result_position=later_proof.result_position,
                segment_indices=(0,),
            ),
        ),
    )
    spliced_rows = tuple(
        row.model_copy(
            update={"content_keys": tuple(sorted(set(row.content_keys) | {spliced_key}))}
        )
        if row.path == ROOT_FILENAME
        else row
        for row in adm.path_associations  # type: ignore[union-attr]
    )
    spliced_entries = tuple(
        sorted((*adm.entries, spliced_entry), key=lambda e: e.content_key)  # type: ignore[union-attr]
    )
    spliced_adm = CurrentRootCompositionAdmission.model_validate(
        admission_field_data(
            adm,
            entries=spliced_entries,
            entries_retained=1 + len(spliced_entries),
            path_associations=spliced_rows,
        )
    )
    with pytest.raises(ValidationError):
        CurrentRootComposition.model_validate(
            {n: getattr(r, n) for n in CurrentRootComposition.model_fields}
            | {"admission": spliced_adm}
        )
    # (3) A detached stale scope key.
    with pytest.raises(ValidationError):
        CurrentRootCompositionAdmission.model_validate(
            admission_field_data(adm, scope_key="0" * 64)
        )
    # (4) A foreign selection splice: a selection from ANOTHER
    # lineage scope cannot ride an ok result.
    other = h_ns(mode, "i-h-splice-other")
    sel_other = select_current_root(s1, other)
    assert sel_other.outcome is RootSelectionOutcome.REFUSED
    foreign_sel = RootSelectionResult(
        outcome=RootSelectionOutcome.OK,
        limitations=(),
        lineage_key=other.lineage_key,
        revision=s1.revision,
        selected_source_digest=r.selection.selected_source_digest,  # type: ignore[union-attr]
        witness_facts=r.selection.witness_facts,  # type: ignore[union-attr]
    )
    with pytest.raises(ValidationError):
        CurrentRootComposition.model_validate(
            {n: getattr(r, n) for n in CurrentRootComposition.model_fields}
            | {"selection": foreign_sel}
        )


def _block_host_io(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("host IO attempted during the pure derivation")

    monkeypatch.setattr("builtins.open", boom)
    monkeypatch.setattr(os, "stat", boom)
    monkeypatch.setattr(os, "lstat", boom)
    monkeypatch.setattr(os, "chdir", boom)
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(subprocess, "Popen", boom)
    monkeypatch.setattr(Path, "open", boom)
    monkeypatch.setattr(Path, "read_bytes", boom)
    monkeypatch.setattr(Path, "read_text", boom)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_h_no_host_io_on_exercised_surfaces(
    mode: Any, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """H: the exercised SUCCESS and REFUSAL surfaces of the public
    derivation perform NO host IO (no open/stat/lstat/chdir/socket/
    Popen/Path read of any kind): the derivation is a pure bounded
    charged operation over the actual retained state."""
    ns, s0 = bootstrap(mode, "i-h-noio")
    s1 = nonroot_read(s0, ns, "n1", endpoint, "Synthetic file content.\n")
    _block_host_io(monkeypatch)
    try:
        assert derive(s1, ns).outcome is _OUT.OK
        assert derive(s0, ns).outcome is _OUT.OK
        other = h_ns(mode, "i-h-noio-other")
        assert derive(s1, other).outcome is _OUT.REFUSED_FOREIGN_SCOPE
        q = derive(
            s1,
            ns,
            composition_bounds=CurrentRootCompositionBounds(max_total_work_units=1),
        )
        assert q.outcome is _OUT.REFUSED_OVER_BOUND
    finally:
        monkeypatch.undo()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_h_private_reprs_never_echo_private_values(mode: Any, endpoint: str) -> None:
    """H: the operational reprs of the result, admission and entry
    suppress private source/ID/workspace values: a canary root body
    and the private call IDs never appear in str/repr of any
    derived record (fixed enums, counts and placeholders only)."""
    CANARY = "canary-root-body-018i-9c4e"
    ns = h_ns(mode, "i-h-privacy")
    s0 = h_bootstrap(ns, rooted(CANARY))
    s1 = refreshed(s0, ns, "priv-call-7f3a", endpoint, CANARY + " refresh.")
    r = derive(s1, ns)
    assert_i_ok(r, s1)
    surfaces = [
        str(r),
        repr(r),
        str(r.admission),
        repr(r.admission),
        str(r.admission.root_entry),  # type: ignore[union-attr]
        repr(r.admission.root_entry),  # type: ignore[union-attr]
        str(r.selection),
        repr(r.selection),
    ]
    surfaces += [str(e) for e in (r.admission.root_entry, *r.admission.entries)]  # type: ignore[union-attr]
    for surface in surfaces:
        assert CANARY not in surface
        assert "priv-call-7f3a" not in surface
        assert "/work" not in surface


def test_h_limitation_enum_exact_1to1_mapping() -> None:
    """H: the closed I limitation vocabulary is EXACTLY the 1:1
    union of the accepted 018-h root-lineage names and the accepted
    018-g current-admission names (which already carry the 018-f
    graph names 1:1) plus the NEW composition-level
    ``root_conflict`` -- every inherited value propagates with its
    exact original value, never relabelled."""
    h_values = {v.value for v in RootLineageLimitation}
    g_values = {v.value for v in CurrentAdmissionLimitation}
    i_values = {v.value for v in CurrentRootCompositionLimitation}
    assert i_values == (h_values | g_values | {"root_conflict"})
    for value in h_values | g_values:
        assert CurrentRootCompositionLimitation(value).value == value


@pytest.mark.parametrize("mode", MODES)
def test_h_h_refusal_closed_outcome_mapping(mode: Any) -> None:
    """H: the H domain refusal mapping is the accepted closed H
    mapping, propagated 1:1 by value: EVERY ``*_over_bound``
    retained-state crossing (H-owned or mirrored from the actual D
    domain) is the fixed over-bound refusal, never a malformed
    label; the H scope names keep their fixed composition
    outcomes."""
    ns, s0 = bootstrap(mode, "i-h-map")
    for lim in RootLineageLimitation:
        r = _h_refusal(s0, lim)
        assert r.state is s0
        assert r.graph is None
        assert r.admission is None
        assert r.diagnostics == (_L(lim.value),)
        if lim is RootLineageLimitation.WORK_UNITS_OVER_BOUND:
            assert r.outcome is _OUT.REFUSED_OVER_BOUND
        elif lim is RootLineageLimitation.FOREIGN_SCOPE:
            assert r.outcome is _OUT.REFUSED_FOREIGN_SCOPE
        elif lim is RootLineageLimitation.VERSION_UNSUPPORTED:
            assert r.outcome is _OUT.REFUSED_VERSION_CONFLICT
        elif lim.value.endswith("_over_bound"):
            assert r.outcome is _OUT.REFUSED_OVER_BOUND
        else:
            assert r.outcome is _OUT.REFUSED_STATE_MALFORMED


# ---------------------------------------------------------------------------
# J. 018-j: association closure (J01/J02) and independent budget domains (J03)
# ---------------------------------------------------------------------------

J_STALE_DIGEST = sha("stale-governing-digest")  # a valid 64-hex, never a real one


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_j01_all_entries_bind_selected_governing_digest(mode: Any, endpoint: str) -> None:
    """J01 positive (both boundaries): in a genuine OK result every
    retained entry -- the root entry and every file entry, and each
    entry's actual key record -- binds the admission's SELECTED
    governing digest exactly."""
    ns, s0 = bootstrap(mode, "i-j01-pos")
    s1 = nonroot_read(s0, ns, "j01a", endpoint, "Synthetic J01 body.\n")
    s2 = refreshed(s1, ns, "j01b", endpoint, ROOT_TEXT + "\nSynthetic J01 changed root.\n")
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    adm = r.admission
    assert adm is not None
    assert adm.root_entry.root_digest == adm.root_digest
    assert adm.root_entry.key_record.root_digest == adm.root_digest
    for entry in adm.entries:
        assert entry.root_digest == adm.root_digest
        assert entry.key_record.root_digest == adm.root_digest


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_j01_historical_governing_key_splice_refused(mode: Any, endpoint: str) -> None:
    """J01 (CONSTRUCTOR-ONLY, labeled): the genuine EARLIER file
    entry (OLD governing root digest and canonical key) spliced
    back into the current admission with its reverse-index row
    remapped is refused at BOTH the admission boundary and the
    result boundary (a model_copy-bypassed nested admission), even
    though its namespace and retained proof are genuine and
    unchanged.  This is the named 018-i constructor defect; the
    public I derivation never emits the historical row."""
    ns, s0 = bootstrap(mode, "i-j01-splice")
    s1 = nonroot_read(s0, ns, "j01c", endpoint, "Synthetic retained A body.\n")
    old = derive(s1, ns)
    assert_i_ok(old, s1)
    old_adm = old.admission
    assert old_adm is not None
    old_entry = i_members_of(old_adm)[("A.md",)]
    s2 = refreshed(s1, ns, "j01d", endpoint, ROOT_TEXT + "\nSynthetic changed governing root.\n")
    current = derive(s2, ns)
    assert_i_ok(current, s2)
    cur_adm = current.admission
    assert cur_adm is not None
    cur_entry = i_members_of(cur_adm)[("A.md",)]
    # genuine preconditions (the original 018-i probe facts)
    assert cur_entry.proof is old_entry.proof
    assert old_entry.root_digest != cur_adm.root_digest
    assert cur_entry.content_key != old_entry.content_key
    # the splice: the old entry replaces the current one; its row
    # key is remapped in the reverse index (as the 018-i probe did)
    spliced_entries = tuple(
        sorted(
            (old_entry if e is cur_entry else e for e in cur_adm.entries),
            key=lambda e: e.content_key,
        )
    )
    spliced_rows = tuple(
        row.model_copy(
            update={
                "content_keys": tuple(
                    sorted(
                        old_entry.content_key if key == cur_entry.content_key else key
                        for key in row.content_keys
                    )
                )
            }
        )
        for row in cur_adm.path_associations
    )
    # (a) the admission boundary refuses the historical governing key
    with pytest.raises(ValidationError) as exc_adm:
        CurrentRootCompositionAdmission(
            **admission_field_data(
                cur_adm,
                entries=spliced_entries,
                entries_retained=1 + len(spliced_entries),
                path_associations=spliced_rows,
            )
        )
    assert "every file entry binds the selected governing root digest" in str(exc_adm.value)
    # (b) the result boundary re-checks the ACTUAL fields of a
    #     model_copy-bypassed nested admission
    bad_adm = cur_adm.model_copy(
        update={
            "entries": spliced_entries,
            "entries_retained": 1 + len(spliced_entries),
            "path_associations": spliced_rows,
        }
    )
    with pytest.raises(ValidationError) as exc_res:
        CurrentRootComposition(
            **{n: getattr(current, n) for n in CurrentRootComposition.model_fields}
            | {"admission": bad_adm}
        )
    assert "every file entry binds the selected governing root digest" in str(exc_res.value)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_j01_entry_vs_key_record_governing_mismatch_refused(mode: Any, endpoint: str) -> None:
    """J01: the governing-digest join is enforced at the ACTUAL
    target boundary: an entry-vs-key-record governing-field
    mismatch refuses at the entry law (fixed private error), and a
    model_copy-bypassed key record inside a constructed entry
    refuses at the admission AND the result boundaries."""
    ns, s0 = bootstrap(mode, "i-j01-mis")
    s1 = nonroot_read(s0, ns, "j01e", endpoint, "Synthetic J01 mismatch body.\n")
    r = derive(s1, ns)
    assert_i_ok(r, s1)
    adm = r.admission
    assert adm is not None
    entry = i_members_of(adm)[("A.md",)]
    # (a) the entry law itself: the entry's governing field must
    #     equal its key record's governing field
    data = entry_field_data(entry, entry.key_record)
    data["root_digest"] = J_STALE_DIGEST
    with pytest.raises(ValidationError) as exc_entry:
        CurrentRootCompositionEntry(**data)
    assert "entry root binding must equal the key record root binding" in str(exc_entry.value)
    # (b) the admission boundary re-checks the ACTUAL key record even
    #     when the entry object bypassed its own law via model_copy
    stale_kr = entry.key_record.model_copy(update={"root_digest": J_STALE_DIGEST})
    bypassed = entry.model_copy(update={"key_record": stale_kr})
    with pytest.raises(ValidationError) as exc_adm:
        CurrentRootCompositionAdmission(**admission_field_data(adm, entries=(bypassed,)))
    assert "every file entry key record binds the selected governing root digest" in str(
        exc_adm.value
    )
    # (c) the result boundary does the same on the nested admission
    bad_adm = adm.model_copy(update={"entries": (bypassed,)})
    with pytest.raises(ValidationError) as exc_res:
        CurrentRootComposition(
            **{n: getattr(r, n) for n in CurrentRootComposition.model_fields}
            | {"admission": bad_adm}
        )
    assert "every file entry key record binds the selected governing root digest" in str(
        exc_res.value
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_j02_reverse_relation_exact_positive(mode: Any, endpoint: str) -> None:
    """J02 positive (both boundaries): the derived reverse index
    equals EXACTLY the represented member-path -> ALL and ONLY
    admitted content keys relation, with the actual admission
    scoped key on every row, the exact root flags, canonical
    ordering/dedup and no extraneous rows."""
    ns, s0 = bootstrap(mode, "i-j02-pos")
    s1 = nonroot_read(s0, ns, "j02a", endpoint, "Synthetic J02 body.\n")
    r = derive(s1, ns)
    assert_i_ok(r, s1)
    adm = r.admission
    assert adm is not None
    expected: dict[str, set[str]] = {}
    for e in (adm.root_entry, *adm.entries):
        for path in e.key_record.member_occurrences:
            expected.setdefault(path, set()).add(e.content_key)
    paths = [row.path for row in adm.path_associations]
    assert paths == sorted(paths)
    assert len(set(paths)) == len(paths)
    assert set(paths) == set(expected)
    for row in adm.path_associations:
        assert row.scoped_key == adm.admission_scoped_key
        assert row.is_root == (row.path == adm.root_path)
        assert set(row.content_keys) == expected[row.path]
        assert list(row.content_keys) == sorted(row.content_keys)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_j02_nonmember_row_refused(mode: Any, endpoint: str) -> None:
    """J02 (CONSTRUCTOR-ONLY, labeled): a typed reverse-index row
    for a path represented by NO admitted entry (pointing at the
    real root key, everything else genuine) is refused at BOTH the
    admission boundary and the result boundary (a model_copy-
    bypassed nested admission).  The named 018-i defect; the index
    never grants root/system authority."""
    ns, s0 = bootstrap(mode, "i-j02-nonmember")
    s1 = nonroot_read(s0, ns, "j02b", endpoint, "Synthetic J02 nonmember body.\n")
    r = derive(s1, ns)
    assert_i_ok(r, s1)
    adm = r.admission
    assert adm is not None
    assert all(
        "Unused.md" not in e.key_record.member_occurrences for e in (adm.root_entry, *adm.entries)
    )
    extra = CurrentAdmissionPathAssociation(
        scoped_key=adm.admission_scoped_key,
        path="Unused.md",
        content_keys=(adm.root_entry.content_key,),
        is_root=False,
    )
    rows = tuple(sorted((*adm.path_associations, extra), key=lambda row: row.path))
    with pytest.raises(ValidationError) as exc_adm:
        CurrentRootCompositionAdmission(**admission_field_data(adm, path_associations=rows))
    assert "the reverse index never names an unrepresented member path" in str(exc_adm.value)
    bad_adm = adm.model_copy(update={"path_associations": rows})
    with pytest.raises(ValidationError) as exc_res:
        CurrentRootComposition(
            **{n: getattr(r, n) for n in CurrentRootComposition.model_fields}
            | {"admission": bad_adm}
        )
    assert "the reverse index never names an unrepresented member path" in str(exc_res.value)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_j02_row_relation_mutations_refused(mode: Any, endpoint: str) -> None:
    """J02 (CONSTRUCTOR-ONLY, labeled): the exact-relation law
    refuses at the target boundary with fixed private errors: a
    wrong member-to-key edge, an unknown content key, a missing
    row, a duplicate path row and a foreign row scope (the actual
    scoped key of another genuine namespace)."""
    ns, s0 = bootstrap(mode, "i-j02-mut")
    s1 = nonroot_read(s0, ns, "j02c", endpoint, "Synthetic J02 mutation body.\n")
    r = derive(s1, ns)
    assert_i_ok(r, s1)
    adm = r.admission
    assert adm is not None
    a_row = next(row for row in adm.path_associations if row.path == "A.md")
    root_key = adm.root_entry.content_key
    # (1) wrong member-to-key edge: the A.md row points at the root key
    rows1 = tuple(
        row.model_copy(update={"content_keys": (root_key,)}) if row.path == "A.md" else row
        for row in adm.path_associations
    )
    with pytest.raises(ValidationError) as e1:
        CurrentRootCompositionAdmission(**admission_field_data(adm, path_associations=rows1))
    assert "each reverse index row holds exactly the admitted content keys" in str(e1.value)
    # (2) an unknown content key added to the A.md row
    rows2 = tuple(
        row.model_copy(update={"content_keys": tuple(sorted((*row.content_keys, J_STALE_DIGEST)))})
        if row.path == "A.md"
        else row
        for row in adm.path_associations
    )
    with pytest.raises(ValidationError) as e2:
        CurrentRootCompositionAdmission(**admission_field_data(adm, path_associations=rows2))
    assert "each reverse index row holds exactly the admitted content keys" in str(e2.value)
    # (3) a missing A.md row
    rows3 = tuple(row for row in adm.path_associations if row.path != "A.md")
    with pytest.raises(ValidationError) as e3:
        CurrentRootCompositionAdmission(**admission_field_data(adm, path_associations=rows3))
    assert "the reverse index covers every represented member path exactly once" in str(e3.value)
    # (4) a duplicate A.md row
    rows4 = tuple(sorted((*adm.path_associations, a_row), key=lambda row: row.path))
    with pytest.raises(ValidationError) as e4:
        CurrentRootCompositionAdmission(**admission_field_data(adm, path_associations=rows4))
    assert "reverse index rows must be sorted by distinct path" in str(e4.value)
    # (5) a foreign row scope: the ACTUAL scoped key of another
    #     genuine namespace (a different evidenced workspace)
    ns_other = h_ns_ws(mode, "i-j02-foreign-ws", "/elsewhere/j02-foreign")
    rows5 = tuple(
        row.model_copy(update={"scoped_key": ns_other.admission_scoped_key})
        for row in adm.path_associations
    )
    with pytest.raises(ValidationError) as e5:
        CurrentRootCompositionAdmission(**admission_field_data(adm, path_associations=rows5))
    assert "every reverse index row binds the actual admission scoped key" in str(e5.value)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_j02_shared_member_multi_key_row_positive(mode: Any, endpoint: str) -> None:
    """J02 positive: a legitimate SHARED member -- the same path
    admitted by two distinct proven bundles (the accepted G
    overlap pattern: two bundles sharing A.md with the same A
    content) -- keeps ONE row with the COMPLETE key set in
    canonical order, and the index stays the exact represented
    relation (all current positives preserved by the J02 law).
    Both modes: the shared row is legal admitted structure, never
    pollution."""
    seg_a, seg_b, seg_c = "A part one.\n", "B part.\n", "C part.\n"
    MARK = "JSHRD"
    ns = h_ns(mode, "i-j02-shared")
    s0 = h_bootstrap(
        ns,
        root_request_ws(WORKSPACE, "Read `A.md`, `B.md` and `C.md` before changing code."),
    )
    s1 = nonroot_read(
        s0,
        ns,
        "j02d",
        endpoint,
        seg_a + MARK + "\n" + seg_b,
        cmd=f"cat A.md && echo '{MARK}' && cat B.md",
    )
    s2 = nonroot_read(
        s1,
        ns,
        "j02e",
        endpoint,
        seg_a + MARK + "\n" + seg_c,
        cmd=f"cat A.md && echo '{MARK}' && cat C.md",
    )
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    adm = r.admission
    assert adm is not None
    by = i_members_of(adm)
    ab = by[("A.md", "B.md")]
    ac = by[("A.md", "C.md")]
    assert ab.content_key != ac.content_key
    row = next(row for row in adm.path_associations if row.path == "A.md")
    assert row.content_keys == tuple(sorted((ab.content_key, ac.content_key)))
    assert row.is_root is False
    b_row = next(row for row in adm.path_associations if row.path == "B.md")
    assert b_row.content_keys == (ab.content_key,)
    c_row = next(row for row in adm.path_associations if row.path == "C.md")
    assert c_row.content_keys == (ac.content_key,)


# --- K: actual nested canonical keys, row shapes and reachable E caps --


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_k01_stale_canonical_key_after_rebind_refused(mode: Any, endpoint: str) -> None:
    """K01 (CONSTRUCTOR-ONLY, labeled): rebounding BOTH the
    entry's and the key record's governing digest fields to the
    selected digest while RETAINING the old actual canonical key
    is refused at the leaf law AND at BOTH parent boundaries:
    the actual canonical key must RE-DERIVE from the actual
    nested key record through the accepted C recipe, and
    comparing digest tags (or entry==record key) alone is never
    the law.  The genuine preconditions (the exact retained
    original proof, the old and new governing keys differing,
    the current entry's key re-deriving exactly) are asserted.
    The public I derivation never emits the forged entry."""
    ns, s0 = bootstrap(mode, "i-k01-rebind")
    s1 = nonroot_read(s0, ns, "k01a", endpoint, "Synthetic retained A body.\n")
    old = derive(s1, ns)
    assert_i_ok(old, s1)
    oe = i_members_of(old.admission)[("A.md",)]
    s2 = refreshed(s1, ns, "k01b", endpoint, ROOT_TEXT + "\nSynthetic governing root changes.\n")
    current = derive(s2, ns)
    assert_i_ok(current, s2)
    adm = current.admission
    assert adm is not None
    ce = i_members_of(adm)[("A.md",)]
    # genuine preconditions (the original probe facts)
    assert ce.proof is oe.proof
    assert oe.root_digest != adm.root_digest
    assert ce.content_key != oe.content_key
    # positive re-derivation precondition: the CURRENT entry's
    # canonical key re-derives from its actual key record exactly
    assert _canonical_entry_key(ce.key_record) == ce.content_key
    # the rebind: BOTH the entry's and the key record's governing
    # digest fields become the selected digest; the OLD canonical
    # key is retained
    kr = oe.key_record.model_copy(update={"root_digest": adm.root_digest})
    bad_entry = oe.model_copy(update={"root_digest": adm.root_digest, "key_record": kr})
    assert kr.root_digest == adm.root_digest
    assert _canonical_entry_key(kr) != bad_entry.content_key
    # (a) the leaf law already rejects the re-bound entry
    with pytest.raises(ValidationError) as exc_leaf:
        CurrentRootCompositionEntry(
            **{n: getattr(bad_entry, n) for n in CurrentRootCompositionEntry.model_fields}
        )
    assert "content key must bind the actual canonical 018-c recipe" in str(exc_leaf.value)
    # the splice (the 018-i probe pattern): the forged entry
    # replaces the current one and its row key is remapped
    entries = tuple(
        sorted((bad_entry if e is ce else e for e in adm.entries), key=lambda e: e.content_key)
    )
    rows = tuple(
        row.model_copy(
            update={
                "content_keys": tuple(
                    sorted(
                        oe.content_key if key == ce.content_key else key for key in row.content_keys
                    )
                )
            }
        )
        for row in adm.path_associations
    )
    # (b) the admission boundary refuses the stale canonical key
    with pytest.raises(ValidationError) as exc_adm:
        CurrentRootCompositionAdmission(
            **admission_field_data(
                adm, entries=entries, entries_retained=1 + len(entries), path_associations=rows
            )
        )
    assert "every entry canonical key re-derives from its actual key record" in str(exc_adm.value)
    # (c) the result boundary re-checks the ACTUAL fields of a
    #     model_copy-bypassed nested admission
    bad_adm = adm.model_copy(
        update={
            "entries": entries,
            "entries_retained": 1 + len(entries),
            "path_associations": rows,
        }
    )
    with pytest.raises(ValidationError) as exc_res:
        CurrentRootComposition(
            **{n: getattr(current, n) for n in CurrentRootComposition.model_fields}
            | {"admission": bad_adm}
        )
    assert "every entry canonical key re-derives from its actual key record" in str(exc_res.value)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_k01_key_record_content_key_mismatch_refused(mode: Any, endpoint: str) -> None:
    """K01: the entry key record's OWN content key must agree
    with the entry at BOTH parent boundaries.  Variant A copies a
    forged content key into the retained key record (the entry
    key unchanged); variant B forges the entry's own content key
    (the key record unchanged).  Both reach the intended target
    with the fixed private error at the admission AND the result
    boundary (model_copy-bypassed nested admissions)."""
    ns, s0 = bootstrap(mode, "i-k01-ck")
    s1 = nonroot_read(s0, ns, "k01c", endpoint, "Synthetic K01 mismatch body.\n")
    r = derive(s1, ns)
    assert_i_ok(r, s1)
    adm = r.admission
    assert adm is not None
    entry = i_members_of(adm)[("A.md",)]
    # (a) variant A: the copied key record carries a forged
    #     content key; the entry's own key is unchanged
    stale_kr = entry.key_record.model_copy(update={"content_key": J_STALE_DIGEST})
    bypassed = entry.model_copy(update={"key_record": stale_kr})
    with pytest.raises(ValidationError) as exc_adm:
        CurrentRootCompositionAdmission(**admission_field_data(adm, entries=(bypassed,)))
    assert "every entry key record content key agrees with the entry" in str(exc_adm.value)
    bad_adm = adm.model_copy(update={"entries": (bypassed,)})
    with pytest.raises(ValidationError) as exc_res:
        CurrentRootComposition(
            **{n: getattr(r, n) for n in CurrentRootComposition.model_fields}
            | {"admission": bad_adm}
        )
    assert "every entry key record content key agrees with the entry" in str(exc_res.value)
    # (b) variant B: the entry's own content key is forged; the
    #     key record is unchanged
    forged = entry.model_copy(update={"content_key": J_STALE_DIGEST})
    with pytest.raises(ValidationError) as exc_adm2:
        CurrentRootCompositionAdmission(**admission_field_data(adm, entries=(forged,)))
    assert "every entry key record content key agrees with the entry" in str(exc_adm2.value)
    bad_adm2 = adm.model_copy(update={"entries": (forged,)})
    with pytest.raises(ValidationError) as exc_res2:
        CurrentRootComposition(
            **{n: getattr(r, n) for n in CurrentRootComposition.model_fields}
            | {"admission": bad_adm2}
        )
    assert "every entry key record content key agrees with the entry" in str(exc_res2.value)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_k02_duplicate_row_key_refused(mode: Any, endpoint: str) -> None:
    """K02 (CONSTRUCTOR-ONLY, labeled): a model_copy row that
    DUPLICATES a genuine admitted content key is refused at the
    leaf row law AND at BOTH parent boundaries: the actual row
    container/count/scalar shape and the strict canonical
    sorted/distinct key order are validated BEFORE the set
    comparison can erase the duplicate fact."""
    ns, s0 = bootstrap(mode, "i-k02-dup")
    s1 = nonroot_read(s0, ns, "k02a", endpoint, "Synthetic retained A body.\n")
    r = derive(s1, ns)
    assert_i_ok(r, s1)
    adm = r.admission
    assert adm is not None
    root_row = next(row for row in adm.path_associations if row.path == adm.root_path)
    duplicate = root_row.model_copy(
        update={"content_keys": root_row.content_keys + root_row.content_keys}
    )
    # (a) the leaf row law already rejects the duplicated key
    with pytest.raises(ValidationError):
        CurrentAdmissionPathAssociation(
            **{n: getattr(duplicate, n) for n in CurrentAdmissionPathAssociation.model_fields}
        )
    # (b) the admission boundary refuses before the set
    #     comparison
    rows = tuple(duplicate if row is root_row else row for row in adm.path_associations)
    with pytest.raises(ValidationError) as exc_adm:
        CurrentRootCompositionAdmission(**admission_field_data(adm, path_associations=rows))
    assert "each reverse index row holds distinct content keys" in str(exc_adm.value)
    # (c) the result boundary re-checks the ACTUAL row
    bad_adm = adm.model_copy(update={"path_associations": rows})
    with pytest.raises(ValidationError) as exc_res:
        CurrentRootComposition(
            **{n: getattr(r, n) for n in CurrentRootComposition.model_fields}
            | {"admission": bad_adm}
        )
    assert "each reverse index row holds distinct content keys" in str(exc_res.value)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_k02_reversed_row_keys_refused(mode: Any, endpoint: str) -> None:
    """K02 (CONSTRUCTOR-ONLY, labeled): a legitimate SHARED
    member (one path admitted by two distinct proven bundles --
    the accepted G overlap pattern) keeps ONE row with the
    COMPLETE key set in canonical order; a model_copy row that
    REVERSES that key order changes no set fact, so the old set
    comparison alone cannot see it: the strict canonical sorted
    order is refused at BOTH parent boundaries with the fixed
    private error."""
    seg_a, seg_b, seg_c = "A part one.\n", "B part.\n", "C part.\n"
    MARK = "KSHRD"
    ns = h_ns(mode, "i-k02-rev")
    s0 = h_bootstrap(
        ns,
        root_request_ws(WORKSPACE, "Read `A.md`, `B.md` and `C.md` before changing code."),
    )
    s1 = nonroot_read(
        s0,
        ns,
        "k02b",
        endpoint,
        seg_a + MARK + "\n" + seg_b,
        cmd=f"cat A.md && echo '{MARK}' && cat B.md",
    )
    s2 = nonroot_read(
        s1,
        ns,
        "k02c",
        endpoint,
        seg_a + MARK + "\n" + seg_c,
        cmd=f"cat A.md && echo '{MARK}' && cat C.md",
    )
    r = derive(s2, ns)
    assert_i_ok(r, s2)
    adm = r.admission
    assert adm is not None
    row = next(row for row in adm.path_associations if row.path == "A.md")
    keys = row.content_keys
    assert len(keys) == 2 and keys == tuple(sorted(keys))
    reversed_row = row.model_copy(update={"content_keys": tuple(reversed(keys))})
    # the SET is unchanged: the set comparison alone cannot see
    # the reversal
    assert set(reversed_row.content_keys) == set(keys)
    rows = tuple(
        reversed_row if candidate is row else candidate for candidate in adm.path_associations
    )
    with pytest.raises(ValidationError) as exc_adm:
        CurrentRootCompositionAdmission(**admission_field_data(adm, path_associations=rows))
    assert "each reverse index row holds canonically sorted content keys" in str(exc_adm.value)
    bad_adm = adm.model_copy(update={"path_associations": rows})
    with pytest.raises(ValidationError) as exc_res:
        CurrentRootComposition(
            **{n: getattr(r, n) for n in CurrentRootComposition.model_fields}
            | {"admission": bad_adm}
        )
    assert "each reverse index row holds canonically sorted content keys" in str(exc_res.value)


# --- J03: independent budget domains and pre-charge fences ----------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_j03_d_local_domain_under_i(mode: Any, endpoint: str) -> None:
    """J03: the ACTUAL D-local per-transition work domain
    (HistoryBounds.max_work_units, charged inside the composition's
    H phase) is INDEPENDENT of the larger H/I outers.  The public-I
    first-over is structurally UNREACHABLE on a coherent state and
    is closed at the actual bounded D-validator stage surface,
    never a fake public positive: (1) the cap is identity-bound
    into the history key, so a state built under one cap cannot be
    derived under a different-cap namespace -- the identity
    control ISOLATES the bound change (the SAME lineage tag,
    lineage key, workspace, identity and version context, with
    ONLY the actual HistoryBounds work cap changed), and the
    exact refusal before any derivation work is
    REFUSED_FOREIGN_SCOPE; and (2) every accepted D transition
    revalidates the FINAL state under the same cap (the
    transition-final-validation invariant: the last-transition
    cost is at least the whole-state cost; receipts revalidate
    too), so any state whose derive-time D validation would
    first-over could never have been built in the first place.
    At the measured at-limit cap the full genuine state validates
    under a lenient shared work outer, and ONE below it the D
    domain refuses with its exact inherited work name while the
    shared outer still has headroom (the crossing is the D-local
    domain, not the outer)."""
    tag = "i-j03-dlocal"
    ns = h_ns(mode, tag)
    s0 = h_bootstrap(ns)
    s1 = nonroot_read(s0, ns, "j03d1", endpoint, "Synthetic D local body one.\n")
    s2 = nonroot_read(s1, ns, "j03d2", endpoint, "Synthetic D local body two.\n")
    assert_i_ok(derive(s2, ns), s2)

    class _shared_outer:
        """The LARGER shared work outer: charged for the same units
        as the D-local domain; its headroom is deliberately
        generous so the D-local ceiling is the binding quantity."""

        def __init__(self) -> None:
            self.spent = 0

        def __call__(self) -> bool:
            self.spent += 1
            return True

    def validates(cap: int) -> bool:
        return (
            validate_causal_history_state(
                s2.d_state, HistoryBounds(max_work_units=cap), _shared_outer()
            )
            is None
        )

    at_limit = _smallest_ok(1, 65536, validates)
    assert at_limit > 1, "the D-local domain must be measurable above the state cost"
    outer_ok = _shared_outer()
    assert (
        validate_causal_history_state(s2.d_state, HistoryBounds(max_work_units=at_limit), outer_ok)
        is None
    )
    assert outer_ok.spent > 0, "the shared outer is charged for the same units"
    outer_over = _shared_outer()
    assert (
        validate_causal_history_state(
            s2.d_state, HistoryBounds(max_work_units=at_limit - 1), outer_over
        )
        is CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
    )
    # The public-I identity-binding control (K03 scope-control
    # correction): the strict-cap namespace keeps the SAME
    # lineage tag -- and therefore the SAME lineage key,
    # workspace, identity and version context -- and changes
    # ONLY the actual HistoryBounds work cap.  The controlled
    # difference is that the identity-bound history key differs
    # solely through the bound, so the exact pre-derivation
    # refusal is FOREIGN SCOPE: the D-local cap can never be
    # crossed through the public I API on a coherent state, and
    # the transition-final-validation invariant is the support
    # for the public first-over being structurally unreachable
    # (never an inference from the absence of an override).
    ns_strict = h_ns(mode, tag, history_bounds=HistoryBounds(max_work_units=at_limit - 1))
    # The controlled difference: the SAME tag keeps the same
    # lineage tag, workspace, identity, versions and every other
    # field -- ONLY the actual HistoryBounds work cap changes,
    # and the cap is identity-bound into the history key (the
    # state-scoped key and the lineage key are derived from it),
    # so the field difference is exactly the bound plus those
    # derived identity keys and nothing else.
    strict_dump = ns_strict.model_dump()
    base_dump = ns.model_dump()
    assert strict_dump["history_key"] != base_dump["history_key"], (
        "the cap is identity-bound into the history key"
    )
    assert strict_dump["state_scoped_key"] != base_dump["state_scoped_key"], (
        "the state-scoped key is derived from the identity-bound history key"
    )
    assert strict_dump["lineage_key"] != base_dump["lineage_key"], (
        "the lineage key is derived from the identity-bound history key"
    )
    assert strict_dump["workspace"] == base_dump["workspace"], "the workspace is unchanged"
    diff = {k for k in strict_dump if strict_dump[k] != base_dump[k]}
    assert diff == {"history_key", "state_scoped_key", "lineage_key", "history_bounds"}, (
        "only the actual history bound and its identity-bound keys differ"
    )
    assert_i_refused(derive(s2, ns_strict), s2, _OUT.REFUSED_FOREIGN_SCOPE, (_L.FOREIGN_SCOPE,))


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_j03_e_domains_under_i(mode: Any, endpoint: str) -> None:
    """J03 (narrowed by K03): the E WORK and DIAGNOSTICS domains
    surface through the F mapping under their exact inherited
    CURRENTNESS_* names and bind INDEPENDENTLY beneath the larger
    H/F/G/I outers through the public-I derivation, over genuine
    retained history with the exact original currentness groups.
    Where a first-over is structurally unreachable through this
    clean public fixture (the derivation's cost for that domain
    sits at the model floor), the domain is closed at the actual
    bounded constructor surface -- the model law itself refuses
    the sub-floor value -- never a fake public positive.  The
    four E COLLECTION domains (paths/groups/witness-memberships/
    relation-pairs) have GENUINELY reachable public first-overs
    and are covered by the dedicated K03 control over genuinely
    larger retained histories."""
    ns, s0 = bootstrap(mode, "i-j03-edom")
    s1 = nonroot_read(s0, ns, "j03e", endpoint, "Synthetic E domain body.\n")
    domains = {
        "max_work_units": (1048576, _L.CURRENTNESS_WORK_UNITS_OVER_BOUND),
        "max_diagnostics": (64, _L.CURRENTNESS_DIAGNOSTICS_OVER_BOUND),
    }
    for field, (hi, name) in domains.items():

        def probe(cap: int, field: str = field) -> bool:
            return (
                derive(s1, ns, currentness_bounds=CurrentnessBounds(**{field: cap})).outcome
                is _OUT.OK
            )

        at_limit = _smallest_ok(1, hi, probe)
        if at_limit > 1:
            assert (
                derive(s1, ns, currentness_bounds=CurrentnessBounds(**{field: at_limit})).outcome
                is _OUT.OK
            )
            r = derive(s1, ns, currentness_bounds=CurrentnessBounds(**{field: at_limit - 1}))
            assert_i_refused(r, s1, _OUT.REFUSED_OVER_BOUND, (name,))
        else:
            # The model floor is the at-limit: the public first-over
            # is structurally unreachable on this clean fixture, and
            # the actual bounded constructor surface refuses the
            # sub-floor value with the fixed model law.
            with pytest.raises(ValidationError):
                CurrentnessBounds(**{field: 0})


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_k03_e_collection_limits_under_i(
    mode: Any, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """K03: the four ACTUAL E collection domains each have a
    GENUINELY REACHABLE public-I first-over over genuinely larger
    retained histories with the exact original currentness
    groups: two distinct nonroot reads cross the supported cap1
    for max_paths/max_groups/max_witness_memberships, and three
    compatible occurrences of one read cross cap1 for
    max_relation_pairs.  At the measured at-limit cap the
    composition succeeds with every other budget at its default
    (the independent actual-domain count/cost positive), and ONE
    below it refuses with the exact inherited collection name,
    the exact prior state and no partial output.  The facade
    sentinel proves the crossing charged ACTUAL F/E work before
    refusal (strictly more than the zero-work foreign-scope
    early refusal).  No forged acquisition, foreign namespace or
    unrelated early cap is a substitute."""
    tag = "i-k03-ecoll"
    ns, s0 = bootstrap(mode, tag)
    a = nonroot_read(s0, ns, "k03a", endpoint, "Synthetic retained body.\n")
    two = nonroot_read(a, ns, "k03b", endpoint, "Synthetic B body.\n", cmd="cat B.md")
    assert_i_ok(derive(two, ns), two)
    repeated = nonroot_read(a, ns, "k03c", endpoint, "Synthetic retained body.\n")
    repeated = nonroot_read(repeated, ns, "k03d", endpoint, "Synthetic retained body.\n")
    assert_i_ok(derive(repeated, ns), repeated)
    # The facade sentinel: count the ACTUAL G facade units
    # charged before each crossing (class-identity-preserving
    # wrapper on the ledger's unit).
    facade_unit = crc._CFacade.unit
    facade = {"n": 0}

    def spy_facade(self: Any) -> bool:
        facade["n"] += 1
        return facade_unit(self)

    monkeypatch.setattr(crc._CFacade, "unit", spy_facade)
    # The early-refusal control: foreign scope refuses BEFORE any
    # F/E work (zero facade units).
    ns_other = h_ns_ws(mode, "i-k03-other-ws", "/elsewhere/k03-foreign")
    facade["n"] = 0
    r_foreign = derive(two, ns_other)
    assert_i_refused(r_foreign, two, _OUT.REFUSED_FOREIGN_SCOPE, (_L.FOREIGN_SCOPE,))
    foreign_work = facade["n"]
    assert foreign_work == 0, "the foreign-scope refusal performs no F/E work"
    cases = (
        ("max_paths", 16384, _L.PATHS_OVER_BOUND, two),
        ("max_groups", 32768, _L.GROUPS_OVER_BOUND, two),
        ("max_witness_memberships", 65536, _L.WITNESS_MEMBERSHIPS_OVER_BOUND, two),
        ("max_relation_pairs", 65536, _L.RELATION_PAIRS_OVER_BOUND, repeated),
    )
    for field, hi, name, state in cases:

        def probe(cap: int, field: str = field, state: RootLineageState = state) -> bool:
            return (
                derive(state, ns, currentness_bounds=CurrentnessBounds(**{field: cap})).outcome
                is _OUT.OK
            )

        at_limit = _smallest_ok(1, hi, probe)
        assert at_limit > 1, "the E collection domain must be measurable above its floor"
        # The at-limit positive: the crossing domain at exactly
        # its necessary cost composes OK, every other budget at
        # its default (headroom).
        assert (
            derive(state, ns, currentness_bounds=CurrentnessBounds(**{field: at_limit})).outcome
            is _OUT.OK
        )
        facade["n"] = 0
        r = derive(state, ns, currentness_bounds=CurrentnessBounds(**{field: at_limit - 1}))
        assert_i_refused(r, state, _OUT.REFUSED_OVER_BOUND, (name,))
        assert facade["n"] > 0, "the crossing charged actual F/E work before refusal"
        assert facade["n"] > foreign_work, "the crossing charged more work than the early refusal"


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_j03_graph_stage_domain_under_i(mode: Any, endpoint: str) -> None:
    """J03: the ACTUAL inherited GraphBounds graph-stage work
    ceiling (the namespace graph bounds, charged on the F graph
    stage) binds SEPARATELY beneath the larger H/F-total/G/I
    outers: a graph-rich retained history (a root source
    referencing forty files plus one read of A.md, so the charged
    graph stage strictly exceeds the admission stage) at the
    measured stage cost composes OK, and ONE below it refuses with
    the exact inherited graph-stage name -- never the
    admission-stage or the total name -- all other budgets at
    their defaults.  The D/H transitions charge no stage ledger,
    so the state builds at every cap and the binary search is over
    the derive only."""
    tag = "i-j03-gstage"
    refs = ", ".join(f"`N{i:02d}.md`" for i in range(40))
    root_content = f"Read {refs} before changing code."

    def build(cap: int) -> tuple[RootLineageNamespace, RootLineageState] | None:
        try:
            ns = h_ns(mode, tag, graph_bounds=GraphBounds(max_work_units=cap))
            s0 = h_bootstrap(ns, root_request_ws(WORKSPACE, root_content))
            s1 = nonroot_read(
                s0, ns, "j03g1", endpoint, "Synthetic graph body one.\n", cmd="cat A.md"
            )
            return ns, s1
        except AssertionError:
            return None

    def probe(cap: int) -> bool:
        built = build(cap)
        if built is None:
            return False
        ns, s = built
        return derive(s, ns).outcome is _OUT.OK

    at_limit = _smallest_ok(1, 100000, probe)
    assert at_limit > 1
    built = build(at_limit - 1)
    assert built is not None
    ns, s = built
    r = derive(s, ns)
    assert_i_refused(r, s, _OUT.REFUSED_OVER_BOUND, (_L.GRAPH_WORK_UNITS_OVER_BOUND,))


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_j03_admission_stage_domain_under_i(mode: Any, endpoint: str) -> None:
    """J03: the ACTUAL inherited GraphBounds admission-planning
    stage ceiling (the same namespace graph bounds charged on the
    G admission stage -- a DISTINCT counter from the F graph
    stage) binds SEPARATELY: an admission-work-rich retained
    history (repeated reads of one file: many charged occurrences
    over one graph node) at the measured stage cost composes OK,
    and ONE below it refuses with the exact admission-stage name
    while the graph stage still has headroom."""
    tag = "i-j03-astage"

    def build(cap: int) -> tuple[RootLineageNamespace, RootLineageState] | None:
        try:
            ns = h_ns(mode, tag, graph_bounds=GraphBounds(max_work_units=cap))
            s0 = h_bootstrap(ns)
            s = s0
            for i in range(3):
                s = nonroot_read(
                    s, ns, f"j03a{i}", endpoint, f"Synthetic stage body {i}.\n", cmd="cat A.md"
                )
            return ns, s
        except AssertionError:
            return None

    def probe(cap: int) -> bool:
        built = build(cap)
        if built is None:
            return False
        ns, s = built
        return derive(s, ns).outcome is _OUT.OK

    at_limit = _smallest_ok(1, 100000, probe)
    assert at_limit > 1
    built = build(at_limit - 1)
    assert built is not None
    ns, s = built
    r = derive(s, ns)
    assert_i_refused(r, s, _OUT.REFUSED_OVER_BOUND, (_L.ADMISSION_WORK_UNITS_EXHAUSTED,))


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_j03_independent_domain_costs_observer(
    mode: Any, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """J03: the four domain ledgers are INDEPENDENT, proven by an
    observer that counts the ACTUAL charged units (class-identity-
    preserving wrappers on each ledger's unit, the H-round hook
    pattern) on ONE generous OK run: the I outer total equals the
    G-subtree plus H-domain charges plus the NEW-I glue (strictly
    positive), and every domain then succeeds at EXACTLY its
    measured cost and refuses ONE below with its own fixed name
    (not only a binary threshold self-measurement)."""
    ns, s1 = _g_fixture(mode, endpoint, "i-j03-obs")
    counts = {"itotal": 0, "g": 0, "f": 0, "h": 0}
    itotal_unit = crc._ITotal.unit
    facade_unit = crc._CFacade.unit
    h_unit = crc._HAdapter.unit

    def spy_itotal(self: Any) -> None:
        counts["itotal"] += 1
        itotal_unit(self)

    def spy_facade(self: Any) -> bool:
        counts["g"] += 1
        if self._f_phase:
            counts["f"] += 1
        return facade_unit(self)

    def spy_h(self: Any) -> bool:
        counts["h"] += 1
        return h_unit(self)

    monkeypatch.setattr(crc._ITotal, "unit", spy_itotal)
    monkeypatch.setattr(crc._CFacade, "unit", spy_facade)
    monkeypatch.setattr(crc._HAdapter, "unit", spy_h)
    assert derive(s1, ns).outcome is _OUT.OK
    c_i, c_g, c_f, c_h = counts["itotal"], counts["g"], counts["f"], counts["h"]
    assert c_f <= c_g
    glue = c_i - c_g - c_h
    assert glue > 0, "the NEW-I glue work is charged independently of G and H"
    # The G cap exactly its real F+admission cost succeeds while the
    # I total has headroom; one below refuses with the G domain name.
    assert (
        derive(s1, ns, admission_bounds=CurrentAdmissionBounds(max_total_work_units=c_g)).outcome
        is _OUT.OK
    )
    assert_i_refused(
        derive(s1, ns, admission_bounds=CurrentAdmissionBounds(max_total_work_units=c_g - 1)),
        s1,
        _OUT.REFUSED_OVER_BOUND,
        (_L.TOTAL_WORK_UNITS_OVER_BOUND,),
    )
    # The I cap exactly G+H leaves NO headroom for the NEW-I glue.
    assert_i_refused(
        derive(
            s1,
            ns,
            composition_bounds=CurrentRootCompositionBounds(max_total_work_units=c_g + c_h),
        ),
        s1,
        _OUT.REFUSED_OVER_BOUND,
        (_L.TOTAL_WORK_UNITS_OVER_BOUND,),
    )
    # The I cap exactly the measured total succeeds.
    assert (
        derive(
            s1, ns, composition_bounds=CurrentRootCompositionBounds(max_total_work_units=c_i)
        ).outcome
        is _OUT.OK
    )
    # The F cap exactly its real subtree cost succeeds; one below
    # refuses with the F domain name.
    assert (
        derive(s1, ns, graph_bounds=CurrentGraphBounds(max_total_work_units=c_f)).outcome is _OUT.OK
    )
    assert_i_refused(
        derive(s1, ns, graph_bounds=CurrentGraphBounds(max_total_work_units=c_f - 1)),
        s1,
        _OUT.REFUSED_OVER_BOUND,
        (_L.TOTAL_WORK_UNITS_OVER_BOUND,),
    )
    # The H cap exactly its real domain cost succeeds; one below
    # refuses with the H domain name.
    assert (
        derive(s1, ns, lineage_bounds=RootLineageBounds(max_total_work_units=c_h)).outcome
        is _OUT.OK
    )
    assert_i_refused(
        derive(s1, ns, lineage_bounds=RootLineageBounds(max_total_work_units=c_h - 1)),
        s1,
        _OUT.REFUSED_OVER_BOUND,
        (_L.WORK_UNITS_OVER_BOUND,),
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_j03_new_construction_precharge_sentinels(
    mode: Any, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """J03: crossing the I cap immediately before each NEW-I fence
    / index / wrapper construction PREVENTS that construction.
    Class-identity-preserving constructor hooks (instrumenting
    __init__ while delegating to the original) record the ACTUAL
    I charge count at each construction on ONE generous OK run --
    the positive hook-increment control (every hook fires at
    least once, so a non-invoked hook cannot pass 0==0).  Three
    capped runs: (E) the cap EXACTLY before the root entry's own
    key-record fence reservation stops the fence and constructs NO
    entry; (A) the cap EXACTLY at the last entry construction lets
    every entry build and stops the first post-entry reservation
    before the admission record; (R) the cap EXACTLY at the
    admission construction lets the admission build and stops the
    result reservation before the OK result record (the refusal's
    own non-OK result construction may fire the hook; only the OK
    record must be prevented).  Every refusal is the fixed I total
    name with the exact prior state."""
    ns, s1 = _g_fixture(mode, endpoint, "i-j03-sent")
    itotal_unit = crc._ITotal.unit
    charge = {"n": 0}

    def spy_itotal(self: Any) -> None:
        charge["n"] += 1
        itotal_unit(self)

    monkeypatch.setattr(crc._ITotal, "unit", spy_itotal)
    entry_counts: list[int] = []
    adm_counts: list[int] = []
    res_ok: list[int] = []
    entry_orig = crcm.CurrentRootCompositionEntry.__init__
    adm_orig = crcm.CurrentRootCompositionAdmission.__init__
    res_orig = crcm.CurrentRootComposition.__init__

    def hook_entry(self: Any, *args: Any, **kwargs: Any) -> None:
        entry_counts.append(charge["n"])
        entry_orig(self, *args, **kwargs)

    def hook_adm(self: Any, *args: Any, **kwargs: Any) -> None:
        adm_counts.append(charge["n"])
        adm_orig(self, *args, **kwargs)

    def hook_res(self: Any, *args: Any, **kwargs: Any) -> None:
        if kwargs.get("outcome") is _OUT.OK:
            res_ok.append(charge["n"])
        res_orig(self, *args, **kwargs)

    monkeypatch.setattr(crcm.CurrentRootCompositionEntry, "__init__", hook_entry)
    monkeypatch.setattr(crcm.CurrentRootCompositionAdmission, "__init__", hook_adm)
    monkeypatch.setattr(crcm.CurrentRootComposition, "__init__", hook_res)
    ok_result = derive(s1, ns)
    assert ok_result.outcome is _OUT.OK
    fence = crcm.KEY_RECORD_FENCE_UNITS
    # Positive hook controls: the constructions really happened on
    # the uncapped run (a non-invoked hook could not pass).
    assert len(entry_counts) >= 1 and len(adm_counts) == 1 and len(res_ok) == 1
    first_entry = entry_counts[0]
    last_entry = entry_counts[-1]
    adm = adm_counts[0]
    assert first_entry > fence, "the root entry fence is charged before its construction"
    assert last_entry >= first_entry
    assert adm > last_entry
    # K01/K02: the ACTUAL canonical re-derivation and row-shape
    # fence reservations are PRE-charged on the I outer BEFORE
    # each construction that performs them: the delta between
    # the last entry construction and the admission construction
    # must include the per-entry canonical re-derivation upper
    # bound (root plus file entries) and the per-row shape upper
    # bound, and the result construction mirrors the same terms.
    ok_adm = ok_result.admission
    assert ok_adm is not None
    k_units = sum(
        crcm.canonical_rekey_units(entry.key_record)
        for entry in (ok_adm.root_entry, *ok_adm.entries)
    ) + sum(crcm.row_shape_units(row.content_keys) for row in ok_adm.path_associations)
    assert k_units > 0, "the K reservation terms are nonzero on a genuine OK run"
    assert adm - last_entry >= k_units, "the K reservations are precharged before the admission"
    assert res_ok[0] - adm >= k_units, "the K reservations are precharged before the OK result"
    # (E) cap exactly before the root entry's own fence reservation:
    # the fence crosses and NO entry is constructed.
    entry_counts.clear()
    r = derive(
        s1,
        ns,
        composition_bounds=CurrentRootCompositionBounds(max_total_work_units=first_entry - fence),
    )
    assert_i_refused(r, s1, _OUT.REFUSED_OVER_BOUND, (_L.TOTAL_WORK_UNITS_OVER_BOUND,))
    assert entry_counts == [], "the pre-charge fence prevented every entry construction"
    # (A) cap exactly at the last entry construction: all entries
    # build, the first post-entry reservation crosses before the
    # admission record.
    entry_counts.clear()
    adm_counts.clear()
    res_ok.clear()
    r = derive(
        s1,
        ns,
        composition_bounds=CurrentRootCompositionBounds(max_total_work_units=last_entry),
    )
    assert_i_refused(r, s1, _OUT.REFUSED_OVER_BOUND, (_L.TOTAL_WORK_UNITS_OVER_BOUND,))
    assert entry_counts, "every entry construction completes before the crossing"
    assert adm_counts == [], "the pre-charge reservation prevented the admission"
    assert res_ok == []
    # (R) cap exactly at the admission construction: the admission
    # builds, the result reservation crosses before the OK result.
    adm_counts.clear()
    res_ok.clear()
    r = derive(
        s1,
        ns,
        composition_bounds=CurrentRootCompositionBounds(max_total_work_units=adm),
    )
    assert_i_refused(r, s1, _OUT.REFUSED_OVER_BOUND, (_L.TOTAL_WORK_UNITS_OVER_BOUND,))
    assert adm_counts, "the admission construction completes before the crossing"
    assert res_ok == [], "the pre-charge reservation prevented the OK result"
