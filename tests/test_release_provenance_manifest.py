"""Regeneration/drift gate for the release provenance manifest (order 009-a, E3).

Rebuilds the artifacts, regenerates the manifest from the actual build inputs,
and fails on any drift against the committed manifest or on forbidden content.
Only `generated_from.git_commit` may legitimately differ: the committed value
must be an ancestor of (or equal to) the current HEAD, so report-only child
commits do not invalidate the manifest while any build-input change does.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import types
from pathlib import Path
from typing import cast

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "release_provenance_manifest.py"
MANIFEST = REPO_ROOT / "packaging" / "release_provenance_manifest.json"
SCHEMA = REPO_ROOT / "packaging" / "release_provenance_manifest.schema.json"


def _load_generator() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("release_provenance_manifest", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load manifest generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def checker() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(
        "artifact_policy_check", REPO_ROOT / "scripts" / "artifact_policy_check.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load artifact policy checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def regenerated(tmp_path_factory: pytest.TempPathFactory) -> dict[str, object]:
    if shutil.which("uv") is None:
        pytest.fail("uv is required to build artifacts for the manifest gate")
    dist = tmp_path_factory.mktemp("dist")
    result = subprocess.run(
        ["uv", "build", "--out-dir", str(dist)],
        cwd=REPO_ROOT,
        capture_output=True,
        timeout=600,
    )
    assert result.returncode == 0, result.stderr.decode()
    module = _load_generator()
    built: dict[str, object] = module.build_manifest(REPO_ROOT, dist)
    return built


def test_manifest_and_schema_exist() -> None:
    assert MANIFEST.is_file()
    assert SCHEMA.is_file()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$id"] == "slaif-release-provenance-v1"
    committed = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert committed["schema"] == "slaif-release-provenance-v1"
    assert committed["schema_version"] == 1


def test_committed_manifest_matches_regenerated(regenerated: dict[str, object]) -> None:
    committed = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def strip_git(data: dict[str, object]) -> dict[str, object]:
        data = json.loads(json.dumps(data))
        generated = cast("dict[str, object]", data["generated_from"])
        generated["git_commit"] = None
        return data

    assert strip_git(committed) == strip_git(regenerated)


def test_committed_git_commit_is_ancestor_of_head(regenerated: dict[str, object]) -> None:
    committed = json.loads(MANIFEST.read_text(encoding="utf-8"))
    git_commit = committed["generated_from"]["git_commit"]
    assert re.fullmatch(r"[0-9a-f]{40}", git_commit)
    exists = subprocess.run(
        ["git", "cat-file", "-e", git_commit], cwd=REPO_ROOT, stdout=subprocess.PIPE
    )
    if exists.returncode != 0:
        pytest.fail("committed manifest git_commit is not resolvable in this checkout")
    head = (
        subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, stdout=subprocess.PIPE)
        .stdout.decode()
        .strip()
    )
    if git_commit == head:
        return
    is_ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", git_commit, head],
        cwd=REPO_ROOT,
        capture_output=True,
    )
    assert is_ancestor.returncode == 0, (
        "committed manifest git_commit is not an ancestor of HEAD; "
        "the manifest must be regenerated when build inputs change"
    )


def test_manifest_has_no_forbidden_content(checker: types.ModuleType) -> None:
    raw = MANIFEST.read_bytes()
    violations: list[str] = []
    checker._check_content(
        "manifest", "release_provenance_manifest.json", {"manifest": raw}, violations
    )
    assert violations == []
    # The manifest is content-free by construction: statuses are fixed classes.
    committed = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert committed["status"] == {
        "deployment_qualified": "disposable-environment-only",
        "cutover_performed": False,
        "released": False,
    }


def test_regenerated_manifest_matches_schema_shape(regenerated: dict[str, object]) -> None:
    # Closed top-level key set (mirrors the schema's additionalProperties=false).
    expected_keys = {
        "schema",
        "schema_version",
        "objective",
        "generated_from",
        "gateway_peer",
        "runtime",
        "artifacts",
        "templates",
        "reference_compatibility",
        "status",
        "limitations",
    }
    assert set(regenerated) == expected_keys
    artifacts = cast("dict[str, dict[str, object]]", regenerated["artifacts"])
    assert set(artifacts) == {"wheel", "sdist"}
    for artifact in artifacts.values():
        assert set(artifact) == {"name", "sha256", "size_bytes", "entry_count"}
        assert re.fullmatch(r"[0-9a-f]{64}", str(artifact["sha256"]))
    peer = cast("dict[str, object]", regenerated["gateway_peer"])
    assert set(peer) == {"repository", "commit", "server_module", "client_module"}
    assert peer["repository"] == "ulfe-lmi/slaif-api-gateway"
    assert re.fullmatch(r"[0-9a-f]{40}", str(peer["commit"]))
    compat = cast("dict[str, object]", regenerated["reference_compatibility"])
    client = cast("dict[str, object]", compat["codex_client"])
    assert compat["model_name"] == "qwen3.8-27b"
    assert client["version"] == "0.149.0"
    assert regenerated["limitations"], "limitations must not be empty"


def test_manifest_fails_on_injected_drift(regenerated: dict[str, object]) -> None:
    committed = json.loads(MANIFEST.read_text(encoding="utf-8"))
    drifted = json.loads(json.dumps(regenerated))
    wheel = cast("dict[str, object]", cast("dict[str, object]", drifted["artifacts"])["wheel"])
    wheel["sha256"] = "0" * 64
    assert drifted != committed
