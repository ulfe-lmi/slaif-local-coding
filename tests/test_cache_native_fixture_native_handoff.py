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
import time
import sys
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
stp = _load_test_module("oap_ac_stp", REPO_ROOT / "tests" / "test_cache_native_fixture_native_prep.py")

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
    return fp._ad_identity_substructure_from_triple((SUBJ_UID, SUBJ_GID, (SUBJ_GID,)))


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
    active_name = AD_ORDER_NAME if active_order == AD_ORDER_ID else AC_ORDER_NAME

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
        "stat": stp.stat_line(WORK_PID, "codex", state, BASH_PID, WORK_PID, 99, stp.TTYS, tpgid, start),
        "cmdline": stp.CODEX_CMDLINE,
        "status": stp.status_bytes(SUBJ_UID, SUBJ_UID),
    }


class _ADWorld(aa._World):
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
        (d / "cgroup").write_text(
            f"0::/system.slice/docker-{self.cid}.scope\n", encoding="ascii"
        )
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


class _ADFakeDocker(aa.AAFakeDocker):
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
        assert prepared["identity"] == identity == snapshot["identity"] == ev_raw["identity"] == record_doc["identity"]

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


def test_ad_unknown_lifetime_frame_refuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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
        foreign["identity"] = fp._ad_identity_substructure_from_triple(
            (1003, 1004, (1004,))
        )
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
        60: stp.subject_proc(
            60, cgroup=stp.CID, uid=SUBJ_UID, gid=SUBJ_GID, groups=(SUBJ_GID,)
        )
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
) -> tuple[Any, Any, _ADWorld, _ADFakeDocker, Any, dict]:
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
        if args == ["rev-parse", "HEAD"]:
            return HEAD.encode("ascii")
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
            "worker": {"pid": 50, "state": "S", "pgrp": 50, "session": 50, "tty": 8, "start_time": 500},
            "bash": {"pid": 40, "state": "S", "pgrp": 40, "session": 40, "tty": 8, "start_time": 100},
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
    snapshot["binding"] = dict(
        ad_binding, order_path="oap/orders/017-ad-other-synthetic-name.md"
    )
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
    terminal["binding"] = dict(
        ad_binding, order_path="oap/orders/017-ad-other-synthetic-name.md"
    )
    with pytest.raises(fci.FixtureError, match="native-owner-record-malformed"):
        fno.parse_native_run_record(terminal)
