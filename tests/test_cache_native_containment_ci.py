"""Pure orchestration tests for the disposable-CI containment runner (017-p).

These tests exercise ONLY the runner's orchestration logic — closed-schema
validation of the probe/inspect records (including invalid metadata
rejection), bounded output capture (held-pipe convergence with the exact
owned group kill, and failed-capture rejection without uncaught thread
exceptions), exact owned process-group cleanup with tiny owned fake
children, the exact confinement argv surface, create-before ownership
registration, the ordered parent-death proof (real tiny owned descendant,
token-bound exact occurrence, pre-termination positive, post-termination
absence), verified image removal (result checked and authoritative absence
query, with cleanup failure visibility), runtime identity grammar failures,
verified-absence cleanup semantics, leftover detection, work-root
protection (pre-existing, direct symlink, ancestor symlink and
``link/../`` alias laundering) and the disposable-CI entry guard.  No test
launches docker, a container, a namespace or a keyring syscall: the actual
containment proof is the remote ``cache-native-containment`` CI job, and
these tests never substitute for it (no ready-file or mocked-flag pass is
accepted — a pass here proves the orchestration, not the boundary).
"""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import re
import select
import shutil
import stat
import subprocess
import sys
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts" / "cache_native_containment_ci.py"
PROBE = REPO_ROOT / "scripts" / "cache_native_containment_probe.py"
DOCKERFILE = REPO_ROOT / "scripts" / "cache_native_containment.Dockerfile"

spec = importlib.util.spec_from_file_location("cache_native_containment_ci", RUNNER)
assert spec is not None and spec.loader is not None
cci = importlib.util.module_from_spec(spec)
sys.modules["cache_native_containment_ci"] = cci
spec.loader.exec_module(cci)

# The probe is imported (never executed) for the pure controls over
# its emission and swap-derivation code.
probe_spec = importlib.util.spec_from_file_location("slaif_containment_probe", PROBE)
assert probe_spec is not None and probe_spec.loader is not None
probe = importlib.util.module_from_spec(probe_spec)
sys.modules["slaif_containment_probe"] = probe
probe_spec.loader.exec_module(probe)


@dataclass(frozen=True)
class ExecResult:
    """Closed bounded result, structurally identical to the runner's
    ``ExecResult`` dataclass (the runner module is loaded from a file
    path and is not visible to mypy)."""

    returncode: int
    output: bytes


def _valid_probe_record(digest: str, mode: str, token: str | None = None) -> dict[str, object]:
    record = {
        "schema": cci.PROBE_SCHEMA,
        "status": "pass",
        "mode": mode,
        "platform": "linux-x86_64",
        "cgroup_version": "v2",
        "cgroup_namespace_differs": True,
        "python_version": "3.12.12",
        "kernel_release": "6.8.0-100-generic",
        "probe_source_sha256": digest,
        "checks": {name: True for name in cci.EXPECTED_CHECKS},
        "measured": {
            **dict(cci._EXPECTED_MEASURED_VALUES),
            # Measured finite zero from the v2 swap-only controller,
            # matching the record's cgroup_version above.
            "swap_limit_source": "v2-swap-max",
        },
    }
    if mode == "hang":
        # Live owned descendant facts: container-internal pid plus the
        # exact per-run token the host binds the occurrence with.
        record["descendant_pid"] = 7
        record["descendant_token"] = token if token is not None else "0" * 32
    return record


def _host_config(exit_code: int) -> dict[str, object]:
    return {
        "NetworkMode": "none",
        "ReadonlyRootfs": True,
        "Runtime": "runc",
        "SecurityOpt": ["seccomp=builtin", "no-new-privileges:true"],
        "CapDrop": ["ALL"],
        "PidsLimit": 64,
        "Memory": cci.MEMORY_BYTES,
        "MemorySwap": cci.MEMORY_BYTES,
        "NanoCpus": 1_000_000_000,
        "Tmpfs": dict(cci.TMPFS_SPECS),
        "ExtraField": "closed-extraction-must-ignore",
        "ExitCode": exit_code,
    }


class FakeDocker:
    """Record-only fake docker executor for the runner orchestration.

    Models the exact supported surface the runner queries — bare
    container IDs, the closed inspect fields, ``image inspect`` for the
    removal verification and the reviewed runtime facts — so failure
    paths are tested against real field shapes, not implementation
    assumptions.
    """

    def __init__(
        self,
        probe_digest: str,
        hang: bool = True,
        *,
        default_runtime: str = "runc",
        runtime_version_line: str = "runc version 1.2.3",
        # Real Moby shape (daemon/runtime_unix.go stockRuntimes via
        # daemon/info_unix.go fillPlatformInfo): the stock runc
        # entry's lowercase ``path`` is the bare name "runc"; other
        # entries may carry an empty path or an absolute path.
        runtimes_path: str = "runc",
        runtimes_entry: bool = True,
        runtimes_payload: dict[str, object] | None = None,
        container_runtime: str = "runc",
        rmi_rc: int = 0,
        after_rmi_state: str = "absent",
        on_hang_rm: Callable[[], None] | None = None,
    ) -> None:
        # after_rmi_state models the authoritative post-rmi
        # ``docker image inspect``: "absent" = genuine no-such-object
        # (verified absence), "present" = image still there (rc 0),
        # "query-failed" = daemon/transport failure (rc 1 WITHOUT the
        # no-such marker — never verified absence).
        assert after_rmi_state in ("absent", "present", "query-failed")
        self.probe_digest = probe_digest
        self.image_id = "sha256:" + "a" * 64
        self.hang = hang
        self.default_runtime = default_runtime
        self.runtime_version_line = runtime_version_line
        self.runtimes_path = runtimes_path
        self.runtimes_payload = runtimes_payload
        self.runtimes_entry = runtimes_entry
        self.container_runtime = container_runtime
        self.rmi_rc = rmi_rc
        self.after_rmi_state = after_rmi_state
        self.on_hang_rm = on_hang_rm
        self.calls: list[list[str]] = []
        self.by_name: dict[str, str] = {}
        self.removed: set[str] = set()
        self.image_removed = False
        self.seen_tokens: dict[str, str] = {}
        self._cid_counter = 0

    def _new_cid(self) -> str:
        self._cid_counter += 1
        return hashlib.sha256(f"cid-{self._cid_counter}".encode()).hexdigest()

    def _name_of(self, container_id: str) -> str:
        for name, cid in self.by_name.items():
            if cid == container_id:
                return name
        raise AssertionError("unknown container")

    def _mode_of(self, container_id: str) -> str:
        return self._name_of(container_id).split("-017p-")[1].split("-")[0]

    def __call__(self, argv: list[str], timeout: float) -> ExecResult:
        self.calls.append(list(argv))
        # The runner's only non-docker query is the bare reviewed
        # name: a daemon-declared path argv would fall through to the
        # closed-surface assertion below and fail the test loudly.
        if argv[0] == self.default_runtime:
            assert argv[1:] == ["--version"]
            return ExecResult(0, (self.runtime_version_line + "\nspec: 1.0.2-dev\n").encode())
        assert argv[0] == "docker"
        cmd = argv[1:]
        sub = cmd[0]
        if sub == "version":
            return ExecResult(0, b"27.1.1\n")
        if sub == "info":
            fmt = cmd[cmd.index("--format") + 1]
            if fmt == "{{range .SecurityOptions}}{{.}} {{end}}":
                return ExecResult(0, b"name=seccomp name=cgroupns\n")
            if fmt == "{{.DefaultRuntime}}":
                return ExecResult(0, (self.default_runtime + "\n").encode())
            if fmt == "{{json .Runtimes}}":
                if self.runtimes_payload is not None:
                    payload = self.runtimes_payload
                elif self.runtimes_entry:
                    payload = {self.default_runtime: {"path": self.runtimes_path}}
                else:
                    payload = {"other": {"path": "/usr/bin/other"}}
                return ExecResult(0, (json.dumps(payload) + "\n").encode())
            raise AssertionError(f"unexpected info format: {fmt}")
        if sub == "pull":
            return ExecResult(0, b"pulled\n")
        if sub == "build":
            return ExecResult(0, b"built\n")
        if sub == "inspect":
            fmt = cmd[cmd.index("--format") + 1]
            target = cmd[-1]
            if fmt == "{{.Id}}" and target == cci.IMAGE_NAME:
                return ExecResult(0, (self.image_id + "\n").encode())
            if fmt == "{{.HostConfig.Runtime}}":
                return ExecResult(0, (self.container_runtime + "\n").encode())
            if fmt == "{{json .HostConfig}}":
                exit_code = 0 if self._mode_of(target) == "success" else 3
                return ExecResult(0, (json.dumps(_host_config(exit_code)) + "\n").encode())
            if fmt == "{{json .Config}}":
                return ExecResult(0, b'{"User": "21001:21001"}\n')
            if fmt == "{{json .State}}":
                exit_code = 0 if self._mode_of(target) == "success" else 3
                state = {"ExitCode": exit_code, "Running": False}
                return ExecResult(0, (json.dumps(state) + "\n").encode())
            raise AssertionError(f"unexpected inspect format: {fmt}")
        if sub == "create":
            name = cmd[cmd.index("--name") + 1]
            if name in self.by_name:
                return ExecResult(1, b"name already in use\n")
            cid = self._new_cid()
            self.by_name[name] = cid
            for item in cmd:
                if item.startswith("SLAIF_PROBE_DESCENDANT_TOKEN="):
                    self.seen_tokens[name] = item.split("=", 1)[1]
            return ExecResult(0, (cid + "\n").encode())
        if sub == "start":
            cid = cmd[cmd.index("-a") + 1] if "-a" in cmd else cmd[-1]
            mode = self._mode_of(cid)
            if mode == "hang" and self.hang:
                token = self.seen_tokens.get(self._name_of(cid), "")
                if not re.fullmatch(r"[0-9a-f]{32}", token):
                    raise AssertionError("hang scenario missing descendant token")
                exc = subprocess.TimeoutExpired(cmd=argv, timeout=timeout)
                # The attached CLI streamed the probe's pre-timeout pass
                # record (with the live owned descendant facts) before
                # the host deadline: model that bounded partial output.
                exc.partial_output = (  # type: ignore[attr-defined]
                    json.dumps(_valid_probe_record(self.probe_digest, "hang", token)) + "\n"
                ).encode()
                raise exc
            record = _valid_probe_record(self.probe_digest, mode)
            line = (json.dumps(record) + "\n").encode()
            return ExecResult(0 if mode == "success" else 3, line)
        if sub == "ps":
            flt = cmd[cmd.index("--filter") + 1]
            if flt.startswith("name="):
                found = self.by_name.get(flt[5:])
                if found is not None and found not in self.removed:
                    return ExecResult(0, (found + "\n").encode())
                return ExecResult(0, b"")
            if flt.startswith("id="):
                target = flt[3:]
                if target in self.by_name.values() and target not in self.removed:
                    return ExecResult(0, (target + "\n").encode())
                return ExecResult(0, b"")
            if flt.startswith("ancestor="):
                leftovers = [c for c in self.by_name.values() if c not in self.removed]
                return ExecResult(0, "".join(c + "\n" for c in leftovers).encode())
            raise AssertionError(f"unexpected filter: {flt}")
        if sub == "rm":
            cid = cmd[2]
            if cid in self.removed:
                return ExecResult(1, b"no such container\n")
            if self._mode_of(cid) == "hang" and self.on_hang_rm is not None:
                # Model the daemon killing the container's PID1 + group:
                # the test-owned real descendant is killed and reaped
                # before rm returns, so post-termination scans are exact.
                self.on_hang_rm()
            self.removed.add(cid)
            return ExecResult(0, (cid + "\n").encode())
        if sub == "rmi":
            if self.rmi_rc == 0 and self.after_rmi_state == "absent":
                self.image_removed = True
            return ExecResult(self.rmi_rc, (self.image_id + "\n").encode())
        if sub == "image":
            assert cmd[1] == "inspect"
            if self.after_rmi_state == "present":
                return ExecResult(0, b"[]\n")
            if self.after_rmi_state == "query-failed":
                return ExecResult(
                    1,
                    b"Cannot connect to the Docker daemon at "
                    b"unix:///var/run/docker.sock. Is the docker daemon running?\n",
                )
            return ExecResult(1, b"Error: No such object: " + self.image_id.encode() + b"\n")
        raise AssertionError(f"unexpected docker command: {cmd}")


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    for name in (PROBE.name, DOCKERFILE.name):
        shutil.copy(REPO_ROOT / "scripts" / name, repo / "scripts" / name)
    (repo / "Dockerfile").write_bytes((REPO_ROOT / "Dockerfile").read_bytes())
    return repo


# -- closed-schema validation --------------------------------------------


def test_validate_probe_record_accepts_exact_pass_record() -> None:
    digest = "c" * 64
    record = _valid_probe_record(digest, "success")
    assert cci.validate_probe_record(record, digest, "success") is record


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.update({**r, "extra": 1}) or r,
        lambda r: r["checks"].pop("seccomp_filter_mode") or r,
        lambda r: r["checks"].update(seccomp_filter_mode=False) or r,
        lambda r: r["checks"].update(seccomp_filter_mode=1) or r,  # int is not bool
        lambda r: r["measured"].update(pids_limit=128) or r,
        lambda r: r["measured"].update(pids_limit=True) or r,  # bool is not an int count
        lambda r: r.update({**r, "probe_source_sha256": "d" * 64}) or r,
        lambda r: r.update({**r, "mode": "fail"}) or r,
        lambda r: r.pop("platform") or r,
    ],
    ids=[
        "extra-key",
        "missing-check",
        "false-check",
        "int-check",
        "measured-mismatch",
        "bool-measured",
        "wrong-digest",
        "wrong-mode",
        "missing-key",
    ],
)
def test_validate_probe_record_rejects_open_schemas(mutate: object) -> None:
    record = _valid_probe_record("c" * 64, "success")
    mutate(record)  # type: ignore[operator]
    with pytest.raises(cci.ContainmentError):
        cci.validate_probe_record(record, "c" * 64, "success")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("python_version", "3.12.12 http://x"),
        ("python_version", "abc"),
        ("python_version", "3.12"),
        ("kernel_release", "6.8.0-100-generic/../etc/passwd"),
        ("kernel_release", "v6.8"),
    ],
)
def test_validate_probe_record_rejects_invalid_version_metadata(field: str, value: str) -> None:
    record = _valid_probe_record("c" * 64, "success")
    record[field] = value
    with pytest.raises(cci.ContainmentError):
        cci.validate_probe_record(record, "c" * 64, "success")


def test_validate_probe_record_hang_fields_closed() -> None:
    digest = "c" * 64
    token = "ab" * 16
    base = _valid_probe_record(digest, "success")
    # success/fail records must not carry the hang-only fields
    with pytest.raises(cci.ContainmentError, match="probe-record-keys"):
        cci.validate_probe_record(
            {**base, "descendant_pid": 7, "descendant_token": token}, digest, "success"
        )
    hang = _valid_probe_record(digest, "hang", token)
    assert cci.validate_probe_record(hang, digest, "hang", token) is hang
    missing = {k: v for k, v in hang.items() if k != "descendant_pid"}
    with pytest.raises(cci.ContainmentError, match="probe-record-keys"):
        cci.validate_probe_record(missing, digest, "hang", token)
    with pytest.raises(cci.ContainmentError, match="probe-record-descendant-token"):
        cci.validate_probe_record({**hang, "descendant_token": "cd" * 16}, digest, "hang", token)
    with pytest.raises(cci.ContainmentError, match="probe-record-descendant-pid"):
        cci.validate_probe_record({**hang, "descendant_pid": True}, digest, "hang", token)
    with pytest.raises(cci.ContainmentError, match="probe-record-descendant-pid"):
        cci.validate_probe_record({**hang, "descendant_pid": 0}, digest, "hang", token)
    with pytest.raises(cci.ContainmentError, match="hang-token-invalid"):
        cci.validate_probe_record(hang, digest, "hang", None)


def test_validate_inspect_record_rejects_drift() -> None:
    valid = cci.extract_inspect_facts(
        _host_config(0),
        {"User": "21001:21001"},
        {
            "ExitCode": 0,
            "Running": False,
        },
    )
    cci.validate_inspect_record(valid, 0)
    host_net = {**valid, "NetworkMode": "host"}
    with pytest.raises(cci.ContainmentError):
        cci.validate_inspect_record(host_net, 0)
    missing = {k: v for k, v in valid.items() if k != "CapDrop"}
    with pytest.raises(cci.ContainmentError):
        cci.validate_inspect_record(missing, 0)
    rw_rootfs = {**valid, "ReadOnlyRootfs": False}
    with pytest.raises(cci.ContainmentError):
        cci.validate_inspect_record(rw_rootfs, 0)
    # unsorted SecurityOpt with the same set is still the exact policy
    cci.validate_inspect_record({**valid, "SecurityOpt": list(reversed(valid["SecurityOpt"]))}, 0)
    # the undocumented extra host-config field is closed-extracted away
    assert "ExtraField" not in valid


# -- bounded output and line extraction -----------------------------------


def test_read_bounded_output_caps_and_drains() -> None:
    stream = io.BytesIO(b"x" * 100_000)
    kept = cci.read_bounded_output(stream, 4096)
    assert len(kept) == 4096
    assert kept == b"x" * 4096
    assert stream.read() == b""  # remainder was drained, not retained


def test_extract_probe_line_last_json_line() -> None:
    line1 = json.dumps({"schema": "x"})
    line2 = json.dumps({"schema": "y"})
    data = f"junk {line1}\n{line2}\n".encode()
    assert cci.extract_probe_line(data) == line2
    assert cci.extract_probe_line(b"no json here\n") is None
    assert cci.extract_probe_line(b"") is None


def test_real_execute_kills_owned_process_group(tmp_path: Path) -> None:
    marker = "time.sleep(60) # slaif-exec-group-test"
    script = tmp_path / "child.py"
    script.write_text(
        "import subprocess, sys, time\n"
        f"subprocess.Popen([sys.executable, '-c', {marker!r}], "
        "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
        "time.sleep(60)\n"
    )
    with pytest.raises(subprocess.TimeoutExpired):
        cci._real_execute([sys.executable, str(script)], 1.0)
    # both the CLI child and its owned descendant are gone
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if cci._count_marker_processes(os.getuid(), "slaif-exec-group-test") == 0:
            break
        time.sleep(0.1)
    assert cci._count_marker_processes(os.getuid(), "slaif-exec-group-test") == 0


# -- bounded capture: held pipe and failed capture -----------------------


def test_real_execute_held_pipe_converges_bounded(tmp_path: Path) -> None:
    # The leader exits while an owned descendant still holds the
    # write side of the pipe: the exact owned group is killed after a
    # bounded grace, the drain converges, and nothing is left behind.
    marker = "slaif-held-pipe-017p"
    script = tmp_path / "parent.py"
    script.write_text(
        "import subprocess, sys\n"
        f"subprocess.Popen([sys.executable, '-c', "
        f"'import time; time.sleep(30) # {marker}'])\n"
        "print('parent-done')\n"
    )
    started = time.monotonic()
    result = cci._real_execute([sys.executable, str(script)], 20.0)
    elapsed = time.monotonic() - started
    assert result.returncode == 0
    assert b"parent-done" in result.output
    assert elapsed < 15  # bounded: grace + group kill + convergence
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if cci._count_marker_processes(os.getuid(), marker) == 0:
            break
        time.sleep(0.1)
    assert cci._count_marker_processes(os.getuid(), marker) == 0


def test_real_execute_capture_read_error_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A capture read failure is a fixed closed state: no uncaught
    # thread exception (raw text leak) and no empty-success output.
    thread_errors: list[str] = []

    def _hook(args: threading.ExceptHookArgs) -> None:
        thread_errors.append(args.exc_type.__name__)

    monkeypatch.setattr(threading, "excepthook", _hook)

    def _broken(*_args: object, **_kwargs: object) -> bytes:
        raise OSError("fixed-synthetic-output-canary")

    monkeypatch.setattr(cci, "read_bounded_output", _broken)
    with pytest.raises(cci.ContainmentError, match="output-read-failed"):
        cci._real_execute([sys.executable, "-c", "print('x')"], 10.0)
    assert thread_errors == []


# -- confinement create-argv surface ---------------------------------------


def test_build_run_conf_argv_confinement_surface() -> None:
    env = {"SLAIF_PROBE_MODE": "success", "SLAIF_PROBE_UID": "21001"}
    argv = cci.build_run_conf_argv("img", "name-0", "slaif-owned-containment-017p=x", env)
    assert argv[1] == "create"  # create-first ownership: the CID is returned before start
    for flag, value in (
        ("--network", "none"),
        ("--read-only", None),
        ("--user", "21001:21001"),
        ("--cap-drop", "ALL"),
        ("--pids-limit", "64"),
        ("--cpus", "1"),
        ("--memory", str(cci.MEMORY_BYTES)),
        ("--memory-swap", str(cci.MEMORY_BYTES)),
        ("--label", "slaif-owned-containment-017p=x"),
    ):
        if value is None:
            assert flag in argv
        else:
            assert argv[argv.index(flag) + 1] == value
    assert argv.count("--security-opt") == 2
    assert "no-new-privileges:true" in argv
    assert "seccomp=builtin" in argv
    for mountpoint, spec_str in cci.TMPFS_SPECS.items():
        assert f"{mountpoint}:{spec_str}" in argv
    assert argv[-1] == "img"
    assert "SLAIF_PROBE_MODE=success" in argv
    # no host mounts, no privileged/host-pid/ipc/network flags anywhere
    forbidden = {"--privileged", "--pid", "--ipc", "-v", "--volumes-from", "--add-host"}
    assert not (forbidden & set(argv))


# -- exact-owned cleanup semantics -------------------------------------------


def test_cleanup_distinguishes_query_failure_and_absence() -> None:
    def query_failed(argv: list[str], timeout: float) -> ExecResult:
        return ExecResult(1, b"")

    with pytest.raises(cci.ContainmentError, match="cleanup-query-failed"):
        cci.cleanup_container(query_failed, "c" * 64)

    def rm_fails(argv: list[str], timeout: float) -> ExecResult:
        if argv[1] == "ps":
            return ExecResult(0, b"c" * 64 + b"\n")
        return ExecResult(1, b"denied\n")

    with pytest.raises(cci.ContainmentError, match="cleanup-failed"):
        cci.cleanup_container(rm_fails, "c" * 64)

    def absent_noop(argv: list[str], timeout: float) -> ExecResult:
        return ExecResult(0, b"")

    cci.cleanup_container(absent_noop, "c" * 64)  # verified absence: no-op


def test_leftover_detection_semantics() -> None:
    def clean(argv: list[str], timeout: float) -> ExecResult:
        return ExecResult(0, b"")

    cci.verify_no_leftovers(clean, cci.IMAGE_NAME)

    def leftover(argv: list[str], timeout: float) -> ExecResult:
        return ExecResult(0, b"deadbeef\n")

    with pytest.raises(cci.ContainmentError, match="leftover-container"):
        cci.verify_no_leftovers(leftover, cci.IMAGE_NAME)


# -- fail-closed preflight ----------------------------------------------------


def test_main_refuses_non_ci_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    rc = cci.main(["--repo", str(tmp_path), "--work", str(tmp_path / "w")])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert out == {"schema": cci.SCHEMA, "status": "fail", "reason": "not-a-disposable-ci-runner"}


def test_main_refuses_non_hosted_ci_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # GITHUB_ACTIONS alone is not the hosted-disposable claim:
    # self-hosted runners (or any other environment value) are refused.
    argv = ["--repo", str(tmp_path), "--work", str(tmp_path / "w")]
    for value in (None, "github-actor"):
        if value is None:
            monkeypatch.delenv("RUNNER_ENVIRONMENT", raising=False)
        else:
            monkeypatch.setenv("RUNNER_ENVIRONMENT", value)
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        rc = cci.main(argv)
        out = json.loads(capsys.readouterr().out)
        assert rc == 1
        assert out == {
            "schema": cci.SCHEMA,
            "status": "fail",
            "reason": "not-a-hosted-ci-runner",
        }


def test_work_root_rejects_preexisting(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    work = tmp_path / "work"
    work.mkdir()
    with pytest.raises(cci.ContainmentError, match="work-root-exists"):
        cci.run(repo, work, FakeDocker("c" * 64).__call__)


def test_work_root_rejects_ancestor_symlink(tmp_path: Path) -> None:
    target = tmp_path / "target"
    (target / "inner").mkdir(parents=True)
    link = tmp_path / "link"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(cci.ContainmentError, match="work-root-untrusted"):
        cci._create_work_root(link / "inner" / "work")
    assert not (target / "inner" / "work").exists()


def test_work_root_rejects_dotdot_alias_of_preexisting_target(tmp_path: Path) -> None:
    # link -> other/inner makes link/../work an alias of other/work:
    # the traversal must be rejected and the pre-existing target
    # preserved untouched (no adoption, no context created in it).
    other = tmp_path / "other"
    (other / "inner").mkdir(parents=True)
    old = other / "work"
    old.mkdir(mode=0o700)
    (old / "sentinel").write_bytes(b"fixed synthetic sentinel")
    link = tmp_path / "link"
    link.symlink_to(other / "inner", target_is_directory=True)
    alias = link / ".." / "work"
    with pytest.raises(cci.ContainmentError, match="work-root-untrusted"):
        cci._create_work_root(alias)
    assert (old / "sentinel").read_bytes() == b"fixed synthetic sentinel"
    assert not (old / "context").exists()
    assert not (tmp_path / "work").exists()


def test_work_root_direct_symlink_and_preservation(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    direct = tmp_path / "direct"
    direct.symlink_to(target, target_is_directory=True)
    with pytest.raises(cci.ContainmentError, match="work-root-exists"):
        cci._create_work_root(direct)
    existing = tmp_path / "existing"
    existing.mkdir(mode=0o755)
    (existing / "sentinel").write_text("fixed synthetic sentinel")
    with pytest.raises(cci.ContainmentError, match="work-root-exists"):
        cci._create_work_root(existing)
    assert stat.S_IMODE(existing.stat().st_mode) == 0o755
    assert (existing / "sentinel").read_text() == "fixed synthetic sentinel"
    fresh = tmp_path / "fresh"
    cci._create_work_root(fresh)
    assert fresh.is_dir() and stat.S_IMODE(fresh.stat().st_mode) == 0o700


def test_run_fails_closed_missing_files(tmp_path: Path) -> None:
    repo = tmp_path / "empty-repo"
    repo.mkdir()
    with pytest.raises(cci.ContainmentError, match="probe-file-missing"):
        cci.run(repo, tmp_path / "work", FakeDocker("c" * 64).__call__)


def test_run_dockerfile_base_must_match_repo(tmp_path: Path) -> None:
    for case, search, replace in (
        ("corrupted", b"7522254", b"7522255"),  # one corrupted digest hex digit
        (
            "unpinned",
            b"python:3.12-slim-bookworm@sha256:782412",
            b"python:3.12-slim-bookworm",
        ),
    ):
        repo = _make_repo(tmp_path / case)
        dockerfile = repo / "scripts" / DOCKERFILE.name
        dockerfile.write_bytes(dockerfile.read_bytes().replace(search, replace))
        with pytest.raises(cci.ContainmentError, match="dockerfile-base"):
            cci.run(repo, tmp_path / ("work-" + case), FakeDocker("c" * 64).__call__)


# -- full orchestration with fake docker ---------------------------------------


def _spawn_run_descendant(token: str) -> subprocess.Popen[bytes]:
    """A real tiny owned descendant carrying the token-bound marker.

    Waits until it is observable in /proc (uid + exact token) so the
    runner's pre-termination positive observation is deterministic.
    """
    marker = f"import time; time.sleep(120) # slaif-hang-descendant-017p {token}"
    child = subprocess.Popen(
        [sys.executable, "-c", marker],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if cci._count_marker_processes(os.getuid(), token) == 1:
            return child
        if child.poll() is not None:
            _kill_child(child)
            raise AssertionError("descendant child exited early")
        time.sleep(0.05)
    _kill_child(child)
    raise AssertionError("descendant child not observable in time")


def _kill_child(child: subprocess.Popen[bytes]) -> None:
    try:
        child.kill()
        child.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass


def test_run_full_success_fake_docker(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    work = tmp_path / "work"
    digest = hashlib.sha256((repo / "scripts" / PROBE.name).read_bytes()).hexdigest()
    token = uuid.uuid4().hex
    child = _spawn_run_descendant(token)
    fake = FakeDocker(digest, on_hang_rm=lambda: _kill_child(child))
    try:
        summary = cci.run(repo, work, fake.__call__, descendant_uid=os.getuid(), hang_token=token)
    finally:
        _kill_child(child)
    assert summary["status"] == "pass"
    assert summary["probe_source_sha256"] == digest
    assert summary["image_removed"] is True
    assert summary["descendant_terminated"] is True
    assert summary["checks"] == {name: True for name in cci.EXPECTED_CHECKS}
    assert summary["measured"] == {
        **dict(cci._EXPECTED_MEASURED_VALUES),
        "swap_limit_source": "v2-swap-max",
    }
    assert summary["python_version"] == "3.12.12"
    assert summary["kernel_release"] == "6.8.0-100-generic"
    assert summary["engine_version"] == "27.1.1"
    assert summary["runtime_name"] == "runc"
    assert summary["runtime_version"] == "1.2.3"
    assert summary["scenarios"]["slaif-containment-017p-success"]["exit_code"] == 0
    assert summary["scenarios"]["slaif-containment-017p-fail"]["exit_code"] == 3
    hang = summary["scenarios"]["slaif-containment-017p-hang"]
    assert hang["host_timeout"] is True
    assert hang["descendant_terminated"] is True
    assert hang["parent_sentinel_survived"] is True
    assert hang["descendant_pid"] == 7
    # The ordered parent-death proof consumed the REAL owned
    # descendant: pre-termination positive, container teardown,
    # post-termination absence (killed and reaped by the fake rm).
    assert child.poll() is not None
    # create-first ownership: every CID is recorded from the create output,
    # and every rm -f targets a created container id only (exactly once —
    # the final sweep is a verified-absence no-op, not a second rm)
    created = list(fake.by_name.values())
    rm_targets = [c[3] for c in fake.calls if c[1] == "rm"]
    assert sorted(rm_targets) == sorted(created)
    create_calls = [c for c in fake.calls if c[1] == "create"]
    assert len(create_calls) == 3
    assert all(
        "--label" in c and c[c.index("--label") + 1].startswith("slaif-owned-containment-017p=")
        for c in create_calls
    )
    # The per-run descendant token reached exactly the hang scenario.
    assert len(fake.seen_tokens) == 1
    assert all(value == token for value in fake.seen_tokens.values())
    assert fake.image_removed
    assert not work.exists()  # owned scratch namespace is torn down


def test_run_hang_must_be_host_timeout(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    digest = hashlib.sha256((repo / "scripts" / PROBE.name).read_bytes()).hexdigest()
    fake = FakeDocker(digest, hang=False)  # container exits: not the timeout case
    with pytest.raises(cci.ContainmentError, match="scenario-expected-timeout"):
        cci.run(repo, tmp_path / "work", fake.__call__)


# -- ordered parent-death proof: failure paths ---------------------------------


def test_run_hang_descendant_leftover_fails(tmp_path: Path) -> None:
    # The fake rm does NOT kill the real descendant: the exact owned
    # occurrence is still alive after container teardown.
    repo = _make_repo(tmp_path)
    digest = hashlib.sha256((repo / "scripts" / PROBE.name).read_bytes()).hexdigest()
    token = uuid.uuid4().hex
    child = _spawn_run_descendant(token)
    fake = FakeDocker(digest)
    try:
        with pytest.raises(cci.ContainmentError, match="descendant-leftover"):
            cci.run(
                repo,
                tmp_path / "work",
                fake.__call__,
                descendant_uid=os.getuid(),
                hang_token=token,
            )
    finally:
        _kill_child(child)
    assert cci._count_marker_processes(os.getuid(), token) == 0


def test_run_hang_descendant_not_observed_fails(tmp_path: Path) -> None:
    # No live owned occurrence: an empty scan is NOT evidence of
    # termination — the pre-termination positive must fail closed.
    repo = _make_repo(tmp_path)
    digest = hashlib.sha256((repo / "scripts" / PROBE.name).read_bytes()).hexdigest()
    token = uuid.uuid4().hex
    fake = FakeDocker(digest)
    with pytest.raises(cci.ContainmentError, match="descendant-not-observed"):
        cci.run(
            repo,
            tmp_path / "work",
            fake.__call__,
            descendant_uid=os.getuid(),
            hang_token=token,
        )


# -- verified image removal: failure visibility --------------------------------


def test_run_image_rmi_failure_stays_visible(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    digest = hashlib.sha256((repo / "scripts" / PROBE.name).read_bytes()).hexdigest()
    token = uuid.uuid4().hex
    child = _spawn_run_descendant(token)
    fake = FakeDocker(digest, rmi_rc=1, on_hang_rm=lambda: _kill_child(child))
    try:
        with pytest.raises(cci.ContainmentError, match="image-rmi-failed"):
            cci.run(
                repo,
                tmp_path / "work",
                fake.__call__,
                descendant_uid=os.getuid(),
                hang_token=token,
            )
    finally:
        _kill_child(child)
    assert not fake.image_removed


def test_run_image_still_present_after_rmi_fails(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    digest = hashlib.sha256((repo / "scripts" / PROBE.name).read_bytes()).hexdigest()
    token = uuid.uuid4().hex
    child = _spawn_run_descendant(token)
    fake = FakeDocker(digest, after_rmi_state="present", on_hang_rm=lambda: _kill_child(child))
    try:
        with pytest.raises(cci.ContainmentError, match="image-still-present"):
            cci.run(
                repo,
                tmp_path / "work",
                fake.__call__,
                descendant_uid=os.getuid(),
                hang_token=token,
            )
    finally:
        _kill_child(child)
    assert not fake.image_removed


def test_run_image_absence_query_failure_fails(tmp_path: Path) -> None:
    # A nonzero ``docker image inspect`` caused by a daemon/transport
    # failure (no no-such marker) is NOT verified absence.
    repo = _make_repo(tmp_path)
    digest = hashlib.sha256((repo / "scripts" / PROBE.name).read_bytes()).hexdigest()
    token = uuid.uuid4().hex
    child = _spawn_run_descendant(token)
    fake = FakeDocker(digest, after_rmi_state="query-failed", on_hang_rm=lambda: _kill_child(child))
    try:
        with pytest.raises(cci.ContainmentError, match="image-absence-unverified"):
            cci.run(
                repo,
                tmp_path / "work",
                fake.__call__,
                descendant_uid=os.getuid(),
                hang_token=token,
            )
    finally:
        _kill_child(child)
    assert not fake.image_removed


# -- runtime identity: closed grammar failure paths -----------------------------


def test_run_runtime_identity_failures(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    digest = hashlib.sha256((repo / "scripts" / PROBE.name).read_bytes()).hexdigest()
    cases: tuple[tuple[dict[str, object], str], ...] = (
        ({"runtime_version_line": "runc version not-a-version"}, "runtime-version-invalid"),
        ({"runtime_version_line": "crun version 1.18"}, "runtime-version-invalid"),
        ({"runtimes_entry": False}, "runtime-invalid"),
        ({"default_runtime": "Runc"}, "runtime-invalid"),
        # The real Moby field is lowercase ``path`` (stock value: the
        # bare name "runc"): the fabricated uppercase "Path" shape and
        # any non-bare/non-absolute shape must fail closed.
        ({"runtimes_payload": {"runc": {"Path": "runc"}}}, "runtime-invalid"),
        ({"runtimes_payload": {"runc": {}}}, "runtime-invalid"),
        ({"runtimes_payload": {"runc": {"path": 5}}}, "runtime-invalid"),
        ({"runtimes_payload": {"runc": {"path": "usr/bin/runc"}}}, "runtime-invalid"),
        ({"runtimes_payload": {"runc": {"path": "/usr/../bin/runc"}}}, "runtime-invalid"),
    )
    for index, (kwargs, reason) in enumerate(cases):
        fake = FakeDocker(digest, **kwargs)  # type: ignore[arg-type]
        with pytest.raises(cci.ContainmentError, match=reason):
            cci.run(repo, tmp_path / f"work-runtime-{index}", fake.__call__)


def test_run_container_runtime_mismatch_fails(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    digest = hashlib.sha256((repo / "scripts" / PROBE.name).read_bytes()).hexdigest()
    fake = FakeDocker(digest, container_runtime="crun")
    with pytest.raises(cci.ContainmentError, match="inspect-mismatch:Runtime"):
        cci.run(repo, tmp_path / "work", fake.__call__)


@pytest.mark.parametrize(
    "runtimes_path",
    ["", "/usr/bin/runc"],
    ids=["empty-path-bare-name", "absolute-path-shape-only"],
)
def test_run_runtime_non_stock_path_shapes_accepted(tmp_path: Path, runtimes_path: str) -> None:
    # Both real supported shapes beyond the stock bare "runc": an
    # empty path and a non-empty absolute path.  The absolute path is
    # shape-validated ONLY and never executed: the version query
    # stays the bare reviewed name through the standard PATH (a path
    # argv would trip the fake's closed-surface assertion).
    repo = _make_repo(tmp_path)
    digest = hashlib.sha256((repo / "scripts" / PROBE.name).read_bytes()).hexdigest()
    token = uuid.uuid4().hex
    child = _spawn_run_descendant(token)
    fake = FakeDocker(digest, runtimes_path=runtimes_path, on_hang_rm=lambda: _kill_child(child))
    try:
        summary = cci.run(
            repo, tmp_path / "work", fake.__call__, descendant_uid=os.getuid(), hang_token=token
        )
    finally:
        _kill_child(child)
    assert summary["runtime_name"] == "runc"
    assert summary["runtime_version"] == "1.2.3"
    assert [c for c in fake.calls if c and c[-1] == "--version"] == [["runc", "--version"]]


# -- probe pure controls: flush-before-hold and measured swap ----------


@pytest.mark.parametrize(
    ("version", "memory_raw", "swap_raw", "expected"),
    [
        ("v2", "536870912", None, ("missing", 0)),
        ("v2", "536870912", "0", ("v2-swap-max", 0)),
        ("v2", "536870912", "1048576", ("v2-swap-max", 1048576)),
        ("v2", "536870912", "max", ("v2-swap-max", -1)),
        ("v1", "536870912", None, ("missing", 0)),
        ("v1", "536870912", "536870912", ("v1-memsw-combined", 0)),
        ("v1", "536870912", "1073741824", ("v1-memsw-combined", 536870912)),
        ("v1", "536870912", "9223372036854771712", ("v1-memsw-combined", -1)),
        ("v1", "9223372036854771712", "1073741824", ("missing", 0)),
        ("v1", "max", "1073741824", ("missing", 0)),
    ],
    ids=[
        "v2-missing-is-not-zero",
        "v2-measured-zero",
        "v2-positive",
        "v2-unlimited",
        "v1-missing-is-not-zero",
        "v1-combined-equals-memory",
        "v1-combined-above-memory",
        "v1-combined-unlimited",
        "v1-memory-unlimited-not-derivable",
        "v1-memory-max-not-derivable",
    ],
)
def test_probe_swap_limit_derivation(
    version: str, memory_raw: str | None, swap_raw: str | None, expected: tuple[str, int]
) -> None:
    # A missing or underivable measurement is never a measured zero
    # that could satisfy swap_disabled; the closed source enum names
    # the controller the value came from (v2 swap-only versus v1
    # combined memsw).
    assert probe._swap_limit(version, memory_raw, swap_raw) == expected


@pytest.mark.parametrize(
    ("cgroup_version", "source"),
    [
        ("v2", "v1-memsw-combined"),  # version/source mismatch
        ("v2", "missing"),  # not measured: never a pass
        ("v1", "v2-swap-max"),
        ("v1", "missing"),
        ("v2", 0),  # non-string source
    ],
)
def test_validate_probe_record_swap_source_closed(cgroup_version: str, source: object) -> None:
    record = _valid_probe_record("c" * 64, "success")
    measured: dict[str, object] = dict(cci._EXPECTED_MEASURED_VALUES)
    measured["swap_limit_source"] = source
    record["cgroup_version"] = cgroup_version
    record["measured"] = measured
    with pytest.raises(cci.ContainmentError, match="probe-measured-mismatch:swap_limit_source"):
        cci.validate_probe_record(record, "c" * 64, "success")


def test_validate_probe_record_v1_measured_swap_accepted() -> None:
    # v1 keeps its correct combined-memsw derivation when the source
    # matches the record's cgroup version and the measured allowance
    # is a finite zero.
    record = _valid_probe_record("c" * 64, "success")
    measured: dict[str, object] = dict(cci._EXPECTED_MEASURED_VALUES)
    measured["swap_limit_source"] = "v1-memsw-combined"
    record["cgroup_version"] = "v1"
    record["measured"] = measured
    assert cci.validate_probe_record(record, "c" * 64, "success") is record


def test_probe_emit_publishes_record_before_child_exit() -> None:
    # The probe's OWN emission path through a real block-buffered
    # stdout pipe: the parent must observe the exact complete record
    # line while the child is still alive (its finite hold after
    # emission) — publication strictly before exit, which is what
    # the host-timeout partial capture depends on.  Pure owned-pipe
    # control: no Docker, no keyring, no namespaces.
    record = {
        "schema": probe.SCHEMA,
        "status": "pass",
        "mode": "hang",
        "descendant_pid": 7,
        "descendant_token": "ab" * 16,
    }
    driver = (
        "import importlib.util, sys, time\n"
        f"spec = importlib.util.spec_from_file_location('slaif_probe', r'{PROBE}')\n"
        "assert spec is not None and spec.loader is not None\n"
        "slaif_probe = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(slaif_probe)\n"
        f"slaif_probe.emit_record({record!r}, sort_keys=True)\n"
        "time.sleep(30)\n"
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", driver], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    assert proc.stdout is not None
    try:
        ready, _, _ = select.select([proc.stdout], [], [], 10.0)
        assert ready, "record not published while the child is still alive"
        line = proc.stdout.readline()
        assert json.loads(line.decode("utf-8")) == record
        assert line.endswith(b"\n")
        assert proc.poll() is None, "child exited: publication is not proven before exit"
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.wait(timeout=10)
