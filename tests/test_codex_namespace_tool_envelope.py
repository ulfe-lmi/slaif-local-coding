"""Full-application fake-upstream regression for the Codex 0.149.0
namespace-tool envelope (order 014-a, workstream B).

The representative sanitized envelope from
``tests/fixtures/codex/0.149.0/namespace_tool_responses.json`` must reach the
disposable upstream without corruption under the route configurations that
correspond to the real-Codex VISION, CACHE, and BOTH arms. These are
full-application tests through ``/v1/responses`` (route selection, image
policy, observation, constitution, injection, and forwarding), not helper-only
shortcuts. The deterministic fake compiler answer mirrors the objective-003
pipeline tests.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import httpx
import pytest

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
from slaif_local_coding.constitution.compiler_models import (
    AcquisitionUrgency,
    CompiledDependency,
    CompiledIndex,
    CompiledRule,
    ConstitutionalClass,
    RuleStrength,
)

MODEL = "synthetic-namespace-model"
SOURCE = (
    b"# Synthetic governance fixture\n\n"
    b"The agent MUST read [PROCEDURE.md](PROCEDURE.md) before mutation.\n"
)
FIXTURE_PATH = (
    Path := __import__("pathlib").Path(__file__).parent
    / "fixtures"
    / "codex"
    / "0.149.0"
    / "namespace_tool_responses.json"
)


def namespace_fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def _index() -> CompiledIndex:
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
        compiler_version="compiler-v3",
        prompt_policy_version="constitutional-rank-v2",
        model=MODEL,
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


def _compiler_response() -> httpx.Response:
    raw = json.dumps(_index().model_dump(mode="json"), separators=(",", ":")).encode()
    return httpx.Response(
        200,
        json={
            "choices": [
                {
                    "message": {"role": "assistant", "content": raw.decode()},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"total_tokens": 2},
        },
    )


def _route(**overrides: Any) -> RouteConfig:
    base: dict[str, Any] = {
        "name": "namespace-route",
        "model": MODEL,
        "max_images_per_request": 1,
        "image_overflow_policy": "retain_newest",
    }
    base.update(overrides)
    return RouteConfig(**base)


def _settings(
    tmp_path: Any,
    *,
    route: RouteConfig,
    constitution: bool,
) -> Settings:
    return Settings(
        server=ServerConfig(request_body_max_bytes=16384),
        upstream=UpstreamConfig(
            base_url="http://upstream.test/v1",
            api_key_env="TEST_NAMESPACE_KEY",
            model=MODEL,
        ),
        routes=[route],
        compiler=(
            CompilerConfig(enabled=True, api_key_env="TEST_NAMESPACE_KEY", max_attempts=1)
            if constitution
            else CompilerConfig()
        ),
        cache=(
            CacheConfig(
                root=tmp_path / "cache",
                fallback_root=None,
                max_total_bytes=1024 * 1024,
                max_entry_bytes=256 * 1024,
                max_pinned_bytes=256 * 1024,
                max_entries=16,
                ttl_seconds=300,
                max_scan_entries=64,
            )
            if constitution
            else CacheConfig()
        ),
        constitution=(
            ConstitutionIntegrationConfig(
                enabled=True,
                principal="local-principal",
                session="local-session",
                repository="local-repository",
            )
            if constitution
            else ConstitutionIntegrationConfig()
        ),
    )


def _governed_input() -> list[dict[str, Any]]:
    return [
        {"role": "user", "content": [{"type": "input_text", "text": "t"}]},
        {"type": "input_file", "filename": "AGENTS.md", "content": SOURCE.decode()},
    ]


async def _post(
    settings: Settings,
    payload: dict[str, Any],
    state: dict[str, Any],
) -> httpx.Response:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            state["compiler_calls"] += 1
            return _compiler_response()
        assert request.url.path == "/v1/responses"
        state["proxy_bodies"].append(json.loads(await request.aread()))
        return httpx.Response(200, json={"id": "sanitized"})

    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        return await client.post("/v1/responses", json=payload)


@pytest.mark.asyncio
async def test_vision_arm_reaches_upstream_without_corruption(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_NAMESPACE_KEY", "test-only-secret")
    settings = _settings(tmp_path, route=_route(), constitution=False)
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    payload = namespace_fixture()
    response = await _post(settings, payload, state)

    assert response.status_code == 200
    assert state["compiler_calls"] == 0
    assert len(state["proxy_bodies"]) == 1
    body = state["proxy_bodies"][0]
    assert body == payload
    assert body["tools"] == payload["tools"]
    assert json.dumps(body["tools"]) == json.dumps(payload["tools"])


@pytest.mark.asyncio
async def test_cache_arm_passthrough_governance_and_schema_preserved(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_NAMESPACE_KEY", "test-only-secret")
    settings = _settings(
        tmp_path,
        route=_route(
            max_images_per_request=None,
            image_overflow_policy="passthrough",
            observation_enabled=True,
            constitution_enabled=True,
        ),
        constitution=True,
    )
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    payload = namespace_fixture()
    # Passthrough semantics: images are counted but never enforced; both
    # synthetic images must arrive unchanged.
    payload["input"] = _governed_input() + [
        {"type": "input_image", "image_url": "older-synthetic"},
        {"type": "input_image", "image_url": "newest-synthetic"},
    ]
    response = await _post(settings, payload, state)

    assert response.status_code == 200
    assert state["compiler_calls"] == 1
    assert len(state["proxy_bodies"]) == 1
    body = state["proxy_bodies"][0]
    assert body["tools"] == payload["tools"]
    assert json.dumps(body["tools"]) == json.dumps(payload["tools"])
    images = [item for item in body["input"] if item.get("type") == "input_image"]
    assert images == [
        {"type": "input_image", "image_url": "older-synthetic"},
        {"type": "input_image", "image_url": "newest-synthetic"},
    ]
    assert body["instructions"].startswith("<SLAIF_RECONSTRUCTED_CONSTITUTION ")
    assert "Acquire PROCEDURE.md" in body["instructions"]


@pytest.mark.asyncio
async def test_both_arm_enforces_newest_with_governance(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_NAMESPACE_KEY", "test-only-secret")
    settings = _settings(
        tmp_path,
        route=_route(observation_enabled=True, constitution_enabled=True),
        constitution=True,
    )
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    payload = namespace_fixture()
    payload["input"] = _governed_input() + [
        {"type": "input_image", "image_url": "older-synthetic"},
        {"type": "input_image", "image_url": "newest-synthetic"},
    ]
    response = await _post(settings, payload, state)

    assert response.status_code == 200
    assert state["compiler_calls"] == 1
    assert len(state["proxy_bodies"]) == 1
    body = state["proxy_bodies"][0]
    assert body["tools"] == payload["tools"]
    assert json.dumps(body["tools"]) == json.dumps(payload["tools"])
    images = [item for item in body["input"] if item.get("type") == "input_image"]
    assert images == [{"type": "input_image", "image_url": "newest-synthetic"}]
    assert body["instructions"].startswith("<SLAIF_RECONSTRUCTED_CONSTITUTION ")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route",
    [
        _route(),
        _route(max_images_per_request=None, image_overflow_policy="passthrough"),
    ],
)
async def test_ambiguous_marker_fails_closed_without_upstream(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch, route: RouteConfig
) -> None:
    monkeypatch.setenv("TEST_NAMESPACE_KEY", "test-only-secret")
    settings = _settings(tmp_path, route=route, constitution=False)
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    payload = namespace_fixture()
    payload["input"] = [{"type": "input_image", "image_url": "x"}]
    # A supported marker at a non-list position is genuinely ambiguous.
    response = await _post(settings, {"type": "input_image", "image_url": "x"} | payload, state)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ambiguous_image_shape"
    assert state["proxy_bodies"] == []
    assert state["compiler_calls"] == 0
