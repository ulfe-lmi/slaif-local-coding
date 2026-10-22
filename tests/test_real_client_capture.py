"""Offline adversarial coverage for the 017-i capture utility.

The utility (``scripts/real_client_capture.py``) is a bounded, opt-in,
fail-closed process-capture harness whose ACTUAL-client path is input-
gated (explicit opt-in plus validated readiness/authorization records;
the generated readiness verdict is ``not_ready``) and is not exercised
by any test in this suite. These tests exercise ONLY the offline
surface: synthetic child executables (pinned injected paths; no
installed-client fallback), the in-process owned fake provider, bounded
provider robustness over raw sockets, extraction allowlists,
supervision/timeout/cap accounting, attempt-ledger persistence, and
privacy non-leakage. No test launches an installed client, calls a
model, or touches a real provider.
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
        # process_id is the controller-issued value for call_01 (step 0).
        assert out["process_id"] == "proc_01"
        assert out["output_bytes"] == len(output.encode())
        import hashlib

        assert out["output_digest"] == hashlib.sha256(output.encode()).hexdigest()
        # selection-v2: the exact received selected synthetic result text
        # is retained losslessly for a proven selected frame (byte
        # verification against the owned seeded workspace happens at run
        # time, so it is not yet asserted here).
        assert out["content"] == "alpha file content\n"
        assert out["content_bytes"] == len(b"alpha file content\n")
        assert out["content_verified"] is None

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
        # Digests present (exact raw output bytes).
        output_frames = [f for f in selection["frames"] if f["item_type"] == "function_call_output"]
        assert output_frames
        for frame in output_frames:
            digest = frame["output_digest"]
            assert isinstance(digest, str) and len(digest) == 64
            assert all(c in "0123456789abcdef" for c in digest)
        # selection-v2: the exact selected synthetic read text is
        # retained losslessly and byte-verified against the owned seeded
        # workspace; nothing else from the request (prompt, history,
        # schemas, headers) is ever published.
        read_frames = [
            f
            for f in selection["frames"]
            if f["item_type"] == "function_call_output" and f["call_id"] == "call_01"
        ]
        assert read_frames
        assert read_frames[0]["content"] == "alpha file content\n"
        assert read_frames[0]["content_verified"] is True
        assert read_frames[0]["content_bytes"] == len(b"alpha file content\n")
        assert "Synthetic capture run" not in json.dumps(selection)
        blob = record_blob(result.run_record_path.parent)
        assert b"alpha file content" in blob  # selection record only (0600)
        assert b"Synthetic capture run" not in blob
        # Exact serialized-byte accounting: the run record reports the
        # exact UTF-8 bytes of the published selection.json.
        assert (
            result.run_record["selection"]["selected_bytes_total"]
            == result.selection_path.stat().st_size
        )
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
# 017-j: issued-call selection binding (pure extraction).
# ---------------------------------------------------------------------------
UNSELECTED_MARKER = "SYNTHETIC_UNSELECTED_MARKER_VALUE"


def _payload(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {"model": rcc.SYNTHETIC_MODEL, "input": items}


def _call_item(
    call_id: str = "call_01",
    name: str = "exec_command",
    cmd: str = "cat A.md",
    workdir: str = ".",
) -> dict[str, Any]:
    return {
        "type": "function_call",
        "call_id": call_id,
        "name": name,
        "arguments": json.dumps({"cmd": cmd, "workdir": workdir}),
    }


def _out_item(call_id: str, output: Any) -> dict[str, Any]:
    if isinstance(output, str):
        out: Any = output
    else:
        out = json.dumps(output, sort_keys=True)
    return {"type": "function_call_output", "call_id": call_id, "output": out}


def _ok_read_output(process_id: str = "proc_01") -> dict[str, Any]:
    return {
        "content": "alpha file content\n",
        "exit_code": 0,
        "status": "completed",
        "process_id": process_id,
    }


class TestIssuedCallBinding:
    def _extract(
        self,
        items: list[dict[str, Any]],
        *,
        steps: tuple[Any, ...] | None = None,
        canary: str = "CANARY",
        mode: str = DEFAULT_MODE,
    ) -> tuple[list[dict[str, Any]], dict[str, int]]:
        payload = _payload(items)
        before = json.loads(json.dumps(payload))
        frames, rejections, _ = rcc.extract_frames(
            payload,
            declared_steps=steps or default_steps(),
            canary=canary,
            request_seq=1,
            mode=mode,
        )
        # Input immutability: extraction never mutates the parsed request.
        assert payload == before
        return list(frames), dict(rejections)

    def test_declared_pair_control(self) -> None:
        frames, rejections = self._extract([_call_item(), _out_item("call_01", _ok_read_output())])
        assert rejections == {}
        assert [f["item_type"] for f in frames] == [
            "function_call",
            "function_call_output",
        ]

    @pytest.mark.parametrize(
        "bad_id", ["call_99", "forged_01", "unexpected_123", UNSELECTED_MARKER]
    )
    def test_orphan_unissued_result_never_selected(self, bad_id: str) -> None:
        frames, rejections = self._extract(
            [_out_item(bad_id, {"content": "synthetic unrelated", "status": "completed"})]
        )
        assert frames == []
        assert rejections == {"call_id_unissued": 1}
        # The raw unissued value is stored nowhere in the result.
        blob = json.dumps([frames, rejections])
        assert bad_id not in blob

    def test_unissued_declared_command_id_never_selected(self) -> None:
        for bad_id in ("call_99", "unexpected_123", UNSELECTED_MARKER):
            frames, rejections = self._extract([_call_item(call_id=bad_id)])
            assert frames == []
            assert rejections == {"call_id_unissued": 1}

    def test_later_step_requires_earlier_completed_output(self) -> None:
        # step 1 command with NO step-0 completed output in the input.
        frames, rejections = self._extract([_call_item(call_id="call_02", cmd="sleep 0.3")])
        assert frames == []
        assert rejections == {"call_id_unissued": 1}
        # step-0 output still "running" is not advancement evidence for
        # the later call, but it remains a proven frame of its own
        # issued call.
        frames, rejections = self._extract(
            [
                _call_item(call_id="call_02", cmd="sleep 0.3"),
                _out_item("call_01", {"status": "running", "process_id": "proc_01"}),
            ]
        )
        assert [f["call_id"] for f in frames] == ["call_01"]
        assert [f["item_type"] for f in frames] == ["function_call_output"]
        assert frames[0]["status"] == "running"
        assert rejections == {"call_id_unissued": 1}
        # A forged "completed" output with an unissued process ID is
        # also not advancement evidence: it is rejected, and the later
        # call stays unissued.
        frames, rejections = self._extract(
            [
                _call_item(call_id="call_02", cmd="sleep 0.3"),
                _out_item("call_01", _ok_read_output(process_id="forged_proc_99")),
            ]
        )
        assert frames == []
        assert rejections == {
            "call_id_unissued": 1,
            "metadata_unissued": 1,
        }
        # The forged process ID is stored nowhere in the result.
        assert "forged_proc_99" not in json.dumps([frames, rejections])

    def test_later_step_selected_after_completed_progression(self) -> None:
        frames, rejections = self._extract(
            [
                _call_item(),
                _out_item("call_01", _ok_read_output()),
                _call_item(call_id="call_02", cmd="sleep 0.3"),
            ]
        )
        assert rejections == {}
        # call_01, its output, then the now-issued call_02.
        assert [f["call_id"] for f in frames] == ["call_01", "call_01", "call_02"]
        assert [f["item_type"] for f in frames] == [
            "function_call",
            "function_call_output",
            "function_call",
        ]

    def test_command_of_different_step_than_id_never_selected(self) -> None:
        # call_02 is the sleep step; a "cat A.md" argument names step 0.
        frames, rejections = self._extract(
            [
                _call_item(),
                _out_item("call_01", _ok_read_output()),
                _call_item(call_id="call_02", cmd="cat A.md"),
            ]
        )
        # call_01 + output are proven; the conflicting call_02 is not.
        assert [f["call_id"] for f in frames] == ["call_01", "call_01"]
        assert [f["item_type"] for f in frames] == [
            "function_call",
            "function_call_output",
        ]
        assert rejections == {"call_id_unissued": 1}

    def test_name_of_different_step_than_id_never_selected(self) -> None:
        frames, rejections = self._extract(
            [_call_item(call_id="call_02", name="some_other_tool", cmd="cat A.md")],
            steps=(
                DeclaredStep(
                    index=0,
                    tool_name="some_other_tool",
                    kind="read",
                    path="A.md",
                    seconds=0.0,
                ),
                DeclaredStep(
                    index=1,
                    tool_name="exec_command",
                    kind="sleep",
                    path="",
                    seconds=0.3,
                ),
            ),
        )
        assert frames == []
        assert rejections == {"call_id_unissued": 1}

    def test_custom_call_requires_issued_input_value(self) -> None:
        steps = (
            DeclaredStep(
                index=0,
                tool_name="synthetic_custom",
                kind="read",
                path="A.md",
                seconds=0.0,
            ),
        )
        call = {
            "type": "custom_tool_call",
            "call_id": "call_01",
            "name": "synthetic_custom",
            "input": "not-the-issued-value",
        }
        frames, rejections = self._extract([call], steps=steps, mode="responses-custom-tool")
        assert frames == []
        assert rejections == {"call_id_unissued": 1}
        call["input"] = rcc._issued_custom_input(0)
        frames, rejections = self._extract([call], steps=steps, mode="responses-custom-tool")
        assert rejections == {}
        assert len(frames) == 1

    def test_unissued_process_id_never_stored(self) -> None:
        frames, rejections = self._extract(
            [
                _call_item(),
                _out_item("call_01", _ok_read_output(process_id=UNSELECTED_MARKER)),
            ]
        )
        # Item-level rejection: the forged output is rejected with the
        # fixed reason; the proven issued call frame is retained. The
        # unissued process ID is stored nowhere in the result.
        assert [f["item_type"] for f in frames] == ["function_call"]
        assert frames[0]["call_id"] == "call_01"
        assert rejections == {"metadata_unissued": 1}
        assert UNSELECTED_MARKER not in json.dumps([frames, rejections])

    def test_session_and_chunk_ids_not_issued(self) -> None:
        for key in ("session_id", "chunk_id"):
            out = _ok_read_output()
            out[key] = "sess_01"
            frames, rejections = self._extract([_call_item(), _out_item("call_01", out)])
            # Item-level rejection of the unissued-metadata output; the
            # proven issued call frame is retained.
            assert [f["item_type"] for f in frames] == ["function_call"]
            assert rejections == {"metadata_unissued": 1}

    def test_repeated_history_snapshot_preserves_occurrences(self) -> None:
        call = _call_item()
        out = _out_item("call_01", _ok_read_output())
        frames, rejections = self._extract([call, out, call, out])
        assert rejections == {}
        assert [f["seq"] for f in frames] == [1, 2, 3, 4]
        transitions = rcc.build_transitions(frames)
        assert len(transitions) == 1
        assert transitions[0]["output_frame_count"] == 2
        assert transitions[0]["final_status"] == "completed"

    def test_malformed_unicode_arguments_rejected_not_echoed(self) -> None:
        # ACTUAL malformed value: a lone surrogate (invalid UTF-8
        # candidate) inside the declared-command arguments. The JSON
        # escape is valid on the wire; the parsed value is not.
        evil = "cat A.md\ud800"
        item = _call_item()
        item["arguments"] = json.dumps({"cmd": evil, "workdir": "."})
        frames, rejections = self._extract([item])
        assert frames == []
        assert rejections == {"malformed_unicode": 1}
        assert evil not in json.dumps([frames, rejections])
        assert "\\ud800" not in json.dumps([frames, rejections])

    def test_valid_unicode_arguments_are_typed_not_malformed(self) -> None:
        # Valid non-ASCII Unicode is NOT malformed: it simply fails the
        # declared-command match like any other undeclared text.
        item = _call_item()
        item["arguments"] = json.dumps({"cmd": "cat \u00e9.md", "workdir": "."})
        frames, rejections = self._extract([item])
        assert frames == []
        assert rejections == {"command_not_declared": 1}
        assert "malformed_unicode" not in rejections


# ---------------------------------------------------------------------------
# 017-j: lossless selected synthetic text, byte verification, serialized
# byte cap (public receiver/run surface).
# ---------------------------------------------------------------------------
UNSELECTED_RUN_MARKER = b"SYNTHETIC_UNSELECTED_RUN_MARKER"


class TestSelectionTextRetention:
    def test_selected_text_retained_and_byte_verified(self, tmp_path: Path) -> None:
        result = run_synthetic(
            tmp_path,
            "text-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            out_name="out-text",
        )
        assert result.outcome == "completed"
        selection = result.selection_record
        assert selection is not None
        assert selection["schema"] == "slaif-real-client-capture-selection-v2"
        assert selection["provenance"] == "synthetic-offline"
        assert selection["fixture_authority"] == "none"
        read_frames = [
            f
            for f in selection["frames"]
            if f["item_type"] == "function_call_output" and f["call_id"] == "call_01"
        ]
        assert read_frames
        frame = read_frames[0]
        # Exact received text, exact bytes, verified against the seeded
        # owned workspace file for the declared path.
        assert frame["content"] == "alpha file content\n"
        assert frame["content_bytes"] == len(b"alpha file content\n")
        assert frame["content_verified"] is True
        # Exact-byte digest of the raw output payload still present.
        import hashlib

        assert isinstance(frame["output_digest"], str)
        assert (
            frame["output_digest"]
            == hashlib.sha256(json.dumps(_ok_read_output(), sort_keys=True).encode()).hexdigest()
        )

    def test_tampered_result_text_stripped_not_published(self, tmp_path: Path) -> None:
        child = tmp_path / "tamper_child.py"
        child.write_text(
            "import json, sys, urllib.request\n"
            "control = json.load(open(sys.argv[1]))\n"
            "base = control['provider_base_url']\n"
            "token = control['token']\n"
            "def post():\n"
            "    body = json.dumps({'model': control['model'], 'stream': True,\n"
            "      'input': [{'role': 'user', 'content': [{'type': 'input_text', 'text': 's'}]}],\n"
            "      'tools': [{'type': 'function', 'name': 'exec_command', 'parameters':\n"
            "        {'type': 'object', 'properties': {'cmd': {'type': 'string'},\n"
            "                                          'workdir': {'type': 'string'}},\n"
            "        'required': ['cmd', 'workdir']}}]}).encode()\n"
            "    req = urllib.request.Request(base + '/responses', data=body,\n"
            "      headers={'Authorization': f'Bearer {token}'})\n"
            "    with urllib.request.urlopen(req, timeout=5) as r: return r.read(65536)\n"
            "def call_from(data):\n"
            "    for line in data.decode().splitlines():\n"
            "        if line.startswith('data: '):\n"
            "            event = json.loads(line[6:])\n"
            "            if event.get('type') == 'response.output_item.added':\n"
            "                return event['item']\n"
            "    raise SystemExit(65)\n"
            "data = post()\n"
            "call = call_from(data)\n"
            "value = {'content': 'TAMPERED-CONTENT-\\n', 'status': 'completed',\n"
            "        'exit_code': 0, 'process_id': 'proc_01'}\n"
            "body2 = json.dumps({'model': control['model'], 'stream': True,\n"
            "  'input': [{'role': 'user', 'content': [{'type': 'input_text', 'text': 's'}]},\n"
            "             call,\n"
            "             {'type': 'function_call_output', 'call_id': call['call_id'],\n"
            "              'output': json.dumps(value)}],\n"
            "  'tools': [{'type': 'function', 'name': 'exec_command', 'parameters':\n"
            "    {'type': 'object', 'properties': {'cmd': {'type': 'string'},\n"
            "                                      'workdir': {'type': 'string'}},\n"
            "    'required': ['cmd', 'workdir']}}]}).encode()\n"
            "req2 = urllib.request.Request(base + '/responses', data=body2,\n"
            "  headers={'Authorization': f'Bearer {token}'})\n"
            "try:\n"
            "    urllib.request.urlopen(req2, timeout=5).read(65536)\n"
            "except urllib.error.HTTPError:\n"
            "    pass\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        child.chmod(0o700)
        result = run_synthetic(
            tmp_path,
            "tamper-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            child=child,
            out_name="out-tamper",
        )
        assert result.outcome == "completed"
        selection = result.selection_record
        assert selection is not None
        # The tampered text is NOT the seeded owned-workspace bytes:
        # stripped, metadata + exact-byte digest retained, typed count.
        assert selection["rejected"]["reason_counts"].get("content_unverified") == 1
        out_frames = [f for f in selection["frames"] if f["item_type"] == "function_call_output"]
        assert out_frames
        assert all(f["content"] is None for f in out_frames)
        assert all(f["content_verified"] is False for f in out_frames)
        assert all(
            isinstance(f["output_digest"], str) and len(f["output_digest"]) == 64
            for f in out_frames
        )
        assert b"TAMPERED-CONTENT" not in record_blob(result.run_record_path.parent)

    def test_unissued_result_value_never_persisted(self, tmp_path: Path) -> None:
        child = tmp_path / "unissued_child.py"
        child.write_text(
            "import json, sys, urllib.request\n"
            "control = json.load(open(sys.argv[1]))\n"
            "base = control['provider_base_url']\n"
            "token = control['token']\n"
            "tools = [{'type': 'function', 'name': 'exec_command', 'parameters':\n"
            "  {'type': 'object', 'properties': {'cmd': {'type': 'string'},\n"
            "                                    'workdir': {'type': 'string'}},\n"
            "  'required': ['cmd', 'workdir']}}]\n"
            "history = [{'role': 'user', 'content': [{'type': 'input_text', 'text': 's'}]}]\n"
            "def post():\n"
            "    body = json.dumps({'model': control['model'], 'stream': True,\n"
            "      'input': history, 'tools': tools}).encode()\n"
            "    req = urllib.request.Request(base + '/responses', data=body,\n"
            "      headers={'Authorization': f'Bearer {token}'})\n"
            "    with urllib.request.urlopen(req, timeout=5) as r: return r.read(65536)\n"
            "def call_from(data):\n"
            "    for line in data.decode().splitlines():\n"
            "        if line.startswith('data: '):\n"
            "            event = json.loads(line[6:])\n"
            "            if event.get('type') == 'response.output_item.added':\n"
            "                return event['item']\n"
            "    raise SystemExit(65)\n"
            "call = call_from(post())\n"
            "history.append(call)\n"
            "value = {'content': 'alpha file content\\n', 'status': 'completed',\n"
            "         'exit_code': 0, 'process_id': 'proc_01'}\n"
            "history.append({'type': 'function_call_output',\n"
            "                'call_id': call['call_id'], 'output': json.dumps(value)})\n"
            "history.append({'type': 'function_call_output',\n"
            "                'call_id': 'unissued_99',\n"
            "                'output': json.dumps({'content': 'synthetic unrelated',\n"
            "                                       'status': 'completed',\n"
            "                                       'process_id': '"
            + UNSELECTED_RUN_MARKER.decode()
            + "'})})\n"
            "post()\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        child.chmod(0o700)
        result = run_synthetic(
            tmp_path,
            "unissued-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            child=child,
            out_name="out-unissued",
        )
        assert result.outcome == "completed"
        # The unissued result (and its private value) is rejected with a
        # fixed reason and stored nowhere under the output directory.
        selection = result.selection_record
        assert selection is not None
        assert selection["rejected"]["reason_counts"].get("call_id_unissued") == 1
        assert all(f["call_id"] != "unissued_99" for f in selection["frames"])
        assert UNSELECTED_RUN_MARKER not in record_blob(result.run_record_path.parent)

    def test_serialized_cap_on_published_bytes(self, tmp_path: Path) -> None:
        first = run_synthetic(
            tmp_path,
            "cap0-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            out_name="out-cap0",
        )
        assert first.outcome == "completed"
        size = first.selection_path.stat().st_size
        assert first.run_record["selection"]["selected_bytes_total"] == size
        # A cap smaller than the serialized record: fixed typed failure,
        # no oversized/partial selection artifact.
        small = run_synthetic(
            tmp_path,
            "cap1-1",
            limits=rcc.CaptureLimits.resolved(max_selected_bytes=100, deadline_seconds=10.0),
            out_name="out-cap1",
        )
        assert small.outcome == "selected_over_bound"
        assert small.selection_path is None
        assert not (tmp_path / "out-cap1" / "selection.json").exists()
        assert small.run_record["selection"]["written"] is False
        # Boundary: a cap exactly at the serialized size is NOT an
        # exceedance (accept either the equal-size publish or a
        # truthful over-bound if the rerun's own serialization differs
        # by the self-size fixed point; never a file over the cap).
        boundary = run_synthetic(
            tmp_path,
            "cap2-1",
            limits=rcc.CaptureLimits.resolved(max_selected_bytes=size, deadline_seconds=10.0),
            out_name="out-cap2",
        )
        if boundary.outcome == "completed":
            assert boundary.selection_path.stat().st_size <= size
        else:
            assert boundary.outcome == "selected_over_bound"
            assert not (tmp_path / "out-cap2" / "selection.json").exists()


# ---------------------------------------------------------------------------
# 017-j: centralized per-run request budget on the owned provider.
# ---------------------------------------------------------------------------
class TestProviderBudgetCentralization:
    def _provider(self, limits: Any) -> tuple[Any, Any, int]:
        state = rcc.ProviderState(limits, rcc.SYNTHETIC_MODEL, DEFAULT_MODE, "tok")
        provider = rcc.FakeProvider(
            state=state, steps=rcc.default_declared_steps(), canary="CANARY"
        )
        port = provider.start()
        return provider, state, port

    def _raw(self, port: int, request: bytes) -> str:
        with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
            sock.sendall(request)
            chunks: list[bytes] = []
            while True:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk)
                if len(b"".join(chunks)) > 65536:
                    break
            return b"".join(chunks).decode("utf-8", "replace")

    def test_unsupported_routes_consume_budget(self, tmp_path: Path) -> None:
        provider, state, port = self._provider(rcc.CaptureLimits.resolved(max_requests=2))
        try:
            codes: list[str] = []
            for _ in range(3):
                response = self._raw(
                    port,
                    (
                        f"GET /v1/unsupported HTTP/1.1\r\n"
                        f"Host: 127.0.0.1:{port}\r\n"
                        f"Authorization: Bearer tok\r\n\r\n"
                    ).encode(),
                )
                codes.append(response.split(" ", 2)[1])
            assert codes[:2] == ["404", "404"]
            assert codes[2] == "429"
            assert state.request_limit_hit
        finally:
            provider.stop()

    def test_unsupported_post_consumes_budget_without_body_read(self, tmp_path: Path) -> None:
        provider, state, port = self._provider(rcc.CaptureLimits.resolved(max_requests=2))
        try:
            response = self._raw(
                port,
                (
                    f"POST /v1/bogus HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{port}\r\n"
                    f"Authorization: Bearer tok\r\n"
                    f"Content-Length: 5\r\n\r\nhello"
                ).encode(),
            )
            assert response.split(" ", 2)[1] == "404"
            assert state.request_count == 1
            response = self._raw(
                port,
                (
                    f"POST /v1/bogus HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{port}\r\n"
                    f"Authorization: Bearer tok\r\n"
                    f"Content-Length: 5\r\n\r\nhello"
                ).encode(),
            )
            assert response.split(" ", 2)[1] == "404"
            response = self._raw(
                port,
                (
                    f"POST /v1/bogus HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{port}\r\n"
                    f"Authorization: Bearer tok\r\n"
                    f"Content-Length: 5\r\n\r\nhello"
                ).encode(),
            )
            assert response.split(" ", 2)[1] == "429"
            assert state.request_limit_hit
        finally:
            provider.stop()

    def test_oversized_body_consumes_budget(self, tmp_path: Path) -> None:
        provider, state, port = self._provider(
            rcc.CaptureLimits.resolved(max_requests=1, max_inbound_bytes=64)
        )
        try:
            body = b"x" * 512
            response = self._raw(
                port,
                (
                    f"POST /v1/responses HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{port}\r\n"
                    f"Authorization: Bearer tok\r\n"
                    f"Content-Length: {len(body)}\r\n\r\n"
                ).encode()
                + body,
            )
            assert response.split(" ", 2)[1] == "413"
            assert state.request_count == 1
            response = self._raw(
                port,
                (
                    f"GET /v1/models HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{port}\r\n"
                    f"Authorization: Bearer tok\r\n\r\n"
                ).encode(),
            )
            assert response.split(" ", 2)[1] == "429"
            assert state.request_limit_hit
        finally:
            provider.stop()

    def test_auth_failure_value_free_and_counted(self, tmp_path: Path) -> None:
        provider, state, port = self._provider(rcc.CaptureLimits.resolved(max_requests=2))
        try:
            response = self._raw(
                port,
                (
                    f"GET /v1/models HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{port}\r\n"
                    f"Authorization: Bearer WRONG-TOKEN-VALUE\r\n\r\n"
                ).encode(),
            )
            assert response.split(" ", 2)[1] == "401"
            assert state.auth_rejected == 1
            # Counted (cannot evade the cap) but value-free: no token
            # value is recorded anywhere in the provider state.
            assert state.request_count == 1
            blob = json.dumps(state.status_counts).encode() + str(state).encode()
            assert b"WRONG-TOKEN-VALUE" not in blob
        finally:
            provider.stop()


# ---------------------------------------------------------------------------
# 017-j: bounded preflight output collection.
# ---------------------------------------------------------------------------
class TestPreflightBoundedOutput:
    def _binary(self, tmp_path: Path, body: str) -> tuple[Path, str]:
        binary = tmp_path / f"probe-{abs(hash(body)) % 100000}"
        binary.write_text(f"#!{sys.executable}\n{body}", encoding="utf-8")
        binary.chmod(0o700)
        return binary, sha256_file(binary)

    def test_version_overflow_is_typed_and_bounded(self, tmp_path: Path) -> None:
        body = (
            "import sys\n"
            "if '--version' in sys.argv:\n"
            "    sys.stdout.buffer.write(b'codex-cli 9.9.9-test\\n')\n"
            "for _ in range(16384):\n"
            "    sys.stdout.buffer.write(b'x' * 1024)\n"
        )
        binary, sha = self._binary(tmp_path, body)
        with pytest.raises(CaptureError) as exc:
            rcc.preflight_binary(binary, TEST_VERSION, sha)
        assert exc.value.failure_class == "binary_version_over_bound"
        # Fixed, non-echoing failure class only.
        assert "x" * 100 not in str(exc.value)

    def test_hanging_probe_is_typed_timeout(self, tmp_path: Path) -> None:
        body = (
            "import sys, time\n"
            "if '--version' in sys.argv:\n"
            "    sys.stdout.buffer.write(b'codex-cli 9.9.9-test\\n')\n"
            "    sys.stdout.flush()\n"
            "else:\n"
            "    time.sleep(30)\n"
        )
        binary, sha = self._binary(tmp_path, body)
        with pytest.raises(CaptureError) as exc:
            rcc.preflight_binary(binary, TEST_VERSION, sha, probe_timeout=1.5)
        assert exc.value.failure_class == "binary_probe_timeout"

    def test_help_overflow_keeps_legacy_class(self, tmp_path: Path) -> None:
        binary = make_synthetic_binary(tmp_path, help_bytes=rcc.HARD_MAX_HELP_BYTES + 1024)
        with pytest.raises(CaptureError) as exc:
            rcc.preflight_binary(binary, TEST_VERSION, sha256_file(binary))
        assert exc.value.failure_class == "binary_help_over_bound"


# ---------------------------------------------------------------------------
# 017-j: protected directories preserve pre-existing permissions/files.
# ---------------------------------------------------------------------------
class TestProtectedDirNoMutation:
    def test_preexisting_shared_mode_preserved_on_rejection(self, tmp_path: Path) -> None:
        dest = tmp_path / "shared-out"
        dest.mkdir(mode=0o755)
        dest.chmod(0o755)
        sentinel = dest / "preexisting"
        sentinel.write_text("synthetic unrelated file", encoding="utf-8")
        before = sentinel.read_bytes()
        mode_before = dest.stat().st_mode & 0o777
        with pytest.raises(CaptureError):
            rcc.run_capture(
                run_id="guard-1",
                out_dir=dest,
                child=tmp_path / "not-a-client",
                child_kind="actual",
                allow_actual_client=False,
            )
        assert dest.stat().st_mode & 0o777 == mode_before  # never chmoded
        assert sentinel.read_bytes() == before
        # No new files in the pre-existing directory.
        assert {x.name for x in dest.iterdir()} == {"preexisting"}

    def test_preexisting_group_writable_rejected_without_mutation(self, tmp_path: Path) -> None:
        dest = tmp_path / "group-out"
        dest.mkdir(mode=0o770)
        dest.chmod(0o770)
        sentinel = dest / "keep"
        sentinel.write_text("keep", encoding="utf-8")
        mode_before = dest.stat().st_mode & 0o777
        with pytest.raises(CaptureError) as exc:
            rcc._protected_dir(dest)
        assert exc.value.failure_class == "protected_dir_unsafe_preexisting"
        assert dest.stat().st_mode & 0o777 == mode_before
        assert sentinel.read_bytes() == b"keep"

    def test_preexisting_symlink_rejected(self, tmp_path: Path) -> None:
        real = tmp_path / "real"
        real.mkdir(mode=0o700)
        link = tmp_path / "link-out"
        link.symlink_to(real)
        with pytest.raises(CaptureError) as exc:
            rcc._protected_dir(link)
        assert exc.value.failure_class == "protected_dir_invalid"
        assert link.is_symlink()
        assert not real.exists() or set(real.iterdir()) == set()

    def test_preexisting_file_rejected(self, tmp_path: Path) -> None:
        target = tmp_path / "a-file"
        target.write_text("x", encoding="utf-8")
        with pytest.raises(CaptureError) as exc:
            rcc._protected_dir(target)
        assert exc.value.failure_class == "protected_dir_invalid"
        assert target.read_text() == "x"

    def test_foreign_owned_rejected_simulated_uid(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        dest = tmp_path / "foreign-out"
        dest.mkdir(mode=0o700)
        mode_before = dest.stat().st_mode & 0o777
        # Simulated caller-UID mismatch (deterministic, non-root): the
        # directory is real and owned by the test user, but the caller
        # presents a different uid to the ownership guard.
        real_uid = os.getuid()
        monkeypatch.setattr(os, "getuid", lambda: real_uid + 1)
        with pytest.raises(CaptureError) as exc:
            rcc._protected_dir(dest)
        assert exc.value.failure_class == "protected_dir_not_owned"
        assert dest.stat().st_mode & 0o777 == mode_before  # never chmoded

    def test_created_output_dir_is_0700(self, tmp_path: Path) -> None:
        dest = tmp_path / "fresh-out"
        rcc._protected_dir(dest)
        assert dest.stat().st_mode & 0o777 == 0o700


# ---------------------------------------------------------------------------
# 017-j: absolute active-run deadline across owned descendants.
# ---------------------------------------------------------------------------
class TestDescendantDeadline:
    def _run(self, tmp_path: Path, code: str, deadline: float) -> Any:
        child = tmp_path / "leader.py"
        child.write_text(code, encoding="utf-8")
        child.chmod(0o700)
        return rcc.run_child(
            argv=[sys.executable, str(child)],
            env={"PATH": "/usr/bin:/bin"},
            cwd=tmp_path,
            limits=rcc.CaptureLimits.resolved(deadline_seconds=deadline),
        )

    def test_normal_exit_control(self, tmp_path: Path) -> None:
        facts = self._run(tmp_path, "raise SystemExit(0)\n", 0.25)
        assert facts.returncode == 0
        assert not facts.timed_out
        assert facts.group_cleanup_verified

    def test_exited_leader_does_not_bypass_descendant_deadline(self, tmp_path: Path) -> None:
        marker = tmp_path / "late-descendant-marker"
        child_code = (
            "import time; from pathlib import Path; "
            f"time.sleep(2); Path({str(marker)!r}).write_text('synthetic late execution'); "
            "time.sleep(1)"
        )
        code = f"import subprocess, sys\nsubprocess.Popen([sys.executable, '-c', {child_code!r}])\n"
        facts = self._run(tmp_path, code, 0.25)
        # The descendant is terminated before it can write at ~2s.
        assert not marker.exists()
        assert facts.group_cleanup_verified
        # Bounded, reported teardown window.
        assert facts.teardown_seconds is not None
        assert 0 <= facts.teardown_seconds <= rcc.TEARDOWN_GRACE_SECONDS + 5

    def test_descendant_finishing_inside_deadline_survives(self, tmp_path: Path) -> None:
        marker = tmp_path / "early-descendant-marker"
        child_code = (
            "import time; from pathlib import Path; "
            f"time.sleep(0.3); Path({str(marker)!r}).write_text('synthetic early execution'); "
            "time.sleep(0.2)"
        )
        code = (
            "import subprocess, sys\n"
            f"subprocess.Popen([sys.executable, '-c', {child_code!r}])\n"
            "import time\n"
            "time.sleep(1.5)\n"
        )
        facts = self._run(tmp_path, code, 5.0)
        assert facts.returncode == 0
        assert not facts.timed_out
        assert marker.exists()  # finished inside the deadline: untouched
        assert facts.group_cleanup_verified


# ---------------------------------------------------------------------------
# 017-j: readiness record closure (closed sets, types, ownership, bounds).
# ---------------------------------------------------------------------------
class TestReadinessRecordClosure:
    def _facts(self) -> Any:
        return rcc.BinaryFacts(
            version="review-version",
            sha256="a" * 64,
            detected_flags=(),
            help_complete=True,
        )

    def _generated_record(self, facts: Any) -> dict[str, Any]:
        return cast("dict[str, Any]", rcc.evaluate_startup_readiness(facts).to_record())

    def test_generated_record_round_trips(self, tmp_path: Path) -> None:
        facts = self._facts()
        record = self._generated_record(facts)
        meta = tmp_path / "readiness.json"
        write_json_0600(meta, record)
        loaded = rcc.load_readiness_record(meta, facts)
        assert loaded.to_record() == record
        assert loaded.verdict == "not_ready"

    def test_reasons_closed_enum(self, tmp_path: Path) -> None:
        facts = self._facts()
        record = self._generated_record(facts)
        record["reasons"] = [UNSELECTED_MARKER]
        meta = tmp_path / "readiness-reasons.json"
        write_json_0600(meta, record)
        with pytest.raises(CaptureError) as exc:
            rcc.load_readiness_record(meta, facts)
        assert exc.value.failure_class == "readiness_record_invalid"
        assert UNSELECTED_MARKER not in repr(exc.value)

    def test_unknown_field_rejected(self, tmp_path: Path) -> None:
        facts = self._facts()
        record = self._generated_record(facts)
        record["detected_flags"] = [UNSELECTED_MARKER]
        meta = tmp_path / "readiness-flags.json"
        write_json_0600(meta, record)
        with pytest.raises(CaptureError) as exc:
            rcc.load_readiness_record(meta, facts)
        assert exc.value.failure_class == "readiness_record_invalid"
        assert UNSELECTED_MARKER not in repr(exc.value)

    def test_flag_count_binding(self, tmp_path: Path) -> None:
        facts = self._facts()
        record = self._generated_record(facts)
        record["detected_flag_count"] = 5
        meta = tmp_path / "readiness-count.json"
        write_json_0600(meta, record)
        with pytest.raises(CaptureError) as exc:
            rcc.load_readiness_record(meta, facts)
        assert exc.value.failure_class == "readiness_record_binding_mismatch"

    def test_control_candidates_closed(self, tmp_path: Path) -> None:
        facts = self._facts()
        record = self._generated_record(facts)
        record["control_candidates"][0]["status"] = "verified"
        meta = tmp_path / "readiness-candidates.json"
        write_json_0600(meta, record)
        with pytest.raises(CaptureError):
            rcc.load_readiness_record(meta, facts)

    def test_group_readable_record_rejected(self, tmp_path: Path) -> None:
        facts = self._facts()
        record = self._generated_record(facts)
        meta = tmp_path / "readiness-mode.json"
        meta.write_text(json.dumps(record))
        meta.chmod(0o644)
        with pytest.raises(CaptureError) as exc:
            rcc.load_readiness_record(meta, facts)
        assert exc.value.failure_class == "readiness_record_unsafe_mode"

    def test_symlink_record_rejected(self, tmp_path: Path) -> None:
        facts = self._facts()
        record = self._generated_record(facts)
        real = tmp_path / "real-readiness.json"
        write_json_0600(real, record)
        link = tmp_path / "link-readiness.json"
        link.symlink_to(real)
        with pytest.raises(CaptureError):
            rcc.load_readiness_record(link, facts)

    def test_foreign_owned_record_rejected_simulated_uid(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Simulated caller-UID mismatch (deterministic, non-root): the
        # record is real and owned by the test user, but the caller
        # presents a different uid to the ownership guard.
        facts = self._facts()
        record = self._generated_record(facts)
        meta = tmp_path / "readiness-foreign.json"
        write_json_0600(meta, record)
        real_uid = os.getuid()
        monkeypatch.setattr(os, "getuid", lambda: real_uid + 1)
        with pytest.raises(CaptureError) as exc:
            rcc.load_readiness_record(meta, facts)
        assert exc.value.failure_class == "readiness_record_not_owned"
        assert meta.read_bytes()  # file preserved


# ---------------------------------------------------------------------------
# 017-j: deterministic non-root proof of the cleanup ownership guard
# (real synthetic root + simulated caller-UID mismatch). The optional
# real-chown environment test above may remain explicitly skipped.
# ---------------------------------------------------------------------------
class TestCleanupOwnershipGuardSimulated:
    def test_cleanup_refuses_foreign_root_simulated_uid(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        setup = rcc.setup_scratch(tmp_path, "sim-foreign-1")
        inner = setup.root / "workspace" / "A.md"
        inner_bytes = inner.read_bytes()
        real_uid = os.getuid()
        monkeypatch.setattr(os, "getuid", lambda: real_uid + 1)
        with pytest.raises(CaptureError) as exc:
            rcc.cleanup_root(setup.root)
        assert exc.value.failure_class == "cleanup_root_not_owned"
        # Files preserved on rejection.
        assert setup.root.exists()
        assert inner.read_bytes() == inner_bytes


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
        assert rcc.SELECTION_SCHEMA == "slaif-real-client-capture-selection-v2"
        assert rcc.RUN_SCHEMA == "slaif-real-client-capture-run-v1"
        assert rcc.ATTEMPT_SCHEMA == "slaif-real-client-capture-attempt-v1"
        assert rcc.READINESS_SCHEMA == "slaif-real-client-capture-readiness-v1"
        assert rcc.AUTHORIZATION_SCHEMA == ("slaif-real-client-capture-authorization-v1")
        assert rcc.CONTROL_SCHEMA == "slaif-real-client-capture-control-v1"


# ---------------------------------------------------------------------------
# 017-k: runtime issued-registry binding (public receiver lifecycle).
# ---------------------------------------------------------------------------
RUNTIME_CHILD_TEMPLATE = """
import json, sys, urllib.request, urllib.error

MODE = "__MODE__"

def main():
    c = json.load(open(sys.argv[1]))
    mode = MODE
    tools = [{"type": "function", "name": "exec_command", "parameters":
        {"type": "object", "properties": {"cmd": {"type": "string"},
                                          "workdir": {"type": "string"}},
        "required": ["cmd", "workdir"]}}]
    user = [{"role": "user", "content": [{"type": "input_text", "text": "s"}]}]
    def post(history):
        body = json.dumps({"model": c["model"], "stream": True,
                           "input": history, "tools": tools}).encode()
        req = urllib.request.Request(c["provider_base_url"] + "/responses",
                                     data=body,
                                     headers={"Authorization": "Bearer " + c["token"]})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = r.read(65536)
        items = []
        for line in data.decode().splitlines():
            if line.startswith("data: "):
                ev = json.loads(line[6:])
                if ev.get("type") == "response.output_item.added":
                    items.append(ev["item"])
        return items
    def call(call_id, cmd):
        return {"type": "function_call", "call_id": call_id,
                "name": "exec_command",
                "arguments": json.dumps({"cmd": cmd, "workdir": "."})}
    def out(call_id, content, status, proc):
        return {"type": "function_call_output", "call_id": call_id,
                "output": json.dumps({"content": content, "status": status,
                                      "exit_code": 0, "process_id": proc})}
    c1 = call("call_01", "cat A.md")
    o1 = out("call_01", "alpha file content\\n", "completed", "proc_01")
    c2 = call("call_02", "sleep 0.3")
    o2 = out("call_02", "", "completed", "proc_02")
    if mode == "preloaded_first":
        # Exact call01/catA/result preloaded BEFORE any controller issue.
        items = post(user + [c1, o1])
        issued = items[0]
        post(user + [issued, out(issued["call_id"], "alpha file content\\n",
                                 "completed", "proc_01")])
    elif mode == "preloaded_later":
        # call02 (and its precondition) preloaded before any issue of it.
        items = post(user + [c1, o1, c2])
        i1 = items[0]
        items = post(user + [i1, o1])
        i2 = items[0]
        post(user + [i1, o1, i2, o2])
    elif mode == "forged_progression":
        # Forged inbound completed progress for call01 while offering
        # call02 early; the controller's own issuance is the evidence.
        items = post(user + [c1, o1, c2])
        i1 = items[0]
        items = post(user + [c1, o1, c2])
        i2 = items[0]
        post(user + [i1, o1, i2, o2])
    else:
        items = post(user)
        issued = items[0]
        post(user + [issued, out(issued["call_id"], "alpha file content\\n",
                                 "completed", "proc_01")])
    return 0

sys.exit(main())
"""


def write_runtime_child(tmp_path: Path, mode: str) -> Path:
    child = tmp_path / f"runtime_child_{mode}.py"
    child.write_text(RUNTIME_CHILD_TEMPLATE.replace("__MODE__", mode), encoding="utf-8")
    child.chmod(0o700)
    return child


class TestIssuedRegistryRuntime:
    def _run(self, tmp_path: Path, mode: str, out_name: str) -> Any:
        return run_synthetic(
            tmp_path,
            f"rt-{mode}",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            child=write_runtime_child(tmp_path, mode),
            out_name=out_name,
        )

    def test_preloaded_first_call_before_issue_is_not_selected(self, tmp_path: Path) -> None:
        result = self._run(tmp_path, "preloaded_first", "out-rt-pre1")
        assert result.outcome == "completed"
        selection = result.selection_record
        assert selection is not None
        frames = selection["frames"]
        # The preloaded pair in request 1 is selected NOWHERE.
        assert not [f for f in frames if f["request_seq"] == 1]
        # The controller-issued echo in request 2 IS selected (2 frames).
        req2 = [f for f in frames if f["request_seq"] == 2]
        assert [f["item_type"] for f in req2] == ["function_call", "function_call_output"]
        # Both preloaded items rejected with the fixed reason.
        assert selection["rejected"]["reason_counts"]["call_id_unissued"] == 2
        # The proven echo is byte-verified against the owned workspace.
        out_frame = [f for f in req2 if f["item_type"] == "function_call_output"][0]
        assert out_frame["content"] == "alpha file content\n"
        assert out_frame["content_verified"] is True

    def test_preloaded_later_call_before_issue_is_not_selected(self, tmp_path: Path) -> None:
        result = self._run(tmp_path, "preloaded_later", "out-rt-pre2")
        assert result.outcome == "completed"
        selection = result.selection_record
        assert selection is not None
        frames = selection["frames"]
        assert not [f for f in frames if f["request_seq"] == 1]
        # call_02 frames appear ONLY after the controller issued it
        # (request 3), never at the preloaded request 1 or 2.
        c2_frames = [f for f in frames if f["call_id"] == "call_02"]
        assert c2_frames and all(f["request_seq"] == 3 for f in c2_frames)
        assert selection["rejected"]["reason_counts"]["call_id_unissued"] == 3
        # Sleep-step empty payload verified.
        sleep_out = [
            f
            for f in c2_frames
            if f["item_type"] == "function_call_output" and f["status"] == "completed"
        ]
        assert sleep_out and sleep_out[0]["content_verified"] is True

    def test_forged_inbound_progression_never_selects_early_call(self, tmp_path: Path) -> None:
        result = self._run(tmp_path, "forged_progression", "out-rt-forged")
        assert result.outcome == "completed"
        selection = result.selection_record
        assert selection is not None
        frames = selection["frames"]
        # No frame at all in request 1 (forged progress + early call02).
        assert not [f for f in frames if f["request_seq"] == 1]
        # Request 2 selects only the actually-issued call_01 pair.
        req2 = [f for f in frames if f["request_seq"] == 2]
        assert [f["call_id"] for f in req2] == ["call_01", "call_01"]
        # call_02 selected only once the controller issued it (request 3).
        c2_frames = [f for f in frames if f["call_id"] == "call_02"]
        assert c2_frames and all(f["request_seq"] == 3 for f in c2_frames)
        # 3 rejections in request 1 + 1 in request 2 (the late call02).
        assert selection["rejected"]["reason_counts"]["call_id_unissued"] == 4

    def test_actual_issued_receiver_control(self, tmp_path: Path) -> None:
        result = self._run(tmp_path, "normal", "out-rt-normal")
        assert result.outcome == "completed"
        selection = result.selection_record
        assert selection is not None
        frames = selection["frames"]
        assert selection["rejected"]["reason_counts"].get("call_id_unissued", 0) == 0
        out_frames = [f for f in frames if f["item_type"] == "function_call_output"]
        assert out_frames and all(f["content_verified"] is True for f in out_frames)


class TestWrongFamilyUnderOfferedSchema:
    def _extract(
        self, items: list[dict[str, Any]], mode: str
    ) -> tuple[list[dict[str, Any]], dict[str, int]]:
        payload = {"model": rcc.SYNTHETIC_MODEL, "input": items}
        frames, rejections, _ = rcc.extract_frames(
            payload,
            declared_steps=rcc.default_declared_steps(),
            canary="CANARY",
            request_seq=1,
            mode=mode,
        )
        return list(frames), dict(rejections)

    def test_custom_call_in_function_mode_rejected(self) -> None:
        frames, rejections = self._extract(
            [
                {
                    "type": "custom_tool_call",
                    "call_id": "call_01",
                    "name": "exec_command",
                    "input": "synthetic-custom-input-01",
                }
            ],
            "responses-function-tool",
        )
        assert frames == []
        assert rejections == {"input_shape_unsupported": 1}

    def test_function_call_in_custom_mode_rejected(self) -> None:
        frames, rejections = self._extract(
            [
                {
                    "type": "function_call",
                    "call_id": "call_01",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat A.md", "workdir": "."}),
                }
            ],
            "responses-custom-tool",
        )
        assert frames == []
        assert rejections == {"input_shape_unsupported": 1}

    def test_matching_family_control(self) -> None:
        frames, rejections = self._extract(
            [_call_item(), _out_item("call_01", _ok_read_output())],
            "responses-function-tool",
        )
        assert rejections == {}
        assert len(frames) == 2


# ---------------------------------------------------------------------------
# 017-k: finalization quiesce (freeze before validation/publication).
# ---------------------------------------------------------------------------
LATE_MARKER = "SYNTHETIC_LATE_UNVERIFIED_VALUE"


class TestFinalizationQuiesce:
    def _patch_stop_injection(self, monkeypatch: pytest.MonkeyPatch, held: dict[str, Any]) -> None:
        original_start = rcc.FakeProvider.start
        original_stop = rcc.FakeProvider.stop

        def start(self_provider: Any) -> int:
            port: int = original_start(self_provider)
            held["port"] = port
            return port

        def stop(self_provider: Any) -> None:
            if not held.get("injected"):
                held["injected"] = True
                import urllib.error
                import urllib.request

                state = self_provider.state
                call = {
                    "type": "function_call",
                    "call_id": "call_01",
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": "cat A.md", "workdir": "."}),
                }
                output = {
                    "type": "function_call_output",
                    "call_id": "call_01",
                    "output": json.dumps(
                        {
                            "content": LATE_MARKER,
                            "status": "completed",
                            "exit_code": 0,
                            "process_id": "proc_01",
                        }
                    ),
                }
                tools = [
                    {
                        "type": "function",
                        "name": "exec_command",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "cmd": {"type": "string"},
                                "workdir": {"type": "string"},
                            },
                            "required": ["cmd", "workdir"],
                        },
                    }
                ]
                body = json.dumps(
                    {"model": state.model, "stream": True, "input": [call, output], "tools": tools}
                ).encode()
                request = urllib.request.Request(
                    f"http://127.0.0.1:{held['port']}/v1/responses",
                    data=body,
                    headers={
                        "Authorization": f"Bearer {state.token}",
                        "Content-Type": "application/json",
                    },
                )
                try:
                    with urllib.request.urlopen(request, timeout=2) as response:
                        response.read(65536)
                except (urllib.error.URLError, TimeoutError, OSError):
                    pass
            original_stop(self_provider)

        monkeypatch.setattr(rcc.FakeProvider, "start", start)
        monkeypatch.setattr(rcc.FakeProvider, "stop", stop)

    def test_normal_receiver_finalization_control(self, tmp_path: Path) -> None:
        result = run_synthetic(
            tmp_path, "fin-1", limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0)
        )
        assert result.outcome == "completed"
        assert result.selection_path is not None and result.selection_path.is_file()
        assert result.run_record["provider"]["frozen"] is True

    def test_request_at_shutdown_boundary_never_persists_unverified_text(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        held: dict[str, Any] = {}
        self._patch_stop_injection(monkeypatch, held)
        out = protected_out_dir(tmp_path)
        result = rcc.run_capture(
            run_id="fin-2",
            out_dir=out,
            child=FAKE_CHILD,
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            child_kind="synthetic",
        )
        assert held.get("injected") is True
        assert result.outcome == "completed"
        # The late unverified text is stored NOWHERE under the output
        # directory (selection, run record, attempt, scratch).
        assert LATE_MARKER.encode() not in record_blob(out)
        selection = result.selection_record
        assert selection is not None
        # Honest accounting: the late known-issued frame was byte-
        # verified and stripped (metadata + digest only).
        assert selection["rejected"]["reason_counts"].get("content_unverified") == 1
        late_frames = [
            f
            for f in selection["frames"]
            if f["item_type"] == "function_call_output" and f["content_verified"] is False
        ]
        assert late_frames
        assert all(f["content"] is None for f in late_frames)
        assert result.run_record["provider"]["frozen"] is True
        assert result.run_record["provider"]["teardown_incomplete"] is False

    @staticmethod
    def _body(history: list[dict[str, Any]]) -> bytes:
        return json.dumps(
            {
                "model": rcc.SYNTHETIC_MODEL,
                "stream": True,
                "input": history,
                "tools": [
                    {
                        "type": "function",
                        "name": "exec_command",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "cmd": {"type": "string"},
                                "workdir": {"type": "string"},
                            },
                            "required": ["cmd", "workdir"],
                        },
                    }
                ],
            }
        ).encode()

    def test_frozen_provider_rejects_appends_and_snapshot_is_final(self, tmp_path: Path) -> None:
        state = rcc.ProviderState(
            rcc.CaptureLimits.resolved(), rcc.SYNTHETIC_MODEL, DEFAULT_MODE, "tok"
        )
        provider = rcc.FakeProvider(
            state=state, steps=rcc.default_declared_steps(), canary="CANARY"
        )
        provider.start()
        user_only = self._body([{"role": "user", "content": [{"type": "input_text", "text": "s"}]}])
        try:
            status, _ = provider.handle_responses_post(user_only)
            assert status == 200  # controller issues call_01 here
            pair = self._body(
                [
                    {"role": "user", "content": [{"type": "input_text", "text": "s"}]},
                    {
                        "type": "function_call",
                        "call_id": "call_01",
                        "name": "exec_command",
                        "arguments": json.dumps({"cmd": "cat A.md", "workdir": "."}),
                    },
                    _out_item("call_01", _ok_read_output()),
                ]
            )
            status, _ = provider.handle_responses_post(pair)
            assert status == 200
            assert len(state.frames) == 2
        finally:
            pass
        provider.stop()
        assert state.frozen is True
        snapshot_before = provider.frame_snapshot()
        # Append attempts after the freeze gate are rejected with a
        # fixed typed status and never reach the frame state.
        status, _ = provider.handle_responses_post(self._body([]))
        assert status == 503
        assert state.post_freeze_rejected == 1
        snapshot_after = provider.frame_snapshot()
        assert snapshot_after == snapshot_before
        assert len(snapshot_after) == 2

    def test_stop_is_bounded_with_stalled_inflight_handler(self, tmp_path: Path) -> None:
        state = rcc.ProviderState(
            rcc.CaptureLimits.resolved(), rcc.SYNTHETIC_MODEL, DEFAULT_MODE, "tok"
        )
        provider = rcc.FakeProvider(
            state=state, steps=rcc.default_declared_steps(), canary="CANARY"
        )
        port = provider.start()
        try:
            # A connection that sends headers but never finishes the
            # body: the handler is in flight, bounded by the 2 s read
            # timeout. stop() must join it under the bounded grace,
            # never hang, and never let it append.
            sock = socket.create_connection(("127.0.0.1", port), timeout=5)
            sock.sendall(
                b"POST /v1/responses HTTP/1.1\r\n"
                b"Host: 127.0.0.1\r\n"
                b"Authorization: Bearer tok\r\n"
                b"Content-Length: 10\r\n"
                b"\r\n"
            )
            import time as _time

            _time.sleep(0.3)  # let the handler spawn and block on the body
            started = _time.monotonic()
            provider.stop()
            elapsed = _time.monotonic() - started
            sock.close()
            assert elapsed < 8.0
            assert state.frozen is True
            assert state.teardown_incomplete is False
            assert state.frames == []
        finally:
            provider.stop()

    def test_build_selection_without_explicit_snapshot_is_pure_facade_control(
        self,
    ) -> None:
        # The 017-j public call form (no explicit snapshot) is preserved
        # for the pure-facade fixture control: the caller owns the static
        # frame state, so there is no live receiver or late-append
        # surface. The runtime finalization path (run_capture) always
        # passes the explicit frozen snapshot, and both forms agree on
        # the same static state.
        state = rcc.ProviderState(
            rcc.CaptureLimits.resolved(), rcc.SYNTHETIC_MODEL, DEFAULT_MODE, "tok"
        )
        payload = {
            "model": rcc.SYNTHETIC_MODEL,
            "input": [_call_item(), _out_item("call_01", _ok_read_output())],
        }
        frames, rejections, _ = rcc.extract_frames(
            payload,
            declared_steps=rcc.default_declared_steps(),
            canary="CANARY",
            request_seq=1,
            mode=DEFAULT_MODE,
        )
        assert rejections == {}
        state.frames = frames
        steps = rcc.default_declared_steps()
        kwargs = dict(
            run_id="pure-facade",
            state=state,
            steps=steps,
            deadline_seconds=1.0,
            elapsed_seconds=0.001,
            child_kind="synthetic",
            client_version=None,
            client_sha256=None,
        )
        implicit = rcc.build_selection(**kwargs)
        explicit = rcc.build_selection(frames=list(state.frames), **kwargs)
        assert explicit == implicit
        texts = [f.get("content") for f in implicit["frames"]]
        assert "alpha file content\n" in texts


# ---------------------------------------------------------------------------
# 017-k: all-method / error-path request accounting and bounded handlers.
# ---------------------------------------------------------------------------
class TestMethodAccounting:
    def _provider(self) -> tuple[Any, Any, int]:
        state = rcc.ProviderState(
            rcc.CaptureLimits.resolved(max_requests=2),
            rcc.SYNTHETIC_MODEL,
            DEFAULT_MODE,
            "tok",
        )
        provider = rcc.FakeProvider(
            state=state, steps=rcc.default_declared_steps(), canary="CANARY"
        )
        port = provider.start()
        return provider, state, port

    def _raw(self, port: int, request: bytes) -> bytes:
        with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
            sock.sendall(request)
            chunks: list[bytes] = []
            while True:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk)
                if len(b"".join(chunks)) > 65536:
                    break
            return b"".join(chunks)

    def test_head_consumes_request_budget(self, tmp_path: Path) -> None:
        provider, state, port = self._provider()
        try:
            codes: list[str] = []
            for _ in range(3):
                response = self._raw(
                    port,
                    (
                        f"HEAD /v1/models HTTP/1.1\r\n"
                        f"Host: 127.0.0.1:{port}\r\n"
                        f"Authorization: Bearer tok\r\n\r\n"
                    ).encode(),
                )
                assert response.split(b" ", 2)[1] in (b"501", b"429")
                codes.append(response.split(b" ", 2)[1].decode())
            assert codes[:2] == ["501", "501"]
            assert codes[2] == "429"
            assert state.request_limit_hit
            assert state.request_count == 3
        finally:
            provider.stop()

    def test_unsupported_arbitrary_method_consumes_budget(self, tmp_path: Path) -> None:
        provider, state, port = self._provider()
        try:
            codes: list[str] = []
            for _ in range(3):
                response = self._raw(
                    port,
                    (
                        f"FOO /v1/models HTTP/1.1\r\n"
                        f"Host: 127.0.0.1:{port}\r\n"
                        f"Authorization: Bearer tok\r\n\r\n"
                    ).encode(),
                )
                codes.append(response.split(b" ", 2)[1].decode())
            assert codes[:2] == ["501", "501"]
            assert codes[2] == "429"
            assert state.request_limit_hit
        finally:
            provider.stop()

    def test_malformed_request_line_consumes_budget_without_echo(self, tmp_path: Path) -> None:
        provider, state, port = self._provider()
        try:
            # Two garbage request lines (malformed dispatch paths) plus
            # one valid GET: the budget is consumed by ALL of them and
            # the error bodies are fixed sanitized text with no echo.
            for _ in range(2):
                response = self._raw(port, b"GARBAGE-LINE\r\n\r\n")
                assert b"GARBAGE" not in response
                assert b"error\n" in response
            response = self._raw(
                port,
                (
                    f"GET /v1/models HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{port}\r\n"
                    f"Authorization: Bearer tok\r\n\r\n"
                ).encode(),
            )
            assert b"HTTP/1.1 429" in response
            assert state.request_limit_hit
            assert state.request_count == 3
        finally:
            provider.stop()

    def test_unsupported_method_error_body_is_fixed_and_silent(self, tmp_path: Path) -> None:
        provider, state, port = self._provider()
        try:
            response = self._raw(
                port,
                (f"BREW /v1/models HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n\r\n").encode(),
            )
            # Fixed sanitized body: the method name is never echoed.
            assert b"BREW" not in response
            assert response.endswith(b"error\n")
            assert state.request_count == 1
        finally:
            provider.stop()

    def test_concurrent_handlers_bounded_and_server_survives(self, tmp_path: Path) -> None:
        import time as _time

        state = rcc.ProviderState(
            rcc.CaptureLimits.resolved(), rcc.SYNTHETIC_MODEL, DEFAULT_MODE, "tok"
        )
        provider = rcc.FakeProvider(
            state=state, steps=rcc.default_declared_steps(), canary="CANARY"
        )
        port = provider.start()
        stalled: list[socket.socket] = []
        try:
            for _ in range(rcc.HARD_MAX_CONCURRENT_HANDLERS):
                sock = socket.create_connection(("127.0.0.1", port), timeout=5)
                # Request line only, no header terminator: the handler
                # stalls in the bounded header read.
                sock.sendall(b"GET /v1/models HTTP/1.1\r\nHost: x\r\n")
                stalled.append(sock)
            _time.sleep(0.3)  # handlers spawned
            fifth = socket.create_connection(("127.0.0.1", port), timeout=5)
            fifth.settimeout(1.0)
            data = b""
            try:
                data = fifth.recv(4096)
            except (TimeoutError, OSError):
                pass
            fifth.close()
            assert data == b""  # rejected without a response
            assert state.rejected_connections >= 1
            # After the stalled handlers hit their bounded read
            # timeout, the server still serves new work.
            _time.sleep(2.5)
            for sock in stalled:
                sock.close()
            response = self._raw(
                port,
                (
                    f"GET /v1/models HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{port}\r\n"
                    f"Authorization: Bearer tok\r\n\r\n"
                ).encode(),
            )
            assert b"HTTP/1.1 200" in response
        finally:
            for sock in stalled:
                try:
                    sock.close()
                except OSError:
                    pass
            provider.stop()


# ---------------------------------------------------------------------------
# 017-k: readiness metadata fidelity (zero and nonzero known flags).
# ---------------------------------------------------------------------------
class TestReadinessMetadataFidelity:
    def _roundtrip(self, tmp_path: Path, flags: tuple[str, ...]) -> None:
        facts = rcc.BinaryFacts(
            version="review-version",
            sha256="a" * 64,
            detected_flags=flags,
            help_complete=True,
        )
        record = rcc.evaluate_startup_readiness(facts).to_record()
        assert record["detected_flag_count"] == len(flags)
        path = tmp_path / f"readiness-{len(flags)}.json"
        write_json_0600(path, record)
        loaded = rcc.load_readiness_record(path, facts)
        # The generated record round-trips byte-for-byte at the
        # metadata level for zero AND every nonzero known-flag count.
        assert loaded.to_record() == record
        assert loaded.verdict == "not_ready"
        assert loaded.detected_flags == facts.detected_flags

    def test_zero_flags_roundtrip_control(self, tmp_path: Path) -> None:
        self._roundtrip(tmp_path, ())

    def test_one_flag_roundtrip(self, tmp_path: Path) -> None:
        self._roundtrip(tmp_path, ("--ephemeral",))

    def test_multiple_nonzero_flags_roundtrip(self, tmp_path: Path) -> None:
        self._roundtrip(tmp_path, ("--ephemeral", "--json", "-s"))

    def test_roundtrip_never_exports_flag_text(self, tmp_path: Path) -> None:
        facts = rcc.BinaryFacts(
            version="review-version",
            sha256="a" * 64,
            detected_flags=("--ephemeral", "--strict-config"),
            help_complete=True,
        )
        record = rcc.evaluate_startup_readiness(facts).to_record()
        path = tmp_path / "readiness-noflags.json"
        write_json_0600(path, record)
        loaded = rcc.load_readiness_record(path, facts)
        # Metadata law: the loaded record still carries the count only.
        assert loaded.to_record()["detected_flag_count"] == 2
        assert "ephemeral" not in json.dumps(loaded.to_record())


# ---------------------------------------------------------------------------
# 017-k: ACTUAL malformed Unicode (lone surrogates) + valid Unicode
# controls, typed and non-echoing, across output/argument/metadata paths.
# ---------------------------------------------------------------------------
class TestMalformedUnicodeStrict:
    MARKER = "SYNTHETIC_UNSELECTED_UNICODE_VALUE"

    def _extract(
        self, items: list[dict[str, Any]], mode: str = DEFAULT_MODE
    ) -> tuple[list[dict[str, Any]], dict[str, int], frozenset[str]]:
        payload = {"model": rcc.SYNTHETIC_MODEL, "input": items}
        before = json.loads(json.dumps(payload))
        frames, rejections, unknown = rcc.extract_frames(
            payload,
            declared_steps=rcc.default_declared_steps(),
            canary="CANARY",
            request_seq=1,
            mode=mode,
        )
        assert payload == before  # input immutability
        return list(frames), dict(rejections), frozenset(unknown)

    def test_malformed_output_content_typed_and_non_echoing(self) -> None:
        evil_content = self.MARKER + "\ud800"  # ACTUAL lone surrogate
        frames, rejections, unknown = self._extract(
            [
                _call_item(),
                _out_item("call_01", {"content": evil_content, "status": "completed"}),
            ]
        )
        assert rejections == {"malformed_unicode": 1}
        exported = json.dumps([frames, dict(rejections), sorted(unknown)])
        assert self.MARKER not in exported
        assert "ud800" not in exported

    def test_malformed_plain_string_output_typed_and_non_echoing(self) -> None:
        evil = self.MARKER + "\ud800"
        frames, rejections, _ = self._extract([_out_item("call_01", evil)])
        assert rejections == {"malformed_unicode": 1}
        assert self.MARKER not in json.dumps([frames, dict(rejections)])

    def test_malformed_custom_input_typed_and_non_echoing(self) -> None:
        steps = (
            DeclaredStep(
                index=0, tool_name="synthetic_custom", kind="read", path="A.md", seconds=0.0
            ),
        )
        payload = {
            "model": rcc.SYNTHETIC_MODEL,
            "input": [
                {
                    "type": "custom_tool_call",
                    "call_id": "call_01",
                    "name": "synthetic_custom",
                    "input": rcc._issued_custom_input(0) + "\ud800",
                }
            ],
        }
        frames, rejections, _ = rcc.extract_frames(
            payload,
            declared_steps=steps,
            canary="CANARY",
            request_seq=1,
            mode="responses-custom-tool",
        )
        assert frames == []
        assert rejections == {"malformed_unicode": 1}

    def test_valid_unicode_output_is_not_malformed(self) -> None:
        # Valid non-ASCII text: processed normally (no malformed
        # Unicode rejection); it may still be unverified at run time,
        # but extraction must not type it malformed.
        frames, rejections, _ = self._extract(
            [
                _call_item(),
                _out_item("call_01", {"content": "caf\u00e9 content\n", "status": "completed"}),
            ]
        )
        assert "malformed_unicode" not in rejections
        assert len(frames) == 2

    def test_run_level_malformed_unicode_no_crash_no_persistence(self, tmp_path: Path) -> None:
        child = tmp_path / "unicode_child.py"
        child.write_text(
            "import json, sys, urllib.request\n"
            "c = json.load(open(sys.argv[1]))\n"
            "tools = [{'type': 'function', 'name': 'exec_command', 'parameters':\n"
            "  {'type': 'object', 'properties': {'cmd': {'type': 'string'},\n"
            "                                    'workdir': {'type': 'string'}},\n"
            "  'required': ['cmd', 'workdir']}}]\n"
            "def post(history):\n"
            "    body = json.dumps({'model': c['model'], 'stream': True,\n"
            "                       'input': history, 'tools': tools}).encode()\n"
            "    req = urllib.request.Request(c['provider_base_url'] + '/responses',\n"
            "                                 data=body,\n"
            "                                 headers={'Authorization': 'Bearer ' + c['token']})\n"
            "    with urllib.request.urlopen(req, timeout=5) as r:\n"
            "        data = r.read(65536)\n"
            "    items = []\n"
            "    for line in data.decode().splitlines():\n"
            "        if line.startswith('data: '):\n"
            "            ev = json.loads(line[6:])\n"
            "            if ev.get('type') == 'response.output_item.added':\n"
            "                items.append(ev['item'])\n"
            "    return items\n"
            "items = post([{'role': 'user', 'content': [{'type': 'input_text', 'text': 's'}]}])\n"
            "call = items[0]\n"
            "evil = 'SYNTHETIC_UNSELECTED_UNICODE_VALUE' + '\\ud800'\n"
            "post([{'role': 'user', 'content': [{'type': 'input_text', 'text': 's'}]},\n"
            "      call,\n"
            "      {'type': 'function_call_output', 'call_id': call['call_id'],\n"
            "       'output': json.dumps({'content': evil, 'status': 'completed',\n"
            "                              'exit_code': 0, 'process_id': 'proc_01'})}])\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        child.chmod(0o700)
        result = run_synthetic(
            tmp_path,
            "uni-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            child=child,
            out_name="out-uni",
        )
        assert result.outcome == "completed"
        selection = result.selection_record
        assert selection is not None
        assert selection["rejected"]["reason_counts"].get("malformed_unicode") == 1
        assert all(f["content"] is None for f in selection["frames"])
        assert b"SYNTHETIC_UNSELECTED_UNICODE_VALUE" not in record_blob(
            result.run_record_path.parent
        )


# ---------------------------------------------------------------------------
# 017-l: owned I/O quiesce (admitted request sockets) and immutable
# original seeds (pre-launch byte binding).
# ---------------------------------------------------------------------------
MUTATED_SEED_MARKER = "SYNTHETIC_UNSELECTED_SEED_REWRITE_VALUE"

SEED_CHILD_TEMPLATE = """
import json, sys, urllib.request
from pathlib import Path

MUTATE = __MUTATE__

def main():
    c = json.load(open(sys.argv[1]))
    tools = [{"type": "function", "name": "exec_command", "parameters":
        {"type": "object", "properties": {"cmd": {"type": "string"},
                                          "workdir": {"type": "string"}},
        "required": ["cmd", "workdir"]}}]
    history = [{"role": "user", "content": [{"type": "input_text", "text": "s"}]}]
    def post():
        body = json.dumps({"model": c["model"], "stream": True,
                           "input": history, "tools": tools}).encode()
        q = urllib.request.Request(c["provider_base_url"] + "/responses", data=body,
                                   headers={"Authorization": "Bearer " + c["token"]})
        with urllib.request.urlopen(q, timeout=5) as r:
            return r.read(65536)
    data = post()
    call = None
    for line in data.decode().splitlines():
        if line.startswith("data: "):
            ev = json.loads(line[6:])
            if ev.get("type") == "response.output_item.added":
                call = ev["item"]
    assert call is not None
    __MUTATION__
    history.append(call)
    history.append({"type": "function_call_output", "call_id": call["call_id"],
                    "output": json.dumps({"content": Path("__PATH__").read_text(),
                                          "status": "completed", "exit_code": 0,
                                          "process_id": "proc_01"})})
    post()
    return 0

sys.exit(main())
"""


def write_seed_child(tmp_path: Path, name: str, path: str, mutate: bool) -> Path:
    mutation = f'Path("{path}").write_text({MUTATED_SEED_MARKER!r})' if mutate else "pass"
    code = (
        SEED_CHILD_TEMPLATE.replace("__MUTATION__", mutation)
        .replace("__PATH__", path)
        .replace("__MUTATE__", "True" if mutate else "False")
    )
    child = tmp_path / name
    child.write_text(code, encoding="utf-8")
    child.chmod(0o700)
    return child


class TestOwnedIoQuiesce:
    """The owned provider must close every admission-owned request
    socket at quiesce, not only the listener (017-l boundary 1)."""

    def test_stop_closes_owned_inflight_drip_body(self, tmp_path: Path) -> None:
        import signal as _signal
        import threading as _threading
        import time as _time

        state = rcc.ProviderState(
            rcc.CaptureLimits.resolved(), rcc.SYNTHETIC_MODEL, DEFAULT_MODE, "tok"
        )
        provider = rcc.FakeProvider(
            state=state, steps=rcc.default_declared_steps(), canary="CANARY"
        )
        port = provider.start()
        # An unrelated process in its own session: provider teardown
        # must never touch it.
        survivor = tmp_path / "survivor.py"
        survivor.write_text("import time\ntime.sleep(30)\n", encoding="utf-8")
        survivor_proc = subprocess.Popen(
            [sys.executable, str(survivor)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        sock: socket.socket | None = None
        drip_stop = _threading.Event()
        drip_thread: _threading.Thread | None = None

        def drip(s: socket.socket) -> None:
            end = _time.monotonic() + 15
            while not drip_stop.wait(0.05) and _time.monotonic() < end:
                try:
                    s.sendall(b"x")
                except OSError:
                    break

        try:
            sock = socket.create_connection(("127.0.0.1", port), timeout=5)
            sock.sendall(
                b"POST /v1/responses HTTP/1.1\r\n"
                b"Host: synthetic\r\n"
                b"Authorization: Bearer tok\r\n"
                b"Content-Length: 1000\r\n"
                b"\r\n"
            )
            end = _time.monotonic() + 5
            while state.request_count < 1 and _time.monotonic() < end:
                _time.sleep(0.01)
            assert state.request_count == 1  # handler entered the body read
            # A progressing drip defeats the per-read 2 s timeout: the
            # read keeps advancing, so only an effective socket shutdown
            # can unblock it.
            drip_thread = _threading.Thread(target=drip, args=(sock,), daemon=True)
            drip_thread.start()
            provider.stop()
            # External observation (no private tracking): the peer must
            # see the owned accepted socket closed (EOF or reset), not
            # a live connection.
            sock.settimeout(0.15)
            closed = False
            end = _time.monotonic() + 1.0
            while _time.monotonic() < end:
                try:
                    data = sock.recv(1024)
                    if not data:
                        closed = True
                        break
                except (ConnectionResetError, BrokenPipeError):
                    closed = True
                    break
                except TimeoutError:
                    continue
            assert closed
            assert state.frozen is True
            assert state.teardown_incomplete is False
            assert state.frames == []
            # Repeated stop is a safe no-op.
            provider.stop()
            assert state.teardown_incomplete is False
            # The unrelated session survived the provider teardown.
            assert survivor_proc.poll() is None
        finally:
            drip_stop.set()
            if drip_thread is not None and drip_thread.ident is not None:
                drip_thread.join(timeout=2)
            if sock is not None:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                sock.close()
            try:
                os.killpg(os.getpgid(survivor_proc.pid), _signal.SIGTERM)
            except OSError:
                survivor_proc.kill()
            survivor_proc.wait(timeout=10)
            provider.stop()

    def test_listener_closed_and_repeated_stop_is_safe(self, tmp_path: Path) -> None:
        import time as _time
        import urllib.request

        state = rcc.ProviderState(
            rcc.CaptureLimits.resolved(), rcc.SYNTHETIC_MODEL, DEFAULT_MODE, "tok"
        )
        provider = rcc.FakeProvider(
            state=state, steps=rcc.default_declared_steps(), canary="CANARY"
        )
        port = provider.start()
        with urllib.request.urlopen(
            urllib.request.Request(
                f"http://127.0.0.1:{port}/v1/models",
                headers={"Authorization": "Bearer tok"},
            ),
            timeout=5,
        ) as response:
            assert response.status == 200
            response.read(1024)
        _time.sleep(0.1)  # let the handler thread finish and deregister
        provider.stop()
        assert state.frozen is True
        assert state.teardown_incomplete is False
        provider.stop()  # idempotent: no server, no thread, no error
        assert state.teardown_incomplete is False
        # The owned listener is actually closed: the port is bindable
        # (SO_REUSEADDR ignores TIME_WAIT leftovers of the handler
        # connection, which is what distinguishes "closed listener"
        # from "still listening").
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind(("127.0.0.1", port))
        finally:
            probe.close()

    def test_teardown_incomplete_never_yields_completed_run(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import time as _time

        # A handler that ignores the socket closure (a pure sleep)
        # outlives a tiny quiesce grace: stop() reports the incomplete
        # teardown honestly and the run must come out with the fixed
        # truthful failure, never completed.
        monkeypatch.setattr(rcc, "HARD_HANDLER_JOIN_GRACE_SECONDS", 0.05)
        # 2.0 s stall: it outlives the serve-loop poll window (<=0.5 s)
        # and the tiny grace, so the handler is provably still alive
        # when the bounded join gives up.
        monkeypatch.setattr(
            rcc._SilentRequestHandler,
            "do_POST",
            lambda self_handler: _time.sleep(2.0),
        )
        child = tmp_path / "post_once_child.py"
        child.write_text(
            "import json, socket, sys, time\n"
            "c = json.load(open(sys.argv[1]))\n"
            "host, port = c['provider_base_url'].replace('http://', '').split('/')[0].split(':')\n"
            "body = json.dumps({'model': c['model'], 'stream': True,\n"
            "  'input': [{'role': 'user', 'content': [{'type': 'input_text', 'text': 's'}]}],\n"
            "  'tools': [{'type': 'function', 'name': 'exec_command', 'parameters':\n"
            "    {'type': 'object', 'properties': {'cmd': {'type': 'string'},\n"
            "                                      'workdir': {'type': 'string'}},\n"
            "    'required': ['cmd', 'workdir']}}]}).encode()\n"
            "s = socket.create_connection((host, int(port)), timeout=5)\n"
            "s.sendall(b'POST /v1/responses HTTP/1.1\\r\\nHost: x\\r\\n'\n"
            "           b'Authorization: Bearer ' + c['token'].encode() + b'\\r\\n'\n"
            "           b'Content-Length: ' + str(len(body)).encode() + b'\\r\\n\\r\\n'\n"
            "           + body)\n"
            "time.sleep(0.5)  # let the handler thread enter its stall\n"
            "s.close()\n",
            encoding="utf-8",
        )
        child.chmod(0o700)
        result = rcc.run_capture(
            run_id="teardown-1",
            out_dir=protected_out_dir(tmp_path),
            child=child,
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            child_kind="synthetic",
        )
        assert result.outcome == "cleanup_failed"
        assert result.selection_path is None
        assert result.run_record["provider"]["teardown_incomplete"] is True
        # Fixed enum only, no raw error details in the persisted record.
        assert result.run_record["outcome"] in rcc.OUTCOMES

    def test_idle_stalled_read_times_out_and_teardown_complete(self, tmp_path: Path) -> None:
        # The failure/timeout path: a stalled (non-progressing) body
        # read hits the per-read timeout, the handler rejects and
        # exits on its own, and teardown is complete with honest
        # accounting.
        import time as _time

        state = rcc.ProviderState(
            rcc.CaptureLimits.resolved(), rcc.SYNTHETIC_MODEL, DEFAULT_MODE, "tok"
        )
        provider = rcc.FakeProvider(
            state=state, steps=rcc.default_declared_steps(), canary="CANARY"
        )
        port = provider.start()
        sock = socket.create_connection(("127.0.0.1", port), timeout=5)
        try:
            sock.sendall(
                b"POST /v1/responses HTTP/1.1\r\n"
                b"Host: synthetic\r\n"
                b"Authorization: Bearer tok\r\n"
                b"Content-Length: 1000\r\n"
                b"\r\n"
            )
            # No drip: the per-read 2 s bound fires and the handler
            # exits with a sanitized 400.
            _time.sleep(3.0)
            provider.stop()
        finally:
            sock.close()
            provider.stop()
        assert state.frozen is True
        assert state.teardown_incomplete is False
        assert state.frames == []
        assert "400" in state.status_counts


class TestOriginalSeedImmutability:
    """Selected text verifies against the immutable pre-launch
    original seeds, never a child-writable file (017-l boundary 2)."""

    def test_actual_issued_default_seed_retains_exact_received_text(self, tmp_path: Path) -> None:
        result = run_synthetic(
            tmp_path,
            "seed-default-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            steps=(rcc.default_declared_steps()[0],),
            out_name="out-seed-default",
        )
        assert result.outcome == "completed"
        selection = result.selection_record
        assert selection is not None
        frames = [f for f in selection["frames"] if f["item_type"] == "function_call_output"]
        assert frames
        # Useful exact received text retained and byte-verified.
        assert frames[0]["content"] == "alpha file content\n"
        assert frames[0]["content_bytes"] == len(b"alpha file content\n")
        assert frames[0]["content_verified"] is True
        assert selection["rejected"]["reason_counts"].get("content_unverified", 0) == 0

    def test_actual_issued_custom_seed_retains_exact_received_text(self, tmp_path: Path) -> None:
        custom_bytes = b"gamma custom fixture content\n"
        steps = (
            rcc.DeclaredStep(
                index=0, tool_name="exec_command", kind="read", path="C.md", seconds=0.0
            ),
        )
        result = run_synthetic(
            tmp_path,
            "seed-custom-1",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
            steps=steps,
            workspace_files=(("C.md", custom_bytes),),
            out_name="out-seed-custom",
        )
        assert result.outcome == "completed"
        selection = result.selection_record
        assert selection is not None
        frames = [f for f in selection["frames"] if f["item_type"] == "function_call_output"]
        assert frames
        assert frames[0]["content"] == custom_bytes.decode()
        assert frames[0]["content_bytes"] == len(custom_bytes)
        assert frames[0]["content_verified"] is True
        assert selection["rejected"]["reason_counts"].get("content_unverified", 0) == 0

    def test_child_mutated_original_never_redefines_seed(self, tmp_path: Path) -> None:
        # The child receives the legitimately issued read, then REWRITES
        # its own A.md and returns the new bytes: the verification must
        # compare against the pre-launch original, so the mutated text
        # is stripped and reaches no persisted record.
        child = write_seed_child(tmp_path, "seed_mutator_child.py", "A.md", mutate=True)
        result = rcc.run_capture(
            run_id="seed-mutator-1",
            out_dir=protected_out_dir(tmp_path),
            child=child,
            steps=(rcc.default_declared_steps()[0],),
            child_kind="synthetic",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
        )
        assert result.outcome == "completed"
        out = result.run_record_path.parent
        assert MUTATED_SEED_MARKER.encode() not in record_blob(out)
        selection = result.selection_record
        assert selection is not None
        # The mutation was actually received (the fixed reason fired),
        # stripped with metadata retained, and never published.
        assert selection["rejected"]["reason_counts"].get("content_unverified") == 1
        out_frames = [f for f in selection["frames"] if f["item_type"] == "function_call_output"]
        assert out_frames
        assert all(f["content"] is None for f in out_frames)
        assert all(f["content_verified"] is False for f in out_frames)

    def test_unseeded_path_content_never_verified(self, tmp_path: Path) -> None:
        # A step reading a path this run never seeded: no original
        # exists, so any received text is unverified and stripped
        # (never invented from the child's file).
        child = tmp_path / "unseeded_child.py"
        child.write_text(
            "import json, sys, urllib.request\n"
            "c = json.load(open(sys.argv[1]))\n"
            "tools = [{'type': 'function', 'name': 'exec_command', 'parameters':\n"
            "  {'type': 'object', 'properties': {'cmd': {'type': 'string'},\n"
            "                                    'workdir': {'type': 'string'}},\n"
            "  'required': ['cmd', 'workdir']}}]\n"
            "history = [{'role': 'user', 'content': [{'type': 'input_text', 'text': 's'}]}]\n"
            "def post():\n"
            "    body = json.dumps({'model': c['model'], 'stream': True, 'input': history,\n"
            "                       'tools': tools}).encode()\n"
            "    q = urllib.request.Request(c['provider_base_url'] + '/responses', data=body,\n"
            "                               headers={'Authorization': 'Bearer ' + c['token']})\n"
            "    with urllib.request.urlopen(q, timeout=5) as r: return r.read(65536)\n"
            "data = post()\n"
            "call = None\n"
            "for line in data.decode().splitlines():\n"
            "    if line.startswith('data: '):\n"
            "        ev = json.loads(line[6:])\n"
            "        if ev.get('type') == 'response.output_item.added': call = ev['item']\n"
            "assert call is not None\n"
            "history.append(call)\n"
            "history.append({'type': 'function_call_output', 'call_id': call['call_id'],\n"
            "                'output': json.dumps({'content': 'ghost unseeded content',\n"
            "                                       'status': 'completed', 'exit_code': 0,\n"
            "                                       'process_id': 'proc_01'})})\n"
            "post()\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        child.chmod(0o700)
        steps = (
            rcc.DeclaredStep(
                index=0, tool_name="exec_command", kind="read", path="C.md", seconds=0.0
            ),
        )
        result = rcc.run_capture(
            run_id="unseeded-1",
            out_dir=protected_out_dir(tmp_path, "out-unseeded"),
            child=child,
            steps=steps,
            child_kind="synthetic",
            limits=rcc.CaptureLimits.resolved(deadline_seconds=10.0),
        )
        assert result.outcome == "completed"
        selection = result.selection_record
        assert selection is not None
        assert selection["rejected"]["reason_counts"].get("content_unverified") == 1
        out_frames = [f for f in selection["frames"] if f["item_type"] == "function_call_output"]
        assert out_frames
        assert all(f["content"] is None for f in out_frames)
        assert all(f["content_verified"] is False for f in out_frames)
        assert b"ghost unseeded content" not in record_blob(result.run_record_path.parent)
