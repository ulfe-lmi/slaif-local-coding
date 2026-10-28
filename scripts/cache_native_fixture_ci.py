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
env dumps, TUI content or exception strings.  On a scenario
failure the closed workflow record carries the fixed reason and,
only when the stand-in itself emitted a closed fail record, that
child's own closed fail token (admitted by explicit allowlist
membership; unknown, malformed or missing tokens stay generic) — a
single fixed token, never raw output.  NO Codex binary is
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
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import IO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cache_native_fixture_controller as fixture_controller  # noqa: E402
import cache_native_fixture_export_client as fixture_export  # noqa: E402
import cache_native_fixture_model as model  # noqa: E402
import cache_native_fixture_runtime_profile as rprofile  # noqa: E402
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


def owner_tmpfs_budgets(profile: rprofile.RuntimeProfile) -> tuple[tuple[str, int, int, int], ...]:
    """The owner-variant tmpfs budgets: the SAME closed mounts,
    sizes and modes, with the subject-owned mounts owned by the
    frozen profile's exact INDEPENDENT subject UID/GID (the
    controller private mount stays exactly 21001/21001).  The
    original budgets are never mutated."""
    if profile.profile != rprofile.PROFILE_OWNER_UID:
        raise FixtureError("tmpfs-profile-invalid")
    budgets = []
    for mount, size, uid, gid in model.DEFAULT_TMPFS_BUDGETS:
        if mount == "/run/slaif-ctl":
            budgets.append((mount, size, uid, gid))
        else:
            budgets.append((mount, size, profile.subject_uid, profile.subject_gid))
    return tuple(budgets)


def owner_tmpfs_specs(profile: rprofile.RuntimeProfile) -> dict[str, str]:
    """The owner-variant create ``--tmpfs`` spec strings (the SAME
    closed spec grammar as the module constant, the frozen
    subject-owned identities)."""
    return {
        mount: (f"rw,nosuid,size={size // 1024}k,uid={uid},gid={gid},mode={oct(mode)[2:]}")
        for mount, size, uid, gid in owner_tmpfs_budgets(profile)
        for mode in (_TMPFS_MODES[mount],)
    }


def owner_tmpfs_spec_env(profile: rprofile.RuntimeProfile) -> str:
    """The owner-variant ``SLAIF_FIXTURE_TMPFS_SPECS`` closed value
    (the stand-in measures the ACTUAL mount table against this
    exact closed spec)."""
    return ",".join(
        f"{mount}:{size}:{uid}:{gid}"
        for mount, size, uid, gid in sorted(owner_tmpfs_budgets(profile))
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
# Module-level closed fact containers for the current run (the
# scenario functions record measured closed facts; run() consumes
# and clears them).  No raw content ever enters them.
_SC_FACTS: dict[str, dict[str, object]] = {}
_SC_EXPORT: dict[str, object] = {}
_SC_TEARDOWN: dict[str, object] = {}


# The 017-ae native attach-binding devpts probe: the EXACT
# immutable read-only Python program that inventories the
# ALLOCATED SLAVE device nodes of the registered fixture's OWN
# devpts namespace (it runs INSIDE the container through the
# owner's guarded exact-CID exec channel as the frozen owner
# exec user, invoked exactly ``python3 -I -S -c <this code>`` —
# isolated interpreter, no site, no user startup, no PYTHONPATH,
# no arbitrary program).  It never reads the native subject's
# /proc, never enumerates the host /dev/pts (its /dev/pts IS the
# fixture's own mount instance — the measured (st_dev, st_ino)
# namespace identity is carried in the closed record and
# coherence-checked against the baseline), never writes, and
# bounds itself closed: at most 96 slave rows (the reserved
# ptmx node is not a slave), at most 65536 serialized output
# bytes (overbound is a fail record, never a truncation) and a
# 5 s internal clock (the host guard clamps the SAME call to
# the remaining owner END; a failed query is never absence).
# The isolation fact is MEASURED, not claimed: the record
# carries whether any user startup/site module is importable —
# a non-isolated probe is a closed refusal at the host.
DEVPTS_PROBE_RECORD = "slaif-017ae-devpts-inventory-v1"
DEVPTS_PROBE_TIMEOUT = 5.0
DEVPTS_MAX_SLAVE_ROWS = 96
DEVPTS_OUTPUT_MAX = 65536
DEVPTS_FAIL_REASONS = (
    "devpts-unreadable",
    "devpts-overbound",
    "devpts-timeout",
    "devpts-row-malformed",
    "devpts-namespace-raced",
    "devpts-policy-unreadable",
    "devpts-policy-overbound",
    "devpts-policy-absent",
    "devpts-policy-malformed",
    "devpts-policy-mismatch",
)
DEVPTS_PROBE = r"""
import json, os, stat, sys, time
def fail(reason):
    print(json.dumps({"record": "slaif-017ae-devpts-inventory-v1",
                      "status": "fail", "reason": reason},
                     sort_keys=True, separators=(",", ":")))
    raise SystemExit(2)
try:
    deadline = time.monotonic() + 5.0
    def check_time():
        if time.monotonic() > deadline:
            fail("devpts-timeout")
    # the measured devpts root frame: the fixture's OWN mount
    # instance (namespace identity = (st_dev, st_ino) of the
    # /dev/pts directory); every node is identity-checked
    # against this root and the frame is re-measured AFTER
    # collection (a raced mount/snapshot cannot pass)
    root = os.stat("/dev/pts")
    if not stat.S_ISDIR(root.st_mode):
        fail("devpts-unreadable")
    namespace = [root.st_dev, root.st_ino]
    check_time()
    # the MEASURED devpts policy fact: the ONE mountinfo entry
    # that binds the measured root to /dev/pts (same
    # namespace/root).  ONLY the derived closed fact (fstype +
    # node gid + node mode) is carried — the raw mount table
    # is never retained, and the permitted node GID/mode is
    # measured, NEVER assumed from the process identity.
    want = b"%d:%d" % (os.major(root.st_dev), os.minor(root.st_dev))
    try:
        with open("/proc/self/mountinfo", "rb") as handle:
            table = handle.read(65537)
    except OSError:
        fail("devpts-policy-unreadable")
    if len(table) > 65536:
        fail("devpts-policy-overbound")
    policy = None
    for line in table.split(b"\n"):
        parts = line.split(b" ")
        if len(parts) < 5 or parts[2] != want or parts[4] != b"/dev/pts":
            continue
        if policy is not None:
            fail("devpts-policy-mismatch")
        if b"-" not in parts:
            fail("devpts-policy-malformed")
        sep = parts.index(b"-")
        if sep + 3 >= len(parts):
            fail("devpts-policy-mismatch")
        if parts[sep + 1] != b"devpts":
            fail("devpts-policy-mismatch")
        gid = None
        mode = None
        for opt in parts[sep + 3].split(b","):
            key, eq, value = opt.partition(b"=")
            if not eq or not value:
                continue
            if key == b"gid":
                # a duplicate or invalid gid option is a
                # closed refusal (no ambiguity, no silent
                # first-wins)
                if gid is not None or not value.isdigit():
                    fail("devpts-policy-malformed")
                gid = int(value)
            elif key == b"mode":
                if (
                    mode is not None
                    or len(value) > 4
                    or not all(c in b"01234567" for c in value)
                ):
                    fail("devpts-policy-malformed")
                mode = int(value, 8)
        if gid is None or mode is None:
            fail("devpts-policy-malformed")
        policy = {"fstype": "devpts", "gid": gid, "mode": mode}
    if policy is None:
        fail("devpts-policy-absent")
    rows = []
    count = 0
    # BOUNDED iteration of the fixture's OWN namespace: the
    # directory is scanned one entry at a time and the 98th
    # entry (the reserved ptmx plus at most 96 slaves) is a
    # refusal BEFORE it is processed or retained — the whole
    # directory is never materialized
    it = os.scandir("/dev/pts")
    try:
        while True:
            check_time()
            try:
                entry = next(it)
            except StopIteration:
                break
            count += 1
            if count > 97:
                fail("devpts-overbound")
            name = entry.name
            if name == "ptmx":
                # the reserved ptmx node: iterated, verified a
                # character node on the SAME root, NOT a slave
                # row
                try:
                    pmx = entry.stat(follow_symlinks=False)
                except OSError:
                    fail("devpts-unreadable")
                if not stat.S_ISCHR(pmx.st_mode) or pmx.st_dev != root.st_dev:
                    fail("devpts-row-malformed")
                continue
            if not (name.isascii() and name.isdigit()):
                fail("devpts-row-malformed")
            try:
                dst = entry.stat(follow_symlinks=False)
            except OSError:
                fail("devpts-unreadable")
            if not stat.S_ISCHR(dst.st_mode):
                fail("devpts-row-malformed")
            if dst.st_dev != root.st_dev:
                fail("devpts-row-malformed")
            rows.append([name, os.major(dst.st_rdev), os.minor(dst.st_rdev),
                         dst.st_ino, dst.st_mode & 0o7777, dst.st_uid, dst.st_gid])
            if len(rows) > 96:
                fail("devpts-overbound")
    finally:
        try:
            it.close()
        except OSError:
            pass
    check_time()
    after = os.stat("/dev/pts")
    if (
        not stat.S_ISDIR(after.st_mode)
        or [after.st_dev, after.st_ino] != namespace
    ):
        fail("devpts-namespace-raced")
    payload = {
        "record": "slaif-017ae-devpts-inventory-v1",
        "status": "pass",
        "uid": os.getuid(),
        "namespace": namespace,
        "policy": policy,
        "isolation": {"site": "site" in sys.modules,
                      "startup": ("sitecustomize" in sys.modules
                                  or "usercustomize" in sys.modules)},
        "slave_rows": rows,
    }
    # the bounds are re-checked at FINAL serialization/return
    # as well (the empty baseline path included): time first,
    # then the closed output bound, then the time again around
    # the return
    check_time()
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    if len(text) > 65536:
        fail("devpts-overbound")
    check_time()
    print(text)
except SystemExit:
    raise
except Exception:
    fail("devpts-unreadable")
"""


# The closed readiness DIAGNOSIS (order 017-y): on a nonzero
# bounded readiness exec, carry ONLY the probe's own exact finite
# closed failure record — if and only if it is exactly one
# fixed-shape record with one of the probe's fixed measured
# causes — as a REFINEMENT of the original ``controller-not-ready``
# category (``controller-not-ready:<cause>``).  Every other shape
# (missing, malformed, multiple/duplicate, foreign, over-bound or
# contradictory) stays the fixed UNKNOWN: the original generic
# token.  No raw output is ever persisted or propagated; the scan
# is in-memory over the already-captured bounded bytes, exactly
# like the stand-in fail-token channel.
def _controller_probe_fail_reason(output: bytes) -> str | None:
    """The ONE closed controller-readiness failure record on a
    nonzero bounded readiness exec (order 017-y).  The ENTIRE
    bounded output must be EXACTLY ONE complete strict record:
    strict ASCII, exactly one line, a strict JSON object (duplicate
    keys refused) with exactly the probe's closed fail key set, the
    fixed probe tag, a fail status and one of the probe's fixed
    measured causes.  Anything less or more — a raw prefix/suffix,
    any extra line (malformed, foreign, contradictory or duplicate
    record), non-ASCII bytes, an unknown reason, or a non-fail
    status — is the fixed UNKNOWN: the caller keeps the original
    generic ``controller-not-ready``.  No line is skipped or
    trusted in isolation; the scan is in-memory over the
    already-captured bounded bytes, and no raw output is ever
    persisted or propagated."""
    try:
        text = output.decode("ascii")
    except UnicodeDecodeError:
        return None
    if not text.endswith("\n") or "\n" in text[:-1] or not text[:-1]:
        return None

    def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
        seen: set[str] = set()
        for key, _value in pairs:
            if key in seen:
                raise ValueError("duplicate key")
            seen.add(key)
        return dict(pairs)

    try:
        obj = json.loads(text[:-1], object_pairs_hook=_reject_duplicate_keys)
    except ValueError:
        return None
    if (
        not isinstance(obj, dict)
        or set(obj) != {"record", "status", "reason"}
        or obj.get("record") != "slaif-fixture-ctl-probe-v1"
        or obj.get("status") != "fail"
    ):
        return None
    reason = obj.get("reason")
    if isinstance(reason, str) and reason in ("uid-not-21001", "pid1-uid", "health-unreachable"):
        return reason
    return None


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


def _real_execute(
    argv: list[str], timeout: float, pty: bool = False, env: Mapping[str, str] | None = None
) -> ExecResult:
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
        return _real_execute_pty(argv, timeout, env)
    proc = subprocess.Popen(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        env=env if env is not None else os.environ,
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


def _real_execute_pty(
    argv: list[str], timeout: float, env: Mapping[str, str] | None = None
) -> ExecResult:
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
            env=env if env is not None else os.environ,
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
    "auth-binding",
    "observe",
)
_INSPECT_FORMATS = frozenset(
    {
        "{{json .HostConfig}}",
        "{{json .Config}}",
        "{{json .State}}",
        "{{.Id}}",
        "{{.HostConfig.LogConfig.Type}}",
        "{{.Config.User}}",
        # the closed readiness diagnosis (017-y): the single
        # finite lifecycle fact selected by the ONE conditional
        # bounded query of the SAME registered CID after a
        # nonzero readiness exec without the probe's closed
        # failure record (the .State.Status line only — never
        # the full State object, its exit code or any log)
        "{{.State.Status}}",
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
        "{{.Name}}",
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
# The order-bound local 017-s rehearsal container namespace (a
# SEPARATE closed slug enumeration; the hosted R pattern above is
# unchanged and the focused lockstep test still binds it to the
# model scenario names).
# The plain slugs compose with the SAME name template as the hosted
# path (``slaif-fixture-<prefix>-<slug>-<pid>-<index>-<hex8>`` with
# prefix 017s) — the round tag appears exactly once, and the closed
# enumeration is the complete set of names the local 017-s rehearsal
# may ever create (arbitrary or double-prefixed names are refused).
LOCAL_SCENARIO_SLUGS = (
    "controller",
    "subject",
    "pty",
    "auth",
    "success",
    "prepared",
)
_LOCAL_NAME_PATTERN = (
    r"slaif-fixture-017s-(?:" + "|".join(LOCAL_SCENARIO_SLUGS) + r")-\d+-\d+-[0-9a-f]{8}"
)
_LOCAL_NAME_RE = re.compile(r"^" + _LOCAL_NAME_PATTERN + r"$")
# Ownership label: the round namespace is closed to the two exact
# fixture rounds that may create containers through this runner.
_LABEL_RE = re.compile(r"^slaif-owned-fixture-017[rs]=[0-9a-f]{32}$")


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
            or re.fullmatch(r"name=" + _LOCAL_NAME_PATTERN, argv[4])
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


def _make_docker_create_matcher(tmpfs_expected: frozenset[str]):
    """The closed create form for one exact closed tmpfs spec set
    (see the module matcher below for the fixed historical set; the
    owner-UID variant is the SAME closed form with the frozen
    profile's subject-owned mount specs — every other flag, the
    controller identity and the confinement law are byte-for-byte
    the original)."""

    def match(argv: list[str]) -> bool:
        if len(argv) < 4 or argv[:2] != ["docker", "create"]:
            return False
        i = 2
        if argv[i] != "--name" or not (
            _NAME_RE.fullmatch(argv[i + 1]) or _LOCAL_NAME_RE.fullmatch(argv[i + 1])
        ):
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
        tmpfs: set[str] = set()
        while i < len(argv) and argv[i] == "--tmpfs":
            if i + 1 >= len(argv) or argv[i + 1] not in tmpfs_expected:
                return False
            tmpfs.add(argv[i + 1])
            i += 2
        if tmpfs != set(tmpfs_expected):
            return False
        while i < len(argv) and argv[i] == "-e":
            if i + 1 >= len(argv):
                return False
            key, sep, value = argv[i + 1].partition("=")
            if not sep or not _ENV_KEY_RE.fullmatch(key) or not _ENV_VALUE_RE.fullmatch(value):
                return False
            i += 2
        return i + 1 == len(argv) and _is_image_ref(argv[i])

    return match


def _original_tmpfs_expected() -> frozenset[str]:
    return frozenset(f"{m}:{TMPFS_SPECS[m]}" for m in TMPFS_SPECS)


_match_docker_create = _make_docker_create_matcher(_original_tmpfs_expected())


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


def _make_docker_exec_matcher(subject_user: str):
    """The exec boundary for one exact closed subject ``uid:gid``
    pair: optional PTY, the controller pair OR that exact subject
    pair, closed env keys/values, an OPTIONAL single
    ``--env-file <path>`` admitted only when that exact path is
    bound for the run via ``bind_env_files`` (the hosted CI path
    binds nothing, so its behavior is unchanged), the exact
    registered CID, and ONLY the fixed fixture python entry points
    (controller probe, stand-in modes, export client).  No shell,
    no arbitrary program.  The original module matcher below is the
    factory applied to the fixed historical subject pair (byte-for-
    byte the original accepted argv set); the owner-UID variant is
    built from the SAME factory with the frozen profile's exact
    ``uid:gid`` (UID and GID independent — never ``uid:uid``)."""

    def match(argv: list[str]) -> bool:
        if len(argv) < 5 or argv[:2] != ["docker", "exec"]:
            return False
        i = 2
        if argv[i] == "-it":
            i += 1
        if (
            i + 1 >= len(argv)
            or argv[i] != "--user"
            or argv[i + 1]
            not in (
                f"{CONTROLLER_UID}:{CONTROLLER_UID}",
                subject_user,
            )
        ):
            return False
        i += 2
        while i + 1 < len(argv) and argv[i] == "-e":
            key, sep, value = argv[i + 1].partition("=")
            if not sep or not _ENV_KEY_RE.fullmatch(key) or not _ENV_VALUE_RE.fullmatch(value):
                return False
            i += 2
        if i < len(argv) and argv[i] == "--env-file":
            if i + 1 >= len(argv) or argv[i + 1] not in _ENV_FILE_BIND:
                return False
            i += 2
        if i >= len(argv) or not _is_cid(argv[i]):
            return False
        tail = argv[i + 1 :]
        probe = (
            len(tail) == 3
            and tail[0] == "python3"
            and tail[1] == "-c"
            and tail[2] == CONTROLLER_PROBE
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

    return match


_match_docker_exec = _make_docker_exec_matcher(f"{SUBJECT_UID}:{SUBJECT_UID}")


def _make_docker_exec_hold_matcher(subject_user: str):
    """The detached hold form for one exact closed subject
    ``uid:gid`` pair (the closed law of the historical form:
    ``-d``, NO PTY, NO -e arguments, NO env file, the exact
    registered CID, and ONLY the fixed stand-in hold entry whose
    issued 32-hex marker is the kernel-cmdline correlation
    identity; no general detach, no shell, no arbitrary argv).
    The original module matcher below is the factory applied to
    the fixed historical subject pair."""

    def match(argv: list[str]) -> bool:
        return (
            len(argv) == 12
            and argv[0] == "docker"
            and argv[1] == "exec"
            and argv[2] == "-d"
            and argv[3] == "--user"
            and argv[4] == subject_user
            and _is_cid(argv[5])
            and argv[6] == "python3"
            and argv[7] == STANDIN_PATH
            and argv[8] == "--mode"
            and argv[9] == "hold"
            and argv[10] == "--hold-token"
            and re.fullmatch(r"[0-9a-f]{32}", argv[11]) is not None
        )

    return match


_match_docker_exec_hold = _make_docker_exec_hold_matcher(f"{SUBJECT_UID}:{SUBJECT_UID}")


def _make_devpts_probe_matcher(subject_user: str):
    """The ONE exact AF-only devpts probe form (017-ae): the
    native attach-binding phase's read-only inventory
    operation, admitted for the canonical 017-af entry ONLY
    (the entry is selected by the owner's OWN bound
    order — a caller flag can never mint it).  The closed
    form is EXACT and NON-PTY: no ``-it`` (a PTY attach would
    allocate and contaminate the measured namespace), no
    controller user (the frozen subject ``uid:gid`` only), no
    ``-e`` environment arguments, no ``--env-file`` — exactly
    ``docker exec --user <frozen uid:gid> <cid> python3 -I -S
    -c <the immutable probe code>``.  The original closed exec
    matcher is reused UNCHANGED for every old form, and the
    AB/AD/default guards keep refusing this new form."""

    def match(argv: list[str]) -> bool:
        return (
            len(argv) == 10
            and argv[0] == "docker"
            and argv[1] == "exec"
            and argv[2] == "--user"
            and argv[3] == subject_user
            and _is_cid(argv[4])
            and argv[5] == "python3"
            and argv[6] == "-I"
            and argv[7] == "-S"
            and argv[8] == "-c"
            and argv[9] == DEVPTS_PROBE
        )

    return match


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
    _match_docker_exec_hold,
    _match_runtime_version,
)


def _make_docker_build_matcher(profile: rprofile.RuntimeProfile):
    """The owner-variant build form for one frozen validated
    profile: the historical ``docker build -t`` head plus the
    EXACT closed build-arg sequence of the profile (the fixed
    profile marker and the frozen subject UID/GID values — the
    original build argv is never accepted here and the original
    matcher is untouched).  No caller can substitute values: the
    closed form carries the profile's own validated integers."""

    def match(argv: list[str]) -> bool:
        return (
            len(argv) == 11
            and argv[:4] == ["docker", "build", "-t", IMAGE_NAME]
            and argv[4:10] == list(profile.build_args)
            and re.fullmatch(r"/[A-Za-z0-9._/-]{1,512}", argv[10]) is not None
            and ".." not in argv[10].split("/")
        )

    return match


def _owner_argv_matchers(profile: rprofile.RuntimeProfile, order_id: str | None = None) -> tuple:
    """The owner-scoped guarded-argv set for ONE frozen runtime
    profile: the SAME closed matchers as the original guard for
    every command whose form is profile-independent, and the
    profile-bound variants for the three surfaces that carry the
    subject identity (build args, exec user, detached hold
    user).  A per-owner matcher tuple — no global mutable
    identity binding.  The ONE new native-specific operation
    (the read-only devpts probe) is admitted for the canonical
    017-af entry ONLY, selected from the owner's OWN bound
    order id: the AB/AD/default guards keep the byte-for-byte
    old closed forms and refuse the new probe argv."""
    return (
        _match_docker_ps,
        _match_docker_version,
        _match_docker_info,
        _match_docker_rm,
        _make_docker_create_matcher(
            frozenset(f"{m}:{spec}" for m, spec in owner_tmpfs_specs(profile).items())
        ),
        _match_docker_start,
        _match_docker_wait,
        _match_docker_pull,
        _make_docker_build_matcher(profile),
        _match_docker_inspect,
        _match_docker_top,
        _match_docker_image_inspect,
        _match_docker_rmi,
        _make_docker_exec_matcher(profile.exec_user),
        _make_docker_exec_hold_matcher(profile.exec_user),
        _match_runtime_version,
    ) + (
        (_make_devpts_probe_matcher(profile.exec_user),) if order_id == rprofile.AF_ORDER_ID else ()
    )


# -- protected environment-file handoff binding (objective 017-s) ----------
# The exec allowlist admits a SINGLE ``--env-file <path>`` argument only
# when that exact path was bound for the run via bind_env_files().  The
# hosted CI path never binds, so its accepted argv set is unchanged; the
# local rehearsal binds its one protected generated env file (0600 under
# a 0700 root) and transfers ONLY the synthetic CODEX_HOME plus the
# generated fake-provider variable through it -- never via argv.
_ENV_FILE_BIND: frozenset[str] = frozenset()


def bind_env_files(paths: set[str]) -> None:
    """Bind the exact protected env-file paths this run may pass to
    ``docker exec --env-file``.  Paths must be absolute, syntactically
    clean (no NUL, no ``..`` component) and bounded.  The bind is
    run-scoped module state: an unbound or differently-spelled path is
    refused by the guard exactly like any other untrusted argv."""
    global _ENV_FILE_BIND
    for path in paths:
        if (
            not isinstance(path, str)
            or not path.startswith("/")
            or "\x00" in path
            or len(path) > 4096
            or ".." in path.split("/")
        ):
            raise FixtureError("env-file-untrusted")
    _ENV_FILE_BIND = frozenset(paths)


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
    matchers: tuple | None = None,
) -> Executor:
    """Runtime NO-CODEX proof: the closed allowlist is the only
    execution path, every call consumes REMAINING shared-deadline
    budget (never a fresh phase budget), and the host ledger
    charges the admission BEFORE work and the drained output AFTER.
    The ledger is REQUIRED: no host command may execute without
    being admitted (charged before work) and accounted (charged
    after); refused argv is counted as a refusal and never
    executed.  ``matchers`` (default: the module's original closed
    set) is the OWNER-SCOPED allowlist: the original callers keep
    the byte-for-byte original matcher tuple, and the owner-UID
    variant passes its own per-owner tuple built from the SAME
    closed factories (no global mutable identity binding)."""

    allowed = _ARGV_MATCHERS if matchers is None else matchers

    def guarded(argv: list[str], timeout: float) -> ExecResult:
        for element in argv:
            if not isinstance(element, str):
                ledger.refuse()
                raise FixtureError("argv-untrusted")
        if not any(matcher(argv) for matcher in allowed):
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


def remove_owned_image_exact(
    executor: Executor, image_id: str, cleanup_failures: list[str]
) -> str | None:
    """Remove the EXACT registered owned image id and verify the
    outcome.  Returns None when the removal command itself failed
    (recorded as ``image-rmi-failed``; the caller's state is left
    unchanged) and otherwise the CLOSED post-removal state:
    ``absent-verified`` (a SUCCESSFUL query that reports no such
    image), ``present-unexpected`` (still present after a claimed
    removal) or ``query-failed-unverified`` (no authoritative
    missing-object marker — a daemon/query failure is NEVER verified
    absence).  Shared by the hosted CI run and the order-bound local
    017-s rehearsal so the verified-absence semantics cannot drift."""
    rmi = executor(["docker", "rmi", image_id], _QUERY_TIMEOUT)
    if rmi.returncode != 0:
        cleanup_failures.append("image-rmi-failed")
        return None
    inspect_result = executor(["docker", "image", "inspect", image_id], _QUERY_TIMEOUT)
    if inspect_result.returncode == 0:
        cleanup_failures.append("image-still-present")
        return "present-unexpected"
    if _NO_SUCH_OBJECT_RE.search(inspect_result.output.decode("ascii", "replace")):
        return "absent-verified"
    cleanup_failures.append("image-absence-unverified")
    return "query-failed-unverified"


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
    image_ref: str,
    name: str,
    owned_label: str,
    env: dict[str, str],
    tmpfs_specs: dict[str, str] | None = None,
) -> list[str]:
    """The exact confinement create-argv: controller UID 21001 as
    PID1, dedicated nonroot identity, all capabilities dropped,
    no-new-privileges, explicit builtin seccomp, read-only rootfs
    with only the owned bounded tmpfs budgets plus the explicitly
    bounded /dev/shm, private network, no host mounts/devices, and
    ``--log-driver none`` (verified by inspection, never by
    ``docker logs``).  ``tmpfs_specs`` (the owner-UID variant only)
    substitutes the closed spec strings for the subject-owned
    mounts (frozen profile identities); None keeps the module
    constant byte-for-byte."""
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
    specs = TMPFS_SPECS if tmpfs_specs is None else tmpfs_specs
    for mountpoint in sorted(specs):
        argv += ["--tmpfs", f"{mountpoint}:{specs[mountpoint]}"]
    for key in sorted(env):
        argv += ["-e", f"{key}={env[key]}"]
    argv.append(image_ref)
    return argv


FIXTURE_BUILD_SOURCES = (
    "cache_native_fixture_model.py",
    "cache_native_fixture_controller.py",
    "cache_native_fixture_standin.py",
    "cache_native_fixture_export_client.py",
)


def prepare_build_context(
    repo: Path,
    artifact_dir: Path,
    context: Path,
    dockerfile_bytes: bytes,
    artifact: dict[str, object],
    profile_data: bytes | None = None,
) -> None:
    """The reviewed allowlisted build context: the pinned-base
    Dockerfile bytes, the four fixture sources, the verified public
    binary, and the public LICENSE/NOTICE identities -- every copy
    re-hashed AFTER writing.  ``context`` and ``artifact_dir`` must
    already be fresh owned subdirectories of the registered work
    root.  Shared by the hosted CI run and the order-bound local
    017-s rehearsal so the local build context cannot drift from the
    reviewed one.  ``profile_data`` (the owner-UID variant only) is
    the closed canonical identity record bytes written as the fixed
    profile DATA file and re-hashed AFTER writing; the owner variant
    additionally ships the inert identity contract module (with the
    same post-write byte check) because it is the single in-image
    source of truth for the subject identity; None keeps the
    original build context byte-for-byte unchanged."""
    (context / "Dockerfile").write_bytes(dockerfile_bytes)
    for name in FIXTURE_BUILD_SOURCES:
        src = (repo / "scripts" / name).read_bytes()
        (context / name).write_bytes(src)
        if sha256_file(context / name) != hashlib.sha256(src).hexdigest():
            raise FixtureError("context-mismatch")
    shutil.copyfile(artifact_dir / model.ARTIFACT_BINARY_NAME, context / model.ARTIFACT_BINARY_NAME)
    if sha256_file(context / model.ARTIFACT_BINARY_NAME) != artifact["binary_sha256"]:
        raise FixtureError("context-mismatch")
    shutil.copyfile(artifact_dir / "LICENSE", context / "codex-0.164.0-license.txt")
    if sha256_file(context / "codex-0.164.0-license.txt") != artifact["license_sha256"]:
        raise FixtureError("context-mismatch")
    shutil.copyfile(artifact_dir / "NOTICE", context / "codex-0.164.0-notice.txt")
    if sha256_file(context / "codex-0.164.0-notice.txt") != artifact["notice_sha256"]:
        raise FixtureError("context-mismatch")
    if profile_data is not None:
        ident_src = (repo / "scripts" / rprofile.IDENTITY_MODULE_NAME).read_bytes()
        ident_dest = context / rprofile.IDENTITY_MODULE_NAME
        ident_dest.write_bytes(ident_src)
        if sha256_file(ident_dest) != hashlib.sha256(ident_src).hexdigest():
            raise FixtureError("context-mismatch")
        data_path = context / rprofile.PROFILE_DATA_NAME
        data_path.write_bytes(profile_data)
        if sha256_file(data_path) != hashlib.sha256(profile_data).hexdigest():
            raise FixtureError("context-mismatch")


def verify_dockerfile_base(repo, dockerfile_name: str = "cache_native_fixture.Dockerfile") -> bytes:
    """The reviewed Dockerfile base check (shared by the hosted CI
    run and the order-bound local 017-s rehearsal): exactly one
    FROM, digest-pinned to the reviewed Python 3.12 base literal,
    and the same embedded literal present in the repository
    Dockerfile (byte-identity, not transcription).  Returns the
    fixture Dockerfile bytes for the build context.  The default
    name is the ORIGINAL fixture Dockerfile (hosted CI and the
    017-s rehearsal keep their exact reviewed input); the
    owner-UID variant passes its own distinct file, which the
    same base law pins."""
    from pathlib import Path

    repo = Path(repo)
    dockerfile_path = repo / "scripts" / dockerfile_name
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
    return dockerfile_bytes


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


def _new_container(
    executor: Executor,
    index: int,
    scenario: str,
    env: dict[str, str],
    prefix: str = "017r",
    on_intent: Callable[[str], None] | None = None,
    tmpfs_specs: dict[str, str] | None = None,
) -> str:
    """Fresh name + ownership label; pre-existing collision is a
    fixed failure (never adopted); the ACTUAL returned bare 64-hex
    CID is validated and registered as owned BEFORE any start.
    ``prefix`` is the CLOSED container namespace (the hosted R
    scenario slugs under 017r; the order-bound local 017-s slugs
    under 017s) — both are admitted by the guard grammar, and the
    exact name is collision-checked before create.
    ``on_intent`` (optional; local 017-s only) is invoked with the
    exact fresh create name AFTER the collision check and BEFORE
    the docker create, so the owner can persist the exact fresh
    ownership intent before the external mutation (the create/
    response gap is then recoverable data, never an adopted
    resource); hosted callers pass None and the command sequence
    is unchanged."""
    if prefix not in ("017r", "017s"):
        raise FixtureError("container-namespace-untrusted")
    name = f"slaif-fixture-{prefix}-{scenario}-{os.getpid()}-{index}-{uuid.uuid4().hex[:8]}"
    label = f"slaif-owned-fixture-{prefix}={uuid.uuid4().hex}"
    if _ps_filter(executor, f"name={name}") != "absent":
        raise FixtureError("name-collision")
    if on_intent is not None:
        on_intent(name)
    result = executor(build_run_conf_argv(IMAGE_NAME, name, label, env, tmpfs_specs), RUN_TIMEOUT)
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
    exec_user: str | None = None,
) -> ExecResult:
    # The exec user: the historical callers pass the fixture uid
    # and the closed ``uid:uid`` form is built as before; the
    # owner-UID variant passes the frozen profile's exact
    # independent ``uid:gid`` (never assumed equal).
    user = _closed_exec_user(uid, exec_user)
    argv = ["docker", "exec"]
    if pty:
        argv += ["-it"]
    argv += ["--user", user]
    for key in sorted(env):
        argv += ["-e", f"{key}={env[key]}"]
    argv += [container_id] + tail
    return executor(argv, timeout)


def _closed_exec_user(uid: int, exec_user: str | None) -> str:
    """The closed exec-user law: ``uid:uid`` for the historical
    callers (byte-for-byte the original form), or the exact
    caller-supplied ``uid:gid`` string — which is admitted only in
    the strict closed decimal form of two independent nonroot
    fixture IDs in the closed Linux range (fixed refusal, no
    echo).  No other user form reaches the guarded executor from
    this module."""
    if exec_user is None:
        return f"{uid}:{uid}"
    if not re.fullmatch(r"\d{1,10}:\d{1,10}", exec_user):
        raise FixtureError("exec-user-form")
    left, right = (int(part) for part in exec_user.split(":"))
    for value in (left, right):
        if value == 0 or value > 4294967294:
            raise FixtureError("exec-user-range")
    return exec_user


def _exec_env_file(
    executor: Executor,
    container_id: str,
    uid: int,
    tail: list[str],
    env: dict[str, str],
    env_file: str,
    timeout: float = RUN_TIMEOUT,
    pty: bool = False,
    exec_user: str | None = None,
) -> ExecResult:
    """Exec with the protected generated env file: the file PATH is
    bound for the run (bind_env_files) and admitted by the closed
    guard grammar; the file's VALUES never appear on argv.  Closed
    fixture-internal variables may still be passed via -e.  The
    ``exec_user`` law is the closed one of :func:`_exec` (the
    owner-UID variant passes the frozen independent ``uid:gid``)."""
    if env_file not in _ENV_FILE_BIND:
        raise FixtureError("env-file-unbound")
    argv = ["docker", "exec"]
    if pty:
        argv += ["-it"]
    argv += ["--user", _closed_exec_user(uid, exec_user)]
    for key in sorted(env):
        argv += ["-e", f"{key}={env[key]}"]
    argv += ["--env-file", env_file, container_id] + tail
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


# -- Closed stand-in failure reason channel -----------------------------------
# When a scenario's stand-in exec exits nonzero, the stand-in has
# (by its closed-record law) already emitted its own fixed reason
# token on the captured stdout.  The runner may carry exactly one
# such token — admitted ONLY by explicit allowlist membership —
# into the runner's closed CI record, so the disposable job log can
# reveal the child cause.  Unknown, malformed or missing tokens
# stay generic (reason only); raw output is never propagated.
_STANDIN_RECORD = "slaif-fixture-standin-v1"
_STANDIN_FAIL_REASONS = frozenset(
    {
        "capabilities-unreadable",
        "cpu-mismatch",
        "cpu-unlimited",
        "cpu-unreadable",
        "denial-inconclusive",
        "denial-unexpected",
        "diagnostic-item",
        "diagnostic-item-count",
        "diagnostic-text-mismatch",
        "diagnostic-wire",
        "error-wire",
        "expected-unissued",
        "expected-writable-mount-missing",
        "filesystem",
        "final-item-type",
        "final-role",
        "final-text-mismatch",
        "final-tools-present",
        "hang-child-not-reaped",
        "hang-token-invalid",
        "identity-not-subject",
        "issue-arguments",
        "issue-identity",
        "issue-item",
        "issue-missing",
        "issue-wire",
        "memory-missing-or-unlimited",
        "mode-invalid",
        "model-import",
        "mount-not-directory",
        "mountinfo-malformed",
        "mountinfo-oversized",
        "mountinfo-unreadable",
        "namespace-invalid",
        "namespace-unreadable",
        "no-libc",
        "parent-namespace-invalid",
        "pids-missing-or-unlimited",
        "platform-not-x86_64",
        "presence-unverified",
        "profile-path-exists",
        "profile-schema",
        "provider-json",
        "provider-protocol",
        "provider-socket",
        "provider-timeout",
        "provider-unicode",
        "pty-not-attached",
        "response-overbound",
        "response-truncated",
        "response-unframed",
        "ro-probe-exists",
        "rootfs-proof-inconclusive",
        "rootfs-writable",
        "run-token-invalid",
        "self-deadline",
        "self-deadline-expired",
        "self-deadline-invalid",
        "sse-created-shape",
        "sse-duplicate",
        "sse-empty",
        "sse-event-empty",
        "sse-event-mismatch",
        "sse-event-unknown",
        "sse-incomplete",
        "sse-item-count",
        "sse-item-mismatch",
        "sse-item-role",
        "sse-item-shape",
        "sse-item-unknown",
        "sse-order",
        "sse-output-mismatch",
        "sse-response-id",
        "sse-status",
        "standin-failure",
        "stop-identity-invalid",
        "stop-not-confirmed",
        "stop-pidfd-unavailable",
        "stop-target-absent",
        "stop-token-invalid",
        "swap-derivation-invalid",
        "swap-missing",
        "swap-nonzero",
        "swap-unlimited",
        "unlisted-writable-mount",
        "use-wire",
    }
)
_STANDIN_DETAIL: str | None = None
# Closed failure diagnostics for the disposable job log: EXACTLY ONE
# fixed stage token and (on the closed validation category) the
# model's fixed-format field message — no tracebacks, no raw
# exceptions, no measured values, no other record content.  The
# stage set is closed: the fixed phase tokens below plus the model's
# closed scenario names (set while the scenario loop runs).
_STAGE: str = "start"
# The stage of the ORIGINAL in-flight failure, preserved separately
# from _STAGE: the cleanup umbrella always moves _STAGE to
# "cleanup", and the original failure must not be misattributed to
# it.  "cleanup" is reported only for failures that occurred in the
# cleanup path itself (or when no earlier stage is attributable).
_FAILURE_STAGE: str | None = None
_FAILURE_STAGES: tuple[str, ...] = (
    "start",
    "work-root",
    "artifact",
    "build-context",
    "collision",
    "preflight",
    "pull",
    "build",
    "sentinels",
    "teardown",
    "publish",
    "cleanup",
)


# Closed admission for the model's fixed-format validation messages
# on the job log: EXACT known category/field combinations only.
# The category is a finite tuple, the field must be a member of the
# model's closed VALIDATION_FIELD_UNIVERSE (finite, explicit — a
# regex-shaped match is NEVER a waiver for arbitrary field text),
# and the fixed output is reconstructed, not echoed.  Anything
# else — including a canary or an oversized field — stays generic.
_MODEL_FIELD_CATEGORIES: tuple[str, ...] = (
    "state",
    "bound",
    "identity",
    "set",
    "type",
    "enum",
)
_MODEL_VALIDATION_FIXED = frozenset(
    {
        "closed record field set mismatch",
        "closed record schema tag unknown",
        "closed record schema tag mismatch",
        "closed record must be an object",
        "budget bound exceeded: issued_calls",
        "budget bound exceeded: lifetime deadline",
        "budget bound exceeded: lifetime_seconds",
        "budget bound exceeded: output_bytes",
    }
)
_MODEL_FIELD_MSG_RE = re.compile(
    r"^closed record field (" + "|".join(_MODEL_FIELD_CATEGORIES) + r") invalid: ([a-z0-9_-]+)$"
)
_MODEL_DIGEST_MSG_RE = re.compile(r"^closed record digest invalid: ([a-z0-9_-]+)$")


def _model_validation_reason(exc: BaseException) -> str:
    """Map a closed-record validation rejection to its fixed-format
    field message ONLY for the exact known category/field
    combinations: fixed no-field forms by exact membership, and
    field forms reconstructed from the closed category plus a field
    that is a member of the model's closed field universe."""
    msg = str(exc)
    if msg in _MODEL_VALIDATION_FIXED:
        return msg
    m = _MODEL_FIELD_MSG_RE.fullmatch(msg)
    if m is not None and m.group(2) in model.VALIDATION_FIELD_UNIVERSE:
        return f"closed record field {m.group(1)} invalid: {m.group(2)}"
    m = _MODEL_DIGEST_MSG_RE.fullmatch(msg)
    if m is not None and m.group(1) in model.VALIDATION_FIELD_UNIVERSE:
        return f"closed record digest invalid: {m.group(1)}"
    return "record-validation"


def _failure_payload(reason: str, stage: str, detail: str | None = None) -> dict[str, object]:
    """The closed failure record for the job log.  ``reason`` is a
    fixed token (runner FixtureError token, the model's fixed-format
    validation message, ``deadline-expired`` or ``internal``);
    ``stage`` one closed stage token; ``detail`` ONLY the
    allowlisted stand-in fail token (absent otherwise)."""
    if stage not in _FAILURE_STAGES and stage not in model.SCENARIO_NAMES:
        raise FixtureError("diagnostic-stage")
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": "fail",
        "reason": reason,
        "stage": stage,
    }
    if detail is not None:
        payload["detail"] = detail
    return payload


def _standin_fail_reason(output: bytes) -> str | None:
    """The LAST closed stand-in fail token on the captured output,
    admitted only by explicit allowlist membership; an unknown
    token, a malformed or truncated record, another record type, a
    non-fail status, or non-ASCII bytes all stay generic (None)."""
    try:
        text = output.decode("ascii")
    except UnicodeDecodeError:
        return None
    detail = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if not isinstance(obj, dict):
            continue
        if obj.get("record") != _STANDIN_RECORD or obj.get("status") != "fail":
            continue
        reason = obj.get("reason")
        if isinstance(reason, str) and reason in _STANDIN_FAIL_REASONS:
            detail = reason
    return detail


def _note_standin_detail(result: ExecResult) -> None:
    """Retain the child's closed fail token for the runner's closed
    record (called only on a stand-in exec failure)."""
    global _STANDIN_DETAIL
    detail = _standin_fail_reason(result.output)
    if detail is not None:
        _STANDIN_DETAIL = detail


def _controller_ready(executor: Executor, container_id: str, ledger: _RunLedger) -> int:
    """The fixed 21001 in-container probe (closed expected object:
    PID1 uid, health, exact controller-root facts, exact owned
    existence of every denied target) must match EXACTLY."""
    result = _exec(executor, container_id, CONTROLLER_UID, ["python3", "-c", CONTROLLER_PROBE], {})
    if result.returncode != 0:
        # Closed readiness diagnosis (017-y): the only closed fact
        # carried from a nonzero readiness exec is the probe's own
        # exact finite closed failure record, as a REFINEMENT of the
        # original controller-not-ready category; anything else is
        # the fixed unknown (the original generic token).  The
        # readiness request/time/output already charged the SAME
        # ledger and END above; a raw exception or Docker failure is
        # not one of the measured causes.
        # The failure path records NO healthz count — that is an
        # unrecorded quantity, never a claim of zero actual
        # readiness requests.
        cause = _controller_probe_fail_reason(result.output)
        if cause is not None:
            raise FixtureError(f"controller-not-ready:{cause}")
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


#: The single finite lifecycle fact selected by the closed
#: readiness diagnosis (017-y): the container's own
#: ``.State.Status`` line (never the full State object).
_LIFECYCLE_STATUS_FORMAT = "{{.State.Status}}"


def _controller_lifecycle_exited(executor: Executor, container_id: str) -> bool | None:
    """The ONE conditional bounded lifecycle query of the closed
    readiness diagnosis (order 017-y): issued ONLY after a
    nonzero bounded readiness exec whose output is NOT the
    probe's exact closed failure record (the probe may have
    failed before it ran, e.g. the container already exited).
    Exactly one allowlisted read-only ``docker inspect`` of the
    SAME already-registered CID selects the single finite fact
    ``.State.Status`` — no raw logs, no error text, no full
    State export, no broad process/container listing, no
    subject/PID oracle.  It runs through the SAME guarded
    executor, so the SAME owner ledger charges the admission
    before the work and the output after, clamped by the SAME
    bounded query deadline of the run's END.  Honest
    interpretation: exactly the closed line ``exited`` is the
    finite selected fact (True); any other status, any other
    output shape and EVERY query failure (a nonzero exit, an
    over-bound or unparseable output, a bounded ``_OwnedTimeout``
    — already charged to the SAME ledger by the guarded executor
    before it is re-raised — and a transport ``OSError``) is
    UNKNOWN (None) — query failure is NOT absence, the SAME
    ledger/END charges are preserved with no reset or refund, and
    the caller keeps the original fixed-unknown generic
    ``controller-not-ready`` token (its first cause is preserved,
    never erased).  Only these concrete query failures are
    closed; KeyboardInterrupt and other cancellation are NOT
    caught here and propagate unchanged."""
    try:
        raw = _query(
            executor,
            ["docker", "inspect", "--format", _LIFECYCLE_STATUS_FORMAT, container_id],
        )
    except FixtureError:
        return None
    except (_OwnedTimeout, OSError):
        # a bounded deadline timeout (charged already) or a
        # transport failure: the query outcome is UNKNOWN — the
        # original readiness cause is preserved by the caller
        return None
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        return None
    return text == "exited\n"


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


def _standin_record(
    output: bytes,
    mode: str,
    extra_fields: frozenset[str],
    subject_uid: int = SUBJECT_UID,
) -> dict[str, object]:
    """Closed shape check of a slaif-fixture-standin-v1 record.
    The historical callers keep the fixed 21002 subject law
    (byte-for-byte the original); the owner-UID variant passes
    the frozen profile's exact subject uid (the measured record
    still carries the ACTUAL measured uid — this is the closed
    identity law, not a relabeling)."""
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
    if record["uid"] != subject_uid:
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


def _verify_confinement(
    host_config: object,
    config: object,
    tmpfs_budgets: tuple[tuple[str, int, int, int], ...] = model.DEFAULT_TMPFS_BUDGETS,
) -> None:
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
    if not isinstance(tmpfs, dict) or set(tmpfs) != set(m for m, _s, _u, _g in tmpfs_budgets):
        raise FixtureError("confinement-tmpfs-set")
    for mount, spec in tmpfs.items():
        if not isinstance(spec, str):
            raise FixtureError("confinement-tmpfs-spec")
        facts = _tmpfs_spec_facts(spec)
        mount_spec = next((size, uid, gid) for m, size, uid, gid in tmpfs_budgets if m == mount)
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


def prepare_container(
    executor,
    index,
    scenario,
    env,
    created,
    ledger,
    prefix: str = "017r",
    on_registered: Callable[[str], None] | None = None,
    on_intent: Callable[[str], None] | None = None,
    tmpfs_specs: dict[str, str] | None = None,
) -> str:
    """The shared scenario preparation: fresh owned name/label, the
    ACTUAL returned CID validated and registered BEFORE any start,
    then start + controller readiness.  Identical command sequence to
    the pre-split scenarios; ``prefix`` selects the closed container
    namespace (hosted 017r scenarios vs order-bound local 017s).
    ``on_registered`` (optional; local 017-s only) is invoked with
    the ACTUAL returned CID AFTER it is registered as owned and
    BEFORE any start, so the caller can persist exact ownership
    before the external mutation; hosted callers pass None and the
    command sequence is unchanged.  ``on_intent`` (optional; local
    017-s only) is invoked with the exact fresh create name AFTER
    the collision check and BEFORE docker create, so the fresh
    ownership intent is persisted before the external mutation;
    hosted callers pass None."""
    cid = _new_container(
        executor, index, scenario, env, prefix, on_intent=on_intent, tmpfs_specs=tmpfs_specs
    )
    created.append(cid)
    if on_registered is not None:
        on_registered(cid)
    _start_container(executor, cid)
    try:
        _controller_ready(executor, cid, ledger)
    except FixtureError as exc:
        # Closed readiness diagnosis (order 017-y): when the
        # nonzero readiness exec produced NO closed probe record
        # (the fixed unknown — the probe may never have run, e.g.
        # the container already exited), exactly ONE conditional
        # bounded lifecycle query of the SAME registered CID
        # selects the single finite fact (.State.Status) and
        # refines the original category.  A measured closed
        # probe cause, any other status, any other output shape
        # and every query failure (query failure is NOT absence)
        # keep the original fixed-unknown token; the actual
        # first cause is preserved through abort/cleanup/
        # publication.  No raw output is ever persisted.
        if (
            str(exc) == "controller-not-ready"
            and _controller_lifecycle_exited(executor, cid) is True
        ):
            raise FixtureError("controller-not-ready:container-exited") from exc
        raise
    return cid


def measure_controller_confinement_on(
    executor,
    cid,
    tmpfs_budgets: tuple[tuple[str, int, int, int], ...] | None = None,
) -> dict[str, str]:
    """NON-CONSUMING controller-side confinement inspection on an
    already-prepared exact CID (local 017-s prepared target): the
    same closed confinement proof as the hosted measurement (the
    real log-driver field, the controller identity, the full
    host/config confinement including the absence of any host
    mounts) WITHOUT the consuming diagnostic POST.  ``tmpfs_budgets``
    (the owner-UID variant only) is the closed spec of the frozen
    subject-owned mounts; None keeps the original budgets."""
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
    _verify_confinement(
        host_config,
        config,
        model.DEFAULT_TMPFS_BUDGETS if tmpfs_budgets is None else tmpfs_budgets,
    )
    return {
        "log_config": "none",
        "config_user": f"{CONTROLLER_UID}:{CONTROLLER_UID}",
    }


def observe_controller_on(
    executor, cid, env_base, ledger, profile: rprofile.RuntimeProfile | None = None
) -> dict[str, object]:
    """Bounded trusted NON-CONSUMING observation of the ACTUAL
    controller state on an already-prepared exact CID (local 017-s
    lifecycle observe): the stand-in under 21002 reads the closed
    /state record (declared scenario, the controller's own
    cumulative request count, the one-shot diagnostic state).  It
    makes no model POST and consumes the diagnostic never; the
    host does not charge the provider API budgets for an
    observation command, and the measured controller counters are
    reported as separate actual facts (a zero host-charge delta
    does not by itself prove zero provider traffic)."""
    if profile is not None and profile.profile != rprofile.PROFILE_OWNER_UID:
        raise FixtureError("observe-profile-invalid")
    subject_uid = profile.subject_uid if profile is not None else SUBJECT_UID
    exec_user = profile.exec_user if profile is not None else None
    result = _exec(
        executor,
        cid,
        subject_uid,
        ["python3", STANDIN_PATH, "--mode", "observe"],
        dict(env_base),
        exec_user=exec_user,
    )
    if result.returncode != 0:
        _note_standin_detail(result)
        raise FixtureError("observe-failed")
    record = _standin_record(
        result.output,
        "observe",
        frozenset({"scenario", "wire_requests", "diagnostic_state", "raw_content_retained"}),
        subject_uid=subject_uid,
    )
    if record["raw_content_retained"] is not False:
        raise FixtureError("observe-record-state")
    if (
        not isinstance(record["wire_requests"], int)
        or isinstance(record["wire_requests"], bool)
        or record["wire_requests"] < 0
    ):
        raise FixtureError("observe-record-state")
    if record["scenario"] not in ("diagnostic", "tool-cycle") or record["diagnostic_state"] not in (
        "unobserved",
        "observed",
    ):
        raise FixtureError("observe-record-state")
    return {
        "scenario": record["scenario"],
        "wire_requests": record["wire_requests"],
        "diagnostic_state": record["diagnostic_state"],
    }


def measure_controller_on(executor, cid, env_base, ledger) -> dict[str, object]:
    """Controller-side measurement on an already-prepared exact CID:
    actual inspection of the declared confinement (the real
    log-driver field, never docker logs; the controller identity; the
    full host/config confinement including the absence of any host
    mounts) plus the ACTUAL no-tools diagnostic on the live wire
    (one request, fixed assistant final text, no tool call)."""
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
    result = _exec(
        executor,
        cid,
        SUBJECT_UID,
        ["python3", STANDIN_PATH, "--mode", "diagnostic"],
        dict(env_base),
    )
    if result.returncode != 0:
        _note_standin_detail(result)
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
    return {
        "requests": record["requests"],
        "attempts": record["attempts"],
    }


def measure_subject_on(executor, cid, env, parent, ledger) -> dict[str, object]:
    """Subject-side (exec as 21002) measurement on an already-
    prepared exact CID: the stand-in's closed measurement record,
    model-validated against fresh budgets.  ``env`` is the container
    environment (including the scenario marker) exactly as the
    pre-split scenario built it."""
    measure_env = _standin_env(env, *parent)
    measure_env["SLAIF_FIXTURE_TMPFS_SPECS"] = TMPFS_SPEC_ENV
    measure_env["SLAIF_FIXTURE_EXPECTED_CPU"] = str(model.CPU_LIMIT)
    measure_env["SLAIF_FIXTURE_PRESENCE_SHA256"] = PRESENCE_SHA256
    result = _exec(
        executor, cid, SUBJECT_UID, ["python3", STANDIN_PATH, "--mode", "measure"], measure_env
    )
    if result.returncode != 0:
        _note_standin_detail(result)
        raise FixtureError("exec-measurement-failed")
    record = _parse_closed_record(result.output)
    model.validate_exec_measurement(record, model.FixtureBudgets())
    return _curated_subject_facts(record)


def _curated_subject_facts(record: dict[str, object]) -> dict[str, object]:
    """Closed facts (measured, never raw): swap source, the keyring
    denial errnos and the reconciled writable-data facts (the
    measured mount table facts, not an argv claim)."""
    return {
        "swap_source": record["swap_source"],
        "uid": record["uid"],
        "gid": record["gid"],
        "groups": record["groups"],
        "keyring_errno": record["keyring_errno"],
        "memory_limit_bytes": record["memory_limit_bytes"],
        "pids_limit": record["pids_limit"],
        "cpu_limit": record["cpu_limit"],
        "writable_mounts": record["writable_mounts"],
        "mounts_scanned": record["mounts_scanned"],
        "masked_null_aliases": record["masked_null_aliases"],
    }


def measure_subject_on_profile(
    executor,
    cid,
    env,
    parent,
    ledger,
    profile: rprofile.RuntimeProfile,
) -> dict[str, object]:
    """Subject-side measurement on the owner-UID variant: the SAME
    closed stand-in measurement as :func:`measure_subject_on`,
    exec'd as the frozen profile's exact independent ``uid:gid``,
    and model-validated with the EXPLICIT v2 subject-measurement
    record bound to the frozen profile subject (UID and GID
    independent, expected effective groups exactly the primary
    GID; the v1 record tag and the v1 fixed-21002 consumer are
    refused in both directions — a v1 record here is a version
    refusal, and the v1 validator rejects any v2 tag)."""
    measure_env = _standin_env(env, *parent)
    measure_env["SLAIF_FIXTURE_TMPFS_SPECS"] = owner_tmpfs_spec_env(profile)
    measure_env["SLAIF_FIXTURE_EXPECTED_CPU"] = str(model.CPU_LIMIT)
    measure_env["SLAIF_FIXTURE_PRESENCE_SHA256"] = PRESENCE_SHA256
    result = _exec(
        executor,
        cid,
        profile.subject_uid,
        ["python3", STANDIN_PATH, "--mode", "measure"],
        measure_env,
        exec_user=profile.exec_user,
    )
    if result.returncode != 0:
        _note_standin_detail(result)
        raise FixtureError("exec-measurement-failed")
    record = _parse_closed_record(result.output)
    if record.get("record") != model.SCHEMA_EXEC_MEASUREMENT_V2:
        raise FixtureError("exec-measurement-version")
    model.validate_exec_measurement_v2(
        record,
        model.FixtureBudgets(tmpfs_budgets=owner_tmpfs_budgets(profile)),
        profile.subject_uid,
        profile.subject_gid,
    )
    return _curated_subject_facts(record)


def pty_attach_on(
    executor,
    cid,
    env_base,
    run_token: str,
    ledger,
    env_file: str | None = None,
    profile: rprofile.RuntimeProfile | None = None,
) -> dict[str, object]:
    """PTY/interactive attachment proof on an already-prepared exact
    CID (the exact future native attachment path): stdin must be a
    TTY, closed terminal size facts, the fresh synthetic CODEX_HOME +
    separate early-beta profile validated against the closed model
    profile schema.  ``env_file`` (local 017-s only; the hosted CI
    path passes None) additionally transfers the protected generated
    env file through the bound ``--env-file`` grammar -- its values
    never appear on argv -- and the stand-in reports the closed
    ``env_handoff_verified`` boolean for it.  ``profile`` (the
    owner-UID variant only) execs as the frozen profile's exact
    independent ``uid:gid`` and validates the record's subject
    identity, workspace ownership and the EXPLICIT v2 synthetic-
    profile record against that frozen subject; None keeps the
    original fixed-21002 behavior byte-for-byte."""
    if profile is not None and profile.profile != rprofile.PROFILE_OWNER_UID:
        raise FixtureError("pty-profile-invalid")
    subject_uid = profile.subject_uid if profile is not None else SUBJECT_UID
    exec_user = profile.exec_user if profile is not None else None
    pty_env = dict(env_base)
    pty_env["SLAIF_RUN_TOKEN"] = run_token
    if env_file is None:
        result = _exec(
            executor,
            cid,
            subject_uid,
            ["python3", STANDIN_PATH, "--mode", "pty"],
            pty_env,
            pty=True,
            exec_user=exec_user,
        )
    else:
        result = _exec_env_file(
            executor,
            cid,
            subject_uid,
            ["python3", STANDIN_PATH, "--mode", "pty"],
            pty_env,
            env_file,
            pty=True,
            exec_user=exec_user,
        )
    if result.returncode != 0:
        _note_standin_detail(result)
        raise FixtureError("pty-attach-failed")
    record = _standin_record(
        result.output,
        "pty",
        frozenset(
            {
                "pty_attached",
                "term_rows",
                "term_cols",
                "terminal_properties_closed_only",
                "env_handoff_verified",
                "workspace",
                "profile",
            }
        ),
        subject_uid=subject_uid,
    )
    if record["pty_attached"] is not True or record["terminal_properties_closed_only"] is not True:
        raise FixtureError("pty-record-state")
    if not isinstance(record["env_handoff_verified"], bool):
        raise FixtureError("pty-record-state")
    workspace = record["workspace"]
    if (
        not isinstance(workspace, dict)
        or set(workspace) != {"path", "mode", "uid"}
        or workspace["path"] != "/run/slaif-subj/work"
        or workspace["mode"] != 0o700
        or workspace["uid"] != subject_uid
    ):
        raise FixtureError("pty-workspace-state")
    for key in ("term_rows", "term_cols"):
        if not isinstance(record[key], int) or isinstance(record[key], bool) or record[key] < 0:
            raise FixtureError("pty-record-state")
    # The host allocated the terminal at the fixed closed size; the
    # measured size must agree (the attachment is actual, not flag-only).
    if record["term_rows"] != PTY_ROWS or record["term_cols"] != PTY_COLS:
        raise FixtureError("pty-term-mismatch")
    profile = record["profile"]
    if exec_user is None:
        model.validate_profile_record(profile)
    else:
        model.validate_profile_record_v2(profile, subject_uid)
    if (
        profile["profile_table_used"] is not False
        or profile["profile_file"] != "early-beta.config.toml"
        or profile["env_key_name"] != "SLAIF_SYNTHETIC_API_KEY"
    ):
        raise FixtureError("profile-record-state")
    return {
        "pty_attached": True,
        "profile_file": profile["profile_file"],
        "profile_sha256": profile["profile_sha256"],
        "profile_table_used": False,
        "env_handoff_verified": record["env_handoff_verified"],
        "workspace": {
            "path": workspace["path"],
            "mode": workspace["mode"],
            "uid": workspace["uid"],
        },
    }


def _sc_controller_measurement(executor, index, env_base, created, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "main"
    env["SLAIF_FIXTURE_SCENARIO"] = "diagnostic"
    cid = prepare_container(executor, index, "controller-measurement", env, created, ledger)
    _SC_FACTS["controller-measurement"] = measure_controller_on(executor, cid, env_base, ledger)
    cleanup_container(executor, cid)
    return "completed"


def _sc_exec_measurement(executor, index, env_base, created, parent, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "main"
    env["SLAIF_FIXTURE_SCENARIO"] = "tool-cycle"
    cid = prepare_container(executor, index, "exec-21002-measurement", env, created, ledger)
    _SC_FACTS["exec-21002-measurement"] = measure_subject_on(executor, cid, env, parent, ledger)
    cleanup_container(executor, cid)
    return "completed"


def _sc_pty_attach(executor, index, env_base, created, run_token: str, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "main"
    env["SLAIF_FIXTURE_SCENARIO"] = "tool-cycle"
    cid = prepare_container(executor, index, "pty-attach", env, created, ledger)
    facts = pty_attach_on(executor, cid, env_base, run_token, ledger)
    # The hosted CI summary keeps its exact R closed fact shape: the
    # local-only env-handoff boolean is retained for the local caller,
    # never published into the hosted record.
    _SC_FACTS["pty-attach"] = {
        key: value
        for key, value in facts.items()
        if key not in ("env_handoff_verified", "workspace")
    }
    cleanup_container(executor, cid)
    return "completed"


def _sc_synthetic_success(executor, index, env_base, created, ledger) -> str:
    env = dict(env_base)
    env["SLAIF_FIXTURE_MODE"] = "main"
    env["SLAIF_FIXTURE_SCENARIO"] = "tool-cycle"
    cid = prepare_container(executor, index, "synthetic-success", env, created, ledger)
    facts, payload, quiesce_record, descendants_before = synthetic_success_on(
        executor, cid, env_base, ledger
    )
    cleanup_container(executor, cid)
    _SC_FACTS["synthetic-success"] = facts
    _SC_EXPORT["payload"] = payload
    _SC_EXPORT["quiesce_record"] = quiesce_record
    _SC_TEARDOWN["cid"] = cid
    _SC_TEARDOWN["descendants_before"] = descendants_before
    return "completed"


def synthetic_success_on(executor, cid, env_base, ledger):
    """The full wire + quiesce + export + host revalidation +
    teardown-prep sequence on an already-prepared exact CID
    (container stays alive; the caller owns its removal).  Returns
    (closed facts, export payload bytes, quiesce record,
    descendants-before count)."""
    # -- the stand-in drives the REAL controller wire (2 requests) --
    result = _exec(
        executor, cid, SUBJECT_UID, ["python3", STANDIN_PATH, "--mode", "success"], dict(env_base)
    )
    if result.returncode != 0:
        _note_standin_detail(result)
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
    facts = {
        "issued_count": len(issued),
        "export_sha256": hashlib.sha256(payload).hexdigest(),
        "quiesce": "closed-pass",
        "export_revalidated": True,
        "standin_requests": record["requests"],
        "standin_attempts": record["attempts"],
        "controller_ledger_requests": snapshot["controller_ledger"]["requests"],
        "retained_capture_bytes": len(payload),
    }
    return facts, payload, quiesce_record, descendants_before


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
        _note_standin_detail(stop_result)
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
        _note_standin_detail(result)
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


def _retain_evidence(dest, payload: bytes, digest: str, work=None) -> str:
    """Atomically retain the published 0600 evidence at an explicit
    protected destination OUTSIDE the disposable work root: the
    published file inside the scratch root is never the only copy of
    the reviewable evidence (the scratch root is destroyed at the
    end of the run).

    ``work`` is the disposable root the destination must NOT lie
    inside; a caller that owns the destination explicitly (a
    protected destination of its own, e.g. the 017-x capability
    record) passes None and only the inside-work refusal is
    skipped — the ancestor trust, atomic no-overwrite, 0600-leaf
    and temp-only-cleanup law are UNCHANGED in either case.

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
    # The retained copy must OUTLIVE the scratch root: a destination
    # at or under the disposable work root is refused outright.
    if work is not None:
        work = Path(work)
        if not work.is_absolute():
            work = Path(os.getcwd()) / work
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
    global _FAILURE_STAGE, _STAGE, _STANDIN_DETAIL
    _SC_FACTS.clear()
    _SC_EXPORT.clear()
    _SC_TEARDOWN.clear()
    _STANDIN_DETAIL = None
    _STAGE = "start"
    _FAILURE_STAGE = None

    # -- ONE shared non-resettable run deadline (host + in-container) --
    deadline = _RunDeadline(time.monotonic() + TOTAL_ANCHOR_SECONDS)
    budgets = model.FixtureBudgets()
    ledger = _RunLedger(budgets)
    # The guarded + ledgered executor is the ONLY execution path for
    # EVERY host command, starting BEFORE any docker query.
    guarded = _guarded_execute(executor, deadline, ledger)

    # -- Reviewed Dockerfile base (byte-identical to the repo base) --
    dockerfile_bytes = verify_dockerfile_base(repo)

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
        state = remove_owned_image_exact(guarded, image_id, cleanup_failures)
        if state is not None:
            image_state = state

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
            _STAGE = "work-root"
            _create_work_root(work)
            work_root_owned = True
            context = _owned_subdir(work, "context")
            artifact_dir = _owned_subdir(work, "artifact")

            # -- Public pinned artifact (size+digest verified,
            #    bounded; LICENSE and NOTICE byte-identity verified) --
            _STAGE = "artifact"
            artifact = fetch_public_artifact(artifact_dir, deadline)

            # -- Build context: Dockerfile + sources + binary +
            #    license + notice (every copy byte-verified) --
            _STAGE = "build-context"
            prepare_build_context(repo, artifact_dir, context, dockerfile_bytes, artifact)

            env_base = {
                "SLAIF_FIXTURE_DEADLINE_ABS": repr(deadline.anchor),
                "SLAIF_FIXTURE_DEADLINE": str(int(TOTAL_ANCHOR_SECONDS)),
                "SLAIF_FIXTURE_PORT": str(CONTROLLER_PORT),
            }

            # -- Pre-existing image collision: never adopt, never
            #    overwrite (verified absence or fixed failure) --
            _STAGE = "collision"
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
            _STAGE = "preflight"
            engine_version, runtime_name, runtime_version = _engine_preflight(guarded)

            # -- Build the fixture image (pinned base, public pull) --
            _STAGE = "pull"
            result = guarded(["docker", "pull", PINNED_BASE], PULL_TIMEOUT)
            if result.returncode != 0:
                raise FixtureError("pull-failed")
            build_attempted = True
            _STAGE = "build"
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
            _STAGE = "sentinels"
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
                _STAGE = name
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
            _FAILURE_STAGE = _STAGE
        finally:
            # Preserve the ORIGINAL failure's stage before the
            # umbrella moves to "cleanup" (a failure that occurred in
            # the scenario phase must not be reported as cleanup).
            primary = sys.exc_info()[1]
            if primary is not None and _FAILURE_STAGE is None:
                _FAILURE_STAGE = _STAGE
            _STAGE = "cleanup"
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

            # A failure RAISED BY the cleanup path itself (distinct
            # from the preserved primary and from the recorded
            # cleanup_failures list) is a cleanup failure: its stage
            # is "cleanup".
            if (
                sys.exc_info()[1] is not None
                and sys.exc_info()[1] is not primary
                and _FAILURE_STAGE is None
            ):
                _FAILURE_STAGE = "cleanup"

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
        _STAGE = "teardown"
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
        _STAGE = "publish"
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
        # Report the ORIGINAL failure's stage (preserved separately
        # from _STAGE, which the cleanup umbrella always advances to
        # "cleanup"); fall back to the current stage when no original
        # failure stage is attributable.
        stage = _FAILURE_STAGE if _FAILURE_STAGE is not None else _STAGE
        print(json.dumps(_failure_payload(str(exc), stage, _STANDIN_DETAIL)))
        return 1
    except model.FixtureError as exc:
        # Closed-record validation rejection: the model's fixed-format
        # field message is a known validation-field category (closed
        # vocabulary, no measured values) — named, never raw.
        stage = _FAILURE_STAGE if _FAILURE_STAGE is not None else _STAGE
        print(json.dumps(_failure_payload(_model_validation_reason(exc), stage)))
        return 1
    except _OwnedTimeout:
        stage = _FAILURE_STAGE if _FAILURE_STAGE is not None else _STAGE
        print(json.dumps(_failure_payload("deadline-expired", stage)))
        return 1
    except Exception:
        stage = _FAILURE_STAGE if _FAILURE_STAGE is not None else _STAGE
        print(json.dumps(_failure_payload("internal", stage)))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
