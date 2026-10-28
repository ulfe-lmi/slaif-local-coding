"""Coupled owner-UID native handoff integration tests (order 017-ac).

The canonical FUTURE 017-ad entry is exercised HERE as inert
software ONLY: the ACTUAL public composition
(``cache_native_fixture_native_owner.NativeOwnerRun``) over the
ACTUAL ``LocalFixtureOwner`` and the ACTUAL public staged
``NativeHandoffWorkflow`` with injected FAKE platform operations
only (fake git, fake docker, fake process table, faithful narrow
identity-reader seam and owned synthetic repositories).  NO
actual local Docker operation, NO native launch, NO worker stop,
NO TTY/job handoff, NO real fixture admission in the real
checkout, NO host signal, NO Codex client.  Fake proof is
software integration — it is never sealed-real-owner, native or
host readiness, and the 017-ad entry stays INERT, input-gated
and unqualified in this round (refused under AC-active before
admission, proven hermetically).

Layers (named separately, per the order):

* the COUPLED public-lifecycle layer: one coherent fake process
  world (bash 40, worker 50 with an unrelated SAME-UID frame,
  native subject 60 held out), the real constructor/admission/
  prepare/stop/register/observe/finish/restore/publish over the
  owner-UID subject 1001:1002, the distinct identity-bearing
  record tags at every retained layer (state, prep snapshot,
  owner evidence, native-owner evidence, native-run terminal)
  and the same frozen identity carried through all of them
  (compared, never rebased);
* the scripted/bootstrap layers: the closed tag/identity laws of
  the retained records (pure data), the frozen subject-identity
  construction law, the AD channel bound factory (320 MiB / 10 s
  clamped to the ABSOLUTE owner END) and the pre-admission
  repository-context refusals over owned synthetic repositories.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import json
import os
import shutil
import socket
import stat
import sys
import time
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_test_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# The owner-UID suite's fake-world builders (AA _World /
# AAFakeDocker / _write_proc_entry) are BORROADED FIRST: their
# interactions with the production modules are value-level only
# (closed JSON records, argv, file bytes over duck-typed seams),
# so the canonical production instances registered by the loads
# below stay shared and consistent across this module.
aa = _load_test_module("oap_ac_aa", REPO_ROOT / "tests" / "test_cache_native_fixture_owner_uid.py")
stl = _load_test_module("oap_ac_stl", REPO_ROOT / "tests" / "test_cache_native_fixture_local.py")
stp = _load_test_module(
    "oap_ac_stp", REPO_ROOT / "tests" / "test_cache_native_fixture_native_prep.py"
)

# The REAL composition module, canonical name (it reuses the
# same ci/local/prep/binding instances the suites above loaded).
FNO_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_native_owner.py"
_spec = importlib.util.spec_from_file_location("cache_native_fixture_native_owner", FNO_PATH)
assert _spec is not None and _spec.loader is not None
fno = importlib.util.module_from_spec(_spec)
sys.modules["cache_native_fixture_native_owner"] = fno
_spec.loader.exec_module(fno)

fci = sys.modules["cache_native_fixture_ci"]
fb = sys.modules["cache_native_fixture_binding"]
fp = sys.modules["cache_native_fixture_native_prep"]
flocal = sys.modules["cache_native_fixture_local"]
fi = sys.modules["cache_native_fixture_identity"]
frp = sys.modules["cache_native_fixture_runtime_profile"]
model = fci.model

HEAD = stl.HEAD
S_ORDER_NAME = Path(stl.ORDER_PATH).name
AC_ORDER_ID = "017-ac"
AC_ORDER_NAME = "017-ac-synthetic-active.md"
AC_ORDER_BYTES = b"# synthetic AC order (fake seam only)\n"
AD_ORDER_ID = "017-ad"
AD_ORDER_NAME = "017-ad-owner-uid-native-handoff-qualification.md"
AD_ORDER_BYTES = b"# synthetic AD order (fake seam only)\n"
# The synthetic 017-ae/017-af order names of the 017-ae gate
# tests (test order bytes ONLY in owned synthetic repositories
# — the real AF order is never created in this checkout).
AF_ORDER_ID = "017-af"
AF_ORDER_NAME = "017-af-owner-uid-native-pty-qualification.md"
AF_ORDER_BYTES = b"# synthetic AF order (fake seam only)\n"
AE_ORDER_ID = "017-ae"
AE_ORDER_NAME = "017-ae-synthetic-active.md"
AE_ORDER_BYTES = b"# synthetic AE order (fake seam only)\n"

SUBJ_UID = 1001
SUBJ_GID = 1002
FAKE_BINARY = hashlib.sha256(b"slaif-fake-native-binary").hexdigest()

# The coherent coupled world's PID map (ONE canonical map): the
# container members (the in-image controller 1, the staged
# native subject 60 — the SAME pids the AA world builders
# use) and the host job world OUTSIDE the container (bash 40,
# the UNRELATED same-UID worker 50 — never a container member,
# never a top row, never touched by the exact-CID removal).
CTL_PID = aa.CTL_PID
NAT_PID = aa.SUBJ_PID
CTL_UID = aa.CTL_UID
CTL_START = aa.CTL_START
NAT_START = aa.SUBJ_START
BASH_PID = 40
WORK_PID = 50
WORK_START = 500


def _ad_description() -> Any:
    return fi.FixtureIdentityDescription(
        profile=fi.PROFILE_OWNER_UID,
        controller_uid=fi.CONTROLLER_UID,
        controller_gid=fi.CONTROLLER_GID,
        subject_uid=SUBJ_UID,
        subject_gid=SUBJ_GID,
        subject_groups=(SUBJ_GID,),
    )


def _ad_identity_dict() -> dict[str, object]:
    """The frozen owner-identity substructure the production
    code derives from the frozen triple (never hand-typed
    digests)."""
    result: dict[str, object] = fp._ad_identity_substructure_from_triple(
        (SUBJ_UID, SUBJ_GID, (SUBJ_GID,))
    )
    return result


def _ad_reader() -> tuple[int, int, int, int, int, int]:
    return (SUBJ_UID, SUBJ_UID, SUBJ_UID, SUBJ_GID, SUBJ_GID, SUBJ_GID)


# -- the synthetic AD repository (owned, hermetic) ------------------------------
def _ad_repo(base: Path, *, active_order: str = AD_ORDER_ID) -> Path:
    """The S-shaped synthetic repo re-activated to the requested
    entry (AD by default; AC for the pre-admission refusal law):
    the committed order set gains the UNIQUE synthetic order and
    oap/active selects it (disk and committed).  Test order bytes
    live ONLY in owned synthetic repositories."""
    repo = Path(stl._make_local_repo(base))
    # the owner-variant build input the S-shaped base lacks
    # (the same faithful source set the AA git fixture commits):
    # the owner Dockerfile base, the inert identity contract
    # module and the entry modules the composition reads
    for name in (
        "cache_native_fixture_owner.Dockerfile",
        "cache_native_fixture_identity.py",
        "cache_native_fixture_native_prep.py",
        "cache_native_fixture_runtime_profile.py",
        "cache_native_fixture_binding.py",
    ):
        (repo / "scripts" / name).write_bytes((REPO_ROOT / "scripts" / name).read_bytes())
    if active_order == AD_ORDER_ID:
        (repo / "oap" / "orders" / AD_ORDER_NAME).write_bytes(AD_ORDER_BYTES)
    else:
        (repo / "oap" / "orders" / AC_ORDER_NAME).write_bytes(AC_ORDER_BYTES)
        (repo / "oap" / "orders" / AD_ORDER_NAME).write_bytes(AD_ORDER_BYTES)
    (repo / "oap" / "active").write_bytes(active_order.encode("ascii") + b"\n")
    return repo


def _ad_git_runner(repo: Path, *, head: str = HEAD, active_order: str = AD_ORDER_ID) -> Any:
    """The fake committed-context git runner (read-only queries
    only) for the synthetic repository."""

    def git_runner(args: list[str], cwd: Path) -> bytes:
        if args == ["rev-parse", "HEAD"]:
            return head.encode("ascii")
        if args == ["status", "--porcelain"]:
            return b""
        if args == ["remote", "get-url", "origin"]:
            return b"https://github.com/ulfe-lmi/slaif-local-coding.git\n"
        if args == ["ls-tree", "--name-only", f"{HEAD}:oap/orders"]:
            names = [S_ORDER_NAME]
            if active_order == AD_ORDER_ID:
                names.append(AD_ORDER_NAME)
            else:
                names += [AC_ORDER_NAME, AD_ORDER_NAME]
            return ("\n".join(names) + "\n").encode("ascii")
        if args == ["show", f"{HEAD}:oap/active"]:
            return active_order.encode("ascii") + b"\n"
        if args == ["show", f"{HEAD}:oap/orders/{S_ORDER_NAME}"]:
            return bytes(stl.ORDER_PATH.read_bytes())
        if args == ["show", f"{HEAD}:oap/orders/{AD_ORDER_NAME}"]:
            return AD_ORDER_BYTES
        if args == ["show", f"{HEAD}:oap/orders/{AC_ORDER_NAME}"]:
            return AC_ORDER_BYTES
        raise AssertionError(f"unexpected git args: {args}")

    return git_runner


def _af_repo(base: Path, *, active_order: str = AF_ORDER_ID) -> Path:
    """The S-shaped synthetic repo for the 017-ae gate tests:
    the AF canonical order file is committed; oap/active
    selects the requested entry (AF by default, AE for the
    pre-admission refusal law).  Test order bytes live ONLY in
    owned synthetic repositories — the real AF order is never
    created in this checkout."""
    repo = Path(stl._make_local_repo(base))
    for name in (
        "cache_native_fixture_owner.Dockerfile",
        "cache_native_fixture_identity.py",
        "cache_native_fixture_native_prep.py",
        "cache_native_fixture_runtime_profile.py",
        "cache_native_fixture_binding.py",
    ):
        (repo / "scripts" / name).write_bytes((REPO_ROOT / "scripts" / name).read_bytes())
    (repo / "oap" / "orders" / AF_ORDER_NAME).write_bytes(AF_ORDER_BYTES)
    if active_order == AE_ORDER_ID:
        (repo / "oap" / "orders" / AE_ORDER_NAME).write_bytes(AE_ORDER_BYTES)
    (repo / "oap" / "active").write_bytes(active_order.encode("ascii") + b"\n")
    return repo


def _af_git_runner(repo: Path, *, head: str = HEAD, active_order: str = AF_ORDER_ID) -> Any:
    """The fake committed-context git runner (read-only queries
    only) for the AF/AE synthetic repository."""

    def git_runner(args: list[str], cwd: Path) -> bytes:
        if args == ["rev-parse", "HEAD"]:
            return head.encode("ascii")
        if args == ["status", "--porcelain"]:
            return b""
        if args == ["remote", "get-url", "origin"]:
            return b"https://github.com/ulfe-lmi/slaif-local-coding.git\n"
        if args == ["ls-tree", "--name-only", f"{HEAD}:oap/orders"]:
            names = [S_ORDER_NAME]
            if active_order == AF_ORDER_ID:
                names.append(AF_ORDER_NAME)
            else:
                names += [AE_ORDER_NAME, AF_ORDER_NAME]
            return ("\n".join(names) + "\n").encode("ascii")
        if args == ["show", f"{HEAD}:oap/active"]:
            return active_order.encode("ascii") + b"\n"
        if args == ["show", f"{HEAD}:oap/orders/{S_ORDER_NAME}"]:
            return bytes(stl.ORDER_PATH.read_bytes())
        if args == ["show", f"{HEAD}:oap/orders/{AF_ORDER_NAME}"]:
            return AF_ORDER_BYTES
        if args == ["show", f"{HEAD}:oap/orders/{AE_ORDER_NAME}"]:
            return AE_ORDER_BYTES
        raise AssertionError(f"unexpected git args: {args}")

    return git_runner


def _hermetic(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fake: Any,
    control: Path,
    uid_calls: list[int],
) -> None:
    """The hermetic local environment over the CANONICAL module
    instances (the same law as the S local suite) — plus the
    global owner-UID scan TRAP: the stub records every scanned
    UID and refuses the subject-UID global scan on the owner-UID
    path (a bare zero stub would hide exactly the forbidden
    membership scan); the controller-UID scan keeps its closed
    historical semantics."""
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


# -- the coherent coupled world: ONE canonical process map ------------------------


def _worker_proc(state: str, *, tpgid: int, start: int = WORK_START) -> dict[str, Any]:
    """The UNRELATED same-UID worker's frame: the SAME UID/GID
    and birth across EVERY state transition — the operator's
    stop/restore changes only the stat state/foreground fields
    (a reset of the status bytes would make any same-UID
    survival claim dishonest)."""
    return {
        "stat": stp.stat_line(
            WORK_PID, "codex", state, BASH_PID, WORK_PID, 99, stp.TTYS, tpgid, start
        ),
        "cmdline": stp.CODEX_CMDLINE,
        "status": stp.status_bytes(SUBJ_UID, SUBJ_UID),
    }


class _ADWorld(aa._World):  # type: ignore[name-defined,misc]
    """The ONE canonical AD fake process map, observed by
    everything: the workflow's host table (bash 40, the
    unrelated same-UID worker 50 — both OUTSIDE the container
    CID, never top rows), the registered-CID channel, the fake
    daemon's exact-CID top, the in-image quiesce subject count
    and the exact-CID removal staging — plus the faithful
    synthetic-proc projection the REAL owner's bounded lifetime
    readers consume (container members only: controller 1 and,
    while launched, the native 60).  The native subject's
    lifecycle is the operator's EXPLICIT launch/exit event —
    never a docker-detached hold, never the AA finite-hold
    clock."""

    subject: dict[str, object] | None

    def __init__(self, proc_root: Path) -> None:
        super().__init__(proc_root)
        self.procs: dict[int, dict[str, Any]] = {
            BASH_PID: stp.bash_proc(BASH_PID, state="S", pgrp=BASH_PID),
            WORK_PID: _worker_proc("S", tpgid=WORK_PID, start=WORK_START),
        }
        self.native_launches = 0
        self.native_exits = 0

    def launch_native(self) -> None:
        """The operator's explicit native launch: the actual
        later native subject bound to the container's OWN
        registered CID — the SAME record projected into the
        canonical map and the synthetic proc view."""
        assert self.cid is not None, "the container is not created yet"
        assert self.subject is None, "one native subject per world"
        self.native_launches += 1
        self.subject = {"cgroup": self.cid}
        # the AA finite-hold clock does NOT govern the native
        # subject (its exit is the explicit event below)
        self.subject_started_at = None
        self.procs[NAT_PID] = stp.subject_proc(
            NAT_PID, cgroup=self.cid, uid=SUBJ_UID, gid=SUBJ_GID, groups=(SUBJ_GID,)
        )
        d = self.proc_root / str(NAT_PID)
        d.mkdir(parents=True, exist_ok=True)
        (d / "cgroup").write_text(f"0::/system.slice/docker-{self.cid}.scope\n", encoding="ascii")
        (d / "stat").write_text(
            stp.stat_line(NAT_PID, "codex", "S", 1, NAT_PID, 77, stp.TTYS, NAT_PID, NAT_START),
            encoding="ascii",
        )
        (d / "status").write_bytes(stp.status_bytes(SUBJ_UID, SUBJ_GID, (SUBJ_GID,)))

    def exit_native(self) -> None:
        """The explicit fake native exit: ABSENCE ONLY (no exit
        code or cause — the verified-gone law); the retained
        registration receipt stays history, never re-measured."""
        assert self.subject is not None, "no native subject to exit"
        self.native_exits += 1
        d = self.proc_root / str(NAT_PID)
        if d.is_dir():
            shutil.rmtree(d)
        self.procs.pop(NAT_PID, None)
        self.subject = None
        self.subject_started_at = None


class _ADFakeDocker(aa.AAFakeDocker):  # type: ignore[name-defined,misc]
    """The scripted fake docker over the AD coupled world: the
    closed original surface plus the owner-scoped argv (the
    frozen 1001:1002 exec user, the explicit v2 closed stand-in
    records, the owner tmpfs create spec echoed back), the
    exact-CID top over the SAME world members, the MEASURED
    in-image quiesce (a still-running native subject cannot
    truthfully yield closure — the canned all-closed record is
    never inherited) and the exact-CID removal staging over the
    same container-member frames.  The host bash/worker are
    never container members: no frame, never a top row, never
    touched by the removal."""

    def __init__(self, world: _ADWorld, proc_root: Path, *, rm_stage: str = "gone") -> None:
        super().__init__(world, proc_root, rm_stage=rm_stage)

    def __call__(self, argv: list[str], timeout: float) -> Any:
        if len(argv) >= 3 and argv[:2] == ["docker", "create"]:
            # the base create logic (name -> exact fresh CID),
            # then the container's ONLY initial member frame:
            # the in-image controller (the host job world stays
            # outside the container cgroup)
            result = aa.stl.LocalFakeDocker.__call__(self, argv, timeout)
            if result.returncode == 0:
                self._world.attach(result.output.decode("ascii").strip())
                aa._write_proc_entry(
                    self.proc_root,
                    CTL_PID,
                    comm="python3",
                    start=CTL_START,
                    uid=CTL_UID,
                    gid=CTL_UID,
                    groups=(),
                    cgroup=self._world.cid,
                )
            return result
        if argv[:3] == ["docker", "exec", "-d"]:
            # the AD native subject is NOT a docker-detached
            # hold: the operator's explicit world events are
            # the only native lifecycle seam
            return self._result(125, b"exec-refused\n")
        return super().__call__(argv, timeout)

    def _stage_post_removal(self) -> None:
        super()._stage_post_removal()
        # the container members leave the canonical map WITH the
        # container (the host job world is never touched)
        self._world.procs.pop(NAT_PID, None)


def _ad_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    world: _ADWorld,
    docker: _ADFakeDocker,
    reader: Any | None = None,
    git: Any | None = None,
) -> tuple[Any, Any, _ADFakeDocker, Path, Path, list[int]]:
    # _make_local_repo nests one level: the repo lands at
    # tmp_path/repo, the same place the journal readers address
    repo = _ad_repo(tmp_path)
    work = tmp_path / "work"
    control = tmp_path / "control"
    owner_evidence = tmp_path / "evidence" / "ad-owner-evidence.json"
    uid_calls: list[int] = []
    _hermetic(tmp_path, monkeypatch, docker, control, uid_calls)
    if git is None:
        git = _ad_git_runner(repo)
    table = stp.FakeTable(world.procs)
    binding = fb.resolve_order_binding(repo, AD_ORDER_ID, HEAD, git_runner=git)
    run = fno.NativeOwnerRun(
        binding,
        repo,
        work,
        owner_evidence,
        control,
        git_runner=git,
        executor=docker,
        table=table,
        worker_pid=WORK_PID,
        bash_pid=BASH_PID,
        tty_foreground_pgrp=WORK_PID,
        identity_reader=reader if reader is not None else _ad_reader,
        # the owner's EXISTING narrow proc seam: the coherent
        # world's synthetic-proc projection (production default
        # the actual /proc, unchanged)
        proc_root=world.proc_root,
    )
    return run, repo, docker, owner_evidence, control, uid_calls


def _join_run(run: Any) -> None:
    """Bounded reap: an owner that has NOT converged (still held)
    first receives the bounded EXACT-OWNER abort over its
    protected interface (never a host signal), then joins."""
    thread = run._thread
    if thread is None:
        return
    if thread.is_alive() and not run.owner._converged:
        with contextlib.suppress(Exception):
            flocal._control_client(run._control_dir, "abort", run._run_id, timeout=15.0)
    thread.join(60.0)
    assert not thread.is_alive(), "owner thread did not converge after bounded abort"


@contextlib.contextmanager
def _owned_run(run: Any) -> Any:
    """Per-test owner convergence (bounded reap in a finally):
    EVERY started test owner converges through the EXACT-OWNER
    protected abort when still held, then joins, even on an
    assertion failure and before monkeypatch teardown restores
    the real executor/endpoint seams — no framework, no host
    cleanup, no new signal.  Idempotent for an already
    converged owner."""
    try:
        yield
    finally:
        _join_run(run)


# -- the COUPLED public-lifecycle positive (the coherent fake world) --------------
def test_ad_full_public_native_lifecycle_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The useful 1001:1002 positive through the REAL public
    composition (constructor/admission/prepare/observe/stop/
    register/observe/finish/restore/publish) over ONE coherent
    coupled fake process world: one canonical PID map shared by
    the host table, the registered-CID channel, the exact-CID
    top, the measured quiesce and the exact-CID removal, with a
    faithful synthetic-proc projection the REAL owner's bounded
    lifetime readers consume themselves."""
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root)
    run, repo, fake, owner_evidence, control, uid_calls = _ad_run(
        tmp_path, monkeypatch, world=world, docker=fake
    )
    with _owned_run(run):
        binding = run.binding
        native_out = tmp_path / "evidence" / "ad-native-run-record.json"
        identity = _ad_identity_dict()
        # the ONE shared run context across the whole lifecycle
        ctx_before = run.owner._owner_context
        anchor_before = run.owner.deadline.anchor
        ledger_before = run.owner.ledger
        worker_birth = world.procs[WORK_PID]["stat"].split()[21]

        # 1. start: the owner publishes the binding's minted run id
        run_id = run.start()
        assert run_id == binding.run_id == run.owner.run_id

        # 2. the DISTINCT identity-bearing AD state form (the v1
        #    reader never sees it — the tag is entry-scoped)
        ad_state = flocal._state_record(control, entry_order=AD_ORDER_ID)
        assert ad_state is not None
        assert ad_state["record"] == flocal.AD_STATE_SCHEMA
        assert ad_state["order"] == AD_ORDER_ID
        assert ad_state["identity"]["subject_uid"] == SUBJ_UID
        assert ad_state["identity"]["subject_gid"] == SUBJ_GID
        assert ad_state["identity"]["subject_groups"] == [SUBJ_GID]
        assert flocal._state_record(control) is None

        # 3. prepare: the AD prep snapshot (the DISTINCT tag plus the
        #    production-derived identity; the subject is still staged)
        prepared = run.prepare()
        assert prepared["record"] == fp.AD_NATIVE_PREP_SCHEMA
        assert prepared["identity"] == identity
        assert prepared["subject"] is None
        fp.validate_prep_snapshot(prepared)
        assert run.owner.target_cid is not None
        # the frozen workflow subject law is the owner's own frozen
        # context (the real owner's OWN collected/derived identity)
        assert run.workflow.subject_identity == (SUBJ_UID, SUBJ_GID, (SUBJ_GID,))
        # the world attached on create with the controller frame
        # ONLY (the native subject is still staged; the host job
        # world has no container frame)
        assert world.cid == run.owner.target_cid
        assert (proc_root / str(CTL_PID) / "cgroup").is_file()
        assert not (proc_root / str(NAT_PID)).exists()
        assert world.native_launches == 0

        # 4. held observation (non-consuming, idempotent)
        run.observe()
        run.observe()

        # 5. the operator stops the worker: the STAT state/foreground
        #    fields change ONLY — the SAME UID/GID/birth survive the
        #    transition (claiming same-UID survival from an unchanged
        #    birth alone would be dishonest if the status were reset)
        world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
        stop = run.record_stop()
        assert run.workflow.stop_receipt is stop
        assert world.procs[WORK_PID]["stat"].split()[21] == worker_birth

        # 6. the operator launches the native subject bound to the
        #    owner's OWN registered CID (the frozen 1001:1002 form);
        #    registration reads the SAME canonical map through the
        #    registered-CID channel
        world.launch_native()
        assert world.procs[NAT_PID]["cgroup"] == run.owner.target_cid
        expectation = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256=FAKE_BINARY,
            run_id=binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        channel = stp.FakeCidScopedTable(
            str(run.owner.target_cid), world.procs, exe_digest=FAKE_BINARY
        )
        snapshot = run.register_subject(NAT_PID, expectation, channel=channel)
        assert snapshot["record"] == fp.AD_NATIVE_PREP_SCHEMA
        assert snapshot["identity"] == identity
        assert snapshot["subject"]["uid"] == SUBJ_UID
        assert snapshot["subject"]["gid"] == SUBJ_GID
        assert snapshot["subject"]["groups"] == [SUBJ_GID]
        fp.validate_prep_snapshot(snapshot)
        identity_receipt = run.workflow.subject_receipt
        assert identity_receipt is not None
        assert identity_receipt.uid == SUBJ_UID
        assert identity_receipt.gid == SUBJ_GID
        assert identity_receipt.groups == (SUBJ_GID,)
        assert identity_receipt.cid_membership == "cid-scoped"
        assert identity_receipt.binary_verified is True
        assert identity_receipt.pty_matched is True

        # 7. observe again: the retained receipt is never re-measured
        run.observe()

        # 8. the EXPLICIT fake native exit before the positive finish:
        #    absence only (no exit code or cause); the retained
        #    receipt stays history, never re-measured
        world.exit_native()
        assert world.native_exits == 1
        assert NAT_PID not in world.procs
        assert not (proc_root / str(NAT_PID)).exists()
        assert run.workflow.subject_receipt is not None

        # 9. finish: the REAL finish/export/teardown over the fake
        #    platform — the in-image quiesce MEASURES zero subjects
        #    (the exit happened; a still-running subject could never
        #    truthfully yield closure), the exact-CID removal removes
        #    the controller member, and the post-removal parser
        #    verifies ENOENT (verified-gone, tri-stated)
        run.finish()
        assert run.owner.terminal_outcome == "pass"
        _join_run(run)
        assert fake.last_quiesce is not None
        assert fake.last_quiesce["owned_subject_stopped"] is True
        assert run.owner.owned_members_before == ((CTL_PID, CTL_START, CTL_UID),)
        assert run.owner.owned_members_after == ((CTL_PID, "verified-gone"),)
        # the unrelated same-UID worker survived the whole run with
        # the SAME uid/gid AND the SAME birth
        worker = world.procs[WORK_PID]
        assert fp.parse_proc_status(worker["status"]) == (SUBJ_UID, SUBJ_UID, ())
        assert worker["stat"].split()[21] == worker_birth

        # 10. the operator restores the SAME worker job (stat-only)
        world.procs[WORK_PID] = _worker_proc("S", tpgid=WORK_PID, start=WORK_START)

        # 11. publish: the DISTINCT identity-bearing AD terminal
        #     record (owner evidence FIRST, native record SECOND,
        #     same-attempt finalization LAST)
        record_doc = run.publish_native(native_out)

        assert record_doc["record"] == fno.AD_NATIVE_RUN_SCHEMA
        assert record_doc["identity"] == identity
        assert record_doc["owner_outcome"] == "pass"
        assert record_doc["attempt"] == "running"  # pending, never a predicted token
        assert record_doc["subject_measured"] is True
        assert record_doc["stop_recorded"] is True
        assert record_doc["native_refusal"] is None
        assert record_doc["verdict"] == {"ready": True, "reasons": []}
        fno.parse_native_run_record(record_doc)
        facts = fp.parse_native_owner_facts(record_doc["native_record"])
        assert facts.schema == fp.AD_NATIVE_OWNER_SCHEMA
        assert facts.identity == (SUBJ_UID, SUBJ_GID, (SUBJ_GID,))
        assert facts.order == AD_ORDER_ID
        assert facts.source_head == HEAD
        assert facts.run_id == binding.run_id
        assert facts.cid == run.owner.target_cid
        assert facts.native_started is True
        assert facts.native_ready is True
        st = native_out.stat()
        assert (st.st_mode & 0o777) == 0o600 and st.st_uid == os.getuid()

        # the same-order journal is terminal pass ONLY after the
        # protected publication (the real finalize token in RAM)
        assert run.finalize_attempt() == "finalized"
        record = fb.read_admission_record(repo, AD_ORDER_ID)
        assert record["attempts"] == [{"head": HEAD, "run_id": binding.run_id, "status": "pass"}]

        # the owner's OWN distinct AD terminal evidence: the SAME
        # frozen identity (compared, never rebased), the exact-CID
        # teardown proof, the bound order
        ev_raw = json.loads(owner_evidence.read_bytes().decode("ascii"))
        flocal.validate_ad_owner_run_evidence(ev_raw)
        assert ev_raw["record"] == flocal.AD_OWNER_RUN_EVIDENCE_SCHEMA
        assert ev_raw["scope"] == flocal.AD_OWNER_RUN_SCOPE
        assert ev_raw["order"] == AD_ORDER_ID
        assert ev_raw["status"] == "pass"
        assert ev_raw["identity"] == identity
        assert ev_raw["teardown_proof"] == "exact-cid-membership"
        assert ev_raw["fixture_consumed_by"] == "unobserved"

        # the same frozen identity across EVERY retained layer of
        # the same attempt (no rebase anywhere in the composition)
        assert (
            prepared["identity"]
            == identity
            == snapshot["identity"]
            == ev_raw["identity"]
            == record_doc["identity"]
        )

        # ONE shared run context: the SAME frozen owner context, END
        # anchor and ledger across the whole lifecycle (compared,
        # never rebased or replaced)
        assert run.owner._owner_context is ctx_before
        assert run.owner.deadline.anchor == anchor_before
        assert run.owner.ledger is ledger_before
        # no global subject-UID scan ever ran on the owner-UID path
        # (the trap would have raised); the controller-UID scan kept
        # its closed historical semantics
        assert SUBJ_UID not in uid_calls
        assert CTL_UID in uid_calls


# -- the native-still-alive contrast (quiesce must measure it) ---------------------
def test_ad_finish_with_native_still_alive_refuses_closure_and_converges(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The native-still-alive contrast: the subject is left in
    the SAME world when finish is called — the in-image quiesce
    MEASURES the owned subject (a still-running subject cannot
    truthfully yield closure), the normal code refuses through
    the closed quiesce record law, the run converges terminal
    FAIL through exact-owned cleanup, and the unrelated
    same-UID worker survives with the SAME uid/gid/birth."""
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root)
    run, repo, fake, owner_evidence, control, uid_calls = _ad_run(
        tmp_path, monkeypatch, world=world, docker=fake
    )
    with _owned_run(run):
        binding = run.binding
        run_id = run.start()
        run.prepare()
        run.observe()
        world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
        run.record_stop()
        world.launch_native()
        expectation = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256=FAKE_BINARY,
            run_id=binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        channel = stp.FakeCidScopedTable(
            str(run.owner.target_cid), world.procs, exe_digest=FAKE_BINARY
        )
        run.register_subject(NAT_PID, expectation, channel=channel)
        worker_birth = world.procs[WORK_PID]["stat"].split()[21]

        # NO explicit native exit: the subject is STILL RUNNING
        assert world.subject is not None
        run.finish()
        # the quiesce was MEASURED, never canned: the owned subject
        # was still running, so closure could not truthfully be
        # claimed (the closed record law refuses it in the normal
        # code path)
        assert fake.last_quiesce is not None
        assert fake.last_quiesce["owned_subject_stopped"] is False
        # the run converged terminal FAIL (no pass, no readiness,
        # no native publication)
        assert run.owner.terminal_outcome == "fail"
        assert run.owner.failure_reason == "export-quiesce-state"
        _join_run(run)
        record = fb.read_admission_record(repo, AD_ORDER_ID)
        assert record["attempts"] == [{"head": HEAD, "run_id": run_id, "status": "fail"}]
        # the DISTINCT AD fail evidence (the SAME frozen identity —
        # compared, never rebased)
        ev_raw = json.loads(owner_evidence.read_bytes().decode("ascii"))
        flocal.validate_ad_owner_run_evidence(ev_raw)
        assert ev_raw["record"] == flocal.AD_OWNER_RUN_EVIDENCE_SCHEMA
        assert ev_raw["status"] == "fail"
        assert ev_raw["reason"] == "export-quiesce-state"
        assert ev_raw["identity"] == _ad_identity_dict()
        # the exact-owned cleanup removed the container and its
        # members from the coherent world; the unrelated same-UID
        # worker survives with the SAME uid/gid AND birth
        assert world.subject is None
        assert NAT_PID not in world.procs
        worker = world.procs[WORK_PID]
        assert fp.parse_proc_status(worker["status"]) == (SUBJ_UID, SUBJ_UID, ())
        assert worker["stat"].split()[21] == worker_birth
        # still no global subject-UID scan on the owner-UID path
        assert SUBJ_UID not in uid_calls


# -- the lifetime-frame contrasts (unknown / still-existing) ------------------------
def _drive_to_finish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, world: _ADWorld, fake: _ADFakeDocker
) -> tuple[Any, Any]:
    run, repo, _fake, _ev, _control, _uid = _ad_run(tmp_path, monkeypatch, world=world, docker=fake)
    try:
        run.start()
        run.prepare()
        run.observe()
        world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
        run.record_stop()
        world.launch_native()
        expectation = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256=FAKE_BINARY,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        channel = stp.FakeCidScopedTable(
            str(run.owner.target_cid), world.procs, exe_digest=FAKE_BINARY
        )
        run.register_subject(NAT_PID, expectation, channel=channel)
        world.exit_native()
        return run, repo
    except BaseException:
        _join_run(run)
        raise


def test_ad_unknown_lifetime_frame_refuses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A present-but-UNREADABLE post-removal frame is unknown,
    never a verified absence: the closed refusal converges the
    run terminal FAIL (never a fabricated zero)."""
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root, rm_stage="unreadable")
    run, repo = _drive_to_finish(tmp_path, monkeypatch, world, fake)
    with _owned_run(run):
        run.finish()
        assert run.owner.terminal_outcome == "fail"
        assert run.owner.failure_reason == "descendant-unverified"
        _join_run(run)
        record = fb.read_admission_record(repo, AD_ORDER_ID)
        assert record["attempts"][0]["status"] == "fail"
        assert fp.parse_proc_status(world.procs[WORK_PID]["status"]) == (SUBJ_UID, SUBJ_UID, ())


def test_ad_still_existing_lifetime_refuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A post-removal frame with the SAME birth AND uid is a
    real leftover (not reuse — only a changed birth proves
    recycle): the closed refusal converges terminal FAIL."""
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root, rm_stage="leftover")
    run, repo = _drive_to_finish(tmp_path, monkeypatch, world, fake)
    with _owned_run(run):
        run.finish()
        assert run.owner.terminal_outcome == "fail"
        assert run.owner.failure_reason == "descendant-leftover"
        _join_run(run)
        record = fb.read_admission_record(repo, AD_ORDER_ID)
        assert record["attempts"][0]["status"] == "fail"
        assert fp.parse_proc_status(world.procs[WORK_PID]["status"]) == (SUBJ_UID, SUBJ_UID, ())


# -- the default AD channel: THIS owner's CID and the SAME absolute END ------------
def test_ad_default_channel_binds_this_owner_cid_and_exact_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When the operator supplies NO channel, the composition
    selects the REAL AD factory bound to THIS owner's own
    registered CID and the SAME absolute owner END anchor (the
    cleanup grace is convergence, never fresh measurement); the
    returned channel registers the subject normally."""
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root)
    run, repo, _f, _ev, _c, _u = _ad_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        run.start()
        run.prepare()
        run.observe()
        world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
        run.record_stop()
        world.launch_native()
        expectation = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256=FAKE_BINARY,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        calls: list[tuple[str, float]] = []
        real_channel = stp.FakeCidScopedTable(
            str(run.owner.target_cid), world.procs, exe_digest=FAKE_BINARY
        )

        def factory(cid: str, end: float) -> Any:
            calls.append((cid, end))
            return real_channel

        monkeypatch.setattr(fno, "build_ad_native_channel", factory)
        end_before = run.owner.deadline.anchor
        snapshot = run.register_subject(NAT_PID, expectation)
        # the factory saw EXACTLY this owner's registered CID and
        # the SAME absolute owner END (no grace, no fresh window)
        assert calls == [(run.owner.target_cid, end_before)]
        assert snapshot["subject"]["uid"] == SUBJ_UID
        assert run.workflow.subject_receipt is not None


def test_ad_default_channel_expired_anchor_refuses_before_factory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Once the SAME absolute owner END has passed, the default
    selection refuses BEFORE any factory call — no refreshed
    measurement window, no factory, no registration."""
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root)
    run, _repo, _f, _ev, _c, _u = _ad_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        run.start()
        run.prepare()
        run.observe()
        world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
        run.record_stop()
        world.launch_native()
        expectation = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256=FAKE_BINARY,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        calls: list[tuple[str, float]] = []

        def factory(cid: str, end: float) -> Any:
            calls.append((cid, end))
            return stp.FakeCidScopedTable(cid, world.procs, exe_digest=FAKE_BINARY)

        monkeypatch.setattr(fno, "build_ad_native_channel", factory)
        # the owner's ONE absolute END has passed
        run.owner.deadline.anchor = time.monotonic() - 1.0
        with pytest.raises(fci.FixtureError, match="native-owner-patience"):
            run.register_subject(NAT_PID, expectation)
        assert calls == []
        # nothing committed
        assert run.workflow.subject_receipt is None


# -- the refused registration commits nothing ----------------------------------------
def test_ad_foreign_registration_refused_commits_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A caller's foreign expectation (foreign CID, or a
    matching-foreign binary) is refused BEFORE any staged
    commit; a later genuinely matching registration within the
    same still-valid measured phase still works."""
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root)
    run, _repo, _f, _ev, _c, _u = _ad_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        run.start()
        run.prepare()
        run.observe()
        world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
        run.record_stop()
        world.launch_native()
        foreign = fp.SubjectExpectation(
            cid="b" * 64,
            binary_sha256=FAKE_BINARY,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        with pytest.raises(fci.FixtureError, match="native-owner-subject-cid-mismatch"):
            run.register_subject(NAT_PID, foreign)
        wrong_binary = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256="f" * 64,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        with pytest.raises(fci.FixtureError, match="native-owner-subject-binary-mismatch"):
            run.register_subject(NAT_PID, wrong_binary)
        # NOTHING committed by the refusals
        assert run.workflow.subject_receipt is None
        # the same still-valid phase: the genuinely matching
        # registration now works
        expectation = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256=FAKE_BINARY,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        channel = stp.FakeCidScopedTable(
            str(run.owner.target_cid), world.procs, exe_digest=FAKE_BINARY
        )
        snapshot = run.register_subject(NAT_PID, expectation, channel=channel)
        assert snapshot["subject"]["uid"] == SUBJ_UID
        assert run.workflow.subject_receipt is not None
        # bounded reap: the held owner converges through its own
        # protected abort (the attempt stays recorded honestly)
        _join_run(run)
        assert run.owner.terminal_outcome == "aborted"


# -- the post-admission drift: compare at use, never rebase -----------------------
def test_ad_post_admission_drift_refuses_at_identity_use(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A drifted host identity after the run's admission is a
    closed refusal at the identity-bound use (the frozen
    context may be COMPARED at use, never rebased); the same
    won attempt converges terminal FAIL with the DISTINCT AD
    fail evidence carrying the FROZEN identity."""
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root)
    calls = {"n": 0}

    def drift_reader() -> tuple[int, int, int, int, int, int]:
        calls["n"] += 1
        if calls["n"] == 1:
            # the construction-time collection (frozen)
            return (SUBJ_UID, SUBJ_UID, SUBJ_UID, SUBJ_GID, SUBJ_GID, SUBJ_GID)
        # consistent, but a DIFFERENT identity at the later use
        return (1003, 1003, 1003, 1004, 1004, 1004)

    run, repo, _f, owner_evidence, _c, uid_calls = _ad_run(
        tmp_path, monkeypatch, world=world, docker=fake, reader=drift_reader
    )
    with _owned_run(run):
        run.start()
        with pytest.raises(fci.FixtureError, match="local-identity-drift"):
            run.prepare()
        _join_run(run)
        assert run.owner.terminal_outcome == "fail"
        assert run.owner.failure_reason == "local-identity-drift"
        # the frozen context was never rebased: the fail evidence
        # carries the FROZEN identity
        ev_raw = json.loads(owner_evidence.read_bytes().decode("ascii"))
        flocal.validate_ad_owner_run_evidence(ev_raw)
        assert ev_raw["record"] == flocal.AD_OWNER_RUN_EVIDENCE_SCHEMA
        assert ev_raw["status"] == "fail"
        assert ev_raw["reason"] == "local-identity-drift"
        assert ev_raw["identity"] == _ad_identity_dict()
        record = fb.read_admission_record(repo, AD_ORDER_ID)
        assert record["attempts"] == [
            {"head": HEAD, "run_id": run.binding.run_id, "status": "fail"}
        ]
        assert SUBJ_UID not in uid_calls


# -- the registration drift: revalidate the frozen context at the staged entry ----
def test_ad_registration_drift_refused_commits_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A host identity that drifts AFTER the successful public
    preparation (before the identity-bound staged registration)
    is a closed refusal at the registration itself: the FROZEN
    owner context is revalidated at this use site (compared,
    never rebased), the refused registration commits NOTHING
    (no receipt, no staged expectation), the frozen workflow
    subject law is unchanged, and the same won attempt
    converges honest ABORT with the same-order journal."""
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root)
    calls = {"n": 0}

    def drift_reader() -> tuple[int, int, int, int, int, int]:
        calls["n"] += 1
        if calls["n"] <= 2:
            # the construction-time collection and the prepare
            # revalidation: the FROZEN eligible identity
            return (SUBJ_UID, SUBJ_UID, SUBJ_UID, SUBJ_GID, SUBJ_GID, SUBJ_GID)
        # a consistent but DIFFERENT identity at the later
        # registration use: a drift fact, never re-frozen
        return (1003, 1003, 1003, 1004, 1004, 1004)

    run, repo, _f, _ev, _c, uid_calls = _ad_run(
        tmp_path, monkeypatch, world=world, docker=fake, reader=drift_reader
    )
    with _owned_run(run):
        run.start()
        prepared = run.prepare()
        assert prepared["record"] == fp.AD_NATIVE_PREP_SCHEMA
        assert prepared["identity"] == _ad_identity_dict()
        original_context = run.owner._owner_context
        run.observe()
        world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
        run.record_stop()
        world.launch_native()
        expectation = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256=FAKE_BINARY,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        channel = stp.FakeCidScopedTable(
            str(run.owner.target_cid), world.procs, exe_digest=FAKE_BINARY
        )
        with pytest.raises(fci.FixtureError, match="local-identity-drift"):
            run.register_subject(NAT_PID, expectation, channel=channel)
        # the refused registration commits NOTHING
        assert run.workflow.subject_receipt is None
        assert run.workflow._subject_pid is None
        assert run.workflow._expectation is None
        # the frozen workflow subject law is UNCHANGED
        assert run.workflow.subject_identity == (SUBJ_UID, SUBJ_GID, (SUBJ_GID,))
        # the frozen context was NEVER rebased
        assert run.owner._owner_context is original_context
        assert original_context.subject_uid == SUBJ_UID
        assert original_context.subject_gid == SUBJ_GID
        # the same won attempt converges honest ABORT
        _join_run(run)
        assert run.owner.terminal_outcome == "aborted"
        record = fb.read_admission_record(repo, AD_ORDER_ID)
        assert record["attempts"] == [
            {"head": HEAD, "run_id": run.binding.run_id, "status": "aborted"}
        ]
        # no global subject-UID scan on the owner-UID path
        assert SUBJ_UID not in uid_calls


def test_ad_finalize_refuses_foreign_identity_and_original_tag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The bound workflow's FINALIZE consumer stays coherent
    with the ORIGINAL frozen workflow context, derived from
    the passing public positive: a retained AD native-owner
    record carrying a VALID FOREIGN frozen identity (another
    owner's consistent triple) can never become ready, and a
    relabeled ORIGINAL-tag record cannot represent the
    AD-bound workflow (the exact tag-pair law); the unmutated
    retained record remains the ready positive control."""
    import copy

    run, _repo, _w, _f, _ev, record = _drive_to_published(tmp_path, monkeypatch)
    native_record = record["native_record"]
    with _owned_run(run):
        # positive control: the SAME retained record composes
        # a ready verdict against the SAME frozen context
        verdict = run.workflow.finalize(native_record)
        assert verdict.ready is True and verdict.reasons == ()
        # a VALID FOREIGN frozen identity (internally
        # consistent 1003:1004) is still foreign: the
        # workflow's ORIGINAL frozen subject law is compared,
        # never adopted
        foreign = copy.deepcopy(native_record)
        foreign["identity"] = fp._ad_identity_substructure_from_triple((1003, 1004, (1004,)))
        with pytest.raises(fci.FixtureError, match="prep-owner-identity-mismatch"):
            run.workflow.finalize(foreign)
        # a relabeled ORIGINAL-tag record (identity removed)
        # cannot represent the AD entry: the EXACT tag-pair
        # law refuses it at the closed record grammar BEFORE
        # any workflow composition (the AD binding requires
        # the DISTINCT identity-bearing tag)
        oldtag = copy.deepcopy(native_record)
        oldtag["record"] = fp.NATIVE_OWNER_SCHEMA
        oldtag.pop("identity")
        with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
            run.workflow.finalize(oldtag)
        # the DIRECT codec enforces the SAME exact tag-pair
        # law (the historical orders of the original tag are
        # unchanged)
        with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
            fp.parse_native_owner_facts(oldtag)
        historical = copy.deepcopy(oldtag)
        historical["order"] = "017-v"
        facts = fp.parse_native_owner_facts(historical)
        assert facts.schema == fp.NATIVE_OWNER_SCHEMA
        assert facts.identity is None
        assert facts.order == "017-v"
        # the AD form still parses under its own closed law
        ad_facts = fp.parse_native_owner_facts(native_record)
        assert ad_facts.schema == fp.AD_NATIVE_OWNER_SCHEMA
        assert ad_facts.identity == (SUBJ_UID, SUBJ_GID, (SUBJ_GID,))


# -- the frozen subject-identity construction law (pure data) ----------------------
def test_ad_frozen_subject_identity_construction_law() -> None:
    """The closed eligible-ID law of the frozen triple: strict
    finite non-root IDs distinct from the controller, and groups
    EXACTLY the one-element primary-GID vector (data
    validation, never measured authority)."""
    # valid
    assert fp._validate_frozen_subject_identity((1001, 1002, (1002,))) == (
        1001,
        1002,
        (1002,),
    )
    cases = [
        ((0, 1002, (1002,)), "prep-frozen-identity-root"),
        ((4294967295, 1002, (1002,)), "prep-frozen-identity-range"),
        ((1001, 0, (0,)), "prep-frozen-identity-root"),
        ((21001, 1002, (1002,)), "prep-frozen-identity-controller"),
        ((1001, 21001, (21001,)), "prep-frozen-identity-controller"),
        ((1001, 1002, ()), "prep-frozen-identity-groups"),
        ((1001, 1002, (1002, 1003)), "prep-frozen-identity-groups"),
        ((1001, 1002, (1003,)), "prep-frozen-identity-groups"),
        ((1001, 1002, 1002), "prep-frozen-identity-groups"),
        ((1001, 1002), "prep-frozen-identity-invalid"),
        (("1001", 1002, (1002,)), "prep-frozen-identity-invalid"),
        ((True, 1002, (1002,)), "prep-frozen-identity-invalid"),
        ((1001, 1002, (1002.0,)), "prep-frozen-identity-groups"),
    ]
    for triple, reason in cases:
        with pytest.raises(fci.FixtureError, match=reason):
            fp._validate_frozen_subject_identity(triple)


# -- the original/frozen identity laws are disjoint (pure collection) --------------
def test_ad_original_and_frozen_identity_laws_are_disjoint() -> None:
    """The ORIGINAL workflow (no frozen identity) keeps the
    fixed-21002 law byte-for-byte and refuses the owner-UID
    subject; the FROZEN AD law keeps its exact closed triple and
    refuses the fixed-21002 subject — including the equal-
    numeric cross-profile separation."""
    owner_procs = {
        60: stp.subject_proc(60, cgroup=stp.CID, uid=SUBJ_UID, gid=SUBJ_GID, groups=(SUBJ_GID,))
    }
    owner_table = stp.FakeTable(owner_procs)
    owner_channel = stp.FakeCidScopedTable(stp.CID, owner_procs, exe_digest=FAKE_BINARY)
    expectation = fp.SubjectExpectation(
        cid=stp.CID,
        binary_sha256=FAKE_BINARY,
        run_id=stp.RUN,
        min_start_time=400,
        expected_tty=stp.TTYS,
    )
    # the ORIGINAL law refuses the owner-UID subject
    with pytest.raises(fci.FixtureError, match="prep-uid-invalid"):
        fp.collect_subject_identity(owner_table, 60, expectation, channel=owner_channel)
    fixed_procs = {60: stp.subject_proc(60, cgroup=stp.CID)}
    fixed_table = stp.FakeTable(fixed_procs)
    fixed_channel = stp.FakeCidScopedTable(stp.CID, fixed_procs, exe_digest=FAKE_BINARY)
    # the ORIGINAL law keeps the fixed-21002 subject
    ident = fp.collect_subject_identity(fixed_table, 60, expectation, channel=fixed_channel)
    assert (ident.uid, ident.gid, ident.groups) == (21002, 21002, (21002,))
    # the FROZEN AD law refuses the fixed-21002 subject
    with pytest.raises(fci.FixtureError, match="prep-uid-invalid"):
        fp.collect_subject_identity(
            fixed_table,
            60,
            expectation,
            channel=fixed_channel,
            subject_identity=(SUBJ_UID, SUBJ_GID, (SUBJ_GID,)),
        )
    # the FROZEN AD law keeps its exact closed triple
    ident = fp.collect_subject_identity(
        owner_table,
        60,
        expectation,
        channel=owner_channel,
        subject_identity=(SUBJ_UID, SUBJ_GID, (SUBJ_GID,)),
    )
    assert (ident.uid, ident.gid, ident.groups) == (SUBJ_UID, SUBJ_GID, (SUBJ_GID,))


# -- the default AD channel factory's closed fields (pure) --------------------------
def test_ad_default_channel_factory_closed_fields() -> None:
    """The REAL AD factory binds the closed native-measurement
    bounds (exactly 320 MiB / 10 s per measurement) clamped to
    the SAME absolute owner END; an invalid END is a closed
    refusal before any channel exists."""
    end = time.monotonic() + 60.0
    ch = fno.build_ad_native_channel("a" * 64, end)
    assert isinstance(ch, fp.RealCidScopedTable)
    assert ch.cid == "a" * 64
    assert ch._max_exe_bytes == 335544320
    assert ch._exe_deadline == 10.0
    assert ch._exe_end == end
    for bad in (float("nan"), float("inf"), True, "10"):
        with pytest.raises(fci.FixtureError, match="native-owner-channel-budget-invalid"):
            fno.build_ad_native_channel("a" * 64, bad)


# -- the prepare-only finish is honestly NOT ready -----------------------------------
def _drive_to_prepared(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, world: _ADWorld, fake: _ADFakeDocker
) -> tuple[Any, Any]:
    run, repo, _f, _ev, _c, _u = _ad_run(tmp_path, monkeypatch, world=world, docker=fake)
    try:
        run.start()
        run.prepare()
        run.observe()
        return run, repo
    except BaseException:
        _join_run(run)
        raise


def test_ad_prepare_only_finish_is_honest_not_ready(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No stop recorded, no subject registered: the held
    instance finishes unconsumed and the DISTINCT AD terminal
    record is honestly NOT ready (it names what is missing; the
    identity is still the SAME frozen substructure)."""
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root)
    run, repo = _drive_to_prepared(tmp_path, monkeypatch, world, fake)
    with _owned_run(run):
        run.finish()
        assert run.owner.terminal_outcome == "pass"
        _join_run(run)
        native_out = tmp_path / "evidence" / "ad-native-run-record.json"
        record = run.publish_native(native_out)
        assert record["record"] == fno.AD_NATIVE_RUN_SCHEMA
        assert record["identity"] == _ad_identity_dict()
        assert record["owner_outcome"] == "pass"
        assert record["subject_measured"] is False
        assert record["stop_recorded"] is False
        assert record["native_record"] is None
        assert record["native_refusal"] is None
        assert record["verdict"]["ready"] is False
        assert record["verdict"]["reasons"], "an unready verdict names what is missing"
        for reason in record["verdict"]["reasons"]:
            assert reason in fp._VERDICT_REASONS
        fno.parse_native_run_record(record)
        assert native_out.exists()
        assert run.finalize_attempt() == "finalized"
        record_doc = fb.read_admission_record(repo, AD_ORDER_ID)
        assert record_doc["attempts"] == [
            {"head": HEAD, "run_id": run.binding.run_id, "status": "pass"}
        ]


# -- the one-shot publication: second publication / pre-existing destination ---------
def _drive_to_published(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Any, Any, _ADWorld, _ADFakeDocker, Any, dict[str, Any]]:
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root)
    run, repo, _f, owner_evidence, _c, _u = _ad_run(tmp_path, monkeypatch, world=world, docker=fake)
    try:
        run.start()
        run.prepare()
        run.observe()
        world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
        run.record_stop()
        world.launch_native()
        expectation = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256=FAKE_BINARY,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        channel = stp.FakeCidScopedTable(
            str(run.owner.target_cid), world.procs, exe_digest=FAKE_BINARY
        )
        run.register_subject(NAT_PID, expectation, channel=channel)
        world.exit_native()
        run.finish()
        assert run.owner.terminal_outcome == "pass"
        _join_run(run)
        world.procs[WORK_PID] = _worker_proc("S", tpgid=WORK_PID, start=WORK_START)
        native_out = tmp_path / "evidence" / "ad-native-run-record.json"
        record = run.publish_native(native_out)
        assert record["owner_outcome"] == "pass"
        return run, repo, world, fake, owner_evidence, record
    except BaseException:
        _join_run(run)
        raise


def test_ad_second_publication_refused_one_shot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The completed owner's publication is a ONE-SHOT terminal
    transition: a second publication on a fresh path is a
    closed refusal (no retry, no relabel), and the RETAINED
    record's closed cross-field law refuses a mutated copy
    (the outer and the nested identity are cross-bound to one
    frozen context — a derived copy with one field changed can
    never validate)."""
    run, repo, _w, _f, _ev, record = _drive_to_published(tmp_path, monkeypatch)
    with _owned_run(run):
        with pytest.raises(fci.FixtureError, match="native-owner-published"):
            run.publish_native(tmp_path / "evidence" / "second.json")
        assert not (tmp_path / "evidence" / "second.json").exists()
        # the RETAINED record validates (the production bytes)
        fno.parse_native_run_record(record)
        # OUTER identity mutated (internally consistent, foreign):
        # the cross-bound nested identity can no longer agree
        import copy

        mutated = copy.deepcopy(record)
        mutated["identity"] = fp._ad_identity_substructure_from_triple((1003, 1004, (1004,)))
        with pytest.raises(fci.FixtureError, match="native-owner-record-malformed"):
            fno.parse_native_run_record(mutated)
        # NESTED identity mutated (internally consistent, foreign)
        mutated = copy.deepcopy(record)
        mutated["native_record"]["identity"] = fp._ad_identity_substructure_from_triple(
            (1003, 1004, (1004,))
        )
        with pytest.raises(fci.FixtureError, match="native-owner-record-malformed"):
            fno.parse_native_run_record(mutated)


def test_ad_preexisting_native_destination_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pre-existing foreign native destination is a closed
    refusal (fail-if-exists): the attempt terminalizes
    honestly, the foreign bytes are preserved untouched, and no
    fresh-path retry is ever made."""
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root)
    run, repo, _f, _ev, _c, _u = _ad_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        run.start()
        run.prepare()
        run.observe()
        world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
        run.record_stop()
        world.launch_native()
        expectation = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256=FAKE_BINARY,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        channel = stp.FakeCidScopedTable(
            str(run.owner.target_cid), world.procs, exe_digest=FAKE_BINARY
        )
        run.register_subject(NAT_PID, expectation, channel=channel)
        world.exit_native()
        run.finish()
        assert run.owner.terminal_outcome == "pass"
        _join_run(run)
        native_out = tmp_path / "evidence" / "ad-native-run-record.json"
        native_out.parent.mkdir(parents=True, exist_ok=True)
        native_out.write_bytes(b"foreign bytes\n")
        with pytest.raises(fci.FixtureError, match="native-owner-evidence-exists"):
            run.publish_native(native_out)
        # the foreign bytes are preserved untouched
        assert native_out.read_bytes() == b"foreign bytes\n"
        # the same won attempt was terminalized honestly (fail)
        record = fb.read_admission_record(repo, AD_ORDER_ID)
        assert record["attempts"] == [
            {"head": HEAD, "run_id": run.binding.run_id, "status": "fail"}
        ]


# -- the pre-admission law: AD refused under AC-active ---------------------------
def test_ad_refused_under_ac_active_before_admission(tmp_path: Path) -> None:
    """The actual repository-context validation refuses 017-ad
    under AC-active BEFORE any admission or external work, proven
    only in an owned synthetic repository (the real checkout is
    never touched)."""
    repo = _ad_repo(tmp_path / "repo", active_order=AC_ORDER_ID)
    git = _ad_git_runner(repo, active_order=AC_ORDER_ID)
    with pytest.raises(fci.FixtureError, match="bind-active-mismatch"):
        fb.resolve_order_binding(repo, AD_ORDER_ID, HEAD, git_runner=git)
    # no admission namespace, no journal, no external work
    assert not (repo / "oap" / "admissions" / AD_ORDER_ID).exists()
    # the AC binding itself still resolves (the active entry)
    ac_binding = fb.resolve_order_binding(repo, AC_ORDER_ID, HEAD, git_runner=git)
    assert ac_binding.order_id == AC_ORDER_ID


# -- the uncollected identity: a closed refusal before any mutation ---------------
def test_ad_uncollected_identity_refuses_and_closes_same_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def failing_reader() -> tuple[int, int, int, int, int, int]:
        raise OSError("raw read seam failure")

    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root)
    # the constructor failure AFTER winning the admission closes
    # THAT SAME run honestly (a terminal fail record — never an
    # orphan running claim); no fixture work happened at all
    with pytest.raises(fci.FixtureError, match="local-identity-id-getter-failure"):
        _ad_run(tmp_path, monkeypatch, world=world, docker=fake, reader=failing_reader)
    repo = tmp_path / "repo"
    record = fb.read_admission_record(repo, AD_ORDER_ID)
    attempts = record["attempts"]
    assert len(attempts) == 1
    assert attempts[0]["head"] == HEAD
    assert attempts[0]["status"] == "fail"
    assert fake.calls == []


def test_ad_mismatched_owner_triple_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Independent real/effective/saved values that DISAGREE never
    collect (the eligible-ID law, closed at the production
    collector)."""

    def mismatched_reader() -> tuple[int, int, int, int, int, int]:
        return (SUBJ_UID, SUBJ_UID + 1, SUBJ_UID, SUBJ_GID, SUBJ_GID, SUBJ_GID)

    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root)
    with pytest.raises(fci.FixtureError, match="local-identity-uid-triple-mismatch"):
        _ad_run(tmp_path, monkeypatch, world=world, docker=fake, reader=mismatched_reader)


# -- the future 017-af entry: owner-UID selection, inert under AE-active -----------
def test_ae_af_entry_selection_and_preserved_closed_mapping() -> None:
    """The canonical FUTURE 017-af native-PTY qualification entry
    selects the SAME owner-UID profile through the closed entry
    mapping (carrying the new producer through the existing
    owner composition), and every EXISTING entry, path and tag
    is preserved byte-for-byte (017-ad stays closed and
    unchanged — no new AD record form is minted)."""
    # the exact canonical AF constants
    assert frp.AF_ORDER_ID == "017-af"
    assert frp.AF_ORDER_PATH == "oap/orders/017-af-owner-uid-native-pty-qualification.md"
    assert frp.AF_OWNER_STATE_SCHEMA == "slaif-017af-owner-state-v1"
    assert frp.AF_NATIVE_RUN_EVIDENCE_SCHEMA == "slaif-017af-native-owner-run-evidence-v1"
    assert frp.AF_NATIVE_RUN_SCHEMA == "slaif-017af-native-owner-run-v1"
    assert frp.AF_OWNER_RUN_SCOPE == "slaif-017af-owner-uid-scope"
    assert frp.AF_NATIVE_ATTACH_BINDING_SCHEMA == "slaif-017af-native-attach-binding-v1"
    # the closed entry mapping: the EXISTING entries
    # preserved byte-for-byte (the sealed FUTURE 017-ah
    # requalification entry added by the 017-ag order is
    # included in the current closed law — its own test
    # re-asserts every preserved constant), each owner-UID
    # entry selecting the SAME owner-UID profile
    assert dict(frp.ENTRY_PROFILES) == {
        "017-s": frp.PROFILE_ORIGINAL,
        "017-x": frp.PROFILE_ORIGINAL,
        "017-y": frp.PROFILE_ORIGINAL,
        frp.AB_ORDER_ID: frp.PROFILE_OWNER_UID,
        frp.AD_ORDER_ID: frp.PROFILE_OWNER_UID,
        frp.AF_ORDER_ID: frp.PROFILE_OWNER_UID,
        frp.AH_ORDER_ID: frp.PROFILE_OWNER_UID,
    }
    assert frp.entry_profile_name("017-s") == frp.PROFILE_ORIGINAL
    assert frp.entry_profile_name("017-x") == frp.PROFILE_ORIGINAL
    assert frp.entry_profile_name("017-y") == frp.PROFILE_ORIGINAL
    assert frp.entry_profile_name(frp.AB_ORDER_ID) == frp.PROFILE_OWNER_UID
    assert frp.entry_profile_name(AD_ORDER_ID) == frp.PROFILE_OWNER_UID
    # AF carries the owner-UID profile (the production
    # derivation, never a caller-authored view)
    assert frp.entry_profile_name(frp.AF_ORDER_ID) == frp.PROFILE_OWNER_UID
    view = frp.entry_runtime_profile(frp.AF_ORDER_ID, _ad_description())
    assert (view.subject_uid, view.subject_gid) == (SUBJ_UID, SUBJ_GID)
    assert view.exec_user == f"{SUBJ_UID}:{SUBJ_GID}"
    # unknown entries still refuse (AF is a known entry, not a
    # wildcard: nothing else is selectable)
    with pytest.raises(frp.ProfileError, match="profile-entry-unknown"):
        frp.entry_profile_name("017-ae")
    with pytest.raises(frp.ProfileError, match="profile-entry-unknown"):
        frp.entry_profile_name("017-zz")
    # every EXISTING canonical constant/tag preserved byte-for-byte
    assert frp.AB_ORDER_ID == "017-ab"
    assert frp.AB_ORDER_PATH == "oap/orders/017-ab-owner-uid-python-capability-qualification.md"
    assert frp.AB_DRIVER_RECORD == "slaif-017ab-owner-uid-exec-capability-v1"
    assert frp.AB_OWNER_RUN_EVIDENCE_SCHEMA == "slaif-017ab-owner-run-evidence-v1"
    assert frp.AB_OWNER_RUN_SCOPE == "slaif-017ab-owner-uid-scope"
    assert frp.AD_ORDER_ID == "017-ad"
    assert frp.AD_ORDER_PATH == "oap/orders/017-ad-owner-uid-native-handoff-qualification.md"
    assert frp.AD_DRIVER_RECORD == "slaif-017ad-owner-uid-native-handoff-v1"
    assert frp.AD_OWNER_STATE_SCHEMA == "slaif-017ad-owner-state-v1"
    assert frp.AD_NATIVE_RUN_EVIDENCE_SCHEMA == "slaif-017ad-native-owner-run-evidence-v1"
    assert frp.AD_NATIVE_RUN_SCHEMA == "slaif-017ad-native-owner-run-v1"
    assert frp.AD_OWNER_RUN_SCOPE == "slaif-017ad-owner-uid-scope"
    assert frp.AD_EXE_MAX_BYTES == 335544320
    assert frp.AD_EXE_DEADLINE_SECONDS == 10.0
    assert not hasattr(frp, "AD_NATIVE_ATTACH_BINDING_SCHEMA")


def test_ae_af_refused_under_ae_active_before_admission(tmp_path: Path) -> None:
    """The REAL repository-context validation refuses 017-af
    under AE-active BEFORE any admission or external work,
    proven only in an owned synthetic repository (the real
    checkout is never touched): the closed canonical map carries
    the AF entry's unique committed order path, the active-
    content law refuses the foreign-active AF binding, and the
    AF admission namespace is never claimed."""
    # coherence: the binding module's closed map mirrors the
    # canonical entry names owned by the runtime-profile module
    assert fb._CANONICAL_ORDER_PATHS[AF_ORDER_ID] == frp.AF_ORDER_PATH
    # the AE-active synthetic repo: the AF order file is
    # committed at its canonical path, active selects AE
    repo = _af_repo(tmp_path / "repo", active_order=AE_ORDER_ID)
    git = _af_git_runner(repo, active_order=AE_ORDER_ID)
    with pytest.raises(fci.FixtureError, match="bind-active-mismatch"):
        fb.resolve_order_binding(repo, AF_ORDER_ID, HEAD, git_runner=git)
    # no admission namespace, no journal, no external work
    assert not (repo / "oap" / "admissions" / AF_ORDER_ID).exists()
    # the AE binding itself still resolves (the active entry)
    ae_binding = fb.resolve_order_binding(repo, AE_ORDER_ID, HEAD, git_runner=git)
    assert ae_binding.order_id == AE_ORDER_ID
    # the AF entry under ITS OWN active context resolves ONLY at
    # its unique canonical committed order path
    af_repo = _af_repo(tmp_path / "afrepo")
    af_git = _af_git_runner(af_repo)
    af_binding = fb.resolve_order_binding(af_repo, AF_ORDER_ID, HEAD, git_runner=af_git)
    assert af_binding.order_path == frp.AF_ORDER_PATH
    # a FOREIGN pattern-matching AF name is a closed refusal
    # BEFORE any admission or owner adoption
    wrong = tmp_path / "wrong" / "repo"
    wrong.parent.mkdir(parents=True)
    wrong_repo = Path(stl._make_local_repo(wrong))
    wrong_name = "017-af-other-synthetic-name.md"
    (wrong_repo / "oap" / "orders" / wrong_name).write_bytes(AF_ORDER_BYTES)
    (wrong_repo / "oap" / "active").write_bytes(AF_ORDER_ID.encode("ascii") + b"\n")

    def wrong_git(args: list[str], cwd: Path) -> bytes:
        if args == ["rev-parse", "HEAD"]:
            return str(HEAD).encode("ascii")
        if args == ["status", "--porcelain"]:
            return b""
        if args == ["remote", "get-url", "origin"]:
            return b"https://github.com/ulfe-lmi/slaif-local-coding.git\n"
        if args == ["ls-tree", "--name-only", f"{HEAD}:oap/orders"]:
            return (S_ORDER_NAME + "\n" + wrong_name + "\n").encode("ascii")
        if args == ["show", f"{HEAD}:oap/active"]:
            return AF_ORDER_ID.encode("ascii") + b"\n"
        if args == ["show", f"{HEAD}:oap/orders/{wrong_name}"]:
            return AF_ORDER_BYTES
        if args == ["show", f"{HEAD}:oap/orders/{S_ORDER_NAME}"]:
            return bytes(stl.ORDER_PATH.read_bytes())
        raise AssertionError(f"unexpected git args: {args}")

    with pytest.raises(fci.FixtureError, match="bind-order-path-mismatch"):
        fb.resolve_order_binding(wrong_repo, AF_ORDER_ID, HEAD, git_runner=wrong_git)
    assert not (wrong_repo / "oap" / "admissions" / AF_ORDER_ID).exists()


# -- the fixed canonical entry: the UNIQUE committed order path -------------------
def test_canonical_entry_path_law(tmp_path: Path) -> None:
    """The fixed canonical future entry resolves ONLY at its own
    unique committed order path (the generic original orders
    stay exactly pattern-generic)."""
    # coherence: the binding module's closed map mirrors the
    # canonical entry names owned by the runtime-profile module
    assert fb._CANONICAL_ORDER_PATHS[AD_ORDER_ID] == frp.AD_ORDER_PATH
    assert fb._CANONICAL_ORDER_PATHS["017-ab"] == frp.AB_ORDER_PATH

    # the canonical AD entry resolves at its own committed path
    repo = _ad_repo(tmp_path / "repo")
    git = _ad_git_runner(repo)
    binding = fb.resolve_order_binding(repo, AD_ORDER_ID, HEAD, git_runner=git)
    assert binding.order_path == frp.AD_ORDER_PATH

    # a FOREIGN pattern-matching name under AD-active is a
    # closed refusal BEFORE any admission or owner adoption
    wrong = tmp_path / "wrong" / "repo"
    wrong.parent.mkdir(parents=True)
    wrong_repo = Path(stl._make_local_repo(wrong))
    wrong_name = "017-ad-other-synthetic-name.md"
    (wrong_repo / "oap" / "orders" / wrong_name).write_bytes(AD_ORDER_BYTES)
    (wrong_repo / "oap" / "active").write_bytes(AD_ORDER_ID.encode("ascii") + b"\n")

    def wrong_git(args: list[str], cwd: Path) -> bytes:
        head = str(HEAD)
        if args == ["rev-parse", "HEAD"]:
            return head.encode("ascii")
        if args == ["status", "--porcelain"]:
            return b""
        if args == ["remote", "get-url", "origin"]:
            return b"https://github.com/ulfe-lmi/slaif-local-coding.git\n"
        if args == ["ls-tree", "--name-only", f"{HEAD}:oap/orders"]:
            return (S_ORDER_NAME + "\n" + wrong_name + "\n").encode("ascii")
        if args == ["show", f"{HEAD}:oap/active"]:
            return AD_ORDER_ID.encode("ascii") + b"\n"
        if args == ["show", f"{HEAD}:oap/orders/{wrong_name}"]:
            return AD_ORDER_BYTES
        if args == ["show", f"{HEAD}:oap/orders/{S_ORDER_NAME}"]:
            return bytes(stl.ORDER_PATH.read_bytes())
        raise AssertionError(f"unexpected git args: {args}")

    with pytest.raises(fci.FixtureError, match="bind-order-path-mismatch"):
        fb.resolve_order_binding(wrong_repo, AD_ORDER_ID, HEAD, git_runner=wrong_git)
    # no admission namespace was ever claimed
    assert not (wrong_repo / "oap" / "admissions" / AD_ORDER_ID).exists()


def test_ad_foreign_path_binding_refused_before_admission(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A directly-constructed binding carrying the AD order id at
    a FOREIGN path is refused before the admission or the owner
    adoption (the composition's closed defense; the resolver law
    above covers the resolved path)."""
    repo = _ad_repo(tmp_path / "repo")
    binding = fb.OrderRunBinding(
        order_id=AD_ORDER_ID,
        order_path="oap/orders/017-ad-other-synthetic-name.md",
        order_sha256="e" * 64,
        active_bytes=AD_ORDER_ID.encode("ascii") + b"\n",
        source_head=HEAD,
        repo_identity="ulfe-lmi/slaif-local-coding",
        run_id=stp.RUN,
    )
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _ADWorld(proc_root)
    fake = _ADFakeDocker(world, proc_root)
    uid_calls: list[int] = []
    _hermetic(tmp_path, monkeypatch, fake, tmp_path / "control", uid_calls)
    with pytest.raises(fci.FixtureError, match="native-owner-order-path-mismatch"):
        fno.NativeOwnerRun(
            binding,
            repo,
            tmp_path / "work",
            tmp_path / "evidence" / "ad-owner-evidence.json",
            tmp_path / "control",
            git_runner=_ad_git_runner(repo),
            executor=fake,
            table=stp.FakeTable(world.procs),
            worker_pid=WORK_PID,
            bash_pid=BASH_PID,
            tty_foreground_pgrp=WORK_PID,
            identity_reader=_ad_reader,
            proc_root=proc_root,
        )
    assert not (repo / "oap" / "admissions" / AD_ORDER_ID).exists()
    assert fake.calls == []


def test_ad_record_consumers_refuse_foreign_path() -> None:
    """The identity-bearing AD record forms are bound to the
    canonical entry's OWN committed order path: a foreign path
    in the retained binding record is a closed refusal in both
    the prep-snapshot consumer and the terminal-run consumer."""
    ad_binding = {
        "record": fb.BINDING_RECORD_SCHEMA,
        "order_id": AD_ORDER_ID,
        "order_path": frp.AD_ORDER_PATH,
        "order_sha256": "e" * 64,
        "active_sha256": "f" * 64,
        "source_head": HEAD,
        "repo_identity": "ulfe-lmi/slaif-local-coding",
        "run_id": stp.RUN,
    }
    snapshot = {
        "record": fp.AD_NATIVE_PREP_SCHEMA,
        "binding": dict(ad_binding),
        "group": {
            "worker": {
                "pid": 50,
                "state": "S",
                "pgrp": 50,
                "session": 50,
                "tty": 8,
                "start_time": 500,
            },
            "bash": {
                "pid": 40,
                "state": "S",
                "pgrp": 40,
                "session": 40,
                "tty": 8,
                "start_time": 100,
            },
            "same_job": True,
            "same_tty": True,
            "foreground_pgrp": 50,
            "members": [],
            "session_other_groups": [],
            "tool_sessions": [],
        },
        "subject": None,
        "identity": _ad_identity_dict(),
    }
    fp.validate_prep_snapshot(snapshot)
    snapshot["binding"] = dict(ad_binding, order_path="oap/orders/017-ad-other-synthetic-name.md")
    with pytest.raises(fci.FixtureError, match="prep-record-malformed"):
        fp.validate_prep_snapshot(snapshot)

    terminal = {
        "record": fno.AD_NATIVE_RUN_SCHEMA,
        "scope": fno.NATIVE_RUN_SCOPE,
        "binding": dict(ad_binding),
        "owner_outcome": "pass",
        "attempt": "running",
        "subject_measured": False,
        "stop_recorded": False,
        "native_record": None,
        "native_refusal": None,
        "verdict": {
            "ready": False,
            "reasons": ["no-native-identity", "worker-stop-unmeasured"],
        },
        "identity": _ad_identity_dict(),
    }
    fno.parse_native_run_record(terminal)
    terminal["binding"] = dict(ad_binding, order_path="oap/orders/017-ad-other-synthetic-name.md")
    with pytest.raises(fci.FixtureError, match="native-owner-record-malformed"):
        fno.parse_native_run_record(terminal)


# -- the AF coupled attach-binding lifecycle (017-ae software) -----------------
# The canonical FUTURE 017-af entry exercised HERE as inert software
# ONLY: the ACTUAL public composition over ONE coherent coupled fake
# process world carrying the fixture-namespace devpts model (the
# measured namespace root, the measured policy fact, the closed
# slave-row vector) and the per-subject metadata seam.  NO actual
# Docker/native/PTY operation; fake proof is software integration —
# never sealed-real-owner, native or host readiness, and the AF
# entry stays INERT and unqualified in this round.

AF_DEVPTS_NS = (9, 42)  # the fixture devpts mount root (st_dev, st_ino)
AF_DEVPTS_POLICY = (5, 0o620)  # the measured node GID / node MODE
AF_ALLOC = (136, 1, 77, 0o620, SUBJ_UID, 5)  # major, minor, inode, mode, uid, gid
AF_TTY_NR = 34817  # new_encode_dev(136, 1) — the derived expected tty_nr


class _AFWorld(_ADWorld):
    """The AF coherent world: the AD canonical PID map plus the
    fixture-namespace devpts model observed by BOTH the probe
    records and the per-subject channel metadata (ONE model —
    the operator's explicit launch event allocates the owned
    slave in the SAME measured namespace)."""

    def __init__(self, proc_root: Path) -> None:
        super().__init__(proc_root)
        self.devpts_rows: dict[int, tuple[int, int, int, int, int, int]] = {}
        self.devpts_allocations = 0
        self.devpts_probe_calls = 0
        # the MEASURED probe uid the record reports (the
        # frozen subject uid by default; a test may report a
        # foreign measured uid to exercise the owner's
        # measurement-boundary binding)
        self.devpts_probe_uid: int = SUBJ_UID

    def _devpts_record(self) -> bytes:
        # the row name is the CANONICAL decimal string (the
        # closed row grammar: str, ascii, isdigit, no leading
        # zeros) — equal to the minor
        rows = [
            [str(name), major, minor, ino, mode, uid, gid]
            for name, (major, minor, ino, mode, uid, gid) in sorted(self.devpts_rows.items())
        ]
        obj = {
            "record": "slaif-017ae-devpts-inventory-v1",
            "status": "pass",
            "uid": self.devpts_probe_uid,
            "namespace": list(AF_DEVPTS_NS),
            "policy": {
                "fstype": "devpts",
                "gid": AF_DEVPTS_POLICY[0],
                "mode": AF_DEVPTS_POLICY[1],
            },
            "isolation": {"site": False, "startup": False},
            "slave_rows": rows,
        }
        return json.dumps(obj, separators=(",", ":")).encode("ascii") + b"\n"

    def launch_native(self) -> None:
        """The operator's explicit native launch: the SAME
        canonical map projection as AD plus the fixture devpts
        ALLOCATION event (one fresh owned slave 136:1 with a
        fresh inode, owned by the subject UID, node GID as
        MEASURED — never assumed equal to the process GID) and
        the per-subject metadata (the FULL measured mode, the
        subject's own mount view)."""
        super().launch_native()
        assert self.devpts_allocations == 0, "one allocation per world"
        self.devpts_allocations += 1
        major, minor, ino, mode, uid, gid = AF_ALLOC
        self.devpts_rows[minor] = (major, minor, ino, mode, uid, gid)
        self.procs[NAT_PID]["devpts_slave"] = {
            "root_dev": AF_DEVPTS_NS[0],
            "root_ino": AF_DEVPTS_NS[1],
            "slave_dev": AF_DEVPTS_NS[0],
            "slave_ino": ino,
            "slave_mode": stat.S_IFCHR | mode,  # the FULL measured mode
            "slave_uid": uid,
            "slave_gid": gid,
            "major": major,
            "minor": minor,
        }


class _AFFakeDocker(_ADFakeDocker):
    """The AF probe surface over the SAME world: the ONE exact
    NON-PTY devpts probe argv (the frozen subject user, the
    registered CID, ``python3 -I -S -c`` with the immutable
    probe body) returns the world's measured inventory record
    (a closed single-line ASCII record with a complete
    capture); every other form keeps the AD/AA scripted
    behavior byte-for-byte."""

    def __call__(self, argv: list[str], timeout: float) -> Any:
        if (
            len(argv) == 10
            and argv[:3] == ["docker", "exec", "--user"]
            and argv[3] == f"{SUBJ_UID}:{SUBJ_GID}"
            and argv[5:9] == ["python3", "-I", "-S", "-c"]
            and argv[9] == fci.DEVPTS_PROBE
        ):
            # The probed CID must be the SAME world's OWN
            # registered CID, and the target container must be
            # live/prepared (created, the controller frame
            # attached and present in the synthetic proc
            # view): the measured inventory is NEVER returned
            # for a foreign, unknown or unprepared target
            if (
                self._world.cid is None
                or self._world.controller is None
                or argv[4] != self._world.cid
                or not (self.proc_root / str(CTL_PID)).is_dir()
            ):
                return self._result(125, b"exec-refused\n")
            self._world.devpts_probe_calls += 1
            return self._result(0, self._world._devpts_record())
        return super().__call__(argv, timeout)


def _af_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    world: _AFWorld,
    docker: _AFFakeDocker,
) -> tuple[Any, Any, _AFFakeDocker, Path, Path, list[int]]:
    repo = _af_repo(tmp_path)
    work = tmp_path / "work"
    control = tmp_path / "control"
    owner_evidence = tmp_path / "evidence" / "af-owner-evidence.json"
    uid_calls: list[int] = []
    _hermetic(tmp_path, monkeypatch, docker, control, uid_calls)
    git = _af_git_runner(repo)
    table = stp.FakeTable(world.procs)
    binding = fb.resolve_order_binding(repo, AF_ORDER_ID, HEAD, git_runner=git)
    run = fno.NativeOwnerRun(
        binding,
        repo,
        work,
        owner_evidence,
        control,
        git_runner=git,
        executor=docker,
        table=table,
        worker_pid=WORK_PID,
        bash_pid=BASH_PID,
        tty_foreground_pgrp=WORK_PID,
        identity_reader=_ad_reader,
        # the owner's EXISTING narrow proc seam: the coherent
        # world's synthetic-proc projection
        proc_root=world.proc_root,
    )
    return run, repo, docker, owner_evidence, control, uid_calls


def _af_prep(run: Any, world: _AFWorld) -> dict[str, object]:
    """The shared AF attach phase: start/prepare/observe, the
    separately measured stop, the ONE-SHOT EMPTY baseline, the
    operator's explicit native launch (the allocation) and the
    derived expectation — the receipt frozen BEFORE any
    registration (two bounded probes, no more)."""
    run.start()
    run.prepare()
    run.observe()
    world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
    run.record_stop()
    baseline = run.collect_attach_baseline()
    assert baseline.inventory.slave_rows == ()
    assert world.devpts_probe_calls == 1
    world.launch_native()
    receipt: dict[str, object] = run.derive_attach_expectation()
    assert world.devpts_probe_calls == 2
    assert receipt["expected_tty_nr"] == AF_TTY_NR
    assert receipt["namespace"] == list(AF_DEVPTS_NS)
    return receipt


def _af_expectation(run: Any, *, expected_tty: int = AF_TTY_NR) -> Any:
    return fp.SubjectExpectation(
        cid=str(run.owner.target_cid),
        binary_sha256=FAKE_BINARY,
        run_id=run.binding.run_id,
        min_start_time=400,
        expected_tty=expected_tty,
    )


def _af_channel_factory(world: _AFWorld, calls: list[tuple[Any, float]]) -> Any:
    def factory(cid: Any, end: float) -> Any:
        calls.append((cid, end))
        return stp.FakeCidScopedTable(cid, world.procs, exe_digest=FAKE_BINARY)

    return factory


def _af_new_world(tmp_path: Path) -> tuple[_AFWorld, _AFFakeDocker]:
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    world = _AFWorld(proc_root)
    return world, _AFFakeDocker(world, proc_root)


def _racy_channel_class(mutate: Any) -> Any:
    """A scripted registered-CID channel whose executable
    re-measurement runs a world mutation (the race point):
    ``mutate(channel, pid, birth)`` between the blocking read
    and its result."""

    class _RacyChannel(stp.FakeCidScopedTable):  # type: ignore[name-defined,misc]
        def __init__(self, cid: str, procs: dict[str, Any], *, world: _AFWorld, **kw: Any) -> None:
            super().__init__(cid, procs, **kw)
            self._world = world
            self._exe_calls = 0

        def exe_sha256(self, pid: int, birth: int) -> Any:
            self._exe_calls += 1
            if self._exe_calls == 2:  # the FINAL-frame re-measurement
                mutate(self, pid, birth)
            return super().exe_sha256(pid, birth)

    _RacyChannel.__name__ = "RacyChannelFor" + mutate.__name__
    return _RacyChannel


def test_af_full_public_native_lifecycle_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The useful 1001:1002 positive through the REAL public
    composition for the AF entry (constructor/admission/
    prepare/stop/baseline/launch/derive/register/exit/
    finish/restore/publish/finalize) over ONE coherent
    coupled fake process world with the fixture devpts
    model: the AF's OWN default exact-CID channel (the
    factory sees the registered CID and the SAME absolute
    owner END — no grace, no fresh window), the expectation
    bound to the DERIVED tty (never the subject's own), the
    measured namespace/device frames at the
    collect-before-commit boundary, and the protected AF
    owner/native/attach terminal records with the SAME
    frozen identity carried through every retained layer.
    The unrelated same-UID worker survives the exact-CID
    world."""
    world, fake = _af_new_world(tmp_path)
    run, repo, _f, owner_evidence, _c, uid_calls = _af_run(
        tmp_path, monkeypatch, world=world, docker=fake
    )
    with _owned_run(run):
        binding = run.binding
        identity = _ad_identity_dict()
        native_out = tmp_path / "evidence" / "af-native-run-record.json"
        proc_root = world.proc_root
        # the ONE shared run context across the whole lifecycle
        ctx_before = run.owner._owner_context
        anchor_before = run.owner.deadline.anchor
        ledger_before = run.owner.ledger
        worker_birth = world.procs[WORK_PID]["stat"].split()[21]

        # start/prepare/observe/stop/baseline/launch/derive
        _af_prep(run, world)
        calls: list[tuple[Any, float]] = []
        monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, calls))
        end_before = run.owner.deadline.anchor
        snapshot = run.register_subject(NAT_PID, _af_expectation(run))
        # the factory saw EXACTLY this owner's registered CID
        # and the SAME absolute owner END
        assert calls == [(run.owner.target_cid, end_before)]
        # the measured subject frame: the owned allocation's
        # derived tty_nr, bound by the collector's OWN pty
        assert snapshot["subject"]["tty"] == AF_TTY_NR
        assert snapshot["subject"]["pty_matched"] is True
        assert snapshot["subject"]["cid_membership"] == "cid-scoped"
        assert run.workflow.subject_receipt is not None
        # the DISTINCT AF tag at the retained prep layer (the
        # SAME frozen identity carried through)
        assert snapshot["record"] == fp.AF_NATIVE_PREP_SCHEMA
        assert snapshot["identity"]["subject_uid"] == SUBJ_UID
        # the attach phase used EXACTLY two bounded probes
        # (the empty baseline + the allocation observation);
        # a later observe reuses the retained receipt and
        # never re-measures
        assert world.devpts_probe_calls == 2
        run.observe()
        assert world.devpts_probe_calls == 2

        # the EXPLICIT fake native exit before the positive
        # finish: absence only (no exit code or cause); the
        # retained receipt stays history, never re-measured
        world.exit_native()
        assert world.native_exits == 1
        assert NAT_PID not in world.procs
        assert not (proc_root / str(NAT_PID)).exists()
        assert run.workflow.subject_receipt is not None

        # finish: the REAL finish/export/teardown over the
        # fake platform — the in-image quiesce MEASURES zero
        # subjects (the exit happened; a still-running
        # subject could never truthfully yield closure), the
        # exact-CID removal removes the controller member,
        # and the post-removal parser verifies ENOENT
        # (verified-gone, tri-stated)
        run.finish()
        assert run.owner.terminal_outcome == "pass"
        _join_run(run)
        assert fake.last_quiesce is not None
        assert fake.last_quiesce["owned_subject_stopped"] is True
        assert run.owner.owned_members_before == ((CTL_PID, CTL_START, CTL_UID),)
        assert run.owner.owned_members_after == ((CTL_PID, "verified-gone"),)
        # the unrelated same-UID worker survived the whole run
        # with the SAME uid/gid AND the SAME birth
        worker = world.procs[WORK_PID]
        assert fp.parse_proc_status(worker["status"]) == (SUBJ_UID, SUBJ_UID, ())
        assert worker["stat"].split()[21] == worker_birth

        # the operator restores the SAME worker job (stat-only)
        world.procs[WORK_PID] = _worker_proc("S", tpgid=WORK_PID, start=WORK_START)

        # publish: the DISTINCT identity-bearing AF terminal
        # record (owner evidence FIRST, native record SECOND,
        # the nested protected attach record, same-attempt
        # finalization LAST)
        record_doc = run.publish_native(native_out)

        assert record_doc["record"] == fno.AF_NATIVE_RUN_SCHEMA
        assert record_doc["identity"] == identity
        assert record_doc["owner_outcome"] == "pass"
        assert record_doc["attempt"] == "running"  # pending, never a predicted token
        assert record_doc["subject_measured"] is True
        assert record_doc["stop_recorded"] is True
        assert record_doc["native_refusal"] is None
        assert record_doc["verdict"] == {"ready": True, "reasons": []}
        fno.parse_native_run_record(record_doc)
        facts = fp.parse_native_owner_facts(record_doc["native_record"])
        assert facts.schema == fp.AF_NATIVE_OWNER_SCHEMA
        assert facts.identity == (SUBJ_UID, SUBJ_GID, (SUBJ_GID,))
        assert facts.order == AF_ORDER_ID
        assert facts.source_head == HEAD
        assert facts.run_id == binding.run_id
        assert facts.cid == run.owner.target_cid
        assert facts.native_started is True
        assert facts.native_ready is True
        # the nested PROTECTED AF attach record: the closed
        # consumer re-derives the allocation from the two
        # embedded inventories against the OUTER binding
        # record (a copied/replayed record never mints
        # authority)
        attach = record_doc["attach_binding"]
        assert attach is not None
        rederived = fp.parse_attach_binding_record(attach, run.binding)
        assert attach["record"] == fp.AF_ATTACH_BINDING_SCHEMA
        assert attach["expected_tty_nr"] == AF_TTY_NR
        assert attach["namespace"] == list(AF_DEVPTS_NS)
        assert attach["cid"] == run.owner.target_cid
        assert rederived.major == AF_ALLOC[0]
        assert rederived.minor == AF_ALLOC[1]
        assert rederived.inode == AF_ALLOC[2]
        assert rederived.mode == AF_ALLOC[3]
        st = native_out.stat()
        assert (st.st_mode & 0o777) == 0o600 and st.st_uid == os.getuid()

        # the same-order journal is terminal pass ONLY after
        # the protected publication (the real finalize token
        # in RAM)
        assert run.finalize_attempt() == "finalized"
        record = fb.read_admission_record(repo, AF_ORDER_ID)
        assert record["attempts"] == [{"head": HEAD, "run_id": binding.run_id, "status": "pass"}]

        # the owner's OWN distinct AF terminal evidence: the
        # SAME frozen identity (compared, never rebased), the
        # exact-CID teardown proof, the bound order
        ev_raw = json.loads(owner_evidence.read_bytes().decode("ascii"))
        flocal.validate_af_owner_run_evidence(ev_raw)
        assert ev_raw["record"] == flocal.AF_OWNER_RUN_EVIDENCE_SCHEMA
        assert ev_raw["scope"] == flocal.AF_OWNER_RUN_SCOPE
        assert ev_raw["order"] == AF_ORDER_ID
        assert ev_raw["status"] == "pass"
        assert ev_raw["identity"] == identity
        assert ev_raw["teardown_proof"] == "exact-cid-membership"
        assert ev_raw["fixture_consumed_by"] == "unobserved"

        # the same frozen identity across EVERY retained
        # layer of the same attempt (no rebase anywhere in
        # the composition)
        assert (
            snapshot["identity"]
            == identity
            == record_doc["identity"]
            == ev_raw["identity"]
            == attach["identity"]
        )

        # ONE shared run context: the SAME frozen owner
        # context, END anchor and ledger across the whole
        # lifecycle (compared, never rebased or replaced)
        assert run.owner._owner_context is ctx_before
        assert run.owner.deadline.anchor == anchor_before
        assert run.owner.ledger is ledger_before
        # no global subject-UID scan ever ran on the
        # owner-UID path (the trap would have raised); the
        # controller-UID scan kept its closed historical
        # semantics
        assert SUBJ_UID not in uid_calls
        assert CTL_UID in uid_calls


def test_af_baseline_foreign_probe_uid_consumes_failed_phase(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A probe record whose MEASURED uid is not the frozen
    subject uid (the record would otherwise be closed and
    valid): a closed typed refusal at the owner's measurement
    boundary — the attempt stays consumed with a retained
    failed phase, NO baseline commits, and NO later fresh
    baseline or second observation (a resampled world could
    hide a multiple-allocation refusal)."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        run.start()
        run.prepare()
        run.observe()
        world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
        run.record_stop()
        world.devpts_probe_uid = 1003  # a foreign MEASURED probe uid
        with pytest.raises(fci.FixtureError, match="local-devpts-probe-uid-mismatch"):
            run.collect_attach_baseline()
        # the consumed failed phase: no usable baseline, the
        # failure retained, the attempt consumed
        assert run._attach_baseline is None
        assert run._attach_failure == "local-devpts-probe-uid-mismatch"
        assert run._attach_baseline_attempted is True
        # NO resampling, ever: a corrected world still refuses
        world.devpts_probe_uid = SUBJ_UID
        with pytest.raises(fci.FixtureError, match="native-owner-attach-baseline-repeat"):
            run.collect_attach_baseline()
        with pytest.raises(fci.FixtureError, match="native-owner-attach-baseline-missing"):
            run.derive_attach_expectation()
        assert run._attach_receipt is None


def test_af_derive_foreign_probe_uid_retains_failure_no_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The baseline measured clean, then the SECOND
    observation's record carries a foreign measured uid: a
    closed typed refusal — the SAME baseline/stop stay
    retained, the attempt stays consumed with a retained
    failed phase, NO receipt commits, and NO resampling (a
    later corrected world still refuses)."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        run.start()
        run.prepare()
        run.observe()
        world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
        run.record_stop()
        baseline = run.collect_attach_baseline()
        assert baseline.inventory.slave_rows == ()
        assert world.devpts_probe_calls == 1
        world.launch_native()
        world.devpts_probe_uid = 1003  # the SECOND observation is foreign
        with pytest.raises(fci.FixtureError, match="local-devpts-probe-uid-mismatch"):
            run.derive_attach_expectation()
        # the SAME measured baseline/stop survive the refusal;
        # the failure is retained; the attempt is consumed
        assert run._attach_baseline is not None
        assert run.workflow.stop_receipt is not None
        assert run._attach_receipt is None
        assert run._attach_failure == "local-devpts-probe-uid-mismatch"
        assert run._attach_derive_attempted is True
        # NO resampling, ever: a corrected world still refuses
        world.devpts_probe_uid = SUBJ_UID
        with pytest.raises(fci.FixtureError, match="native-owner-attach-binding-repeat"):
            run.derive_attach_expectation()
        assert run._attach_receipt is None


def _af_prep_through_baseline(run: Any, world: Any) -> None:
    """start/prepare/observe/stop + the ONE-SHOT EMPTY baseline
    (the attach phase up to the allocation, no derive)."""
    run.start()
    run.prepare()
    run.observe()
    world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
    run.record_stop()
    baseline = run.collect_attach_baseline()
    assert baseline.inventory.slave_rows == ()


def test_af_derive_end_crossed_during_measurement_retains_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The SAME absolute owner END crosses DURING the second
    measurement (the entry check passed; the final check in
    the failure-handled region refuses): the attempt stays
    consumed with a retained failed phase, NO receipt commits,
    and NO resampling."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep_through_baseline(run, world)
        world.launch_native()
        real = run.owner.devpts_inventory
        obs = real()  # the valid measured observation (probe #2)

        def crossed_end() -> Any:
            # the owner's ONE absolute END passes at the race
            # point: the final check after the measurement
            # refuses
            run.owner.deadline.anchor = time.monotonic() - 1.0
            return obs

        monkeypatch.setattr(run.owner, "devpts_inventory", crossed_end)
        with pytest.raises(fci.FixtureError, match="native-owner-patience"):
            run.derive_attach_expectation()
        assert run._attach_receipt is None
        assert run._attach_failure == "native-owner-patience"
        assert run._attach_derive_attempted is True
        # NO resampling, ever
        with pytest.raises(fci.FixtureError, match="native-owner-attach-binding-repeat"):
            run.derive_attach_expectation()
        assert run._attach_receipt is None


def test_af_derive_final_stop_check_resumes_worker_retains_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The worker RESUMES at the final stable-stop re-check
    (after the observation, the retained stop receipt is
    re-verified and no longer holds): a closed refusal — the
    attempt stays consumed with a retained failed phase, NO
    receipt commits, and NO resampling."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep_through_baseline(run, world)
        world.launch_native()
        real = run.owner.devpts_inventory
        obs = real()  # the valid measured observation (probe #2)

        def resume_worker() -> Any:
            # the SAME worker job resumes: the recorded stop
            # phase no longer holds
            world.procs[WORK_PID] = _worker_proc("S", tpgid=WORK_PID, start=WORK_START)
            return obs

        monkeypatch.setattr(run.owner, "devpts_inventory", resume_worker)
        with pytest.raises(fci.FixtureError, match="prep-stop-unobserved"):
            run.derive_attach_expectation()
        assert run._attach_receipt is None
        assert run._attach_failure == "prep-stop-unobserved"
        assert run._attach_derive_attempted is True
        # the SAME measured baseline survives the refusal
        assert run._attach_baseline is not None
        # NO resampling, ever
        with pytest.raises(fci.FixtureError, match="native-owner-attach-binding-repeat"):
            run.derive_attach_expectation()
        assert run._attach_receipt is None


def test_af_derive_identity_drift_during_measurement_retains_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The host owner identity DRIFTS after the measurement:
    the frozen-context revalidation in the failure-handled
    region refuses — the attempt stays consumed with a
    retained failed phase, NO receipt commits, and NO
    resampling."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep_through_baseline(run, world)
        world.launch_native()
        real = run.owner.devpts_inventory
        obs = real()  # measured BEFORE the drift is installed

        monkeypatch.setattr(run.owner, "devpts_inventory", lambda: obs)
        monkeypatch.setattr(
            run.owner,
            "identity_reader",
            lambda: (SUBJ_UID + 1, SUBJ_UID + 1, SUBJ_UID + 1, SUBJ_GID, SUBJ_GID, SUBJ_GID),
        )
        with pytest.raises(fci.FixtureError, match="local-identity-drift"):
            run.derive_attach_expectation()
        assert run._attach_receipt is None
        assert run._attach_failure == "local-identity-drift"
        assert run._attach_derive_attempted is True
        # NO resampling, ever
        with pytest.raises(fci.FixtureError, match="native-owner-attach-binding-repeat"):
            run.derive_attach_expectation()
        assert run._attach_receipt is None


def test_af_derive_copy_failure_retains_failure_no_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A record that CANNOT be prepared as the public copy
    (a non-closed value smuggled past the producer) is a
    refusal INSIDE the failure-handled region: the attempt
    stays consumed with a retained failed phase, NO private
    receipt commits, and NO resampling."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep_through_baseline(run, world)
        world.launch_native()

        real_producer = fp.attach_binding_record

        def unserializable_record(**kw: Any) -> Any:
            record = real_producer(**kw)
            # a non-closed value: the record cannot be copied
            # to its public JSON form
            record["observation"] = {**record["observation"], "bogus": object()}
            return record

        monkeypatch.setattr(fp, "attach_binding_record", unserializable_record)
        with pytest.raises(TypeError):
            run.derive_attach_expectation()
        assert run._attach_receipt is None
        assert run._attach_failure is not None
        assert run._attach_derive_attempted is True
        # NO resampling, ever
        with pytest.raises(fci.FixtureError, match="native-owner-attach-binding-repeat"):
            run.derive_attach_expectation()
        assert run._attach_receipt is None


def test_af_devpts_probe_guard_af_only_and_old_guards_refuse() -> None:
    """The ONE exact NON-PTY devpts probe argv is admitted by
    the canonical 017-af entry's guard ONLY (selected from the
    owner's OWN bound order): the AB/AD/default guards keep
    the byte-for-byte old closed forms and refuse the exact
    new probe and every modified argv (no -it — a PTY would
    allocate and contaminate the measured namespace — no
    controller user, no environment, no alternate python
    flags)."""
    profile = frp.owner_runtime_profile(_ad_description())
    assert profile.exec_user == f"{SUBJ_UID}:{SUBJ_GID}"
    af_matchers = fci._owner_argv_matchers(profile, frp.AF_ORDER_ID)
    ad_matchers = fci._owner_argv_matchers(profile, frp.AD_ORDER_ID)
    ab_matchers = fci._owner_argv_matchers(profile, frp.AB_ORDER_ID)
    # the original entries keep the byte-for-byte original
    # module-level matcher tuple (their owners never mint the
    # owner-scoped set)
    original_matchers = fci._ARGV_MATCHERS
    # direct AF guard construction: EXACTLY ONE extra closed
    # matcher, callable without TypeError (the old forms are
    # the SAME unchanged matchers, plus the narrow AF one)
    assert len(af_matchers) == len(ad_matchers) + 1
    af_probe_matcher = af_matchers[-1]
    assert callable(af_probe_matcher)
    # the old forms are BEHAVIORALLY unchanged between the
    # AF and non-AF owner tuples (factory closures are not
    # identity-comparable — compare their decisions over the
    # closed old forms)
    # the SAME closed old forms (positives and negatives):
    # the AF and non-AF owner tuples decide them identically
    old_forms: list[list[str]] = [
        ["docker", "ps", "-aq", "--filter", "id=" + "a" * 64],  # admitted
        ["docker", "version", "--format", "{{.Server.Version}}"],  # admitted
        [
            "docker",
            "exec",
            "--user",
            f"{SUBJ_UID}:{SUBJ_GID}",
            "f" * 64,
            "python3",
            "-c",
            fci.CONTROLLER_PROBE,
        ],  # admitted (subject user)
        [
            "docker",
            "exec",
            "--user",
            f"{SUBJ_UID}:{SUBJ_GID}",
            "f" * 64,
            "python3",
            fci.EXPORT_CLIENT_PATH,
        ],  # admitted (export)
        [
            "docker",
            "exec",
            "--user",
            f"{SUBJ_UID}:{SUBJ_GID}",
            "f" * 64,
            "python3",
            "-c",
            "print(1)",
        ],  # refused (open program)
        ["docker", "ps", "-a"],  # refused (not the closed form)
    ]
    admitted = 0
    for argv in old_forms:
        # matchers may return a truthy re.Match — compare
        # decisions, not objects
        for m_af, m_other in zip(af_matchers[:-1], ad_matchers, strict=True):
            assert bool(m_af(argv)) == bool(m_other(argv))
        admitted += sum(1 for m in ad_matchers if m(argv))
    assert admitted >= 4  # the positive forms really are admitted

    def probe_argv(
        user: str = f"{SUBJ_UID}:{SUBJ_GID}",
        cid: str = "f" * 64,
        python: tuple[str, ...] = ("python3", "-I", "-S", "-c"),
        body: str = fci.DEVPTS_PROBE,
        prefix: tuple[str, ...] = (),
        suffix: tuple[str, ...] = (),
    ) -> list[str]:
        return ["docker", "exec", *prefix, "--user", user, cid, *python, body, *suffix]

    exact = probe_argv()
    assert len(exact) == 10
    # the AF entry's guard admits the exact form (any valid
    # registered-CID-shaped target)
    assert af_probe_matcher(exact) is True
    assert af_probe_matcher(probe_argv(cid="e" * 64)) is True
    # the AB/AD/default guards refuse the EXACT new probe
    assert not any(m(exact) for m in ad_matchers)
    assert not any(m(exact) for m in ab_matchers)
    assert not any(m(exact) for m in original_matchers)
    # every modified argv is refused by EVERY guard, AF
    # included (the closed form is EXACT)
    for mutated in (
        probe_argv(prefix=("-it",)),  # a PTY attach contaminates
        probe_argv(user="21001:21001"),  # the controller user
        # the ORIGINAL profile's OWN valid exec user: the
        # native-specific operation form itself is unavailable
        # to the original/default guard (not merely a wrong
        # user refusal)
        probe_argv(user="21002:21002"),
        probe_argv(prefix=("--env-file", "/tmp/slaif-env")),  # env-file
        [
            "docker",
            "exec",
            "--user",
            f"{SUBJ_UID}:{SUBJ_GID}",
            "f" * 64,
            "python3",
            "-I",
            "-S",
            "-e",
            "A=1",
            "-c",
            fci.DEVPTS_PROBE,
        ],  # -e
        probe_argv(python=("python3", "-S", "-c")),  # no -I
        probe_argv(python=("python3", "-I", "-c")),  # no -S
        probe_argv(python=("python3.12", "-I", "-S", "-c")),  # alternate binary
        probe_argv(body="print(1)"),  # a different probe body
        probe_argv(suffix=("--flag",)),  # an extra argument
        exact[:-1],  # a missing argument
        probe_argv(cid="xyz"),  # a non-CID target
    ):
        assert not any(m(mutated) for m in af_matchers)
        assert not any(m(mutated) for m in ad_matchers)
        assert not any(m(mutated) for m in original_matchers)


def test_af_probe_refuses_foreign_or_unprepared_target(tmp_path: Path) -> None:
    """The fake probe surface is bound to the SAME world's OWN
    registered CID and a live/prepared container (created,
    the controller frame attached): the measured inventory is
    never returned for a foreign CID-shaped argv, an unknown
    container, or an unprepared target (a closed refusal, no
    probe charged)."""
    world, fake = _af_new_world(tmp_path)
    probe = [
        "docker",
        "exec",
        "--user",
        f"{SUBJ_UID}:{SUBJ_GID}",
        "f" * 64,
        "python3",
        "-I",
        "-S",
        "-c",
        fci.DEVPTS_PROBE,
    ]
    # no container registered yet: any CID-shaped probe is a
    # closed refusal, no probe charged
    assert fake(probe, 5.0).returncode == 125
    assert world.devpts_probe_calls == 0
    # a prepared world: the SAME registered CID is admitted
    world.cid = "f" * 64
    world.controller = {"cgroup": world.cid}
    aa._write_proc_entry(
        world.proc_root,
        CTL_PID,
        comm="python3",
        start=CTL_START,
        uid=CTL_UID,
        gid=CTL_UID,
        groups=(),
        cgroup=world.cid,
    )
    assert fake(probe, 5.0).returncode == 0
    assert world.devpts_probe_calls == 1
    # a FOREIGN CID-shaped argv over the SAME prepared world:
    # closed refusal, no probe charged
    foreign = list(probe)
    foreign[4] = "e" * 64
    assert fake(foreign, 5.0).returncode == 125
    assert world.devpts_probe_calls == 1


def _af_drive_to_published(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Any, Any, Any, Any]:
    """Drive the coherent AF world through
    start/prepare/stop/baseline/launch/derive/register/exit/
    finish (the COMPLETED owner, not yet published)."""
    world, fake = _af_new_world(tmp_path)
    run, repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    try:
        _af_prep(run, world)
        monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, []))
        run.register_subject(NAT_PID, _af_expectation(run))
        world.exit_native()
        run.finish()
        assert run.owner.terminal_outcome == "pass"
        _join_run(run)
        world.procs[WORK_PID] = _worker_proc("S", tpgid=WORK_PID, start=WORK_START)
        return run, repo, world, fake
    except BaseException:
        _join_run(run)
        raise


def _af_at_use_owner(case_dir: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Any, Any]:
    """ONE fresh prepared AF owner (start/prepare/observe done,
    the ORIGINAL owner END untouched) for a single at-use
    boundary case — each case gets its OWN owned subdirectory
    (a fresh synthetic repo/admission/control — an admission
    is never reset or reused) so separate owners keep each
    case's END and phase facts clean."""
    case_dir.mkdir(parents=True, exist_ok=True)
    world, fake = _af_new_world(case_dir)
    run, _repo, _f, _ev, _c, _u = _af_run(case_dir, monkeypatch, world=world, docker=fake)
    try:
        run.start()
        run.prepare()
        run.observe()
        return run, world
    except BaseException:
        # a setup assertion/refusal still reaps its owner
        # before monkeypatch teardown
        _join_run(run)
        raise


def test_af_devpts_inventory_at_use_boundaries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The REAL owner.devpts_inventory's at-use boundary over
    scripted executors (ONE fresh owner per case, the
    ORIGINAL owner END never refreshed): an executor failure,
    a retained valid prefix with discarded extra bytes,
    over-cap output (the drained-total law — the existing
    closed refusal), a late blocking return crossing the
    per-probe absolute end, and a host identity drift DURING
    the probe are all closed typed refusals — the measured
    observation never escapes; the complete valid capture is
    retained (the boundary does not over-refuse).  Every fake
    nonempty result carries its drained total EXACTLY; the
    guarded/reader fakes are scoped so they restore BEFORE
    the owned-run final cleanup."""
    # positive control: the complete valid capture is retained
    run, world = _af_at_use_owner(tmp_path / "case-positive", monkeypatch)
    valid = world._devpts_record()  # the closed valid empty-baseline record
    with _owned_run(run):
        with monkeypatch.context() as mp:
            mp.setattr(
                run.owner,
                "guarded",
                lambda argv, timeout: fci.ExecResult(0, valid, drained_bytes=len(valid)),
            )
            obs = run.owner.devpts_inventory()
            assert obs.inventory.uid == SUBJ_UID
            assert obs.inventory.slave_rows == ()
            assert obs.record == valid
    # 1. an executor failure is a closed typed refusal
    run, world = _af_at_use_owner(tmp_path / "case1", monkeypatch)
    with _owned_run(run):
        with monkeypatch.context() as mp:
            mp.setattr(run.owner, "guarded", lambda argv, timeout: fci.ExecResult(1, b""))
            with pytest.raises(fci.FixtureError, match="local-devpts-exec-failed"):
                run.owner.devpts_inventory()
    # 2. a retained valid prefix with DISCARDED extra output
    # is not a complete observation (the drained total is not
    # the retained bytes)
    run, world = _af_at_use_owner(tmp_path / "case2", monkeypatch)
    valid = world._devpts_record()
    with _owned_run(run):
        with monkeypatch.context() as mp:
            mp.setattr(
                run.owner,
                "guarded",
                lambda argv, timeout: fci.ExecResult(0, valid, drained_bytes=len(valid) + 16),
            )
            with pytest.raises(fci.FixtureError, match="local-devpts-capture-invalid"):
                run.owner.devpts_inventory()
    # 3. over-cap output: the drained TOTAL (retained +
    # discarded) crossing the cap is refused by the
    # complete-capture law — the EXISTING closed refusal (the
    # consumer's own byte cap is proven separately at the
    # pure codec level)
    run, world = _af_at_use_owner(tmp_path / "case3", monkeypatch)
    with _owned_run(run):
        with monkeypatch.context() as mp:
            mp.setattr(
                run.owner,
                "guarded",
                lambda argv, timeout: fci.ExecResult(
                    0,
                    b"x" * (fci.DEVPTS_OUTPUT_MAX + 1),
                    drained_bytes=fci.DEVPTS_OUTPUT_MAX + 1,
                ),
            )
            with pytest.raises(fci.FixtureError, match="local-devpts-capture-invalid"):
                run.owner.devpts_inventory()
    # 4. a late blocking return crossing the per-probe
    # absolute end (min(start + the probe's own bound, the
    # ORIGINAL owner END) — here the probe's own bound,
    # scoped to this case only): no grace, no fresh window
    run, world = _af_at_use_owner(tmp_path / "case4", monkeypatch)
    valid = world._devpts_record()
    with _owned_run(run):
        with monkeypatch.context() as mp:
            mp.setattr(fci, "DEVPTS_PROBE_TIMEOUT", 0.05)

            def late(argv: object, timeout: object) -> object:
                time.sleep(0.06)
                return fci.ExecResult(0, valid, drained_bytes=len(valid))

            mp.setattr(run.owner, "guarded", late)
            with pytest.raises(fci.FixtureError, match="local-devpts-end-expired"):
                run.owner.devpts_inventory()
    # 5. a host identity drift DURING the probe: the entry
    # revalidation passes, the RETURN revalidation refuses
    run, world = _af_at_use_owner(tmp_path / "case5", monkeypatch)
    valid = world._devpts_record()
    with _owned_run(run):
        with monkeypatch.context() as mp:
            calls = {"n": 0}

            def drift_reader() -> tuple[int, int, int, int, int, int]:
                calls["n"] += 1
                if calls["n"] == 1:
                    return (SUBJ_UID, SUBJ_UID, SUBJ_UID, SUBJ_GID, SUBJ_GID, SUBJ_GID)
                return (SUBJ_UID + 1, SUBJ_UID + 1, SUBJ_UID + 1, SUBJ_GID, SUBJ_GID, SUBJ_GID)

            mp.setattr(
                run.owner,
                "guarded",
                lambda argv, timeout: fci.ExecResult(0, valid, drained_bytes=len(valid)),
            )
            mp.setattr(run.owner, "identity_reader", drift_reader)
            with pytest.raises(fci.FixtureError, match="local-identity-drift"):
                run.owner.devpts_inventory()
            assert calls["n"] == 2  # entry + return revalidation


def test_af_second_publication_refused_one_shot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The completed AF owner's publication is a ONE-SHOT
    terminal transition: a second publication on a fresh path
    is a closed refusal (no retry, no relabel), and the
    RETAINED AF record's closed cross-field law refuses a
    mutated copy (the outer, the nested native and the nested
    attach identities are cross-bound to ONE frozen context;
    a derived copy with one field changed can never
    validate)."""
    run, _repo, _w, _f = _af_drive_to_published(tmp_path, monkeypatch)
    with _owned_run(run):
        record = run.publish_native(tmp_path / "evidence" / "af-native-run-record.json")
        assert record["owner_outcome"] == "pass"
        with pytest.raises(fci.FixtureError, match="native-owner-published"):
            run.publish_native(tmp_path / "evidence" / "second.json")
        assert not (tmp_path / "evidence" / "second.json").exists()
        # the RETAINED record validates (the production bytes)
        fno.parse_native_run_record(record)
        import copy

        foreign = fp._ad_identity_substructure_from_triple((1003, 1004, (1004,)))
        # OUTER identity mutated (internally consistent, foreign):
        # the cross-bound nested identities can no longer agree
        mutated = copy.deepcopy(record)
        mutated["identity"] = foreign
        with pytest.raises(fci.FixtureError, match="native-owner-record-malformed"):
            fno.parse_native_run_record(mutated)
        # NESTED native-record identity mutated
        mutated = copy.deepcopy(record)
        mutated["native_record"]["identity"] = foreign
        with pytest.raises(fci.FixtureError, match="native-owner-record-malformed"):
            fno.parse_native_run_record(mutated)
        # NESTED attach identity mutated (cross-bound to the
        # outer frozen context)
        mutated = copy.deepcopy(record)
        mutated["attach_binding"]["identity"] = foreign
        with pytest.raises(fci.FixtureError, match="native-owner-record-malformed"):
            fno.parse_native_run_record(mutated)
        # NESTED attach CID mutated (cross-bound to the
        # measured native record's CID)
        mutated = copy.deepcopy(record)
        mutated["attach_binding"]["cid"] = "e" * 64
        with pytest.raises(fci.FixtureError, match="native-owner-record-malformed"):
            fno.parse_native_run_record(mutated)


def test_af_preexisting_native_destination_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pre-existing foreign AF native destination is a
    closed refusal (fail-if-exists): the attempt
    terminalizes honestly, the foreign bytes are preserved
    untouched, and no fresh-path retry is ever made."""
    world, fake = _af_new_world(tmp_path)
    run, repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        try:
            _af_prep(run, world)
            monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, []))
            run.register_subject(NAT_PID, _af_expectation(run))
            world.exit_native()
            run.finish()
            assert run.owner.terminal_outcome == "pass"
            _join_run(run)
            native_out = tmp_path / "evidence" / "af-native-run-record.json"
            native_out.parent.mkdir(parents=True, exist_ok=True)
            native_out.write_bytes(b"foreign bytes\n")
            with pytest.raises(fci.FixtureError, match="native-owner-evidence-exists"):
                run.publish_native(native_out)
            # the foreign bytes are preserved untouched
            assert native_out.read_bytes() == b"foreign bytes\n"
            # the same won attempt was terminalized honestly (fail)
            record = fb.read_admission_record(repo, AF_ORDER_ID)
            assert record["attempts"] == [
                {"head": HEAD, "run_id": run.binding.run_id, "status": "fail"}
            ]
        except BaseException:
            _join_run(run)
            raise


def test_af_registration_refuses_caller_channel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A caller-supplied channel for the AF entry is a closed
    refusal BEFORE any factory call or commit (the AF entry
    measures through its OWN default exact registered-CID
    channel only — no bypass of the scoped/birth-bound
    reads)."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        calls: list[tuple[Any, float]] = []
        monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, calls))
        channel = stp.FakeCidScopedTable(
            str(run.owner.target_cid), world.procs, exe_digest=FAKE_BINARY
        )
        with pytest.raises(fci.FixtureError, match="native-owner-attach-channel-invalid"):
            run.register_subject(NAT_PID, _af_expectation(run), channel=channel)
        assert calls == []  # the default factory was never consulted
        assert run.workflow.subject_receipt is None


def test_af_registration_without_receipt_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No measured attach receipt (the allocation was never
    derived): the registration is a closed refusal BEFORE any
    channel or commit — a foreign/unobserved expectation can
    never bind the AF entry."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        run.start()
        run.prepare()
        run.observe()
        world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
        run.record_stop()
        run.collect_attach_baseline()
        world.launch_native()  # the subject exists, but NO derive ran
        with pytest.raises(fci.FixtureError, match="native-owner-attach-binding-missing"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def test_af_registration_pty_mismatch_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An expectation whose PTY is NOT the derived expected
    tty_nr (the expected PTY comes from the owned attach,
    never from the subject itself or a guess): a closed
    refusal, nothing committed."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, []))
        with pytest.raises(fci.FixtureError, match="native-owner-attach-pty-mismatch"):
            run.register_subject(NAT_PID, _af_expectation(run, expected_tty=AF_TTY_NR + 1))
        assert run.workflow.subject_receipt is None


def test_af_registration_context_invalid_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A retained receipt whose allocation no longer encodes
    to its own derived tty_nr (a corrupted/contradicted
    context): a closed refusal at the re-encode frame BEFORE
    any channel or commit."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        run._attach_receipt["allocation"]["major"] = 137  # corrupted retained context
        with pytest.raises(fci.FixtureError, match="native-owner-attach-context-invalid"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def test_af_registration_foreign_namespace_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The SAME numeric tty in a FOREIGN devpts namespace (the
    subject's mount view root differs from the measured
    private namespace): a closed refusal, nothing committed —
    equal tty numbers alone are never sufficient."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        world.procs[NAT_PID]["devpts_slave"]["root_dev"] = 28  # a foreign namespace root
        monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, []))
        with pytest.raises(fci.FixtureError, match="native-owner-attach-devpts-namespace-mismatch"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def test_af_registration_foreign_node_device_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The selected slave node lives on a DIFFERENT filesystem
    than the measured devpts root (an equal inode/mode/owner
    on another filesystem is not the owned allocation): a
    closed refusal, nothing committed."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        world.procs[NAT_PID]["devpts_slave"]["slave_dev"] = 10  # a foreign filesystem
        monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, []))
        with pytest.raises(fci.FixtureError, match="native-owner-attach-devpts-namespace-mismatch"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def test_af_registration_device_mismatch_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A slave device whose major/minor is not the owned
    allocation's device: a closed refusal, nothing committed."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        world.procs[NAT_PID]["devpts_slave"]["major"] = 137
        monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, []))
        with pytest.raises(fci.FixtureError, match="native-owner-attach-devpts-device-mismatch"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def test_af_registration_inode_mismatch_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A slave node with a different inode than the owned
    allocation (a different node wearing the same number): a
    closed refusal, nothing committed."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        world.procs[NAT_PID]["devpts_slave"]["slave_ino"] = 78
        monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, []))
        with pytest.raises(fci.FixtureError, match="native-owner-attach-devpts-inode-mismatch"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def test_af_registration_mode_mismatch_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A slave node whose PERMISSION BITS differ from the owned
    allocation (the FULL measured mode is normalized before
    comparison): a closed refusal, nothing committed."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        world.procs[NAT_PID]["devpts_slave"]["slave_mode"] = stat.S_IFCHR | 0o640
        monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, []))
        with pytest.raises(fci.FixtureError, match="native-owner-attach-devpts-mode-mismatch"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def test_af_registration_owner_mismatch_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A slave node owned by a different UID/GID than the
    owned allocation: a closed refusal, nothing committed."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        world.procs[NAT_PID]["devpts_slave"]["slave_uid"] = 1003
        monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, []))
        with pytest.raises(fci.FixtureError, match="native-owner-attach-devpts-owner-mismatch"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def test_af_registration_unreadable_metadata_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The per-subject metadata is unreadable/absent from the
    subject's mount view (a typed unknown, never an
    assumption): a closed refusal, nothing committed."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        del world.procs[NAT_PID]["devpts_slave"]
        monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, []))
        with pytest.raises(fci.FixtureError, match="native-owner-attach-devpts-unreadable"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def test_af_registration_out_of_scope_subject_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The subject is no longer observed in the registered
    container's scope (the scoped stat read is the typed
    unknown): a closed refusal, nothing committed."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        del world.procs[NAT_PID]["cgroup"]
        monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, []))
        with pytest.raises(fci.FixtureError, match="native-owner-attach-devpts-unreadable"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def _mutate_pid_reuse(channel: Any, pid: int, birth: int) -> None:
    """A PID reuse AT the final executable re-measurement: the
    same number is now a DIFFERENT process (a new birth)."""
    channel._world.procs[pid] = stp.subject_proc(
        pid,
        cgroup=str(channel.cid),
        uid=SUBJ_UID,
        gid=SUBJ_GID,
        groups=(SUBJ_GID,),
        start=birth + 1,
    )


def test_af_final_frame_pid_reuse_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A PID reused AFTER collection (the same number now a
    different process, detected by the birth-bound channel at
    the final executable re-measurement): a closed refusal,
    NO receipt commit — a reused PID can never validate
    itself against a fresh stat."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        racy = _racy_channel_class(_mutate_pid_reuse)

        def factory(cid: Any, end: float) -> Any:
            return racy(cid, world.procs, world=world, exe_digest=FAKE_BINARY)

        monkeypatch.setattr(fno, "build_ad_native_channel", factory)
        with pytest.raises(fci.FixtureError, match="native-owner-attach-identity-drift"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def _mutate_uid_drift(channel: Any, pid: int, birth: int) -> None:
    """A native-UID drift AT the final executable
    re-measurement: the SAME process (same birth) changes its
    UID after collection."""
    p = channel._world.procs[pid]
    p["status"] = stp.status_bytes(1003, SUBJ_GID, (SUBJ_GID,))


def test_af_final_frame_uid_drift_during_hash_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A native UID drift DURING the final metadata/hash (the
    same process, the same birth, a changed UID): the identity
    frame re-verified AFTER the blocking operations refuses —
    the collected frame never goes stale at commit, and NO
    receipt commits."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        racy = _racy_channel_class(_mutate_uid_drift)

        def factory(cid: Any, end: float) -> Any:
            return racy(cid, world.procs, world=world, exe_digest=FAKE_BINARY)

        monkeypatch.setattr(fno, "build_ad_native_channel", factory)
        with pytest.raises(fci.FixtureError, match="native-owner-attach-identity-drift"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def _mutate_namespace_race(channel: Any, pid: int, birth: int) -> None:
    """A devpts namespace change AT the final executable
    re-measurement: the subject's mount view root is no
    longer the measured private namespace."""
    channel._world.procs[pid]["devpts_slave"]["root_dev"] = 28


def test_af_final_frame_namespace_raced_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A namespace change DURING the final hash (caught by the
    devpts frame re-read AFTER the executable re-measurement,
    still bound to the ORIGINAL collected PID/birth): a
    closed refusal, NO receipt commit."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        racy = _racy_channel_class(_mutate_namespace_race)

        def factory(cid: Any, end: float) -> Any:
            return racy(cid, world.procs, world=world, exe_digest=FAKE_BINARY)

        monkeypatch.setattr(fno, "build_ad_native_channel", factory)
        with pytest.raises(fci.FixtureError, match="native-owner-attach-devpts-namespace-mismatch"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def _mutate_exe_drift(channel: Any, pid: int, birth: int) -> None:
    """An in-place exec AT the final executable
    re-measurement: the SAME PID/birth now runs a different
    binary (the current-executable race)."""
    channel._exe_digest = "e" * 64


def test_af_final_frame_exe_drift_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An in-place exec DURING the final hash (same PID, same
    birth, a different actual running executable): the
    current-executable race law refuses across the final
    metadata phase, NO receipt commit."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)
        racy = _racy_channel_class(_mutate_exe_drift)

        def factory(cid: Any, end: float) -> Any:
            return racy(cid, world.procs, world=world, exe_digest=FAKE_BINARY)

        monkeypatch.setattr(fno, "build_ad_native_channel", factory)
        with pytest.raises(fci.FixtureError, match="native-owner-attach-identity-drift"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


def _mutate_end_crossed(channel: Any, pid: int, birth: int) -> None:
    """The SAME absolute owner END crosses AT the final
    executable re-measurement (the owner's deadline
    anchor is set by the test below)."""


def test_af_final_frame_end_crossed_during_hash_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The SAME absolute owner END crossed DURING the final
    hash: the original-END gate at the collect-before-commit
    boundary refuses — NO receipt commit, no cleanup-grace
    measurement, no captured-duration extension."""
    world, fake = _af_new_world(tmp_path)
    run, _repo, _f, _ev, _c, _u = _af_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        _af_prep(run, world)

        def cross_end(channel: Any, pid: int, birth: int) -> None:
            # the owner's ONE absolute END passes at the race point
            run.owner.deadline.anchor = time.monotonic() - 1.0

        racy = _racy_channel_class(cross_end)

        def factory(cid: Any, end: float) -> Any:
            return racy(cid, world.procs, world=world, exe_digest=FAKE_BINARY)

        monkeypatch.setattr(fno, "build_ad_native_channel", factory)
        with pytest.raises(fci.FixtureError, match="native-owner-patience"):
            run.register_subject(NAT_PID, _af_expectation(run))
        assert run.workflow.subject_receipt is None


# ============================================================================
# 017-ag: the sealed INERT 017-ah entry + zero-group coupled lifecycle
# ============================================================================

AH_ORDER_ID = "017-ah"
AH_ORDER_NAME = "017-ah-owner-uid-native-pty-requalification.md"
AH_ORDER_BYTES = b"# synthetic AH order (fake seam only)\n"
AG_ORDER_ID = "017-ag"
AG_ORDER_NAME = "017-ag-synthetic-active.md"
AG_ORDER_BYTES = b"# synthetic AG order (fake seam only)\n"

# The UNRELATED well-formed kernel-thread-like observation
# row present across the coupled lifecycle (pgrp 0 / session
# 0 / tty 0 / tpgid -1 — observation data only: never a
# group member, never a tool session, never an authority
# frame, never mutated).
KERNEL_PID = 999


def _kernel_proc() -> dict[str, Any]:
    return {
        "stat": stp.stat_line(KERNEL_PID, "kworker/0:1", "S", 2, 0, 0, 0, -1, 5),
        "cmdline": b"",
        "status": stp.status_bytes(0, 0),
    }


def _ah_repo(base: Path, *, active_order: str = AH_ORDER_ID) -> Path:
    """The S-shaped synthetic repo for the 017-ag AH entry
    tests: the AH canonical order file is committed; oap/active
    selects the requested entry (AH by default, AG for the
    pre-admission refusal law).  Test order bytes live ONLY in
    owned synthetic repositories — the real AH order is never
    created in this checkout."""
    repo = Path(stl._make_local_repo(base))
    for name in (
        "cache_native_fixture_owner.Dockerfile",
        "cache_native_fixture_identity.py",
        "cache_native_fixture_native_prep.py",
        "cache_native_fixture_runtime_profile.py",
        "cache_native_fixture_binding.py",
    ):
        (repo / "scripts" / name).write_bytes((REPO_ROOT / "scripts" / name).read_bytes())
    (repo / "oap" / "orders" / AH_ORDER_NAME).write_bytes(AH_ORDER_BYTES)
    if active_order == AG_ORDER_ID:
        (repo / "oap" / "orders" / AG_ORDER_NAME).write_bytes(AG_ORDER_BYTES)
    (repo / "oap" / "active").write_bytes(active_order.encode("ascii") + b"\n")
    return repo


def _ah_git_runner(repo: Path, *, head: str = HEAD, active_order: str = AH_ORDER_ID) -> Any:
    """The fake committed-context git runner (read-only
    queries only) for the AH/AG synthetic repository."""

    def git_runner(args: list[str], cwd: Path) -> bytes:
        if args == ["rev-parse", "HEAD"]:
            return head.encode("ascii")
        if args == ["status", "--porcelain"]:
            return b""
        if args == ["remote", "get-url", "origin"]:
            return b"https://github.com/ulfe-lmi/slaif-local-coding.git\n"
        if args == ["ls-tree", "--name-only", f"{HEAD}:oap/orders"]:
            names = [S_ORDER_NAME]
            if active_order == AH_ORDER_ID:
                names.append(AH_ORDER_NAME)
            else:
                names += [AG_ORDER_NAME, AH_ORDER_NAME]
            return ("\n".join(names) + "\n").encode("ascii")
        if args == ["show", f"{HEAD}:oap/active"]:
            return active_order.encode("ascii") + b"\n"
        if args == ["show", f"{HEAD}:oap/orders/{S_ORDER_NAME}"]:
            return bytes(stl.ORDER_PATH.read_bytes())
        if args == ["show", f"{HEAD}:oap/orders/{AH_ORDER_NAME}"]:
            return AH_ORDER_BYTES
        if args == ["show", f"{HEAD}:oap/orders/{AG_ORDER_NAME}"]:
            return AG_ORDER_BYTES
        raise AssertionError(f"unexpected git args: {args}")

    return git_runner


def _ah_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    world: _AFWorld,
    docker: _AFFakeDocker,
) -> tuple[Any, Any, _AFFakeDocker, Path, Path, list[int]]:
    """The coupled AH composition over the SAME coherent fake
    world: the REAL public NativeOwnerRun over the AH binding
    (the sealed INERT entry exercised as software only)."""
    repo = _ah_repo(tmp_path)
    work = tmp_path / "work"
    control = tmp_path / "control"
    owner_evidence = tmp_path / "evidence" / "ah-owner-evidence.json"
    uid_calls: list[int] = []
    _hermetic(tmp_path, monkeypatch, docker, control, uid_calls)
    git = _ah_git_runner(repo)
    table = stp.FakeTable(world.procs)
    binding = fb.resolve_order_binding(repo, AH_ORDER_ID, HEAD, git_runner=git)
    run = fno.NativeOwnerRun(
        binding,
        repo,
        work,
        owner_evidence,
        control,
        git_runner=git,
        executor=docker,
        table=table,
        worker_pid=WORK_PID,
        bash_pid=BASH_PID,
        tty_foreground_pgrp=WORK_PID,
        identity_reader=_ad_reader,
        proc_root=world.proc_root,
    )
    return run, repo, docker, owner_evidence, control, uid_calls


def test_ag_ah_entry_selection_and_preserved_closed_mapping() -> None:
    """The canonical sealed FUTURE 017-ah native-PTY
    requalification entry selects the SAME owner-UID profile
    through the closed entry mapping (composing the EXISTING
    owner/guarded exact-CID/NativeOwnerRun and devpts
    producer APIs), and every EXISTING entry, path and tag is
    preserved byte-for-byte (the AF tags stay AF-only, even
    equal numeric identities)."""
    # the exact canonical AH constants
    assert frp.AH_ORDER_ID == "017-ah"
    assert frp.AH_ORDER_PATH == "oap/orders/017-ah-owner-uid-native-pty-requalification.md"
    assert frp.AH_OWNER_STATE_SCHEMA == "slaif-017ah-owner-state-v1"
    assert frp.AH_NATIVE_RUN_EVIDENCE_SCHEMA == "slaif-017ah-native-owner-run-evidence-v1"
    assert frp.AH_NATIVE_RUN_SCHEMA == "slaif-017ah-native-owner-run-v1"
    assert frp.AH_OWNER_RUN_SCOPE == "slaif-017ah-owner-uid-scope"
    assert frp.AH_NATIVE_ATTACH_BINDING_SCHEMA == "slaif-017ah-native-attach-binding-v1"
    # the closed entry mapping: the SIX existing entries
    # preserved byte-for-byte, plus AH selecting the SAME
    # owner-UID profile
    assert dict(frp.ENTRY_PROFILES) == {
        "017-s": frp.PROFILE_ORIGINAL,
        "017-x": frp.PROFILE_ORIGINAL,
        "017-y": frp.PROFILE_ORIGINAL,
        frp.AB_ORDER_ID: frp.PROFILE_OWNER_UID,
        frp.AD_ORDER_ID: frp.PROFILE_OWNER_UID,
        frp.AF_ORDER_ID: frp.PROFILE_OWNER_UID,
        frp.AH_ORDER_ID: frp.PROFILE_OWNER_UID,
    }
    assert frp.entry_profile_name("017-s") == frp.PROFILE_ORIGINAL
    assert frp.entry_profile_name("017-x") == frp.PROFILE_ORIGINAL
    assert frp.entry_profile_name("017-y") == frp.PROFILE_ORIGINAL
    assert frp.entry_profile_name(frp.AB_ORDER_ID) == frp.PROFILE_OWNER_UID
    assert frp.entry_profile_name(AD_ORDER_ID) == frp.PROFILE_OWNER_UID
    assert frp.entry_profile_name(AF_ORDER_ID) == frp.PROFILE_OWNER_UID
    # AH carries the owner-UID profile (the production
    # derivation, never a caller-authored view)
    assert frp.entry_profile_name(frp.AH_ORDER_ID) == frp.PROFILE_OWNER_UID
    view = frp.entry_runtime_profile(frp.AH_ORDER_ID, _ad_description())
    assert (view.subject_uid, view.subject_gid) == (SUBJ_UID, SUBJ_GID)
    assert view.exec_user == f"{SUBJ_UID}:{SUBJ_GID}"
    # unknown entries still refuse (AH is a known entry, not a
    # wildcard: nothing else is selectable)
    with pytest.raises(frp.ProfileError, match="profile-entry-unknown"):
        frp.entry_profile_name("017-ae")
    with pytest.raises(frp.ProfileError, match="profile-entry-unknown"):
        frp.entry_profile_name("017-zz")
    # every EXISTING canonical constant/tag preserved byte-for-byte
    assert frp.AB_ORDER_ID == "017-ab"
    assert frp.AB_ORDER_PATH == "oap/orders/017-ab-owner-uid-python-capability-qualification.md"
    assert frp.AB_DRIVER_RECORD == "slaif-017ab-owner-uid-exec-capability-v1"
    assert frp.AB_OWNER_RUN_EVIDENCE_SCHEMA == "slaif-017ab-owner-run-evidence-v1"
    assert frp.AB_OWNER_RUN_SCOPE == "slaif-017ab-owner-uid-scope"
    assert frp.AD_ORDER_ID == "017-ad"
    assert frp.AD_ORDER_PATH == "oap/orders/017-ad-owner-uid-native-handoff-qualification.md"
    assert frp.AD_DRIVER_RECORD == "slaif-017ad-owner-uid-native-handoff-v1"
    assert frp.AD_OWNER_STATE_SCHEMA == "slaif-017ad-owner-state-v1"
    assert frp.AD_NATIVE_RUN_EVIDENCE_SCHEMA == "slaif-017ad-native-owner-run-evidence-v1"
    assert frp.AD_NATIVE_RUN_SCHEMA == "slaif-017ad-native-owner-run-v1"
    assert frp.AD_OWNER_RUN_SCOPE == "slaif-017ad-owner-uid-scope"
    assert frp.AD_EXE_MAX_BYTES == 335544320
    assert frp.AD_EXE_DEADLINE_SECONDS == 10.0
    assert not hasattr(frp, "AD_NATIVE_ATTACH_BINDING_SCHEMA")
    assert frp.AF_ORDER_ID == "017-af"
    assert frp.AF_ORDER_PATH == "oap/orders/017-af-owner-uid-native-pty-qualification.md"
    assert frp.AF_OWNER_STATE_SCHEMA == "slaif-017af-owner-state-v1"
    assert frp.AF_NATIVE_RUN_EVIDENCE_SCHEMA == "slaif-017af-native-owner-run-evidence-v1"
    assert frp.AF_NATIVE_RUN_SCHEMA == "slaif-017af-native-owner-run-v1"
    assert frp.AF_OWNER_RUN_SCOPE == "slaif-017af-owner-uid-scope"
    assert frp.AF_NATIVE_ATTACH_BINDING_SCHEMA == "slaif-017af-native-attach-binding-v1"
    # the distinct AH identity-bearing tags (AH-only, never
    # AF's, even equal numeric identities)
    assert fp.AH_NATIVE_PREP_SCHEMA == "slaif-017ah-native-handoff-prep-v1"
    assert fp.AH_NATIVE_OWNER_SCHEMA == "slaif-017ah-native-owner-evidence-v1"
    assert fp.AH_ATTACH_BINDING_SCHEMA == "slaif-017ah-native-attach-binding-v1"
    assert fno.AH_NATIVE_RUN_SCHEMA == "slaif-017ah-native-owner-run-v1"
    assert flocal.AH_STATE_SCHEMA == "slaif-017ah-owner-state-v1"
    assert flocal.AH_OWNER_RUN_EVIDENCE_SCHEMA == "slaif-017ah-native-owner-run-evidence-v1"
    assert flocal.AH_OWNER_RUN_SCOPE == "slaif-017ah-owner-uid-scope"


def test_ag_ah_refused_under_ag_active_before_admission(tmp_path: Path) -> None:
    """The REAL repository-context validation refuses 017-ah
    under AG-active BEFORE any admission or external work,
    proven only in an owned synthetic repository (the real
    checkout is never touched): the closed canonical map
    carries the AH entry's unique committed order path, the
    active-content law refuses the foreign-active AH binding,
    and the AH admission namespace is never claimed.  The
    ACTUAL real AH order file and namespace stay ABSENT in
    this checkout (the entry is sealed INERT)."""
    # coherence: the binding module's closed map mirrors the
    # canonical entry names owned by the runtime-profile module
    assert fb._CANONICAL_ORDER_PATHS[AH_ORDER_ID] == frp.AH_ORDER_PATH
    # the AG-active synthetic repo: the AH order file is
    # committed at its canonical path, active selects AG
    repo = _ah_repo(tmp_path / "repo", active_order=AG_ORDER_ID)
    git = _ah_git_runner(repo, active_order=AG_ORDER_ID)
    with pytest.raises(fci.FixtureError, match="bind-active-mismatch"):
        fb.resolve_order_binding(repo, AH_ORDER_ID, HEAD, git_runner=git)
    # no admission namespace (the ACTUAL production
    # admission path, including any claim), no journal, no
    # external work
    assert not fb.admission_dir_path(repo, AH_ORDER_ID).exists()
    assert not fb.admission_path(repo, AH_ORDER_ID).exists()
    assert not fb.claim_path(repo, AH_ORDER_ID).exists()
    # the AG binding itself still resolves (the active entry)
    ag_binding = fb.resolve_order_binding(repo, AG_ORDER_ID, HEAD, git_runner=git)
    assert ag_binding.order_id == AG_ORDER_ID
    # the AH entry under ITS OWN active context resolves ONLY at
    # its unique canonical committed order path
    ah_repo = _ah_repo(tmp_path / "ahrepopo")
    ah_git = _ah_git_runner(ah_repo)
    ah_binding = fb.resolve_order_binding(ah_repo, AH_ORDER_ID, HEAD, git_runner=ah_git)
    assert ah_binding.order_path == frp.AH_ORDER_PATH
    # a FOREIGN pattern-matching AH name is a closed refusal
    # BEFORE any admission or owner adoption
    wrong = tmp_path / "wrong" / "repo"
    wrong.parent.mkdir(parents=True)
    wrong_repo = Path(stl._make_local_repo(wrong))
    wrong_name = "017-ah-other-synthetic-name.md"
    (wrong_repo / "oap" / "orders" / wrong_name).write_bytes(AH_ORDER_BYTES)
    (wrong_repo / "oap" / "active").write_bytes(AH_ORDER_ID.encode("ascii") + b"\n")

    def wrong_git(args: list[str], cwd: Path) -> bytes:
        if args == ["rev-parse", "HEAD"]:
            return str(HEAD).encode("ascii")
        if args == ["status", "--porcelain"]:
            return b""
        if args == ["remote", "get-url", "origin"]:
            return b"https://github.com/ulfe-lmi/slaif-local-coding.git\n"
        if args == ["ls-tree", "--name-only", f"{HEAD}:oap/orders"]:
            return (S_ORDER_NAME + "\n" + wrong_name + "\n").encode("ascii")
        if args == ["show", f"{HEAD}:oap/active"]:
            return AH_ORDER_ID.encode("ascii") + b"\n"
        if args == ["show", f"{HEAD}:oap/orders/{wrong_name}"]:
            return AH_ORDER_BYTES
        if args == ["show", f"{HEAD}:oap/orders/{S_ORDER_NAME}"]:
            return bytes(stl.ORDER_PATH.read_bytes())
        raise AssertionError(f"unexpected git args: {args}")

    with pytest.raises(fci.FixtureError, match="bind-order-path-mismatch"):
        fb.resolve_order_binding(wrong_repo, AH_ORDER_ID, HEAD, git_runner=wrong_git)
    assert not fb.admission_dir_path(wrong_repo, AH_ORDER_ID).exists()
    # the ACTUAL real AH order file and namespace stay ABSENT
    # in this checkout (the sealed INERT entry)
    assert list((REPO_ROOT / "oap" / "orders").glob("017-ah-*")) == []
    # the real production admission namespace (repo
    # .oap-local/<order>) is ABSENT in this checkout
    assert not fb.admission_dir_path(REPO_ROOT, AH_ORDER_ID).exists()
    assert not fb.admission_path(REPO_ROOT, AH_ORDER_ID).exists()


def _devpts_probe_argv(
    user: str = f"{SUBJ_UID}:{SUBJ_GID}",
    cid: str = "f" * 64,
    python: tuple[str, ...] = ("python3", "-I", "-S", "-c"),
    body: str = fci.DEVPTS_PROBE,
    prefix: tuple[str, ...] = (),
    suffix: tuple[str, ...] = (),
) -> list[str]:
    return ["docker", "exec", *prefix, "--user", user, cid, *python, body, *suffix]


def test_ag_ah_devpts_probe_guard_carries_ah_and_old_guards_refuse() -> None:
    """The ONE exact NON-PTY devpts probe argv is admitted for
    the canonical 017-ah entry TOO, selected from the owner's
    OWN bound order (the sealed INERT entry carries the same
    frozen authority as AF when later activated): the
    AB/AD/default guards keep the byte-for-byte old closed
    forms and refuse the exact probe and every modified argv,
    and the AF entry's guard is unchanged."""
    profile = frp.owner_runtime_profile(_ad_description())
    assert profile.exec_user == f"{SUBJ_UID}:{SUBJ_GID}"
    ah_matchers = fci._owner_argv_matchers(profile, frp.AH_ORDER_ID)
    af_matchers = fci._owner_argv_matchers(profile, frp.AF_ORDER_ID)
    ad_matchers = fci._owner_argv_matchers(profile, frp.AD_ORDER_ID)
    ab_matchers = fci._owner_argv_matchers(profile, frp.AB_ORDER_ID)
    # the original entries keep the byte-for-byte original
    # module-level matcher tuple (their owners never mint the
    # owner-scoped set)
    original_matchers = fci._ARGV_MATCHERS
    # direct AH guard construction: the SAME shape as the AF
    # tuple — the unchanged old forms plus ONE closed probe
    # matcher, callable without TypeError
    assert len(ah_matchers) == len(af_matchers) == len(ad_matchers) + 1
    ah_probe_matcher = ah_matchers[-1]
    assert callable(ah_probe_matcher)
    # the old forms are BEHAVIORALLY identical across the AH,
    # AF and non-AF owner tuples (compare their decisions over
    # the closed old forms)
    old_forms: list[list[str]] = [
        ["docker", "ps", "-aq", "--filter", "id=" + "a" * 64],  # admitted
        ["docker", "version", "--format", "{{.Server.Version}}"],  # admitted
        [
            "docker",
            "exec",
            "--user",
            f"{SUBJ_UID}:{SUBJ_GID}",
            "f" * 64,
            "python3",
            "-c",
            fci.CONTROLLER_PROBE,
        ],  # admitted (subject user)
        [
            "docker",
            "exec",
            "--user",
            f"{SUBJ_UID}:{SUBJ_GID}",
            "f" * 64,
            "python3",
            fci.EXPORT_CLIENT_PATH,
        ],  # admitted (export)
        [
            "docker",
            "exec",
            "--user",
            f"{SUBJ_UID}:{SUBJ_GID}",
            "f" * 64,
            "python3",
            "-c",
            "print(1)",
        ],  # refused (open program)
        ["docker", "ps", "-a"],  # refused (not the closed form)
    ]
    admitted = 0
    for argv in old_forms:
        for m_ah, m_ad in zip(ah_matchers[:-1], ad_matchers, strict=True):
            assert bool(m_ah(argv)) == bool(m_ad(argv))
        admitted += sum(1 for m in ad_matchers if m(argv))
    assert admitted >= 4  # the positive forms really are admitted
    exact = _devpts_probe_argv()
    assert len(exact) == 10
    # AH admits the exact form (any valid registered-CID-shaped
    # target)
    assert ah_probe_matcher(exact) is True
    assert ah_probe_matcher(_devpts_probe_argv(cid="e" * 64)) is True
    # the AF entry's guard is unchanged
    assert af_matchers[-1](exact) is True
    # the AB/AD/default guards refuse the EXACT new probe
    assert not any(m(exact) for m in ad_matchers)
    assert not any(m(exact) for m in ab_matchers)
    assert not any(m(exact) for m in original_matchers)
    # every modified argv is refused by EVERY guard, AH
    # included (the closed form is EXACT)
    for mutated in (
        _devpts_probe_argv(prefix=("-it",)),  # a PTY attach contaminates
        _devpts_probe_argv(user="21001:21001"),  # the controller user
        _devpts_probe_argv(user="21002:21002"),  # the original profile user
        _devpts_probe_argv(prefix=("--env-file", "/tmp/slaif-env")),  # env-file
        [
            "docker",
            "exec",
            "--user",
            f"{SUBJ_UID}:{SUBJ_GID}",
            "f" * 64,
            "python3",
            "-I",
            "-S",
            "-e",
            "A=1",
            "-c",
            fci.DEVPTS_PROBE,
        ],  # -e
        _devpts_probe_argv(python=("python3", "-S", "-c")),  # no -I
        _devpts_probe_argv(python=("python3", "-I", "-c")),  # no -S
        _devpts_probe_argv(python=("python3.12", "-I", "-S", "-c")),  # alternate binary
        _devpts_probe_argv(body="print(1)"),  # a different probe body
        _devpts_probe_argv(suffix=("--flag",)),  # an extra argument
        exact[:-1],  # a missing argument
        _devpts_probe_argv(cid="xyz"),  # a non-CID target
    ):
        assert not any(m(mutated) for m in ah_matchers)
        assert not any(m(mutated) for m in af_matchers)
        assert not any(m(mutated) for m in ad_matchers)
        assert not any(m(mutated) for m in original_matchers)


def _attach_observations() -> tuple[Any, Any, Any]:
    """The closed devpts pair (the empty baseline + ONE owned
    slave) over the shared fixture model, built through the
    closed consumer (pure data, no probe execution)."""
    base: dict[str, object] = {
        "record": fci.DEVPTS_PROBE_RECORD,
        "status": "pass",
        "uid": SUBJ_UID,
        "namespace": list(AF_DEVPTS_NS),
        "policy": {
            "fstype": "devpts",
            "gid": AF_DEVPTS_POLICY[0],
            "mode": AF_DEVPTS_POLICY[1],
        },
        "isolation": {"site": False, "startup": False},
        "slave_rows": [],
    }
    major, minor, ino, mode, uid, gid = AF_ALLOC
    obs = dict(base)
    obs["slave_rows"] = [[str(minor), major, minor, ino, mode, uid, gid]]

    def _record(obj: dict[str, object]) -> Any:
        return fp.parse_devpts_inventory_record(
            (json.dumps(obj, separators=(",", ":")) + "\n").encode("ascii")
        )

    baseline = _record(base)
    observation = _record(obs)
    allocation = fp.derive_attach_allocation(
        baseline.inventory, observation.inventory, subject_uid=SUBJ_UID
    )
    return baseline, observation, allocation


def test_ag_ah_attach_binding_tag_pair_cross_entry_refused(tmp_path: Path) -> None:
    """The DISTINCT attach-binding tags stay entry-pure in
    BOTH directions (even for equal-numeric identities): the
    producer mints the binding's OWN canonical tag, and the
    closed consumer refuses any cross-entry tag/binding pair
    BEFORE any authority is derived — a copied or replayed
    record of the other entry never mints authority."""
    af_repo = _af_repo(tmp_path / "af")
    af_git = _af_git_runner(af_repo)
    af_binding = fb.resolve_order_binding(af_repo, AF_ORDER_ID, HEAD, git_runner=af_git)
    ah_repo = _ah_repo(tmp_path / "ah")
    ah_git = _ah_git_runner(ah_repo)
    ah_binding = fb.resolve_order_binding(ah_repo, AH_ORDER_ID, HEAD, git_runner=ah_git)
    baseline, observation, allocation = _attach_observations()
    identity = _ad_identity_dict()
    cid = "f" * 64
    af_record = fp.attach_binding_record(
        baseline=baseline,
        observation=observation,
        allocation=allocation,
        binding=af_binding,
        identity=identity,
        cid=cid,
    )
    ah_record = fp.attach_binding_record(
        baseline=baseline,
        observation=observation,
        allocation=allocation,
        binding=ah_binding,
        identity=identity,
        cid=cid,
    )
    assert af_record["record"] == fp.AF_ATTACH_BINDING_SCHEMA
    assert ah_record["record"] == fp.AH_ATTACH_BINDING_SCHEMA
    # positive controls: each tag parses against ITS OWN binding
    assert fp.parse_attach_binding_record(af_record, af_binding).expected_tty_nr == AF_TTY_NR
    assert fp.parse_attach_binding_record(ah_record, ah_binding).expected_tty_nr == AF_TTY_NR
    # cross-entry refusals: the AF tag never carries an AH
    # binding and vice versa
    with pytest.raises(fci.FixtureError, match="prep-attach-binding-mismatch"):
        fp.parse_attach_binding_record(af_record, ah_binding)
    with pytest.raises(fci.FixtureError, match="prep-attach-binding-mismatch"):
        fp.parse_attach_binding_record(ah_record, af_binding)
    # the SAME cross-entry pair in the retained-dict binding
    # form is refused identically (the dict is validated by
    # the full closed grammar, then compared exactly)
    with pytest.raises(fci.FixtureError, match="prep-attach-binding-mismatch"):
        fp.parse_attach_binding_record(af_record, ah_binding.to_record())
    with pytest.raises(fci.FixtureError, match="prep-attach-binding-mismatch"):
        fp.parse_attach_binding_record(ah_record, af_binding.to_record())


def test_ag_ah_full_public_native_lifecycle_with_kernel_zero_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The ORDER-REQUIRED coupled public NativeOwnerRun
    lifecycle containing UNRELATED kernel rows: the coherent
    fake world carries a well-formed zero pgrp/session kernel
    observation across prepare/observe/stop/register/finish/
    restore/retention, and the AH entry's full public
    composition still passes end to end — the zero row is
    observed but never adopted (not a group member, not a
    tool session, never a signal target or authority frame,
    never mutated), and the AH's OWN distinct identity-
    bearing record tags are carried through every retained
    layer (state, prep snapshot, attach binding, native-owner
    facts through the REAL finalization dispatcher, native-
    run terminal, owner evidence) with the SAME frozen
    identity.  NO actual Docker/native/PTY operation: fake
    proof only — the AH entry stays sealed INERT in this
    round."""
    import copy

    world, fake = _af_new_world(tmp_path)
    kernel_before = _kernel_proc()
    world.procs[KERNEL_PID] = dict(kernel_before)
    run, repo, _f, owner_evidence, _c, uid_calls = _ah_run(
        tmp_path, monkeypatch, world=world, docker=fake
    )
    with _owned_run(run):
        binding = run.binding
        identity = _ad_identity_dict()
        native_out = tmp_path / "evidence" / "ah-native-run-record.json"
        proc_root = world.proc_root
        # the ONE shared run context across the whole lifecycle
        ctx_before = run.owner._owner_context
        anchor_before = run.owner.deadline.anchor
        ledger_before = run.owner.ledger

        # start/prepare/observe/stop/baseline/launch/derive
        # (the kernel zero row is present through every one
        # of these traversals)
        _af_prep(run, world)

        # the zero observation row is OBSERVED but never
        # adopted: not a group member, not a tool session,
        # and no zero group appears anywhere in the collected
        # facts
        facts = fp.collect_worker_group(stp.FakeTable(world.procs), WORK_PID, BASH_PID, WORK_PID)
        assert KERNEL_PID not in [m.pid for m in facts.members]
        assert KERNEL_PID not in {m.pid for _g, ms in facts.tool_sessions for m in ms}
        assert all(g != 0 for g, _count in facts.session_other_groups)

        # the DISTINCT AH state tag on disk (the v1 reader
        # never sees it — the tag is entry-scoped)
        ah_state = flocal._state_record(_c, entry_order=AH_ORDER_ID)
        assert ah_state is not None
        assert ah_state["record"] == flocal.AH_STATE_SCHEMA
        assert ah_state["order"] == AH_ORDER_ID
        assert ah_state["identity"]["subject_uid"] == SUBJ_UID

        calls: list[tuple[Any, float]] = []
        monkeypatch.setattr(fno, "build_ad_native_channel", _af_channel_factory(world, calls))
        end_before = run.owner.deadline.anchor
        snapshot = run.register_subject(NAT_PID, _af_expectation(run))
        # the factory saw EXACTLY this owner's registered CID
        # and the SAME absolute owner END
        assert calls == [(run.owner.target_cid, end_before)]
        # the measured subject frame: the owned allocation's
        # derived tty_nr, bound by the collector's OWN pty
        assert snapshot["subject"]["tty"] == AF_TTY_NR
        assert snapshot["subject"]["pty_matched"] is True
        assert snapshot["subject"]["cid_membership"] == "cid-scoped"
        assert run.workflow.subject_receipt is not None
        # the DISTINCT AH tag at the retained prep layer (the
        # SAME frozen identity carried through)
        assert snapshot["record"] == fp.AH_NATIVE_PREP_SCHEMA
        assert snapshot["identity"]["subject_uid"] == SUBJ_UID
        # the attach phase used EXACTLY two bounded probes
        # (the empty baseline + the allocation observation);
        # a later observe reuses the retained receipt and
        # never re-measures
        assert world.devpts_probe_calls == 2
        run.observe()
        assert world.devpts_probe_calls == 2

        # the EXPLICIT fake native exit before the positive
        # finish: absence only (no exit code or cause)
        world.exit_native()
        assert world.native_exits == 1
        assert NAT_PID not in world.procs
        assert not (proc_root / str(NAT_PID)).exists()
        assert run.workflow.subject_receipt is not None

        # finish: the REAL finish/export/teardown over the
        # fake platform — the kernel zero row is present in
        # the host table through the whole convergence
        run.finish()
        assert run.owner.terminal_outcome == "pass"
        _join_run(run)
        assert fake.last_quiesce is not None
        assert fake.last_quiesce["owned_subject_stopped"] is True
        assert run.owner.owned_members_before == ((CTL_PID, CTL_START, CTL_UID),)
        assert run.owner.owned_members_after == ((CTL_PID, "verified-gone"),)
        # the unrelated same-UID worker survived the whole
        # run with the SAME uid/gid; the kernel zero row
        # survived UNCHANGED (observation data is never
        # mutated)
        worker = world.procs[WORK_PID]
        assert fp.parse_proc_status(worker["status"]) == (SUBJ_UID, SUBJ_UID, ())
        assert world.procs[KERNEL_PID] == kernel_before

        # the operator restores the SAME worker job (stat-
        # only) with the kernel row still present
        world.procs[WORK_PID] = _worker_proc("S", tpgid=WORK_PID, start=WORK_START)

        # publish: the DISTINCT identity-bearing AH terminal
        # record (owner evidence FIRST, native record SECOND,
        # the nested protected AH attach record, same-attempt
        # finalization LAST)
        record_doc = run.publish_native(native_out)
        assert record_doc["record"] == fno.AH_NATIVE_RUN_SCHEMA
        assert record_doc["identity"] == identity
        assert record_doc["owner_outcome"] == "pass"
        assert record_doc["attempt"] == "running"  # pending, never a predicted token
        assert record_doc["subject_measured"] is True
        assert record_doc["stop_recorded"] is True
        assert record_doc["native_refusal"] is None
        assert record_doc["verdict"] == {"ready": True, "reasons": []}
        fno.parse_native_run_record(record_doc)
        facts2 = fp.parse_native_owner_facts(record_doc["native_record"])
        assert facts2.schema == fp.AH_NATIVE_OWNER_SCHEMA
        assert facts2.identity == (SUBJ_UID, SUBJ_GID, (SUBJ_GID,))
        assert facts2.order == AH_ORDER_ID
        assert facts2.source_head == HEAD
        assert facts2.run_id == binding.run_id
        assert facts2.cid == run.owner.target_cid
        assert facts2.native_started is True
        assert facts2.native_ready is True
        # the nested PROTECTED AH attach record: the closed
        # consumer re-derives the allocation from the two
        # embedded inventories against the OUTER binding
        # record (a copied/replayed record never mints
        # authority)
        attach = record_doc["attach_binding"]
        assert attach is not None
        rederived = fp.parse_attach_binding_record(attach, run.binding)
        assert attach["record"] == fp.AH_ATTACH_BINDING_SCHEMA
        assert attach["expected_tty_nr"] == AF_TTY_NR
        assert attach["namespace"] == list(AF_DEVPTS_NS)
        assert attach["cid"] == run.owner.target_cid
        assert rederived.major == AF_ALLOC[0]
        assert rederived.minor == AF_ALLOC[1]
        assert rederived.inode == AF_ALLOC[2]
        assert rederived.mode == AF_ALLOC[3]
        st = native_out.stat()
        assert (st.st_mode & 0o777) == 0o600 and st.st_uid == os.getuid()

        # the same-order journal is terminal pass ONLY after
        # the protected publication (the real finalize token
        # in RAM)
        assert run.finalize_attempt() == "finalized"
        record = fb.read_admission_record(repo, AH_ORDER_ID)
        assert record["attempts"] == [{"head": HEAD, "run_id": binding.run_id, "status": "pass"}]

        # the owner's OWN distinct AH terminal evidence: the
        # SAME frozen identity (compared, never rebased), the
        # exact-CID teardown proof, the bound order —
        # validated by the REAL AH evidence validator
        ev_raw = json.loads(owner_evidence.read_bytes().decode("ascii"))
        flocal.validate_ah_owner_run_evidence(ev_raw)
        assert ev_raw["record"] == flocal.AH_OWNER_RUN_EVIDENCE_SCHEMA
        assert ev_raw["scope"] == flocal.AH_OWNER_RUN_SCOPE
        assert ev_raw["order"] == AH_ORDER_ID
        assert ev_raw["status"] == "pass"
        assert ev_raw["identity"] == identity
        assert ev_raw["teardown_proof"] == "exact-cid-membership"
        assert ev_raw["fixture_consumed_by"] == "unobserved"

        # the same frozen identity across EVERY retained
        # layer of the same attempt (no rebase anywhere in
        # the composition)
        assert (
            snapshot["identity"]
            == identity
            == record_doc["identity"]
            == ev_raw["identity"]
            == attach["identity"]
        )

        # ONE shared run context: the SAME frozen owner
        # context, END anchor and ledger across the whole
        # lifecycle (compared, never rebased or replaced)
        assert run.owner._owner_context is ctx_before
        assert run.owner.deadline.anchor == anchor_before
        assert run.owner.ledger is ledger_before
        # no global subject-UID scan ever ran on the
        # owner-UID path (the trap would have raised)
        assert SUBJ_UID not in uid_calls
        assert CTL_UID in uid_calls

        # the EXACT tag-pair law across entries over the
        # retained AH native record: a relabeled order or tag
        # is a closed refusal, and the AH record reaches the
        # REAL parser through the public finalization
        # dispatcher (not a direct codec call alone)
        native_record = record_doc["native_record"]
        with _owned_run(run):
            verdict = run.workflow.finalize(native_record)
            assert verdict.ready is True and verdict.reasons == ()
            foreign_order = copy.deepcopy(native_record)
            foreign_order["order"] = AF_ORDER_ID
            with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
                fp.parse_native_owner_facts(foreign_order)
            af_tag = copy.deepcopy(native_record)
            af_tag["record"] = fp.AF_NATIVE_OWNER_SCHEMA
            with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
                fp.parse_native_owner_facts(af_tag)
            # the dispatcher itself refuses the OTHER
            # entry's tag for this AH-bound workflow (the
            # AF-tagged record is dispatched to the shared
            # consumer, whose tag-pair law refuses it)
            with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
                run.workflow.finalize(af_tag)
            original_tag = copy.deepcopy(native_record)
            original_tag["record"] = fp.NATIVE_OWNER_SCHEMA
            original_tag.pop("identity")
            with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
                fp.parse_native_owner_facts(original_tag)
            with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
                run.workflow.finalize(original_tag)
            # the original tag of the AF entry is refused too
            original_af = copy.deepcopy(original_tag)
            original_af["order"] = AF_ORDER_ID
            with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
                fp.parse_native_owner_facts(original_af)
            # the unmutated retained record remains the ready
            # positive control
            verdict2 = run.workflow.finalize(native_record)
            assert verdict2.ready is True and verdict2.reasons == ()


def test_ag_ah_zero_frames_never_earn_stop_authority_in_composition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The useful coupled negative: a ZERO pgrp/session
    observation frame can never earn STOP authority inside
    the REAL public composition — a zeroed Bash frame (same
    pid/birth) passes the baseline birth binding but is
    refused by the stop collector's OWN zero-group law
    (the B.pgrp AND B.session checks), and a zeroed Worker
    frame is refused by the baseline binding itself; neither
    refusal commits a receipt, and the won attempt converges
    honest ABORT (the unrelated kernel zero observation row
    stays present and is never adopted)."""
    world, fake = _af_new_world(tmp_path)
    world.procs[KERNEL_PID] = _kernel_proc()
    run, repo, _f, _ev, _c, _u = _ah_run(tmp_path, monkeypatch, world=world, docker=fake)
    with _owned_run(run):
        run.start()
        run.prepare()
        run.observe()
        world.procs[WORK_PID] = _worker_proc("T", tpgid=BASH_PID, start=WORK_START)
        # 1) the BASH frame zeroed (same pid/birth 100): the
        #    baseline binding passes, the stop collector's
        #    zero-group law refuses — no stop receipt
        world.procs[BASH_PID] = {
            "stat": stp.stat_line(BASH_PID, "bash", "S", 1, 0, 0, stp.TTYS, 0, 100),
            "cmdline": b"bash\0",
            "status": stp.bash_proc(BASH_PID, state="S", pgrp=BASH_PID)["status"],
        }
        with pytest.raises(fci.FixtureError, match="prep-stop-unobserved"):
            run.record_stop()
        assert run.workflow._stop_receipt is None
        # 2) the WORKER frame zeroed (same pid/birth): the
        #    baseline binding itself refuses the zeroed W
        #    group/session
        world.procs[WORK_PID] = {
            "stat": stp.stat_line(
                WORK_PID, "codex", "T", BASH_PID, 0, 0, stp.TTYS, BASH_PID, WORK_START
            ),
            "cmdline": stp.CODEX_CMDLINE,
            "status": stp.status_bytes(SUBJ_UID, SUBJ_UID),
        }
        with pytest.raises(fci.FixtureError, match="prep-worker-invalid"):
            run.record_stop()
        assert run.workflow._stop_receipt is None
        _join_run(run)
        assert run.owner.terminal_outcome == "aborted"
        record = fb.read_admission_record(repo, AH_ORDER_ID)
        assert record["attempts"] == [
            {"head": HEAD, "run_id": run.binding.run_id, "status": "aborted"}
        ]
