"""Offline adversarial coverage for the 017-i capture utility.

The utility (``scripts/real_client_capture.py``) is a bounded, opt-in,
fail-closed process-capture harness whose ACTUAL-client path is disabled by
construction. These tests exercise ONLY the offline surface: synthetic
child executables (pinned injected paths; no installed-client fallback),
the in-process owned fake provider, bounded provider robustness over raw
sockets, extraction allowlists, supervision/timeout/cap accounting,
attempt-ledger persistence, and privacy non-leakage. No test launches an
installed client, calls a model, or touches a real provider.
"""

from __future__ import annotations

import importlib.util
import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
UTILITY = REPO_ROOT / "scripts" / "real_client_capture.py"
FAKE_CHILD = REPO_ROOT / "scripts" / "real_client_capture_fake_child.py"

spec = importlib.util.spec_from_file_location("real_client_capture", UTILITY)
assert spec is not None and spec.loader is not None
rcc = importlib.util.module_from_spec(spec)
sys.modules["real_client_capture"] = rcc
spec.loader.exec_module(rcc)

CaptureError = cast("type[Any]", rcc.CaptureError)
DeclaredStep = cast(type, rcc.DeclaredStep)
ProviderState = cast(type, rcc.ProviderState)
FakeProvider = cast(type, rcc.FakeProvider)

DEFAULT_MODE = "responses-function-tool"
TEST_VERSION = "9.9.9-test"


def make_synthetic_binary(
    tmp_path: Path,
    *,
    version: str = TEST_VERSION,
    help_flags: tuple[str, ...] = (
        "--ephemeral",
        "--skip-git-repo-check",
        "--ignore-rules",
        "--json",
        "-s",
        "-C",
        "-m",
        "--version",
        "--help",
    ),
    help_bytes: int | None = None,
    exit_code: int | None = None,
) -> Path:
    """A wholly synthetic 'client-like' binary (never an installed client)."""
    lines = "\n".join(f"    print({flag!r})" for flag in help_flags)
    if exit_code is not None:
        # Preflight probes (--version / exec --help) succeed; the actual exec
        # session exits with the pinned code (a truthful child failure).
        body = (
            "import sys\n"
            f"if sys.argv[1:] == ['--version']:\n"
            f"    print('codex-cli {version}')\n"
            f"    sys.exit(0)\n"
            f"elif sys.argv[1:] == ['exec', '--help']:\n"
            f"{lines}\n"
            f"    sys.exit(0)\n"
            f"sys.exit({exit_code})\n"
        )
    else:
        body = (
            "import sys\n"
            f"if sys.argv[1:] == ['--version']:\n"
            f"    print('codex-cli {version}')\n"
            f"elif sys.argv[1:] == ['exec', '--help']:\n"
            f"{lines}\n"
            f"    sys.exit(0)\n"
            f"else:\n"
            f"    sys.exit(0)\n"
        )
    if help_bytes is not None:
        body = (
            "import sys\n"
            f"if sys.argv[1:] == ['--version']:\n"
            f"    print('codex-cli {version}')\n"
            f"elif sys.argv[1:] == ['exec', '--help']:\n"
            f"    print('x' * {help_bytes})\n"
            f"    sys.exit(0)\n"
            f"else:\n"
            f"    sys.exit(0)\n"
        )
    binary = tmp_path / f"fakebin-{abs(hash(body)) % 100000}"
    binary.write_text(f"#!{sys.executable}\n{body}", encoding="utf-8")
    binary.chmod(0o700)
    return binary


def sha256_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_0600(path: Path, record: dict[str, Any]) -> None:
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    path.chmod(0o600)


def protected_out_dir(tmp_path: Path, name: str = "out") -> Path:
    out = tmp_path / name
    out.mkdir(mode=0o700)
    out.chmod(0o700)
    return out


def default_steps() -> tuple[Any, ...]:
    return tuple(rcc.default_declared_steps())


# ---------------------------------------------------------------------------
# Limits: fail-closed resolution; hard caps cannot silently rise.
# ---------------------------------------------------------------------------
class TestLimits:
    def test_hard_defaults(self) -> None:
        limits = rcc.CaptureLimits.resolved()
        assert limits.max_requests == rcc.HARD_MAX_REQUESTS == 20
        assert limits.max_inbound_bytes == rcc.HARD_MAX_INBOUND_BYTES == 1048576
        assert limits.max_selected_bytes == rcc.HARD_MAX_SELECTED_BYTES == 262144
        assert limits.deadline_seconds == rcc.HARD_DEADLINE_SECONDS == 120.0
        assert limits.max_child_output_bytes == rcc.HARD_MAX_CHILD_OUTPUT_BYTES == 4194304
        assert limits.max_actual_attempts == rcc.HARD_MAX_ACTUAL_ATTEMPTS == 1

    def test_lowering_is_allowed(self) -> None:
        limits = rcc.CaptureLimits.resolved(
            max_requests=3,
            max_inbound_bytes=4096,
            max_selected_bytes=1024,
            deadline_seconds=0.5,
            max_child_output_bytes=2048,
        )
        assert limits.max_requests == 3
        assert limits.deadline_seconds == 0.5

    @pytest.mark.parametrize(
        ("kwargs", "expected_class"),
        [
            ({"max_requests": 21}, "limits_max_requests_over_hard_cap"),
            ({"max_inbound_bytes": 1048577}, "limits_max_inbound_bytes_over_hard_cap"),
            ({"max_selected_bytes": 262145}, "limits_max_selected_bytes_over_hard_cap"),
            ({"deadline_seconds": 120.1}, "limits_deadline_seconds_over_hard_cap"),
            (
                {"max_child_output_bytes": 4194305},
                "limits_max_child_output_bytes_over_hard_cap",
            ),
            ({"max_actual_attempts": 2}, "limits_max_actual_attempts_over_hard_cap"),
            ({"max_requests": 0}, "limits_max_requests_over_hard_cap"),
            ({"max_requests": -1}, "limits_max_requests_over_hard_cap"),
            ({"deadline_seconds": 0.0}, "limits_deadline_seconds_over_hard_cap"),
            ({"deadline_seconds": -2.0}, "limits_deadline_seconds_over_hard_cap"),
            ({"max_requests": "20"}, "limits_max_requests_invalid"),
            ({"max_requests": True}, "limits_max_requests_invalid"),
            ({"deadline_seconds": "1.0"}, "limits_deadline_seconds_invalid"),
        ],
    )
    def test_over_hard_cap_or_invalid_fails_closed(
        self, kwargs: dict[str, Any], expected_class: str
    ) -> None:
        with pytest.raises(CaptureError) as exc:
            rcc.CaptureLimits.resolved(**kwargs)
        assert exc.value.failure_class == expected_class


# ---------------------------------------------------------------------------
# Binary preflight (read-only) and static startup readiness.
# ---------------------------------------------------------------------------
class TestBinaryPreflight:
    def test_synthetic_binary_verified(self, tmp_path: Path) -> None:
        binary = make_synthetic_binary(tmp_path)
        facts = rcc.preflight_binary(binary, TEST_VERSION, sha256_file(binary))
        assert facts.version == TEST_VERSION
        assert facts.sha256 == sha256_file(binary)
        assert "--ephemeral" in facts.detected_flags
        assert facts.help_complete

    def test_hash_mismatch(self, tmp_path: Path) -> None:
        binary = make_synthetic_binary(tmp_path)
        bad = "0" * 64
        with pytest.raises(CaptureError) as exc:
            rcc.preflight_binary(binary, TEST_VERSION, bad)
        assert exc.value.failure_class == "binary_hash_mismatch"

    def test_version_mismatch(self, tmp_path: Path) -> None:
        binary = make_synthetic_binary(tmp_path)
        with pytest.raises(CaptureError) as exc:
            rcc.preflight_binary(binary, "0.0.1", sha256_file(binary))
        assert exc.value.failure_class == "binary_version_mismatch"

    def test_symlink_rejected(self, tmp_path: Path) -> None:
        binary = make_synthetic_binary(tmp_path)
        link = tmp_path / "link"
        link.symlink_to(binary)
        with pytest.raises(CaptureError) as exc:
            rcc.preflight_binary(link, TEST_VERSION, sha256_file(binary))
        assert exc.value.failure_class == "binary_symlink"

    def test_missing(self, tmp_path: Path) -> None:
        with pytest.raises(CaptureError) as exc:
            rcc.preflight_binary(tmp_path / "nope", TEST_VERSION, "0" * 64)
        assert exc.value.failure_class == "binary_missing"

    def test_help_over_bound(self, tmp_path: Path) -> None:
        binary = make_synthetic_binary(tmp_path, help_bytes=rcc.HARD_MAX_HELP_BYTES + 1)
        with pytest.raises(CaptureError) as exc:
            rcc.preflight_binary(binary, TEST_VERSION, sha256_file(binary))
        assert exc.value.failure_class == "binary_help_over_bound"

    def test_required_flags_missing(self, tmp_path: Path) -> None:
        binary = make_synthetic_binary(tmp_path, help_flags=("--json",))
        with pytest.raises(CaptureError) as exc:
            rcc.preflight_binary(binary, TEST_VERSION, sha256_file(binary))
        assert exc.value.failure_class == "binary_flags_unsupported"


class TestStartupReadiness:
    def test_static_evaluation_is_not_ready(self, tmp_path: Path) -> None:
        binary = make_synthetic_binary(tmp_path)
        facts = rcc.preflight_binary(binary, TEST_VERSION, sha256_file(binary))
        readiness = rcc.evaluate_startup_readiness(facts)
        assert readiness.verdict == "not_ready"
        assert "plugin_catalog_sync_control_unverified" in readiness.reasons
        assert "telemetry_update_control_unverified" in readiness.reasons
        record = readiness.to_record()
        assert record["schema"] == rcc.READINESS_SCHEMA
        assert all(
            candidate["status"] == "unverified" for candidate in record["control_candidates"]
        )
        # Metadata only: no raw help text may appear in the record.
        assert "ephemeral" not in json.dumps(record)

    def test_readiness_record_binding_mismatch(self, tmp_path: Path) -> None:
        binary = make_synthetic_binary(tmp_path)
        facts = rcc.preflight_binary(binary, TEST_VERSION, sha256_file(binary))
        record = rcc.evaluate_startup_readiness(facts).to_record()
        path = tmp_path / "readiness.json"
        write_json_0600(path, record)
        record["binary_sha256"] = "f" * 64
        write_json_0600(path, record)
        with pytest.raises(CaptureError) as exc:
            rcc.load_readiness_record(path, facts)
        assert exc.value.failure_class == "readiness_record_binding_mismatch"


# ---------------------------------------------------------------------------
# Attempt ledger: O_EXCL, consume-once, no reset, non-sensitive.
# ---------------------------------------------------------------------------
class TestAttemptLedger:
    def _dir(self, tmp_path: Path) -> Path:
        d = tmp_path / "attempts"
        d.mkdir(mode=0o700)
        d.chmod(0o700)
        return d

    def test_claim_consume_and_no_reset(self, tmp_path: Path) -> None:
        d = self._dir(tmp_path)
        rcc.claim_attempt(d, "run-1", "actual")
        assert rcc.attempt_state(d, "run-1") == "claimed"
        data = json.loads((d / "run-1.attempt").read_text())
        assert set(data) == {
            "schema",
            "run_id",
            "created_utc",
            "child_kind",
            "state",
            "outcome",
        }
        assert data["schema"] == rcc.ATTEMPT_SCHEMA
        assert data["outcome"] is None
        assert (d / "run-1.attempt").stat().st_mode & 0o777 == 0o600
        # A second wrapper invocation must not reset or re-claim.
        with pytest.raises(CaptureError) as exc:
            rcc.claim_attempt(d, "run-1", "actual")
        assert exc.value.failure_class == "attempt_already_claimed"
        rcc.consume_attempt(d, "run-1", "completed")
        assert rcc.attempt_state(d, "run-1") == "consumed"
        data = json.loads((d / "run-1.attempt").read_text())
        assert data["outcome"] == "completed"
        with pytest.raises(CaptureError) as exc:
            rcc.claim_attempt(d, "run-1", "actual")
        assert exc.value.failure_class == "attempt_already_claimed"

    def test_invalid_run_ids(self, tmp_path: Path) -> None:
        d = self._dir(tmp_path)
        for bad in ("", "has space", "x" * 129, "-lead", "a/b"):
            with pytest.raises(CaptureError):
                rcc.claim_attempt(d, bad, "synthetic")

    def test_unknown_run_id_is_none(self, tmp_path: Path) -> None:
        d = self._dir(tmp_path)
        assert rcc.attempt_state(d, "ghost") is None


# ---------------------------------------------------------------------------
# External authorization record: closed schema, bounds, read-only.
# ---------------------------------------------------------------------------
class TestAuthorization:
    def _limits(self) -> Any:
        return rcc.CaptureLimits.resolved(
            max_requests=20,
            max_inbound_bytes=1048576,
            max_selected_bytes=262144,
            deadline_seconds=120.0,
        )

    def test_valid_record_accepted(self, tmp_path: Path) -> None:
        path = tmp_path / "auth.json"
        write_json_0600(
            path,
            {
                "schema": rcc.AUTHORIZATION_SCHEMA,
                "run_id": "run-1",
                "max_attempts": 1,
                "max_requests": 20,
                "max_inbound_bytes": 1048576,
                "max_selected_bytes": 262144,
                "deadline_seconds": 120.0,
            },
        )
        data = rcc.load_authorization(path, "run-1", self._limits())
        assert data["max_attempts"] == 1

    def test_missing(self, tmp_path: Path) -> None:
        with pytest.raises(CaptureError) as exc:
            rcc.load_authorization(tmp_path / "nope.json", "run-1", self._limits())
        assert exc.value.failure_class == "authorization_missing"

    @pytest.mark.parametrize(
        "mutate",
        [
            lambda r: r.pop("max_attempts"),
            lambda r: r.update(extra=1),
            lambda r: r.update(schema="other"),
            lambda r: r.update(run_id="other"),
            lambda r: r.update(max_attempts=2),
            lambda r: r.update(max_requests=21),
            lambda r: r.update(max_inbound_bytes=1048577),
            lambda r: r.update(max_selected_bytes=262145),
            lambda r: r.update(deadline_seconds=120.1),
            lambda r: r.update(max_requests="20"),
            lambda r: r.update(deadline_seconds=-1),
        ],
    )
    def test_invalid_records_rejected(self, tmp_path: Path, mutate: Any) -> None:
        path = tmp_path / "auth.json"
        record = {
            "schema": rcc.AUTHORIZATION_SCHEMA,
            "run_id": "run-1",
            "max_attempts": 1,
            "max_requests": 20,
            "max_inbound_bytes": 1048576,
            "max_selected_bytes": 262144,
            "deadline_seconds": 120.0,
        }
        mutate(record)
        write_json_0600(path, record)
        with pytest.raises(CaptureError):
            rcc.load_authorization(path, "run-1", self._limits())


# ---------------------------------------------------------------------------
# Provider robustness over raw sockets (malformed/chunked/oversized/invalid
# length, auth, request limits). No content is ever persisted.
# ---------------------------------------------------------------------------
def start_provider(
    limits: Any, model: str = rcc.SYNTHETIC_MODEL, token: str = "tok"
) -> tuple[Any, Any]:
    state = ProviderState(limits, model, DEFAULT_MODE, token)
    provider = FakeProvider(state=state, steps=default_steps(), canary="CANARY")
    port = provider.start()
    return provider, (state, port)


class TestProviderRobustness:
    def _raw(self, port: int, payload: bytes) -> bytes:
        with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
            sock.sendall(payload)
            chunks: list[bytes] = []
            while True:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk)
                if len(b"".join(chunks)) > 65536:
                    break
            return b"".join(chunks)

    def _post_headers(self, port: int, extra: str, token: str = "tok") -> str:
        return (
            f"POST /v1/responses HTTP/1.1\r\n"
            f"Host: 127.0.0.1:{port}\r\n"
            f"Authorization: Bearer {token}\r\n"
            f"{extra}"
        )

    def test_valid_body_accepted(self, tmp_path: Path) -> None:
        provider, (state, port) = start_provider(rcc.CaptureLimits.resolved())
        try:
            body = json.dumps(
                {
                    "model": rcc.SYNTHETIC_MODEL,
                    "stream": True,
                    "input": [{"role": "user", "content": [{"type": "input_text", "text": "hi"}]}],
                    "tools": [{"type": "function", "name": "exec_command"}],
                }
            ).encode()
            request = (
                self._post_headers(
                    port, f"Content-Length: {len(body)}\r\nContent-Type: application/json\r\n\r\n"
                ).encode()
                + body
            )
            response = self._raw(port, request)
            assert response.startswith(b"HTTP/1.1 200")
            assert b"event: response.created" in response
        finally:
            provider.stop()

    @pytest.mark.parametrize(
        ("length_header", "body", "expected"),
        [
            ("abc", b"", "400"),
            ("-5", b"", "400"),
            ("1.5", b"", "400"),
            (str(rcc.HARD_MAX_INBOUND_BYTES + 1), b"", "413"),
        ],
    )
    def test_invalid_content_length(
        self, tmp_path: Path, length_header: str, body: bytes, expected: str
    ) -> None:
        provider, (state, port) = start_provider(rcc.CaptureLimits.resolved())
        try:
            request = (
                self._post_headers(port, f"Content-Length: {length_header}\r\n\r\n").encode() + body
            )
            response = self._raw(port, request)
            assert f"HTTP/1.1 {expected}".encode() in response
        finally:
            provider.stop()

    def test_incomplete_body(self, tmp_path: Path) -> None:
        provider, (state, port) = start_provider(rcc.CaptureLimits.resolved())
        try:
            request = self._post_headers(port, "Content-Length: 100\r\n\r\n").encode() + b"short"
            response = self._raw(port, request)
            assert b"HTTP/1.1 400" in response
        finally:
            provider.stop()

    def test_chunked_valid(self, tmp_path: Path) -> None:
        provider, (state, port) = start_provider(rcc.CaptureLimits.resolved())
        try:
            body = json.dumps(
                {
                    "model": rcc.SYNTHETIC_MODEL,
                    "stream": True,
                    "input": [{"role": "user", "content": [{"type": "input_text", "text": "hi"}]}],
                    "tools": [{"type": "function", "name": "exec_command"}],
                }
            ).encode()
            half = len(body) // 2
            request = self._post_headers(port, "Transfer-Encoding: chunked\r\n\r\n").encode()
            request += (
                f"{half:x}\r\n".encode()
                + body[:half]
                + b"\r\n"
                + f"{len(body) - half:x}\r\n".encode()
                + body[half:]
                + b"\r\n0\r\n\r\n"
            )
            response = self._raw(port, request)
            assert response.startswith(b"HTTP/1.1 200")
        finally:
            provider.stop()

    @pytest.mark.parametrize(
        "chunked_payload",
        [
            b"zz\r\n\r\n",  # invalid size token
            b"%x\r\n\r\n",  # invalid length
            b"99999999\r\n\r\n",  # oversized chunk
            b"1\r\nA\r\n",  # missing terminator/end
            b"2\r\nab",  # truncated chunk
        ],
    )
    def test_chunked_invalid(self, tmp_path: Path, chunked_payload: bytes) -> None:
        provider, (state, port) = start_provider(rcc.CaptureLimits.resolved())
        try:
            request = (
                self._post_headers(port, "Transfer-Encoding: chunked\r\n\r\n").encode()
                + chunked_payload
            )
            response = self._raw(port, request)
            assert b"HTTP/1.1 400" in response or b"HTTP/1.1 413" in response
        finally:
            provider.stop()

    def test_conflicting_length_headers(self, tmp_path: Path) -> None:
        provider, (state, port) = start_provider(rcc.CaptureLimits.resolved())
        try:
            request = (
                self._post_headers(
                    port,
                    "Content-Length: 5\r\nTransfer-Encoding: chunked\r\n\r\n",
                ).encode()
                + b"hello"
            )
            response = self._raw(port, request)
            assert b"HTTP/1.1 400" in response
        finally:
            provider.stop()

    def test_oversized_body_rejected_and_counted(self, tmp_path: Path) -> None:
        limits = rcc.CaptureLimits.resolved(max_inbound_bytes=1024)
        provider, (state, port) = start_provider(limits)
        try:
            body = b"x" * 2048
            request = (
                self._post_headers(port, f"Content-Length: {len(body)}\r\n\r\n").encode() + body
            )
            response = self._raw(port, request)
            assert b"HTTP/1.1 413" in response
            assert b"x" * 100 not in response  # generic sanitized body only
        finally:
            provider.stop()

    @pytest.mark.parametrize(
        "body",
        [
            b"{not json",
            b"[" + b"[" * 200000 + b"]" * 200000,  # deep nesting
            json.dumps({"model": rcc.SYNTHETIC_MODEL}).encode() + b"\xff\xfe",
            "\u00e9\u00e9 invalid".encode("utf-8") + b"\x00" * 50,
        ],
    )
    def test_malformed_bodies_fail_closed(self, tmp_path: Path, body: bytes) -> None:
        provider, (state, port) = start_provider(rcc.CaptureLimits.resolved())
        try:
            request = (
                self._post_headers(port, f"Content-Length: {len(body)}\r\n\r\n").encode() + body
            )
            response = self._raw(port, request)
            assert b"HTTP/1.1 400" in response
        finally:
            provider.stop()

    @pytest.mark.parametrize("auth", [None, "Bearer wrong", "Token tok"])
    def test_auth_rejected_without_values(self, tmp_path: Path, auth: str | None) -> None:
        provider, (state, port) = start_provider(rcc.CaptureLimits.resolved())
        try:
            header = "" if auth is None else f"Authorization: {auth}\r\n"
            request = (
                f"POST /v1/responses HTTP/1.1\r\n"
                f"Host: 127.0.0.1:{port}\r\n"
                f"{header}"
                f"Content-Length: 2\r\n\r\n"
                "{}"
            ).encode()
            response = self._raw(port, request)
            assert b"HTTP/1.1 401" in response
        finally:
            provider.stop()
        assert state.auth_rejected == 1

    def test_request_limit(self, tmp_path: Path) -> None:
        limits = rcc.CaptureLimits.resolved(max_requests=3)
        provider, (state, port) = start_provider(limits)
        try:
            body = json.dumps(
                {
                    "model": rcc.SYNTHETIC_MODEL,
                    "stream": True,
                    "input": [{"role": "user", "content": [{"type": "input_text", "text": "hi"}]}],
                    "tools": [{"type": "function", "name": "exec_command"}],
                }
            ).encode()
            statuses: list[str] = []
            for _ in range(4):
                request = (
                    self._post_headers(port, f"Content-Length: {len(body)}\r\n\r\n").encode() + body
                )
                response = self._raw(port, request)
                statuses.append(response.split(b" ", 2)[1].decode())
            assert statuses[:3] == ["200", "200", "200"]
            assert statuses[3] == "429"
            assert state.request_limit_hit
        finally:
            provider.stop()

    def test_unknown_path_404_and_models_authorized(self, tmp_path: Path) -> None:
        provider, (state, port) = start_provider(rcc.CaptureLimits.resolved())
        try:
            response = self._raw(
                port,
                (
                    f"GET /v1/nope HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{port}\r\n"
                    f"Authorization: Bearer tok\r\n"
                    f"\r\n"
                ).encode(),
            )
            assert b"HTTP/1.1 404" in response
            response = self._raw(
                port,
                (
                    f"GET /v1/models HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{port}\r\n"
                    f"Authorization: Bearer tok\r\n"
                    f"\r\n"
                ).encode(),
            )
            assert b"HTTP/1.1 200" in response
            assert rcc.SYNTHETIC_MODEL.encode() in response
        finally:
            provider.stop()

    def test_no_state_leaks_raw_content(self, tmp_path: Path) -> None:
        provider, (state, port) = start_provider(rcc.CaptureLimits.resolved())
        try:
            secret_marker = b"SECRET-MARKER-DO-NOT-PERSIST"
            body = json.dumps(
                {
                    "model": rcc.SYNTHETIC_MODEL,
                    "stream": True,
                    "input": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": secret_marker.decode(),
                                }
                            ],
                        }
                    ],
                    "tools": [{"type": "function", "name": "exec_command"}],
                }
            ).encode()
            request = (
                self._post_headers(port, f"Content-Length: {len(body)}\r\n\r\n").encode() + body
            )
            self._raw(port, request)
        finally:
            provider.stop()
        blob = json.dumps(
            {
                "frames": state.frames,
                "rejections": state.rejection_counts,
                "status_counts": state.status_counts,
            }
        ).encode()
        assert secret_marker not in blob


# ---------------------------------------------------------------------------
# Allowlisted extraction (pure, content-free).
# ---------------------------------------------------------------------------
class TestExtraction:
    def _extract(
        self,
        items: list[dict[str, Any]],
        *,
        steps: tuple[Any, ...] | None = None,
        canary: str = "CANARY",
        mode: str = DEFAULT_MODE,
    ) -> tuple[list[dict[str, Any]], dict[str, int], frozenset[str]]:
        payload = {"model": rcc.SYNTHETIC_MODEL, "input": items}
        frames, rejections, unknown = rcc.extract_frames(
            payload,
            declared_steps=steps or default_steps(),
            canary=canary,
            request_seq=2,
            mode=mode,
        )
        return list(frames), dict(rejections), frozenset(unknown)

    def test_declared_call_and_output_selected(self) -> None:
        output = json.dumps(
            {
                "content": "alpha file content\n",
                "exit_code": 0,
                "status": "completed",
                "process_id": "proc_01",
            },
            sort_keys=True,
        )
        frames, rejections, unknown = self._extract(
            [
                {
                    "type": "function_call",
                    "call_id": "call_01",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat A.md", "workdir": "."}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "call_01",
                    "output": output,
                },
            ]
        )
        assert rejections == {}
        assert unknown == frozenset()
        assert [f["item_type"] for f in frames] == [
            "function_call",
            "function_call_output",
        ]
        call, out = frames
        assert call["declared_command_index"] == 0
        assert out["status"] == "completed"
        assert out["exit_code"] == 0
        assert out["process_id"] == "proc_01"
        assert out["output_bytes"] == len(output.encode())
        import hashlib

        assert out["output_digest"] == hashlib.sha256(output.encode()).hexdigest()
        # Exact-byte digest even though the wrapper parsed.
        assert "alpha file content" not in json.dumps(frames)

    def test_undeclared_command_rejected(self) -> None:
        frames, rejections, _ = self._extract(
            [
                {
                    "type": "function_call",
                    "call_id": "call_01",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "rm -rf /", "workdir": "."}),
                }
            ]
        )
        assert frames == []
        assert rejections == {"command_not_declared": 1}

    def test_invalid_call_id_rejected(self) -> None:
        frames, rejections, _ = self._extract(
            [
                {
                    "type": "function_call",
                    "call_id": "bad id!",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat A.md", "workdir": "."}),
                }
            ]
        )
        assert frames == []
        assert rejections == {"call_id_invalid": 1}

    def test_undeclared_name_rejected(self) -> None:
        frames, rejections, _ = self._extract(
            [
                {
                    "type": "function_call",
                    "call_id": "call_01",
                    "name": "some_other_tool",
                    "arguments": json.dumps({"cmd": "cat A.md", "workdir": "."}),
                }
            ]
        )
        assert frames == []
        assert rejections == {"name_not_declared": 1}

    def test_canary_in_output_rejected_without_echo(self) -> None:
        frames, rejections, _ = self._extract(
            [
                {
                    "type": "function_call_output",
                    "call_id": "call_01",
                    "output": "SYNTHETIC-CANARY-xyz leaked",
                }
            ],
            canary="SYNTHETIC-CANARY-xyz",
        )
        assert frames == []
        assert rejections == {"credential_marker_present": 1}

    def test_canary_in_custom_input_rejected(self) -> None:
        frames, rejections, _ = self._extract(
            [
                {
                    "type": "custom_tool_call",
                    "call_id": "call_01",
                    "name": "synthetic_custom",
                    "input": "prefix CANARY suffix",
                }
            ],
            steps=(
                DeclaredStep(
                    index=0, tool_name="synthetic_custom", kind="read", path="A.md", seconds=0.0
                ),
            ),
            mode="responses-custom-tool",
        )
        assert frames == []
        assert rejections == {"credential_marker_present": 1}

    def test_custom_input_digest_only(self) -> None:
        steps = (
            DeclaredStep(
                index=0, tool_name="synthetic_custom", kind="read", path="A.md", seconds=0.0
            ),
        )
        frames, rejections, _ = self._extract(
            [
                {
                    "type": "custom_tool_call",
                    "call_id": "call_01",
                    "name": "synthetic_custom",
                    "input": "synthetic-custom-input-01",
                }
            ],
            steps=steps,
            mode="responses-custom-tool",
        )
        assert rejections == {}
        assert len(frames) == 1
        frame = frames[0]
        assert frame["input_bytes"] == len("synthetic-custom-input-01")
        assert "synthetic-custom-input-01" not in json.dumps(frames)

    def test_unknown_output_fields_rejected(self) -> None:
        frames, rejections, _ = self._extract(
            [
                {
                    "type": "function_call_output",
                    "call_id": "call_01",
                    "output": json.dumps({"status": "completed", "wat": 1}),
                }
            ]
        )
        assert frames == []
        assert rejections == {"output_shape_unsupported": 1}

    def test_invalid_status_rejected(self) -> None:
        frames, rejections, _ = self._extract(
            [
                {
                    "type": "function_call_output",
                    "call_id": "call_01",
                    "output": json.dumps({"status": "exploded"}),
                }
            ]
        )
        assert frames == []
        assert rejections == {"output_shape_unsupported": 1}

    def test_exit_code_range(self) -> None:
        frames, rejections, _ = self._extract(
            [
                {
                    "type": "function_call_output",
                    "call_id": "call_01",
                    "output": json.dumps({"exit_code": 256}),
                }
            ]
        )
        assert frames == []
        assert rejections == {"metadata_value_over_bound": 1}

    def test_overlong_metadata_rejected(self) -> None:
        frames, rejections, _ = self._extract(
            [
                {
                    "type": "function_call_output",
                    "call_id": "call_01",
                    "output": json.dumps({"process_id": "p" * (rcc.HARD_MAX_METADATA_BYTES + 1)}),
                }
            ]
        )
        assert frames == []
        assert rejections == {"metadata_value_over_bound": 1}

    def test_plain_string_output_digest_only(self) -> None:
        frames, rejections, _ = self._extract(
            [
                {
                    "type": "function_call_output",
                    "call_id": "call_01",
                    "output": "alpha file content\n",
                }
            ]
        )
        assert rejections == {}
        assert len(frames) == 1
        frame = frames[0]
        assert frame["status"] is None
        assert frame["output_bytes"] == len("alpha file content\n")
        assert frame["output_field_names"] is None

    def test_unknown_item_types_counted_not_echoed(self) -> None:
        frames, rejections, unknown = self._extract(
            [
                {"type": "computer_call", "call_id": "c1"},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "x"},
                        {"type": "image_url", "url": "http://x"},
                    ],
                },
            ]
        )
        assert frames == []
        assert rejections == {}
        assert "computer_call" in unknown
        assert "image_url" in unknown
        # Echoed nowhere in the result structures.
        blob = json.dumps([frames, dict(rejections)]).encode()
        assert b"computer_call" not in blob

    def test_mode_detection(self) -> None:
        assert (
            rcc.observe_tool_mode({"tools": [{"type": "function"}, {"type": "function"}]})
            == "responses-function-tool"
        )
        assert rcc.observe_tool_mode({"tools": [{"type": "custom"}]}) == "responses-custom-tool"
        assert (
            rcc.observe_tool_mode({"tools": [{"type": "function"}, {"type": "custom"}]})
            == "unknown"
        )
        assert rcc.observe_tool_mode({"tools": []}) == "unknown"
        assert rcc.observe_tool_mode({"tools": [{"type": "mystery"}]}) == "unknown"
        assert rcc.observe_tool_mode({}) == "unknown"

    def test_causal_transitions_preserved(self) -> None:
        frames, _, _ = self._extract(
            [
                {
                    "type": "function_call",
                    "call_id": "call_01",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat A.md", "workdir": "."}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "call_01",
                    "output": json.dumps({"status": "running", "process_id": "proc_01"}),
                },
                {
                    "type": "function_call_output",
                    "call_id": "call_01",
                    "output": json.dumps(
                        {
                            "status": "completed",
                            "exit_code": 0,
                            "process_id": "proc_01",
                        }
                    ),
                },
            ]
        )
        transitions = rcc.build_transitions(frames)
        assert len(transitions) == 1
        transition = transitions[0]
        assert transition["call_id"] == "call_01"
        assert transition["output_frame_count"] == 2
        assert transition["final_status"] == "completed"


# ---------------------------------------------------------------------------
# Child supervision: deadline, output cap, group cleanup, env isolation.
# ---------------------------------------------------------------------------
SLEEP_CHILD = """
import time
time.sleep({seconds})
"""

SLEEP_GRANDCHILD_CHILD = """
import subprocess, sys, time
subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep({seconds})
"""

SPLATTER_CHILD = """
import sys
sys.stdout.write("y" * {bytes})
sys.stdout.flush()
"""


def write_child(tmp_path: Path, body: str, name: str = "child.py") -> Path:
    child = tmp_path / name
    child.write_text(body, encoding="utf-8")
    child.chmod(0o700)
    return child


class TestChildSupervision:
    def test_normal_exit_and_counts(self, tmp_path: Path) -> None:
        child = write_child(
            tmp_path,
            "import sys\nsys.stdout.write('abcd')\nsys.stderr.write('ef')\n",
        )
        facts = rcc.run_child(
            argv=[sys.executable, str(child)],
            env={"PATH": "/usr/bin:/bin"},
            cwd=tmp_path,
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
        )
        assert facts.returncode == 0
        assert facts.stdout_bytes == 4
        assert facts.stderr_bytes == 2
        assert not facts.timed_out
        assert not facts.output_cap_exceeded
        assert facts.group_cleanup_verified

    def test_deadline_kills_owned_group_only(self, tmp_path: Path) -> None:
        child = write_child(tmp_path, SLEEP_GRANDCHILD_CHILD.format(seconds=30))
        survivor = tmp_path / "survivor.py"
        survivor.write_text("import time\ntime.sleep(30)\n", encoding="utf-8")
        survivor_proc = subprocess.Popen(
            [sys.executable, str(survivor)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,  # a DIFFERENT session: must survive
        )
        try:
            facts = rcc.run_child(
                argv=[sys.executable, str(child)],
                env={"PATH": "/usr/bin:/bin"},
                cwd=tmp_path,
                limits=rcc.CaptureLimits.resolved(deadline_seconds=0.5),
            )
            # The unrelated process (its own session) was never touched.
            assert survivor_proc.poll() is None
        finally:
            try:
                os.killpg(os.getpgid(survivor_proc.pid), 15)
            except OSError:
                survivor_proc.kill()
            survivor_proc.wait(timeout=10)
        assert facts.timed_out
        assert facts.returncode is not None
        assert facts.group_cleanup_verified

    def test_output_cap_kills_session(self, tmp_path: Path) -> None:
        child = write_child(tmp_path, SPLATTER_CHILD.format(bytes=100_000))
        facts = rcc.run_child(
            argv=[sys.executable, str(child)],
            env={"PATH": "/usr/bin:/bin"},
            cwd=tmp_path,
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0, max_child_output_bytes=1024),
        )
        assert facts.output_cap_exceeded
        assert facts.stdout_bytes <= 1024  # capped count, never raw
        assert facts.group_cleanup_verified

    def test_env_isolation(self, tmp_path: Path) -> None:
        child = write_child(
            tmp_path,
            "import json, os\n"
            "json.dump({'names': sorted(os.environ)}, open('env-names.json', 'w'))\n",
        )
        rcc.run_child(
            argv=[sys.executable, str(child)],
            env=rcc.build_child_env(rcc.setup_scratch(tmp_path, "envtest"), "tok"),
            cwd=tmp_path,
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
        )
        names = json.loads((tmp_path / "env-names.json").read_text())["names"]
        assert "HOME" in names and "CODEX_HOME" in names
        for forbidden in (
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "http_proxy",
            "HTTPS_PROXY",
            "SLAIF_TEST_PARENT_MARKER",
            "GIT_DIR",
        ):
            assert forbidden not in names


# ---------------------------------------------------------------------------
# End-to-end synthetic runs (offline): the ONLY launch path exercised here
# is the injected synthetic child; the actual-client path is fail-closed.
# ---------------------------------------------------------------------------
def run_synthetic(
    tmp_path: Path,
    run_id: str,
    *,
    limits: Any | None = None,
    markers: tuple[str, ...] = (),
    env_check_var: str | None = None,
    spawn_grandchild: bool = False,
    child: Path | None = None,
    steps: tuple[Any, ...] | None = None,
    workspace_files: tuple[tuple[str, bytes], ...] = (),
    mode: str = DEFAULT_MODE,
    out_name: str = "out",
) -> Any:
    out = protected_out_dir(tmp_path, out_name)
    return rcc.run_capture(
        run_id=run_id,
        out_dir=out,
        child=child or FAKE_CHILD,
        limits=limits,
        mode=mode,
        steps=steps or default_steps(),
        markers=markers,
        env_check_var=env_check_var,
        spawn_grandchild=spawn_grandchild,
        workspace_files=workspace_files,
    )


def record_blob(out: Path) -> bytes:
    blob = b""
    for path in out.rglob("*"):
        if path.is_file():
            blob += path.read_bytes()
    return blob


class TestSyntheticRuns:
    def test_happy_path_full(self, tmp_path: Path) -> None:
        monkeypatch_env = {"SLAIF_TEST_PARENT_MARKER": "parentsecret"}
        old = {k: os.environ.get(k) for k in monkeypatch_env}
        os.environ.update(monkeypatch_env)
        try:
            result = run_synthetic(
                tmp_path,
                "happy-1",
                limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
                markers=("stdout", "stderr", "header", "prompt"),
                env_check_var="SLAIF_TEST_PARENT_MARKER",
                spawn_grandchild=True,
            )
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        assert result.outcome == "completed"
        assert result.child_facts.returncode == 0
        assert result.child_facts.group_cleanup_verified
        assert result.scratch_entries_removed > 0
        assert result.run_record["child"]["env_facts"] == {
            "codex_home_is_child": True,
            "parent_marker_present": False,
            "token_env_present": True,
        }
        selection = result.selection_record
        assert selection is not None
        assert selection["provenance"] == "synthetic-offline"
        assert selection["fixture_authority"] == "none"
        assert selection["client"]["mode"] == DEFAULT_MODE
        assert selection["client"]["version"] is None
        assert selection["client"]["binary_sha256"] is None
        types = {f["item_type"] for f in selection["frames"]}
        assert types == {"function_call", "function_call_output"}
        assert len(selection["transitions"]) == 2
        for transition in selection["transitions"]:
            assert transition["final_status"] == "completed"
        # running -> completed sequence preserved for the sleep call.
        sleep_outputs = [
            f
            for f in selection["frames"]
            if f["call_id"] == "call_02" and f["item_type"] == "function_call_output"
        ]
        statuses = [f["status"] for f in sleep_outputs]
        assert "running" in statuses and "completed" in statuses
        # Digests present (exact raw output bytes), raw content absent.
        output_frames = [f for f in selection["frames"] if f["item_type"] == "function_call_output"]
        assert output_frames
        for frame in output_frames:
            digest = frame["output_digest"]
            assert isinstance(digest, str) and len(digest) == 64
            assert all(c in "0123456789abcdef" for c in digest)
        assert "alpha file content" not in json.dumps(selection)
        assert b"alpha file content" not in record_blob(result.run_record_path.parent)
        # Leak markers: derived from the run id; must persist nowhere.
        for channel in ("stdout", "stderr", "header", "prompt"):
            marker = f"LEAK-happy-1-{channel}".encode()
            assert marker not in record_blob(result.run_record_path.parent)
        # Permissions.
        out = result.run_record_path.parent
        assert out.stat().st_mode & 0o777 == 0o700
        assert result.run_record_path.stat().st_mode & 0o777 == 0o600
        assert (
            result.selection_path is not None
            and result.selection_path.stat().st_mode & 0o777 == 0o600
        )
        assert (out / "attempts" / "happy-1.attempt").stat().st_mode & 0o777 == 0o600
        # Scratch root fully removed.
        assert not (out / "scratch" / "slaif-capture-happy-1").exists()

    def test_custom_mode_run(self, tmp_path: Path) -> None:
        steps = tuple(
            DeclaredStep(
                index=s.index,
                tool_name="synthetic_custom",
                kind=s.kind,
                path=s.path,
                seconds=s.seconds,
                workdir=s.workdir,
            )
            for s in default_steps()
        )
        result = run_synthetic(
            tmp_path,
            "custom-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            mode="responses-custom-tool",
            steps=steps,
            out_name="out-custom",
        )
        assert result.outcome == "completed"
        selection = result.selection_record
        assert selection is not None
        assert selection["client"]["mode"] == "responses-custom-tool"
        assert any(f["item_type"] == "custom_tool_call" for f in selection["frames"])
        assert any(f["item_type"] == "custom_tool_call_output" for f in selection["frames"])
        # Causal ids preserved across the custom pair (no flattening).
        call_ids = {
            f["call_id"]
            for f in selection["frames"]
            if f["item_type"] in {"custom_tool_call", "custom_tool_call_output"}
        }
        assert call_ids == {"call_01", "call_02"}
        assert len(selection["transitions"]) == 2

    def test_deadline_timeout_with_grandchild(self, tmp_path: Path) -> None:
        steps = (
            DeclaredStep(
                index=0,
                tool_name="exec_command",
                kind="read",
                path="A.md",
                seconds=0.0,
            ),
            DeclaredStep(
                index=1,
                tool_name="exec_command",
                kind="sleep",
                path="",
                seconds=5.0,
            ),
        )
        result = run_synthetic(
            tmp_path,
            "timeout-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=0.6),
            steps=steps,
            spawn_grandchild=True,
            out_name="out-timeout",
        )
        assert result.outcome == "timed_out"
        assert result.child_facts.timed_out
        assert result.child_facts.group_cleanup_verified
        assert result.selection_path is None

    def test_request_limit(self, tmp_path: Path) -> None:
        result = run_synthetic(
            tmp_path,
            "reqlimit-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0, max_requests=4),
            out_name="out-reqlimit",
        )
        assert result.outcome == "request_limit_exceeded"
        assert result.run_record["provider"]["request_limit_hit"]
        assert result.selection_path is None

    def test_selected_over_bound(self, tmp_path: Path) -> None:
        result = run_synthetic(
            tmp_path,
            "selbound-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0, max_selected_bytes=50),
            out_name="out-selbound",
        )
        assert result.outcome == "selected_over_bound"
        assert result.selection_path is None
        assert result.run_record["selection"]["written"] is False

    def test_credential_canary_in_output(self, tmp_path: Path) -> None:
        canary = b"SYNTHETIC-CANARY-canary-1"
        steps = (
            DeclaredStep(
                index=0,
                tool_name="exec_command",
                kind="read",
                path="canary.md",
                seconds=0.0,
            ),
        )
        result = run_synthetic(
            tmp_path,
            "canary-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            steps=steps,
            workspace_files=(("canary.md", canary),),
            out_name="out-canary",
        )
        assert result.outcome == "completed"
        selection = result.selection_record
        assert selection is not None
        assert selection["rejected"]["reason_counts"].get("credential_marker_present") == 1
        assert canary not in record_blob(result.run_record_path.parent)
        # The call itself (declared) is still selected; the output is not.
        assert any(f["item_type"] == "function_call" for f in selection["frames"])
        assert not any(f["item_type"] == "function_call_output" for f in selection["frames"])

    def test_child_failure(self, tmp_path: Path) -> None:
        child = write_child(tmp_path, "import sys\nsys.exit(3)\n")
        result = run_synthetic(
            tmp_path,
            "childfail-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            child=child,
            out_name="out-childfail",
        )
        assert result.outcome == "child_failure"
        assert result.child_facts.returncode == 3
        # Attempt consumed with the truthful outcome.
        assert (
            rcc.attempt_state(result.run_record_path.parent / "attempts", "childfail-1")
            == "consumed"
        )

    def test_provider_error_child(self, tmp_path: Path) -> None:
        child = tmp_path / "provider_err_child.py"
        child.write_text(
            "import json, sys, urllib.request\n"
            "control = json.load(open(sys.argv[1]))\n"
            "url = control['provider_base_url'] + '/bogus'\n"
            "req = urllib.request.Request(url, headers={'Authorization': "
            "f\"Bearer {control['token']}\"})\n"
            "try:\n"
            "    urllib.request.urlopen(req, timeout=5)\n"
            "except urllib.error.HTTPError as exc:\n"
            "    sys.exit(65)\n"
            "except Exception:\n"
            "    sys.exit(65)\n",
            encoding="utf-8",
        )
        child.chmod(0o700)
        result = run_synthetic(
            tmp_path,
            "provfail-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            child=child,
            out_name="out-provfail",
        )
        assert result.outcome == "provider_error"
        assert result.run_record["provider"]["status_counts"].get("404")

    def test_undeclared_incoming_command_rejected(self, tmp_path: Path) -> None:
        child = tmp_path / "undeclared_child.py"
        child.write_text(
            "import json, sys, urllib.request\n"
            "control = json.load(open(sys.argv[1]))\n"
            "base = control['provider_base_url']\n"
            "token = control['token']\n"
            "body = json.dumps({'model': control['model'], 'stream': True,\n"
            "  'input': [{'role': 'user', 'content': [{'type': 'input_text',"
            " 'text': 'hi'}],\n"
            "   'type': 'function_call', 'call_id': 'forged_01',\n"
            "   'name': 'exec_command',\n"
            "   'arguments': json.dumps({'cmd': 'curl evil', 'workdir': '.'})}],\n"
            "  'tools': [{'type': 'function', 'name': 'exec_command'}]}).encode()"
            "\n"
            "req = urllib.request.Request(base + '/responses', data=body,\n"
            "  headers={'Authorization': f'Bearer {token}'})\n"
            "try:\n"
            "    urllib.request.urlopen(req, timeout=5)\n"
            "except urllib.error.HTTPError:\n"
            "    pass\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        child.chmod(0o700)
        result = run_synthetic(
            tmp_path,
            "undecl-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            child=child,
            out_name="out-undecl",
        )
        assert result.outcome == "completed"
        selection = result.selection_record
        assert selection is not None
        assert selection["rejected"]["reason_counts"].get("command_not_declared") == 1
        assert b"curl evil" not in record_blob(result.run_record_path.parent)
        assert all(f["call_id"] != "forged_01" for f in selection["frames"])


# ---------------------------------------------------------------------------
# Tool-mode mismatch fails closed.
# ---------------------------------------------------------------------------
class TestToolModeMismatch:
    def test_mismatch_fails_closed(self, tmp_path: Path) -> None:
        child = tmp_path / "mode_mismatch_child.py"
        child.write_text(
            "import json, sys, urllib.request\n"
            "control = json.load(open(sys.argv[1]))\n"
            "base = control['provider_base_url']\n"
            "token = control['token']\n"
            "body = json.dumps({'model': control['model'], 'stream': True,\n"
            "  'input': [{'role': 'user', 'content': [{'type': 'input_text',"
            " 'text': 'hi'}]}],\n"
            "  'tools': [{'type': 'custom', 'name': 'x'}]}).encode()\n"
            "req = urllib.request.Request(base + '/responses', data=body,\n"
            "  headers={'Authorization': f'Bearer {token}'})\n"
            "try:\n"
            "    urllib.request.urlopen(req, timeout=5)\n"
            "except urllib.error.HTTPError:\n"
            "    pass\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        child.chmod(0o700)
        result = run_synthetic(
            tmp_path,
            "mismatch-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            child=child,
            mode=DEFAULT_MODE,
            out_name="out-mismatch",
        )
        assert result.outcome == "tool_mode_mismatch"
        assert result.run_record["provider"]["tool_mode_mismatch"]
        assert result.selection_path is None


# ---------------------------------------------------------------------------
# Actual-client path: fail-closed gates (no genuine client is ever invoked).
# ---------------------------------------------------------------------------
class TestActualFailClosed:
    def test_without_opt_in(self, tmp_path: Path) -> None:
        out = protected_out_dir(tmp_path)
        with pytest.raises(CaptureError) as exc:
            rcc.run_capture(
                run_id="actual-1",
                out_dir=out,
                child=FAKE_CHILD,
                child_kind="actual",
            )
        assert exc.value.failure_class == "actual_client_not_opted_in"
        assert not (out / "attempts").exists() or not list((out / "attempts").iterdir())

    def test_missing_bindings(self, tmp_path: Path) -> None:
        out = protected_out_dir(tmp_path)
        with pytest.raises(CaptureError) as exc:
            rcc.run_capture(
                run_id="actual-2",
                out_dir=out,
                child=FAKE_CHILD,
                child_kind="actual",
                allow_actual_client=True,
            )
        assert exc.value.failure_class == "actual_binary_binding_missing"

    def test_readiness_not_ready_blocks_launch(self, tmp_path: Path) -> None:
        out = protected_out_dir(tmp_path)
        binary = make_synthetic_binary(tmp_path)
        facts = rcc.preflight_binary(binary, TEST_VERSION, sha256_file(binary))
        readiness = rcc.evaluate_startup_readiness(facts)
        record_path = out / "readiness.json"
        write_json_0600(record_path, readiness.to_record())
        with pytest.raises(CaptureError) as exc:
            rcc.run_capture(
                run_id="actual-3",
                out_dir=out,
                child=FAKE_CHILD,
                child_kind="actual",
                allow_actual_client=True,
                binary=binary,
                expected_version=TEST_VERSION,
                expected_sha256=sha256_file(binary),
                readiness_record=record_path,
                authorized_record=out / "auth.json",
            )
        assert exc.value.failure_class == "readiness_not_ready"
        # No attempt was claimed: the gate failed before any launch state.
        assert rcc.attempt_state(out / "attempts", "actual-3") is None

    def test_consumed_attempt_blocks_second_launch(self, tmp_path: Path) -> None:
        out = protected_out_dir(tmp_path)
        binary = make_synthetic_binary(tmp_path, exit_code=7)
        sha = sha256_file(binary)
        facts = rcc.preflight_binary(binary, TEST_VERSION, sha)
        ready = rcc.ReadinessFacts(
            verdict="ready",
            reasons=(),
            binary_version=facts.version,
            binary_sha256=facts.sha256,
            detected_flags=facts.detected_flags,
            control_candidates=rcc.STARTUP_CONTROL_CANDIDATES,
        )
        readiness_path = out / "readiness.json"
        write_json_0600(readiness_path, ready.to_record())
        auth_path = out / "auth.json"
        write_json_0600(
            auth_path,
            {
                "schema": rcc.AUTHORIZATION_SCHEMA,
                "run_id": "actual-4",
                "max_attempts": 1,
                "max_requests": 20,
                "max_inbound_bytes": 1048576,
                "max_selected_bytes": 262144,
                "deadline_seconds": 10.0,
            },
        )

        def run_once() -> Any:
            return rcc.run_capture(
                run_id="actual-4",
                out_dir=out,
                child=FAKE_CHILD,
                child_kind="actual",
                allow_actual_client=True,
                binary=binary,
                expected_version=TEST_VERSION,
                expected_sha256=sha,
                readiness_record=readiness_path,
                authorized_record=auth_path,
            )

        first = run_once()
        # The synthetic stand-in binary exits 7: a truthful child_failure,
        # and the one-attempt ledger claim is consumed.
        assert first.outcome == "child_failure"
        assert first.child_facts.returncode == 7
        assert rcc.attempt_state(out / "attempts", "actual-4") == "consumed"
        with pytest.raises(CaptureError) as exc:
            run_once()
        assert exc.value.failure_class == "attempt_already_claimed"

    def test_binary_preflight_fails_before_claim(self, tmp_path: Path) -> None:
        out = protected_out_dir(tmp_path)
        with pytest.raises(CaptureError) as exc:
            rcc.run_capture(
                run_id="actual-5",
                out_dir=out,
                child=FAKE_CHILD,
                child_kind="actual",
                allow_actual_client=True,
                binary=tmp_path / "missing",
                expected_version=TEST_VERSION,
                expected_sha256="0" * 64,
                readiness_record=out / "readiness.json",
                authorized_record=out / "auth.json",
            )
        assert exc.value.failure_class == "binary_missing"
        assert rcc.attempt_state(out / "attempts", "actual-5") is None


# ---------------------------------------------------------------------------
# Scratch/workspace/cleanup guards.
# ---------------------------------------------------------------------------
class TestWorkspaceAndCleanup:
    def test_scratch_root_modes_and_config(self, tmp_path: Path) -> None:
        setup = rcc.setup_scratch(tmp_path, "modes-1")
        assert setup.root.stat().st_mode & 0o777 == 0o700
        for name in ("child-home", "child-home-home", "workspace"):
            assert (setup.root / name).stat().st_mode & 0o777 == 0o700
        for name, _ in rcc.WORKSPACE_FILES:
            assert (setup.root / "workspace" / name).stat().st_mode & 0o777 == 0o600
        rcc.write_child_config(setup.child_home, 1, "m")
        config = setup.child_home / "config.toml"
        assert config.stat().st_mode & 0o777 == 0o600
        rcc.cleanup_root(setup.root)
        assert not setup.root.exists()

    def test_preexisting_root_rejected(self, tmp_path: Path) -> None:
        rcc.setup_scratch(tmp_path, "pre-1")
        with pytest.raises(CaptureError) as exc:
            rcc.setup_scratch(tmp_path, "pre-1")
        assert exc.value.failure_class == "scratch_root_exists"

    def test_extra_workspace_file_traversal_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(CaptureError) as exc:
            rcc.setup_scratch(tmp_path, "ws-esc", (("../evil.md", b"x"),))
        assert exc.value.failure_class == "workspace_file_name_invalid"

    def test_cleanup_refuses_symlink_entry(self, tmp_path: Path) -> None:
        setup = rcc.setup_scratch(tmp_path, "sym-1")
        target = tmp_path / "outside.md"
        target.write_text("keep me", encoding="utf-8")
        (setup.root / "workspace" / "link.md").symlink_to(target)
        with pytest.raises(CaptureError) as exc:
            rcc.cleanup_root(setup.root)
        assert exc.value.failure_class == "cleanup_entry_unexpected_type"
        # Root and target survive the refused cleanup.
        assert setup.root.exists()
        assert target.read_text() == "keep me"

    def test_cleanup_refuses_foreign_root(self, tmp_path: Path) -> None:
        setup = rcc.setup_scratch(tmp_path, "foreign-1")
        if os.geteuid() == 0:
            pytest.skip("cannot test foreign ownership as root")
        try:
            import pwd

            other_uid = pwd.getpwnam("daemon").pw_uid
            os.chown(setup.root, other_uid, -1)
        except (KeyError, PermissionError, OSError):
            pytest.skip("cannot chown to another uid here")
        with pytest.raises(CaptureError) as exc:
            rcc.cleanup_root(setup.root)
        assert exc.value.failure_class == "cleanup_root_not_owned"


# ---------------------------------------------------------------------------
# CLI surface.
# ---------------------------------------------------------------------------
def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(UTILITY)] + args,
        capture_output=True,
        text=True,
        timeout=120,
    )


class TestCli:
    def test_version(self) -> None:
        proc = run_cli(["--version"])
        assert proc.returncode == 0
        assert "real-client-capture" in proc.stdout

    def test_check_not_ready_record(self, tmp_path: Path) -> None:
        binary = make_synthetic_binary(tmp_path)
        out_record = tmp_path / "readiness.json"
        proc = run_cli(
            [
                "check",
                "--binary",
                str(binary),
                "--version",
                TEST_VERSION,
                "--sha256",
                sha256_file(binary),
                "--out-record",
                str(out_record),
            ]
        )
        assert proc.returncode == 3
        assert "verdict=not_ready" in proc.stdout
        assert "plugin_catalog_sync_control_unverified" in proc.stdout
        record = json.loads(out_record.read_text())
        assert record["verdict"] == "not_ready"
        # No raw help output in the console summary or the record.
        assert "codex-cli" not in proc.stdout
        assert "ephemeral" not in proc.stdout
        assert "ephemeral" not in out_record.read_text()
        assert out_record.stat().st_mode & 0o777 == 0o600

    def test_check_hash_mismatch(self, tmp_path: Path) -> None:
        binary = make_synthetic_binary(tmp_path)
        proc = run_cli(
            [
                "check",
                "--binary",
                str(binary),
                "--version",
                TEST_VERSION,
                "--sha256",
                "f" * 64,
            ]
        )
        assert proc.returncode == 1
        assert proc.stdout.strip() == "check: binary_hash_mismatch"
        assert proc.stderr == ""

    def test_run_cli_happy_and_sanitized_summary(self, tmp_path: Path) -> None:
        out = protected_out_dir(tmp_path)
        proc = run_cli(
            [
                "run",
                "--child",
                str(FAKE_CHILD),
                "--run-id",
                "cli-1",
                "--out-dir",
                str(out),
                "--deadline-seconds",
                "10",
                "--marker",
                "prompt",
            ]
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert proc.stdout.startswith("run: outcome=completed")
        assert "LEAK-cli-1-prompt" not in proc.stdout
        assert "LEAK-cli-1-prompt" not in proc.stderr
        assert b"LEAK-cli-1-prompt" not in record_blob(out)

    def test_run_cli_rejects_raised_limits(self, tmp_path: Path) -> None:
        out = protected_out_dir(tmp_path)
        proc = run_cli(
            [
                "run",
                "--child",
                str(FAKE_CHILD),
                "--run-id",
                "cli-2",
                "--out-dir",
                str(out),
                "--max-requests",
                "21",
            ]
        )
        assert proc.returncode == 2
        assert proc.stdout.strip() == "run: limits_max_requests_over_hard_cap"


# ---------------------------------------------------------------------------
# Static guarantees: stdlib-only, no OAP awareness, no installed-client
# fallback, no adapter-runtime coupling.
# ---------------------------------------------------------------------------
class TestStaticGuarantees:
    def _source(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def test_stdlib_only_imports(self) -> None:

        allowed = set(sys.stdlib_module_names)
        for path in (UTILITY, FAKE_CHILD):
            for line in self._source(path).splitlines():
                stripped = line.strip()
                if stripped.startswith("import "):
                    names = stripped[len("import ") :].split(",")
                    for name in names:
                        top = name.strip().split(" as ")[0].split(".")[0]
                        assert top in allowed, f"{path.name}: {top}"
                elif stripped.startswith("from "):
                    rest = stripped[len("from ") :].split(" import")[0]
                    top = rest.strip().split(".")[0]
                    assert top in allowed, f"{path.name}: {top}"

    def test_no_oap_or_runtime_coupling(self) -> None:
        blob = self._source(UTILITY) + self._source(FAKE_CHILD)
        assert "oap/active" not in blob
        assert "oap/orders" not in blob
        assert "slaif_local_coding" not in blob
        assert "constitution" not in blob

    def test_no_installed_client_fallback(self, tmp_path: Path) -> None:
        out = protected_out_dir(tmp_path)
        with pytest.raises(CaptureError) as exc:
            rcc.run_capture(
                run_id="nofallback-1",
                out_dir=out,
                child=tmp_path / "does-not-exist.py",
            )
        assert exc.value.failure_class == "synthetic_child_missing"

    def test_child_symlink_rejected(self, tmp_path: Path) -> None:
        out = protected_out_dir(tmp_path)
        link = tmp_path / "child-link.py"
        link.symlink_to(FAKE_CHILD)
        with pytest.raises(CaptureError) as exc:
            rcc.run_capture(
                run_id="symchild-1",
                out_dir=out,
                child=link,
            )
        assert exc.value.failure_class == "synthetic_child_missing"

    def test_utility_version_and_schemas_stable(self) -> None:
        assert rcc.SCHEMA == "slaif-real-client-capture-v1"
        assert rcc.SELECTION_SCHEMA == "slaif-real-client-capture-selection-v1"
        assert rcc.RUN_SCHEMA == "slaif-real-client-capture-run-v1"
        assert rcc.ATTEMPT_SCHEMA == "slaif-real-client-capture-attempt-v1"
        assert rcc.READINESS_SCHEMA == "slaif-real-client-capture-readiness-v1"
        assert rcc.AUTHORIZATION_SCHEMA == ("slaif-real-client-capture-authorization-v1")
        assert rcc.CONTROL_SCHEMA == "slaif-real-client-capture-control-v1"
