"""Capture only bounded top-level Codex tool-definition type labels.

This helper is deliberately disposable: the fake Responses provider reads one
synthetic request, extracts only validated ``tools[].type`` strings, returns a
fixed error, and then stops. No request body, credentials, image, prompt, or
tool data crosses the result boundary.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import threading
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from tests.helpers import vision_e2e_support as vision
from tests.helpers.e2e_support import _sandbox_environment

MAX_TOOL_DEFINITIONS = 16
MAX_UNIQUE_TYPES = 16
MAX_REQUEST_BYTES = 8_388_608
MAX_TYPE_LENGTH = 64
SAFE_TYPE = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")
CAPTURE_KEY_ENV = "SLAIF_CAPTURE_KEY"


class CaptureServer(ThreadingHTTPServer):
    """One-request server with only sanitized capture state."""

    captured_types: tuple[str, ...] | None = None
    rejected: bool = False


class Handler(BaseHTTPRequestHandler):
    server: CaptureServer

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/responses":
            self.server.rejected = True
            self._fixed_error(404)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
            self.server.rejected = True
            self._fixed_error(413)
            return
        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body)
            types = _extract_types(payload)
        except (TypeError, ValueError, json.JSONDecodeError):
            self.server.rejected = True
        else:
            self.server.captured_types = types
        finally:
            body = b""
        self._fixed_error(400)

    def _fixed_error(self, status: int) -> None:
        response = b'{"error":{"type":"synthetic_capture_stop"}}'
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format: str, *args: object) -> None:
        del format, args


def _extract_types(payload: object) -> tuple[str, ...]:
    if not isinstance(payload, dict):
        raise ValueError("request must be an object")
    tools = payload.get("tools")
    if not isinstance(tools, list) or not tools or len(tools) > MAX_TOOL_DEFINITIONS:
        raise ValueError("bounded top-level tools list required")
    result: list[str] = []
    for definition in tools:
        if not isinstance(definition, dict):
            raise ValueError("tool definition must be an object")
        marker = definition.get("type")
        if (
            not isinstance(marker, str)
            or len(marker) > MAX_TYPE_LENGTH
            or not SAFE_TYPE.fullmatch(marker)
        ):
            raise ValueError("unsafe tool type")
        result.append(marker)
    if len(set(result)) > MAX_UNIQUE_TYPES:
        raise ValueError("too many unique tool types")
    return tuple(result)


def _capture_command(
    codex_bin: Path | str,
    fixture: vision.VisionFixturePaths,
    output_path: Path,
) -> list[str]:
    return [
        str(codex_bin),
        "--dangerously-bypass-approvals-and-sandbox",
        "exec",
        "--json",
        "--strict-config",
        "--cd",
        str(fixture.repository),
        "--image",
        str(fixture.full_image.path),
        "--output-last-message",
        str(output_path),
        "Return the word synthetic.",
    ]


def capture_tool_types(codex_bin: Path | str = "codex") -> tuple[tuple[str, int], ...]:
    """Run one no-model Codex invocation and return ordered types/counts."""
    with tempfile.TemporaryDirectory(prefix="slaif-codex-tool-types-") as temporary:
        root = Path(temporary)
        server: CaptureServer | None = None
        fixture = vision.write_vision_fixture(
            root,
            base_url="http://127.0.0.1:0/v1",
            api_key_env=CAPTURE_KEY_ENV,
        )
        vision.write_vision_model_catalog(codex_bin, fixture.model_catalog)
        server = CaptureServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.handle_request, daemon=True)
        thread.start()
        port = server.server_address[1]
        fixture.codex_config.write_text(
            fixture.codex_config.read_text(encoding="utf-8").replace(
                "http://127.0.0.1:0/v1", f"http://127.0.0.1:{port}/v1"
            ),
            encoding="utf-8",
        )
        os.chmod(fixture.codex_config, 0o600)
        output_path = root / "last-message.tmp"
        environment = _sandbox_environment(fixture.codex_home, CAPTURE_KEY_ENV)
        environment[CAPTURE_KEY_ENV] = "synthetic-only"
        with (
            tempfile.TemporaryFile(dir=fixture.codex_home) as stdout,
            tempfile.TemporaryFile(dir=fixture.codex_home) as stderr,
        ):
            process = subprocess.Popen(
                _capture_command(codex_bin, fixture, output_path),
                cwd=fixture.repository,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
            )
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                raise RuntimeError("codex_tool_capture_timeout") from None
        thread.join(timeout=5)
        server.server_close()
        if thread.is_alive():
            raise RuntimeError("capture_server_did_not_stop")
        if server.rejected or server.captured_types is None:
            raise RuntimeError("safe_tool_type_capture_failed")
        counts = Counter(server.captured_types)
        ordered_unique = tuple(dict.fromkeys(server.captured_types))
        return tuple((marker, counts[marker]) for marker in ordered_unique)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-bin", default="codex")
    args = parser.parse_args()
    ordered = capture_tool_types(args.codex_bin)
    print(json.dumps({"types": ordered, "unique_types": len(ordered)}, separators=(",", ":")))


if __name__ == "__main__":
    main()
