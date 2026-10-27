"""017-aa owner-UID fixture integration — focused public fake tests.

These tests drive the ACTUAL public owner-UID surface of the
integrated owner (017-aa): the owner's own identity collection/
derivation through the ONE raw read seam, the frozen immutable
owner context, the owner-scoped guarded allowlist (build args,
create tmpfs specs, the exact independent exec user), the v2
subject/pty/observe record law, the closed AB terminal evidence
validator, and the EXACT registered-CID owned-lifetime teardown
registry (CID-attested pre-removal frames, the tri-stated
post-removal verification, the over-bound/unreadable/raced frame
refusals, and the recycled / still-existing / contradictory-frame
classification law).

Everything runs over injected FAKE external operations only: a
real synthetic git repository sealed at the canonical future
017-ab entry, a fake identity reader, a fake docker over a fake
process world, and a fake /proc root read by the PRODUCTION
bounded readers.  No test launches docker, a container or the
stand-in; no real fixture admission in the real checkout; no
worker stop or host signal.
"""

from __future__ import annotations

import errno
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import socket
import stat
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

AB_ORDER_ID = "017-ab"
AB_ORDER_NAME = "017-ab-owner-uid-python-capability-qualification.md"
AB_ORDER_BYTES = b"# synthetic AB order (fake seam only)\n"

# The useful owner-UID identity: INDEPENDENT uid/gid (never
# uid:uid), distinct from the fixed controller 21001.
SUBJ_UID = 1001
SUBJ_GID = 1002
CTL_UID = 21001

CTL_PID = 1
SUBJ_PID = 60
WORKER_PID = 70
CTL_START = 100
SUBJ_START = 500
WORKER_START = 900
RECYCLED_START = 777


def _load_test_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


stl = _load_test_module("oap_aa_stl", REPO_ROOT / "tests" / "test_cache_native_fixture_local.py")
stp = _load_test_module(
    "oap_aa_stp", REPO_ROOT / "tests" / "test_cache_native_fixture_native_prep.py"
)

fci = sys.modules["cache_native_fixture_ci"]
fb = sys.modules["cache_native_fixture_binding"]
fp = sys.modules["cache_native_fixture_native_prep"]
fctl = sys.modules["cache_native_fixture_controller"]
frp = sys.modules["cache_native_fixture_runtime_profile"]
fi = sys.modules["cache_native_fixture_identity"]
flocal = sys.modules["cache_native_fixture_local"]
model = fci.model
FixtureError = fci.FixtureError
S_ORDER_NAME = Path(stl.ORDER_PATH).name


# -- fake proc frames (production readers over a synthetic root) -----------------


def _write_proc_entry(
    root: Path,
    pid: int,
    *,
    comm: str,
    start: int,
    uid: int,
    gid: int,
    groups: tuple[int, ...],
    cgroup: str | None,
) -> None:
    """One synthetic /proc/<pid> entry (cgroup/stat/status) under
    the fake root: the production bounded readers do the reading,
    parsing and refusal — the files are the only fake."""
    d = root / str(pid)
    d.mkdir(parents=True, exist_ok=True)
    if cgroup is not None:
        (d / "cgroup").write_text(f"0::/system.slice/docker-{cgroup}.scope\n", encoding="ascii")
    (d / "stat").write_text(stp.stat_line(pid, comm, start=start), encoding="ascii")
    (d / "status").write_bytes(stp.status_bytes(uid, gid, groups))


# -- the fake exact-CID process world ---------------------------------------------


class _World:
    """The fake exact-CID process world of the owner-UID variant:
    the controller (pid 1, fixed 21001) is a member from create;
    the held subject (pid 60) appears when the fake detached exec
    is issued and runs the SAME finite hold law as the real
    stand-in (at most HOLD_SECONDS of the FAKE CONTAINER's own
    time, then a natural exit — absence only, never an exit code
    or cause); the UNRELATED same-UID worker (pid 70) never is a
    member (no registered-CID cgroup) and must survive every
    teardown untouched."""

    #: The fake container's finite hold bound: the SAME 20-second
    #: hard bound the real stand-in hold mode enforces
    #: (``HOLD_MAX_SECONDS``), measured in the fake container's own
    #: time — the test advances this clock, no host sleep occurs.
    HOLD_SECONDS = 20.0

    def __init__(self, proc_root: Path) -> None:
        self.cid: str | None = None
        self.controller: dict[str, Any] | None = None
        self.subject: dict[str, Any] | None = None
        self.worker: dict[str, Any] | None = None
        self.race_pids: set[int] = set()
        self.proc_root = proc_root
        # The fake CONTAINER clock (container time, not host wall
        # time): the held subject's finite hold expires on THIS
        # clock, so a coherent coupled world needs no host sleep.
        self.time = 0.0
        self.subject_started_at: float | None = None

    def now(self) -> float:
        return self.time

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise AssertionError("the fake container clock runs forward only")
        self.time += seconds
        # Container time advancing PAST the finite bound IS the
        # natural exit: expire here (and again at every operation,
        # where further time may have passed).
        self.expire_hold_if_due()

    def expire_hold_if_due(self) -> None:
        """The finite hold's natural exit on the fake container
        clock: at (and only at) its finite bound the subject
        process leaves the world — absence only (no exit code or
        cause is recorded, the verified-gone law)."""
        if self.subject is None or self.subject_started_at is None:
            return
        if self.time - self.subject_started_at < self.HOLD_SECONDS:
            return
        d = self.proc_root / str(SUBJ_PID)
        if d.is_dir():
            shutil.rmtree(d)
        self.subject = None
        self.subject_started_at = None

    def attach(self, cid: str) -> None:
        self.cid = cid
        self.controller = {"cgroup": cid}
        self.worker = {"cgroup": None}

    def member_pids(self) -> list[int]:
        out = [CTL_PID]
        if self.subject is not None:
            out.append(SUBJ_PID)
        out.extend(sorted(self.race_pids))
        return out


# -- the fake docker over the world -------------------------------------------------


def _aa_description() -> Any:
    return fi.FixtureIdentityDescription(
        profile=fi.PROFILE_OWNER_UID,
        controller_uid=fi.CONTROLLER_UID,
        controller_gid=fi.CONTROLLER_GID,
        subject_uid=SUBJ_UID,
        subject_gid=SUBJ_GID,
        subject_groups=(SUBJ_GID,),
    )


def _owner_tmpfs_dict() -> dict[str, str]:
    # The fake daemon reports back EXACTLY the owner-variant
    # create --tmpfs specs the production owner sends (the closed
    # spec grammar with octal modes and the frozen subject-owned
    # identities), never a re-derivation with its own formatting.
    return dict(fci.owner_tmpfs_specs(frp.owner_runtime_profile(_aa_description())))


def _owner_exec_measurement_record() -> dict[str, Any]:
    record: dict[str, Any] = stl._exec_measurement_record()
    record["record"] = model.SCHEMA_EXEC_MEASUREMENT_V2
    record["uid"] = SUBJ_UID
    record["gid"] = SUBJ_GID
    record["groups"] = []
    for mount in record["writable_mounts"]:
        if mount["root"] in ("/run/slaif-subj", "/tmp"):
            mount["uid"] = SUBJ_UID
            mount["gid"] = SUBJ_GID
    return record


def _owner_profile_record() -> dict[str, Any]:
    record: dict[str, Any] = stl._profile_record()
    record["record"] = model.SCHEMA_PROFILE_V2
    record["codex_home_uid"] = SUBJ_UID
    return record


def _standin_record_aa(mode: str, **extra: object) -> dict[str, Any]:
    record = {
        "record": "slaif-fixture-standin-v1",
        "status": "pass",
        "mode": mode,
        "uid": SUBJ_UID,
    }
    record.update(extra)
    return record


class AAFakeDocker(stl.LocalFakeDocker):  # type: ignore[name-defined,misc]
    """The scripted fake docker over the AA world: the original
    closed surface PLUS the owner-scoped argv (build args, the
    owner tmpfs create spec, the frozen 1001:1002 exec user), the
    exact-CID top over the world's members, and the post-removal
    proc-world staging (the container's cgroup is gone: the owned
    members' proc frames leave EXACTLY per the staged scenario;
    the unrelated same-UID worker is never touched)."""

    def __init__(self, world: _World, proc_root: Path, *, rm_stage: str = "gone") -> None:
        super().__init__()
        self._world = world
        self.proc_root = proc_root
        self.rm_stage = rm_stage
        self.hold_calls: list[str] = []
        self.top_override: bytes | None = None
        self.top_rc = 0
        self.rm_rc = 0
        # The in-image controller's LAST quiesce measurement
        # against the world (the coherence proof: canned closure
        # facts are never inherited — the owned subject count is
        # measured from the world's held subject).
        self.last_quiesce: dict[str, Any] | None = None

    def __call__(self, argv: list[str], timeout: float) -> Any:
        # Container time advances with every operation: the
        # finite hold may expire (natural exit) before the query.
        self._world.expire_hold_if_due()
        if len(argv) >= 3 and argv[:2] == ["docker", "create"]:
            result = super().__call__(argv, timeout)
            if result.returncode == 0:
                self._world.attach(result.output.decode("ascii").strip())
                _write_proc_entry(
                    self.proc_root,
                    CTL_PID,
                    comm="python3",
                    start=CTL_START,
                    uid=CTL_UID,
                    gid=CTL_UID,
                    groups=(),
                    cgroup=self._world.cid,
                )
                _write_proc_entry(
                    self.proc_root,
                    WORKER_PID,
                    comm="worker",
                    start=WORKER_START,
                    uid=SUBJ_UID,
                    gid=SUBJ_UID,
                    groups=(),
                    cgroup=None,
                )
            return result
        if argv[:3] == ["docker", "exec", "-d"]:
            # The exact closed detached hold form the owner issues
            # (``docker exec -d --user U:G CID python3
            # <standin> --mode hold --hold-token TOKEN``): the
            # independent user at argv[4], the REGISTERED CID, the
            # frozen stand-in hold mode, the 32-hex run marker.
            # Anything else is refused, never interpreted.
            expected = [
                "--user",
                f"{SUBJ_UID}:{SUBJ_GID}",
                self._world.cid,
                "python3",
                fci.STANDIN_PATH,
                "--mode",
                "hold",
                "--hold-token",
            ]
            if (
                len(argv) != 12
                or argv[3:11] != expected
                or re.fullmatch(r"[0-9a-f]{32}", argv[11]) is None
            ):
                return self._result(125, b"exec-refused\n")
            self.hold_calls.append(argv[11])
            self._world.subject = {"cgroup": self._world.cid}
            self._world.subject_started_at = self._world.now()
            _write_proc_entry(
                self.proc_root,
                SUBJ_PID,
                comm="python3",
                start=SUBJ_START,
                uid=SUBJ_UID,
                gid=SUBJ_GID,
                groups=(SUBJ_GID,),
                cgroup=self._world.cid,
            )
            return self._result(0, b"")
        if len(argv) == 3 and argv[:2] == ["docker", "top"]:
            if self.top_override is not None:
                return self._result(self.top_rc, self.top_override)
            rows = "".join(f"slaifctl     {p}      python3\n" for p in self._world.member_pids())
            return self._result(0, b"UID          PID    COMMAND\n" + rows.encode("ascii"))
        if len(argv) >= 3 and argv[:2] == ["docker", "rm"]:
            if self.rm_rc:
                return self._result(self.rm_rc, b"")
            result = super().__call__(argv, timeout)
            if result.returncode == 0:
                self._stage_post_removal()
            return result
        if argv[:2] == ["docker", "inspect"] and "{{json .HostConfig}}" in argv:
            cfg = stl._host_config()
            cfg["Tmpfs"] = _owner_tmpfs_dict()
            return self._result(0, json.dumps(cfg).encode("ascii"))
        if (
            len(argv) >= 5
            and argv[1] == "exec"
            and argv[2] != "-d"
            and "--user" in argv
            and argv[argv.index("--user") + 1] == f"{CTL_UID}:{CTL_UID}"
            and argv[-2:] == ["python3", fci.EXPORT_CLIENT_PATH]
        ):
            # The 21001 export client: the in-image controller's
            # OWN quiesce measurement against the fake world
            # (the owned subject count is MEASURED from the
            # world's held subject — a still-holding subject is a
            # closed quiesce failure, exactly as in the real
            # controller; the canned all-closed record is never
            # inherited).
            quiesce = self._quiesce_record_measured()
            self.last_quiesce = quiesce
            payload = self._export_payload_bytes()
            sha = hashlib.sha256(payload).hexdigest()
            return self._result(
                0,
                b"quiesce-ok "
                + json.dumps(quiesce, sort_keys=True, separators=(",", ":")).encode()
                + b"\nexport-sha256 "
                + sha.encode()
                + b"\n"
                + payload,
            )
        if len(argv) >= 3 and argv[1] == "exec" and argv[2] != "-d" and "--user" in argv:
            if argv[argv.index("--user") + 1] == f"{SUBJ_UID}:{SUBJ_GID}":
                return self._owner_exec(argv)
        return super().__call__(argv, timeout)

    def _quiesce_record_measured(self) -> dict[str, Any]:
        # The closed quiesce facts as the in-image controller
        # would MEASURE them over the fake world: the owned
        # subject count is the world's held subject (the finite
        # hold process) — present means not stopped; the
        # controller's own socket/handler/tool closure is the
        # closed by-design fact of the fake platform.
        subjects = 1 if self._world.subject is not None else 0
        return {
            "record": model.SCHEMA_QUIESCE,
            "provider_sockets_closed": True,
            "handlers_stopped": True,
            "owned_subject_stopped": subjects == 0,
            "owned_tools_stopped": True,
            "active_connections": 0,
            "residual_writers": 0,
        }

    def _owner_exec(self, argv: list[str]) -> Any:
        cmd = argv[1:]
        i = 1
        itty = False
        if cmd[i] == "-it":
            itty = True
            i += 1
        assert cmd[i] == "--user"
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
        if (
            len(tail) == 4
            and tail[0] == "python3"
            and tail[1] == fci.STANDIN_PATH
            and tail[2] == "--mode"
        ):
            return self._owner_standin_exec(tail[3], itty, env, env_file)
        raise AssertionError(f"unexpected owner exec tail: {tail}")

    def _owner_standin_exec(
        self, mode: str, itty: bool, env: dict[str, str], env_file: str | None
    ) -> Any:
        profile = frp.owner_runtime_profile(_aa_description())
        if mode == "measure":
            assert env.get("SLAIF_FIXTURE_TMPFS_SPECS") == fci.owner_tmpfs_spec_env(profile)
            assert "SLAIF_FIXTURE_PRESENCE_SHA256" in env
            line = _owner_exec_measurement_record()
        elif mode == "pty":
            assert itty, "the pty rehearsal must attach through -it"
            assert len(env.get("SLAIF_RUN_TOKEN", "")) == 32
            assert env_file, "the local pty rehearsal must use the protected env file"
            self.env_file_path = env_file
            line = _standin_record_aa(
                "pty",
                pty_attached=True,
                term_rows=fci.PTY_ROWS,
                term_cols=fci.PTY_COLS,
                terminal_properties_closed_only=True,
                env_handoff_verified=True,
                workspace={"path": "/run/slaif-subj/work", "mode": 0o700, "uid": SUBJ_UID},
                profile=_owner_profile_record(),
            )
        elif mode == "observe":
            line = _standin_record_aa(
                "observe",
                scenario="diagnostic",
                wire_requests=0,
                diagnostic_state="unobserved",
                raw_content_retained=False,
            )
        else:
            raise AssertionError(f"unexpected owner standin mode: {mode}")
        out = (json.dumps(line, sort_keys=True, separators=(",", ":")) + "\n").encode()
        return self._result(0, out)

    def _stage_post_removal(self) -> None:
        """The container AND its cgroup are gone: the in-memory
        members disappear and the owned proc frames leave EXACTLY
        per the staged scenario (the unrelated worker's frame is
        never touched)."""
        root = self.proc_root
        stage = self.rm_stage
        self._world.subject = None
        self._world.controller = None
        for pid in (CTL_PID, SUBJ_PID):
            d = root / str(pid)
            if not d.is_dir():
                continue
            if stage == "recycled" and pid == CTL_PID:
                # A DIFFERENT birth at the same PID: PID reuse.
                (d / "stat").write_text(
                    stp.stat_line(CTL_PID, "python3", start=RECYCLED_START), encoding="ascii"
                )
            elif stage == "contradictory" and pid == CTL_PID:
                # The SAME birth with a changed UID: a
                # contradictory frame (neither reuse nor the
                # owned member).
                (d / "status").write_bytes(stp.status_bytes(21002, 21002, (21002,)))
            elif stage == "overbound" and pid == CTL_PID:
                (d / "stat").write_text(
                    stp.stat_line(CTL_PID, "python3", start=CTL_START) + " " + "x" * 8300,
                    encoding="ascii",
                )
            elif stage == "unreadable" and pid == CTL_PID:
                os.chmod(d / "stat", 0)
            elif stage == "leftover" and pid == CTL_PID:
                pass  # same birth AND uid kept: a real leftover
            else:
                shutil.rmtree(d)


# -- the synthetic 017-ab repository + hermetic seams -------------------------------


def _ab_git_fixture(base: Path) -> tuple[Path, str]:
    """A REAL synthetic git repository committing the CANONICAL
    FUTURE 017-ab sealed entry: actual git history so the public
    resolver's real read-only git path verifies the bound literal
    head, the committed active and the unique committed order
    bytes.  The S-shaped checkout content is copied and committed
    too — including the owner-variant Dockerfile, the inert
    identity module and the runtime-profile module the owner
    build-context phase reads from the repository."""
    root = base / "repo"
    root.mkdir(parents=True)

    def git(*args: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL)

    git("init", "-q")
    git("remote", "add", "origin", "https://github.com/ulfe-lmi/slaif-local-coding.git")
    (root / ".git" / "info" / "exclude").write_bytes(b"/.oap-local/\n")
    (root / "scripts").mkdir(parents=True)
    for name in (
        "cache_native_fixture_ci.py",
        "cache_native_fixture_model.py",
        "cache_native_fixture_controller.py",
        "cache_native_fixture_standin.py",
        "cache_native_fixture_export_client.py",
        "cache_native_fixture_local.py",
        "cache_native_fixture_native_prep.py",
        "cache_native_fixture_identity.py",
        "cache_native_fixture_runtime_profile.py",
        "cache_native_fixture.Dockerfile",
        "cache_native_fixture_owner.Dockerfile",
    ):
        (root / "scripts" / name).write_bytes((REPO_ROOT / "scripts" / name).read_bytes())
    (root / "Dockerfile").write_bytes((REPO_ROOT / "Dockerfile").read_bytes())
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "ci.yml").write_bytes(
        (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_bytes()
    )
    (root / "oap" / "orders").mkdir(parents=True)
    (root / "oap" / "orders" / S_ORDER_NAME).write_bytes(stl.ORDER_PATH.read_bytes())
    (root / "oap" / "orders" / AB_ORDER_NAME).write_bytes(AB_ORDER_BYTES)
    (root / "oap" / "active").write_bytes(AB_ORDER_ID.encode("ascii") + b"\n")
    git("add", "oap/active", f"oap/orders/{S_ORDER_NAME}", f"oap/orders/{AB_ORDER_NAME}")
    git("add", "scripts", "Dockerfile", ".github")
    git(
        "-c",
        "commit.gpgsign=false",
        "-c",
        "user.name=Synthetic",
        "-c",
        "user.email=synthetic@example.invalid",
        "commit",
        "-qm",
        "fixture",
    )
    head = git("rev-parse", "HEAD").decode("ascii").strip()
    return root, head


def _aa_hermetic(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fake: AAFakeDocker,
    control: Path,
    uid_calls: list[int],
) -> None:
    monkeypatch.setattr(fci, "fetch_public_artifact", stl._fake_fetch)
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

    def uid_spy(uid: int) -> int:
        # The global owner-UID scan trap: a zero stub must not
        # hide accidental use of the subject-UID global scan on
        # the owner-UID path; the controller-UID scan keeps its
        # historical semantics.
        uid_calls.append(uid)
        if uid == SUBJ_UID:
            raise AssertionError("global subject-UID scan attempted on the owner-UID path")
        return 0

    monkeypatch.setattr(fci, "_count_fixture_uid_processes", uid_spy)
    for var in flocal._LOCAL_ENDPOINT_SELECTION_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    sock = socket.socket(socket.AF_UNIX)
    sock_path = tmp_path / "docker.sock"
    sock.bind(str(sock_path))
    sock.close()
    monkeypatch.setattr(flocal, "_LOCAL_DOCKER_SOCKET", str(sock_path))
    fake._state_path = str(control / flocal._CONTROL_STATE_NAME)


def _aa_setup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    rm_stage: str = "gone",
) -> dict[str, Any]:
    repo, head = _ab_git_fixture(tmp_path / "repo")
    work = tmp_path / "work"
    control = tmp_path / "control"
    evidence = tmp_path / "evidence" / "ab-owner-evidence.json"
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _World(proc_root)
    docker = AAFakeDocker(world, proc_root, rm_stage=rm_stage)
    uid_calls: list[int] = []
    _aa_hermetic(tmp_path, monkeypatch, docker, control, uid_calls)
    return {
        "repo": repo,
        "head": head,
        "work": work,
        "control": control,
        "evidence": evidence,
        "proc_root": proc_root,
        "world": world,
        "docker": docker,
        "uid_calls": uid_calls,
    }


def _admit_ab(repo: Path, head: str) -> Any:
    binding = fb.resolve_order_binding(repo, AB_ORDER_ID, head)
    fb.admit_order_attempt(repo, AB_ORDER_ID, binding)
    return binding


def _reader() -> tuple[int, int, int, int, int, int]:
    return (SUBJ_UID, SUBJ_UID, SUBJ_UID, SUBJ_GID, SUBJ_GID, SUBJ_GID)


def _start_owner(paths: dict[str, Any], binding: Any, reader: Any) -> tuple[Any, threading.Thread]:
    owner = flocal.LocalFixtureOwner(
        paths["repo"],
        paths["work"],
        paths["evidence"],
        paths["head"],
        paths["control"],
        executor=paths["docker"],
        binding=binding,
        identity_reader=reader,
        proc_root=paths["proc_root"],
    )
    thread = threading.Thread(target=owner.serve, daemon=True)
    thread.start()
    end = time.monotonic() + 30.0
    while time.monotonic() < end:
        # The AB owner publishes the DISTINCT identity-bearing AB
        # state tag: the reader is entry-aware (the v1 tag/grammar
        # is never widened to the new profile record).
        if flocal._state_record(paths["control"], entry_order=AB_ORDER_ID) is not None:
            break
    else:
        pytest.fail("owner never published its initial state")
    return owner, thread


def _join_owner(
    thread: threading.Thread, *, control: Path, run_id: str, timeout: float = 60.0
) -> None:
    if thread.is_alive():
        with contextlib_suppress():
            stl._client(control, "abort", run_id, timeout=15.0)
    thread.join(timeout)
    if thread.is_alive():
        pytest.fail("owner thread did not converge after bounded abort")


def contextlib_suppress() -> Any:
    import contextlib

    return contextlib.suppress(Exception)


def _drive_prepare_hold(paths: dict[str, Any], run_id: str) -> dict[str, Any]:
    prepared = stl._client(paths["control"], "prepare", run_id)
    assert prepared["ok"] is True, prepared
    cid = str(prepared["detail"]["cid"])
    assert cid == paths["world"].cid, "the world must carry the ACTUAL created CID"
    held = stl._client(paths["control"], "hold", run_id)
    assert held["ok"] is True, held
    return {"cid": cid, "hold_token": str(held["detail"]["hold_token"])}


def _drive_finish(paths: dict[str, Any], run_id: str) -> dict[str, Any]:
    finished = stl._client(paths["control"], "finish", run_id)
    assert finished["ok"] is True, finished
    detail: dict[str, Any] = finished["detail"]
    return detail


# -- Part A: the narrow lifetime-frame boundaries -----------------------------------
# The production frame law (CID-attested pre-removal frame, the
# tri-stated post-removal raw reader) over fake /proc roots and a
# narrow scripted raw channel — swaps at each read boundary are
# refused, never adopted.

FRAME_CID = "c" * 64


class _FrameHarness:
    """Binds the production owner frame methods to a fake proc
    root (no owner construction, no admission)."""

    def __init__(self, proc_root: Path) -> None:
        self._proc_root = proc_root

    _owned_member_frame = flocal.LocalFixtureOwner._owned_member_frame
    _member_lifetime = flocal.LocalFixtureOwner._member_lifetime


class _ScriptedChannel:
    """The narrow fake raw channel: the scripted stat/status
    sequence for ONE exact PID (the production frame law runs on
    it: scope gating is the channel's job, the stability law is
    the frame's)."""

    def __init__(self, stats: list[bytes | None], status: bytes | None) -> None:
        self._stats = list(stats)
        self._status = status
        self.stat_calls = 0

    def stat(self, pid: int) -> bytes | None:
        value = self._stats[min(self.stat_calls, len(self._stats) - 1)]
        self.stat_calls += 1
        return value

    def status(self, pid: int) -> bytes | None:
        return self._status


def _stat_bytes(pid: int, start: int) -> bytes:
    raw: bytes = stp.stat_line(pid, "python3", start=start).encode("ascii")
    return raw


def _status_bytes(uid: int, gid: int, groups: tuple[int, ...]) -> bytes:
    raw: bytes = stp.status_bytes(uid, gid, groups)
    return raw


def test_owned_frame_stable_positive(tmp_path: Path) -> None:
    root = tmp_path / "proc"
    _write_proc_entry(
        root,
        42,
        comm="python3",
        start=123,
        uid=SUBJ_UID,
        gid=SUBJ_GID,
        groups=(SUBJ_GID,),
        cgroup=FRAME_CID,
    )
    table = fp.RealCidScopedTable(FRAME_CID, root=root)
    assert _FrameHarness(root)._owned_member_frame(42, table) == (123, SUBJ_UID)


def test_owned_frame_out_of_scope_refused(tmp_path: Path) -> None:
    root = tmp_path / "proc"
    _write_proc_entry(
        root,
        42,
        comm="worker",
        start=123,
        uid=SUBJ_UID,
        gid=SUBJ_UID,
        groups=(),
        cgroup=None,
    )
    table = fp.RealCidScopedTable(FRAME_CID, root=root)
    assert _FrameHarness(root)._owned_member_frame(42, table) is None


def test_owned_frame_no_entry_refused(tmp_path: Path) -> None:
    root = tmp_path / "proc"
    root.mkdir()
    table = fp.RealCidScopedTable(FRAME_CID, root=root)
    assert _FrameHarness(root)._owned_member_frame(42, table) is None


def test_owned_frame_cgroup_missing_refused(tmp_path: Path) -> None:
    root = tmp_path / "proc"
    _write_proc_entry(
        root,
        42,
        comm="python3",
        start=123,
        uid=SUBJ_UID,
        gid=SUBJ_GID,
        groups=(SUBJ_GID,),
        cgroup=FRAME_CID,
    )
    (root / "42" / "cgroup").unlink()
    table = fp.RealCidScopedTable(FRAME_CID, root=root)
    assert _FrameHarness(root)._owned_member_frame(42, table) is None


def test_owned_frame_overbound_stat_refused(tmp_path: Path) -> None:
    root = tmp_path / "proc"
    _write_proc_entry(
        root,
        42,
        comm="python3",
        start=123,
        uid=SUBJ_UID,
        gid=SUBJ_GID,
        groups=(SUBJ_GID,),
        cgroup=FRAME_CID,
    )
    (root / "42" / "stat").write_text(
        stp.stat_line(42, "python3", start=123) + " " + "x" * 8300, encoding="ascii"
    )
    table = fp.RealCidScopedTable(FRAME_CID, root=root)
    assert _FrameHarness(root)._owned_member_frame(42, table) is None


def test_owned_frame_scripted_stable() -> None:
    ch = _ScriptedChannel(
        [_stat_bytes(42, 123), _stat_bytes(42, 123)], _status_bytes(SUBJ_UID, SUBJ_GID, (SUBJ_GID,))
    )
    o = _FrameHarness(Path("/nonexistent"))
    assert o._owned_member_frame(42, ch) == (123, SUBJ_UID)


def test_owned_frame_scripted_second_stat_swap_refused() -> None:
    # The process identity changed in the second stat read (exit +
    # PID reuse in the window): a raced frame is never adopted.
    ch = _ScriptedChannel(
        [_stat_bytes(42, 123), _stat_bytes(42, 456)],
        _status_bytes(SUBJ_UID, SUBJ_GID, (SUBJ_GID,)),
    )
    o = _FrameHarness(Path("/nonexistent"))
    assert o._owned_member_frame(42, ch) is None


def test_owned_frame_scripted_status_window_gone_refused() -> None:
    # The member vanished between the first stat and the status
    # read: no stable combined frame.
    ch = _ScriptedChannel([_stat_bytes(42, 123), _stat_bytes(42, 123)], None)
    o = _FrameHarness(Path("/nonexistent"))
    assert o._owned_member_frame(42, ch) is None


def test_owned_frame_scripted_second_stat_gone_refused() -> None:
    # The member vanished between the status and the confirming
    # second stat read.
    ch = _ScriptedChannel(
        [_stat_bytes(42, 123), None], _status_bytes(SUBJ_UID, SUBJ_GID, (SUBJ_GID,))
    )
    o = _FrameHarness(Path("/nonexistent"))
    assert o._owned_member_frame(42, ch) is None


def test_owned_frame_scripted_pid_mismatch_refused() -> None:
    # The stat line's own pid field disagrees with the listed PID
    # in either read.
    ch = _ScriptedChannel(
        [_stat_bytes(43, 123), _stat_bytes(42, 123)], _status_bytes(SUBJ_UID, SUBJ_GID, (SUBJ_GID,))
    )
    o = _FrameHarness(Path("/nonexistent"))
    assert o._owned_member_frame(42, ch) is None
    ch2 = _ScriptedChannel(
        [_stat_bytes(42, 123), _stat_bytes(43, 123)], _status_bytes(SUBJ_UID, SUBJ_GID, (SUBJ_GID,))
    )
    assert o._owned_member_frame(42, ch2) is None


def test_member_lifetime_positive(tmp_path: Path) -> None:
    root = tmp_path / "proc"
    _write_proc_entry(
        root,
        42,
        comm="python3",
        start=123,
        uid=SUBJ_UID,
        gid=SUBJ_GID,
        groups=(SUBJ_GID,),
        cgroup=None,
    )
    assert _FrameHarness(root)._member_lifetime(42) == (123, SUBJ_UID)


def test_member_lifetime_gone(tmp_path: Path) -> None:
    root = tmp_path / "proc"
    root.mkdir()
    assert _FrameHarness(root)._member_lifetime(42) == "gone"


def test_member_lifetime_status_vanished_unverified(tmp_path: Path) -> None:
    root = tmp_path / "proc"
    _write_proc_entry(
        root,
        42,
        comm="python3",
        start=123,
        uid=SUBJ_UID,
        gid=SUBJ_GID,
        groups=(SUBJ_GID,),
        cgroup=None,
    )
    (root / "42" / "status").unlink()
    assert _FrameHarness(root)._member_lifetime(42) is None


def test_member_lifetime_stat_unreadable_unverified(tmp_path: Path) -> None:
    root = tmp_path / "proc"
    _write_proc_entry(
        root,
        42,
        comm="python3",
        start=123,
        uid=SUBJ_UID,
        gid=SUBJ_GID,
        groups=(SUBJ_GID,),
        cgroup=None,
    )
    os.chmod(root / "42" / "stat", 0)
    # EACCES is never conflated with verified-gone.
    assert _FrameHarness(root)._member_lifetime(42) is None


def test_member_lifetime_overbound_stat_refused(tmp_path: Path) -> None:
    root = tmp_path / "proc"
    _write_proc_entry(
        root,
        42,
        comm="python3",
        start=123,
        uid=SUBJ_UID,
        gid=SUBJ_GID,
        groups=(SUBJ_GID,),
        cgroup=None,
    )
    (root / "42" / "stat").write_text(
        stp.stat_line(42, "python3", start=123) + " " + "x" * 8300, encoding="ascii"
    )
    # An over-bound frame is refused, never silently truncated.
    assert _FrameHarness(root)._member_lifetime(42) is None


def test_member_lifetime_overbound_status_refused(tmp_path: Path) -> None:
    root = tmp_path / "proc"
    _write_proc_entry(
        root,
        42,
        comm="python3",
        start=123,
        uid=SUBJ_UID,
        gid=SUBJ_GID,
        groups=(SUBJ_GID,),
        cgroup=None,
    )
    (root / "42" / "status").write_bytes(b"Name:\tpython3\n" + b"x" * 9000)
    assert _FrameHarness(root)._member_lifetime(42) is None


def test_member_lifetime_pid_mismatch_refused(tmp_path: Path) -> None:
    root = tmp_path / "proc"
    _write_proc_entry(
        root,
        42,
        comm="python3",
        start=123,
        uid=SUBJ_UID,
        gid=SUBJ_GID,
        groups=(SUBJ_GID,),
        cgroup=None,
    )
    (root / "42" / "stat").write_text(stp.stat_line(43, "python3", start=123), encoding="ascii")
    assert _FrameHarness(root)._member_lifetime(42) is None


def test_member_lifetime_malformed_stat_refused(tmp_path: Path) -> None:
    root = tmp_path / "proc"
    _write_proc_entry(
        root,
        42,
        comm="python3",
        start=123,
        uid=SUBJ_UID,
        gid=SUBJ_GID,
        groups=(SUBJ_GID,),
        cgroup=None,
    )
    (root / "42" / "stat").write_text(b"not a stat line".decode("ascii"), encoding="ascii")
    assert _FrameHarness(root)._member_lifetime(42) is None


def test_member_lifetime_same_birth_changed_uid_reports_frame(tmp_path: Path) -> None:
    # The raw reader reports the measured frame; the
    # contradictory same-birth/changed-uid classification refusal
    # is the teardown law (covered by the lifecycle test).
    root = tmp_path / "proc"
    _write_proc_entry(
        root,
        42,
        comm="python3",
        start=123,
        uid=21002,
        gid=21002,
        groups=(21002,),
        cgroup=None,
    )
    assert _FrameHarness(root)._member_lifetime(42) == (123, 21002)


# -- Part B: the public owner lifecycle (useful 1001:1002) ---------------------------


def test_lifecycle_owner_uid_positive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The full useful owner-UID positive over the fake platform:
    the REAL owner (own collection/derivation, frozen context,
    owner-scoped guard, v2 record law) drives prepare -> hold ->
    finish to a pass with the EXACT registered-CID
    owned-lifetime proof: the held 1001:1002 subject runs its
    SAME finite hold and exits naturally (container time,
    absence only) BEFORE finish, so the export's quiesce
    MEASURES the subject gone (never a canned closure) and the
    EXACT registered-CID inventory at teardown lists the fixed
    21001 controller only — CID-attested before removal and
    verified-gone after; the unrelated same-UID worker and the
    real sentinel survive; no global subject-UID scan is ever
    attempted."""
    paths = _aa_setup(tmp_path, monkeypatch)
    binding = _admit_ab(paths["repo"], paths["head"])
    owner, thread = _start_owner(paths, binding, _reader)
    run_id = binding.run_id
    try:
        # The frozen context: independent uid/gid, never uid:uid.
        ctx = owner._owner_context
        assert ctx is not None
        assert (ctx.subject_uid, ctx.subject_gid) == (SUBJ_UID, SUBJ_GID)
        assert ctx.exec_user == f"{SUBJ_UID}:{SUBJ_GID}"
        assert ctx.subject_groups == (SUBJ_GID,)
        assert ctx.order_id == AB_ORDER_ID
        assert ctx.bind_head == paths["head"]
        _drive_prepare_hold(paths, run_id)
        # The finite hold elapses in CONTAINER time before finish:
        # the subject exits naturally (absence only — no exit
        # code or cause) BEFORE the export's quiesce measures it.
        # A still-holding subject is a closed quiesce failure (the
        # dedicated negative proves the fake measures, not
        # fabricates).
        paths["world"].advance(paths["world"].HOLD_SECONDS + 1.0)
        assert paths["world"].subject is None
        assert not (paths["proc_root"] / str(SUBJ_PID) / "stat").is_file()
        finished = _drive_finish(paths, run_id)
        assert finished["outcome"] == "pass", finished
    finally:
        _join_owner(thread, control=paths["control"], run_id=run_id)
    assert owner.terminal_outcome == "pass"
    # The owned-lifetime registry: at teardown the finite hold has
    # already exited, so the EXACT registered-CID inventory lists
    # the members actually remaining — the fixed controller only
    # (the subject frame is gone before removal and is never
    # re-adopted from an old list position).
    assert owner.owned_members_before == ((CTL_PID, CTL_START, CTL_UID),)
    # The remaining owned identity verified gone after the
    # exact-CID removal (coupled: the removal succeeded AND the
    # member is gone — not inferred from the count).
    assert owner.owned_members_after == ((CTL_PID, "verified-gone"),)
    assert owner.teardown_descendants_after == 0
    assert owner.descendants_before == 1
    # No global subject-UID scan; the controller scan may run.
    assert SUBJ_UID not in paths["uid_calls"]
    assert CTL_UID in paths["uid_calls"]
    # The unrelated same-UID worker survived the whole run.
    assert (paths["proc_root"] / str(WORKER_PID) / "stat").is_file()
    # The detached hold used the frozen independent exec user.
    assert len(paths["docker"].hold_calls) == 1
    # The export's quiesce MEASURED the subject gone (the
    # coherence fact: no canned closure inherited).
    assert paths["docker"].last_quiesce is not None
    assert paths["docker"].last_quiesce["owned_subject_stopped"] is True
    # The closed AB terminal evidence, validated by the production
    # validator, retains the frozen identity substructure and the
    # exact-CID teardown proof marker.
    evidence = json.loads(paths["evidence"].read_bytes())
    flocal.validate_ab_owner_run_evidence(evidence)
    assert evidence["record"] == flocal.AB_OWNER_RUN_EVIDENCE_SCHEMA
    assert evidence["order"] == AB_ORDER_ID
    assert evidence["status"] == "pass"
    assert evidence["teardown_proof"] == "exact-cid-membership"
    assert evidence["identity"]["subject_uid"] == SUBJ_UID
    assert evidence["identity"]["subject_gid"] == SUBJ_GID
    assert evidence["identity"]["subject_groups"] == [SUBJ_GID]
    assert evidence["identity"]["fingerprint"] == ctx.fingerprint
    assert (
        evidence["teardown"]["descendants_before"] == 1
        and evidence["teardown"]["descendants_after"] == 0
    )


def test_lifecycle_owner_uid_hold_alive_at_export_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The quiesce coherence law, negative side: when the finite
    hold has NOT elapsed in container time before finish, the
    in-image controller's quiesce MEASURES the subject alive
    (``owned_subject_stopped`` False) and the export's closed
    quiesce validation refuses — the run fails honestly with the
    closed reason, the exact-CID cleanup still converges (the
    still-holding subject is removed as part of the exact-owned
    removal, never signalled or waited on), and the honest fail
    evidence closes the closed AB grammar.  A canned all-closed
    quiesce record could not produce this: the fake measures the
    world, it never fabricates a zero."""
    paths = _aa_setup(tmp_path, monkeypatch)
    binding = _admit_ab(paths["repo"], paths["head"])
    owner, thread = _start_owner(paths, binding, _reader)
    run_id = binding.run_id
    try:
        _drive_prepare_hold(paths, run_id)
        # The container clock is NOT advanced: the finite hold is
        # still running at export time.
        assert paths["world"].subject is not None
        finished = stl._client(paths["control"], "finish", run_id)
        assert finished["ok"] is True, finished
        assert finished["detail"]["outcome"] == "fail", finished
        assert finished["detail"]["stage"] == "finish", finished
    finally:
        _join_owner(thread, control=paths["control"], run_id=run_id)
    assert owner.terminal_outcome == "fail"
    assert owner.failure_reason == "export-quiesce-state"
    # The fake MEASURED the live subject (the coherence fact):
    assert paths["docker"].last_quiesce is not None
    assert paths["docker"].last_quiesce["owned_subject_stopped"] is False
    # The primary failure is BEFORE the teardown phase, so the
    # pre-removal inventory was never measured (the honest record
    # keeps its initial unmeasured value, never an adopted one);
    # the exact-owned cleanup still converged and removed the
    # container (the subject frame left with it, absence only).
    assert owner.owned_members_before is None
    assert not (paths["proc_root"] / str(SUBJ_PID) / "stat").is_file()
    # The honest fail evidence closes the closed AB grammar.
    evidence = json.loads(paths["evidence"].read_bytes())
    flocal.validate_ab_owner_run_evidence(evidence)
    assert evidence["status"] == "fail"
    assert evidence["reason"] == "export-quiesce-state"
    assert evidence["stage"] == "finish"
    # No global subject-UID scan; the unrelated worker survives.
    assert SUBJ_UID not in paths["uid_calls"]
    assert (paths["proc_root"] / str(WORKER_PID) / "stat").is_file()


def _lifecycle_teardown_case(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    rm_stage: str,
    outcome: str,
    expected_after: tuple[tuple[int, str], ...] | None,
    expected_reason: str | None = None,
) -> None:
    """One post-removal staging scenario over the full lifecycle."""
    paths = _aa_setup(tmp_path, monkeypatch, rm_stage=rm_stage)
    binding = _admit_ab(paths["repo"], paths["head"])
    owner, thread = _start_owner(paths, binding, _reader)
    run_id = binding.run_id
    try:
        _drive_prepare_hold(paths, run_id)
        # Every scenario that reaches finish: the finite hold has
        # elapsed in container time (natural exit, absence only)
        # BEFORE the export's quiesce — the staged post-removal
        # fact is the CONTROLLER frame, the subject frame is
        # already gone.
        paths["world"].advance(paths["world"].HOLD_SECONDS + 1.0)
        finished = _drive_finish(paths, run_id)
        assert finished["outcome"] == outcome, finished
    finally:
        _join_owner(thread, control=paths["control"], run_id=run_id)
    assert owner.terminal_outcome == outcome
    if expected_after is not None:
        assert owner.owned_members_after == expected_after
    evidence = json.loads(paths["evidence"].read_bytes())
    flocal.validate_ab_owner_run_evidence(evidence)
    assert evidence["order"] == AB_ORDER_ID
    assert evidence["status"] == ("pass" if outcome == "pass" else "fail")
    if expected_reason is not None:
        assert evidence["reason"] == expected_reason
    # In every scenario: no global subject-UID scan, and the
    # unrelated same-UID worker survives.
    assert SUBJ_UID not in paths["uid_calls"]
    assert (paths["proc_root"] / str(WORKER_PID) / "stat").is_file()


def test_lifecycle_teardown_still_existing_leftover(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A frame with the SAME birth AND uid after removal: the owned
    # member (the fixed controller — the subject's finite hold has
    # already exited naturally before finish) is a real leftover —
    # a closed refusal, never a pass.
    _lifecycle_teardown_case(
        tmp_path,
        monkeypatch,
        rm_stage="leftover",
        outcome="fail",
        expected_after=((CTL_PID, "still-existing"),),
        expected_reason="descendant-leftover",
    )


def test_lifecycle_teardown_contradictory_frame(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The SAME birth with a CHANGED uid after removal: a
    # contradictory frame — neither the owned member (frame
    # mismatch) nor a proven reuse (no birth change): refused,
    # never classified.
    _lifecycle_teardown_case(
        tmp_path,
        monkeypatch,
        rm_stage="contradictory",
        outcome="fail",
        # The contradictory frame refuses DURING the post-removal
        # loop: the after-registry is never finalized (None).
        expected_after=None,
        expected_reason="descendant-unverified",
    )


def test_lifecycle_teardown_recycled_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # A DIFFERENT birth at the same PID after removal: ONLY a
    # changed birth proves PID reuse — the owned member is gone
    # and the occupant is a different process, never mislabeled,
    # signalled or counted as one.
    _lifecycle_teardown_case(
        tmp_path,
        monkeypatch,
        rm_stage="recycled",
        outcome="pass",
        expected_after=((CTL_PID, "recycled"),),
    )


def test_lifecycle_teardown_overbound_frame(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # An over-bound post-removal frame: refused (unknown), never
    # truncated into a fake verification.
    _lifecycle_teardown_case(
        tmp_path,
        monkeypatch,
        rm_stage="overbound",
        outcome="fail",
        expected_after=None,
        expected_reason="descendant-unverified",
    )


def test_lifecycle_teardown_unreadable_frame(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # An unreadable (EACCES) post-removal frame: never conflated
    # with verified-gone.
    _lifecycle_teardown_case(
        tmp_path,
        monkeypatch,
        rm_stage="unreadable",
        outcome="fail",
        expected_after=None,
        expected_reason="descendant-unverified",
    )


def test_lifecycle_pre_teardown_raced_member(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A listed member with NO proc frame at the CID-attested read
    # (exited between the top listing and the frame read): list
    # position alone is not ownership — a closed refusal before
    # removal, never a silently ignored member.
    paths = _aa_setup(tmp_path, monkeypatch)
    paths["world"].race_pids.add(88)
    binding = _admit_ab(paths["repo"], paths["head"])
    owner, thread = _start_owner(paths, binding, _reader)
    run_id = binding.run_id
    try:
        _drive_prepare_hold(paths, run_id)
        # The finite hold elapses in container time before finish
        # (the subject exits naturally); the pre-removal inventory
        # then lists the controller AND the raced member — the
        # subject frame is already gone.
        paths["world"].advance(paths["world"].HOLD_SECONDS + 1.0)
        finished = _drive_finish(paths, run_id)
        assert finished["outcome"] == "fail", finished
        assert finished["stage"] == "teardown", finished
    finally:
        _join_owner(thread, control=paths["control"], run_id=run_id)
    assert owner.terminal_outcome == "fail"
    # The pre-removal registry never adopted the raced PID.
    assert owner.owned_members_before is None
    assert owner.descendants_before == 2
    evidence = json.loads(paths["evidence"].read_bytes())
    flocal.validate_ab_owner_run_evidence(evidence)
    assert evidence["reason"] == "descendant-unverified"
    assert SUBJ_UID not in paths["uid_calls"]
    assert (paths["proc_root"] / str(WORKER_PID) / "stat").is_file()


def test_lifecycle_identity_drift_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # The owner's OWN collection freezes the context at
    # construction; a changed host identity at actual use (the
    # bounded current-ID coherence read) is a closed refusal
    # BEFORE any fixture work — never a silent rebase.
    paths = _aa_setup(tmp_path, monkeypatch)
    binding = _admit_ab(paths["repo"], paths["head"])
    holder = {"ids": (SUBJ_UID, SUBJ_UID, SUBJ_UID, SUBJ_GID, SUBJ_GID, SUBJ_GID)}

    def reader() -> tuple[int, int, int, int, int, int]:
        return holder["ids"]

    owner, thread = _start_owner(paths, binding, reader)
    run_id = binding.run_id
    try:
        holder["ids"] = (1003, 1003, 1003, 1004, 1004, 1004)
        prepared = stl._client(paths["control"], "prepare", run_id)
        assert prepared["ok"] is False, prepared
        assert prepared["reason"] == "local-identity-drift", prepared
    finally:
        _join_owner(thread, control=paths["control"], run_id=run_id)
    assert owner.terminal_outcome == "fail"
    assert owner.failure_reason == "local-identity-drift"
    # The frozen context stays the construction-time identity.
    assert (owner._owner_context.subject_uid, owner._owner_context.subject_gid) == (
        SUBJ_UID,
        SUBJ_GID,
    )
    assert SUBJ_UID not in paths["uid_calls"]


def test_lifecycle_identity_drift_after_hold_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # LATE drift: the host identity changes AFTER prepare/hold
    # and BEFORE finish.  The FROZEN context is revalidated at
    # finish's identity-bound use (the bounded current-ID
    # coherence read through the SAME seam) — the drift is a
    # closed refusal at the finish stage (no rebase, no adoption
    # of the new IDs), the exact-owned cleanup still converges,
    # and the terminal evidence retains the FROZEN identity,
    # never the drifted one.
    paths = _aa_setup(tmp_path, monkeypatch)
    binding = _admit_ab(paths["repo"], paths["head"])
    holder = {"ids": (SUBJ_UID, SUBJ_UID, SUBJ_UID, SUBJ_GID, SUBJ_GID, SUBJ_GID)}

    def reader() -> tuple[int, int, int, int, int, int]:
        return holder["ids"]

    owner, thread = _start_owner(paths, binding, reader)
    run_id = binding.run_id
    try:
        _drive_prepare_hold(paths, run_id)
        ctx = owner._owner_context
        assert ctx is not None
        # The drift begins AFTER the run (prepare/hold already
        # revalidated the SAME frozen context successfully).
        holder["ids"] = (1003, 1003, 1003, 1004, 1004, 1004)
        finished = stl._client(paths["control"], "finish", run_id)
        assert finished["ok"] is True, finished
        assert finished["detail"]["outcome"] == "fail", finished
        assert finished["detail"]["stage"] == "finish", finished
    finally:
        _join_owner(thread, control=paths["control"], run_id=run_id)
    assert owner.terminal_outcome == "fail"
    assert owner.failure_reason == "local-identity-drift"
    # The frozen context was never rebased: the terminal evidence
    # retains the construction-time identity.
    assert (owner._owner_context.subject_uid, owner._owner_context.subject_gid) == (
        SUBJ_UID,
        SUBJ_GID,
    )
    evidence = json.loads(paths["evidence"].read_bytes())
    flocal.validate_ab_owner_run_evidence(evidence)
    assert evidence["status"] == "fail"
    assert evidence["reason"] == "local-identity-drift"
    assert evidence["stage"] == "finish"
    assert evidence["identity"]["subject_uid"] == SUBJ_UID
    assert evidence["identity"]["subject_gid"] == SUBJ_GID
    assert evidence["identity"]["fingerprint"] == ctx.fingerprint
    # The exact-owned cleanup converged without any global
    # subject-UID scan (for either identity); the unrelated
    # same-UID worker survives.
    assert SUBJ_UID not in paths["uid_calls"]
    assert (paths["proc_root"] / str(WORKER_PID) / "stat").is_file()


def test_lifecycle_guard_refuses_foreign_exec_user(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The owner-scoped guarded allowlist admits ONLY the frozen
    # profile's exact independent exec user for subject work: a
    # foreign user on the same command is refused before
    # execution (counted as a refusal, never run).
    paths = _aa_setup(tmp_path, monkeypatch)
    binding = _admit_ab(paths["repo"], paths["head"])
    owner, thread = _start_owner(paths, binding, _reader)
    run_id = binding.run_id
    try:
        _drive_prepare_hold(paths, run_id)
        cid = paths["world"].cid
        assert cid is not None
        with pytest.raises(FixtureError) as exc:
            owner.guarded(
                [
                    "docker",
                    "exec",
                    "-d",
                    "--user",
                    "1001:1001",
                    cid,
                    "python3",
                    fci.STANDIN_PATH,
                    "--mode",
                    "hold",
                    "--hold-token",
                    "f" * 32,
                ],
                10.0,
            )
        assert str(exc.value) == "argv-untrusted"
        # The refused argv never reached the executor.
        assert len(paths["docker"].hold_calls) == 1
        # The finite hold elapses in container time before finish
        # (the subject exits naturally), so the export's quiesce
        # measures the subject gone and the run converges to its
        # useful pass.
        paths["world"].advance(paths["world"].HOLD_SECONDS + 1.0)
    finally:
        _drive_finish(paths, run_id)
        _join_owner(thread, control=paths["control"], run_id=run_id)
    assert owner.terminal_outcome == "pass"


# -- Part C: the closed AB terminal evidence validator ------------------------------


def _ab_identity() -> dict[str, Any]:
    desc = _aa_description()
    return {
        "profile": desc.profile,
        "fingerprint": fi.fingerprint_description(desc),
        "subject_uid": SUBJ_UID,
        "subject_gid": SUBJ_GID,
        "subject_groups": [SUBJ_GID],
        "profile_data_sha256": hashlib.sha256(fi.encode_description(desc)).hexdigest(),
    }


def _zero_ledger() -> dict[str, int]:
    return dict(flocal._ledger_facts(fci._RunLedger(model.FixtureBudgets())))


def _fail_substructure() -> dict[str, Any]:
    return {
        "status": "fail",
        "order": AB_ORDER_ID,
        "run_id": "a" * 32,
        "bind_head": "b" * 40,
        "deadline_expired": False,
        "ledger": _zero_ledger(),
        "runner_kernel": "x",
        "runner_arch": "x86_64",
        "runner_python": "3.12.0",
        "reason": "descendant-unverified",
        "stage": "teardown",
        "cleanup_failures": [],
        # The closed phase tokens actually completed BEFORE the
        # failing teardown stage (``finish`` is phase-done before
        # teardown; teardown/publish are the unfinished tail):
        "phases_completed": sorted(p for p in flocal._PHASES if p not in ("teardown", "publish")),
        "resources": {
            "containers": [],
            "create_intent": None,
            "image_id": None,
            "build_attempted": True,
            "env_file": None,
        },
        "recovery_state_retained": False,
    }


def _ab_fail_record(**overrides: Any) -> dict[str, Any]:
    record = {
        "record": flocal.AB_OWNER_RUN_EVIDENCE_SCHEMA,
        "scope": flocal.AB_OWNER_RUN_SCOPE,
        "teardown_proof": "exact-cid-membership",
        "identity": _ab_identity(),
    }
    record.update(_fail_substructure())
    record.update(overrides)
    return record


def test_ab_evidence_canonical_fail_positive() -> None:
    # The useful canonical AB fail record of the 017-ab entry:
    # valid closed substructures, codec-intact identity.
    flocal.validate_ab_owner_run_evidence(_ab_fail_record())


def test_ab_evidence_foreign_order_refused() -> None:
    # The AB-tagged grammar is the canonical AB entry ONLY: an
    # AB record of any other order id is refused (the old native
    # generic-order law is the native validator's own and stays
    # unchanged).
    for order in ("017-x", "017-y", "017-v"):
        record = _ab_fail_record(order=order)
        with pytest.raises(FixtureError):
            flocal.validate_ab_owner_run_evidence(record)


def test_ab_evidence_tamper_refusals() -> None:
    # Wrong tag/scope/marker, broken codec integrity, broken
    # identity field laws and key-set drift are all refused.
    cases: list[tuple[str, Any]] = []
    tampered_digest = dict(_ab_identity())
    tampered_digest["profile_data_sha256"] = "0" * 64
    cases.append(("digest", _ab_fail_record(identity=tampered_digest)))
    tampered_fp = dict(_ab_identity())
    tampered_fp["fingerprint"] = "1" * 64
    cases.append(("fingerprint", _ab_fail_record(identity=tampered_fp)))
    tampered_groups = dict(_ab_identity())
    tampered_groups["subject_groups"] = [SUBJ_UID]
    cases.append(("groups", _ab_fail_record(identity=tampered_groups)))
    tampered_profile = dict(_ab_identity())
    tampered_profile["profile"] = fi.PROFILE_ORIGINAL
    cases.append(("profile", _ab_fail_record(identity=tampered_profile)))
    cases.append(
        (
            "tag",
            _ab_fail_record(record=flocal.NATIVE_OWNER_RUN_EVIDENCE_SCHEMA),
        )
    )
    cases.append(("scope", _ab_fail_record(scope=flocal.NATIVE_OWNER_RUN_SCOPE)))
    cases.append(("marker", _ab_fail_record(teardown_proof="uid-scan")))
    no_identity = _ab_fail_record()
    del no_identity["identity"]
    cases.append(("missing-identity", no_identity))
    no_marker = _ab_fail_record()
    del no_marker["teardown_proof"]
    cases.append(("missing-marker", no_marker))
    extra = _ab_fail_record(extra_key=1)
    cases.append(("extra-key", extra))
    for _name, record in cases:
        with pytest.raises(FixtureError):
            flocal.validate_ab_owner_run_evidence(record)


def test_native_evidence_generic_order_law_unchanged() -> None:
    # The native-scope record keeps its generic new-order law
    # (any order id) and the fixed-21002 subject law: the same
    # substructure under the native tags of 017-x validates.
    record = {
        "record": flocal.NATIVE_OWNER_RUN_EVIDENCE_SCHEMA,
        "scope": flocal.NATIVE_OWNER_RUN_SCOPE,
    }
    record.update(_fail_substructure())
    record["order"] = "017-x"
    flocal.validate_native_owner_run_evidence(record)


# -- Part D: the in-image controller's owner-profile quiesce accounting -------
#
# The closed law the real in-image controller now enforces: the
# quiesce subject is resolved from the SAME fixed image-owned
# identity facts (mode constant parsed never executed, DATA
# decoded never imported) BEFORE any scan — the original image
# (absent marker) keeps the fixed-21002 subject law byte-for-byte
# and never imports the identity module at all (the original
# image does not carry it), and a corrupted owner image fails the
# quiesce closed.  Only the raw lstat/open OS seams are faked
# (the exact pattern of the stand-in image-mode law); every
# state/size/grammar/codec check runs as production code.


def _ctl_resolution_case(
    monkeypatch: pytest.MonkeyPatch,
    files: dict[str, bytes],
    expect: int | str,
    *,
    overrides: dict[str, object] | None = None,
    block_identity_module: bool = False,
) -> None:
    overrides = overrides or {}

    def lstat(path: str) -> Any:
        if path in overrides:
            value = overrides[path]
            if isinstance(value, BaseException):
                raise value
            return value
        if path not in files:
            raise FileNotFoundError(errno.ENOENT, "synthetic absent", path)
        return SimpleNamespace(
            st_mode=stat.S_IFREG | 0o444,
            st_uid=0,
            st_gid=0,
            st_size=len(files[path]),
        )

    class Reader(io.BytesIO):
        def read(self, n: int | None = -1) -> bytes:
            if n is None or n < 0:
                raise AssertionError("unbounded read")
            return super().read(n)

    def open_file(path: str, mode: str = "rb") -> Any:
        assert mode == "rb"
        if path not in files:
            raise FileNotFoundError(errno.ENOENT, "synthetic absent", path)
        return Reader(files[path])

    monkeypatch.setattr(fctl.os, "lstat", lstat)
    monkeypatch.setattr("builtins.open", open_file)
    if block_identity_module:
        monkeypatch.setitem(sys.modules, "cache_native_fixture_identity", None)
    if isinstance(expect, int):
        assert fctl.quiesce_subject_uid() == expect
    else:
        with pytest.raises(fctl.ControllerError) as exc:
            fctl.quiesce_subject_uid()
        assert str(exc.value) == expect


def test_controller_quiesce_accounting_original_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # No marker (the original image): the fixed-21002 quiesce
    # subject law — and the identity module is NEVER imported
    # (blocked to prove it; the original image does not carry it).
    _ctl_resolution_case(monkeypatch, {}, fctl.SUBJECT_UID, block_identity_module=True)
    assert fctl.SUBJECT_UID == 21002


def test_controller_quiesce_accounting_owner_frozen_subject_uid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The explicit owner marker + the bounded immutable DATA: the
    # quiesce subject is the DATA's frozen INDEPENDENT subject UID
    # (never uid:uid, never the original subject).
    owner_marker = (
        'SLAIF_FIXTURE_IDENTITY_PROFILE = "slaif-fixture-identity-owner-uid-v1"\n'
    ).encode("ascii")
    _ctl_resolution_case(
        monkeypatch,
        {
            fctl.IDENTITY_PROFILE_FILE: owner_marker,
            fctl.PROFILE_DATA_PATH: fi.encode_description(_aa_description()),
        },
        SUBJ_UID,
    )
    assert SUBJ_UID != SUBJ_GID, "the useful pair is independent uid/gid"


def test_controller_quiesce_accounting_explicit_original_ignores_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The explicit ORIGINAL marker value behaves like an absent
    # marker even when a valid owner DATA file sits at the path —
    # a file's presence never selects the mode; the identity
    # module is never imported in this path either.
    original_marker = (
        'SLAIF_FIXTURE_IDENTITY_PROFILE = "slaif-fixture-identity-original-v1"\n'
    ).encode("ascii")
    _ctl_resolution_case(
        monkeypatch,
        {
            fctl.IDENTITY_PROFILE_FILE: original_marker,
            fctl.PROFILE_DATA_PATH: fi.encode_description(_aa_description()),
        },
        fctl.SUBJECT_UID,
        block_identity_module=True,
    )


def test_controller_quiesce_accounting_owner_corrupted_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Every corrupted-owner case refuses with a fixed token —
    # never the original subject, never a silent zero.
    owner_marker = (
        'SLAIF_FIXTURE_IDENTITY_PROFILE = "slaif-fixture-identity-owner-uid-v1"\n'
    ).encode("ascii")
    valid_data = fi.encode_description(_aa_description())
    # The controller identity is FIXED 21001/21001 by the codec's
    # own field law (a foreign controller cannot even be encoded
    # as a valid record), so the mismatch is exercised as closed
    # record BYTES whose controller identity does not match the
    # production law — decode refuses, the quiesce refuses.
    foreign_controller = valid_data.replace(
        b'"controller":{"gid":21001,"uid":21001}',
        b'"controller":{"gid":21003,"uid":21003}',
    )
    assert foreign_controller != valid_data
    # The canonical record of the ORIGINAL profile carries its
    # own fixed identity law (21002 subject): a valid closed
    # record whose profile is simply not the owner one.
    original_profile_data = fi.encode_description(
        fi.FixtureIdentityDescription(
            profile=fi.PROFILE_ORIGINAL,
            controller_uid=fi.CONTROLLER_UID,
            controller_gid=fi.CONTROLLER_GID,
            subject_uid=21002,
            subject_gid=21002,
            subject_groups=(21002,),
        )
    )
    cases: list[tuple[str, dict[str, bytes], str, dict[str, object], bool]] = [
        (
            "owner-missing-data",
            {fctl.IDENTITY_PROFILE_FILE: owner_marker},
            "quiesce-data-missing",
            {},
            False,
        ),
        (
            "owner-data-wrong-profile",
            {
                fctl.IDENTITY_PROFILE_FILE: owner_marker,
                fctl.PROFILE_DATA_PATH: original_profile_data,
            },
            "quiesce-data-invalid",
            {},
            False,
        ),
        (
            "owner-data-controller-mismatch",
            {
                fctl.IDENTITY_PROFILE_FILE: owner_marker,
                fctl.PROFILE_DATA_PATH: foreign_controller,
            },
            "quiesce-data-invalid",
            {},
            False,
        ),
        (
            "owner-data-malformed",
            {
                fctl.IDENTITY_PROFILE_FILE: owner_marker,
                fctl.PROFILE_DATA_PATH: b"not-a-closed-record",
            },
            "quiesce-data-invalid",
            {},
            False,
        ),
        (
            "owner-data-oversized",
            {
                fctl.IDENTITY_PROFILE_FILE: owner_marker,
                fctl.PROFILE_DATA_PATH: b"x" * (fi.MAX_RECORD_BYTES + 1),
            },
            "quiesce-data-size",
            {},
            False,
        ),
        (
            "owner-data-writable",
            {fctl.IDENTITY_PROFILE_FILE: owner_marker},
            "quiesce-data-state",
            {
                fctl.PROFILE_DATA_PATH: SimpleNamespace(
                    st_mode=stat.S_IFREG | 0o644,
                    st_uid=0,
                    st_gid=0,
                    st_size=len(valid_data),
                )
            },
            False,
        ),
        (
            "owner-data-foreign-owner",
            {fctl.IDENTITY_PROFILE_FILE: owner_marker},
            "quiesce-data-state",
            {
                fctl.PROFILE_DATA_PATH: SimpleNamespace(
                    st_mode=stat.S_IFREG | 0o444,
                    st_uid=1001,
                    st_gid=1002,
                    st_size=len(valid_data),
                )
            },
            False,
        ),
        (
            "owner-module-missing",
            {
                fctl.IDENTITY_PROFILE_FILE: owner_marker,
                fctl.PROFILE_DATA_PATH: valid_data,
            },
            "quiesce-profile-module",
            {},
            True,
        ),
        (
            "mode-unknown-value",
            {fctl.IDENTITY_PROFILE_FILE: (b'SLAIF_FIXTURE_IDENTITY_PROFILE = "foreign"\n')},
            "quiesce-profile-unknown",
            {},
            False,
        ),
        (
            "mode-extra-statement",
            {fctl.IDENTITY_PROFILE_FILE: owner_marker + b'print("no")\n'},
            "quiesce-profile-grammar",
            {},
            False,
        ),
        (
            "mode-eacces-is-not-absence",
            {fctl.PROFILE_DATA_PATH: valid_data},
            "quiesce-profile-lookup",
            {fctl.IDENTITY_PROFILE_FILE: PermissionError(errno.EACCES, "synthetic denied")},
            False,
        ),
        (
            "mode-eio-is-not-absence",
            {fctl.PROFILE_DATA_PATH: valid_data},
            "quiesce-profile-lookup",
            {fctl.IDENTITY_PROFILE_FILE: OSError(errno.EIO, "synthetic I/O failure")},
            False,
        ),
        (
            "mode-symlink",
            {fctl.PROFILE_DATA_PATH: valid_data},
            "quiesce-profile-state",
            {
                fctl.IDENTITY_PROFILE_FILE: SimpleNamespace(
                    st_mode=stat.S_IFLNK | 0o777,
                    st_uid=0,
                    st_gid=0,
                    st_size=10,
                )
            },
            False,
        ),
        (
            "mode-foreign-owner",
            {fctl.PROFILE_DATA_PATH: valid_data},
            "quiesce-profile-state",
            {
                fctl.IDENTITY_PROFILE_FILE: SimpleNamespace(
                    st_mode=stat.S_IFREG | 0o444,
                    st_uid=1001,
                    st_gid=1002,
                    st_size=len(owner_marker),
                )
            },
            False,
        ),
    ]
    for name, files, expect, overrides, block in cases:
        try:
            _ctl_resolution_case(
                monkeypatch,
                files,
                expect,
                overrides=overrides,
                block_identity_module=block,
            )
        except (AssertionError, fctl.ControllerError) as exc:
            pytest.fail(f"{name}: {type(exc).__name__}: {exc}")


# -- the closed RuntimeProfile construction law (pure DATA) ------------------
def _aa_profile_clone(base: Any, **changes: Any) -> Any:
    import dataclasses

    kw = {f.name: getattr(base, f.name) for f in dataclasses.fields(base)}
    kw.update(changes)
    return frp.RuntimeProfile(**kw)


def _aa_profile_refused(fn: Any) -> None:
    try:
        fn()
    except frp.ProfileError:
        return
    raise AssertionError("accepted-invalid-profile-data")


def test_runtime_profile_closed_construction() -> None:
    """The maintained closed construction law for the runtime
    profile view (pure DATA — never admission or readiness
    authority): useful original and independent-UID/GID
    positives; equal numeric tuples under distinct profiles stay
    isolated; caller containers are owned (no mutable alias
    retained, bounded length checked BEFORE any copy); and the
    complete field/profile/exec-user/build-arg/profile-DATA
    consistency law refuses every invalid view with a fixed
    non-echoing error."""
    original = frp.original_runtime_profile()
    assert original.exec_user == "21002:21002"
    assert original.profile_data is None
    assert original.build_args == ()

    def owner(u: int, g: int) -> Any:
        return frp.entry_runtime_profile(
            AB_ORDER_ID,
            fi.derive_owner_uid_identity(fi.HostOwnerIds(u, u, u, g, g, g)),
        )

    prof = owner(SUBJ_UID, SUBJ_GID)
    assert prof.exec_user == "1001:1002"  # INDEPENDENT uid:gid, never uid:uid
    assert prof.expected_groups == (SUBJ_GID,)
    assert fi.decode_description(prof.profile_data).subject_gid == SUBJ_GID
    equal_numeric = owner(21002, 21002)
    assert equal_numeric.profile != original.profile
    assert equal_numeric.profile_data is not None

    # -- the caller's containers are owned, never aliased -----------
    def groups_owned() -> None:
        v = [SUBJ_GID]
        o = _aa_profile_clone(prof, expected_groups=v)
        v.append(9999)
        assert o.expected_groups == (SUBJ_GID,) and isinstance(o.expected_groups, tuple)

    def argv_owned() -> None:
        v = list(prof.build_args)
        o = _aa_profile_clone(prof, build_args=v)
        v.append("--arbitrary-extra")
        assert o.build_args == prof.build_args and isinstance(o.build_args, tuple)

    def bytes_owned() -> None:
        v = bytearray(prof.profile_data)
        o = _aa_profile_clone(prof, profile_data=v)
        v[:] = b"changed"
        assert o.profile_data == prof.profile_data and isinstance(o.profile_data, bytes)

    for fn in (groups_owned, argv_owned, bytes_owned):
        fn()

    class _NoIteration(list[object]):
        def __iter__(self) -> Any:
            raise AssertionError("copied-before-bound")

    # the bound is enforced BEFORE the copy (no iteration happens)
    _aa_profile_refused(
        lambda: _aa_profile_clone(prof, expected_groups=_NoIteration([SUBJ_GID, 1003]))
    )
    _aa_profile_refused(lambda: _aa_profile_clone(prof, build_args=_NoIteration([None] * 4097)))

    # -- the complete field/profile/consistency law ------------------
    for _name, changes in (
        ("unknown-profile", {"profile": "other"}),
        ("boolean-uid", {"subject_uid": True}),
        ("root-uid", {"subject_uid": 0}),
        ("controller-uid", {"subject_uid": 21001}),
        ("controller-gid", {"subject_gid": 21001}),
        ("overflow-gid", {"subject_gid": 4294967295}),
        ("inconsistent-exec-user", {"exec_user": "1001:1001"}),
        ("foreign-effective-group", {"expected_groups": (1003,)}),
        ("nested-mutable-group", {"expected_groups": ([SUBJ_GID],)}),
        ("missing-build-args", {"build_args": ()}),
        ("extra-build-arg", {"build_args": prof.build_args + ("--arbitrary",)}),
        (
            "wrong-baked-profile-data",
            {"profile_data": fi.encode_description(fi.original_fixture_identity())},
        ),
        ("missing-baked-owner-data", {"profile_data": None}),
    ):
        _aa_profile_refused(lambda changes=changes: _aa_profile_clone(prof, **changes))

    # -- the closed entry selection law --------------------------------
    _aa_profile_refused(lambda: frp.entry_runtime_profile("017-aa"))
    _aa_profile_refused(lambda: frp.entry_runtime_profile("017-s", fi.original_fixture_identity()))
    _aa_profile_refused(
        lambda: frp.entry_runtime_profile(AB_ORDER_ID, fi.original_fixture_identity())
    )


def test_v2_reserved_controller_id_refused() -> None:
    """The maintained v2 subject/profile ID law: the reserved
    controller identity (UID 21001 OR GID 21001) is never a
    legal subject expectation in the new physical-identity law,
    while the useful independent 1001/1002 subject is admitted
    (pure data validation; no measured-authority claim)."""
    import dataclasses

    def exec_case(uid: int, gid: int, expected: bool) -> None:
        record = _owner_exec_measurement_record()
        record.update(record=model.SCHEMA_EXEC_MEASUREMENT_V2, uid=uid, gid=gid)
        budgets = model.FixtureBudgets()
        mounts = []
        for name, size, u, g in budgets.tmpfs_budgets:
            mounts.append((name, size, uid if u == 21002 else u, gid if g == 21002 else g))
        for entry in record["writable_mounts"]:
            if entry["uid"] == 21002:
                entry["uid"] = uid
            if entry["gid"] == 21002:
                entry["gid"] = gid
        budgets = dataclasses.replace(budgets, tmpfs_budgets=tuple(mounts))
        try:
            model.validate_exec_measurement_v2(record, budgets, uid, gid)
            accepted = True
        except model.FixtureError:
            accepted = False
        assert accepted is expected, (uid, gid, accepted)

    for uid, gid, expected in (
        (1001, 1002, True),
        (21001, 1002, False),
        (1001, 21001, False),
        (21001, 21001, False),
    ):
        exec_case(uid, gid, expected)

    for uid, expected in ((1001, True), (21001, False)):
        record = _owner_profile_record()
        record.update(record=model.SCHEMA_PROFILE_V2, codex_home_uid=uid)
        try:
            model.validate_profile_record_v2(record, uid)
            accepted = True
        except model.FixtureError:
            accepted = False
        assert accepted is expected, (uid, accepted)
