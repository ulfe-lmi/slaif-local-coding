import json
import logging
from collections.abc import AsyncIterator, Callable, Coroutine, MutableMapping
from typing import Any

import httpx
import pytest

from slaif_local_coding.app import create_app
from slaif_local_coding.config import RouteConfig, ServerConfig, Settings, UpstreamConfig


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


@pytest.mark.asyncio
async def test_health_models_auth_and_header_filter(settings: Settings) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer test-only-secret"
        assert "upgrade" not in request.headers
        assert "x-slaif-principal" not in request.headers
        return httpx.Response(
            200,
            headers={"content-type": "application/json", "connection": "close", "x-secret": "no"},
            json={"data": [{"id": "qwen"}]},
        )

    response = await call(
        settings,
        handler,
        "GET",
        "/v1/models",
        headers={
            "authorization": "Bearer attacker",
            "upgrade": "attacker-protocol",
            "x-slaif-principal": "spoof",
        },
    )
    assert response.status_code == 200 and response.json()["data"][0]["id"] == "qwen"
    assert "x-secret" not in response.headers


@pytest.mark.asyncio
async def test_nonstream_tool_usage_and_error_fidelity(settings: Settings) -> None:
    expected = {
        "choices": [{"message": {"tool_calls": [{"function": {"name": "f", "arguments": "{}"}}]}}],
        "usage": {"total_tokens": 3},
    }

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, headers={"content-type": "application/json"}, json=expected)

    response = await call(
        settings,
        handler,
        "POST",
        "/v1/chat/completions",
        json={"model": "qwen", "messages": [], "tools": [{"type": "function"}]},
    )
    assert response.status_code == 429 and response.json() == expected


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
async def test_client_disconnect_closes_upstream(settings: Settings) -> None:
    class Stream(httpx.AsyncByteStream):
        closed = False

        async def __aiter__(self) -> AsyncIterator[bytes]:
            yield b"data: one\n\n"
            yield b"data: two\n\n"

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
        return {"type": "http.disconnect"}

    async def send(_message: MutableMapping[str, Any]) -> None:
        return None

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
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        await client.post("/v1/responses", json={"model": "qwen", "input": "private marker"})
        metrics = (await client.get("/metrics")).text
    assert "private marker" not in metrics and 'route="vision"' in metrics
