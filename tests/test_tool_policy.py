"""Route-scoped Responses tool-envelope compatibility tests."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Callable, Coroutine
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

import slaif_local_coding.app as app_module
from slaif_local_coding.app import create_app
from slaif_local_coding.config import (
    CacheConfig,
    CompilerConfig,
    ConstitutionIntegrationConfig,
    RouteConfig,
    ServerConfig,
    Settings,
    UpstreamConfig,
)
from slaif_local_coding.constitution.pipeline import ConstitutionPipeline
from slaif_local_coding.tool_policy import (
    DISABLED_CODEX_TOOL_TYPES,
    MAX_RESPONSES_TOOL_DECLARATIONS,
    RESPONSES_TOOL_POLICY_VERSION,
    ResponsesToolPolicyError,
    apply_responses_tool_policy,
)


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("TEST_TOOL_POLICY_KEY", "test-only-secret")
    return Settings(
        server=ServerConfig(request_body_max_bytes=20_000),
        upstream=UpstreamConfig(
            base_url="http://upstream.test/v1",
            api_key_env="TEST_TOOL_POLICY_KEY",
            model="qwen",
        ),
        routes=[
            RouteConfig(
                name="codex",
                model="qwen",
                max_images_per_request=1,
                image_overflow_policy="retain_newest",
                responses_tool_policy="drop_disabled_codex_search",
            )
        ],
    )


async def exchange(
    settings: Settings,
    payload: object,
    handler: Callable[[httpx.Request], Coroutine[None, None, httpx.Response]],
    *,
    endpoint: str = "/v1/responses",
    content: bytes | None = None,
) -> httpx.Response:
    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        if content is not None:
            return await client.post(
                endpoint, content=content, headers={"content-type": "application/json"}
            )
        return await client.post(endpoint, json=payload)


def tool_payload(tools: list[dict[str, Any]], **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": "qwen",
        "input": [
            {"type": "function_call", "call_id": "call-1", "name": "local", "arguments": "{}"},
            {"type": "function_call_output", "call_id": "call-1", "output": "synthetic-result"},
        ],
        "tools": tools,
    }
    payload.update(extra)
    return payload


@pytest.mark.parametrize(
    "types",
    [
        ("tool_search",),
        ("web_search",),
        ("tool_search", "web_search"),
        ("tool_search", "tool_search", "web_search", "tool_search"),
    ],
)
def test_pure_policy_removes_each_disabled_type_and_preserves_order(types: tuple[str, ...]) -> None:
    tools = [{"type": marker, "marker": index} for index, marker in enumerate(types)]
    tools.extend(
        [
            {"type": "function", "function": {"name": "local", "parameters": {}}},
            {"type": "custom", "name": "custom-local", "format": {"type": "text"}},
            {"type": "namespace", "namespace": {"name": "local"}},
        ]
    )
    payload = tool_payload(tools)
    result = apply_responses_tool_policy(payload, "drop_disabled_codex_search")
    assert result.observed_count == len(tools)
    assert result.removed_count == len(types)
    assert result.outcome == "transformed"
    assert [item["type"] for item in result.payload["tools"]] == [
        "function",
        "custom",
        "namespace",
    ]
    assert result.payload["input"] == payload["input"]
    assert payload["tools"] == tools


@pytest.mark.parametrize("choice", [None, "auto", "none"])
def test_only_disabled_tools_are_omitted_for_automatic_or_no_choice(
    choice: str | None,
) -> None:
    payload = tool_payload([{"type": "tool_search"}, {"type": "web_search"}])
    if choice is not None:
        payload["tool_choice"] = choice
    result = apply_responses_tool_policy(payload, "drop_disabled_codex_search")
    assert "tools" not in result.payload
    if choice is not None:
        assert result.payload["tool_choice"] == choice


@pytest.mark.parametrize(
    "choice",
    [
        "tool_search",
        "web_search",
        {"type": "tool_search"},
        {"type": "allowed_tools", "mode": "auto", "tools": [{"type": "web_search"}]},
    ],
)
def test_explicit_disabled_tool_choice_is_rejected(choice: object) -> None:
    payload = tool_payload([{"type": "tool_search"}, {"type": "web_search"}], tool_choice=choice)
    with pytest.raises(ResponsesToolPolicyError) as raised:
        apply_responses_tool_policy(payload, "drop_disabled_codex_search")
    assert raised.value.code == "responses_disabled_tool_choice"
    assert raised.value.reason == "explicit_disabled_tool_choice"


def test_only_disabled_tools_cannot_satisfy_required_choice() -> None:
    payload = tool_payload([{"type": "tool_search"}], tool_choice="required")
    with pytest.raises(ResponsesToolPolicyError) as raised:
        apply_responses_tool_policy(payload, "drop_disabled_codex_search")
    assert raised.value.reason == "required_tool_choice_after_removal"


def test_deep_tool_choice_fails_at_the_policy_bound() -> None:
    nested: object = {"mode": "auto"}
    for _ in range(513):
        nested = {"nested": nested}
    payload = tool_payload([{"type": "tool_search"}], tool_choice=nested)
    with pytest.raises(ResponsesToolPolicyError) as raised:
        apply_responses_tool_policy(payload, "drop_disabled_codex_search")
    assert raised.value.reason == "tool_choice_too_large"


def test_captured_codex_vector_is_content_free_and_consumed() -> None:
    vector_path = Path("tests/fixtures/gateway/responses_tool_filter_vectors.json")
    vector = json.loads(vector_path.read_text(encoding="utf-8"))
    existing = json.loads(
        Path("tests/fixtures/gateway/openai_compatible_vectors.json").read_text(encoding="utf-8")
    )
    assert existing["responses_tool_policy_vector"] == vector_path.name
    assert tuple(vector["observed_top_level_tool_types"]) == (
        "function",
        "custom",
        "tool_search",
        "web_search",
        "namespace",
    )
    assert set(vector["adapter_postcondition"]["drop_exact_types_before_qwen"]) == set(
        DISABLED_CODEX_TOOL_TYPES
    )
    assert vector["adapter_postcondition"]["policy_version"] == RESPONSES_TOOL_POLICY_VERSION
    assert vector["gateway_precondition"]["provider_hosted_web_search_execution_granted"] is False
    assert vector["accounting"]["public_request_reservation_and_ledger_rows"] == 1
    assert all(
        secret not in vector_path.read_text(encoding="utf-8")
        for secret in ("Authorization", "Bearer", "private-prompt", "private-query")
    )


@pytest.mark.asyncio
async def test_filter_preserves_function_custom_namespace_and_continuation(
    settings: Settings,
) -> None:
    payload = tool_payload(
        [
            {"type": "function", "function": {"name": "lookup", "parameters": {"type": "object"}}},
            {"type": "tool_search", "query": "private-search-query"},
            {"type": "custom", "name": "render", "format": {"type": "text"}},
            {"type": "web_search", "query": "private-web-query"},
            {"type": "namespace", "namespace": {"name": "local"}},
        ]
    )
    received: dict[str, Any] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        received.update(json.loads(await request.aread()))
        return httpx.Response(200, json={"id": "synthetic"})

    response = await exchange(settings, payload, handler)
    assert response.status_code == 200
    assert [item["type"] for item in received["tools"]] == ["function", "custom", "namespace"]
    assert received["tools"][0]["function"]["name"] == "lookup"
    assert received["tools"][1]["format"] == {"type": "text"}
    assert received["tools"][2]["namespace"] == {"name": "local"}
    assert received["input"] == payload["input"]
    assert "private-search-query" not in received
    assert "private-web-query" not in received


@pytest.mark.asyncio
async def test_rejection_happens_before_observation_compiler_cache_or_upstream(
    settings: Settings, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_TOOL_POLICY_COMPILER_KEY", "compiler-only-secret")
    route = settings.routes[0].model_copy(
        update={"observation_enabled": True, "constitution_enabled": True}
    )
    governed = Settings(
        server=settings.server,
        upstream=settings.upstream,
        routes=[route],
        compiler=CompilerConfig(
            enabled=True, api_key_env="TEST_TOOL_POLICY_COMPILER_KEY", max_attempts=1
        ),
        cache=CacheConfig(root=tmp_path / "cache", fallback_root=tmp_path / "fallback"),
        constitution=ConstitutionIntegrationConfig(
            enabled=True,
            principal="local-principal",
            session="local-session",
            repository="local-repository",
        ),
    )
    observed = MagicMock(side_effect=AssertionError("observation must not run"))
    process = AsyncMock(side_effect=AssertionError("compiler/cache pipeline must not run"))
    monkeypatch.setattr(app_module, "observe_request_for_pipeline", observed)
    monkeypatch.setattr(ConstitutionPipeline, "process", process)
    upstream_calls = 0

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal upstream_calls
        upstream_calls += 1
        return httpx.Response(200, json={})

    response = await exchange(
        governed,
        tool_payload([{"type": "tool_search"}], tool_choice={"type": "tool_search"}),
        handler,
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "responses_disabled_tool_choice"
    assert upstream_calls == 0
    observed.assert_not_called()
    process.assert_not_awaited()
    assert not list((tmp_path / "cache").rglob("*"))


@pytest.mark.asyncio
async def test_malformed_non_list_and_oversized_tools_fail_closed(
    settings: Settings,
) -> None:
    payloads: list[object] = [
        {"model": "qwen", "tools": {"type": "tool_search"}},
        tool_payload([{"type": "function"}, {}]),
        tool_payload([{"type": "tool_search"}] * (MAX_RESPONSES_TOOL_DECLARATIONS + 1)),
    ]
    upstream_calls = 0

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal upstream_calls
        upstream_calls += 1
        return httpx.Response(200, json={})

    for payload in payloads:
        response = await exchange(settings, payload, handler)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "responses_tool_policy_invalid"
    assert upstream_calls == 0


@pytest.mark.asyncio
async def test_passthrough_default_and_chat_are_byte_stable(
    settings: Settings,
) -> None:
    raw = (
        b'{"model":"qwen", "tools":[{"type":"tool_search",'
        b'"query":"private-query"}], "input":"synthetic"}'
    )
    received: list[tuple[str, bytes]] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        received.append((request.url.path, await request.aread()))
        return httpx.Response(200, json={})

    passthrough = settings.model_copy(
        update={
            "routes": [
                settings.routes[0].model_copy(
                    update={
                        "responses_tool_policy": "passthrough",
                        "max_images_per_request": None,
                        "image_overflow_policy": "passthrough",
                    }
                )
            ]
        }
    )
    response = await exchange(passthrough, {}, handler, content=raw)
    assert response.status_code == 200
    assert received[-1] == ("/v1/responses", raw)

    chat = await exchange(settings, {}, handler, endpoint="/v1/chat/completions", content=raw)
    assert chat.status_code == 200
    assert received[-1] == ("/v1/chat/completions", raw)


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True])
async def test_stream_and_nonstream_have_equivalent_filtered_request(
    settings: Settings, stream: bool
) -> None:
    events = [b"data: response.created\n\n", b"data: response.completed\n\n"]
    received: list[dict[str, Any]] = []

    class Stream(httpx.AsyncByteStream):
        async def __aiter__(self) -> AsyncIterator[bytes]:
            for event in events:
                yield event

    async def handler(request: httpx.Request) -> httpx.Response:
        received.append(json.loads(await request.aread()))
        if stream:
            return httpx.Response(
                200, headers={"content-type": "text/event-stream"}, stream=Stream()
            )
        return httpx.Response(200, json={"id": "synthetic"})

    response = await exchange(
        settings,
        tool_payload(
            [
                {"type": "function", "function": {"name": "local"}},
                {"type": "tool_search"},
                {"type": "web_search"},
            ],
            stream=stream,
        ),
        handler,
    )
    assert response.status_code == 200
    assert [item["type"] for item in received[0]["tools"]] == ["function"]
    if stream:
        assert response.content == b"".join(events)


@pytest.mark.asyncio
async def test_image_and_governance_items_survive_tool_filter_ordering(
    settings: Settings,
) -> None:
    source = (
        "# AGENTS.md instructions for repo\n\n<INSTRUCTIONS>\nMUST preserve this.\n</INSTRUCTIONS>"
    )
    payload = tool_payload(
        [{"type": "tool_search"}, {"type": "function", "function": {"name": "local"}}],
        input=[
            {"type": "input_image", "image_url": "old-image"},
            {"type": "input_file", "filename": "AGENTS.md", "content": source},
            {"type": "input_image", "image_url": "new-image"},
        ],
    )
    received: dict[str, Any] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        received.update(json.loads(await request.aread()))
        return httpx.Response(200, json={})

    response = await exchange(settings, payload, handler)
    assert response.status_code == 200
    assert [item["image_url"] for item in received["input"] if item["type"] == "input_image"] == [
        "new-image"
    ]
    input_file = next(item for item in received["input"] if item["type"] == "input_file")
    assert input_file["content"] == source
    assert [item["type"] for item in received["tools"]] == ["function"]


@pytest.mark.asyncio
async def test_metrics_are_fixed_and_do_not_contain_tool_content(settings: Settings) -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.post(
            "/v1/responses",
            json=tool_payload(
                [
                    {"type": "tool_search", "query": "private-query"},
                    {"type": "function", "function": {"name": "local"}},
                    {"type": "web_search", "query": "private-web-query"},
                ]
            ),
        )
        metrics = (await client.get("/metrics")).text
    assert response.status_code == 200
    assert 'route="codex"' in metrics
    assert 'outcome="transformed"' in metrics
    assert 'reason="disabled_codex_search_removed"' in metrics
    assert "private-query" not in metrics
    assert "private-web-query" not in metrics
    assert "tool_search" not in metrics
    assert "web_search" not in metrics
