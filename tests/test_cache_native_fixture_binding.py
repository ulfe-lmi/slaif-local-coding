"""Order-binding tests for the 017-t order/run binding module.

Pure/fake-layer law: a fake git runner and a tmp repository stand
in for the real checkout; no test touches the real git remote,
the real .oap-local namespace or the network.  The real git
binary is never launched (the default runner is only covered
structurally); the admitted S record is exercised on the
historical 017-s schema without rewriting it.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BINDING_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_binding.py"
CI_PATH = REPO_ROOT / "scripts" / "cache_native_fixture_ci.py"

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

HEAD = "f" * 40
ORDER_BYTES = b"# OAP Work Order 017-t: test order\n"
ORDER_NAME = "017-t-evidence-finalization-and-native-preparation.md"
ORIGIN = "https://github.com/ulfe-lmi/slaif-local-coding.git"


def _make_repo(tmp_path: Path, *, active: bytes | None = b"017-t\n") -> Path:
    repo = tmp_path / "repo"
    (repo / "oap" / "orders").mkdir(parents=True, exist_ok=True)
    (repo / "oap" / "orders" / ORDER_NAME).write_bytes(ORDER_BYTES)
    if active is not None:
        (repo / "oap" / "active").write_bytes(active)
    (repo / ".git" / "info").mkdir(parents=True, exist_ok=True)
    (repo / ".git" / "info" / "exclude").write_bytes(b"")
    return repo


def _git_runner(
    *,
    head: str = HEAD,
    dirty: bytes = b"",
    order_names: tuple[str, ...] = (ORDER_NAME,),
    order_bytes: bytes = ORDER_BYTES,
    origin: str = ORIGIN,
    committed_active: bytes | None = b"017-t\n",
    ls_tree_fail: bool = False,
) -> Any:
    calls: list[tuple[str, ...]] = []

    def git_runner(args: list[str], repo: Path) -> bytes:
        calls.append(tuple(args))
        if args == ["rev-parse", "HEAD"]:
            return head.encode()
        if args == ["status", "--porcelain"]:
            return dirty
        if args == ["remote", "get-url", "origin"]:
            return (origin + "\n").encode()
        if args[:2] == ["ls-tree", "--name-only"]:
            if ls_tree_fail:
                raise AssertionError("runner must model git failure via returncode, not raise")
            return ("\n".join(order_names) + ("\n" if order_names else "")).encode()
        if args[0] == "show":
            ref = args[1]
            if ref.endswith(":oap/active"):
                if committed_active is None:
                    # model git failure (nonzero rc) for a missing
                    # committed file: the module maps it to None
                    raise fci.FixtureError("bind-git-failed")
                return committed_active
            name = ref.split(":", 1)[1].removeprefix("oap/orders/")
            if name not in order_names:
                raise AssertionError(f"unexpected order ref: {name}")
            return order_bytes
        raise AssertionError(f"unexpected git args: {args}")

    git_runner.calls = calls  # type: ignore[attr-defined]
    return git_runner


def _binding(
    tmp_path: Path,
    git: Any | None = None,
    *,
    order_id: str = "017-t",
    head: str = HEAD,
) -> Any:
    repo = tmp_path / "repo"
    if not repo.exists():
        _make_repo(tmp_path)
    if git is None:
        git = _git_runner(head=head)
    return fb.resolve_order_binding(repo, order_id, head, git_runner=git)


# -- valid resolution ------------------------------------------------------------


def test_valid_binding_resolves_read_only(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    git = _git_runner()
    before = sorted(p.relative_to(repo).as_posix() for p in repo.rglob("*") if p.is_file())
    b = fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=git)
    after = sorted(p.relative_to(repo).as_posix() for p in repo.rglob("*") if p.is_file())
    assert before == after  # strictly read-only: nothing created or changed
    assert b.order_id == "017-t"
    assert b.order_path == f"oap/orders/{ORDER_NAME}"
    assert b.order_sha256 == __import__("hashlib").sha256(ORDER_BYTES).hexdigest()
    assert b.active_bytes == b"017-t\n"
    assert b.source_head == HEAD
    assert b.repo_identity == "ulfe-lmi/slaif-local-coding"
    assert len(b.run_id) == 32 and int(b.run_id, 16) >= 0
    # the closed record is stable and hash-only over the active bytes
    rec = b.to_record()
    assert set(rec) == {
        "record",
        "order_id",
        "order_path",
        "order_sha256",
        "active_sha256",
        "source_head",
        "repo_identity",
        "run_id",
    }
    assert rec["active_sha256"] == __import__("hashlib").sha256(b"017-t\n").hexdigest()
    # two resolutions mint distinct run identities
    b2 = fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=git)
    assert b2.run_id != b.run_id


def test_binding_uses_only_closed_git_grammar(tmp_path: Path) -> None:
    git = _git_runner()
    fb.resolve_order_binding(_make_repo(tmp_path), "017-t", HEAD, git_runner=git)
    allowed = {
        ("rev-parse", "HEAD"),
        ("status", "--porcelain"),
        ("remote", "get-url", "origin"),
        ("ls-tree", "--name-only", f"{HEAD}:oap/orders"),
        ("show", f"{HEAD}:oap/orders/{ORDER_NAME}"),
        ("show", f"{HEAD}:oap/active"),
    }
    assert set(git.calls) == allowed


def test_origin_never_echoed_in_binding(tmp_path: Path) -> None:
    b = _binding(tmp_path)
    assert "github.com" not in b.repo_identity
    assert "https" not in b.repo_identity
    assert "://" not in b.repo_identity


@pytest.mark.parametrize(
    "origin,expected",
    [
        ("https://github.com/ulfe-lmi/slaif-local-coding", "ulfe-lmi/slaif-local-coding"),
        ("https://github.com/ULFE-LMI/Slaif-Local-Coding.git", "ulfe-lmi/slaif-local-coding"),
    ],
)
def test_origin_grammar_accepted_normalized(origin: str, expected: str) -> None:
    assert fb.parse_repo_identity(origin) == expected


@pytest.mark.parametrize(
    "origin",
    [
        "ssh://git@github.com/ulfe-lmi/slaif-local-coding.git",
        # TEST-NET documentation endpoint refused, not echoed
        "https://192.0.2.77:18020/v1/repo.git",
        "https://github.com/ulfe-lmi/slaif-local-coding/tree/main",
        "https://github.com/ulfe-lmi",
        "git@github.com:ulfe-lmi/slaif-local-coding.git",
        "https://github.com/ulfe-lmi/slaif-local-coding?token=abc",
        "",
    ],
)
def test_origin_grammar_refused_closed(origin: str) -> None:
    with pytest.raises(fci.FixtureError, match="bind-origin-untrusted"):
        fb.parse_repo_identity(origin)


# -- resolution refusals -----------------------------------------------------------


def test_malformed_order_ids_refused_before_git(tmp_path: Path) -> None:
    for bad in ("017-", "17-t", "017-T", "017-tt1", "017-1", "017-t ", "", 17, None, b"017-t"):
        git = _git_runner()
        with pytest.raises(fci.FixtureError, match="bind-order-id-invalid"):
            fb.resolve_order_binding(_make_repo(tmp_path), bad, HEAD, git_runner=git)
        assert git.calls == []


def test_head_mismatch_refused(tmp_path: Path) -> None:
    with pytest.raises(fci.FixtureError, match="bind-head-mismatch"):
        _binding(tmp_path, git=_git_runner(head="e" * 40))


@pytest.mark.parametrize("head", ["f" * 39, "g" * 40, "f" * 41, "F" * 40, ""])
def test_head_invalid_refused(tmp_path: Path, head: str) -> None:
    with pytest.raises(fci.FixtureError, match="bind-head-invalid"):
        _binding(tmp_path, head=head)


def test_dirty_worktree_refused(tmp_path: Path) -> None:
    with pytest.raises(fci.FixtureError, match="bind-worktree-dirty"):
        _binding(tmp_path, git=_git_runner(dirty=b" M oap/active\n"))


def test_active_missing_refused(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, active=None)
    with pytest.raises(fci.FixtureError, match="bind-active-missing"):
        fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=_git_runner())


def test_active_mismatch_refused(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, active=b"017-s\n")
    with pytest.raises(fci.FixtureError, match="bind-active-mismatch"):
        fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=_git_runner())


def test_order_ambiguous_on_zero_or_duplicate(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    with pytest.raises(fci.FixtureError, match="bind-order-ambiguous"):
        fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=_git_runner(order_names=()))
    with pytest.raises(fci.FixtureError, match="bind-order-ambiguous"):
        fb.resolve_order_binding(
            repo,
            "017-t",
            HEAD,
            git_runner=_git_runner(order_names=(ORDER_NAME, "017-t-duplicate.md")),
        )
    # a non-order name does not count; a subdirectory never counts
    with pytest.raises(fci.FixtureError, match="bind-order-ambiguous"):
        fb.resolve_order_binding(
            repo,
            "017-t",
            HEAD,
            git_runner=_git_runner(order_names=("README.md", "017-t-notes.md/")),
        )

    # a git TRANSPORT failure (hung query) stays a distinct token;
    # an empty listing is the zero-match outcome
    def _base_bytes(args: list[str], r: Path) -> bytes:
        out = _git_runner()(args, r)
        assert isinstance(out, bytes)
        return out

    def hang_ls(args: list[str], r: Path) -> bytes:
        if args[0] == "ls-tree":
            raise fci.FixtureError("bind-git-timeout")
        return _base_bytes(args, r)

    def empty_ok(args: list[str], r: Path) -> bytes:
        if args[0] == "ls-tree":
            return b""
        return _base_bytes(args, r)

    with pytest.raises(fci.FixtureError, match="bind-git-timeout"):
        fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=hang_ls)
    with pytest.raises(fci.FixtureError, match="bind-order-ambiguous"):
        fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=empty_ok)


def test_order_bytes_and_missing_refused(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    (repo / "oap" / "orders" / ORDER_NAME).write_bytes(ORDER_BYTES + b"tampered\n")
    with pytest.raises(fci.FixtureError, match="bind-order-bytes"):
        fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=_git_runner())
    repo2 = _make_repo(tmp_path / "r2")
    (repo2 / "oap" / "orders" / ORDER_NAME).unlink()
    with pytest.raises(fci.FixtureError, match="bind-order-missing"):
        fb.resolve_order_binding(repo2, "017-t", HEAD, git_runner=_git_runner())


# -- per-order stable one-attempt namespaces ----------------------------------------


def test_admit_records_then_exhausts(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    b = _binding(tmp_path)
    fb.admit_order_attempt(repo, "017-t", b, git_runner=_git_runner())
    record = fb.read_admission_record(repo, "017-t")
    assert record == {
        "record": "slaif-oap-order-admission-v1",
        "order": "017-t",
        "attempts": [{"head": HEAD, "run_id": b.run_id, "status": "running"}],
    }
    assert fb.admission_exhausted(repo, "017-t") is True
    # a fresh binding (new run id, same order) cannot admit a second attempt
    b2 = _binding(tmp_path)
    assert b2.run_id != b.run_id
    with pytest.raises(fci.FixtureError, match="bind-attempt-exhausted"):
        fb.admit_order_attempt(repo, "017-t", b2, git_runner=_git_runner())
    # terminal record preserves the honest outcome and stays exhausted
    fb.record_order_attempt(repo, "017-t", b.run_id, "pass")
    record = fb.read_admission_record(repo, "017-t")
    assert record["attempts"][0]["status"] == "pass"
    assert fb.admission_exhausted(repo, "017-t") is True
    # the exclude line landed locally (no tracked file)
    exclude = (repo / ".git" / "info" / "exclude").read_bytes()
    assert b".oap-local/" in exclude


def test_namespace_stable_across_head_and_phase(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    b1 = _binding(tmp_path, head=HEAD)
    fb.admit_order_attempt(repo, "017-t", b1, git_runner=_git_runner())
    # a CHANGED head inside the same activated order never resets the
    # namespace: the record is keyed by the order, not the head.
    head2 = "e" * 40
    b2 = _binding(tmp_path, head=head2)
    with pytest.raises(fci.FixtureError, match="bind-attempt-exhausted"):
        fb.admit_order_attempt(repo, "017-t", b2, git_runner=_git_runner(head=head2))
    # a changed directory (fresh checkout copy of the repo root, same
    # .oap-local namespace) never resets it either.
    repo_moved = tmp_path / "repo-moved"
    (repo_moved / "oap" / "orders").mkdir(parents=True)
    (repo_moved / "oap" / "orders" / ORDER_NAME).write_bytes(ORDER_BYTES)
    (repo_moved / "oap" / "active").write_bytes(b"017-t\n")
    (repo_moved / ".git" / "info").mkdir(parents=True)
    (repo_moved / ".oap-local").symlink_to(repo / ".oap-local")
    assert fb.admission_exhausted(repo_moved, "017-t") is True
    # a different order id gets its own fresh namespace
    assert fb.read_admission_record(repo, "017-u")["attempts"] == []
    assert fb.admission_exhausted(repo, "017-u") is False


def test_s_record_preserved_schema_and_exhaustion(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, active=b"017-s\n")
    (repo / "oap" / "orders" / "017-s-local-fixture-preparation-and-supervision.md").write_bytes(
        b"# S order\n"
    )
    adir = repo / ".oap-local" / "017-s"
    adir.mkdir(parents=True, mode=0o700)
    s_record = {
        "record": "slaif-017s-admission-v1",
        "order": "017-s",
        "attempts": [{"head": "a" * 40, "run_id": "c" * 32, "status": "pass"}],
    }
    (adir / "admission.json").write_text(json.dumps(s_record, sort_keys=True) + "\n")
    os.chmod(adir / "admission.json", 0o600)
    os.chmod(adir, 0o700)
    os.chmod(adir.parent, 0o700)
    # the historical S record reads back EXACTLY (schema and bytes)
    assert fb.read_admission_record(repo, "017-s") == s_record
    assert fb.admission_exhausted(repo, "017-s") is True
    # and a new 017-s binding cannot admit into it
    git_s = _git_runner(
        order_names=("017-s-local-fixture-preparation-and-supervision.md",),
        order_bytes=b"# S order\n",
        committed_active=b"017-s\n",
    )
    b_s = fb.resolve_order_binding(repo, "017-s", HEAD, git_runner=git_s)
    with pytest.raises(fci.FixtureError, match="bind-attempt-exhausted"):
        fb.admit_order_attempt(repo, "017-s", b_s, git_runner=git_s)
    # the shared schema is NOT accepted for the 017-s order (schema drift)
    bad = dict(s_record, record="slaif-oap-order-admission-v1")
    (adir / "admission.json").write_text(json.dumps(bad, sort_keys=True) + "\n")
    with pytest.raises(fci.FixtureError, match="bind-admission-malformed"):
        fb.read_admission_record(repo, "017-s")
    # and the 017-t namespace in the same repo is untouched
    assert fb.read_admission_record(repo, "017-t")["attempts"] == []


def test_untrusted_or_malformed_record_refused(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    b = _binding(tmp_path)
    fb.admit_order_attempt(repo, "017-t", b, git_runner=_git_runner())
    path = repo / ".oap-local" / "017-t" / "admission.json"
    os.chmod(path, 0o644)
    with pytest.raises(fci.FixtureError, match="bind-admission-untrusted"):
        fb.read_admission_record(repo, "017-t")
    os.chmod(path, 0o600)
    path.write_bytes(b"not json\n")
    with pytest.raises(fci.FixtureError, match="bind-admission-malformed"):
        fb.read_admission_record(repo, "017-t")
    # an overbound record is rejected, never truncated into a valid one
    big = {"record": "slaif-oap-order-admission-v1", "order": "017-t", "attempts": []}
    path.write_bytes((json.dumps(big) + "x" * 9000).encode())
    with pytest.raises(fci.FixtureError, match="bind-admission-malformed"):
        fb.read_admission_record(repo, "017-t")


def test_claim_blocks_second_admit_and_stale_claim_reclaimed(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    b1 = _binding(tmp_path)
    fb.admit_order_attempt(repo, "017-t", b1, git_runner=_git_runner())
    # the live claim of the admitted run blocks a concurrent admit
    claim = repo / ".oap-local" / "017-t" / "admission.claim"
    assert claim.read_bytes() == b1.run_id.encode()
    b2 = _binding(tmp_path)
    with pytest.raises(fci.FixtureError, match="bind-attempt-exhausted"):
        fb.admit_order_attempt(repo, "017-t", b2, git_runner=_git_runner())
    # a terminal record with its own (unreleased) claim is stale and
    # is reclaimed exactly once by a fresh admit
    fb.record_order_attempt(repo, "017-t", b1.run_id, "pass")
    b3 = _binding(tmp_path)
    with pytest.raises(fci.FixtureError, match="bind-attempt-exhausted"):
        fb.admit_order_attempt(repo, "017-t", b3, git_runner=_git_runner())


def test_foreign_claim_and_bad_record_refused(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    adir = repo / ".oap-local" / "017-t"
    adir.mkdir(parents=True, mode=0o700)
    os.chmod(adir.parent, 0o700)
    os.chmod(adir, 0o700)
    (adir / "admission.claim").write_bytes(b"z" * 32)  # claim for a non-admitted run
    b = _binding(tmp_path)
    with pytest.raises(fci.FixtureError, match="bind-attempt-exhausted"):
        fb.admit_order_attempt(repo, "017-t", b, git_runner=_git_runner())
    (adir / "admission.claim").unlink()
    (adir / "admission.json").write_bytes(b'{"record":"x","order":"017-t","attempts":[]}\n')
    os.chmod(adir / "admission.json", 0o600)
    with pytest.raises(fci.FixtureError, match="bind-admission-malformed"):
        fb.read_admission_record(repo, "017-t")
    # a malformed record is refused, never read as not-exhausted
    with pytest.raises(fci.FixtureError, match="bind-admission-malformed"):
        fb.admission_exhausted(repo, "017-t")


def test_admission_env_refused_not_adopted(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    adir = repo / ".oap-local" / "017-t"
    adir.mkdir(parents=True)
    os.chmod(adir, 0o755)  # group-writable: never adopted, never chmod'd
    b = _binding(tmp_path)
    with pytest.raises(fci.FixtureError, match="bind-admission-env"):
        fb.admit_order_attempt(repo, "017-t", b, git_runner=_git_runner())
    assert os.lstat(adir).st_mode & 0o777 == 0o755  # untouched
    repo2 = _make_repo(tmp_path / "r2")
    link = repo2 / ".oap-local" / "017-t"
    link.parent.mkdir(parents=True)
    link.symlink_to(tmp_path / "elsewhere")
    with pytest.raises(fci.FixtureError, match="bind-admission-env"):
        fb.admit_order_attempt(repo2, "017-t", b, git_runner=_git_runner())


def test_record_attempt_rejects_bad_run_and_status(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    b = _binding(tmp_path)
    fb.admit_order_attempt(repo, "017-t", b, git_runner=_git_runner())
    for bad_run in ("c" * 31, "g" * 32, True):
        with pytest.raises(fci.FixtureError, match="bind-admission-malformed"):
            fb.record_order_attempt(repo, "017-t", bad_run, "pass")
    with pytest.raises(fci.FixtureError, match="bind-admission-malformed"):
        fb.record_order_attempt(repo, "017-t", b.run_id, "running")


# -- context revalidation at the admission boundary (review 1) ---------------------


def test_committed_active_mismatch_refused_at_resolve(tmp_path: Path) -> None:
    # models a legitimate assume-unchanged index: clean status, disk
    # active T, committed active S.  Clean status is NOT content
    # binding: the committed bytes must be compared explicitly.
    repo = _make_repo(tmp_path)
    with pytest.raises(fci.FixtureError, match="bind-active-committed-mismatch"):
        fb.resolve_order_binding(
            repo, "017-t", HEAD, git_runner=_git_runner(committed_active=b"017-s\n")
        )
    assert not (repo / ".oap-local").exists()


def test_committed_active_missing_at_head_refused(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    with pytest.raises(fci.FixtureError, match="bind-active-committed-mismatch"):
        fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=_git_runner(committed_active=None))
    assert not (repo / ".oap-local").exists()


def test_foreign_repo_binding_refused_before_mutation(tmp_path: Path) -> None:
    repo_a = _make_repo(tmp_path)
    b = fb.resolve_order_binding(repo_a, "017-t", HEAD, git_runner=_git_runner())
    repo_b = _make_repo(tmp_path / "rB", active=b"017-u\n")
    runner_b = _git_runner(
        head="b" * 40,
        origin="https://github.com/other/synthetic.git",
        committed_active=b"017-u\n",
    )
    with pytest.raises(fci.FixtureError, match="bind-head-drift"):
        fb.admit_order_attempt(repo_b, "017-t", b, git_runner=runner_b)
    assert not (repo_b / ".oap-local").exists()


def test_head_drift_since_resolution_refused_before_mutation(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    b = fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=_git_runner())
    with pytest.raises(fci.FixtureError, match="bind-head-drift"):
        fb.admit_order_attempt(repo, "017-t", b, git_runner=_git_runner(head="b" * 40))
    assert not (repo / ".oap-local").exists()


@pytest.mark.parametrize(
    "mutate",
    ["disk-active", "committed-active", "origin"],
    ids=["disk-active", "committed-active", "origin"],
)
def test_repo_context_drift_since_resolution_refused(tmp_path: Path, mutate: str) -> None:
    repo = _make_repo(tmp_path)
    b = fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=_git_runner())
    if mutate == "disk-active":
        (repo / "oap" / "active").write_bytes(b"017-u\n")
        runner, token = _git_runner(), "bind-active-drift"
    elif mutate == "committed-active":
        runner, token = _git_runner(committed_active=b"017-u\n"), "bind-active-committed-mismatch"
    else:
        runner, token = (
            _git_runner(origin="https://github.com/other/synthetic.git"),
            "bind-repo-identity-mismatch",
        )
    with pytest.raises(fci.FixtureError, match=token):
        fb.admit_order_attempt(repo, "017-t", b, git_runner=runner)
    assert not (repo / ".oap-local").exists()


# -- terminal-record immutability (review 1) ----------------------------------------


def test_terminal_record_immutable_single_finalization(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    b = _binding(tmp_path)
    fb.admit_order_attempt(repo, "017-t", b, git_runner=_git_runner())
    path = repo / ".oap-local" / "017-t" / "admission.json"
    claim = repo / ".oap-local" / "017-t" / "admission.claim"
    assert fb.record_order_attempt(repo, "017-t", b.run_id, "fail") == "finalized"
    assert claim.exists() is False
    before = path.read_bytes()
    # a later finalization of the SAME run cannot rewrite the
    # terminal outcome (no hidden failure), and raises nothing
    assert fb.record_order_attempt(repo, "017-t", b.run_id, "pass") == "terminal-preserved"
    assert path.read_bytes() == before
    assert json.loads(before)["attempts"][0]["status"] == "fail"
    # a mismatched finalization (unknown run) is a closed no-op
    assert fb.record_order_attempt(repo, "017-t", "e" * 32, "pass") == "not-running"
    assert path.read_bytes() == before


def test_historical_s_terminal_record_never_rewritten(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, active=b"017-s\n")
    adir = repo / ".oap-local" / "017-s"
    adir.mkdir(parents=True, mode=0o700)
    s_record = {
        "record": "slaif-017s-admission-v1",
        "order": "017-s",
        "attempts": [{"head": "a" * 40, "run_id": "c" * 32, "status": "pass"}],
    }
    path = adir / "admission.json"
    path.write_text(json.dumps(s_record, sort_keys=True) + "\n")
    os.chmod(path, 0o600)
    os.chmod(adir, 0o700)
    os.chmod(adir.parent, 0o700)
    before = path.read_bytes()
    # the historical consumed S ledger is byte-for-byte immutable:
    # no exception, no rewrite, no claim side effects
    assert fb.record_order_attempt(repo, "017-s", "c" * 32, "fail") == "terminal-preserved"
    assert path.read_bytes() == before
    assert not (adir / "admission.claim").exists()


# -- bounded owned-regular reads (review 1 static observation) ------------------------


def test_special_and_overbound_active_objects_refused(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    active = repo / "oap" / "active"
    active.unlink()
    os.mkfifo(active)  # special file: closed refusal, no blocking read
    with pytest.raises(fci.FixtureError, match="bind-active-object"):
        fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=_git_runner())
    active.unlink()
    active.write_bytes(b"017-t\n")
    target = repo / "oap" / "active-target"
    target.write_bytes(b"017-t\n")
    active.unlink()
    active.symlink_to(target)  # link, never followed
    with pytest.raises(fci.FixtureError, match="bind-active-object"):
        fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=_git_runner())


def test_overbound_active_object_refused(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, active=b"017-t\n" + b"x" * 5000)
    with pytest.raises(fci.FixtureError, match="bind-active-object"):
        fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=_git_runner())


def test_symlinked_and_overbound_order_objects_refused(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    order = repo / "oap" / "orders" / ORDER_NAME
    order.unlink()
    (repo / "oap" / "orders" / ORDER_NAME).symlink_to("/etc/hostname")  # foreign target
    with pytest.raises(fci.FixtureError, match="bind-order-object"):
        fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=_git_runner())
    (repo / "oap" / "orders" / ORDER_NAME).unlink()
    big = repo / "oap" / "orders" / ORDER_NAME
    big.write_bytes(b"o" * ((1 << 20) + 1))
    with pytest.raises(fci.FixtureError, match="bind-order-object"):
        fb.resolve_order_binding(repo, "017-t", HEAD, git_runner=_git_runner())


def test_admission_reasons_closed_vocabulary() -> None:
    src = BINDING_PATH.read_text()
    tokens = set(re.findall(r'FixtureError\("([a-z-]+)"\)', src))
    assert tokens <= fb.BIND_REASONS
    assert all(isinstance(t, str) and t for t in fb.BIND_REASONS)
