"""Focused fake-upstream coverage for process-local compaction rehydration."""

from __future__ import annotations

import asyncio
import dataclasses
import hashlib
import json
from typing import Any

import httpx
import pytest

from slaif_local_coding.app import create_app
from slaif_local_coding.constitution.pipeline import RehydrationKey
from tests.test_pipeline import (
    PRIVATE_TOKEN,
    SOURCE_TEXT,
    agents_payload,
    compiler_response,
    enabled_settings,
)


def zero_root_payload() -> dict[str, Any]:
    return {
        "model": "test-model",
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": "Continue without project files."}],
            }
        ],
    }


def index_for_source(source: str, *, rule_id: str, statement: str) -> dict[str, Any]:
    dependency = {
        "path": "PROCEDURE.md",
        "reference_confidence": 0.9,
        "constitutional_priority": 80,
        "classification": "P1",
        "relationship": "delegated procedure",
        "evidence": "markdown reference",
        "acquisition_urgency": "next_turn",
    }
    return {
        "schema_version": "constitution-index-v1",
        "compiler_version": "compiler-v2",
        "prompt_policy_version": "constitutional-rank-v2",
        "model": "test-model",
        "source_logical_path": "AGENTS.md",
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "source_byte_length": len(source.encode()),
        "summary": f"Bounded {rule_id} summary.",
        "rules": [
            {
                "rule_id": rule_id,
                "strength": "must",
                "statement": statement,
                "location": "line 3",
                "evidence": "MUST sentence",
            }
        ],
        "roles": ["coding agent"],
        "authorities": ["human"],
        "source_of_truth_boundaries": ["source files override this index"],
        "ordering_constraints": [],
        "exceptions": [],
        "dependencies": [dependency],
        "reread_triggers": ["source hash changes"],
        "status": "success",
    }


def compiler_index_response(value: dict[str, Any]) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": json.dumps(value, separators=(",", ":")),
                    }
                }
            ],
            "usage": {"total_tokens": 2},
        },
    )


async def exchange_one(
    settings: Any,
    state: dict[str, Any],
    payloads: list[dict[str, Any]],
    *,
    compiler_responses: list[httpx.Response] | None = None,
) -> list[httpx.Response]:
    queued = list(compiler_responses or [])
    responses: list[httpx.Response] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            state["compiler_calls"] += 1
            return queued.pop(0)
        assert request.url.path == "/v1/responses"
        state["proxy_bodies"].append(await request.aread())
        return httpx.Response(200, json={"id": "sanitized"})

    app = create_app(settings, httpx.MockTransport(handler))
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://adapter.test") as client:
        for payload in payloads:
            response = await client.post("/v1/responses", json=payload)
            responses.append(response)
        state["metrics"] = (await client.get("/metrics")).text
        state["pipeline"] = app.state.constitution_pipeline
    return responses


@pytest.mark.asyncio
async def test_root_populates_then_zero_root_rehydrates_without_compiler(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path)
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    responses = await exchange_one(
        settings,
        state,
        [agents_payload(), zero_root_payload()],
        compiler_responses=[compiler_response()],
    )

    assert [item.status_code for item in responses] == [200, 200]
    assert state["compiler_calls"] == 1
    assert len(state["proxy_bodies"]) == 2
    first_value = json.loads(state["proxy_bodies"][0])
    second_value = json.loads(state["proxy_bodies"][1])
    assert first_value["instructions"] == second_value["instructions"]
    assert "<SLAIF_RECONSTRUCTED_CONSTITUTION" in second_value["instructions"]
    values = state["metrics"]
    assert 'state="populated"' in values
    assert 'state="hit"' in values
    assert 'state="injected"' in values
    assert PRIVATE_TOKEN not in values and SOURCE_TEXT not in values


@pytest.mark.asyncio
async def test_disabled_rehydration_preserves_zero_root_and_never_populates(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path, rehydration_enabled=False)
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    responses = await exchange_one(
        settings,
        state,
        [agents_payload(), zero_root_payload()],
        compiler_responses=[compiler_response()],
    )

    assert [item.status_code for item in responses] == [200, 200]
    assert state["compiler_calls"] == 1
    first_value = json.loads(state["proxy_bodies"][0])
    second_value = json.loads(state["proxy_bodies"][1])
    assert "<SLAIF_RECONSTRUCTED_CONSTITUTION" in first_value["instructions"]
    assert "instructions" not in second_value
    assert state["pipeline"]._rehydration == {}
    metrics = state["metrics"]
    assert 'state="disabled"' in metrics
    assert 'reason="rehydration_disabled"' in metrics
    assert 'state="populated"' not in metrics
    assert 'state="hit"' not in metrics
    assert PRIVATE_TOKEN not in metrics and SOURCE_TEXT not in metrics


@pytest.mark.asyncio
async def test_changed_static_identity_does_not_cross_hit(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path)
    state: dict[str, Any] = {"compiler_calls": 0}
    queued = [compiler_response()]
    bodies: list[bytes] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions" and queued:
            state["compiler_calls"] += 1
            return queued.pop(0)
        if request.url.path == "/v1/responses":
            bodies.append(await request.aread())
        return httpx.Response(200, json={"id": "sanitized"})

    from slaif_local_coding.app import create_app

    app = create_app(settings, httpx.MockTransport(handler))
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://adapter.test") as client:
        populated = await client.post("/v1/responses", json=agents_payload())
        assert populated.status_code == 200

        pipeline = app.state.constitution_pipeline
        original = pipeline.constitution
        pipeline.constitution = original.model_copy(update={"session": "different"})
        isolated = await client.post("/v1/responses", json=zero_root_payload())
        assert isolated.status_code == 200
        isolated_body = json.loads(bodies[-1])
        assert "instructions" not in isolated_body

        pipeline.constitution = original
        restored = await client.post("/v1/responses", json=zero_root_payload())

    restored_body = json.loads(bodies[-1])
    assert restored.status_code == 200
    assert state["compiler_calls"] == 1
    assert restored_body["instructions"] == json.loads(bodies[0])["instructions"]


def test_rehydration_key_matches_every_static_dimension(tmp_path: Any) -> None:
    settings = enabled_settings(tmp_path)
    key = RehydrationKey(
        principal=settings.constitution.principal or "",
        route="constitution-route",
        session=settings.constitution.session or "",
        repository=settings.constitution.repository or "",
        model=settings.upstream.model,
        root_logical_path="AGENTS.md",
        root_source_sha256="0" * 64,
        index_schema_version="constitution-index-v1",
        compiler_version="compiler-v2",
        prompt_policy_version="constitutional-rank-v2",
        reasoning_effort="low",
        max_source_bytes=262_144,
        max_prompt_bytes=384_000,
        max_output_tokens=3000,
        max_output_bytes=256_000,
        max_candidates=128,
        max_json_depth=24,
        observation_schema_version=settings.observation.schema_version,
        observation_policy_version=settings.observation.policy_version,
        observation_max_source_bytes=settings.observation.max_source_bytes,
        observation_max_candidates=settings.observation.max_candidates,
        observation_max_evidence_per_candidate=settings.observation.max_evidence_per_candidate,
        observation_max_total_evidence=settings.observation.max_total_evidence,
        observation_max_path_bytes=settings.observation.max_path_bytes,
        selector_schema_version=settings.constitution.selector_schema_version,
        render_version=settings.constitution.render_version,
        working_set_policy_version=settings.constitution.working_set_policy_version,
        max_injected_bytes=settings.constitution.max_injected_bytes,
        candidate_max_count=settings.constitution.candidate_max_count,
        working_set_max_entries=settings.constitution.working_set_max_entries,
        acquisition_max_count=settings.constitution.acquisition_max_count,
        max_dependency_acquisitions=settings.constitution.max_dependency_acquisitions,
        entry_render_max_bytes=settings.constitution.entry_render_max_bytes,
        injection_max_depth=settings.constitution.injection_max_depth,
        injection_max_nodes=settings.constitution.injection_max_nodes,
    )
    excluded = {"root_logical_path", "root_source_sha256"}
    baseline = key.model_dump(exclude=excluded)
    string_fields = (
        "principal",
        "route",
        "session",
        "repository",
        "model",
        "index_schema_version",
        "compiler_version",
        "prompt_policy_version",
        "reasoning_effort",
        "selector_schema_version",
        "render_version",
        "working_set_policy_version",
    )
    numeric_fields = (
        "max_source_bytes",
        "max_prompt_bytes",
        "max_output_tokens",
        "max_output_bytes",
        "max_candidates",
        "max_json_depth",
        "observation_max_source_bytes",
        "observation_max_candidates",
        "observation_max_evidence_per_candidate",
        "observation_max_total_evidence",
        "observation_max_path_bytes",
        "max_injected_bytes",
        "candidate_max_count",
        "working_set_max_entries",
        "acquisition_max_count",
        "max_dependency_acquisitions",
        "entry_render_max_bytes",
        "injection_max_depth",
        "injection_max_nodes",
    )
    for field in string_fields:
        changed = key.model_copy(update={field: f"changed-{field}"})
        assert changed.model_dump(exclude=excluded) != baseline
    for field in numeric_fields:
        changed = key.model_copy(update={field: key.model_dump()[field] + 1})
        assert changed.model_dump(exclude=excluded) != baseline


@pytest.mark.asyncio
async def test_ttl_corruption_restart_and_conflict_fail_safe(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path)
    state: dict[str, Any] = {"compiler_calls": 0}
    queued = [compiler_response(), compiler_response()]
    bodies: list[bytes] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions" and queued:
            state["compiler_calls"] += 1
            return queued.pop(0)
        if request.url.path == "/v1/responses":
            bodies.append(await request.aread())
        return httpx.Response(200, json={"id": "sanitized"})

    from slaif_local_coding.app import create_app

    app = create_app(settings, httpx.MockTransport(handler))
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://adapter.test") as client:
        populated = await client.post("/v1/responses", json=agents_payload())
        assert populated.status_code == 200

        conflict = zero_root_payload()
        opening = '<SLAIF_RECONSTRUCTED_CONSTITUTION render_version="constitution-render-v1">'
        conflict["instructions"] = f"{opening}\ndifferent\n</SLAIF_RECONSTRUCTED_CONSTITUTION>"
        rejected = await client.post("/v1/responses", json=conflict)
        assert rejected.status_code == 422

        pipeline = app.state.constitution_pipeline
        key = next(iter(pipeline._rehydration))
        pipeline._rehydration[key] = dataclasses.replace(
            pipeline._rehydration[key],
            created_at=pipeline._rehydration[key].created_at
            - settings.constitution.rehydration.ttl_seconds
            - 1,
        )
        expired = await client.post("/v1/responses", json=zero_root_payload())
        assert expired.status_code == 200
        assert json.loads(bodies[-1]).get("instructions") is None

        # Repopulate through the persistent cache, then inject an invalid typed entry.
        await client.post("/v1/responses", json=agents_payload())
        key = next(iter(pipeline._rehydration))
        pipeline._rehydration[key] = object()
        corrupt = await client.post("/v1/responses", json=zero_root_payload())
        assert corrupt.status_code == 200

    restart_state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}
    restarted = await exchange_one(enabled_settings(tmp_path), restart_state, [zero_root_payload()])
    assert restarted[0].status_code == 200
    assert restart_state["compiler_calls"] == 0

    assert state["compiler_calls"] == 1
    assert 'state="stale_expired"' in (await _metrics_text(app))
    assert 'reason="corrupt_or_oversized"' in (await _metrics_text(app))


async def _metrics_text(app: Any) -> str:
    import httpx

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://adapter.test") as client:
        return (await client.get("/metrics")).text


@pytest.mark.asyncio
async def test_new_root_replaces_previous_working_set_same_process(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path)
    old_source = SOURCE_TEXT
    new_source = SOURCE_TEXT + "\nDistinct replacement content.\n"
    queued = [
        compiler_response(),
        compiler_index_response(
            index_for_source(
                new_source,
                rule_id="replacement-rule",
                statement="Use the replacement procedure.",
            )
        ),
    ]
    state: dict[str, Any] = {"compiler_calls": 0, "proxy_bodies": []}

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            state["compiler_calls"] += 1
            return queued.pop(0)
        state["proxy_bodies"].append(await request.aread())
        return httpx.Response(200, json={"id": "sanitized"})

    from slaif_local_coding.app import create_app

    app = create_app(settings, httpx.MockTransport(handler))
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://adapter.test") as client:
        first_response = await client.post("/v1/responses", json=agents_payload())
        replacement_payload = agents_payload()
        replacement_payload["input"][0]["content"] = new_source
        replacement_response = await client.post("/v1/responses", json=replacement_payload)
        rehydrated_response = await client.post("/v1/responses", json=zero_root_payload())
        metrics = (await client.get("/metrics")).text
        print([line for line in metrics.splitlines() if "rehydration" in line])

    assert [first_response.status_code, replacement_response.status_code] == [200, 200]
    assert rehydrated_response.status_code == 200
    assert state["compiler_calls"] == 2
    old_value = json.loads(state["proxy_bodies"][0])
    new_value = json.loads(state["proxy_bodies"][1])
    rehydrated_value = json.loads(state["proxy_bodies"][2])
    assert old_value["instructions"] != new_value["instructions"]
    assert new_value["instructions"] == rehydrated_value["instructions"]
    assert "replacement-rule" in new_value["instructions"]
    assert old_source in old_value["input"][0]["content"]
    assert PRIVATE_TOKEN not in metrics and new_source not in metrics


@pytest.mark.asyncio
async def test_chat_rehydrates_and_is_idempotent(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path)
    state: dict[str, Any] = {"compiler_calls": 0}
    queued = [compiler_response()]
    bodies: list[bytes] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions" and queued:
            state["compiler_calls"] += 1
            return queued.pop(0)
        if request.url.path == "/v1/chat/completions":
            bodies.append(await request.aread())
        return httpx.Response(200, json={"id": "sanitized"})

    from slaif_local_coding.app import create_app

    root_chat = {
        "model": "test-model",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "input_file", "filename": "AGENTS.md", "content": SOURCE_TEXT}
                ],
            }
        ],
    }
    compacted = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "Continue."}],
    }
    app = create_app(settings, httpx.MockTransport(handler))
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://adapter.test") as client:
        first = await client.post("/v1/chat/completions", json=root_chat)
        second = await client.post("/v1/chat/completions", json=compacted)
        third = await client.post("/v1/chat/completions", json=compacted)

    assert first.status_code == second.status_code == third.status_code == 200
    assert state["compiler_calls"] == 1
    first_message = json.loads(bodies[0])["messages"][0]
    second_message = json.loads(bodies[1])["messages"][0]
    third_message = json.loads(bodies[2])["messages"][0]
    assert first_message["role"] == second_message["role"] == third_message["role"] == "system"
    assert first_message["content"] == second_message["content"] == third_message["content"]


def test_lru_and_total_byte_pressure_discard_oldest_safe_entry(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path)
    state: dict[str, Any] = {"compiler_calls": 0}
    responses = asyncio.run(_populate_once(settings, state))
    assert responses.status_code == 200
    pipeline = state["pipeline"]
    first_key = next(iter(pipeline._rehydration))
    first_entry = pipeline._rehydration[first_key]

    # Tighten the live process-local bounds without touching persistent cache.
    pipeline.constitution = pipeline.constitution.model_copy(
        update={
            "rehydration": pipeline.constitution.rehydration.model_copy(
                update={
                    "max_entries": 2,
                    "max_entry_bytes": first_entry.bytes,
                    "max_total_bytes": first_entry.bytes,
                }
            )
        }
    )
    second_key = first_key.model_copy(update={"root_source_sha256": "1" * 64})
    pipeline._store_rehydration(
        key=second_key,
        root=first_entry.root,
        dependencies=first_entry.dependencies,
        metadata=first_entry.inclusion_metadata,
        endpoint="/v1/responses",
        route_name="constitution-route",
    )

    assert first_key not in pipeline._rehydration
    assert list(pipeline._rehydration) == [second_key]
    assert pipeline._rehydration_bytes == first_entry.bytes
    assert 'state="populated"' in state["metrics"]


def test_oversized_rehydration_does_not_evict_valid_entries(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    settings = enabled_settings(tmp_path)
    state: dict[str, Any] = {"compiler_calls": 0}
    response = asyncio.run(_populate_once(settings, state))
    assert response.status_code == 200
    pipeline = state["pipeline"]
    first_key = next(iter(pipeline._rehydration))
    first_entry = pipeline._rehydration[first_key]
    pipeline.constitution = pipeline.constitution.model_copy(
        update={
            "rehydration": pipeline.constitution.rehydration.model_copy(
                update={
                    "max_entries": 2,
                    "max_entry_bytes": first_entry.bytes,
                    "max_total_bytes": first_entry.bytes - 1,
                }
            )
        }
    )

    pipeline._store_rehydration(
        key=first_key.model_copy(update={"root_source_sha256": "2" * 64}),
        root=first_entry.root,
        dependencies=first_entry.dependencies,
        metadata=first_entry.inclusion_metadata,
        endpoint="/v1/responses",
        route_name="constitution-route",
    )

    assert list(pipeline._rehydration) == [first_key]
    assert pipeline._rehydration_bytes == first_entry.bytes


async def _populate_once(settings: Any, state: dict[str, Any]) -> httpx.Response:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            state["compiler_calls"] += 1
            return compiler_response()
        return httpx.Response(200, json={"id": "sanitized"})

    from slaif_local_coding.app import create_app

    app = create_app(settings, httpx.MockTransport(handler))
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://adapter.test") as client:
        response = await client.post("/v1/responses", json=agents_payload())
        state["metrics"] = (await client.get("/metrics")).text
        state["pipeline"] = app.state.constitution_pipeline
    return response
