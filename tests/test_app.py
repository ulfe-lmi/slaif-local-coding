import asyncio
import gzip
import json
import logging
import os
import re
from collections.abc import AsyncIterator, Callable, Coroutine, MutableMapping
from pathlib import Path
from typing import Any, cast

import httpx
import pytest
from starlette.requests import Request

import slaif_local_coding.app as app_module
from slaif_local_coding.app import V1RuntimeUnavailableError, create_app
from slaif_local_coding.config import (
    CacheConfig,
    CompilerConfig,
    ConstitutionIntegrationConfig,
    ContextCacheConfig,
    ContextCacheRecoveryConfig,
    ContextCacheRouteContract,
    GatewayIngressConfig,
    RouteConfig,
    ServerConfig,
    Settings,
    UpstreamConfig,
)
from slaif_local_coding.constitution.bundles.bundle_budget import BundleBudgetConfig
from slaif_local_coding.constitution.bundles.bundle_compile_work import BundleCompileWork
from slaif_local_coding.constitution.bundles.bundle_compiler import (
    BundleCompiledRule,
    BundleCompilerConfig,
    serialize_compiled_index,
)
from slaif_local_coding.constitution.bundles.bundle_tokenizer import BundleTokenizer
from slaif_local_coding.constitution.bundles.causal_history_models import CAUSAL_ROOT_FACT
from slaif_local_coding.constitution.bundles.ram_state import RamStateOwnerRegistry
from slaif_local_coding.constitution.bundles.ram_state_models import RamStateBounds
from slaif_local_coding.constitution.bundles.recovery_store import (
    RecoveryStore,
    session_directory_name,
)
from slaif_local_coding.constitution.bundles.root_region_admission_result_models import (
    RootRegionAdmissionOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_currentness_models import (
    RootRegionCurrentnessOutcome,
    RootRegionUncertaintyClass,
)
from slaif_local_coding.constitution.bundles.v1_application import (
    V1Session,
    build_session_address,
)
from slaif_local_coding.constitution.bundles.v1_runtime import V1Runtime, V1RuntimeReason
from slaif_local_coding.constitution.cache import RequestIdentity
from tests.helpers.transport_observer import DirectTransportObserver
from tests.test_causal_history import WORKSPACE, exec_call, frame, out_item, root_item
from tests.test_v1_application import (
    _completion_bytes,
    _echo_compiler_handler,
    _index_for_demand,
)


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("TEST_UPSTREAM_KEY", "test-only-secret")
    return Settings(
        server=ServerConfig(request_body_max_bytes=4096),
        upstream=UpstreamConfig(
            base_url="http://upstream.test", api_key_env="TEST_UPSTREAM_KEY", model="qwen"
        ),
        routes=[
            RouteConfig(
                name="vision",
                model="qwen",
                max_images_per_request=1,
                image_overflow_policy="retain_newest",
            )
        ],
    )


async def call(
    settings: Settings,
    handler: Callable[[httpx.Request], Coroutine[None, None, httpx.Response]],
    method: str,
    path: str,
    **kwargs: Any,
) -> httpx.Response:
    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        return await client.request(method, path, **kwargs)


def post_scope(headers: list[tuple[bytes, bytes]] | None = None) -> dict[str, Any]:
    return {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/v1/responses",
        "raw_path": b"/v1/responses",
        "query_string": b"",
        "headers": headers or [(b"content-type", b"application/json")],
        "client": ("127.0.0.1", 1),
        "server": ("127.0.0.1", 18031),
    }


def authenticated_settings(
    settings: Settings, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> Settings:
    monkeypatch.setenv("TEST_ADAPTER_SERVICE_TOKEN", "adapter-only-synthetic-token")
    monkeypatch.setenv("TEST_COMPILER_KEY", "compiler-only-synthetic-token")
    route = settings.routes[0].model_copy(
        update={"observation_enabled": True, "constitution_enabled": True}
    )
    return Settings(
        server=settings.server,
        gateway_ingress=GatewayIngressConfig(
            mode="service_bearer_static_identity", service_token_env="TEST_ADAPTER_SERVICE_TOKEN"
        ),
        upstream=settings.upstream.model_copy(update={"base_url": "http://upstream.test/v1"}),
        routes=[route],
        observation=settings.observation,
        compiler=CompilerConfig(enabled=True, api_key_env="TEST_COMPILER_KEY"),
        cache=CacheConfig(root=tmp_path / "cache", fallback_root=tmp_path / "fallback-cache"),
        constitution=ConstitutionIntegrationConfig(
            enabled=True,
            principal="local-appliance-principal",
            session="local-appliance-session",
            repository="local-appliance-repository",
        ),
        observability=settings.observability,
    )


@pytest.mark.asyncio
async def test_health_models_auth_and_header_filter(settings: Settings) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer test-only-secret"
        assert request.headers["accept-encoding"] == "identity"
        assert "upgrade" not in request.headers
        assert "x-remove-me" not in request.headers
        assert "x-slaif-principal" not in request.headers
        assert "cookie" not in request.headers
        assert "x-internal-secret" not in request.headers
        assert request.url.query == b"cursor=opaque%2Bvalue"
        return httpx.Response(
            200,
            headers={
                "content-type": "application/json",
                "connection": "retry-after",
                "retry-after": "99",
                "x-secret": "no",
            },
            json={"data": [{"id": "qwen"}]},
        )

    response = await call(
        settings,
        handler,
        "GET",
        "/v1/models?cursor=opaque%2Bvalue",
        headers={
            "authorization": "Bearer attacker",
            "connection": "x-remove-me, upgrade",
            "x-remove-me": "private",
            "upgrade": "attacker-protocol",
            "x-slaif-principal": "spoof",
            "cookie": "private-cookie",
            "x-internal-secret": "private-internal-header",
        },
    )
    assert response.status_code == 200 and response.json()["data"][0]["id"] == "qwen"
    assert "x-secret" not in response.headers
    assert "retry-after" not in response.headers


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("headers", "expected_status"),
    [
        (None, 401),
        ({"authorization": "Basic adapter-only-synthetic-token"}, 401),
        ({"authorization": "Bearer"}, 401),
        ({"authorization": "Bearer "}, 401),
        ({"authorization": "Bearer  adapter-only-synthetic-token"}, 401),
        ({"authorization": "Bearer adapter-only-synthetic-token extra"}, 401),
        ({"authorization": "Bearer\tadapter-only-synthetic-token"}, 401),
        ({"authorization": "Bearer adapter-only-synthetic-token\t"}, 401),
        ({"authorization": "Bearer adapter-only-synthetic-token "}, 401),
        ({"authorization": "Bearer wrong-synthetic-token"}, 403),
        ({"authorization": "Bearer " + "x" * 4097}, 401),
    ],
)
async def test_service_ingress_rejects_invalid_authorization_before_work(
    settings: Settings,
    tmp_path: Any,
    monkeypatch: pytest.MonkeyPatch,
    headers: dict[str, str] | None,
    expected_status: int,
) -> None:
    authenticated = authenticated_settings(settings, tmp_path, monkeypatch)
    calls = 0

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={})

    app = create_app(authenticated, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.post(
            "/v1/responses",
            content=b"not-json-and-should-not-be-parsed",
            headers=headers,
        )
    assert response.status_code == expected_status
    assert response.headers.get("www-authenticate") == (
        "Bearer" if expected_status == 401 else None
    )
    assert response.json()["error"]["code"] in {
        "invalid_service_authorization",
        "service_authorization_denied",
    }
    assert calls == 0
    assert "adapter-only-synthetic-token" not in response.text


@pytest.mark.asyncio
async def test_service_ingress_rejects_duplicate_authorization_without_cache_write(
    settings: Settings, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticated = authenticated_settings(settings, tmp_path, monkeypatch)
    calls = 0

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={})

    app = create_app(authenticated, httpx.MockTransport(handler))
    cache_entries_before = sorted(tmp_path.joinpath("cache").rglob("*"))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={"model": "qwen", "input": "synthetic"},
            headers=[
                ("authorization", "Bearer adapter-only-synthetic-token"),
                ("authorization", "Bearer second-synthetic-token"),
            ],
        )
    assert response.status_code == 401
    assert calls == 0
    assert sorted(tmp_path.joinpath("cache").rglob("*")) == cache_entries_before


def test_request_service_token_uses_same_validator_as_environment(
    settings: Settings, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticated = authenticated_settings(settings, tmp_path, monkeypatch)
    valid = "x" * 4096
    invalid = "x\u00a0x"
    monkeypatch.setenv("TEST_ADAPTER_SERVICE_TOKEN", valid)
    for token, expected in ((valid, None), (invalid, 401), ("x x", 401)):
        request = Request(post_scope(headers=[(b"authorization", f"Bearer {token}".encode())]))
        result = app_module._authenticate_service_request(request, authenticated)
        if expected is None:
            assert result is None
        else:
            assert result is not None and result.status_code == expected


@pytest.mark.asyncio
async def test_service_ingress_forwards_only_qwen_auth_and_keeps_static_identity(
    settings: Settings,
    tmp_path: Any,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    authenticated = authenticated_settings(settings, tmp_path, monkeypatch)
    received: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        received.append(request)
        assert request.headers["authorization"] == "Bearer test-only-secret"
        assert "adapter-only-synthetic-token" not in str(request.headers)
        assert "x-slaif-principal" not in request.headers
        assert "x-slaif-session" not in request.headers
        assert "x-internal-owner" not in request.headers
        assert "cookie" not in request.headers
        assert json.loads(request.content)["model"] == "qwen"
        return httpx.Response(200, json={"usage": {"input_tokens": 2, "output_tokens": 1}})

    app = create_app(authenticated, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        with caplog.at_level(logging.INFO):
            response_one = await client.post(
                "/v1/responses",
                json={"model": "qwen", "input": "synthetic-one"},
                headers={
                    "authorization": "Bearer adapter-only-synthetic-token",
                    "x-slaif-principal": "spoofed-principal-one",
                    "x-slaif-session": "spoofed-session-one",
                    "x-internal-owner": "spoofed-owner-one",
                    "cookie": "spoofed-cookie-one",
                },
            )
            response_two = await client.post(
                "/v1/responses",
                json={"model": "qwen", "input": "synthetic-two"},
                headers={
                    "authorization": "Bearer adapter-only-synthetic-token",
                    "x-slaif-principal": "spoofed-principal-two",
                    "x-slaif-session": "spoofed-session-two",
                    "x-forwarded-for": "spoofed-address-two",
                },
            )
            metrics = (await client.get("/metrics")).text
    assert response_one.status_code == response_two.status_code == 200
    assert len(received) == 2
    assert "adapter-only-synthetic-token" not in caplog.text
    assert "adapter-only-synthetic-token" not in metrics
    assert "spoofed-principal" not in metrics
    pipeline = app.state.constitution_pipeline
    assert pipeline is not None
    identity = pipeline._identity("vision")
    assert identity.principal == "local-appliance-principal"
    assert identity.session == "local-appliance-session"
    assert identity.repository == "local-appliance-repository"


@pytest.mark.asyncio
async def test_gateway_vector_auth_preserves_image_tools_usage_and_sse(
    settings: Settings, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    vector = json.loads(Path("tests/fixtures/gateway/openai_compatible_vectors.json").read_text())
    authenticated = authenticated_settings(settings, tmp_path, monkeypatch)
    authenticated.routes[0].model = vector["request"]["model_after_gateway_rewrite"]
    authenticated.upstream.model = vector["request"]["model_after_gateway_rewrite"]
    events = [b"data: gateway-one\n\n", b"data: [DONE]\n\n"]

    class Stream(httpx.AsyncByteStream):
        async def __aiter__(self) -> AsyncIterator[bytes]:
            for event in events:
                yield event

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer test-only-secret"
        payload = json.loads(await request.aread())
        assert payload["model"] == "qwen3.8-27b"
        assert payload["tools"][0]["type"] == "function"
        content = payload["input"]
        assert content[0]["type"] == "function_call_output"
        assert [item["image_url"] for item in content if item["type"] == "input_image"] == [
            "new-image"
        ]
        if payload.get("stream"):
            return httpx.Response(
                200, headers={"content-type": "text/event-stream"}, stream=Stream()
            )
        return httpx.Response(
            200,
            json={"usage": {"input_tokens": 4, "output_tokens": 3}, "output": []},
        )

    app = create_app(authenticated, httpx.MockTransport(handler))
    payload: dict[str, Any] = {
        "model": "qwen3.8-27b",
        "input": [
            {"type": "input_image", "image_url": "old-image"},
            {"type": "function_call_output", "call_id": "call-1", "output": "ok"},
            {"type": "input_image", "image_url": "new-image"},
        ],
        "tools": [{"type": "function", "function": {"name": "lookup"}}],
    }
    headers = {"authorization": "Bearer adapter-only-synthetic-token"}
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        nonstream = await client.post("/v1/responses", json=payload, headers=headers)
        payload["stream"] = True
        streamed = await client.post("/v1/responses", json=payload, headers=headers)
    assert nonstream.status_code == streamed.status_code == 200
    assert nonstream.json()["usage"] == {"input_tokens": 4, "output_tokens": 3}
    assert streamed.content == b"".join(events)


@pytest.mark.asyncio
async def test_service_ingress_readiness_is_fixed_and_secret_free(
    settings: Settings, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticated = authenticated_settings(settings, tmp_path, monkeypatch)

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/health"
        return httpx.Response(200, json={})

    app = create_app(authenticated, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        ready = await client.get("/readyz")
        assert ready.status_code == 200
        assert ready.json()["gateway_ingress"] == "ready"
        monkeypatch.delenv("TEST_ADAPTER_SERVICE_TOKEN")
        unavailable = await client.get("/readyz")
    assert unavailable.status_code == 503
    assert unavailable.json()["gateway_ingress"] == "unavailable"
    assert "adapter-only-synthetic-token" not in unavailable.text


@pytest.mark.asyncio
async def test_nonstream_upstream_error_is_sanitized_and_retryable(settings: Settings) -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            headers={"content-type": "application/json", "retry-after": "3"},
            json={"error": {"message": "upstream-private-body", "path": "/private/path"}},
        )

    response = await call(
        settings,
        handler,
        "POST",
        "/v1/chat/completions",
        json={"model": "qwen", "messages": [], "tools": [{"type": "function"}]},
    )
    assert response.status_code == 429
    assert response.json() == {
        "error": {
            "message": "upstream returned an error",
            "type": "upstream_error",
            "code": "upstream_error",
        }
    }
    assert response.headers["retry-after"] == "3"
    assert "upstream-private-body" not in response.text
    assert "/private/path" not in response.text


@pytest.mark.asyncio
async def test_app_error_close_exposes_only_bounded_original_provider_facts(
    settings: Settings,
) -> None:
    body = (
        b'{"error":{"message":"private-provider-sentinel","type":"BadRequestError",'
        b'"code":400,"param":null}}'
    )

    class ErrorStream(httpx.AsyncByteStream):
        close_calls = 0

        async def __aiter__(self) -> AsyncIterator[bytes]:
            yield body

        async def aclose(self) -> None:
            self.close_calls += 1

    stream = ErrorStream()

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, headers={"content-type": "application/json"}, stream=stream)

    observer = DirectTransportObserver(httpx.MockTransport(handler))
    app = create_app(settings, observer)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.post("/v1/chat/completions", json={"model": "qwen", "messages": []})

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "message": "upstream returned an error",
            "type": "upstream_error",
            "code": "upstream_error",
        }
    }
    records = cast(tuple[dict[str, object], ...], observer.snapshot()["records"])
    record = records[0]
    provider_error = cast(dict[str, object], record["provider_error"])
    assert provider_error["http_status"] == 400
    assert provider_error["body_class"] == "error_object"
    assert provider_error["type_class"] == "BadRequestError"
    assert provider_error["code_status_relation"] == "matching"
    assert "private-provider-sentinel" not in json.dumps(observer.snapshot())
    assert stream.close_calls == 1


@pytest.mark.asyncio
async def test_nonstream_response_body_bound_is_sanitized(settings: Settings) -> None:
    settings.server.response_body_max_bytes = 32

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"x" * 33)

    response = await call(
        settings,
        handler,
        "GET",
        "/health",
    )
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "upstream_response_too_large"


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True])
async def test_compressed_response_preserves_encoding_and_raw_bytes(
    settings: Settings, stream: bool
) -> None:
    raw = b'{"usage":{"total_tokens":3},"output":"ok"}'
    encoded = gzip.compress(raw)

    class EncodedStream(httpx.AsyncByteStream):
        async def __aiter__(self) -> AsyncIterator[bytes]:
            yield encoded[:7]
            yield encoded[7:]

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/json", "content-encoding": "gzip"},
            stream=EncodedStream(),
        )

    response = await call(
        settings,
        handler,
        "POST",
        "/v1/responses",
        json={"model": "qwen", "input": "x", "stream": stream},
    )
    assert response.status_code == 200
    assert response.headers["content-encoding"] == "gzip"
    assert response.content == raw


@pytest.mark.asyncio
async def test_transform_newest_and_continuation_unchanged(settings: Settings) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        value = json.loads(await request.aread())
        content = value["input"]
        assert [item.get("image_url") for item in content if item.get("type") == "input_image"] == [
            "new"
        ]
        assert content[0] == {"type": "function_call_output", "call_id": "c", "output": "ok"}
        return httpx.Response(200, json={"usage": {"input_tokens": 1}})

    payload = {
        "model": "qwen",
        "input": [
            {"type": "input_image", "image_url": "old"},
            {"type": "function_call_output", "call_id": "c", "output": "ok"},
            {"type": "input_image", "image_url": "new"},
        ],
    }
    assert (await call(settings, handler, "POST", "/v1/responses", json=payload)).status_code == 200


@pytest.mark.asyncio
async def test_zero_one_forward_exact_body(settings: Settings) -> None:
    raw = b'{"model":"qwen", "input":[{"type":"input_image","image_url":"one"}]}'

    async def handler(request: httpx.Request) -> httpx.Response:
        assert await request.aread() == raw
        return httpx.Response(200, json={})

    assert (
        await call(
            settings,
            handler,
            "POST",
            "/v1/responses",
            content=raw,
            headers={"content-type": "application/json"},
        )
    ).status_code == 200


@pytest.mark.asyncio
async def test_route_scoped_observation_preserves_bytes_and_emits_safe_counts(
    settings: Settings,
) -> None:
    raw = (
        b'{"model":"qwen","input":[{"type":"input_file","filename":"AGENTS.md",'
        b'"content":"MUST read private/synthetic-policy.md"}]}'
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        assert await request.aread() == raw
        return httpx.Response(200, json={})

    settings.routes[0].observation_enabled = True
    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.post(
            "/v1/responses",
            content=raw,
            headers={
                "content-type": "application/json",
                "x-slaif-principal": "spoofed-private-principal",
                "x-slaif-session": "spoofed-private-session",
            },
        )
        metrics = (await client.get("/metrics")).text
    assert response.status_code == 200
    assert 'evidence_type="input_file"' in metrics
    assert 'route="vision"' in metrics
    assert "private/synthetic-policy.md" not in metrics
    assert "spoofed-private" not in metrics


@pytest.mark.asyncio
async def test_observation_disabled_has_no_observation_or_extra_upstream_call(
    settings: Settings,
) -> None:
    calls = 0

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={})

    response = await call(
        settings,
        handler,
        "POST",
        "/v1/responses",
        json={"model": "qwen", "input": [{"filename": "AGENTS.md", "content": "rules"}]},
    )
    assert response.status_code == 200 and calls == 1


@pytest.mark.asyncio
async def test_observation_last_resort_fallback_preserves_one_unchanged_request(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw = b'{"model":"qwen","input":"synthetic"}'
    calls = 0

    def injected_failure(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("synthetic observation failure")

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        assert await request.aread() == raw
        return httpx.Response(200, json={})

    def injected_sources_failure(*_args: Any, **_kwargs: Any) -> tuple[None, None]:
        injected_failure()
        raise AssertionError("unreachable")

    monkeypatch.setattr(app_module, "observe_request_for_pipeline", injected_sources_failure)
    settings.routes[0].observation_enabled = True
    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.post(
            "/v1/responses", content=raw, headers={"content-type": "application/json"}
        )
        metrics = (await client.get("/metrics")).text
    assert response.status_code == 200 and calls == 1
    assert 'reason="parsing_error"' in metrics


@pytest.mark.asyncio
async def test_reject_passthrough_unknown_and_bounds(settings: Settings) -> None:
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, content=await request.aread())

    two = {"model": "qwen", "input": [{"type": "input_image"}, {"type": "input_image"}]}
    settings.routes[0].image_overflow_policy = "reject"
    assert (await call(settings, handler, "POST", "/v1/responses", json=two)).status_code == 422
    assert calls == 0
    settings.routes[0].image_overflow_policy = "passthrough"
    assert (await call(settings, handler, "POST", "/v1/responses", json=two)).json() == two
    assert (
        await call(settings, handler, "POST", "/v1/responses", json={"model": "other"})
    ).status_code == 422
    assert (
        await call(settings, handler, "POST", "/v1/responses", content=b"x" * 4097)
    ).status_code == 413


def nested_input(depth: int, *, image: bool = False) -> dict[str, Any]:
    value: Any = {"type": "input_image", "image_url": "private-depth-sentinel"} if image else "x"
    leaf_depth = 1 if image else 0
    for index in range(depth - 1 - leaf_depth):
        value = [value] if index % 2 else {"item": value}
    return {"model": "qwen", "input": value}


@pytest.mark.asyncio
async def test_json_depth_exact_limit_and_plus_one_have_deterministic_boundary(
    settings: Settings, caplog: pytest.LogCaptureFixture
) -> None:
    settings.server.json_max_nesting_depth = 8
    calls = 0

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={})

    assert (
        await call(settings, handler, "POST", "/v1/responses", json=nested_input(8))
    ).status_code == 200
    with caplog.at_level(logging.INFO):
        rejected = await call(
            settings, handler, "POST", "/v1/responses", json=nested_input(9, image=True)
        )
    assert rejected.status_code == 400
    assert rejected.json() == {
        "error": {
            "message": "request JSON exceeds configured nesting limit",
            "type": "invalid_request_error",
            "code": "json_nesting_too_deep",
        }
    }
    assert calls == 1
    assert "private-depth-sentinel" not in rejected.text
    assert "private-depth-sentinel" not in caplog.text
    assert "RecursionError" not in rejected.text + caplog.text


@pytest.mark.asyncio
async def test_depth_reject_has_bounded_metric_and_no_private_content(settings: Settings) -> None:
    settings.server.json_max_nesting_depth = 4
    calls = 0

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200)

    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        rejected = await client.post("/v1/responses", json=nested_input(5, image=True))
        metrics = (await client.get("/metrics")).text
    assert rejected.status_code == 400
    assert calls == 0
    assert 'endpoint="/v1/responses",route="passthrough",status="400",stream="false"' in metrics
    assert "private-depth-sentinel" not in metrics


@pytest.mark.asyncio
async def test_depth_600_reproducer_and_deep_non_image_never_reach_upstream(
    settings: Settings,
) -> None:
    calls = 0

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200)

    for image in (False, True):
        response = await call(
            settings, handler, "POST", "/v1/responses", json=nested_input(600, image=image)
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "json_nesting_too_deep"
    assert calls == 0


@pytest.mark.asyncio
async def test_representative_nested_responses_and_chat_remain_compatible(
    settings: Settings,
) -> None:
    bodies: list[dict[str, Any]] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        bodies.append(json.loads(await request.aread()))
        return httpx.Response(200, json={})

    responses = {
        "model": "qwen",
        "input": [{"content": [{"type": "input_image", "image_url": "one"}]}],
        "tools": [{"type": "function", "function": {"name": "f", "parameters": {}}}],
    }
    chat = {
        "model": "qwen",
        "messages": [
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": "one"}}]}
        ],
        "tools": [{"type": "function", "function": {"name": "f", "parameters": {}}}],
    }
    assert (
        await call(settings, handler, "POST", "/v1/responses", json=responses)
    ).status_code == 200
    assert (
        await call(settings, handler, "POST", "/v1/chat/completions", json=chat)
    ).status_code == 200
    assert bodies == [responses, chat]


@pytest.mark.asyncio
async def test_incremental_body_bound_stops_consuming_remaining_chunks(settings: Settings) -> None:
    settings.server.request_body_max_bytes = 64
    upstream_calls = 0

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal upstream_calls
        upstream_calls += 1
        return httpx.Response(200)

    app = create_app(settings, httpx.MockTransport(handler))
    chunks = [b"x" * 40, b"y" * 25, b"private-unconsumed-tail"]
    consumed = 0
    sent: list[MutableMapping[str, Any]] = []

    async def receive() -> dict[str, Any]:
        nonlocal consumed
        chunk = chunks[consumed]
        consumed += 1
        return {"type": "http.request", "body": chunk, "more_body": consumed < len(chunks)}

    async def send(message: MutableMapping[str, Any]) -> None:
        sent.append(message)

    await app(post_scope(), receive, send)
    assert sent[0]["status"] == 413
    assert consumed == 2
    assert upstream_calls == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("maximum", "body", "content_length", "expected"),
    [
        (43, b'{"model":"qwen","input":"1234567890123456"}', None, 200),
        (42, b'{"model":"qwen","input":"1234567890123456"}', None, 413),
        (42, b'{"model":"qwen","input":"1234567890123456"}', b"1", 413),
        (42, b'{"model":"qwen","input":"1234567890123456"}', b"999", 413),
        (64, b'{"model":', None, 400),
    ],
)
async def test_body_limit_exact_actual_and_content_length_cases(
    settings: Settings,
    maximum: int,
    body: bytes,
    content_length: bytes | None,
    expected: int,
) -> None:
    settings.server.request_body_max_bytes = maximum

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    headers = [(b"content-type", b"application/json")]
    if content_length is not None:
        headers.append((b"content-length", content_length))
    messages = [
        {"type": "http.request", "body": body[:20], "more_body": True},
        {"type": "http.request", "body": body[20:], "more_body": False},
    ]
    sent: list[MutableMapping[str, Any]] = []

    async def receive() -> dict[str, Any]:
        return messages.pop(0)

    async def send(message: MutableMapping[str, Any]) -> None:
        sent.append(message)

    await create_app(settings, httpx.MockTransport(handler))(post_scope(headers), receive, send)
    assert sent[0]["status"] == expected


@pytest.mark.asyncio
async def test_sse_event_order_and_incremental_chunks(settings: Settings) -> None:
    events = [b"data: one\n\n", b"data: two\n\n", b"data: [DONE]\n\n"]

    class Stream(httpx.AsyncByteStream):
        async def __aiter__(self) -> AsyncIterator[bytes]:
            for event in events:
                yield event

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=Stream())

    response = await call(
        settings,
        handler,
        "POST",
        "/v1/responses",
        json={"model": "qwen", "input": "x", "stream": True},
    )
    assert response.content == b"".join(events)


@pytest.mark.asyncio
async def test_first_sse_chunk_arrives_before_upstream_completion(settings: Settings) -> None:
    first_yielded = asyncio.Event()
    first_sent = asyncio.Event()
    release_second = asyncio.Event()
    upstream_closed = asyncio.Event()

    class Stream(httpx.AsyncByteStream):
        async def __aiter__(self) -> AsyncIterator[bytes]:
            yield b"data: one\n\n"
            first_yielded.set()
            await release_second.wait()
            yield b"data: two\n\ndata: [DONE]\n\n"

        async def aclose(self) -> None:
            upstream_closed.set()

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=Stream())

    body = json.dumps({"model": "qwen", "input": "x", "stream": True}).encode()
    request_sent = False
    downstream: list[bytes] = []

    async def receive() -> dict[str, Any]:
        nonlocal request_sent
        if not request_sent:
            request_sent = True
            return {"type": "http.request", "body": body, "more_body": False}
        await asyncio.Event().wait()
        raise AssertionError("unreachable")

    async def send(message: MutableMapping[str, Any]) -> None:
        if message["type"] == "http.response.body" and message.get("body"):
            downstream.append(message["body"])
            first_sent.set()

    task = asyncio.create_task(
        create_app(settings, httpx.MockTransport(handler))(post_scope(), receive, send)
    )
    await asyncio.wait_for(first_yielded.wait(), 1)
    await asyncio.wait_for(first_sent.wait(), 1)
    assert downstream == [b"data: one\n\n"]
    assert not task.done()
    release_second.set()
    await asyncio.wait_for(task, 1)
    assert b"".join(downstream) == b"data: one\n\ndata: two\n\ndata: [DONE]\n\n"
    assert upstream_closed.is_set()


@pytest.mark.asyncio
async def test_client_disconnect_closes_upstream(settings: Settings) -> None:
    first_sent = asyncio.Event()
    release_never = asyncio.Event()

    class Stream(httpx.AsyncByteStream):
        closed = False

        async def __aiter__(self) -> AsyncIterator[bytes]:
            yield b"data: one\n\n"
            await release_never.wait()

        async def aclose(self) -> None:
            self.closed = True

    stream = Stream()

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=stream)

    app = create_app(settings, httpx.MockTransport(handler))
    body = json.dumps({"model": "qwen", "input": "x", "stream": True}).encode()
    received = False

    async def receive() -> dict[str, Any]:
        nonlocal received
        if not received:
            received = True
            return {"type": "http.request", "body": body, "more_body": False}
        await first_sent.wait()
        return {"type": "http.disconnect"}

    async def send(message: MutableMapping[str, Any]) -> None:
        if message["type"] == "http.response.body" and message.get("body"):
            first_sent.set()

    scope: dict[str, Any] = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/v1/responses",
        "raw_path": b"/v1/responses",
        "query_string": b"",
        "headers": [(b"content-type", b"application/json")],
        "client": ("127.0.0.1", 1),
        "server": ("127.0.0.1", 18031),
    }
    await app(scope, receive, send)
    assert first_sent.is_set()
    assert stream.closed


@pytest.mark.asyncio
async def test_timeout_sanitized_and_no_raw_logging(
    settings: Settings, caplog: pytest.LogCaptureFixture
) -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("raw-private-payload")

    with caplog.at_level(logging.INFO):
        response = await call(
            settings,
            handler,
            "POST",
            "/v1/responses",
            json={"model": "qwen", "input": "raw-private-payload"},
        )
    assert response.status_code == 503
    assert "raw-private-payload" not in caplog.text


@pytest.mark.asyncio
async def test_metrics_have_bounded_labels(settings: Settings) -> None:
    ready = True

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health" and not ready:
            return httpx.Response(503)
        return httpx.Response(200, json={})

    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        await client.post("/v1/responses", json={"model": "qwen", "input": "private marker"})
        assert (await client.get("/readyz")).status_code == 200
        ready = False
        assert (await client.get("/readyz")).status_code == 503
        await client.post("/v1/responses", content=b"private malformed marker")
        await client.get("/private-query?secret=private-query-value")
        metrics = (await client.get("/metrics")).text
    for private_value in (
        "private marker",
        "private malformed marker",
        "private-query-value",
        "test-only-secret",
    ):
        assert private_value not in metrics
    assert 'route="vision"' in metrics
    assert 'endpoint="unsupported"' in metrics
    assert 'status="400"' in metrics
    assert "slaif_readiness_state 0.0" in metrics
    assert "slaif_response_header_duration_seconds" in metrics


@pytest.mark.asyncio
async def test_metrics_can_be_disabled_without_exposing_registry(settings: Settings) -> None:
    settings = settings.model_copy(
        update={
            "observability": settings.observability.model_copy(update={"metrics_enabled": False})
        }
    )

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    response = await call(settings, handler, "GET", "/metrics")
    assert response.status_code == 404
    assert "slaif_requests_total" not in response.text


@pytest.mark.asyncio
async def test_normal_governed_request_makes_zero_constitution_pipeline_calls(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Objective-003-a contracts stay library-only: public handlers remain inert."""
    from unittest.mock import AsyncMock, MagicMock

    from slaif_local_coding.constitution.cache import DerivedIndexCache
    from slaif_local_coding.constitution.compiler import ConstitutionalCompiler

    compiler_compile = AsyncMock(side_effect=AssertionError("public request invoked compiler"))
    cache_put = MagicMock(side_effect=AssertionError("public request wrote derived cache"))
    selector_call = MagicMock(side_effect=AssertionError("public request selected working set"))
    responses_inject = MagicMock(side_effect=AssertionError("public Responses request injected"))
    chat_inject = MagicMock(side_effect=AssertionError("public Chat request injected"))
    monkeypatch.setattr(ConstitutionalCompiler, "compile", compiler_compile)
    monkeypatch.setattr(DerivedIndexCache, "put", cache_put)
    monkeypatch.setattr(
        "slaif_local_coding.constitution.working_set.select_working_set", selector_call
    )
    monkeypatch.setattr(
        "slaif_local_coding.constitution.injection.inject_responses", responses_inject
    )
    monkeypatch.setattr(
        "slaif_local_coding.constitution.injection.inject_chat_completions", chat_inject
    )
    observed = settings.model_copy(
        update={
            "routes": [
                settings.routes[0].model_copy(update={"observation_enabled": True}),
            ]
        }
    )
    governed = {
        "model": "qwen",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "# AGENTS.md instructions for repo\n\n<INSTRUCTIONS>\n"
                            "MUST stay unchanged.\n</INSTRUCTIONS>"
                        ),
                    }
                ],
            }
        ],
    }

    async def handler(request: httpx.Request) -> httpx.Response:
        assert json.loads(request.content) == governed
        return httpx.Response(200, json={"id": "unchanged"})

    response = await call(observed, handler, "POST", "/v1/responses", json=governed)
    assert response.status_code == 200
    compiler_compile.assert_not_awaited()
    cache_put.assert_not_called()
    selector_call.assert_not_called()
    responses_inject.assert_not_called()
    chat_inject.assert_not_called()


# ---------------------------------------------------------------------------
# 022-a: the fixed v1 startup refusal at the create_app entry point and the
# preserved legacy entry points (fake transports, synthetic identity and
# environment names, no real secrets, no live upstream).
# ---------------------------------------------------------------------------


def _v1_settings(tmp_path: Path) -> Settings:
    """A fully valid closed v1 settings (the recovery root is NOT
    prepared here: the startup-failure case proves the capability
    refusal, the runnable case prepares the root explicitly)."""
    return Settings(
        server=ServerConfig(request_body_max_bytes=4096),
        upstream=UpstreamConfig(
            base_url="http://127.0.0.1:18020/v1",
            api_key_env="TEST_V1_UPSTREAM_KEY",
            model="qwen38-27b",
        ),
        routes=[
            RouteConfig(
                name="text",
                model="qwen38-27b",
                max_images_per_request=0,
                image_overflow_policy="reject",
                observation_enabled=True,
                constitution_enabled=True,
            )
        ],
        constitution=ConstitutionIntegrationConfig(
            enabled=True,
            identity_source="static",
            principal="local-principal",
            session="local-session",
            repository="local-repository",
        ),
        context_cache=ContextCacheConfig(
            profile="dependency-bundles-v1",
            budget=BundleBudgetConfig(context_tokens=32_768),
            compiler=BundleCompilerConfig(
                model="qwen38-27b",
                base_url="http://127.0.0.1:18020/v1",
                model_revision="a" * 40,
                compatibility_identity="slaif-rtx3090-compat-1",
                api_key_env="TEST_V1_COMPILER_KEY",
            ),
            ram=RamStateBounds(
                session_max_owned_bytes=128 * 1024 * 1024,
                process_max_owned_bytes=512 * 1024 * 1024,
            ),
            recovery=ContextCacheRecoveryConfig(
                enabled=True,
                root=tmp_path / "v1-recovery",
            ),
            marker_key_env="TEST_V1_MARKER_KEY",
            route_contracts={
                "text": ContextCacheRouteContract(model="qwen38-27b", context_tokens=32_768)
            },
        ),
    )


def test_v1_profile_startup_failure_before_any_runtime_construction(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _forbidden_client(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("the v1 startup failure must precede HTTP client construction")

    monkeypatch.setattr(httpx, "AsyncClient", _forbidden_client)
    settings = _v1_settings(tmp_path)
    recovery_root = settings.context_cache.recovery.root
    assert recovery_root is not None
    with pytest.raises(V1RuntimeUnavailableError) as excinfo:
        create_app(settings)
    assert excinfo.value.reason is V1RuntimeReason.RECOVERY_ROOT
    # The failure precedes the client and the recovery owner: the
    # configured store root was never created, opened or probed.
    assert not recovery_root.exists()
    # The failure holds with an injected transport as well: the
    # transport is never wired because no client is constructed.
    with pytest.raises(V1RuntimeUnavailableError) as excinfo:
        create_app(
            settings,
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"ok": True})),
        )
    assert excinfo.value.reason is V1RuntimeReason.RECOVERY_ROOT
    assert not recovery_root.exists()


def test_v1_profile_startup_builds_the_runnable_runtime(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # The distinct application-owned private marker key material: a
    # protected environment REFERENCE resolved once at runtime
    # construction (022-c).  Synthetic test material, 16-256 bytes.
    monkeypatch.setenv("TEST_V1_MARKER_KEY", "0123456789abcdef0123456789abcdef")
    settings = _v1_settings(tmp_path)
    recovery_root = settings.context_cache.recovery.root
    assert recovery_root is not None
    # The operator-prepared protected root (the store never creates it).
    recovery_root.mkdir(mode=0o700)
    recovery_root.chmod(0o700)
    app = create_app(settings)
    runtime = app.state.v1_runtime
    assert isinstance(runtime, V1Runtime)
    # V1 governed routes never instantiate the legacy pipeline.
    assert app.state.constitution_pipeline is None
    # The ACTUAL accepted components are process-owned.
    assert type(runtime.recovery_store) is RecoveryStore
    assert type(runtime.tokenizer) is BundleTokenizer
    assert type(runtime.ram_registry) is RamStateOwnerRegistry
    assert runtime.ram_registry.work is not None
    assert type(runtime.compile_work) is BundleCompileWork
    # The marker key resolved once, repr-suppressed, length-bounded.
    assert runtime.marker_key == b"0123456789abcdef0123456789abcdef"
    assert "marker_key" not in repr(runtime)
    assert set(runtime.governed_routes) == {"text"}
    assert runtime.governed_routes["text"].model == "qwen38-27b"
    assert runtime.budget_plan.config.context_tokens == 32_768
    assert runtime.admission_mode == "lean"


def test_v1_profile_startup_marker_key_failure_precedes_http_client(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _forbidden_client(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("the v1 marker-key failure must precede HTTP client construction")

    monkeypatch.setattr(httpx, "AsyncClient", _forbidden_client)
    # The configured reference names an environment variable that is
    # unset: the fixed typed marker-key capability failure, before any
    # network component and before the recovery owner is constructed.
    monkeypatch.delenv("TEST_V1_MARKER_KEY", raising=False)
    settings = _v1_settings(tmp_path)
    recovery_root = settings.context_cache.recovery.root
    assert recovery_root is not None
    recovery_root.mkdir(mode=0o700)
    recovery_root.chmod(0o700)
    with pytest.raises(V1RuntimeUnavailableError) as excinfo:
        create_app(settings)
    assert excinfo.value.reason is V1RuntimeReason.MARKER_KEY


def test_v1_profile_startup_marker_key_out_of_range_precedes_http_client(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _forbidden_client(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("the v1 marker-key failure must precede HTTP client construction")

    monkeypatch.setattr(httpx, "AsyncClient", _forbidden_client)
    # A 15-byte value is below the closed 16-256 byte bound.
    monkeypatch.setenv("TEST_V1_MARKER_KEY", "0123456789abcde")
    settings = _v1_settings(tmp_path)
    recovery_root = settings.context_cache.recovery.root
    assert recovery_root is not None
    recovery_root.mkdir(mode=0o700)
    recovery_root.chmod(0o700)
    with pytest.raises(V1RuntimeUnavailableError) as excinfo:
        create_app(settings)
    assert excinfo.value.reason is V1RuntimeReason.MARKER_KEY


@pytest.mark.asyncio
async def test_explicit_legacy_profile_stays_usable_through_existing_entry_point(
    settings: Settings,
) -> None:
    legacy = Settings(
        server=settings.server,
        upstream=settings.upstream,
        routes=settings.routes,
        context_cache=ContextCacheConfig(profile="legacy"),
    )
    assert legacy.context_cache.profile == "legacy"

    async def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("healthz must not touch the upstream")

    response = await call(legacy, handler, "GET", "/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# 022-c: the governed v1 request path end-to-end over the ACTUAL
# create_app entry point (one bounded fake upstream serving BOTH the
# main forward and the direct tool-free compiler channel; synthetic
# identity and environment names; no real secrets, no live upstream).
# ---------------------------------------------------------------------------


class TestV1GovernedRequestPath:
    """The ordered app-seam proof: the marker pre-check before raw
    acquisition, the byte-identical transformed-round fixed point of
    the single outgoing body and the marker-side 409 refusal."""

    @staticmethod
    def _governed_payload() -> dict[str, Any]:
        """One decoded Responses request: the legitimate root
        envelope plus a complete (recognized, not yet acquired --
        trusted issuance is the order section 3 wiring) read pair."""
        return {
            "model": "qwen38-27b",
            "input": [
                root_item("Follow the workspace protocol.\n"),
                exec_call("c1", "cat c1.md"),
                out_item("c1", frame("A body.\n")),
            ],
        }

    async def test_governed_round_fixed_point_and_marker_refusal(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("TEST_V1_MARKER_KEY", "0123456789abcdef0123456789abcdef")
        monkeypatch.setenv("TEST_V1_COMPILER_KEY", "test-only-compiler")
        monkeypatch.setenv("TEST_V1_UPSTREAM_KEY", "test-only-upstream")
        settings = _v1_settings(tmp_path)
        recovery_root = settings.context_cache.recovery.root
        assert recovery_root is not None
        # The operator-prepared protected root (the store never creates it).
        recovery_root.mkdir(mode=0o700)
        recovery_root.chmod(0o700)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo(request)
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            return httpx.Response(200, json={"id": "resp-022c"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        # V1 governed routes never instantiate the legacy pipeline.
        assert app.state.constitution_pipeline is None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            # Round one: the first governed request.  The marker
            # pre-check finds no candidate in the ORIGINAL payload;
            # the transition accepts; the transaction compiles the
            # ACTUAL admitted root entry through the work plane (the
            # direct tool-free channel) and commits the root LIVE
            # edit before the single outgoing serialization.
            response1 = await client.post("/v1/responses", json=self._governed_payload())
            assert response1.status_code == 200
            assert response1.json() == {"id": "resp-022c"}
            assert len(captured_main) == 1
            round1_body = captured_main[0].content
            # The outgoing body is canonical JSON: the envelope newlines
            # cross the wire as \n escapes (the environment head bytes).
            head = f"# AGENTS.md instructions for {WORKSPACE}\\n\\n<INSTRUCTIONS>\\n".encode()
            assert head in round1_body
            assert round1_body.count(b"[slaif-live:v") == 1
            assert round1_body.count(b"[slaif-evidence:v") == 0
            # The root source is replaced; the unacquired read carrier
            # stays raw (the admission entries only are edited).
            assert b"Follow the workspace protocol" not in round1_body
            assert b"A body." in round1_body
            assert captured_main[0].url.host == "127.0.0.1"
            assert captured_main[0].url.port == 18020
            assert captured_main[0].url.path == "/v1/responses"
            assert captured_main[0].headers["authorization"] == "Bearer test-only-upstream"
            # The ONE direct tool-free compiler call for the admitted
            # entry (never the public adapter pipeline).
            assert len(captured_compile) == 1
            compile_request = captured_compile[0]
            assert compile_request.url.host == "127.0.0.1"
            assert compile_request.url.port == 18020
            assert compile_request.url.path == "/v1/chat/completions"
            assert compile_request.headers["authorization"] == "Bearer test-only-compiler"
            compile_body = json.loads(compile_request.content)
            assert compile_body["stream"] is False
            assert "tools" not in compile_body
            assert [m["role"] for m in compile_body["messages"]] == ["system", "user"]
            # Round two: the client resends its OWN transformed
            # payload: the pre-check unsplices the shadow, the
            # ordinary hit publishes nothing, and the transaction
            # replays the marker in place -- the single outgoing body
            # is byte-identical (the fixed point).
            response2 = await client.post(
                "/v1/responses",
                content=round1_body,
                headers={"content-type": "application/json"},
            )
            assert response2.status_code == 200
            assert len(captured_main) == 2
            assert captured_main[1].content == round1_body
            # In-epoch compile reuse: the retained payload is a
            # RAM-only HIT (no further upstream call).
            assert len(captured_compile) == 1
            # Round three: a tampered tag in the resent transformed
            # payload is the fixed typed marker-side refusal -- NO
            # raw fallback forward, NO raw acquisition committed.
            tag_start = round1_body.find(b"[slaif-live:v")
            assert tag_start != -1
            flip = tag_start + 20  # well inside the base64url tag body
            flipped = b"A" if round1_body[flip : flip + 1] != b"A" else b"B"
            tampered = round1_body[:flip] + flipped + round1_body[flip + 1 :]
            response3 = await client.post(
                "/v1/responses",
                content=tampered,
                headers={"content-type": "application/json"},
            )
            assert response3.status_code == 409
            error = response3.json()["error"]
            assert error["code"] == "v1_transaction_conflict"
            assert error["message"] == "governed v1 request refused"
            assert len(captured_main) == 2  # never a raw fallback
            # The refusal committed nothing: the untampered round
            # still replays to the fixed point.
            response4 = await client.post(
                "/v1/responses",
                content=round1_body,
                headers={"content-type": "application/json"},
            )
            assert response4.status_code == 200
            assert len(captured_main) == 3
            assert captured_main[2].content == round1_body

    @staticmethod
    def _governed_session(app: Any, settings: Settings) -> V1Session | None:
        """The live session of the static governed identity (the
        trusted static closure of these tests)."""
        runtime = app.state.v1_runtime
        assert runtime is not None
        identity = RequestIdentity(
            principal="local-principal",
            session="local-session",
            repository="local-repository",
            route="text",
        )
        address = build_session_address(
            runtime,
            identity,
            settings.routes[0],
            settings.context_cache.route_contracts["text"],
        )
        return cast("V1Session | None", app.state.v1_sessions.get(address))

    async def test_upstream_tool_call_issuance_marks_the_read_next_round(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The order section 3 app wiring end to end: the round-one
        ACTUAL direct upstream response issues the trusted call
        through the per-request frozen issuance context (committed
        under the state CAS and the protected generation); the
        round-two matching read pair is then ACQUIRED and the single
        outgoing body carries the root LIVE marker and the read LIVE
        marker; the resend is the byte-identical fixed point with no
        further upstream calls."""
        monkeypatch.setenv("TEST_V1_MARKER_KEY", "0123456789abcdef0123456789abcdef")
        monkeypatch.setenv("TEST_V1_COMPILER_KEY", "test-only-compiler")
        monkeypatch.setenv("TEST_V1_UPSTREAM_KEY", "test-only-upstream")
        settings = _v1_settings(tmp_path)
        recovery_root = settings.context_cache.recovery.root
        assert recovery_root is not None
        recovery_root.mkdir(mode=0o700)
        recovery_root.chmod(0o700)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)
        root_body = "Follow `c1.md` before acting.\n"

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo(request)
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            if len(captured_main) == 1:
                # The round-one direct response issues c1.
                return httpx.Response(
                    200,
                    json={
                        "id": "resp-r1",
                        "status": "completed",
                        "output": (
                            {
                                "type": "function_call",
                                "id": "fc-c1",
                                "call_id": "c1",
                                "name": "exec_command",
                                "arguments": json.dumps({"cmd": "cat c1.md"}),
                            },
                        ),
                    },
                )
            return httpx.Response(200, json={"id": f"resp-r{len(captured_main)}"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            # Round one: the root-only request.  The direct response
            # issues c1; the per-request issuance context registers
            # it under the committed-state CAS.
            response1 = await client.post(
                "/v1/responses",
                json={"model": "qwen38-27b", "input": [root_item(root_body)]},
            )
            assert response1.status_code == 200
            round1_body = captured_main[0].content
            assert round1_body.count(b"[slaif-live:v") == 1
            assert b"Follow `c1.md` before acting." not in round1_body
            assert len(captured_compile) == 1  # the admitted root entry
            # The issuance committed (revision over the bootstrap).
            session = self._governed_session(app, settings)
            assert session is not None
            assert session.owner.revision == 2
            # Round two: the client result for the issued call.  The
            # read pair is now ACQUIRED (the same-run FILE entry):
            # the outgoing body edits BOTH carriers.
            round2_payload = {
                "model": "qwen38-27b",
                "input": [
                    root_item(root_body),
                    exec_call("c1", "cat c1.md"),
                    out_item("c1", frame("A body.\n")),
                ],
            }
            response2 = await client.post("/v1/responses", json=round2_payload)
            assert response2.status_code == 200
            round2_body = captured_main[1].content
            assert round2_body.count(b"[slaif-live:v") == 2
            assert round2_body.count(b"[slaif-evidence:v") == 0
            assert b"A body." not in round2_body
            assert b"Follow `c1.md` before acting." not in round2_body
            assert len(captured_compile) == 2  # + the acquired read entry
            # Round three: the resend of the OWN transformed payload
            # is the byte-identical fixed point, no further upstream
            # calls (the RAM hit).
            response3 = await client.post(
                "/v1/responses",
                content=round2_body,
                headers={"content-type": "application/json"},
            )
            assert response3.status_code == 200
            assert captured_main[2].content == round2_body
            assert len(captured_compile) == 2

    async def test_upstream_error_response_earns_no_issuance(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The 400-or-higher error path never feeds the issuance
        observer: the upstream error body carrying a completed
        function call earns NO issuance (the fixed generic error is
        still passed through), and the subsequent read pair of that
        call stays unacquired and raw."""
        monkeypatch.setenv("TEST_V1_MARKER_KEY", "0123456789abcdef0123456789abcdef")
        monkeypatch.setenv("TEST_V1_COMPILER_KEY", "test-only-compiler")
        monkeypatch.setenv("TEST_V1_UPSTREAM_KEY", "test-only-upstream")
        settings = _v1_settings(tmp_path)
        recovery_root = settings.context_cache.recovery.root
        assert recovery_root is not None
        recovery_root.mkdir(mode=0o700)
        recovery_root.chmod(0o700)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo(request)
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            if len(captured_main) == 1:
                # A 500 whose body carries a completed function call:
                # issuance evidence only ever comes from the ACTUAL
                # direct main response below 400.
                return httpx.Response(
                    500,
                    json={
                        "id": "resp-err",
                        "status": "completed",
                        "output": (
                            {
                                "type": "function_call",
                                "id": "fc-c9",
                                "call_id": "c9",
                                "name": "exec_command",
                                "arguments": json.dumps({"cmd": "cat c9.md"}),
                            },
                        ),
                    },
                )
            return httpx.Response(200, json={"id": "resp-r2"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            response1 = await client.post(
                "/v1/responses",
                json={
                    "model": "qwen38-27b",
                    "input": [root_item("Follow `c9.md` before acting.\n")],
                },
            )
            assert response1.status_code == 500
            error1 = response1.json()["error"]
            assert error1["code"] == "upstream_error"
            assert error1["message"] == "upstream returned an error"
            round1_body = captured_main[0].content
            # The error response earned no issuance.
            session = self._governed_session(app, settings)
            assert session is not None
            snapshot = session.owner.snapshot
            assert snapshot is not None
            assert snapshot.state.d_state.issuances == ()
            # Round two: the c9 read pair is rejoined over the SAME-run
            # evidence (the root references c9.md): the FILE entry and
            # its LIVE marker are earned by the graph, but the
            # occurrence is retained UNANCHORED (no issuance binding
            # was ever registered from the error body).
            r1 = json.loads(round1_body)
            round2_payload = {
                "model": "qwen38-27b",
                "input": [
                    *r1["input"],
                    exec_call("c9", "cat c9.md"),
                    out_item("c9", frame("B body.\n")),
                ],
            }
            response2 = await client.post("/v1/responses", json=round2_payload)
            assert response2.status_code == 200
            round2_body = captured_main[1].content
            assert round2_body.count(b"[slaif-live:v") == 2
            assert b"B body." not in round2_body
            session = self._governed_session(app, settings)
            assert session is not None
            snapshot = session.owner.snapshot
            assert snapshot is not None
            d_state = snapshot.state.d_state
            assert d_state.issuances == ()  # the error body still earns none
            occurrences = [o for o in d_state.occurrences if o.call_id == "c9"]
            assert len(occurrences) == 1
            assert occurrences[0].anchored is False

    async def test_compiler_traffic_never_observed_for_issuance(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The compiler upstream (the direct tool-free channel) is
        never fed to the issuance observer: the compiler's completion
        carries a well-formed tool call that WOULD be an issuance if
        it were observed as the main response, and no such issuance
        is registered (the compiler's own validation of the content
        still runs and the round completes)."""
        monkeypatch.setenv("TEST_V1_MARKER_KEY", "0123456789abcdef0123456789abcdef")
        monkeypatch.setenv("TEST_V1_COMPILER_KEY", "test-only-compiler")
        monkeypatch.setenv("TEST_V1_UPSTREAM_KEY", "test-only-upstream")
        settings = _v1_settings(tmp_path)
        recovery_root = settings.context_cache.recovery.root
        assert recovery_root is not None
        recovery_root.mkdir(mode=0o700)
        recovery_root.chmod(0o700)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []

        def compiler_handler(request: httpx.Request) -> httpx.Response:
            captured_compile.append(request)
            body = json.loads(request.content)
            user = body["messages"][1]["content"]
            index = _index_for_demand(user, body["model"])
            return httpx.Response(
                200,
                json={
                    "id": "chatcmpl-022c",
                    "object": "chat.completion",
                    "model": "qwen38-27b",
                    "choices": (
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": serialize_compiled_index(index).decode("utf-8"),
                                "tool_calls": (
                                    {
                                        "id": "evil-1",
                                        "type": "function",
                                        "function": {
                                            "name": "exec_command",
                                            "arguments": json.dumps({"cmd": "cat evil.md"}),
                                        },
                                    },
                                ),
                            },
                            "finish_reason": "stop",
                        },
                    ),
                    "usage": {
                        "prompt_tokens": 1,
                        "completion_tokens": 1,
                        "total_tokens": 2,
                    },
                },
            )

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_handler(request)
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            return httpx.Response(200, json={"id": "resp-022c"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            response1 = await client.post(
                "/v1/responses",
                json={
                    "model": "qwen38-27b",
                    "input": [root_item("Follow `c1.md` before acting.\n")],
                },
            )
            assert response1.status_code == 200
            assert response1.json() == {"id": "resp-022c"}
            # The compile ran (the content validated through the
            # ACTUAL compiler parser) and the root marker was minted.
            assert len(captured_compile) == 1
            assert captured_main[0].content.count(b"[slaif-live:v") == 1
            # The compiler's tool call was NEVER observed as an
            # issuance (the observer only consumes the actual direct
            # main upstream response).
            session = self._governed_session(app, settings)
            assert session is not None
            snapshot = session.owner.snapshot
            assert snapshot is not None
            assert snapshot.state.d_state.issuances == ()

    async def test_two_distinct_frozen_frontiers_never_rebase_on_later_facts(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The per-request FROZEN represented-frontier law end to end
        over the ACTUAL FastAPI entry point (two distinct frontiers):
        round one (the cold bootstrap commits the graph-admitted cA
        read UNANCHORED) issues xA from the ACTUAL split SSE stream
        under its own frozen frontier (the root fact plus the cA
        occurrence); round two pairs the xA receipt, anchoring the
        new occurrence under that EXACT frozen frontier (one proven
        parent edge per member), and this request's own represented
        frontier reduces to the single new occurrence (both proven
        ancestors reduce); the round-two nonstream response then
        issues y under THAT distinct frontier.  The two retained
        issuances carry two DISTINCT frozen frontiers: the first one
        is never rebased on the later-committed receipt."""
        monkeypatch.setenv("TEST_V1_MARKER_KEY", "0123456789abcdef0123456789abcdef")
        monkeypatch.setenv("TEST_V1_COMPILER_KEY", "test-only-compiler")
        monkeypatch.setenv("TEST_V1_UPSTREAM_KEY", "test-only-upstream")
        settings = _v1_settings(tmp_path)
        recovery_root = settings.context_cache.recovery.root
        assert recovery_root is not None
        recovery_root.mkdir(mode=0o700)
        recovery_root.chmod(0o700)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)
        root_body = "Follow `cA.md` and `x1.md` before acting.\n"
        xA_args = json.dumps({"cmd": "cat x1.md"})

        def sse(data: dict[str, Any]) -> bytes:
            return (
                b"data: "
                + json.dumps(data, separators=(",", ":"), ensure_ascii=True).encode()
                + b"\n\n"
            )

        # The round-one ACTUAL direct SSE response: the complete xA
        # function call assembled over bounded chunk seams (one frame
        # is deliberately split across two yielded chunks so the
        # incremental assembly runs over real seams).
        frame_added = sse(
            {
                "type": "response.output_item.added",
                "item": {
                    "type": "function_call",
                    "id": "fc-xA",
                    "call_id": "xA",
                    "name": "exec_command",
                    "arguments": "",
                },
            }
        )
        frame_delta_1 = sse(
            {
                "type": "response.function_call_arguments.delta",
                "item_id": "xA",
                "delta": '{"cmd": "',
            }
        )
        frame_delta_2 = sse(
            {
                "type": "response.function_call_arguments.delta",
                "item_id": "xA",
                "delta": 'cat x1.md"}',
            }
        )
        frame_completed = sse(
            {
                "type": "response.function_call_arguments.completed",
                "item_id": "xA",
                "item": {
                    "type": "function_call",
                    "id": "fc-xA",
                    "call_id": "xA",
                    "name": "exec_command",
                    "arguments": xA_args,
                },
            }
        )
        frame_done = sse(
            {"type": "response.completed", "response": {"id": "resp-r1", "status": "completed"}}
        )
        full_stream = (
            frame_added
            + frame_delta_1
            + frame_delta_2
            + frame_completed
            + frame_done
            + b"data: [DONE]\n\n"
        )
        split_at = len(frame_added) + len(frame_delta_1) // 2  # mid-frame

        class XStream(httpx.AsyncByteStream):
            async def __aiter__(self) -> AsyncIterator[bytes]:
                yield full_stream[:split_at]
                yield full_stream[split_at:]

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo(request)
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            if len(captured_main) == 1:
                return httpx.Response(
                    200, headers={"content-type": "text/event-stream"}, stream=XStream()
                )
            if len(captured_main) == 2:
                # The round-two direct (nonstream) response issues y.
                return httpx.Response(
                    200,
                    json={
                        "id": "resp-r2",
                        "status": "completed",
                        "output": (
                            {
                                "type": "function_call",
                                "id": "fc-y",
                                "call_id": "y",
                                "name": "exec_command",
                                "arguments": json.dumps({"cmd": "cat y1.md"}),
                            },
                        ),
                    },
                )
            return httpx.Response(200, json={"id": f"resp-r{len(captured_main)}"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            # Round one: the cold bootstrap over root + the cA read
            # pair (the root references cA.md: graph-admitted); the
            # ACTUAL split SSE issues xA under this request's frozen
            # represented frontier.
            response1 = await client.post(
                "/v1/responses",
                json={
                    "model": "qwen38-27b",
                    "input": [
                        root_item(root_body),
                        exec_call("cA", "cat cA.md"),
                        out_item("cA", frame("CA body.\n")),
                    ],
                    "stream": True,
                },
            )
            assert response1.status_code == 200
            # The actual SSE passes through byte-identical.
            assert response1.content == full_stream
            round1_body = captured_main[0].content
            assert round1_body.count(b"[slaif-live:v") == 2  # root + cA
            assert b"CA body." not in round1_body
            assert b"Follow `cA.md` and `x1.md` before acting." not in round1_body
            assert len(captured_compile) == 2  # root + cA, once each
            session = self._governed_session(app, settings)
            assert session is not None
            # The bootstrap (root + cA) is revision one; the xA
            # issuance registration is revision two.
            assert session.owner.revision == 2
            snapshot = session.owner.snapshot
            assert snapshot is not None
            d = snapshot.state.d_state
            occs = {o.call_id: o for o in d.occurrences}
            assert set(occs) == {"cA"}
            occ_a = occs["cA"]
            assert occ_a.anchored is False  # client history: no binding
            issuances = {i.call_id: i for i in d.issuances}
            assert set(issuances) == {"xA"}
            x_issuance = issuances["xA"]
            # The FROZEN round-one frontier: exactly the two facts
            # this request represents (never the retained state).
            assert x_issuance.parent_frontier == tuple(
                sorted((CAUSAL_ROOT_FACT, occ_a.occurrence_id))
            )
            # Round two: the xA receipt pairs with the retained
            # issuance: the new occurrence is ANCHORED under the
            # frozen round-one frontier (one proven parent edge per
            # member), and this request's own represented frontier
            # reduces to the single new occurrence (both proven
            # ancestors reduce).
            round2_payload = {
                "model": "qwen38-27b",
                "input": [
                    root_item(root_body),
                    exec_call("xA", "cat x1.md"),
                    out_item("xA", frame("X1 body.\n")),
                ],
            }
            response2 = await client.post("/v1/responses", json=round2_payload)
            assert response2.status_code == 200
            round2_body = captured_main[1].content
            assert round2_body.count(b"[slaif-live:v") == 2  # root + x1
            assert b"X1 body." not in round2_body
            assert b"Follow `cA.md` and `x1.md` before acting." not in round2_body
            assert len(captured_compile) == 3  # + the x1 read entry
            session = self._governed_session(app, settings)
            assert session is not None
            # The anchor (revision three) and the y issuance
            # (revision four).
            assert session.owner.revision == 4
            snapshot = session.owner.snapshot
            assert snapshot is not None
            d = snapshot.state.d_state
            occs = {o.call_id: o for o in d.occurrences}
            assert set(occs) == {"cA", "xA"}
            occ_x1 = occs["xA"]
            assert occ_x1.anchored is True
            links = {(link.child, link.parent) for link in d.parent_links}
            assert (occ_x1.occurrence_id, CAUSAL_ROOT_FACT) in links
            assert (occ_x1.occurrence_id, occ_a.occurrence_id) in links
            issuances = {i.call_id: i for i in d.issuances}
            assert set(issuances) == {"xA", "y"}
            y_issuance = issuances["y"]
            # The two DISTINCT frozen frontiers: y registered under
            # the reduced round-two frontier; xA's frontier is the
            # EXACT round-one one (never rebased on the later
            # committed receipt).
            assert y_issuance.parent_frontier == (occ_x1.occurrence_id,)
            assert x_issuance.parent_frontier == tuple(
                sorted((CAUSAL_ROOT_FACT, occ_a.occurrence_id))
            )
            assert x_issuance.parent_frontier != y_issuance.parent_frontier
            assert occ_x1.occurrence_id not in x_issuance.parent_frontier
            # Round three: the resend of the OWN transformed payload
            # is the byte-identical fixed point (no rebase, no
            # further upstream calls: the RAM hit).
            response3 = await client.post(
                "/v1/responses",
                content=round2_body,
                headers={"content-type": "application/json"},
            )
            assert response3.status_code == 200
            assert captured_main[2].content == round2_body
            assert len(captured_compile) == 3

    async def test_publish_fault_refuses_replay_until_the_generation_heals(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The replay-after-fault proof through the ACTUAL
        FastAPI/fake-upstream path: the round-two transition commits
        (the RAM revision advances) while the protected generation
        faults on fsync -- the fixed 503 refusal with NO forward,
        the durable generation and its bound untouched; the SAME
        payload resent while the fault persists is refused again (
        the retained generation-one pointer is bound to the
        revision-one snapshot it actually published: it can never
        prove the newer undurable record set); once the fault heals
        the same payload publishes generation two, the single
        outgoing body is the exact transformed form, and the resend
        is the byte-identical fixed point."""
        monkeypatch.setenv("TEST_V1_MARKER_KEY", "0123456789abcdef0123456789abcdef")
        monkeypatch.setenv("TEST_V1_COMPILER_KEY", "test-only-compiler")
        monkeypatch.setenv("TEST_V1_UPSTREAM_KEY", "test-only-upstream")
        settings = _v1_settings(tmp_path)
        recovery_root = settings.context_cache.recovery.root
        assert recovery_root is not None
        recovery_root.mkdir(mode=0o700)
        recovery_root.chmod(0o700)
        real_fsync = os.fsync
        fault = {"on": False}

        def faulty_fsync(fd: int) -> None:
            if fault["on"]:
                raise OSError(5, "I/O error")
            real_fsync(fd)

        # The injected durable-fault window: the round-two protected
        # generation (and every attempt while the window is open)
        # fails at fsync; everything else is the real fsync.
        monkeypatch.setattr(os, "fsync", faulty_fsync)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)
        root_body = "Follow `c1.md` before acting.\n"

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo(request)
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            return httpx.Response(200, json={"id": f"resp-r{len(captured_main)}"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            # Round one: the cold bootstrap publishes generation one.
            response1 = await client.post(
                "/v1/responses",
                json={"model": "qwen38-27b", "input": [root_item(root_body)]},
            )
            assert response1.status_code == 200
            round1_body = captured_main[0].content
            assert round1_body.count(b"[slaif-live:v") == 1
            assert b"Follow `c1.md` before acting." not in round1_body
            session = self._governed_session(app, settings)
            assert session is not None
            assert session.session_owner is not None
            assert session.last_publish is not None
            assert session.last_publish.generation == 1
            assert session.last_publish_bound is not None
            assert session.last_publish_bound[0] == 1
            assert session.session_owner.bound_generation == 1
            round2_payload = {
                "model": "qwen38-27b",
                "input": [
                    root_item(root_body),
                    exec_call("c1", "cat c1.md"),
                    out_item("c1", frame("A body.\n")),
                ],
            }
            # Round two: the commit applies (RAM revision two) while
            # the protected generation faults: the fixed 503 refusal
            # with NO forward.
            fault["on"] = True
            response2 = await client.post("/v1/responses", json=round2_payload)
            assert response2.status_code == 503
            error2 = response2.json()["error"]
            assert error2["code"] == "v1_publish_refused"
            assert error2["message"] == "governed v1 request refused"
            assert len(captured_main) == 1  # no forward, no raw fallback
            assert session.owner.revision == 2
            snapshot = session.owner.snapshot
            assert snapshot is not None
            assert snapshot.state.d_state.revision == 2
            # The durable generation and its bound are UNTOUCHED:
            # the retained pointer still proves only revision one.
            assert session.last_publish is not None
            assert session.last_publish.generation == 1
            assert session.last_publish_bound is not None
            assert session.last_publish_bound[0] == 1
            assert session.session_owner is not None
            assert session.session_owner.bound_generation == 1
            # The SAME payload resent while the fault persists:
            # refused again (the newer undurable record set is never
            # forwarded under the stale proof).
            response3 = await client.post("/v1/responses", json=round2_payload)
            assert response3.status_code == 503
            assert response3.json()["error"]["code"] == "v1_publish_refused"
            assert len(captured_main) == 1
            assert session.owner.revision == 2
            assert session.session_owner is not None
            assert session.session_owner.bound_generation == 1
            assert session.last_publish is not None
            assert session.last_publish.generation == 1
            # The fault heals: the same payload now publishes
            # generation two and the single outgoing body is the
            # exact transformed form.
            fault["on"] = False
            response4 = await client.post("/v1/responses", json=round2_payload)
            assert response4.status_code == 200
            round2_body = captured_main[1].content
            assert round2_body.count(b"[slaif-live:v") == 2  # root + c1
            assert b"A body." not in round2_body
            assert b"Follow `c1.md` before acting." not in round2_body
            assert len(captured_compile) == 2
            assert session.last_publish is not None
            assert session.last_publish.generation == 2
            assert session.last_publish_bound is not None
            assert session.last_publish_bound[0] == 2
            assert session.session_owner is not None
            assert session.session_owner.bound_generation == 2
            # The resend of the OWN transformed payload: the
            # byte-identical fixed point (the ordinary hit under the
            # retained generation-two publication, no recompile).
            response5 = await client.post(
                "/v1/responses",
                content=round2_body,
                headers={"content-type": "application/json"},
            )
            assert response5.status_code == 200
            assert captured_main[2].content == round2_body
            assert len(captured_compile) == 2
            assert session.session_owner is not None
            assert session.session_owner.bound_generation == 2


# ---------------------------------------------------------------------------
# 022-d: the v1 application closure at the actual create_app entry point
# (the COLD marker gate before raw acquisition, the currentness 409 family
# over the accepted 020 owned/fenced admit/checkpoint path, and the complete
# R01-R05/S01-S02 application evidence for BOTH endpoints over one bounded
# fake upstream; synthetic identity, environment names and fixture sources;
# no real secrets, no live upstream).
# ---------------------------------------------------------------------------

_SYNTHETIC_TAG = "[slaif-live:v1:SYNTHETIC]"
_TAG_RE = re.compile(rb"\[slaif-(?:live|evidence):v1:[A-Za-z0-9_-]{43}\]")


class TestV1ApplicationClosure:
    """The ordered 022-d acceptance: marker-side cold refusal, the
    currentness/fence refusal family with zero main forward, and the
    endpoint-complete application evidence (Chat stable placement,
    split-SSE issuance, source-absent reinjection, change/replay/revert,
    failure families, disconnect and route protection)."""

    @staticmethod
    def _setup(
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        *,
        principal: str = "local-principal",
        session: str = "local-session",
        extra_ungoverned_route: bool = False,
    ) -> Settings:
        """The closed v1 settings with the protected recovery root
        prepared (the store never creates it) and the three synthetic
        protected environment references set."""
        monkeypatch.setenv("TEST_V1_MARKER_KEY", "0123456789abcdef0123456789abcdef")
        monkeypatch.setenv("TEST_V1_COMPILER_KEY", "test-only-compiler")
        monkeypatch.setenv("TEST_V1_UPSTREAM_KEY", "test-only-upstream")
        settings = _v1_settings(tmp_path)
        if principal != "local-principal" or session != "local-session":
            settings = settings.model_copy(
                update={
                    "constitution": settings.constitution.model_copy(
                        update={"principal": principal, "session": session}
                    )
                }
            )
        if extra_ungoverned_route:
            settings = settings.model_copy(
                update={
                    "routes": [
                        settings.routes[0],
                        RouteConfig(
                            name="plain",
                            model="other-model",
                            max_images_per_request=0,
                            image_overflow_policy="reject",
                        ),
                    ]
                }
            )
        recovery_root = settings.context_cache.recovery.root
        assert recovery_root is not None
        recovery_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        recovery_root.chmod(0o700)
        return settings

    @staticmethod
    def _session(
        app: Any,
        settings: Settings,
        *,
        principal: str = "local-principal",
        session: str = "local-session",
    ) -> V1Session | None:
        runtime = app.state.v1_runtime
        assert runtime is not None
        identity = RequestIdentity(
            principal=principal,
            session=session,
            repository="local-repository",
            route="text",
        )
        address = build_session_address(
            runtime,
            identity,
            settings.routes[0],
            settings.context_cache.route_contracts["text"],
        )
        return cast("V1Session | None", app.state.v1_sessions.get(address))

    @staticmethod
    def _root_envelope_text(content: str) -> str:
        """The exact Codex user-message envelope (the recognized root
        carrier text; root authority is Responses-only)."""
        return (
            f"# AGENTS.md instructions for {WORKSPACE}\n\n"
            f"<INSTRUCTIONS>\n{content}\n</INSTRUCTIONS>\n"
        )

    # -- 022-d section 1: the COLD marker gate ----------------------

    async def test_cold_marker_in_root_refuses_before_any_acquisition(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The fresh-address marker law end to end: the synthetic
        non-authoritative tag in the FIRST root envelope of a fresh
        trusted session is the fixed 409 marker-side refusal BEFORE
        any raw acquisition, owner allocation or checkpoint (zero main
        forward, zero compile, no live owner, no committed
        generation); the same address's later legitimate root
        bootstraps successfully at generation one."""
        settings = self._setup(monkeypatch, tmp_path)
        recovery_root = settings.context_cache.recovery.root
        assert recovery_root is not None
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo(request)
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            return httpx.Response(200, json={"id": f"resp-r{len(captured_main)}"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            # The first root envelope carries the synthetic tag inside
            # the recognized root content span: the fixed refusal.
            payload1 = {
                "model": "qwen38-27b",
                "input": [root_item(f"Follow the workspace protocol.\n{_SYNTHETIC_TAG}\n")],
            }
            response1 = await client.post("/v1/responses", json=payload1)
            assert response1.status_code == 409
            error1 = response1.json()["error"]
            assert error1["code"] == "v1_transaction_conflict"
            assert error1["message"] == "governed v1 request refused"
            # Zero new owner, generation, compile and main calls.
            assert len(captured_main) == 0
            assert len(captured_compile) == 0
            assert self._session(app, settings) is None
            # No committed protected generation for the address.
            runtime = app.state.v1_runtime
            assert runtime is not None
            identity = RequestIdentity(
                principal="local-principal",
                session="local-session",
                repository="local-repository",
                route="text",
            )
            address = build_session_address(
                runtime,
                identity,
                settings.routes[0],
                settings.context_cache.route_contracts["text"],
            )
            probe = runtime.recovery_store.open_session(address)
            try:
                assert probe.current_generation() == 0
            finally:
                probe.close()
            # The same address's LATER legitimate root bootstraps.
            response2 = await client.post(
                "/v1/responses",
                json={
                    "model": "qwen38-27b",
                    "input": [root_item("Follow the workspace protocol.\n")],
                },
            )
            assert response2.status_code == 200
            round2_body = captured_main[0].content
            assert round2_body.count(b"[slaif-live:v") == 1
            assert b"Follow the workspace protocol." not in round2_body
            assert len(captured_compile) == 1
            session = self._session(app, settings)
            assert session is not None
            assert session.last_publish is not None
            assert session.last_publish.generation == 1
            assert session.last_publish_bound == (1, 1)
            assert session.session_owner is not None
            assert session.session_owner.bound_generation == 1

    async def test_cold_marker_outside_source_spans_stays_data(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The closed-location law: a marker-shaped string OUTSIDE the
        actual cold-recognized source spans (an ordinary input_text
        item) stays data -- the legitimate root bootstraps and the
        ordinary text crosses the wire byte-present; and a ROOTLESS
        payload carrying the tag is not a governed request at all
        (forwarded unchanged, no session, no compile)."""
        settings = self._setup(monkeypatch, tmp_path)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo(request)
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            return httpx.Response(200, json={"id": f"resp-r{len(captured_main)}"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            payload = {
                "model": "qwen38-27b",
                "input": [
                    root_item("Follow the workspace protocol.\n"),
                    {
                        "type": "input_text",
                        "text": f"ordinary text mentioning {_SYNTHETIC_TAG} elsewhere",
                    },
                ],
            }
            response1 = await client.post("/v1/responses", json=payload)
            assert response1.status_code == 200
            body1 = captured_main[0].content
            # The legitimate root is the ONLY edited carrier.
            assert len(_TAG_RE.findall(body1)) == 1
            assert b"Follow the workspace protocol." not in body1
            # The ordinary marker-shaped text stays data, byte-present.
            assert b"ordinary text mentioning [slaif-live:v1:SYNTHETIC] elsewhere" in body1
            assert len(captured_compile) == 1
            assert self._session(app, settings) is not None

        # The ROOTLESS tagged payload: not a governed request.
        settings2 = self._setup(monkeypatch, tmp_path / "second")
        captured_main2: list[httpx.Request] = []
        captured_compile2: list[httpx.Request] = []
        compiler_echo2 = _echo_compiler_handler(captured_compile2)

        def handler2(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo2(request)
            assert request.url.path == "/v1/responses"
            captured_main2.append(request)
            return httpx.Response(200, json={"id": "resp-plain"})

        app2 = create_app(settings2, httpx.MockTransport(handler2))
        assert app2.state.v1_runtime is not None
        rootless = {
            "model": "qwen38-27b",
            "input": [{"type": "input_text", "text": f"note {_SYNTHETIC_TAG}"}],
        }
        sent = json.dumps(rootless, separators=(",", ":"), ensure_ascii=True).encode()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app2), base_url="http://adapter.test"
        ) as client2:
            response2 = await client2.post(
                "/v1/responses", content=sent, headers={"content-type": "application/json"}
            )
        assert response2.status_code == 200
        assert len(captured_main2) == 1
        assert captured_main2[0].content == sent  # forwarded unchanged
        assert len(captured_compile2) == 0
        assert self._session(app2, settings2) is None

    async def test_cold_prior_session_marker_refused_across_sessions(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The isolation proof: a marker actually issued by trusted
        session A, presented COLD to a DIFFERENT trusted namespace B
        (different principal/session, identical source, the SAME
        protected recovery root), is the fixed 409 with zero
        acquisition for B -- B's fresh address cannot authenticate
        A's retained source marker.  B's own clean identical root
        then bootstraps with its own compile and its own distinct
        marker (no cross-namespace reuse or resolution)."""
        settings_a = self._setup(monkeypatch, tmp_path)
        settings_b = self._setup(
            monkeypatch,
            tmp_path,
            principal="other-principal",
            session="other-session",
        )
        captured_main_a: list[httpx.Request] = []
        captured_compile_a: list[httpx.Request] = []
        captured_main_b: list[httpx.Request] = []
        captured_compile_b: list[httpx.Request] = []
        compiler_echo_a = _echo_compiler_handler(captured_compile_a)
        compiler_echo_b = _echo_compiler_handler(captured_compile_b)
        root_body = "Follow the workspace protocol.\n"

        def handler_a(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo_a(request)
            assert request.url.path == "/v1/responses"
            captured_main_a.append(request)
            return httpx.Response(200, json={"id": "resp-a1"})

        def handler_b(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo_b(request)
            assert request.url.path == "/v1/responses"
            captured_main_b.append(request)
            return httpx.Response(200, json={"id": f"resp-b{len(captured_main_b)}"})

        app_a = create_app(settings_a, httpx.MockTransport(handler_a))
        app_b = create_app(settings_b, httpx.MockTransport(handler_b))
        assert app_a.state.v1_runtime is not None
        assert app_b.state.v1_runtime is not None
        async with (
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app_a),
                base_url="http://adapter.test",
            ) as client_a,
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app_b),
                base_url="http://adapter.test",
            ) as client_b,
        ):
            # Session A bootstraps and mints its own marker.
            response_a1 = await client_a.post(
                "/v1/responses",
                json={"model": "qwen38-27b", "input": [root_item(root_body)]},
            )
            assert response_a1.status_code == 200
            tag_a = _TAG_RE.search(captured_main_a[0].content)
            assert tag_a is not None
            assert len(captured_compile_a) == 1
            # Session B cold-presents the SAME root carrying A's
            # actual tag: the fixed marker-side refusal for B.
            response_b1 = await client_b.post(
                "/v1/responses",
                json={
                    "model": "qwen38-27b",
                    "input": [root_item(f"{root_body}{tag_a.group(0).decode()}\n")],
                },
            )
            assert response_b1.status_code == 409
            error_b1 = response_b1.json()["error"]
            assert error_b1["code"] == "v1_transaction_conflict"
            assert len(captured_main_b) == 0
            assert len(captured_compile_b) == 0
            assert (
                self._session(
                    app_b, settings_b, principal="other-principal", session="other-session"
                )
                is None
            )
            # B's own clean identical root: its own compile and its
            # own DISTINCT marker (the MAC is namespace-scoped).
            response_b2 = await client_b.post(
                "/v1/responses",
                json={"model": "qwen38-27b", "input": [root_item(root_body)]},
            )
            assert response_b2.status_code == 200
            body_b2 = captured_main_b[0].content
            assert body_b2.count(b"[slaif-live:v") == 1
            assert b"Follow the workspace protocol." not in body_b2
            assert len(captured_compile_b) == 1
            tag_b = _TAG_RE.search(body_b2)
            assert tag_b is not None
            assert tag_b.group(0) != tag_a.group(0)
            # A's state is untouched by B's attempts.
            session_a = self._session(app_a, settings_a)
            assert session_a is not None
            assert session_a.last_publish is not None
            assert session_a.last_publish.generation == 1
            assert tag_b.group(0) != tag_a.group(0)
            # A's state is untouched by B's attempts.
            session_a = self._session(app_a, settings_a)
            assert session_a is not None
            assert session_a.last_publish is not None
            assert session_a.last_publish.generation == 1

    # -- 022-d section 2: currentness and the accepted fence --------

    @staticmethod
    def _currentness_round2_payload() -> dict[str, Any]:
        """The boundaryless mixed root-bearing result: the complete
        frame carries a NEW AGENTS.md region (the governing root of
        the result cannot be established under P source policy) plus
        the referenced A.md content in one boundaryless bundle."""
        return {
            "model": "qwen38-27b",
            "input": [
                root_item("Follow `A.md` before acting.\n"),
                exec_call("c1", "cat AGENTS.md A.md"),
                out_item(
                    "c1",
                    frame("# AGENTS.md\n\nWorkspace protocol revision two.\n" + "A body.\n"),
                ),
            ],
        }

    @staticmethod
    def _issuing_handler(
        captured_main: list[httpx.Request],
        compiler_echo: Any,
        *,
        cmd: str,
        call_id: str = "c1",
    ) -> Any:
        """The main upstream: the FIRST direct response issues ONE
        complete exec_command read; every later response is plain."""

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return cast("httpx.Response", compiler_echo(request))
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            if len(captured_main) == 1:
                return httpx.Response(
                    200,
                    json={
                        "id": "resp-r1",
                        "status": "completed",
                        "output": (
                            {
                                "type": "function_call",
                                "id": f"fc-{call_id}",
                                "call_id": call_id,
                                "name": "exec_command",
                                "arguments": json.dumps({"cmd": cmd}),
                            },
                        ),
                    },
                )
            return httpx.Response(200, json={"id": f"resp-r{len(captured_main)}"})

        return handler

    async def test_unproven_currentness_refuses_with_retained_evidence(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The accepted typed 409 for established root currentness:
        the legitimate root (referencing A.md) bootstraps and its
        direct response issues the complete AGENTS.md+A.md read; the
        subsequent boundaryless root-bearing result yields the ACTUAL
        P/Q/T evidence `root_currentness_unproven` and the transaction
        is the fixed 409 with ZERO main forward (the negative evidence
        is committed and retained -- the adverse transition publishes
        the fence generation and the state generation; no bootstrap
        fallback); the identical request repeated is refused again."""
        settings = self._setup(monkeypatch, tmp_path)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)
        app = create_app(
            settings,
            httpx.MockTransport(
                self._issuing_handler(captured_main, compiler_echo, cmd="cat AGENTS.md A.md")
            ),
        )
        assert app.state.v1_runtime is not None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            # Round one: the legitimate root; the direct response
            # issues the complete read (bootstrap + issuance).
            response1 = await client.post(
                "/v1/responses",
                json={
                    "model": "qwen38-27b",
                    "input": [root_item("Follow `A.md` before acting.\n")],
                },
            )
            assert response1.status_code == 200
            session = self._session(app, settings)
            assert session is not None
            assert session.owner.revision == 2
            assert session.last_publish is not None
            assert session.last_publish.generation == 2
            assert session.last_publish_bound == (2, 1)
            assert session.session_owner is not None
            assert session.session_owner.bound_generation == 2
            # Round two: the boundaryless root-bearing result.
            response2 = await client.post("/v1/responses", json=self._currentness_round2_payload())
            assert response2.status_code == 409
            error2 = response2.json()["error"]
            assert error2["code"] == "v1_transaction_conflict"
            assert error2["message"] == "governed v1 request refused"
            assert len(captured_main) == 1  # zero main forward
            # The negative evidence is committed and retained.
            assert session.owner.revision == 3
            assert session.last_publish is not None
            assert session.last_publish.generation == 4
            assert session.last_publish_bound == (3, 1)
            assert session.session_owner is not None
            assert session.session_owner.bound_generation == 4
            snapshot = session.owner.snapshot
            assert snapshot is not None
            assert snapshot.result.outcome is RootRegionAdmissionOutcome.ROOT_CURRENTNESS_UNPROVEN
            r_result = snapshot.result.r_result
            assert r_result is not None
            q_result = r_result.q_result
            assert q_result is not None
            assert q_result.outcome is RootRegionCurrentnessOutcome.ROOT_CURRENTNESS_UNPROVEN
            witness_classes = {w.uncertainty_class for w in q_result.uncertainty_witnesses}
            assert RootRegionUncertaintyClass.OPAQUE_ROOT_BEARING_GROUP in witness_classes
            # The identical request repeated: refused again, no
            # forward, no bootstrap fallback.
            response3 = await client.post("/v1/responses", json=self._currentness_round2_payload())
            assert response3.status_code == 409
            assert response3.json()["error"]["code"] == "v1_transaction_conflict"
            assert len(captured_main) == 1
            response3 = await client.post("/v1/responses", json=self._currentness_round2_payload())
            assert response3.status_code == 409
            assert response3.json()["error"]["code"] == "v1_transaction_conflict"
            assert len(captured_main) == 1

    async def test_adverse_fence_fault_refuses_and_heals_to_conflict(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The fence-law fault test through the actual path: the
        fault-injection raises `OSError` in `os.fsync` for the
        round-two transition -- the adverse durable FENCE cannot
        publish, so NO state transition is permitted at all: the
        fixed 503 transition refusal with no forward, the RAM
        revision, the durable generation and the bound all untouched;
        once the fault heals the same request earns the accepted
        currentness 409 (fence + state generations published, bound
        advanced)."""
        settings = self._setup(monkeypatch, tmp_path)
        real_fsync = os.fsync
        fault = {"on": False}

        def faulty_fsync(fd: int) -> None:
            if fault["on"]:
                raise OSError(5, "I/O error")
            real_fsync(fd)

        monkeypatch.setattr(os, "fsync", faulty_fsync)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)
        app = create_app(
            settings,
            httpx.MockTransport(
                self._issuing_handler(captured_main, compiler_echo, cmd="cat AGENTS.md A.md")
            ),
        )
        assert app.state.v1_runtime is not None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            response1 = await client.post(
                "/v1/responses",
                json={
                    "model": "qwen38-27b",
                    "input": [root_item("Follow `A.md` before acting.\n")],
                },
            )
            assert response1.status_code == 200
            session = self._session(app, settings)
            assert session is not None
            assert session.owner.revision == 2
            assert session.last_publish is not None
            assert session.last_publish.generation == 2
            assert session.last_publish_bound == (2, 1)
            # The fault window opens for the round-two transition.
            fault["on"] = True
            response2 = await client.post("/v1/responses", json=self._currentness_round2_payload())
            assert response2.status_code == 503
            error2 = response2.json()["error"]
            assert error2["code"] == "v1_transition_refused"
            assert error2["message"] == "governed v1 request refused"
            assert len(captured_main) == 1  # no forward, no raw fallback
            # NOTHING was permitted: no RAM advance, no generation,
            # the prior bound retained.
            assert session.owner.revision == 2
            assert session.last_publish is not None
            assert session.last_publish.generation == 2
            assert session.last_publish_bound == (2, 1)
            assert session.session_owner is not None
            assert session.session_owner.bound_generation == 2
            # The fault heals: the same request now earns the
            # accepted currentness 409 with the fence + state
            # generations published.
            fault["on"] = False
            response3 = await client.post("/v1/responses", json=self._currentness_round2_payload())
            assert response3.status_code == 409
            assert response3.json()["error"]["code"] == "v1_transaction_conflict"
            assert len(captured_main) == 1
            assert session.owner.revision == 3
            assert session.last_publish is not None
            assert session.last_publish.generation == 4
            assert session.last_publish_bound == (3, 1)
            assert session.session_owner is not None
            assert session.session_owner.bound_generation == 4

    async def test_cold_prepublication_failure_cleans_owner_and_recovers(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The cold prepublication failure law: the fault-injection
        raises `OSError` in `os.fsync` starting with the SECOND fsync
        (the first hit is the resume probe's session-directory
        fsync), so the checkpoint file's fsync fails while the cold
        owner/writer is already acquired: the fixed 503 cold-publish
        refusal with zero main/compile, the acquired owner and writer
        safely torn down (no live owner, no committed generation, the
        orphan checkpoint bytes unreferenced by any pointer), the
        same-process re-establishment fail-closed (the fenced epoch
        law mints a DISTINCT epoch for the re-acquired owner, so its
        record can never match the orphan bytes and the torn-
        checkpoint law refuses without any main forward), and the
        later legitimate cold startup of the SAME address in a FRESH
        process succeeds at generation one (the store's idempotent
        same-generation orphan re-publication: the fresh registry's
        first allocation is epoch one again, so the re-derived
        record is byte-identical and completes the interrupted
        publication)."""
        settings = self._setup(monkeypatch, tmp_path)
        real_fsync = os.fsync
        fault = {"on": True, "skip": 1, "n": 0}

        def faulty_fsync(fd: int) -> None:
            fault["n"] += 1
            if fault["on"] and fault["n"] > fault["skip"]:
                raise OSError(5, "I/O error")
            real_fsync(fd)

        monkeypatch.setattr(os, "fsync", faulty_fsync)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo(request)
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            return httpx.Response(200, json={"id": f"resp-r{len(captured_main)}"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        root_payload = {
            "model": "qwen38-27b",
            "input": [root_item("Follow the workspace protocol.\n")],
        }
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            response1 = await client.post("/v1/responses", json=root_payload)
            assert response1.status_code == 503
            error1 = response1.json()["error"]
            assert error1["code"] == "v1_cold_publish_refused"
            assert error1["message"] == "governed v1 request refused"
            assert len(captured_main) == 0
            assert len(captured_compile) == 0
            # The acquired cold owner/writer was torn down: no live
            # session, no committed generation for the address.
            assert self._session(app, settings) is None
            runtime = app.state.v1_runtime
            assert runtime is not None
            identity = RequestIdentity(
                principal="local-principal",
                session="local-session",
                repository="local-repository",
                route="text",
            )
            address = build_session_address(
                runtime,
                identity,
                settings.routes[0],
                settings.context_cache.route_contracts["text"],
            )
            probe = runtime.recovery_store.open_session(address)
            try:
                assert probe.current_generation() == 0
            finally:
                probe.close()
            # The failed publication left the orphan checkpoint
            # bytes on disk, unreferenced by any pointer.
            session_dir = runtime.recovery_store.root / session_directory_name(address)
            assert (session_dir / "checkpoint-1.json").is_file()
            assert not (session_dir / "current.json").exists()
        # The same-process re-establishment is fail-closed: the
        # fenced epoch law mints a DISTINCT epoch for the re-
        # acquired owner, so its record can never match the orphan
        # bytes and the torn-checkpoint law refuses (zero main
        # forward, no compile, no state change).
        fault["on"] = False
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            response1b = await client.post("/v1/responses", json=root_payload)
        assert response1b.status_code == 503
        error1b = response1b.json()["error"]
        assert error1b["code"] == "v1_cold_publish_refused"
        assert error1b["message"] == "governed v1 request refused"
        assert len(captured_main) == 0
        assert len(captured_compile) == 0
        assert self._session(app, settings) is None
        # The later legitimate cold startup after cleanup: a FRESH
        # process (a new app instance with a fresh RAM registry)
        # over the SAME recovery root re-derives the byte-identical
        # record (the fresh registry's first allocation is epoch
        # one again) and completes generation one through the
        # store's idempotent same-generation orphan re-publication.
        settings_b = self._setup(monkeypatch, tmp_path)
        assert settings_b.context_cache.recovery.root == settings.context_cache.recovery.root
        captured_main_b: list[httpx.Request] = []
        captured_compile_b: list[httpx.Request] = []
        compiler_echo_b = _echo_compiler_handler(captured_compile_b)

        def handler_b(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo_b(request)
            assert request.url.path == "/v1/responses"
            captured_main_b.append(request)
            return httpx.Response(200, json={"id": f"resp-r{len(captured_main_b)}"})

        app_b = create_app(settings_b, httpx.MockTransport(handler_b))
        assert app_b.state.v1_runtime is not None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app_b), base_url="http://adapter.test"
        ) as client:
            response2 = await client.post("/v1/responses", json=root_payload)
        assert response2.status_code == 200
        round2_body = captured_main_b[0].content
        assert round2_body.count(b"[slaif-live:v") == 1
        assert b"Follow the workspace protocol." not in round2_body
        assert len(captured_compile_b) == 1
        session = self._session(app_b, settings_b)
        assert session is not None
        assert session.last_publish is not None
        assert session.last_publish.generation == 1
        assert session.last_publish_bound == (1, 1)
        assert session.session_owner is not None
        assert session.session_owner.bound_generation == 1
        # The durable publication completed: the pointer now
        # references the checkpoint.
        runtime_b = app_b.state.v1_runtime
        assert runtime_b is not None
        identity_b = RequestIdentity(
            principal="local-principal",
            session="local-session",
            repository="local-repository",
            route="text",
        )
        address_b = build_session_address(
            runtime_b,
            identity_b,
            settings_b.routes[0],
            settings_b.context_cache.route_contracts["text"],
        )
        session_dir_b = runtime_b.recovery_store.root / session_directory_name(address_b)
        assert (session_dir_b / "current.json").is_file()
        assert (session_dir_b / "checkpoint-1.json").is_file()

    # -- 022-d section 3: the endpoint-complete application evidence --

    @staticmethod
    def _chat_read_messages(
        root_text: str,
        call_id: str,
        cmd: str,
        body: str,
        *,
        second_call_id: str | None = None,
        second_cmd: str | None = None,
        second_body: str | None = None,
    ) -> list[dict[str, Any]]:
        """The Chat carrier of a read pair (assistant tool_calls +
        tool result) after the user root message; optionally a second
        pair appended (the genuine new read of the source-change
        law)."""
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": root_text},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": cmd}),
                        },
                    }
                ],
            },
            {"role": "tool", "tool_call_id": call_id, "content": frame(body)},
        ]
        if second_call_id is not None and second_cmd is not None and second_body is not None:
            messages += [
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": second_call_id,
                            "type": "function",
                            "function": {
                                "name": "exec_command",
                                "arguments": json.dumps({"cmd": second_cmd}),
                            },
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": second_call_id, "content": frame(second_body)},
            ]
        return messages

    async def test_chat_nonstream_governed_rounds_with_compiled_system_placement(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The Chat endpoint at the actual app boundary: the
        Responses bootstrap establishes the root (the root authority
        is Responses-only; a Chat user message carrying the same
        envelope stays data, never a root carrier); the Chat rounds
        then issue AND complete their own reads on the SAME chat
        endpoint (the call-ID binding law is endpoint-inclusive: a
        responses-issued ID can never be completed on chat).  Each
        transformed outgoing body carries the ACTUAL selected
        compiled context at the stable Chat system placement as the
        FIRST message while every other message (the user root text,
        the assistant tool_calls, the tool result order) is preserved;
        the ONLY Chat source carrier edited is the acquired tool
        result (raw source gone, live marker in); the Chat direct
        response's issuance freezes under THIS request's own
        represented completed-fact frontier (c1 under the root fact,
        c2 under c1's retained occurrence -- internal compiler
        traffic and client fabrication supply none); the resend of
        the transformed body is the byte-identical fixed point with
        no further compile."""
        settings = self._setup(monkeypatch, tmp_path)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)
        root_body = "Follow `c1.md` then `c2.md` before acting.\n"
        root_text = self._root_envelope_text(root_body)

        def chat_issue(cid: str, cmd: str) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "id": f"chatcmpl-{cid}",
                    "object": "chat.completion",
                    "model": "qwen38-27b",
                    "choices": (
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": (
                                    {
                                        "id": cid,
                                        "type": "function",
                                        "function": {
                                            "name": "exec_command",
                                            "arguments": json.dumps({"cmd": cmd}),
                                        },
                                    },
                                ),
                            },
                            "finish_reason": "tool_calls",
                        },
                    ),
                    "usage": {
                        "prompt_tokens": 1,
                        "completion_tokens": 1,
                        "total_tokens": 2,
                    },
                },
            )

        def chat_plain() -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "id": "chatcmpl-plain",
                    "object": "chat.completion",
                    "model": "qwen38-27b",
                    "choices": (
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": "done"},
                            "finish_reason": "stop",
                        },
                    ),
                    "usage": {
                        "prompt_tokens": 1,
                        "completion_tokens": 1,
                        "total_tokens": 2,
                    },
                },
            )

        next_issue = {"n": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                if request.headers["authorization"] == "Bearer test-only-compiler":
                    return compiler_echo(request)
                captured_main.append(request)
                n = next_issue["n"]
                next_issue["n"] += 1
                if n == 0:
                    # The round-two Chat direct response issues c1.
                    return chat_issue("c1", "cat c1.md")
                if n == 1:
                    # The round-three Chat direct response issues c2.
                    return chat_issue("c2", "cat c2.md")
                return chat_plain()
            assert request.url.path == "/v1/responses"
            # Round one: the root-only bootstrap (no read issued on
            # the responses endpoint: its ID binding could never be
            # completed on the chat endpoint).
            return httpx.Response(
                200,
                json={
                    "id": "resp-r1",
                    "status": "completed",
                    "output": (
                        {
                            "type": "message",
                            "content": [{"type": "output_text", "text": "ok"}],
                        },
                    ),
                },
            )

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        runtime = app.state.v1_runtime
        assert runtime is not None
        identity = RequestIdentity(
            principal="local-principal",
            session="local-session",
            repository="local-repository",
            route="text",
        )
        address = build_session_address(
            runtime, identity, settings.routes[0], settings.context_cache.route_contracts["text"]
        )

        def session_state() -> Any:
            session = app.state.v1_sessions.get(address)
            assert session is not None
            return session

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            # Round one (Responses): the root-only bootstrap.
            response1 = await client.post(
                "/v1/responses",
                json={"model": "qwen38-27b", "input": [root_item(root_body)]},
            )
            assert response1.status_code == 200
            session = session_state()
            assert session.owner.revision == 1
            assert session.last_publish is not None
            assert session.last_publish.generation == 1
            assert session.last_publish_bound == (1, 1)
            assert len(captured_compile) == 1
            # Round two (Chat): the user root text is DATA (the root
            # authority is Responses-only); the outgoing body carries
            # the selected compiled root at the stable system
            # placement; the direct response issues c1.
            response2 = await client.post(
                "/v1/chat/completions",
                json={"model": "qwen38-27b", "messages": [{"role": "user", "content": root_text}]},
            )
            assert response2.status_code == 200
            session = session_state()
            assert session.owner.revision == 2
            assert session.last_publish is not None
            assert session.last_publish.generation == 2
            assert session.last_publish_bound == (2, 1)
            assert len(captured_compile) == 1
            body2 = json.loads(captured_main[0].content)
            system2 = body2["messages"][0]
            assert system2["role"] == "system"
            assert system2["content"].startswith("[slaif-compiled-context:v1]\n")
            assert system2["content"].endswith("[/slaif-compiled-context:v1]")
            assert system2["content"].count("<slaif-compiled-block") == 1
            assert body2["messages"][1] == {"role": "user", "content": root_text}
            assert captured_main[0].content.count(b"[slaif-live:v") == 0
            d_state = session.owner.snapshot.state.d_state
            assert [issuance.call_id for issuance in d_state.issuances] == ["c1"]
            c1_issuance = d_state.issuances[0]
            assert c1_issuance.endpoint == "chat"
            assert c1_issuance.parent_frontier == (CAUSAL_ROOT_FACT,)
            # Round three (Chat): the c1 result is ACQUIRED (the only
            # Chat source carrier edited live, raw source gone); the
            # outgoing body's system region now carries root AND c1;
            # the direct response issues c2 under c1's occurrence.
            response3 = await client.post(
                "/v1/chat/completions",
                json={
                    "model": "qwen38-27b",
                    "messages": self._chat_read_messages(root_text, "c1", "cat c1.md", "A body.\n"),
                },
            )
            assert response3.status_code == 200
            session = session_state()
            assert session.owner.revision == 4
            assert session.last_publish is not None
            assert session.last_publish.generation == 4
            assert session.last_publish_bound == (4, 1)
            assert len(captured_compile) == 2
            body3 = json.loads(captured_main[1].content)
            system3 = body3["messages"][0]
            assert system3["role"] == "system"
            assert system3["content"].count("<slaif-compiled-block") == 2
            assert body3["messages"][1] == {"role": "user", "content": root_text}
            assert body3["messages"][2]["role"] == "assistant"
            assert body3["messages"][3]["role"] == "tool"
            assert body3["messages"][3]["tool_call_id"] == "c1"
            assert captured_main[1].content.count(b"[slaif-live:v") == 1
            assert b"A body." not in captured_main[1].content
            d_state = session.owner.snapshot.state.d_state
            assert [
                (occurrence.call_id, occurrence.endpoint) for occurrence in d_state.occurrences
            ] == [("c1", "chat")]
            assert [issuance.call_id for issuance in d_state.issuances] == ["c1", "c2"]
            c1_occurrence = d_state.occurrences[0].occurrence_id
            c2_issuance = d_state.issuances[1]
            assert c2_issuance.endpoint == "chat"
            assert c2_issuance.parent_frontier == (c1_occurrence,)
            # Round four (Chat): the c2 result round earns the c2
            # marker (two live carriers, no evidence, both raw
            # sources gone).
            response4 = await client.post(
                "/v1/chat/completions",
                json={
                    "model": "qwen38-27b",
                    "messages": self._chat_read_messages(
                        root_text,
                        "c1",
                        "cat c1.md",
                        "A body.\n",
                        second_call_id="c2",
                        second_cmd="cat c2.md",
                        second_body="C2 body.\n",
                    ),
                },
            )
            assert response4.status_code == 200
            session = session_state()
            assert session.owner.revision == 5
            assert session.last_publish is not None
            assert session.last_publish.generation == 5
            assert session.last_publish_bound == (5, 1)
            assert len(captured_compile) == 3
            assert captured_main[2].content.count(b"[slaif-live:v") == 2
            assert captured_main[2].content.count(b"[slaif-evidence:v") == 0
            assert b"A body." not in captured_main[2].content
            assert b"C2 body." not in captured_main[2].content
            # Round five: the client resends its OWN transformed
            # payload: the byte-identical fixed point, no further
            # compile, no further generation.
            response5 = await client.post(
                "/v1/chat/completions",
                content=captured_main[2].content,
                headers={"content-type": "application/json"},
            )
            assert response5.status_code == 200
            session = session_state()
            assert session.owner.revision == 5
            assert session.last_publish is not None
            assert session.last_publish.generation == 5
            assert captured_main[3].content == captured_main[2].content
            assert len(captured_compile) == 3

    async def test_chat_split_sse_issuance_and_acquisition(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The Chat split-SSE issuance end to end: after the
        Responses bootstrap, the Chat streaming round (the user root
        text only -- no new evidence, the ordinary hit) carries the
        ACTUAL direct `chat.completion.chunk` stream whose complete
        tool call is assembled over bounded chunk seams (one frame
        deliberately split mid-frame); the issuance is registered
        under this request's FROZEN frontier (the represented root
        fact only); the stream passes through byte-identical; the
        next Chat round pairs the receipt (the read acquired, the
        occurrence anchored under that frontier, the tool carrier
        edited, the compiled region extended to both blocks)."""
        settings = self._setup(monkeypatch, tmp_path)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)
        root_body = "Follow `c1.md` before acting.\n"
        root_text = self._root_envelope_text(root_body)

        def chat_sse(data: dict[str, Any]) -> bytes:
            return (
                b"data: "
                + json.dumps(data, separators=(",", ":"), ensure_ascii=True).encode()
                + b"\n\n"
            )

        args = json.dumps({"cmd": "cat c1.md"})
        frame_1 = chat_sse(
            {
                "id": "chatcmpl-sse",
                "object": "chat.completion.chunk",
                "choices": (
                    {
                        "index": 0,
                        "delta": {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": (
                                {
                                    "index": 0,
                                    "id": "fc-c1",
                                    "type": "function",
                                    "function": {
                                        "name": "exec_command",
                                        "arguments": "",
                                    },
                                },
                            ),
                        },
                    },
                ),
            }
        )
        frame_2a = chat_sse(
            {
                "id": "chatcmpl-sse",
                "object": "chat.completion.chunk",
                "choices": (
                    {
                        "index": 0,
                        "delta": {
                            "tool_calls": (
                                {
                                    "index": 0,
                                    "function": {"arguments": args[:7]},
                                },
                            ),
                        },
                    },
                ),
            }
        )
        frame_2b = chat_sse(
            {
                "id": "chatcmpl-sse",
                "object": "chat.completion.chunk",
                "choices": (
                    {
                        "index": 0,
                        "delta": {
                            "tool_calls": (
                                {
                                    "index": 0,
                                    "function": {"arguments": args[7:]},
                                },
                            ),
                        },
                    },
                ),
            }
        )
        frame_done = chat_sse(
            {
                "id": "chatcmpl-sse",
                "object": "chat.completion.chunk",
                "choices": ({"index": 0, "delta": {}, "finish_reason": "stop"},),
            }
        )
        full_stream = frame_1 + frame_2a + frame_2b + frame_done + b"data: [DONE]\n\n"
        split_at = len(frame_1) + len(frame_2a) // 2  # mid-frame

        class XStream(httpx.AsyncByteStream):
            async def __aiter__(self) -> AsyncIterator[bytes]:
                yield full_stream[:split_at]
                yield full_stream[split_at:]

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                if request.headers["authorization"] == "Bearer test-only-compiler":
                    return compiler_echo(request)
                captured_main.append(request)
                return httpx.Response(
                    200, headers={"content-type": "text/event-stream"}, stream=XStream()
                )
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            return httpx.Response(200, json={"id": "resp-r1"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            # Round one (Responses): the bootstrap (no issuance).
            response1 = await client.post(
                "/v1/responses",
                json={"model": "qwen38-27b", "input": [root_item(root_body)]},
            )
            assert response1.status_code == 200
            assert len(captured_compile) == 1  # the admitted root entry
            session = self._session(app, settings)
            assert session is not None
            assert session.owner.revision == 1
            # Round two (Chat stream): the ordinary hit over the
            # user root text; the direct split SSE issues fc-c1.
            response2 = await client.post(
                "/v1/chat/completions",
                json={
                    "model": "qwen38-27b",
                    "messages": [{"role": "user", "content": root_text}],
                    "stream": True,
                },
            )
            assert response2.status_code == 200
            # The actual SSE passes through byte-identical.
            assert response2.content == full_stream
            round2_body = captured_main[1].content
            # The Chat user message is NOT a root carrier (root
            # authority is Responses-only): its text stays data; the
            # stable system placement carries the root block only.
            out2 = json.loads(round2_body)
            assert out2["messages"][0]["role"] == "system"
            assert out2["messages"][0]["content"].count("<slaif-compiled-block") == 1
            assert out2["messages"][1] == {"role": "user", "content": root_text}
            assert round2_body.count(b"[slaif-live:v") == 0
            assert len(captured_compile) == 1  # RAM hit: no recompile
            # The issuance committed under the FROZEN root-only
            # frontier.
            assert session.owner.revision == 2
            snapshot = session.owner.snapshot
            assert snapshot is not None
            d = snapshot.state.d_state
            issuances = {i.call_id: i for i in d.issuances}
            assert set(issuances) == {"fc-c1"}
            assert issuances["fc-c1"].parent_frontier == (CAUSAL_ROOT_FACT,)
            # Round three (Chat): the receipt pairs the retained
            # issuance: the read is ACQUIRED (anchored under the
            # frozen frontier), the tool carrier edited, the region
            # extended to both blocks.
            chat3 = {
                "model": "qwen38-27b",
                "messages": self._chat_read_messages(root_text, "fc-c1", "cat c1.md", "X1 body.\n"),
            }
            response3 = await client.post("/v1/chat/completions", json=chat3)
            assert response3.status_code == 200
            out3 = json.loads(captured_main[2].content)
            assert out3["messages"][0]["content"].count("<slaif-compiled-block") == 2
            assert out3["messages"][3]["role"] == "tool"
            assert "[slaif-live:v" in out3["messages"][3]["content"]
            body3 = captured_main[2].content
            assert body3.count(b"[slaif-live:v") == 1
            assert b"X1 body." not in body3
            assert len(captured_compile) == 2  # + the c1 read entry
            session = self._session(app, settings)
            assert session is not None
            snapshot = session.owner.snapshot
            assert snapshot is not None
            d = snapshot.state.d_state
            occ = {o.call_id: o for o in d.occurrences}["fc-c1"]
            assert occ.anchored is True
            links = {(link.child, link.parent) for link in d.parent_links}
            assert (occ.occurrence_id, CAUSAL_ROOT_FACT) in links
            assert occ.anchored is True
            links = {(link.child, link.parent) for link in d.parent_links}
            assert (occ.occurrence_id, CAUSAL_ROOT_FACT) in links

    async def test_reduced_history_reinjects_source_absent_working_set(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """R01/R04/R05 at the app boundary: after the fixed point,
        the REDUCED client history (the root envelope plus the bare
        exec call, NO result) carries no read carrier; the ordinary
        RAM reuse edits the root carrier from the retained state,
        reinjects the COMPLETE source-absent compiled working set
        (both rendered blocks) at the Responses stable placement,
        and recompiles nothing (no recompile for selection alone)."""
        settings = self._setup(monkeypatch, tmp_path)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)
        root_body = "Follow `c1.md` before acting.\n"

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo(request)
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            return httpx.Response(200, json={"id": f"resp-r{len(captured_main)}"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        round1_payload = {
            "model": "qwen38-27b",
            "input": [
                root_item(root_body),
                exec_call("c1", "cat c1.md"),
                out_item("c1", frame("A body.\n")),
            ],
        }
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            # Round one: the read is acquired (root + c1).
            response1 = await client.post("/v1/responses", json=round1_payload)
            assert response1.status_code == 200
            round1_body = captured_main[0].content
            assert round1_body.count(b"[slaif-live:v") == 2
            assert b"A body." not in round1_body
            assert len(captured_compile) == 2
            # Round two: the resend fixed point (RAM hit).
            response2 = await client.post(
                "/v1/responses",
                content=round1_body,
                headers={"content-type": "application/json"},
            )
            assert response2.status_code == 200
            assert captured_main[1].content == round1_body
            assert len(captured_compile) == 2
            # Round three: the REDUCED history (root + bare call).
            reduced = {
                "model": "qwen38-27b",
                "input": [root_item(root_body), exec_call("c1", "cat c1.md")],
            }
            response3 = await client.post("/v1/responses", json=reduced)
            assert response3.status_code == 200
            out3 = json.loads(captured_main[2].content)
            # The root carrier is edited from the retained state.
            assert captured_main[2].content.count(b"[slaif-live:v") == 1
            assert root_body not in captured_main[2].content.decode()
            # The source-absent working set is reinjected: BOTH
            # rendered blocks at the stable Responses placement,
            # without the original source from the client.
            instructions = out3["instructions"]
            assert instructions.startswith("[slaif-compiled-context:v1]\n")
            assert instructions.endswith("[/slaif-compiled-context:v1]")
            assert instructions.count("<slaif-compiled-block") == 2
            assert b"A body." not in captured_main[2].content
            # No recompile for selection alone.
            assert len(captured_compile) == 2

    async def test_source_change_stale_replay_and_revert(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """C04/C05/R03 at the app boundary: the model-ISSUED re-read of
        the same path at new bytes (the direct response's function_call
        is the causality edge that proves the later version -- a
        same-batch read carries no anchor and is the fixed content-
        conflict refusal) recompiles and marks the NEW carrier live
        while the positively superseded old ORIGINAL's carrier (the
        retained D occurrence re-presented raw by the client) earns the
        non-resolving evidence marker without rebuilding the old entry
        key; resending the OLD transformed body (its now-stale live
        marker) is the fixed 409 with no forward; a further issued
        re-read carrying the ORIGINAL bytes is the deliberate revert --
        no recompile (the retained historical payload is reused) and
        the v1 carriers are live again while the v2 carrier is the
        superseded evidence."""
        settings = self._setup(monkeypatch, tmp_path)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)
        root_body = "Follow `c1.md` before acting.\n"

        def resp_issue(cid: str) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "id": f"resp-{cid}",
                    "status": "completed",
                    "output": (
                        {
                            "type": "function_call",
                            "id": f"fc-{cid}",
                            "call_id": cid,
                            "name": "exec_command",
                            "arguments": json.dumps({"cmd": "cat c1.md"}),
                        },
                    ),
                },
            )

        def resp_plain(n: int) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "id": f"resp-r{n}",
                    "status": "completed",
                    "output": (
                        {
                            "type": "message",
                            "content": [{"type": "output_text", "text": "ok"}],
                        },
                    ),
                },
            )

        issue_at = {1: "c2", 2: "c3"}

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo(request)
            assert request.url.path == "/v1/responses"
            n = len(captured_main) + 1
            captured_main.append(request)
            return resp_issue(issue_at[n]) if n in issue_at else resp_plain(n)

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        runtime = app.state.v1_runtime
        assert runtime is not None
        identity = RequestIdentity(
            principal="local-principal",
            session="local-session",
            repository="local-repository",
            route="text",
        )
        address = build_session_address(
            runtime, identity, settings.routes[0], settings.context_cache.route_contracts["text"]
        )

        def carrier_marks(body: bytes) -> dict[str, tuple[str, ...]]:
            """The actual marker kinds on each function_call_output's
            output text, keyed by call_id (the carrier-level view)."""
            marks: dict[str, tuple[str, ...]] = {}
            for item in json.loads(body)["input"]:
                if item.get("type") != "function_call_output":
                    continue
                text = item.get("output", "")
                found = tuple(
                    kind
                    for kind, prefix in (
                        ("LIVE", "[slaif-live:v"),
                        ("EVIDENCE", "[slaif-evidence:v"),
                    )
                    if prefix in text
                )
                marks[str(item.get("call_id"))] = found
            return marks

        base = [
            root_item(root_body),
            exec_call("c1", "cat c1.md"),
            out_item("c1", frame("A body.\n")),
        ]
        v2_pair = [
            exec_call("c2", "cat c1.md"),
            out_item("c2", frame("A body v2.\n")),
        ]
        v1_pair = [
            exec_call("c3", "cat c1.md"),
            out_item("c3", frame("A body.\n")),
        ]
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            # Round one: the read is acquired (root + c1); the direct
            # response issues the re-read c2 (the causality edge).
            response1 = await client.post(
                "/v1/responses", json={"model": "qwen38-27b", "input": list(base)}
            )
            assert response1.status_code == 200
            round1_body = captured_main[0].content
            assert round1_body.count(b"[slaif-live:v") == 2
            assert round1_body.count(b"[slaif-evidence:v") == 0
            assert len(captured_compile) == 2
            session = app.state.v1_sessions.get(address)
            assert session is not None
            d_state = session.owner.snapshot.state.d_state
            c1_occurrence = d_state.occurrences[0].occurrence_id
            c2_issuance = {i.call_id: i for i in d_state.issuances}["c2"]
            assert set(c2_issuance.parent_frontier) == {c1_occurrence, CAUSAL_ROOT_FACT}
            # Round two: the issued re-read completes at the NEW
            # bytes: the new carrier is live; the positively
            # superseded old original's carrier is the non-resolving
            # evidence marker (the old entry key is never rebuilt);
            # the direct response issues c3.
            response2 = await client.post(
                "/v1/responses",
                json={"model": "qwen38-27b", "input": list(base) + v2_pair},
            )
            assert response2.status_code == 200
            round2_body = captured_main[1].content
            assert round2_body.count(b"[slaif-live:v") == 2
            assert round2_body.count(b"[slaif-evidence:v") == 1
            marks2 = carrier_marks(round2_body)
            assert marks2["c1"] == ("EVIDENCE",)
            assert marks2["c2"] == ("LIVE",)
            assert b"A body." not in round2_body
            assert b"A body v2." not in round2_body
            assert len(captured_compile) == 3  # + the v2 entry
            # Round three: resending the OLD transformed body (its
            # c1 live marker is now stale over the superseded
            # occurrence) is the fixed 409 with no forward.
            response3 = await client.post(
                "/v1/responses",
                content=round1_body,
                headers={"content-type": "application/json"},
            )
            assert response3.status_code == 409
            assert response3.json()["error"]["code"] == "v1_transaction_conflict"
            assert len(captured_main) == 2
            # Round four: the deliberate revert (the issued re-read
            # c3 carrying the ORIGINAL v1 bytes): no recompile (the
            # retained historical payload is reused), the v1 carriers
            # are live again, the v2 carrier is the superseded
            # evidence.
            response4 = await client.post(
                "/v1/responses",
                json={"model": "qwen38-27b", "input": list(base) + v2_pair + v1_pair},
            )
            assert response4.status_code == 200
            round4_body = captured_main[2].content
            assert round4_body.count(b"[slaif-live:v") == 3
            assert round4_body.count(b"[slaif-evidence:v") == 1
            marks4 = carrier_marks(round4_body)
            assert marks4["c1"] == ("LIVE",)
            assert marks4["c2"] == ("EVIDENCE",)
            assert marks4["c3"] == ("LIVE",)
            assert b"A body." not in round4_body
            assert b"A body v2." not in round4_body
            # The retained historical v1 payload is reused: NO
            # recompile.
            assert len(captured_compile) == 3

    async def test_compiler_failure_refuses_then_heals(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The typed compiler-failure family at the app boundary: an
        invalid compiler completion is never an entry -- the
        governed transaction is the fixed 503 with zero main forward
        and exactly ONE compile attempt (the terminal work-plane
        failure is re-served to the same-epoch repeat with the SAME
        typed refusal and no retry loophole); the bootstrap remains
        committed at generation one with its bound; and the restart
        -- a fresh process over the SAME recovery root, resuming the
        durable generation in a distinct epoch whose work plane
        carries no terminal -- completes the SAME request with
        exactly one successful compile, after which the fixed point
        holds."""
        settings = self._setup(monkeypatch, tmp_path)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)
        compile_calls = {"n": 0}

        def compiler(request: httpx.Request) -> httpx.Response:
            compile_calls["n"] += 1
            if compile_calls["n"] == 1:
                # The synthetic invalid completion (no valid
                # compiled index content).
                captured_compile.append(request)
                return httpx.Response(200, content=_completion_bytes("{invalid compiled index"))
            return compiler_echo(request)

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler(request)
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            return httpx.Response(200, json={"id": f"resp-r{len(captured_main)}"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        root_payload = {
            "model": "qwen38-27b",
            "input": [root_item("Follow the workspace protocol.\n")],
        }
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            response1 = await client.post("/v1/responses", json=root_payload)
            assert response1.status_code == 503
            error1 = response1.json()["error"]
            assert error1["code"] == "v1_compiler_refused"
            assert error1["message"] == "governed v1 request refused"
            assert len(captured_main) == 0  # zero main forward
            assert len(captured_compile) == 1  # the invalid attempt
            # The bootstrap is committed (generation one) but the
            # invalid result is never an entry.
            session = self._session(app, settings)
            assert session is not None
            assert session.last_publish is not None
            assert session.last_publish.generation == 1
            assert session.last_publish_bound == (1, 1)
            # The same-epoch repeat: the terminal failure is
            # re-served with the SAME typed refusal and no new
            # invocation (no retry loophole).
            response2 = await client.post("/v1/responses", json=root_payload)
            assert response2.status_code == 503
            assert response2.json()["error"]["code"] == "v1_compiler_refused"
            assert len(captured_main) == 0
            assert len(captured_compile) == 1
        # Process exit: the composed teardown releases the exclusive
        # writer so the restart can own the session.
        async with app.router.lifespan_context(app):
            pass
        # The restart: a fresh process over the SAME recovery root
        # (the durable generation resumes in a distinct epoch whose
        # work plane carries no terminal).
        settings_b = self._setup(monkeypatch, tmp_path)
        captured_main_b: list[httpx.Request] = []
        captured_compile_b: list[httpx.Request] = []
        compiler_echo_b = _echo_compiler_handler(captured_compile_b)

        def handler_b(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo_b(request)
            assert request.url.path == "/v1/responses"
            captured_main_b.append(request)
            return httpx.Response(200, json={"id": f"resp-r{len(captured_main_b)}"})

        app_b = create_app(settings_b, httpx.MockTransport(handler_b))
        assert app_b.state.v1_runtime is not None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app_b), base_url="http://adapter.test"
        ) as client:
            response3 = await client.post("/v1/responses", json=root_payload)
            assert response3.status_code == 200
            round3_body = captured_main_b[0].content
            assert round3_body.count(b"[slaif-live:v") == 1
            assert b"Follow the workspace protocol." not in round3_body
            assert len(captured_compile_b) == 1  # exactly one SUCCESSFUL compile
            session_b = self._session(app_b, settings_b)
            assert session_b is not None
            assert session_b.last_publish is not None
            # The resumed owner materializes its restored record
            # set's generation in the distinct live epoch.
            assert session_b.last_publish.generation == 3
            assert session_b.last_publish_bound == (1, 2)
            # The fixed point (RAM hit, no recompile).
            response4 = await client.post(
                "/v1/responses",
                content=round3_body,
                headers={"content-type": "application/json"},
            )
            assert response4.status_code == 200
            assert captured_main_b[1].content == round3_body
            assert len(captured_compile_b) == 1

    async def test_budget_overflow_refuses_then_heals(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The typed budget-allowance family at the app boundary: a
        VALID compiler index whose rendered block exceeds the
        entry's width x slot allowance is typed BEFORE retention
        (the allowance fence -- no truncation, no partial form is
        ever injected, retained or forwarded) -- the fixed 503 with
        zero main forward and exactly ONE compile attempt; the
        terminal failure is re-served to the same-epoch repeat with
        the SAME typed refusal; and the restart (a fresh process
        over the SAME recovery root) completes the SAME request with
        an in-allowance compile, after which the fixed point holds
        and the oversized statement never reached the model."""
        settings = self._setup(monkeypatch, tmp_path)
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compile_calls = {"n": 0}

        def oversized_rules() -> tuple[BundleCompiledRule, ...]:
            return tuple(
                BundleCompiledRule(
                    rule_id=f"v1-big-rule-{i}",
                    strength="must",
                    statement="Bounded synthetic overflow statement rule text. " * 11,
                    location="",
                    evidence="Overflow evidence.",
                )
                for i in range(10)
            )

        def compiler(request: httpx.Request) -> httpx.Response:
            compile_calls["n"] += 1
            captured_compile.append(request)
            body = json.loads(request.content)
            index = _index_for_demand(body["messages"][1]["content"], body["model"])
            if compile_calls["n"] == 1:
                # A model-valid index that crosses the entry's
                # rendered allowance (width one x slot).
                index = index.model_copy(update={"rules": oversized_rules()})
            return httpx.Response(
                200, content=_completion_bytes(serialize_compiled_index(index).decode("utf-8"))
            )

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler(request)
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            return httpx.Response(200, json={"id": f"resp-r{len(captured_main)}"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        root_payload = {
            "model": "qwen38-27b",
            "input": [root_item("Follow the workspace protocol.\n")],
        }
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            response1 = await client.post("/v1/responses", json=root_payload)
            assert response1.status_code == 503
            error1 = response1.json()["error"]
            assert error1["code"] == "v1_compiler_refused"
            assert error1["message"] == "governed v1 request refused"
            assert len(captured_main) == 0  # zero main forward
            assert len(captured_compile) == 1  # the over-allowance attempt
            session = self._session(app, settings)
            assert session is not None
            assert session.last_publish is not None
            assert session.last_publish.generation == 1
            assert session.last_publish_bound == (1, 1)
            # The same-epoch repeat: re-served with the SAME typed
            # refusal and no new invocation.
            response2 = await client.post("/v1/responses", json=root_payload)
            assert response2.status_code == 503
            assert response2.json()["error"]["code"] == "v1_compiler_refused"
            assert len(captured_main) == 0
            assert len(captured_compile) == 1
        # Process exit: the composed teardown releases the exclusive
        # writer so the restart can own the session.
        async with app.router.lifespan_context(app):
            pass
        # The restart: a fresh process over the SAME recovery root.
        settings_b = self._setup(monkeypatch, tmp_path)
        captured_main_b: list[httpx.Request] = []
        captured_compile_b: list[httpx.Request] = []
        compile_calls_b = {"n": 0}

        def compiler_b(request: httpx.Request) -> httpx.Response:
            # The in-allowance compiler output for every restart
            # compile.
            compile_calls_b["n"] += 1
            captured_compile_b.append(request)
            body = json.loads(request.content)
            index = _index_for_demand(body["messages"][1]["content"], body["model"])
            return httpx.Response(
                200, content=_completion_bytes(serialize_compiled_index(index).decode("utf-8"))
            )

        def handler_b(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_b(request)
            assert request.url.path == "/v1/responses"
            captured_main_b.append(request)
            return httpx.Response(200, json={"id": f"resp-r{len(captured_main_b)}"})

        app_b = create_app(settings_b, httpx.MockTransport(handler_b))
        assert app_b.state.v1_runtime is not None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app_b), base_url="http://adapter.test"
        ) as client:
            response3 = await client.post("/v1/responses", json=root_payload)
            assert response3.status_code == 200
            round3_body = captured_main_b[0].content
            assert round3_body.count(b"[slaif-live:v") == 1
            assert b"Follow the workspace protocol." not in round3_body
            # The oversized statement never reached the model (no
            # truncated or partial form is ever forwarded).
            assert b"Overflow evidence." not in round3_body
            assert b"Bounded synthetic overflow statement rule text." not in round3_body
            assert len(captured_compile_b) == 1
            session_b = self._session(app_b, settings_b)
            assert session_b is not None
            assert session_b.last_publish is not None
            assert session_b.last_publish.generation == 3
            assert session_b.last_publish_bound == (1, 2)
            # The fixed point (RAM hit, no recompile).
            response4 = await client.post(
                "/v1/responses",
                content=round3_body,
                headers={"content-type": "application/json"},
            )
            assert response4.status_code == 200
            assert captured_main_b[1].content == round3_body
            assert len(captured_compile_b) == 1

    async def test_v1_stream_disconnect_closes_upstream(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The S02 cancellation contract on a v1-governed streaming
        request: the cold bootstrap commits before the stream; the
        client disconnect after the first forwarded chunk cancels
        the owned upstream work (the upstream stream is closed)."""
        settings = self._setup(monkeypatch, tmp_path)
        first_sent = asyncio.Event()
        release_never = asyncio.Event()

        class Stream(httpx.AsyncByteStream):
            closed = False

            async def __aiter__(self) -> AsyncIterator[bytes]:
                yield b"data: one\n\n"
                await release_never.wait()

            async def aclose(self) -> None:
                self.closed = True

        stream = Stream()
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo(request)
            assert request.url.path == "/v1/responses"
            return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=stream)

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        body = json.dumps(
            {
                "model": "qwen38-27b",
                "input": [root_item("Follow the workspace protocol.\n")],
                "stream": True,
            },
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode()
        received = False

        async def receive() -> dict[str, Any]:
            nonlocal received
            if not received:
                received = True
                return {"type": "http.request", "body": body, "more_body": False}
            await first_sent.wait()
            return {"type": "http.disconnect"}

        async def send(message: MutableMapping[str, Any]) -> None:
            if message["type"] == "http.response.body" and message.get("body"):
                first_sent.set()

        scope: dict[str, Any] = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/v1/responses",
            "raw_path": b"/v1/responses",
            "query_string": b"",
            "headers": [(b"content-type", b"application/json")],
            "client": ("127.0.0.1", 1),
            "server": ("127.0.0.1", 18031),
        }
        await app(scope, receive, send)
        assert first_sent.is_set()
        assert stream.closed

    async def test_ungoverned_route_forwards_unchanged(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The S02 route protection: a second route whose model
        carries NO explicit route contract is never a governed v1
        route -- its root-bearing payload crosses the wire
        byte-identical with no session, no compile and no v1
        component touched, while the governed route's contract law
        stays exact (the contract set equals the governed set)."""
        settings = self._setup(monkeypatch, tmp_path, extra_ungoverned_route=True)
        # The contract law: exactly the governed routes carry
        # contracts.
        assert set(settings.context_cache.route_contracts) == {"text"}
        captured_main: list[httpx.Request] = []
        captured_compile: list[httpx.Request] = []
        compiler_echo = _echo_compiler_handler(captured_compile)

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/chat/completions":
                return compiler_echo(request)
            assert request.url.path == "/v1/responses"
            captured_main.append(request)
            return httpx.Response(200, json={"id": "resp-plain"})

        app = create_app(settings, httpx.MockTransport(handler))
        assert app.state.v1_runtime is not None
        root_payload = {
            "model": "other-model",
            "input": [root_item("Follow the workspace protocol.\n")],
        }
        sent = json.dumps(root_payload, separators=(",", ":"), ensure_ascii=True).encode()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
        ) as client:
            response = await client.post(
                "/v1/responses",
                content=sent,
                headers={"content-type": "application/json"},
            )
        assert response.status_code == 200
        assert len(captured_main) == 1
        # Byte-identical forward: the root envelope stays raw.
        assert captured_main[0].content == sent
        assert b"Follow the workspace protocol." in captured_main[0].content
        assert len(captured_compile) == 0
        assert self._session(app, settings) is None
