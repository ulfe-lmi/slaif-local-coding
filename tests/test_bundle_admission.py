"""018-c: public bundle-admission composition — the inert pure
lean/greedy admission and structural-identity surface.

PUBLIC composition tests for ``observe_bundle_admission`` /
``observe_bundle_admission_batch``: the accepted 017 observation
(re-derived under the ACTUAL effective ``ObservationBounds``), the
single evidenced root/workspace binding (the 018-a law), the accepted
018-b bundle-proof pass (one shared source ledger) and the new AND/OR
raw-reference closure (one shared work ledger) compose into ONE
bounded lean/greedy admission snapshot under one explicit trusted
namespace.  All payloads are inline known-synthetic original API
payloads on BOTH read endpoints (legacy framed and native carriers);
no model, native, client or service facility is started.

Locked law surface: eligibility is independent root reachability
(acquisition and admission stay separate); the lean/greedy truth
table (all-eligible whole in both modes, mixed boundaryless lean
refusal / greedy whole with the per-occurrence authority vector,
mixed proven-group lean per-group admission with the no A+C splice
law, zero-eligible refusal including unrelated singletons); group
certificates only under the all-eligible same-canonical-directory
common-base law (different bases and mixed eligibility stay
unresolved-origin evidence); the LEAST complete AND/OR derivation
depth law after the bounded certificate fixed point (accepted old
``max_depth`` never pre-empts a valid shorter new group derivation;
scanned-text caching never freezes downstream or certificate
depths); the canonical structural content key (ordered member
occurrences, exact aggregate digest, ownership partition, scope and
ALL effective bound sets, the actual reference grammar identity)
with deliberate provenance exclusion; the complete reverse
member-path index (every ACTUAL association attempt charged before
dedup); source-version and offgraph observations retained
independently of admission; every original 018-b proof retained
verbatim in a separate bounded occurrence provenance; every bound
at-limit / one-over under the ACTUAL effective values (no partial
admission on any refusal); the total emitted closed-enum diagnostic
bound (the stricter of the stage and snapshot caps); and
privacy/purity (repr/errors never echo source, private IDs or
identity values; no host IO).
"""

from __future__ import annotations

import builtins
import copy
import hashlib
import json
import os
import socket
import subprocess
from pathlib import Path
from typing import Any

import pytest

from slaif_local_coding.constitution.bundles import (
    EMPTY_SOURCE_SHA256,
    AdmissionLimitation,
    AdmissionMode,
    AdmissionOutcome,
    BoundaryClass,
    BundleAdmissionBounds,
    BundleAdmissionNamespace,
    BundleAdmissionSnapshot,
    BundleProofBounds,
    BundleProofOutcome,
    EntryClass,
    GraphBounds,
    GraphRequest,
    MemberClass,
    NodeStatus,
    ObservationBounds,
    PathContext,
    make_bundle_admission_namespace,
    make_bundle_proof_namespace,
    make_graph_namespace,
    observe_bundle_admission,
    observe_bundle_admission_batch,
    observe_bundle_proofs,
    observe_graph_batch,
)
from slaif_local_coding.constitution.cache import RequestIdentity

IDENTITY = RequestIdentity(
    principal="synthetic-admission-principal",
    session="synthetic-admission-session",
    repository="synthetic-admission-repo",
    route="synthetic-admission-route",
)
FINGERPRINT = "abcdef0123456789" * 4
WORKSPACE = "/work"
MARKER = "__UNIQUE_BOUNDARY_018c__"


def make_ns(
    mode: AdmissionMode = AdmissionMode.LEAN,
    depth: int = 64,
    bounds: BundleAdmissionBounds | None = None,
    graph_bounds: GraphBounds | None = None,
    proof_bounds: BundleProofBounds | None = None,
) -> BundleAdmissionNamespace:
    return make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-admission-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
        bounds=bounds,
        graph_bounds=graph_bounds or GraphBounds(max_depth=depth),
        proof_bounds=proof_bounds,
    )


def root_item(content: str) -> dict[str, Any]:
    return {
        "role": "user",
        "content": [
            {
                "type": "input_text",
                "text": (
                    f"# AGENTS.md instructions for {WORKSPACE}\n\n"
                    f"<INSTRUCTIONS>\n{content}\n</INSTRUCTIONS>\n"
                ),
            }
        ],
    }


def exec_call(cid: str, cmd: str) -> dict[str, Any]:
    return {
        "type": "function_call",
        "call_id": cid,
        "name": "exec_command",
        "arguments": json.dumps({"cmd": cmd}),
    }


def out_item(cid: str, text: str) -> dict[str, Any]:
    return {"type": "function_call_output", "call_id": cid, "output": text}


def frame_legacy(chunk: str, body: str, code: int = 0) -> str:
    return (
        f"Chunk ID: {chunk}\n"
        "Wall time: 0.0000 seconds\n"
        f"Process exited with code {code}\n"
        f"Output:\n{body}"
    )


def responses_payload(*items: dict[str, Any]) -> dict[str, Any]:
    return {"model": "synthetic-admission-model", "input": list(items)}


def chat_payload(*calls: tuple[str, str, str]) -> dict[str, Any]:
    """One assistant turn: (call_id, command, wrapper text) triples."""
    messages: list[dict[str, Any]] = [
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
                for cid, cmd, _frame in calls
            ],
        }
    ]
    messages.extend(
        {"role": "tool", "tool_call_id": cid, "content": frame} for cid, _cmd, frame in calls
    )
    return {"model": "synthetic-admission-model", "messages": messages}


def batch(*payloads: dict[str, Any], endpoint: str = "responses") -> tuple[GraphRequest, ...]:
    return tuple(GraphRequest(payload=p, endpoint=endpoint, context=None) for p in payloads)


def single(
    payload: dict[str, Any],
    mode: AdmissionMode = AdmissionMode.LEAN,
    depth: int = 64,
    bounds: BundleAdmissionBounds | None = None,
    graph_bounds: GraphBounds | None = None,
    proof_bounds: BundleProofBounds | None = None,
) -> BundleAdmissionSnapshot:
    return observe_bundle_admission(
        payload,
        make_ns(
            mode=mode,
            depth=depth,
            bounds=bounds,
            graph_bounds=graph_bounds,
            proof_bounds=proof_bounds,
        ),
        endpoint="responses",
    )


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


# --- Admission truth table (original public API, both endpoints) ----------
# Root authority is Responses-only (the accepted 017 law): the batch
# carries the legitimate effective Responses root plus the read
# evidence on EITHER endpoint (responses legacy framed / chat tool
# result).


def _root_payload() -> dict[str, Any]:
    return responses_payload(root_item("A.md"))


def _read_payloads() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        responses_payload(
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("l1", "alpha")),
        ),
        chat_payload(("call-a", "cat A.md", frame_legacy("l1", "alpha"))),
    )


@pytest.mark.parametrize("endpoint", ["responses", "chat"])
def test_all_eligible_whole_bundle_both_modes(endpoint: str) -> None:
    """All members independently reachable: BOTH modes admit the whole
    on both endpoints (root authority from the responses request)."""
    responses_read, chat_read = _read_payloads()
    payload = responses_read if endpoint == "responses" else chat_read
    reqs = (
        GraphRequest(payload=_root_payload(), endpoint="responses", context=None),
        GraphRequest(payload=payload, endpoint=endpoint, context=None),
    )
    for mode in (AdmissionMode.LEAN, AdmissionMode.GREEDY):
        snapshot = observe_bundle_admission_batch(reqs, make_ns(mode=mode))
        assert snapshot.outcome is AdmissionOutcome.COMPLETE
        assert len(snapshot.entries) == 1
        entry = snapshot.entries[0]
        assert entry.entry_class is EntryClass.FILE_BUNDLE_ENTRY
        assert entry.key_record.member_occurrences == ("A.md",)
        assert entry.member_classes == (MemberClass.ELIGIBLE,)
        assert entry.key_record.aggregate_source_digest == sha256_hex("alpha")
        assert {n.path for n in snapshot.eligibility_nodes} == {"AGENTS.md", "A.md"}
        assert snapshot.offgraph_nodes == ()
        assert len(snapshot.source_proofs) == 1
        assert entry.proof is snapshot.source_proofs[0]
        # the root entry is required and distinct from the file key
        assert snapshot.root_entry is not None
        assert snapshot.root_entry.content_key != entry.content_key


def test_mixed_boundaryless_lean_refuses_greedy_whole() -> None:
    """Mixed eligible/background boundaryless: lean admits NOTHING for
    the bundle, greedy admits the whole preserving the per-occurrence
    authority vector (B is never upgraded); the boundaryless source
    proves NO individual member hash, and an independently known
    standalone B read stays offgraph provenance."""
    payload = responses_payload(
        root_item("A.md"),
        exec_call("call-ab", "cat A.md B.md"),
        out_item("call-ab", frame_legacy("l1", "alphabeta")),
    )
    lean = single(payload)
    assert lean.outcome is AdmissionOutcome.COMPLETE
    assert lean.entries == ()
    # A.md is root-reachable (eligible, content-missing: the group is
    # boundaryless, so no per-file acquisition is invented); B.md is a
    # group supplier only and never an offgraph node; nothing is
    # admitted.
    nodes = {n.path: n for n in lean.eligibility_nodes}
    assert set(nodes) == {"AGENTS.md", "A.md"}
    assert nodes["A.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING
    assert lean.offgraph_nodes == ()
    assert AdmissionLimitation.CANDIDATE_UNPROVEN in lean.diagnostics

    greedy = single(payload, mode=AdmissionMode.GREEDY)
    assert greedy.outcome is AdmissionOutcome.COMPLETE
    assert len(greedy.entries) == 1
    entry = greedy.entries[0]
    assert entry.key_record.member_occurrences == ("A.md", "B.md")
    assert entry.member_classes == (MemberClass.ELIGIBLE, MemberClass.GREEDY_BACKGROUND)
    assert entry.key_record.aggregate_source_digest == sha256_hex("alphabeta")
    # boundaryless ownership: one BOUNDARYLESS group over both occurrences
    assert len(entry.key_record.ownership_groups) == 1
    group = entry.key_record.ownership_groups[0]
    assert group.boundary_class is BoundaryClass.BOUNDARYLESS
    assert group.member_occurrence_indices == (0, 1)
    assert group.group_digest == sha256_hex("alphabeta")
    # the COMPLETE original proof is retained verbatim: the aggregate
    # bytes/digest only — the width of one distinct path never earns a
    # per-file member digest, and no per-file OffgraphSourceNode with a
    # guessed beta source is invented from the group.
    assert len(greedy.source_proofs) == 1
    assert entry.proof is greedy.source_proofs[0]
    assert entry.proof.source_text == "alphabeta"
    assert entry.proof.source_digest == sha256_hex("alphabeta")
    assert entry.proof.segments[0].member_digest is None
    assert tuple(m.normalized for m in entry.proof.requested_members) == (
        "A.md",
        "B.md",
    )
    assert greedy.offgraph_nodes == ()

    # an INDEPENDENTLY known offgraph B: the same boundaryless bundle
    # plus a standalone B read.  B.md is acquired (its own proven
    # single-occurrence source) but never graph-eligible, so it is
    # offgraph provenance in BOTH modes; lean still admits nothing and
    # greedy still admits only the whole bundle (no standalone B entry,
    # no per-file hash inferred from the group).
    for mode in (AdmissionMode.LEAN, AdmissionMode.GREEDY):
        payload_b = responses_payload(
            root_item("A.md"),
            exec_call("call-ab", "cat A.md B.md"),
            out_item("call-ab", frame_legacy("l1", "alphabeta")),
            exec_call("call-b", "cat B.md"),
            out_item("call-b", frame_legacy("l2", "beta")),
        )
        snapshot = single(payload_b, mode=mode)
        assert snapshot.outcome is AdmissionOutcome.COMPLETE
        offgraph = {n.path: n for n in snapshot.offgraph_nodes}
        assert set(offgraph) == {"B.md"}
        assert offgraph["B.md"].status is NodeStatus.ACQUIRED
        assert offgraph["B.md"].source_digest == sha256_hex("beta")
        eligible = {n.path: n for n in snapshot.eligibility_nodes}
        assert set(eligible) == {"AGENTS.md", "A.md"}
        assert eligible["A.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING
        if mode is AdmissionMode.LEAN:
            assert snapshot.entries == ()
        else:
            assert len(snapshot.entries) == 1
            assert snapshot.entries[0].key_record.member_occurrences == (
                "A.md",
                "B.md",
            )
            assert snapshot.entries[0].member_classes == (
                MemberClass.ELIGIBLE,
                MemberClass.GREEDY_BACKGROUND,
            )


def _partition_payload(member_refs: str, cmd: str, body: str) -> dict[str, Any]:
    return responses_payload(
        root_item(member_refs),
        exec_call("call-part", cmd),
        out_item("call-part", frame_legacy("l1", body)),
    )


def test_mixed_proven_partition_lean_no_splice_and_isolated_key_equality() -> None:
    """Proven AB|C partition (A eligible / B.py background / C eligible):
    lean admits ONLY the all-eligible C group (never splicing C onto the
    mixed boundaryless A+B.py group); the isolated-C key equals the
    standalone-C and guarded-one-iteration-loop-C keys (the order's
    canonical isolation law; the standalone keeps the IDENTICAL root
    text, which is key material); greedy admits the whole A+B.py+C with
    the per-occurrence authority vector."""
    boundary = "__BOUNDARY_018c__"
    whole_source = "alphabackgroundgamma"  # the slot bytes (markers excluded)
    payload = _partition_payload(
        "A.md C.md",
        f"cat A.md B.py && echo '{boundary}' && cat C.md",
        f"alphabackground{boundary}\ngamma",  # the echo's newline is the proven boundary
    )

    lean = single(payload)
    assert lean.outcome is AdmissionOutcome.COMPLETE
    assert len(lean.entries) == 1
    entry = lean.entries[0]
    assert entry.entry_class is EntryClass.FILE_BUNDLE_ENTRY
    assert entry.key_record.member_occurrences == ("C.md",)
    assert entry.member_classes == (MemberClass.ELIGIBLE,)
    assert entry.admitted_segments == (1,)  # the C group, never an A+C splice
    assert entry.key_record.aggregate_source_digest == sha256_hex("gamma")
    assert entry.width == 1
    group = entry.key_record.ownership_groups[0]
    assert group.boundary_class is BoundaryClass.PROVEN
    assert group.member_occurrence_indices == (0,)  # entry-local group (0)
    assert group.group_digest == sha256_hex("gamma")
    # the ORIGINAL proof keeps both segments and member positions untouched
    assert entry.proof is not None
    assert len(entry.proof.segments) == 2
    assert tuple(s.member_positions for s in entry.proof.segments) == ((0, 1), (2,))
    assert entry.proof.source_text == whole_source
    # mixed boundaryless group: A.md stays eligible content-missing,
    # C.md is acquired by its proven singleton segment, B.py is a group
    # supplier only (never an offgraph node) and no per-file hash is
    # invented for the group
    nodes = {n.path: n for n in lean.eligibility_nodes}
    assert nodes["A.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING
    assert nodes["C.md"].status is NodeStatus.ACQUIRED
    assert "B.py" not in nodes
    assert lean.offgraph_nodes == ()
    assert len(lean.source_proofs) == 1
    assert entry.proof is lean.source_proofs[0]

    greedy = single(payload, mode=AdmissionMode.GREEDY)
    assert greedy.outcome is AdmissionOutcome.COMPLETE
    assert len(greedy.entries) == 1
    gentry = greedy.entries[0]
    assert gentry.key_record.member_occurrences == ("A.md", "B.py", "C.md")
    assert gentry.member_classes == (
        MemberClass.ELIGIBLE,
        MemberClass.GREEDY_BACKGROUND,
        MemberClass.ELIGIBLE,
    )
    assert gentry.admitted_segments == (0, 1)
    assert gentry.key_record.aggregate_source_digest == sha256_hex(whole_source)

    # A|B|C with the background member in the middle: lean admits the
    # independently proven A and C groups SEPARATELY — exactly two
    # entries, never an A+C spliced entry.
    split = single(
        _partition_payload(
            "A.md C.md",
            "cat A.md && echo '__ONE_018c__' && cat B.py && echo '__TWO_018c__' && cat C.md",
            "alpha__ONE_018c__\nbackground__TWO_018c__\ngamma",
        )
    )
    assert split.outcome is AdmissionOutcome.COMPLETE
    assert {e.key_record.member_occurrences for e in split.entries} == {
        ("A.md",),
        ("C.md",),
    }

    # standalone C (its own read) and the guarded one-iteration loop C,
    # under the IDENTICAL root text, must have the SAME content key as
    # the isolated C (parser method is provenance, not key material).
    standalone = single(_partition_payload("A.md C.md", "cat C.md", "gamma"))
    loop = single(
        _partition_payload("A.md C.md", 'for f in C.md; do cat "$f" || exit 1; done', "gamma")
    )
    for other in (standalone, loop):
        assert other.outcome is AdmissionOutcome.COMPLETE
        assert len(other.entries) == 1
        assert other.entries[0].content_key == entry.content_key
        assert other.entries[0].key_record.root_digest == entry.key_record.root_digest


def test_zero_eligible_unrelated_singleton_neither_mode() -> None:
    """Zero eligible (unrelated singleton not referenced by the root):
    neither mode admits; the source stays offgraph provenance."""
    for mode in (AdmissionMode.LEAN, AdmissionMode.GREEDY):
        payload = responses_payload(
            root_item("A.md"),
            exec_call("call-b", "cat B.md"),
            out_item("call-b", frame_legacy("l1", "beta")),
        )
        snapshot = single(payload, mode=mode)
        assert snapshot.outcome is AdmissionOutcome.COMPLETE
        assert snapshot.entries == ()
        # A.md is referenced by the root (eligible, content-missing:
        # reachability is retained even though nothing is admitted);
        # B.md is acquired but unreachable (offgraph provenance).
        eligible = {n.path: n for n in snapshot.eligibility_nodes}
        assert set(eligible) == {"AGENTS.md", "A.md"}
        assert eligible["A.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING
        offgraph = {n.path: n for n in snapshot.offgraph_nodes}
        assert set(offgraph) == {"B.md"}
        assert offgraph["B.md"].status is NodeStatus.ACQUIRED
        assert offgraph["B.md"].source_digest == sha256_hex("beta")
        assert AdmissionLimitation.CANDIDATE_UNPROVEN in snapshot.diagnostics


def test_acquired_empty_singleton_reachable_admits() -> None:
    """An exact empty file read (EMPTY_SOURCE_SHA256) is a real
    acquired-empty source: reachable, width 1, admitted in both
    modes, never an unknown-hash fiction."""
    for mode in (AdmissionMode.LEAN, AdmissionMode.GREEDY):
        payload = responses_payload(
            root_item("A.md"),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("l1", "")),
        )
        snapshot = single(payload, mode=mode)
        assert snapshot.outcome is AdmissionOutcome.COMPLETE
        assert len(snapshot.entries) == 1
        entry = snapshot.entries[0]
        assert entry.key_record.member_occurrences == ("A.md",)
        assert entry.key_record.aggregate_source_digest == EMPTY_SOURCE_SHA256
        assert entry.width == 1
        assert entry.key_record.ownership_groups[0].group_digest == EMPTY_SOURCE_SHA256
        nodes = {n.path: n for n in snapshot.eligibility_nodes}
        assert nodes["A.md"].status is NodeStatus.ACQUIRED_EMPTY


def test_reachability_chain_missing_leaf() -> None:
    """root -> A (read) whose body references B: B stays a DISCOVERED
    CONTENT-MISSING eligibility node (no source is invented) and its
    own references are NOT followed (no acquisition, no bootstrap)."""
    payload = responses_payload(
        root_item("A.md"),
        exec_call("call-a", "cat A.md"),
        out_item("call-a", frame_legacy("l1", "alpha B.md")),
    )
    snapshot = single(payload)
    assert snapshot.outcome is AdmissionOutcome.COMPLETE
    nodes = {n.path: n for n in snapshot.eligibility_nodes}
    assert set(nodes) == {"AGENTS.md", "A.md", "B.md"}
    assert nodes["A.md"].status is NodeStatus.ACQUIRED
    assert nodes["B.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING
    assert nodes["B.md"].source_digest is None
    # A's read is admitted (whole, all-eligible singleton)
    assert len(snapshot.entries) == 1
    assert snapshot.entries[0].key_record.member_occurrences == ("A.md",)


def test_cycle_preserved_no_invented_eligibility() -> None:
    """A <-> B cycle: eligibility comes from the root (A), the cycle
    edges are retained with occurrence counts, and no depth is
    fabricated."""
    payload = responses_payload(
        root_item("A.md"),
        exec_call("call-a", "cat A.md"),
        out_item("call-a", frame_legacy("l1", "alpha B.md")),
        exec_call("call-b", "cat B.md"),
        out_item("call-b", frame_legacy("l1", "beta A.md")),
    )
    snapshot = single(payload)
    assert snapshot.outcome is AdmissionOutcome.COMPLETE
    nodes = {n.path: n for n in snapshot.eligibility_nodes}
    assert set(nodes) == {"AGENTS.md", "A.md", "B.md"}
    rels = {(r.referring_path, r.target_path): r for r in snapshot.ordinary_relationships}
    assert ("A.md", "B.md") in rels
    assert ("B.md", "A.md") in rels
    # both file reads are all-eligible singletons: two entries
    assert {e.key_record.member_occurrences for e in snapshot.entries} == {
        ("A.md",),
        ("B.md",),
    }


def _depth_preemption_payload(t_body: str) -> dict[str, Any]:
    """The order's depth-preemption vector: the boundaryless AB group
    earns T at depth 2 while the ordinary walk X->Y->T gives 3."""
    return responses_payload(
        root_item("A.md B.md X.md"),
        exec_call("call-ab", "cat A.md B.md"),
        out_item("call-ab", frame_legacy("c1", "T.md")),
        exec_call("call-x", "cat X.md"),
        out_item("call-x", frame_legacy("c1", "Y.md")),
        exec_call("call-y", "cat Y.md"),
        out_item("call-y", frame_legacy("c1", "T.md")),
        exec_call("call-t", "cat T.md"),
        out_item("call-t", frame_legacy("c1", t_body)),
    )


def test_group_certificate_depth_preemption_at_max_depth_2() -> None:
    """TRUE preemption: T's content is a non-reference, so the only
    derivations are the group certificate (depth 2) and the ordinary
    walk X->Y->T (depth 3).  The accepted old graph max_depth would
    refuse T at 3; the new c fixed point COMPLETEs at max_depth 2
    because the LEAST complete derivation is the certificate's 2."""
    snapshot = single(_depth_preemption_payload("leaf"), depth=2)
    assert snapshot.outcome is AdmissionOutcome.COMPLETE
    nodes = {n.path: n for n in snapshot.eligibility_nodes}
    assert set(nodes) == {
        "AGENTS.md",
        "A.md",
        "B.md",
        "X.md",
        "Y.md",
        "T.md",
    }
    certs = {c.target_path: c for c in snapshot.certificates}
    assert certs["T.md"].derivation_depth == 2
    assert certs["T.md"].supplier_occurrences == ("A.md", "B.md")
    # the longer ordinary walk is retained as occurrence evidence (no
    # fabricated shortest distance claim), but it never authorizes
    # admission over the least derivation
    rels = {(r.referring_path, r.target_path) for r in snapshot.ordinary_relationships}
    assert ("X.md", "Y.md") in rels
    assert ("Y.md", "T.md") in rels
    assert ("T.md", "U.md") not in rels


def test_least_derivation_descendant_relaxation() -> None:
    """DESCENDANT relaxation regression: T's body references U.md.  The
    group certificate earns T at depth 2 (after the ordinary walk first
    placed T at 3), so the re-scanned T must re-relax U to its LEAST
    derivation 3 (the old scan-once freeze would leave U at 4 and the
    max_depth 3 gate would wrongly refuse the whole snapshot)."""
    snapshot = single(_depth_preemption_payload("U.md"), depth=3)
    assert snapshot.outcome is AdmissionOutcome.COMPLETE
    nodes = {n.path: n for n in snapshot.eligibility_nodes}
    assert set(nodes) == {
        "AGENTS.md",
        "A.md",
        "B.md",
        "X.md",
        "Y.md",
        "T.md",
        "U.md",
    }
    assert nodes["U.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING
    certs = {c.target_path: c for c in snapshot.certificates}
    assert certs["T.md"].derivation_depth == 2
    rels = {(r.referring_path, r.target_path) for r in snapshot.ordinary_relationships}
    assert ("T.md", "U.md") in rels


def test_certificate_supplier_shortening_rederives() -> None:
    """An already-earned certificate must be re-derived when a
    supplier's least derivation shortens (here via a second
    certificate): T's depth follows 4 -> 3, and max_depth 3 is
    satisfied by the LEAST complete derivation only."""
    payload = responses_payload(
        root_item("A.md X.md B2.md"),
        # group G: boundaryless cat A.md S.md -> T.md (S initially at 3)
        exec_call("call-g", "cat A.md S.md"),
        out_item("call-g", frame_legacy("c1", "T.md")),
        # group G2: boundaryless cat A.md B2.md -> S.md (shallow suppliers)
        exec_call("call-g2", "cat A.md B2.md"),
        out_item("call-g2", frame_legacy("c1", "S.md")),
        # the long ordinary walk to S: X -> Y -> S
        exec_call("call-x", "cat X.md"),
        out_item("call-x", frame_legacy("c1", "Y.md")),
        exec_call("call-y", "cat Y.md"),
        out_item("call-y", frame_legacy("c1", "S.md")),
    )
    snapshot = single(payload, depth=3)
    assert snapshot.outcome is AdmissionOutcome.COMPLETE
    by_target: dict[str, list[Any]] = {}
    for cert in snapshot.certificates:
        by_target.setdefault(cert.target_path, []).append(cert)
    assert by_target["S.md"][0].derivation_depth == 2
    assert by_target["T.md"][0].derivation_depth == 3
    assert {n.path for n in snapshot.eligibility_nodes} == {
        "AGENTS.md",
        "A.md",
        "X.md",
        "B2.md",
        "Y.md",
        "S.md",
        "T.md",
    }


# --- Scoped diagnostic law (actual original API, stage caps) -----------
#
# Every stage enforces its OWN emitted conflicts plus the shared
# observation limitations, and the admission total cap always applies
# to the final output; shared early root/binding refusals belong to
# BOTH accepted graph/proof surfaces and cannot bypass either cap.
# The new composition must match the ACCEPTED old surface exactly
# (outcome, conflicts, observation limitations) under the same
# effective bounds, and no bound refusal retains a partial admission.


def _two_obs_payload() -> dict[str, Any]:
    """Two KNOWN observation limitations: A's read is nonzero (no
    complete output is proven) and B's result is a malformed wrapper;
    the root references both files."""
    return responses_payload(
        root_item("A.md B.md"),
        exec_call("synthetic-negative-a", "cat A.md"),
        out_item("synthetic-negative-a", frame_legacy("c1", "alpha", code=1)),
        exec_call("synthetic-negative-b", "cat B.md"),
        out_item("synthetic-negative-b", "synthetic malformed wrapper"),
    )


def _proof_source_payload() -> dict[str, Any]:
    """A proof-stage source refusal (10 UTF-8 bytes against a 5-byte
    per-body ceiling) plus ONE known observation limitation (B's
    nonzero read)."""
    return responses_payload(
        root_item("A.md"),
        exec_call("synthetic-large-first", "cat A.md"),
        out_item("synthetic-large-first", frame_legacy("c1", "abcdefghij")),
        exec_call("synthetic-nonzero-last", "cat B.md"),
        out_item("synthetic-nonzero-last", frame_legacy("c1", "beta", code=1)),
    )


def _no_root_two_obs_requests() -> tuple[GraphRequest, ...]:
    """The same two observed limitations with NO root (the explicit
    trusted context proves the workspace; no source authority is
    fabricated)."""
    return (
        GraphRequest(
            payload={"input": _two_obs_payload()["input"][1:]},
            endpoint="responses",
            context=PathContext(workspace=WORKSPACE),
        ),
    )


def _assert_matches_old_surface(
    old: Any,
    actual: BundleAdmissionSnapshot,
    *,
    outcome_value: str,
    conflict_values: list[str],
    obs_values: list[str],
) -> None:
    assert old.outcome.value == outcome_value
    assert [c.value for c in old.conflicts] == conflict_values
    assert [lim.value for lim in old.observation_limitations] == obs_values
    # the NEW admission matches the ACCEPTED old surface exactly
    assert actual.outcome.value == old.outcome.value
    assert [c.value for c in actual.conflicts] == [c.value for c in old.conflicts]
    assert [lim.value for lim in actual.observation_limitations] == [
        lim.value for lim in old.observation_limitations
    ]
    if old.outcome.value != "complete":
        assert actual.entries == ()
        assert actual.root_entry is None


@pytest.mark.parametrize("cap", [2, 1])
def test_known_graph_observation_limits_stage_scope(cap: int) -> None:
    """Initial known observation limitations honor the graph-stage cap
    BEFORE retention/append: at-limit 2 is COMPLETE with both
    limitations carried; 1 collapses to ONE DIAGNOSTICS_FULL with none
    copied (the old graph does exactly this)."""
    graph = GraphBounds(max_diagnostics=cap)
    reqs = (GraphRequest(payload=_two_obs_payload(), endpoint="responses", context=None),)
    old = observe_graph_batch(
        reqs,
        make_graph_namespace(
            IDENTITY,
            model_identity="synthetic-admission-model",
            config_fingerprint=FINGERPRINT,
            workspace=WORKSPACE,
            bounds=graph,
        ),
    )
    actual = observe_bundle_admission_batch(reqs, make_ns(graph_bounds=graph))
    if cap == 2:
        _assert_matches_old_surface(
            old,
            actual,
            outcome_value="complete",
            conflict_values=[],
            obs_values=["nonzero_exit", "unknown_completion"],
        )
        assert actual.outcome is AdmissionOutcome.COMPLETE
    else:
        _assert_matches_old_surface(
            old,
            actual,
            outcome_value="over_bound",
            conflict_values=["diagnostics_full"],
            obs_values=[],
        )
        assert actual.outcome is AdmissionOutcome.OVER_BOUND
        assert AdmissionLimitation.DIAGNOSTICS_FULL in actual.conflicts


# --- Direct namespace key forgery and scope key isolation ----------------


def _identity_with(**changes: str) -> RequestIdentity:
    base = {
        "principal": IDENTITY.principal,
        "session": IDENTITY.session,
        "repository": IDENTITY.repository,
        "route": IDENTITY.route,
    }
    base.update(changes)
    return RequestIdentity(**base)


def _perturbed_bounds(value: Any) -> Any:
    dump = value.model_dump()
    for name, current in dump.items():
        if isinstance(current, int) and current > 1:
            dump[name] = current - 1
            break
    else:
        raise AssertionError(f"no adjustable field on {type(value).__name__}")
    return type(value)(**dump)


def test_direct_namespace_key_forgery_refused() -> None:
    """Direct model construction recomputes BOTH 64-hex keys from the
    ACTUAL bound identity/versions/mode/all effective bound sets: a
    forged, stale or borrowed key (including keys of a different
    identity scope) does not construct, and the fixed refusal leaks
    no identity value."""
    import slaif_local_coding.constitution.bundles.bundle_admission_models as m

    ns = make_ns()
    data = ns.model_dump()
    other = make_bundle_admission_namespace(
        _identity_with(principal="synthetic-other-principal"),
        model_identity="synthetic-admission-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
    )
    field_forgery = {
        "principal": ns.principal + "-changed",
        "session": ns.session + "-changed",
        "repository": ns.repository + "-changed",
        "route": ns.route + "-changed",
        "model_identity": ns.model_identity + "-changed",
        "config_fingerprint": "1234567890abcdef" * 4,
        "mode": AdmissionMode.GREEDY,
        "workspace": "/other-work",
        "bounds": BundleAdmissionBounds(max_entries=127),
        "proof_bounds": _perturbed_bounds(ns.proof_bounds),
        "graph_bounds": GraphBounds(max_depth=63),
        "observation_bounds": _perturbed_bounds(ns.observation_bounds),
    }
    cases = [
        {"namespace_key": other.namespace_key, "scoped_key": other.scoped_key},
        {"namespace_key": "0" * 64, "scoped_key": ns.scoped_key},
        {"namespace_key": ns.namespace_key, "scoped_key": other.scoped_key},
    ]
    cases.extend({field: value} for field, value in field_forgery.items())
    for changes in cases:
        bad = dict(data)
        bad.update(changes)
        with pytest.raises(ValueError) as excinfo:
            m.BundleAdmissionNamespace(**bad)
        message = str(excinfo.value)
        assert "inconsistent with the bound identity" in message, changes
        assert "synthetic" not in message.lower(), changes


def test_namespace_scope_key_isolation() -> None:
    """Every ACTUAL scope dimension is semantic content-key material:
    the same observed root and reads under a namespace differing only
    in one of identity principal/session/repository/route, model,
    config fingerprint, workspace (root scope), mode, root content or
    any effective bound set yield DISTINCT structural keys (and a
    distinct scoped key where the law binds that dimension)."""
    payload = responses_payload(
        root_item("A.md"),
        exec_call("call-a", "cat A.md"),
        out_item("call-a", frame_legacy("l1", "alpha")),
    )
    base = make_ns()
    base_snapshot = observe_bundle_admission(payload, base, endpoint="responses")
    assert base_snapshot.outcome is AdmissionOutcome.COMPLETE
    assert base_snapshot.root_entry is not None
    file_key = base_snapshot.entries[0].content_key

    def workspace_payload(workspace: str) -> dict[str, Any]:
        return responses_payload(
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            f"# AGENTS.md instructions for {workspace}\n\n"
                            f"<INSTRUCTIONS>\nA.md\n</INSTRUCTIONS>\n"
                        ),
                    }
                ],
            },
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("l1", "alpha")),
        )

    workspace_variant = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-admission-model",
        config_fingerprint=FINGERPRINT,
        workspace="/other-work",
    )
    variants: list[tuple[str, BundleAdmissionNamespace, dict[str, Any]]] = [
        (
            "principal",
            make_bundle_admission_namespace(
                _identity_with(principal="synthetic-other-principal"),
                model_identity="synthetic-admission-model",
                config_fingerprint=FINGERPRINT,
                workspace=WORKSPACE,
            ),
            payload,
        ),
        (
            "session",
            make_bundle_admission_namespace(
                _identity_with(session="synthetic-other-session"),
                model_identity="synthetic-admission-model",
                config_fingerprint=FINGERPRINT,
                workspace=WORKSPACE,
            ),
            payload,
        ),
        (
            "repository",
            make_bundle_admission_namespace(
                _identity_with(repository="synthetic-other-repo"),
                model_identity="synthetic-admission-model",
                config_fingerprint=FINGERPRINT,
                workspace=WORKSPACE,
            ),
            payload,
        ),
        (
            "route",
            make_bundle_admission_namespace(
                _identity_with(route="synthetic-other-route"),
                model_identity="synthetic-admission-model",
                config_fingerprint=FINGERPRINT,
                workspace=WORKSPACE,
            ),
            payload,
        ),
        (
            "model",
            make_bundle_admission_namespace(
                IDENTITY,
                model_identity="synthetic-other-model",
                config_fingerprint=FINGERPRINT,
                workspace=WORKSPACE,
            ),
            payload,
        ),
        (
            "config",
            make_bundle_admission_namespace(
                IDENTITY,
                model_identity="synthetic-admission-model",
                config_fingerprint="1234567890abcdef" * 4,
                workspace=WORKSPACE,
            ),
            payload,
        ),
        ("workspace", workspace_variant, workspace_payload("/other-work")),
        ("mode", make_ns(mode=AdmissionMode.GREEDY), payload),
        (
            "root",
            make_ns(),
            responses_payload(
                root_item("A.md B.md"),
                exec_call("call-a", "cat A.md"),
                out_item("call-a", frame_legacy("l1", "alpha")),
            ),
        ),
        (
            "admission-bounds",
            make_ns(bounds=BundleAdmissionBounds(max_entries=127)),
            payload,
        ),
        (
            "proof-bounds",
            make_ns(proof_bounds=_perturbed_bounds(base.proof_bounds)),
            payload,
        ),
        ("graph-bounds", make_ns(depth=63), payload),
        (
            "observation-bounds",
            make_bundle_admission_namespace(
                IDENTITY,
                model_identity="synthetic-admission-model",
                config_fingerprint=FINGERPRINT,
                workspace=WORKSPACE,
                observation_bounds=_perturbed_bounds(base.observation_bounds),
            ),
            payload,
        ),
    ]
    for label, variant, variant_payload in variants:
        if label == "root":
            # Only the observed root content differs: the root digest
            # is content-key material, not scoped-key material, so the
            # scope stays exactly equal
            assert variant.scoped_key == base.scoped_key
        else:
            assert variant.scoped_key != base.scoped_key, label
        snapshot = observe_bundle_admission(variant_payload, variant, endpoint="responses")
        assert snapshot.outcome is AdmissionOutcome.COMPLETE, label
        assert snapshot.root_entry is not None, label
        assert snapshot.root_entry.content_key != base_snapshot.root_entry.content_key, label
        assert snapshot.entries[0].content_key != file_key, label
    # workspace is bound into the SCOPED key only: the same identity /
    # mode / bound sets keep the pre-root namespace key equal
    assert workspace_variant.namespace_key == base.namespace_key
    assert workspace_variant.scoped_key != base.scoped_key


# --- Original duplicate source groups: segment provenance + combined bound ---


def _duplicate_group_requests(root_text: str, endpoint: str) -> tuple[GraphRequest, ...]:
    """ONE original finite-plan read proving TWO separate identical AB
    groups at positions (0,1) and (2,3), each reference-bearing; the
    root request carries the legitimate effective Responses root."""
    command = "cat A.md B.md && echo '__GROUP_BOUNDARY__' && cat A.md B.md"
    frame = frame_legacy("g1", "C.md__GROUP_BOUNDARY__\nC.md")
    read = (
        responses_payload(exec_call("call-dup", command), out_item("call-dup", frame))
        if endpoint == "responses"
        else chat_payload(("call-dup", command, frame))
    )
    return (
        GraphRequest(
            payload=responses_payload(root_item(root_text)),
            endpoint="responses",
            context=None,
        ),
        GraphRequest(payload=read, endpoint=endpoint, context=None),
    )


def _proof_ns_for(ns: BundleAdmissionNamespace) -> Any:
    return make_bundle_proof_namespace(
        IDENTITY,
        model_identity=ns.model_identity,
        config_fingerprint=ns.config_fingerprint,
        workspace=ns.workspace,
        bounds=ns.proof_bounds,
        graph_bounds=ns.graph_bounds,
        observation_bounds=ns.observation_bounds,
    )


@pytest.mark.parametrize("endpoint", ["responses", "chat"])
@pytest.mark.parametrize(
    ("root_text", "all_eligible"),
    [
        ("A.md B.md", True),
        ("A.md", False),
        ("Z.md", False),
    ],
)
def test_duplicate_source_groups_original_segment_provenance(
    endpoint: str, root_text: str, all_eligible: bool
) -> None:
    """One original read with two SEPARATE identical AB groups keeps
    both original segment indices (0 and 1) in the group-owned
    records: the same carrier never collapses distinct original
    occurrences. All-eligible same-base suppliers earn two
    certificates; mixed or zero eligibility keeps two
    unresolved-origin records. The exact original 018-b proof is
    retained unchanged."""
    reqs = _duplicate_group_requests(root_text, endpoint)
    ns = make_ns(mode=AdmissionMode.GREEDY)
    baseline = observe_bundle_proofs(reqs, _proof_ns_for(ns))
    assert baseline.outcome is BundleProofOutcome.COMPLETE
    proof = baseline.bundles[0]
    assert [list(s.member_positions) for s in proof.segments] == [[0, 1], [2, 3]]
    snapshot = observe_bundle_admission_batch(reqs, ns)
    assert snapshot.outcome is AdmissionOutcome.COMPLETE
    records = snapshot.certificates if all_eligible else snapshot.unresolved_origins
    assert len(records) == 2
    assert {r.segment_index for r in records} == {0, 1}
    for record in records:
        assert record.request_index == proof.request_index
        assert record.carrier_location == proof.result_location
    assert snapshot.source_proofs == baseline.bundles


@pytest.mark.parametrize("endpoint", ["responses", "chat"])
def test_duplicate_groups_combined_relationship_bound(endpoint: str) -> None:
    """COMBINED ordinary relationships (root -> A, root -> B) plus the
    TWO distinct group certificates: at max_edges 4 the snapshot is
    COMPLETE; at 3 the whole snapshot refuses with no partial
    retention (separately typed facts, one effective bound)."""
    reqs = _duplicate_group_requests("A.md B.md", endpoint)
    at = observe_bundle_admission_batch(
        reqs, make_ns(mode=AdmissionMode.GREEDY, graph_bounds=GraphBounds(max_edges=4))
    )
    assert at.outcome is AdmissionOutcome.COMPLETE
    assert len(at.certificates) == 2
    over = observe_bundle_admission_batch(
        reqs, make_ns(mode=AdmissionMode.GREEDY, graph_bounds=GraphBounds(max_edges=3))
    )
    _assert_whole_empty_refusal(over, AdmissionLimitation.EDGES_OVER_BOUND)


# --- Structural key law, root idempotence, reverse index ----------------


def _n_singletons_payload(n: int) -> dict[str, Any]:
    """Root references n distinct files, each independently read: n
    eligible singletons (plus the required root)."""
    items = [root_item(" ".join(f"F{i}.md" for i in range(n)))]
    for i in range(n):
        items.append(exec_call(f"call-f{i}", f"cat F{i}.md"))
        items.append(out_item(f"call-f{i}", frame_legacy(f"l{i}", f"body{i}")))
    return responses_payload(*items)


def _interning_payload() -> dict[str, Any]:
    """AB then A then identical A again (three original reads); the
    root references BOTH members so the AB group is all-eligible."""
    return responses_payload(
        root_item("A.md B.md"),
        exec_call("call-ab", "cat A.md B.md"),
        out_item("call-ab", frame_legacy("l1", "alpha beta")),
        exec_call("call-a1", "cat A.md"),
        out_item("call-a1", frame_legacy("l2", "alpha")),
        exec_call("call-a2", "cat A.md"),
        out_item("call-a2", frame_legacy("l3", "alpha")),
    )


def test_structural_key_ordered_member_identity() -> None:
    """[A,B] and [B,A] over IDENTICAL root text and the SAME aggregate
    bytes are distinct keys: the ordered represented member
    occurrences are semantic key material."""
    ab = single(
        responses_payload(
            root_item("A.md B.md"),
            exec_call("call-ab", "cat A.md B.md"),
            out_item("call-ab", frame_legacy("l1", "alpha beta")),
        )
    )
    ba = single(
        responses_payload(
            root_item("A.md B.md"),
            exec_call("call-ba", "cat B.md A.md"),
            out_item("call-ba", frame_legacy("l1", "alpha beta")),
        )
    )
    # IDENTICAL root text: the root binding is held constant, so the
    # key difference can only be the ordered member occurrences
    assert ab.root_digest == ba.root_digest
    for snapshot in (ab, ba):
        assert snapshot.outcome is AdmissionOutcome.COMPLETE
        assert len(snapshot.entries) == 1
        assert snapshot.entries[0].key_record.aggregate_source_digest == sha256_hex("alpha beta")
    assert ab.entries[0].content_key != ba.entries[0].content_key


def test_same_aggregate_different_known_ownership() -> None:
    """Known boundaries are semantic compiler input: A="a"/B="bc" and
    A="ab"/B="c" have the SAME aggregate bytes but different known
    ownership, and both differ from the boundaryless AB proof of the
    same bytes (three keys, one digest)."""

    def partition(a: str, b: str) -> BundleAdmissionSnapshot:
        return single(
            responses_payload(
                root_item("A.md B.md"),
                exec_call("call-part", "cat A.md && echo 'MKR018c' && cat B.md"),
                out_item("call-part", frame_legacy("l1", f"{a}MKR018c\n{b}")),
            )
        )

    a_bc = partition("a", "bc")
    ab_c = partition("ab", "c")
    boundaryless = single(
        responses_payload(
            root_item("A.md B.md"),
            exec_call("call-ab", "cat A.md B.md"),
            out_item("call-ab", frame_legacy("l1", "abc")),
        )
    )
    keys = {
        a_bc.entries[0].content_key,
        ab_c.entries[0].content_key,
        boundaryless.entries[0].content_key,
    }
    assert len(keys) == 3
    for snapshot in (a_bc, ab_c, boundaryless):
        assert snapshot.outcome is AdmissionOutcome.COMPLETE
        assert snapshot.entries[0].key_record.aggregate_source_digest == sha256_hex("abc")


def test_root_vs_file_same_bytes_distinct_keys() -> None:
    """A file read at the root path with the SAME bytes is consistent
    (not competing roots) but the root key and the FILE key stay
    distinct: a file result never acquires root authority."""
    snapshot = single(
        responses_payload(
            root_item("AGENTS.md"),
            exec_call("call-agents", "cat AGENTS.md"),
            out_item("call-agents", frame_legacy("l1", "AGENTS.md")),
        )
    )
    assert snapshot.outcome is AdmissionOutcome.COMPLETE
    assert len(snapshot.entries) == 1
    entry = snapshot.entries[0]
    assert snapshot.root_entry is not None
    # both bind the identical aggregate source bytes
    assert snapshot.root_entry.key_record.aggregate_source_digest == sha256_hex("AGENTS.md")
    assert entry.key_record.aggregate_source_digest == sha256_hex("AGENTS.md")
    # but the classes (and therefore the keys) differ
    assert entry.entry_class is EntryClass.FILE_BUNDLE_ENTRY
    assert snapshot.root_entry.content_key != entry.content_key


def test_root_duplicate_idempotence() -> None:
    """Repeated byte- and scope-identical root envelopes deduplicate to
    ONE root entry while preserving their bounded original provenance
    (two envelope occurrences); the root counts once as a represented
    member / reverse association."""
    snapshot = single(
        responses_payload(
            root_item("A.md"),
            root_item("A.md"),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("l1", "alpha")),
        )
    )
    assert snapshot.outcome is AdmissionOutcome.COMPLETE
    assert snapshot.root_entry is not None
    assert len(snapshot.root_entry.envelope_occurrences) == 2
    assert snapshot.entries_retained == 2  # one root entry + one file entry
    assert snapshot.member_occurrences_charged == 2  # root (once) + A
    assert snapshot.reverse_association_attempts == 2
    # the duplicated root changes NOTHING about the keys: compare
    # against the single-identical-root control
    control = single(
        responses_payload(
            root_item("A.md"),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("l1", "alpha")),
        )
    )
    assert snapshot.root_entry is not None
    assert control.root_entry is not None
    assert snapshot.root_entry.content_key == control.root_entry.content_key
    assert snapshot.entries[0].content_key == control.entries[0].content_key


def test_full_reverse_index_with_greedy_background() -> None:
    """The reverse index maps EVERY represented path to ALL admitted
    content keys, including the greedy background member; the root row
    is flagged, and an independently known offgraph B.py read is
    retained as observation but never admitted (no standalone entry).
    The retained version observation carries the EXACT original
    request index and carrier of the accepted 018-b proof for the
    standalone B.py read."""
    payload = responses_payload(
        root_item("A.md"),
        exec_call("call-ab", "cat A.md B.py"),
        out_item("call-ab", frame_legacy("l1", "alphabackground")),
        exec_call("call-a", "cat A.md"),
        out_item("call-a", frame_legacy("l2", "alpha")),
        exec_call("call-b", "cat B.py"),
        out_item("call-b", frame_legacy("l3", "background")),
    )
    snapshot = single(payload, mode=AdmissionMode.GREEDY)
    assert snapshot.outcome is AdmissionOutcome.COMPLETE
    ab_key = next(
        e.content_key
        for e in snapshot.entries
        if e.key_record.member_occurrences == ("A.md", "B.py")
    )
    a_key = next(
        e.content_key for e in snapshot.entries if e.key_record.member_occurrences == ("A.md",)
    )
    associations = {p.path: p for p in snapshot.path_associations}
    assert set(associations) == {"AGENTS.md", "A.md", "B.py"}
    root_row = associations["AGENTS.md"]
    assert snapshot.root_entry is not None
    assert root_row.is_root is True
    assert root_row.content_keys == (snapshot.root_entry.content_key,)
    assert associations["A.md"].content_keys == tuple(sorted((a_key, ab_key)))
    assert associations["A.md"].is_root is False
    # B.py is represented ONLY by the greedy bundle: the standalone
    # read is offgraph provenance, never an admitted entry
    assert associations["B.py"].content_keys == (ab_key,)
    assert {e.key_record.member_occurrences for e in snapshot.entries} == {
        ("A.md", "B.py"),
        ("A.md",),
    }
    offgraph = {n.path: n for n in snapshot.offgraph_nodes}
    assert set(offgraph) == {"B.py"}
    assert offgraph["B.py"].status is NodeStatus.ACQUIRED
    assert offgraph["B.py"].source_digest == sha256_hex("background")
    # the standalone nonadmitted B.py read is retained as a source
    # VERSION observation with its digest, request index and the
    # EXACT original carrier of the accepted 018-b proof for call-b
    observations = {v.path: v for v in snapshot.version_observations}
    b_obs = observations["B.py"]
    assert b_obs.content_digest == sha256_hex("background")
    ns = make_ns(mode=AdmissionMode.GREEDY)
    proof_ns = make_bundle_proof_namespace(
        IDENTITY,
        model_identity=ns.model_identity,
        config_fingerprint=ns.config_fingerprint,
        workspace=ns.workspace,
        bounds=ns.proof_bounds,
        graph_bounds=ns.graph_bounds,
        observation_bounds=ns.observation_bounds,
    )
    baseline = observe_bundle_proofs(
        (GraphRequest(payload=payload, endpoint="responses", context=None),),
        proof_ns,
    )
    b_proof = next(p for p in baseline.bundles if p.call_id == "call-b")
    assert b_obs.request_index == b_proof.request_index
    assert b_obs.carrier_location == b_proof.result_location


# --- Effective bound law: defaults, ceilings, at-limit / one-over -------


def test_admission_bound_ceilings_refuse_wider() -> None:
    """Admission defaults AND hard ceilings: 128 / 1024 / 4096 / 64.
    At-ceiling construction is accepted; wider is refused."""
    for field, ceiling in (
        ("max_entries", 128),
        ("max_member_occurrences", 1024),
        ("max_reverse_associations", 4096),
        ("max_diagnostics", 64),
    ):
        BundleAdmissionBounds(**{field: ceiling})
        with pytest.raises(ValueError):
            BundleAdmissionBounds(**{field: ceiling + 1})


def _assert_whole_empty_refusal(
    snapshot: BundleAdmissionSnapshot, reason: AdmissionLimitation
) -> None:
    assert snapshot.outcome is AdmissionOutcome.OVER_BOUND
    assert reason in snapshot.conflicts
    assert snapshot.entries == ()
    assert snapshot.root_entry is None


def test_admission_bound_at_limit_one_over() -> None:
    """Every admission bound: at-limit succeeds, first over refuses the
    WHOLE snapshot (no partial admission)."""
    # max_entries: the root counts as one retained entry
    at = single(_n_singletons_payload(1), bounds=BundleAdmissionBounds(max_entries=2))
    assert at.outcome is AdmissionOutcome.COMPLETE
    assert at.entries_retained == 2  # root + one file entry
    over = single(_n_singletons_payload(2), bounds=BundleAdmissionBounds(max_entries=2))
    _assert_whole_empty_refusal(over, AdmissionLimitation.ENTRIES_OVER_BOUND)

    # max_member_occurrences: the root counts as one represented member
    single_read = responses_payload(
        root_item("A.md"),
        exec_call("call-a", "cat A.md"),
        out_item("call-a", frame_legacy("l1", "alpha")),
    )
    at = single(single_read, bounds=BundleAdmissionBounds(max_member_occurrences=2))
    assert at.outcome is AdmissionOutcome.COMPLETE
    assert at.member_occurrences_charged == 2  # root + A
    group2 = responses_payload(
        root_item("A.md B.md"),
        exec_call("call-ab", "cat A.md B.md"),
        out_item("call-ab", frame_legacy("l1", "alpha beta")),
    )
    over = single(group2, bounds=BundleAdmissionBounds(max_member_occurrences=2))
    _assert_whole_empty_refusal(over, AdmissionLimitation.MEMBER_OCCURRENCES_OVER_BOUND)

    # max_reverse_associations: every ACTUAL attempt is charged before
    # dedup (repeated A+A is three attempts: root + A + A)
    repeated = responses_payload(
        root_item("A.md"),
        exec_call("call-aa", "cat A.md A.md"),
        out_item("call-aa", frame_legacy("l1", "aa")),
    )
    at = single(repeated, bounds=BundleAdmissionBounds(max_reverse_associations=3))
    assert at.outcome is AdmissionOutcome.COMPLETE
    assert at.reverse_association_attempts == 3
    over = single(repeated, bounds=BundleAdmissionBounds(max_reverse_associations=2))
    _assert_whole_empty_refusal(over, AdmissionLimitation.REVERSE_ASSOCIATIONS_OVER_BOUND)
    # the interning shape (AB, A, A again) is five attempts
    at = single(_interning_payload(), bounds=BundleAdmissionBounds(max_reverse_associations=5))
    assert at.outcome is AdmissionOutcome.COMPLETE
    assert at.reverse_association_attempts == 5
    over = single(_interning_payload(), bounds=BundleAdmissionBounds(max_reverse_associations=4))
    _assert_whole_empty_refusal(over, AdmissionLimitation.REVERSE_ASSOCIATIONS_OVER_BOUND)

    # max_diagnostics: the TOTAL emitted closed-enum diagnostics
    # (conflicts + admission diagnostics + deduplicated shared
    # observation limitations): the known two-observation payload
    # emits exactly one output_inconsistent diagnostic plus
    # nonzero_exit + unknown_completion, so TOTAL 3 is at-limit and
    # 2 crosses with a typed whole-empty refusal
    at = single(_two_obs_payload(), bounds=BundleAdmissionBounds(max_diagnostics=3))
    assert at.outcome is AdmissionOutcome.COMPLETE
    assert [d.value for d in at.diagnostics] == ["output_inconsistent"]
    assert [lim.value for lim in at.observation_limitations] == [
        "nonzero_exit",
        "unknown_completion",
    ]
    assert at.conflicts == ()
    over = single(_two_obs_payload(), bounds=BundleAdmissionBounds(max_diagnostics=2))
    _assert_whole_empty_refusal(over, AdmissionLimitation.DIAGNOSTICS_FULL)


def _all_suppliers_payload() -> dict[str, Any]:
    """root -> {A,B}; boundaryless AB -> C; C read.  Exact cumulative
    source charge: the inspected root body is the 9 UTF-8 byte literal
    'A.md B.md' (the extracted INSTRUCTIONS body) + 4 (AB body 'C.md')
    + 4 (C body 'leaf') + 8 (the closure's owned segment re-exposures)
    = 25; 3 candidate references, 2 ordinary relationships + 1 group
    certificate, 16 work units."""
    return responses_payload(
        root_item("A.md B.md"),
        exec_call("call-ab", "cat A.md B.md"),
        out_item("call-ab", frame_legacy("c1", "C.md")),
        exec_call("call-c", "cat C.md"),
        out_item("call-c", frame_legacy("c1", "leaf")),
    )


def test_graph_bound_at_limit_one_over() -> None:
    """Every ACTUAL effective graph bound: at-limit succeeds, first
    over refuses the whole snapshot with its fixed typed reason."""
    payload = _all_suppliers_payload()

    def run(graph: GraphBounds) -> BundleAdmissionSnapshot:
        return observe_bundle_admission(payload, make_ns(graph_bounds=graph), endpoint="responses")

    baseline = run(GraphBounds())
    assert baseline.outcome is AdmissionOutcome.COMPLETE
    assert baseline.work_units == 16

    cases = (
        ({"max_edges": 3}, AdmissionLimitation.EDGES_OVER_BOUND),
        ({"max_documents": 3}, AdmissionLimitation.DOCUMENT_OVER_BOUND),
        (
            {"max_reference_candidates_total": 3},
            AdmissionLimitation.CANDIDATES_TOTAL_OVER_BOUND,
        ),
        (
            {"max_reference_candidates_per_document": 2},
            AdmissionLimitation.CANDIDATES_PER_DOCUMENT_OVER_BOUND,
        ),
        (
            {"max_work_units": baseline.work_units},
            AdmissionLimitation.WORK_UNITS_EXHAUSTED,
        ),
        (
            {"max_single_source_bytes": 9},
            AdmissionLimitation.SOURCE_OVER_BOUND,
        ),
        (
            {"max_total_inspected_source_bytes": 25},
            AdmissionLimitation.TOTAL_SOURCE_OVER_BOUND,
        ),
    )
    for kwargs, reason in cases:
        field = next(iter(kwargs))
        at = run(GraphBounds(**kwargs))
        assert at.outcome is AdmissionOutcome.COMPLETE, field
        over = run(GraphBounds(**{field: kwargs[field] - 1}))
        _assert_whole_empty_refusal(over, reason)


def test_max_depth_least_derivation_at_limit_one_over() -> None:
    """max_depth applies to the LEAST complete derivation: the chain
    A -> B -> C reaches C at depth 3, so at-limit 3 is COMPLETE and
    one-over 2 refuses the whole snapshot (no silent lost
    reachability)."""
    payload = responses_payload(
        root_item("A.md"),
        exec_call("call-a", "cat A.md"),
        out_item("call-a", frame_legacy("l1", "B.md")),
        exec_call("call-b", "cat B.md"),
        out_item("call-b", frame_legacy("l2", "C.md")),
        exec_call("call-c", "cat C.md"),
        out_item("call-c", frame_legacy("l3", "gamma")),
    )
    at = single(payload, depth=3)
    assert at.outcome is AdmissionOutcome.COMPLETE
    assert {n.path for n in at.eligibility_nodes} == {
        "AGENTS.md",
        "A.md",
        "B.md",
        "C.md",
    }
    over = single(payload, depth=2)
    _assert_whole_empty_refusal(over, AdmissionLimitation.DERIVATION_DEPTH_OVER_BOUND)


# --- Inherited limit propagation (durable 72 ROOT controls) -------------
#
# Durable port of the 72 known-synthetic controls that ROOT executed
# against the 018-c final source (the final-limit-propagation probe):
# the remaining graph node/batch ceilings, the inherited proof
# budgets (bundle/member counts, segment slots, marker and the exact
# cumulative marker-search windows) and BOTH path ceilings, exercised
# on BOTH read endpoints in BOTH namespace modes through the ORIGINAL
# admission batch API.  A crossed path ceiling is a per-candidate
# nonacquisition (COMPLETE outcome, root retained, no file entries,
# at least one typed limitation), never a fabricated global
# whole-empty failure.  Every payload is inline known-synthetic; no S
# runtime path dependency.


def _limit_requests(
    root: str, reads: tuple[tuple[str, str], ...], endpoint: str
) -> tuple[GraphRequest, GraphRequest]:
    """Root envelope request (Responses-only root authority) plus one
    read request on the given endpoint."""
    items: list[dict[str, Any]] = [root_item(root)]
    frames: list[tuple[str, str, str]] = []
    for index, (cmd, body) in enumerate(reads):
        cid = f"synthetic-limit-{index}"
        frame = frame_legacy("c1", body)
        if endpoint == "responses":
            items.extend((exec_call(cid, cmd), out_item(cid, frame)))
        else:
            frames.append((cid, cmd, frame))
    if endpoint == "responses":
        read_payload: dict[str, Any] = {"input": items[1:]}
    else:
        read_payload = chat_payload(*frames)
    return (
        GraphRequest(payload={"input": [items[0]]}, endpoint="responses", context=None),
        GraphRequest(payload=read_payload, endpoint=endpoint, context=None),
    )


def _limit_check(
    label: str,
    endpoint: str,
    mode: AdmissionMode,
    requests: tuple[GraphRequest, GraphRequest],
    ns: BundleAdmissionNamespace,
    *,
    complete: bool,
    reason: str | None = None,
    nonacquisition: bool = False,
) -> None:
    """The exact probe pass criterion over ONE original batch, with
    the original payloads required to stay byte-identical."""
    original = [copy.deepcopy(r.payload) for r in requests]
    snap = observe_bundle_admission_batch(requests, ns)
    values = [x.value for x in (*snap.conflicts, *snap.diagnostics, *snap.observation_limitations)]
    if nonacquisition:
        ok = (
            snap.outcome is AdmissionOutcome.COMPLETE
            and snap.root_entry is not None
            and not snap.entries
            and bool(values)
        )
    elif complete:
        ok = (
            snap.outcome is AdmissionOutcome.COMPLETE
            and snap.root_entry is not None
            and bool(snap.entries)
        )
    else:
        ok = (
            snap.outcome is AdmissionOutcome.OVER_BOUND
            and reason in [x.value for x in snap.conflicts]
            and snap.root_entry is None
            and not snap.entries
            and not snap.source_proofs
        )
    assert ok, (
        f"{label} ({endpoint}/{mode.value}): outcome={snap.outcome.value} "
        f"reasons={values} entries={len(snap.entries)}"
    )
    assert [r.payload for r in requests] == original, f"{label}: original payload mutated"


@pytest.mark.parametrize("mode", [AdmissionMode.LEAN, AdmissionMode.GREEDY])
@pytest.mark.parametrize("endpoint", ["responses", "chat"])
def test_inherited_limit_propagation_matrix(mode: AdmissionMode, endpoint: str) -> None:
    group = _limit_requests(
        "A.md B.md", (("cat A.md B.md", "C.md"), ("cat C.md", "leaf")), endpoint
    )
    for cap in (4, 3):
        _limit_check(
            f"graph_nodes_{cap}",
            endpoint,
            mode,
            group,
            make_ns(mode, graph_bounds=GraphBounds(max_nodes=cap)),
            complete=(cap == 4),
            reason="nodes_over_bound",
        )
    single = _limit_requests("A.md", (("cat A.md", "alpha"),), endpoint)
    for cap in (2, 1):
        _limit_check(
            f"graph_requests_{cap}",
            endpoint,
            mode,
            single,
            make_ns(mode, graph_bounds=GraphBounds(max_requests=cap)),
            complete=(cap == 2),
            reason="batch_over_bound",
        )
    two = _limit_requests("A.md B.md", (("cat A.md", "alpha"), ("cat B.md", "beta")), endpoint)
    for cap in (2, 1):
        _limit_check(
            f"proof_bundles_{cap}",
            endpoint,
            mode,
            two,
            make_ns(mode, proof_bounds=BundleProofBounds(max_bundles=cap)),
            complete=(cap == 2),
            reason="bundles_over_bound",
        )
    members = _limit_requests("A.md B.md", (("cat A.md B.md", "alphabeta"),), endpoint)
    for cap in (2, 1):
        _limit_check(
            f"proof_members_{cap}",
            endpoint,
            mode,
            members,
            make_ns(mode, proof_bounds=BundleProofBounds(max_members=cap)),
            complete=(cap == 2),
            reason="members_over_bound",
        )
    segments = _limit_requests(
        "A.md B.md C.md",
        (
            (
                "cat A.md && echo 'M1' && cat B.md && echo 'M2' && cat C.md && echo 'M3'",
                "alphaM1\nbetaM2\ngammaM3\n",
            ),
        ),
        endpoint,
    )
    for cap in (4, 3):
        _limit_check(
            f"proof_segments_{cap}",
            endpoint,
            mode,
            segments,
            make_ns(mode, proof_bounds=BundleProofBounds(max_segments=cap)),
            complete=(cap == 4),
            reason="segments_over_bound",
        )
    marker = _limit_requests(
        "A.md B.md", (("cat A.md && echo 'MM' && cat B.md", "alphaMM\nbeta"),), endpoint
    )
    for cap in (3, 2):
        _limit_check(
            f"proof_marker_{cap}",
            endpoint,
            mode,
            marker,
            make_ns(mode, proof_bounds=BundleProofBounds(max_marker=cap)),
            complete=(cap == 3),
            reason="marker_over_bound",
        )
    search = _limit_requests(
        "A.md B.md C.md D.md",
        (
            ("cat A.md && echo 'M' && cat B.md", "alphaM\nbeta"),
            ("cat C.md && echo 'N' && cat D.md", "gammaN\ndelta"),
        ),
        endpoint,
    )
    for cap in (23, 22):
        _limit_check(
            f"proof_marker_search_{cap}",
            endpoint,
            mode,
            search,
            make_ns(mode, proof_bounds=BundleProofBounds(max_marker_search=cap)),
            complete=(cap == 23),
            reason="marker_search_over_bound",
        )
    long_name = "LONGNAME.md"
    path_len = len(long_name.encode("utf-8"))
    path_reqs = _limit_requests(long_name, ((f"cat {long_name}", "leaf"),), endpoint)
    for scope in ("graph", "observation"):
        for cap in (path_len, path_len - 1):
            if scope == "graph":
                ns = make_ns(mode, graph_bounds=GraphBounds(max_path_bytes=cap))
            else:
                ns = make_bundle_admission_namespace(
                    IDENTITY,
                    model_identity="synthetic-admission-model",
                    config_fingerprint=FINGERPRINT,
                    workspace=WORKSPACE,
                    mode=mode,
                    observation_bounds=ObservationBounds(max_path_bytes=cap),
                )
            _limit_check(
                f"{scope}_member_path_{cap}",
                endpoint,
                mode,
                path_reqs,
                ns,
                complete=(cap == path_len),
                nonacquisition=(cap < path_len),
            )


# --- Actual supported-version refusal -------------------------------------


def test_actual_version_refusals_whole_empty() -> None:
    """Each ACTUAL supported version bound into the namespace: a
    coherent direct construction with an unsupported version (checksums
    recomputed, so this tests actual support, not forgery detection)
    refuses the whole snapshot with VERSION_UNSUPPORTED."""
    import slaif_local_coding.constitution.bundles.bundle_admission_models as m

    payload = responses_payload(
        root_item("A.md"),
        exec_call("call-a", "cat A.md"),
        out_item("call-a", frame_legacy("l1", "alpha")),
    )
    reqs = (GraphRequest(payload=payload, endpoint="responses", context=None),)
    ns = make_ns()
    for field in (
        "admission_version",
        "graph_version",
        "reference_version",
        "proof_version",
        "observation_version",
    ):
        data = ns.model_dump()
        data[field] = "synthetic-unsupported/v999"
        canonical = m._canonical_namespace_fields(
            principal=data["principal"],
            session=data["session"],
            repository=data["repository"],
            route=data["route"],
            model_identity=data["model_identity"],
            config_fingerprint=data["config_fingerprint"],
            admission_version=data["admission_version"],
            graph_version=data["graph_version"],
            reference_version=data["reference_version"],
            proof_version=data["proof_version"],
            observation_version=data["observation_version"],
            mode=ns.mode.value,
            bounds=ns.bounds,
            proof_bounds=ns.proof_bounds,
            graph_bounds=ns.graph_bounds,
            observation_bounds=ns.observation_bounds,
        )
        data["namespace_key"] = hashlib.sha256(canonical).hexdigest()
        data["scoped_key"] = sha256_hex(data["namespace_key"] + "\0" + ns.workspace)
        changed = m.BundleAdmissionNamespace(**data)
        assert changed.namespace_key != ns.namespace_key
        snapshot = observe_bundle_admission_batch(reqs, changed)
        assert snapshot.outcome is AdmissionOutcome.VERSION_CONFLICT, field
        assert AdmissionLimitation.VERSION_UNSUPPORTED in snapshot.conflicts
        assert snapshot.entries == ()
        assert snapshot.root_entry is None


# --- Purity, operational privacy, unchanged original payload -------------


def test_public_purity_privacy_and_payload_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The public path performs NO host IO, leaves the ORIGINAL payload
    byte-unchanged, and operational repr never echoes source bytes,
    private call IDs or identity values."""
    rootcanary = "SYNTHETIC-ROOT-PRIVATE-CANARY"
    filecanary = "SYNTHETIC-FILE-PRIVATE-CANARY"
    principal_canary = "SYNTHETIC-PRINCIPAL-CANARY"
    session_canary = "SYNTHETIC-SESSION-CANARY"
    payload = responses_payload(
        root_item("A.md"),
        exec_call("call-canary", "cat A.md"),
        out_item("call-canary", frame_legacy("l1", "alpha")),
    )
    payload["input"][0]["content"][0]["text"] = payload["input"][0]["content"][0]["text"].replace(
        "</INSTRUCTIONS>", f"{rootcanary}\n</INSTRUCTIONS>"
    )
    payload["input"][2]["output"] = (
        payload["input"][2]["output"].split("Output:", 1)[0] + "Output:\n" + filecanary
    )
    identity = RequestIdentity(
        principal=principal_canary,
        session=session_canary,
        repository="synthetic",
        route="synthetic",
    )
    ns = make_bundle_admission_namespace(
        identity,
        model_identity="synthetic",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
    )
    original = copy.deepcopy(payload)
    attempts: list[str] = []

    def deny(name: str) -> Any:
        def fn(*args: Any, **kwargs: Any) -> Any:
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

    snapshot = observe_bundle_admission(payload, ns, endpoint="responses")

    assert snapshot.outcome is AdmissionOutcome.COMPLETE
    assert payload == original  # original payload unchanged
    assert not attempts  # no host IO facility touched
    canaries = (rootcanary, filecanary, principal_canary, session_canary)
    for text in (repr(snapshot), str(snapshot)):
        for canary in canaries:
            assert canary not in text
    for record in (*snapshot.entries, snapshot.root_entry, *snapshot.source_proofs):
        for canary in canaries:
            assert canary not in repr(record)


@pytest.mark.parametrize("cap", [3, 2])
def test_graph_work_refusal_kept_or_collapsed_by_cap(cap: int) -> None:
    """A graph work refusal (max_work_units 1) plus the two known
    observation limitations: cap 3 retains the original work reason +
    2 obs; cap 2 (3 > cap) normalizes to DIAGNOSTICS_FULL with no
    copied obs."""
    graph = GraphBounds(max_diagnostics=cap, max_work_units=1)
    reqs = (GraphRequest(payload=_two_obs_payload(), endpoint="responses", context=None),)
    old = observe_graph_batch(
        reqs,
        make_graph_namespace(
            IDENTITY,
            model_identity="synthetic-admission-model",
            config_fingerprint=FINGERPRINT,
            workspace=WORKSPACE,
            bounds=graph,
        ),
    )
    actual = observe_bundle_admission_batch(reqs, make_ns(graph_bounds=graph))
    if cap == 3:
        _assert_matches_old_surface(
            old,
            actual,
            outcome_value="over_bound",
            conflict_values=["work_units_exhausted"],
            obs_values=["nonzero_exit", "unknown_completion"],
        )
        assert AdmissionLimitation.WORK_UNITS_EXHAUSTED in actual.conflicts
    else:
        _assert_matches_old_surface(
            old,
            actual,
            outcome_value="over_bound",
            conflict_values=["diagnostics_full"],
            obs_values=[],
        )
        assert AdmissionLimitation.DIAGNOSTICS_FULL in actual.conflicts


@pytest.mark.parametrize("cap", [2, 1])
def test_proof_source_refusal_stage_scope(cap: int) -> None:
    """A proof-stage source refusal (a 10-byte body against the 5-byte
    ceiling) plus one known observation limitation: cap 2 retains the
    original source reason + 1 obs; cap 1 (2 > cap) normalizes to
    DIAGNOSTICS_FULL with no copied obs."""
    graph = GraphBounds(max_single_source_bytes=5)
    proof = BundleProofBounds(max_diagnostics=cap)
    reqs = (GraphRequest(payload=_proof_source_payload(), endpoint="responses", context=None),)
    old = observe_bundle_proofs(
        reqs,
        make_bundle_proof_namespace(
            IDENTITY,
            model_identity="synthetic-admission-model",
            config_fingerprint=FINGERPRINT,
            workspace=WORKSPACE,
            graph_bounds=graph,
            bounds=proof,
        ),
    )
    actual = observe_bundle_admission_batch(reqs, make_ns(graph_bounds=graph, proof_bounds=proof))
    if cap == 2:
        _assert_matches_old_surface(
            old,
            actual,
            outcome_value="over_bound",
            conflict_values=["source_over_bound"],
            obs_values=["nonzero_exit"],
        )
        assert AdmissionLimitation.SOURCE_OVER_BOUND in actual.conflicts
    else:
        _assert_matches_old_surface(
            old,
            actual,
            outcome_value="over_bound",
            conflict_values=["diagnostics_full"],
            obs_values=[],
        )
        assert AdmissionLimitation.DIAGNOSTICS_FULL in actual.conflicts


@pytest.mark.parametrize("stage", ["graph", "proof"])
@pytest.mark.parametrize("cap", [3, 2])
def test_early_no_root_stage_scope(stage: str, cap: int) -> None:
    """A shared EARLY no-root refusal with two observed limitations
    belongs to BOTH accepted surfaces: the capped stage keeps NO_ROOT +
    2 obs at 3 and collapses to DIAGNOSTICS_FULL at 2 while the other
    stage stays at its 64 default."""
    graph = GraphBounds(max_diagnostics=cap if stage == "graph" else 64)
    proof = BundleProofBounds(max_diagnostics=cap if stage == "proof" else 64)
    reqs = _no_root_two_obs_requests()
    if stage == "graph":
        old: Any = observe_graph_batch(
            reqs,
            make_graph_namespace(
                IDENTITY,
                model_identity="synthetic-admission-model",
                config_fingerprint=FINGERPRINT,
                workspace=WORKSPACE,
                bounds=graph,
            ),
        )
    else:
        old = observe_bundle_proofs(
            reqs,
            make_bundle_proof_namespace(
                IDENTITY,
                model_identity="synthetic-admission-model",
                config_fingerprint=FINGERPRINT,
                workspace=WORKSPACE,
                graph_bounds=graph,
                bounds=proof,
            ),
        )
    actual = observe_bundle_admission_batch(reqs, make_ns(graph_bounds=graph, proof_bounds=proof))
    if cap == 3:
        _assert_matches_old_surface(
            old,
            actual,
            outcome_value="no_root",
            conflict_values=["no_root"],
            obs_values=["nonzero_exit", "unknown_completion"],
        )
        assert actual.outcome is AdmissionOutcome.NO_ROOT
        assert AdmissionLimitation.NO_ROOT in actual.conflicts
    else:
        _assert_matches_old_surface(
            old,
            actual,
            outcome_value="over_bound",
            conflict_values=["diagnostics_full"],
            obs_values=[],
        )
        assert actual.outcome is AdmissionOutcome.OVER_BOUND
        assert AdmissionLimitation.DIAGNOSTICS_FULL in actual.conflicts
