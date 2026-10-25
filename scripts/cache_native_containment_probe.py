#!/usr/bin/env python3
"""In-container probe for the disposable-CI containment capability (017-p).

Runs INSIDE the minimal disposable fixture container built from the
repository's digest-pinned Python 3.12 base, under the explicit
confinement the runner requests: ``--network none``, read-only root
filesystem, a dedicated nonroot UID/GID, all capabilities dropped,
``no-new-privileges`` and the explicit ``seccomp=builtin`` policy.

The probe measures the ACTUAL boundary from the child's own point of
view (no asserted flags, no handwritten readiness): child-measured
``/proc/self`` identity, capability and seccomp state, namespace
identities for PID/mount/IPC/UTS/net/user/cgroup compared against
the disposable parent's identities (supplied as synthetic constants
by the runner), the private loopback, absent parent sentinels,
read-only root versus owned writable tmpfs roots, the exact cgroup
memory/PID limits, and empirical keyring-syscall denial with
harmless invalid-argument probes.

Keyring probe law: the reviewed x86_64 ABI
(arch/x86/include/asm/unistd_64.h, verified against
/usr/include/x86_64-linux-gnu/asm/unistd_64.h) defines
``add_key`` 248, ``request_key`` 249, ``keyctl`` 250.  The probes
use NULL pointers and a zero destination (a NULL type cannot
resolve or touch any existing key; without the policy the kernel
fails in ``copy_from_user`` before any lookup or mutation) and an
UNKNOWN keyctl command (-1; valid commands are 0..29 per
/usr/include/linux/keyctl.h, so no read/mutation opcode such as
KEYCTL_DESCRIBE is ever invoked).  Every required vararg is
supplied explicitly with its correct type per the reviewed man
pages: add_key(type, description, payload, datalen, keyring) and
request_key(type, description, callout_info, dest_keyring).  The
default policy must yield EPERM for all three before any
lookup/mutation.  Never reads or enumerates real keys.  Any other
platform is a fixed failure (no skip, no substitution).

Lifecycle law: in hang mode the probe first spawns a tiny owned
sleeping descendant (fixed marker argv, finite 120 s lifetime) and
then keeps PID1 alive (finite 600 s) so the host timeout proves
the ordered parent-death case: a live owned descendant before
PID1 termination, the descendant and the exact container gone
afterward, and the unrelated parent-owned sentinel surviving.
Every deadline is finite: loss of the host controller cannot
leave an indefinitely running owned container.

The probe prints exactly ONE closed-schema JSON line (a pass record,
or a fail record naming the failed check enums) and exits 0 (pass),
1 (check failure) or 3 (deliberate-failure mode after the checks).
Stdlib only.  No repository code, no client, no model, no
credentials, no filesystem outside the owned tmpfs roots.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import errno
import hashlib
import json
import os
import platform
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time

SCHEMA = "slaif-cache-native-containment-probe-v1"
PROBE_PATH = "/opt/slaif-containment-probe.py"
PROBE_MODE_ENV = "SLAIF_PROBE_MODE"

# Reviewed x86_64 syscall numbers (arch/x86/include/asm/unistd_64.h).
_X86_64_SYSCALLS = {"add_key": 248, "request_key": 249, "keyctl": 250}
# Unknown keyctl command: valid commands are 0..29 (linux/keyctl.h),
# so -1 cannot name any read/mutation opcode and, absent the policy,
# fails in the kernel's command dispatch without touching a key.
_KEYCTL_UNKNOWN_COMMAND = -1
_EPERM = errno.EPERM
_NS_ID_RE = re.compile(r"^[a-z0-9_]+:\[\d+\]$")

# Namespace identities compared against the disposable parent: the
# order requires private PID/proc/mount/IPC/UTS/net; the user
# namespace is expected SHARED (the dedicated nonroot uid lives in
# the host user namespace); cgroup is recorded informationally.
_REQUIRED_DIFFER_NS = ("pid", "mnt", "ipc", "uts", "net")
_ALL_NS = ("pid", "mnt", "ipc", "uts", "net", "user", "cgroup")

_MODE_SUCCESS = "success"
_MODE_FAIL = "fail"
_MODE_HANG = "hang"
_MODES = frozenset({_MODE_SUCCESS, _MODE_FAIL, _MODE_HANG})


class ProbeError(RuntimeError):
    """Fixed internal probe error (never emitted as raw detail)."""


def _env_int(name: str) -> int:
    try:
        return int(os.environ[name])
    except (KeyError, ValueError) as exc:
        raise ProbeError(f"missing-or-invalid-env:{name}") from exc


def _env_str(name: str) -> str:
    try:
        value = os.environ[name]
    except KeyError as exc:
        raise ProbeError(f"missing-env:{name}") from exc
    if not value:
        raise ProbeError(f"empty-env:{name}")
    return value


def _status_field(name: str) -> str:
    with open("/proc/self/status", encoding="ascii") as handle:
        for line in handle:
            if line.startswith(name + ":"):
                return line.split(":", 1)[1].strip()
    raise ProbeError(f"missing-status-field:{name}")


def _loopback_echo_ok() -> bool:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]
        payload = b"slaif-loopback-echo-017p"

        def _serve() -> None:
            try:
                conn, _addr = server.accept()
                with conn:
                    data = conn.recv(64)
                    conn.sendall(data)
            except OSError:
                pass

        thread = threading.Thread(target=_serve, daemon=True)
        thread.start()
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=5) as client:
                client.sendall(payload)
                got = client.recv(64)
        finally:
            thread.join(timeout=5)
        return got == payload
    finally:
        server.close()


def _parent_listener_unreachable(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=3):
            return False  # reached: the net namespace is not private
    except (ConnectionRefusedError, OSError):
        return True


def _interfaces_loopback_only() -> bool:
    with open("/proc/net/dev", encoding="ascii") as handle:
        lines = handle.readlines()[2:]
    names = {line.split(":", 1)[0].strip() for line in lines if line.strip()}
    return names == {"lo"}


def _keyring_errno(syscall_no: int, *args: object) -> int:
    """Invoke a raw syscall via glibc and return the resulting errno."""
    lib_name = ctypes.util.find_library("c")
    if not lib_name:
        raise ProbeError("no-libc")
    libc = ctypes.CDLL(lib_name, use_errno=True)
    ctypes.set_errno(0)
    result = libc.syscall(ctypes.c_long(syscall_no), *args)
    err = ctypes.get_errno()
    del result
    return err


def _cgroup_value(name: str) -> str | None:
    for base in ("/sys/fs/cgroup", "/sys/fs/cgroup/memory", "/sys/fs/cgroup/pids"):
        candidate = os.path.join(base, name)
        if os.path.isfile(candidate):
            with open(candidate, encoding="ascii") as handle:
                return handle.read().strip()
    return None


def _writable_tmpfs_bytes(mountpoints: tuple[str, ...]) -> tuple[int, int]:
    """Measure the explicitly selected owned writable tmpfs roots.

    Only the declared writable tmpfs mountpoints are counted (the
    runtime-managed ``/dev`` device mount is not an owned writable
    root); a mount counts only when it is tmpfs AND mounted ``rw``;
    ``size=`` values are parsed with the ``k`` (1024-byte) suffix.
    Returns ``(total_bytes, counted_mounts)``.
    """
    total = 0
    counted = 0
    with open("/proc/mounts", encoding="ascii") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) < 4:
                continue
            mountpoint, fstype, options = parts[1], parts[2], parts[3]
            if mountpoint not in mountpoints or fstype != "tmpfs":
                continue
            option_list = options.split(",")
            if "ro" in option_list:
                continue
            for option in option_list:
                if option.startswith("size="):
                    value = option.split("=", 1)[1]
                    if value.endswith("k"):
                        total += int(value[:-1]) * 1024
                    else:
                        total += int(value)
                    counted += 1
                    break
    return total, counted


def _rootfs_write_denied() -> bool:
    try:
        with open("/probe-write-denied-017p", "wb"):
            raise ProbeError("rootfs-writable")
    except OSError as exc:
        return exc.errno == errno.EROFS
    except FileNotFoundError:
        return False


def _tmpfs_write_ok() -> bool:
    try:
        with tempfile.NamedTemporaryFile(dir="/tmp", prefix="probe-tmp-") as handle:
            handle.write(b"probe tmpfs write 017p\n")
            handle.flush()
        return True
    except OSError:
        return False


def _child_deadline_kill_ok() -> bool:
    child = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(2)
        if child.poll() is not None:
            return False  # exited on its own: the deadline demo did not run
        child.kill()
        child.wait(timeout=10)
        return child.poll() is not None
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=10)


def _parent_namespace_ids() -> dict[str, str]:
    ids: dict[str, str] = {}
    for name in _ALL_NS:
        value = _env_str(f"SLAIF_PROBE_PARENT_NS_{name.upper()}")
        if not _NS_ID_RE.fullmatch(value):
            raise ProbeError(f"malformed-parent-ns:{name}")
        ids[name] = value
    return ids


#: Base marker argv of the hang-mode owned descendant.  The host binds
#: the EXACT owned occurrence through the per-run token (never a bare
#: global marker): it verifies one live occurrence BEFORE container
#: teardown and its disappearance AFTER, by a bounded /proc scan of
#: uid + exact token (no cmdline content emitted).  The finite 120 s
#: child lifetime bounds the orphan window if PID1 is lost.
HANG_DESCENDANT_MARKER_BASE = "import time; time.sleep(120) # slaif-hang-descendant-017p "
_DESCENDANT_TOKEN_RE = re.compile(r"^[0-9a-f]{32}$")
#: Kept alive so the Popen objects (and their fds) survive until exit.
_HANG_DESCENDANTS: list[subprocess.Popen[bytes]] = []


def _spawn_hang_descendant(token: str) -> int:
    if not _DESCENDANT_TOKEN_RE.fullmatch(token):
        raise ProbeError("invalid-descendant-token")
    child = subprocess.Popen(
        [sys.executable, "-c", f"{HANG_DESCENDANT_MARKER_BASE}{token}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _HANG_DESCENDANTS.append(child)
    return child.pid


def main() -> int:
    mode = os.environ.get(PROBE_MODE_ENV, _MODE_SUCCESS)
    if mode not in _MODES:
        print(json.dumps({"schema": SCHEMA, "status": "fail", "failed": ["invalid_mode"]}))
        return 1
    uname = platform.uname()
    if uname.system != "Linux" or uname.machine != "x86_64":
        print(json.dumps({"schema": SCHEMA, "status": "fail", "failed": ["platform"]}))
        return 1

    checks: dict[str, bool] = {}
    measured: dict[str, int] = {}
    cgroup_ns_differs = False
    cgroup_version = "v2"
    probe_digest = ""
    try:
        uid, gid = os.getuid(), os.getgid()
        expected_uid, expected_gid = _env_int("SLAIF_PROBE_UID"), _env_int("SLAIF_PROBE_GID")
        parent_pid = _env_int("SLAIF_PROBE_PARENT_PID")
        parent_port = _env_int("SLAIF_PROBE_PARENT_LISTENER_PORT")
        sentinel_file = _env_str("SLAIF_PROBE_SENTINEL_FILE")
        sentinel_socket = _env_str("SLAIF_PROBE_SENTINEL_SOCKET")
        expected_memory = _env_int("SLAIF_PROBE_EXPECTED_MEMORY_BYTES")
        expected_pids = _env_int("SLAIF_PROBE_EXPECTED_PIDS")
        expected_storage = _env_int("SLAIF_PROBE_EXPECTED_STORAGE_BYTES")
        writable_mounts = tuple(m for m in _env_str("SLAIF_PROBE_WRITABLE_MOUNTS").split(",") if m)
        parent_ns = _parent_namespace_ids()
        descendant_token = ""
        if mode == _MODE_HANG:
            descendant_token = _env_str("SLAIF_PROBE_DESCENDANT_TOKEN")
            if not _DESCENDANT_TOKEN_RE.fullmatch(descendant_token):
                raise ProbeError("invalid-descendant-token")

        checks["dedicated_nonroot_uid_gid"] = (uid, gid) == (
            expected_uid,
            expected_gid,
        ) and uid != 0
        checks["no_supplementary_groups"] = os.getgroups() == [gid]

        cap_fields = ("CapEff", "CapPrm", "CapInh", "CapBnd", "CapAmb")
        capabilities_zero = True
        for field in cap_fields:
            if _status_field(field) != "0000000000000000":
                capabilities_zero = False
        checks["capabilities_all_zero"] = capabilities_zero
        checks["no_new_privs"] = _status_field("NoNewPrivs") == "1"
        checks["seccomp_filter_mode"] = _status_field("Seccomp") == "2"
        checks["private_pid_namespace"] = _status_field("NSpid") == "1"
        checks["parent_proc_absent"] = not os.path.isdir(f"/proc/{parent_pid}")
        checks["parent_sentinels_absent"] = not (
            os.path.lexists(sentinel_file) or os.path.lexists(sentinel_socket)
        )

        # Namespace identities compared against the disposable parent.
        self_ns = {name: os.readlink(f"/proc/self/ns/{name}") for name in _ALL_NS}
        checks["namespace_ids_differ_from_parent"] = all(
            self_ns[name] != parent_ns[name] for name in _REQUIRED_DIFFER_NS
        )
        checks["user_namespace_shared"] = self_ns["user"] == parent_ns["user"]
        cgroup_ns_differs = self_ns["cgroup"] != parent_ns["cgroup"]

        checks["private_netns_loopback_only"] = _interfaces_loopback_only()
        checks["private_loopback_echo_ok"] = _loopback_echo_ok()
        checks["parent_listener_unreachable"] = _parent_listener_unreachable(parent_port)

        checks["rootfs_read_only_denied"] = _rootfs_write_denied()
        checks["tmpfs_write_ok"] = _tmpfs_write_ok()

        cgroup_version = "v2" if os.path.isfile("/sys/fs/cgroup/memory.max") else "v1"
        memory_raw = _cgroup_value("memory.max") or _cgroup_value("memory.limit_in_bytes")
        swap_raw = _cgroup_value("memory.swap.max") or _cgroup_value("memory.memsw.limit_in_bytes")
        pids_raw = _cgroup_value("pids.max")
        measured["memory_limit_bytes"] = (
            int(memory_raw) if memory_raw and memory_raw != "max" else 0
        )
        measured["swap_limit_bytes"] = int(swap_raw) if swap_raw and swap_raw != "max" else 0
        measured["pids_limit"] = int(pids_raw) if pids_raw and pids_raw != "max" else 0
        storage_bytes, counted_mounts = _writable_tmpfs_bytes(writable_mounts)
        measured["writable_storage_bytes"] = storage_bytes
        measured["writable_mount_count"] = counted_mounts
        checks["memory_limit_exact"] = measured["memory_limit_bytes"] == expected_memory
        checks["swap_disabled"] = measured["swap_limit_bytes"] == 0
        checks["pids_limit_exact"] = measured["pids_limit"] == expected_pids
        checks["writable_storage_limit_exact"] = measured[
            "writable_storage_bytes"
        ] == expected_storage and measured["writable_mount_count"] == len(writable_mounts)

        # Harmless invalid-argument keyring probes (never touch a key):
        # NULL type/description/payload/callout_info (add_key: five
        # x86_64 arguments ending in the destination keyring serial;
        # request_key: four x86_64 arguments ending in the destination
        # keyring) and an unknown keyctl command.
        err = _keyring_errno(
            _X86_64_SYSCALLS["add_key"],
            ctypes.c_void_p(None),  # NULL type
            ctypes.c_void_p(None),  # description: NULL
            ctypes.c_void_p(None),  # payload: NULL
            ctypes.c_long(0),  # datalen
            ctypes.c_long(0),  # destination keyring (serial 0: none)
        )
        measured["keyring_errno_add_key"] = err
        err = _keyring_errno(
            _X86_64_SYSCALLS["request_key"],
            ctypes.c_void_p(None),  # NULL type
            ctypes.c_void_p(None),  # description: NULL
            ctypes.c_void_p(None),  # callout_info: NULL
            ctypes.c_long(0),  # dest_keyring: 0 (none)
        )
        measured["keyring_errno_request_key"] = err
        err = _keyring_errno(
            _X86_64_SYSCALLS["keyctl"],
            ctypes.c_long(_KEYCTL_UNKNOWN_COMMAND),  # unknown command: no opcode
            ctypes.c_long(0),
            ctypes.c_long(0),
            ctypes.c_long(0),
            ctypes.c_long(0),
        )
        measured["keyring_errno_keyctl"] = err
        checks["keyring_syscalls_denied"] = (
            measured["keyring_errno_add_key"] == _EPERM
            and measured["keyring_errno_request_key"] == _EPERM
            and measured["keyring_errno_keyctl"] == _EPERM
        )

        checks["child_deadline_kill_ok"] = _child_deadline_kill_ok()
        with open(PROBE_PATH, "rb") as handle:
            probe_digest = hashlib.sha256(handle.read()).hexdigest()
    except Exception:
        print(json.dumps({"schema": SCHEMA, "status": "fail", "failed": ["internal"]}))
        return 1

    failed = sorted(name for name, ok in checks.items() if not ok)
    if failed:
        print(json.dumps({"schema": SCHEMA, "status": "fail", "failed": failed}))
        return 3 if mode == _MODE_FAIL else 1

    record = {
        "schema": SCHEMA,
        "status": "pass",
        "mode": mode,
        "platform": "linux-x86_64",
        "cgroup_version": cgroup_version,
        "cgroup_namespace_differs": cgroup_ns_differs,
        "python_version": platform.python_version(),
        "kernel_release": uname.release,
        "probe_source_sha256": probe_digest,
        "checks": checks,
        "measured": measured,
    }
    if mode == _MODE_HANG:
        # Ordered parent-death case: the live owned descendant is
        # spawned BEFORE the pass record is emitted, so the host sees
        # its (container-internal) pid in the closed record and can
        # positively observe the exact token-bound occurrence before
        # it kills the registered container.
        record["descendant_pid"] = _spawn_hang_descendant(descendant_token)
        record["descendant_token"] = descendant_token
    print(json.dumps(record, sort_keys=True))
    if mode == _MODE_FAIL:
        return 3
    if mode == _MODE_HANG:
        # Both lifetimes are finite (120 s child, 600 s PID1): a lost
        # host controller cannot leave an indefinitely running owned
        # container.
        time.sleep(600)
    return 0


if __name__ == "__main__":
    sys.exit(main())
