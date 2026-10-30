#!/usr/bin/env python3
"""Disposable-CI containment capability runner (objective 017-p).

Runs ONLY on a disposable GitHub-hosted runner (never the protected
development/Qwen host; the main entry refuses any context that is not
both ``GITHUB_ACTIONS=true`` and ``RUNNER_ENVIRONMENT=github-hosted``).
Builds the minimal digest-pinned fixture image, creates owned
synthetic parent sentinels (file, unix socket, ephemeral loopback
listener, a parent-owned sentinel process) plus the parent namespace
identities, and drives three container scenarios under the explicit
confinement:

- ``--network none`` (private net namespace, own loopback only);
- read-only root filesystem with ONLY the owned bounded writable
  tmpfs roots (explicitly selected, rw-filtered, ``k``-suffixed);
- dedicated nonroot UID/GID, all capabilities dropped,
  ``no-new-privileges``;
- the EXPLICIT builtin seccomp policy (never unconfined or
  daemon-custom-by-assumption);
- bounded memory (no swap), PID, CPU and writable-storage limits.

Ownership/lifecycle law: each scenario uses a FRESH container name
plus an ownership label and is created with ``docker create`` so the
actual returned CID (bare 64-hex) is validated and registered as
owned BEFORE any start; a pre-existing name collision is a fixed
failure (never adopted, never removed).  Every cleanup removes only
registered owned IDs and verifies absence through a successful
bounded authority query, distinguishing verified absence from a
daemon/query failure (cleanup uncertainty is a recorded failure,
never swallowed as no-orphans).

Scenarios: ``success`` (closed-schema pass record, exit 0), ``fail``
(deliberate probe failure after the checks, exit 3) and ``hang``
(the probe spawns a per-run token-bound live owned descendant and
reports it in the closed record; the host-side bounded timeout then
proves the parent-death case IN ORDER: one exact owned occurrence
positively observed BEFORE the registered container is killed, its
disappearance and the container's verified absence AFTER, the
unrelated parent-owned sentinel surviving).

Output discipline: every docker invocation is argv-based (no shell),
its output is captured BOUNDED (cap, drain, discard) with exact
owned process-group cleanup (a leader that exits while an owned
descendant still holds the pipe is group-killed after a bounded
grace, and the pipe fd is owned by the reader thread alone, so the
runner can never block on a cross-thread buffer lock), and only the
closed JSON schemas defined here ever reach the workflow log — never
raw container inspect dumps, env dumps, arbitrary child output or
exception strings.  Image removal is result-checked and its absence
verified only by a successful authoritative query reporting no such
image/object (a daemon or query failure is a distinct unverified
state, never conflated with absence); cleanup failures stay visible
even when a primary check also failed.  A fail-closed reason is a
fixed enum.
No genuine client, model, GPU, provider or Gateway activity; stdlib
only; this job is the containment capability proof, not genuine
native-client qualification (D09 remains NOT RUN).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import signal
import socket
import stat
import subprocess
import sys
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import IO

SCHEMA = "slaif-cache-native-containment-ci-v1"
PROBE_SCHEMA = "slaif-cache-native-containment-probe-v1"
# Exact digest-pinned Python 3.12 base, byte-identical to the
# repository Dockerfile's runtime base (copied, not transcribed).
PINNED_BASE = (
    "python:3.12-slim-bookworm"
    "@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254"
)
IMAGE_NAME = "slaif-containment-probe:local"
PROBE_UID = 21001
PROBE_GID = 21001
MEMORY_BYTES = 512 * 1024 * 1024  # <= 512 MiB, no swap
PIDS_LIMIT = 64
NANOCPUS = 1_000_000_000  # <= 1 CPU
TMPFS_SPECS = {
    "/tmp": "rw,noexec,nosuid,size=32768k,mode=1777",
    "/run": "rw,nosuid,size=8192k,mode=755",
    "/dev/shm": "rw,nosuid,size=16384k,mode=1777",
}
TMPFS_TOTAL_BYTES = (32768 + 8192 + 16384) * 1024  # <= 64 MiB combined
OUTPUT_CAP = 1 * 1024 * 1024  # bounded child/docker output capture
RUN_TIMEOUT = 300.0
HANG_TIMEOUT = 20.0
BUILD_TIMEOUT = 600.0
PULL_TIMEOUT = 600.0
_QUERY_TIMEOUT = 60.0
_READER_GRACE_SECONDS = 5.0  # normal exit: drain grace before group kill
_READER_RECOVERY_SECONDS = 10.0  # after group kill: bounded convergence
_LEADER_REAP_SECONDS = 10.0  # bounded reap of the session leader
_CONTAINER_ID_RE = re.compile(r"^[0-9a-f]{64}$")  # bare 64-hex (no sha256:)
_IMAGE_ID_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_PYTHON_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?\Z")
_KERNEL_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:-\d+[0-9A-Za-z.-]*)?\Z")
_ENGINE_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?\Z")
_RUNTIME_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_RUNTIME_PATH_RE = re.compile(r"^/[A-Za-z0-9._/-]{1,254}$")
_RUNTIME_VERSION_RE = re.compile(
    r"^(?P<name>[a-z0-9][a-z0-9._-]{0,63}) version "
    r"(?P<version>\d+\.\d+(?:\.\d+)?(?:[-+][0-9A-Za-z.+-]+)?)\Z"
)
_DESCENDANT_TOKEN_RE = re.compile(r"^[0-9a-f]{32}$")
# The docker CLI's authoritative missing-object marker: verified
# absence requires a SUCCESSFUL query that reports no such
# image/object; a daemon or transport failure (no marker) is a
# distinct unverified state, never absence.
_NO_SUCH_OBJECT_RE = re.compile(r"no such (?:image|object)", re.IGNORECASE)
_NS_NAMES = ("pid", "mnt", "ipc", "uts", "net", "user", "cgroup")

# Unrelated parent-owned sentinel process marker (survives the hang
# scenario's container teardown; killed by the runner at the end).
# NOTE: the -c body must import time itself; a bare time.sleep would
# NameError and the sentinel would die before the scenario runs.
PARENT_SENTINEL_MARKER = "import time; time.sleep(600) # slaif-parent-sentinel-017p"

EXPECTED_CHECKS = frozenset(
    {
        "dedicated_nonroot_uid_gid",
        "no_supplementary_groups",
        "capabilities_all_zero",
        "no_new_privs",
        "seccomp_filter_mode",
        "private_pid_namespace",
        "namespace_ids_differ_from_parent",
        "user_namespace_shared",
        "parent_proc_absent",
        "parent_sentinels_absent",
        "private_netns_loopback_only",
        "private_loopback_echo_ok",
        "parent_listener_unreachable",
        "rootfs_read_only_denied",
        "tmpfs_write_ok",
        "memory_limit_exact",
        "swap_disabled",
        "pids_limit_exact",
        "writable_storage_limit_exact",
        "keyring_syscalls_denied",
        "child_deadline_kill_ok",
    }
)
EXPECTED_MEASURED = (
    "memory_limit_bytes",
    "swap_limit_bytes",
    "swap_limit_source",
    "pids_limit",
    "writable_storage_bytes",
    "writable_mount_count",
    "keyring_errno_add_key",
    "keyring_errno_request_key",
    "keyring_errno_keyctl",
)
_EXPECTED_MEASURED_VALUES = {
    "memory_limit_bytes": MEMORY_BYTES,
    "swap_limit_bytes": 0,
    "pids_limit": PIDS_LIMIT,
    "writable_storage_bytes": TMPFS_TOTAL_BYTES,
    "writable_mount_count": len(TMPFS_SPECS),
    "keyring_errno_add_key": 1,  # EPERM: policy denial before any lookup
    "keyring_errno_request_key": 1,
    "keyring_errno_keyctl": 1,
}


class ContainmentError(RuntimeError):
    """Fail-closed runner error carrying a fixed reason enum only."""


@dataclass(frozen=True)
class ExecResult:
    returncode: int
    output: bytes  # bounded (<= OUTPUT_CAP + one chunk), rest discarded


Executor = Callable[[list[str], float], ExecResult]


class _OwnedTimeout(subprocess.TimeoutExpired):
    """Host deadline carrying the bounded partial captured output.

    The hang scenario needs the probe's pre-timeout record (its
    token-bound descendant facts) even though the attached CLI was
    killed at the deadline; the partial output is bounded exactly
    like any other capture.
    """

    def __init__(self, cmd: list[str], timeout: float, partial_output: bytes) -> None:
        super().__init__(cmd, timeout)
        self.partial_output = partial_output


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_bounded_output(stream: IO[bytes], cap: int) -> bytes:
    """Read a byte stream keeping at most ``cap`` bytes; discard the rest."""
    kept = bytearray()
    while True:
        chunk = stream.read(65536)
        if not chunk:
            break
        if len(kept) < cap:
            kept.extend(chunk[: cap - len(kept)])
        # else: drain and discard (bounded memory)
    return bytes(kept)


def extract_probe_line(data: bytes) -> str | None:
    """Return the last non-empty JSON-ish line (closed-schema candidate)."""
    lines = [
        line
        for line in data.decode("utf-8", "replace").splitlines()
        if line.strip().startswith("{")
    ]
    return lines[-1] if lines else None


def validate_probe_record(
    data: object,
    expected_probe_digest: str,
    expected_mode: str,
    expected_token: str | None = None,
) -> dict[str, object]:
    """Closed-schema validation of the probe's pass record (fail closed)."""
    if not isinstance(data, dict):
        raise ContainmentError("probe-record-not-object")
    top_keys = {
        "schema",
        "status",
        "mode",
        "platform",
        "cgroup_version",
        "cgroup_namespace_differs",
        "python_version",
        "kernel_release",
        "probe_source_sha256",
        "checks",
        "measured",
    }
    if expected_mode == "hang":
        # The hang record additionally carries the live owned
        # descendant's (container-internal) pid and the exact per-run
        # token the host uses to bind the occurrence in /proc.
        top_keys |= {"descendant_pid", "descendant_token"}
        if expected_token is None or not _DESCENDANT_TOKEN_RE.fullmatch(expected_token):
            raise ContainmentError("hang-token-invalid")
    if set(data) != top_keys:
        raise ContainmentError("probe-record-keys")
    if data["schema"] != PROBE_SCHEMA:
        raise ContainmentError("probe-record-schema")
    if data["status"] != "pass":
        raise ContainmentError("probe-record-status")
    if data["mode"] != expected_mode:
        raise ContainmentError("probe-record-mode")
    if data["platform"] != "linux-x86_64":
        raise ContainmentError("probe-record-platform")
    if data["cgroup_version"] not in ("v1", "v2"):
        raise ContainmentError("probe-record-cgroup")
    if not isinstance(data["cgroup_namespace_differs"], bool):
        raise ContainmentError("probe-record-cgroup-ns-type")
    if not isinstance(data["python_version"], str) or not _PYTHON_VERSION_RE.fullmatch(
        data["python_version"]
    ):
        raise ContainmentError("probe-record-python-version")
    if not isinstance(data["kernel_release"], str) or not _KERNEL_VERSION_RE.fullmatch(
        data["kernel_release"]
    ):
        raise ContainmentError("probe-record-kernel-release")
    digest = data["probe_source_sha256"]
    if (
        not isinstance(digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
        or digest != expected_probe_digest
    ):
        raise ContainmentError("probe-record-digest")
    checks = data["checks"]
    if not isinstance(checks, dict) or set(checks) != EXPECTED_CHECKS:
        raise ContainmentError("probe-checks-keys")
    for name, ok in checks.items():
        if not isinstance(ok, bool) or not ok:
            raise ContainmentError(f"probe-check-failed:{name}")
    measured = data["measured"]
    if not isinstance(measured, dict) or set(measured) != set(EXPECTED_MEASURED):
        raise ContainmentError("probe-measured-keys")
    for name, expected in _EXPECTED_MEASURED_VALUES.items():
        value = measured[name]
        if not isinstance(value, int) or isinstance(value, bool) or value != expected:
            raise ContainmentError(f"probe-measured-mismatch:{name}")
    # The swap fact must be a MEASURED finite value whose source
    # matches the record's cgroup version: v2 swap-only
    # (memory.swap.max) or v1 combined memsw (memsw - memory).  A
    # missing/underivable measurement is a fixed failure here, never
    # a measured zero.
    swap_source = measured["swap_limit_source"]
    expected_swap_source = "v2-swap-max" if data["cgroup_version"] == "v2" else "v1-memsw-combined"
    if not isinstance(swap_source, str) or swap_source != expected_swap_source:
        raise ContainmentError("probe-measured-mismatch:swap_limit_source")
    if expected_mode == "hang":
        pid = data["descendant_pid"]
        if not isinstance(pid, int) or isinstance(pid, bool) or pid < 1:
            raise ContainmentError("probe-record-descendant-pid")
        token = data["descendant_token"]
        if (
            not isinstance(token, str)
            or not _DESCENDANT_TOKEN_RE.fullmatch(token)
            or token != expected_token
        ):
            raise ContainmentError("probe-record-descendant-token")
    return data


def validate_inspect_record(data: object, expected_exit_code: int) -> None:
    """Closed extraction from the exact documented inspect fields.

    ``data`` is the closed subset extracted from the container's
    ``HostConfig``/``Config``/``State`` JSON (the actual HostConfig
    field is ``ReadonlyRootfs``); key names here are this runner's
    closed output vocabulary.
    """
    if not isinstance(data, dict):
        raise ContainmentError("inspect-not-object")
    expected = {
        "NetworkMode": "none",
        "ReadOnlyRootfs": True,
        "SecurityOpt": ["no-new-privileges:true", "seccomp=builtin"],
        "CapDrop": ["ALL"],
        "User": f"{PROBE_UID}:{PROBE_GID}",
        "PidsLimit": PIDS_LIMIT,
        "Memory": MEMORY_BYTES,
        "MemorySwap": MEMORY_BYTES,
        "NanoCpus": NANOCPUS,
        "Tmpfs": dict(TMPFS_SPECS),
        "ExitCode": expected_exit_code,
        "Running": False,
    }
    if set(data) != set(expected):
        raise ContainmentError("inspect-keys")
    for key, want in expected.items():
        got = data[key]
        if key == "SecurityOpt":
            if (
                not isinstance(got, list)
                or not isinstance(want, list)
                or sorted(got) != sorted(want)
            ):
                raise ContainmentError(f"inspect-mismatch:{key}")
        elif key == "Tmpfs":
            if not isinstance(got, dict) or got != want:
                raise ContainmentError(f"inspect-mismatch:{key}")
        elif got != want:
            raise ContainmentError(f"inspect-mismatch:{key}")


def extract_inspect_facts(host_config: object, config: object, state: object) -> dict[str, object]:
    """Closed extraction of the documented fields from inspect JSON."""
    if (
        not isinstance(host_config, dict)
        or not isinstance(config, dict)
        or not isinstance(state, dict)
    ):
        raise ContainmentError("inspect-not-object")
    return {
        "NetworkMode": host_config.get("NetworkMode"),
        "ReadOnlyRootfs": host_config.get("ReadonlyRootfs"),
        "SecurityOpt": host_config.get("SecurityOpt"),
        "CapDrop": host_config.get("CapDrop"),
        "User": config.get("User"),
        "PidsLimit": host_config.get("PidsLimit"),
        "Memory": host_config.get("Memory"),
        "MemorySwap": host_config.get("MemorySwap"),
        "NanoCpus": host_config.get("NanoCpus"),
        "Tmpfs": host_config.get("Tmpfs"),
        "ExitCode": state.get("ExitCode"),
        "Running": state.get("Running"),
    }


def build_run_conf_argv(
    image_ref: str, name: str, owned_label: str, env: dict[str, str]
) -> list[str]:
    """The exact confinement create-argv (no shell, no host mounts, no secrets)."""
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
        f"{PROBE_UID}:{PROBE_GID}",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges:true",
        "--security-opt",
        "seccomp=builtin",
        "--memory",
        str(MEMORY_BYTES),
        "--memory-swap",
        str(MEMORY_BYTES),
        "--pids-limit",
        str(PIDS_LIMIT),
        "--cpus",
        "1",
    ]
    for mountpoint, spec in sorted(TMPFS_SPECS.items()):
        argv += ["--tmpfs", f"{mountpoint}:{spec}"]
    for key in sorted(env):
        argv += ["-e", f"{key}={env[key]}"]
    argv.append(image_ref)
    return argv


def _kill_process_group(proc: subprocess.Popen[bytes]) -> None:
    """Kill the exact owned process group (CLI + owned descendants)."""
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.kill()
        except (ProcessLookupError, OSError):
            pass


def _real_execute(argv: list[str], timeout: float) -> ExecResult:
    """Run an argv list with bounded output capture and owned-group cleanup.

    The child runs in its own session so a timeout kills the exact
    owned process group (docker CLI plus any owned descendants such
    as build workers).  The stdout pipe is owned by the reader
    thread ALONE: it reads, bounds, drains and closes the fd, so the
    parent never closes a BufferedReader another thread may be
    reading (no cross-thread lock can hang the runner).  A leader
    that exits while an owned descendant still holds the write side
    is handled on EVERY path by a bounded grace join followed by the
    exact owned group kill — the pipe closes, the reader converges,
    and no reader or owned descendant is left behind; a
    non-converging drain is a recorded failure, never an empty
    output presented as complete.
    A capture read failure is caught in the reader and reported to
    the parent as the fixed closed state ``output-read-failed``: it
    never escapes as an uncaught thread exception (raw text leak)
    and never degrades into an empty-success ExecResult.
    """
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
            capture["data"] = read_bounded_output(pipe, OUTPUT_CAP)
        except Exception as exc:  # closed fixed state for the parent
            # A failed capture must never surface as an uncaught
            # thread exception (raw exception text through the
            # default hook) nor as an empty-success output.
            capture["error"] = exc
        finally:
            # This thread alone owns the pipe fd after start.
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
            # Host deadline: kill the exact owned group, reap the
            # leader, converge the bounded drain, then re-raise with
            # the partial captured output attached.
            _kill_process_group(proc)
            try:
                proc.wait(timeout=_LEADER_REAP_SECONDS)
            except subprocess.TimeoutExpired:
                raise ContainmentError("process-cleanup-failed") from None
            reader.join(timeout=_READER_RECOVERY_SECONDS)
            if reader.is_alive():
                raise ContainmentError("process-cleanup-failed") from None
            if "error" in capture:
                raise ContainmentError("output-read-failed") from None
            partial = capture.get("data", b"")
            assert isinstance(partial, bytes)
            raise _OwnedTimeout(argv, timeout, partial) from None
        # Leader exited.  An owned descendant may still hold the
        # write side: bounded grace, then the exact owned group kill
        # so the pipe closes and the reader converges.
        reader.join(timeout=_READER_GRACE_SECONDS)
        if reader.is_alive():
            _kill_process_group(proc)
            reader.join(timeout=_READER_RECOVERY_SECONDS)
            if reader.is_alive():
                raise ContainmentError("process-cleanup-failed") from None
        if "error" in capture:
            raise ContainmentError("output-read-failed") from None
    finally:
        if proc.poll() is None:
            _kill_process_group(proc)
        try:
            proc.wait(timeout=_LEADER_REAP_SECONDS)
        except subprocess.TimeoutExpired:
            pass
    data = capture.get("data", b"")
    assert isinstance(data, bytes)
    return ExecResult(returncode, data)


def _query(executor: Executor, argv: list[str]) -> bytes:
    result = executor(argv, _QUERY_TIMEOUT)
    if result.returncode != 0:
        raise ContainmentError("query-failed")
    return result.output


def _ps_filter(executor: Executor, filter_arg: str) -> str:
    """``absent`` | ``present`` | ``query-failed`` (never conflated).

    Verified absence requires a SUCCESSFUL bounded authority query
    (``docker ps -aq --filter <filter>`` returning empty); a daemon
    or query failure is a distinct state the caller must treat as a
    cleanup uncertainty.
    """
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
        raise ContainmentError("cleanup-query-failed")
    if state == "absent":
        return
    result = executor(["docker", "rm", "-f", container_id], _QUERY_TIMEOUT)
    if result.returncode != 0:
        raise ContainmentError("cleanup-failed")
    if _ps_filter(executor, f"id={container_id}") != "absent":
        raise ContainmentError("cleanup-failed")


def verify_no_leftovers(executor: Executor, image_ref: str) -> None:
    """No container (running or stopped) may remain for the built image."""
    result = executor(["docker", "ps", "-aq", "--filter", f"ancestor={image_ref}"], _QUERY_TIMEOUT)
    if result.returncode != 0:
        raise ContainmentError("leftover-query-failed")
    if result.output.strip():
        raise ContainmentError("leftover-container")


def parent_namespace_ids() -> dict[str, str]:
    """The disposable parent's own namespace identities (read-only)."""
    return {name: os.readlink(f"/proc/self/ns/{name}") for name in _NS_NAMES}


def _create_work_root(work: Path) -> None:
    """Create a FRESH owned 0700 scratch root (never adopt/overwrite).

    The path is validated AS GIVEN: no lexical ``.``/``..`` folding
    and no symlink resolution are applied before the walk (folding
    would launder a symlinked ancestor such as ``link/../work`` into
    a clean-looking alias of a pre-existing target), so
    parent-traversal components are rejected outright.  Every
    existing component must be a real, non-symlink directory, so a
    symlink anywhere in the chain cannot relocate the new root into
    an untrusted or pre-existing location, and the validated path is
    the exact path subsequent steps use.  The final component must
    not pre-exist (in any form); only it is created, owned by the
    current uid, with mode exactly 0700.  Existing objects and
    modes are preserved untouched.
    """
    if not os.path.isabs(str(work)):
        work = Path(os.path.join(os.getcwd(), str(work)))
    if ".." in work.parts or "." in work.parts:
        raise ContainmentError("work-root-untrusted")
    current = Path("/")
    for part in work.parts[1:-1]:
        candidate = current / part
        if candidate.is_symlink():
            raise ContainmentError("work-root-untrusted")
        if not candidate.is_dir():
            raise ContainmentError("work-root-untrusted")
        current = candidate
    if not current.is_dir() or current.is_symlink():
        raise ContainmentError("work-root-untrusted")
    path = current / work.parts[-1]
    if path.exists() or path.is_symlink():
        raise ContainmentError("work-root-exists")
    path.mkdir()
    os.chmod(path, stat.S_IRWXU)
    st = path.lstat()
    if stat.S_IMODE(st.st_mode) != stat.S_IRWXU or st.st_uid != os.getuid():
        raise ContainmentError("work-root-untrusted")


def _owned_subdir(work: Path, name: str) -> Path:
    path = work / name
    if path.exists() or path.is_symlink():
        raise ContainmentError("work-root-exists")
    path.mkdir()
    os.chmod(path, stat.S_IRWXU)
    return path


def _spawn_parent_sentinel() -> subprocess.Popen[bytes]:
    """Unrelated parent-owned sentinel process (must survive teardown)."""
    return subprocess.Popen(
        [sys.executable, "-c", PARENT_SENTINEL_MARKER],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _count_marker_processes(uid: int, marker: str) -> int:
    """Bounded read-only /proc count of exact uid + marker occurrences.

    A vanished entry (FileNotFoundError mid-scan) is expected churn
    in teardown windows; ANY other read error means the scan did not
    observe the whole namespace, so the count is not evidence of
    absence — that is a recorded scan failure, never a silent zero.
    """
    count = 0
    try:
        entries = [entry for entry in os.listdir("/proc") if entry.isdigit()]
    except OSError:
        raise ContainmentError("proc-scan-failed") from None
    for entry in sorted(entries, key=int)[:20000]:
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
            raise ContainmentError("proc-scan-degraded") from None
        if marker.encode() in cmdline:
            count += 1
    return count


def _scenario_env(
    mode: str,
    parent_pid: int,
    parent_port: int,
    sentinel_file: Path,
    sentinel_socket: Path,
    parent_ns: dict[str, str],
    descendant_token: str | None = None,
) -> dict[str, str]:
    env = {
        "SLAIF_PROBE_MODE": mode,
        "SLAIF_PROBE_UID": str(PROBE_UID),
        "SLAIF_PROBE_GID": str(PROBE_GID),
        "SLAIF_PROBE_PARENT_PID": str(parent_pid),
        "SLAIF_PROBE_PARENT_LISTENER_PORT": str(parent_port),
        "SLAIF_PROBE_SENTINEL_FILE": str(sentinel_file),
        "SLAIF_PROBE_SENTINEL_SOCKET": str(sentinel_socket),
        "SLAIF_PROBE_EXPECTED_MEMORY_BYTES": str(MEMORY_BYTES),
        "SLAIF_PROBE_EXPECTED_PIDS": str(PIDS_LIMIT),
        "SLAIF_PROBE_EXPECTED_STORAGE_BYTES": str(TMPFS_TOTAL_BYTES),
        "SLAIF_PROBE_WRITABLE_MOUNTS": ",".join(sorted(TMPFS_SPECS)),
    }
    if mode == "hang" and descendant_token is not None:
        env["SLAIF_PROBE_DESCENDANT_TOKEN"] = descendant_token
    for name in _NS_NAMES:
        env[f"SLAIF_PROBE_PARENT_NS_{name.upper()}"] = parent_ns[name]
    return env


def _inspect_container(
    executor: Executor,
    container_id: str,
    expected_exit_code: int,
    expected_runtime: str,
) -> None:
    """Exact documented-field extraction (no Sprig, no raw dumps).

    The container's ``HostConfig.Runtime`` must additionally be the
    exact reviewed default runtime (closed bare-token query).
    """
    host_config = json.loads(
        _query(
            executor,
            ["docker", "inspect", "--format", "{{json .HostConfig}}", container_id],
        )
    )
    config = json.loads(
        _query(executor, ["docker", "inspect", "--format", "{{json .Config}}", container_id])
    )
    state = json.loads(
        _query(executor, ["docker", "inspect", "--format", "{{json .State}}", container_id])
    )
    validate_inspect_record(extract_inspect_facts(host_config, config, state), expected_exit_code)
    runtime = (
        _query(
            executor,
            ["docker", "inspect", "--format", "{{.HostConfig.Runtime}}", container_id],
        )
        .decode("ascii", "replace")
        .strip()
    )
    if not _RUNTIME_NAME_RE.fullmatch(runtime) or runtime != expected_runtime:
        raise ContainmentError("inspect-mismatch:Runtime")


def run(
    repo: Path,
    work: Path,
    executor: Executor,
    descendant_uid: int = PROBE_UID,
    hang_token: str | None = None,
) -> dict[str, object]:
    # ``descendant_uid`` is the uid the runner must find for the
    # token-bound owned descendant in /proc: the fixture uid in the
    # real disposable CI, or the caller's own uid in the local
    # orchestration tests (which own a real tiny child).  The token
    # (per-run, 32 hex) binds the EXACT owned occurrence; it is
    # injected by tests or generated fresh here.
    if hang_token is None:
        hang_token = uuid.uuid4().hex
    if not _DESCENDANT_TOKEN_RE.fullmatch(hang_token):
        raise ContainmentError("hang-token-invalid")
    # -- Reviewed probe/Dockerfile sources (identity-verified) ---------
    probe_path = repo / "scripts" / "cache_native_containment_probe.py"
    dockerfile_path = repo / "scripts" / "cache_native_containment.Dockerfile"
    for path in (probe_path, dockerfile_path):
        if not path.is_file():
            raise ContainmentError("probe-file-missing")
    probe_digest = sha256_file(probe_path)
    dockerfile_bytes = dockerfile_path.read_bytes()
    base_literal = b"python:3.12-slim-bookworm@sha256:"
    embedded = [
        line.split(b"FROM ", 1)[1].strip()
        for line in dockerfile_bytes.splitlines()
        if line.startswith(b"FROM ")
    ]
    if len(embedded) != 1 or not embedded[0].startswith(base_literal):
        raise ContainmentError("dockerfile-base-unpinned")
    digest_hex = embedded[0].split(b"@sha256:")[1].decode("ascii")
    if not re.fullmatch(r"[0-9a-f]{64}", digest_hex):
        raise ContainmentError("dockerfile-base-unpinned")
    reference = (repo / "Dockerfile").read_bytes()
    if embedded[0] not in reference:  # byte-identical to the repo Dockerfile base
        raise ContainmentError("dockerfile-base-mismatch")

    # -- Fresh owned protected scratch namespace -----------------------
    _create_work_root(work)
    context = _owned_subdir(work, "context")
    (context / "Dockerfile").write_bytes(dockerfile_bytes)
    (context / "cache_native_containment_probe.py").write_bytes(probe_path.read_bytes())
    if sha256_file(context / "cache_native_containment_probe.py") != probe_digest:
        raise ContainmentError("context-mismatch")

    # -- Engine preflight: version + explicit seccomp availability -----
    engine_version = (
        _query(executor, ["docker", "version", "--format", "{{.Server.Version}}"])
        .decode("ascii", "replace")
        .strip()
    )
    if not _ENGINE_VERSION_RE.fullmatch(engine_version):
        raise ContainmentError("engine-version-invalid")
    security_options = (
        _query(executor, ["docker", "info", "--format", "{{range .SecurityOptions}}{{.}} {{end}}"])
        .decode("ascii", "replace")
        .strip()
    )
    if "name=seccomp" not in security_options:
        raise ContainmentError("seccomp-unavailable")

    # -- Runtime identity: bounded reviewed facts (closed output) -----
    # The exact default runtime and its version are obtained through
    # closed bounded queries only (bare tokens, one JSON object, one
    # version line) — never raw inspect/env dumps.  Anything that
    # does not match the reviewed grammar fails closed.
    default_runtime = (
        _query(executor, ["docker", "info", "--format", "{{.DefaultRuntime}}"])
        .decode("ascii", "replace")
        .strip()
    )
    if not _RUNTIME_NAME_RE.fullmatch(default_runtime):
        raise ContainmentError("runtime-invalid")
    try:
        runtimes = json.loads(
            _query(executor, ["docker", "info", "--format", "{{json .Runtimes}}"])
        )
    except ValueError:
        raise ContainmentError("runtime-invalid") from None
    runtime_entry = runtimes.get(default_runtime) if isinstance(runtimes, dict) else None
    # Moby serializes Runtimes with the lowercase ``path`` field
    # (api/types/system/runtime.go, omitempty).  daemon/info_unix.go's
    # fillPlatformInfo fills it from daemon/runtime_unix.go's
    # stockRuntimes(), where the stock runc entry's path is the bare
    # name "runc" (defaultRuntimeName): the REAL stock shape is a
    # bare token, not an absolute path.  An empty path (other
    # entries) is likewise resolved through the standard PATH.  A
    # non-empty daemon-declared absolute path is shape-validated
    # ONLY and never executed; anything else fails closed.
    runtime_path = runtime_entry.get("path") if isinstance(runtime_entry, dict) else None
    if not isinstance(runtime_path, str):
        raise ContainmentError("runtime-invalid")
    if runtime_path and not (
        _RUNTIME_NAME_RE.fullmatch(runtime_path)
        or (_RUNTIME_PATH_RE.fullmatch(runtime_path) and ".." not in runtime_path.split("/"))
    ):
        raise ContainmentError("runtime-invalid")
    # The version query is bound to the reviewed bare name (grammar
    # validated above) resolved through the runner's standard PATH —
    # a daemon-supplied executable path is never executed.
    version_line = (
        _query(executor, [default_runtime, "--version"]).decode("ascii", "replace").splitlines()
    )
    version_match = _RUNTIME_VERSION_RE.fullmatch(version_line[0].strip() if version_line else "")
    if version_match is None or version_match.group("name") != default_runtime:
        raise ContainmentError("runtime-version-invalid")
    runtime_version = version_match.group("version")

    # -- Build the minimal fixture image (pinned base, public pull) ----
    result = executor(["docker", "pull", PINNED_BASE], PULL_TIMEOUT)
    if result.returncode != 0:
        raise ContainmentError("pull-failed")
    result = executor(["docker", "build", "-t", IMAGE_NAME, str(context)], BUILD_TIMEOUT)
    if result.returncode != 0:
        raise ContainmentError("build-failed")
    image_id = (
        _query(executor, ["docker", "inspect", "--format", "{{.Id}}", IMAGE_NAME])
        .decode("ascii", "replace")
        .strip()
    )
    if not _IMAGE_ID_RE.fullmatch(image_id):
        raise ContainmentError("build-failed")

    # -- Owned synthetic parent sentinels (no real parent data) --------
    sentinels = _owned_subdir(work, "sentinels")
    sentinel_file = sentinels / "parent-sentinel-file"
    sentinel_file.write_bytes(b"slaif-synthetic-parent-sentinel-017p\n")
    os.chmod(sentinel_file, stat.S_IRUSR | stat.S_IWUSR)
    sentinel_file_digest = sha256_file(sentinel_file)
    sentinel_socket_path = sentinels / "parent-sentinel-socket"
    _sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    _sock.bind(str(sentinel_socket_path))
    _sock.close()  # the file remains as the forbidden-data sentinel
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    parent_port = listener.getsockname()[1]
    parent_pid = os.getpid()
    parent_ns = parent_namespace_ids()
    sentinel_process = _spawn_parent_sentinel()
    created_containers: list[str] = []
    cleanup_error: ContainmentError | None = None
    cleanup_failures: list[str] = []
    image_removed = False
    try:
        scenarios: dict[str, dict[str, object]] = {}
        success_record: dict[str, object] | None = None
        descendant_terminated = False

        for index, (mode, timeout, expect_timeout) in enumerate(
            (
                ("success", RUN_TIMEOUT, False),
                ("fail", RUN_TIMEOUT, False),
                ("hang", HANG_TIMEOUT, True),
            )
        ):
            name = f"slaif-containment-017p-{mode}-{os.getpid()}-{index}-{uuid.uuid4().hex[:8]}"
            owned_label = f"slaif-owned-containment-017p={uuid.uuid4().hex}"
            env = _scenario_env(
                mode,
                parent_pid,
                parent_port,
                sentinel_file,
                sentinel_socket_path,
                parent_ns,
                hang_token if mode == "hang" else None,
            )

            # Pre-existing name collision: fixed failure, never adopt.
            if _ps_filter(executor, f"name={name}") != "absent":
                raise ContainmentError("name-collision")
            # create -> validate/record the actual returned CID first.
            result = executor(build_run_conf_argv(IMAGE_NAME, name, owned_label, env), timeout)
            if result.returncode != 0:
                raise ContainmentError("create-failed")
            container_id = result.output.decode("ascii", "replace").strip()
            if not _CONTAINER_ID_RE.fullmatch(container_id):
                raise ContainmentError("create-failed")
            created_containers.append(container_id)

            try:
                start = executor(["docker", "start", "-a", container_id], timeout)
                host_timeout = False
            except subprocess.TimeoutExpired as exc:
                host_timeout = True
                start = None
                partial_output = getattr(exc, "partial_output", None)

            if expect_timeout:
                if not host_timeout:
                    raise ContainmentError("scenario-expected-timeout")
                # Ordered parent-death proof (never a bare empty-scan
                # claim):
                # 1) the closed record proves the probe completed all
                #    containment checks and reports the live owned
                #    descendant with its exact per-run token;
                if partial_output is None:
                    raise ContainmentError("probe-output-missing")
                line = extract_probe_line(partial_output)
                if line is None:
                    raise ContainmentError("probe-output-missing")
                try:
                    record = json.loads(line)
                except ValueError:
                    raise ContainmentError("probe-output-malformed") from None
                validated = validate_probe_record(record, probe_digest, "hang", hang_token)
                # 2) pre-termination POSITIVE: exactly one live owned
                #    occurrence (uid + exact token) is observed;
                if _count_marker_processes(descendant_uid, hang_token) != 1:
                    raise ContainmentError("descendant-not-observed")
                # 3) kill the registered container (PID1 + group);
                cleanup_container(executor, container_id)
                # 4) post-termination: the exact occurrence is gone
                #    and the container is verified absent (inside
                #    cleanup_container), while the unrelated parent
                #    sentinel survives.
                if _count_marker_processes(descendant_uid, hang_token) != 0:
                    raise ContainmentError("descendant-leftover")
                descendant_terminated = True
                if sentinel_process.poll() is not None:
                    raise ContainmentError("sentinel-process-died")
                scenarios[name.split(f"-{os.getpid()}-")[0]] = {
                    "host_timeout": True,
                    "exit_code": None,
                    "descendant_terminated": True,
                    "parent_sentinel_survived": True,
                    "descendant_pid": validated["descendant_pid"],
                }
            else:
                if host_timeout or start is None:
                    raise ContainmentError("scenario-timeout")
                exit_code = start.returncode
                if mode == "success" and exit_code != 0:
                    raise ContainmentError("probe-check-failed")
                if mode == "fail" and exit_code == 0:
                    raise ContainmentError("scenario-expected-failure")
                line = extract_probe_line(start.output)
                if line is None:
                    raise ContainmentError("probe-output-missing")
                try:
                    record = json.loads(line)
                except ValueError:
                    raise ContainmentError("probe-output-malformed") from None
                validated = validate_probe_record(record, probe_digest, mode)
                if mode == "success":
                    success_record = validated
                _inspect_container(executor, container_id, exit_code, default_runtime)
                # Exact-owned cleanup after EVERY non-timeout scenario;
                # verified absence.  (The hang scenario performs its
                # own ordered cleanup above, between the two scans.)
                cleanup_container(executor, container_id)
                scenarios[name.split(f"-{os.getpid()}-")[0]] = {
                    "host_timeout": False,
                    "exit_code": exit_code,
                    "probe_status": validated["status"],
                }

            if sha256_file(sentinel_file) != sentinel_file_digest:
                raise ContainmentError("sentinel-changed")
            if not sentinel_socket_path.exists():
                raise ContainmentError("sentinel-changed")

        verify_no_leftovers(executor, IMAGE_NAME)
    except ContainmentError as exc:
        cleanup_error = exc
    finally:
        listener.close()
        sentinel_socket_path.unlink(missing_ok=True)
        # Idempotent exact-owned sweep: already-cleaned containers are
        # verified-absent no-ops; containers left behind by an early
        # failure are removed by their registered owned id only.
        for container_id in created_containers:
            try:
                cleanup_container(executor, container_id)
            except ContainmentError as cleanup_exc:
                cleanup_failures.append(f"container-cleanup:{cleanup_exc}")
        # Image removal: check the exact owned result, then verify
        # ACTUAL absence through an authoritative daemon query.  A
        # successful rmi proves the daemon processed the removal; an
        # image still present afterwards means the removal did not
        # take effect.  Absence is "verified" only when the query
        # succeeds and the daemon explicitly reports no such
        # image/object; a daemon/transport failure (nonzero exit
        # WITHOUT the authoritative marker) is a distinct unverified
        # state — never conflated with absence.
        try:
            rmi = executor(["docker", "rmi", image_id], _QUERY_TIMEOUT)
            if rmi.returncode != 0:
                cleanup_failures.append("image-rmi-failed")
            else:
                inspect_result = executor(["docker", "image", "inspect", image_id], _QUERY_TIMEOUT)
                if inspect_result.returncode == 0:
                    cleanup_failures.append("image-still-present")
                elif _NO_SUCH_OBJECT_RE.search(inspect_result.output.decode("ascii", "replace")):
                    image_removed = True
                else:
                    # A failed daemon/query is NOT verified absence.
                    cleanup_failures.append("image-absence-unverified")
        except ContainmentError as cleanup_exc:
            cleanup_failures.append(f"image-cleanup:{cleanup_exc}")
        try:
            sentinel_process.kill()
            sentinel_process.wait(timeout=_LEADER_REAP_SECONDS)
        except (OSError, subprocess.TimeoutExpired):
            cleanup_failures.append("sentinel-cleanup-failed")
        shutil.rmtree(work, ignore_errors=True)
    if cleanup_failures:
        # Cleanup failures stay visible even when a primary check
        # also failed; both remain in the fixed-reason report.
        cleanup_reason = ";".join(sorted(set(cleanup_failures)))
        if cleanup_error is not None:
            raise ContainmentError(f"{cleanup_error};{cleanup_reason}")
        raise ContainmentError(cleanup_reason)
    if cleanup_error is not None:
        raise cleanup_error

    assert success_record is not None
    uname = platform.uname()
    return {
        "schema": SCHEMA,
        "status": "pass",
        "engine_version": engine_version,
        "runtime_name": default_runtime,
        "runtime_version": runtime_version,
        "python_version": success_record["python_version"],
        "kernel_release": success_record["kernel_release"],
        "cgroup_version": success_record["cgroup_version"],
        "runner_kernel": uname.release,
        "runner_arch": uname.machine,
        "runner_python": platform.python_version(),
        "base_image": PINNED_BASE,
        "image_id": image_id,
        "probe_source_sha256": probe_digest,
        "scenarios": scenarios,
        "checks": success_record["checks"],
        "measured": success_record["measured"],
        "descendant_terminated": descendant_terminated,
        "engine_confined": True,
        "sentinels_unchanged": True,
        "cleanup_exact_only": True,
        "no_leftover_containers": True,
        "image_removed": image_removed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="repository checkout root")
    parser.add_argument("--work", required=True, help="fresh owned disposable work root")
    args = parser.parse_args(argv)
    if os.environ.get("GITHUB_ACTIONS") != "true":
        print(
            json.dumps(
                {
                    "schema": SCHEMA,
                    "status": "fail",
                    "reason": "not-a-disposable-ci-runner",
                }
            )
        )
        return 1
    # The capability proof claims a hosted disposable runner: on
    # GitHub Actions that is RUNNER_ENVIRONMENT=github-hosted.  A
    # self-hosted runner (or any other environment) is refused.
    if os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted":
        print(
            json.dumps(
                {
                    "schema": SCHEMA,
                    "status": "fail",
                    "reason": "not-a-hosted-ci-runner",
                }
            )
        )
        return 1
    repo = Path(args.repo)
    work = Path(args.work)
    try:
        summary = run(repo, work, _real_execute)
    except ContainmentError as exc:
        print(json.dumps({"schema": SCHEMA, "status": "fail", "reason": str(exc)}))
        return 1
    except Exception:
        print(json.dumps({"schema": SCHEMA, "status": "fail", "reason": "internal"}))
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
