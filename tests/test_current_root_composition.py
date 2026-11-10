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
    make_causal_history_namespace,
)
from slaif_local_coding.constitution.bundles.current_admission_models import (
    CurrentAdmissionBounds,
    CurrentAdmissionLimitation,
    CurrentAdmissionWitness,
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
    # proof's admitted region), so ONLY the result-level
    # input-state proof join can refuse it: the later proof object
    # is not retained by the earlier input D state.
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
    spliced_adm = CurrentRootCompositionAdmission.model_validate(
        admission_field_data(adm, entries=(spliced_entry,), path_associations=spliced_rows)
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
