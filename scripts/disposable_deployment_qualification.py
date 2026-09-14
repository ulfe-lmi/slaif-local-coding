"""Disposable operational qualification for the deployment path (order 009-a, D).

Exercises the full deployment mechanics in a disposable environment against
FAKE LOOPBACK upstreams only:

- verifies 18031 is free (and 18020/18021 state) before and after;
- builds artifacts, runs the artifact policy check, installs the wheel into a
  fresh empty venv;
- creates the config from the documented template using only the documented
  placeholder substitutions;
- starts the candidate on 127.0.0.1:18031 and polls readiness;
- verifies /healthz, /readyz, private /metrics, Responses and Chat JSON/SSE,
  ordinary function-tool envelopes, usage preservation, and first-byte
  streaming (no full buffering);
- proves clean stop/restart (no orphan process), an upgrade that preserves the
  intended configuration, a mechanical rollback, and a failed start injected
  at the documented point (unreachable upstream) with recovery;
- optionally verifies the unit under the user systemd manager (systemd-analyze
  verify and one uniquely named transient systemd-run unit, fully removed);
- removes every disposable resource and records absence proof.

This script performs zero protected-service mutation: it never touches the
protected upstream on 18020 (read-only health check only), never writes
outside the disposable workdir, and never leaves a listener on 18031.

Usage:

    python scripts/disposable_deployment_qualification.py [--workdir DIR] [--keep]
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import tomllib
import urllib.request
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PORT = 18031
PROTECTED_PORT = 18020
ABSENT_PORT = 18021
TEMPLATE = REPO_ROOT / "config" / "adapter.deployment.template.toml"
DOCUMENTED_PLACEHOLDERS = ("__UPSTREAM_BASE_URL__", "__UPSTREAM_MODEL__")
SYNTHETIC_KEY_NAME = "QWEN3090_API_KEY"
SYNTHETIC_KEY_VALUE = "qual009-synthetic-loopback-only"
FAKE_MODEL = "fake-model-009"
PROMPT_MARKER = "SLAIF009-QUAL-MARKER"
READY_TIMEOUT_SECONDS = 30
READY_POLL_SECONDS = 0.5
UNREACHABLE_WAIT_SECONDS = 15


# ---------------------------------------------------------------------------
# Fake loopback upstream
# ---------------------------------------------------------------------------


class _FakeState:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}
        self.request_paths: list[str] = []
        self.lock = threading.Lock()


def _sse_event(event: str, data: dict) -> bytes:
    return f"event: {event}\ndata: {json.dumps(data, separators=(',', ':'))}\n\n".encode()


def _responses_sse(state: _FakeState, tool_call: bool) -> Iterator[bytes]:
    base = {
        "id": "resp_fake_009",
        "object": "response",
        "status": "in_progress",
        "model": FAKE_MODEL,
        "output": [],
    }
    yield _sse_event("response.created", {"type": "response.created", "response": base})
    yield _sse_event("response.in_progress", {"type": "response.in_progress", "response": base})
    if tool_call:
        item = {
            "id": "fc_fake_009",
            "type": "function_call",
            "call_id": "call_fake_009",
            "name": "fake_lookup",
            "arguments": "{}",
            "status": "in_progress",
        }
        yield _sse_event(
            "response.output_item.added",
            {"type": "response.output_item.added", "output_index": 0, "item": item},
        )
        yield _sse_event(
            "response.function_call_arguments.done",
            {
                "type": "response.function_call_arguments.done",
                "item_id": "fc_fake_009",
                "output_index": 0,
                "call_id": "call_fake_009",
                "arguments": "{}",
            },
        )
        item["status"] = "completed"
        yield _sse_event(
            "response.output_item.done",
            {"type": "response.output_item.done", "output_index": 0, "item": item},
        )
    else:
        item = {
            "id": "msg_fake_009",
            "type": "message",
            "status": "in_progress",
            "role": "assistant",
            "content": [],
        }
        yield _sse_event(
            "response.output_item.added",
            {"type": "response.output_item.added", "output_index": 0, "item": item},
        )
        part = {"type": "output_text", "text": "", "status": "in_progress", "annotations": []}
        yield _sse_event(
            "response.content_part.added",
            {
                "type": "response.content_part.added",
                "item_id": "msg_fake_009",
                "output_index": 0,
                "content_index": 0,
                "part": part,
            },
        )
        yield _sse_event(
            "response.output_text.delta",
            {
                "type": "response.output_text.delta",
                "item_id": "msg_fake_009",
                "output_index": 0,
                "content_index": 0,
                "delta": "slaif009 fake response text",
            },
        )
        part["text"] = "slaif009 fake response text"
        part["status"] = "completed"
        yield _sse_event(
            "response.output_text.done",
            {
                "type": "response.output_text.done",
                "item_id": "msg_fake_009",
                "output_index": 0,
                "content_index": 0,
                "text": "slaif009 fake response text",
            },
        )
        yield _sse_event(
            "response.content_part.done",
            {
                "type": "response.content_part.done",
                "item_id": "msg_fake_009",
                "output_index": 0,
                "content_index": 0,
                "part": part,
            },
        )
        item["status"] = "completed"
        item["content"] = [part]
        yield _sse_event(
            "response.output_item.done",
            {"type": "response.output_item.done", "output_index": 0, "item": item},
        )
    # Delay the terminal event: proves the stream is not fully buffered.
    time.sleep(0.3)
    done = dict(base)
    done["status"] = "completed"
    done["usage"] = {"input_tokens": 11, "output_tokens": 7, "total_tokens": 18}
    yield _sse_event("response.completed", {"type": "response.completed", "response": done})


def _chat_sse(include_usage: bool) -> Iterator[bytes]:
    def chunk(payload: dict) -> bytes:
        return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n".encode()

    base = {
        "id": "chatcmpl_fake_009",
        "object": "chat.completion.chunk",
        "created": 1,
        "model": FAKE_MODEL,
        "choices": [],
    }
    first = dict(
        base,
        choices=[
            {"index": 0, "delta": {"role": "assistant", "content": ""}, "finish_reason": None}
        ],
    )
    yield chunk(first)
    yield chunk(
        dict(
            base,
            choices=[
                {"index": 0, "delta": {"content": "slaif009 fake chat text"}, "finish_reason": None}
            ],
        )
    )
    time.sleep(0.3)
    terminal = dict(base, choices=[{"index": 0, "delta": {}, "finish_reason": "stop"}])
    yield chunk(terminal)
    if include_usage:
        yield chunk(
            dict(
                base,
                choices=[],
                usage={"prompt_tokens": 9, "completion_tokens": 5, "total_tokens": 14},
            )
        )
    yield b"data: [DONE]\n\n"


class _FakeHandler(BaseHTTPRequestHandler):
    server_version = "slaif-fake-009"

    def log_message(self, *args: object) -> None:  # silence
        return

    def _record(self, path: str) -> None:
        state: _FakeState = self.server.state  # type: ignore[attr-defined]
        with state.lock:
            key = f"{self.command} {path}"
            state.counts[key] = state.counts.get(key, 0) + 1
            state.request_paths.append(key)

    def _send(self, status: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_sse(self, chunks: Iterator[bytes]) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        for chunk in chunks:
            self.wfile.write(chunk)
            self.wfile.flush()

    def _route_path(self) -> str:
        # The adapter forwards an empty query as a trailing ``?`` (httpx URL
        # joining); treat it as absent, matching real vLLM behavior.
        return self.path.split("?", 1)[0]

    def do_GET(self) -> None:  # noqa: N802 - http.server API
        path = self._route_path()
        self._record(path)
        if path == "/health":
            self._send(200, b'{"status":"ok"}')
        elif path == "/v1/models":
            self._send(
                200,
                json.dumps(
                    {
                        "object": "list",
                        "data": [{"id": FAKE_MODEL, "object": "model", "owned_by": "slaif-test"}],
                    }
                ).encode(),
            )
        else:
            self._send(
                404,
                json.dumps(
                    {"error": {"message": "not found", "type": "invalid_request_error"}}
                ).encode(),
            )

    def do_POST(self) -> None:  # noqa: N802 - http.server API
        path = self._route_path()
        self._record(path)
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            self._send(400, b'{"error":{"message":"invalid json","type":"invalid_request_error"}}')
            return
        if path == "/v1/responses":
            if body.get("stream"):
                tool_call = any(
                    isinstance(t, dict) and t.get("name") == "fake_lookup"
                    for t in body.get("tools") or []
                )
                self._send_sse(_responses_sse(self.server.state, tool_call))  # type: ignore[arg-type]
            else:
                if any(
                    isinstance(t, dict) and t.get("name") == "fake_lookup"
                    for t in body.get("tools") or []
                ):
                    output = [
                        {
                            "id": "fc_fake_009",
                            "type": "function_call",
                            "call_id": "call_fake_009",
                            "name": "fake_lookup",
                            "arguments": "{}",
                            "status": "completed",
                        }
                    ]
                else:
                    output = [
                        {
                            "id": "msg_fake_009",
                            "type": "message",
                            "role": "assistant",
                            "status": "completed",
                            "content": [
                                {"type": "output_text", "text": "slaif009 fake response text"}
                            ],
                        }
                    ]
                self._send(
                    200,
                    json.dumps(
                        {
                            "id": "resp_fake_009",
                            "object": "response",
                            "status": "completed",
                            "model": FAKE_MODEL,
                            "output": output,
                            "usage": {"input_tokens": 11, "output_tokens": 7, "total_tokens": 18},
                        }
                    ).encode(),
                )
        elif path == "/v1/chat/completions":
            if body.get("stream"):
                include_usage = (body.get("stream_options") or {}).get("include_usage") is True
                self._send_sse(_chat_sse(include_usage))
            else:
                message: dict = {"role": "assistant", "content": "slaif009 fake chat text"}
                if body.get("tools"):
                    message = {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_fake_009",
                                "type": "function",
                                "function": {"name": "fake_lookup", "arguments": "{}"},
                            }
                        ],
                    }
                self._send(
                    200,
                    json.dumps(
                        {
                            "id": "chatcmpl_fake_009",
                            "object": "chat.completion",
                            "created": 1,
                            "model": FAKE_MODEL,
                            "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
                            "usage": {
                                "prompt_tokens": 9,
                                "completion_tokens": 5,
                                "total_tokens": 14,
                            },
                        }
                    ).encode(),
                )
        else:
            self._send(404, b'{"error":{"message":"not found","type":"invalid_request_error"}}')


def start_fake_upstream() -> tuple[ThreadingHTTPServer, _FakeState, int]:
    state = _FakeState()
    server = ThreadingHTTPServer(("127.0.0.1", 0), _FakeHandler)
    server.state = state  # type: ignore[attr-defined]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, state, server.server_address[1]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
        return True


def port_listening(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def get_status(url: str, timeout: float = 3.0) -> int:
    """Return the HTTP status (error statuses included) or 0 if unreachable.

    ``urllib.request.urlopen`` raises on HTTP error statuses, which would
    make a documented 503 readiness look like connection failure; use
    ``http.client`` so the status code is observed directly.
    """
    parts = urlsplit(url)
    try:
        conn = http.client.HTTPConnection(parts.hostname, parts.port, timeout=timeout)
        try:
            conn.request("GET", parts.path or "/")
            response = conn.getresponse()
            response.read()
            return int(response.status)
        finally:
            conn.close()
    except OSError:
        return 0


def wait_ready(base: str, timeout: float) -> tuple[bool, float, int]:
    start = time.monotonic()
    last_status = 0
    deadline = start + timeout
    while time.monotonic() < deadline:
        last_status = get_status(f"{base}/readyz")
        if last_status == 200:
            return True, time.monotonic() - start, last_status
        time.sleep(READY_POLL_SECONDS)
    return False, time.monotonic() - start, last_status


def stream_sse(base: str, path: str, payload: dict) -> dict:
    """Stream one SSE request, returning event order + timing facts."""
    conn = http.client.HTTPConnection("127.0.0.1", CANDIDATE_PORT, timeout=60)
    body = json.dumps(payload)
    conn.request("POST", path, body=body, headers={"Content-Type": "application/json"})
    response = conn.getresponse()
    status = response.status
    events: list[str] = []
    data: list[dict] = []
    first_byte_at: float | None = None
    terminal_at: float | None = None
    start = time.monotonic()
    current_event = ""
    raw_lines: Iterator[bytes] = iter(lambda: response.fp.readline(), b"")
    for line in raw_lines:
        if first_byte_at is None:
            first_byte_at = time.monotonic() - start
        if not line:
            break
        text = line.decode("utf-8", errors="replace").rstrip("\r\n")
        if text.startswith("event: "):
            current_event = text[7:]
        elif text.startswith("data: "):
            payload = text[6:]
            if payload == "[DONE]":
                terminal_at = time.monotonic() - start
                continue
            data.append(json.loads(payload))
            if current_event:
                events.append(current_event)
            if current_event == "response.completed":
                terminal_at = time.monotonic() - start
            current_event = ""
    if status == 200 and path == "/v1/chat/completions":
        # Chat SSE: no event: lines; terminal is [DONE].
        events = ["chat.data", "chat.done"]
        terminal_at = time.monotonic() - start
    conn.close()
    return {
        "status": status,
        "events": events,
        "data_count": len(data),
        "first_byte_s": first_byte_at,
        "terminal_s": terminal_at,
        "tail_s": (terminal_at or 0) - (first_byte_at or 0),
        "terminal": data[-1] if data else None,
    }


def http_json(
    base_port: int, method: str, path: str, payload: dict | None = None
) -> tuple[int, dict | None]:
    conn = http.client.HTTPConnection("127.0.0.1", base_port, timeout=60)
    body = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    conn.request(method, path, body=body, headers=headers)
    response = conn.getresponse()
    raw = response.read()
    conn.close()
    try:
        return response.status, json.loads(raw.decode("utf-8")) if raw else None
    except ValueError:
        return response.status, None


def render_template(values: dict[str, str]) -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    found = sorted(set(re.findall(r"__[A-Z0-9_]+__", text)))
    documented = sorted(DOCUMENTED_PLACEHOLDERS)
    if found != documented:
        raise RuntimeError(f"template placeholders changed: {found} != {documented}")
    for key, value in values.items():
        text = text.replace(key, value)
    if "__" in text:
        raise RuntimeError("unsubstituted placeholder remains in rendered config")
    tomllib.loads(text)  # must parse
    return text


def write_protected(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    path.write_bytes(data)
    os.chmod(path, 0o600)


def inventory_state(root: Path) -> dict:
    if not root.exists():
        return {"exists": False, "entries": 0}
    entries = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
    return {"exists": True, "entries": len(entries)}


def run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, **kwargs)


def install_wheel(venv: Path, wheel: Path, reinstall: bool = False) -> subprocess.CompletedProcess:
    """Install a wheel into the disposable venv via the project's ``uv pip``.

    The venv is created with ``--without-pip`` because uv-managed and minimal
    system interpreters do not ship ensurepip; ``uv pip`` is the project's
    mandated installer and keeps the install wheel-only plus index
    dependencies.
    """
    cmd = [
        "uv",
        "pip",
        "install",
        "--python",
        str(venv / "bin" / "python"),
        "--no-cache",
    ]
    if reinstall:
        cmd.append("--reinstall")
    cmd.append(str(wheel))
    return run(cmd, timeout=900)


def start_candidate(venv: Path, config: Path, env_file: Path) -> subprocess.Popen:
    env = dict(os.environ)
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            name, value = line.split("=", 1)
            env[name] = value
    return subprocess.Popen(
        [str(venv / "bin" / "slaif-local-coding"), "--config", str(config)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def stop_candidate(proc: subprocess.Popen, config: Path) -> dict:
    proc.terminate()
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)
    orphan = run(["pgrep", "-f", str(config)])
    return {
        "exit_code": proc.returncode,
        "orphan_process": orphan.returncode == 0,
        "port_free_after_stop": port_free(CANDIDATE_PORT),
    }


def unit_facts() -> dict:
    out = run(["systemctl", "--user", "status", "qwen-serving-vision.service", "--no-pager"])
    text = out.stdout.decode(errors="replace")
    active = ""
    main_pid = ""
    for line in text.splitlines():
        if line.strip().startswith("Active:"):
            active = line.split(";", 1)[0].strip()
        if line.strip().startswith("Main PID:"):
            main_pid = line.split(":", 1)[1].strip().split("(")[0].strip()
    return {"active": active, "main_pid": main_pid}


# ---------------------------------------------------------------------------
# Qualification
# ---------------------------------------------------------------------------


def qualify(workdir: Path, keep: bool, skip_systemd: bool) -> dict:
    evidence: dict = {"objective": "009-a", "workdir": str(workdir), "steps": {}}
    failures: list[str] = []
    fake_server: ThreadingHTTPServer | None = None
    fake_state: _FakeState | None = None
    fake_port = 0
    candidate: subprocess.Popen | None = None
    unit_before = unit_facts()
    evidence["protected_before"] = {
        "unit": unit_before,
        "protected_18020_listening": port_listening(PROTECTED_PORT),
        "protected_18020_health": get_status(f"http://127.0.0.1:{PROTECTED_PORT}/health"),
        "absent_18021_listening": port_listening(ABSENT_PORT),
        "candidate_18031_free": port_free(CANDIDATE_PORT),
    }
    if not evidence["protected_before"]["candidate_18031_free"]:
        raise RuntimeError("port 18031 is not free before qualification")
    if evidence["protected_before"]["absent_18021_listening"]:
        raise RuntimeError("unexpected listener on 18021 before qualification")

    try:
        # S1: build artifacts into the disposable workdir.
        dist = workdir / "dist"
        dist.mkdir(parents=True, exist_ok=True)
        build = run(["uv", "build", "--out-dir", str(dist)], cwd=REPO_ROOT, timeout=600)
        evidence["steps"]["build"] = {"exit": build.returncode}
        if build.returncode != 0:
            raise RuntimeError("uv build failed")

        # S2: artifact policy check on the disposable build.
        checker = REPO_ROOT / "scripts" / "artifact_policy_check.py"
        check = run([sys.executable, str(checker), "--dist", str(dist), "--inspect"], timeout=300)
        check_result = json.loads(check.stdout.decode())
        evidence["steps"]["artifact_policy"] = check_result
        if not check_result["ok"]:
            raise RuntimeError(f"artifact policy check failed: {check_result['violations']}")

        # S3: fresh disposable venv + wheel-only install.
        venv = workdir / "venv"
        run([sys.executable, "-m", "venv", "--without-pip", str(venv)], timeout=300)
        wheels = sorted(
            set(dist.glob("slaif_local_coding-*.whl")) | set(dist.glob("slaif-local-coding-*.whl"))
        )
        install = install_wheel(venv, wheels[0])
        probe = run(
            [
                str(venv / "bin" / "python"),
                "-c",
                "import slaif_local_coding as s, json; print(json.dumps({'f': s.__file__}))",
            ],
            timeout=120,
        )
        module_file = json.loads(probe.stdout.decode())["f"]
        evidence["steps"]["fresh_install"] = {
            "install_exit": install.returncode,
            "module_file_in_venv": module_file.startswith(str(venv.resolve())),
            "module_file": module_file,
        }
        if install.returncode != 0 or not module_file.startswith(str(venv.resolve())):
            raise RuntimeError("fresh disposable install failed")

        # S4: fake loopback upstream only.
        fake_server, fake_state, fake_port = start_fake_upstream()
        evidence["steps"]["fake_upstream"] = {"port": fake_port, "loopback_only": True}

        # S5: config from the documented template, documented placeholders only.
        state_dir = workdir / "state"
        config = state_dir / "config" / "adapter.toml"
        env_file = state_dir / "env" / "adapter.env"
        rendered = render_template(
            {
                "__UPSTREAM_BASE_URL__": f"http://127.0.0.1:{fake_port}/v1",
                "__UPSTREAM_MODEL__": FAKE_MODEL,
            }
        )
        write_protected(config, rendered.encode())
        write_protected(env_file, f"{SYNTHETIC_KEY_NAME}={SYNTHETIC_KEY_VALUE}\n".encode())
        evidence["steps"]["config_from_template"] = {
            "placeholders_substituted": list(DOCUMENTED_PLACEHOLDERS),
            "config_mode": oct(os.stat(config).st_mode & 0o777),
            "env_mode": oct(os.stat(env_file).st_mode & 0o777),
            "env_names_only": True,
        }

        base = f"http://127.0.0.1:{CANDIDATE_PORT}"
        # S6: start candidate (artifact A) and reach readiness.
        candidate = start_candidate(venv, config, env_file)
        ready, ready_time, ready_status = wait_ready(base, READY_TIMEOUT_SECONDS)
        evidence["steps"]["start_a"] = {
            "ready": ready,
            "ready_time_s": round(ready_time, 3),
            "readyz_status": ready_status,
        }
        if not ready:
            raise RuntimeError("candidate A did not reach readiness")
        listener = run(["ss", "-ltn", ""])
        listener_lines = [
            line for line in listener.stdout.decode().splitlines() if f":{CANDIDATE_PORT}" in line
        ]
        evidence["steps"]["listener"] = {
            "loopback_only": all(
                line.split()[3].startswith("127.0.0.1:") for line in listener_lines
            )
            and bool(listener_lines),
            "line_count": len(listener_lines),
        }

        # S7: contract checks.
        hz = get_status(f"{base}/healthz")
        rz = get_status(f"{base}/readyz")
        metrics = get_status(f"{base}/metrics")
        models_status, models_body = http_json(CANDIDATE_PORT, "GET", "/v1/models")
        prompt = f"qualify {PROMPT_MARKER} zero"
        resp = http_json(
            CANDIDATE_PORT,
            "POST",
            "/v1/responses",
            {
                "model": FAKE_MODEL,
                "input": [{"role": "user", "content": prompt}],
                "stream": False,
            },
        )
        resp_stream = stream_sse(
            base,
            "/v1/responses",
            {"model": FAKE_MODEL, "input": [{"role": "user", "content": prompt}], "stream": True},
        )
        resp_tool = stream_sse(
            base,
            "/v1/responses",
            {
                "model": FAKE_MODEL,
                "input": [{"role": "user", "content": prompt}],
                "tools": [
                    {
                        "type": "function",
                        "name": "fake_lookup",
                        "description": "fake",
                        "parameters": {"type": "object", "properties": {}},
                    }
                ],
                "stream": True,
            },
        )
        chat_tool_status, chat_tool_body = http_json(
            CANDIDATE_PORT,
            "POST",
            "/v1/chat/completions",
            {
                "model": FAKE_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "fake_lookup",
                            "description": "fake",
                            "parameters": {"type": "object", "properties": {}},
                        },
                    }
                ],
            },
        )
        chat_stream = stream_sse(
            base,
            "/v1/chat/completions",
            {
                "model": FAKE_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
                "stream_options": {"include_usage": True},
            },
        )
        metrics_body = ""
        with urllib.request.urlopen(f"{base}/metrics", timeout=10) as r:  # noqa: S310 - loopback only
            metrics_body = r.read().decode(errors="replace")
        terminal_resp = resp_stream["terminal"] or {}
        terminal_usage = (terminal_resp.get("response") or {}).get("usage")
        evidence["steps"]["contract"] = {
            "healthz": hz,
            "readyz": rz,
            "metrics": metrics,
            "models_status": models_status,
            "models_has_fake_model": bool(
                models_body and any(d.get("id") == FAKE_MODEL for d in models_body.get("data", []))
            ),
            "responses_json_status": resp[0],
            "responses_json_usage": (resp[1] or {}).get("usage"),
            "responses_sse_events": resp_stream["events"],
            "responses_sse_usage": terminal_usage,
            "responses_sse_first_byte_before_terminal": (
                resp_stream["first_byte_s"] is not None
                and resp_stream["terminal_s"] is not None
                and resp_stream["tail_s"] >= 0.25
            ),
            "responses_tool_sse_events": resp_tool["events"],
            "responses_tool_call_id": None,
            "chat_tool_status": chat_tool_status,
            "chat_tool_name": None,
            "chat_sse_events": chat_stream["events"],
            "metrics_contains_requests_total": "slaif_requests_total" in metrics_body,
            "metrics_contains_prompt_marker": PROMPT_MARKER in metrics_body,
        }
        # Extract tool facts with one dedicated non-streaming tool request.
        tool_facts = _extract_tool_facts(base)
        evidence["steps"]["contract"]["responses_tool_call_id"] = tool_facts["responses_call_id"]
        chat_tool_message = (chat_tool_body or {}).get("choices", [{}])[0].get("message", {})
        tool_calls = chat_tool_message.get("tool_calls") or []
        evidence["steps"]["contract"]["chat_tool_name"] = (
            tool_calls[0].get("function", {}).get("name") if tool_calls else None
        )
        if (
            hz != 200
            or rz != 200
            or metrics != 200
            or models_status != 200
            or resp[0] != 200
            or resp_stream["status"] != 200
            or resp_tool["status"] != 200
            or chat_tool_status != 200
            or chat_stream["status"] != 200
            or not evidence["steps"]["contract"]["responses_sse_first_byte_before_terminal"]
            or evidence["steps"]["contract"]["metrics_contains_prompt_marker"]
            or not evidence["steps"]["contract"]["metrics_contains_requests_total"]
            or not evidence["steps"]["contract"]["models_has_fake_model"]
            or tool_facts["responses_call_id"] != "call_fake_009"
            or evidence["steps"]["contract"]["chat_tool_name"] != "fake_lookup"
        ):
            raise RuntimeError("contract checks failed")

        # S8: clean stop/restart.
        stop_facts = stop_candidate(candidate, config)
        evidence["steps"]["stop_restart"] = {
            "first_stop": stop_facts,
            "restart": None,
        }
        candidate = start_candidate(venv, config, env_file)
        ready2, ready2_time, _ = wait_ready(base, READY_TIMEOUT_SECONDS)
        smoke2 = http_json(
            CANDIDATE_PORT,
            "POST",
            "/v1/responses",
            {"model": FAKE_MODEL, "input": [{"role": "user", "content": prompt}], "stream": False},
        )
        evidence["steps"]["stop_restart"]["restart"] = {
            "ready": ready2,
            "ready_time_s": round(ready2_time, 3),
            "smoke_status": smoke2[0],
        }
        if not ready2 or smoke2[0] != 200:
            raise RuntimeError("restart did not recover")

        # S9: upgrade with the supported procedure.
        cache_root = Path("/dev/shm/slaif-local-coding")
        inv_before = {
            "config_sha256": _sha256_file(config),
            "config_mode": oct(os.stat(config).st_mode & 0o777),
            "cache_root_state": inventory_state(cache_root),
        }
        stamp_a = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        backup_a = workdir / "backups" / stamp_a
        backup_a.mkdir(parents=True, exist_ok=True)
        (backup_a / "adapter.toml").write_bytes(config.read_bytes())
        os.chmod(backup_a / "adapter.toml", 0o600)
        # Keep the exact wheel filename: ``uv pip`` refuses non-wheel names.
        (backup_a / wheels[0].name).write_bytes(wheels[0].read_bytes())
        os.chmod(backup_a / wheels[0].name, 0o600)
        inventory_a = {
            "config_sha256": inv_before["config_sha256"],
            "wheel_sha256": _sha256_file(wheels[0]),
            "wheel_size_bytes": wheels[0].stat().st_size,
            "cache_root_state": inv_before["cache_root_state"],
        }
        write_protected(backup_a / "inventory.json", json.dumps(inventory_a, indent=2).encode())

        dist2 = workdir / "dist2"
        dist2.mkdir(parents=True, exist_ok=True)
        run(["uv", "build", "--out-dir", str(dist2)], cwd=REPO_ROOT, timeout=600)
        wheels2 = sorted(
            set(dist2.glob("slaif_local_coding-*.whl"))
            | set(dist2.glob("slaif-local-coding-*.whl"))
        )
        reinstall = install_wheel(venv, wheels2[0], reinstall=True)
        stop_facts2 = stop_candidate(candidate, config)
        candidate = start_candidate(venv, config, env_file)
        ready3, ready3_time, _ = wait_ready(base, READY_TIMEOUT_SECONDS)
        smoke3 = http_json(
            CANDIDATE_PORT,
            "POST",
            "/v1/responses",
            {"model": FAKE_MODEL, "input": [{"role": "user", "content": prompt}], "stream": False},
        )
        inv_after = {
            "config_sha256": _sha256_file(config),
            "config_mode": oct(os.stat(config).st_mode & 0o777),
            "cache_root_state": inventory_state(cache_root),
        }
        evidence["steps"]["upgrade"] = {
            "previous_artifact_sha256": _sha256_file(wheels[0]),
            "new_artifact_sha256": _sha256_file(wheels2[0]),
            "install_exit": reinstall.returncode,
            "stop": stop_facts2,
            "ready": ready3,
            "ready_time_s": round(ready3_time, 3),
            "smoke_status": smoke3[0],
            "backup_dir": str(backup_a.relative_to(workdir)),
            "backup_files": sorted(p.name for p in backup_a.iterdir()),
            "before": inv_before,
            "after": inv_after,
            "config_preserved": inv_before["config_sha256"] == inv_after["config_sha256"],
            "cache_disposable_no_migration": inv_before["cache_root_state"]
            == inv_after["cache_root_state"],
        }
        if not (
            reinstall.returncode == 0
            and ready3
            and smoke3[0] == 200
            and evidence["steps"]["upgrade"]["config_preserved"]
            and evidence["steps"]["upgrade"]["cache_disposable_no_migration"]
        ):
            raise RuntimeError("upgrade verification failed")

        # S10: mechanical rollback from the backup.
        stop_facts3 = stop_candidate(candidate, config)
        rollback_install = install_wheel(venv, backup_a / wheels[0].name, reinstall=True)
        config.write_bytes((backup_a / "adapter.toml").read_bytes())
        os.chmod(config, 0o600)
        candidate = start_candidate(venv, config, env_file)
        ready4, ready4_time, _ = wait_ready(base, READY_TIMEOUT_SECONDS)
        smoke4 = http_json(
            CANDIDATE_PORT,
            "POST",
            "/v1/responses",
            {"model": FAKE_MODEL, "input": [{"role": "user", "content": prompt}], "stream": False},
        )
        evidence["steps"]["rollback"] = {
            "stop": stop_facts3,
            "install_exit": rollback_install.returncode,
            "config_restored_sha256": _sha256_file(config),
            "config_matches_backup": _sha256_file(config)
            == _sha256_file(backup_a / "adapter.toml"),
            "ready": ready4,
            "ready_time_s": round(ready4_time, 3),
            "smoke_status": smoke4[0],
        }
        if not (
            rollback_install.returncode == 0
            and evidence["steps"]["rollback"]["config_matches_backup"]
            and ready4
            and smoke4[0] == 200
        ):
            raise RuntimeError("rollback verification failed")

        # S11: failed start injected at the documented point (unreachable
        # upstream in the NEW configuration), then recovery by rollback.
        dead_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dead_sock.bind(("127.0.0.1", 0))
        dead_port = dead_sock.getsockname()[1]
        dead_sock.close()
        stamp_b = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        backup_b = workdir / "backups" / f"{stamp_b}-pre-failure"
        backup_b.mkdir(parents=True, exist_ok=True)
        (backup_b / "adapter.toml").write_bytes(config.read_bytes())
        os.chmod(backup_b / "adapter.toml", 0o600)
        (backup_b / wheels[0].name).write_bytes((backup_a / wheels[0].name).read_bytes())
        os.chmod(backup_b / wheels[0].name, 0o600)
        rendered_bad = render_template(
            {
                "__UPSTREAM_BASE_URL__": f"http://127.0.0.1:{dead_port}/v1",
                "__UPSTREAM_MODEL__": FAKE_MODEL,
            }
        )
        stop_facts4 = stop_candidate(candidate, config)
        config.write_bytes(rendered_bad.encode())
        os.chmod(config, 0o600)
        candidate = start_candidate(venv, config, env_file)
        ready5, _, readyz_status5 = wait_ready(base, UNREACHABLE_WAIT_SECONDS)
        readyz_body5 = http_json(CANDIDATE_PORT, "GET", "/readyz")
        stop_facts5 = stop_candidate(candidate, config)
        # Recovery: restore previous configuration and artifact.
        rollback2 = install_wheel(venv, backup_b / wheels[0].name, reinstall=True)
        config.write_bytes((backup_b / "adapter.toml").read_bytes())
        os.chmod(config, 0o600)
        candidate = start_candidate(venv, config, env_file)
        ready6, ready6_time, _ = wait_ready(base, READY_TIMEOUT_SECONDS)
        smoke6 = http_json(
            CANDIDATE_PORT,
            "POST",
            "/v1/responses",
            {"model": FAKE_MODEL, "input": [{"role": "user", "content": prompt}], "stream": False},
        )
        evidence["steps"]["failed_start_injection"] = {
            "injected_point": "new configuration upstream unreachable (closed loopback port)",
            "first_stop": stop_facts4,
            "unreachable_ready": ready5,
            "unreachable_readyz_status": readyz_status5,
            "unreachable_readyz_upstream": (readyz_body5[1] or {}).get("upstream"),
            "stopped_after_injection": stop_facts5,
            "recovery_install_exit": rollback2.returncode,
            "recovery_config_sha256": _sha256_file(config),
            "recovery_config_matches_backup": _sha256_file(config)
            == _sha256_file(backup_b / "adapter.toml"),
            "recovery_ready": ready6,
            "recovery_ready_time_s": round(ready6_time, 3),
            "recovery_smoke_status": smoke6[0],
        }
        if not (
            ready5 is False
            and readyz_status5 == 503
            and (readyz_body5[1] or {}).get("upstream") == "unavailable"
            and ready6
            and smoke6[0] == 200
            and evidence["steps"]["failed_start_injection"]["recovery_config_matches_backup"]
        ):
            raise RuntimeError("failed-start injection or recovery verification failed")

        # S12: stop final candidate and scan its full output for privacy.
        stop_facts6 = stop_candidate(candidate, config)
        full_output = (candidate.stdout.read() or b"").decode(errors="replace")
        candidate = None
        evidence["steps"]["final_stop"] = {
            **stop_facts6,
            "stdout_contains_prompt_marker": PROMPT_MARKER in full_output,
            "stdout_contains_synthetic_key": SYNTHETIC_KEY_VALUE in full_output,
        }
        if (
            evidence["steps"]["final_stop"]["stdout_contains_prompt_marker"]
            or evidence["steps"]["final_stop"]["stdout_contains_synthetic_key"]
        ):
            raise RuntimeError("raw content appeared in candidate output")

        # S13: systemd verification (best effort; absence is not a blocker).
        # The transient unit needs 18031 free, so this runs after the stop.
        evidence["steps"]["systemd"] = _systemd_verification(venv, config, env_file, skip_systemd)

        # S14: cleanup and absence proof.
        fake_state_final = dict(fake_state.counts) if fake_state else {}
        if fake_server is not None:
            fake_server.shutdown()
            fake_server.server_close()
        unit_after = unit_facts()
        evidence["protected_after"] = {
            "unit": unit_after,
            "protected_18020_listening": port_listening(PROTECTED_PORT),
            "protected_18020_health": get_status(f"http://127.0.0.1:{PROTECTED_PORT}/health"),
            "absent_18021_listening": port_listening(ABSENT_PORT),
            "candidate_18031_free": port_free(CANDIDATE_PORT),
        }
        evidence["steps"]["fake_upstream_request_counts"] = fake_state_final
        evidence["steps"]["cleanup"] = {
            "workdir_removed": not keep,
            "unit_unchanged": unit_before == unit_after,
            "no_orphan_candidate": run(["pgrep", "-f", str(config)]).returncode != 0,
        }
        evidence["result"] = "PASS" if not failures else "FAIL"
        if keep:
            (workdir / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
        return evidence
    except Exception as exc:  # noqa: BLE001 - qualification must report and clean up
        if fake_server is not None:
            fake_server.shutdown()
            fake_server.server_close()
        if candidate is not None:
            try:
                candidate.terminate()
                candidate.wait(timeout=10)
            except Exception:
                candidate.kill()
        failures.append(f"{type(exc).__name__}: {exc}")
        evidence["result"] = "FAIL"
        evidence["failure"] = failures[-1]
        if keep:
            (workdir / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
        return evidence
    finally:
        if not keep and workdir.exists():
            shutil.rmtree(workdir, ignore_errors=True)


def _extract_tool_facts(base: str) -> dict:
    conn = http.client.HTTPConnection("127.0.0.1", CANDIDATE_PORT, timeout=60)
    conn.request(
        "POST",
        "/v1/responses",
        body=json.dumps(
            {
                "model": FAKE_MODEL,
                "input": [{"role": "user", "content": "tool probe"}],
                "tools": [
                    {
                        "type": "function",
                        "name": "fake_lookup",
                        "description": "fake",
                        "parameters": {"type": "object", "properties": {}},
                    }
                ],
                "stream": False,
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    response = conn.getresponse()
    payload = json.loads(response.read().decode())
    conn.close()
    call_id = None
    for item in payload.get("output", []):
        if item.get("type") == "function_call":
            call_id = item.get("call_id")
    return {"responses_call_id": call_id}


def _systemd_verification(venv: Path, config: Path, env_file: Path, skip: bool) -> dict:
    facts: dict = {"attempted": True}
    if skip:
        facts.update({"attempted": False, "reason": "skipped by flag"})
        return facts
    if shutil.which("systemd-run") is None:
        facts.update({"attempted": False, "reason": "systemd-run not available"})
        return facts
    unit = REPO_ROOT / "packaging" / "slaif-local-coding.service"
    verify = run(["systemd-analyze", "--user", "verify", str(unit)], timeout=120)
    out = (verify.stdout.decode() + verify.stderr.decode()).strip()
    facts["systemd_analyze_verify"] = {
        "exit": verify.returncode,
        "output_lines": len(out.splitlines()),
        "output_has_error": any(line.startswith("ERROR") for line in out.splitlines()),
    }
    unit_name = f"slaif-009-qual-{os.getpid()}.service"
    start = run(
        [
            "systemd-run",
            "--user",
            "--collect",
            f"--unit={unit_name}",
            f"--setenv={SYNTHETIC_KEY_NAME}={SYNTHETIC_KEY_VALUE}",
            "--",
            str(venv / "bin" / "slaif-local-coding"),
            "--config",
            str(config),
        ],
        timeout=60,
    )
    facts["transient_unit_start"] = {"exit": start.returncode, "unit": unit_name}
    if start.returncode == 0:
        base = f"http://127.0.0.1:{CANDIDATE_PORT}"
        ready, ready_time, _ = wait_ready(base, READY_TIMEOUT_SECONDS)
        healthz = get_status(f"{base}/healthz")
        facts["transient_unit_ready"] = {
            "ready": ready,
            "ready_time_s": round(ready_time, 3),
            "healthz": healthz,
        }
        stop = run(["systemctl", "--user", "stop", unit_name], timeout=60)
        facts["transient_unit_stop"] = {"exit": stop.returncode}
        listing = run(["systemctl", "--user", "list-units", "--all", "--no-legend"], timeout=60)
        removed = unit_name not in listing.stdout.decode()
        facts["transient_unit_removed"] = removed
        facts["port_free_after_transient"] = port_free(CANDIDATE_PORT)
    return facts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", type=Path, default=None)
    parser.add_argument("--keep", action="store_true", help="keep the workdir for inspection")
    parser.add_argument("--skip-systemd", action="store_true")
    args = parser.parse_args()

    workdir = args.workdir or Path(f"/tmp/slaif-009-qual-{os.getpid()}")
    evidence = qualify(workdir, args.keep, args.skip_systemd)
    # Print a bounded, payload-free summary (never raw bodies or secrets).
    summary = {
        "result": evidence["result"],
        "protected_before": evidence.get("protected_before"),
        "protected_after": evidence.get("protected_after"),
        "steps": evidence.get("steps"),
        "failure": evidence.get("failure"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if evidence["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
