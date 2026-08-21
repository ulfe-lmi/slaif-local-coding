"""Safely capture one minimized synthetic Codex project-instruction envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

MODEL = "synthetic-capture-model"
PROVIDER = "synthetic_capture"
PROJECT_PREFIX = "# AGENTS.md instructions for "
LOGICAL_LABEL = "repo"
PROJECT_PATTERN = re.compile(
    r"# AGENTS\.md instructions for (?P<label>[^\r\n]+)\r?\n\r?\n"
    r"<INSTRUCTIONS>\r?\n(?P<content>.*?)\r?\n</INSTRUCTIONS>",
    re.DOTALL,
)


class CaptureServer(ThreadingHTTPServer):
    captured: dict[str, Any] | None = None


class Handler(BaseHTTPRequestHandler):
    server: CaptureServer

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/responses":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 2_000_000:
            self.send_error(413)
            return
        payload = json.loads(self.rfile.read(length))
        if payload.get("stream") is not True:
            self.send_error(400)
            return
        self.server.captured = payload
        response = {
            "type": "response.completed",
            "response": {
                "id": "resp_synthetic",
                "object": "response",
                "created_at": 0,
                "status": "completed",
                "model": MODEL,
                "output": [],
                "usage": {
                    "input_tokens": 1,
                    "input_tokens_details": {"cached_tokens": 0},
                    "output_tokens": 0,
                    "output_tokens_details": {"reasoning_tokens": 0},
                    "total_tokens": 1,
                },
            },
        }
        body = f"event: response.completed\ndata: {json.dumps(response)}\n\n".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


def _all_marker_paths(value: Any, path: str = "$") -> list[str]:
    if isinstance(value, str):
        return [path] if "AGENTS.md instructions" in value else []
    if isinstance(value, list):
        return [
            found
            for index, child in enumerate(value)
            for found in _all_marker_paths(child, f"{path}[{index}]")
        ]
    if isinstance(value, dict):
        return [
            found
            for key, child in value.items()
            for found in _all_marker_paths(child, f"{path}.{key}")
        ]
    return []


def _one_block(text: str, *, allow_environment_tail: bool) -> tuple[str, str]:
    matches = list(PROJECT_PATTERN.finditer(text))
    if len(matches) != 1 or matches[0].start() != 0:
        raise RuntimeError("project block is not unique at the supported boundary")
    suffix = text[matches[0].end() :]
    if suffix not in ("", "\n", "\r\n"):
        if not allow_environment_tail or not re.fullmatch(
            r"(?:\r?\n)?<environment_context>\r?\n.*\r?\n</environment_context>\r?\n?",
            suffix,
            re.DOTALL,
        ):
            raise RuntimeError("unsupported material follows project block")
    return matches[0].group("label"), matches[0].group("content")


def minimize(payload: dict[str, Any]) -> dict[str, Any]:
    marker_paths = _all_marker_paths(payload)
    if (
        len(marker_paths) != 2
        or marker_paths[0] != "$.instructions"
        or not re.fullmatch(r"\$\.input\[\d+\]\.content\[\d+\]\.text", marker_paths[1])
    ):
        instructions_value = payload.get("instructions")
        instruction_facts = {
            "is_string": isinstance(instructions_value, str),
            "contains_agents": isinstance(instructions_value, str)
            and "AGENTS.md" in instructions_value,
            "contains_project_phrase": isinstance(instructions_value, str)
            and "instructions for" in instructions_value,
            "contains_open_delimiter": isinstance(instructions_value, str)
            and "<INSTRUCTIONS>" in instructions_value,
            "contains_synthetic_rule": isinstance(instructions_value, str)
            and "MUST read [security](docs/SECURITY.md)." in instructions_value,
        }
        raise RuntimeError(
            "unsupported marker locations/count; "
            f"count={len(marker_paths)} paths={marker_paths!r} instructions={instruction_facts!r}"
        )
    location_match = re.fullmatch(
        r"\$\.input\[(?P<input>\d+)\]\.content\[(?P<content>\d+)\]\.text", marker_paths[1]
    )
    assert location_match is not None
    input_index = int(location_match.group("input"))
    content_index = int(location_match.group("content"))
    instructions = payload.get("instructions")
    inputs = payload.get("input")
    if (
        not isinstance(instructions, str)
        or not isinstance(inputs, list)
        or input_index >= len(inputs)
    ):
        raise RuntimeError("missing supported top-level positions")
    parent = inputs[input_index]
    if not isinstance(parent, dict) or parent.get("role") != "user":
        raise RuntimeError("supported input parent is not top-level user")
    content = parent.get("content")
    if not isinstance(content, list) or content_index >= len(content):
        raise RuntimeError("supported user content is missing")
    item = content[content_index]
    if not isinstance(item, dict) or item.get("type") != "input_text":
        raise RuntimeError("supported user item is not input_text")
    user_text = item.get("text")
    if not isinstance(user_text, str):
        raise RuntimeError("supported user text is missing")
    instruction_label, instruction_content = _one_block(instructions, allow_environment_tail=False)
    user_label, user_content = _one_block(user_text, allow_environment_tail=True)
    if instruction_label != user_label or instruction_content != user_content:
        raise RuntimeError("paired logical label/content does not agree")
    encoded = instruction_content.encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    envelope = (
        f"# AGENTS.md instructions for {LOGICAL_LABEL}\n\n"
        f"<INSTRUCTIONS>\n{instruction_content}\n</INSTRUCTIONS>"
    )
    return {
        "model": MODEL,
        "instructions": envelope,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": envelope
                        + "\n<environment_context>\n"
                        + "<synthetic-discarded />\n</environment_context>",
                    }
                ],
            }
        ],
        "sanitized_provenance": {
            "marker_occurrences": 2,
            "logical_label": LOGICAL_LABEL,
            "content_byte_length": len(encoded),
            "content_sha256": digest,
            "occurrences_agree": True,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with tempfile.TemporaryDirectory(prefix="slaif-codex-capture-") as temporary:
        root = Path(temporary)
        home = root / "codex-home"
        repository = root / "repository"
        home.mkdir(mode=0o700)
        repository.mkdir()
        (repository / "AGENTS.md").write_text(
            "MUST read [security](docs/SECURITY.md).\nNEVER skip `TESTING.md`.\n"
        )
        subprocess.run(["git", "init", "-q", str(repository)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(repository), "add", "AGENTS.md"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(repository),
                "-c",
                "user.name=Synthetic Capture",
                "-c",
                "user.email=synthetic@example.invalid",
                "commit",
                "-q",
                "-m",
                "Synthetic fixture",
            ],
            check=True,
            capture_output=True,
        )
        bundled = subprocess.run(
            [args.codex_bin, "debug", "models", "--bundled"],
            env={**os.environ, "CODEX_HOME": str(home)},
            check=True,
            capture_output=True,
            text=True,
        )
        catalog = json.loads(bundled.stdout)
        template = next(model for model in catalog["models"] if model["slug"] == "gpt-5.4")
        template["slug"] = MODEL
        template["display_name"] = MODEL
        template["description"] = "Synthetic capture model"
        catalog_path = root / "model-catalog.json"
        catalog_path.write_text(json.dumps({"models": [template]}))
        server = CaptureServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.handle_request, daemon=True)
        thread.start()
        port = server.server_address[1]
        env = {**os.environ, "CODEX_HOME": str(home), "SLAIF_CAPTURE_KEY": "synthetic-only"}
        provider = (
            '{name="Synthetic capture",base_url="http://127.0.0.1:'
            f'{port}/v1",env_key="SLAIF_CAPTURE_KEY",wire_api="responses"}}'
        )
        command = [
            args.codex_bin,
            "exec",
            "--ephemeral",
            "--ignore-user-config",
            "-C",
            str(repository),
            "-m",
            MODEL,
            "-c",
            f'model_provider="{PROVIDER}"',
            "-c",
            f"model_providers.{PROVIDER}={provider}",
            "-c",
            f'model_catalog_json="{catalog_path}"',
            "Return the word synthetic.",
        ]
        completed = subprocess.run(command, env=env, capture_output=True, timeout=30)
        thread.join(timeout=5)
        server.server_close()
        if completed.returncode != 0:
            raise RuntimeError(f"Codex exited with status {completed.returncode}")
        if server.captured is None:
            raise RuntimeError("fake endpoint received no request")
        minimized = minimize(server.captured)
        args.output.write_text(json.dumps(minimized, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
