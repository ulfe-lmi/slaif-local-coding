"""Pytest gate for the mechanical release-artifact policy (order 009-a, B3).

Builds fresh wheel+sdist artifacts with the locked toolchain, runs the same
inspection the CI/local-gate script uses, and verifies the scanner detects
injected violations (negative control).
"""

from __future__ import annotations

import importlib.util
import json
import types
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "scripts" / "artifact_policy_check.py"


def _load_checker() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("artifact_policy_check", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load artifact policy checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def checker() -> types.ModuleType:
    return _load_checker()


@pytest.fixture(scope="module")
def built_dist(tmp_path_factory: pytest.TempPathFactory) -> Path:
    import shutil
    import subprocess

    if shutil.which("uv") is None:
        pytest.fail("uv is required to build artifacts for the policy gate")
    dist = tmp_path_factory.mktemp("dist")
    result = subprocess.run(
        ["uv", "build", "--out-dir", str(dist)],
        cwd=REPO_ROOT,
        capture_output=True,
        timeout=600,
    )
    assert result.returncode == 0, result.stderr.decode()
    assert len(list(dist.glob("slaif_local_coding-*.whl"))) == 1
    assert len(list(dist.glob("slaif_local_coding-*.tar.gz"))) == 1
    return dist


def test_wheel_is_verified_clean(checker: types.ModuleType, built_dist: Path) -> None:
    result = checker.inspect_artifacts(built_dist)
    assert result["ok"], result["violations"]
    assert result["facts"]["wheel_top_level"] == [
        "slaif_local_coding",
        "slaif_local_coding-0.1.0.dist-info",
    ]
    assert result["facts"]["wheel_package_file_count"] >= 20


def test_sdist_is_developer_only_whitelist(checker: types.ModuleType, built_dist: Path) -> None:
    result = checker.inspect_artifacts(built_dist)
    assert result["ok"], result["violations"]
    sdist_files = checker._artifact_files(next(built_dist.glob("slaif_local_coding-*.tar.gz")))
    # Orchestration transcripts, runtime state, and host-specific files never
    # ship in the developer archive.
    for forbidden in (
        "oap/orders",
        "oap/reports",
        "oap/active",
        "oap/evidence",
        "oap/bin",
        "oap/runtime.env.example",
        "scripts",
        "references",
        "Local",
        "clean",
        "unchanged",
        "AGENTS.md",
        "docs/LIVE-TEST-ENVIRONMENT.md",
        "tests/test_config.py",
        "tests/test_packaging.py",
    ):
        offenders = [
            name for name in sdist_files if name == forbidden or name.startswith(forbidden + "/")
        ]
        assert not offenders, (forbidden, offenders)
    # The runtime package is present and complete in the archive (under src/).
    assert "src/slaif_local_coding/__init__.py" in sdist_files
    assert any(name.startswith("src/slaif_local_coding/constitution/") for name in sdist_files)


def test_forbidden_entries_are_detected(checker: types.ModuleType, tmp_path: Path) -> None:
    # Synthetic wheel: a forbidden oap transcript entry plus a host path.
    wheel_path = tmp_path / "bad.whl"
    with zipfile.ZipFile(wheel_path, "w") as wheel:
        wheel.writestr("slaif_local_coding/__init__.py", '"""x."""\n')
        wheel.writestr("slaif_local_coding-0.1.0.dist-info/METADATA", "Metadata-Version: 2.1\n")
        wheel.writestr("slaif_local_coding-0.1.0.dist-info/WHEEL", "Wheel-Version: 1.0\n")
        wheel.writestr("slaif_local_coding-0.1.0.dist-info/RECORD", "")
        wheel.writestr("oap/orders/001-evil.md", "# transcript\n")
        wheel.writestr("slaif_local_coding/leak.py", "HOST = '/synology/homes/x'\n")
    files = checker._artifact_files(wheel_path)
    violations: list[str] = []
    checker._check_paths("wheel", "bad.whl", list(files), violations)
    checker._check_content("wheel", "bad.whl", files, violations)
    joined = "\n".join(violations)
    assert "oap/orders/001-evil.md" in joined
    assert "host_path_synology" in joined


def test_forbidden_credential_content_is_detected(checker: types.ModuleType) -> None:
    violations: list[str] = []
    files = {
        "config/adapter.env": b"QWEN3090_API_KEY=abcdef1234567890\n",
        "docs/note.md": b"LAN endpoint http://10.8.132.75:18020/v1\n",
    }
    checker._check_content("sdist", "bad.tar.gz", files, violations)
    joined = "\n".join(violations)
    assert "upstream_api_key_value" in joined
    assert "private_lan_endpoint" in joined


def test_clean_reference_content_passes(checker: types.ModuleType) -> None:
    violations: list[str] = []
    files = {
        "config/adapter.example.toml": b'api_key_env = "QWEN3090_API_KEY"\n',
        "README.md": b"Reference deployment: private vLLM endpoint (names only).\n",
    }
    checker._check_content("sdist", "ok.tar.gz", files, violations)
    assert violations == []


def test_inspect_reports_missing_artifacts(checker: types.ModuleType, tmp_path: Path) -> None:
    result = checker.inspect_artifacts(tmp_path)
    assert not result["ok"]
    assert any("expected exactly one wheel" in v for v in result["violations"])
    assert any("expected exactly one sdist" in v for v in result["violations"])


def test_inspect_json_is_serializable(checker: types.ModuleType, built_dist: Path) -> None:
    result = checker.inspect_artifacts(built_dist)
    payload = json.dumps(result, sort_keys=True)
    assert "wheel_sha256" in json.loads(payload)["facts"]
