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
import http.server
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx
from openai import APIStatusError, OpenAI
from prometheus_client.parser import text_string_to_metric_families

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.dont_write_bytecode = True

from codex_tool_envelope_differential import (  # noqa: E402
    VariantResult,
    run_differential,
)

from slaif_local_coding.gateway_identity import (  # noqa: E402
    canonical_identity_bytes,
    expected_signature,
)
from tests.helpers.e2e_support import governed_prompt, run_codex_once  # noqa: E402
from tests.helpers.gateway_accounting_rehearsal import (  # noqa: E402
    GATEWAY_MAIN_SHA,
    PROVIDER,
    PUBLIC_MODEL,
    RESPONSES_ENDPOINT,
    UPSTREAM_MODEL,
    GatewayRehearsalFacts,
    assert_gateway_rehearsal_facts,
)
from tests.helpers.path_safety import assert_allowlisted_diagnostic_argv  # noqa: E402
from tests.helpers.vision_e2e_support import (  # noqa: E402
    VISION_MODEL,
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
CODEX_MODULE_VERSION = "3"
CODEX_FIXTURE_SHA256 = "ca1e03a35de1eaeceb894cec9895af0c154e0d2fa0aa8da87f98716e1567f9ec"


class _FakeQwenServer(http.server.ThreadingHTTPServer):
    """Direct fake provider; it intentionally has no relay/status endpoint."""

    daemon_threads = True

    def __init__(self, token: str) -> None:
        super().__init__(("127.0.0.1", 0), _FakeQwenHandler)
        self.token = token
        self.calls = 0
        self.compiler_calls = 0
        self.inference_calls = 0
        self.stream_calls = 0
        self.tool_types: set[str] = set()
        self.post_path_classes: set[str] = set()
        self.bad_auth = False
        self._lock = threading.Lock()

    def record(self, *, compiler: bool, streaming: bool, tool_types: set[str]) -> None:
        with self._lock:
            self.calls += 1
            if compiler:
                self.compiler_calls += 1
            else:
                self.inference_calls += 1
                if streaming:
                    self.stream_calls += 1
            self.tool_types.update(tool_types)

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            return {
                "calls": self.calls,
                "compiler_calls": self.compiler_calls,
                "inference_calls": self.inference_calls,
                "stream_calls": self.stream_calls,
                "tool_types": sorted(self.tool_types),
                "post_path_classes": sorted(self.post_path_classes),
                "bad_auth": self.bad_auth,
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
    def _response() -> dict[str, object]:
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
                            "text": "bounded fake response",
                            "annotations": [],
                        }
                    ],
                }
            ],
            "usage": {"input_tokens": 2, "output_tokens": 2, "total_tokens": 4},
        }

    def _stream(self) -> None:
        response_id = "fake-response"
        events = (
            {
                "type": "response.created",
                "response": {"id": response_id, "status": "in_progress", "model": PUBLIC_MODEL},
            },
            {"type": "response.output_text.delta", "delta": "bounded"},
            {
                "type": "response.completed",
                "response": {
                    "id": response_id,
                    "status": "completed",
                    "output": [],
                    "usage": {"input_tokens": 2, "output_tokens": 2, "total_tokens": 4},
                },
            },
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        for event in events:
            wire = f"event: {event['type']}\ndata: {json.dumps(event, separators=(',', ':'))}\n\n"
            self.wfile.write(wire.encode("utf-8"))
            self.wfile.flush()

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
        self.server.post_path_classes.add(
            "responses"
            if request_path == "/v1/responses"
            else "compiler"
            if request_path == "/v1/chat/completions"
            else "bare_responses"
            if request_path == "/responses"
            else "double_v1_responses"
            if request_path == "/v1/v1/responses"
            else "responses_trailing_slash"
            if request_path == "/v1/responses/"
            else "responses_query"
            if self.path.startswith("/v1/responses?")
            else "responses_variant"
            if request_path.startswith("/v1/responses")
            else "chat_variant"
            if request_path.startswith("/v1/chat/completions")
            else "other"
        )
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
        self.server.record(
            compiler=False, streaming=streaming, tool_types=self._tool_types(payload)
        )
        if streaming:
            self._stream()
        else:
            self._json(200, self._response())


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
            "--property=ActiveState,SubState,MainPID,ExecMainStartTimestampMonotonic",
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
        "text_inactive": text_values.get("ActiveState") == "inactive"
        and text_values.get("MainPID") == "0",
        "has_18020": bool(re.search(r":18020\b", listener_text)),
        "has_18021": bool(re.search(r":18021\b", listener_text)),
        "has_18031": bool(re.search(r":18031\b", listener_text)),
    }


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
    from slaif_gateway.config import Settings
    from slaif_gateway.db.repositories.audit import AuditRepository
    from slaif_gateway.db.repositories.institutions import InstitutionsRepository
    from slaif_gateway.db.repositories.keys import GatewayKeysRepository
    from slaif_gateway.db.repositories.one_time_secrets import OneTimeSecretsRepository
    from slaif_gateway.db.repositories.owners import OwnersRepository
    from slaif_gateway.db.repositories.pricing import PricingRulesRepository
    from slaif_gateway.db.repositories.provider_configs import ProviderConfigsRepository
    from slaif_gateway.db.repositories.routing import ModelRoutesRepository
    from slaif_gateway.schemas.keys import CreateGatewayKeyInput
    from slaif_gateway.services.key_service import KeyService
    from slaif_gateway.services.responses_route_capabilities import default_responses_capabilities
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

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
                    "fixture_sha256": CODEX_FIXTURE_SHA256,
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
    from slaif_gateway.db.models import GatewayKey, ModelRoute, QuotaReservation, UsageLedger
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

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


def _decimal_text(value: Decimal | None) -> str:
    if value is None:
        return "missing"
    return format(value.normalize(), "f")


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


def _request_metric_classes(metrics: str) -> tuple[str, ...]:
    """Return bounded endpoint/status classes for a disposable failure diagnostic."""
    totals: dict[tuple[str, str, str], int] = {}
    for family in text_string_to_metric_families(metrics):
        for sample in family.samples:
            if sample.name != "slaif_requests_total":
                continue
            endpoint = sample.labels.get("endpoint", "unsupported")
            endpoint_class = {
                "/v1/responses": "responses",
                "/v1/chat/completions": "chat",
                "/health": "health",
                "/v1/models": "models",
            }.get(endpoint, "unsupported")
            status = sample.labels.get("status", "other")
            route = sample.labels.get("route", "other")
            key = (endpoint_class, status, "local" if route == LOCAL_ROUTE else "other")
            totals[key] = totals.get(key, 0) + int(float(sample.value))
    return tuple(
        f"{endpoint}_{status}_{route}_{count}"
        for (endpoint, status, route), count in sorted(totals.items())
        if count > 0
    )


def _adapter_metrics(client: httpx.Client, adapter_port: int) -> str:
    response = client.get(f"http://127.0.0.1:{adapter_port}/metrics")
    if response.status_code != 200:
        raise RuntimeError("candidate_metrics_unavailable")
    return response.text


def _wait_status(client: httpx.Client, url: str, *, headers: dict[str, str] | None = None) -> int:
    deadline = time.monotonic() + 45
    last_status = 0
    while time.monotonic() < deadline:
        try:
            response = client.get(url, headers=headers)
            last_status = response.status_code
            if response.status_code < 500:
                return response.status_code
        except httpx.HTTPError:
            pass
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


def _disable_catalog_search_tools(path: Path) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    models = document.get("models")
    selected = next(item for item in models if item.get("slug") == PUBLIC_MODEL)
    selected["experimental_supported_tools"] = []
    selected["supports_search_tool"] = False
    selected["web_search_tool_type"] = "text"
    path.write_text(json.dumps(document, separators=(",", ":")), encoding="utf-8")
    os.chmod(path, 0o600)


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


def _run_rehearsal(
    args: argparse.Namespace, *, preflight: dict[str, object]
) -> GatewayRehearsalFacts:
    started = time.monotonic()
    gateway_root = args.gateway_root.resolve()
    # Keep the venv launcher path itself; resolving its symlink would bypass
    # the disposable venv and execute the system interpreter.
    gateway_python = Path(args.gateway_python).absolute()
    if (
        _run_command(["git", "-C", str(gateway_root), "rev-parse", "HEAD"]).stdout.strip()
        != GATEWAY_MAIN_SHA
    ):
        raise RuntimeError("gateway_sha_mismatch")
    checkout_clean_before = not bool(
        _run_command(["git", "-C", str(gateway_root), "status", "--short"]).stdout.strip()
    )
    if not checkout_clean_before:
        raise RuntimeError("gateway_checkout_dirty")
    codex = Path(args.codex).resolve()
    codex_version = _codex_version(codex)
    if codex_version != CODEX_VERSION:
        raise RuntimeError("codex_version_mismatch")
    qwen_key = os.environ.get(QWEN_KEY_ENV)
    if not qwen_key:
        raise RuntimeError("protected_qwen_key_unavailable")
    before_protected = _protected_snapshot()
    if not before_protected["vision_active"] or not before_protected["has_18020"]:
        raise RuntimeError("protected_vision_fixture_not_active")
    if not before_protected["text_inactive"] or before_protected["has_18021"]:
        raise RuntimeError("protected_fixture_precondition_failed")
    gateway_port = _free_loopback_port()
    adapter_port = _free_loopback_port(18031)
    if adapter_port != 18031:
        raise RuntimeError("candidate_port_18031_not_free")
    gateway_url = f"http://127.0.0.1:{gateway_port}"
    synthetic = _gateway_settings(gateway_url)
    service_token = "synthetic-005c-adapter-service-token"
    gateway_key: str | None = None
    gateway_process: subprocess.Popen[bytes] | None = None
    candidate_process: subprocess.Popen[bytes] | None = None
    postgres_name: str | None = None
    postgres_image_was_absent = False
    postgres_image_id: str | None = None
    postgres_image_digest: str | None = None
    container_removed = False
    image_removed = False
    logs: tuple[Path, ...] = ()
    temporary_name: str | None = None
    fact: GatewayRehearsalFacts | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="slaif-005c-rehearsal-") as temporary:
            temporary_name = temporary
            temp_root = Path(temporary)
            gateway_log_path = temp_root / "gateway.log"
            candidate_log_path = temp_root / "candidate.log"
            logs = (gateway_log_path, candidate_log_path)
            fixture = write_vision_fixture(temp_root / "fixture", gateway_url + "/v1", QWEN_KEY_ENV)
            adapter_config_text = fixture.adapter_config.read_text(encoding="utf-8")
            adapter_config_text = adapter_config_text.replace(
                "[upstream]\n",
                '[gateway_ingress]\nmode = "service_bearer_static_identity"\n'
                f'service_token_env = "{SERVICE_TOKEN_ENV}"\n\n[upstream]\n',
                1,
            )
            fixture.adapter_config.write_text(adapter_config_text, encoding="utf-8")
            os.chmod(fixture.adapter_config, 0o600)
            codex_config_text = fixture.codex_config.read_text(encoding="utf-8")
            codex_config_text = codex_config_text.replace(
                f'model = "{VISION_MODEL}"', f'model = "{PUBLIC_MODEL}"', 1
            ).replace(f'env_key = "{QWEN_KEY_ENV}"', f'env_key = "{PUBLIC_KEY_ENV}"', 1)
            fixture.codex_config.write_text(codex_config_text, encoding="utf-8")
            os.chmod(fixture.codex_config, 0o600)
            fixture = replace(fixture, api_key_env=PUBLIC_KEY_ENV)
            write_vision_model_catalog(codex, fixture.model_catalog, model=PUBLIC_MODEL)
            _disable_catalog_search_tools(fixture.model_catalog)
            if not _public_model_catalog_ok(fixture.model_catalog):
                raise RuntimeError("codex_catalog_contract_failed")

            (
                postgres_name,
                postgres_port,
                tmpfs_only,
                postgres_image_was_absent,
                postgres_image_id,
                postgres_image_digest,
            ) = _docker_start_postgres()
            database_url = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@127.0.0.1:{postgres_port}/{DATABASE_NAME}"
            gateway_env = _gateway_environment(
                gateway_root=gateway_root,
                database_url=database_url,
                gateway_port=gateway_port,
                hmac_secret=synthetic["hmac_secret"],
                encryption_key=synthetic["encryption_key"],
                service_token=service_token,
                signing_secret="synthetic-005c-signing-secret-0123456789",
                derivation_secret="synthetic-005c-derivation-secret-0123456789",
            )
            migrate_env = dict(gateway_env)
            migration_succeeded = False
            for _ in range(3):
                migration = _run_command(
                    [str(gateway_python), "-m", "alembic", "upgrade", "head"],
                    cwd=gateway_root,
                    env=migrate_env,
                )
                if migration.returncode == 0:
                    migration_succeeded = True
                    break
                time.sleep(1)
            if not migration_succeeded:
                raise RuntimeError("gateway_migration_failed")
            seeded = asyncio.run(
                _seed_database(
                    gateway_root,
                    database_url,
                    adapter_port=adapter_port,
                    failure_port=_free_loopback_port(),
                    hmac_secret=synthetic["hmac_secret"],
                    encryption_key=synthetic["encryption_key"],
                )
            )
            gateway_key = seeded["plaintext_key"]
            seeded_key_id = seeded["gateway_key_id"]
            candidate_process = _build_candidate_process(
                gateway_python,
                fixture.adapter_config,
                _candidate_environment(
                    service_token,
                    qwen_key,
                    "synthetic-005c-signing-secret-0123456789",
                ),
                candidate_log_path,
            )
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                candidate_health = _wait_status(
                    http,
                    f"http://127.0.0.1:{adapter_port}/health",
                    headers={"Authorization": f"Bearer {service_token}"},
                )
                candidate_ready = _wait_status(http, f"http://127.0.0.1:{adapter_port}/readyz")
                if candidate_health != 200 or candidate_ready != 200:
                    raise RuntimeError("candidate_not_ready")
            gateway_process = _build_gateway_process(
                gateway_python, gateway_root, gateway_port, gateway_env, gateway_log_path
            )
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                gateway_health = _wait_status(http, f"{gateway_url}/healthz")
                gateway_ready = _wait_status(http, f"{gateway_url}/readyz")
            if gateway_health != 200 or gateway_ready != 200:
                raise RuntimeError("gateway_not_ready")
            if not gateway_key:
                raise RuntimeError("seed_key_unavailable")
            client = OpenAI(
                api_key=gateway_key,
                base_url=gateway_url + "/v1/",
                timeout=120,
                max_retries=0,
            )
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                before_unauthorized = _metric_sum(
                    _adapter_metrics(http, adapter_port), "slaif_requests_total"
                )
                unauthorized = http.get(
                    f"{gateway_url}/v1/models",
                    headers={"Authorization": "Bearer sk-slaif-invalid." + "a" * 43},
                )
                after_unauthorized = _metric_sum(
                    _adapter_metrics(http, adapter_port), "slaif_requests_total"
                )
                unauthorized_status = unauthorized.status_code
            models = client.models.list()
            model_ids = tuple(str(item.id) for item in models.data)
            text_response = client.responses.create(
                model=PUBLIC_MODEL,
                input="Return a short acknowledgment.",
                max_output_tokens=32,
                store=False,
            )
            text_usage = getattr(getattr(text_response, "usage", None), "total_tokens", None)
            if not isinstance(text_usage, int):
                raise RuntimeError("text_usage_missing")
            stream_types: list[str] = []
            stream_completed_usage = False
            stream = client.responses.create(
                model=PUBLIC_MODEL,
                input="Return one short streamed acknowledgment.",
                max_output_tokens=32,
                tools=[
                    {
                        "type": "namespace",
                        "name": "functions",
                        "tools": [
                            {
                                "type": "function",
                                "name": "rehearsal_noop",
                                "description": (
                                    "A bounded no-op tool that must not be called in this turn."
                                ),
                                "parameters": {
                                    "type": "object",
                                    "properties": {},
                                    "additionalProperties": False,
                                },
                            }
                        ],
                    }
                ],
                tool_choice="none",
                stream=True,
            )
            for event in stream:
                event_type = getattr(event, "type", None)
                if isinstance(event_type, str):
                    stream_types.append(event_type)
                if event_type == "response.completed":
                    usage = getattr(getattr(event, "response", None), "usage", None)
                    stream_completed_usage = isinstance(getattr(usage, "total_tokens", None), int)
            data_url = "data:image/png;base64," + base64.b64encode(
                fixture.full_image.path.read_bytes()
            ).decode("ascii")
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                before_image = _adapter_metrics(http, adapter_port)
            image_response = client.responses.create(
                model=PUBLIC_MODEL,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "Describe this synthetic image briefly.",
                            },
                            {"type": "input_image", "image_url": data_url, "detail": "auto"},
                        ],
                    }
                ],
                max_output_tokens=32,
                store=False,
            )
            if getattr(image_response, "usage", None) is None:
                raise RuntimeError("image_usage_missing")
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                after_image = _adapter_metrics(http, adapter_port)
                before_codex_metrics = _adapter_metrics(http, adapter_port)
            before_codex_rows = asyncio.run(_db_snapshot(gateway_root, database_url, seeded_key_id))
            public_key_previous = os.environ.get(PUBLIC_KEY_ENV)
            os.environ[PUBLIC_KEY_ENV] = gateway_key
            try:
                codex_run = run_codex_once(
                    codex,
                    fixture,
                    governed_prompt(),
                    timeout_seconds=300,
                    expected_command="cat GOVERNANCE-DEPENDENCY.md",
                    feature_flags=tuple(preflight["feature_flags"]),
                    ignore_user_config=bool(preflight["ignore_user_config"]),
                    provider_base_url=(
                        f"{gateway_url}/v1" if bool(preflight["ignore_user_config"]) else None
                    ),
                    model=PUBLIC_MODEL,
                )
            finally:
                if public_key_previous is None:
                    os.environ.pop(PUBLIC_KEY_ENV, None)
                else:
                    os.environ[PUBLIC_KEY_ENV] = public_key_previous
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                after_codex_metrics = _adapter_metrics(http, adapter_port)
            after_codex_rows = asyncio.run(_db_snapshot(gateway_root, database_url, seeded_key_id))
            asyncio.run(_tighten_request_limit(gateway_root, database_url, seeded_key_id))
            codex_request_count = int(codex_run.event_type_counts.get("response.created", 0))
            compiler_attempt_delta = _metric_sum(
                after_codex_metrics, "slaif_constitution_compiler_attempts_total"
            ) - _metric_sum(before_codex_metrics, "slaif_constitution_compiler_attempts_total")
            compiler_success_delta = _metric_sum(
                after_codex_metrics, "slaif_constitution_compiler_successes_total"
            ) - _metric_sum(before_codex_metrics, "slaif_constitution_compiler_successes_total")
            over_quota_status = 0
            over_quota_candidate_delta = 0
            for _ in range(3):
                with httpx.Client(timeout=30, follow_redirects=False) as http:
                    before_quota = _metric_sum(
                        _adapter_metrics(http, adapter_port), "slaif_requests_total"
                    )
                try:
                    client.responses.create(
                        model=PUBLIC_MODEL,
                        input="quota probe",
                        max_output_tokens=8,
                        store=False,
                    )
                except APIStatusError as exc:
                    if exc.status_code not in {402, 429}:
                        raise RuntimeError("unexpected_quota_probe_failure") from None
                    over_quota_status = int(exc.status_code)
                    with httpx.Client(timeout=30, follow_redirects=False) as http:
                        over_quota_candidate_delta = (
                            _metric_sum(
                                _adapter_metrics(http, adapter_port), "slaif_requests_total"
                            )
                            - before_quota
                        )
                    break
            if over_quota_status == 0:
                raise RuntimeError("quota_rejection_not_observed")
            final_rows = asyncio.run(_db_snapshot(gateway_root, database_url, seeded_key_id))
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                image_seen_delta = _metric_sum(
                    after_image,
                    "slaif_image_items_total",
                    {"route": "qwen38-vision-codex", "result": "seen"},
                ) - _metric_sum(
                    before_image,
                    "slaif_image_items_total",
                    {"route": "qwen38-vision-codex", "result": "seen"},
                )
                image_removed_delta = _metric_sum(
                    after_image,
                    "slaif_image_items_total",
                    {"route": "qwen38-vision-codex", "result": "removed"},
                ) - _metric_sum(
                    before_image,
                    "slaif_image_items_total",
                    {"route": "qwen38-vision-codex", "result": "removed"},
                )
            safe_log_values = (
                service_token,
                qwen_key,
                gateway_key,
                fixture.sentinel_token,
                "GOVERNANCE-DEPENDENCY.md",
            )
            logs_clean = _secret_free_logs(logs, safe_log_values)
            before_codex_request_count = before_codex_rows["ledger_count"]
            after_codex_request_count = after_codex_rows["ledger_count"]
            fact = GatewayRehearsalFacts(
                gateway_sha=GATEWAY_MAIN_SHA,
                gateway_checkout_clean_before=checkout_clean_before,
                gateway_checkout_clean_after=False,
                postgres_image_preexisted=not postgres_image_was_absent,
                postgres_image_pulled=postgres_image_was_absent,
                postgres_image_removed=False,
                postgres_tmpfs_only=tmpfs_only,
                gateway_health_status=gateway_health,
                gateway_ready_status=gateway_ready,
                candidate_health_status=candidate_health,
                candidate_ready_status=candidate_ready,
                models_status=200,
                models_visible_count=len(model_ids),
                models_visible_expected=model_ids == (PUBLIC_MODEL,),
                text_status=200,
                text_usage_total=int(text_usage),
                stream_status=200,
                stream_event_types=tuple(stream_types),
                stream_completed_usage=stream_completed_usage,
                image_status=200,
                image_seen_delta=image_seen_delta,
                image_removed_delta=image_removed_delta,
                codex_version=codex_version,
                codex_exit_status=codex_run.exit_status,
                codex_tool_calls=codex_run.tool_calls,
                codex_dependency_reads=codex_run.dependency_observation.successful_dependency_reads,
                codex_sentinel_passed=codex_run.sentinel_passed,
                codex_effective_governance=codex_run.failure_reason == "success"
                and codex_run.dependency_observation.lifecycle == "success",
                codex_public_request_count=codex_request_count,
                compiler_attempt_delta=compiler_attempt_delta,
                compiler_success_delta=compiler_success_delta,
                compiler_added_gateway_rows=after_codex_request_count
                - before_codex_request_count
                - codex_request_count,
                unauthorized_status=unauthorized_status,
                unauthorized_candidate_request_delta=after_unauthorized - before_unauthorized,
                over_quota_status=over_quota_status,
                over_quota_candidate_request_delta=over_quota_candidate_delta,
                reservation_count=final_rows["reservation_count"],
                finalized_reservation_count=final_rows["finalized_reservation_count"],
                pending_reservation_count=final_rows["pending_reservation_count"],
                ledger_count=final_rows["ledger_count"],
                finalized_ledger_count=final_rows["finalized_ledger_count"],
                failed_ledger_count=final_rows["failed_ledger_count"],
                duplicate_request_id_count=final_rows["duplicate_request_id_count"],
                provider_usage_rows=final_rows["provider_usage_rows"],
                key_requests_used=final_rows["key_requests_used"],
                key_requests_reserved=final_rows["key_requests_reserved"],
                key_tokens_used=final_rows["key_tokens_used"],
                key_tokens_reserved=final_rows["key_tokens_reserved"],
                key_cost_used_eur=final_rows["key_cost_used_eur"],
                key_cost_reserved_eur=final_rows["key_cost_reserved_eur"],
                ledger_total_tokens=final_rows["ledger_total_tokens"],
                ledger_total_cost_eur=final_rows["ledger_total_cost_eur"],
                route_metadata_ok=final_rows["route_metadata_ok"],
                gateway_key_not_forwarded=logs_clean and candidate_health == 200,
                adapter_service_token_not_forwarded=logs_clean and candidate_ready == 200,
                qwen_credential_boundary_ok=candidate_ready == 200
                and QWEN_KEY_ENV not in gateway_env,
                compiler_not_accounted_as_public=(
                    compiler_attempt_delta > 0
                    and after_codex_request_count - before_codex_request_count
                    == codex_request_count
                ),
                gateway_logs_secret_free=logs_clean,
                candidate_logs_secret_free=logs_clean,
                candidate_listener_removed=False,
                gateway_listener_removed=False,
                postgres_container_removed=False,
                temporary_state_removed=False,
                protected_vision_pid_unchanged=False,
                protected_vision_start_unchanged=False,
                protected_vision_listener_unchanged=False,
                text_service_still_inactive=False,
                no_18021_listener=False,
                no_18031_listener=False,
            )
    finally:
        _stop_process(gateway_process)
        _stop_process(candidate_process)
        container_removed, image_removed = _docker_cleanup(postgres_name, postgres_image_was_absent)
        after_protected = _protected_snapshot()
        checkout_clean_after = not bool(
            _run_command(["git", "-C", str(gateway_root), "status", "--short"]).stdout.strip()
        )
        if fact is not None:
            gateway_listener_removed = not bool(
                _run_command(["ss", "-ltnp"]).stdout
                and re.search(rf":{gateway_port}\b", _run_command(["ss", "-ltnp"]).stdout)
            )
            candidate_listener_removed = not bool(
                re.search(r":18031\b", _run_command(["ss", "-ltnp"]).stdout)
            )
            fact = replace(
                fact,
                gateway_checkout_clean_after=checkout_clean_after,
                postgres_image_removed=image_removed,
                candidate_listener_removed=candidate_listener_removed,
                gateway_listener_removed=gateway_listener_removed,
                postgres_container_removed=container_removed,
                protected_vision_pid_unchanged=before_protected["vision_pid"]
                == after_protected["vision_pid"],
                protected_vision_start_unchanged=before_protected["vision_start"]
                == after_protected["vision_start"],
                protected_vision_listener_unchanged=before_protected["has_18020"]
                == after_protected["has_18020"],
                text_service_still_inactive=bool(after_protected["text_inactive"]),
                no_18021_listener=not bool(after_protected["has_18021"]),
                no_18031_listener=not bool(after_protected["has_18031"]),
            )
    if fact is None:
        raise RuntimeError("rehearsal_did_not_produce_facts")
    if temporary_name is not None:
        fact = replace(fact, temporary_state_removed=not Path(temporary_name).exists())
    assert_gateway_rehearsal_facts(fact)
    if time.monotonic() - started > MAX_REHEARSAL_SECONDS:
        raise RuntimeError("rehearsal_time_budget_exceeded")
    return fact


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


def _stream_event_types(chunks: object) -> tuple[str, ...]:
    """Parse only bounded event type labels from a transient streaming body."""
    if not isinstance(chunks, list):
        return ()
    line_buffer = bytearray()
    event_types: list[str] = []
    for chunk in chunks:
        if not isinstance(chunk, bytes):
            continue
        line_buffer.extend(chunk)
        while b"\n" in line_buffer:
            line, _, remainder = line_buffer.partition(b"\n")
            line_buffer = bytearray(remainder)
            line = bytes(line.rstrip(b"\r"))
            if not line.startswith(b"data:"):
                continue
            data = line[5:].lstrip(b" ")
            try:
                payload = json.loads(data)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if isinstance(payload, dict) and isinstance(payload.get("type"), str):
                event_types.append(payload["type"])
    return tuple(event_types)


def _timed_public_stream(
    gateway_url: str, gateway_key: str, body: dict[str, object]
) -> tuple[int, tuple[str, ...], dict[str, str]]:
    """Run the ordinary client-boundary stream and emit only timing buckets."""
    from scripts.local_qwen_provider_differential import _timing_bucket

    started = time.monotonic()
    timing: dict[str, str] = {}
    chunks: list[bytes] = []
    with httpx.Client(timeout=300, follow_redirects=False) as http:
        with http.stream(
            "POST",
            f"{gateway_url}/v1/responses",
            headers={
                "Authorization": f"Bearer {gateway_key}",
                "Accept": "text/event-stream",
                "Content-Type": "application/json",
            },
            content=json.dumps(body, separators=(",", ":")).encode("utf-8"),
        ) as response:
            bucket = _timing_bucket(time.monotonic() - started)
            if bucket is not None:
                timing["response_headers"] = bucket
            if not 200 <= response.status_code < 300:
                return response.status_code, (), timing
            for chunk in response.iter_raw():
                if not chunk:
                    continue
                if "first_sse_bytes" not in timing:
                    bucket = _timing_bucket(time.monotonic() - started)
                    if bucket is not None:
                        timing["first_sse_bytes"] = bucket
                chunks.append(chunk)
            event_types = _stream_event_types(chunks)
            if "response.completed" in event_types:
                bucket = _timing_bucket(time.monotonic() - started)
                if bucket is not None:
                    timing["terminal_completion"] = bucket
    bucket = _timing_bucket(time.monotonic() - started)
    if bucket is not None:
        timing["normal_close"] = bucket
    return response.status_code, event_types, timing


def _response_status(call: Any) -> int:
    try:
        call()
    except APIStatusError as exc:
        return int(exc.status_code)
    return 200


def _signed_probe_headers(service_token: str, signing_secret: str) -> dict[str, str]:
    timestamp = str(int(time.time()))
    nonce = secrets.token_urlsafe(16)
    principal = "synthetic-probe-principal"
    session = "synthetic-probe-session"
    repository = "synthetic-probe-repository"
    canonical = canonical_identity_bytes(
        method="GET",
        path="/health",
        raw_query=b"",
        body=b"",
        principal=principal,
        session=session,
        repository=repository,
        route=LOCAL_ROUTE,
        timestamp=timestamp,
        nonce=nonce,
    )
    return {
        "Authorization": f"Bearer {service_token}",
        "X-SLAIF-Identity-Version": "v1",
        "X-SLAIF-Principal": principal,
        "X-SLAIF-Session": session,
        "X-SLAIF-Repository": repository,
        "X-SLAIF-Route": LOCAL_ROUTE,
        "X-SLAIF-Timestamp": timestamp,
        "X-SLAIF-Nonce": nonce,
        "X-SLAIF-Signature": expected_signature(
            secret=signing_secret.encode("ascii"), canonical=canonical
        ),
    }


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


def _openai_kwargs(body: dict[str, object]) -> dict[str, object]:
    """Move only the synthetic client metadata into the SDK extension field."""
    result = dict(body)
    metadata = result.pop("client_metadata", None)
    if metadata is not None:
        result["extra_body"] = {"client_metadata": metadata}
    return result


def _run_direct_composed_rehearsal(
    args: argparse.Namespace, *, preflight: dict[str, object]
) -> dict[str, object]:
    """Run one direct Gateway -> Local -> provider composition.

    The provider target is the only topology variable.  In particular, there
    is no forwarding relay or provider-side status endpoint in this driver.
    """
    provider_target = str(args.provider_target)
    if provider_target not in {"fake", "protected"}:
        raise RuntimeError("provider_target_invalid")
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
    protected_before = _protected_snapshot() if provider_target == "protected" else None
    if provider_target == "protected":
        if codex_version != CODEX_VERSION:
            raise RuntimeError("codex_version_mismatch")
        if not os.environ.get(QWEN_KEY_ENV):
            raise RuntimeError("protected_qwen_key_unavailable")
        if (
            not protected_before
            or not protected_before["vision_active"]
            or not protected_before["has_18020"]
        ):
            raise RuntimeError("protected_vision_fixture_not_active")
        if not protected_before["text_inactive"] or protected_before["has_18021"]:
            raise RuntimeError("protected_fixture_precondition_failed")
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
    candidate_process: subprocess.Popen[bytes] | None = None
    postgres_name: str | None = None
    postgres_image_was_absent = False
    temporary_name: str | None = None
    logs_clean = False
    result: dict[str, object] = {}
    logs: tuple[Path, ...] = ()
    try:
        with tempfile.TemporaryDirectory(prefix="slaif-005k-composed-") as temporary:
            temporary_name = temporary
            temp_root = Path(temporary)
            gateway_log = temp_root / "gateway.log"
            candidate_log = temp_root / "candidate.log"
            logs = (gateway_log, candidate_log)
            if provider_target == "fake":
                fake_server = _FakeQwenServer("synthetic-005k-qwen-token")
                fake_thread = _start_threaded_server(fake_server)
                provider_url = f"http://127.0.0.1:{fake_server.server_address[1]}"
                qwen_key = fake_server.token
            else:
                provider_url = "http://127.0.0.1:18020"
                qwen_key = os.environ[QWEN_KEY_ENV]
            if provider_target == "fake":
                with httpx.Client(timeout=10, follow_redirects=False) as http:
                    fake_health = http.get(
                        f"{provider_url}/health",
                        headers={"Authorization": f"Bearer {qwen_key}"},
                    )
                if fake_health.status_code != 200:
                    raise RuntimeError("fake_provider_not_ready")
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
            _disable_catalog_search_tools(fixture.model_catalog)
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
            candidate_process = _build_candidate_process(
                gateway_python,
                fixture.adapter_config,
                _candidate_environment(service_token, qwen_key, signing_secret),
                candidate_log,
            )
            with httpx.Client(timeout=45, follow_redirects=False) as http:
                candidate_ready = _wait_status(http, f"http://127.0.0.1:{adapter_port}/readyz")
                candidate_health = _wait_status(
                    http,
                    f"http://127.0.0.1:{adapter_port}/healthz",
                )
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
            session_a = str(uuid.uuid4())
            session_b = str(uuid.uuid4())
            local_tools = [
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
            adapter_tools = [
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
            try:
                text_response = client.responses.create(
                    **_openai_kwargs(
                        _composed_request_body(session_a, "ordinary non-stream", tools=local_tools)
                    ),
                    max_output_tokens=32,
                    store=False,
                )
            except APIStatusError as exc:
                provider_calls = "unknown"
                if fake_server is not None:
                    fake_snapshot = fake_server.snapshot()
                    provider_calls = str(fake_snapshot["calls"])
                    provider_path = (
                        "responses"
                        if "responses" in fake_snapshot["post_path_classes"]
                        else "bare_responses"
                        if "bare_responses" in fake_snapshot["post_path_classes"]
                        else "double_v1_responses"
                        if "double_v1_responses" in fake_snapshot["post_path_classes"]
                        else "responses_trailing_slash"
                        if "responses_trailing_slash" in fake_snapshot["post_path_classes"]
                        else "responses_query"
                        if "responses_query" in fake_snapshot["post_path_classes"]
                        else "responses_variant"
                        if "responses_variant" in fake_snapshot["post_path_classes"]
                        else "chat_variant"
                        if "chat_variant" in fake_snapshot["post_path_classes"]
                        else "compiler"
                        if "compiler" in fake_snapshot["post_path_classes"]
                        else "other"
                        if "other" in fake_snapshot["post_path_classes"]
                        else "none"
                    )
                else:
                    provider_path = "unknown"
                candidate_requests = "unknown"
                candidate_status = "unknown"
                candidate_route = "unknown"
                candidate_metric_classes = "unknown"
                try:
                    with httpx.Client(timeout=10, follow_redirects=False) as metrics_http:
                        candidate_metrics = _adapter_metrics(metrics_http, adapter_port)
                        candidate_requests = str(
                            _metric_sum(candidate_metrics, "slaif_requests_total")
                        )
                        candidate_metric_classes = (
                            ";".join(_request_metric_classes(candidate_metrics)) or "none"
                        )
                        candidate_status = next(
                            (
                                str(status)
                                for status in (200, 400, 401, 403, 404, 409, 422, 500, 502, 503)
                                if _metric_sum(
                                    candidate_metrics,
                                    "slaif_requests_total",
                                    {"status": str(status)},
                                )
                                > 0
                            ),
                            "none",
                        )
                        candidate_route = next(
                            (
                                "local" if route == LOCAL_ROUTE else route
                                for route in ("passthrough", LOCAL_ROUTE)
                                if _metric_sum(
                                    candidate_metrics,
                                    "slaif_requests_total",
                                    {"route": route},
                                )
                                > 0
                            ),
                            "none",
                        )
                except (OSError, httpx.HTTPError, RuntimeError):
                    pass
                error_code = "unknown"
                try:
                    error_payload = exc.response.json()
                    error_value = (
                        error_payload.get("error", {}).get("code")
                        if isinstance(error_payload, dict)
                        and isinstance(error_payload.get("error"), dict)
                        else None
                    )
                    if isinstance(error_value, str) and re.fullmatch(
                        r"[a-z0-9_]{1,96}", error_value
                    ):
                        error_code = error_value
                except (TypeError, ValueError):
                    pass
                raise RuntimeError(
                    f"text_status_{exc.status_code}_{error_code}_provider_calls_{provider_calls}"
                    f"_candidate_requests_{candidate_requests}"
                    f"_candidate_status_{candidate_status}"
                    f"_candidate_route_{candidate_route}"
                    f"_candidate_metrics_{candidate_metric_classes}"
                    f"_provider_path_{provider_path}"
                ) from None
            text_usage = getattr(getattr(text_response, "usage", None), "total_tokens", None)
            if not isinstance(text_usage, int) or text_usage <= 0:
                raise RuntimeError("text_usage_missing")
            stream_body = _composed_request_body(session_a, "ordinary stream", tools=adapter_tools)
            stream_body.update({"stream": True, "max_output_tokens": 32, "store": False})
            stream_status, stream_types, stream_timing = _timed_public_stream(
                gateway_url, seeded["plaintext_key"], stream_body
            )
            if (
                stream_status != 200
                or stream_types[-1:] != ("response.completed",)
                or not stream_timing
            ):
                raise RuntimeError("stream_contract_failed")
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
            root_kwargs = {
                "model": PUBLIC_MODEL,
                "input": root_input,
                "tools": adapter_tools,
                "extra_body": {
                    "client_metadata": _composed_request_body(
                        session_a, "root", tools=adapter_tools
                    )["client_metadata"]
                },
                "max_output_tokens": 32,
                "store": False,
            }
            client.responses.create(**root_kwargs)
            client.responses.create(**root_kwargs)
            zero_root = _openai_kwargs(_composed_request_body(session_a, "zero root rehydration"))
            zero_root.update({"max_output_tokens": 32, "store": False})
            client.responses.create(**zero_root)
            with httpx.Client(timeout=45, follow_redirects=False) as http:
                after_constitution = _adapter_metrics(http, adapter_port)
            compiler_before = _metric_sum(
                before_constitution, "slaif_constitution_compiler_attempts_total"
            )
            compiler_after = _metric_sum(
                after_constitution, "slaif_constitution_compiler_attempts_total"
            )
            cache_hits = _metric_sum(
                after_constitution, "slaif_constitution_cache_hits_total"
            ) - _metric_sum(before_constitution, "slaif_constitution_cache_hits_total")
            rehydration_hits = _metric_sum(
                after_constitution,
                "slaif_constitution_rehydration_total",
                {"state": "hit", "reason": "zero_root"},
            ) - _metric_sum(
                before_constitution,
                "slaif_constitution_rehydration_total",
                {"state": "hit", "reason": "zero_root"},
            )
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
                "client_metadata": _composed_request_body(session_b, "second owner root")[
                    "client_metadata"
                ]
            }
            second_client.responses.create(**second_root)
            asyncio.run(
                _tighten_request_limit(gateway_root, database_url, seeded["second_gateway_key_id"])
            )
            if _response_status(lambda: second_client.responses.create(**second_root)) not in {
                402,
                429,
            }:
                raise RuntimeError("second_key_quota_not_rejected")

            codex_facts: dict[str, object] = {"status": "NOT_RUN"}
            if provider_target == "protected":
                public_key_previous = os.environ.get(PUBLIC_KEY_ENV)
                os.environ[PUBLIC_KEY_ENV] = seeded["plaintext_key"]
                try:
                    codex_run = run_codex_once(
                        codex,
                        fixture,
                        governed_prompt(),
                        timeout_seconds=300,
                        expected_command="cat GOVERNANCE-DEPENDENCY.md",
                        feature_flags=tuple(preflight["feature_flags"]),
                        ignore_user_config=bool(preflight["ignore_user_config"]),
                        provider_base_url=(
                            gateway_url + "/v1" if bool(preflight["ignore_user_config"]) else None
                        ),
                        model=PUBLIC_MODEL,
                    )
                finally:
                    if public_key_previous is None:
                        os.environ.pop(PUBLIC_KEY_ENV, None)
                    else:
                        os.environ[PUBLIC_KEY_ENV] = public_key_previous
                codex_facts = {
                    "version": codex_version,
                    "exit_status": codex_run.exit_status,
                    "tool_calls": codex_run.tool_calls,
                    "dependency_reads": (
                        codex_run.dependency_observation.successful_dependency_reads
                    ),
                    "sentinel_passed": codex_run.sentinel_passed,
                    "effective_governance": (
                        codex_run.failure_reason == "success"
                        and codex_run.dependency_observation.lifecycle == "success"
                    ),
                }
                if codex_run.exit_status != 0 or not codex_run.sentinel_passed:
                    raise RuntimeError("codex_governance_acceptance_failed")

            invalid_status = _response_status(
                lambda: OpenAI(
                    api_key="sk-slaif-invalid", base_url=gateway_url + "/v1/", max_retries=0
                ).models.list()
            )
            if invalid_status not in {401, 403}:
                raise RuntimeError("invalid_public_key_not_rejected")
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
            failure_client = OpenAI(
                api_key=seeded["failure_plaintext_key"],
                base_url=gateway_url + "/v1/",
                timeout=30,
                max_retries=0,
            )
            failure_status = _response_status(
                lambda: failure_client.responses.create(
                    model=FAILURE_MODEL,
                    input="controlled provider failure",
                    max_output_tokens=8,
                    store=False,
                )
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
            result = {
                "status": "PARTIAL" if provider_target == "protected" else "PASSED",
                "provider_target": provider_target,
                "gateway_sha": GATEWAY_MAIN_SHA,
                "gateway_health_status": gateway_health,
                "gateway_ready_status": gateway_ready,
                "candidate_health_status": candidate_health,
                "candidate_ready_status": candidate_ready,
                "models_visible_expected": gateway_models_probe.status_code == 200,
                "text_status": 200,
                "text_usage_present": True,
                "stream_status": stream_status,
                "stream_event_types": stream_types,
                "stream_timing_buckets": stream_timing,
                "image_status": 200,
                "image_seen": image_seen,
                "image_removed": image_removed,
                "codex": codex_facts,
                "compiler_attempt_delta": compiler_after - compiler_before,
                "cache_hits": cache_hits,
                "rehydration_hits": rehydration_hits,
                "second_owner_isolated": True,
                "invalid_public_key_status": invalid_status,
                "over_quota_status": over_quota_status,
                "hosted_tool_choice_status": hosted_status,
                "controlled_failure_status": failure_status,
                "failure_provider_calls": failure_server.calls,
                "replay_tamper": "NOT_RUN_NO_REQUEST_RELAY",
                "relay_started": False,
                "provider_url_class": "fake_loopback"
                if provider_target == "fake"
                else "protected_loopback",
                "fake_provider": None if fake_server is None else fake_server.snapshot(),
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
                "postgres_tmpfs_only": tmpfs_only,
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
        _stop_process(gateway_process)
        _stop_process(candidate_process)
        _stop_threaded_server(fake_server, fake_thread)
        _stop_threaded_server(failure_server, failure_thread)
        _docker_cleanup(postgres_name, postgres_image_was_absent)
        if provider_target == "protected" and protected_before is not None:
            protected_after = _protected_snapshot()
            result["protected_unchanged"] = {
                "pid": protected_before["vision_pid"] == protected_after["vision_pid"],
                "start": protected_before["vision_start"] == protected_after["vision_start"],
                "listener": protected_before["has_18020"] == protected_after["has_18020"],
                "text_inactive": bool(protected_after["text_inactive"]),
                "no_18021": not bool(protected_after["has_18021"]),
                "no_18031": not bool(protected_after["has_18031"]),
            }
        else:
            result["protected_unchanged"] = "NOT_APPLICABLE_FAKE"
        result["gateway_listener_removed"] = not bool(
            re.search(rf":{gateway_port}\b", _run_command(["ss", "-ltnp"]).stdout)
        )
        result["candidate_listener_removed"] = not bool(
            re.search(r":18031\b", _run_command(["ss", "-ltnp"]).stdout)
        )
        result["temporary_state_removed"] = (
            temporary_name is not None and not Path(temporary_name).exists()
        )
        result["logs_secret_free"] = logs_clean
    if not result:
        raise RuntimeError("composed_rehearsal_did_not_produce_facts")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gateway-root", type=Path, required=True)
    parser.add_argument("--gateway-python", type=Path, required=True)
    parser.add_argument("--codex", type=Path, default=shutil.which("codex") or "codex")
    parser.add_argument("--provider-target", choices=("fake", "protected"), default="fake")
    args = parser.parse_args()
    try:
        preflight, _ = _tool_envelope_preflight(args.gateway_root.resolve(), args.codex)
        print(json.dumps({"status": "PREFLIGHT", **preflight}, sort_keys=True), flush=True)
        if preflight["gateway_policy"] != "ACCEPTED":
            print(
                json.dumps(
                    {"status": "FAILED", "error_type": "tool_envelope_preflight_gateway_rejected"},
                    sort_keys=True,
                )
            )
            return 1
        facts = _run_direct_composed_rehearsal(args, preflight=preflight)
    except Exception as exc:  # pragma: no cover - bounded live process boundary
        safe_code = str(exc)
        if not re.fullmatch(r"[a-z0-9_]{1,512}", safe_code):
            safe_code = (
                "runtime_error_empty"
                if isinstance(exc, RuntimeError) and not safe_code
                else type(exc).__name__
            )
        print(json.dumps({"status": "FAILED", "error_type": safe_code}, sort_keys=True))
        return 1
    print(json.dumps(facts, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
