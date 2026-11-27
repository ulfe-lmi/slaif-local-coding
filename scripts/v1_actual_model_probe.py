"""Narrow opt-in v1 actual-model qualification probe (order 024-a).

Software-only preparation for the approved 024 actual-model and
genuine-client qualification:

- ONE closed loopback-only candidate on 127.0.0.1:18031 (the fixed
  development adapter port), bound to the exact development artifact
  (the pinned wheel SHA-256 installed in a fresh venv);
- ONE bounded synthetic session through the actual main request path
  and the separate tool-free compiler channel;
- fake peers only: the main upstream and the compiler channel are
  closed to the probe-owned fake peer (no other destination); the
  probe performs no live inference and starts no Codex or model
  client;
- serial, opt-in, finite request/response/time budgets, and exact
  allowed endpoint, model and run identity; unsupported or exhausted
  cases are closed typed refusals;
- probe-owned synthetic credentials: the three channel credentials
  are GENERATED inside each run (never caller-selected host
  environment references) and exist only in the candidate child's
  minimal environment;
- ownership proven before session traffic: a free-port precheck
  plus the /proc socket-inode join, scoped to the launched child's
  OWN fd directory, that the 18031 LISTEN owner is the exact
  launched candidate child (checked before any readiness HTTP);
- bounded content-free facts only (counts, statuses, booleans and
  digests retained under the private work root; never content, never
  credential values, never private paths).

The first later real invocation requires a separate exact order naming
the actual authorized upstream, the protected credential references,
each call budget and the observed model contract.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx

# -- Closed candidate topology (never caller-selected) -----------------

CANDIDATE_HOST = "127.0.0.1"
CANDIDATE_PORT = 18031
PEER_HOST = "127.0.0.1"
PEER_PORT = 18032
ALLOWED_MAIN_ENDPOINTS = ("/v1/responses", "/v1/chat/completions")
ALLOWED_OBSERVATION_ENDPOINTS = ("/healthz", "/readyz", "/v1/models")
DEFAULT_DECLARED_MODEL = "qwen38-27b"
# Fixed synthetic credential environment NAMES (closed constants;
# the probe generates each run's values internally and they exist
# only in the candidate child's minimal environment — never
# caller-selected host environment references, never emitted).
V1_PROBE_UPSTREAM_KEY_ENV = "SLAIF_V1_PROBE_UPSTREAM_KEY"
V1_PROBE_COMPILER_KEY_ENV = "SLAIF_V1_PROBE_COMPILER_KEY"
V1_PROBE_MARKER_KEY_ENV = "SLAIF_V1_PROBE_MARKER_KEY"
DEFAULT_MAX_MAIN_REQUESTS = 8
DEFAULT_MAX_RESPONSE_BYTES = 4 * 1024 * 1024
DEFAULT_REQUEST_TIMEOUT_SECONDS = 60.0
DEFAULT_TOTAL_BUDGET_SECONDS = 300.0
# The closed synthetic session's actual compiler work (the root
# bootstrap and the acquired file): the peer's compile-observation
# cap refuses any traffic beyond the selected session.
V1_SESSION_COMPILE_LIMIT = 2
# Closed finite maxima for the configurable probe budgets (the probe
# is bounded by construction; the selected case never approaches them).
MAX_MAIN_REQUESTS_CEILING = 64
MAX_RESPONSE_BYTES_CEILING = 16 * 1024 * 1024
REQUEST_TIMEOUT_SECONDS_CEILING = 300.0
TOTAL_BUDGET_SECONDS_CEILING = 900.0

# The pinned tokenizer/render capability revision (the 021 closed
# digest-pinned asset table).
PINNED_REVISION = "37561816e66b5b9153b1b64c10968c18c1e6f4a0"

# -- Closed refusal vocabulary (content-free) ---------------------------

REFUSAL_SPEC_INVALID = "v1-probe-spec-invalid"
REFUSAL_NON_LOOPBACK_UPSTREAM = "v1-probe-non-loopback-upstream"
REFUSAL_UNRESOLVABLE_CREDENTIAL = "v1-probe-credential-reference-unresolvable"
REFUSAL_ARTIFACT_MISMATCH = "v1-probe-artifact-identity-mismatch"
REFUSAL_RUN_IN_PROGRESS = "v1-probe-run-in-progress"
REFUSAL_UNSUPPORTED_ENDPOINT = "v1-probe-unsupported-endpoint"
REFUSAL_MODEL_CONTRACT = "v1-probe-model-contract-mismatch"
REFUSAL_BUDGET_EXHAUSTED = "v1-probe-budget-exhausted"
REFUSAL_ROUND_REFUSED = "v1-probe-round-refused"
REFUSAL_CANDIDATE_UNREACHABLE = "v1-probe-candidate-unreachable"
REFUSAL_PEER_PORT_BUSY = "v1-probe-peer-port-busy"
REFUSAL_CANDIDATE_FAILED = "v1-probe-candidate-failed"
REFUSAL_TOOLS = (
    REFUSAL_SPEC_INVALID,
    REFUSAL_NON_LOOPBACK_UPSTREAM,
    REFUSAL_UNRESOLVABLE_CREDENTIAL,
    REFUSAL_ARTIFACT_MISMATCH,
    REFUSAL_RUN_IN_PROGRESS,
    REFUSAL_UNSUPPORTED_ENDPOINT,
    REFUSAL_MODEL_CONTRACT,
    REFUSAL_BUDGET_EXHAUSTED,
    REFUSAL_ROUND_REFUSED,
    REFUSAL_CANDIDATE_UNREACHABLE,
    REFUSAL_PEER_PORT_BUSY,
    REFUSAL_CANDIDATE_FAILED,
)

_HEX32 = re.compile(r"^[0-9a-f]{32}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class V1ProbeRefusal(RuntimeError):
    """A closed typed probe refusal (content-free token plus detail)."""

    def __init__(self, token: str, detail: str) -> None:
        if token not in REFUSAL_TOOLS:
            raise AssertionError("unknown refusal token")
        super().__init__(f"{token}: {detail}")
        self.token = token
        self.detail = detail


# -- Closed candidate specification --------------------------------------


@dataclass(frozen=True)
class V1CandidateSpec:
    """The exact allowed endpoint/model/run identity and budgets.

    The candidate host/port are the closed module constants (the
    specification cannot select another destination); the upstream and
    compiler channels must be the probe-owned fake peer with an empty
    or ``/v1`` path.  The credential references are the fixed
    synthetic environment NAMES closed in this module (the
    generated per-run values never cross this module's surface).
    """

    declared_model: str
    run_id: str
    upstream_base_url: str
    compiler_base_url: str
    max_main_requests: int = DEFAULT_MAX_MAIN_REQUESTS
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES
    request_timeout_seconds: float = DEFAULT_REQUEST_TIMEOUT_SECONDS
    total_budget_seconds: float = DEFAULT_TOTAL_BUDGET_SECONDS
    artifact_wheel_path: Path | None = None
    artifact_wheel_sha256: str | None = None

    def validate(self) -> None:
        if self.declared_model != DEFAULT_DECLARED_MODEL:
            raise V1ProbeRefusal(
                REFUSAL_SPEC_INVALID, "declared model is outside the selected case"
            )
        if not _HEX32.match(self.run_id):
            raise V1ProbeRefusal(REFUSAL_SPEC_INVALID, "run id is not 32 lowercase hex")
        for label, url in (
            ("upstream", self.upstream_base_url),
            ("compiler", self.compiler_base_url),
        ):
            parsed = urlsplit(url)
            if parsed.scheme != "http" or parsed.hostname != PEER_HOST or parsed.port != PEER_PORT:
                raise V1ProbeRefusal(
                    REFUSAL_NON_LOOPBACK_UPSTREAM,
                    f"{label} channel must be the probe-owned fake peer",
                )
            if parsed.username is not None or parsed.password is not None:
                raise V1ProbeRefusal(REFUSAL_SPEC_INVALID, f"{label} URL carries credentials")
            if parsed.query or parsed.fragment:
                raise V1ProbeRefusal(
                    REFUSAL_SPEC_INVALID,
                    f"{label} URL carries a query or fragment",
                )
            if parsed.path not in ("", "/v1"):
                raise V1ProbeRefusal(REFUSAL_SPEC_INVALID, f"{label} path must be empty or /v1")
        if (
            not isinstance(self.max_main_requests, int)
            or isinstance(self.max_main_requests, bool)
            or not 1 <= self.max_main_requests <= MAX_MAIN_REQUESTS_CEILING
        ):
            raise V1ProbeRefusal(
                REFUSAL_SPEC_INVALID, "main request budget is outside the closed bound"
            )
        if (
            not isinstance(self.max_response_bytes, int)
            or isinstance(self.max_response_bytes, bool)
            or not 1 <= self.max_response_bytes <= MAX_RESPONSE_BYTES_CEILING
        ):
            raise V1ProbeRefusal(
                REFUSAL_SPEC_INVALID, "response byte budget is outside the closed bound"
            )
        if (
            not isinstance(self.request_timeout_seconds, float)
            or not math.isfinite(self.request_timeout_seconds)
            or not 0 < self.request_timeout_seconds <= REQUEST_TIMEOUT_SECONDS_CEILING
        ):
            raise V1ProbeRefusal(
                REFUSAL_SPEC_INVALID, "request timeout is outside the closed bound"
            )
        if (
            not isinstance(self.total_budget_seconds, float)
            or not math.isfinite(self.total_budget_seconds)
            or not 0 < self.total_budget_seconds <= TOTAL_BUDGET_SECONDS_CEILING
        ):
            raise V1ProbeRefusal(REFUSAL_SPEC_INVALID, "total budget is outside the closed bound")

    @staticmethod
    def check_endpoint(path: str) -> None:
        if path not in ALLOWED_MAIN_ENDPOINTS + ALLOWED_OBSERVATION_ENDPOINTS:
            raise V1ProbeRefusal(REFUSAL_UNSUPPORTED_ENDPOINT, "endpoint is not allowed")


def verify_artifact_identity(wheel_path: Path, expected_sha256: str) -> None:
    """The exact development artifact binding (digest over the bytes)."""
    if not _HEX64.match(expected_sha256):
        raise V1ProbeRefusal(REFUSAL_SPEC_INVALID, "expected sha256 is not 64 hex")
    if not wheel_path.is_file():
        raise V1ProbeRefusal(REFUSAL_ARTIFACT_MISMATCH, "wheel file is missing")
    digest = hashlib.sha256()
    with wheel_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != expected_sha256:
        raise V1ProbeRefusal(
            REFUSAL_ARTIFACT_MISMATCH, "wheel sha256 does not match the pinned identity"
        )


# -- Peer capture and bounded content-free facts -------------------------


class V1PeerCapture:
    """The probe peer's bounded observation of the actual forwarded
    traffic (the main bodies and the decoded compiler-demand user
    texts).  The caps are the selected main-request budget and the
    closed session compile count: extra traffic is the closed
    budget-exhausted refusal (the peer answers it with the typed
    provider fault).  The texts are consumed only for boolean
    containment checks inside the driver and are never retained or
    returned."""

    def __init__(
        self,
        max_main_bodies: int = DEFAULT_MAX_MAIN_REQUESTS,
        max_compile_texts: int = V1_SESSION_COMPILE_LIMIT,
    ) -> None:
        self._lock = threading.Lock()
        self._max_main_bodies = max_main_bodies
        self._max_compile_texts = max_compile_texts
        self._main_bodies: list[bytes] = []
        self._compile_user_texts: list[str] = []

    def add_main_body(self, body: bytes) -> None:
        with self._lock:
            if len(self._main_bodies) >= self._max_main_bodies:
                raise V1ProbeRefusal(REFUSAL_BUDGET_EXHAUSTED, "main observation budget exhausted")
            self._main_bodies.append(body)

    def add_compile_user_text(self, text: str) -> None:
        with self._lock:
            if len(self._compile_user_texts) >= self._max_compile_texts:
                raise V1ProbeRefusal(
                    REFUSAL_BUDGET_EXHAUSTED, "compiler observation budget exhausted"
                )
            self._compile_user_texts.append(text)

    @property
    def main_bodies(self) -> tuple[bytes, ...]:
        with self._lock:
            return tuple(self._main_bodies)

    @property
    def compile_user_texts(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(self._compile_user_texts)


@dataclass(frozen=True)
class V1ProbeFacts:
    """The bounded content-free session facts (024-a scope 2)."""

    run_id: str
    declared_model: str
    healthz_status: int
    readyz_status: int
    models_status: int
    model_contract_ok: bool
    rounds: tuple[tuple[str, int], ...]
    main_forward_count: int
    compiler_call_count: int
    r1_root_source_absent: bool
    r1_live_markers: int
    r1_evidence_markers: int
    r1_compiled_blocks: int
    r1_region_frame: bool
    r2_root_source_absent: bool
    r2_file_source_absent: bool
    r2_live_markers: int
    r2_evidence_markers: int
    r2_compiled_blocks: int
    r2_region_frame: bool
    r3_fixed_point: bool
    r3_new_compiler_calls: int
    r4_root_source_absent: bool
    r4_file_source_absent: bool
    r4_compiled_blocks: int
    r4_region_frame: bool
    r4_new_compiler_calls: int
    r5_first_event: str
    r5_completed: bool
    r5_root_source_absent: bool
    r5_compiled_blocks: int
    r5_region_frame: bool
    r6_cancelled: bool
    r6_forward_matches_r2: bool
    r7_fixed_point: bool
    r7_new_compiler_calls: int
    root_demand_carries_root_source: bool
    root_demand_candidate_count: int
    file_demand_carries_file_source: bool
    file_demand_foreign_candidate_count: int
    requests_used: int
    deadline_ok: bool
    response_bytes_ok: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "v1-probe-facts-v1",
            "run_id": self.run_id,
            "declared_model": self.declared_model,
            "healthz_status": self.healthz_status,
            "readyz_status": self.readyz_status,
            "models_status": self.models_status,
            "model_contract_ok": self.model_contract_ok,
            "rounds": [list(item) for item in self.rounds],
            "main_forward_count": self.main_forward_count,
            "compiler_call_count": self.compiler_call_count,
            "r1_root_source_absent": self.r1_root_source_absent,
            "r1_live_markers": self.r1_live_markers,
            "r1_evidence_markers": self.r1_evidence_markers,
            "r1_compiled_blocks": self.r1_compiled_blocks,
            "r1_region_frame": self.r1_region_frame,
            "r2_root_source_absent": self.r2_root_source_absent,
            "r2_file_source_absent": self.r2_file_source_absent,
            "r2_live_markers": self.r2_live_markers,
            "r2_evidence_markers": self.r2_evidence_markers,
            "r2_compiled_blocks": self.r2_compiled_blocks,
            "r2_region_frame": self.r2_region_frame,
            "r3_fixed_point": self.r3_fixed_point,
            "r3_new_compiler_calls": self.r3_new_compiler_calls,
            "r4_root_source_absent": self.r4_root_source_absent,
            "r4_file_source_absent": self.r4_file_source_absent,
            "r4_compiled_blocks": self.r4_compiled_blocks,
            "r4_region_frame": self.r4_region_frame,
            "r4_new_compiler_calls": self.r4_new_compiler_calls,
            "r5_first_event": self.r5_first_event,
            "r5_completed": self.r5_completed,
            "r5_root_source_absent": self.r5_root_source_absent,
            "r5_compiled_blocks": self.r5_compiled_blocks,
            "r5_region_frame": self.r5_region_frame,
            "r6_cancelled": self.r6_cancelled,
            "r6_forward_matches_r2": self.r6_forward_matches_r2,
            "r7_fixed_point": self.r7_fixed_point,
            "r7_new_compiler_calls": self.r7_new_compiler_calls,
            "root_demand_carries_root_source": self.root_demand_carries_root_source,
            "root_demand_candidate_count": self.root_demand_candidate_count,
            "file_demand_carries_file_source": self.file_demand_carries_file_source,
            "file_demand_foreign_candidate_count": self.file_demand_foreign_candidate_count,
            "requests_used": self.requests_used,
            "deadline_ok": self.deadline_ok,
            "response_bytes_ok": self.response_bytes_ok,
        }


# -- Synthetic session payload (the closed fixture bytes) ----------------

WORKSPACE = "/work"
ROOT_BODY = "Follow `docs/A.md` before acting.\n"
A_BODY = "Bounded synthetic dependency text.\n"
READ_CALL_ID = "c1"
READ_CMD = "cat docs/A.md"
FILE_CANDIDATE = "docs/A.md"


def _root_item() -> dict[str, Any]:
    return {
        "role": "user",
        "content": [
            {
                "type": "input_text",
                "text": (
                    f"# AGENTS.md instructions for {WORKSPACE}\n\n"
                    f"<INSTRUCTIONS>\n{ROOT_BODY}\n</INSTRUCTIONS>\n"
                ),
            }
        ],
    }


def _a_frame() -> str:
    return (
        "Chunk ID: synthetic\n"
        "Wall time: 0.0000 seconds\n"
        "Process exited with code 0\n"
        f"Output:\n{A_BODY}"
    )


def _exec_call() -> dict[str, Any]:
    return {
        "type": "function_call",
        "call_id": READ_CALL_ID,
        "name": "exec_command",
        "arguments": json.dumps({"cmd": READ_CMD}),
    }


def _out_item() -> dict[str, Any]:
    return {"type": "function_call_output", "call_id": READ_CALL_ID, "output": _a_frame()}


def session_payloads() -> dict[str, Any]:
    """The closed synthetic session (one root plus one acquired file)."""
    return {
        "r1_bootstrap": {
            "model": DEFAULT_DECLARED_MODEL,
            "input": [_root_item()],
        },
        "r2_acquire": {
            "model": DEFAULT_DECLARED_MODEL,
            "input": [_root_item(), _exec_call(), _out_item()],
        },
        "r4_source_absent": {
            "model": DEFAULT_DECLARED_MODEL,
            "input": [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Continue the session."}],
                }
            ],
        },
    }


# -- The session driver ----------------------------------------------------


async def _request_bounded(
    client: httpx.AsyncClient,
    spec: V1CandidateSpec,
    method: str,
    path: str,
    payload: bytes | None,
    *,
    stream: bool,
    cancel_after_first_event: bool,
    deadline: float,
    requests_used: list[int],
) -> tuple[int, bytes, list[str], bool]:
    """One bounded request: the response bytes are read under the cap
    in the stream's NATIVE chunks (no fixed-size re-chunking, so a
    short stream is never held back until EOF by the iterator), SSE
    data lines are collected content-free (event types only), and the
    optional cancel closes the stream as soon as the first event is
    observed (before the stream completes).  Returns (status, body,
    event types, cancelled)."""
    if time.monotonic() > deadline:
        raise V1ProbeRefusal(REFUSAL_BUDGET_EXHAUSTED, "total time budget exhausted")

    def remaining() -> float:
        return deadline - time.monotonic()

    if path in ALLOWED_MAIN_ENDPOINTS:
        requests_used[0] += 1
        if requests_used[0] > spec.max_main_requests:
            raise V1ProbeRefusal(REFUSAL_BUDGET_EXHAUSTED, "main request budget exhausted")
    spec.check_endpoint(path)
    headers = {"content-type": "application/json"} if payload is not None else {}
    try:
        response = await asyncio.wait_for(
            client.send(
                client.build_request(method, path, content=payload, headers=headers),
                stream=True,
            ),
            timeout=remaining(),
        )
    except TimeoutError:
        raise V1ProbeRefusal(REFUSAL_BUDGET_EXHAUSTED, "request deadline exceeded") from None
    chunks: list[bytes] = []
    total = 0
    events: list[str] = []
    buffer = b""
    parsed_offset = 0
    cancelled = False
    # Native chunks: each yield is one chunk of the underlying stream
    # (httpx ByteChunker(None) passes them through uncombined), so the
    # first-event cancel is observed at event granularity, not at the
    # iterator's own size.
    stream_iter = response.aiter_bytes()
    try:
        while True:
            try:
                chunk = await asyncio.wait_for(stream_iter.__anext__(), timeout=remaining())
            except StopAsyncIteration:
                break
            except TimeoutError:
                raise V1ProbeRefusal(REFUSAL_BUDGET_EXHAUSTED, "stream deadline exceeded") from None
            total += len(chunk)
            if total > spec.max_response_bytes:
                raise V1ProbeRefusal(REFUSAL_BUDGET_EXHAUSTED, "response byte budget exhausted")
            chunks.append(chunk)
            if stream:
                buffer += chunk
                while True:
                    newline = buffer.find(b"\n", parsed_offset)
                    if newline == -1:
                        break
                    line = buffer[parsed_offset:newline]
                    parsed_offset = newline + 1
                    if line.startswith(b"data: ") and line != b"data: [DONE]":
                        try:
                            event_type = json.loads(line[6:].decode("utf-8"))["type"]
                        except (ValueError, KeyError, UnicodeDecodeError):
                            event_type = "untyped"
                        events.append(str(event_type))
                        if cancel_after_first_event:
                            cancelled = True
                            break
                if cancelled:
                    break
            if time.monotonic() > deadline:
                raise V1ProbeRefusal(REFUSAL_BUDGET_EXHAUSTED, "total time budget exhausted")
    finally:
        await response.aclose()
    return response.status_code, b"".join(chunks), events, cancelled


def _normalized(body: bytes) -> str:
    """The decoded JSON canonical form with the streaming flag removed
    (the streamed rounds differ only by that field)."""
    data: Any = json.loads(body.decode("utf-8"))
    if isinstance(data, dict):
        data.pop("stream", None)
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


async def run_v1_probe_session(
    *,
    client: httpx.AsyncClient,
    spec: V1CandidateSpec,
    capture: V1PeerCapture,
) -> V1ProbeFacts:
    """The ONE bounded synthetic session through the actual main
    request path and the separate tool-free compiler channel."""
    spec.validate()
    deadline = time.monotonic() + spec.total_budget_seconds
    requests_used = [0]
    rounds: list[tuple[str, int]] = []

    def main_body(index: int) -> bytes:
        bodies = capture.main_bodies
        if index >= len(bodies):
            raise V1ProbeRefusal(REFUSAL_CANDIDATE_FAILED, "peer captured no forward")
        return bodies[index]

    async def observation(path: str) -> tuple[int, bytes]:
        status, body, _, _ = await _request_bounded(
            client,
            spec,
            "GET",
            path,
            None,
            stream=False,
            cancel_after_first_event=False,
            deadline=deadline,
            requests_used=requests_used,
        )
        return status, body

    async def post_round(
        name: str, payload: bytes | dict[str, Any], *, stream: bool = False
    ) -> tuple[int, bytes, list[str]]:
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        status, raw, events, _ = await _request_bounded(
            client,
            spec,
            "POST",
            "/v1/responses",
            body,
            stream=stream,
            cancel_after_first_event=False,
            deadline=deadline,
            requests_used=requests_used,
        )
        rounds.append((name, status))
        return status, raw, events

    # Observation pass (the exact allowed model/run identity check).
    healthz_status, _ = await observation("/healthz")
    models_status, models_body = await observation("/v1/models")
    readyz_status, _ = await observation("/readyz")
    if healthz_status != 200 or readyz_status != 200:
        raise V1ProbeRefusal(REFUSAL_CANDIDATE_UNREACHABLE, "candidate is not ready")
    model_contract_ok = False
    if models_status == 200:
        try:
            listing = json.loads(models_body.decode("utf-8")).get("data", [])
            model_contract_ok = any(item.get("id") == spec.declared_model for item in listing)
        except (ValueError, AttributeError):
            model_contract_ok = False
    if not model_contract_ok:
        raise V1ProbeRefusal(
            REFUSAL_MODEL_CONTRACT,
            "the /v1/models listing does not contain the declared model",
        )

    payloads = session_payloads()

    # Round one: the root-only bootstrap (the peer's direct response
    # issues the read -- the trusted issuance channel).
    status, _, _ = await post_round("r1-bootstrap", payloads["r1_bootstrap"])
    if status != 200:
        raise V1ProbeRefusal(REFUSAL_ROUND_REFUSED, f"r1-bootstrap status {status}")

    # Round two: the issued read completes; the file entry is
    # admitted, compiled and replaced.
    status, _, _ = await post_round("r2-acquire", payloads["r2_acquire"])
    if status != 200:
        raise V1ProbeRefusal(REFUSAL_ROUND_REFUSED, f"r2-acquire status {status}")
    # Per-round compiler snapshots: each delta below is measured
    # IMMEDIATELY after its own round (never sampled from the final
    # count), so a late or early compile is attributed to the round
    # that earned it.
    after_r2 = len(capture.compile_user_texts)

    # Round three: the resend of the OWN transformed body is the
    # byte-identical fixed point (RAM reuse, zero recompile).
    r2_body = main_body(1)
    status, _, _ = await post_round("r3-replay", r2_body)
    if status != 200:
        raise V1ProbeRefusal(REFUSAL_ROUND_REFUSED, f"r3-replay status {status}")
    after_r3 = len(capture.compile_user_texts)

    # Round four: the source-absent request; the required compiled
    # working set is reconstructed from RAM.
    status, _, _ = await post_round("r4-source-absent", payloads["r4_source_absent"])
    if status != 200:
        raise V1ProbeRefusal(REFUSAL_ROUND_REFUSED, f"r4-source-absent status {status}")
    after_r4 = len(capture.compile_user_texts)

    # Round five: the streamed bootstrap (ordinary SSE preservation).
    stream_payload = dict(payloads["r1_bootstrap"])
    stream_payload["stream"] = True
    status, _, r5_events = await post_round("r5-stream", stream_payload, stream=True)
    if status != 200:
        raise V1ProbeRefusal(REFUSAL_ROUND_REFUSED, f"r5-stream status {status}")

    # Round six: a stream cancelled after the first event.
    cancel_payload = dict(payloads["r2_acquire"])
    cancel_payload["stream"] = True
    status, _, _, r6_cancelled = await _request_bounded(
        client,
        spec,
        "POST",
        "/v1/responses",
        json.dumps(cancel_payload).encode(),
        stream=True,
        cancel_after_first_event=True,
        deadline=deadline,
        requests_used=requests_used,
    )
    rounds.append(("r6-stream-cancel", status))
    if status != 200 or not r6_cancelled:
        raise V1ProbeRefusal(REFUSAL_ROUND_REFUSED, f"r6-stream-cancel status {status}")
    after_r6 = len(capture.compile_user_texts)

    # Round seven: after the cancel the session still replays to the
    # byte-identical fixed point.
    status, _, _ = await post_round("r7-post-cancel", r2_body)
    if status != 200:
        raise V1ProbeRefusal(REFUSAL_ROUND_REFUSED, f"r7-post-cancel status {status}")
    after_r7 = len(capture.compile_user_texts)

    # The bounded content-free facts (boolean containment only; the
    # decoded texts are never retained).
    r1 = main_body(0)
    r2 = main_body(1)
    r3 = main_body(2)
    r4 = main_body(3)
    r5 = main_body(4)
    r6 = main_body(5)
    r7 = main_body(6)

    def decoded_texts(body: bytes) -> tuple[str, ...]:
        try:
            data: Any = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return ()
        texts: list[str] = []

        def walk(value: Any) -> None:
            if isinstance(value, str):
                texts.append(value)
            elif isinstance(value, list):
                for item in value:
                    walk(item)
            elif isinstance(value, dict):
                for item in value.values():
                    walk(item)

        walk(data)
        return tuple(texts)

    def absent(body: bytes, source: str) -> bool:
        return all(source not in text for text in decoded_texts(body))

    def frame_present(body: bytes) -> bool:
        return b"[slaif-compiled-context:v1:" in body

    compile_texts = capture.compile_user_texts
    root_demand = compile_texts[0] if len(compile_texts) > 0 else ""
    file_demand = compile_texts[1] if len(compile_texts) > 1 else ""

    facts = V1ProbeFacts(
        run_id=spec.run_id,
        declared_model=spec.declared_model,
        healthz_status=healthz_status,
        readyz_status=readyz_status,
        models_status=models_status,
        model_contract_ok=model_contract_ok,
        rounds=tuple(rounds),
        main_forward_count=len(capture.main_bodies),
        compiler_call_count=len(compile_texts),
        r1_root_source_absent=absent(r1, ROOT_BODY),
        r1_live_markers=r1.count(b"[slaif-live:v"),
        r1_evidence_markers=r1.count(b"[slaif-evidence:v"),
        r1_compiled_blocks=r1.count(b"<slaif-compiled-block"),
        r1_region_frame=frame_present(r1),
        r2_root_source_absent=absent(r2, ROOT_BODY),
        r2_file_source_absent=absent(r2, A_BODY),
        r2_live_markers=r2.count(b"[slaif-live:v"),
        r2_evidence_markers=r2.count(b"[slaif-evidence:v"),
        r2_compiled_blocks=r2.count(b"<slaif-compiled-block"),
        r2_region_frame=frame_present(r2),
        r3_fixed_point=r3 == r2,
        r3_new_compiler_calls=after_r3 - after_r2,
        r4_root_source_absent=absent(r4, ROOT_BODY),
        r4_file_source_absent=absent(r4, A_BODY),
        r4_compiled_blocks=r4.count(b"<slaif-compiled-block"),
        r4_region_frame=frame_present(r4),
        r4_new_compiler_calls=after_r4 - after_r3,
        r5_first_event=r5_events[0] if r5_events else "",
        r5_completed="response.completed" in r5_events,
        r5_root_source_absent=absent(r5, ROOT_BODY),
        r5_compiled_blocks=r5.count(b"<slaif-compiled-block"),
        r5_region_frame=frame_present(r5),
        r6_cancelled=r6_cancelled,
        r6_forward_matches_r2=_normalized(r6) == _normalized(r2),
        r7_fixed_point=r7 == r2,
        r7_new_compiler_calls=after_r7 - after_r6,
        root_demand_carries_root_source=ROOT_BODY in root_demand,
        root_demand_candidate_count=root_demand.count(f'"{FILE_CANDIDATE}"'),
        file_demand_carries_file_source=A_BODY in file_demand,
        file_demand_foreign_candidate_count=file_demand.count(f'"{FILE_CANDIDATE}"'),
        requests_used=requests_used[0],
        deadline_ok=time.monotonic() <= deadline,
        response_bytes_ok=True,
    )
    # The closed required-evidence gate: a 200-status session is NOT
    # success unless the actual compiled dependency evidence was
    # earned (content-free check over the facts above).
    if not (
        facts.r1_root_source_absent
        and facts.r1_compiled_blocks >= 1
        and facts.r2_root_source_absent
        and facts.r2_file_source_absent
        and facts.r2_live_markers >= 2
        and facts.r2_compiled_blocks >= 2
        and facts.root_demand_carries_root_source
        and facts.file_demand_carries_file_source
        and facts.r3_fixed_point
        and facts.r3_new_compiler_calls == 0
        and facts.r4_root_source_absent
        and facts.r4_file_source_absent
        and facts.r4_compiled_blocks >= 2
        and facts.r4_new_compiler_calls == 0
        and facts.r7_fixed_point
        and facts.r7_new_compiler_calls == 0
    ):
        raise V1ProbeRefusal(
            REFUSAL_CANDIDATE_FAILED,
            "the required compiled dependency evidence was not earned",
        )
    return facts


# -- The probe-owned fake peer (the only destination of both channels) --

# The peer's bounded request-body read (the synthetic session bodies
# are far smaller; this is a transport safety bound, not a case bound).
MAX_PEER_BODY_BYTES = 8 * 1024 * 1024
CANDIDATE_READY_TIMEOUT_SECONDS = 60.0
_FAKE_ERROR = json.dumps(
    {"error": {"message": "synthetic peer fault", "type": "probe_synthetic_fault"}}
).encode("utf-8")


def _resp_issue_bytes() -> bytes:
    """The first main response issues the session's single read (the
    trusted issuance channel; the exact accepted fixture shape)."""
    return json.dumps(
        {
            "id": f"resp-{READ_CALL_ID}",
            "status": "completed",
            "output": (
                {
                    "type": "function_call",
                    "id": f"fc-{READ_CALL_ID}",
                    "call_id": READ_CALL_ID,
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": READ_CMD}),
                },
            ),
        }
    ).encode("utf-8")


def _resp_plain_bytes(index: int) -> bytes:
    """A later main response (the closed plain message shape)."""
    return json.dumps(
        {
            "id": f"resp-r{index}",
            "status": "completed",
            "output": (
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "ok"}],
                },
            ),
        }
    ).encode("utf-8")


def _sse_bytes(body: bytes) -> bytes:
    """The ordinary SSE framing of one completed response (the
    accepted pass-through shape: created, completed, DONE)."""
    data: Any = json.loads(body.decode("utf-8"))
    created = {
        "type": "response.created",
        "response": {"id": data.get("id", "resp-sse"), "status": "in_progress"},
    }
    completed = {"type": "response.completed", "response": data}
    return (
        f"data: {json.dumps(created)}\n\ndata: {json.dumps(completed)}\n\ndata: [DONE]\n\n"
    ).encode()


def _compiler_completion_bytes(user: str, model: str) -> bytes:
    """The accepted echo compiler, reused from the existing fake
    application helpers (the actual validation of the demand's
    identity and candidate set still runs in the product code)."""
    root = str(Path(__file__).resolve().parent.parent)
    if root not in sys.path:
        sys.path.insert(0, root)
    from slaif_local_coding.constitution.bundles.bundle_compiler import (
        serialize_compiled_index,
    )
    from tests.test_v1_application import _completion_bytes, _index_for_demand

    index = _index_for_demand(user, model)
    return _completion_bytes(serialize_compiled_index(index).decode("utf-8"))


class _PeerServer(ThreadingHTTPServer):
    """The closed peer server (the daemon threads make the bounded
    cancel clean; the custom fields carry the run context)."""

    daemon_threads = True
    declared_model: str
    peer: V1FakePeer

    def handle_error(self, request: Any, client_address: Any) -> None:
        # A cancelled client stream (the round-six cancel) is an
        # expected outcome; the peer logs nothing.
        pass


class _PeerHandler(BaseHTTPRequestHandler):
    server: _PeerServer

    def log_message(self, *args: Any) -> None:
        # No raw content logging (method/path only would be
        # content-free, but the probe keeps the peer silent).
        pass

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path in ("/v1/health", "/health"):
            # The candidate's own /readyz probes the upstream health
            # endpoint; the owned peer answers it content-free.
            self._send(200, b'{"status": "ok"}', "application/json")
            return
        if path in ("/v1/models", "/models"):
            body = json.dumps(
                {
                    "object": "list",
                    "data": [{"id": self.server.declared_model, "object": "model"}],
                }
            ).encode("utf-8")
            self._send(200, body, "application/json")
        else:
            self._send(404, _FAKE_ERROR, "application/json")

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        try:
            length = int(self.headers.get("content-length") or 0)
        except ValueError:
            length = 0
        if length < 0 or length > MAX_PEER_BODY_BYTES:
            self._send(413, _FAKE_ERROR, "application/json")
            return
        raw = self.rfile.read(length) if length else b""
        peer = self.server.peer
        if path in ("/v1/responses", "/responses"):
            try:
                peer.capture.add_main_body(raw)
            except V1ProbeRefusal:
                # Extra traffic past the selected budget: the typed
                # provider fault (the candidate's own failure law
                # applies).
                self._send(500, _FAKE_ERROR, "application/json")
                return
            status, body, content_type = peer.handle_main(raw)
        elif path in ("/v1/chat/completions", "/chat/completions"):
            status, body, content_type = peer.handle_compiler(raw)
        else:
            self._send(404, _FAKE_ERROR, "application/json")
            return
        self._send(status, body, content_type)


class V1FakePeer:
    """The probe-owned loopback peer on the closed 18032 port: the
    fake main upstream and the fake tool-free compiler in ONE closed
    server.  It is the only destination the candidate configuration
    can name (the spec validation enforces it)."""

    def __init__(self, spec: V1CandidateSpec) -> None:
        self.spec = spec
        self.capture = V1PeerCapture(max_main_bodies=spec.max_main_requests)
        self._lock = threading.Lock()
        self._main_count = 0
        try:
            server = _PeerServer((PEER_HOST, PEER_PORT), _PeerHandler)
        except OSError:
            raise V1ProbeRefusal(REFUSAL_PEER_PORT_BUSY, "the probe peer port is busy") from None
        server.declared_model = spec.declared_model
        server.peer = self
        self._server = server
        self._thread = threading.Thread(target=server.serve_forever, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def shutdown(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=10)

    def handle_main(self, raw: bytes) -> tuple[int, bytes, str]:
        with self._lock:
            self._main_count += 1
            count = self._main_count
            first = count == 1
        try:
            payload: Any = json.loads(raw.decode("utf-8"))
            streaming = isinstance(payload, dict) and bool(payload.get("stream"))
        except (ValueError, UnicodeDecodeError):
            return 400, _FAKE_ERROR, "application/json"
        body = _resp_issue_bytes() if first else _resp_plain_bytes(count)
        if streaming:
            return 200, _sse_bytes(body), "text/event-stream"
        return 200, body, "application/json"

    def handle_compiler(self, raw: bytes) -> tuple[int, bytes, str]:
        try:
            body: Any = json.loads(raw.decode("utf-8"))
            user = str(body["messages"][1]["content"])
            model = str(body["model"])
        except (ValueError, KeyError, IndexError, TypeError, UnicodeDecodeError):
            return 400, _FAKE_ERROR, "application/json"
        try:
            self.capture.add_compile_user_text(user)
        except V1ProbeRefusal:
            return 500, _FAKE_ERROR, "application/json"
        try:
            return 200, _compiler_completion_bytes(user, model), "application/json"
        except Exception:
            # An unexpected demand shape is a synthetic fault: the
            # candidate's own typed compiler-failure law applies.
            return 500, _FAKE_ERROR, "application/json"


# -- The closed candidate configuration ----------------------------------


def build_candidate_config_toml(spec: V1CandidateSpec, recovery_root: Path) -> str:
    """The closed candidate configuration: the exact development
    artifact's opted-in v1 settings, bound to the probe-owned fake
    peer.  Credential references are the fixed synthetic environment
    NAMES; the values never enter the file."""
    return f"""[server]
listen_host = "{CANDIDATE_HOST}"
listen_port = {CANDIDATE_PORT}
request_body_max_bytes = 4194304
response_body_max_bytes = 4194304

[upstream]
base_url = "{spec.upstream_base_url}"
api_key_env = "{V1_PROBE_UPSTREAM_KEY_ENV}"
model = "{spec.declared_model}"

[[routes]]
name = "text"
model = "{spec.declared_model}"
max_images_per_request = 0
image_overflow_policy = "reject"
observation_enabled = true
constitution_enabled = true

[constitution]
enabled = true
identity_source = "static"
principal = "v1-probe-principal"
session = "v1-probe-session"
repository = "v1-probe-repository"

[context_cache]
profile = "dependency-bundles-v1"
workers = 1
admission_mode = "lean"
marker_key_env = "{V1_PROBE_MARKER_KEY_ENV}"

[context_cache.budget]
context_tokens = 32768

[context_cache.compiler]
model = "{spec.declared_model}"
base_url = "{spec.compiler_base_url}"
model_revision = "{PINNED_REVISION}"
compatibility_identity = "slaif-rtx3090-compat-1"
api_key_env = "{V1_PROBE_COMPILER_KEY_ENV}"

[context_cache.ram]
session_max_owned_bytes = 134217728
process_max_owned_bytes = 536870912

[context_cache.recovery]
enabled = true
root = "{recovery_root}"

[context_cache.route_contracts.text]
model = "{spec.declared_model}"
context_tokens = 32768
"""


# -- The serial run lifecycle ---------------------------------------------


def acquire_run_lock(work_root: Path, run_id: str) -> Path:
    """ONE probe run at a time (the closed serial opt-in).  ANY
    pre-existing lock file — live, stale or malformed — is the closed
    run-in-progress refusal: the probe's own state lives in an
    exactly-owned fresh run directory, so there is no stale-lock
    takeover to perform, and plain exclusive acquisition (no
    read/unlink race) preserves pre-existing unrelated state."""
    lock_path = work_root / "v1-probe.lock"
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise V1ProbeRefusal(
            REFUSAL_RUN_IN_PROGRESS, "a pre-existing run lock is present"
        ) from None
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(f"pid={os.getpid()} run_id={run_id}\n")
            stream.flush()
            os.fsync(stream.fileno())
    except OSError:
        # Only the marker THIS invocation just created is removed when
        # the write fails; pre-existing unrelated state is never
        # touched.
        try:
            os.unlink(lock_path)
        except OSError:
            pass
        raise V1ProbeRefusal(REFUSAL_RUN_IN_PROGRESS, "the run lock could not be written") from None
    return lock_path


def release_run_lock(lock_path: Path) -> None:
    """Unlink only the marker this invocation created (its own pid;
    plain exclusive acquisition means a file this process created can
    only be its own); a foreign or unreadable file is left in place."""
    try:
        content = lock_path.read_text(encoding="utf-8").strip()
    except OSError:
        return
    match = re.fullmatch(r"pid=(\d+) run_id=([0-9a-f]{32})", content)
    if match is not None and int(match.group(1)) == os.getpid():
        try:
            os.unlink(lock_path)
        except OSError:
            pass


def _write_private(path: Path, text: str) -> None:
    """The atomic 0600 writer (temp, fsync, rename; refuse pre-existing)."""
    tmp = path.with_name(f".{path.name}.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(text.encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    except BaseException:
        if tmp.exists():
            os.unlink(tmp)
        raise


def prepare_venv(wheel_path: Path, work_root: Path) -> Path:
    """The fresh candidate venv bound to the exact development
    artifact (a noneditable wheel install; no other source).  The
    venv path is inside the probe's own fresh run directory, so no
    pre-existing caller path is cleared or modified."""
    uv = shutil.which("uv")
    if uv is None:
        raise V1ProbeRefusal(REFUSAL_CANDIDATE_FAILED, "uv is not available")
    venv = work_root / "venv"
    python_bin = venv / "bin" / "python"
    for cmd in (
        [uv, "venv", "--python", "3.12", str(venv)],
        [uv, "pip", "install", "--python", str(python_bin), "--no-cache", str(wheel_path)],
    ):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        except (OSError, subprocess.TimeoutExpired):
            raise V1ProbeRefusal(
                REFUSAL_CANDIDATE_FAILED, "the candidate venv preparation failed"
            ) from None
        if proc.returncode != 0:
            raise V1ProbeRefusal(REFUSAL_CANDIDATE_FAILED, "the candidate venv preparation failed")
    if not python_bin.is_file():
        raise V1ProbeRefusal(REFUSAL_CANDIDATE_FAILED, "the candidate venv python is missing")
    return python_bin


def start_candidate(
    venv_python: Path,
    config_path: Path,
    work_root: Path,
    credential_values: Mapping[str, str],
) -> subprocess.Popen[bytes]:
    """The candidate process on the closed 18031 port.  Safe
    credential custody: the child receives a MINIMAL environment
    holding ONLY the probe-generated synthetic credential values for
    this run (the three configured environment names; generated
    inside the run, never printed, never from the host
    environment, nothing else)."""
    env = dict(credential_values)
    log_path = work_root / "candidate.log"
    log = os.fdopen(os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600), "ab")
    try:
        return subprocess.Popen(
            [str(venv_python), "-m", "slaif_local_coding", "--config", str(config_path)],
            stdout=log,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=str(work_root),
        )
    except OSError:
        raise V1ProbeRefusal(
            REFUSAL_CANDIDATE_FAILED, "the candidate process could not start"
        ) from None
    finally:
        log.close()


def wait_candidate_ready(candidate: subprocess.Popen[bytes]) -> None:
    """The bounded readiness gate: poll the known child's listener
    identity FIRST and only request /healthz once the exact launched
    child owns the 18031 LISTEN socket (no HTTP before ownership; a
    free-port precheck alone leaves an ownership race)."""
    deadline = time.monotonic() + CANDIDATE_READY_TIMEOUT_SECONDS
    url = f"http://{CANDIDATE_HOST}:{CANDIDATE_PORT}/healthz"
    client = httpx.Client(timeout=2.0, trust_env=False)
    try:
        while time.monotonic() < deadline:
            if candidate.poll() is not None:
                raise V1ProbeRefusal(
                    REFUSAL_CANDIDATE_FAILED,
                    "the candidate process exited before readiness",
                )
            if not _child_owns_listener(candidate, CANDIDATE_PORT):
                time.sleep(0.25)
                continue
            try:
                response = client.get(url)
            except httpx.HTTPError:
                response = None
            if response is not None and response.status_code == 200:
                return
            time.sleep(0.25)
    finally:
        client.close()
    raise V1ProbeRefusal(REFUSAL_CANDIDATE_UNREACHABLE, "the candidate never became ready")


def stop_candidate(candidate: subprocess.Popen[bytes]) -> None:
    """The bounded stop: SIGTERM, then SIGKILL, then the closed port
    check (the 18031 listener must be gone)."""
    if candidate.poll() is None:
        candidate.terminate()
        try:
            candidate.wait(timeout=10)
        except subprocess.TimeoutExpired:
            candidate.kill()
            candidate.wait(timeout=10)
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if probe.connect_ex((CANDIDATE_HOST, CANDIDATE_PORT)) == 0:
            raise V1ProbeRefusal(
                REFUSAL_CANDIDATE_FAILED, "the candidate port is still open after stop"
            )
    finally:
        probe.close()


def _require_loopback_port_free(port: int, token: str, detail: str) -> None:
    """Ownership pre-check: the closed loopback port must have NO
    listener before the probe starts its own owner there (after
    startup, the candidate child and the peer thread are the only
    processes this run created that can bind those ports)."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if probe.connect_ex((CANDIDATE_HOST, port)) == 0:
            raise V1ProbeRefusal(token, detail)
    finally:
        probe.close()


def _listener_inodes(port: int) -> set[str]:
    """The socket inodes in LISTEN state on the closed loopback port
    (kernel /proc/net tables; content-free network metadata)."""
    inodes: set[str] = set()
    for table in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            with open(table, encoding="ascii") as stream:
                lines = stream.readlines()
        except OSError:
            continue
        for line in lines[1:]:
            parts = line.split()
            if len(parts) < 10 or parts[3] != "0A":  # 0A = LISTEN
                continue
            try:
                local_port = int(parts[1].rsplit(":", 1)[1], 16)
            except (IndexError, ValueError):
                continue
            if local_port == port:
                inodes.add(parts[9])
    return inodes


def _child_owns_listener(candidate: subprocess.Popen[bytes], port: int) -> bool:
    """Prove that the exact launched child owns the LISTEN socket on
    the closed port: the port's LISTEN inodes are matched against the
    child's OWN fd directory only (no host-process enumeration).
    Returns False when no listener exists, the child fd directory is
    unreadable, or no fd maps to a listener inode."""
    inodes = _listener_inodes(port)
    if not inodes:
        return False
    fd_dir = f"/proc/{candidate.pid}/fd"
    try:
        fds = os.listdir(fd_dir)
    except OSError:
        return False
    for fd in fds:
        try:
            target = os.readlink(f"{fd_dir}/{fd}")
        except OSError:
            continue
        if target.startswith("socket:[") and target[8:-1] in inodes:
            return True
    return False


def retain_facts(facts: V1ProbeFacts, work_root: Path) -> Path:
    """The protected 0600 facts retention (atomic; refuse pre-existing)."""
    path = work_root / f"v1-probe-facts-{facts.run_id}.json"
    if path.exists():
        raise V1ProbeRefusal(REFUSAL_RUN_IN_PROGRESS, "the facts file for this run already exists")
    payload = (json.dumps(facts.to_dict(), indent=2, sort_keys=True) + "\n").encode("utf-8")
    tmp = work_root / f".{path.name}.tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    except BaseException:
        if tmp.exists():
            os.unlink(tmp)
        raise
    return path


# -- The opt-in entry point -------------------------------------------------


async def _probe_client_session(spec: V1CandidateSpec, capture: V1PeerCapture) -> V1ProbeFacts:
    async with httpx.AsyncClient(
        base_url=f"http://{CANDIDATE_HOST}:{CANDIDATE_PORT}",
        timeout=spec.request_timeout_seconds,
        trust_env=False,
    ) as client:
        return await run_v1_probe_session(client=client, spec=spec, capture=capture)


def _emit(status: str, **fields: Any) -> None:
    sys.stdout.write(json.dumps({"status": status, **fields}, sort_keys=True) + "\n")
    sys.stdout.flush()


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="v1_actual_model_probe",
        description="the bounded opt-in v1 actual-model qualification probe (024-a)",
    )
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--work-root", required=True)
    parser.add_argument("--wheel", default=None)
    parser.add_argument("--wheel-sha256", default=None)
    parser.add_argument("--declared-model", default=DEFAULT_DECLARED_MODEL)
    parser.add_argument("--upstream-base-url", default=f"http://{PEER_HOST}:{PEER_PORT}/v1")
    parser.add_argument("--compiler-base-url", default=f"http://{PEER_HOST}:{PEER_PORT}/v1")
    parser.add_argument("--max-main-requests", type=int, default=DEFAULT_MAX_MAIN_REQUESTS)
    parser.add_argument("--max-response-bytes", type=int, default=DEFAULT_MAX_RESPONSE_BYTES)
    parser.add_argument(
        "--request-timeout-seconds", type=float, default=DEFAULT_REQUEST_TIMEOUT_SECONDS
    )
    parser.add_argument("--total-budget-seconds", type=float, default=DEFAULT_TOTAL_BUDGET_SECONDS)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if not args.confirm:
        _emit(
            "refused",
            token=REFUSAL_SPEC_INVALID,
            detail="opt-in confirmation is required",
        )
        return 3
    run_id = secrets.token_hex(16)
    wheel = Path(args.wheel or os.environ.get("SLAIF_V1_PROBE_WHEEL", ""))
    wheel_sha256 = args.wheel_sha256 or os.environ.get("SLAIF_V1_PROBE_WHEEL_SHA256", "")
    if not str(wheel) or not wheel_sha256:
        _emit("refused", token=REFUSAL_SPEC_INVALID, detail="wheel reference is missing")
        return 3
    spec = V1CandidateSpec(
        declared_model=args.declared_model,
        run_id=run_id,
        upstream_base_url=args.upstream_base_url,
        compiler_base_url=args.compiler_base_url,
        max_main_requests=args.max_main_requests,
        max_response_bytes=args.max_response_bytes,
        request_timeout_seconds=float(args.request_timeout_seconds),
        total_budget_seconds=float(args.total_budget_seconds),
    )
    candidate: subprocess.Popen[bytes] | None = None
    peer: V1FakePeer | None = None
    lock_path: Path | None = None
    run_dir: Path | None = None
    facts: V1ProbeFacts | None = None
    rc = 0
    runtime_phase = False
    try:
        spec.validate()
        verify_artifact_identity(wheel, wheel_sha256)
        # Probe-generated synthetic credentials for THIS run (never
        # caller-selected host environment references; never emitted).
        credential_values = {
            V1_PROBE_UPSTREAM_KEY_ENV: secrets.token_hex(32),
            V1_PROBE_COMPILER_KEY_ENV: secrets.token_hex(32),
            V1_PROBE_MARKER_KEY_ENV: secrets.token_hex(32),
        }
        work_root = Path(args.work_root)
        # The caller work root is used as-is (created 0700 only when
        # absent; an existing path is never re-moded).
        try:
            if not work_root.is_dir():
                work_root.mkdir(mode=0o700, parents=True)
        except (FileExistsError, OSError):
            raise V1ProbeRefusal(REFUSAL_CANDIDATE_FAILED, "the work root is not usable") from None
        # The probe's own state lives in an exactly-owned fresh run
        # directory (refused when it already exists).
        try:
            run_dir = work_root / f"v1-run-{run_id}"
            run_dir.mkdir(mode=0o700)
        except FileExistsError:
            raise V1ProbeRefusal(
                REFUSAL_CANDIDATE_FAILED, "the fresh run directory already exists"
            ) from None
        except OSError:
            raise V1ProbeRefusal(REFUSAL_CANDIDATE_FAILED, "the work root is not usable") from None
        lock_path = acquire_run_lock(work_root, run_id)
        venv_python = prepare_venv(wheel, run_dir)
        recovery_root = run_dir / "recovery"
        recovery_root.mkdir(mode=0o700)
        config_path = run_dir / "candidate.toml"
        _write_private(config_path, build_candidate_config_toml(spec, recovery_root))
        _require_loopback_port_free(
            CANDIDATE_PORT,
            REFUSAL_CANDIDATE_FAILED,
            "the candidate port is already in use",
        )
        _require_loopback_port_free(
            PEER_PORT, REFUSAL_PEER_PORT_BUSY, "the probe peer port is busy"
        )
        peer = V1FakePeer(spec)
        peer.start()
        candidate = start_candidate(venv_python, config_path, run_dir, credential_values)
        runtime_phase = True
        wait_candidate_ready(candidate)
        facts = asyncio.run(_probe_client_session(spec, peer.capture))
    except V1ProbeRefusal as exc:
        _emit("refused", token=exc.token, detail=exc.detail)
        rc = 4 if runtime_phase else 3
    finally:
        # Cleanup runs on EVERY path: a refused venv, peer or
        # candidate startup releases every resource already
        # acquired, including the lock; a failed candidate-shutdown
        # verification can never skip the peer and lock release.
        stop_error: V1ProbeRefusal | None = None
        if candidate is not None:
            try:
                stop_candidate(candidate)
            except V1ProbeRefusal as exc:
                stop_error = exc
        if peer is not None:
            try:
                peer.shutdown()
            except OSError:
                pass  # the bounded peer teardown never blocks the lock
        if lock_path is not None:
            release_run_lock(lock_path)
        if stop_error is not None:
            if rc == 0:
                _emit("refused", token=stop_error.token, detail=stop_error.detail)
                rc = 4
            else:
                # A secondary content-free line (the primary
                # refusal was already emitted on stdout).
                sys.stderr.write(
                    json.dumps(
                        {
                            "status": "cleanup-refused",
                            "token": stop_error.token,
                            "detail": stop_error.detail,
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )
                sys.stderr.flush()
    if rc == 0:
        # Success path after cleanup: the facts file is retained at
        # <work-root>/v1-run-<run-id>/v1-probe-facts-<run-id>.json;
        # no private path is emitted.  This runs OUTSIDE the finally
        # block so an unexpected setup exception can never be masked
        # by the facts assertion.
        assert facts is not None and run_dir is not None
        retain_facts(facts, run_dir)
        _emit("complete", facts=facts.to_dict())
    return rc


if __name__ == "__main__":
    sys.exit(main())
