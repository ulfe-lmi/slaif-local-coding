"""Order 013-i, B8 (extended by order 013-j, J2): scoped documentation
consistency gate tests.

Positive: the gate passes on the real repository tree. Negative fixtures in
temporary trees: a broken relative link, a stale 'this PR' line, a stale
0.1.0-released claim, a compose build key, a quickstart build token, a
pre-advanced-marker build token in INSTALL.md, a README release-state
section, a missing session export, a command-local env assignment, a
readyz-wait helper reference, a 'stop whatever' instruction, a missing
operator fact (platform/reader scope/RepoDigests), a missing secret guard,
the 'content-addressed source tag' terminology, an ARCHITECTURE.md R18
publication state, and a runbook 013-b attribution each fail the gate.
Stdlib only; no network, no host state.
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


SESSION_EXPORTS_BLOCK = (
    "export SLAIF_LOCAL_CODING_IMAGE=ghcr.io/ulfe-lmi/slaif-local-coding@sha256:D\n"
    "export SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml\n"
    "export SLAIF_ENV_FILE=/opt/slaif/adapter.env\n"
)

SECRET_GUARDS_BLOCK = (
    ': "${QWEN3090_API_KEY:?set QWEN3090_API_KEY before creating the env file}"\n'
    ': "${SLAIF_ADAPTER_SERVICE_TOKEN:?set SLAIF_ADAPTER_SERVICE_TOKEN '
    'before creating the env file}"\n'
    ': "${SLAIF_ADAPTER_SIGNING_SECRET:?set SLAIF_ADAPTER_SIGNING_SECRET '
    'before creating the env file}"\n'
)


def _operator_doc_body() -> str:
    """The facts the operator-session checks require (positive fixture)."""
    return (
        "Linux host (linux/amd64) with Docker Engine + Compose v2.\n"
        "External GHCR reader scope: read:packages (classic PAT; distinct\n"
        "from the Actions `packages: read` keyword).\n"
        "Verify the pulled tag resolves to the recorded digest via RepoDigests.\n"
        "Bounded health wait on the compose healthcheck (no extra helper file).\n"
        + SESSION_EXPORTS_BLOCK
        + SECRET_GUARDS_BLOCK
    )


def _make_docs_tree(root: Path) -> None:
    """Minimal repo tree that passes every gate check."""
    (root / "docs").mkdir(parents=True)
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / "README.md").write_text(
        "# Product\n\n"
        "See [QUICKSTART.md](QUICKSTART.md) and [INSTALL.md](INSTALL.md).\n"
        "Index: [docs/README.md](docs/README.md); license: [LICENSE](LICENSE).\n",
        encoding="utf-8",
    )
    (root / "QUICKSTART.md").write_text(
        "# Quickstart\n\nDocker pull-only path; nothing to build.\n\n" + _operator_doc_body(),
        encoding="utf-8",
    )
    (root / "INSTALL.md").write_text(
        "# Install\n\n"
        "## Docker primary\n\n"
        "Pull the image; the host builds nothing.\n\n" + _operator_doc_body() + "\n"
        "## Advanced: direct-host (systemd) installation\n\n"
        "This section may use `uv build` and `python -m venv`.\n",
        encoding="utf-8",
    )
    (root / "ARCHITECTURE.md").write_text(
        "# Architecture\n\n"
        "Current state: the RC is a separate later round; cutover not performed.\n",
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
        "RELEASE-CUTOVER-RUNBOOK.md",
    ):
        (root / "docs" / name).write_text(f"# {name}\n\nscoped doc\n", encoding="utf-8")
    (root / "compose.yaml").write_text(
        "name: x\n\nservices:\n  adapter:\n"
        "    image: ${SLAIF_LOCAL_CODING_IMAGE:?required explicit image}\n",
        encoding="utf-8",
    )
    (root / ".github" / "workflows" / "release-image.yml").write_text(
        "name: release\non:\n  workflow_dispatch:\n", encoding="utf-8"
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


def test_readme_release_status_section_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "README.md").write_text(
        "# Product\n\n"
        "See [QUICKSTART.md](QUICKSTART.md) and [INSTALL.md](INSTALL.md).\n\n"
        "## Release status\n\n"
        "0.1.0-rc1 is being prepared and frozen.\n",
        encoding="utf-8",
    )
    violations = checker.check_repo(tmp_path)
    assert any("readme-release-state" in v and "Release status" in v for v in violations)
    assert any("readme-release-state" in v and "being prepared and frozen" in v for v in violations)


def test_readme_objective_013_history_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "README.md").write_text(
        "# Product\n\n"
        "See [QUICKSTART.md](QUICKSTART.md) and [INSTALL.md](INSTALL.md).\n\n"
        "Objective 013 pushed the historical private tag during publication.\n",
        encoding="utf-8",
    )
    violations = checker.check_repo(tmp_path)
    assert any("readme-release-state" in v and "Objective-013" in v for v in violations)


def test_missing_session_export_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    body = _operator_doc_body().replace("export SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml\n", "")
    (tmp_path / "QUICKSTART.md").write_text(
        "# Quickstart\n\nDocker pull-only path.\n\n" + body, encoding="utf-8"
    )
    violations = checker.check_repo(tmp_path)
    assert any("session-export" in v and "SLAIF_CONFIG_FILE" in v for v in violations)


def test_command_local_env_assignment_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "INSTALL.md").write_text(
        "# Install\n\n"
        "## Docker primary\n\n" + _operator_doc_body() + "\n"
        "SLAIF_CONFIG_FILE=/opt/slaif/adapter.toml \\\n"
        "SLAIF_ENV_FILE=/opt/slaif/adapter.env \\\n"
        "docker compose pull\n\n"
        "## Advanced: direct-host (systemd) installation\n\n",
        encoding="utf-8",
    )
    violations = checker.check_repo(tmp_path)
    assert sum("command-local-env" in v for v in violations) == 2


def test_readyz_wait_helper_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "QUICKSTART.md").write_text(
        "# Quickstart\n\n" + _operator_doc_body() + "\nThen run packaging/readyz-wait.sh.\n",
        encoding="utf-8",
    )
    (tmp_path / "INSTALL.md").write_text(
        "# Install\n\n"
        "## Docker primary\n\n" + _operator_doc_body() + "\npackaging/readyz-wait.sh\n\n"
        "## Advanced: direct-host (systemd) installation\n\n",
        encoding="utf-8",
    )
    violations = checker.check_repo(tmp_path)
    assert any("QUICKSTART.md" in v and "readyz-wait-helper" in v for v in violations)
    assert any("INSTALL.md" in v and "readyz-wait-helper" in v for v in violations)


def test_stop_whatever_instruction_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "QUICKSTART.md").write_text(
        "# Quickstart\n\n" + _operator_doc_body() + "\nPort busy? Stop whatever owns the port.\n",
        encoding="utf-8",
    )
    violations = checker.check_repo(tmp_path)
    assert any("stop-whatever" in v for v in violations)


@pytest.mark.parametrize("token", ["linux/amd64", "read:packages", "RepoDigests"])
def test_missing_operator_fact_fails(checker: types.ModuleType, tmp_path: Path, token: str) -> None:
    _make_docs_tree(tmp_path)
    body = _operator_doc_body().replace(token, "REPLACED")
    (tmp_path / "INSTALL.md").write_text(
        "# Install\n\n"
        "## Docker primary\n\n" + body + "\n"
        "## Advanced: direct-host (systemd) installation\n\n",
        encoding="utf-8",
    )
    violations = checker.check_repo(tmp_path)
    assert any("operator-fact" in v and token in v for v in violations)


@pytest.mark.parametrize(
    "guard",
    [
        "${QWEN3090_API_KEY:?",
        "${SLAIF_ADAPTER_SERVICE_TOKEN:?",
        "${SLAIF_ADAPTER_SIGNING_SECRET:?",
    ],
)
def test_missing_secret_guard_fails(checker: types.ModuleType, tmp_path: Path, guard: str) -> None:
    _make_docs_tree(tmp_path)
    body = _operator_doc_body().replace(f"{guard[1:-1]}?set", "PLAIN")
    (tmp_path / "QUICKSTART.md").write_text(
        "# Quickstart\n\nDocker pull-only path.\n\n" + body, encoding="utf-8"
    )
    violations = checker.check_repo(tmp_path)
    assert any("secret-guard" in v and guard in v for v in violations)


def test_content_addressed_source_tag_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "docs" / "TOPOLOGY.md").write_text(
        "# Topology\n\nThe publish uses tag 0.1.0-rc1 + content-addressed source tag.\n",
        encoding="utf-8",
    )
    violations = checker.check_repo(tmp_path)
    assert any("content-addressed-source-tag" in v for v in violations)


def test_architecture_r18_holding_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "ARCHITECTURE.md").write_text(
        "# Architecture\n\nPublication is PENDING as of this PR's head on the order's R18 hold.\n",
        encoding="utf-8",
    )
    violations = checker.check_repo(tmp_path)
    assert any("file-stale-claim" in v and "R18" in v for v in violations)
    assert any("file-stale-claim" in v and "PENDING as of this PR" in v for v in violations)
    assert any("stale-claim" in v and "this PR" in v for v in violations)


def test_runbook_013b_attribution_fails(checker: types.ModuleType, tmp_path: Path) -> None:
    _make_docs_tree(tmp_path)
    (tmp_path / "docs" / "RELEASE-CUTOVER-RUNBOOK.md").write_text(
        "# Runbook\n\n"
        "The 0.1.0 publication has since been performed (round 013-b; the "
        "digest is recorded in `packaging/release_record.json`).\n",
        encoding="utf-8",
    )
    violations = checker.check_repo(tmp_path)
    assert any("file-stale-claim" in v and "013-b" in v for v in violations)
    assert any("file-stale-claim" in v and "release_record.json" in v for v in violations)


def test_historical_runbook_block_is_allowed(checker: types.ModuleType, tmp_path: Path) -> None:
    """Unmistakably historical prose (non-public package, legacy output)
    does not trip the runbook current-claim patterns."""
    _make_docs_tree(tmp_path)
    (tmp_path / "docs" / "RELEASE-CUTOVER-RUNBOOK.md").write_text(
        "# Runbook\n\n"
        "Historical: rounds 013-b..013-g performed a registry-only publication\n"
        "to the non-public package (legacy, NOT the RC target); the\n"
        "final-release record packaging/release_record.json does not exist.\n",
        encoding="utf-8",
    )
    violations = [v for v in checker.check_repo(tmp_path) if "file-stale-claim" in v]
    assert violations == []
