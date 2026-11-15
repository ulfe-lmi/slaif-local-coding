"""018-f constructor-level invariants for the current-graph records.

Constructor-level SHAPE laws (construction is not authentication):
every exported current-graph record is validated against the closed
enums, sorted/deduplicated containers, the bounded version-owned
owner identities, the edge/diagnostic ceiling arithmetic, the
recomputed version-owned scope key, and the fixed
enums/counts/private-repr privacy law.  The derivation itself
(``derive_current_graph``) and its original-API matrix live in
``test_current_graph.py``; the state object used for the result
laws comes from an ACTUAL 018-d root bootstrap (no fabricated
positive proof).
"""

from __future__ import annotations

import hashlib
from typing import Any, cast

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
)
from slaif_local_coding.constitution.bundles.causal_history import (
    observe_causal_history,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CausalHistoryOutcome,
    CausalHistoryState,
)
from slaif_local_coding.constitution.bundles.current_graph_models import (
    CURRENT_GRAPH_CONTRACT_VERSION,
    CURRENT_GRAPH_POLICY_VERSION,
    PRIVATE_PATH_PLACEHOLDER,
    ROOT_OWNER,
    CurrentGraph,
    CurrentGraphBounds,
    CurrentGraphCandidate,
    CurrentGraphCertificate,
    CurrentGraphEdge,
    CurrentGraphEdgeKind,
    CurrentGraphLimitation,
    CurrentGraphNode,
    CurrentGraphOrigin,
    CurrentGraphOutcome,
    CurrentGraphReason,
    CurrentGraphResult,
    CurrentGraphStatus,
    CurrentGraphSupplier,
    CurrentGraphSupplierKind,
    _owner_group,
    _owner_source,
    current_graph_scope_key,
)
from slaif_local_coding.constitution.bundles.currentness_models import (
    CURRENTNESS_CONTRACT_VERSION,
    CURRENTNESS_POLICY_VERSION,
    OPAQUE_GROUP_RECIPE_VERSION,
    CurrentnessBounds,
)
from slaif_local_coding.constitution.bundles.graph_models import (
    GRAPH_CONTRACT_VERSION,
    ROOT_FILENAME,
    CandidateStatus,
    CandidateSyntax,
    GraphBounds,
    GraphLimitation,
    ReferenceCandidate,
)
from slaif_local_coding.constitution.bundles.observation_models import (
    EMPTY_SOURCE_SHA256,
    CharSpan,
)
from tests.test_causal_history import empty_state, make_ns, root_request

CANARY = "ZCANARYZ"  # sentinel path/target token for the privacy laws

ROOT_BODY = "Read `A.md` first."
ROOT_DIGEST = hashlib.sha256(ROOT_BODY.encode("utf-8")).hexdigest()
A_DIGEST = hashlib.sha256(b"From A see `C.md`.\n").hexdigest()
W1 = hashlib.sha256(b"witness-1").hexdigest()
W2 = hashlib.sha256(b"witness-2").hexdigest()
# The hash ordering of W1/W2 is not under test control: the sorted
# pair is explicit wherever two witnesses appear.
WITNESSES = tuple(sorted((W1, W2)))
UNSORTED_WITNESSES = (WITNESSES[1], WITNESSES[0])


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _hex64(value: int) -> str:
    return hashlib.sha256(str(value).encode()).hexdigest()


ORIGIN = CurrentGraphOrigin(
    occurrence_id=W1,
    group_index=0,
    request_index=1,
    call_position=0,
    result_position=0,
)


def _candidate(
    *,
    referring_path: str | None = None,
    target_chars: str = "C.md",
    target_char_span: CharSpan | None = None,
    target_byte_span: CharSpan | None = None,
    status: CandidateStatus = CandidateStatus.ACCEPTED,
    reasons: tuple[GraphLimitation, ...] = (),
    occurrence_index: int = 0,
) -> ReferenceCandidate:
    """One valid accepted-shape reference candidate (the ACTUAL 018-c
    record; 018-f records embed it but never interpolate it raw)."""
    span = target_char_span or CharSpan(start=4, end=8)
    return ReferenceCandidate(
        referring_path=referring_path,
        scoped_key=_hex64(3),
        syntax=CandidateSyntax.BACKTICK_CODE,
        target_chars=target_chars,
        target_char_span=span,
        target_byte_span=target_byte_span or span,
        status=status,
        reasons=reasons,
        occurrence_index=occurrence_index,
    )


def _root_node() -> CurrentGraphNode:
    return CurrentGraphNode(
        path=ROOT_FILENAME,
        status=CurrentGraphStatus.CURRENT_KNOWN,
        digest=ROOT_DIGEST,
        owner=ROOT_OWNER,
        depth=0,
    )


def _root_supplier() -> CurrentGraphSupplier:
    return CurrentGraphSupplier(
        kind=CurrentGraphSupplierKind.ROOT,
        path=ROOT_FILENAME,
        digest=ROOT_DIGEST,
    )


def _valid_graph(**overrides: object) -> CurrentGraph:
    """ONE coherent minimal graph; the scope key is RECOMPUTED from
    the final actual fields, so a version override stays coherent."""
    data: dict[str, Any] = {
        "history_key": _hex64(1),
        "revision": 1,
        "workspace": "/work",
        "root_digest": ROOT_DIGEST,
        "contract_version": CURRENT_GRAPH_CONTRACT_VERSION,
        "policy_version": CURRENT_GRAPH_POLICY_VERSION,
        "graph_version": GRAPH_CONTRACT_VERSION,
        "reference_version": "cache-reference/v1",
        "proof_version": "cache-proof/v1",
        "currentness_contract_version": CURRENTNESS_CONTRACT_VERSION,
        "currentness_policy_version": CURRENTNESS_POLICY_VERSION,
        "currentness_recipe_version": OPAQUE_GROUP_RECIPE_VERSION,
        "currentness_scope_key": _hex64(2),
        "bounds": CurrentGraphBounds(),
        "currentness_bounds": CurrentnessBounds(),
        "graph_bounds": GraphBounds(),
        "suppliers": (_root_supplier(),),
        "nodes": (_root_node(),),
        "emitted_reasons": 0,
    }
    data.update(overrides)
    scope_key = current_graph_scope_key(
        cast(str, data["history_key"]),
        cast(str, data["workspace"]),
        cast(str, data["root_digest"]),
        cast(str, data["contract_version"]),
        cast(str, data["policy_version"]),
        cast(str, data["graph_version"]),
        cast(str, data["reference_version"]),
        cast(str, data["proof_version"]),
        cast(str, data["currentness_contract_version"]),
        cast(str, data["currentness_policy_version"]),
        cast(str, data["currentness_recipe_version"]),
        cast(str, data["currentness_scope_key"]),
        cast(CurrentGraphBounds, data["bounds"]),
        cast(CurrentnessBounds, data["currentness_bounds"]),
        cast(GraphBounds, data["graph_bounds"]),
    )
    data["scope_key"] = scope_key
    return CurrentGraph(**data)


@pytest.fixture(scope="module")
def bootstrapped_state() -> CausalHistoryState:
    """An ACTUAL 018-d root bootstrap state (real Responses root
    request; no fabricated occurrence or acquisition)."""
    ns = make_ns(AdmissionMode.LEAN)
    state = empty_state(ns)
    transition = observe_causal_history((root_request(),), ns, state, 0)
    assert transition.outcome is CausalHistoryOutcome.ACCEPTED
    assert transition.state is not None
    return transition.state


# ---------------------------------------------------------------------------
# Bounds and scope-key laws
# ---------------------------------------------------------------------------


def test_current_graph_bounds_law() -> None:
    bounds = CurrentGraphBounds()
    assert (bounds.max_total_work_units, bounds.max_diagnostics) == (1048576, 64)
    stricter = CurrentGraphBounds(max_total_work_units=5, max_diagnostics=7)
    assert (stricter.max_total_work_units, stricter.max_diagnostics) == (5, 7)
    with pytest.raises(ValidationError):
        CurrentGraphBounds(max_total_work_units=0)
    with pytest.raises(ValidationError):
        CurrentGraphBounds(max_total_work_units=1048577)
    with pytest.raises(ValidationError):
        CurrentGraphBounds(max_diagnostics=0)
    with pytest.raises(ValidationError):
        CurrentGraphBounds(max_diagnostics=65)
    with pytest.raises(ValidationError):
        CurrentGraphBounds(unknown_bound=1)  # type: ignore[call-arg]
    with pytest.raises(ValueError):  # frozen
        bounds.max_total_work_units = 1


def test_scope_key_binds_actual_version_fields() -> None:
    base = _valid_graph()
    # A coherent graph with an unsupported actual version is
    # constructible at the model layer (construction is not
    # authentication) and its scope key DIFFERS from the supported
    # one: the key binds the actual version fields.
    v9 = _valid_graph(contract_version="cache-current-graph/v9")
    assert v9.contract_version == "cache-current-graph/v9"
    assert v9.scope_key != base.scope_key
    policy9 = _valid_graph(policy_version="current-graph-policy/v9")
    assert policy9.scope_key != base.scope_key
    assert policy9.scope_key != v9.scope_key
    # A stale/forged scope key over the same actual fields refuses.
    dumped = base.model_dump()
    with pytest.raises(ValidationError, match="scope key"):
        CurrentGraph(**{**dumped, "scope_key": _hex64(99)})
    with pytest.raises(ValidationError):
        CurrentGraph(**{**dumped, "history_key": _hex64(98)})
    with pytest.raises(ValidationError):
        CurrentGraph(**{**dumped, "currentness_scope_key": _hex64(97)})


# ---------------------------------------------------------------------------
# Owner identity laws
# ---------------------------------------------------------------------------


def test_owner_identities_are_bounded_and_sensitive() -> None:
    owner = _owner_source("A.md", A_DIGEST)
    assert owner == _owner_source("A.md", A_DIGEST)
    assert owner != _owner_source("B.md", A_DIGEST)
    assert owner != _owner_source("A.md", _sha("other content"))
    # A legal long member path (>~436 chars, well beyond any old
    # arbitrary text cap) still yields the bounded 64-hex identity.
    long_path = "a" * 540 + "/A.md"
    long_owner = _owner_source(long_path, A_DIGEST)
    assert len(long_owner) == 64 and long_owner != owner
    group_owner = _owner_group(_hex64(5), A_DIGEST)
    assert group_owner == _owner_group(_hex64(5), A_DIGEST)
    assert group_owner != _owner_group(_hex64(6), A_DIGEST)
    assert group_owner != owner  # domain separation
    assert group_owner != _owner_source(_hex64(5), A_DIGEST)


def test_node_owner_binding_laws() -> None:
    good = CurrentGraphNode(
        path="A.md",
        status=CurrentGraphStatus.CURRENT_KNOWN,
        digest=A_DIGEST,
        owner=_owner_source("A.md", A_DIGEST),
        witnesses=(W1,),
        depth=1,
    )
    assert good.owner is not None
    for owner in ("not-a-hex-owner", _hex64(77), ROOT_OWNER):
        with pytest.raises(ValidationError):
            CurrentGraphNode(
                path="A.md",
                status=CurrentGraphStatus.CURRENT_KNOWN,
                digest=A_DIGEST,
                owner=owner,
                witnesses=(W1,),
                depth=1,
            )


def test_node_status_laws() -> None:
    root = _root_node()
    assert root.status is CurrentGraphStatus.CURRENT_KNOWN and root.depth == 0
    with pytest.raises(ValidationError):
        CurrentGraphNode(
            path=ROOT_FILENAME,
            status=CurrentGraphStatus.DISCOVERED_UNACQUIRED,
            digest=ROOT_DIGEST,
            owner=ROOT_OWNER,
            depth=0,
        )
    with pytest.raises(ValidationError):
        CurrentGraphNode(
            path=ROOT_FILENAME,
            status=CurrentGraphStatus.CURRENT_KNOWN,
            digest=ROOT_DIGEST,
            owner=ROOT_OWNER,
            depth=1,
        )
    with pytest.raises(ValidationError):
        CurrentGraphNode(
            path=ROOT_FILENAME,
            status=CurrentGraphStatus.CURRENT_KNOWN,
            digest=ROOT_DIGEST,
            owner=_hex64(8),
            depth=0,
        )
    with pytest.raises(ValidationError):  # empty digest is not current-known
        CurrentGraphNode(
            path="E.md",
            status=CurrentGraphStatus.CURRENT_KNOWN,
            digest=EMPTY_SOURCE_SHA256,
            owner=_owner_source("E.md", EMPTY_SOURCE_SHA256),
            witnesses=(W1,),
            depth=1,
        )
    empty = CurrentGraphNode(
        path="E.md",
        status=CurrentGraphStatus.CURRENT_EMPTY,
        digest=EMPTY_SOURCE_SHA256,
        owner=_owner_source("E.md", EMPTY_SOURCE_SHA256),
        witnesses=(W1,),
        depth=2,
    )
    assert empty.digest == EMPTY_SOURCE_SHA256
    with pytest.raises(ValidationError):
        CurrentGraphNode(
            path="E.md",
            status=CurrentGraphStatus.CURRENT_EMPTY,
            digest=A_DIGEST,
            owner=_owner_source("E.md", A_DIGEST),
            witnesses=(W1,),
            depth=2,
        )
    unavailable = CurrentGraphNode(
        path="U.md", status=CurrentGraphStatus.BLOCKED_AMBIGUITY, depth=1
    )
    assert unavailable.digest is None and unavailable.owner is None
    assert unavailable.witnesses == ()
    with pytest.raises(ValidationError):
        CurrentGraphNode(
            path="U.md",
            status=CurrentGraphStatus.BLOCKED_AMBIGUITY,
            digest=A_DIGEST,
            owner=_owner_source("U.md", A_DIGEST),
            witnesses=(W1,),
            depth=1,
        )
    for witnesses in (UNSORTED_WITNESSES, (W1, W1), ("nothex",)):
        with pytest.raises(ValidationError):
            CurrentGraphNode(
                path="A.md",
                status=CurrentGraphStatus.CURRENT_KNOWN,
                digest=A_DIGEST,
                owner=_owner_source("A.md", A_DIGEST),
                witnesses=witnesses,
                depth=1,
            )


# ---------------------------------------------------------------------------
# Supplier / origin laws
# ---------------------------------------------------------------------------


def test_supplier_kind_laws() -> None:
    root = _root_supplier()
    assert root.kind is CurrentGraphSupplierKind.ROOT
    with pytest.raises(ValidationError):
        CurrentGraphSupplier(kind=CurrentGraphSupplierKind.ROOT, path="A.md", digest=A_DIGEST)
    with pytest.raises(ValidationError):
        CurrentGraphSupplier(
            kind=CurrentGraphSupplierKind.ROOT,
            path=ROOT_FILENAME,
            digest=ROOT_DIGEST,
            witnesses=(W1,),
        )
    with pytest.raises(ValidationError):
        CurrentGraphSupplier(kind=CurrentGraphSupplierKind.ROOT, path=ROOT_FILENAME)
    source = CurrentGraphSupplier(
        kind=CurrentGraphSupplierKind.SOURCE,
        path="A.md",
        digest=A_DIGEST,
        members=("A.md",),
        witnesses=(W1,),
        coordinates=(ORIGIN,),
    )
    assert source.members == ("A.md",)
    with pytest.raises(ValidationError):
        CurrentGraphSupplier(
            kind=CurrentGraphSupplierKind.SOURCE,
            path="A.md",
            digest=A_DIGEST,
            members=("A.md", "B.md"),
            witnesses=(W1,),
            coordinates=(ORIGIN,),
        )
    with pytest.raises(ValidationError):
        CurrentGraphSupplier(
            kind=CurrentGraphSupplierKind.SOURCE,
            path=ROOT_FILENAME,
            digest=ROOT_DIGEST,
            members=(ROOT_FILENAME,),
            witnesses=(W1,),
            coordinates=(ORIGIN,),
        )
    with pytest.raises(ValidationError):
        CurrentGraphSupplier(
            kind=CurrentGraphSupplierKind.SOURCE,
            path="A.md",
            digest=A_DIGEST,
            members=("A.md",),
            witnesses=(W1,),
        )
    with pytest.raises(ValidationError):
        CurrentGraphSupplier(
            kind=CurrentGraphSupplierKind.SOURCE,
            path="A.md",
            digest=A_DIGEST,
            identity=_hex64(5),
            members=("A.md",),
            witnesses=(W1,),
            coordinates=(ORIGIN,),
        )
    group = CurrentGraphSupplier(
        kind=CurrentGraphSupplierKind.GROUP,
        identity=_hex64(5),
        group_digest=_hex64(6),
        members=("A.md", "B.md"),
        witnesses=(W1,),
        coordinates=(ORIGIN,),
    )
    assert group.path is None and group.digest is None
    with pytest.raises(ValidationError):
        CurrentGraphSupplier(
            kind=CurrentGraphSupplierKind.GROUP,
            path="A.md",
            identity=_hex64(5),
            group_digest=_hex64(6),
            members=("A.md", "B.md"),
            witnesses=(W1,),
            coordinates=(ORIGIN,),
        )
    with pytest.raises(ValidationError):
        CurrentGraphSupplier(
            kind=CurrentGraphSupplierKind.GROUP,
            identity=_hex64(5),
            group_digest=_hex64(6),
            members=("A.md",),
            witnesses=(W1,),
            coordinates=(ORIGIN,),
        )
    with pytest.raises(ValidationError):
        CurrentGraphSupplier(
            kind=CurrentGraphSupplierKind.GROUP,
            identity=_hex64(5),
            group_digest=_hex64(6),
            members=(ROOT_FILENAME, ROOT_FILENAME),
            witnesses=(W1,),
            coordinates=(ORIGIN,),
        )
    with pytest.raises(ValidationError):
        CurrentGraphSupplier(
            kind=CurrentGraphSupplierKind.GROUP,
            identity=_hex64(5),
            members=("A.md", "B.md"),
            witnesses=(W1,),
            coordinates=(ORIGIN,),
        )


def test_origin_laws() -> None:
    assert (ORIGIN.group_index, ORIGIN.request_index) == (0, 1)
    with pytest.raises(ValidationError):
        CurrentGraphOrigin(
            occurrence_id="nothex",
            group_index=0,
            request_index=0,
            call_position=0,
            result_position=0,
        )
    with pytest.raises(ValidationError):
        CurrentGraphOrigin(
            occurrence_id=W1, group_index=-1, request_index=0, call_position=0, result_position=0
        )
    with pytest.raises(ValidationError):
        CurrentGraphOrigin(
            occurrence_id=W1, group_index=0, request_index=-1, call_position=0, result_position=0
        )


# ---------------------------------------------------------------------------
# Certificate laws
# ---------------------------------------------------------------------------


def _usable_certificate() -> CurrentGraphCertificate:
    return CurrentGraphCertificate(
        group_identity=_hex64(21),
        group_digest=_hex64(22),
        members=("B.md", "C.md"),
        candidate=_candidate(),
        possible_origins=("B.md", "C.md"),
        suppliers=("B.md",),
        resolved_target="C.md",
        depth=2,
        usable=True,
        witnesses=(W1,),
    )


def _blocked_certificate(
    *,
    resolved_target: str | None = None,
    reasons: tuple[CurrentGraphReason, ...] = (CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE,),
    occurrence_index: int = 1,
) -> CurrentGraphCertificate:
    return CurrentGraphCertificate(
        group_identity=_hex64(21),
        group_digest=_hex64(23),
        members=("B.md", "E.md"),
        candidate=_candidate(occurrence_index=occurrence_index),
        possible_origins=("B.md", "E.md"),
        suppliers=("B.md", "E.md"),
        resolved_target=resolved_target,
        usable=False,
        reasons=reasons,
        witnesses=(W2,),
    )


def test_certificate_laws() -> None:
    usable = _usable_certificate()
    assert usable.resolved_target == "C.md" and usable.depth == 2
    assert usable.reasons == ()
    blocked = _blocked_certificate(resolved_target="D.md")
    assert blocked.depth is None and blocked.usable is False
    with pytest.raises(ValidationError):
        _usable_certificate_with(reasons=(CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE,))
    with pytest.raises(ValidationError):
        _usable_certificate_with(resolved_target=None)
    with pytest.raises(ValidationError):
        _usable_certificate_with(depth=None)
    with pytest.raises(ValidationError):
        _usable_certificate_with(suppliers=())
    with pytest.raises(ValidationError):
        _blocked_certificate(resolved_target="D.md", reasons=())
    with pytest.raises(ValidationError):
        _blocked_certificate_with(depth=1)
    with pytest.raises(ValidationError):
        _certificate_with(suppliers=("X.md",))
    with pytest.raises(ValidationError):
        _certificate_with(suppliers=(ROOT_FILENAME,))
    with pytest.raises(ValidationError):
        _certificate_with(possible_origins=("C.md", "B.md"))
    with pytest.raises(ValidationError):
        _certificate_with(suppliers=("C.md", "B.md"))
    with pytest.raises(ValidationError):
        _blocked_certificate_with(
            reasons=(
                CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE,
                CurrentGraphReason.NO_COMMON_DIRECTORY,
            )
        )
    with pytest.raises(ValidationError):
        _blocked_certificate_with(
            reasons=(
                CurrentGraphReason.NO_COMMON_DIRECTORY,
                CurrentGraphReason.NO_COMMON_DIRECTORY,
            )
        )


def _usable_certificate_with(**overrides: object) -> CurrentGraphCertificate:
    data: dict[str, Any] = {
        "group_identity": _hex64(21),
        "group_digest": _hex64(22),
        "members": ("B.md", "C.md"),
        "candidate": _candidate(),
        "possible_origins": ("B.md", "C.md"),
        "suppliers": ("B.md",),
        "resolved_target": "C.md",
        "depth": 2,
        "usable": True,
        "witnesses": (W1,),
    }
    data.update(overrides)
    return CurrentGraphCertificate(**data)


def _blocked_certificate_with(**overrides: object) -> CurrentGraphCertificate:
    data: dict[str, Any] = {
        "group_identity": _hex64(21),
        "group_digest": _hex64(23),
        "members": ("B.md", "E.md"),
        "candidate": _candidate(occurrence_index=1),
        "possible_origins": ("B.md", "E.md"),
        "suppliers": ("B.md", "E.md"),
        "resolved_target": None,
        "usable": False,
        "reasons": (CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE,),
        "witnesses": (W2,),
    }
    data.update(overrides)
    return CurrentGraphCertificate(**data)


def _certificate_with(**overrides: object) -> CurrentGraphCertificate:
    data: dict[str, Any] = {
        "group_identity": _hex64(21),
        "group_digest": _hex64(22),
        "members": ("B.md", "C.md"),
        "candidate": _candidate(),
        "possible_origins": ("B.md", "C.md"),
        "suppliers": ("B.md",),
        "resolved_target": "C.md",
        "depth": 2,
        "usable": True,
        "witnesses": (W1,),
    }
    data.update(overrides)
    return CurrentGraphCertificate(**data)


# ---------------------------------------------------------------------------
# Graph container laws
# ---------------------------------------------------------------------------


def test_graph_container_laws() -> None:
    graph = _valid_graph()
    dumped = graph.model_dump()
    root_node = dumped["nodes"][0]
    a_node = {"path": "A.md", "status": "discovered_unacquired", "depth": 1}
    b_node = {"path": "B.md", "status": "discovered_unacquired", "depth": 1}
    with pytest.raises(ValidationError):
        CurrentGraph(**{**dumped, "root_path": "AGENTS2.md"})
    with pytest.raises(ValidationError):
        CurrentGraph(**{**dumped, "history_key": "nothex"})
    with pytest.raises(ValidationError):
        CurrentGraph(**{**dumped, "workspace": "w" * 1025})
    with pytest.raises(ValidationError):
        CurrentGraph(**{**dumped, "contract_version": "v" * 129})
    # Exactly one root node carrying the exact anchor digest.
    with pytest.raises(ValidationError, match="root node"):
        CurrentGraph(**{**dumped, "nodes": [a_node]})
    with pytest.raises(ValidationError, match="anchor digest"):
        CurrentGraph(**{**dumped, "root_digest": _hex64(55)})
    with pytest.raises(ValidationError, match="sorted"):
        CurrentGraph(**{**dumped, "nodes": [root_node, a_node]})
    with pytest.raises(ValidationError, match="deduplicated"):
        CurrentGraph(**{**dumped, "nodes": [root_node, root_node]})
    # Edge endpoints must be graph nodes; edges sorted/deduplicated by
    # (source, target, kind, owner).
    edge_a = {
        "source": ROOT_FILENAME,
        "target": "A.md",
        "kind": "ordinary",
        "owner": ROOT_OWNER,
        "witnesses": [],
        "depth": 1,
    }
    edge_z = {**edge_a, "target": "Z.md"}
    with pytest.raises(ValidationError, match="endpoints"):
        CurrentGraph(
            **{
                **dumped,
                "nodes": [a_node, root_node],
                "edges": [edge_z],
            }
        )
    with pytest.raises(ValidationError, match="deduplicated"):
        CurrentGraph(
            **{
                **dumped,
                "nodes": [a_node, root_node],
                "edges": [edge_a, dict(edge_a)],
            }
        )
    edge_b = {**edge_a, "target": "B.md"}
    nodes_ab = [a_node, b_node, root_node]
    with pytest.raises(ValidationError, match="sorted"):
        CurrentGraph(
            **{
                **dumped,
                "nodes": nodes_ab,
                "edges": [edge_b, edge_a],
            }
        )
    # Certificates sorted/deduplicated per group candidate.
    cert_a = {
        "group_identity": _hex64(21),
        "group_digest": _hex64(22),
        "members": ["B.md", "C.md"],
        "candidate": _candidate().model_dump(),
        "possible_origins": ["B.md", "C.md"],
        "suppliers": ["B.md"],
        "resolved_target": "C.md",
        "depth": 2,
        "usable": True,
        "witnesses": [W1],
    }
    cert_b = {**cert_a, "candidate": _candidate(occurrence_index=1).model_dump()}
    with pytest.raises(ValidationError, match="sorted"):
        CurrentGraph(
            **{
                **dumped,
                "nodes": nodes_ab,
                "certificates": [cert_b, cert_a],
            }
        )
    with pytest.raises(ValidationError, match="deduplicated"):
        CurrentGraph(
            **{
                **dumped,
                "nodes": nodes_ab,
                "certificates": [cert_a, cert_a],
            }
        )
    # Candidates sorted/deduplicated per source candidate.
    owner = _owner_source("A.md", A_DIGEST)
    candidate_entry = {
        "owner": owner,
        "candidate": _candidate(status=CandidateStatus.UNSUPPORTED).model_dump(),
    }
    candidate_later = {
        "owner": owner,
        "candidate": _candidate(occurrence_index=1).model_dump(),
    }
    with pytest.raises(ValidationError, match="sorted"):
        CurrentGraph(
            **{
                **dumped,
                "candidates": [candidate_later, candidate_entry],
            }
        )
    # Unreachable paths sorted/deduplicated; at most one root supplier.
    with pytest.raises(ValidationError, match="sorted"):
        CurrentGraph(
            **{
                **dumped,
                "unreachable_current_paths": ["B.md", "A.md"],
            }
        )
    root_supplier = dumped["suppliers"][0]
    with pytest.raises(ValidationError, match="root supplier"):
        CurrentGraph(
            **{
                **dumped,
                "suppliers": [root_supplier, root_supplier],
            }
        )


def test_graph_ceiling_arithmetic() -> None:
    a_node = CurrentGraphNode(path="A.md", status=CurrentGraphStatus.DISCOVERED_UNACQUIRED, depth=1)
    nodes = (a_node, _root_node())
    edge = CurrentGraphEdge(
        source=ROOT_FILENAME,
        target="A.md",
        kind=CurrentGraphEdgeKind.ORDINARY,
        owner=ROOT_OWNER,
        witnesses=(),
        depth=1,
    )
    certificate = CurrentGraphCertificate(
        group_identity=_hex64(21),
        group_digest=_hex64(22),
        members=("A.md",),
        candidate=_candidate(),
        possible_origins=("A.md",),
        suppliers=("A.md",),
        resolved_target="A.md",
        depth=2,
        usable=True,
        witnesses=(W1,),
    )
    ok = _valid_graph(
        graph_bounds=GraphBounds(max_edges=2),
        nodes=nodes,
        edges=(edge,),
        certificates=(certificate,),
    )
    assert ok.scope_key is not None
    with pytest.raises(ValidationError, match="edge ceiling"):
        _valid_graph(
            graph_bounds=GraphBounds(max_edges=1),
            nodes=nodes,
            edges=(edge,),
            certificates=(certificate,),
        )
    with pytest.raises(ValidationError, match="node ceiling"):
        _valid_graph(graph_bounds=GraphBounds(max_nodes=1), nodes=nodes)


def test_graph_emitted_reason_accounting() -> None:
    blocked = CurrentGraphNode(path="E.md", status=CurrentGraphStatus.BLOCKED_CONFLICT, depth=1)
    nodes = (_root_node(), blocked)
    with pytest.raises(ValidationError, match="emitted"):
        _valid_graph(nodes=nodes, emitted_reasons=0)
    ok = _valid_graph(nodes=nodes, emitted_reasons=1)
    assert ok.emitted_reasons == 1
    blocked_other = CurrentGraphNode(
        path="D.md", status=CurrentGraphStatus.BLOCKED_AMBIGUITY, depth=1
    )
    with pytest.raises(ValidationError, match="diagnostic ceiling"):
        _valid_graph(
            nodes=(_root_node(), blocked_other, blocked),
            emitted_reasons=2,
            bounds=CurrentGraphBounds(max_diagnostics=1),
        )


# ---------------------------------------------------------------------------
# Result laws (state from the ACTUAL 018-d root bootstrap)
# ---------------------------------------------------------------------------


def test_result_ok_carries_overlay_without_diagnostics(
    bootstrapped_state: CausalHistoryState,
) -> None:
    graph = _valid_graph()
    result = CurrentGraphResult(
        outcome=CurrentGraphOutcome.OK, state=bootstrapped_state, overlay=graph
    )
    assert result.overlay is graph
    assert result.diagnostics == ()
    with pytest.raises(ValidationError):
        CurrentGraphResult(
            outcome=CurrentGraphOutcome.OK,
            state=bootstrapped_state,
            overlay=graph,
            diagnostics=(CurrentGraphLimitation.ROOT_MISSING,),
        )
    with pytest.raises(ValidationError):
        CurrentGraphResult(outcome=CurrentGraphOutcome.OK, state=bootstrapped_state, overlay=None)


def test_result_refusal_carries_diagnostics_without_overlay(
    bootstrapped_state: CausalHistoryState,
) -> None:
    refusal = CurrentGraphResult(
        outcome=CurrentGraphOutcome.REFUSED_NO_ROOT,
        state=bootstrapped_state,
        diagnostics=(CurrentGraphLimitation.ROOT_MISSING,),
    )
    assert refusal.overlay is None
    with pytest.raises(ValidationError):
        CurrentGraphResult(
            outcome=CurrentGraphOutcome.REFUSED_NO_ROOT,
            state=bootstrapped_state,
            overlay=_valid_graph(),
            diagnostics=(CurrentGraphLimitation.ROOT_MISSING,),
        )
    with pytest.raises(ValidationError):
        CurrentGraphResult(
            outcome=CurrentGraphOutcome.REFUSED_NO_ROOT,
            state=bootstrapped_state,
            diagnostics=(),
        )
    with pytest.raises(ValidationError):  # sorted by value
        CurrentGraphResult(
            outcome=CurrentGraphOutcome.REFUSED_OVER_BOUND,
            state=bootstrapped_state,
            diagnostics=(
                CurrentGraphLimitation.ROOT_MISSING,
                CurrentGraphLimitation.GRAPH_NODES_OVER_BOUND,
            ),
        )
    with pytest.raises(ValidationError):  # deduplicated
        CurrentGraphResult(
            outcome=CurrentGraphOutcome.REFUSED_OVER_BOUND,
            state=bootstrapped_state,
            diagnostics=(
                CurrentGraphLimitation.GRAPH_NODES_OVER_BOUND,
                CurrentGraphLimitation.GRAPH_NODES_OVER_BOUND,
            ),
        )


# ---------------------------------------------------------------------------
# Privacy law: nested operational representations
# ---------------------------------------------------------------------------


def _rich_graph() -> CurrentGraph:
    a_owner = _owner_source("A.md", A_DIGEST)
    a_node = CurrentGraphNode(
        path="A.md",
        status=CurrentGraphStatus.CURRENT_KNOWN,
        digest=A_DIGEST,
        owner=a_owner,
        witnesses=WITNESSES,
        depth=1,
    )
    canary_node = CurrentGraphNode(
        path=f"{CANARY}.md",
        status=CurrentGraphStatus.DISCOVERED_UNACQUIRED,
        depth=1,
    )
    b_node = CurrentGraphNode(path="B.md", status=CurrentGraphStatus.DISCOVERED_UNACQUIRED, depth=2)
    c_node = CurrentGraphNode(path="C.md", status=CurrentGraphStatus.DISCOVERED_UNACQUIRED, depth=2)
    e_node = CurrentGraphNode(path="E.md", status=CurrentGraphStatus.BLOCKED_CONFLICT, depth=2)
    nodes = (a_node, _root_node(), b_node, c_node, e_node, canary_node)
    edges = (
        CurrentGraphEdge(
            source="A.md",
            target="C.md",
            kind=CurrentGraphEdgeKind.ORDINARY,
            owner=a_owner,
            witnesses=WITNESSES,
            depth=2,
        ),
        CurrentGraphEdge(
            source=ROOT_FILENAME,
            target="A.md",
            kind=CurrentGraphEdgeKind.ORDINARY,
            owner=ROOT_OWNER,
            witnesses=(),
            depth=1,
        ),
    )
    usable_cert = CurrentGraphCertificate(
        group_identity=_hex64(21),
        group_digest=_hex64(22),
        members=("B.md", "C.md"),
        candidate=_candidate(),
        possible_origins=("B.md", "C.md"),
        suppliers=("B.md",),
        resolved_target="C.md",
        depth=2,
        usable=True,
        witnesses=(W1,),
    )
    blocked_cert = CurrentGraphCertificate(
        group_identity=_hex64(21),
        group_digest=_hex64(23),
        members=("B.md", "E.md"),
        candidate=_candidate(occurrence_index=1),
        possible_origins=("B.md", "E.md"),
        suppliers=("B.md", "E.md"),
        resolved_target=None,
        usable=False,
        reasons=(CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE,),
        witnesses=(W2,),
    )
    retained = CurrentGraphCandidate(
        owner=a_owner,
        candidate=_candidate(
            target_chars=CANARY,
            status=CandidateStatus.UNSUPPORTED,
            reasons=(GraphLimitation.PATH_TRAVERSAL,),
        ),
    )
    suppliers = (
        _root_supplier(),
        CurrentGraphSupplier(
            kind=CurrentGraphSupplierKind.SOURCE,
            path="A.md",
            digest=A_DIGEST,
            members=("A.md",),
            witnesses=WITNESSES,
            coordinates=(ORIGIN,),
        ),
        CurrentGraphSupplier(
            kind=CurrentGraphSupplierKind.GROUP,
            identity=_hex64(21),
            group_digest=_hex64(22),
            members=("B.md", "C.md"),
            witnesses=(W1,),
            coordinates=(ORIGIN,),
        ),
    )
    return _valid_graph(
        suppliers=suppliers,
        nodes=nodes,
        edges=edges,
        certificates=(usable_cert, blocked_cert),
        candidates=(retained,),
        unreachable_current_paths=("E.md", f"{CANARY}.md"),
        emitted_reasons=2,
    )


def test_repr_privacy_covers_nested_records(bootstrapped_state: CausalHistoryState) -> None:
    graph = _rich_graph()
    result = CurrentGraphResult(
        outcome=CurrentGraphOutcome.OK, state=bootstrapped_state, overlay=graph
    )
    records = (
        [graph, result, ORIGIN]
        + list(graph.suppliers)
        + list(graph.nodes)
        + list(graph.edges)
        + list(graph.certificates)
        + list(graph.candidates)
    )
    for record in records:
        for representation in (repr(record), str(record)):
            assert CANARY not in representation, (type(record), representation)
    # The private path values are masked to the fixed placeholder;
    # the presence/absence flag and the counts stay observable.
    a_node = next(n for n in graph.nodes if n.path == "A.md")
    assert PRIVATE_PATH_PLACEHOLDER in repr(a_node)
    assert "A.md" not in repr(a_node)
    group_supplier = next(s for s in graph.suppliers if s.kind is CurrentGraphSupplierKind.GROUP)
    assert "path=None" in repr(group_supplier)
    # The retained candidate summary exposes the target length only,
    # never the raw target.
    retained = graph.candidates[0]
    assert f"target_length={len(CANARY)}" in repr(retained)
    assert CANARY not in repr(retained)
    # The graph-level repr masks the workspace value.
    assert "/work" not in repr(graph)
