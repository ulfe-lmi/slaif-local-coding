"""018-a: pure bounded graph closure — determinism, budgets, binding refusals."""

from __future__ import annotations

from slaif_local_coding.constitution.bundles import (
    GraphBounds,
    GraphLimitation,
    GraphNamespace,
    GraphOutcome,
    GraphSnapshot,
    NodeStatus,
    ReferenceCandidate,
    SourceDocument,
    SourceKind,
    SourceOccurrence,
    build_graph,
    make_graph_namespace,
)
from slaif_local_coding.constitution.bundles.observation_models import (
    EMPTY_SOURCE_SHA256,
    CharSpan,
)
from slaif_local_coding.constitution.cache import RequestIdentity

IDENT = RequestIdentity(
    principal="synthetic-principal",
    session="synthetic-session",
    repository="synthetic-repository",
    route="synthetic-route",
)
D1 = "1" * 64
D2 = "2" * 64
D3 = "3" * 64
D4 = "4" * 64


def ns_with(bounds: GraphBounds) -> GraphNamespace:
    return make_graph_namespace(
        IDENT,
        model_identity="synthetic-model",
        config_fingerprint="a" * 64,
        workspace="/work",
        bounds=bounds,
    )


def docs_for(ns: GraphNamespace) -> tuple[SourceDocument, ...]:
    sk = ns.scoped_key
    return (
        doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=sk),
        doc("docs/A.md", D2, scoped_key=sk),
        doc("docs/B.md", D3, scoped_key=sk),
        doc("docs/C.md", D4, scoped_key=sk),
    )


def doc(
    path: str,
    digest: str | None,
    status: NodeStatus = NodeStatus.ACQUIRED,
    kind: SourceKind | None = SourceKind.READ,
    scoped_key: str = "a" * 64,
    byte_length: int | None = 1,
    char_length: int | None = 1,
    occs: list[SourceOccurrence] | None = None,
) -> SourceDocument:
    if occs is None:
        occs = (
            [
                SourceOccurrence(
                    request_index=0,
                    carrier_location="$.input[probe]",
                    piece_index=0,
                    span=CharSpan(start=0, end=1 if status is NodeStatus.ACQUIRED else 0),
                )
            ]
            if status in (NodeStatus.ACQUIRED, NodeStatus.ACQUIRED_EMPTY)
            else []
        )
    if digest == EMPTY_SOURCE_SHA256:
        byte_length, char_length = 0, 0
    return SourceDocument(
        path=path,
        scoped_key=scoped_key,
        digest=digest,
        byte_length=byte_length,
        char_length=char_length,
        status=status,
        kind=kind,
        occurrences=tuple(occs),
    )


def cand(
    referring: str,
    target: str,
    idx: int = 0,
    referring_digest: str = D1,
    scoped_key: str = "a" * 64,
) -> ReferenceCandidate:
    from slaif_local_coding.constitution.bundles import CandidateStatus, CandidateSyntax

    return ReferenceCandidate(
        referring_path=referring,
        scoped_key=scoped_key,
        referring_digest=referring_digest,
        syntax=CandidateSyntax.PLAIN_PATH,
        target_chars=target,
        target_char_span=CharSpan(start=0, end=len(target)),
        target_byte_span=CharSpan(start=0, end=len(target)),
        resolved_path=None,
        status=CandidateStatus.ACCEPTED,
        reasons=(),
        occurrence_index=idx,
    )


def run(
    ns: GraphNamespace,
    documents: tuple[SourceDocument, ...],
    refs: dict[str, tuple[ReferenceCandidate, ...]],
    bounds: GraphBounds,
    root_path: str = "AGENTS.md",
) -> GraphSnapshot:
    return build_graph(
        documents=documents,
        root_path=root_path,
        workspace="/work",
        refs_by_path=refs,
        namespace=ns,
        bounds=bounds,
    )


class TestClosure:
    def test_root_to_nested_closure(self) -> None:
        ns = ns_with(GraphBounds())
        sk = ns.scoped_key
        snap = run(
            ns,
            docs_for(ns),
            {
                "AGENTS.md": (cand("AGENTS.md", "docs/A.md", scoped_key=sk),),
                # targets resolve against the REFERENCING document's
                # directory (docs/), so "B.md" -> docs/B.md
                "docs/A.md": (cand("docs/A.md", "B.md", referring_digest=D2, scoped_key=sk),),
            },
            GraphBounds(),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        assert {(e.from_path, e.to_path) for e in snap.edges} == {
            ("AGENTS.md", "docs/A.md"),
            ("docs/A.md", "docs/B.md"),
        }
        assert snap.max_depth == 2

    def test_arrival_order_independent_byte_equal(self) -> None:
        ns = ns_with(GraphBounds())
        sk = ns.scoped_key
        first = doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=sk)
        a = doc("docs/A.md", D2, scoped_key=sk)
        b = doc("docs/B.md", D3, scoped_key=sk)
        refs: dict[str, tuple[ReferenceCandidate, ...]] = {
            "AGENTS.md": (cand("AGENTS.md", "docs/A.md", scoped_key=sk),),
            "docs/A.md": (cand("docs/A.md", "B.md", referring_digest=D2, scoped_key=sk),),
        }
        s1 = run(ns, (first, a, b), refs, GraphBounds())
        s2 = run(ns, (b, first, a), refs, GraphBounds())
        assert s1 == s2

    def test_off_graph_document_does_not_expand(self) -> None:
        ns = ns_with(GraphBounds())
        sk = ns.scoped_key
        snap = run(
            ns,
            (
                doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=sk),
                doc("docs/OFF.md", D2, scoped_key=sk),
            ),
            {
                "docs/OFF.md": (
                    cand("docs/OFF.md", "docs/GONE.md", referring_digest=D2, scoped_key=sk),
                )
            },
            GraphBounds(),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        assert snap.edges == ()
        assert [n.path for n in snap.nodes if n.status is NodeStatus.ACQUIRED] == [
            "AGENTS.md",
            "docs/OFF.md",
        ]

    def test_missing_reachable_content_never_fabricated(self) -> None:
        ns = ns_with(GraphBounds())
        sk = ns.scoped_key
        snap = run(
            ns,
            (doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=sk),),
            {"AGENTS.md": (cand("AGENTS.md", "docs/GONE.md", scoped_key=sk),)},
            GraphBounds(),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        assert snap.missing == ("docs/GONE.md",)
        gone = next(n for n in snap.nodes if n.path == "docs/GONE.md")
        assert gone.status is NodeStatus.DISCOVERED_CONTENT_MISSING
        assert gone.digest is None
        assert gone.kind is None

    def test_acquired_empty_source_has_no_outgoing(self) -> None:
        ns = ns_with(GraphBounds())
        sk = ns.scoped_key
        snap = run(
            ns,
            (
                doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=sk),
                doc(
                    "docs/EMPTY.md",
                    EMPTY_SOURCE_SHA256,
                    status=NodeStatus.ACQUIRED_EMPTY,
                    scoped_key=sk,
                ),
            ),
            {
                "AGENTS.md": (cand("AGENTS.md", "docs/EMPTY.md", scoped_key=sk),),
                "docs/EMPTY.md": (
                    cand(
                        "docs/EMPTY.md",
                        "docs/B.md",
                        referring_digest=EMPTY_SOURCE_SHA256,
                        scoped_key=sk,
                    ),
                ),
            },
            GraphBounds(),
        )
        # Empty source: its own references must not expand (no body was
        # acquired to scan); the reference record is inert.
        # EXACT expectation: the incoming root edge is present (a
        # subset check would also pass with NO edge at all), the empty
        # node has no outgoing edge, and the edge carries the target's
        # true shortest root distance (1).
        assert [(e.from_path, e.to_path) for e in snap.edges] == [
            ("AGENTS.md", "docs/EMPTY.md"),
        ]
        assert snap.edges[0].depth == 1
        empty = next(n for n in snap.nodes if n.path == "docs/EMPTY.md")
        assert empty.status is NodeStatus.ACQUIRED_EMPTY
        assert empty.digest == EMPTY_SOURCE_SHA256
        assert empty.byte_length == 0
        assert snap.missing == ()

    def test_repeated_identical_root_deduped(self) -> None:
        ns = ns_with(GraphBounds())
        sk = ns.scoped_key
        root = doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=sk)
        snap = run(
            ns,
            (root, root),
            {},
            GraphBounds(),
        )
        roots = [n for n in snap.nodes if n.path == "AGENTS.md"]
        assert len(roots) == 1
        assert len(roots[0].occurrences) == 2

    def test_self_cycle_terminates_with_depth_zero(self) -> None:
        ns = ns_with(GraphBounds())
        sk = ns.scoped_key
        snap = run(
            ns,
            (doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=sk),),
            {"AGENTS.md": (cand("AGENTS.md", "AGENTS.md", scoped_key=sk),)},
            GraphBounds(),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        assert len(snap.edges) == 1
        assert snap.edges[0].depth == 0
        assert snap.max_depth == 0

    def test_two_node_cycle_terminates_with_shortest_depths(self) -> None:
        ns = ns_with(GraphBounds())
        sk = ns.scoped_key
        snap = run(
            ns,
            docs_for(ns)[:3],
            {
                "AGENTS.md": (cand("AGENTS.md", "docs/A.md", scoped_key=sk),),
                "docs/A.md": (cand("docs/A.md", "B.md", referring_digest=D2, scoped_key=sk),),
                "docs/B.md": (cand("docs/B.md", "A.md", referring_digest=D3, scoped_key=sk),),
            },
            GraphBounds(),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        assert snap.max_depth == 2
        depths = {(e.from_path, e.to_path): e.depth for e in snap.edges}
        assert depths == {
            ("AGENTS.md", "docs/A.md"): 1,
            ("docs/A.md", "docs/B.md"): 2,
            ("docs/B.md", "docs/A.md"): 1,
        }

    def test_shared_target_single_edge_with_occurrence_evidence(self) -> None:
        ns = ns_with(GraphBounds())
        sk = ns.scoped_key
        snap = run(
            ns,
            (
                doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=sk),
                doc("docs/A.md", D2, scoped_key=sk),
            ),
            {
                "AGENTS.md": (
                    cand("AGENTS.md", "docs/A.md", 0, scoped_key=sk),
                    cand("AGENTS.md", "docs/A.md", 1, scoped_key=sk),
                    cand("AGENTS.md", "docs/A.md", 2, scoped_key=sk),
                ),
            },
            GraphBounds(),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        assert len(snap.edges) == 1
        assert snap.candidates_total == 3

    def test_version_conflict_independent_of_input_order(self) -> None:
        ns = ns_with(GraphBounds())
        sk = ns.scoped_key
        a1 = doc("docs/A.md", D2, scoped_key=sk)
        a2 = doc("docs/A.md", D3, scoped_key=sk)
        root = doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=sk)
        refs: dict[str, tuple[ReferenceCandidate, ...]] = {
            "AGENTS.md": (cand("AGENTS.md", "docs/A.md", scoped_key=sk),)
        }
        s1 = run(ns, (root, a1, a2), refs, GraphBounds())
        s2 = run(ns, (root, a2, a1), refs, GraphBounds())
        assert s1 == s2
        assert s1.outcome is GraphOutcome.VERSION_CONFLICT
        node = next(n for n in s1.nodes if n.path == "docs/A.md")
        assert node.status is NodeStatus.VERSION_CONFLICT
        assert node.digest is None
        assert node.kind is None
        assert node.byte_length is None
        assert len(node.occurrences) == 2
        # The reference still points at the conflicting PATH; no
        # version is selected for it.
        assert {(e.from_path, e.to_path) for e in s1.edges} == {
            ("AGENTS.md", "docs/A.md"),
        }

    def test_competing_effective_root_refused(self) -> None:
        ns = ns_with(GraphBounds())
        sk = ns.scoped_key
        snap = run(
            ns,
            (
                doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=sk),
                doc("AGENTS.md", D2, scoped_key=sk),  # tool read, different content
            ),
            {},
            GraphBounds(),
        )
        assert snap.outcome is GraphOutcome.ROOT_CONFLICT
        assert GraphLimitation.COMPETING_ROOTS in snap.conflicts


class TestBudgets:
    def test_nodes_at_limit_and_one_over(self) -> None:
        at = ns_with(GraphBounds(max_nodes=4))
        snap = run(at, docs_for(at), {}, GraphBounds(max_nodes=4))
        assert snap.outcome is GraphOutcome.COMPLETE
        over = ns_with(GraphBounds(max_nodes=3))
        snap = run(over, docs_for(over), {}, GraphBounds(max_nodes=3))
        assert snap.outcome is GraphOutcome.OVER_BOUND
        assert snap.conflicts == (GraphLimitation.NODES_OVER_BOUND,)

    def test_edges_at_limit_and_one_over(self) -> None:
        at = ns_with(GraphBounds(max_edges=3))
        snap = run(
            at,
            docs_for(at),
            {
                "AGENTS.md": (
                    cand("AGENTS.md", "docs/A.md", 0, scoped_key=at.scoped_key),
                    cand("AGENTS.md", "docs/B.md", 1, scoped_key=at.scoped_key),
                    cand("AGENTS.md", "docs/C.md", 2, scoped_key=at.scoped_key),
                )
            },
            GraphBounds(max_edges=3),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        assert len(snap.edges) == 3
        over = ns_with(GraphBounds(max_edges=2))
        snap = run(
            over,
            docs_for(over),
            {
                "AGENTS.md": (
                    cand("AGENTS.md", "docs/A.md", 0, scoped_key=over.scoped_key),
                    cand("AGENTS.md", "docs/B.md", 1, scoped_key=over.scoped_key),
                    cand("AGENTS.md", "docs/C.md", 2, scoped_key=over.scoped_key),
                )
            },
            GraphBounds(max_edges=2),
        )
        assert snap.outcome is GraphOutcome.OVER_BOUND
        assert snap.conflicts == (GraphLimitation.EDGES_OVER_BOUND,)

    def test_depth_at_limit_and_one_over(self) -> None:
        def chain_refs(sk: str) -> dict[str, tuple[ReferenceCandidate, ...]]:
            return {
                "AGENTS.md": (cand("AGENTS.md", "docs/A.md", scoped_key=sk),),
                "docs/A.md": (cand("docs/A.md", "B.md", referring_digest=D2, scoped_key=sk),),
                "docs/B.md": (cand("docs/B.md", "C.md", referring_digest=D3, scoped_key=sk),),
            }

        at = ns_with(GraphBounds(max_depth=3))
        snap = run(at, docs_for(at), chain_refs(at.scoped_key), GraphBounds(max_depth=3))
        assert snap.outcome is GraphOutcome.COMPLETE
        assert snap.max_depth == 3
        over = ns_with(GraphBounds(max_depth=2))
        snap = run(over, docs_for(over), chain_refs(over.scoped_key), GraphBounds(max_depth=2))
        assert snap.outcome is GraphOutcome.OVER_BOUND
        assert snap.conflicts == (GraphLimitation.DEPTH_OVER_BOUND,)

    def test_work_units_at_limit_and_one_over(self) -> None:
        def chain_refs(sk: str) -> dict[str, tuple[ReferenceCandidate, ...]]:
            return {
                "AGENTS.md": (cand("AGENTS.md", "docs/A.md", scoped_key=sk),),
                "docs/A.md": (cand("docs/A.md", "B.md", referring_digest=D2, scoped_key=sk),),
                "docs/B.md": (cand("docs/B.md", "C.md", referring_digest=D3, scoped_key=sk),),
            }

        # One work unit per dequeued node + per candidate: 4 nodes + 3
        # candidates = 7 units on the full chain.
        at = ns_with(GraphBounds(max_work_units=7))
        snap = run(at, docs_for(at), chain_refs(at.scoped_key), GraphBounds(max_work_units=7))
        assert snap.outcome is GraphOutcome.COMPLETE
        over = ns_with(GraphBounds(max_work_units=6))
        snap = run(over, docs_for(over), chain_refs(over.scoped_key), GraphBounds(max_work_units=6))
        assert snap.outcome is GraphOutcome.OVER_BOUND
        assert snap.conflicts == (GraphLimitation.WORK_UNITS_EXHAUSTED,)

    def test_diagnostics_at_limit_and_one_over(self) -> None:
        at = ns_with(GraphBounds(max_diagnostics=1))
        snap = run(
            at,
            (doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=at.scoped_key),),
            {"AGENTS.md": (cand("AGENTS.md", "/work-other/A.md", 0, scoped_key=at.scoped_key),)},
            GraphBounds(max_diagnostics=1),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        assert snap.conflicts == (GraphLimitation.PATH_OUTSIDE_WORKSPACE,)
        over = ns_with(GraphBounds(max_diagnostics=1))
        snap = run(
            over,
            (doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=over.scoped_key),),
            {
                "AGENTS.md": (
                    cand("AGENTS.md", "/work-other/A.md", 0, scoped_key=over.scoped_key),
                    cand("AGENTS.md", "../EVIL.md", 1, scoped_key=over.scoped_key),
                )
            },
            GraphBounds(max_diagnostics=1),
        )
        assert snap.outcome is GraphOutcome.OVER_BOUND
        assert snap.conflicts == (GraphLimitation.DIAGNOSTICS_FULL,)

    def test_path_bytes_at_limit_and_one_over(self) -> None:
        at = ns_with(GraphBounds(max_path_bytes=9))
        snap = run(
            at,
            (doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=at.scoped_key),),
            {
                "AGENTS.md": (cand("AGENTS.md", "docs/A.md", scoped_key=at.scoped_key),),
            },
            GraphBounds(max_path_bytes=9),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        assert len(snap.edges) == 1
        over = ns_with(GraphBounds(max_path_bytes=8))
        snap = run(
            over,
            (doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=over.scoped_key),),
            {
                "AGENTS.md": (cand("AGENTS.md", "docs/A.md", scoped_key=over.scoped_key),),
            },
            GraphBounds(max_path_bytes=8),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        assert snap.edges == ()
        assert GraphLimitation.PATH_TOO_LONG in snap.conflicts


class TestBindingRefusals:
    def test_candidate_must_bind_actual_referring_version(self) -> None:
        ns = ns_with(GraphBounds())
        sk = ns.scoped_key
        snap = run(
            ns,
            (
                doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=sk),
                doc("docs/A.md", D2, scoped_key=sk),
            ),
            {
                "AGENTS.md": (cand("AGENTS.md", "docs/A.md", scoped_key=sk),),
                # Forged: claims the root digest for a docs/A.md
                # reference that actually maps to digest D2.
                "docs/A.md": (cand("docs/A.md", "B.md", referring_digest=D1, scoped_key=sk),),
            },
            GraphBounds(),
        )
        assert snap.outcome is GraphOutcome.VERSION_CONFLICT
        assert snap.conflicts == (GraphLimitation.CANDIDATE_DIGEST_MISMATCH,)
        assert snap.edges == ()

    def test_bounds_mismatch_refused(self) -> None:
        ns = ns_with(GraphBounds())
        snap = run(ns, docs_for(ns), {}, GraphBounds(max_nodes=7))
        assert snap.outcome is GraphOutcome.OVER_BOUND
        assert snap.conflicts == (GraphLimitation.BOUNDS_MISMATCH,)

    def test_workspace_mismatch_refused(self) -> None:
        ns = ns_with(GraphBounds())
        other = make_graph_namespace(
            IDENT,
            model_identity="synthetic-model",
            config_fingerprint="a" * 64,
            workspace="/other",
            bounds=ns.bounds,
        )
        snap = run(
            ns,
            (doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=ns.scoped_key),),
            {},
            ns.bounds,
        )
        assert snap.outcome is GraphOutcome.COMPLETE  # sanity: own scope works
        mismatched = build_graph(
            documents=(doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=other.scoped_key),),
            root_path="AGENTS.md",
            workspace="/work",
            refs_by_path={},
            namespace=other,
            bounds=other.bounds,
        )
        # documents from another scope than the namespace: refused.
        assert mismatched.outcome is GraphOutcome.OVER_BOUND

    def test_namespace_scope_mismatch_refused(self) -> None:
        ns = ns_with(GraphBounds())
        foreign = make_graph_namespace(
            RequestIdentity(
                principal="other-principal",
                session="synthetic-session",
                repository="synthetic-repository",
                route="synthetic-route",
            ),
            model_identity="synthetic-model",
            config_fingerprint="a" * 64,
            workspace="/work",
            bounds=ns.bounds,
        )
        snap = run(
            ns,
            (doc("AGENTS.md", D1, kind=SourceKind.ROOT, scoped_key=foreign.scoped_key),),
            {},
            ns.bounds,
        )
        assert snap.outcome is GraphOutcome.OVER_BOUND
        assert snap.conflicts == (GraphLimitation.NAMESPACE_MISMATCH,)
        assert snap.nodes == ()

    def test_no_root_refused(self) -> None:
        ns = ns_with(GraphBounds())
        snap = run(
            ns,
            (doc("docs/A.md", D2, scoped_key=ns.scoped_key),),
            {},
            GraphBounds(),
        )
        assert snap.outcome is GraphOutcome.NO_ROOT
        assert snap.nodes == ()
