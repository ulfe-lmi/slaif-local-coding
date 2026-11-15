"""018-c: durable known-synthetic original-input matrix.

The four versioned fixture files under ``tests/fixtures/cache_admission/v1/``
are VERBATIM copies of the review-target vector files (known-synthetic
ORIGINAL API inputs only; command strings are data and are never
executed):

- ``admission_original_inputs_v1.json``
  (S/probes/018-c-original-input-vectors-v1.json, sha256
  ``8dd49c3110101a624a030575942ba1e8f96b42f13b43d2e1d23eb2c7fe62bb97``)
- ``admission_native_inputs_v1.json``
  (S/probes/018-c-native-input-vectors-v1.json, sha256
  ``c820bba99001d4a07e5e91f6b8c69e5df7aab665e3dac22fa5d33ff4fe6a60dd``)
- ``admission_group_depth_preemption_v1.json``
  (S/probes/018-c-group-depth-preemption-vectors-v1.json, sha256
  ``dece27c005bdcbeb6077d74a4c28a4a0ecee673a1247e259ba6c4f054f7fbfe3``)
- ``admission_interning_provenance_v1.json``
  (S/probes/018-c-interning-provenance-vectors-v1.json, sha256
  ``4b78275ab41c5128023ffd9ede43f7c6f1fc4e69331f29cee4401e93423b37f5``)

The fixture ``expectation`` labels are review targets, not test
results; the assertions below are the ACTUAL required semantics:
positive complete-output/read-grammar preconditions (every original
proof retained in ``source_proofs`` with its exact source bytes),
eligibility (independent root reachability, ``DISCOVERED_CONTENT_MISSING``
preserved), the lean/greedy truth table, the all-eligible common-base
group-certificate law (different bases and mixed eligibility stay
unresolved-origin evidence), the LEAST complete AND/OR derivation depth
after the bounded fixed point (accepted ``max_depth`` never pre-empts a
valid shorter new group derivation), the canonical structural content
key (parser method and original coordinates are provenance, not key
material) and the complete reverse index.  The legitimate effective
Responses root is always additionally required.  No model, native,
client or service facility is started.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from slaif_local_coding.constitution.bundles import (
    BoundaryClass,
    GraphBounds,
    GraphRequest,
    MemberClass,
    NodeStatus,
    make_bundle_proof_namespace,
    observe_bundle_admission_batch,
    observe_bundle_proofs,
)
from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
    AdmissionOutcome,
    make_bundle_admission_namespace,
)
from slaif_local_coding.constitution.bundles.bundle_proof_models import (
    BundleProofOutcome,
)
from slaif_local_coding.constitution.cache import RequestIdentity

FIXTURES = Path(__file__).parent / "fixtures" / "cache_admission" / "v1"
IDENTITY = RequestIdentity(
    principal="synthetic-vector-principal",
    session="synthetic-vector-session",
    repository="synthetic-vector-repo",
    route="synthetic-vector-route",
)
FINGERPRINT = "abcdef0123456789" * 4
WORKSPACE = "/work"


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _load(name: str) -> list[dict[str, Any]]:
    with open(FIXTURES / name, encoding="utf-8") as handle:
        document = json.load(handle)
    cases: list[dict[str, Any]] = document["cases"]
    return cases


ORIGINAL = _load("admission_original_inputs_v1.json")
NATIVE = _load("admission_native_inputs_v1.json")
DEPTH = _load("admission_group_depth_preemption_v1.json")
INTERN = _load("admission_interning_provenance_v1.json")

assert len(ORIGINAL) == 22
assert len(NATIVE) == 66
assert len(DEPTH) == 8
assert len(INTERN) == 8


def test_admission_fixture_self_identification() -> None:
    """The four admission MATRIX containers carry a SEPARATE provenance
    from the old single-observation fixture schema (``cache_bundles``
    ``_fixture`` files): they are verbatim known-synthetic case
    matrices of the S review-target vector files.  Pin their actual
    version, status, synthetic authority, case counts and the known
    SHA256 originals."""
    expected = {
        "admission_original_inputs_v1.json": (
            "018c-independent-original-inputs/v1",
            22,
            "8dd49c3110101a624a030575942ba1e8f96b42f13b43d2e1d23eb2c7fe62bb97",
        ),
        "admission_native_inputs_v1.json": (
            "018c-independent-native-inputs/v1",
            66,
            "c820bba99001d4a07e5e91f6b8c69e5df7aab665e3dac22fa5d33ff4fe6a60dd",
        ),
        "admission_group_depth_preemption_v1.json": (
            "018c-group-depth-preemption/v1",
            8,
            "dece27c005bdcbeb6077d74a4c28a4a0ecee673a1247e259ba6c4f054f7fbfe3",
        ),
        "admission_interning_provenance_v1.json": (
            "018c-interning-provenance-inputs/v1",
            8,
            "4b78275ab41c5128023ffd9ede43f7c6f1fc4e69331f29cee4401e93423b37f5",
        ),
    }
    for name, (version, count, digest) in expected.items():
        raw = (FIXTURES / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest, name
        document = json.loads(raw)
        assert document["version"] == version, name
        assert document["status"] == "PREPARED_NOT_EXECUTED", name
        authority = document.get("authority") or document.get("scope") or ""
        assert "synthetic" in authority.lower(), name
        assert len(document["cases"]) == count, name
        assert all(
            isinstance(case, dict) and case["name"] and case["endpoint"]
            for case in document["cases"]
        ), name


MAIN = [(case, None) for case in ORIGINAL + NATIVE]
DEPTH_CASES = [(case, case["graph_max_depth"]) for case in DEPTH]
INTERN_CASES = [(case, None) for case in INTERN]


def _namespace(mode: AdmissionMode, depth: int) -> Any:
    return make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-vector-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
        graph_bounds=GraphBounds(max_depth=depth),
    )


def _requests(case: dict[str, Any]) -> tuple[GraphRequest, ...]:
    return tuple(
        GraphRequest(payload=entry["payload"], endpoint=entry["endpoint"])
        for entry in case["requests"]
    )


def _run(case: dict[str, Any], mode: AdmissionMode, depth: int) -> Any:
    before = json.dumps(case["requests"], sort_keys=True)
    snapshot = observe_bundle_admission_batch(_requests(case), _namespace(mode, depth))
    # the public API must leave the ORIGINAL payload bytes unchanged
    assert json.dumps(case["requests"], sort_keys=True) == before
    return snapshot


def _effective_depth(case: dict[str, Any], depth: int | None) -> int:
    return depth or case.get("graph_max_depth") or case.get("max_depth") or 64


def _proof_namespace(depth: int) -> Any:
    return make_bundle_proof_namespace(
        IDENTITY,
        model_identity="synthetic-vector-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        graph_bounds=GraphBounds(max_depth=depth),
    )


def _accepted_bundles(case: dict[str, Any], depth: int) -> Any:
    """The ACCEPTED 018-b proof derivation over the SAME original
    payload (the canonical read-call oracle): one native exec+poll
    lifecycle is ONE read proof with two pieces, so the expected proof
    count comes from the accepted derivation itself, never from
    counting raw result frames."""
    return observe_bundle_proofs(_requests(case), _proof_namespace(depth))


_DEPTH_NAMES = {c["name"] for c in DEPTH}


def _legacy_source_oracle(case: dict[str, Any]) -> dict[str, str] | None:
    """Per original read CALL ID, the exact canonical LEGACY wrapper
    source body (the known-synthetic legacy fixture bytes): the legacy
    case with the same name/endpoint (plus layout, for the interning
    vectors) is the byte oracle every carrier variant must reproduce,
    independently of native/chunked parsing.  The original and native
    matrices twin against the ORIGINAL file; the depth and interning
    vectors twin against their own ``variant == "legacy"`` cases."""
    name, endpoint, layout = case["name"], case["endpoint"], case.get("layout")
    if layout is not None:
        pool = (
            t
            for t in INTERN
            if t["name"] == name and t["endpoint"] == endpoint and t.get("layout") == layout
        )
    elif name in _DEPTH_NAMES:
        pool = (t for t in DEPTH if t["name"] == name and t["endpoint"] == endpoint)
    else:
        pool = (t for t in ORIGINAL if t["name"] == name and t["endpoint"] == endpoint)
    twin = next((t for t in pool if t.get("variant") in (None, "legacy")), None)
    if twin is None:
        return None
    expected: dict[str, str] = {}
    for req in twin["requests"]:
        payload = req["payload"]
        for item in payload.get("input", []):
            if item.get("type") == "function_call_output":
                expected[item["call_id"]] = item["output"].split("Output:\n", 1)[1]
        for item in payload.get("messages", []):
            if item.get("role") == "tool":
                expected[item["tool_call_id"]] = item["content"].split("Output:\n", 1)[1]
    return expected


def _assert_proofs(case: dict[str, Any], snapshot: Any, depth: int) -> None:
    """Positive precondition: the retained source proofs are exactly
    the accepted 018-b proofs for the same original payload (same
    call association, carrier spans, members, and verbatim source
    bytes) - the exact accepted proof/source provenance."""
    baseline = _accepted_bundles(case, depth)
    assert baseline.outcome is BundleProofOutcome.COMPLETE
    actual = list(snapshot.source_proofs)
    expected = list(baseline.bundles)
    assert len(actual) == len(expected)
    for proof in actual:
        assert proof in expected, case["name"]
    for proof in expected:
        assert proof in actual, case["name"]


def _assert_common(case: dict[str, Any], snapshot: Any, depth: int) -> None:
    assert snapshot.outcome is AdmissionOutcome.COMPLETE
    expected = set(case["expected_reachable_file_paths"]) | {"AGENTS.md"}
    assert {n.path for n in snapshot.eligibility_nodes} == expected
    assert snapshot.root_entry is not None
    _assert_proofs(case, snapshot, depth)


def _nodes(snapshot: Any) -> dict[str, Any]:
    return {n.path: n for n in snapshot.eligibility_nodes}


def _offgraph(snapshot: Any) -> dict[str, Any]:
    return {n.path: n for n in snapshot.offgraph_nodes}


def _occurrences(snapshot: Any) -> set[tuple[str, ...]]:
    return {e.key_record.member_occurrences for e in snapshot.entries}


def _unresolved_targets(snapshot: Any) -> dict[tuple[str, ...], tuple[str, ...]]:
    return {
        r.possible_origins: (tuple(c.target_chars for c in r.candidates),)[0]
        for r in snapshot.unresolved_origins
    }


def _assert_both(case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int) -> None:
    """reachable-boundaryless: all members root-reachable, boundaryless."""
    _assert_common(case, snapshot, depth)
    assert len(snapshot.entries) == 1
    entry = snapshot.entries[0]
    assert entry.key_record.member_occurrences == ("A.md", "B.md")
    assert entry.member_classes == (MemberClass.ELIGIBLE, MemberClass.ELIGIBLE)
    assert entry.key_record.aggregate_source_digest == sha256_hex("alpha beta")
    assert entry.width == 2
    group = entry.key_record.ownership_groups[0]
    assert group.boundary_class is BoundaryClass.BOUNDARYLESS
    assert group.member_occurrence_indices == (0, 1)
    assert group.group_digest == sha256_hex("alpha beta")
    # the width of one distinct path never earns per-file digests
    assert entry.proof.segments[0].member_digest is None
    assert entry.proof.source_text == "alpha beta"
    nodes = _nodes(snapshot)
    assert nodes["A.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING
    assert nodes["B.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING


def _assert_greedy_only_no_c(
    case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int
) -> None:
    """mixed-same-base: mixed boundaryless group; C.md unresolved."""
    _assert_common(case, snapshot, depth)
    nodes = _nodes(snapshot)
    assert "C.md" not in nodes  # the mixed group cannot attribute C.md
    origins = _unresolved_targets(snapshot)
    assert origins[("A.md", "B.md")] == ("C.md",)
    if mode is AdmissionMode.LEAN:
        assert snapshot.entries == ()
        return
    assert len(snapshot.entries) == 1
    entry = snapshot.entries[0]
    assert entry.key_record.member_occurrences == ("A.md", "B.md")
    assert entry.member_classes == (MemberClass.ELIGIBLE, MemberClass.GREEDY_BACKGROUND)
    assert snapshot.offgraph_nodes == ()


def _assert_both_group_c_all(
    case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int
) -> None:
    """all-suppliers-common-base: certificate depth 2; C acquired."""
    _assert_common(case, snapshot, depth)
    assert _occurrences(snapshot) == {("A.md", "B.md"), ("C.md",)}
    certs = {c.target_path: c for c in snapshot.certificates}
    assert set(certs) == {"C.md"}
    assert certs["C.md"].supplier_occurrences == ("A.md", "B.md")
    assert certs["C.md"].derivation_depth == 2
    assert certs["C.md"].source_digest == sha256_hex("C.md")
    nodes = _nodes(snapshot)
    assert nodes["C.md"].status is NodeStatus.ACQUIRED
    assert nodes["C.md"].source_digest == sha256_hex("leaf")
    assert nodes["A.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING
    assert nodes["B.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING


def _assert_both_group_c_unlocked(
    case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int
) -> None:
    """group-unlocked: B.md becomes eligible via X.md, certificate depth 3."""
    _assert_common(case, snapshot, depth)
    assert _occurrences(snapshot) == {("A.md", "B.md"), ("C.md",), ("X.md",)}
    certs = {c.target_path: c for c in snapshot.certificates}
    assert set(certs) == {"C.md"}
    assert certs["C.md"].supplier_occurrences == ("A.md", "B.md")
    assert certs["C.md"].derivation_depth == 3
    nodes = _nodes(snapshot)
    assert nodes["X.md"].status is NodeStatus.ACQUIRED
    assert nodes["B.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING
    assert nodes["C.md"].status is NodeStatus.ACQUIRED


def _assert_no_file_entries_no_c(
    case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int
) -> None:
    """unrelated-singleton: offgraph B.md known; C.md never followed."""
    _assert_common(case, snapshot, depth)
    assert snapshot.entries == ()
    offgraph = _offgraph(snapshot)
    assert set(offgraph) == {"B.md"}
    assert offgraph["B.md"].status is NodeStatus.ACQUIRED
    assert offgraph["B.md"].source_digest == sha256_hex("C.md")
    assert "C.md" not in _nodes(snapshot)


def _assert_both_unresolved_c(
    case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int
) -> None:
    """different-directories: equal directories never identify a supplier."""
    _assert_common(case, snapshot, depth)
    assert snapshot.certificates == ()
    assert len(snapshot.entries) == 1
    entry = snapshot.entries[0]
    assert entry.key_record.member_occurrences == ("d1/A.md", "d2/B.md")
    assert entry.member_classes == (MemberClass.ELIGIBLE, MemberClass.ELIGIBLE)
    origins = _unresolved_targets(snapshot)
    assert origins[("d1/A.md", "d2/B.md")] == ("C.md",)
    assert "C.md" not in _nodes(snapshot)


def _assert_greedy_only_no_b_no_c(
    case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int
) -> None:
    """no-group-self-bootstrap: a mixed group cannot bootstrap its own
    missing eligibility from an unattributed reference in that group."""
    _assert_common(case, snapshot, depth)
    nodes = _nodes(snapshot)
    assert "B.md" not in nodes
    assert "C.md" not in nodes
    origins = _unresolved_targets(snapshot)
    assert set(origins[("A.md", "B.md")]) == {"B.md", "C.md"}
    if mode is AdmissionMode.LEAN:
        assert snapshot.entries == ()
        return
    assert len(snapshot.entries) == 1
    entry = snapshot.entries[0]
    assert entry.key_record.member_occurrences == ("A.md", "B.md")
    assert entry.member_classes == (MemberClass.ELIGIBLE, MemberClass.GREEDY_BACKGROUND)


def _assert_both_depth2(
    case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int
) -> None:
    """alternate-shorter-group-depth: the LEAST complete derivation of D
    is 2 (via E.md), so max_depth 2 COMPLETEs although the C.md route is
    3 (a longer alternate walk neither pre-empts nor is pre-empted)."""
    _assert_common(case, snapshot, depth)
    assert _occurrences(snapshot) == {
        ("A.md", "B.md"),
        ("C.md",),
        ("E.md",),
        ("D.md",),
    }
    certs = {c.target_path: c for c in snapshot.certificates}
    assert certs["C.md"].derivation_depth == 2
    nodes = _nodes(snapshot)
    assert nodes["C.md"].status is NodeStatus.ACQUIRED
    assert nodes["D.md"].status is NodeStatus.ACQUIRED


def _assert_both_root_depth0(
    case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int
) -> None:
    """root-back-cycle: the group reference targets the root; the root
    self/back-cycle target depth stays 0 under max_depth 1."""
    _assert_common(case, snapshot, depth)
    assert len(snapshot.entries) == 1
    entry = snapshot.entries[0]
    assert entry.key_record.member_occurrences == ("A.md", "B.md")
    assert {"AGENTS.md", "A.md", "B.md"} <= set(_nodes(snapshot))
    # a tool group never establishes the root: the root entry binds the
    # legitimate envelope, not the group content
    assert snapshot.root_entry.key_record.aggregate_source_digest != sha256_hex("AGENTS.md")


def _assert_both_unknown_member_digest(
    case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int
) -> None:
    """repeated-occurrence-width1: A.md A.md stays width 1 with an
    unknown individual hash (the repeated group never earns one)."""
    _assert_common(case, snapshot, depth)
    assert len(snapshot.entries) == 1
    entry = snapshot.entries[0]
    assert entry.key_record.member_occurrences == ("A.md", "A.md")
    assert entry.width == 1
    group = entry.key_record.ownership_groups[0]
    assert group.boundary_class is BoundaryClass.BOUNDARYLESS
    assert group.member_occurrence_indices == (0, 1)
    assert group.group_digest == sha256_hex("aa")
    assert entry.proof.segments[0].member_digest is None
    assert _nodes(snapshot)["A.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING


def _assert_both_key_equivalent_standalone(
    case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int
) -> None:
    """guarded-singleton: the guarded one-iteration loop singleton has
    the SAME structural key as the plain ``cat A.md`` singleton (parser
    method is provenance, not key material)."""
    _assert_common(case, snapshot, depth)
    assert len(snapshot.entries) == 1
    entry = snapshot.entries[0]
    assert entry.key_record.member_occurrences == ("A.md",)
    assert entry.key_record.ownership_groups[0].boundary_class is BoundaryClass.PROVEN
    assert entry.key_record.aggregate_source_digest == sha256_hex("alpha")
    standalone = {
        "requests": [
            {
                "endpoint": "responses",
                "payload": {
                    "model": "synthetic-vector-model",
                    "input": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": (
                                        "# AGENTS.md instructions for /work\n\n"
                                        "<INSTRUCTIONS>\nA.md\n</INSTRUCTIONS>\n"
                                    ),
                                }
                            ],
                        },
                        {
                            "type": "function_call",
                            "call_id": "synthetic-standalone",
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": "cat A.md"}),
                        },
                        {
                            "type": "function_call_output",
                            "call_id": "synthetic-standalone",
                            "output": (
                                "Chunk ID: l1\nWall time: 0.0000 seconds\n"
                                "Process exited with code 0\nOutput:\nalpha"
                            ),
                        },
                    ],
                },
            }
        ]
    }
    other = _run(standalone, mode, _effective_depth(case, None))
    assert len(other.entries) == 1
    assert other.entries[0].content_key == entry.content_key


def _assert_depth_preemption(
    case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int
) -> None:
    """group-shortcut-repairs-old-depth-refusal: at max_depth 2 the
    LEAST complete derivation of T.md is the group certificate's 2
    (the ordinary X->Y->T walk is 3 and does not pre-empt it); the old
    ordinary graph would refuse T at 3."""
    assert snapshot.outcome is AdmissionOutcome.COMPLETE
    assert snapshot.root_entry is not None
    _assert_proofs(case, snapshot, depth)
    assert _occurrences(snapshot) == {
        ("A.md", "B.md"),
        ("X.md",),
        ("Y.md",),
        ("T.md",),
    }
    certs = {c.target_path: c for c in snapshot.certificates}
    assert set(certs) == {"T.md"}
    assert certs["T.md"].supplier_occurrences == ("A.md", "B.md")
    assert certs["T.md"].derivation_depth == 2
    assert _nodes(snapshot)["T.md"].status is NodeStatus.ACQUIRED


def _assert_interning(case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int) -> None:
    """AB-A-Aagain-original-carriers: AB then A then identical A yields
    TWO FILE entries plus the separate required root; A's actual
    entry/key identity is interned (reused), and ALL THREE original
    proofs/carriers are retained separately (this is structural
    interning, not compiler/cache-hit evidence)."""
    assert snapshot.outcome is AdmissionOutcome.COMPLETE
    assert len(snapshot.entries) == 2
    assert _occurrences(snapshot) == {("A.md", "B.md"), ("A.md",)}
    a_entries = [e for e in snapshot.entries if e.key_record.member_occurrences == ("A.md",)]
    assert len(a_entries) == 1
    a_entry = a_entries[0]
    assert a_entry.key_record.ownership_groups[0].boundary_class is BoundaryClass.PROVEN
    assert a_entry.key_record.aggregate_source_digest == sha256_hex("alpha")
    assert len(snapshot.source_proofs) == 3
    _assert_proofs(case, snapshot, depth)
    call_ids = sorted(p.call_id for p in snapshot.source_proofs)
    assert call_ids == [
        "synthetic-intern-0",
        "synthetic-intern-1",
        "synthetic-intern-2",
    ]
    assert snapshot.entries_retained == 3  # root + two file entries
    # the reverse index maps every represented path to ALL admitted keys
    associations = {p.path: p.content_keys for p in snapshot.path_associations}
    a_key = a_entry.content_key
    ab_key = next(
        e.content_key
        for e in snapshot.entries
        if e.key_record.member_occurrences == ("A.md", "B.md")
    )
    assert associations["A.md"] == tuple(sorted((a_key, ab_key)))
    assert associations["B.md"] == (ab_key,)
    root_key = snapshot.root_entry.content_key
    assert associations["AGENTS.md"] == (root_key,)
    assert snapshot.root_entry not in snapshot.entries


# --- carrier surface expectations ---------------------------------------

_SURFACE_BY_VARIANT = {
    # native file: every variant is process-only (the token line is
    # legacy-malformed; multi-chunk is process-only)
    "native-final-tokens": "process",
    "native-chunks-final-no-tokens": "process",
    "native-chunks-final-tokens": "process",
    # depth file: the no-token native final is positive on BOTH
    # surfaces -> the seam law retains ONE read-primary record
    "native-no-tokens": "read",
    "native-tokens": "process",
    # interning file
    "legacy": "read",
    "chunks": "process",
}


def _assert_surfaces(case: dict[str, Any], snapshot: Any) -> None:
    variant = case.get("variant")
    if variant is None:
        return  # legacy carriers (the original-input matrix)
    expected = _SURFACE_BY_VARIANT[variant]
    for proof in snapshot.source_proofs:
        assert proof.surface.value == expected, (case["name"], variant)
    if variant in ("native-chunks-final-no-tokens", "native-chunks-final-tokens", "chunks"):
        for proof in snapshot.source_proofs:
            assert len(proof.pieces) == 2
            # one original exec piece plus its causally associated poll
            # piece (never invented from IDs or detached coordinates)
            assert len({p.call_id for p in proof.pieces}) == 2
            assert sum(1 for p in proof.pieces if "-poll-" in p.call_id) == 1


def _assert_legacy_bytes(case: dict[str, Any], snapshot: Any) -> None:
    """EXACT canonical source bytes per original read call ID: every
    retained proof's source_text/source_digest equals the known
    LEGACY fixture body for that call (independent of native carrier
    parsing); the expected nonzero read count is required."""
    expected = _legacy_source_oracle(case)
    assert expected is not None, f"no legacy twin for declared vector case {case['name']}"
    assert len(expected) > 0
    proofs = list(snapshot.source_proofs)
    assert len(proofs) == len(expected), case["name"]
    for proof in proofs:
        assert proof.source_text == expected[proof.call_id], case["name"]
        assert proof.source_digest == sha256_hex(expected[proof.call_id]), case["name"]


_EXPECTATIONS = {
    "both": _assert_both,
    "greedy-only-no-C": _assert_greedy_only_no_c,
    "no-file-entries-no-C": _assert_no_file_entries_no_c,
    "both-unresolved-C": _assert_both_unresolved_c,
    "greedy-only-no-B-no-C": _assert_greedy_only_no_b_no_c,
    "both-depth2": _assert_both_depth2,
    "both-root-depth0": _assert_both_root_depth0,
    "both-unknown-member-digest": _assert_both_unknown_member_digest,
    "both-key-equivalent-standalone": _assert_both_key_equivalent_standalone,
}
_GROUP_C_BY_NAME = {
    "all-suppliers-common-base": _assert_both_group_c_all,
    "group-unlocked-by-later-independent-source": _assert_both_group_c_unlocked,
}


def _dispatch(case: dict[str, Any], snapshot: Any, mode: AdmissionMode, depth: int) -> None:
    if case["name"] == "group-shortcut-repairs-old-depth-refusal":
        _assert_depth_preemption(case, snapshot, mode, depth)
        return
    if case["name"] == "AB-A-Aagain-original-carriers":
        _assert_interning(case, snapshot, mode, depth)
        return
    expectation = case["expectation"]
    if expectation == "both-group-C":
        _GROUP_C_BY_NAME[case["name"]](case, snapshot, mode, depth)
        return
    _EXPECTATIONS[expectation](case, snapshot, mode, depth)


_ALL = MAIN + DEPTH_CASES + INTERN_CASES


def _ids() -> list[str]:
    ids = []
    for case, depth in _ALL:
        variant = case.get("variant", "legacy")
        ids.append(
            f"{case['name']}__{case['endpoint']}__{variant}" + (f"__d{depth}" if depth else "")
        )
    return ids


@pytest.mark.parametrize("case,depth", _ALL, ids=_ids())
@pytest.mark.parametrize("mode", [AdmissionMode.LEAN, AdmissionMode.GREEDY])
def test_original_input_matrix(
    mode: AdmissionMode, case: dict[str, Any], depth: int | None
) -> None:
    snapshot = _run(case, mode, _effective_depth(case, depth))
    _dispatch(case, snapshot, mode, _effective_depth(case, depth))
    _assert_surfaces(case, snapshot)
    _assert_legacy_bytes(case, snapshot)
