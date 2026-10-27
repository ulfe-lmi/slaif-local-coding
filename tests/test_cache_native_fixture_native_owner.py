"""Public native-owner lifecycle composition tests (order 017-v).

These tests drive the ACTUAL public composition
(``cache_native_fixture_native_owner.NativeOwnerRun``) over the
ACTUAL ``LocalFixtureOwner`` and the ACTUAL public staged
``NativeHandoffWorkflow`` with injected FAKE external operations
only: fake git, fake docker executor, fake process-table seam and
owned synthetic repositories.  No test launches docker, a
container, a namespace or the native binary; no worker stop or
host signal; no real fixture admission in the real checkout.
The owner's own exact-owned sentinel child (the same tiny
Python child the S local suite uses) is reaped by the owner's
own terminal cleanup.

Covered: the full public positive lifecycle (start -> prepare ->
observe -> measured stop -> staged subject registration ->
observe -> finish/export/teardown -> restore -> publish_native)
with the same CID bound across all phases and the measured
subject removed by the exact CID teardown; the owner's DISTINCT
native-scope terminal evidence (no historical S whole-run false
assertions); the honest publication ordering (the pass attempt
is pending in the retained record, finalized only after the
protected native record is retained); and the public negatives
(bad binding type, exhausted/stale admission, staged
registration refusals, prepare-only honesty, owner-failure and
abort honesty, the native-scope closed validator).
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import json
import os
import socket
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


stl = _load_test_module("oap_v_stl", REPO_ROOT / "tests" / "test_cache_native_fixture_local.py")
stp = _load_test_module(
    "oap_v_stp", REPO_ROOT / "tests" / "test_cache_native_fixture_native_prep.py"
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
model = fci.model

HEAD = stl.HEAD
S_ORDER_NAME = Path(stl.ORDER_PATH).name
V_ORDER_ID = "017-v"
V_ORDER_NAME = f"{V_ORDER_ID}-synthetic-native-owner-public-lifecycle.md"
V_ORDER_BYTES = b"# synthetic V order (fake seam only)\n"
FAKE_BINARY = hashlib.sha256(b"slaif-fake-native-binary").hexdigest()


def _v_repo(base: Path) -> Path:
    """The S-shaped synthetic repo, re-activated as 017-v: the
    committed order set gains the UNIQUE synthetic V order and
    oap/active selects 017-v (disk and committed)."""
    repo = Path(stl._make_local_repo(base))
    (repo / "oap" / "orders" / V_ORDER_NAME).write_bytes(V_ORDER_BYTES)
    (repo / "oap" / "active").write_bytes(V_ORDER_ID.encode("ascii") + b"\n")
    return repo


def _v_git_runner(repo: Path, *, head: str = HEAD) -> Any:
    """The fake committed-context git runner for the V-shaped
    synthetic repository (read-only queries only)."""

    def git_runner(args: list[str], cwd: Path) -> bytes:
        if args == ["rev-parse", "HEAD"]:
            return head.encode("ascii")
        if args == ["status", "--porcelain"]:
            return b""
        if args == ["remote", "get-url", "origin"]:
            return b"https://github.com/ulfe-lmi/slaif-local-coding.git\n"
        if args == ["ls-tree", "--name-only", f"{HEAD}:oap/orders"]:
            return (S_ORDER_NAME + "\n" + V_ORDER_NAME + "\n").encode("ascii")
        if args == ["show", f"{HEAD}:oap/active"]:
            return V_ORDER_ID.encode("ascii") + b"\n"
        if args == ["show", f"{HEAD}:oap/orders/{S_ORDER_NAME}"]:
            return bytes(stl.ORDER_PATH.read_bytes())
        if args == ["show", f"{HEAD}:oap/orders/{V_ORDER_NAME}"]:
            return V_ORDER_BYTES
        raise AssertionError(f"unexpected git args: {args}")

    return git_runner


def _hermetic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fake: Any, control: Path) -> None:
    """The hermetic local environment over the CANONICAL module
    instances (the same law as the S local suite)."""
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


def _world() -> tuple[Any, dict[int, dict[str, Any]]]:
    """The fake process world: bash 40, worker 50 (foreground),
    and the native subject 60 HELD OUT (the staged law: the
    subject is not in the world until the operator launches it
    after the measured stop)."""
    table, procs = stp._lifecycle_table()
    procs.pop(60)
    return table, procs


def _run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    docker: Any | None = None,
    executor: Any = None,
    table: Any | None = None,
    procs: dict[int, dict[str, Any]] | None = None,
    git: Any | None = None,
) -> tuple[Any, Any, Any, Path, Path]:
    repo = _v_repo(tmp_path / "repo")
    work = tmp_path / "work"
    control = tmp_path / "control"
    owner_evidence = tmp_path / "evidence" / "native-owner-evidence.json"
    fake = docker if docker is not None else stl.LocalFakeDocker()
    _hermetic(tmp_path, monkeypatch, fake, control)
    if git is None:
        git = _v_git_runner(repo)
    if table is None:
        table, procs = _world()
    binding = fb.resolve_order_binding(repo, V_ORDER_ID, HEAD, git_runner=git)
    run = fno.NativeOwnerRun(
        binding,
        repo,
        work,
        owner_evidence,
        control,
        git_runner=git,
        executor=executor if executor is not None else fake,
        table=table,
        worker_pid=50,
        bash_pid=40,
        tty_foreground_pgrp=50,
    )
    return run, repo, fake, owner_evidence, control


def _join_run(run: Any) -> None:
    """Bounded reap: an owner that has NOT converged (still held,
    e.g. a registration-refusal test) first receives the bounded
    EXACT-OWNER abort over its protected interface (never a host
    signal), then joins; a converged owner is reaped as-is."""
    thread = run._thread
    if thread is None:
        return
    if thread.is_alive() and not run.owner._converged:
        with contextlib.suppress(Exception):
            flocal._control_client(run._control_dir, "abort", run._run_id, timeout=15.0)
    thread.join(60.0)
    assert not thread.is_alive(), "owner thread did not converge after bounded abort"


# -- the full public positive lifecycle (fake seams only) ----------------------
def test_full_public_native_lifecycle_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    table, procs = _world()
    fake = stl.LocalFakeDocker()
    run_holder: dict[str, Any] = {}

    def executor(argv: list[str], timeout: float) -> Any:
        run = run_holder.get("run")
        # the exact CID teardown removes the native subject from
        # the coupled process world (the fake side effect that
        # stands for the measured teardown on the real backend)
        if (
            run is not None
            and run.owner.target_cid is not None
            and argv[:2] == ["docker", "rm"]
            and argv[-1] == run.owner.target_cid
        ):
            procs.pop(60, None)
        return fake(argv, timeout)

    run, repo, fake, owner_evidence, control = _run(
        tmp_path, monkeypatch, docker=fake, executor=executor, table=table, procs=procs
    )
    run_holder["run"] = run
    binding = run.binding
    native_out = tmp_path / "evidence" / "native-run-record.json"

    # 1. start: the owner publishes the binding's minted run id
    run_id = run.start()
    assert run_id == binding.run_id == run.owner.run_id

    # 2. prepare: the exact target CID is held (unconsumed); the
    #    workflow freezes the W/B baseline with NO predicted
    #    subject (staged registration)
    prepared = run.prepare()
    assert run.owner.target_cid is not None
    assert run.workflow.subject_receipt is None
    assert run.workflow.stop_receipt is None
    # the bound attempt is running in the order namespace
    record = fb.read_admission_record(repo, V_ORDER_ID)
    assert record["attempts"] == [{"head": HEAD, "run_id": binding.run_id, "status": "running"}]
    # the frozen baseline is the measured worker job, bound to
    # the binding's own run identity
    assert prepared["group"]["worker"]["pid"] == 50
    assert prepared["group"]["worker"]["state"] == "S"
    assert prepared["binding"]["run_id"] == binding.run_id
    assert prepared["binding"]["order_id"] == V_ORDER_ID

    # 3. held observation (non-consuming, idempotent)
    run.observe()
    run.observe()

    # 4. the operator stops the worker (the measured stop event)
    procs[50] = stp._worker_proc("T", tpgid=40)
    stop = run.record_stop()
    assert run.workflow.stop_receipt is stop

    # 5. the operator launches the native subject bound to the
    #    owner's OWN registered CID (independent source)
    procs[60] = stp.subject_proc(60, cgroup=str(run.owner.target_cid))
    expectation = fp.SubjectExpectation(
        cid=str(run.owner.target_cid),
        binary_sha256=FAKE_BINARY,
        run_id=binding.run_id,
        min_start_time=400,
        expected_tty=stp.TTYS,
    )
    channel = stp.FakeCidScopedTable(str(run.owner.target_cid), procs, exe_digest=FAKE_BINARY)
    snapshot = run.register_subject(60, expectation, channel=channel)
    assert snapshot["subject"] is not None
    identity = run.workflow.subject_receipt
    assert identity is not None
    assert identity.cid_membership == "cid-scoped"
    assert identity.binary_verified is True
    assert identity.pty_matched is True

    # 6. observe again: the retained receipt is never re-measured
    run.observe()

    # 7. finish: the REAL finish/export/teardown over the fake
    #    platform; the exact CID removal removes the subject
    run.finish()
    assert 60 not in procs
    assert run.owner.terminal_outcome == "pass"
    _join_run(run)

    # 8. the operator restores the SAME worker job
    procs[50] = stp._worker_proc("S", tpgid=50)

    # 9. publish: the DISTINCT native-scope terminal record
    record_doc = run.publish_native(native_out)

    # the retained record: honest pending journal state, measured
    # prerequisites, the bound native record, the ready verdict
    assert record_doc["owner_outcome"] == "pass"
    assert record_doc["attempt"] == "running"  # pending, never a predicted token
    assert record_doc["subject_measured"] is True
    assert record_doc["stop_recorded"] is True
    assert record_doc["native_refusal"] is None
    assert record_doc["verdict"] == {"ready": True, "reasons": []}
    facts = fp.parse_native_owner_facts(record_doc["native_record"])
    assert facts.order == V_ORDER_ID
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
    record = fb.read_admission_record(repo, V_ORDER_ID)
    assert record["attempts"] == [{"head": HEAD, "run_id": binding.run_id, "status": "pass"}]

    # the owner's OWN distinct native-scope terminal evidence:
    # validated closed record, no historical S whole-run false
    # assertions, the bound order (never relabeled as S)
    ev_raw = json.loads(owner_evidence.read_bytes().decode("ascii"))
    flocal.validate_native_owner_run_evidence(ev_raw)
    assert ev_raw["record"] == flocal.NATIVE_OWNER_RUN_EVIDENCE_SCHEMA
    assert ev_raw["scope"] == flocal.NATIVE_OWNER_RUN_SCOPE
    assert ev_raw["order"] == V_ORDER_ID
    assert ev_raw["status"] == "pass"
    assert ev_raw["fixture_consumed_by"] == "unobserved"
    assert ev_raw["prepared"]["disposition"] == "finished-unconsumed"
    for key in ("native_started", "worker_stopped", "codex_invoked", "native_ready"):
        assert key not in ev_raw
    assert "image_identity_vs_ci" not in ev_raw

    # the fake platform never saw an external action beyond the
    # owner's own docker surface; the subject world is clean
    assert 60 not in procs
    # the restored worker runs again in its OWN foreground group
    assert procs[50]["stat"].split()[2] == "S"
    assert int(procs[50]["stat"].split()[7]) == 50  # tpgid: own foreground group


# -- public negatives ----------------------------------------------------------
def test_binding_must_be_verified_order_run_binding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _v_repo(tmp_path / "repo")
    with pytest.raises(fci.FixtureError, match="native-owner-binding-invalid"):
        fno.NativeOwnerRun(
            "not-a-binding", repo, tmp_path / "work", tmp_path / "owner.json", tmp_path / "control"
        )
    # refused before any mutation: no admission namespace
    assert not (repo / ".oap-local").exists()


def test_exhausted_admission_refuses_second_run_before_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run, repo, fake, _evidence, _control = _run(tmp_path, monkeypatch)
    try:
        run.start()
        run.prepare()
        run.finish()
        _join_run(run)
        run.publish_native(tmp_path / "evidence" / "native-run-record.json")
    finally:
        _join_run(run)
    record_before = fb.read_admission_record(repo, V_ORDER_ID)
    assert record_before["attempts"][0]["status"] == "pass"

    # a fresh, verified binding for the SAME order: the one-attempt
    # law refuses BEFORE the owner exists (no external action)
    binding2 = fb.resolve_order_binding(repo, V_ORDER_ID, HEAD, git_runner=_v_git_runner(repo))
    with pytest.raises(fci.FixtureError, match="bind-attempt-exhausted"):
        fno.NativeOwnerRun(
            binding2,
            repo,
            tmp_path / "work2",
            tmp_path / "owner2.json",
            tmp_path / "control2",
            git_runner=_v_git_runner(repo),
            executor=fake,
            table=stp.FakeTable({}),
        )
    record_after = fb.read_admission_record(repo, V_ORDER_ID)
    assert record_after == record_before


def test_stale_head_binding_refused_before_any_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _v_repo(tmp_path / "repo")
    binding = fb.resolve_order_binding(repo, V_ORDER_ID, HEAD, git_runner=_v_git_runner(repo))
    stale = _v_git_runner(repo, head="e" * 40)
    calls: list[list[str]] = []

    def fake_exec(argv: list[str], timeout: float) -> Any:
        calls.append(list(argv))
        raise AssertionError("stale binding must not reach the executor")

    with pytest.raises(fci.FixtureError, match="bind-head-drift"):
        fno.NativeOwnerRun(
            binding,
            repo,
            tmp_path / "work",
            tmp_path / "owner.json",
            tmp_path / "control",
            git_runner=stale,
            executor=fake_exec,
            table=stp.FakeTable({}),
        )
    assert calls == []
    assert not (tmp_path / "work").exists()
    assert not (tmp_path / "owner.json").exists()


def test_register_before_prepare_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run, _repo, _fake, _evidence, _control = _run(tmp_path, monkeypatch)
    expectation = fp.SubjectExpectation(
        cid=stp.CID,
        binary_sha256=FAKE_BINARY,
        run_id=run.binding.run_id,
        min_start_time=400,
        expected_tty=stp.TTYS,
    )
    # this owner's own registration is not measured yet: the
    # owner-bound check closes before the workflow's phase gate
    with pytest.raises(fci.FixtureError, match="native-owner-registration-unmeasured"):
        run.register_subject(60, expectation)


def test_register_before_stop_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run, _repo, _fake, _evidence, _control = _run(tmp_path, monkeypatch)
    try:
        run.start()
        run.prepare()
        expectation = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256=FAKE_BINARY,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        with pytest.raises(fci.FixtureError, match="prep-stop-not-recorded"):
            run.register_subject(60, expectation)
    finally:
        _join_run(run)


def test_double_registration_and_resumed_worker_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    table, procs = _world()
    run, _repo, _fake, _evidence, _control = _run(tmp_path, monkeypatch, table=table, procs=procs)
    try:
        run.start()
        run.prepare()
        procs[50] = stp._worker_proc("T", tpgid=40)
        run.record_stop()
        procs[60] = stp.subject_proc(60, cgroup=str(run.owner.target_cid))
        expectation = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256=FAKE_BINARY,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        channel = stp.FakeCidScopedTable(str(run.owner.target_cid), procs, exe_digest=FAKE_BINARY)
        run.register_subject(60, expectation, channel=channel)
        # the registered identity is immutable
        with pytest.raises(fci.FixtureError, match="prep-subject-registered"):
            run.register_subject(60, expectation, channel=channel)
        # a RESUMED worker (or any current-phase drift) at a later
        # registration attempt is refused by the CURRENT stop
        # predicate — the retained historical stop receipt is
        # never replaced
        procs[50] = stp._worker_proc("S", tpgid=50)
        procs[70] = stp.subject_proc(70, cgroup=str(run.owner.target_cid))
        foreign = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256=FAKE_BINARY,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        with pytest.raises(fci.FixtureError, match="prep-subject-registered"):
            run.register_subject(70, foreign, channel=channel)
    finally:
        _join_run(run)


def test_foreign_run_id_expectation_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    table, procs = _world()
    run, _repo, _fake, _evidence, _control = _run(tmp_path, monkeypatch, table=table, procs=procs)
    try:
        run.start()
        run.prepare()
        procs[50] = stp._worker_proc("T", tpgid=40)
        run.record_stop()
        procs[60] = stp.subject_proc(60, cgroup=str(run.owner.target_cid))
        expectation = fp.SubjectExpectation(
            cid=str(run.owner.target_cid),
            binary_sha256=FAKE_BINARY,
            run_id="e" * 32,  # foreign run identity
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        channel = stp.FakeCidScopedTable(str(run.owner.target_cid), procs, exe_digest=FAKE_BINARY)
        with pytest.raises(fci.FixtureError, match="prep-subject-run-mismatch"):
            run.register_subject(60, expectation, channel=channel)
    finally:
        _join_run(run)


def _drive_to_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    docker: Any,
    table: Any,
    procs: dict[int, dict[str, Any]],
) -> tuple[Any, Any, Any, Any, Any]:
    """The full coupled positive up to the independently measured
    same-worker restoration, ready for the publication boundary
    under test (the same world the full lifecycle positive
    drives)."""
    run_holder: dict[str, Any] = {}

    def executor(argv: list[str], timeout: float) -> Any:
        run = run_holder.get("run")
        if (
            run is not None
            and run.owner.target_cid is not None
            and argv[:2] == ["docker", "rm"]
            and argv[-1] == run.owner.target_cid
        ):
            procs.pop(60, None)
        return docker(argv, timeout)

    run, repo, fake, owner_evidence, control = _run(
        tmp_path,
        monkeypatch,
        docker=docker,
        executor=executor,
        table=table,
        procs=procs,
    )
    run_holder["run"] = run
    run.start()
    run.prepare()
    procs[50] = stp._worker_proc("T", tpgid=40)
    run.record_stop()
    cid = str(run.owner.target_cid)
    procs[60] = stp.subject_proc(60, cgroup=cid)
    expectation = fp.SubjectExpectation(
        cid=cid,
        binary_sha256=FAKE_BINARY,
        run_id=run.binding.run_id,
        min_start_time=400,
        expected_tty=stp.TTYS,
    )
    channel = stp.FakeCidScopedTable(cid, procs, exe_digest=FAKE_BINARY)
    run.register_subject(60, expectation, channel=channel)
    fake.diagnostic_observed = True
    fake.wire_requests = 1
    run.observe()
    run.finish()
    assert run.owner.terminal_outcome == "pass"
    _join_run(run)
    procs[50] = stp._worker_proc("S", tpgid=50)
    return run, repo, fake, owner_evidence, control


def test_foreign_owner_context_refused_then_recovered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The SAME-owner binding (order 017-w section 1): a
    matching foreign expectation + foreign channel, and a
    matching foreign expected + measured binary, cannot
    redefine this owner's subject; a refused registration
    commits nothing and a later genuinely matching
    registration within the same still-valid measured phase
    succeeds."""
    table, procs = _world()
    fake = stl.LocalFakeDocker()
    run, _repo, _fake, _evidence, _control = _run(
        tmp_path, monkeypatch, docker=fake, table=table, procs=procs
    )
    try:
        run.start()
        run.prepare()
        procs[50] = stp._worker_proc("T", tpgid=40)
        run.record_stop()
        cid = str(run.owner.target_cid)
        # foreign CID: the collector agrees with the foreign
        # expectation/channel — the owner's registration does
        # not
        foreign_cid = "d" * 64
        procs[60] = stp.subject_proc(60, cgroup=foreign_cid)
        foreign_exp = fp.SubjectExpectation(
            cid=foreign_cid,
            binary_sha256=FAKE_BINARY,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        with pytest.raises(fci.FixtureError, match="native-owner-subject-cid-mismatch"):
            run.register_subject(
                60,
                foreign_exp,
                channel=stp.FakeCidScopedTable(foreign_cid, procs, exe_digest=FAKE_BINARY),
            )
        assert run.workflow.subject_receipt is None
        # foreign binary: matching CID, foreign expected and
        # measured binary
        procs[60] = stp.subject_proc(60, cgroup=cid)
        foreign_bin_exp = fp.SubjectExpectation(
            cid=cid,
            binary_sha256="e" * 64,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        with pytest.raises(fci.FixtureError, match="native-owner-subject-binary-mismatch"):
            run.register_subject(
                60, foreign_bin_exp, channel=stp.FakeCidScopedTable(cid, procs, exe_digest="e" * 64)
            )
        assert run.workflow.subject_receipt is None
        # the later genuinely matching registration in the
        # same still-valid measured phase succeeds
        matching_exp = fp.SubjectExpectation(
            cid=cid,
            binary_sha256=FAKE_BINARY,
            run_id=run.binding.run_id,
            min_start_time=400,
            expected_tty=stp.TTYS,
        )
        snapshot = run.register_subject(
            60, matching_exp, channel=stp.FakeCidScopedTable(cid, procs, exe_digest=FAKE_BINARY)
        )
        assert snapshot["subject"] is not None
        assert run.workflow.subject_receipt is not None
    finally:
        _join_run(run)


def test_origin_drift_before_owner_construction_refused_and_terminal_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Order 017-w section 2: a repository-identity drift
    AFTER the won admission but BEFORE the actual owner
    construction is compared against the ORIGINAL frozen
    binding (not re-resolved and discarded) — the refused
    constructor closes that SAME attempt honestly with a
    terminal fail and performs no external action."""
    repo = _v_repo(tmp_path / "repo")
    base_git = _v_git_runner(repo)
    reads = [0]
    external: list[bool] = []

    def git(args: list[str], cwd: Path) -> bytes:
        if args == ["remote", "get-url", "origin"]:
            reads[0] += 1
            if reads[0] >= 3:
                return b"https://github.com/other-synthetic/other.git\n"
        return bytes(base_git(args, cwd))

    def fake_exec(argv: list[str], timeout: float) -> Any:
        external.append(True)
        raise AssertionError("constructor must not call external platform")

    binding = fb.resolve_order_binding(repo, V_ORDER_ID, HEAD, git_runner=git)
    with pytest.raises(fci.FixtureError, match="bind-repo-identity-mismatch"):
        fno.NativeOwnerRun(
            binding,
            repo,
            tmp_path / "work",
            tmp_path / "evidence.json",
            tmp_path / "control",
            git_runner=git,
            executor=fake_exec,
            table=stp.FakeTable({}),
        )
    states = [entry["status"] for entry in fb.read_admission_record(repo, V_ORDER_ID)["attempts"]]
    assert states == ["fail"]
    assert external == []
    assert not (tmp_path / "work").exists()


def test_failed_publication_terminalizes_and_blocks_fresh_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Order 017-w section 3: a writer refusal at the
    completed-run publication boundary terminalizes the
    qualified attempt (journal fail); a later publication to
    a FRESH path refuses without creating a new qualifying
    record, relabeling the attempt or resetting the journal."""
    table, procs = _world()
    fake = stl.LocalFakeDocker()
    run, repo, _fake, _evidence, _control = _drive_to_publication(
        tmp_path, monkeypatch, docker=fake, table=table, procs=procs
    )
    try:
        untrusted = tmp_path / "untrusted"
        untrusted.mkdir()
        untrusted.chmod(0o770)
        with pytest.raises(fci.FixtureError):
            run.publish_native(untrusted / "result.json")
        journal = fb.read_admission_record(repo, V_ORDER_ID)
        assert journal["attempts"][0]["status"] == "fail"
        target = tmp_path / "native-final"
        target.mkdir()
        with pytest.raises(fci.FixtureError, match="native-owner-published"):
            run.publish_native(target / "retry.json")
        assert not (target / "retry.json").exists()
        # the journal stays honestly terminal-fail (no rewrite)
        journal = fb.read_admission_record(repo, V_ORDER_ID)
        assert journal["attempts"][0]["status"] == "fail"
    finally:
        _join_run(run)


def test_unverified_finalization_cannot_return_qualified_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Order 017-w section 3: a record-unreadable finalization
    AFTER the protected retention is a closed failure — the
    immutable retained bytes and the journal facts are
    preserved as-is and no normal qualified success is
    returned; the one-shot transition blocks any retry."""
    table, procs = _world()
    fake = stl.LocalFakeDocker()
    run, repo, _fake, _evidence, _control = _drive_to_publication(
        tmp_path, monkeypatch, docker=fake, table=table, procs=procs
    )
    try:
        native_out = tmp_path / "evidence" / "native-run-record.json"
        real_finalize = fb.record_order_attempt

        def unreadable_finalize(owned: Any, oid: str, run_id: str, status: str) -> str:
            if status == "pass":
                return "record-unreadable"
            return str(real_finalize(owned, oid, run_id, status))

        monkeypatch.setattr(fb, "record_order_attempt", unreadable_finalize)
        with pytest.raises(fci.FixtureError, match="native-owner-finalization-unverified"):
            run.publish_native(native_out)
        # the retained record is preserved AS IS (pending
        # journal state at build time, never rewritten)
        retained = json.loads(native_out.read_bytes())
        assert retained["owner_outcome"] == "pass"
        assert retained["attempt"] == "running"
        # the POST-RETENTION unverified finalization preserves
        # the actual journal fact as-is (still pending — this
        # path never re-closes, overwrites or relabels the
        # journal) and never a qualified pass
        journal = fb.read_admission_record(repo, V_ORDER_ID)
        assert journal["attempts"][0]["status"] == "running"
        # the one-shot transition: no fresh-path retry
        with pytest.raises(fci.FixtureError, match="native-owner-published"):
            run.publish_native(tmp_path / "evidence" / "retry.json")
        assert not (tmp_path / "evidence" / "retry.json").exists()
    finally:
        _join_run(run)


def test_raced_terminal_fail_cannot_return_qualified_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Order 017-w section 3: a finalization that races to a
    contradictory terminal state (fail) after the retention
    is a closed failure — the raced journal fact is preserved
    (never rewritten to pass) and no normal qualified
    success is returned."""
    table, procs = _world()
    fake = stl.LocalFakeDocker()
    run, repo, _fake, _evidence, _control = _drive_to_publication(
        tmp_path, monkeypatch, docker=fake, table=table, procs=procs
    )
    try:
        native_out = tmp_path / "evidence" / "native-run-record.json"
        real_finalize = fb.record_order_attempt

        def raced_finalize(owned: Any, oid: str, run_id: str, status: str) -> str:
            if status == "pass":
                real_finalize(owned, oid, run_id, "fail")
            return str(real_finalize(owned, oid, run_id, status))

        monkeypatch.setattr(fb, "record_order_attempt", raced_finalize)
        with pytest.raises(fci.FixtureError, match="native-owner-finalization-unverified"):
            run.publish_native(native_out)
        # the raced terminal fact is preserved, never rewritten
        journal = fb.read_admission_record(repo, V_ORDER_ID)
        assert journal["attempts"][0]["status"] == "fail"
        retained = json.loads(native_out.read_bytes())
        assert retained["attempt"] == "running"
        with pytest.raises(fci.FixtureError, match="native-owner-published"):
            run.publish_native(tmp_path / "evidence" / "retry.json")
    finally:
        _join_run(run)


def test_completed_run_measurement_failure_closes_and_blocks_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Order 017-w section 3: a verdict MEASUREMENT failure on
    the completed run closes the qualified attempt truthfully
    (an unpublished pass never leaves the attempt running),
    propagates the primary closed refusal unchanged, and
    blocks any fresh-path retry."""
    table, procs = _world()
    fake = stl.LocalFakeDocker()
    run, repo, _fake, _evidence, _control = _drive_to_publication(
        tmp_path, monkeypatch, docker=fake, table=table, procs=procs
    )
    try:

        def broken_finalize(self: Any, owner_record: Any) -> Any:
            raise fci.FixtureError("prep-not-prepared")

        monkeypatch.setattr(fp.NativeHandoffWorkflow, "finalize", broken_finalize)
        with pytest.raises(fci.FixtureError, match="prep-not-prepared"):
            run.publish_native(tmp_path / "evidence" / "native-run-record.json")
        journal = fb.read_admission_record(repo, V_ORDER_ID)
        assert journal["attempts"][0]["status"] == "fail"
        with pytest.raises(fci.FixtureError, match="native-owner-published"):
            run.publish_native(tmp_path / "evidence" / "retry.json")
        assert not (tmp_path / "evidence" / "retry.json").exists()
    finally:
        _join_run(run)


def test_publication_serialization_failure_closes_and_blocks_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Order 017-w section 3: an unexpected serialization
    error at the completed-run publication boundary closes
    the attempt truthfully and surfaces as the module's own
    closed "internal" token (never raw), blocking any
    fresh-path retry."""
    table, procs = _world()
    fake = stl.LocalFakeDocker()
    run, repo, _fake, _evidence, _control = _drive_to_publication(
        tmp_path, monkeypatch, docker=fake, table=table, procs=procs
    )
    try:

        def broken_write(path: Any, record: Any, work: Any = None) -> None:
            raise TypeError("non-serializable record value")

        monkeypatch.setattr(fno, "_write_native_run_record", broken_write)
        with pytest.raises(fci.FixtureError, match="internal"):
            run.publish_native(tmp_path / "evidence" / "native-run-record.json")
        journal = fb.read_admission_record(repo, V_ORDER_ID)
        assert journal["attempts"][0]["status"] == "fail"
        with pytest.raises(fci.FixtureError, match="native-owner-published"):
            run.publish_native(tmp_path / "evidence" / "retry.json")
        assert not (tmp_path / "evidence" / "retry.json").exists()
    finally:
        _join_run(run)


def test_prepare_only_finish_is_honest_not_ready(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run, repo, _fake, owner_evidence, _control = _run(tmp_path, monkeypatch)
    try:
        run.start()
        run.prepare()
        run.observe()
        # NO stop recorded, NO subject registered: the held
        # instance is finished unconsumed
        run.finish()
        _join_run(run)
        assert run.owner.terminal_outcome == "pass"
        native_out = tmp_path / "evidence" / "native-run-record.json"
        record = run.publish_native(native_out)
        assert record["owner_outcome"] == "pass"
        assert record["subject_measured"] is False
        assert record["stop_recorded"] is False
        assert record["native_record"] is None
        assert record["native_refusal"] is None
        assert record["verdict"]["ready"] is False
        assert record["verdict"]["reasons"], "an unready verdict names what is missing"
        for reason in record["verdict"]["reasons"]:
            assert reason in fp._VERDICT_REASONS
        assert native_out.exists()
        assert run.finalize_attempt() == "finalized"
        record_doc = fb.read_admission_record(repo, V_ORDER_ID)
        assert record_doc["attempts"][0]["status"] == "pass"
        ev_raw = json.loads(owner_evidence.read_bytes().decode("ascii"))
        flocal.validate_native_owner_run_evidence(ev_raw)
        assert ev_raw["fixture_consumed_by"] == "unobserved"
    finally:
        _join_run(run)


def test_owner_failure_publishes_honest_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = stl.LocalFakeDocker(build_rc=1)
    run, repo, _fake, owner_evidence, _control = _run(tmp_path, monkeypatch, docker=fake)
    try:
        run.start()
        with pytest.raises(fci.FixtureError):
            run.prepare()
        _join_run(run)
        assert run.owner.terminal_outcome == "fail"
        # the owner's OWN distinct native-scope fail evidence is
        # retained (the qualifying owner publication)
        ev_raw = json.loads(owner_evidence.read_bytes().decode("ascii"))
        flocal.validate_native_owner_run_evidence(ev_raw)
        assert ev_raw["status"] == "fail"
        assert ev_raw["order"] == V_ORDER_ID
        for key in ("native_started", "worker_stopped", "codex_invoked", "native_ready"):
            assert key not in ev_raw
        # the terminal fail finalized the bound attempt honestly
        record = fb.read_admission_record(repo, V_ORDER_ID)
        assert record["attempts"][0]["status"] == "fail"
        # the workflow was never prepared: the native-run record
        # cannot be minted (a closed refusal, never a fabrication)
        with pytest.raises(fci.FixtureError, match="prep-not-prepared"):
            run.publish_native(tmp_path / "evidence" / "native-run-record.json")
        # the journal stays honestly terminal-fail (no rewrite)
        record = fb.read_admission_record(repo, V_ORDER_ID)
        assert record["attempts"][0]["status"] == "fail"
    finally:
        _join_run(run)


def test_abort_publishes_honest_aborted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run, repo, _fake, owner_evidence, _control = _run(tmp_path, monkeypatch)
    try:
        run.start()
        run.prepare()
        run.abort()
        _join_run(run)
        assert run.owner.terminal_outcome == "aborted"
        record = fb.read_admission_record(repo, V_ORDER_ID)
        assert record["attempts"][0]["status"] == "aborted"
        native_out = tmp_path / "evidence" / "native-run-record.json"
        record_doc = run.publish_native(native_out)
        assert record_doc["owner_outcome"] == "aborted"
        assert record_doc["attempt"] == "terminal-preserved"
        assert record_doc["native_record"] is None
        assert record_doc["verdict"]["ready"] is False
        assert native_out.exists()
        ev_raw = json.loads(owner_evidence.read_bytes().decode("ascii"))
        flocal.validate_native_owner_run_evidence(ev_raw)
        assert ev_raw["status"] == "fail"
        assert ev_raw["reason"] == "cancelled"
    finally:
        _join_run(run)


# -- the distinct native-scope closed validator --------------------------------
def test_native_owner_run_evidence_validator_closed() -> None:
    base = {
        "record": flocal.NATIVE_OWNER_RUN_EVIDENCE_SCHEMA,
        "scope": flocal.NATIVE_OWNER_RUN_SCOPE,
        "status": "fail",
        "order": V_ORDER_ID,
        "run_id": "c" * 32,
        "bind_head": HEAD,
        "deadline_expired": False,
        "reason": "build-failed",
        "stage": "build",
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
    # the honest native-scope fail record validates
    flocal.validate_native_owner_run_evidence(dict(base))
    # the S schema is not this scope (and vice versa: the S
    # validator refuses the native grammar)
    s_like = dict(base)
    s_like["record"] = flocal.SCHEMA
    s_like.pop("scope")
    s_like["order"] = "017-s"
    with pytest.raises(fci.FixtureError, match="native-owner-run-evidence-invalid"):
        flocal.validate_native_owner_run_evidence(s_like)
    with_s_flags = dict(base)
    with_s_flags["native_started"] = False
    with pytest.raises(fci.FixtureError, match="native-owner-run-evidence-invalid"):
        flocal.validate_native_owner_run_evidence(with_s_flags)
    # the OAP order grammar is enforced (not fixed to 017-s)
    bad_order = dict(base)
    bad_order["order"] = "017-s1"  # digit: outside the OAP id grammar
    with pytest.raises(fci.FixtureError, match="native-owner-run-evidence-invalid"):
        flocal.validate_native_owner_run_evidence(bad_order)
    bad_head = dict(base)
    bad_head["bind_head"] = "nope"
    with pytest.raises(fci.FixtureError, match="native-owner-run-evidence-invalid"):
        flocal.validate_native_owner_run_evidence(bad_head)
    unknown = dict(base)
    unknown["extra"] = True
    with pytest.raises(fci.FixtureError, match="native-owner-run-evidence-invalid"):
        flocal.validate_native_owner_run_evidence(unknown)
    bad_ledger = dict(base)
    bad_ledger["ledger"] = dict(base["ledger"], api_requests=5)
    with pytest.raises(fci.FixtureError, match="native-owner-run-evidence-invalid"):
        flocal.validate_native_owner_run_evidence(bad_ledger)
    bad_reason = dict(base)
    bad_reason["reason"] = "not-a-real-token"
    with pytest.raises(fci.FixtureError, match="native-owner-run-evidence-invalid"):
        flocal.validate_native_owner_run_evidence(bad_reason)
