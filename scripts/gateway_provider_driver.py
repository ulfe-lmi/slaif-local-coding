#!/usr/bin/env python3
"""Run the pinned gateway provider adapter against a disposable candidate.

This repository-only driver is deliberately outside the production package. It
starts a loopback Local Coding listener and a fake vLLM listener, then imports
the gateway adapter from an externally supplied, detached gateway checkout.
It prints only content-free facts.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import socket
import subprocess
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from slaif_local_coding.app import create_app  # noqa: E402
from slaif_local_coding.config import (  # noqa: E402
    CacheConfig,
    CompilerConfig,
    ConstitutionIntegrationConfig,
    GatewayIngressConfig,
    RehydrationConfig,
    RouteConfig,
    ServerConfig,
    Settings,
    UpstreamConfig,
)
from tests.helpers.gateway_provider_driver import (  # noqa: E402
    GATEWAY_MAIN_SHA,
    UPSTREAM_MODEL,
    ProviderDriverFacts,
    assert_provider_driver_facts,
    provider_request_field_names,
    safe_provider_request_body,
)

SERVICE_TOKEN = "adapter-driver-service-token"
QWEN_TOKEN = "qwen-driver-upstream-token"
CLIENT_TOKEN = "client-gateway-token"


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
    raise RuntimeError("no loopback port available")


def _pinned_gateway_sha(gateway_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(gateway_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("gateway checkout cannot be verified") from exc
    sha = result.stdout.strip()
    if sha != GATEWAY_MAIN_SHA:
        raise RuntimeError("gateway checkout is not the required pinned commit")
    return sha


def _load_gateway_types(gateway_root: Path) -> tuple[type[Any], type[Any], Any]:
    sys.path.insert(0, str(gateway_root / "app"))
    try:
        from slaif_gateway.providers.headers import build_provider_headers
        from slaif_gateway.providers.openai_compatible import (
            OpenAICompatibleProviderAdapter,
        )
        from slaif_gateway.schemas.providers import ProviderRequest
    except ImportError as exc:
        raise RuntimeError("pinned gateway provider imports are unavailable") from exc
    return OpenAICompatibleProviderAdapter, ProviderRequest, build_provider_headers


def _fake_vllm_app(state: dict[str, Any]) -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    async def stream_events():
        events = (
            {"type": "response.created", "id": "driver-response"},
            {"type": "response.output_text.delta", "delta": "ok"},
            {
                "type": "response.completed",
                "response": {
                    "status": "completed",
                    "usage": {"input_tokens": 3, "output_tokens": 2, "total_tokens": 5},
                },
            },
        )
        for event in events:
            yield f"data: {json.dumps(event, separators=(',', ':'))}\n\n".encode()

    @app.post("/v1/responses", response_model=None)
    async def responses(request: Request) -> JSONResponse | StreamingResponse:
        body = await request.json()
        state["upstream_auth_ok"] = request.headers.get("authorization") == f"Bearer {QWEN_TOKEN}"
        state["upstream_model"] = body.get("model")
        state["upstream_request_count"] = state.get("upstream_request_count", 0) + 1
        state["upstream_received_service_token"] = SERVICE_TOKEN in str(request.headers)
        if body.get("stream") is True:
            return StreamingResponse(stream_events(), media_type="text/event-stream")
        return JSONResponse(
            {
                "id": "driver-response",
                "object": "response",
                "model": body.get("model"),
                "output": [],
                "usage": {"input_tokens": 3, "output_tokens": 2, "total_tokens": 5},
            },
            headers={"X-Request-ID": "driver-upstream-request"},
        )

    return app


async def _start_server(app: FastAPI, port: int) -> tuple[uvicorn.Server, asyncio.Task[None]]:
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="critical",
        access_log=False,
        log_config=None,
    )
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    for _ in range(300):
        if server.started:
            return server, task
        if task.done():
            await task
        await asyncio.sleep(0.01)
    server.should_exit = True
    await task
    raise RuntimeError("disposable server did not start")


async def _stop_server(server: uvicorn.Server, task: asyncio.Task[None]) -> None:
    server.should_exit = True
    try:
        await asyncio.wait_for(task, timeout=5)
    except TimeoutError:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


def _candidate_settings(*, adapter_port: int, fake_port: int, cache_root: Path) -> Settings:
    return Settings(
        server=ServerConfig(listen_port=adapter_port, request_body_max_bytes=1_048_576),
        gateway_ingress=GatewayIngressConfig(
            mode="service_bearer_static_identity", service_token_env="SLAIF_DRIVER_SERVICE_TOKEN"
        ),
        upstream=UpstreamConfig(
            base_url=f"http://127.0.0.1:{fake_port}/v1",
            api_key_env="SLAIF_DRIVER_QWEN_TOKEN",
            model="qwen3.8-27b",
        ),
        routes=[
            RouteConfig(
                name="driver-route",
                model="qwen3.8-27b",
                image_overflow_policy="passthrough",
                observation_enabled=True,
                constitution_enabled=True,
            )
        ],
        compiler=CompilerConfig(enabled=True, api_key_env="SLAIF_DRIVER_QWEN_TOKEN"),
        cache=CacheConfig(root=cache_root, fallback_root=cache_root / "fallback"),
        constitution=ConstitutionIntegrationConfig(
            enabled=True,
            principal="driver-static-principal",
            session="driver-static-session",
            repository="driver-static-repository",
            rehydration=RehydrationConfig(enabled=False),
        ),
    )


async def _run(gateway_root: Path, preferred_adapter_port: int) -> ProviderDriverFacts:
    gateway_sha = _pinned_gateway_sha(gateway_root)
    adapter_type, provider_request_type, build_provider_headers = _load_gateway_types(gateway_root)
    adapter_port = _free_loopback_port(preferred_adapter_port)
    fake_port = _free_loopback_port()
    state: dict[str, Any] = {}

    import os

    os.environ["SLAIF_DRIVER_SERVICE_TOKEN"] = SERVICE_TOKEN
    os.environ["SLAIF_DRIVER_QWEN_TOKEN"] = QWEN_TOKEN

    fake_server: uvicorn.Server | None = None
    fake_task: asyncio.Task[None] | None = None
    candidate_server: uvicorn.Server | None = None
    candidate_task: asyncio.Task[None] | None = None
    async with httpx.AsyncClient(timeout=10, follow_redirects=False) as gateway_http:
        with tempfile.TemporaryDirectory(prefix="slaif-005b-driver-") as temp_dir:
            fake_server, fake_task = await _start_server(_fake_vllm_app(state), fake_port)
            settings = _candidate_settings(
                adapter_port=adapter_port,
                fake_port=fake_port,
                cache_root=Path(temp_dir) / "cache",
            )
            candidate_server, candidate_task = await _start_server(
                create_app(settings), adapter_port
            )
            try:
                health = await gateway_http.get(
                    f"http://127.0.0.1:{adapter_port}/health",
                    headers={"Authorization": f"Bearer {SERVICE_TOKEN}"},
                )
                if health.status_code != 200:
                    raise RuntimeError(
                        f"candidate service health check failed status={health.status_code}"
                    )

                adapter = adapter_type(
                    SimpleNamespace(OPENAI_UPSTREAM_API_KEY=CLIENT_TOKEN),
                    provider_name="openai_compatible",
                    base_url=f"http://127.0.0.1:{adapter_port}/v1",
                    api_key=SERVICE_TOKEN,
                    timeout_seconds=10,
                    http_client=gateway_http,
                )
                request = provider_request_type(
                    provider="openai_compatible",
                    upstream_model=UPSTREAM_MODEL,
                    endpoint="/v1/responses",
                    body=safe_provider_request_body(),
                    request_id="driver-request-id",
                    extra_headers={
                        "Content-Type": "application/json",
                        "X-SLAIF-Principal": "untrusted-driver-header",
                    },
                )
                if CLIENT_TOKEN in repr(request) or "authorization" in provider_request_field_names(
                    request
                ):
                    raise RuntimeError("ProviderRequest retained forbidden client credentials")

                nonstream = await adapter.forward_response(request)
                stream_request = provider_request_type(
                    provider=request.provider,
                    upstream_model=request.upstream_model,
                    endpoint=request.endpoint,
                    body={**request.body, "stream": True},
                    request_id=request.request_id,
                    extra_headers=request.extra_headers,
                )
                stream_chunks = [chunk async for chunk in adapter.stream_response(stream_request)]
                stream_types = tuple(
                    payload["type"]
                    for chunk in stream_chunks
                    if isinstance((payload := chunk.json_body), dict)
                    and isinstance(payload.get("type"), str)
                )

                filtered_headers = build_provider_headers(
                    SERVICE_TOKEN,
                    provider="openai_compatible",
                    extra_headers={
                        "Authorization": f"Bearer {CLIENT_TOKEN}",
                        "Cookie": "client-cookie",
                        "X-SLAIF-Principal": "untrusted-driver-header",
                    },
                )
                metrics = (await gateway_http.get(f"http://127.0.0.1:{adapter_port}/metrics")).text
                client_key_filtered = (
                    filtered_headers.get("Authorization") == f"Bearer {SERVICE_TOKEN}"
                    and "Cookie" not in filtered_headers
                    and CLIENT_TOKEN not in str(filtered_headers)
                )
                identity_headers_filtered = not any(
                    name.lower().startswith("x-slaif-") for name in filtered_headers
                )
                facts = ProviderDriverFacts(
                    gateway_sha=gateway_sha,
                    adapter_class=adapter_type.__name__,
                    provider_request_class=provider_request_type.__name__,
                    nonstream_status=nonstream.status_code,
                    nonstream_upstream_model=str(state.get("upstream_model", "")),
                    nonstream_usage_total=(
                        None if nonstream.usage is None else nonstream.usage.total_tokens
                    ),
                    stream_status=200 if stream_chunks else 500,
                    stream_event_types=stream_types,
                    stream_event_count=len(stream_chunks),
                    candidate_auth_ok=health.status_code == 200,
                    upstream_auth_ok=state.get("upstream_auth_ok") is True,
                    upstream_service_token_not_forwarded=(
                        state.get("upstream_received_service_token") is False
                    ),
                    rewritten_model_ok=state.get("upstream_model") == "qwen3.8-27b",
                    client_key_filtered=client_key_filtered,
                    identity_headers_filtered=identity_headers_filtered,
                    metrics_secret_free=not any(
                        secret in metrics for secret in (SERVICE_TOKEN, QWEN_TOKEN, CLIENT_TOKEN)
                    ),
                    provider_only_no_accounting=True,
                )
                assert_provider_driver_facts(facts)
                return facts
            finally:
                if candidate_server is not None and candidate_task is not None:
                    await _stop_server(candidate_server, candidate_task)
                if fake_server is not None and fake_task is not None:
                    await _stop_server(fake_server, fake_task)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gateway-root", type=Path, required=True)
    parser.add_argument("--adapter-port", type=int, default=18031)
    args = parser.parse_args()
    try:
        facts = asyncio.run(_run(args.gateway_root, args.adapter_port))
    except Exception as exc:  # pragma: no cover - exercised by the bounded driver run
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__}))
        return 1
    print(json.dumps({"status": "PASSED", **asdict(facts)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
