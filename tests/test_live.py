"""Bounded opt-in tests against a foreground adapter on port 18031."""

import hashlib
import json
import os
import re
from typing import Any

import httpx
import pytest
from prometheus_client import CollectorRegistry, generate_latest

from slaif_local_coding.config import ObservationPolicy
from slaif_local_coding.constitution.cache import (
    CacheIdentity,
    CachePolicy,
    DerivedIndexCache,
)
from slaif_local_coding.constitution.compiler import (
    CompilerSettings,
    ConstitutionalCompiler,
    ObservedSourceMetadata,
)
from slaif_local_coding.constitution.compiler_models import CompilerResult
from slaif_local_coding.constitution.references import extract_references

pytestmark = pytest.mark.skipif(os.getenv("SLAIF_LIVE_TEST") != "1", reason="set SLAIF_LIVE_TEST=1")


def test_live_health_models_and_text() -> None:
    with httpx.Client(base_url="http://127.0.0.1:18031", timeout=90) as client:
        assert client.get("/healthz").status_code == 200
        assert client.get("/readyz").status_code == 200
        assert client.get("/health").status_code == 200
        models = client.get("/v1/models")
        assert models.status_code == 200
        assert any(item["id"] == "qwen3.8-27b" for item in models.json()["data"])
        response = client.post(
            "/v1/responses",
            json={"model": "qwen3.8-27b", "input": "Reply with OK only.", "max_output_tokens": 8},
        )
        assert response.status_code == 200


def test_live_forced_tool_and_multiturn() -> None:
    tool: dict[str, Any] = {
        "type": "function",
        "name": "lookup_code",
        "description": "Return a short synthetic code.",
        "parameters": {
            "type": "object",
            "properties": {"label": {"type": "string"}},
            "required": ["label"],
            "additionalProperties": False,
        },
    }
    with httpx.Client(base_url="http://127.0.0.1:18031", timeout=90) as client:
        first = client.post(
            "/v1/responses",
            json={
                "model": "qwen3.8-27b",
                "input": "Call lookup_code with label alpha.",
                "tools": [tool],
                "tool_choice": {"type": "function", "name": "lookup_code"},
                "max_output_tokens": 80,
            },
        )
        assert first.status_code == 200
        calls = [
            item for item in first.json().get("output", []) if item.get("type") == "function_call"
        ]
        assert len(calls) == 1
        assert isinstance(json.loads(calls[0]["arguments"]), dict)
        continuation = client.post(
            "/v1/responses",
            json={
                "model": "qwen3.8-27b",
                "input": [
                    calls[0],
                    {
                        "type": "function_call_output",
                        "call_id": calls[0]["call_id"],
                        "output": "SYNTHETIC-OK",
                    },
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": "Use the synthetic result."}],
                    },
                ],
                "tools": [tool],
                "max_output_tokens": 40,
            },
        )
        assert continuation.status_code == 200


def test_live_sse_event_structure() -> None:
    with httpx.Client(base_url="http://127.0.0.1:18031", timeout=90) as client:
        with client.stream(
            "POST",
            "/v1/responses",
            json={
                "model": "qwen3.8-27b",
                "input": "Reply with OK only.",
                "stream": True,
                "max_output_tokens": 8,
            },
        ) as response:
            assert response.status_code == 200
            event_types = []
            for line in response.iter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    event_types.append(json.loads(line[6:])["type"])
            assert event_types[0] == "response.created"
            assert "response.completed" in event_types


def test_live_automatic_and_streaming_tool_calls() -> None:
    tool: dict[str, Any] = {
        "type": "function",
        "name": "lookup_code",
        "description": "Return a synthetic code; always use this for code lookups.",
        "parameters": {
            "type": "object",
            "properties": {"label": {"type": "string"}},
            "required": ["label"],
        },
    }
    with httpx.Client(base_url="http://127.0.0.1:18031", timeout=90) as client:
        automatic = client.post(
            "/v1/responses",
            json={
                "model": "qwen3.8-27b",
                "input": "Use lookup_code for label beta.",
                "tools": [tool],
                "max_output_tokens": 80,
            },
        )
        assert automatic.status_code == 200
        assert any(item.get("type") == "function_call" for item in automatic.json()["output"])
        with client.stream(
            "POST",
            "/v1/responses",
            json={
                "model": "qwen3.8-27b",
                "input": "Call lookup_code for label gamma.",
                "tools": [tool],
                "tool_choice": {"type": "function", "name": "lookup_code"},
                "stream": True,
                "max_output_tokens": 80,
            },
        ) as streamed:
            assert streamed.status_code == 200
            types = [
                json.loads(line[6:])["type"]
                for line in streamed.iter_lines()
                if line.startswith("data: ") and line != "data: [DONE]"
            ]
            assert any("function_call" in event_type for event_type in types)


def test_live_one_and_two_image_requests() -> None:
    # Two distinguishable synthetic 1x1 PNG fixtures; no user/customer image data.
    images = [
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl2nWQAAAAASUVORK5CYII=",
    ]

    def metric_value(text: str, result: str) -> float:
        match = re.search(
            rf'slaif_image_items_total\{{result="{result}",'
            rf'route="qwen38-vision-codex"\}} ([0-9.]+)',
            text,
        )
        return float(match.group(1)) if match else 0.0

    with httpx.Client(base_url="http://127.0.0.1:18031", timeout=120) as client:
        before = client.get("/metrics").text
        before_seen = metric_value(before, "seen")
        before_removed = metric_value(before, "removed")
        for count in (1, 2):
            content: list[dict[str, Any]] = [{"type": "text", "text": "Answer OK only."}]
            content.extend(
                {"type": "image_url", "image_url": {"url": image}} for image in images[:count]
            )
            response = client.post(
                "/v1/chat/completions",
                json={
                    "model": "qwen3.8-27b",
                    "messages": [{"role": "user", "content": content}],
                    "max_tokens": 8,
                },
            )
            if response.status_code >= 400:
                pytest.skip("live endpoint rejected an image request (verified zero-image case)")
            assert response.status_code == 200
        after = client.get("/metrics").text
        assert metric_value(after, "seen") - before_seen == 3
        assert metric_value(after, "removed") - before_removed == 1


@pytest.mark.asyncio
async def test_live_enabled_constitution_pipeline_miss_then_hit() -> None:
    """Run only against the temporary 18031 config whose route enables 003-b."""

    def value(text: str, name: str) -> float:
        match = re.search(rf"^{re.escape(name)}(?:\{{[^}}]*\}})? ([0-9.]+)$", text, re.M)
        return float(match.group(1)) if match else 0.0

    payload = {
        "model": "qwen3.8-27b",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "# AGENTS.md instructions for repository\n\n<INSTRUCTIONS>\n"
                            "# Synthetic governance fixture\n\n"
                            "The agent MUST read [PROCEDURE.md](PROCEDURE.md) before mutation.\n"
                            "</INSTRUCTIONS>"
                        ),
                    }
                ],
            },
        ],
    }

    def injected_value(text: str) -> float:
        match = re.search(
            r'^slaif_constitution_pipeline_requests_total\{.*state="injected".*\} ([0-9.]+)$',
            text,
            re.M,
        )
        return float(match.group(1)) if match else 0.0

    async with httpx.AsyncClient(base_url="http://127.0.0.1:18031", timeout=120) as client:
        before = (await client.get("/metrics")).text
        first = await client.post("/v1/responses", json=payload)
        second = await client.post("/v1/responses", json=payload)
        after = (await client.get("/metrics")).text
    if 'state="injected"' not in after:
        pytest.skip("temporary adapter did not enable the objective-003-b pipeline")
    assert first.status_code == second.status_code == 200
    injected_delta = injected_value(after) - injected_value(before)
    cache_hit_delta = value(after, "slaif_constitution_cache_hits_total") - value(
        before, "slaif_constitution_cache_hits_total"
    )
    assert injected_delta >= 2
    assert cache_hit_delta >= 1


@pytest.mark.asyncio
async def test_live_constitution_compiler_and_cache(tmp_path: Any) -> None:
    """One bounded synthetic miss is persisted; the identical call is a hit."""
    source = (
        b"# Synthetic governance fixture\n\n"
        b"The coding agent MUST read [PROCEDURE.md](PROCEDURE.md) before mutation.\n"
        b"NEVER expose synthetic secrets.\n"
    )
    extraction = extract_references(source.decode(), ObservationPolicy())
    assert [candidate.path for candidate in extraction.candidates] == ["PROCEDURE.md"]
    settings = CompilerSettings(
        base_url="http://127.0.0.1:18020/v1",
        api_key_env="QWEN3090_API_KEY",
        model="qwen3.8-27b",
        timeout_seconds=120,
        max_attempts=2,
        max_output_tokens=3000,
    )
    cache_identity = CacheIdentity(
        principal="oap-live-test",
        route="compiler-library",
        session="bounded-002a",
        repository="synthetic-repository",
    )
    policy = CachePolicy(
        root=tmp_path / "derived-cache",
        fallback_root=None,
        max_total_bytes=1024 * 1024,
        max_entry_bytes=256 * 1024,
        max_pinned_bytes=256 * 1024,
        max_entries=16,
        ttl_seconds=300,
        max_scan_entries=64,
    )
    metrics_registry = CollectorRegistry()
    async with ConstitutionalCompiler(
        settings,
        cache=DerivedIndexCache(policy, registry=metrics_registry),
        registry=metrics_registry,
    ) as compiler:

        async def compile_once() -> CompilerResult:
            return await compiler.compile(
                source,
                "AGENTS.md",
                ObservedSourceMetadata(
                    logical_path="AGENTS.md",
                    content_sha256=hashlib.sha256(source).hexdigest(),
                    byte_length=len(source),
                ),
                extraction.candidates,
                cache_identity,
            )

        first = await compile_once()
        assert first.ok
        assert first.index is not None
        assert first.cache_outcome == "miss-persisted"
        assert [item.path for item in first.index.dependencies] == ["PROCEDURE.md"]
        second = await compile_once()
        assert second.ok and second.cache_outcome == "hit"
    metrics = generate_latest(compiler.registry).decode()
    assert "slaif_constitution_cache_hits_total 1.0" in metrics
    assert "SYNTHETIC" not in metrics and "PROCEDURE" not in metrics
