"""Bounded opt-in tests against a foreground adapter on port 18031."""

import json
import os
from typing import Any

import httpx
import pytest

pytestmark = pytest.mark.skipif(os.getenv("SLAIF_LIVE_TEST") != "1", reason="set SLAIF_LIVE_TEST=1")


def test_live_health_models_and_text() -> None:
    with httpx.Client(base_url="http://127.0.0.1:18031", timeout=90) as client:
        assert client.get("/healthz").status_code == 200
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
    # Public-domain-style synthetic 1x1 PNG fixture; no user/customer image data.
    image = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    with httpx.Client(base_url="http://127.0.0.1:18031", timeout=120) as client:
        for count in (1, 2):
            content: list[dict[str, Any]] = [{"type": "text", "text": "Answer OK only."}]
            content.extend({"type": "image_url", "image_url": {"url": image}} for _ in range(count))
            response = client.post(
                "/v1/chat/completions",
                json={
                    "model": "qwen3.8-27b",
                    "messages": [{"role": "user", "content": content}],
                    "max_tokens": 8,
                },
            )
            assert response.status_code == 200
