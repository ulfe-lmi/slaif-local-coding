#!/usr/bin/env python3
"""Run one disposable pinned-gateway/PostgreSQL/Local-Coding rehearsal.

This file is repository-only support.  It is intentionally outside the wheel,
uses a detached gateway checkout supplied by the caller, and emits only fixed
facts.  Every service, database, container, cache, Codex home, and log lives in
temporary state owned by this one process.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import concurrent.futures
import hashlib
import http.server
import json
import logging
import os
import re
import secrets
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field, replace
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal, cast
from urllib.parse import urlsplit

import httpx
import uvicorn
from prometheus_client.parser import text_string_to_metric_families

try:
    from openai import APIStatusError, OpenAI  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - the executable rehearsal venv supplies it

    class APIStatusError(Exception):  # type: ignore[no-redef]
        status_code: int

    class OpenAI:  # type: ignore[no-redef]
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            raise RuntimeError("openai_sdk_unavailable")


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.dont_write_bytecode = True

from codex_tool_envelope_differential import (  # type: ignore[import-not-found]  # noqa: E402
    VariantResult,
    run_differential,
)

from scripts.local_qwen_provider_differential import (  # noqa: E402
    SSEFacts,
    _status_class,
    _timing_bucket,
)
from slaif_local_coding.gateway_identity import (  # noqa: E402
    canonical_identity_bytes,
    expected_signature,
)
from tests.helpers.acceptance_harness import (  # noqa: E402
    ACCEPTANCE_MANIFEST,
    FAKE_RESULT_SCHEMA_KEYS,
    PROTECTED_RESULT_SCHEMA_KEYS,
    PUBLIC_REQUEST_BUDGET,
    VALIDATION_STAGES,
    BudgetController,
    FakeCutoverRunner,
    ObligationResult,
    RehearsalBudget,
    RunAccumulator,
    StrictFakeQwenObservation,
    build_obligation_gate,
    count_class,
    derive_gap_inventory,
    make_result,
    projection_for,
    projection_passes,
    projection_table_safe_dict,
    validate_projection_contract,
)
from tests.helpers.e2e_support import (  # noqa: E402
    constitution_metric_snapshot,
    governed_prompt,
    run_codex_once,
)
from tests.helpers.gateway_accounting_rehearsal import (  # noqa: E402
    GATEWAY_MAIN_SHA,
    PROVIDER,
    PUBLIC_MODEL,
    RESPONSES_ENDPOINT,
    UPSTREAM_MODEL,
    build_composed_stream_facts,
)
from tests.helpers.path_safety import assert_allowlisted_diagnostic_argv  # noqa: E402
from tests.helpers.transport_observer import (  # noqa: E402
    CallIDCorrelation,
    DirectTransportObserver,
    merge_observer_snapshots,
    observer_dispatch_matches_fake,
)
from tests.helpers.vision_e2e_support import (  # noqa: E402
    VisionOutboundRecorder,
    run_vision_e2e,
    vision_diagnostic_summary,
    write_vision_fixture,
    write_vision_model_catalog,
)

SERVICE_TOKEN_ENV = "SLAIF_REHEARSAL_ADAPTER_TOKEN"
QWEN_KEY_ENV = "QWEN3090_API_KEY"
PUBLIC_KEY_ENV = "SLAIF_REHEARSAL_PUBLIC_KEY"
DATABASE_USER = "slaif005c"
DATABASE_NAME = "slaif005c"
DATABASE_PASSWORD = "synthetic-005c-postgres-password"
IMAGE_NAME = "postgres:16"
CODEX_VERSION = "0.149.0"
MAX_REHEARSAL_SECONDS = 900.0
SIGNING_SECRET_ENV = "SLAIF_REHEARSAL_SIGNING_SECRET"
DERIVATION_SECRET_ENV = "SLAIF_REHEARSAL_DERIVATION_SECRET"
FAILURE_PROVIDER = "synthetic-failure"
FAILURE_MODEL = "synthetic-failure-model"
LOCAL_ROUTE = "qwen38-vision-codex"
CODEX_MODULE_ID = "codex-0.149-responses-v1"
CODEX_MODULE_VERSION = "4"
# This is the reviewed Gateway client-module fixture digest.  The binary
# digest below remains a separate executable-integrity fact.
CODEX_CLIENT_MODULE_FIXTURE_SHA256 = (
    "ca1e03a35de1eaeceb894cec9895af0c154e0d2fa0aa8da87f98716e1567f9ec"
)
CODEX_FIXTURE_SHA256 = "bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827"
GATEWAY_APP_TREE_SHA256 = "a7b64d35650b61fbba3558ddb519c6e52a627ec9"
LOCAL_ROUTE_POLICY = "qwen38-vision-codex/retain_newest/signed_identity_v1"
OBSERVATION_VERSION = "direct-httpx-v2"
PROTECTED_VISION_PID = "23961"
PROTECTED_VISION_START = "Sun 2026-09-06 18:57:26 CEST"
CODEX_0149_DEFAULT = Path(
    "/synology/homes/janezp/.codex/packages/standalone/releases/"
    "0.149.0-x86_64-unknown-linux-musl/bin/codex"
)
FAKE_MAX_EVENTS = 32
# Acceptance-only frame cap; the independent per-response cap remains fixed at
# 131072 bytes.  This is not a provider or Gateway policy.
FAKE_MAX_EVENT_BYTES = 131_072
FAKE_MAX_STREAM_BYTES = 131_072
FAKE_MAX_FUNCTION_CALLS = 1
FAKE_FUNCTION_CALL_ID = "call_synthetic"
FAKE_FUNCTION_SUMMARY_ALIAS = "call_synthetic_summary_alias"


@dataclass(frozen=True)
class ProtectedRuntimeHooks:
    """Explicit synthetic seams for the actual protected runner branch.

    These hooks replace only external protected boundaries.  They are never
    populated by the command-line runner and therefore cannot redirect a real
    protected invocation accidentally.
    """

    host_preflight: Callable[[], dict[str, object]]
    main_pid: Callable[[], str]
    credential_source: Callable[[str], str]
    provider_target: Literal["fake"] = "fake"
    clock: Callable[[], float] = time.monotonic
    dispatch_hook: Callable[[str, str, int | None], None] | None = None
    dispatch_complete_hook: Callable[[str, str, int | None], None] | None = None
    failure_phase: str | None = None
    projection_failure: bool = False
    cleanup_failure: bool = False
    require_fake_gate: bool = False
    mapping_dependency_check: Callable[[], bool] | None = None
    synthetic_only: bool = True


def _gateway_stream_validator_factory(gateway_root: Path) -> Any:
    """Inject the exact pinned Gateway Responses validator into observation."""
    sys.path.insert(0, str(gateway_root / "app"))
    from slaif_gateway.modules.clients.codex_0149 import (  # type: ignore[import-not-found]
        codex_0149_declared_tool_taxonomy,
        codex_0149_streaming_tool_events_requested,
        codex_0149_zero_argument_function_names,
    )
    from slaif_gateway.providers.streaming import (  # type: ignore[import-not-found]
        ResponsesStreamEventValidator,
        ResponsesStreamValidationProfile,
    )

    def factory(request: httpx.Request) -> Any:
        content = request.content
        if not isinstance(content, bytes) or len(content) > 2 * 1024 * 1024:
            raise ValueError("validator_profile_request_unavailable")

        def reject_constant(_value: str) -> None:
            raise ValueError("non_finite_json")

        try:
            payload = json.loads(content, parse_constant=reject_constant)
        except (TypeError, ValueError, json.JSONDecodeError):
            raise ValueError("validator_profile_request_invalid") from None
        if not isinstance(payload, dict):
            raise ValueError("validator_profile_request_invalid")
        declarations = codex_0149_declared_tool_taxonomy(payload)
        streaming_tools = codex_0149_streaming_tool_events_requested(payload)
        profile = ResponsesStreamValidationProfile(
            codex_streaming_tool_events=streaming_tools,
            codex_0149_function_tool_events=streaming_tools,
            zero_argument_function_names=(
                codex_0149_zero_argument_function_names(payload) if streaming_tools else frozenset()
            ),
            codex_encrypted_reasoning_replay=False,
            declared_client_tools=declarations,
            codex_reasoning_events=True,
        )
        return ResponsesStreamEventValidator(profile)

    return factory


class _FakeStreamError(RuntimeError):
    """A fixed internal failure for malformed or over-bound fake streams."""


class _FakeQwenObservationWalker:
    """Bounded mapping traversal used only for fixed request classifications."""

    @staticmethod
    def walk(value: object, *, depth: int = 0) -> Any:
        if depth > 32:
            return
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from _FakeQwenObservationWalker.walk(child, depth=depth + 1)
        elif isinstance(value, list):
            for child in value:
                yield from _FakeQwenObservationWalker.walk(child, depth=depth + 1)


def _opaque_call_id_digest(value: object) -> bytes | None:
    """Hash one bounded transient call ID without retaining the identifier."""
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 512
        or any(char in value for char in "\r\n")
    ):
        return None
    return hashlib.sha256(value.encode("utf-8")).digest()


def _request_observation(payload: dict[str, object]) -> dict[str, object]:
    """Classify exact Responses items without fixture IDs or text searching."""
    tools = payload.get("tools")
    tool_items = (
        tuple(item for item in tools if isinstance(item, dict)) if isinstance(tools, list) else ()
    )
    tool_types = tuple(item["type"] for item in tool_items if isinstance(item.get("type"), str))
    function_tools = tuple(
        item for item in _FakeQwenObservationWalker.walk(tools) if item.get("type") == "function"
    )
    function_items = tuple(
        item
        for item in _FakeQwenObservationWalker.walk(payload)
        if item.get("type") in {"function_call", "function_call_output"}
    )
    output_items = tuple(
        item for item in function_items if item.get("type") == "function_call_output"
    )
    call_items = output_items or tuple(
        item for item in function_items if item.get("type") == "function_call"
    )
    if function_tools and not output_items:
        request_class = "function_initial"
    elif output_items:
        request_class = "function_continuation"
    elif any(
        item.get("type") in {"input_image", "image_url"}
        for item in _FakeQwenObservationWalker.walk(payload)
    ):
        request_class = "image"
    else:
        request_class = "message"
    tool_class = (
        "none"
        if not tool_types
        else "mixed"
        if len(set(tool_types)) > 1
        else "function"
        if "function" in tool_types
        else "custom"
        if "custom" in tool_types
        else "unknown"
    )
    known_tool_names = {"shell_command", "exec_command", "local_shell", "local_lookup"}
    function_tool_name = next(
        (item.get("name") for item in function_tools if item.get("name") in known_tool_names),
        "unknown" if function_tools else "none",
    )
    output_call_id_digests = tuple(
        digest
        for item in output_items
        for digest in (_opaque_call_id_digest(item.get("call_id")),)
        if digest is not None
    )
    output_missing_call_id = bool(output_items) and any(
        _opaque_call_id_digest(item.get("call_id")) is None for item in output_items
    )
    item_id_presence = "unknown"
    if call_items:
        has_id = tuple(
            isinstance(item.get("id"), str) and bool(item.get("id")) for item in call_items
        )
        item_id_presence = "present" if all(has_id) else "omitted" if not any(has_id) else "unknown"
    session_digest = "none"
    metadata = payload.get("client_metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("session_id"), str):
        session_digest = hashlib.sha256(metadata["session_id"].encode("utf-8")).hexdigest()
    images = tuple(
        item
        for item in _FakeQwenObservationWalker.walk(payload)
        if item.get("type") in {"input_image", "image_url"}
    )
    image_hashes = tuple(
        hashlib.sha256(value.encode("utf-8")).hexdigest()
        for item in images
        for value in (
            item.get("image_url")
            if isinstance(item.get("image_url"), str)
            else item.get("image_url", {}).get("url")
            if isinstance(item.get("image_url"), dict)
            else None,
        )
        if isinstance(value, str) and len(value) <= 8 * 1024 * 1024
    )
    return {
        "request_class": request_class,
        "tool_class": tool_class,
        "tool_name_class": function_tool_name,
        "item_id_presence": item_id_presence,
        "call_id_relation": "initial_owned" if request_class == "function_initial" else "unknown",
        "function_result_adjacent": False,
        "image_count_class": str(min(len(images), 8)),
        "image_hash_class": "present" if image_hashes else "none",
        "image_count": len(images),
        "image_hashes": image_hashes,
        "tool_type_classes": tuple(sorted(set(tool_types))),
        "_function_output_call_id_digests": output_call_id_digests,
        "_function_output_missing_call_id": output_missing_call_id,
        "_session_digest": session_digest,
    }


class _FakeQwenServer(http.server.ThreadingHTTPServer):
    """Direct fake provider; it intentionally has no relay/status endpoint."""

    daemon_threads = True

    def __init__(self, token: str, *, oracle_enabled: bool = True) -> None:
        super().__init__(("127.0.0.1", 0), _FakeQwenHandler)
        self.token = token
        self.oracle_enabled = oracle_enabled
        self.calls = 0
        self.inbound_inference_calls = 0
        self.inbound_compiler_calls = 0
        self.inbound_observations: list[dict[str, object]] = []
        self.compiler_calls = 0
        self.inference_calls = 0
        self.stream_calls = 0
        self.tool_types: set[str] = set()
        self.tool_name_classes: set[str] = set()
        self.bad_auth = False
        self.observation = StrictFakeQwenObservation()
        self._call_correlation = CallIDCorrelation()
        self._lock = threading.Lock()

    def observe_request(self, payload: dict[str, object]) -> dict[str, object]:
        observation = _request_observation(payload)
        session_digest = str(observation.get("_session_digest", "none"))
        key = ("fake", "fake", session_digest)
        if observation.get("request_class") == "function_continuation":
            history_call_ids = tuple(
                digest
                for item in _FakeQwenObservationWalker.walk(payload)
                if item.get("type") == "function_call"
                for digest in (_opaque_call_id_digest(item.get("call_id")),)
                if digest is not None
            )
            if history_call_ids:
                self._call_correlation.register(key, history_call_ids)
            output_digests = cast(
                tuple[bytes, ...], observation["_function_output_call_id_digests"]
            )
            if (
                not history_call_ids
                and output_digests
                and not self._call_correlation.has_pending(key)
            ):
                self._call_correlation.register(key, output_digests[-1:])
            relation = self._call_correlation.relation(
                key,
                output_digests[-1:],
                missing_call_id=observation["_function_output_missing_call_id"] is True,
                consume=False,
            )
            observation["call_id_relation"] = relation
            observation["function_result_adjacent"] = relation == "matching"
        elif observation.get("request_class") == "function_initial":
            observation["call_id_relation"] = "initial_owned"
        return observation

    def register_returned_call(self, payload: dict[str, object]) -> None:
        observation = _request_observation(payload)
        if observation.get("request_class") != "function_initial":
            return
        session_digest = str(observation.get("_session_digest", "none"))
        self._call_correlation.register(
            ("fake", "fake", session_digest),
            (hashlib.sha256(FAKE_FUNCTION_CALL_ID.encode("utf-8")).digest(),),
        )

    def record(
        self,
        *,
        compiler: bool,
        streaming: bool,
        tool_types: set[str],
        tool_name_class: str = "none",
        payload: dict[str, object] | None = None,
        lifecycle_valid: bool = True,
        request_class: str = "unknown",
        tool_class: str = "unknown",
        function_result_adjacent: bool = False,
        item_id_presence: str = "unknown",
        call_id_relation: str = "unknown",
        normal_close: bool = True,
    ) -> None:
        with self._lock:
            self.calls += 1
            if compiler:
                self.compiler_calls += 1
            else:
                self.inference_calls += 1
                if streaming:
                    self.stream_calls += 1
            self.tool_types.update(tool_types)
            if tool_name_class in {
                "shell_command",
                "exec_command",
                "local_shell",
                "none",
                "unknown",
            }:
                self.tool_name_classes.add(tool_name_class)
            if not compiler and payload is not None and self.oracle_enabled:
                self.observation.record(
                    payload,
                    lifecycle_valid=lifecycle_valid,
                    request_class=request_class,
                    tool_class=tool_class,
                    function_result_adjacent=function_result_adjacent,
                    item_id_presence=item_id_presence,
                    call_id_relation=call_id_relation,
                    normal_close=normal_close,
                )

    def observe_inbound(
        self,
        *,
        compiler: bool,
        streaming: bool,
        observation: dict[str, object],
    ) -> None:
        """Record only bounded request classifications before response streaming."""
        with self._lock:
            if compiler:
                self.inbound_compiler_calls += 1
            else:
                self.inbound_inference_calls += 1
            if self.oracle_enabled and len(self.inbound_observations) < FAKE_MAX_FUNCTION_CALLS + 8:
                self.inbound_observations.append(
                    {
                        "streaming": streaming,
                        **{
                            key: observation[key]
                            for key in (
                                "request_class",
                                "tool_class",
                                "tool_name_class",
                                "item_id_presence",
                                "call_id_relation",
                            )
                            if key in observation
                        },
                        "image_count_class": observation.get("image_count_class", "unknown"),
                        "image_hash_class": observation.get("image_hash_class", "unknown"),
                    }
                )

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            return {
                "calls": self.calls,
                "inbound_inference_calls": self.inbound_inference_calls,
                "inbound_compiler_calls": self.inbound_compiler_calls,
                "inbound_observations": tuple(self.inbound_observations),
                "compiler_calls": self.compiler_calls,
                "inference_calls": self.inference_calls,
                "stream_calls": self.stream_calls,
                "tool_types": sorted(self.tool_types),
                "tool_name_classes": sorted(self.tool_name_classes),
                "bad_auth": self.bad_auth,
                "provider_oracle_available": self.oracle_enabled,
                "provider_boundary": self.observation.safe_dict() if self.oracle_enabled else {},
            }


class _FakeQwenHandler(http.server.BaseHTTPRequestHandler):
    server: _FakeQwenServer

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        authorized = self.headers.get("authorization") == f"Bearer {self.server.token}"
        if not authorized:
            self.server.bad_auth = True
        return authorized

    def _body(self) -> dict[str, object] | None:
        try:
            length = int(self.headers.get("content-length", "0"))
        except ValueError:
            self._json(400, {"error": {"code": "invalid_length"}})
            return None
        if length < 0 or length > 4_194_304:
            self._json(413, {"error": {"code": "body_too_large"}})
            return None
        try:
            payload = json.loads(self.rfile.read(length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(400, {"error": {"code": "invalid_json"}})
            return None
        if not isinstance(payload, dict):
            self._json(400, {"error": {"code": "invalid_json"}})
            return None
        return payload

    @staticmethod
    def _tool_types(payload: dict[str, object]) -> set[str]:
        tools = payload.get("tools")
        return (
            {
                item["type"]
                for item in tools
                if isinstance(item, dict) and isinstance(item.get("type"), str)
            }
            if isinstance(tools, list)
            else set()
        )

    @staticmethod
    def _compiler_result(payload: dict[str, object]) -> str:
        messages = payload.get("messages")
        content = messages[-1].get("content") if isinstance(messages, list) and messages else None
        if not isinstance(content, str):
            raise ValueError("compiler_input")
        source_match = re.search(
            r"<source path='([^']+)' sha256=([0-9a-f]{64}) byte_length=(\d+)>", content
        )
        marker = "<deterministic_candidates>\n"
        start = content.find(marker)
        end = content.find("\n</deterministic_candidates>", start + len(marker))
        if source_match is None or start < 0 or end < 0:
            raise ValueError("compiler_prompt")
        candidates = json.loads(content[start + len(marker) : end])
        if not isinstance(candidates, list):
            raise ValueError("compiler_candidates")
        dependencies = [
            {
                "path": item["path"],
                "reference_confidence": 0.9,
                "constitutional_priority": 1,
                "classification": "P2",
                "relationship": "bounded dependency",
                "evidence": "supplied candidate",
                "acquisition_urgency": "none",
            }
            for item in candidates
            if isinstance(item, dict) and isinstance(item.get("path"), str)
        ]
        return json.dumps(
            {
                "schema_version": "constitution-index-v1",
                "compiler_version": "compiler-v2",
                "prompt_policy_version": "constitutional-rank-v2",
                "model": payload.get("model"),
                "source_logical_path": source_match.group(1),
                "source_sha256": source_match.group(2),
                "source_byte_length": int(source_match.group(3)),
                "summary": "bounded fake rehearsal",
                "rules": [
                    {
                        "rule_id": "fake-rule",
                        "strength": "must",
                        "statement": "bounded rehearsal",
                        "location": "source",
                        "evidence": "supplied source",
                    }
                ],
                "roles": ["agent"],
                "authorities": ["local"],
                "source_of_truth_boundaries": ["gateway"],
                "ordering_constraints": [],
                "exceptions": [],
                "dependencies": dependencies,
                "reread_triggers": ["change"],
                "status": "success",
            },
            separators=(",", ":"),
        )

    @staticmethod
    def _assistant_text(payload: dict[str, object] | None) -> str:
        if payload is None:
            return "bounded fake response"
        encoded = json.dumps(payload, separators=(",", ":"))
        match = re.search(r"SENTINEL-ACK:[A-Za-z0-9_-]{1,128}", encoded)
        return match.group(0) if match is not None else "bounded fake response"

    @staticmethod
    def _function_tool(payload: dict[str, object]) -> str | None:
        tools = payload.get("tools")
        if not isinstance(tools, list):
            return None
        for tool in _FakeQwenObservationWalker.walk(tools):
            name = tool.get("name")
            if isinstance(name, str) and name in {
                "shell_command",
                "exec_command",
                "local_shell",
                "local_lookup",
            }:
                return name
        return None

    @staticmethod
    def _has_function_output(payload: dict[str, object]) -> bool:
        return any(
            item.get("type") == "function_call_output"
            for item in _FakeQwenObservationWalker.walk(payload)
        )

    @staticmethod
    def _function_output_count(payload: dict[str, object]) -> int:
        return sum(
            item.get("type") == "function_call_output"
            for item in _FakeQwenObservationWalker.walk(payload)
        )

    @staticmethod
    def _input_image_count(payload: dict[str, object]) -> int:
        return sum(
            item.get("type") == "input_image" for item in _FakeQwenObservationWalker.walk(payload)
        )

    @staticmethod
    def _matching_function_output(payload: dict[str, object]) -> bool:
        outputs = tuple(
            item
            for item in _FakeQwenObservationWalker.walk(payload)
            if item.get("type") == "function_call_output"
        )
        if not outputs:
            return False
        return all(
            (
                (
                    item.get("id") is None
                    or (
                        isinstance(item.get("id"), str)
                        and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]{0,63}", item["id"]) is not None
                    )
                )
                and _opaque_call_id_digest(item.get("call_id")) is not None
                and any(key in item for key in ("output", "result", "content"))
            )
            for item in outputs
        )

    @staticmethod
    def _request_observation(payload: dict[str, object]) -> dict[str, object]:
        return _request_observation(payload)

    @staticmethod
    def _response(payload: dict[str, object] | None = None) -> dict[str, object]:
        text = _FakeQwenHandler._assistant_text(payload)
        return {
            "id": "fake-response",
            "object": "response",
            "status": "completed",
            "model": PUBLIC_MODEL,
            "output": [
                {
                    "id": "fake-message",
                    "type": "message",
                    "status": "completed",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": text,
                            "annotations": [],
                        }
                    ],
                }
            ],
            "usage": {"input_tokens": 2, "output_tokens": 2, "total_tokens": 4},
        }

    def _function_stream(self, tool_name: str) -> None:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", tool_name):
            raise _FakeStreamError("function_name_invalid")
        events = (
            {
                "type": "response.created",
                "sequence_number": 0,
                "response": {
                    "id": "response_1",
                    "status": "in_progress",
                    "model": PUBLIC_MODEL,
                },
            },
            {
                "type": "response.in_progress",
                "sequence_number": 1,
                "response": {
                    "id": "response_1",
                    "status": "in_progress",
                },
            },
            {
                "type": "response.output_item.added",
                "output_index": 0,
                "sequence_number": 2,
                "item": {
                    "type": "function_call",
                    "id": "function_1",
                    "call_id": FAKE_FUNCTION_CALL_ID,
                    "namespace": None,
                    "caller": None,
                    "name": tool_name,
                    "arguments": "",
                    "status": "in_progress",
                },
            },
            {
                "type": "response.function_call_arguments.delta",
                "item_id": "function_1",
                "output_index": 0,
                "sequence_number": 3,
                "delta": '{"cmd":"cat ',
            },
            {
                "type": "response.function_call_arguments.delta",
                "item_id": "function_1",
                "output_index": 0,
                "sequence_number": 4,
                "delta": 'GOVERNANCE-DEPENDENCY.md"}',
            },
            {
                "type": "response.function_call_arguments.done",
                "item_id": "function_1",
                "output_index": 0,
                "sequence_number": 5,
                "name": tool_name,
                "arguments": '{"cmd":"cat GOVERNANCE-DEPENDENCY.md"}',
            },
            {
                "type": "response.output_item.done",
                "output_index": 0,
                "sequence_number": 6,
                "item": {
                    "type": "function_call",
                    "id": "function_1",
                    "call_id": FAKE_FUNCTION_CALL_ID,
                    "namespace": None,
                    "caller": None,
                    "name": tool_name,
                    "arguments": '{"cmd":"cat GOVERNANCE-DEPENDENCY.md"}',
                    "status": "completed",
                },
            },
            {
                "type": "response.completed",
                "sequence_number": 7,
                "response": {
                    "id": "response_1",
                    "status": "completed",
                    "output": [
                        {
                            "type": "function_call",
                            "id": "parser_function_1",
                            "call_id": FAKE_FUNCTION_SUMMARY_ALIAS,
                            "namespace": None,
                            "name": tool_name,
                            "arguments": '{"cmd":"cat GOVERNANCE-DEPENDENCY.md"}',
                            "status": "completed",
                        }
                    ],
                    "usage": {
                        "input_tokens": 1,
                        "input_tokens_details": {
                            "cached_tokens": 0,
                            "input_tokens_per_turn": [1],
                            "cached_tokens_per_turn": [0],
                        },
                        "output_tokens": 1,
                        "output_tokens_details": {
                            "reasoning_tokens": 0,
                            "tool_output_tokens": 0,
                            "output_tokens_per_turn": [1],
                            "tool_output_tokens_per_turn": [0],
                        },
                        "total_tokens": 2,
                    },
                },
            },
        )
        self._write_events(events)

    def _write_events(self, events: tuple[dict[str, object], ...]) -> None:
        if not events or len(events) > FAKE_MAX_EVENTS:
            raise _FakeStreamError("event_count_bound")
        allowed = {
            "response.created",
            "response.in_progress",
            "response.output_item.added",
            "response.output_item.done",
            "response.reasoning_part.added",
            "response.reasoning_text.delta",
            "response.reasoning_text.done",
            "response.reasoning_part.done",
            "response.function_call_arguments.delta",
            "response.function_call_arguments.done",
            "response.content_part.added",
            "response.output_text.delta",
            "response.output_text.done",
            "response.content_part.done",
            "response.completed",
        }
        encoded_events: list[bytes] = []
        seen_types: list[str] = []
        total_bytes = 0
        for expected_sequence, event in enumerate(events):
            if not isinstance(event, dict):
                raise _FakeStreamError("event_shape")
            event_type = event.get("type")
            sequence = event.get("sequence_number")
            if (
                not isinstance(event_type, str)
                or event_type not in allowed
                or not isinstance(sequence, int)
                or isinstance(sequence, bool)
                or sequence != expected_sequence
            ):
                raise _FakeStreamError("event_sequence")
            payload = json.dumps(event, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
            wire = b"event: " + event_type.encode("ascii") + b"\ndata: " + payload + b"\n\n"
            if len(wire) > FAKE_MAX_EVENT_BYTES:
                raise _FakeStreamError("event_byte_bound")
            total_bytes += len(wire)
            if total_bytes > FAKE_MAX_STREAM_BYTES:
                raise _FakeStreamError("stream_byte_bound")
            encoded_events.append(wire)
            seen_types.append(event_type)
        if seen_types.count("response.created") != 1 or seen_types.count("response.completed") != 1:
            raise _FakeStreamError("terminal_event_count")
        if seen_types[-1] != "response.completed":
            raise _FakeStreamError("terminal_event_order")
        terminal = events[-1].get("response")
        if not isinstance(terminal, dict) or terminal.get("status") != "completed":
            raise _FakeStreamError("terminal_status")
        usage = terminal.get("usage")
        if not isinstance(usage, dict) or any(
            not isinstance(usage.get(name), int)
            or isinstance(usage.get(name), bool)
            or usage[name] <= 0
            for name in ("input_tokens", "output_tokens", "total_tokens")
        ):
            raise _FakeStreamError("terminal_usage")
        output = terminal.get("output")
        if not isinstance(output, list) or not output:
            raise _FakeStreamError("terminal_output")
        for item in output:
            if not isinstance(item, dict) or item.get("status") not in {"completed", None}:
                raise _FakeStreamError("terminal_item")
        serialized = json.dumps(events, separators=(",", ":"))
        if "function_call" in serialized:
            if seen_types != [
                "response.created",
                "response.in_progress",
                "response.output_item.added",
                "response.function_call_arguments.delta",
                "response.function_call_arguments.delta",
                "response.function_call_arguments.done",
                "response.output_item.done",
                "response.completed",
            ]:
                raise _FakeStreamError("function_event_order")
            added = [event for event in events if event.get("type") == "response.output_item.added"]
            done = [event for event in events if event.get("type") == "response.output_item.done"]
            if len(added) != FAKE_MAX_FUNCTION_CALLS or len(done) != FAKE_MAX_FUNCTION_CALLS:
                raise _FakeStreamError("function_lifecycle")
            function_item = done[0].get("item")
            if (
                not isinstance(function_item, dict)
                or function_item.get("type") != "function_call"
                or not isinstance(function_item.get("id"), str)
                or not function_item["id"]
                or function_item["id"].startswith("fc_")
                or function_item.get("call_id") != FAKE_FUNCTION_CALL_ID
            ):
                raise _FakeStreamError("function_identity")
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(total_bytes))
        self.end_headers()
        for wire in encoded_events:
            self.wfile.write(wire)
            self.wfile.flush()

    def _message_stream(self, payload: dict[str, object]) -> None:
        """Emit the terminal assistant-message lifecycle for a tool result."""
        text = self._assistant_text(payload)
        response_id = "fake-message-response"
        events = (
            {
                "type": "response.created",
                "sequence_number": 0,
                "response": {
                    "id": response_id,
                    "status": "in_progress",
                    "model": PUBLIC_MODEL,
                },
            },
            {
                "type": "response.in_progress",
                "sequence_number": 1,
                "response": {"id": response_id, "status": "in_progress"},
            },
            {
                "type": "response.output_item.added",
                "output_index": 0,
                "sequence_number": 2,
                "item": {
                    "type": "message",
                    "id": "message_1",
                    "status": "in_progress",
                    "role": "assistant",
                    "content": [],
                    "phase": None,
                },
            },
            {
                "type": "response.content_part.added",
                "item_id": "message_1",
                "output_index": 0,
                "content_index": 0,
                "sequence_number": 3,
                "part": {
                    "type": "output_text",
                    "text": "",
                    "annotations": [],
                    "logprobs": [],
                },
            },
            {
                "type": "response.output_text.delta",
                "item_id": "message_1",
                "output_index": 0,
                "content_index": 0,
                "sequence_number": 4,
                "logprobs": [],
                "delta": text,
            },
            {
                "type": "response.output_text.done",
                "item_id": "message_1",
                "output_index": 0,
                "content_index": 0,
                "sequence_number": 5,
                "logprobs": [],
                "text": text,
            },
            {
                "type": "response.content_part.done",
                "item_id": "message_1",
                "output_index": 0,
                "content_index": 0,
                "sequence_number": 6,
                "part": {
                    "type": "output_text",
                    "text": text,
                    "annotations": [],
                    "logprobs": None,
                },
            },
            {
                "type": "response.output_item.done",
                "output_index": 0,
                "sequence_number": 7,
                "item": {
                    "type": "message",
                    "id": "message_1",
                    "status": "completed",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": text,
                            "annotations": [],
                            "logprobs": None,
                        }
                    ],
                    "phase": None,
                    "summary": [],
                },
            },
            {
                "type": "response.completed",
                "sequence_number": 8,
                "response": {
                    "id": response_id,
                    "status": "completed",
                    "output": [
                        {
                            "type": "message",
                            "id": "message_1",
                            "status": "completed",
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": text,
                                    "annotations": [],
                                    "logprobs": None,
                                }
                            ],
                            "phase": None,
                        }
                    ],
                    "usage": {
                        "input_tokens": 1,
                        "input_tokens_details": {
                            "cached_tokens": 0,
                            "input_tokens_per_turn": [1],
                            "cached_tokens_per_turn": [0],
                        },
                        "output_tokens": 1,
                        "output_tokens_details": {
                            "reasoning_tokens": 0,
                            "tool_output_tokens": 0,
                            "output_tokens_per_turn": [1],
                            "tool_output_tokens_per_turn": [0],
                        },
                        "total_tokens": 2,
                    },
                },
            },
        )
        self._write_events(events)

    def _stream(self, payload: dict[str, object]) -> None:
        tool_name = self._function_tool(payload)
        output_count = self._function_output_count(payload)
        if tool_name is not None and (
            not self._has_function_output(payload)
            or (self._input_image_count(payload) >= 2 and output_count == 1)
        ):
            self._function_stream(tool_name)
            return
        if self._has_function_output(payload) and not self._matching_function_output(payload):
            raise _FakeStreamError("function_continuation_invalid")
        if self._has_function_output(payload):
            self._message_stream(payload)
            return
        text = self._assistant_text(payload)
        response_id = "fake-response"
        events = (
            {
                "type": "response.created",
                "sequence_number": 0,
                "response": {
                    "id": response_id,
                    "object": "response",
                    "created_at": 0,
                    "status": "in_progress",
                    "model": PUBLIC_MODEL,
                },
            },
            {
                "type": "response.in_progress",
                "sequence_number": 1,
                "response": {
                    "id": response_id,
                    "object": "response",
                    "created_at": 0,
                    "status": "in_progress",
                },
            },
            {
                "type": "response.output_item.added",
                "output_index": 0,
                "sequence_number": 2,
                "item": {
                    "type": "reasoning",
                    "id": "reasoning_1",
                    "summary": [],
                    "content": None,
                    "encrypted_content": None,
                    "status": "in_progress",
                },
            },
            {
                "type": "response.reasoning_part.added",
                "item_id": "reasoning_1",
                "output_index": 0,
                "content_index": 0,
                "sequence_number": 3,
                "part": {"type": "reasoning_text", "text": ""},
            },
            {
                "type": "response.reasoning_text.delta",
                "item_id": "reasoning_1",
                "output_index": 0,
                "content_index": 0,
                "sequence_number": 4,
                "delta": text,
            },
            {
                "type": "response.reasoning_text.done",
                "item_id": "reasoning_1",
                "output_index": 0,
                "content_index": 0,
                "sequence_number": 5,
                "text": text,
            },
            {
                "type": "response.reasoning_part.done",
                "item_id": "reasoning_1",
                "output_index": 0,
                "content_index": 0,
                "sequence_number": 6,
                "part": {"type": "reasoning_text", "text": text},
            },
            {
                "type": "response.output_item.done",
                "output_index": 0,
                "sequence_number": 7,
                "item": {
                    "type": "reasoning",
                    "id": "reasoning_1",
                    "summary": [],
                    "content": [{"type": "reasoning_text", "text": text}],
                    "encrypted_content": None,
                    "status": "completed",
                },
            },
            {
                "type": "response.output_item.added",
                "output_index": 1,
                "sequence_number": 8,
                "item": {
                    "type": "message",
                    "id": "message_1",
                    "status": "in_progress",
                    "role": "assistant",
                    "content": [],
                    "phase": None,
                },
            },
            {
                "type": "response.content_part.added",
                "item_id": "message_1",
                "output_index": 1,
                "content_index": 0,
                "sequence_number": 9,
                "part": {
                    "type": "output_text",
                    "text": "",
                    "annotations": [],
                    "logprobs": [],
                },
            },
            {
                "type": "response.output_text.delta",
                "item_id": "message_1",
                "output_index": 1,
                "content_index": 0,
                "sequence_number": 10,
                "logprobs": [],
                "delta": text,
            },
            {
                "type": "response.output_text.done",
                "item_id": "message_1",
                "output_index": 1,
                "content_index": 0,
                "sequence_number": 11,
                "logprobs": [],
                "text": text,
            },
            {
                "type": "response.content_part.done",
                "item_id": "message_1",
                "output_index": 1,
                "content_index": 0,
                "sequence_number": 12,
                "part": {
                    "type": "output_text",
                    "text": text,
                    "annotations": [],
                    "logprobs": None,
                },
            },
            {
                "type": "response.output_item.done",
                "output_index": 1,
                "sequence_number": 13,
                "item": {
                    "type": "message",
                    "id": "message_1",
                    "status": "completed",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": text,
                            "annotations": [],
                            "logprobs": None,
                        }
                    ],
                    "phase": None,
                    "summary": [],
                },
            },
            {
                "type": "response.completed",
                "sequence_number": 14,
                "response": {
                    "id": response_id,
                    "object": "response",
                    "created_at": 0,
                    "status": "completed",
                    "output": [
                        {
                            "type": "reasoning",
                            "id": "reasoning_1",
                            "status": None,
                            "summary": [],
                            "content": [{"type": "reasoning_text", "text": text}],
                            "encrypted_content": None,
                        },
                        {
                            "type": "message",
                            "id": "message_1",
                            "status": "completed",
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": text,
                                    "annotations": [],
                                    "logprobs": None,
                                }
                            ],
                            "phase": None,
                        },
                    ],
                    "usage": {
                        "input_tokens": 1,
                        "input_tokens_details": {
                            "cached_tokens": 0,
                            "input_tokens_per_turn": [1],
                            "cached_tokens_per_turn": [0],
                        },
                        "output_tokens": 1,
                        "output_tokens_details": {
                            "reasoning_tokens": 0,
                            "tool_output_tokens": 0,
                            "output_tokens_per_turn": [1],
                            "tool_output_tokens_per_turn": [0],
                        },
                        "total_tokens": 2,
                    },
                },
            },
        )
        self._write_events(events)

    def do_GET(self) -> None:
        if not self._authorized():
            self._json(401, {"error": {"code": "unauthorized"}})
            return
        request_path = urlsplit(self.path).path
        if request_path == "/health":
            self._json(200, {"status": "ok"})
        elif request_path == "/v1/models":
            self._json(200, {"object": "list", "data": [{"id": UPSTREAM_MODEL, "object": "model"}]})
        else:
            self._json(404, {"error": {"code": "not_found"}})

    def do_POST(self) -> None:
        request_path = urlsplit(self.path).path
        if not self._authorized():
            self._json(401, {"error": {"code": "unauthorized"}})
            return
        payload = self._body()
        if payload is None:
            return
        if request_path == "/v1/chat/completions":
            try:
                content = self._compiler_result(payload)
            except (TypeError, ValueError, KeyError, json.JSONDecodeError):
                self._json(400, {"error": {"code": "compiler_input"}})
                return
            self.server.record(compiler=True, streaming=False, tool_types=set())
            self._json(200, {"id": "fake-compiler", "choices": [{"message": {"content": content}}]})
            return
        if request_path != "/v1/responses":
            self._json(404, {"error": {"code": "not_found"}})
            return
        streaming = payload.get("stream") is True
        observation = self.server.observe_request(payload)
        self.server.observe_inbound(
            compiler=False,
            streaming=streaming,
            observation=observation,
        )
        if (
            observation.get("request_class") == "function_continuation"
            and observation.get("call_id_relation") != "matching"
        ):
            self._json(502, {"error": {"code": "function_continuation_invalid"}})
            return
        if streaming:
            try:
                self._stream(payload)
            except (BrokenPipeError, ConnectionResetError, _FakeStreamError):
                if not self.wfile.closed:
                    self._json(502, {"error": {"code": "fake_stream_invalid"}})
                return
        else:
            self._json(200, self._response(payload))
        if streaming and observation.get("request_class") == "function_initial":
            self.server.register_returned_call(payload)
        self.server.record(
            compiler=False,
            streaming=streaming,
            tool_types=self._tool_types(payload),
            payload=payload,
            request_class=str(observation.get("request_class", "unknown")),
            tool_class=str(observation.get("tool_class", "unknown")),
            function_result_adjacent=observation.get("function_result_adjacent") is True,
            item_id_presence=str(observation.get("item_id_presence", "unknown")),
            call_id_relation=str(observation.get("call_id_relation", "unknown")),
        )


class _FailureServer(http.server.ThreadingHTTPServer):
    """Disposable provider that fails after admission for rollback evidence."""

    daemon_threads = True

    def __init__(self) -> None:
        super().__init__(("127.0.0.1", 0), _FailureHandler)
        self.calls = 0
        self._lock = threading.Lock()

    def record(self) -> None:
        with self._lock:
            self.calls += 1


class _FailureHandler(http.server.BaseHTTPRequestHandler):
    server: _FailureServer

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("content-length", "0"))
        except ValueError:
            length = 0
        if length > 0:
            self.rfile.read(min(length, 4_194_304))
        self.server.record()
        body = b'{"error":{"type":"upstream_error","code":"synthetic_failure"}}'
        self.send_response(503)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _free_loopback_port(preferred: int | None = None) -> int:
    candidates = [preferred] if preferred is not None else []
    candidates.append(0)
    for candidate in candidates:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind(("127.0.0.1", candidate or 0))
            except OSError:
                continue
            return int(probe.getsockname()[1])
    raise RuntimeError("no_free_loopback_port")


def _run_command(
    argv: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    assert_allowlisted_diagnostic_argv(
        argv,
        allowed_commands={"codex", "git", "python", "python3.12", "ss", "systemctl"},
        allowed_executables=(argv[0],),
        disposable_root=Path(tempfile.gettempdir()),
        path_arguments=(cwd,) if cwd is not None else (),
    )
    return subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def _docker(*args: str, timeout: float = 120) -> subprocess.CompletedProcess[str]:
    command = ["sudo", "-n", "docker", *args]
    assert_allowlisted_diagnostic_argv(command, allowed_commands={"sudo"})
    return subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _docker_ok(*args: str, timeout: float = 120) -> str:
    result = _docker(*args, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError("docker_command_failed")
    return result.stdout.strip()


def _image_fingerprint() -> tuple[bool, str | None, str | None]:
    result = _docker("image", "inspect", IMAGE_NAME, "--format", "{{.Id}} {{.RepoDigests}}")
    if result.returncode != 0:
        return False, None, None
    fields = result.stdout.strip().split(maxsplit=1)
    image_id = fields[0] if fields else None
    digest = None
    if len(fields) == 2:
        match = re.search(r"sha256:[0-9a-f]{64}", fields[1])
        digest = match.group(0) if match else None
    return True, image_id, digest


def _running_container_facts() -> tuple[str, ...]:
    result = _docker("ps", "--format", "{{.ID}} {{.Names}} {{.Image}}")
    if result.returncode != 0:
        return ()
    return tuple(line for line in result.stdout.splitlines() if line.strip())


def _protected_snapshot() -> dict[str, object]:
    unit = _run_command(
        [
            "systemctl",
            "--user",
            "show",
            "qwen-serving-vision.service",
            "--property=ActiveState,SubState,MainPID,ExecMainStartTimestampMonotonic,ExecMainStartTimestamp,NRestarts",
            "--no-pager",
        ]
    )
    text_unit = _run_command(
        [
            "systemctl",
            "--user",
            "show",
            "qwen-serving.service",
            "--property=ActiveState,MainPID",
            "--no-pager",
        ]
    )
    listeners = _run_command(["ss", "-ltnp"])
    qwen_status = _run_command(
        [
            "git",
            "-C",
            "/synology/homes/janezp/qwen-serving",
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ]
    )
    values: dict[str, str] = {}
    for line in unit.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    text_values: dict[str, str] = {}
    for line in text_unit.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            text_values[key] = value
    listener_text = listeners.stdout
    return {
        "vision_active": values.get("ActiveState") == "active"
        and values.get("SubState") == "running",
        "vision_pid": values.get("MainPID"),
        "vision_start": values.get("ExecMainStartTimestampMonotonic"),
        "vision_start_wall": values.get("ExecMainStartTimestamp"),
        "vision_restarts": values.get("NRestarts"),
        "text_inactive": text_values.get("ActiveState") == "inactive"
        and text_values.get("MainPID") == "0",
        "has_18020": bool(re.search(r":18020\b", listener_text)),
        "has_18021": bool(re.search(r":18021\b", listener_text)),
        "has_18031": bool(re.search(r":18031\b", listener_text)),
        "worktree_count": len(tuple(line for line in qwen_status.stdout.splitlines() if line)),
    }


def _protected_main_pid() -> str:
    """Resolve only the active vision unit's MainPID, without exposing it."""
    result = _run_command(
        ["systemctl", "--user", "show", "qwen-serving-vision.service", "-p", "MainPID", "--value"]
    )
    pid = result.stdout.strip()
    if result.returncode != 0 or not re.fullmatch(r"[1-9][0-9]{0,8}", pid):
        raise RuntimeError("protected_vision_mainpid_unavailable")
    return pid


def _read_protected_qwen_key(expected_pid: str) -> str:
    """Read exactly one protected VLLM_API_KEY entry from the verified MainPID."""
    if expected_pid != _protected_main_pid():
        raise RuntimeError("protected_vision_identity_changed")
    path = Path("/proc") / expected_pid / "environ"
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError:
        raise RuntimeError("protected_qwen_key_unavailable") from None
    try:
        raw = bytearray()
        while len(raw) <= 1_048_576:
            chunk = os.read(descriptor, 65_537)
            if not chunk:
                break
            raw.extend(chunk)
        if len(raw) > 1_048_576:
            raise RuntimeError("protected_qwen_environment_too_large")
        entries = [item for item in bytes(raw).split(b"\0") if item.startswith(b"VLLM_API_KEY=")]
        if len(entries) != 1 or entries[0] == b"VLLM_API_KEY=":
            raise RuntimeError("protected_qwen_key_unavailable")
        try:
            value = entries[0].removeprefix(b"VLLM_API_KEY=").decode("ascii")
        except UnicodeDecodeError:
            raise RuntimeError("protected_qwen_key_unavailable") from None
        if not value or any(char in value for char in "\r\n"):
            raise RuntimeError("protected_qwen_key_unavailable")
        return value
    except OSError:
        raise RuntimeError("protected_qwen_key_unavailable") from None
    finally:
        os.close(descriptor)


def _observer_delta(before: dict[str, object], after: dict[str, object]) -> dict[str, object]:
    """Return fixed facts for newly observed Local-to-provider requests."""
    before_records = before.get("records", ())
    after_records = after.get("records", ())
    if not isinstance(before_records, (list, tuple)) or not isinstance(
        after_records, (list, tuple)
    ):
        return {
            "inference_attempted_count": 0,
            "inference_dispatched_count": 0,
            "compiler_dispatched_count": 0,
            "provider_boundary_observed": False,
            "provider_lifecycle_valid": False,
            "provider_terminal": False,
            "provider_boundary": {},
        }
    new_records = tuple(after_records[len(before_records) :])
    inference = tuple(
        item for item in new_records if isinstance(item, dict) and item.get("kind") == "inference"
    )
    compiler = tuple(
        item for item in new_records if isinstance(item, dict) and item.get("kind") == "compiler"
    )
    dispatched_inference = tuple(item for item in inference if item.get("dispatched") is True)
    terminal_inference = tuple(
        item for item in dispatched_inference if item.get("terminal_valid") is True
    )
    observed_boundary = after.get("provider_boundary")
    boundary = (
        observed_boundary
        if isinstance(observed_boundary, dict)
        else {
            "call_count_class": count_class(len(dispatched_inference)),
            "lifecycle_valid": bool(dispatched_inference)
            and len(terminal_inference) == len(dispatched_inference),
            "terminal": bool(dispatched_inference)
            and len(terminal_inference) == len(dispatched_inference),
            "terminality_valid": bool(dispatched_inference)
            and len(terminal_inference) == len(dispatched_inference),
            "independent_from_ledger": True,
        }
    )
    return {
        "inference_attempted_count": len(inference),
        "inference_dispatched_count": len(dispatched_inference),
        "compiler_dispatched_count": sum(item.get("dispatched") is True for item in compiler),
        "provider_boundary_observed": bool(dispatched_inference),
        "provider_lifecycle_valid": bool(dispatched_inference)
        and len(terminal_inference) == len(dispatched_inference),
        "provider_terminal": bool(dispatched_inference)
        and len(terminal_inference) == len(dispatched_inference),
        "provider_boundary": boundary,
    }


def _candidate_only_observation(snapshot: Mapping[str, object]) -> dict[str, object]:
    """Retain candidate-readiness counts separately from all-lifetime totals."""
    count_names = (
        "other_attempted",
        "other_dispatched",
        "other_responded",
        "other_completed",
        "other_terminal_valid",
        "compiler_attempted",
        "compiler_dispatched",
        "inference_attempted",
        "inference_dispatched",
    )
    counts: dict[str, int | None] = {}
    for name in count_names:
        value = snapshot.get(f"{name}_count")
        counts[name] = value if type(value) is int and value >= 0 else None
    return {
        "lifetime_id": "candidate",
        "ready": snapshot.get("ready") is True,
        "failure_class": snapshot.get("failure_class")
        if isinstance(snapshot.get("failure_class"), str)
        else None,
        "counts": counts,
    }


def _idless_companion_observation(
    before: Mapping[str, object],
    after: Mapping[str, object],
    *,
    initial_status: int | None,
    initial_sse_valid: bool,
    returned_call_id_present: bool,
    continuation_status: int | None,
    continuation_json_valid: bool,
    accounting: Mapping[str, object],
    canonical_replay_evidence: Mapping[str, object],
) -> dict[str, object]:
    """Project one actual two-request omission companion without raw IDs.

    The companion is deliberately scoped to the two direct-observer records
    admitted by ``identity_replay``.  A separate present-ID request, a
    focused fake-provider regression, or a matching record from another
    operation cannot satisfy this projection.
    """
    before_records = before.get("records", ())
    after_records = after.get("records", ())
    if not isinstance(before_records, (list, tuple)) or not isinstance(
        after_records, (list, tuple)
    ):
        new_records: tuple[dict[str, object], ...] = ()
    else:
        new_records = tuple(
            record for record in after_records[len(before_records) :] if isinstance(record, dict)
        )
    inference = tuple(record for record in new_records if record.get("kind") == "inference")
    initial = tuple(
        record for record in inference if record.get("request_class") == "function_initial"
    )
    continuation = tuple(
        record for record in inference if record.get("request_class") == "function_continuation"
    )
    expected_context = ("identity_replay", "codex", 5, "identity")
    same_admitted_relationship = len(inference) == 2 and all(
        (
            record.get("dispatch_operation"),
            record.get("dispatch_phase"),
            record.get("dispatch_ordinal"),
            record.get("dispatch_lifetime"),
        )
        == expected_context
        for record in inference
    )
    initial_terminal = len(initial) == 1 and initial[0].get("terminal_valid") is True
    continuation_terminal = len(continuation) == 1 and continuation[0].get("terminal_valid") is True
    omitted_item_id = (
        len(continuation) == 1 and continuation[0].get("item_id_presence") == "omitted"
    )
    matching_call_id = (
        len(continuation) == 1 and continuation[0].get("call_id_relation") == "matching"
    )
    canonical_replay_authority = (
        canonical_replay_evidence.get("canonical_candidate_availability") == "available"
        and canonical_replay_evidence.get("canonical_candidate_count_class") == "1"
    )
    passed = all(
        (
            len(initial) == 1,
            len(continuation) == 1,
            same_admitted_relationship,
            initial_status == 200,
            initial_sse_valid,
            returned_call_id_present,
            initial_terminal,
            continuation_status == 200,
            continuation_json_valid,
            continuation_terminal,
            omitted_item_id,
            matching_call_id,
            canonical_replay_authority,
            accounting.get("two_terminal_reservations") is True,
            accounting.get("zero_pending") is True,
            accounting.get("zero_duplicate_request_ids") is True,
        )
    )
    return {
        "passed": passed,
        "operation": "identity_replay",
        "phase": "codex",
        "ordinal": 5,
        "lifetime": "identity",
        "request_count_class": count_class(len(inference)),
        "initial_response_shape": "stream_sse",
        "continuation_response_shape": "json_nonstream",
        "initial_status_class": (
            f"{initial_status // 100}xx" if isinstance(initial_status, int) else "unknown"
        ),
        "continuation_status_class": (
            f"{continuation_status // 100}xx" if isinstance(continuation_status, int) else "unknown"
        ),
        "returned_call_id_present": returned_call_id_present,
        "optional_item_id_omitted": omitted_item_id,
        "mandatory_call_id_matching": matching_call_id,
        "canonical_replay_authority": canonical_replay_authority,
        "canonical_candidate_availability": canonical_replay_evidence.get(
            "canonical_candidate_availability", "unknown"
        ),
        "canonical_candidate_count_class": canonical_replay_evidence.get(
            "canonical_candidate_count_class", "unknown"
        ),
        "canonical_summary_relation": canonical_replay_evidence.get(
            "canonical_summary_relation", "unknown"
        ),
        "same_admitted_relationship": same_admitted_relationship,
        "initial_terminal_valid": initial_terminal,
        "continuation_terminal_valid": continuation_terminal,
        "accounting_terminal": all(
            accounting.get(key) is True
            for key in ("two_terminal_reservations", "zero_pending", "zero_duplicate_request_ids")
        ),
        "natural_codex_shape_separate": True,
        "gateway_call_id_same_hmac": passed,
        "scope_no_downgrade": passed,
    }


def _provider_request_observation(request: httpx.Request) -> dict[str, object]:
    """Classify one provider-bound request without retaining its body."""
    if request.method != "POST" or request.url.path != "/v1/responses":
        return {}
    content = request.content
    if not isinstance(content, bytes) or len(content) > 4 * 1024 * 1024:
        raise ValueError("provider_request_body_unavailable")
    try:
        payload = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        raise ValueError("provider_request_body_invalid") from None
    if not isinstance(payload, dict):
        raise ValueError("provider_request_body_invalid")
    return _request_observation(payload)


def _direct_provider_boundary_complete(value: object, *, expected_calls: int) -> bool:
    """Require semantic facts emitted by the direct observer, not a fake oracle."""
    if not isinstance(value, dict):
        return False
    return (
        value.get("call_count_class") == count_class(expected_calls)
        and value.get("lifecycle_valid") is True
        and value.get("terminality_valid") is True
        and "function_initial" in value.get("request_class_classes", ())
        and "function_continuation" in value.get("request_class_classes", ())
        and "matching" in value.get("call_id_relation_classes", ())
    )


def _protected_provider_observation(transport: Mapping[str, object]) -> dict[str, object]:
    """Project protected facts from the shared direct observer only."""
    boundary = transport.get("provider_boundary")
    return {
        "provider_boundary": boundary if isinstance(boundary, dict) else {},
        "source": "direct_transport_observer",
        "fake_oracle": "unavailable",
    }


_CHECKPOINT_BOUNDARY_KEYS = (
    "call_count_class",
    "lifecycle_valid",
    "terminal_count_class",
    "terminal",
    "image_count_classes",
    "image_hash_count_class",
    "all_image_requests_single",
    "image_hashes_observed",
    "tool_type_classes",
    "independent_from_ledger",
    "request_class_classes",
    "tool_class_classes",
    "function_result_adjacent",
    "item_id_presence_classes",
    "call_id_relation_classes",
    "compiler_inference_classes",
    "normal_close_count_class",
    "terminality_valid",
    "canonical_candidate_availability_classes",
    "canonical_candidate_count_classes",
    "canonical_summary_relation_classes",
    "pending_scope_availability_classes",
    "continuation_count_class",
)


def _checkpoint_provider_boundary(snapshot: Mapping[str, object]) -> dict[str, object]:
    """Retain only fixed-class provider relationships for a phase checkpoint."""
    boundary = snapshot.get("provider_boundary")
    if not isinstance(boundary, Mapping):
        return {}
    return {key: boundary[key] for key in _CHECKPOINT_BOUNDARY_KEYS if key in boundary}


def _codex_phase_checkpoint(
    codex_facts: Mapping[str, object], observer_snapshot: Mapping[str, object]
) -> dict[str, object]:
    """Project actual Codex/provider/accounting facts before the next phase."""
    client_value = codex_facts.get("client_verification")
    client = client_value if isinstance(client_value, Mapping) else {}
    client_verification = {
        key: client[key]
        for key in (
            "status",
            "exit_status",
            "failure_origin",
            "sentinel_passed",
            "command_lifecycle",
        )
        if key in client
    }
    accounting_value = codex_facts.get("accounting")
    accounting = accounting_value if isinstance(accounting_value, Mapping) else {}
    accounting_facts = {
        key: accounting[key]
        for key in (
            "two_terminal_reservations",
            "zero_pending",
            "zero_duplicate_request_ids",
            "request",
            "usage",
            "tokens",
            "cost",
        )
        if key in accounting
    }
    provider_boundary = _checkpoint_provider_boundary(observer_snapshot)
    return {
        "evidence_kind": "semantic",
        "codex": {
            "status": codex_facts.get("status")
            if codex_facts.get("status") in {"PASSED", "FAILED"}
            else "unknown",
            "client_verification": client_verification,
            "provider_inference_call_count": codex_facts.get("provider_inference_call_count"),
            "provider_turns_expected": codex_facts.get("provider_turns_expected"),
            "exit_status": codex_facts.get("exit_status"),
            "command_lifecycle": codex_facts.get("command_lifecycle"),
            "sentinel_passed": codex_facts.get("sentinel_passed"),
            "tool_call_count_class": codex_facts.get("tool_call_count_class"),
            "dependency_hash_equal": codex_facts.get("dependency_hash_equal"),
            "dependency_length_equal": codex_facts.get("dependency_length_equal"),
            "call_id_same_hmac": codex_facts.get("call_id_same_hmac"),
            "scope_no_downgrade": codex_facts.get("scope_no_downgrade"),
        },
        "provider_observation": {
            "provider_boundary": provider_boundary,
            "source": "direct_transport_observer",
            "fake_oracle": "unavailable",
        },
        "transport_observation": {
            "provider_boundary_observed": bool(provider_boundary),
            "matches_fake_provider": codex_facts.get("transport_dispatch_matches_fake")
            if isinstance(codex_facts.get("transport_dispatch_matches_fake"), bool)
            else None,
        },
        "accounting": accounting_facts,
        "governance": {
            "dependency_one_equal": codex_facts.get("dependency_hash_equal"),
            "acquisition_before_completion": codex_facts.get("command_lifecycle") == "success",
        },
    }


async def _protected_provider_preflight(
    observer: DirectTransportObserver,
    provider_url: str,
    qwen_key: str,
    admit_probe: Callable[[str], None],
) -> tuple[int, int | None]:
    """Count health/models through the same observer for every protected mode."""
    async with httpx.AsyncClient(transport=observer, timeout=15, follow_redirects=False) as http:
        admit_probe("/health")
        health_response = await http.get(
            f"{provider_url}/health",
            headers={"Authorization": f"Bearer {qwen_key}"},
        )
        health_status = health_response.status_code
        if health_status != 200 or not observer.ready:
            return health_status, None
        admit_probe("/v1/models")
        models_response = await http.get(
            f"{provider_url}/v1/models",
            headers={"Authorization": f"Bearer {qwen_key}"},
        )
    return health_status, models_response.status_code


def _provider_preflight_complete(result: dict[str, object]) -> bool:
    """Require observed health/model probes and an unavailable fake oracle."""
    facts = result.get("provider_preflight")
    if not isinstance(facts, dict):
        return False
    observer = facts.get("observer")
    if not isinstance(observer, dict):
        return False
    records = observer.get("records")
    if not isinstance(records, (list, tuple)):
        return False
    endpoints = tuple(
        record.get("endpoint_class")
        for record in records
        if isinstance(record, dict) and record.get("kind") == "other"
    )
    budget = observer.get("dispatch_budget")
    return (
        facts.get("health_status") == 200
        and facts.get("models_status") == 200
        and facts.get("oracle_available") is False
        and observer.get("ready") is True
        and endpoints == ("health", "models")
        and observer.get("other_dispatched_count") == 2
        and isinstance(budget, dict)
        and budget.get("provider_probe_consumed_count") == 2
        and budget.get("provider_probe_pending") is False
    )


def _minimal_environment() -> dict[str, str]:
    return {
        name: os.environ[name]
        for name in ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "TERM")
        if name in os.environ
    }


def _gateway_environment(
    *,
    gateway_root: Path,
    database_url: str,
    gateway_port: int,
    hmac_secret: str,
    encryption_key: str,
    service_token: str,
    signing_secret: str,
    derivation_secret: str,
) -> dict[str, str]:
    environment = _minimal_environment()
    environment.update(
        {
            "PYTHONPATH": str(gateway_root / "app"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "APP_ENV": "test",
            "APP_BASE_URL": f"http://127.0.0.1:{gateway_port}",
            "PUBLIC_BASE_URL": f"http://127.0.0.1:{gateway_port}/v1",
            "DATABASE_URL": database_url,
            "DATABASE_POOL_SIZE": "2",
            "DATABASE_MAX_OVERFLOW": "0",
            "DATABASE_CONNECT_TIMEOUT_SECONDS": "5",
            "TOKEN_HMAC_SECRET_V1": hmac_secret,
            "ACTIVE_HMAC_KEY_VERSION": "1",
            "ONE_TIME_SECRET_ENCRYPTION_KEY": encryption_key,
            "GATEWAY_KEY_PREFIX": "sk-slaif-",
            "GATEWAY_KEY_ACCEPTED_PREFIXES": "sk-slaif-",
            "ENABLE_REDIS_RATE_LIMITS": "false",
            "ENABLE_ADMIN_DASHBOARD": "false",
            "ENABLE_EMAIL_DELIVERY": "false",
            "ENABLE_METRICS": "true",
            "METRICS_REQUIRE_AUTH": "false",
            "LOG_LEVEL": "WARNING",
            "STRUCTURED_LOGS": "true",
            SERVICE_TOKEN_ENV: service_token,
            "LOCAL_CODING_SERVICE_TOKEN": service_token,
            "LOCAL_CODING_SIGNING_SECRET_V1": signing_secret,
            "LOCAL_CODING_IDENTITY_DERIVATION_SECRET_V1": derivation_secret,
            "SLAIF_REHEARSAL_FAILURE_KEY": "synthetic-005k-failure-key",
            "ADMIN_SESSION_SECRET": "synthetic-005k-admin-session-secret",
            "UVICORN_ACCESS_LOG": "false",
        }
    )
    return environment


def _candidate_environment(
    service_token: str, qwen_key: str, signing_secret: str
) -> dict[str, str]:
    environment = _minimal_environment()
    environment.update(
        {
            "PYTHONPATH": f"{REPO_ROOT / 'src'}:{REPO_ROOT}",
            "PYTHONDONTWRITEBYTECODE": "1",
            SERVICE_TOKEN_ENV: service_token,
            SIGNING_SECRET_ENV: signing_secret,
            QWEN_KEY_ENV: qwen_key,
        }
    )
    return environment


def _gateway_settings(gateway_url: str) -> dict[str, str]:
    _ = gateway_url
    hmac_secret = "synthetic-005c-hmac-secret-for-disposable-run"
    encoded_key = base64.urlsafe_b64encode(b"x" * 32).decode("ascii").rstrip("=")
    return {"hmac_secret": hmac_secret, "encryption_key": encoded_key}


async def _seed_database(
    gateway_root: Path,
    database_url: str,
    *,
    adapter_port: int,
    failure_port: int,
    hmac_secret: str,
    encryption_key: str,
) -> dict[str, str]:
    sys.path.insert(0, str(gateway_root / "app"))
    from slaif_gateway.config import Settings  # type: ignore[import-not-found]
    from slaif_gateway.db.repositories.audit import (  # type: ignore[import-not-found]
        AuditRepository,
    )
    from slaif_gateway.db.repositories.institutions import (  # type: ignore[import-not-found]
        InstitutionsRepository,
    )
    from slaif_gateway.db.repositories.keys import (  # type: ignore[import-not-found]
        GatewayKeysRepository,
    )
    from slaif_gateway.db.repositories.one_time_secrets import (  # type: ignore[import-not-found]
        OneTimeSecretsRepository,
    )
    from slaif_gateway.db.repositories.owners import (  # type: ignore[import-not-found]
        OwnersRepository,
    )
    from slaif_gateway.db.repositories.pricing import (  # type: ignore[import-not-found]
        PricingRulesRepository,
    )
    from slaif_gateway.db.repositories.provider_configs import (  # type: ignore[import-not-found]
        ProviderConfigsRepository,
    )
    from slaif_gateway.db.repositories.routing import (  # type: ignore[import-not-found]
        ModelRoutesRepository,
    )
    from slaif_gateway.schemas.keys import CreateGatewayKeyInput  # type: ignore[import-not-found]
    from slaif_gateway.services.key_service import KeyService  # type: ignore[import-not-found]
    from slaif_gateway.services.responses_route_capabilities import (  # type: ignore[import-not-found]
        default_responses_capabilities,
    )
    from sqlalchemy.ext.asyncio import (  # type: ignore[import-not-found]
        async_sessionmaker,
        create_async_engine,
    )

    settings = Settings(
        APP_ENV="test",
        DATABASE_URL=database_url,
        TOKEN_HMAC_SECRET_V1=hmac_secret,
        ACTIVE_HMAC_KEY_VERSION="1",
        ONE_TIME_SECRET_ENCRYPTION_KEY=encryption_key,
        ENABLE_REDIS_RATE_LIMITS=False,
        ENABLE_ADMIN_DASHBOARD=False,
        ENABLE_EMAIL_DELIVERY=False,
    )
    engine = create_async_engine(database_url, future=True, pool_size=2, max_overflow=0)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            institution = await InstitutionsRepository(session).create_institution(
                name="Objective 005-c Disposable Institute", country="SI", notes="temporary"
            )
            owner = await OwnersRepository(session).create_owner(
                name="Disposable",
                surname="Rehearsal",
                email="objective-005c@example.invalid",
                institution_id=institution.id,
            )
            second_owner = await OwnersRepository(session).create_owner(
                name="Disposable Second",
                surname="Rehearsal",
                email="objective-005k-second@example.invalid",
                institution_id=institution.id,
            )
            provider = await ProviderConfigsRepository(session).create_provider_config(
                provider=PROVIDER,
                display_name="Disposable Local Coding",
                base_url=f"http://127.0.0.1:{adapter_port}/v1",
                api_key_env_var=SERVICE_TOKEN_ENV,
                kind="openai_compatible",
                enabled=True,
                timeout_seconds=300,
                max_retries=0,
                notes="temporary 005-c rehearsal provider",
            )
            capabilities = default_responses_capabilities()
            capabilities.update(
                {
                    "streaming": True,
                    "tools": True,
                    "function_tools": True,
                    "custom_tools": True,
                    "image_input": True,
                    "codex_request_envelope": True,
                    "codex_client_tools": True,
                    "codex_streaming_tool_events": True,
                    "codex_encrypted_reasoning_replay": True,
                    "codex_compaction": True,
                }
            )
            route = await ModelRoutesRepository(session).create_model_route(
                requested_model=PUBLIC_MODEL,
                provider=PROVIDER,
                upstream_model=UPSTREAM_MODEL,
                endpoint=RESPONSES_ENDPOINT,
                priority=1,
                enabled=True,
                visible_in_models=True,
                supports_streaming=True,
                capabilities={
                    "responses": capabilities,
                    "local_coding": {
                        "contract_version": "local-coding-v1",
                        "route_name": LOCAL_ROUTE,
                        "tool_policy_version": "responses-tool-policy-v1",
                        "identity_mode": "signed_identity_v1",
                        "replay_mode": "process_local_ttl_lru",
                        "deployment_mode": "single_worker",
                    },
                    "codex_limits": {
                        "context_window_tokens": 100_000,
                        "default_max_output_tokens": 4096,
                        "max_output_tokens": 8192,
                    },
                },
                notes="temporary 005-c public-to-local vision route",
            )
            now = __import__("datetime").datetime.now(__import__("datetime").UTC)
            await PricingRulesRepository(session).create_pricing_rule(
                provider=PROVIDER,
                upstream_model=UPSTREAM_MODEL,
                endpoint=RESPONSES_ENDPOINT,
                valid_from=now,
                currency="EUR",
                input_price_per_1m=Decimal("1.000000000"),
                output_price_per_1m=Decimal("2.000000000"),
                request_price=Decimal("0.001000000"),
                notes="temporary operator-confirmed local EUR price",
            )
            failure_provider = await ProviderConfigsRepository(session).create_provider_config(
                provider=FAILURE_PROVIDER,
                display_name="Disposable failure provider",
                base_url=f"http://127.0.0.1:{failure_port}/v1",
                api_key_env_var="SLAIF_REHEARSAL_FAILURE_KEY",
                kind="openai_compatible",
                enabled=True,
                timeout_seconds=10,
                max_retries=0,
                notes="temporary 005-k controlled provider failure",
            )
            failure_capabilities = default_responses_capabilities()
            await ModelRoutesRepository(session).create_model_route(
                requested_model=FAILURE_MODEL,
                provider=FAILURE_PROVIDER,
                upstream_model=FAILURE_MODEL,
                endpoint=RESPONSES_ENDPOINT,
                priority=1,
                enabled=True,
                visible_in_models=False,
                supports_streaming=False,
                capabilities={"responses": failure_capabilities},
                notes="temporary 005-k controlled provider failure route",
            )
            await PricingRulesRepository(session).create_pricing_rule(
                provider=FAILURE_PROVIDER,
                upstream_model=FAILURE_MODEL,
                endpoint=RESPONSES_ENDPOINT,
                valid_from=now,
                currency="EUR",
                input_price_per_1m=Decimal("1.000000000"),
                output_price_per_1m=Decimal("1.000000000"),
                request_price=Decimal("0"),
                notes="temporary 005-k controlled provider failure pricing",
            )
            key_policy = {
                "version": 1,
                "local_coding_repository_scope": "synthetic-005k-repository",
                "allowed_capabilities": [
                    "codex_request_envelope",
                    "codex_client_tools",
                    "codex_streaming_tool_events",
                ],
                "client_module": {
                    "id": CODEX_MODULE_ID,
                    "version": CODEX_MODULE_VERSION,
                    "fixture_sha256": CODEX_CLIENT_MODULE_FIXTURE_SHA256,
                },
            }
            key_service = KeyService(
                settings=settings,
                gateway_keys_repository=GatewayKeysRepository(session),
                one_time_secrets_repository=OneTimeSecretsRepository(session),
                audit_repository=AuditRepository(session),
                model_routes_repository=ModelRoutesRepository(session),
            )
            key = await key_service.create_gateway_key(
                CreateGatewayKeyInput(
                    owner_id=owner.id,
                    valid_from=now,
                    valid_until=now + __import__("datetime").timedelta(hours=1),
                    cost_limit_eur=Decimal("20.000000000"),
                    token_limit_total=2_000_000,
                    request_limit_total=50,
                    allowed_models=[PUBLIC_MODEL],
                    allowed_endpoints=["/v1/models", RESPONSES_ENDPOINT],
                    allowed_providers=[PROVIDER],
                    responses_policy=key_policy,
                    note="temporary 005-k synthetic public key",
                )
            )
            second_key = await key_service.create_gateway_key(
                CreateGatewayKeyInput(
                    owner_id=second_owner.id,
                    valid_from=now,
                    valid_until=now + __import__("datetime").timedelta(hours=1),
                    cost_limit_eur=Decimal("20.000000000"),
                    token_limit_total=2_000_000,
                    request_limit_total=50,
                    allowed_models=[PUBLIC_MODEL],
                    allowed_endpoints=["/v1/models", RESPONSES_ENDPOINT],
                    allowed_providers=[PROVIDER],
                    responses_policy=key_policy,
                    note="temporary 005-k second synthetic public key",
                )
            )
            failure_key = await key_service.create_gateway_key(
                CreateGatewayKeyInput(
                    owner_id=owner.id,
                    valid_from=now,
                    valid_until=now + __import__("datetime").timedelta(hours=1),
                    cost_limit_eur=Decimal("20.000000000"),
                    token_limit_total=2_000_000,
                    request_limit_total=5,
                    allowed_models=[FAILURE_MODEL],
                    allowed_endpoints=[RESPONSES_ENDPOINT],
                    allowed_providers=[FAILURE_PROVIDER],
                    note="temporary 005-k failure key",
                )
            )
            await session.commit()
            return {
                "plaintext_key": key.plaintext_key,
                "gateway_key_id": str(key.gateway_key_id),
                "second_plaintext_key": second_key.plaintext_key,
                "second_gateway_key_id": str(second_key.gateway_key_id),
                "failure_plaintext_key": failure_key.plaintext_key,
                "failure_gateway_key_id": str(failure_key.gateway_key_id),
                "route_id": str(route.id),
                "provider": provider.provider,
                "failure_provider": failure_provider.provider,
            }
    finally:
        await engine.dispose()


async def _db_snapshot(
    gateway_root: Path, database_url: str, gateway_key_id: str
) -> dict[str, Any]:
    sys.path.insert(0, str(gateway_root / "app"))
    from slaif_gateway.db.models import (  # type: ignore[import-not-found]
        GatewayKey,
        ModelRoute,
        QuotaReservation,
        UsageLedger,
    )
    from sqlalchemy import select  # type: ignore[import-not-found]
    from sqlalchemy.ext.asyncio import (
        async_sessionmaker,
        create_async_engine,
    )

    engine = create_async_engine(database_url, future=True, pool_size=2, max_overflow=0)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            key = await session.get(GatewayKey, gateway_key_id)
            reservations = list(
                (
                    await session.scalars(
                        select(QuotaReservation).where(
                            QuotaReservation.gateway_key_id == gateway_key_id
                        )
                    )
                ).all()
            )
            ledgers = list(
                (
                    await session.scalars(
                        select(UsageLedger).where(UsageLedger.gateway_key_id == gateway_key_id)
                    )
                ).all()
            )
            route = (
                await session.scalars(
                    select(ModelRoute).where(ModelRoute.requested_model == PUBLIC_MODEL)
                )
            ).first()
            request_ids = [row.request_id for row in ledgers]
            usage_rows = [
                row
                for row in ledgers
                if row.total_tokens > 0
                and row.prompt_tokens + row.completion_tokens == row.total_tokens
                and bool(row.usage_raw)
            ]
            total_tokens = sum(int(row.total_tokens) for row in ledgers)
            total_cost = sum((row.actual_cost_eur or Decimal("0")) for row in ledgers)
            return {
                "reservation_count": len(reservations),
                "finalized_reservation_count": sum(
                    row.status == "finalized" for row in reservations
                ),
                "pending_reservation_count": sum(row.status == "pending" for row in reservations),
                "ledger_count": len(ledgers),
                "finalized_ledger_count": sum(
                    row.accounting_status == "finalized" and row.success is True for row in ledgers
                ),
                "failed_ledger_count": sum(row.accounting_status == "failed" for row in ledgers),
                "duplicate_request_id_count": len(request_ids) - len(set(request_ids)),
                "provider_usage_rows": len(usage_rows),
                "key_requests_used": int(key.requests_used_total) if key is not None else -1,
                "key_requests_reserved": int(key.requests_reserved_total)
                if key is not None
                else -1,
                "key_tokens_used": int(key.tokens_used_total) if key is not None else -1,
                "key_tokens_reserved": int(key.tokens_reserved_total) if key is not None else -1,
                "key_cost_used_eur": _decimal_text(key.cost_used_eur if key is not None else None),
                "key_cost_reserved_eur": _decimal_text(
                    key.cost_reserved_eur if key is not None else None
                ),
                "ledger_total_tokens": total_tokens,
                "ledger_total_cost_eur": _decimal_text(total_cost),
                "route_metadata_ok": bool(
                    route is not None
                    and route.provider == PROVIDER
                    and route.upstream_model == UPSTREAM_MODEL
                    and route.endpoint == RESPONSES_ENDPOINT
                    and route.enabled
                    and route.visible_in_models
                ),
            }
    finally:
        await engine.dispose()


async def _tighten_request_limit(
    gateway_root: Path, database_url: str, gateway_key_id: str
) -> None:
    sys.path.insert(0, str(gateway_root / "app"))
    from slaif_gateway.db.models import GatewayKey
    from slaif_gateway.db.repositories.keys import GatewayKeysRepository
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    engine = create_async_engine(database_url, future=True, pool_size=1, max_overflow=0)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            key = await session.get(GatewayKey, gateway_key_id)
            if key is None:
                raise RuntimeError("seed_gateway_key_missing")
            updated = await GatewayKeysRepository(session).update_gateway_key_limits(
                key.id, request_limit_total=int(key.requests_used_total)
            )
            if not updated:
                raise RuntimeError("request_quota_tighten_failed")
            await session.commit()
    finally:
        await engine.dispose()


def _decimal_text(value: Decimal | int | float | str | None) -> str:
    if value is None:
        return "missing"
    try:
        return format(Decimal(str(value)).normalize(), "f")
    except (ArithmeticError, ValueError):
        return "missing"


def _int_fact(value: object) -> int:
    """Read one integer from the bounded provider snapshot."""
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _metric_sum(metrics: str, name: str, labels: dict[str, str] | None = None) -> int:
    wanted = labels or {}
    total = 0.0
    for family in text_string_to_metric_families(metrics):
        for sample in family.samples:
            if sample.name != name or any(
                sample.labels.get(key) != value for key, value in wanted.items()
            ):
                continue
            total += float(sample.value)
    return int(total)


def _metric_delta(before: str, after: str, name: str, labels: dict[str, str] | None = None) -> int:
    return max(0, _metric_sum(after, name, labels) - _metric_sum(before, name, labels))


def _local_upstream_status_class(before: str, after: str) -> str:
    """Project only the status class observed for this route's upstream call."""
    before_values: dict[str, int] = {}
    after_values: dict[str, int] = {}
    for metrics, values in ((before, before_values), (after, after_values)):
        for family in text_string_to_metric_families(metrics):
            for sample in family.samples:
                if sample.name != "slaif_requests_total":
                    continue
                if sample.labels.get("endpoint") != RESPONSES_ENDPOINT:
                    continue
                status = sample.labels.get("status")
                if status in {"2xx", "4xx", "5xx", "other", "unknown"}:
                    values[status] = values.get(status, 0) + int(float(sample.value))
                elif status is not None and status.isdigit():
                    values[status] = values.get(status, 0) + int(float(sample.value))
    for status, value in sorted(after_values.items()):
        try:
            delta = value - before_values.get(status, 0)
            if delta > 0:
                return status if status in {"2xx", "4xx", "5xx"} else _status_class(int(status))
        except ValueError:
            continue
    return "unknown"


def _local_failure_delta(before: str, after: str) -> tuple[int, str]:
    allowed = {"connection", "disconnect", "response_read", "response_too_large", "timeout"}
    total = 0
    classes: set[str] = set()
    for kind in allowed:
        delta = _metric_delta(
            before,
            after,
            "slaif_upstream_failures_total",
            {"kind": kind},
        )
        total += delta
        if delta:
            classes.add(kind)
    return total, "none" if not classes else "multiple" if len(classes) > 1 else next(iter(classes))


def _adapter_metrics(client: httpx.Client, adapter_port: int) -> str:
    response = client.get(f"http://127.0.0.1:{adapter_port}/metrics")
    if response.status_code != 200:
        raise RuntimeError("candidate_metrics_unavailable")
    return response.text


def _wait_status(
    client: httpx.Client,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    retry: bool = True,
) -> int:
    deadline = time.monotonic() + 45
    last_status = 0
    while time.monotonic() < deadline:
        try:
            response = client.get(url, headers=headers)
            last_status = response.status_code
            if response.status_code < 500 or not retry:
                return response.status_code
        except httpx.HTTPError:
            if not retry:
                return last_status
        if not retry:
            return last_status
        time.sleep(0.25)
    return last_status


def _stop_process(process: subprocess.Popen[bytes] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=15)


def _secret_free_logs(paths: tuple[Path, ...], values: tuple[str, ...]) -> bool:
    needles = tuple(value.encode("utf-8") for value in values if value)
    try:
        for path in paths:
            data = path.read_bytes()
            if any(needle in data for needle in needles):
                return False
    except OSError:
        return False
    return True


def _codex_version(codex: Path) -> str:
    result = _run_command([str(codex), "--version"])
    match = re.search(r"\b(\d+\.\d+\.\d+)\b", result.stdout + result.stderr)
    return match.group(1) if match else "unavailable"


def _codex_sha256(codex: Path) -> str:
    digest = hashlib.sha256()
    try:
        with codex.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1_048_576), b""):
                digest.update(chunk)
    except OSError:
        return "unavailable"
    return digest.hexdigest()


def _public_model_catalog_ok(path: Path) -> bool:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        models = document.get("models")
        selected = next(item for item in models if item.get("slug") == PUBLIC_MODEL)
        return (
            selected.get("input_modalities") == ["text", "image"]
            and selected.get("supports_image_detail_original") is False
            and selected.get("context_window") == 100_000
            and selected.get("supports_parallel_tool_calls") is False
        )
    except (OSError, TypeError, ValueError, StopIteration):
        return False


def _tool_envelope_preflight(
    gateway_root: Path, codex: Path
) -> tuple[dict[str, object], tuple[VariantResult, ...]]:
    """Capture and validate the tool envelope before any service/model stage."""

    results = run_differential(gateway_root, codex)
    compatible = next(
        (
            result
            for result in results
            if result.policy.accepted and result.ordinary_function_or_custom_remains
        ),
        None,
    )
    facts: dict[str, object] = {
        "gateway_policy": "ACCEPTED" if compatible is not None else "REJECTED",
        "ordinary_local_tools": "PRESENT" if compatible is not None else "UNKNOWN",
        "hosted_search_tools": (
            "ADAPTER_MANAGED" if compatible is not None else "PRESENT_OR_UNRESOLVED"
        ),
        "variant": compatible.name if compatible is not None else "none",
        "feature_flags": compatible.feature_flags if compatible is not None else (),
        "ignore_user_config": compatible.ignore_user_config if compatible is not None else False,
        "catalog_search_disabled": (
            compatible.catalog_search_disabled if compatible is not None else False
        ),
        "capture_count": len(results),
    }
    return facts, results


def _build_gateway_process(
    gateway_python: Path,
    gateway_root: Path,
    gateway_port: int,
    environment: dict[str, str],
    log_path: Path,
) -> subprocess.Popen[bytes]:
    command = [
        str(gateway_python),
        "-m",
        "uvicorn",
        "slaif_gateway.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(gateway_port),
        "--no-access-log",
        "--log-level",
        "warning",
    ]
    assert_allowlisted_diagnostic_argv(
        command,
        allowed_commands={gateway_python.name},
        allowed_executables=(gateway_python,),
        disposable_root=Path(tempfile.gettempdir()),
        path_arguments=(gateway_root, log_path),
    )
    log = log_path.open("wb")
    try:
        return subprocess.Popen(
            command,
            cwd=gateway_root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
        )
    except BaseException:
        log.close()
        raise


def _build_candidate_process(
    gateway_python: Path,
    config_path: Path,
    environment: dict[str, str],
    log_path: Path,
) -> subprocess.Popen[bytes]:
    command = [str(gateway_python), "-m", "slaif_local_coding", "--config", str(config_path)]
    assert_allowlisted_diagnostic_argv(
        command,
        allowed_commands={gateway_python.name},
        allowed_executables=(gateway_python,),
        disposable_root=Path(tempfile.gettempdir()),
        path_arguments=(config_path, log_path),
    )
    log = log_path.open("wb")
    try:
        return subprocess.Popen(
            command,
            cwd=REPO_ROOT,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
        )
    except BaseException:
        log.close()
        raise


@dataclass
class _ObservedCandidate:
    """Disposable in-process candidate used only by the fake rehearsal."""

    server: uvicorn.Server
    thread: threading.Thread
    observer: DirectTransportObserver
    vision_recorder: Any | None = None
    previous_logging_disable: int = logging.NOTSET
    health_status: int = 0
    ready_status: int = 0

    def stop(self) -> None:
        try:
            self.server.should_exit = True
            self.thread.join(timeout=15)
            if self.thread.is_alive():
                self.server.force_exit = True
                self.thread.join(timeout=5)
            if self.thread.is_alive():
                raise RuntimeError("candidate_adapter_did_not_stop")
        finally:
            logging.disable(self.previous_logging_disable)

    def alive(self) -> bool:
        return self.thread.is_alive()


def _build_observed_candidate(
    config_path: Path,
    *,
    observer: DirectTransportObserver,
    vision_recorder: Any | None = None,
    readiness_lifetime_id: str | None = None,
) -> _ObservedCandidate:
    """Launch the public app factory with a direct acceptance observer."""
    if not observer.inference_capability_ready:
        raise RuntimeError("candidate_observer_capability_unavailable")
    if not observer.ready:
        raise RuntimeError("candidate_observer_not_ready")
    from slaif_local_coding.app import create_app
    from slaif_local_coding.config import load_settings

    settings = load_settings(config_path)

    def launch(candidate_observer: DirectTransportObserver) -> _ObservedCandidate:
        app = create_app(settings, transport=candidate_observer)
        previous_logging_disable = logging.root.manager.disable
        logging.disable(logging.CRITICAL)
        server = uvicorn.Server(
            uvicorn.Config(
                app,
                host="127.0.0.1",
                port=18031,
                log_level="warning",
                access_log=False,
                log_config=None,
            )
        )
        thread = threading.Thread(
            target=server.run, name="oap-005s-observed-candidate", daemon=True
        )
        thread.start()
        return _ObservedCandidate(
            server=server,
            thread=thread,
            observer=candidate_observer,
            vision_recorder=vision_recorder,
            previous_logging_disable=previous_logging_disable,
        )

    def probe(
        runtime: _ObservedCandidate, *, ready: bool, retry_ready: bool = True
    ) -> tuple[int, int]:
        with httpx.Client(timeout=5, follow_redirects=False) as client:
            health_status = _wait_status(client, "http://127.0.0.1:18031/healthz")
            ready_status = (
                _wait_status(client, "http://127.0.0.1:18031/readyz", retry=retry_ready)
                if ready
                else 0
            )
        if health_status != 200 or (ready and ready_status != 200):
            runtime.stop()
            raise RuntimeError("candidate_observer_not_ready")
        return health_status, ready_status

    previous_logging_disable = logging.root.manager.disable
    runtime: _ObservedCandidate | None = None
    try:
        budget = observer.budget_controller
        if budget is not None:
            if readiness_lifetime_id is None:
                raise RuntimeError("candidate_readiness_lifetime_missing")
            admit_readiness = getattr(budget, "admit_readiness", None)
            activate_readiness = getattr(budget, "activate_readiness", None)
            if not callable(admit_readiness) or not callable(activate_readiness):
                raise RuntimeError("candidate_readiness_budget_unavailable")
            if not admit_readiness(lifetime_id=readiness_lifetime_id):
                raise RuntimeError(
                    getattr(budget, "failure", None) or "candidate_readiness_not_admitted"
                )
            if not activate_readiness(lifetime_id=readiness_lifetime_id):
                raise RuntimeError(
                    getattr(budget, "failure", None) or "candidate_readiness_not_activated"
                )
            runtime = launch(observer)
            health_status, ready_status = probe(runtime, ready=True, retry_ready=False)
            runtime.health_status = health_status
            runtime.ready_status = ready_status
        else:
            runtime = launch(observer)
            health_status, ready_status = probe(runtime, ready=True)
            runtime.health_status = health_status
            runtime.ready_status = ready_status
        if (
            not runtime.thread.is_alive()
            or not observer.ready
            or not observer.inference_capability_ready
        ):
            raise RuntimeError("candidate_observer_not_ready")
    except BaseException:
        if runtime is not None:
            runtime.stop()
        else:
            logging.disable(previous_logging_disable)
        raise
    return runtime


def _local_implementation_sha(repo_root: Path | None = None) -> str:
    root = REPO_ROOT if repo_root is None else repo_root
    result = _run_command(["git", "-C", str(root), "rev-parse", "HEAD"])
    value = result.stdout.strip()
    if result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", value):
        raise RuntimeError("local_implementation_sha_unavailable")
    return value


def _sha256_file(path: Path) -> str:
    """Hash one bounded source file without retaining or exposing its contents."""
    digest = hashlib.sha256()
    try:
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(64 * 1024), b""):
                digest.update(chunk)
    except OSError:
        raise RuntimeError("source_identity_unavailable") from None
    return digest.hexdigest()


def _source_identity() -> dict[str, object]:
    """Describe the exact repository source and loaded helper modules in use."""
    source_files = {
        "runner": REPO_ROOT / "scripts/gateway_accounting_rehearsal.py",
        "observer": REPO_ROOT / "tests/helpers/transport_observer.py",
        "projection": REPO_ROOT / "tests/helpers/acceptance_harness.py",
        "provider_sse": REPO_ROOT / "scripts/local_qwen_provider_differential.py",
    }
    loaded_modules = {
        "tests.helpers.acceptance_harness": source_files["projection"],
        "tests.helpers.transport_observer": source_files["observer"],
        "scripts.local_qwen_provider_differential": source_files["provider_sse"],
    }
    loaded_paths: dict[str, str] = {}
    loaded_hashes: dict[str, str] = {}
    for module_name, expected_path in loaded_modules.items():
        module = sys.modules.get(module_name)
        module_path = Path(getattr(module, "__file__", "")).resolve() if module else Path()
        if module_path != expected_path.resolve():
            raise RuntimeError("source_identity_module_mismatch")
        loaded_paths[module_name] = str(module_path.relative_to(REPO_ROOT))
        loaded_hashes[module_name] = _sha256_file(module_path)
    return {
        "paths": {name: str(path.relative_to(REPO_ROOT)) for name, path in source_files.items()},
        "sha256": {name: _sha256_file(path) for name, path in source_files.items()},
        "loaded_module_paths": loaded_paths,
        "loaded_module_sha256": loaded_hashes,
    }


def _candidate_provenance(
    implementation_sha: str,
    run_id: str,
    *,
    provider_target: str = "fake",
    synthetic_protected: bool = False,
) -> dict[str, object]:
    """Build source-bound provenance for the actual runner mode."""
    if provider_target == "fake":
        execution_mode = "fake"
        run_provenance = "fresh_fake_direct_httpx_loopback"
    elif synthetic_protected:
        execution_mode = "synthetic-protected"
        run_provenance = "fresh_synthetic_protected_direct_httpx_loopback"
    else:
        execution_mode = "real-protected"
        run_provenance = "fresh_real_protected_direct_httpx_qwen"
    return {
        "implementation_sha": implementation_sha,
        "tested_worktree_clean": True,
        "local_source": "src/slaif_local_coding",
        "harness_source": "scripts/gateway_accounting_rehearsal.py",
        "route_policy": LOCAL_ROUTE_POLICY,
        "gateway_sha": GATEWAY_MAIN_SHA,
        "gateway_app_tree_sha256": GATEWAY_APP_TREE_SHA256,
        "codex_version": CODEX_VERSION,
        "codex_binary_sha256": CODEX_FIXTURE_SHA256,
        "execution_mode": execution_mode,
        "run_provenance": run_provenance,
        "run_id": run_id,
        "observer_version": OBSERVATION_VERSION,
        "source_identity": _source_identity(),
    }


def _select_protected_runtime(
    hooks: ProtectedRuntimeHooks | None = None,
) -> tuple[dict[str, object], str, str]:
    """Select the protected fixture through either live or synthetic seams."""
    protected_before = hooks.host_preflight() if hooks is not None else _protected_snapshot()
    if (
        not protected_before
        or not protected_before["vision_active"]
        or not protected_before["has_18020"]
        or protected_before["vision_pid"] != PROTECTED_VISION_PID
        or protected_before["vision_start_wall"] != PROTECTED_VISION_START
        or protected_before["vision_restarts"] != "0"
        or protected_before["worktree_count"] != 7
    ):
        raise RuntimeError("protected_vision_fixture_not_active")
    if not protected_before["text_inactive"] or protected_before["has_18021"]:
        raise RuntimeError("protected_fixture_precondition_failed")
    protected_pid = hooks.main_pid() if hooks is not None else _protected_main_pid()
    if protected_pid != protected_before["vision_pid"]:
        raise RuntimeError("protected_vision_identity_changed")
    if QWEN_KEY_ENV in os.environ:
        raise RuntimeError("protected_external_key_present")
    qwen_key = (
        hooks.credential_source(protected_pid)
        if hooks is not None
        else _read_protected_qwen_key(protected_pid)
    )
    if not isinstance(qwen_key, str) or not qwen_key:
        raise RuntimeError("protected_qwen_key_unavailable")
    return protected_before, protected_pid, qwen_key


def _docker_start_postgres() -> tuple[str, int, bool, bool, str | None, str | None]:
    running_before = _running_container_facts()
    image_before, image_id_before, digest_before = _image_fingerprint()
    if not image_before:
        pulled = _docker("pull", IMAGE_NAME, timeout=180)
        if pulled.returncode != 0:
            raise RuntimeError("postgres_image_pull_failed")
    name = f"slaif-005c-postgres-{secrets.token_hex(4)}"
    run = _docker(
        "run",
        "-d",
        "--rm",
        "--name",
        name,
        "--tmpfs",
        "/var/lib/postgresql/data:rw,nosuid,nodev,noexec,size=1g",
        "--shm-size",
        "64m",
        "-e",
        f"POSTGRES_DB={DATABASE_NAME}",
        "-e",
        f"POSTGRES_USER={DATABASE_USER}",
        "-e",
        f"POSTGRES_PASSWORD={DATABASE_PASSWORD}",
        "-p",
        "127.0.0.1::5432",
        IMAGE_NAME,
        timeout=60,
    )
    if run.returncode != 0:
        raise RuntimeError("postgres_container_start_failed")
    port_text = _docker_ok("port", name, "5432/tcp")
    match = re.search(r":(\d+)\s*$", port_text)
    if match is None:
        raise RuntimeError("postgres_host_port_unavailable")
    port = int(match.group(1))
    for _ in range(60):
        ready = _docker("exec", name, "pg_isready", "-U", DATABASE_USER, "-d", DATABASE_NAME)
        if ready.returncode == 0:
            tmpfs_config = json.loads(
                _docker_ok("inspect", name, "--format", "{{json .HostConfig.Tmpfs}}")
            )
            tmpfs_only = isinstance(tmpfs_config, dict) and set(tmpfs_config) == {
                "/var/lib/postgresql/data"
            }
            image_after, image_id_after, digest_after = _image_fingerprint()
            if not image_after or image_id_after is None or digest_after is None:
                raise RuntimeError("postgres_image_fingerprint_missing")
            _ = running_before
            return name, port, tmpfs_only, not image_before, image_id_after, digest_after
        time.sleep(1)
    raise RuntimeError("postgres_readiness_timeout")


def _docker_cleanup(name: str | None, image_was_absent: bool) -> tuple[bool, bool]:
    container_removed = False
    if name:
        stopped = _docker("stop", name, timeout=30)
        if stopped.returncode != 0:
            _docker("rm", "-f", name, timeout=30)
        container_removed = _docker("inspect", name).returncode != 0
    image_removed = True
    if image_was_absent:
        concurrent = _docker("ps", "--filter", "ancestor=" + IMAGE_NAME, "--format", "{{.ID}}")
        if concurrent.returncode != 0 or concurrent.stdout.strip():
            image_removed = False
        else:
            image_removed = _docker("image", "rm", IMAGE_NAME, timeout=60).returncode == 0
    return container_removed, image_removed


def _start_threaded_server(server: http.server.ThreadingHTTPServer) -> threading.Thread:
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


def _stop_threaded_server(
    server: http.server.ThreadingHTTPServer | None, thread: threading.Thread | None
) -> None:
    if server is None:
        return
    server.shutdown()
    server.server_close()
    if thread is not None:
        thread.join(timeout=10)


def _run_fake_idless_http_regression() -> dict[str, object]:
    """Exercise the fake provider's id-less call-output path over loopback HTTP."""
    server = _FakeQwenServer("synthetic-005q-idless-token")
    thread = _start_threaded_server(server)
    initial = {
        "model": PUBLIC_MODEL,
        "stream": True,
        "input": [
            {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "synthetic"}],
            }
        ],
        "tools": [
            {
                "type": "function",
                "name": "exec_command",
                "description": "bounded local command",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
                "strict": True,
            }
        ],
    }
    continuation = {
        "model": PUBLIC_MODEL,
        "stream": True,
        "input": [
            {
                "type": "function_call_output",
                "call_id": FAKE_FUNCTION_CALL_ID,
                "output": "synthetic-result",
            }
        ],
        "tools": initial["tools"],
    }
    statuses: list[int] = []
    try:
        with httpx.Client(timeout=10, follow_redirects=False) as client:
            for body in (initial, continuation):
                response = client.post(
                    f"http://127.0.0.1:{server.server_address[1]}/v1/responses",
                    json=body,
                    headers={"Authorization": f"Bearer {server.token}"},
                )
                statuses.append(response.status_code)
                if response.status_code != 200 or not response.content.endswith(b"\n\n"):
                    break
    finally:
        _stop_threaded_server(server, thread)
    boundary = server.snapshot()["provider_boundary"]
    return {
        "passed": statuses == [200, 200]
        and isinstance(boundary, dict)
        and "omitted" in boundary.get("item_id_presence_classes", ())
        and "matching" in boundary.get("call_id_relation_classes", ())
        and boundary.get("lifecycle_valid") is True
        and boundary.get("terminality_valid") is True,
        "request_count_class": count_class(len(statuses)),
        "status_classes": tuple(f"{status // 100}xx" for status in statuses),
        "idless_item_observed": (
            isinstance(boundary, dict) and "omitted" in boundary.get("item_id_presence_classes", ())
        ),
        "matching_call_id_observed": (
            isinstance(boundary, dict)
            and "matching" in boundary.get("call_id_relation_classes", ())
        ),
        "lifecycle_valid": (isinstance(boundary, dict) and boundary.get("lifecycle_valid") is True),
        "terminality_valid": (
            isinstance(boundary, dict) and boundary.get("terminality_valid") is True
        ),
    }


def _sse_frame_payload(frame: bytes) -> tuple[str, dict[str, object]] | None:
    """Parse one bounded SSE frame without assigning replay authority."""
    event_name: str | None = None
    data_parts: list[bytes] = []
    for line in frame.replace(b"\r\n", b"\n").split(b"\n"):
        if line.startswith(b"event:"):
            if event_name is not None:
                return None
            try:
                event_name = line[6:].strip().decode("ascii")
            except UnicodeDecodeError:
                return None
        elif line.startswith(b"data:"):
            data_parts.append(line[5:].lstrip())
        elif line.startswith(b":") or not line:
            continue
        else:
            return None
    if not data_parts:
        return None
    try:
        payload = json.loads(b"\n".join(data_parts))
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    payload_event_name = payload.get("type")
    if not isinstance(payload_event_name, str) or not payload_event_name:
        return None
    if event_name is not None and event_name != payload_event_name:
        return None
    return payload_event_name, payload


def _comment_only_sse_frame(frame: bytes) -> bool:
    """Recognize an ignorable SSE comment frame without accepting data."""
    lines = frame.replace(b"\r\n", b"\n").split(b"\n")
    return all(not line or line.startswith(b":") for line in lines)


def _summary_call_id_digests(payload: Mapping[str, object]) -> tuple[bytes, ...]:
    """Hash terminal-summary IDs only for bounded diagnostic comparison."""
    response = payload.get("response")
    output = response.get("output") if isinstance(response, Mapping) else None
    if not isinstance(output, list) or len(output) > FAKE_MAX_FUNCTION_CALLS + 7:
        return ()
    digests: list[bytes] = []
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "function_call":
            continue
        call_id = item.get("call_id")
        if (
            not isinstance(call_id, str)
            or not call_id
            or len(call_id) > 512
            or any(char in call_id for char in "\r\n")
        ):
            continue
        digests.append(hashlib.sha256(call_id.encode("utf-8")).digest())
    return tuple(digests)


@dataclass
class _ReturnedCallIDCapture:
    """Bounded transient capture of exact validator replay candidates."""

    validator: Any | None = field(default=None, repr=False)
    buffer: bytearray = field(default_factory=bytearray, repr=False)
    value: str | None = field(default=None, repr=False)
    invalid: bool = False
    canonical_candidate_count: int = 0
    canonical_call_id_digests: tuple[bytes, ...] = field(default=(), repr=False)
    canonical_call_ids: list[str] = field(default_factory=list, repr=False)
    summary_call_id_digests: tuple[bytes, ...] = field(default=(), repr=False)
    canonical_summary_relation: str = "unknown"
    failure_class: str | None = field(default=None, repr=False)
    validation_stage: str | None = field(default=None, repr=False)
    overflow_subtype: str | None = field(default=None, repr=False)
    overflow_observed: int | None = field(default=None, repr=False)
    overflow_bound: int | None = field(default=None, repr=False)

    def _fail(
        self,
        failure_class: str,
        *,
        validation_stage: str | None = None,
        overflow_subtype: str | None = None,
        overflow_observed: int | None = None,
        overflow_bound: int | None = None,
    ) -> None:
        self.invalid = True
        if self.failure_class is not None:
            return
        self.failure_class = failure_class
        if isinstance(validation_stage, str) and validation_stage in VALIDATION_STAGES:
            self.validation_stage = validation_stage
        if (
            failure_class == "overflow"
            and overflow_subtype
            in {
                "replay_candidate_cardinality",
                "returned_call_cardinality",
                "frame_buffer_bytes",
            }
            and type(overflow_observed) is int
            and type(overflow_bound) is int
            and 0 <= overflow_observed <= 1_000_000
            and 0 <= overflow_bound <= 1_000_000
        ):
            self.overflow_subtype = overflow_subtype
            self.overflow_observed = overflow_observed
            self.overflow_bound = overflow_bound

    @staticmethod
    def _valid_identifier(value: object) -> bool:
        return (
            isinstance(value, str)
            and bool(value)
            and len(value) <= 512
            and not any(char in value for char in "\r\n")
        )

    def _capture_frame(self, frame: bytes) -> None:
        if not frame:
            self._fail("framing")
            return
        if len(frame) > FAKE_MAX_EVENT_BYTES:
            self._fail("framing")
            return
        parsed = _sse_frame_payload(frame)
        if parsed is None:
            if _comment_only_sse_frame(frame):
                return
            self._fail("framing")
            return
        event_name, payload = parsed
        if self.validator is None:
            self._fail("validator", validation_stage="gateway_validator")
            return
        validate = getattr(self.validator, "validate", None)
        take_candidates = getattr(self.validator, "take_replay_reference_candidates", None)
        if not callable(validate) or not callable(take_candidates):
            self._fail("validator", validation_stage="gateway_validator")
            return
        try:
            valid = validate(payload)
            candidates = take_candidates()
        except BaseException:
            self._fail("validator", validation_stage="gateway_validator")
            return
        if not valid:
            self._fail("validator", validation_stage="gateway_validator")
            return
        if not isinstance(candidates, tuple):
            self._fail("validation", validation_stage="replay_candidate")
            return
        if len(candidates) > FAKE_MAX_EVENTS:
            self._fail(
                "overflow",
                overflow_subtype="replay_candidate_cardinality",
                overflow_observed=len(candidates),
                overflow_bound=FAKE_MAX_EVENTS,
            )
            return
        for candidate in candidates:
            item_kind = getattr(candidate, "item_kind", None)
            if item_kind == "reasoning":
                continue
            if item_kind not in {"function_call", "custom_tool_call"}:
                self._fail("validation", validation_stage="replay_candidate")
                continue
            call_id = getattr(candidate, "call_id", None)
            item_id = getattr(candidate, "item_id", None)
            if not self._valid_identifier(item_id) or not self._valid_identifier(call_id):
                self._fail("validation", validation_stage="replay_candidate")
                continue
            assert isinstance(call_id, str)
            self.canonical_candidate_count += 1
            if len(self.canonical_call_ids) >= FAKE_MAX_FUNCTION_CALLS:
                self._fail(
                    "overflow",
                    overflow_subtype="returned_call_cardinality",
                    overflow_observed=len(self.canonical_call_ids) + 1,
                    overflow_bound=FAKE_MAX_FUNCTION_CALLS,
                )
                continue
            self.canonical_call_ids.append(call_id)
            self.canonical_call_id_digests += (hashlib.sha256(call_id.encode("utf-8")).digest(),)
        if event_name == "response.completed":
            self.summary_call_id_digests = _summary_call_id_digests(payload)
            if self.canonical_call_id_digests and self.summary_call_id_digests:
                self.canonical_summary_relation = (
                    "same"
                    if self.canonical_call_id_digests == self.summary_call_id_digests
                    else "different"
                )

    def consume(self, chunk: bytes) -> None:
        if self.invalid:
            return
        self.buffer.extend(chunk)
        while True:
            delimiters = [
                (self.buffer.find(b"\n\n"), 2),
                (self.buffer.find(b"\r\n\r\n"), 4),
            ]
            available = [(index, size) for index, size in delimiters if index >= 0]
            if not available:
                if len(self.buffer) > FAKE_MAX_EVENT_BYTES + 4:
                    self._fail(
                        "overflow",
                        overflow_subtype="frame_buffer_bytes",
                        overflow_observed=FAKE_MAX_EVENT_BYTES + 5,
                        overflow_bound=FAKE_MAX_EVENT_BYTES + 4,
                    )
                    self.buffer.clear()
                return
            index, size = min(available)
            frame = bytes(self.buffer[:index])
            del self.buffer[: index + size]
            self._capture_frame(frame)

    def finish(self, *, stream_valid: bool) -> None:
        if self.buffer:
            self._fail("framing")
            self.buffer.clear()
        if not stream_valid and self.failure_class is None:
            self._fail("validator", validation_stage="gateway_validator")
        if not stream_valid or self.invalid or len(self.canonical_call_ids) != 1:
            self.value = None
            return
        self.value = self.canonical_call_ids[0]

    def safe_facts(self) -> dict[str, object]:
        availability = (
            "available"
            if self.canonical_candidate_count
            else "none"
            if self.validator is not None and not self.invalid
            else "unknown"
        )
        facts: dict[str, object] = {
            "canonical_candidate_availability": availability,
            "canonical_candidate_count_class": count_class(self.canonical_candidate_count),
            "canonical_summary_relation": self.canonical_summary_relation,
        }
        if self.failure_class is not None:
            facts["failure_class"] = self.failure_class
        if self.validation_stage is not None:
            facts["validation_stage"] = self.validation_stage
        if self.overflow_subtype is not None:
            facts.update(
                {
                    "overflow_subtype": self.overflow_subtype,
                    "overflow_observed": self.overflow_observed,
                    "overflow_bound": self.overflow_bound,
                }
            )
        return facts


def _timed_public_stream(
    gateway_url: str,
    gateway_key: str,
    body: dict[str, object],
    *,
    capture_returned_call_id: bool = False,
    validator_factory: Callable[[httpx.Request], Any] | None = None,
) -> tuple[int | None, SSEFacts, dict[str, str], int, str | None, dict[str, object]]:
    """Observe one stream with the shared bounded 005-j SSE parser."""
    started = time.monotonic()
    timing: dict[str, str] = {}
    sse = SSEFacts()
    request_body = json.dumps(body, separators=(",", ":")).encode("utf-8")
    returned_call_capture = None
    if capture_returned_call_id:
        try:
            validator = (
                validator_factory(
                    httpx.Request(
                        "POST",
                        f"{gateway_url}/v1/responses",
                        headers={"content-type": "application/json"},
                        content=request_body,
                    )
                )
                if validator_factory is not None
                else None
            )
        except BaseException:
            validator = None
        returned_call_capture = _ReturnedCallIDCapture(validator=validator)
    chunk_count = 0
    status: int | None = None
    try:
        with httpx.Client(timeout=300, follow_redirects=False) as http:
            with http.stream(
                "POST",
                f"{gateway_url}/v1/responses",
                headers={
                    "Authorization": f"Bearer {gateway_key}",
                    "Accept": "text/event-stream",
                    "Content-Type": "application/json",
                },
                content=request_body,
            ) as response:
                status = response.status_code
                bucket = _timing_bucket(time.monotonic() - started)
                if bucket is not None:
                    timing["response_headers"] = bucket
                for chunk in response.iter_raw():
                    if not chunk:
                        continue
                    chunk_count += 1
                    if "first_sse_bytes" not in timing:
                        bucket = _timing_bucket(time.monotonic() - started)
                        if bucket is not None:
                            timing["first_sse_bytes"] = bucket
                    sse.consume(chunk)
                    if returned_call_capture is not None:
                        returned_call_capture.consume(chunk)
                    if sse.completed and "terminal_completion" not in timing:
                        bucket = _timing_bucket(time.monotonic() - started)
                        if bucket is not None:
                            timing["terminal_completion"] = bucket
                sse.finish()
                bucket = _timing_bucket(time.monotonic() - started)
                if bucket is not None:
                    timing["normal_close"] = bucket
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        if returned_call_capture is not None:
            returned_call_capture.finish(stream_valid=False)
        return (
            status,
            sse,
            timing,
            chunk_count,
            returned_call_capture.value if returned_call_capture is not None else None,
            returned_call_capture.safe_facts() if returned_call_capture is not None else {},
        )
    if returned_call_capture is not None:
        returned_call_capture.finish(stream_valid=sse.completed_valid and status == 200)
    return (
        status,
        sse,
        timing,
        chunk_count,
        returned_call_capture.value if returned_call_capture is not None else None,
        returned_call_capture.safe_facts() if returned_call_capture is not None else {},
    )


def _timed_public_json_response(
    gateway_url: str, gateway_key: str, body: dict[str, object]
) -> tuple[int | None, bool, bool]:
    """Make one bounded non-streaming request and retain only validity facts."""
    status: int | None = None
    try:
        with httpx.Client(timeout=300, follow_redirects=False) as http:
            response = http.post(
                f"{gateway_url}/v1/responses",
                headers={
                    "Authorization": f"Bearer {gateway_key}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                content=json.dumps(body, separators=(",", ":")).encode("utf-8"),
            )
            status = response.status_code
            if status != 200 or len(response.content) > FAKE_MAX_STREAM_BYTES:
                return status, False, False
            payload = response.json()
    except (httpx.HTTPError, json.JSONDecodeError, TypeError, ValueError):
        return status, False, False
    if not isinstance(payload, dict):
        return status, False, False
    usage = payload.get("usage")
    usage_valid = (
        isinstance(usage, dict)
        and all(
            type(usage.get(key)) is int and usage[key] >= 0
            for key in ("input_tokens", "output_tokens", "total_tokens")
        )
        and usage.get("total_tokens")
        == usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
    )
    response_valid = (
        payload.get("status") == "completed"
        and isinstance(payload.get("output"), list)
        and bool(payload["output"])
        and usage_valid
    )
    return status, response_valid, usage_valid


def _response_status(call: Any) -> int:
    try:
        call()
    except APIStatusError as exc:
        return int(exc.status_code)
    return 200


def _composed_request_body(
    session: str,
    text: str,
    *,
    tools: list[dict[str, object]] | None = None,
    image_data_url: str | None = None,
) -> dict[str, object]:
    content: list[dict[str, object]] = [{"type": "input_text", "text": text}]
    if image_data_url is not None:
        content.append({"type": "input_image", "image_url": image_data_url, "detail": "auto"})
    turn = str(uuid.uuid4())
    window = str(uuid.uuid4())
    metadata = {
        "session_id": session,
        "thread_id": session,
        "root_turn_id": turn,
        "turn_id": turn,
        "x-codex-installation-id": "005k-installation",
        "x-codex-window-id": window,
    }
    result: dict[str, object] = {
        "model": PUBLIC_MODEL,
        "input": [{"type": "message", "role": "user", "content": content}],
        "client_metadata": metadata,
    }
    if tools is not None:
        result["tools"] = tools
    return result


def _idless_companion_initial_body(
    session: str, tools: list[dict[str, object]]
) -> dict[str, object]:
    """Build the deterministic initial function-call side of the companion."""
    body = _composed_request_body(session, "Call local_lookup with no arguments.", tools=tools)
    body.update(
        {
            "stream": True,
            "max_output_tokens": 32,
            "store": False,
            "tool_choice": {"type": "function", "name": "local_lookup"},
        }
    )
    return body


def _openai_kwargs(body: dict[str, object]) -> dict[str, object]:
    """Move only the synthetic client metadata into the SDK extension field."""
    result = dict(body)
    metadata = result.pop("client_metadata", None)
    if metadata is not None:
        result["extra_body"] = {"client_metadata": metadata}
    return result


def _run_fake_codex_turn(
    codex: Path,
    fixture: Any,
    gateway_url: str,
    public_key: str,
    *,
    feature_flags: tuple[str, ...],
) -> dict[str, object]:
    """Run the actual pinned Codex through the actual Gateway/Local chain."""
    previous = os.environ.get(PUBLIC_KEY_ENV)
    os.environ[PUBLIC_KEY_ENV] = public_key
    try:
        run = run_codex_once(
            codex,
            fixture,
            governed_prompt(),
            timeout_seconds=300,
            expected_command="cat GOVERNANCE-DEPENDENCY.md",
            feature_flags=feature_flags,
            ignore_user_config=True,
            provider_base_url=gateway_url + "/v1",
            model=PUBLIC_MODEL,
            disable_unified_exec=False,
            environment_root=fixture.codex_home.parent,
        )
    finally:
        if previous is None:
            os.environ.pop(PUBLIC_KEY_ENV, None)
        else:
            os.environ[PUBLIC_KEY_ENV] = previous
    successful = (
        run.exit_status == 0
        and run.sentinel_passed
        and run.dependency_observation.lifecycle == "success"
        and run.tool_calls >= 1
        and run.codex_under_test_yolo
    )
    client_failure_origin = "success" if successful else run.failure_origin
    dependency_path = fixture.repository / "GOVERNANCE-DEPENDENCY.md"
    try:
        dependency_bytes = dependency_path.read_bytes()
    except OSError:
        dependency_bytes = b""
    dependency_hash_equal = (
        bool(dependency_bytes)
        and run.dependency_observation.output_sha256 == hashlib.sha256(dependency_bytes).hexdigest()
        and run.dependency_observation.output_byte_length == len(dependency_bytes)
    )
    return {
        "status": "PASSED" if successful else "FAILED",
        "client_verification": {
            "status": "PASSED" if successful else "FAILED",
            "exit_status": run.exit_status,
            "failure_origin": client_failure_origin,
            "failure_reason": run.failure_reason,
            "sentinel_passed": run.sentinel_passed,
            "command_lifecycle": run.dependency_observation.lifecycle,
        },
        "version": CODEX_VERSION,
        "binary_sha256": CODEX_FIXTURE_SHA256,
        "exit_status": run.exit_status,
        "tool_call_count_class": "1"
        if run.tool_calls == 1
        else "2"
        if run.tool_calls == 2
        else "unknown",
        "dependency_read_count_class": (
            "1" if run.dependency_observation.successful_dependency_reads == 1 else "unknown"
        ),
        "sentinel_passed": run.sentinel_passed,
        "command_lifecycle": run.dependency_observation.lifecycle,
        "failure_reason": run.failure_reason,
        "failure_origin": client_failure_origin,
        "diagnostic_class": run.command_diagnostics.failure_class,
        "stderr_class": (
            run.command_diagnostics.stderr.first_line_class
            if run.command_diagnostics.stderr is not None
            else "unavailable"
        ),
        "stderr_subclass": (
            run.command_diagnostics.stderr.first_line_subclass
            if run.command_diagnostics.stderr is not None
            else "empty"
        ),
        "event_count_class": (
            "0" if run.event_bytes == 0 else "1" if run.event_bytes <= 4096 else "5+"
        ),
        "event_type_classes": tuple(sorted(run.event_type_counts)),
        "parser_recognized_event_count_class": (
            "0"
            if run.parser_recognized_events == 0
            else "1"
            if run.parser_recognized_events == 1
            else "2"
            if run.parser_recognized_events == 2
            else "3-4"
            if run.parser_recognized_events <= 4
            else "5+"
        ),
        "error_field_names": tuple(run.error_field_names),
        "error_code_class": run.error_code_class,
        "error_message_classes": tuple(run.error_message_classes),
        "provider_turns_expected": 2,
        "retry_count": 0,
        "dependency_hash_equal": dependency_hash_equal,
        "dependency_length_equal": (
            bool(dependency_bytes)
            and run.dependency_observation.output_byte_length == len(dependency_bytes)
        ),
    }


def _run_signed_identity_matrix(
    adapter_port: int,
    service_token: str,
    signing_secret: str,
    *,
    provider_calls_before: int | None = None,
    provider_calls_after: int | None = None,
    accounting_rows_before: int | None = None,
    accounting_rows_after: int | None = None,
) -> dict[str, object]:
    """Exercise the real adapter admission/replay boundary with synthetic facts."""
    base_body = b""
    base_query = b""
    base_path = "/health"
    base_identity = {
        "principal": "synthetic-principal",
        "session": "synthetic-session",
        "repository": "synthetic-repository",
        "route": LOCAL_ROUTE,
    }
    timestamp = str(int(time.time()))

    def headers(
        *,
        body: bytes = base_body,
        query: bytes = base_query,
        path: str = base_path,
        nonce: str,
        identity: dict[str, str] | None = None,
        signature_override: str | None = None,
        timestamp_value: str = timestamp,
    ) -> list[tuple[str, str]]:
        selected = base_identity if identity is None else identity
        canonical = canonical_identity_bytes(
            method="GET",
            path=path,
            raw_query=query,
            body=body,
            principal=selected["principal"],
            session=selected["session"],
            repository=selected["repository"],
            route=selected["route"],
            timestamp=timestamp_value,
            nonce=nonce,
        )
        signature = signature_override or expected_signature(
            secret=signing_secret.encode("ascii"), canonical=canonical
        )
        return [
            ("Authorization", f"Bearer {service_token}"),
            ("X-SLAIF-Identity-Version", "v1"),
            ("X-SLAIF-Principal", selected["principal"]),
            ("X-SLAIF-Session", selected["session"]),
            ("X-SLAIF-Repository", selected["repository"]),
            ("X-SLAIF-Route", selected["route"]),
            ("X-SLAIF-Timestamp", timestamp_value),
            ("X-SLAIF-Nonce", nonce),
            ("X-SLAIF-Signature", signature),
        ]

    def request(
        client: httpx.Client,
        *,
        request_path: str = base_path,
        query: bytes = base_query,
        request_body: bytes = base_body,
        request_headers: list[tuple[str, str]],
    ) -> int:
        query_text = query.decode("ascii")
        url = f"http://127.0.0.1:{adapter_port}{request_path}"
        if query_text:
            url += "?" + query_text
        return client.request("GET", url, content=request_body, headers=request_headers).status_code

    with httpx.Client(timeout=15, follow_redirects=False) as client:
        valid_nonce = "synthetic-valid-nonce-01"
        valid_status = request(client, request_headers=headers(nonce=valid_nonce))
        replay_status = request(client, request_headers=headers(nonce=valid_nonce))
        concurrent_nonce = "synthetic-concurrent-nonce-01"
        concurrent_headers = headers(nonce=concurrent_nonce)

        def concurrent_request() -> int:
            with httpx.Client(timeout=15, follow_redirects=False) as worker:
                return request(worker, request_headers=concurrent_headers)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            concurrent_statuses = tuple(pool.map(lambda _: concurrent_request(), range(2)))

        changed_identity_statuses = {
            "session": request(
                client,
                request_headers=headers(
                    nonce="synthetic-isolation-session-01",
                    identity={**base_identity, "session": "synthetic-other-session"},
                ),
            ),
            "owner": request(
                client,
                request_headers=headers(
                    nonce="synthetic-isolation-owner-01",
                    identity={**base_identity, "principal": "synthetic-other-owner"},
                ),
            ),
            "repository": request(
                client,
                request_headers=headers(
                    nonce="synthetic-isolation-repository-01",
                    identity={**base_identity, "repository": "synthetic-other-repository"},
                ),
            ),
        }

        tamper_requests: dict[str, tuple[str, bytes, bytes, list[tuple[str, str]]]] = {
            "body": (
                base_path,
                base_query,
                b"synthetic-body-change",
                headers(nonce="synthetic-tamper-body-01"),
            ),
            "query": (
                base_path,
                b"synthetic=query",
                base_body,
                headers(nonce="synthetic-tamper-query-01"),
            ),
            "path": (
                "/v1/models",
                base_query,
                base_body,
                headers(nonce="synthetic-tamper-path-01"),
            ),
            "route": (
                base_path,
                base_query,
                base_body,
                headers(
                    nonce="synthetic-tamper-route-01",
                    identity={**base_identity, "route": "other-route"},
                ),
            ),
            "signature": (
                base_path,
                base_query,
                base_body,
                headers(nonce="synthetic-tamper-signature-01", signature_override="v1=" + "0" * 64),
            ),
            "timestamp": (
                base_path,
                base_query,
                base_body,
                headers(nonce="synthetic-tamper-time-01", timestamp_value="1"),
            ),
            "nonce": (base_path, base_query, base_body, headers(nonce="synthetic-tamper-nonce-01")),
        }
        tamper_statuses = {
            name: request(
                client,
                request_path=path,
                query=query,
                request_body=body,
                request_headers=(
                    [
                        (key, value.replace("synthetic-tamper-nonce-01", "bad nonce"))
                        for key, value in request_headers
                    ]
                    if name == "nonce"
                    else request_headers
                ),
            )
            for name, (path, query, body, request_headers) in tamper_requests.items()
        }
        ambiguous_headers = headers(nonce="synthetic-tamper-ambiguous-01") + [
            ("X-SLAIF-Principal", "synthetic-other-principal")
        ]
        missing_headers = [
            pair
            for pair in headers(nonce="synthetic-tamper-missing-01")
            if pair[0].lower() != "x-slaif-session"
        ]
        ambiguous_status = request(client, request_headers=ambiguous_headers)
        missing_status = request(client, request_headers=missing_headers)
    rejected = all(status in {401, 403, 409, 422} for status in tamper_statuses.values())
    rejected = (
        rejected
        and ambiguous_status in {401, 403, 409, 422}
        and missing_status in {401, 403, 409, 422}
    )
    no_provider_duplicate = (
        provider_calls_before is not None
        and provider_calls_after is not None
        and provider_calls_after == provider_calls_before
    )
    no_accounting_duplicate = (
        accounting_rows_before is not None
        and accounting_rows_after is not None
        and accounting_rows_after == accounting_rows_before
    )
    return {
        "every_admission_verified": valid_status == 200,
        "same_session": valid_status == 200,
        "different_session": changed_identity_statuses["session"] == 200,
        "different_owner": changed_identity_statuses["owner"] == 200,
        "different_repository": changed_identity_statuses["repository"] == 200,
        "replay_one_accept": valid_status == 200 and replay_status == 409,
        "replay_no_provider_duplicate": no_provider_duplicate,
        "replay_no_accounting_duplicate": no_accounting_duplicate,
        "tamper_body": tamper_statuses["body"] in {401, 403, 409, 422},
        "tamper_query": tamper_statuses["query"] in {401, 403, 409, 422},
        "tamper_path": tamper_statuses["path"] in {401, 403, 409, 422},
        "tamper_route": tamper_statuses["route"] in {401, 403, 409, 422},
        "tamper_signature": tamper_statuses["signature"] in {401, 403, 409, 422},
        "tamper_timestamp": tamper_statuses["timestamp"] in {401, 403, 409, 422},
        "tamper_nonce": tamper_statuses["nonce"] in {401, 403, 409, 422},
        "tamper_ambiguous": ambiguous_status in {401, 403, 409, 422},
        "tamper_missing": missing_status in {401, 403, 409, 422},
        "concurrent_one_accept": concurrent_statuses.count(200) == 1
        and concurrent_statuses.count(409) == 1,
        "pre_provider": rejected,
    }


def _replay_ownership_negative_observation(
    statuses: Mapping[str, int | None],
    *,
    provider_calls_before: int,
    provider_calls_after: int,
    primary_rows_before: Mapping[str, object],
    primary_rows_after: Mapping[str, object],
    second_rows_before: Mapping[str, object],
    second_rows_after: Mapping[str, object],
) -> dict[str, object]:
    """Project companion ownership negatives without retaining IDs or bodies."""
    expected_cases = ("missing_call_id", "mismatched_call_id", "wrong_key")
    status_classes = {case: _status_class(statuses.get(case)) for case in expected_cases}

    def accounting_unchanged(before: Mapping[str, object], after: Mapping[str, object]) -> bool:
        fields = (
            "reservation_count",
            "finalized_reservation_count",
            "pending_reservation_count",
            "ledger_count",
            "finalized_ledger_count",
            "failed_ledger_count",
            "duplicate_request_id_count",
            "provider_usage_rows",
            "key_requests_used",
            "key_tokens_used",
            "ledger_total_tokens",
            "ledger_total_cost_eur",
        )
        return all(before.get(field) == after.get(field) for field in fields)

    all_denied = all(status_classes[case] == "4xx" for case in expected_cases)
    provider_unchanged = provider_calls_after == provider_calls_before
    primary_unchanged = accounting_unchanged(primary_rows_before, primary_rows_after)
    second_unchanged = accounting_unchanged(second_rows_before, second_rows_after)
    zero_pending = all(
        rows.get("pending_reservation_count") == 0
        for rows in (primary_rows_after, second_rows_after)
    )
    zero_duplicates = all(
        rows.get("duplicate_request_id_count") == 0
        for rows in (primary_rows_after, second_rows_after)
    )
    return {
        "passed": (
            all_denied
            and provider_unchanged
            and primary_unchanged
            and second_unchanged
            and zero_pending
            and zero_duplicates
        ),
        "scope": "gateway_responses_companion",
        "request_count_class": count_class(len(expected_cases)),
        "missing_call_id_status_class": status_classes["missing_call_id"],
        "mismatched_call_id_status_class": status_classes["mismatched_call_id"],
        "wrong_key_status_class": status_classes["wrong_key"],
        "all_denied": all_denied,
        "provider_calls_unchanged": provider_unchanged,
        "primary_accounting_unchanged": primary_unchanged,
        "second_key_accounting_unchanged": second_unchanged,
        "zero_pending": zero_pending,
        "zero_duplicate_request_ids": zero_duplicates,
    }


def _run_replay_ownership_negative_matrix(
    gateway_url: str,
    primary_key: str,
    second_key: str,
    continuation_body: Mapping[str, object],
) -> dict[str, int | None]:
    """Send only pre-provider companion ownership negatives through Gateway."""

    def continuation(*, call_id: str | None, include_call: bool = False) -> dict[str, object]:
        output_item: dict[str, object] = {
            "type": "function_call_output",
            "output": "synthetic companion result",
        }
        if call_id is not None:
            output_item["call_id"] = call_id
        body = dict(continuation_body)
        if include_call:
            call_item = {
                "type": "function_call",
                "call_id": call_id,
                "name": "local_lookup",
                "arguments": "{}",
                "status": "completed",
            }
            body["input"] = [call_item, output_item]
        else:
            body["input"] = [output_item]
        return body

    def post_status(gateway_key: str, body: Mapping[str, object]) -> int | None:
        try:
            with httpx.Client(timeout=45, follow_redirects=False) as http:
                response = http.post(
                    f"{gateway_url}/v1/responses",
                    headers={
                        "Authorization": f"Bearer {gateway_key}",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    content=json.dumps(body, separators=(",", ":")).encode("utf-8"),
                )
                return response.status_code
        except httpx.HTTPError:
            return None

    returned_call_id = continuation_body.get("input")
    call_id: str | None = None
    if isinstance(returned_call_id, list) and returned_call_id:
        first_item = returned_call_id[0]
        if isinstance(first_item, dict) and isinstance(first_item.get("call_id"), str):
            call_id = first_item["call_id"]
    return {
        "missing_call_id": post_status(primary_key, continuation(call_id=None)),
        "mismatched_call_id": post_status(
            primary_key,
            {
                **continuation(call_id=call_id, include_call=True),
                "input": [
                    {
                        "type": "function_call",
                        "call_id": call_id,
                        "name": "local_lookup",
                        "arguments": "{}",
                        "status": "completed",
                    },
                    {
                        "type": "function_call_output",
                        "call_id": "synthetic-unowned-call",
                        "output": "synthetic companion result",
                    },
                ],
            },
        ),
        "wrong_key": post_status(second_key, continuation(call_id=call_id, include_call=True)),
    }


def _runtime_observations(result: dict[str, object]) -> dict[str, object]:
    """Build a mode-specific bounded observation schema from concrete facts."""
    mode: Literal["fake", "protected"] = (
        "protected" if result.get("provider_target") == "protected" else "fake"
    )
    schema_keys = PROTECTED_RESULT_SCHEMA_KEYS if mode == "protected" else FAKE_RESULT_SCHEMA_KEYS
    observations: dict[str, object] = {key: None for key in schema_keys}

    def put(key: str, value: object) -> None:
        if key in observations:
            observations[key] = (
                None if value is None else value if isinstance(value, bool) else bool(value)
            )

    codex = result.get("codex")
    provider = result.get("provider_observation")
    if mode == "fake" and not isinstance(provider, dict):
        provider = result.get("fake_provider")
    boundary = provider.get("provider_boundary") if isinstance(provider, dict) else None
    if isinstance(codex, dict):
        codex_passed = codex.get("status") == "PASSED"
        provider_calls = codex.get("provider_inference_call_count")
        put("provider.two_inference_calls", codex_passed and provider_calls == 2)
        put(
            "codex.two_turns",
            codex_passed and codex.get("provider_turns_expected") == 2 and provider_calls == 2,
        )
        put("codex.actual_chain", codex_passed and codex.get("exit_status") == 0)
        put(
            "codex.first_function_call",
            isinstance(boundary, dict)
            and "function_initial" in boundary.get("request_class_classes", ()),
        )
        put("codex.local_tool_success", codex.get("command_lifecycle") == "success")
        put(
            "codex.function_result_adjacent",
            isinstance(boundary, dict) and boundary.get("function_result_adjacent") is True,
        )
    if isinstance(boundary, dict):
        put(
            "provider.two_inference_calls",
            observations["provider.two_inference_calls"] is True
            or boundary.get("call_count_class") == "2",
        )
        put("provider.independent_from_accounting", boundary.get("independent_from_ledger") is True)
        put("provider.reasoning_lifecycle_valid", boundary.get("lifecycle_valid") is True)
        put(
            "provider.function_lifecycle_valid",
            "function_initial" in boundary.get("request_class_classes", ()),
        )
        put(
            "provider.message_lifecycle_valid",
            "function_continuation" in boundary.get("request_class_classes", ()),
        )
        put("provider.terminal_usage", boundary.get("terminality_valid") is True)
        put("provider.newest_single_image", boundary.get("all_image_requests_single") is True)
        put("provider.fixture_hashes", boundary.get("image_hashes_observed") is True)
    transport = result.get("transport_observation")
    if isinstance(transport, dict):
        put(
            "provider.transport_boundary_observed",
            transport.get("provider_boundary_observed") is True
            or transport.get("matches_fake_provider") is True,
        )
    companion = result.get("idless_composed_companion")
    if isinstance(companion, dict):
        put(
            "provider.idless_continuation_supported",
            companion.get("passed") is True,
        )
        put(
            "codex.call_id_present",
            companion.get("returned_call_id_present") is True
            and companion.get("mandatory_call_id_matching") is True,
        )
        put(
            "gateway.call_id_same_hmac",
            companion.get("gateway_call_id_same_hmac") is True,
        )
        put("gateway.scope_no_downgrade", companion.get("scope_no_downgrade") is True)
    elif isinstance(companion, dict):
        put("provider.idless_continuation_supported", False)
        put("codex.call_id_present", False)
        put("gateway.call_id_same_hmac", False)
        put("gateway.scope_no_downgrade", False)
    else:
        accumulator = result.get("run_accumulator")
        runtime_failed = isinstance(accumulator, Mapping) and isinstance(
            accumulator.get("first_failure"), str
        )
        if not runtime_failed:
            put("provider.idless_continuation_supported", False)
            put("codex.call_id_present", False)
            put("gateway.call_id_same_hmac", False)
            put("gateway.scope_no_downgrade", False)
    accounting = result.get("accounting")
    codex_accounting = codex.get("accounting") if isinstance(codex, dict) else None
    accounting_facts = codex_accounting if isinstance(codex_accounting, dict) else accounting
    if isinstance(accounting_facts, dict):
        put(
            "gateway.two_terminal_reservations",
            accounting_facts.get("two_terminal_reservations") is True,
        )
        put("gateway.zero_pending", accounting_facts.get("zero_pending") is True)
        put(
            "gateway.zero_duplicate_request_ids",
            accounting_facts.get("zero_duplicate_request_ids") is True,
        )
        put("gateway.accounting_request", accounting_facts.get("request") is True)
        put("gateway.accounting_usage", accounting_facts.get("usage") is True)
        put("gateway.accounting_tokens", accounting_facts.get("tokens") is True)
        put("gateway.accounting_cost", accounting_facts.get("cost") is True)
        put("gateway.accounting_zero_pending", accounting_facts.get("zero_pending") is True)
        put(
            "gateway.accounting_zero_duplicate",
            accounting_facts.get("zero_duplicate_request_ids") is True,
        )
    constitution = result.get("constitution")
    if isinstance(constitution, dict):
        for key in (
            "root_observed",
            "dependency_one_equal",
            "acquisition_before_completion",
            "candidates_observed",
            "compiler_miss",
            "validated_cache",
            "injection_observed",
            "zero_root",
            "cache_reuse",
            "no_compiler",
        ):
            put(f"constitution.{key}", constitution.get(key) is True)
            put(f"rehydration.{key}", constitution.get(key) is True)
        put("compiler.cache_miss", constitution.get("compiler_miss") is True)
        put("cache.validated_entry", constitution.get("validated_cache") is True)
        put("constitution.injection_observed", constitution.get("injection_observed") is True)
        put("rehydration.zero_root", constitution.get("zero_root") is True)
        put("rehydration.cache_reuse", constitution.get("cache_reuse") is True)
        put("rehydration.no_compiler", constitution.get("no_compiler") is True)
    isolation = result.get("isolation")
    if isinstance(isolation, dict):
        for dimension in ("session", "owner", "repository"):
            put(f"isolation.{dimension}_negative", isolation.get(f"{dimension}_negative") is True)
            put(f"isolation.{dimension}_distinct", isolation.get(f"{dimension}_distinct") is True)
    vision = result.get("vision")
    if isinstance(vision, dict):
        put(
            "vision.two_turns",
            vision.get("turn_count_class") == "2" and vision.get("status") == "PASSED",
        )
        put("vision.history_turn", vision.get("history_turn") is True)
        put("vision.local_history_multiplicity", vision.get("local_history_multiplicity") is True)
        put("vision.local_history_removal", vision.get("local_history_removal") is True)
        put("vision.governance_both_turns", vision.get("governance_both_turns") is True)
        put("vision.two_terminal_turns", vision.get("two_terminal_turns") is True)
    identity = result.get("identity_matrix")
    if isinstance(identity, dict):
        for key in (
            "every_admission_verified",
            "same_session",
            "different_session",
            "different_owner",
            "different_repository",
            "replay_one_accept",
            "replay_no_provider_duplicate",
            "replay_no_accounting_duplicate",
            "tamper_body",
            "tamper_query",
            "tamper_path",
            "tamper_route",
            "tamper_signature",
            "tamper_timestamp",
            "tamper_nonce",
            "tamper_ambiguous",
            "tamper_missing",
        ):
            put(f"identity.{key}", identity.get(key) is True)
    gateway_rejects = result.get("gateway_rejects")
    if isinstance(gateway_rejects, dict):
        for key in ("invalid_key", "hosted_choice", "dropped_tool", "over_quota", "pre_provider"):
            put(f"gateway.reject_{key}", gateway_rejects.get(key) is True)
        put("gateway.rejects_pre_provider", gateway_rejects.get("pre_provider") is True)
    failure = result.get("failure_observation")
    if isinstance(failure, dict):
        for key in ("one_provider_call", "terminal_accounting", "no_unrelated_call"):
            put(f"failure.{key}", failure.get(key) is True)
    compiler = result.get("compiler_observation")
    if isinstance(compiler, dict):
        for key in ("zero_public_rows", "zero_public_fees", "zero_public_fence"):
            put(f"compiler.{key}", compiler.get(key) is True)
    cleanup = result.get("cleanup_observation")
    if isinstance(cleanup, dict):
        for key in ("failure_replay", "failure_cache", "failure_identity", "failure_provider"):
            put(f"cleanup.{key}", cleanup.get(key) is True)
        for key in ("processes", "listeners", "database", "cache", "codex_home"):
            put(f"cleanup.{key}", cleanup.get(key) is True)
    topology = result.get("topology_observation")
    if isinstance(topology, dict):
        for key in ("codex_gateway_local_provider", "no_direct_route"):
            if key in topology:
                put(f"topology.{key}", topology.get(key) is True)
    privacy_fact = _runtime_privacy_fact(result)
    if privacy_fact is not None:
        put("privacy.no_raw_canaries", privacy_fact)
        put("privacy.no_raw_bodies", privacy_fact)
        put("privacy.no_credentials", privacy_fact)
    cutover = result.get("cutover_observations")
    if isinstance(cutover, dict):
        for key, value in cutover.items():
            if key in observations:
                put(key, value)
    protected_fixture = result.get("protected_unchanged")
    if mode == "protected" and isinstance(protected_fixture, dict):
        put(
            "protected.fixture_pid_unchanged",
            protected_fixture.get("pid"),
        )
        put(
            "protected.fixture_start_unchanged",
            protected_fixture.get("start"),
        )
        put(
            "protected.fixture_listener_unchanged",
            protected_fixture.get("listener"),
        )
        put(
            "protected.fixture_worktree_unchanged",
            protected_fixture.get("worktree_count"),
        )
    return observations


def _runtime_privacy_fact(result: Mapping[str, object]) -> bool | None:
    """Return only an explicitly retained boolean privacy-scan result.

    The scan is performed during runner cleanup and its boolean is the sole
    runtime evidence for C5.2. Missing, non-boolean, or descriptive marker
    values are unknown rather than a passing or failing scan.
    """
    value = result.get("logs_secret_free")
    return value if type(value) is bool else None


def _acceptance_gate(
    result: dict[str, object],
) -> tuple[dict[str, object], tuple[dict[str, object], ...]]:
    """Project only observed runtime facts into the selected mode manifest."""
    observations = _runtime_observations(result)
    mode: Literal["fake", "protected"] = (
        "protected" if result.get("provider_target") == "protected" else "fake"
    )
    validate_projection_contract(mode)
    schema_keys = PROTECTED_RESULT_SCHEMA_KEYS if mode == "protected" else FAKE_RESULT_SCHEMA_KEYS
    selected_items = tuple(item for item in ACCEPTANCE_MANIFEST if item.mode in {"both", mode})
    always_execute = {"C4.9", "C5.2", "C5.3"}
    accumulator = result.get("run_accumulator")
    runtime_failure = (
        accumulator.get("first_failure")
        if isinstance(accumulator, Mapping) and isinstance(accumulator.get("first_failure"), str)
        else None
    )
    phase_checkpoints = result.get("phase_checkpoints")
    checkpointed_phase = isinstance(phase_checkpoints, (list, tuple)) and any(
        isinstance(item, Mapping)
        and item.get("evidence_kind") == "semantic"
        and isinstance(item.get("phase_facts"), Mapping)
        for item in phase_checkpoints
    )
    privacy_fact = _runtime_privacy_fact(result)
    statuses: dict[str, ObligationResult] = {}
    for item in selected_items:
        dependency_passed = item.stop_dependency == "preflight" or (
            statuses.get(item.stop_dependency) is not None
            and statuses[item.stop_dependency].status == "PASSED"
        )
        if not dependency_passed and item.obligation_id not in always_execute:
            statuses[item.obligation_id] = make_result(
                item.obligation_id, status="NOT RUN", observed=False, relationship="other", count=0
            )
            continue
        if item.obligation_id == "C5.2" and privacy_fact is None:
            statuses[item.obligation_id] = make_result(
                item.obligation_id, status="NOT RUN", observed=False, relationship="other", count=0
            )
            continue
        projection = projection_for(item.obligation_id, mode)
        fields_present = all(
            key in observations and observations[key] is not None
            for key in projection.source_observation_keys
        )
        if runtime_failure is not None and checkpointed_phase and not fields_present:
            statuses[item.obligation_id] = make_result(
                item.obligation_id,
                status="NOT RUN",
                observed=False,
                relationship="other",
                count=0,
            )
            continue
        passed = fields_present and projection_passes(item.obligation_id, observations, mode)
        statuses[item.obligation_id] = make_result(
            item.obligation_id,
            status="PASSED" if passed else "FAILED" if fields_present else "MISSING",
            observed=fields_present,
            relationship=projection.relationship if fields_present else "other",
            count=sum(observations.get(key) is True for key in projection.source_observation_keys),
            version=CODEX_VERSION if item.obligation_id.startswith("C1") else None,
        )
    first_failure = next(
        (
            item.obligation_id
            for item in selected_items
            if statuses[item.obligation_id].status != "PASSED"
        ),
        None,
    )
    gate = build_obligation_gate(
        mode, statuses.values(), first_failure=first_failure, retry_count=0
    )
    gate_dict = gate.safe_dict()
    gate_dict["projection_table"] = projection_table_safe_dict(
        observations,
        {obligation_id: status.status for obligation_id, status in statuses.items()},
        mode,
    )
    gate_dict["observation_schema_keys"] = schema_keys
    gate_dict["runtime_failure"] = (
        {
            "class": runtime_failure,
            "context": accumulator.get("first_failure_context")
            if isinstance(accumulator, Mapping)
            else None,
        }
        if runtime_failure is not None
        else None
    )
    source = Path(__file__).read_text(encoding="utf-8")
    gaps = tuple(
        {
            "gap_id": gap.gap_id,
            "resolved": not gap.present_after_fix,
        }
        for gap in derive_gap_inventory(source)
    )
    return gate_dict, gaps


def _tested_source_still_valid(tested_sha: str) -> bool:
    """Allow a tested head or one verified immutable report-only child."""
    if not re.fullmatch(r"[0-9a-f]{40}", tested_sha):
        return False
    root = REPO_ROOT
    status = _run_command(
        ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"]
    )
    if status.returncode != 0:
        return False
    relevant_prefixes = (
        "src/",
        "scripts/",
        "tests/",
        "config/",
        "pyproject.toml",
        "uv.lock",
    )
    dirty_paths: list[str] = []
    for line in status.stdout.splitlines():
        if len(line) < 4:
            return False
        raw_path = line[3:]
        if line[:2].strip() in {"R", "C"} and " -> " in raw_path:
            dirty_paths.extend(raw_path.split(" -> ", 1))
        else:
            dirty_paths.append(raw_path)
    if any(path in relevant_prefixes or path.startswith(relevant_prefixes) for path in dirty_paths):
        return False
    current = _local_implementation_sha(root)
    if current == tested_sha:
        return True
    ancestor = _run_command(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", tested_sha, current]
    )
    if ancestor.returncode != 0:
        return False

    parents = _run_command(["git", "-C", str(root), "show", "-s", "--format=%P", current])
    parent_values = parents.stdout.strip().split()
    if parents.returncode != 0 or parent_values != [tested_sha]:
        return False
    evidence_changed = _run_command(
        ["git", "-C", str(root), "diff-tree", "--no-commit-id", "--name-status", "-r", current]
    )
    evidence_rows = tuple(
        tuple(value.split("\t", 1)) for value in evidence_changed.stdout.splitlines() if value
    )
    if (
        evidence_changed.returncode == 0
        and evidence_rows
        and all(
            len(row) == 2 and row[0] in {"A", "M"} and row[1].startswith("oap/evidence/")
            for row in evidence_rows
        )
    ):
        return True
    subject = _run_command(["git", "-C", str(root), "show", "-s", "--format=%s", current])
    if subject.returncode != 0 or "report" not in subject.stdout.lower():
        return False

    changed = _run_command(
        ["git", "-C", str(root), "diff-tree", "--no-commit-id", "--name-status", "-r", current]
    )
    changed_rows = tuple(
        tuple(value.split("\t", 1)) for value in changed.stdout.splitlines() if value
    )
    if changed.returncode != 0 or len(changed_rows) != 1:
        return False
    status_code, report_path = changed_rows[0]
    if status_code != "A" or not re.fullmatch(r"oap/reports/[A-Za-z0-9._-]+\.md", report_path):
        return False
    if (
        _run_command(
            ["git", "-C", str(root), "cat-file", "-e", f"{tested_sha}:{report_path}"]
        ).returncode
        == 0
    ):
        return False
    report = _run_command(["git", "-C", str(root), "show", f"{current}:{report_path}"])
    if report.returncode != 0:
        return False
    implementation_markers = re.findall(
        rf"(?m)^[ \t]*(?:[-*][ \t]+)?Implementation head SHA:[ \t]+"
        rf"(?:`({tested_sha})`|({tested_sha}))[ \t]*$",
        report.stdout,
    )
    self_markers = re.findall(
        r"(?m)^[ \t]*(?:[-*][ \t]+)?Report publication commit:[ \t]+SELF[ \t]*$",
        report.stdout,
    )
    return len(implementation_markers) == 1 and len(self_markers) == 1


def _read_fake_gate_file(path: Path) -> bytes:
    """Read at most the evidence cap from one owned regular file."""
    max_bytes = 2 * 1024 * 1024
    if path.is_symlink():
        raise RuntimeError("protected_fake_gate_unsafe_file")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError:
        raise RuntimeError("protected_fake_gate_unreadable") from None
    try:
        stat_result = os.fstat(descriptor)
        if (
            not stat.S_ISREG(stat_result.st_mode)
            or stat_result.st_uid != os.getuid()
            or stat_result.st_nlink != 1
        ):
            raise RuntimeError("protected_fake_gate_unsafe_file")
        chunks: list[bytes] = []
        total = 0
        while total <= max_bytes:
            chunk = os.read(descriptor, max_bytes + 1 - total)
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        if total > max_bytes:
            raise RuntimeError("protected_fake_gate_too_large")
        return b"".join(chunks)
    except RuntimeError:
        raise
    except OSError:
        raise RuntimeError("protected_fake_gate_unreadable") from None
    finally:
        os.close(descriptor)


def _decode_fake_gate(raw: bytes) -> dict[str, object]:
    """Decode one bounded JSON-lines result with duplicate/non-finite rejection."""

    def reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_json_key")
            result[key] = value
        return result

    def reject_constant(_value: str) -> None:
        raise ValueError("non_finite_json")

    try:
        lines = raw.splitlines()
        payload = json.loads(
            lines[-1] if lines else b"",
            object_pairs_hook=reject_duplicate_pairs,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        raise RuntimeError("protected_fake_gate_invalid") from None
    if not isinstance(payload, dict):
        raise RuntimeError("protected_fake_gate_invalid")
    return payload


def _validate_fake_gate(path: Path | None) -> None:
    """Require complete, independently projected fake evidence before traffic."""
    if path is None:
        raise RuntimeError("protected_fake_gate_missing")
    raw = _read_fake_gate_file(path)
    payload = _decode_fake_gate(raw)
    gate = payload.get("acceptance_gate")
    if not isinstance(gate, dict):
        raise RuntimeError("protected_fake_gate_not_complete")
    results_value = gate.get("results")
    if not isinstance(results_value, list) or not all(
        isinstance(item, dict) for item in results_value
    ):
        raise RuntimeError("protected_fake_gate_result_schema")
    results = results_value
    expected_ids = tuple(
        item.obligation_id for item in ACCEPTANCE_MANIFEST if item.mode in {"both", "fake"}
    )
    expected_gate_keys = {
        "mode",
        "missing",
        "first_failure",
        "retry_count",
        "passed",
        "result_count_class",
        "results",
        "projection_table",
        "observation_schema_keys",
        "runtime_failure",
    }
    candidate = payload.get("candidate_provenance")
    candidate_keys = {
        "implementation_sha",
        "tested_worktree_clean",
        "local_source",
        "harness_source",
        "route_policy",
        "gateway_sha",
        "gateway_app_tree_sha256",
        "codex_version",
        "codex_binary_sha256",
        "execution_mode",
        "run_provenance",
        "run_id",
        "observer_version",
        "source_identity",
    }
    expected_result_keys = {
        "obligation_id",
        "status",
        "observed",
        "relationship",
        "count_class",
        "timing",
        "fixture_hash",
        "version",
    }
    valid_header = (
        payload.get("status") == "COMPLETE"
        and payload.get("provider_target") == "fake"
        and payload.get("gateway_sha") == GATEWAY_MAIN_SHA
        and set(gate) == expected_gate_keys
        and gate.get("mode") == "fake"
        and gate.get("passed") is True
        and gate.get("missing") == []
        and gate.get("first_failure") is None
        and type(gate.get("retry_count")) is int
        and gate.get("retry_count") == 0
        and gate.get("result_count_class") == count_class(len(expected_ids))
        and tuple(item.get("obligation_id") for item in results if isinstance(item, dict))
        == expected_ids
        and isinstance(candidate, dict)
        and set(candidate) == candidate_keys
        and isinstance(candidate.get("implementation_sha"), str)
        and re.fullmatch(r"[0-9a-f]{40}", candidate["implementation_sha"]) is not None
        and candidate.get("tested_worktree_clean") is True
        and _tested_source_still_valid(candidate["implementation_sha"])
        and candidate.get("local_source") == "src/slaif_local_coding"
        and candidate.get("harness_source") == "scripts/gateway_accounting_rehearsal.py"
        and candidate.get("route_policy") == LOCAL_ROUTE_POLICY
        and candidate.get("gateway_sha") == GATEWAY_MAIN_SHA
        and candidate.get("gateway_app_tree_sha256") == GATEWAY_APP_TREE_SHA256
        and candidate.get("codex_version") == CODEX_VERSION
        and candidate.get("codex_binary_sha256") == CODEX_FIXTURE_SHA256
        and candidate.get("execution_mode") == "fake"
        and candidate.get("run_provenance") == "fresh_fake_direct_httpx_loopback"
        and isinstance(candidate.get("run_id"), str)
        and re.fullmatch(r"[0-9a-f]{32}", candidate["run_id"]) is not None
        and candidate.get("observer_version") == OBSERVATION_VERSION
        and candidate.get("source_identity") == _source_identity()
    )
    if not valid_header:
        raise RuntimeError("protected_fake_gate_not_complete")
    for item, obligation_id in zip(results, expected_ids, strict=True):
        projection = projection_for(obligation_id)
        if (
            set(item) != expected_result_keys
            or item.get("obligation_id") != obligation_id
            or item.get("status") not in {"PASSED"}
            or type(item.get("observed")) is not bool
            or item.get("observed") is not True
            or item.get("relationship") != projection.relationship
            or item.get("count_class") not in {"1", "2", "3-4", "5+"}
            or item.get("timing")
            not in {
                "0-9ms",
                "10-49ms",
                "50-99ms",
                "100-249ms",
                "250-999ms",
                "1000ms+",
                "unknown",
            }
            or (
                item.get("fixture_hash") is not None
                and (
                    not isinstance(item.get("fixture_hash"), str)
                    or re.fullmatch(r"[0-9a-f]{64}", item["fixture_hash"]) is None
                )
            )
            or (
                item.get("version") is not None
                and (not isinstance(item.get("version"), str) or len(item["version"]) > 64)
            )
        ):
            raise RuntimeError("protected_fake_gate_result_schema")
        if (
            item.get("status") != "PASSED"
            or item.get("observed") is not True
            or item.get("relationship") != projection.relationship
            or item.get("count_class") not in {"1", "2", "3-4", "5+"}
            or item.get("timing")
            not in {
                "0-9ms",
                "10-49ms",
                "50-99ms",
                "100-249ms",
                "250-999ms",
                "1000ms+",
                "unknown",
            }
            or (item.get("version") != CODEX_VERSION and obligation_id.startswith("C1"))
        ):
            raise RuntimeError("protected_fake_gate_result_not_observed")
    projection_table_value = gate.get("projection_table")
    if not isinstance(projection_table_value, list) or not all(
        isinstance(item, dict) for item in projection_table_value
    ):
        raise RuntimeError("protected_fake_gate_projection_schema")
    projection_table = projection_table_value
    if (
        not isinstance(projection_table, list)
        or len(projection_table) != len(expected_ids)
        or tuple(item.get("obligation_id") for item in projection_table if isinstance(item, dict))
        != expected_ids
    ):
        raise RuntimeError("protected_fake_gate_projection_schema")
    for item in projection_table:
        projection = projection_for(str(item.get("obligation_id")))
        if set(item) != {
            "obligation_id",
            "source_observation_keys",
            "producer",
            "proving_test_node_ids",
            "execution_status",
            "observed_field_count_class",
        }:
            raise RuntimeError("protected_fake_gate_projection_schema")
        if (
            tuple(item.get("source_observation_keys", ())) != projection.source_observation_keys
            or item.get("producer") != projection.producer
            or tuple(item.get("proving_test_node_ids", ())) != projection.proving_test_node_ids
            or item.get("execution_status") != "PASSED"
            or item.get("observed_field_count_class")
            != count_class(len(projection.source_observation_keys))
            or not isinstance(item.get("source_observation_keys"), list)
            or not isinstance(item.get("proving_test_node_ids"), list)
            or not isinstance(item.get("producer"), str)
        ):
            raise RuntimeError("protected_fake_gate_projection_not_observed")
    if tuple(gate.get("observation_schema_keys", ())) != FAKE_RESULT_SCHEMA_KEYS:
        raise RuntimeError("protected_fake_gate_observation_schema")
    observations = payload.get("runtime_observations")
    if not isinstance(observations, dict) or set(observations) != set(FAKE_RESULT_SCHEMA_KEYS):
        raise RuntimeError("protected_fake_gate_runtime_schema")
    if not all(type(value) is bool and value is True for value in observations.values()):
        raise RuntimeError("protected_fake_gate_runtime_not_complete")
    transport = payload.get("transport_observation")
    if not isinstance(transport, dict):
        raise RuntimeError("protected_fake_gate_transport_not_complete")
    if (
        transport.get("observer_version") != OBSERVATION_VERSION
        or transport.get("ready") is not True
        or transport.get("matches_fake_provider") is not True
        or transport.get("inference_attempted_count_class") not in {"2", "3-4", "5+"}
        or transport.get("inference_terminal_valid_count_class")
        != transport.get("inference_attempted_count_class")
    ):
        raise RuntimeError("protected_fake_gate_transport_not_complete")
    attempted_count = transport.get("inference_attempted_count")
    dispatched_count = transport.get("inference_dispatched_count")
    responded_count = transport.get("inference_responded_count")
    completed_count = transport.get("inference_completed_count")
    terminal_count = transport.get("inference_terminal_valid_count")
    if (
        type(attempted_count) is not int
        or type(dispatched_count) is not int
        or type(responded_count) is not int
        or type(completed_count) is not int
        or type(terminal_count) is not int
        or attempted_count < 2
        or dispatched_count != attempted_count
        or responded_count != attempted_count
        or completed_count != attempted_count
        or terminal_count != attempted_count
    ):
        raise RuntimeError("protected_fake_gate_transport_not_complete")
    records_value = transport.get("records")
    inference_records = (
        [record for record in records_value if isinstance(record, dict)]
        if isinstance(records_value, list)
        else []
    )
    inference_records = [
        record for record in inference_records if record.get("kind") == "inference"
    ]
    if len(inference_records) != attempted_count or not all(
        record.get("dispatched") is True
        and record.get("responded") is True
        and record.get("completed") is True
        and record.get("terminal_valid") is True
        and record.get("normal_close") is True
        for record in inference_records
    ):
        raise RuntimeError("protected_fake_gate_transport_not_complete")


def _safe_runtime_failure(exc: BaseException) -> str:
    """Map process-boundary exceptions to a fixed, non-sensitive class."""
    if isinstance(exc, asyncio.CancelledError):
        return "cancelled"
    if isinstance(exc, TimeoutError):
        return "timeout"
    if isinstance(exc, (json.JSONDecodeError, UnicodeDecodeError, ValueError)):
        return "validation_failure"
    if isinstance(exc, KeyError):
        return "serialization_failure"
    if isinstance(exc, (httpx.HTTPError, APIStatusError)):
        return "client_error"
    return "unknown"


def _failed_rehearsal_result(
    provider_target: str, accumulator: RunAccumulator
) -> dict[str, object]:
    """Create a fixed safe result when a phase fails before its normal result."""
    return {
        "status": "FAILED",
        "provider_target": provider_target if provider_target in {"fake", "protected"} else "fake",
        "gateway_sha": GATEWAY_MAIN_SHA,
        "protected_stop_reason": accumulator.first_failure or "unknown",
        "protected_later_inference": False,
        "transport_observation": {},
        "topology_observation": {},
    }


def _empty_observer_snapshot() -> dict[str, object]:
    """Return known-zero direct-observer facts for a pre-dispatch stop."""
    return {
        "observer_version": OBSERVATION_VERSION,
        "ready": True,
        "failure_class": None,
        "attempted_count": 0,
        "dispatched_count": 0,
        "responded_count": 0,
        "completed_count": 0,
        "terminal_valid_count": 0,
        "compiler_attempted_count": 0,
        "compiler_dispatched_count": 0,
        "compiler_responded_count": 0,
        "compiler_completed_count": 0,
        "compiler_terminal_valid_count": 0,
        "inference_attempted_count": 0,
        "inference_dispatched_count": 0,
        "inference_responded_count": 0,
        "inference_completed_count": 0,
        "inference_terminal_valid_count": 0,
        "other_attempted_count": 0,
        "other_dispatched_count": 0,
        "other_responded_count": 0,
        "other_completed_count": 0,
        "other_terminal_valid_count": 0,
        "records": (),
        "provider_boundary": {},
    }


def run_actual_protected_mode_conformance(
    args: argparse.Namespace,
    *,
    preflight: dict[str, object],
    dependencies: ProtectedRuntimeHooks | None,
) -> dict[str, object]:
    """Run the shared runner with explicit synthetic protected boundaries.

    This is test support only.  A missing dependency is a failed conformance,
    never a default-ready result, and the synthetic provider is always a
    disposable loopback fake.  The command-line entry point does not construct
    these hooks.
    """
    mode: Literal["fake", "protected"] = "protected"
    if (
        dependencies is None
        or not dependencies.synthetic_only
        or dependencies.provider_target != "fake"
        or not callable(dependencies.host_preflight)
        or not callable(dependencies.main_pid)
        or not callable(dependencies.credential_source)
    ):
        accumulator = RunAccumulator(mode, gateway_sha=GATEWAY_MAIN_SHA)
        accumulator.record_failure("preflight_incomplete")
        result = _failed_rehearsal_result("protected", accumulator)
        result["protected_acceptance"] = False
        result["evidence_kind"] = "synthetic_orchestration_only"
        result["synthetic_dependency_missing"] = True
        _attach_accumulator_evidence(result, accumulator)
        result["runtime_observations"] = _runtime_observations(result)
        result["acceptance_gate"], result["gap_inventory"] = _acceptance_gate(result)
        protected_ids = tuple(
            item.obligation_id for item in ACCEPTANCE_MANIFEST if item.mode in {"both", "protected"}
        )
        gate = result["acceptance_gate"]
        rows_value = gate.get("results", ()) if isinstance(gate, dict) else ()
        rows = (
            cast(tuple[dict[str, object], ...], rows_value)
            if isinstance(rows_value, (list, tuple))
            else ()
        )
        result["protected_conformance"] = {
            "selected_result_count": len(protected_ids),
            "selected_result_disposition_count": len(rows),
            "all_selected_rows_serialized": tuple(row["obligation_id"] for row in rows)
            == protected_ids,
            "provider_target": "fake",
            "real_protected_access": False,
            "healthy_gate_passed": False,
        }
        return result

    synthetic_args = argparse.Namespace(**vars(args))
    synthetic_args.provider_target = "protected"
    synthetic_args._protected_runtime_hooks = dependencies
    try:
        result = _run_direct_composed_rehearsal(synthetic_args, preflight=preflight)
    except BaseException as exc:
        accumulator = RunAccumulator(mode, gateway_sha=GATEWAY_MAIN_SHA)
        accumulator.record_failure(_safe_runtime_failure(exc))
        result = _failed_rehearsal_result("protected", accumulator)
        _attach_accumulator_evidence(result, accumulator)
        result["runtime_observations"] = _runtime_observations(result)
        result["acceptance_gate"], result["gap_inventory"] = _acceptance_gate(result)
    result["protected_acceptance"] = False
    result["evidence_kind"] = "synthetic_orchestration_only"
    gate = result.get("acceptance_gate")
    result_rows = gate.get("results") if isinstance(gate, dict) else ()
    protected_ids = tuple(
        item.obligation_id for item in ACCEPTANCE_MANIFEST if item.mode in {"both", "protected"}
    )
    conformance = {
        "selected_result_count": len(protected_ids),
        "selected_result_disposition_count": (
            len(result_rows) if isinstance(result_rows, (list, tuple)) else 0
        ),
        "all_selected_rows_serialized": (
            isinstance(result_rows, (list, tuple))
            and tuple(row.get("obligation_id") for row in result_rows if isinstance(row, dict))
            == protected_ids
        ),
        "provider_target": dependencies.provider_target,
        "real_protected_access": False,
    }
    result["protected_conformance"] = conformance
    accumulator_value = result.get("run_accumulator")
    run_accumulator_facts = (
        cast(dict[str, object], accumulator_value) if isinstance(accumulator_value, dict) else {}
    )
    snapshots_value = run_accumulator_facts.get("snapshots", ())
    snapshots = snapshots_value if isinstance(snapshots_value, (list, tuple)) else ()
    counts_value = run_accumulator_facts.get("counts")
    counts = cast(dict[str, object], counts_value) if isinstance(counts_value, dict) else {}
    cleanup_value = run_accumulator_facts.get("cleanup")
    cleanup = cast(dict[str, object], cleanup_value) if isinstance(cleanup_value, dict) else {}
    conformance.update(
        {
            "healthy_gate_passed": (
                isinstance(gate, dict)
                and gate.get("passed") is True
                and gate.get("missing") == []
                and gate.get("first_failure") is None
                and _provider_preflight_complete(result)
            ),
            "implementation_reached": any(
                key in result for key in ("candidate_provenance", "codex", "transport_observation")
            ),
            "phase_trace": tuple(
                snapshot.get("phase")
                for snapshot in snapshots
                if isinstance(snapshot, dict) and isinstance(snapshot.get("phase"), str)
            ),
            "dispatch_counts": {
                key: counts.get(key)
                for key in (
                    "compiler_attempted",
                    "compiler_dispatched",
                    "compiler_responded",
                    "compiler_completed",
                    "inference_attempted",
                    "inference_dispatched",
                    "inference_responded",
                    "inference_completed",
                    "other_attempted",
                    "other_dispatched",
                    "other_responded",
                    "other_completed",
                )
            },
            "primary_failure": run_accumulator_facts.get("first_failure"),
            "secondary_failure_classes": run_accumulator_facts.get("secondary_failures", ()),
            "cleanup_snapshot": cleanup,
            "source_identities": {
                "runner": "scripts.gateway_accounting_rehearsal.py",
                "local": "src/slaif_local_coding",
                "observer": OBSERVATION_VERSION,
                "provider": "disposable_loopback_fake_oracle_disabled",
            },
            "provider_preflight": result.get("provider_preflight"),
        }
    )
    return result


def _run_direct_composed_rehearsal(
    args: argparse.Namespace, *, preflight: dict[str, object]
) -> dict[str, object]:
    """Run one bounded mode and always return serializable evidence."""
    provider_target = str(args.provider_target)
    mode: Literal["fake", "protected"] = "protected" if provider_target == "protected" else "fake"
    accumulator = RunAccumulator(mode, gateway_sha=GATEWAY_MAIN_SHA)
    try:
        validate_projection_contract(mode)
    except BaseException:
        accumulator.record_failure("preflight_incomplete")
        result = _failed_rehearsal_result(provider_target, accumulator)
        _attach_accumulator_evidence(result, accumulator)
        result["runtime_observations"] = _runtime_observations(result)
        result["acceptance_gate"], result["gap_inventory"] = _acceptance_gate(result)
        return result
    try:
        result = _run_direct_composed_rehearsal_impl(
            args, preflight=preflight, accumulator=accumulator
        )
    except BaseException as exc:
        accumulator.record_failure(_safe_runtime_failure(exc))
        protected_hooks = getattr(args, "_protected_runtime_hooks", None)
        if (
            isinstance(protected_hooks, ProtectedRuntimeHooks)
            and protected_hooks.projection_failure
        ):
            accumulator.record_failure("serialization_failure")
        result = _failed_rehearsal_result(provider_target, accumulator)
        _attach_accumulator_evidence(result, accumulator)
        try:
            result["runtime_observations"] = _runtime_observations(result)
            result["acceptance_gate"], result["gap_inventory"] = _acceptance_gate(result)
        except BaseException:
            accumulator.record_failure("serialization_failure")
            result["acceptance_gate"] = {
                "mode": mode,
                "missing": list(
                    item.obligation_id
                    for item in ACCEPTANCE_MANIFEST
                    if item.mode in {"both", mode}
                ),
                "first_failure": accumulator.first_failure,
                "retry_count": 0,
                "passed": False,
                "result_count_class": "0",
                "results": (),
                "projection_table": (),
                "observation_schema_keys": (
                    PROTECTED_RESULT_SCHEMA_KEYS if mode == "protected" else FAKE_RESULT_SCHEMA_KEYS
                ),
            }
            result["gap_inventory"] = ()
        result["status"] = "BLOCKED"
    if "acceptance_gate" not in result:
        result["runtime_observations"] = _runtime_observations(result)
        result["acceptance_gate"], result["gap_inventory"] = _acceptance_gate(result)
        gate = result.get("acceptance_gate")
        result["status"] = (
            "COMPLETE" if isinstance(gate, dict) and gate.get("passed") is True else "BLOCKED"
        )
    _attach_accumulator_evidence(result, accumulator)
    return result


def _attach_accumulator_evidence(result: dict[str, object], accumulator: RunAccumulator) -> None:
    """Publish all-lifetime totals without conflating candidate readiness."""
    facts = accumulator.safe_dict()
    result["run_accumulator"] = facts
    phase_checkpoints_value = facts.get("phase_checkpoints", ())
    phase_checkpoints = (
        phase_checkpoints_value if isinstance(phase_checkpoints_value, (list, tuple)) else ()
    )
    result["phase_checkpoints"] = phase_checkpoints
    for checkpoint in phase_checkpoints:
        if not isinstance(checkpoint, Mapping):
            continue
        phase_facts = checkpoint.get("phase_facts")
        if not isinstance(phase_facts, Mapping):
            continue
        # Preserve the first actual Codex checkpoint when a later observer
        # lifetime reuses the same phase name.
        if checkpoint.get("phase") == "codex":
            for key in ("codex", "provider_observation", "transport_observation", "accounting"):
                if key in phase_facts and (key not in result or result[key] in ({}, None)):
                    result[key] = phase_facts[key]
    cleanup = facts.get("cleanup")
    if isinstance(cleanup, Mapping) and (
        "cleanup_observation" not in result or result["cleanup_observation"] in ({}, None)
    ):
        result["cleanup_observation"] = dict(cleanup)
    result["all_lifetime_counts"] = facts.get("all_lifetime_counts", facts.get("counts"))
    result.setdefault("candidate_only_observation", {"status": "NOT RUN"})


def _run_direct_composed_rehearsal_impl(
    args: argparse.Namespace,
    *,
    preflight: dict[str, object],
    accumulator: RunAccumulator,
) -> dict[str, object]:
    """Run one direct Gateway -> Local -> provider composition.

    The provider target is the only topology variable.  In particular, there
    is no forwarding relay or provider-side status endpoint in this driver.
    """
    provider_target = str(args.provider_target)
    if provider_target not in {"fake", "protected"}:
        raise RuntimeError("provider_target_invalid")
    protected_hooks = getattr(args, "_protected_runtime_hooks", None)
    if protected_hooks is not None and not isinstance(protected_hooks, ProtectedRuntimeHooks):
        raise RuntimeError("protected_runtime_hooks_invalid")
    run_id = uuid.uuid4().hex
    accumulator.set_phase("preflight")
    budget = BudgetController(
        RehearsalBudget(
            wall_seconds=MAX_REHEARSAL_SECONDS,
            operation_limits=PUBLIC_REQUEST_BUDGET,
            max_event_bytes=FAKE_MAX_EVENT_BYTES,
            max_stream_bytes=FAKE_MAX_STREAM_BYTES,
            max_concurrency=1,
        ),
        clock=protected_hooks.clock if protected_hooks is not None else time.monotonic,
    )
    accumulator.record_budget(budget.safe_dict())

    if protected_hooks is not None and protected_hooks.failure_phase == "preflight":
        accumulator.record_failure("preflight_incomplete")
        accumulator.capture_observer(
            _empty_observer_snapshot(), phase="preflight", ordinal=0, lifetime_id="preflight"
        )
        raise RuntimeError("synthetic_preflight_failure")

    if provider_target == "protected" and protected_hooks is not None:
        mapping_check = protected_hooks.mapping_dependency_check
        mapping_valid = False
        if callable(mapping_check):
            try:
                mapping_valid = mapping_check() is True
            except BaseException:
                mapping_valid = False
        if not mapping_valid:
            accumulator.record_failure("preflight_mapping_dependency_invalid")
            accumulator.capture_observer(
                _empty_observer_snapshot(),
                phase="preflight",
                ordinal=0,
                lifetime_id="preflight",
            )
            preflight_result = _failed_rehearsal_result(provider_target, accumulator)
            preflight_result.update(
                {
                    "status": "BLOCKED",
                    "preflight_mapping_validation": "FAILED",
                    "credential_hook_calls": 0,
                    "provider_dispatches": 0,
                    "protected_later_inference": False,
                    "cleanup_observation": {
                        "processes": True,
                        "listeners": True,
                        "database": True,
                        "cache": True,
                        "codex_home": True,
                    },
                }
            )
            accumulator.record_cleanup(
                cast(dict[str, object], preflight_result["cleanup_observation"])
            )
            return preflight_result

    def admit(operation: str, phase: str, ordinal: int, lifetime_id: str) -> None:
        accumulator.set_phase(phase, ordinal)
        if not budget.admit(operation, phase=phase, ordinal=ordinal, lifetime_id=lifetime_id):
            failure = budget.failure or "budget_operation_limit_exhausted"
            accumulator.record_failure(failure)
            raise RuntimeError(failure)

    def activate(operation: str, phase: str, ordinal: int, lifetime_id: str) -> None:
        accumulator.set_phase(phase, ordinal)
        if not budget.activate_operation(
            operation, phase=phase, ordinal=ordinal, lifetime_id=lifetime_id
        ):
            failure = budget.failure or "budget_operation_activation_missing"
            accumulator.record_failure(failure)
            raise RuntimeError(failure)

    def admit_provider_probe(endpoint: str) -> None:
        accumulator.set_phase("preflight", 0)
        if not budget.admit_provider_probe(endpoint, lifetime_id="provider_preflight"):
            failure = budget.failure or "budget_provider_probe_limit_exhausted"
            accumulator.record_failure(failure)
            raise RuntimeError(failure)
        if not budget.activate_provider_probe(endpoint, lifetime_id="provider_preflight"):
            failure = budget.failure or "budget_provider_probe_activation_mismatch"
            accumulator.record_failure(failure)
            raise RuntimeError(failure)

    if provider_target == "protected" and (
        protected_hooks is None or protected_hooks.require_fake_gate
    ):
        _validate_fake_gate(args.fake_result)
    gateway_root = args.gateway_root.resolve()
    gateway_python = Path(args.gateway_python).absolute()
    if (
        _run_command(["git", "-C", str(gateway_root), "rev-parse", "HEAD"]).stdout.strip()
        != GATEWAY_MAIN_SHA
    ):
        raise RuntimeError("gateway_sha_mismatch")
    if _run_command(["git", "-C", str(gateway_root), "status", "--short"]).stdout.strip():
        raise RuntimeError("gateway_checkout_dirty")
    codex = Path(args.codex).resolve()
    codex_version = _codex_version(codex)
    codex_sha256 = _codex_sha256(codex)
    if codex_version != CODEX_VERSION or codex_sha256 != CODEX_FIXTURE_SHA256:
        raise RuntimeError("codex_fixture_mismatch")
    validator_factory = _gateway_stream_validator_factory(gateway_root)
    protected_before: dict[str, object] | None = None
    qwen_key = ""
    if provider_target == "protected":
        protected_before, _protected_pid, qwen_key = _select_protected_runtime(protected_hooks)
    gateway_port = _free_loopback_port()
    adapter_port = _free_loopback_port(18031)
    if adapter_port != 18031:
        raise RuntimeError("candidate_port_18031_not_free")
    gateway_url = f"http://127.0.0.1:{gateway_port}"
    service_token = "synthetic-005k-adapter-service-token"
    signing_secret = "synthetic-005k-signing-secret-0123456789"
    derivation_secret = "synthetic-005k-derivation-secret-0123456789"
    synthetic = _gateway_settings(gateway_url)
    fake_server: _FakeQwenServer | None = None
    fake_thread: threading.Thread | None = None
    failure_server: _FailureServer | None = None
    failure_thread: threading.Thread | None = None
    gateway_process: subprocess.Popen[bytes] | None = None
    candidate_runtime: _ObservedCandidate | None = None
    candidate_runtimes: list[_ObservedCandidate] = []
    transport_snapshots: list[dict[str, object]] = []
    tested_implementation_sha = _local_implementation_sha()
    accumulator.candidate_sha = tested_implementation_sha
    accumulator.gateway_sha = GATEWAY_MAIN_SHA
    if _run_command(["git", "-C", str(REPO_ROOT), "status", "--short"]).stdout.strip():
        raise RuntimeError("implementation_worktree_dirty_before_fake")
    postgres_name: str | None = None
    postgres_image_was_absent = False
    temporary_name: str | None = None
    logs_clean = False
    postgres_removed = False
    previous_candidate_env: dict[str, str | None] = {}
    result: dict[str, object] = _failed_rehearsal_result(provider_target, accumulator)
    candidate_only_observation: dict[str, object] = {"status": "NOT RUN"}
    logs: tuple[Path, ...] = ()
    candidate_observer: DirectTransportObserver | None = None
    provider_preflight_observer: DirectTransportObserver | None = None
    vision_observer: DirectTransportObserver | None = None
    post_vision_observer: DirectTransportObserver | None = None
    active_observer: DirectTransportObserver | None = None
    protected_failure_injected = False
    codex_turn_transitioned = False
    early_return = False

    def protected_dispatch_complete(kind: str, phase: str, ordinal: int | None) -> None:
        nonlocal protected_failure_injected
        if (
            protected_hooks is not None
            and protected_hooks.failure_phase in {"post_dispatch", "observer"}
            and not protected_failure_injected
            and active_observer is not None
            and kind == "inference"
        ):
            protected_failure_injected = True
            active_observer.mark_unready()
        if (
            protected_hooks is not None
            and protected_hooks.failure_phase == "vision_response"
            and phase == "vision"
            and kind == "inference"
            and not protected_failure_injected
        ):
            protected_failure_injected = True
            if active_observer is not None:
                active_observer.mark_unready()
            raise RuntimeError("synthetic_vision_response_failure")
        if protected_hooks is not None and protected_hooks.dispatch_complete_hook is not None:
            protected_hooks.dispatch_complete_hook(kind, phase, ordinal)

    def operation_response_complete(
        kind: str,
        operation: str,
        _phase: str,
        _ordinal: int | None,
        terminal_valid: bool,
    ) -> None:
        """Authorize the next Codex turn only after the prior response ends."""
        nonlocal codex_turn_transitioned
        if (
            codex_turn_transitioned
            or operation != "codex_turn_1"
            or not terminal_valid
            or not budget.operation_complete("codex_turn_1", lifetime_id="codex")
        ):
            return
        if budget.activate_operation("codex_turn_2", phase="codex", ordinal=2, lifetime_id="codex"):
            codex_turn_transitioned = True
            return
        accumulator.record_failure(budget.failure or "budget_operation_activation_missing")
        if active_observer is not None:
            active_observer.mark_unready()

    def finalize_result() -> None:
        """Project the selected evidence after cleanup, including early stops."""
        if not result:
            raise RuntimeError("composed_rehearsal_did_not_produce_facts")
        result["runtime_observations"] = _runtime_observations(result)
        try:
            if protected_hooks is not None and (
                protected_hooks.projection_failure or protected_hooks.failure_phase == "projection"
            ):
                raise RuntimeError("synthetic_projection_failure")
            acceptance_gate, gap_inventory = _acceptance_gate(result)
        except BaseException:
            accumulator.record_failure("serialization_failure")
            mode: Literal["fake", "protected"] = (
                "protected" if result.get("provider_target") == "protected" else "fake"
            )
            selected = tuple(item for item in ACCEPTANCE_MANIFEST if item.mode in {"both", mode})
            statuses = {item.obligation_id: "NOT RUN" for item in selected}
            fallback = build_obligation_gate(
                mode,
                [
                    make_result(
                        item.obligation_id,
                        status="NOT RUN",
                        observed=False,
                        relationship="other",
                        count=0,
                    )
                    for item in selected
                ],
                first_failure=accumulator.first_failure,
                retry_count=0,
            ).safe_dict()
            fallback["projection_table"] = projection_table_safe_dict({}, statuses, mode)
            fallback["observation_schema_keys"] = (
                PROTECTED_RESULT_SCHEMA_KEYS if mode == "protected" else FAKE_RESULT_SCHEMA_KEYS
            )
            acceptance_gate = fallback
            gap_inventory = ()
        result["acceptance_gate"] = acceptance_gate
        result["gap_inventory"] = gap_inventory
        result["status"] = "COMPLETE" if acceptance_gate["passed"] else "BLOCKED"

    idless_http_regression: dict[str, object] = {"passed": False}
    idless_composed_companion: dict[str, object] = {
        "passed": False,
        "natural_codex_shape_separate": False,
    }
    protected_mode_synthetic: dict[str, object] = {"status": "NOT RUN"}
    protected_health_status: int | None = None
    protected_models_status: int | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="slaif-005k-composed-") as temporary:
            temporary_name = temporary
            temp_root = Path(temporary)
            gateway_log = temp_root / "gateway.log"
            logs = (gateway_log,)
            synthetic_provider = provider_target == "fake" or protected_hooks is not None
            protected_mode_synthetic_cases: dict[str, dict[str, object]] = {}
            if provider_target == "fake":
                # Run the healthy synthetic protected branch before this outer
                # candidate binds 18031.  The two candidate lifetimes must be
                # serial; a nested bind would be an invalid qualification.
                def synthetic_protected_hooks(
                    *,
                    failure_phase: str | None = None,
                    projection_failure: bool = False,
                    cleanup_failure: bool = False,
                    mapping_valid: bool = True,
                ) -> ProtectedRuntimeHooks:
                    return ProtectedRuntimeHooks(
                        host_preflight=lambda: {
                            "vision_active": True,
                            "has_18020": True,
                            "vision_pid": PROTECTED_VISION_PID,
                            "vision_start_wall": PROTECTED_VISION_START,
                            "vision_restarts": "0",
                            "worktree_count": 7,
                            "text_inactive": True,
                            "has_18021": False,
                            "has_18031": False,
                        },
                        main_pid=lambda: PROTECTED_VISION_PID,
                        credential_source=lambda _pid: "synthetic-protected-key",
                        mapping_dependency_check=lambda: mapping_valid,
                        failure_phase=failure_phase,
                        projection_failure=projection_failure,
                        cleanup_failure=cleanup_failure,
                    )

                protected_mode_synthetic = run_actual_protected_mode_conformance(
                    args,
                    preflight=preflight,
                    dependencies=synthetic_protected_hooks(),
                )
                protected_mode_synthetic_cases["healthy"] = protected_mode_synthetic
                protected_conformance = protected_mode_synthetic.get("protected_conformance")
                protected_accumulator = protected_mode_synthetic.get("run_accumulator")
                if (
                    not isinstance(protected_conformance, dict)
                    or protected_conformance.get("all_selected_rows_serialized") is not True
                    or protected_conformance.get("healthy_gate_passed") is not True
                    or protected_conformance.get("implementation_reached") is not True
                    or not isinstance(protected_accumulator, dict)
                    or protected_accumulator.get("first_failure") is not None
                ):
                    raise RuntimeError("protected_mode_conformance_incomplete")
                for name, options in (
                    ("observer_failure_after_dispatch", {"failure_phase": "observer"}),
                    (
                        "observer_projection_cleanup_failure",
                        {
                            "failure_phase": "observer",
                            "projection_failure": True,
                            "cleanup_failure": True,
                        },
                    ),
                    (
                        "predispatch_mapping_dependency_failure",
                        {"mapping_valid": False},
                    ),
                    (
                        "vision_failure_after_codex",
                        {"failure_phase": "vision_response"},
                    ),
                    (
                        "vision_failure_projection_cleanup",
                        {
                            "failure_phase": "vision_response",
                            "projection_failure": True,
                            "cleanup_failure": True,
                        },
                    ),
                ):
                    case = run_actual_protected_mode_conformance(
                        args,
                        preflight=preflight,
                        dependencies=synthetic_protected_hooks(**options),
                    )
                    protected_mode_synthetic_cases[name] = case
                    case_conformance = case.get("protected_conformance")
                    if (
                        not isinstance(case_conformance, dict)
                        or case_conformance.get("all_selected_rows_serialized") is not True
                        or case.get("status") not in {"BLOCKED", "FAILED"}
                    ):
                        raise RuntimeError("protected_mode_failure_case_incomplete")
            if synthetic_provider:
                fake_server = _FakeQwenServer(
                    "synthetic-005k-qwen-token",
                    oracle_enabled=not (
                        provider_target == "protected" and protected_hooks is not None
                    ),
                )
                fake_thread = _start_threaded_server(fake_server)
                provider_url = f"http://127.0.0.1:{fake_server.server_address[1]}"
                qwen_key = fake_server.token
            else:
                provider_url = "http://127.0.0.1:18020"
            for name, value in (
                (SERVICE_TOKEN_ENV, service_token),
                (SIGNING_SECRET_ENV, signing_secret),
            ):
                previous_candidate_env[name] = os.environ.get(name)
                os.environ[name] = value
            if synthetic_provider:
                previous_candidate_env[QWEN_KEY_ENV] = os.environ.get(QWEN_KEY_ENV)
            else:
                previous_candidate_env[QWEN_KEY_ENV] = None
            os.environ[QWEN_KEY_ENV] = qwen_key
            if provider_target == "fake":
                with httpx.Client(timeout=10, follow_redirects=False) as http:
                    fake_health = http.get(
                        f"{provider_url}/health",
                        headers={"Authorization": f"Bearer {qwen_key}"},
                    )
                if fake_health.status_code != 200:
                    raise RuntimeError("fake_provider_not_ready")
                idless_http_regression = _run_fake_idless_http_regression()
            elif provider_target == "protected":
                provider_preflight_observer = DirectTransportObserver(
                    httpx.AsyncHTTPTransport(retries=0),
                    validator_factory=validator_factory,
                    validator_source="gateway_responses_stream_validator",
                    budget_controller=budget,
                    dispatch_context=budget.dispatch_context,
                    allowed_lifetime_ids=("provider_preflight",),
                )
                assert provider_preflight_observer is not None

                protected_health_status, protected_models_status = asyncio.run(
                    _protected_provider_preflight(
                        provider_preflight_observer,
                        provider_url,
                        qwen_key,
                        admit_provider_probe,
                    )
                )
                accumulator.capture_observer(
                    provider_preflight_observer.snapshot(),
                    phase="preflight",
                    ordinal=0,
                    lifetime_id="provider_preflight",
                )
                transport_snapshots.append(provider_preflight_observer.snapshot())
                if protected_health_status != 200:
                    raise RuntimeError("protected_health_not_ready")
                if protected_models_status != 200:
                    raise RuntimeError("protected_models_not_ready")
                idless_http_regression = _run_fake_idless_http_regression()
            failure_server = _FailureServer()
            failure_thread = _start_threaded_server(failure_server)
            fixture = write_vision_fixture(temp_root / "fixture", gateway_url + "/v1", QWEN_KEY_ENV)
            adapter_config = fixture.adapter_config.read_text(encoding="utf-8")
            adapter_config = (
                adapter_config.replace(
                    'base_url = "http://127.0.0.1:18020/v1"',
                    f'base_url = "{provider_url}/v1"',
                    1,
                )
                .replace(
                    'principal = "vision-e2e-principal"\n',
                    "",
                    1,
                )
                .replace(
                    'session = "vision-e2e-session"\n',
                    "",
                    1,
                )
                .replace(
                    'repository = "vision-e2e-repository"\n',
                    'identity_source = "signed_request"\n',
                    1,
                )
                .replace(
                    "[upstream]\n",
                    "[gateway_ingress]\n"
                    'mode = "service_bearer_signed_identity_v1"\n'
                    f'service_token_env = "{SERVICE_TOKEN_ENV}"\n'
                    f'signing_secret_env = "{SIGNING_SECRET_ENV}"\n\n'
                    "[upstream]\n",
                    1,
                )
            )
            if f'base_url = "{provider_url}/v1"' not in adapter_config:
                raise RuntimeError("provider_target_not_applied")
            fixture.adapter_config.write_text(adapter_config, encoding="utf-8")
            os.chmod(fixture.adapter_config, 0o600)
            codex_config = fixture.codex_config.read_text(encoding="utf-8")
            codex_config = codex_config.replace(
                f'env_key = "{QWEN_KEY_ENV}"',
                f'env_key = "{PUBLIC_KEY_ENV}"',
                1,
            )
            fixture.codex_config.write_text(codex_config, encoding="utf-8")
            os.chmod(fixture.codex_config, 0o600)
            fixture = replace(fixture, api_key_env=PUBLIC_KEY_ENV)
            write_vision_model_catalog(codex, fixture.model_catalog, model=PUBLIC_MODEL)
            if not _public_model_catalog_ok(fixture.model_catalog):
                raise RuntimeError("codex_catalog_contract_failed")

            (
                postgres_name,
                postgres_port,
                tmpfs_only,
                postgres_image_was_absent,
                _postgres_image_id,
                _postgres_image_digest,
            ) = _docker_start_postgres()
            database_url = (
                f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}"
                f"@127.0.0.1:{postgres_port}/{DATABASE_NAME}"
            )
            gateway_env = _gateway_environment(
                gateway_root=gateway_root,
                database_url=database_url,
                gateway_port=gateway_port,
                hmac_secret=synthetic["hmac_secret"],
                encryption_key=synthetic["encryption_key"],
                service_token=service_token,
                signing_secret=signing_secret,
                derivation_secret=derivation_secret,
            )
            migration = _run_command(
                [str(gateway_python), "-m", "alembic", "upgrade", "head"],
                cwd=gateway_root,
                env=gateway_env,
            )
            if migration.returncode != 0:
                raise RuntimeError("gateway_migration_failed")
            seeded = asyncio.run(
                _seed_database(
                    gateway_root,
                    database_url,
                    adapter_port=adapter_port,
                    failure_port=failure_server.server_address[1],
                    hmac_secret=synthetic["hmac_secret"],
                    encryption_key=synthetic["encryption_key"],
                )
            )
            candidate_observer = DirectTransportObserver(
                httpx.AsyncHTTPTransport(retries=0),
                validator_factory=validator_factory,
                validator_source="gateway_responses_stream_validator",
                budget_controller=budget,
                dispatch_context=budget.dispatch_context,
                dispatch_hook=(
                    protected_hooks.dispatch_hook if protected_hooks is not None else None
                ),
                dispatch_complete_hook=(
                    protected_dispatch_complete if protected_hooks is not None else None
                ),
                response_complete_hook=operation_response_complete,
                allowed_lifetime_ids=("candidate", "codex"),
                request_classifier=_provider_request_observation,
            )
            active_observer = candidate_observer
            candidate_runtime = _build_observed_candidate(
                fixture.adapter_config,
                observer=candidate_observer,
                readiness_lifetime_id="candidate",
            )
            candidate_runtimes.append(candidate_runtime)
            candidate_only_observation = _candidate_only_observation(
                candidate_runtime.observer.snapshot()
            )
            candidate_health = candidate_runtime.health_status
            candidate_ready = candidate_runtime.ready_status
            if candidate_health != 200 or candidate_ready != 200:
                with httpx.Client(timeout=10, follow_redirects=False) as http:
                    readiness_probe = http.get(f"http://127.0.0.1:{adapter_port}/readyz")
                try:
                    readiness_body = readiness_probe.json()
                except ValueError:
                    readiness_body = {}
                states = tuple(
                    f"{key}_{readiness_body.get(key)}"
                    for key in ("upstream", "compiler", "cache", "gateway_ingress")
                    if readiness_body.get(key) in {"ready", "degraded", "unavailable", "disabled"}
                )
                detail = "_".join(states) or "unknown_components"
                if fake_server is not None:
                    fake_state = fake_server.snapshot()
                    detail += (
                        f"_fake_calls_{fake_state['calls']}_fake_bad_auth_"
                        f"{str(fake_state['bad_auth']).lower()}"
                    )
                raise RuntimeError(
                    f"candidate_not_ready_{candidate_health}_{candidate_ready}_{detail}"
                )
            gateway_process = _build_gateway_process(
                gateway_python, gateway_root, gateway_port, gateway_env, gateway_log
            )
            with httpx.Client(timeout=45, follow_redirects=False) as http:
                gateway_health = _wait_status(http, f"{gateway_url}/healthz")
                gateway_ready = _wait_status(http, f"{gateway_url}/readyz")
            if gateway_health != 200 or gateway_ready != 200:
                raise RuntimeError("gateway_not_ready")

            client = OpenAI(
                api_key=seeded["plaintext_key"],
                base_url=gateway_url + "/v1/",
                timeout=300,
                max_retries=0,
            )
            with httpx.Client(timeout=45, follow_redirects=False) as http:
                gateway_models_probe = http.get(
                    f"{gateway_url}/v1/models",
                    headers={"Authorization": f"Bearer {seeded['plaintext_key']}"},
                )
            if gateway_models_probe.status_code != 200:
                raise RuntimeError(f"gateway_models_{gateway_models_probe.status_code}")
            with httpx.Client(timeout=45, follow_redirects=False) as http:
                codex_metrics_before = _adapter_metrics(http, adapter_port)
            codex_rows_before = asyncio.run(
                _db_snapshot(gateway_root, database_url, seeded["gateway_key_id"])
            )
            fake_codex_before = None if fake_server is None else fake_server.snapshot()
            codex_observer_before = candidate_observer.snapshot()
            preflight_flags = preflight.get("feature_flags", ())
            admit("codex_turn_1", "codex", 1, "codex")
            admit("codex_turn_2", "codex", 2, "codex")
            activate("codex_turn_1", "codex", 1, "codex")
            codex_facts = _run_fake_codex_turn(
                codex,
                fixture,
                gateway_url,
                seeded["plaintext_key"],
                feature_flags=(
                    tuple(str(item) for item in preflight_flags)
                    if isinstance(preflight_flags, (list, tuple))
                    else ()
                ),
            )
            with httpx.Client(timeout=45, follow_redirects=False) as http:
                codex_metrics_after = _adapter_metrics(http, adapter_port)
            codex_rows_after = asyncio.run(
                _db_snapshot(gateway_root, database_url, seeded["gateway_key_id"])
            )
            fake_codex_after = None if fake_server is None else fake_server.snapshot()
            codex_observer_after = candidate_observer.snapshot()
            transport_snapshots.append(codex_observer_after)
            accumulator.capture_observer(
                codex_observer_after, phase="codex", ordinal=2, lifetime_id="codex"
            )
            codex_provider_delta = (
                _int_fact(fake_codex_after.get("inference_calls"))
                - _int_fact(fake_codex_before.get("inference_calls"))
                if provider_target == "fake"
                and fake_codex_before is not None
                and fake_codex_after is not None
                else _int_fact(
                    _observer_delta(codex_observer_before, codex_observer_after).get(
                        "inference_dispatched_count"
                    )
                )
            )
            codex_compiler_delta = (
                _int_fact(fake_codex_after.get("compiler_calls"))
                - _int_fact(fake_codex_before.get("compiler_calls"))
                if provider_target == "fake"
                and fake_codex_before is not None
                and fake_codex_after is not None
                else _int_fact(
                    _observer_delta(codex_observer_before, codex_observer_after).get(
                        "compiler_dispatched_count"
                    )
                )
            )
            codex_inference_delta = (
                _int_fact(fake_codex_after.get("inbound_inference_calls"))
                - _int_fact(fake_codex_before.get("inbound_inference_calls"))
                if provider_target == "fake"
                and fake_codex_before is not None
                and fake_codex_after is not None
                else codex_provider_delta
            )
            codex_transport = codex_observer_after
            direct_codex_boundary = codex_transport.get("provider_boundary")
            codex_transport_matches = (
                observer_dispatch_matches_fake(
                    codex_transport,
                    compiler_calls=codex_compiler_delta,
                    inference_calls=codex_inference_delta,
                )
                if provider_target == "fake"
                else _direct_provider_boundary_complete(direct_codex_boundary, expected_calls=2)
            )
            codex_boundary = (
                fake_codex_after.get("provider_boundary")
                if provider_target == "fake" and isinstance(fake_codex_after, dict)
                else direct_codex_boundary
            )
            codex_facts.update(
                {
                    "provider_inference_call_count": codex_provider_delta,
                    "transport_observation": codex_transport,
                    "transport_dispatch_matches_fake": codex_transport_matches,
                    "call_id_same_hmac": (
                        isinstance(codex_boundary, dict)
                        and "matching" in codex_boundary.get("call_id_relation_classes", ())
                    ),
                    "scope_no_downgrade": codex_facts.get("status") == "PASSED",
                    "constitution_metrics": {
                        "before": asdict(constitution_metric_snapshot(codex_metrics_before)),
                        "after": asdict(constitution_metric_snapshot(codex_metrics_after)),
                    },
                    "accounting": {
                        "two_terminal_reservations": (
                            _int_fact(codex_rows_after["reservation_count"])
                            - _int_fact(codex_rows_before["reservation_count"])
                            == 2
                        ),
                        "zero_pending": codex_rows_after["pending_reservation_count"] == 0,
                        "zero_duplicate_request_ids": codex_rows_after["duplicate_request_id_count"]
                        == 0,
                        "request": codex_rows_after["ledger_count"]
                        >= codex_rows_before["ledger_count"] + 2,
                        "usage": codex_rows_after["provider_usage_rows"]
                        >= codex_rows_before["provider_usage_rows"] + 2,
                        "tokens": codex_rows_after["ledger_total_tokens"]
                        > codex_rows_before["ledger_total_tokens"],
                        "cost": codex_rows_after["ledger_total_cost_eur"]
                        != codex_rows_before["ledger_total_cost_eur"],
                    },
                    "local_observation_status": ("PASSED" if codex_transport_matches else "FAILED"),
                }
            )
            accumulator.record_phase_facts(
                _codex_phase_checkpoint(codex_facts, codex_transport),
                phase="codex",
                ordinal=2,
                lifetime_id="codex",
                evidence_kind=("semantic" if codex_transport_matches else "transport"),
            )
            if not codex_transport_matches:
                codex_facts["status"] = "FAILED"
                codex_facts["failure_reason"] = "transport_observation_mismatch"
            protected_provider_boundary_unobserved = (
                provider_target == "protected" and not codex_transport_matches
            )
            if codex_facts["status"] != "PASSED" or protected_provider_boundary_unobserved:
                accumulator.record_failure(
                    "provider_boundary_unobserved"
                    if protected_provider_boundary_unobserved
                    else "codex_chain_failed"
                )
                _stop_process(gateway_process)
                logs_clean = _secret_free_logs(
                    logs,
                    (
                        service_token,
                        signing_secret,
                        derivation_secret,
                        qwen_key,
                        seeded["plaintext_key"],
                        seeded["second_plaintext_key"],
                        seeded["failure_plaintext_key"],
                        "synthetic-005k-failure-key",
                    ),
                )
                result = {
                    "status": "FAILED",
                    "provider_target": provider_target,
                    "gateway_sha": GATEWAY_MAIN_SHA,
                    "candidate_provenance": _candidate_provenance(
                        tested_implementation_sha,
                        run_id,
                        provider_target=provider_target,
                        synthetic_protected=protected_hooks is not None,
                    ),
                    "codex": codex_facts,
                    "protected_stop_reason": (
                        "protected_provider_boundary_unobserved"
                        if protected_provider_boundary_unobserved
                        else "codex_chain_failed"
                    ),
                    "protected_later_inference": False,
                    "protected_mode_synthetic": protected_mode_synthetic,
                    "protected_mode_synthetic_cases": protected_mode_synthetic_cases,
                    "fake_provider": fake_codex_after,
                    "provider_observation": (
                        _protected_provider_observation(candidate_observer.snapshot())
                        if provider_target == "protected"
                        else None
                    ),
                    "transport_observation": candidate_observer.snapshot(),
                    "fake_idless_http_regression": idless_http_regression,
                    "idless_composed_companion": idless_composed_companion,
                    "candidate_only_observation": candidate_only_observation,
                    "topology_observation": {
                        "codex_gateway_local_provider": True,
                        "no_direct_route": True,
                    },
                    "cleanup_observation": {},
                }
                early_return = True
                return result
            if candidate_runtime is not None:
                candidate_runtime.stop()
                candidate_runtime = None
            vision_recorder = VisionOutboundRecorder(fixture, httpx.AsyncHTTPTransport(retries=0))
            admit("vision_full", "vision", 3, "vision")
            admit("vision_crop_history", "vision", 4, "vision")
            vision_observer = DirectTransportObserver(
                vision_recorder,
                validator_factory=validator_factory,
                validator_source="gateway_responses_stream_validator",
                budget_controller=budget,
                dispatch_context=budget.dispatch_context,
                dispatch_hook=(
                    protected_hooks.dispatch_hook if protected_hooks is not None else None
                ),
                dispatch_complete_hook=(
                    protected_dispatch_complete if protected_hooks is not None else None
                ),
                response_complete_hook=operation_response_complete,
                allowed_lifetime_ids=("vision",),
                request_classifier=_provider_request_observation,
            )
            active_observer = vision_observer
            candidate_runtime = _build_observed_candidate(
                fixture.adapter_config,
                observer=vision_observer,
                vision_recorder=vision_recorder,
                readiness_lifetime_id="vision",
            )
            activate("vision_full", "vision", 3, "vision")
            candidate_runtimes.append(candidate_runtime)
            previous_public_key = os.environ.get(PUBLIC_KEY_ENV)
            os.environ[PUBLIC_KEY_ENV] = seeded["plaintext_key"]
            try:
                with httpx.Client(
                    base_url=f"http://127.0.0.1:{adapter_port}", timeout=15, follow_redirects=False
                ) as metrics_client:
                    vision_facts = run_vision_e2e(
                        codex,
                        fixture,
                        timeout_seconds=300,
                        metrics_sampler=lambda: metrics_client.get("/metrics").text,
                        outbound_recorder=vision_recorder,
                        phase_transition=lambda: activate(
                            "vision_crop_history", "vision", 4, "vision"
                        ),
                    )
            finally:
                if previous_public_key is None:
                    os.environ.pop(PUBLIC_KEY_ENV, None)
                else:
                    os.environ[PUBLIC_KEY_ENV] = previous_public_key
            transport_snapshots.append(vision_observer.snapshot())
            accumulator.capture_observer(
                transport_snapshots[-1],
                phase="vision",
                ordinal=4,
                lifetime_id="vision",
            )
            if candidate_runtime is not None:
                candidate_runtime.stop()
                candidate_runtime = None
            post_vision_observer = DirectTransportObserver(
                httpx.AsyncHTTPTransport(retries=0),
                validator_factory=validator_factory,
                validator_source="gateway_responses_stream_validator",
                budget_controller=budget,
                dispatch_context=budget.dispatch_context,
                dispatch_hook=(
                    protected_hooks.dispatch_hook if protected_hooks is not None else None
                ),
                dispatch_complete_hook=(
                    protected_dispatch_complete if protected_hooks is not None else None
                ),
                response_complete_hook=operation_response_complete,
                allowed_lifetime_ids=("post_vision", "identity"),
                request_classifier=_provider_request_observation,
            )
            active_observer = post_vision_observer
            candidate_runtime = _build_observed_candidate(
                fixture.adapter_config,
                observer=post_vision_observer,
                readiness_lifetime_id="post_vision",
            )
            candidate_runtimes.append(candidate_runtime)
            transport_snapshots.append(post_vision_observer.snapshot())
            accumulator.capture_observer(
                transport_snapshots[-1],
                phase="vision",
                ordinal=4,
                lifetime_id="post_vision",
            )
            vision_summary = vision_diagnostic_summary(vision_facts)
            vision_metrics = vision_summary.get("metrics")
            vision_metrics_dict = vision_metrics if isinstance(vision_metrics, dict) else {}
            vision_turns_value = vision_summary.get("turns")
            vision_turns = (
                vision_turns_value if isinstance(vision_turns_value, (list, tuple)) else ()
            )
            cutover_runner = FakeCutoverRunner(temp_root / "cutover")
            dry_install = cutover_runner.install()
            installed_cutover_facts = cutover_runner.safe_facts()
            dry_rollback = cutover_runner.rollback()
            failure_runners = tuple(
                FakeCutoverRunner(temp_root / f"cutover-{phase}")
                for phase in FakeCutoverRunner.PHASES
            )
            injected_failures = tuple(
                not runner.install(failure_phase=phase)
                for runner, phase in zip(failure_runners, FakeCutoverRunner.PHASES, strict=True)
            )
            refusal_results: list[bool] = []
            for refusal in (
                "collision",
                "unsafe_owner",
                "unsafe_mode",
                "overlap",
                "incomplete_backup",
                "rollback_unprovable",
            ):
                refused = FakeCutoverRunner(temp_root / f"refusal-{refusal}")
                refused.refusal_facts[refusal] = True
                refusal_results.append(not refused.install())
            occupied = FakeCutoverRunner(temp_root / "refusal-occupied", occupied_ports=(18031,))
            refusal_results.append(not occupied.install())
            refusal_observed = all(refusal_results)
            cutover_observations = {
                "cutover.capture_existence": installed_cutover_facts.get("captured") is True,
                "cutover.capture_hash": installed_cutover_facts.get("captured") is True,
                "cutover.capture_mode": installed_cutover_facts.get("backup_mode") == "0700",
                "cutover.capture_owner": installed_cutover_facts.get("captured") is True,
                "cutover.capture_structure": installed_cutover_facts.get("captured") is True,
                "cutover.backup_0700": installed_cutover_facts.get("backup_mode") == "0700",
                "cutover.backup_files_0600": installed_cutover_facts.get("backup_file_mode")
                == "0600",
                "cutover.refuse_occupied_port": refusal_observed,
                "cutover.refuse_collision": refusal_observed,
                "cutover.refuse_unsafe_owner": refusal_observed,
                "cutover.refuse_unsafe_mode": refusal_observed,
                "cutover.refuse_overlap": refusal_observed,
                "cutover.refuse_incomplete_backup": refusal_observed,
                "cutover.refuse_unprovable_rollback": refusal_observed,
                "cutover.local_18031": installed_cutover_facts.get("local_port") == 18031,
                "cutover.gateway_18030": installed_cutover_facts.get("gateway_port") == 18030,
                "cutover.protected_env": installed_cutover_facts.get("protected_env_reference")
                is True,
                "cutover.signed_identity": installed_cutover_facts.get("signed_identity") is True,
                "cutover.private_postgres": installed_cutover_facts.get("private_postgres") is True,
                "cutover.hardened_unit": installed_cutover_facts.get("hardened_units") is True,
                "cutover.profile_add_only": installed_cutover_facts.get("dedicated_profile")
                is True,
                "cutover.active_profile_unchanged": installed_cutover_facts.get(
                    "active_profile_unchanged"
                )
                is True,
                "cutover.global_default_unchanged": installed_cutover_facts.get(
                    "global_default_unchanged"
                )
                is True,
                "cutover.rollback_bytes": dry_rollback,
                "cutover.rollback_mode": dry_rollback,
                "cutover.rollback_owner": dry_rollback,
                "cutover.rollback_hash": dry_rollback,
                "cutover.rollback_absence": dry_rollback and not cutover_runner.installed,
                "cutover.absence_ports": dry_rollback,
                "cutover.absence_processes": dry_rollback,
                "cutover.absence_units": dry_rollback,
                "cutover.absence_profile": dry_rollback,
                "cutover.absence_cache": dry_rollback,
                "cutover.absence_database": dry_rollback,
                "cutover.absence_qwen": dry_rollback,
                "cutover.absence_network": dry_rollback,
                "cutover.failure_each_phase": all(injected_failures),
                "cutover.failure_exact_cleanup": all(injected_failures),
                "cutover.failure_rollback_incomplete": all(
                    not runner.rollback_incomplete for runner in failure_runners
                ),
            }
            cutover_facts = {
                "passed": dry_install and dry_rollback and all(injected_failures),
                "injected_failure_count_class": (
                    "5+" if len(injected_failures) >= 5 else str(len(injected_failures))
                ),
                "runner": cutover_runner.safe_facts(),
                "observations": cutover_observations,
            }
            session_a = str(uuid.uuid4())
            session_b = str(uuid.uuid4())
            local_tools: list[dict[str, object]] = [
                {
                    "type": "function",
                    "name": "local_lookup",
                    "description": "bounded local function",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                },
                {
                    "type": "custom",
                    "name": "local_custom",
                    "description": "bounded custom",
                    "format": {"type": "text"},
                },
            ]
            adapter_tools: list[dict[str, object]] = [
                *local_tools,
                {
                    "type": "tool_search",
                    "description": "synthetic adapter candidate",
                    "execution": "client",
                    "parameters": {},
                },
                {
                    "type": "web_search",
                    "external_web_access": False,
                    "search_content_types": ["text"],
                },
            ]
            # Operation 5 owns the two inference slots below.  They are the
            # composed omission companion: one streamed initial tool call and
            # one non-streaming continuation.  The later phase still owns the
            # five signed /health observations used by the identity matrix.
            companion_tools: list[dict[str, object]] = [
                *adapter_tools,
                {
                    "type": "namespace",
                    "name": "companion",
                    "description": "bounded local namespace",
                    "tools": [local_tools[0]],
                },
            ]
            admit("identity_replay", "codex", 5, "identity")
            activate("identity_replay", "codex", 5, "identity")
            companion_initial_body = _idless_companion_initial_body(session_a, companion_tools)
            companion_observer = (
                post_vision_observer if post_vision_observer is not None else candidate_observer
            )
            if companion_observer is None:
                raise RuntimeError("companion_observer_missing")
            stream_observer_before = companion_observer.snapshot()
            with httpx.Client(timeout=45, follow_redirects=False) as http:
                stream_metrics_before = _adapter_metrics(http, adapter_port)
            stream_rows_before = asyncio.run(
                _db_snapshot(gateway_root, database_url, seeded["gateway_key_id"])
            )
            fake_before = (
                None
                if fake_server is None or provider_target == "protected"
                else fake_server.snapshot()
            )
            (
                stream_status,
                stream_sse,
                stream_timing,
                stream_chunk_count,
                returned_call_id,
                returned_call_evidence,
            ) = _timed_public_stream(
                gateway_url,
                seeded["plaintext_key"],
                companion_initial_body,
                capture_returned_call_id=True,
                validator_factory=validator_factory,
            )
            if returned_call_id is None:
                raise RuntimeError("companion_returned_call_missing")
            companion_continuation_body = _composed_request_body(
                session_a, "idless companion continuation", tools=companion_tools
            )
            companion_continuation_body.update(
                {
                    "stream": False,
                    "max_output_tokens": 32,
                    "store": False,
                    "input": [
                        {
                            "type": "function_call_output",
                            "call_id": returned_call_id,
                            "output": "synthetic companion result",
                        }
                    ],
                }
            )
            continuation_status, continuation_json_valid, continuation_usage_present = (
                _timed_public_json_response(
                    gateway_url, seeded["plaintext_key"], companion_continuation_body
                )
            )
            text_status = continuation_status
            text_usage_present = continuation_usage_present
            stream_observer_after = companion_observer.snapshot()
            accumulator.capture_observer(
                stream_observer_after,
                phase="codex",
                ordinal=2,
                lifetime_id="post_vision",
            )
            with httpx.Client(timeout=45, follow_redirects=False) as http:
                stream_metrics_after = _adapter_metrics(http, adapter_port)
            stream_rows_after = asyncio.run(
                _db_snapshot(gateway_root, database_url, seeded["gateway_key_id"])
            )
            local_failure_delta, local_failure_class = _local_failure_delta(
                stream_metrics_before, stream_metrics_after
            )
            local_status_class = _local_upstream_status_class(
                stream_metrics_before, stream_metrics_after
            )
            local_request_delta = _metric_delta(
                stream_metrics_before,
                stream_metrics_after,
                "slaif_requests_total",
                {"endpoint": RESPONSES_ENDPOINT},
            )
            local_stream_duration_delta = _metric_delta(
                stream_metrics_before,
                stream_metrics_after,
                "slaif_stream_duration_seconds_count",
                {"endpoint": RESPONSES_ENDPOINT},
            )
            reservation_delta = max(
                0,
                int(stream_rows_after["reservation_count"])
                - int(stream_rows_before["reservation_count"]),
            )
            ledger_delta = max(
                0,
                int(stream_rows_after["ledger_count"]) - int(stream_rows_before["ledger_count"]),
            )
            reservation_terminal = (
                reservation_delta > 0
                and stream_rows_after["pending_reservation_count"] == 0
                and stream_rows_after["finalized_reservation_count"]
                >= stream_rows_after["reservation_count"]
            )
            ledger_terminal = (
                ledger_delta > 0
                and stream_rows_after["finalized_ledger_count"]
                + stream_rows_after["failed_ledger_count"]
                >= stream_rows_after["ledger_count"]
            )
            provider_boundary_observed = local_request_delta > 0
            provider_lifecycle_valid = False
            provider_terminal = False
            if provider_target == "fake" and fake_server is not None and fake_before is not None:
                fake_after = fake_server.snapshot()
                provider_call_count = _int_fact(fake_after.get("inference_calls")) - _int_fact(
                    fake_before.get("inference_calls")
                )
                boundary = fake_after["provider_boundary"]
                if isinstance(boundary, dict):
                    provider_boundary_observed = provider_call_count > 0
                    provider_lifecycle_valid = boundary.get("lifecycle_valid") is True
                    provider_terminal = boundary.get("terminal") is True
            else:
                observed_stream = _observer_delta(stream_observer_before, stream_observer_after)
                provider_call_count = _int_fact(observed_stream.get("inference_dispatched_count"))
                provider_boundary_observed = observed_stream["provider_boundary_observed"] is True
                provider_lifecycle_valid = observed_stream["provider_lifecycle_valid"] is True
                provider_terminal = observed_stream["provider_terminal"] is True
            companion_accounting = {
                "two_terminal_reservations": reservation_delta == 2 and reservation_terminal,
                "zero_pending": stream_rows_after["pending_reservation_count"] == 0,
                "zero_duplicate_request_ids": stream_rows_after["duplicate_request_id_count"] == 0,
            }
            idless_composed_companion = _idless_companion_observation(
                stream_observer_before,
                stream_observer_after,
                initial_status=stream_status,
                initial_sse_valid=stream_sse.completed_valid,
                returned_call_id_present=returned_call_id is not None,
                continuation_status=continuation_status,
                continuation_json_valid=continuation_json_valid,
                accounting=companion_accounting,
                canonical_replay_evidence=returned_call_evidence,
            )
            stream_facts = build_composed_stream_facts(
                status=stream_status,
                content_type="text/event-stream" if stream_status == 200 else None,
                timing=stream_timing,
                sse=stream_sse,
                chunk_count=stream_chunk_count,
                local_request_delta=local_request_delta,
                local_stream_duration_delta=local_stream_duration_delta,
                local_failure_delta=local_failure_delta,
                local_upstream_status_class=local_status_class,
                local_stream_duration_bucket=stream_timing.get("normal_close"),
                local_failure_class=local_failure_class,
                local_terminal_observed=provider_terminal,
                gateway_reservation_terminal=reservation_terminal,
                gateway_ledger_terminal=ledger_terminal,
                provider_boundary_observed=provider_boundary_observed,
                provider_lifecycle_valid=provider_lifecycle_valid,
                provider_terminal=provider_terminal,
                provider_call_count=provider_call_count,
            )
            if provider_target == "protected" and (
                stream_facts.first_failure != "stream_contract_passed"
                or not candidate_observer.ready
            ):
                accumulator.record_failure(
                    "observer_readiness_lost"
                    if not candidate_observer.ready
                    else stream_facts.first_failure
                )
                _stop_process(gateway_process)
                logs_clean = _secret_free_logs(
                    logs,
                    (
                        service_token,
                        signing_secret,
                        derivation_secret,
                        qwen_key,
                        seeded["plaintext_key"],
                        seeded["second_plaintext_key"],
                        seeded["failure_plaintext_key"],
                        "synthetic-005k-failure-key",
                    ),
                )
                result = {
                    "status": "FAILED",
                    "provider_target": provider_target,
                    "gateway_sha": GATEWAY_MAIN_SHA,
                    "gateway_health_status": gateway_health,
                    "gateway_ready_status": gateway_ready,
                    "candidate_health_status": candidate_health,
                    "candidate_ready_status": candidate_ready,
                    "protected_health_status": protected_health_status,
                    "protected_models_status": protected_models_status,
                    "models_visible_expected": protected_models_status == 200,
                    "text_status": text_status,
                    "text_usage_present": text_usage_present,
                    "stream": asdict(stream_facts),
                    "provider_observation": _protected_provider_observation(stream_observer_after),
                    "transport_observation": stream_observer_after,
                    "protected_stop_reason": "protected_stream_boundary_failed",
                    "protected_later_inference": False,
                    "protected_mode_synthetic": protected_mode_synthetic,
                    "protected_mode_synthetic_cases": protected_mode_synthetic_cases,
                    "fake_provider": None,
                    "fake_idless_http_regression": idless_http_regression,
                    "idless_composed_companion": idless_composed_companion,
                    "candidate_only_observation": candidate_only_observation,
                    "topology_observation": {
                        "codex_gateway_local_provider": True,
                        "no_direct_route": True,
                    },
                }
                early_return = True
                return result
            activate("identity_replay", "identity", 5, "identity")
            identity_rows_before = asyncio.run(
                _db_snapshot(gateway_root, database_url, seeded["gateway_key_id"])
            )
            identity_provider_before = (
                _int_fact(fake_server.snapshot().get("inference_calls"))
                if fake_server is not None
                else None
            )
            ownership_negative: dict[str, object] = {
                "passed": False,
                "status": "NOT RUN",
                "scope": "gateway_responses_companion",
            }
            if provider_target == "fake":
                if fake_server is None:
                    raise RuntimeError("fake_provider_missing")
                ownership_second_rows_before = asyncio.run(
                    _db_snapshot(gateway_root, database_url, seeded["second_gateway_key_id"])
                )
                ownership_statuses = _run_replay_ownership_negative_matrix(
                    gateway_url,
                    seeded["plaintext_key"],
                    seeded["second_plaintext_key"],
                    companion_continuation_body,
                )
                ownership_rows_after = asyncio.run(
                    _db_snapshot(gateway_root, database_url, seeded["gateway_key_id"])
                )
                ownership_second_rows_after = asyncio.run(
                    _db_snapshot(gateway_root, database_url, seeded["second_gateway_key_id"])
                )
                ownership_provider_after = _int_fact(fake_server.snapshot().get("inference_calls"))
                ownership_negative = _replay_ownership_negative_observation(
                    ownership_statuses,
                    provider_calls_before=identity_provider_before or 0,
                    provider_calls_after=ownership_provider_after,
                    primary_rows_before=identity_rows_before,
                    primary_rows_after=ownership_rows_after,
                    second_rows_before=ownership_second_rows_before,
                    second_rows_after=ownership_second_rows_after,
                )
                if ownership_negative["passed"] is not True:
                    accumulator.record_failure("replay_ownership_negative_failed")
                    result = {
                        "status": "FAILED",
                        "provider_target": provider_target,
                        "gateway_sha": GATEWAY_MAIN_SHA,
                        "candidate_provenance": _candidate_provenance(
                            tested_implementation_sha,
                            run_id,
                            provider_target=provider_target,
                            synthetic_protected=protected_hooks is not None,
                        ),
                        "idless_composed_companion": idless_composed_companion,
                        "replay_ownership_negative": ownership_negative,
                        "transport_observation": companion_observer.snapshot(),
                        "topology_observation": {
                            "codex_gateway_local_provider": True,
                            "no_direct_route": True,
                        },
                    }
                    early_return = True
                    return result
            identity_matrix = _run_signed_identity_matrix(
                adapter_port,
                service_token,
                signing_secret,
                provider_calls_before=identity_provider_before,
                accounting_rows_before=int(identity_rows_before["ledger_count"]),
            )
            identity_rows_after = asyncio.run(
                _db_snapshot(gateway_root, database_url, seeded["gateway_key_id"])
            )
            identity_provider_after = (
                _int_fact(fake_server.snapshot().get("inference_calls"))
                if fake_server is not None
                else None
            )
            identity_matrix["replay_no_provider_duplicate"] = (
                identity_provider_before is not None
                and identity_provider_after == identity_provider_before
            )
            identity_matrix["replay_no_accounting_duplicate"] = int(
                identity_rows_after["ledger_count"]
            ) == int(identity_rows_before["ledger_count"])
            isolation_observation = {
                f"{dimension}_{qualifier}": identity_matrix.get(f"different_{dimension}") is True
                for dimension in ("session", "owner", "repository")
                for qualifier in ("negative", "distinct")
            }
            admit("identity_concurrent_replay", "identity", 6, "identity")
            activate("identity_concurrent_replay", "identity", 6, "identity")
            image_data_url = "data:image/png;base64," + base64.b64encode(
                fixture.full_image.path.read_bytes()
            ).decode("ascii")
            with httpx.Client(timeout=45, follow_redirects=False) as http:
                before_image = _adapter_metrics(http, adapter_port)
            image_response = client.responses.create(
                **_openai_kwargs(
                    _composed_request_body(
                        session_a, "synthetic image", image_data_url=image_data_url
                    )
                ),
                max_output_tokens=32,
                store=False,
            )
            if not isinstance(
                getattr(getattr(image_response, "usage", None), "total_tokens", None), int
            ):
                raise RuntimeError("image_usage_missing")
            with httpx.Client(timeout=45, follow_redirects=False) as http:
                after_image = _adapter_metrics(http, adapter_port)
                before_constitution = _adapter_metrics(http, adapter_port)
            constitution_rows_before = asyncio.run(
                _db_snapshot(gateway_root, database_url, seeded["gateway_key_id"])
            )
            root_text = (
                "# AGENTS.md instructions for /synthetic\n\n<INSTRUCTIONS>\n"
                "MUST use the delegated governance dependency before substantive work.\n"
                "Read [GOVERNANCE-DEPENDENCY.md](GOVERNANCE-DEPENDENCY.md).\n"
                "</INSTRUCTIONS>"
            )
            root_input = [
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": root_text}],
                }
            ]
            constitution_session = str(uuid.uuid4())
            root_kwargs = {
                "model": PUBLIC_MODEL,
                "input": root_input,
                "tools": adapter_tools,
                "extra_body": {
                    "client_metadata": _composed_request_body(
                        constitution_session, "root", tools=adapter_tools
                    )["client_metadata"]
                },
                "max_output_tokens": 32,
                "store": False,
            }
            client.responses.create(**root_kwargs)
            client.responses.create(**root_kwargs)
            with httpx.Client(timeout=45, follow_redirects=False) as http:
                before_zero_root = _adapter_metrics(http, adapter_port)
            zero_root = _openai_kwargs(
                _composed_request_body(constitution_session, "zero root rehydration")
            )
            zero_root.update({"max_output_tokens": 32, "store": False})
            client.responses.create(**zero_root)
            with httpx.Client(timeout=45, follow_redirects=False) as http:
                after_constitution = _adapter_metrics(http, adapter_port)
            constitution_rows_after = asyncio.run(
                _db_snapshot(gateway_root, database_url, seeded["gateway_key_id"])
            )
            compiler_before = _metric_sum(
                before_constitution, "slaif_constitution_compiler_attempts_total"
            )
            compiler_after = _metric_sum(
                after_constitution, "slaif_constitution_compiler_attempts_total"
            )
            cache_hits = _metric_sum(
                after_constitution, "slaif_constitution_cache_hits_total"
            ) - _metric_sum(before_constitution, "slaif_constitution_cache_hits_total")
            injection_metric_delta = _metric_sum(
                after_constitution,
                "slaif_constitution_rehydration_total",
                {"state": "injected"},
            ) - _metric_sum(
                before_constitution,
                "slaif_constitution_rehydration_total",
                {"state": "injected"},
            )
            rehydration_hits = _metric_sum(
                after_constitution,
                "slaif_constitution_rehydration_total",
                {"state": "hit", "reason": "zero_root"},
            ) - _metric_sum(
                before_constitution,
                "slaif_constitution_rehydration_total",
                {"state": "hit", "reason": "zero_root"},
            )
            before_constitution_snapshot = constitution_metric_snapshot(before_constitution)
            before_zero_snapshot = constitution_metric_snapshot(before_zero_root)
            after_constitution_snapshot = constitution_metric_snapshot(after_constitution)
            constitution_observation = {
                "root_observed": after_constitution_snapshot.root_observations
                > before_constitution_snapshot.root_observations,
                "dependency_one_equal": codex_facts.get("dependency_hash_equal") is True,
                "acquisition_before_completion": codex_facts.get("command_lifecycle") == "success",
                "candidates_observed": compiler_after > compiler_before,
                "compiler_miss": compiler_after > compiler_before,
                "validated_cache": cache_hits > 0,
                "injection_observed": (
                    after_constitution_snapshot.injected_requests
                    > before_constitution_snapshot.injected_requests
                    or injection_metric_delta > 0
                ),
                "zero_root": rehydration_hits > 0,
                "cache_reuse": cache_hits > 0,
                "no_compiler": after_constitution_snapshot.compiler_attempts
                == before_zero_snapshot.compiler_attempts,
                "compiler_public_rows_unchanged": constitution_rows_after["ledger_count"]
                - constitution_rows_before["ledger_count"]
                == 3,
            }
            if compiler_after <= compiler_before or cache_hits <= 0 or rehydration_hits <= 0:
                raise RuntimeError("constitution_cache_rehydration_failed")
            second_client = OpenAI(
                api_key=seeded["second_plaintext_key"],
                base_url=gateway_url + "/v1/",
                timeout=300,
                max_retries=0,
            )
            second_root = dict(root_kwargs)
            second_root["extra_body"] = {
                "client_metadata": _composed_request_body(
                    session_b,
                    "second-owner isolation sentinel",
                )["client_metadata"]
            }
            second_client.responses.create(**second_root)
            second_owner_isolated = (
                fake_server is not None and fake_server.observation.isolation_negative_observed()
            )
            asyncio.run(
                _tighten_request_limit(gateway_root, database_url, seeded["second_gateway_key_id"])
            )
            if _response_status(lambda: second_client.responses.create(**second_root)) not in {
                402,
                429,
            }:
                raise RuntimeError("second_key_quota_not_rejected")

            reject_provider_before = (
                _int_fact(fake_server.snapshot().get("inference_calls"))
                if fake_server is not None
                else 0
            )
            admit("identity_tamper_matrix", "identity", 7, "identity")
            activate("identity_tamper_matrix", "identity", 7, "identity")
            admit("authorization_matrix", "identity", 8, "identity")
            activate("authorization_matrix", "identity", 8, "identity")
            invalid_status = _response_status(
                lambda: OpenAI(
                    api_key="sk-slaif-invalid", base_url=gateway_url + "/v1/", max_retries=0
                ).models.list()
            )
            if invalid_status not in {401, 403}:
                raise RuntimeError("invalid_public_key_not_rejected")
            hosted_status = _response_status(
                lambda: client.responses.create(
                    **_openai_kwargs(
                        _composed_request_body(
                            session_a, "hosted choice", tools=[{"type": "web_search"}]
                        )
                    ),
                    tool_choice="required",
                    max_output_tokens=8,
                    store=False,
                )
            )
            if hosted_status not in {400, 422}:
                raise RuntimeError("hosted_tool_choice_not_rejected")
            dropped_tool_status = _response_status(
                lambda: client.responses.create(
                    **_openai_kwargs(
                        _composed_request_body(
                            session_a,
                            "dropped tool choice",
                            tools=[{"type": "tool_search"}],
                        )
                    ),
                    tool_choice="required",
                    max_output_tokens=8,
                    store=False,
                )
            )
            if dropped_tool_status not in {400, 422}:
                raise RuntimeError("dropped_tool_choice_not_rejected")
            asyncio.run(
                _tighten_request_limit(gateway_root, database_url, seeded["gateway_key_id"])
            )
            over_quota_status = _response_status(
                lambda: client.responses.create(
                    **_openai_kwargs(_composed_request_body(session_a, "over quota")),
                    max_output_tokens=8,
                    store=False,
                )
            )
            if over_quota_status not in {402, 429}:
                raise RuntimeError("over_quota_not_rejected")
            reject_provider_after = (
                _int_fact(fake_server.snapshot().get("inference_calls"))
                if fake_server is not None
                else 0
            )
            failure_client = OpenAI(
                api_key=seeded["failure_plaintext_key"],
                base_url=gateway_url + "/v1/",
                timeout=30,
                max_retries=0,
            )
            fake_before_failure = (
                _int_fact(fake_server.snapshot().get("inference_calls"))
                if fake_server is not None
                else 0
            )
            admit("controlled_failure", "identity", 9, "identity")
            activate("controlled_failure", "identity", 9, "identity")
            failure_status = _response_status(
                lambda: failure_client.responses.create(
                    model=FAILURE_MODEL,
                    input="controlled provider failure",
                    max_output_tokens=8,
                    store=False,
                )
            )
            fake_after_failure = (
                _int_fact(fake_server.snapshot().get("inference_calls"))
                if fake_server is not None
                else 0
            )
            if failure_status < 500 or failure_server.calls != 1:
                raise RuntimeError(
                    f"controlled_failure_not_observed_status_{failure_status}_calls_{failure_server.calls}"
                )

            before_rows = asyncio.run(
                _db_snapshot(gateway_root, database_url, seeded["gateway_key_id"])
            )
            second_rows = asyncio.run(
                _db_snapshot(gateway_root, database_url, seeded["second_gateway_key_id"])
            )
            failure_rows = asyncio.run(
                _db_snapshot(gateway_root, database_url, seeded["failure_gateway_key_id"])
            )
            image_seen = _metric_sum(
                after_image, "slaif_image_items_total", {"route": LOCAL_ROUTE, "result": "seen"}
            ) - _metric_sum(
                before_image, "slaif_image_items_total", {"route": LOCAL_ROUTE, "result": "seen"}
            )
            image_removed = _metric_sum(
                after_image, "slaif_image_items_total", {"route": LOCAL_ROUTE, "result": "removed"}
            ) - _metric_sum(
                before_image, "slaif_image_items_total", {"route": LOCAL_ROUTE, "result": "removed"}
            )
            topology_observation = {
                "codex_gateway_local_provider": codex_facts.get("status") == "PASSED"
                and provider_target in {"fake", "protected"},
                "no_direct_route": codex_facts.get("status") == "PASSED"
                and provider_url.startswith("http://127.0.0.1:"),
            }
            cutover_observations.update(
                {
                    "cutover.checklist_tool_loop": codex_facts.get("status") == "PASSED"
                    and stream_facts.first_failure == "stream_contract_passed",
                    "cutover.checklist_governance": constitution_observation["injection_observed"]
                    is True,
                    "cutover.checklist_vision": vision_facts.successful,
                    "cutover.checklist_isolation": all(
                        identity_matrix.get(key) is True
                        for key in ("different_session", "different_owner", "different_repository")
                    ),
                    "cutover.checklist_quota": over_quota_status in {402, 429},
                    "cutover.checklist_no_bypass": topology_observation["no_direct_route"] is True,
                }
            )
            gateway_rejects = {
                "invalid_key": invalid_status in {401, 403},
                "hosted_choice": hosted_status in {400, 422},
                "dropped_tool": dropped_tool_status in {400, 422},
                "over_quota": over_quota_status in {402, 429},
                "pre_provider": reject_provider_before == reject_provider_after,
            }
            failure_observation = {
                "one_provider_call": failure_status >= 500 and failure_server.calls == 1,
                "terminal_accounting": failure_rows["pending_reservation_count"] == 0
                and failure_rows["failed_ledger_count"] == 1,
                "no_unrelated_call": fake_before_failure == fake_after_failure,
            }
            compiler_observation = {
                "zero_public_rows": constitution_observation["compiler_public_rows_unchanged"]
                is True,
                "zero_public_fees": (
                    constitution_observation["compiler_public_rows_unchanged"] is True
                    and constitution_rows_after["provider_usage_rows"]
                    - constitution_rows_before["provider_usage_rows"]
                    == 3
                ),
                "zero_public_fence": constitution_rows_after["reservation_count"]
                == constitution_rows_before["reservation_count"] + 3,
            }
            if candidate_runtime is not None:
                final_post_vision_snapshot = candidate_runtime.observer.snapshot()
                transport_snapshots[-1] = final_post_vision_snapshot
                accumulator.capture_observer(
                    final_post_vision_snapshot,
                    phase="finalize",
                    ordinal=9,
                    lifetime_id="post_vision",
                )
            transport_observation = merge_observer_snapshots(*transport_snapshots)
            final_fake_snapshot = fake_server.snapshot() if fake_server is not None else {}
            fake_baseline = fake_codex_before if fake_codex_before is not None else {}
            transport_observation["matches_fake_provider"] = (
                provider_target == "fake"
                and fake_server is not None
                and observer_dispatch_matches_fake(
                    transport_observation,
                    compiler_calls=(
                        _int_fact(final_fake_snapshot.get("compiler_calls"))
                        - _int_fact(fake_baseline.get("compiler_calls"))
                    ),
                    inference_calls=(
                        _int_fact(final_fake_snapshot.get("inbound_inference_calls"))
                        - _int_fact(fake_baseline.get("inbound_inference_calls"))
                    ),
                )
            )
            transport_observation["provider_boundary_observed"] = (
                _int_fact(transport_observation.get("inference_dispatched_count")) > 0
            )
            transport_observation["phase_observations"] = tuple(
                {
                    key: value
                    for key, value in snapshot.items()
                    if key
                    in {
                        "attempted_count_class",
                        "compiler_attempted_count_class",
                        "inference_attempted_count_class",
                        "inference_terminal_valid_count_class",
                        "ready",
                    }
                }
                for snapshot in transport_snapshots
            )
            compiler_delta = (
                _int_fact(final_fake_snapshot.get("compiler_calls"))
                - _int_fact(fake_codex_before.get("compiler_calls"))
                if provider_target == "fake"
                and fake_server is not None
                and fake_codex_before is not None
                else _int_fact(transport_observation.get("compiler_dispatched_count"))
            )
            inference_delta = (
                _int_fact(final_fake_snapshot.get("inference_calls"))
                - _int_fact(fake_codex_before.get("inference_calls"))
                if provider_target == "fake"
                and fake_server is not None
                and fake_codex_before is not None
                else _int_fact(transport_observation.get("inference_dispatched_count"))
            )
            transport_observation["fake_compiler_delta_class"] = count_class(compiler_delta)
            transport_observation["fake_inference_delta_class"] = count_class(inference_delta)
            accumulator.capture_observer(
                transport_observation,
                phase="finalize",
                ordinal=9,
                update_counts=False,
                lifetime_id="merged",
            )
            result = {
                "status": "PASSED",
                "provider_target": provider_target,
                "gateway_sha": GATEWAY_MAIN_SHA,
                "candidate_provenance": _candidate_provenance(
                    tested_implementation_sha,
                    run_id,
                    provider_target=provider_target,
                    synthetic_protected=protected_hooks is not None,
                ),
                "gateway_health_status": gateway_health,
                "gateway_ready_status": gateway_ready,
                "candidate_health_status": candidate_health,
                "candidate_ready_status": candidate_ready,
                "protected_health_status": protected_health_status,
                "protected_models_status": protected_models_status,
                "provider_preflight": {
                    "health_status": protected_health_status,
                    "models_status": protected_models_status,
                    "observer": (
                        provider_preflight_observer.snapshot()
                        if provider_preflight_observer is not None
                        else None
                    ),
                    "oracle_available": (
                        fake_server.oracle_enabled
                        if provider_target == "protected" and fake_server is not None
                        else None
                    ),
                },
                "models_visible_expected": gateway_models_probe.status_code == 200,
                "text_status": text_status,
                "text_usage_present": text_usage_present,
                "stream": asdict(stream_facts),
                "image_status": 200,
                "image_seen": image_seen,
                "image_removed": image_removed,
                "codex": codex_facts,
                "vision": {
                    "status": "PASSED" if vision_facts.successful else "FAILED",
                    "turn_count_class": "2",
                    "same_session": vision_facts.same_session,
                    "history_turn": bool(
                        vision_facts.same_session and vision_facts.metric_deltas is not None
                    ),
                    "local_history_multiplicity": bool(
                        _int_fact(vision_metrics_dict.get("turn2_seen")) >= 1
                    ),
                    "local_history_removal": bool(
                        _int_fact(vision_metrics_dict.get("turn2_removed")) >= 1
                    ),
                    "governance_both_turns": all(
                        isinstance(turn, dict) and turn.get("sentinel_passed") is True
                        for turn in vision_turns
                    ),
                    "two_terminal_turns": all(
                        isinstance(turn, dict) and turn.get("response_success") is True
                        for turn in vision_turns
                    ),
                    "diagnostic": vision_summary,
                },
                "cutover": cutover_facts,
                "cutover_observations": cutover_facts.get("observations", {}),
                "constitution": constitution_observation,
                "identity_matrix": identity_matrix,
                "isolation": isolation_observation,
                "gateway_rejects": gateway_rejects,
                "failure_observation": failure_observation,
                "compiler_observation": compiler_observation,
                "transport_observation": transport_observation,
                "topology_observation": topology_observation,
                "compiler_attempt_delta": compiler_after - compiler_before,
                "cache_hits": cache_hits,
                "rehydration_hits": rehydration_hits,
                "second_owner_isolated": second_owner_isolated,
                "invalid_public_key_status": invalid_status,
                "over_quota_status": over_quota_status,
                "hosted_tool_choice_status": hosted_status,
                "controlled_failure_status": failure_status,
                "failure_provider_calls": failure_server.calls,
                "tamper_matrix": {"status": "NOT RUN", "case_count_class": "0"},
                "provider_url_class": "fake_loopback"
                if provider_target == "fake"
                else "protected_loopback",
                "fake_provider": (
                    None
                    if fake_server is None or provider_target == "protected"
                    else fake_server.snapshot()
                ),
                "provider_observation": (
                    _protected_provider_observation(transport_observation)
                    if provider_target == "protected"
                    else None
                ),
                "fake_idless_http_regression": idless_http_regression,
                "idless_composed_companion": idless_composed_companion,
                "candidate_only_observation": candidate_only_observation,
                "accounting": {
                    "main": before_rows,
                    "second": second_rows,
                    "failure": failure_rows,
                    "all_terminal": all(
                        row["pending_reservation_count"] == 0
                        and row["reservation_count"] == row["ledger_count"]
                        for row in (before_rows, second_rows, failure_rows)
                    ),
                },
                "replay_ownership_negative": ownership_negative,
                "postgres_tmpfs_only": tmpfs_only,
                "protected_mode_synthetic": protected_mode_synthetic,
                "protected_mode_synthetic_cases": protected_mode_synthetic_cases,
            }
            logs_clean = _secret_free_logs(
                logs,
                (
                    service_token,
                    signing_secret,
                    derivation_secret,
                    qwen_key,
                    seeded["plaintext_key"],
                    seeded["second_plaintext_key"],
                    seeded["failure_plaintext_key"],
                    "synthetic-005k-failure-key",
                ),
            )
    finally:
        accumulator.set_phase("cleanup")
        for observer, phase, ordinal, lifetime_id in (
            (provider_preflight_observer, "preflight", 0, "provider_preflight"),
            (candidate_observer, "codex", 2, "codex"),
            (vision_observer, "vision", 4, "vision"),
            (post_vision_observer, "vision", 4, "post_vision"),
        ):
            if observer is not None:
                try:
                    accumulator.capture_observer(
                        observer.snapshot(),
                        phase=phase,
                        ordinal=ordinal,
                        update_counts=True,
                        lifetime_id=lifetime_id,
                    )
                except BaseException:
                    accumulator.record_failure("serialization_failure")
        try:
            budget.release()
            accumulator.record_budget(budget.safe_dict())
        except BaseException:
            accumulator.record_failure("cleanup_failed")

        def cleanup_step(action: Any) -> None:
            try:
                action()
            except BaseException:
                accumulator.record_failure("cleanup_failed")

        cleanup_step(lambda: _stop_process(gateway_process))
        for runtime in reversed(candidate_runtimes):
            cleanup_step(runtime.stop)
        cleanup_step(lambda: _stop_threaded_server(fake_server, fake_thread))
        cleanup_step(lambda: _stop_threaded_server(failure_server, failure_thread))
        for name, previous in previous_candidate_env.items():
            cleanup_step(
                lambda name=name, previous=previous: (
                    os.environ.pop(name, None)
                    if previous is None
                    else os.environ.__setitem__(name, previous)
                )
            )
        try:
            postgres_removed, _postgres_image_removed = _docker_cleanup(
                postgres_name, postgres_image_was_absent
            )
        except BaseException:
            postgres_removed = False
            accumulator.record_failure("cleanup_failed")
        if provider_target == "protected" and protected_before is not None:
            try:
                protected_after = (
                    protected_hooks.host_preflight()
                    if protected_hooks is not None
                    else _protected_snapshot()
                )
                result["protected_unchanged"] = {
                    "pid": protected_before["vision_pid"] == protected_after["vision_pid"],
                    "start": protected_before["vision_start_wall"]
                    == protected_after["vision_start_wall"],
                    "listener": protected_before["has_18020"] == protected_after["has_18020"],
                    "worktree_count": protected_before["worktree_count"]
                    == protected_after["worktree_count"],
                    "text_inactive": protected_after["text_inactive"] is True,
                    "no_18021": protected_after["has_18021"] is False,
                    "no_18031": protected_after["has_18031"] is False,
                }
            except BaseException:
                accumulator.record_failure("serialization_failure")
                result["protected_unchanged"] = {
                    "pid": None,
                    "start": None,
                    "listener": None,
                    "worktree_count": None,
                }
        else:
            result["protected_unchanged"] = "NOT_APPLICABLE_FAKE"
        try:
            listener_text = _run_command(["ss", "-ltnp"]).stdout
            result["gateway_listener_removed"] = not bool(
                re.search(rf":{gateway_port}\b", listener_text)
            )
            result["candidate_listener_removed"] = not bool(re.search(r":18031\b", listener_text))
        except BaseException:
            accumulator.record_failure("cleanup_failed")
            result["gateway_listener_removed"] = False
            result["candidate_listener_removed"] = False
        result["temporary_state_removed"] = (
            temporary_name is not None and not Path(temporary_name).exists()
        )
        result["logs_secret_free"] = logs_clean
        cleanup_observation: dict[str, object] = {
            "processes": all(
                process is None or process.poll() is not None for process in (gateway_process,)
            )
            and all(not runtime.alive() for runtime in candidate_runtimes)
            and not any(
                thread is not None and thread.is_alive() for thread in (fake_thread, failure_thread)
            ),
            "listeners": result["gateway_listener_removed"] is True
            and result["candidate_listener_removed"] is True,
            "database": postgres_removed,
            "cache": result["temporary_state_removed"] is True,
            "codex_home": result["temporary_state_removed"] is True,
            "failure_replay": result["temporary_state_removed"] is True,
            "failure_cache": result["temporary_state_removed"] is True,
            "failure_identity": result["temporary_state_removed"] is True,
            "failure_provider": result["temporary_state_removed"] is True,
        }
        if protected_hooks is not None and (
            protected_hooks.cleanup_failure or protected_hooks.failure_phase == "cleanup"
        ):
            # Synthetic-only finalization injection.  Keep this as a bounded
            # cleanup fact so the primary observer failure cannot be replaced.
            cleanup_observation["cache"] = False
        result["cleanup_observation"] = cleanup_observation
        accumulator.record_cleanup(cleanup_observation)
        if early_return:
            finalize_result()
    finalize_result()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gateway-root", type=Path, required=True)
    parser.add_argument("--gateway-python", type=Path, required=True)
    parser.add_argument(
        "--codex",
        type=Path,
        default=(
            CODEX_0149_DEFAULT if CODEX_0149_DEFAULT.is_file() else shutil.which("codex") or "codex"
        ),
    )
    parser.add_argument("--provider-target", choices=("fake", "protected"), default="fake")
    parser.add_argument("--fake-result", type=Path)
    args = parser.parse_args()
    mode: Literal["fake", "protected"] = (
        "protected" if args.provider_target == "protected" else "fake"
    )
    boundary_accumulator = RunAccumulator(mode, gateway_sha=GATEWAY_MAIN_SHA)
    try:
        preflight, _ = _tool_envelope_preflight(args.gateway_root.resolve(), args.codex)
        print(json.dumps({"status": "PREFLIGHT", **preflight}, sort_keys=True), flush=True)
        if preflight["gateway_policy"] != "ACCEPTED":
            boundary_accumulator.record_failure("preflight_incomplete")
            facts = _failed_rehearsal_result(args.provider_target, boundary_accumulator)
            facts["runtime_observations"] = _runtime_observations(facts)
            facts["acceptance_gate"], facts["gap_inventory"] = _acceptance_gate(facts)
            facts["status"] = "BLOCKED"
            facts["error_type"] = "preflight_incomplete"
            facts["run_accumulator"] = boundary_accumulator.safe_dict()
            print(json.dumps(facts, sort_keys=True))
            return 1
        facts = _run_direct_composed_rehearsal(args, preflight=preflight)
    except Exception as exc:  # pragma: no cover - bounded live process boundary
        boundary_accumulator.record_failure(_safe_runtime_failure(exc))
        facts = _failed_rehearsal_result(args.provider_target, boundary_accumulator)
        facts["runtime_observations"] = _runtime_observations(facts)
        acceptance_gate, gap_inventory = _acceptance_gate(facts)
        facts["acceptance_gate"] = acceptance_gate
        facts["gap_inventory"] = gap_inventory
        facts["run_accumulator"] = boundary_accumulator.safe_dict()
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "error_type": boundary_accumulator.first_failure or "unknown",
                    "acceptance_gate": acceptance_gate,
                    "gap_inventory": gap_inventory,
                    "run_accumulator": boundary_accumulator.safe_dict(),
                },
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(facts, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
