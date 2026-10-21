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

Order 017-i scope: OFFLINE ONLY. Round 017-j repaired the utility's
selection, privacy, ownership, and resource boundaries (issued-call
selection binding, closed metadata sets, lossless but byte-verified
synthetic result-text retention under selection schema v2, exact
serialized-byte selection cap, centralized per-run request budget,
bounded preflight output collection, permission-preserving protected
directories, readiness-record closure, and an absolute active-run
deadline that also covers owned descendants). Round 017-k repaired the
remaining four bounded defects exposed by independent review of 017-j:
(1) RUNTIME frame selection is now bound to the controller's ACTUAL
issued records (`FakeProvider._issued`) captured before each provider
request -- a preloaded/anticipated/forged call is never selected
before the controller issues it; the pure-facade candidate parsing
(declared-step inference) is a distinct mode used only by the offline
fixture controls; (2) finalization QUIESCES the owned provider before
final validation/publication -- freeze, stop accepting, close the
listening socket, join in-flight handlers under a bounded grace -- and
validates/serializes an explicit frozen frame snapshot, so no late
append can reach a published record; (3) EVERY request method and
error-dispatch path (unsupported methods, malformed request lines,
unsupported versions) consumes the per-run budget with fixed
sanitized errors, and accepted handler concurrency is bounded;
(4) readiness metadata round-trips the validated live-facts flag count
faithfully (no placeholder tuples), and malformed Unicode (e.g. lone
surrogates) is rejected with the fixed typed ``malformed_unicode``
reason before any encoding/hashing/retention, with the raw value
stored nowhere and no lossy replacement.

The actual-client launch path exists in code and is GATED, not
unreachable by construction: a caller that supplies an explicit opt-in,
a validated readiness record whose verdict is ``ready``, a validated
external strategic authorization record bound to the run, and an
unconsumed one-attempt ledger claim CAN launch a stand-in binary
through this public API. Such caller-supplied records are external
input; they are NOT proof that any real client's unverified startup
controls were verified or applied. This version's own static evaluation
(``evaluate_startup_readiness``) only ever emits ``not_ready`` -- the
plugin/catalog sync, update and telemetry controls remain unverified on
local static evidence, and unknown control means NOT READY, never
silent fetch. Ordinary offline runs use an injected wholly synthetic
child executable and an in-process owned fake provider; they NEVER
launch an installed client, call a model, or touch a provider.

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
- Selection is bound to the controller's ISSUED call records: the exact
  issued call ID (``call_NN`` for the step at 0-based position NN-1),
  the tool family/name, the declared step/command and expected argument
  values, and the controller-issued process ID (``proc_NN``) for
  results. At RUNTIME (the owned provider receiver) the issued set is
  the controller's actual ``_issued`` records created BEFORE that
  provider request: a preloaded, anticipated, or forged call is never
  selected before the controller issues it, and issuance/completion is
  never inferred from a caller's predicted ID or forged earlier status.
  The pure-facade candidate parsing (declared-step ID inference plus
  progression from the request's own completed outputs) is a distinct
  fixture mode used only by the offline pure controls; a constructor or
  manually populated state is not runtime provenance evidence.
  Unissued, orphaned, conflicting, mismatched, or wrong-mode items are
  rejected with a fixed reason and their raw values are never stored.
  Only predeclared harmless synthetic commands are ever emitted or
  selectable; arbitrary incoming command/code is never executed,
  selected, or echoed. The child never executes model-directed
  commands.
- Selected synthetic result TEXT is retained losslessly (selection
  schema v2) only after strict ownership, source/shape, and byte
  validation: at run time the exact received text of a selected read
  result must equal the bytes THIS RUN seeded into the owned workspace
  for the declared path (sleep steps: the exact empty payload), or the
  text is stripped (metadata + exact-byte digest retained) and a fixed
  ``content_unverified`` count is recorded. This is a narrow
  synthetic-fixture export permission, NOT permission to save full
  requests, user/system/developer messages, tool schemas, headers,
  histories, unknown child stdout/stderr, credentials, or unrelated
  tool output. Fake-child content stays labeled synthetic with
  ``fixture_authority: "none"``; no actual client format is earned.
- Malformed Unicode (e.g. a lone surrogate from a JSON ``\\ud800``
  escape) is validated before any encoding, hashing, or retention on
  the function/custom output/argument and metadata paths: the frame is
  rejected with the fixed typed ``malformed_unicode`` reason, the raw
  value is stored nowhere (not in exceptions, reprs, digests, or
  records), and no lossy replacement ever masquerades as fidelity.
  Valid non-ASCII Unicode is processed normally.
- The per-run selected-byte cap applies to the EXACT UTF-8 bytes of the
  canonical serialization that is published (metadata and serialization
  overhead included): serialize once, validate once, publish those same
  bytes; exceedance is a fixed typed failure with no oversized or
  partial artifact.
- Finalization QUIESCES the owned provider before any final validation
  or publication: the frame state is frozen (no further appends, ever),
  the accept loop stops, the listening socket closes, and in-flight
  handler work is joined under a bounded grace; validation and
  serialization then operate on the explicit frozen frame snapshot, so
  no late or in-flight append can reach a persisted record, console,
  repr, diagnostic, or error. Unsuccessful cleanup is reported
  honestly, never hidden.
- EVERY request method and error-dispatch path reaching the owned
  provider -- known routes, unsupported routes, unsupported HTTP
  methods, malformed request lines, unsupported versions, oversize
  bodies -- consumes the per-run request budget before any
  route/auth/body outcome branch (the centralized accounting also
  covers the BaseHTTPRequestHandler error-dispatch fallback, which the
  017-j do_GET/do_POST-only centralization missed); authentication
  failures remain value-free (counter only); error dispatch sends
  fixed sanitized bodies that never echo the request line or method;
  accepted handler concurrency is bounded (bounded, honestly reported
  teardown).
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
import select
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
SELECTION_SCHEMA = "slaif-real-client-capture-selection-v2"
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
HARD_MAX_CONCURRENT_HANDLERS = 4
HARD_HANDLER_JOIN_GRACE_SECONDS = 10.0

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
        "call_id_unissued",
        "metadata_unissued",
        "content_unverified",
        "malformed_unicode",
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


def _run_bounded(
    argv: list[str],
    cap: int,
    timeout: float = 15.0,
    overflow_class: str = "binary_probe_over_bound",
) -> tuple[bytes, bool]:
    """Run a read-only CLI probe with BOUNDED streaming collection.

    Output is drained in bounded chunks under a finite wall-clock
    deadline; exceeding the byte cap or the deadline kills the probe
    and fails closed with a fixed, non-echoing class. No unbounded
    buffer followed by truncation. Returns (bounded bytes, complete).
    """
    try:
        proc = subprocess.Popen(  # noqa: S603 - fixed argv, never a shell
            argv,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env={"PATH": CHILD_ENV_FIXED_PATH, "LC_ALL": "C.UTF-8"},
        )
    except OSError:
        raise CaptureError("binary_probe_failed") from None
    data = bytearray()
    overflow = False
    timed_out = False
    deadline = time.monotonic() + timeout
    try:
        stream = proc.stdout
        assert stream is not None
        fd = stream.fileno()
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                break
            try:
                ready, _, _ = select.select([fd], [], [], min(0.1, remaining))
            except OSError:
                break
            if not ready:
                continue
            try:
                chunk = os.read(fd, 65536)
            except OSError:
                break
            if not chunk:
                break
            data.extend(chunk)
            if len(data) > cap:
                overflow = True
                break
    finally:
        if overflow or timed_out:
            try:
                proc.kill()
            except OSError:
                pass
        try:
            proc.stdout.close()
        except (OSError, AttributeError):
            pass
    try:
        proc.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            pass
    if timed_out:
        raise CaptureError("binary_probe_timeout")
    if overflow:
        raise CaptureError(overflow_class)
    if proc.returncode != 0:
        raise CaptureError("binary_probe_failed")
    return bytes(data), len(data) <= cap


def _detect_flags(help_text: str) -> tuple[str, ...]:
    found: list[str] = []
    for flag in sorted(DECLARED_FLAG_SET):
        pattern = r"(?<![A-Za-z0-9-])" + re.escape(flag) + r"(?![A-Za-z0-9-])"
        if re.search(pattern, help_text):
            found.append(flag)
    return tuple(found)


def preflight_binary(
    binary: Path, expected_version: str, expected_sha256: str, probe_timeout: float = 15.0
) -> BinaryFacts:
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
    version_data, _ = _run_bounded(
        [str(binary), "--version"],
        HARD_MAX_VERSION_BYTES,
        probe_timeout,
        overflow_class="binary_version_over_bound",
    )
    version_line = version_data.decode("utf-8", "replace").splitlines()
    version = version_line[0].strip() if version_line else ""
    # Expected form: "<tool> <version>" (e.g. "codex-cli 0.162.1").
    parts = version.split()
    observed_version = parts[-1] if len(parts) >= 2 else version
    if not VERSION_RE.fullmatch(observed_version) or observed_version != expected_version:
        raise CaptureError("binary_version_mismatch")
    help_data, complete = _run_bounded(
        [str(binary), "exec", "--help"],
        HARD_MAX_HELP_BYTES,
        probe_timeout,
        overflow_class="binary_help_over_bound",
    )
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


READINESS_RECORD_MAX_BYTES = 16 * 1024


def load_readiness_record(path: Path, facts: BinaryFacts) -> ReadinessFacts:
    """Validate a previously written readiness record (metadata only).

    Closed validation: exact key set, closed verdict/reason enums, exact
    binding to the live preflight facts (version, sha256, flag count),
    the fixed startup-control candidate table, and protected metadata
    read rules (regular non-symlink file, current owner, mode 0600,
    bounded size). Any deviation fails closed with a sanitized class;
    no record value ever reaches an exception, repr, or diagnostic.
    A ``ready`` verdict in a record is caller-supplied external input
    that can unlock the gated launch path; it is not evidence that the
    real client's unverified startup controls were verified or applied.
    """
    try:
        st = path.lstat()
    except OSError:
        raise CaptureError("readiness_record_invalid") from None
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
        raise CaptureError("readiness_record_invalid")
    if st.st_uid != os.getuid():
        raise CaptureError("readiness_record_not_owned")
    if st.st_mode & 0o077:
        raise CaptureError("readiness_record_unsafe_mode")
    if st.st_size > READINESS_RECORD_MAX_BYTES:
        raise CaptureError("readiness_record_over_bound")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError):
        raise CaptureError("readiness_record_invalid") from None
    if not isinstance(data, dict):
        raise CaptureError("readiness_record_invalid")
    expected_keys = {
        "schema",
        "verdict",
        "reasons",
        "binary_version",
        "binary_sha256",
        "detected_flag_count",
        "control_candidates",
    }
    if set(data) != expected_keys or data.get("schema") != READINESS_SCHEMA:
        raise CaptureError("readiness_record_invalid")
    verdict = data.get("verdict")
    if verdict not in {"ready", "not_ready"}:
        raise CaptureError("readiness_record_invalid")
    reasons = data.get("reasons")
    if (
        not isinstance(reasons, list)
        or len(reasons) > len(READINESS_REASONS)
        or not all(isinstance(r, str) for r in reasons)
        or not set(reasons) <= READINESS_REASONS
    ):
        raise CaptureError("readiness_record_invalid")
    if data.get("binary_sha256") != facts.sha256:
        raise CaptureError("readiness_record_binding_mismatch")
    if data.get("binary_version") != facts.version:
        raise CaptureError("readiness_record_binding_mismatch")
    count = data.get("detected_flag_count")
    if (
        isinstance(count, bool)
        or not isinstance(count, int)
        or count < 0
        or count > len(DECLARED_FLAG_SET)
    ):
        raise CaptureError("readiness_record_invalid")
    if count != len(facts.detected_flags):
        raise CaptureError("readiness_record_binding_mismatch")
    candidates = data.get("control_candidates")
    if (
        not isinstance(candidates, list)
        or len(candidates) != len(STARTUP_CONTROL_CANDIDATES)
        or any(
            not isinstance(c, dict)
            or set(c) != {"name", "status"}
            or c.get("name") != name
            or c.get("status") != status
            for c, (name, status) in zip(candidates, STARTUP_CONTROL_CANDIDATES, strict=True)
        )
    ):
        raise CaptureError("readiness_record_invalid")
    # The record carries the flag COUNT only (metadata law); the live
    # preflight facts own the in-memory flag set, and the validated
    # binding ``count == len(facts.detected_flags)`` above means the
    # reconstructed facts reproduce the record's count exactly
    # (zero and every nonzero case) with no placeholder semantics and
    # no flag-text export: ``to_record()`` serializes the count again.
    return ReadinessFacts(
        verdict=verdict,
        reasons=tuple(reasons),
        binary_version=str(data["binary_version"]),
        binary_sha256=str(data["binary_sha256"]),
        detected_flags=facts.detected_flags,
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
    """Require/create a private owned directory (never follows links).

    Pre-existing directories are accepted only when they are owned by
    the current user and NOT group- or world-writable; they are never
    chmoded, so a shared or foreign directory is rejected without
    mutation (its mode and contents are preserved). Permission bits are
    set only on directories THIS run creates.
    """
    if path.is_symlink():
        raise CaptureError("protected_dir_invalid")
    if path.exists():
        if not path.is_dir():
            raise CaptureError("protected_dir_invalid")
        st = path.lstat()
        if st.st_uid != os.getuid():
            raise CaptureError("protected_dir_not_owned")
        if st.st_mode & 0o022:
            raise CaptureError("protected_dir_unsafe_preexisting")
        return
    parent = path.parent
    if not parent.is_dir() or parent.is_symlink():
        raise CaptureError("protected_dir_parent_invalid")
    pst = parent.lstat()
    if pst.st_mode & 0o002:
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
        # 017-k finalization: the frame state is frozen when the owned
        # provider is quiesced; no append may happen after the freeze
        # gate is set (rechecked under this lock at the append site).
        self.frozen = False
        self.post_freeze_rejected = 0
        self.rejected_connections = 0
        self.teardown_incomplete = False

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


class _OwnedThreadingHTTPServer(ThreadingHTTPServer):
    """ThreadingHTTPServer with bounded, tracked handler work.

    Accepted connections beyond the hard handler cap are closed
    without a response and counted (the per-REQUEST budget is a
    separate law; a connection that never sends a request line
    consumes no request budget). Handler threads are tracked so the
    owner can join them under a bounded grace at quiesce time, and
    handler exceptions are counted, never printed (no traceback may
    echo raw content to the console).
    """

    daemon_threads = True

    def __init__(
        self,
        server_address: tuple[str, int],
        RequestHandlerClass: type,  # noqa: N803 - http.server API
        *,
        state: ProviderState,
    ) -> None:
        super().__init__(server_address, RequestHandlerClass)
        self.state = state
        self._handler_count = 0
        self._handler_lock = threading.Lock()

    def handle_error(self, request: Any, client_address: Any) -> None:  # noqa: N802
        # Count only: the stdlib prints the traceback, which is a
        # console-echo path the privacy law forbids.
        try:
            self.state.malformed_count += 1
        except Exception:  # noqa: BLE001
            pass

    def process_request(self, request: Any, client_address: Any) -> None:  # noqa: N802
        with self._handler_lock:
            if self._handler_count >= HARD_MAX_CONCURRENT_HANDLERS:
                self.state.rejected_connections += 1
                try:
                    request.close()
                except OSError:
                    pass
                return
            self._handler_count += 1
        thread = threading.Thread(
            target=self._tracked_request, args=(request, client_address), daemon=True
        )
        thread.start()

    def _tracked_request(self, request: Any, client_address: Any) -> None:
        try:
            self.process_request_thread(request, client_address)
        finally:
            with self._handler_lock:
                self._handler_count -= 1

    def active_handlers(self) -> int:
        with self._handler_lock:
            return self._handler_count


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
        self._server: _OwnedThreadingHTTPServer | None = None
        self._port = 0
        self._thread: threading.Thread | None = None

    # -- lifecycle ---------------------------------------------------------
    def start(self) -> int:
        outer = self

        class Handler(_SilentRequestHandler):
            provider = outer

        self._server = _OwnedThreadingHTTPServer(("127.0.0.1", 0), Handler, state=self.state)
        self._port = self._server.server_address[1]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self._port

    def stop(self) -> None:
        """Quiesce the owned provider and freeze the frame state.

        Order: freeze first (the append path rechecks the gate under
        the state lock, so NO further frame append can happen from
        this point on), stop the accept loop, close the listening
        socket, then join in-flight handler work under a bounded
        grace. A handler that outlives the grace is reported honestly
        (``teardown_incomplete``) and can still never reach the
        frozen snapshot or a published record. Idempotent.
        """
        st = self.state
        with st.lock:
            st.frozen = True
        server = self._server
        self._server = None
        if server is not None:
            try:
                server.shutdown()
            except Exception:  # noqa: BLE001 - quiesce must never raise
                pass
            try:
                server.server_close()
            except Exception:  # noqa: BLE001
                pass
        if self._thread is not None:
            self._thread.join(timeout=HARD_CHILD_IO_TIMEOUT_SECONDS)
            self._thread = None
        if server is not None:
            deadline = time.monotonic() + HARD_HANDLER_JOIN_GRACE_SECONDS
            while server.active_handlers() > 0 and time.monotonic() < deadline:
                time.sleep(0.01)
            if server.active_handlers() > 0:
                st.teardown_incomplete = True

    def frame_snapshot(self) -> list[dict[str, Any]]:
        """A list copy of the frame state under the state lock.

        After :meth:`stop` (frozen + handler join) no further append
        can happen, so the snapshot taken then is the FINAL frame
        state; validation and serialization operate on it, never on
        the live list, so serialization cannot pick up a later
        unverified append.
        """
        with self.state.lock:
            return list(self.state.frames)

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
            if st.frozen:
                # Quiesced provider: no extraction, no append, no
                # response-script advance; fixed sanitized rejection.
                st.post_freeze_rejected += 1
                return 503, b"service unavailable\n"
            st.responses_count += 1
            st.ingress_bytes_total += min(len(body), st.limits.max_inbound_bytes)
            if st.responses_count > st.limits.max_requests:
                st.request_limit_hit = True
                return 429, b"rate limited\n"
            # Runtime provenance: only the controller's ACTUAL issued
            # records created before this request may prove issuance.
            issued_snapshot = tuple(self._issued)
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
            issued=issued_snapshot,
        )
        with st.lock:
            if st.frozen:
                # Frozen while this request was being parsed: the
                # frames are discarded, never appended or published.
                st.post_freeze_rejected += 1
                return 503, b"service unavailable\n"
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

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        """Fixed sanitized error dispatch for EVERY error path.

        BaseHTTPRequestHandler funnels unsupported methods, malformed
        request lines, overlong lines, and unsupported versions
        through ``send_error``; its default body echoes the request
        line or method name. This override (a) consumes the per-run
        request budget here exactly once, so error-dispatch paths
        cannot evade the cap, and (b) sends a fixed sanitized body
        with no message/explain echo.
        """
        try:
            if self._count_request():
                return
            self._send(int(code), b"error\n", "text/plain")
        except (OSError, ValueError, AttributeError):
            self.close_connection = True

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
    def _count_request(self) -> bool:
        """Centralized per-run request accounting.

        EVERY request that reaches a handler consumes the per-run
        budget BEFORE any route, auth, body, or error outcome branch, so
        unsupported and malformed fixture requests cannot evade the
        cap. Authentication failures stay value-free (counter only).
        Returns True when the cap is already hit (a sanitized 429 was
        sent; the handler must stop).
        """
        st = self.provider.state
        with st.lock:
            st.request_count += 1
            over = st.request_count > st.limits.max_requests
            if over:
                st.request_limit_hit = True
        if over:
            st.count_status(429)
            self._send(429, b"rate limited\n", "text/plain")
        return over

    def do_GET(self) -> None:  # noqa: N802 - http.server API
        st = self.provider.state
        if self._count_request():
            return
        if not self._headers_ok():
            st.count_status(400)
            self._send(400, b"bad request\n", "text/plain")
            return
        if not self._auth_ok():
            st.count_status(401)
            self._send(401, b"unauthorized\n", "text/plain")
            return
        if self.path != "/v1/models":
            st.count_status(404)
            self._send(404, b"not found\n", "text/plain")
            return
        body = json.dumps(
            {"object": "list", "data": [{"id": st.model, "object": "model"}]},
            separators=(",", ":"),
        ).encode("utf-8")
        st.count_status(200)
        self._send(200, body, "application/json")

    def do_POST(self) -> None:  # noqa: N802 - http.server API
        st = self.provider.state
        if self._count_request():
            return
        if not self._headers_ok():
            st.count_status(400)
            self._send(400, b"bad request\n", "text/plain")
            return
        if not self._auth_ok():
            st.count_status(401)
            self._send(401, b"unauthorized\n", "text/plain")
            return
        if self.path != "/v1/responses":
            # Unsupported route: bounded work, no body read, close.
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


def _strict_utf8(value: str) -> bytes | None:
    """Strict UTF-8 encoding, or None for malformed Unicode.

    A Python ``str`` carrying a lone surrogate (e.g. from a JSON
    ``\\ud800`` escape) is malformed Unicode: it can never be a
    faithful byte value. Callers must check this BEFORE any
    encoding, hashing, or retention; the raw value is then rejected
    with the fixed typed reason and stored nowhere. Never raises,
    never echoes.
    """
    try:
        return value.encode("utf-8")
    except UnicodeEncodeError:
        return None


def _arguments_carry_malformed_unicode(arguments: Any) -> bool:
    """True when the declared-command arguments JSON carries a
    malformed-Unicode (non-strict) string value. Valid Unicode (e.g.
    ``\\u00e9``) is NOT malformed; it simply fails the declared-
    command match like any other text."""
    if not isinstance(arguments, str) or len(arguments) > HARD_MAX_STEP_BYTES * 4:
        return False
    try:
        parsed = json.loads(arguments)
    except (ValueError, RecursionError):
        return False
    if not isinstance(parsed, dict):
        return False
    return any(isinstance(value, str) and _strict_utf8(value) is None for value in parsed.values())


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
        # selection-v2: exact received result text, retained only for
        # proven selected synthetic frames (see module docstring law);
        # None until byte-verified at run time, never reconstructed.
        "content": None,
        "content_bytes": None,
        "content_verified": None,
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


def _issued_call_id(step_pos: int) -> str:
    """The controller's exact issued call ID for the step at 0-based
    position ``step_pos`` (the step machine issues one new call per
    response, in step order)."""
    return f"call_{step_pos + 1:02d}"


def _issued_process_id(step_pos: int) -> str:
    """The controller-issued process ID a result for the step at
    ``step_pos`` must carry (or omit)."""
    return f"proc_{step_pos + 1:02d}"


def _issued_custom_input(step_pos: int) -> str:
    """The controller-issued custom-tool input value for the step at
    ``step_pos`` (expected argument value of an issued custom call)."""
    return f"synthetic-custom-input-{step_pos + 1:02d}"


def _parse_output_structured(output: Any) -> Any:
    """Structured output payload as a dict, or None (never raises)."""
    if isinstance(output, str):
        try:
            parsed = json.loads(output)
        except (ValueError, RecursionError):
            return None
        return parsed if isinstance(parsed, dict) else None
    if isinstance(output, dict):
        return output
    return None


def _declared_command_match(arguments: Any, steps: tuple[DeclaredStep, ...]) -> int | None:
    """Position of the declared step whose exact command this
    ``arguments`` string names (any declared step), or None."""
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
    for pos, step in enumerate(steps):
        if cmd == step.cmd_text() and workdir == step.workdir:
            return pos
    return None


def extract_frames(
    payload: Any,
    *,
    declared_steps: tuple[DeclaredStep, ...],
    canary: str,
    request_seq: int,
    mode: str,
    issued: tuple[tuple[str, int], ...] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int], frozenset[str]]:
    """Extract PROVEN selected frames from ONE parsed request payload.

    Two distinct modes, never conflated:

    - RUNTIME provenance (``issued`` given): the owned provider
      receiver passes the controller's ACTUAL issued records
      (``FakeProvider._issued``) captured BEFORE this provider
      request. Only those (call ID, step position) pairs prove
      issuance; a preloaded, anticipated, or forged call is never
      selected before the controller issues it, and issuance/
      completion is never inferred from a caller's predicted ID or
      forged earlier status (the controller's own gating already
      encoded causal progression when it issued each record).
    - PURE candidate/fixture parsing (``issued`` is None): declared-
      step ID inference plus progression from this request's own
      completed outputs. This is the offline pure-facade mode used by
      the fixture controls; it is NOT runtime provenance evidence.

    In both modes the tool family/name, the declared step/command and
    expected argument values, and the controller-issued process ID for
    results are enforced, malformed Unicode is rejected with the fixed
    typed reason before any encoding/hashing/retention, and unissued,
    orphaned, conflicting, mismatched, or wrong-mode items are
    rejected with a fixed reason; raw values are never stored. The
    input payload is never mutated.
    """
    frames: list[dict[str, Any]] = []
    rejections: dict[str, int] = {}
    items, unknown_types = _iter_items(payload)
    seq = 0

    def reject(reason: str) -> None:
        rejections[reason] = rejections.get(reason, 0) + 1

    # Issuence proof. Runtime mode binds to the controller's actual
    # records created before this request; pure-facade mode infers the
    # declared-step IDs (fixture controls only).
    if issued is None:
        issued_positions = {_issued_call_id(pos): pos for pos in range(len(declared_steps))}
        use_completion_inference = True
    else:
        issued_positions = {call_id: pos for call_id, pos in issued}
        use_completion_inference = False
    declared_names = {s.tool_name for s in declared_steps}
    # The item family must match the mode of the actually OFFERED tool
    # schema; a wrong-family item is a typed unsupported shape.
    if mode == "responses-function-tool":
        allowed_item_types = {"function_call", "function_call_output"}
    else:
        allowed_item_types = {"custom_tool_call", "custom_tool_call_output"}
    # Controller advancement evidence (PURE-facade mode only): a step
    # position counts as completed in this request's input only when a
    # structurally valid completed output for its issued ID with
    # controller-issued metadata is present. An unissued process ID,
    # or any session/chunk ID, is unearned metadata and never unlocks
    # a later step's call. Runtime mode does NOT infer progression
    # from inbound status; the issued registry is the evidence.
    completed: set[int] = set()
    if use_completion_inference:
        for entry in items:
            if entry.get("type") not in {"function_call_output", "custom_tool_call_output"}:
                continue
            cid = _bounded_str(entry.get("call_id"), HARD_MAX_CALL_ID_BYTES)
            if cid is None or cid not in issued_positions:
                continue
            pos = issued_positions[cid]
            structured = _parse_output_structured(entry.get("output"))
            if not isinstance(structured, dict) or structured.get("status") != "completed":
                continue
            process_id = structured.get("process_id")
            if process_id is not None and process_id != _issued_process_id(pos):
                continue
            if "session_id" in structured or "chunk_id" in structured:
                continue
            completed.add(pos)
    # Canary membership bytes: a malformed-Unicode canary is a
    # meaningless marker; it is treated as absent (never crashes,
    # never echoed).
    canary_bytes = _strict_utf8(canary)
    if canary_bytes is None:
        canary_bytes = b""

    for entry in items:
        item_type = entry.get("type")
        if item_type not in allowed_item_types:
            # Wrong family under the offered tool schema (or a
            # non-selectable shape): typed, counted, never stored.
            if isinstance(item_type, str) and item_type in ITEM_TYPES:
                reject("input_shape_unsupported")
            continue
        call_id = _bounded_str(entry.get("call_id"), HARD_MAX_CALL_ID_BYTES)
        if call_id is None or not CALL_ID_RE.fullmatch(call_id):
            reject("call_id_invalid")
            continue
        pos = issued_positions.get(call_id)
        seq += 1
        frame = _frame_base(seq, request_seq, item_type, call_id)

        if item_type in {"function_call", "custom_tool_call"}:
            name = _bounded_str(entry.get("name"), HARD_MAX_NAME_BYTES)
            if name is None or name not in declared_names:
                reject("name_not_declared")
                continue
            frame["name"] = name
            # Declared-command check first (fixed taxonomy: an
            # undeclared command is command_not_declared regardless of
            # the ID); malformed Unicode inside the arguments is the
            # distinct typed malformed_unicode reason.
            if item_type == "function_call":
                if _arguments_carry_malformed_unicode(entry.get("arguments")):
                    reject("malformed_unicode")
                    continue
                matched = _declared_command_match(entry.get("arguments"), declared_steps)
                if matched is None:
                    reject("command_not_declared")
                    continue
            else:
                matched = None
            if pos is None:
                # Syntactically valid ID the controller never issued.
                reject("call_id_unissued")
                continue
            step = declared_steps[pos]
            if name != step.tool_name:
                # The ID belongs to a different step than the name.
                reject("call_id_unissued")
                continue
            if item_type == "function_call":
                if matched != pos:
                    # Declared command of a DIFFERENT step than the
                    # issued ID names: conflicting, never proven.
                    reject("call_id_unissued")
                    continue
            else:
                tool_input = entry.get("input")
                if not isinstance(tool_input, str) or not tool_input:
                    reject("input_shape_unsupported")
                    continue
                input_bytes = _strict_utf8(tool_input)
                if input_bytes is None:
                    reject("malformed_unicode")
                    continue
                if len(input_bytes) > HARD_MAX_METADATA_BYTES * 4:
                    reject("metadata_value_over_bound")
                    continue
                if canary in tool_input:
                    reject("credential_marker_present")
                    continue
                if tool_input != _issued_custom_input(pos):
                    # Not the exact expected argument value the
                    # controller issued for this call ID.
                    reject("call_id_unissued")
                    continue
                frame["input_digest"] = _digest_bytes(input_bytes)
                frame["input_bytes"] = len(input_bytes)
            # Pure-facade progression only: every earlier step must
            # have a completed output in this request's input, or this
            # call was never issued at this point. Runtime mode: the
            # issued registry is the progression proof.
            if use_completion_inference and any(j not in completed for j in range(pos)):
                reject("call_id_unissued")
                continue
            frame["declared_command_index"] = pos
            frames.append(frame)
        else:
            # Output frames: the call ID must be an issued ID (an
            # orphan result naming an unissued call is rejected and its
            # raw value is never stored).
            if pos is None:
                reject("call_id_unissued")
                continue
            output = entry.get("output")
            if isinstance(output, str) and _strict_utf8(output) is None:
                # Malformed Unicode in the raw output text: typed,
                # counted, never encoded, hashed, or stored.
                reject("malformed_unicode")
                continue
            payload_bytes = _output_payload_bytes(output)
            if payload_bytes is None:
                reject("output_shape_unsupported")
                continue
            if canary_bytes in payload_bytes:
                reject("credential_marker_present")
                continue
            frame["output_digest"] = _digest_bytes(payload_bytes)
            frame["output_bytes"] = len(payload_bytes)
            structured: Any = _parse_output_structured(output)
            if structured is None:
                # Plain-string (non-JSON) output: the exact received
                # text IS the controlled synthetic result payload for a
                # proven selected frame; digest stays on the raw bytes
                # and no completion metadata is invented.
                if isinstance(output, str):
                    frame["content"] = output
                    frame["content_bytes"] = len(payload_bytes)
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
                value = structured.get(key)
                if value is None:
                    continue
                if key == "process_id":
                    v = _bounded_str(value, HARD_MAX_METADATA_BYTES)
                    if v is None:
                        reject("metadata_value_over_bound")
                        bad = True
                        break
                    if v != _issued_process_id(pos):
                        # Not the controller-issued process ID for this
                        # call: unearned metadata, rejected, never
                        # stored.
                        reject("metadata_unissued")
                        bad = True
                        break
                    frame["process_id"] = v
                else:
                    # session_id/chunk_id are not controller-issued
                    # values; any presence is typed and rejected.
                    reject("metadata_unissued")
                    bad = True
                    break
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
            if "content" in structured:
                content = structured.get("content")
                if not isinstance(content, str):
                    # Unknown/unearned result shape: typed, metadata
                    # only, never stored.
                    reject("output_shape_unsupported")
                    continue
                content_bytes = _strict_utf8(content)
                if content_bytes is None:
                    # Malformed Unicode result text: typed, counted,
                    # never encoded, hashed, or retained.
                    reject("malformed_unicode")
                    continue
                if len(content_bytes) > HARD_MAX_INBOUND_BYTES:
                    reject("metadata_value_over_bound")
                    continue
                # Lossless retention of the exact received text for a
                # proven selected synthetic frame (selection-v2); the
                # run-time byte verification against the owned seeded
                # workspace happens in _verify_selected_content.
                frame["content"] = content
                frame["content_bytes"] = len(content_bytes)
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
    frames: list[dict[str, Any]] | None = None,
    steps: tuple[DeclaredStep, ...],
    deadline_seconds: float,
    elapsed_seconds: float,
    child_kind: str,
    client_version: str | None,
    client_sha256: str | None,
) -> dict[str, Any]:
    # ``frames`` is the FROZEN snapshot (see run_capture): serialization
    # cannot pick up a later unverified append. The runtime finalization
    # path (run_capture) ALWAYS passes the explicit frozen snapshot; the
    # omitted-frames form is the pure-facade fixture control, where the
    # caller owns the static frame state (no live receiver exists, so
    # there is no late-append surface).
    if frames is None:
        frames = list(state.frames)
    frames = sorted(frames, key=lambda f: (f["request_seq"], f["seq"]))
    provenance = "synthetic-offline" if child_kind == "synthetic" else "actual-capture"
    record: dict[str, Any] = {
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
                else _digest_bytes(
                    b"\n".join(
                        t.encode("utf-8")
                        for t in sorted(state.unsupported_item_types)
                        if _strict_utf8(t) is not None
                    )
                )
            ),
        },
        # Exact UTF-8 byte length of the canonical serialization of THIS
        # record (metadata and serialization overhead included); see
        # serialize_selection. It is the unit the per-run selected-byte
        # cap is enforced on.
        "selected_bytes_total": 0,
    }
    record["selected_bytes_total"] = _selection_self_size(record)
    return record


def _selection_bytes(record: dict[str, Any]) -> bytes:
    """Canonical serialization: indent=1, sorted keys, trailing newline."""
    return (json.dumps(record, indent=1, sort_keys=True) + "\n").encode("utf-8")


def _selection_self_size(record: dict[str, Any]) -> int:
    """Self-consistent serialized size of the record.

    The record embeds its own serialized byte length, so the value is
    the fixed point ``v == size(record with selected_bytes_total=v)``.
    The iteration converges because the size only depends on the field's
    decimal width.
    """
    value = 0
    for _ in range(16):
        record["selected_bytes_total"] = value
        size = len(_selection_bytes(record))
        if size == value:
            return size
        value = size
    raise CaptureError("selection_size_unstable")


def serialize_selection(record: dict[str, Any]) -> bytes:
    """The exact bytes a run publishes as ``selection.json``.

    Serialize once, validate once, publish those same bytes: the
    returned length equals ``record["selected_bytes_total"]``, and the
    per-run selected-byte cap is enforced on this length.
    """
    data = _selection_bytes(record)
    if record.get("selected_bytes_total") != len(data):
        raise CaptureError("selection_size_unstable")
    return data


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
    # Bounded, honest report of the teardown window: wall-clock seconds
    # from leader exit until the owned group was verified gone.
    teardown_seconds: float | None = None


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
    leader_exited_at = time.monotonic()
    # Absolute active-run deadline across owned descendants: a normal
    # leader exit never disables the deadline. Never wait past the
    # deadline for inherited pipe drains.
    remaining = deadline - time.monotonic()
    out_thread.join(timeout=max(0.0, remaining))
    err_thread.join(timeout=max(0.0, remaining))
    if time.monotonic() >= deadline:
        # The deadline arrived while owned descendants (e.g. pipe
        # holders) may still run: terminate/reap the owned group NOW,
        # then finish draining with a bounded teardown grace only.
        _reap_group_members(pgid, grace_seconds=TEARDOWN_GRACE_SECONDS)
        out_thread.join(timeout=TEARDOWN_GRACE_SECONDS)
        err_thread.join(timeout=TEARDOWN_GRACE_SECONDS)
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
    return ChildFacts(
        returncode=proc.returncode,
        stdout_bytes=stdout_bytes,
        stderr_bytes=stderr_bytes,
        timed_out=timed_out,
        output_cap_exceeded=cap,
        group_cleanup_verified=group_gone,
        teardown_seconds=round(time.monotonic() - leader_exited_at, 3),
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
TEARDOWN_GRACE_SECONDS = 2.0
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
            "frozen": state.frozen,
            "post_freeze_rejected": state.post_freeze_rejected,
            "rejected_connections": state.rejected_connections,
            "teardown_incomplete": state.teardown_incomplete,
        }


def _verify_selected_content(
    frames: list[dict[str, Any]],
    state: ProviderState,
    steps: tuple[DeclaredStep, ...],
    workspace: Path,
) -> None:
    """Byte-validate selected result text against the owned workspace.

    ``frames`` is the FROZEN snapshot taken after the owned provider
    was quiesced (frozen + handler join), so no later append can reach
    this validation or the published record. Only text that EXACTLY
    equals the bytes this run seeded into the owned workspace for the
    declared read path (or the exact empty payload of a sleep step) is
    retained as controlled synthetic content. Anything else is
    stripped (metadata + exact-byte digest retained) and counted with
    the fixed content_unverified reason. Nothing is ever
    reconstructed from hashes, constants, or guessed metadata.
    """
    issued = {_issued_call_id(pos): pos for pos in range(len(steps))}
    for frame in frames:
        if frame["item_type"] not in {"function_call_output", "custom_tool_call_output"}:
            frame["content_verified"] = None
            continue
        content = frame.get("content")
        if content is None:
            frame["content_verified"] = None
            continue
        pos = issued.get(frame["call_id"])
        if pos is None:
            state.reject_frame("content_unverified")
            frame["content"] = None
            frame["content_bytes"] = None
            frame["content_verified"] = False
            continue
        step = steps[pos]
        try:
            seeded = (workspace / step.path).read_bytes() if step.kind == "read" else b""
        except OSError:
            seeded = None
        # Defense in depth: retained content is already strict-UTF-8
        # from extraction; a None encode can never verify.
        content_bytes = _strict_utf8(content)
        if seeded is not None and content_bytes is not None and content_bytes == seeded:
            frame["content_verified"] = True
        else:
            state.reject_frame("content_unverified")
            frame["content"] = None
            frame["content_bytes"] = None
            frame["content_verified"] = False


def _select_outcome(
    state: ProviderState,
    child: ChildFacts,
) -> tuple[str, bool]:
    """Return (outcome, build_selection). The selected-byte cap is
    enforced separately on the EXACT serialized selection bytes (see
    serialize_selection), never on a different accounting."""
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
        # QUIESCE the owned provider BEFORE any final validation or
        # publication: freeze the frame state (no further appends,
        # ever), stop accepting, close the listening socket, join
        # in-flight handler work under a bounded grace. The child has
        # fully exited, so no drain grace is needed; the bounded
        # handler join inside stop() covers any straggler.
        provider.stop()
        state = provider.state
        # Explicit FROZEN snapshot: validation and serialization
        # operate on it, never on the live list, so no late or
        # in-flight append can reach a published record.
        frame_snapshot = provider.frame_snapshot()
        # Byte-verify selected result text against the owned seeded
        # workspace in the frozen snapshot BEFORE any selection is
        # serialized or published.
        _verify_selected_content(frame_snapshot, state, declared_steps, scratch.workspace)
        provider_summary = _provider_summary(state)
        outcome, write_selection = _select_outcome(state, child_facts)
        total_selected = 0
        selection_data: bytes | None = None
        if write_selection:
            selection_record = build_selection(
                run_id=run_id,
                state=state,
                frames=frame_snapshot,
                steps=declared_steps,
                deadline_seconds=eff_limits.deadline_seconds,
                elapsed_seconds=time.monotonic() - started,
                child_kind=child_kind,
                client_version=client_version,
                client_sha256=client_sha256,
            )
            # Serialize ONCE; the cap applies to the EXACT UTF-8 bytes
            # that will be published (metadata and serialization
            # overhead included); publish those same bytes.
            selection_data = serialize_selection(selection_record)
            total_selected = len(selection_data)
            if total_selected > eff_limits.max_selected_bytes:
                outcome = "selected_over_bound"
                write_selection = False
                selection_record = None
                selection_data = None
                total_selected = 0
        if write_selection and selection_data is not None:
            selection_path = out_dir / "selection.json"
            _write_atomic_0600(selection_path, selection_data)
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
                "teardown_seconds": child_facts.teardown_seconds,
                "env_facts": child_env_facts,
            },
            "selection": {
                "frame_count": len(frame_snapshot),
                "transition_count": len(build_transitions(frame_snapshot)),
                # Exact UTF-8 bytes of the published selection.json
                # record (metadata and serialization overhead included);
                # 0 when no selection was published.
                "selected_bytes_total": total_selected,
                "rejected_counts": dict(state.rejection_counts),
                "written": write_selection and selection_data is not None,
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
