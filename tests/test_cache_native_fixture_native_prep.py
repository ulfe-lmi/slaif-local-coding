"""Native-handoff preparation-contract tests (order 017-t, section 3).

Pure/fake-layer law plus tiny EXACT-OWNED Python children for the
real /proc metadata mechanics only: no test signals any process
other than its own exact-owned children (killed by the test's
exact-owned cleanup if still alive at teardown), launches a
container or namespace, runs the native binary, or touches the
real worker/Bash group.  The real /proc reader is exercised
against the test's own short-lived child and against an absent
pid; the fake table covers every boundary the real table would
make unsafe to exercise.  The full PUBLIC lifecycle is proven
with fake platform behavior only: prepare/observe/record_stop/
finalize over scripted metadata, with the native-owner
producer record and the historical S record both bound through
the closed parsers.
"""

from __future__ import annotations

import ast
import base64
import dataclasses
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PREP_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_native_prep.py"
BINDING_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_binding.py"
CI_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_ci.py"
LOCAL_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_local.py"

import importlib.util  # noqa: E402

ci_spec = importlib.util.spec_from_file_location("cache_native_fixture_ci", CI_PATH)
assert ci_spec is not None and ci_spec.loader is not None
fci = importlib.util.module_from_spec(ci_spec)
sys.modules["cache_native_fixture_ci"] = fci
ci_spec.loader.exec_module(fci)

b_spec = importlib.util.spec_from_file_location("cache_native_fixture_binding", BINDING_PATH)
assert b_spec is not None and b_spec.loader is not None
fb = importlib.util.module_from_spec(b_spec)
sys.modules["cache_native_fixture_binding"] = fb
b_spec.loader.exec_module(fb)

p_spec = importlib.util.spec_from_file_location("cache_native_fixture_native_prep", PREP_PATH)
assert p_spec is not None and p_spec.loader is not None
fp = importlib.util.module_from_spec(p_spec)
sys.modules["cache_native_fixture_native_prep"] = fp
p_spec.loader.exec_module(fp)

# The REAL R/S owner module: imported (module load only, no
# instantiation — __init__ is what claims the S one-attempt
# namespace, and the real backend is never invoked in T) so
# the full positive can drive its actual finish/export/
# teardown code with fake platform operations.
l_spec = importlib.util.spec_from_file_location("cache_native_fixture_local", LOCAL_PATH)
assert l_spec is not None and l_spec.loader is not None
flocal = importlib.util.module_from_spec(l_spec)
sys.modules["cache_native_fixture_local"] = flocal
l_spec.loader.exec_module(flocal)

CID = "a" * 64
FOREIGN_CID = "9" * 64
BINARY = "b" * 64
OTHER_BINARY = "e" * 64
RUN = "c" * 32
HEAD = "d" * 40
IMAGE_ID = "4" * 64
TTYS = 34817
CODEX_ARGV = fp.SUBJECT_ARGV
CODEX_CMDLINE = b"\0".join(a.encode("ascii") for a in CODEX_ARGV) + b"\0"


# -- fake process table ------------------------------------------------------------


def stat_line(
    pid: int,
    comm: str = "bash",
    state: str = "S",
    ppid: int = 1,
    pgrp: int | None = None,
    session: int | None = None,
    tty: int = 0,
    tpgid: int = 0,
    start: int = 100,
) -> str:
    pgrp = pid if pgrp is None else pgrp
    session = pgrp if session is None else session
    fields = (
        [state, str(ppid), str(pgrp), str(session), str(tty), str(tpgid)]
        + ["0"] * 13
        + [str(start)]
        + ["0"] * 30
    )
    return f"{pid} ({comm}) " + " ".join(fields)


def status_bytes(uid: int, gid: int, groups: tuple[int, ...] = ()) -> bytes:
    return (
        f"Name:\tcodex\nUmask:\t0000\nState:\tS (sleeping)\nTgid:\t1\n"
        f"Uid:\t{uid}\t{uid}\t{uid}\t{uid}\nGid:\t{gid}\t{gid}\t{gid}\t{gid}\n"
        f"Groups:\t{' '.join(str(g) for g in groups) if groups else ''}\n"
    ).encode("ascii")


def bash_proc(
    pid: int,
    *,
    state: str = "S",
    ppid: int = 1,
    pgrp: int | None = None,
    session: int = 99,
    tty: int = TTYS,
    start: int = 100,
    tpgid: int = 0,
) -> dict[str, Any]:
    return {
        "stat": stat_line(
            pid, "bash", state, ppid, pgrp if pgrp is not None else pid, session, tty, tpgid, start
        ),
        "cmdline": b"bash\0",
        "status": status_bytes(1000, 1000),
    }


def subject_proc(
    pid: int,
    *,
    argv: bytes = CODEX_CMDLINE,
    uid: int = 21002,
    gid: int = 21002,
    groups: tuple[int, ...] = (21002,),
    state: str = "S",
    ppid: int = 1,
    pgrp: int | None = None,
    session: int = 77,
    tty: int = TTYS,
    tpgid: int | None = None,
    start: int = 500,
    cgroup: str | None = None,
) -> dict[str, Any]:
    pgrp = pid if pgrp is None else pgrp
    proc: dict[str, Any] = {
        "stat": stat_line(
            pid,
            "codex",
            state,
            ppid,
            pgrp,
            session,
            tty,
            tpgid if tpgid is not None else pgrp,
            start,
        ),
        "cmdline": argv,
        "status": status_bytes(uid, gid, groups),
    }
    if cgroup is not None:
        proc["cgroup"] = cgroup
    return proc


class FakeTable:
    def __init__(self, procs: dict[int, dict[str, Any]], *, absent: set[int] | None = None) -> None:
        self.procs = procs
        # pids whose entry EXISTS but is unreadable: an unknown,
        # never a proven absence
        self._absent = absent or set()

    def stat(self, pid: int) -> bytes | None:
        p = self.procs.get(pid)
        return p["stat"].encode("ascii") if p else None

    def cmdline(self, pid: int) -> bytes | None:
        p = self.procs.get(pid)
        return p["cmdline"] if p else None

    def status(self, pid: int) -> bytes | None:
        p = self.procs.get(pid)
        return p["status"] if p else None

    def list_pids(self) -> list[int]:
        return sorted(self.procs)

    def pid_present(self, pid: int) -> bool | None:
        if pid in self._absent:
            return None  # entry unreadable: unknown, not a verified absence
        return pid not in self.procs  # True = proven missing, False = present


class FakeCidScopedTable:
    """A scripted registered-CID channel over fake metadata:
    every read is scoped to the registered CID, and the
    executable digest is the channel's measured half."""

    def __init__(
        self,
        cid: str,
        procs: dict[int, dict[str, Any]],
        *,
        exe_digest: str | None = BINARY,
    ) -> None:
        self._cid = cid
        self._procs = procs
        self._exe_digest = exe_digest

    @property
    def cid(self) -> str:
        return self._cid

    def _in_scope(self, pid: int) -> bool:
        p = self._procs.get(pid)
        return p is not None and p.get("cgroup") == self._cid

    def cgroup_scope(self, pid: int) -> str | None:
        return f"docker-{self._cid}.scope" if self._in_scope(pid) else None

    def stat(self, pid: int) -> bytes | None:
        p = self._procs.get(pid)
        if p is None or not self._in_scope(pid):
            return None
        raw: str = p["stat"]
        return raw.encode("ascii")

    def cmdline(self, pid: int) -> bytes | None:
        p = self._procs.get(pid)
        if p is None or not self._in_scope(pid):
            return None
        raw: bytes = p["cmdline"]
        return raw

    def status(self, pid: int) -> bytes | None:
        p = self._procs.get(pid)
        if p is None or not self._in_scope(pid):
            return None
        raw: bytes = p["status"]
        return raw

    def list_pids(self) -> list[int]:
        raise fci.FixtureError("prep-channel-no-enumeration")

    def exe_sha256(self, pid: int, birth: int) -> str | None:
        p = self._procs.get(pid)
        if p is None or not self._in_scope(pid):
            return None
        try:
            st = fp.parse_proc_stat(p["stat"])
        except fci.FixtureError:
            return None
        if st.start_time != birth:
            raise fci.FixtureError("prep-subject-invalid")
        return self._exe_digest


def _expectation(**overrides: Any) -> Any:
    base: dict[str, Any] = {
        "cid": CID,
        "binary_sha256": BINARY,
        "run_id": RUN,
        "min_start_time": 400,
        "expected_tty": TTYS,
    }
    base.update(overrides)
    return fp.SubjectExpectation(**base)


def _binding() -> Any:
    return fb.OrderRunBinding(
        order_id="017-t",
        order_path="oap/orders/017-t-evidence-finalization-and-native-preparation.md",
        order_sha256="e" * 64,
        active_bytes=b"017-t\n",
        source_head=HEAD,
        repo_identity="ulfe-lmi/slaif-local-coding",
        run_id=RUN,
    )


def _owner_record(**overrides: Any) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "record": "slaif-017s-local-evidence-v1",
        "order": "017-s",
        "status": "pass",
        "run_id": RUN,
        "codex_invoked": False,
        "worker_stopped": False,
        "native_started": False,
        "native_ready": False,
        "prepared": {"cid": CID, "state": "prepared-unconsumed"},
        "artifact": {"binary_sha256": BINARY},
        "export": {"bytes": 2991, "sha256": "7" * 64},
        "teardown": {
            "container_present_before": True,
            "container_removal": "absent-verified",
            "image_removal": "absent-verified",
            "descendants_after": 0,
            "sentinel_survived": True,
        },
    }
    rec.update(overrides)
    return rec


def _native_owner_record(**overrides: Any) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "record": fp.NATIVE_OWNER_SCHEMA,
        "producer": fp.NATIVE_OWNER_PRODUCER,
        "status": "pass",
        "order": "017-t",
        "source_head": HEAD,
        "run_id": RUN,
        "prepared": {"cid": CID},
        "image": {"image_id": IMAGE_ID},
        "artifact": {"binary_sha256": BINARY},
        "export": {"bytes": 4096, "sha256": "7" * 64},
        "teardown": {
            "container_present_before": True,
            "container_removal": "absent-verified",
            "image_removal": "absent-verified",
            "descendants_after": 0,
            "sentinel_survived": True,
        },
        "native_started": True,
        "native_ready": True,
    }
    rec.update(overrides)
    return rec


def _worker_proc(state: str = "S", *, tpgid: int = 50, start: int = 500) -> dict[str, Any]:
    return {
        "stat": stat_line(50, "codex", state, 40, 50, 99, TTYS, tpgid, start),
        "cmdline": CODEX_CMDLINE,
        "status": status_bytes(1000, 1000),
    }


def _job_table(
    worker_state: str = "S",
    bash_state: str = "S",
    *,
    worker: bool = True,
    bash: bool = True,
    worker_tpgid: int = 50,
    worker_start: int = 500,
) -> FakeTable:
    procs: dict[int, dict[str, Any]] = {}
    if bash:
        procs[40] = bash_proc(40, state=bash_state, pgrp=40)
    if worker:
        procs[50] = _worker_proc(worker_state, tpgid=worker_tpgid, start=worker_start)
    return FakeTable(procs)


def _stop_receipt() -> Any:
    # the STABLE stopped phase: W observed T, B running, the
    # foreground observed (on W's own tpgid) back on B.pgrp
    return fp.collect_stop_observation(_job_table(worker_state="T", worker_tpgid=40), 50, 40)


# -- pure parsers ---------------------------------------------------------------------


def test_stat_parser_closed() -> None:
    st = fp.parse_proc_stat(stat_line(7, "my (weird) comm", "R", 3, 9, 11, TTYS, 9, 42))
    assert (
        st.pid,
        st.comm,
        st.state,
        st.ppid,
        st.pgrp,
        st.session,
        st.tty,
        st.tpgid,
        st.start_time,
    ) == (7, "my (weird) comm", "R", 3, 9, 11, TTYS, 9, 42)
    # a legitimate no-TTY process: tpgid -1 is preserved as the
    # explicit unavailable-foreground state, never malformed
    assert fp.parse_proc_stat(stat_line(7, "c", "S", 3, 9, 11, 0, -1, 42)).tpgid == -1
    for bad in (
        "",
        "no-space",
        "x (c) S 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0",  # non-numeric pid
        "7 (c R 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0",  # missing close paren
        "7 (c) S 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0",  # too few fields
        "7 (c) Q 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0",  # unknown state char
        "7 (c) S -1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0",  # negative ppid
        "7 (c) S 1 1 1 0 -2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0",  # tpgid below -1
        "7 () S 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0",  # empty comm
    ):
        with pytest.raises(fci.FixtureError, match="prep-stat-malformed"):
            fp.parse_proc_stat(bad)


def test_cmdline_parser_closed() -> None:
    assert fp.parse_proc_cmdline(CODEX_CMDLINE) == CODEX_ARGV
    assert fp.parse_proc_cmdline(b"") == ()
    for bad in (
        b"no-trailing-nul",
        b"a\0\0b\0",  # empty argv element
        b"a\xffb\0",  # non-ascii
        b"x" * (fp._CMDLINE_MAX + 1),  # overbound
        b"\0",  # only a NUL
    ):
        with pytest.raises(fci.FixtureError, match="prep-cmdline-malformed"):
            fp.parse_proc_cmdline(bad)


def test_status_parser_closed() -> None:
    assert fp.parse_proc_status(status_bytes(21002, 21002, (21002,))) == (21002, 21002, (21002,))
    assert fp.parse_proc_status(status_bytes(0, 0, ())) == (0, 0, ())
    for bad in (
        b"Name:\tcodex\n",  # missing all identity lines
        b"Uid:\t21002\t21002\t21002\t21002\nGid:\t1\t1\t1\t1\n",  # no Groups
        b"Uid:\t-x\t1\t1\t1\nGid:\t1\t1\t1\t1\nGroups:\t1\n",  # non-numeric
        b"x" * (fp._STATUS_MAX + 1),
    ):
        with pytest.raises(fci.FixtureError, match="prep-status-malformed"):
            fp.parse_proc_status(bad)


# -- worker/Bash group facts -------------------------------------------------------------


def test_collect_worker_group_positive() -> None:
    table = FakeTable(
        {
            40: bash_proc(40, ppid=1),  # Bash B: own job group 40
            50: {  # worker W: job group 50
                "stat": stat_line(50, "codex", "S", 40, 50, 99, TTYS, 500),
                "cmdline": CODEX_CMDLINE,
                "status": status_bytes(1000, 1000),
            },
            51: bash_proc(51, ppid=40, pgrp=50, state="R"),  # a 2nd member of G
            70: bash_proc(70, ppid=40, pgrp=70),  # separately grouped tool session
            71: bash_proc(71, ppid=70, pgrp=70),
            80: bash_proc(80, ppid=1, pgrp=80, session=1234),  # other session: ignored
        }
    )
    facts = fp.collect_worker_group(table, 50, 40)
    assert facts.worker_pid == 50 and facts.bash_pid == 40
    assert facts.worker_pgrp == 50 and facts.bash_pgrp == 40
    assert facts.worker_session == 99 and facts.bash_session == 99
    assert facts.worker_start_time == 100 and facts.bash_start_time == 100
    assert facts.same_job is False and facts.same_tty is True
    assert facts.foreground_pgrp is None  # unobserved, never guessed
    assert [(m.pid, m.state) for m in facts.members] == [(50, "S"), (51, "R")]
    assert facts.session_other_groups == ((40, 1), (70, 2))
    # the tty foreground observation, when supplied read-only, is carried exactly
    fg = fp.collect_worker_group(table, 50, 40, foreground_pgrp=40)
    assert fg.foreground_pgrp == 40


def test_worker_group_vanished_and_invalid() -> None:
    table = FakeTable({40: bash_proc(40)})
    with pytest.raises(fci.FixtureError, match="prep-worker-vanished"):
        fp.collect_worker_group(table, 50, 40)
    for bad_pid in (0, -1, True, "50", None):
        with pytest.raises(fci.FixtureError, match="prep-worker-invalid"):
            fp.collect_worker_group(table, bad_pid)
    # the worker's parent (Bash B) vanished
    table2 = FakeTable(
        {
            50: {
                "stat": stat_line(50, "codex", "S", 999, 50, 99, TTYS, 500),
                "cmdline": CODEX_CMDLINE,
                "status": status_bytes(1000, 1000),
            }
        }
    )
    with pytest.raises(fci.FixtureError, match="prep-bash-vanished"):
        fp.collect_worker_group(table2, 50)
    table_with_worker = FakeTable(
        {
            40: bash_proc(40),
            50: {
                "stat": stat_line(50, "codex", "S", 40, 50, 99, TTYS, 500),
                "cmdline": CODEX_CMDLINE,
                "status": status_bytes(1000, 1000),
            },
        }
    )
    for bad_bash in (0, True):
        with pytest.raises(fci.FixtureError, match="prep-bash-invalid"):
            fp.collect_worker_group(table_with_worker, 50, bad_bash)


def test_group_membership_overbound() -> None:
    procs: dict[int, dict[str, Any]] = {
        40: bash_proc(40),
        50: {
            "stat": stat_line(50, "codex", "S", 40, 50, 99, TTYS, 500),
            "cmdline": CODEX_CMDLINE,
            "status": status_bytes(1000, 1000),
        },
    }
    for i in range(fp._MEMBERSHIP_MAX + 2):
        pid = 1000 + i
        procs[pid] = bash_proc(pid, ppid=40, pgrp=50)
    table = FakeTable(procs)
    with pytest.raises(fci.FixtureError, match="prep-proc-overbound"):
        fp.collect_worker_group(table, 50, 40)


def test_tool_session_provenance_closed() -> None:
    procs: dict[int, dict[str, Any]] = {
        40: bash_proc(40, ppid=1, pgrp=40),
        50: {
            "stat": stat_line(50, "codex", "S", 40, 50, 99, TTYS, 500),
            "cmdline": CODEX_CMDLINE,
            "status": status_bytes(1000, 1000),
        },
        # a MEASURED worker descendant that setsid into a new session
        70: bash_proc(70, ppid=50, pgrp=70, session=1234),
        # unrelated, same session: retained as unknown
        80: bash_proc(80, ppid=1, pgrp=80, session=99),
        # separately registered exact pid+birth, new session
        90: bash_proc(90, ppid=1, pgrp=90, session=1235),
        # same uid alone is NOT provenance: neither adopted nor recorded
        95: bash_proc(95, ppid=1, pgrp=95, session=1236),
    }
    table = FakeTable(procs)
    facts = fp.collect_worker_group(table, 50, 40, registered_owners={90: 100})
    tool = {pgrp: list(ms) for pgrp, ms in facts.tool_sessions}
    assert [m.provenance for m in tool[70]] == ["worker-descendant"]
    assert [m.provenance for m in tool[80]] == ["unknown"]
    assert [m.provenance for m in tool[90]] == ["owned"]
    assert 95 not in tool
    # a registered birth mismatch is not ownership: unknown elsewhere is dropped
    facts2 = fp.collect_worker_group(table, 50, 40, registered_owners={90: 999})
    tool2 = {pgrp: list(ms) for pgrp, ms in facts2.tool_sessions}
    assert 90 not in tool2
    # the same-uid member is never adopted as owned
    facts3 = fp.collect_worker_group(table, 50, 40)
    tool3 = {pgrp: list(ms) for pgrp, ms in facts3.tool_sessions}
    assert all(m.provenance == "unknown" for m in tool3[80])
    with pytest.raises(fci.FixtureError, match="prep-worker-invalid"):
        fp.collect_worker_group(table, 50, 40, registered_owners={0: 1})
    with pytest.raises(fci.FixtureError, match="prep-worker-invalid"):
        fp.collect_worker_group(table, 50, 40, registered_owners={"x": 1})


# -- subject identity ----------------------------------------------------------------------


def test_subject_host_unscoped_unmeasured() -> None:
    for groups in ((21002,), ()):  # the closed group law: own primary or none
        table = FakeTable({60: subject_proc(60, groups=groups)})
        ident = fp.collect_subject_identity(table, 60, _expectation())
        assert ident.source == "cid-registered"
        assert ident.cid == CID and ident.run_id == RUN
        assert ident.uid == 21002 and ident.gid == 21002
        assert ident.groups == groups
        assert ident.argv == CODEX_ARGV
        assert ident.argv_sha256 == fp.argv_digest(CODEX_ARGV)
        # no channel: the binary is UNMEASURED, never assumed
        assert ident.binary_sha256 is None and ident.binary_verified is False
        assert ident.cid_membership == "host-unscoped"
        assert ident.cid_attestation == "expectation-only"
        assert ident.tty == TTYS and ident.start_time == 500 and ident.start_bound is True
    # an unobserved birth bound is incomplete, not a refusal, and never claimed
    table = FakeTable({60: subject_proc(60)})
    ident2 = fp.collect_subject_identity(table, 60, _expectation(min_start_time=None))
    assert ident2.start_bound is False
    # a missing expectation fact is refused, not guessed
    with pytest.raises(fci.FixtureError, match="prep-expectation-invalid"):
        fp.collect_subject_identity(table, 60, _expectation(cid="z" * 64))


def test_subject_channel_measured_positive() -> None:
    table = FakeTable({60: subject_proc(60, cgroup=CID)})
    channel = FakeCidScopedTable(CID, table.procs)
    ident = fp.collect_subject_identity(table, 60, _expectation(), channel=channel)
    assert ident.cid_membership == "cid-scoped"
    assert ident.binary_sha256 == BINARY and ident.binary_verified is True
    # a channel without the executable measurement stays
    # unmeasured — never assumed from the expectation
    channel_none = FakeCidScopedTable(CID, table.procs, exe_digest=None)
    ident2 = fp.collect_subject_identity(table, 60, _expectation(), channel=channel_none)
    assert ident2.binary_sha256 is None and ident2.binary_verified is False
    assert ident2.cid_membership == "cid-scoped"


def test_subject_channel_cid_mismatch_refused() -> None:
    # a channel bound to a DIFFERENT CID than the expectation
    # can never record a cid-scoped identity, no matter what
    # its process metadata says
    table = FakeTable({60: subject_proc(60, cgroup=FOREIGN_CID)})
    channel = FakeCidScopedTable(FOREIGN_CID, table.procs)
    with pytest.raises(fci.FixtureError, match="prep-channel-cid-mismatch"):
        fp.collect_subject_identity(table, 60, _expectation(), channel=channel)
    # the foreign-scope positive control: a process of
    # container Y on the registered channel of container X
    # does not exist on that channel
    table2 = FakeTable({60: subject_proc(60, cgroup=FOREIGN_CID)})
    channel2 = FakeCidScopedTable(CID, table2.procs)
    with pytest.raises(fci.FixtureError, match="prep-subject-vanished"):
        fp.collect_subject_identity(table2, 60, _expectation(), channel=channel2)


def test_subject_measured_binary_mismatch_refused() -> None:
    table = FakeTable({60: subject_proc(60, cgroup=CID)})
    channel = FakeCidScopedTable(CID, table.procs, exe_digest=OTHER_BINARY)
    with pytest.raises(fci.FixtureError, match="prep-binary-invalid"):
        fp.collect_subject_identity(table, 60, _expectation(), channel=channel)


def test_subject_identity_negatives() -> None:
    wrong_argv = b"python3\0-c\0pass\0"
    cases: list[Any] = [
        (dict(argv=wrong_argv), "prep-argv-invalid"),
        (dict(uid=0), "prep-uid-invalid"),
        (dict(gid=0), "prep-gid-invalid"),
        (dict(groups=(0,)), "prep-groups-invalid"),
        (dict(groups=(21002, 21003)), "prep-groups-invalid"),
        (dict(tty=9999), "prep-tty-invalid"),
        (dict(start=399), "prep-start-unbound"),
    ]
    for overrides, token in cases:
        table = FakeTable({60: subject_proc(60, **overrides)})
        with pytest.raises(fci.FixtureError, match=token):
            fp.collect_subject_identity(table, 60, _expectation())
    with pytest.raises(fci.FixtureError, match="prep-subject-vanished"):
        fp.collect_subject_identity(FakeTable({}), 60, _expectation())
    with pytest.raises(fci.FixtureError, match="prep-subject-invalid"):
        fp.collect_subject_identity(FakeTable({60: subject_proc(60)}), 0, _expectation())


def test_no_tty_tpgid_is_explicit_unavailable() -> None:
    # a legitimate no-TTY process: tpgid -1 is preserved as
    # the explicit unavailable-foreground state
    table = FakeTable({60: subject_proc(60, tty=0, tpgid=-1)})
    ident = fp.collect_subject_identity(table, 60, _expectation(expected_tty=None))
    assert ident.tty == 0


def _subject_record(ident: Any) -> dict[str, Any]:
    return {
        "source": ident.source,
        "cid": ident.cid,
        "pid": ident.pid,
        "uid": ident.uid,
        "gid": ident.gid,
        "groups": list(ident.groups),
        "argv": list(ident.argv),
        "argv_sha256": ident.argv_sha256,
        "binary_sha256": ident.binary_sha256,
        "binary_verified": ident.binary_verified,
        "cid_attestation": ident.cid_attestation,
        "cid_membership": ident.cid_membership,
        "tty": ident.tty,
        "start_time": ident.start_time,
        "start_bound": ident.start_bound,
        "run_id": ident.run_id,
        "pty_matched": ident.pty_matched,
    }


def test_subject_retained_record_validation() -> None:
    table = FakeTable({60: subject_proc(60, cgroup=CID)})
    ident = fp.collect_subject_identity(
        table, 60, _expectation(), channel=FakeCidScopedTable(CID, table.procs)
    )
    rec = _subject_record(ident)
    again = fp.validate_subject_identity(rec, _expectation())
    assert again == ident
    # unbound birth is INCOMPLETE (start_bound False), never ready-by-flag
    unbound = dict(rec, start_bound=False)
    again2 = fp.validate_subject_identity(unbound, _expectation(min_start_time=None))
    assert again2.start_bound is False
    forged = dict(rec, start_bound=False, start_time=10)
    with pytest.raises(fci.FixtureError, match="prep-start-unbound"):
        fp.validate_subject_identity(forged, _expectation(min_start_time=400))
    for key, bad in (
        ("source", "host-uid"),
        ("cid", "b" * 64),
        ("run_id", "d" * 32),
        ("binary_sha256", "e" * 64),
        ("binary_verified", False),
        ("cid_attestation", "forged"),
        ("cid_membership", "half-scoped"),
        ("uid", 0),
        ("gid", 1000),
        ("groups", [21002.0]),  # float: not a strict integer (shape)
        ("groups", [True]),  # bool: not a strict integer (shape)
        ("groups", [0]),  # foreign group: the closed value law
        ("argv_sha256", "f" * 64),
        ("tty", 9999),
    ):
        bad_rec = dict(rec)
        bad_rec[key] = bad
        token = {
            "source": "prep-source-invalid",
            "cid": "prep-cid-invalid",
            "binary_sha256": "prep-binary-invalid",
            "binary_verified": "prep-binary-invalid",
            "cid_attestation": "prep-source-invalid",
            "uid": "prep-uid-invalid",
            "gid": "prep-gid-invalid",
            "tty": "prep-tty-invalid",
            "argv_sha256": "prep-record-malformed",
            "run_id": "prep-record-malformed",
        }.get(key, "prep-record-malformed")
        if key in ("groups",):
            # shape first: non-strict-integer groups are a record
            # malformation; the closed VALUE law (foreign group) is
            # prep-groups-invalid
            token = "prep-record-malformed" if bad in ([21002.0], [True]) else "prep-groups-invalid"
        with pytest.raises(fci.FixtureError, match=token):
            fp.validate_subject_identity(bad_rec, _expectation())
    # a self-consistent record with a NON-pinned argv is the argv
    # value refusal (digest matches the wrong argv, so the integrity
    # check passes and the closed value law refuses)
    wrong_argv = ["codex", "--yolo"]
    bad_rec = dict(rec, argv=wrong_argv, argv_sha256=fp.argv_digest(tuple(wrong_argv)))
    with pytest.raises(fci.FixtureError, match="prep-argv-invalid"):
        fp.validate_subject_identity(bad_rec, _expectation())
    # and an argv tamper that breaks the digest is a record-integrity
    # refusal, not an argv value refusal
    with pytest.raises(fci.FixtureError, match="prep-record-malformed"):
        fp.validate_subject_identity(dict(rec, argv=wrong_argv), _expectation())
    # strict shape: extra / missing keys are malformed
    extra = dict(rec, forged_flag=True)
    with pytest.raises(fci.FixtureError, match="prep-record-malformed"):
        fp.validate_subject_identity(extra, _expectation())
    missing = {k: v for k, v in rec.items() if k != "start_bound"}
    with pytest.raises(fci.FixtureError, match="prep-record-malformed"):
        fp.validate_subject_identity(missing, _expectation())
    with pytest.raises(fci.FixtureError, match="prep-record-malformed"):
        fp.validate_subject_identity({"ready": True}, _expectation())


# -- stop observation --------------------------------------------------------------------


def test_stop_observation_stable_phase_positive() -> None:
    receipt = fp.collect_stop_observation(_job_table(worker_state="T", worker_tpgid=40), 50, 40)
    assert (receipt.worker_pid, receipt.worker_start_time, receipt.worker_pgrp) == (50, 500, 50)
    assert receipt.worker_session == 99 and receipt.worker_tty == TTYS
    # the foreground is observed (on W's own tpgid) back on B's
    # group: Bash has reclaimed the TTY in the stable stopped phase
    assert receipt.worker_tpgid == 40
    assert (receipt.bash_pid, receipt.bash_state, receipt.bash_pgrp) == (40, "S", 40)


def test_stop_observation_negatives() -> None:
    # the worker is still running: no stop observed to record
    with pytest.raises(fci.FixtureError, match="prep-stop-unobserved"):
        fp.collect_stop_observation(_job_table(worker_state="S", worker_tpgid=40), 50, 40)
    # G holds the foreground: a different (not the stable) phase
    with pytest.raises(fci.FixtureError, match="prep-stop-unobserved"):
        fp.collect_stop_observation(_job_table(worker_state="T", worker_tpgid=50), 50, 40)
    # partial stop: another observed member of G still runs
    procs = _job_table(worker_state="T", worker_tpgid=40).procs
    procs[51] = bash_proc(51, ppid=40, pgrp=50, state="R")
    with pytest.raises(fci.FixtureError, match="prep-stop-unobserved"):
        fp.collect_stop_observation(FakeTable(procs), 50, 40)
    # Bash stopped or vanished: the stable phase is not observed
    with pytest.raises(fci.FixtureError, match="prep-stop-unobserved"):
        fp.collect_stop_observation(
            _job_table(worker_state="T", worker_tpgid=40, bash_state="T"), 50, 40
        )
    with pytest.raises(fci.FixtureError, match="prep-bash-vanished"):
        fp.collect_stop_observation(
            _job_table(worker_state="T", worker_tpgid=40, bash=False), 50, 40
        )
    # the right-pane job layout: G differs from B's group
    procs_same = {
        40: bash_proc(40, pgrp=50),
        50: _worker_proc("T", tpgid=40),
    }
    with pytest.raises(fci.FixtureError, match="prep-stop-unobserved"):
        fp.collect_stop_observation(FakeTable(procs_same), 50, 40)
    # the worker vanished, or the pid is invalid
    with pytest.raises(fci.FixtureError, match="prep-worker-vanished"):
        fp.collect_stop_observation(FakeTable({40: bash_proc(40)}), 50, 40)
    with pytest.raises(fci.FixtureError, match="prep-worker-invalid"):
        fp.collect_stop_observation(_job_table(), 0, 40)
    with pytest.raises(fci.FixtureError, match="prep-bash-invalid"):
        fp.collect_stop_observation(_job_table(), 50, 0)


# -- restoration facts --------------------------------------------------------------------


def test_restoration_requires_recorded_stop() -> None:
    # a single current snapshot can never prove a past stop
    r = fp.collect_restoration(_job_table(worker_state="S", worker_tpgid=50), 50, 40, 50)
    assert r.stop_recorded is False and r.restored is False


def test_restoration_matrix() -> None:
    receipt = _stop_receipt()
    # the measured positive: the same worker running again, its
    # own group holding the observed foreground, after a stop
    r = fp.collect_restoration(
        _job_table(worker_state="S", worker_tpgid=50), 50, 40, 50, stop_receipt=receipt
    )
    assert (r.worker_state, r.bash_state, r.worker_stopped) == ("S", "S", False)
    assert (r.stop_recorded, r.restored) == (True, True)
    # the worker is still stopped: the STOPPED phase, reported as such
    r = fp.collect_restoration(
        _job_table(worker_state="T", worker_tpgid=40), 50, 40, 50, stop_receipt=receipt
    )
    assert r.worker_stopped is True and r.restored is False
    # foreground unobserved (None) or observed on the wrong group
    r = fp.collect_restoration(
        _job_table(worker_state="S", worker_tpgid=50), 50, 40, stop_receipt=receipt
    )
    assert r.restored is False
    r = fp.collect_restoration(
        _job_table(worker_state="S", worker_tpgid=50), 50, 40, 40, stop_receipt=receipt
    )
    assert r.restored is False
    # a birth substitution is not the same worker
    r = fp.collect_restoration(
        _job_table(worker_state="S", worker_tpgid=50, worker_start=999),
        50,
        40,
        50,
        stop_receipt=receipt,
    )
    assert r.restored is False
    # the worker or Bash vanished: honest unknowns, never restored
    r = fp.collect_restoration(_job_table(worker=False), 50, 40, 50, stop_receipt=receipt)
    assert r.worker_state is None and r.worker_stopped is False and r.restored is False
    r = fp.collect_restoration(_job_table(bash=False), 50, 40, 50, stop_receipt=receipt)
    assert r.bash_state is None and r.restored is False
    # a forged stop receipt is a closed refusal
    with pytest.raises(fci.FixtureError, match="prep-verdict-input-invalid"):
        fp.collect_restoration(_job_table(), 50, 40, 50, stop_receipt={"restored": True})
    # invalid pids
    with pytest.raises(fci.FixtureError, match="prep-worker-invalid"):
        fp.collect_restoration(_job_table(), 0, 40)
    with pytest.raises(fci.FixtureError, match="prep-bash-invalid"):
        fp.collect_restoration(_job_table(), 50, 0)


# -- owner final facts (historical S record) ------------------------------------------------


def test_owner_facts_parser_positive() -> None:
    facts = fp.parse_owner_final_facts(_owner_record())
    assert facts.schema == fp.OWNER_FACTS_SCHEMA
    assert facts.status == "pass" and facts.run_id == RUN and facts.cid == CID
    assert facts.binary_sha256 == BINARY
    assert facts.export_sha256 == "7" * 64
    assert facts.teardown_verified is True and facts.sentinel_survived is True
    assert facts.descendants_after == 0
    # the S flags keep their whole-rehearsal meaning: that run
    # never invoked Codex, stopped the worker, or started native
    assert facts.codex_invoked is False and facts.worker_stopped is False
    assert facts.native_started is False and facts.native_ready is False


@pytest.mark.parametrize(
    "overrides",
    [
        {"status": "fail"},
        {"order": "017-t"},  # producer/scope binding: S record is for 017-s only
        {"run_id": "x" * 32},
        {"codex_invoked": True},
        {"native_started": True},
        {"native_ready": True},
        {"prepared": {"cid": "z" * 64}},
        {"artifact": {"binary_sha256": "not-hex"}},
        {"export": {"bytes": 1, "sha256": "not-hex"}},
        {
            "teardown": {
                "container_present_before": False,
                "container_removal": "absent-verified",
                "image_removal": "absent-verified",
                "descendants_after": 0,
                "sentinel_survived": True,
            }
        },
        {
            "teardown": {
                "container_present_before": True,
                "container_removal": "still-present",
                "image_removal": "absent-verified",
                "descendants_after": 0,
                "sentinel_survived": True,
            }
        },
        {
            "teardown": {
                "container_present_before": True,
                "container_removal": "absent-verified",
                "image_removal": "absent-verified",
                "descendants_after": 1,
                "sentinel_survived": True,
            }
        },
        {
            "teardown": {
                "container_present_before": True,
                "container_removal": "absent-verified",
                "image_removal": "absent-verified",
                "descendants_after": True,
                "sentinel_survived": True,
            }
        },  # bool is not an integer
        {
            "teardown": {
                "container_present_before": True,
                "container_removal": "absent-verified",
                "image_removal": "absent-verified",
                "descendants_after": 0,
                "sentinel_survived": False,
            }
        },
    ],
)
def test_owner_facts_parser_negatives(overrides: dict[str, Any]) -> None:
    with pytest.raises(fci.FixtureError, match="prep-owner-record-malformed"):
        fp.parse_owner_final_facts(_owner_record(**overrides))
    for not_a_mapping in (None, "pass", ["pass"]):
        with pytest.raises(fci.FixtureError, match="prep-owner-record-malformed"):
            fp.parse_owner_final_facts(not_a_mapping)
    for missing in ("teardown", "order", "artifact"):
        rec = _owner_record()
        del rec[missing]
        with pytest.raises(fci.FixtureError, match="prep-owner-record-malformed"):
            fp.parse_owner_final_facts(rec)


# -- native-owner producer and parser ---------------------------------------------------


def _valid_payload(
    *,
    corrupt_original: bool = False,
    unquiesced: bool = False,
    unknown_field: bool = False,
) -> bytes:
    """The canonical shared-validator-valid export payload:
    the same closed shape the R/S finish path and the
    shared export client's validate_payload accept (exact
    top-level set, closed quiesce/snapshot records, closed
    diagnostic/position, originals whose DECODED bytes bind
    to the snapshot bytes AND sha)."""
    selected: dict[str, Any] = {
        "quiesce": {
            "record": "slaif-fixture-quiesce-v1",
            "provider_sockets_closed": True,
            "handlers_stopped": True,
            "owned_subject_stopped": True,
            "owned_tools_stopped": not unquiesced,
            "active_connections": 0,
            "residual_writers": 0,
        },
        "snapshot": {
            "record": "slaif-fixture-selected-snapshot-v1",
            "synthetic": True,
            "issued_calls": [],
            "originals_bytes": 11,
            "originals_sha256": hashlib.sha256(b"onetwothree").hexdigest(),
            "exporter_uid": 21001,
            "exported_before_teardown": True,
            "controller_ledger": {"requests": 2, "output_bytes": 0},
        },
        "diagnostic": {"state": "unobserved"},
        "observed_at_position": None,
        "originals": [
            base64.b64encode(b"wrong" if (corrupt_original and i == 0) else orig).decode("ascii")
            for i, orig in enumerate((b"one", b"two", b"three"))
        ],
        "originals_count": 3,
    }
    if unknown_field:
        selected["unexpected"] = True
    return json.dumps(selected, sort_keys=True, separators=(",", ":")).encode("ascii")


def _producer_context(**overrides: Any) -> dict[str, Any]:
    """The closed 6-key measured-context mapping the real
    owned adapter exposes.  Constructed INDEPENDENTLY of
    _producer_kwargs (the declared binding): the two must
    agree for the producer to emit a record."""
    ctx: dict[str, Any] = {
        "order": "017-t",
        "source_head": HEAD,
        "run_id": RUN,
        "cid": CID,
        "image_id": IMAGE_ID,
        "binary_sha256": BINARY,
    }
    ctx.update(overrides)
    return ctx


_DEFAULT_PAYLOAD = object()


class _OpaqueContext:
    """Sentinel: expose NO measured_context attribute at
    all (the bare public record-boundary seam only)."""


_FULL_CONTEXT = object()
_OPAQUE_CONTEXT = _OpaqueContext()


class FakeOwnerMeasurement:
    """The fake owned finish/export/teardown measurement
    path (the real backend is never invoked in T).
    ``context`` controls the measured-context extension:
    _FULL_CONTEXT (default) exposes the full context
    matching _producer_context(); an explicit mapping
    exposes exactly that mapping (including None =
    incomplete); _OPAQUE_CONTEXT exposes no attribute at
    all (the bare record-boundary seam)."""

    def __init__(
        self,
        *,
        payload: object = _DEFAULT_PAYLOAD,
        present_before: bool | None = True,
        cid_absent: bool | None = True,
        image_absent: bool | None = True,
        descendants: int | None = 0,
        sentinel: bool | None = True,
        native_started: bool | None = True,
        native_ready: bool | None = True,
        context: object = _FULL_CONTEXT,
    ) -> None:
        self._payload = _valid_payload() if payload is _DEFAULT_PAYLOAD else payload
        self._present_before = present_before
        self._cid_absent = cid_absent
        self._image_absent = image_absent
        self._descendants = descendants
        self._sentinel = sentinel
        self._native_started = native_started
        self._native_ready = native_ready
        if context is _OPAQUE_CONTEXT:
            return  # the bare seam: no measured_context attribute
        if context is _FULL_CONTEXT:
            context = _producer_context()
        self.measured_context = context

    def export_payload(self) -> bytes | None:
        payload = self._payload
        if isinstance(payload, bytes):
            return payload
        if payload is None:
            return None
        raise AssertionError("unexpected export payload fixture value")

    def container_present_before(self) -> bool | None:
        return self._present_before

    def container_absent_after(self) -> bool | None:
        return self._cid_absent

    def image_absent_after(self) -> bool | None:
        return self._image_absent

    def descendants_after(self) -> int | None:
        return self._descendants

    def sentinel_survived(self) -> bool | None:
        return self._sentinel

    def native_started(self) -> bool | None:
        return self._native_started

    def native_ready(self) -> bool | None:
        return self._native_ready


def _producer_kwargs(**overrides: Any) -> dict[str, Any]:
    kw: dict[str, Any] = {
        "order": "017-t",
        "source_head": HEAD,
        "run_id": RUN,
        "cid": CID,
        "image_id": IMAGE_ID,
        "binary_sha256": BINARY,
    }
    kw.update(overrides)
    return kw


def test_producer_positive_full_validation() -> None:
    payload = _valid_payload()
    rec = fp.produce_native_owner_record(
        FakeOwnerMeasurement(payload=payload), **_producer_kwargs()
    )
    # the digest is COMPUTED from the measured payload, the
    # FULL payload is validated by the ACTUAL shared export
    # law, and the full context is bound into the closed
    # record
    assert rec["record"] == fp.NATIVE_OWNER_SCHEMA
    assert rec["producer"] == fp.NATIVE_OWNER_PRODUCER
    assert rec["status"] == "pass"
    assert rec["order"] == "017-t" and rec["source_head"] == HEAD and rec["run_id"] == RUN
    assert rec["prepared"] == {"cid": CID}
    assert rec["image"] == {"image_id": IMAGE_ID}
    assert rec["artifact"] == {"binary_sha256": BINARY}
    assert rec["export"]["bytes"] == len(payload)
    assert rec["export"]["sha256"] == hashlib.sha256(payload).hexdigest()
    assert rec["teardown"] == {
        "container_present_before": True,
        "container_removal": "absent-verified",
        "image_removal": "absent-verified",
        "descendants_after": 0,
        "sentinel_survived": True,
    }
    assert rec["native_started"] is True and rec["native_ready"] is True
    # producer/consumer agreement: the closed consumer validates it
    facts = fp.parse_native_owner_facts(rec)
    assert facts.binary_sha256 == BINARY and facts.image_id == IMAGE_ID
    assert facts.export_bytes == len(payload) and facts.teardown_verified is True


@pytest.mark.parametrize(
    "overrides",
    [
        {"order": "017"},
        {"order": "017-U"},
        {"source_head": "d" * 39},
        {"source_head": "D" * 40},
        {"run_id": "c" * 31},
        {"cid": "a" * 63},
        {"image_id": "4" * 64 + "z"},
        {"binary_sha256": "b" * 63},
    ],
)
def test_producer_context_refusals(overrides: dict[str, Any]) -> None:
    with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
        fp.produce_native_owner_record(FakeOwnerMeasurement(), **_producer_kwargs(**overrides))


def _assert_shared_invalid(data: bytes) -> None:
    """Precondition: the negative is independently invalid
    under the ACTUAL shared export law (mirroring the
    strategic probe's own precondition)."""
    with pytest.raises(ValueError):
        fci.fixture_export.validate_payload(data)


@pytest.mark.parametrize(
    "data",
    [
        b"not-json",
        _valid_payload(corrupt_original=True),
        _valid_payload(unquiesced=True),
        _valid_payload(unknown_field=True),
    ],
)
def test_producer_full_payload_validation_refusals(data: bytes) -> None:
    _assert_shared_invalid(data)
    with pytest.raises(fci.FixtureError, match="prep-export-invalid"):
        fp.produce_native_owner_record(FakeOwnerMeasurement(payload=data), **_producer_kwargs())


_FORGED_CONTEXTS: dict[str, Any] = {
    "order": "017-v",
    "source_head": "e" * 40,
    "run_id": "e" * 32,
    "cid": FOREIGN_CID,
    "image_id": "5" * 64,
    "binary_sha256": OTHER_BINARY,
}


@pytest.mark.parametrize("key", sorted(_FORGED_CONTEXTS))
def test_producer_measured_context_mismatch_refused(key: str) -> None:
    forged = _producer_context(**{key: _FORGED_CONTEXTS[key]})
    with pytest.raises(fci.FixtureError, match="prep-native-owner-context-mismatch"):
        fp.produce_native_owner_record(FakeOwnerMeasurement(context=forged), **_producer_kwargs())


def test_producer_measured_context_incomplete_refused() -> None:
    full = _producer_context()
    missing = dict(full)
    del missing["cid"]
    extra = dict(full, attacker="x")
    for bad in (None, missing, extra, "not-a-mapping", 42):
        with pytest.raises(fci.FixtureError, match="prep-native-owner-context-mismatch"):
            fp.produce_native_owner_record(FakeOwnerMeasurement(context=bad), **_producer_kwargs())


def test_producer_measured_context_bound_positive() -> None:
    m = FakeOwnerMeasurement()
    context = m.measured_context
    assert isinstance(context, dict)
    assert set(context) == {
        "order",
        "source_head",
        "run_id",
        "cid",
        "image_id",
        "binary_sha256",
    }
    rec = fp.produce_native_owner_record(m, **_producer_kwargs())
    assert rec["order"] == "017-t" and rec["prepared"] == {"cid": CID}
    assert rec["image"] == {"image_id": IMAGE_ID}
    assert rec["artifact"] == {"binary_sha256": BINARY}


def test_producer_opaque_measurement_boundary() -> None:
    # a measurement WITHOUT the measured_context attribute is
    # the bare public record-boundary seam (the strategic
    # probe's scope): the FULL shared payload validation and
    # the closed teardown facts still apply, but no resource
    # binding is claimed
    payload = _valid_payload()
    rec = fp.produce_native_owner_record(
        FakeOwnerMeasurement(payload=payload, context=_OPAQUE_CONTEXT), **_producer_kwargs()
    )
    assert rec["export"]["sha256"] == hashlib.sha256(payload).hexdigest()
    assert rec["export"]["bytes"] == len(payload)


@pytest.mark.parametrize("image_id", [IMAGE_ID, "sha256:" + IMAGE_ID])
def test_producer_image_id_closed_forms(image_id: str) -> None:
    # both closed image-identity forms are admitted (the bare
    # digest and the ACTUAL measured Docker form), the record
    # retains the measured form, and the typed fact is the
    # normalized bare digest
    context = _producer_context(image_id=image_id)
    rec = fp.produce_native_owner_record(
        FakeOwnerMeasurement(context=context), **_producer_kwargs(image_id=image_id)
    )
    assert rec["image"] == {"image_id": image_id}
    facts = fp.parse_native_owner_facts(rec)
    assert facts.image_id == IMAGE_ID
    with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
        fp.produce_native_owner_record(
            FakeOwnerMeasurement(), **_producer_kwargs(image_id="sha256:" + "5" * 63)
        )
    with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
        fp.produce_native_owner_record(
            FakeOwnerMeasurement(), **_producer_kwargs(image_id="5" * 64 + "g")
        )


class FakeCompletedOwner:
    """The fake COMPLETED native-owner state over the faked
    backend: exactly the closed attribute seam the real
    OwnedOwnerMeasurement adapter reads (no platform
    operation is invoked)."""

    def __init__(
        self,
        *,
        export_payload: bytes | None,
        descendants_before: int = 1,
        teardown_container_absent: bool | None = True,
        image_removed: bool = True,
        teardown_descendants_after: int | None = 0,
        sentinel_survived: bool = True,
        target_cid: str | None = CID,
        image_id: str | None = IMAGE_ID,
        run_id: str = RUN,
        order: str = "017-t",
        bind_head: str = HEAD,
        binary_sha256: str | None = BINARY,
    ) -> None:
        self.export_payload = export_payload
        self.descendants_before = descendants_before
        self.teardown_container_absent = teardown_container_absent
        self.image_removed = image_removed
        self.teardown_descendants_after = teardown_descendants_after
        self.sentinel_survived = sentinel_survived
        self.target_cid = target_cid
        self.image_id = image_id
        self.run_id = run_id
        self.optin = {"order": order, "bind_head": bind_head}
        self.artifact = {"binary_sha256": binary_sha256} if binary_sha256 is not None else None


def _cid_scoped_receipt() -> Any:
    table = FakeTable({60: subject_proc(60, cgroup=CID)})
    return fp.collect_subject_identity(
        table, 60, _expectation(), channel=FakeCidScopedTable(CID, table.procs)
    )


def _host_unscoped_receipt() -> Any:
    table = FakeTable({60: subject_proc(60)})
    return fp.collect_subject_identity(table, 60, _expectation())


def test_owned_adapter_full_native_owner_positive() -> None:
    owner = FakeCompletedOwner(export_payload=_valid_payload())
    receipt = _cid_scoped_receipt()
    m = fp.OwnedOwnerMeasurement(owner, subject=receipt)
    rec = fp.produce_native_owner_record(m, **_producer_kwargs())
    # the record is bound to the owner's OWN measured state
    assert rec["run_id"] == owner.run_id
    assert rec["prepared"] == {"cid": owner.target_cid}
    assert rec["image"] == {"image_id": owner.image_id}
    assert rec["artifact"] == {"binary_sha256": BINARY}
    payload = owner.export_payload
    assert payload is not None
    assert rec["export"]["sha256"] == hashlib.sha256(payload).hexdigest()
    assert rec["export"]["bytes"] == len(payload)
    # the native facts come from the PUBLIC collector's
    # measured output, not a caller flag
    assert rec["native_started"] is True and rec["native_ready"] is True
    fp.parse_native_owner_facts(rec)


def test_owned_adapter_no_subject_receipt_refused() -> None:
    # a run whose collectors never measured a native subject
    # has no measured native start: the producer refuses
    owner = FakeCompletedOwner(export_payload=_valid_payload())
    with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
        fp.produce_native_owner_record(fp.OwnedOwnerMeasurement(owner), **_producer_kwargs())


def test_owned_adapter_started_but_not_ready() -> None:
    # a measured-but-unqualified subject (host-unscoped,
    # binary unmeasured) is honestly started-but-NOT-ready
    owner = FakeCompletedOwner(export_payload=_valid_payload())
    m = fp.OwnedOwnerMeasurement(owner, subject=_host_unscoped_receipt())
    assert m.native_started() is True
    assert m.native_ready() is False
    rec = fp.produce_native_owner_record(m, **_producer_kwargs())
    assert rec["native_started"] is True and rec["native_ready"] is False
    fp.parse_native_owner_facts(rec)


def test_owned_adapter_owner_binary_mismatch_not_ready() -> None:
    # the owner's OWN registered artifact differs from the
    # measured subject executable: the CID/run strings alone
    # cannot substitute for exact executable agreement —
    # honestly started, not ready
    owner = FakeCompletedOwner(export_payload=_valid_payload(), binary_sha256=OTHER_BINARY)
    m = fp.OwnedOwnerMeasurement(owner, subject=_cid_scoped_receipt())
    assert m.native_started() is True
    assert m.native_ready() is False
    rec = fp.produce_native_owner_record(m, **_producer_kwargs(binary_sha256=OTHER_BINARY))
    assert rec["native_started"] is True and rec["native_ready"] is False
    fp.parse_native_owner_facts(rec)


def test_owned_adapter_unbound_pty_not_ready() -> None:
    # a subject whose expected PTY was never bound (an
    # unobserved expected PTY or a measured tty0 process) is
    # honestly started, never ready: the visible native
    # handoff requires an actually bound, matched, nonzero
    # expected PTY
    table = FakeTable({60: subject_proc(60, cgroup=CID)})
    unbound = fp.collect_subject_identity(
        table, 60, _expectation(expected_tty=None), channel=FakeCidScopedTable(CID, table.procs)
    )
    assert unbound.pty_matched is False
    table0 = FakeTable({60: subject_proc(60, cgroup=CID, tty=0, tpgid=-1)})
    no_tty = fp.collect_subject_identity(
        table0, 60, _expectation(expected_tty=None), channel=FakeCidScopedTable(CID, table0.procs)
    )
    assert no_tty.pty_matched is False
    assert no_tty.tty == 0  # legitimate no-TTY parsing is preserved
    owner = FakeCompletedOwner(export_payload=_valid_payload())
    for receipt in (unbound, no_tty):
        m = fp.OwnedOwnerMeasurement(owner, subject=receipt)
        assert m.native_started() is True
        assert m.native_ready() is False


@pytest.mark.parametrize(
    "overrides",
    [
        {"export_payload": None},
        {"teardown_container_absent": None},
        {"image_removed": False},
        {"teardown_descendants_after": 1},
        {"sentinel_survived": False},
    ],
)
def test_owned_adapter_unmeasured_state_refused(overrides: dict[str, Any]) -> None:
    kwargs: dict[str, Any] = {"export_payload": _valid_payload()}
    kwargs.update(overrides)
    owner = FakeCompletedOwner(**kwargs)
    with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
        fp.produce_native_owner_record(
            fp.OwnedOwnerMeasurement(owner, subject=_cid_scoped_receipt()), **_producer_kwargs()
        )


@pytest.mark.parametrize(
    "overrides",
    [
        {"target_cid": None},
        {"binary_sha256": None},
        {"order": ""},
    ],
)
def test_owned_adapter_incomplete_context_refused(overrides: dict[str, Any]) -> None:
    owner = FakeCompletedOwner(export_payload=_valid_payload(), **overrides)
    with pytest.raises(fci.FixtureError, match="prep-native-owner-context-mismatch"):
        fp.produce_native_owner_record(
            fp.OwnedOwnerMeasurement(owner, subject=_cid_scoped_receipt()), **_producer_kwargs()
        )


def test_owned_adapter_measured_context_binds_refused() -> None:
    # the owner state belongs to a DIFFERENT resource than the
    # declared binding: the measured teardown can never be
    # claimed for the declared resource (either direction)
    owner = FakeCompletedOwner(export_payload=_valid_payload(), target_cid=FOREIGN_CID)
    with pytest.raises(fci.FixtureError, match="prep-native-owner-context-mismatch"):
        fp.produce_native_owner_record(
            fp.OwnedOwnerMeasurement(owner, subject=_cid_scoped_receipt()), **_producer_kwargs()
        )
    owner2 = FakeCompletedOwner(export_payload=_valid_payload())
    with pytest.raises(fci.FixtureError, match="prep-native-owner-context-mismatch"):
        fp.produce_native_owner_record(
            fp.OwnedOwnerMeasurement(owner2, subject=_cid_scoped_receipt()),
            **_producer_kwargs(cid=FOREIGN_CID),
        )


def test_real_owner_class_exposes_adapter_seam() -> None:
    # the REAL R/S owner class assigns the complete closed
    # seam the OwnedOwnerMeasurement adapter reads (AST check
    # only: no instantiation — the real backend is never
    # invoked in T)
    source = (REPO_ROOT / "scripts" / "cache_native_fixture_local.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    assigned: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "LocalFixtureOwner":
            for sub in ast.walk(node):
                if (
                    isinstance(sub, ast.Attribute)
                    and isinstance(sub.ctx, ast.Store)
                    and isinstance(sub.value, ast.Name)
                    and sub.value.id == "self"
                ):
                    assigned.add(sub.attr)
    required = {
        "export_payload",
        "descendants_before",
        "teardown_container_absent",
        "image_removed",
        "teardown_descendants_after",
        "sentinel_survived",
        "target_cid",
        "image_id",
        "run_id",
        "optin",
        "artifact",
    }
    missing = required - assigned
    assert not missing, f"real owner class missing adapter seam: {sorted(missing)}"


class _FakeDockerPlatform:
    """The scripted fake Docker platform operations for the
    REAL owner finish/export/teardown path (no real daemon,
    no real container): every response is the closed shape
    the real guarded path requires."""

    def __init__(
        self,
        *,
        cid: str,
        image_id: str,
        payload: bytes,
        quiesce: dict[str, Any],
        procs: dict[int, dict[str, Any]] | None = None,
    ) -> None:
        self._cid = cid
        self._image_id = image_id
        self._payload = payload
        self._quiesce = quiesce
        self._procs = procs
        self._ps_calls = 0
        self.calls: list[list[str]] = []

    def __call__(self, argv: list[str], timeout: float) -> Any:
        a = list(argv)
        self.calls.append(a)
        if (
            a[:4] == ["docker", "exec", "--user", "21002:21002"]
            and a[4] == self._cid
            and a[-2:] == ["--mode", "observe"]
        ):
            record = {
                "record": "slaif-fixture-standin-v1",
                "status": "pass",
                "mode": "observe",
                "uid": 21002,
                "scenario": "diagnostic",
                "wire_requests": 2,
                "diagnostic_state": "unobserved",
                "raw_content_retained": False,
            }
            return fci.ExecResult(0, (json.dumps(record) + "\n").encode("ascii"))
        if a[:4] == ["docker", "exec", "--user", "21001:21001"] and a[4] == self._cid:
            quiesce_line = b"quiesce-ok " + json.dumps(
                self._quiesce, sort_keys=True, separators=(",", ":")
            ).encode("ascii")
            data = (
                quiesce_line
                + b"\nexport-sha256 "
                + hashlib.sha256(self._payload).hexdigest().encode("ascii")
                + b"\n"
                + self._payload
            )
            return fci.ExecResult(0, data)
        if a[:2] == ["docker", "top"] and a[2] == self._cid:
            return fci.ExecResult(0, b"UID\tPID\nfixture\t4242\n")
        if a[:4] == ["docker", "ps", "-aq", "--filter"] and a[4] == f"id={self._cid}":
            self._ps_calls += 1
            if self._ps_calls == 1:
                return fci.ExecResult(0, self._cid.encode("ascii") + b"\n")
            return fci.ExecResult(0, b"")
        if a[:4] == ["docker", "ps", "-aq", "--filter"]:
            return fci.ExecResult(0, b"")
        if a[:2] == ["docker", "rm"] and a[-1] == self._cid:
            # the exact CID removal is what removes the
            # native subject from the coupled fake process
            # world (a scripted fake side effect, never a
            # pre-deleted world)
            if self._procs is not None:
                self._procs.pop(60, None)
            return fci.ExecResult(0, self._cid.encode("ascii") + b"\n")
        if a[:2] == ["docker", "rmi"] and a[2] == self._image_id:
            return fci.ExecResult(0, b"")
        if a[:3] == ["docker", "image", "inspect"] and a[3] == self._image_id:
            return fci.ExecResult(
                1, b"Error: No such image: " + self._image_id.encode("ascii") + b"\n"
            )
        raise AssertionError(f"unscripted platform command: {a}")


def test_real_owner_finish_teardown_drives_producer() -> None:
    # the full PUBLIC positive over the REAL owned
    # finish/export/teardown path, coupled to ONE shared fake
    # process world: the ACTUAL public workflow first measures
    # the native subject while the SAME CID is alive and
    # records the worker stop; the actual
    # LocalFixtureOwner.finish() + _teardown_verified() code is
    # THEN driven with FAKE platform operations whose exact CID
    # removal updates that SAME world to absent (no real
    # daemon; __init__ is skipped, so no S admission claim, no
    # signal handler, no control directory); the producer is
    # driven from the retained pre-teardown receipt, and the
    # same worker is restored before finalize composes.
    payload = _valid_payload()
    quiesce = json.loads(payload)["quiesce"]
    image_id = "sha256:" + "f" * 64
    # one shared fake process world: the SAME W worker job and
    # the native subject in the SAME CID, alive before teardown
    table, procs = _lifecycle_table()
    platform = _FakeDockerPlatform(
        cid=CID, image_id=image_id, payload=payload, quiesce=quiesce, procs=procs
    )
    wf = _workflow(table, channel=FakeCidScopedTable(CID, table.procs))
    snap = wf.prepare()  # native identity measured while the CID is alive
    assert snap["subject"] is not None
    assert snap["subject"]["cid_membership"] == "cid-scoped"
    # the operator stops the worker job (fake metadata only)
    procs[50] = _worker_proc("T", tpgid=40)
    wf.record_stop()
    budgets = fci.model.FixtureBudgets()
    deadline = fci._RunDeadline(time.monotonic() + fci.TOTAL_ANCHOR_SECONDS)
    ledger = fci._RunLedger(budgets)
    owner = object.__new__(flocal.LocalFixtureOwner)
    # The real __init__ always initializes this (None for the
    # ORIGINAL non-owner-UID form; this seam is that form): set
    # the faithful original default explicitly rather than
    # relying on any missing-attribute fallback in production.
    owner._owner_context = None
    owner._abort_by_caller = False
    owner.abort_path = None
    owner.state_path = None
    owner.target_cid = CID
    owner.phase = "prepare"
    owner.env_base = {}
    owner.budgets = budgets
    owner.ledger = ledger
    owner.guarded = fci._guarded_execute(platform, deadline, ledger)
    owner.run_id = RUN
    owner.consumed = None
    owner.sentinel = None
    owner.sentinel_survived = False
    owner.image_id = image_id
    owner.build_attempted = False
    owner.image_removed = False
    owner.cleanup_failures = []
    owner.created = []
    owner.descendants_before = 0
    owner.teardown_container_absent = None
    owner.teardown_descendants_after = None
    owner.export_payload = None
    owner.export_sha = ""
    owner.finish_observed = None
    owner.finish_position = None
    owner.finish_ledger_requests = None
    owner.phases_completed = set()
    owner.optin = {"order": "017-t", "bind_head": HEAD, "head": HEAD, "order_sha256": "e" * 64}
    owner.artifact = {"binary_sha256": BINARY}
    sentinel = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(3.0)"])
    try:
        owner.sentinel = sentinel
        owner.finish()
    finally:
        if sentinel.poll() is None:
            sentinel.kill()
        sentinel.wait(timeout=5)
    # the REAL path measured the closed facts on the owner
    assert owner.export_payload == payload
    assert owner.export_sha == hashlib.sha256(payload).hexdigest()
    assert owner.finish_ledger_requests == 2
    assert owner.finish_position is None
    assert owner.descendants_before == 1
    assert owner.teardown_container_absent is True
    assert owner.teardown_descendants_after == 0
    assert owner.image_removed is True
    assert owner.sentinel_survived is True
    # the SAME fake process world now reflects the measured
    # teardown: the native subject is gone from the host view
    # (removed by the exact CID removal, never pre-deleted)
    assert 60 not in procs
    assert table.pid_present(60) is True  # verified absence, same table
    # the real adapter over the REAL owner's measured state,
    # with the PUBLIC workflow's measured subject receipt (taken
    # while the SAME CID was alive) as the only native-fact
    # source
    measurement = fp.OwnedOwnerMeasurement(owner, subject=wf.subject_receipt)
    declared = {
        "order": wf.binding.order_id,
        "source_head": HEAD,
        "run_id": RUN,
        "cid": CID,
        "image_id": image_id,
        "binary_sha256": BINARY,
    }
    record = fp.produce_native_owner_record(measurement, **declared)
    assert record["image"] == {"image_id": image_id}  # measured form retained
    facts = fp.parse_native_owner_facts(record)
    assert facts.image_id == "f" * 64  # normalized bare digest
    assert facts.native_started is True and facts.native_ready is True
    # a declared binding that does not match the measured
    # owner state (even a different closed form) is refused
    # at the producer
    with pytest.raises(fci.FixtureError, match="prep-native-owner-context-mismatch"):
        fp.produce_native_owner_record(measurement, **dict(declared, image_id="f" * 64))
    # the operator restores the SAME worker job in the foreground
    procs[50] = _worker_proc("S", tpgid=50)
    verdict = wf.finalize(record)
    assert verdict.ready is True and verdict.reasons == ()


@pytest.mark.parametrize(
    "overrides",
    [
        {"payload": b""},
        {"payload": None},
        {"present_before": None},
        {"present_before": False},
        {"cid_absent": None},
        {"cid_absent": False},
        {"image_absent": None},
        {"image_absent": False},
        {"descendants": None},
        {"descendants": 1},
        {"descendants": True},
        {"sentinel": None},
        {"sentinel": False},
        {"native_started": None},
        {"native_started": False},
        {"native_ready": None},
        {"native_ready": "true"},
    ],
)
def test_producer_unmeasured_or_contradicted_refusals(overrides: dict[str, Any]) -> None:
    with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
        fp.produce_native_owner_record(FakeOwnerMeasurement(**overrides), **_producer_kwargs())


def test_producer_overbound_and_missing_seam_refusals() -> None:
    with pytest.raises(fci.FixtureError, match="prep-export-overbound"):
        fp.produce_native_owner_record(
            FakeOwnerMeasurement(), max_export_bytes=10, **_producer_kwargs()
        )
    for broken in (object(), 42, {"export_payload": b"x"}):
        with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
            fp.produce_native_owner_record(broken, **_producer_kwargs())


def test_producer_tampered_record_still_refused_by_consumer() -> None:
    rec = fp.produce_native_owner_record(FakeOwnerMeasurement(), **_producer_kwargs())
    tampered = dict(rec)
    tampered["native_ready"] = "true"
    with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
        fp.parse_native_owner_facts(tampered)
    tampered2 = dict(rec)
    # the consumer re-checks the closed record grammar (the digest
    # itself is bound to the payload only at the producer): a
    # zero-byte export is refused by the consumer law
    tampered2["export"] = {"bytes": 0, "sha256": "f" * 64}
    with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
        fp.parse_native_owner_facts(tampered2)


def test_native_owner_parser_negatives() -> None:
    cases = [
        _native_owner_record(status="fail"),
        _native_owner_record(record=fp.OWNER_FACTS_SCHEMA),
        _native_owner_record(producer="someone-else"),
        _native_owner_record(order="017"),
        _native_owner_record(source_head="z" * 39),
        _native_owner_record(run_id="x" * 31),
        _native_owner_record(prepared={"cid": "z" * 64}),
        _native_owner_record(image={"image_id": "z" * 64}),
        _native_owner_record(export={"bytes": 0, "sha256": "7" * 64}),
        _native_owner_record(export={"bytes": True, "sha256": "7" * 64}),
        _native_owner_record(native_started=False),
        _native_owner_record(
            teardown={
                "container_present_before": True,
                "container_removal": "absent-verified",
                "image_removal": "absent-verified",
                "descendants_after": 2,
                "sentinel_survived": True,
            }
        ),
    ]
    for rec in cases:
        with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
            fp.parse_native_owner_facts(rec)
    for not_a_mapping in (None, "pass", ["pass"]):
        with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
            fp.parse_native_owner_facts(not_a_mapping)


def test_native_owner_parser_closed_keys() -> None:
    # the closed record grammar: the valid baseline parses, and
    # any unknown or missing field (top level or nested, or a
    # non-mapping nested object) is a closed non-echoing
    # refusal before the record is used
    fp.parse_native_owner_facts(_native_owner_record())  # valid baseline
    extra = _native_owner_record()
    extra["unexpected_field"] = "fixed-synthetic-value"
    with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
        fp.parse_native_owner_facts(extra)
    for key in sorted(_native_owner_record()):
        missing = _native_owner_record()
        del missing[key]
        with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
            fp.parse_native_owner_facts(missing)
    nested_extra = _native_owner_record()
    nested_extra["teardown"] = dict(nested_extra["teardown"], extra="x")
    with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
        fp.parse_native_owner_facts(nested_extra)
    nested_nonmapping = _native_owner_record()
    nested_nonmapping["prepared"] = "cid"
    with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
        fp.parse_native_owner_facts(nested_nonmapping)
    # the truthful negative (started-but-not-ready) still PARSES:
    # the closed grammar validates shape, the verdict refuses
    # readiness
    not_ready = _native_owner_record(native_ready=False)
    assert fp.parse_native_owner_facts(not_ready).native_ready is False


def test_expectation_from_owner() -> None:
    owner = fp.parse_owner_final_facts(_owner_record())
    exp = fp.expectation_from_owner(owner, min_start_time=400, expected_tty=TTYS)
    assert exp.cid == CID and exp.binary_sha256 == BINARY and exp.run_id == RUN
    assert exp.attestation == "registered-owner-record"
    assert exp.min_start_time == 400 and exp.expected_tty == TTYS
    native = fp.parse_native_owner_facts(_native_owner_record())
    exp2 = fp.expectation_from_owner(native, min_start_time=None, expected_tty=None)
    assert exp2.cid == CID and exp2.attestation == "registered-owner-record"
    assert exp2.min_start_time is None and exp2.expected_tty is None
    # a raw map is not an owner record
    with pytest.raises(fci.FixtureError, match="prep-owner-record-malformed"):
        fp.expectation_from_owner({"cid": CID}, min_start_time=None, expected_tty=None)


# -- verdict composition --------------------------------------------------------------


def _measured_subject() -> Any:
    table = FakeTable({60: subject_proc(60, cgroup=CID)})
    return fp.collect_subject_identity(
        table, 60, _expectation(), channel=FakeCidScopedTable(CID, table.procs)
    )


def _ready_triple() -> tuple[Any, Any, Any]:
    # the ready composition is a NATIVE-scope owner: the
    # historical S scope can never qualify it
    owner = fp.parse_native_owner_facts(_native_owner_record())
    subject = _measured_subject()
    restoration = fp.collect_restoration(
        _job_table(worker_state="S", worker_tpgid=50), 50, 40, 50, stop_receipt=_stop_receipt()
    )
    return owner, subject, restoration


def test_verdict_ready_composition() -> None:
    owner, subject, restoration = _ready_triple()
    verdict = fp.compose_handoff_verdict(owner, subject, restoration, subject_absent=True)
    assert verdict.ready is True and verdict.reasons == ()


def test_verdict_missing_fact_matrix() -> None:
    owner, subject, restoration = _ready_triple()
    v = fp.compose_handoff_verdict(None, subject, restoration, subject_absent=True)
    assert v.ready is False and v.reasons == ("no-owner-final",)
    weak_owner = dataclasses.replace(owner, teardown_verified=False)
    v = fp.compose_handoff_verdict(weak_owner, subject, restoration, subject_absent=True)
    assert v.reasons == ("owner-teardown-unverified",)
    # a historical S-scope owner is never native-ready: the
    # closed scope refusal composes alongside its own facts
    s_owner = fp.parse_owner_final_facts(_owner_record())
    v = fp.compose_handoff_verdict(s_owner, subject, restoration, subject_absent=True)
    assert v.ready is False and v.reasons == ("owner-scope-not-native",)
    foreign_owner = fp.parse_native_owner_facts(_native_owner_record(prepared={"cid": FOREIGN_CID}))
    v = fp.compose_handoff_verdict(foreign_owner, subject, restoration, subject_absent=True)
    assert v.reasons == ("owner-subject-context-mismatch",)
    foreign_run = fp.parse_native_owner_facts(_native_owner_record(run_id="d" * 32))
    v = fp.compose_handoff_verdict(foreign_run, subject, restoration, subject_absent=True)
    assert v.reasons == ("owner-subject-context-mismatch",)
    unbound = dataclasses.replace(subject, start_bound=False)
    v = fp.compose_handoff_verdict(owner, unbound, restoration, subject_absent=True)
    assert v.reasons == ("subject-start-unbound",)
    # a cid-scoped subject whose executable was not measured
    table_unmeasured = FakeTable({60: subject_proc(60, cgroup=CID)})
    unmeasured = fp.collect_subject_identity(
        table_unmeasured,
        60,
        _expectation(),
        channel=FakeCidScopedTable(CID, table_unmeasured.procs, exe_digest=None),
    )
    v = fp.compose_handoff_verdict(owner, unmeasured, restoration, subject_absent=True)
    assert v.reasons == ("subject-binary-unmeasured",)
    # a raw host-table observation: unscoped AND unmeasured
    unscoped = fp.collect_subject_identity(FakeTable({60: subject_proc(60)}), 60, _expectation())
    v = fp.compose_handoff_verdict(owner, unscoped, restoration, subject_absent=True)
    assert v.reasons == ("subject-cid-unscoped", "subject-binary-unmeasured")
    v = fp.compose_handoff_verdict(owner, None, restoration, subject_absent=True)
    assert v.reasons == ("no-native-identity",)
    v = fp.compose_handoff_verdict(owner, subject, restoration)  # absence unverified
    assert v.reasons == ("subject-absence-unverified",)
    v = fp.compose_handoff_verdict(owner, subject, restoration, subject_absent=False)
    assert v.reasons == ("subject-absence-unverified",)
    v = fp.compose_handoff_verdict(owner, subject, None, subject_absent=True)
    assert v.reasons == ("no-restoration",)
    no_stop = fp.collect_restoration(_job_table(worker_state="S", worker_tpgid=50), 50, 40, 50)
    v = fp.compose_handoff_verdict(owner, subject, no_stop, subject_absent=True)
    assert v.reasons == ("worker-stop-unmeasured",)
    not_restored = fp.collect_restoration(
        _job_table(worker_state="T", worker_tpgid=40), 50, 40, 50, stop_receipt=_stop_receipt()
    )
    v = fp.compose_handoff_verdict(owner, subject, not_restored, subject_absent=True)
    assert v.reasons == ("same-job-restore-unmeasured",)
    all_missing = fp.compose_handoff_verdict(None, None, None)
    assert all_missing.reasons == ("no-owner-final", "no-native-identity", "no-restoration")


def test_verdict_owner_subject_agreement_refusals() -> None:
    owner, subject, restoration = _ready_triple()
    # the owner's registered artifact differs from the measured
    # subject executable: same CID/run strings cannot substitute
    # for exact executable agreement
    other = fp.parse_native_owner_facts(
        _native_owner_record(artifact={"binary_sha256": OTHER_BINARY})
    )
    v = fp.compose_handoff_verdict(other, subject, restoration, subject_absent=True)
    assert v.ready is False and v.reasons == ("owner-subject-binary-mismatch",)
    # an otherwise valid native-owner record that honestly says
    # started-but-NOT-ready can never qualify the composition
    not_ready = fp.parse_native_owner_facts(_native_owner_record(native_ready=False))
    v = fp.compose_handoff_verdict(not_ready, subject, restoration, subject_absent=True)
    assert v.ready is False and v.reasons == ("owner-native-unready",)
    # a subject whose expected PTY was never bound (unobserved
    # expectation) cannot qualify the visible native handoff
    table = FakeTable({60: subject_proc(60, cgroup=CID)})
    unbound = fp.collect_subject_identity(
        table, 60, _expectation(expected_tty=None), channel=FakeCidScopedTable(CID, table.procs)
    )
    v = fp.compose_handoff_verdict(owner, unbound, restoration, subject_absent=True)
    assert v.ready is False and v.reasons == ("subject-pty-unmatched",)
    # a measured tty0/tpgid-1 no-TTY subject cannot either
    table0 = FakeTable({60: subject_proc(60, cgroup=CID, tty=0, tpgid=-1)})
    no_tty = fp.collect_subject_identity(
        table0, 60, _expectation(expected_tty=None), channel=FakeCidScopedTable(CID, table0.procs)
    )
    v = fp.compose_handoff_verdict(owner, no_tty, restoration, subject_absent=True)
    assert v.ready is False and v.reasons == ("subject-pty-unmatched",)


def test_verdict_refuses_fabricated_flags() -> None:
    owner, subject, restoration = _ready_triple()
    for position in range(4):
        args: list[Any] = [owner, subject, restoration]
        kwargs: dict[str, Any] = {"subject_absent": True}
        if position < 3:
            args[position] = {"ready": True}
        else:
            kwargs["subject_absent"] = {"ready": True}
        with pytest.raises(fci.FixtureError, match="prep-verdict-input-invalid"):
            fp.compose_handoff_verdict(*args, **kwargs)


# -- the public workflow ---------------------------------------------------------------------------


def _workflow(
    table: FakeTable,
    *,
    channel: FakeCidScopedTable | None = None,
    with_subject: bool = True,
) -> Any:
    return fp.NativeHandoffWorkflow(
        _binding(),
        table,
        worker_pid=50,
        bash_pid=40,
        subject_pid=60 if with_subject else None,
        expectation=_expectation() if with_subject else None,
        owner_run_id=RUN,
        tty_foreground_pgrp=50,
        channel=channel,
    )


def _lifecycle_table() -> tuple[FakeTable, dict[int, dict[str, Any]]]:
    procs: dict[int, dict[str, Any]] = {
        40: bash_proc(40, state="S", pgrp=40),
        50: _worker_proc("S", tpgid=50),
        60: subject_proc(60, cgroup=CID),
    }
    return FakeTable(procs), procs


def test_workflow_rejects_unprepared_and_prepopulated() -> None:
    table = _job_table()
    wf = fp.NativeHandoffWorkflow(_binding(), table, worker_pid=50, bash_pid=40)
    with pytest.raises(fci.FixtureError, match="prep-not-prepared"):
        wf.observe()
    with pytest.raises(fci.FixtureError, match="prep-not-prepared"):
        wf.finalize(_owner_record())
    with pytest.raises(fci.FixtureError, match="prep-not-prepared"):
        wf.record_stop()
    # a constructor or manually prepopulated record is not workflow
    # evidence: there is no facts parameter to prepopulate
    import inspect

    params = inspect.signature(fp.NativeHandoffWorkflow.__init__).parameters
    assert not any(p in params for p in ("facts", "record", "group", "subject", "restoration"))
    with pytest.raises(TypeError):
        fp.NativeHandoffWorkflow(
            _binding(), table, worker_pid=50, bash_pid=40, subject={"ready": True}
        )
    with pytest.raises(fci.FixtureError, match="prep-binding-invalid"):
        fp.NativeHandoffWorkflow({"order_id": "017-t"}, table)
    with pytest.raises(fci.FixtureError, match="prep-binding-invalid"):
        fp.NativeHandoffWorkflow(_binding(), table, owner_run_id="nope")


def test_workflow_prepare_collects_before_recording() -> None:
    table, _ = _lifecycle_table()
    wf = _workflow(table, channel=FakeCidScopedTable(CID, table.procs))
    snap = wf.prepare()
    fp.validate_prep_snapshot(snap)
    assert snap["record"] == fp.NATIVE_PREP_SCHEMA
    assert snap["binding"] == _binding().to_record()
    assert snap["group"]["worker"]["pid"] == 50
    assert snap["group"]["worker"]["start_time"] == 500
    assert snap["group"]["bash"]["pid"] == 40
    assert snap["group"]["bash"]["start_time"] == 100
    assert snap["subject"] is not None
    assert snap["subject"]["argv"] == list(CODEX_ARGV)
    assert snap["subject"]["cid_membership"] == "cid-scoped"
    assert snap["subject"]["binary_sha256"] == BINARY
    # observe RE-COLLECTS (a changed table is re-measured, not replayed)
    table.procs[50] = _worker_proc("T", tpgid=40)
    snap2 = wf.observe()
    assert snap2["group"]["worker"]["state"] == "T"
    assert snap2["subject"]["start_time"] == 500  # the same subject process
    # raw host content is not retained: no comm/env beyond the closed fields
    assert "comm" not in snap["group"]["worker"]
    assert set(snap["group"]["worker"]) == {"pid", "state", "pgrp", "session", "tty", "start_time"}


def test_workflow_observe_refuses_substituted_worker() -> None:
    table, procs = _lifecycle_table()
    wf = _workflow(table)
    wf.prepare()
    # the worker is substituted (PID reuse with a new birth)
    procs[50] = _worker_proc("S", tpgid=50, start=999)
    with pytest.raises(fci.FixtureError, match="prep-worker-invalid"):
        wf.observe()
    # a repeated prepare must not reset the frozen baseline either
    with pytest.raises(fci.FixtureError, match="prep-worker-invalid"):
        wf.prepare()
    # and a stop recorded after the substitution is refused
    procs[50] = _worker_proc("T", tpgid=40, start=999)
    with pytest.raises(fci.FixtureError, match="prep-worker-invalid"):
        wf.record_stop()
    # a substituted BASH is refused the same way
    table2, procs2 = _lifecycle_table()
    wf2 = _workflow(table2)
    wf2.prepare()
    procs2[40] = bash_proc(40, state="S", pgrp=40, start=777)
    with pytest.raises(fci.FixtureError, match="prep-bash-invalid"):
        wf2.observe()


def test_workflow_observe_refuses_reused_subject_pid() -> None:
    table, procs = _lifecycle_table()
    wf = _workflow(table, channel=FakeCidScopedTable(CID, table.procs))
    wf.prepare()
    # a different process reuses pid 60 (new birth): the receipt
    # is retained, the substitution is refused, never adopted
    procs[60] = subject_proc(60, cgroup=CID, start=800)
    with pytest.raises(fci.FixtureError, match="prep-subject-invalid"):
        wf.observe()


def test_public_lifecycle_native_owner_producer_ready() -> None:
    # the full PUBLIC positive: same running worker baseline ->
    # measured stable stop -> native identity collected inside the
    # registered CID -> the REAL owned adapter over a completed
    # native-owner state (faked backend), with the workflow's
    # measured subject receipt as the only native-fact source ->
    # the ACTUAL producer validates the full payload and binds
    # the measured context to the declared binding -> subject
    # proven absent -> same worker restored -> positive composite
    table, procs = _lifecycle_table()
    wf = _workflow(table, channel=FakeCidScopedTable(CID, table.procs))
    snap = wf.prepare()
    fp.validate_prep_snapshot(snap)
    assert snap["subject"] is not None
    assert snap["subject"]["binary_verified"] is True
    # the same process re-observed non-consuming
    assert wf.observe()["subject"]["start_time"] == 500
    # the operator stops the worker job (fake metadata only — no signal)
    procs[50] = _worker_proc("T", tpgid=40)
    receipt = wf.record_stop()
    assert (receipt.worker_pid, receipt.worker_pgrp, receipt.worker_tpgid) == (50, 50, 40)
    assert wf.record_stop() is receipt  # recorded event, never re-measured
    # the native subject's teardown: the pid entry is proven missing
    del procs[60]
    # the operator restores the same job in the foreground
    procs[50] = _worker_proc("S", tpgid=50)
    # the completed native-owner state (faked backend) is
    # measured through the REAL owned adapter; the declared
    # binding is derived from the workflow's verified binding +
    # registered run + registered expectation — an INDEPENDENT
    # source from the measured owner state, which the producer
    # cross-checks exactly
    owner = FakeCompletedOwner(export_payload=_valid_payload())
    measurement = fp.OwnedOwnerMeasurement(owner, subject=wf.subject_receipt)
    expectation = _expectation()
    declared = {
        "order": wf.binding.order_id,  # the bound order of this handoff
        "source_head": wf.binding.source_head,
        "run_id": RUN,
        "cid": expectation.cid,
        "image_id": owner.image_id,
        "binary_sha256": expectation.binary_sha256,
    }
    owner_record = fp.produce_native_owner_record(measurement, **declared)
    payload = owner.export_payload
    assert payload is not None
    assert owner_record["export"]["sha256"] == hashlib.sha256(payload).hexdigest()
    assert owner_record["run_id"] == RUN
    # a declared binding that does NOT match the measured owner
    # state is refused at the producer (never a workflow fact)
    with pytest.raises(fci.FixtureError, match="prep-native-owner-context-mismatch"):
        fp.produce_native_owner_record(measurement, **dict(declared, cid=FOREIGN_CID))
    verdict = wf.finalize(owner_record)
    assert verdict.ready is True and verdict.reasons == ()


def test_public_lifecycle_s_record_still_accepted() -> None:
    # the historical S rehearsal record still decodes and
    # validates as its own scope (never relabeled as
    # native), but it can NEVER qualify a native-ready
    # composition: the cross-scope verdict composes the
    # closed scope refusal alongside its measured facts
    table, procs = _lifecycle_table()
    wf = _workflow(table, channel=FakeCidScopedTable(CID, table.procs))
    wf.prepare()
    procs[50] = _worker_proc("T", tpgid=40)
    wf.record_stop()
    del procs[60]
    procs[50] = _worker_proc("S", tpgid=50)
    verdict = wf.finalize(_owner_record())
    assert verdict.ready is False
    assert verdict.reasons == ("owner-scope-not-native",)


def _stopped_public_workflow(
    expectation: Any | None = None,
) -> tuple[Any, dict[int, Any]]:
    table, procs = _lifecycle_table()
    wf = fp.NativeHandoffWorkflow(
        _binding(),
        table,
        worker_pid=50,
        bash_pid=40,
        subject_pid=60,
        expectation=_expectation() if expectation is None else expectation,
        owner_run_id=RUN,
        tty_foreground_pgrp=50,
        channel=FakeCidScopedTable(CID, table.procs),
    )
    wf.prepare()
    procs[50] = _worker_proc("T", tpgid=40)
    wf.record_stop()
    return wf, procs


def test_public_lifecycle_owner_subject_agreement() -> None:
    # the full PUBLIC agreement law end-to-end: a changed owner
    # registered binary, an honest started-but-not-ready record,
    # and an unknown owner field all refuse the native-ready
    # composition; the valid same-owner positive above composes
    # ready
    wf, procs = _stopped_public_workflow()
    owner = FakeCompletedOwner(export_payload=_valid_payload(), binary_sha256=OTHER_BINARY)
    measurement = fp.OwnedOwnerMeasurement(owner, subject=wf.subject_receipt)
    record = fp.produce_native_owner_record(
        measurement,
        order=wf.binding.order_id,
        source_head=HEAD,
        run_id=RUN,
        cid=CID,
        image_id=owner.image_id,
        binary_sha256=OTHER_BINARY,
    )
    del procs[60]
    procs[50] = _worker_proc("S", tpgid=50)
    verdict = wf.finalize(record)
    # both boundaries bind the agreement: the adapter's honest
    # started-but-not-ready fact and the composition's exact
    # executable agreement
    assert verdict.ready is False
    assert verdict.reasons == ("owner-native-unready", "owner-subject-binary-mismatch")
    # the honest started-but-not-ready record is retained as a
    # truthful negative and still refused by the composition
    wf2, procs2 = _stopped_public_workflow()
    owner2 = FakeCompletedOwner(export_payload=_valid_payload())
    record2 = fp.produce_native_owner_record(
        fp.OwnedOwnerMeasurement(owner2, subject=wf2.subject_receipt),
        order=wf2.binding.order_id,
        source_head=HEAD,
        run_id=RUN,
        cid=CID,
        image_id=owner2.image_id,
        binary_sha256=BINARY,
    )
    record2["native_ready"] = False
    del procs2[60]
    procs2[50] = _worker_proc("S", tpgid=50)
    verdict2 = wf2.finalize(record2)
    assert verdict2.ready is False and "owner-native-unready" in verdict2.reasons
    # an unknown field in the closed owner record is a closed
    # non-echoing refusal (never a silent composition)
    wf3, procs3 = _stopped_public_workflow()
    owner3 = FakeCompletedOwner(export_payload=_valid_payload())
    record3 = fp.produce_native_owner_record(
        fp.OwnedOwnerMeasurement(owner3, subject=wf3.subject_receipt),
        order=wf3.binding.order_id,
        source_head=HEAD,
        run_id=RUN,
        cid=CID,
        image_id=owner3.image_id,
        binary_sha256=BINARY,
    )
    record3["unexpected_field"] = "fixed-synthetic-value"
    with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
        wf3.finalize(record3)
    _ = procs3  # the world is left untouched (no mutation happened)


def test_public_lifecycle_unbound_pty_never_ready() -> None:
    # an explicitly unobserved expected PTY still produces a
    # fully measured subject, but it can never qualify the
    # visible native handoff
    wf, procs = _stopped_public_workflow(expectation=_expectation(expected_tty=None))
    record = fp.produce_native_owner_record(FakeOwnerMeasurement(), **_producer_kwargs())
    del procs[60]
    procs[50] = _worker_proc("S", tpgid=50)
    verdict = wf.finalize(record)
    assert verdict.ready is False and verdict.reasons == ("subject-pty-unmatched",)


def test_public_lifecycle_no_tty_subject_never_ready() -> None:
    # a measured tty0/tpgid-1 no-TTY subject (legitimate
    # metadata parsing) can never qualify the visible native
    # handoff
    table, procs = _lifecycle_table()
    procs[60] = subject_proc(60, cgroup=CID, tty=0, tpgid=-1)
    wf = fp.NativeHandoffWorkflow(
        _binding(),
        table,
        worker_pid=50,
        bash_pid=40,
        subject_pid=60,
        expectation=_expectation(expected_tty=None),
        owner_run_id=RUN,
        tty_foreground_pgrp=50,
        channel=FakeCidScopedTable(CID, table.procs),
    )
    wf.prepare()
    procs[50] = _worker_proc("T", tpgid=40)
    wf.record_stop()
    record = fp.produce_native_owner_record(FakeOwnerMeasurement(), **_producer_kwargs())
    del procs[60]
    procs[50] = _worker_proc("S", tpgid=50)
    verdict = wf.finalize(record)
    assert verdict.ready is False and verdict.reasons == ("subject-pty-unmatched",)


def test_public_lifecycle_adversarial_negatives() -> None:
    # absence NOT proven (entry unreadable): an unknown, never a
    # verified absence — not ready
    table, procs = _lifecycle_table()
    table._absent = {60}
    wf = _workflow(table, channel=FakeCidScopedTable(CID, table.procs))
    wf.prepare()
    procs[50] = _worker_proc("T", tpgid=40)
    wf.record_stop()
    procs[50] = _worker_proc("S", tpgid=50)
    verdict = wf.finalize(
        fp.produce_native_owner_record(FakeOwnerMeasurement(), **_producer_kwargs())
    )
    assert verdict.ready is False and verdict.reasons == ("subject-absence-unverified",)
    # the subject was never torn down: still present — not ready
    table2, procs2 = _lifecycle_table()
    wf2 = _workflow(table2, channel=FakeCidScopedTable(CID, table2.procs))
    wf2.prepare()
    procs2[50] = _worker_proc("T", tpgid=40)
    wf2.record_stop()
    procs2[50] = _worker_proc("S", tpgid=50)
    verdict2 = wf2.finalize(
        fp.produce_native_owner_record(FakeOwnerMeasurement(), **_producer_kwargs())
    )
    assert verdict2.ready is False and verdict2.reasons == ("subject-absence-unverified",)
    # no stop was ever recorded
    table3, procs3 = _lifecycle_table()
    wf3 = _workflow(table3, channel=FakeCidScopedTable(CID, table3.procs))
    wf3.prepare()
    del procs3[60]
    verdict3 = wf3.finalize(
        fp.produce_native_owner_record(FakeOwnerMeasurement(), **_producer_kwargs())
    )
    assert verdict3.ready is False and verdict3.reasons == ("worker-stop-unmeasured",)
    # the worker was never restored (still stopped at finalize)
    table4, procs4 = _lifecycle_table()
    wf4 = _workflow(table4, channel=FakeCidScopedTable(CID, table4.procs))
    wf4.prepare()
    procs4[50] = _worker_proc("T", tpgid=40)
    wf4.record_stop()
    del procs4[60]
    verdict4 = wf4.finalize(
        fp.produce_native_owner_record(FakeOwnerMeasurement(), **_producer_kwargs())
    )
    assert verdict4.ready is False and verdict4.reasons == ("same-job-restore-unmeasured",)
    # a native-owner record with a foreign CID is not this context
    table5, procs5 = _lifecycle_table()
    wf5 = _workflow(table5, channel=FakeCidScopedTable(CID, table5.procs))
    wf5.prepare()
    procs5[50] = _worker_proc("T", tpgid=40)
    wf5.record_stop()
    del procs5[60]
    procs5[50] = _worker_proc("S", tpgid=50)
    # a record whose MEASURED context is the foreign CID is a
    # valid record for THAT resource — the workflow (not the
    # producer) composes the context mismatch
    foreign = fp.produce_native_owner_record(
        FakeOwnerMeasurement(context=_producer_context(cid=FOREIGN_CID)),
        **_producer_kwargs(cid=FOREIGN_CID),
    )
    verdict5 = wf5.finalize(foreign)
    assert verdict5.ready is False and verdict5.reasons == ("owner-subject-context-mismatch",)
    # an S record claiming native facts is refused by its closed law
    with pytest.raises(fci.FixtureError, match="prep-owner-record-malformed"):
        wf5.finalize(_owner_record(native_started=True))
    # a native-owner record that never started native is out of scope
    with pytest.raises(fci.FixtureError, match="prep-native-owner-record-malformed"):
        fp.produce_native_owner_record(
            FakeOwnerMeasurement(native_started=False), **_producer_kwargs()
        )


def test_workflow_finalize_owner_dispatch_and_run_binding() -> None:
    table = _job_table()
    wf = fp.NativeHandoffWorkflow(_binding(), table, worker_pid=50, bash_pid=40, owner_run_id=RUN)
    wf.prepare()
    verdict = wf.finalize(_owner_record())
    assert verdict.ready is False  # no subject observed: never ready
    assert "no-native-identity" in verdict.reasons
    # an unknown record schema is a closed refusal
    bad = _owner_record()
    bad["record"] = "some-other-schema"
    with pytest.raises(fci.FixtureError, match="prep-owner-record-malformed"):
        wf.finalize(bad)
    # a run binding mismatch is refused for BOTH owner scopes
    wf2 = fp.NativeHandoffWorkflow(
        _binding(), _job_table(), worker_pid=50, bash_pid=40, owner_run_id=RUN
    )
    wf2.prepare()
    with pytest.raises(fci.FixtureError, match="prep-owner-run-mismatch"):
        wf2.finalize(_owner_record(run_id="d" * 32))
    wf3 = fp.NativeHandoffWorkflow(
        _binding(), _job_table(), worker_pid=50, bash_pid=40, owner_run_id=RUN
    )
    wf3.prepare()
    with pytest.raises(fci.FixtureError, match="prep-owner-run-mismatch"):
        wf3.finalize(_native_owner_record(run_id="d" * 32))


def test_workflow_vanished_subject_receipt_retained() -> None:
    table, procs = _lifecycle_table()
    wf = _workflow(table, channel=FakeCidScopedTable(CID, table.procs))
    snap = wf.prepare()
    assert snap["subject"] is not None
    del procs[60]  # the subject vanished after registration
    verdict = wf.finalize(_native_owner_record())
    # the receipt is retained (never re-collected/replaced): the
    # identity exists and its absence is verified; the only
    # missing fact is the unrecorded stop
    assert verdict.reasons == ("worker-stop-unmeasured",)


# -- real /proc table mechanics (tiny exact-owned children only) -------------------


def _synthetic_proc_root(tmp_path: Path, *, cid: str, pid: int = 42, start: int = 500) -> Path:
    """A synthetic bounded /proc root for the REAL table
    classes: one process entry in the registered CID's
    cgroup scope, with a real regular exe file behind the
    magic-link symlink."""
    proc = tmp_path / str(pid)
    proc.mkdir()
    (proc / "stat").write_text(
        stat_line(pid, "codex", "S", 1, pid, 77, TTYS, pid, start), encoding="ascii"
    )
    (proc / "cgroup").write_text(f"0::/system.slice/docker-{cid}.scope\n", encoding="ascii")
    (proc / "cmdline").write_bytes(CODEX_CMDLINE)
    (proc / "status").write_bytes(status_bytes(21002, 21002, (21002,)))
    exe_target = tmp_path / "fake-native-binary"
    exe_target.write_bytes(b"fake-native-binary-bytes")
    os.symlink(exe_target, proc / "exe")
    return tmp_path


def test_real_cid_scoped_table_synthetic_proc(tmp_path: Path) -> None:
    root = _synthetic_proc_root(tmp_path, cid=CID)
    table = fp.RealCidScopedTable(CID, root=root)
    assert table.cid == CID
    assert table.cgroup_scope(42) == f"docker-{CID}.scope"
    assert table.stat(42) is not None
    assert table.cmdline(42) == CODEX_CMDLINE
    assert table.status(42) is not None
    assert table.pid_present(42) is False  # present, scope readable
    assert table.pid_present(99999) is True  # proven missing
    digest = fp.hashlib.sha256(b"fake-native-binary-bytes").hexdigest()
    assert table.exe_sha256(42, 500) == digest
    # the wrong (pid, birth) pair is a closed refusal
    with pytest.raises(fci.FixtureError, match="prep-subject-invalid"):
        table.exe_sha256(42, 499)
    # a foreign registered CID never sees the entry
    foreign = fp.RealCidScopedTable(FOREIGN_CID, root=root)
    assert foreign.cgroup_scope(42) is None
    assert foreign.stat(42) is None
    assert foreign.exe_sha256(42, 500) is None
    assert foreign.pid_present(42) is None  # unreadable scope: unknown
    # the channel never enumerates the host
    with pytest.raises(fci.FixtureError, match="prep-channel-no-enumeration"):
        table.list_pids()
    # over-bound total bytes and an expired deadline are closed
    with pytest.raises(fci.FixtureError, match="prep-proc-overbound"):
        fp.RealCidScopedTable(CID, root=root, max_exe_bytes=10).exe_sha256(42, 500)
    with pytest.raises(fci.FixtureError, match="prep-exe-timeout"):
        fp.RealCidScopedTable(CID, root=root, exe_deadline=-1.0).exe_sha256(42, 500)


def test_real_cid_scoped_table_exec_swap_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # an exec in the same process (the magic link now resolves
    # to a DIFFERENT file) is a closed refusal after the hash —
    # a same-descriptor fstat and an unchanged birth alone
    # cannot detect it
    root = _synthetic_proc_root(tmp_path, cid=CID)
    other = tmp_path / "swapped-binary"
    other.write_bytes(b"swapped-native-binary")
    exe_path = root / "42" / "exe"
    real_open = os.open
    state = {"opens": 0}

    def fake_open(path: str | Path, flags: int, mode: int = 0o777) -> int:
        if Path(path) == exe_path:
            state["opens"] += 1
            if state["opens"] >= 2:
                return real_open(other, flags)
        return real_open(path, flags, mode)

    monkeypatch.setattr(fp.os, "open", fake_open)
    table = fp.RealCidScopedTable(CID, root=root)
    with pytest.raises(fci.FixtureError, match="prep-exe-changed"):
        table.exe_sha256(42, 500)


def test_real_proc_table_pid_present() -> None:
    table = fp.RealProcTable()
    assert table.pid_present(os.getpid()) is False  # this process is present
    assert table.pid_present(1 << 22) is True  # far beyond any live pid


def test_real_proc_table_tiny_owned_child() -> None:
    # the REAL /proc reader against the test's own short-lived
    # exact-owned Python child (the child outlives the reads:
    # the test's exact-owned cleanup kills the exact child if
    # it is still alive, then waits it out)
    child = subprocess.Popen(
        [sys.executable, "-c", "import os, time; print(os.getpid(), flush=True); time.sleep(2.0)"],
        stdout=subprocess.PIPE,
    )
    try:
        out = child.stdout
        assert out is not None
        pid_line = out.readline().decode("ascii").strip()
        pid = int(pid_line)
        table = fp.RealProcTable()
        raw = table.stat(pid)
        assert raw is not None
        parsed = fp.parse_proc_stat(raw.decode("ascii"))
        assert parsed.pid == pid
        assert parsed.state in fp._RUNNING_STATES
        assert parsed.ppid == os.getpid()
        assert table.pid_present(pid) is False
        status = table.status(pid)
        assert status is not None
        uid, gid, groups = fp.parse_proc_status(status)
        assert uid == os.getuid() and gid == os.getgid()
        # absent-pid negative: a far pid is a proven absence
        assert table.pid_present(1 << 22) is True
    finally:
        if child.poll() is None:
            child.kill()
        child.wait(timeout=5)
    # the killed (or already exited) child's entry is proven
    # missing once it is gone
    for _ in range(50):
        if fp.RealProcTable().pid_present(pid) is True:
            break
        time.sleep(0.1)
    assert fp.RealProcTable().pid_present(pid) is True


# -- static law (closed execution surface) -----------------------------------------


def test_prep_module_has_no_execution_surface() -> None:
    # the preparation module NEVER imports or calls the
    # process-execution surface: no subprocess/signal/pty/
    # ctypes, and no kill/fork/exec/system/popen/os.kill*
    # calls anywhere
    source = PREP_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not imported & {"subprocess", "signal", "pty", "ctypes"}
    banned_attrs = {
        "kill",
        "killpg",
        "system",
        "popen",
        "execv",
        "execl",
        "execve",
        "execlp",
        "fork",
        "forkpty",
        "send_signal",
        "spawnl",
        "spawnv",
    }
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "os"
            and node.attr in banned_attrs
        ):
            raise AssertionError(f"banned os surface in prep module: os.{node.attr}")
        if isinstance(node, ast.Name) and node.id in banned_attrs:
            raise AssertionError(f"banned name in prep module: {node.id}")


def test_prep_reasons_closed_vocabulary() -> None:
    # every closed refusal token the module can raise is in
    # the declared vocabulary (and the vocabulary is live)
    source = PREP_PATH.read_text(encoding="utf-8")
    tokens = set(re.findall(r'FixtureError\("(prep-[a-z0-9-]+)"\)', source))
    assert tokens
    assert tokens <= set(fp.PREP_REASONS)


# -- complete-group observation: vanished vs unreadable (017-u) --------------------


class _TriStateTable(FakeTable):
    """A listed pid whose stat read returns None while the entry
    itself tri-states: still existing (pid_present False),
    independently verified gone (True), or unknown (absent set).
    ``hidden`` pids stay in the (possibly stale) listing."""

    def __init__(self, procs: dict[int, dict[str, Any]]) -> None:
        super().__init__(procs)
        self.hidden: set[int] = set()

    def stat(self, pid: int) -> bytes | None:
        if pid in self.hidden:
            return None
        return super().stat(pid)

    def list_pids(self) -> list[int]:
        result = super().list_pids()
        for pid in sorted(self.hidden):
            if pid not in result:
                result.append(pid)
        return result


class _CapabilityLessTable:
    """The historical table shape WITHOUT the pid_present
    capability: a None stat cannot be tri-stated at all, so
    presence is an unknown, never a verified absence."""

    def __init__(self, procs: dict[int, dict[str, Any]], hidden: set[int]) -> None:
        self._procs = procs
        self._hidden = hidden

    def stat(self, pid: int) -> bytes | None:
        if pid in self._hidden:
            return None
        p = self._procs.get(pid)
        return p["stat"].encode("ascii") if p else None

    def cmdline(self, pid: int) -> bytes | None:
        p = self._procs.get(pid)
        return p["cmdline"] if p else None

    def status(self, pid: int) -> bytes | None:
        p = self._procs.get(pid)
        return p["status"] if p else None

    def list_pids(self) -> list[int]:
        result = sorted(self._procs)
        for pid in sorted(self._hidden):
            if pid not in result:
                result.append(pid)
        return result


def _group_readability_world() -> tuple[dict[int, dict[str, Any]], _TriStateTable]:
    """The right-pane job (Bash 40 / worker 50) with ONE extra
    G member (51) and no subject — the public group/stop flow."""
    table, procs = _lifecycle_table()
    procs.pop(60)
    t = _TriStateTable(procs)
    return procs, t


def _group_member(state: str) -> dict[str, Any]:
    return subject_proc(
        51, state=state, ppid=50, pgrp=50, session=99, tty=TTYS, tpgid=40, uid=1000, gid=1000
    )


def test_public_stop_tri_state_matrix() -> None:
    # complete observed stopped group: the stop is recorded
    procs, t = _group_readability_world()
    procs[51] = _group_member("S")
    flow = _workflow(t, with_subject=False)
    flow.prepare()
    procs[50] = _worker_proc("T", tpgid=40)
    procs[51] = _group_member("T")
    assert flow.record_stop() is not None

    # a running G member: the stable stop is not established
    procs2, t2 = _group_readability_world()
    procs2[51] = _group_member("S")
    flow2 = _workflow(t2, with_subject=False)
    flow2.prepare()
    procs2[50] = _worker_proc("T", tpgid=40)
    procs2[51] = _group_member("S")
    with pytest.raises(fci.FixtureError, match="prep-stop-unobserved"):
        flow2.record_stop()

    # stale-listed but independently VERIFIED-gone member:
    # tolerated under the bounded churn law
    procs3, t3 = _group_readability_world()
    procs3[51] = _group_member("S")
    flow3 = _workflow(t3, with_subject=False)
    flow3.prepare()
    procs3[50] = _worker_proc("T", tpgid=40)
    del procs3[51]
    t3.hidden.add(51)
    assert t3.pid_present(51) is True  # verified gone despite stale listing
    assert flow3.record_stop() is not None

    # unreadable stat with a POSITIVELY still-existing entry:
    # the complete stop can never be minted
    procs4, t4 = _group_readability_world()
    procs4[51] = _group_member("S")
    flow4 = _workflow(t4, with_subject=False)
    flow4.prepare()
    procs4[50] = _worker_proc("T", tpgid=40)
    t4.hidden.add(51)
    assert t4.pid_present(51) is False  # entry still exists, not raced away
    with pytest.raises(fci.FixtureError, match="prep-stop-unobserved"):
        flow4.record_stop()
    # the failed event recorded NOTHING: a second call re-measures
    assert flow4._stop_receipt is None


def test_worker_group_tri_state_inventory() -> None:
    # fully observed group: complete bounded membership
    procs, t = _group_readability_world()
    procs[51] = _group_member("S")
    facts = fp.collect_worker_group(t, 50, 40, 40)
    assert sorted(m.pid for m in facts.members) == [50, 51]

    # unreadable still-existing entry: the inventory is a closed
    # refusal, never a silently truncated listing
    t.hidden.add(51)
    with pytest.raises(fci.FixtureError, match="prep-group-incomplete"):
        fp.collect_worker_group(t, 50, 40, 40)

    # stale-listed but verified-gone entry: tolerated, not a member
    del procs[51]
    t2 = _TriStateTable(procs)
    t2.hidden.add(51)
    facts2 = fp.collect_worker_group(t2, 50, 40, 40)
    assert [m.pid for m in facts2.members] == [50]


def test_unreadable_initial_prepare_refused_then_recovered() -> None:
    procs, t = _group_readability_world()
    procs[51] = _group_member("S")
    t.hidden.add(51)
    flow = _workflow(t, with_subject=False)
    with pytest.raises(fci.FixtureError, match="prep-group-incomplete"):
        flow.prepare()
    # the failed prepare minted no baseline or admission
    with pytest.raises(fci.FixtureError, match="prep-not-prepared"):
        flow.observe()
    with pytest.raises(fci.FixtureError, match="prep-not-prepared"):
        flow.record_stop()
    # the same workflow is fully usable once the inventory is
    # completely observed
    t.hidden.clear()
    first = flow.prepare()
    assert first is not None
    procs[50] = _worker_proc("T", tpgid=40)
    procs[51] = _group_member("T")
    assert flow.record_stop() is not None


def test_repeated_prepare_and_observe_failure_preserve_baseline() -> None:
    procs, t = _group_readability_world()
    procs[51] = _group_member("S")
    flow = _workflow(t, with_subject=False)
    first = flow.prepare()
    # break the inventory AFTER a valid prepare
    t.hidden.add(51)
    with pytest.raises(fci.FixtureError, match="prep-group-incomplete"):
        flow.prepare()
    with pytest.raises(fci.FixtureError, match="prep-group-incomplete"):
        flow.observe()
    # the frozen baseline and last valid observation survive:
    # once the group is completely observed again, the SAME
    # worker job is still the bound baseline
    t.hidden.clear()
    again = flow.observe()
    assert json.dumps(again, sort_keys=True) == json.dumps(first, sort_keys=True)
    assert flow._baseline is not None
    assert flow._baseline.worker_pid == 50
    assert flow._baseline.worker_start_time == 500


def test_capability_less_table_never_mints_completeness() -> None:
    # a healthy listing with the capability absent still works:
    # the tri-state seam is only consulted for None stats
    procs, _ = _group_readability_world()
    procs[51] = _group_member("S")
    healthy = _CapabilityLessTable(procs, set())
    flow = fp.NativeHandoffWorkflow(
        _binding(),
        healthy,
        worker_pid=50,
        bash_pid=40,
        subject_pid=None,
        expectation=None,
        owner_run_id=RUN,
        tty_foreground_pgrp=50,
    )
    flow.prepare()
    procs[50] = _worker_proc("T", tpgid=40)
    procs[51] = _group_member("T")
    assert flow.record_stop() is not None

    # an unreadable listed entry with NO presence capability:
    # unknown, never a verified absence — both the inventory
    # and the complete stop refuse
    unreadable = _CapabilityLessTable(procs, {51})
    with pytest.raises(fci.FixtureError, match="prep-group-incomplete"):
        fp.collect_worker_group(unreadable, 50, 40, 40)
    procs2, _2 = _group_readability_world()
    procs2[51] = _group_member("T")
    procs2[50] = _worker_proc("T", tpgid=40)
    stop_table = _CapabilityLessTable(procs2, {51})
    with pytest.raises(fci.FixtureError, match="prep-stop-unobserved"):
        fp.collect_stop_observation(stop_table, 50, 40)


def test_failed_stop_cannot_claim_restoration() -> None:
    procs, t = _group_readability_world()
    procs[51] = _group_member("S")
    flow = _workflow(t, with_subject=False)
    flow.prepare()
    # the stop is refused: an unreadable still-existing member
    procs[50] = _worker_proc("T", tpgid=40)
    t.hidden.add(51)
    with pytest.raises(fci.FixtureError, match="prep-stop-unobserved"):
        flow.record_stop()
    # a later RUNNING snapshot (foreground back on G) cannot claim
    # restoration from the failed event
    t.hidden.clear()
    procs[50] = _worker_proc("S", tpgid=50)
    procs[51] = _group_member("S")
    verdict = flow.finalize(None)
    assert verdict.ready is False
    assert "worker-stop-unmeasured" in verdict.reasons
    # a later GENUINELY observed stable stop is a distinct event
    procs[50] = _worker_proc("T", tpgid=40)
    procs[51] = _group_member("T")
    receipt = flow.record_stop()
    assert receipt is not None
    # and the restored phase measured against THAT receipt holds
    procs[50] = _worker_proc("S", tpgid=50)
    procs[51] = _group_member("S")
    facts = fp.collect_restoration(t, 50, 40, 50, stop_receipt=receipt)
    assert facts.stop_recorded is True
    assert facts.restored is True


def test_membership_cap_unaffected_by_verified_churn() -> None:
    def member(pid: int) -> dict[str, Any]:
        return subject_proc(
            pid, state="S", ppid=50, pgrp=50, session=99, tty=TTYS, tpgid=50, uid=1000, gid=1000
        )

    # at-limit (worker + 255 members = _MEMBERSHIP_MAX) plus
    # verified-gone churn entries: complete, churn not counted
    procs: dict[int, dict[str, Any]] = {
        40: bash_proc(40, state="S", pgrp=40),
        50: _worker_proc("S", tpgid=50),
    }
    for i in range(fp._MEMBERSHIP_MAX - 1):
        procs[1000 + i] = member(1000 + i)
    t = _TriStateTable(procs)
    t.hidden.update({9000, 9001})  # stale-listed, verified gone
    facts = fp.collect_worker_group(t, 50, 40, 40)
    assert len(facts.members) == fp._MEMBERSHIP_MAX

    # one-over the bound (with the same churn): closed refusal
    procs[1500] = member(1500)
    with pytest.raises(fci.FixtureError, match="prep-proc-overbound"):
        fp.collect_worker_group(t, 50, 40, 40)
