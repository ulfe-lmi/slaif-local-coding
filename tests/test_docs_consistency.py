"""Order 013-i, B8: scoped documentation consistency gate tests.

Positive: the gate passes on the real repository tree. Negative fixtures in
temporary trees: a broken relative link, a stale 'this PR' line, a stale
0.1.0-released claim, a compose build key, a quickstart build token, and a
pre-advanced-marker build token in INSTALL.md each fail the gate. Stdlib
only; no network, no host state.
"""

from __future__ import annotations

import importlib.util
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "scripts" / "docs_consistency_check.py"


def _load_checker() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("docs_consistency_check", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load docs consistency checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def checker() -> types.ModuleType:
    return _load_checker()


def _make_docs_tree(root: Path) -> None:
    """Minimal repo tree that passes every gate check."""
    (root / "docs").mkdir(parents=True)
    (root / "README.md").write_text(
        "# Product\n\n"
        "See [QUICKSTART.md](QUICKSTART.md) and [INSTALL.md](INSTALL.md).\n"
        "Index: [docs/README.md](docs/README.md); license: [LICENSE](LICENSE).\n",
        encoding="utf-8",
    )
    (root / "QUICKSTART.md").write_text(
        "# Quickstart\n\nDocker pull-only path; nothing to build.\n", encoding="utf-8"
    )
    (root / "INSTALL.md").write_text(
        "# Install\n\n"
        "## Docker primary\n\n"
        "Pull the image; the host builds nothing.\n\n"
        "## Advanced: direct-host (systemd) installation\n\n"
        "This section may use `uv build` and `python -m venv`.\n",
        encoding="utf-8",
    )
    (root / "LICENSE").write_text("Apache-2.0\n", encoding="utf-8")
    (root / "NOTICE").write_text("notice\n", encoding="utf-8")
    for name in (
        "README.md",
        "RC-HANDOFF.md",
        "DOCKER-INSTALL.md",
        "DEPLOYMENT.md",
        "ADAPTER-CONFIGURATION.md",
        "TOPOLOGY.md",
        "DOCKER-SECURITY-DELTA.md",
        "RELEASE-ARTIFACT-POLICY.md",
    ):
        (root / "docs" / name).write_text(f"# {name}\n\nscoped doc\n", encoding="utf-8")
    (root / "compose.yaml").write_text(
        "name: x\n\nservices:\n  adapter:\n"
        "    image: ${SLAIF_LOCAL_CODING_IMAGE:?required explicit image}\n",
        encoding="utf-8",
    )


def test_real_repo_passes(checker: types.ModuleType) -> None:
    assert checker.check_repo(REPO_ROOT) == []


def test_real_repo_cli_exit_zero(
    checker: types.ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    assert checker.main(["--repo-root", str(REPO_ROOT)]) == 0
    assert "docs consistency: OK" in capsys.readouterr().out


def test_broken_relative_link_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "QUICKSTART.md").write_text(
        "# Quickstart\n\nSee [MISSING-DOC.md](MISSING-DOC.md).\n", encoding="utf-8"
    )
    violations = checker.check_repo(tmp_path)
    assert any(
        "QUICKSTART.md" in v and "MISSING-DOC.md" in v and "broken-link" in v for v in violations
    )


def test_missing_required_file_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "NOTICE").unlink()
    violations = checker.check_repo(tmp_path)
    assert any(v.startswith("NOTICE:") and "required-file" in v for v in violations)


def test_readme_without_quickstart_link_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "README.md").write_text(
        "# Product\n\nSee [INSTALL.md](INSTALL.md) only.\n", encoding="utf-8"
    )
    violations = checker.check_repo(tmp_path)
    assert any("readme-links" in v and "QUICKSTART.md" in v for v in violations)


def test_stale_this_pr_claim_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "README.md").write_text(
        "# Product\n\nSee [QUICKSTART.md](QUICKSTART.md) and "
        "[INSTALL.md](INSTALL.md).\n\nThe status changes once this PR merges.\n",
        encoding="utf-8",
    )
    violations = checker.check_repo(tmp_path)
    assert any("stale-claim" in v and "this PR" in v for v in violations)


def test_stale_released_claim_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "INSTALL.md").write_text(
        "# Install\n\nVersion 0.1.0 is released to GHCR and ready.\n\n"
        "## Advanced: direct-host (systemd) installation\n\n",
        encoding="utf-8",
    )
    violations = checker.check_repo(tmp_path)
    assert any("stale-claim" in v and "0.1.0" in v for v in violations)


def test_rc_wording_is_not_a_false_positive(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "README.md").write_text(
        "# Product\n\nSee [QUICKSTART.md](QUICKSTART.md) and "
        "[INSTALL.md](INSTALL.md).\n\n"
        "The historical private 0.1.0 tag was never published to users and is\n"
        "not the RC benchmark target; 0.1.0-rc1 is prepared as a candidate.\n",
        encoding="utf-8",
    )
    assert checker.check_repo(tmp_path) == []


def test_compose_build_key_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "compose.yaml").write_text(
        "name: x\n\nservices:\n  adapter:\n"
        "    image: ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc1\n"
        "    build:\n      context: .\n",
        encoding="utf-8",
    )
    violations = checker.check_repo(tmp_path)
    assert any("compose-build-key" in v for v in violations)


def test_quickstart_build_token_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "QUICKSTART.md").write_text(
        "# Quickstart\n\nFirst run `uv build` locally.\n", encoding="utf-8"
    )
    violations = checker.check_repo(tmp_path)
    assert any("quickstart-build-token" in v and "uv build" in v for v in violations)


def test_install_pre_marker_build_token_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "INSTALL.md").write_text(
        "# Install\n\nThe quick way: run `uv sync --frozen` first.\n\n"
        "## Advanced: direct-host (systemd) installation\n\n"
        "uv build is allowed here.\n",
        encoding="utf-8",
    )
    violations = checker.check_repo(tmp_path)
    assert any("install-pre-marker-build-token" in v and "uv sync" in v for v in violations)


def test_install_missing_marker_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "INSTALL.md").write_text("# Install\n\nDocker only.\n", encoding="utf-8")
    violations = checker.check_repo(tmp_path)
    assert any("install-marker" in v for v in violations)
