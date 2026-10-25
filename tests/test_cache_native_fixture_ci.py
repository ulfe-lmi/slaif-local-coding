"""Pure orchestration tests for the disposable-CI fixture runner (017-r).

These tests exercise ONLY the runner's orchestration logic: the closed
command grammar (exact docker operation forms, the closed scenario-name
enumeration, the env value grammar, the reviewed runtime --version),
the host ledger (admission charged BEFORE work, refused argv counted
and never executed, drained vs retained bytes distinct, provider
request/attempt caps), the guarded preflight/build/query/cleanup flow
through a scripted FakeDocker (full success plus every failure path),
the owned host-side PTY seam (a REAL local pty pair, actual tty
identity/properties, exact fd cleanup, bounded partial on timeout),
the export wire prefix parsing, the full-confinement inspect
verification, the measured sentinel survival and the publication
evidence retention.  No test launches docker, a container, a namespace
or the native binary: the actual fixture proof is the remote
``cache-native-fixture`` CI job, and these tests never substitute for
it.
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import io
import json
import os
import signal
import socket
import stat
import subprocess
import sys
import tarfile
import threading
import time
from pathlib import Path
from typing import Any, NoReturn

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts" / "cache_native_fixture_ci.py"

spec = importlib.util.spec_from_file_location("cache_native_fixture_ci", RUNNER)
assert spec is not None and spec.loader is not None
fci = importlib.util.module_from_spec(spec)
sys.modules["cache_native_fixture_ci"] = fci
spec.loader.exec_module(fci)

model = fci.model
fixture_export = fci.fixture_export

CID = "a" * 64
IMAGE_ID = "sha256:" + "b" * 64

QUIESCE_RECORD = {
    "record": "slaif-fixture-quiesce-v1",
    "provider_sockets_closed": True,
    "handlers_stopped": True,
    "owned_subject_stopped": True,
    "owned_tools_stopped": True,
    "active_connections": 0,
    "residual_writers": 0,
}


def _expected_issued_bindings() -> list[dict[str, Any]]:
    """The COHERENT closed issued bindings: re-derived from the
    stand-in's closed fixed request and the controller's
    single-source call-id / argument-digest derivation (the same
    derivation the host runner revalidates against — never None
    digests, never positions the controller cannot have produced)."""
    payload = fci.fixture_standin._fixed_request(fci.fixture_standin._synthetic_tools())
    bindings = []
    for index, entry in enumerate(payload["tools"]):
        if not isinstance(entry, dict) or entry.get("type") != "function":
            continue
        name = entry.get("name")
        if not isinstance(name, str) or name not in model.KNOWN_TOOL_NAMES:
            continue
        bindings.append(
            {
                "family": "function",
                "name": name,
                "call_id": fci.fixture_controller.expected_call_id(name, 0, index),
                "position": 0,
                "arguments_sha256": fci.fixture_controller.expected_arguments_sha256(name),
            }
        )
    return bindings


# The stand-in's OBSERVED issuance (its closed record) carries the
# same closed-derived call identities the controller would issue —
# the fake never invents literal call ids that the derivation
# cannot produce.
ISSUED_CALLS = [
    {"family": binding["family"], "name": binding["name"], "call_id": binding["call_id"]}
    for binding in _expected_issued_bindings()
]


def _standin_record(mode: str, **extra: object) -> dict[str, Any]:
    record = {
        "record": "slaif-fixture-standin-v1",
        "status": "pass",
        "mode": mode,
        "uid": fci.SUBJECT_UID,
    }
    record.update(extra)
    return record


def _profile_record() -> dict[str, Any]:
    return {
        "record": "slaif-fixture-profile-v1",
        "codex_home_mode": 0o700,
        "codex_home_uid": fci.SUBJECT_UID,
        "base_config_sha256": "1" * 64,
        "base_config_mode": 0o600,
        "profile_file": "early-beta.config.toml",
        "profile_sha256": "2" * 64,
        "profile_mode": 0o600,
        "profile_table_used": False,
        "credential_file_mode": 0o600,
        "credential_sha256": "3" * 64,
        "env_key_name": "SLAIF_SYNTHETIC_API_KEY",
        "loopback_only": True,
    }


def _exec_measurement_record() -> dict[str, Any]:
    return {
        "record": "slaif-fixture-exec-measurement-v1",
        "uid": fci.SUBJECT_UID,
        "gid": fci.SUBJECT_UID,
        "groups": [],
        "capabilities": {
            name: 0 for name in ("ambient", "bounding", "effective", "inheritable", "permitted")
        },
        "no_new_privs": True,
        "seccomp_filter_mode": 2,
        "namespaces": {name: True for name in model.NAMESPACE_FACTS},
        "loopback_only": True,
        "keyring_errno": {name: 1 for name in ("add_key", "request_key", "keyctl")},
        "memory_limit_bytes": fci.MEMORY_BYTES,
        "swap_limit_bytes": 0,
        "swap_source": "v2-swap-max",
        "cpu_limit": model.CPU_LIMIT,
        "pids_limit": fci.PIDS_LIMIT,
        "writable_mounts": [
            # Actual stand-in order: sorted roots (the scan emits
            # the documented data roots in sorted order).
            {
                "root": "/dev/shm",
                "size_bytes": 64 * 1024 * 1024,
                "uid": 0,
                "gid": 0,
                "mode": 0o1777,
            },
            {
                "root": "/run/slaif-ctl",
                "size_bytes": 64 * 1024 * 1024,
                "uid": fci.CONTROLLER_UID,
                "gid": fci.CONTROLLER_UID,
                "mode": 0o700,
            },
            {
                "root": "/run/slaif-subj",
                "size_bytes": 64 * 1024 * 1024,
                "uid": fci.SUBJECT_UID,
                "gid": fci.SUBJECT_UID,
                "mode": 0o700,
            },
            {
                "root": "/tmp",
                "size_bytes": 64 * 1024 * 1024,
                "uid": fci.SUBJECT_UID,
                "gid": fci.SUBJECT_UID,
                "mode": 0o1777,
            },
        ],
        "mounts_scanned": 13,
        "masked_null_aliases": 0,
        "rootfs_readonly": True,
        "controller_pid1_uid": fci.CONTROLLER_UID,
        "private_pid1_exempt": True,
        "denied": {
            name: {"present_21001": True, "subject": "eacces"} for name in model.DENIED_TARGETS
        },
        "host_isolation": {
            "parent_proc_visible": False,
            "host_sentinel_visible": False,
            "host_listener_reachable": False,
        },
    }


def _selected_payload() -> bytes:
    return json.dumps(_selected_payload_object(), sort_keys=True, separators=(",", ":")).encode()


def _selected_payload_object() -> dict[str, Any]:
    # The controller's OWN ledger at export time in the scripted
    # success scenario: two stand-in POSTs plus the quiesce and the
    # export command itself (the runner reconciles this exact
    # identity against the client-side measurements).
    snapshot = {
        "record": "slaif-fixture-selected-snapshot-v1",
        "synthetic": True,
        "issued_calls": _expected_issued_bindings(),
        "originals_bytes": 11,
        "originals_sha256": hashlib.sha256(b"onetwothree").hexdigest(),
        "exporter_uid": fci.CONTROLLER_UID,
        "exported_before_teardown": True,
        "controller_ledger": {"requests": 4, "output_bytes": 2048},
    }
    originals = [base64.b64encode(raw).decode("ascii") for raw in (b"one", b"two", b"three")]
    payload = {
        "quiesce": QUIESCE_RECORD,
        "snapshot": snapshot,
        # The OBSERVED metadata diagnostic of the closed fixed first
        # POST (the tools region was actually offered), observed at
        # the first admitted request position (0 on a fresh
        # controller) — not the canned unobserved marker.
        "diagnostic": model.bounds_diagnostic(
            fci.fixture_standin._fixed_request(fci.fixture_standin._synthetic_tools())
        ),
        "observed_at_position": 0,
        "originals": originals,
        "originals_count": len(originals),
    }
    return payload


def _host_config() -> dict[str, Any]:
    return {
        "Binds": None,
        "ContainerIDFile": "",
        "LogConfig": {"Type": "none", "Config": None},
        "NetworkMode": "none",
        "PortBindings": {},
        "AutoRemove": False,
        "VolumeDriver": "",
        "VolumesFrom": None,
        "CapAdd": None,
        "CapDrop": ["ALL"],
        "IpcMode": "private",
        "PidMode": "",
        "Privileged": False,
        "PublishAllPorts": False,
        "ReadonlyRootfs": True,
        "SecurityOpt": ["no-new-privileges:true", "seccomp=builtin"],
        "UsernsMode": "",
        "Runtime": "runc",
        "ShmSize": fci.SHM_SIZE_BYTES,
        "Mounts": None,
        "DeviceRequests": None,
        "Memory": fci.MEMORY_BYTES,
        "NanoCpus": fci.NANOCPUS,
        "MemorySwap": fci.MEMORY_BYTES,
        "PidsLimit": fci.PIDS_LIMIT,
        # ACTUAL daemon shape: absent device mappings serialize as an
        # empty (non-nil) list, not null (docker CLI create request
        # carries deviceMappings := []container.DeviceMapping{}).
        "Devices": [],
        "Ulimits": [],
        "Tmpfs": {
            "/run/slaif-ctl": "rw,nosuid,size=65536k,uid=21001,gid=21001,mode=700",
            "/run/slaif-subj": "rw,nosuid,size=65536k,uid=21002,gid=21002,mode=700",
            "/tmp": "rw,nosuid,size=65536k,uid=21002,gid=21002,mode=1777",
        },
    }


def _config_json() -> dict[str, Any]:
    return {
        "User": f"{fci.CONTROLLER_UID}:{fci.CONTROLLER_UID}",
        "Image": fci.IMAGE_NAME,
        "Env": ["PYTHONUNBUFFERED=1"],
    }


class FixtureFakeDocker:
    """Record-only fake docker executor for the fixture runner.

    Models the exact closed surface the runner queries (collision
    check, engine preflight, pull/build, per-CID inspect/top/exec,
    ps filters, rm, rmi and the authoritative image-inspect absence
    marker) so failure paths are tested against real field shapes,
    not implementation assumptions."""

    def __init__(
        self,
        *,
        image_present_before: bool = False,
        collision_output: bytes | None = None,
        default_runtime: str = "runc",
        runtimes_path: str = "runc",
        crash_code: str = "137",
        sleep_build: float = 0.0,
        image_absence: str = "absent",
        export_variant: str = "success",
        ghost_container: bool = False,
        healthz_attempts: int = 1,
        build_rc: int = 0,
        id_query_rc: int = 0,
        id_query_output: bytes | None = None,
        skip_id_discovery: bool = False,
        recovery_mode: str = "id",
        rmi_rc: int = 0,
        export_mutate: Any = None,
        rm_fail: str = "none",
        standin_fail: tuple[str, str | None] | None = None,
    ) -> None:
        assert image_absence in ("absent", "query-failed", "present")
        # The export-fail and quiesce-fail SCENARIOS are modeled by
        # their container slugs on every run; this knob only
        # overrides the synthetic-success export wire.
        assert export_variant in (
            "success",
            "sha-mismatch",
            "quiesce-malformed",
            "quiesce-noprefix",
        )
        assert recovery_mode in ("id", "absent", "query-failed", "bad-id")
        assert rm_fail in ("none", "timeout")
        self.image_present_before = image_present_before
        self.collision_output = collision_output
        self.default_runtime = default_runtime
        self.runtimes_path = runtimes_path
        self.crash_code = crash_code
        self.sleep_build = sleep_build
        self.image_absence = image_absence
        self.export_variant = export_variant
        self.ghost_container = ghost_container
        self.healthz_attempts = healthz_attempts
        self.build_rc = build_rc
        self.id_query_rc = id_query_rc
        self.id_query_output = id_query_output
        self.skip_id_discovery = skip_id_discovery
        self.recovery_mode = recovery_mode
        self.rmi_rc = rmi_rc
        self.export_mutate = export_mutate
        self.rm_fail = rm_fail
        self.standin_fail = standin_fail
        self.built = False
        self.image_removed = False
        self.calls: list[list[str]] = []
        self.drained_total = 0
        self.by_name: dict[str, str] = {}
        self.removed: set[str] = set()
        self.seen_env: dict[str, dict[str, str]] = {}
        self.image_tag_inspects = 0
        self.rmi_calls: list[str] = []
        if self.ghost_container:
            self.by_name["slaif-fixture-017r-ghost-0-0-deadbeef"] = hashlib.sha256(
                b"ghost"
            ).hexdigest()

    def _result(self, rc: int, out: bytes, drained: int | None = None) -> Any:
        self.drained_total += len(out) if drained is None else drained
        return fci.ExecResult(rc, out, len(out) if drained is None else drained)

    def _slug_of(self, container_id: str) -> str:
        for name, cid in self.by_name.items():
            if cid == container_id:
                return name.split("-017r-")[1].rsplit("-", 3)[0]
        raise AssertionError("unknown container")

    def __call__(self, argv: list[str], timeout: float) -> Any:
        self.calls.append(list(argv))
        if argv[0] == "runc":
            assert argv[1:] == ["--version"]
            return self._result(0, b"runc version 1.2.3\nspec: 1.0.2-dev\n")
        assert argv[0] == "docker"
        cmd = argv[1:]
        if cmd[:2] == ["version", "--format"]:
            assert cmd[2] == "{{.Server.Version}}"
            return self._result(0, b"27.1.1\n")
        if cmd[:2] == ["info", "--format"]:
            fmt = cmd[2]
            if fmt == "{{range .SecurityOptions}}{{.}} {{end}}":
                return self._result(0, b"name=seccomp name=cgroupns\n")
            if fmt == "{{.DefaultRuntime}}":
                return self._result(0, (self.default_runtime + "\n").encode())
            if fmt == "{{json .Runtimes}}":
                payload = {self.default_runtime: {"path": self.runtimes_path}}
                return self._result(0, json.dumps(payload).encode() + b"\n")
            raise AssertionError(f"unexpected info format: {fmt}")
        if cmd[0] == "pull":
            assert cmd[1] == fci.PINNED_BASE
            return self._result(0, b"pulled\n")
        if cmd[0] == "build":
            if self.sleep_build:
                time.sleep(self.sleep_build)
            if self.build_rc == 0:
                self.built = True
            return self._result(
                self.build_rc, b"built\n" if self.build_rc == 0 else b"build error\n"
            )
        if cmd[:2] == ["inspect", "--format"]:
            fmt, target = cmd[2], cmd[3]
            if target == fci.IMAGE_NAME:
                assert fmt == "{{.Id}}"
                self.image_tag_inspects += 1
                discovery = not self.skip_id_discovery and self.image_tag_inspects == 2
                if self.image_present_before or self.built:
                    if discovery and self.id_query_rc:
                        return self._result(
                            self.id_query_rc,
                            self.id_query_output
                            if self.id_query_output is not None
                            else b"build id query failed\n",
                        )
                    if self.built and not discovery:
                        mode = self.recovery_mode
                        if mode == "id":
                            return self._result(0, (IMAGE_ID + "\n").encode())
                        if mode == "absent":
                            return self._result(
                                1, b"Error: No such object: " + fci.IMAGE_NAME.encode() + b"\n"
                            )
                        if mode == "query-failed":
                            return self._result(1, b"Cannot connect to the Docker daemon.\n")
                        return self._result(0, b"not-an-image-id\n")
                    return self._result(0, (IMAGE_ID + "\n").encode())
                if self.collision_output is not None:
                    return self._result(1, self.collision_output)
                return self._result(1, b"Error: No such object: " + fci.IMAGE_NAME.encode() + b"\n")
            if fmt == "{{.HostConfig.LogConfig.Type}}":
                return self._result(0, b"none\n")
            if fmt == "{{.Config.User}}":
                return self._result(0, f"{fci.CONTROLLER_UID}:{fci.CONTROLLER_UID}\n".encode())
            if fmt == "{{json .HostConfig}}":
                return self._result(0, json.dumps(_host_config()).encode() + b"\n")
            if fmt == "{{json .Config}}":
                return self._result(0, json.dumps(_config_json()).encode() + b"\n")
            raise AssertionError(f"unexpected inspect format: {fmt}")
        if cmd[0] == "create":
            name = cmd[cmd.index("--name") + 1]
            if name in self.by_name:
                return self._result(1, b"Error: name already in use\n")
            cid = hashlib.sha256(name.encode()).hexdigest()
            self.by_name[name] = cid
            env = {
                item.split("=", 1)[0]: item.split("=", 1)[1]
                for item in cmd
                if item.startswith("SLAIF_")
            }
            self.seen_env[name] = env
            return self._result(0, (cid + "\n").encode())
        if cmd[0] == "start":
            return self._result(0, b"")
        if cmd[0] == "wait":
            return self._result(0, (self.crash_code + "\n").encode())
        if cmd[0] == "top":
            return self._result(0, b"UID          PID    COMMAND\nslaifctl     1      python3\n")
        if cmd[0] == "exec":
            return self._exec(argv, cmd)
        if cmd[0] == "ps":
            flt = cmd[cmd.index("--filter") + 1]
            if flt.startswith("name="):
                found = self.by_name.get(flt[5:])
                if found is not None and found not in self.removed:
                    return self._result(0, (found + "\n").encode())
                return self._result(0, b"")
            if flt.startswith("id="):
                target = flt[3:]
                if target in self.by_name.values() and target not in self.removed:
                    return self._result(0, (target + "\n").encode())
                return self._result(0, b"")
            if flt.startswith("ancestor="):
                leftovers = [c for c in self.by_name.values() if c not in self.removed]
                return self._result(0, "".join(c + "\n" for c in leftovers).encode())
            raise AssertionError(f"unexpected filter: {flt}")
        if cmd[0] == "rm":
            cid = cmd[2]
            if self.rm_fail == "timeout":
                # Operational cleanup failure: the guarded Docker
                # operation times out (an _OwnedTimeout, NOT a
                # FixtureError).  The measured drained total (1024
                # bytes emitted, 4096 drained) must still charge the
                # non-resettable host ledger exactly once.
                partial = b"slaif-fixture-cleanup-timeout-partial\n"
                assert len(partial) == 38
                raise fci._OwnedTimeout(list(self.calls[-1]), timeout, partial, drained_bytes=4096)
            self.removed.add(cid)
            return self._result(0, (cid + "\n").encode())
        if cmd[0] == "rmi":
            self.rmi_calls.append(cmd[1])
            if self.rmi_rc == 0:
                self.image_removed = True
            return self._result(
                self.rmi_rc, b"Deleted: untagged\n" if self.rmi_rc == 0 else b"rmi error\n"
            )
        if cmd[:2] == ["image", "inspect"]:
            if self.image_absence == "present":
                return self._result(0, b"[]\n")
            if self.image_absence == "query-failed":
                return self._result(
                    1, b"Cannot connect to the Docker daemon at unix:///var/run/docker.sock.\n"
                )
            return self._result(1, b"Error: No such object: " + IMAGE_ID.encode() + b"\n")
        raise AssertionError(f"unexpected docker command: {cmd}")

    def _exec(self, argv: list[str], cmd: list[str]) -> Any:
        i = 1
        itty = False
        if cmd[i] == "-it":
            itty = True
            i += 1
        assert cmd[i] == "--user"
        uid = cmd[i + 1]
        i += 2
        env: dict[str, str] = {}
        while i < len(cmd) and cmd[i] == "-e":
            key, value = cmd[i + 1].split("=", 1)
            env[key] = value
            i += 2
        cid = cmd[i]
        i += 1
        tail = cmd[i:]
        assert fci._is_cid(cid)
        if tail[:2] == ["python3", "-c"]:
            assert tail[2] == fci.CONTROLLER_PROBE
            assert uid == f"{fci.CONTROLLER_UID}:{fci.CONTROLLER_UID}"
            record = dict(fci.EXPECTED_CTL_PROBE)
            record["healthz_attempts"] = self.healthz_attempts
            line = json.dumps(record, sort_keys=True, separators=(",", ":"))
            return self._result(0, (line + "\n").encode())
        if (
            len(tail) == 4
            and tail[0] == "python3"
            and tail[1] == fci.STANDIN_PATH
            and tail[2] == "--mode"
        ):
            return self._standin_exec(tail[3], itty, env, uid)
        if len(tail) == 2 and tail[0] == "python3" and tail[1] == fci.EXPORT_CLIENT_PATH:
            assert uid == f"{fci.CONTROLLER_UID}:{fci.CONTROLLER_UID}"
            return self._export_exec(cid)
        raise AssertionError(f"unexpected exec tail: {tail}")

    def _standin_exec(self, mode: str, itty: bool, env: dict[str, str], uid: str) -> Any:
        assert uid == f"{fci.SUBJECT_UID}:{fci.SUBJECT_UID}"
        if self.standin_fail is not None and self.standin_fail[0] == mode:
            if self.standin_fail[1] is None:
                # No closed record at all (crash-like): the runner
                # must stay generic, never invent a child cause.
                return self._result(2, b"")
            fail_line = {
                "record": "slaif-fixture-standin-v1",
                "status": "fail",
                "reason": self.standin_fail[1],
            }
            return self._result(
                2, (json.dumps(fail_line, sort_keys=True, separators=(",", ":")) + "\n").encode()
            )
        line = None
        if mode == "diagnostic":
            line = _standin_record(
                "diagnostic",
                requests=1,
                attempts=1,
                response_kind="fixed-final-text-no-tools",
                raw_content_retained=False,
            )
        elif mode == "measure":
            assert "SLAIF_FIXTURE_TMPFS_SPECS" in env
            assert "SLAIF_FIXTURE_PRESENCE_SHA256" in env
            line = _exec_measurement_record()
        elif mode == "pty":
            assert itty, "the pty scenario must attach through -it"
            assert len(env.get("SLAIF_RUN_TOKEN", "")) == 32
            line = _standin_record(
                "pty",
                pty_attached=True,
                term_rows=fci.PTY_ROWS,
                term_cols=fci.PTY_COLS,
                terminal_properties_closed_only=True,
                profile=_profile_record(),
            )
        elif mode == "success":
            line = _standin_record(
                "success",
                issued_count=len(ISSUED_CALLS),
                issued_calls=ISSUED_CALLS,
                sse_wire="responses",
                final_text_fixed=True,
                raw_content_retained=False,
                requests=2,
                attempts=2,
            )
        elif mode == "fail":
            line = _standin_record(
                "fail",
                provider_state="unissued",
                raw_content_retained=False,
                requests=1,
                attempts=2,
            )
        elif mode == "hang":
            token = env.get("SLAIF_HANG_TOKEN", "")
            assert len(token) == 32 and token == env["SLAIF_HANG_TOKEN"]
            line = _standin_record(
                "hang",
                descendant_pid=4242,
                descendant_starttime=98765,
                descendant_token=token,
                pre_hold_record_flushed=True,
            )
            partial = (json.dumps(line, sort_keys=True) + "\n").encode()
            # The hang's emitted bytes ARE its measured drained total
            # (retained + discarded; equal in this model): count them
            # exactly once so the host ledger's charged total matches
            # the emitter's measured total after the timeout charge.
            self.drained_total += len(partial)
            raise fci._OwnedTimeout(list(self.calls[-1]), 1.0, partial)
        elif mode == "stop-owned":
            assert env.get("SLAIF_STOP_PID") == "4242"
            assert env.get("SLAIF_STOP_STARTTIME") == "98765"
            line = _standin_record(
                "stop-owned", stopped_exactly_one=True, same_uid_only=True, starttime_verified=True
            )
        elif mode == "output-cap":
            head = (
                json.dumps(
                    _standin_record("output-cap", record_flushed_before_filler=True), sort_keys=True
                )
                + "\n"
            ).encode()
            pad = fci.OUTPUT_CAP - len(head)
            pattern = b"slaif-fixture-bounded-filler "
            filler = pattern * (pad // len(pattern))
            filler += b"p" * (pad - len(filler))
            out = head + filler
            assert len(out) == fci.OUTPUT_CAP
            return self._result(0, out, drained=fci.OUTPUT_CAP + 256 * 1024)
        else:
            raise AssertionError(f"unexpected standin mode: {mode}")
        assert line is not None
        return self._result(
            3 if mode == "fail" else 0, (json.dumps(line, sort_keys=True) + "\n").encode()
        )

    def _export_exec(self, cid: str) -> Any:
        # The scenario controller MODES are modeled by the container
        # slug: export-fail mode corrupts the export frame after a
        # bounded prefix, quiesce-fail mode never produces a closed
        # quiesce record, and the synthetic-success container gets
        # the healthy payload (with the optional wire overrides).
        slug = self._slug_of(cid)
        if slug == "export-fail":
            return self._result(
                2,
                b"quiesce-ok "
                + json.dumps(QUIESCE_RECORD, sort_keys=True, separators=(",", ":")).encode()
                + b"\nexport-fail export-invalid\n",
            )
        if slug == "quiesce-fail":
            return self._result(2, b"export-fail quiesce-state\n")
        if slug == "synthetic-success":
            if self.export_mutate is not None:
                obj = _selected_payload_object()
                self.export_mutate(obj)
                payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
            else:
                payload = _selected_payload()
            sha = hashlib.sha256(payload).hexdigest()
            if self.export_variant == "sha-mismatch":
                sha = "0" * 64
            quiesce = (
                b"quiesce-ok "
                + json.dumps(QUIESCE_RECORD, sort_keys=True, separators=(",", ":")).encode()
            )
            if self.export_variant == "quiesce-malformed":
                quiesce = b'quiesce-ok {"provider_sockets_closed"'
            if self.export_variant == "quiesce-noprefix":
                quiesce = (
                    b"quiesce-no "
                    + json.dumps(QUIESCE_RECORD, sort_keys=True, separators=(",", ":")).encode()
                )
            return self._result(0, quiesce + b"\nexport-sha256 " + sha.encode() + b"\n" + payload)
        raise AssertionError(f"unexpected export container: {slug}")
        sha = hashlib.sha256(payload).hexdigest()
        if self.export_variant == "sha-mismatch":
            sha = "0" * 64
        quiesce = (
            b"quiesce-ok "
            + json.dumps(QUIESCE_RECORD, sort_keys=True, separators=(",", ":")).encode()
        )
        if self.export_variant == "quiesce-malformed":
            quiesce = b'quiesce-ok {"provider_sockets_closed"'
        if self.export_variant == "quiesce-noprefix":
            quiesce = (
                b"quiesce-no "
                + json.dumps(QUIESCE_RECORD, sort_keys=True, separators=(",", ":")).encode()
            )
        return self._result(0, quiesce + b"\nexport-sha256 " + sha.encode() + b"\n" + payload)


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    for name in (
        "cache_native_fixture_ci.py",
        "cache_native_fixture_model.py",
        "cache_native_fixture_controller.py",
        "cache_native_fixture_standin.py",
        "cache_native_fixture_export_client.py",
        "cache_native_fixture.Dockerfile",
    ):
        shutil_copy = (REPO_ROOT / "scripts" / name).read_bytes()
        (repo / "scripts" / name).write_bytes(shutil_copy)
    (repo / "Dockerfile").write_bytes((REPO_ROOT / "Dockerfile").read_bytes())
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_bytes(
        (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_bytes()
    )
    return repo


def _fake_fetch(dest_dir: Any, deadline: Any) -> dict[str, str | int]:
    binary = dest_dir / model.ARTIFACT_BINARY_NAME
    binary.write_bytes(b"slaif-fake-native-binary")
    (dest_dir / "LICENSE").write_bytes(b"Apache-2.0 (fake for pure tests)")
    (dest_dir / "NOTICE").write_bytes(b"MIT (fake notice for pure tests)")
    return {
        "binary_sha256": hashlib.sha256(b"slaif-fake-native-binary").hexdigest(),
        "binary_size": len(b"slaif-fake-native-binary"),
        "license_sha256": hashlib.sha256(b"Apache-2.0 (fake for pure tests)").hexdigest(),
        "notice_sha256": hashlib.sha256(b"MIT (fake notice for pure tests)").hexdigest(),
    }


def _dead_sentinel() -> subprocess.Popen[bytes]:
    proc = subprocess.Popen(
        [sys.executable, "-c", "pass"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    proc.wait(timeout=10)
    return proc


def _setup(
    tmp_path: Path,
    monkeypatch: Any,
    fake: FixtureFakeDocker,
    *,
    anchor_seconds: float | None = None,
    dead_sentinel: bool = False,
) -> tuple[Path, Path, Path]:
    repo = _make_repo(tmp_path)
    work = tmp_path / "work"
    evidence_out = tmp_path / "evidence" / "selected-evidence.json"
    monkeypatch.setattr(fci, "fetch_public_artifact", _fake_fetch)
    # The orchestration fake writes fake bytes: the pinned public
    # identity constants are patched to those bytes' actual digests
    # (the flow under test is orchestration, not public identity).
    monkeypatch.setattr(
        model,
        "ARTIFACT_LICENSE_SHA256",
        hashlib.sha256(b"Apache-2.0 (fake for pure tests)").hexdigest(),
    )
    monkeypatch.setattr(
        model,
        "ARTIFACT_NOTICE_SHA256",
        hashlib.sha256(b"MIT (fake notice for pure tests)").hexdigest(),
    )
    monkeypatch.setattr(fci, "_count_fixture_uid_processes", lambda uid: 0)
    counts = [1, 0]
    monkeypatch.setattr(fci, "_count_uid_marker_processes", lambda uid, marker: counts.pop(0))
    if anchor_seconds is not None:
        monkeypatch.setattr(fci, "TOTAL_ANCHOR_SECONDS", anchor_seconds)
    if dead_sentinel:
        monkeypatch.setattr(fci, "_spawn_parent_sentinel", _dead_sentinel)
    return repo, work, evidence_out


# -- closed grammar ----------------------------------------------------------


def test_name_pattern_lockstep_with_model_scenarios() -> None:
    alternation = fci._NAME_PATTERN.split("slaif-fixture-017r-(?:")[1]
    alternation = alternation.split(")-\\d+")[0]
    assert set(alternation.split("|")) == set(model.SCENARIO_NAMES)
    for scenario in model.SCENARIO_NAMES:
        name = f"slaif-fixture-017r-{scenario}-4242-7-abcd1234"
        assert fci._NAME_RE.fullmatch(name)
    for name in (
        "slaif-fixture-017r-bogus-scenario-4242-7-abcd1234",
        "slaif-fixture-017r-synthetic-success-4242-7-abcd123",
        "other-fixture-017r-synthetic-success-4242-7-abcd1234",
    ):
        assert not fci._NAME_RE.fullmatch(name)


def test_env_value_grammar_closed() -> None:
    assert fci._ENV_VALUE_RE.fullmatch("/home/runner/work/_temp/slaif-fixture-017r/sentinels/x")
    assert fci._ENV_VALUE_RE.fullmatch("mnt:[4026531836]")
    assert fci._ENV_VALUE_RE.fullmatch("1234567890.123456")
    for bad in ("", "has space", "semi;colon", "quote'x", "dollar$x"):
        assert not fci._ENV_VALUE_RE.fullmatch(bad)


def test_match_docker_top_closed() -> None:
    assert fci._match_docker_top(["docker", "top", CID])
    assert not fci._match_docker_top(["docker", "top", "abc"])
    assert not fci._match_docker_top(["docker", "top", CID, "ps", "aux"])


def test_inspect_formats_closed() -> None:
    for fmt in (
        "{{json .HostConfig}}",
        "{{json .Config}}",
        "{{.HostConfig.LogConfig.Type}}",
        "{{.Config.User}}",
    ):
        assert fci._match_docker_inspect(["docker", "inspect", "--format", fmt, CID])
    # The wrong field name and every open format stay refused.
    for fmt in ("{{.HostConfig.LogDriver}}", "{{.Name}}", "{{json .}}"):
        assert not fci._match_docker_inspect(["docker", "inspect", "--format", fmt, CID])


def test_create_argv_allowlist_lockstep_includes_shm_bound() -> None:
    # The confinement builder and the host allowlist agree on the
    # EXACT argv, including the explicit /dev/shm bound (the
    # reconciled writable-data surface): any drift between the
    # configured confinement and the admitted grammar fails closed.
    name = "slaif-fixture-017r-synthetic-success-1-0-01234567"
    label = "slaif-owned-fixture-017r=" + "a" * 32
    argv = fci.build_run_conf_argv(fci.IMAGE_NAME, name, label, {})
    assert fci._match_docker_create(argv)
    # The explicit bound is present with the documented value.
    assert "--shm-size" in argv
    assert argv[argv.index("--shm-size") + 1] == fci.SHM_SIZE_ARG
    # Dropping the explicit shm bound breaks the lockstep.
    broken = [a for a in argv if a not in ("--shm-size", fci.SHM_SIZE_ARG)]
    assert not fci._match_docker_create(broken)
    # A wrong shm size is refused just as surely.
    wrong = list(argv)
    wrong[wrong.index(fci.SHM_SIZE_ARG)] = "128m"
    assert not fci._match_docker_create(wrong)


# -- host ledger -------------------------------------------------------------


def test_ledger_admission_charged_before_work_and_refusals_counted() -> None:
    calls: list[list[str]] = []

    def executor(argv: list[str], timeout: float) -> Any:
        calls.append(list(argv))
        return fci.ExecResult(0, b"ok", drained_bytes=2)

    deadline = fci._RunDeadline(time.monotonic() + 100.0)
    ledger = fci._RunLedger(model.FixtureBudgets())
    guarded = fci._guarded_execute(executor, deadline, ledger)
    with pytest.raises(fci.FixtureError, match="argv-untrusted"):
        guarded(["/usr/local/bin/codex", "--version"], 5.0)
    with pytest.raises(fci.FixtureError, match="argv-untrusted"):
        guarded(["sh", "-c", "codex --help"], 5.0)
    assert ledger.refusals == 2
    assert ledger.admissions == 0
    assert calls == []
    guarded(["docker", "ps", "-aq", "--filter", "id=" + CID], 5.0)
    assert ledger.admissions == 1
    assert ledger.bytes_retained == 2
    assert ledger.bytes_drained == 2
    assert calls == [["docker", "ps", "-aq", "--filter", "id=" + CID]]


def test_guarded_execute_requires_ledger() -> None:
    deadline = fci._RunDeadline(time.monotonic() + 100.0)
    with pytest.raises(TypeError):
        fci._guarded_execute(lambda argv, timeout: None, deadline)


def test_ledger_http_caps_and_identity_validate_before_mutation() -> None:
    budgets = model.FixtureBudgets(max_requests=10, max_attempts=12)
    ledger = fci._RunLedger(budgets)
    ledger.charge_http(budgets.max_requests, budgets.max_attempts, budgets.max_requests, 0)
    assert ledger.api_requests == 10
    assert ledger.api_attempts == 12
    assert ledger.requests_admitted == 10
    assert ledger.requests_refused == 0
    with pytest.raises(fci.FixtureError, match="ledger-request-cap"):
        ledger.charge_http(1, 1, 1, 0)
    # The refused charge left EVERY counter untouched (validation
    # happens before any mutation): no partial accounting, no
    # refund, no reset.
    assert ledger.api_requests == 10
    assert ledger.api_attempts == 12
    assert ledger.requests_admitted == 10
    assert ledger.requests_refused == 0
    with pytest.raises(fci.FixtureError, match="ledger-attempt-cap"):
        ledger.charge_http(0, budgets.max_attempts + 1, 0, 0)
    fresh = fci._RunLedger(budgets)
    with pytest.raises(fci.FixtureError, match="ledger-attempt-identity"):
        fresh.charge_http(2, 1, 2, 0)
    with pytest.raises(fci.FixtureError, match="ledger-requests-invalid"):
        fresh.charge_http(-1, 0, 0, 0)
    with pytest.raises(fci.FixtureError, match="ledger-outcome-identity"):
        fresh.charge_http(2, 2, 1, 0)
    assert fresh.api_requests == 0
    assert fresh.api_attempts == 0
    assert fresh.requests_admitted == 0
    assert fresh.requests_refused == 0


def test_ledger_reservation_is_pre_work_enforcement() -> None:
    # A scenario whose closed worst-case wire bound does not fit the
    # REMAINING API budgets (current counters + worst case) is
    # refused BEFORE its work; reservations check, they do not hold
    # — the MEASURED charges are what accumulate — and an overbound
    # charge is refused with the counters untouched.
    budgets = model.FixtureBudgets(max_requests=5, max_attempts=6)
    ledger = fci._RunLedger(budgets)
    ledger.reserve_http(3, 4)
    with pytest.raises(fci.FixtureError, match="ledger-reserve-identity"):
        ledger.reserve_http(2, 1)
    with pytest.raises(fci.FixtureError, match="ledger-reserve-requests-invalid"):
        ledger.reserve_http(-1, 0)
    assert ledger.api_requests == 0
    assert ledger.api_attempts == 0
    # After the MEASURED charge of the first scenario, the REMAINING
    # bound is what the next reservation must fit.
    ledger.charge_http(3, 4, 2, 1)
    with pytest.raises(fci.FixtureError, match="ledger-request-reserve"):
        ledger.reserve_http(3, 3)  # 3 + 3 > 5
    with pytest.raises(fci.FixtureError, match="ledger-attempt-reserve"):
        ledger.reserve_http(0, 3)  # 4 + 3 > 6
    ledger.reserve_http(2, 2)  # 3 + 2 == 5 fits exactly
    assert ledger.api_requests == 3
    assert ledger.api_attempts == 4
    assert ledger.requests_admitted == 2
    assert ledger.requests_refused == 1


def test_ledger_output_cap_drained_not_retained() -> None:
    ledger = fci._RunLedger(model.FixtureBudgets())
    cap = model.FixtureBudgets().output_cap_bytes
    ledger.charge(fci.ExecResult(0, b"x" * 10, drained_bytes=cap))
    with pytest.raises(fci.FixtureError, match="ledger-output-cap"):
        ledger.charge(fci.ExecResult(0, b"", drained_bytes=1))
    # The overbound charge was still accounted (measured, not hidden):
    # drained total is cap+1 while retained capture stayed tiny.
    assert ledger.bytes_retained == 10
    assert ledger.bytes_drained == cap + 1


# -- export prefix parsing ---------------------------------------------------


def test_parse_prefixed_record_positive_and_negative() -> None:
    body = json.dumps(QUIESCE_RECORD, sort_keys=True).encode()
    record = fci._parse_prefixed_record(b"quiesce-ok " + body, fci._QUIESCE_PREFIX)
    assert record == QUIESCE_RECORD
    with pytest.raises(fci.FixtureError, match="export-quiesce-state"):
        fci._parse_prefixed_record(b"quiesce-no " + body, fci._QUIESCE_PREFIX)
    with pytest.raises(fci.FixtureError, match="probe-output-malformed"):
        fci._parse_prefixed_record(b"quiesce-ok {partial", fci._QUIESCE_PREFIX)
    with pytest.raises(fci.FixtureError, match="probe-output-missing"):
        fci._parse_prefixed_record(b"quiesce-ok ", fci._QUIESCE_PREFIX)


# -- full-confinement verification -------------------------------------------


@pytest.mark.parametrize(
    "mutate",
    [
        lambda hc: hc.update(Binds=["/host:/mnt"]),
        lambda hc: hc.update(Devices=[{"PathOnHost": "/dev/x"}]),
        lambda hc: hc.update(NetworkMode="host"),
        lambda hc: hc.update(MemorySwap=fci.MEMORY_BYTES + 1),
        lambda hc: hc.update(ReadonlyRootfs=False),
        lambda hc: hc.update(CapDrop=["NET_ADMIN"]),
        lambda hc: hc.update(SeccompProfileName="unconfined"),
        lambda hc: hc.update(NoNewPrivileges=False),
        lambda hc: hc.update(SecurityOpt=[]),
        lambda hc: hc.pop("SecurityOpt"),
        lambda hc: hc.update(SecurityOpt=["no-new-privileges:true"]),
        lambda hc: hc.update(SecurityOpt=["no-new-privileges:true", "seccomp=unconfined"]),
        lambda hc: hc.update(Mounts=[{"Type": "bind", "Source": "/host", "Target": "/mnt"}]),
        lambda hc: hc.update(Mounts=[{"Type": "volume", "Source": "vol", "Target": "/data"}]),
        lambda hc: hc.update(Mounts=[{"Type": "tmpfs", "Source": "tmpfs", "Target": "/unlisted"}]),
        lambda hc: hc.update(Mounts="not-a-list"),
        lambda hc: hc.update(DeviceRequests=[{"Count": 1, "Driver": "nvidia"}]),
        lambda hc: hc.update(ShmSize=32 * 1024 * 1024),
        lambda hc: hc.pop("ShmSize"),
        lambda hc: hc.pop("DeviceRequests"),
        lambda hc: hc.update(Privileged=True),
        lambda hc: hc.update(PidsLimit=fci.PIDS_LIMIT + 1),
        lambda hc: hc.update(NanoCpus=fci.NANOCPUS * 2),
        lambda hc: hc.update(LogConfig={"Type": "json-file"}),
        lambda hc: hc["Tmpfs"].pop("/tmp"),
        lambda hc: hc["Tmpfs"].update(extra="rw,nosuid,size=65536k,uid=21002,gid=21002,mode=1777"),
        lambda hc: hc["Tmpfs"].update(
            **{"/tmp": "rw,nosuid,size=128k,uid=21002,gid=21002,mode=1777"}
        ),
        lambda hc: hc["Tmpfs"].update(
            **{"/tmp": "rw,nosuid,size=65536k,uid=21003,gid=21002,mode=1777"}
        ),
        lambda hc: hc["Tmpfs"].update(
            **{"/tmp": "rw,nosuid,size=65536k,uid=21002,gid=21002,mode=700"}
        ),
        lambda hc: hc.pop("Binds"),
    ],
)
def test_verify_confinement_rejects_drift(mutate: Any) -> None:
    host = _host_config()
    mutate(host)
    with pytest.raises(fci.FixtureError, match="confinement"):
        fci._verify_confinement(host, _config_json())


def test_verify_confinement_accepts_exact() -> None:
    fci._verify_confinement(_host_config(), _config_json())


@pytest.mark.parametrize("key", ["Binds", "Devices", "VolumesFrom", "DeviceRequests"])
@pytest.mark.parametrize("absent", [None, []])
def test_verify_confinement_absent_state_null_or_empty(key: Any, absent: Any) -> None:
    # Both Go slice JSON shapes are the absent state (see the
    # runner's schema note): null (nil slice) and [] (non-nil empty
    # slice sent by the docker CLI) must both pass.
    host = _host_config()
    host[key] = absent
    fci._verify_confinement(host, _config_json())


@pytest.mark.parametrize("key", ["Binds", "Devices", "VolumesFrom", "DeviceRequests"])
@pytest.mark.parametrize("bad", ["bogus", 0, True, {"x": 1}])
def test_verify_confinement_absent_state_wrong_type_rejected(key: Any, bad: Any) -> None:
    host = _host_config()
    host[key] = bad
    with pytest.raises(fci.FixtureError, match=f"confinement-value:{key}"):
        fci._verify_confinement(host, _config_json())
    config = _config_json()
    config["User"] = "0:0"
    with pytest.raises(fci.FixtureError, match="confinement-user"):
        fci._verify_confinement(_host_config(), config)
    config = _config_json()
    config["Image"] = "other:tag"
    with pytest.raises(fci.FixtureError, match="confinement-image"):
        fci._verify_confinement(_host_config(), config)


# -- full run through FakeDocker ----------------------------------------------


def test_run_full_success_fake_docker(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker()
    repo, work, evidence_out = _setup(tmp_path, monkeypatch, fake)
    result = fci.run(repo, work, fake, evidence_out=str(evidence_out))
    assert result["status"] == "pass"
    assert result["schema"] == fci.SCHEMA
    assert result["codex_invoked"] is False
    # The measured aggregate provider accounting across ALL
    # scenarios, published as the DISTINCT closed quantities:
    # api_requests = 1 diagnostic POST + 2 success POSTs +
    #   2 fail POSTs + 2 export-fail commands + 1 quiesce-fail
    #   command = 10 (every refused call is still a request);
    # api_attempts = the same 10 (each attempt received a response
    #   in the scripted run);
    # admitted = 1 diagnostic + 2 success POSTs + quiesce(ok) +
    #   export(ok) + quiesce-fail's refused quiesce excluded = 7;
    # refused = fail's 400 POST + export-fail's invalid frame +
    #   quiesce-fail's refused quiesce = 3; 7 + 3 == 10;
    # healthz_attempts = the nine readiness probes' measured
    #   polling (a distinct quantity, never an API charge).
    for record in (result["summary"], result["publish"]):
        assert record["api_requests"] == 10
        assert record["api_attempts"] == 10
        assert record["requests_admitted"] == 7
        assert record["requests_refused"] == 3
        assert record["healthz_attempts"] == 9
    # bytes_drained is ALL drained/emitted bytes (the output-cap
    # scenario drained 256KiB beyond its retained capture);
    # bytes_retained is the distinct bounded kept total.
    assert result["publish"]["bytes_drained"] == fake.drained_total
    ledger = result["scenarios_detail"]["ledger"]
    assert ledger["api_requests"] == 10
    assert ledger["api_attempts"] == 10
    assert ledger["requests_admitted"] == 7
    assert ledger["requests_refused"] == 3
    assert ledger["healthz_attempts"] == 9
    assert ledger["docker_refusals"] == 0
    # Every admitted host command is exactly the executed call list.
    assert ledger["docker_admissions"] == len(fake.calls)
    assert 0 < ledger["bytes_retained"] < ledger["bytes_drained"]
    assert result["publish"]["bytes_retained"] == ledger["bytes_retained"]
    assert result["teardown"]["sentinel_survived"] is True
    assert result["image_removed"] is True
    assert result["no_leftover_containers"] is True
    # The measured reconciled writable-data surface is carried
    # closed into the summary: the exact documented roots and the
    # 256 MiB effective total (192 MiB app budgets + 64 MiB /dev/shm).
    summary_mounts = result["summary"]["writable_mounts"]
    assert [m["root"] for m in summary_mounts] == sorted(
        {m["root"] for m in _exec_measurement_record()["writable_mounts"]}
    )
    assert result["summary"]["writable_data_total_bytes"] == (256 * 1024 * 1024)
    scenarios = {e["name"]: e["state"] for e in result["summary"]["scenarios"]}
    assert scenarios == dict(model.REQUIRED_SCENARIOS)
    assert result["scenarios_detail"]["synthetic-success"]["retained_capture_bytes"] == len(
        _selected_payload()
    )
    # The stand-in's measured client facts and the trusted
    # controller's own exported ledger agree on the closed identity.
    success_detail = result["scenarios_detail"]["synthetic-success"]
    assert success_detail["standin_requests"] == 2
    assert success_detail["standin_attempts"] == 2
    assert success_detail["controller_ledger_requests"] == 4
    # Preflight/build flow: collision check first, then the exact
    # reviewed query vocabulary, then pull/build/id.
    assert fake.calls[0] == ["docker", "inspect", "--format", "{{.Id}}", fci.IMAGE_NAME]
    assert fake.calls[1] == ["docker", "version", "--format", "{{.Server.Version}}"]
    assert fake.calls[2] == [
        "docker",
        "info",
        "--format",
        "{{range .SecurityOptions}}{{.}} {{end}}",
    ]
    assert fake.calls[3] == ["docker", "info", "--format", "{{.DefaultRuntime}}"]
    assert fake.calls[4] == ["docker", "info", "--format", "{{json .Runtimes}}"]
    assert fake.calls[5] == ["runc", "--version"]
    assert fake.calls[6] == ["docker", "pull", fci.PINNED_BASE]
    assert fake.calls[7][:4] == ["docker", "build", "-t", fci.IMAGE_NAME]
    assert fake.calls[8] == ["docker", "inspect", "--format", "{{.Id}}", fci.IMAGE_NAME]
    # Every generated container name matched the closed grammar.
    for call in fake.calls:
        if call[1] == "create":
            assert fci._NAME_RE.fullmatch(call[call.index("--name") + 1])
    # The no-tools diagnostic was actually exercised (21002, one request).
    diag = [c for c in fake.calls if c[-2:] == ["--mode", "diagnostic"]]
    assert len(diag) == 1
    assert "-it" not in diag[0]
    # The pty scenario attached through an actual -it argv.
    pty = [c for c in fake.calls if c[1] == "exec" and "-it" in c]
    assert len(pty) == 1
    assert pty[0][-1] == "pty"
    # The exported call ids are cross-identical between the stand-in
    # record and the host re-validated snapshot.
    assert result["scenarios_detail"]["synthetic-success"]["issued_count"] == 2
    assert fake.image_removed
    # The evidence was retained at the protected destination BEFORE
    # the disposable work root was destroyed.
    assert not work.exists()
    assert evidence_out.exists()
    assert stat.S_IMODE(evidence_out.lstat().st_mode) == 0o600
    assert stat.S_IMODE(evidence_out.parent.lstat().st_mode) == 0o700
    assert (
        hashlib.sha256(evidence_out.read_bytes()).hexdigest() == result["summary"]["export_sha256"]
    )
    assert result["evidence_out"] == str(evidence_out)


def test_run_image_collision_never_adopted(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(image_present_before=True)
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="image-collision"):
        fci.run(repo, work, fake)
    assert fake.built is False


def test_run_image_collision_query_unverified(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(collision_output=b"Cannot connect to the Docker daemon.\n")
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="image-collision-unverified"):
        fci.run(repo, work, fake)


def test_run_preflight_refuses_daemon_codex_runtime(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(default_runtime="codex")
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="argv-untrusted"):
        fci.run(repo, work, fake)


def test_run_preflight_refuses_absolute_runtime_path(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(default_runtime="/usr/local/bin/codex")
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="runtime-invalid"):
        fci.run(repo, work, fake)


def test_run_sentinel_death_fails_and_cleanup_visible(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker()
    repo, work, _ = _setup(tmp_path, monkeypatch, fake, dead_sentinel=True)
    with pytest.raises(fci.FixtureError, match="sentinel-process-died"):
        fci.run(repo, work, fake)
    # The exact owned sweep still covered every registered container.
    assert set(fake.by_name.values()) == fake.removed
    assert fake.image_removed


def test_run_hang_descendant_not_observed(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker()
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    monkeypatch.setattr(fci, "_count_uid_marker_processes", lambda uid, marker: 2)
    with pytest.raises(fci.FixtureError, match="descendant-not-observed"):
        fci.run(repo, work, fake)


def test_run_hang_descendant_leftover(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker()
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    counts = [1, 1]
    monkeypatch.setattr(fci, "_count_uid_marker_processes", lambda uid, marker: counts.pop(0))
    with pytest.raises(fci.FixtureError, match="descendant-leftover"):
        fci.run(repo, work, fake)


def test_run_export_sha_mismatch(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(export_variant="sha-mismatch")
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="export-sha-mismatch"):
        fci.run(repo, work, fake)


def test_run_quiesce_malformed_record(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(export_variant="quiesce-malformed")
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="probe-output-malformed"):
        fci.run(repo, work, fake)


def test_run_quiesce_prefix_missing(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(export_variant="quiesce-noprefix")
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="export-quiesce-state"):
        fci.run(repo, work, fake)


def test_run_crash_code_mismatch(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(crash_code="139")
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="crash-code-mismatch"):
        fci.run(repo, work, fake)


def test_run_leftover_container(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(ghost_container=True)
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="leftover-container"):
        fci.run(repo, work, fake)


def test_run_image_absence_query_failure_is_not_absence(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(image_absence="query-failed")
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="image-absence-unverified"):
        fci.run(repo, work, fake)


def test_run_image_still_present_after_rmi(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(image_absence="present")
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="image-still-present"):
        fci.run(repo, work, fake)


def test_run_deadline_expiry_converges_through_cleanup(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(sleep_build=1.5, skip_id_discovery=True)
    repo, work, _ = _setup(tmp_path, monkeypatch, fake, anchor_seconds=1.0)
    with pytest.raises(fci.FixtureError, match="deadline-expired"):
        fci.run(repo, work, fake)
    # The build ran and THEN the deadline expired before the image-id
    # discovery: the id was never registered, but the owned FRESH TAG
    # (verified absent before build, exclusively ours) is inspected
    # under the ONE cleanup grace, the id is recovered through it,
    # and the EXACT removal is attempted and verified.  Leaving a
    # known built image behind is never successful convergence.
    assert fake.built is True
    assert fake.image_removed is True
    assert fake.rmi_calls == [IMAGE_ID]
    recovery_inspect = fake.calls.count(
        ["docker", "inspect", "--format", "{{.Id}}", fci.IMAGE_NAME]
    )
    assert recovery_inspect == 2  # collision check + tag recovery
    assert not work.exists()


def test_run_deadline_expiry_recovery_query_failure_unverified(
    tmp_path: Path, monkeypatch: Any
) -> None:
    fake = FixtureFakeDocker(sleep_build=1.5, skip_id_discovery=True, recovery_mode="query-failed")
    repo, work, _ = _setup(tmp_path, monkeypatch, fake, anchor_seconds=1.0)
    with pytest.raises(
        fci.FixtureError, match="deadline-expired;image-recovery-unverified"
    ) as excinfo:
        fci.run(repo, work, fake)
    # The recovery was ATTEMPTED (the tag inspect through the guard)
    # and its unresolvable outcome is an HONEST recorded failure —
    # never a silent skip, never verified absence.
    assert "image-recovery-unverified" in str(excinfo.value)
    assert fake.image_removed is False
    assert fake.calls.count(["docker", "inspect", "--format", "{{.Id}}", fci.IMAGE_NAME]) == 2
    assert not work.exists()


def test_run_deadline_expiry_recovery_no_image_left(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(sleep_build=1.5, skip_id_discovery=True, recovery_mode="absent")
    repo, work, _ = _setup(tmp_path, monkeypatch, fake, anchor_seconds=1.0)
    with pytest.raises(fci.FixtureError, match="deadline-expired"):
        fci.run(repo, work, fake)
    # The build left no image behind: the tag inspect verified
    # absence, so no removal was attempted and the primary failure
    # (deadline) is the only recorded error.
    assert fake.built is True
    assert fake.image_removed is False
    assert fake.rmi_calls == []


def test_run_build_failure_cleanup_runs_and_no_publish(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(build_rc=1, recovery_mode="absent")
    repo, work, evidence_out = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="build-failed"):
        fci.run(repo, work, fake)
    # Build failed: the build was ATTEMPTED (so the owned tag is
    # inspected under the grace even though it never completed); it
    # left no image (verified absence) and no unowned object was
    # touched; nothing is published.
    assert fake.built is False
    assert fake.image_removed is False
    assert fake.rmi_calls == []
    assert fake.calls.count(["docker", "inspect", "--format", "{{.Id}}", fci.IMAGE_NAME]) == 2
    assert fake.by_name == {}
    assert not evidence_out.exists()
    assert not work.exists()


def test_run_id_query_failure_recovery_unverified(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(
        id_query_rc=1,
        id_query_output=b"Cannot connect to the Docker daemon.\n",
        recovery_mode="query-failed",
    )
    repo, work, evidence_out = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="query-failed;image-recovery-unverified") as excinfo:
        fci.run(repo, work, fake)
    # The primary failure (id discovery query) stays visible AND the
    # recovery attempt's unverified outcome is recorded separately;
    # the run fails closed with no publication.
    assert "image-recovery-unverified" in str(excinfo.value)
    assert fake.image_removed is False
    assert not evidence_out.exists()
    assert not work.exists()


def test_run_rmi_failure_recorded_and_no_publish(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(rmi_rc=1)
    repo, work, evidence_out = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="image-rmi-failed"):
        fci.run(repo, work, fake)
    assert fake.image_removed is False
    assert fake.rmi_calls == [IMAGE_ID]
    # The independent container sweep still ran in full.
    assert set(fake.by_name.values()) == fake.removed
    assert not evidence_out.exists()
    assert not work.exists()


# -- closed stand-in failure reason channel ------------------------------------
# The stand-in's own closed fail token (strict allowlist) may reach
# the runner's closed CI record; unknown/malformed/missing tokens
# stay generic.  Raw output is never propagated.


def _standin_fail_output(reason: str) -> bytes:
    return (
        json.dumps(
            {"record": "slaif-fixture-standin-v1", "status": "fail", "reason": reason},
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode()


def test_standin_fail_reason_allowlist() -> None:
    # Known closed tokens are admitted; the LAST closed fail record
    # wins when several appear.
    assert (
        fci._standin_fail_reason(_standin_fail_output("unlisted-writable-mount"))
        == "unlisted-writable-mount"
    )
    assert (
        fci._standin_fail_reason(
            _standin_fail_output("cpu-mismatch") + _standin_fail_output("swap-missing")
        )
        == "swap-missing"
    )
    # Unknown token: generic.
    assert fci._standin_fail_reason(_standin_fail_output("totally-unknown-token")) is None
    # Malformed / truncated record: generic.
    assert (
        fci._standin_fail_reason(
            b'{"record": "slaif-fixture-standin-v1", "status": "fail", "reason": "cpu-mism'
        )
        is None
    )
    # Another record type (the 21001 controller probe): generic.
    assert (
        fci._standin_fail_reason(
            b'{"record": "slaif-fixture-ctl-probe-v1",'
            b' "status": "fail", "reason": "cpu-mismatch"}\n'
        )
        is None
    )
    # Non-fail status: generic.
    assert (
        fci._standin_fail_reason(
            b'{"record": "slaif-fixture-standin-v1", "status": "pass", "reason": "cpu-mismatch"}\n'
        )
        is None
    )
    # Empty / non-ASCII output: generic.
    assert fci._standin_fail_reason(b"") is None
    assert fci._standin_fail_reason(b"\xff\xfe") is None


def test_run_measure_failure_retains_closed_detail(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(standin_fail=("measure", "unlisted-writable-mount"))
    repo, work, evidence_out = _setup(tmp_path, monkeypatch, fake)
    monkeypatch.setattr(fci, "_STANDIN_DETAIL", None)
    with pytest.raises(fci.FixtureError, match="exec-measurement-failed"):
        fci.run(repo, work, fake)
    # The fixed scenario reason stays primary; the child's closed
    # token is retained separately for the job log.
    assert fci._STANDIN_DETAIL == "unlisted-writable-mount"
    assert not evidence_out.exists()
    assert not work.exists()


def test_run_measure_unknown_token_stays_generic(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(standin_fail=("measure", "totally-unknown-token"))
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    monkeypatch.setattr(fci, "_STANDIN_DETAIL", None)
    with pytest.raises(fci.FixtureError, match="exec-measurement-failed"):
        fci.run(repo, work, fake)
    assert fci._STANDIN_DETAIL is None
    assert not work.exists()


def test_standin_detail_does_not_carry_across_runs(tmp_path: Path, monkeypatch: Any) -> None:
    # First run: the measure child emits a closed fail token.
    fake1 = FixtureFakeDocker(standin_fail=("measure", "unlisted-writable-mount"))
    repo, work, _ = _setup(tmp_path, monkeypatch, fake1)
    monkeypatch.setattr(fci, "_STANDIN_DETAIL", None)
    with pytest.raises(fci.FixtureError, match="exec-measurement-failed"):
        fci.run(repo, work, fake1)
    assert fci._STANDIN_DETAIL == "unlisted-writable-mount"
    # Second run: an unrelated failure with NO stand-in record must
    # NOT inherit the first run's token (per-run scoping, proven
    # without any monkeypatch clear between the runs).
    fake2 = FixtureFakeDocker(build_rc=1)
    with pytest.raises(fci.FixtureError, match="build-failed"):
        fci.run(repo, work, fake2)
    assert fci._STANDIN_DETAIL is None


def test_run_measure_without_closed_record_stays_generic(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker(standin_fail=("measure", None))
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    monkeypatch.setattr(fci, "_STANDIN_DETAIL", None)
    with pytest.raises(fci.FixtureError, match="exec-measurement-failed"):
        fci.run(repo, work, fake)
    assert fci._STANDIN_DETAIL is None
    assert not work.exists()


def test_main_closed_record_includes_standin_detail(monkeypatch: Any, capsys: Any) -> None:
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("RUNNER_ENVIRONMENT", "github-hosted")
    monkeypatch.setattr(fci, "_STANDIN_DETAIL", "cpu-mismatch")

    def boom(repo: Any, work: Any, executor: Any, evidence_out: Any = None) -> Any:
        raise fci.FixtureError("exec-measurement-failed")

    monkeypatch.setattr(fci, "run", boom)
    rc = fci.main(["--repo", ".", "--work", "/nonexistent-work-root-017r"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert out["schema"] == fci.SCHEMA
    assert out["reason"] == "exec-measurement-failed"
    assert out["detail"] == "cpu-mismatch"


def test_main_closed_record_without_detail(monkeypatch: Any, capsys: Any) -> None:
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("RUNNER_ENVIRONMENT", "github-hosted")
    monkeypatch.setattr(fci, "_STANDIN_DETAIL", None)

    def boom(repo: Any, work: Any, executor: Any, evidence_out: Any = None) -> Any:
        raise fci.FixtureError("exec-measurement-failed")

    monkeypatch.setattr(fci, "run", boom)
    rc = fci.main(["--repo", ".", "--work", "/nonexistent-work-root-017r"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert out["reason"] == "exec-measurement-failed"
    assert "detail" not in out


def test_run_setup_failure_no_build_no_image_removal_attempted(
    tmp_path: Path, monkeypatch: Any
) -> None:
    fake = FixtureFakeDocker()
    repo, work, evidence_out = _setup(tmp_path, monkeypatch, fake)
    (repo / "scripts" / "cache_native_fixture.Dockerfile").unlink()
    with pytest.raises(fci.FixtureError, match="dockerfile-missing"):
        fci.run(repo, work, fake)
    # Setup failed BEFORE the build: the build was never attempted,
    # so no image removal is attempted (the pre-build verified
    # absence of the owned tag remains the registered fact).  The
    # dockerfile check runs before ANY docker command, so no docker
    # call ever reached the fake.
    assert fake.built is False
    assert fake.image_removed is False
    assert fake.rmi_calls == []
    assert fake.calls == []
    assert not evidence_out.exists()
    assert not work.exists()


def test_run_foreign_image_never_touched(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker()
    repo, work, evidence_out = _setup(tmp_path, monkeypatch, fake)
    foreign = "slaif-foreign-image:latest"
    fci.run(repo, work, fake, evidence_out=str(evidence_out))
    # No command ever referenced the unowned image (inspect, rm or
    # rmi): cleanup is exact-owned only.
    for call in fake.calls:
        assert foreign not in call
    assert fake.rmi_calls == [IMAGE_ID]


def test_run_low_limit_budget_refuses_overbudget_scenario_before_work(
    tmp_path: Path, monkeypatch: Any
) -> None:
    # max_requests=6: controller-measurement reserves 1 and charges
    # 1 measured; exec/pty reserve 0; synthetic-success reserves 4
    # (total 5 <= 6) and charges 4 measured; synthetic-fail's closed
    # worst case (2) no longer fits (5 + 2 > 6) and is refused
    # BEFORE any of its work reaches the fake receiver.
    original = model.FixtureBudgets

    def low_limit(*args: Any, **kwargs: Any) -> Any:
        kwargs["max_requests"] = 6
        kwargs["max_attempts"] = 6
        return original(*args, **kwargs)

    monkeypatch.setattr(fci.model, "FixtureBudgets", low_limit)
    fake = FixtureFakeDocker()
    repo, work, evidence_out = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match="ledger-request-reserve"):
        fci.run(repo, work, fake)
    # The forbidden scenario's wire work NEVER reached the fake
    # receiver: no fail-mode stand-in exec was ever issued.
    for call in fake.calls:
        assert call[-2:] != ["--mode", "fail"]
    # The successful scenarios before the refusal did run, and the
    # run converges through the full exact-owned cleanup with no
    # publication.
    assert any(call[-2:] == ["--mode", "success"] for call in fake.calls)
    assert set(fake.by_name.values()) == fake.removed
    assert fake.image_removed
    assert not evidence_out.exists()
    assert not work.exists()


@pytest.mark.parametrize(
    "mutate, reason",
    [
        # -- host binding revalidation negatives (the closed-object
        #    proof passes; the host's closed-derivation comparison
        #    catches the violation) --
        (
            lambda p: p["snapshot"]["issued_calls"][0].update(arguments_sha256="f" * 64),
            "export-identity-mismatch",
        ),
        (lambda p: p["snapshot"]["issued_calls"][1].update(position=1), "export-identity-mismatch"),
        (
            lambda p: p["snapshot"]["issued_calls"][0].update(call_id="slaif-syn-" + "e" * 24),
            "export-identity-mismatch",
        ),
        (lambda p: p["snapshot"]["issued_calls"].pop(), "export-identity-mismatch"),
        (
            lambda p: p["snapshot"]["issued_calls"].append(dict(p["snapshot"]["issued_calls"][0])),
            "export-identity-mismatch",
        ),
        # the stand-in observed issuance disagrees with the closed
        # derivation (the fake's success stand-in record is re-derived
        # from the same closed tools, so a drifted snapshot is caught by
        # the host comparison, not echoed)
        (
            lambda p: p.update(diagnostic={"state": "unobserved"}, observed_at_position=None),
            "export-identity-mismatch",
        ),
        (lambda p: p.update(observed_at_position=7), "export-identity-mismatch"),
        # -- trusted-controller reconciliation negative: the exported
        #    controller ledger does not agree with the measured client
        #    facts --
        (
            lambda p: p["snapshot"]["controller_ledger"].update(requests=3),
            "controller-ledger-mismatch",
        ),
        # -- closed-object proof negatives (fail inside the model
        #    validators, mapped to the fixed host failure) --
        (lambda p: p["snapshot"]["issued_calls"][0].update(family="other"), "export-invalid"),
        (lambda p: p["snapshot"].pop("controller_ledger"), "export-invalid"),
        (lambda p: p["snapshot"]["controller_ledger"].update(extra=1), "export-invalid"),
    ],
)
def test_run_binding_violations_refused_without_publication(
    mutate: Any, reason: Any, tmp_path: Path, monkeypatch: Any
) -> None:
    fake = FixtureFakeDocker(export_mutate=mutate)
    repo, work, evidence_out = _setup(tmp_path, monkeypatch, fake)
    with pytest.raises(fci.FixtureError, match=reason):
        fci.run(repo, work, fake)
    # Failed runs publish nothing, and the exact-owned sweep still
    # covered every registered container and the image.
    assert not evidence_out.exists()
    assert not work.exists()
    assert set(fake.by_name.values()) == fake.removed
    assert fake.image_removed


def test_run_publication_only_after_verified_teardown_order(
    tmp_path: Path, monkeypatch: Any
) -> None:
    fake = FixtureFakeDocker()
    repo, work, evidence_out = _setup(tmp_path, monkeypatch, fake)
    result = fci.run(repo, work, fake, evidence_out=str(evidence_out))
    # Publication order: EVERY owned container removal completed,
    # then the post-teardown leftover verification (ancestor filter
    # over the exact built image) ran, and only THEN the image
    # removal (the cleanup umbrella) and the evidence publication —
    # the exact closed phase order, all proven by the recorded
    # command sequence.
    rmi_index = fake.calls.index(["docker", "rmi", IMAGE_ID])
    verify_index = fake.calls.index(
        ["docker", "ps", "-aq", "--filter", f"ancestor={fci.IMAGE_NAME}"]
    )
    rm_indexes = [i for i, call in enumerate(fake.calls) if call[1] == "rm"]
    assert rm_indexes, "no container removal was attempted"
    assert max(rm_indexes) < verify_index < rmi_index
    assert result["publish"]["artifact_sha256"] == result["summary"]["export_sha256"]
    assert (
        hashlib.sha256(evidence_out.read_bytes()).hexdigest()
        == result["publish"]["artifact_sha256"]
    )


def test_run_ledger_admission_cap(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker()
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    monkeypatch.setattr(fci._RunLedger, "MAX_HOST_ADMISSIONS", 5)
    with pytest.raises(fci.FixtureError, match="ledger-admission-cap"):
        fci.run(repo, work, fake)


def test_run_dockerfile_missing(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker()
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    (repo / "scripts" / "cache_native_fixture.Dockerfile").unlink()
    with pytest.raises(fci.FixtureError, match="dockerfile-missing"):
        fci.run(repo, work, fake)


def test_static_no_codex_workflow_job(tmp_path: Path, monkeypatch: Any) -> None:
    fake = FixtureFakeDocker()
    repo, work, _ = _setup(tmp_path, monkeypatch, fake)
    yml_path = repo / ".github" / "workflows" / "ci.yml"
    yml_path.write_text(
        yml_path.read_text() + "\n  cache-native-fixture:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - name: bad\n"
        "        run: echo codex --help\n"
    )
    with pytest.raises(fci.FixtureError, match="codex-invocation-static"):
        fci.run(repo, work, fake)


# -- owned PTY seam (real local pty, no docker) --------------------------------


def test_pty_seam_real_tty_properties_and_fd_cleanup() -> None:
    script = (
        "import sys,fcntl,termios,struct,os\n"
        "rows,cols,_,_ = struct.unpack('HHHH',fcntl.ioctl(0,"
        "termios.TIOCGWINSZ,b'\\x00'*8))\n"
        "print('tty=%s rows=%d cols=%d name=%s' % "
        "(sys.stdin.isatty(), rows, cols, os.ttyname(0)))\n"
    )
    before = len(os.listdir("/proc/self/fd"))
    result = fci._real_execute([sys.executable, "-c", script], 15.0, pty=True)
    after = len(os.listdir("/proc/self/fd"))
    assert result.returncode == 0
    text = result.output.decode("ascii")
    assert text.startswith(f"tty=True rows={fci.PTY_ROWS} cols={fci.PTY_COLS} name=/dev/pts/")
    assert result.drained_bytes == len(result.output)
    assert after <= before  # the owned master fd was closed


def test_pty_seam_auto_detects_docker_exec_it(tmp_path: Path, monkeypatch: Any) -> None:
    shim = tmp_path / "shim"
    shim.mkdir()
    (shim / "docker").write_text(
        "#!/usr/bin/env python3\n"
        "import sys,fcntl,termios,struct\n"
        "try:\n"
        "    rows,cols,_,_ = struct.unpack('HHHH',fcntl.ioctl(0,"
        "termios.TIOCGWINSZ,b'\\x00'*8))\n"
        "except Exception:\n"
        "    rows=cols=0\n"
        "print('tty=%s rows=%d cols=%d' % "
        "(sys.stdin.isatty(), rows, cols))\n"
    )
    (shim / "docker").chmod(0o755)
    monkeypatch.setenv("PATH", str(shim) + os.pathsep + os.environ["PATH"])
    argv = [
        "docker",
        "exec",
        "-it",
        "--user",
        f"{fci.SUBJECT_UID}:{fci.SUBJECT_UID}",
        CID,
        "python3",
        fci.STANDIN_PATH,
        "--mode",
        "pty",
    ]
    result = fci._real_execute(argv, 15.0)
    assert result.output.decode("ascii").startswith(
        f"tty=True rows={fci.PTY_ROWS} cols={fci.PTY_COLS}"
    )


def test_pty_seam_pipe_path_not_used_without_it() -> None:
    result = fci._real_execute([sys.executable, "-c", "import sys;print(sys.stdin.isatty())"], 15.0)
    assert result.output.decode("ascii").strip() == "False"


def test_pty_seam_timeout_bounded_partial_and_cleanup() -> None:
    before = len(os.listdir("/proc/self/fd"))
    with pytest.raises(fci._OwnedTimeout) as excinfo:
        fci._real_execute([sys.executable, "-c", "import time; time.sleep(10)"], 0.5, pty=True)
    after = len(os.listdir("/proc/self/fd"))
    assert isinstance(excinfo.value.partial_output, bytes)
    assert after <= before  # the owned master fd was closed


# -- entry guard ----------------------------------------------------------------


def test_main_refuses_non_ci_context(tmp_path: Path, monkeypatch: Any, capsys: Any) -> None:
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("RUNNER_ENVIRONMENT", raising=False)
    rc = fci.main(["--repo", str(tmp_path), "--work", str(tmp_path / "w")])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert out["reason"] == "not-a-disposable-ci-runner"


def test_main_refuses_non_hosted_ci_context(tmp_path: Path, monkeypatch: Any, capsys: Any) -> None:
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.delenv("RUNNER_ENVIRONMENT", raising=False)
    rc = fci.main(["--repo", str(tmp_path), "--work", str(tmp_path / "w")])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert out["reason"] == "not-a-hosted-ci-runner"


# -- actual controller + stand-in wire accounting (real loopback
#    sockets, pure Python; no Docker, no namespace, no native
#    binary) ------------------------------------------------------------
# The host ledger scopes are checked against the ACTUAL controller
# ledger and the stand-in's measured closed records, not a scripted
# echo: a refused or malformed call is a request with a refused
# outcome, and the diagnostic observation/position must be the
# controller's own measured facts.


def _start_provider(tmp_path: Path, scenario: str) -> Any:
    ledger = model.FixtureLedger()
    ledger.set_deadline(300.0)
    registry = model.IssuedRegistry(ledger.budgets.max_requests)
    provider = fci.fixture_controller.Provider(
        0,
        ledger,
        registry,
        threading.Lock(),
        scenario=scenario,
        originals_dir=str(tmp_path / "originals"),
        exporter_uid=fci.CONTROLLER_UID,
    )
    provider.seed_originals()
    thread = threading.Thread(target=provider.serve, daemon=True)
    provider.accept_thread = thread
    thread.start()
    return ledger, registry, provider, thread


def _stop_provider(provider: Any, thread: Any) -> None:
    provider.closed = True
    thread.join(timeout=10)


def _standin_wire_env(monkeypatch: Any, port: int) -> None:
    monkeypatch.setenv("SLAIF_FIXTURE_PORT", str(port))
    monkeypatch.setenv("SLAIF_FIXTURE_DEADLINE_ABS", repr(time.monotonic() + 30.0))


def _raw_post(port: int, body: bytes) -> tuple[int | None, bytes]:
    request = (
        b"POST /v1/responses HTTP/1.1\r\n"
        b"Host: 127.0.0.1\r\n"
        b"Content-Type: application/json\r\n"
        + f"Content-Length: {len(body)}\r\n".encode()
        + b"\r\n"
        + body
    )
    sock = socket.create_connection(("127.0.0.1", port), timeout=5.0)
    try:
        sock.sendall(request)
        data = b""
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            data += chunk
    finally:
        sock.close()
    if b"\r\n\r\n" not in data:
        return None, data
    head, _, body_out = data.partition(b"\r\n\r\n")
    status = int(head.split(b" ", 2)[1])
    return status, body_out


def test_wire_refused_post_is_a_request_both_ledgers_agree(
    tmp_path: Path, monkeypatch: Any, capsys: Any
) -> None:
    ledger, registry, provider, thread = _start_provider(tmp_path, "tool-cycle")
    try:
        _standin_wire_env(monkeypatch, provider.port)
        rc = fci.fixture_standin.fail_mode()
        assert rc == 3
        record = json.loads(capsys.readouterr().out)
        assert record["status"] == "pass"
        assert record["mode"] == "fail"
        assert record["provider_state"] == "unissued"
        assert record["raw_content_retained"] is False
        # The stand-in's MEASURED client-side split: the issuance
        # POST answered 200 (admitted), the foreign-result POST
        # answered 400 slaif_fixture_unissued (refused) — a refused
        # call IS a request.
        assert record["requests"] == 1
        assert record["attempts"] == 2
        host = fci._RunLedger(model.FixtureBudgets())
        host.charge_http(
            record["attempts"],
            record["attempts"],
            record["requests"],
            record["attempts"] - record["requests"],
        )
        # The ACTUAL controller ledger (trusted observation, read
        # from the running provider) agrees: record_request ran for
        # BOTH POSTs before routing, so its request count equals the
        # host's api_requests for the scenario.
        assert ledger.requests == host.api_requests == 2
        assert host.api_attempts == 2
        assert host.requests_admitted == 1
        assert host.requests_refused == 1
        # The scenario state advanced only to awaiting-results; the
        # refused result never advanced it, and the exact-issued
        # registry holds the two issued calls.
        assert provider.scenario_state == "awaiting-results"
        assert len(registry.entries()) == 2
    finally:
        _stop_provider(provider, thread)


def test_wire_diagnostic_observation_is_measured(
    tmp_path: Path, monkeypatch: Any, capsys: Any
) -> None:
    ledger, registry, provider, thread = _start_provider(tmp_path, "diagnostic")
    try:
        _standin_wire_env(monkeypatch, provider.port)
        rc = fci.fixture_standin.diagnostic_mode()
        assert rc == 0
        record = json.loads(capsys.readouterr().out)
        assert record["status"] == "pass"
        assert record["mode"] == "diagnostic"
        assert record["requests"] == 1
        assert record["attempts"] == 1
        assert record["response_kind"] == "fixed-final-text-no-tools"
        # One actual POST: the controller counted exactly one
        # request, the metadata diagnostic was MEASURED from the
        # actual request's tools region, and the observation bound
        # to the first admitted request position (0).
        assert ledger.requests == 1
        # The diagnostic POST carries the closed NO-TOOLS request,
        # so the observed metadata diagnostic is the measurement of
        # an empty tools region (never the synthetic tools set).
        expected = fci.fixture_standin._fixed_request([])
        assert provider.diagnostic == model.bounds_diagnostic(expected)
        assert provider.observed_at_position == 0
        assert provider.scenario_state == "done"
        assert registry.count() == 0
        host = fci._RunLedger(model.FixtureBudgets())
        host.charge_http(record["attempts"], record["attempts"], record["requests"], 0)
        assert host.api_requests == ledger.requests
    finally:
        _stop_provider(provider, thread)


def test_wire_malformed_body_fixed_refusal_still_a_request(tmp_path: Path) -> None:
    ledger, registry, provider, thread = _start_provider(tmp_path, "tool-cycle")
    try:
        status, body = _raw_post(provider.port, b"not-json{")
        assert status == 400
        parsed = json.loads(body.decode("ascii"))
        assert parsed["error"]["code"] == "malformed-request"
        # The malformed POST still consumed a request position
        # (record_request before parsing): the fixed refusal is a
        # request with a refused outcome, and NOTHING advanced —
        # no issuance, no scenario progress.
        assert ledger.requests == 1
        assert registry.count() == 0
        assert provider.scenario_state == "awaiting-issue"
        host = fci._RunLedger(model.FixtureBudgets())
        host.charge_http(1, 1, 0, 1)
        assert host.api_requests == ledger.requests
        assert host.requests_admitted == 0
        assert host.requests_refused == 1
    finally:
        _stop_provider(provider, thread)


# -- review 15: /proc scan bound (no silent truncation) -----------------------


def _no_exec() -> Any:
    def executor(argv: Any, timeout: Any) -> NoReturn:
        raise AssertionError("no host command may run on this path")

    return executor


def test_proc_scan_one_over_bound_rejects_both_counts(monkeypatch: Any) -> None:
    # 20001 entries exceed the closed scan bound: the listing is
    # incomplete as far as the bound goes, so presence/absence may
    # not be claimed — rejected, never truncated into a false zero.
    entries = [str(i) for i in range(1, 20002)]
    monkeypatch.setattr(fci.os, "listdir", lambda path: entries)
    with pytest.raises(fci.FixtureError, match="proc-scan-oversized"):
        fci._count_uid_marker_processes(21002, "owned-token")
    with pytest.raises(fci.FixtureError, match="proc-scan-oversized"):
        fci._count_fixture_uid_processes(21002)


def _fake_proc_open(uids: dict[int, int], cmdlines: dict[int, bytes]) -> Any:
    def fake_open(filename: Any, *args: Any, **kwargs: Any) -> Any:
        pid = int(str(filename).split("/")[2])
        if str(filename).endswith("/status"):
            return io.StringIO(f"Uid:\t{uids[pid]}\n")
        if str(filename).endswith("/cmdline"):
            return io.BytesIO(cmdlines[pid])
        raise AssertionError(f"unexpected fake file: {filename}")

    return fake_open


def test_proc_scan_complete_listing_counts_exact_match(monkeypatch: Any) -> None:
    monkeypatch.setattr(fci.os, "listdir", lambda path: ["1", "2"])
    monkeypatch.setattr(
        "builtins.open",
        _fake_proc_open({1: 1000, 2: 21002}, {1: b"python unrelated", 2: b"python owned-token"}),
    )
    assert fci._count_uid_marker_processes(21002, "owned-token") == 1
    assert fci._count_fixture_uid_processes(21002) == 1


def test_proc_scan_vanished_entry_is_expected_churn(monkeypatch: Any) -> None:
    monkeypatch.setattr(fci.os, "listdir", lambda path: ["1", "2"])
    base = _fake_proc_open({1: 1000, 2: 21002}, {1: b"python x", 2: b"python owned-token"})

    def fake_open(filename: Any, *args: Any, **kwargs: Any) -> Any:
        if str(filename).endswith("1/status"):
            raise FileNotFoundError("vanished between listdir and read")
        return base(filename, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)
    assert fci._count_uid_marker_processes(21002, "owned-token") == 1
    assert fci._count_fixture_uid_processes(21002) == 1


# -- review 15: timed-out captures are charged the drained total --------------


def test_guarded_timeout_charges_drained_total_once() -> None:
    ledger = fci._RunLedger(model.FixtureBudgets())
    deadline = fci._RunDeadline(time.monotonic() + 60.0)
    timeout = fci._OwnedTimeout(["docker", "ps", "-aq"], 1.0, b"x" * 10, 1000)

    def fake_executor(argv: Any, timeout_seconds: Any) -> NoReturn:
        raise timeout

    guarded = fci._guarded_execute(fake_executor, deadline, ledger)
    argv = ["docker", "ps", "-aq", "--filter", "id=" + CID]
    with pytest.raises(fci._OwnedTimeout):
        guarded(argv, 1.0)
    # Exactly ONE charge of the measured drained total (retained +
    # discarded) and the bounded retained partial: a hang emitting
    # substantial discarded output can never skip the non-resettable
    # output budget, and the timeout is not double-charged.
    assert ledger.bytes_drained == 1000
    assert ledger.bytes_retained == 10
    assert ledger.admissions == 1
    assert ledger.refusals == 0


def test_guarded_timeout_over_output_cap_fails_closed() -> None:
    budgets = model.FixtureBudgets(output_cap_bytes=16)
    ledger = fci._RunLedger(budgets)
    deadline = fci._RunDeadline(time.monotonic() + 60.0)
    timeout = fci._OwnedTimeout(["docker", "ps", "-aq"], 1.0, b"x" * 10, 1000)

    def fake_executor(argv: Any, timeout_seconds: Any) -> NoReturn:
        raise timeout

    guarded = fci._guarded_execute(fake_executor, deadline, ledger)
    argv = ["docker", "ps", "-aq", "--filter", "id=" + CID]
    with pytest.raises(fci.FixtureError, match="ledger-output-cap"):
        guarded(argv, 1.0)


# -- review 16: public artifact preparation against the real helpers ---------


def _make_archive(members: list[tuple[str, bytes, dict[str, Any]]]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for name, data, extra in members:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.type = extra.get("type", tarfile.REGTYPE)
            info.linkname = extra.get("linkname", "")
            tar.addfile(info, io.BytesIO(data) if info.type == tarfile.REGTYPE else None)
    raw = buf.getvalue()
    gz = io.BytesIO()
    with gzip.GzipFile(fileobj=gz, mode="wb", mtime=0) as handle:
        handle.write(raw)
    return gz.getvalue()


LICENSE_FAKE = b"Apache License\nVersion 2.0, January 2004 (fake for pure tests)\n"
NOTICE_FAKE = b"fake pinned NOTICE: Ratatui derived, MIT license\n"
BINARY_FAKE = b"slaif-synthetic-native-binary"


class _FakeResponse:
    def __init__(self, data: bytes, flags: list[list[bool]]) -> None:
        self._buf = io.BytesIO(data)
        self._flag = [False]
        flags.append(self._flag)

    def read(self, n: int) -> bytes:
        return self._buf.read(n)

    def close(self) -> None:
        self._flag[0] = True


class _FakeHTTP:
    def __init__(self, routes: dict[str, bytes | Exception]) -> None:
        self.routes = routes
        self.flags: list[list[bool]] = []

    def urlopen(self, request: Any, timeout: Any = None) -> _FakeResponse:
        url = str(getattr(request, "full_url", request))
        for suffix, payload in self.routes.items():
            if url.endswith(suffix):
                if isinstance(payload, Exception):
                    raise payload
                return _FakeResponse(payload, self.flags)
        raise AssertionError(f"unrouted URL: {url}")


def _artifact_env(
    monkeypatch: Any,
    *,
    archive: bytes | None = None,
    license: bytes = LICENSE_FAKE,
    notice: bytes = NOTICE_FAKE,
    expected_size: int | None = None,
    expected_sha: str | None = None,
    max_bytes: int | None = None,
    license_cap: int | None = None,
    license_sha: str | None = None,
    notice_sha: str | None = None,
) -> _FakeHTTP:
    if archive is None:
        archive = _make_archive([(model.ARTIFACT_BINARY_NAME, BINARY_FAKE, {})])
    http = _FakeHTTP(
        {
            "/codex-x86_64-unknown-linux-musl.tar.gz": archive,
            "/LICENSE": license,
            "/NOTICE": notice,
        }
    )
    monkeypatch.setattr(fci.urllib.request, "urlopen", http.urlopen)
    monkeypatch.setattr(
        model, "ARTIFACT_ARCHIVE_SIZE", expected_size if expected_size is not None else len(archive)
    )
    monkeypatch.setattr(
        model,
        "ARTIFACT_ARCHIVE_SHA256",
        expected_sha if expected_sha is not None else hashlib.sha256(archive).hexdigest(),
    )
    if max_bytes is not None:
        monkeypatch.setattr(model, "ARTIFACT_BINARY_MAX_BYTES", max_bytes)
    if license_cap is not None:
        monkeypatch.setattr(fci, "_LICENSE_CAP", license_cap)
    monkeypatch.setattr(
        model,
        "ARTIFACT_LICENSE_SHA256",
        license_sha if license_sha is not None else hashlib.sha256(license).hexdigest(),
    )
    monkeypatch.setattr(
        model,
        "ARTIFACT_NOTICE_SHA256",
        notice_sha if notice_sha is not None else hashlib.sha256(notice).hexdigest(),
    )
    return http


def _deadline() -> Any:
    return fci._RunDeadline(time.monotonic() + 60.0)


def test_artifact_fetch_extract_verify_real_helpers(monkeypatch: Any, tmp_path: Path) -> None:
    http = _artifact_env(monkeypatch)
    dest = tmp_path / "artifact"
    dest.mkdir()
    result = fci.fetch_public_artifact(dest, _deadline())
    assert result["binary_sha256"] == hashlib.sha256(BINARY_FAKE).hexdigest()
    assert result["binary_size"] == len(BINARY_FAKE)
    assert result["license_sha256"] == hashlib.sha256(LICENSE_FAKE).hexdigest()
    assert result["notice_sha256"] == hashlib.sha256(NOTICE_FAKE).hexdigest()
    assert (dest / "LICENSE").read_bytes() == LICENSE_FAKE
    assert (dest / "NOTICE").read_bytes() == NOTICE_FAKE
    assert (dest / model.ARTIFACT_BINARY_NAME).read_bytes() == BINARY_FAKE
    # EVERY owned response handle was closed (success path).
    assert http.flags and all(flag[0] for flag in http.flags)


def test_artifact_digest_failure_writes_nothing_and_closes(
    monkeypatch: Any, tmp_path: Path
) -> None:
    http = _artifact_env(monkeypatch, expected_sha="0" * 64)
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="archive-digest"):
        fci.fetch_public_artifact(dest, _deadline())
    assert not (dest / model.ARTIFACT_BINARY_NAME).exists()
    assert not (dest / "LICENSE").exists()
    assert not (dest / "NOTICE").exists()
    assert all(flag[0] for flag in http.flags)


def test_artifact_empty_archive_typed_shape_failure(monkeypatch: Any, tmp_path: Path) -> None:
    _artifact_env(monkeypatch, archive=_make_archive([]))
    dest = tmp_path / "artifact"
    dest.mkdir()
    # Exactly one member is required BEFORE any filesystem fact is
    # read: an empty archive is a typed closed-shape failure, never
    # a leaked lstat exception on the never-created binary path.
    with pytest.raises(fci.FixtureError, match="archive-shape"):
        fci.fetch_public_artifact(dest, _deadline())
    assert not (dest / model.ARTIFACT_BINARY_NAME).exists()


def test_artifact_wrong_name_member_rejected(monkeypatch: Any, tmp_path: Path) -> None:
    _artifact_env(monkeypatch, archive=_make_archive([("other-name", BINARY_FAKE, {})]))
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="archive-shape"):
        fci.fetch_public_artifact(dest, _deadline())


def test_artifact_extra_member_rejected(monkeypatch: Any, tmp_path: Path) -> None:
    _artifact_env(
        monkeypatch,
        archive=_make_archive(
            [(model.ARTIFACT_BINARY_NAME, BINARY_FAKE, {}), ("extra.txt", b"extra", {})]
        ),
    )
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="archive-shape"):
        fci.fetch_public_artifact(dest, _deadline())


def test_artifact_duplicate_member_rejected(monkeypatch: Any, tmp_path: Path) -> None:
    _artifact_env(
        monkeypatch,
        archive=_make_archive(
            [
                (model.ARTIFACT_BINARY_NAME, BINARY_FAKE, {}),
                (model.ARTIFACT_BINARY_NAME, b"other", {}),
            ]
        ),
    )
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="archive-shape"):
        fci.fetch_public_artifact(dest, _deadline())


def test_artifact_symlink_member_rejected(monkeypatch: Any, tmp_path: Path) -> None:
    _artifact_env(
        monkeypatch,
        archive=_make_archive(
            [
                (
                    model.ARTIFACT_BINARY_NAME,
                    b"",
                    {"type": tarfile.SYMTYPE, "linkname": "/etc/passwd"},
                )
            ]
        ),
    )
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="archive-shape"):
        fci.fetch_public_artifact(dest, _deadline())


def test_artifact_hardlink_member_rejected(monkeypatch: Any, tmp_path: Path) -> None:
    _artifact_env(
        monkeypatch,
        archive=_make_archive(
            [
                (
                    model.ARTIFACT_BINARY_NAME,
                    b"",
                    {"type": tarfile.LNKTYPE, "linkname": model.ARTIFACT_BINARY_NAME},
                )
            ]
        ),
    )
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="archive-shape"):
        fci.fetch_public_artifact(dest, _deadline())


def test_artifact_path_escape_member_rejected(monkeypatch: Any, tmp_path: Path) -> None:
    _artifact_env(monkeypatch, archive=_make_archive([("sub/../../evil", BINARY_FAKE, {})]))
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="archive-shape"):
        fci.fetch_public_artifact(dest, _deadline())
    assert not (tmp_path / "evil").exists()


def test_artifact_stream_size_mismatch_rejected(monkeypatch: Any, tmp_path: Path) -> None:
    archive = _make_archive([(model.ARTIFACT_BINARY_NAME, BINARY_FAKE, {})])
    _artifact_env(monkeypatch, archive=archive, expected_size=len(archive) + 5)
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="archive-size"):
        fci.fetch_public_artifact(dest, _deadline())


def test_artifact_stream_oversize_rejected(monkeypatch: Any, tmp_path: Path) -> None:
    archive = _make_archive([(model.ARTIFACT_BINARY_NAME, BINARY_FAKE, {})])
    _artifact_env(monkeypatch, archive=archive, expected_size=8)
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="archive-oversize"):
        fci.fetch_public_artifact(dest, _deadline())


def test_artifact_decompressed_oversize_rejected(monkeypatch: Any, tmp_path: Path) -> None:
    _artifact_env(monkeypatch, max_bytes=16)  # BINARY_FAKE is 31 bytes
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="binary-oversize"):
        fci.fetch_public_artifact(dest, _deadline())
    # No byte beyond the cap is ever written: the partial (if the
    # file object was created) is bounded by the cap.
    partial = dest / model.ARTIFACT_BINARY_NAME
    assert not partial.exists() or partial.stat().st_size <= 16


def test_artifact_license_oversize_rejected(monkeypatch: Any, tmp_path: Path) -> None:
    _artifact_env(monkeypatch, license_cap=4)
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="license-oversize"):
        fci.fetch_public_artifact(dest, _deadline())
    assert not (dest / "LICENSE").exists()


def test_artifact_license_digest_mismatch_rejected(monkeypatch: Any, tmp_path: Path) -> None:
    _artifact_env(monkeypatch, license_sha="0" * 64)
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="license-identity"):
        fci.fetch_public_artifact(dest, _deadline())
    assert not (dest / "LICENSE").exists()


def test_artifact_notice_digest_mismatch_rejected(monkeypatch: Any, tmp_path: Path) -> None:
    _artifact_env(monkeypatch, notice_sha="0" * 64)
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="notice-identity"):
        fci.fetch_public_artifact(dest, _deadline())
    assert not (dest / "NOTICE").exists()


def test_artifact_notice_empty_rejected(monkeypatch: Any, tmp_path: Path) -> None:
    _artifact_env(monkeypatch, notice=b"")
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="notice-shape"):
        fci.fetch_public_artifact(dest, _deadline())
    assert not (dest / "NOTICE").exists()


def test_artifact_fetch_failure_fixed_reason_and_closed(monkeypatch: Any, tmp_path: Path) -> None:
    archive = _make_archive([(model.ARTIFACT_BINARY_NAME, BINARY_FAKE, {})])
    http = _FakeHTTP(
        {
            "/codex-x86_64-unknown-linux-musl.tar.gz": OSError("injected network failure"),
            "/LICENSE": LICENSE_FAKE,
            "/NOTICE": NOTICE_FAKE,
        }
    )
    monkeypatch.setattr(fci.urllib.request, "urlopen", http.urlopen)
    monkeypatch.setattr(model, "ARTIFACT_ARCHIVE_SIZE", len(archive))
    monkeypatch.setattr(model, "ARTIFACT_ARCHIVE_SHA256", hashlib.sha256(archive).hexdigest())
    dest = tmp_path / "artifact"
    dest.mkdir()
    with pytest.raises(fci.FixtureError, match="archive-fetch-failed"):
        fci.fetch_public_artifact(dest, _deadline())


# -- review 16: early preparation under the cleanup umbrella ------------------


def test_early_fetch_failure_destroys_owned_work_root(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _make_repo(tmp_path)
    work = tmp_path / "work"

    def boom(dest_dir: Any, deadline: Any) -> NoReturn:
        raise fci.FixtureError("archive-digest")

    monkeypatch.setattr(fci, "fetch_public_artifact", boom)
    with pytest.raises(fci.FixtureError, match="^archive-digest$"):
        fci.run(repo, work, _no_exec())
    # The newly owned scratch root is destroyed by the umbrella even
    # on an EARLY preparation failure (never leaked).
    assert not os.path.lexists(str(work))


def test_context_copy_mismatch_destroys_owned_work_root(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _make_repo(tmp_path)
    work = tmp_path / "work"
    monkeypatch.setattr(fci, "fetch_public_artifact", _fake_fetch)
    monkeypatch.setattr(fci, "sha256_file", lambda path: "0" * 64)
    with pytest.raises(fci.FixtureError, match="context-mismatch"):
        fci.run(repo, work, _no_exec())
    assert not os.path.lexists(str(work))


def test_work_cleanup_failure_exposed_with_primary_preserved(
    tmp_path: Path, monkeypatch: Any
) -> None:
    repo = _make_repo(tmp_path)
    work = tmp_path / "work"

    def boom(dest_dir: Any, deadline: Any) -> NoReturn:
        raise fci.FixtureError("archive-digest")

    monkeypatch.setattr(fci, "fetch_public_artifact", boom)
    monkeypatch.setattr(fci, "_destroy_owned_work_root", lambda target: False)
    with pytest.raises(fci.FixtureError) as excinfo:
        fci.run(repo, work, _no_exec())
    # The primary failure is PRESERVED (never replaced) and the
    # failed verified destruction is exposed honestly on it.
    assert str(excinfo.value).startswith("archive-digest")
    assert "work-cleanup-failed" in str(excinfo.value)
    assert os.path.lexists(str(work))  # destruction actually failed


# -- review 17: protected atomic evidence publication --------------------------

EVIDENCE_PAYLOAD = b"slaif-selected-evidence-payload"
EVIDENCE_DIGEST = hashlib.sha256(EVIDENCE_PAYLOAD).hexdigest()


def _no_tmp_left(parent: Path) -> None:
    assert parent.is_dir()
    assert not [p for p in parent.iterdir() if p.name.startswith("selected-evidence.json.tmp-")]


def test_retain_evidence_atomic_success_modes_and_bytes(tmp_path: Path) -> None:
    work = tmp_path / "work-root"
    dest = tmp_path / "out" / "evidence" / "selected-evidence.json"
    result = fci._retain_evidence(dest, EVIDENCE_PAYLOAD, EVIDENCE_DIGEST, work)
    assert result == str(dest)
    assert dest.read_bytes() == EVIDENCE_PAYLOAD
    assert stat.S_IMODE(dest.lstat().st_mode) == 0o600
    assert stat.S_IMODE(dest.parent.lstat().st_mode) == 0o700
    assert dest.parent.lstat().st_uid == os.getuid()
    _no_tmp_left(dest.parent)


def test_retain_evidence_existing_destination_refused(tmp_path: Path) -> None:
    work = tmp_path / "work-root"
    dest = tmp_path / "out" / "selected-evidence.json"
    dest.parent.mkdir()
    dest.write_bytes(b"pre-existing bytes")
    with pytest.raises(fci.FixtureError, match="evidence-exists"):
        fci._retain_evidence(dest, EVIDENCE_PAYLOAD, EVIDENCE_DIGEST, work)
    assert dest.read_bytes() == b"pre-existing bytes"  # never overwritten
    _no_tmp_left(dest.parent)


def test_retain_evidence_inside_work_refused(tmp_path: Path) -> None:
    work = tmp_path / "work-root"
    work.mkdir()
    dest = work / "selected-evidence.json"
    with pytest.raises(fci.FixtureError, match="evidence-inside-work"):
        fci._retain_evidence(dest, EVIDENCE_PAYLOAD, EVIDENCE_DIGEST, work)
    assert not dest.exists()


def test_retain_evidence_symlinked_ancestor_refused(tmp_path: Path) -> None:
    work = tmp_path / "work-root"
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    os.symlink(real, link)
    dest = link / "selected-evidence.json"
    with pytest.raises(fci.FixtureError, match="evidence-path-untrusted"):
        fci._retain_evidence(dest, EVIDENCE_PAYLOAD, EVIDENCE_DIGEST, work)
    assert not (real / "selected-evidence.json").exists()


def test_retain_evidence_foreign_owned_ancestry_refused(tmp_path: Path, monkeypatch: Any) -> None:
    # Simulated foreign uid: the real-uid pytest ancestry is then an
    # arbitrary FOREIGN (non-root) owner — never trusted (owner-
    # write could rename/swap the protected leaf), so the refusal
    # fires at the first foreign ancestor, before the immediate-
    # parent check.
    work = tmp_path / "work-root"
    parent = tmp_path / "out"
    parent.mkdir()
    real_uid = os.getuid()
    monkeypatch.setattr(fci.os, "getuid", lambda: real_uid + 7)
    dest = parent / "selected-evidence.json"
    with pytest.raises(fci.FixtureError, match="evidence-ancestor-untrusted"):
        fci._retain_evidence(dest, EVIDENCE_PAYLOAD, EVIDENCE_DIGEST, work)
    _no_tmp_left(parent)


def test_retain_evidence_current_uid_0755_traversal_ancestor_admitted(
    tmp_path: Path,
) -> None:
    # Current-uid ordinary traversal ancestry (0755, not
    # group/other-writable) is admitted — 0700 is demanded only on
    # the private leaf and on state created by this invocation.
    work = tmp_path / "work-root"
    home = tmp_path / "home755"
    home.mkdir()
    os.chmod(home, 0o755)
    dest = home / "evidence-dir" / "selected-evidence.json"
    result = fci._retain_evidence(dest, EVIDENCE_PAYLOAD, EVIDENCE_DIGEST, work)
    assert result == str(dest)
    assert stat.S_IMODE(dest.lstat().st_mode) == 0o600
    assert stat.S_IMODE(dest.parent.lstat().st_mode) == 0o700
    _no_tmp_left(dest.parent)


@pytest.mark.parametrize("mode", [0o775, 0o777, 0o755 | stat.S_IWGRP])
def test_retain_evidence_current_uid_writable_ancestor_refused(tmp_path: Path, mode: Any) -> None:
    # A current-uid ancestor that is group/other-writable is
    # untrusted (group members could rename/swap the protected
    # leaf): refused, nothing written.
    work = tmp_path / "work-root"
    bad = tmp_path / "writable755"
    bad.mkdir()
    os.chmod(bad, mode)
    dest = bad / "selected-evidence.json"
    with pytest.raises(fci.FixtureError, match="evidence-ancestor-untrusted"):
        fci._retain_evidence(dest, EVIDENCE_PAYLOAD, EVIDENCE_DIGEST, work)
    assert not dest.exists()


@pytest.mark.parametrize(
    "mode,owner,self_uid,trusted",
    [
        # current-uid traversal ancestry
        (0o755, 1000, 1000, True),
        (0o700, 1000, 1000, True),
        (0o775, 1000, 1000, False),  # current-uid group-writable
        (0o777, 1000, 1000, False),  # current-uid world-writable
        (0o644, 1000, 1000, False),  # current-uid non-traversable
        # root-owned explicitly trusted system ancestry
        (0o755, 0, 1000, True),  # /, /home, /usr
        (0o1777, 0, 1000, True),  # /tmp: sticky shared temp
        (0o1755, 0, 1000, True),  # sticky, no writable classes
        (0o777, 0, 1000, False),  # root world-writable sticky-less
        (0o775, 0, 1000, False),  # root group-writable sticky-less
        (0o700, 0, 1000, False),  # root-owned, other cannot traverse
        # arbitrary foreign (non-root) owners are never trusted
        (0o755, 1001, 1000, False),  # foreign owner can rename/swap
        (0o1777, 1001, 1000, False),  # owner controls its sticky dir
        (0o700, 1001, 1000, False),  # foreign, non-traversable
    ],
)
def test_existing_ancestor_trusted_matrix(
    mode: Any, owner: Any, self_uid: Any, trusted: Any
) -> None:
    assert fci._existing_ancestor_trusted(mode, owner, self_uid) is trusted


def test_retain_evidence_traversal_component_refused(tmp_path: Path) -> None:
    work = tmp_path / "work-root"
    dest = tmp_path / "out" / ".." / "out" / "selected-evidence.json"
    with pytest.raises(fci.FixtureError, match="evidence-path-untrusted"):
        fci._retain_evidence(dest, EVIDENCE_PAYLOAD, EVIDENCE_DIGEST, work)


def test_retain_evidence_write_failure_leaves_no_final(tmp_path: Path, monkeypatch: Any) -> None:
    work = tmp_path / "work-root"
    dest = tmp_path / "out" / "selected-evidence.json"
    real_fdopen = os.fdopen

    def flaky_fdopen(fd: Any, *args: Any, **kwargs: Any) -> Any:
        handle = real_fdopen(fd, *args, **kwargs)
        real_write = handle.write

        def flaky(chunk: Any) -> NoReturn:
            real_write(chunk[:4])  # partial write, then the failure
            raise OSError("injected write failure")

        handle.write = flaky
        return handle

    monkeypatch.setattr(fci.os, "fdopen", flaky_fdopen)
    with pytest.raises(OSError):
        fci._retain_evidence(dest, EVIDENCE_PAYLOAD, EVIDENCE_DIGEST, work)
    assert not dest.exists()  # no partial final file
    _no_tmp_left(dest.parent)  # only the owned temp is cleaned up


def test_retain_evidence_short_write_digest_failure_leaves_no_final(
    tmp_path: Path, monkeypatch: Any
) -> None:
    work = tmp_path / "work-root"
    dest = tmp_path / "out" / "selected-evidence.json"
    real_fdopen = os.fdopen

    def short_fdopen(fd: Any, *args: Any, **kwargs: Any) -> Any:
        handle = real_fdopen(fd, *args, **kwargs)
        real_write = handle.write

        def short(chunk: Any) -> Any:
            return real_write(chunk[:4])  # short write, no exception

        handle.write = short
        return handle

    monkeypatch.setattr(fci.os, "fdopen", short_fdopen)
    with pytest.raises(fci.FixtureError, match="evidence-digest"):
        fci._retain_evidence(dest, EVIDENCE_PAYLOAD, EVIDENCE_DIGEST, work)
    assert not dest.exists()
    _no_tmp_left(dest.parent)


def test_retain_evidence_digest_mismatch_leaves_no_final(tmp_path: Path, monkeypatch: Any) -> None:
    work = tmp_path / "work-root"
    dest = tmp_path / "out" / "selected-evidence.json"
    monkeypatch.setattr(fci, "sha256_file", lambda path: "0" * 64)
    with pytest.raises(fci.FixtureError, match="evidence-digest"):
        fci._retain_evidence(dest, EVIDENCE_PAYLOAD, EVIDENCE_DIGEST, work)
    assert not dest.exists()
    _no_tmp_left(dest.parent)


def test_retain_evidence_concurrent_destination_at_commit_preserved(
    tmp_path: Path, monkeypatch: Any
) -> None:
    # Commit-boundary control: a destination appearing BETWEEN the
    # early existence check and the commit must be preserved — an
    # overwriting rename is not an atomic no-overwrite publication.
    work = tmp_path / "work-root"
    dest = tmp_path / "out" / "selected-evidence.json"
    dest.parent.mkdir()
    os.chmod(dest.parent, 0o700)  # the protected parent contract
    real_sha = fci.sha256_file
    state = {"calls": 0}

    def racing_sha(path: Any) -> Any:
        state["calls"] += 1
        if state["calls"] == 1:
            # The concurrent writer wins at the commit boundary
            # (after the pre-commit digest check of the temp file).
            dest.write_bytes(b"concurrent destination bytes")
        return real_sha(path)

    monkeypatch.setattr(fci, "sha256_file", racing_sha)
    with pytest.raises(fci.FixtureError, match="evidence-exists"):
        fci._retain_evidence(dest, EVIDENCE_PAYLOAD, EVIDENCE_DIGEST, work)
    # The concurrent bytes are preserved, never overwritten.
    assert dest.read_bytes() == b"concurrent destination bytes"
    _no_tmp_left(dest.parent)


# -- review 19: named failure paths of the NEW capture implementation ------


class _CancelingExecutor:
    """A fake host-cancellation seam: the scripted executor runs
    normally until the Nth admitted call, then the host dies ONCE
    (one-shot KeyboardInterrupt — the single in-flight cancellation
    is the case under test: cleanup must then run to completion,
    which a persistent outage would make impossible and could never
    claim removals for).  No host-wide signal is ever sent."""

    def __init__(self, inner: Any, after_calls: int, one_shot: bool = True) -> None:
        self.inner = inner
        self.after_calls = after_calls
        self.one_shot = one_shot
        self.calls = 0
        self.cancelled = False

    def __call__(self, argv: list[str], timeout: float) -> Any:
        self.calls += 1
        if self.one_shot:
            # EXACTLY ONE cancellation: the (N+1)th admitted call.
            if self.calls == self.after_calls + 1:
                self.cancelled = True
                raise KeyboardInterrupt("host cancelled")
        elif self.calls > self.after_calls:
            # Persistent outage (a distinct case that can never
            # claim removals).
            self.cancelled = True
            raise KeyboardInterrupt("host cancelled")
        return self.inner(argv, timeout)


def test_run_cancelled_host_preserves_cancellation_and_cleans_up(
    tmp_path: Path, monkeypatch: Any
) -> None:
    fake = FixtureFakeDocker(ghost_container=True)
    repo, work, evidence_out = _setup(tmp_path, monkeypatch, fake)
    # Cancel mid-scenario: after the image is built and a container is
    # created, BEFORE publication.
    canceling = _CancelingExecutor(fake, 12)
    ghost_cid = next(cid for name, cid in fake.by_name.items() if "ghost" in name)
    with pytest.raises(KeyboardInterrupt):
        fci.run(repo, work, canceling, evidence_out=str(evidence_out))
    # The cancellation is PRESERVED (a raw KeyboardInterrupt, not a
    # FixtureError and never a success), the scratch root is
    # destroyed, and NO evidence is published.
    assert not os.path.lexists(str(work))
    assert not evidence_out.exists()
    # Every OWNED container created by the run was removed (exact
    # owned cleanup was attempted for each independent resource);
    # the unrelated pre-existing ghost container is untouched.
    assert set(fake.by_name.values()) - {ghost_cid} <= fake.removed
    assert ghost_cid not in fake.removed
    # The owned image was removed through the exact owned id.
    assert fake.image_removed
    assert fake.rmi_calls == [IMAGE_ID]


def test_run_cancelled_host_with_cleanup_failure_exposes_both(
    tmp_path: Path, monkeypatch: Any
) -> None:
    # A failed cleanup cannot be bypassed by the cancellation nor
    # silently become success: it is exposed ON the preserved
    # cancellation.
    fake = FixtureFakeDocker(rmi_rc=1)
    repo, work, evidence_out = _setup(tmp_path, monkeypatch, fake)
    canceling = _CancelingExecutor(fake, 12)
    with pytest.raises(KeyboardInterrupt) as excinfo:
        fci.run(repo, work, canceling, evidence_out=str(evidence_out))
    assert "image-rmi-failed" in str(excinfo.value)
    assert not os.path.lexists(str(work))
    assert not evidence_out.exists()
    assert not fake.image_removed


def test_run_cancelled_host_cleanup_timeout_charges_and_continues(
    tmp_path: Path, monkeypatch: Any
) -> None:
    # A guarded actual Docker cleanup operation can raise
    # _OwnedTimeout (or an operational OSError) — neither is a
    # FixtureError.  The sweep must record an HONEST unverified
    # state, charge the timeout's measured drained bytes exactly
    # once, keep attempting the LATER independent owned resources
    # (image / sentinel / work root), and preserve the primary
    # cancellation — never turn an unverified query into absence
    # nor let the failure bypass or replace it.
    charged: list[object] = []
    real_charge = fci._RunLedger.charge

    def charge_spy(self: Any, result: Any) -> None:
        charged.append(result)
        real_charge(self, result)

    monkeypatch.setattr(fci._RunLedger, "charge", charge_spy)
    fake = FixtureFakeDocker(ghost_container=True, rm_fail="timeout")
    repo, work, evidence_out = _setup(tmp_path, monkeypatch, fake)
    canceling = _CancelingExecutor(fake, 12)
    ghost_cid = next(cid for name, cid in fake.by_name.items() if "ghost" in name)
    with pytest.raises(KeyboardInterrupt) as excinfo:
        fci.run(repo, work, canceling, evidence_out=str(evidence_out))
    # The preserved primary carries the HONEST unverified reason.
    assert "container-cleanup:timeout-unverified" in str(excinfo.value)
    # The timed-out drained bytes charged the ledger EXACTLY ONCE.
    timeouts = [c for c in charged if isinstance(c, fci._OwnedTimeout)]
    assert len(timeouts) == 1
    assert timeouts[0].drained_bytes == 4096
    # The failed rm is NOT verified absence: the owned container is
    # still present in the fake's state (unverified, recorded).
    owned_cids = [cid for cid in fake.by_name.values() if cid != ghost_cid]
    assert owned_cids
    assert any(cid not in fake.removed for cid in owned_cids)
    # LATER independent owned cleanup was still attempted: the exact
    # owned image id was removed, the unrelated ghost untouched.
    assert fake.image_removed
    assert fake.rmi_calls == [IMAGE_ID]
    assert ghost_cid not in fake.removed
    # No evidence published; the scratch root destroyed.
    assert not os.path.lexists(str(work))
    assert not evidence_out.exists()


def test_real_execute_held_pipe_converges_bounded(tmp_path: Path, monkeypatch: Any) -> None:
    # The NEW pipe capture seam: the leader exits while a same-group
    # descendant holds the pipe — bounded convergence by the exact
    # owned group kill after the drain grace, with the bounded
    # partial retained and the measured drained total preserved.
    monkeypatch.setattr(fci, "_READER_GRACE_SECONDS", 1.0)
    monkeypatch.setattr(fci, "_READER_RECOVERY_SECONDS", 1.0)
    monkeypatch.setattr(fci, "_LEADER_REAP_SECONDS", 2.0)
    pidfile = tmp_path / "holder.pid"
    code = (
        "import os, subprocess, sys\n"
        "holder = subprocess.Popen("
        "[sys.executable, '-c', 'import time; time.sleep(60)'], "
        "stdout=None, stderr=subprocess.DEVNULL)\n"
        "with open(sys.argv[1], 'w') as fh:\n"
        "    fh.write(str(holder.pid))\n"
        "print('slaif-held-pipe-partial', flush=True)\n"
        "os._exit(0)\n"
    )
    result = fci._real_execute([sys.executable, "-c", code, str(pidfile)], 5.0)
    assert result.returncode == 0
    assert result.output == b"slaif-held-pipe-partial\n"
    assert result.drained_bytes == len(result.output)
    # The exact owned group kill reached the same-group holder: the
    # pipe closed and the bounded convergence completed (the test
    # would otherwise hang or leak the 60-second holder).
    _assert_test_owned_holder_gone(pidfile)


def test_real_execute_held_pipe_escaped_holder_fails_closed(
    tmp_path: Path, monkeypatch: Any
) -> None:
    # A holder that escaped the owned group cannot be reached by the
    # group kill: the NEW seam converges to the HONEST fixed failure
    # (no uncaught thread exception, no empty-success output).
    monkeypatch.setattr(fci, "_READER_GRACE_SECONDS", 1.0)
    monkeypatch.setattr(fci, "_READER_RECOVERY_SECONDS", 1.0)
    monkeypatch.setattr(fci, "_LEADER_REAP_SECONDS", 2.0)
    pidfile = tmp_path / "holder.pid"
    code = (
        "import os, subprocess, sys\n"
        "holder = subprocess.Popen("
        "[sys.executable, '-c', "
        "'import os, time\\nos.setsid()\\ntime.sleep(60)'], "
        "stdout=None, stderr=subprocess.DEVNULL)\n"
        "with open(sys.argv[1], 'w') as fh:\n"
        "    fh.write(str(holder.pid))\n"
        "print('slaif-held-pipe-partial', flush=True)\n"
        "os._exit(0)\n"
    )
    try:
        with pytest.raises(fci.FixtureError, match="process-cleanup-failed"):
            fci._real_execute([sys.executable, "-c", code, str(pidfile)], 5.0)
    finally:
        # Unconditional exact-identity cleanup on EVERY path: even a
        # failing assertion must leave no orphan and no reader.
        _reap_test_owned_holder(pidfile)


def _reap_test_owned_holder(pidfile: Path) -> None:
    """Exact-identity reap of the TEST-OWNED escaped holder (its own
    pid, no pattern matching, no other repository process) — run on
    EVERY path so a test failure can never leave an orphan or a
    reader behind."""
    if not pidfile.exists():
        return
    holder_pid = int(pidfile.read_text())
    try:
        os.kill(holder_pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    for _ in range(50):
        if not os.path.exists(f"/proc/{holder_pid}"):
            break
        time.sleep(0.1)
    assert not os.path.exists(f"/proc/{holder_pid}")


def _assert_test_owned_holder_gone(pidfile: Path) -> None:
    """The owned group kill has already been issued by the seam
    under test; the holder's own fd closure is what let the bounded
    capture converge, so its death is proven.  Its /proc entry can
    still outlive that instant while the kernel reaper is busy under
    load (a dead process's fds close at death, before the entry is
    reaped), so poll the EXACT owned pid with a bounded wait instead
    of racing the reaper."""
    if not pidfile.exists():
        return
    holder_pid = int(pidfile.read_text())
    for _ in range(50):
        if not os.path.exists(f"/proc/{holder_pid}"):
            return
        time.sleep(0.1)
    raise AssertionError(f"test-owned holder {holder_pid} still present after the bounded wait")


def test_real_execute_pty_held_pipe_converges_bounded(tmp_path: Path, monkeypatch: Any) -> None:
    # The NEW owned PTY seam: the leader exits while a same-group
    # descendant holds the slave — bounded convergence by the exact
    # owned group kill, the bounded partial retained, the slave-side
    # end (EIO) treated as the normal stream end, not a capture error.
    monkeypatch.setattr(fci, "_READER_GRACE_SECONDS", 1.0)
    monkeypatch.setattr(fci, "_READER_RECOVERY_SECONDS", 1.0)
    monkeypatch.setattr(fci, "_LEADER_REAP_SECONDS", 2.0)
    pidfile = tmp_path / "holder.pid"
    code = (
        "import os, subprocess, sys\n"
        "holder = subprocess.Popen("
        "[sys.executable, '-c', 'import time; time.sleep(60)'], "
        "stdout=None, stderr=None)\n"
        "with open(sys.argv[1], 'w') as fh:\n"
        "    fh.write(str(holder.pid))\n"
        "print('slaif-pty-held-partial', flush=True)\n"
        "os._exit(0)\n"
    )
    result = fci._real_execute_pty([sys.executable, "-c", code, str(pidfile)], 5.0)
    assert result.returncode == 0
    assert result.output.startswith(b"slaif-pty-held-partial")
    assert result.drained_bytes >= len(result.output)
    _assert_test_owned_holder_gone(pidfile)


def test_real_execute_capture_read_error_fails_closed(monkeypatch: Any) -> None:
    # A reader read error on the NEW pipe seam is the fixed closed
    # state output-read-failed: never an empty-success output, never
    # an uncaught thread exception; the exact owned child is reaped.
    def boom(stream: Any, cap: Any) -> NoReturn:
        raise RuntimeError("injected read failure")

    monkeypatch.setattr(fci, "read_bounded_output", boom)
    with pytest.raises(fci.FixtureError, match="output-read-failed"):
        fci._real_execute([sys.executable, "-c", "pass"], 5.0)
