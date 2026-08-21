"""Safely capture one minimized synthetic Codex project-instruction envelope."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

MODEL = "synthetic-capture-model"
PROVIDER = "synthetic_capture"
PROJECT_PREFIX = "# AGENTS.md instructions for "


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


def minimize(payload: dict[str, Any]) -> dict[str, Any]:
    found: list[dict[str, Any]] = []
    for parent in payload.get("input", []):
        if not isinstance(parent, dict) or parent.get("role") != "developer":
            continue
        for item in parent.get("content", []):
            if (
                isinstance(item, dict)
                and item.get("type") == "input_text"
                and isinstance(item.get("text"), str)
                and item["text"].startswith(PROJECT_PREFIX)
            ):
                found.append(
                    {
                        "role": "developer",
                        "content": [{"type": "input_text", "text": item["text"]}],
                    }
                )
    if len(found) != 1:

        def marker_paths(value: Any, path: str = "$") -> list[str]:
            if isinstance(value, str):
                return [path] if "AGENTS.md instructions" in value else []
            if isinstance(value, list):
                return [
                    found_path
                    for index, child in enumerate(value)
                    for found_path in marker_paths(child, f"{path}[{index}]")
                ]
            if isinstance(value, dict):
                return [
                    found_path
                    for key, child in value.items()
                    for found_path in marker_paths(child, f"{path}.{key}")
                ]
            return []

        structure = [
            (
                parent.get("role"),
                [item.get("type") for item in parent.get("content", []) if isinstance(item, dict)],
            )
            for parent in payload.get("input", [])
            if isinstance(parent, dict)
        ]
        text_markers = [
            {
                "starts_project_prefix": item.get("text", "").startswith(PROJECT_PREFIX),
                "contains_agents_marker": "AGENTS.md instructions" in item.get("text", ""),
                "contains_open_delimiter": "<INSTRUCTIONS>" in item.get("text", ""),
            }
            for parent in payload.get("input", [])
            if isinstance(parent, dict) and parent.get("role") == "developer"
            for item in parent.get("content", [])
            if isinstance(item, dict) and isinstance(item.get("text"), str)
        ]
        raise RuntimeError(
            f"expected one project item, observed {len(found)}; "
            f"sanitized role/type structure={structure!r}, markers={text_markers!r}, "
            f"marker_paths={marker_paths(payload)!r}"
        )
    return {"model": MODEL, "input": found}


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
