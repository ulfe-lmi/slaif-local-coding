"""Simulated Gateway runtime signer client (order 011-a, workstream C5/C6).

Stdlib-only disposable client that stands in for the separate SLAIF API
Gateway's Local-Coding route runtime: it mints the accepted signed identity
v1 requests (service Bearer + HMAC-SHA256 over the exact canonical bytes,
nonce + timestamp, replay protection) and drives the bounded C5/C6 evidence
set against the containerized adapter and its fake upstream.

It is repository-only test tooling: excluded from both artifacts, never a
production component, and it never logs secret values — token and signing
secret values are read from environment variables by name only.

One operation per invocation; one bounded JSON fact line on stdout; exit 0
iff the operation's expectation held.

Operations:
  models             signed GET  /v1/models (expect 200 + model listed)
  chat               signed POST /v1/chat/completions non-stream
                     (expect 200 + sentinel in content)
  chat-stream        signed POST /v1/chat/completions stream:true
                     (expect 200 + SSE frames with sentinel + terminal [DONE])
  tool-roundtrip     signed tool-call request + signed continuation
                     (expect tool call with sentinel, then sentinel text)
  neg-cross-namespace   connect to the adapter's loopback address (expect a
                     connection failure: loopback does not cross namespaces)
  neg-missing-token     signed request without the Bearer credential
                     (expect 401)
  neg-bad-signature     tampered signature (expect 401 or 403)
  neg-replay            the same signed request twice (expect 409 replay)
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import socket
import sys
import time
import urllib.error
import urllib.request

MAX_RESPONSE_BYTES = 1_048_576


def _signed_headers(
    *,
    method: str,
    path: str,
    raw_query: bytes,
    body: bytes,
    principal: str,
    session: str,
    repository: str,
    route: str,
    secret: bytes,
    timestamp: str | None = None,
    nonce: str | None = None,
    tamper_signature: bool = False,
) -> dict[str, str]:
    """Exact v1 canonical-bytes signing (mirrors the adapter contract)."""
    timestamp = timestamp or str(int(time.time()))
    nonce = nonce or secrets.token_urlsafe(24)
    fields = (
        "slaif-local-coding-identity-v1",
        method,
        path,
        hashlib.sha256(raw_query).hexdigest(),
        hashlib.sha256(body).hexdigest(),
        principal,
        session,
        repository,
        route,
        timestamp,
        nonce,
    )
    canonical = "\n".join(fields).encode("utf-8")
    signature = "v1=" + hmac.new(secret, canonical, hashlib.sha256).hexdigest()
    if tamper_signature:
        signature = "v1=" + ("0" if signature[3] != "0" else "1") + signature[4:]
    return {
        "x-slaif-identity-version": "v1",
        "x-slaif-principal": principal,
        "x-slaif-session": session,
        "x-slaif-repository": repository,
        "x-slaif-route": route,
        "x-slaif-timestamp": timestamp,
        "x-slaif-nonce": nonce,
        "x-slaif-signature": signature,
    }


def _http(
    endpoint: str,
    method: str,
    path: str,
    *,
    headers: dict[str, str] | None,
    body: bytes | None,
) -> dict[str, object]:
    url = endpoint.rstrip("/") + path
    try:
        request = urllib.request.Request(url, data=body, method=method)
        for name, value in (headers or {}).items():
            request.add_header(name, value)
        if body is not None and not any(name.lower() == "content-type" for name in (headers or {})):
            request.add_header("content-type", "application/json")
        with urllib.request.urlopen(request, timeout=30) as response:
            status: int = response.status
            raw: bytes = response.read(MAX_RESPONSE_BYTES)
            ctype = response.headers.get("content-type", "")
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read(MAX_RESPONSE_BYTES)
        ctype = exc.headers.get("content-type", "") if exc.headers else ""
    except OSError as exc:
        return {"status": "connection_failed", "error_class": type(exc).__name__}
    parsed: object
    try:
        parsed = json.loads(raw.decode("utf-8")) if raw else None
    except (UnicodeDecodeError, json.JSONDecodeError):
        parsed = None
    return {
        "status": status,
        "content_type": ctype,
        "raw": raw,
        "json": parsed,
    }


def _sse_facts(raw: bytes) -> dict[str, object]:
    text = raw.decode("utf-8", "replace")
    lines = [line for line in text.splitlines() if line.startswith("data:")]
    content_parts: list[str] = []
    for line in lines:
        payload = line[len("data:") :].strip()
        if payload == "[DONE]":
            continue
        try:
            chunk = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if not isinstance(chunk, dict):
            continue
        for choice in chunk.get("choices", []):
            if not isinstance(choice, dict):
                continue
            delta = choice.get("delta", {})
            if isinstance(delta, dict) and isinstance(delta.get("content"), str):
                content_parts.append(delta["content"])
    return {
        "sse_frames": len(lines),
        "terminal_done": text.strip().endswith("data: [DONE]"),
        "streamed_content": "".join(content_parts),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--operation",
        required=True,
        choices=[
            "models",
            "chat",
            "chat-stream",
            "tool-roundtrip",
            "neg-cross-namespace",
            "neg-missing-token",
            "neg-bad-signature",
            "neg-replay",
        ],
    )
    parser.add_argument("--endpoint", required=True, help="e.g. http://172.17.0.1:18031")
    parser.add_argument("--service-token-env", default="SLAIF_SIM_SERVICE_TOKEN")
    parser.add_argument("--signing-secret-env", default="SLAIF_SIM_SIGNING_SECRET")
    parser.add_argument("--principal", default="sim-gateway-principal")
    parser.add_argument("--session", default="sim-session-011")
    parser.add_argument("--repository", default="sim-repository-011")
    parser.add_argument("--route", default="qwen38-vision-codex")
    parser.add_argument("--model", default="qwen3.8-27b")
    parser.add_argument("--expect-sentinel", default="")
    args = parser.parse_args()

    token = os.environ.get(args.service_token_env, "")
    secret = os.environ.get(args.signing_secret_env, "")
    operation = args.operation
    if operation != "neg-cross-namespace" and (not token or not secret):
        print(
            json.dumps(
                {"operation": operation, "ok": False, "class": "sim_credentials_unavailable"}
            )
        )
        return 2

    identity = {
        "principal": args.principal,
        "session": args.session,
        "repository": args.repository,
        "route": args.route,
        "secret": secret.encode("ascii"),
    }

    ok = False
    detail: dict[str, object] = {}

    if operation == "models":
        headers = _signed_headers(
            method="GET", path="/v1/models", raw_query=b"", body=b"", **identity
        )
        headers["authorization"] = f"Bearer {token}"
        facts = _http(args.endpoint, "GET", "/v1/models", headers=headers, body=None)
        payload = facts.get("json")
        models = payload.get("data", []) if isinstance(payload, dict) else []
        ok = (
            facts.get("status") == 200
            and isinstance(models, list)
            and any(isinstance(m, dict) and m.get("id") == args.model for m in models)
        )
        detail = {"status": facts.get("status"), "model_listed": ok}
    elif operation == "chat":
        body = json.dumps(
            {
                "model": args.model,
                "messages": [{"role": "user", "content": "bounded synthetic ping"}],
                "stream": False,
            },
            separators=(",", ":"),
        ).encode("utf-8")
        headers = _signed_headers(
            method="POST", path="/v1/chat/completions", raw_query=b"", body=body, **identity
        )
        headers["authorization"] = f"Bearer {token}"
        facts = _http(args.endpoint, "POST", "/v1/chat/completions", headers=headers, body=body)
        payload = facts.get("json")
        content = ""
        if isinstance(payload, dict):
            choices = payload.get("choices")
            if isinstance(choices, list) and choices and isinstance(choices[0], dict):
                message = choices[0].get("message", {})
                if isinstance(message, dict) and isinstance(message.get("content"), str):
                    content = message["content"]
        ok = facts.get("status") == 200 and args.expect_sentinel in content
        detail = {"status": facts.get("status"), "sentinel_match": ok}
    elif operation == "chat-stream":
        body = json.dumps(
            {
                "model": args.model,
                "messages": [{"role": "user", "content": "bounded synthetic ping"}],
                "stream": True,
            },
            separators=(",", ":"),
        ).encode("utf-8")
        headers = _signed_headers(
            method="POST", path="/v1/chat/completions", raw_query=b"", body=body, **identity
        )
        headers["authorization"] = f"Bearer {token}"
        facts = _http(args.endpoint, "POST", "/v1/chat/completions", headers=headers, body=body)
        sse = _sse_facts(bytes(facts.get("raw", b"")))
        ok = (
            facts.get("status") == 200
            and sse["sse_frames"] >= 2
            and sse["terminal_done"] is True
            and args.expect_sentinel in sse["streamed_content"]
        )
        detail = {"status": facts.get("status"), **sse, "sentinel_match": ok}
    elif operation == "tool-roundtrip":
        tool_body = json.dumps(
            {
                "model": args.model,
                "messages": [{"role": "user", "content": "bounded synthetic tool ping"}],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "fake_item_lookup",
                            "description": "bounded synthetic tool",
                            "parameters": {
                                "type": "object",
                                "properties": {"item_id": {"type": "string"}},
                            },
                        },
                    }
                ],
                "tool_choice": "required",
            },
            separators=(",", ":"),
        ).encode("utf-8")
        headers = _signed_headers(
            method="POST", path="/v1/chat/completions", raw_query=b"", body=tool_body, **identity
        )
        headers["authorization"] = f"Bearer {token}"
        first = _http(
            args.endpoint, "POST", "/v1/chat/completions", headers=headers, body=tool_body
        )
        payload = first.get("json")
        call_id = ""
        call_name = ""
        arguments = ""
        if isinstance(payload, dict):
            choices = payload.get("choices")
            if isinstance(choices, list) and choices and isinstance(choices[0], dict):
                message = choices[0].get("message", {})
                if isinstance(message, dict):
                    for call in message.get("tool_calls", []):
                        if isinstance(call, dict):
                            call_id = str(call.get("id", ""))
                            fn = call.get("function", {})
                            if isinstance(fn, dict):
                                call_name = str(fn.get("name", ""))
                                arguments = str(fn.get("arguments", ""))
        first_ok = (
            first.get("status") == 200
            and call_id
            and call_name == "fake_item_lookup"
            and args.expect_sentinel in arguments
        )
        if not first_ok:
            ok = False
            detail = {
                "phase": "tool_call",
                "status": first.get("status"),
                "sentinel_in_arguments": first_ok,
            }
        else:
            continuation_body = json.dumps(
                {
                    "model": args.model,
                    "messages": [
                        {"role": "user", "content": "bounded synthetic tool ping"},
                        {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": call_id,
                                    "type": "function",
                                    "function": {
                                        "name": call_name,
                                        "arguments": arguments,
                                    },
                                }
                            ],
                        },
                        {
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": "bounded synthetic tool result",
                        },
                    ],
                },
                separators=(",", ":"),
            ).encode("utf-8")
            headers2 = _signed_headers(
                method="POST",
                path="/v1/chat/completions",
                raw_query=b"",
                body=continuation_body,
                **identity,
            )
            headers2["authorization"] = f"Bearer {token}"
            second = _http(
                args.endpoint,
                "POST",
                "/v1/chat/completions",
                headers=headers2,
                body=continuation_body,
            )
            payload2 = second.get("json")
            content = ""
            if isinstance(payload2, dict):
                choices = payload2.get("choices")
                if isinstance(choices, list) and choices and isinstance(choices[0], dict):
                    message = choices[0].get("message", {})
                    if isinstance(message, dict) and isinstance(message.get("content"), str):
                        content = message["content"]
            ok = second.get("status") == 200 and args.expect_sentinel in content
            detail = {
                "phase": "continuation",
                "status": second.get("status"),
                "sentinel_match": ok,
            }
    elif operation == "neg-cross-namespace":
        host, _, port = args.endpoint.partition(":")
        if host.startswith("http://"):
            host = host[len("http://") :]
        host, _, port = host.partition(":")
        try:
            with socket.create_connection((host or "127.0.0.1", int(port or "18031")), timeout=5):
                ok = False
                detail = {"class": "unexpectedly_reachable"}
        except OSError as exc:
            ok = True
            detail = {"class": type(exc).__name__}
    elif operation == "neg-missing-token":
        body = json.dumps(
            {"model": args.model, "messages": [{"role": "user", "content": "neg"}]},
            separators=(",", ":"),
        ).encode("utf-8")
        headers = _signed_headers(
            method="POST", path="/v1/chat/completions", raw_query=b"", body=body, **identity
        )
        # deliberately no authorization header
        facts = _http(args.endpoint, "POST", "/v1/chat/completions", headers=headers, body=body)
        ok = facts.get("status") == 401
        detail = {"status": facts.get("status")}
    elif operation == "neg-bad-signature":
        body = json.dumps(
            {"model": args.model, "messages": [{"role": "user", "content": "neg"}]},
            separators=(",", ":"),
        ).encode("utf-8")
        headers = _signed_headers(
            method="POST",
            path="/v1/chat/completions",
            raw_query=b"",
            body=body,
            tamper_signature=True,
            **identity,
        )
        headers["authorization"] = f"Bearer {token}"
        facts = _http(args.endpoint, "POST", "/v1/chat/completions", headers=headers, body=body)
        ok = facts.get("status") in {401, 403}
        detail = {"status": facts.get("status")}
    elif operation == "neg-replay":
        body = json.dumps(
            {"model": args.model, "messages": [{"role": "user", "content": "neg-replay"}]},
            separators=(",", ":"),
        ).encode("utf-8")
        fixed = {"timestamp": str(int(time.time())), "nonce": secrets.token_urlsafe(24)}
        headers = _signed_headers(
            method="POST",
            path="/v1/chat/completions",
            raw_query=b"",
            body=body,
            tamper_signature=False,
            **identity,
            **fixed,
        )
        headers["authorization"] = f"Bearer {token}"
        first = _http(args.endpoint, "POST", "/v1/chat/completions", headers=headers, body=body)
        second = _http(args.endpoint, "POST", "/v1/chat/completions", headers=headers, body=body)
        ok = first.get("status") == 200 and second.get("status") == 409
        detail = {"first_status": first.get("status"), "second_status": second.get("status")}

    print(json.dumps({"operation": operation, "ok": ok, **detail}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
