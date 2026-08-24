"""Fake-upstream coverage for the objective-003-b one-root request pipeline."""

from __future__ import annotations

import hashlib
import json
from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest

from slaif_local_coding.app import create_app
from slaif_local_coding.config import (
    CacheConfig,
    CompilerConfig,
    ConstitutionIntegrationConfig,
    ObservationPolicy,
    RehydrationConfig,
    RouteConfig,
    ServerConfig,
    Settings,
    UpstreamConfig,
)
from slaif_local_coding.constitution.compiler_models import (
    AcquisitionUrgency,
    CompiledDependency,
    CompiledIndex,
    CompiledRule,
    ConstitutionalClass,
    RuleStrength,
)
from slaif_local_coding.constitution.references import extract_references

SOURCE = (
    b"# Synthetic governance fixture\n\n"
    b"The agent MUST read [PROCEDURE.md](PROCEDURE.md) before mutation.\n"
)
SOURCE_TEXT = SOURCE.decode()
PRIVATE_TOKEN = "unique-raw-source-token-9f2a"


def index() -> CompiledIndex:
    dependency = CompiledDependency(
        path="PROCEDURE.md",
        reference_confidence=0.9,
        constitutional_priority=80,
        classification=ConstitutionalClass.P1_DELEGATED_OR_SECURITY,
        relationship="delegated procedure",
        evidence="markdown reference",
        acquisition_urgency=AcquisitionUrgency.NEXT_TURN,
    )
    return CompiledIndex(
        schema_version="constitution-index-v1",
        compiler_version="compiler-v2",
        prompt_policy_version="constitutional-rank-v2",
        model="test-model",
        source_logical_path="AGENTS.md",
        source_sha256=hashlib.sha256(SOURCE).hexdigest(),
        source_byte_length=len(SOURCE),
        summary="Bounded synthetic governance summary.",
        rules=(
            CompiledRule(
                rule_id="read-procedure",
                strength=RuleStrength.MUST,
                statement="Read the referenced procedure.",
                location="line 3",
                evidence="MUST sentence",
            ),
        ),
        roles=("coding agent",),
        authorities=("human",),
        source_of_truth_boundaries=("source files override this index",),
        ordering_constraints=(),
        exceptions=(),
        dependencies=(dependency,),
        reread_triggers=("source hash changes",),
    )


class SyntheticStream(httpx.AsyncByteStream):
    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield b"data: synthetic\n"
        yield b"data: [DONE]\n\n"


def compiler_response() -> httpx.Response:
    raw = json.dumps(index().model_dump(mode="json"), separators=(",", ":")).encode()
    return httpx.Response(
        200,
        json={
            "choices": [{"message": {"role": "assistant", "content": raw.decode()}}],
            "usage": {"total_tokens": 2},
        },
    )


def enabled_settings(
    tmp_path: Any, *, session: str = "local-session", rehydration_enabled: bool = True
) -> Settings:
    return Settings(
        server=ServerConfig(request_body_max_bytes=8192),
        upstream=UpstreamConfig(
            base_url="http://upstream.test/v1",
            api_key_env="TEST_PIPELINE_KEY",
            model="test-model",
        ),
        routes=[
            RouteConfig(
                name="constitution-route",
                model="test-model",
                max_images_per_request=1,
                image_overflow_policy="retain_newest",
                observation_enabled=True,
                constitution_enabled=True,
            )
        ],
        compiler=CompilerConfig(enabled=True, api_key_env="TEST_PIPELINE_KEY", max_attempts=1),
        cache=CacheConfig(
            root=tmp_path / f"cache-{session}",
            fallback_root=None,
            max_total_bytes=1024 * 1024,
            max_entry_bytes=256 * 1024,
            max_pinned_bytes=256 * 1024,
            max_entries=16,
            ttl_seconds=300,
            max_scan_entries=64,
        ),
        constitution=ConstitutionIntegrationConfig(
            enabled=True,
            principal="local-principal",
            session=session,
            repository="local-repository",
            rehydration=RehydrationConfig(enabled=rehydration_enabled),
        ),
    )


def agents_payload(**changes: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "model": "test-model",
        "input": [
            {
                "type": "input_file",
                "filename": "AGENTS.md",
                "content": SOURCE_TEXT,
            }
        ],
    }
    value.update(changes)
    return value


async def exchange(
    settings: Settings,
    state: dict[str, Any],
    payload: dict[str, Any],
    *,
    compile_result: httpx.Response | None = None,
) -> httpx.Response:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            state["compiler_calls"] += 1
            if compile_result is not None:
                return compile_result
            return compiler_response()
        assert request.url.path == "/v1/responses"
        state["proxy_bodies"].append(await request.aread())
        return httpx.Response(200, json={"id": "sanitized"})

    app = create_app(settings, httpx.MockTransport(handler))
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://adapter.test") as client:
        response = await client.post("/v1/responses", json=payload)
        state["metrics"] = (await client.get("/metrics")).text
    return response


@pytest.mark.asyncio
async def test_disabled_and_spoofed_headers_preserve_exact_request(tmp_path: Any) -> None:
    from pytest import MonkeyPatch

    monkeypatch = MonkeyPatch()
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path)
    settings.constitution = settings.constitution.model_copy(update={"enabled": False})
    raw = json.dumps(agents_payload(), separators=(",", ":")).encode()
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            state["compiler_calls"] += 1
            raise AssertionError("disabled route must not compile")
        state["proxy_bodies"].append(await request.aread())
        return httpx.Response(200, json={})

    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.post(
            "/v1/responses",
            content=raw,
            headers={"x-slaif-principal": "spoof", "x-slaif-session": "spoof"},
        )
    assert response.status_code == 200
    assert state["proxy_bodies"] == [raw]
    assert state["compiler_calls"] == 0


@pytest.mark.asyncio
async def test_one_root_responses_injects_then_uses_persistent_cache_hit(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path)
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    first = await exchange(settings, state, agents_payload())
    second = await exchange(settings, state, agents_payload())

    assert first.status_code == second.status_code == 200
    assert state["compiler_calls"] == 1
    assert len(state["proxy_bodies"]) == 2
    first_value = json.loads(state["proxy_bodies"][0])
    second_value = json.loads(state["proxy_bodies"][1])
    assert first_value["instructions"] == second_value["instructions"]
    assert first_value["instructions"].startswith("<SLAIF_RECONSTRUCTED_CONSTITUTION ")
    assert "Acquire PROCEDURE.md" in first_value["instructions"]
    assert first_value["model"] == "test-model"

    values = state["metrics"]
    assert 'state="injected"' in values
    assert "slaif_constitution_cache_hits_total 1.0" in values
    assert PRIVATE_TOKEN not in values and SOURCE_TEXT not in values
    assert "local-principal" not in values and "local-repository" not in values


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [agents_payload(input="no root"), {"model": "test-model"}])
async def test_zero_roots_remain_byte_stable_without_compilation(
    tmp_path: Any, payload: dict[str, Any]
) -> None:
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path)
    raw = json.dumps(payload, separators=(",", ":")).encode()
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    response = await exchange(settings, state, payload)
    assert response.status_code == 200
    assert state["compiler_calls"] == 0
    assert state["proxy_bodies"] == [raw]


@pytest.mark.asyncio
async def test_multiple_roots_degrade_without_compilation(tmp_path: Any) -> None:
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    payload = agents_payload()
    second_root = payload["input"][0].copy()
    second_root["content"] = SOURCE_TEXT + "\nDistinct root content.\n"
    payload["input"].append(second_root)
    raw = json.dumps(payload, separators=(",", ":")).encode()
    settings = enabled_settings(tmp_path)
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    response = await exchange(settings, state, payload)

    assert response.status_code == 200
    assert state["compiler_calls"] == 0
    assert state["proxy_bodies"] == [raw]
    values = state["metrics"]
    assert 'reason="ambiguous_root"' in values


@pytest.mark.asyncio
async def test_compiler_failure_forwards_original_governance_request(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    payload = agents_payload()
    raw = json.dumps(payload, separators=(",", ":")).encode()
    settings = enabled_settings(tmp_path)
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    failure = httpx.Response(503, json={"error": "sanitized"})
    response = await exchange(settings, state, payload, compile_result=failure)

    assert response.status_code == 200
    assert state["compiler_calls"] == 1
    assert state["proxy_bodies"] == [raw]
    values = state["metrics"]
    assert 'reason="compiler_upstream_status"' in values


@pytest.mark.asyncio
async def test_readiness_reports_disposable_cache_degradation(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    base_settings = enabled_settings(tmp_path)
    settings = base_settings.model_copy(
        update={
            "cache": base_settings.cache.model_copy(
                update={"root": tmp_path / "missing-parent" / "cache", "fallback_root": None}
            )
        }
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/health"
        return httpx.Response(200, json={})

    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "config": "valid",
        "upstream": "ready",
        "gateway_ingress": "disabled",
        "compiler": "ready",
        "cache": "unavailable",
    }


@pytest.mark.asyncio
async def test_image_policy_tools_and_stream_choice_are_preserved(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    payload = agents_payload(
        stream=True,
        tools=[{"type": "function", "name": "synthetic"}],
        input=[
            {"type": "input_image", "image_url": "older-image"},
            {
                "type": "input_file",
                "filename": "AGENTS.md",
                "content": SOURCE_TEXT,
            },
            {"type": "input_image", "image_url": "newest-image"},
        ],
    )
    seen: dict[str, Any] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            return compiler_response()
        seen["body"] = json.loads(await request.aread())
        return httpx.Response(200, stream=SyntheticStream())

    app = create_app(enabled_settings(tmp_path), httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.post("/v1/responses", json=payload)

    assert response.status_code == 200
    assert response.text == "data: synthetic\ndata: [DONE]\n\n"
    body = seen["body"]
    images = [item["image_url"] for item in body["input"] if item.get("type") == "input_image"]
    assert images == ["newest-image"]
    assert body["tools"] == [{"type": "function", "name": "synthetic"}]
    assert body["stream"] is True
    assert "<SLAIF_RECONSTRUCTED_CONSTITUTION" in body["instructions"]


@pytest.mark.asyncio
async def test_conflicting_marker_fails_closed_after_cache_is_available(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path)
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    primed = await exchange(settings, state, agents_payload())
    assert primed.status_code == 200

    conflict = agents_payload()
    opening = '<SLAIF_RECONSTRUCTED_CONSTITUTION render_version="constitution-render-v1">'
    conflict["instructions"] = f"{opening}\ndifferent\n</SLAIF_RECONSTRUCTED_CONSTITUTION>"
    proxy_calls = len(state["proxy_bodies"])
    rejected = await exchange(settings, state, conflict)

    assert rejected.status_code == 422
    assert rejected.json()["error"]["code"] == "constitution_conflicting_marker"
    assert len(state["proxy_bodies"]) == proxy_calls
    values = state["metrics"]
    assert 'reason="conflicting_marker"' in values


@pytest.mark.asyncio
async def test_different_static_session_does_not_cross_hit(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    await exchange(enabled_settings(tmp_path, session="session-one"), state, agents_payload())
    await exchange(enabled_settings(tmp_path, session="session-two"), state, agents_payload())
    assert state["compiler_calls"] == 2


def test_candidate_extraction_supplies_complete_deterministic_paths() -> None:
    candidates = extract_references(SOURCE_TEXT, ObservationPolicy())
    assert [candidate.path for candidate in candidates.candidates] == ["PROCEDURE.md"]
