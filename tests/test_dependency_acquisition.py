"""Request-only dependency acquisition and bounded incremental compilation."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from typing import Any

import httpx
import pytest

from slaif_local_coding.app import create_app
from slaif_local_coding.config import (
    CacheConfig,
    CompilerConfig,
    ConstitutionIntegrationConfig,
    ObservationPolicy,
    RouteConfig,
    ServerConfig,
    Settings,
    UpstreamConfig,
)
from slaif_local_coding.constitution import ObservationContext, observe_request_for_pipeline
from slaif_local_coding.constitution.compiler_models import (
    AcquisitionUrgency,
    CompiledDependency,
    CompiledIndex,
    CompiledRule,
    ConstitutionalClass,
    RuleStrength,
)
from slaif_local_coding.constitution.models import (
    DependencyObservationReason,
    EvidenceType,
    TrustClass,
)

ROOT = (
    b"# Synthetic governance\n\n"
    b"MUST read [SECURITY.md](SECURITY.md) and [PROCEDURE.md](PROCEDURE.md).\n"
)
ROOT_TEXT = ROOT.decode()
DEPENDENCY = b"MUST NEVER bypass the sentinel dependency rule.\n"
DEPENDENCY_TEXT = DEPENDENCY.decode()
RAW_DEPENDENCY_TOKEN = "unique-dependency-raw-token-b7c3"


def context() -> ObservationContext:
    return ObservationContext(
        endpoint="/v1/responses",
        route_id="constitution",
        model="test-model",
        streaming=False,
        discriminator_trust=TrustClass.ABSENT,
    )


def root_payload(**changes: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "model": "test-model",
        "input": [
            {
                "type": "input_file",
                "filename": "AGENTS.md",
                "content": ROOT_TEXT,
            }
        ],
    }
    value.update(changes)
    return value


def input_dependency(payload: dict[str, Any], *, content: str = DEPENDENCY_TEXT) -> None:
    payload["input"].append({"type": "input_file", "filename": "SECURITY.md", "content": content})


def procedure_dependency(payload: dict[str, Any]) -> None:
    payload["input"].append(
        {"type": "input_file", "filename": "PROCEDURE.md", "content": DEPENDENCY_TEXT}
    )


def responses_tool_dependency(payload: dict[str, Any], *, output: Any = DEPENDENCY_TEXT) -> None:
    payload["input"].extend(
        [
            {
                "type": "function_call",
                "call_id": "dependency-call",
                "name": "exec_command",
                "arguments": json.dumps({"cmd": "head -n 20 SECURITY.md"}),
            },
            {"type": "function_call_output", "call_id": "dependency-call", "output": output},
        ]
    )


def chat_pairing() -> dict[str, Any]:
    return {
        "model": "test-model",
        "input": [
            {"type": "input_file", "filename": "AGENTS.md", "content": ROOT_TEXT},
            {
                "type": "function_call",
                "call_id": "chat-call",
                "name": "exec_command",
                "arguments": '{"cmd":"cat SECURITY.md"}',
            },
            {
                "type": "function_call_output",
                "call_id": "chat-call",
                "output": DEPENDENCY_TEXT,
            },
        ],
        "messages": [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "id": "paired-chat-call",
                        "function": {
                            "name": "exec_command",
                            "arguments": '{"cmd":"sed -n \'1,20p\' SECURITY.md"}',
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "paired-chat-call",
                "content": DEPENDENCY_TEXT,
            },
        ],
    }


def index(
    path: str, source: bytes, *, dependencies: tuple[CompiledDependency, ...] = ()
) -> CompiledIndex:
    return CompiledIndex(
        schema_version="constitution-index-v1",
        compiler_version="compiler-v2",
        prompt_policy_version="constitutional-rank-v2",
        model="test-model",
        source_logical_path=path,
        source_sha256=hashlib.sha256(source).hexdigest(),
        source_byte_length=len(source),
        summary=f"Bounded synthetic summary for {path}.",
        rules=(
            CompiledRule(
                rule_id="root-rule" if path == "AGENTS.md" else "dependency-rule",
                strength=RuleStrength.MUST,
                statement="Preserve the bounded synthetic rule.",
                location="line 1",
                evidence="synthetic fixture",
            ),
        ),
        roles=("coding agent",),
        authorities=("repository sources",),
        source_of_truth_boundaries=("source files override this index",),
        dependencies=dependencies,
        reread_triggers=("source hash changes",),
    )


def root_index() -> CompiledIndex:
    def declaration(path: str) -> CompiledDependency:
        return CompiledDependency(
            path=path,
            reference_confidence=0.9,
            constitutional_priority=80,
            classification=ConstitutionalClass.P1_DELEGATED_OR_SECURITY,
            relationship="delegated law",
            evidence="markdown reference",
            acquisition_urgency=AcquisitionUrgency.NEXT_TURN,
        )

    return index(
        "AGENTS.md", ROOT, dependencies=(declaration("SECURITY.md"), declaration("PROCEDURE.md"))
    )


def compiler_response(path: str, source: bytes) -> httpx.Response:
    compiled = root_index() if path == "AGENTS.md" else index("SECURITY.md", source)
    raw = json.dumps(compiled.model_dump(mode="json"), separators=(",", ":")).encode()
    return httpx.Response(
        200,
        json={"choices": [{"message": {"content": raw.decode()}}]},
    )


def enabled_settings(tmp_path: Any, *, session: str = "session-a", budget: int = 4) -> Settings:
    return Settings(
        server=ServerConfig(request_body_max_bytes=16_384),
        upstream=UpstreamConfig(
            base_url="http://upstream.test/v1",
            api_key_env="TEST_DEPENDENCY_KEY",
            model="test-model",
        ),
        routes=[
            RouteConfig(
                name="constitution-route",
                model="test-model",
                max_images_per_request=0,
                image_overflow_policy="reject",
                observation_enabled=True,
                constitution_enabled=True,
            )
        ],
        observation=ObservationPolicy(max_source_bytes=256),
        compiler=CompilerConfig(enabled=True, api_key_env="TEST_DEPENDENCY_KEY", max_attempts=1),
        cache=CacheConfig(
            root=tmp_path / f"cache-{session}",
            fallback_root=None,
            max_total_bytes=1024 * 1024,
            max_entry_bytes=256 * 1024,
            max_pinned_bytes=256 * 1024,
            max_entries=32,
            ttl_seconds=300,
            max_scan_entries=64,
        ),
        constitution=ConstitutionIntegrationConfig(
            enabled=True,
            principal="principal",
            session=session,
            repository="repository",
            max_dependency_acquisitions=budget,
        ),
    )


async def exchange(
    settings: Settings, state: dict[str, Any], payload: dict[str, Any]
) -> httpx.Response:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            state["compiler_calls"] += 1
            body = json.loads(await request.aread())
            user = body["messages"][1]["content"]
            marker = "<source path="
            start = user.index(marker) + len(marker) + 1
            end = user.index("'", start)
            path = user[start:end]
            source = ROOT if path == "AGENTS.md" else DEPENDENCY
            return compiler_response(path, source)
        state["proxy_bodies"].append(await request.aread())
        return httpx.Response(200, json={"id": "sanitized"})

    app = create_app(settings, httpx.MockTransport(handler))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.post("/v1/responses", json=payload)
        state.setdefault("metrics_history", []).append((await client.get("/metrics")).text)
    return response


def test_input_file_dependency_is_exact_bounded_and_private() -> None:
    policy = ObservationPolicy(max_source_bytes=256)
    payload = root_payload()
    input_dependency(payload)
    result, _, sources = observe_request_for_pipeline(payload, context(), policy)

    assert [item.logical_path for item in result.dependencies] == ["SECURITY.md"]
    assert sources["SECURITY.md"] == DEPENDENCY
    public_json = result.model_dump_json()
    assert RAW_DEPENDENCY_TOKEN not in public_json
    assert hashlib.sha256(DEPENDENCY).hexdigest() not in public_json


def test_responses_input_file_and_tool_dependencies_are_deterministic() -> None:
    file_payload = root_payload()
    input_dependency(file_payload)
    tool_payload = root_payload()
    responses_tool_dependency(tool_payload)

    first = observe_request_for_pipeline(file_payload, context(), ObservationPolicy())
    second = observe_request_for_pipeline(tool_payload, context(), ObservationPolicy())
    third = observe_request_for_pipeline(tool_payload, context(), ObservationPolicy())

    assert first[0].dependencies[0].logical_path == "SECURITY.md"
    assert first[2]["SECURITY.md"] == DEPENDENCY
    assert second[0].dependencies[0].evidence[0].type is EvidenceType.PAIRED_TOOL_RESULT
    assert second[2]["SECURITY.md"] == DEPENDENCY
    assert second[0].model_dump_json() == third[0].model_dump_json()


def test_chat_message_tool_result_pairs_with_exact_call_id() -> None:
    payload = chat_pairing()
    del payload["input"][2:]
    result, _, sources = observe_request_for_pipeline(payload, context(), ObservationPolicy())
    assert [item.evidence[0].type.value for item in result.dependencies] == ["paired_tool_result"]
    assert sources["SECURITY.md"] == DEPENDENCY


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        (
            lambda value: value.append(dict(value[1])),
            DependencyObservationReason.DUPLICATE_EVIDENCE,
        ),
        (
            lambda value: value[-1].update(output={"unexpected": True}),
            DependencyObservationReason.MISMATCHED_PAIRING,
        ),
        (
            lambda value: value.insert(-1, dict(value[-2])),
            DependencyObservationReason.DUPLICATE_EVIDENCE,
        ),
    ],
)
def test_invalid_or_duplicate_evidence_is_never_acquired(
    mutation: Any, reason: DependencyObservationReason
) -> None:
    payload = root_payload()
    responses_tool_dependency(payload)
    mutation(payload["input"])
    result, _, sources = observe_request_for_pipeline(payload, context(), ObservationPolicy())

    assert result.dependencies == () and sources == {}
    assert reason in {item.reason for item in result.dependency_rejections}


def test_unsafe_mismatched_and_oversized_dependencies_fail_closed() -> None:
    unsafe = root_payload()
    unsafe["input"].append({"type": "input_file", "filename": "../SECURITY.md", "content": "x"})
    mismatched = root_payload()
    mismatched["input"].append({"type": "input_file", "filename": "SECURITY.md"})
    oversized_policy = ObservationPolicy(max_source_bytes=256)
    oversized = root_payload()
    oversized["input"].append(
        {"type": "input_file", "filename": "SECURITY.md", "content": "x" * 257}
    )

    unsafe_result = observe_request_for_pipeline(unsafe, context(), ObservationPolicy())
    mismatched_result = observe_request_for_pipeline(mismatched, context(), ObservationPolicy())
    oversized_result = observe_request_for_pipeline(oversized, context(), oversized_policy)

    for result in (unsafe_result[0], mismatched_result[0], oversized_result[0]):
        assert result.dependencies == ()
    assert DependencyObservationReason.UNSAFE_PATH in {
        item.reason for item in unsafe_result[0].dependency_rejections
    }
    assert DependencyObservationReason.MISMATCHED_PAIRING in {
        item.reason for item in mismatched_result[0].dependency_rejections
    }
    assert DependencyObservationReason.CONTENT_TOO_LARGE in {
        item.reason for item in oversized_result[0].dependency_rejections
    }


@pytest.mark.asyncio
async def test_root_plus_dependency_compiles_then_reuses_both_indexes(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_DEPENDENCY_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path)
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    payload = root_payload()
    input_dependency(payload)
    first = await exchange(settings, state, payload)
    second = await exchange(settings, state, payload)

    assert first.status_code == second.status_code == 200
    assert state["compiler_calls"] == 2
    first_value = json.loads(state["proxy_bodies"][0])
    second_value = json.loads(state["proxy_bodies"][1])
    assert "Bounded synthetic summary for SECURITY.md." in first_value["instructions"]
    assert "MUST NEVER bypass" not in first_value["instructions"]
    assert first_value["instructions"] == second_value["instructions"]

    metrics = "\n".join(state["metrics_history"])
    outcomes = {
        match.group(1): float(value)
        for line in metrics.splitlines()
        if line.startswith("slaif_constitution_dependency_acquisitions_total{")
        for match in [re.search(r'outcome="([^"]+)"', line)]
        if match
        for value in [line.rsplit(" ", 1)[-1]]
    }
    assert outcomes == {"cache_hit": 1.0, "cache_miss": 1.0}
    assert RAW_DEPENDENCY_TOKEN not in metrics and ROOT_TEXT not in metrics


@pytest.mark.asyncio
async def test_budget_preserves_missing_dependency_instruction(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_DEPENDENCY_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path, budget=1)
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    payload = root_payload()
    input_dependency(payload)
    procedure_dependency(payload)
    response = await exchange(settings, state, payload)

    assert response.status_code == 200
    assert state["compiler_calls"] == 2
    body = json.loads(state["proxy_bodies"][0])
    assert "Acquire PROCEDURE.md" in body["instructions"]
    metrics = state["metrics_history"][0]
    assert 'outcome="budget_exceeded"' in metrics


@pytest.mark.asyncio
async def test_dependency_compiler_failure_still_injects_root_missing_instruction(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_DEPENDENCY_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path)
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    payload = root_payload()
    input_dependency(payload)

    async def failing_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            state["compiler_calls"] += 1
            if state["compiler_calls"] > 1:
                return httpx.Response(503, json={"error": "sanitized"})
            return compiler_response("AGENTS.md", ROOT)
        state["proxy_bodies"].append(await request.aread())
        return httpx.Response(200, json={"id": "sanitized"})

    app = create_app(settings, httpx.MockTransport(failing_handler))
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://adapter.test") as client:
        response = await client.post("/v1/responses", json=payload)
        metrics = (await client.get("/metrics")).text

    assert response.status_code == 200
    assert state["compiler_calls"] == 2
    body = json.loads(state["proxy_bodies"][0])
    assert "Acquire PROCEDURE.md" in body["instructions"]
    assert 'outcome="invalid"' in metrics


@pytest.mark.asyncio
async def test_identity_isolation_and_cancellation_slot_release(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_DEPENDENCY_KEY", "test-only-secret")
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    payload = root_payload()
    input_dependency(payload)
    await exchange(enabled_settings(tmp_path, session="one"), state, payload)
    await exchange(enabled_settings(tmp_path, session="two"), state, payload)
    assert state["compiler_calls"] == 4

    from prometheus_client import CollectorRegistry

    from slaif_local_coding.constitution.cache import CacheIdentity, CachePolicy
    from slaif_local_coding.constitution.compiler import CompilerSettings, ConstitutionalCompiler
    from slaif_local_coding.constitution.pipeline import ConstitutionPipeline

    class CancelledCompiler(ConstitutionalCompiler):
        async def compile(self, *args: Any, **kwargs: Any) -> Any:
            raise asyncio.CancelledError()

    settings = CompilerSettings(
        base_url="http://upstream.test/v1",
        api_key_env="TEST_DEPENDENCY_KEY",
        model="test-model",
    )
    pipeline = ConstitutionPipeline(
        constitution=enabled_settings(tmp_path).constitution,
        compiler=settings,
        cache_policy=CachePolicy(
            root=tmp_path / "cancel",
            fallback_root=None,
            max_total_bytes=1024 * 1024,
            max_entry_bytes=256 * 1024,
            max_pinned_bytes=256 * 1024,
            max_entries=16,
            ttl_seconds=300,
            max_scan_entries=64,
        ),
        registry=CollectorRegistry(),
        client=httpx.AsyncClient(),
    )
    original_compile = ConstitutionalCompiler.compile
    try:
        type(pipeline.compiler).compile = CancelledCompiler.compile  # type: ignore[method-assign, assignment]
        with pytest.raises(asyncio.CancelledError):
            await pipeline._compile_dependencies(
                root_index=root_index(),
                observation_policy=ObservationPolicy(),
                source_bytes_by_dependency={"SECURITY.md": DEPENDENCY},
                identity=CacheIdentity(principal="p", route="r", session="s", repository="repo"),
                endpoint="/v1/responses",
                route_name="route",
            )
    finally:
        type(pipeline.compiler).compile = original_compile  # type: ignore[method-assign]
        await pipeline.aclose()
    assert pipeline.compiler._slot._value == 1
