"""018-b: public bundle-proof bridge — the inert pure proof surface.

PUBLIC composition tests for ``observe_bundle_proofs`` /
``observe_bundle_proof``: the accepted 017 observation (re-derived
under the namespace's ACTUAL effective ``ObservationBounds``) feeds
the single evidenced root/workspace binding (the 018-a law) and the
bridge-owned cumulative source/proof ledgers, earning immutable
SELF-CONTAINED bundle source proofs — whole (017-attributed
boundaryless region) and partitioned (the new finite unique-marker
law over the full proven output).  All payloads are inline
known-synthetic; no model, native, client or service facility is
started, and no fixture lifecycle or historical seed is involved.

Locked law surface: requested versus proven-executed member
occurrences stay distinct; the proof carries the exact aggregate
source TEXT (self-contained, never dependent on caller payload
survival) with the complete original carrier/piece spans, the
actual exec/poll call association and numeric call/result
positions, and the original role/root-authority binding; the
same-occurrence consistency law compares the full common proof
signature BEFORE retention (mismatch acquires nothing); a negative
old surface never vetoes an independently earned positive; every
inspected source body and owned reconstruction is preflighted under
the ACTUAL effective cumulative bounds BEFORE any owned copy
(at-limit stays at-limit, the first over-bound is a fixed typed
refusal); private IDs and source content are suppressed in every
operational representation.

The product is pure and inert: the no-host-IO control monkeypatches
the host facilities and fails on any attempt.
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
from typing import Any

import pytest

from slaif_local_coding.constitution.bundles import (
    BUNDLE_PROOF_CONTRACT_VERSION,
    EMPTY_SOURCE_SHA256,
    BundleLimitation,
    BundleMarkerRole,
    BundlePiece,
    BundleProof,
    BundleProofBounds,
    BundleProofKind,
    BundleProofNamespace,
    BundleProofOutcome,
    BundleProofSnapshot,
    BundleSegment,
    BundleSourceRole,
    BundleSurface,
    GraphBounds,
    GraphRequest,
    make_bundle_proof_namespace,
    observe_bundle_proof,
    observe_bundle_proofs,
)
from slaif_local_coding.constitution.bundles.compound_reads import READ_PLAN_GRAMMAR
from slaif_local_coding.constitution.bundles.literal_loops import LOOP_GRAMMAR
from slaif_local_coding.constitution.bundles.observation_models import (
    OBSERVER_VERSION,
    READ_GRAMMAR,
    CharSpan,
    NormalizedPath,
    ObservationBounds,
    PathContext,
    PathForm,
)
from slaif_local_coding.constitution.cache import RequestIdentity

IDENT = RequestIdentity(
    principal="synthetic-principal",
    session="synthetic-session",
    repository="synthetic-repository",
    route="synthetic-route",
)
FINGERPRINT = "abcdef0123456789" * 4
WORKSPACE = "/work"
ROOT_TEXT = "Read A.md and B.md."
A_BODY = "alpha"
B_BODY = "beta"
C_BODY = "gamma"


def make_ns(
    bounds: BundleProofBounds | None = None,
    graph_bounds: GraphBounds | None = None,
    observation_bounds: ObservationBounds | None = None,
    workspace: str = WORKSPACE,
    **identity: str,
) -> BundleProofNamespace:
    base = dict(
        principal="synthetic-principal",
        session="synthetic-session",
        repository="synthetic-repository",
        route="synthetic-route",
    )
    base.update(identity)
    return make_bundle_proof_namespace(
        RequestIdentity(**base),
        model_identity="synthetic-model",
        config_fingerprint=FINGERPRINT,
        workspace=workspace,
        bounds=bounds,
        graph_bounds=graph_bounds,
        observation_bounds=observation_bounds,
    )


def forced_version_ns(field: str, value: str) -> BundleProofNamespace:
    """A valid-key namespace carrying an UNSUPPORTED version field.

    Direct model construction recomputes the scoped keys from the
    supplied versions, so the key pair is consistent — the entry's
    supported-version refusal is the only check that can catch it.
    """
    ns = make_ns()
    data = ns.model_dump(mode="python")
    data[field] = value
    from slaif_local_coding.constitution.bundles.bundle_proof_models import (
        _canonical_namespace_fields,
    )

    raw = _canonical_namespace_fields(
        data["principal"],
        data["session"],
        data["repository"],
        data["route"],
        data["model_identity"],
        data["config_fingerprint"],
        data["bundle_proof_version"],
        data["observation_version"],
        data["graph_version"],
        ns.bounds,
        ns.graph_bounds,
        ns.observation_bounds,
    )
    data["namespace_key"] = hashlib.sha256(raw).hexdigest()
    data["scoped_key"] = hashlib.sha256(
        (data["namespace_key"] + "\0" + ns.workspace).encode()
    ).hexdigest()
    return BundleProofNamespace(**data)


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
    """Pinned native final; ``tokens`` adds the token line (legacy-
    malformed on the legacy surface, accepted by the native surface).

    ``chunk`` must be exactly six lowercase hex digits (the native
    chunk-ID grammar)."""
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


def batch(payload: dict[str, Any], endpoint: str = "responses") -> tuple[GraphRequest, ...]:
    return (GraphRequest(payload=payload, endpoint=endpoint, context=None),)


def single(payload: dict[str, Any], endpoint: str = "responses") -> Any:
    return observe_bundle_proof(payload, make_ns(), endpoint=endpoint)


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _span(start: int, end: int) -> CharSpan:
    return CharSpan(start=start, end=end)


def _resolved(path: str) -> NormalizedPath:
    return NormalizedPath(raw=path, form=PathForm.RELATIVE, normalized=path)


def _test_piece(call_id: str) -> BundlePiece:
    return BundlePiece(
        piece_index=0,
        carrier_location="$.input[2]",
        char_span=_span(0, 3),
        char_length=3,
        byte_length=3,
        call_id=call_id,
        call_location="$.input[1]",
        call_position=1,
        result_position=2,
    )


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


# --- Whole legacy read proofs ---------------------------------------------


class TestWholeLegacyRead:
    """The whole (boundaryless 017-attributed region) read proof."""

    def test_single_read_whole_responses(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
        )
        original = copy.deepcopy(payload)
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert payload == original
        assert snap.outcome is BundleProofOutcome.COMPLETE
        assert len(snap.bundles) == 1
        proof = snap.bundles[0]
        assert proof.kind is BundleProofKind.WHOLE
        assert proof.surface is BundleSurface.READ
        assert proof.endpoint == "responses"
        assert proof.source_role is BundleSourceRole.FILE_TOOL_RESULT
        assert proof.grammar == READ_GRAMMAR
        assert proof.command_digest is not None and len(proof.command_digest) == 64
        assert proof.source_text == A_BODY
        assert proof.source_digest == sha256_hex(A_BODY)
        assert proof.source_char_length == len(A_BODY)
        assert proof.source_byte_length == len(A_BODY.encode("utf-8"))
        # Root-authority binding (scoping only, no authority conferred).
        assert proof.root_path == "AGENTS.md"
        assert proof.root_digest == sha256_hex(ROOT_TEXT)
        # Requested versus proven-executed (one occurrence each).
        assert len(proof.requested_members) == 1
        assert proof.requested_members[0].normalized == "A.md"
        assert proof.proven_executed == ("A.md",)
        assert proof.distinct_member_count == 1
        # The exact single original carrier and its structural positions.
        assert len(proof.pieces) == 1
        piece = proof.pieces[0]
        assert piece.carrier_location == "$.input[2]"
        assert piece.call_location == "$.input[1]"
        assert piece.call_id == "call-a"
        assert piece.call_position == 1
        assert piece.result_position == 2
        assert piece.char_span.start == len(
            "Chunk ID: c1\nWall time: 0.0000 seconds\nProcess exited with code 0\nOutput:\n"
        )
        assert piece.char_span.end - piece.char_span.start == len(A_BODY)
        assert piece.byte_length == len(A_BODY.encode("utf-8"))
        # The whole region: one segment owning the one attributable
        # occurrence (per-file digest earned).
        assert len(proof.segments) == 1
        segment = proof.segments[0]
        assert segment.member_positions == (0,)
        assert segment.digest == sha256_hex(A_BODY)
        assert segment.member_digest == segment.digest
        assert segment.piece_spans[0] is not None
        assert (
            _carrier(payload, piece.carrier_location)[piece.char_span.start : piece.char_span.end]
            == A_BODY
        )

    def test_single_read_whole_chat_endpoint(self) -> None:
        # Root authority is Responses-only: the chat evidence request
        # is bound by the legitimate Responses root of the SAME batch.
        chat = chat_payload(("call-a", "cat A.md", frame_legacy("c1", A_BODY)))
        original = copy.deepcopy(chat)
        requests = (
            GraphRequest(
                payload=responses_payload(root_item(WORKSPACE, ROOT_TEXT)),
                endpoint="responses",
                context=None,
            ),
            GraphRequest(payload=chat, endpoint="chat", context=None),
        )
        snap = observe_bundle_proofs(requests, make_ns())
        assert chat == original
        assert snap.outcome is BundleProofOutcome.COMPLETE
        proof = snap.bundles[0]
        assert proof.endpoint == "chat"
        assert proof.source_text == A_BODY
        # Chat structural positions (the 017-m law): the exact
        # assistant tool-call pointer and its message index for the
        # call; the exact result (tool) message pointer and index for
        # the result.
        assert proof.pieces[0].carrier_location == "$.messages[1]"
        assert proof.pieces[0].call_location == "$.messages[0].tool_calls[0]"
        assert proof.pieces[0].call_position == 0
        assert proof.pieces[0].result_position == 1
        assert proof.proven_executed == ("A.md",)

    def test_multi_members_whole_no_per_file_digest(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md B.md"),
            out_item("call-a", frame_legacy("c1", A_BODY + B_BODY)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        proof = snap.bundles[0]
        assert proof.source_text == A_BODY + B_BODY
        assert proof.proven_executed == ("A.md", "B.md")
        assert proof.distinct_member_count == 2
        segment = proof.segments[0]
        assert segment.member_positions == (0, 1)
        assert segment.member_digest is None  # boundaryless: no per-file proof

    def test_repeated_members_are_two_occurrences_not_singleton(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY + A_BODY)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        proof = snap.bundles[0]
        assert proof.proven_executed == ("A.md", "A.md")
        assert proof.distinct_member_count == 1
        assert proof.segments[0].member_positions == (0, 1)
        assert proof.segments[0].member_digest is None

    def test_prefix_suffix_echo_whole_keeps_marker_facts(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "echo 'P' && cat A.md && echo 'S'"),
            out_item("call-a", frame_legacy("c1", "P\n" + A_BODY + "S\n")),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        proof = snap.bundles[0]
        assert proof.kind is BundleProofKind.WHOLE
        assert proof.grammar == READ_PLAN_GRAMMAR
        assert proof.source_text == A_BODY  # echoes are non-source
        assert len(proof.markers) == 2
        prefix, suffix = proof.markers
        assert prefix.role is BundleMarkerRole.PREFIX
        assert prefix.char_length == 2
        assert prefix.byte_length == 2
        assert suffix.role is BundleMarkerRole.SUFFIX
        assert suffix.char_length == 2
        # The marker spans sit outside the source region, on the same
        # original carrier.
        assert prefix.piece_spans[0] is not None
        assert suffix.piece_spans[0] is not None
        carrier = _carrier(payload, proof.pieces[0].carrier_location)
        ps = prefix.piece_spans[0]
        ss = suffix.piece_spans[0]
        assert ps is not None and ss is not None
        assert carrier[ps.start : ps.end] == "P\n"
        assert carrier[ss.start : ss.end] == "S\n"

    def test_empty_exterior_echo_earns_one_char_marker(self) -> None:
        # The accepted 017 plan law earns the empty fully-quoted
        # literal: the exterior marker fact is the bare LF (1 char),
        # while the NEW interior-marker law stays strict and nonempty.
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "echo '' && cat A.md"),
            out_item("call-a", frame_legacy("c1", "\n" + A_BODY)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        proof = snap.bundles[0]
        assert proof.source_text == A_BODY
        assert len(proof.markers) == 1
        assert proof.markers[0].role is BundleMarkerRole.PREFIX
        assert proof.markers[0].char_length == 1
        assert proof.markers[0].byte_length == 1

    def test_empty_file_whole_uses_exact_empty_digest(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", "")),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        proof = snap.bundles[0]
        assert proof.source_text == ""
        assert proof.source_digest == EMPTY_SOURCE_SHA256
        assert proof.segments[0].digest == EMPTY_SOURCE_SHA256
        assert proof.segments[0].member_digest == EMPTY_SOURCE_SHA256

    def test_guarded_loop_whole_proof_unchanged(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", 'for f in A.md B.md; do cat "$f" || exit 1; done'),
            out_item("call-a", frame_legacy("c1", A_BODY + "\n" + B_BODY)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        proof = snap.bundles[0]
        assert proof.grammar == LOOP_GRAMMAR
        assert proof.kind is BundleProofKind.WHOLE
        assert proof.source_text == A_BODY + "\n" + B_BODY
        assert proof.proven_executed == ("A.md", "B.md")
        assert proof.segments[0].member_digest is None


# --- Whole native process proofs ------------------------------------------


class TestWholeNativeProcess:
    """Native (process-surface) whole proofs over the original pieces."""

    def test_native_immediate_no_token_both_surfaces_one_record(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_native_final("0a1b2c", A_BODY)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        # The same physical occurrence is positive on BOTH surfaces;
        # the consistency law retains ONE record (read primary).
        assert len(snap.bundles) == 1
        proof = snap.bundles[0]
        assert proof.surface is BundleSurface.READ
        assert proof.source_text == A_BODY
        assert proof.pieces[0].call_id == "call-a"
        assert proof.pieces[0].call_position == 1
        assert proof.pieces[0].result_position == 2

    def test_native_immediate_with_token_process_only(self) -> None:
        # The token line makes the frame legacy-malformed: the legacy
        # read surface earns nothing; the native process surface
        # still proves the whole region.
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_native_final("0a1b2c", A_BODY, tokens=25)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        assert len(snap.bundles) == 1
        proof = snap.bundles[0]
        assert proof.surface is BundleSurface.PROCESS
        assert proof.source_text == A_BODY
        assert proof.proven_executed == ("A.md",)

    def test_native_chunk_multi_piece_call_association(self) -> None:
        body0, body1, body2 = "al", "pha", B_BODY
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md B.md"),
            out_item("call-a", frame_native_running(73, "0a1b2c", body0, 4)),
            poll_call("call-p1", 73),
            out_item("call-p1", frame_native_running(73, "3d4e5f", body1, 4)),
            poll_call("call-p2", 73),
            out_item("call-p2", frame_native_final("6e7f80", body2, 4)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        assert len(snap.bundles) == 1
        proof = snap.bundles[0]
        assert proof.source_text == body0 + body1 + body2
        assert len(proof.pieces) == 3
        # The actual exec/poll association of every original piece:
        # the initial piece is the exec call's result; each poll piece
        # is its causally associated poll's result (never invented).
        pieces = proof.pieces
        assert pieces[0].call_id == "call-a"
        assert pieces[0].call_position == 1
        assert pieces[0].result_position == 2
        assert pieces[0].carrier_location == "$.input[2]"
        assert pieces[1].call_id == "call-p1"
        assert pieces[1].call_position == 3
        assert pieces[1].result_position == 4
        assert pieces[2].call_id == "call-p2"
        assert pieces[2].call_position == 5
        assert pieces[2].result_position == 6
        # Every piece maps only to its own original carrier.
        for piece in pieces:
            carrier = _carrier(payload, piece.carrier_location)
            assert carrier[piece.char_span.start : piece.char_span.end]
        assert proof.proven_executed == ("A.md", "B.md")

    def test_native_empty_pieces(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_native_running(73, "0a1b2c", "", 4)),
            poll_call("call-p1", 73),
            out_item("call-p1", frame_native_final("3d4e5f", "", 4)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        proof = snap.bundles[0]
        assert proof.source_text == ""
        assert proof.source_digest == EMPTY_SOURCE_SHA256
        assert len(proof.pieces) == 2


# --- Partitioned finite unique-marker proofs -------------------------------


class TestPartition:
    """The new finite unique-marker partition over the full output."""

    def test_two_groups_single_occurrence_each(self) -> None:
        body = A_BODY + "MID\n" + B_BODY
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md && echo 'MID' && cat B.md"),
            out_item("call-a", frame_legacy("c1", body)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        assert len(snap.bundles) == 1
        proof = snap.bundles[0]
        assert proof.kind is BundleProofKind.PARTITIONED
        assert proof.source_text == A_BODY + B_BODY
        assert proof.source_digest == sha256_hex(A_BODY + B_BODY)
        assert len(proof.segments) == 2
        first, second = proof.segments
        assert first.member_positions == (0,)
        assert first.digest == sha256_hex(A_BODY)
        assert first.member_digest == first.digest
        assert second.member_positions == (1,)
        assert second.digest == sha256_hex(B_BODY)
        assert second.member_digest == second.digest
        # One proven interior marker with its exact original interval.
        assert len(proof.markers) == 1
        marker = proof.markers[0]
        assert marker.role is BundleMarkerRole.INTERIOR
        assert marker.char_length == 4
        assert marker.byte_length == 4
        carrier = _carrier(payload, proof.pieces[0].carrier_location)
        ms = marker.piece_spans[0]
        assert ms is not None
        assert carrier[ms.start : ms.end] == "MID\n"
        # Per-piece spans reconstruct the exact payload substrings.
        for segment in proof.segments:
            for span in segment.piece_spans:
                assert span is not None
                assert carrier[span.start : span.end]

    def test_three_groups_boundaryless_ab_plus_c(self) -> None:
        body = A_BODY + B_BODY + "M\n" + C_BODY
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md B.md && echo 'M' && cat C.md"),
            out_item("call-a", frame_legacy("c1", body)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        proof = snap.bundles[0]
        assert proof.source_text == A_BODY + B_BODY + C_BODY
        assert len(proof.segments) == 2
        ab, c = proof.segments
        # The consecutive cat group A+B stays boundaryless internally.
        assert ab.member_positions == (0, 1)
        assert ab.member_digest is None
        assert ab.digest == sha256_hex(A_BODY + B_BODY)
        assert c.member_positions == (2,)
        assert c.member_digest == c.digest

    def test_missing_final_newline(self) -> None:
        body = A_BODY + "M\n" + B_BODY  # no trailing newline after B
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md && echo 'M' && cat B.md"),
            out_item("call-a", frame_legacy("c1", body)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        proof = snap.bundles[0]
        assert proof.source_text == A_BODY + B_BODY

    def test_empty_member_bodies(self) -> None:
        body = "" + "M\n" + ""
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md && echo 'M' && cat B.md"),
            out_item("call-a", frame_legacy("c1", body)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        proof = snap.bundles[0]
        assert proof.source_text == ""
        assert proof.source_digest == EMPTY_SOURCE_SHA256
        assert all(seg.digest == EMPTY_SOURCE_SHA256 for seg in proof.segments)
        assert all(seg.member_digest == EMPTY_SOURCE_SHA256 for seg in proof.segments)

    def test_unicode_bodies_exact_char_and_byte_lengths(self) -> None:
        a = "héllo-ü"
        b = "β-文"
        body = a + "M\n" + b
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md && echo 'M' && cat B.md"),
            out_item("call-a", frame_legacy("c1", body)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        proof = snap.bundles[0]
        assert proof.source_text == a + b
        assert proof.source_char_length == len(a + b)
        assert proof.source_byte_length == len((a + b).encode("utf-8"))
        assert proof.source_byte_length > proof.source_char_length
        first, second = proof.segments
        assert first.char_length == len(a)
        assert first.byte_length == len(a.encode("utf-8"))
        assert second.char_length == len(b)
        assert second.byte_length == len(b.encode("utf-8"))
        assert first.digest == sha256_hex(a)
        assert second.digest == sha256_hex(b)

    def test_cd_transition_resolves_under_target(self) -> None:
        body = A_BODY + "M\n" + B_BODY
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md && echo 'M' && cd /work/sub && cat B.md"),
            out_item("call-a", frame_legacy("c1", body)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        proof = snap.bundles[0]
        assert proof.proven_executed == ("A.md", "sub/B.md")
        assert proof.source_text == A_BODY + B_BODY

    def test_marker_split_across_native_pieces_responses(self) -> None:
        # The marker literal crosses the exec/poll piece boundary.
        body0, body1 = A_BODY + "MI", "D\n" + B_BODY
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md && echo 'MID' && cat B.md"),
            out_item("call-a", frame_native_running(73, "0a1b2c", body0, 4)),
            poll_call("call-p1", 73),
            out_item("call-p1", frame_native_final("3d4e5f", body1, 4)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        proof = snap.bundles[0]
        assert proof.kind is BundleProofKind.PARTITIONED
        assert proof.source_text == A_BODY + B_BODY
        assert len(proof.markers) == 1
        spans = proof.markers[0].piece_spans
        assert spans[0] is not None and spans[1] is not None
        assert spans[0].end - spans[0].start == 2  # "MI" in piece 0
        assert spans[1].end - spans[1].start == 2  # "D\n" in piece 1
        c0 = _carrier(payload, proof.pieces[0].carrier_location)
        c1 = _carrier(payload, proof.pieces[1].carrier_location)
        assert c0[spans[0].start : spans[0].end] == "MI"
        assert c1[spans[1].start : spans[1].end] == "D\n"

    def test_marker_split_across_native_pieces_chat(self) -> None:
        body0, body1 = A_BODY + "MI", "D\n" + B_BODY
        messages: list[dict[str, Any]] = [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "call-a",
                        "type": "function",
                        "function": {
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": "cat A.md && echo 'MID' && cat B.md"}),
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call-a",
                "content": frame_native_running(73, "0a1b2c", body0, 4),
            },
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "call-p1",
                        "type": "function",
                        "function": {
                            "name": "write_stdin",
                            "arguments": json.dumps({"session_id": 73, "chars": ""}),
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call-p1",
                "content": frame_native_final("3d4e5f", body1, 4),
            },
        ]
        payload = {"model": "synthetic-bundle-model", "messages": messages}
        # Root authority is Responses-only: the chat evidence request
        # is bound by the legitimate Responses root of the SAME batch.
        requests = (
            GraphRequest(
                payload=responses_payload(root_item(WORKSPACE, ROOT_TEXT)),
                endpoint="responses",
                context=None,
            ),
            GraphRequest(payload=payload, endpoint="chat", context=None),
        )
        snap = observe_bundle_proofs(requests, make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        proof = snap.bundles[0]
        assert proof.kind is BundleProofKind.PARTITIONED
        assert proof.source_text == A_BODY + B_BODY
        spans = proof.markers[0].piece_spans
        assert spans[0] is not None and spans[1] is not None


# --- Root / workspace / namespace binding (the 018-a law) ------------------


class TestRootAndNamespaceBinding:
    """The single evidenced Responses root binds the whole batch."""

    def test_no_root_refuses(self) -> None:
        payload = responses_payload(
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.NO_ROOT
        assert snap.bundles == ()
        assert BundleLimitation.NO_ROOT in snap.conflicts

    def test_competing_roots_refuse(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, "First root text."),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
        )
        payload2 = responses_payload(
            root_item(WORKSPACE, "Different root text."),
        )
        requests = (
            GraphRequest(payload=payload, endpoint="responses", context=None),
            GraphRequest(payload=payload2, endpoint="responses", context=None),
        )
        snap = observe_bundle_proofs(requests, make_ns())
        assert snap.outcome is BundleProofOutcome.ROOT_CONFLICT
        assert BundleLimitation.COMPETING_ROOTS in snap.conflicts
        assert snap.bundles == ()

    def test_repeated_same_root_is_idempotent(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        assert len(snap.bundles) == 1
        assert snap.bundles[0].root_digest == sha256_hex(ROOT_TEXT)

    def test_chat_root_never_establishes_root(self) -> None:
        # A root envelope in a Chat-only request is not a legitimate
        # effective Responses root.
        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": (
                    f"# AGENTS.md instructions for {WORKSPACE}\n\n"
                    f"<INSTRUCTIONS>\n{ROOT_TEXT}\n</INSTRUCTIONS>\n"
                ),
            },
        ]
        payload = {"model": "synthetic-bundle-model", "messages": messages}
        snap = observe_bundle_proof(payload, make_ns(), endpoint="chat")
        assert snap.outcome is BundleProofOutcome.NO_ROOT

    def test_workspace_mismatch_refuses(self) -> None:
        payload = responses_payload(
            root_item("/other", ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())  # ns workspace /work
        assert snap.outcome is BundleProofOutcome.ROOT_CONFLICT
        assert BundleLimitation.WORKSPACE_MISMATCH in snap.conflicts

    def test_root_context_mismatch_refuses(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
        )
        request = GraphRequest(
            payload=payload,
            endpoint="responses",
            context=PathContext(workspace="/elsewhere", workdir=None),
        )
        snap = observe_bundle_proofs((request,), make_ns())
        assert snap.outcome is BundleProofOutcome.ROOT_CONFLICT
        assert BundleLimitation.ROOT_CONTEXT_MISMATCH in snap.conflicts

    def test_derived_workspace_acquires_like_explicit(self) -> None:
        items = (
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
        )
        derived = observe_bundle_proofs(batch(responses_payload(*items)), make_ns())
        explicit = observe_bundle_proofs(
            (
                GraphRequest(
                    payload=responses_payload(*items),
                    endpoint="responses",
                    context=PathContext(workspace=WORKSPACE, workdir=WORKSPACE),
                ),
            ),
            make_ns(),
        )
        assert derived.outcome is BundleProofOutcome.COMPLETE
        assert explicit.outcome is BundleProofOutcome.COMPLETE
        assert derived.bundles[0].source_text == explicit.bundles[0].source_text
        assert derived.bundles[0].source_digest == explicit.bundles[0].source_digest

    def test_forged_namespace_keys_are_rejected(self) -> None:
        ns = make_ns()
        data = ns.model_dump(mode="python")
        data["namespace_key"] = "0" * 64
        with pytest.raises(ValueError, match="inconsistent"):
            BundleProofNamespace(**data)

    def test_namespace_isolates_principals(self) -> None:
        one = make_ns()
        other = make_ns(principal="other-principal")
        assert one.namespace_key != other.namespace_key
        assert one.scoped_key != other.scoped_key

    def test_actual_bounds_are_bound_into_the_key(self) -> None:
        default = make_ns()
        stricter = make_ns(bounds=BundleProofBounds(max_members=5))
        assert default.namespace_key != stricter.namespace_key
        # A direct construction that keeps the stricter key with the
        # default bounds (or vice versa) is inconsistent and refused.
        data = stricter.model_dump(mode="python")
        data["bounds"] = BundleProofBounds()
        with pytest.raises(ValueError, match="inconsistent"):
            BundleProofNamespace(**data)

    def test_supplied_bounds_must_equal_namespace(self) -> None:
        ns = make_ns()
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
        )
        with pytest.raises(ValueError, match="bounds must equal"):
            observe_bundle_proofs(batch(payload), ns, bounds=BundleProofBounds(max_members=5))
        # Equal bounds are accepted.
        snap = observe_bundle_proofs(batch(payload), ns, bounds=BundleProofBounds())
        assert snap.outcome is BundleProofOutcome.COMPLETE


# --- Supported-version refusal ---------------------------------------------


class TestVersionRefusal:
    """Valid-key namespaces with unsupported versions are refused."""

    @pytest.mark.parametrize(
        "field",
        ["bundle_proof_version", "observation_version", "graph_version"],
    )
    def test_unsupported_version_refused(self, field: str) -> None:
        ns = forced_version_ns(field, "unsupported-contract-version-v99")
        assert getattr(ns, field) == "unsupported-contract-version-v99"
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
        )
        snap = observe_bundle_proofs(batch(payload), ns)
        assert snap.outcome is BundleProofOutcome.VERSION_CONFLICT
        assert BundleLimitation.VERSION_UNSUPPORTED in snap.conflicts
        assert snap.bundles == ()

    def test_supported_versions_are_the_published_constants(self) -> None:
        ns = make_ns()
        assert ns.bundle_proof_version == BUNDLE_PROOF_CONTRACT_VERSION
        assert ns.observation_version == OBSERVER_VERSION


# --- Same-occurrence consistency and source conflicts -----------------------


class TestSeamAndConflicts:
    """The consistency law compares BEFORE retention; a mismatched
    proof acquires nothing from that occurrence."""

    def _fault_process(
        self, mutate: Callable[[BundleProof], BundleProof], req_payload: dict[str, Any]
    ) -> BundleProofSnapshot:
        from slaif_local_coding.constitution.bundles import bundle_proof as bp

        original = bp._process_bundle

        def changed(
            *args: Any, **kwargs: Any
        ) -> tuple[BundleProof | None, BundleLimitation | None]:
            proof, reason = original(*args, **kwargs)
            assert proof is not None, "fault fixture expected a positive process"
            return mutate(proof), reason

        bp._process_bundle = changed
        try:
            return observe_bundle_proofs(batch(req_payload), make_ns())
        finally:
            bp._process_bundle = original

    def test_seam_conflict_piece_ownership(self) -> None:
        # Native final WITHOUT the token line is positive on BOTH
        # accepted 017 surfaces (legacy read + native process) over
        # the same occurrence, so the patched process proof is
        # compared against the read proof before retention.
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md B.md"),
            out_item("call-a", frame_native_final("3d4e5f", A_BODY + B_BODY)),
        )

        def mutate(proof: BundleProof) -> BundleProof:
            seg = proof.segments[0].model_copy(
                update={"member_positions": (0,), "member_digest": proof.source_digest}
            )
            return proof.model_copy(update={"segments": (seg,)})

        snap = self._fault_process(mutate, payload)
        assert snap.outcome is not BundleProofOutcome.COMPLETE
        assert BundleLimitation.SEAM_CONFLICT in snap.conflicts
        assert snap.bundles == ()

    def test_seam_conflict_root_binding(self) -> None:
        # Native final WITHOUT the token line: positive on both
        # surfaces over the same occurrence (see piece-ownership).
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_native_final("3d4e5f", A_BODY)),
        )

        def mutate(proof: BundleProof) -> BundleProof:
            return proof.model_copy(update={"root_digest": "0" * 64})

        snap = self._fault_process(mutate, payload)
        assert BundleLimitation.SEAM_CONFLICT in snap.conflicts
        assert snap.bundles == ()

    def test_seam_conflict_marker_role(self) -> None:
        # Native final WITHOUT the token line: positive on both
        # surfaces over the same occurrence (see piece-ownership).
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "echo 'BEGIN' && cat A.md && echo 'END'"),
            out_item("call-a", frame_native_final("3d4e5f", "BEGIN\n" + A_BODY + "END\n")),
        )

        def mutate(proof: BundleProof) -> BundleProof:
            assert len(proof.markers) == 2
            marker = proof.markers[0].model_copy(update={"role": BundleMarkerRole.SUFFIX})
            return proof.model_copy(update={"markers": (marker, proof.markers[1])})

        snap = self._fault_process(mutate, payload)
        assert BundleLimitation.SEAM_CONFLICT in snap.conflicts
        assert snap.bundles == ()

    def test_seam_conflict_piece_call_identity(self) -> None:
        # Native final WITHOUT the token line: positive on both
        # surfaces over the same occurrence (see piece-ownership).
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_native_final("3d4e5f", A_BODY)),
        )

        def mutate(proof: BundleProof) -> BundleProof:
            piece = proof.pieces[0].model_copy(update={"call_id": "other-private"})
            return proof.model_copy(update={"pieces": (piece,)})

        snap = self._fault_process(mutate, payload)
        assert BundleLimitation.SEAM_CONFLICT in snap.conflicts
        assert snap.bundles == ()

    def test_seam_conflict_command_digest(self) -> None:
        # Native final WITHOUT the token line: positive on both
        # surfaces over the same occurrence (see piece-ownership).
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_native_final("3d4e5f", A_BODY)),
        )

        def mutate(proof: BundleProof) -> BundleProof:
            return proof.model_copy(update={"command_digest": "0" * 64})

        snap = self._fault_process(mutate, payload)
        assert BundleLimitation.SEAM_CONFLICT in snap.conflicts
        assert snap.bundles == ()

    def test_seam_conflict_requested_member_order(self) -> None:
        # Native final WITHOUT the token line: positive on both
        # surfaces over the same occurrence (see piece-ownership).
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md B.md"),
            out_item("call-a", frame_native_final("3d4e5f", A_BODY + B_BODY)),
        )

        def mutate(proof: BundleProof) -> BundleProof:
            return proof.model_copy(
                update={"requested_members": tuple(reversed(proof.requested_members))}
            )

        snap = self._fault_process(mutate, payload)
        assert BundleLimitation.SEAM_CONFLICT in snap.conflicts
        assert snap.bundles == ()

    def test_source_conflict_same_path_different_content(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
            exec_call("call-b", "cat A.md"),
            out_item("call-b", frame_legacy("c2", "ALPHA")),  # different bytes
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is not BundleProofOutcome.COMPLETE
        assert BundleLimitation.SOURCE_CONFLICT in snap.conflicts
        # The conflicting single-occurrence bundles are not retained.
        for proof in snap.bundles:
            for segment in proof.segments:
                if segment.member_digest is not None:
                    assert segment.member_digest in (
                        sha256_hex(A_BODY),
                        sha256_hex("ALPHA"),
                    )

    def test_negative_surface_never_vetoes_positive(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-bad", "ls"),
            out_item("call-bad", frame_legacy("c1", "listing")),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c2", A_BODY)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.outcome is BundleProofOutcome.COMPLETE
        assert len(snap.bundles) == 1
        assert snap.bundles[0].source_text == A_BODY


# --- Budgets: at-limit / one-over / preflight law ---------------------------


class TestBudgets:
    """Every bound: at-limit stays at-limit, the first over-bound is a
    fixed typed refusal BEFORE any owned copy/retention."""

    def test_bundles_at_limit_and_over(self) -> None:
        items2 = (
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
            exec_call("call-b", "cat B.md"),
            out_item("call-b", frame_legacy("c2", B_BODY)),
        )
        at_limit = observe_bundle_proofs(
            batch(responses_payload(*items2)), make_ns(bounds=BundleProofBounds(max_bundles=2))
        )
        assert at_limit.outcome is BundleProofOutcome.COMPLETE
        assert len(at_limit.bundles) == 2
        over = observe_bundle_proofs(
            batch(responses_payload(*items2)),
            make_ns(bounds=BundleProofBounds(max_bundles=1)),
        )
        assert over.outcome is BundleProofOutcome.OVER_BOUND
        assert BundleLimitation.BUNDLES_OVER_BOUND in over.conflicts
        assert over.bundles == ()

    def test_members_at_limit_and_over(self) -> None:
        items = (
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md B.md"),
            out_item("call-a", frame_legacy("c1", A_BODY + B_BODY)),
        )
        at_limit = observe_bundle_proofs(
            batch(responses_payload(*items)), make_ns(bounds=BundleProofBounds(max_members=2))
        )
        assert at_limit.outcome is BundleProofOutcome.COMPLETE
        assert len(at_limit.bundles) == 1
        over = observe_bundle_proofs(
            batch(responses_payload(*items)), make_ns(bounds=BundleProofBounds(max_members=1))
        )
        assert over.outcome is BundleProofOutcome.OVER_BOUND
        assert BundleLimitation.MEMBERS_OVER_BOUND in over.conflicts
        assert over.bundles == ()

    def test_members_over_bound_cumulative_across_bundles(self) -> None:
        items = (
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
            exec_call("call-b", "cat B.md"),
            out_item("call-b", frame_legacy("c2", B_BODY)),
        )
        snap = observe_bundle_proofs(
            batch(responses_payload(*items)), make_ns(bounds=BundleProofBounds(max_members=1))
        )
        assert snap.outcome is BundleProofOutcome.OVER_BOUND
        assert BundleLimitation.MEMBERS_OVER_BOUND in snap.conflicts
        assert snap.bundles == ()

    def test_member_preflight_before_carrier_fetch(self) -> None:
        # The second candidate's output carrier must NOT be fetched
        # (or the second proof allocated) before the member refusal.
        from slaif_local_coding.constitution.bundles import bundle_proof as bp

        items = (
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
            exec_call("call-b", "cat B.md"),
            out_item("call-b", frame_legacy("c2", B_BODY)),
        )
        # White-box seam: the private imported helper is not an
        # explicitly exported module attribute (mypy strict).
        original_carrier = bp._carrier_string  # type: ignore[attr-defined]
        original_proof = bp._bundle_proof
        seen = {"second_carrier": 0, "proof_allocations": 0}

        def carrier(payload: Any, location: str) -> Any:
            if location == "$.input[4]":
                seen["second_carrier"] += 1
            return original_carrier(payload, location)

        def proof(**kw: Any) -> Any:
            seen["proof_allocations"] += 1
            return original_proof(**kw)

        bp._carrier_string = carrier  # type: ignore[attr-defined]
        bp._bundle_proof = proof
        try:
            snap = observe_bundle_proofs(
                batch(responses_payload(*items)),
                make_ns(bounds=BundleProofBounds(max_members=1)),
            )
        finally:
            bp._carrier_string = original_carrier  # type: ignore[attr-defined]
            bp._bundle_proof = original_proof
        assert snap.outcome is BundleProofOutcome.OVER_BOUND
        assert BundleLimitation.MEMBERS_OVER_BOUND in snap.conflicts
        assert seen["proof_allocations"] == 1
        assert seen["second_carrier"] == 0

    def test_segments_at_limit_and_over(self) -> None:
        # M1/M2 interior, M3 suffix -> 4 source slots (the trailing
        # empty slot after the suffix marker counts too).
        command = "cat A.md && echo 'M1' && cat B.md && echo 'M2' && cat C.md && echo 'M3'"
        body = A_BODY + "M1\n" + B_BODY + "M2\n" + C_BODY + "M3\n"
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", command),
            out_item("call-a", frame_legacy("c1", body)),
        )
        at_limit = observe_bundle_proofs(
            batch(payload), make_ns(bounds=BundleProofBounds(max_segments=4))
        )
        assert at_limit.outcome is BundleProofOutcome.COMPLETE
        assert len(at_limit.bundles[0].segments) == 3
        over = observe_bundle_proofs(
            batch(payload), make_ns(bounds=BundleProofBounds(max_segments=3))
        )
        assert over.outcome is BundleProofOutcome.OVER_BOUND
        assert BundleLimitation.SEGMENTS_OVER_BOUND in over.conflicts
        assert over.bundles == ()

    def test_marker_over_bound(self) -> None:
        long_literal = "L" * 20
        command = f"cat A.md && echo '{long_literal}' && cat B.md"
        body = A_BODY + long_literal + "\n" + B_BODY
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", command),
            out_item("call-a", frame_legacy("c1", body)),
        )
        snap = observe_bundle_proofs(
            batch(payload), make_ns(bounds=BundleProofBounds(max_marker=10))
        )
        assert snap.outcome is BundleProofOutcome.OVER_BOUND
        assert BundleLimitation.MARKER_OVER_BOUND in snap.conflicts
        assert snap.bundles == ()

    def test_marker_search_cumulative_shared(self) -> None:
        # Each full output window is ~14 bytes; two scans at limit 27
        # pass, at limit 26 the second scan is refused.  The charge is
        # shared and cumulative (never reset per marker/file/request).
        items = (
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md && echo 'M' && cat B.md"),
            out_item("call-a", frame_legacy("c1", A_BODY + "M\n" + B_BODY)),
            exec_call("call-b", "cat C.md && echo 'N' && cat D.md"),
            out_item("call-b", frame_legacy("c2", C_BODY + "N\n" + "delta")),
        )
        payload = responses_payload(*items)
        at_limit = observe_bundle_proofs(
            batch(payload), make_ns(bounds=BundleProofBounds(max_marker_search=30))
        )
        assert at_limit.outcome is BundleProofOutcome.COMPLETE
        assert len(at_limit.bundles) == 2
        over = observe_bundle_proofs(
            batch(payload), make_ns(bounds=BundleProofBounds(max_marker_search=20))
        )
        assert over.outcome is BundleProofOutcome.OVER_BOUND
        assert BundleLimitation.MARKER_SEARCH_OVER_BOUND in over.conflicts
        assert over.bundles == ()

    def test_diagnostics_at_limit(self) -> None:
        # One positive (process surface) plus one refused read candidate
        # at the finite diagnostic bound: COMPLETE with the one
        # retained candidate diagnostic.
        from slaif_local_coding.constitution.bundles import bundle_proof as bp

        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_native_final("0a1b2c", A_BODY)),
        )
        original = bp._read_bundle

        def negative(*a: Any, **kw: Any) -> Any:
            return None, BundleLimitation.PLAN_UNSUPPORTED

        bp._read_bundle = negative
        try:
            snap = observe_bundle_proofs(
                batch(payload), make_ns(bounds=BundleProofBounds(max_diagnostics=1))
            )
        finally:
            bp._read_bundle = original
        assert snap.outcome is BundleProofOutcome.COMPLETE
        assert len(snap.bundles) == 1
        assert len(snap.diagnostics) == 1
        assert snap.diagnostics[0] is BundleLimitation.PLAN_UNSUPPORTED

    def test_diagnostics_overflow_before_retention(self) -> None:
        from slaif_local_coding.constitution.bundles import bundle_proof as bp

        items = (
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md && echo 'M' && cat B.md"),
            out_item("call-a", frame_legacy("c1", A_BODY + B_BODY)),  # marker missing
            exec_call("call-b", "cat C.md && echo 'N' && cat D.md"),
            out_item("call-b", frame_legacy("c2", C_BODY + "delta")),
        )
        originals = (bp._read_bundle, bp._process_bundle)
        seen = {"calls": 0}

        def negative(*a: Any, **kw: Any) -> Any:
            seen["calls"] += 1
            return None, BundleLimitation.PLAN_UNSUPPORTED

        bp._read_bundle = negative
        bp._process_bundle = negative
        try:
            snap = observe_bundle_proofs(
                batch(responses_payload(*items)),
                make_ns(bounds=BundleProofBounds(max_diagnostics=1)),
            )
        finally:
            bp._read_bundle, bp._process_bundle = originals
        assert snap.outcome is BundleProofOutcome.OVER_BOUND
        assert BundleLimitation.DIAGNOSTICS_FULL in snap.conflicts
        assert snap.bundles == ()
        assert 0 < seen["calls"] <= 2
        total = len(snap.conflicts) + len(snap.diagnostics) + len(snap.observation_limitations)
        assert total <= 1

    def test_source_single_body_over_bound(self) -> None:
        big = "x" * 30
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", big)),
        )
        graph = GraphBounds(max_single_source_bytes=20)
        snap = observe_bundle_proofs(batch(payload), make_ns(graph_bounds=graph))
        assert snap.outcome is BundleProofOutcome.OVER_BOUND
        assert BundleLimitation.SOURCE_OVER_BOUND in snap.conflicts
        assert snap.bundles == ()

    def test_source_total_over_bound(self) -> None:
        body = "x" * 10
        items = (
            root_item(WORKSPACE, "r."),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", body)),
            exec_call("call-b", "cat B.md"),
            out_item("call-b", frame_legacy("c2", body)),
            exec_call("call-c", "cat C.md"),
            out_item("call-c", frame_legacy("c3", body)),
        )
        graph = GraphBounds(max_total_inspected_source_bytes=25)
        snap = observe_bundle_proofs(batch(responses_payload(*items)), make_ns(graph_bounds=graph))
        assert snap.outcome is BundleProofOutcome.OVER_BOUND
        assert BundleLimitation.TOTAL_SOURCE_OVER_BOUND in snap.conflicts
        assert snap.bundles == ()

    def test_batch_over_bound(self) -> None:
        items = (
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", A_BODY)),
        )
        requests = (
            GraphRequest(payload=responses_payload(*items), endpoint="responses", context=None),
            GraphRequest(payload=responses_payload(*items), endpoint="responses", context=None),
            GraphRequest(payload=responses_payload(*items), endpoint="responses", context=None),
        )
        graph = GraphBounds(max_requests=2)
        snap = observe_bundle_proofs(requests, make_ns(graph_bounds=graph))
        assert snap.outcome is BundleProofOutcome.OVER_BOUND
        assert BundleLimitation.BATCH_OVER_BOUND in snap.conflicts
        assert snap.bundles == ()


# --- Typed negative refusals -------------------------------------------------


class TestNegatives:
    """Unsupported / inconsistent candidates acquire nothing."""

    def _snap(self, command: str, frame: str) -> Any:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", command),
            out_item("call-a", frame),
        )
        return observe_bundle_proofs(batch(payload), make_ns())

    def test_marker_missing_refuses_partition(self) -> None:
        snap = self._snap("cat A.md && echo 'M' && cat B.md", frame_legacy("c1", A_BODY + B_BODY))
        assert snap.outcome is BundleProofOutcome.COMPLETE
        assert snap.bundles == ()
        assert BundleLimitation.MARKER_MISSING in snap.diagnostics

    def test_marker_duplicate_refuses_partition(self) -> None:
        body = A_BODY + "M\n" + B_BODY + "M\n"
        snap = self._snap("cat A.md && echo 'M' && cat B.md", frame_legacy("c1", body))
        assert snap.bundles == ()
        assert BundleLimitation.MARKER_DUPLICATE in snap.diagnostics

    def test_marker_order_refuses_partition(self) -> None:
        body = A_BODY + "M2\n" + B_BODY + "M1\n"
        snap = self._snap(
            "cat A.md && echo 'M1' && cat B.md && echo 'M2' && cat C.md",
            frame_legacy("c1", body + C_BODY),
        )
        assert snap.bundles == ()
        assert BundleLimitation.MARKER_ORDER in snap.diagnostics

    def test_unsupported_statements_refuse_partition(self) -> None:
        for command, body in [
            ("cat A.md && echo 'M' && ls && cat B.md", A_BODY + "M\n" + B_BODY),
            ("cat A.md && echo 'M' && sleep 1 && cat B.md", A_BODY + "M\n" + B_BODY),
            ("cat A.md; echo 'M' && cat B.md", A_BODY + "M\n" + B_BODY),
            ("cat A.* && echo 'M' && cat B.md", A_BODY + "M\n" + B_BODY),
            ("cat $A && echo 'M' && cat B.md", A_BODY + "M\n" + B_BODY),
        ]:
            snap = self._snap(command, frame_legacy("c1", body))
            assert snap.bundles == (), command
            assert BundleLimitation.PLAN_UNSUPPORTED in snap.diagnostics, command

    def test_loop_command_is_never_partitioned(self) -> None:
        snap = self._snap(
            'for f in A.md B.md; do cat "$f" || exit 1; done && echo M',
            frame_legacy("c1", A_BODY + B_BODY + "M\n"),
        )
        assert snap.bundles == ()

    def test_nonzero_exit_refuses_partition(self) -> None:
        snap = self._snap(
            "cat A.md && echo 'M' && cat B.md",
            frame_legacy_code("c1", A_BODY + "M\n" + B_BODY, 1),
        )
        assert snap.bundles == ()
        assert BundleLimitation.OUTPUT_INCONSISTENT in snap.diagnostics

    def test_truncated_output_refuses(self) -> None:
        snap = self._snap(
            "cat A.md && echo 'M' && cat B.md",
            frame_legacy_truncated("c1", A_BODY + "M\n" + B_BODY),
        )
        assert snap.bundles == ()

    def test_running_process_is_not_a_candidate(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_native_running(73, "0a1b2c", A_BODY, 4)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.bundles == ()

    def test_missing_output_is_not_a_candidate(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.bundles == ()

    def test_workspace_traversal_member_unresolved(self) -> None:
        snap = self._snap("cat ../outside.md", frame_legacy("c1", A_BODY))
        assert snap.bundles == ()
        assert BundleLimitation.MEMBER_UNRESOLVED in snap.diagnostics

    def test_segment_unexplained_refuses(self) -> None:
        # The cd-only run between the markers must print nothing; the
        # "junk" slot bytes are unexplained by any cat group.
        body = A_BODY + "M1\n" + "junk" + "M2\n" + B_BODY
        snap = self._snap(
            "cat A.md && echo 'M1' && cd /work && echo 'M2' && cat B.md",
            frame_legacy("c1", body),
        )
        assert snap.bundles == ()
        assert BundleLimitation.SEGMENT_UNEXPLAINED in snap.diagnostics

    def test_unknown_tool_name_never_acquires(self) -> None:
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            {
                "type": "function_call",
                "call_id": "call-x",
                "name": "unknown_tool",
                "arguments": json.dumps({"cmd": "cat A.md"}),
            },
            out_item("call-x", frame_legacy("c1", A_BODY)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert snap.bundles == ()


# --- Both ACTUAL path ceilings on represented members (order 83/84) ---------


class TestMemberPathBounds:
    """Every normalized represented member reference is bounded by
    BOTH the effective GraphBounds path bound and the effective
    ObservationBounds path bound (UTF-8 bytes), checked before any
    member charge or source/proof copy; a violation is the fixed
    typed ``MEMBER_PATH_OVER_BOUND`` non-acquisition (an observation-
    bound violation stays the 017 ``MEMBER_UNRESOLVED`` typing)."""

    AT_LIMIT = "ABCDEF.md"  # 9 UTF-8 bytes
    ONE_OVER = "ABCDEFG.md"  # 10 UTF-8 bytes

    def test_read_at_limit_and_one_over(self) -> None:
        at_limit = observe_bundle_proofs(
            batch(
                responses_payload(
                    root_item(WORKSPACE, ROOT_TEXT),
                    exec_call("call-a", f"cat {self.AT_LIMIT}"),
                    out_item("call-a", frame_legacy("c1", A_BODY)),
                )
            ),
            make_ns(graph_bounds=GraphBounds(max_path_bytes=9)),
        )
        assert at_limit.outcome is BundleProofOutcome.COMPLETE
        assert len(at_limit.bundles) == 1
        assert at_limit.bundles[0].source_text == A_BODY
        one_over = observe_bundle_proofs(
            batch(
                responses_payload(
                    root_item(WORKSPACE, ROOT_TEXT),
                    exec_call("call-a", f"cat {self.ONE_OVER}"),
                    out_item("call-a", frame_legacy("c1", A_BODY)),
                )
            ),
            make_ns(graph_bounds=GraphBounds(max_path_bytes=9)),
        )
        assert one_over.bundles == ()
        assert BundleLimitation.MEMBER_PATH_OVER_BOUND in one_over.diagnostics
        assert BundleLimitation.MEMBER_UNRESOLVED not in one_over.diagnostics

    def test_byte_units_not_chars(self) -> None:
        # "\u00e9\u00e9\u00e9.md" is 6 chars but 9 UTF-8 bytes: at limit.
        at_limit = observe_bundle_proofs(
            batch(
                responses_payload(
                    root_item(WORKSPACE, ROOT_TEXT),
                    exec_call("call-a", "cat \u00e9\u00e9\u00e9.md"),
                    out_item("call-a", frame_legacy("c1", A_BODY)),
                )
            ),
            make_ns(graph_bounds=GraphBounds(max_path_bytes=9)),
        )
        assert at_limit.outcome is BundleProofOutcome.COMPLETE
        assert len(at_limit.bundles) == 1
        # "\u00e9\u00e9\u00e9\u00e9.md" is 7 chars but 11 UTF-8 bytes: over.
        one_over = observe_bundle_proofs(
            batch(
                responses_payload(
                    root_item(WORKSPACE, ROOT_TEXT),
                    exec_call("call-a", "cat \u00e9\u00e9\u00e9\u00e9.md"),
                    out_item("call-a", frame_legacy("c1", A_BODY)),
                )
            ),
            make_ns(graph_bounds=GraphBounds(max_path_bytes=9)),
        )
        assert one_over.bundles == ()
        assert BundleLimitation.MEMBER_PATH_OVER_BOUND in one_over.diagnostics

    def test_native_process_surface(self) -> None:
        # Token line: native-process-only positive (legacy-malformed).
        snap = observe_bundle_proofs(
            batch(
                responses_payload(
                    root_item(WORKSPACE, ROOT_TEXT),
                    exec_call("call-a", f"cat {self.ONE_OVER}"),
                    out_item("call-a", frame_native_final("3d4e5f", A_BODY, 8)),
                )
            ),
            make_ns(graph_bounds=GraphBounds(max_path_bytes=9)),
        )
        assert snap.bundles == ()
        assert BundleLimitation.MEMBER_PATH_OVER_BOUND in snap.diagnostics

    def test_chat_endpoint(self) -> None:
        chat = chat_payload(("call-a", f"cat {self.ONE_OVER}", frame_legacy("c1", A_BODY)))
        requests = (
            GraphRequest(
                payload=responses_payload(root_item(WORKSPACE, ROOT_TEXT)),
                endpoint="responses",
                context=None,
            ),
            GraphRequest(payload=chat, endpoint="chat", context=None),
        )
        snap = observe_bundle_proofs(requests, make_ns(graph_bounds=GraphBounds(max_path_bytes=9)))
        assert snap.bundles == ()
        assert BundleLimitation.MEMBER_PATH_OVER_BOUND in snap.diagnostics

    def test_observation_bound_violation_stays_unresolved(self) -> None:
        # The observation bound (not the graph bound) is the violated
        # ceiling: the 017 normalization stays typed
        # MEMBER_UNRESOLVED, never relabeled MEMBER_PATH_OVER_BOUND.
        snap = observe_bundle_proofs(
            batch(
                responses_payload(
                    root_item(WORKSPACE, ROOT_TEXT),
                    exec_call("call-a", f"cat {self.ONE_OVER}"),
                    out_item("call-a", frame_legacy("c1", A_BODY)),
                )
            ),
            make_ns(
                graph_bounds=GraphBounds(max_path_bytes=4096),
                observation_bounds=ObservationBounds(max_path_bytes=9),
            ),
        )
        assert snap.bundles == ()
        assert BundleLimitation.MEMBER_UNRESOLVED in snap.diagnostics
        assert BundleLimitation.MEMBER_PATH_OVER_BOUND not in snap.diagnostics


# --- Privacy and purity -------------------------------------------------------


class TestPrivacyAndPurity:
    """Private IDs and source content never enter operational output."""

    def test_proof_repr_suppresses_source_and_ids(self) -> None:
        secret_body = "TOP-SECRET-SOURCE-CONTENT"
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", secret_body)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        proof = snap.bundles[0]
        rendered = repr(proof)
        assert secret_body not in rendered
        assert "call-a" not in rendered
        assert "<private-id>" in rendered

    def test_snapshot_str_suppresses_source(self) -> None:
        secret_body = "TOP-SECRET-SOURCE-CONTENT"
        payload = responses_payload(
            root_item(WORKSPACE, ROOT_TEXT),
            exec_call("call-a", "cat A.md"),
            out_item("call-a", frame_legacy("c1", secret_body)),
        )
        snap = observe_bundle_proofs(batch(payload), make_ns())
        assert secret_body not in str(snap)
        assert "call-a" not in str(snap)

    def test_piece_repr_empty_call_id_stays_exact(self) -> None:
        empty = _test_piece("")
        rendered = repr(empty)
        assert "call_id=''" in rendered
        assert "<private-id>" not in rendered
        named = _test_piece("call-x")
        rendered_named = repr(named)
        assert "call_id='<private-id>'" in rendered_named
        assert "call-x" not in rendered_named

    def test_bundle_proof_validation_error_hides_input(self) -> None:
        from pydantic import ValidationError

        canary = "CANARY-PRIVATE-SOURCE-TEXT"
        with pytest.raises(ValidationError) as excinfo:
            BundleProof(
                surface=BundleSurface.READ,
                kind=BundleProofKind.WHOLE,
                grammar=READ_GRAMMAR,
                request_index=0,
                call_id="call-a",
                call_location="$.input[1]",
                call_position=1,
                result_location="$.input[2]",
                result_position=2,
                endpoint="responses",
                root_path="AGENTS.md",
                root_digest=sha256_hex(ROOT_TEXT),
                requested_members=(_resolved("A.md"),),
                proven_executed=("A.md",),
                distinct_member_count=1,
                pieces=(
                    BundlePiece(
                        piece_index=0,
                        carrier_location="$.input[2]",
                        char_span=_span(0, 3),
                        char_length=3,
                        byte_length=3,
                        call_id="call-a",
                        call_location="$.input[1]",
                        call_position=1,
                        result_position=2,
                    ),
                ),
                segments=(
                    BundleSegment(
                        index=0,
                        member_positions=(0,),
                        char_length=3,
                        byte_length=3,
                        digest="0" * 64,  # wrong digest: canary must not leak
                        member_digest="0" * 64,
                        piece_spans=(_span(0, 3),),
                    ),
                ),
                source_text=canary,
                source_char_length=3,
                source_byte_length=3,
                source_digest="1" * 64,
            )
        assert canary not in str(excinfo.value)

    def test_no_host_io(self) -> None:
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
        try:
            body0, body1 = "al", "pha"
            payload = responses_payload(
                root_item(WORKSPACE, ROOT_TEXT),
                exec_call("call-a", "cat A.md && echo 'M' && cat B.md"),
                out_item("call-a", frame_native_running(9203, "0a1b2c", body0, 8)),
                poll_call("call-p", 9203),
                out_item("call-p", frame_native_final("3d4e5f", body1 + "x\nM\ny", 8)),
            )
            original = copy.deepcopy(payload)
            snap = observe_bundle_proofs(batch(payload), make_ns())
            assert attempts == []
            assert payload == original
            assert snap.outcome is BundleProofOutcome.COMPLETE
            # source_text is the exact ordered segment concatenation:
            # A.md "alphax\n" (running "al" + final "phax\n") and
            # B.md "y", with the proven "M\n" marker excluded.
            assert snap.bundles[0].source_text == "alphax\n" + "y"
        finally:
            restore()
