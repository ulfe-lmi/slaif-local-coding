"""Wholly synthetic fake child for the 017-i capture utility (offline only).

This is a test/data child, NOT a client: it emulates the bounded
client-side protocol behavior needed to exercise the capture utility's
provider, extraction, supervision, and privacy paths. It is driven solely
by the utility-owned control file (a closed schema) and a predeclared
harmless command table. It never executes arbitrary or incoming commands,
never reads the parent environment, never persists raw provider traffic,
and treats every provider response as untrusted data (bounded parsing, no
content logging).

Its JSONL stdout carries metadata-only events (counts and booleans), plus
optionally declared leak-marker lines (``LEAK-<run_id>-<channel>``) that
the offline tests use to prove non-leakage. Exit codes: 0 complete,
64 undeclared command, 65 provider/control error.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

CONTROL_SCHEMA = "slaif-real-client-capture-control-v1"
UNDECLARED_COMMAND_EXIT = 64
PROVIDER_ERROR_EXIT = 65
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
REQUEST_TIMEOUT = 10.0


def fail(event_type: str, code: int, **extra: object) -> int:
    event = {"type": event_type}
    event.update(extra)
    sys.stdout.write(json.dumps(event, sort_keys=True) + "\n")
    sys.stdout.flush()
    return code


def emit(event_type: str, **extra: object) -> None:
    event = {"type": event_type}
    event.update(extra)
    sys.stdout.write(json.dumps(event, sort_keys=True) + "\n")
    sys.stdout.flush()


def http_json(
    url: str,
    method: str,
    body: bytes | None,
    token: str,
    extra_headers: dict[str, str] | None,
) -> tuple[int, bytes]:
    headers = {"Authorization": f"Bearer {token}"}
    if extra_headers:
        headers.update(extra_headers)
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            data = response.read(MAX_RESPONSE_BYTES + 1)
            if len(data) > MAX_RESPONSE_BYTES:
                raise ValueError("oversized")
            return response.status, data
    except urllib.error.HTTPError as exc:
        # Read and discard the bounded error body; never echo it.
        try:
            exc.read(65536)
        except (OSError, ValueError):
            pass
        return exc.code, b""
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return 0, b""


def parse_sse_items(data: bytes) -> list[dict[str, object]]:
    """Bounded in-memory SSE parse; returns output items only."""
    items: list[dict[str, object]] = []
    text = data.decode("utf-8", "replace")
    for block in text.split("\n\n"):
        event_type = ""
        data_lines: list[str] = []
        for line in block.split("\n"):
            if line.startswith("event: "):
                event_type = line[len("event: ") :].strip()
            elif line.startswith("data: "):
                data_lines.append(line[len("data: ") :])
        if event_type != "response.output_item.added" or not data_lines:
            continue
        try:
            payload = json.loads("\n".join(data_lines))
        except ValueError:
            continue
        if not isinstance(payload, dict):
            continue
        item = payload.get("item")
        if isinstance(item, dict):
            items.append(item)
    return items


def main() -> int:
    if len(sys.argv) != 2:
        return 2
    try:
        with open(sys.argv[1], "rb") as stream:
            control = json.loads(stream.read(1024 * 1024).decode("utf-8"))
    except (OSError, ValueError):
        return 2
    if not isinstance(control, dict) or control.get("schema") != CONTROL_SCHEMA:
        return 2
    for key in ("provider_base_url", "model", "mode", "token", "run_id", "steps", "markers"):
        if key not in control:
            return 2
    run_id = str(control["run_id"])
    base_url = str(control["provider_base_url"])
    model = str(control["model"])
    mode = str(control["mode"])
    token = str(control["token"])
    steps = control["steps"]
    markers = control["markers"] if isinstance(control["markers"], dict) else {}
    if not isinstance(steps, list) or not steps:
        return 2
    spawn_grandchild = bool(control.get("spawn_grandchild", False))

    if spawn_grandchild:
        # A grandchild in the same process group: proves group cleanup.
        subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(60)"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    env_check_var = control.get("env_check_var")
    parent_marker_present = (
        os.environ.get(str(env_check_var)) is not None if env_check_var else False
    )
    codex_home_set = os.environ.get("CODEX_HOME") is not None
    token_env_present = os.environ.get("SLAIF_CAPTURE_TOKEN") is not None
    fact_path = os.path.join(os.environ.get("CODEX_HOME", "."), "env-fact.json")
    try:
        with open(fact_path, "w", encoding="utf-8") as stream:
            json.dump(
                {
                    "parent_marker_present": parent_marker_present,
                    "codex_home_is_child": codex_home_set,
                    "token_env_present": token_env_present,
                },
                stream,
            )
        os.chmod(fact_path, 0o600)
    except OSError:
        pass

    extra_headers = None
    if markers.get("header"):
        extra_headers = {"X-SLAIF-Marker": f"LEAK-{run_id}-header"}

    # 1. Bounded models probe (like a genuine client catalog check).
    status, _ = http_json(base_url + "/models", "GET", None, token, extra_headers)
    if status != 200:
        return fail(
            "slaif_fake_child_provider_error", PROVIDER_ERROR_EXIT, stage="models", status=status
        )
    emit("slaif_fake_child_start", steps=len(steps))
    emit(
        "slaif_fake_child_env",
        parent_marker_present=parent_marker_present,
        codex_home_set=codex_home_set,
        token_env_present=token_env_present,
    )

    prompt = "Synthetic capture run."
    if markers.get("prompt"):
        prompt += f" LEAK-{run_id}-prompt"
    if mode == "responses-function-tool":
        tools = [
            {
                "type": "function",
                "name": str(step.get("tool_name", "")),
                "description": "synthetic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cmd": {"type": "string"},
                        "workdir": {"type": "string"},
                    },
                    "required": ["cmd", "workdir"],
                },
            }
            for step in steps
        ]
    else:
        tools = [
            {
                "type": "custom",
                "name": str(step.get("tool_name", "")),
                "description": "synthetic",
            }
            for step in steps
        ]

    history: list[dict[str, object]] = [
        {
            "role": "user",
            "content": [{"type": "input_text", "text": prompt}],
        }
    ]
    output_type = (
        "function_call_output" if mode == "responses-function-tool" else "custom_tool_call_output"
    )

    def post(body_obj: dict[str, object]) -> tuple[int, list[dict[str, object]]]:
        nonlocal request_seq
        request_seq += 1
        emit("slaif_fake_child_request", seq=request_seq)
        body = json.dumps(body_obj, separators=(",", ":")).encode("utf-8")
        status, data = http_json(base_url + "/responses", "POST", body, token, extra_headers)
        if status != 200:
            return fail(
                "slaif_fake_child_provider_error",
                PROVIDER_ERROR_EXIT,
                stage="responses",
                status=status,
            )
        return 200, parse_sse_items(data)

    def request_body() -> dict[str, object]:
        return {
            "model": model,
            "stream": True,
            "input": history,
            "tools": tools,
            "instructions": "synthetic capture",
        }

    def append_output(call_id: str, output: dict[str, object]) -> None:
        history.append(
            {
                "type": output_type,
                "call_id": call_id,
                "output": json.dumps(output, sort_keys=True),
            }
        )

    request_seq = 0
    status, items = post(request_body())
    if not items:
        return fail("slaif_fake_child_no_tool_call", PROVIDER_ERROR_EXIT, seq=request_seq)
    call = items[-1]
    call_type = str(call.get("type", ""))
    if mode == "responses-function-tool" and call_type != "function_call":
        return fail("slaif_fake_child_tool_shape", PROVIDER_ERROR_EXIT, seq=request_seq)
    if mode == "responses-custom-tool" and call_type != "custom_tool_call":
        return fail("slaif_fake_child_tool_shape", PROVIDER_ERROR_EXIT, seq=request_seq)
    history.append(dict(call))

    for index, step in enumerate(steps):
        call_id = str(call.get("call_id", ""))
        if step.get("kind") == "read":
            # Execute ONLY the predeclared literal file read (own workspace).
            try:
                with open(os.path.join(".", str(step.get("path", ""))), "rb") as f:
                    content = f.read(1024 * 1024).decode("utf-8", "replace")
            except OSError:
                return fail("slaif_fake_child_file_error", PROVIDER_ERROR_EXIT, seq=request_seq)
            append_output(
                call_id,
                {
                    "content": content,
                    "exit_code": 0,
                    "status": "completed",
                    "process_id": f"proc_{index + 1:02d}",
                },
            )
            if index + 1 < len(steps):
                status, items = post(request_body())
                if not items:
                    return fail(
                        "slaif_fake_child_no_tool_call", PROVIDER_ERROR_EXIT, seq=request_seq
                    )
                call = items[-1]
                if str(call.get("type", "")) not in ("function_call", "custom_tool_call"):
                    return fail("slaif_fake_child_tool_shape", PROVIDER_ERROR_EXIT, seq=request_seq)
                history.append(dict(call))
            else:
                post(request_body())  # final step: provider returns the final message
        elif step.get("kind") == "sleep":
            process_id = f"proc_{index + 1:02d}"
            append_output(
                call_id,
                {"content": "", "status": "running", "process_id": process_id},
            )
            post(request_body())  # expect in-progress ack (no new items)
            time.sleep(float(step.get("seconds", 0.0)))
            append_output(
                call_id,
                {
                    "content": "",
                    "exit_code": 0,
                    "status": "completed",
                    "process_id": process_id,
                },
            )
            if index + 1 < len(steps):
                status, items = post(request_body())
                if not items:
                    return fail(
                        "slaif_fake_child_no_tool_call", PROVIDER_ERROR_EXIT, seq=request_seq
                    )
                call = items[-1]
                if str(call.get("type", "")) not in ("function_call", "custom_tool_call"):
                    return fail("slaif_fake_child_tool_shape", PROVIDER_ERROR_EXIT, seq=request_seq)
                history.append(dict(call))
            else:
                post(request_body())  # expect final message
        else:
            return fail("slaif_fake_child_step_invalid", PROVIDER_ERROR_EXIT, seq=request_seq)

    if markers.get("stderr"):
        sys.stderr.write(f"LEAK-{run_id}-stderr\n")
        sys.stderr.flush()
    if markers.get("stdout"):
        sys.stdout.write(f"LEAK-{run_id}-stdout\n")
        sys.stdout.flush()
    emit("slaif_fake_child_complete", requests=request_seq)
    return 0


if __name__ == "__main__":
    sys.exit(main())
