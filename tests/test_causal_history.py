"""018-d: original-API causal-occurrence kernel -- durable
known-synthetic controls over the inert pure state machine.

PUBLIC transition tests for ``observe_causal_history`` (and, later in
the module, the trusted issuance/receipt/relation surface): the
legitimate effective Responses root envelope and the accepted 017
read evidence on BOTH read endpoints (legacy framed carriers) compose
through the shared 018-b ``_proof_collect`` core into ONE bounded
original-payload observation transition over the immutable
``CausalHistoryState``.  All payloads are inline known-synthetic; no
S runtime path dependency; no model, native, client or service
facility is started.

Locked law surface covered here: the root-only bootstrap (retained
ONCE per state, revision advanced exactly once, exact anchor
provenance), the idempotent root replay, the SAME-lineage rootless
observation reusing the previously acquired immutable anchor (no
synthetic root request, no re-inspection, root identity object
preserved), rootless-vs-empty-state refusal, forged prior-anchor and
foreign-scope refusals preserving the EXACT prior state, CAS
mismatch, same-batch exact replay (one occurrence retained, FIRST
provenance kept, the transition's new/replayed lists disjoint),
same-batch changed-result conflict, cross-batch exact replay as a
pure REPLAYED no-op, and the charged new-proof member/piece
retention law (duplicate operands count; crossing refuses atomically
BEFORE retention).  The native pending-process per-call law is
covered by the known-synthetic chain fixtures: a genuine poll
extension retains the poll's ACTUAL observed binding (never a
fabricated issuance), a reused observed poll ID (pending or
completed) is a typed conflict, and the complete schema-evidenced
inventory's same-ID unsupported/changed arguments refuse with the
exact closed diagnostics.  The issuance/receipt/relation surface
and the full bound matrices extend this module under the same order.
"""

from __future__ import annotations

import builtins
import copy
import hashlib
import inspect
import json
import os
import socket
import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from slaif_local_coding.constitution.bundles import (
    BundleProofBounds,
    GraphBounds,
    ObservationBounds,
    observe_bundle_admission_batch,
)
from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
    AdmissionOutcome,
    make_bundle_admission_namespace,
)
from slaif_local_coding.constitution.bundles.causal_history import (
    observe_causal_history,
    register_issuance,
    register_receipt,
    relation,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ARGUMENTS_JSON_VERSION,
    CAUSAL_HISTORY_CONTRACT_VERSION,
    CAUSAL_ROOT_FACT,
    MAX_REVISION,
    CausalHistoryLimitation,
    CausalHistoryNamespace,
    CausalHistoryOutcome,
    CausalHistoryState,
    CausalHistoryTransition,
    CausalRelation,
    HistoryBounds,
    ParentLink,
    ResultFingerprintRecord,
    RootAnchor,
    _canonical_history_fields,
    canonicalize_tool_arguments,
    make_causal_history_namespace,
    validate_causal_history_state,
)
from slaif_local_coding.constitution.bundles.graph_observation import GraphRequest
from slaif_local_coding.constitution.bundles.observation_models import (
    CharSpan,
    Limitation,
    PathContext,
    ProcessOutcome,
)
from slaif_local_coding.constitution.bundles.observe import observe_request
from slaif_local_coding.constitution.cache import RequestIdentity

IDENTITY = RequestIdentity(
    principal="synthetic-history-principal",
    session="synthetic-history-session",
    repository="synthetic-history-repo",
    route="synthetic-history-route",
)
FINGERPRINT = "abcdef0123456789" * 4
LINEAGE = "synthetic-history-lineage"
WORKSPACE = "/work"
ROOT_TEXT = "Read `A.md` before changing code."
READ_BODY = "Synthetic file content.\n"
ROOT_LOCATION = "$.input[0].content[0]"
MODES = (AdmissionMode.LEAN, AdmissionMode.GREEDY)
ENDPOINTS = ("responses", "chat")


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def root_item(content: str = ROOT_TEXT) -> dict[str, Any]:
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


def frame(body: str) -> str:
    return (
        "Chunk ID: synthetic\n"
        "Wall time: 0.0000 seconds\n"
        "Process exited with code 0\n"
        f"Output:\n{body}"
    )


def exec_call(cid: str, cmd: str = "cat A.md") -> dict[str, Any]:
    return {
        "type": "function_call",
        "call_id": cid,
        "name": "exec_command",
        "arguments": json.dumps({"cmd": cmd}),
    }


def out_item(cid: str, text: str) -> dict[str, Any]:
    return {"type": "function_call_output", "call_id": cid, "output": text}


def read_request(
    endpoint: str,
    cid: str,
    body: str = READ_BODY,
    cmd: str = "cat A.md",
) -> GraphRequest:
    """One original ROOTLESS read request on EITHER read endpoint.

    Root authority is Responses-only (the accepted 017 law): a chat
    request never anchors a root, so root evidence always comes from
    a separate legitimate Responses envelope request (see
    ``root_read_batch`` / ``responses_rooted_read``).
    """
    if endpoint == "responses":
        payload = {"input": [exec_call(cid, cmd), out_item(cid, frame(body))]}
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
                {"role": "tool", "tool_call_id": cid, "content": frame(body)},
            ]
        }
    return GraphRequest(payload=payload, endpoint=endpoint, context=None)


def root_request() -> GraphRequest:
    return GraphRequest(payload={"input": [root_item()]}, endpoint="responses", context=None)


def responses_rooted_read(cid: str, body: str = READ_BODY, cmd: str = "cat A.md") -> GraphRequest:
    """One legitimate Responses request carrying the effective root
    envelope AND the read evidence (root authority is Responses-only).
    """
    payload = {"input": [root_item(), exec_call(cid, cmd), out_item(cid, frame(body))]}
    return GraphRequest(payload=payload, endpoint="responses", context=None)


def root_read_batch(
    endpoint: str, cid: str, body: str = READ_BODY, cmd: str = "cat A.md"
) -> tuple[GraphRequest, ...]:
    """The legitimate batch on EITHER read endpoint: the Responses
    root envelope request plus the endpoint's read request."""
    return (root_request(), read_request(endpoint, cid, body, cmd))


def make_ns(
    mode: AdmissionMode = AdmissionMode.LEAN,
    lineage: str = LINEAGE,
    history_bounds: HistoryBounds | None = None,
    graph_bounds: GraphBounds | None = None,
    proof_bounds: BundleProofBounds | None = None,
    observation_bounds: ObservationBounds | None = None,
) -> CausalHistoryNamespace:
    admission = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-history-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
        graph_bounds=graph_bounds,
        proof_bounds=proof_bounds,
        observation_bounds=observation_bounds,
    )
    return make_causal_history_namespace(admission, lineage, bounds=history_bounds)


def empty_state(ns: CausalHistoryNamespace) -> CausalHistoryState:
    return CausalHistoryState(history_key=ns.history_key, revision=0)


# --- Native process chain (pending poll) known-synthetic fixtures --------

PENDING_BODY = "Synthetic partial output.\n"
PENDING_TAIL = "Synthetic final output.\n"
CHAIN_SESSION = 9001

# Distinct complete version bodies for the nonroot version-chain law.
V1_BODY = "Version one body.\n"
V2_BODY = "Version two body.\n"


def running_frame(body: str, session_id: int = CHAIN_SESSION) -> str:
    return (
        "Chunk ID: a1b2c3\n"
        "Wall time: 0.0010 seconds\n"
        f"Process running with session ID {session_id}\n"
        "Original token count: 4\n"
        f"Output:\n{body}"
    )


def terminal_frame(body: str) -> str:
    return (
        "Chunk ID: d4e5f6\n"
        "Wall time: 0.0010 seconds\n"
        "Process exited with code 0\n"
        "Original token count: 4\n"
        f"Output:\n{body}"
    )


def poll_arguments(session_id: int = CHAIN_SESSION) -> str:
    return json.dumps({"session_id": session_id, "chars": ""})


def chain_request(
    endpoint: str,
    cid: str,
    body: str,
    poll_cid: str | None = None,
    poll_text: str | None = None,
    session_id: int = CHAIN_SESSION,
) -> GraphRequest:
    """One native exec chain on EITHER read endpoint: the exec call
    with its running frame, optionally followed by the causally
    associated write_stdin poll and the poll's own result frame."""
    if endpoint == "responses":
        items: list[dict[str, Any]] = [
            exec_call(cid),
            out_item(cid, running_frame(body, session_id)),
        ]
        if poll_cid is not None:
            items.append(
                {
                    "type": "function_call",
                    "call_id": poll_cid,
                    "name": "write_stdin",
                    "arguments": poll_arguments(session_id),
                }
            )
            items.append(out_item(poll_cid, poll_text or ""))
        payload: dict[str, Any] = {"input": items}
    else:
        messages: list[dict[str, Any]] = [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": cid,
                        "type": "function",
                        "function": {
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": "cat A.md"}),
                        },
                    }
                ],
            },
            {"role": "tool", "tool_call_id": cid, "content": running_frame(body, session_id)},
        ]
        if poll_cid is not None:
            messages.append(
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": poll_cid,
                            "type": "function",
                            "function": {
                                "name": "write_stdin",
                                "arguments": poll_arguments(session_id),
                            },
                        }
                    ],
                }
            )
            messages.append({"role": "tool", "tool_call_id": poll_cid, "content": poll_text or ""})
        payload = {"messages": messages}
    return GraphRequest(payload=payload, endpoint=endpoint, context=None)


def canonical_fp(name: str, arguments: str) -> str:
    """The accepted canonical argument fingerprint for an expected
    binding (generous caps, no charging: a pure oracle)."""
    result = canonicalize_tool_arguments(
        name,
        arguments,
        max_argument_bytes=10**9,
        max_total_argument_bytes=10**9,
        max_argument_nodes=10**9,
        max_argument_depth=10**9,
        charge_total=lambda n: True,
        work=lambda: True,
    )
    assert result.ok and result.fingerprint is not None
    return result.fingerprint


# --- Root bootstrap and SAME-lineage rootless reuse ---------------------


@pytest.mark.parametrize("mode", MODES)
def test_root_only_bootstrap_revision_and_anchor(mode: AdmissionMode) -> None:
    """A legitimate root envelope bootstraps the anchor exactly once:
    revision 0 -> 1, exact anchor facts, NO occurrence/result evidence
    is invented from the root itself."""
    ns = make_ns(mode)
    empty = empty_state(ns)
    result = observe_causal_history((root_request(),), ns, empty, 0)
    assert result.outcome is CausalHistoryOutcome.ACCEPTED
    assert result.revision_before == 0
    assert result.revision_after == 1
    assert result.state.revision == 1
    assert result.new_occurrences == ()
    assert result.replayed_occurrences == ()
    root = result.state.root
    assert root is not None
    assert root.root_text == ROOT_TEXT
    assert root.root_digest == sha256_hex(ROOT_TEXT)
    assert root.workspace == WORKSPACE
    assert root.first_request_index == 0
    assert root.source_byte_length == len(ROOT_TEXT.encode("utf-8"))
    assert root.location == ROOT_LOCATION
    assert root.content_span.length == len(ROOT_TEXT)
    assert result.state.occurrences == ()
    assert result.state.results == ()
    assert result.state.issuances == ()
    assert result.state.parent_links == ()
    # privacy: no source text or private identity in operational output
    assert ROOT_TEXT not in repr(result)
    assert "synthetic-history-principal" not in repr(result)


@pytest.mark.parametrize("mode", MODES)
def test_root_only_bootstrap_idempotent_replay(mode: AdmissionMode) -> None:
    """Re-observing the same legitimate root is a pure replay: the
    EXACT prior state is preserved, no revision advance, the anchor is
    not re-earned."""
    ns = make_ns(mode)
    first = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert first.outcome is CausalHistoryOutcome.ACCEPTED
    again = observe_causal_history((root_request(),), ns, first.state, 1)
    assert again.outcome is CausalHistoryOutcome.REPLAYED
    assert again.state is first.state
    assert again.revision_before == 1
    assert again.revision_after == 1
    assert again.new_occurrences == ()
    assert again.replayed_occurrences == ()
    assert again.state.root is first.state.root


@pytest.mark.parametrize("mode", MODES)
def test_root_and_read_bootstrap_single_request(mode: AdmissionMode) -> None:
    """One request carrying the root envelope AND a complete read
    bootstraps the anchor and retains the completed occurrence with
    its exact original source facts."""
    ns = make_ns(mode)
    result = observe_causal_history((responses_rooted_read("first"),), ns, empty_state(ns), 0)
    assert result.outcome is CausalHistoryOutcome.ACCEPTED
    assert result.state.revision == 1
    assert result.state.root is not None
    assert len(result.state.occurrences) == 1
    occ = result.state.occurrences[0]
    assert occ.call_id == "first"
    assert occ.anchored is False
    assert occ.endpoint == "responses"
    assert occ.proof.source_text == READ_BODY
    assert occ.proof.source_digest == sha256_hex(READ_BODY)
    assert occ.proof.source_byte_length == len(READ_BODY.encode("utf-8"))
    assert tuple(m.normalized for m in occ.proof.requested_members) == ("A.md",)
    assert len(result.state.results) == 1
    record = result.state.results[0]
    assert record.call_id == "first"
    assert record.complete is True
    assert record.first_request_index == 0


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_prior_root_rootless_read_both_endpoints(mode: AdmissionMode, endpoint: str) -> None:
    """A later rootless observation of the SAME lineage reuses the
    previously acquired immutable anchor: one new occurrence on EITHER
    read endpoint, root identity object preserved, revision advances
    once.  No synthetic root request, no re-inspection."""
    ns = make_ns(mode)
    prior = observe_causal_history(root_read_batch("responses", "first"), ns, empty_state(ns), 0)
    assert prior.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(prior.state.occurrences) == 1
    assert prior.state.root is not None
    result = observe_causal_history((read_request(endpoint, "second"),), ns, prior.state, 1)
    assert result.outcome is CausalHistoryOutcome.ACCEPTED
    assert result.revision_before == 1
    assert result.revision_after == 2
    assert result.state.revision == 2
    assert len(result.state.occurrences) == 2
    assert result.state.root is prior.state.root
    assert {o.call_id for o in result.state.occurrences} == {"first", "second"}
    assert len(result.state.results) == 2
    assert result.state.root.first_request_index == 0


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_rootless_empty_state_refuses(mode: AdmissionMode, endpoint: str) -> None:
    """Rootless input plus the exact empty prior state cannot
    bootstrap authority: typed NO_ROOT refusal, EXACT prior state."""
    ns = make_ns(mode)
    empty = empty_state(ns)
    result = observe_causal_history((read_request(endpoint, "orphan"),), ns, empty, 0)
    assert result.outcome is CausalHistoryOutcome.REFUSED_NO_ROOT
    assert result.state is empty
    assert result.revision_before == 0
    assert result.revision_after == 0
    assert CausalHistoryLimitation.NO_ROOT in result.diagnostics


@pytest.mark.parametrize("mode", MODES)
def test_rootless_forged_anchor_workspace_refuses(mode: AdmissionMode) -> None:
    """A forged prior anchor from another root scope (same borrowed
    history key) cannot be reused: explicit WORKSPACE_MISMATCH refusal,
    EXACT prior state preserved."""
    ns = make_ns(mode)
    forged_root = RootAnchor(
        root_text=ROOT_TEXT,
        root_digest=sha256_hex(ROOT_TEXT),
        workspace="/forged",
        first_request_index=0,
        source_byte_length=len(ROOT_TEXT.encode("utf-8")),
        location=ROOT_LOCATION,
        content_span=CharSpan(start=0, end=len(ROOT_TEXT)),
    )
    forged = CausalHistoryState(history_key=ns.history_key, revision=1, root=forged_root)
    result = observe_causal_history((read_request("responses", "late"),), ns, forged, 1)
    assert result.outcome is CausalHistoryOutcome.REFUSED_ROOT_CONFLICT
    assert result.state is forged
    assert CausalHistoryLimitation.WORKSPACE_MISMATCH in result.diagnostics
    assert result.revision_before == 1
    assert result.revision_after == 1


@pytest.mark.parametrize("mode", MODES)
def test_foreign_scope_state_refuses(mode: AdmissionMode) -> None:
    """A state from another lineage (different history scope key) is
    refused explicitly BEFORE any observation work, EXACT prior state."""
    ns = make_ns(mode)
    other = make_ns(mode, lineage="other-lineage")
    other_state = CausalHistoryState(history_key=other.history_key, revision=0)
    result = observe_causal_history((root_request(),), ns, other_state, 0)
    assert result.outcome is CausalHistoryOutcome.REFUSED_FOREIGN_SCOPE
    assert result.state is other_state
    assert result.revision_before == 0
    assert result.revision_after == 0
    assert result.diagnostics == ()


@pytest.mark.parametrize("mode", MODES)
def test_cas_mismatch_preserves_exact_state(mode: AdmissionMode) -> None:
    """A CAS mismatch is refused BEFORE any observation/retention
    work; the EXACT prior state is preserved."""
    ns = make_ns(mode)
    empty = empty_state(ns)
    result = observe_causal_history((root_request(),), ns, empty, 7)
    assert result.outcome is CausalHistoryOutcome.REFUSED_CAS_MISMATCH
    assert result.state is empty
    assert result.revision_before == 0
    assert result.revision_after == 0


# --- Same-batch evidence: replay, conflict, charged retention ----------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_same_batch_exact_replay_accepts_once(mode: AdmissionMode, endpoint: str) -> None:
    """Two IDENTICAL original requests in ONE batch against a
    root-only prior state retain ONE occurrence/result: the duplicate
    is an idempotent replay of staged evidence, FIRST provenance kept,
    the transition's new/replayed lists stay disjoint (the new
    occurrence is classified NEW exactly once)."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    assert boot.state.root is not None
    req = read_request(endpoint, "first")
    result = observe_causal_history((req, copy.deepcopy(req)), ns, boot.state, 1)
    assert result.outcome is CausalHistoryOutcome.ACCEPTED
    assert result.revision_before == 1
    assert result.revision_after == 2
    assert len(result.state.occurrences) == 1
    assert len(result.new_occurrences) == 1
    assert result.replayed_occurrences == ()
    assert len(result.state.results) == 1
    occ = result.state.occurrences[0]
    assert occ.call_id == "first"
    assert occ.proof.source_digest == sha256_hex(READ_BODY)
    assert occ.proof.request_index == 0


@pytest.mark.parametrize("mode", MODES)
def test_same_batch_triple_duplicate_accepts_once(mode: AdmissionMode) -> None:
    """Three identical requests in ONE batch: still exactly one
    retained occurrence (no duplicate records, no validator refusal)."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    req = read_request("responses", "dup")
    result = observe_causal_history(
        (req, copy.deepcopy(req), copy.deepcopy(req)), ns, boot.state, 1
    )
    assert result.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(result.state.occurrences) == 1
    assert len(result.new_occurrences) == 1
    assert result.replayed_occurrences == ()
    assert len(result.state.results) == 1


@pytest.mark.parametrize("mode", MODES)
def test_same_batch_changed_result_conflict(mode: AdmissionMode) -> None:
    """The SAME call ID with a CHANGED result in one batch is an
    atomic typed conflict (a deliberate change requires a genuinely
    new call, never a resold identity); the EXACT prior state is
    preserved."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    req_a = read_request("responses", "first")
    req_b = read_request("responses", "first", body="CHANGED BYTES\n")
    result = observe_causal_history((req_a, req_b), ns, boot.state, 1)
    assert result.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert CausalHistoryLimitation.RESULT_CONFLICT in result.diagnostics
    assert result.state is boot.state
    assert result.revision_before == 1
    assert result.revision_after == 1


@pytest.mark.parametrize("mode", MODES)
def test_cross_batch_exact_replay_is_noop(mode: AdmissionMode) -> None:
    """An exact completed replay in a LATER batch is a pure REPLAYED
    transition: the retained occurrence is listed once, the EXACT
    prior state is preserved, no revision advance."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    first = observe_causal_history((read_request("responses", "first"),), ns, boot.state, 1)
    assert first.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(first.state.occurrences) == 1
    again = observe_causal_history((read_request("responses", "first"),), ns, first.state, 2)
    assert again.outcome is CausalHistoryOutcome.REPLAYED
    assert again.state is first.state
    assert again.revision_before == 2
    assert again.revision_after == 2
    assert again.new_occurrences == ()
    assert len(again.replayed_occurrences) == 1
    assert again.replayed_occurrences[0].occurrence_id == first.state.occurrences[0].occurrence_id


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_new_proof_member_piece_work_charged_before_retention(
    mode: AdmissionMode, endpoint: str
) -> None:
    """Every retained proof member occurrence of a NEW occurrence
    charges the ONE shared per-transition work ledger BEFORE
    retention: 32 repeated operands cross max_work_units=16 and
    refuse atomically (nothing retained, EXACT prior state); at the
    default ceiling all 32 member occurrences are retained with the
    exact original source bytes/digest."""
    body = READ_BODY * 32
    cmd = "cat " + " ".join(["A.md"] * 32)
    batch = root_read_batch(endpoint, "big", body=body, cmd=cmd)

    ns_cap = make_ns(mode, history_bounds=HistoryBounds(max_work_units=16))
    empty = empty_state(ns_cap)
    refused = observe_causal_history(batch, ns_cap, empty, 0)
    assert refused.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert CausalHistoryLimitation.WORK_UNITS_OVER_BOUND in refused.diagnostics
    assert refused.state is empty
    assert refused.state.occurrences == ()
    assert refused.state.results == ()
    assert refused.revision_after == 0

    ns_default = make_ns(mode)
    accepted = observe_causal_history(batch, ns_default, empty_state(ns_default), 0)
    assert accepted.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(accepted.state.occurrences) == 1
    proof = accepted.state.occurrences[0].proof
    assert tuple(m.normalized for m in proof.requested_members) == ("A.md",) * 32
    assert proof.source_digest == sha256_hex(body)
    assert proof.source_byte_length == len(body.encode("utf-8"))


# --- Native pending chains: observed poll bindings (018-d law) -----------


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_pending_poll_extension_retains_observed_bindings(
    mode: AdmissionMode, endpoint: str
) -> None:
    """A genuine 017-accepted poll extension retains the poll's ACTUAL
    observed binding (ID + endpoint + tool name + canonical argument
    digest) aligned with the extended piece facts: observed evidence,
    never a fabricated issuance; raw arguments are never retained."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    pending = observe_causal_history(
        (chain_request(endpoint, "hist-exec", PENDING_BODY),), ns, boot.state, 1
    )
    assert pending.outcome is CausalHistoryOutcome.ACCEPTED
    assert pending.state.occurrences == ()
    assert len(pending.state.results) == 1
    rec = pending.state.results[0]
    assert rec.complete is False
    assert len(rec.piece_facts) == 1
    assert rec.piece_call_bindings == (
        (
            "hist-exec",
            endpoint,
            "exec_command",
            canonical_fp("exec_command", json.dumps({"cmd": "cat A.md"})),
        ),
    )
    extended = observe_causal_history(
        (
            chain_request(
                endpoint,
                "hist-exec",
                PENDING_BODY,
                poll_cid="hist-poll",
                poll_text=running_frame(PENDING_TAIL),
            ),
        ),
        ns,
        pending.state,
        2,
    )
    assert extended.outcome is CausalHistoryOutcome.ACCEPTED
    assert extended.revision_before == 2
    assert extended.revision_after == 3
    assert extended.state.occurrences == ()
    assert len(extended.state.results) == 1
    rec2 = extended.state.results[0]
    assert rec2.complete is False
    assert len(rec2.piece_facts) == 2
    assert rec2.piece_call_bindings[0][:1] == ("hist-exec",)
    assert rec2.piece_call_bindings[1] == (
        "hist-poll",
        endpoint,
        "write_stdin",
        canonical_fp("write_stdin", poll_arguments()),
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_pending_poll_id_reused_as_exec_refused(mode: AdmissionMode, endpoint: str) -> None:
    """A pending chain's OBSERVED poll ID is immutable binding
    evidence: reusing it as an exec_command read ID in a later batch
    is a typed whole-state conflict (the EXACT prior state is
    preserved, no revision advance, no rebind)."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    pending = observe_causal_history(
        (chain_request(endpoint, "hist-exec", PENDING_BODY),), ns, boot.state, 1
    )
    assert pending.outcome is CausalHistoryOutcome.ACCEPTED
    extended = observe_causal_history(
        (
            chain_request(
                endpoint,
                "hist-exec",
                PENDING_BODY,
                poll_cid="hist-poll",
                poll_text=running_frame(PENDING_TAIL),
            ),
        ),
        ns,
        pending.state,
        2,
    )
    assert extended.outcome is CausalHistoryOutcome.ACCEPTED
    reuse = observe_causal_history((read_request(endpoint, "hist-poll"),), ns, extended.state, 3)
    assert reuse.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert reuse.state is extended.state
    assert reuse.revision_before == 3
    assert reuse.revision_after == 3
    assert reuse.state.results == extended.state.results


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_completed_poll_id_reused_as_exec_refused(mode: AdmissionMode, endpoint: str) -> None:
    """A completed chain's poll ID (retained through the complete
    proof's piece facts) is likewise immutable binding evidence:
    reusing it as an exec read ID is a typed conflict, while the EXACT
    full-chain re-observation stays a pure idempotent REPLAYED no-op
    (aggregate source-digest equality alone never re-opens the
    per-call law)."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    pending = observe_causal_history(
        (chain_request(endpoint, "hist-exec", PENDING_BODY),), ns, boot.state, 1
    )
    assert pending.outcome is CausalHistoryOutcome.ACCEPTED
    completed = observe_causal_history(
        (
            chain_request(
                endpoint,
                "hist-exec",
                PENDING_BODY,
                poll_cid="hist-poll",
                poll_text=terminal_frame(PENDING_TAIL),
            ),
        ),
        ns,
        pending.state,
        2,
    )
    assert completed.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(completed.state.occurrences) == 1
    occ = completed.state.occurrences[0]
    assert occ.proof.source_text == PENDING_BODY + PENDING_TAIL
    assert occ.proof.source_digest == sha256_hex(PENDING_BODY + PENDING_TAIL)
    assert occ.proof.pieces[1].call_id == "hist-poll"
    record = next(r for r in completed.state.results if r.call_id == "hist-exec")
    assert record.complete is True
    assert record.piece_call_bindings[1][:2] == ("hist-poll", endpoint)
    reuse = observe_causal_history((read_request(endpoint, "hist-poll"),), ns, completed.state, 3)
    assert reuse.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert reuse.state is completed.state
    assert reuse.revision_before == 3
    assert reuse.revision_after == 3
    again = observe_causal_history(
        (
            chain_request(
                endpoint,
                "hist-exec",
                PENDING_BODY,
                poll_cid="hist-poll",
                poll_text=terminal_frame(PENDING_TAIL),
            ),
        ),
        ns,
        completed.state,
        3,
    )
    assert again.outcome is CausalHistoryOutcome.REPLAYED
    assert again.state is completed.state


@pytest.mark.parametrize("mode", MODES)
def test_inventory_known_id_unsupported_args_typed_tuple_diagnostic(
    mode: AdmissionMode,
) -> None:
    """The same-ID immutability law over the COMPLETE schema-evidenced
    inventory: a retained known ID re-appearing with NON-STRICT
    arguments refuses with the EXACT single-element canonical-recipe
    diagnostic (the tuple path -- a bare StrEnum here would be
    iterated as characters and fail model validation), and with VALID
    but different JSON arguments it is a typed ISSUANCE_CONFLICT.
    The EXACT prior state is preserved in both cases."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    first = observe_causal_history((read_request("responses", "known-call"),), ns, boot.state, 1)
    assert first.outcome is CausalHistoryOutcome.ACCEPTED
    unsupported = GraphRequest(
        payload={
            "input": [
                exec_call("fresh-call"),
                out_item("fresh-call", frame(READ_BODY)),
                {
                    "type": "function_call",
                    "call_id": "known-call",
                    "name": "exec_command",
                    "arguments": "not-json-at-all",
                },
            ]
        },
        endpoint="responses",
        context=None,
    )
    result = observe_causal_history((unsupported,), ns, first.state, 2)
    assert result.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert result.diagnostics == (CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED,)
    assert result.state is first.state
    changed = GraphRequest(
        payload={
            "input": [
                exec_call("fresh-call-2"),
                out_item("fresh-call-2", frame(READ_BODY)),
                {
                    "type": "function_call",
                    "call_id": "known-call",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "printf synthetic"}),
                },
            ]
        },
        endpoint="responses",
        context=None,
    )
    result2 = observe_causal_history((changed,), ns, first.state, 2)
    assert result2.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert CausalHistoryLimitation.ISSUANCE_CONFLICT in result2.diagnostics
    assert result2.state is first.state


# --- Trusted issuance / late receipt / relation (018-d law) --------------

ISSUE_ARGS = json.dumps({"cmd": "cat A.md"})
ISSUE_ARGS_CANONICAL_EQUIV = '{\n  "cmd": "cat A.md"\n}'


def _receipt(
    state: CausalHistoryState,
    ns: CausalHistoryNamespace,
    cid: str,
    frontier: tuple[str, ...],
    revision: int,
    args: str = ISSUE_ARGS,
    endpoint: str = "responses",
    name: str = "exec_command",
) -> CausalHistoryTransition:
    return register_receipt(state, ns, cid, endpoint, name, args, frontier, revision)


@pytest.mark.parametrize("mode", MODES)
def test_issuance_accepts_canonical_replay_and_conflicts(mode: AdmissionMode) -> None:
    """A trusted issuance records the EXACT binding plus the frozen
    canonical frontier; the exact same call replayed (canonical
    argument equivalence, frontier order/duplicates canonicalized) is
    a pure REPLAYED no-op; any changed binding or frontier under the
    same call is a typed conflict preserving the EXACT state."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    first = observe_causal_history((read_request("responses", "first-occ"),), ns, boot.state, 1)
    assert first.outcome is CausalHistoryOutcome.ACCEPTED
    issued = register_issuance(
        first.state,
        ns,
        "iss-1",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        2,
    )
    assert issued.outcome is CausalHistoryOutcome.ACCEPTED
    assert issued.revision_before == 2
    assert issued.revision_after == 3
    assert len(issued.state.issuances) == 1
    assert issued.state.issuances[0].call_id == "iss-1"
    assert issued.state.issuances[0].parent_frontier == (CAUSAL_ROOT_FACT,)
    # Canonical argument equivalence + frontier order/duplicate
    # canonicalization: the SAME issued call replays.
    again = register_issuance(
        issued.state,
        ns,
        "iss-1",
        "responses",
        "exec_command",
        ISSUE_ARGS_CANONICAL_EQUIV,
        (CAUSAL_ROOT_FACT, CAUSAL_ROOT_FACT),
        3,
    )
    assert again.outcome is CausalHistoryOutcome.REPLAYED
    assert again.state is issued.state
    assert again.revision_after == 3
    # Changed arguments under the same call: typed conflict.
    changed_args = register_issuance(
        issued.state,
        ns,
        "iss-1",
        "responses",
        "exec_command",
        json.dumps({"cmd": "printf synthetic"}),
        (CAUSAL_ROOT_FACT,),
        3,
    )
    assert changed_args.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert CausalHistoryLimitation.ISSUANCE_CONFLICT in changed_args.diagnostics
    assert changed_args.state is issued.state
    # Changed frozen frontier under the same call: typed conflict.
    occ_id = first.state.occurrences[0].occurrence_id
    changed_frontier = register_issuance(
        issued.state,
        ns,
        "iss-1",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (occ_id, CAUSAL_ROOT_FACT),
        3,
    )
    assert changed_frontier.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert CausalHistoryLimitation.ISSUANCE_CONFLICT in changed_frontier.diagnostics
    assert changed_frontier.state is issued.state


@pytest.mark.parametrize("mode", MODES)
def test_issuance_frontier_shape_and_known_fact_laws(mode: AdmissionMode) -> None:
    """Frontier law: empty frontier is a malformed binding; a
    malformed member and an UNKNOWN 64-hex member refuse with
    FRONTIER_CONFLICT; the root fact is a known fact ONLY while the
    anchor is retained; all refusals preserve the EXACT state."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    empty_frontier = register_issuance(
        boot.state, ns, "iss-e", "responses", "exec_command", ISSUE_ARGS, (), 1
    )
    assert empty_frontier.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert CausalHistoryLimitation.MALFORMED_BINDING in empty_frontier.diagnostics
    assert empty_frontier.state is boot.state
    unknown = register_issuance(
        boot.state,
        ns,
        "iss-u",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        ("f" * 64,),
        1,
    )
    assert unknown.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert CausalHistoryLimitation.FRONTIER_CONFLICT in unknown.diagnostics
    assert unknown.state is boot.state
    malformed_member = register_issuance(
        boot.state,
        ns,
        "iss-m",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        ("not-a-fact-id",),
        1,
    )
    assert malformed_member.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert CausalHistoryLimitation.FRONTIER_CONFLICT in malformed_member.diagnostics
    assert malformed_member.state is boot.state
    # The root fact is unknown WITHOUT a retained anchor (exact empty
    # state: no anchor was ever acquired).
    empty = empty_state(ns)
    root_fact_no_root = register_issuance(
        empty,
        ns,
        "iss-r",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        0,
    )
    assert root_fact_no_root.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert CausalHistoryLimitation.FRONTIER_CONFLICT in root_fact_no_root.diagnostics
    assert root_fact_no_root.state is empty


@pytest.mark.parametrize("mode", MODES)
def test_issuance_reused_observed_id_law(mode: AdmissionMode) -> None:
    """A call ID already carrying OBSERVED evidence cannot be issued
    under a different immutable binding; the SAME binding issues
    cleanly and leaves the observed occurrence UNANCHORED (issuance
    is not acquisition or anchoring)."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    observed = observe_causal_history((read_request("responses", "obs-1"),), ns, boot.state, 1)
    assert observed.outcome is CausalHistoryOutcome.ACCEPTED
    different_name = register_issuance(
        observed.state,
        ns,
        "obs-1",
        "responses",
        "other_tool",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        2,
    )
    assert different_name.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert CausalHistoryLimitation.ISSUANCE_CONFLICT in different_name.diagnostics
    assert different_name.state is observed.state
    same_binding = register_issuance(
        observed.state,
        ns,
        "obs-1",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        2,
    )
    assert same_binding.outcome is CausalHistoryOutcome.ACCEPTED
    assert same_binding.state.occurrences[0].anchored is False
    assert len(same_binding.state.issuances) == 1


@pytest.mark.parametrize("mode", MODES)
def test_issuance_cas_scope_and_retention_laws(mode: AdmissionMode) -> None:
    """CAS mismatch and foreign scope refuse before any work; the
    actual frontier length is prefilled BEFORE dedup; the cumulative
    issuance cap refuses before retention; the EXACT state is
    preserved in every refusal."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    cas = register_issuance(
        boot.state,
        ns,
        "iss-c",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        99,
    )
    assert cas.outcome is CausalHistoryOutcome.REFUSED_CAS_MISMATCH
    assert cas.state is boot.state
    foreign_ns = make_ns(mode, lineage="foreign-lineage")
    foreign = register_issuance(
        boot.state,
        foreign_ns,
        "iss-f",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        1,
    )
    assert foreign.outcome is CausalHistoryOutcome.REFUSED_FOREIGN_SCOPE
    assert foreign.state is boot.state
    # Actual length BEFORE dedup: three members cross max=2 even
    # though the canonical frontier has one distinct fact.
    ns_len = make_ns(mode, history_bounds=HistoryBounds(max_frontier_members=2))
    boot_len = observe_causal_history((root_request(),), ns_len, empty_state(ns_len), 0)
    assert boot_len.outcome is CausalHistoryOutcome.ACCEPTED
    over = register_issuance(
        boot_len.state,
        ns_len,
        "iss-l",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT, CAUSAL_ROOT_FACT, CAUSAL_ROOT_FACT),
        1,
    )
    assert over.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert CausalHistoryLimitation.FRONTIER_OVER_BOUND in over.diagnostics
    assert over.state is boot_len.state
    # Cumulative issuance cap: one retained, the second refuses.
    ns_cap = make_ns(mode, history_bounds=HistoryBounds(max_issuances=1))
    boot_cap = observe_causal_history((root_request(),), ns_cap, empty_state(ns_cap), 0)
    assert boot_cap.outcome is CausalHistoryOutcome.ACCEPTED
    first = register_issuance(
        boot_cap.state,
        ns_cap,
        "iss-a",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        1,
    )
    assert first.outcome is CausalHistoryOutcome.ACCEPTED
    second = register_issuance(
        first.state,
        ns_cap,
        "iss-b",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        2,
    )
    assert second.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert CausalHistoryLimitation.ISSUANCES_OVER_BOUND in second.diagnostics
    assert second.state is first.state


@pytest.mark.parametrize("mode", MODES)
def test_receipt_anchors_unanchored_occurrence(mode: AdmissionMode) -> None:
    """A late trusted receipt anchors an UNANCHORED completed
    occurrence under its trusted issuance's COMPLETE frozen frontier
    (stored edges == frontier, no omitted parents); an exact receipt
    replay is a pure REPLAYED no-op; the revision advances exactly
    once per accepted anchoring."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    read = observe_causal_history((read_request("responses", "rec-1"),), ns, boot.state, 1)
    assert read.outcome is CausalHistoryOutcome.ACCEPTED
    assert read.state.occurrences[0].anchored is False
    issued = register_issuance(
        read.state,
        ns,
        "rec-1",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        2,
    )
    assert issued.outcome is CausalHistoryOutcome.ACCEPTED
    occ_id = read.state.occurrences[0].occurrence_id
    anchored = _receipt(issued.state, ns, "rec-1", (CAUSAL_ROOT_FACT,), 3)
    assert anchored.outcome is CausalHistoryOutcome.ACCEPTED
    assert anchored.revision_before == 3
    assert anchored.revision_after == 4
    assert anchored.state.occurrences[0].anchored is True
    assert anchored.state.parent_links == (ParentLink(child=occ_id, parent=CAUSAL_ROOT_FACT),)
    again = _receipt(anchored.state, ns, "rec-1", (CAUSAL_ROOT_FACT,), 4)
    assert again.outcome is CausalHistoryOutcome.REPLAYED
    assert again.state is anchored.state
    assert again.revision_after == 4


@pytest.mark.parametrize("mode", MODES)
def test_receipt_without_prior_issuance_creates_it(mode: AdmissionMode) -> None:
    """A receipt with no prior issuance for the call is the trusted
    issuance itself: ONE issuance is created, the unanchored
    occurrence is anchored under the receipt's frozen frontier."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    read = observe_causal_history((read_request("responses", "rec-2"),), ns, boot.state, 1)
    assert read.outcome is CausalHistoryOutcome.ACCEPTED
    anchored = _receipt(read.state, ns, "rec-2", (CAUSAL_ROOT_FACT,), 2)
    assert anchored.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(anchored.state.issuances) == 1
    assert anchored.state.issuances[0].call_id == "rec-2"
    assert anchored.state.occurrences[0].anchored is True
    assert len(anchored.state.parent_links) == 1


@pytest.mark.parametrize("mode", MODES)
def test_receipt_mismatch_unknown_parent_and_cycle(mode: AdmissionMode) -> None:
    """Receipt refusal law: a changed binding, an unknown call, an
    unknown frontier parent and a cycle (including the self-member
    case and a genuine multi-edge cycle through a descendant) all
    refuse atomically with the exact closed diagnostics, the EXACT
    prior state preserved."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    read = observe_causal_history((read_request("responses", "rec-3"),), ns, boot.state, 1)
    assert read.outcome is CausalHistoryOutcome.ACCEPTED
    occ_id = read.state.occurrences[0].occurrence_id
    changed_binding = _receipt(
        read.state,
        ns,
        "rec-3",
        (CAUSAL_ROOT_FACT,),
        2,
        args=json.dumps({"cmd": "printf synthetic"}),
    )
    assert changed_binding.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert CausalHistoryLimitation.RECEIPT_BINDING_MISMATCH in changed_binding.diagnostics
    assert changed_binding.state is read.state
    unknown_call = _receipt(read.state, ns, "never-seen", (CAUSAL_ROOT_FACT,), 2)
    assert unknown_call.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert CausalHistoryLimitation.RECEIPT_BINDING_MISMATCH in unknown_call.diagnostics
    assert unknown_call.state is read.state
    unknown_parent = _receipt(read.state, ns, "rec-3", ("f" * 64, CAUSAL_ROOT_FACT), 2)
    assert unknown_parent.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert CausalHistoryLimitation.RECEIPT_UNKNOWN_PARENT in unknown_parent.diagnostics
    assert unknown_parent.state is read.state
    # Self-member cycle: the child in its own frozen frontier.
    self_cycle = _receipt(read.state, ns, "rec-3", (occ_id, CAUSAL_ROOT_FACT), 2)
    assert self_cycle.outcome is CausalHistoryOutcome.REFUSED_CYCLE
    assert CausalHistoryLimitation.RECEIPT_CYCLE in self_cycle.diagnostics
    assert self_cycle.state is read.state
    # Genuine cycle: B anchored under {A, root}; a receipt for A
    # under {B, root} would close A <- B <- A.
    pair = observe_causal_history(
        (
            read_request("responses", "cyc-a"),
            read_request("responses", "cyc-b"),
        ),
        ns,
        read.state,
        2,
    )
    assert pair.outcome is CausalHistoryOutcome.ACCEPTED
    a_occ = next(o for o in pair.state.occurrences if o.call_id == "cyc-a")
    b_occ = next(o for o in pair.state.occurrences if o.call_id == "cyc-b")
    issued_b = register_issuance(
        pair.state,
        ns,
        "cyc-b",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (a_occ.occurrence_id, CAUSAL_ROOT_FACT),
        3,
    )
    assert issued_b.outcome is CausalHistoryOutcome.ACCEPTED
    anchored_b = _receipt(
        issued_b.state,
        ns,
        "cyc-b",
        (a_occ.occurrence_id, CAUSAL_ROOT_FACT),
        4,
    )
    assert anchored_b.outcome is CausalHistoryOutcome.ACCEPTED
    cycle = _receipt(
        anchored_b.state,
        ns,
        "cyc-a",
        (b_occ.occurrence_id, CAUSAL_ROOT_FACT),
        5,
    )
    assert cycle.outcome is CausalHistoryOutcome.REFUSED_CYCLE
    assert CausalHistoryLimitation.RECEIPT_CYCLE in cycle.diagnostics
    assert cycle.state is anchored_b.state


@pytest.mark.parametrize("mode", MODES)
def test_receipt_causal_links_over_bound(mode: AdmissionMode) -> None:
    """The cumulative causal-link cap is checked BEFORE any edge is
    retained: a two-known-member frontier crosses
    max_causal_links=1 (after the known-fact and cycle laws pass)
    and refuses whole-empty with the EXACT prior state."""
    ns = make_ns(mode, history_bounds=HistoryBounds(max_causal_links=1))
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    read = observe_causal_history(
        (
            read_request("responses", "rec-l"),
            read_request("responses", "other-l"),
        ),
        ns,
        boot.state,
        1,
    )
    assert read.outcome is CausalHistoryOutcome.ACCEPTED
    other_occ = next(o for o in read.state.occurrences if o.call_id == "other-l")
    refused = _receipt(read.state, ns, "rec-l", (other_occ.occurrence_id, CAUSAL_ROOT_FACT), 2)
    assert refused.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert CausalHistoryLimitation.CAUSAL_LINKS_OVER_BOUND in refused.diagnostics
    assert refused.state is read.state


@pytest.mark.parametrize("mode", MODES)
def test_relation_laws_and_receipt_order_never_a_clock(mode: AdmissionMode) -> None:
    """Relation law: SAME only for the same KNOWN occurrence; unknown
    or equal-unknown IDs are UNKNOWN; BEFORE/AFTER hold ONLY through
    the frozen parent evidence (receipt ORDER never a clock); two
    known unconnected events are INCOMPARABLE; foreign scope and
    malformed endpoints refuse with explicit fixed errors."""
    ns = make_ns(mode)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    reads = observe_causal_history(
        (
            read_request("responses", "rel-a"),
            read_request("responses", "rel-b"),
            read_request("responses", "rel-c"),
        ),
        ns,
        boot.state,
        1,
    )
    assert reads.outcome is CausalHistoryOutcome.ACCEPTED
    a_occ = next(o for o in reads.state.occurrences if o.call_id == "rel-a")
    b_occ = next(o for o in reads.state.occurrences if o.call_id == "rel-b")
    c_occ = next(o for o in reads.state.occurrences if o.call_id == "rel-c")
    # Unconnected known events: INCOMPARABLE in BOTH directions
    # (never ordered by list/registration position).
    assert (
        relation(reads.state, ns, c_occ.occurrence_id, a_occ.occurrence_id)
        is CausalRelation.INCOMPARABLE
    )
    assert (
        relation(reads.state, ns, a_occ.occurrence_id, c_occ.occurrence_id)
        is CausalRelation.INCOMPARABLE
    )
    assert (
        relation(reads.state, ns, a_occ.occurrence_id, a_occ.occurrence_id) is CausalRelation.SAME
    )
    unknown = "f" * 64
    assert relation(reads.state, ns, unknown, unknown) is CausalRelation.UNKNOWN
    assert relation(reads.state, ns, unknown, a_occ.occurrence_id) is CausalRelation.UNKNOWN
    # Anchor A under {root}; anchor B under {A, root}.
    issued_a = register_issuance(
        reads.state,
        ns,
        "rel-a",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        2,
    )
    assert issued_a.outcome is CausalHistoryOutcome.ACCEPTED
    anchored_a = _receipt(issued_a.state, ns, "rel-a", (CAUSAL_ROOT_FACT,), 3)
    assert anchored_a.outcome is CausalHistoryOutcome.ACCEPTED
    issued_b = register_issuance(
        anchored_a.state,
        ns,
        "rel-b",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (a_occ.occurrence_id, CAUSAL_ROOT_FACT),
        4,
    )
    assert issued_b.outcome is CausalHistoryOutcome.ACCEPTED
    anchored_b = _receipt(
        issued_b.state,
        ns,
        "rel-b",
        (a_occ.occurrence_id, CAUSAL_ROOT_FACT),
        5,
    )
    assert anchored_b.outcome is CausalHistoryOutcome.ACCEPTED
    assert (
        relation(anchored_b.state, ns, a_occ.occurrence_id, b_occ.occurrence_id)
        is CausalRelation.BEFORE
    )
    assert (
        relation(anchored_b.state, ns, b_occ.occurrence_id, a_occ.occurrence_id)
        is CausalRelation.AFTER
    )
    assert (
        relation(anchored_b.state, ns, a_occ.occurrence_id, a_occ.occurrence_id)
        is CausalRelation.SAME
    )
    # Unrelated C stays INCOMPARABLE to both anchored facts.
    assert (
        relation(anchored_b.state, ns, c_occ.occurrence_id, b_occ.occurrence_id)
        is CausalRelation.INCOMPARABLE
    )
    # Receipt ORDER never a clock: a fresh lineage where B is
    # received BEFORE A still yields BEFORE(A, B) (the edges are
    # frozen at issuance, not by arrival order).
    fresh = make_ns(mode, lineage="receipt-order-lineage")
    fboot = observe_causal_history((root_request(),), fresh, empty_state(fresh), 0)
    fread = observe_causal_history(
        (
            read_request("responses", "ord-a"),
            read_request("responses", "ord-b"),
        ),
        fresh,
        fboot.state,
        1,
    )
    assert fread.outcome is CausalHistoryOutcome.ACCEPTED
    oa = next(o for o in fread.state.occurrences if o.call_id == "ord-a")
    ob = next(o for o in fread.state.occurrences if o.call_id == "ord-b")
    f_issued_a = register_issuance(
        fread.state,
        fresh,
        "ord-a",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        2,
    )
    f_issued_b = register_issuance(
        fread.state,
        fresh,
        "ord-b",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (oa.occurrence_id, CAUSAL_ROOT_FACT),
        3,
    )
    # A stale expected revision against the OLD state is the CAS
    # refusal: the revision is a CAS/serialization fence, never a
    # clock, and the refusal preserves the EXACT prior state.
    assert f_issued_b.outcome is CausalHistoryOutcome.REFUSED_CAS_MISMATCH
    assert f_issued_b.state is fread.state
    f_issued_b2 = register_issuance(
        f_issued_a.state,
        fresh,
        "ord-b",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        (oa.occurrence_id, CAUSAL_ROOT_FACT),
        3,
    )
    assert f_issued_b2.outcome is CausalHistoryOutcome.ACCEPTED
    # Receive B FIRST (its issuance already exists), then A.
    f_receipt_b = _receipt(
        f_issued_b2.state, fresh, "ord-b", (oa.occurrence_id, CAUSAL_ROOT_FACT), 4
    )
    assert f_receipt_b.outcome is CausalHistoryOutcome.ACCEPTED
    f_receipt_a = _receipt(f_receipt_b.state, fresh, "ord-a", (CAUSAL_ROOT_FACT,), 5)
    assert f_receipt_a.outcome is CausalHistoryOutcome.ACCEPTED
    assert (
        relation(f_receipt_a.state, fresh, oa.occurrence_id, ob.occurrence_id)
        is CausalRelation.BEFORE
    )
    # Foreign scope and malformed endpoints: explicit fixed errors.
    foreign = make_ns(mode, lineage="relation-foreign-lineage")
    with pytest.raises(ValueError, match="own history scope"):
        relation(f_receipt_a.state, foreign, oa.occurrence_id, ob.occurrence_id)
    with pytest.raises(ValueError, match="64-hex occurrence IDs"):
        relation(f_receipt_a.state, fresh, "x" * 64, ob.occurrence_id)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_issuance_rebinds_observed_poll_id_refused(mode: AdmissionMode, endpoint: str) -> None:
    """A retained chain's poll ID is retained OBSERVED binding
    evidence (through the complete result's per-piece bindings, not
    only the result's own call ID): a trusted issuance that re-binds
    that ID to a DIFFERENT immutable binding is a typed
    ISSUANCE_CONFLICT with the EXACT prior state preserved, while the
    SAME observed binding is honored (accepted, then a pure REPLAYED
    exact replay).  Both read endpoints, both namespace modes."""
    ns = make_ns(mode, lineage=f"issuance-poll-{mode.value}-{endpoint}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    pending = observe_causal_history(
        (chain_request(endpoint, "iss-exec", PENDING_BODY),), ns, boot.state, 1
    )
    assert pending.outcome is CausalHistoryOutcome.ACCEPTED
    completed = observe_causal_history(
        (
            chain_request(
                endpoint,
                "iss-exec",
                PENDING_BODY,
                poll_cid="iss-poll",
                poll_text=terminal_frame(PENDING_TAIL),
            ),
        ),
        ns,
        pending.state,
        2,
    )
    assert completed.outcome is CausalHistoryOutcome.ACCEPTED
    occ = completed.state.occurrences[0]
    assert occ.proof.source_text == PENDING_BODY + PENDING_TAIL
    assert occ.proof.source_digest == sha256_hex(PENDING_BODY + PENDING_TAIL)
    assert occ.proof.pieces[1].call_id == "iss-poll"
    record = next(r for r in completed.state.results if r.call_id == "iss-exec")
    assert record.complete is True
    assert record.piece_call_bindings[1][:2] == ("iss-poll", endpoint)
    rebind = register_issuance(
        completed.state,
        ns,
        "iss-poll",
        endpoint,
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        3,
    )
    assert rebind.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert rebind.diagnostics == (CausalHistoryLimitation.ISSUANCE_CONFLICT,)
    assert rebind.state is completed.state
    assert rebind.revision_before == 3
    assert rebind.revision_after == 3
    same = register_issuance(
        completed.state,
        ns,
        "iss-poll",
        endpoint,
        "write_stdin",
        poll_arguments(CHAIN_SESSION),
        (CAUSAL_ROOT_FACT,),
        3,
    )
    assert same.outcome is CausalHistoryOutcome.ACCEPTED
    assert same.state is not completed.state
    assert same.state.issuances[0].call_id == "iss-poll"
    assert same.state.issuances[0].parent_frontier == (CAUSAL_ROOT_FACT,)
    replay = register_issuance(
        same.state,
        ns,
        "iss-poll",
        endpoint,
        "write_stdin",
        poll_arguments(CHAIN_SESSION),
        (CAUSAL_ROOT_FACT,),
        4,
    )
    assert replay.outcome is CausalHistoryOutcome.REPLAYED
    assert replay.state is same.state


class _IterationSentinel(list[str]):
    """A raw frontier list whose ITERATION raises: proves the raw
    length preflight happens BEFORE any tuple conversion, copy or
    dedup (a list length is an O(1) read, never an iteration)."""

    def __iter__(self) -> Iterator[str]:
        raise AssertionError("frontier iterated before the raw length preflight")


@pytest.mark.parametrize("mode", MODES)
def test_trusted_frontier_raw_length_before_any_copy(mode: AdmissionMode) -> None:
    """max_frontier_members bounds the RAW supplied member count
    BEFORE any tuple conversion/copy/dedup: a 2-member list at cap 1
    returns the fixed FRONTIER_OVER_BOUND typed refusal (no
    iteration, EXACT prior state preserved) for BOTH trusted
    registration and receipt; a 2-member list at cap 2 (one member
    after the charged canonical dedup) passes and is accepted with
    the canonical frontier retained."""
    ns = make_ns(
        mode,
        lineage=f"frontier-over-{mode.value}",
        history_bounds=HistoryBounds(max_frontier_members=1),
    )
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    over = register_issuance(
        boot.state,
        ns,
        "frontier-over",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        _IterationSentinel(["a" * 64, "b" * 64]),
        1,
    )
    assert over.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert over.diagnostics == (CausalHistoryLimitation.FRONTIER_OVER_BOUND,)
    assert over.state is boot.state
    over_receipt = register_receipt(
        boot.state,
        ns,
        "frontier-over",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        _IterationSentinel(["a" * 64, "b" * 64]),
        1,
    )
    assert over_receipt.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert over_receipt.diagnostics == (CausalHistoryLimitation.FRONTIER_OVER_BOUND,)
    assert over_receipt.state is boot.state
    at_limit_ns = make_ns(
        mode,
        lineage=f"frontier-atlimit-{mode.value}",
        history_bounds=HistoryBounds(max_frontier_members=2),
    )
    at_boot = observe_causal_history((root_request(),), at_limit_ns, empty_state(at_limit_ns), 0)
    assert at_boot.outcome is CausalHistoryOutcome.ACCEPTED
    at_limit = register_issuance(
        at_boot.state,
        at_limit_ns,
        "frontier-at",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        [CAUSAL_ROOT_FACT, CAUSAL_ROOT_FACT],
        1,
    )
    assert at_limit.outcome is CausalHistoryOutcome.ACCEPTED
    assert at_limit.state.issuances[0].parent_frontier == (CAUSAL_ROOT_FACT,)


def _linked_chain_state(
    mode: AdmissionMode,
    lineage: str,
    history_bounds: HistoryBounds,
    links: int,
) -> tuple[CausalHistoryNamespace, CausalHistoryState, list[str], int]:
    """Build the genuine ORIGINAL-API chain: root bootstrap plus
    ``links`` trusted-linked original reads (each read observed, then
    anchored by a receipt whose frozen frontier is the previous
    occurrence) and one final UNANCHORED target read.  Returns the
    namespace, the state, the linked occurrence IDs in order and the
    NEXT expected revision for the target state.  No fabricated state
    or proofs: every record came through the public transition APIs."""
    ns = make_ns(mode, lineage=lineage, history_bounds=history_bounds)
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    state: CausalHistoryState = boot.state
    revision = 1
    linked: list[str] = []
    for index in range(1, links + 1):
        cid = f"chain-{index:02d}"
        observed = observe_causal_history(
            (read_request("responses", cid, f"Synthetic chain read {index:02d}.\n"),),
            ns,
            state,
            revision,
        )
        assert observed.outcome is CausalHistoryOutcome.ACCEPTED
        state = observed.state
        revision += 1
        occ_id = next(o.occurrence_id for o in state.occurrences if o.call_id == cid)
        frontier = (CAUSAL_ROOT_FACT,) if not linked else (linked[-1],)
        anchored = register_receipt(
            state, ns, cid, "responses", "exec_command", ISSUE_ARGS, frontier, revision
        )
        assert anchored.outcome is CausalHistoryOutcome.ACCEPTED
        state = anchored.state
        revision += 1
        linked.append(occ_id)
    target = observe_causal_history(
        (read_request("responses", "target-01", "Synthetic target read.\n"),),
        ns,
        state,
        revision,
    )
    assert target.outcome is CausalHistoryOutcome.ACCEPTED
    return ns, target.state, linked, revision + 1


@pytest.mark.parametrize("mode", MODES)
def test_receipt_ancestry_work_overflow_typed_refusal(mode: AdmissionMode) -> None:
    """The receipt's charged acyclicity closures share the ONE
    per-transition work ledger: a genuine 40-linked-read state at
    max_work_units=1024 whose receipt frontier is ALL 40 known
    ancestors crosses the ledger and returns the atomic typed
    REFUSED_OVER_BOUND / WORK_UNITS_OVER_BOUND transition with the
    EXACT old state preserved (never an uncaught error).  The
    bounded relation query still answers BEFORE inside budget, and
    the SAME construction at the default work ceiling accepts."""
    tight = HistoryBounds(max_work_units=1024)
    ns, target_state, linked, revision = _linked_chain_state(
        mode, f"receipt-work-over-{mode.value}", tight, 40
    )
    target_id = next(o.occurrence_id for o in target_state.occurrences if o.call_id == "target-01")
    first_id, last_id = linked[0], linked[-1]
    assert relation(target_state, ns, first_id, last_id) is CausalRelation.BEFORE
    # The unanchored target carries NO temporal edge: it never becomes
    # AFTER (or BEFORE) a known fact merely by existing in the state.
    assert relation(target_state, ns, target_id, last_id) is CausalRelation.INCOMPARABLE
    over = register_receipt(
        target_state,
        ns,
        "target-01",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        tuple(sorted(linked)),
        revision,
    )
    assert over.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert over.diagnostics == (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,)
    assert over.state is target_state
    assert over.revision_before == revision
    assert over.revision_after == revision
    relaxed_ns, relaxed_state, relaxed_linked, relaxed_revision = _linked_chain_state(
        mode, f"receipt-work-at-{mode.value}", HistoryBounds(), 40
    )
    accepted = register_receipt(
        relaxed_state,
        relaxed_ns,
        "target-01",
        "responses",
        "exec_command",
        ISSUE_ARGS,
        tuple(sorted(relaxed_linked)),
        relaxed_revision,
    )
    assert accepted.outcome is CausalHistoryOutcome.ACCEPTED
    assert accepted.revision_after == relaxed_revision + 1
    target_occ = next(o for o in accepted.state.occurrences if o.call_id == "target-01")
    assert target_occ.anchored is True
    assert len(accepted.state.parent_links) == len(relaxed_state.parent_links) + 40


@pytest.mark.parametrize("mode", MODES)
def test_validator_piece_binding_conflict_law(mode: AdmissionMode) -> None:
    """The bounded charged state validation enforces the immutable
    same-ID law over EVERY retained observed call fact, including
    per-piece bindings: two retained result records whose piece
    bindings carry the SAME poll ID under DIFFERENT immutable
    bindings refuse with RESULT_CONFLICT; the SAME poll ID under a
    DIFFERENT initial-EXEC owner refuses as well even when the
    binding, span bytes and status all match (owner reassignment is
    never authorized); a single-owner consistent record stays
    coherent (no issuance is invented)."""
    ns = make_ns(mode, lineage=f"validator-piece-{mode.value}")
    fp_exec = canonical_fp("exec_command", ISSUE_ARGS)
    fp_poll = canonical_fp("write_stdin", poll_arguments(CHAIN_SESSION))
    digest = sha256_hex("val-piece")
    session = sha256_hex("val-nosession")

    def _record(call_id: str, poll_endpoint: str) -> ResultFingerprintRecord:
        return ResultFingerprintRecord(
            call_id=call_id,
            endpoint="responses",
            tool_name="exec_command",
            argument_fingerprint=fp_exec,
            result_fingerprint=sha256_hex(f"val-result-{call_id}"),
            complete=True,
            first_request_index=0,
            session_digest=session,
            piece_facts=((0, 3, 3, digest),),
            piece_call_bindings=(("val-poll", poll_endpoint, "write_stdin", fp_poll),),
            piece_completion=(None,),
        )

    consistent = CausalHistoryState(
        history_key=ns.history_key,
        revision=0,
        results=(_record("val-e1", "responses"),),
    )
    assert validate_causal_history_state(consistent) is None
    # The SAME poll ID under a DIFFERENT initial-EXEC owner (binding,
    # span bytes and status all identical) is an owner reassignment.
    owner_conflict = CausalHistoryState(
        history_key=ns.history_key,
        revision=0,
        results=(_record("val-e1", "responses"), _record("val-e2", "responses")),
    )
    assert validate_causal_history_state(owner_conflict) is CausalHistoryLimitation.RESULT_CONFLICT
    # And still a conflict under a DIFFERENT immutable binding.
    conflict = CausalHistoryState(
        history_key=ns.history_key,
        revision=0,
        results=(_record("val-e1", "responses"), _record("val-e2", "chat")),
    )
    assert validate_causal_history_state(conflict) is CausalHistoryLimitation.RESULT_CONFLICT


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("version_field", ("history_version", "arguments_version"))
def test_relation_refuses_unsupported_actual_versions(
    mode: AdmissionMode, version_field: str
) -> None:
    """The relation query applies the SAME fail-closed actual-version
    law as the transitions: a coherent namespace whose ACTUAL
    history/arguments version is unsupported (matching scope keys,
    previously acquired source) refuses with a fixed query error
    BEFORE any positive interpretation -- never a false SAME/UNKNOWN
    over acquired source.  The supported surface keeps answering
    (SAME for the same known ID)."""
    ns = make_ns(mode, lineage=f"query-version-{mode.value}-{version_field}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    first = observe_causal_history((read_request("responses", "qv-occ"),), ns, boot.state, 1)
    assert first.outcome is CausalHistoryOutcome.ACCEPTED
    occ = first.state.occurrences[0]
    assert relation(first.state, ns, occ.occurrence_id, occ.occurrence_id) is CausalRelation.SAME
    # (1) STALE-KEY tamper: the ACTUAL unsupported version is bound but
    # the SUPPORTED scope keys are left unchanged (a model_copy never
    # recomputes).  The keys still match the acquired state, so the
    # refusal must come from the version law, not a scope mismatch.
    stale = ns.model_copy(update={version_field: "unsupported-causal-history/v0"})
    assert stale.history_key == ns.history_key
    with pytest.raises(ValueError, match="supported actual versions"):
        relation(first.state, stale, occ.occurrence_id, occ.occurrence_id)
    # (2) COHERENT DIRECT construction: every actual field carried
    # over, the ACTUAL unsupported version bound, and BOTH scope keys
    # correctly recomputed (the constructor revalidates them).  The
    # matching negative state metadata fixture carries the recomputed
    # key; the source was previously genuinely acquired under the
    # supported namespace, so this proves unsupported-POLICY refusal
    # independent of any stale-key rejection.
    bad = _direct_unsupported_ns(ns, version_field)
    assert bad.history_key != ns.history_key
    assert bad.history_version != CAUSAL_HISTORY_CONTRACT_VERSION or (
        bad.arguments_version != CAUSAL_ARGUMENTS_JSON_VERSION
    )
    bad_state = first.state.model_copy(update={"history_key": bad.history_key})
    assert bad_state.history_key == bad.history_key
    transition = observe_causal_history((), bad, bad_state, bad_state.revision)
    assert transition.outcome is CausalHistoryOutcome.REFUSED_VERSION_CONFLICT
    assert transition.state is bad_state
    with pytest.raises(ValueError, match="supported actual versions"):
        relation(bad_state, bad, occ.occurrence_id, occ.occurrence_id)


def _direct_unsupported_ns(
    ns: CausalHistoryNamespace, version_field: str
) -> CausalHistoryNamespace:
    """A coherent DIRECT-constructed causal-history scope carrying the
    ACTUAL unsupported version: all real fields copied from the
    supported namespace, the one version field replaced, and BOTH
    scope keys recomputed from the actual fields (the constructor
    revalidates the recomputation, so a stale key would raise)."""
    fields = {name: getattr(ns, name) for name in CausalHistoryNamespace.model_fields}
    fields[version_field] = "unsupported-synthetic/v99"
    canonical = {
        name: fields[name] for name in inspect.signature(_canonical_history_fields).parameters
    }
    canonical["mode"] = ns.mode.value
    fields["history_key"] = hashlib.sha256(_canonical_history_fields(**canonical)).hexdigest()
    fields["state_scoped_key"] = hashlib.sha256(
        (fields["history_key"] + "\0" + fields["workspace"]).encode()
    ).hexdigest()
    return CausalHistoryNamespace(**fields)


def _swap_frame(req: GraphRequest, endpoint: str, frame: str, poll: bool = False) -> GraphRequest:
    """Replace the exec (``poll=False``) or poll result frame of a
    rootless chain request.  A frame is a fixed prefix plus its
    output body, so swapping the whole frame is byte-exact carrier
    surgery on the ORIGINAL payload."""
    if endpoint == "responses":
        req.payload["input"][3 if poll else 1]["output"] = frame
    else:
        req.payload["messages"][3 if poll else 1]["content"] = frame
    return req


def _pending_base(
    mode: AdmissionMode, endpoint: str, tag: str
) -> tuple[CausalHistoryNamespace, CausalHistoryState, int]:
    """Root bootstrap + one genuine RUNNING pending observation
    (exact original 017 RUNNING piece precondition).  Returns the
    namespace, the pending transition state and its revision."""
    ns = make_ns(mode, lineage=f"pending-{tag}-{mode.value}-{endpoint}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    pending = observe_causal_history(
        (chain_request(endpoint, f"{tag}-exec", PENDING_BODY),), ns, boot.state, 1
    )
    assert pending.outcome is CausalHistoryOutcome.ACCEPTED
    assert not pending.state.occurrences
    assert len(pending.state.results) == 1
    assert pending.state.results[0].complete is False
    return ns, pending.state, pending.revision_after


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_pending_same_length_byte_mutation_refused(mode: AdmissionMode, endpoint: str) -> None:
    """Replaying a pending chain with the SAME-LENGTH but different
    original bytes is a typed conflict: lengths alone are NOT byte
    identity, the EXACT pending state is preserved, and no completed
    source is invented."""
    ns, state, revision = _pending_base(mode, endpoint, "pl")
    replacement = "Z" * (len(PENDING_BODY) - 1) + "\n"
    assert len(replacement) == len(PENDING_BODY) and replacement != PENDING_BODY
    mutated = _swap_frame(
        chain_request(endpoint, "pl-exec", PENDING_BODY), endpoint, running_frame(replacement)
    )
    result = observe_causal_history((mutated,), ns, state, revision)
    assert result.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert result.diagnostics == (CausalHistoryLimitation.RESULT_CONFLICT,)
    assert result.state is state
    assert result.revision_before == revision
    assert result.revision_after == revision


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_pending_mutated_seen_prefix_on_completion_refused(
    mode: AdmissionMode, endpoint: str
) -> None:
    """A completed chain whose ALREADY-SEEN initial frame bytes were
    mutated (same length) plus a legitimate final poll must refuse:
    the retained pending prefix digests are immutable byte identity,
    and the EXACT pending state is preserved (no completed source)."""
    ns, state, revision = _pending_base(mode, endpoint, "pm")
    replacement = "Z" * (len(PENDING_BODY) - 1) + "\n"
    assert len(replacement) == len(PENDING_BODY) and replacement != PENDING_BODY
    full = chain_request(
        endpoint,
        "pm-exec",
        PENDING_BODY,
        poll_cid="pm-poll",
        poll_text=terminal_frame(PENDING_TAIL),
    )
    corrupt = _swap_frame(full, endpoint, running_frame(replacement))
    result = observe_causal_history((corrupt,), ns, state, revision)
    assert result.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert result.diagnostics == (CausalHistoryLimitation.RESULT_CONFLICT,)
    assert result.state is state
    assert not result.state.occurrences


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_pending_changed_process_session_refused(mode: AdmissionMode, endpoint: str) -> None:
    """The immutable process-session association is retained per call:
    the SAME exec ID and SAME result body under a DIFFERENT chain
    session ID is a typed conflict (whole-body or source-digest
    equality alone cannot prove per-call result equality), EXACT
    pending state preserved."""
    ns, state, revision = _pending_base(mode, endpoint, "ps")
    changed = _swap_frame(
        chain_request(endpoint, "ps-exec", PENDING_BODY),
        endpoint,
        running_frame(PENDING_BODY, session_id=9002),
    )
    result = observe_causal_history((changed,), ns, state, revision)
    assert result.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert result.diagnostics == (CausalHistoryLimitation.RESULT_CONFLICT,)
    assert result.state is state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_completed_frames_resegmented_same_aggregate_source_refused(
    mode: AdmissionMode, endpoint: str
) -> None:
    """A completed two-frame chain resegmented so ONE byte moves from
    the initial frame to the final poll frame keeps the SAME
    whole-source digest and the SAME call IDs, but BOTH existing
    per-call result facts changed: the aggregate equality never
    re-opens the per-call byte law, so this is a typed conflict
    preserving the EXACT completed state (never a REPLAYED)."""
    ns, state, revision = _pending_base(mode, endpoint, "rs")
    completed = observe_causal_history(
        (
            chain_request(
                endpoint,
                "rs-exec",
                PENDING_BODY,
                poll_cid="rs-poll",
                poll_text=terminal_frame(PENDING_TAIL),
            ),
        ),
        ns,
        state,
        revision,
    )
    assert completed.outcome is CausalHistoryOutcome.ACCEPTED
    occ = completed.state.occurrences[0]
    assert occ.proof.source_text == PENDING_BODY + PENDING_TAIL
    assert occ.proof.source_digest == sha256_hex(PENDING_BODY + PENDING_TAIL)
    assert occ.proof.pieces[1].call_id == "rs-poll"
    resegmented = _swap_frame(
        chain_request(
            endpoint,
            "rs-exec",
            PENDING_BODY,
            poll_cid="rs-poll",
            poll_text=terminal_frame(PENDING_TAIL),
        ),
        endpoint,
        running_frame(PENDING_BODY[:-1]),
    )
    resegmented = _swap_frame(
        resegmented,
        endpoint,
        terminal_frame(PENDING_BODY[-1:] + PENDING_TAIL),
        poll=True,
    )
    result = observe_causal_history((resegmented,), ns, completed.state, completed.revision_after)
    assert result.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert result.diagnostics == (CausalHistoryLimitation.RESULT_CONFLICT,)
    assert result.state is completed.state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_old_initial_pending_replay_after_completion_is_noop(
    mode: AdmissionMode, endpoint: str
) -> None:
    """Re-observing the EXACT old initial running frame AFTER the
    chain completed is an idempotent no-op: the old frame is the
    EXACT old prefix of the retained per-call facts, so the completed
    state (revision, source, occurrences) is preserved unchanged --
    never a conflict, never a regression to pending."""
    ns, state, revision = _pending_base(mode, endpoint, "rp")
    completed = observe_causal_history(
        (
            chain_request(
                endpoint,
                "rp-exec",
                PENDING_BODY,
                poll_cid="rp-poll",
                poll_text=terminal_frame(PENDING_TAIL),
            ),
        ),
        ns,
        state,
        revision,
    )
    assert completed.outcome is CausalHistoryOutcome.ACCEPTED
    occ = completed.state.occurrences[0]
    assert occ.proof.source_text == PENDING_BODY + PENDING_TAIL
    replay = observe_causal_history(
        (chain_request(endpoint, "rp-exec", PENDING_BODY),),
        ns,
        completed.state,
        completed.revision_after,
    )
    assert replay.outcome is CausalHistoryOutcome.REPLAYED
    assert replay.state is completed.state
    assert replay.revision_before == completed.revision_after
    assert replay.revision_after == completed.revision_after


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_pending_old_prefix_replay_while_still_running_is_noop(
    mode: AdmissionMode, endpoint: str
) -> None:
    """Re-observing the EXACT old initial frame while the retained
    chain is still RUNNING with more known polls is an idempotent
    no-op: the extended retained facts (revision, pieces, poll
    bindings) are preserved, never regressed or re-stamped.  The
    extended fixture carries its ORIGINAL 017 RUNNING two-piece
    precondition (no eligibility shortcut)."""
    ns, state, revision = _pending_base(mode, endpoint, "pp")
    extended_req = chain_request(
        endpoint,
        "pp-exec",
        PENDING_BODY,
        poll_cid="pp-poll",
        poll_text=running_frame(PENDING_TAIL),
    )
    extended_evidence = observe_request(
        extended_req.payload,
        PathContext(workspace=WORKSPACE),
        ns.observation_bounds,
        endpoint,
    )
    assert len(extended_evidence.processes) == 1
    assert extended_evidence.processes[0].outcome is ProcessOutcome.RUNNING
    assert len(extended_evidence.processes[0].pieces) == 2
    assert (
        extended_evidence.processes[0].pieces[1].char_span.slice(running_frame(PENDING_TAIL))
        == PENDING_TAIL
    )
    extended = observe_causal_history((extended_req,), ns, state, revision)
    assert extended.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(extended.state.results[0].piece_facts) == 2
    prefix = observe_causal_history(
        (chain_request(endpoint, "pp-exec", PENDING_BODY),),
        ns,
        extended.state,
        extended.revision_after,
    )
    assert prefix.outcome is CausalHistoryOutcome.REPLAYED
    assert prefix.state is extended.state
    assert prefix.revision_before == extended.revision_after
    assert prefix.revision_after == extended.revision_after
    rec = prefix.state.results[0]
    assert len(rec.piece_facts) == 2
    assert rec.piece_call_bindings[1][0] == "pp-poll"


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_completed_same_frame_count_status_mutation_refused(
    mode: AdmissionMode, endpoint: str
) -> None:
    """A completed chain re-observed with the SAME frame count, IDs,
    arguments and slice bytes but a CHANGED terminal status (the
    final frame now running) is an immutable completion-fact
    mutation, never an old prefix: typed conflict, EXACT prior
    state, and a genuinely strictly-older prefix stays a no-op.
    Baseline and mutated fixtures both carry their ORIGINAL 017
    process-completeness preconditions (exact bundle digest for the
    COMPLETE baseline; RUNNING two-piece shape for the mutation),
    so the conflict is not an eligibility failure."""
    ns, state, revision = _pending_base(mode, endpoint, "sf")
    bundle = PENDING_BODY + PENDING_TAIL
    completed_req = chain_request(
        endpoint,
        "sf-exec",
        PENDING_BODY,
        poll_cid="sf-poll",
        poll_text=terminal_frame(PENDING_TAIL),
    )
    completed_evidence = observe_request(
        completed_req.payload,
        PathContext(workspace=WORKSPACE),
        ns.observation_bounds,
        endpoint,
    )
    assert len(completed_evidence.processes) == 1
    assert completed_evidence.processes[0].outcome is ProcessOutcome.COMPLETE
    assert completed_evidence.processes[0].bundle_digest == sha256_hex(bundle)
    completed = observe_causal_history((completed_req,), ns, state, revision)
    assert completed.outcome is CausalHistoryOutcome.ACCEPTED
    occurrence = completed.state.occurrences[0]
    assert occurrence.proof.source_text == bundle
    assert occurrence.proof.source_digest == sha256_hex(bundle)
    assert occurrence.proof.pieces[1].call_id == "sf-poll"
    mutated = _swap_frame(
        chain_request(
            endpoint,
            "sf-exec",
            PENDING_BODY,
            poll_cid="sf-poll",
            poll_text=terminal_frame(PENDING_TAIL),
        ),
        endpoint,
        running_frame(PENDING_TAIL),
        poll=True,
    )
    mutated_evidence = observe_request(
        mutated.payload,
        PathContext(workspace=WORKSPACE),
        ns.observation_bounds,
        endpoint,
    )
    assert len(mutated_evidence.processes) == 1
    assert mutated_evidence.processes[0].outcome is ProcessOutcome.RUNNING
    assert len(mutated_evidence.processes[0].pieces) == 2
    result = observe_causal_history((mutated,), ns, completed.state, completed.revision_after)
    assert result.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert result.diagnostics == (CausalHistoryLimitation.RESULT_CONFLICT,)
    assert result.state is completed.state
    # The genuinely strictly-older initial prefix stays a no-op.
    older = observe_causal_history(
        (chain_request(endpoint, "sf-exec", PENDING_BODY),),
        ns,
        completed.state,
        completed.revision_after,
    )
    assert older.outcome is CausalHistoryOutcome.REPLAYED
    assert older.state is completed.state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_cross_chain_same_poll_changed_result_bytes_refused(
    mode: AdmissionMode, endpoint: str
) -> None:
    """A poll ID's retained RESULT bytes are immutable across every
    chain: a second ORIGINAL complete chain reusing the SAME poll
    ID/tool/arguments/session with SAME-LENGTH but different poll
    output bytes is a typed whole-state conflict (EXACT prior
    state; no fabricated issuance or acquisition).  Baseline and
    second-chain fixtures both carry their ORIGINAL 017 COMPLETE
    preconditions with exact bundle digests (the second chain's
    digest differs only by the changed same-length poll slice), so
    the conflict is not an eligibility failure."""
    ns, state, revision = _pending_base(mode, endpoint, "pc")
    bundle = PENDING_BODY + PENDING_TAIL
    completed_req = chain_request(
        endpoint,
        "pc-exec",
        PENDING_BODY,
        poll_cid="pc-poll",
        poll_text=terminal_frame(PENDING_TAIL),
    )
    completed_evidence = observe_request(
        completed_req.payload,
        PathContext(workspace=WORKSPACE),
        ns.observation_bounds,
        endpoint,
    )
    assert len(completed_evidence.processes) == 1
    assert completed_evidence.processes[0].outcome is ProcessOutcome.COMPLETE
    assert completed_evidence.processes[0].bundle_digest == sha256_hex(bundle)
    completed = observe_causal_history((completed_req,), ns, state, revision)
    assert completed.outcome is CausalHistoryOutcome.ACCEPTED
    occurrence = completed.state.occurrences[0]
    assert occurrence.proof.source_text == bundle
    assert occurrence.proof.source_digest == sha256_hex(bundle)
    assert occurrence.proof.pieces[1].call_id == "pc-poll"
    mutated_tail = "X" * (len(PENDING_TAIL) - 1) + "\n"
    assert len(mutated_tail) == len(PENDING_TAIL) and mutated_tail != PENDING_TAIL
    other_req = chain_request(
        endpoint,
        "pc-exec2",
        PENDING_BODY,
        poll_cid="pc-poll",
        poll_text=terminal_frame(mutated_tail),
    )
    other_evidence = observe_request(
        other_req.payload,
        PathContext(workspace=WORKSPACE),
        ns.observation_bounds,
        endpoint,
    )
    assert len(other_evidence.processes) == 1
    assert other_evidence.processes[0].outcome is ProcessOutcome.COMPLETE
    assert other_evidence.processes[0].bundle_digest == sha256_hex(PENDING_BODY + mutated_tail)
    other = observe_causal_history((other_req,), ns, completed.state, completed.revision_after)
    assert other.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert other.diagnostics == (CausalHistoryLimitation.RESULT_CONFLICT,)
    assert other.state is completed.state
    assert other.state.results == completed.state.results


def _two_poll_chain(
    endpoint: str,
    cid: str,
    body: str,
    poll_a: str,
    frame_a: str,
    poll_b: str,
    frame_b: str,
    session_id: int = CHAIN_SESSION,
) -> GraphRequest:
    """One genuine three-frame native chain (exec + two causally
    associated write_stdin polls) on EITHER read endpoint."""
    exec_msg = {
        "role": "assistant",
        "tool_calls": [
            {
                "id": cid,
                "type": "function",
                "function": {
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat A.md"}),
                },
            }
        ],
    }
    if endpoint == "responses":
        items = [
            exec_call(cid),
            out_item(cid, running_frame(body, session_id)),
            {
                "type": "function_call",
                "call_id": poll_a,
                "name": "write_stdin",
                "arguments": poll_arguments(session_id),
            },
            out_item(poll_a, frame_a),
            {
                "type": "function_call",
                "call_id": poll_b,
                "name": "write_stdin",
                "arguments": poll_arguments(session_id),
            },
            out_item(poll_b, frame_b),
        ]
        payload: dict[str, Any] = {"input": items}
    else:
        messages: list[dict[str, Any]] = [
            exec_msg,
            {"role": "tool", "tool_call_id": cid, "content": running_frame(body, session_id)},
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": poll_a,
                        "type": "function",
                        "function": {
                            "name": "write_stdin",
                            "arguments": poll_arguments(session_id),
                        },
                    }
                ],
            },
            {"role": "tool", "tool_call_id": poll_a, "content": frame_a},
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": poll_b,
                        "type": "function",
                        "function": {
                            "name": "write_stdin",
                            "arguments": poll_arguments(session_id),
                        },
                    }
                ],
            },
            {"role": "tool", "tool_call_id": poll_b, "content": frame_b},
        ]
        payload = {"messages": messages}
    return GraphRequest(payload=payload, endpoint=endpoint, context=None)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_cross_chain_same_poll_changed_status_refused(mode: AdmissionMode, endpoint: str) -> None:
    """A poll ID's retained COMPLETION fact is immutable across every
    chain: a second ORIGINAL complete chain reusing the SAME poll
    ID/arguments/session and the SAME poll slice bytes, but with the
    poll frame now RUNNING (a new terminal poll appended), changes
    the selected per-frame completion status: typed conflict, EXACT
    prior state (byte identity alone is not result identity).
    Baseline and three-frame fixtures both carry their ORIGINAL 017
    COMPLETE preconditions with exact bundle digests (the three-
    frame chain appends one new terminal slice), so the conflict is
    not an eligibility failure."""
    ns, state, revision = _pending_base(mode, endpoint, "st")
    bundle = PENDING_BODY + PENDING_TAIL
    completed_req = chain_request(
        endpoint,
        "st-exec",
        PENDING_BODY,
        poll_cid="st-poll",
        poll_text=terminal_frame(PENDING_TAIL),
    )
    completed_evidence = observe_request(
        completed_req.payload,
        PathContext(workspace=WORKSPACE),
        ns.observation_bounds,
        endpoint,
    )
    assert len(completed_evidence.processes) == 1
    assert completed_evidence.processes[0].outcome is ProcessOutcome.COMPLETE
    assert completed_evidence.processes[0].bundle_digest == sha256_hex(bundle)
    completed = observe_causal_history((completed_req,), ns, state, revision)
    assert completed.outcome is CausalHistoryOutcome.ACCEPTED
    occurrence = completed.state.occurrences[0]
    assert occurrence.proof.source_text == bundle
    assert occurrence.proof.source_digest == sha256_hex(bundle)
    assert occurrence.proof.pieces[1].call_id == "st-poll"
    appended = "Synthetic appended output.\n"
    other = _two_poll_chain(
        endpoint,
        "st-exec2",
        PENDING_BODY,
        "st-poll",
        running_frame(PENDING_TAIL),
        "st-poll2",
        terminal_frame(appended),
    )
    other_evidence = observe_request(
        other.payload,
        PathContext(workspace=WORKSPACE),
        ns.observation_bounds,
        endpoint,
    )
    assert len(other_evidence.processes) == 1
    assert other_evidence.processes[0].outcome is ProcessOutcome.COMPLETE
    expected_digest = sha256_hex(bundle + appended)
    assert other_evidence.processes[0].bundle_digest == expected_digest
    result = observe_causal_history((other,), ns, completed.state, completed.revision_after)
    assert result.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert result.diagnostics == (CausalHistoryLimitation.RESULT_CONFLICT,)
    assert result.state is completed.state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_cross_chain_same_poll_owner_reassignment_refused(
    mode: AdmissionMode, endpoint: str
) -> None:
    """A poll call/result's evidenced initial-EXEC owner is immutable:
    a second ORIGINAL complete chain (even a genuinely trusted-issued
    descendant of the first exec) reusing the SAME poll ID with
    IDENTICAL bytes/status/session is an atomic RESULT_CONFLICT with
    the EXACT prior state -- old terminal poll history never completes
    a different exec.  The same second exec with a genuinely fresh
    poll ID (reusing the numeric backend session) is a legitimate
    descendant completion with the BEFORE relation."""
    ns, state, revision = _pending_base(mode, endpoint, "po")
    bundle = PENDING_BODY + PENDING_TAIL
    completed_req = chain_request(
        endpoint,
        "po-exec",
        PENDING_BODY,
        poll_cid="po-poll",
        poll_text=terminal_frame(PENDING_TAIL),
    )
    completed_evidence = observe_request(
        completed_req.payload,
        PathContext(workspace=WORKSPACE),
        ns.observation_bounds,
        endpoint,
    )
    assert completed_evidence.processes[0].outcome is ProcessOutcome.COMPLETE
    assert completed_evidence.processes[0].bundle_digest == sha256_hex(bundle)
    completed = observe_causal_history((completed_req,), ns, state, revision)
    assert completed.outcome is CausalHistoryOutcome.ACCEPTED
    occ1 = completed.state.occurrences[0]
    assert occ1.proof.source_text == bundle
    # Late valid receipt anchors the first exec under the root.
    anchored = register_receipt(
        completed.state,
        ns,
        "po-exec",
        endpoint,
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        completed.revision_after,
    )
    assert anchored.outcome is CausalHistoryOutcome.ACCEPTED
    occ1_id = next(o.occurrence_id for o in anchored.state.occurrences if o.call_id == "po-exec")
    # Trusted issuance: the second exec is a genuine descendant.
    issued = register_issuance(
        anchored.state,
        ns,
        "po-exec2",
        endpoint,
        "exec_command",
        ISSUE_ARGS,
        (occ1_id,),
        anchored.revision_after,
    )
    assert issued.outcome is CausalHistoryOutcome.ACCEPTED
    other_body = "Synthetic second source.\n"
    poached_req = chain_request(
        endpoint,
        "po-exec2",
        other_body,
        poll_cid="po-poll",
        poll_text=terminal_frame(PENDING_TAIL),
    )
    poached_evidence = observe_request(
        poached_req.payload,
        PathContext(workspace=WORKSPACE),
        ns.observation_bounds,
        endpoint,
    )
    assert poached_evidence.processes[0].outcome is ProcessOutcome.COMPLETE
    assert poached_evidence.processes[0].bundle_digest == sha256_hex(other_body + PENDING_TAIL)
    poached = observe_causal_history((poached_req,), ns, issued.state, issued.revision_after)
    assert poached.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert poached.diagnostics == (CausalHistoryLimitation.RESULT_CONFLICT,)
    assert poached.state is issued.state
    # Control: the same second exec with a FRESH poll ID is a
    # legitimate descendant completion (the numeric backend session
    # may be reused; it is never a clock or globally reserved).
    fresh_req = chain_request(
        endpoint,
        "po-exec2",
        other_body,
        poll_cid="po-poll2",
        poll_text=terminal_frame(PENDING_TAIL),
    )
    fresh_evidence = observe_request(
        fresh_req.payload,
        PathContext(workspace=WORKSPACE),
        ns.observation_bounds,
        endpoint,
    )
    assert fresh_evidence.processes[0].outcome is ProcessOutcome.COMPLETE
    assert fresh_evidence.processes[0].bundle_digest == sha256_hex(other_body + PENDING_TAIL)
    fresh = observe_causal_history((fresh_req,), ns, issued.state, issued.revision_after)
    assert fresh.outcome is CausalHistoryOutcome.ACCEPTED
    occ2 = next(o for o in fresh.state.occurrences if o.call_id == "po-exec2")
    assert occ2.proof.source_text == other_body + PENDING_TAIL
    assert occ2.proof.pieces[1].call_id == "po-poll2"
    assert relation(fresh.state, ns, occ1_id, occ2.occurrence_id) is CausalRelation.BEFORE


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_same_batch_running_growth_retains_latest_poll_binding(
    mode: AdmissionMode, endpoint: str
) -> None:
    """ONE batch whose first request is the initial RUNNING chain and
    whose second is the SAME chain extended by a new RUNNING poll
    retains the LATEST staged record (both pieces and the poll's
    actual observed binding, never the stale first snapshot); the
    reused observed poll ID is then a typed conflict (no fabricated
    issuance or acquisition)."""
    ns = make_ns(mode, lineage=f"sg-growth-{mode.value}-{endpoint}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    growth_req = chain_request(
        endpoint,
        "sg-exec",
        PENDING_BODY,
        poll_cid="sg-poll",
        poll_text=running_frame(PENDING_TAIL),
    )
    growth_evidence = observe_request(
        growth_req.payload,
        PathContext(workspace=WORKSPACE),
        ns.observation_bounds,
        endpoint,
    )
    assert growth_evidence.processes[0].outcome is ProcessOutcome.RUNNING
    assert len(growth_evidence.processes[0].pieces) == 2
    batch = (
        chain_request(endpoint, "sg-exec", PENDING_BODY),
        growth_req,
    )
    growth = observe_causal_history(batch, ns, boot.state, 1)
    assert growth.outcome is CausalHistoryOutcome.ACCEPTED
    assert growth.state.revision == 2
    record = next(r for r in growth.state.results if r.call_id == "sg-exec")
    assert record.complete is False
    assert len(record.piece_facts) == 2
    assert record.piece_call_bindings[1][0] == "sg-poll"
    assert record.first_request_index == 0
    reuse = observe_causal_history((read_request(endpoint, "sg-poll"),), ns, growth.state, 2)
    assert reuse.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert reuse.state is growth.state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_same_batch_cross_chain_changed_poll_result_refused(
    mode: AdmissionMode, endpoint: str
) -> None:
    """Staged same-batch owner law: ONE batch containing the complete
    E1/P chain and a second ORIGINAL complete chain reusing P with
    SAME-LENGTH CHANGED poll bytes is refused atomically with the
    EXACT prior state (the staged first chain's producer fact makes
    the second chain's P an owner reassignment under changed bytes);
    both fixtures carry their ORIGINAL 017 COMPLETE preconditions."""
    ns = make_ns(mode, lineage=f"sm-batch-{mode.value}-{endpoint}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    bundle = PENDING_BODY + PENDING_TAIL
    full_req = chain_request(
        endpoint,
        "sm-exec",
        PENDING_BODY,
        poll_cid="sm-poll",
        poll_text=terminal_frame(PENDING_TAIL),
    )
    full_evidence = observe_request(
        full_req.payload,
        PathContext(workspace=WORKSPACE),
        ns.observation_bounds,
        endpoint,
    )
    assert full_evidence.processes[0].outcome is ProcessOutcome.COMPLETE
    assert full_evidence.processes[0].bundle_digest == sha256_hex(bundle)
    mutated_tail = "X" * (len(PENDING_TAIL) - 1) + "\n"
    assert len(mutated_tail) == len(PENDING_TAIL) and mutated_tail != PENDING_TAIL
    other_req = chain_request(
        endpoint,
        "sm-exec2",
        PENDING_BODY,
        poll_cid="sm-poll",
        poll_text=terminal_frame(mutated_tail),
    )
    other_evidence = observe_request(
        other_req.payload,
        PathContext(workspace=WORKSPACE),
        ns.observation_bounds,
        endpoint,
    )
    assert other_evidence.processes[0].outcome is ProcessOutcome.COMPLETE
    assert other_evidence.processes[0].bundle_digest == sha256_hex(PENDING_BODY + mutated_tail)
    same_batch = observe_causal_history((full_req, other_req), ns, boot.state, 1)
    assert same_batch.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert same_batch.diagnostics == (CausalHistoryLimitation.RESULT_CONFLICT,)
    assert same_batch.state is boot.state
    assert same_batch.revision_after == boot.state.revision


@pytest.mark.parametrize("mode", MODES)
def test_trusted_canonical_work_exhaustion_resource_refusal(mode: AdmissionMode) -> None:
    """Canonical-argument work exhaustion under max_work_units=1 is a
    RESOURCE refusal for BOTH trusted registrations: the atomic typed
    REFUSED_OVER_BOUND/WORK_UNITS_OVER_BOUND with the EXACT prior
    state (work exhaustion is never a content conflict)."""
    ns = make_ns(
        mode,
        lineage=f"work-exhaust-{mode.value}",
        history_bounds=HistoryBounds(max_work_units=1),
    )
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    for op in (register_issuance, register_receipt):
        result = op(
            boot.state,
            ns,
            "w-call",
            "responses",
            "exec_command",
            ISSUE_ARGS,
            (CAUSAL_ROOT_FACT,),
            boot.state.revision,
        )
        assert result.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
        assert result.diagnostics == (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,)
        assert result.state is boot.state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_same_batch_pending_then_complete_first_result_provenance(
    mode: AdmissionMode, endpoint: str
) -> None:
    """ONE batch whose first request is the genuine RUNNING chain and
    whose second is the SAME call's complete chain retains the EARLIEST
    original result provenance (first_request_index 0) while the
    completed occurrence's proof keeps the first COMPLETE SOURCE index
    (1); one ACCEPTED transition, one revision increment."""
    ns = make_ns(mode, lineage=f"pv-provenance-{mode.value}-{endpoint}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    batch = (
        chain_request(endpoint, "pv-exec", PENDING_BODY),
        chain_request(
            endpoint,
            "pv-exec",
            PENDING_BODY,
            poll_cid="pv-poll",
            poll_text=terminal_frame(PENDING_TAIL),
        ),
    )
    result = observe_causal_history(batch, ns, boot.state, 1)
    assert result.outcome is CausalHistoryOutcome.ACCEPTED
    assert result.state.revision == 2
    occ = next(o for o in result.state.occurrences if o.call_id == "pv-exec")
    assert occ.proof.request_index == 1
    assert occ.proof.source_text == PENDING_BODY + PENDING_TAIL
    rec = next(r for r in result.state.results if r.call_id == "pv-exec")
    assert rec.first_request_index == 0
    assert rec.complete is True
    assert len(rec.piece_facts) == 2


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_pending_to_complete_at_limit_piece_retention(mode: AdmissionMode, endpoint: str) -> None:
    """Pending->complete UPGRADE replaces the pending piece retention
    (net accounting over the FINAL retained state, not prior+batch): at
    max_retained_pieces=2 the 1-piece RUNNING then 2-piece COMPLETE
    upgrade is accepted retaining exactly 2 proof pieces; at cap 1 the
    same upgrade refuses atomically with the EXACT prior state; a
    direct (non-upgrade) 2-piece complete at cap 2 is the control."""
    bundle = PENDING_BODY + PENDING_TAIL
    for cap in (1, 2):
        ns = make_ns(
            mode,
            lineage=f"piece-cap{cap}-{mode.value}-{endpoint}",
            history_bounds=HistoryBounds(max_retained_pieces=cap),
        )
        boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
        assert boot.outcome is CausalHistoryOutcome.ACCEPTED
        pending_req = chain_request(endpoint, f"rl{cap}-exec", PENDING_BODY)
        pending = observe_causal_history((pending_req,), ns, boot.state, 1)
        assert pending.outcome is CausalHistoryOutcome.ACCEPTED
        assert len(pending.state.results[0].piece_facts) == 1
        upgrade_req = chain_request(
            endpoint,
            f"rl{cap}-exec",
            PENDING_BODY,
            poll_cid=f"rl{cap}-poll",
            poll_text=terminal_frame(PENDING_TAIL),
        )
        upgrade_evidence = observe_request(
            upgrade_req.payload,
            PathContext(workspace=WORKSPACE),
            ns.observation_bounds,
            endpoint,
        )
        assert upgrade_evidence.processes[0].outcome is ProcessOutcome.COMPLETE
        assert upgrade_evidence.processes[0].bundle_digest == sha256_hex(bundle)
        upgrade = observe_causal_history((upgrade_req,), ns, pending.state, 2)
        if cap == 2:
            assert upgrade.outcome is CausalHistoryOutcome.ACCEPTED
            occurrence = upgrade.state.occurrences[0]
            assert len(occurrence.proof.pieces) == 2
            record = next(r for r in upgrade.state.results if r.call_id == f"rl{cap}-exec")
            assert record.complete is True
            assert len(record.piece_facts) == 2
            direct_req = chain_request(
                endpoint,
                f"rl{cap}d-exec",
                PENDING_BODY,
                poll_cid=f"rl{cap}d-poll",
                poll_text=terminal_frame(PENDING_TAIL),
            )
            direct = observe_causal_history((direct_req,), ns, boot.state, 1)
            assert direct.outcome is CausalHistoryOutcome.ACCEPTED
            assert len(direct.state.occurrences[0].proof.pieces) == 2
        else:
            assert upgrade.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
            assert upgrade.diagnostics == (CausalHistoryLimitation.RETAINED_PIECES_OVER_BOUND,)
            assert upgrade.state is pending.state


# --- Full new-bound matrix: at-limit / one-over (018-d law) --------------
#
# Every HistoryBounds field is exercised at its AT-LIMIT and ONE-OVER
# point with the typed whole-empty refusal and EXACT prior-state
# preservation.  max_frontier_members and max_work_units already have
# their dedicated durable controls above (raw frontier preflight;
# charged member/piece and receipt-ancestry work).


@pytest.mark.parametrize("mode", MODES)
def test_bound_max_issuances_at_limit_and_one_over(mode: AdmissionMode) -> None:
    """max_issuances counts retained issued-call bindings
    cumulatively: at the cap the last issuance is accepted; one more
    refuses with ISSUANCES_OVER_BOUND before any copy/retention."""
    ns = make_ns(
        mode, lineage=f"bound-issuances-{mode.value}", history_bounds=HistoryBounds(max_issuances=2)
    )
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    i1 = register_issuance(
        boot.state, ns, "bi-1", "responses", "exec_command", ISSUE_ARGS, (CAUSAL_ROOT_FACT,), 1
    )
    i2 = register_issuance(
        i1.state, ns, "bi-2", "responses", "exec_command", ISSUE_ARGS, (CAUSAL_ROOT_FACT,), 2
    )
    assert i1.outcome is CausalHistoryOutcome.ACCEPTED
    assert i2.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(i2.state.issuances) == 2
    i3 = register_issuance(
        i2.state, ns, "bi-3", "responses", "exec_command", ISSUE_ARGS, (CAUSAL_ROOT_FACT,), 3
    )
    assert i3.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert i3.diagnostics == (CausalHistoryLimitation.ISSUANCES_OVER_BOUND,)
    assert i3.state is i2.state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_bound_max_occurrences_at_limit_and_one_over(mode: AdmissionMode, endpoint: str) -> None:
    """max_occurrences counts retained completed read occurrences
    cumulatively: at the cap the last read is retained; the next
    distinct read refuses with OCCURRENCES_OVER_BOUND before
    retention (EXACT prior state)."""
    ns = make_ns(
        mode,
        lineage=f"bound-occurrences-{mode.value}-{endpoint}",
        history_bounds=HistoryBounds(max_occurrences=1),
    )
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    r1 = observe_causal_history((read_request(endpoint, "bo-1"),), ns, boot.state, 1)
    assert r1.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(r1.state.occurrences) == 1
    r2 = observe_causal_history((read_request(endpoint, "bo-2"),), ns, r1.state, 2)
    assert r2.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert r2.diagnostics == (CausalHistoryLimitation.OCCURRENCES_OVER_BOUND,)
    assert r2.state is r1.state


@pytest.mark.parametrize("mode", MODES)
def test_bound_max_causal_links_at_limit_and_one_over(mode: AdmissionMode) -> None:
    """max_causal_links counts retained unique immediate parent links
    cumulatively: the first receipt edge reaches the cap; the second
    receipt's edge refuses with CAUSAL_LINKS_OVER_BOUND before any
    edge/occurrence mutation (EXACT prior state)."""
    ns = make_ns(
        mode, lineage=f"bound-links-{mode.value}", history_bounds=HistoryBounds(max_causal_links=1)
    )
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    s = observe_causal_history((read_request("responses", "bl-1"),), ns, boot.state, 1).state
    s = observe_causal_history((read_request("responses", "bl-2"),), ns, s, 2).state
    c1 = register_receipt(
        s, ns, "bl-1", "responses", "exec_command", ISSUE_ARGS, (CAUSAL_ROOT_FACT,), 3
    )
    assert c1.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(c1.state.parent_links) == 1
    c2 = register_receipt(
        c1.state, ns, "bl-2", "responses", "exec_command", ISSUE_ARGS, (CAUSAL_ROOT_FACT,), 4
    )
    assert c2.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert c2.diagnostics == (CausalHistoryLimitation.CAUSAL_LINKS_OVER_BOUND,)
    assert c2.state is c1.state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_bound_max_observed_results_at_limit_and_one_over(
    mode: AdmissionMode, endpoint: str
) -> None:
    """max_observed_results counts retained immutable call-result
    fingerprint records cumulatively: a legacy read retains its
    derivable result record at observation; at the cap the next
    distinct read refuses with RESULTS_OVER_BOUND before retention."""
    ns = make_ns(
        mode,
        lineage=f"bound-results-{mode.value}-{endpoint}",
        history_bounds=HistoryBounds(max_observed_results=1),
    )
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    r1 = observe_causal_history((read_request(endpoint, "br-1"),), ns, boot.state, 1)
    assert r1.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(r1.state.results) == 1
    r2 = observe_causal_history((read_request(endpoint, "br-2"),), ns, r1.state, 2)
    assert r2.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert r2.diagnostics == (CausalHistoryLimitation.RESULTS_OVER_BOUND,)
    assert r2.state is r1.state


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_bound_max_retained_members_and_pieces_at_limit_and_one_over(
    mode: AdmissionMode, endpoint: str
) -> None:
    """max_retained_members / max_retained_pieces count retained proof
    member occurrences and piece/span records cumulatively BEFORE
    distinct-path slot width: 32 repeated operands at cap 32 are all
    retained, at cap 31 the batch refuses atomically (nothing
    retained); pieces accumulate across occurrences in ONE batch (cap
    2 retains both reads, cap 1 refuses the whole batch)."""
    body = READ_BODY * 32
    cmd = "cat " + " ".join(["A.md"] * 32)
    batch = root_read_batch(endpoint, "big", body=body, cmd=cmd)
    members_at = make_ns(
        mode,
        lineage=f"bound-members-{mode.value}-{endpoint}",
        history_bounds=HistoryBounds(max_retained_members=32),
    )
    at_limit = observe_causal_history(batch, members_at, empty_state(members_at), 0)
    assert at_limit.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(at_limit.state.occurrences[0].proof.requested_members) == 32
    members_over = make_ns(
        mode,
        lineage=f"bound-members-over-{mode.value}-{endpoint}",
        history_bounds=HistoryBounds(max_retained_members=31),
    )
    members_empty = empty_state(members_over)
    one_over = observe_causal_history(batch, members_over, members_empty, 0)
    assert one_over.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert one_over.diagnostics == (CausalHistoryLimitation.RETAINED_MEMBERS_OVER_BOUND,)
    assert one_over.state is members_empty
    assert one_over.state.occurrences == ()
    two_read_batch = (
        root_request(),
        read_request(endpoint, "bp-1"),
        read_request(endpoint, "bp-2"),
    )
    pieces_at = make_ns(
        mode,
        lineage=f"bound-pieces-{mode.value}-{endpoint}",
        history_bounds=HistoryBounds(max_retained_pieces=2),
    )
    pieces_ok = observe_causal_history(two_read_batch, pieces_at, empty_state(pieces_at), 0)
    assert pieces_ok.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(pieces_ok.state.occurrences) == 2
    pieces_over = make_ns(
        mode,
        lineage=f"bound-pieces-over-{mode.value}-{endpoint}",
        history_bounds=HistoryBounds(max_retained_pieces=1),
    )
    pieces_refused = observe_causal_history(
        two_read_batch, pieces_over, empty_state(pieces_over), 0
    )
    assert pieces_refused.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert pieces_refused.diagnostics == (CausalHistoryLimitation.RETAINED_PIECES_OVER_BOUND,)
    assert pieces_refused.state.occurrences == ()


ROOT_ANCHOR_BYTES = 33  # exact retained root source (see RootAnchor)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_bound_max_retained_source_bytes_at_limit_and_one_over(
    mode: AdmissionMode, endpoint: str
) -> None:
    """max_retained_source_bytes = root anchor ONCE plus exact UTF-8
    proof-source bytes per newly retained occurrence, cumulative and
    pre-copy: root (33) + 4 + 4 is exactly at cap 41; cap 40 the
    second read crosses and refuses atomically; cap 32 the root
    bootstrap itself refuses.  EXACT prior state on every refusal."""
    boot_ns = make_ns(
        mode,
        lineage=f"bound-src-root-{mode.value}-{endpoint}",
        history_bounds=HistoryBounds(max_retained_source_bytes=ROOT_ANCHOR_BYTES),
    )
    boot = observe_causal_history((root_request(),), boot_ns, empty_state(boot_ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    boot_root = boot.state.root
    assert boot_root is not None
    assert boot_root.source_byte_length == ROOT_ANCHOR_BYTES
    root_over_ns = make_ns(
        mode,
        lineage=f"bound-src-rootover-{mode.value}-{endpoint}",
        history_bounds=HistoryBounds(max_retained_source_bytes=ROOT_ANCHOR_BYTES - 1),
    )
    root_empty = empty_state(root_over_ns)
    root_over = observe_causal_history((root_request(),), root_over_ns, root_empty, 0)
    assert root_over.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert root_over.diagnostics == (CausalHistoryLimitation.RETAINED_SOURCE_BYTES_OVER_BOUND,)
    assert root_over.state is root_empty
    for tag, cap in (("at", ROOT_ANCHOR_BYTES + 8), ("over", ROOT_ANCHOR_BYTES + 7)):
        ns = make_ns(
            mode,
            lineage=f"bound-src-{tag}-{mode.value}-{endpoint}",
            history_bounds=HistoryBounds(max_retained_source_bytes=cap),
        )
        s = observe_causal_history((root_request(),), ns, empty_state(ns), 0).state
        r1 = observe_causal_history((read_request(endpoint, "bs-1", "A.md"),), ns, s, 1)
        assert r1.outcome is CausalHistoryOutcome.ACCEPTED
        r2 = observe_causal_history((read_request(endpoint, "bs-2", "B.md"),), ns, r1.state, 2)
        if tag == "at":
            assert r2.outcome is CausalHistoryOutcome.ACCEPTED
            assert len(r2.state.occurrences) == 2
        else:
            assert r2.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
            assert r2.diagnostics == (CausalHistoryLimitation.RETAINED_SOURCE_BYTES_OVER_BOUND,)
            assert r2.state is r1.state


@pytest.mark.parametrize("mode", MODES)
def test_bound_max_argument_bytes_at_limit_and_one_over(mode: AdmissionMode) -> None:
    """max_argument_bytes bounds the ACTUAL argument fingerprint input
    bytes: the exact 19-byte trusted arguments are at cap 19; cap 18
    refuses with ARGUMENTS_OVER_BOUND before any canonical
    construction (EXACT prior state)."""
    assert len(ISSUE_ARGS) == 19
    at_ns = make_ns(
        mode,
        lineage=f"bound-argbytes-{mode.value}",
        history_bounds=HistoryBounds(max_argument_bytes=len(ISSUE_ARGS)),
    )
    s = observe_causal_history((root_request(),), at_ns, empty_state(at_ns), 0).state
    at = register_issuance(
        s, at_ns, "ba-1", "responses", "exec_command", ISSUE_ARGS, (CAUSAL_ROOT_FACT,), 1
    )
    assert at.outcome is CausalHistoryOutcome.ACCEPTED
    over_ns = make_ns(
        mode,
        lineage=f"bound-argbytes-over-{mode.value}",
        history_bounds=HistoryBounds(max_argument_bytes=len(ISSUE_ARGS) - 1),
    )
    s2 = observe_causal_history((root_request(),), over_ns, empty_state(over_ns), 0).state
    over = register_issuance(
        s2, over_ns, "ba-2", "responses", "exec_command", ISSUE_ARGS, (CAUSAL_ROOT_FACT,), 1
    )
    assert over.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert over.diagnostics == (CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,)
    assert over.state is s2


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_bound_max_total_argument_bytes_at_limit_and_one_over(
    mode: AdmissionMode, endpoint: str
) -> None:
    """max_total_argument_bytes is the CUMULATIVE input + canonical
    argument bytes inspected/constructed PER TRANSITION (shared
    ledger, never reset per call): each read charges its 19 input +
    18 canonical bytes in the inventory phase AND again in the proof
    binding phase (74 per read), so a two-read batch charges 148: at
    cap 148 both reads are retained; at cap 147 the batch refuses
    atomically as a RESOURCE refusal (REFUSED_OVER_BOUND /
    ARGUMENTS_OVER_BOUND -- a cumulative-budget crossing is never a
    content conflict) with nothing retained and the EXACT prior
    state."""
    batch = (
        root_request(),
        read_request(endpoint, "bt-1"),
        read_request(endpoint, "bt-2"),
    )
    at_ns = make_ns(
        mode,
        lineage=f"bound-totalarg-{mode.value}-{endpoint}",
        history_bounds=HistoryBounds(max_total_argument_bytes=148),
    )
    at = observe_causal_history(batch, at_ns, empty_state(at_ns), 0)
    assert at.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(at.state.occurrences) == 2
    over_ns = make_ns(
        mode,
        lineage=f"bound-totalarg-over-{mode.value}-{endpoint}",
        history_bounds=HistoryBounds(max_total_argument_bytes=147),
    )
    over_empty = empty_state(over_ns)
    over = observe_causal_history(batch, over_ns, over_empty, 0)
    assert over.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert over.diagnostics == (CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,)
    assert over.state is over_empty
    assert over.state.occurrences == ()


@pytest.mark.parametrize("mode", MODES)
def test_bound_max_argument_nodes_at_limit_and_one_over(mode: AdmissionMode) -> None:
    """max_argument_nodes counts every JSON value/container AND every
    object key as one unit: {'a': 1} is exactly 3 nodes (object, key,
    value) at cap 3; cap 2 refuses with ARGUMENTS_OVER_BOUND."""
    args3 = json.dumps({"a": 1})
    at_ns = make_ns(
        mode,
        lineage=f"bound-nodes-{mode.value}",
        history_bounds=HistoryBounds(max_argument_nodes=3),
    )
    s = observe_causal_history((root_request(),), at_ns, empty_state(at_ns), 0).state
    at = register_issuance(
        s, at_ns, "bn-1", "responses", "exec_command", args3, (CAUSAL_ROOT_FACT,), 1
    )
    assert at.outcome is CausalHistoryOutcome.ACCEPTED
    over_ns = make_ns(
        mode,
        lineage=f"bound-nodes-over-{mode.value}",
        history_bounds=HistoryBounds(max_argument_nodes=2),
    )
    s2 = observe_causal_history((root_request(),), over_ns, empty_state(over_ns), 0).state
    over = register_issuance(
        s2, over_ns, "bn-2", "responses", "exec_command", args3, (CAUSAL_ROOT_FACT,), 1
    )
    assert over.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert over.diagnostics == (CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,)
    assert over.state is s2


@pytest.mark.parametrize("mode", MODES)
def test_bound_max_argument_depth_at_limit_and_one_over(mode: AdmissionMode) -> None:
    """max_argument_depth bounds JSON nesting (scalar depth 0, each
    container level one): {'a': {'b': 1}} reaches depth 2 at cap 2;
    cap 1 refuses with ARGUMENTS_OVER_BOUND.  Bare non-object
    arguments are separately unsupported (never depth-refused)."""
    args2 = json.dumps({"a": {"b": 1}})
    at_ns = make_ns(
        mode,
        lineage=f"bound-depth-{mode.value}",
        history_bounds=HistoryBounds(max_argument_depth=2),
    )
    s = observe_causal_history((root_request(),), at_ns, empty_state(at_ns), 0).state
    at = register_issuance(
        s, at_ns, "bd-1", "responses", "exec_command", args2, (CAUSAL_ROOT_FACT,), 1
    )
    assert at.outcome is CausalHistoryOutcome.ACCEPTED
    over_ns = make_ns(
        mode,
        lineage=f"bound-depth-over-{mode.value}",
        history_bounds=HistoryBounds(max_argument_depth=1),
    )
    s2 = observe_causal_history((root_request(),), over_ns, empty_state(over_ns), 0).state
    over = register_issuance(
        s2, over_ns, "bd-2", "responses", "exec_command", args2, (CAUSAL_ROOT_FACT,), 1
    )
    assert over.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert over.diagnostics == (CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,)
    assert over.state is s2
    # The bare non-object control uses the DEPTH-ACCEPTED namespace
    # (cap 2): the top-level non-object is a CONTENT refusal,
    # independent of the depth bound (at cap 1 the depth crossing
    # would be refused first as a bound).
    bare = register_issuance(
        s, at_ns, "bd-3", "responses", "exec_command", "[[1]]", (CAUSAL_ROOT_FACT,), 1
    )
    assert bare.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert bare.diagnostics == (CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED,)


def _two_limitation_batch() -> GraphRequest:
    """One original batch emitting exactly TWO distinct observation
    limitations (a null-ID result: malformed wrapper + missing result
    ID) and acquiring nothing: the at-limit / one-over pair for the
    TOTAL final diagnostics cap."""
    args = json.dumps({"cmd": "cat A.md"})
    normal = (
        "Chunk ID: ok\n"
        "Wall time: 0.0000 seconds\n"
        "Process exited with code 0\n"
        "Original token count: 4\n"
        "Output:\nFine.\n"
    )
    payload = {
        "input": [
            {"type": "function_call", "call_id": "dl-1", "name": "exec_command", "arguments": args},
            {"type": "function_call_output", "call_id": "dl-1", "output": normal},
            {"type": "function_call_output", "call_id": None, "output": normal},
        ]
    }
    return GraphRequest(payload=payload, endpoint="responses", context=None)


@pytest.mark.parametrize("mode", MODES)
def test_bound_max_diagnostics_total_cap_normalization(mode: AdmissionMode) -> None:
    """max_diagnostics is the TOTAL across BOTH emitted closed lists:
    a batch with two distinct observation limitations at cap 2 keeps
    the original reasons (no state change); at cap 1 the crossing
    normalizes to the ONE fixed whole-empty DIAGNOSTICS_FULL refusal
    with NO copied limitations (no silent truncation)."""
    batch = _two_limitation_batch()
    at_ns = make_ns(
        mode,
        lineage=f"bound-diag-{mode.value}",
        history_bounds=HistoryBounds(max_diagnostics=2),
    )
    s = observe_causal_history((root_request(),), at_ns, empty_state(at_ns), 0).state
    at = observe_causal_history((batch,), at_ns, s, 1)
    assert at.outcome is CausalHistoryOutcome.REPLAYED
    assert at.observation_limitations == (
        Limitation.MALFORMED_WRAPPER,
        Limitation.MISSING_RESULT_ID,
    )
    assert at.diagnostics == ()
    assert at.state is s
    over_ns = make_ns(
        mode,
        lineage=f"bound-diag-over-{mode.value}",
        history_bounds=HistoryBounds(max_diagnostics=1),
    )
    s2 = observe_causal_history((root_request(),), over_ns, empty_state(over_ns), 0).state
    over = observe_causal_history((batch,), over_ns, s2, 1)
    assert over.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert over.diagnostics == (CausalHistoryLimitation.DIAGNOSTICS_FULL,)
    assert over.observation_limitations == ()
    assert over.state is s2


@pytest.mark.parametrize("mode", MODES)
def test_revision_overflow_refuses_before_mutation(mode: AdmissionMode) -> None:
    """Revision 0..2**63-1: a state AT MAX_REVISION refuses every
    state-changing transition with REVISION_OVERFLOW BEFORE any
    mutation (root bootstrap, trusted issuance), preserving the
    EXACT prior state."""
    ns = make_ns(mode, lineage=f"bound-revision-{mode.value}")
    full = CausalHistoryState(history_key=ns.history_key, revision=MAX_REVISION)
    boot = observe_causal_history((root_request(),), ns, full, MAX_REVISION)
    assert boot.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert boot.diagnostics == (CausalHistoryLimitation.REVISION_OVERFLOW,)
    assert boot.state is full
    issue = register_issuance(
        full, ns, "rv-1", "responses", "exec_command", ISSUE_ARGS, (CAUSAL_ROOT_FACT,), MAX_REVISION
    )
    assert issue.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
    assert issue.diagnostics == (CausalHistoryLimitation.REVISION_OVERFLOW,)
    assert issue.state is full


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_input_and_old_state_immutability(mode: AdmissionMode, endpoint: str) -> None:
    """Transitions are pure over immutable inputs: the ORIGINAL
    request payloads and the EXACT prior state objects are bit-for-bit
    unchanged after an ACCEPTED transition and after a REFUSED one
    (no in-place mutation of caller-owned data)."""
    ns = make_ns(mode, lineage=f"immut-{mode.value}-{endpoint}")
    root_req = root_request()
    read_req = read_request(endpoint, "im-1")
    state_before = empty_state(ns)
    boot_payload = copy.deepcopy(root_req.payload)
    read_payload = copy.deepcopy(read_req.payload)
    state_before_snapshot = copy.deepcopy(state_before)
    boot = observe_causal_history((root_req,), ns, state_before, 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    first = observe_causal_history((read_req,), ns, boot.state, 1)
    assert first.outcome is CausalHistoryOutcome.ACCEPTED
    # A same-ID changed-arguments refusal on top of the accepted state.
    changed = GraphRequest(
        payload={
            "input": [
                {
                    "type": "function_call",
                    "call_id": "im-1",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "printf synthetic"}),
                },
            ]
        },
        endpoint="responses",
        context=None,
    )
    refused = observe_causal_history((changed,), ns, first.state, 2)
    assert refused.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert refused.state is first.state
    assert root_req.payload == boot_payload
    assert read_req.payload == read_payload
    assert state_before == state_before_snapshot
    assert state_before is not first.state


@pytest.mark.parametrize("mode", MODES)
def test_no_host_io_after_setup_and_private_errors(
    monkeypatch: pytest.MonkeyPatch, mode: AdmissionMode
) -> None:
    """The original-API transition performs NO host IO after setup
    (no filesystem, socket or process facility), leaves the ORIGINAL
    payloads byte-unchanged, and operational repr/errors never echo
    source bytes, private call IDs or identity values."""
    rootcanary = "SYNTHETIC-ROOT-IO-CANARY"
    filecanary = "SYNTHETIC-FILE-IO-CANARY"
    idcanary = "SYNTHETIC-ID-IO-CANARY"
    principal_canary = "SYNTHETIC-PRINCIPAL-IO-CANARY"
    session_canary = "SYNTHETIC-SESSION-IO-CANARY"
    identity = RequestIdentity(
        principal=principal_canary,
        session=session_canary,
        repository="synthetic-io-repo",
        route="synthetic-io-route",
    )
    admission = make_bundle_admission_namespace(
        identity,
        model_identity="synthetic-io-model",
        config_fingerprint=FINGERPRINT,
        workspace=WORKSPACE,
        mode=mode,
    )
    ns = make_causal_history_namespace(admission, f"io-lineage-{mode.value}")
    root_req = root_request()
    root_req.payload["input"][0]["content"][0]["text"] = root_req.payload["input"][0]["content"][0][
        "text"
    ].replace("</INSTRUCTIONS>", f"{rootcanary}\n</INSTRUCTIONS>")
    read_req = read_request("responses", idcanary)
    read_req.payload["input"][1]["output"] = (
        read_req.payload["input"][1]["output"].split("Output:", 1)[0] + "Output:\n" + filecanary
    )
    root_payload = copy.deepcopy(root_req.payload)
    read_payload = copy.deepcopy(read_req.payload)
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

    boot = observe_causal_history((root_req,), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    first = observe_causal_history((read_req,), ns, boot.state, 1)
    assert first.outcome is CausalHistoryOutcome.ACCEPTED
    assert root_req.payload == root_payload
    assert read_req.payload == read_payload
    assert not attempts
    canaries = (rootcanary, filecanary, idcanary, principal_canary, session_canary)
    for text in (repr(boot), repr(first), repr(first.state), str(first.state)):
        for canary in canaries:
            assert canary not in text
    for occ in first.state.occurrences:
        for canary in canaries:
            assert canary not in repr(occ)
    for rec in first.state.results:
        for canary in canaries:
            assert canary not in repr(rec)
    # Trusted registration/receipt/query under the SAME guard: the
    # second read endpoint (chat), the positive AND negative trusted
    # issuance and receipt paths, and a relation query (both the
    # positive interpretation and the foreign-scope fixed error).
    # The chat read uses its OWN private ID: one call ID cannot span
    # both endpoint families (the immutable same-ID binding law).
    # A distinct fresh ID keeps the raw canary substring so the
    # privacy checks still exercise it.
    chatidcanary = f"{idcanary}-chat"
    chat_req = read_request("chat", chatidcanary)
    chat_payload = copy.deepcopy(chat_req.payload)
    chat = observe_causal_history((chat_req,), ns, first.state, first.state.revision)
    assert chat.outcome is CausalHistoryOutcome.ACCEPTED
    chat_occ = next(o for o in chat.state.occurrences if o.endpoint == "chat")
    issued = register_issuance(
        chat.state,
        ns,
        chatidcanary,
        "chat",
        "exec_command",
        json.dumps({"cmd": "cat A.md"}),
        (CAUSAL_ROOT_FACT,),
        chat.state.revision,
    )
    assert issued.outcome is CausalHistoryOutcome.ACCEPTED
    rebind = register_issuance(
        issued.state,
        ns,
        chatidcanary,
        "chat",
        "other_tool",
        json.dumps({"cmd": "cat A.md"}),
        (CAUSAL_ROOT_FACT,),
        issued.state.revision,
    )
    assert rebind.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert rebind.state is issued.state
    anchored = register_receipt(
        issued.state,
        ns,
        chatidcanary,
        "chat",
        "exec_command",
        json.dumps({"cmd": "cat A.md"}),
        (CAUSAL_ROOT_FACT,),
        issued.state.revision,
    )
    assert anchored.outcome is CausalHistoryOutcome.ACCEPTED
    unknown = register_receipt(
        anchored.state,
        ns,
        "never-seen-io",
        "chat",
        "exec_command",
        json.dumps({"cmd": "cat A.md"}),
        (CAUSAL_ROOT_FACT,),
        anchored.state.revision,
    )
    assert unknown.outcome is CausalHistoryOutcome.REFUSED_CONFLICT
    assert unknown.state is anchored.state
    assert (
        relation(anchored.state, ns, chat_occ.occurrence_id, chat_occ.occurrence_id)
        is CausalRelation.SAME
    )
    foreign_ns = make_causal_history_namespace(admission, f"io-foreign-{mode.value}")
    with pytest.raises(ValueError, match="own history scope"):
        relation(anchored.state, foreign_ns, chat_occ.occurrence_id, chat_occ.occurrence_id)
    assert chat_req.payload == chat_payload
    for text in (repr(chat), repr(issued), repr(anchored), repr(unknown)):
        for canary in canaries:
            assert canary not in text
        assert chatidcanary not in text
    assert not attempts
    # Errors are private too: a construction refusal never echoes the
    # canary identity values.
    with pytest.raises(ValueError) as excinfo:
        make_causal_history_namespace(
            admission,
            f"io-lineage-over-{mode.value}",
            bounds=HistoryBounds(max_work_units=2**62),
        )
    assert principal_canary not in str(excinfo.value)
    assert session_canary not in str(excinfo.value)


# --- Inherited limits at the NEW history composition (64 controls) ------
#
# Durable port of ROOT's 64 known-synthetic new-composition controls:
# the ACTUAL applicable inherited ceilings (graph request batch, the
# reused proof bundle/member/segment/marker and the exact cumulative
# marker-search windows, and BOTH path ceilings) enforced through the
# NEW ``observe_causal_history`` original API over the actual
# admission->history namespace factory, on BOTH read endpoints in BOTH
# namespace modes.  Graph-node closure is OUTSIDE this pure stage: it
# is omitted here, never relabeled as a history pass.  An over-bound
# crossing refuses atomically with the EXACT empty prior state and the
# exact fixed reason; a crossed path ceiling is a per-candidate
# nonacquisition (ACCEPTED, root retained, NO occurrences, at least
# one typed diagnostic/limitation), never a whole-empty failure.  No S
# runtime path dependency.


def _history_limit_requests(
    root: str, reads: tuple[tuple[str, str], ...], endpoint: str
) -> tuple[GraphRequest, GraphRequest]:
    """Root envelope request (Responses-only root authority) plus one
    read request carrying the given read calls on the given endpoint."""
    items: list[dict[str, Any]] = []
    messages: list[dict[str, Any]] = []
    for index, (cmd, body) in enumerate(reads):
        cid = f"synthetic-history-limit-{index}"
        call_args = json.dumps({"cmd": cmd})
        text = frame(body)
        if endpoint == "responses":
            items.extend(
                (
                    {
                        "type": "function_call",
                        "call_id": cid,
                        "name": "exec_command",
                        "arguments": call_args,
                    },
                    out_item(cid, text),
                )
            )
        else:
            messages.extend(
                (
                    {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": cid,
                                "type": "function",
                                "function": {
                                    "name": "exec_command",
                                    "arguments": call_args,
                                },
                            }
                        ],
                    },
                    {"role": "tool", "tool_call_id": cid, "content": text},
                )
            )
    if endpoint == "responses":
        read_payload: dict[str, Any] = {"input": items}
    else:
        read_payload = {"messages": messages}
    root_req = GraphRequest(
        payload={"input": [root_item(root)]}, endpoint="responses", context=None
    )
    return root_req, GraphRequest(payload=read_payload, endpoint=endpoint, context=None)


def _history_limit_check(
    label: str,
    mode: AdmissionMode,
    requests: tuple[GraphRequest, GraphRequest],
    ns: CausalHistoryNamespace,
    *,
    complete: bool,
    reason: CausalHistoryLimitation | None = None,
    nonacquisition: bool = False,
) -> None:
    """The exact probe pass criterion over ONE original batch through
    the NEW history transition, with the original payloads required to
    stay byte-identical."""
    original = [copy.deepcopy(r.payload) for r in requests]
    empty = CausalHistoryState(history_key=ns.history_key, revision=0)
    snap = observe_causal_history(requests, ns, empty, 0)
    values = [x.value for x in (*snap.diagnostics, *snap.observation_limitations)]
    if nonacquisition:
        ok = (
            snap.outcome is CausalHistoryOutcome.ACCEPTED
            and snap.state.root is not None
            and not snap.state.occurrences
            and bool(values)
        )
    elif complete:
        ok = (
            snap.outcome is CausalHistoryOutcome.ACCEPTED
            and snap.state.root is not None
            and bool(snap.state.occurrences)
        )
    else:
        ok = (
            snap.outcome is CausalHistoryOutcome.REFUSED_OVER_BOUND
            and reason is not None
            and reason.value in values
            and snap.state.root is None
            and not snap.state.occurrences
            and snap.state is empty
        )
    assert ok, (
        f"{label} ({mode.value}): outcome={snap.outcome.value} "
        f"reasons={values} occurrences={len(snap.state.occurrences)}"
    )
    assert [r.payload for r in requests] == original, f"{label}: original payload mutated"


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_history_inherited_limit_propagation_matrix(mode: AdmissionMode, endpoint: str) -> None:
    single = _history_limit_requests("A.md", (("cat A.md", "alpha"),), endpoint)
    for cap in (2, 1):
        _history_limit_check(
            f"graph_requests_{cap}",
            mode,
            single,
            make_ns(mode, graph_bounds=GraphBounds(max_requests=cap)),
            complete=(cap == 2),
            reason=CausalHistoryLimitation.BATCH_OVER_BOUND,
        )
    two = _history_limit_requests(
        "A.md B.md", (("cat A.md", "alpha"), ("cat B.md", "beta")), endpoint
    )
    for cap in (2, 1):
        _history_limit_check(
            f"proof_bundles_{cap}",
            mode,
            two,
            make_ns(mode, proof_bounds=BundleProofBounds(max_bundles=cap)),
            complete=(cap == 2),
            reason=CausalHistoryLimitation.BUNDLES_OVER_BOUND,
        )
    members = _history_limit_requests("A.md B.md", (("cat A.md B.md", "alphabeta"),), endpoint)
    for cap in (2, 1):
        _history_limit_check(
            f"proof_members_{cap}",
            mode,
            members,
            make_ns(mode, proof_bounds=BundleProofBounds(max_members=cap)),
            complete=(cap == 2),
            reason=CausalHistoryLimitation.MEMBERS_OVER_BOUND,
        )
    segments = _history_limit_requests(
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
        _history_limit_check(
            f"proof_segments_{cap}",
            mode,
            segments,
            make_ns(mode, proof_bounds=BundleProofBounds(max_segments=cap)),
            complete=(cap == 4),
            reason=CausalHistoryLimitation.SEGMENTS_OVER_BOUND,
        )
    marker = _history_limit_requests(
        "A.md B.md", (("cat A.md && echo 'MM' && cat B.md", "alphaMM\nbeta"),), endpoint
    )
    for cap in (3, 2):
        _history_limit_check(
            f"proof_marker_{cap}",
            mode,
            marker,
            make_ns(mode, proof_bounds=BundleProofBounds(max_marker=cap)),
            complete=(cap == 3),
            reason=CausalHistoryLimitation.MARKER_OVER_BOUND,
        )
    search = _history_limit_requests(
        "A.md B.md C.md D.md",
        (
            ("cat A.md && echo 'M' && cat B.md", "alphaM\nbeta"),
            ("cat C.md && echo 'N' && cat D.md", "gammaN\ndelta"),
        ),
        endpoint,
    )
    for cap in (23, 22):
        _history_limit_check(
            f"proof_marker_search_{cap}",
            mode,
            search,
            make_ns(mode, proof_bounds=BundleProofBounds(max_marker_search=cap)),
            complete=(cap == 23),
            reason=CausalHistoryLimitation.MARKER_SEARCH_OVER_BOUND,
        )
    long_name = "LONGNAME.md"
    path_len = len(long_name.encode("utf-8"))
    path_reqs = _history_limit_requests(long_name, ((f"cat {long_name}", "leaf"),), endpoint)
    for scope in ("graph", "observation"):
        for cap in (path_len, path_len - 1):
            if scope == "graph":
                ns = make_ns(mode, graph_bounds=GraphBounds(max_path_bytes=cap))
            else:
                ns = make_ns(
                    mode,
                    lineage=f"hist-limit-{mode.value}",
                    observation_bounds=ObservationBounds(max_path_bytes=cap),
                )
            _history_limit_check(
                f"{scope}_member_path_{cap}",
                mode,
                path_reqs,
                ns,
                complete=(cap == path_len),
                nonacquisition=(cap < path_len),
            )


# --- Native frontier and complete-empty source acceptance --------------


def _empty_terminal_frame() -> str:
    """A genuine already-exited native frame with an EMPTY output
    body (exact 017 complete evidence of a zero-byte source)."""
    return (
        "Chunk ID: a1b2c3\n"
        "Wall time: 0.0010 seconds\n"
        "Process exited with code 0\n"
        "Original token count: 0\n"
        "Output:\n"
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_native_initial_exec_frontier_ignores_later_poll_frontier(
    mode: AdmissionMode, endpoint: str
) -> None:
    """Native multi-piece read frontier law: the completed read
    occurrence is anchored by the INITIAL EXEC issuance frontier
    alone.  A later write_stdin poll issued under a SEPARATE
    completed occurrence (unrelated X under the same root) records
    its own frozen frontier, but it never makes the underlying read
    E newer than X: E vs X stays INCOMPARABLE from E's initial
    root-only frontier, with the complete source bytes and the
    actual anchored facts verified."""
    ns = make_ns(mode, lineage=f"native-frontier-{mode.value}-{endpoint}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    e_issue = register_issuance(
        boot.state,
        ns,
        "nf-exec",
        endpoint,
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        boot.state.revision,
    )
    assert e_issue.outcome is CausalHistoryOutcome.ACCEPTED
    e_pending = observe_causal_history(
        (chain_request(endpoint, "nf-exec", PENDING_BODY),),
        ns,
        e_issue.state,
        e_issue.state.revision,
    )
    assert e_pending.outcome is CausalHistoryOutcome.ACCEPTED
    assert not e_pending.state.occurrences
    assert len(e_pending.state.results) == 1
    assert e_pending.state.results[0].complete is False
    x_issue = register_issuance(
        e_pending.state,
        ns,
        "nf-frontier-x",
        endpoint,
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        e_pending.state.revision,
    )
    assert x_issue.outcome is CausalHistoryOutcome.ACCEPTED
    x_done = observe_causal_history(
        (read_request(endpoint, "nf-frontier-x"),),
        ns,
        x_issue.state,
        x_issue.state.revision,
    )
    assert x_done.outcome is CausalHistoryOutcome.ACCEPTED
    x_occ = x_done.state.occurrences[0]
    assert x_occ.anchored
    assert x_occ.proof.source_text == READ_BODY
    # The LATER poll issuance carries X's completed occurrence as its
    # frozen frontier -- distinct from E's root-only initial frontier.
    p_issue = register_issuance(
        x_done.state,
        ns,
        "nf-final-poll",
        endpoint,
        "write_stdin",
        poll_arguments(),
        (x_occ.occurrence_id,),
        x_done.state.revision,
    )
    assert p_issue.outcome is CausalHistoryOutcome.ACCEPTED
    assert p_issue.state.issuances[-1].parent_frontier == (x_occ.occurrence_id,)
    full = chain_request(
        endpoint,
        "nf-exec",
        PENDING_BODY,
        poll_cid="nf-final-poll",
        poll_text=terminal_frame(PENDING_TAIL),
    )
    done = observe_causal_history((full,), ns, p_issue.state, p_issue.state.revision)
    assert done.outcome is CausalHistoryOutcome.ACCEPTED
    assert done.state.revision == p_issue.state.revision + 1
    e_occ = next(o for o in done.state.occurrences if o.call_id == "nf-exec")
    assert e_occ.anchored
    assert e_occ.proof.source_text == PENDING_BODY + PENDING_TAIL
    assert e_occ.proof.pieces[1].call_id == "nf-final-poll"
    # E's initial frontier is root-only and X is a separate root child:
    # the poll's later frontier must NOT order E against X.
    assert (
        relation(done.state, ns, e_occ.occurrence_id, x_occ.occurrence_id)
        is CausalRelation.INCOMPARABLE
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_native_complete_empty_source_is_retained(mode: AdmissionMode, endpoint: str) -> None:
    """A genuine 017 COMPLETE read of a genuinely empty source is a
    successful singleton admission: the retained occurrence keeps the
    exact empty source text, zero source bytes and the exact empty
    sha256, with a complete result record (both endpoints/modes)."""
    ns = make_ns(mode, lineage=f"empty-source-{mode.value}-{endpoint}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    empty_frame = _empty_terminal_frame()
    if endpoint == "responses":
        payload: dict[str, Any] = {
            "input": [exec_call("empty-exec"), out_item("empty-exec", empty_frame)]
        }
    else:
        payload = {
            "messages": [
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "empty-exec",
                            "type": "function",
                            "function": {
                                "name": "exec_command",
                                "arguments": json.dumps({"cmd": "cat A.md"}),
                            },
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": "empty-exec", "content": empty_frame},
            ]
        }
    evidence = observe_request(
        payload, PathContext(workspace=WORKSPACE), ns.observation_bounds, endpoint
    )
    assert len(evidence.processes) == 1
    assert evidence.processes[0].outcome is ProcessOutcome.COMPLETE
    assert evidence.processes[0].bundle_digest == hashlib.sha256(b"").hexdigest()
    done = observe_causal_history(
        (GraphRequest(payload=payload, endpoint=endpoint, context=None),),
        ns,
        boot.state,
        boot.state.revision,
    )
    assert done.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(done.state.occurrences) == 1
    proof = done.state.occurrences[0].proof
    assert proof.source_text == ""
    assert proof.source_byte_length == 0
    assert proof.source_digest == hashlib.sha256(b"").hexdigest()
    assert done.state.results[0].complete is True


# --- Named original-API law controls (final durable coverage) ----------
#
# Compact durable counterparts of the order's named original-API
# evidence that the durable file did not previously hold as explicit
# repository cases (the ROOT basic-60 / pending / inherited probes
# pass at the same kernel; these are repository regressions, not
# closed-probe reruns): body-spoofed receipt flags cannot anchor (NO
# header API exists in this pure stage -- a JSON body field is never
# trusted authority), missing/malformed IDs stay typed non-acquiring
# under the accepted 017 limitation vocabulary, a SHIFTED completed
# replay (outer positions after history reduction) keeps exact state
# and FIRST provenance, the A-v1 -> trusted descendant A-v2 ->
# genuinely descendant new A-v1 chain with old-v1 replay and a
# fresh-looking unissued ID, initial mixed versions of a nonroot file
# plus sibling forks and a late older result (arrival never a clock),
# an unrelated B leaving the unchanged A proof byte-exact, and the
# original unsupported/truncated/nonzero frames staying unacquired
# through the NEW kernel with honest fixed limitations.


def _id_case_payloads(endpoint: str, call_id: Any, result_id: Any) -> GraphRequest:
    """One original read request with the given call/result ID
    values (missing/malformed identity cases)."""
    args = json.dumps({"cmd": "cat A.md"})
    if endpoint == "responses":
        payload = {
            "input": [
                {
                    "type": "function_call",
                    "call_id": call_id,
                    "name": "exec_command",
                    "arguments": args,
                },
                {"type": "function_call_output", "call_id": result_id, "output": frame(READ_BODY)},
            ]
        }
    else:
        payload = {
            "messages": [
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": call_id,
                            "type": "function",
                            "function": {"name": "exec_command", "arguments": args},
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": result_id, "content": frame(READ_BODY)},
            ]
        }
    return GraphRequest(payload=payload, endpoint=endpoint, context=None)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_body_receipt_spoof_cannot_anchor(mode: AdmissionMode, endpoint: str) -> None:
    """A caller BODY receipt/frontier/trust flag cannot anchor an
    otherwise valid unissued complete original read or bootstrap a
    rootless state.  The spoofed body field carries a FULLY
    VALID-LOOKING trusted binding (correct call ID/endpoint/name/
    arguments and the known root frontier) so that an erroneous
    implementation cannot pass by merely ignoring an invalid-looking
    receipt: body metadata alone must never anchor.  The matching
    legitimate INTERNAL ``register_receipt`` over the SAME complete
    baseline does anchor, proving the facts are real.  No header API
    exists in this pure stage (no HTTP header qualification is
    claimed from a JSON field test)."""
    ns = make_ns(mode, lineage=f"spoof-{mode.value}-{endpoint}")
    empty = empty_state(ns)
    plain = read_request(endpoint, "spoof-1")
    valid_receipt = {
        "call_id": "spoof-1",
        "endpoint": endpoint,
        "name": "exec_command",
        "arguments": ISSUE_ARGS,
        "frontier": [CAUSAL_ROOT_FACT],
        "trusted": True,
    }
    if endpoint == "responses":
        spoofed_payload = json.loads(json.dumps(plain.payload))
        spoofed_payload["input"].append({"type": "causal_receipt", **valid_receipt})
    else:
        spoofed_payload = json.loads(json.dumps(plain.payload))
        spoofed_payload["messages"][1]["trusted_receipt"] = valid_receipt
    spoofed = GraphRequest(payload=spoofed_payload, endpoint=endpoint, context=None)
    # Rootless + exact empty prior state: still the fixed NO_ROOT law.
    base = observe_causal_history((plain,), ns, empty, 0)
    assert base.outcome is CausalHistoryOutcome.REFUSED_NO_ROOT
    assert base.state is empty
    fake = observe_causal_history((spoofed,), ns, empty, 0)
    assert fake.outcome is CausalHistoryOutcome.REFUSED_NO_ROOT
    assert fake.state is empty
    assert fake.diagnostics == (CausalHistoryLimitation.NO_ROOT,)
    # Rooted: the read is admitted but UNANCHORED, with no issuance
    # minted from the body flag -- behaviorally inert versus the
    # unspoofed baseline.
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    rooted_base = observe_causal_history((plain,), ns, boot.state, boot.state.revision)
    assert rooted_base.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(rooted_base.state.occurrences) == 1
    assert rooted_base.state.occurrences[0].anchored is False
    assert rooted_base.state.issuances == ()
    rooted_fake = observe_causal_history((spoofed,), ns, boot.state, boot.state.revision)
    assert rooted_fake.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(rooted_fake.state.occurrences) == 1
    assert rooted_fake.state.occurrences[0].anchored is False
    assert rooted_fake.state.issuances == ()
    assert rooted_fake.state.revision == rooted_base.state.revision
    # The SAME facts delivered through the trusted INTERNAL API DO
    # anchor the unissued complete occurrence (positive control).
    legitimate = register_receipt(
        rooted_base.state,
        ns,
        "spoof-1",
        endpoint,
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        rooted_base.state.revision,
    )
    assert legitimate.outcome is CausalHistoryOutcome.ACCEPTED
    assert legitimate.state.occurrences[0].anchored is True
    assert legitimate.state.revision == rooted_base.state.revision + 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_missing_malformed_id_nonacquiring_typed(mode: AdmissionMode, endpoint: str) -> None:
    """Missing/malformed call/result identities at the NEW original
    composition stay typed and NON-ACQUIRING: the accepted 017
    limitation vocabulary is carried, no completed ID is ever
    invented, the EXACT prior state is preserved and the revision
    never advances (no duplicate observer)."""
    ns = make_ns(mode, lineage=f"ids-{mode.value}-{endpoint}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    cases = (
        ("missing_call_id", "", "", (Limitation.MISSING_CALL_ID, Limitation.MISSING_RESULT_ID)),
        ("null_call_id", None, None, (Limitation.MISSING_CALL_ID, Limitation.MISSING_RESULT_ID)),
        (
            "missing_result_id",
            "mm-rid",
            "",
            (Limitation.MISSING_CALL_RESULT, Limitation.MISSING_RESULT_ID),
        ),
        (
            "numeric_call_id",
            0,
            0,
            (Limitation.MALFORMED_CALL_ID, Limitation.MALFORMED_RESULT_ID),
        ),
        (
            "numeric_result_id",
            "mm-num",
            7,
            (Limitation.MALFORMED_RESULT_ID, Limitation.MISSING_CALL_RESULT),
        ),
    )
    for name, call_id, result_id, expected in cases:
        result = observe_causal_history(
            (_id_case_payloads(endpoint, call_id, result_id),), ns, boot.state, boot.state.revision
        )
        assert result.outcome is CausalHistoryOutcome.REPLAYED, name
        assert result.state is boot.state, name
        assert result.revision_before == boot.state.revision, name
        assert result.revision_after == boot.state.revision, name
        assert result.state.occurrences == (), name
        for limitation in expected:
            assert limitation in result.observation_limitations, name


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_shifted_completed_replay_noop(mode: AdmissionMode, endpoint: str) -> None:
    """A shifted completed replay (the identical read pair with an
    extra outer input/message item prepended, i.e. the positions
    moved after history reduction) is a pure REPLAYED no-op: EXACT
    state, no revision advance, FIRST provenance retained."""
    ns = make_ns(mode, lineage=f"shift-{mode.value}-{endpoint}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    first = observe_causal_history((read_request(endpoint, "sh-1"),), ns, boot.state, 1)
    assert first.outcome is CausalHistoryOutcome.ACCEPTED
    occ = first.state.occurrences[0]
    plain_payload = read_request(endpoint, "sh-1").payload
    if endpoint == "responses":
        shifted_payload = {
            "input": [
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "compaction shift"}],
                },
                *plain_payload["input"],
            ]
        }
    else:
        shifted_payload = {
            "messages": [
                {"role": "user", "content": "compaction shift"},
                *plain_payload["messages"],
            ]
        }
    shifted = GraphRequest(payload=shifted_payload, endpoint=endpoint, context=None)
    replay = observe_causal_history((shifted,), ns, first.state, first.state.revision)
    assert replay.outcome is CausalHistoryOutcome.REPLAYED
    assert CausalHistoryLimitation.REPLAY_POSITION_SHIFTED in replay.diagnostics
    assert replay.state is first.state
    assert replay.revision_before == first.state.revision
    assert replay.revision_after == first.state.revision
    assert len(replay.replayed_occurrences) == 1
    assert replay.replayed_occurrences[0].occurrence_id == occ.occurrence_id
    # FIRST provenance is retained: the result record and the proof
    # still point at the original request position.
    assert first.state.results[0].first_request_index == 0
    assert first.state.occurrences[0].proof.request_index == 0


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_version_descendant_chain_and_unissued_id(mode: AdmissionMode, endpoint: str) -> None:
    """Original A-v1 -> trusted descendant A-v2 -> genuinely
    descendant NEW A-v1: distinct occurrence identities with the
    exact source bytes, genuine partial-order relations from the
    frozen frontiers, an old A-v1 replay no-op, and a fresh-looking
    UNISSUED ID that stays unanchored and incomparable (no
    current-winner/invalidation/compiler claim at this stage)."""
    ns = make_ns(mode, lineage=f"versions-{mode.value}-{endpoint}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    v1 = observe_causal_history((read_request(endpoint, "vd-av1", V1_BODY),), ns, boot.state, 1)
    assert v1.outcome is CausalHistoryOutcome.ACCEPTED
    o1 = v1.state.occurrences[0]
    assert o1.proof.source_text == V1_BODY
    i2 = register_issuance(
        v1.state,
        ns,
        "vd-av2",
        endpoint,
        "exec_command",
        ISSUE_ARGS,
        (o1.occurrence_id, CAUSAL_ROOT_FACT),
        v1.state.revision,
    )
    assert i2.outcome is CausalHistoryOutcome.ACCEPTED
    v2 = observe_causal_history(
        (read_request(endpoint, "vd-av2", V2_BODY),), ns, i2.state, i2.state.revision
    )
    assert v2.outcome is CausalHistoryOutcome.ACCEPTED
    o2 = next(o for o in v2.state.occurrences if o.call_id == "vd-av2")
    assert o2.anchored
    assert o2.proof.source_text == V2_BODY
    assert relation(v2.state, ns, o1.occurrence_id, o2.occurrence_id) is CausalRelation.BEFORE
    i3 = register_issuance(
        v2.state,
        ns,
        "vd-av1new",
        endpoint,
        "exec_command",
        ISSUE_ARGS,
        (o2.occurrence_id, CAUSAL_ROOT_FACT),
        v2.state.revision,
    )
    assert i3.outcome is CausalHistoryOutcome.ACCEPTED
    new_v1 = observe_causal_history(
        (read_request(endpoint, "vd-av1new", V1_BODY),), ns, i3.state, i3.state.revision
    )
    assert new_v1.outcome is CausalHistoryOutcome.ACCEPTED
    o3 = next(o for o in new_v1.state.occurrences if o.call_id == "vd-av1new")
    assert o3.anchored
    assert o3.proof.source_text == V1_BODY
    assert o3.occurrence_id != o1.occurrence_id
    assert relation(new_v1.state, ns, o1.occurrence_id, o3.occurrence_id) is CausalRelation.BEFORE
    old_replay = observe_causal_history(
        (read_request(endpoint, "vd-av1", V1_BODY),), ns, new_v1.state, new_v1.state.revision
    )
    assert old_replay.outcome is CausalHistoryOutcome.REPLAYED
    assert old_replay.state is new_v1.state
    assert old_replay.revision_after == new_v1.state.revision
    fresh = observe_causal_history(
        (read_request(endpoint, "vd-fresh", V2_BODY),), ns, new_v1.state, new_v1.state.revision
    )
    assert fresh.outcome is CausalHistoryOutcome.ACCEPTED
    ox = next(o for o in fresh.state.occurrences if o.call_id == "vd-fresh")
    assert ox.anchored is False
    assert (
        relation(fresh.state, ns, o2.occurrence_id, ox.occurrence_id) is CausalRelation.INCOMPARABLE
    )
    assert (
        relation(fresh.state, ns, ox.occurrence_id, o2.occurrence_id) is CausalRelation.INCOMPARABLE
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_initial_mixed_versions_siblings_and_late_older_result(
    mode: AdmissionMode, endpoint: str
) -> None:
    """Initial mixed versions of a NONROOT file stay retained and
    incomparable (no call/arrival/list/digest clock); trusted
    sibling forks stay incomparable; and an older-registered
    outstanding result arriving AFTER a newer-frontier receipt never
    becomes AFTER merely from arrival."""
    ns = make_ns(mode, lineage=f"mixed-{mode.value}-{endpoint}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    mixed = observe_causal_history(
        (
            read_request(endpoint, "mv-1", V1_BODY),
            read_request(endpoint, "mv-2", V2_BODY),
        ),
        ns,
        boot.state,
        1,
    )
    assert mixed.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(mixed.state.occurrences) == 2
    o1 = next(o for o in mixed.state.occurrences if o.call_id == "mv-1")
    o2 = next(o for o in mixed.state.occurrences if o.call_id == "mv-2")
    assert o1.proof.source_text == V1_BODY
    assert o2.proof.source_text == V2_BODY
    assert (
        relation(mixed.state, ns, o1.occurrence_id, o2.occurrence_id) is CausalRelation.INCOMPARABLE
    )
    assert (
        relation(mixed.state, ns, o2.occurrence_id, o1.occurrence_id) is CausalRelation.INCOMPARABLE
    )
    # Sibling forks under the SAME root-only frontier; the
    # older-registered sibling is received LAST.
    forks = observe_causal_history(
        (
            read_request(endpoint, "sib-1", V1_BODY),
            read_request(endpoint, "sib-2", V2_BODY, cmd="cat B.md"),
        ),
        ns,
        mixed.state,
        mixed.state.revision,
    )
    assert forks.outcome is CausalHistoryOutcome.ACCEPTED
    fs1 = register_issuance(
        forks.state,
        ns,
        "sib-1",
        endpoint,
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        forks.state.revision,
    )
    fs2 = register_issuance(
        fs1.state,
        ns,
        "sib-2",
        endpoint,
        "exec_command",
        json.dumps({"cmd": "cat B.md"}),
        (CAUSAL_ROOT_FACT,),
        fs1.state.revision,
    )
    assert fs2.outcome is CausalHistoryOutcome.ACCEPTED
    newer_first = register_receipt(
        fs2.state,
        ns,
        "sib-2",
        endpoint,
        "exec_command",
        json.dumps({"cmd": "cat B.md"}),
        (CAUSAL_ROOT_FACT,),
        fs2.state.revision,
    )
    assert newer_first.outcome is CausalHistoryOutcome.ACCEPTED
    older_last = register_receipt(
        newer_first.state,
        ns,
        "sib-1",
        endpoint,
        "exec_command",
        ISSUE_ARGS,
        (CAUSAL_ROOT_FACT,),
        newer_first.state.revision,
    )
    assert older_last.outcome is CausalHistoryOutcome.ACCEPTED
    a1 = next(o for o in older_last.state.occurrences if o.call_id == "sib-1")
    a2 = next(o for o in older_last.state.occurrences if o.call_id == "sib-2")
    assert a1.anchored and a2.anchored
    assert (
        relation(older_last.state, ns, a1.occurrence_id, a2.occurrence_id)
        is CausalRelation.INCOMPARABLE
    )
    assert (
        relation(older_last.state, ns, a2.occurrence_id, a1.occurrence_id)
        is CausalRelation.INCOMPARABLE
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_late_older_original_result_not_after_newer(mode: AdmissionMode, endpoint: str) -> None:
    """A delayed ORIGINAL result from an OLDER frozen frontier never
    becomes AFTER a newer-frontier occurrence merely from arrival:
    OLD is issued under parent A; a newer intermediate L is issued
    and completed; NEW is issued under L; NEW's original result is
    observed FIRST and OLD's original result arrives LAST -- OLD vs
    NEW stays incomparable (no arrival/registration-revision clock).
    Exact original source preconditions on every read."""
    ns = make_ns(mode, lineage=f"late-older-{mode.value}-{endpoint}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    a = observe_causal_history((read_request(endpoint, "lo-a"),), ns, boot.state, 1)
    assert a.outcome is CausalHistoryOutcome.ACCEPTED
    o_a = a.state.occurrences[0]
    assert o_a.proof.source_text == READ_BODY
    issue_l = register_issuance(
        a.state,
        ns,
        "lo-l",
        endpoint,
        "exec_command",
        ISSUE_ARGS,
        (o_a.occurrence_id,),
        a.state.revision,
    )
    assert issue_l.outcome is CausalHistoryOutcome.ACCEPTED
    mid = observe_causal_history(
        (read_request(endpoint, "lo-l", "Intermediate body.\n"),),
        ns,
        issue_l.state,
        issue_l.state.revision,
    )
    assert mid.outcome is CausalHistoryOutcome.ACCEPTED
    o_l = mid.state.occurrences[-1]
    assert o_l.proof.source_text == "Intermediate body.\n"
    issue_old = register_issuance(
        mid.state,
        ns,
        "lo-old",
        endpoint,
        "exec_command",
        ISSUE_ARGS,
        (o_a.occurrence_id,),
        mid.state.revision,
    )
    assert issue_old.outcome is CausalHistoryOutcome.ACCEPTED
    issue_new = register_issuance(
        issue_old.state,
        ns,
        "lo-new",
        endpoint,
        "exec_command",
        ISSUE_ARGS,
        (o_l.occurrence_id,),
        issue_old.state.revision,
    )
    assert issue_new.outcome is CausalHistoryOutcome.ACCEPTED
    newer = observe_causal_history(
        (read_request(endpoint, "lo-new", "Newer body.\n"),),
        ns,
        issue_new.state,
        issue_new.state.revision,
    )
    assert newer.outcome is CausalHistoryOutcome.ACCEPTED
    o_newer = newer.state.occurrences[-1]
    assert o_newer.proof.source_text == "Newer body.\n"
    older = observe_causal_history(
        (read_request(endpoint, "lo-old", "Late old body.\n"),),
        ns,
        newer.state,
        newer.state.revision,
    )
    assert older.outcome is CausalHistoryOutcome.ACCEPTED
    o_older = older.state.occurrences[-1]
    assert o_older.proof.source_text == "Late old body.\n"
    assert (
        relation(older.state, ns, o_older.occurrence_id, o_newer.occurrence_id)
        is CausalRelation.INCOMPARABLE
    )
    assert (
        relation(older.state, ns, o_newer.occurrence_id, o_older.occurrence_id)
        is CausalRelation.INCOMPARABLE
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_unrelated_b_preserves_a_identity(mode: AdmissionMode, endpoint: str) -> None:
    """An unrelated B observation leaves the unchanged A retained
    proof byte-exact and its occurrence identity untouched: the
    frozen occurrence object, ID, source text/digest/length all
    survive B's independent retention, AND A's ACTUAL accepted
    018-c structural content key is unchanged when the real
    admission runs on the SAME original requests with and without B
    (the admission namespace is derived from the history
    namespace's ACTUAL fields with recomputed-key agreement
    checked; no d compiler key is minted, no reuse/counts claim)."""
    dual_root_text = "Read `A.md` and `B.md` before changing code."
    ns = make_ns(mode, lineage=f"stability-{mode.value}-{endpoint}")
    root_req = GraphRequest(
        payload={"input": [root_item(content=dual_root_text)]}, endpoint="responses", context=None
    )
    boot = observe_causal_history((root_req,), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    read_a = read_request(endpoint, "st-a", V1_BODY)
    read_b = read_request(endpoint, "st-b", V2_BODY, cmd="cat B.md")
    a = observe_causal_history((read_a,), ns, boot.state, 1)
    assert a.outcome is CausalHistoryOutcome.ACCEPTED
    a_occ = a.state.occurrences[0]
    b = observe_causal_history(
        (read_b,),
        ns,
        a.state,
        a.state.revision,
    )
    assert b.outcome is CausalHistoryOutcome.ACCEPTED
    assert len(b.state.occurrences) == 2
    a_again = next(o for o in b.state.occurrences if o.call_id == "st-a")
    assert a_again is a_occ
    assert a_again.occurrence_id == a_occ.occurrence_id
    assert a_again.proof.source_text == a_occ.proof.source_text == V1_BODY
    assert a_again.proof.source_digest == a_occ.proof.source_digest
    assert a_again.proof.source_byte_length == a_occ.proof.source_byte_length
    b_occ = next(o for o in b.state.occurrences if o.call_id == "st-b")
    assert b_occ.proof.source_text == V2_BODY
    # The ACTUAL accepted 018-c semantic key: the SAME actual
    # admission namespace (derived from the history namespace's
    # actual fields; recomputed keys must agree) over the SAME
    # original requests.  B's presence never changes A's content
    # key while A's retained proof stays exact.
    admission_ns = make_bundle_admission_namespace(
        RequestIdentity(
            principal=ns.principal,
            session=ns.session,
            repository=ns.repository,
            route=ns.route,
        ),
        model_identity=ns.model_identity,
        config_fingerprint=ns.config_fingerprint,
        workspace=ns.workspace,
        mode=ns.mode,
        graph_bounds=ns.graph_bounds,
        proof_bounds=ns.proof_bounds,
        observation_bounds=ns.observation_bounds,
    )
    assert admission_ns.namespace_key == ns.admission_namespace_key
    assert admission_ns.scoped_key == ns.admission_scoped_key
    snap_before = observe_bundle_admission_batch((root_req, read_a), admission_ns)
    assert snap_before.outcome is AdmissionOutcome.COMPLETE
    snap_after = observe_bundle_admission_batch((root_req, read_a, read_b), admission_ns)
    assert snap_after.outcome is AdmissionOutcome.COMPLETE
    a_before = next(e for e in snap_before.entries if e.key_record.member_occurrences == ("A.md",))
    a_after = next(e for e in snap_after.entries if e.key_record.member_occurrences == ("A.md",))
    assert a_before.content_key == a_after.content_key
    assert a_before.proof is not None and a_after.proof is not None
    assert a_before.proof.source_text == a_after.proof.source_text == V1_BODY
    assert a_before.proof.source_digest == a_after.proof.source_digest
    b_after = next(e for e in snap_after.entries if e.key_record.member_occurrences == ("B.md",))
    assert b_after.content_key != a_after.content_key
    assert b_after.proof is not None
    assert b_after.proof.source_text == V2_BODY


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_unsupported_nonzero_truncated_unacquired(mode: AdmissionMode, endpoint: str) -> None:
    """Original unsupported / truncated / nonzero process-read frames
    stay UNACQUIRED through the NEW kernel: honest fixed limitations
    (the accepted 017 closed vocabularies), no completed occurrence,
    no revision advance for the pure non-acquiring no-ops; the
    truncated frame retains only its non-acquiring result record."""
    ns = make_ns(mode, lineage=f"unacq-{mode.value}-{endpoint}")
    boot = observe_causal_history((root_request(),), ns, empty_state(ns), 0)
    assert boot.outcome is CausalHistoryOutcome.ACCEPTED
    chat_root_note = (Limitation.UNSUPPORTED_ENDPOINT,) if endpoint == "chat" else ()
    # (1) unsupported read syntax: typed non-acquiring no-op.
    unsupported = observe_causal_history(
        (read_request(endpoint, "ua-1", READ_BODY, cmd="sed -n 1p A.md"),),
        ns,
        boot.state,
        boot.state.revision,
    )
    assert unsupported.outcome is CausalHistoryOutcome.REPLAYED
    assert unsupported.diagnostics == (CausalHistoryLimitation.PLAN_UNSUPPORTED,)
    assert Limitation.FRAGMENT_COMMAND in unsupported.observation_limitations
    for limitation in chat_root_note:
        assert limitation in unsupported.observation_limitations
    assert unsupported.state is boot.state
    assert unsupported.state.occurrences == ()
    # (2) global nonzero exit: no per-read completion claim.
    nonzero_frame = (
        "Chunk ID: synthetic\n"
        "Wall time: 0.0000 seconds\n"
        "Process exited with code 1\n"
        f"Output:\n{READ_BODY}"
    )
    if endpoint == "responses":
        nz_req = GraphRequest(
            payload={"input": [exec_call("ua-2"), out_item("ua-2", nonzero_frame)]},
            endpoint="responses",
            context=None,
        )
    else:
        nz_req = GraphRequest(
            payload={
                "messages": [
                    {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "ua-2",
                                "type": "function",
                                "function": {
                                    "name": "exec_command",
                                    "arguments": json.dumps({"cmd": "cat A.md"}),
                                },
                            }
                        ],
                    },
                    {"role": "tool", "tool_call_id": "ua-2", "content": nonzero_frame},
                ]
            },
            endpoint="chat",
            context=None,
        )
    nonzero = observe_causal_history((nz_req,), ns, boot.state, boot.state.revision)
    assert nonzero.outcome is CausalHistoryOutcome.REPLAYED
    assert nonzero.diagnostics == (CausalHistoryLimitation.OUTPUT_INCONSISTENT,)
    assert Limitation.NONZERO_EXIT in nonzero.observation_limitations
    for limitation in chat_root_note:
        assert limitation in nonzero.observation_limitations
    assert nonzero.state is boot.state
    assert nonzero.state.occurrences == ()
    # (3) truncated final frame: never complete, non-acquiring result
    # record retained with the exact 017 wrapper+process limitations.
    warning = "Warning: truncated output (original token count: 512)\nTotal output lines: 64\n\n"
    truncated_frame = (
        "Chunk ID: 3d4e5f\n"
        "Wall time: 0.6789 seconds\n"
        "Process exited with code 0\n"
        "Original token count: 512\n"
        f"Output:\n{warning}head\ntail\n"
    )
    if endpoint == "responses":
        tr_req = GraphRequest(
            payload={"input": [exec_call("ua-3"), out_item("ua-3", truncated_frame)]},
            endpoint="responses",
            context=None,
        )
    else:
        tr_req = GraphRequest(
            payload={
                "messages": [
                    {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "ua-3",
                                "type": "function",
                                "function": {
                                    "name": "exec_command",
                                    "arguments": json.dumps({"cmd": "cat A.md"}),
                                },
                            }
                        ],
                    },
                    {"role": "tool", "tool_call_id": "ua-3", "content": truncated_frame},
                ]
            },
            endpoint="chat",
            context=None,
        )
    truncated = observe_causal_history((tr_req,), ns, boot.state, boot.state.revision)
    assert truncated.outcome is CausalHistoryOutcome.ACCEPTED
    assert truncated.state.occurrences == ()
    assert truncated.state.revision == boot.state.revision + 1
    assert len(truncated.state.results) == 1
    assert truncated.state.results[0].complete is False
    for limitation in (Limitation.MALFORMED_WRAPPER, Limitation.PROCESS_TRUNCATED, *chat_root_note):
        assert limitation in truncated.observation_limitations
