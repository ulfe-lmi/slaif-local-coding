"""018-a: public bounded graph observation — the acquisition-to-graph seam.

PUBLIC composition tests for ``observe_graph`` / ``observe_graph_batch``:
the accepted 017 observation (under the 017 package's own ceilings,
metadata only) feeds the single evidenced root/workspace binding, the
GRAPH-OWNED cumulative source ledger (accounted BEFORE any graph-owned
copy/retention), bounded acquisition, the reference scan and the
deterministic closure.  All payloads are inline known-synthetic; no
model, native, client or service facility is started, and no fixture
lifecycle or historical seed is involved.

Seam law locked here: a 017 COMPLETE read always carries members
normalized under its observed context, so public non-attribution
manifests as NON-COMPLETE member-unproven reads (never as a
COMPLETE-but-unattributable node); the derived-context law makes a
context-less request acquire exactly what an evidenced-context request
would; cross-surface dedup keeps ONE node for an identical
call/result/path/digest positive on both surfaces (READ primary);
process regions are reconstructed ONLY from the original piece
carriers (re-derivation agreement is asserted on the payload itself).

The product is pure and inert: the no-host-IO control monkeypatches the
host facilities and fails on any attempt (a harness failure is
distinguished from a product failure).
"""

from __future__ import annotations

import builtins
import copy
import hashlib
import json
import os
import socket
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import pytest

from slaif_local_coding.constitution.bundles import (
    EMPTY_SOURCE_SHA256,
    GraphBounds,
    GraphLimitation,
    GraphNamespace,
    GraphOutcome,
    GraphRequest,
    GraphSnapshot,
    NodeStatus,
    SourceDocument,
    SourceKind,
    make_graph_namespace,
    observe_graph,
    observe_graph_batch,
)
from slaif_local_coding.constitution.bundles.observation_models import (
    CharSpan,
    Limitation,
    PathContext,
    ProcessOutcome,
    ReadOutcome,
)
from slaif_local_coding.constitution.bundles.observe import observe_request
from slaif_local_coding.constitution.cache import RequestIdentity

IDENT = RequestIdentity(
    principal="synthetic-principal",
    session="synthetic-session",
    repository="synthetic-repository",
    route="synthetic-route",
)
FINGERPRINT = "abcdef0123456789" * 4
WORKSPACE = "/work"
ROOT_TEXT = "See [a](docs/A.md)."
A_BODY = "See B.md."
B_BODY = "leaf"


def ident(**overrides: str) -> RequestIdentity:
    base = dict(
        principal="synthetic-principal",
        session="synthetic-session",
        repository="synthetic-repository",
        route="synthetic-route",
    )
    base.update(overrides)
    return RequestIdentity(**base)


def make_ns(
    bounds: GraphBounds | None = None,
    workspace: str = WORKSPACE,
    **identity: str,
) -> GraphNamespace:
    return make_graph_namespace(
        ident(**identity),
        model_identity="synthetic-model",
        config_fingerprint=FINGERPRINT,
        workspace=workspace,
        bounds=bounds,
    )


# --- Known-synthetic payload helpers ------------------------------------


def root_item(label: str, content: str) -> dict[str, Any]:
    return {
        "role": "user",
        "content": [
            {
                "type": "input_text",
                "text": (
                    f"# AGENTS.md instructions for {label}\n\n"
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


def poll_call(cid: str, session: int) -> dict[str, Any]:
    return {
        "type": "function_call",
        "call_id": cid,
        "name": "write_stdin",
        "arguments": json.dumps({"session_id": session, "chars": ""}),
    }


def frame_legacy(chunk: str, body: str) -> str:
    """Legacy tool wrapper final (any chunk token, no token line)."""
    return (
        f"Chunk ID: {chunk}\nWall time: 0.0000 seconds\nProcess exited with code 0\nOutput:\n{body}"
    )


def frame_legacy_code(chunk: str, body: str, code: int) -> str:
    return (
        f"Chunk ID: {chunk}\n"
        f"Wall time: 0.0000 seconds\n"
        f"Process exited with code {code}\n"
        f"Output:\n{body}"
    )


def frame_legacy_truncated(chunk: str, body: str) -> str:
    return (
        f"Chunk ID: {chunk}\n"
        f"Wall time: 0.0000 seconds\n"
        f"Process exited with code 0\n"
        f"Truncated: true\n"
        f"Output:\n{body}"
    )


def frame_native_final(chunk: str, body: str, tokens: int | None = None) -> str:
    """Pinned native final; ``tokens`` adds the token line (legacy-malformed)."""
    head = f"Chunk ID: {chunk}\nWall time: 0.0000 seconds\nProcess exited with code 0\n"
    if tokens is not None:
        head += f"Original token count: {tokens}\n"
    return f"{head}Output:\n{body}"


def frame_native_running(session: int, chunk: str, body: str, tokens: int) -> str:
    return (
        f"Chunk ID: {chunk}\n"
        f"Wall time: 0.0000 seconds\n"
        f"Process running with session ID {session}\n"
        f"Original token count: {tokens}\n"
        f"Output:\n{body}"
    )


def responses_payload(*items: dict[str, Any]) -> dict[str, Any]:
    return {"model": "synthetic-bundle-model", "input": list(items)}


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
    return {"model": "synthetic-bundle-model", "messages": messages}


# --- Snapshot projection helpers -----------------------------------------


def node_map(snap: GraphSnapshot) -> dict[str, SourceDocument]:
    return {node.path: node for node in snap.nodes}


def edge_set(snap: GraphSnapshot) -> set[tuple[str, str]]:
    return {(edge.from_path, edge.to_path) for edge in snap.edges}


def semantic(snap: GraphSnapshot) -> tuple[Any, ...]:
    """R3 semantic projection: provenance coordinates are excluded.

    Request order legitimately changes ``request_index`` / carrier
    locations (provenance is never renumbered to normalize order), so
    order-independence is asserted on this projection; byte-equal
    serialized snapshots are asserted for identical input order.
    """
    return (
        snap.outcome,
        frozenset((n.path, n.digest, n.status.value) for n in snap.nodes),
        frozenset((e.from_path, e.to_path) for e in snap.edges),
        tuple(sorted(snap.missing)),
        snap.root_digest,
        tuple(
            sorted((u.bundle_digest, tuple(u.possible_origins)) for u in snap.unresolved_origins)
        ),
        tuple(sorted(c.value for c in snap.conflicts)),
    )


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _carrier(payload: dict[str, Any], location: str) -> str:
    """Resolve one exact 017 location pointer into the payload."""
    if location.startswith("$.input["):
        rest = location[len("$.input[") :]
        index_s, _sep, tail = rest.partition("]")
        item = payload["input"][int(index_s)]
        if tail == "":
            out: str = item["output"]
            return out
        j_s, _sep2, tail2 = tail[len(".content[") :].partition("]")
        assert tail2 == ""
        text: str = item["content"][int(j_s)]["text"]
        return text
    index_s, _sep3, _tail3 = location[len("$.messages[") :].partition("]")
    content: str = payload["messages"][int(index_s)]["content"]
    return content


CLOSURE_ITEMS = (
    root_item(WORKSPACE, ROOT_TEXT),
    exec_call("call-a", "cat docs/A.md"),
    out_item("call-a", frame_legacy("c1", A_BODY)),
    exec_call("call-b", "cat docs/B.md"),
    out_item("call-b", frame_legacy("c2", B_BODY)),
)


class TestRootAndWorkspaceBinding:
    """The single evidenced root and workspace bind the whole batch."""

    def test_root_read_closure_public(self) -> None:
        payload = responses_payload(*CLOSURE_ITEMS)
        original = copy.deepcopy(payload)
        snap = observe_graph(payload, make_ns())
        nodes = node_map(snap)
        # Input invariance: the payload is never mutated.
        assert payload == original
        assert snap.outcome is GraphOutcome.COMPLETE
        assert set(nodes) == {"AGENTS.md", "docs/A.md", "docs/B.md"}
        assert nodes["AGENTS.md"].kind is SourceKind.ROOT
        assert nodes["docs/A.md"].kind is SourceKind.READ
        assert nodes["docs/B.md"].kind is SourceKind.READ
        assert edge_set(snap) == {
            ("AGENTS.md", "docs/A.md"),
            ("docs/A.md", "docs/B.md"),
        }
        assert snap.root_digest == sha256_hex(ROOT_TEXT)
        assert nodes["docs/A.md"].digest == sha256_hex(A_BODY)
        assert nodes["docs/B.md"].digest == sha256_hex(B_BODY)
        assert snap.request_count == 1
        assert snap.documents_inspected == 3
        # Re-derivation agreement: each node digest equals the sha256 of
        # the exact payload substring at its reported occurrence span.
        for path, expected in (
            ("AGENTS.md", ROOT_TEXT),
            ("docs/A.md", A_BODY),
            ("docs/B.md", B_BODY),
        ):
            node = nodes[path]
            assert len(node.occurrences) == 1
            occ = node.occurrences[0]
            carrier = _carrier(payload, occ.carrier_location)
            assert carrier[occ.span.start : occ.span.end] == expected
            assert sha256_hex(expected) == node.digest

    def test_arrival_order_semantic_equal_and_deterministic(self) -> None:
        ns = make_ns()
        root_first = responses_payload(*CLOSURE_ITEMS)
        root_last = responses_payload(
            *CLOSURE_ITEMS[1:],
            CLOSURE_ITEMS[0],
        )
        assert semantic(observe_graph(root_first, ns)) == semantic(observe_graph(root_last, ns))
        # Determinism: identical input order yields byte-equal records.
        assert (
            observe_graph(root_first, ns).model_dump() == observe_graph(root_first, ns).model_dump()
        )

    def test_root_after_dependencies_batch(self) -> None:
        ns = make_ns()
        snap = observe_graph_batch(
            (
                GraphRequest(
                    payload=responses_payload(
                        exec_call("call-a", "cat docs/A.md"),
                        out_item("call-a", frame_legacy("c1", A_BODY)),
                    ),
                    endpoint="responses",
                ),
                GraphRequest(
                    payload=responses_payload(
                        exec_call("call-b", "cat docs/B.md"),
                        out_item("call-b", frame_legacy("c2", B_BODY)),
                    ),
                    endpoint="responses",
                ),
                GraphRequest(
                    payload=responses_payload(root_item(WORKSPACE, ROOT_TEXT)),
                    endpoint="responses",
                ),
            ),
            ns,
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        assert edge_set(snap) == {
            ("AGENTS.md", "docs/A.md"),
            ("docs/A.md", "docs/B.md"),
        }
        assert snap.request_count == 3
        assert semantic(snap) == semantic(observe_graph(responses_payload(*CLOSURE_ITEMS), ns))

    def test_chat_batch_with_responses_root(self) -> None:
        ns = make_ns()
        snap = observe_graph_batch(
            (
                GraphRequest(
                    payload=responses_payload(root_item(WORKSPACE, ROOT_TEXT)),
                    endpoint="responses",
                ),
                GraphRequest(
                    payload=chat_payload(
                        ("call-a", "cat docs/A.md", frame_legacy("c1", A_BODY)),
                        ("call-b", "cat docs/B.md", frame_legacy("c2", B_BODY)),
                    ),
                    endpoint="chat",
                ),
            ),
            ns,
        )
        nodes = node_map(snap)
        assert snap.outcome is GraphOutcome.COMPLETE
        assert set(nodes) == {"AGENTS.md", "docs/A.md", "docs/B.md"}
        assert edge_set(snap) == {
            ("AGENTS.md", "docs/A.md"),
            ("docs/A.md", "docs/B.md"),
        }
        assert nodes["docs/A.md"].digest == sha256_hex(A_BODY)
        assert snap.request_count == 2

    def test_single_chat_without_root_is_no_root(self) -> None:
        snap = observe_graph(
            chat_payload(("call-a", "cat docs/A.md", frame_legacy("c1", A_BODY))),
            make_ns(),
            endpoint="chat",
        )
        assert snap.outcome is GraphOutcome.NO_ROOT
        assert GraphLimitation.NO_ROOT in snap.conflicts
        assert snap.nodes == ()
        assert snap.root_digest is None

    def test_responses_reads_without_root_are_no_root(self) -> None:
        snap = observe_graph(
            responses_payload(
                exec_call("call-a", "cat docs/A.md"),
                out_item("call-a", frame_legacy("c1", A_BODY)),
            ),
            make_ns(),
        )
        assert snap.outcome is GraphOutcome.NO_ROOT
        assert GraphLimitation.NO_ROOT in snap.conflicts
        assert snap.nodes == ()

    def test_competing_roots_refused(self) -> None:
        ns = make_ns()
        snap = observe_graph_batch(
            (
                GraphRequest(
                    payload=responses_payload(root_item(WORKSPACE, "root one.")),
                    endpoint="responses",
                ),
                GraphRequest(
                    payload=responses_payload(root_item(WORKSPACE, "root two.")),
                    endpoint="responses",
                ),
            ),
            ns,
        )
        assert snap.outcome is GraphOutcome.ROOT_CONFLICT
        assert GraphLimitation.COMPETING_ROOTS in snap.conflicts
        assert snap.nodes == ()

    def test_equal_roots_dedup_with_both_occurrences(self) -> None:
        ns = make_ns()
        root = root_item(WORKSPACE, ROOT_TEXT)
        snap = observe_graph_batch(
            (
                GraphRequest(payload=responses_payload(root), endpoint="responses"),
                GraphRequest(
                    payload=responses_payload(
                        root,
                        exec_call("call-a", "cat docs/A.md"),
                        out_item("call-a", frame_legacy("c1", A_BODY)),
                    ),
                    endpoint="responses",
                ),
            ),
            ns,
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        root_node = node_map(snap)["AGENTS.md"]
        assert len(root_node.occurrences) == 2
        assert root_node.digest == sha256_hex(ROOT_TEXT)

    def test_root_context_mismatch_refused(self) -> None:
        snap = observe_graph(
            responses_payload(*CLOSURE_ITEMS),
            make_ns(),
            context=PathContext(workspace="/other"),
        )
        assert snap.outcome is GraphOutcome.ROOT_CONFLICT
        assert GraphLimitation.ROOT_CONTEXT_MISMATCH in snap.conflicts

    def test_root_context_agree_is_complete(self) -> None:
        snap = observe_graph(
            responses_payload(*CLOSURE_ITEMS),
            make_ns(),
            context=PathContext(workspace=WORKSPACE),
        )
        assert snap.outcome is GraphOutcome.COMPLETE

    def test_namespace_workspace_mismatch_refused(self) -> None:
        snap = observe_graph(responses_payload(*CLOSURE_ITEMS), make_ns(workspace="/work2"))
        assert snap.outcome is GraphOutcome.ROOT_CONFLICT
        assert GraphLimitation.WORKSPACE_MISMATCH in snap.conflicts

    def test_noncanonical_root_scope_label_unproven(self) -> None:
        snap = observe_graph(responses_payload(root_item("/work/", "x")), make_ns())
        assert snap.outcome is GraphOutcome.WORKSPACE_UNPROVEN
        assert GraphLimitation.WORKSPACE_UNPROVEN in snap.conflicts

    def test_root_self_reference_has_zero_depth(self) -> None:
        snap = observe_graph(
            responses_payload(root_item(WORKSPACE, "See [self](AGENTS.md).")),
            make_ns(),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        self_edges = [
            e for e in snap.edges if (e.from_path, e.to_path) == ("AGENTS.md", "AGENTS.md")
        ]
        assert len(self_edges) == 1
        assert self_edges[0].depth == 0
        assert snap.max_depth == 0

    def test_derived_context_none_acquires_like_evidenced(self) -> None:
        """The design-promised derived-root scope: a context-less request
        is re-observed under the single evidenced root scope and acquires
        exactly what an evidenced-context request would."""
        ns = make_ns()
        payload = responses_payload(*CLOSURE_ITEMS)
        derived = observe_graph(payload, ns)
        evidenced = observe_graph(payload, ns, context=PathContext(workspace=WORKSPACE))
        assert derived.outcome is GraphOutcome.COMPLETE
        assert evidenced.outcome is GraphOutcome.COMPLETE
        assert semantic(derived) == semantic(evidenced)
        nodes = node_map(derived)
        assert nodes["docs/A.md"].digest == sha256_hex(A_BODY)
        assert nodes["docs/B.md"].digest == sha256_hex(B_BODY)


class TestAcquisitionSeams:
    """The accepted 017 seam: which observations acquire sources here."""

    def _snap(self, *items: dict[str, Any], root: str = "plain root.") -> GraphSnapshot:
        return observe_graph(responses_payload(root_item(WORKSPACE, root), *items), make_ns())

    def test_legacy_read_only_positive(self) -> None:
        # Non-6-hex chunk token: legacy positive, native unparseable.
        snap = self._snap(
            exec_call("call-a", "cat docs/A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
            root="See [a](docs/A.md).",
        )
        node = node_map(snap)["docs/A.md"]
        assert snap.outcome is GraphOutcome.COMPLETE
        assert node.kind is SourceKind.READ
        assert node.digest == sha256_hex(A_BODY)
        assert len(node.occurrences) == 1

    def test_pinned_native_with_token_line_is_process_only(self) -> None:
        # Legacy-malformed (the token line), independently earned process
        # region: PROCESS primary, no veto, no read-surface node.
        snap = self._snap(
            exec_call("call-c", "cat docs/C.md"),
            out_item("call-c", frame_native_final("c30f21", "C-content", tokens=5)),
            root="See [c](docs/C.md).",
        )
        node = node_map(snap)["docs/C.md"]
        assert snap.outcome is GraphOutcome.COMPLETE
        assert node.kind is SourceKind.PROCESS
        assert node.digest == sha256_hex("C-content")
        assert len(node.occurrences) == 1

    def test_intersection_frame_without_token_line_deduped_once(self) -> None:
        # A 6-hex chunk final WITHOUT the token line is positive on BOTH
        # surfaces.  Prove the overlapping-positive premise on the
        # accepted 017 report FIRST, then the graph deduplicates that
        # one physical occurrence: ONE node, READ primary, ONE
        # occurrence (the two carrier-evidence records collapse on
        # identical call/result/path/digest).
        payload = responses_payload(
            root_item(WORKSPACE, "See [a](docs/A.md)."),
            exec_call("call-a", "cat docs/A.md"),
            out_item("call-a", frame_native_final("3d4e5f", A_BODY)),
        )
        report = observe_request(payload, PathContext(workspace=WORKSPACE), None, "responses")
        assert report.reads[0].outcome is ReadOutcome.COMPLETE
        assert report.processes[0].outcome is ProcessOutcome.COMPLETE
        assert (
            report.reads[0].bundle_digest == report.processes[0].bundle_digest == sha256_hex(A_BODY)
        )
        snap = observe_graph(payload, make_ns())
        node = node_map(snap)["docs/A.md"]
        assert snap.outcome is GraphOutcome.COMPLETE
        assert node.kind is SourceKind.READ
        assert node.digest == sha256_hex(A_BODY)
        assert len(node.occurrences) == 1

    def test_chunked_native_singleton_from_original_carriers(self) -> None:
        body0, body1 = "chunk-zero\n", "chunk-one\n"
        payload = responses_payload(
            root_item(WORKSPACE, "See [s](docs/S.md)."),
            exec_call("call-e", "cat docs/S.md"),
            out_item("call-e", frame_native_running(9203, "0a1b2c", body0, 8)),
            poll_call("call-p", 9203),
            out_item("call-p", frame_native_final("3d4e5f", body1, 8)),
        )
        snap = observe_graph(payload, make_ns())
        node = node_map(snap)["docs/S.md"]
        assert snap.outcome is GraphOutcome.COMPLETE
        assert node.kind is SourceKind.PROCESS
        assert node.digest == sha256_hex(body0 + body1)
        # Two occurrences on the TWO ORIGINAL piece carriers (never a
        # virtual joined string).
        assert len(node.occurrences) == 2
        assert len({o.carrier_location for o in node.occurrences}) == 2
        joined = "".join(
            _carrier(payload, o.carrier_location)[o.span.start : o.span.end]
            for o in sorted(node.occurrences, key=lambda o: o.piece_index)
        )
        assert sha256_hex(joined) == node.digest

    def test_empty_singleton_is_empty_digest_node(self) -> None:
        snap = self._snap(
            exec_call("call-e", "cat docs/E.md"),
            out_item("call-e", frame_legacy("ce", "")),
            root="See [e](docs/E.md).",
        )
        node = node_map(snap)["docs/E.md"]
        assert snap.outcome is GraphOutcome.COMPLETE
        assert node.status is NodeStatus.ACQUIRED_EMPTY
        assert node.digest == EMPTY_SOURCE_SHA256
        assert node.byte_length == 0
        assert node.char_length == 0
        # The empty node contributes no outgoing edges.
        assert edge_set(snap) == {("AGENTS.md", "docs/E.md")}

    @pytest.mark.parametrize(
        ("build", "cmd", "expected_read", "expected_proc"),
        [
            (
                lambda body: frame_legacy_code("c1", body, 1),
                "cat docs/N.md",
                (ReadOutcome.NONZERO_EXIT, (Limitation.NONZERO_EXIT,)),
                None,
            ),
            (
                # A VALID six-lower-hex native chunk: this case is the
                # native nonzero control (not another legacy-only one).
                lambda body: (
                    "Chunk ID: 3d4e5f\n"
                    "Wall time: 0.0000 seconds\n"
                    "Process exited with code 1\n"
                    "Output:\n" + body
                ),
                "cat docs/N.md",
                (ReadOutcome.NONZERO_EXIT, (Limitation.NONZERO_EXIT,)),
                (ProcessOutcome.NONZERO_EXIT, ()),
            ),
            (
                lambda body: frame_legacy_truncated("c1", body),
                "cat docs/N.md",
                (ReadOutcome.TRUNCATED, (Limitation.TRUNCATED_OUTPUT,)),
                None,
            ),
            (
                lambda body: (
                    "Chunk ID: 3d4e5f\n"
                    "Wall time: 0.0000 seconds\n"
                    "Process exited with code 0\n"
                    "Original token count: 9\n"
                    "Output:\n" + body + "\n... 456 bytes omitted ..."
                ),
                "cat docs/N.md",
                (ReadOutcome.UNSUPPORTED, (Limitation.MALFORMED_WRAPPER,)),
                (ProcessOutcome.TRUNCATED, (Limitation.PROCESS_TRUNCATED,)),
            ),
        ],
        ids=["legacy-nonzero", "native-nonzero", "legacy-truncated", "native-truncated-marker"],
    )
    def test_non_acquiring_terminal_outcomes_contribute_no_source(
        self,
        build: Any,
        cmd: str,
        expected_read: tuple[ReadOutcome, tuple[Limitation, ...]],
        expected_proc: tuple[ProcessOutcome, tuple[Limitation, ...]] | None,
    ) -> None:
        # Predecessor 017 outcomes under the evidenced workspace first
        # (the native cases carry the valid six-hex native chunk); then
        # the public graph acquires nothing from any of them.
        payload = responses_payload(exec_call("call-n", cmd), out_item("call-n", build("N-body")))
        report = observe_request(payload, PathContext(workspace=WORKSPACE), None, "responses")
        assert len(report.reads) == 1
        assert report.reads[0].outcome is expected_read[0]
        assert report.reads[0].reasons == expected_read[1]
        if expected_proc is None:
            assert report.processes == ()
        else:
            assert len(report.processes) == 1
            assert report.processes[0].outcome is expected_proc[0]
            assert report.processes[0].reasons == expected_proc[1]
        snap = self._snap(exec_call("call-n", cmd), out_item("call-n", build("N-body")))
        assert snap.outcome is GraphOutcome.COMPLETE
        assert set(node_map(snap)) == {"AGENTS.md"}
        assert edge_set(snap) == set()
        assert snap.unresolved_origins == ()

    def test_running_only_contributes_no_source(self) -> None:
        snap = self._snap(
            exec_call("call-r", "cat docs/R.md"),
            out_item("call-r", frame_native_running(9203, "0a1b2c", "so far\n", 8)),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        assert set(node_map(snap)) == {"AGENTS.md"}

    def test_missing_origin_unpaired_contributes_no_source(self) -> None:
        # A result with no issued call is unpaired: non-acquiring.
        snap = self._snap(out_item("orphan", frame_legacy("c1", A_BODY)))
        assert snap.outcome is GraphOutcome.COMPLETE
        assert set(node_map(snap)) == {"AGENTS.md"}
        assert snap.unresolved_origins == ()

    def test_member_unproven_read_contributes_no_source(self) -> None:
        # Public non-attribution: the member cannot be attributed to the
        # evidenced workspace, so the read is non-COMPLETE and the graph
        # acquires nothing (no source, no edge).  A 017 COMPLETE read
        # always carries normalized members, so a COMPLETE-but-unattributable
        # node is structurally unreachable at this public entry.
        snap = observe_graph(
            responses_payload(
                root_item(WORKSPACE, "plain root."),
                exec_call("call-x", "cat ../outside.md"),
                out_item("call-x", frame_legacy("c1", "outside")),
            ),
            make_ns(),
            context=PathContext(workspace=WORKSPACE),
        )
        assert set(node_map(snap)) == {"AGENTS.md"}
        assert edge_set(snap) == set()

    def test_absolute_member_under_evidenced_context_acquires(self) -> None:
        snap = observe_graph(
            responses_payload(
                root_item(WORKSPACE, "plain root."),
                exec_call("call-x", "cat /work/docs/A.md"),
                out_item("call-x", frame_legacy("c1", A_BODY)),
            ),
            make_ns(),
            context=PathContext(workspace=WORKSPACE),
        )
        node = node_map(snap).get("docs/A.md")
        assert node is not None
        assert node.digest == sha256_hex(A_BODY)

    def test_multi_member_bundle_not_split(self) -> None:
        body = "M1|body|M2"
        snap = self._snap(
            exec_call("call-m", "cat docs/M1.md docs/M2.md"),
            out_item("call-m", frame_legacy("cm", body)),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        assert set(node_map(snap)) == {"AGENTS.md"}
        assert len(snap.unresolved_origins) == 1
        origin = snap.unresolved_origins[0]
        assert origin.possible_origins == ("docs/M1.md", "docs/M2.md")
        # Whole-bundle digest, never per-member hashes.
        assert origin.bundle_digest == sha256_hex(body)
        assert edge_set(snap) == set()

    def test_same_directory_mixed_eligible_background_unresolved(self) -> None:
        # One eligible .md plus one background file in the SAME directory:
        # the whole boundaryless bundle stays unresolved (no member
        # split) even though the root explicitly references the eligible
        # member — same-directory equality is NOT ownership/eligibility
        # proof (lean/greedy admission is b-scope).
        body = "A-content|next|See NEXT.md."
        snap = self._snap(
            exec_call("call-m", "cat A.md notes.txt"),
            out_item("call-m", frame_legacy("cm", body)),
            root="See [a](A.md).",
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        nodes = node_map(snap)
        # A.md is reachable by reference but content-unacquired:
        # discovered-missing with NO fabricated digest/kind/lengths.
        assert set(nodes) == {"AGENTS.md", "A.md"}
        a = nodes["A.md"]
        assert a.status is NodeStatus.DISCOVERED_CONTENT_MISSING
        assert a.digest is None
        assert a.kind is None
        assert a.byte_length is None
        assert len(snap.unresolved_origins) == 1
        origin = snap.unresolved_origins[0]
        assert origin.possible_origins == ("A.md", "notes.txt")
        assert origin.bundle_digest == sha256_hex(body)
        # The NEXT.md reference inside the unsegmented bundle body is
        # RETAINED as the origin's candidate evidence — but no NEXT.md
        # node or edge is fabricated from a shared-directory shortcut.
        assert any(c.target_chars == "NEXT.md" for c in origin.candidates)
        assert "NEXT.md" not in nodes
        assert edge_set(snap) == {("AGENTS.md", "A.md")}

    def test_version_conflict_selects_no_version(self) -> None:
        snap = self._snap(
            exec_call("ra", "cat docs/A.md"),
            out_item("ra", frame_legacy("ra", "version-1")),
            exec_call("rb", "cat docs/A.md"),
            out_item("rb", frame_legacy("rb", "version-2")),
            root="See [a](docs/A.md).",
        )
        node = node_map(snap)["docs/A.md"]
        assert snap.outcome is GraphOutcome.VERSION_CONFLICT
        assert node.status is NodeStatus.VERSION_CONFLICT
        assert node.digest is None
        assert node.kind is None
        assert GraphLimitation.VERSION_CONFLICT in snap.conflicts

    def test_mismatched_positive_seam_is_typed_conflict(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Internal seam fault injection: ONE physical call/result
        # occurrence is positive on BOTH surfaces, but the process
        # member is FORGED.md (same call/carriers/region; a synthetic
        # internal helper fault — NOT external payload forgery, an
        # authentication bypass, or an actual 017 defect).  The
        # overlapping-positive baseline is proven first; the mismatched
        # positive is a typed VERSION_CONFLICT that acquires NO source
        # or edge from that occurrence (no good-looking selection).
        import slaif_local_coding.constitution.bundles.graph_observation as go

        frame = (
            "Chunk ID: 3d4e5f\n"
            "Wall time: 0.0100 seconds\n"
            "Process exited with code 0\n"
            "Output:\nSee NEXT.md."
        )
        payload = responses_payload(
            root_item(WORKSPACE, "See A.md."),
            exec_call("same-physical-call", "cat A.md"),
            out_item("same-physical-call", frame),
        )
        report = observe_request(payload, PathContext(workspace=WORKSPACE), None, "responses")
        assert report.reads[0].outcome is ReadOutcome.COMPLETE
        assert report.processes[0].outcome is ProcessOutcome.COMPLETE
        assert report.reads[0].bundle_digest == report.processes[0].bundle_digest
        baseline = observe_graph(payload, make_ns())
        assert baseline.outcome is GraphOutcome.COMPLETE
        assert sum(1 for n in baseline.nodes if n.path == "A.md") == 1

        original = observe_request  # same object as go.observe_request

        def mismatch(*args: Any, **kwargs: Any) -> Any:
            r = original(*args, **kwargs)
            if not r.processes:
                return r
            p = r.processes[0]
            member = p.requested_members[0].model_copy(
                update={"raw": "FORGED.md", "normalized": "FORGED.md"}
            )
            p = p.model_copy(
                update={
                    "requested_members": (member,),
                    "proven_executed": ("FORGED.md",),
                }
            )
            return r.model_copy(update={"processes": (p,) + r.processes[1:]})

        monkeypatch.setattr(go, "observe_request", mismatch)
        result = observe_graph(payload, make_ns())
        paths = [n.path for n in result.nodes]
        edges = [(e.from_path, e.to_path) for e in result.edges]
        assert result.outcome is GraphOutcome.VERSION_CONFLICT
        assert "FORGED.md" not in paths
        assert not any(a in ("A.md", "FORGED.md") for a, _b in edges)
        assert GraphLimitation.VERSION_CONFLICT in result.conflicts

    def test_consistent_whole_bundle_overlap_is_one_record(self) -> None:
        # ONE physical boundaryless multi-member occurrence (6-hex
        # native final WITHOUT token line: both surfaces COMPLETE, no
        # per-file hash earned) is ONE graph source record: the
        # whole-bundle digest, ordered members and original interval
        # are retained with read-primary dedup — no per-file split,
        # hash or admission policy is invented.
        frame = (
            "Chunk ID: 3d4e5f\n"
            "Wall time: 0.0100 seconds\n"
            "Process exited with code 0\n"
            "Output:\nSee NEXT.md."
        )
        payload = responses_payload(
            root_item(WORKSPACE, "See A.md."),
            exec_call("same-physical-call", "cat A.md B.md"),
            out_item("same-physical-call", frame),
        )
        report = observe_request(payload, PathContext(workspace=WORKSPACE), None, "responses")
        assert report.reads[0].outcome is ReadOutcome.COMPLETE
        assert report.processes[0].outcome is ProcessOutcome.COMPLETE
        assert report.reads[0].bundle_digest == report.processes[0].bundle_digest
        assert len(report.reads[0].requested_members) == 2
        assert len(report.processes[0].requested_members) == 2
        snap = observe_graph(payload, make_ns())
        assert snap.outcome is GraphOutcome.COMPLETE
        assert len(snap.unresolved_origins) == 1
        record = snap.unresolved_origins[0]
        assert record.bundle_digest == report.reads[0].bundle_digest
        assert tuple(record.possible_origins) == ("A.md", "B.md")
        assert record.request_index == 0
        acquired = {n.path for n in snap.nodes if n.status is NodeStatus.ACQUIRED}
        assert "A.md" not in acquired and "B.md" not in acquired

    def test_mismatched_whole_bundle_order_is_typed_conflict(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Internal seam fault: the SAME boundaryless multi-member
        # occurrence is positive on BOTH surfaces, but the process
        # ordered members are REVERSED (synthetic internal helper
        # fault — NOT external forgery or a 017 defect).  The whole-
        # bundle proofs disagree: that occurrence acquires NO source
        # and NO candidate record, and the snapshot refuses ready
        # with a typed VERSION_CONFLICT.
        import slaif_local_coding.constitution.bundles.graph_observation as go

        frame = (
            "Chunk ID: 3d4e5f\n"
            "Wall time: 0.0100 seconds\n"
            "Process exited with code 0\n"
            "Output:\nSee NEXT.md."
        )
        payload = responses_payload(
            root_item(WORKSPACE, "See A.md."),
            exec_call("same-physical-call", "cat A.md B.md"),
            out_item("same-physical-call", frame),
        )
        report = observe_request(payload, PathContext(workspace=WORKSPACE), None, "responses")
        assert report.reads[0].outcome is ReadOutcome.COMPLETE
        assert report.processes[0].outcome is ProcessOutcome.COMPLETE
        assert len(report.processes[0].requested_members) == 2
        baseline = observe_graph(payload, make_ns())
        assert baseline.outcome is GraphOutcome.COMPLETE
        assert len(baseline.unresolved_origins) == 1

        original = observe_request  # same object as go.observe_request

        def mismatch(*args: Any, **kwargs: Any) -> Any:
            r = original(*args, **kwargs)
            if not r.processes:
                return r
            p = r.processes[0]
            p = p.model_copy(
                update={
                    "requested_members": tuple(reversed(p.requested_members)),
                    "proven_executed": tuple(reversed(p.proven_executed)),
                }
            )
            return r.model_copy(update={"processes": (p,) + r.processes[1:]})

        monkeypatch.setattr(go, "observe_request", mismatch)
        result = observe_graph(payload, make_ns())
        assert result.outcome is GraphOutcome.VERSION_CONFLICT
        assert result.unresolved_origins == ()
        assert GraphLimitation.VERSION_CONFLICT in result.conflicts
        acquired = {n.path for n in result.nodes if n.status is NodeStatus.ACQUIRED}
        assert "A.md" not in acquired and "B.md" not in acquired

    def test_equal_bytes_different_original_spans_is_typed_conflict(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Internal seam fault: both surfaces are positive with EQUAL
        # exact source bytes, digest and path, but the ORIGINAL
        # carrier intervals disagree (equal text at different
        # occurrences is not the deduplicated proof).  Typed
        # conflict; that occurrence acquires no source or edge.
        import slaif_local_coding.constitution.bundles.graph_observation as go

        digest = hashlib.sha256(b"SAME.md").hexdigest()
        frame = (
            "Chunk ID: 3d4e5f\n"
            "Wall time: 0.0100 seconds\n"
            "Process exited with code 0\n"
            "Output:\nSAME.mdSAME.md"
        )
        payload = responses_payload(
            root_item(WORKSPACE, "See A.md."),
            exec_call("same-physical-call", "cat A.md"),
            out_item("same-physical-call", frame),
        )
        report = observe_request(payload, PathContext(workspace=WORKSPACE), None, "responses")
        assert report.reads[0].outcome is ReadOutcome.COMPLETE
        assert report.processes[0].outcome is ProcessOutcome.COMPLETE
        baseline = observe_graph(payload, make_ns())
        assert baseline.outcome is GraphOutcome.COMPLETE
        assert sum(1 for n in baseline.nodes if n.path == "A.md") == 1

        original = observe_request  # same object as go.observe_request

        def mismatch(*args: Any, **kwargs: Any) -> Any:
            r = original(*args, **kwargs)
            if not r.reads or not r.processes:
                return r
            rd, p = r.reads[0], r.processes[0]
            if rd.content_span is None:
                return r  # context-derivation probe pass: unattributable
            start = rd.content_span.start
            rd = rd.model_copy(
                update={
                    "content_span": CharSpan(start=start, end=start + 7),
                    "bundle_digest": digest,
                    "member_digests": (digest,),
                }
            )
            p = p.model_copy(
                update={
                    "region_piece_spans": (CharSpan(start=start + 7, end=start + 14),),
                    "proven_region_char_length": 7,
                    "bundle_digest": digest,
                    "member_digests": (digest,),
                }
            )
            return r.model_copy(
                update={"reads": (rd,) + r.reads[1:], "processes": (p,) + r.processes[1:]}
            )

        monkeypatch.setattr(go, "observe_request", mismatch)
        result = observe_graph(payload, make_ns())
        assert result.outcome is GraphOutcome.VERSION_CONFLICT
        assert not any(e.from_path == "A.md" for e in result.edges)
        assert GraphLimitation.VERSION_CONFLICT in result.conflicts

    def test_mixed_member_count_positive_proof_is_typed_conflict(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Internal seam fault: the SAME physical occurrence proves a
        # single member (A.md) on the read surface while the process
        # surface claims an ordered A+B whole bundle (no per-file hash
        # is fabricated).  The member counts disagree: a typed
        # conflict, NO source and NO candidate record from that
        # occurrence, refused ready.
        import slaif_local_coding.constitution.bundles.graph_observation as go

        frame = (
            "Chunk ID: 3d4e5f\n"
            "Wall time: 0.0100 seconds\n"
            "Process exited with code 0\n"
            "Output:\nSee NEXT.md."
        )
        payload = responses_payload(
            root_item(WORKSPACE, "See A.md."),
            exec_call("same-physical-call", "cat A.md"),
            out_item("same-physical-call", frame),
        )
        report = observe_request(payload, PathContext(workspace=WORKSPACE), None, "responses")
        assert report.reads[0].outcome is ReadOutcome.COMPLETE
        assert report.processes[0].outcome is ProcessOutcome.COMPLETE
        assert len(report.reads[0].requested_members) == 1
        baseline = observe_graph(payload, make_ns())
        assert baseline.outcome is GraphOutcome.COMPLETE
        assert sum(1 for n in baseline.nodes if n.path == "A.md") == 1

        original = observe_request  # same object as go.observe_request

        def mismatch(*args: Any, **kwargs: Any) -> Any:
            r = original(*args, **kwargs)
            if not r.processes:
                return r
            p = r.processes[0]
            b = p.requested_members[0].model_copy(update={"raw": "B.md", "normalized": "B.md"})
            p = p.model_copy(
                update={
                    "requested_members": p.requested_members + (b,),
                    "proven_executed": ("A.md", "B.md"),
                    "member_digests": (None, None),
                    "distinct_member_count": 2,
                    "slot_width": 2,
                    "final_cat_member_indexes": (0, 1),
                }
            )
            return r.model_copy(update={"processes": (p,) + r.processes[1:]})

        monkeypatch.setattr(go, "observe_request", mismatch)
        result = observe_graph(payload, make_ns())
        assert result.outcome is GraphOutcome.VERSION_CONFLICT
        assert result.unresolved_origins == ()
        assert not any(e.from_path == "A.md" for e in result.edges)
        assert GraphLimitation.VERSION_CONFLICT in result.conflicts

    def test_process_complete_without_region_contributes_no_source(self) -> None:
        # A valid 017 process completion whose command grammar earns NO
        # source region (sleep-bearing, non-read): the process is
        # COMPLETE, but the graph acquires no source or edge (no
        # fabricated region, no metadata-only hash).
        payload = responses_payload(
            root_item(WORKSPACE, "plain root."),
            exec_call("call-s", "sleep 1"),
            out_item("call-s", frame_native_final("3d4e5f", "slept")),
        )
        report = observe_request(payload, PathContext(workspace=WORKSPACE), None, "responses")
        assert report.processes[0].outcome is ProcessOutcome.COMPLETE
        assert report.processes[0].proven_region_char_length is None
        assert report.processes[0].bundle_digest is None
        snap = observe_graph(payload, make_ns())
        assert snap.outcome is GraphOutcome.COMPLETE
        assert set(node_map(snap)) == {"AGENTS.md"}
        assert edge_set(snap) == set()

    def test_chat_earned_fixture_chunked_native_batch(self) -> None:
        # Chat process carrier through the public batch, reusing the
        # EARNED known-synthetic 017 Chat fixture (assistant
        # tool_calls plus tool messages; the chain poll is issued in a
        # LATER assistant message — the 017 structural causality law).
        # All four explicit/derived-context x root-first/last
        # combinations acquire the chunked singleton in the same bounded
        # namespace as the legitimate Responses root, with occurrences
        # on the two ORIGINAL piece carriers.
        fixture_path = (
            Path(__file__).parent
            / "fixtures"
            / "cache_bundles"
            / "v1"
            / "process_chat_running_complete.json"
        )
        fixture_bytes = fixture_path.read_bytes()
        assert (
            hashlib.sha256(fixture_bytes).hexdigest()
            == "0c232a600319035ba02908d38dfc4085fa2a35e3c710d09b2d1f8a4b01c8ef0b"
        )
        chat = json.loads(fixture_bytes)
        joined_body = "Chat first chunk line\r\nChat final chunk line\r\n"
        expected_digest = sha256_hex(joined_body)
        # Predecessor: the earned 017 Chat chain is COMPLETE with two
        # pieces and the joined region digest.
        report = observe_request(chat, PathContext(workspace=WORKSPACE), None, "chat")
        assert report.processes[0].outcome is ProcessOutcome.COMPLETE
        assert len(report.processes[0].pieces) == 2
        assert report.processes[0].bundle_digest == expected_digest
        root = responses_payload(root_item(WORKSPACE, "See A.md."))
        for explicit_context in (False, True):
            ctx = PathContext(workspace=WORKSPACE) if explicit_context else None
            for root_first in (True, False):
                requests = (
                    GraphRequest(payload=root, endpoint="responses", context=ctx),
                    GraphRequest(payload=chat, endpoint="chat", context=ctx),
                )
                if not root_first:
                    requests = (requests[1], requests[0])
                snap = observe_graph_batch(requests, make_ns())
                node = node_map(snap)["A.md"]
                assert snap.outcome is GraphOutcome.COMPLETE, (
                    explicit_context,
                    root_first,
                )
                assert snap.request_count == 2
                assert node.kind is SourceKind.PROCESS
                assert node.digest == expected_digest
                assert len(node.occurrences) == 2
                assert len({o.carrier_location for o in node.occurrences}) == 2
                joined = "".join(
                    _carrier(chat, o.carrier_location)[o.span.start : o.span.end]
                    for o in sorted(node.occurrences, key=lambda o: o.piece_index)
                )
                assert sha256_hex(joined) == node.digest

    def test_chat_same_turn_poll_chain_conflict_contributes_no_source(self) -> None:
        # The 017 structural causality law at the graph level: a chain
        # poll issued in the SAME assistant message as the exec (its
        # position never follows the initial result) is a typed
        # PROCESS_CHAIN_CONFLICT — non-acquiring, no fabricated source.
        body0, body1 = "chunk-zero\n", "chunk-one\n"
        running = frame_native_running(9203, "0a1b2c", body0, 8)
        final = frame_native_final("3d4e5f", body1)
        chat = {
            "model": "synthetic-bundle-model",
            "messages": [
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "call-e",
                            "type": "function",
                            "function": {
                                "name": "exec_command",
                                "arguments": json.dumps({"cmd": "cat A.md"}),
                            },
                        },
                        {
                            "id": "call-p",
                            "type": "function",
                            "function": {
                                "name": "write_stdin",
                                "arguments": json.dumps({"session_id": 9203, "chars": ""}),
                            },
                        },
                    ],
                },
                {"role": "tool", "tool_call_id": "call-e", "content": running},
                {"role": "tool", "tool_call_id": "call-p", "content": final},
            ],
        }
        report = observe_request(chat, PathContext(workspace=WORKSPACE), None, "chat")
        assert report.processes[0].outcome is ProcessOutcome.UNSUPPORTED
        assert Limitation.PROCESS_CHAIN_CONFLICT in report.processes[0].reasons
        # A Chat request alone carries no root; pair it with the
        # legitimate Responses root in one bounded batch.
        snap = observe_graph_batch(
            (
                GraphRequest(
                    payload=responses_payload(root_item(WORKSPACE, "See A.md.")),
                    endpoint="responses",
                ),
                GraphRequest(payload=chat, endpoint="chat"),
            ),
            make_ns(),
        )
        assert snap.outcome is GraphOutcome.COMPLETE
        nodes = node_map(snap)
        assert "A.md" not in nodes or nodes["A.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING
        if "A.md" in nodes:
            assert nodes["A.md"].digest is None
        assert not any(a == "A.md" for a, _b in edge_set(snap))


class TestUnrelatedOffGraph:
    """An acquired but unreachable document expands nothing until the
    fixed point reaches it, then it is reconsidered."""

    def test_off_graph_document_contributes_no_edges(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, "root only."),
            exec_call("call-z", "cat docs/Z.md"),
            out_item("call-z", frame_legacy("cz", "See B2.md.")),
        )
        snap = observe_graph(payload, make_ns())
        assert snap.outcome is GraphOutcome.COMPLETE
        nodes = node_map(snap)
        assert set(nodes) == {"AGENTS.md", "docs/Z.md"}
        # Z is unreachable: its reference mints no edge and no missing node.
        assert edge_set(snap) == set()
        assert snap.missing == ()
        assert "docs/B2.md" not in nodes

    def test_off_graph_document_reconsidered_once_reachable(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, "See [z](docs/Z.md)."),
            exec_call("call-z", "cat docs/Z.md"),
            out_item("call-z", frame_legacy("cz", "See B2.md.")),
        )
        snap = observe_graph(payload, make_ns())
        assert snap.outcome is GraphOutcome.COMPLETE
        assert edge_set(snap) == {
            ("AGENTS.md", "docs/Z.md"),
            ("docs/Z.md", "docs/B2.md"),
        }
        assert snap.missing == ("docs/B2.md",)
        assert node_map(snap)["docs/B2.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING


class TestNamespaceIsolation:
    """Every identity/bounds/workspace component binds the namespace keys."""

    def test_each_identity_component_changes_the_scoped_key(self) -> None:
        base = make_ns()
        for override in (
            {"principal": "other-principal"},
            {"session": "other-session"},
            {"repository": "other-repository"},
            {"route": "other-route"},
        ):
            assert make_ns(**cast(Any, override)).scoped_key != base.scoped_key
        assert (
            make_graph_namespace(
                IDENT,
                model_identity="other-model",
                config_fingerprint=FINGERPRINT,
                workspace=WORKSPACE,
            ).scoped_key
            != base.scoped_key
        )
        assert (
            make_graph_namespace(
                IDENT,
                model_identity="synthetic-model",
                config_fingerprint="b" * 64,
                workspace=WORKSPACE,
            ).scoped_key
            != base.scoped_key
        )
        assert make_ns(workspace="/work3").scoped_key != base.scoped_key

    def test_bounds_bind_into_the_pre_root_key(self) -> None:
        base = make_ns()
        bounded = make_ns(GraphBounds(max_nodes=10))
        assert bounded.namespace_key != base.namespace_key
        assert bounded.scoped_key != base.scoped_key

    def test_payload_cannot_assert_identity(self) -> None:
        # The same payload observes COMPLETE under a DIFFERENT session:
        # identity comes only from the supplied namespace object.
        payload = responses_payload(*CLOSURE_ITEMS)
        assert observe_graph(payload, make_ns()).outcome is GraphOutcome.COMPLETE
        assert (
            observe_graph(payload, make_ns(session="other-session")).outcome
            is GraphOutcome.COMPLETE
        )

    def test_explicit_bounds_must_equal_namespace_bounds(self) -> None:
        ns = make_ns()
        request = GraphRequest(
            payload=responses_payload(root_item(WORKSPACE, "r")), endpoint="responses"
        )
        with pytest.raises(ValueError, match="bounds must equal"):
            observe_graph_batch((request,), ns, bounds=GraphBounds(max_nodes=10))
        # At the namespace's own bounds the identical batch passes.
        assert observe_graph_batch((request,), ns).outcome is GraphOutcome.COMPLETE


class TestBudgetsPublic:
    """At-limit / one-over for the graph budgets the public path owns."""

    def test_batch_requests_at_limit_and_one_over(self) -> None:
        root = root_item(WORKSPACE, "r")
        ns = make_ns(GraphBounds(max_requests=1))
        single = observe_graph_batch(
            (GraphRequest(payload=responses_payload(root), endpoint="responses"),), ns
        )
        assert single.outcome is GraphOutcome.COMPLETE
        double = observe_graph_batch(
            (
                GraphRequest(payload=responses_payload(root), endpoint="responses"),
                GraphRequest(payload=responses_payload(root), endpoint="responses"),
            ),
            ns,
        )
        assert double.outcome is GraphOutcome.OVER_BOUND
        assert GraphLimitation.BATCH_OVER_BOUND in double.conflicts

    def test_document_budget_counts_duplicates_across_requests(self) -> None:
        read = (
            exec_call("call-a", "cat docs/A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
        )
        ns = make_ns(GraphBounds(max_documents=2))
        at_limit = observe_graph_batch(
            (
                GraphRequest(
                    payload=responses_payload(root_item(WORKSPACE, "r")),
                    endpoint="responses",
                ),
                GraphRequest(payload=responses_payload(*read), endpoint="responses"),
            ),
            ns,
        )
        assert at_limit.outcome is GraphOutcome.COMPLETE
        assert at_limit.documents_inspected == 2
        one_over = observe_graph_batch(
            (
                GraphRequest(
                    payload=responses_payload(root_item(WORKSPACE, "r")),
                    endpoint="responses",
                ),
                GraphRequest(payload=responses_payload(*read), endpoint="responses"),
                GraphRequest(payload=responses_payload(*read), endpoint="responses"),
            ),
            ns,
        )
        assert one_over.outcome is GraphOutcome.OVER_BOUND
        assert GraphLimitation.DOCUMENT_OVER_BOUND in one_over.conflicts
        assert one_over.nodes == ()

    def test_single_source_bytes_at_limit_and_one_over(self) -> None:
        ns = make_ns(GraphBounds(max_single_source_bytes=10))
        at_limit = observe_graph(
            responses_payload(
                root_item(WORKSPACE, "r"),
                exec_call("k1", "cat docs/F1.md"),
                out_item("k1", frame_legacy("f1", "0123456789")),
            ),
            ns,
        )
        assert at_limit.outcome is GraphOutcome.COMPLETE
        one_over = observe_graph(
            responses_payload(
                root_item(WORKSPACE, "r"),
                exec_call("k1", "cat docs/F1.md"),
                out_item("k1", frame_legacy("f1", "01234567890")),
            ),
            ns,
        )
        assert one_over.outcome is GraphOutcome.OVER_BOUND
        assert GraphLimitation.SOURCE_OVER_BOUND in one_over.conflicts

    def test_total_inspected_bytes_cumulative_at_limit_and_one_over(self) -> None:
        big = "x" * 400
        items = [
            root_item(WORKSPACE, "r"),  # 1 byte
            exec_call("k1", "cat docs/F1.md"),
            out_item("k1", frame_legacy("f1", big)),
            exec_call("k2", "cat docs/F2.md"),
            out_item("k2", frame_legacy("f2", big)),
            exec_call("k3", "cat docs/F3.md"),
            out_item("k3", frame_legacy("f3", big)),
        ]
        # 1 + 3 * 400 = 1201 inspected bytes.
        at_limit = observe_graph(
            responses_payload(*items),
            make_ns(GraphBounds(max_total_inspected_source_bytes=1201)),
        )
        assert at_limit.outcome is GraphOutcome.COMPLETE
        assert at_limit.source_bytes_inspected == 1201
        one_over = observe_graph(
            responses_payload(*items),
            make_ns(GraphBounds(max_total_inspected_source_bytes=1200)),
        )
        assert one_over.outcome is GraphOutcome.OVER_BOUND
        assert GraphLimitation.TOTAL_SOURCE_OVER_BOUND in one_over.conflicts
        assert one_over.nodes == ()

    def test_per_document_candidates_at_limit_and_one_over(self) -> None:
        two_refs = "See [a](docs/A1.md) [b](docs/B1.md)."
        three_refs = "See [a](docs/A1.md) [b](docs/B1.md) [c](docs/C1.md)."
        at_limit = observe_graph(
            responses_payload(root_item(WORKSPACE, two_refs)),
            make_ns(GraphBounds(max_reference_candidates_per_document=2)),
        )
        assert at_limit.outcome is GraphOutcome.COMPLETE
        assert at_limit.candidates_per_document_max == 2
        one_over = observe_graph(
            responses_payload(root_item(WORKSPACE, three_refs)),
            make_ns(GraphBounds(max_reference_candidates_per_document=2)),
        )
        assert one_over.outcome is GraphOutcome.OVER_BOUND
        assert GraphLimitation.CANDIDATES_PER_DOCUMENT_OVER_BOUND in one_over.conflicts

    def test_total_candidates_across_documents_counts_unsupported(self) -> None:
        a_body = "See [b](docs/B1.md) [c](docs/C1.md) and https://example.com/x.md."
        items = (
            root_item(WORKSPACE, "See [a](docs/A.md)."),
            exec_call("call-a", "cat docs/A.md"),
            out_item("call-a", frame_legacy("c1", a_body)),
        )
        # 1 (root) + 3 (A: two links + one external) = 4 candidates.
        at_limit = observe_graph(
            responses_payload(*items),
            make_ns(GraphBounds(max_reference_candidates_total=4)),
        )
        assert at_limit.outcome is GraphOutcome.COMPLETE
        assert at_limit.candidates_total == 4
        one_over = observe_graph(
            responses_payload(*items),
            make_ns(GraphBounds(max_reference_candidates_total=3)),
        )
        assert one_over.outcome is GraphOutcome.OVER_BOUND
        assert GraphLimitation.CANDIDATES_TOTAL_OVER_BOUND in one_over.conflicts


class TestDiagnosticsPublic:
    """The TOTAL emitted fixed diagnostics are bounded at public finalization."""

    def test_conflicts_alone_at_limit(self) -> None:
        root = "See [outside](/work-other/A.md) [escape](../B.md)."
        at_limit = observe_graph(
            responses_payload(root_item(WORKSPACE, root)),
            make_ns(GraphBounds(max_diagnostics=2)),
        )
        assert at_limit.outcome is GraphOutcome.COMPLETE
        assert GraphLimitation.PATH_OUTSIDE_WORKSPACE in at_limit.conflicts
        assert GraphLimitation.PATH_TRAVERSAL in at_limit.conflicts
        one_over = observe_graph(
            responses_payload(root_item(WORKSPACE, root)),
            make_ns(GraphBounds(max_diagnostics=1)),
        )
        assert one_over.outcome is GraphOutcome.OVER_BOUND
        assert one_over.conflicts == (GraphLimitation.DIAGNOSTICS_FULL,)
        assert one_over.observation_limitations == ()

    def test_graph_conflicts_plus_observation_limitations_sum(self) -> None:
        # One graph path conflict + two distinct unpaired observation
        # limitations: the TOTAL, not the per-field count, is bounded.
        payload = responses_payload(
            root_item(WORKSPACE, "See [escape](../B.md)."),
            exec_call("no-result", "cat docs/A.md"),
            out_item("orphan", frame_legacy("c1", A_BODY)),
        )
        at_limit = observe_graph(payload, make_ns(GraphBounds(max_diagnostics=3)))
        assert at_limit.outcome is GraphOutcome.COMPLETE
        assert len(at_limit.conflicts) == 1
        assert len(at_limit.observation_limitations) == 2
        one_over = observe_graph(payload, make_ns(GraphBounds(max_diagnostics=2)))
        assert one_over.outcome is GraphOutcome.OVER_BOUND
        assert one_over.conflicts == (GraphLimitation.DIAGNOSTICS_FULL,)
        assert one_over.observation_limitations == ()

    def test_observation_limitations_alone_at_limit(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, "plain root."),
            exec_call("no-result", "cat docs/A.md"),
            out_item("orphan", frame_legacy("c1", A_BODY)),
        )
        at_limit = observe_graph(payload, make_ns(GraphBounds(max_diagnostics=2)))
        assert at_limit.outcome is GraphOutcome.COMPLETE
        assert len(at_limit.observation_limitations) == 2
        assert at_limit.conflicts == ()


class TestDeterminismAndInvariance:
    def test_byte_equal_serialization_on_identical_input(self) -> None:
        ns = make_ns()
        payload = responses_payload(*CLOSURE_ITEMS)
        first = observe_graph(payload, ns).model_dump()
        second = observe_graph(payload, ns).model_dump()
        assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)

    def test_reordered_requests_semantic_equal(self) -> None:
        ns = make_ns()
        root = GraphRequest(
            payload=responses_payload(root_item(WORKSPACE, ROOT_TEXT)), endpoint="responses"
        )
        reads = GraphRequest(
            payload=responses_payload(
                exec_call("call-a", "cat docs/A.md"),
                out_item("call-a", frame_legacy("c1", A_BODY)),
            ),
            endpoint="responses",
        )
        assert semantic(observe_graph_batch((root, reads), ns)) == semantic(
            observe_graph_batch((reads, root), ns)
        )

    def test_payload_values_unchanged(self) -> None:
        payload = responses_payload(*CLOSURE_ITEMS)
        original = copy.deepcopy(payload)
        observe_graph(payload, make_ns())
        observe_graph(
            payload,
            make_ns(),
            context=PathContext(workspace=WORKSPACE),
        )
        assert payload == original


class TestPrivacyAndSafety:
    def test_operational_repr_never_echoes_private_values_or_content(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat docs/A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
            exec_call("call-m", "cat docs/M1.md docs/M2.md"),
            out_item("call-m", frame_legacy("cm", "M1|body|M2")),
        )
        snap = observe_graph(payload, make_ns())
        request = GraphRequest(payload=payload, endpoint="responses")
        rendered = " ".join(
            [str(snap), repr(snap), str(snap.namespace), repr(request), str(request)]
        )
        for secret in (
            "synthetic-principal",
            "synthetic-session",
            "synthetic-repository",
            "synthetic-route",
            "synthetic-model",
            FINGERPRINT,
            WORKSPACE,
            ROOT_TEXT,
            A_BODY,
            "M1|body|M2",
        ):
            assert secret not in rendered

    def test_invalid_input_errors_are_fixed_and_safe(self) -> None:
        canary = "SECRET-CANARY-9f3a"
        with pytest.raises(ValueError) as excinfo:
            GraphRequest(payload={"model": canary, "input": []}, endpoint="not-an-endpoint")
        message = str(excinfo.value)
        assert canary not in message
        assert "not-an-endpoint" not in message
        with pytest.raises(ValueError):
            observe_graph("not-a-dict", make_ns())  # type: ignore[arg-type]

    def test_snapshot_records_are_frozen(self) -> None:
        snap = observe_graph(responses_payload(*CLOSURE_ITEMS), make_ns())
        with pytest.raises(ValueError):
            snap.outcome = GraphOutcome.NO_ROOT

    def test_private_bundle_proof_repr_never_echoes_source_or_id(self) -> None:
        # The internal whole-bundle proof record carries raw source
        # bytes and the private call ID; its operational
        # representation suppresses both while the internal typed
        # data is untouched.
        import slaif_local_coding.constitution.bundles.graph_observation as go

        source_canary = "SYNTHETIC-SOURCE-CANARY-7f3"
        id_canary = "SYNTHETIC-ID-CANARY-7f3"
        proof = go._BundleProof(
            "read",
            0,
            id_canary,
            "$.input[2].output",
            "$.input[1]",
            ("A.md", "B.md"),
            "a" * 64,
            source_canary,
            ("A.md", "B.md"),
            (),
        )
        rendered = repr(proof) + " " + str(proof)
        assert source_canary not in rendered
        assert id_canary not in rendered
        assert proof.content == source_canary  # internal data untouched
        assert proof.call_id == id_canary


class TestPurity:
    """The public path is pure: any host IO attempt fails the test."""

    def _forbid_io(self) -> tuple[list[str], Callable[[], None]]:
        """Patch the host facilities; return (attempts, restore).

        The restore callable is explicit so the test restores BEFORE any
        exception propagates: Python traceback formatting touches
        ``linecache``/``os.stat`` and would otherwise collide with the
        forbidden patches.
        """

        attempts: list[str] = []

        def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            attempts.append("forbidden_io_attempt")
            raise AssertionError("forbidden_io_attempt")

        targets = [
            (builtins, "open"),
            (Path, "open"),
            (Path, "resolve"),
            (Path, "stat"),
            (Path, "exists"),
            (Path, "read_text"),
            (Path, "read_bytes"),
            (os, "stat"),
            (os, "system"),
            (subprocess, "Popen"),
            (subprocess, "run"),
            (socket, "socket"),
            (socket, "create_connection"),
        ]
        saved = [(owner, name, getattr(owner, name)) for owner, name in targets]

        def restore() -> None:
            for owner, name, value in saved:
                setattr(owner, name, value)

        for owner, name, _value in saved:
            setattr(owner, name, forbidden)
        return attempts, restore

    def test_full_composition_makes_no_host_io(self) -> None:
        attempts, restore = self._forbid_io()
        try:
            body0, body1 = "chunk-zero\n", "chunk-one\n"
            payload = responses_payload(
                root_item(WORKSPACE, ROOT_TEXT),
                exec_call("call-a", "cat docs/A.md"),
                out_item("call-a", frame_legacy("c1", A_BODY)),
                exec_call("call-e", "cat docs/S.md"),
                out_item("call-e", frame_native_running(9203, "0a1b2c", body0, 8)),
                poll_call("call-p", 9203),
                out_item("call-p", frame_native_final("3d4e5f", body1, 8)),
            )
            original = copy.deepcopy(payload)
            snap = observe_graph(payload, make_ns())
            assert attempts == []
            assert snap.outcome is GraphOutcome.COMPLETE
            nodes = node_map(snap)
            # docs/B.md is referenced by docs/A.md's own content: it is
            # discovered (missing), never fabricated.
            assert set(nodes) == {"AGENTS.md", "docs/A.md", "docs/B.md", "docs/S.md"}
            assert nodes["docs/B.md"].status is NodeStatus.DISCOVERED_CONTENT_MISSING
            assert payload == original
        finally:
            restore()

    def test_chat_batch_makes_no_host_io(self) -> None:
        attempts, restore = self._forbid_io()
        try:
            snap = observe_graph_batch(
                (
                    GraphRequest(
                        payload=responses_payload(root_item(WORKSPACE, ROOT_TEXT)),
                        endpoint="responses",
                    ),
                    GraphRequest(
                        payload=chat_payload(
                            ("call-a", "cat docs/A.md", frame_legacy("c1", A_BODY))
                        ),
                        endpoint="chat",
                    ),
                ),
                make_ns(),
            )
            assert attempts == []
            assert snap.outcome is GraphOutcome.COMPLETE
        finally:
            restore()
