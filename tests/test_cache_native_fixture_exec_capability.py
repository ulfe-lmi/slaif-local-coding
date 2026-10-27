"""017-x live Python executable capability — focused public fake tests.

These tests drive the ACTUAL public X surface (the owner's closed
``hold``/``top`` control commands, the sealed child resolve+admit
CLI entry, the closed capability-record retention/validator and the
capability driver) over injected FAKE external operations only:
fake git, fake docker executor, fake process world/channel and
owned synthetic repositories.  No test launches docker, a
container or the stand-in; no real fixture admission in the real
checkout; no worker stop or host signal.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import json
import os
import re
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
SCRIPTS = REPO_ROOT / "scripts"
X_ORDER_ID = "017-x"
X_ORDER_NAME = "017-x-live-python-executable-capability.md"
# the 017-y sealed entry (the closed readiness diagnosis plus the
# ONE separately bound Python-only capability attempt of order
# 017-y; the historical X entry/namespace/records are unchanged)
Y_ORDER_ID = "017-y"
SUBJECT = 21002
CID = "f" * 64
TOKEN = "1" * 32


def _load_test_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


stl = _load_test_module("oap_x_stl", REPO_ROOT / "tests" / "test_cache_native_fixture_local.py")
stp = _load_test_module(
    "oap_x_stp", REPO_ROOT / "tests" / "test_cache_native_fixture_native_prep.py"
)

#: The ACTUAL Popen, captured before any test patches the shared
#: subprocess module (a per-call capture would chain fakes across
#: driver runs inside one test).
REAL_POPEN = subprocess.Popen

_spec = importlib.util.spec_from_file_location(
    "cache_native_fixture_exec_capability", SCRIPTS / "cache_native_fixture_exec_capability.py"
)
assert _spec is not None and _spec.loader is not None
fxc = importlib.util.module_from_spec(_spec)
sys.modules["cache_native_fixture_exec_capability"] = fxc
_spec.loader.exec_module(fxc)

fci = sys.modules["cache_native_fixture_ci"]
fb = sys.modules["cache_native_fixture_binding"]
fp = sys.modules["cache_native_fixture_native_prep"]
flocal = sys.modules["cache_native_fixture_local"]
model = fci.model

HEAD = stl.HEAD
S_ORDER_NAME = Path(stl.ORDER_PATH).name
FixtureError = fci.FixtureError


# -- the synthetic 017-x repository + fake git ---------------------------------
def _x_repo(base: Path) -> Path:
    """The S-shaped synthetic repository re-activated as 017-x: the
    committed order set gains the unique X order file and
    oap/active selects 017-x (disk and committed)."""
    repo = Path(stl._make_local_repo(base))
    (repo / "oap" / "orders" / X_ORDER_NAME).write_bytes(b"# synthetic X order (fake seam only)\n")
    (repo / "oap" / "active").write_bytes(X_ORDER_ID.encode("ascii") + b"\n")
    return repo


def _x_git_runner(repo: Path, *, head: str = HEAD) -> Any:
    def git_runner(args: list[str], cwd: Path) -> bytes:
        if args == ["rev-parse", "HEAD"]:
            return head.encode("ascii")
        if args == ["status", "--porcelain"]:
            return b""
        if args == ["remote", "get-url", "origin"]:
            return b"https://github.com/ulfe-lmi/slaif-local-coding.git\n"
        if args == ["ls-tree", "--name-only", f"{HEAD}:oap/orders"]:
            return (S_ORDER_NAME + "\n" + X_ORDER_NAME + "\n").encode("ascii")
        if args == ["show", f"{HEAD}:oap/active"]:
            return X_ORDER_ID.encode("ascii") + b"\n"
        if args == ["show", f"{HEAD}:oap/orders/{S_ORDER_NAME}"]:
            return bytes(stl.ORDER_PATH.read_bytes())
        if args == ["show", f"{HEAD}:oap/orders/{X_ORDER_NAME}"]:
            return b"# synthetic X order (fake seam only)\n"
        raise AssertionError(f"unexpected git args: {args}")

    return git_runner


def _x_hermetic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fake: Any, control: Path) -> None:
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
    monkeypatch.setattr(fci, "_count_fixture_uid_processes", lambda uid: 0)
    for var in flocal._LOCAL_ENDPOINT_SELECTION_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    sock = socket.socket(socket.AF_UNIX)
    sock_path = tmp_path / "docker.sock"
    sock.bind(str(sock_path))
    sock.close()
    monkeypatch.setattr(flocal, "_LOCAL_DOCKER_SOCKET", str(sock_path))
    fake._state_path = str(control / flocal._CONTROL_STATE_NAME)


# -- the fake process world + channel -------------------------------------------
def _hold_argv(token: str) -> bytes:
    return (
        b"\0".join(
            x.encode("ascii")
            for x in (
                "python3",
                "/opt/slaif-fixture/cache_native_fixture_standin.py",
                "--mode",
                "hold",
                "--hold-token",
                token,
            )
        )
        + b"\0"
    )


def _controller_proc(cid: str) -> dict[str, Any]:
    proc: dict[str, Any] = stp.subject_proc(
        1,
        argv=b"python3\0/opt/slaif-fixture/cache_native_fixture_controller.py\0",
        uid=21001,
        gid=21001,
        groups=(),
        tty=0,
        tpgid=0,
        start=100,
        cgroup=cid,
    )
    return proc


def _subject_proc(
    pid: int,
    token: str,
    cid: str,
    *,
    uid: int = SUBJECT,
    gid: int = SUBJECT,
    groups: tuple[int, ...] = (SUBJECT,),
    start: int = 500,
) -> dict[str, Any]:
    proc: dict[str, Any] = stp.subject_proc(
        pid,
        argv=_hold_argv(token),
        uid=uid,
        gid=gid,
        groups=groups,
        tty=0,
        tpgid=0,
        start=start,
        cgroup=cid,
    )
    return proc


class _World:
    """The fake exact-CID process world: the controller (pid 1)
    is always a member; the hold subject (pid 60) appears when the
    fake exec -d is issued and is removed by the owner teardown."""

    def __init__(
        self,
        cid: str | None = None,
        *,
        subject_uid: int = SUBJECT,
        subject_gid: int = SUBJECT,
        subject_groups: tuple[int, ...] = (SUBJECT,),
    ) -> None:
        self.cid = cid
        self.controller = _controller_proc(cid) if cid is not None else None
        self.subject: dict[str, Any] | None = None
        self.extra: dict[int, dict[str, Any]] = {}
        self.subject_uid = subject_uid
        self.subject_gid = subject_gid
        self.subject_groups = subject_groups

    def attach(self, cid: str) -> None:
        """Synchronize the world with the ACTUAL docker-created
        CID (the fake executor derives the CID from the create
        name; the world must carry that exact scope on every
        member, never a caller-picked stand-in)."""
        self.cid = cid
        self.controller = _controller_proc(cid)

    def pids(self) -> list[int]:
        out = [1]
        if self.subject is not None:
            out.append(60)
        out.extend(sorted(self.extra))
        return out

    def proc(self, pid: int) -> dict[str, Any] | None:
        if pid == 1 and self.controller is not None:
            return self.controller
        if pid == 60 and self.subject is not None:
            return self.subject
        if pid in self.extra:
            return self.extra[pid]
        return None

    def launch_subject(self, token: str) -> None:
        if self.cid is None:
            raise AssertionError("world not attached to the created CID")
        self.subject = _subject_proc(
            60,
            token,
            self.cid,
            uid=self.subject_uid,
            gid=self.subject_gid,
            groups=self.subject_groups,
        )

    def add_subject(self, pid: int, token: str) -> None:
        """A second fresh closed-form member (the ambiguous
        correlation control): same CID scope, its own birth."""
        if self.cid is None:
            raise AssertionError("world not attached to the created CID")
        self.extra[pid] = _subject_proc(pid, token, self.cid, start=501 + pid)


class _FakeChannel:
    """The scripted registered-CID channel over the fake world —
    FAITHFUL to the real channel's read law: EVERY read is
    scope-gated (a process not observed in the BOUND CID's cgroup
    scope does not exist on this channel; a foreign-CID or
    cgroup-less pid is never in scope), the tri-state verified
    absence (gone = True, in-scope present = False, existing but
    out-of-scope = None — an unprovable entry is an unknown, never
    a verified absence), and the birth-bound exe digest."""

    def __init__(self, cid: str, world: _World, *, exe_digest: str | None = "a" * 64) -> None:
        self._cid = cid
        self._world = world
        self._exe_digest = exe_digest
        # every scoped exe access records whether the subject was
        # ALIVE at that instant (the measured-while-alive proof)
        self.exe_accesses: list[bool] = []

    @property
    def cid(self) -> str:
        return self._cid

    def _in_scope(self, pid: int) -> bool:
        p = self._world.proc(pid)
        return p is not None and p.get("cgroup") == self._cid

    def cgroup_scope(self, pid: int) -> str | None:
        return f"docker-{self._cid}.scope" if self._in_scope(pid) else None

    def stat(self, pid: int) -> bytes | None:
        p = self._world.proc(pid)
        if p is None:
            return None
        return p["stat"].encode("ascii") if self._in_scope(pid) else None

    def cmdline(self, pid: int) -> bytes | None:
        p = self._world.proc(pid)
        if p is None:
            return None
        return p["cmdline"] if self._in_scope(pid) else None

    def status(self, pid: int) -> bytes | None:
        p = self._world.proc(pid)
        if p is None:
            return None
        return p["status"] if self._in_scope(pid) else None

    def list_pids(self) -> list[int]:
        raise FixtureError("prep-channel-no-enumeration")

    def pid_present(self, pid: int) -> bool | None:
        p = self._world.proc(pid)
        if p is None:
            return True  # the entry is gone: verified absence
        if p.get("cgroup") != self._cid:
            # the entry exists but the registered scope is
            # unreadable or no longer ours: unknown, never a
            # verified absence
            return None
        return False

    def exe_sha256(self, pid: int, birth: int) -> str | None:
        p = self._world.proc(pid)
        if p is None or not self._in_scope(pid):
            return None
        st = fp.parse_proc_stat(p["stat"])
        if st.start_time != birth:
            raise FixtureError("prep-subject-invalid")
        self.exe_accesses.append(self._world.subject is not None)
        return self._exe_digest


# -- the fake docker over the world (top + hold exec) ----------------------------
class XFakeDocker(stl.LocalFakeDocker):  # type: ignore[name-defined,misc]
    def __init__(self, world: _World, *, subject_hold_seconds: float | None = None) -> None:
        super().__init__()
        self._world = world
        # the stand-in's OWN finite hold: when set, the dispatched
        # subject expires on its own after this many seconds (the
        # removal is the subject's natural finite lifetime — no
        # signal from the owner or the driver)
        self.subject_hold_seconds = subject_hold_seconds
        self.top_override: bytes | None = None
        self.top_rc: int = 0
        self.hold_rc: int = 0
        self.rm_rc: int = 0
        self.hold_calls: list[str] = []
        self.proc_root: Path | None = None
        self._subject_timer: threading.Timer | None = None

    def __call__(self, argv: list[str], timeout: float) -> Any:
        if len(argv) >= 3 and argv[:2] == ["docker", "create"]:
            result = super().__call__(argv, timeout)
            # the fake create DERIVES the CID from the create
            # name; the world carries that ACTUAL created CID
            # (parsed from the response — never a caller stand-in)
            if result.returncode == 0:
                self._world.attach(result.output.decode("ascii").strip())
            return result
        if len(argv) >= 3 and argv[:3] == ["docker", "exec", "-d"]:
            self.hold_calls.append(argv[-1])
            if self.hold_rc == 0:
                self._world.launch_subject(argv[-1])
                if self.proc_root is not None:
                    (self.proc_root / "60").mkdir(exist_ok=True)
                if self.subject_hold_seconds is not None:

                    def _expire() -> None:
                        self._world.subject = None
                        if self.proc_root is not None:
                            with contextlib.suppress(OSError):
                                (self.proc_root / "60").rmdir()

                    self._subject_timer = threading.Timer(self.subject_hold_seconds, _expire)
                    self._subject_timer.start()
            return self._result(self.hold_rc, b"")
        if len(argv) == 3 and argv[:2] == ["docker", "top"]:
            if self.top_override is not None:
                return self._result(self.top_rc, self.top_override)
            rows = "".join(f"slaifctl     {p}      python3\n" for p in self._world.pids())
            return self._result(0, b"UID          PID    COMMAND\n" + rows.encode("ascii"))
        if len(argv) >= 3 and argv[:2] == ["docker", "rm"] and self.rm_rc:
            # the exact owned container removal FAILS: the world
            # keeps the container (a failed rm leaves it)
            return self._result(self.rm_rc, b"")
        result = super().__call__(argv, timeout)
        if argv[:2] == ["docker", "rm"] and result.returncode == 0:
            self._world.subject = None
        return result


# -- the owner-level fixture ------------------------------------------------------
def _x_setup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, world: _World | None = None
) -> dict[str, Any]:
    repo = _x_repo(tmp_path / "repo")
    work = tmp_path / "work"
    control = tmp_path / "control"
    evidence = tmp_path / "evidence" / "native-owner-evidence.json"
    fake = XFakeDocker(world if world is not None else _World())
    _x_hermetic(tmp_path, monkeypatch, fake, control)
    return {
        "repo": repo,
        "work": work,
        "control": control,
        "evidence": evidence,
        "docker": fake,
        "git_runner": _x_git_runner(repo),
    }


def _x_owner(paths: dict[str, Any], binding: Any) -> tuple[Any, threading.Thread, str]:
    owner = flocal.LocalFixtureOwner(
        paths["repo"],
        paths["work"],
        paths["evidence"],
        HEAD,
        paths["control"],
        git_runner=paths["git_runner"],
        executor=paths["docker"],
        binding=binding,
    )
    thread = threading.Thread(target=owner.serve, daemon=True)
    thread.start()
    end = time.monotonic() + 30.0
    while time.monotonic() < end:
        state = flocal._state_record(paths["control"])
        if state is not None:
            return owner, thread, str(state["run_id"])
    pytest.fail("owner never published its initial state")


def _client(control: Path, command: str, run_id: str, timeout: float = 30.0) -> dict[str, Any]:
    response: dict[str, Any] = stl._client(control, command, run_id, timeout)
    return response


def _join_owner(
    thread: threading.Thread,
    *,
    control: Path | None = None,
    run_id: str | None = None,
    timeout: float = 60.0,
) -> None:
    """Bounded EXACT-OWNER convergence in every case (pass or
    fail): a still-held owner receives its own bounded abort over
    the protected interface (never a host signal) and is joined;
    a still-alive owner after the bounded abort fails the test
    loudly instead of leaking it."""
    if thread.is_alive() and control is not None and run_id is not None:
        with contextlib.suppress(Exception):
            _client(control, "abort", run_id, timeout=15.0)
    thread.join(timeout)
    if thread.is_alive():
        pytest.fail("owner thread did not converge after bounded abort")


def _admit_x(paths: dict[str, Any]) -> Any:
    binding = fb.resolve_order_binding(
        paths["repo"], X_ORDER_ID, HEAD, git_runner=paths["git_runner"]
    )
    fb.admit_order_attempt(paths["repo"], X_ORDER_ID, binding, git_runner=paths["git_runner"])
    return binding


# -- owner-level: the closed hold/top control commands ---------------------------
def test_hold_and_top_public_interface(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The full owner public positive over the fake platform:
    prepare -> top (one member) -> hold (the ONE closed detached
    start) -> top (the fresh subject is a member) -> the one-
    start latch refuses a second start -> abort convergence."""
    paths = _x_setup(tmp_path, monkeypatch)
    binding = _admit_x(paths)
    owner, thread, run_id = _x_owner(paths, binding)
    try:
        prepared = _client(paths["control"], "prepare", run_id)
        assert prepared["ok"] is True
        top1 = _client(paths["control"], "top", run_id)
        assert top1["ok"] is True
        assert top1["detail"] == {"pids": [1], "rows": 1}
        held = _client(paths["control"], "hold", run_id)
        assert held["ok"] is True
        assert isinstance(held["detail"]["hold_token"], str)
        assert re.fullmatch(r"[0-9a-f]{32}", held["detail"]["hold_token"])
        token = held["detail"]["hold_token"]
        assert token == owner.run_token
        top2 = _client(paths["control"], "top", run_id)
        assert top2["detail"] == {"pids": [1, 60], "rows": 2}
        # the ONE start is consumed: a second start is refused, no
        # retry, no convergence (the held target is still finishable)
        second = _client(paths["control"], "hold", run_id)
        assert second["ok"] is False
        assert second["reason"] == "local-hold-already-started"
        assert len(paths["docker"].hold_calls) == 1
        aborted = _client(paths["control"], "abort", run_id)
        assert aborted["ok"] is True
        assert aborted["detail"]["outcome"] == "aborted"
    finally:
        _join_owner(thread, control=paths["control"], run_id=run_id)
    assert owner.terminal_outcome == "aborted"
    journal = fb.read_admission_record(paths["repo"], X_ORDER_ID)["attempts"]
    assert journal == [{"head": HEAD, "run_id": run_id, "status": "aborted"}]


def test_hold_start_failure_consumes_one_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A FAILED detached start consumes the one start: the run
    refuses any retry and stays finishable (prep-only honest
    unready)."""
    paths = _x_setup(tmp_path, monkeypatch)
    paths["docker"].hold_rc = 1
    binding = _admit_x(paths)
    owner, thread, run_id = _x_owner(paths, binding)
    try:
        assert _client(paths["control"], "prepare", run_id)["ok"] is True
        first = _client(paths["control"], "hold", run_id)
        assert first["ok"] is False
        assert first["reason"] == "local-hold-start-failed"
        second = _client(paths["control"], "hold", run_id)
        assert second["ok"] is False
        assert second["reason"] == "local-hold-already-started"
        finished = _client(paths["control"], "finish", run_id)
        assert finished["ok"] is True
        assert finished["detail"]["outcome"] == "pass"
    finally:
        _join_owner(thread, control=paths["control"], run_id=run_id)
    assert owner.terminal_outcome == "pass"


def test_top_closed_grammar_controls(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The top parser under the closed forms: the daemon's default
    ``-ef`` header with command arguments containing spaces is
    admitted (PID located by header), the existing fixture form
    stays admitted, and unknown/duplicate-column/duplicate/zero/
    non-numeric/overbound inventories are closed refusals."""
    paths = _x_setup(tmp_path, monkeypatch)
    binding = _admit_x(paths)
    owner, thread, run_id = _x_owner(paths, binding)
    docker = paths["docker"]
    try:
        assert _client(paths["control"], "prepare", run_id)["ok"] is True
        docker.top_override = (
            b"UID          PID    PPID  C STIME TTY          TIME CMD\n"
            b"slaifctl     1       0   0 01:00 ?        00:00:00 "
            b"python3 /opt/slaif-fixture/cache_native_fixture_controller.py serve\n"
        )
        assert _client(paths["control"], "top", run_id)["detail"] == {"pids": [1], "rows": 1}
        # the closed 3-column form with a spaced command argument
        docker.top_override = (
            b"UID          PID    COMMAND\n"
            b"slaifctl     1      python3 "
            b"/opt/slaif-fixture/cache_native_fixture_controller.py serve\n"
        )
        assert _client(paths["control"], "top", run_id)["detail"] == {"pids": [1], "rows": 1}
        bad = {
            "unknown_header": b"PID    USER    COMMAND\n1      slaifctl  python3\n",
            "duplicate_pid_column": b"UID   PID   PID   COMMAND\nslaifctl 1 1 python3\n",
            "duplicate_pid_rows": (
                b"UID          PID    COMMAND\n"
                b"slaifctl     1      python3\nslaifctl     1      python3\n"
            ),
            "zero_pid": b"UID          PID    COMMAND\nslaifctl     0      python3\n",
            "non_numeric_pid": b"UID          PID    COMMAND\nslaifctl     x      python3\n",
        }
        for name, payload in bad.items():
            docker.top_override = payload
            response = _client(paths["control"], "top", run_id)
            assert response["ok"] is False, name
            assert response["reason"] in (
                "top-query-failed",
                "top-count-untrusted",
            ), (name, response["reason"])
        rows = "".join(f"slaifctl     {n}      python3\n" for n in range(1, 98)).encode("ascii")
        docker.top_override = b"UID          PID    COMMAND\n" + rows
        response = _client(paths["control"], "top", run_id)
        assert response["ok"] is False
        assert response["reason"] == "top-count-untrusted"
        # exactly the 96-row bound is admitted
        rows = "".join(f"slaifctl     {n}      python3\n" for n in range(1, 97)).encode("ascii")
        docker.top_override = b"UID          PID    COMMAND\n" + rows
        detail = _client(paths["control"], "top", run_id)["detail"]
        assert detail["rows"] == 96 and len(detail["pids"]) == 96
    finally:
        _join_owner(thread, control=paths["control"], run_id=run_id)


def test_numeric_hold_token_never_coerced() -> None:
    """The closed marker grammar is an ACTUAL string: a numeric
    (or any non-string) hold_token is refused, never coerced by
    str(); the exact string form is admitted."""

    def response(token: Any) -> dict[str, Any]:
        return {
            "record": flocal.CONTROL_RECORD,
            "ok": True,
            "command": "hold",
            "run_id": "a" * 32,
            "reason": None,
            "detail": {"hold_token": token},
        }

    flocal._validate_control_response(response(TOKEN), "hold")
    with pytest.raises(FixtureError):
        flocal._validate_control_response(response(int(TOKEN)), "hold")
    with pytest.raises(FixtureError):
        flocal._validate_control_response(response(b"1" * 32), "hold")


def _sealed_git_fixture(base: Path, order: str, order_bytes: bytes) -> tuple[Path, str]:
    """A REAL synthetic git repository committing the SEALED
    ENTRY's order: actual git history so the public CLI's real
    read-only git path (never a fake runner) verifies the bound
    literal head, the committed active and the unique committed
    order bytes.  The S-shaped checkout content (the fixture
    sources, the Dockerfile and the CI workflow) is copied and
    committed too, exactly as the S synthetic repository carries
    it; the stable admission namespace is excluded from git
    status.  Exactly ONE order file of the entry's pattern is
    committed, so the real resolver's uniqueness check holds."""
    root = base / "repo"
    root.mkdir(parents=True)

    def git(*args: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL)

    git("init", "-q")
    git("remote", "add", "origin", "https://github.com/ulfe-lmi/slaif-local-coding.git")
    # git init already created .git/info; the stable admission
    # namespace is excluded from git status
    (root / ".git" / "info" / "exclude").write_bytes(b"/.oap-local/\n")
    (root / "scripts").mkdir(parents=True)
    for name in (
        "cache_native_fixture_ci.py",
        "cache_native_fixture_model.py",
        "cache_native_fixture_controller.py",
        "cache_native_fixture_standin.py",
        "cache_native_fixture_export_client.py",
        "cache_native_fixture_local.py",
        "cache_native_fixture.Dockerfile",
    ):
        (root / "scripts" / name).write_bytes((REPO_ROOT / "scripts" / name).read_bytes())
    (root / "Dockerfile").write_bytes((REPO_ROOT / "Dockerfile").read_bytes())
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "ci.yml").write_bytes(
        (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_bytes()
    )
    # the S-shaped committed context: the historical S order plus
    # the unique sealed-entry order, with oap/active selecting
    # that entry's order id
    order_name = Path(fxc._SEALED_ENTRIES[order].order_path).name
    (root / "oap" / "orders").mkdir(parents=True)
    (root / "oap" / "orders" / S_ORDER_NAME).write_bytes(stl.ORDER_PATH.read_bytes())
    (root / "oap" / "orders" / order_name).write_bytes(order_bytes)
    (root / "oap" / "active").write_bytes(order.encode("ascii") + b"\n")
    git(
        "add",
        "oap/active",
        f"oap/orders/{S_ORDER_NAME}",
        f"oap/orders/{order_name}",
    )
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


def _x_git_fixture(base: Path) -> tuple[Path, str]:
    """The historical 017-x sealed-entry repository fixture (the
    exact original synthetic order content, byte-for-byte)."""
    return _sealed_git_fixture(base, X_ORDER_ID, b"# synthetic X order (fake seam only)\n")


def _y_git_fixture(base: Path) -> tuple[Path, str]:
    """The 017-y sealed-entry repository fixture (the unique
    committed 017-y order, oap/active selecting 017-y; the
    historical X order is NOT committed, so no X namespace
    exists in this synthetic repository at all)."""
    return _sealed_git_fixture(base, Y_ORDER_ID, b"# synthetic 017-y order (fake seam only)\n")


def test_public_cli_child_owned_resolve_admit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The SEALED CHILD owns resolve+admit ONCE over the REAL
    public CLI path (real read-only git against a real synthetic
    repository): one entry admits exactly one identity and
    serves it; a second entry (fresh output roots) is refused
    with the admission left byte-identical (the one-attempt law
    is never bypassed by journal reconstruction)."""
    repo, head = _x_git_fixture(tmp_path)
    served: list[str] = []

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("external fixture action forbidden")

    monkeypatch.setattr(flocal, "_local_bound_executor", lambda: forbidden)

    def _fake_serve(owner: Any) -> int:
        served.append(owner.run_id)
        return 0

    monkeypatch.setattr(flocal.LocalFixtureOwner, "serve", _fake_serve)
    for var in flocal._LOCAL_ENDPOINT_SELECTION_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    args = [
        "owner",
        "--order",
        X_ORDER_ID,
        "--bind-head",
        head,
        "--repo",
        str(repo),
        "--work",
        str(tmp_path / "work"),
        "--control-dir",
        str(tmp_path / "control"),
        "--evidence-out",
        str(tmp_path / "evidence.json"),
    ]
    first = _cli_main(monkeypatch, args)
    assert first == 0
    assert len(served) == 1
    journal_path = fb.admission_path(repo, X_ORDER_ID)
    journal_before = journal_path.read_bytes()
    attempts = fb.read_admission_record(repo, X_ORDER_ID)["attempts"]
    assert attempts == [{"head": head, "run_id": served[0], "status": "running"}]
    second_args = list(args)
    for name, value in (
        ("--work", "other-work"),
        ("--control-dir", "other-control"),
        ("--evidence-out", "other-evidence.json"),
    ):
        second_args[second_args.index(name) + 1] = str(tmp_path / value)
    second = _cli_main(monkeypatch, second_args)
    assert second == 1
    assert len(served) == 1
    assert journal_before == journal_path.read_bytes()


def _cli_main(monkeypatch: pytest.MonkeyPatch, args: list[str]) -> int:
    import io

    text = io.StringIO()
    with contextlib.redirect_stdout(text):
        rc = flocal.main(args)
    return int(rc)


# -- the protected capability-record retention (closed, atomic) ------------------
def _startup_record() -> dict[str, Any]:
    record: dict[str, Any] = fxc._driver_record("fail", "local-driver-startup", bind_head="b" * 40)
    return record


def test_retain_record_closed_and_atomic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The reviewed protected retention: legitimate fresh 0600
    publication; pre-existing destination preserved byte/inode;
    group/other-writable ancestor refused; symlink ancestor
    refused; an interrupted write NEVER exposes the final
    destination (temp-only cleanup)."""
    record = _startup_record()
    good = tmp_path / "good"
    good.mkdir(mode=0o700)
    path = good / "record.json"
    fxc._retain_record(record, path)
    assert json.loads(path.read_bytes()) == record
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    original = path.read_bytes()
    inode = path.stat().st_ino
    with pytest.raises(FixtureError):
        fxc._retain_record(record, path)
    assert path.read_bytes() == original
    assert path.stat().st_ino == inode

    writable = tmp_path / "writable"
    writable.mkdir(mode=0o700)
    writable.chmod(0o770)
    target = writable / "record.json"
    with pytest.raises(FixtureError):
        fxc._retain_record(record, target)
    assert not target.exists()

    real = tmp_path / "real"
    real.mkdir(mode=0o700)
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    target = link / "record.json"
    with pytest.raises(FixtureError):
        fxc._retain_record(record, target)
    assert not (real / "record.json").exists()

    failure_dir = tmp_path / "failure"
    failure_dir.mkdir(mode=0o700)
    target = failure_dir / "record.json"
    observed_final_before_complete: list[bool] = []
    real_fdopen = os.fdopen

    class PartialWrite:
        def __init__(self, fd: int, *args: Any, **kwargs: Any) -> None:
            self.inner = real_fdopen(fd, *args, **kwargs)

        def __enter__(self) -> PartialWrite:
            return self

        def __exit__(self, *args: Any) -> None:
            self.inner.close()

        def write(self, data: bytes) -> None:
            self.inner.write(data[:7])
            self.inner.flush()
            observed_final_before_complete.append(target.exists())
            raise OSError("synthetic interrupted write")

    monkeypatch.setattr(fxc.os, "fdopen", PartialWrite)
    with pytest.raises(OSError):
        fxc._retain_record(record, target)
    assert observed_final_before_complete == [False]
    assert not target.exists()


def test_retain_record_refuses_open_schemas() -> None:
    """The closed record validator refuses the open/contradictory
    shapes (state coherence: digest grammar agrees with the
    measured executable state; the subject identity law; the
    inventory bounds; a measured identity implies a subject)."""
    base = fxc._driver_record(
        "pass",
        None,
        bind_head="a" * 40,
        run_id="b" * 32,
        owner_exit=0,
        evidence_sha256="c" * 64,
        capability={
            "cid": "d" * 64,
            "subject": {
                "pid": 60,
                "birth": 500,
                "uid": SUBJECT,
                "gid": SUBJECT,
                "groups": [SUBJECT],
            },
            "process_identity": "measured",
            "executable": "measured",
            "executable_sha256": "e" * 64,
            "pre_inventory_rows": 1,
            "post_inventory_rows": 2,
            "inventory_rows_max": fxc.INVENTORY_ROWS_MAX,
            "subject_exit": "verified-gone",
        },
    )
    fxc._validate_capability_record(base)
    unknown = json.loads(json.dumps(base))
    unknown["capability"].update({"executable": "unknown", "executable_sha256": None})
    fxc._validate_capability_record(unknown)

    def bad(name: str, change: Any) -> None:
        value = json.loads(json.dumps(base))
        change(value["capability"])
        with pytest.raises(FixtureError) as exc:
            fxc._validate_capability_record(value)
        assert "cap-record" in str(exc.value), name

    bad(
        "measured_exe_requires_measured_process",
        lambda c: c.update({"process_identity": "refused"}),
    )
    bad(
        "measured_exe_requires_subject",
        lambda c: c.update({"process_identity": "not-measured", "subject": None}),
    )
    bad("subject_requires_cid", lambda c: c.update({"cid": None}))
    bad("subject_pid_positive", lambda c: c["subject"].update({"pid": 0}))
    bad("subject_birth_non_negative", lambda c: c["subject"].update({"birth": -1}))
    bad("subject_uid_fixed", lambda c: c["subject"].update({"uid": 21001}))
    bad("subject_gid_fixed", lambda c: c["subject"].update({"gid": 21001}))
    bad("subject_group_law", lambda c: c["subject"].update({"groups": [0, SUBJECT]}))
    bad("pre_within_bound", lambda c: c.update({"pre_inventory_rows": 97}))
    bad("post_within_bound", lambda c: c.update({"post_inventory_rows": 97}))
    bad("subject_requires_post_rows", lambda c: c.update({"post_inventory_rows": 0}))


# -- the verified-gone exit vocabulary -------------------------------------------
def test_wait_natural_exit_verified_gone_label(tmp_path: Path) -> None:
    """The honest exit vocabulary: a verified absence is
    ``verified-gone`` (never a claimed natural termination), a
    presence is ``still-present``, an unreadable entry is
    ``unknown``; the bound is honored (no fresh phase deadline)."""

    class _Channel:
        def __init__(self, present: bool | None) -> None:
            self._present = present

        def pid_present(self, pid: int) -> bool | None:
            return self._present

    assert fxc.wait_natural_exit(_Channel(True), 60, bound=1.0) == "verified-gone"
    assert fxc.wait_natural_exit(_Channel(False), 60, bound=0.2) == "still-present"
    assert fxc.wait_natural_exit(_Channel(None), 60, bound=0.2) == "unknown"
    with pytest.raises(FixtureError):
        fxc.wait_natural_exit(_Channel(True), 60, bound=-1.0)
    with pytest.raises(FixtureError):
        fxc.wait_natural_exit(_Channel(True), 60, bound=float("inf"))


# -- driver level: the public fake lifecycle ---------------------------------------
#
# Two compositions, each with an honest scope:
#
# (a) the scripted driver unit: the REAL run_exec_capability over a
#     fake platform — a real exact-owned sealed child (the model of
#     the owner process: alive until the owner side converges,
#     never signalled), a fake owner side that bootstraps the FRESH
#     protected control root and publishes the closed state with
#     the child's own pid, a scripted owner-side control response,
#     the faithful exact-CID channel over the fake world, and a
#     per-attested-pid proc root (the host is never enumerated).
#     The driver's startup authority is exercised: the fresh
#     control root, the published pid == the ACTUAL child's pid,
#     the child's liveness, and the journal's ONE admission.  A
#     prior/foreign owner's state is never adopted.
#
# (b) the coupled public-owner terminal composition (the root
#     terminal probe's pattern, tracked): the REAL owner over the
#     fake platform (real constructor/control/finish/export/
#     teardown, in-process) is driven prepare -> hold; the scoped
#     live measurement of the subject's executable happens WHILE
#     the subject is alive and BEFORE the owner's own finish; the
#     REAL _terminal then converges the SAME run (the real bound
#     evidence bytes, the ONE shared admission's terminal
#     finalization, the protected retention first) with the
#     owner's thread lifecycle coupled as the process/reader
#     facts.

CODE_EXIT0 = "import sys; sys.exit(0)\n"
CODE_SLEEP_UNTIL_FLAG = (
    "import os, pathlib, time\n"
    "p = pathlib.Path(os.environ.get('X_ABORT_FLAG', '/nonexistent'))\n"
    "for _ in range(400):\n"
    "    if p.exists():\n"
    "        break\n"
    "    time.sleep(0.05)\n"
)
CODE_CAP = (
    "import sys, time\n"
    "o = sys.stdout.buffer\n"
    "c = b'x' * 65536\n"
    "try:\n"
    "    for _ in range(18):\n"
    "        o.write(c)\n"
    "        o.flush()\n"
    "        time.sleep(0.03)\n"
    "except OSError:\n"
    "    pass\n"
)


CODE_STARTUP_REFUSE = (
    "import json, sys\n"
    "line = json.dumps("
    f"{{'record': {flocal.CONTROL_RECORD!r}, 'stage': 'startup', "
    "'reason': 'local-rehearsal-exists'}, sort_keys=True)\n"
    "sys.stdout.write(line + '\\n')\n"
    "sys.stdout.flush()\n"
    "sys.exit(1)\n"
)


class _ErrStream:
    """A pipe whose read fails: the closed read-error fact."""

    def __init__(self, real: Any) -> None:
        self._real = real
        self._raised = False

    def read(self, _n: int) -> bytes:
        if not self._raised:
            self._raised = True
            raise OSError("synthetic pipe read error")
        return b""

    def close(self) -> None:
        try:
            self._real.close()
        except OSError:
            pass


def _journal(repo: Path) -> list[dict[str, Any]]:
    return _journal_for(repo, X_ORDER_ID)


def _journal_for(repo: Path, order: str) -> list[dict[str, Any]]:
    record = fb.read_admission_record(repo, order)
    attempts: list[dict[str, Any]] = record["attempts"]
    return attempts


def _stage1_owner_pass_entry(
    base: Path, monkeypatch: pytest.MonkeyPatch, order: str
) -> dict[str, Any]:
    """Stage 1 (scripted unit): the REAL owner over the fake
    platform converges to a pass and retains its bound native
    evidence in the SEALED ENTRY's namespace; the bound attempt
    is left RUNNING for the driver's terminal finalization (the
    distinct native law).  Bounded exact-owned convergence on
    every path (pass or fail)."""
    repo, head = (_x_git_fixture if order == X_ORDER_ID else _y_git_fixture)(base)
    binding = fb.resolve_order_binding(repo, order, head)
    fb.admit_order_attempt(repo, order, binding)
    run_id = binding.run_id
    world = _World()
    docker = XFakeDocker(world)
    work = base / "work"
    control = base / "control"
    evidence = base / "evidence" / "native-owner-evidence.json"
    hermetic = base / "hermetic"
    hermetic.mkdir(exist_ok=True)
    _x_hermetic(hermetic, monkeypatch, docker, control)
    owner = flocal.LocalFixtureOwner(
        repo, work, evidence, head, control, executor=docker, binding=binding
    )
    thread = threading.Thread(target=owner.serve, daemon=True)
    thread.start()
    try:
        end = time.monotonic() + 30.0
        while time.monotonic() < end:
            if flocal._state_record(control) is not None:
                break
        prepared = _client(control, "prepare", run_id)
        assert prepared["ok"] is True, prepared
        cid = str(prepared["detail"]["cid"])
        assert cid == world.cid  # the world carries the ACTUAL created CID
        held = _client(control, "hold", run_id)
        assert held["ok"] is True, held
        # the EXACT observed closed state bytes of this real prior
        # owner (captured WHILE it still serves — the terminal
        # teardown destroys the control surface and the owner's
        # retained evidence is the durable fact)
        state_bytes = (control / flocal._CONTROL_STATE_NAME).read_bytes()
        finished = _client(control, "finish", run_id)
        assert finished["ok"] is True, finished
        assert finished["detail"]["outcome"] == "pass"
    finally:
        _join_owner(thread, control=control, run_id=run_id)
    assert owner.terminal_outcome == "pass"
    assert _journal_for(repo, order) == [{"head": head, "run_id": run_id, "status": "running"}]
    return {
        "repo": repo,
        "head": head,
        "run_id": run_id,
        "cid": cid,
        "evidence_bytes": evidence.read_bytes(),
        "state_bytes": state_bytes,
        "world": world,
    }


def _stage1_owner_pass(base: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """The historical 017-x stage 1 (the original X entry)."""
    return _stage1_owner_pass_entry(base, monkeypatch, X_ORDER_ID)


def _driver_run(
    base: Path,
    monkeypatch: pytest.MonkeyPatch,
    stage: dict[str, Any],
    *,
    client: Any,
    converge_flag: Path,
    child_code: str = CODE_SLEEP_UNTIL_FLAG,
    end_anchor: float | None = None,
    err_stream: bool = False,
    bootstrap_state: dict[str, Any] | None = None,
    child_bootstraps: bool = True,
    entry_order: str = X_ORDER_ID,
) -> dict[str, Any]:
    """Stage 2 (scripted unit): the REAL driver over the fake
    platform.  The fake sealed child is a real exact-owned process
    that stays alive until the OWNER SIDE signals convergence
    (the converge flag — the model of the owner process
    converging on its terminal command), so the driver's startup
    verification and owner wait observe a live owner exactly as
    the real composition does.  The fake owner side bootstraps
    the FRESH protected control root and publishes the closed
    state with the child's own pid (the real owner does this in
    the child itself).  The exact-owned test child is reaped by
    this helper on every path (never name-matched, never
    signalled).  ``entry_order`` selects the SEALED entry the
    driver runs under (the historical 017-x entry by default)."""
    base.mkdir(parents=True, exist_ok=True)
    os.chmod(base, 0o700)  # the protected record-parent root
    control = base / "control"
    assert not control.exists()  # the fresh bootstrap: no prior root
    proc_root = base / "proc"
    proc_root.mkdir(exist_ok=True)
    (proc_root / "1").mkdir(exist_ok=True)
    record_out = base / "record.json"
    evidence_dest = base / "evidence.json"
    anchor = end_anchor if end_anchor is not None else time.monotonic() + 700.0
    procs: list[Any] = []
    channels: list[_FakeChannel] = []
    factory_calls: list[tuple[str, float]] = []

    def fake_popen(argv: list[str], **kwargs: Any) -> Any:
        assert "owner" in argv and entry_order in argv
        assert kwargs.get("start_new_session") is True
        env = dict(os.environ)
        env["X_ABORT_FLAG"] = str(converge_flag)
        proc = REAL_POPEN(
            [sys.executable, "-c", child_code],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            env=env,
        )
        procs.append(proc)
        if err_stream:
            proc.stdout = _ErrStream(proc.stdout)  # type: ignore[assignment]
        if not child_bootstraps:
            # the sealed child refused BEFORE the control surface
            # (no root, no state — the startup line is its only
            # output)
            return proc
        # the fake OWNER side bootstraps the fresh protected
        # control root and publishes the closed state (the child's
        # own pid — the real owner does this in the child itself)
        state = (
            bootstrap_state
            if bootstrap_state is not None
            else {
                "record": flocal.STATE_SCHEMA,
                "run_id": stage["run_id"],
                "pid": proc.pid,
                "end_anchor": anchor,
                "phase": "start",
                "status": "running",
            }
        )
        control.mkdir(mode=0o700)
        state_path = control / flocal._CONTROL_STATE_NAME
        state_path.write_bytes(json.dumps(state, sort_keys=True).encode("ascii"))
        os.chmod(state_path, 0o600)
        return proc

    def factory(cid: str, remaining: float) -> Any:
        channel = _FakeChannel(cid, stage["world"], exe_digest="a" * 64)
        channels.append(channel)
        factory_calls.append((cid, remaining))
        return channel

    monkeypatch.setattr(fxc.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(flocal, "_control_client", client)
    try:
        started = time.monotonic()
        record = fxc.run_exec_capability(
            stage["repo"],
            stage["head"],
            base / "work",
            control,
            evidence_dest,
            channel_factory=factory,
            proc_root=proc_root,
            record_out=record_out,
            entry=fxc._SEALED_ENTRIES[entry_order],
        )
        elapsed = time.monotonic() - started
    finally:
        # the owner side always converges (the fake child exits on
        # its own finite watch bound once the flag exists — never
        # signalled) and is then reaped
        with contextlib.suppress(OSError):
            converge_flag.touch()
        for proc in procs:
            if proc.poll() is None:
                proc.wait(timeout=5.0)
    return {
        "record": record,
        "channels": channels,
        "factory_calls": factory_calls,
        "elapsed": elapsed,
        "record_out": record_out,
        "control": control,
        "evidence": evidence_dest,
    }


def _happy_client(
    stage: dict[str, Any], proc_root: Path, converge_flag: Path, evidence_dest: Path
) -> Any:
    """The scripted owner side of the full positive: prepare ->
    pre top -> the ONE hold (launches the fresh subject, whose
    finite hold expires on its own) -> post top -> finish (the
    owner side converges and retains the bound native evidence
    bytes).  The subject is removed by its OWN finite lifetime
    (no signal)."""
    world: _World = stage["world"]
    state = {"post_hold": False}

    def _ok(detail: dict[str, Any]) -> dict[str, Any]:
        return {"ok": True, "reason": None, "detail": detail}

    def _kill60() -> None:
        world.subject = None
        with contextlib.suppress(OSError):
            (proc_root / "60").rmdir()

    def client(_control_dir: Any, command: str, run_id: str, _timeout: float) -> dict[str, Any]:
        assert run_id == stage["run_id"]
        if command == "prepare":
            return _ok({"cid": stage["cid"], "state": "prepared", "observed": 0, "end_anchor": 1.0})
        if command == "top":
            pids = [1, 60] if state["post_hold"] else [1]
            return _ok({"pids": pids, "rows": len(pids)})
        if command == "hold":
            if not state["post_hold"]:
                state["post_hold"] = True
                (proc_root / "60").mkdir()
                world.launch_subject(TOKEN)
                threading.Timer(0.5, _kill60).start()
            return _ok({"hold_token": TOKEN})
        if command == "finish":
            evidence_dest.write_bytes(stage["evidence_bytes"])
            os.chmod(evidence_dest, 0o600)
            with contextlib.suppress(OSError):
                converge_flag.touch()
            return _ok({"outcome": "pass"})
        raise AssertionError(f"unexpected command: {command}")

    return client


def test_driver_scripted_full_positive_measures_subject_while_alive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scripted driver unit (a): the real run_exec_capability,
    with the fake sealed child's published state bound to the
    ACTUAL child's pid (startup authority), measures the
    subject's executable WHILE ALIVE (every scoped exe access
    observes the live subject), clamps the executable read
    against the SAME owner END and the issued hold's own finite
    lifetime, then converges through the SAME run identity: the
    protected record retention FIRST and only then the
    same-attempt terminal finalization (ONE shared admission
    end-to-end).  The retained record bytes are IMMUTABLE at
    retention time — the later RAM finalize facts are never
    rewritten into them."""
    stage = _stage1_owner_pass(tmp_path / "positive", monkeypatch)
    base = tmp_path / "positive-run"
    flag = base / "converge-flag"
    out = _driver_run(
        base,
        monkeypatch,
        stage,
        client=_happy_client(stage, base / "proc", flag, base / "evidence.json"),
        converge_flag=flag,
    )
    record = out["record"]
    assert record["status"] == "pass"
    assert record["reason"] is None
    assert record["run_id"] == stage["run_id"]
    assert record["bind_head"] == stage["head"]
    assert record["terminal_command"] == "none"
    assert record["owner_exit"] == 0
    assert record["reader_state"] == "drained"
    assert record["capture_state"] == "drained"
    assert record["evidence_state"] == "verified-pass"
    assert record["retention"] == "retained"
    assert record["finalize"] == "finalized"
    cap = record["capability"]
    assert cap["cid"] == stage["cid"]
    assert cap["process_identity"] == "measured"
    assert cap["executable"] == "measured"
    assert cap["executable_sha256"] == "a" * 64
    assert cap["subject"] == {
        "pid": 60,
        "birth": 500,
        "uid": SUBJECT,
        "gid": SUBJECT,
        "groups": [SUBJECT],
    }
    assert cap["pre_inventory_rows"] == 1
    assert cap["post_inventory_rows"] == 2
    assert cap["subject_exit"] == "verified-gone"
    # the executable was read WHILE the subject was alive on EVERY
    # scoped access (a post-exit capture could never earn this)
    accesses = [flag for ch in out["channels"] for flag in ch.exe_accesses]
    assert accesses and all(accesses)
    # the executable channel is clamped at MEASUREMENT time: the
    # second (measurement) construction is bounded by the issued
    # hold's own finite lifetime and strictly less than the full
    # prepare-time remaining budget
    first_cid, first_budget = out["factory_calls"][0]
    second_cid, second_budget = out["factory_calls"][1]
    assert first_cid == second_cid == stage["cid"]
    assert 0.0 < second_budget <= fxc.STANDIN_HOLD_MAX_SECONDS + 0.25
    assert second_budget < first_budget
    # the ONE shared admission: the driver's terminal
    # finalization is the ONLY terminal journal entry
    assert _journal(stage["repo"]) == [
        {"head": stage["head"], "run_id": stage["run_id"], "status": "pass"}
    ]
    # the retained record is IMMUTABLE at retention time: the
    # later RAM publication facts (retention/finalize) are never
    # rewritten into the retained bytes (the W ordering)
    payload = json.loads(out["record_out"].read_bytes())
    assert payload == {
        **record,
        "retention": "not-requested",
        "finalize": "not-attempted",
    }
    assert stat.S_IMODE(out["record_out"].stat().st_mode) == 0o600
    assert out["elapsed"] < 60.0


def test_driver_startup_refuses_preexisting_control_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Startup authority (layer 1): a PRE-EXISTING control root
    is a prior/foreign owner's terminal/control surface — the
    driver refuses BEFORE any launch: no sealed child, no
    command, no journal mutation, a closed fail record."""
    stage = _stage1_owner_pass(tmp_path / "ctl", monkeypatch)
    base = tmp_path / "ctl-run"
    base.mkdir(parents=True, exist_ok=True)
    control = base / "control"
    control.mkdir(mode=0o700)
    state_path = control / flocal._CONTROL_STATE_NAME
    state_path.write_bytes(stage["state_bytes"])
    os.chmod(state_path, 0o600)
    launched: list[str] = []
    monkeypatch.setattr(fxc.subprocess, "Popen", lambda *a, **k: launched.append("launched"))
    record = fxc.run_exec_capability(
        stage["repo"],
        stage["head"],
        base / "work",
        control,
        base / "evidence.json",
        record_out=base / "record.json",
    )
    assert launched == []
    assert record["status"] == "fail"
    assert record["reason"] == "local-control-exists"
    assert record["run_id"] is None
    # the prior owner's bound attempt is never mutated
    assert _journal(stage["repo"]) == [
        {"head": stage["head"], "run_id": stage["run_id"], "status": "running"}
    ]
    assert not (base / "record.json").exists()


def test_driver_startup_refuses_foreign_prior_owner_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Startup authority (layer 2): the EXACT observed closed
    state bytes of a real prior owner (same bound run id and
    head, still RUNNING in the journal) replayed into a fresh
    control root are never adopted: the published pid is not the
    ACTUAL sealed child's pid, so the driver refuses before any
    command — no prepare/top/hold/finish, no abort, and the old
    journal entry is never mutated (the confirmed foreign-owner
    bootstrap diagnostic)."""
    stage = _stage1_owner_pass(tmp_path / "foreign", monkeypatch)
    base = tmp_path / "foreign-run"
    flag = base / "converge-flag"
    calls: list[str] = []

    def refuse_client(
        _control_dir: Any, command: str, _run_id: str, _timeout: float
    ) -> dict[str, Any]:
        calls.append(command)
        raise AssertionError("foreign prior owner: no command may be issued")

    out = _driver_run(
        base,
        monkeypatch,
        stage,
        client=refuse_client,
        converge_flag=flag,
        # the EXACT observed closed state bytes of the real prior
        # owner (its own pid — not the new child's)
        bootstrap_state=json.loads(stage["state_bytes"].decode("ascii")),
    )
    assert calls == []
    record = out["record"]
    assert record["status"] == "fail"
    assert record["reason"] == "local-owner-foreign-state"
    assert record["run_id"] is None  # never adopted
    assert record["terminal_command"] == "none"
    # the old RUNNING journal entry is never mutated
    assert _journal(stage["repo"]) == [
        {"head": stage["head"], "run_id": stage["run_id"], "status": "running"}
    ]
    assert not out["record_out"].exists()


def _coupled_owner_held(
    base: Path, monkeypatch: pytest.MonkeyPatch, hold_seconds: float = 2.0
) -> dict[str, Any]:
    """Coupled composition (b): the REAL owner over the fake
    platform (real constructor/control, in-process thread)
    converges prepare -> hold and is HELD with the fresh subject
    alive (the stand-in's own finite hold expires on its own)."""
    repo, head = _x_git_fixture(base)
    binding = fb.resolve_order_binding(repo, X_ORDER_ID, head)
    fb.admit_order_attempt(repo, X_ORDER_ID, binding)
    run_id = binding.run_id
    world = _World()
    docker = XFakeDocker(world, subject_hold_seconds=hold_seconds)
    work = base / "work"
    control = base / "control"
    evidence = base / "evidence" / "native-owner-evidence.json"
    hermetic = base / "hermetic"
    hermetic.mkdir(exist_ok=True)
    _x_hermetic(hermetic, monkeypatch, docker, control)
    proc_root = base / "proc"
    proc_root.mkdir(exist_ok=True)
    (proc_root / "1").mkdir(exist_ok=True)
    docker.proc_root = proc_root
    owner = flocal.LocalFixtureOwner(
        repo, work, evidence, head, control, executor=docker, binding=binding
    )
    thread = threading.Thread(target=owner.serve, daemon=True)
    thread.start()
    ok = False
    try:
        end = time.monotonic() + 30.0
        while time.monotonic() < end:
            if flocal._state_record(control) is not None:
                break
        prepared = _client(control, "prepare", run_id)
        assert prepared["ok"] is True, prepared
        cid = str(prepared["detail"]["cid"])
        assert cid == world.cid  # the world carries the ACTUAL created CID
        held = _client(control, "hold", run_id)
        assert held["ok"] is True, held
        ok = True
    finally:
        # bounded exact-owned convergence on failure paths only:
        # a still-held owner receives its own bounded abort over
        # the protected interface and is joined
        if not ok:
            _join_owner(thread, control=control, run_id=run_id)
    return {
        "repo": repo,
        "head": head,
        "run_id": run_id,
        "cid": cid,
        "control": control,
        "evidence": evidence,
        "thread": thread,
        "owner": owner,
        "world": world,
        "docker": docker,
        "channel": _FakeChannel(cid, world, exe_digest="a" * 64),
        "token": held["detail"]["hold_token"],
        "proc_root": proc_root,
    }


def _coupled_capability(ctx: dict[str, Any]) -> dict[str, object]:
    """The measured coupled capability facts: the bounded
    exact-CID inventory (per-attested-pid host consults only),
    the scoped live measurement WHILE the subject is alive, and
    the bounded natural-exit observation (the subject's own
    finite hold — no signal)."""
    channel: _FakeChannel = ctx["channel"]
    proc_root: Path = ctx["proc_root"]
    token: str = ctx["token"]
    pre_rows = fxc.discover_inventory(channel, proc_root, [1], token=None)
    assert len(pre_rows) == 1
    post_rows = fxc.discover_inventory(channel, proc_root, [1, 60], token=token)
    subject, corr = fxc.correlate_subject(pre_rows, post_rows, token)
    assert corr == "correlated" and subject is not None
    pid = int(subject["pid"])
    birth = int(subject["birth"])
    measured = fxc.measure_live_subject(channel, pid, birth, token=token)
    # every scoped exe access observed the ALIVE subject
    assert channel.exe_accesses and all(channel.exe_accesses)
    assert measured["process_identity"] == "measured"
    assert measured["executable"] == "measured"
    assert measured["executable_sha256"] == "a" * 64
    exit_state = fxc.wait_natural_exit(channel, pid, bound=15.0)
    assert exit_state == "verified-gone"
    return {
        "cid": ctx["cid"],
        "subject": {
            "pid": pid,
            "birth": birth,
            "uid": int(subject["uid"]),
            "gid": int(subject["gid"]),
            "groups": list(subject["groups"]),
        },
        "process_identity": str(measured["process_identity"]),
        "executable": str(measured["executable"]),
        "executable_sha256": measured["executable_sha256"],
        "pre_inventory_rows": len(pre_rows),
        "post_inventory_rows": len(post_rows),
        "inventory_rows_max": fxc.INVENTORY_ROWS_MAX,
        "subject_exit": exit_state,
    }


def _coupled_terminal(
    ctx: dict[str, Any],
    capability: dict[str, object],
    *,
    abort: bool,
    finalize_pass: bool,
    record_out: Path,
    record_run: str | None = None,
    reason: str | None = None,
) -> dict[str, object]:
    """The REAL _terminal over the coupled composition: the
    owner's thread lifecycle coupled as the process/reader
    facts (the owner never signalled by the terminal)."""

    class _CoupledProc:
        def poll(self) -> int | None:
            return None if ctx["thread"].is_alive() else ctx["owner"]._exit_code

        def wait(self, timeout: float) -> int:
            ctx["thread"].join(min(float(timeout), 0.2))
            value = self.poll()
            if value is None:
                raise subprocess.TimeoutExpired("synthetic coupled owner", timeout)
            return value

    class _CoupledReader:
        def is_alive(self) -> bool:
            alive = ctx["thread"].is_alive()
            return bool(alive)

        def join(self, timeout: float) -> None:
            ctx["thread"].join(min(float(timeout), 0.1))

    run_id = record_run or ctx["run_id"]
    record = fxc._driver_record(
        "fail" if reason is not None else "pass",
        reason,
        bind_head=ctx["head"],
        run_id=run_id,
        capability=capability,
    )
    result: dict[str, object] = fxc._terminal(
        ctx["repo"],
        _CoupledProc(),
        _CoupledReader(),
        ctx["control"],
        run_id,
        time.monotonic() + 10.0,
        ctx["evidence"],
        record,
        record_out,
        abort=abort,
        finalize_pass=finalize_pass,
    )
    return result


def test_terminal_coupled_public_owner_measures_before_finish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The coupled public-owner terminal positive (b): the real
    driver terminal converges the SAME LIVE owner AFTER the
    scoped live measurement of the subject's executable happened
    WHILE the subject was alive and BEFORE the owner's own
    finish — the real bound evidence bytes, the ONE shared
    admission's terminal finalization, the protected retention
    FIRST, and the retained record bytes IMMUTABLE at retention
    time (the later RAM finalize facts are never rewritten into
    them)."""
    base = tmp_path / "coupled"
    base.mkdir()
    os.chmod(base, 0o700)  # the protected record-parent root
    ctx = _coupled_owner_held(base, monkeypatch)
    try:
        capability = _coupled_capability(ctx)
        finished = _client(ctx["control"], "finish", ctx["run_id"])
        assert finished["ok"] is True, finished
        assert finished["detail"]["outcome"] == "pass"
        _join_owner(ctx["thread"], control=ctx["control"], run_id=ctx["run_id"])
        assert ctx["owner"].terminal_outcome == "pass"
        result = _coupled_terminal(
            ctx,
            capability,
            abort=False,
            finalize_pass=True,
            record_out=base / "capability.json",
        )
    finally:
        if ctx["thread"].is_alive():
            _join_owner(ctx["thread"], control=ctx["control"], run_id=ctx["run_id"])
    assert result["status"] == "pass"
    assert result["reason"] is None
    assert result["run_id"] == ctx["run_id"]
    assert result["terminal_command"] == "none"
    assert result["owner_exit"] == 0
    assert result["reader_state"] == "drained"
    assert result["capture_state"] == "drained"
    assert result["evidence_state"] == "verified-pass"
    assert result["evidence_sha256"] == hashlib.sha256(ctx["evidence"].read_bytes()).hexdigest()
    assert result["retention"] == "retained"
    assert result["finalize"] == "finalized"
    cap_result = result["capability"]
    assert isinstance(cap_result, dict)
    assert cap_result["executable_sha256"] == "a" * 64
    # the ONE shared admission: the terminal finalization is the
    # ONLY terminal journal entry
    assert _journal(ctx["repo"]) == [
        {"head": ctx["head"], "run_id": ctx["run_id"], "status": "pass"}
    ]
    payload = json.loads((base / "capability.json").read_bytes())
    assert payload == {
        **result,
        "retention": "not-requested",
        "finalize": "not-attempted",
    }


def test_terminal_coupled_abort_converges_real_owner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The terminal's bounded abort reaches the SAME LIVE real
    owner over the protected interface (never a host signal):
    the held owner converges itself as aborted, the PRIMARY
    phase reason is preserved (the owner's own fail evidence is
    a separate verified fact), the already-terminal journal
    entry is preserved (never rewritten), and the closed
    terminal-preserved token is recorded."""
    base = tmp_path / "abort"
    base.mkdir()
    os.chmod(base, 0o700)  # the protected record-parent root
    ctx = _coupled_owner_held(base, monkeypatch)
    try:
        capability = _coupled_capability(ctx)
        result = _coupled_terminal(
            ctx,
            capability,
            abort=True,
            finalize_pass=False,
            record_out=base / "capability.json",
            reason="cap-subject-vanished",
        )
    finally:
        if ctx["thread"].is_alive():
            _join_owner(ctx["thread"], control=ctx["control"], run_id=ctx["run_id"])
    assert result["status"] == "fail"
    assert result["reason"] == "cap-subject-vanished"  # primary preserved
    assert result["terminal_command"] == "abort"
    assert result["owner_exit"] == 130
    assert result["evidence_state"] == "verified-fail"
    assert result["finalize"] == "terminal-preserved"
    assert not ctx["thread"].is_alive()
    assert ctx["owner"].terminal_outcome == "aborted"
    assert _journal(ctx["repo"]) == [
        {"head": ctx["head"], "run_id": ctx["run_id"], "status": "aborted"}
    ]


def test_terminal_refused_retention_preserves_original(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A PRE-EXISTING record destination is a closed retention
    refusal: the qualified pass is refused (never an overwrite),
    the original bytes are preserved byte- and inode-for-byte,
    and the SAME bound attempt closes as fail (no fresh-path
    retry, no journal pass)."""
    base = tmp_path / "retention"
    base.mkdir()
    os.chmod(base, 0o700)  # the protected record-parent root
    ctx = _coupled_owner_held(base, monkeypatch)
    try:
        capability = _coupled_capability(ctx)
        finished = _client(ctx["control"], "finish", ctx["run_id"])
        assert finished["ok"] is True, finished
        _join_owner(ctx["thread"], control=ctx["control"], run_id=ctx["run_id"])
        dest = base / "capability.json"
        dest.write_bytes(b"preserved original\n")
        os.chmod(dest, 0o600)
        original = dest.read_bytes()
        inode = dest.stat().st_ino
        result = _coupled_terminal(
            ctx, capability, abort=False, finalize_pass=True, record_out=dest
        )
    finally:
        if ctx["thread"].is_alive():
            _join_owner(ctx["thread"], control=ctx["control"], run_id=ctx["run_id"])
    assert result["status"] == "fail"
    assert result["reason"] == "cap-record-retention"
    assert result["retention"] == "refused"
    assert dest.read_bytes() == original
    assert dest.stat().st_ino == inode
    assert _journal(ctx["repo"]) == [
        {"head": ctx["head"], "run_id": ctx["run_id"], "status": "fail"}
    ]


def test_terminal_unverified_finalize_preserves_running(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A post-retention UNVERIFIED finalization (the journal
    read-back cannot be verified) never returns a qualified
    success: the retained record and its actual journal facts
    are preserved (the running attempt is NOT rewritten to
    fail), and the closed token is recorded on the fail
    record."""
    base = tmp_path / "unverified"
    base.mkdir()
    os.chmod(base, 0o700)  # the protected record-parent root
    ctx = _coupled_owner_held(base, monkeypatch)
    try:
        capability = _coupled_capability(ctx)
        finished = _client(ctx["control"], "finish", ctx["run_id"])
        assert finished["ok"] is True, finished
        _join_owner(ctx["thread"], control=ctx["control"], run_id=ctx["run_id"])
        original_finalize = fxc.oap_binding.record_order_attempt

        def unverified(*args: Any) -> str:
            return "record-unreadable" if args[-1] == "pass" else original_finalize(*args)

        monkeypatch.setattr(fxc.oap_binding, "record_order_attempt", unverified)
        result = _coupled_terminal(
            ctx, capability, abort=False, finalize_pass=True, record_out=base / "c.json"
        )
    finally:
        if ctx["thread"].is_alive():
            _join_owner(ctx["thread"], control=ctx["control"], run_id=ctx["run_id"])
    assert result["status"] == "fail"
    assert result["reason"] == "local-driver-finalize"
    assert result["retention"] == "retained"
    assert result["finalize"] == "record-unreadable"
    # the post-retention unverified finalization preserves the
    # ACTUAL journal facts (running — never rewritten to fail)
    assert _journal(ctx["repo"]) == [
        {"head": ctx["head"], "run_id": ctx["run_id"], "status": "running"}
    ]


def test_terminal_foreign_run_id_not_finalized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A terminal record carrying a FOREIGN run id (absent from
    the journal) can never qualify: the bound evidence carries
    the real run id, so the record is invalid evidence for that
    foreign id, the foreign id is never finalized (the closed
    not-running token), and the real run's RUNNING attempt is
    preserved untouched."""
    base = tmp_path / "foreignrun"
    base.mkdir()
    os.chmod(base, 0o700)  # the protected record-parent root
    ctx = _coupled_owner_held(base, monkeypatch)
    try:
        capability = _coupled_capability(ctx)
        finished = _client(ctx["control"], "finish", ctx["run_id"])
        assert finished["ok"] is True, finished
        _join_owner(ctx["thread"], control=ctx["control"], run_id=ctx["run_id"])
        result = _coupled_terminal(
            ctx,
            capability,
            abort=False,
            finalize_pass=True,
            record_out=base / "capability.json",
            record_run="e" * 32,
        )
    finally:
        if ctx["thread"].is_alive():
            _join_owner(ctx["thread"], control=ctx["control"], run_id=ctx["run_id"])
    assert result["status"] == "fail"
    assert result["reason"] == "local-driver-evidence"
    assert result["evidence_state"] == "invalid"
    assert result["finalize"] == "not-running"
    assert _journal(ctx["repo"]) == [
        {"head": ctx["head"], "run_id": ctx["run_id"], "status": "running"}
    ]


def test_terminal_resolves_capture_state_after_drain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The capture state is a SHARED live holder read AFTER the
    reader is drained: a cap hit discovered DURING the final
    drain gates the pass (a value captured before the drain
    would have been ``drained``).  Driven on the real _terminal
    with a real exact-owned child (never signalled) and no
    backend."""
    repo, head = _x_git_fixture(tmp_path)
    binding = fb.resolve_order_binding(repo, X_ORDER_ID, head)
    fb.admit_order_attempt(repo, X_ORDER_ID, binding)
    run_id = binding.run_id
    control = tmp_path / "control"
    control.mkdir(mode=0o700)
    evidence_out = tmp_path / "evidence.json"  # absent: the capture fault is the first failure
    record_out = tmp_path / "record.json"
    record = fxc._driver_record(
        "pass",
        None,
        bind_head=head,
        run_id=run_id,
        owner_exit=0,
        capability={
            "cid": "d" * 64,
            "subject": {
                "pid": 60,
                "birth": 500,
                "uid": SUBJECT,
                "gid": SUBJECT,
                "groups": [SUBJECT],
            },
            "process_identity": "measured",
            "executable": "measured",
            "executable_sha256": "e" * 64,
            "pre_inventory_rows": 1,
            "post_inventory_rows": 2,
            "inventory_rows_max": fxc.INVENTORY_ROWS_MAX,
            "subject_exit": "verified-gone",
        },
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", CODE_EXIT0],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    box: list[str] = ["drained"]

    def flipper() -> None:
        time.sleep(0.3)
        box[0] = "cap"

    reader = threading.Thread(target=flipper, daemon=True)
    reader.start()
    try:
        result = fxc._terminal(
            repo,
            proc,
            reader,
            control,
            run_id,
            time.monotonic() + 10.0,
            evidence_out,
            record,
            record_out,
            abort=False,
            finalize_pass=True,
            capture_state=lambda: box[0],
        )
    finally:
        proc.wait(timeout=5.0)
        if proc.stdout is not None:
            proc.stdout.close()
    assert result["status"] == "fail"
    assert result["reason"] == "local-driver-output"
    assert result["capture_state"] == "cap"
    assert result["reader_state"] == "drained"
    assert result["owner_exit"] == 0
    assert result["evidence_state"] == "missing"
    assert result["finalize"] == "finalized"
    assert result["retention"] == "retained"
    assert _journal(repo) == [{"head": head, "run_id": run_id, "status": "fail"}]


def test_driver_capture_cap_forbids_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A TOTAL capture cap (the sealed child's output exceeds the
    closed bound) is a closed driver fault: the qualified pass is
    gated off, the SAME pending attempt is closed as fail, and
    the record is retained best-effort (no journal pass)."""
    stage = _stage1_owner_pass(tmp_path / "cap", monkeypatch)
    base = tmp_path / "cap-run"
    out = _driver_run(
        base,
        monkeypatch,
        stage,
        client=_happy_client(stage, base / "proc", base / "converge-flag", base / "evidence.json"),
        child_code=CODE_CAP,
        converge_flag=base / "converge-flag",
    )
    record = out["record"]
    assert record["status"] == "fail"
    assert record["reason"] == "local-driver-output"
    assert record["capture_state"] == "cap"
    assert record["terminal_command"] == "none"
    assert record["owner_exit"] == 0
    assert record["evidence_state"] == "verified-pass"
    assert record["finalize"] == "finalized"
    assert record["retention"] == "retained"
    assert _journal(stage["repo"]) == [
        {"head": stage["head"], "run_id": stage["run_id"], "status": "fail"}
    ]


def test_driver_capture_read_error_forbids_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pipe READ ERROR in the output reader is the same closed
    driver fault class: the qualified pass is gated off and the
    attempt closes as fail (the primary record is retained)."""
    stage = _stage1_owner_pass(tmp_path / "readerr", monkeypatch)
    base = tmp_path / "readerr-run"
    out = _driver_run(
        base,
        monkeypatch,
        stage,
        client=_happy_client(stage, base / "proc", base / "converge-flag", base / "evidence.json"),
        child_code=CODE_EXIT0,
        converge_flag=base / "converge-flag",
        err_stream=True,
    )
    record = out["record"]
    assert record["status"] == "fail"
    assert record["reason"] == "local-driver-output"
    assert record["capture_state"] == "read-error"
    assert record["finalize"] == "finalized"
    assert record["retention"] == "retained"
    assert _journal(stage["repo"]) == [
        {"head": stage["head"], "run_id": stage["run_id"], "status": "fail"}
    ]


def test_driver_expired_budget_refuses_before_blocking_wait(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An EXPIRED remaining budget refuses BEFORE any blocking
    wait and before ANY control I/O: the still-running owner is
    distinguished by a non-blocking poll only (owner_exit None),
    the reader is reaped with the zero remaining budget (held),
    no terminal command is issued, and the same attempt closes
    as fail on the primary patience reason."""
    stage = _stage1_owner_pass(tmp_path / "expired", monkeypatch)
    base = tmp_path / "expired-run"
    calls: list[str] = []

    def refuse_client(
        _control_dir: Any, command: str, _run_id: str, _timeout: float
    ) -> dict[str, Any]:
        calls.append(command)
        raise AssertionError("expired budget: no control I/O may be issued")

    # deterministic expired anchor: the published anchor must be
    # POSITIVE (the closed state grammar) yet expired (anchor +
    # grace < now).  A real-clock relative anchor cannot satisfy
    # both on a fresh runner with low monotonic() uptime (a
    # negative anchor would be rejected as malformed state and the
    # driver would time out in the startup loop instead); pin the
    # driver's own clock far past a small positive anchor so the
    # expired state is proven BEFORE any I/O regardless of the
    # runner's uptime.
    fake_now = 1.0e9
    monkeypatch.setattr(fxc.time, "monotonic", lambda: fake_now)
    out = _driver_run(
        base,
        monkeypatch,
        stage,
        client=refuse_client,
        converge_flag=base / "converge-flag",
        end_anchor=1.0,
    )
    assert calls == []
    record = out["record"]
    assert record["status"] == "fail"
    assert record["reason"] == "local-driver-patience"
    assert record["terminal_command"] == "none"
    assert record["owner_exit"] is None  # polled, never waited on
    assert record["reader_state"] == "held"
    assert record["evidence_state"] == "missing"
    assert record["finalize"] == "finalized"
    assert record["retention"] == "retained"
    assert _journal(stage["repo"]) == [
        {"head": stage["head"], "run_id": stage["run_id"], "status": "fail"}
    ]


def _fail_evidence_bytes(stage: dict[str, Any]) -> bytes:
    """A VALID closed native fail-form record with a DIFFERENT
    owner reason (the primary phase reason must survive it)."""
    rec: dict[str, Any] = {
        "record": flocal.NATIVE_OWNER_RUN_EVIDENCE_SCHEMA,
        "scope": flocal.NATIVE_OWNER_RUN_SCOPE,
        "status": "fail",
        "order": X_ORDER_ID,
        "run_id": stage["run_id"],
        "bind_head": stage["head"],
        "deadline_expired": True,
        "reason": "deadline-expired",
        "stage": "cleanup",
        "cleanup_failures": [],
        "phases_completed": ["start", "work-root", "preflight", "collision", "artifact"],
        "resources": {
            "containers": [],
            "create_intent": None,
            "image_id": None,
            "build_attempted": True,
            "env_file": None,
        },
        "recovery_state_retained": False,
        "ledger": {
            "docker_admissions": 0,
            "docker_refusals": 0,
            "bytes_drained": 0,
            "bytes_retained": 0,
            "api_requests": 0,
            "api_attempts": 0,
            "requests_admitted": 0,
            "requests_refused": 0,
            "healthz_attempts": 0,
        },
        "runner_kernel": "5.15.0",
        "runner_arch": "x86_64",
        "runner_python": "3.12.0",
    }
    flocal.validate_native_owner_run_evidence(rec)
    return (json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def test_driver_failed_hold_refusal_preserves_primary_reason(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A refused one-shot hold is the experiment's closed
    conclusion: the PRIMARY phase reason survives the owner's
    own (valid, different) fail evidence, the driver issues the
    owner's OWN bounded abort (never a host signal) which the
    fake owner side answers by converging itself, the finish is
    never issued, and the same attempt closes as fail."""
    stage = _stage1_owner_pass(tmp_path / "failedhold", monkeypatch)
    base = tmp_path / "failedhold-run"
    flag = base / "converge-flag"

    def client(_control_dir: Any, command: str, run_id: str, _timeout: float) -> dict[str, Any]:
        assert run_id == stage["run_id"]
        if command == "prepare":
            return {
                "ok": True,
                "reason": None,
                "detail": {
                    "cid": stage["cid"],
                    "state": "prepared",
                    "observed": 0,
                    "end_anchor": 1.0,
                },
            }
        if command == "top":
            return {"ok": True, "reason": None, "detail": {"pids": [1], "rows": 1}}
        if command == "hold":
            return {"ok": False, "reason": "local-hold-start-failed", "detail": None}
        if command == "abort":
            # the fake OWNER side converges itself on the abort
            # command (the driver never signals the owner) and
            # retains its own valid fail evidence
            with contextlib.suppress(OSError):
                flag.touch()
            base_evidence = base / "evidence.json"
            base_evidence.write_bytes(_fail_evidence_bytes(stage))
            os.chmod(base_evidence, 0o600)
            return {"ok": True, "reason": None, "detail": {"outcome": "aborted"}}
        raise AssertionError(f"finish must never be issued, got {command}")

    out = _driver_run(base, monkeypatch, stage, client=client, converge_flag=flag)
    record = out["record"]
    assert record["status"] == "fail"
    assert record["reason"] == "local-hold-start-failed"  # primary preserved
    assert record["terminal_command"] == "abort"
    assert record["owner_exit"] == 0  # the owner side converged on the abort
    assert record["reader_state"] == "drained"
    assert record["evidence_state"] == "verified-fail"
    assert record["finalize"] == "finalized"
    assert record["retention"] == "retained"
    cap = record["capability"]
    assert cap["process_identity"] == "not-measured"
    assert cap["subject"] is None
    assert cap["subject_exit"] == "not-observed"
    assert _journal(stage["repo"]) == [
        {"head": stage["head"], "run_id": stage["run_id"], "status": "fail"}
    ]


def test_driver_ambiguous_duplicate_subject_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TWO fresh closed-form members (same token, distinct
    births) are a closed REFUSAL: the driver never silently
    selects the first candidate; the run converges through its
    own bounded abort and the same attempt closes as fail (the
    owner's evidence is never reached — missing)."""
    stage = _stage1_owner_pass(tmp_path / "ambiguous", monkeypatch)
    base = tmp_path / "ambiguous-run"
    world: _World = stage["world"]
    flag = base / "converge-flag"
    state = {"post_hold": False}

    def client(_control_dir: Any, command: str, run_id: str, _timeout: float) -> dict[str, Any]:
        assert run_id == stage["run_id"]
        if command == "prepare":
            return {
                "ok": True,
                "reason": None,
                "detail": {
                    "cid": stage["cid"],
                    "state": "prepared",
                    "observed": 0,
                    "end_anchor": 1.0,
                },
            }
        if command == "top":
            pids = [1, 60, 61] if state["post_hold"] else [1]
            return {"ok": True, "reason": None, "detail": {"pids": pids, "rows": len(pids)}}
        if command == "hold":
            if not state["post_hold"]:
                state["post_hold"] = True
                (base / "proc" / "60").mkdir()
                (base / "proc" / "61").mkdir()
                world.launch_subject(TOKEN)
                world.add_subject(61, TOKEN)
            return {"ok": True, "reason": None, "detail": {"hold_token": TOKEN}}
        if command == "abort":
            with contextlib.suppress(OSError):
                flag.touch()
            return {"ok": True, "reason": None, "detail": {"outcome": "aborted"}}
        raise AssertionError(f"finish must never be issued, got {command}")

    out = _driver_run(base, monkeypatch, stage, client=client, converge_flag=flag)
    record = out["record"]
    assert record["status"] == "fail"
    assert record["reason"] == "cap-correlation-ambiguous"
    assert record["terminal_command"] == "abort"
    assert record["evidence_state"] == "missing"
    cap = record["capability"]
    assert cap["process_identity"] == "refused"
    assert cap["subject"] is None
    assert cap["subject_exit"] == "not-observed"
    assert record["finalize"] == "finalized"
    assert record["retention"] == "retained"
    assert _journal(stage["repo"]) == [
        {"head": stage["head"], "run_id": stage["run_id"], "status": "fail"}
    ]


def test_driver_identity_mismatch_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A fresh closed-form member that does NOT carry the subject
    identity law (UID/GID 21002) is a closed refusal after the
    bounded scan window (shortened here only for test time — the
    correlation law is unchanged); the attempt closes as fail."""
    stage = _stage1_owner_pass(tmp_path / "mismatch", monkeypatch)
    base = tmp_path / "mismatch-run"
    world: _World = stage["world"]
    world.subject_uid = 21001
    world.subject_gid = 21001
    world.subject_groups = (21001,)
    flag = base / "converge-flag"
    state = {"post_hold": False}

    def client(_control_dir: Any, command: str, run_id: str, _timeout: float) -> dict[str, Any]:
        assert run_id == stage["run_id"]
        if command == "prepare":
            return {
                "ok": True,
                "reason": None,
                "detail": {
                    "cid": stage["cid"],
                    "state": "prepared",
                    "observed": 0,
                    "end_anchor": 1.0,
                },
            }
        if command == "top":
            pids = [1, 60] if state["post_hold"] else [1]
            return {"ok": True, "reason": None, "detail": {"pids": pids, "rows": len(pids)}}
        if command == "hold":
            if not state["post_hold"]:
                state["post_hold"] = True
                (base / "proc" / "60").mkdir()
                world.launch_subject(TOKEN)
            return {"ok": True, "reason": None, "detail": {"hold_token": TOKEN}}
        if command == "abort":
            with contextlib.suppress(OSError):
                flag.touch()
            return {"ok": True, "reason": None, "detail": {"outcome": "aborted"}}
        raise AssertionError(f"finish must never be issued, got {command}")

    monkeypatch.setattr(fxc, "SUBJECT_SCAN_WINDOW_SECONDS", 0.75)
    out = _driver_run(base, monkeypatch, stage, client=client, converge_flag=flag)
    record = out["record"]
    assert record["status"] == "fail"
    assert record["reason"] == "cap-correlation-identity-mismatch"
    assert record["terminal_command"] == "abort"
    cap = record["capability"]
    assert cap["process_identity"] == "refused"
    assert cap["subject"] is None
    assert record["finalize"] == "finalized"
    assert record["retention"] == "retained"
    assert _journal(stage["repo"]) == [
        {"head": stage["head"], "run_id": stage["run_id"], "status": "fail"}
    ]


def _tamper_bytes(evidence_bytes: bytes, mutate: Any) -> bytes:
    rec = json.loads(evidence_bytes.decode("ascii"))
    mutate(rec)
    return (json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def test_driver_foreign_and_s_scope_evidence_not_adopted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The retained owner evidence is BOUND to this exact
    attempt: a valid record carrying a foreign run id, and a
    record in the historical S scope (valid in its own scope),
    are both this run's INVALID evidence — the qualified pass is
    refused and the same attempt closes as fail."""
    cases = (
        ("foreign", lambda rec: rec.update({"run_id": "e" * 32})),
        (
            "s-scope",
            lambda rec: (
                rec.update({"record": flocal.SCHEMA, "order": "017-s"}),
                rec.pop("scope"),
                rec.update(
                    {
                        "native_started": False,
                        "worker_stopped": False,
                        "codex_invoked": False,
                        "native_ready": False,
                        "image_identity_vs_ci": False,
                    }
                ),
            ),
        ),
    )
    # BOTH real prior-owner stages (real synthetic git history) are
    # built BEFORE any driver run: the driver's fake sealed-child
    # Popen substitute must not be live while git builds the
    # fixture repositories.
    prepared = []
    for label, mutate in cases:
        stage = _stage1_owner_pass(tmp_path / label, monkeypatch)
        prepared.append((label, stage, _tamper_bytes(stage["evidence_bytes"], mutate)))
    for label, stage, tampered in prepared:
        base = tmp_path / f"{label}-run"
        flag = base / "converge-flag"

        def client(
            _control_dir: Any,
            command: str,
            run_id: str,
            _timeout: float,
            _stage: dict[str, Any] = stage,
            _bytes: bytes = tampered,
            _base: Path = base,
            _flag: Path = flag,
        ) -> dict[str, Any]:
            assert run_id == _stage["run_id"]
            if command == "prepare":
                return {
                    "ok": True,
                    "reason": None,
                    "detail": {
                        "cid": _stage["cid"],
                        "state": "prepared",
                        "observed": 0,
                        "end_anchor": 1.0,
                    },
                }
            if command == "top":
                pids = [1, 60] if _stage.get("_post_hold", False) else [1]
                return {"ok": True, "reason": None, "detail": {"pids": pids, "rows": len(pids)}}
            if command == "hold":
                if not _stage.get("_post_hold", False):
                    _stage["_post_hold"] = True
                    (_base / "proc" / "60").mkdir()
                    _stage["world"].launch_subject(TOKEN)

                    def _expire() -> None:
                        _stage["world"].subject = None
                        with contextlib.suppress(OSError):
                            (_base / "proc" / "60").rmdir()

                    threading.Timer(0.5, _expire).start()
                return {"ok": True, "reason": None, "detail": {"hold_token": TOKEN}}
            if command == "finish":
                (_base / "evidence.json").write_bytes(_bytes)
                os.chmod(_base / "evidence.json", 0o600)
                with contextlib.suppress(OSError):
                    _flag.touch()
                return {"ok": True, "reason": None, "detail": {"outcome": "pass"}}
            raise AssertionError(f"unexpected command: {command}")

        out = _driver_run(base, monkeypatch, stage, client=client, converge_flag=flag)
        record = out["record"]
        assert record["status"] == "fail", label
        assert record["reason"] == "local-driver-evidence", label
        assert record["evidence_state"] == "invalid", label
        assert record["terminal_command"] == "none", label
        assert record["finalize"] == "finalized", label
        assert record["retention"] == "retained", label
        assert _journal(stage["repo"]) == [
            {"head": stage["head"], "run_id": stage["run_id"], "status": "fail"}
        ], label


# -- the closed measurement/discovery truth (direct fake controls) ----------------
def test_measure_unknown_executable_coherent_identity() -> None:
    """Readable, frame-coherent identity with an unreadable/absent
    exe link is the HONEST unknown: the process identity stays
    measured (its closed frame law held), the executable capability
    is ``unknown`` with NO digest — never a fallback to an expected
    artifact hash, never a verified negative."""
    world = _World(CID)
    world.launch_subject(TOKEN)
    channel = _FakeChannel(CID, world, exe_digest=None)
    subject = world.subject
    assert subject is not None
    birth = fp.parse_proc_stat(subject["stat"]).start_time
    measured = fxc.measure_live_subject(channel, 60, birth, token=TOKEN)
    assert measured == {
        "process_identity": "measured",
        "executable": "unknown",
        "executable_sha256": None,
    }
    # the exe link WAS read (while the subject was alive) and found
    # absent — an honest unknown, measured on a coherent frame
    assert channel.exe_accesses == [True]


def test_measure_refuses_reused_pid_birth_mismatch() -> None:
    """A matching pid whose BIRTH differs (pid reuse) is a closed
    identity refusal BEFORE any executable read: no digest, no exe
    access, the executable capability is never measured."""
    world = _World(CID)
    world.launch_subject(TOKEN)
    channel = _FakeChannel(CID, world, exe_digest="a" * 64)
    measured = fxc.measure_live_subject(channel, 60, 999999, token=TOKEN)
    assert measured == {
        "process_identity": "refused",
        "executable": "not-measured",
        "executable_sha256": None,
    }
    assert channel.exe_accesses == []  # the frame refused first


def test_measure_refuses_frame_race_after_read() -> None:
    """An exec that changes the cmdline DURING the executable read
    is a frame race: the contradictory later frame is never stamped
    with the digest (refused, no digest) — a measured digest on the
    pre-exec frame would be a lie."""
    world = _World(CID)
    world.launch_subject(TOKEN)

    class _RacingChannel(_FakeChannel):
        def exe_sha256(self, pid: int, birth: int) -> str | None:
            digest = super().exe_sha256(pid, birth)
            # the subject execs to a foreign form mid-read
            raced = world.subject
            assert raced is not None
            raced["cmdline"] = b"evil\0binary\0"
            return digest

    channel = _RacingChannel(CID, world, exe_digest="a" * 64)
    subject = world.subject
    assert subject is not None
    birth = fp.parse_proc_stat(subject["stat"]).start_time
    measured = fxc.measure_live_subject(channel, 60, birth, token=TOKEN)
    assert measured == {
        "process_identity": "refused",
        "executable": "not-measured",
        "executable_sha256": None,
    }
    # the read happened (the subject was alive) and the frame
    # contradicted AFTER it
    assert channel.exe_accesses == [True]


def test_measure_refuses_subject_vanished_after_read() -> None:
    """A subject that EXITS during the executable read is an exit
    race: the post-read scoped reads no longer see the in-scope
    entry, the frame is contradictory (vanished), and the digest is
    never stamped (refused, no digest)."""
    world = _World(CID)
    world.launch_subject(TOKEN)

    class _VanishingChannel(_FakeChannel):
        def exe_sha256(self, pid: int, birth: int) -> str | None:
            digest = super().exe_sha256(pid, birth)
            # the subject's own finite lifetime ends mid-read
            world.subject = None
            return digest

    channel = _VanishingChannel(CID, world, exe_digest="a" * 64)
    subject = world.subject
    assert subject is not None
    birth = fp.parse_proc_stat(subject["stat"]).start_time
    measured = fxc.measure_live_subject(channel, 60, birth, token=TOKEN)
    assert measured == {
        "process_identity": "refused",
        "executable": "not-measured",
        "executable_sha256": None,
    }
    assert channel.exe_accesses == [True]


def test_discovery_absent_verified_vs_foreign_scope_refusal(tmp_path: Path) -> None:
    """The closed inventory truth: an attested member whose host
    entry is gone counts ABSENT only when the channel independently
    verifies the pid gone (tri-state True); an attested member that
    EXISTS on the host but is not in the registered CID scope
    (foreign cgroup / raced membership) is a closed refusal — never
    an absent row and never a silent skip."""
    proc_root = tmp_path / "proc"
    (proc_root / "1").mkdir(parents=True)
    # vanished member: entry gone + the channel verifies it gone
    world = _World(CID)  # controller only; the subject never launched
    channel = _FakeChannel(CID, world)
    rows = fxc.discover_inventory(channel, proc_root, [1, 60], token=TOKEN)
    assert [row["pid"] for row in rows] == [1]
    # foreign scope: the entry exists on the host but the registered
    # scope is not ours
    world2 = _World(CID)
    world2.launch_subject(TOKEN)
    (proc_root / "60").mkdir()
    foreign = _FakeChannel("e" * 64, world2)
    with pytest.raises(FixtureError) as exc:
        fxc.discover_inventory(foreign, proc_root, [1, 60], token=TOKEN)
    assert str(exc.value) == "cap-inventory-unverified"


# -- the driver terminal over the coupled owner (closed owner outcomes) -----------
def test_driver_failed_sealed_startup_closed_reason(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A SEALED child that refuses BEFORE the control surface (no
    root, no state) and exits with its own closed startup refusal
    line is honored: the driver returns the child's CLOSED reason
    with the child's actual exit code, issues NO command, adopts no
    identity, and leaves the prior bound attempt unmutated."""
    stage = _stage1_owner_pass(tmp_path / "startfail", monkeypatch)
    base = tmp_path / "startfail-run"
    calls: list[str] = []

    def refuse_client(
        _control_dir: Any, command: str, _run_id: str, _timeout: float
    ) -> dict[str, Any]:
        calls.append(command)
        raise AssertionError("failed startup: no command may be issued")

    out = _driver_run(
        base,
        monkeypatch,
        stage,
        client=refuse_client,
        converge_flag=base / "converge-flag",
        child_code=CODE_STARTUP_REFUSE,
        child_bootstraps=False,
    )
    assert calls == []
    record = out["record"]
    assert record["status"] == "fail"
    assert record["reason"] == "local-rehearsal-exists"  # the child's own closed reason
    assert record["owner_exit"] == 1
    assert record["run_id"] is None  # never adopted
    assert record["terminal_command"] == "none"
    assert record["reader_state"] == "drained"
    assert record["evidence_state"] == "not-verified"
    assert record["finalize"] == "not-attempted"
    assert record["retention"] == "not-requested"
    # the prior owner's bound attempt is never mutated
    assert _journal(stage["repo"]) == [
        {"head": stage["head"], "run_id": stage["run_id"], "status": "running"}
    ]
    assert not out["record_out"].exists()


def test_terminal_coupled_cleanup_failure_refuses_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The exact owned container removal FAILS at teardown: the
    owner converges as a closed fail (cleanup-failed, with the
    unverified container cleanup fact) and retains honest fail
    evidence; the terminal never returns a qualified pass over the
    owner's own closed failure — the owner's reason is reported and
    the same attempt is already closed by the owner."""
    base = tmp_path / "cleanupfail"
    base.mkdir()
    os.chmod(base, 0o700)  # the protected record-parent root
    ctx = _coupled_owner_held(base, monkeypatch)
    try:
        capability = _coupled_capability(ctx)
        # the exact owned container removal fails at teardown
        ctx["docker"].rm_rc = 1
        finished = _client(ctx["control"], "finish", ctx["run_id"])
        assert finished["ok"] is True, finished
        assert finished["detail"]["outcome"] == "fail", finished
        _join_owner(ctx["thread"], control=ctx["control"], run_id=ctx["run_id"])
        owner = ctx["owner"]
        assert owner.terminal_outcome == "fail"
        assert owner.failure_reason == "cleanup-failed"
        assert "container-cleanup-unverified" in owner.cleanup_failures
        result = _coupled_terminal(
            ctx,
            capability,
            abort=False,
            finalize_pass=True,
            record_out=base / "capability.json",
        )
    finally:
        if ctx["thread"].is_alive():
            _join_owner(ctx["thread"], control=ctx["control"], run_id=ctx["run_id"])
    assert result["status"] == "fail"
    assert result["reason"] == "cleanup-failed"  # the owner's closed reason
    assert result["evidence_state"] == "verified-fail"
    assert result["owner_exit"] == 1
    assert result["terminal_command"] == "none"
    assert result["finalize"] == "terminal-preserved"
    assert result["retention"] == "retained"
    assert _journal(ctx["repo"]) == [
        {"head": ctx["head"], "run_id": ctx["run_id"], "status": "fail"}
    ]


def test_terminal_coupled_unrelated_survival_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The UNRELATED parent sentinel dying mid-run is the fail-fast
    containment fact: the owner converges as a closed fail
    (sentinel-process-died) with honest fail evidence, and the
    terminal never returns a qualified pass over the owner's own
    closed failure.  The death is the test-side fixture operation on
    the owner's OWN exact-owned sentinel (the containment fact under
    test); the owner reaps it in its own cleanup."""
    base = tmp_path / "survival"
    base.mkdir()
    os.chmod(base, 0o700)  # the protected record-parent root
    ctx = _coupled_owner_held(base, monkeypatch)
    try:
        capability = _coupled_capability(ctx)
        sentinel = ctx["owner"].sentinel
        assert sentinel is not None
        sentinel.kill()  # the unrelated parent sentinel dies mid-run
        finished = _client(ctx["control"], "finish", ctx["run_id"])
        assert finished["ok"] is True, finished
        assert finished["detail"]["outcome"] == "fail", finished
        _join_owner(ctx["thread"], control=ctx["control"], run_id=ctx["run_id"])
        owner = ctx["owner"]
        assert owner.terminal_outcome == "fail"
        assert owner.failure_reason == "sentinel-process-died"
        result = _coupled_terminal(
            ctx,
            capability,
            abort=False,
            finalize_pass=True,
            record_out=base / "capability.json",
        )
    finally:
        if ctx["thread"].is_alive():
            _join_owner(ctx["thread"], control=ctx["control"], run_id=ctx["run_id"])
    assert result["status"] == "fail"
    assert result["reason"] == "sentinel-process-died"
    assert result["evidence_state"] == "verified-fail"
    assert result["owner_exit"] == 1
    assert result["terminal_command"] == "none"
    assert result["finalize"] == "terminal-preserved"
    assert result["retention"] == "retained"
    assert _journal(ctx["repo"]) == [
        {"head": ctx["head"], "run_id": ctx["run_id"], "status": "fail"}
    ]


def test_driver_main_closed_grammar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The driver's thin public entry is a CLOSED grammar: the
    explicit opt-in order id must be 017-x and the protected
    capability-record destination is REQUIRED by the preflight
    (the ONE qualification attempt is never admitted without its
    retention destination).  Any other form is a closed fail
    line BEFORE any launch — no sealed child, no backend."""
    import io

    launched: list[str] = []

    def refuse_popen(*args: Any, **kwargs: Any) -> Any:
        launched.append("launched")
        raise AssertionError("closed grammar: no launch may occur")

    monkeypatch.setattr(fxc.subprocess, "Popen", refuse_popen)
    args = [
        "capability",
        "--order",
        X_ORDER_ID,
        "--bind-head",
        "a" * 40,
        "--repo",
        str(tmp_path / "repo"),
        "--work",
        str(tmp_path / "work"),
        "--control-dir",
        str(tmp_path / "control"),
        "--evidence-out",
        str(tmp_path / "evidence.json"),
    ]
    # the record destination is REQUIRED by the preflight
    text = io.StringIO()
    with contextlib.redirect_stdout(text):
        rc = fxc.main(args)
    assert rc == 1
    line = json.loads(text.getvalue().strip().splitlines()[-1])
    assert line["record"] == fxc.DRIVER_RECORD
    assert line["status"] == "fail"
    assert line["reason"] == "local-args-invalid"
    assert line["bind_head"] == "0" * 40
    assert launched == []
    # the opt-in order id is closed: another order id is refused
    args2 = list(args)
    args2[args2.index("--order") + 1] = "017-s"
    text2 = io.StringIO()
    with contextlib.redirect_stdout(text2):
        rc2 = fxc.main(args2)
    assert rc2 == 1
    line2 = json.loads(text2.getvalue().strip().splitlines()[-1])
    assert line2["record"] == fxc.DRIVER_RECORD
    assert line2["status"] == "fail"
    assert line2["reason"] == "local-args-invalid"
    assert launched == []


def test_driver_record_out_inside_work_refused_before_launch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A --record-out at or UNDER the disposable work root is a
    closed READ-ONLY refusal before any launch, command or
    mutation — for absolute AND relative work/destination forms
    (the same lexical cwd convention as the publisher, no symlink
    resolution): the retained record must outlive the scratch
    root — it must not be destroyed with it, nor recreate the
    destroyed root after the owner's teardown."""

    def _refuse(*a: Any, **k: Any) -> Any:
        raise AssertionError("no launch may happen for this refusal")

    monkeypatch.setattr(fxc.subprocess, "Popen", _refuse)
    cases = [
        ("under", "work/record.json", False),
        ("work-itself", "work", False),
        ("relative", "work/record.json", True),
    ]
    for name, rel, chdir in cases:
        base = tmp_path / f"base-{name}"
        base.mkdir()
        os.chmod(base, 0o700)
        if chdir:
            monkeypatch.chdir(base)
            repo: Any = "repo"
            work: Any = "work"
            control: Any = "control"
            evidence: Any = "evidence.json"
            record_out_arg: Any = rel
        else:
            repo = tmp_path / "repo"
            work = base / "work"
            control = base / "control"
            evidence = base / "evidence.json"
            record_out_arg = base / rel
        record = fxc.run_exec_capability(
            repo,
            "f" * 40,
            work,
            control,
            evidence,
            record_out=record_out_arg,
        )
        assert record["record"] == fxc.DRIVER_RECORD
        assert record["status"] == "fail"
        assert record["reason"] == "record-out-inside-work"
        assert not (base / "control").exists()  # no bootstrap surface
        assert not (base / "work").exists()  # no scratch root created


# ---------------------------------------------------------------------------
# 017-y sealed entry: the DISTINCT namespace of the closed readiness
# diagnosis plus the ONE separately bound Python-only capability
# attempt.  The historical X entry/namespace/records are unchanged;
# Y evidence is never labeled X and a foreign record is never
# adopted as this run.
# ---------------------------------------------------------------------------


def test_y_full_positive_driver_retains_y_record_before_pass_finalization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The 017-y scripted driver positive through the public code:
    the real owner converges in the DISTINCT 017-y namespace, the
    real driver runs under the Y sealed entry, and the matching Y
    protected record is retained FIRST (tag/order paired to the
    entry) and only then the same-attempt terminal finalization.
    The retained record bytes are IMMUTABLE at retention time; the
    historical X namespace never exists in this synthetic
    repository, so no X journal entry can be adopted."""
    stage = _stage1_owner_pass_entry(tmp_path / "y-positive", monkeypatch, Y_ORDER_ID)
    base = tmp_path / "y-positive-run"
    flag = base / "converge-flag"
    out = _driver_run(
        base,
        monkeypatch,
        stage,
        client=_happy_client(stage, base / "proc", flag, base / "evidence.json"),
        converge_flag=flag,
        entry_order=Y_ORDER_ID,
    )
    record = out["record"]
    assert record["status"] == "pass"
    assert record["reason"] is None
    assert record["order"] == Y_ORDER_ID
    assert record["record"] == "slaif-017y-exec-capability-driver-v1"
    assert record["run_id"] == stage["run_id"]
    assert record["retention"] == "retained"
    assert record["finalize"] == "finalized"
    # the retained record is IMMUTABLE at retention time and
    # paired to the Y entry (the W ordering; no X label anywhere)
    payload = json.loads(out["record_out"].read_bytes())
    assert payload["order"] == Y_ORDER_ID
    assert payload["record"] == "slaif-017y-exec-capability-driver-v1"
    assert payload == {
        **record,
        "retention": "not-requested",
        "finalize": "not-attempted",
    }
    assert stat.S_IMODE(out["record_out"].stat().st_mode) == 0o600
    # the ONE Y admission: the driver's terminal finalization is
    # the ONLY terminal journal entry, in the 017-y namespace
    assert _journal_for(stage["repo"], Y_ORDER_ID) == [
        {"head": stage["head"], "run_id": stage["run_id"], "status": "pass"}
    ]
    # the historical X namespace was never admitted in this
    # repository — nothing is adopted or reconstructed
    assert _journal_for(stage["repo"], X_ORDER_ID) == []
    assert out["elapsed"] < 60.0


def test_retain_record_cross_entry_refused(tmp_path: Path) -> None:
    """The closed record-pair law: a retained record is valid
    ONLY under its canonical entry.  The canonical X and Y pairs
    pass; a Y record under the X entry, an X record under the Y
    entry, and any caller-created descriptor (a known order
    paired with the wrong tag, or an unknown order/tag) are
    refused BEFORE any destination is touched."""
    cap = fxc._SEALED_ENTRIES

    def canonical(order: str, dest: Path) -> None:
        record = fxc._driver_record(
            "pass", None, bind_head="1" * 40, run_id="1" * 32, entry=cap[order]
        )
        fxc._retain_record(record, dest, cap[order])
        kept = json.loads(dest.read_bytes())
        assert kept["order"] == order

    canonical(X_ORDER_ID, tmp_path / "x.json")
    canonical(Y_ORDER_ID, tmp_path / "y.json")

    # Y record presented under the X entry: schema refusal, no file
    y_record = fxc._driver_record(
        "pass", None, bind_head="1" * 40, run_id="1" * 32, entry=cap[Y_ORDER_ID]
    )
    with pytest.raises(fxc.FixtureError, match="cap-record-schema"):
        fxc._retain_record(y_record, tmp_path / "cross-1.json", cap[X_ORDER_ID])
    assert not (tmp_path / "cross-1.json").exists()

    # X record presented under the Y entry: schema refusal, no file
    x_record = fxc._driver_record(
        "pass", None, bind_head="1" * 40, run_id="1" * 32, entry=cap[X_ORDER_ID]
    )
    with pytest.raises(fxc.FixtureError, match="cap-record-schema"):
        fxc._retain_record(x_record, tmp_path / "cross-2.json", cap[Y_ORDER_ID])
    assert not (tmp_path / "cross-2.json").exists()

    # a caller-created descriptor (a known order paired with the
    # WRONG tag, and an unknown order/tag) is refused before any
    # field is trusted — even for a record it would otherwise
    # "accept"
    foreign = fxc._SealedEntry(
        Y_ORDER_ID, cap[Y_ORDER_ID].order_path, "slaif-017x-exec-capability-driver-v1"
    )
    with pytest.raises(fxc.FixtureError, match="cap-sealed-entry"):
        fxc._retain_record(y_record, tmp_path / "cross-3.json", foreign)
    unknown = fxc._SealedEntry("017-z", "oap/orders/017-z.md", "synthetic-foreign")
    with pytest.raises(fxc.FixtureError, match="cap-sealed-entry"):
        fxc._retain_record(y_record, tmp_path / "cross-4.json", unknown)
    assert not (tmp_path / "cross-3.json").exists()
    assert not (tmp_path / "cross-4.json").exists()


def test_y_driver_refuses_foreign_x_running_journal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Distinct namespaces: the driver under the Y entry never
    adopts the historical X running journal entry — the bound
    verification reads the 017-y namespace (absent here) and the
    launch is refused before any owner-side command (closed
    cap-binding-mismatch, no Y journal entry minted)."""
    stage = _stage1_owner_pass(tmp_path / "y-xstage", monkeypatch)
    base = tmp_path / "y-xstage-run"
    flag = base / "converge-flag"
    out = _driver_run(
        base,
        monkeypatch,
        stage,
        client=_happy_client(stage, base / "proc", flag, base / "evidence.json"),
        converge_flag=flag,
        entry_order=Y_ORDER_ID,
    )
    record = out["record"]
    assert record["status"] == "fail"
    assert record["reason"] == "cap-binding-mismatch"
    assert record["order"] == Y_ORDER_ID
    # the X attempt is left EXACTLY as the real owner left it
    # (running) — never closed, replaced or relabeled by the Y
    # driver; and the Y namespace stays empty
    assert _journal_for(stage["repo"], X_ORDER_ID) == [
        {"head": stage["head"], "run_id": stage["run_id"], "status": "running"}
    ]
    assert _journal_for(stage["repo"], Y_ORDER_ID) == []


def test_public_cli_entry_selection(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The public CLI entry selection: 017-y is a SEALED ENTRY id
    (the run is driven under the Y entry with its own order
    argv), the historical 017-x default keeps its exact meaning,
    and an unknown order id is a closed argument refusal BEFORE
    any run (no launch, no adoption)."""
    captured: dict[str, Any] = {}

    def fake_run(*args: Any, **kwargs: Any) -> dict[str, Any]:
        captured.update({"called": True, "entry": kwargs.get("entry")})
        record: dict[str, Any] = fxc._driver_record(
            "pass", None, bind_head="2" * 40, run_id="2" * 32, entry=kwargs["entry"]
        )
        return record

    monkeypatch.setattr(fxc, "run_exec_capability", fake_run)
    base_args = [
        "capability",
        "--bind-head",
        "2" * 40,
        "--repo",
        str(tmp_path / "repo"),
        "--work",
        str(tmp_path / "work"),
        "--control-dir",
        str(tmp_path / "control"),
        "--evidence-out",
        str(tmp_path / "evidence.json"),
        "--record-out",
        str(tmp_path / "record.json"),
    ]

    def run_main(order: str | None) -> dict[str, Any]:
        argv = list(base_args)
        if order is not None:
            argv += ["--order", order]
        import io

        text = io.StringIO()
        with contextlib.redirect_stdout(text):
            rc = fxc.main(argv)
        assert rc == (0 if order in ("017-x", "017-y") else 1)
        record: dict[str, Any] = json.loads(text.getvalue())
        return record

    # 017-y: the sealed entry is selected and the run is driven
    # under it (the owner argv carries the Y order id)
    record = run_main("017-y")
    assert record["status"] == "pass"
    assert record["order"] == Y_ORDER_ID
    assert record["record"] == "slaif-017y-exec-capability-driver-v1"
    assert captured["entry"] is fxc._SEALED_ENTRIES[Y_ORDER_ID]

    # 017-x: the historical default meaning, byte-for-byte
    captured.clear()
    record = run_main("017-x")
    assert record["status"] == "pass"
    assert record["order"] == X_ORDER_ID
    assert record["record"] == "slaif-017x-exec-capability-driver-v1"
    assert captured["entry"] is fxc._SEALED_ENTRIES[X_ORDER_ID]

    # an unknown order id: closed argument refusal, NO run
    captured.clear()
    record = run_main("017-z")
    assert record["status"] == "fail"
    assert record["reason"] == "local-args-invalid"
    assert "called" not in captured
