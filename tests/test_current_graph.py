"""018-f: original-API current graph closure -- durable
known-synthetic controls over the ONE bounded pure derivation.

``derive_current_graph`` is the single original-API surface under
this order: it takes the ACTUAL 018-d retained state, its ACTUAL
namespace and explicit current-graph/currentness bounds, and
derives the pure current graph over the CURRENT semantic sources
selected from the ACTUAL 018-e per-ownership-group currentness
records, rebuilding root reachability from scratch.  All fixtures
are inline known-synthetic original GraphRequests on BOTH read
endpoints and BOTH admission modes; no S runtime path dependency;
no model, native, client or service facility is started.

Locked law surface covered here (order sections A-I):
  A. withdrawal and return follow the ACTUAL current suppliers
     (a completed empty descendant withdraws outgoing derivations
     while the possessed current originals -- B and C, both with
     useful outgoing evidence -- stay honest; old replay alone
     restores nothing; a genuine descendant restores using the
     SAME already-possessed originals, original witnesses kept);
  B. group-certificate self-bootstrap refusal with a REAL
     self-supporting cycle (AB->C->B, both C and B acquired) that
     the fresh root closure refuses; independent alternates
     preserve a certificate and their withdrawal takes it;
  C. conservative opaque staling by a descendant singleton
     (including the equal-looking case where the new singleton
     bytes equal the old opaque aggregate: the certificate is
     withdrawn, no per-file source is spliced, and the new
     ordinary derivation legitimately keeps the target reachable);
     the equal-digest reversed AB/BA ambiguity supplies nothing;
  D. partitioned proven A|B independence: a changed descendant A
     removes ONLY the old A edges while the old B segment keeps
     supplying its own (whole-proof usable-only filtering would
     fail this);
  E. least AND/OR depth (an ordinary path at depth 2 beats a
     usable certificate at depth 3), max-depth enforced AFTER the
     fixed point, the common-lexical-directory law, and repeated
     operands staying group-owned;
  F. equal incomparable witnesses block (BLOCKED_CONFLICT) while
     every witness stays retained; a child of only one cannot
     resolve; a child of ALL does; unrelated updates never move
     the owner of an unrelated current source;
  G. honest availability states (discovered vs unreachable
     possessed vs blocked ambiguity) in one fixture; empty
     withdraws while pending/truncated/nonzero frames cannot
     (they never become complete); root refresh refused by 018-d
     with the anchor unchanged; root-bearing reads (recorded
     preconditions plus the root-member certificate law); the
     fresh RootAnchor field-shape/value/span/Unicode law (typed
     refusals, exact state, pre-inspection sentinels, coherent
     span containment);
  H. max_requests bounds ORIGINAL API BATCHES, not retained
     occurrences: 130 completed observations across 130 single
     legal batches derive OK with a one-path current source set,
     while a 129-request batch on the unchanged old public batch
     API remains overbound;
  I. the new outer work/diagnostic domains and every inherited
     graph-stage domain at limit and first over (graph-stage work
     charged alongside outer for graph-owned operations; the
     UTF-8 source preflight honors the REMAINING total inspected-
     source allowance with zero-copy early exits), shared 018-e
     plus graph work, foreign/malformed/coherently-unsupported
     actual namespaces, state identity/immutability, private
     operational reprs and no host IO on every public path.
"""

from __future__ import annotations

import builtins
import hashlib
import inspect
import json
import os
import pathlib
import socket
import subprocess
from collections.abc import Callable
from typing import Any

import pytest

from slaif_local_coding.constitution.bundles import current_graph as _current_graph_impl
from slaif_local_coding.constitution.bundles.bundle_admission import (
    observe_bundle_admission_batch,
)
from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionLimitation,
    AdmissionMode,
    AdmissionOutcome,
    _canonical_namespace_fields,
    make_bundle_admission_namespace,
)
from slaif_local_coding.constitution.bundles.causal_history import (
    observe_causal_history,
    register_issuance,
    register_receipt,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
    CausalHistoryLimitation,
    CausalHistoryNamespace,
    CausalHistoryOutcome,
    _canonical_history_fields,
)
from slaif_local_coding.constitution.bundles.current_graph import (
    derive_current_graph,
)
from slaif_local_coding.constitution.bundles.current_graph_models import (
    ROOT_OWNER,
    CurrentGraph,
    CurrentGraphBounds,
    CurrentGraphCertificate,
    CurrentGraphLimitation,
    CurrentGraphNode,
    CurrentGraphOutcome,
    CurrentGraphReason,
    CurrentGraphResult,
    CurrentGraphStatus,
    CurrentGraphSupplierKind,
)
from slaif_local_coding.constitution.bundles.currentness import (
    derive_currentness_overlay,
)
from slaif_local_coding.constitution.bundles.currentness_models import (
    CurrentnessBounds,
    CurrentnessOutcome,
    CurrentnessOverlay,
    CurrentnessStatus,
)
from slaif_local_coding.constitution.bundles.graph_models import (
    CandidateStatus,
    CandidateSyntax,
    GraphBounds,
    GraphLimitation,
)
from slaif_local_coding.constitution.bundles.graph_observation import GraphRequest
from slaif_local_coding.constitution.bundles.observation_models import (
    EMPTY_SOURCE_SHA256,
    CharSpan,
    Limitation,
)
from tests.test_causal_history import (
    ENDPOINTS,
    FINGERPRINT,
    IDENTITY,
    MODES,
    PENDING_BODY,
    WORKSPACE,
    chain_request,
    empty_state,
    make_ns,
    read_request,
    root_item,
    root_request,
)

ROOT_TEXT = "Read `A.md` before changing code."  # 33 ASCII bytes
READ_CMD = "cat A.md"
READ_ARGS = json.dumps({"cmd": READ_CMD})
CANARY = "ZCANARYZ"  # sentinel path token for the privacy controls


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _hex64(value: int) -> str:
    return hashlib.sha256(str(value).encode()).hexdigest()


class Hist:
    """Original-API history driver with graph-bounds support.

    Tracks the EXACT (state, revision) pair over ONE namespace and
    the accepted 018-d transitions; refusals and replays are
    asserted at the call site through the raw transition, never
    through this helper.  ``graph``/``graph_ok`` run the 018-f
    derivation over the ACTUAL retained state and namespace."""

    def __init__(
        self,
        mode: AdmissionMode,
        endpoint: str,
        graph_bounds: GraphBounds | None = None,
    ) -> None:
        self.mode = mode
        self.endpoint = endpoint
        self.ns = make_ns(mode, graph_bounds=graph_bounds)
        self.state = empty_state(self.ns)
        self.revision = 0
        self._issued: dict[str, tuple[str, str]] = {}

    def boot_root(self, body: str = ROOT_TEXT) -> None:
        self.observe(
            GraphRequest(payload={"input": [root_item(body)]}, endpoint="responses", context=None),
            note="root",
        )
        # The bootstrap earns the ACTUAL anchor only (no read
        # occurrences), bound to the exact envelope source body.
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

    def read(self, cid: str, body: str, cmd: str = READ_CMD, name: str = "exec_command") -> str:
        before = len(self.state.occurrences)
        self.observe(read_request(self.endpoint, cid, body, cmd), note=f"read:{cid}")
        occurrences = self.state.occurrences
        # EXACTLY ONE new completed read occurrence for this request,
        # bound to the ACTUAL original request/issuance facts BEFORE
        # any graph oracle may run.
        assert len(occurrences) == before + 1, "exactly one new occurrence"
        occurrence = occurrences[-1]
        assert occurrence.call_id == cid
        assert occurrence.endpoint == self.endpoint
        assert occurrence.tool_name == name
        if cid in self._issued:
            fingerprint, issued_name = self._issued[cid]
            # issued call/result fingerprint match: the retained
            # canonical argument fingerprint and tool name equal the
            # ACTUAL retained issuance binding (raw args are never
            # retained; the fingerprint is the binding fact).
            assert occurrence.argument_fingerprint == fingerprint
            assert occurrence.tool_name == issued_name
            assert occurrence.anchored is True
        proof = occurrence.proof
        assert proof.endpoint == self.endpoint
        # exact original source bytes/digest/length preconditions
        assert proof.source_text == body
        assert proof.source_digest == _sha(body)
        assert proof.source_byte_length == len(body.encode("utf-8"))
        assert proof.source_char_length == len(body)
        # simple single-cat commands: the requested members are the
        # exact command operands (partitioned commands assert their
        # segment facts explicitly at the call site).
        if "&&" not in cmd and cmd.startswith("cat "):
            assert tuple(m.normalized for m in proof.requested_members) == tuple(cmd.split()[1:])
        return occurrence.occurrence_id

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
        issued = next(i for i in self.state.issuances if i.call_id == cid)
        self._issued[cid] = (issued.argument_fingerprint, issued.tool_name)

    def replay(self, request: GraphRequest) -> None:
        """The EXACT original request replays as a pure no-op."""
        transition = observe_causal_history((request,), self.ns, self.state, self.revision)
        assert transition.outcome is CausalHistoryOutcome.REPLAYED, (
            transition.outcome,
            transition.diagnostics,
        )
        assert transition.state is self.state

    def graph(
        self,
        bounds: CurrentGraphBounds | None = None,
        currentness_bounds: CurrentnessBounds | None = None,
    ) -> CurrentGraphResult:
        return derive_current_graph(self.state, self.ns, bounds, currentness_bounds)

    def graph_ok(
        self,
        bounds: CurrentGraphBounds | None = None,
        currentness_bounds: CurrentnessBounds | None = None,
    ) -> CurrentGraph:
        result = self.graph(bounds, currentness_bounds)
        assert result.outcome is CurrentGraphOutcome.OK, (result.outcome, result.diagnostics)
        assert result.state is self.state
        assert result.overlay is not None
        return result.overlay


def node(graph: CurrentGraph, path: str) -> CurrentGraphNode:
    for candidate in graph.nodes:
        if candidate.path == path:
            return candidate
    raise AssertionError(f"node {path} is not represented")


def node_paths(graph: CurrentGraph) -> set[str]:
    return {candidate.path for candidate in graph.nodes}


def edges_from(graph: CurrentGraph, source: str) -> set[str]:
    return {edge.target for edge in graph.edges if edge.source == source}


def cert_for_members(
    graph: CurrentGraph, members: tuple[str, ...]
) -> CurrentGraphCertificate | None:
    for cert in graph.certificates:
        if cert.members == members:
            return cert
    return None


def overlay_of(h: Hist) -> CurrentnessOverlay:
    """The ACTUAL 018-e currentness overlay over the same state (a
    charged precondition pinning the per-group path facts the graph
    selection consumes)."""
    result = derive_currentness_overlay(h.state, h.ns)
    assert result.outcome is CurrentnessOutcome.OK, (result.outcome, result.diagnostics)
    assert result.overlay is not None
    return result.overlay


def path_status(overlay: CurrentnessOverlay, path: str) -> CurrentnessStatus:
    for record in overlay.paths:
        if record.path == path:
            return record.status
    raise AssertionError(f"path {path} is not represented")


def assert_refused(
    result: CurrentGraphResult,
    state: Any,
    outcome: CurrentGraphOutcome,
    limitation: CurrentGraphLimitation,
) -> None:
    """A fixed typed whole-result refusal over the EXACT input
    state: no partial graph, one closed reason."""
    assert result.outcome is outcome, (result.outcome, result.diagnostics)
    assert result.diagnostics == (limitation,), result.diagnostics
    assert result.state is state
    assert result.overlay is None


class _SentinelStr(str):
    """Counting stand-in for a retained source region: the preflight
    law must refuse BEFORE any character inspection or owned
    encode copy, which these counters prove."""

    getitems = 0
    encodes = 0

    def __getitem__(self, index: int | slice[Any, Any, Any]) -> str:  # type: ignore[override]
        _SentinelStr.getitems += 1
        return str.__getitem__(self, index)

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        _SentinelStr.encodes += 1
        return str.encode(self, encoding, errors)

    @classmethod
    def reset(cls) -> None:
        cls.getitems = 0
        cls.encodes = 0


def forge(anchor: Any, **overrides: Any) -> Any:
    """A corrupted COPY of the retained anchor (full field dict,
    unvalidated model_construct -- construction is not
    authentication)."""
    values = dict(anchor.__dict__)
    values.update(overrides)
    return anchor.model_construct(**values)


def _coherent_rekeyed_ns(
    ns: CausalHistoryNamespace, updates: dict[str, str | None]
) -> CausalHistoryNamespace:
    """A coherent DIRECT-constructed causal-history scope carrying
    the ACTUAL updated fields: every real field copied, the named
    fields replaced, and the FULL key chain recomputed from the
    actual fields (admission namespace key, admission scoped key,
    history key, state scoped key).  The real constructor
    revalidates the whole recomputation, so a stale key or any
    shape defect would raise at construction."""
    fields: dict[str, object] = {
        name: getattr(ns, name) for name in CausalHistoryNamespace.model_fields
    }
    fields.update(updates)
    admission_canonical = {
        name: fields[name] for name in inspect.signature(_canonical_namespace_fields).parameters
    }
    admission_canonical["mode"] = str(ns.mode)
    admission_key = hashlib.sha256(
        _canonical_namespace_fields(**admission_canonical)  # type: ignore[arg-type]
    ).hexdigest()
    scoped_key = hashlib.sha256(
        (admission_key + "\0" + str(fields["workspace"])).encode()
    ).hexdigest()
    # The admission keys land in the field set BEFORE the history
    # canonical is read: for a changed base version the history key
    # depends on the RECOMPUTED admission key pair.
    fields["admission_namespace_key"] = admission_key
    fields["admission_scoped_key"] = scoped_key
    history_canonical = {
        name: fields[name] for name in inspect.signature(_canonical_history_fields).parameters
    }
    history_canonical["mode"] = str(ns.mode)
    history_key = hashlib.sha256(
        _canonical_history_fields(**history_canonical)  # type: ignore[arg-type]
    ).hexdigest()
    fields["history_key"] = history_key
    fields["state_scoped_key"] = hashlib.sha256(
        (history_key + "\0" + str(fields["workspace"])).encode()
    ).hexdigest()
    return CausalHistoryNamespace(**fields)  # type: ignore[arg-type]


def _frame_request(endpoint: str, cid: str, frame_text: str, cmd: str = READ_CMD) -> GraphRequest:
    """One endpoint-aware original request carrying a raw exec
    frame (nonzero exit or truncated output -- known-synthetic
    non-acquiring shapes)."""
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


def _graph_content(graph: CurrentGraph) -> dict[str, object]:
    """The derivation-content fields of one graph (everything the
    fixed-point emits; the revision field tracks the input state
    and is asserted separately where it may advance)."""
    dump = graph.model_dump()
    return {
        key: dump[key]
        for key in (
            "suppliers",
            "nodes",
            "edges",
            "certificates",
            "candidates",
            "unreachable_current_paths",
            "emitted_reasons",
        )
    }


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_a_withdrawal_and_restoration(mode: AdmissionMode, endpoint: str) -> None:
    """A: Root->Start; Start-v1->B; B->C; C->E.  A descendant
    COMPLETE-EMPTY Start-v2 withdraws B/C/E's outgoing derivations
    while BOTH possessed current originals stay honest (B and C
    both listed unreachable); the EXACT old Start-v1 replay is a
    no-op that restores nothing; a genuinely descendant Start-v3
    restores the edges using the SAME already-possessed B/C
    originals (no new downstream acquisition; original witnesses
    kept)."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `Start.md` first.")
    start1 = h.read("c-start1", "See `B.md`.", cmd="cat Start.md")
    b_occ = h.read("c-b", "See `C.md`.", cmd="cat B.md")
    c_occ = h.read("c-c", "See `E.md`.", cmd="cat C.md")
    g = h.graph_ok()
    assert node(g, "Start.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "Start.md").depth == 1
    assert node(g, "B.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "B.md").witnesses == (b_occ,)
    assert node(g, "B.md").depth == 2
    assert node(g, "C.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "C.md").witnesses == (c_occ,)
    assert node(g, "C.md").depth == 3
    assert node(g, "E.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "E.md").depth == 4
    assert edges_from(g, "AGENTS.md") == {"Start.md"}
    assert edges_from(g, "Start.md") == {"B.md"}
    assert edges_from(g, "B.md") == {"C.md"}
    assert edges_from(g, "C.md") == {"E.md"}
    assert g.unreachable_current_paths == ()

    # A completed EMPTY descendant withdraws Start's outgoing
    # derivations; BOTH possessed current originals (B and C) stay
    # honest and the never-possessed E leaves the derivation.
    h.issue("c-start2", (start1, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat Start.md"}))
    start2 = h.read("c-start2", "", cmd="cat Start.md")
    g2 = h.graph_ok()
    assert node(g2, "Start.md").status is CurrentGraphStatus.CURRENT_EMPTY
    assert node(g2, "Start.md").digest == EMPTY_SOURCE_SHA256
    paths2 = node_paths(g2)
    assert "B.md" not in paths2 and "C.md" not in paths2 and "E.md" not in paths2
    assert g2.unreachable_current_paths == ("B.md", "C.md")
    assert edges_from(g2, "AGENTS.md") == {"Start.md"}
    assert not any(edge.source in ("B.md", "C.md") for edge in g2.edges)

    occurrences_before = len(h.state.occurrences)
    # The EXACT original Start-v1 request replays as a pure no-op
    # and restores nothing: old replay alone never re-derives.
    h.replay(read_request(endpoint, "c-start1", "See `B.md`.", cmd="cat Start.md"))
    g2b = h.graph_ok()
    assert g2b.model_dump() == g2.model_dump()

    # A genuinely descendant Start-v3 (the equal old bytes anchored
    # under v2) restores reachability using the SAME already-
    # possessed B/C originals: B and C keep their ORIGINAL
    # witnesses.
    h.issue("c-start3", (start2, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat Start.md"}))
    h.read("c-start3", "See `B.md`.", cmd="cat Start.md")
    g3 = h.graph_ok()
    assert node(g3, "Start.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g3, "B.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g3, "B.md").witnesses == (b_occ,)
    assert node(g3, "C.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g3, "C.md").witnesses == (c_occ,)
    assert node(g3, "C.md").depth == 3
    assert node(g3, "E.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert edges_from(g3, "Start.md") == {"B.md"}
    assert edges_from(g3, "B.md") == {"C.md"}
    assert edges_from(g3, "C.md") == {"E.md"}
    assert g3.unreachable_current_paths == ()
    # No new downstream acquisition: exactly ONE new occurrence
    # exists (the restoring Start-v3 read itself); B and C keep
    # their ORIGINAL occurrences (witnesses asserted above).
    assert len(h.state.occurrences) == occurrences_before + 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_b_certificate_self_bootstrap_and_alternate(mode: AdmissionMode, endpoint: str) -> None:
    """B: Root->Start and Root->D (D initially unpossessed);
    Start-v1 independently reaches A/B; the opaque AB group targets
    C; C is ACQUIRED and references B, so the fixture carries a
    REAL self-supporting cycle AB->C->B that only the certificate
    could feed.  Start-v2 reaching only A drops B and C with the
    certificate (NO self-bootstrap through the cycle); the
    independent Root->D->B alternate preserves the certificate;
    withdrawing D (completed empty) takes it with the alternate."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `Start.md` and `D.md` first.")
    start1 = h.read("c-start1", "Read `A.md` and `B.md`.", cmd="cat Start.md")
    h.read("c-ab", "See `C.md` here.\n", cmd="cat A.md B.md")
    c_occ = h.read("c-c", "See `B.md` back.\n", cmd="cat C.md")
    g = h.graph_ok()
    # Phase 1: A/B discovered via Start; C possessed and CURRENT at
    # the group depth 1 + max(depth A, depth B) = 3; the acquired
    # C->B ordinary edge exists but C's reachability itself flows
    # from the usable certificate.
    assert node(g, "A.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "B.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "D.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "C.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "C.md").witnesses == (c_occ,)
    assert node(g, "C.md").depth == 3
    assert "B.md" in edges_from(g, "C.md")
    cert = cert_for_members(g, ("A.md", "B.md"))
    assert cert is not None
    assert cert.usable is True
    assert cert.resolved_target == "C.md"
    assert cert.depth == 3
    assert cert.reasons == ()
    assert cert.suppliers == ("A.md", "B.md")
    assert cert.possible_origins == ("A.md", "B.md")
    assert g.unreachable_current_paths == ()

    # Phase 2: Start-v2 reaches only A.  B's only remaining route
    # would be the self-supporting AB->C->B cycle, which the fresh
    # root closure refuses: B and C leave the derivation (no C->B
    # edge from an unreached source) and the certificate is
    # retained as unusable evidence.
    h.issue("c-start2", (start1, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat Start.md"}))
    h.read("c-start2", "Read `A.md`.", cmd="cat Start.md")
    g2 = h.graph_ok()
    paths2 = node_paths(g2)
    assert "B.md" not in paths2 and "C.md" not in paths2
    assert "A.md" in paths2 and "D.md" in paths2
    assert not any(edge.source == "C.md" for edge in g2.edges)
    cert2 = cert_for_members(g2, ("A.md", "B.md"))
    assert cert2 is not None and cert2.usable is False
    assert CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE in cert2.reasons
    # The common-directory agreement is still verified as evidence
    # (a disagreement would be a corrupted-state refusal), but ONLY
    # usability joins a target: C.md was never joined above.
    assert cert2.resolved_target == "C.md"
    assert cert2.depth is None
    # C is possessed and current but unreachable: honest.
    assert g2.unreachable_current_paths == ("C.md",)

    # Phase 3: the INDEPENDENT alternate Root->D->B (D possessed,
    # referencing B) preserves the certificate: B re-enters through
    # D, never through the certificate, and the acquired C joins
    # again with its original witness and its own C->B edge.
    h.read("c-d", "See `B.md`.", cmd="cat D.md")
    g3 = h.graph_ok()
    assert node(g3, "D.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g3, "B.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g3, "B.md").depth == 2
    assert edges_from(g3, "D.md") == {"B.md"}
    assert node(g3, "C.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g3, "C.md").witnesses == (c_occ,)
    assert "B.md" in edges_from(g3, "C.md")
    cert3 = cert_for_members(g3, ("A.md", "B.md"))
    assert cert3 is not None and cert3.usable is True
    assert cert3.resolved_target == "C.md"
    assert g3.unreachable_current_paths == ()

    # Phase 4: withdrawing the alternate (completed empty D)
    # removes B again; the cycle CANNOT bootstrap the certificate
    # (the acquired C would only be reachable through the very
    # certificate it supports).
    d_occ = h.state.occurrences[-1].occurrence_id
    h.issue("c-d2", (d_occ, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat D.md"}))
    h.read("c-d2", "", cmd="cat D.md")
    g4 = h.graph_ok()
    assert node(g4, "D.md").status is CurrentGraphStatus.CURRENT_EMPTY
    paths4 = node_paths(g4)
    assert "B.md" not in paths4 and "C.md" not in paths4
    cert4 = cert_for_members(g4, ("A.md", "B.md"))
    assert cert4 is not None and cert4.usable is False
    assert CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE in cert4.reasons
    assert g4.unreachable_current_paths == ("C.md",)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_descendant_singleton_stales_opaque_group(mode: AdmissionMode, endpoint: str) -> None:
    """C: A/B independently eligible under the root; the opaque AB
    group targets C.  A descendant singleton A stales the opaque AB
    group conservatively (its unattributed bytes are never assumed
    to match A's new bytes) and withdraws the certificate; the
    EXACT old AB request replay does not restore it; a genuine
    descendant NEW AB is current again and its certificate
    restores the target.  The untouched B member keeps its
    current-opaque evidence and NO spliced per-file source is ever
    invented for it."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md` first.")
    ab = h.read("c-ab", "About `C.md`.\n", cmd="cat A.md B.md")
    g = h.graph_ok()
    assert node(g, "A.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "B.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    cert = cert_for_members(g, ("A.md", "B.md"))
    assert cert is not None and cert.usable is True
    assert node(g, "C.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED

    # A descendant singleton A (anchored under the AB occurrence)
    # stales the opaque group even though the group cannot know
    # A's new bytes.
    h.issue("c-a", (ab, CAUSAL_ROOT_FACT))
    h.read("c-a", "A content.\n", cmd="cat A.md")
    g2 = h.graph_ok()
    assert cert_for_members(g2, ("A.md", "B.md")) is None
    assert "C.md" not in node_paths(g2)
    assert node(g2, "A.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g2, "A.md").digest == _sha("A content.\n")
    # B keeps its untouched current-opaque state; no per-file
    # source supplier is spliced out of the aggregate.
    assert node(g2, "B.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert all(
        supplier.path != "B.md"
        for supplier in g2.suppliers
        if supplier.kind is CurrentGraphSupplierKind.SOURCE
    )

    # The EXACT original AB request replays as a pure no-op: the
    # staled group does not revive and no certificate returns.
    h.replay(read_request(endpoint, "c-ab", "About `C.md`.\n", cmd="cat A.md B.md"))
    g2b = h.graph_ok()
    assert cert_for_members(g2b, ("A.md", "B.md")) is None
    assert "C.md" not in node_paths(g2b)

    # A genuine descendant NEW AB (anchored under the singleton) is
    # current again and its certificate restores the target.
    a_occ = h.state.occurrences[-1].occurrence_id
    h.issue("c-ab2", (a_occ, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat A.md B.md"}))
    h.read("c-ab2", "About `C.md` again.\n", cmd="cat A.md B.md")
    g3 = h.graph_ok()
    cert3 = cert_for_members(g3, ("A.md", "B.md"))
    assert cert3 is not None and cert3.usable is True
    assert cert3.resolved_target == "C.md"
    assert node(g3, "C.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_equal_looking_singleton_stales_opaque_group(mode: AdmissionMode, endpoint: str) -> None:
    """C (equal-looking): the new singleton A carries EXACTLY the
    old opaque AB aggregate bytes.  Ownership still cannot be
    attributed, so the old group is staled and its certificate
    withdrawn (no fabricated B source, no root-text assumption) --
    while the new singleton's OWN ordinary A->C reference
    legitimately keeps C reachable through a fresh derivation.  An
    exact old AB replay restores nothing."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md` first.")
    ab_body = "About `C.md`.\n"
    ab = h.read("c-ab", ab_body, cmd="cat A.md B.md")
    g = h.graph_ok()
    cert = cert_for_members(g, ("A.md", "B.md"))
    assert cert is not None and cert.usable is True
    assert node(g, "C.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED

    # The descendant singleton reads the SAME bytes as the whole
    # opaque aggregate.
    h.issue("c-a", (ab, CAUSAL_ROOT_FACT))
    a_new = h.read("c-a", ab_body, cmd="cat A.md")
    # 018-e precondition: the old boundaryless group is STALE (its
    # unattributed ownership can never be proven equal to A's new
    # proven bytes); the new singleton group is current known.
    ov = overlay_of(h)
    old_group = next(
        record for record in ov.groups if record.occurrence_id == ab and record.group_index == 0
    )
    new_group = next(
        record for record in ov.groups if record.occurrence_id == a_new and record.group_index == 0
    )
    assert old_group.group_status not in (
        CurrentnessStatus.CURRENT_OPAQUE,
        CurrentnessStatus.CURRENT_KNOWN,
    )
    assert new_group.group_status is CurrentnessStatus.CURRENT_KNOWN
    assert path_status(ov, "B.md") is not CurrentnessStatus.CURRENT_KNOWN

    g2 = h.graph_ok()
    # The old certificate is withdrawn (the staled group is
    # excluded BEFORE scanning: no certificate at all).
    assert cert_for_members(g2, ("A.md", "B.md")) is None
    assert g2.certificates == ()
    # The new singleton A is current known at its exact digest.
    assert node(g2, "A.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g2, "A.md").digest == _sha(ab_body)
    # The NEW ordinary A->C derivation legitimately keeps C
    # reachable (an independent fresh derivation -- not the old
    # group's).
    assert node(g2, "C.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert "C.md" in edges_from(g2, "A.md")
    # B is still honestly unavailable: the old group is staled and
    # no per-file source is fabricated for it.
    assert node(g2, "B.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g2, "B.md").digest is None
    assert all(
        supplier.path != "B.md"
        for supplier in g2.suppliers
        if supplier.kind is CurrentGraphSupplierKind.SOURCE
    )
    assert all(
        "B.md" not in supplier.members
        for supplier in g2.suppliers
        if supplier.kind is CurrentGraphSupplierKind.GROUP
    )

    # The EXACT original AB request replays as a pure no-op:
    # nothing is restored.
    h.replay(read_request(endpoint, "c-ab", ab_body, cmd="cat A.md B.md"))
    g2b = h.graph_ok()
    assert cert_for_members(g2b, ("A.md", "B.md")) is None
    assert node(g2b, "C.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert "C.md" in edges_from(g2b, "A.md")
    assert node(g2b, "B.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_c_reversed_equal_digest_ambiguity_supplies_nothing(
    mode: AdmissionMode, endpoint: str
) -> None:
    """C: equal-digest reversed AB/BA -- two unissued boundaryless
    groups with EQUAL aggregate bytes but reversed ordered members
    are distinct opaque identities whose conflicting ownership
    ambiguity blocks both paths; BOTH groups are excluded before
    scanning, so no certificate or candidate is derived from them
    (the original proofs stay in the input state with their equal
    aggregate digests and reversed shapes) and no spliced
    pseudo-singleton source is invented."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md` first.")
    h.read("c-ab", "See `C.md` here.\n", cmd="cat A.md B.md")
    h.read("c-ba", "See `C.md` here.\n", cmd="cat B.md A.md")
    # 018-e precondition: both paths are ownership-ambiguous (two
    # conflicting unattributed groups).  The two boundaryless
    # segments carry EQUAL aggregate bytes (same digest) yet the
    # versioned opaque identities are DISTINCT (the ordered member
    # shape is the identity; the digest is never one).
    ov = overlay_of(h)
    assert path_status(ov, "A.md") is CurrentnessStatus.OWNERSHIP_AMBIGUITY
    assert path_status(ov, "B.md") is CurrentnessStatus.OWNERSHIP_AMBIGUITY
    group_records = sorted(ov.groups, key=lambda r: r.occurrence_id)
    assert len(group_records) == 2
    assert len({record.opaque_identity for record in group_records}) == 2
    boundaryless_digests = {
        segment.digest
        for occurrence in h.state.occurrences
        for segment in occurrence.proof.segments
        if segment.member_digest is None
    }
    assert len(boundaryless_digests) == 1
    g = h.graph_ok()
    assert node(g, "A.md").status is CurrentGraphStatus.BLOCKED_AMBIGUITY
    assert node(g, "B.md").status is CurrentGraphStatus.BLOCKED_AMBIGUITY
    # An ambiguous group supplies NOTHING: no certificate, no
    # candidate target joins, no source; the only supplier is the
    # root anchor.
    assert g.certificates == ()
    assert "C.md" not in node_paths(g)
    assert all(supplier.kind is CurrentGraphSupplierKind.ROOT for supplier in g.suppliers)
    assert g.emitted_reasons == 2


# ---------------------------------------------------------------------------
# D: partitioned proven A|B -- per-member independence
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_partitioned_proof_per_member_independence(mode: AdmissionMode, endpoint: str) -> None:
    """D: one partitioned proven A|B read.  A changed descendant of A
    removes ONLY the old A edges; the old B segment -- inside the SAME
    now-unusable whole proof -- keeps supplying its own edge with its
    ORIGINAL witness (whole-proof usable-only filtering would have
    dropped B with A, and no per-file source is ever spliced out of
    a stale aggregate)."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md` first.")
    seg_a = "From A see `C.md`.\n"
    seg_b = "From B see `D.md`.\n"
    # The 017 partitioned law: the retained source is the EXACT
    # concatenated segment bytes (the proven marker delimiters are
    # not source bytes).
    h.observe(
        read_request(
            endpoint,
            "c-p1",
            seg_a + "MARK\n" + seg_b,
            cmd="cat A.md && echo 'MARK' && cat B.md",
        ),
        note="read:c-p1",
    )
    occurrence = h.state.occurrences[-1]
    p1 = occurrence.occurrence_id
    assert len(h.state.occurrences) == 1
    assert occurrence.call_id == "c-p1"
    assert occurrence.endpoint == endpoint
    proof = occurrence.proof
    assert proof.source_text == seg_a + seg_b
    assert proof.source_digest == _sha(seg_a + seg_b)
    assert proof.source_byte_length == len((seg_a + seg_b).encode("utf-8"))
    segments = proof.segments
    # EXACT partitioned proven preconditions: two proven members with
    # their granted digests, before any graph oracle.
    assert len(segments) == 2
    assert segments[0].member_positions == (0,)
    assert segments[0].member_digest == _sha(seg_a)
    assert segments[0].char_length == len(seg_a)
    assert segments[1].member_positions == (1,)
    assert segments[1].member_digest == _sha(seg_b)
    assert segments[1].char_length == len(seg_b)

    g = h.graph_ok()
    assert node(g, "A.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "A.md").digest == _sha(seg_a)
    assert node(g, "A.md").witnesses == (p1,)
    assert node(g, "A.md").depth == 1
    assert node(g, "B.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "B.md").digest == _sha(seg_b)
    assert node(g, "B.md").witnesses == (p1,)
    assert node(g, "B.md").depth == 1
    assert node(g, "C.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "C.md").depth == 2
    assert node(g, "D.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "D.md").depth == 2
    assert edges_from(g, "A.md") == {"C.md"}
    assert edges_from(g, "B.md") == {"D.md"}
    sources = {
        supplier.path: supplier
        for supplier in g.suppliers
        if supplier.kind is CurrentGraphSupplierKind.SOURCE
    }
    assert set(sources) == {"A.md", "B.md"}
    assert sources["A.md"].digest == _sha(seg_a)
    assert sources["A.md"].witnesses == (p1,)
    assert sources["B.md"].digest == _sha(seg_b)
    assert sources["B.md"].witnesses == (p1,)
    assert g.certificates == ()
    assert g.unreachable_current_paths == ()

    # A changed descendant of A: only the A segment stales; the old
    # B segment of the same (now unusable) whole proof keeps its
    # own edge and its ORIGINAL witness.
    h.issue("c-a2", (p1, CAUSAL_ROOT_FACT))
    a2 = h.read("c-a2", "A changed.\n")
    g2 = h.graph_ok()
    assert node(g2, "A.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g2, "A.md").digest == _sha("A changed.\n")
    assert node(g2, "A.md").witnesses == (a2,)
    assert "C.md" not in node_paths(g2)
    assert not any(edge.source == "A.md" for edge in g2.edges)
    assert node(g2, "B.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g2, "B.md").digest == _sha(seg_b)
    assert node(g2, "B.md").witnesses == (p1,)
    assert node(g2, "D.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g2, "D.md").depth == 2
    assert edges_from(g2, "B.md") == {"D.md"}
    # The surviving B derivation is owned by B's ACTUAL current
    # source (path + digest), never by the stale whole proof.
    b_edge = next(edge for edge in g2.edges if edge.source == "B.md")
    assert b_edge.owner == node(g2, "B.md").owner
    assert b_edge.witnesses == (p1,)
    assert g2.unreachable_current_paths == ()


# ---------------------------------------------------------------------------
# E: least AND/OR depth, max depth after the fixed point, the common
#     lexical directory law, repeated-operand group ownership
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_least_and_or_depth_alternatives_min(mode: AdmissionMode, endpoint: str) -> None:
    """E: surviving alternatives keep BOTH derivations: the ordinary
    root->Start->C path (depth 2) and the usable AB certificate
    (derivation depth 1 + max(depth A, depth B) = 3).  The TARGET's
    least complete depth takes the MIN over alternatives (the
    ordinary route wins), while the certificate keeps its own
    group depth."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `Start.md` and `S.md` first.")
    h.read("c-start", "Read `A.md` and `B.md` and `C.md`.", cmd="cat Start.md")
    h.read("c-ab", "See `C.md` here.\n", cmd="cat A.md B.md")
    g = h.graph_ok()
    assert node(g, "Start.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "S.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "S.md").depth == 1
    assert node(g, "A.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "B.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "C.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    cert = cert_for_members(g, ("A.md", "B.md"))
    assert cert is not None and cert.usable is True
    assert cert.resolved_target == "C.md"
    assert cert.depth == 3
    assert node(g, "C.md").depth == 2
    assert edges_from(g, "AGENTS.md") == {"Start.md", "S.md"}
    assert edges_from(g, "Start.md") == {"A.md", "B.md", "C.md"}


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_max_depth_enforced_after_fixed_point(mode: AdmissionMode, endpoint: str) -> None:
    """E: the effective max_depth is enforced AFTER the joint fixed
    point: a depth-3 chain refuses with the exact graph-stage
    limitation and exact state under max_depth=2, and the SAME
    fixture derives normally under max_depth=3."""
    h2 = Hist(mode, endpoint, graph_bounds=GraphBounds(max_depth=2))
    h2.boot_root("Read `S1.md` first.")
    s1 = h2.read("c-s1", "See `S2.md`.", cmd="cat S1.md")
    h2.issue("c-s2", (s1, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat S2.md"}))
    h2.read("c-s2", "See `S3.md`.", cmd="cat S2.md")
    assert_refused(
        h2.graph(),
        h2.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.GRAPH_DEPTH_OVER_BOUND,
    )

    h3 = Hist(mode, endpoint, graph_bounds=GraphBounds(max_depth=3))
    h3.boot_root("Read `S1.md` first.")
    s1 = h3.read("c-s1", "See `S2.md`.", cmd="cat S1.md")
    h3.issue("c-s2", (s1, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat S2.md"}))
    h3.read("c-s2", "See `S3.md`.", cmd="cat S2.md")
    g = h3.graph_ok()
    assert node(g, "S3.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "S3.md").depth == 3


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_no_common_directory_withholds_certificate(mode: AdmissionMode, endpoint: str) -> None:
    """E: a group certificate is usable only when EVERY possible
    nonroot supplier shares the SAME canonical lexical directory.
    x/A.md and y/B.md do not (convergent references never
    compensate): the target is never joined, and the certificate is
    retained as unresolved evidence with the closed reason and exact
    origin/supplier sets."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `x/A.md` and `y/B.md` first.")
    h.read("c-xy", "See `z/C.md` here.\n", cmd="cat x/A.md y/B.md")
    g = h.graph_ok()
    assert node(g, "x/A.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "y/B.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert "z/C.md" not in node_paths(g)
    cert = cert_for_members(g, ("x/A.md", "y/B.md"))
    assert cert is not None and cert.usable is False
    assert cert.reasons == (CurrentGraphReason.NO_COMMON_DIRECTORY,)
    assert cert.possible_origins == ("x/A.md", "y/B.md")
    assert cert.suppliers == ("x/A.md", "y/B.md")
    assert cert.resolved_target is None
    assert cert.depth is None
    assert g.unreachable_current_paths == ()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_repeated_operand_group_owned(mode: AdmissionMode, endpoint: str) -> None:
    """E: repeated operands (cat A.md A.md) form ONE boundaryless
    group: the certificate is group-owned (never per-file hashing of
    A), the repeated members do not inflate the derivation depth,
    and A is never granted a singleton source from the aggregate."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    h.read("c-aa", "See `C.md`.\n", cmd="cat A.md A.md")
    g = h.graph_ok()
    assert node(g, "A.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "C.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "C.md").depth == 2
    cert = cert_for_members(g, ("A.md", "A.md"))
    assert cert is not None and cert.usable is True
    assert cert.resolved_target == "C.md"
    assert cert.depth == 2
    assert cert.suppliers == ("A.md",)
    assert cert.possible_origins == ("A.md",)
    assert all(supplier.kind is not CurrentGraphSupplierKind.SOURCE for supplier in g.suppliers)
    groups = [s for s in g.suppliers if s.kind is CurrentGraphSupplierKind.GROUP]
    assert len(groups) == 1
    assert groups[0].members == ("A.md", "A.md")
    assert groups[0].path is None
    assert groups[0].digest is None
    assert groups[0].identity is not None
    assert groups[0].group_digest is not None


# ---------------------------------------------------------------------------
# F: conflicting witnesses block; a child of all resolves; unrelated
#     updates never move ownership
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_conflicting_witnesses_block_then_resolve(mode: AdmissionMode, endpoint: str) -> None:
    """F: equal incomparable known A witnesses block A as
    BLOCKED_CONFLICT while EVERY witness stays retained in state; a
    changed child of only ONE witness does not resolve (the other
    frontier witness stays incomparable); a child of ALL witnesses
    does; an unrelated B update never moves A's current ownership."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` and `B.md` first.")
    a1 = h.read("c-a1", "A one.\n")
    a2 = h.read("c-a2", "A two.\n")
    b1 = h.read("c-b1", "B one.\n", cmd="cat B.md")
    g = h.graph_ok()
    assert node(g, "A.md").status is CurrentGraphStatus.BLOCKED_CONFLICT
    assert node(g, "A.md").digest is None
    assert node(g, "A.md").owner is None
    assert node(g, "A.md").witnesses == ()
    assert node(g, "B.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "B.md").digest == _sha("B one.\n")
    assert node(g, "B.md").witnesses == (b1,)
    assert g.emitted_reasons == 1
    # The block is a per-path derivation state, never an erasure:
    # every conflicting original stays retained in the state.
    assert {"c-a1", "c-a2", "c-b1"} <= {o.call_id for o in h.state.occurrences}

    # A changed child of only ONE conflicting witness: the other
    # witness is still on the frozen frontier (incomparable) -- A
    # stays blocked.
    h.issue("c-a3", (a1, CAUSAL_ROOT_FACT))
    a3 = h.read("c-a3", "A three.\n")
    g2 = h.graph_ok()
    assert node(g2, "A.md").status is CurrentGraphStatus.BLOCKED_CONFLICT

    # A child of ALL witnesses resolves A to exactly that content.
    h.issue("c-a4", (a2, a3, CAUSAL_ROOT_FACT))
    a4 = h.read("c-a4", "A four.\n")
    g3 = h.graph_ok()
    a_node3 = node(g3, "A.md")
    assert a_node3.status is CurrentGraphStatus.CURRENT_KNOWN
    assert a_node3.digest == _sha("A four.\n")
    assert a_node3.witnesses == (a4,)
    owner_a = a_node3.owner

    # Unrelated B update: B moves, A's current ownership never does.
    h.issue("c-b2", (b1, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat B.md"}))
    b2 = h.read("c-b2", "B two.\n", cmd="cat B.md")
    g4 = h.graph_ok()
    assert node(g4, "B.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g4, "B.md").digest == _sha("B two.\n")
    assert node(g4, "B.md").witnesses == (b2,)
    assert node(g4, "A.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g4, "A.md").digest == _sha("A four.\n")
    assert node(g4, "A.md").owner == owner_a


# ---------------------------------------------------------------------------
# G: honest availability, non-completing frames, root anchor law
# ---------------------------------------------------------------------------

_TRUNC_WARNING = "Warning: truncated output (original token count: 512)\nTotal output lines: 64\n\n"
TRUNCATED_FRAME = (
    "Chunk ID: 3d4e5f\n"
    "Wall time: 0.6789 seconds\n"
    "Process exited with code 0\n"
    "Original token count: 512\n"
    f"Output:\n{_TRUNC_WARNING}head\ntail\n"
)
NONZERO_FRAME = (
    "Chunk ID: synthetic\n"
    + "Wall time: 0.0000 seconds\n"
    + "Process exited with code 1\n"
    + "Output:\nSynthetic file content.\n"
)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_availability_states_and_non_completing_frames(
    mode: AdmissionMode, endpoint: str
) -> None:
    """G: honest availability in ONE fixture: discovered-unacquired
    (A), blocked ambiguity (C), current (D) and possessed-off-graph
    (B, listed unreachable).  A completed empty withdraws D's
    references; pending/truncated/nonzero frames never complete
    (occurrence count and graph content unchanged); a changed
    nonzero terminal frame for the same call is a typed
    non-acquiring replay with the exact state preserved."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` and `C.md` and `D.md` first.")
    h.read("c-b", "B body.\n", cmd="cat B.md")
    h.read("c-cx", "One.\n", cmd="cat C.md X.md")
    h.read("c-xc", "One.\n", cmd="cat X.md C.md")
    d_occ = h.read("c-d", "See `E.md`.\n", cmd="cat D.md")
    g = h.graph_ok()
    assert node(g, "A.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "A.md").digest is None
    assert node(g, "A.md").owner is None
    assert node(g, "A.md").witnesses == ()
    assert node(g, "A.md").depth == 1
    assert node(g, "C.md").status is CurrentGraphStatus.BLOCKED_AMBIGUITY
    assert node(g, "D.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "D.md").witnesses == (d_occ,)
    assert node(g, "E.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "E.md").depth == 2
    assert edges_from(g, "AGENTS.md") == {"A.md", "C.md", "D.md"}
    assert edges_from(g, "D.md") == {"E.md"}
    # B is possessed but referenced by NO current derivation.
    assert g.unreachable_current_paths == ("B.md",)
    assert g.emitted_reasons == 1
    # An ownership-ambiguous group supplies NOTHING (the same law as
    # the equal-digest reversed AB/BA control): no certificate, no
    # group supplier, no source -- only the root anchor and the
    # possessed singletons supply.  B is possessed (its own proven
    # singleton) but referenced by NO current derivation: a supplier
    # AND unreachable.
    assert all(supplier.kind is not CurrentGraphSupplierKind.GROUP for supplier in g.suppliers)
    assert {
        supplier.path
        for supplier in g.suppliers
        if supplier.kind is CurrentGraphSupplierKind.SOURCE
    } == {"B.md", "D.md"}

    # A completed EMPTY descendant withdraws D's outgoing references.
    h.issue("c-d2", (d_occ, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat D.md"}))
    h.read("c-d2", "", cmd="cat D.md")
    g2 = h.graph_ok()
    assert node(g2, "D.md").status is CurrentGraphStatus.CURRENT_EMPTY
    assert node(g2, "D.md").digest == EMPTY_SOURCE_SHA256
    assert "E.md" not in node_paths(g2)
    assert not any(edge.source == "D.md" for edge in g2.edges)
    assert g2.unreachable_current_paths == ("B.md",)
    content2 = _graph_content(g2)

    # PENDING frame: accepted, never completes (the exact 018-d
    # non-acquiring pending law).
    before = len(h.state.occurrences)
    h.observe(chain_request(endpoint, "g-pend", PENDING_BODY), note="pending")
    assert len(h.state.occurrences) == before
    assert next(r for r in h.state.results if r.call_id == "g-pend").complete is False
    assert _graph_content(h.graph_ok()) == content2

    # TRUNCATED terminal frame: never complete; the honest 017
    # wrapper/process limitations are retained, no occurrence.
    truncated = h.observe(_frame_request(endpoint, "g-trunc", TRUNCATED_FRAME), note="truncated")
    assert truncated is CausalHistoryOutcome.ACCEPTED
    assert len(h.state.occurrences) == before
    assert next(r for r in h.state.results if r.call_id == "g-trunc").complete is False
    assert _graph_content(h.graph_ok()) == content2

    # NONZERO terminal frame: a typed non-acquiring replay with the
    # exact state preserved; no completion claim, no graph change.
    transition = observe_causal_history(
        (_frame_request(endpoint, "g-nonzero", NONZERO_FRAME),),
        h.ns,
        h.state,
        h.revision,
    )
    assert transition.outcome is CausalHistoryOutcome.REPLAYED
    assert transition.diagnostics == (CausalHistoryLimitation.OUTPUT_INCONSISTENT,)
    assert Limitation.NONZERO_EXIT in transition.observation_limitations
    assert transition.state is h.state
    assert len(h.state.occurrences) == before
    assert _graph_content(h.graph_ok()) == content2


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_root_refresh_refused_anchor_unchanged(mode: AdmissionMode, endpoint: str) -> None:
    """G: a second root over an already-anchored scope is still
    refused by the 018-d state machine (root refresh remains
    reserved, not granted); the retained anchor is untouched and
    the derivation is normal over it."""
    h = Hist(mode, endpoint)
    h.boot_root()
    anchor = h.state.root
    assert anchor is not None
    refresh = GraphRequest(
        payload={"input": [root_item("Read `Z.md` instead.")]},
        endpoint="responses",
        context=None,
    )
    transition = observe_causal_history((refresh,), h.ns, h.state, h.revision)
    assert transition.outcome is CausalHistoryOutcome.REFUSED_ROOT_CONFLICT
    assert transition.state is h.state
    assert h.state.root is anchor
    assert anchor.root_text == ROOT_TEXT
    assert anchor.root_digest == _sha(ROOT_TEXT)
    g = h.graph_ok()
    assert node(g, "AGENTS.md").digest == _sha(ROOT_TEXT)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_root_bearing_reads(mode: AdmissionMode, endpoint: str) -> None:
    """G: a read of the root file ALONE competes with the anchor and
    is refused by 018-d; a root-bearing opaque group is observed,
    but its certificate can never attribute the unattributed root
    bytes to the anchor (ROOT_MEMBER_UNATTRIBUTED): no target
    joins, the root node keeps its exact digest, and the GROUP
    supplier retains the full origin evidence."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    solo = observe_causal_history(
        (read_request(endpoint, "c-root-solo", "Root text.\n", cmd="cat AGENTS.md"),),
        h.ns,
        h.state,
        h.revision,
    )
    assert solo.outcome is CausalHistoryOutcome.REFUSED_ROOT_CONFLICT
    assert CausalHistoryLimitation.COMPETING_ROOTS in solo.diagnostics
    assert solo.state is h.state
    assert len(h.state.occurrences) == 0

    h.read("c-rootab", "See `Z.md` here.\n", cmd="cat AGENTS.md A.md")
    assert len(h.state.occurrences) == 1
    g = h.graph_ok()
    assert "Z.md" not in node_paths(g)
    cert = cert_for_members(g, ("AGENTS.md", "A.md"))
    assert cert is not None and cert.usable is False
    assert CurrentGraphReason.ROOT_MEMBER_UNATTRIBUTED in cert.reasons
    assert cert.possible_origins == ("A.md", "AGENTS.md")
    assert cert.suppliers == ("A.md",)
    assert cert.resolved_target == "Z.md"
    assert cert.depth is None
    assert node(g, "A.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    groups = [s for s in g.suppliers if s.kind is CurrentGraphSupplierKind.GROUP]
    assert len(groups) == 1
    assert groups[0].members == ("AGENTS.md", "A.md")
    assert node(g, "AGENTS.md").digest == _sha("Read `A.md` first.")


_G4_CONTENT_START = 51
_G4_CONTENT_END = 84
_G4_LEN = _G4_CONTENT_END - _G4_CONTENT_START


def _g4_case(anchor: Any, **overrides: Any) -> Any:
    return forge(anchor, **overrides)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_root_anchor_field_shape_negatives(mode: AdmissionMode, endpoint: str) -> None:
    """G: EVERY actual RootAnchor field is freshly validated under
    the charged preflight (model_validate(existing_instance) alone
    would accept these forged model_construct copies): wrong shapes
    (non-string source, null location/workspace/content span,
    string/fractional/boolean coordinates, dict envelope span),
    negative or fractional index/length, a negative-content span,
    an envelope that excludes the last source character, and a
    non-encodable (isolated-surrogate) source are all fixed typed
    refusals with the EXACT input state preserved.  The corrupted
    copies are negative controls, never acquisition authority."""
    h = Hist(mode, endpoint)
    h.boot_root()
    anchor = h.state.root
    assert anchor is not None
    surrogate_text = "Read \ud800 A.md before changing code."
    assert len(surrogate_text) == _G4_LEN
    cases: dict[str, dict[str, object]] = {
        "negative_content_span": _g4_case(
            anchor, content_span=CharSpan.model_construct(start=-1, end=_G4_CONTENT_END)
        ),
        "envelope_excludes_last_source_character": _g4_case(
            anchor, envelope_span=CharSpan(start=0, end=_G4_CONTENT_END - 1)
        ),
        "negative_original_request_index": _g4_case(anchor, first_request_index=-1),
        "malformed_unicode_source": _g4_case(anchor, root_text=surrogate_text),
        "nonstring_source": _g4_case(anchor, root_text=7),
        "null_location": _g4_case(anchor, location=None),
        "string_original_request_index": _g4_case(anchor, first_request_index="0"),
        "fractional_original_request_index": _g4_case(anchor, first_request_index=0.5),
        "string_span_start": _g4_case(
            anchor, content_span=CharSpan.model_construct(start="0", end=_G4_CONTENT_END)
        ),
        "fractional_span_coordinates": _g4_case(
            anchor,
            content_span=CharSpan.model_construct(start=0.5, end=_G4_CONTENT_END + 0.5),
        ),
        "boolean_original_request_index": _g4_case(anchor, first_request_index=True),
        "nonhex_digest": _g4_case(anchor, root_digest="z" * 64),
        "fractional_byte_length": _g4_case(anchor, source_byte_length=33.5),
        "boolean_byte_length": _g4_case(anchor, source_byte_length=True),
        "nonstring_workspace": _g4_case(anchor, workspace=7),
        "null_content_span": _g4_case(anchor, content_span=None),
        "dict_envelope_span": _g4_case(anchor, envelope_span={"start": 0, "end": 100}),
        "null_source": _g4_case(anchor, root_text=None),
    }
    for name, forged in cases.items():
        state = h.state.model_copy(update={"root": forged})
        result = derive_current_graph(state, h.ns)
        assert result.outcome is CurrentGraphOutcome.REFUSED_STATE_MALFORMED, (
            name,
            result.outcome,
            result.diagnostics,
        )
        assert result.diagnostics == (CurrentGraphLimitation.ROOT_MALFORMED,), (
            name,
            result.diagnostics,
        )
        assert result.state is state, name
        assert result.overlay is None, name


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_g_root_preflight_sentinels(mode: AdmissionMode, endpoint: str) -> None:
    """G: the anchor byte preflight refuses BEFORE any character
    inspection or owned encode copy.  The coherent 65-ASCII root
    under max_single_source_bytes=64 (content span matching the
    enlarged text, envelope extended to CONTAIN it -- so the
    source-byte cap crossing, not an unrelated span failure, is
    what is reached) touches ZERO characters and ZERO encodes.  The
    coherent 40xe9 root (80 bytes) exits the bounded walk
    mid-region: 0 < touches < 40, still zero encodes."""
    h = Hist(mode, endpoint, graph_bounds=GraphBounds(max_single_source_bytes=64))
    h.boot_root()
    anchor = h.state.root
    assert anchor is not None
    start = anchor.content_span.start
    assert start == _G4_CONTENT_START

    _SentinelStr.reset()
    long_text = _SentinelStr("A" * 65)
    long_anchor = forge(
        anchor,
        root_text=long_text,
        root_digest=_sha("A" * 65),
        source_byte_length=65,
        content_span=CharSpan(start=start, end=start + 65),
        envelope_span=CharSpan(start=0, end=start + 65),
    )
    state = h.state.model_copy(update={"root": long_anchor})
    assert_refused(
        derive_current_graph(state, h.ns),
        state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.GRAPH_SOURCE_BYTES_OVER_BOUND,
    )
    assert _SentinelStr.getitems == 0
    assert _SentinelStr.encodes == 0

    _SentinelStr.reset()
    wide_text = _SentinelStr("\u00e9" * 40)
    wide_anchor = forge(
        anchor,
        root_text=wide_text,
        root_digest=_sha("\u00e9" * 40),
        source_byte_length=80,
        content_span=CharSpan(start=start, end=start + 40),
        envelope_span=CharSpan(start=0, end=start + 40),
    )
    state2 = h.state.model_copy(update={"root": wide_anchor})
    assert_refused(
        derive_current_graph(state2, h.ns),
        state2,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.GRAPH_SOURCE_BYTES_OVER_BOUND,
    )
    assert 0 < _SentinelStr.getitems < 40
    assert _SentinelStr.encodes == 0


# ---------------------------------------------------------------------------
# H: max_requests bounds ORIGINAL API BATCHES, not retained occurrences
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_h_max_requests_bounds_batches_not_retention(mode: AdmissionMode, endpoint: str) -> None:
    """H: 130 completed observations across 130 single legal
    original batches derive OK over a one-path current source set
    (max_requests is NOT reinterpreted as a retained-occurrence
    count); the unchanged old public batch API still refuses one
    129-request batch at the SAME inherited cap."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    for index in range(130):
        h.read(f"c-h{index:03d}", "A stable body.\n")
    assert len(h.state.occurrences) == 130
    g = h.graph_ok()
    a_node = node(g, "A.md")
    assert a_node.status is CurrentGraphStatus.CURRENT_KNOWN
    assert a_node.digest == _sha("A stable body.\n")
    assert a_node.depth == 1
    assert len(a_node.witnesses) == 130
    source = next(s for s in g.suppliers if s.kind is CurrentGraphSupplierKind.SOURCE)
    assert source.path == "A.md"
    assert source.members == ("A.md",)
    assert len(source.witnesses) == 130
    assert g.emitted_reasons == 0
    assert g.candidates == ()
    assert g.certificates == ()

    # Pair control: the unchanged public batch API still bounds ONE
    # batch at the SAME inherited cap: the canonical Responses-root
    # envelope plus 128 read requests (129 requests) refuses
    # overbound with the closed batch limitation and no partial
    # admission, while 128 requests (root + 127 reads) completes.
    admission_ns = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-history-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
    )

    def _pair_batch(read_count: int) -> tuple[GraphRequest, ...]:
        return (
            root_request(),
            *(
                read_request(endpoint, f"c-pair{i:03d}", "Pair body.\n", cmd="cat P.md")
                for i in range(read_count)
            ),
        )

    over = observe_bundle_admission_batch(_pair_batch(128), admission_ns)
    assert over.outcome is AdmissionOutcome.OVER_BOUND
    assert AdmissionLimitation.BATCH_OVER_BOUND in over.conflicts
    assert over.root_entry is None
    assert over.entries == ()
    under = observe_bundle_admission_batch(_pair_batch(127), admission_ns)
    assert AdmissionLimitation.BATCH_OVER_BOUND not in under.conflicts
    assert under.outcome is AdmissionOutcome.COMPLETE
    assert under.root_entry is not None


# ---------------------------------------------------------------------------
# I: resource domains at limit/first over, identity/immutability,
#    versions, no host IO, private operational reprs
# ---------------------------------------------------------------------------


def _work_fixture(h: Hist) -> None:
    """One earned DAG mixing currentness work and graph work:
    root -> Start -> {A, B}; the opaque AB group targets C; a
    changed descendant A (so per-group selection, not whole-proof
    usability, is exercised in the closure)."""
    h.boot_root("Read `Start.md` first.")
    h.read("c-start", "Read `A.md` and `B.md`.", cmd="cat Start.md")
    ab = h.read("c-ab", "See `C.md` here.\n", cmd="cat A.md B.md")
    h.issue("c-a2", (ab, CAUSAL_ROOT_FACT))
    h.read("c-a2", "A new.\n")


def _smallest_ok(lo: int, hi: int, probe: Callable[[int], bool]) -> int:
    """The smallest cap in [lo, hi] for which the probe derives OK
    (the fixture is EXACT-fixture/ID bound; only the cap moves, so
    the measured threshold binds this fixture, not a general law)."""
    assert probe(hi), "the upper cap must derive OK for this fixture"
    while lo < hi:
        mid = (lo + hi) // 2
        if probe(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_outer_work_at_limit_first_over(mode: AdmissionMode, endpoint: str) -> None:
    """I: the NEW outer work ledger spans the ACTUAL 018-e
    currentness work AND the graph work: the fixture derives OK at
    the measured smallest passing cap and ONE unit below it is
    refused with the exact outer-domain limitation and the exact
    input state."""
    h = Hist(mode, endpoint)
    _work_fixture(h)

    def probe(cap: int) -> bool:
        return (
            h.graph(bounds=CurrentGraphBounds(max_total_work_units=cap)).outcome
            is CurrentGraphOutcome.OK
        )

    work = _smallest_ok(1, 1 << 20, probe)
    ok = h.graph(bounds=CurrentGraphBounds(max_total_work_units=work))
    assert ok.outcome is CurrentGraphOutcome.OK
    assert ok.state is h.state
    assert ok.overlay is not None
    assert_refused(
        h.graph(bounds=CurrentGraphBounds(max_total_work_units=work - 1)),
        h.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.TOTAL_WORK_UNITS_OVER_BOUND,
    )


def _build_stage_hist(mode: AdmissionMode, endpoint: str, cap: int) -> Hist:
    """A fresh fixture built under a per-cap ACTUAL namespace: the
    graph-stage cap is an inherited actual field, so the retained
    proofs must bind the real per-cap scope keys (a rekey of an
    older state would be a foreign-scope forgery, not the test)."""
    ns = make_ns(
        mode,
        lineage=f"gw-{mode.value}-{endpoint}-{cap}",
        graph_bounds=GraphBounds(max_work_units=cap),
    )
    h = Hist(mode, endpoint)
    h.ns = ns
    h.state = empty_state(ns)
    h.revision = 0
    _work_fixture(h)
    return h


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_graph_stage_work_at_limit_first_over(mode: AdmissionMode, endpoint: str) -> None:
    """I: the inherited graph-stage work domain (GraphBounds.
    max_work_units) is charged ALONGSIDE the outer ledger for
    graph-owned operations: the fixture derives OK at the measured
    smallest passing stage cap and one below is refused with the
    exact stage-domain limitation, the outer default untouched."""

    def probe(cap: int) -> bool:
        h = _build_stage_hist(mode, endpoint, cap)
        result = derive_current_graph(h.state, h.ns)
        return result.outcome is CurrentGraphOutcome.OK and result.state is h.state

    work = _smallest_ok(1, 65536, probe)
    ok_hist = _build_stage_hist(mode, endpoint, work)
    ok = derive_current_graph(ok_hist.state, ok_hist.ns)
    assert ok.outcome is CurrentGraphOutcome.OK
    assert ok.state is ok_hist.state
    over_hist = _build_stage_hist(mode, endpoint, work - 1)
    assert_refused(
        derive_current_graph(over_hist.state, over_hist.ns),
        over_hist.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.GRAPH_WORK_UNITS_OVER_BOUND,
    )


# ---------------------------------------------------------------------------
# I: sorted-collection reservation (N log N) and iteration-visit accounting
# ---------------------------------------------------------------------------


def _run_charged_sort(
    values: list[Any],
    key: Callable[[Any], object] | None,
    work_cap: int,
) -> tuple[int, tuple[Any, ...]]:
    """Run the charged graph-owned sort under a fresh bounded ledger
    at the given outer cap; returns (exact outer work spent, result)."""
    outer = _current_graph_impl._OuterLedger(CurrentGraphBounds(max_total_work_units=work_cap))
    stage = _current_graph_impl._StageLedger(GraphBounds())
    result = _current_graph_impl._sorted(values, key, outer, stage)
    return outer.work_spent, tuple(result)


def test_i_charged_sort_law() -> None:
    """I: graph-owned sorts are charged stable merges: the output is
    identical to the built-in sorted (unsorted multi-pass, keyed,
    duplicates and stability included), the linear reservation
    happens BEFORE the operation (a budget below it touches
    nothing), and every actual comparison and element write is
    charged one-for-one -- the exact outer total is
    1 + n + n * ceil(log2 n) + comparisons (empty input: no work)."""
    # (1) output identity against the built-in sorted.
    for sample in (
        ["b", "a", "c", "a", "b"],
        [3, 1, 4, 2],
        [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        [5, 2, 9, 1, 7, 3, 8, 4, 6, 0, 11, 12, 10],
    ):
        _cost, result = _run_charged_sort(list(sample), None, 1 << 20)
        assert result == tuple(sorted(sample))
    _cost, result = _run_charged_sort([], None, 1)
    assert result == () and _cost == 0
    _cost, result = _run_charged_sort(["only"], None, 1 << 10)
    assert result == ("only",) and _cost == 2  # construction + working copy
    # keyed form: the key moves WITH the value through every pass.
    keyed: list[Any] = [("k", "x"), ("k", "y"), ("j", "z"), ("k", "w"), ("a", "q")]
    _cost, result = _run_charged_sort(keyed, lambda t: t[0], 1 << 20)
    assert result == tuple(sorted(keyed, key=lambda t: t[0]))
    # stability: on equal keys the earlier element stays earlier.
    assert result == (("a", "q"), ("j", "z"), ("k", "x"), ("k", "y"), ("k", "w"))

    # (2) exact accounting identity on distinct multi-pass inputs:
    # total = 1 + n + n*ceil(log2 n) element writes + the measured
    # actual comparison count.
    for n in (2, 3, 5, 8, 16, 32):
        _CountingWitness.reset()
        values: list[Any] = [_CountingWitness(n - 1 - i) for i in range(n)]
        cost, result = _run_charged_sort(values, None, 1 << 20)
        comparisons = _CountingWitness.lts
        assert [w._value for w in result] == list(range(n))
        assert comparisons >= 1
        assert cost == 1 + n + n * (n - 1).bit_length() + comparisons

    # (3) the linear reservation precedes the operation: a budget
    # below 1 + n refuses before the working copy is even built, so
    # no comparison can have run.
    for n in (2, 8):
        _CountingWitness.reset()
        values = [_CountingWitness(n - 1 - i) for i in range(n)]
        with pytest.raises(_current_graph_impl._OuterOverflow):
            _run_charged_sort(values, None, n)
        assert _CountingWitness.lts == 0


class _CountingWitness:
    """A hashable, comparable stand-in for a witness coordinate that
    counts every membership hash and comparison it participates in,
    proving the reservation happens BEFORE the collection is touched
    (zero probes at one unit below the reservation)."""

    hashes = 0
    lts = 0

    def __init__(self, value: int) -> None:
        self._value = value
        self._hash = hash(value)

    def __hash__(self) -> int:
        _CountingWitness.hashes += 1
        return self._hash

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _CountingWitness) and self._value == other._value

    def __lt__(self, other: _CountingWitness) -> bool:
        _CountingWitness.lts += 1
        return self._value < other._value

    def __repr__(self) -> str:
        return f"W{self._value}"

    @classmethod
    def reset(cls) -> None:
        cls.hashes = 0
        cls.lts = 0


def _sort_witnesses_fixture(values: list[Any], work_cap: int) -> tuple[Any, ...]:
    outer = _current_graph_impl._OuterLedger(CurrentGraphBounds(max_total_work_units=work_cap))
    stage = _current_graph_impl._StageLedger(GraphBounds())
    return _current_graph_impl._sort_witnesses(values, outer, stage)


def test_i_sort_witnesses_reservation_before_collection() -> None:
    """I: witness retention reserves the linear part (construction
    + set walk over the INPUT length + working copy) BEFORE the
    collection is touched -- one unit below that reservation
    nothing is hashed or compared -- and then charges every actual
    comparison and element write of the dedup sort: the exact outer
    total is 1 + 2n + m*ceil(log2 m) + comparisons where m is the
    deduplicated count (duplicates shrink the sort but never the
    reserved set walk)."""

    def smallest_witness_cap(values: list[Any]) -> int:
        def ok(cap: int) -> bool:
            try:
                _sort_witnesses_fixture(values, cap)
            except _current_graph_impl._OuterOverflow:
                return False
            return True

        lo, hi = 1, 1 << 16
        assert ok(hi)
        while lo < hi:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo

    total_unique: dict[int, int] = {}
    for n in (2, 16):
        values: list[Any] = [_CountingWitness(i) for i in reversed(range(n))]
        _CountingWitness.reset()
        with pytest.raises(_current_graph_impl._OuterOverflow):
            _sort_witnesses_fixture(values, 2 * n)
        assert _CountingWitness.hashes == 0 and _CountingWitness.lts == 0
        total = smallest_witness_cap(values)
        _CountingWitness.reset()
        result = _sort_witnesses_fixture(values, total)
        comparisons = _CountingWitness.lts
        assert [w._value for w in result] == list(range(n))
        assert _CountingWitness.hashes >= n
        assert total == 1 + 2 * n + n * (n - 1).bit_length() + comparisons
        total_unique[n] = total
    # duplicate control: 16 input coordinates, 3 distinct values --
    # reserving the unique count (3) still refuses untouched because
    # the set walk runs over the INPUT length 16; the exact total
    # then accounts the sort over the 3 unique values only.
    duplicates: list[Any] = [_CountingWitness(i % 3) for i in range(16)]
    _CountingWitness.reset()
    with pytest.raises(_current_graph_impl._OuterOverflow):
        _sort_witnesses_fixture(duplicates, 1 + 2 * 3)
    assert _CountingWitness.hashes == 0 and _CountingWitness.lts == 0
    total_dup = smallest_witness_cap(duplicates)
    _CountingWitness.reset()
    result = _sort_witnesses_fixture(duplicates, total_dup)
    comparisons_dup = _CountingWitness.lts
    assert [w._value for w in result] == [0, 1, 2]
    assert total_dup == 1 + 2 * 16 + 3 * (3 - 1).bit_length() + comparisons_dup
    assert total_dup < total_unique[16]


def _witness_fixture(h: Hist, count: int) -> None:
    """Root plus ``count`` equal-content reads of A.md: ONE interned
    (path, digest) source supplier carrying ``count`` distinct
    witness coordinates -- every extra read adds a membership to the
    sorted witness retention, never a new supplier."""
    h.boot_root(ROOT_TEXT)
    for i in range(count):
        h.read(f"c-a{i}", "A same.\n")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_witness_sorted_reservation_work_charged(mode: AdmissionMode, endpoint: str) -> None:
    """I: end-to-end, every retained witness membership is accounted
    (linear set-walk reservation over the input length plus the
    charged merge's element writes and comparisons): the 130-witness
    fixture passes at the measured smallest outer cap,
    first-over-refuses with the exact input state, and costs at
    least one full 130-vs-1 witness-retention difference over the
    1-witness fixture."""
    h130 = Hist(mode, endpoint)
    _witness_fixture(h130, 130)
    graph = h130.graph_ok()
    source = next(s for s in graph.suppliers if s.kind is CurrentGraphSupplierKind.SOURCE)
    assert len(source.witnesses) == 130
    assert len(source.coordinates) == 130

    def probe130(cap: int) -> bool:
        return (
            h130.graph(bounds=CurrentGraphBounds(max_total_work_units=cap)).outcome
            is CurrentGraphOutcome.OK
        )

    work = _smallest_ok(1, 1 << 20, probe130)
    ok = h130.graph(bounds=CurrentGraphBounds(max_total_work_units=work))
    assert ok.outcome is CurrentGraphOutcome.OK
    assert ok.state is h130.state
    assert_refused(
        h130.graph(bounds=CurrentGraphBounds(max_total_work_units=work - 1)),
        h130.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.TOTAL_WORK_UNITS_OVER_BOUND,
    )

    h1 = Hist(mode, endpoint)
    _witness_fixture(h1, 1)

    def probe1(cap: int) -> bool:
        return (
            h1.graph(bounds=CurrentGraphBounds(max_total_work_units=cap)).outcome
            is CurrentGraphOutcome.OK
        )

    work1 = _smallest_ok(1, 1 << 20, probe1)
    assert work - work1 >= (1 + 2 * 130 + 130 * (130 - 1).bit_length()) - (1 + 2 * 1)


def _iteration_fixture(h: Hist) -> None:
    """Root -> S (acquired); acquired S -> acquired X (terminal);
    four distinct opaque (Q{i}, R{i}) groups whose members are
    referenced ONLY by their own group (group-attributed
    current-opaque rows; a path shared by several groups would be
    ownership-ambiguous instead), all targeting the unacquired
    T.md.  Every group is
    SELECTED as current-opaque but every member is unreachable, so
    each certificate is retained unusable and re-evaluated on each
    joint pass until finalization, while the ordinary joins force
    repeated already-scanned node visits: that iteration/re-visit
    work is real charged work in both ledgers.  (A member referenced
    but never acquired would be ownership-ambiguous instead, staling
    the whole opaque group out of selection -- a different law.)"""
    h.boot_root("Read `S.md` first.")
    h.read("c-s", "Read `X.md`.", cmd="cat S.md")
    h.read("c-x", "End.\n", cmd="cat X.md")
    for i in range(4):
        h.read(f"c-g{i}", "See `T.md`.\n", cmd=f"cat Q{i}.md R{i}.md")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_iteration_visit_work_charged(mode: AdmissionMode, endpoint: str) -> None:
    """I: repeated-pass node/candidate visits (already-scanned skips
    and already-finalized re-visits) are charged in both ledgers:
    the fixture passes at the measured smallest outer cap and
    first-over-refuses with the exact input state, and the same
    holds for the inherited graph-stage work domain under per-cap
    actual namespaces."""
    h = Hist(mode, endpoint)
    _iteration_fixture(h)
    assert len(h.state.occurrences) == 6
    overlay = overlay_of(h)
    # the four groups are ACTUAL selected current-opaque ownership
    # units (their members are group-attributed, nothing else
    # references them); S/X are singleton current-known.
    q_groups = sorted(
        (grp.members, grp.group_status) for grp in overlay.groups if grp.members[0].startswith("Q")
    )
    assert q_groups == [
        ((f"Q{i}.md", f"R{i}.md"), CurrentnessStatus.CURRENT_OPAQUE) for i in range(4)
    ]
    for grp in overlay.groups:
        if not grp.members[0].startswith("Q"):
            assert grp.group_status is CurrentnessStatus.CURRENT_KNOWN, grp.members
    graph = h.graph_ok()
    # only the root and the acquired chain are graph nodes: the
    # group members and the certificate target were never joined.
    assert node_paths(graph) == {"AGENTS.md", "S.md", "X.md"}
    for i in range(4):
        cert = cert_for_members(graph, (f"Q{i}.md", f"R{i}.md"))
        assert cert is not None
        assert cert.usable is False
        assert cert.depth is None
        assert cert.resolved_target == "T.md"
        assert CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE in cert.reasons
    assert len(graph.certificates) == 4
    assert graph.unreachable_current_paths == ()

    def probe(cap: int) -> bool:
        return (
            h.graph(bounds=CurrentGraphBounds(max_total_work_units=cap)).outcome
            is CurrentGraphOutcome.OK
        )

    work = _smallest_ok(1, 1 << 20, probe)
    ok = h.graph(bounds=CurrentGraphBounds(max_total_work_units=work))
    assert ok.outcome is CurrentGraphOutcome.OK
    assert ok.state is h.state
    assert_refused(
        h.graph(bounds=CurrentGraphBounds(max_total_work_units=work - 1)),
        h.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.TOTAL_WORK_UNITS_OVER_BOUND,
    )

    def build_stage_hist(cap: int, lineage: str) -> Hist:
        ns = make_ns(
            mode,
            lineage=lineage,
            graph_bounds=GraphBounds(max_work_units=cap),
        )
        fresh = Hist(mode, endpoint)
        fresh.ns = ns
        fresh.state = empty_state(ns)
        fresh.revision = 0
        _iteration_fixture(fresh)
        return fresh

    def stage_probe(cap: int) -> bool:
        fresh = build_stage_hist(cap, f"gi-{mode.value}-{endpoint}-{cap}")
        return derive_current_graph(fresh.state, fresh.ns).outcome is CurrentGraphOutcome.OK

    stage_work = _smallest_ok(1, 65536, stage_probe)
    over = build_stage_hist(stage_work - 1, f"gi-{mode.value}-{endpoint}-over")
    assert_refused(
        derive_current_graph(over.state, over.ns),
        over.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.GRAPH_WORK_UNITS_OVER_BOUND,
    )


def _diag_fixture(h: Hist) -> None:
    """Two root-referenced paths, each carried by a pair of equal
    byte-digest reversed opaque groups: exactly TWO blocked
    ambiguity nodes (C1, C2) -- the emitted reason total to target."""
    h.boot_root("Read `C1.md` and `C2.md` first.")
    h.read("c-c1x", "One.\n", cmd="cat C1.md X.md")
    h.read("c-xc1", "One.\n", cmd="cat X.md C1.md")
    h.read("c-c2y", "Two.\n", cmd="cat C2.md Y.md")
    h.read("c-yc2", "Two.\n", cmd="cat Y.md C2.md")


def _build_diag_hist(mode: AdmissionMode, endpoint: str, cap: int) -> Hist:
    ns = make_ns(
        mode,
        lineage=f"gd-{mode.value}-{endpoint}-{cap}",
        graph_bounds=GraphBounds(max_diagnostics=cap),
    )
    h = Hist(mode, endpoint)
    h.ns = ns
    h.state = empty_state(ns)
    h.revision = 0
    _diag_fixture(h)
    return h


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_root_only_group_supplies_nothing(mode: AdmissionMode, endpoint: str) -> None:
    """I: a read group whose members are ALL the root file is
    CURRENT_OPAQUE in the ACTUAL 018-e overlay but supplies nothing
    in 018-f: the root-only membership scan is a charged per-member
    walk, the group is skipped, no group supplier or alternate
    root-text supplier appears, and the derivation is OK at the
    measured smallest outer cap (first over refused)."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    h.read("c-r1", "Root bytes.\n", cmd="cat AGENTS.md AGENTS.md")
    ov = overlay_of(h)
    assert [(g.members, g.group_status) for g in ov.groups] == [
        (("AGENTS.md", "AGENTS.md"), CurrentnessStatus.CURRENT_OPAQUE)
    ]
    g = h.graph_ok()
    assert [s.kind for s in g.suppliers] == [CurrentGraphSupplierKind.ROOT]
    assert node(g, "AGENTS.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "A.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED

    def probe(cap: int) -> bool:
        return (
            h.graph(bounds=CurrentGraphBounds(max_total_work_units=cap)).outcome
            is CurrentGraphOutcome.OK
        )

    work = _smallest_ok(1, 1 << 20, probe)
    assert (
        h.graph(bounds=CurrentGraphBounds(max_total_work_units=work)).outcome
        is CurrentGraphOutcome.OK
    )
    assert_refused(
        h.graph(bounds=CurrentGraphBounds(max_total_work_units=work - 1)),
        h.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.TOTAL_WORK_UNITS_OVER_BOUND,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_supplier_interning_witness_deferred_charged(mode: AdmissionMode, endpoint: str) -> None:
    """I: ONE occurrence with TWO proven singleton groups of the
    SAME path/digest (cat A.md && echo MARK && cat A.md) interns
    ONE source supplier whose raw witness list receives the SAME
    occurrence twice: duplicate witness elimination and ordering
    are deferred to the charged output retention (final witnesses
    deduplicated/sorted, BOTH original group coordinates retained),
    and the outer cap boundary lands on the charged total (first
    over refused)."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    seg = "A same.\n"
    # The 017 partitioned law: the request result output carries the
    # marker line, but the retained original source is the EXACT
    # concatenated segment bytes (the proven marker delimiters are
    # not source bytes).
    h.observe(
        read_request(
            endpoint,
            "c-r1",
            seg + "MARK\n" + seg,
            cmd="cat A.md && echo 'MARK' && cat A.md",
        ),
        note="read:c-r1",
    )
    occurrences = h.state.occurrences
    assert len(occurrences) == 1
    occurrence = occurrences[-1]
    assert occurrence.call_id == "c-r1"
    assert occurrence.endpoint == endpoint
    occ = occurrence.occurrence_id
    proof = occurrence.proof
    assert proof.source_text == seg + seg
    assert proof.source_digest == _sha(seg + seg)
    assert [t.member_positions for t in proof.segments] == [(0,), (1,)]
    assert [t.member_digest for t in proof.segments] == [_sha(seg), _sha(seg)]
    ov = overlay_of(h)
    assert sorted((g.members, g.group_index, g.group_status) for g in ov.groups) == [
        (("A.md",), 0, CurrentnessStatus.CURRENT_KNOWN),
        (("A.md",), 1, CurrentnessStatus.CURRENT_KNOWN),
    ]
    g = h.graph_ok()
    source = [s for s in g.suppliers if s.kind is CurrentGraphSupplierKind.SOURCE]
    assert len(source) == 1
    s0 = source[0]
    assert s0.path == "A.md"
    assert s0.digest == _sha(seg)
    assert s0.witnesses == (occ,)  # deduplicated by the charged retention
    assert len(s0.coordinates) == 2
    assert tuple(c.group_index for c in s0.coordinates) == (0, 1)
    assert all(c.occurrence_id == occ for c in s0.coordinates)
    assert node(g, "A.md").witnesses == (occ,)
    assert node(g, "A.md").depth == 1

    def probe(cap: int) -> bool:
        return (
            h.graph(bounds=CurrentGraphBounds(max_total_work_units=cap)).outcome
            is CurrentGraphOutcome.OK
        )

    work = _smallest_ok(1, 1 << 20, probe)
    ok = h.graph(bounds=CurrentGraphBounds(max_total_work_units=work))
    assert ok.outcome is CurrentGraphOutcome.OK
    assert ok.state is h.state
    assert_refused(
        h.graph(bounds=CurrentGraphBounds(max_total_work_units=work - 1)),
        h.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.TOTAL_WORK_UNITS_OVER_BOUND,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_diagnostic_caps_at_limit_first_over(mode: AdmissionMode, endpoint: str) -> None:
    """I: the NEW outer diagnostic domain (CurrentGraphBounds.
    max_diagnostics) and the inherited stage diagnostic domain
    (GraphBounds.max_diagnostics) each bound the TOTAL newly emitted
    closed reason entries, charged before each actual emission: the
    two-blocked-node fixture passes at cap 2 and first-over-refuses
    at cap 1 in both domains."""
    h = Hist(mode, endpoint)
    _diag_fixture(h)
    g = h.graph_ok()
    blocked = [
        n
        for n in g.nodes
        if n.status
        in (
            CurrentGraphStatus.BLOCKED_CONFLICT,
            CurrentGraphStatus.BLOCKED_AMBIGUITY,
        )
    ]
    assert {n.path for n in blocked} == {"C1.md", "C2.md"}
    assert g.emitted_reasons == 2
    at_limit = h.graph(bounds=CurrentGraphBounds(max_diagnostics=2))
    assert at_limit.outcome is CurrentGraphOutcome.OK
    assert_refused(
        h.graph(bounds=CurrentGraphBounds(max_diagnostics=1)),
        h.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.DIAGNOSTICS_FULL,
    )
    ok_stage = _build_diag_hist(mode, endpoint, 2)
    ok = derive_current_graph(ok_stage.state, ok_stage.ns)
    assert ok.outcome is CurrentGraphOutcome.OK
    assert ok.overlay is not None
    assert ok.overlay.emitted_reasons == 2
    over_stage = _build_diag_hist(mode, endpoint, 1)
    assert_refused(
        derive_current_graph(over_stage.state, over_stage.ns),
        over_stage.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.GRAPH_DIAGNOSTICS_OVER_BOUND,
    )


def _build_capped_hist(
    mode: AdmissionMode, endpoint: str, lineage: str, graph_bounds: GraphBounds
) -> Hist:
    ns = make_ns(mode, lineage=lineage, graph_bounds=graph_bounds)
    h = Hist(mode, endpoint)
    h.ns = ns
    h.state = empty_state(ns)
    h.revision = 0
    return h


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_inherited_node_cap(mode: AdmissionMode, endpoint: str) -> None:
    """I: the inherited node ceiling bounds the ACTUAL emitted nodes
    (root + one discovered = 2): at-limit OK, first-over typed
    refusal."""
    required = 2
    ok_hist = _build_capped_hist(
        mode, endpoint, f"gn-{mode.value}-{endpoint}", GraphBounds(max_nodes=required)
    )
    ok_hist.boot_root("Read `A.md` first.")
    ok = derive_current_graph(ok_hist.state, ok_hist.ns)
    assert ok.outcome is CurrentGraphOutcome.OK
    assert len(ok.overlay.nodes) == required  # type: ignore[union-attr]
    over_hist = _build_capped_hist(
        mode, endpoint, f"gn-{mode.value}-{endpoint}-over", GraphBounds(max_nodes=1)
    )
    over_hist.boot_root("Read `A.md` first.")
    assert_refused(
        derive_current_graph(over_hist.state, over_hist.ns),
        over_hist.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.GRAPH_NODES_OVER_BOUND,
    )


def _two_edge_fixture(h: Hist) -> None:
    h.boot_root("Read `A.md` first.")
    h.read("c-a", "See `B.md`.", cmd="cat A.md")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_inherited_edge_cap(mode: AdmissionMode, endpoint: str) -> None:
    """I: the inherited edge ceiling bounds the COMBINED emitted
    ordinary edges + usable certificates (here 2 ordinary): at-limit
    OK, first-over typed refusal."""
    required = 2
    ok_hist = _build_capped_hist(
        mode, endpoint, f"ge-{mode.value}-{endpoint}", GraphBounds(max_edges=required)
    )
    _two_edge_fixture(ok_hist)
    ok = derive_current_graph(ok_hist.state, ok_hist.ns)
    assert ok.outcome is CurrentGraphOutcome.OK
    assert len(ok.overlay.edges) == required  # type: ignore[union-attr]
    over_hist = _build_capped_hist(
        mode, endpoint, f"ge-{mode.value}-{endpoint}-over", GraphBounds(max_edges=1)
    )
    _two_edge_fixture(over_hist)
    assert_refused(
        derive_current_graph(over_hist.state, over_hist.ns),
        over_hist.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.GRAPH_EDGES_OVER_BOUND,
    )


def _three_candidate_fixture(h: Hist) -> None:
    h.boot_root("Read `A.md` first.")
    h.read("c-a", "`../escape.md` and `B.md` here.\n", cmd="cat A.md")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_inherited_candidate_cap(mode: AdmissionMode, endpoint: str) -> None:
    """I: the inherited candidate ceiling charges EVERY actual
    enumeration attempt (root 1 + source 2 = 3, before acceptance/
    dedup): at-limit OK, first-over typed refusal; the retained
    output is only the unresolvable traversal candidate."""
    required = 3
    ok_hist = _build_capped_hist(
        mode,
        endpoint,
        f"gc-{mode.value}-{endpoint}",
        GraphBounds(max_reference_candidates_total=required),
    )
    _three_candidate_fixture(ok_hist)
    ok = derive_current_graph(ok_hist.state, ok_hist.ns)
    assert ok.outcome is CurrentGraphOutcome.OK
    overlay = ok.overlay
    assert overlay is not None
    assert len(overlay.candidates) == 1
    entry = overlay.candidates[0]
    assert entry.candidate.syntax is CandidateSyntax.BACKTICK_CODE
    assert entry.candidate.status is CandidateStatus.ACCEPTED
    assert GraphLimitation.PATH_TRAVERSAL in entry.candidate.reasons
    assert entry.owner == node(overlay, "A.md").owner
    over_hist = _build_capped_hist(
        mode,
        endpoint,
        f"gc-{mode.value}-{endpoint}-over",
        GraphBounds(max_reference_candidates_total=2),
    )
    _three_candidate_fixture(over_hist)
    assert_refused(
        derive_current_graph(over_hist.state, over_hist.ns),
        over_hist.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.GRAPH_CANDIDATES_OVER_BOUND,
    )


def _two_document_fixture(h: Hist) -> None:
    h.boot_root("Read `A.md` first.")
    h.read("c-a", "See `B.md`.\n", cmd="cat A.md")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_inherited_document_cap(mode: AdmissionMode, endpoint: str) -> None:
    """I: the inherited document ceiling charges each ACTUAL scanned
    source region (root + A = 2): at-limit OK, first-over typed
    refusal."""
    required = 2
    ok_hist = _build_capped_hist(
        mode, endpoint, f"gd2-{mode.value}-{endpoint}", GraphBounds(max_documents=required)
    )
    _two_document_fixture(ok_hist)
    ok = derive_current_graph(ok_hist.state, ok_hist.ns)
    assert ok.outcome is CurrentGraphOutcome.OK
    over_hist = _build_capped_hist(
        mode, endpoint, f"gd2-{mode.value}-{endpoint}-over", GraphBounds(max_documents=1)
    )
    _two_document_fixture(over_hist)
    assert_refused(
        derive_current_graph(over_hist.state, over_hist.ns),
        over_hist.state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.GRAPH_DOCUMENTS_OVER_BOUND,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_inherited_single_source_cap(mode: AdmissionMode, endpoint: str) -> None:
    """I: the inherited per-source byte ceiling is ONE shared actual
    cap: the observation stage enforces it on EVERY retained source
    (the 33-byte root bootstrap is accepted at cap 33 and refused
    with the exact inherited limitation at cap 32 BEFORE any
    retention), and the 018-f derivation re-defends it on the
    charged anchor preflight over the ACTUAL retained anchor (the
    coherent forged-anchor zero-touch sentinel control)."""
    ok_hist = _build_capped_hist(
        mode,
        endpoint,
        f"gs-{mode.value}-{endpoint}",
        GraphBounds(max_single_source_bytes=33),
    )
    ok_hist.boot_root()
    ok = derive_current_graph(ok_hist.state, ok_hist.ns)
    assert ok.outcome is CurrentGraphOutcome.OK
    ok_overlay = ok.overlay
    assert ok_overlay is not None
    assert node(ok_overlay, "AGENTS.md").depth == 0
    over_hist = _build_capped_hist(
        mode,
        endpoint,
        f"gs-{mode.value}-{endpoint}-over",
        GraphBounds(max_single_source_bytes=32),
    )
    transition = observe_causal_history(
        (
            GraphRequest(
                payload={"input": [root_item(ROOT_TEXT)]},
                endpoint="responses",
                context=None,
            ),
        ),
        over_hist.ns,
        over_hist.state,
        over_hist.revision,
    )
    assert transition.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert transition.diagnostics == (CausalHistoryLimitation.SOURCE_OVER_BOUND,)
    assert transition.state is over_hist.state
    assert over_hist.state.root is None


def _build_total_hist(mode: AdmissionMode, endpoint: str, cap: int) -> Hist:
    h = _build_capped_hist(
        mode,
        endpoint,
        f"gt-{mode.value}-{endpoint}-{cap}",
        GraphBounds(max_total_inspected_source_bytes=cap),
    )
    h.boot_root()
    h.read("c-a", "See `B.md`.\n", cmd="cat A.md")
    return h


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_inherited_total_inspected_cap(mode: AdmissionMode, endpoint: str) -> None:
    """I: the inherited TOTAL inspected-source allowance is honored
    per region against the REMAINING budget (root 33B + A 12B = 45):
    the O(1) character guard refuses an over-remaining region with
    ZERO touches; a multibyte region exits the bounded walk
    mid-region (0 < touches < len, zero encodes); at the exact total
    the fixture derives OK."""
    ok_hist = _build_total_hist(mode, endpoint, 45)
    ok = derive_current_graph(ok_hist.state, ok_hist.ns)
    assert ok.outcome is CurrentGraphOutcome.OK
    ok_overlay = ok.overlay
    assert ok_overlay is not None
    assert node(ok_overlay, "B.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED

    over_hist = _build_total_hist(mode, endpoint, 44)
    _SentinelStr.reset()
    occ = over_hist.state.occurrences[-1]
    assert occ.proof.source_text == "See `B.md`.\n"
    forged_proof = occ.proof.model_copy(update={"source_text": _SentinelStr(occ.proof.source_text)})
    forged_occ = occ.model_copy(update={"proof": forged_proof})
    state = over_hist.state.model_copy(
        update={"occurrences": over_hist.state.occurrences[:-1] + (forged_occ,)}
    )
    assert_refused(
        derive_current_graph(state, over_hist.ns),
        state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.GRAPH_SOURCE_BYTES_OVER_BOUND,
    )
    assert _SentinelStr.getitems == 0
    assert _SentinelStr.encodes == 0

    wide_hist = _build_capped_hist(
        mode,
        endpoint,
        f"gt-{mode.value}-{endpoint}-wide",
        GraphBounds(max_total_inspected_source_bytes=45),
    )
    wide_hist.boot_root()
    wide_hist.read("c-a", "\u00e9" * 8, cmd="cat A.md")
    _SentinelStr.reset()
    w_occ = wide_hist.state.occurrences[-1]
    w_forged_proof = w_occ.proof.model_copy(
        update={"source_text": _SentinelStr(w_occ.proof.source_text)}
    )
    w_forged_occ = w_occ.model_copy(update={"proof": w_forged_proof})
    w_state = wide_hist.state.model_copy(
        update={"occurrences": wide_hist.state.occurrences[:-1] + (w_forged_occ,)}
    )
    assert_refused(
        derive_current_graph(w_state, wide_hist.ns),
        w_state,
        CurrentGraphOutcome.REFUSED_OVER_BOUND,
        CurrentGraphLimitation.GRAPH_SOURCE_BYTES_OVER_BOUND,
    )
    assert 0 < _SentinelStr.getitems < 8
    assert _SentinelStr.encodes == 0

    wide_ok = _build_capped_hist(
        mode,
        endpoint,
        f"gt-{mode.value}-{endpoint}-wide-ok",
        GraphBounds(max_total_inspected_source_bytes=49),
    )
    wide_ok.boot_root()
    wide_ok.read("c-a", "\u00e9" * 8, cmd="cat A.md")
    assert derive_current_graph(wide_ok.state, wide_ok.ns).outcome is (CurrentGraphOutcome.OK)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_foreign_scope_and_malformed_state(mode: AdmissionMode, endpoint: str) -> None:
    """I: the early O(1) fences: a mismatched ACTUAL history key is
    a foreign-scope refusal, and a corrupted retained state
    (duplicated occurrence identities) is a malformed-state
    refusal -- both with the exact input state and no overlay."""
    h = Hist(mode, endpoint)
    h.boot_root()
    h.read("c-1", "A body.\n")
    foreign_ns = h.ns.model_copy(update={"history_key": "f" * 64})
    assert_refused(
        derive_current_graph(h.state, foreign_ns),
        h.state,
        CurrentGraphOutcome.REFUSED_FOREIGN_SCOPE,
        CurrentGraphLimitation.FOREIGN_SCOPE,
    )
    malformed = h.state.model_copy(update={"occurrences": h.state.occurrences * 2})
    assert_refused(
        derive_current_graph(malformed, h.ns),
        malformed,
        CurrentGraphOutcome.REFUSED_STATE_MALFORMED,
        CurrentGraphLimitation.STATE_MALFORMED,
    )


_VERSION_FIELDS = (
    "admission_version",
    "observation_version",
    "graph_version",
    "reference_version",
    "proof_version",
    "history_version",
    "arguments_version",
)


@pytest.mark.parametrize("field", _VERSION_FIELDS)
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_coherent_unsupported_versions_refused(
    mode: AdmissionMode, endpoint: str, field: str
) -> None:
    """I: EACH of the SEVEN actual inherited version fields is
    revalidated against the supported constants BEFORE any
    interpretation: a coherent DIRECT-constructed namespace with
    the actual full key chain recomputed (so the negative state
    key MATCHES and no stale-key fence can mask) is refused
    REFUSED_VERSION_CONFLICT with the exact negative state."""
    h = Hist(mode, endpoint)
    h.boot_root()
    h.read("c-v", "A body.\n")
    coherent = _coherent_rekeyed_ns(h.ns, {field: "unsupported-synthetic/v99"})
    assert coherent.history_key != h.ns.history_key
    negative_state = h.state.model_copy(update={"history_key": coherent.history_key})
    assert_refused(
        derive_current_graph(negative_state, coherent),
        negative_state,
        CurrentGraphOutcome.REFUSED_VERSION_CONFLICT,
        CurrentGraphLimitation.VERSION_UNSUPPORTED,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_state_identity_and_immutability(mode: AdmissionMode, endpoint: str) -> None:
    """I: the derivation never mutates its inputs: on OK the EXACT
    state object is returned, the deep dump and every retained
    proof's exact bytes/digest/lengths are unchanged; on every
    refusal the EXACT input state is preserved with no overlay."""
    h = Hist(mode, endpoint)
    _work_fixture(h)
    state = h.state
    before = state.model_dump()
    proofs_before = [
        (
            o.proof.source_text,
            o.proof.source_digest,
            o.proof.source_byte_length,
            o.proof.source_char_length,
        )
        for o in state.occurrences
    ]
    ok = h.graph()
    assert ok.outcome is CurrentGraphOutcome.OK
    assert ok.state is state
    assert state.model_dump() == before
    assert [
        (
            o.proof.source_text,
            o.proof.source_digest,
            o.proof.source_byte_length,
            o.proof.source_char_length,
        )
        for o in state.occurrences
    ] == proofs_before

    foreign = derive_current_graph(state, h.ns.model_copy(update={"history_key": "f" * 64}))
    assert foreign.outcome is CurrentGraphOutcome.REFUSED_FOREIGN_SCOPE
    assert foreign.state is state
    assert foreign.overlay is None
    malformed_state = state.model_copy(update={"occurrences": state.occurrences * 2})
    malformed = derive_current_graph(malformed_state, h.ns)
    assert malformed.outcome is CurrentGraphOutcome.REFUSED_STATE_MALFORMED
    assert malformed.state is malformed_state
    assert malformed.overlay is None
    over = h.graph(bounds=CurrentGraphBounds(max_total_work_units=1))
    assert over.outcome is CurrentGraphOutcome.REFUSED_OVER_BOUND
    assert over.state is state
    assert over.overlay is None


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_public_paths_perform_no_host_io(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """I: every public current-graph path -- the OK derivation and
    the foreign-scope / malformed-state / outer-overbound /
    coherent-unsupported-version / forged-root refusals -- performs
    no host IO: no file, socket, subprocess or path IO facility is
    touched after import/setup."""
    h = Hist(mode, endpoint)
    h.boot_root()
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

    ok = derive_current_graph(state, h.ns)
    assert ok.outcome is CurrentGraphOutcome.OK
    assert ok.overlay is not None
    foreign = derive_current_graph(state, h.ns.model_copy(update={"history_key": "f" * 64}))
    assert foreign.outcome is CurrentGraphOutcome.REFUSED_FOREIGN_SCOPE
    malformed_state = state.model_copy(update={"occurrences": state.occurrences * 2})
    malformed = derive_current_graph(malformed_state, h.ns)
    assert malformed.outcome is CurrentGraphOutcome.REFUSED_STATE_MALFORMED
    over = derive_current_graph(state, h.ns, CurrentGraphBounds(max_total_work_units=1))
    assert over.outcome is CurrentGraphOutcome.REFUSED_OVER_BOUND
    version_ns = _coherent_rekeyed_ns(h.ns, {"history_version": "unsupported-synthetic/v99"})
    version_state = state.model_copy(update={"history_key": version_ns.history_key})
    version = derive_current_graph(version_state, version_ns)
    assert version.outcome is CurrentGraphOutcome.REFUSED_VERSION_CONFLICT
    anchor = state.root
    assert anchor is not None
    forged_state = state.model_copy(update={"root": forge(anchor, root_text=7)})
    forged = derive_current_graph(forged_state, h.ns)
    assert forged.outcome is CurrentGraphOutcome.REFUSED_STATE_MALFORMED
    assert attempts == []


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_i_operational_reprs_stay_private(mode: AdmissionMode, endpoint: str) -> None:
    """I: the fixed enums/counts/private-repr law over EVERY
    exported nested record: actual path values never appear in
    repr() or str() of any supplier/node/edge/certificate/candidate/
    origin, of the graph itself, or of a refusal result, while the
    actual internal path fields stay unchanged."""
    h = Hist(mode, endpoint)
    h.boot_root(f"Read `{CANARY}A.md` first.")
    h.read("c-priv", f"See `{CANARY}B.md`.\n", cmd=f"cat {CANARY}A.md")
    g = h.graph_ok()
    assert node(g, f"{CANARY}A.md").digest == _sha(f"See `{CANARY}B.md`.\n")
    records: list[Any] = [g]
    records.extend(g.suppliers)
    records.extend(g.nodes)
    records.extend(g.edges)
    records.extend(g.certificates)
    records.extend(g.candidates)
    for supplier in g.suppliers:
        records.extend(supplier.coordinates)
    for certificate in g.certificates:
        records.append(certificate.candidate)
    for record in records:
        for rendered in (repr(record), str(record)):
            assert CANARY not in rendered, rendered
    refused = derive_current_graph(h.state, h.ns.model_copy(update={"history_key": "f" * 64}))
    for rendered in (repr(refused), str(refused)):
        assert CANARY not in rendered, rendered


# ---------------------------------------------------------------------------
# D (boundaryless subsegment): a partitioned proof carrying one proven
# singleton segment and one boundaryless subsegment; the subsegment
# stays indivisible when the proven sibling stales
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_d_boundaryless_subsegment_indivisible(mode: AdmissionMode, endpoint: str) -> None:
    """D: one partitioned proof with a proven A segment and a
    boundaryless (B, C) subsegment.  A changed descendant of A
    stales ONLY the A segment (its D edge goes); the boundaryless
    (B, C) subsegment of the SAME now-unusable whole proof stays
    current and INDIVISIBLE: its certificate record persists (still
    honestly unusable) and no spliced per-file B or C source is ever
    invented from the aggregate."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    seg_a = "From A see `D.md`.\n"
    seg_bc = "From BC see `E.md`.\n"
    h.observe(
        read_request(
            endpoint,
            "c-p1",
            seg_a + "MK\n" + seg_bc,
            cmd="cat A.md && echo 'MK' && cat B.md C.md",
        ),
        note="read:c-p1",
    )
    occurrence = h.state.occurrences[-1]
    p1 = occurrence.occurrence_id
    proof = occurrence.proof
    # EXACT partitioned preconditions: one proven singleton segment
    # plus one boundaryless subsegment (marker bytes excluded from
    # the retained source).
    assert proof.source_text == seg_a + seg_bc
    assert proof.source_digest == _sha(seg_a + seg_bc)
    segments = proof.segments
    assert len(segments) == 2
    assert segments[0].member_positions == (0,)
    assert segments[0].member_digest == _sha(seg_a)
    assert segments[1].member_positions == (1, 2)
    assert segments[1].member_digest is None
    assert segments[1].digest == _sha(seg_bc)

    g = h.graph_ok()
    assert node(g, "A.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "A.md").digest == _sha(seg_a)
    assert node(g, "A.md").witnesses == (p1,)
    assert node(g, "D.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "D.md").depth == 2
    assert edges_from(g, "A.md") == {"D.md"}
    cert = cert_for_members(g, ("B.md", "C.md"))
    assert cert is not None and cert.usable is False
    assert CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE in cert.reasons
    assert cert.resolved_target == "E.md"
    assert cert.depth is None
    assert "E.md" not in node_paths(g)
    assert all(
        supplier.path not in ("B.md", "C.md")
        for supplier in g.suppliers
        if supplier.kind is CurrentGraphSupplierKind.SOURCE
    )
    groups = [s for s in g.suppliers if s.kind is CurrentGraphSupplierKind.GROUP]
    assert len(groups) == 1
    assert groups[0].members == ("B.md", "C.md")
    assert groups[0].witnesses == (p1,)

    # A changed descendant of A: only the proven A segment stales.
    h.issue("c-a2", (p1, CAUSAL_ROOT_FACT))
    h.read("c-a2", "A changed.\n")
    g2 = h.graph_ok()
    assert node(g2, "A.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g2, "A.md").digest == _sha("A changed.\n")
    assert "D.md" not in node_paths(g2)
    assert not any(edge.source == "A.md" for edge in g2.edges)
    # The boundaryless subsegment survives per-group selection,
    # unchanged, with its ORIGINAL witness; still indivisible.
    cert2 = cert_for_members(g2, ("B.md", "C.md"))
    assert cert2 is not None and cert2.usable is False
    assert CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE in cert2.reasons
    assert cert2.resolved_target == "E.md"
    assert "E.md" not in node_paths(g2)
    assert all(
        supplier.path not in ("B.md", "C.md")
        for supplier in g2.suppliers
        if supplier.kind is CurrentGraphSupplierKind.SOURCE
    )
    groups2 = [s for s in g2.suppliers if s.kind is CurrentGraphSupplierKind.GROUP]
    assert len(groups2) == 1
    assert groups2[0].members == ("B.md", "C.md")
    assert groups2[0].witnesses == (p1,)
    assert g2.unreachable_current_paths == ()


# ---------------------------------------------------------------------------
# F (equal-content witnesses + DAG laws): equal-content interning keeps
# ALL supporting witnesses; a child of one blocks, a child of all
# resolves; unissued new versions, delayed older results, late trusted
# receipts and shifted replays follow the ACTUAL DAG, never arrival
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_equal_content_witnesses_retained(mode: AdmissionMode, endpoint: str) -> None:
    """F: two UNISSUED reads of A with EXACTLY equal content intern
    to the same known digest, and the current supplier and A's OWN
    outgoing derivation retain ALL supporting witnesses (first
    provenance, never collapsed); the root-owned Root->A edge is
    owned by the root anchor and never inherits the target's
    witnesses.
    A changed child of only ONE equal witness blocks the source
    (the untouched witness stays incomparable on the frozen
    frontier); a descendant of ALL witnesses resolves.  A later
    UNISSUED new version is incomparable with the resolved
    descendant (arrival never wins); an exact shifted replay of the
    original resolving request is a pure no-op."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    # The equal A bodies carry a REAL outgoing reference so the
    # retained witness facts can be asserted on A's own derivation
    # (a vacuous no-outgoing-edge fixture would not prove it).
    a_body = "See `C.md`.\n"
    a1 = h.read("c-a1", a_body)
    a2 = h.read("c-a2", a_body)
    by_call = {o.call_id: o for o in h.state.occurrences}
    # equal-content interning preconditions: distinct occurrences,
    # identical exact bytes/digest.
    assert a1 != a2
    assert by_call["c-a1"].proof.source_digest == _sha(a_body)
    assert by_call["c-a2"].proof.source_digest == _sha(a_body)
    assert by_call["c-a1"].proof.segments[0].member_digest == _sha(a_body)
    assert by_call["c-a2"].proof.segments[0].member_digest == _sha(a_body)
    both = tuple(sorted((a1, a2)))
    g = h.graph_ok()
    a_node = node(g, "A.md")
    assert a_node.status is CurrentGraphStatus.CURRENT_KNOWN
    assert a_node.digest == _sha(a_body)
    assert a_node.witnesses == both
    supplier = next(
        s for s in g.suppliers if s.kind is CurrentGraphSupplierKind.SOURCE and s.path == "A.md"
    )
    assert supplier.witnesses == both
    assert len(supplier.coordinates) == 2
    # The root-owned derivation carries the SOURCE (root) node's
    # witnesses -- the root anchor owns it and it never inherits
    # the target A's two witnesses.
    root_edge = next(e for e in g.edges if e.source == "AGENTS.md" and e.target == "A.md")
    assert root_edge.owner == ROOT_OWNER
    assert root_edge.witnesses == ()
    # A's OWN outgoing derivation retains BOTH supporting
    # witnesses.
    a_edge = next(e for e in g.edges if e.source == "A.md" and e.target == "C.md")
    assert a_edge.witnesses == both
    assert a_edge.owner == a_node.owner
    assert node(g, "C.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED

    # A changed child of only ONE equal witness: the untouched
    # witness is still on the frozen frontier (incomparable) -> the
    # source blocks; nothing is erased.
    h.issue("c-a3", (a1, CAUSAL_ROOT_FACT))
    a3 = h.read("c-a3", "A child.\n")
    g2 = h.graph_ok()
    assert node(g2, "A.md").status is CurrentGraphStatus.BLOCKED_CONFLICT
    assert {"c-a1", "c-a2", "c-a3"} <= {o.call_id for o in h.state.occurrences}

    # A descendant of ALL witnesses resolves A to exactly that
    # content.
    h.issue("c-a4", (a2, a3, CAUSAL_ROOT_FACT))
    a4 = h.read("c-a4", "A all.\n")
    g3 = h.graph_ok()
    assert node(g3, "A.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g3, "A.md").digest == _sha("A all.\n")
    assert node(g3, "A.md").witnesses == (a4,)
    content3 = _graph_content(g3)

    # An UNISSUED new version with different content is incomparable
    # with the resolved descendant: retained conflict, not
    # latest-wins by arrival.
    h.read("c-a5", "A later.\n")
    g4 = h.graph_ok()
    assert node(g4, "A.md").status is CurrentGraphStatus.BLOCKED_CONFLICT
    assert node(g4, "A.md").digest is None
    content4 = _graph_content(g4)
    assert content4 != content3

    # A shifted replay of the EXACT original resolving request (an
    # unrelated outer item prepended) is a pure no-op.
    plain = read_request(endpoint, "c-a4", "A all.\n").payload
    if endpoint == "responses":
        shifted_payload = {
            "input": [
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "compaction shift"}],
                },
                *plain["input"],
            ]
        }
    else:
        shifted_payload = {
            "messages": [
                {"role": "user", "content": "compaction shift"},
                *plain["messages"],
            ]
        }
    shifted = GraphRequest(payload=shifted_payload, endpoint=endpoint, context=None)
    replay = observe_causal_history((shifted,), h.ns, h.state, h.revision)
    assert replay.outcome is CausalHistoryOutcome.REPLAYED
    assert CausalHistoryLimitation.REPLAY_POSITION_SHIFTED in replay.diagnostics
    assert replay.state is h.state
    assert _graph_content(h.graph_ok()) == content4


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_delayed_older_result_retained_conflict(mode: AdmissionMode, endpoint: str) -> None:
    """F: a DELAYED older result (an issued-but-outstanding call
    completing late under the old frontier) is incomparable with
    the newer completed lineage: the graph retains the conflict
    (never latest-wins by arrival, never stale-erasure of the old
    witness); a genuine descendant of BOTH resolves."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    # An issued-but-OUTSTANDING old call.
    h.issue("c-old", (CAUSAL_ROOT_FACT,))
    b1 = h.read("c-b1", "A base.\n")
    assert node(h.graph_ok(), "A.md").digest == _sha("A base.\n")
    # A newer completed read under the base.
    h.issue("c-new", (b1, CAUSAL_ROOT_FACT))
    new_occ = h.read("c-new", "A new.\n")
    g = h.graph_ok()
    assert node(g, "A.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "A.md").digest == _sha("A new.\n")
    # The delayed older result completes NOW (anchored under the old
    # frontier): incomparable with the newer lineage.
    old_occ = h.read("c-old", "A base.\n")
    g2 = h.graph_ok()
    assert node(g2, "A.md").status is CurrentGraphStatus.BLOCKED_CONFLICT
    assert {"c-b1", "c-new", "c-old"} <= {o.call_id for o in h.state.occurrences}
    # A genuine descendant of both resolves.
    h.issue("c-merge", (old_occ, new_occ, CAUSAL_ROOT_FACT))
    merge_occ = h.read("c-merge", "A merged.\n")
    g3 = h.graph_ok()
    assert node(g3, "A.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g3, "A.md").digest == _sha("A merged.\n")
    assert node(g3, "A.md").witnesses == (merge_occ,)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_f_late_trusted_receipt_establishes_edge(mode: AdmissionMode, endpoint: str) -> None:
    """F: two incomparable unissued A reads conflict; a LATE trusted
    receipt for one of them establishes the ACTUAL frozen parent
    edge (a descendant of the other).  Currentness follows the
    actual DAG, never arrival order: the receipted read is the
    descendant and its content becomes current."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    o = h.read("c-o", "A o.\n")
    n = h.read("c-n", "A n.\n")
    g = h.graph_ok()
    assert node(g, "A.md").status is CurrentGraphStatus.BLOCKED_CONFLICT
    receipt = register_receipt(
        h.state, h.ns, "c-o", endpoint, "exec_command", READ_ARGS, (n, CAUSAL_ROOT_FACT), h.revision
    )
    assert receipt.outcome is CausalHistoryOutcome.ACCEPTED
    h.state, h.revision = receipt.state, receipt.revision_after
    g2 = h.graph_ok()
    assert node(g2, "A.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g2, "A.md").digest == _sha("A o.\n")
    assert node(g2, "A.md").witnesses == (o,)


# ---------------------------------------------------------------------------
# E (offgraph/background): possessed-off-graph and boundaryless-group
# background references never silently govern reachability
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_offgraph_and_background_references_never_govern(
    mode: AdmissionMode, endpoint: str
) -> None:
    """E: a possessed STANDALONE source (B) referenced by NO current
    derivation is off-graph: it stays current but unreachable, its
    outgoing reference G is never scanned or joined, and it
    contributes no edge or candidate.  A current boundaryless
    opaque group (A, D) whose member D is independently offgraph
    cannot certify its target H either: the certificate is emitted
    with NOT_INDEPENDENTLY_REACHABLE and nothing is joined.
    Off-graph and greedy-background references never silently
    govern."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `A.md` first.")
    # B is a standalone possessed source on its OWN path (never a
    # member of any group): possessed, current, but referenced by
    # no current derivation -> off-graph.
    h.read("c-b", "See `G.md`.\n", cmd="cat B.md")
    # (A, D) is one boundaryless opaque group: A is referenced by
    # the root, D is independently offgraph (referenced by
    # nothing).
    h.read("c-ad", "See `H.md`.\n", cmd="cat A.md D.md")
    # ACTUAL 018-e currentness preconditions before any graph
    # oracle: B current-known standalone; A/D current as ONE
    # boundaryless opaque group.
    ov = overlay_of(h)
    assert path_status(ov, "B.md") is CurrentnessStatus.CURRENT_KNOWN
    assert path_status(ov, "A.md") is CurrentnessStatus.CURRENT_OPAQUE
    assert path_status(ov, "D.md") is CurrentnessStatus.CURRENT_OPAQUE
    b_occ = next(o for o in h.state.occurrences if o.call_id == "c-b")
    ad_occ = next(o for o in h.state.occurrences if o.call_id == "c-ad")
    assert b_occ.proof.segments[0].member_digest == _sha("See `G.md`.\n")
    ad_segment = ad_occ.proof.segments[0]
    assert ad_segment.member_positions == (0, 1)
    assert ad_segment.member_digest is None  # boundaryless: no per-member bytes
    assert ad_segment.digest == _sha("See `H.md`.\n")
    g = h.graph_ok()
    # The off-graph standalone source is honest: current supplier
    # retained, listed unreachable.
    assert node(g, "A.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert g.unreachable_current_paths == ("B.md",)
    b_supplier = next(
        s for s in g.suppliers if s.kind is CurrentGraphSupplierKind.SOURCE and s.path == "B.md"
    )
    assert b_supplier.witnesses == (b_occ.occurrence_id,)
    # B's own reference is never scanned (off-graph source): G, D
    # and H are not joined, B contributes no edge or candidate.
    assert "G.md" not in node_paths(g)
    assert "D.md" not in node_paths(g)
    assert not any(edge.source == "B.md" for edge in g.edges)
    assert g.candidates == ()
    # The current opaque (A, D) group cannot certify H while D is
    # independently offgraph: the certificate is emitted but
    # unusable, and H never joins.
    cert = cert_for_members(g, ("A.md", "D.md"))
    assert cert is not None and cert.usable is False
    assert CurrentGraphReason.NOT_INDEPENDENTLY_REACHABLE in cert.reasons
    assert cert.resolved_target == "H.md"
    group_supplier = next(
        s
        for s in g.suppliers
        if s.kind is CurrentGraphSupplierKind.GROUP and s.members == ("A.md", "D.md")
    )
    assert group_supplier.witnesses == (ad_occ.occurrence_id,)
    assert "H.md" not in node_paths(g)
    assert all(cert_.usable is False for cert_ in g.certificates)


# ---------------------------------------------------------------------------
# E (depth recompute): the least complete AND/OR depth is recomputed
# after withdrawals (the shallow route withdraws, the deeper
# surviving route governs)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_e_depth_recomputed_after_withdrawal(mode: AdmissionMode, endpoint: str) -> None:
    """E: T is reachable through the shallow route root->S1->T
    (depth 2) and the deeper route root->L1->M->T (depth 3); the
    node takes the LEAST (2).  A completed-empty S1 withdraws the
    shallow route and the least complete depth is RECOMPUTED from
    the surviving route (3), while the surviving route itself keeps
    its depths."""
    h = Hist(mode, endpoint)
    h.boot_root("Read `S1.md` and `L1.md` first.")
    s1 = h.read("c-s1", "See `T.md`.", cmd="cat S1.md")
    h.read("c-l1", "See `M.md`.", cmd="cat L1.md")
    h.read("c-m1", "See `T.md`.", cmd="cat M.md")
    g = h.graph_ok()
    assert node(g, "S1.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "L1.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "M.md").status is CurrentGraphStatus.CURRENT_KNOWN
    assert node(g, "M.md").depth == 2
    assert node(g, "T.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g, "T.md").depth == 2
    assert edges_from(g, "S1.md") == {"T.md"}
    assert edges_from(g, "M.md") == {"T.md"}

    # Withdraw the shallow route (completed empty S1).
    h.issue("c-s2", (s1, CAUSAL_ROOT_FACT), json.dumps({"cmd": "cat S1.md"}))
    h.read("c-s2", "", cmd="cat S1.md")
    g2 = h.graph_ok()
    assert node(g2, "S1.md").status is CurrentGraphStatus.CURRENT_EMPTY
    assert "T.md" not in edges_from(g2, "S1.md")
    assert node(g2, "T.md").status is CurrentGraphStatus.DISCOVERED_UNACQUIRED
    assert node(g2, "T.md").depth == 3
    assert node(g2, "M.md").depth == 2
