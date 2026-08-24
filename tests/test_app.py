import asyncio
import gzip
import json
import logging
from collections.abc import AsyncIterator, Callable, Coroutine, MutableMapping
from pathlib import Path
from typing import Any

import httpx
import pytest

import slaif_local_coding.app as app_module
from slaif_local_coding.app import create_app
from slaif_local_coding.config import (
    CacheConfig,
    CompilerConfig,
    ConstitutionIntegrationConfig,
    GatewayIngressConfig,
    RouteConfig,
    ServerConfig,
    Settings,
    UpstreamConfig,
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
