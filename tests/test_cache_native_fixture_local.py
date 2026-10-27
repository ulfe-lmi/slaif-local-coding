"""Pure lifecycle tests for the order-bound local 017-s owner.

These tests exercise the local owner's PROTECTED CONTROL INTERFACE
(prepare / observe / rehearse / finish / abort over the bounded
closed socket protocol) with a scripted FakeDocker, a fake git
runner and the real closed records — the same fake-layer law as the
hosted R runner tests: no test launches docker, a container, a
namespace or the native binary.  The actual local proof is the ONE
bounded rehearsal at the committed/pushed/green head; these tests
never substitute for it.

Covered: the full pass lifecycle through the interface (same run,
ledger, attempt, END), non-consuming observe, create-intent /
CID-before-start state publication, the held env file through
PREPARED, prepare-failure convergence with retained fail evidence
and the recovered build intent, owner-abort command, exact-run-id
abort file, deadline expiry, cleanup-failure-forbids-pass, the
sentinel fact, single rmi, client-disappearance independence,
run-id / malformed-request refusal, opt-in refusals recording no
attempt, one-attempt admission, bounded git reads and the sealed
owner argv.
"""

from __future__ import annotations

import base64
import contextlib
import copy
import hashlib
import importlib.util
import json
import os
import socket
import stat
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CI_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_ci.py"
LOCAL_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_local.py"
ORDER_PATH = REPO_ROOT / "oap" / "orders" / "017-s-local-fixture-preparation-and-supervision.md"

spec = importlib.util.spec_from_file_location("cache_native_fixture_ci", CI_PATH)
assert spec is not None and spec.loader is not None
fci = importlib.util.module_from_spec(spec)
sys.modules["cache_native_fixture_ci"] = fci
spec.loader.exec_module(fci)

model = fci.model
fixture_standin = fci.fixture_standin

lci_spec = importlib.util.spec_from_file_location("cache_native_fixture_local", LOCAL_PATH)
assert lci_spec is not None and lci_spec.loader is not None
flocal = importlib.util.module_from_spec(lci_spec)
sys.modules["cache_native_fixture_local"] = flocal
lci_spec.loader.exec_module(flocal)

HEAD = "f" * 40
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


def _local_payload(wire_requests: int, position: int | None, diagnostic: dict[str, Any]) -> bytes:
    """The closed selected payload frame the controller exports for
    a MEASURED one-shot diagnostic state: the diagnostic scenario
    ISSUES NOTHING (empty issued_calls) and the controller's OWN
    ledger is the measured wire history plus exactly the two
    exporter commands (quiesce + export)."""
    snapshot = {
        "record": "slaif-fixture-selected-snapshot-v1",
        "synthetic": True,
        "issued_calls": [],
        "originals_bytes": 11,
        "originals_sha256": hashlib.sha256(b"onetwothree").hexdigest(),
        "exporter_uid": fci.CONTROLLER_UID,
        "exported_before_teardown": True,
        "controller_ledger": {"requests": wire_requests + 2, "output_bytes": 2048},
    }
    originals = [base64.b64encode(raw).decode("ascii") for raw in (b"one", b"two", b"three")]
    payload = {
        "quiesce": QUIESCE_RECORD,
        "snapshot": snapshot,
        "diagnostic": diagnostic,
        "observed_at_position": position,
        "originals": originals,
        "originals_count": len(originals),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def _local_selected_payload(
    wire_requests: int, position: int = 0, diagnostic: dict[str, Any] | None = None
) -> bytes:
    """The OBSERVED (diagnostic-consumed) selected payload.  The
    default is the S python rehearsal's fixed single-source
    no-tools metadata at causal position 0; an external subject's
    own request carries its OWN closed metadata diagnostic at its
    measured causal position."""
    if diagnostic is None:
        diagnostic = model.bounds_diagnostic(fixture_standin._fixed_request([]))
    return _local_payload(wire_requests, position, diagnostic)


def _local_unobserved_payload(wire_requests: int) -> bytes:
    """The UNOBSERVED selected payload: no admitted POST ever
    consumed the one-shot diagnostic (causal position None)."""
    return _local_payload(wire_requests, None, {"state": "unobserved"})


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


class LocalFakeDocker:
    """Scripted fake docker executor for the local 017-s owner.

    Models the exact closed surface the local flow queries (engine
    preflight, collision probe, pull/build, the single prepared
    container's create/start/exec/inspect/top/rm, the image rmi and
    the authoritative absence marker).  The fake records the state
    file AT the create and start boundaries (the CID-before-start
    publication proofs) and models the controller's own cumulative
    request count for the non-consuming observe."""

    def __init__(
        self,
        *,
        build_rc: int = 0,
        sleep_build: float = 0.0,
        id_query_rc: int = 0,
        rm_fail: str = "none",
        standin_fail: tuple[str, str | None] | None = None,
        observe_wire: int | None = None,
        create_fail_rc: int = 0,
        observe_states: list[dict[str, Any]] | None = None,
        export_state: dict[str, Any] | None = None,
        export_diagnostic: dict[str, Any] | None = None,
        export_payload: bytes | None = None,
        diagnostic_position: int = 0,
        daemon_name: str | None = None,
    ) -> None:
        assert rm_fail in ("none", "timeout")
        self.build_rc = build_rc
        self.sleep_build = sleep_build
        self.id_query_rc = id_query_rc
        self.rm_fail = rm_fail
        self.standin_fail = standin_fail
        self.observe_wire = observe_wire
        self.create_fail_rc = create_fail_rc
        self.observe_states = observe_states
        self.observe_calls = 0
        self.export_state = export_state
        self.export_diagnostic = export_diagnostic
        self.export_payload = export_payload
        self.diagnostic_position = diagnostic_position
        self.daemon_name = daemon_name
        self.built = False
        self.image_removed = False
        self.calls: list[list[str]] = []
        self.by_name: dict[str, str] = {}
        self.removed: set[str] = set()
        self.rmi_calls: list[str] = []
        self.wire_requests = 0
        self.diagnostic_observed = False
        self.image_tag_inspects = 0
        self.env_file_path: str | None = None
        self.state_at_create: dict[str, Any] | None = None
        self.state_at_start: dict[str, Any] | None = None
        self.build_gate: threading.Event | None = None

    def _result(self, rc: int, out: bytes) -> Any:
        return fci.ExecResult(rc, out, len(out))

    def _read_state(self) -> dict[str, Any]:
        path = Path(self._state_path)
        state: dict[str, Any] = json.loads(path.read_bytes().decode("ascii"))
        return state

    # the control dir is wired in by the test before any command
    _state_path: str = ""

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
                return self._result(0, b"runc\n")
            if fmt == "{{json .Runtimes}}":
                return self._result(0, json.dumps({"runc": {"path": "runc"}}).encode() + b"\n")
            if fmt == "{{.Name}}":
                return self._result(0, (self.daemon_name or socket.gethostname()).encode() + b"\n")
            raise AssertionError(f"unexpected info format: {fmt}")
        if cmd[0] == "pull":
            assert cmd[1] == fci.PINNED_BASE
            return self._result(0, b"pulled\n")
        if cmd[0] == "build":
            if self.build_gate is not None:
                assert self.build_gate.wait(30.0), "build gate never released"
            if self.sleep_build:
                time.sleep(self.sleep_build)
            if self.build_rc == 0:
                self.built = True
            out = b"built\n" if self.build_rc == 0 else b"build error\n"
            return self._result(self.build_rc, out)
        if cmd[:2] == ["inspect", "--format"]:
            fmt, target = cmd[2], cmd[3]
            if target == fci.IMAGE_NAME:
                assert fmt == "{{.Id}}"
                self.image_tag_inspects += 1
                # 1st inspect: the collision probe (before build);
                # 2nd: the owner's id discovery (after build) —
                # id_query_rc simulates that ONE query failing;
                # later inspects (the umbrella's own-tag recovery)
                # behave normally.
                if self.image_tag_inspects == 1:
                    err = b"Error: No such object: " + fci.IMAGE_NAME.encode() + b"\n"
                    return self._result(1, err)
                if self.image_tag_inspects == 2 and self.id_query_rc:
                    return self._result(self.id_query_rc, b"build id query failed\n")
                if self.built or self.image_removed:
                    if self.image_removed:
                        err = b"Error: No such object: " + fci.IMAGE_NAME.encode() + b"\n"
                        return self._result(1, err)
                if self.built:
                    return self._result(0, (IMAGE_ID + "\n").encode())
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
            assert self._state_path, "state path not wired"
            self.state_at_create = self._read_state()
            cid = hashlib.sha256(name.encode()).hexdigest()
            self.by_name[name] = cid
            if self.create_fail_rc:
                # The create/response gap: the name was reserved and
                # the object may exist, but the CID response is lost
                # to the caller (a failed create is not proof of
                # absence).
                return self._result(self.create_fail_rc, b"create error\n")
            return self._result(0, (cid + "\n").encode())
        if cmd[0] == "start":
            cid = cmd[1]
            assert self._state_path, "state path not wired"
            self.state_at_start = self._read_state()
            return self._result(0, b"")
        if cmd[0] == "top":
            return self._result(0, b"UID          PID    COMMAND\nslaifctl     1      python3\n")
        if cmd[0] == "exec":
            return self._exec(cmd)
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
                partial = b"slaif-fixture-cleanup-timeout-partial\n"
                raise fci._OwnedTimeout(list(self.calls[-1]), timeout, partial, drained_bytes=4096)
            self.removed.add(cid)
            return self._result(0, (cid + "\n").encode())
        if cmd[0] == "rmi":
            self.rmi_calls.append(cmd[1])
            if cmd[1] == IMAGE_ID:
                self.image_removed = True
            return self._result(0, b"Deleted: untagged\n")
        if cmd[:2] == ["image", "inspect"]:
            if self.image_removed:
                return self._result(1, b"Error: No such object: " + IMAGE_ID.encode() + b"\n")
            if self.built:
                return self._result(0, b"[]\n")
            return self._result(1, b"Error: No such object: " + IMAGE_ID.encode() + b"\n")
        raise AssertionError(f"unexpected docker command: {cmd}")

    def _exec(self, cmd: list[str]) -> Any:
        i = 1
        itty = False
        if cmd[i] == "-it":
            itty = True
            i += 1
        assert cmd[i] == "--user"
        uid = cmd[i + 1]
        i += 2
        env: dict[str, str] = {}
        env_file = None
        while i < len(cmd) and (cmd[i] == "-e" or cmd[i] == "--env-file"):
            if cmd[i] == "--env-file":
                env_file = cmd[i + 1]
            else:
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
            record["healthz_attempts"] = 1
            line = json.dumps(record, sort_keys=True, separators=(",", ":"))
            return self._result(0, (line + "\n").encode())
        if (
            len(tail) == 4
            and tail[0] == "python3"
            and tail[1] == fci.STANDIN_PATH
            and tail[2] == "--mode"
        ):
            return self._standin_exec(tail[3], itty, env, uid, env_file)
        if len(tail) == 2 and tail[0] == "python3" and tail[1] == fci.EXPORT_CLIENT_PATH:
            assert uid == f"{fci.CONTROLLER_UID}:{fci.CONTROLLER_UID}"
            payload = self._export_payload_bytes()
            sha = hashlib.sha256(payload).hexdigest()
            quiesce = (
                b"quiesce-ok "
                + json.dumps(QUIESCE_RECORD, sort_keys=True, separators=(",", ":")).encode()
            )
            return self._result(0, quiesce + b"\nexport-sha256 " + sha.encode() + b"\n" + payload)
        raise AssertionError(f"unexpected exec tail: {tail}")

    def _export_payload_bytes(self) -> bytes:
        # The verbatim override is the FORGERY seam (a closed but
        # identity-inconsistent payload the host must reject).
        if self.export_payload is not None:
            return self.export_payload
        if self.export_state is not None:
            wire = self.export_state["wire_requests"]
            observed = self.export_state["diagnostic_state"] == "observed"
        else:
            wire = self.wire_requests
            observed = self.diagnostic_observed
        if observed:
            return _local_selected_payload(
                wire,
                position=self.diagnostic_position,
                diagnostic=self.export_diagnostic,
            )
        return _local_unobserved_payload(wire)

    def _standin_exec(
        self, mode: str, itty: bool, env: dict[str, str], uid: str, env_file: str | None
    ) -> Any:
        assert uid == f"{fci.SUBJECT_UID}:{fci.SUBJECT_UID}"
        if self.standin_fail is not None and self.standin_fail[0] == mode:
            if self.standin_fail[1] is None:
                return self._result(2, b"")
            fail_line = {
                "record": "slaif-fixture-standin-v1",
                "status": "fail",
                "reason": self.standin_fail[1],
            }
            return self._result(
                2, (json.dumps(fail_line, sort_keys=True, separators=(",", ":")) + "\n").encode()
            )
        if mode == "measure":
            assert "SLAIF_FIXTURE_TMPFS_SPECS" in env
            assert "SLAIF_FIXTURE_PRESENCE_SHA256" in env
            line = _exec_measurement_record()
        elif mode == "pty":
            assert itty, "the pty rehearsal must attach through -it"
            assert len(env.get("SLAIF_RUN_TOKEN", "")) == 32
            assert env_file, "the local pty rehearsal must use the protected env file"
            self.env_file_path = env_file
            line = _standin_record(
                "pty",
                pty_attached=True,
                term_rows=fci.PTY_ROWS,
                term_cols=fci.PTY_COLS,
                terminal_properties_closed_only=True,
                env_handoff_verified=True,
                workspace={"path": "/run/slaif-subj/work", "mode": 0o700, "uid": fci.SUBJECT_UID},
                profile=_profile_record(),
            )
        elif mode == "observe":
            if self.observe_states is not None:
                # Explicit measured state SEQUENCE (an external
                # subject's wire history between prepare and
                # finish): the nth observe reports the nth state,
                # the last one holding thereafter.
                state = self.observe_states[min(self.observe_calls, len(self.observe_states) - 1)]
                self.observe_calls += 1
                wire = state["wire_requests"]
                dstate = state["diagnostic_state"]
            else:
                wire = self.observe_wire if self.observe_wire is not None else self.wire_requests
                dstate = "observed" if self.diagnostic_observed else "unobserved"
            line = _standin_record(
                "observe",
                scenario="diagnostic",
                wire_requests=wire,
                diagnostic_state=dstate,
                raw_content_retained=False,
            )
        elif mode == "auth-binding":
            assert len(env.get("SLAIF_RUN_TOKEN", "")) == 32
            self.wire_requests += 3
            self.diagnostic_observed = True
            line = _standin_record(
                "auth-binding",
                valid_admitted=True,
                wrong_refused=True,
                missing_refused=True,
                diagnostic_response="fixed-final-text-no-tools",
                requests=3,
                attempts=3,
            )
        else:
            raise AssertionError(f"unexpected standin mode: {mode}")
        out = (json.dumps(line, sort_keys=True, separators=(",", ":")) + "\n").encode()
        return self._result(0, out)


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


def _make_local_repo(
    tmp_path: Path, *, dirty: bytes = b"", order_bytes: bytes | None = None
) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    for name in (
        "cache_native_fixture_ci.py",
        "cache_native_fixture_model.py",
        "cache_native_fixture_controller.py",
        "cache_native_fixture_standin.py",
        "cache_native_fixture_export_client.py",
        "cache_native_fixture_local.py",
        "cache_native_fixture.Dockerfile",
    ):
        (repo / "scripts" / name).write_bytes((REPO_ROOT / "scripts" / name).read_bytes())
    (repo / "Dockerfile").write_bytes((REPO_ROOT / "Dockerfile").read_bytes())
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_bytes(
        (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_bytes()
    )
    (repo / "oap" / "orders").mkdir(parents=True)
    order = order_bytes if order_bytes is not None else ORDER_PATH.read_bytes()
    (repo / "oap" / "orders" / "017-s-local-fixture-preparation-and-supervision.md").write_bytes(
        order
    )
    (repo / "oap" / "active").write_bytes(b"017-s\n")
    (repo / ".git" / "info").mkdir(parents=True)
    (repo / ".git" / "info" / "exclude").write_bytes(b"")
    return repo


def _git_runner_factory(dirty: bytes = b"", order_bytes: bytes | None = None) -> Any:
    order = order_bytes if order_bytes is not None else ORDER_PATH.read_bytes()

    def git_runner(args: list[str], repo: Path) -> bytes:
        if args == ["rev-parse", "HEAD"]:
            return HEAD.encode()
        if args == ["status", "--porcelain"]:
            return dirty
        if len(args) == 2 and args[0] == "show" and args[1] == f"{HEAD}:{flocal.ORDER_PATH}":
            return order
        raise AssertionError(f"unexpected git args: {args}")

    return git_runner


def _setup(
    tmp_path: Path, monkeypatch: Any, fake: LocalFakeDocker, **repo_kwargs: Any
) -> dict[str, Any]:
    repo = _make_local_repo(tmp_path, **repo_kwargs)
    work = tmp_path / "work"
    control = tmp_path / "control"
    evidence = tmp_path / "evidence" / "local-evidence.json"
    monkeypatch.setattr(fci, "fetch_public_artifact", _fake_fetch)
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
    # hermetic endpoint selection: no inherited remote endpoint may
    # leak into the local owner's section-2 verification
    for var in flocal._LOCAL_ENDPOINT_SELECTION_VARS:
        monkeypatch.delenv(var, raising=False)
    # hermetic local environment: the disposable hosted runner's
    # ambient GITHUB_ACTIONS must not reach the local owner's
    # production hosted-env guard (the explicit hosted-refusal
    # negative test sets it back on purpose)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    # hermetic narrow local socket: a bound (closed) AF_UNIX file the
    # owner may lstat read-only (no Docker call, no listener)
    sock = socket.socket(socket.AF_UNIX)
    sock_path = tmp_path / "docker.sock"
    sock.bind(str(sock_path))
    sock.close()
    monkeypatch.setattr(flocal, "_LOCAL_DOCKER_SOCKET", str(sock_path))
    fake._state_path = str(control / flocal._CONTROL_STATE_NAME)
    return {
        "repo": repo,
        "work": work,
        "control": control,
        "evidence": evidence,
        "git_runner": _git_runner_factory(**repo_kwargs),
    }


def _start_owner(paths: dict[str, Any], fake: LocalFakeDocker, **owner_kwargs: Any) -> Any:
    owner = flocal.LocalFixtureOwner(
        paths["repo"],
        paths["work"],
        paths["evidence"],
        HEAD,
        paths["control"],
        git_runner=paths["git_runner"],
        executor=fake,
        **owner_kwargs,
    )
    thread = threading.Thread(target=owner.serve, daemon=True)
    thread.start()
    end = time.monotonic() + 30.0
    while time.monotonic() < end:
        state = flocal._state_record(paths["control"])
        if state is not None:
            return owner, thread, str(state["run_id"])
        time.sleep(0.05)
    pytest.fail("owner never published its initial state")


def _client(control: Path, command: str, run_id: str, timeout: float = 120.0) -> dict[str, Any]:
    response = flocal._control_client(control, command, run_id, timeout)
    assert isinstance(response, dict)
    return response


def _join(
    thread: threading.Thread,
    *,
    control: Path | None = None,
    run_id: str | None = None,
    timeout: float = 60.0,
) -> None:
    """Join the owner thread.  When the test is in a FAILED state,
    first issue the bounded EXACT-OWNER abort (the owner's own
    terminal command over its protected interface — never a host
    signal), so a failed assertion cannot leave a live owner thread
    or the unrelated parent sentinel behind.  The owner is reaped
    only through its own convergence; a still-alive owner after the
    bounded abort fails the test loudly instead of leaking it."""
    if sys.exc_info()[0] is not None and control is not None and run_id is not None:
        with contextlib.suppress(Exception):
            _client(control, "abort", run_id, timeout=15.0)
    thread.join(timeout)
    if thread.is_alive():
        pytest.fail("owner thread did not converge after bounded abort")


def _read_evidence(evidence: Path) -> dict[str, Any]:
    raw = evidence.read_bytes()
    record: dict[str, Any] = json.loads(raw.decode("ascii"))
    flocal.validate_local_evidence(record)
    return record


# -- full lifecycle through the protected interface ------------------------------
def test_full_lifecycle_pass_through_control_interface(tmp_path: Path, monkeypatch: Any) -> None:
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        prepared = _client(paths["control"], "prepare", run_id)
        assert prepared["ok"] is True
        detail = prepared["detail"]
        cid = detail["cid"]
        assert fci._is_cid(cid)
        assert detail["state"] == "prepared-unconsumed"
        assert detail["observed"] == {
            "scenario": "diagnostic",
            "wire_requests": 0,
            "diagnostic_state": "unobserved",
        }
        assert detail["end_anchor"] > 0
        # The exact fresh create intent was published BEFORE create,
        # and the exact CID was published BEFORE start.
        assert fake.state_at_create is not None
        assert fake.state_at_create["create_intent"] == next(n for n in fake.by_name)
        assert fake.state_at_create["containers"] == []
        assert fake.state_at_start is not None
        assert fake.state_at_start["containers"] == [cid]
        # The protected env file is HELD while the fixture is held.
        assert fake.env_file_path is not None
        assert os.path.isfile(fake.env_file_path)
        observed = _client(paths["control"], "observe", run_id)
        assert observed["ok"] is True
        assert observed["detail"] == {
            "scenario": "diagnostic",
            "wire_requests": 0,
            "diagnostic_state": "unobserved",
            "raw_content_retained": False,
        }
        consumed = _client(paths["control"], "rehearse", run_id)
        assert consumed["ok"] is True
        assert consumed["detail"]["admitted"] == 1
        assert consumed["detail"]["refused"] == 2
        final = _client(paths["control"], "finish", run_id)
        assert final["ok"] is True
        assert final["detail"]["outcome"] == "pass"
        assert final["detail"]["control_dir_retained"] is False
        assert final["detail"]["stage"] == "publish"
        assert final["detail"]["evidence_sha256"] is not None
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 0
    # retained closed evidence, protected modes, outside the work root
    evidence = paths["evidence"]
    est = os.lstat(evidence)
    assert stat.S_IMODE(est.st_mode) == 0o600 and est.st_uid == os.getuid()
    record = _read_evidence(evidence)
    assert record["status"] == "pass"
    assert record["run_id"] == run_id
    assert record["ledger"] == {
        "docker_admissions": record["ledger"]["docker_admissions"],
        "docker_refusals": 0,
        "bytes_drained": record["ledger"]["bytes_drained"],
        "bytes_retained": record["ledger"]["bytes_retained"],
        "api_requests": 5,
        "api_attempts": 5,
        "requests_admitted": 3,
        "requests_refused": 2,
        "healthz_attempts": record["ledger"]["healthz_attempts"],
    }
    assert record["ledger"]["healthz_attempts"] >= 1
    assert record["image_state"] == "absent-verified"
    assert record["image_identity_vs_ci"] is False
    assert record["teardown"]["sentinel_survived"] is True
    assert record["env_file"]["removed"] is True
    assert record["phases"]["prepare"]["cid"] == record["phases"]["consume"]["cid"]
    assert record["phases"]["consume"]["cid"] == record["phases"]["finish"]["cid"]
    # single rmi of the exact built image id
    assert fake.rmi_calls == [IMAGE_ID]
    assert fake.removed == {cid}
    # the disposable scratch and the control root are both gone; the
    # held env file with them
    assert not os.path.exists(paths["work"])
    assert not os.path.exists(paths["control"])
    assert not os.path.exists(fake.env_file_path)
    # the stable one-attempt record is terminal pass
    admission = json.loads((paths["repo"] / ".oap-local" / "017-s" / "admission.json").read_bytes())
    assert admission["attempts"] == [{"head": HEAD, "run_id": run_id, "status": "pass"}]


def test_repeated_observe_never_consumes(tmp_path: Path, monkeypatch: Any) -> None:
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        _client(paths["control"], "prepare", run_id)
        first = _client(paths["control"], "observe", run_id)
        second = _client(paths["control"], "observe", run_id)
        third = _client(paths["control"], "observe", run_id)
        assert first["detail"] == second["detail"] == third["detail"]
        assert first["detail"]["wire_requests"] == 0
        assert first["detail"]["diagnostic_state"] == "unobserved"
        final = _client(paths["control"], "finish" and "rehearse", run_id)
        assert final["ok"] is True
        finished = _client(paths["control"], "finish", run_id)
        assert finished["detail"]["outcome"] == "pass"
        # the controller's own ledger at export: 3 auth + 2 exporter —
        # the repeated observes allocated no position and charged no
        # provider requests on the host side
        assert fake.wire_requests == 3
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    record = _read_evidence(paths["evidence"])
    assert record["phases"]["finish"]["controller_ledger_requests"] == 5
    assert record["phases"]["finish"]["observed_at_position"] == 0
    assert record["ledger"]["api_requests"] == 5


def test_prepare_failure_converges_retains_fail_evidence(tmp_path: Path, monkeypatch: Any) -> None:
    fake = LocalFakeDocker(build_rc=1)
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        response = _client(paths["control"], "prepare", run_id)
        assert response["ok"] is False
        assert response["reason"] == "build-failed"
        # the owner already converged: its protected control surface
        # is closed and the socket unlinked, so a late client gets
        # the closed typed refusal (no further service, no silent
        # accept of a post-convergence command)
        with pytest.raises(fci.FixtureError, match="local-control-socket-untrusted"):
            _client(paths["control"], "observe", run_id)
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 1
    record = _read_evidence(paths["evidence"])
    assert record["status"] == "fail"
    assert record["reason"] == "build-failed"
    assert record["stage"] == "build"
    # the fresh build intent was registered before the build and the
    # exact tag is retained as recovery data (the id was never
    # learned); the build failed BEFORE the container create, so no
    # create name intent was ever published
    assert record["resources"]["build_attempted"] is True
    assert record["resources"]["image_id"] is None
    assert record["resources"]["create_intent"] is None
    assert record["resources"]["containers"] == []
    # the failed id discovery could not verify image absence: the
    # protected registry/ledger is retained outside the scratch
    assert "image-cleanup-unverified" in record["cleanup_failures"]
    assert record["recovery_state_retained"] is True
    assert os.path.isdir(paths["control"])
    assert os.path.isfile(paths["control"] / flocal._CONTROL_STATE_NAME)
    assert not os.path.exists(paths["work"])
    admission = json.loads((paths["repo"] / ".oap-local" / "017-s" / "admission.json").read_bytes())
    assert admission["attempts"] == [{"head": HEAD, "run_id": run_id, "status": "fail"}]


def test_unknown_id_build_intent_recovered_via_own_tag(tmp_path: Path, monkeypatch: Any) -> None:
    # The build SUCCEEDS but the id discovery query fails: the image
    # exists under the exact own tag (the collision probe proved it
    # absent before the build).  The umbrella must recover the exact
    # fresh intent through that tag and verify removal.
    fake = LocalFakeDocker(id_query_rc=1)
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        response = _client(paths["control"], "prepare", run_id)
        assert response["ok"] is False
        # the measured token is the shared guarded-query failure (the
        # id discovery query itself failed, not the build)
        assert response["reason"] == "query-failed"
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    # the umbrella recovered the id through the tag and removed it
    assert fake.rmi_calls == [IMAGE_ID]
    assert fake.image_removed is True
    record = _read_evidence(paths["evidence"])
    assert record["status"] == "fail"
    assert record["reason"] == "query-failed"
    assert record["stage"] == "build"
    # the recovery SUCCEEDED: no image cleanup failure was recorded
    assert "image-cleanup-unverified" not in record["cleanup_failures"]
    assert record["resources"]["image_id"] == IMAGE_ID
    # complete measured cleanup: the control root is destroyed
    assert record["recovery_state_retained"] is False
    assert not os.path.exists(paths["control"])


def test_abort_command_while_held_converges_aborted(tmp_path: Path, monkeypatch: Any) -> None:
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        prepared = _client(paths["control"], "prepare", run_id)
        assert prepared["ok"] is True
        response = _client(paths["control"], "abort", run_id)
        assert response["ok"] is True
        assert response["detail"]["outcome"] == "aborted"
        assert response["detail"]["stage"] == "prepared"
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 130
    record = _read_evidence(paths["evidence"])
    assert record["status"] == "fail"
    assert record["reason"] == "cancelled"
    # the held container and image were still cleaned up
    cid = prepared["detail"]["cid"]
    assert fake.removed == {cid}
    assert fake.rmi_calls == [IMAGE_ID]
    admission = json.loads((paths["repo"] / ".oap-local" / "017-s" / "admission.json").read_bytes())
    assert admission["attempts"] == [{"head": HEAD, "run_id": run_id, "status": "aborted"}]


def test_abort_file_at_next_phase_boundary(tmp_path: Path, monkeypatch: Any) -> None:
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        _client(paths["control"], "prepare", run_id)
        # the exact run-id abort file: the SAME convergence at the
        # next phase boundary (the rehearse command's abort check,
        # still in the prepared phase), as a truthful abort
        (paths["control"] / "abort").write_text(run_id)
        response = _client(paths["control"], "rehearse", run_id)
        assert response["ok"] is False
        assert response["reason"] == "cancelled"
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 130
    record = _read_evidence(paths["evidence"])
    assert record["reason"] == "cancelled"
    assert record["stage"] == "prepared"


def test_env_file_held_through_prepared_removed_on_terminal(
    tmp_path: Path, monkeypatch: Any
) -> None:
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        _client(paths["control"], "prepare", run_id)
        assert fake.env_file_path is not None
        env_path = fake.env_file_path
        # held: the protected file is present while the owner holds
        st = os.lstat(env_path)
        assert stat.S_IMODE(st.st_mode) == 0o600
        state = flocal._state_record(paths["control"])
        assert state is not None
        assert state["env_file"] == env_path
        # terminal (abort): the umbrella removes the exact file
        _client(paths["control"], "abort", run_id)
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert not os.path.exists(env_path)
    record = _read_evidence(paths["evidence"])
    assert "env-file-remove-failed" not in record["cleanup_failures"]


def test_deadline_expiry_converges_through_cleanup(tmp_path: Path, monkeypatch: Any) -> None:
    # ONE anchor: the owner's own budget expires mid-build; the
    # grace only authorizes the cleanup window and never makes the
    # expired run on-time.
    monkeypatch.setattr(fci, "TOTAL_ANCHOR_SECONDS", 10.0)
    fake = LocalFakeDocker(sleep_build=5.0)
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake, deadline_offset=7.0)
    try:
        response = _client(paths["control"], "prepare", run_id, timeout=60.0)
        assert response["ok"] is False
        assert response["reason"] == "deadline-expired"
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 1
    record = _read_evidence(paths["evidence"])
    assert record["status"] == "fail"
    assert record["deadline_expired"] is True
    assert record["reason"] == "deadline-expired"
    assert record["stage"] == "build"
    # the ONE cleanup grace authorizes the recovery WINDOW: the
    # exact own-tag recovery succeeds inside it, the image is
    # verified removed and no cleanup failure remains
    assert fake.rmi_calls == [IMAGE_ID]
    assert "image-cleanup-unverified" not in record["cleanup_failures"]
    assert record["recovery_state_retained"] is False


def test_cleanup_failure_forbids_pass(tmp_path: Path, monkeypatch: Any) -> None:
    # The teardown rm times out: the primary failure is preserved and
    # the incomplete cleanup forbids a pass (truthful fail evidence),
    # while the independent image/sentinel cleanup is still attempted.
    fake = LocalFakeDocker(rm_fail="timeout")
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        _client(paths["control"], "prepare", run_id)
        _client(paths["control"], "rehearse", run_id)
        final = _client(paths["control"], "finish", run_id)
        assert final["ok"] is True
        assert final["detail"]["outcome"] == "fail"
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 1
    record = _read_evidence(paths["evidence"])
    assert record["status"] == "fail"
    assert "container-cleanup-unverified" in record["cleanup_failures"]
    # independent cleanup was still attempted: the image was removed
    assert fake.rmi_calls == [IMAGE_ID]
    # the unrelated sentinel survived the whole run (it is not a
    # fixture resource and must not be recorded dead)
    assert "sentinel-died" not in record["cleanup_failures"]
    admission = json.loads((paths["repo"] / ".oap-local" / "017-s" / "admission.json").read_bytes())
    assert admission["attempts"][0]["status"] == "fail"


def test_sentinel_death_is_containment_fact(tmp_path: Path, monkeypatch: Any) -> None:
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)

    def _dead_sentinel() -> subprocess.Popen[bytes]:
        proc = subprocess.Popen(
            [sys.executable, "-c", "pass"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        proc.wait(timeout=10)
        return proc

    monkeypatch.setattr(fci, "_spawn_parent_sentinel", _dead_sentinel)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        # the dead sentinel is caught at the FIRST phase boundary
        # after spawn (fail-fast containment fact): prepare itself
        # converges on the measured sentinel death
        response = _client(paths["control"], "prepare", run_id)
        assert response["ok"] is False
        assert response["reason"] == "sentinel-process-died"
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 1
    record = _read_evidence(paths["evidence"])
    assert record["reason"] == "sentinel-process-died"
    assert record["stage"] == "sentinels"
    # the actually-dead sentinel is the containment fact, kept
    # separate from the reap
    assert "sentinel-died" in record["cleanup_failures"]
    assert "sentinel-cleanup-failed" not in record["cleanup_failures"]
    # the already-learned built image was still removed exactly once
    assert fake.rmi_calls == [IMAGE_ID]


def test_rmi_exactly_once_healthy_finish(tmp_path: Path, monkeypatch: Any) -> None:
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        _client(paths["control"], "prepare", run_id)
        _client(paths["control"], "rehearse", run_id)
        _client(paths["control"], "finish", run_id)
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert fake.rmi_calls == [IMAGE_ID]
    assert len(fake.rmi_calls) == 1


# -- protocol closedness and independence ------------------------------------------
def test_client_disappearance_does_not_stop_owner(tmp_path: Path, monkeypatch: Any) -> None:
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        # a client that vanishes mid-command: the owner still
        # completes the command and keeps serving (client disappearance
        # cannot stop or reset ownership)
        raw = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        raw.connect(str(paths["control"] / flocal._CONTROL_SOCK_NAME))
        request = (
            json.dumps(
                {"record": flocal.CONTROL_RECORD, "command": "prepare", "run_id": run_id},
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode()
        raw.sendall(request)
        raw.close()
        end = time.monotonic() + 30.0
        state = None
        while time.monotonic() < end:
            state = flocal._state_record(paths["control"])
            if state is not None and state["phase"] != "start":
                break
            time.sleep(0.1)
        assert state is not None and state["phase"] != "start"
        # the fixture is still held and addressable by a NEW client
        observed = _client(paths["control"], "observe", run_id)
        assert observed["ok"] is True
        assert observed["detail"]["wire_requests"] == 0
        _client(paths["control"], "rehearse", run_id)
        final = _client(paths["control"], "finish", run_id)
        assert final["detail"]["outcome"] == "pass"
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 0


def test_run_id_mismatch_and_malformed_refused(tmp_path: Path, monkeypatch: Any) -> None:
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        # a response not bound to the EXACT requested identity is a
        # protocol violation: the client raises the closed typed
        # error instead of exposing any result (owner refusal is
        # defense-in-depth for the in-window race; the client-side
        # binding is what closes the gap)
        with pytest.raises(fci.FixtureError, match="local-control-protocol"):
            _client(paths["control"], "observe", "0" * 32)
        # malformed / overbound raw input is dropped, owner keeps serving
        raw = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        raw.connect(str(paths["control"] / flocal._CONTROL_SOCK_NAME))
        raw.sendall(b"not-json-at-all\n")
        raw.close()
        raw = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        raw.connect(str(paths["control"] / flocal._CONTROL_SOCK_NAME))
        raw.sendall(b"x" * (flocal._CONTROL_REQUEST_CAP + 1))
        raw.close()
        state = flocal._state_record(paths["control"])
        assert state is not None and state["phase"] == "start" and state["status"] == "running"
        prepared = _client(paths["control"], "prepare", run_id)
        assert prepared["ok"] is True
        _client(paths["control"], "abort", run_id)
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 130


# -- opt-in and one-attempt admission ------------------------------------------------
def _optin_refusal(paths: dict[str, Any], bind_head: str = HEAD) -> str:
    """A read-only opt-in refusal: the OWNER CONSTRUCTOR raises the
    closed refusal token before ``serve`` (the refusal is read-only
    and happens before the experiment boundary) — no attempt
    record, no workspace, no listener.  Returns the measured
    token."""
    with pytest.raises(fci.FixtureError) as excinfo:
        flocal.LocalFixtureOwner(
            paths["repo"],
            paths["work"],
            paths["evidence"],
            bind_head,
            paths["control"],
            git_runner=paths["git_runner"],
            executor=LocalFakeDocker(),
        )
    # a read-only refusal records NO attempt
    assert not os.path.exists(paths["repo"] / ".oap-local")
    return str(excinfo.value)


def test_optin_refusals_record_no_attempt(tmp_path: Path, monkeypatch: Any) -> None:
    # dirty worktree: the bound source must be clean
    paths = _setup(tmp_path / "a", monkeypatch, LocalFakeDocker(), dirty=b" M scripts/x.py\n")
    assert _optin_refusal(paths) == "local-worktree-dirty"
    # oap/active selects a different order: the literal active bytes
    # must select 017-s
    paths = _setup(tmp_path / "b", monkeypatch, LocalFakeDocker())
    (paths["repo"] / "oap" / "active").write_bytes(b"017-r\n")
    assert _optin_refusal(paths) == "local-active-mismatch"
    # head mismatch: the bound head is literal and must equal HEAD
    paths = _setup(tmp_path / "c", monkeypatch, LocalFakeDocker())
    assert _optin_refusal(paths, bind_head="e" * 40) == "local-head-mismatch"


def test_hosted_env_refused_before_any_mutation(tmp_path: Path, monkeypatch: Any) -> None:
    """The PRODUCTION hosted-env guard (not a test stand-in): the
    disposable hosted runner's ambient GITHUB_ACTIONS=true refuses
    the local owner at construction, before any attempt record,
    workspace, control root or docker call; the refusal is
    read-only and records nothing."""
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(flocal.FixtureError) as exc:
        flocal.LocalFixtureOwner(
            paths["repo"],
            paths["work"],
            paths["evidence"],
            HEAD,
            paths["control"],
            git_runner=paths["git_runner"],
            executor=fake,
        )
    assert str(exc.value) == "local-hosted-env"
    assert not os.path.exists(paths["repo"] / ".oap-local")
    assert not paths["work"].exists()
    assert not paths["control"].exists()
    assert fake.calls == []


def test_second_admitted_attempt_refused(tmp_path: Path, monkeypatch: Any) -> None:
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        _client(paths["control"], "prepare", run_id)
        _client(paths["control"], "abort", run_id)
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    # a fresh owner against the SAME repository (same activated S,
    # fresh work/control/evidence so the refusal is specifically the
    # one-attempt law, not the no-pre-existing-evidence rule) is
    # refused before any mutation: the one attempt is already
    # recorded (aborted)
    second = {
        "work": tmp_path / "work2",
        "control": tmp_path / "control2",
        "evidence": tmp_path / "evidence2" / "local-evidence.json",
    }
    (second["evidence"].parent).mkdir(parents=True)
    with pytest.raises(fci.FixtureError, match="local-attempt-exhausted"):
        flocal.LocalFixtureOwner(
            paths["repo"],
            second["work"],
            second["evidence"],
            HEAD,
            second["control"],
            git_runner=paths["git_runner"],
            executor=LocalFakeDocker(),
        )
    admission = json.loads((paths["repo"] / ".oap-local" / "017-s" / "admission.json").read_bytes())
    assert len(admission["attempts"]) == 1


def test_stale_claim_reclaimed_exactly_once(tmp_path: Path, monkeypatch: Any) -> None:
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    # simulate a crash between the terminal record and the claim
    # release: the terminal record exists and the owned claim file
    # still carries that run id (the ONE attempt is already
    # consumed by the terminal record)
    run_id = "c" * 32
    admit_root = paths["repo"] / ".oap-local"
    admit_dir = paths["repo"] / ".oap-local" / "017-s"
    admit_root.mkdir(parents=True)
    admit_dir.mkdir(parents=True)
    # BOTH owned ancestor components must be exactly 0700 for the
    # protected admission surface
    os.chmod(admit_root, 0o700)
    os.chmod(admit_dir, 0o700)
    (admit_dir / "admission.json").write_text(
        json.dumps(
            {
                "record": flocal.ADMISSION_SCHEMA,
                "order": flocal.ORDER_ID,
                "attempts": [{"head": HEAD, "run_id": run_id, "status": "fail"}],
            }
        )
        + "\n"
    )
    os.chmod(admit_dir / "admission.json", 0o600)
    (admit_dir / "admission.claim").write_text(run_id)
    os.chmod(admit_dir / "admission.claim", 0o600)
    # the stale claim is RECLAIMED exactly once, but the one
    # attempt was already consumed by the terminal record: the new
    # owner is refused before any mutation (and its own transient
    # claim is released again)
    with pytest.raises(fci.FixtureError, match="local-attempt-exhausted"):
        flocal.LocalFixtureOwner(
            paths["repo"],
            paths["work"],
            paths["evidence"],
            HEAD,
            paths["control"],
            git_runner=paths["git_runner"],
            executor=LocalFakeDocker(),
        )
    # exactly one reclaim: the stale claim file is gone
    assert not (admit_dir / "admission.claim").exists()
    admission = json.loads((admit_dir / "admission.json").read_bytes())
    assert admission["attempts"] == [{"head": HEAD, "run_id": run_id, "status": "fail"}]


# -- bounded reads and sealed launch ---------------------------------------------------
def test_git_hung_query_bounded_and_reaped(tmp_path: Path, monkeypatch: Any) -> None:
    monkeypatch.setattr(flocal, "_GIT_TIMEOUT_SECONDS", 1.0)
    killed: list[bool] = []

    # a git child that emits NOTHING and never exits: the read must
    # be time-bounded, the child killed and reaped, the stream closed
    class _SilentStream:
        def __init__(self) -> None:
            # the READ end of a pipe whose write end is held open:
            # select never marks it ready and no EOF arrives
            self._r, self._w = os.pipe()

        def close(self) -> None:
            for fd in (self._r, self._w):
                try:
                    os.close(fd)
                except OSError:
                    pass

        def fileno(self) -> int:
            return self._r

    class _SilentProc:
        def __init__(self) -> None:
            self.stdout = _SilentStream()
            self.returncode = None

        def kill(self) -> None:
            killed.append(True)

        def wait(self, timeout: float | None = None) -> int:
            return 0

    monkeypatch.setattr(flocal.subprocess, "Popen", lambda *a, **k: _SilentProc())
    with pytest.raises(fci.FixtureError, match="local-git-timeout"):
        flocal._git_default(["rev-parse", "HEAD"], tmp_path)
    assert killed, "the hung child must be killed"


def test_git_overbound_output_killed(tmp_path: Path, monkeypatch: Any) -> None:
    monkeypatch.setattr(flocal, "_GIT_OUTPUT_MAX", 64)
    killed: list[bool] = []

    class _BigStream:
        def __init__(self) -> None:
            self._r, self._w = os.pipe()
            os.write(self._w, b"y" * 256)
            os.close(self._w)

        def fileno(self) -> int:
            return self._r

        def close(self) -> None:
            try:
                os.close(self._r)
            except OSError:
                pass

    class _BigProc:
        def __init__(self) -> None:
            self.stdout = _BigStream()
            self.returncode = None

        def kill(self) -> None:
            killed.append(True)

        def wait(self, timeout: float | None = None) -> int:
            return 0

    monkeypatch.setattr(flocal.subprocess, "Popen", lambda *a, **k: _BigProc())
    with pytest.raises(fci.FixtureError, match="local-git-output-overbound"):
        flocal._git_default(["rev-parse", "HEAD"], tmp_path)
    assert killed, "the overbound child must be killed"


def test_read_bounded_rejects_over_cap(tmp_path: Path) -> None:
    path = tmp_path / "f"
    path.write_bytes(b"z" * 100)
    assert flocal._read_bounded(path, 100) == b"z" * 100
    with pytest.raises(fci.FixtureError, match="local-admission-malformed"):
        flocal._read_bounded(path, 99)


def test_owner_argv_sealed() -> None:
    argv = flocal._owner_argv("/m", "e" * 40, "/r", "/w", "/c", "/e")
    assert argv == [
        sys.executable,
        "/m",
        "owner",
        "--order",
        "017-s",
        "--bind-head",
        "e" * 40,
        "--repo",
        "/r",
        "--work",
        "/w",
        "--control-dir",
        "/c",
        "--evidence-out",
        "/e",
    ]


def test_no_bare_pid_signalling_static() -> None:
    source = LOCAL_PATH.read_text()
    for forbidden in ("os.kill(", "os.killpg(", "signal.pthread_kill", "os.getpgrp()"):
        assert forbidden not in source, f"forbidden host signalling form: {forbidden}"
    # exactly ONE anchor constant and ONE bounded cleanup grace use
    assert source.count("CLEANUP_GRACE_SECONDS,") >= 1
    assert "add_grace(" in source
    assert source.count("add_grace(") == 1


def test_state_object_closed_schema(tmp_path: Path) -> None:
    run_id = "d" * 32
    good = {
        "record": flocal.STATE_SCHEMA,
        "run_id": run_id,
        "pid": 1234,
        "end_anchor": 1234.5,
        "phase": "start",
        "status": "running",
        "containers": [],
        "create_intent": None,
        "image_id": None,
        "build_attempted": False,
        "env_file": None,
        "ledger": flocal._ledger_facts(fci._RunLedger(model.FixtureBudgets())),
    }
    flocal._validate_state_object(good, run_id)
    bad_status = dict(good, status="a" * 64)
    with pytest.raises(fci.FixtureError, match="local-state-malformed"):
        flocal._validate_state_object(bad_status, run_id)
    bad_intent = dict(good, create_intent="slaif-fixture-017s-recovery-1-0-abcdef12")
    with pytest.raises(fci.FixtureError, match="local-state-malformed"):
        flocal._validate_state_object(bad_intent, run_id)
    good_intent = dict(
        good,
        create_intent="slaif-fixture-017s-prepared-12345-0-abcdef12",
    )
    flocal._validate_state_object(good_intent, run_id)
    bad_anchor = dict(good, end_anchor=-1)
    with pytest.raises(fci.FixtureError, match="local-state-malformed"):
        flocal._validate_state_object(bad_anchor, run_id)


# -- review10 item6: the generic finish variants (no mandatory
# python consume) through the PROTECTED control interface -------
def test_finish_unobserved_variant_composition(tmp_path: Path, monkeypatch: Any) -> None:
    """prepare -> finish with NO rehearse: the held instance is
    finished while its one-shot diagnostic was never consumed.  The
    retained record is a truthful unobserved variant: no consume
    phase, finished-unconsumed disposition, the controller ledger
    is exactly the two exporter commands, and the host ledger
    charged nothing but those two requests."""
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        prepared = _client(paths["control"], "prepare", run_id)
        assert prepared["ok"] is True
        final = _client(paths["control"], "finish", run_id)
        assert final["ok"] is True
        detail = final["detail"]
        assert detail["outcome"] == "pass"
        assert detail["stage"] == "publish"
        assert detail["control_dir_retained"] is False
        assert detail["evidence_sha256"] is not None
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 0
    evidence = _read_evidence(paths["evidence"])
    assert evidence["status"] == "pass"
    assert evidence["fixture_consumed_by"] == "unobserved"
    assert evidence["prepared"]["disposition"] == "finished-unconsumed"
    # NO consume phase: the variant key set is prepare + finish only
    assert set(evidence["phases"]) == {"prepare", "finish"}
    finish = evidence["phases"]["finish"]
    assert finish["observed_at_position"] is None
    assert finish["controller_ledger_requests"] == 2
    assert finish["observed_at_finish"] == {
        "scenario": "diagnostic",
        "wire_requests": 0,
        "diagnostic_state": "unobserved",
    }
    # The retained payload ITSELF is the unobserved closed record
    selected = json.loads(base64.b64decode(evidence["export"]["payload_b64"]))
    assert selected["diagnostic"] == {"state": "unobserved"}
    assert selected["observed_at_position"] is None
    assert selected["snapshot"]["issued_calls"] == []
    assert selected["snapshot"]["controller_ledger"]["requests"] == 2
    # The host ledger: exactly the two exporter commands, nothing
    # consumed, no model traffic
    assert evidence["ledger"]["api_requests"] == 2
    assert evidence["ledger"]["api_attempts"] == 2
    assert evidence["ledger"]["requests_admitted"] == 2
    assert evidence["ledger"]["requests_refused"] == 0
    # Verified clean convergence: the control root is destroyed
    assert not paths["control"].exists()


def _external_diagnostic() -> dict[str, Any]:
    # A DISTINCT closed metadata diagnostic: the subject's own
    # tool-bearing request through the actual R single-source
    # derivation — never the python rehearsal's empty-tools
    # metadata.
    value: dict[str, Any] = model.bounds_diagnostic(
        fixture_standin._fixed_request(fixture_standin._synthetic_tools())
    )
    return value


def test_finish_external_variant_composition(tmp_path: Path, monkeypatch: Any) -> None:
    """A SEPARATE principal held the instance and consumed the
    one-shot diagnostic (a tool-bearing request) before finish.
    The owner's python rehearse never ran; finish still completes
    the SAME interface from the ACTUAL closed controller
    observation, and the retained record is the truthful external
    variant (own request-derived metadata diagnostic, measured
    causal position, controller ledger = wire + 2)."""
    external_state = {
        "scenario": "diagnostic",
        "wire_requests": 3,
        "diagnostic_state": "observed",
    }
    fresh_state = {
        "scenario": "diagnostic",
        "wire_requests": 0,
        "diagnostic_state": "unobserved",
    }
    fake = LocalFakeDocker(
        observe_states=[fresh_state, external_state],
        export_state=external_state,
        export_diagnostic=_external_diagnostic(),
        diagnostic_position=2,
    )
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        prepared = _client(paths["control"], "prepare", run_id)
        assert prepared["ok"] is True
        # prepare's own observation is the FRESH controller state
        assert prepared["detail"]["observed"] == fresh_state
        final = _client(paths["control"], "finish", run_id)
        assert final["ok"] is True
        detail = final["detail"]
        assert detail["outcome"] == "pass"
        assert detail["stage"] == "publish"
        assert detail["control_dir_retained"] is False
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 0
    evidence = _read_evidence(paths["evidence"])
    assert evidence["status"] == "pass"
    assert evidence["fixture_consumed_by"] == "external"
    assert evidence["prepared"]["disposition"] == "consumed-by-external-subject"
    assert set(evidence["phases"]) == {"prepare", "finish"}
    finish = evidence["phases"]["finish"]
    assert finish["observed_at_position"] == 2
    assert finish["controller_ledger_requests"] == 5
    assert finish["observed_at_finish"] == external_state
    # The retained payload is the subject's OWN closed diagnostic at
    # its measured position — distinct from the python metadata
    selected = json.loads(base64.b64decode(evidence["export"]["payload_b64"]))
    assert selected["diagnostic"] == _external_diagnostic()
    assert selected["diagnostic"] != model.bounds_diagnostic(fixture_standin._fixed_request([]))
    assert selected["observed_at_position"] == 2
    assert selected["snapshot"]["controller_ledger"]["requests"] == 5


def test_finish_forged_export_identity_mismatch(tmp_path: Path, monkeypatch: Any) -> None:
    """A closed-but-INCONSISTENT export payload (controller ledger
    below the observed wire) is refused by the measured identity
    gate: primary failure preserved, no pass, control retained."""
    external_state = {
        "scenario": "diagnostic",
        "wire_requests": 3,
        "diagnostic_state": "observed",
    }
    fresh_state = {
        "scenario": "diagnostic",
        "wire_requests": 0,
        "diagnostic_state": "unobserved",
    }
    forged = json.loads(_local_selected_payload(3, position=2, diagnostic=_external_diagnostic()))
    forged["snapshot"]["controller_ledger"]["requests"] = 2  # < observed wire 3
    forged_bytes = json.dumps(forged, sort_keys=True, separators=(",", ":")).encode()
    fake = LocalFakeDocker(
        observe_states=[fresh_state, external_state],
        export_state=external_state,
        export_diagnostic=_external_diagnostic(),
        diagnostic_position=2,
        export_payload=forged_bytes,
    )
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        assert _client(paths["control"], "prepare", run_id)["ok"] is True
        final = _client(paths["control"], "finish", run_id)
        assert final["ok"] is True
        detail = final["detail"]
        assert detail["outcome"] == "fail"
        assert detail["stage"] == "finish"
        # The primary failure is NOT unverified cleanup: the exact
        # owned cleanup converged (verified), so the control root is
        # destroyed and the retained FAIL EVIDENCE carries the
        # registry (retention follows unverified cleanup, never a
        # primary failure alone).
        assert detail["control_dir_retained"] is False
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 1
    evidence = _read_evidence(paths["evidence"])
    assert evidence["status"] == "fail"
    assert evidence["reason"] == "export-identity-mismatch"
    assert evidence["stage"] == "finish"
    assert evidence["recovery_state_retained"] is False
    assert not paths["control"].exists()
    # the registry is carried by the retained evidence itself
    assert len(evidence["resources"]["containers"]) == 1
    assert evidence["resources"]["image_id"] == IMAGE_ID


def test_pass_evidence_summary_bound_to_payload(tmp_path: Path, monkeypatch: Any) -> None:
    """The outer FINISH summary and the retained payload are ONE
    measurement: a summary field that disagrees with the DECODED
    snapshot/position, a wrong variant disposition, a wrong variant
    label, or a cross-variant payload can never validate as pass
    (separate range laws do not establish summary == payload)."""
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        assert _client(paths["control"], "prepare", run_id)["ok"] is True
        assert _client(paths["control"], "finish", run_id)["detail"]["outcome"] == "pass"
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    valid = _read_evidence(paths["evidence"])
    assert valid["fixture_consumed_by"] == "unobserved"

    def tampered(mutate: Any) -> None:
        record = copy.deepcopy(valid)
        mutate(record)
        with pytest.raises(flocal.FixtureError, match="local-evidence-invalid"):
            flocal.validate_local_evidence(record)

    # (a) summary position != decoded payload position (None)
    tampered(lambda r: r["phases"]["finish"].__setitem__("observed_at_position", 0))
    # (b) summary ledger != decoded payload ledger (2): the value 3
    #     still passes the generic range law (>= 2, >= wire 0) —
    #     only the decoded binding rejects it
    tampered(lambda r: r["phases"]["finish"].__setitem__("controller_ledger_requests", 3))
    # (c) the python-rehearsal disposition on an unobserved record
    tampered(lambda r: r["prepared"].__setitem__("disposition", "consumed-by-python-rehearsal"))
    # (d) the external variant label on an unobserved observation
    tampered(lambda r: r.__setitem__("fixture_consumed_by", "external"))
    # (e) a python-variant payload (fixed metadata, position 0,
    #     ledger 5) embedded in an unobserved record: the payload
    #     law against the measured wire (0) and the summary binding
    #     both reject it
    python_payload = _local_selected_payload(3)

    def swap_payload(r: dict[str, Any]) -> None:
        digest = hashlib.sha256(python_payload).hexdigest()
        r["export"]["sha256"] = digest
        r["export"]["bytes"] = len(python_payload)
        r["export"]["payload_b64"] = base64.b64encode(python_payload).decode("ascii")
        r["phases"]["finish"]["export_sha256"] = digest
        r["phases"]["finish"]["retained_capture_bytes"] = len(python_payload)

    tampered(swap_payload)


# -- review10: the public control client's closed surface ----------
def _stub_control_root(base: Path, name: str) -> Path:
    root = base / name
    root.mkdir(parents=True)
    os.chmod(str(root), 0o700)
    return root


def _stub_control_response(command: str, run_id: str) -> dict[str, Any]:
    details = {
        "prepare": {
            "cid": "a" * 64,
            "state": "prepared-unconsumed",
            "observed": {
                "scenario": "diagnostic",
                "wire_requests": 0,
                "diagnostic_state": "unobserved",
            },
            "end_anchor": 1234.5,
        },
        "observe": {
            "scenario": "diagnostic",
            "wire_requests": 0,
            "diagnostic_state": "unobserved",
            "raw_content_retained": False,
        },
    }
    return {
        "record": flocal.CONTROL_RECORD,
        "ok": True,
        "command": command,
        "run_id": run_id,
        "reason": None,
        "detail": details[command],
    }


def _listen_once(
    root: Path, handler: Any, budget: float = 10.0
) -> tuple[threading.Thread, threading.Event]:
    """ONE accepted connection on the protected root, driven by the
    handler over the real (loopback) socket under a FINITE fixture
    budget: the accept and every handler read are deadline-bounded
    (the thread always self-terminates), and the readiness event is
    set ONLY AFTER listen() — a client can never connect before the
    listener is actually ready.  Returns (thread, ready); the
    caller joins the thread (bounded) in a finally so neither a
    passing nor a failing test leaves a live listener."""
    ready = threading.Event()

    def run() -> None:
        listener: socket.socket | None = None
        try:
            listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            listener.bind(str(root / flocal._CONTROL_SOCK_NAME))
            os.chmod(str(root / flocal._CONTROL_SOCK_NAME), 0o600)
            listener.listen(1)
            ready.set()
            listener.settimeout(budget)
            conn, _ = listener.accept()
            conn.settimeout(budget)
            try:
                handler(conn)
            finally:
                conn.close()
        except OSError:
            pass
        finally:
            if listener is not None:
                listener.close()
            # unlink the socket path the fixture bound (owned root)
            try:
                os.unlink(str(root / flocal._CONTROL_SOCK_NAME))
            except OSError:
                pass

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread, ready


def _read_request_line(conn: socket.socket) -> dict[str, Any]:
    data = b""
    while b"\n" not in data:
        chunk = conn.recv(65536)
        if not chunk:
            raise OSError("peer closed")
        data += chunk
        if len(data) > 8192:
            raise OSError("overbound request")
    request: dict[str, Any] = json.loads(data.decode("ascii"))
    return request


def test_control_client_refuses_untrusted_socket_modes(tmp_path: Path) -> None:
    run_id = "c" * 32
    name = flocal._CONTROL_SOCK_NAME
    # (1) a write-only (0200) socket: the declared producer
    #     contract is exactly 0600 — never a loose or write-only
    #     mode.
    root = _stub_control_root(tmp_path, "m0200")
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    listener.bind(str(root / name))
    os.chmod(str(root / name), 0o200)
    with pytest.raises(flocal.FixtureError, match="local-control-socket-untrusted"):
        flocal._control_client(root, "observe", run_id, 5.0)
    listener.close()
    # (2) a symlinked socket: a link is never the socket.
    real = tmp_path / "real.sock"
    realsock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    realsock.bind(str(real))
    os.chmod(str(real), 0o600)
    root2 = _stub_control_root(tmp_path, "mlink")
    os.symlink(str(real), str(root2 / name))
    with pytest.raises(flocal.FixtureError, match="local-control-socket-untrusted"):
        flocal._control_client(root2, "observe", run_id, 5.0)
    realsock.close()
    # (3) a group/world-accessible (0755) control root.
    root3 = _stub_control_root(tmp_path, "m0755")
    listener3 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    listener3.bind(str(root3 / name))
    os.chmod(str(root3 / name), 0o600)
    os.chmod(str(root3), 0o755)
    with pytest.raises(flocal.FixtureError, match="local-control-socket-untrusted"):
        flocal._control_client(root3, "observe", run_id, 5.0)
    listener3.close()


def test_control_client_refuses_foreign_run_id(tmp_path: Path) -> None:
    run_id = "c" * 32
    root = _stub_control_root(tmp_path, "runid")

    def handler(conn: socket.socket) -> None:
        request = _read_request_line(conn)
        # a DIFFERENT valid 32-hex identity is not an answer to
        # this command
        response = _stub_control_response(request["command"], "d" * 32)
        conn.sendall((json.dumps(response, sort_keys=True, separators=(",", ":")) + "\n").encode())

    thread, ready = _listen_once(root, handler)
    try:
        assert ready.wait(5.0), "stub listener never became ready"
        with pytest.raises(flocal.FixtureError, match="local-control-protocol"):
            flocal._control_client(root, "observe", run_id, 10.0)
    finally:
        thread.join(12.0)


def test_control_client_absolute_budget_stops_slow_drip(tmp_path: Path) -> None:
    run_id = "c" * 32
    root = _stub_control_root(tmp_path, "drip")

    def handler(conn: socket.socket) -> None:
        _read_request_line(conn)
        payload = (
            json.dumps(
                _stub_control_response("observe", run_id), sort_keys=True, separators=(",", ":")
            )
            + "\n"
        ).encode()
        for offset in range(len(payload)):
            conn.sendall(payload[offset : offset + 1])
            time.sleep(0.3)

    thread, ready = _listen_once(root, handler, budget=15.0)
    try:
        assert ready.wait(5.0), "stub listener never became ready"
        start = time.monotonic()
        with pytest.raises(flocal.FixtureError, match="local-control-protocol"):
            flocal._control_client(root, "observe", run_id, 1.0)
        elapsed = time.monotonic() - start
        # ONE absolute remaining budget: the command is refused at
        # the ~1.0s deadline, never stretched byte-by-byte (the
        # full drip would take tens of seconds)
        assert elapsed < 3.0
    finally:
        thread.join(17.0)


def test_control_client_refuses_infinite_anchor(tmp_path: Path) -> None:
    run_id = "c" * 32
    root = _stub_control_root(tmp_path, "anchor")

    def handler(conn: socket.socket) -> None:
        _read_request_line(conn)
        response = _stub_control_response("prepare", run_id)
        response["detail"] = dict(response["detail"])
        response["detail"]["end_anchor"] = float("inf")  # serializes as Infinity
        conn.sendall((json.dumps(response, sort_keys=True, separators=(",", ":")) + "\n").encode())

    thread, ready = _listen_once(root, handler)
    try:
        assert ready.wait(5.0), "stub listener never became ready"
        with pytest.raises(flocal.FixtureError, match="local-control-protocol"):
            flocal._control_client(root, "prepare", run_id, 10.0)
    finally:
        thread.join(12.0)


# -- review10: owner terminal failure matrix (fake Docker only) ---
def test_control_root_destroy_failure_forbids_pass(tmp_path: Path, monkeypatch: Any) -> None:
    """An UNVERIFIED control-root destruction is a measured cleanup
    failure: it forbids the pass BEFORE any publication, retains
    the protected registry/ledger, and records the admitted
    attempt as fail — never a pass that later disappears."""
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    real_destroy = fci._destroy_owned_work_root

    def gated_destroy(path: object, *args: Any, **kwargs: Any) -> bool:
        if str(path) == str(paths["control"]):
            return False
        result: bool = real_destroy(path, *args, **kwargs)
        return result

    monkeypatch.setattr(fci, "_destroy_owned_work_root", gated_destroy)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        assert _client(paths["control"], "prepare", run_id)["ok"] is True
        assert _client(paths["control"], "observe", run_id)["ok"] is True
        assert _client(paths["control"], "rehearse", run_id)["ok"] is True
        final = _client(paths["control"], "finish", run_id)
        assert final["ok"] is True
        detail = final["detail"]
        assert detail["outcome"] == "fail"
        assert detail["stage"] == "cleanup"
        assert detail["control_dir_retained"] is True
        assert detail["evidence_sha256"] is not None
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 1
    evidence = _read_evidence(paths["evidence"])
    assert evidence["status"] == "fail"
    assert evidence["reason"] == "cleanup-incomplete"
    assert evidence["stage"] == "cleanup"
    assert "control-cleanup-unverified" in evidence["cleanup_failures"]
    assert evidence["recovery_state_retained"] is True
    # the retained protected control root survives for the
    # separately-authorized recovery
    assert paths["control"].is_dir()
    # the admitted attempt is recorded fail, never pass
    admission = flocal._read_admission(flocal._admission_path(paths["repo"]))
    assert [a["status"] for a in admission["attempts"] if a["run_id"] == run_id] == ["fail"]


def test_create_gap_retains_unverified_intent(tmp_path: Path, monkeypatch: Any) -> None:
    """The create/response gap: the exact fresh create intent was
    persisted, the CID response was lost, and a ps discovery under
    the exact name finds an object.  Name discovery is a QUERY, not
    attestation: the object is NEVER removed, the intent is
    retained, and the image cleanup still converges."""
    fake = LocalFakeDocker(create_fail_rc=1)
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        prepared = _client(paths["control"], "prepare", run_id)
        assert prepared["ok"] is False
        assert prepared["reason"] == "create-failed"
        assert prepared["detail"] is None
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 1
    evidence = _read_evidence(paths["evidence"])
    assert evidence["status"] == "fail"
    assert evidence["reason"] == "create-failed"
    assert evidence["stage"] == "prepare-target"
    assert "container-cleanup-unverified" in evidence["cleanup_failures"]
    resources = evidence["resources"]
    assert resources["containers"] == []
    assert resources["create_intent"] is not None
    assert fci._LOCAL_NAME_RE.fullmatch(resources["create_intent"])
    assert resources["build_attempted"] is True
    assert resources["image_id"] == IMAGE_ID
    assert evidence["recovery_state_retained"] is True
    # NO unattested CID was ever removed: the discovered object
    # stays for the separately-authorized recovery
    assert fake.removed == set()
    assert len(fake.by_name) == 1
    # the image cleanup still ran exactly once and verified absent
    assert fake.image_removed is True
    assert fake.rmi_calls == [IMAGE_ID]


# -- section 2: verified local Docker endpoint binding --------------------------
def test_local_endpoint_selection_refused_before_mutation(tmp_path: Path, monkeypatch: Any) -> None:
    """An explicit remote selection (DOCKER_HOST or a foreign
    DOCKER_CONTEXT) refuses BEFORE any mutation: no docker command,
    no scratch/control root, the closed reason, and no echo of the
    selected value."""
    cases = (
        {"DOCKER_HOST": "tcp://127.0.0.1:2375"},
        {"DOCKER_HOST": "unix:///var/run/remote-docker.sock"},
        {"DOCKER_CONTEXT": "remote-ctx"},
    )
    for index, selection in enumerate(cases):
        fake = LocalFakeDocker()
        paths = _setup(tmp_path / f"sel{index}", monkeypatch, fake)
        for var, value in selection.items():
            monkeypatch.setenv(var, value)
        owner = flocal.LocalFixtureOwner(
            paths["repo"],
            paths["work"],
            paths["evidence"],
            HEAD,
            paths["control"],
            git_runner=paths["git_runner"],
            executor=fake,
        )
        with pytest.raises(flocal.FixtureError) as exc:
            owner.prepare()
        assert str(exc.value) == "local-docker-endpoint"
        # refused BEFORE any mutation: no docker call, no roots
        assert fake.calls == []
        assert not paths["work"].exists()
        for var in selection:
            monkeypatch.delenv(var)


def test_local_endpoint_default_context_admitted(tmp_path: Path, monkeypatch: Any) -> None:
    """The daemon's own ``default`` context is this host's endpoint
    and is admitted: the read-only daemon-name corroboration
    (through the pinned bound executor) is the FIRST docker action
    of the run, after the socket proof and before any mutation."""
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    # AFTER _setup (which delenvs the selector vars): the daemon's
    # own default context is the selection actually exercised here
    monkeypatch.setenv("DOCKER_CONTEXT", "default")
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        prepared = _client(paths["control"], "prepare", run_id)
        assert prepared["ok"] is True
        _client(paths["control"], "abort", run_id)
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 130
    assert fake.calls[0] == ["docker", "info", "--format", "{{.Name}}"]


def test_local_daemon_identity_refused_closed(tmp_path: Path, monkeypatch: Any) -> None:
    """A foreign daemon name (the daemon behind the pinned socket is
    NOT this host) is a closed refusal: only the read-only name query
    ran, nothing was mutated, and the fail evidence carries the
    closed reason with the measured one admission."""
    fake = LocalFakeDocker(daemon_name="foreign-host")
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        prepared = _client(paths["control"], "prepare", run_id)
        assert prepared["ok"] is False
        assert prepared["reason"] == "local-docker-endpoint"
        assert prepared["detail"] is None
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 1
    assert fake.calls == [["docker", "info", "--format", "{{.Name}}"]]
    assert not paths["work"].exists()
    evidence = _read_evidence(paths["evidence"])
    assert evidence["status"] == "fail"
    assert evidence["reason"] == "local-docker-endpoint"
    assert evidence["stage"] == "start"
    assert evidence["ledger"]["docker_admissions"] == 1


def test_local_socket_unknown_refused_before_docker(tmp_path: Path, monkeypatch: Any) -> None:
    """The narrow local unix socket must EXIST read-only as a socket
    file: a missing path or a regular file there refuses BEFORE any
    docker command runs (the lstat proof precedes the daemon query).
    Each case gets a fresh repository (the one-attempt law)."""
    for index, state in enumerate(("missing", "regular-file")):
        fake = LocalFakeDocker()
        paths = _setup(tmp_path / f"sock{index}", monkeypatch, fake)
        # a path distinct from the hermetic socket _setup already
        # bound: "missing" stays absent, the other is a regular file
        sock_path = tmp_path / f"sock{index}" / "verified.sock"
        if state == "regular-file":
            sock_path.write_bytes(b"not-a-socket")
        monkeypatch.setattr(flocal, "_LOCAL_DOCKER_SOCKET", str(sock_path))
        owner, thread, run_id = _start_owner(paths, fake)
        try:
            prepared = _client(paths["control"], "prepare", run_id)
            assert prepared["ok"] is False
            assert prepared["reason"] == "local-docker-endpoint"
        finally:
            _join(thread, control=paths["control"], run_id=run_id)
        assert owner._exit_code == 1
        assert fake.calls == []
        assert not paths["work"].exists()


def test_local_bound_executor_freezes_env_once_per_owner(monkeypatch: Any) -> None:
    """The child environment is snapshotted ONCE per owner (at the
    factory call): DOCKER_HOST is pinned to the verified local
    socket, the overriding context selection is removed, and a later
    HOME/DOCKER_CONFIG/DOCKER_CONTEXT drift cannot reach a later
    child (no per-call rebuild).  No real executor runs."""
    captured: dict[str, object] = {}

    def fake_real_execute(
        argv: list[str], timeout: float, pty: bool = False, env: dict[str, str] | None = None
    ) -> Any:
        captured["argv"] = argv
        captured["env"] = env
        return fci.ExecResult(0, b"", 0)

    monkeypatch.setenv("PATH", "/usr/bin:/bin")
    monkeypatch.setattr(fci, "_real_execute", fake_real_execute)
    bound = flocal._local_bound_executor()
    bound(["docker", "info"], 5.0)
    env = captured["env"]
    assert isinstance(env, dict)
    assert env["DOCKER_HOST"] == flocal._LOCAL_DOCKER_ENDPOINT_PIN
    assert "DOCKER_CONTEXT" not in env
    assert env["PATH"] == "/usr/bin:/bin"
    # drift AFTER the once-per-owner snapshot: the SAME frozen
    # mapping still reaches the next child
    monkeypatch.setenv("DOCKER_CONTEXT", "remote-ctx")
    monkeypatch.setenv("HOME", "/tmp/drift")
    monkeypatch.setenv("DOCKER_CONFIG", "/tmp/drift/config")
    bound(["docker", "info"], 5.0)
    assert captured["env"] is env
    assert "DOCKER_CONTEXT" not in env
    assert env["PATH"] == "/usr/bin:/bin"


def _subject_facts_canonical() -> dict[str, Any]:
    base = _exec_measurement_record()
    return {key: base[key] for key in flocal._SUBJECT_FACT_KEYS}


def test_validate_subject_facts_closed_contract() -> None:
    """The curated subject facts are REVALIDATED against the
    approved R model contract: the measured canonical subset
    passes, and every forged identity/limit/mount/table fact is
    refused with the closed token."""
    canonical = _subject_facts_canonical()
    flocal._validate_subject_facts(canonical)  # the measured subset passes

    def reject(mutate: Any) -> None:
        facts = copy.deepcopy(canonical)
        mutate(facts)
        with pytest.raises(flocal.FixtureError, match="local-evidence-invalid"):
            flocal._validate_subject_facts(facts)

    reject(lambda f: f.__setitem__("uid", 21002.0))  # float uid
    reject(lambda f: f.__setitem__("gid", fci.CONTROLLER_UID))  # wrong gid
    reject(lambda f: f.__setitem__("groups", [21002.0]))  # float group
    reject(lambda f: f.__setitem__("groups", [0]))  # root group
    reject(lambda f: f.__setitem__("groups", [fci.SUBJECT_UID, fci.SUBJECT_UID]))  # duplicate
    reject(lambda f: f.__setitem__("groups", "21002"))  # not a list
    reject(
        lambda f: f.__setitem__("keyring_errno", {"add_key": 0, "request_key": 1, "keyctl": 1})
    )  # success errno
    reject(lambda f: f.__setitem__("memory_limit_bytes", 0))
    reject(lambda f: f.__setitem__("pids_limit", 0))
    reject(lambda f: f.__setitem__("cpu_limit", True))  # bool limit
    reject(lambda f: f.__setitem__("swap_source", "bogus-source"))

    def drop_mount(f: dict[str, Any]) -> None:
        f["writable_mounts"] = [m for m in f["writable_mounts"] if m["root"] != "/tmp"]

    reject(drop_mount)  # missing required root

    def foreign_mount(f: dict[str, Any]) -> None:
        f["writable_mounts"] = f["writable_mounts"] + [
            {
                "root": "/mnt",
                "size_bytes": 64 * 1024 * 1024,
                "uid": fci.SUBJECT_UID,
                "gid": fci.SUBJECT_UID,
                "mode": 0o700,
            }
        ]

    reject(foreign_mount)  # unconfigured root

    def dup_mount(f: dict[str, Any]) -> None:
        f["writable_mounts"] = f["writable_mounts"] + [
            {
                "root": "/tmp",
                "size_bytes": 64 * 1024 * 1024,
                "uid": fci.SUBJECT_UID,
                "gid": fci.SUBJECT_UID,
                "mode": 0o1777,
            }
        ]

    reject(dup_mount)  # duplicate root

    def shm_oversize(f: dict[str, Any]) -> None:
        for m in f["writable_mounts"]:
            if m["root"] == "/dev/shm":
                m["size_bytes"] = 128 * 1024 * 1024

    reject(shm_oversize)  # beyond the explicit SHM bound

    def ctl_wrong_size(f: dict[str, Any]) -> None:
        for m in f["writable_mounts"]:
            if m["root"] == "/run/slaif-ctl":
                m["size_bytes"] = 32 * 1024 * 1024

    reject(ctl_wrong_size)  # configured size mismatch

    def ctl_wrong_mode(f: dict[str, Any]) -> None:
        for m in f["writable_mounts"]:
            if m["root"] == "/run/slaif-ctl":
                m["mode"] = 0o755

    reject(ctl_wrong_mode)  # closed mode set

    def ctl_foreign_owner(f: dict[str, Any]) -> None:
        for m in f["writable_mounts"]:
            if m["root"] == "/run/slaif-ctl":
                m["uid"] = 0

    reject(ctl_foreign_owner)  # configured owner
    reject(lambda f: f.__setitem__("mounts_scanned", 0))  # empty table
    reject(lambda f: f.__setitem__("mounts_scanned", 513))  # scanner cap
    reject(lambda f: f.__setitem__("masked_null_aliases", 14))  # 4 + 14 > 13
    reject(lambda f: f.__setitem__("extra_key", 1))  # closed key set

    def drop_key(f: dict[str, Any]) -> None:
        f.pop("swap_source")

    reject(drop_key)
    # the group variant law's POSITIVE: the own primary gid admits
    own = copy.deepcopy(canonical)
    own["groups"] = [fci.SUBJECT_UID]
    flocal._validate_subject_facts(own)


# -- review10: the thin rehearsal driver's closed boundaries -------
class _FakeDriverStream:
    def __init__(self, chunks: int = 0, eof: bool = True) -> None:
        self._chunks = chunks
        self._eof = eof
        self.closed = False

    def read(self, n: int) -> bytes:
        if self._eof and self._chunks <= 0:
            return b""
        if self._chunks > 0:
            self._chunks -= 1
        return b"x" * min(n, 65536)

    def close(self) -> None:
        self.closed = True


class _FakeDriverProc:
    def __init__(
        self,
        pid: int,
        poll_rc: int | None,
        wait_rc: int = 0,
        wait_timeout: bool = False,
        stream: Any = None,
        poll_sequence: list[int | None] | None = None,
    ) -> None:
        self.pid = pid
        self.returncode = poll_rc
        self._poll_rc = poll_rc
        self._wait_rc = wait_rc
        self._wait_timeout = wait_timeout
        self._poll_seq = poll_sequence
        self._poll_i = 0
        self.stdout = stream if stream is not None else _FakeDriverStream()
        self.wait_calls: list[float | None] = []

    def poll(self) -> int | None:
        if self._poll_seq is not None:
            idx = min(self._poll_i, len(self._poll_seq) - 1)
            self._poll_i += 1
            return self._poll_seq[idx]
        return self._poll_rc

    def wait(self, timeout: float | None = None) -> int | None:
        self.wait_calls.append(timeout)
        if self._wait_timeout:
            assert timeout is not None
            raise subprocess.TimeoutExpired(cmd="owner", timeout=timeout)
        self.returncode = self._wait_rc
        return self._wait_rc


def _fake_owner_state(control: Path, run_id: str, end_anchor: float) -> None:
    state = {
        "record": flocal.STATE_SCHEMA,
        "run_id": run_id,
        "pid": os.getpid(),
        "end_anchor": end_anchor,
        "phase": "prepared",
        "status": "running",
        "containers": [],
        "create_intent": None,
        "image_id": None,
        "build_attempted": False,
        "env_file": None,
        "ledger": flocal._ledger_facts(fci._RunLedger(model.FixtureBudgets())),
    }
    path = control / flocal._CONTROL_STATE_NAME
    path.write_text(json.dumps(state, sort_keys=True) + "\n")
    os.chmod(str(path), 0o600)


def test_driver_same_session_refused(tmp_path: Path, monkeypatch: Any) -> None:
    """INDEPENDENCE is verified, never assumed: a child whose
    session equals the driver's session is a closed driver failure
    (the owner is never signalled; it keeps its own END)."""
    control = _stub_control_root(tmp_path, "driver-iso")
    evidence = tmp_path / "evidence" / "local-evidence.json"
    _fake_owner_state(control, "c" * 32, time.monotonic() + 100)
    proc = _FakeDriverProc(pid=os.getpid(), poll_rc=None)
    monkeypatch.setattr(flocal.subprocess, "Popen", lambda argv, **kw: proc)
    summary = flocal.run_local_rehearsal(
        tmp_path / "repo", "f" * 40, tmp_path / "work", control, evidence
    )
    assert summary["status"] == "fail"
    assert summary["reason"] == "local-driver-independence"
    assert summary["run_id"] == "c" * 32
    assert summary["owner_exit"] is None
    # the owner was never waited on or signalled
    assert proc.wait_calls == []


def test_driver_startup_wait_timeout_gives_up_closed(tmp_path: Path, monkeypatch: Any) -> None:
    """A startup that publishes no state and whose bounded reap
    EXPIRES is a closed driver failure: the still-running owner is
    left to its own finite END (never signalled, never waited past
    the closed reap budget)."""
    control = _stub_control_root(tmp_path, "driver-startup")
    evidence = tmp_path / "evidence" / "local-evidence.json"
    proc = _FakeDriverProc(pid=os.getpid() + 1, poll_rc=None, wait_timeout=True)
    monkeypatch.setattr(flocal.subprocess, "Popen", lambda argv, **kw: proc)
    monkeypatch.setattr(flocal, "_CONTROL_STARTUP_TIMEOUT", 0.3)
    summary = flocal.run_local_rehearsal(
        tmp_path / "repo", "f" * 40, tmp_path / "work", control, evidence
    )
    assert summary["status"] == "fail"
    assert summary["reason"] == "local-driver-startup"
    assert summary["run_id"] is None
    assert summary["owner_exit"] is None
    assert len(proc.wait_calls) == 1
    assert proc.wait_calls[0] == flocal._DRIVER_STARTUP_REAP_SECONDS
    assert proc.returncode is None


def test_driver_capture_cap_fault_forbids_pass(tmp_path: Path, monkeypatch: Any) -> None:
    """A capture that hits its TOTAL byte cap (the stream was not
    drained to EOF) is a fault: the final pass is gated off even
    though the owner exited 0."""
    control = _stub_control_root(tmp_path, "driver-cap")
    evidence = tmp_path / "evidence" / "local-evidence.json"
    _fake_owner_state(control, "e" * 32, time.monotonic() + 100)
    stream = _FakeDriverStream(chunks=(1 << 20) // 65536 + 8, eof=False)
    # The owner is ALIVE through the commands (poll None) and exits
    # 0 during the final wait.  PID 1 supplies a valid foreign
    # session identity for the driver's ACTUAL getsid check (the
    # host init is never in this test process's session) — nothing
    # is spawned.
    proc = _FakeDriverProc(pid=1, poll_rc=None, wait_rc=0, stream=stream)
    monkeypatch.setattr(flocal.subprocess, "Popen", lambda argv, **kw: proc)

    def fake_client(control_dir: Path, command: str, run_id: str, timeout: float) -> dict[str, Any]:
        return {
            "record": flocal.CONTROL_RECORD,
            "ok": True,
            "command": command,
            "run_id": run_id,
            "reason": None,
            "detail": {},
        }

    monkeypatch.setattr(flocal, "_control_client", fake_client)
    summary = flocal.run_local_rehearsal(
        tmp_path / "repo", "f" * 40, tmp_path / "work", control, evidence
    )
    assert summary["status"] == "fail"
    assert summary["reason"] == "local-driver-output"
    assert summary["run_id"] == "e" * 32
    assert summary["owner_exit"] == 0
    assert stream.closed is True


class _FakeClock:
    def __init__(self, now: float) -> None:
        self.now = now

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


def _driver_boundary_setup(
    tmp_path: Path, monkeypatch: Any, proc: _FakeDriverProc
) -> tuple[Path, Path]:
    """Shared fake-clock driver boundary: END 1100 + the real 600
    grace = patience 1700; each of the four commands consumes 200
    fake seconds, so the final wait begins at 1800 — the approved
    ONE END+grace anchor is ALREADY ELAPSED."""
    control = _stub_control_root(tmp_path, "driver-boundary")
    evidence = tmp_path / "evidence" / "local-evidence.json"
    _fake_owner_state(control, "b" * 32, 1100.0)
    clock = _FakeClock(now=1000.0)
    monkeypatch.setattr(flocal.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(flocal.time, "sleep", clock.sleep)
    monkeypatch.setattr(flocal.subprocess, "Popen", lambda argv, **kw: proc)

    def fake_client(control_dir: Path, command: str, run_id: str, timeout: float) -> dict[str, Any]:
        clock.now += 200.0
        return {
            "record": flocal.CONTROL_RECORD,
            "ok": True,
            "command": command,
            "run_id": run_id,
            "reason": None,
            "detail": {},
        }

    monkeypatch.setattr(flocal, "_control_client", fake_client)
    return control, evidence


def test_driver_final_wait_expired_refuses_before_blocking(
    tmp_path: Path, monkeypatch: Any
) -> None:
    """An EXPIRED remaining budget at the final reap refuses BEFORE
    any blocking wait: no fresh positive floor, no post-window
    pass — the closed patience failure is returned and the
    still-running owner is left to its own finite END."""
    proc = _FakeDriverProc(pid=1, poll_rc=None, wait_rc=0, poll_sequence=[None, None, None])
    control, evidence = _driver_boundary_setup(tmp_path, monkeypatch, proc)
    summary = flocal.run_local_rehearsal(
        tmp_path / "repo", "f" * 40, tmp_path / "work", control, evidence
    )
    assert summary["status"] == "fail"
    assert summary["reason"] == "local-driver-patience"
    assert summary["run_id"] == "b" * 32
    assert summary["owner_exit"] is None
    # the expired budget refused BEFORE a blocking wait
    assert proc.wait_calls == []


def test_driver_final_wait_expired_distinguishes_exited_owner(
    tmp_path: Path, monkeypatch: Any
) -> None:
    """The already-EXITED owner is distinguished at the same
    expired boundary: a non-blocking poll observes the exit (no
    renewed wait), the run proceeds to the next closed gate — and
    that gate, not the patience gate, reports the missing
    evidence."""
    proc = _FakeDriverProc(pid=1, poll_rc=None, wait_rc=0, poll_sequence=[None, None, 0])
    control, evidence = _driver_boundary_setup(tmp_path, monkeypatch, proc)
    summary = flocal.run_local_rehearsal(
        tmp_path / "repo", "f" * 40, tmp_path / "work", control, evidence
    )
    assert summary["status"] == "fail"
    assert summary["reason"] == "local-driver-evidence"
    assert summary["run_id"] == "b" * 32
    assert summary["owner_exit"] == 0
    # no blocking wait was issued for the expired budget
    assert proc.wait_calls == []


def test_driver_valid_baseline_passes_with_real_evidence(tmp_path: Path, monkeypatch: Any) -> None:
    """The VALID public baseline: a faithful fake process/external
    seam (sealed argv verified, real state read, real bounded
    client calls, real exit) over the ACTUAL retained closed
    evidence from a genuine owner pass — the driver's own
    validate_local_evidence runs on the real bytes (no validator
    stub) and the identity/exit/digest gates hold."""
    # Stage 1: a genuine owner pass produces the real retained
    # evidence.
    fake = LocalFakeDocker()
    paths = _setup(tmp_path, monkeypatch, fake)
    owner, thread, run_id = _start_owner(paths, fake)
    try:
        assert _client(paths["control"], "prepare", run_id)["ok"] is True
        assert _client(paths["control"], "observe", run_id)["ok"] is True
        assert _client(paths["control"], "rehearse", run_id)["ok"] is True
        assert _client(paths["control"], "finish", run_id)["detail"]["outcome"] == "pass"
    finally:
        _join(thread, control=paths["control"], run_id=run_id)
    assert owner._exit_code == 0
    real_evidence = paths["evidence"].read_bytes()
    _read_evidence(paths["evidence"])  # closed validation of the retained record
    # Stage 2: the public driver over the faithful seams.
    control = _stub_control_root(tmp_path, "driver-pass")
    _fake_owner_state(control, run_id, time.monotonic() + 100)
    proc = _FakeDriverProc(pid=1, poll_rc=None, wait_rc=0)
    expected_argv = flocal._owner_argv(
        str(LOCAL_PATH.resolve()),
        HEAD,
        paths["repo"],
        tmp_path / "work2",
        control,
        paths["evidence"],
    )

    def popen(argv: list[str], **kw: Any) -> _FakeDriverProc:
        assert argv == expected_argv  # the SEALED owner launch form
        return proc

    monkeypatch.setattr(flocal.subprocess, "Popen", popen)
    commands: list[str] = []

    def fake_client(
        control_dir: Path, command: str, run_id_bound: str, timeout: float
    ) -> dict[str, Any]:
        commands.append(command)
        return {
            "record": flocal.CONTROL_RECORD,
            "ok": True,
            "command": command,
            "run_id": run_id_bound,
            "reason": None,
            "detail": {},
        }

    monkeypatch.setattr(flocal, "_control_client", fake_client)
    summary = flocal.run_local_rehearsal(
        paths["repo"], HEAD, tmp_path / "work2", control, paths["evidence"]
    )
    assert commands == ["prepare", "observe", "rehearse", "finish"]
    assert summary["status"] == "pass"
    assert summary["run_id"] == run_id
    assert summary["owner_exit"] == 0
    assert summary["reason"] is None
    assert summary["evidence_sha256"] == hashlib.sha256(real_evidence).hexdigest()


class _HeldDriverStream:
    def __init__(self, release_after: float) -> None:
        self._release_after = release_after
        self.closed = False

    def read(self, n: int) -> bytes:
        # A pipe that does not reach EOF within the driver's finite
        # settle window (the owner "still writing" beyond it).
        time.sleep(self._release_after)
        return b""

    def close(self) -> None:
        self.closed = True


class _ReadErrorDriverStream:
    def __init__(self) -> None:
        self.closed = False

    def read(self, n: int) -> bytes:
        raise OSError("simulated capture read error")

    def close(self) -> None:
        self.closed = True


def test_driver_held_reader_forbids_pass(tmp_path: Path, monkeypatch: Any) -> None:
    """A reader that never settles within the bounded window is a
    closed driver failure: the pass gate requires the drain to be
    complete, and the driver never waits a live reader forever."""
    control = _stub_control_root(tmp_path, "driver-held")
    evidence = tmp_path / "evidence" / "local-evidence.json"
    _fake_owner_state(control, "f" * 32, time.monotonic() + 100)
    stream = _HeldDriverStream(release_after=8.0)
    proc = _FakeDriverProc(pid=1, poll_rc=None, wait_rc=0, stream=stream)
    monkeypatch.setattr(flocal.subprocess, "Popen", lambda argv, **kw: proc)

    def fake_client(control_dir: Path, command: str, run_id: str, timeout: float) -> dict[str, Any]:
        return {
            "record": flocal.CONTROL_RECORD,
            "ok": True,
            "command": command,
            "run_id": run_id,
            "reason": None,
            "detail": {},
        }

    monkeypatch.setattr(flocal, "_control_client", fake_client)
    start = time.monotonic()
    summary = flocal.run_local_rehearsal(
        tmp_path / "repo", "f" * 40, tmp_path / "work", control, evidence
    )
    elapsed = time.monotonic() - start
    assert summary["status"] == "fail"
    assert summary["reason"] == "local-driver-output"
    assert summary["run_id"] == "f" * 32
    assert summary["owner_exit"] == 0
    # the finite settle window was honored (no unbounded reader wait)
    assert elapsed < 10.0


def test_driver_read_error_fault_forbids_pass(tmp_path: Path, monkeypatch: Any) -> None:
    """A capture READ ERROR is a fault exactly like the cap: the
    stream was not drained to EOF, so the pass is gated off."""
    control = _stub_control_root(tmp_path, "driver-readerr")
    evidence = tmp_path / "evidence" / "local-evidence.json"
    _fake_owner_state(control, "2" * 32, time.monotonic() + 100)
    proc = _FakeDriverProc(pid=1, poll_rc=None, wait_rc=0, stream=_ReadErrorDriverStream())
    monkeypatch.setattr(flocal.subprocess, "Popen", lambda argv, **kw: proc)

    def fake_client(control_dir: Path, command: str, run_id: str, timeout: float) -> dict[str, Any]:
        return {
            "record": flocal.CONTROL_RECORD,
            "ok": True,
            "command": command,
            "run_id": run_id,
            "reason": None,
            "detail": {},
        }

    monkeypatch.setattr(flocal, "_control_client", fake_client)
    summary = flocal.run_local_rehearsal(
        tmp_path / "repo", "f" * 40, tmp_path / "work", control, evidence
    )
    assert summary["status"] == "fail"
    assert summary["reason"] == "local-driver-output"
    assert summary["run_id"] == "2" * 32
    assert summary["owner_exit"] == 0


def test_public_main_client_missing_state(tmp_path: Path, capsys: Any) -> None:
    """The public CLI over a control root with NO state is a closed
    refusal record (never a traceback), with the zeroed identity."""
    control = _stub_control_root(tmp_path, "main-missing")
    rc = flocal.main(["client", "--control-dir", str(control), "--command", "observe"])
    record = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert record["record"] == flocal.CONTROL_RECORD
    assert record["ok"] is False
    assert record["command"] == "observe"
    assert record["run_id"] == "0" * 32
    assert record["reason"] == "local-state-missing"
    assert record["detail"] is None


def test_public_main_client_expired_anchor_refuses_before_io(
    tmp_path: Path, monkeypatch: Any, capsys: Any
) -> None:
    """An ALREADY-ELAPSED owner END+grace anchor is refused BEFORE
    any IO with the exact run identity preserved (the budget is
    never refreshed for a dead anchor).  A deterministic fake clock
    proves the elapsed state: a fresh runner's short system uptime
    must never change the premise."""
    control = _stub_control_root(tmp_path, "main-expired")
    # fixed anchor 1000 + the real 600 grace; the clock is already
    # at 3000, so END+grace (1600) is 1400 s behind BEFORE any IO
    _fake_owner_state(control, "9" * 32, 1000.0)
    clock = _FakeClock(now=3000.0)
    monkeypatch.setattr(flocal.time, "monotonic", clock.monotonic)
    rc = flocal.main(["client", "--control-dir", str(control), "--command", "observe"])
    record = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert record["ok"] is False
    assert record["command"] == "observe"
    assert record["run_id"] == "9" * 32
    assert record["reason"] == "local-driver-patience"
    assert record["detail"] is None
    # the refusal happened before any control IO
    assert not (control / flocal._CONTROL_SOCK_NAME).exists()


def test_y_readiness_lifecycle_reason_closed_vocabulary() -> None:
    # 017-y: the closed readiness-diagnosis refinements are members
    # of the owner-evidence closed reason vocabulary; the original
    # generic token and its relation are preserved
    for token in (
        "controller-not-ready",
        "controller-not-ready:uid-not-21001",
        "controller-not-ready:pid1-uid",
        "controller-not-ready:health-unreachable",
        "controller-not-ready:container-exited",
    ):
        assert token in flocal._CI_REASONS
        assert token in flocal._FAILURE_REASONS
