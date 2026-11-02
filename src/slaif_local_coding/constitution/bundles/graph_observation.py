"""Public bounded graph observation composition (objective 018-a).

``observe_graph_batch`` / ``observe_graph`` are the typed public entry
points: each request runs the ACCEPTED 017 pure observation under the
017 package's own ceilings (the 017 report retains spans/digests/
metadata only, never raw source bytes), the single evidenced root and
workspace are bound, the GRAPH-OWNED cumulative source ledger is
enforced BEFORE any graph-owned body copy/reconstruction/retention
(every inspected source body — the root body, every legacy read
content body, every proven native process region body — complete,
duplicate and unsupported included, within each request and across the
batch), bounded documents are acquired, their references scanned, and
the deterministic graph closed.

Pure and inert: the payload is never mutated; no filesystem, process,
network or model facility anywhere in the module (tests monkeypatch
and fail on any attempt).  Cross-surface dedup: the same call/result
occurrence positive on both the legacy read and the native process
surface is ONE node iff call identity, positions, carrier evidence,
ordered members, region intervals and the exact digest all agree; the
pinned native WITH-token-line frame is legacy-MALFORMED (non-acquiring)
yet its independently earned process region is still consumed (no
veto).  A tool read never establishes a root.

Derived-context law: the single evidenced root scope is the design-
promised workspace for requests whose own context carries no evidenced
workspace — such requests are RE-OBSERVED under it (an explicit
workdir is preserved; explicit contexts keep their original reports)
BEFORE any read/process acquisition, so a context-less request acquires
exactly what an evidenced-context request would.  The 017 package keeps
its own semantics and ceilings throughout.

    Cross-surface seam law: a single call/result occurrence that is
    positive on BOTH the legacy read and the native process surface must
    prove the SAME source with the SAME full proof signature FIRST —
    the actual call position, the exact original carrier intervals
    (occurrences keyed by request index, carrier and piece), the
    ordered member and the exact digest; the same-occurrence proof is
    compared before any retention, and ``_retain`` by path and
    post-hoc dedup never compare it.  Equal bytes in DIFFERENT
    original intervals are not matching proof.  A mismatched positive
    seam is a typed conflict: the conflicting occurrence is pruned
    from each fact's node (it acquires NO source or edge — no
    good-looking selection), and a would-be ready snapshot is refused
    ``VERSION_CONFLICT``.  Single-member retention additionally
    requires the recorded member digest to equal the ACTUAL
    reconstructed content/region bytes (a metadata-only hash is not
    source proof).  Boundaryless multi-member bundles are held to the
    SAME consistency law on their WHOLE-BUNDLE proof: the ordered
    member paths, the exact whole digest and the original occurrence
    evidence.  Equal proof on the same occurrence is ONE
    unresolved-origin record (read primary, counted once), and a
    mismatched ordered proof acquires no source/candidate record from
    that occurrence and refuses ready.  Unknown per-member hashes do
    not erase whole-bundle proof; no per-file split, hash or edge is
    invented and no admission policy is introduced.
"""

from __future__ import annotations

from typing import Any, NamedTuple

from pydantic import field_validator

from ..bundles.client_paths import normalize_read_path, validate_workspace
from ..bundles.graph import build_graph
from ..bundles.graph_models import (
    ROOT_FILENAME,
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
    UnresolvedOriginCandidate,
    _fixed,
    _GraphFrozen,
    _sha256_hex,
)
from ..bundles.observation_models import (
    Limitation,
    NormalizedPath,
    PathContext,
    ProcessOutcome,
    ProcessPiece,
    ReadOutcome,
    sha256_hex,
)
from ..bundles.observe import (
    ENDPOINT_CHAT,
    ENDPOINT_RESPONSES,
    observe_request,
)
from ..bundles.process_chunks import _utf8_byte_length_range
from ..bundles.references import ReferenceScan, scan_references


class GraphRequest(_GraphFrozen):
    """One bounded decoded request for the public graph composition.

    ``endpoint`` is the explicit validated endpoint context (017 law);
    ``context`` is the evidenced client-workspace context (``None``
    allowed; its workspace, when present, must AGREE with the evidenced
    root scope).  The payload is protected internal data: the
    operational representation never echoes it.
    """

    payload: dict[str, Any]
    endpoint: str
    context: PathContext | None = None

    @field_validator("endpoint")
    @classmethod
    def _v_endpoint(cls, value: str) -> str:
        if value not in (ENDPOINT_RESPONSES, ENDPOINT_CHAT):
            raise _fixed("endpoint must be an explicit validated endpoint")
        return value

    def __repr__(self) -> str:
        context = "None" if self.context is None else "PathContext(<protected>)"
        return (
            f"GraphRequest(payload=<protected dict {len(self.payload)} keys>, "
            f"endpoint={self.endpoint!r}, context={context})"
        )

    __str__ = __repr__


class _SourceLedger:
    """Graph-owned cumulative source budget ledger (R4 law).

    Accounts exact UTF-8 byte lengths of every inspected source body
    BEFORE any graph-owned copy/retention; at-limit stays at-limit and
    the first over-bound source is a fixed typed refusal (no body copy
    for the exceeding or later sources).
    """

    def __init__(self, bounds: GraphBounds) -> None:
        self._bounds = bounds
        self.total_bytes = 0
        self.documents = 0
        self.refusal: GraphLimitation | None = None

    def account(self, byte_length: int) -> None:
        if self.refusal is not None:
            return
        if byte_length > self._bounds.max_single_source_bytes:
            self.refusal = GraphLimitation.SOURCE_OVER_BOUND
            return
        if self.total_bytes + byte_length > self._bounds.max_total_inspected_source_bytes:
            self.refusal = GraphLimitation.TOTAL_SOURCE_OVER_BOUND
            return
        self.total_bytes += byte_length
        self.documents += 1
        if self.documents > self._bounds.max_documents:
            self.refusal = GraphLimitation.DOCUMENT_OVER_BOUND


def _carrier_string(payload: dict[str, Any], location: str) -> str | None:
    """The exact decoded string carried at one 017 location pointer.

    Strict walker over the three 017 location shapes (root item text,
    Responses function_call_output, Chat tool content); never evaluates
    or infers, returns ``None`` on any deviation.
    """
    if location.startswith("$.input["):
        rest = location[len("$.input[") :]
        index_s, sep, tail = rest.partition("]")
        if not sep or not index_s.isdigit():
            return None
        index = int(index_s)
        items = payload.get("input")
        if not isinstance(items, list) or index >= len(items):
            return None
        item = items[index]
        if not isinstance(item, dict):
            return None
        if tail == "":
            value = item.get("output")
            return value if isinstance(value, str) else None
        if not tail.startswith(".content["):
            return None
        index2_s, sep2, tail2 = tail[len(".content[") :].partition("]")
        if tail2 != "" or not sep2 or not index2_s.isdigit():
            return None
        index2 = int(index2_s)
        content = item.get("content")
        if not isinstance(content, list) or index2 >= len(content):
            return None
        entry = content[index2]
        if not isinstance(entry, dict):
            return None
        value = entry.get("text")
        return value if isinstance(value, str) else None
    if location.startswith("$.messages["):
        rest = location[len("$.messages[") :]
        index_s, sep, tail = rest.partition("]")
        if tail != "" or not sep or not index_s.isdigit():
            return None
        index = int(index_s)
        messages = payload.get("messages")
        if not isinstance(messages, list) or index >= len(messages):
            return None
        message = messages[index]
        if not isinstance(message, dict):
            return None
        value = message.get("content")
        return value if isinstance(value, str) else None
    return None


def _refusal(
    namespace: GraphNamespace,
    outcome: GraphOutcome,
    conflicts: tuple[GraphLimitation, ...],
    request_count: int,
    limitations: tuple[Limitation, ...],
    documents_inspected: int = 0,
    source_bytes_inspected: int = 0,
) -> GraphSnapshot:
    # Total emitted fixed diagnostics (fixed reasons + copied
    # observation/global limitations) are bounded by
    # ``max_diagnostics`` at every public refusal: overflow is ONE
    # fixed ``DIAGNOSTICS_FULL`` refusal, never unbounded copied
    # reasons (no silent truncation, no governance loss).
    if len(conflicts) + len(limitations) > namespace.bounds.max_diagnostics:
        return GraphSnapshot(
            namespace=namespace,
            outcome=GraphOutcome.OVER_BOUND,
            conflicts=(GraphLimitation.DIAGNOSTICS_FULL,),
            request_count=request_count,
            documents_inspected=documents_inspected,
            source_bytes_inspected=source_bytes_inspected,
        )
    return GraphSnapshot(
        namespace=namespace,
        outcome=outcome,
        conflicts=conflicts,
        request_count=request_count,
        observation_limitations=limitations,
        documents_inspected=documents_inspected,
        source_bytes_inspected=source_bytes_inspected,
    )


def _resolve_member(
    member: NormalizedPath,
    context: PathContext | None,
    workspace: str,
    max_path_bytes: int,
) -> str | None:
    """The member's workspace-relative path, or ``None`` (unattributed).

    A member already normalized under the request's own context keeps
    that result.  A context-less request whose member is unproven ONLY
    for lack of an evidenced workspace (UNPROVEN_CWD / UNKNOWN_WORKSPACE)
    is re-resolved lexically against the derived root workspace; any
    other typed refusal stands.
    """
    if member.normalized is not None:
        return member.normalized
    if context is not None:
        return None
    if member.limitation not in (
        Limitation.UNPROVEN_CWD,
        Limitation.UNKNOWN_WORKSPACE,
    ):
        return None
    recheck = normalize_read_path(
        member.raw,
        PathContext(workspace=workspace, workdir=None),
        max_path_bytes,
    )
    return recheck.normalized


def _occurrence(
    request_index: int,
    carrier_location: str,
    piece_index: int,
    span: Any,
) -> SourceOccurrence:
    return SourceOccurrence(
        request_index=request_index,
        carrier_location=carrier_location,
        piece_index=piece_index,
        span=span,
    )


def _retain(
    documents: dict[str, SourceDocument],
    contents: dict[str, str],
    namespace: GraphNamespace,
    path: str,
    content: str,
    digest: str,
    kind: SourceKind,
    occurrences: tuple[SourceOccurrence, ...],
) -> SourceDocument:
    """Retain one acquired source under its path (dedup/conflict law)."""
    if path not in documents:
        doc = SourceDocument(
            path=path,
            scoped_key=namespace.scoped_key,
            digest=digest,
            byte_length=len(content.encode("utf-8")),
            char_length=len(content),
            status=(NodeStatus.ACQUIRED_EMPTY if content == "" else NodeStatus.ACQUIRED),
            kind=kind,
            occurrences=occurrences,
        )
        documents[path] = doc
        contents[path] = content
        return doc
    existing = documents[path]
    merged_occurrences = tuple(dict.fromkeys(existing.occurrences + occurrences))
    if existing.status is NodeStatus.VERSION_CONFLICT or existing.digest != digest:
        doc = SourceDocument(
            path=path,
            scoped_key=namespace.scoped_key,
            digest=None,
            byte_length=None,
            char_length=None,
            status=NodeStatus.VERSION_CONFLICT,
            kind=None,
            occurrences=merged_occurrences,
        )
        documents[path] = doc
        return doc
    doc = existing.model_copy(update={"occurrences": merged_occurrences})
    documents[path] = doc
    return doc


def _scan(
    text: str,
    referring_path: str | None,
    namespace: GraphNamespace,
    referring_digest: str | None,
    bounds: GraphBounds,
) -> ReferenceScan:
    return scan_references(
        text,
        referring_path=referring_path,
        scoped_key=namespace.scoped_key,
        referring_digest=referring_digest,
        bounds=bounds,
    )


class _BundleProof(NamedTuple):
    """One boundaryless multi-member occurrence's WHOLE-BUNDLE proof.

    No per-file hash, byte or edge is invented (a-slice origin law);
    the ordered resolved member paths, the exact whole-bundle digest
    and the original occurrence evidence are the proof signature.
    """

    surface: str  # "read" | "process"
    request_index: int
    call_id: str
    result_location: str
    call_location: str
    ordered_paths: tuple[str, ...]
    digest: str
    content: str
    possible_origins: tuple[str, ...]
    occurrences: tuple[SourceOccurrence, ...]

    def __repr__(self) -> str:
        # Operational representation: fixed surface, counts, locations,
        # spans, digests and public paths stay observable; the private
        # call ID value and the raw source bytes never do.  The internal
        # typed fields are untouched — only their representation is
        # suppressed.
        return (
            f"_BundleProof(surface={self.surface!r}, "
            f"request_index={self.request_index}, call_id='[private]', "
            f"result_location={self.result_location!r}, "
            f"call_location={self.call_location!r}, "
            f"ordered_paths={self.ordered_paths!r}, digest='{self.digest}', "
            f"content='<protected {len(self.content)} chars>', "
            f"possible_origins={self.possible_origins!r}, "
            f"occurrences={self.occurrences!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()


def observe_graph_batch(
    requests: tuple[GraphRequest, ...],
    namespace: GraphNamespace,
    bounds: GraphBounds | None = None,
) -> GraphSnapshot:
    """One bounded batch of decoded requests to one graph snapshot.

    The entry takes exactly one namespace (mixed-namespace batches are
    structurally impossible; a record from another scope is a defensive
    typed refusal).  ``bounds``, when supplied, must equal the
    namespace's effective bounds (the pre-root key binds them); the 017
    observation pass always runs under the 017 package's own ceilings.
    """
    if bounds is None:
        effective = namespace.bounds
    elif bounds != namespace.bounds:
        raise _fixed("bounds must equal the namespace effective bounds")
    else:
        effective = bounds

    request_count = len(requests)
    if request_count > effective.max_requests:
        return _refusal(
            namespace,
            GraphOutcome.OVER_BOUND,
            (GraphLimitation.BATCH_OVER_BOUND,),
            request_count,
            (),
        )

    # --- 017 observation pass (accepted 017 ceilings, metadata only) ---
    reports = [
        observe_request(request.payload, request.context, None, request.endpoint)
        for request in requests
    ]
    observations_limitations: set[Limitation] = set()
    for report in reports:
        observations_limitations.update(report.roots.conflicts)
        observations_limitations.update(reason for read in report.reads for reason in read.reasons)
        observations_limitations.update(
            reason for proc in report.processes for reason in proc.reasons
        )
        observations_limitations.update(u.limitation for u in report.unpaired)
    ordered_limitations = tuple(sorted(observations_limitations))

    # --- Root / workspace binding ----------------------------------------
    authoritative: list[tuple[int, Any]] = []
    for request_index, report in enumerate(reports):
        for root_occ in report.roots.roots:
            authoritative.append((request_index, root_occ))
    if not authoritative:
        return _refusal(
            namespace,
            GraphOutcome.NO_ROOT,
            (GraphLimitation.NO_ROOT,),
            request_count,
            ordered_limitations,
        )
    identities = {(occ.scope_label, occ.digest) for _, occ in authoritative}
    if len(identities) > 1:
        return _refusal(
            namespace,
            GraphOutcome.ROOT_CONFLICT,
            (GraphLimitation.COMPETING_ROOTS,),
            request_count,
            ordered_limitations,
        )
    scope_label, root_digest = next(iter(identities))
    workspace = validate_workspace(scope_label, effective.max_path_bytes)
    if workspace is None or workspace != scope_label:
        return _refusal(
            namespace,
            GraphOutcome.WORKSPACE_UNPROVEN,
            (GraphLimitation.WORKSPACE_UNPROVEN,),
            request_count,
            ordered_limitations,
        )
    if workspace != namespace.workspace:
        return _refusal(
            namespace,
            GraphOutcome.ROOT_CONFLICT,
            (GraphLimitation.WORKSPACE_MISMATCH,),
            request_count,
            ordered_limitations,
        )
    for request in requests:
        if (
            request.context is not None
            and request.context.workspace is not None
            and request.context.workspace != workspace
        ):
            return _refusal(
                namespace,
                GraphOutcome.ROOT_CONFLICT,
                (GraphLimitation.ROOT_CONTEXT_MISMATCH,),
                request_count,
                ordered_limitations,
            )

    # --- Derived-workspace re-observation ---------------------------------
    # A request whose own context carries no evidenced workspace was
    # observed UNPROVEN; the single evidenced root scope is the
    # derived context it is re-observed under (explicit workdir
    # preserved; explicit-context requests keep their original reports).
    for index, request in enumerate(requests):
        context = request.context
        if context is not None and context.workspace is not None:
            continue
        reports[index] = observe_request(
            request.payload,
            PathContext(
                workspace=workspace,
                workdir=context.workdir if context is not None else None,
            ),
            None,
            request.endpoint,
        )
    # Root law is context-independent; single-source the authoritative
    # occurrences and the observation limitations from the FINAL reports.
    authoritative = []
    observations_limitations = set()
    for request_index, report in enumerate(reports):
        for root_occ in report.roots.roots:
            authoritative.append((request_index, root_occ))
        observations_limitations.update(report.roots.conflicts)
        observations_limitations.update(reason for read in report.reads for reason in read.reasons)
        observations_limitations.update(
            reason for proc in report.processes for reason in proc.reasons
        )
        observations_limitations.update(u.limitation for u in report.unpaired)
    ordered_limitations = tuple(sorted(observations_limitations))

    # --- Graph-owned source ledger (before any copy/retention) -----------
    ledger = _SourceLedger(effective)

    def _over_bound() -> GraphSnapshot:
        return _refusal(
            namespace,
            GraphOutcome.OVER_BOUND,
            (ledger.refusal,),  # type: ignore[arg-type]
            request_count,
            ordered_limitations,
            ledger.documents,
        )

    # --- Root node ----------------------------------------------------------
    documents: dict[str, SourceDocument] = {}
    contents: dict[str, str] = {}
    root_content: str | None = None
    for request_index, root_occ in authoritative:
        carrier = _carrier_string(requests[request_index].payload, root_occ.location)
        span = root_occ.content_span
        if carrier is None or span is None or span.end > len(carrier):
            continue
        # Measure and account BEFORE any graph-owned copy: EVERY root
        # occurrence (duplicates included) is an inspected source body
        # (the ledger counts them all); only the first occurrence is
        # copied, and every occurrence's digest is already bound by the
        # single (scope_label, digest) identity established above.
        n_bytes = _utf8_byte_length_range(carrier, span.start, span.end)
        if n_bytes is None:
            return _refusal(
                namespace,
                GraphOutcome.WORKSPACE_UNPROVEN,
                (GraphLimitation.WORKSPACE_UNPROVEN,),
                request_count,
                ordered_limitations,
                ledger.documents,
            )
        ledger.account(n_bytes)
        if ledger.refusal is not None:
            return _over_bound()
        if root_content is None:
            root_content = carrier[span.start : span.end]
            if sha256_hex(root_content) != root_occ.digest:
                # Defensive 017 integrity defect: the root is not
                # acquired (no echo of the content).
                return _refusal(
                    namespace,
                    GraphOutcome.NO_ROOT,
                    (GraphLimitation.WORKSPACE_UNPROVEN,),
                    request_count,
                    ordered_limitations,
                    ledger.documents,
                )
        _retain(
            documents,
            contents,
            namespace,
            ROOT_FILENAME,
            root_content,
            root_occ.digest,
            SourceKind.ROOT,
            (_occurrence(request_index, root_occ.location, 0, span),),
        )
    if root_content is None or ROOT_FILENAME not in documents:
        return _refusal(
            namespace,
            GraphOutcome.NO_ROOT,
            (GraphLimitation.NO_ROOT,),
            request_count,
            ordered_limitations,
        )

    # --- Reference / candidate accounting state -----------------------------
    candidates_total = 0
    candidates_per_document_max = 0
    unresolved: list[UnresolvedOriginCandidate] = []
    read_node_keys: dict[tuple[str, str, str, str | None], str] = {}
    # Single-member seam facts ((request, call, result) occurrence ->
    # (call position, path, digest, full occurrence evidence)),
    # recorded ONLY for single-member acquisitions; the cross-surface
    # seam law compares the FULL proof signature before the reference
    # pass (path/digest alone is not the contracted proof).
    read_facts: dict[tuple[int, str, str], tuple[str, str, str, tuple[SourceOccurrence, ...]]] = {}
    # Boundaryless whole-bundle proof facts: one per positive
    # multi-member occurrence per surface, decided by the cross-surface
    # whole-bundle consistency law after BOTH passes and before any
    # candidate accounting/retention (the SAME physical occurrence with
    # the SAME whole-bundle proof is ONE record, read primary; a
    # MISMATCHED ordered proof acquires no record from that occurrence
    # and refuses ready).
    bundle_proofs: list[_BundleProof] = []

    def _account_candidates(count: int) -> bool:
        """Update candidate totals; return False on the typed refusal."""
        nonlocal candidates_total, candidates_per_document_max
        candidates_total += count
        candidates_per_document_max = max(candidates_per_document_max, count)
        return candidates_total <= effective.max_reference_candidates_total

    # --- Read pass ---------------------------------------------------------
    for request_index, (request, report) in enumerate(zip(requests, reports, strict=True)):
        payload = request.payload
        for read in report.reads:
            if read.content_span is None:
                continue
            carrier = _carrier_string(payload, read.result_location)
            if carrier is None:
                continue
            span = read.content_span
            if span.end > len(carrier):
                continue
            n_bytes = _utf8_byte_length_range(carrier, span.start, span.end)
            if n_bytes is None:
                continue  # 017 already typed MALFORMED_UNICODE
            ledger.account(n_bytes)
            if ledger.refusal is not None:
                return _over_bound()
            if not (
                read.outcome is ReadOutcome.COMPLETE
                and read.removable
                and read.bundle_digest is not None
            ):
                continue  # non-acquiring: inspected and counted only
            content = carrier[span.start : span.end]
            if sha256_hex(content) != read.bundle_digest:
                continue  # defensive integrity defect
            valid_paths = tuple(
                sorted(
                    {
                        path
                        for member in read.requested_members
                        if (
                            path := _resolve_member(
                                member,
                                request.context,
                                workspace,
                                effective.max_path_bytes,
                            )
                        )
                        is not None
                    }
                )
            )
            single = (
                len(read.requested_members) == 1
                and read.distinct_member_count == 1
                and len(read.member_digests) == 1
                and read.member_digests[0] is not None
            )
            if single and valid_paths:
                path = _resolve_member(
                    read.requested_members[0],
                    request.context,
                    workspace,
                    effective.max_path_bytes,
                )
                assert path is not None
                member_digest = read.member_digests[0]
                assert member_digest is not None
                if member_digest != sha256_hex(content):
                    continue  # metadata-only hash: not source proof
                occurrence = _occurrence(request_index, read.result_location, 0, span)
                _retain(
                    documents,
                    contents,
                    namespace,
                    path,
                    content,
                    member_digest,
                    SourceKind.READ,
                    (occurrence,),
                )
                read_facts[(request_index, read.call_id, read.result_location)] = (
                    read.call_location,
                    path,
                    member_digest,
                    (occurrence,),
                )
                read_node_keys[(read.call_id, read.result_location, path, member_digest)] = path
            elif len(read.requested_members) > 1 and valid_paths:
                bundle_digest = read.bundle_digest
                assert bundle_digest is not None
                bundle_proofs.append(
                    _BundleProof(
                        "read",
                        request_index,
                        read.call_id,
                        read.result_location,
                        read.call_location,
                        tuple(
                            path
                            for member in read.requested_members
                            if (
                                path := _resolve_member(
                                    member,
                                    request.context,
                                    workspace,
                                    effective.max_path_bytes,
                                )
                            )
                            is not None
                        ),
                        bundle_digest,
                        content,
                        valid_paths,
                        (_occurrence(request_index, read.result_location, 0, span),),
                    )
                )

    # --- Process pass -------------------------------------------------------
    process_node_keys: dict[tuple[str, str, str, str | None], str] = {}
    proc_facts: dict[tuple[int, str, str], tuple[str, str, str, tuple[SourceOccurrence, ...]]] = {}
    for request_index, (request, report) in enumerate(zip(requests, reports, strict=True)):
        payload = request.payload
        for proc in report.processes:
            if proc.outcome is not ProcessOutcome.COMPLETE:
                continue
            if (
                proc.proven_region_char_length is None
                or proc.bundle_digest is None
                or len(proc.region_piece_spans) != len(proc.pieces)
                or not any(span is not None for span in proc.region_piece_spans)
            ):
                continue  # no earned region: never acquiring
            region_chars = 0
            region_bytes = 0
            pieces: list[tuple[ProcessPiece, Any, int]] = []
            ok = True
            for piece, region_span in zip(proc.pieces, proc.region_piece_spans, strict=True):
                if region_span is None:
                    continue
                carrier = _carrier_string(payload, piece.result_location)
                if carrier is None or region_span.end > len(carrier):
                    ok = False
                    break
                n_bytes = _utf8_byte_length_range(carrier, region_span.start, region_span.end)
                if n_bytes is None:
                    ok = False
                    break
                region_bytes += n_bytes
                region_chars += region_span.end - region_span.start
                pieces.append((piece, region_span, n_bytes))
            if not ok or not pieces:
                continue
            if region_chars != proc.proven_region_char_length:
                continue  # defensive integrity defect
            ledger.account(region_bytes)
            if ledger.refusal is not None:
                return _over_bound()
            region = "".join(
                carrier[region_span.start : region_span.end]
                for piece, region_span, _ in pieces
                if (carrier := _carrier_string(payload, piece.result_location)) is not None
            )
            region_hash = _sha256_hex(region.encode("utf-8"))
            if region_hash != proc.bundle_digest:
                continue  # defensive integrity defect
            valid_paths = tuple(
                sorted(
                    {
                        path
                        for member in proc.requested_members
                        if (
                            path := _resolve_member(
                                member,
                                request.context,
                                workspace,
                                effective.max_path_bytes,
                            )
                        )
                        is not None
                    }
                )
            )
            single = (
                len(proc.requested_members) == 1
                and proc.distinct_member_count == 1
                and len(proc.member_digests) == 1
                and proc.member_digests[0] is not None
            )
            if single and valid_paths:
                path = _resolve_member(
                    proc.requested_members[0],
                    request.context,
                    workspace,
                    effective.max_path_bytes,
                )
                assert path is not None
                member_digest = proc.member_digests[0]
                assert member_digest is not None
                if member_digest != region_hash:
                    continue  # metadata-only hash: not source proof
                occurrences = tuple(
                    _occurrence(
                        request_index,
                        piece.result_location,
                        piece.piece_index,
                        region_span,
                    )
                    for piece, region_span, _ in pieces
                )
                _retain(
                    documents,
                    contents,
                    namespace,
                    path,
                    region,
                    member_digest,
                    SourceKind.PROCESS,
                    occurrences,
                )
                proc_facts[(request_index, proc.exec_call_id, proc.final_result_location or "")] = (
                    proc.exec_call_location,
                    path,
                    member_digest,
                    occurrences,
                )
                process_node_keys[
                    (
                        proc.exec_call_id,
                        proc.final_result_location or "",
                        path,
                        member_digest,
                    )
                ] = path
            elif len(proc.requested_members) > 1 and valid_paths:
                bundle_digest = proc.bundle_digest
                assert bundle_digest is not None
                bundle_proofs.append(
                    _BundleProof(
                        "process",
                        request_index,
                        proc.exec_call_id,
                        proc.final_result_location or "",
                        proc.exec_call_location,
                        tuple(
                            path
                            for member in proc.requested_members
                            if (
                                path := _resolve_member(
                                    member,
                                    request.context,
                                    workspace,
                                    effective.max_path_bytes,
                                )
                            )
                            is not None
                        ),
                        bundle_digest,
                        region,
                        valid_paths,
                        tuple(
                            _occurrence(
                                request_index,
                                piece.result_location,
                                piece.piece_index,
                                region_span,
                            )
                            for piece, region_span, _ in pieces
                        ),
                    )
                )

    # --- Whole-bundle cross-surface proof consistency ----------------------
    # The SAME physical call/result occurrence positive on BOTH surfaces
    # with the SAME whole-bundle proof (actual call position, ordered
    # member paths, exact whole digest, original occurrence evidence) is
    # ONE record (read primary) — counted once, never twice.  A
    # MISMATCHED ordered proof acquires NO source/candidate record from
    # that occurrence and refuses ready (typed conflict).  Unknown
    # member hashes do not erase whole-bundle proof; no per-file
    # split/hash/edge and no admission policy is introduced.
    seam_conflicted = False

    def _prune_conflicting(path: str, occurrences: tuple[SourceOccurrence, ...]) -> None:
        doc = documents.get(path)
        if doc is None:
            return
        identity = {(o.request_index, o.carrier_location, o.piece_index) for o in occurrences}
        kept = tuple(
            o
            for o in doc.occurrences
            if (o.request_index, o.carrier_location, o.piece_index) not in identity
        )
        if not kept:
            documents.pop(path, None)
            contents.pop(path, None)
            return
        documents[path] = doc.model_copy(update={"occurrences": kept})

    bundle_by_key: dict[tuple[int, str, str], list[_BundleProof]] = {}
    for proof in bundle_proofs:
        bundle_by_key.setdefault(
            (proof.request_index, proof.call_id, proof.result_location), []
        ).append(proof)
    fact_keys = set(read_facts) | set(proc_facts)
    surviving_bundles: list[_BundleProof] = []
    for key in sorted(bundle_by_key):
        entries = bundle_by_key[key]
        if key in fact_keys:
            # A positive single-member fact and a positive whole-bundle
            # proof from the SAME call/result occurrence disagree on the
            # ordered members: conflicting positive evidence acquires no
            # source or candidate record from that occurrence (typed
            # conflict), per the same-occurrence consistency law.
            seam_conflicted = True
            for facts in (read_facts, proc_facts):
                fact = facts.get(key)
                if fact is not None:
                    _prune_conflicting(fact[1], fact[3])
            continue  # the bundle record is refused as well
        read_entries = [p for p in entries if p.surface == "read"]
        proc_entries = [p for p in entries if p.surface == "process"]
        if read_entries and proc_entries:
            read_proof = read_entries[0]
            proc_proof = proc_entries[0]
            if (
                read_proof.call_location,
                read_proof.ordered_paths,
                read_proof.digest,
                read_proof.occurrences,
            ) != (
                proc_proof.call_location,
                proc_proof.ordered_paths,
                proc_proof.digest,
                proc_proof.occurrences,
            ):
                seam_conflicted = True
                continue  # both records refused: no source/candidates
            surviving_bundles.extend(read_entries)
        else:
            surviving_bundles.extend(entries)
    for proof in sorted(
        surviving_bundles,
        key=lambda p: (p.request_index, p.result_location, p.surface),
    ):
        scan = _scan(proof.content, None, namespace, None, effective)
        if scan.limitation is not None:
            return _refusal(
                namespace,
                GraphOutcome.OVER_BOUND,
                (scan.limitation,),
                request_count,
                ordered_limitations,
                ledger.documents,
            )
        if not _account_candidates(len(scan.candidates)):
            return _refusal(
                namespace,
                GraphOutcome.OVER_BOUND,
                (GraphLimitation.CANDIDATES_TOTAL_OVER_BOUND,),
                request_count,
                ordered_limitations,
                ledger.documents,
            )
        unresolved.append(
            UnresolvedOriginCandidate(
                scoped_key=namespace.scoped_key,
                bundle_digest=proof.digest,
                possible_origins=proof.possible_origins,
                candidates=scan.candidates,
                request_index=proof.request_index,
                carrier_location=proof.result_location,
            )
        )

    # --- Cross-surface dedup (identical call/result/bytes) ------------------
    for (call_id, result_location, path, digest), process_path in process_node_keys.items():
        read_path = read_node_keys.get((call_id, result_location, path, digest))
        if read_path is None or read_path != process_path:
            continue
        read_node = documents.get(read_path)
        process_node = documents.get(process_path)
        if read_node is None or process_node is None or read_node is process_node:
            continue
        # Identical call/result identity, member and digest: ONE node.
        # The read-surface attribution is primary (kind READ); the
        # process region occurrences are preserved in the union.
        merged = read_node.model_copy(
            update={
                "occurrences": tuple(
                    dict.fromkeys(read_node.occurrences + process_node.occurrences)
                )
            }
        )
        documents[path] = merged
        read_node_keys[(call_id, result_location, path, digest)] = path
        process_node_keys[(call_id, result_location, path, digest)] = path

    # --- Cross-surface seam conflict (same occurrence, differing proof) ------
    # ONE call/result occurrence positive on BOTH surfaces must prove
    # the SAME source with the SAME full proof signature: actual call
    # position, exact original carrier intervals (occurrences keyed by
    # request index, carrier and piece), ordered member, exact digest.
    # Equal bytes in DIFFERENT original intervals are not matching
    # proof.  A mismatch is a typed conflict: the conflicting
    # occurrence is pruned from each fact's node (that occurrence
    # acquires NO source or edge, no good-looking selection), and the
    # snapshot is refused ready with VERSION_CONFLICT.
    for key in read_facts.keys() & proc_facts.keys():
        r_call_location, r_path, r_digest, r_occurrences = read_facts[key]
        p_call_location, p_path, p_digest, p_occurrences = proc_facts[key]
        if (
            r_call_location,
            r_path,
            r_digest,
            r_occurrences,
        ) != (p_call_location, p_path, p_digest, p_occurrences):
            seam_conflicted = True
            _prune_conflicting(r_path, r_occurrences)
            _prune_conflicting(p_path, p_occurrences)

    # --- Reference pass (acquired documents only) ----------------------------
    refs_by_path: dict[str, tuple[ReferenceCandidate, ...]] = {}
    for path in sorted(documents):
        doc = documents[path]
        if doc.status is not NodeStatus.ACQUIRED:
            continue
        scan = _scan(contents[path], path, namespace, doc.digest, effective)
        if scan.limitation is not None:
            # A whole-document scan refusal (per-document candidate
            # overflow, or a defensive MALFORMED_UNICODE) is a fixed
            # typed OVER_BOUND refusal, never a partial success.
            return _refusal(
                namespace,
                GraphOutcome.OVER_BOUND,
                (scan.limitation,),
                request_count,
                ordered_limitations,
                ledger.documents,
            )
        if not _account_candidates(len(scan.candidates)):
            return _refusal(
                namespace,
                GraphOutcome.OVER_BOUND,
                (GraphLimitation.CANDIDATES_TOTAL_OVER_BOUND,),
                request_count,
                ordered_limitations,
                ledger.documents,
            )
        refs_by_path[path] = scan.candidates

    # --- Closure ---------------------------------------------------------------
    snapshot = build_graph(
        documents=tuple(documents[path] for path in sorted(documents)),
        root_path=ROOT_FILENAME,
        workspace=workspace,
        refs_by_path=refs_by_path,
        namespace=namespace,
        bounds=effective,
    )
    final_conflicts = tuple(sorted(set(snapshot.conflicts)))
    if seam_conflicted and snapshot.outcome is GraphOutcome.COMPLETE:
        # A mismatched positive seam cannot hide under a ready
        # snapshot: typed conflict (the conflicting occurrence has
        # already been pruned: no source, no edge from it).
        snapshot = snapshot.model_copy(update={"outcome": GraphOutcome.VERSION_CONFLICT})
        final_conflicts = tuple(sorted(set(final_conflicts) | {GraphLimitation.VERSION_CONFLICT}))
    # Total emitted fixed diagnostics on the final public snapshot
    # (graph conflicts + observation/global limitations) are bounded
    # by ``max_diagnostics``: overflow is ONE fixed
    # ``DIAGNOSTICS_FULL`` refusal, never unbounded copied reasons.
    if len(final_conflicts) + len(ordered_limitations) > effective.max_diagnostics:
        return _refusal(
            namespace,
            GraphOutcome.OVER_BOUND,
            (GraphLimitation.DIAGNOSTICS_FULL,),
            request_count,
            (),
            ledger.documents,
            ledger.total_bytes,
        )
    return snapshot.model_copy(
        update={
            "request_count": request_count,
            "observation_limitations": ordered_limitations,
            "unresolved_origins": tuple(
                sorted(
                    unresolved,
                    key=lambda item: (item.request_index, item.carrier_location),
                )
            ),
            "conflicts": final_conflicts,
            "candidates_total": candidates_total,
            "candidates_per_document_max": candidates_per_document_max,
            "documents_inspected": ledger.documents,
            "source_bytes_inspected": ledger.total_bytes,
        }
    )


def observe_graph(
    payload: dict[str, Any],
    namespace: GraphNamespace,
    *,
    endpoint: str = ENDPOINT_RESPONSES,
    context: PathContext | None = None,
    bounds: GraphBounds | None = None,
) -> GraphSnapshot:
    """Single-request convenience delegate for one decoded payload.

    The endpoint is explicit (default ``responses``); the 017 law never
    infers root authority from an unvalidated selection.
    """
    request = GraphRequest(payload=payload, endpoint=endpoint, context=context)
    return observe_graph_batch((request,), namespace, bounds)
