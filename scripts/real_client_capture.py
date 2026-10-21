"""Repository-owned real-client process-capture utility (order 017-i).

Purpose
-------
An explicit, opt-in, bounded capture harness for the dependency-bundle cache
rework's later AUTHORIZED actual-capture round. It binds an isolated
synthetic workspace/CODEX_HOME to a pinned release client binary
(version/hash/mode), points the client's provider at an owned ephemeral
loopback fake provider, and selects ONLY allowlisted synthetic
call/result/provenance frames (plus sanitized provenance) into a closed
metadata schema. Everything else is bounded, counted, or discarded.

Order 017-i scope: OFFLINE ONLY. The actual-client launch path exists in
code but is fail-closed by construction: it requires an explicit opt-in
flag, a readiness record whose verdict is ``ready`` (this version of the
utility never emits one -- the plugin/catalog sync, update and telemetry
controls remain unverified from local static evidence, and unknown control
means NOT READY, never silent fetch), an external strategic
authorization record, and an unconsumed one-attempt ledger claim.
Ordinary offline runs use an injected wholly synthetic child executable
and an in-process owned fake provider; they NEVER launch an installed
client, call a model, or touch a provider.

Hard law (implemented as fail-closed code, not documentary warnings):

- stdlib only; no new dependencies.
- Explicit opt-in; the actual-child runner is disabled by default.
- Isolated minimal synthetic workspace/CODEX_HOME; the child environment is
  built from scratch (fixed PATH, child HOME/XDG/CODEX_HOME) and inherits
  NOTHING from the parent: no auth, profile, global config, keys, SQLite,
  hooks, login state, or network/proxy variables.
- The fake provider is an ephemeral unused 127.0.0.1 port (bind 0); it is
  never 18020/18031 and no protected service is touched.
- Attempt/request/time/output/process limits are enforced in code:
  per-run request count, per-request 1 MiB ingress, 256 KiB selected,
  120 s hard deadline, 4 MiB aggregate child output, one actual attempt,
  one concurrent child. Limits may be LOWERED by configuration; they can
  never silently rise above the hard caps.
- A hard deadline independently cancels the owned process group, the owned
  server, and the owned reader threads; cleanup is verified after both
  normal exit and timeout, without killing unrelated processes (the child
  always starts its own session; only its group is signalled).
- In-memory bounded request parsing only: headers and bodies are read with
  finite caps (Content-Length and chunked forms; malformed, chunked,
  oversized and invalid-length payloads all fail closed with sanitized
  generic responses), parsed once in memory, allowlisted, and discarded.
  Nothing is streamed to disk.
- Privacy: the server is log-silent; diagnostics are fixed enums and
  counts; no raw request, system prompt, tool schema, header value, body,
  history, credential, unknown stdout or stderr is ever written to disk,
  console, error, or trace. Invalid or unexpected strings are never
  echoed through exceptions or reprs (exceptions carry a failure class
  only). Credential-bearing transport headers are validated in memory and
  rejected without values; a declared canary marker in any selectable
  content rejects the frame without echo.
- Only predeclared harmless synthetic commands (the controller's declared
  table) are ever emitted or selectable; arbitrary incoming command/code
  is never executed, selected, or echoed. The child never executes model-
  directed commands.
- Tool mode is read from the actual offered tool schema in memory
  (function vs custom); unknown modes, mixed shapes, and declared/observed
  mismatches fail closed. Causal call IDs are preserved through nested
  frames; inner results are never flattened away.
- Persistent attempt state is a protected, non-sensitive, bounded counter
  record (O_EXCL, mode 0600): a one-attempt run ID, consumed before any
  genuine child launch, never resettable by a new wrapper invocation, and
  never carrying raw request data.
- Scratch roots are created 0700, owned, non-symlink, and removed only by
  exact per-entry validated cleanup of the exact root this run created
  (never a broad rm -rf, never shared or pre-existing state).
- This utility does not own, read, or modify OAP active/orders, and the
  adapter runtime is never taught to consult it.

Usage (offline, synthetic child -- the only launch path exercised in
ordinary tests):

    python scripts/real_client_capture.py run \
        --child scripts/real_client_capture_fake_child.py \
        --run-id offline-017-i --out-dir /path/to/0700/out

Read-only preflight + static readiness (no client session):

    python scripts/real_client_capture.py check \
        --binary /abs/path/to/codex --version 0.162.1 \
        --sha256 <64hex> [--out-record /0700dir/readiness.json]

Exit codes: 0 ok; 1 capture failure (sanitized class); 2 usage error;
3 readiness not ready (record written).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import signal
import stat
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

SCHEMA = "slaif-real-client-capture-v1"
SELECTION_SCHEMA = "slaif-real-client-capture-selection-v1"
RUN_SCHEMA = "slaif-real-client-capture-run-v1"
ATTEMPT_SCHEMA = "slaif-real-client-capture-attempt-v1"
READINESS_SCHEMA = "slaif-real-client-capture-readiness-v1"
AUTHORIZATION_SCHEMA = "slaif-real-client-capture-authorization-v1"

VERSION = "real-client-capture 1.0"

# ---------------------------------------------------------------------------
# Hard caps. Configuration may LOWER these for tests; it can never raise
# them. These are the actual hard caps named by the order: at most one
# actual client launch under an external authorized-run identity, max 20
# requests, 120 s deadline, 1 MiB per inbound request, 256 KiB selected.
# ---------------------------------------------------------------------------
HARD_MAX_REQUESTS = 20
HARD_MAX_INBOUND_BYTES = 1024 * 1024  # 1 MiB per inbound request
HARD_MAX_SELECTED_BYTES = 256 * 1024  # 256 KiB aggregate selected
HARD_DEADLINE_SECONDS = 120.0
HARD_MAX_CHILD_OUTPUT_BYTES = 4 * 1024 * 1024  # aggregate stdout+stderr
HARD_MAX_HEADER_BYTES = 16 * 1024
HARD_MAX_HEADER_LINES = 64
HARD_MAX_HEADER_LINE_BYTES = 256
HARD_MAX_ACTUAL_ATTEMPTS = 1
HARD_MAX_CONCURRENT_CHILDREN = 1
HARD_MAX_VERSION_BYTES = 256
HARD_MAX_HELP_BYTES = 256 * 1024
HARD_MAX_BINARY_BYTES = 1024 * 1024 * 1024
HARD_MAX_RUN_ID_BYTES = 128
HARD_MAX_CALL_ID_BYTES = 128
HARD_MAX_NAME_BYTES = 64
HARD_MAX_ITEM_TYPE_BYTES = 64
HARD_MAX_METADATA_BYTES = 256
HARD_MAX_FIELD_NAMES = 16
HARD_MAX_DECLARED_STEPS = 16
HARD_MAX_STEP_BYTES = 256
HARD_MAX_UNSUPPORTED_TYPE_SAMPLES = 8
HARD_MAX_SSE_EVENT_BYTES = 64 * 1024
HARD_SSE_READ_TIMEOUT_SECONDS = 2.0
HARD_CHILD_IO_TIMEOUT_SECONDS = 30.0

RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
CALL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,63}$")

# Closed protocol sets. Anything outside them is typed, counted, never
# echoed.
TOOL_MODES: frozenset[str] = frozenset({"responses-function-tool", "responses-custom-tool"})
TOOL_SCHEMA_TYPES: frozenset[str] = frozenset({"function", "custom"})
ITEM_TYPES: frozenset[str] = frozenset(
    {
        "function_call",
        "function_call_output",
        "custom_tool_call",
        "custom_tool_call_output",
    }
)
OUTPUT_STATUSES: frozenset[str] = frozenset({"running", "completed", "failed"})
OUTPUT_DICT_KEYS: frozenset[str] = frozenset(
    {
        "content",
        "exit_code",
        "process_id",
        "session_id",
        "chunk_id",
        "chunk_index",
        "status",
    }
)

OUTCOMES: frozenset[str] = frozenset(
    {
        "completed",
        "child_failure",
        "timed_out",
        "output_cap_exceeded",
        "request_limit_exceeded",
        "tool_mode_mismatch",
        "selected_over_bound",
        "provider_error",
        "preflight_failed",
        "readiness_not_ready",
        "authorization_invalid",
        "attempt_already_consumed",
        "setup_failed",
        "cleanup_failed",
        "unsupported",
        "record_write_failed",
    }
)

REJECTION_REASONS: frozenset[str] = frozenset(
    {
        "call_id_invalid",
        "name_not_declared",
        "command_not_declared",
        "input_shape_unsupported",
        "output_shape_unsupported",
        "credential_marker_present",
        "metadata_value_over_bound",
    }
)

READINESS_REASONS: frozenset[str] = frozenset(
    {
        "plugin_catalog_sync_control_unverified",
        "telemetry_update_control_unverified",
        "help_incomplete",
    }
)

# Flags whose presence is verified from the binary's own read-only
# ``exec --help`` output. The set is fixed here (no speculative flags are
# invented); only membership of these known tokens is recorded.
DECLARED_FLAG_SET: frozenset[str] = frozenset(
    {
        "--ephemeral",
        "--skip-git-repo-check",
        "--ignore-user-config",
        "--ignore-rules",
        "--json",
        "--strict-config",
        "--enable",
        "--disable",
        "-c",
        "-s",
        "-C",
        "-m",
        "-h",
        "--help",
        "-V",
        "--version",
    }
)

# Candidate startup controls documented in public references. None of them
# carries locally verifiable proof of suppressing the observed startup
# plugin/catalog git sync, update, or telemetry in the pinned binary, so
# every candidate is ``unverified`` and the readiness verdict is
# fail-closed ``not_ready``.
STARTUP_CONTROL_CANDIDATES: tuple[tuple[str, str], ...] = (
    ("features.remote_plugin", "unverified"),
    ("features.plugins", "unverified"),
    ("features.code_mode.enabled", "unverified"),
    ("features.unified_exec", "unverified"),
)

# The child environment is built from scratch. These are the only names the
# child ever receives (values are synthetic or owned paths).
CHILD_ENV_FIXED_PATH = "/usr/local/bin:/usr/bin:/bin"
CHILD_ENV_TOKEN_NAME = "SLAIF_CAPTURE_TOKEN"
CHILD_ENV_CHILD_NAME = "SLAIF_CAPTURE_CHILD"

SYNTHETIC_PROMPT = (
    "Synthetic capture run. Execute only the declared commands in order. Reply DONE when finished."
)


class CaptureError(RuntimeError):
    """Fail-closed capture failure carrying a sanitized class only.

    The exception text IS the failure class; no raw payload, path content,
    header value, or model output is ever embedded, so ``repr()`` and
    tracebacks cannot leak content.
    """

    def __init__(self, failure_class: str) -> None:
        if not failure_class or not failure_class.isascii() or len(failure_class) > 64:
            raise ValueError("failure class must be a bounded ascii token")
        self.failure_class = failure_class
        super().__init__(failure_class)


# ---------------------------------------------------------------------------
# Limits: fail-closed resolution. None means "hard default"; any explicit
# value must be a positive number NOT above the hard cap.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CaptureLimits:
    max_requests: int
    max_inbound_bytes: int
    max_selected_bytes: int
    deadline_seconds: float
    max_child_output_bytes: int
    max_actual_attempts: int

    @classmethod
    def resolved(
        cls,
        *,
        max_requests: int | None = None,
        max_inbound_bytes: int | None = None,
        max_selected_bytes: int | None = None,
        deadline_seconds: float | None = None,
        max_child_output_bytes: int | None = None,
        max_actual_attempts: int | None = None,
    ) -> CaptureLimits:
        def _check_int(name: str, value: Any, hard: int) -> int:
            if isinstance(value, bool) or not isinstance(value, int):
                raise CaptureError(f"limits_{name}_invalid")
            if value < 1 or value > hard:
                raise CaptureError(f"limits_{name}_over_hard_cap")
            return value

        def _check_float(name: str, value: Any, hard: float) -> float:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise CaptureError(f"limits_{name}_invalid")
            v = float(value)
            if not (0.0 < v <= hard):
                raise CaptureError(f"limits_{name}_over_hard_cap")
            return v

        return cls(
            max_requests=_check_int(
                "max_requests",
                HARD_MAX_REQUESTS if max_requests is None else max_requests,
                HARD_MAX_REQUESTS,
            ),
            max_inbound_bytes=_check_int(
                "max_inbound_bytes",
                HARD_MAX_INBOUND_BYTES if max_inbound_bytes is None else max_inbound_bytes,
                HARD_MAX_INBOUND_BYTES,
            ),
            max_selected_bytes=_check_int(
                "max_selected_bytes",
                HARD_MAX_SELECTED_BYTES if max_selected_bytes is None else max_selected_bytes,
                HARD_MAX_SELECTED_BYTES,
            ),
            deadline_seconds=_check_float(
                "deadline_seconds",
                HARD_DEADLINE_SECONDS if deadline_seconds is None else deadline_seconds,
                HARD_DEADLINE_SECONDS,
            ),
            max_child_output_bytes=_check_int(
                "max_child_output_bytes",
                HARD_MAX_CHILD_OUTPUT_BYTES
                if max_child_output_bytes is None
                else max_child_output_bytes,
                HARD_MAX_CHILD_OUTPUT_BYTES,
            ),
            max_actual_attempts=_check_int(
                "max_actual_attempts",
                HARD_MAX_ACTUAL_ATTEMPTS if max_actual_attempts is None else max_actual_attempts,
                HARD_MAX_ACTUAL_ATTEMPTS,
            ),
        )


# ---------------------------------------------------------------------------
# Binary preflight (read-only: hash, --version, exec --help) and static
# startup readiness. No client session, no provider, no network.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class BinaryFacts:
    version: str
    sha256: str
    detected_flags: tuple[str, ...]
    help_complete: bool


def _run_bounded(argv: list[str], cap: int, timeout: float = 15.0) -> tuple[bytes, bool]:
    """Run a read-only CLI probe; return (bounded bytes, complete)."""
    proc = subprocess.run(  # noqa: S603 - fixed argv, never a shell
        argv,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env={"PATH": CHILD_ENV_FIXED_PATH, "LC_ALL": "C.UTF-8"},
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        raise CaptureError("binary_probe_failed")
    data = proc.stdout[:cap]
    return data, len(proc.stdout) <= cap


def _detect_flags(help_text: str) -> tuple[str, ...]:
    found: list[str] = []
    for flag in sorted(DECLARED_FLAG_SET):
        pattern = r"(?<![A-Za-z0-9-])" + re.escape(flag) + r"(?![A-Za-z0-9-])"
        if re.search(pattern, help_text):
            found.append(flag)
    return tuple(found)


def preflight_binary(binary: Path, expected_version: str, expected_sha256: str) -> BinaryFacts:
    """Read-only verification of the pinned release binary."""
    if not RUN_ID_RE.fullmatch(expected_version) and not VERSION_RE.fullmatch(expected_version):
        raise CaptureError("expected_version_invalid")
    if not HEX64_RE.fullmatch(expected_sha256):
        raise CaptureError("expected_sha256_invalid")
    try:
        st = binary.lstat()
    except OSError:
        raise CaptureError("binary_missing") from None
    if stat.S_ISLNK(st.st_mode):
        raise CaptureError("binary_symlink")
    if not stat.S_ISREG(st.st_mode):
        raise CaptureError("binary_not_regular")
    if st.st_uid != os.getuid():
        raise CaptureError("binary_not_owned")
    digest = hashlib.sha256()
    total = 0
    try:
        with binary.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                total += len(chunk)
                if total > HARD_MAX_BINARY_BYTES:
                    raise CaptureError("binary_over_bound")
                digest.update(chunk)
    except OSError:
        raise CaptureError("binary_unreadable") from None
    if digest.hexdigest() != expected_sha256:
        raise CaptureError("binary_hash_mismatch")
    version_data, _ = _run_bounded([str(binary), "--version"], HARD_MAX_VERSION_BYTES)
    version_line = version_data.decode("utf-8", "replace").splitlines()
    version = version_line[0].strip() if version_line else ""
    # Expected form: "<tool> <version>" (e.g. "codex-cli 0.162.1").
    parts = version.split()
    observed_version = parts[-1] if len(parts) >= 2 else version
    if not VERSION_RE.fullmatch(observed_version) or observed_version != expected_version:
        raise CaptureError("binary_version_mismatch")
    help_data, complete = _run_bounded([str(binary), "exec", "--help"], HARD_MAX_HELP_BYTES)
    flags = _detect_flags(help_data.decode("utf-8", "replace"))
    if not complete:
        raise CaptureError("binary_help_over_bound")
    required = {"--ephemeral", "--skip-git-repo-check", "--ignore-rules", "--json"}
    if not required.issubset(set(flags)):
        raise CaptureError("binary_flags_unsupported")
    return BinaryFacts(
        version=observed_version,
        sha256=expected_sha256,
        detected_flags=flags,
        help_complete=complete,
    )


@dataclass(frozen=True)
class ReadinessFacts:
    verdict: str
    reasons: tuple[str, ...]
    binary_version: str
    binary_sha256: str
    detected_flags: tuple[str, ...]
    control_candidates: tuple[tuple[str, str], ...]

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": READINESS_SCHEMA,
            "verdict": self.verdict,
            "reasons": list(self.reasons),
            "binary_version": self.binary_version,
            "binary_sha256": self.binary_sha256,
            # Metadata only: never persist the observed flag text itself.
            "detected_flag_count": len(self.detected_flags),
            "control_candidates": [
                {"name": name, "status": status} for name, status in self.control_candidates
            ],
        }


def evaluate_startup_readiness(facts: BinaryFacts) -> ReadinessFacts:
    """Static, metadata-only startup readiness evaluation.

    The observed H-round child performed a startup plugin/catalog git sync
    into its fresh CODEX_HOME. Relocating a private home plus ``--ephemeral``
    does NOT prove that component/plugin downloads, updates, or telemetry
    are suppressed, and this version carries no packaged static evidence
    proving any candidate control. Unknown control therefore means NOT
    READY (fail closed), never a silent fetch. A ``ready`` verdict can only
    ever come from a future explicit verification round with packaged
    static proof; this code path deliberately has no such mechanism.
    """
    reasons: list[str] = []
    reasons.append("plugin_catalog_sync_control_unverified")
    reasons.append("telemetry_update_control_unverified")
    if not facts.help_complete:
        reasons.append("help_incomplete")
    return ReadinessFacts(
        verdict="not_ready",
        reasons=tuple(reasons),
        binary_version=facts.version,
        binary_sha256=facts.sha256,
        detected_flags=facts.detected_flags,
        control_candidates=STARTUP_CONTROL_CANDIDATES,
    )


def load_readiness_record(path: Path, facts: BinaryFacts) -> ReadinessFacts:
    """Validate a previously written readiness record (metadata only)."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise CaptureError("readiness_record_invalid") from None
    if not isinstance(data, dict) or data.get("schema") != READINESS_SCHEMA:
        raise CaptureError("readiness_record_invalid")
    if data.get("binary_sha256") != facts.sha256:
        raise CaptureError("readiness_record_binding_mismatch")
    if data.get("binary_version") != facts.version:
        raise CaptureError("readiness_record_binding_mismatch")
    verdict = data.get("verdict")
    reasons = data.get("reasons")
    if verdict not in {"ready", "not_ready"} or not isinstance(reasons, list):
        raise CaptureError("readiness_record_invalid")
    if not all(isinstance(r, str) for r in reasons):
        raise CaptureError("readiness_record_invalid")
    return ReadinessFacts(
        verdict=verdict,
        reasons=tuple(reasons),
        binary_version=str(data["binary_version"]),
        binary_sha256=str(data["binary_sha256"]),
        # The record no longer carries flag text; the live preflight facts
        # own the in-memory flag set.
        detected_flags=(),
        control_candidates=STARTUP_CONTROL_CANDIDATES,
    )


# ---------------------------------------------------------------------------
# Protected attempt ledger and external authorization record.
# The ledger is non-sensitive bounded counter state: a run ID, a kind, and
# a claim/consume state. It never carries raw request data. A claimed
# record is consumed exactly once; a consumed run ID can never be re-
# claimed (no reset by any new wrapper invocation).
# ---------------------------------------------------------------------------
def _validate_run_id(run_id: str) -> None:
    if (
        not isinstance(run_id, str)
        or not run_id
        or len(run_id) > HARD_MAX_RUN_ID_BYTES
        or not RUN_ID_RE.fullmatch(run_id)
    ):
        raise CaptureError("run_id_invalid")


def _write_atomic_0600(path: Path, data: bytes) -> None:
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(path, 0o600)


def _rewrite_atomic_0600(path: Path, data: bytes) -> None:
    """Atomic rewrite of a file THIS run created (O_TRUNC, no EXCL)."""
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(path, 0o600)


def _protected_dir(path: Path) -> None:
    """Require/create a private owned 0700 directory (never follows links)."""
    if path.exists():
        if path.is_symlink() or not path.is_dir():
            raise CaptureError("protected_dir_invalid")
        st = path.lstat()
        if st.st_uid != os.getuid():
            raise CaptureError("protected_dir_not_owned")
        os.chmod(path, 0o700)
        return
    parent = path.parent
    if not parent.is_dir() or parent.is_symlink():
        raise CaptureError("protected_dir_parent_invalid")
    try:
        os.mkdir(path, 0o700)
        os.chmod(path, 0o700)
    except OSError:
        raise CaptureError("protected_dir_create_failed") from None
    st = path.lstat()
    if st.st_uid != os.getuid():
        raise CaptureError("protected_dir_not_owned")


def claim_attempt(attempts_dir: Path, run_id: str, child_kind: str) -> None:
    _validate_run_id(run_id)
    if child_kind not in {"synthetic", "actual"}:
        raise CaptureError("child_kind_invalid")
    _protected_dir(attempts_dir)
    record = {
        "schema": ATTEMPT_SCHEMA,
        "run_id": run_id,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "child_kind": child_kind,
        "state": "claimed",
        "outcome": None,
    }
    try:
        _write_atomic_0600(attempts_dir / f"{run_id}.attempt", json.dumps(record).encode("utf-8"))
    except FileExistsError:
        raise CaptureError("attempt_already_claimed") from None
    except OSError:
        raise CaptureError("attempt_claim_failed") from None


def consume_attempt(attempts_dir: Path, run_id: str, outcome: str) -> None:
    _validate_run_id(run_id)
    if outcome not in OUTCOMES:
        raise CaptureError("outcome_invalid")
    path = attempts_dir / f"{run_id}.attempt"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise CaptureError("attempt_record_invalid") from None
    if not isinstance(data, dict) or data.get("schema") != ATTEMPT_SCHEMA:
        raise CaptureError("attempt_record_invalid")
    if data.get("run_id") != run_id or data.get("state") not in {
        "claimed",
        "consumed",
    }:
        raise CaptureError("attempt_record_invalid")
    record = {
        "schema": ATTEMPT_SCHEMA,
        "run_id": run_id,
        "created_utc": str(data.get("created_utc", ""))[:32],
        "child_kind": str(data.get("child_kind", "")),
        "state": "consumed",
        "outcome": outcome,
    }
    tmp = path.with_suffix(".tmp")
    try:
        fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(json.dumps(record).encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
        os.chmod(path, 0o600)
    except OSError:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise CaptureError("attempt_consume_failed") from None


def attempt_state(attempts_dir: Path, run_id: str) -> str | None:
    _validate_run_id(run_id)
    path = attempts_dir / f"{run_id}.attempt"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("schema") != ATTEMPT_SCHEMA:
        return None
    state = data.get("state")
    return state if state in {"claimed", "consumed"} else None


def load_authorization(path: Path, run_id: str, limits: CaptureLimits) -> dict[str, Any]:
    """Validate the external strategic authorized-run record (read-only).

    The record carries identity and bound facts only: one run ID, a one-
    attempt budget, and per-run bounds that may only LOWER the hard caps.
    The utility never writes this file.
    """
    try:
        st = path.lstat()
    except OSError:
        raise CaptureError("authorization_missing") from None
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
        raise CaptureError("authorization_invalid")
    if st.st_uid != os.getuid():
        raise CaptureError("authorization_not_owned")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise CaptureError("authorization_invalid") from None
    if not isinstance(data, dict):
        raise CaptureError("authorization_invalid")
    expected = {
        "schema",
        "run_id",
        "max_attempts",
        "max_requests",
        "max_inbound_bytes",
        "max_selected_bytes",
        "deadline_seconds",
    }
    if set(data) != expected or data.get("schema") != AUTHORIZATION_SCHEMA:
        raise CaptureError("authorization_invalid")
    if data.get("run_id") != run_id:
        raise CaptureError("authorization_run_mismatch")
    for key in ("max_attempts", "max_requests", "max_inbound_bytes", "max_selected_bytes"):
        value = data.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise CaptureError("authorization_invalid")
    deadline = data.get("deadline_seconds")
    if (
        isinstance(deadline, bool)
        or not isinstance(deadline, (int, float))
        or not (0.0 < float(deadline))
    ):
        raise CaptureError("authorization_invalid")
    if (
        data["max_attempts"] > limits.max_actual_attempts
        or data["max_requests"] > limits.max_requests
        or data["max_inbound_bytes"] > limits.max_inbound_bytes
        or data["max_selected_bytes"] > limits.max_selected_bytes
        or float(deadline) > limits.deadline_seconds
    ):
        raise CaptureError("authorization_over_limits")
    return data


# ---------------------------------------------------------------------------
# Owned ephemeral loopback fake provider. Log-silent; bounded header and
# body reads (Content-Length and chunked; malformed, oversized and invalid-
# length payloads fail closed with sanitized generic responses); in-memory
# bounded JSON parsing; allowlisted frame extraction; everything discarded
# after the run. Binds 127.0.0.1 with an OS-assigned ephemeral port (bind
# 0) -- never 18020/18031.
# ---------------------------------------------------------------------------
class ProviderState:
    """Bounded in-memory provider accounting for one run."""

    def __init__(self, limits: CaptureLimits, model: str, mode: str, token: str) -> None:
        self.limits = limits
        self.model = model
        self.mode = mode
        self.token = token
        self.lock = threading.Lock()
        self.request_count = 0
        self.responses_count = 0
        self.ingress_bytes_total = 0
        self.auth_rejected = 0
        self.malformed_count = 0
        self.status_counts: dict[str, int] = {}
        self.fatal_mode_mismatch = False
        self.request_limit_hit = False
        self.frames: list[dict[str, Any]] = []
        self.rejection_counts: dict[str, int] = {}
        self.unsupported_item_type_count = 0
        self.unsupported_item_types: set[str] = set()
        self.selected_bytes_total = 0
        self.response_script_index = 0

    def count_status(self, status: int) -> None:
        with self.lock:
            key = str(status)
            self.status_counts[key] = self.status_counts.get(key, 0) + 1

    def reject_frame(self, reason: str) -> None:
        with self.lock:
            self.rejection_counts[reason] = self.rejection_counts.get(reason, 0) + 1


@dataclass(frozen=True)
class DeclaredStep:
    """One predeclared harmless synthetic command (controller-owned)."""

    index: int
    tool_name: str
    kind: str  # "read" | "sleep"
    path: str  # literal workspace-relative file (kind read) or "" (sleep)
    seconds: float  # 0.0 for read, positive for sleep
    workdir: str = "."

    def cmd_text(self) -> str:
        if self.kind == "read":
            return f"cat {self.path}"
        return f"sleep {self.seconds:g}"


def default_declared_steps() -> tuple[DeclaredStep, ...]:
    return (
        DeclaredStep(index=0, tool_name="exec_command", kind="read", path="A.md", seconds=0.0),
        DeclaredStep(index=1, tool_name="exec_command", kind="sleep", path="", seconds=0.3),
    )


def render_sse_events(events: list[dict[str, Any]]) -> bytes:
    parts: list[bytes] = []
    for event in events:
        payload = event.get("data")
        if payload is None:
            raise CaptureError("controller_event_invalid")
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        if len(data) > HARD_MAX_SSE_EVENT_BYTES:
            raise CaptureError("controller_event_over_bound")
        parts.append(f"event: {event['type']}\ndata: ".encode() + data + b"\n\n")
    return b"".join(parts)


class FakeProvider:
    """The owned fake provider: server, scripted controller, extraction."""

    def __init__(
        self,
        *,
        state: ProviderState,
        steps: tuple[DeclaredStep, ...],
        canary: str,
    ) -> None:
        self.state = state
        self.steps = steps
        self.canary = canary
        self._issued: list[tuple[str, int]] = []
        self._ack_count = 0
        self._server: ThreadingHTTPServer | None = None
        self._port = 0
        self._thread: threading.Thread | None = None

    # -- lifecycle ---------------------------------------------------------
    def start(self) -> int:
        outer = self

        class Handler(_SilentRequestHandler):
            provider = outer

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._server.daemon_threads = True
        self._port = self._server.server_address[1]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self._port

    def stop(self) -> None:
        if self._server is not None:
            try:
                self._server.shutdown()
            except Exception:  # noqa: BLE001 - shutdown must never raise
                pass
            try:
                self._server.server_close()
            except Exception:  # noqa: BLE001
                pass
            self._server = None
        if self._thread is not None:
            self._thread.join(timeout=HARD_CHILD_IO_TIMEOUT_SECONDS)
            self._thread = None

    # -- scripted controller ----------------------------------------------
    def _input_call_state(self, payload: Any) -> dict[str, str]:
        """Latest output status per call ID in this request's input."""
        status_by_call: dict[str, str] = {}
        items, _ = _iter_items(payload)
        for entry in items:
            if entry.get("type") not in {
                "function_call_output",
                "custom_tool_call_output",
            }:
                continue
            call_id = entry.get("call_id")
            if not isinstance(call_id, str):
                continue
            output = entry.get("output")
            if isinstance(output, str):
                try:
                    output = json.loads(output)
                except (ValueError, RecursionError):
                    continue
            if isinstance(output, dict):
                status = output.get("status")
                if isinstance(status, str):
                    status_by_call[call_id] = status
        return status_by_call

    def next_response(self, payload: Any) -> bytes:
        """Scripted synthetic responses; a content-aware step machine.

        A new declared tool call is issued only when the previous call has
        a COMPLETED output in the request input (or it is the first call).
        A request whose newest output for the current call is still
        ``running`` gets a bounded in-progress acknowledgement (no new
        items). Once every declared step has been called and completed,
        the final message is returned. Only predeclared harmless frames
        are ever emitted.
        """
        st = self.state
        with st.lock:
            issued: list[tuple[str, int]] = list(self._issued)
            status_by_call = self._input_call_state(payload)
            if issued:
                last_call_id, _ = issued[-1]
                if status_by_call.get(last_call_id) == "running":
                    ack_id = f"ack_{len(issued) + 1:02d}"
                    self._ack_count += 1
                    st.response_script_index += 1
                    return render_sse_events(
                        [
                            {
                                "type": "response.in_progress",
                                "data": {
                                    "type": "response.in_progress",
                                    "response": {"id": ack_id, "status": "in_progress"},
                                },
                            }
                        ]
                    )
            next_index = len(issued)
            can_issue = next_index < len(self.steps)
            if can_issue:
                if issued:
                    last_call_id, _ = issued[-1]
                    if status_by_call.get(last_call_id) != "completed":
                        can_issue = False
            if not can_issue:
                st.response_script_index += 1
                final_item = {
                    "type": "message",
                    "id": "msg_final",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "DONE"}],
                }
                return render_sse_events(
                    [
                        {
                            "type": "response.created",
                            "data": {
                                "type": "response.created",
                                "response": {"id": "resp_final", "status": "in_progress"},
                            },
                        },
                        {
                            "type": "response.output_item.added",
                            "data": {
                                "type": "response.output_item.added",
                                "sequence_number": 0,
                                "item": final_item,
                            },
                        },
                        {
                            "type": "response.completed",
                            "data": {
                                "type": "response.completed",
                                "response": {"id": "resp_final", "status": "completed"},
                            },
                        },
                    ]
                )
            step = self.steps[next_index]
            call_id = f"call_{next_index + 1:02d}"
            self._issued.append((call_id, next_index))
            st.response_script_index += 1
            if st.mode == "responses-function-tool":
                item = {
                    "type": "function_call",
                    "id": f"msg_{next_index + 1:02d}",
                    "call_id": call_id,
                    "name": step.tool_name,
                    "arguments": json.dumps(
                        {"cmd": step.cmd_text(), "workdir": step.workdir},
                        separators=(",", ":"),
                    ),
                }
            else:
                item = {
                    "type": "custom_tool_call",
                    "id": f"msg_{next_index + 1:02d}",
                    "call_id": call_id,
                    "name": step.tool_name,
                    "input": f"synthetic-custom-input-{next_index + 1:02d}",
                }
            return render_sse_events(
                [
                    {
                        "type": "response.created",
                        "data": {
                            "type": "response.created",
                            "response": {
                                "id": f"resp_{next_index + 1:02d}",
                                "status": "in_progress",
                            },
                        },
                    },
                    {
                        "type": "response.output_item.added",
                        "data": {
                            "type": "response.output_item.added",
                            "sequence_number": 0,
                            "item": item,
                        },
                    },
                    {
                        "type": "response.completed",
                        "data": {
                            "type": "response.completed",
                            "response": {"id": f"resp_{next_index + 1:02d}", "status": "completed"},
                        },
                    },
                ]
            )

    @staticmethod
    def _declared_cmd(step: DeclaredStep) -> str:
        return step.cmd_text()

    # -- per-request handling ----------------------------------------------
    def handle_responses_post(self, body: bytes) -> tuple[int, bytes]:
        st = self.state
        with st.lock:
            st.responses_count += 1
            st.ingress_bytes_total += min(len(body), st.limits.max_inbound_bytes)
            if st.responses_count > st.limits.max_requests:
                st.request_limit_hit = True
                return 429, b"rate limited\n"
        try:
            payload = json.loads(body.decode("utf-8"))
        except (ValueError, RecursionError, MemoryError):
            st.malformed_count += 1
            return 400, b"bad request\n"
        if not isinstance(payload, dict):
            st.malformed_count += 1
            return 400, b"bad request\n"
        if payload.get("model") != st.model:
            st.malformed_count += 1
            return 400, b"bad request\n"
        mode = observe_tool_mode(payload)
        if mode == "unknown":
            st.fatal_mode_mismatch = True
            return 400, b"bad request\n"
        if mode != st.mode:
            st.fatal_mode_mismatch = True
            return 400, b"bad request\n"
        frames, rejections, unknown_types = extract_frames(
            payload,
            declared_steps=self.steps,
            canary=self.canary,
            request_seq=st.responses_count,
            mode=st.mode,
        )
        with st.lock:
            st.frames.extend(frames)
            for reason, count in rejections.items():
                st.rejection_counts[reason] = st.rejection_counts.get(reason, 0) + count
            st.unsupported_item_type_count += len(unknown_types)
            st.unsupported_item_types.update(unknown_types)
        if st.fatal_mode_mismatch:
            return 400, b"bad request\n"
        response_bytes = self.next_response(payload)
        return 200, response_bytes


class _SilentRequestHandler(BaseHTTPRequestHandler):
    """Log-silent bounded HTTP handler for the owned fake provider."""

    protocol_version = "HTTP/1.1"
    server_version = "SLAIFFakeProvider"
    sys_version = ""
    provider: FakeProvider  # set by the enclosing class factory

    def setup(self) -> None:  # noqa: N802 - http.server API
        super().setup()
        # Finite reads: a client that stalls mid-headers or mid-body must be
        # rejected with a sanitized error, never pin the handler thread.
        self.connection.settimeout(HARD_REQUEST_READ_TIMEOUT_SECONDS)

    def log_message(self, *args: object) -> None:  # noqa: D102 - silent
        return

    # -- helpers -----------------------------------------------------------
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        try:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        self.close_connection = True

    def _headers_ok(self) -> bool:
        st = self.provider.state
        total = 0
        for name, value in self.headers.items():
            total += len(name) + len(value) + 4
            if len(value) > HARD_MAX_HEADER_LINE_BYTES:
                st.malformed_count += 1
                return False
        if len(self.headers) > HARD_MAX_HEADER_LINES or total > HARD_MAX_HEADER_BYTES:
            st.malformed_count += 1
            return False
        return True

    def _read_body(self) -> tuple[bytes | None, int]:
        """Finite bounded body read. Returns (body, status); body None =>
        the client must be rejected with the given sanitized status."""
        st = self.provider.state
        te = (self.headers.get("Transfer-Encoding") or "").lower()
        cl = self.headers.get("Content-Length")
        if "chunked" in te and cl is not None:
            return None, 400
        if "chunked" in te:
            return self._read_chunked()
        if cl is None:
            return b"", 200
        if not cl.isdigit() or len(cl) > 12:
            return None, 400
        length = int(cl)
        remaining = st.limits.max_inbound_bytes
        if length > remaining:
            return None, 413
        chunks: list[bytes] = []
        received = 0
        try:
            while received < length:
                chunk = self.rfile.read(min(65536, length - received))
                if not chunk:
                    return None, 400  # incomplete body
                chunks.append(chunk)
                received += len(chunk)
        except (OSError, ValueError):
            return None, 400
        return b"".join(chunks), 200

    def _read_chunked(self) -> tuple[bytes | None, int]:
        st = self.provider.state
        remaining = st.limits.max_inbound_bytes
        chunks: list[bytes] = []
        try:
            while True:
                size_line = self.rfile.readline(HARD_MAX_HEADER_LINE_BYTES + 2)
                if len(size_line) > HARD_MAX_HEADER_LINE_BYTES:
                    return None, 400
                if not size_line.endswith(b"\r\n"):
                    return None, 400
                token = size_line[:-2].split(b";", 1)[0].strip()
                if not token or len(token) > 16:
                    return None, 400
                if not re.fullmatch(rb"[0-9a-fA-F]+", token):
                    return None, 400
                size = int(token, 16)
                if size > remaining:
                    return None, 413
                if size == 0:
                    # Bounded trailer drain (ignored), then end.
                    while True:
                        trailer = self.rfile.readline(HARD_MAX_HEADER_LINE_BYTES + 2)
                        if trailer in (b"\r\n", b"\n", b""):
                            break
                        if len(trailer) > HARD_MAX_HEADER_LINE_BYTES:
                            return None, 400
                    return b"".join(chunks), 200
                data = self.rfile.read(size)
                if len(data) != size:
                    return None, 400
                terminator = self.rfile.read(2)
                if terminator != b"\r\n":
                    return None, 400
                chunks.append(data)
                remaining -= size
        except (OSError, ValueError):
            return None, 400

    # -- routes ------------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802 - http.server API
        st = self.provider.state
        if not self._headers_ok():
            st.count_status(400)
            self._send(400, b"bad request\n", "text/plain")
            return
        if self.path != "/v1/models":
            st.count_status(404)
            self._send(404, b"not found\n", "text/plain")
            return
        if not self._auth_ok():
            st.count_status(401)
            self._send(401, b"unauthorized\n", "text/plain")
            return
        over_limit = False
        with st.lock:
            st.request_count += 1
            if st.request_count > st.limits.max_requests:
                st.request_limit_hit = True
                over_limit = True
        if over_limit:
            st.count_status(429)
            self._send(429, b"rate limited\n", "text/plain")
            return
        body = json.dumps(
            {"object": "list", "data": [{"id": st.model, "object": "model"}]},
            separators=(",", ":"),
        ).encode("utf-8")
        st.count_status(200)
        self._send(200, body, "application/json")

    def do_POST(self) -> None:  # noqa: N802 - http.server API
        st = self.provider.state
        if not self._headers_ok():
            st.count_status(400)
            self._send(400, b"bad request\n", "text/plain")
            return
        if self.path != "/v1/responses":
            st.count_status(404)
            self._send(404, b"not found\n", "text/plain")
            return
        body, status = self._read_body()
        if body is None:
            st.malformed_count += 1
            st.count_status(status)
            self.close_connection = True
            self._send(status, b"bad request\n", "text/plain")
            return
        if not self._auth_ok():
            st.count_status(401)
            self._send(401, b"unauthorized\n", "text/plain")
            return
        over_limit = False
        with st.lock:
            st.request_count += 1
            if st.request_count > st.limits.max_requests:
                st.request_limit_hit = True
                over_limit = True
        if over_limit:
            st.count_status(429)
            self._send(429, b"rate limited\n", "text/plain")
            return
        status, response = self.provider.handle_responses_post(body)
        st.count_status(status)
        content_type = "text/event-stream" if status == 200 else "text/plain"
        self._send(status, response, content_type)

    def _auth_ok(self) -> bool:
        """Validate the synthetic credential in memory; never record it."""
        st = self.provider.state
        header = self.headers.get("Authorization")
        if header is None:
            st.auth_rejected += 1
            return False
        prefix = "Bearer "
        if not header.startswith(prefix):
            st.auth_rejected += 1
            return False
        if not secrets.compare_digest(header[len(prefix) :], st.token):
            st.auth_rejected += 1
            return False
        return True


# ---------------------------------------------------------------------------
# Allowlisted extraction. Pure, in-memory, content-free: only declared
# synthetic frames and bounded metadata are selected; everything else is
# typed, counted, and never echoed.
# ---------------------------------------------------------------------------
def _bounded_str(value: Any, cap: int) -> str | None:
    if not isinstance(value, str) or not value or len(value) > cap:
        return None
    return value


def _digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _output_payload_bytes(output: Any) -> bytes | None:
    if isinstance(output, str):
        return output.encode("utf-8")
    if isinstance(output, dict):
        try:
            return json.dumps(output, sort_keys=True, separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError):
            return None
    return None


def _frame_base(seq: int, request_seq: int, item_type: str, call_id: str) -> dict[str, Any]:
    return {
        "seq": seq,
        "request_seq": request_seq,
        "item_type": item_type,
        "call_id": call_id,
        "name": None,
        "declared_command_index": None,
        "input_digest": None,
        "input_bytes": None,
        "output_digest": None,
        "output_bytes": None,
        "status": None,
        "process_id": None,
        "session_id": None,
        "chunk_id": None,
        "chunk_index": None,
        "exit_code": None,
        "parent_call_id": None,
        "output_field_names": None,
    }


def _iter_items(payload: Any) -> tuple[list[dict[str, Any]], set[str]]:
    """Collect item containers from a parsed Responses request, in order.

    Returns (items, unknown_types): selected-shape items plus the bounded
    set of observed non-selectable ``type`` tokens (metadata only).
    """
    items: list[dict[str, Any]] = []
    unknown: set[str] = set()
    input_value = payload.get("input") if isinstance(payload, dict) else None
    if isinstance(input_value, str) or input_value is None:
        return items, unknown
    if not isinstance(input_value, list) or len(input_value) > 4096:
        return items, unknown
    entries: list[dict[str, Any]] = []
    for entry in input_value:
        if not isinstance(entry, dict):
            continue
        entries.append(entry)
        content = entry.get("content")
        if isinstance(content, list):
            for sub in content:
                if isinstance(sub, dict):
                    entries.append(sub)
    for entry in entries:
        item_type = entry.get("type")
        if not isinstance(item_type, str):
            continue
        if item_type in ITEM_TYPES:
            items.append(entry)
        elif (
            len(item_type) <= HARD_MAX_ITEM_TYPE_BYTES
            and len(unknown) < HARD_MAX_UNSUPPORTED_TYPE_SAMPLES
        ):
            unknown.add(item_type)
    return items, unknown


def _check_declared_command(arguments: Any, steps: tuple[DeclaredStep, ...]) -> int | None:
    if not isinstance(arguments, str):
        return None
    if len(arguments) > HARD_MAX_STEP_BYTES * 4:
        return None
    try:
        parsed = json.loads(arguments)
    except (ValueError, RecursionError):
        return None
    if not isinstance(parsed, dict):
        return None
    if set(parsed) != {"cmd", "workdir"}:
        return None
    cmd = parsed.get("cmd")
    workdir = parsed.get("workdir")
    if not isinstance(cmd, str) or not isinstance(workdir, str):
        return None
    for step in steps:
        if step.tool_name != "exec_command":
            continue
        if cmd == FakeProvider._declared_cmd(step) and workdir == step.workdir:
            return step.index
    return None


def extract_frames(
    payload: Any,
    *,
    declared_steps: tuple[DeclaredStep, ...],
    canary: str,
    request_seq: int,
    mode: str,
) -> tuple[list[dict[str, Any]], dict[str, int], frozenset[str]]:
    """Extract allowlisted frames from ONE parsed request payload."""
    frames: list[dict[str, Any]] = []
    rejections: dict[str, int] = {}
    items, unknown_types = _iter_items(payload)
    seq = 0

    def reject(reason: str) -> None:
        rejections[reason] = rejections.get(reason, 0) + 1

    for entry in items:
        item_type = entry.get("type")
        call_id = _bounded_str(entry.get("call_id"), HARD_MAX_CALL_ID_BYTES)
        if call_id is None or not CALL_ID_RE.fullmatch(call_id):
            if isinstance(item_type, str) and item_type in ITEM_TYPES:
                reject("call_id_invalid")
            continue
        seq += 1
        frame = _frame_base(seq, request_seq, item_type, call_id)

        if item_type in {"function_call", "custom_tool_call"}:
            name = _bounded_str(entry.get("name"), HARD_MAX_NAME_BYTES)
            if name is None or name not in {s.tool_name for s in declared_steps}:
                reject("name_not_declared")
                continue
            frame["name"] = name
            if item_type == "function_call":
                index = _check_declared_command(entry.get("arguments"), declared_steps)
                if index is None:
                    reject("command_not_declared")
                    continue
                frame["declared_command_index"] = index
            else:
                tool_input = entry.get("input")
                if not isinstance(tool_input, str) or not tool_input:
                    reject("input_shape_unsupported")
                    continue
                if canary in tool_input:
                    reject("credential_marker_present")
                    continue
                data = tool_input.encode("utf-8")
                if len(data) > HARD_MAX_METADATA_BYTES * 4:
                    reject("metadata_value_over_bound")
                    continue
                frame["input_digest"] = _digest_bytes(data)
                frame["input_bytes"] = len(data)
            frames.append(frame)
        else:
            # Output frames.
            output = entry.get("output")
            payload_bytes = _output_payload_bytes(output)
            if payload_bytes is None:
                reject("output_shape_unsupported")
                continue
            if canary.encode("utf-8") in payload_bytes:
                reject("credential_marker_present")
                continue
            frame["output_digest"] = _digest_bytes(payload_bytes)
            frame["output_bytes"] = len(payload_bytes)
            structured: Any = output
            if isinstance(output, str):
                # A string output may carry a JSON object wrapper inside
                # the exact bytes; the digest always stays on the raw bytes.
                try:
                    parsed = json.loads(output)
                except (ValueError, RecursionError):
                    parsed = None
                if isinstance(parsed, dict):
                    structured = parsed
            if not isinstance(structured, dict):
                # Plain-string (non-JSON) outputs carry no declared
                # completion metadata: digest/bytes only; the transition
                # stays incomplete (never "completed").
                frames.append(frame)
                continue
            names = sorted(structured.keys())
            if (
                len(names) > HARD_MAX_FIELD_NAMES
                or any(len(n) > HARD_MAX_NAME_BYTES for n in names)
                or not set(names) <= OUTPUT_DICT_KEYS
            ):
                reject("output_shape_unsupported")
                continue
            frame["output_field_names"] = names
            bad = False
            for key in ("process_id", "session_id", "chunk_id"):
                value = _bounded_str(structured.get(key), HARD_MAX_METADATA_BYTES)
                if structured.get(key) is not None and value is None:
                    reject("metadata_value_over_bound")
                    bad = True
                    break
                frame[key] = value
            if bad:
                continue
            exit_code = structured.get("exit_code")
            if exit_code is not None and (
                isinstance(exit_code, bool)
                or not isinstance(exit_code, int)
                or not (0 <= exit_code <= 255)
            ):
                reject("metadata_value_over_bound")
                continue
            frame["exit_code"] = None if exit_code is None else int(exit_code)
            chunk_index = structured.get("chunk_index")
            if chunk_index is not None and (
                isinstance(chunk_index, bool)
                or not isinstance(chunk_index, int)
                or not (0 <= chunk_index <= 10_000)
            ):
                reject("metadata_value_over_bound")
                continue
            frame["chunk_index"] = None if chunk_index is None else int(chunk_index)
            status = structured.get("status")
            if status is not None:
                if status not in OUTPUT_STATUSES:
                    reject("output_shape_unsupported")
                    continue
                frame["status"] = status
            frames.append(frame)
    return frames, rejections, frozenset(unknown_types)


def observe_tool_mode(payload: Any) -> str:
    """Read the actual offered tool schema (in memory). Unknown => closed."""
    tools = payload.get("tools") if isinstance(payload, dict) else None
    if not isinstance(tools, list) or not tools:
        return "unknown"
    types: set[str] = set()
    for tool in tools:
        if not isinstance(tool, dict):
            return "unknown"
        ttype = tool.get("type")
        if not isinstance(ttype, str) or ttype not in TOOL_SCHEMA_TYPES:
            return "unknown"
        types.add(ttype)
    if types == {"function"}:
        return "responses-function-tool"
    if types == {"custom"}:
        return "responses-custom-tool"
    return "unknown"


def build_transitions(frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pair call frames with output frames by causal call ID (no
    flattening: each output keeps its own frame; the transition only links
    sequences)."""
    calls: dict[str, dict[str, Any]] = {}
    outputs: dict[str, list[dict[str, Any]]] = {}
    for frame in frames:
        if frame["item_type"] in {"function_call", "custom_tool_call"}:
            calls.setdefault(frame["call_id"], frame)
        else:
            outputs.setdefault(frame["call_id"], []).append(frame)
    transitions: list[dict[str, Any]] = []
    for call_id in sorted(calls):
        outs = outputs.get(call_id, [])
        if not outs:
            continue
        final_status = None
        for out in outs:
            if out["status"] is not None:
                final_status = out["status"]
        transitions.append(
            {
                "call_id": call_id,
                "call_request_seq": calls[call_id]["request_seq"],
                "first_output_request_seq": min(o["request_seq"] for o in outs),
                "output_frame_count": len(outs),
                "final_status": final_status,
            }
        )
    return transitions


def build_selection(
    *,
    run_id: str,
    state: ProviderState,
    steps: tuple[DeclaredStep, ...],
    deadline_seconds: float,
    elapsed_seconds: float,
    child_kind: str,
    client_version: str | None,
    client_sha256: str | None,
) -> dict[str, Any]:
    frames = sorted(state.frames, key=lambda f: (f["request_seq"], f["seq"]))
    total = sum(f["output_bytes"] or 0 for f in frames)
    total += sum(f["input_bytes"] or 0 for f in frames)
    provenance = "synthetic-offline" if child_kind == "synthetic" else "actual-capture"
    return {
        "schema": SELECTION_SCHEMA,
        "provenance": provenance,
        "fixture_authority": "none",
        "run_id": run_id,
        "client": {
            "mode": state.mode,
            "version": client_version,
            "binary_sha256": client_sha256,
        },
        "requests": {
            "count": state.responses_count,
            "ingress_bytes_total": state.ingress_bytes_total,
        },
        "deadline_seconds": deadline_seconds,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "frames": frames,
        "transitions": build_transitions(frames),
        "rejected": {
            "reason_counts": dict(state.rejection_counts),
            "unsupported_item_type_count": state.unsupported_item_type_count,
            "unsupported_item_type_digest": (
                None
                if not state.unsupported_item_types
                else _digest_bytes("\n".join(sorted(state.unsupported_item_types)).encode("utf-8"))
            ),
        },
        "selected_bytes_total": total,
    }


# ---------------------------------------------------------------------------
# Scratch workspace, child environment, child supervision, cleanup.
# ---------------------------------------------------------------------------
WORKSPACE_FILES: tuple[tuple[str, bytes], ...] = (
    ("A.md", b"alpha file content\n"),
    ("B.md", b"beta file content\n"),
    ("empty.txt", b""),
    ("large.txt", b"x" * (200 * 1024) + b"\n"),
)


@dataclass
class ScratchSetup:
    root: Path
    child_home: Path
    child_home_home: Path
    workspace: Path
    created: bool  # this run created the root (only then may cleanup remove it)


def setup_scratch(
    base: Path,
    run_id: str,
    extra_workspace_files: tuple[tuple[str, bytes], ...] = (),
) -> ScratchSetup:
    _protected_dir(base)
    root = base / f"slaif-capture-{run_id}"
    if root.exists() or root.is_symlink():
        raise CaptureError("scratch_root_exists")
    parts: dict[str, Path] = {}
    try:
        os.mkdir(root, 0o700)
        os.chmod(root, 0o700)
        for name in ("child-home", "child-home-home", "workspace"):
            path = root / name
            os.mkdir(path, 0o700)
            os.chmod(path, 0o700)
            parts[name] = path
        for name, data in WORKSPACE_FILES:
            file_path = parts["workspace"] / name
            _write_atomic_0600(file_path, data)
        for name, data in extra_workspace_files:
            if not name or "/" in name or name.startswith("."):
                raise CaptureError("workspace_file_name_invalid")
            if len(name) > HARD_MAX_NAME_BYTES or len(data) > HARD_MAX_INBOUND_BYTES:
                raise CaptureError("workspace_file_over_bound")
            file_path = parts["workspace"] / name
            _write_atomic_0600(file_path, data)
    except CaptureError:
        raise
    except OSError:
        raise CaptureError("scratch_setup_failed") from None
    st = root.lstat()
    if st.st_uid != os.getuid():
        raise CaptureError("scratch_root_not_owned")
    return ScratchSetup(
        root=root,
        child_home=parts["child-home"],
        child_home_home=parts["child-home-home"],
        workspace=parts["workspace"],
        created=True,
    )


def write_child_config(child_home: Path, port: int, model: str) -> Path:
    text = (
        f'model = "{model}"\n'
        'model_provider = "slaif-capture"\n'
        "\n"
        "[model_providers.slaif-capture]\n"
        'name = "SLAIF synthetic capture provider"\n'
        f'base_url = "http://127.0.0.1:{port}/v1"\n'
        f'env_key = "{CHILD_ENV_TOKEN_NAME}"\n'
        'wire_api = "responses"\n'
    )
    path = child_home / "config.toml"
    _write_atomic_0600(path, text.encode("utf-8"))
    return path


def build_child_env(scratch: ScratchSetup, token: str) -> dict[str, str]:
    """From-scratch child environment: nothing inherited from the parent."""
    home = str(scratch.child_home_home)
    return {
        "PATH": CHILD_ENV_FIXED_PATH,
        "HOME": home,
        "CODEX_HOME": str(scratch.child_home),
        "XDG_CONFIG_HOME": home + "/.config",
        "XDG_DATA_HOME": home + "/.data",
        "XDG_CACHE_HOME": home + "/.cache",
        "XDG_STATE_HOME": home + "/.state",
        "LC_ALL": "C.UTF-8",
        CHILD_ENV_CHILD_NAME: "1",
        CHILD_ENV_TOKEN_NAME: token,
    }


def collect_child_env_facts(scratch: ScratchSetup) -> dict[str, Any] | None:
    """Read the closed child-side environment-isolation fact file (if the
    synthetic child wrote one). Booleans only; content-free."""
    path = scratch.child_home / "env-fact.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    expected = {
        "parent_marker_present": bool,
        "codex_home_is_child": bool,
        "token_env_present": bool,
    }
    if set(data) != set(expected):
        return None
    if any(not isinstance(data[key], expected[key]) for key in expected):
        return None
    return {key: bool(data[key]) for key in sorted(expected)}


@dataclass
class ChildFacts:
    returncode: int | None
    stdout_bytes: int
    stderr_bytes: int
    timed_out: bool
    output_cap_exceeded: bool
    group_cleanup_verified: bool


def _group_members_gone(pgid: int, grace_seconds: float = 10.0) -> bool:
    deadline = time.monotonic() + grace_seconds
    while True:
        found = False
        try:
            pids = os.listdir("/proc")
        except OSError:
            return True
        for entry in pids:
            if not entry.isdigit():
                continue
            try:
                with open(f"/proc/{entry}/stat", "rb") as stream:
                    stat_text = stream.read(4096)
            except OSError:
                continue
            # Fields: pid (comm) state ppid pgrp ... ; comm may contain
            # spaces/parens, so parse from the last closing paren.
            try:
                tail = stat_text.rsplit(b")", 1)[1].split()
            except IndexError:
                continue
            if len(tail) >= 3:
                try:
                    if int(tail[2]) == pgid:
                        found = True
                        break
                except ValueError:
                    continue
        if not found:
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.05)


def _reap_group_members(pgid: int, grace_seconds: float = 2.0) -> None:
    """TERM (then KILL) leftover members of one owned process group."""
    deadline = time.monotonic() + grace_seconds
    while True:
        try:
            os.killpg(pgid, signal.SIGTERM)
        except OSError:
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(0.05)
    try:
        os.killpg(pgid, signal.SIGKILL)
    except OSError:
        pass


def kill_process_group(proc: subprocess.Popen[bytes], grace_seconds: float = 5.0) -> None:
    if proc.poll() is not None:
        return
    try:
        pgid = os.getpgid(proc.pid)
    except OSError:
        return
    try:
        os.killpg(pgid, signal.SIGTERM)
    except OSError:
        return
    deadline = time.monotonic() + grace_seconds
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            return
        time.sleep(0.05)
    if proc.poll() is None:
        try:
            os.killpg(pgid, signal.SIGKILL)
        except OSError:
            pass


def run_child(
    *,
    argv: list[str],
    env: dict[str, str],
    cwd: Path,
    limits: CaptureLimits,
    stdin_bytes: bytes | None = None,
) -> ChildFacts:
    """Supervise one owned child session (always a new session/group).

    stdout/stderr are drained in bounded memory: byte counts only, never
    content. Exceeding the aggregate output cap, or the hard deadline,
    terminates the owned group (SIGTERM then SIGKILL) and nothing else.
    """
    proc = subprocess.Popen(
        argv,
        stdin=subprocess.PIPE if stdin_bytes is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=str(cwd),
        start_new_session=True,
    )
    assert proc.stdout is not None
    assert proc.stderr is not None
    try:
        pgid = os.getpgid(proc.pid)
    except OSError:
        pgid = proc.pid
    state: dict[str, Any] = {"stdout": 0, "stderr": 0, "cap": False}
    state_lock = threading.Lock()

    def kill_session() -> None:
        with state_lock:
            if state.get("killer_armed"):
                return
            state["killer_armed"] = True
        kill_process_group(proc)

    def drain(stream: Any, key: str) -> None:
        try:
            while True:
                chunk = stream.read(65536)
                if not chunk:
                    break
                exceeded = False
                with state_lock:
                    state[key] += len(chunk)
                    total = state["stdout"] + state["stderr"]
                    exceeded = total > limits.max_child_output_bytes
                    if exceeded:
                        state["cap"] = True
                if exceeded:
                    kill_session()
        except (OSError, ValueError):
            return

    out_thread = threading.Thread(target=drain, args=(proc.stdout, "stdout"), daemon=True)
    err_thread = threading.Thread(target=drain, args=(proc.stderr, "stderr"), daemon=True)
    out_thread.start()
    err_thread.start()
    if proc.stdin is not None:
        try:
            proc.stdin.write(stdin_bytes or b"")
            proc.stdin.close()
        except (BrokenPipeError, OSError):
            pass
    timed_out = False
    deadline = time.monotonic() + limits.deadline_seconds
    try:
        proc.wait(timeout=max(0.05, limits.deadline_seconds))
    except subprocess.TimeoutExpired:
        timed_out = True
        kill_process_group(proc)
        try:
            proc.wait(timeout=HARD_CHILD_IO_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            pass
    out_thread.join(timeout=HARD_CHILD_IO_TIMEOUT_SECONDS)
    err_thread.join(timeout=HARD_CHILD_IO_TIMEOUT_SECONDS)
    for stream in (proc.stdout, proc.stderr):
        try:
            stream.close()
        except OSError:
            pass
    if proc.stdin is not None:
        try:
            proc.stdin.close()
        except OSError:
            pass
    with state_lock:
        stdout_bytes = min(state["stdout"], limits.max_child_output_bytes)
        stderr_bytes = min(state["stderr"], limits.max_child_output_bytes)
        cap = state["cap"]
    # Cleanup on BOTH paths (normal exit and timeout): the run owns the
    # whole session group, so any leftover member is reaped here. Only the
    # owned pgid is ever signalled; unrelated processes are untouched.
    _reap_group_members(pgid)
    group_gone = _group_members_gone(pgid)
    _ = deadline
    return ChildFacts(
        returncode=proc.returncode,
        stdout_bytes=stdout_bytes,
        stderr_bytes=stderr_bytes,
        timed_out=timed_out,
        output_cap_exceeded=cap,
        group_cleanup_verified=group_gone,
    )


def cleanup_root(root: Path) -> int:
    """Exact per-entry validated removal of the exact owned scratch root.

    Refuses symlinks, special files, foreign ownership, and any path that
    is not strictly inside the root. Returns the removed entry count.
    """
    if root.is_symlink() or not root.is_dir():
        raise CaptureError("cleanup_root_invalid")
    st = root.lstat()
    if st.st_uid != os.getuid():
        raise CaptureError("cleanup_root_not_owned")
    root_real = root.resolve()
    removed = 0
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        current = Path(dirpath)
        for name in list(dirnames) + list(filenames):
            path = current / name
            try:
                lst = path.lstat()
            except OSError:
                continue
            if stat.S_ISLNK(lst.st_mode) or not (
                stat.S_ISREG(lst.st_mode) or stat.S_ISDIR(lst.st_mode)
            ):
                raise CaptureError("cleanup_entry_unexpected_type")
            if lst.st_uid != os.getuid():
                raise CaptureError("cleanup_entry_not_owned")
            if not path.resolve().is_relative_to(root_real):
                raise CaptureError("cleanup_entry_escape")
            if stat.S_ISDIR(lst.st_mode):
                os.rmdir(path)
            else:
                os.unlink(path)
            removed += 1
    os.rmdir(root)
    if root.exists() or root.is_symlink():
        raise CaptureError("cleanup_root_remains")
    return removed


# ---------------------------------------------------------------------------
# Orchestration.
# ---------------------------------------------------------------------------
SYNTHETIC_MODEL = "synthetic-capture-model"
CONTROL_SCHEMA = "slaif-real-client-capture-control-v1"
DRAIN_GRACE_SECONDS = 2.0
HARD_REQUEST_READ_TIMEOUT_SECONDS = 2.0
PROVIDER_ERROR_EXIT = 65
UNDECLARED_COMMAND_EXIT = 64


@dataclass
class RunOutcome:
    outcome: str
    run_record: dict[str, Any]
    selection_record: dict[str, Any] | None
    run_record_path: Path
    selection_path: Path | None
    child_facts: ChildFacts
    scratch_entries_removed: int


def _write_record(path: Path, record: dict[str, Any]) -> Path:
    _write_atomic_0600(path, (json.dumps(record, indent=1, sort_keys=True) + "\n").encode("utf-8"))
    return path


def _provider_summary(state: ProviderState) -> dict[str, Any]:
    with state.lock:
        return {
            "request_count": state.request_count,
            "responses_count": state.responses_count,
            "ingress_bytes_total": state.ingress_bytes_total,
            "auth_rejected": state.auth_rejected,
            "malformed_count": state.malformed_count,
            "status_counts": dict(state.status_counts),
            "request_limit_hit": state.request_limit_hit,
            "tool_mode_mismatch": state.fatal_mode_mismatch,
        }


def _select_outcome(
    state: ProviderState,
    child: ChildFacts,
    total_selected: int,
    limits: CaptureLimits,
) -> tuple[str, bool]:
    """Return (outcome, selection_written)."""
    if state.fatal_mode_mismatch:
        return "tool_mode_mismatch", False
    if state.request_limit_hit:
        return "request_limit_exceeded", False
    if child.timed_out:
        return "timed_out", False
    if child.output_cap_exceeded:
        return "output_cap_exceeded", False
    if child.returncode == PROVIDER_ERROR_EXIT:
        return "provider_error", False
    if child.returncode != 0:
        return "child_failure", False
    if total_selected > limits.max_selected_bytes:
        return "selected_over_bound", False
    return "completed", True


def run_capture(
    *,
    run_id: str,
    out_dir: Path,
    child: Path,
    limits: CaptureLimits | None = None,
    mode: str = "responses-function-tool",
    steps: tuple[DeclaredStep, ...] | None = None,
    markers: tuple[str, ...] = (),
    env_check_var: str | None = None,
    spawn_grandchild: bool = False,
    canary: str | None = None,
    workspace_files: tuple[tuple[str, bytes], ...] = (),
    scratch_base: Path | None = None,
    child_kind: str = "synthetic",
    allow_actual_client: bool = False,
    binary: Path | None = None,
    expected_version: str | None = None,
    expected_sha256: str | None = None,
    readiness_record: Path | None = None,
    authorized_record: Path | None = None,
) -> RunOutcome:
    """Run one bounded capture. See the module docstring for the law."""
    eff_limits = limits or CaptureLimits.resolved()
    _validate_run_id(run_id)
    if mode not in TOOL_MODES:
        raise CaptureError("mode_invalid")
    if child_kind not in {"synthetic", "actual"}:
        raise CaptureError("child_kind_invalid")
    for marker in markers:
        if marker not in {"stdout", "stderr", "header", "prompt"}:
            raise CaptureError("marker_invalid")
    declared_steps = steps or default_declared_steps()
    if len(declared_steps) > HARD_MAX_DECLARED_STEPS or any(
        not isinstance(s, DeclaredStep)
        or s.kind not in {"read", "sleep"}
        or len(s.cmd_text()) > HARD_MAX_STEP_BYTES
        for s in declared_steps
    ):
        raise CaptureError("declared_steps_invalid")
    if canary is None:
        canary = f"SYNTHETIC-CANARY-{run_id}"
    if not canary or len(canary) > HARD_MAX_METADATA_BYTES:
        raise CaptureError("canary_invalid")

    _protected_dir(out_dir)
    attempts_dir = out_dir / "attempts"

    # -- actual-client fail-closed gate (before any scratch or launch) -----
    client_version: str | None = None
    client_sha256: str | None = None
    if child_kind == "actual":
        if not allow_actual_client:
            raise CaptureError("actual_client_not_opted_in")
        if binary is None or expected_version is None or expected_sha256 is None:
            raise CaptureError("actual_binary_binding_missing")
        if readiness_record is None or authorized_record is None:
            raise CaptureError("actual_readiness_missing")
        facts = preflight_binary(Path(binary), expected_version, expected_sha256)
        readiness = load_readiness_record(Path(readiness_record), facts)
        if readiness.verdict != "ready":
            raise CaptureError("readiness_not_ready")
        load_authorization(Path(authorized_record), run_id, eff_limits)
        claim_attempt(attempts_dir, run_id, "actual")
        client_version = facts.version
        client_sha256 = facts.sha256

    if child_kind == "synthetic":
        if child.is_symlink() or not child.is_file():
            raise CaptureError("synthetic_child_missing")
        child = child.absolute()
        claim_attempt(attempts_dir, run_id, "synthetic")

    scratch_base_eff = scratch_base if scratch_base is not None else out_dir / "scratch"
    scratch = setup_scratch(scratch_base_eff, run_id, workspace_files)
    token = secrets.token_hex(16)
    outcome = "setup_failed"
    child_facts = ChildFacts(None, 0, 0, False, False, False)
    provider_summary: dict[str, Any] = {}
    selection_record: dict[str, Any] | None = None
    selection_path: Path | None = None
    scratch_entries_removed = 0
    started = time.monotonic()
    provider = FakeProvider(
        state=ProviderState(eff_limits, SYNTHETIC_MODEL, mode, token),
        steps=declared_steps,
        canary=canary,
    )
    try:
        port = provider.start()
        write_child_config(scratch.child_home, port, SYNTHETIC_MODEL)
        control: dict[str, Any] = {
            "schema": CONTROL_SCHEMA,
            "provider_base_url": f"http://127.0.0.1:{port}/v1",
            "model": SYNTHETIC_MODEL,
            "mode": mode,
            "token": token,
            "run_id": run_id,
            "steps": [
                {
                    "index": s.index,
                    "tool_name": s.tool_name,
                    "cmd": s.cmd_text(),
                    "kind": s.kind,
                    "path": s.path,
                    "seconds": s.seconds,
                    "workdir": s.workdir,
                }
                for s in declared_steps
            ],
            "markers": {
                "stdout": "stdout" in markers,
                "stderr": "stderr" in markers,
                "header": "header" in markers,
                "prompt": "prompt" in markers,
            },
            "env_check_var": env_check_var,
            "spawn_grandchild": spawn_grandchild,
        }
        control_path = scratch.root / "control.json"
        _write_atomic_0600(control_path, json.dumps(control).encode("utf-8"))
        env = build_child_env(scratch, token)
        if child_kind == "synthetic":
            argv = [sys.executable, str(child), str(control_path)]
            stdin_bytes: bytes | None = None
        else:
            assert binary is not None
            argv = [
                str(binary),
                "exec",
                "--ephemeral",
                "--json",
                "--skip-git-repo-check",
                "--ignore-rules",
                "-s",
                "danger-full-access",
                "-C",
                str(scratch.workspace),
                "-m",
                SYNTHETIC_MODEL,
                "-",
            ]
            stdin_bytes = SYNTHETIC_PROMPT.encode("utf-8")
        child_facts = run_child(
            argv=argv,
            env=env,
            cwd=scratch.workspace,
            limits=eff_limits,
            stdin_bytes=stdin_bytes,
        )
        child_env_facts = collect_child_env_facts(scratch)
        # Bounded drain grace for in-flight provider requests, then stop.
        time.sleep(min(DRAIN_GRACE_SECONDS, eff_limits.deadline_seconds / 4))
        provider.stop()
        state = provider.state
        provider_summary = _provider_summary(state)
        total_selected = sum(f["output_bytes"] or 0 for f in state.frames) + sum(
            f["input_bytes"] or 0 for f in state.frames
        )
        outcome, write_selection = _select_outcome(state, child_facts, total_selected, eff_limits)
        if write_selection:
            selection_record = build_selection(
                run_id=run_id,
                state=state,
                steps=declared_steps,
                deadline_seconds=eff_limits.deadline_seconds,
                elapsed_seconds=time.monotonic() - started,
                child_kind=child_kind,
                client_version=client_version,
                client_sha256=client_sha256,
            )
            selection_path = _write_record(out_dir / "selection.json", selection_record)
        run_record = {
            "schema": RUN_SCHEMA,
            "run_id": run_id,
            "child_kind": child_kind,
            "outcome": outcome,
            "client": {
                "mode": mode,
                "version": client_version,
                "binary_sha256": client_sha256,
            },
            "provider": provider_summary,
            "child": {
                "returncode": child_facts.returncode,
                "stdout_bytes": child_facts.stdout_bytes,
                "stderr_bytes": child_facts.stderr_bytes,
                "timed_out": child_facts.timed_out,
                "output_cap_exceeded": child_facts.output_cap_exceeded,
                "group_cleanup_verified": child_facts.group_cleanup_verified,
                "env_facts": child_env_facts,
            },
            "selection": {
                "frame_count": len(state.frames),
                "transition_count": len(build_transitions(state.frames)),
                "selected_bytes_total": total_selected,
                "rejected_counts": dict(state.rejection_counts),
                "written": write_selection,
            },
            "scratch_entries_removed": scratch_entries_removed,
            "limits": {
                "max_requests": eff_limits.max_requests,
                "max_inbound_bytes": eff_limits.max_inbound_bytes,
                "max_selected_bytes": eff_limits.max_selected_bytes,
                "deadline_seconds": eff_limits.deadline_seconds,
                "max_child_output_bytes": eff_limits.max_child_output_bytes,
            },
            "elapsed_seconds": round(time.monotonic() - started, 3),
        }
        _write_record(out_dir / "run.json", run_record)
        if not child_facts.group_cleanup_verified:
            outcome = "cleanup_failed"
            run_record["outcome"] = outcome
            _rewrite_atomic_0600(
                out_dir / "run.json",
                (json.dumps(run_record, indent=1, sort_keys=True) + "\n").encode("utf-8"),
            )
        consume_attempt(attempts_dir, run_id, outcome)
        if scratch.created:
            try:
                scratch_entries_removed = cleanup_root(scratch.root)
                run_record["scratch_entries_removed"] = scratch_entries_removed
                _rewrite_atomic_0600(
                    out_dir / "run.json",
                    (json.dumps(run_record, indent=1, sort_keys=True) + "\n").encode("utf-8"),
                )
            except CaptureError:
                outcome = "cleanup_failed"
                run_record["outcome"] = outcome
                _rewrite_atomic_0600(
                    out_dir / "run.json",
                    (json.dumps(run_record, indent=1, sort_keys=True) + "\n").encode("utf-8"),
                )
                consume_attempt(attempts_dir, run_id, outcome)
    except CaptureError:
        provider.stop()
        if scratch.created:
            try:
                cleanup_root(scratch.root)
            except CaptureError:
                pass
        if attempt_state(attempts_dir, run_id) == "claimed":
            consume_attempt(attempts_dir, run_id, "setup_failed")
        raise
    except OSError:
        provider.stop()
        if scratch.created:
            try:
                cleanup_root(scratch.root)
            except CaptureError:
                pass
        if attempt_state(attempts_dir, run_id) == "claimed":
            consume_attempt(attempts_dir, run_id, "record_write_failed")
        raise CaptureError("record_write_failed") from None
    return RunOutcome(
        outcome=outcome,
        run_record=run_record,
        selection_record=selection_record,
        run_record_path=out_dir / "run.json",
        selection_path=selection_path,
        child_facts=child_facts,
        scratch_entries_removed=scratch_entries_removed,
    )


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------
def cmd_check(args: argparse.Namespace) -> int:
    try:
        facts = preflight_binary(Path(args.binary).resolve(), args.version, args.sha256)
    except CaptureError as exc:
        print(f"check: {exc.failure_class}")
        return 1
    readiness = evaluate_startup_readiness(facts)
    record = readiness.to_record()
    if args.out_record:
        out_path = Path(args.out_record)
        try:
            _protected_dir(out_path.parent)
            _write_atomic_0600(
                out_path, (json.dumps(record, indent=1, sort_keys=True) + "\n").encode("utf-8")
            )
        except (CaptureError, OSError):
            print("check: record_write_failed")
            return 1
    print(
        "check: verdict="
        + readiness.verdict
        + " reasons="
        + ",".join(readiness.reasons)
        + " flags="
        + str(len(facts.detected_flags))
        + " version="
        + facts.version
        + " sha256="
        + facts.sha256
    )
    return 0 if readiness.verdict == "ready" else 3


def cmd_run(args: argparse.Namespace) -> int:
    try:
        limits = CaptureLimits.resolved(
            max_requests=args.max_requests,
            max_inbound_bytes=args.max_inbound_bytes,
            max_selected_bytes=args.max_selected_bytes,
            deadline_seconds=args.deadline_seconds,
            max_child_output_bytes=args.max_child_output_bytes,
        )
    except CaptureError as exc:
        print(f"run: {exc.failure_class}")
        return 2
    steps = default_declared_steps()
    if args.mode == "responses-custom-tool":
        steps = tuple(
            DeclaredStep(
                index=s.index,
                tool_name="synthetic_custom",
                kind=s.kind,
                path=s.path,
                seconds=s.seconds,
                workdir=s.workdir,
            )
            for s in steps
        )
    try:
        result = run_capture(
            run_id=args.run_id,
            out_dir=Path(args.out_dir),
            child=Path(args.child),
            limits=limits,
            mode=args.mode,
            steps=steps,
            markers=tuple(args.marker),
            env_check_var=args.env_check_var,
            spawn_grandchild=args.spawn_grandchild,
        )
    except CaptureError as exc:
        print(f"run: {exc.failure_class}")
        return 1
    print(
        "run: outcome="
        + result.outcome
        + " requests="
        + str(result.run_record["provider"]["request_count"])
        + " frames="
        + str(result.run_record["selection"]["frame_count"])
        + " transitions="
        + str(result.run_record["selection"]["transition_count"])
        + " selected_bytes="
        + str(result.run_record["selection"]["selected_bytes_total"])
        + " child_rc="
        + str(result.child_facts.returncode)
        + " group_cleanup_verified="
        + str(result.child_facts.group_cleanup_verified)
        + " scratch_removed="
        + str(result.scratch_entries_removed)
    )
    return 0 if result.outcome == "completed" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="real_client_capture",
        description="Bounded opt-in real-client process-capture utility (order 017-i, offline).",
    )
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="read-only binary preflight + static readiness")
    check.add_argument("--binary", required=True)
    check.add_argument("--version", dest="version", required=True)
    check.add_argument("--sha256", required=True)
    check.add_argument("--out-record", default=None)

    run = sub.add_parser("run", help="run one bounded capture (synthetic child by default)")
    run.add_argument("--child", required=True)
    run.add_argument("--run-id", required=True)
    run.add_argument("--out-dir", required=True)
    run.add_argument("--mode", default="responses-function-tool", choices=sorted(TOOL_MODES))
    run.add_argument("--max-requests", type=int, default=None)
    run.add_argument("--max-inbound-bytes", type=int, default=None)
    run.add_argument("--max-selected-bytes", type=int, default=None)
    run.add_argument("--deadline-seconds", type=float, default=None)
    run.add_argument("--max-child-output-bytes", type=int, default=None)
    run.add_argument(
        "--marker",
        action="append",
        default=[],
        choices=["stdout", "stderr", "header", "prompt"],
        help="enable one synthetic leak-marker channel (test aid)",
    )
    run.add_argument("--env-check-var", default=None)
    run.add_argument("--spawn-grandchild", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "check":
        return cmd_check(args)
    return cmd_run(args)


if __name__ == "__main__":
    sys.exit(main())
