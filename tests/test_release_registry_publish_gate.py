"""Order 013-j, J1: verified-absent-for-both write-precondition gate tests.

Executes the publisher control flow (``main``) with the registry boundary
(``tag_digest_strict``) and the Docker boundary (``_docker``) mocked, and
asserts ZERO tag/push mutations for every stop case: occupied source,
occupied RC (different and same digest), partial prior publication,
unauthorized/inaccessible, unknown registry status (order 013-k, K3 —
passed through the mocked boundary unchanged, one case per target),
malformed digest, unresolved registry error, forbidden final tag,
wrong RC identity, and wrong repository. The
successful verified-absent path is proven on the exact call sequence
(tag -> push -> recheck -> tag -> push, registry API verification,
GITHUB_OUTPUT + SLAIF_PUBLISHED_DIGEST), including the pre-write recheck
race and the candidate-tag recheck after the source push.

The pure decision function ``plan_pre_write`` is covered on its full
state matrix (tri-state plus unknown statuses). Deterministic: no docker,
no network, no registry, no host state.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "release_registry_publish.py"

ABSENT = "absent"
DIGEST = "digest"
UNAUTHORIZED = "unauthorized"
# Order 013-k, K3: a registry status outside the known tri-state. The mock
# boundary passes it through UNCHANGED (it no longer converts every
# non-absent/non-unauthorized state into DIGEST).
UNKNOWN = "unknown-registry-status"

D1 = "sha256:" + "a" * 64
D2 = "sha256:" + "b" * 64
MALFORMED = "sha256:zzz"
SHA40 = "ab" * 20
LOCAL_IMAGE = "slaif-local-coding:0.1.0-local"


def _load_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("release_registry_publish_gate", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load release_registry_publish")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod() -> types.ModuleType:
    return _load_module()


# ---------------------------------------------------------------------------
# plan_pre_write: the pure tri-state matrix.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("sha_state", "rc_state", "match"),
    [
        ((ABSENT, None), (ABSENT, None), "proceed"),
        ((DIGEST, D1), (ABSENT, None), "PARTIAL"),
        ((DIGEST, D1), (DIGEST, D1), "SAME digest"),
        ((DIGEST, D1), (DIGEST, D2), "OCCUPIED"),
        ((ABSENT, None), (DIGEST, D1), "OCCUPIED"),
        ((UNAUTHORIZED, None), (ABSENT, None), "could not be verified"),
        ((ABSENT, None), (UNAUTHORIZED, None), "could not be verified"),
        ((DIGEST, MALFORMED), (ABSENT, None), "malformed"),
        ((ABSENT, None), (DIGEST, MALFORMED), "malformed"),
        ((UNAUTHORIZED, None), (UNAUTHORIZED, None), "could not be verified"),
        # Order 013-k, K3: unknown registry statuses are never proceed.
        ((UNKNOWN, None), (ABSENT, None), "EXPLICIT verified-absent"),
        ((ABSENT, None), (UNKNOWN, None), "EXPLICIT verified-absent"),
        ((UNKNOWN, None), (UNKNOWN, None), "EXPLICIT verified-absent"),
    ],
)
def test_plan_pre_write_matrix(
    mod: types.ModuleType,
    sha_state: tuple[str, str | None],
    rc_state: tuple[str, str | None],
    match: str,
) -> None:
    sha_status, sha_digest = sha_state
    rc_status, rc_digest = rc_state
    if match == "proceed":
        assert (
            mod.plan_pre_write(
                "sha-x", (sha_status, sha_digest), "0.1.0-rc1", (rc_status, rc_digest)
            )
            == "proceed"
        )
    else:
        with pytest.raises(mod.PublishError, match=match):
            mod.plan_pre_write(
                "sha-x", (sha_status, sha_digest), "0.1.0-rc1", (rc_status, rc_digest)
            )


# ---------------------------------------------------------------------------
# main(): mocked registry + docker boundaries.
# ---------------------------------------------------------------------------


class MockBoundaries:
    def __init__(self, mod: types.ModuleType, tag_states: dict[str, list[tuple[str, str | None]]]):
        self.mod = mod
        self.tag_states = {k: list(v) for k, v in tag_states.items()}
        self.docker_calls: list[tuple[str, ...]] = []
        self.registry_checks: list[tuple[str, str]] = []

    def _next_state(self, tag: str) -> tuple[str, str | None]:
        queue = self.tag_states[tag]
        if not queue:
            raise AssertionError(f"unexpected additional registry check for {tag!r}")
        return queue.pop(0)

    def tag_digest_strict(self, repo: str, tag: str, token: str | None) -> tuple[str, str | None]:
        self.registry_checks.append((repo, tag))
        status, digest = self._next_state(tag)
        if status == ABSENT:
            return (self.mod.TAG_STATUS_ABSENT, None)
        if status == UNAUTHORIZED:
            return (self.mod.TAG_STATUS_UNAUTHORIZED, None)
        if status == DIGEST:
            return (self.mod.TAG_STATUS_DIGEST, digest)
        # Order 013-k, K3: unknown statuses pass through UNCHANGED (the
        # mocked boundary no longer converts them into DIGEST).
        return (status, digest)

    def _docker(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
        self.docker_calls.append(args)
        if args[:1] == ("push",):
            stderr = f"{args[0]}: digest:{D1} size: 1\n".encode()
            return subprocess.CompletedProcess(args, 0, b"", stderr)
        return subprocess.CompletedProcess(args, 0, b"", b"")


def run_main(
    mod: types.ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tag_states: dict[str, list[tuple[str, str | None]]],
    argv: list[str] | None = None,
    token: str = "synthetic-token",
    with_output: bool = True,
) -> tuple[int | str, str, MockBoundaries]:
    bounds = MockBoundaries(mod, tag_states)
    monkeypatch.setattr(mod, "tag_digest_strict", bounds.tag_digest_strict)
    monkeypatch.setattr(mod, "_docker", bounds._docker)
    if token is None:
        monkeypatch.delenv("SLAIF_GHCR_TOKEN", raising=False)
    else:
        monkeypatch.setenv("SLAIF_GHCR_TOKEN", token)
    if with_output:
        monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "github_output"))
    else:
        monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    base_argv = [
        "release_registry_publish.py",
        "--local-image",
        LOCAL_IMAGE,
        "--git-sha",
        SHA40,
    ]
    monkeypatch.setattr("sys.argv", base_argv + (argv or []))
    import contextlib
    import io

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = mod.main()
        except mod.PublishError as exc:
            rc = "PublishError:" + str(exc)
    return rc, buf.getvalue(), bounds


def sha_tag() -> str:
    return f"sha-{SHA40}"


def rc_tag() -> str:
    return "0.1.0-rc1"


def test_occupied_source_tag_zero_mutations(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    rc, out, bounds = run_main(
        mod,
        monkeypatch,
        tmp_path,
        {sha_tag(): [(DIGEST, D1)], rc_tag(): [(ABSENT, None)]},
    )
    assert isinstance(rc, str) and rc.startswith("PublishError")
    assert "OCCUPIED" in out or "OCCUPIED" in str(rc)
    assert bounds.docker_calls == [], "occupied source must stop BEFORE any docker mutation"


def test_occupied_rc_tag_different_digest_zero_mutations(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    rc, _out, bounds = run_main(
        mod,
        monkeypatch,
        tmp_path,
        {sha_tag(): [(ABSENT, None)], rc_tag(): [(DIGEST, D2)]},
    )
    assert isinstance(rc, str) and rc.startswith("PublishError")
    assert "OCCUPIED" in str(rc)
    assert bounds.docker_calls == []


def test_occupied_rc_same_digest_prior_publication_zero_mutations(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    rc, _out, bounds = run_main(
        mod,
        monkeypatch,
        tmp_path,
        {sha_tag(): [(DIGEST, D1)], rc_tag(): [(DIGEST, D1)]},
    )
    assert isinstance(rc, str) and rc.startswith("PublishError")
    assert "SAME digest" in str(rc)
    assert "prior completed publication" in str(rc)
    assert bounds.docker_calls == []


def test_partial_prior_publication_reported_never_completed(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    rc, _out, bounds = run_main(
        mod,
        monkeypatch,
        tmp_path,
        {sha_tag(): [(DIGEST, D1)], rc_tag(): [(ABSENT, None)]},
    )
    assert isinstance(rc, str) and rc.startswith("PublishError")
    assert "PARTIAL" in str(rc)
    assert "never re-pushes or auto-completes" in str(rc)
    assert bounds.docker_calls == []


def test_unauthorized_state_zero_mutations(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    rc, _out, bounds = run_main(
        mod,
        monkeypatch,
        tmp_path,
        {sha_tag(): [(UNAUTHORIZED, None)], rc_tag(): [(ABSENT, None)]},
    )
    assert isinstance(rc, str) and rc.startswith("PublishError")
    assert "could not be verified" in str(rc)
    assert bounds.docker_calls == []


def test_malformed_digest_zero_mutations(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    rc, _out, bounds = run_main(
        mod,
        monkeypatch,
        tmp_path,
        {sha_tag(): [(DIGEST, MALFORMED)], rc_tag(): [(ABSENT, None)]},
    )
    assert isinstance(rc, str) and rc.startswith("PublishError")
    assert "malformed" in str(rc)
    assert bounds.docker_calls == []


def test_unknown_status_source_tag_zero_mutations(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Order 013-k, K3: an UNKNOWN registry status on the source tag (passed
    # through the mocked boundary unchanged) must stop main() with ZERO
    # docker mutations.
    rc, _out, bounds = run_main(
        mod,
        monkeypatch,
        tmp_path,
        {sha_tag(): [(UNKNOWN, None)], rc_tag(): [(ABSENT, None)]},
    )
    assert isinstance(rc, str) and rc.startswith("PublishError")
    assert "EXPLICIT verified-absent" in str(rc)
    assert "never treated as absent" in str(rc)
    assert bounds.docker_calls == []


def test_unknown_status_rc_tag_zero_mutations(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Order 013-k, K3: an UNKNOWN registry status on the candidate tag must
    # stop main() with ZERO docker mutations.
    rc, _out, bounds = run_main(
        mod,
        monkeypatch,
        tmp_path,
        {sha_tag(): [(ABSENT, None)], rc_tag(): [(UNKNOWN, None)]},
    )
    assert isinstance(rc, str) and rc.startswith("PublishError")
    assert "EXPLICIT verified-absent" in str(rc)
    assert "never treated as absent" in str(rc)
    assert bounds.docker_calls == []


def test_unresolved_registry_error_zero_mutations(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def raising(repo: str, tag: str, token: str | None) -> tuple[str, str | None]:
        raise ConnectionError("registry unreachable")

    monkeypatch.setattr(mod, "tag_digest_strict", raising)
    monkeypatch.setenv("SLAIF_GHCR_TOKEN", "synthetic-token")
    monkeypatch.setattr(
        "sys.argv",
        ["release_registry_publish.py", "--local-image", LOCAL_IMAGE, "--git-sha", SHA40],
    )
    docker_calls: list[tuple[str, ...]] = []

    def _docker_record(*a: str, **k: str) -> None:
        docker_calls.append(a)

    monkeypatch.setattr(mod, "_docker", _docker_record)
    with pytest.raises(mod.PublishError, match="unresolved"):
        mod.main()
    assert docker_calls == []


@pytest.mark.parametrize("forbidden", ["0.1.0", "latest", "stable", "v0.1.0"])
def test_forbidden_final_tag_zero_touch(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, forbidden: str
) -> None:
    bounds = MockBoundaries(mod, {})
    monkeypatch.setattr(mod, "tag_digest_strict", bounds.tag_digest_strict)
    monkeypatch.setattr(mod, "_docker", bounds._docker)
    monkeypatch.setenv("SLAIF_GHCR_TOKEN", "synthetic-token")
    monkeypatch.setattr(
        "sys.argv",
        [
            "release_registry_publish.py",
            "--local-image",
            LOCAL_IMAGE,
            "--git-sha",
            SHA40,
            "--release-tag",
            forbidden,
        ],
    )
    with pytest.raises(mod.PublishError, match="final/stable tag"):
        mod.main()
    assert bounds.docker_calls == []
    assert bounds.registry_checks == [], "identity law precedes any registry access"


def test_wrong_rc_identity_zero_touch(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    bounds = MockBoundaries(mod, {})
    monkeypatch.setattr(mod, "tag_digest_strict", bounds.tag_digest_strict)
    monkeypatch.setattr(mod, "_docker", bounds._docker)
    monkeypatch.setenv("SLAIF_GHCR_TOKEN", "synthetic-token")
    monkeypatch.setattr(
        "sys.argv",
        [
            "release_registry_publish.py",
            "--local-image",
            LOCAL_IMAGE,
            "--git-sha",
            SHA40,
            "--release-tag",
            "0.1.0-rc2",
        ],
    )
    with pytest.raises(mod.PublishError, match="not the expected RC identity"):
        mod.main()
    assert bounds.docker_calls == []
    assert bounds.registry_checks == []


def test_wrong_repository_zero_touch(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    bounds = MockBoundaries(mod, {})
    monkeypatch.setattr(mod, "tag_digest_strict", bounds.tag_digest_strict)
    monkeypatch.setattr(mod, "_docker", bounds._docker)
    monkeypatch.setenv("SLAIF_GHCR_TOKEN", "synthetic-token")
    monkeypatch.setattr(
        "sys.argv",
        [
            "release_registry_publish.py",
            "--local-image",
            LOCAL_IMAGE,
            "--git-sha",
            SHA40,
            "--repo",
            "someone-else/other-repo",
        ],
    )
    with pytest.raises(mod.PublishError, match="not the expected"):
        mod.main()
    assert bounds.docker_calls == []
    assert bounds.registry_checks == []


def test_verified_absent_success_exact_sequence(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Checks: pre-write (both), immediate recheck (both), post-push source
    # API check, candidate pre-write recheck, final verification (both).
    rc, out, bounds = run_main(
        mod,
        monkeypatch,
        tmp_path,
        {
            # sha: pre-write, immediate recheck, post-push API check, final
            # verification.
            sha_tag(): [(ABSENT, None), (ABSENT, None), (DIGEST, D1), (DIGEST, D1)],
            # rc: pre-write, immediate recheck, candidate pre-write recheck,
            # final verification.
            rc_tag(): [(ABSENT, None), (ABSENT, None), (ABSENT, None), (DIGEST, D1)],
        },
    )
    assert rc == 0, out
    # Exact mutation sequence: tag+push the source alias, then tag+push the
    # candidate tag. Nothing else.
    assert bounds.docker_calls == [
        ("tag", LOCAL_IMAGE, f"ghcr.io/ulfe-lmi/slaif-local-coding:{sha_tag()}"),
        ("push", f"ghcr.io/ulfe-lmi/slaif-local-coding:{sha_tag()}"),
        ("tag", LOCAL_IMAGE, f"ghcr.io/ulfe-lmi/slaif-local-coding:{rc_tag()}"),
        ("push", f"ghcr.io/ulfe-lmi/slaif-local-coding:{rc_tag()}"),
    ]
    assert "SLAIF_PUBLISHED_DIGEST=" + D1 in out
    emitted = json.loads(out.strip().splitlines()[-2])
    assert emitted == {"digest": D1, "tag": rc_tag()}
    output_lines = (tmp_path / "github_output").read_text(encoding="utf-8").splitlines()
    assert f"published_digest={D1}" in output_lines
    assert f"published_tag={rc_tag()}" in output_lines


def test_pre_write_recheck_race_zero_push(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # First check: both absent. The immediate pre-write recheck (a race
    # window) reports the source tag occupied: the run must stop with ZERO
    # pushes (zero docker mutations at all).
    rc, _out, bounds = run_main(
        mod,
        monkeypatch,
        tmp_path,
        {
            sha_tag(): [(ABSENT, None), (DIGEST, D2)],
            rc_tag(): [(ABSENT, None), (ABSENT, None)],
        },
    )
    assert isinstance(rc, str) and rc.startswith("PublishError")
    assert "OCCUPIED" in str(rc)
    assert bounds.docker_calls == [], "a race-induced occupation must stop before ANY write"


def test_candidate_recheck_after_source_push_stops_partial(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Source alias is written; the recheck immediately before the candidate
    # write finds it occupied (a concurrent publication): exactly ONE tag
    # and ONE push were performed, and the run reports the partial state
    # without any further mutation.
    rc, _out, bounds = run_main(
        mod,
        monkeypatch,
        tmp_path,
        {
            sha_tag(): [(ABSENT, None), (ABSENT, None), (DIGEST, D1)],
            rc_tag(): [(ABSENT, None), (ABSENT, None), (DIGEST, D2)],
        },
    )
    assert isinstance(rc, str) and rc.startswith("PublishError")
    assert "PARTIAL" in str(rc)
    assert bounds.docker_calls == [
        ("tag", LOCAL_IMAGE, f"ghcr.io/ulfe-lmi/slaif-local-coding:{sha_tag()}"),
        ("push", f"ghcr.io/ulfe-lmi/slaif-local-coding:{sha_tag()}"),
    ]
