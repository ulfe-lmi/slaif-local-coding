"""21002 Python stand-in for the serial right-pane native fixture (017-r).

Runs ONLY inside the disposable fixture image as UID/GID 21002 (the
native-subject identity a later foreground Codex client will attach
with, via ``docker exec --user 21002:21002``).  Stdlib only.

Every fact in the emitted closed records is MEASURED from this process
and its environment, never authored: identity from the kernel,
capabilities/seccomp/NoNewPrivs from /proc/self/status (proc names
CapAmb/CapBnd/CapEff/CapInh/CapPrm — all five sets, no skip or
default zero), namespaces compared against the disposable parent's
bounded ``name:[id]`` readlink grammar, loopback reachability, the
EXACT reviewed 017-p harmless keyring ABI (NULL type/description/
payload/callout_info, add_key's full five-argument x86_64 form with a
zero destination-keyring serial, request_key's four-argument form,
and the UNKNOWN keyctl command -1 which names no linux/keyctl.h
opcode; a non-x86_64 platform fails closed BEFORE any syscall),
effective cgroup limits with the P v1 unlimited-page-counter
sentinel and missing/unlimited swap distinctions (never an inferred
zero), the exact configured writable-mount identities, an actual
EROFS write denial on an image path (generic EACCES/EPERM is not a
read-only proof), and the host parent isolation facts.

Modes (all emit ONE closed JSON record as the final stdout line):
  measure     full SCHEMA_EXEC_MEASUREMENT subject facts
  pty         closed PTY attachment metadata (terminal properties only)
  success     real Responses-API wire: SSE function_call issuance by
              the controller at its OWN causal request position, then
              function_call_output references validated by the
              controller against the exact-issued registry
  fail        deliberate never-issued call reference (fixed provider
              error envelope, closed state)
  hang        flushed pre-hang record (pid + starttime identity),
              owned token-bound child, finite hold
  output-cap  flushed record then bounded filler past the host cap
  stop-owned  same-UID exact-owned stopper: token + pid + starttime
              (PID-reuse protected) in this private PID namespace
  hold        017-x live executable capability: closed identity
              record (pid + starttime + uid/gid/groups + bound
              32-hex token) flushed FIRST, then a hard finite hold
              of at most 20 s (self-deadline backstopped), natural
              exit 0 — no model POST, no child, no shell
  observe     closed NON-CONSUMING controller /state record (no
              model POST, no consume)

Nothing here invokes Codex, reads a real profile/credential, or
retains raw content.  The synthetic CODEX_HOME + separate early-beta
profile file use only the exact 0.164.0 supported provider/config
schema (env_key pattern for the generated fake credential; no
[profiles.NAME] table; no copied host profile).
"""

from __future__ import annotations

import ctypes
import ctypes.util
import errno as errno_mod
import hashlib
import http.client
import json
import math
import os
import platform
import re
import signal
import stat as stat_mod
import sys
import time

CTL_DIR = "/run/slaif-ctl"
CTL_SOCKET_DIR = f"{CTL_DIR}/socket"
CTL_EXPORTER_SOCKET = f"{CTL_SOCKET_DIR}/exporter.sock"
CTL_ISSUED_REGISTRY = f"{CTL_DIR}/issued-registry.json"
CTL_ORIGINALS_DIR = f"{CTL_DIR}/originals"
CTL_SENTINEL = f"{CTL_DIR}/sentinel"
CTL_PROC1_ENVIRON = "/proc/1/environ"
# Production default is the bounded subject private tmpfs; an env
# override exists ONLY for pure local tests (no local fixture root).
SUBJ_DIR = os.environ.get("SLAIF_SUBJ_DIR", "/run/slaif-subj")
SUBJ_CODEX_HOME = f"{SUBJ_DIR}/codex-home"
SUBJ_CREDENTIAL = f"{SUBJ_DIR}/credential"
SUBJ_WORKDIR = f"{SUBJ_DIR}/work"
PROVIDER_HOST = "127.0.0.1"

SUBJECT_UID = 21002
# The baked closed profile DATA file of the owner-UID image variant
# (017-aa): present ONLY in that image (baked immutable, root-owned
# 0444 on the read-only rootfs) and the bounded subject-identity
# record of the owner mode.  Its presence or absence NEVER selects
# the identity mode — that binding is the explicit image-owned
# mode-constant file below.
PROFILE_DATA_PATH = "/opt/slaif-fixture/fixture-identity.json"
# The EXPLICIT image-owned identity-mode CONSTANT file (generated
# ONLY by the owner-variant Dockerfile as a closed single-constant
# Python source, root-owned 0444 on the read-only rootfs): an
# immutable image fact — NOT runtime-overridable (the host neither
# passes nor creates it; the guarded exec env is the closed set).
# Its absence is the ORIGINAL default: the fixed-21002 law applies
# byte-for-byte even if an arbitrary file sits at the DATA path.
# The exact closed owner value selects the owner-UID law (which
# then REQUIRES the bounded immutable DATA file and never falls
# back); the explicit original value is the original law; any other
# value, malformed content or non-immutable file state fails
# closed.  The file is Parsed as closed content — never imported
# or executed.
IDENTITY_PROFILE_FILE = "/opt/slaif-fixture/identity_profile.py"
IDENTITY_PROFILE_OWNER = "slaif-fixture-identity-owner-uid-v1"
IDENTITY_PROFILE_ORIGINAL = "slaif-fixture-identity-original-v1"
# Bounded content cap for the mode-constant file (cap+1 reads: an
# overbound file is refused WITHOUT being fully read).
IDENTITY_PROFILE_FILE_MAX_BYTES = 128
# The 017-x hard finite hold bound: the subject holds AT MOST this
# many seconds (further capped by the shared self-deadline backstop)
# so a host-side observer can measure its CURRENT executable while
# the subject is still alive.
HOLD_MAX_SECONDS = 20.0

MODES = (
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
    "hold",
)
NS_NAMES = ("pid", "mnt", "ipc", "uts", "net", "user")

# Reviewed x86_64 syscall numbers (arch/x86/include/asm/unistd_64.h,
# as verified in 017-p against /usr/include/x86_64-linux-gnu/asm/
# unistd_64.h).
_X86_64_SYSCALLS = {"add_key": 248, "request_key": 249, "keyctl": 250}
# Unknown keyctl command: valid commands are 0..29 (linux/keyctl.h),
# so -1 cannot name any read/mutation opcode and, absent the policy,
# fails in the kernel's command dispatch without touching a key.
_KEYCTL_UNKNOWN_COMMAND = -1
_NS_ID_RE = re.compile(r"^[a-z0-9_]+:\[\d+\]$")
#: cgroup v1 controllers surface the kernel's unlimited page-counter
#: limit (PAGE_COUNTER_MAX, 0x7FFFFFFFFFFFF000) as this value instead
#: of the string "max" (017-p reviewed sentinel).
_V1_UNLIMITED = 0x7FFFFFFFFFFFF000
FIXED_FINAL_TEXT = "slaif fixed final text"
_EXPECTED_ARGUMENT_FIELDS: dict[str, tuple[str, ...]] = {
    "exec_command": ("cmd",),
    "write_stdin": ("session_id", "chars"),
}
_RESPONSE_CAP = 1024 * 1024
_SSE_CREATED = "response.created"
_SSE_ITEM_ADDED = "response.output_item.added"
_SSE_ITEM_DONE = "response.output_item.done"
_SSE_COMPLETED = "response.completed"
_SSE_EVENT_TYPES = (_SSE_CREATED, _SSE_ITEM_ADDED, _SSE_ITEM_DONE, _SSE_COMPLETED)


class StandinError(RuntimeError):
    """Fixed-reason standin failure (never echoes raw content)."""


def env_int(name: str, default: int | None = None) -> int:
    raw = os.environ.get(name, "" if default is None else str(default))
    try:
        return int(raw)
    except ValueError:
        raise StandinError(f"env-invalid:{name}") from None


def env_str(name: str, default: str = "") -> str:
    value = os.environ.get(name, default)
    if any(ord(c) < 32 or c == "\x7f" for c in value):
        raise StandinError(f"env-invalid:{name}")
    return value


def emit(record: dict) -> None:
    sys.stdout.write(json.dumps(record, sort_keys=True, separators=(",", ":")))
    sys.stdout.write("\n")
    sys.stdout.flush()


def fail(fixed_reason: str) -> int:
    emit({"record": "slaif-fixture-standin-v1", "status": "fail", "reason": fixed_reason})
    return 2


def closed_reason(exc: BaseException) -> str:
    """Fixed closed reason mapping: no arbitrary exception content,
    raw child output, or traceback text ever enters a record."""
    if isinstance(exc, StandinError):
        reason = exc.args[0] if exc.args else ""
        if (
            isinstance(reason, str)
            and reason
            and re.fullmatch(r"[a-z0-9_]{1,64}(-[a-z0-9_]{1,64})*", reason)
        ):
            return reason
        return "standin-failure"
    if isinstance(exc, http.client.HTTPException):
        return "provider-protocol"
    if isinstance(exc, socket_timeout_type()):
        return "provider-timeout"
    if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
        return "provider-socket"
    if isinstance(exc, UnicodeDecodeError):
        return "provider-unicode"
    if isinstance(exc, ValueError):
        return "provider-json"
    if isinstance(exc, FileNotFoundError):
        return "filesystem"
    return "standin-failure"


def socket_timeout_type() -> type:
    import socket

    return socket.timeout


# -- exact reviewed 017-p keyring ABI ------------------------------------------
def keyring_errno(syscall_no: int, *args: object, libc: object | None = None) -> int:
    """Invoke a raw syscall via glibc and return the resulting errno.

    The reviewed harmless P ABI is the ONLY sanctioned form: NULL
    type/description/payload/callout_info pointers and explicit
    typed zero integers; an injectable ``libc`` lets pure tests
    record calls without invoking any real keyring syscall.
    """
    if libc is None:
        lib_name = ctypes.util.find_library("c")
        if not lib_name:
            raise StandinError("no-libc")
        libc = ctypes.CDLL(lib_name, use_errno=True)
    ctypes.set_errno(0)
    result = libc.syscall(ctypes.c_long(syscall_no), *args)
    err = ctypes.get_errno()
    del result
    return err


def measure_keyring_errno(libc: object | None = None) -> dict[str, int]:
    # Architecture prerequisite BEFORE any syscall: fail closed on a
    # non-x86_64 ABI (syscall numbers are architecture-specific).
    uname = platform.uname()
    if uname.system != "Linux" or uname.machine != "x86_64":
        raise StandinError("platform-not-x86_64")
    null = ctypes.c_void_p(None)
    zero = ctypes.c_long(0)
    return {
        "add_key": keyring_errno(
            _X86_64_SYSCALLS["add_key"],
            null,  # NULL type
            null,  # description: NULL
            null,  # payload: NULL
            zero,  # datalen
            zero,  # destination keyring (serial 0: none)
            libc=libc,
        ),
        "request_key": keyring_errno(
            _X86_64_SYSCALLS["request_key"],
            null,  # NULL type
            null,  # description: NULL
            null,  # callout_info: NULL
            zero,  # dest_keyring: 0 (none)
            libc=libc,
        ),
        "keyctl": keyring_errno(
            _X86_64_SYSCALLS["keyctl"],
            ctypes.c_long(_KEYCTL_UNKNOWN_COMMAND),  # unknown command
            zero,
            zero,
            zero,
            zero,
            libc=libc,
        ),
    }


# -- measured kernel facts -------------------------------------------------------
def self_status() -> dict[str, str]:
    with open("/proc/self/status", encoding="ascii") as handle:
        return {
            line.split(":", 1)[0]: line.split(":", 1)[1].strip() for line in handle if ":" in line
        }


def measure_capabilities(status: dict[str, str]) -> dict[str, int]:
    # Exact Linux proc status field names; all five sets are required.
    caps: dict[str, int] = {}
    for line_name, field_name in (
        ("CapAmb", "ambient"),
        ("CapBnd", "bounding"),
        ("CapEff", "effective"),
        ("CapInh", "inheritable"),
        ("CapPrm", "permitted"),
    ):
        value = status.get(line_name)
        if value is None:
            raise StandinError("capabilities-unreadable")
        try:
            caps[field_name] = int(value, 16)
        except ValueError:
            raise StandinError("capabilities-unreadable") from None
    return caps


def parent_namespaces_from_env() -> dict[str, str]:
    ns: dict[str, str] = {}
    for name in NS_NAMES:
        value = env_str(f"SLAIF_FIXTURE_PARENT_NS_{name.upper()}")
        if not _NS_ID_RE.fullmatch(value):
            raise StandinError("parent-namespace-invalid")
        ns[name] = value
    return ns


def measure_namespaces(parent_ns: dict[str, str]) -> dict[str, bool]:
    facts: dict[str, bool] = {}
    for name in NS_NAMES:
        try:
            self_ns = os.readlink(f"/proc/self/ns/{name}")
        except OSError:
            raise StandinError("namespace-unreadable") from None
        if not _NS_ID_RE.fullmatch(self_ns):
            raise StandinError("namespace-invalid")
        # Real readlinks are ``name:[id]``; compare the id part.
        self_id = self_ns.split(":", 1)[1]
        parent_id = parent_ns[name].split(":", 1)[1]
        if name == "user":
            facts["user_shared"] = self_id == parent_id
        elif name == "mnt":
            facts["mount_private"] = self_id != parent_id
        else:
            facts[f"{name}_private"] = self_id != parent_id
    return facts


def _cgroup_value(name: str) -> str | None:
    for base in (
        "/sys/fs/cgroup",
        "/sys/fs/cgroup/memory",
        "/sys/fs/cgroup/pids",
        "/sys/fs/cgroup/cpu",
    ):
        candidate = os.path.join(base, name)
        if os.path.isfile(candidate):
            with open(candidate, encoding="ascii") as handle:
                return handle.read().strip()
    return None


def cgroup_memory_swap() -> tuple[int, int, str]:
    """Measured (memory, swap, swap_source) with the exact P
    derivation: v2's swap-only controller versus v1's combined
    memsw limit, the v1 unlimited sentinel, and missing/unlimited
    distinctions.  Missing or unlimited is never an inferred zero."""
    cgroup_version = "v2" if os.path.isfile("/sys/fs/cgroup/memory.max") else "v1"
    memory_raw = _cgroup_value("memory.max") or _cgroup_value("memory.limit_in_bytes")
    if (
        memory_raw is None
        or memory_raw == "max"
        or (memory_raw.isdigit() and int(memory_raw) >= _V1_UNLIMITED)
    ):
        raise StandinError("memory-missing-or-unlimited")
    swap_raw = (
        _cgroup_value("memory.swap.max")
        if cgroup_version == "v2"
        else _cgroup_value("memory.memsw.limit_in_bytes")
    )
    if cgroup_version == "v2":
        if swap_raw is None:
            raise StandinError("swap-missing")
        if swap_raw == "max":
            raise StandinError("swap-unlimited")
        return int(memory_raw), int(swap_raw), "v2-swap-max"
    if swap_raw is None:
        raise StandinError("swap-missing")
    # The v1 unlimited sentinel (or the "max" spelling) makes the
    # swap allowance underivable for a finite memory limit: it is a
    # typed missing/unlimited outcome, never a measured zero and
    # never a fabricated allowance.
    if swap_raw == "max" or (swap_raw.isdigit() and int(swap_raw) >= _V1_UNLIMITED):
        raise StandinError("swap-missing")
    memsw = int(swap_raw)
    if int(memory_raw) >= _V1_UNLIMITED:
        raise StandinError("swap-missing")
    allowance = memsw - int(memory_raw)
    if allowance < 0:
        # An underivable controller pair is typed invalid, never a
        # measured zero.
        raise StandinError("swap-derivation-invalid")
    return int(memory_raw), allowance, "v1-memsw-combined"


def cgroup_pids() -> int:
    raw = _cgroup_value("pids.max")
    if raw is None or raw == "max":
        raise StandinError("pids-missing-or-unlimited")
    return int(raw)


def cpu_limit(expected: int) -> int:
    """Exact quota/period comparison (no flooring: 1.5 CPUs must not
    read as the configured 1)."""
    quota: int | None = None
    period: int | None = None
    if os.path.isfile("/sys/fs/cgroup/cpu.max"):
        parts = _cgroup_value("cpu.max").split()
        if parts[0] == "max":
            raise StandinError("cpu-unlimited")
        quota, period = int(parts[0]), int(parts[1])
    elif _cgroup_value("cpu.cfs_quota_us") is not None:
        quota = int(_cgroup_value("cpu.cfs_quota_us"))
        period = int(_cgroup_value("cpu.cfs_period_us"))
        if quota < 0:
            raise StandinError("cpu-unlimited")
    else:
        raise StandinError("cpu-unreadable")
    if period is None or period <= 0:
        raise StandinError("cpu-unreadable")
    if quota != expected * period:
        raise StandinError("cpu-mismatch")
    return expected


# The subject's own mount table is the evidence for the writable-
# data inventory (a configured-roots-only stat would prove nothing
# about unlisted mounts).  The mountinfo path is a module constant
# so focused tests can point it at a synthetic owned table.
_MOUNTINFO_PATH = "/proc/self/mountinfo"
# Standard kernel virtual / device filesystem classes: distinct from
# ordinary writable tmpfs DATA.  They may be rw (proc, devpts, ...)
# or ro; they are never counted as writable data storage and never
# fail the scan.  The daemon's /dev tmpfs is a device surface, not
# data.  RAM-backed DATA filesystems (ramfs, hugetlbfs) are NOT
# virtual: they are unbounded by design, so any unlisted rw instance
# is writable data and fails closed.  Any other rw mount (a writable
# bind, an rw overlay, an unlisted tmpfs) is an unlisted writable
# data mount: fail-closed.
_VIRTUAL_FSTYPE = frozenset(
    {
        "proc",
        "sysfs",
        "cgroup",
        "cgroup2",
        "pstore",
        "securityfs",
        "devpts",
        "mqueue",
        "debugfs",
        "tracefs",
        "configfs",
        "bpf",
        "netlink",
        "autofs",
        "fusectl",
        "binfmt_misc",
        "rpc_pipefs",
        "nsfs",
    }
)
_DEVICE_TMPFS_ROOT = "/dev"
# The daemon's bounded shared-memory mount (module constant so the
# focused unit tests can point it at an owned directory).
_SHM_ROOT = "/dev/shm"

# The default profile masks SELECTED procfs/sysfs FILES by bind-
# mounting the /dev/null character device over them (moby v28.5.1
# oci/defaults.go default masked paths; runc v1.5.2 maskPaths: a
# FILE gets a plain MS_BIND of the verified /dev/null, a DIRECTORY
# gets a read-only tmpfs).  The file aliases therefore appear in
# the ACTUAL mount table as rw mounts backed by the /dev tmpfs — a
# device surface, never writable data.  They are admitted only
# under the strictly-evidenced closed identity: the source-root
# file identity inside the /dev tmpfs (/null), the NARROW
# known-default file-mask path set, and the exact character device
# type + major 1/minor 3 on the node itself (the same identity
# runc's verifyDevNull/isDevNull enforces before masking).  A wrong
# device, a regular file, a directory, or an unreviewed path is
# never admitted: the scan stays fail-closed.  (The directory masks
# are ro tmpfs and never reach the rw data check.)
_MASKED_NULL_SOURCE_ROOT = "/null"
_MASKED_NULL_FILE_PATHS = frozenset(
    {
        "/proc/interrupts",
        "/proc/kcore",
        "/proc/keys",
        "/proc/latency_stats",
        "/proc/timer_list",
        "/proc/timer_stats",
        "/proc/sched_debug",
    }
)
_MASKED_NULL_THERMAL_RE = re.compile(r"^/sys/devices/system/cpu/cpu[0-9]+/thermal_throttle$")
_NULL_DEVICE_RDEV = os.makedev(1, 3)


def _unesc_mountinfo(value: str) -> str:
    return value.replace("\\040", " ").replace("\\011", "\t").replace("\\013", "\n")


def measure_mounts(specs: list[tuple[str, int, int, int]]) -> tuple[list[dict], int, int]:
    """RECONCILED writable-data inventory from the ACTUAL mount table.

    The table input is BOUNDED before retention (finite chunk/byte/
    record caps; overflow is fail-closed — a truncated prefix is
    never labeled complete): every rw mount is then classified —
    kernel virtual/device filesystems are a separate class; rw
    tmpfs is data only at the documented roots (the configured
    budgets plus the daemon's explicitly bounded /dev/shm); anything
    else is an unlisted writable data mount: fail-closed.  Every
    documented root must be observed as an rw mount, and each is
    measured (lstat/statvfs).  Returns the ordered data entries,
    the number of COMPLETE table records scanned, and the count of
    the strictly-evidenced masked /dev/null file aliases (device
    surface, never writable data)."""
    # Closed finite input bounds (local: the selected-AST probe's
    # fixed context carries no new names).
    chunk_bytes = 65536
    max_bytes = 256 * 1024
    max_records = 512
    try:
        handle = open(_MOUNTINFO_PATH, encoding="ascii")
    except OSError:
        raise StandinError("mountinfo-unreadable") from None
    try:
        with handle:
            chunks: list[str] = []
            total = 0
            while True:
                chunk = handle.read(chunk_bytes)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise StandinError("mountinfo-oversized")
                chunks.append(chunk)
    except StandinError:
        raise
    except (OSError, UnicodeDecodeError):
        raise StandinError("mountinfo-unreadable") from None
    data = "".join(chunks)
    lines = [ln for ln in data.splitlines() if ln.strip()]
    if len(lines) > max_records:
        raise StandinError("mountinfo-oversized")
    if not lines:
        raise StandinError("mountinfo-malformed")
    documented: set[str] = {root for root, _s, _u, _g in specs}
    documented.add(_SHM_ROOT)
    observed: dict[str, str] = {}
    masked_null_aliases = 0

    def _masked_null_alias(src_root: str, mountpoint: str) -> bool:
        """The runc maskPaths file mask, proved element by element
        on the exact node: source-root file identity, narrow
        known-default path, and the exact chr 1:3 device (an OSError
        on the node is inconclusive, never an admission)."""
        if src_root != _MASKED_NULL_SOURCE_ROOT:
            return False
        if (
            mountpoint not in _MASKED_NULL_FILE_PATHS
            and _MASKED_NULL_THERMAL_RE.fullmatch(mountpoint) is None
        ):
            return False
        try:
            node = os.lstat(mountpoint)
        except OSError:
            return False
        if not stat_mod.S_ISCHR(node.st_mode):
            return False
        return node.st_rdev == _NULL_DEVICE_RDEV

    for line in lines:
        head, sep, tail = line.partition(" - ")
        if not sep:
            raise StandinError("mountinfo-malformed")
        fields = head.split()
        if len(fields) < 6:
            raise StandinError("mountinfo-malformed")
        src_root = _unesc_mountinfo(fields[3])
        root = _unesc_mountinfo(fields[4])
        options = fields[5].split(",")
        fstype = tail.split(" ")[0]
        if not fstype:
            raise StandinError("mountinfo-malformed")
        if "rw" not in options:
            continue  # read-only: not writable data of any class
        if fstype in _VIRTUAL_FSTYPE:
            continue  # virtual/device class: separate, not data
        if fstype == "tmpfs":
            if root == _DEVICE_TMPFS_ROOT:
                continue  # daemon device surface, not data
            if root not in documented:
                if not _masked_null_alias(src_root, root):
                    raise StandinError("unlisted-writable-mount")
                masked_null_aliases += 1
                continue
        else:
            raise StandinError("unlisted-writable-mount")
        observed[root] = fstype
    for root in documented:
        if root not in observed:
            raise StandinError("expected-writable-mount-missing")
    mounts = []
    for root in sorted(observed):
        st = os.lstat(root)
        vfs = os.statvfs(root)
        if not stat_mod.S_ISDIR(st.st_mode):
            raise StandinError("mount-not-directory")
        mounts.append(
            {
                "root": root,
                "size_bytes": vfs.f_blocks * vfs.f_bsize,
                "uid": st.st_uid,
                "gid": st.st_gid,
                "mode": stat_mod.S_IMODE(st.st_mode),
            }
        )
    return mounts, len(lines), masked_null_aliases


def measure_rootfs_readonly(probe_path: str) -> bool:
    """Actual EROFS write denial on a FIXED image-local path.  The
    path must not pre-exist (and never be a link alias): O_EXCL and
    O_NOFOLLOW make any pre-existing object a fail-closed
    inconclusive, so the probe can only ever create a fresh owned
    file.  Generic EACCES/EPERM are NOT a read-only proof (they also
    happen on a read-writable root for non-owner paths); a
    successful create is a containment failure."""
    if os.path.lexists(probe_path):
        raise StandinError("ro-probe-exists")
    try:
        fd = os.open(probe_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except OSError as exc:
        if exc.errno == errno_mod.EROFS:
            return True
        # EEXIST/EACCES/EPERM/ENOTDIR/... : never an RO proof
        raise StandinError("rootfs-proof-inconclusive") from None
    try:
        os.close(fd)
        os.unlink(probe_path)
    except OSError:
        pass
    raise StandinError("rootfs-writable")


def measure_denied() -> dict[str, dict]:
    # The closed record law requires the controller-owned EXISTENCE
    # of each protected target to be established first (ENOENT alone
    # is not a protection proof).  The runner's separate 21001
    # presence probe establishes it inside the container, and its
    # closed sha256 is injected here: a mismatched or missing digest
    # means the existence facts are unverified and the whole
    # measurement fails closed.
    raw_presence = env_str("SLAIF_FIXTURE_PRESENCE_SHA256")
    if not re.fullmatch(r"[0-9a-f]{64}", raw_presence):
        raise StandinError("presence-unverified")
    expected_presence = hashlib.sha256(
        json.dumps(
            {
                name: True
                for name in (
                    "controller_socket_dir",
                    "issued_registry",
                    "controller_originals",
                    "controller_sentinel",
                    "controller_proc",
                    "exporter_socket",
                )
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    if raw_presence != expected_presence:
        raise StandinError("presence-unverified")
    targets = {
        "controller_socket_dir": CTL_SOCKET_DIR,
        "issued_registry": CTL_ISSUED_REGISTRY,
        "controller_originals": CTL_ORIGINALS_DIR,
        "controller_sentinel": CTL_SENTINEL,
        "controller_proc": CTL_PROC1_ENVIRON,
        "exporter_socket": CTL_EXPORTER_SOCKET,
    }
    denied: dict[str, dict] = {}
    for name, path in targets.items():
        try:
            if name == "controller_proc":
                # The explicit protected target is the controller's
                # credential file (owner-only); /proc/1 directory
                # visibility is expected and is not the claim.
                with open(path, "rb"):
                    raise StandinError("denial-unexpected")
            os.stat(path)
            raise StandinError("denial-unexpected")
        except StandinError:
            raise
        except OSError as exc:
            if exc.errno == errno_mod.EACCES:
                state = "eacces"
            elif exc.errno == errno_mod.EPERM:
                state = "eperm"
            elif exc.errno == errno_mod.ENOENT:
                state = "enoent"
            else:
                raise StandinError("denial-inconclusive") from None
        denied[name] = {"present_21001": True, "subject": state}
    return denied


def _port_reachable(port: int) -> bool:
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.2)
    try:
        sock.connect((PROVIDER_HOST, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def measure_host_isolation() -> dict[str, bool]:
    parent_pid = env_int("SLAIF_FIXTURE_PARENT_PID")
    parent_port = env_int("SLAIF_FIXTURE_PARENT_PORT")
    sentinel_path = env_str("SLAIF_FIXTURE_SENTINEL_PATH")
    return {
        "parent_proc_visible": os.path.isdir(f"/proc/{parent_pid}"),
        "host_sentinel_visible": os.path.exists(sentinel_path),
        "host_listener_reachable": _port_reachable(parent_port),
    }


def create_synthetic_profile(run_token: str, v2: bool = False) -> dict:
    """Fresh owned synthetic CODEX_HOME + SEPARATE early-beta profile
    file (official 0.164.0 docs: --profile NAME overlays
    CODEX_HOME/NAME.config.toml, not a [profiles.NAME] table),
    entirely in the subject private tmpfs.  Only the exact supported
    0.164.0 provider/config schema is used (env_key pattern; the
    generated fake credential is a 0600 file, never the profile
    value).  Only closed identity facts are returned.  ``v2`` (the
    owner-UID variant only) emits the same closed facts under the
    v2 profile-record tag; the default keeps the original record
    byte-for-byte."""
    import hashlib

    os.makedirs(SUBJ_CODEX_HOME, mode=0o700, exist_ok=True)
    os.chmod(SUBJ_CODEX_HOME, 0o700)
    port = env_int("SLAIF_FIXTURE_PORT", 18443)
    # The required startup controls of the exact pinned public
    # 0.164.0 config schema (codex-rs/core/config.schema.json at
    # 6aaac694803004a63c6f393d153c96d22521a6b9): no startup update
    # check, analytics disabled, all OTEL exporters off, plugin
    # synchronization/remote plugins/recommended plugins/plugin
    # hooks off (features.plugins defaults to TRUE at this commit,
    # so it must be set explicitly), and nonessential history off.
    # These are fixture-only settings of a disposable synthetic
    # profile — no native behavior claim, and the actual offered
    # native tool modes are preserved (no unified_exec/code-mode
    # swap).
    base = (
        'model_provider = "slaif_synthetic_provider"\n'
        'model = "slaif-synthetic-model"\n'
        "\n"
        "check_for_update_on_startup = false\n"
        "\n"
        "[analytics]\n"
        "enabled = false\n"
        "\n"
        "[otel]\n"
        'exporter = "none"\n'
        'trace_exporter = "none"\n'
        'metrics_exporter = "none"\n'
        "\n"
        "[features]\n"
        "plugins = false\n"
        "remote_plugin = false\n"
        "recommended_plugins = false\n"
        "plugin_hooks = false\n"
        "\n"
        "[model_providers.slaif_synthetic_provider]\n"
        'name = "slaif synthetic loopback provider"\n'
        f'base_url = "http://127.0.0.1:{port}/v1"\n'
        'wire_api = "responses"\n'
        'env_key = "SLAIF_SYNTHETIC_API_KEY"\n'
        "requires_openai_auth = false\n"
        "\n"
        "[history]\n"
        'persistence = "none"\n'
    )
    profile = (
        'model = "slaif-synthetic-model"\n'
        'approval_policy = "never"\n'
        'sandbox_mode = "danger-full-access"\n'
    )
    credential = "slaif-synthetic-" + hashlib.sha256(run_token.encode()).hexdigest()[:32]
    base_path = f"{SUBJ_CODEX_HOME}/config.toml"
    profile_path = f"{SUBJ_CODEX_HOME}/early-beta.config.toml"
    for path, content in (
        (base_path, base),
        (profile_path, profile),
        (SUBJ_CREDENTIAL, credential),
    ):
        if os.path.islink(path) or os.path.exists(path):
            raise StandinError("profile-path-exists")
        with open(path, "w", encoding="ascii") as handle:
            handle.write(content)
        os.chmod(path, 0o600)
    return {
        "record": "slaif-fixture-profile-v2" if v2 else "slaif-fixture-profile-v1",
        "codex_home_mode": stat_mod.S_IMODE(os.lstat(SUBJ_CODEX_HOME).st_mode),
        "codex_home_uid": os.lstat(SUBJ_CODEX_HOME).st_uid,
        "base_config_sha256": hashlib.sha256(base.encode()).hexdigest(),
        "base_config_mode": stat_mod.S_IMODE(os.lstat(base_path).st_mode),
        "profile_file": "early-beta.config.toml",
        "profile_sha256": hashlib.sha256(profile.encode()).hexdigest(),
        "profile_mode": stat_mod.S_IMODE(os.lstat(profile_path).st_mode),
        "profile_table_used": False,
        "credential_file_mode": stat_mod.S_IMODE(os.lstat(SUBJ_CREDENTIAL).st_mode),
        "credential_sha256": hashlib.sha256(credential.encode()).hexdigest(),
        "env_key_name": "SLAIF_SYNTHETIC_API_KEY",
        "loopback_only": True,
    }


def _image_identity_profile_raw() -> bytes | None:
    """The bounded immutable read of the image-owned mode constant.

    Absent file: None (the original default — the original image
    never bakes it).  ABSENCE is verified ENOENT ONLY: any other
    lookup failure (EACCES, EIO, ...) is a fixed closed refusal —
    a failed lookup must never silently choose the original.
    Present file: the lstat facts are verified FIRST (regular
    file, no link, root-owned, mode 0444 — the in-image immutable
    state; anything else is a closed refusal), then the content
    is read with a cap+1 bound (an overbound file is refused,
    never fully read).
    """
    try:
        st = os.lstat(IDENTITY_PROFILE_FILE)
    except OSError as exc:
        if exc.errno != errno_mod.ENOENT:
            raise StandinError("identity-profile-lookup") from None
        return None
    if (
        not stat_mod.S_ISREG(st.st_mode)
        or st.st_uid != 0
        or st.st_gid != 0
        or stat_mod.S_IMODE(st.st_mode) != 0o444
    ):
        raise StandinError("identity-profile-state")
    if st.st_size > IDENTITY_PROFILE_FILE_MAX_BYTES:
        raise StandinError("identity-profile-size")
    try:
        with open(IDENTITY_PROFILE_FILE, "rb") as handle:
            raw = handle.read(IDENTITY_PROFILE_FILE_MAX_BYTES + 1)
    except OSError:
        raise StandinError("identity-profile-unreadable") from None
    if len(raw) > IDENTITY_PROFILE_FILE_MAX_BYTES:
        raise StandinError("identity-profile-size")
    return raw


def _parse_identity_profile(raw: bytes) -> str | None:
    """The closed single-constant content law (pure, no FS).

    The content must be exactly one line of the closed grammar
    (a fixed name, `` = ``, the quoted closed value, one trailing
    newline); the closed values are the two canonical profile
    names: the owner value selects the owner-UID mode, the
    original value the original mode (like an absent file); any
    other value, malformed grammar or encoding is a closed
    refusal.  The content is never imported or executed.
    """
    match = re.fullmatch(rb'SLAIF_FIXTURE_IDENTITY_PROFILE = "([a-z0-9-]+)"\n', raw)
    if match is None:
        raise StandinError("identity-profile-grammar")
    value = match.group(1).decode("ascii")
    if value == IDENTITY_PROFILE_OWNER:
        return "owner"
    if value == IDENTITY_PROFILE_ORIGINAL:
        return None
    raise StandinError("identity-profile-unknown")


def _expected_subject_pair() -> tuple[int, int] | None:
    """The closed in-image subject identity expectation.

    The mode is bound by the EXPLICIT image-owned generated
    mode-constant file (immutable root-owned 0444 content, parsed
    never executed): an absent file or the explicit original value
    keeps the historical fixed-21002 law byte-for-byte, ignoring
    any file at the DATA path (the original default — a file's
    presence NEVER selects the mode).  The exact closed owner
    value REQUIRES the bounded immutable DATA file — non-immutable
    DATA state (link/missing/wrong owner/mode), oversize, malformed
    or unknown-profile DATA fails closed, there is NEVER a
    fallback to the original profile.  Non-immutable mode-file
    state, overbound or malformed content and unknown values fail
    closed.  The expected subject is the DATA's INDEPENDENT
    (uid, gid) pair.
    """
    raw_mode = _image_identity_profile_raw()
    mode = None if raw_mode is None else _parse_identity_profile(raw_mode)
    if mode != "owner":
        return None
    try:
        import cache_native_fixture_identity as fixture_identity
    except ImportError:
        raise StandinError("profile-data-module") from None
    try:
        st = os.lstat(PROFILE_DATA_PATH)
    except OSError as exc:
        if exc.errno != errno_mod.ENOENT:
            raise StandinError("profile-data-lookup") from None
        raise StandinError("profile-data-missing") from None
    if (
        not stat_mod.S_ISREG(st.st_mode)
        or st.st_uid != 0
        or st.st_gid != 0
        or stat_mod.S_IMODE(st.st_mode) != 0o444
    ):
        raise StandinError("profile-data-state")
    max_bytes = fixture_identity.MAX_RECORD_BYTES
    if st.st_size > max_bytes:
        raise StandinError("profile-data-size")
    try:
        with open(PROFILE_DATA_PATH, "rb") as handle:
            raw = handle.read(max_bytes + 1)
    except OSError:
        raise StandinError("profile-data-unreadable") from None
    if len(raw) > max_bytes:
        raise StandinError("profile-data-size")
    try:
        desc = fixture_identity.decode_description(raw)
    except ValueError:
        raise StandinError("profile-data-invalid") from None
    if desc.profile != fixture_identity.PROFILE_OWNER_UID or (
        desc.controller_uid,
        desc.controller_gid,
    ) != (fixture_identity.CONTROLLER_UID, fixture_identity.CONTROLLER_GID):
        raise StandinError("profile-data-invalid")
    return (desc.subject_uid, desc.subject_gid)


def _subject_identity_refusal(uid_only: bool) -> str | None:
    """The closed subject identity law at ONE check site.

    Returns None when the law holds, else the fixed refusal token
    (never raises).  In the original mode (absent image-owned
    marker) the historical law is byte-for-byte the original
    (uid-only sites keep checking uid only).  In the owner-UID
    mode the subject must be EXACTLY the frozen independent
    (uid, gid) pair at every site — UID and GID are never assumed
    equal.
    """
    try:
        expected = _expected_subject_pair()
    except StandinError as exc:
        return closed_reason(exc)
    if expected is None:
        if os.getuid() != SUBJECT_UID:
            return "identity-not-subject"
        if uid_only:
            return None
        return "identity-not-subject" if os.getgid() != SUBJECT_UID else None
    return None if (os.getuid(), os.getgid()) == expected else "identity-not-subject"


def measure_mode() -> int:
    try:
        # Early identity prerequisite: the subject measures as the
        # closed in-image expectation (original: the fixed 21002
        # pair, byte-for-byte).
        expected = _expected_subject_pair()
        if expected is None:
            if os.getuid() != SUBJECT_UID or os.getgid() != SUBJECT_UID:
                return fail("identity-not-subject")
        elif (os.getuid(), os.getgid()) != expected:
            return fail("identity-not-subject")
        status = self_status()
        specs = [
            (
                part.split(":")[0],
                int(part.split(":")[1]),
                int(part.split(":")[2]),
                int(part.split(":")[3]),
            )
            for part in env_str("SLAIF_FIXTURE_TMPFS_SPECS").split(",")
            if part
        ]
        expected_cpu = env_int("SLAIF_FIXTURE_EXPECTED_CPU", 1)
        memory, swap, source = cgroup_memory_swap()
        if swap != 0:
            raise StandinError("swap-nonzero")
        # Reconciled writable-data inventory from the ACTUAL mount
        # table: configured budgets + explicitly bounded /dev/shm,
        # fail-closed on any unlisted writable data mount.  The
        # scanned-record count proves the scan happened; the
        # strictly-evidenced masked /dev/null file aliases (runc
        # maskPaths) are counted, never counted as data.
        writable_mounts, mounts_scanned, masked_null_aliases = measure_mounts(specs)
        record = {
            # v2: the same closed facts measured under the frozen
            # owner-profile subject; v1 stays byte-for-byte.
            "record": (
                "slaif-fixture-exec-measurement-v2"
                if expected is not None
                else "slaif-fixture-exec-measurement-v1"
            ),
            "uid": os.getuid(),
            "gid": os.getgid(),
            "groups": list(os.getgroups()),
            "capabilities": measure_capabilities(status),
            "no_new_privs": status.get("NoNewPrivs") == "1",
            "seccomp_filter_mode": int(status.get("Seccomp", "-1")),
            "namespaces": measure_namespaces(parent_namespaces_from_env()),
            "loopback_only": _loopback_only(),
            "keyring_errno": measure_keyring_errno(),
            "memory_limit_bytes": memory,
            "swap_limit_bytes": swap,
            "swap_source": source,
            "cpu_limit": cpu_limit(expected_cpu),
            "pids_limit": cgroup_pids(),
            "writable_mounts": writable_mounts,
            "mounts_scanned": mounts_scanned,
            "masked_null_aliases": masked_null_aliases,
            "rootfs_readonly": measure_rootfs_readonly(
                env_str("SLAIF_FIXTURE_RO_PROBE_PATH", "/opt/slaif-fixture/.ro-probe")
            ),
            "controller_pid1_uid": int(
                open("/proc/1/status", encoding="ascii").read().split("Uid:")[1].split()[0]
            ),
            "private_pid1_exempt": os.getpid() != 1 and os.path.isdir("/proc/1"),
            "denied": measure_denied(),
            "host_isolation": measure_host_isolation(),
        }
        emit(record)
        return 0
    except (StandinError, OSError, ValueError, http.client.HTTPException) as exc:
        return fail(closed_reason(exc))


def _loopback_only() -> bool:
    with open("/proc/net/dev", encoding="ascii") as handle:
        lines = handle.readlines()[2:]
    names = {line.split(":", 1)[0].strip() for line in lines if line.strip()}
    return names == {"lo"}


def pty_mode() -> int:
    """PTY/interactive attachment proof (the exact future native
    attachment path): stdin must be a TTY (docker exec -it), the
    closed terminal size facts are emitted (no raw TUI content), and
    the FRESH synthetic CODEX_HOME + separate early-beta profile file
    are created entirely in the subject-private tmpfs and validated
    against the closed model profile schema BEFORE the record is
    published."""
    try:
        try:
            expected = _expected_subject_pair()
        except StandinError as exc:
            return fail(closed_reason(exc))
        if expected is None:
            if os.getuid() != SUBJECT_UID:
                return fail("identity-not-subject")
        elif (os.getuid(), os.getgid()) != expected:
            return fail("identity-not-subject")
        if not sys.stdin.isatty():
            return fail("pty-not-attached")
        import fcntl
        import struct
        import termios

        size = struct.unpack(
            "HHHH", fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ, b"\x00" * 8)
        )
        token = env_str("SLAIF_RUN_TOKEN")
        if not re.fullmatch(r"[0-9a-f]{32}", token):
            return fail("run-token-invalid")
        profile = create_synthetic_profile(token, v2=expected is not None)
        try:
            import cache_native_fixture_model as fixture_model

            if expected is None:
                fixture_model.validate_profile_record(profile)
            else:
                fixture_model.validate_profile_record_v2(profile, expected[0])
        except ImportError:
            return fail("model-import")
        except fixture_model.FixtureError:
            return fail("profile-schema")
        # Closed environment-handoff proof for the future native
        # attach: the protected host env file delivers ONLY the
        # synthetic CODEX_HOME and the generated fake-provider
        # variable.  The value is compared against the subject-owned
        # credential file (same closed run-token derivation) and is
        # NEVER emitted.  Absent environment (hosted CI path) is a
        # truthful false, not a failure here.
        env_home = os.environ.get("CODEX_HOME")
        env_key = os.environ.get("SLAIF_SYNTHETIC_API_KEY")
        handoff = False
        if (
            env_home == SUBJ_CODEX_HOME
            and isinstance(env_key, str)
            and re.fullmatch(r"slaif-synthetic-[0-9a-f]{32}", env_key)
        ):
            # Bounded comparison: the credential is a known finite
            # length (16-char synthetic prefix + 32 hex); read at most
            # that plus one and require the exact length, so a
            # subject-writable oversized file can never be slurped.
            try:
                with open(SUBJ_CREDENTIAL, "rb") as handle:
                    observed = handle.read(len(env_key) + 1)
                handoff = len(observed) == len(env_key) and observed == env_key.encode("ascii")
            except OSError:
                handoff = False
        # Concrete subject-owned synthetic workspace for the later
        # foreground attach's explicit exec workdir: created by the
        # SUBJECT (21002) in its private tmpfs, exact ownership
        # re-measured, closed facts only.
        if os.path.islink(SUBJ_WORKDIR) or os.path.exists(SUBJ_WORKDIR):
            raise StandinError("workspace-path-exists")
        os.makedirs(SUBJ_WORKDIR, mode=0o700)
        os.chmod(SUBJ_WORKDIR, 0o700)
        ws = os.lstat(SUBJ_WORKDIR)
        workspace = {
            "path": SUBJ_WORKDIR,
            "mode": stat_mod.S_IMODE(ws.st_mode),
            "uid": ws.st_uid,
        }
        emit(
            {
                "record": "slaif-fixture-standin-v1",
                "status": "pass",
                "mode": "pty",
                "uid": os.getuid(),
                "pty_attached": True,
                "term_rows": size[0],
                "term_cols": size[1],
                "terminal_properties_closed_only": True,
                "env_handoff_verified": handoff,
                "workspace": workspace,
                "profile": profile,
            }
        )
        return 0
    except (StandinError, OSError, ValueError) as exc:
        return fail(closed_reason(exc))


# -- real Responses-API wire flow ---------------------------------------------
def _absolute_deadline() -> float:
    """One global cumulative experiment deadline: the host passes the
    SAME absolute monotonic anchor to every scenario of a run, so
    each exec consumes remaining budget instead of resetting the
    total.  Falls back to a relative finite deadline only when the
    anchor is absent."""
    raw_abs = os.environ.get("SLAIF_FIXTURE_DEADLINE_ABS", "")
    if raw_abs:
        try:
            absolute = float(raw_abs)
        except ValueError:
            raise StandinError("self-deadline-invalid") from None
        if not math.isfinite(absolute) or absolute <= time.monotonic():
            raise StandinError("self-deadline-expired")
        return absolute
    return time.monotonic() + env_int("SLAIF_FIXTURE_DEADLINE", 1800)


def _remaining(deadline: float) -> float:
    left = deadline - time.monotonic()
    if left <= 0:
        raise StandinError("self-deadline")
    return left


def _provider_post(
    path: str,
    payload: dict,
    deadline: float,
    authorization: str | None = None,
) -> tuple[int, str, bytes]:
    """One bounded POST against the real provider route.  Returns the
    ASSERTED (status, content_type, body): the response Content-Length
    is checked BEFORE any body read (an overbound or missing frame is
    a failure, never a silently truncated accept), and the caller
    verifies the exact expected status and wire content type so a
    wrong-status fixed JSON body cannot masquerade as the declared
    outcome."""
    headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}
    if authorization is not None:
        headers["Authorization"] = authorization
    _remaining(deadline)
    timeout = max(0.05, min(2.0, _remaining(deadline)))
    conn = http.client.HTTPConnection(
        PROVIDER_HOST, env_int("SLAIF_FIXTURE_PORT", 18443), timeout=timeout
    )
    try:
        conn.request(
            "POST",
            path,
            body=json.dumps(payload).encode(),
            headers=headers,
        )
        response = conn.getresponse()
        content_type = (response.getheader("Content-Type") or "").strip()
        length = response.getheader("Content-Length")
        if length is None or not length.isdigit():
            raise StandinError("response-unframed")
        if int(length) > _RESPONSE_CAP:
            raise StandinError("response-overbound")
        body = response.read()
        if len(body) != int(length):
            raise StandinError("response-truncated")
        _remaining(deadline)
        return response.status, content_type, body
    finally:
        conn.close()


def _provider_get(path: str, deadline: float) -> tuple[int, str, bytes]:
    """One bounded GET against a closed provider status route.
    Returns the ASSERTED (status, content_type, body) with the same
    closed framing law as the POST path: the Content-Length is
    checked BEFORE any body read, an overbound or missing frame is
    a failure, and the caller verifies the exact expected status
    and wire content type."""
    headers = {"Accept": "application/json"}
    _remaining(deadline)
    timeout = max(0.05, min(2.0, _remaining(deadline)))
    conn = http.client.HTTPConnection(
        PROVIDER_HOST, env_int("SLAIF_FIXTURE_PORT", 18443), timeout=timeout
    )
    try:
        conn.request("GET", path, headers=headers)
        response = conn.getresponse()
        content_type = (response.getheader("Content-Type") or "").strip()
        length = response.getheader("Content-Length")
        if length is None or not length.isdigit():
            raise StandinError("response-unframed")
        if int(length) > _RESPONSE_CAP:
            raise StandinError("response-overbound")
        body = response.read()
        if len(body) != int(length):
            raise StandinError("response-truncated")
        _remaining(deadline)
        return response.status, content_type, body
    finally:
        conn.close()


def _validate_sse_item(item: object) -> None:
    """Closed validation of one output item against the public
    0.164.0 types (tag 6aaac694803004a63c6f393d153c96d22521a6b9):
    message items REQUIRE role (the native consumer rejects a
    missing role); output_text content items REQUIRE text
    (annotations are optional and never required); function_call
    items REQUIRE name/call_id/arguments with arguments a JSON
    object string (exact known-tool fields for known names).
    This is the supported fixture wire subset; it is static/pure
    proof, distinct from any later genuine client execution."""
    if not isinstance(item, dict):
        raise StandinError("sse-item-shape")
    itype = item.get("type")
    if itype == "message":
        if set(item) != {"type", "id", "role", "content"}:
            raise StandinError("sse-item-shape")
        if item.get("role") != "assistant":
            raise StandinError("sse-item-role")
        content = item.get("content")
        if not isinstance(content, list) or not content:
            raise StandinError("sse-item-shape")
        for part in content:
            if not isinstance(part, dict) or part.get("type") != "output_text":
                raise StandinError("sse-item-shape")
            if not set(part) <= {"type", "text", "annotations", "logprobs"}:
                raise StandinError("sse-item-shape")
            if not isinstance(part.get("text"), str) or not part["text"]:
                raise StandinError("sse-item-shape")
    elif itype == "function_call":
        if set(item) != {"type", "id", "call_id", "name", "arguments"}:
            raise StandinError("sse-item-shape")
        if not isinstance(item.get("name"), str) or not item["name"]:
            raise StandinError("sse-item-shape")
        if not isinstance(item.get("call_id"), str) or not item["call_id"]:
            raise StandinError("sse-item-shape")
        arguments = item.get("arguments")
        if not isinstance(arguments, str):
            raise StandinError("sse-item-shape")
        try:
            parsed_args = json.loads(arguments)
        except ValueError:
            raise StandinError("sse-item-shape") from None
        if not isinstance(parsed_args, dict):
            raise StandinError("sse-item-shape")
        expected = _EXPECTED_ARGUMENT_FIELDS.get(item["name"])
        if expected is not None and set(parsed_args) != set(expected):
            raise StandinError("sse-item-shape")
    else:
        raise StandinError("sse-item-unknown")


def _parse_sse(body: bytes, expect_items: int | None = None) -> dict:
    """Bounded closed parse of the REAL 0.164.0 Responses SSE
    envelope as a state machine over the EXACT tagged sequence:
    exactly one response.created first; then item groups, each a
    response.output_item.added IMMEDIATELY followed by
    response.output_item.done carrying the SAME completed item at
    the same strictly-ascending output_index (the two are the
    distinct native event paths, not interchangeable); then exactly
    one response.completed last whose status is completed, whose id
    matches the created id and whose output equals the done items.
    Duplicates, reorderings, unknown events, unterminated item
    groups, unknown item types and missing role/text are all
    failures.  Retains only closed item facts; raw text content is
    verified against the fixed final text by the caller and never
    retained."""
    text = body.decode("utf-8")  # ValueError -> provider-json
    events: list[tuple[str, dict]] = []
    for block in text.split("\n\n"):
        event_type = None
        data = None
        for line in block.split("\n"):
            if line.startswith("event:"):
                event_type = line[len("event:") :].strip()
            elif line.startswith("data:"):
                data = line[len("data:") :].strip()
        if event_type is None:
            continue
        if event_type not in _SSE_EVENT_TYPES:
            raise StandinError("sse-event-unknown")
        if not data:
            raise StandinError("sse-event-empty")
        parsed = json.loads(data)
        if not isinstance(parsed, dict) or parsed.get("type") != event_type:
            raise StandinError("sse-event-mismatch")
        events.append((event_type, parsed))
    if not events:
        raise StandinError("sse-empty")

    state = "expect-created"
    response_id: str | None = None
    items: list[dict] = []
    pending: tuple[int, dict] | None = None
    for event_type, parsed in events:
        if event_type == _SSE_CREATED:
            if state != "expect-created":
                raise StandinError("sse-duplicate")
            resp = parsed.get("response")
            if not isinstance(resp, dict) or not isinstance(resp.get("id"), str) or not resp["id"]:
                raise StandinError("sse-created-shape")
            response_id = resp["id"]
            state = "expect-item-or-completed"
        elif event_type == _SSE_ITEM_ADDED:
            if state != "expect-item-or-completed":
                raise StandinError("sse-order")
            index = parsed.get("output_index")
            if not isinstance(index, int) or isinstance(index, bool) or index != len(items):
                raise StandinError("sse-order")
            item = parsed.get("item")
            _validate_sse_item(item)
            pending = (index, item)
            state = "expect-done"
        elif event_type == _SSE_ITEM_DONE:
            if state != "expect-done" or pending is None:
                raise StandinError("sse-order")
            index = parsed.get("output_index")
            item = parsed.get("item")
            if index != pending[0] or item != pending[1]:
                raise StandinError("sse-item-mismatch")
            items.append(pending[1])
            pending = None
            state = "expect-item-or-completed"
        else:  # _SSE_COMPLETED
            if pending is not None or state == "expect-done":
                raise StandinError("sse-incomplete")
            if state == "expect-created":
                raise StandinError("sse-order")
            if state == "done":
                raise StandinError("sse-duplicate")
            resp = parsed.get("response")
            if not isinstance(resp, dict) or resp.get("status") != "completed":
                raise StandinError("sse-status")
            if resp.get("id") != response_id:
                raise StandinError("sse-response-id")
            if resp.get("output") != items:
                raise StandinError("sse-output-mismatch")
            state = "done"
    if state != "done":
        raise StandinError("sse-incomplete")
    if expect_items is not None and len(items) != expect_items:
        raise StandinError("sse-item-count")
    return {"items": items, "response_id": response_id}


def _fixed_request(tools: list, extra_input: list | None = None) -> dict:
    input_items = [{"role": "user", "content": "slaif synthetic scenario request"}]
    if extra_input:
        input_items.extend(extra_input)
    return {
        "model": "slaif-synthetic-model",
        "instructions": "slaif synthetic fixture flow",
        "input": input_items,
        "tools": tools,
        "stream": True,
    }


def _synthetic_tools() -> list:
    return [
        {
            "type": "function",
            "name": "exec_command",
            "description": "synthetic exec stand-in",
            "parameters": {
                "type": "object",
                "required": ["cmd"],
                "properties": {"cmd": {"type": "string"}},
            },
        },
        {
            "type": "function",
            "name": "write_stdin",
            "description": "synthetic stdin stand-in",
            "parameters": {
                "type": "object",
                "required": ["session_id"],
                "properties": {"session_id": {"type": "integer"}, "chars": {"type": "string"}},
            },
        },
    ]


def _arguments_closed(name: str, arguments: object) -> bool:
    """Closed check of the function_call arguments string: parseable
    JSON object with exactly the expected known fields (values are
    validated for shape, never retained)."""
    if not isinstance(arguments, str):
        return False
    try:
        parsed = json.loads(arguments)
    except ValueError:
        return False
    if not isinstance(parsed, dict):
        return False
    expected = _EXPECTED_ARGUMENT_FIELDS.get(name)
    if expected is None or set(parsed) != set(expected):
        return False
    return True


def success_mode() -> int:
    """Issue step: the controller issues at ITS OWN causal request
    position (a caller-authored flag could not authorize issuance).
    Use step: function_call_output references are validated by the
    controller against the exact-issued registry."""
    deadline = _absolute_deadline()
    try:
        status, content_type, body = _provider_post(
            "/v1/responses", _fixed_request(_synthetic_tools()), deadline
        )
        if status != 200 or content_type != "text/event-stream":
            return fail("issue-wire")
        first = _parse_sse(body, expect_items=2)
        issued = []
        seen_call_ids: set[str] = set()
        for item in first["items"]:
            if item.get("type") != "function_call":
                return fail("issue-item")
            name = item.get("name")
            call_id = item.get("call_id")
            arguments = item.get("arguments")
            if (
                not isinstance(name, str)
                or name not in _EXPECTED_ARGUMENT_FIELDS
                or not isinstance(call_id, str)
                or call_id in seen_call_ids
            ):
                return fail("issue-identity")
            seen_call_ids.add(call_id)
            if not _arguments_closed(name, arguments):
                return fail("issue-arguments")
            issued.append({"family": "function", "name": name, "call_id": call_id})
        if len(issued) < 2:
            return fail("issue-missing")
        outputs = [
            {
                "type": "function_call_output",
                "call_id": call["call_id"],
                "output": "slaif synthetic tool output",
            }
            for call in issued
        ]
        status, content_type, body = _provider_post(
            "/v1/responses", _fixed_request(_synthetic_tools(), outputs), deadline
        )
        if status != 200 or content_type != "text/event-stream":
            return fail("use-wire")
        second = _parse_sse(body, expect_items=1)
        item = second["items"][0]
        if item.get("type") != "message":
            return fail("final-item-type")
        # the public 0.164.0 Message item REQUIRES role
        if item.get("role") != "assistant":
            return fail("final-role")
        final_text_ok = False
        for content in item.get("content") or []:
            if (
                isinstance(content, dict)
                and content.get("type") == "output_text"
                and content.get("text") == FIXED_FINAL_TEXT
            ):
                final_text_ok = True
        if not final_text_ok:
            return fail("final-text-mismatch")
        # no tools in the terminal response: the completed envelope's
        # output is verified by the parser to equal these done items,
        # so message-only items prove the terminal no-tools shape
        if any(i.get("type") != "message" for i in second["items"]):
            return fail("final-tools-present")
        emit(
            {
                "record": "slaif-fixture-standin-v1",
                "status": "pass",
                "mode": "success",
                "uid": os.getuid(),
                "issued_count": len(issued),
                "issued_calls": issued,
                "sse_wire": "responses",
                "final_text_fixed": True,
                "raw_content_retained": False,
                # Measured provider accounting for the host ledger:
                # exactly two POSTs, both admitted (200 SSE).
                "requests": 2,
                "attempts": 2,
            }
        )
        return 0
    except (StandinError, OSError, ValueError, http.client.HTTPException) as exc:
        return fail(closed_reason(exc))


def fail_mode() -> int:
    """Deliberate failure: reference a call id the controller never
    issued.  The CLOSED scenario semantics require the exact order:
    a preloaded result at the issuance state is refused as
    ``preloaded-result`` (inbound results are never progress), so
    the stand-in first performs the controller-owned issuance
    (its own position), THEN references the foreign call id in the
    results state, where the controller must answer the fixed
    closed ``slaif_fixture_unissued`` error envelope (OpenAI-style,
    sanitized) without advancing the scenario."""
    deadline = _absolute_deadline()
    try:
        status, content_type, body = _provider_post(
            "/v1/responses", _fixed_request(_synthetic_tools()), deadline
        )
        if status != 200 or content_type != "text/event-stream":
            return fail("issue-wire")
        first = _parse_sse(body, expect_items=2)
        if any(item.get("type") != "function_call" for item in first["items"]):
            return fail("issue-item")
        status, content_type, body = _provider_post(
            "/v1/responses",
            _fixed_request(
                _synthetic_tools(),
                [
                    {
                        "type": "function_call_output",
                        "call_id": "slaif-never-issued",
                        "output": "slaif synthetic tool output",
                    }
                ],
            ),
            deadline,
        )
        # The error path answers a fixed JSON envelope, not SSE.
        if status != 400 or content_type != "application/json":
            return fail("error-wire")
        parsed = json.loads(body.decode("ascii"))
        error = parsed.get("error")
        if not isinstance(error, dict) or error.get("code") != "slaif_fixture_unissued":
            return fail("expected-unissued")
        emit(
            {
                "record": "slaif-fixture-standin-v1",
                "status": "pass",
                "mode": "fail",
                "uid": os.getuid(),
                "provider_state": "unissued",
                "raw_content_retained": False,
                # Measured provider accounting: two POSTs attempted,
                # only the issuance admitted; the results-state request
                # was refused (400 slaif_fixture_unissued) and still
                # counts as an attempt.
                "requests": 1,
                "attempts": 2,
            }
        )
        return 3  # the declared deliberate-fail exit code
    except (StandinError, OSError, ValueError, http.client.HTTPException) as exc:
        return fail(closed_reason(exc))


def diagnostic_mode() -> int:
    """The default no-tools diagnostic ACTUALLY exercised on the
    live wire: one POST /v1/responses with NO tools must answer the
    fixed assistant final text as the ONLY output item (measured
    closed wire facts; no raw content retained).  The host health
    readiness probe does not count as this exercise."""
    deadline = _absolute_deadline()
    try:
        status, content_type, body = _provider_post("/v1/responses", _fixed_request([]), deadline)
        if status != 200 or content_type != "text/event-stream":
            return fail("diagnostic-wire")
        parsed = _parse_sse(body, expect_items=1)
        items = parsed["items"]
        if len(items) != 1:
            return fail("diagnostic-item-count")
        item = items[0]
        if item.get("type") != "message" or item.get("role") != "assistant":
            return fail("diagnostic-item")
        # terminal no-tools shape: the ONLY output item is the
        # fixed final message
        final_text_ok = False
        for content in item.get("content") or []:
            if (
                isinstance(content, dict)
                and content.get("type") == "output_text"
                and content.get("text") == FIXED_FINAL_TEXT
            ):
                final_text_ok = True
        if not final_text_ok:
            return fail("diagnostic-text-mismatch")
        emit(
            {
                "record": "slaif-fixture-standin-v1",
                "status": "pass",
                "mode": "diagnostic",
                "uid": os.getuid(),
                "requests": 1,
                "attempts": 1,
                "response_kind": "fixed-final-text-no-tools",
                "raw_content_retained": False,
            }
        )
        return 0
    except (StandinError, OSError, ValueError, http.client.HTTPException) as exc:
        return fail(closed_reason(exc))


def auth_binding_mode() -> int:
    """Closed local (017-s) controller auth-binding proof: against
    the ACTUAL loopback provider the subject verifies the three
    closed auth outcomes -- the valid synthetic bearer is admitted
    (200, answering the no-tools diagnostic with the fixed
    assistant final text -- the valid POST CONSUMES the one-shot
    diagnostic), a same-length WRONG bearer is refused (401), and
    a MISSING header is refused (401).  Only closed booleans and
    counts are emitted; the credential value is never emitted,
    logged or retained.  The controller must be constructed with
    the same run token bound (local container only); the hosted CI
    path never runs this mode and keeps its auth-less semantics."""
    deadline = _absolute_deadline()
    try:
        refusal = _subject_identity_refusal(True)
        if refusal is not None:
            return fail(refusal)
        token = env_str("SLAIF_RUN_TOKEN")
        if not re.fullmatch(r"[0-9a-f]{32}", token):
            return fail("run-token-invalid")
        credential = "slaif-synthetic-" + hashlib.sha256(token.encode()).hexdigest()[:32]
        wrong = credential[:-1] + ("0" if credential[-1] != "0" else "1")
        payload = _fixed_request([])
        valid_status, valid_ct, valid_body = _provider_post(
            "/v1/responses", payload, deadline, authorization="Bearer " + credential
        )
        wrong_status, _, _ = _provider_post(
            "/v1/responses", payload, deadline, authorization="Bearer " + wrong
        )
        missing_status, _, _ = _provider_post("/v1/responses", payload, deadline)
        diagnostic_response = "unverified"
        if valid_status == 200 and valid_ct == "text/event-stream":
            # The admitted valid POST is the ACTUAL no-tools
            # diagnostic: its single output item must be the fixed
            # assistant final text with no tool call (measured
            # closed shape; no raw content retained).
            parsed = _parse_sse(valid_body, expect_items=1)
            items = parsed["items"]
            if len(items) == 1:
                item = items[0]
                if item.get("type") != "message" or item.get("role") != "assistant":
                    return fail("diagnostic-item")
                final_text_ok = False
                for content in item.get("content") or []:
                    if (
                        isinstance(content, dict)
                        and content.get("type") == "output_text"
                        and content.get("text") == FIXED_FINAL_TEXT
                    ):
                        final_text_ok = True
                if final_text_ok:
                    diagnostic_response = "fixed-final-text-no-tools"
                else:
                    return fail("diagnostic-text-mismatch")
            else:
                return fail("diagnostic-item-count")
        emit(
            {
                "record": "slaif-fixture-standin-v1",
                "status": "pass",
                "mode": "auth-binding",
                "uid": os.getuid(),
                "valid_admitted": valid_status == 200,
                "wrong_refused": wrong_status == 401,
                "missing_refused": missing_status == 401,
                "diagnostic_response": diagnostic_response,
                "requests": 3,
                "attempts": 3,
            }
        )
        return 0
    except (StandinError, OSError, ValueError, http.client.HTTPException) as exc:
        return fail(closed_reason(exc))


def observe_mode() -> int:
    """Closed NON-CONSUMING observation of the actual controller
    state (local 017-s lifecycle observe): one GET /state reports
    the declared scenario, the controller's own cumulative request
    count and the one-shot diagnostic state as closed values.  This
    command makes NO model POST: it never consumes the diagnostic,
    never advances scenario or exporter state, and the host treats
    it as an observation command, not a provider API request
    (the measured controller counter is a separate actual fact,
    never inferred from a host charge delta)."""
    deadline = _absolute_deadline()
    try:
        refusal = _subject_identity_refusal(True)
        if refusal is not None:
            return fail(refusal)
        # The closed scenario grammar for this observe
        # transport: the unset default AND the explicitly
        # carried historical values (the historical owners set
        # the EXISTING container scenario key explicitly at
        # prepare time) keep the historical two-scenario set
        # byte-for-byte; the canonical AJ transport selects its
        # OWN closed format-capture expectation and NOTHING
        # else.  The key is transport data only — never
        # origin/admission/readiness authority — and the
        # host revalidates the record against its OWN verified
        # entry below this closed grammar (any other carried
        # value is a closed refusal).
        carried = env_str("SLAIF_FIXTURE_SCENARIO", "")
        if carried == "format-capture":
            allowed_scenarios = ("format-capture",)
        elif carried in ("", "diagnostic", "tool-cycle"):
            allowed_scenarios = ("diagnostic", "tool-cycle")
        else:
            return fail("observe-transport")
        status, content_type, body = _provider_get("/state", deadline)
        if status != 200 or content_type != "application/json":
            return fail("observe-wire")
        try:
            record = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return fail("provider-json")
        if (
            not isinstance(record, dict)
            or set(record) != {"record", "scenario", "wire_requests", "diagnostic"}
            or record["record"] != "slaif-fixture-state-v1"
            or record["scenario"] not in allowed_scenarios
            or not isinstance(record["wire_requests"], int)
            or isinstance(record["wire_requests"], bool)
            or not (0 <= record["wire_requests"] <= 512)
            or record["diagnostic"] not in ("unobserved", "observed")
        ):
            return fail("observe-shape")
        emit(
            {
                "record": "slaif-fixture-standin-v1",
                "status": "pass",
                "mode": "observe",
                "uid": os.getuid(),
                "scenario": record["scenario"],
                "wire_requests": record["wire_requests"],
                "diagnostic_state": record["diagnostic"],
                "raw_content_retained": False,
            }
        )
        return 0
    except (StandinError, OSError, ValueError, http.client.HTTPException) as exc:
        return fail(closed_reason(exc))


def _proc_starttime(pid: int) -> int:
    with open(f"/proc/{pid}/stat", "rb") as handle:
        data = handle.read(4096)
    # Field 22 (starttime) is after the comm field, which is
    # parenthesized and may contain spaces/parens.
    tail = data.rsplit(b")", 1)[1].split()
    return int(tail[19])  # 22nd field = index 19 after "state "


def hang_mode() -> int:
    """Flush the pre-hang record (pid + starttime identity for
    PID-reuse-safe stop ownership), spawn the exact owned token-bound
    child, then hold within the finite self-deadline backstop."""
    token = env_str("SLAIF_HANG_TOKEN")
    if not re.fullmatch(r"[0123456789abcdef]{32}", token):
        return fail("hang-token-invalid")
    import subprocess

    deadline = _absolute_deadline()
    with open(f"{SUBJ_DIR}/standin-sentinel", "w", encoding="ascii") as handle:
        handle.write("slaif-synthetic-standin-sentinel\n")
    os.chmod(f"{SUBJ_DIR}/standin-sentinel", 0o600)
    child = subprocess.Popen(
        [sys.executable, "-c", f"import time; time.sleep(300) # slaif-hang-descendant-{token}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    starttime = _proc_starttime(child.pid)
    emit(
        {
            "record": "slaif-fixture-standin-v1",
            "status": "pass",
            "mode": "hang",
            "uid": os.getuid(),
            "descendant_pid": child.pid,
            "descendant_starttime": starttime,
            "descendant_token": token,
            "pre_hold_record_flushed": True,
        }
    )
    try:
        child.wait(timeout=max(0.1, min(300.0, _remaining(deadline))))
    except subprocess.TimeoutExpired:
        # Explicit same-UID exact-owned cleanup of OUR child: the
        # finite sleep is a backstop, not proof of cleanup.
        try:
            child.kill()
        except OSError:
            pass
    try:
        child.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        return fail("hang-child-not-reaped")
    return 0


def output_cap_mode() -> int:
    """Flush the record FIRST, then emit bounded filler that pushes
    the host capture past its finite cap (the cap is enforced host
    side; this proves the ordering the record depends on)."""
    emit(
        {
            "record": "slaif-fixture-standin-v1",
            "status": "pass",
            "mode": "output-cap",
            "uid": os.getuid(),
            "record_flushed_before_filler": True,
        }
    )
    filler = b"slaif-fixture-bounded-filler "
    chunk = filler * (64 * 1024 // len(filler))
    for _ in range(12):  # ~768 KiB of closed filler
        sys.stdout.buffer.write(chunk)
    sys.stdout.buffer.flush()
    return 0


def _verify_owned_pid(pid: int, starttime: int, token: str) -> bool:
    """Fresh identity check of the EXACT reported private-container
    target: uid == own uid, token bound in cmdline, starttime
    (immutable) matching.  A vanished or identity-mismatched pid is
    a reuse/gone condition, never a kill candidate."""
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as handle:
            cmdline = handle.read(4096)
        with open(f"/proc/{pid}/status", encoding="ascii") as handle:
            uid_line = next((line for line in handle if line.startswith("Uid:")), None)
        current_starttime = _proc_starttime(pid)
    except (FileNotFoundError, StopIteration, ValueError, OSError):
        return False
    if uid_line is None or int(uid_line.split()[1]) != os.getuid():
        return False
    if token.encode() not in cmdline:
        return False
    return current_starttime == starttime


def _signal_owned(pid: int, starttime: int, token: str) -> bool:
    """Signal the exact verified target through a PID-BOUND handle:
    FIRST os.pidfd_open (the pidfd binds the specific process that
    had that pid at open time, so a later reused pid is never
    addressable through it), THEN a fresh identity verification of
    /proc/<pid> (uid + token + immutable starttime — a vanished or
    reused pid fails here and is never signalled), THEN
    signal.pidfd_send_signal on that handle with explicit
    siginfo=None and flags=0.  The descriptor is closed on ALL
    paths.  There is NO numeric-PID fallback: if the pidfd API is
    unavailable or denied, exact ownership cannot be established
    and the caller must fail closed (the host's declared
    exact-owned-CID cleanup remains the removal path)."""
    pidfd_open = getattr(os, "pidfd_open", None)
    pidfd_send = getattr(signal, "pidfd_send_signal", None)
    if pidfd_open is None or pidfd_send is None:
        return False
    try:
        fd = pidfd_open(pid)
    except OSError:
        # ESRCH: gone at open; EPERM: policy denies pidfd — in both
        # cases the target is never signalled.
        return False
    try:
        if not _verify_owned_pid(pid, starttime, token):
            return False
        try:
            pidfd_send(fd, signal.SIGTERM, None, 0)
        except OSError:
            # EPERM (policy denies the signal on the bound handle) or
            # ESRCH (the bound process vanished after verification):
            # a fixed closed failure, never an escape and never a
            # numeric-PID retry.
            return False
        return True
    finally:
        try:
            os.close(fd)
        except OSError:
            pass


def stop_owned_mode() -> int:
    """Same-UID exact-owned stopper on the EXACT reported target
    (pid + starttime + token identity in this private PID namespace,
    uid == own uid).  Degraded evidence fails closed; no host UID,
    no name or pattern kill, no broad substring scan as ownership."""
    refusal = _subject_identity_refusal(True)
    if refusal is not None:
        return fail(refusal)
    token = env_str("SLAIF_STOP_TOKEN")
    if not re.fullmatch(r"[0123456789abcdef]{32}", token):
        return fail("stop-token-invalid")
    try:
        expected_pid = env_int("SLAIF_STOP_PID")
        expected_starttime = env_int("SLAIF_STOP_STARTTIME")
    except StandinError:
        return fail("stop-identity-invalid")
    if expected_pid <= 1 or expected_pid == os.getpid():
        return fail("stop-identity-invalid")
    if not (hasattr(os, "pidfd_open") and hasattr(signal, "pidfd_send_signal")):
        # No pidfd ABI: exact ownership cannot be established; the
        # declared closed failure, never a numeric-PID kill.
        return fail("stop-pidfd-unavailable")
    if not _signal_owned(expected_pid, expected_starttime, token):
        return fail("stop-target-absent")
    for _ in range(100):
        if not os.path.isdir(f"/proc/{expected_pid}"):
            break
        time.sleep(0.05)
    else:
        return fail("stop-not-confirmed")
    emit(
        {
            "record": "slaif-fixture-standin-v1",
            "status": "pass",
            "mode": "stop-owned",
            "uid": os.getuid(),
            "stopped_exactly_one": True,
            "same_uid_only": True,
            "starttime_verified": True,
        }
    )
    return 0


def _absolute_anchor_required() -> float:
    """The 017-x hold rides the SAME shared absolute experiment
    anchor the host passes to every scenario: a MISSING anchor is a
    closed refusal (the legacy relative fallback would mint a fresh
    phase deadline, which this mode must never do), a non-numeric
    anchor is invalid, and a non-finite or already-elapsed anchor is
    expired."""
    raw_abs = os.environ.get("SLAIF_FIXTURE_DEADLINE_ABS", "")
    if not raw_abs:
        raise StandinError("self-anchor-missing")
    try:
        absolute = float(raw_abs)
    except ValueError:
        raise StandinError("self-deadline-invalid") from None
    if not math.isfinite(absolute) or absolute <= time.monotonic():
        raise StandinError("self-deadline-expired")
    return absolute


def hold_mode(argv_token: str | None = None) -> int:
    """The 017-x live executable capability hold: verify the
    SUBJECT identity (UID and GID are BOTH the subject identity),
    flush the closed identity record (pid + immutable starttime +
    uid/gid/groups + the bound 32-hex token — a PID-reuse-safe
    identity for the host-side bounded exact-CID correlation)
    FIRST, then hold hard for at most 20 s, further capped by the
    SAME finite absolute experiment anchor, and exit 0 naturally.
    No model POST, no child process, no shell, no host mount: the
    capability under test is a host-side READ of this process's
    CURRENT executable WHILE THIS PROCESS IS ALIVE — a synchronous
    capture that only returns after the hold ends can never prove
    that.  Every pre-hold failure is a closed non-echoing refusal;
    nothing holds before the identity, token and anchor are all
    verified."""
    refusal = _subject_identity_refusal(False)
    if refusal is not None:
        return fail(refusal)
    try:
        if argv_token is not None:
            # The issued marker is bound on the kernel cmdline
            # (the host-side correlation identity for the detached
            # capability start); the closed env form remains the
            # synchronous-test source.
            token = argv_token
        else:
            token = env_str("SLAIF_HOLD_TOKEN")
        if not re.fullmatch(r"[0-9a-f]{32}", token):
            return fail("hold-token-invalid")
        deadline = _absolute_anchor_required()
        emit(
            {
                "record": "slaif-fixture-standin-v1",
                "status": "pass",
                "mode": "hold",
                "uid": os.getuid(),
                "gid": os.getgid(),
                "groups": os.getgroups(),
                "pid": os.getpid(),
                "starttime": _proc_starttime(os.getpid()),
                "token": token,
                "record_flushed_before_hold": True,
            }
        )
        hold_seconds = min(HOLD_MAX_SECONDS, _remaining(deadline))
    except (StandinError, OSError, ValueError) as exc:
        return fail(closed_reason(exc))
    time.sleep(hold_seconds)
    return 0


def main(argv: list[str]) -> int:
    if len(argv) not in (3, 5) or argv[1] != "--mode" or argv[2] not in MODES:
        return fail("mode-invalid")
    hold_token: str | None = None
    if len(argv) == 5:
        # The ONE closed argv extension of this CLI: the hold mode's
        # issued 32-hex marker, carried on the kernel cmdline as the
        # host-side correlation identity for the detached capability
        # start.  No other mode or argument form is admitted — this
        # is not a general shell/argv escape.
        if argv[2] != "hold" or argv[3] != "--hold-token":
            return fail("mode-invalid")
        hold_token = argv[4]
    modes = {
        "measure": measure_mode,
        "pty": pty_mode,
        "success": success_mode,
        "fail": fail_mode,
        "hang": hang_mode,
        "output-cap": output_cap_mode,
        "stop-owned": stop_owned_mode,
        "diagnostic": diagnostic_mode,
        "auth-binding": auth_binding_mode,
        "observe": observe_mode,
        "hold": hold_mode,
    }
    if argv[2] == "hold":
        return hold_mode(hold_token)
    return modes[argv[2]]()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
