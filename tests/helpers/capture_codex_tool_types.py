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
import shutil
import subprocess
import tempfile
import threading
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from tests.helpers import vision_e2e_support as vision
from tests.helpers.e2e_support import _sandbox_environment
from tests.helpers.path_safety import assert_allowlisted_diagnostic_argv

MAX_TOOL_DEFINITIONS = 16
MAX_UNIQUE_TYPES = 16
MAX_REQUEST_BYTES = 8_388_608
MAX_TYPE_LENGTH = 64
SAFE_TYPE = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")
CAPTURE_KEY_ENV = "SLAIF_CAPTURE_KEY"


@dataclass(frozen=True)
class CodexToolCapture:
    """Sanitized result of one disposable first-request capture."""

    tool_type_counts: tuple[tuple[str, int], ...]
    request_received: bool
    codex_exit_status: int | None
    timed_out: bool
    policy_observation: object | None = None


class CaptureServer(ThreadingHTTPServer):
    """One-request server with only sanitized capture state."""

    captured_types: tuple[str, ...] | None = None
    policy_observation: object | None = None
    request_reducer: Callable[[object], object] | None = None
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
            types = _extract_types(payload, require_nonempty=False)
        except (TypeError, ValueError, json.JSONDecodeError):
            self.server.rejected = True
        else:
            self.server.captured_types = types
            if self.server.request_reducer is not None:
                self.server.policy_observation = self.server.request_reducer(payload)
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


def _extract_types(payload: object, *, require_nonempty: bool = True) -> tuple[str, ...]:
    if not isinstance(payload, dict):
        raise ValueError("request must be an object")
    tools = payload.get("tools", [])
    if (
        not isinstance(tools, list)
        or (require_nonempty and not tools)
        or len(tools) > MAX_TOOL_DEFINITIONS
    ):
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
    *,
    feature_flags: tuple[str, ...] = (),
    ignore_user_config: bool = False,
    provider_base_url: str | None = None,
) -> list[str]:
    command = [
        str(codex_bin),
        "--dangerously-bypass-approvals-and-sandbox",
        "exec",
        "--json",
        "--ephemeral",
        "--strict-config",
    ]
    command.extend(flag for feature in feature_flags for flag in ("--disable", feature))
    if ignore_user_config:
        if provider_base_url is None:
            raise ValueError("provider_base_url is required when ignoring user config")
        command.extend(
            [
                "--ignore-user-config",
                "-C",
                str(fixture.repository),
                "-m",
                vision.VISION_MODEL,
                "-c",
                'model_provider="slaif-capture"',
                "-c",
                (
                    "model_providers.slaif-capture={"
                    f'name="Synthetic capture",base_url="{provider_base_url}",'
                    f'env_key="{CAPTURE_KEY_ENV}",wire_api="responses"'
                    "}"
                ),
                "-c",
                f"model_catalog_json={json.dumps(str(fixture.model_catalog))}",
            ]
        )
    else:
        command.extend(["--cd", str(fixture.repository)])
    command.extend(
        [
            "--output-last-message",
            str(output_path),
            "Return the word synthetic.",
        ]
    )
    return command


def capture_codex_request(
    codex_bin: Path | str = "codex",
    *,
    feature_flags: tuple[str, ...] = (),
    ignore_user_config: bool = False,
    catalog_mutator: Callable[[Path], None] | None = None,
    request_reducer: Callable[[object], object] | None = None,
) -> CodexToolCapture:
    """Run one bounded no-model capture and discard the request body."""

    with tempfile.TemporaryDirectory(prefix="slaif-codex-tool-envelope-") as temporary:
        root = Path(temporary)
        home = root / "home"
        scratch = root / "tmp"
        home.mkdir(mode=0o700)
        scratch.mkdir(mode=0o700)
        fixture = vision.write_vision_fixture(
            root / "fixture",
            base_url="http://127.0.0.1:0/v1",
            api_key_env=CAPTURE_KEY_ENV,
        )
        codex_executable = Path(shutil.which(str(codex_bin)) or str(codex_bin)).resolve()
        vision.write_vision_model_catalog(
            codex_executable,
            fixture.model_catalog,
            environment_root=home,
        )
        if catalog_mutator is not None:
            catalog_mutator(fixture.model_catalog)
        server = CaptureServer(("127.0.0.1", 0), Handler)
        server.request_reducer = request_reducer
        thread = threading.Thread(target=server.handle_request, daemon=True)
        thread.start()
        port = server.server_address[1]
        provider_base_url = f"http://127.0.0.1:{port}/v1"
        fixture.codex_config.write_text(
            fixture.codex_config.read_text(encoding="utf-8").replace(
                "http://127.0.0.1:0/v1", provider_base_url
            ),
            encoding="utf-8",
        )
        os.chmod(fixture.codex_config, 0o600)
        output_path = root / "last-message.tmp"
        command = _capture_command(
            codex_executable,
            fixture,
            output_path,
            feature_flags=feature_flags,
            ignore_user_config=ignore_user_config,
            provider_base_url=provider_base_url,
        )
        assert_allowlisted_diagnostic_argv(
            command,
            allowed_commands={codex_executable.name},
            allowed_executables=(codex_executable,),
            disposable_root=root,
            path_arguments=(
                fixture.repository,
                fixture.codex_home,
                fixture.codex_config,
                fixture.model_catalog,
                output_path,
            ),
        )
        environment = _sandbox_environment(fixture.codex_home, CAPTURE_KEY_ENV)
        environment["HOME"] = str(home)
        environment["TMPDIR"] = str(scratch)
        environment[CAPTURE_KEY_ENV] = "synthetic-only"
        exit_status: int | None = None
        timed_out = False
        with (
            tempfile.TemporaryFile(dir=fixture.codex_home) as stdout,
            tempfile.TemporaryFile(dir=fixture.codex_home) as stderr,
        ):
            process = subprocess.Popen(
                command,
                cwd=fixture.repository,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
            )
            try:
                exit_status = process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                timed_out = True
        thread.join(timeout=5)
        server.server_close()
        if thread.is_alive():
            raise RuntimeError("capture_server_did_not_stop")
        if server.rejected or server.captured_types is None:
            raise RuntimeError("safe_tool_type_capture_failed")
        counts = Counter(server.captured_types)
        ordered_unique = tuple(dict.fromkeys(server.captured_types))
        return CodexToolCapture(
            tool_type_counts=tuple((marker, counts[marker]) for marker in ordered_unique),
            request_received=True,
            codex_exit_status=exit_status,
            timed_out=timed_out,
            policy_observation=server.policy_observation,
        )


def capture_tool_types(codex_bin: Path | str = "codex") -> tuple[tuple[str, int], ...]:
    """Run one no-model Codex invocation and return ordered types/counts."""
    capture = capture_codex_request(codex_bin)
    return capture.tool_type_counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-bin", default="codex")
    args = parser.parse_args()
    ordered = capture_tool_types(args.codex_bin)
    print(json.dumps({"types": ordered, "unique_types": len(ordered)}, separators=(",", ":")))


if __name__ == "__main__":
    main()
