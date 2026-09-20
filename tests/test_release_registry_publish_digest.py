"""Digest-capture and RC-tag-law unit tests for
scripts/release_registry_publish.py (order 013-e, D1; order 013-i, D13/D14).

The 013-d C6 dispatch proved the GITHUB_TOKEN push is registry-accepted, but
the script's `_push_digest()` scanned captured stdout only while the docker
CLI (non-TTY) emits push progress — including the final digest line — on
stderr. These tests pin the corrected contract of the pure
`extract_push_digest` parser and the failure-path behavior (ref named,
output tail included, SLAIF_GHCR_TOKEN value redacted). Deterministic: no
docker, no network, no host state.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "release_registry_publish.py"

DIGEST_HEX = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
DIGEST = f"sha256:{DIGEST_HEX}"
OTHER_DIGEST_HEX = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
OTHER_DIGEST = f"sha256:{OTHER_DIGEST_HEX}"
SHA40 = "ab" * 20
PUSH_REF = f"ghcr.io/ulfe-lmi/slaif-local-coding:sha-{SHA40}"


def _load_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("release_registry_publish", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load release_registry_publish")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod() -> types.ModuleType:
    return _load_module()


# Realistic non-TTY `docker push` transcript: banner, layer progress lines on
# stderr, and the final '<ref>: digest:sha256:<64-hex> size:<n>' line.
NON_TTY_TRANSCRIPT = (
    "The push refers to repository [ghcr.io/ulfe-lmi/slaif-local-coding]\n"
    "c3d4e5f6a7b8: Preparing\n"
    "a1b2c3d4e5f6: Preparing\n"
    "f6e5d4c3b2a1: Waiting\n"
    "c3d4e5f6a7b8: Layer already exists\n"
    "a1b2c3d4e5f6: Pushed\n"
    f"f6e5d4c3b2a1: Pushed\n"
    f"sha-{SHA40}: digest:{DIGEST} size: 2832\n"
)


def test_non_tty_transcript_returns_final_digest(mod: types.ModuleType) -> None:
    assert mod.extract_push_digest(NON_TTY_TRANSCRIPT) == DIGEST


def test_release_tag_final_line_form(mod: types.ModuleType) -> None:
    # The real non-TTY docker CLI prints the size suffix with a space after
    # the colon; the no-space variant is accepted for robustness.
    with_space = (
        "The push refers to repository [ghcr.io/ulfe-lmi/slaif-local-coding]\n"
        "c3d4e5f6a7b8: Layer already exists\n"
        f"0.1.0: digest:{DIGEST} size: 1418\n"
    )
    assert mod.extract_push_digest(with_space) == DIGEST
    no_space = f"0.1.0: digest:{DIGEST} size:1418\n"
    assert mod.extract_push_digest(no_space) == DIGEST
    no_size = f"0.1.0: digest:{DIGEST}\n"
    assert mod.extract_push_digest(no_size) == DIGEST


def test_legacy_bare_digest_forms(mod: types.ModuleType) -> None:
    assert mod.extract_push_digest(f"digest: {DIGEST}\n") == DIGEST
    assert mod.extract_push_digest(f"digest:{DIGEST}\n") == DIGEST


def test_multiple_candidates_last_match_wins(mod: types.ModuleType) -> None:
    transcript = (
        f"digest: {OTHER_DIGEST}\ndigest:{OTHER_DIGEST}\nsha-{SHA40}: digest:{DIGEST} size: 2832\n"
    )
    assert mod.extract_push_digest(transcript) == DIGEST


def test_no_digest_line_returns_none(mod: types.ModuleType) -> None:
    transcript = (
        "The push refers to repository [ghcr.io/ulfe-lmi/slaif-local-coding]\n"
        "c3d4e5f6a7b8: Preparing\n"
        "a1b2c3d4e5f6: Pushed\n"
        "denied: requested access to the resource is denied\n"
    )
    assert mod.extract_push_digest(transcript) is None
    assert mod.extract_push_digest("") is None


@pytest.mark.parametrize(
    "bad_line",
    [
        "digest: sha256:" + "a" * 63 + "\n",  # short
        "digest: sha256:" + "a" * 65 + "\n",  # long
        "digest: sha256:" + "g" * 64 + "\n",  # non-hex
        "digest: sha256:" + "a" * 62 + "g1\n",  # non-hex inside
    ],
)
def test_malformed_digest_lines_return_none(mod: types.ModuleType, bad_line: str) -> None:
    assert mod.extract_push_digest(bad_line) is None


def test_failure_path_includes_tail_and_redacts_token(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    sentinel = "SLAIF-SENTINEL-GHCR-VALUE-4f9a2b7c1d3e8f00"
    stderr_tail = (
        b"The push refers to repository [ghcr.io/ulfe-lmi/slaif-local-coding]\n"
        b"c3d4e5f6a7b8: Preparing\n"
        b"a1b2c3d4e5f6: Pushed\n"
        b"credential guard line: " + sentinel.encode("ascii") + b"\n"
        b"denied: requested access to the resource is denied\n"
    )

    def fake_docker(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
        assert args[:1] == ("push",)
        assert args[1] == PUSH_REF
        return subprocess.CompletedProcess(
            args=["docker", *args],
            returncode=0,
            stdout=b"",
            stderr=stderr_tail,
        )

    monkeypatch.setattr(mod, "_docker", fake_docker)
    monkeypatch.setenv("SLAIF_GHCR_TOKEN", sentinel)
    with pytest.raises(mod.PublishError) as excinfo:
        mod._push_digest(PUSH_REF)
    message = str(excinfo.value)
    # The ref is named and the output tail is included ...
    assert PUSH_REF in message
    assert "denied: requested access to the resource is denied" in message
    # ... but the token value is redacted in every line.
    assert sentinel not in message
    assert "***" in message


def test_failure_path_without_token_env_keeps_tail(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    stderr_tail = b"c3d4e5f6a7b8: Preparing\ndeprecated: progress line\n"

    def fake_docker(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(
            args=["docker", *args], returncode=0, stdout=b"", stderr=stderr_tail
        )

    monkeypatch.setattr(mod, "_docker", fake_docker)
    monkeypatch.delenv("SLAIF_GHCR_TOKEN", raising=False)
    with pytest.raises(mod.PublishError) as excinfo:
        mod._push_digest(PUSH_REF)
    message = str(excinfo.value)
    assert PUSH_REF in message
    assert "c3d4e5f6a7b8: Preparing" in message
    assert "deprecated: progress line" in message


def test_build_push_references_are_qualified_for_rc_default(
    mod: types.ModuleType,
) -> None:
    fixture_sha = "0" * 40
    sha_ref, candidate_ref = mod.build_push_references(mod.REPO_DEFAULT, fixture_sha, "0.1.0-rc1")
    assert sha_ref == f"ghcr.io/ulfe-lmi/slaif-local-coding:sha-{fixture_sha}"
    assert candidate_ref == "ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc1"


def test_build_push_references_take_explicit_candidate_tag(
    mod: types.ModuleType,
) -> None:
    fixture_sha = "1" * 40
    sha_ref, candidate_ref = mod.build_push_references(
        "ulfe-lmi/slaif-local-coding", fixture_sha, "0.1.0-rc2"
    )
    assert sha_ref == f"ghcr.io/ulfe-lmi/slaif-local-coding:sha-{fixture_sha}"
    assert candidate_ref == "ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc2"


def test_forbidden_final_tags_are_closed_set(mod: types.ModuleType) -> None:
    # Order 013-i, D13: no code path of the RC workflow may write a final
    # or stable tag; the guard set is closed and complete.
    assert mod.FORBIDDEN_FINAL_TAGS == frozenset({"0.1.0", "latest", "stable", "v0.1.0"})
    assert "0.1.0-rc1" not in mod.FORBIDDEN_FINAL_TAGS


def _run_main(mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, *argv: str) -> int:
    monkeypatch.setattr(sys, "argv", ["release_registry_publish.py", *argv])
    return int(mod.main())


@pytest.mark.parametrize("final_tag", ["0.1.0", "latest", "stable", "v0.1.0"])
def test_main_rejects_final_release_tag(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch, final_tag: str
) -> None:
    # The rejection happens BEFORE any credential or registry access.
    monkeypatch.delenv("SLAIF_GHCR_TOKEN", raising=False)
    with pytest.raises(mod.PublishError, match="final/stable tag"):
        _run_main(
            mod,
            monkeypatch,
            "--local-image",
            "slaif-local-coding:local",
            "--git-sha",
            "0" * 40,
            "--release-tag",
            final_tag,
        )


def test_main_rejects_bad_git_sha(mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SLAIF_GHCR_TOKEN", raising=False)
    with pytest.raises(mod.PublishError, match="40-hex"):
        _run_main(
            mod,
            monkeypatch,
            "--local-image",
            "slaif-local-coding:local",
            "--git-sha",
            "short",
            "--release-tag",
            "0.1.0-rc1",
        )


def test_main_requires_token_for_private_package(
    mod: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Order 013-i, D13: the private package's tag state cannot be verified
    # anonymously, so a missing token fails closed before any mutation.
    monkeypatch.delenv("SLAIF_GHCR_TOKEN", raising=False)
    with pytest.raises(mod.PublishError, match="SLAIF_GHCR_TOKEN"):
        _run_main(
            mod,
            monkeypatch,
            "--local-image",
            "slaif-local-coding:local",
            "--git-sha",
            "0" * 40,
            "--release-tag",
            "0.1.0-rc1",
        )


def test_self_check_references_still_returns_zero(
    mod: types.ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    assert mod.self_check_references() == 0
    out = capsys.readouterr().out
    assert "reference self-check OK" in out
    assert "0.1.0-rc1" in out
    assert "forbidden final tags" in out
