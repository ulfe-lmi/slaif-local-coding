"""Pure bounded graph closure for the 018-a trusted-namespace foundation.

``resolve_reference`` is the lexical resolution law (fragment stripped
for resolution ONLY; ``..`` safe while every prefix stays inside the
evidenced workspace; absolute targets accepted only under component
containment proof; no filesystem, no ``resolve``/``stat``/``exists``).

``build_graph`` is the fixed-point closure over acquired workspace
documents: edges only from reachable attributable current documents;
``max_depth`` is the TRUE shortest root distance (relaxation over the
edge set, not discovery order; empty and missing reachable leaves are
distance nodes too, so a walk into an already shallower target never
falsely over-bounds); repeated references to the same target are ONE
deduplicated directed edge (occurrence evidence stays in the candidate
records); every node (including each ``DISCOVERED_CONTENT_MISSING``
node) is counted against ``max_nodes`` BEFORE insertion; every emitted
edge is bound to the ACTUAL mapped version of its referring document
(a candidate whose referring path/digest does not match the mapped
document is a fixed typed refusal, never an edge); the supplied bounds
must equal the namespace-bound bounds; unread referenced documents
become ``DISCOVERED_CONTENT_MISSING`` nodes (never fabricated); same
path with different content is a typed ``VERSION_CONFLICT`` (never
chosen by tuple order/call ID/hash/arrival); the accumulated emitted
fixed reasons are bounded by ``max_diagnostics`` (overflow is one fixed
``DIAGNOSTICS_FULL`` refusal, never an unbounded reason set); over any
budget is a fixed typed ``OVER_BOUND`` refusal, never a success-shaped
truncated prefix.

Pure and inert: no filesystem, network, shell or model facility.  All
records carry the explicit scoped key of the single supplied namespace
(R2 law); a supplied record from another scope is a fixed
``NAMESPACE_MISMATCH`` refusal before any work.
"""

from __future__ import annotations

import math
from collections import deque
from collections.abc import Mapping

from .graph_models import (
    CandidateStatus,
    GraphBounds,
    GraphEdge,
    GraphLimitation,
    GraphNamespace,
    GraphOutcome,
    GraphSnapshot,
    NodeStatus,
    ReferenceCandidate,
    SourceDocument,
    SourceKind,
)


def _refusal(
    namespace: GraphNamespace,
    outcome: GraphOutcome,
    conflicts: tuple[GraphLimitation, ...],
    work_units: int = 0,
) -> GraphSnapshot:
    return GraphSnapshot(
        namespace=namespace,
        outcome=outcome,
        conflicts=conflicts,
        work_units=work_units,
    )


def _walk(base: list[str], segments: list[str]) -> list[str] | GraphLimitation:
    """Lexical segment walk; ``..`` may never pop below the workspace root."""
    stack: list[str] = list(base)
    for segment in segments:
        if segment in ("", "."):
            continue
        if segment == "..":
            if not stack:
                return GraphLimitation.PATH_TRAVERSAL
            stack.pop()
            continue
        stack.append(segment)
    return stack


def resolve_reference(
    referring_path: str,
    target: str,
    workspace: str,
    max_path_bytes: int,
) -> tuple[str | None, GraphLimitation | None]:
    """Resolve one reference target lexically against the workspace.

    ``target`` is the exact observed destination characters (a fragment
    after the first ``#`` is stripped for resolution ONLY and never
    rewritten into the target).  Relative targets resolve against the
    referring document's directory; absolute targets are accepted only
    under component containment proof against the evidenced workspace
    (``/work-other`` is not inside ``/work``).  Returns the normalized
    workspace-relative path, or the exact typed refusal.
    """
    path_portion = target.split("#", 1)[0]
    if not path_portion:
        return None, GraphLimitation.TARGET_UNSUPPORTED_CHAR
    workspace_parts = [part for part in workspace[1:].split("/") if part]
    if path_portion.startswith("/"):
        if path_portion.startswith("//"):
            return None, GraphLimitation.PATH_OUTSIDE_WORKSPACE
        parts = [part for part in path_portion[1:].split("/") if part]
        if len(parts) <= len(workspace_parts):
            # The workspace directory itself (or an ancestor): a
            # directory, never a file target.
            return None, GraphLimitation.PATH_OUTSIDE_WORKSPACE
        if parts[: len(workspace_parts)] != workspace_parts:
            return None, GraphLimitation.PATH_OUTSIDE_WORKSPACE
        base: list[str] = []
        segments = parts[len(workspace_parts) :]
    else:
        base = [part for part in referring_path.split("/") if part][:-1]
        segments = path_portion.split("/")
    walked = _walk(base, segments)
    if isinstance(walked, GraphLimitation):
        return None, walked
    if not walked:
        return None, GraphLimitation.PATH_TRAVERSAL
    normalized = "/".join(walked)
    if len(normalized.encode("utf-8")) > max_path_bytes:
        return None, GraphLimitation.PATH_TOO_LONG
    return normalized, None


def _scope_mismatch(
    namespace: GraphNamespace,
    documents: tuple[SourceDocument, ...],
    refs_by_path: Mapping[str, tuple[ReferenceCandidate, ...]],
) -> bool:
    if any(doc.scoped_key != namespace.scoped_key for doc in documents):
        return True
    return any(
        candidate.scoped_key != namespace.scoped_key
        for candidates in refs_by_path.values()
        for candidate in candidates
    )


def build_graph(
    documents: tuple[SourceDocument, ...],
    root_path: str,
    workspace: str,
    refs_by_path: Mapping[str, tuple[ReferenceCandidate, ...]],
    namespace: GraphNamespace,
    bounds: GraphBounds,
) -> GraphSnapshot:
    """Build the deterministic bounded graph snapshot for one namespace.

    ``documents`` are the acquired source records (ACQUIRED /
    ACQUIRED_EMPTY) constructed under *namespace* by the composition;
    ``refs_by_path`` maps each acquired document path to its scanned
    candidate records.  The snapshot's ``request_count`` /
    ``observation_limitations`` / unresolved-origin fields and the
    all-candidates totals are finalized by the public composition
    (``model_copy``), which is the only caller that holds batch-level
    facts.
    """
    if workspace != namespace.workspace:
        return _refusal(namespace, GraphOutcome.OVER_BOUND, (GraphLimitation.WORKSPACE_MISMATCH,))
    if bounds != namespace.bounds:
        # The namespace key binds the effective bounds; a different
        # effective configuration is a caller contract violation.
        return _refusal(namespace, GraphOutcome.OVER_BOUND, (GraphLimitation.BOUNDS_MISMATCH,))
    if _scope_mismatch(namespace, documents, refs_by_path):
        return _refusal(namespace, GraphOutcome.OVER_BOUND, (GraphLimitation.NAMESPACE_MISMATCH,))

    # --- Root binding -------------------------------------------------
    root_docs = [
        doc
        for doc in documents
        if doc.path == root_path
        and doc.kind is not None
        and doc.kind is SourceKind.ROOT
        and doc.status in (NodeStatus.ACQUIRED, NodeStatus.ACQUIRED_EMPTY)
    ]
    root_conflicted = any(
        doc.path == root_path and doc.status is NodeStatus.VERSION_CONFLICT for doc in documents
    )
    if root_conflicted:
        # A tool read at the root path with different content is a
        # competing effective root: no reset/supersession, typed
        # conflict (a tool read never establishes the root).
        return _refusal(
            namespace,
            GraphOutcome.ROOT_CONFLICT,
            (GraphLimitation.COMPETING_ROOTS,),
        )
    if not root_docs:
        return _refusal(namespace, GraphOutcome.NO_ROOT, (GraphLimitation.NO_ROOT,))
    root_digests = {doc.digest for doc in root_docs}
    if len(root_digests) > 1:
        return _refusal(namespace, GraphOutcome.ROOT_CONFLICT, (GraphLimitation.COMPETING_ROOTS,))

    # --- Node map (dedup by path+digest; conflict by path) ------------
    nodes: dict[str, SourceDocument] = {}
    conflict_paths: set[str] = set()
    for doc in documents:
        if doc.status not in (
            NodeStatus.ACQUIRED,
            NodeStatus.ACQUIRED_EMPTY,
            NodeStatus.VERSION_CONFLICT,
        ):
            continue
        existing = nodes.get(doc.path)
        if existing is None:
            nodes[doc.path] = doc
            if doc.status is NodeStatus.VERSION_CONFLICT:
                conflict_paths.add(doc.path)
            continue
        if (
            doc.status is NodeStatus.VERSION_CONFLICT
            or existing.status is NodeStatus.VERSION_CONFLICT
        ):
            merged = existing.occurrences + doc.occurrences
            nodes[doc.path] = SourceDocument(
                path=doc.path,
                scoped_key=namespace.scoped_key,
                digest=None,
                byte_length=None,
                char_length=None,
                status=NodeStatus.VERSION_CONFLICT,
                kind=None,
                occurrences=merged,
            )
            conflict_paths.add(doc.path)
            continue
        if doc.digest == existing.digest:
            merged_occurrences = existing.occurrences + doc.occurrences
            nodes[doc.path] = existing.model_copy(update={"occurrences": merged_occurrences})
        else:
            # Same path, different content: typed conflict, no version
            # selected (no kind/digest/lengths retained).
            merged = existing.occurrences + doc.occurrences
            nodes[doc.path] = SourceDocument(
                path=doc.path,
                scoped_key=namespace.scoped_key,
                digest=None,
                byte_length=None,
                char_length=None,
                status=NodeStatus.VERSION_CONFLICT,
                kind=None,
                occurrences=merged,
            )
            conflict_paths.add(doc.path)

    if root_path not in nodes:
        return _refusal(namespace, GraphOutcome.NO_ROOT, (GraphLimitation.NO_ROOT,))
    if len(nodes) > bounds.max_nodes:
        return _refusal(namespace, GraphOutcome.OVER_BOUND, (GraphLimitation.NODES_OVER_BOUND,))

    # --- Fixed-point closure (shortest-distance relaxation) -----------
    # ``dist`` is the TRUE shortest root distance per reachable path
    # (strict-decrease relaxation, so cycles terminate); it covers empty
    # and missing reachable leaves, not only queued nonempty sources.
    # ``edge_owners`` deduplicates graph edge ownership: repeated
    # references to the same (from, to) pair are ONE directed edge, and
    # the occurrence evidence stays in the candidate records.
    work_units = 0
    edge_owners: dict[tuple[str, str], tuple[str, int]] = {}
    missing: set[str] = set()
    path_limitations: set[GraphLimitation] = set()
    dist: dict[str, int] = {}
    if nodes[root_path].status is not NodeStatus.VERSION_CONFLICT:
        dist[root_path] = 0
        queue: deque[str] = deque([root_path])
    else:
        queue = deque()

    while queue:
        current = queue.popleft()
        work_units += 1
        if work_units > bounds.max_work_units:
            return _refusal(
                namespace,
                GraphOutcome.OVER_BOUND,
                (GraphLimitation.WORK_UNITS_EXHAUSTED,),
                work_units,
            )
        ref_doc = nodes[current]
        for candidate in refs_by_path.get(current, ()):
            work_units += 1
            if work_units > bounds.max_work_units:
                return _refusal(
                    namespace,
                    GraphOutcome.OVER_BOUND,
                    (GraphLimitation.WORK_UNITS_EXHAUSTED,),
                    work_units,
                )
            if candidate.status is not CandidateStatus.ACCEPTED:
                continue
            if (
                candidate.referring_path != current
                or ref_doc.digest is None
                or candidate.referring_digest != ref_doc.digest
            ):
                # A candidate that cannot bind to the ACTUAL mapped
                # document version must never emit an edge.
                return _refusal(
                    namespace,
                    GraphOutcome.VERSION_CONFLICT,
                    (GraphLimitation.CANDIDATE_DIGEST_MISMATCH,),
                    work_units,
                )
            resolved, limitation = resolve_reference(
                current, candidate.target_chars, workspace, bounds.max_path_bytes
            )
            if limitation is not None:
                path_limitations.add(limitation)
                continue
            assert resolved is not None
            key = (current, resolved)
            if key not in edge_owners:
                if len(edge_owners) + 1 > bounds.max_edges:
                    return _refusal(
                        namespace,
                        GraphOutcome.OVER_BOUND,
                        (GraphLimitation.EDGES_OVER_BOUND,),
                        work_units,
                    )
                edge_owners[key] = (
                    candidate.referring_digest,
                    candidate.occurrence_index,
                )
            if resolved not in nodes:
                if len(nodes) + 1 > bounds.max_nodes:
                    return _refusal(
                        namespace,
                        GraphOutcome.OVER_BOUND,
                        (GraphLimitation.NODES_OVER_BOUND,),
                        work_units,
                    )
                nodes[resolved] = SourceDocument(
                    path=resolved,
                    scoped_key=namespace.scoped_key,
                    status=NodeStatus.DISCOVERED_CONTENT_MISSING,
                )
                missing.add(resolved)
            next_depth = dist[current] + 1
            if next_depth < dist.get(resolved, math.inf):
                dist[resolved] = next_depth
                node = nodes.get(resolved)
                if node is not None and node.status is NodeStatus.ACQUIRED:
                    queue.append(resolved)

    max_reach = max(dist.values()) if dist else 0
    if max_reach > bounds.max_depth:
        # Shortest-distance law: only a node whose TRUE shortest root
        # distance exceeds the bound over-bounds the graph; a walk that
        # reaches an already shallower target never does.
        return _refusal(
            namespace,
            GraphOutcome.OVER_BOUND,
            (GraphLimitation.DEPTH_OVER_BOUND,),
            work_units,
        )
    conflict_set = (
        {GraphLimitation.VERSION_CONFLICT} if conflict_paths else set()
    ) | path_limitations
    if root_path in conflict_paths:
        # A tool read at the root path with different content is a
        # competing effective root: no reset/supersession, typed conflict.
        conflict_set.add(GraphLimitation.COMPETING_ROOTS)
    if len(conflict_set) > bounds.max_diagnostics:
        # Finite diagnostic budget over the accumulated emitted fixed
        # reasons: overflow is one fixed typed refusal, never a
        # success-shaped snapshot with an unbounded reason set (no
        # silent truncation, no governance loss).
        return _refusal(
            namespace,
            GraphOutcome.OVER_BOUND,
            (GraphLimitation.DIAGNOSTICS_FULL,),
            work_units,
        )
    outcome = (
        GraphOutcome.ROOT_CONFLICT
        if root_path in conflict_paths
        else GraphOutcome.VERSION_CONFLICT
        if conflict_paths
        else GraphOutcome.COMPLETE
    )
    conflicts = tuple(sorted(conflict_set))
    ordered_nodes = tuple(
        sorted(
            nodes.values(),
            key=lambda doc: (doc.path, doc.status.value),
        )
    )
    ordered_edges = tuple(
        sorted(
            (
                GraphEdge(
                    scoped_key=namespace.scoped_key,
                    from_path=from_path,
                    to_path=to_path,
                    referring_digest=referring_digest,
                    occurrence_index=occurrence_index,
                    # The target's TRUE shortest root distance (0 for
                    # a root self-reference); cycle back-edges never
                    # inflate: they carry the target's shortest
                    # distance, not the walk length.
                    depth=dist[to_path],
                )
                for (from_path, to_path), (
                    referring_digest,
                    occurrence_index,
                ) in edge_owners.items()
            ),
            key=lambda edge: (
                edge.from_path,
                edge.to_path,
                edge.referring_digest,
                edge.occurrence_index,
            ),
        )
    )
    candidates_total = sum(len(items) for items in refs_by_path.values())
    candidates_per_document_max = max((len(items) for items in refs_by_path.values()), default=0)
    source_bytes = sum(doc.byte_length for doc in documents if doc.byte_length is not None)
    return GraphSnapshot(
        namespace=namespace,
        outcome=outcome,
        root_path=root_path,
        root_digest=nodes[root_path].digest,
        nodes=ordered_nodes,
        edges=ordered_edges,
        missing=tuple(sorted(missing)),
        conflicts=conflicts,
        work_units=work_units,
        max_depth=max_reach,
        documents_inspected=len(documents),
        source_bytes_inspected=source_bytes,
        candidates_total=candidates_total,
        candidates_per_document_max=candidates_per_document_max,
    )
