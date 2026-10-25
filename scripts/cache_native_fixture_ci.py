#!/usr/bin/env python3
"""Disposable-CI serial right-pane native fixture runner (017-r).

Runs ONLY on a disposable GitHub-hosted runner (never the protected
development/Qwen host; the entry refuses any context that is not
both ``GITHUB_ACTIONS=true`` and ``RUNNER_ENVIRONMENT=github-hosted``).
Fetches the pinned public Codex 0.164.0 musl archive (size and SHA256
verified BEFORE bounded extraction of the single expected regular
executable; symlink/hardlink/path-escape/oversize are fixed
failures), builds the digest-pinned fixture image (controller/exporter
UID 21001, native-subject UID 21002, immutable source/executable/
license files, no host mounts), and drives ten fresh-container
scenarios under the explicit confinement:

- ``--network none`` (private net namespace, own loopback only);
- read-only root filesystem with ONLY the reconciled bounded
  writable-data surface: the owned tmpfs roots (explicit uid/gid/
  mode budgets, 192 MiB total cap) plus the daemon's /dev/shm
  explicitly bounded to 64 MiB (256 MiB reconciled total);
- dedicated nonroot UID/GID, all capabilities dropped,
  ``no-new-privileges``;
- the EXPLICIT builtin seccomp policy;
- bounded memory (no swap: ``--memory == --memory-swap``), PID 96,
  CPU 1 limits;
- ``--log-driver none`` verified through the actual inspection
  value (no ``docker logs`` anywhere in R).

Ownership/lifecycle law: each scenario uses a FRESH container name
plus an ownership label, created with ``docker create`` so the
actual returned CID (bare 64-hex) is validated and registered as
owned BEFORE any start; a pre-existing name collision is a fixed
failure (never adopted, never removed).  Cleanup removes only
registered owned IDs and verifies absence through a successful
bounded authority query (verified absence vs query failure are
distinct states, never conflated).

Scenarios (the model's REQUIRED_SCENARIOS is the single source of
truth): controller-measurement (actual inspect of the full declared
confinement on the exact CID plus the default no-tools diagnostic
exercised on the live wire), exec-21002-measurement, pty-attach
(a REAL host-side owned PTY seam: the docker exec -it child gets an
allocated terminal so the promised attachment is actual, not just an
argv flag; fresh synthetic CODEX_HOME + separate early-beta profile
file, closed-schema validated), synthetic-success (controller-owned
issuance, exact-results, then quiesce -> 21001 export while the
container still exists -> host independent closed-object
validation -> exact CID/descendant teardown verified -> only THEN
0700/0600 publication), synthetic-fail, synthetic-hang (pre-hang record,
positive-before token scan, exact-owned pidfd stopper exec,
negative-after, unrelated parent sentinel survives),
synthetic-output-cap (bounded capture cap hit, record flushed
first), export-fail (corrupted declared frame refused closed),
quiesce-fail (no closed record ever produced) and controller-crash.

Accounting: ONE host ledger is wrapped around the guarded executor
from the start of the run (every host command passes the closed
allowlist, the shared deadline AND the finite admission/output
bounds; refused argv is counted, never executed).  Per-container
provider request/attempt facts are measured by the stand-in closed
records and charged into the SAME ledger before the next scenario is
admitted; retained capture bytes and all drained/emitted bytes are
distinct measured quantities.  The unrelated parent sentinel's
survival is measured (never overwritten) before its intentional
reap, and every owned resource (image, containers, sentinel,
listener) is registered BEFORE its lifecycle mutation so every
failure path converges through the same bounded exact-owned cleanup.
The published 0600 evidence is atomically retained at an explicit
protected destination OUTSIDE the disposable work root before that
root is destroyed.

Deadline law: ONE shared host monotonic anchor is created at the
START of the run and passed as ``SLAIF_FIXTURE_DEADLINE_ABS`` to
every scenario; the host-side fetch, build, queries, scenario and
cleanup steps consume the SAME remaining budget before every
blocking operation (only a single explicit bounded cleanup grace is
ever added), so no phase — host or in-container — resets the total.
Output discipline: every host invocation is argv-based (no shell)
against the CLOSED command allowlist (exact docker operation
grammar, exact fixture python/script/probe entry points, reviewed
runtime --version), its output captured BOUNDED with exact owned
process-group cleanup (the reviewed P pipe/reader design), and only
closed records reach the workflow log — never raw container output,
env dumps, TUI content or exception strings.  NO Codex binary is
invoked anywhere in R (not even --help): the allowlist admits no
native executable path or shell launch form, and the workflow
fixture job and the fixture sources are statically asserted free of
any invocation.
This job is the Python-only disposable-CI capability proof, not
genuine native-client qualification (D09 remains NOT RUN).  No
secrets are forwarded to the fixture.
"""

from __future__ import annotations

import argparse
import ast
import fcntl
import hashlib
import json
import os
import platform
import pty as pty_module
import re
import shutil
import signal
import socket
import stat
import struct
import subprocess
import sys
import tarfile
import termios
import threading
import time
import urllib.request
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import IO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cache_native_fixture_controller as fixture_controller  # noqa: E402
import cache_native_fixture_export_client as fixture_export  # noqa: E402
import cache_native_fixture_model as model  # noqa: E402
import cache_native_fixture_standin as fixture_standin  # noqa: E402

SCHEMA = "slaif-cache-native-fixture-ci-v1"
# Exact digest-pinned Python 3.12 base, byte-identical to the
# repository Dockerfile's runtime base (copied, not transcribed).
PINNED_BASE = (
    "python:3.12-slim-bookworm"
    "@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254"
)
IMAGE_NAME = "slaif-fixture-017r:local"
CONTROLLER_UID = model.CONTROLLER_UID  # 21001
SUBJECT_UID = model.SUBJECT_UID  # 21002
CONTROLLER_PORT = 18443
MEMORY_BYTES = model.MEMORY_LIMIT_BYTES  # 1 GiB, no swap
PIDS_LIMIT = model.PIDS_LIMIT  # 96
NANOCPUS = 1_000_000_000  # 1 CPU
# Docker tmpfs specs: per-budget explicit uid/gid/mode (controller
# private mounts 0700-only; subject scratch may use 1777).
_TMPFS_MODES = {("/run/slaif-ctl"): 0o700, ("/run/slaif-subj"): 0o700, ("/tmp"): 0o1777}
TMPFS_SPECS: dict[str, str] = {
    mount: (f"rw,nosuid,size={size // 1024}k,uid={uid},gid={gid},mode={oct(mode)[2:]}")
    for mount, size, uid, gid in model.DEFAULT_TMPFS_BUDGETS
    for mode in (_TMPFS_MODES[mount],)
}
TMPFS_TOTAL_BYTES = sum(size for _m, size, _u, _g in model.DEFAULT_TMPFS_BUDGETS)
TMPFS_SPEC_ENV = ",".join(
    f"{mount}:{size}:{uid}:{gid}" for mount, size, uid, gid in sorted(model.DEFAULT_TMPFS_BUDGETS)
)
# The daemon's default shared-memory mount is subject-writable, so
# it is explicitly bounded (never left to the daemon default) and
# measured back by the subject (model.SHM_SIZE_BYTES, 64 MiB).
SHM_SIZE_BYTES = model.SHM_SIZE_BYTES
SHM_SIZE_ARG = f"{SHM_SIZE_BYTES // (1024 * 1024)}m"
OUTPUT_CAP = 512 * 1024  # bounded child/docker output capture
# Closed bound on the readiness probe's own polling: the probe polls
# /healthz inside a fixed 30-second window with >=1s between
# attempts, so it structurally cannot attempt more than 30 times.
# The measured count is a distinct ledger quantity (it never charges
# the API request/attempt budgets) and must fall in [1, 30].
HZ_ATTEMPTS_WORST = 30
# The host-side owned PTY seam's fixed terminal size (the docker
# exec -it child is given an allocated terminal with exactly this
# size; the stand-in measures it back and the runner cross-checks).
PTY_ROWS = 24
PTY_COLS = 80
RUN_TIMEOUT = 120.0
HANG_TIMEOUT = 45.0
CRASH_WAIT_TIMEOUT = 90.0
BUILD_TIMEOUT = 600.0
PULL_TIMEOUT = 600.0
FETCH_TIMEOUT = 600.0
_QUERY_TIMEOUT = 60.0
_READER_GRACE_SECONDS = 5.0  # normal exit: drain grace before group kill
_READER_RECOVERY_SECONDS = 10.0  # after group kill: bounded convergence
_LEADER_REAP_SECONDS = 10.0  # bounded reap of the session leader
# One shared cumulative wall budget for the whole fixture run.
TOTAL_ANCHOR_SECONDS = 1800.0
_CONTAINER_ID_RE = re.compile(r"^[0-9a-f]{64}$")  # bare 64-hex (no sha256:)
_IMAGE_ID_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_TOKEN_RE = re.compile(r"^[0-9a-f]{32}$")
_ENGINE_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?\Z")
_RUNTIME_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_RUNTIME_PATH_RE = re.compile(r"^/[A-Za-z0-9._/-]{1,254}$")
_RUNTIME_VERSION_RE = re.compile(
    r"^(?P<name>[a-z0-9][a-z0-9._-]{0,63}) version "
    r"(?P<version>\d+\.\d+(?:.\d+)?(?:[-+][0-9A-Za-z.+-]+)?)\Z"
)
_NS_NAMES = ("pid", "mnt", "ipc", "uts", "net", "user")
# The docker CLI's authoritative missing-object marker: verified
# absence requires a SUCCESSFUL query that reports no such
# image/object; a daemon or transport failure (no marker) is a
# distinct unverified state, never absence.
_NO_SUCH_OBJECT_RE = re.compile(r"no such (?:image|object)", re.IGNORECASE)
# Unrelated parent-owned sentinel process marker (survives all
# scenarios; killed by the runner at the end).  The -c body must
# import time itself (a bare time.sleep would NameError).
PARENT_SENTINEL_MARKER = "import time; time.sleep(600) # slaif-parent-sentinel-017r"
# The controller-owned existence facts the 21002 denied-access proof
# requires (model law: ENOENT alone is not protection proof).  Both
# sides derive the same closed sha from the same fixed target set.
DENIED_TARGETS = model.DENIED_TARGETS
PRESENCE_SHA256 = hashlib.sha256(
    json.dumps(
        {name: True for name in DENIED_TARGETS}, sort_keys=True, separators=(",", ":")
    ).encode()
).hexdigest()
FIXTURE_SCRIPTS_DIR = "/opt/slaif-fixture"
STANDIN_PATH = f"{FIXTURE_SCRIPTS_DIR}/cache_native_fixture_standin.py"
EXPORT_CLIENT_PATH = f"{FIXTURE_SCRIPTS_DIR}/cache_native_fixture_export_client.py"

# Closed expected controller-measurement probe record (the probe
# runs INSIDE the container as 21001; the runner compares the full
# closed object, never raw output).
_CTL_PROBE_FACTS = {
    "ctl_dir": {"uid": CONTROLLER_UID, "mode": 0o700, "type": "dir"},
    "socket_dir": {"uid": CONTROLLER_UID, "mode": 0o700, "type": "dir"},
    "originals": {"uid": CONTROLLER_UID, "mode": 0o700, "type": "dir"},
    "registry": {"uid": CONTROLLER_UID, "mode": 0o600, "type": "file"},
    "sentinel": {"uid": CONTROLLER_UID, "mode": 0o600, "type": "file"},
    "exporter": {"uid": CONTROLLER_UID, "mode": 0o600, "type": "sock"},
}
EXPECTED_CTL_PROBE = {
    "record": "slaif-fixture-ctl-probe-v1",
    "status": "pass",
    "uid": CONTROLLER_UID,
    "pid1_uid": CONTROLLER_UID,
    "health": "ok",
    "facts": _CTL_PROBE_FACTS,
    "present": {name: True for name in DENIED_TARGETS},
}
# Module-level closed fact containers for the current run (the
# scenario functions record measured closed facts; run() consumes
# and clears them).  No raw content ever enters them.
_SC_FACTS: dict[str, dict[str, object]] = {}
_SC_EXPORT: dict[str, object] = {}
_SC_TEARDOWN: dict[str, object] = {}
# Fixed in-container probe (executed as 21001, argv-based python -c;
# emits exactly one closed JSON line, no raw content).
CONTROLLER_PROBE = r"""
import json, os, stat, sys, time, urllib.request
def fail(reason):
    print(json.dumps({"record": "slaif-fixture-ctl-probe-v1",
                      "status": "fail", "reason": reason},
                     sort_keys=True, separators=(",", ":")))
    raise SystemExit(2)
if os.getuid() != 21001:
    fail("uid-not-21001")
uid1 = None
with open("/proc/1/status", encoding="ascii") as handle:
    for line in handle:
        if line.startswith("Uid:"):
            uid1 = int(line.split()[1])
if uid1 != 21001:
    fail("pid1-uid")
deadline = time.time() + 30
ready = False
attempts = 0
while time.time() < deadline:
    attempts += 1
    try:
        with urllib.request.urlopen(
                "http://127.0.0.1:18443/healthz", timeout=2) as resp:
            if resp.status == 200:
                ready = True
                break
    except Exception:
        pass
    time.sleep(1)
if not ready:
    fail("health-unreachable")
targets = {
    "ctl_dir": "/run/slaif-ctl",
    "socket_dir": "/run/slaif-ctl/socket",
    "originals": "/run/slaif-ctl/originals",
    "registry": "/run/slaif-ctl/issued-registry.json",
    "sentinel": "/run/slaif-ctl/sentinel",
    "exporter": "/run/slaif-ctl/socket/exporter.sock",
}
facts = {}
for name, path in targets.items():
    st = os.lstat(path)
    kind = ("dir" if stat.S_ISDIR(st.st_mode)
            else "sock" if stat.S_ISSOCK(st.st_mode)
            else "file" if stat.S_ISREG(st.st_mode) else "bad")
    facts[name] = {"uid": st.st_uid, "mode": stat.S_IMODE(st.st_mode),
                   "type": kind}
presence_targets = {
    "controller_socket_dir": "/run/slaif-ctl/socket",
    "issued_registry": "/run/slaif-ctl/issued-registry.json",
    "controller_originals": "/run/slaif-ctl/originals",
    "controller_sentinel": "/run/slaif-ctl/sentinel",
    "controller_proc": "/proc/1/environ",
    "exporter_socket": "/run/slaif-ctl/socket/exporter.sock",
}
present = {name: os.path.lexists(path)
           for name, path in presence_targets.items()}
print(json.dumps({"record": "slaif-fixture-ctl-probe-v1",
                  "status": "pass", "uid": 21001, "pid1_uid": 21001,
                  "health": "ok", "healthz_attempts": attempts,
                  "facts": facts, "present": present},
                 sort_keys=True, separators=(",", ":")))
"""


class FixtureError(RuntimeError):
    """Fail-closed runner error carrying a fixed reason enum only."""


@dataclass(frozen=True)
class ExecResult:
    returncode: int
    output: bytes  # bounded (<= OUTPUT_CAP + one chunk), rest discarded
    drained_bytes: int = 0  # ALL bytes read (retained + discarded)


Executor = Callable[[list[str], float], ExecResult]


class _OwnedTimeout(subprocess.TimeoutExpired):
    """Host deadline carrying the bounded partial captured output.

    The hang scenario needs the stand-in's pre-timeout record (its
    token-bound descendant facts) even though the attached CLI was
    killed at the deadline; the partial output is bounded exactly
    like any other capture.  The reader's MEASURED drained total
    (retained + discarded) is preserved alongside the retained
    partial so the non-resettable output ledger can be charged the
    true drained amount instead of silently losing it on timeout.
    ``output`` aliases the retained partial so the timeout is
    chargeable exactly like any other bounded capture.
    """

    def __init__(
        self,
        cmd: list[str],
        timeout: float,
        partial_output: bytes,
        drained_bytes: int | None = None,
    ) -> None:
        super().__init__(cmd, timeout)
        self.partial_output = partial_output
        self.output = partial_output
        self.drained_bytes = len(partial_output) if drained_bytes is None else drained_bytes


def sha256_file(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_bounded_output(stream: IO[bytes], cap: int) -> tuple[bytes, int]:
    """Read a byte stream keeping at most ``cap`` bytes; drain and
    discard the rest.  Returns (kept, total_read): the retained
    capture and ALL drained/emitted bytes are distinct measured
    quantities (the total is the budget-charged figure)."""
    kept = bytearray()
    total = 0
    while True:
        chunk = stream.read(65536)
        if not chunk:
            break
        total += len(chunk)
        if len(kept) < cap:
            kept.extend(chunk[: cap - len(kept)])
        # else: drain and discard (bounded memory)
    return bytes(kept), total


def extract_record_line(data: bytes) -> str | None:
    """Return the last non-empty JSON-ish line (closed-record candidate)."""
    lines = [
        line
        for line in data.decode("utf-8", "replace").splitlines()
        if line.strip().startswith("{")
    ]
    return lines[-1] if lines else None


def _kill_process_group(proc: subprocess.Popen[bytes]) -> None:
    """Kill the exact owned process group (CLI + owned descendants)."""
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.kill()
        except (ProcessLookupError, OSError):
            pass


def _real_execute(argv: list[str], timeout: float, pty: bool = False) -> ExecResult:
    """Run an argv list with bounded output capture and owned-group
    cleanup (the reviewed P pipe/reader design).

    The child runs in its own session so a timeout kills the exact
    owned process group.  The stdout pipe is owned by the reader
    thread ALONE: it reads, bounds, drains and closes the fd, so the
    parent never closes a BufferedReader another thread may be
    reading (no cross-thread lock can hang the runner).  A leader
    that exits while an owned descendant still holds the write side
    is handled on EVERY path by a bounded grace join followed by the
    exact owned group kill.  A capture read failure is caught in the
    reader and reported to the parent as the fixed closed state
    ``output-read-failed``: it never escapes as an uncaught thread
    exception (raw text leak) and never degrades into an
    empty-success ExecResult.

    PTY attachment is ACTUAL, not an argv flag: for a closed-grammar
    ``docker exec -it`` argv (the only argv form the allowlist admits
    with ``-it``) — or when requested explicitly — the child's stdio
    is an OWNED allocated terminal (pty.openpty at the fixed closed
    size) so the docker client really has an interactive stdio seam;
    the master fd is owned by the reader thread ALONE and closed
    exactly once on every path."""
    use_pty = pty or (
        len(argv) >= 3 and argv[0] == "docker" and argv[1] == "exec" and "-it" in argv
    )
    if use_pty:
        return _real_execute_pty(argv, timeout)
    proc = subprocess.Popen(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    assert proc.stdout is not None
    pipe = proc.stdout
    capture: dict[str, object] = {}

    def _reader() -> None:
        try:
            kept, total = read_bounded_output(pipe, OUTPUT_CAP)
            capture["data"] = kept
            capture["total"] = total
        except Exception:
            capture["error"] = True
        finally:
            try:
                pipe.close()
            except OSError:
                pass

    reader = threading.Thread(target=_reader, daemon=True)
    reader.start()
    try:
        try:
            returncode = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill_process_group(proc)
            try:
                proc.wait(timeout=_LEADER_REAP_SECONDS)
            except subprocess.TimeoutExpired:
                raise FixtureError("process-cleanup-failed") from None
            reader.join(timeout=_READER_RECOVERY_SECONDS)
            if reader.is_alive():
                raise FixtureError("process-cleanup-failed") from None
            if "error" in capture:
                raise FixtureError("output-read-failed") from None
            partial = capture.get("data", b"")
            total = capture.get("total", 0)
            assert isinstance(partial, bytes)
            assert isinstance(total, int)
            raise _OwnedTimeout(argv, timeout, partial, total) from None
        reader.join(timeout=_READER_GRACE_SECONDS)
        if reader.is_alive():
            _kill_process_group(proc)
            reader.join(timeout=_READER_RECOVERY_SECONDS)
            if reader.is_alive():
                raise FixtureError("process-cleanup-failed") from None
        if "error" in capture:
            raise FixtureError("output-read-failed") from None
    finally:
        if proc.poll() is None:
            _kill_process_group(proc)
        try:
            proc.wait(timeout=_LEADER_REAP_SECONDS)
        except subprocess.TimeoutExpired:
            pass
    data = capture.get("data", b"")
    assert isinstance(data, bytes)
    total = capture.get("total", 0)
    assert isinstance(total, int)
    return ExecResult(returncode, data, total)


def _real_execute_pty(argv: list[str], timeout: float) -> ExecResult:
    """The owned host-side PTY seam: the child's stdio is an
    allocated terminal with the fixed closed size, so ``docker
    exec -it`` is a real attachment even though the GitHub step
    itself has no interactive stdin TTY.  The master fd is owned by
    the reader thread ALONE (it reads, bounds, drains and closes it)
    so the parent never touches another thread's fd; the slave is
    closed by the parent immediately after spawn.  A read OSError
    (EIO after the owned slave side is gone) is the NORMAL end of
    the stream, not a capture error: truncation stays fail-closed
    because every consumer must then parse a complete closed record.
    """
    master, slave = pty_module.openpty()
    fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", PTY_ROWS, PTY_COLS, 0, 0))
    try:
        proc = subprocess.Popen(
            argv,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            start_new_session=True,
        )
    except BaseException:
        os.close(slave)
        os.close(master)
        raise
    os.close(slave)
    capture: dict[str, object] = {}

    def _reader() -> None:
        kept = bytearray()
        total = 0
        try:
            while True:
                chunk = os.read(master, 65536)
                if not chunk:
                    break
                total += len(chunk)
                if len(kept) < OUTPUT_CAP:
                    kept.extend(chunk[: OUTPUT_CAP - len(kept)])
        except OSError:
            pass  # owned slave side gone = normal stream end
        finally:
            try:
                os.close(master)
            except OSError:
                pass
            capture["data"] = bytes(kept)
            capture["total"] = total

    reader = threading.Thread(target=_reader, daemon=True)
    reader.start()
    try:
        try:
            returncode = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill_process_group(proc)
            try:
                proc.wait(timeout=_LEADER_REAP_SECONDS)
            except subprocess.TimeoutExpired:
                raise FixtureError("process-cleanup-failed") from None
            reader.join(timeout=_READER_RECOVERY_SECONDS)
            if reader.is_alive():
                raise FixtureError("process-cleanup-failed") from None
            partial = capture.get("data", b"")
            total = capture.get("total", 0)
            assert isinstance(partial, bytes)
            assert isinstance(total, int)
            raise _OwnedTimeout(argv, timeout, partial, total) from None
        reader.join(timeout=_READER_GRACE_SECONDS)
        if reader.is_alive():
            _kill_process_group(proc)
            reader.join(timeout=_READER_RECOVERY_SECONDS)
            if reader.is_alive():
                raise FixtureError("process-cleanup-failed") from None
    finally:
        if proc.poll() is None:
            _kill_process_group(proc)
        try:
            proc.wait(timeout=_LEADER_REAP_SECONDS)
        except subprocess.TimeoutExpired:
            pass
        # Every path that reaches here has JOINED the reader (or
        # raised), and the reader's finally owns the master close;
        # the seam fd therefore never leaks into this process.
    data = capture.get("data", b"")
    assert isinstance(data, bytes)
    total = capture.get("total", 0)
    assert isinstance(total, int)
    return ExecResult(returncode, data, total)


# -- closed command allowlist (the ONLY executable argv vocabulary) --
# The guard is a narrow reviewable allowlist, not a character-class
# scan: it permits ONLY the exact docker operation grammar below,
# the exact fixture python/script/probe entry points, and the
# reviewed bare runtime --version query (the runtime name is
# grammar-validated by the engine preflight before any argv is
# built).  Anything else — native executable paths, shell launch
# forms, arbitrary programs — is a fixed failure BEFORE any process
# is created.  A static archive filename in fetch data is never an
# executed argv element and is therefore outside (and refused by)
# this vocabulary.
_STANDIN_MODES = (
    "measure",
    "pty",
    "success",
    "fail",
    "hang",
    "output-cap",
    "stop-owned",
    "diagnostic",
)
_INSPECT_FORMATS = frozenset(
    {
        "{{json .HostConfig}}",
        "{{json .Config}}",
        "{{json .State}}",
        "{{.Id}}",
        "{{.HostConfig.LogConfig.Type}}",
        "{{.Config.User}}",
    }
)
# The engine preflight's closed query vocabulary (exact operation
# grammar; the daemon-declared runtime path is never executed).
_VERSION_FORMATS = frozenset({"{{.Server.Version}}"})
_INFO_FORMATS = frozenset(
    {
        "{{range .SecurityOptions}}{{.}} {{end}}",
        "{{.DefaultRuntime}}",
        "{{json .Runtimes}}",
    }
)
_ENV_KEY_RE = re.compile(r"^SLAIF_(?:FIXTURE_|HANG_|STOP_|RUN_)[A-Z0-9_]{1,64}$")
# Closed env value grammar: numerics, hex digests, ns link
# identifiers (``mnt:[123]``), the shared monotonic anchor repr,
# tmpfs spec lists, uid pairs, ports, tokens and owned absolute
# paths (the hosted runner's owned temp roots may contain ``_``).
_ENV_VALUE_RE = re.compile(r"^[0-9A-Za-z.:,/@\[\]=_-]{1,512}$")
# The scenario container name pattern (anchor-free for embedding):
# the scenario segment is the CLOSED model scenario-name
# enumeration, not an open character class (the focused test suite
# asserts lockstep with model.SCENARIO_NAMES).
_NAME_PATTERN = (
    r"slaif-fixture-017r-(?:"
    r"controller-measurement|exec-21002-measurement|pty-attach|"
    r"synthetic-success|synthetic-fail|synthetic-hang|"
    r"synthetic-output-cap|export-fail|quiesce-fail|controller-crash"
    r")-\d+-\d+-[0-9a-f]{8}"
)
_NAME_RE = re.compile(r"^" + _NAME_PATTERN + r"$")
_LABEL_RE = re.compile(r"^slaif-owned-fixture-017r=[0-9a-f]{32}$")


def _is_cid(value: str) -> bool:
    return bool(_CONTAINER_ID_RE.fullmatch(value))


def _is_image_ref(value: str) -> bool:
    return value == IMAGE_NAME


def _match_docker_ps(argv: list[str]) -> bool:
    return (
        len(argv) == 5
        and argv[:4] == ["docker", "ps", "-aq", "--filter"]
        and (
            re.fullmatch(r"name=" + _NAME_PATTERN, argv[4])
            or re.fullmatch(r"id=[0-9a-f]{64}", argv[4])
            or argv[4] == f"ancestor={IMAGE_NAME}"
        )
    )


def _match_docker_version(argv: list[str]) -> bool:
    return (
        len(argv) == 4
        and argv[:3] == ["docker", "version", "--format"]
        and argv[3] in _VERSION_FORMATS
    )


def _match_docker_info(argv: list[str]) -> bool:
    return (
        len(argv) == 4 and argv[:3] == ["docker", "info", "--format"] and argv[3] in _INFO_FORMATS
    )


def _match_docker_rm(argv: list[str]) -> bool:
    return len(argv) == 4 and argv[:3] == ["docker", "rm", "-f"] and _is_cid(argv[3])


def _match_docker_create(argv: list[str]) -> bool:
    if len(argv) < 4 or argv[:2] != ["docker", "create"]:
        return False
    i = 2
    if argv[i] != "--name" or not _NAME_RE.fullmatch(argv[i + 1]):
        return False
    i += 2
    if argv[i] != "--label" or not _LABEL_RE.fullmatch(argv[i + 1]):
        return False
    i += 2
    fixed = (
        ("--network", "none"),
        ("--read-only", ""),
        ("--user", f"{CONTROLLER_UID}:{CONTROLLER_UID}"),
        ("--cap-drop", "ALL"),
        ("--security-opt", "no-new-privileges:true"),
        ("--security-opt", "seccomp=builtin"),
        ("--log-driver", "none"),
        ("--memory", str(MEMORY_BYTES)),
        ("--memory-swap", str(MEMORY_BYTES)),
        ("--pids-limit", str(PIDS_LIMIT)),
        ("--cpus", "1"),
        ("--shm-size", SHM_SIZE_ARG),
    )
    for flag, value in fixed:
        if argv[i] != flag:
            return False
        if value:
            if i + 1 >= len(argv) or argv[i + 1] != value:
                return False
            i += 2
        else:
            i += 1
    expected_tmpfs = {f"{m}:{TMPFS_SPECS[m]}" for m in TMPFS_SPECS}
    tmpfs: set[str] = set()
    while i < len(argv) and argv[i] == "--tmpfs":
        if i + 1 >= len(argv) or argv[i + 1] not in expected_tmpfs:
            return False
        tmpfs.add(argv[i + 1])
        i += 2
    if tmpfs != expected_tmpfs:
        return False
    while i < len(argv) and argv[i] == "-e":
        if i + 1 >= len(argv):
            return False
        key, sep, value = argv[i + 1].partition("=")
        if not sep or not _ENV_KEY_RE.fullmatch(key) or not _ENV_VALUE_RE.fullmatch(value):
            return False
        i += 2
    return i + 1 == len(argv) and _is_image_ref(argv[i])


def _match_docker_start(argv: list[str]) -> bool:
    return len(argv) == 3 and argv[:2] == ["docker", "start"] and _is_cid(argv[2])


def _match_docker_wait(argv: list[str]) -> bool:
    return len(argv) == 3 and argv[:2] == ["docker", "wait"] and _is_cid(argv[2])


def _match_docker_pull(argv: list[str]) -> bool:
    return len(argv) == 3 and argv[:2] == ["docker", "pull"] and argv[2] == PINNED_BASE


def _match_docker_build(argv: list[str]) -> bool:
    return (
        len(argv) == 5
        and argv[:4] == ["docker", "build", "-t", IMAGE_NAME]
        and re.fullmatch(r"/[A-Za-z0-9._/-]{1,512}", argv[4])
        and ".." not in argv[4].split("/")
    )


def _match_docker_inspect(argv: list[str]) -> bool:
    return (
        len(argv) == 5
        and argv[:3] == ["docker", "inspect", "--format"]
        and argv[3] in _INSPECT_FORMATS
        and (_is_cid(argv[4]) or _is_image_ref(argv[4]))
    )


def _match_docker_top(argv: list[str]) -> bool:
    return len(argv) == 3 and argv[:2] == ["docker", "top"] and _is_cid(argv[2])


def _match_docker_image_inspect(argv: list[str]) -> bool:
    return (
        len(argv) == 4
        and argv[:3] == ["docker", "image", "inspect"]
        and re.fullmatch(r"sha256:[0-9a-f]{64}", argv[3])
    )


def _match_docker_rmi(argv: list[str]) -> bool:
    return (
        len(argv) == 3
        and argv[:2] == ["docker", "rmi"]
        and re.fullmatch(r"sha256:[0-9a-f]{64}", argv[2])
    )


def _match_docker_exec(argv: list[str]) -> bool:
    """The exec boundary: optional PTY, the exact fixture uid pair,
    closed env keys/values, the exact registered CID, and ONLY the
    fixed fixture python entry points (controller probe, stand-in
    modes, export client).  No shell, no arbitrary program."""
    if len(argv) < 5 or argv[:2] != ["docker", "exec"]:
        return False
    i = 2
    if argv[i] == "-it":
        i += 1
    if argv[i] != "--user" or argv[i + 1] not in (
        f"{CONTROLLER_UID}:{CONTROLLER_UID}",
        f"{SUBJECT_UID}:{SUBJECT_UID}",
    ):
        return False
    i += 2
    while i < len(argv) and argv[i] == "-e":
        key, sep, value = argv[i + 1].partition("=")
        if not sep or not _ENV_KEY_RE.fullmatch(key) or not _ENV_VALUE_RE.fullmatch(value):
            return False
        i += 2
    if not _is_cid(argv[i]):
        return False
    tail = argv[i + 1 :]
    probe = (
        len(tail) == 3 and tail[0] == "python3" and tail[1] == "-c" and tail[2] == CONTROLLER_PROBE
    )
    standin = (
        len(tail) == 4
        and tail[0] == "python3"
        and tail[1] == STANDIN_PATH
        and tail[2] == "--mode"
        and tail[3] in _STANDIN_MODES
    )
    export = len(tail) == 2 and tail[0] == "python3" and tail[1] == EXPORT_CLIENT_PATH
    return probe or standin or export


def _match_runtime_version(argv: list[str]) -> bool:
    return (
        len(argv) == 2
        and argv[1] == "--version"
        and _RUNTIME_NAME_RE.fullmatch(argv[0])
        and argv[0] != "codex"
    )


_ARGV_MATCHERS = (
    _match_docker_ps,
    _match_docker_version,
    _match_docker_info,
    _match_docker_rm,
    _match_docker_create,
    _match_docker_start,
    _match_docker_wait,
    _match_docker_pull,
    _match_docker_build,
    _match_docker_inspect,
    _match_docker_top,
    _match_docker_image_inspect,
    _match_docker_rmi,
    _match_docker_exec,
    _match_runtime_version,
)


# -- host ledger (non-resettable, shared with the shared deadline) ----------
class _RunLedger:
    """The host-side NON-RESETTABLE aggregate ledger covering every
    container and phase of the run (no per-phase reset, no refunds).

    The DISTINCT measured quantities (closed documented scopes, see
    docs/CACHE-OBSERVATION-CONTRACT.md) are kept as distinct
    counters and are never redefined into each other:

    * docker_admissions / docker_refusals — the host command
      allowlist: an admission is charged BEFORE the work; a refused
      argv is counted and never executed;
    * bytes_drained / bytes_retained — ALL captured bytes vs the
      bounded retained capture (the output budget charges drained);
    * api_requests — provider API requests that RECEIVED A RESPONSE
      (POST /v1/responses answered 200 or 400; exporter quiesce /
      export commands answered); a refused call IS a request;
    * api_attempts — client-side wire attempts, the superset of
      api_requests (refused connections and retries included);
    * requests_admitted / requests_refused — the response outcomes
      of api_requests (200 / quiesce-ok / valid frame vs 400 /
      error line / invalid frame), so admitted + refused ==
      api_requests;
    * healthz_attempts — readiness polling attempts, bounded by the
      probe's own closed 30-second window; a distinct quantity that
      never charges the API budgets.

    Enforcement is PRE-WORK: each scenario's closed worst-case wire
    bound is reserved against the REMAINING API budgets before any
    of its work may start (an over-budget scenario never begins),
    and the MEASURED scenario facts are charged at scenario end with
    all validation BEFORE any counter mutation (an overbound charge
    is refused with every counter left exactly as found).  A phase
    that crashes keeps its reservation outstanding and the run fails
    closed — there is no reset, no refund and no silent re-budgeting
    from unknown or crashed phases."""

    MAX_HOST_ADMISSIONS = 256  # closed finite host-command bound

    def __init__(self, budgets: model.FixtureBudgets) -> None:
        self.output_cap = budgets.output_cap_bytes
        self.max_requests = budgets.max_requests
        self.max_attempts = budgets.max_attempts
        self.admissions = 0
        self.refusals = 0
        self.bytes_drained = 0
        self.bytes_retained = 0
        self.api_requests = 0
        self.api_attempts = 0
        self.requests_admitted = 0
        self.requests_refused = 0
        self.healthz_attempts = 0

    @staticmethod
    def _check_int(name: str, value: object) -> int:
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise FixtureError(f"ledger-{name}-invalid")
        return value

    def admit(self) -> None:
        """Charge the admission BEFORE the work happens."""
        if self.admissions + 1 > self.MAX_HOST_ADMISSIONS:
            raise FixtureError("ledger-admission-cap")
        self.admissions += 1

    def refuse(self) -> None:
        self.refusals += 1

    def charge(self, result: ExecResult | _OwnedTimeout) -> None:
        drained = result.drained_bytes
        if not isinstance(drained, int) or drained < 0:
            raise FixtureError("ledger-output-invalid")
        self.bytes_drained += drained
        self.bytes_retained += len(result.output)
        if self.bytes_drained > self.output_cap:
            raise FixtureError("ledger-output-cap")

    def charge_healthz(self, attempts: int) -> None:
        """Charge the MEASURED readiness polling attempts (distinct
        quantity; bounded by the probe's closed window)."""
        self._check_int("healthz", attempts)
        self.healthz_attempts += attempts

    def reserve_http(self, requests: int, attempts: int) -> None:
        """PRE-WORK reservation: the scenario's closed worst-case
        wire bound must fit the REMAINING API budgets before any of
        the scenario's wire work may start.  A scenario that cannot
        fit is refused BEFORE its first request — the reservation
        uses the current counters (all previously measured charges
        included), so an over-budget scenario can never begin."""
        self._check_int("reserve-requests", requests)
        self._check_int("reserve-attempts", attempts)
        if requests > attempts:
            raise FixtureError("ledger-reserve-identity")
        if self.api_requests + requests > self.max_requests:
            raise FixtureError("ledger-request-reserve")
        if self.api_attempts + attempts > self.max_attempts:
            raise FixtureError("ledger-attempt-reserve")

    def charge_http(self, requests: int, attempts: int, admitted: int, refused: int) -> None:
        """SCENARIO-END charge of the MEASURED per-container wire
        facts (called before the next scenario is admitted).  ALL
        validation happens BEFORE any counter mutation: an invalid,
        overbound or outcome-inconsistent charge is refused with
        every counter left exactly as found (no partial mutation,
        no refund, no reset)."""
        requests = self._check_int("requests", requests)
        attempts = self._check_int("attempts", attempts)
        admitted = self._check_int("admitted", admitted)
        refused = self._check_int("refused", refused)
        if requests > attempts:
            raise FixtureError("ledger-attempt-identity")
        if admitted + refused != requests:
            raise FixtureError("ledger-outcome-identity")
        if self.api_requests + requests > self.max_requests:
            raise FixtureError("ledger-request-cap")
        if self.api_attempts + attempts > self.max_attempts:
            raise FixtureError("ledger-attempt-cap")
        # mutate only after every check passed
        self.api_requests += requests
        self.api_attempts += attempts
        self.requests_admitted += admitted
        self.requests_refused += refused


def _guarded_execute(
    executor: Executor,
    deadline: _RunDeadline,
    ledger: _RunLedger,
) -> Executor:
    """Runtime NO-CODEX proof: the closed allowlist is the only
    execution path, every call consumes REMAINING shared-deadline
    budget (never a fresh phase budget), and the host ledger
    charges the admission BEFORE work and the drained output AFTER.
    The ledger is REQUIRED: no host command may execute without
    being admitted (charged before work) and accounted (charged
    after); refused argv is counted as a refusal and never
    executed."""

    def guarded(argv: list[str], timeout: float) -> ExecResult:
        for element in argv:
            if not isinstance(element, str):
                ledger.refuse()
                raise FixtureError("argv-untrusted")
        if not any(matcher(argv) for matcher in _ARGV_MATCHERS):
            ledger.refuse()
            raise FixtureError("argv-untrusted")
        ledger.admit()
        effective = min(timeout, deadline.remaining())
        try:
            result = executor(argv, effective)
        except _OwnedTimeout as exc:
            # A timed-out capture is still a measured fact: charge the
            # drained total (retained + discarded) and the bounded
            # retained partial exactly once, before the scenario
            # consumes the timeout — a hang emitting discarded output
            # can never skip the non-resettable output budget.
            ledger.charge(exc)
            raise
        ledger.charge(result)
        return result

    return guarded


def _query(executor: Executor, argv: list[str]) -> bytes:
    result = executor(argv, _QUERY_TIMEOUT)
    if result.returncode != 0:
        raise FixtureError("query-failed")
    return result.output


def _ps_filter(executor: Executor, filter_arg: str) -> str:
    """``absent`` | ``present`` | ``query-failed`` (never conflated)."""
    result = executor(["docker", "ps", "-aq", "--filter", filter_arg], _QUERY_TIMEOUT)
    if result.returncode != 0:
        return "query-failed"
    return "absent" if result.output.strip() == b"" else "present"


def cleanup_container(executor: Executor, container_id: str) -> None:
    """Remove ONLY the exact registered owned container (idempotent).

    Already-absent (verified) is a successful no-op; ``rm -f`` is
    used only for a verified-present owned container, and the result
    is re-verified.  Query failure or a still-present container is a
    recorded cleanup failure, never swallowed.
    """
    state = _ps_filter(executor, f"id={container_id}")
    if state == "query-failed":
        raise FixtureError("cleanup-query-failed")
    if state == "absent":
        return
    result = executor(["docker", "rm", "-f", container_id], _QUERY_TIMEOUT)
    if result.returncode != 0:
        raise FixtureError("cleanup-failed")
    if _ps_filter(executor, f"id={container_id}") != "absent":
        raise FixtureError("cleanup-failed")


def verify_no_leftovers(executor: Executor, image_ref: str) -> None:
    """No container (running or stopped) may remain for the built image."""
    result = executor(["docker", "ps", "-aq", "--filter", f"ancestor={image_ref}"], _QUERY_TIMEOUT)
    if result.returncode != 0:
        raise FixtureError("leftover-query-failed")
    if result.output.strip():
        raise FixtureError("leftover-container")


def parent_namespace_ids() -> dict[str, str]:
    """The disposable parent's own namespace identities (read-only)."""
    return {name: os.readlink(f"/proc/self/ns/{name}") for name in _NS_NAMES}


def _create_work_root(work) -> None:
    """Create a FRESH owned 0700 scratch root (never adopt/overwrite).

    The path is validated AS GIVEN: no lexical ``.``/``..`` folding
    and no symlink resolution are applied before the walk (folding
    would launder a symlinked ancestor such as ``link/../work`` into
    a clean-looking alias of a pre-existing target), so
    parent-traversal components are rejected outright.  Every
    existing component must be a real, non-symlink directory, and
    the final component must not pre-exist (in any form).
    """
    from pathlib import Path

    if not os.path.isabs(str(work)):
        work = Path(os.path.join(os.getcwd(), str(work)))
    if ".." in work.parts or "." in work.parts:
        raise FixtureError("work-root-untrusted")
    current = Path("/")
    for part in work.parts[1:-1]:
        candidate = current / part
        if candidate.is_symlink():
            raise FixtureError("work-root-untrusted")
        if not candidate.is_dir():
            raise FixtureError("work-root-untrusted")
        current = candidate
    if not current.is_dir() or current.is_symlink():
        raise FixtureError("work-root-untrusted")
    path = current / work.parts[-1]
    if path.exists() or path.is_symlink():
        raise FixtureError("work-root-exists")
    path.mkdir()
    os.chmod(path, stat.S_IRWXU)
    st = path.lstat()
    if stat.S_IMODE(st.st_mode) != stat.S_IRWXU or st.st_uid != os.getuid():
        raise FixtureError("work-root-untrusted")


def _owned_subdir(work, name: str):
    from pathlib import Path

    path = Path(work) / name
    if path.exists() or path.is_symlink():
        raise FixtureError("work-root-exists")
    path.mkdir()
    os.chmod(path, stat.S_IRWXU)
    return path


def _destroy_owned_work_root(work) -> bool:
    """Destroy the EXACT registered fresh owned scratch root and
    VERIFY the result.  The root was created fresh by this run (the
    registration fact in _create_work_root), so destroying it never
    touches a pre-existing root or changes any pre-existing
    permission.  A failed or unverified destruction is an honest
    False for the caller to expose — never a silent skip."""
    try:
        shutil.rmtree(work)
    except OSError:
        pass
    return not os.path.lexists(str(work))


def _spawn_parent_sentinel() -> subprocess.Popen[bytes]:
    """Unrelated parent-owned sentinel process (must survive teardown)."""
    return subprocess.Popen(
        [sys.executable, "-c", PARENT_SENTINEL_MARKER],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _count_uid_marker_processes(uid: int, marker: str) -> int:
    """Bounded read-only /proc count of exact uid + marker occurrences.

    Container processes ARE visible in the host /proc (the private
    namespace hides the host from the container, never the reverse);
    the uid filter selects the fixture subject's container children.
    A vanished entry (FileNotFoundError mid-scan) is expected churn;
    ANY other read error means the scan did not observe the whole
    namespace — a recorded scan failure, never a silent zero.
    """
    count = 0
    try:
        entries = [e for e in os.listdir("/proc") if e.isdigit()]
    except OSError:
        raise FixtureError("proc-scan-failed") from None
    if len(entries) > 20000:
        # The closed scan bound is exceeded: the listing is INCOMPLETE
        # as far as the supported bound goes, so presence/absence may
        # not be claimed from it.  Reject before any count (a silent
        # truncation would turn an unobserved match into a false
        # absence); normal vanished-entry churn handling is preserved
        # for complete listings.
        raise FixtureError("proc-scan-oversized") from None
    for entry in sorted(entries, key=int):
        try:
            with open(f"/proc/{entry}/status", encoding="ascii") as handle:
                uid_line = next((line for line in handle if line.startswith("Uid:")), None)
            if uid_line is None:
                continue
            if int(uid_line.split()[1]) != uid:
                continue
            with open(f"/proc/{entry}/cmdline", "rb") as handle:
                cmdline = handle.read(4096)
        except FileNotFoundError:
            continue  # vanished between listdir and read (expected churn)
        except (OSError, ValueError, StopIteration):
            raise FixtureError("proc-scan-degraded") from None
        if marker.encode() in cmdline:
            count += 1
    return count


def _count_fixture_uid_processes(uid: int) -> int:
    """Bounded read-only /proc count of ALL processes of the fixture
    uid (the post-teardown negative-after scan)."""
    count = 0
    try:
        entries = [e for e in os.listdir("/proc") if e.isdigit()]
    except OSError:
        raise FixtureError("proc-scan-failed") from None
    if len(entries) > 20000:
        # Over-bound listing: reject before any presence/absence claim
        # (see _count_uid_marker_processes); never truncate silently.
        raise FixtureError("proc-scan-oversized") from None
    for entry in sorted(entries, key=int):
        try:
            with open(f"/proc/{entry}/status", encoding="ascii") as handle:
                uid_line = next((line for line in handle if line.startswith("Uid:")), None)
            if uid_line is None:
                continue
            count += int(uid_line.split()[1]) == uid
        except FileNotFoundError:
            continue
        except (OSError, ValueError, StopIteration):
            raise FixtureError("proc-scan-degraded") from None
    return count


# -- public pinned artifact (fetch, verify, bounded extract) ------------------
class _RunDeadline:
    """The SAME shared finite run deadline as the in-container
    ``SLAIF_FIXTURE_DEADLINE_ABS`` anchor: fetch, build, queries,
    scenarios and cleanup each consume REMAINING budget before every
    blocking operation, so a progressing slow transfer can never
    reset the total (a single in-flight socket operation is bounded
    by the timeout chosen at connection time).  One explicit bounded
    cleanup grace may be added ONCE with a closed reason; a fresh
    phase budget is never the global budget."""

    def __init__(self, anchor: float) -> None:
        self.anchor = anchor
        self._grace = 0.0
        self._grace_reason: str | None = None

    def remaining(self) -> float:
        left = self.anchor + self._grace - time.monotonic()
        if left <= 0:
            raise FixtureError("deadline-expired")
        return left

    def add_grace(self, seconds: float, reason: str) -> None:
        if self._grace_reason is not None:
            raise FixtureError("deadline-grace-repeat")
        if not re.fullmatch(r"[a-z0-9-]{1,64}", reason):
            raise FixtureError("deadline-grace-invalid")
        if not 0 < seconds <= 600:
            raise FixtureError("deadline-grace-invalid")
        self._grace += seconds
        self._grace_reason = reason


_LICENSE_CAP = 24 * 1024


def _fetch_archive(dest, deadline: _RunDeadline) -> None:
    """Stream the public archive to an owned file (bounded memory)
    under the shared run deadline: the COMPLETE size is verified
    before any digest/extract step, and every read is preceded by a
    remaining-budget check (a slow progressing transfer cannot
    exceed the non-resettable total)."""
    request = urllib.request.Request(
        model.ARTIFACT_ARCHIVE_URL, headers={"User-Agent": "slaif-fixture-ci/017r"}
    )
    received = 0
    try:
        response = urllib.request.urlopen(request, timeout=min(120.0, deadline.remaining()))
    except Exception:
        raise FixtureError("archive-fetch-failed") from None
    try:
        with open(dest, "wb") as handle:
            while True:
                deadline.remaining()  # cumulative total enforcement
                chunk = response.read(65536)
                if not chunk:
                    break
                received += len(chunk)
                if received > model.ARTIFACT_ARCHIVE_SIZE:
                    raise FixtureError("archive-oversize")
                handle.write(chunk)
        deadline.remaining()
    except FixtureError:
        raise
    except Exception:
        raise FixtureError("archive-fetch-failed") from None
    finally:
        # The owned response handle is closed on EVERY success and
        # failure path (an error mid-stream never leaks it).
        response.close()
    if received != model.ARTIFACT_ARCHIVE_SIZE:
        raise FixtureError("archive-size")


def _fetch_text_identity(
    url: str,
    dest,
    cap: int,
    expected_sha256: str,
    markers: tuple[str, ...],
    tag: str,
    deadline: _RunDeadline,
) -> str:
    """Fetch a public text document at the pinned commit with bounded
    reads (cap+1 overflow detection — a longer response is rejected,
    never hashed truncated as the full document), verify the FULL
    byte identity (size via digest, closed markers, exact sha256)
    BEFORE any write, then store it at the owned destination.
    The response is closed on every path.  Returns the sha256."""
    from pathlib import Path

    request = urllib.request.Request(url, headers={"User-Agent": "slaif-fixture-ci/017r"})
    try:
        response = urllib.request.urlopen(request, timeout=min(60.0, deadline.remaining()))
    except Exception:
        raise FixtureError(f"{tag}-fetch-failed") from None
    try:
        data = response.read(cap + 1)
    except Exception:
        raise FixtureError(f"{tag}-fetch-failed") from None
    finally:
        response.close()
    if len(data) > cap:
        raise FixtureError(f"{tag}-oversize")
    if not data:
        raise FixtureError(f"{tag}-shape")
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise FixtureError(f"{tag}-identity")
    text = data.decode("utf-8", "replace")
    for marker in markers:
        if marker not in text:
            raise FixtureError(f"{tag}-identity")
    Path(dest).write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def _fetch_license(dest, deadline: _RunDeadline) -> str:
    """Fetch the public Apache-2.0 LICENSE at the pinned commit with
    the closed byte identity (size, markers, exact sha256)."""
    return _fetch_text_identity(
        model.ARTIFACT_LICENSE_URL,
        dest,
        _LICENSE_CAP,
        model.ARTIFACT_LICENSE_SHA256,
        model.ARTIFACT_LICENSE_MARKERS,
        "license",
        deadline,
    )


_NOTICE_CAP = 8 * 1024


def _fetch_notice(dest, deadline: _RunDeadline) -> str:
    """Fetch the public NOTICE (Ratatui-derived code, MIT) at the
    pinned commit with the closed byte identity (size, markers,
    exact sha256)."""
    return _fetch_text_identity(
        model.ARTIFACT_NOTICE_URL,
        dest,
        _NOTICE_CAP,
        model.ARTIFACT_NOTICE_SHA256,
        model.ARTIFACT_NOTICE_MARKERS,
        "notice",
        deadline,
    )


def fetch_public_artifact(dest_dir, deadline: _RunDeadline) -> dict[str, object]:
    """Fetch, size+digest verify, then extract ONLY the single
    expected regular executable (no symlink/hardlink/path escape,
    bounded decompressed size), and fetch the public license text at
    the pinned commit.  Returns the closed artifact facts."""
    from pathlib import Path

    archive = Path(dest_dir) / "archive.tar.gz"
    _fetch_archive(archive, deadline)
    digest = hashlib.sha256()
    with open(archive, "rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    if digest.hexdigest() != model.ARTIFACT_ARCHIVE_SHA256:
        raise FixtureError("archive-digest")
    binary_path = Path(dest_dir) / model.ARTIFACT_BINARY_NAME
    members_checked = 0
    try:
        with tarfile.open(archive, "r:gz") as tar:
            for member in tar:
                members_checked += 1
                if members_checked > 8:
                    raise FixtureError("archive-shape")
                if member.name != model.ARTIFACT_BINARY_NAME:
                    raise FixtureError("archive-shape")
                if (
                    member.issym()
                    or member.islnk()
                    or not member.isfile()
                    or member.name.startswith("/")
                    or ".." in member.name.split("/")
                ):
                    raise FixtureError("archive-shape")
                extracted = tar.extractfile(member)
                if extracted is None:
                    raise FixtureError("archive-shape")
                written = 0
                with open(binary_path, "wb") as handle:
                    while True:
                        deadline.remaining()
                        chunk = extracted.read(1024 * 1024)
                        if not chunk:
                            break
                        written += len(chunk)
                        if written > model.ARTIFACT_BINARY_MAX_BYTES:
                            raise FixtureError("binary-oversize")
                        handle.write(chunk)
    except FixtureError:
        raise
    except Exception:
        raise FixtureError("archive-extract-failed") from None
    # Exactly one member is REQUIRED before any filesystem fact is
    # read: an empty (or over-bound multi-member) archive is a typed
    # closed-shape failure, never a leaked lstat exception on the
    # never-created binary path.
    if members_checked != 1:
        raise FixtureError("archive-shape")
    st = binary_path.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_size != written:
        raise FixtureError("binary-identity")
    license_sha = _fetch_license(Path(dest_dir) / "LICENSE", deadline)
    notice_sha = _fetch_notice(Path(dest_dir) / "NOTICE", deadline)
    return {
        "binary_sha256": sha256_file(binary_path),
        "binary_size": st.st_size,
        "license_sha256": license_sha,
        "notice_sha256": notice_sha,
    }


# -- exact confinement create-argv (no shell, no host mounts, no secrets) -------
def build_run_conf_argv(
    image_ref: str, name: str, owned_label: str, env: dict[str, str]
) -> list[str]:
    """The exact confinement create-argv: controller UID 21001 as
    PID1, dedicated nonroot identity, all capabilities dropped,
    no-new-privileges, explicit builtin seccomp, read-only rootfs
    with only the owned bounded tmpfs budgets plus the explicitly
    bounded /dev/shm, private network, no host mounts/devices, and
    ``--log-driver none`` (verified by inspection, never by
    ``docker logs``)."""
    argv = [
        "docker",
        "create",
        "--name",
        name,
        "--label",
        owned_label,
        "--network",
        "none",
        "--read-only",
        "--user",
        f"{CONTROLLER_UID}:{CONTROLLER_UID}",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges:true",
        "--security-opt",
        "seccomp=builtin",
        "--log-driver",
        "none",
        "--memory",
        str(MEMORY_BYTES),
        "--memory-swap",
        str(MEMORY_BYTES),
        "--pids-limit",
        str(PIDS_LIMIT),
        "--cpus",
        "1",
        "--shm-size",
        SHM_SIZE_ARG,
    ]
    for mountpoint in sorted(TMPFS_SPECS):
        argv += ["--tmpfs", f"{mountpoint}:{TMPFS_SPECS[mountpoint]}"]
    for key in sorted(env):
        argv += ["-e", f"{key}={env[key]}"]
    argv.append(image_ref)
    return argv


def _engine_preflight(executor: Executor) -> tuple[str, str, str]:
    """Engine version + explicit seccomp + reviewed runtime identity
    (closed bounded queries only — never raw inspect/env dumps; the
    daemon-declared runtime path is shape-validated only and the
    version query runs the reviewed bare name through the standard
    PATH, never a daemon-supplied executable).  Returns
    (engine_version, runtime_name, runtime_version)."""
    engine_version = (
        _query(executor, ["docker", "version", "--format", "{{.Server.Version}}"])
        .decode("ascii", "replace")
        .strip()
    )
    if not _ENGINE_VERSION_RE.fullmatch(engine_version):
        raise FixtureError("engine-version-invalid")
    security_options = (
        _query(executor, ["docker", "info", "--format", "{{range .SecurityOptions}}{{.}} {{end}}"])
        .decode("ascii", "replace")
        .strip()
    )
    if "name=seccomp" not in security_options:
        raise FixtureError("seccomp-unavailable")
    default_runtime = (
        _query(executor, ["docker", "info", "--format", "{{.DefaultRuntime}}"])
        .decode("ascii", "replace")
        .strip()
    )
    if not _RUNTIME_NAME_RE.fullmatch(default_runtime):
        raise FixtureError("runtime-invalid")
    try:
        runtimes = json.loads(
            _query(executor, ["docker", "info", "--format", "{{json .Runtimes}}"])
        )
    except ValueError:
        raise FixtureError("runtime-invalid") from None
    runtime_entry = runtimes.get(default_runtime) if isinstance(runtimes, dict) else None
    # Moby serializes Runtimes with the lowercase ``path`` field; the
    # stock runc entry's path is the bare name "runc" (daemon/
    # runtime_unix.go stockRuntimes -> defaultRuntimeName), and an
    # empty path is likewise PATH-resolved.  A non-empty daemon-
    # declared absolute path is shape-validated ONLY, never executed.
    runtime_path = runtime_entry.get("path") if isinstance(runtime_entry, dict) else None
    if not isinstance(runtime_path, str):
        raise FixtureError("runtime-invalid")
    if runtime_path and not (
        _RUNTIME_NAME_RE.fullmatch(runtime_path)
        or (_RUNTIME_PATH_RE.fullmatch(runtime_path) and ".." not in runtime_path.split("/"))
    ):
        raise FixtureError("runtime-invalid")
    version_line = (
        _query(executor, [default_runtime, "--version"]).decode("ascii", "replace").splitlines()
    )
    version_match = _RUNTIME_VERSION_RE.fullmatch(version_line[0].strip() if version_line else "")
    if version_match is None or version_match.group("name") != default_runtime:
        raise FixtureError("runtime-version-invalid")
    return engine_version, default_runtime, version_match.group("version")


def _static_no_codex_invocation(repo) -> None:
    """Closed static proof that no R path invokes the native binary:
    (1) in every fixture python source, no call may carry an argv
    list containing the token ``codex``; (2) in the workflow, the
    cache-native-fixture job's non-comment lines must not contain
    the codex token as a word."""
    from pathlib import Path

    sources = (
        "cache_native_fixture_ci.py",
        "cache_native_fixture_controller.py",
        "cache_native_fixture_standin.py",
        "cache_native_fixture_export_client.py",
        "cache_native_fixture_model.py",
    )
    for name in sources:
        tree = ast.parse((Path(repo) / "scripts" / name).read_bytes().decode("utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not node.args:
                continue
            first = node.args[0]
            argv: list[str] = []
            if isinstance(first, ast.List):
                argv = [
                    elt.value
                    for elt in first.elts
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                ]
            elif isinstance(first, ast.Constant) and isinstance(first.value, str):
                argv = [first.value]
            if "codex" in argv:
                raise FixtureError("codex-invocation-static")
    workflow = (Path(repo) / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    in_job = False
    for raw_line in workflow.splitlines():
        line = raw_line.strip()
        if re.fullmatch(r"\s*cache-native-fixture:\s*", raw_line):
            in_job = True
            continue
        if in_job:
            if raw_line and not raw_line[0].isspace():
                in_job = False  # next top-level key: job section ended
                continue
            if line.startswith("#") or not line:
                continue
            if re.search(r"\bcodex\b", line, re.IGNORECASE):
                raise FixtureError("codex-invocation-static")


# -- scenario lifecycle helpers -------------------------------------------------
def _standin_env(
    base: dict[str, str],
    parent_pid: int,
    parent_port: int,
    sentinel_path,
    parent_ns: dict[str, str],
) -> dict[str, str]:
    env = dict(base)
    env["SLAIF_FIXTURE_PARENT_PID"] = str(parent_pid)
    env["SLAIF_FIXTURE_PARENT_PORT"] = str(parent_port)
    env["SLAIF_FIXTURE_SENTINEL_PATH"] = str(sentinel_path)
    for name in _NS_NAMES:
        env[f"SLAIF_FIXTURE_PARENT_NS_{name.upper()}"] = parent_ns[name]
    return env


def _new_container(executor: Executor, index: int, scenario: str, env: dict[str, str]) -> str:
    """Fresh name + ownership label; pre-existing collision is a
    fixed failure (never adopted); the ACTUAL returned bare 64-hex
    CID is validated and registered as owned BEFORE any start."""
    name = f"slaif-fixture-017r-{scenario}-{os.getpid()}-{index}-{uuid.uuid4().hex[:8]}"
    label = f"slaif-owned-fixture-017r={uuid.uuid4().hex}"
    if _ps_filter(executor, f"name={name}") != "absent":
        raise FixtureError("name-collision")
    result = executor(build_run_conf_argv(IMAGE_NAME, name, label, env), RUN_TIMEOUT)
    if result.returncode != 0:
        raise FixtureError("create-failed")
    container_id = result.output.decode("ascii", "replace").strip()
    if not _is_cid(container_id):
        raise FixtureError("create-failed")
    return container_id


def _start_container(executor: Executor, container_id: str) -> None:
    result = executor(["docker", "start", container_id], RUN_TIMEOUT)
    if result.returncode != 0:
        raise FixtureError("start-failed")


def _exec(
    executor: Executor,
    container_id: str,
    uid: int,
    tail: list[str],
    env: dict[str, str],
    timeout: float = RUN_TIMEOUT,
    pty: bool = False,
) -> ExecResult:
    argv = ["docker", "exec"]
    if pty:
        argv += ["-it"]
    argv += ["--user", f"{uid}:{uid}"]
    for key in sorted(env):
        argv += ["-e", f"{key}={env[key]}"]
    argv += [container_id] + tail
    return executor(argv, timeout)


def _parse_closed_record(output: bytes) -> dict[str, object]:
    line = extract_record_line(output)
    if line is None:
        raise FixtureError("probe-output-missing")
    try:
        record = json.loads(line)
    except ValueError:
        raise FixtureError("probe-output-malformed") from None
    if not isinstance(record, dict):
        raise FixtureError("probe-output-malformed")
    return record


def _controller_ready(executor: Executor, container_id: str, ledger: _RunLedger) -> int:
    """The fixed 21001 in-container probe (closed expected object:
    PID1 uid, health, exact controller-root facts, exact owned
    existence of every denied target) must match EXACTLY."""
    result = _exec(executor, container_id, CONTROLLER_UID, ["python3", "-c", CONTROLLER_PROBE], {})
    if result.returncode != 0:
        raise FixtureError("controller-not-ready")
    record = _parse_closed_record(result.output)
    # The closed static object must match EXACTLY; the readiness
    # polling count is the single measured field (variable by design,
    # bounded by the probe's own closed 30-second window) and is
    # charged as a DISTINCT ledger quantity.
    if set(record) != set(EXPECTED_CTL_PROBE) | {"healthz_attempts"}:
        raise FixtureError("controller-measurement-mismatch")
    static = {key: value for key, value in record.items() if key != "healthz_attempts"}
    if static != EXPECTED_CTL_PROBE:
        raise FixtureError("controller-measurement-mismatch")
    attempts = record["healthz_attempts"]
    if (
        not isinstance(attempts, int)
        or isinstance(attempts, bool)
        or not 1 <= attempts <= HZ_ATTEMPTS_WORST
    ):
        raise FixtureError("controller-measurement-mismatch")
    ledger.charge_healthz(attempts)
    return attempts


def _inspect_closed(executor: Executor, container_id: str, field: str, expected: str) -> None:
    value = (
        _query(executor, ["docker", "inspect", "--format", field, container_id])
        .decode("ascii", "replace")
        .strip()
    )
    if value != expected:
        raise FixtureError(f"inspect-mismatch:{field}")


def _descendant_count(executor: Executor, container_id: str) -> int:
    """Bounded ``docker top`` process count for the exact owned CID
    (positive-before teardown fact; the header line is excluded)."""
    result = executor(["docker", "top", container_id], _QUERY_TIMEOUT)
    if result.returncode != 0:
        raise FixtureError("top-query-failed")
    lines = [line for line in result.output.decode("ascii", "replace").splitlines() if line.strip()]
    if not lines:
        raise FixtureError("top-query-failed")
    count = len(lines) - 1  # header
    if count < 1 or count > 200:
        raise FixtureError("top-count-untrusted")
    return count


def _standin_record(output: bytes, mode: str, extra_fields: frozenset[str]) -> dict[str, object]:
    """Closed shape check of a slaif-fixture-standin-v1 record."""
    record = _parse_closed_record(output)
    base = {"record", "status", "mode", "uid"}
    if set(record) != base | extra_fields:
        raise FixtureError("standin-record-keys")
    if (
        record["record"] != "slaif-fixture-standin-v1"
        or record["status"] != "pass"
        or record["mode"] != mode
    ):
        raise FixtureError("standin-record-state")
    if record["uid"] != SUBJECT_UID:
        raise FixtureError("standin-record-identity")
    return record


_QUIESCE_PREFIX = b"quiesce-ok "


def _parse_prefixed_record(data: bytes, prefix: bytes) -> dict[str, object]:
    """Parse a closed record carried behind an EXACT fixed wire
    prefix (the export client's ``quiesce-ok `` line): the prefix is
    stripped verbatim and the remainder must be exactly one closed
    JSON object line (a bare ``extract_record_line`` over the whole
    line would drop the prefixed record entirely)."""
    if not data.startswith(prefix):
        raise FixtureError("export-quiesce-state")
    body = data[len(prefix) :]
    if body.count(b"\n") > 1 or b"\r" in body:
        raise FixtureError("probe-output-malformed")
    body = body.split(b"\n", 1)[0].strip()
    if not body:
        raise FixtureError("probe-output-missing")
    try:
        record = json.loads(body.decode("ascii"))
    except (ValueError, UnicodeDecodeError):
        raise FixtureError("probe-output-malformed") from None
    if not isinstance(record, dict):
        raise FixtureError("probe-output-malformed")
    return record


def _tmpfs_spec_facts(spec: str) -> dict[str, str]:
    facts: dict[str, str] = {}
    for part in spec.split(","):
        if "=" in part:
            key, value = part.split("=", 1)
        else:
            key, value = part, ""
        if not key or key in facts:
            raise FixtureError("confinement-tmpfs-spec")
        facts[key] = value
    return facts


def _size_to_bytes(value: str) -> int:
    if value.isdigit():
        return int(value)
    unit = value[-1:]
    mult = {"k": 1024, "m": 1024 * 1024, "g": 1024**3}.get(unit)
    if mult is None or not value[:-1].isdigit():
        raise FixtureError("confinement-tmpfs-spec")
    return int(value[:-1]) * mult


def _verify_confinement(host_config: object, config: object) -> None:
    """The ACTUAL full-confinement verification on the exact CID's
    inspect output: controller identity, exact private network,
    read-only root with ONLY the owned bounded tmpfs budgets, exact
    capability/no-new-privileges/builtin-seccomp (the ACTUAL
    SecurityOpt string list)/memory(no-swap)/PID/CPU values, the
    explicit /dev/shm bound, the actual log-driver field, and the
    ABSENCE of any caller-configured host mounts, devices or volume
    sources (daemon-standard tmpfs facts stay distinct and admitted)."""
    if not isinstance(host_config, dict) or not isinstance(config, dict):
        raise FixtureError("confinement-shape")
    if config.get("User") != f"{CONTROLLER_UID}:{CONTROLLER_UID}":
        raise FixtureError("confinement-user")
    if config.get("Image") != IMAGE_NAME:
        raise FixtureError("confinement-image")
    expected = {
        "NetworkMode": "none",
        "ReadonlyRootfs": True,
        "CapDrop": ["ALL"],
        "Memory": MEMORY_BYTES,
        "MemorySwap": MEMORY_BYTES,
        "PidsLimit": PIDS_LIMIT,
        "NanoCpus": NANOCPUS,
        "Privileged": False,
        "UsernsMode": "",
        "IpcMode": "private",
        "PidMode": "",
        # The explicitly bounded /dev/shm (shared reviewed constant).
        "ShmSize": SHM_SIZE_BYTES,
    }
    for key, value in expected.items():
        if key not in host_config:
            raise FixtureError(f"confinement-missing:{key}")
        if host_config[key] != value:
            raise FixtureError(f"confinement-value:{key}")
    # Go JSON semantics on the ACTUAL inspect output (moby
    # api/types/container/hostconfig.go, v28.5.1: HostConfig embeds
    # Resources; none of these four carries omitempty): the key is
    # ALWAYS present; a nil slice serializes as JSON null, while the
    # docker CLI sends a non-nil EMPTY slice for absent device
    # mappings (cli command/container/opts.go:
    # `deviceMappings := []container.DeviceMapping{}`), which the
    # daemon persists and re-serializes as [].  Both the null and the
    # empty-list shape are the ABSENT state; any configured (non-
    # empty) entry — or any other non-absent type — is a
    # confinement violation.  The device/bind denial is preserved.
    for key in ("Binds", "Devices", "VolumesFrom", "DeviceRequests"):
        if key not in host_config:
            raise FixtureError(f"confinement-missing:{key}")
        value = host_config[key]
        if value is not None:
            if not isinstance(value, list) or len(value) != 0:
                raise FixtureError(f"confinement-value:{key}")
    # The ACTUAL official representation of the security options is
    # HostConfig.SecurityOpt, the list of strings exactly as
    # configured: the no-new-privileges and builtin-seccomp proofs
    # are these entries themselves.  NoNewPrivileges and
    # SeccompProfileName are NOT keys of the official HostConfig
    # schema: when present they must be consistent (never ignored),
    # but their absence can never fail — and an empty SecurityOpt
    # can never be proved by invented fields.
    security_opt = host_config.get("SecurityOpt")
    if not isinstance(security_opt, list) or not all(
        isinstance(item, str) for item in security_opt
    ):
        raise FixtureError("confinement-securityopt")
    if "no-new-privileges:true" not in security_opt:
        raise FixtureError("confinement-no-new-privileges")
    if "seccomp=builtin" not in security_opt:
        raise FixtureError("confinement-seccomp")
    if (
        host_config.get("NoNewPrivileges") is not None
        and host_config["NoNewPrivileges"] is not True
    ):
        raise FixtureError("confinement-value:NoNewPrivileges")
    if (
        host_config.get("SeccompProfileName") is not None
        and host_config["SeccompProfileName"] != "builtin"
    ):
        raise FixtureError("confinement-value:SeccompProfileName")
    # Actual HostConfig.Mounts: caller-configured mounts are
    # prohibited (no-host-mounts/devices contract); the daemon's own
    # standard tmpfs facts (the bounded /dev/shm — and, on some
    # daemon versions, the --tmpfs entries) are distinct from caller
    # mounts and are the only admitted entries.  Any bind, volume or
    # unreviewed type fails closed.
    mounts = host_config.get("Mounts")
    if mounts is not None:
        if not isinstance(mounts, list):
            raise FixtureError("confinement-mounts")
        admitted_targets = set(TMPFS_SPECS) | {"/dev/shm"}
        for entry in mounts:
            if (
                not isinstance(entry, dict)
                or entry.get("Type") != "tmpfs"
                or entry.get("Source") != "tmpfs"
                or entry.get("Target") not in admitted_targets
            ):
                raise FixtureError("confinement-mounts")
    log_config = host_config.get("LogConfig")
    if not isinstance(log_config, dict) or log_config.get("Type") != "none":
        raise FixtureError("confinement-logconfig")
    tmpfs = host_config.get("Tmpfs")
    if not isinstance(tmpfs, dict) or set(tmpfs) != set(TMPFS_SPECS):
        raise FixtureError("confinement-tmpfs-set")
    for mount, spec in tmpfs.items():
        if not isinstance(spec, str):
            raise FixtureError("confinement-tmpfs-spec")
        facts = _tmpfs_spec_facts(spec)
        mount_spec = next(
            (size, uid, gid) for m, size, uid, gid in model.DEFAULT_TMPFS_BUDGETS if m == mount
        )
        if set(facts) != {"rw", "nosuid", "size", "uid", "gid", "mode"}:
            raise FixtureError("confinement-tmpfs-spec")
        if _size_to_bytes(facts["size"]) != mount_spec[0]:
            raise FixtureError("confinement-tmpfs-size")
        if int(facts["uid"]) != mount_spec[1] or int(facts["gid"]) != mount_spec[2]:
            raise FixtureError("confinement-tmpfs-identity")
        if int(facts["mode"], 8) != _TMPFS_MODES[mount]:
            raise FixtureError("confinement-tmpfs-mode")


# -- the ten required scenarios -------------------------------------------------
# Closed per-scenario WORST-CASE provider wire bounds
# (api_requests worst, api_attempts worst), derived from each
# scenario's closed stand-in record fields and the export client's
# closed command sequence (the readiness healthz polling is a
# distinct quantity and is not part of these bounds):
#   controller-measurement  1 no-tools diagnostic POST
#   exec-21002-measurement  none (capability measurement only)
#   pty-attach              none (terminal/profile measurement)
#   synthetic-success       2 stand-in POSTs + quiesce + export
#   synthetic-fail          2 stand-in POSTs (one answered 400)
#   synthetic-hang          none (descendant lifecycle only)
#   synthetic-output-cap    none (bounded capture filler only)
#   export-fail             quiesce + export commands
#   quiesce-fail            quiesce command (refused; no export)
#   controller-crash        none (the controller dies before serving)
# Each bound is RESERVED before the scenario's work and the MEASURED
# facts are charged at its end (an over-reservation is a failure).
_SCENARIO_HTTP_WORST: dict[str, tuple[int, int]] = {
    "controller-measurement": (1, 1),
    "exec-21002-measurement": (0, 0),
    "pty-attach": (0, 0),
    "synthetic-success": (4, 4),
    "synthetic-fail": (2, 2),
    "synthetic-hang": (0, 0),
    "synthetic-output-cap": (0, 0),
    "export-fail": (2, 2),
    "quiesce-fail": (1, 1),
    "controller-crash": (0, 0),
}


def _sc_controller_measurement(executor, index, env_base, created, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "main"
    env["SLAIF_FIXTURE_SCENARIO"] = "diagnostic"
    cid = _new_container(executor, index, "controller-measurement", env)
    created.append(cid)
    _start_container(executor, cid)
    _controller_ready(executor, cid, ledger)
    # Actual inspection of the declared confinement on the exact CID:
    # the real log-driver field (never docker logs), the controller
    # identity, and the full host/config confinement including the
    # absence of any host mounts.
    _inspect_closed(executor, cid, "{{.HostConfig.LogConfig.Type}}", "none")
    _inspect_closed(executor, cid, "{{.Config.User}}", f"{CONTROLLER_UID}:{CONTROLLER_UID}")
    host_config = json.loads(
        _query(executor, ["docker", "inspect", "--format", "{{json .HostConfig}}", cid]).decode(
            "ascii", "replace"
        )
    )
    config = json.loads(
        _query(executor, ["docker", "inspect", "--format", "{{json .Config}}", cid]).decode(
            "ascii", "replace"
        )
    )
    _verify_confinement(host_config, config)
    # The default no-tools diagnostic is ACTUALLY exercised on the
    # live wire (health-only readiness does not count): one request,
    # fixed assistant final text, no tool call.
    result = _exec(
        executor,
        cid,
        SUBJECT_UID,
        ["python3", STANDIN_PATH, "--mode", "diagnostic"],
        dict(env_base),
    )
    if result.returncode != 0:
        raise FixtureError("diagnostic-failed")
    record = _standin_record(
        result.output,
        "diagnostic",
        frozenset({"requests", "attempts", "response_kind", "raw_content_retained"}),
    )
    if record["response_kind"] != "fixed-final-text-no-tools":
        raise FixtureError("diagnostic-record-state")
    # Measured wire facts for the one no-tools diagnostic POST:
    # every answered request is a request; the 200 is admitted.
    ledger.charge_http(
        int(record["attempts"]),
        int(record["attempts"]),
        int(record["requests"]),
        int(record["attempts"]) - int(record["requests"]),
    )
    _SC_FACTS["controller-measurement"] = {
        "requests": record["requests"],
        "attempts": record["attempts"],
    }
    cleanup_container(executor, cid)
    return "completed"


def _sc_exec_measurement(executor, index, env_base, created, parent, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "main"
    env["SLAIF_FIXTURE_SCENARIO"] = "tool-cycle"
    cid = _new_container(executor, index, "exec-21002-measurement", env)
    created.append(cid)
    _start_container(executor, cid)
    _controller_ready(executor, cid, ledger)
    measure_env = _standin_env(env, *parent)
    measure_env["SLAIF_FIXTURE_TMPFS_SPECS"] = TMPFS_SPEC_ENV
    measure_env["SLAIF_FIXTURE_EXPECTED_CPU"] = str(model.CPU_LIMIT)
    measure_env["SLAIF_FIXTURE_PRESENCE_SHA256"] = PRESENCE_SHA256
    result = _exec(
        executor, cid, SUBJECT_UID, ["python3", STANDIN_PATH, "--mode", "measure"], measure_env
    )
    if result.returncode != 0:
        raise FixtureError("exec-measurement-failed")
    record = _parse_closed_record(result.output)
    model.validate_exec_measurement(record, model.FixtureBudgets())
    # Closed facts retained for the runner facts line (measured,
    # never raw): swap source, the keyring denial errnos and the
    # reconciled writable-data facts (carried closed into the CI
    # summary — the measured mount table facts, not an argv claim).
    _SC_FACTS["exec-21002-measurement"] = {
        "swap_source": record["swap_source"],
        "keyring_errno": record["keyring_errno"],
        "memory_limit_bytes": record["memory_limit_bytes"],
        "pids_limit": record["pids_limit"],
        "cpu_limit": record["cpu_limit"],
        "writable_mounts": record["writable_mounts"],
        "mounts_scanned": record["mounts_scanned"],
    }
    cleanup_container(executor, cid)
    return "completed"


def _sc_pty_attach(executor, index, env_base, created, run_token: str, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "main"
    env["SLAIF_FIXTURE_SCENARIO"] = "tool-cycle"
    cid = _new_container(executor, index, "pty-attach", env)
    created.append(cid)
    _start_container(executor, cid)
    _controller_ready(executor, cid, ledger)
    pty_env = dict(env_base)
    pty_env["SLAIF_RUN_TOKEN"] = run_token
    result = _exec(
        executor, cid, SUBJECT_UID, ["python3", STANDIN_PATH, "--mode", "pty"], pty_env, pty=True
    )
    if result.returncode != 0:
        raise FixtureError("pty-attach-failed")
    record = _standin_record(
        result.output,
        "pty",
        frozenset(
            {"pty_attached", "term_rows", "term_cols", "terminal_properties_closed_only", "profile"}
        ),
    )
    if record["pty_attached"] is not True or record["terminal_properties_closed_only"] is not True:
        raise FixtureError("pty-record-state")
    for key in ("term_rows", "term_cols"):
        if not isinstance(record[key], int) or isinstance(record[key], bool) or record[key] < 0:
            raise FixtureError("pty-record-state")
    # The host allocated the terminal at the fixed closed size; the
    # measured size must agree (the attachment is actual, not flag-only).
    if record["term_rows"] != PTY_ROWS or record["term_cols"] != PTY_COLS:
        raise FixtureError("pty-term-mismatch")
    profile = record["profile"]
    model.validate_profile_record(profile)
    if (
        profile["profile_table_used"] is not False
        or profile["profile_file"] != "early-beta.config.toml"
        or profile["env_key_name"] != "SLAIF_SYNTHETIC_API_KEY"
    ):
        raise FixtureError("profile-record-state")
    _SC_FACTS["pty-attach"] = {
        "pty_attached": True,
        "profile_file": profile["profile_file"],
        "profile_sha256": profile["profile_sha256"],
        "profile_table_used": False,
    }
    cleanup_container(executor, cid)
    return "completed"


def _sc_synthetic_success(executor, index, env_base, created, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "main"
    env["SLAIF_FIXTURE_SCENARIO"] = "tool-cycle"
    cid = _new_container(executor, index, "synthetic-success", env)
    created.append(cid)
    _start_container(executor, cid)
    _controller_ready(executor, cid, ledger)
    # -- the stand-in drives the REAL controller wire (2 requests) --
    result = _exec(
        executor, cid, SUBJECT_UID, ["python3", STANDIN_PATH, "--mode", "success"], dict(env_base)
    )
    if result.returncode != 0:
        raise FixtureError("synthetic-success-failed")
    record = _standin_record(
        result.output,
        "success",
        frozenset(
            {
                "issued_count",
                "issued_calls",
                "sse_wire",
                "final_text_fixed",
                "raw_content_retained",
                "requests",
                "attempts",
            }
        ),
    )
    issued = record["issued_calls"]
    if not isinstance(issued, list) or len(issued) < 2 or record["issued_count"] != len(issued):
        raise FixtureError("synthetic-issued-shape")
    seen: set[str] = set()
    for entry in issued:
        if not isinstance(entry, dict) or set(entry) != {"family", "name", "call_id"}:
            raise FixtureError("synthetic-issued-shape")
        if (
            entry["family"] != "function"
            or entry["name"] not in model.KNOWN_TOOL_NAMES
            or not isinstance(entry["call_id"], str)
            or entry["call_id"] in seen
        ):
            raise FixtureError("synthetic-issued-shape")
        seen.add(entry["call_id"])
    if (
        record["sse_wire"] != "responses"
        or record["final_text_fixed"] is not True
        or record["raw_content_retained"] is not False
    ):
        raise FixtureError("synthetic-record-state")
    # -- quiesce -> 21001 export WHILE THE CONTAINER STILL EXISTS --
    export_result = _exec(
        executor, cid, CONTROLLER_UID, ["python3", EXPORT_CLIENT_PATH], dict(env_base)
    )
    if export_result.returncode != 0:
        raise FixtureError("success-export-failed")
    data = export_result.output
    i1 = data.find(b"\n")
    i2 = data.find(b"\n", i1 + 1)
    if i1 < 0 or i2 < 0:
        raise FixtureError("export-shape")
    line1, line2, payload = data[:i1], data[i1 + 1 : i2], data[i2 + 1 :]
    if not line1.startswith(b"quiesce-ok "):
        raise FixtureError("export-quiesce-state")
    quiesce_record = _parse_prefixed_record(line1, _QUIESCE_PREFIX)
    model.validate_quiesce_record(quiesce_record)
    if not line2.startswith(b"export-sha256 "):
        raise FixtureError("export-shape")
    declared_sha = line2[len(b"export-sha256 ") :].decode("ascii", "replace")
    if (
        not re.fullmatch(r"[0-9a-f]{64}", declared_sha)
        or declared_sha != hashlib.sha256(payload).hexdigest()
    ):
        raise FixtureError("export-sha-mismatch")
    # -- HOST INDEPENDENT closed-object revalidation (the client's
    # proof is not the host's) --
    try:
        selected = fixture_export.validate_payload(payload)
    except (ValueError, model.FixtureError):
        # A payload that fails the closed-object proof is a fixed
        # host failure (the raw payload is never reflected).
        raise FixtureError("export-invalid") from None
    snapshot = selected["snapshot"]
    # -- ISSUED BINDING revalidation against the CLOSED derivation
    # (never the child's echo): the expected bindings are re-derived
    # from the stand-in's closed fixed request and the controller's
    # single-source call-id / argument-digest derivation; a changed,
    # missing or extra binding field is a fixed failure.  The
    # stand-in's OBSERVED issuance must agree with the same closed
    # derivation, and the exported diagnostic/position must match
    # the closed expected metadata observation (the first admitted
    # POST is position 0 on a fresh controller).
    expected_payload = fixture_standin._fixed_request(fixture_standin._synthetic_tools())
    expected_bindings = []
    for bind_index, entry in enumerate(expected_payload["tools"]):
        if not isinstance(entry, dict) or entry.get("type") != "function":
            continue
        name = entry.get("name")
        if not isinstance(name, str) or name not in model.KNOWN_TOOL_NAMES:
            continue
        expected_bindings.append(
            {
                "family": "function",
                "name": name,
                "call_id": fixture_controller.expected_call_id(name, 0, bind_index),
                "position": 0,
                "arguments_sha256": fixture_controller.expected_arguments_sha256(name),
            }
        )
    if snapshot["issued_calls"] != expected_bindings:
        raise FixtureError("export-identity-mismatch")
    if [
        {"family": entry["family"], "name": entry["name"], "call_id": entry["call_id"]}
        for entry in issued
    ] != [
        {"family": binding["family"], "name": binding["name"], "call_id": binding["call_id"]}
        for binding in expected_bindings
    ]:
        raise FixtureError("export-identity-mismatch")
    if (
        selected["diagnostic"] != model.bounds_diagnostic(expected_payload)
        or selected["observed_at_position"] != 0
    ):
        raise FixtureError("export-identity-mismatch")
    # -- trusted-controller reconciliation: the controller's OWN
    # ledger (exported with the snapshot) must count exactly the
    # stand-in's POSTs plus the two exporter commands (quiesce +
    # export): an independent observation, not the child's echo --
    if snapshot["controller_ledger"]["requests"] != int(record["attempts"]) + 2:
        raise FixtureError("controller-ledger-mismatch")
    # -- MEASURED wire charge: stand-in POSTs + quiesce + export
    #    (both exporter commands received closed responses, so both
    #    are admitted outcomes here) --
    ledger.charge_http(
        int(record["attempts"]) + 2,
        int(record["attempts"]) + 2,
        int(record["requests"]) + 2,
        int(record["attempts"]) - int(record["requests"]),
    )
    # -- exact CID/descendant teardown VERIFIED, then publish --
    descendants_before = _descendant_count(executor, cid)
    cleanup_container(executor, cid)
    _SC_FACTS["synthetic-success"] = {
        "issued_count": len(issued),
        "export_sha256": hashlib.sha256(payload).hexdigest(),
        "quiesce": "closed-pass",
        "export_revalidated": True,
        "standin_requests": record["requests"],
        "standin_attempts": record["attempts"],
        "controller_ledger_requests": snapshot["controller_ledger"]["requests"],
        "retained_capture_bytes": len(payload),
    }
    _SC_EXPORT["payload"] = payload
    _SC_EXPORT["quiesce_record"] = quiesce_record
    _SC_TEARDOWN["cid"] = cid
    _SC_TEARDOWN["descendants_before"] = descendants_before
    return "completed"


def _sc_synthetic_fail(executor, index, env_base, created, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "main"
    env["SLAIF_FIXTURE_SCENARIO"] = "tool-cycle"
    cid = _new_container(executor, index, "synthetic-fail", env)
    created.append(cid)
    _start_container(executor, cid)
    _controller_ready(executor, cid, ledger)
    result = _exec(
        executor, cid, SUBJECT_UID, ["python3", STANDIN_PATH, "--mode", "fail"], dict(env_base)
    )
    if result.returncode != 3:
        raise FixtureError("synthetic-fail-undeclared")
    record = _standin_record(
        result.output,
        "fail",
        frozenset({"provider_state", "raw_content_retained", "requests", "attempts"}),
    )
    if record["provider_state"] != "unissued" or record["raw_content_retained"] is not False:
        raise FixtureError("synthetic-fail-state")
    # Measured wire facts: two answered POSTs (issuance 200 + the
    # refused foreign-result 400); the refused call IS a request
    # with a refused outcome.
    ledger.charge_http(
        int(record["attempts"]),
        int(record["attempts"]),
        int(record["requests"]),
        int(record["attempts"]) - int(record["requests"]),
    )
    _SC_FACTS["synthetic-fail"] = {
        "exit_code": 3,
        "provider_state": "unissued",
        "requests": record["requests"],
        "attempts": record["attempts"],
    }
    cleanup_container(executor, cid)
    return "failed-as-designed"


def _sc_synthetic_hang(executor, index, env_base, created, sentinel_process, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "main"
    env["SLAIF_FIXTURE_SCENARIO"] = "tool-cycle"
    cid = _new_container(executor, index, "synthetic-hang", env)
    created.append(cid)
    _start_container(executor, cid)
    _controller_ready(executor, cid, ledger)
    hang_token = uuid.uuid4().hex
    hang_env = dict(env_base)
    hang_env["SLAIF_HANG_TOKEN"] = hang_token
    try:
        _exec(
            executor,
            cid,
            SUBJECT_UID,
            ["python3", STANDIN_PATH, "--mode", "hang"],
            hang_env,
            timeout=HANG_TIMEOUT,
        )
        raise FixtureError("hang-did-not-timeout")
    except _OwnedTimeout as exc:
        partial = exc.partial_output
    record = _standin_record(
        partial,
        "hang",
        frozenset(
            {
                "descendant_pid",
                "descendant_starttime",
                "descendant_token",
                "pre_hold_record_flushed",
            }
        ),
    )
    if record["descendant_token"] != hang_token or record["pre_hold_record_flushed"] is not True:
        raise FixtureError("hang-record-state")
    dpid = record["descendant_pid"]
    dstart = record["descendant_starttime"]
    if (
        not isinstance(dpid, int)
        or isinstance(dpid, bool)
        or dpid < 1
        or not isinstance(dstart, int)
        or isinstance(dstart, bool)
        or dstart < 1
    ):
        raise FixtureError("hang-record-state")
    # 2) PRE-termination POSITIVE: exactly one live owned occurrence
    #    (subject uid + exact token) observed in the host /proc.
    if _count_uid_marker_processes(SUBJECT_UID, hang_token) != 1:
        raise FixtureError("descendant-not-observed")
    # 3) the EXACT owned stopper through the reviewed pidfd path:
    #    fresh identity verification, pidfd-bound SIGTERM, no
    #    numeric-PID fallback (executed as the subject uid 21002).
    stop_env = dict(env_base)
    stop_env["SLAIF_STOP_TOKEN"] = hang_token
    stop_env["SLAIF_STOP_PID"] = str(dpid)
    stop_env["SLAIF_STOP_STARTTIME"] = str(dstart)
    stop_result = _exec(
        executor, cid, SUBJECT_UID, ["python3", STANDIN_PATH, "--mode", "stop-owned"], stop_env
    )
    if stop_result.returncode != 0:
        raise FixtureError("stop-owner-failed")
    stop_record = _standin_record(
        stop_result.output,
        "stop-owned",
        frozenset({"stopped_exactly_one", "same_uid_only", "starttime_verified"}),
    )
    if (
        stop_record["stopped_exactly_one"] is not True
        or stop_record["same_uid_only"] is not True
        or stop_record["starttime_verified"] is not True
    ):
        raise FixtureError("stop-record-state")
    # 4) POST-termination: the exact occurrence is GONE, the
    #    unrelated parent sentinel survives.
    if _count_uid_marker_processes(SUBJECT_UID, hang_token) != 0:
        raise FixtureError("descendant-leftover")
    if sentinel_process.poll() is not None:
        raise FixtureError("sentinel-process-died")
    _SC_FACTS["synthetic-hang"] = {
        "host_timeout": True,
        "descendant_terminated": True,
        "stopper": "pass",
        "sentinel_survived": True,
    }
    cleanup_container(executor, cid)
    return "timed-out-as-designed"


def _sc_output_cap(executor, index, env_base, created, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "main"
    env["SLAIF_FIXTURE_SCENARIO"] = "tool-cycle"
    cid = _new_container(executor, index, "synthetic-output-cap", env)
    created.append(cid)
    _start_container(executor, cid)
    _controller_ready(executor, cid, ledger)
    result = _exec(
        executor,
        cid,
        SUBJECT_UID,
        ["python3", STANDIN_PATH, "--mode", "output-cap"],
        dict(env_base),
    )
    if result.returncode != 0:
        raise FixtureError("output-cap-failed")
    # The finite bounded capture was HIT: the stand-in flushed the
    # closed record first, then emitted filler past the cap.
    if len(result.output) != OUTPUT_CAP:
        raise FixtureError("output-cap-not-hit")
    record = _standin_record(
        result.output, "output-cap", frozenset({"record_flushed_before_filler"})
    )
    if record["record_flushed_before_filler"] is not True:
        raise FixtureError("output-cap-state")
    _SC_FACTS["synthetic-output-cap"] = {"capture_bytes": OUTPUT_CAP, "cap_hit": True}
    cleanup_container(executor, cid)
    return "cap-hit-as-designed"


def _sc_export_fail(executor, index, env_base, created, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "export-fail"
    env["SLAIF_FIXTURE_SCENARIO"] = "tool-cycle"
    cid = _new_container(executor, index, "export-fail", env)
    created.append(cid)
    _start_container(executor, cid)
    _controller_ready(executor, cid, ledger)
    result = _exec(executor, cid, CONTROLLER_UID, ["python3", EXPORT_CLIENT_PATH], dict(env_base))
    if result.returncode != 2:
        raise FixtureError("export-fail-undeclared")
    lines = [line for line in result.output.split(b"\n") if line.strip()]
    if len(lines) != 2 or not lines[0].startswith(b"quiesce-ok "):
        raise FixtureError("export-fail-undeclared")
    quiesce_record = _parse_prefixed_record(lines[0], _QUIESCE_PREFIX)
    model.validate_quiesce_record(quiesce_record)
    if lines[1].strip() != b"export-fail export-invalid":
        raise FixtureError("export-fail-undeclared")
    # Measured wire facts: quiesce answered (admitted) + export
    # command answered with an invalid frame (refused outcome).
    ledger.charge_http(2, 2, 1, 1)
    _SC_FACTS["export-fail"] = {"reason": "export-invalid"}
    cleanup_container(executor, cid)
    return "failed-as-designed"


def _sc_quiesce_fail(executor, index, env_base, created, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "quiesce-fail"
    env["SLAIF_FIXTURE_SCENARIO"] = "tool-cycle"
    cid = _new_container(executor, index, "quiesce-fail", env)
    created.append(cid)
    _start_container(executor, cid)
    _controller_ready(executor, cid, ledger)
    result = _exec(executor, cid, CONTROLLER_UID, ["python3", EXPORT_CLIENT_PATH], dict(env_base))
    if result.returncode != 2:
        raise FixtureError("quiesce-fail-undeclared")
    lines = [line for line in result.output.decode("utf-8", "replace").splitlines() if line.strip()]
    # NO closed quiesce record is ever produced; the export client
    # publishes nothing but the fixed reason.
    if lines != ["export-fail quiesce-state"]:
        raise FixtureError("quiesce-fail-undeclared")
    # Measured wire facts: the quiesce command received a closed
    # refusal answer (a request with a refused outcome; no export
    # command was ever sent).
    ledger.charge_http(1, 1, 0, 1)
    _SC_FACTS["quiesce-fail"] = {"reason": "quiesce-state"}
    cleanup_container(executor, cid)
    return "failed-as-designed"


def _sc_controller_crash(executor, index, env_base, created, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "crash"
    env["SLAIF_FIXTURE_SCENARIO"] = "diagnostic"
    cid = _new_container(executor, index, "controller-crash", env)
    created.append(cid)
    _start_container(executor, cid)
    wait = executor(["docker", "wait", cid], CRASH_WAIT_TIMEOUT)
    if wait.returncode != 0:
        raise FixtureError("crash-wait-failed")
    exit_code = wait.output.decode("ascii", "replace").strip()
    if exit_code != "137":
        raise FixtureError("crash-code-mismatch")
    _SC_FACTS["controller-crash"] = {"exit_code": 137}
    cleanup_container(executor, cid)
    return "crashed-as-designed"


# -- the run ---------------------------------------------------------------------
def _existing_ancestor_trusted(mode: int, owner_uid: int, self_uid: int) -> bool:
    """The explicit trust rule for an EXISTING intermediate evidence
    ancestor (protected-path convention, review 23):

    - current-uid ancestry: ordinary home/traversal directories need
      not all be 0700 — admitted when not group/other-writable and
      owner-traversable (0700 is demanded on the private leaf and on
      the state this invocation creates, never on pre-existing
      shared traversal);
    - root-owned ancestry: the explicitly trusted system ancestry
      (/, /home, /usr, ...); a root-owned writable shared root is
      admitted only with the sticky bit (the POSIX /tmp convention —
      sticky protects entries from other unprivileged users, not
      from the directory owner, so owner identity is what matters);
    - arbitrary foreign (non-root) owners: never trusted — owner-
      write remains set, so the owner can rename/swap entries, and
      the owner also controls a sticky directory.
    """
    if owner_uid == self_uid:
        return not (mode & (stat.S_IWGRP | stat.S_IWOTH)) and bool(mode & stat.S_IXUSR)
    if owner_uid == 0:
        if not mode & stat.S_IXOTH:
            return False
        writable = mode & (stat.S_IWGRP | stat.S_IWOTH)
        return not writable or bool(mode & stat.S_ISVTX)
    return False


def _retain_evidence(dest, payload: bytes, digest: str, work) -> str:
    """Atomically retain the published 0600 evidence at an explicit
    protected destination OUTSIDE the disposable work root: the
    published file inside the scratch root is never the only copy of
    the reviewable evidence (the scratch root is destroyed at the
    end of the run).

    The destination and every ancestor are validated AS GIVEN (no
    lexical ``.``/``..`` folding, no symlink resolution before the
    walk, the same protected-path convention as the work root): a
    traversal component, a link alias, a current-uid
    group/other-writable intermediate ancestor, a non-root-owned
    (arbitrary foreign) ancestor, or a root-owned sticky-less
    writable / non-traversable ancestor is refused; current-uid
    non-writable traversal ancestry (ordinary 0755 home/work
    directories) and root-owned system ancestry (0755, or writable
    WITH the sticky bit — the POSIX /tmp convention) are admitted
    without any chmod or runner-ownership demand, while 0700 is
    demanded on the private leaf and on every component this
    invocation creates; no pre-existing untrusted object is ever
    adopted and no pre-existing state is ever chmod'd (a missing
    parent chain is created fresh 0700 by this invocation).  The destination must not lie inside
    the disposable work root (such a copy would be destroyed with
    the scratch and reported retained dishonestly), and an existing
    final destination is refused, never overwritten.  The bytes go
    to a fresh 0600 same-directory temporary file; the complete
    byte/digest checks finish BEFORE the atomic final commit
    (same-directory rename).  A failed write, digest or
    pre-publication step removes only the temporary object this
    invocation demonstrably owns: the final destination is either
    absent or the verified committed file — a partial or wrong
    final file is never left behind."""
    from pathlib import Path

    dest = Path(dest)
    if not dest.is_absolute():
        dest = Path(os.getcwd()) / dest
    work = Path(work)
    if not work.is_absolute():
        work = Path(os.getcwd()) / work
    # The retained copy must OUTLIVE the scratch root: a destination
    # at or under the disposable work root is refused outright.
    try:
        dest.relative_to(work)
    except ValueError:
        pass
    else:
        raise FixtureError("evidence-inside-work")
    if dest.exists() or dest.is_symlink():
        raise FixtureError("evidence-exists")
    if ".." in dest.parts or "." in dest.parts:
        raise FixtureError("evidence-path-untrusted")
    current = Path("/")
    for part in dest.parts[1:-1]:
        candidate = current / part
        # AS-GIVEN alias check on every level (a link anywhere in the
        # chain launders the validated path).  Then the EXPLICIT
        # trust rule for pre-existing intermediate ancestors
        # (_existing_ancestor_trusted): current-uid traversal
        # ancestry (ordinary home/work directories, e.g. the hosted
        # /home/runner/work/_temp chain) is admitted when not
        # group/other-writable — 0700 is demanded only on the
        # private leaf and on state this invocation creates;
        # root-owned ancestry is the explicitly trusted system
        # ancestry (a root-owned writable shared root admitted only
        # with the sticky bit, the POSIX /tmp convention); arbitrary
        # foreign (non-root) owners are never trusted because
        # owner-write lets them rename/swap entries (and they
        # control their own sticky directory).  No pre-existing
        # state is ever chmod'd.
        if candidate.is_symlink():
            raise FixtureError("evidence-path-untrusted")
        if candidate.exists() and not candidate.is_dir():
            raise FixtureError("evidence-path-untrusted")
        if not candidate.is_dir():
            candidate.mkdir()
            os.chmod(candidate, stat.S_IRWXU)
            st = candidate.lstat()
            if stat.S_IMODE(st.st_mode) != stat.S_IRWXU or st.st_uid != os.getuid():
                raise FixtureError("evidence-ancestor-untrusted")
        else:
            st = candidate.lstat()
            if not _existing_ancestor_trusted(stat.S_IMODE(st.st_mode), st.st_uid, os.getuid()):
                raise FixtureError("evidence-ancestor-untrusted")
        current = candidate
    parent = dest.parent
    st = parent.lstat()
    if stat.S_IMODE(st.st_mode) != stat.S_IRWXU or st.st_uid != os.getuid():
        raise FixtureError("evidence-parent-untrusted")
    tmp = dest.with_name(dest.name + ".tmp-" + uuid.uuid4().hex)
    tmp_owned = False
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        tmp_owned = True
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
        if stat.S_IMODE(tmp.lstat().st_mode) != (stat.S_IRUSR | stat.S_IWUSR):
            raise FixtureError("evidence-tmp-mode")
        if sha256_file(tmp) != digest:
            raise FixtureError("evidence-digest")
        # ATOMIC NO-OVERWRITE COMMIT: os.link fails with
        # FileExistsError if a destination appears between the early
        # existence check and this commit — the concurrent bytes are
        # preserved, the owned temp is cleaned up, and the fixed
        # refuse-overwrite reason is raised.  An overwriting rename
        # would violate the refuse-overwrite contract.
        try:
            os.link(tmp, dest)
        except FileExistsError:
            raise FixtureError("evidence-exists") from None
        try:
            os.unlink(tmp)
        except OSError:
            if os.path.lexists(str(tmp)):
                raise FixtureError("evidence-tmp-cleanup-failed") from None
        tmp_owned = False
    finally:
        if tmp_owned:
            try:
                os.unlink(tmp)
            except OSError:
                pass
    if stat.S_IMODE(dest.lstat().st_mode) != (stat.S_IRUSR | stat.S_IWUSR):
        raise FixtureError("evidence-mode")
    if sha256_file(dest) != digest:
        raise FixtureError("evidence-digest")
    return str(dest)


def run(repo, work, executor, evidence_out=None) -> dict[str, object]:
    """The complete disposable-CI fixture run.  Returns the closed
    summary object (already model-validated) on success; raises a
    fixed-reason FixtureError on any failure.  EVERY host command
    passes the guarded executor (closed allowlist + shared deadline
    + host ledger) from the collision check through cleanup; EVERY
    owned resource (image, containers, sentinel, listener) is
    registered before its lifecycle mutation; and EVERY failure path
    — collision, preflight, build, setup, scenario, deadline expiry
    or publication — converges through the same bounded exact-owned
    cleanup.  The published evidence is retained at an explicit
    protected destination before the disposable work root is
    destroyed."""
    from pathlib import Path

    repo = Path(repo)
    work = Path(work)
    _SC_FACTS.clear()
    _SC_EXPORT.clear()
    _SC_TEARDOWN.clear()

    # -- ONE shared non-resettable run deadline (host + in-container) --
    deadline = _RunDeadline(time.monotonic() + TOTAL_ANCHOR_SECONDS)
    budgets = model.FixtureBudgets()
    ledger = _RunLedger(budgets)
    # The guarded + ledgered executor is the ONLY execution path for
    # EVERY host command, starting BEFORE any docker query.
    guarded = _guarded_execute(executor, deadline, ledger)

    # -- Reviewed Dockerfile base (byte-identical to the repo base) --
    dockerfile_path = repo / "scripts" / "cache_native_fixture.Dockerfile"
    if not dockerfile_path.is_file():
        raise FixtureError("dockerfile-missing")
    dockerfile_bytes = dockerfile_path.read_bytes()
    base_literal = b"python:3.12-slim-bookworm@sha256:"
    embedded = [
        line.split(b"FROM ", 1)[1].strip()
        for line in dockerfile_bytes.splitlines()
        if line.startswith(b"FROM ")
    ]
    if len(embedded) != 1 or not embedded[0].startswith(base_literal):
        raise FixtureError("dockerfile-base-unpinned")
    digest_hex = embedded[0].split(b"@sha256:")[1].decode("ascii")
    if not re.fullmatch(r"[0-9a-f]{64}", digest_hex):
        raise FixtureError("dockerfile-base-unpinned")
    reference = (repo / "Dockerfile").read_bytes()
    if embedded[0] not in reference:
        raise FixtureError("dockerfile-base-mismatch")

    # -- Static NO-codex proof (sources + workflow fixture job) ------
    _static_no_codex_invocation(repo)

    # Owned-resource registration state (registered BEFORE any
    # lifecycle mutation can reference them; initialized here so the
    # cleanup umbrella's finally body can reference every name on
    # ANY failure path, including early preparation failures).  The
    # intended FRESH owned image tag is registered here: pre-existing
    # state under it is rejected (never adopted), and the cleanup
    # path may only ever operate on objects verified as this owned
    # tag/id.
    owned_image_tag = IMAGE_NAME
    created_containers: list[str] = []
    scenarios: dict[str, str] = {}
    cleanup_error: FixtureError | None = None
    image_state = "absent-verified"  # until the build claims the tag
    cleanup_failures: list[str] = []
    sentinel_survived = False
    owned_image_id: str | None = None
    build_attempted = False
    sentinel_process: subprocess.Popen[bytes] | None = None
    listener: socket.socket | None = None
    sentinel_file: Path | None = None
    sentinel_file_digest: str | None = None
    parent_pid: int | None = None
    parent_port: int | None = None
    parent_ns: dict[str, str] | None = None
    run_token = ""
    artifact: dict[str, object] | None = None
    work_root_owned = False

    def _remove_owned_image(image_id: str) -> None:
        """Remove the EXACT owned image id and verify the outcome:
        still-present and daemon/query-failure are DISTINCT recorded
        cleanup failures (a failed query is never verified absence)."""
        nonlocal image_state
        rmi = guarded(["docker", "rmi", image_id], _QUERY_TIMEOUT)
        if rmi.returncode != 0:
            cleanup_failures.append("image-rmi-failed")
            return
        inspect_result = guarded(["docker", "image", "inspect", image_id], _QUERY_TIMEOUT)
        if inspect_result.returncode == 0:
            cleanup_failures.append("image-still-present")
            image_state = "present-unexpected"
        elif _NO_SUCH_OBJECT_RE.search(inspect_result.output.decode("ascii", "replace")):
            image_state = "absent-verified"
        else:
            cleanup_failures.append("image-absence-unverified")
            image_state = "query-failed-unverified"

    def _record_sweep_failure(where: str, exc: Exception) -> None:
        """Record an HONEST unverified cleanup outcome.  A timed-out
        capture is already measured: the guarded executor charged its
        drained bytes to the non-resettable host ledger exactly once
        before re-raising, so recording here charges nothing again.
        A failed or timed-out cleanup query is never reported as
        verified absence, and the recorded reason is exposed (on the
        preserved primary or as the run failure) — never swallowed."""
        if isinstance(exc, _OwnedTimeout):
            cleanup_failures.append(f"{where}:timeout-unverified")
        elif isinstance(exc, OSError):
            cleanup_failures.append(f"{where}:operational-unverified")
        else:
            cleanup_failures.append(f"{where}:{exc}")

    try:
        try:
            # -- Fresh owned protected scratch namespace (owned from
            #    this point on: EVERY later failure path converges
            #    through the cleanup umbrella that destroys exactly
            #    this registered fresh root) --
            _create_work_root(work)
            work_root_owned = True
            context = _owned_subdir(work, "context")
            artifact_dir = _owned_subdir(work, "artifact")

            # -- Public pinned artifact (size+digest verified,
            #    bounded; LICENSE and NOTICE byte-identity verified) --
            artifact = fetch_public_artifact(artifact_dir, deadline)

            # -- Build context: Dockerfile + sources + binary +
            #    license + notice (every copy byte-verified) --
            (context / "Dockerfile").write_bytes(dockerfile_bytes)
            for name in (
                "cache_native_fixture_model.py",
                "cache_native_fixture_controller.py",
                "cache_native_fixture_standin.py",
                "cache_native_fixture_export_client.py",
            ):
                src = (repo / "scripts" / name).read_bytes()
                (context / name).write_bytes(src)
                if sha256_file(context / name) != hashlib.sha256(src).hexdigest():
                    raise FixtureError("context-mismatch")
            shutil.copyfile(
                artifact_dir / model.ARTIFACT_BINARY_NAME, context / model.ARTIFACT_BINARY_NAME
            )
            if sha256_file(context / model.ARTIFACT_BINARY_NAME) != artifact["binary_sha256"]:
                raise FixtureError("context-mismatch")
            shutil.copyfile(artifact_dir / "LICENSE", context / "codex-0.164.0-license.txt")
            if sha256_file(context / "codex-0.164.0-license.txt") != artifact["license_sha256"]:
                raise FixtureError("context-mismatch")
            shutil.copyfile(artifact_dir / "NOTICE", context / "codex-0.164.0-notice.txt")
            if sha256_file(context / "codex-0.164.0-notice.txt") != artifact["notice_sha256"]:
                raise FixtureError("context-mismatch")

            env_base = {
                "SLAIF_FIXTURE_DEADLINE_ABS": repr(deadline.anchor),
                "SLAIF_FIXTURE_DEADLINE": str(int(TOTAL_ANCHOR_SECONDS)),
                "SLAIF_FIXTURE_PORT": str(CONTROLLER_PORT),
            }

            # -- Pre-existing image collision: never adopt, never
            #    overwrite (verified absence or fixed failure) --
            probe = guarded(
                ["docker", "inspect", "--format", "{{.Id}}", owned_image_tag], _QUERY_TIMEOUT
            )
            if probe.returncode == 0:
                raise FixtureError("image-collision")
            if not _NO_SUCH_OBJECT_RE.search(probe.output.decode("ascii", "replace")):
                raise FixtureError("image-collision-unverified")
            # The owned fresh tag is now exclusively ours: verified
            # absent before build (the registration fact).

            # -- Engine preflight (through the guard): version +
            #    seccomp + runtime identity, reviewed bare-name query
            engine_version, runtime_name, runtime_version = _engine_preflight(guarded)

            # -- Build the fixture image (pinned base, public pull) --
            result = guarded(["docker", "pull", PINNED_BASE], PULL_TIMEOUT)
            if result.returncode != 0:
                raise FixtureError("pull-failed")
            build_attempted = True
            result = guarded(
                ["docker", "build", "-t", owned_image_tag, str(context)], BUILD_TIMEOUT
            )
            if result.returncode != 0:
                raise FixtureError("build-failed")
            image_id = (
                _query(guarded, ["docker", "inspect", "--format", "{{.Id}}", owned_image_tag])
                .decode("ascii", "replace")
                .strip()
            )
            if not _IMAGE_ID_RE.fullmatch(image_id):
                raise FixtureError("build-failed")
            owned_image_id = image_id

            # -- Owned synthetic parent sentinels (no real parent
            #    data), inside the cleanup umbrella.
            sentinels = _owned_subdir(work, "sentinels")
            sentinel_file = sentinels / "parent-sentinel-file"
            sentinel_fd = os.open(sentinel_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(sentinel_fd, "wb") as handle:
                handle.write(b"slaif-synthetic-parent-sentinel-017r\n")
            sentinel_file_digest = sha256_file(sentinel_file)
            listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listener.bind(("127.0.0.1", 0))
            listener.listen(1)
            parent_port = listener.getsockname()[1]
            parent_pid = os.getpid()
            parent_ns = parent_namespace_ids()
            sentinel_process = _spawn_parent_sentinel()
            run_token = uuid.uuid4().hex

            for index, (name, _required) in enumerate(model.REQUIRED_SCENARIOS):
                # PRE-WORK: the scenario's closed worst-case wire
                # bound must fit the REMAINING API budgets before
                # any of its work may start (an over-budget scenario
                # never begins its wire work).
                ledger.reserve_http(*_SCENARIO_HTTP_WORST[name])
                if name == "controller-measurement":
                    state = _sc_controller_measurement(
                        guarded, index, env_base, created_containers, ledger
                    )
                elif name == "exec-21002-measurement":
                    assert parent_pid is not None
                    assert parent_port is not None
                    assert sentinel_file is not None
                    assert parent_ns is not None
                    state = _sc_exec_measurement(
                        guarded,
                        index,
                        env_base,
                        created_containers,
                        (parent_pid, parent_port, sentinel_file, parent_ns),
                        ledger,
                    )
                elif name == "pty-attach":
                    state = _sc_pty_attach(
                        guarded, index, env_base, created_containers, run_token, ledger
                    )
                elif name == "synthetic-success":
                    state = _sc_synthetic_success(
                        guarded, index, env_base, created_containers, ledger
                    )
                elif name == "synthetic-fail":
                    state = _sc_synthetic_fail(guarded, index, env_base, created_containers, ledger)
                elif name == "synthetic-hang":
                    assert sentinel_process is not None
                    state = _sc_synthetic_hang(
                        guarded, index, env_base, created_containers, sentinel_process, ledger
                    )
                elif name == "synthetic-output-cap":
                    state = _sc_output_cap(guarded, index, env_base, created_containers, ledger)
                elif name == "export-fail":
                    state = _sc_export_fail(guarded, index, env_base, created_containers, ledger)
                elif name == "quiesce-fail":
                    state = _sc_quiesce_fail(guarded, index, env_base, created_containers, ledger)
                else:  # controller-crash
                    state = _sc_controller_crash(
                        guarded, index, env_base, created_containers, ledger
                    )
                scenarios[name] = state
                # (The MEASURED per-container wire facts were charged
                # into the shared ledger at the scenario's own end,
                # before the next scenario's pre-work reservation.)
                # The unrelated parent sentinel must be ALIVE after
                # every scenario (measured, never assumed).
                assert sentinel_process is not None
                if sentinel_process.poll() is not None:
                    raise FixtureError("sentinel-process-died")
                assert sentinel_file is not None
                assert sentinel_file_digest is not None
                if sha256_file(sentinel_file) != sentinel_file_digest:
                    raise FixtureError("sentinel-changed")
            verify_no_leftovers(guarded, IMAGE_NAME)
        except FixtureError as exc:
            cleanup_error = exc
        finally:
            # Teardown/cleanup for EVERY path (success, scenario
            # failure, setup failure, deadline expiry): the explicit
            # one-time bounded grace, then every INDEPENDENT owned
            # resource is attempted — an earlier cleanup failure
            # never skips the rest — and each unverified result is
            # reported.
            deadline.add_grace(600.0, "cleanup")
            # MEASURED before the intentional reap (never overwritten):
            # a prematurely dead sentinel is a recorded cleanup
            # failure, not a silent True.
            if sentinel_process is not None:
                sentinel_survived = sentinel_process.poll() is None
                if not sentinel_survived:
                    cleanup_failures.append("sentinel-died")
            if listener is not None:
                try:
                    listener.close()
                except OSError:
                    cleanup_failures.append("listener-cleanup-failed")
            for cid in created_containers:
                try:
                    cleanup_container(guarded, cid)
                except (FixtureError, _OwnedTimeout, OSError) as exc:
                    _record_sweep_failure("container-cleanup", exc)
            # -- owned image: the exact owned id when registered;
            #    otherwise — when the build was attempted but the ID
            #    discovery missed (deadline expiry / query failure)
            #    — the owned FRESH TAG (exclusively ours: verified
            #    absent before build) is inspected under the single
            #    cleanup grace to recover the id and attempt the
            #    exact removal.  An unresolvable ownership is an
            #    HONEST unverified cleanup failure with the attempt
            #    proven, never a silent skip and never a successful
            #    convergence on a known built image.
            if owned_image_id is not None:
                try:
                    _remove_owned_image(owned_image_id)
                except (FixtureError, _OwnedTimeout, OSError) as exc:
                    _record_sweep_failure("image-cleanup", exc)
            elif build_attempted:
                try:
                    probe = guarded(
                        ["docker", "inspect", "--format", "{{.Id}}", owned_image_tag],
                        _QUERY_TIMEOUT,
                    )
                    if probe.returncode == 0:
                        recovered = probe.output.decode("ascii", "replace").strip()
                        if _IMAGE_ID_RE.fullmatch(recovered):
                            _remove_owned_image(recovered)
                        else:
                            cleanup_failures.append("image-recovery-unverified")
                            image_state = "query-failed-unverified"
                    else:
                        if _NO_SUCH_OBJECT_RE.search(probe.output.decode("ascii", "replace")):
                            # the build left no image behind:
                            # verified absence
                            image_state = "absent-verified"
                        else:
                            cleanup_failures.append("image-recovery-unverified")
                            image_state = "query-failed-unverified"
                except (FixtureError, _OwnedTimeout, OSError) as exc:
                    _record_sweep_failure("image-cleanup", exc)
            # (build never attempted: the pre-build verified absence
            # of the owned tag remains the registered fact)
            if sentinel_process is not None:
                try:
                    sentinel_process.kill()
                    sentinel_process.wait(timeout=_LEADER_REAP_SECONDS)
                except (OSError, subprocess.TimeoutExpired):
                    cleanup_failures.append("sentinel-cleanup-failed")
                if sentinel_process.poll() is None:
                    cleanup_failures.append("sentinel-cleanup-failed")

            # A non-FixtureError in flight (e.g. a cancelled host /
            # KeyboardInterrupt) is PRESERVED — never replaced, and
            # never swallowed into a success by the publish path —
            # but a failed cleanup is exposed on it honestly.
            if cleanup_failures:
                primary = sys.exc_info()[1]
                if primary is not None and not isinstance(primary, FixtureError):
                    reason = ";".join(sorted(set(cleanup_failures)))
                    primary.args = (
                        f"{primary.args[0] if primary.args else type(primary).__name__};{reason}",
                    )

        if cleanup_failures:
            reason = ";".join(sorted(set(cleanup_failures)))
            if cleanup_error is not None:
                raise FixtureError(f"{cleanup_error};{reason}")
            raise FixtureError(reason)
        if cleanup_error is not None:
            raise cleanup_error

        # -- teardown-verified, THEN publish (phase order) ------------
        # Descendants negative-after: no fixture-uid process remains
        # in the host /proc after the exact-owned sweep.
        if (
            _count_fixture_uid_processes(CONTROLLER_UID) != 0
            or _count_fixture_uid_processes(SUBJECT_UID) != 0
        ):
            raise FixtureError("descendant-leftover")
        _SC_TEARDOWN["descendants_after"] = 0

        export_payload = _SC_EXPORT.get("payload")
        if not isinstance(export_payload, bytes) or not export_payload:
            raise FixtureError("export-missing")
        if len(export_payload) > budgets.max_export_bytes:
            raise FixtureError("export-overbound")
        export_sha = hashlib.sha256(export_payload).hexdigest()

        deadline_expired = False
        try:
            deadline.remaining()
        except FixtureError:
            deadline_expired = True

        # -- Closed records: built and validated BEFORE publication --
        if artifact is None:
            raise FixtureError("artifact-missing")
        artifact_record = {
            "record": model.SCHEMA_ARTIFACT,
            "tag": model.ARTIFACT_TAG,
            "commit": model.ARTIFACT_COMMIT,
            "archive_sha256": model.ARTIFACT_ARCHIVE_SHA256,
            "archive_size": model.ARTIFACT_ARCHIVE_SIZE,
            "binary_name": model.ARTIFACT_BINARY_NAME,
            "binary_sha256": artifact["binary_sha256"],
            "binary_size": artifact["binary_size"],
            "license": model.ARTIFACT_LICENSE,
            "license_sha256": artifact["license_sha256"],
            "notice": model.ARTIFACT_NOTICE,
            "notice_sha256": artifact["notice_sha256"],
            "signature_verification": model.SIGNATURE_VERIFICATION,
        }
        model.validate_artifact_record(artifact_record)

        cid = _SC_TEARDOWN.get("cid")
        if not isinstance(cid, str) or not _is_cid(cid):
            raise FixtureError("teardown-cid-missing")
        descendants_before = _SC_TEARDOWN.get("descendants_before")
        if (
            not isinstance(descendants_before, int)
            or isinstance(descendants_before, bool)
            or descendants_before < 1
        ):
            raise FixtureError("teardown-facts-missing")
        teardown_record = {
            "record": model.SCHEMA_TEARDOWN,
            "cid": cid,
            "container_present_before": True,
            "container_inspect_after": "absent-verified",
            "image_present_before": True,
            "image_inspect_after": image_state,
            "descendants_before": descendants_before,
            "descendants_after": 0,
            # MEASURED before the intentional reap above (any scenario
            # that observed the sentinel's death raised a fixed
            # failure, and the pre-reap poll was the recorded fact).
            "sentinel_survived": sentinel_survived,
            "export_completed_before_teardown": True,
        }
        model.validate_teardown_record(teardown_record)

        # Measured aggregate provider accounting across ALL scenarios
        # and containers: the shared non-resettable ledger charged
        # each scenario's MEASURED closed per-container facts at the
        # scenario's end (pre-work reservations enforced the bounds
        # before the work), so its counters ARE the aggregate (no
        # hardcoded totals, no relabelled byte counts).  The distinct
        # quantities stay distinct: api_requests vs api_attempts vs
        # admitted/refused outcomes vs healthz polling vs host
        # command admissions; drained vs retained bytes.
        _SC_FACTS["ledger"] = {
            "docker_admissions": ledger.admissions,
            "docker_refusals": ledger.refusals,
            "bytes_drained": ledger.bytes_drained,
            "bytes_retained": ledger.bytes_retained,
            "api_requests": ledger.api_requests,
            "api_attempts": ledger.api_attempts,
            "requests_admitted": ledger.requests_admitted,
            "requests_refused": ledger.requests_refused,
            "healthz_attempts": ledger.healthz_attempts,
        }

        # The publish record is fully closed and validated BEFORE the
        # evidence bytes are written (the post-write mode/digest
        # checks are the publication evidence, not first validation).
        publish_record = {
            "record": model.SCHEMA_PUBLISH,
            "publish_dir_mode": 0o700,
            "artifact_file_mode": 0o600,
            "artifact_sha256": export_sha,
            "snapshot_digest_match": True,
            "api_requests": ledger.api_requests,
            "api_attempts": ledger.api_attempts,
            "requests_admitted": ledger.requests_admitted,
            "requests_refused": ledger.requests_refused,
            "healthz_attempts": ledger.healthz_attempts,
            "docker_admissions": ledger.admissions,
            "docker_refusals": ledger.refusals,
            "bytes_drained": ledger.bytes_drained,
            "bytes_retained": ledger.bytes_retained,
            "deadline_expired": deadline_expired,
        }
        model.validate_publish_record(publish_record, budgets)

        summary = {
            "record": model.SCHEMA_CI_SUMMARY,
            "scenarios": [{"name": name, "state": state} for name, state in scenarios.items()],
            "container_removal": "absent-verified",
            "image_removal": image_state,
            "export_sha256": export_sha,
            "codex_invoked": False,
            "api_requests": ledger.api_requests,
            "api_attempts": ledger.api_attempts,
            "requests_admitted": ledger.requests_admitted,
            "requests_refused": ledger.requests_refused,
            "healthz_attempts": ledger.healthz_attempts,
            "docker_admissions": ledger.admissions,
            "docker_refusals": ledger.refusals,
            "bytes_drained": ledger.bytes_drained,
            "bytes_retained": ledger.bytes_retained,
            # The measured reconciled writable-data surface, carried
            # closed from the validated 21002 measurement (the
            # actual mount-table facts, not the argv claim).
            "writable_mounts": _SC_FACTS["exec-21002-measurement"]["writable_mounts"],
            "writable_data_total_bytes": sum(
                entry["size_bytes"]
                for entry in _SC_FACTS["exec-21002-measurement"]["writable_mounts"]
            ),
            "deadline_expired": deadline_expired,
        }
        model.validate_ci_summary(summary)

        # Atomic 0700/0600 publication (0600 BEFORE any write).
        publish_dir = _owned_subdir(work, "publish")
        artifact_file = publish_dir / "selected-evidence.json"
        tmp_file = publish_dir / "selected-evidence.json.tmp"
        fd = os.open(tmp_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(export_payload)
        os.replace(tmp_file, artifact_file)
        dir_mode = stat.S_IMODE(publish_dir.lstat().st_mode)
        file_mode = stat.S_IMODE(artifact_file.lstat().st_mode)
        if dir_mode != 0o700 or file_mode != 0o600:
            raise FixtureError("publish-mode")
        if sha256_file(artifact_file) != export_sha:
            raise FixtureError("publish-digest")
        if (
            dir_mode != publish_record["publish_dir_mode"]
            or file_mode != publish_record["artifact_file_mode"]
        ):
            raise FixtureError("publish-mode")

        # Retain the reviewable evidence OUTSIDE the disposable work
        # root before that root is destroyed.
        retained_out: str | None = None
        if evidence_out is not None:
            retained_out = _retain_evidence(Path(evidence_out), export_payload, export_sha, work)

        uname = platform.uname()
        return {
            "schema": SCHEMA,
            "status": "pass",
            "summary": summary,
            "artifact": artifact_record,
            "teardown": teardown_record,
            "publish": publish_record,
            "engine_version": engine_version,
            "runtime_name": runtime_name,
            "runtime_version": runtime_version,
            "base_image": PINNED_BASE,
            "image_id": image_id,
            "runner_kernel": uname.release,
            "runner_arch": uname.machine,
            "runner_python": platform.python_version(),
            "scenarios_detail": _SC_FACTS,
            "codex_invoked": False,
            "cleanup_exact_only": True,
            "no_leftover_containers": True,
            "image_removed": image_state == "absent-verified",
            "evidence_out": retained_out,
        }
    finally:
        # The disposable scratch root is destroyed last (the retained
        # evidence copy already lives at its protected destination).
        # ONLY the exact registered fresh root is destroyed (never a
        # pre-existing root); the result is VERIFIED, and a failed
        # destruction is exposed honestly while the primary failure
        # (if any) is preserved — never replaced or hidden.
        if work_root_owned and not _destroy_owned_work_root(work):
            primary = sys.exc_info()[1]
            if primary is None:
                raise FixtureError("work-cleanup-failed") from None
            if isinstance(primary, FixtureError):
                primary.args = (f"{primary.args[0]};work-cleanup-failed",)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="repository checkout root")
    parser.add_argument("--work", required=True, help="fresh owned disposable work root")
    parser.add_argument(
        "--evidence-out",
        default=None,
        help="explicit protected destination (0700 dir/0600 file, "
        "runner-created) where the published evidence is "
        "retained outside the disposable work root",
    )
    args = parser.parse_args(argv)
    if os.environ.get("GITHUB_ACTIONS") != "true":
        print(
            json.dumps({"schema": SCHEMA, "status": "fail", "reason": "not-a-disposable-ci-runner"})
        )
        return 1
    if os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted":
        print(json.dumps({"schema": SCHEMA, "status": "fail", "reason": "not-a-hosted-ci-runner"}))
        return 1
    try:
        result = run(
            Path(args.repo), Path(args.work), _real_execute, evidence_out=args.evidence_out
        )
    except FixtureError as exc:
        print(json.dumps({"schema": SCHEMA, "status": "fail", "reason": str(exc)}))
        return 1
    except Exception:
        print(json.dumps({"schema": SCHEMA, "status": "fail", "reason": "internal"}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
