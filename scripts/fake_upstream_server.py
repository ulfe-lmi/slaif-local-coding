"""Disposable fake OpenAI-compatible upstream (order 011-a, workstream B12).

Stdlib-only, loopback-only, disposable test service used by the Docker CI
job and local qualification runs. It is NOT a production component and is
excluded from both artifacts (the top-level ``scripts/`` hatch exclusion).

Endpoints (bounded JSON only):
- ``GET /health``
- ``GET /v1/models``
- ``POST /v1/chat/completions`` — non-streaming completion, SSE streaming
  completion, and an ordinary function-tool round-trip shape.

Every representative response embeds the per-run sentinel token
(``SLAIF_FAKE_SENTINEL:<token>``) so a caller can correlate that a request
reached exactly this fake instance (sentinel correlation). No request or
response body is logged; only bounded counts and the fixed startup line are
emitted. The process must be killed by the caller (disposable by design).
"""

from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

MAX_BODY_BYTES = 1_048_576


def _tool_name(request: dict[str, Any]) -> str:
    tools = request.get("tools")
    if isinstance(tools, list) and tools:
        first = tools[0]
        if isinstance(first, dict):
            fn = first.get("function")
            if isinstance(fn, dict) and isinstance(fn.get("name"), str) and fn["name"]:
                return fn["name"]
    return "fake_tool"


class _FakeHandler(BaseHTTPRequestHandler):
    server_version = "slaif-fake-upstream/0.1"
    sys_version = ""

    def log_message(self, *args: object) -> None:  # no raw payload logging
        return

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error_envelope(self, status: int, code: str) -> None:
        self._send_json(
            status,
            {
                "error": {
                    "message": "fake upstream bounded error",
                    "type": "invalid_request_error",
                    "code": code,
                }
            },
        )

    def do_GET(self) -> None:  # noqa: N802 - http.server API
        # Real HTTP servers match on the path, not the raw request target:
        # an empty query ("/v1/models?") is the same resource as "/v1/models".
        path = urlsplit(self.path).path
        if path == "/health":
            self._send_json(200, {"status": "ok"})
        elif path == "/v1/models":
            sentinel = self.server.sentinel  # type: ignore[attr-defined]
            self._send_json(
                200,
                {
                    "object": "list",
                    "data": [
                        {
                            "id": self.server.model,  # type: ignore[attr-defined]
                            "object": "model",
                            "created": 1,
                            "owned_by": "slaif-fake",
                            "root": f"SLAIF_FAKE_SENTINEL:{sentinel}",
                        }
                    ],
                },
            )
        else:
            self._send_error_envelope(404, "unknown_path")

    def do_POST(self) -> None:  # noqa: N802 - http.server API
        path = urlsplit(self.path).path
        if path != "/v1/chat/completions":
            self._send_error_envelope(404, "unknown_path")
            return
        try:
            length = int(self.headers.get("content-length", "0"))
        except ValueError:
            self._send_error_envelope(400, "invalid_request")
            return
        if length > MAX_BODY_BYTES:
            self._send_error_envelope(413, "request_too_large")
            return
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            request = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_error_envelope(400, "invalid_json")
            return
        if not isinstance(request, dict):
            self._send_error_envelope(400, "invalid_request")
            return
        sentinel = f"SLAIF_FAKE_SENTINEL:{self.server.sentinel}"  # type: ignore[attr-defined]
        model = self.server.model  # type: ignore[attr-defined]
        tool_roundtrip = (
            isinstance(request.get("tools"), list) and request.get("tool_choice", "auto") != "none"
        )
        has_tool_result = any(
            isinstance(m, dict) and m.get("role") == "tool"
            for m in request.get("messages", [])
            if isinstance(m, dict)
        )
        if request.get("stream") is True:
            self._send_sse(sentinel, model)
        elif tool_roundtrip and not has_tool_result:
            name = _tool_name(request)
            self._send_json(
                200,
                {
                    "id": "chatcmpl-fake-tool",
                    "object": "chat.completion",
                    "created": 1,
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "call_fake_1",
                                        "type": "function",
                                        "function": {
                                            "name": name,
                                            "arguments": json.dumps(
                                                {"item_id": sentinel},
                                                separators=(",", ":"),
                                            ),
                                        },
                                    }
                                ],
                            },
                            "finish_reason": "tool_calls",
                        }
                    ],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                },
            )
        else:
            self._send_json(
                200,
                {
                    "id": "chatcmpl-fake-text",
                    "object": "chat.completion",
                    "created": 1,
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": sentinel},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                },
            )

    def _send_sse(self, sentinel: str, model: str) -> None:
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.send_header("cache-control", "no-cache")
        self.end_headers()

        def frame(delta: dict[str, Any], finish: str | None) -> bytes:
            payload = {
                "id": "chatcmpl-fake-stream",
                "object": "chat.completion.chunk",
                "created": 1,
                "model": model,
                "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
            }
            return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n".encode()

        try:
            self.wfile.write(frame({"role": "assistant", "content": ""}, None))
            self.wfile.write(frame({"content": sentinel}, None))
            self.wfile.write(frame({}, "stop"))
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=18033)
    parser.add_argument("--model", default="qwen3.8-27b")
    parser.add_argument("--sentinel", required=True)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        print("fake upstream: port is invalid", file=sys.stderr)
        return 2
    if not isinstance(args.sentinel, str) or not 1 <= len(args.sentinel) <= 128:
        print("fake upstream: sentinel is invalid", file=sys.stderr)
        return 2

    server = ThreadingHTTPServer(("127.0.0.1", args.port), _FakeHandler)
    server.model = args.model  # type: ignore[attr-defined]
    server.sentinel = args.sentinel  # type: ignore[attr-defined]
    print(
        json.dumps(
            {
                "fake_upstream": "ready",
                "bind": "127.0.0.1",
                "port": args.port,
                "model": args.model,
                "sentinel_set": True,
            }
        ),
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
