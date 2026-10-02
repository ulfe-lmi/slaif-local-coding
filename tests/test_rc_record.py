"""Order 013-i, C12 (completed by order 013-j, J5): RC artifact record
generator, handoff renderer, and strict loader tests.

Covers the strict builder (``scripts/rc_artifact_record.build_rc_record`` —
slaif-rc-record-v3: the direct source-input hash map, build-environment
pins, base-image identities, supported platform, the publishing
workflow run's head SHA, and the DERIVED real-Codex compatibility
qualification facts (order 014-b, workstream B.3: one manifest-verified,
closed-schema facts file from the append-only testing ledger; no manual
verdict assertions)), the ledger-manifest tamper classes, the companion
JSON Schema / record consistency regression (order 014-b, workstream
B.2), the deterministic handoff renderer (``render_handoff``), the
frozen-identity emitters (``_emit_frozen``), and the round-trip through
the provenance generator's closed-key strict loader
(``release_provenance_manifest.load_rc_record``).
Deterministic: temporary repo fixtures, no network, no registry, no
docker, no fake digest mode.
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import re
import subprocess
import types
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RC_SCRIPT = REPO_ROOT / "scripts" / "rc_artifact_record.py"
GENERATOR = REPO_ROOT / "scripts" / "release_provenance_manifest.py"
COMPANION_SCHEMA = REPO_ROOT / "packaging" / "rc_artifact_record.schema.json"
REPO_RECORD = REPO_ROOT / "packaging" / "rc_record.json"

WHEEL_SHA = "d" * 64
GATEWAY_SHA = "f" * 40
DIGEST = "sha256:" + "b" * 64
# The source commit is a REAL commit in the fixture git repository (order
# 014-c, workstream B: the record builder binds the literal supplied
# source ref with ref-based input maps, so the fixture must be a git
# repository). The fixture tags the source commit `fixture-source`.
SOURCE_TAG = "fixture-source"
PUBLISHED_AT = "2026-09-20T00:00:00Z"
LOCK_CONTENT = b"version = 1\n# fixture lock\n"
# The retained qualified client (order 014-b, workstream D): exact Codex
# CLI 0.149.0 standalone release binary.
CLIENT_VERSION = "0.149.0"
CLIENT_SHA = "bbc3341e44c9ead340ed9570c17be936e37870f570751a941699ffd04d672827"
# The single manifest-verified facts file the compatibility section is
# derived from (order 014-b, workstream B.3): the next ledger number.
QUALIFICATION_FACTS = "oap/evidence/testing-ledger/005/real-codex-rc9-qualification.json"
EVIDENCE_PATH = "oap/evidence/testing-ledger/005"
COMPATIBILITY: dict[str, object] = {
    "client_version": CLIENT_VERSION,
    "client_sha256": CLIENT_SHA,
    "topology": "standalone-loopback-no-gateway",
    "arm_verdicts": {"vision": "pass", "cache": "pass", "both": "pass"},
    "direct_control": "pass",
    "evidence_path": EVIDENCE_PATH,
}
# The fixture Dockerfile carries the same digest-pinned bases as the
# repository Dockerfile (non-secret build facts, committed).
UV_IMAGE = (
    "ghcr.io/astral-sh/uv:0.12.5@"
    "sha256:e85be844203885286c60ffad8a858d48afb6c5a5c237ca0e67f12e74b8f174b1"
)
PYTHON_IMAGE = (
    "python:3.12-slim-bookworm@"
    "sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254"
)
FIXTURE_DOCKERFILE = (
    f"FROM {UV_IMAGE} AS uv-provider\n"
    f"FROM {PYTHON_IMAGE} AS build\n"
    f"FROM {PYTHON_IMAGE} AS runtime\n"
)
# Minimal hermetic pyproject so the source-input map policy is fully
# determined inside the fixture (no real build backend required). The
# tests/ include is deliberate (order 014-c, workstream B): tests are
# mapped inputs — the RC4 failure was an altered mapped test after the
# source freeze.
FIXTURE_PYPROJECT = (
    "[project]\n"
    'name = "fixture"\n'
    'version = "0.1.0"\n'
    "\n"
    "[tool.hatch.build]\n"
    "exclude = []\n"
    "\n"
    "[tool.hatch.build.targets.sdist]\n"
    'include = ["pyproject.toml", "README.md", "LICENSE", "uv.lock", "Dockerfile", "tests"]\n'
)

V3_KEYS = {
    "schema",
    "rc_identifier",
    "product_version",
    "image_source_commit",
    "oci_image_reference",
    "oci_image_digest",
    "oci_tags",
    "published_at",
    "publication_workflow",
    "publication_workflow_run_id",
    "workflow_head_sha",
    "private_registry_auth_required",
    "final_public_release",
    "cutover_performed",
    "wheel_sha256",
    "dependency_lock_sha256",
    "gateway_authority_sha",
    "build_environment",
    "build_toolchain",
    "base_images",
    "image_platform",
    "source_input_hashes",
    "deployment_assumptions",
    "compatibility",
}


def _load_module(path: Path, name: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def rc_mod() -> types.ModuleType:
    return _load_module(RC_SCRIPT, "rc_artifact_record")


@pytest.fixture(scope="module")
def generator() -> types.ModuleType:
    return _load_module(GENERATOR, "release_provenance_manifest_for_rc_tests")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _valid_facts(*, direct: str | None = "PASS") -> dict[str, object]:
    """A fully valid closed-schema v2 gate facts record (the gate's own
    validator accepts it); DIRECT is contextual (PASS/FAIL/absent)."""
    arms: dict[str, dict[str, object]] = {}
    for arm, reqs, compiler_calls, cache_entries in (
        ("VISION", 2, 0, 0),
        ("CACHE", 2, 1, 1),
        ("BOTH", 2, 1, 1),
    ):
        arms[arm] = {
            "attempts": 1,
            "exit_status": 0,
            "duration_seconds": 10,
            "sentinel_present": True,
            "sentinel_size_bytes": 3,
            "adapter_requests_ok": reqs,
            "adapter_requests_500": 0,
            "adapter_requests_422": 0,
            "adapter_requests_total": reqs,
            "upstream_failures": 0,
            "compiler_calls": compiler_calls,
            "compiler_cache_entries": cache_entries,
            "tool_interactions": 2,
            "stdout_bytes": 120,
            "stderr_bytes": 300,
            "verdict": "PASS",
            "failure_class": "none",
        }
    if direct is not None:
        arms["DIRECT"] = {
            "attempts": 1,
            "exit_status": 0,
            "duration_seconds": 5,
            "sentinel_present": True,
            "sentinel_size_bytes": 3,
            "adapter_requests_ok": 0,
            "adapter_requests_500": 0,
            "adapter_requests_422": 0,
            "adapter_requests_total": 0,
            "upstream_failures": 0,
            "compiler_calls": 0,
            "compiler_cache_entries": 0,
            "tool_interactions": 1,
            "stdout_bytes": 90,
            "stderr_bytes": 280,
            "verdict": direct,
            "failure_class": "none" if direct == "PASS" else "codex-exit",
        }
    return {
        "schema": "slaif-real-codex-rc-qualification-v2",
        "created_at": "2026-09-28T00:00:00Z",
        "client": {
            "version": CLIENT_VERSION,
            "sha256": CLIENT_SHA,
            "binary_class": "standalone-release",
        },
        "wheel": {
            "sha256": WHEEL_SHA,
            "expected_sha256": WHEEL_SHA,
            "binding": "equal",
        },
        "topology": (
            "disposable-codex-home;loopback-adapter;port-18031;"
            "existing-backend;gateway-ingress-disabled"
        ),
        "limits": {
            "output_cap_bytes": 1048576,
            "max_attempts": 2,
            "attempt_timeout_seconds": 600,
            "total_timeout_seconds": 5400,
            "max_adapter_requests": 64,
            "max_compiler_calls": 4,
            "max_tool_interactions": 8,
            "arm_count": len(arms),
        },
        "arms": arms,
        "protected_state_unchanged": True,
        "protected_state": {
            "files_checked": 13,
            "files_changed": 0,
            "units": {"qwen-serving-vision.service": "active"},
            "ports": {"18020": 1, "18031": 0},
        },
        "disposable_state_removed": True,
        "verdict": "PASS",
    }


def _write_qualification_ledger(
    repo: Path,
    facts: dict[str, object] | None = None,
    *,
    facts_name: str = "real-codex-rc9-qualification.json",
    manifest_entries: dict[str, str] | None = None,
) -> Path:
    """Write the closed ledger directory (README + facts + MANIFEST.sha256
    covering exactly the directory minus the manifest itself)."""
    if facts is None:
        facts = _valid_facts()
    ledger = repo / "oap" / "evidence" / "testing-ledger" / "005"
    ledger.mkdir(parents=True, exist_ok=True)
    (ledger / "README.md").write_text("fixture ledger entry\n", encoding="utf-8")
    (ledger / facts_name).write_text(
        json.dumps(facts, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if manifest_entries is None:
        manifest_entries = {
            "oap/evidence/testing-ledger/005/README.md": _sha256_file(ledger / "README.md"),
            f"oap/evidence/testing-ledger/005/{facts_name}": _sha256_file(ledger / facts_name),
        }
    (ledger / "MANIFEST.sha256").write_text(
        "\n".join(f"{digest}  {rel}" for rel, digest in sorted(manifest_entries.items())) + "\n",
        encoding="utf-8",
    )
    return ledger


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", *args],
        capture_output=True,
        check=True,
    )
    return proc.stdout.decode().strip()


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def _source_sha(repo: Path) -> str:
    return _git(repo, "rev-parse", SOURCE_TAG)


def _fixture_manifest(
    rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path
) -> dict[str, object]:
    """The committed v5 manifest recording the SOURCE ref's input map
    (the J4/014-c law: the record is built only where the source-ref map
    equals the recorded map and the checkout map equals the same map)."""
    source_sha = _git(repo, "rev-parse", SOURCE_TAG)
    return {
        "schema": "slaif-release-provenance-v5",
        "generated_from": {"git_commit": source_sha},
        "artifacts": {"wheel": {"sha256": WHEEL_SHA}},
        "gateway_peer": {"commit": GATEWAY_SHA},
        "build": {"build_environment": dict(generator.BUILD_ENVIRONMENT)},
        "source_inputs": dict(rc_mod.map_from_git_commit(repo, source_sha)),
    }


def _write_manifest(rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path) -> None:
    (repo / "packaging").mkdir(exist_ok=True)
    (repo / "packaging" / "release_provenance_manifest.json").write_text(
        json.dumps(_fixture_manifest(rc_mod, generator, repo)), encoding="utf-8"
    )


@pytest.fixture()
def repo(rc_mod: types.ModuleType, generator: types.ModuleType, tmp_path: Path) -> Path:
    """Fixture git repository with the truthful A/B sequence (order
    014-c, workstream B): source commit S (tagged `fixture-source`)
    carrying the exact mapped inputs, then a derived-metadata child
    (manifest + qualification ledger only) at which the builder runs."""
    (tmp_path / "LICENSE").write_text("Apache-2.0\n", encoding="utf-8")
    _git(tmp_path, "init", "-q")
    _commit(tmp_path, "C0: license only")
    (tmp_path / "pyproject.toml").write_text(FIXTURE_PYPROJECT, encoding="utf-8")
    (tmp_path / "README.md").write_text("# fixture\n", encoding="utf-8")
    (tmp_path / "uv.lock").write_bytes(LOCK_CONTENT)
    (tmp_path / "Dockerfile").write_text(FIXTURE_DOCKERFILE, encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_fixture.py").write_text(
        "def test_fixture():\n    assert True\n", encoding="utf-8"
    )
    _commit(tmp_path, "S: source inputs")
    _git(tmp_path, "tag", SOURCE_TAG)
    _write_manifest(rc_mod, generator, tmp_path)
    _write_qualification_ledger(tmp_path)
    _commit(tmp_path, "B: derived metadata (manifest + ledger)")
    return tmp_path


@pytest.fixture()
def repo_lock_unmapped(
    rc_mod: types.ModuleType, generator: types.ModuleType, tmp_path: Path
) -> Path:
    """Like `repo`, but the dependency lock is NOT a mapped input (the
    fixture policy excludes it) so the source-ref lock binding
    (order 014-c, workstream B.3) is observable: a later-tree lock drift
    passes the input-map checks and must still be ignored by the
    record's lock fact."""
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'name = "fixture"\n'
        'version = "0.1.0"\n'
        "\n"
        "[tool.hatch.build]\n"
        'exclude = ["uv.lock"]\n'
        "\n"
        "[tool.hatch.build.targets.sdist]\n"
        'include = ["pyproject.toml", "README.md", "LICENSE", "Dockerfile", "tests"]\n',
        encoding="utf-8",
    )
    (tmp_path / "LICENSE").write_text("Apache-2.0\n", encoding="utf-8")
    _git(tmp_path, "init", "-q")
    _commit(tmp_path, "C0: license only")
    (tmp_path / "README.md").write_text("# fixture\n", encoding="utf-8")
    (tmp_path / "uv.lock").write_bytes(LOCK_CONTENT)
    (tmp_path / "Dockerfile").write_text(FIXTURE_DOCKERFILE, encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_fixture.py").write_text(
        "def test_fixture():\n    assert True\n", encoding="utf-8"
    )
    _commit(tmp_path, "S: source inputs (lock unmapped)")
    _git(tmp_path, "tag", SOURCE_TAG)
    _write_manifest(rc_mod, generator, tmp_path)
    _write_qualification_ledger(tmp_path)
    _commit(tmp_path, "B: derived metadata (manifest + ledger)")
    return tmp_path


def _lock_sha() -> str:
    return hashlib.sha256(LOCK_CONTENT).hexdigest()


def _fixture_base_images(generator: types.ModuleType, repo: Path) -> dict[str, dict[str, str]]:
    return {
        stage: {"name": fact["name"], "digest": fact["digest"]}
        for stage, fact in generator._dockerfile_base_images(repo).items()
    }


def test_derive_compatibility_happy_path(rc_mod: types.ModuleType, repo: Path) -> None:
    derived = rc_mod.derive_compatibility(repo, QUALIFICATION_FACTS)
    assert derived == COMPATIBILITY


def test_derive_compatibility_direct_variants(rc_mod: types.ModuleType, repo: Path) -> None:
    # A failing contextual DIRECT arm records a blocker; absent = not_run.
    _write_qualification_ledger(repo, _valid_facts(direct="FAIL"))
    derived = rc_mod.derive_compatibility(repo, QUALIFICATION_FACTS)
    assert derived["direct_control"] == "blocked"
    _write_qualification_ledger(repo, _valid_facts(direct=None))
    derived = rc_mod.derive_compatibility(repo, QUALIFICATION_FACTS)
    assert derived["direct_control"] == "not_run"


@pytest.mark.parametrize(
    "tamper",
    [
        # manifest integrity
        lambda r: (r / "oap/evidence/testing-ledger/005/README.md").write_text(
            "altered\n", encoding="utf-8"
        ),
        lambda r: (r / "oap/evidence/testing-ledger/005/extra.txt").write_text(
            "not in manifest\n", encoding="utf-8"
        ),
        lambda r: (r / "oap/evidence/testing-ledger/005/README.md").unlink(),
        lambda r: _rewrite_manifest(
            r,
            line_filter=lambda line: line.replace("  oap/", " oap/"),  # single space
        ),
        lambda r: _rewrite_manifest(r, line_filter=lambda line: line + "x"),
        # facts path identity
        "wrong-facts-filename",
        "wrong-ledger-number",
        # facts verdicts / state
        lambda r: _rewrite_facts(r, verdict="BLOCKED"),
        lambda r: _rewrite_facts(r, protected_state_unchanged=False),
        lambda r: _rewrite_facts(r, disposable_state_removed=False),
        lambda r: _rewrite_facts(r, arm="CACHE", verdict="FAIL"),
        lambda r: _rewrite_facts(r, drop_arm="BOTH"),
        # wheel / client / topology binding
        lambda r: _rewrite_facts(r, wheel_sha256="c" * 64),
        lambda r: _rewrite_facts(r, wheel_binding="not-verified"),
        lambda r: _rewrite_facts(r, client_version="9.9.9"),
        lambda r: _rewrite_facts(r, client_sha256="c" * 64),
        lambda r: _rewrite_facts(r, topology="standalone-with-gateway"),
        # closed-schema drift
        lambda r: _rewrite_facts(r, extra_top_key="x"),
    ],
    ids=[
        "manifest-hash-mismatch",
        "manifest-extra-file",
        "manifest-missing-entry",
        "manifest-single-space",
        "manifest-long-line",
        "wrong-facts-filename",
        "wrong-ledger-number",
        "overall-blocked",
        "protected-state-changed",
        "disposable-not-removed",
        "arm-cache-fail",
        "arm-both-missing",
        "wheel-mismatch",
        "wheel-binding-unverified",
        "client-version-drift",
        "client-sha-drift",
        "topology-drift",
        "facts-key-drift",
    ],
)
def test_derive_compatibility_tamper_classes(
    rc_mod: types.ModuleType, repo: Path, tamper: object
) -> None:
    """Every tampering/mismatch class fails closed (order 014-b, B.3)."""
    facts_rel = QUALIFICATION_FACTS
    if tamper == "wrong-facts-filename":
        facts_rel = "oap/evidence/testing-ledger/003/real-codex-rc3-qualification.json"
        _write_qualification_ledger(repo, facts_name="real-codex-rc3-qualification.json")
    elif tamper == "wrong-ledger-number":
        facts_rel = "oap/evidence/testing-ledger/3/real-codex-rc9-qualification.json"
    elif callable(tamper):
        tamper(repo)
    with pytest.raises(rc_mod.RCRecordError):
        rc_mod.derive_compatibility(repo, facts_rel)


def _rewrite_facts(repo: Path, **overrides: object) -> None:
    """Rewrite the ledger facts with targeted deviations, then re-sign the
    ledger manifest so ONLY the targeted fact is the deviation."""
    facts = json.loads((repo / QUALIFICATION_FACTS).read_text(encoding="utf-8"))
    arm = overrides.pop("arm", None)
    drop_arm = overrides.pop("drop_arm", None)
    if arm is not None:
        facts["arms"][str(arm)]["verdict"] = overrides.pop("verdict", "FAIL")
    if drop_arm is not None:
        del facts["arms"][str(drop_arm)]
    if "verdict" in overrides:
        facts["verdict"] = overrides.pop("verdict")
    if "wheel_sha256" in overrides:
        facts["wheel"]["sha256"] = overrides.pop("wheel_sha256")
    if "wheel_binding" in overrides:
        facts["wheel"]["binding"] = overrides.pop("wheel_binding")
    if "client_version" in overrides:
        facts["client"]["version"] = overrides.pop("client_version")
    if "client_sha256" in overrides:
        facts["client"]["sha256"] = overrides.pop("client_sha256")
    if "topology" in overrides:
        facts["topology"] = overrides.pop("topology")
    if "extra_top_key" in overrides:
        facts[str(overrides.pop("extra_top_key"))] = 1
    for key, value in overrides.items():
        facts[key] = value
    (repo / QUALIFICATION_FACTS).write_text(
        json.dumps(facts, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _resign_ledger(repo)


def _resign_ledger(repo: Path) -> None:
    """Recompute the ledger manifest after a tampered facts rewrite so the
    manifest stays hash-valid and ONLY the targeted fact is the deviation."""
    ledger = repo / "oap" / "evidence" / "testing-ledger" / "005"
    entries = {
        f"oap/evidence/testing-ledger/005/{p.name}": _sha256_file(p)
        for p in sorted(ledger.iterdir())
        if p.is_file() and p.name != "MANIFEST.sha256"
    }
    (ledger / "MANIFEST.sha256").write_text(
        "\n".join(f"{d}  {rel}" for rel, d in sorted(entries.items())) + "\n",
        encoding="utf-8",
    )


def _rewrite_manifest(repo: Path, line_filter: Callable[[str], str]) -> None:
    ledger = repo / "oap" / "evidence" / "testing-ledger" / "005"
    manifest = ledger / "MANIFEST.sha256"
    lines = manifest.read_text(encoding="utf-8").splitlines()
    manifest.write_text("\n".join(line_filter(line) for line in lines) + "\n", encoding="utf-8")


def test_build_rc_record_happy_path(
    rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path
) -> None:
    source = _source_sha(repo)
    record = rc_mod.build_rc_record(
        repo, source, DIGEST, source, PUBLISHED_AT, None, QUALIFICATION_FACTS
    )
    assert set(record) == V3_KEYS
    assert record["schema"] == "slaif-rc-record-v3"
    assert record["rc_identifier"] == "0.1.0-rc9"
    assert record["product_version"] == "0.1.0"
    assert record["image_source_commit"] == source
    assert record["oci_image_reference"] == "ghcr.io/ulfe-lmi/slaif-local-coding"
    assert record["oci_image_digest"] == DIGEST
    assert record["oci_tags"] == ["0.1.0-rc9", f"sha-{source}"]
    assert record["published_at"] == PUBLISHED_AT
    assert record["publication_workflow"] == "release-image.yml"
    assert record["publication_workflow_run_id"] is None
    # Order 013-j, J5: the publication is bound to the workflow run's head;
    # order 014-c, workstream B.5: the head IS the exact image source
    # commit (one qualified source boundary).
    assert record["workflow_head_sha"] == source
    # Order 014-c, workstream B: the record's input map is EXACTLY the
    # source-ref map (not a later tree's), and the lock/base-image facts
    # are the source-ref facts.
    assert record["source_input_hashes"] == rc_mod.map_from_git_commit(repo, source)
    assert (
        record["dependency_lock_sha256"]
        == hashlib.sha256(
            subprocess.run(
                ["git", "-C", str(repo), "show", f"{source}:uv.lock"],
                capture_output=True,
                check=True,
            ).stdout
        ).hexdigest()
    )
    assert record["base_images"] == {
        stage: {"name": fact["name"], "digest": fact["digest"]}
        for stage, fact in generator._dockerfile_base_images_text(
            subprocess.run(
                ["git", "-C", str(repo), "show", f"{source}:Dockerfile"],
                capture_output=True,
                check=True,
            ).stdout.decode()
        ).items()
    }
    # Order 014-b, workstream B.3: the compatibility section is DERIVED
    # from the manifest-verified facts file.
    assert record["compatibility"] == COMPATIBILITY
    # A published RC must never imply a final release or a cutover.
    assert record["private_registry_auth_required"] is True
    assert record["final_public_release"] is False
    assert record["cutover_performed"] is False
    assert record["build_toolchain"] == {
        "backend": "hatchling==1.32.0",
        "uv": "0.12.5",
        "python": "3.12",
    }
    # Order 013-j, J5: the full pinned build environment and the
    # digest-pinned bases are carried directly (not cross-bound).
    assert record["build_environment"] == dict(generator.BUILD_ENVIRONMENT)
    assert record["base_images"] == _fixture_base_images(generator, repo)
    assert record["image_platform"] == "linux/amd64"


def test_build_rc_record_binds_manifest_lock_and_input_facts(
    rc_mod: types.ModuleType, repo: Path
) -> None:
    source = _source_sha(repo)
    record = rc_mod.build_rc_record(
        repo, source, DIGEST, source, PUBLISHED_AT, 42, QUALIFICATION_FACTS
    )
    assert record["wheel_sha256"] == WHEEL_SHA
    assert record["dependency_lock_sha256"] == _lock_sha()
    assert record["gateway_authority_sha"] == GATEWAY_SHA
    assert record["publication_workflow_run_id"] == 42
    # The DIRECT source-input hash map (config/compose/packaging/build
    # inputs) is carried in the record itself, equal to the source-ref
    # map, which equals the working tree at the derived child.
    assert record["source_input_hashes"] == rc_mod.map_from_git_commit(repo, source)
    assert record["source_input_hashes"] == rc_mod.map_from_directory(repo)


def test_build_rc_record_refuses_drifted_working_tree(rc_mod: types.ModuleType, repo: Path) -> None:
    # J4/014-c B: an ancestor relationship is NOT sufficient — the
    # checkout's inputs must equal the SOURCE-REF map. Alter one mapped
    # input in the tree.
    source = _source_sha(repo)
    (repo / "README.md").write_text("# altered\n", encoding="utf-8")
    with pytest.raises(rc_mod.RCRecordError, match="current checkout input map differs"):
        rc_mod.build_rc_record(
            repo, source, DIGEST, source, PUBLISHED_AT, None, QUALIFICATION_FACTS
        )


def test_build_rc_record_refuses_tampered_facts(rc_mod: types.ModuleType, repo: Path) -> None:
    # A BLOCKED overall verdict in the ledger facts cannot produce a record.
    source = _source_sha(repo)
    _rewrite_facts(repo, verdict="BLOCKED")
    with pytest.raises(rc_mod.RCRecordError, match="overall verdict"):
        rc_mod.build_rc_record(
            repo, source, DIGEST, source, PUBLISHED_AT, None, QUALIFICATION_FACTS
        )


@pytest.mark.parametrize("bad_source", ["a" * 39, "a" * 41, "g" * 40, "ABCDEF" * 7 + "ab"])
def test_build_rc_record_rejects_bad_source(
    rc_mod: types.ModuleType, repo: Path, bad_source: str
) -> None:
    source = _source_sha(repo)
    with pytest.raises(rc_mod.RCRecordError, match="40-hex"):
        rc_mod.build_rc_record(
            repo, bad_source, DIGEST, source, PUBLISHED_AT, None, QUALIFICATION_FACTS
        )


@pytest.mark.parametrize("bad_head", ["e" * 39, "e" * 41, "g" * 40, ""])
def test_build_rc_record_rejects_bad_head_sha(
    rc_mod: types.ModuleType, repo: Path, bad_head: str
) -> None:
    source = _source_sha(repo)
    with pytest.raises(rc_mod.RCRecordError, match="head_sha"):
        rc_mod.build_rc_record(
            repo, source, DIGEST, bad_head, PUBLISHED_AT, None, QUALIFICATION_FACTS
        )


# ---------------------------------------------------------------------------
# Order 014-c, workstream B: fail-closed source-ref binding (the RC4
# failure and its neighbor classes).
# ---------------------------------------------------------------------------


def test_build_rc_record_rejects_head_sha_not_source(rc_mod: types.ModuleType, repo: Path) -> None:
    # B.5: workflow_head_sha must be the EXACT supplied source ref.
    source = _source_sha(repo)
    with pytest.raises(rc_mod.RCRecordError, match="workflow head is not the exact"):
        rc_mod.build_rc_record(
            repo, source, DIGEST, "f" * 40, PUBLISHED_AT, None, QUALIFICATION_FACTS
        )


def test_build_rc_record_rejects_missing_source_ref(rc_mod: types.ModuleType, repo: Path) -> None:
    # B.1: the supplied source ref must exist in the repository.
    with pytest.raises(rc_mod.RCRecordError, match="does not exist"):
        rc_mod.build_rc_record(
            repo, "0" * 40, DIGEST, "0" * 40, PUBLISHED_AT, None, QUALIFICATION_FACTS
        )


def test_build_rc_record_rejects_non_ancestor_source_ref(
    rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path
) -> None:
    # B.2: a source ref on a LOST branch (valid-shaped, identical inputs,
    # identical wheel) is not the publication head and must fail.
    start_branch = _git(repo, "branch", "--show-current")
    base = _git(repo, "rev-parse", SOURCE_TAG + "^")
    # Lost branch: derived-only change from base => identical input map
    # and wheel, but NOT reachable from the current branch.
    _git(repo, "checkout", "-q", "-b", "lost", base)
    (repo / "oap").mkdir(exist_ok=True)
    (repo / "oap" / "active").write_text("lost\n", encoding="utf-8")
    lost = _commit(repo, "lost branch: derived metadata only")
    _git(repo, "checkout", "-q", start_branch)
    # The working-tree manifest records base (on the path to `lost`, with
    # the identical map) so only the reachability law can reject.
    (repo / "packaging" / "release_provenance_manifest.json").write_text(
        json.dumps(
            {
                "schema": "slaif-release-provenance-v5",
                "generated_from": {"git_commit": base},
                "artifacts": {"wheel": {"sha256": WHEEL_SHA}},
                "gateway_peer": {"commit": GATEWAY_SHA},
                "build": {"build_environment": dict(generator.BUILD_ENVIRONMENT)},
                "source_inputs": dict(rc_mod.map_from_git_commit(repo, base)),
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(rc_mod.RCRecordError, match="not reachable from the current checkout"):
        rc_mod.build_rc_record(repo, lost, DIGEST, lost, PUBLISHED_AT, None, QUALIFICATION_FACTS)


def test_build_rc_record_rejects_rc4_failure_later_tree_manifest(
    rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path
) -> None:
    """The exact RC4 failure (order 014-c): the committed manifest was
    regenerated from a LATER tree C whose mapped test file differs from
    the immutable image source S. The wheel hash and the product source
    (src/) are unchanged — a valid-shaped record must still be rejected
    because the source-ref map is not the recorded map."""
    source = _source_sha(repo)
    # C: a mapped test input changes after the source freeze.
    (repo / "tests" / "test_fixture.py").write_text(
        "def test_fixture():\n    assert True  # drifted after S\n", encoding="utf-8"
    )
    later = _commit(repo, "C: mapped test altered after source freeze")
    assert later != source
    # The committed (post-publication style) manifest is regenerated from
    # C: its recorded map equals C's map, NOT S's map; the wheel fact is
    # byte-identical (src/ untouched).
    (repo / "packaging" / "release_provenance_manifest.json").write_text(
        json.dumps(
            {
                "schema": "slaif-release-provenance-v5",
                "generated_from": {"git_commit": later},
                "artifacts": {"wheel": {"sha256": WHEEL_SHA}},
                "gateway_peer": {"commit": GATEWAY_SHA},
                "build": {"build_environment": dict(generator.BUILD_ENVIRONMENT)},
                "source_inputs": dict(rc_mod.map_from_git_commit(repo, later)),
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(rc_mod.RCRecordError, match="source-ref input map differs"):
        rc_mod.build_rc_record(
            repo, source, DIGEST, source, PUBLISHED_AT, None, QUALIFICATION_FACTS
        )


def test_build_rc_record_rejects_checkout_source_mismatch(
    rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path
) -> None:
    """The manifest records the source-ref map (honest pre-publication
    state), but a mapped input moved in a later commit: the checkout map
    no longer equals the source-ref map."""
    source = _source_sha(repo)
    (repo / "uv.lock").write_bytes(b"version = 1\n# drifted after S\n")
    _commit(repo, "C: dependency lock drifted after source freeze")
    with pytest.raises(rc_mod.RCRecordError, match="current checkout input map differs"):
        rc_mod.build_rc_record(
            repo, source, DIGEST, source, PUBLISHED_AT, None, QUALIFICATION_FACTS
        )


def test_build_rc_record_allows_derived_only_child(
    rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path
) -> None:
    """Allowed derived-only differences (record/handoff/manifest/OAP) in
    a later child do NOT break the source-ref binding: no mapped input
    moved, so the builder succeeds and carries the source-ref map."""
    source = _source_sha(repo)
    (repo / "packaging" / "rc_record.json").write_text(
        json.dumps({"schema": "slaif-rc-record-v3"}), encoding="utf-8"
    )
    (repo / "packaging" / "rc_handoff.md").write_text("# handoff\n", encoding="utf-8")
    (repo / "oap" / "active").write_text("014-c\n", encoding="utf-8")
    _commit(repo, "C: derived metadata only (record/handoff/oap)")
    record = rc_mod.build_rc_record(
        repo, source, DIGEST, source, PUBLISHED_AT, None, QUALIFICATION_FACTS
    )
    assert record["source_input_hashes"] == rc_mod.map_from_git_commit(repo, source)


def test_build_rc_record_binds_lock_to_source_ref_not_later_tree(
    rc_mod: types.ModuleType, repo_lock_unmapped: Path
) -> None:
    """B.3: with the lock NOT a mapped input, a later-tree lock drift is
    invisible to the input-map checks — the record's lock fact must still
    come from the SOURCE REF (git show <source>:uv.lock)."""
    source = _source_sha(repo_lock_unmapped)
    source_lock_sha = hashlib.sha256(
        subprocess.run(
            ["git", "-C", str(repo_lock_unmapped), "show", f"{source}:uv.lock"],
            capture_output=True,
            check=True,
        ).stdout
    ).hexdigest()
    drifted_lock = b"version = 1\n# later-tree drift (unmapped)\n"
    (repo_lock_unmapped / "uv.lock").write_bytes(drifted_lock)
    _commit(repo_lock_unmapped, "C: unmapped lock drifted")
    record = rc_mod.build_rc_record(
        repo_lock_unmapped, source, DIGEST, source, PUBLISHED_AT, None, QUALIFICATION_FACTS
    )
    assert record["dependency_lock_sha256"] == source_lock_sha
    assert record["dependency_lock_sha256"] != hashlib.sha256(drifted_lock).hexdigest()


@pytest.mark.parametrize(
    "bad_digest",
    [
        "b" * 64,  # missing sha256: prefix
        "sha256:" + "b" * 63,  # short
        "sha256:" + "b" * 65,  # long
        "sha256:" + "g" * 64,  # non-hex
    ],
)
def test_build_rc_record_rejects_bad_digest(
    rc_mod: types.ModuleType, repo: Path, bad_digest: str
) -> None:
    with pytest.raises(rc_mod.RCRecordError, match="sha256"):
        source = _source_sha(repo)
        rc_mod.build_rc_record(
            repo, source, bad_digest, source, PUBLISHED_AT, None, QUALIFICATION_FACTS
        )


@pytest.mark.parametrize(
    "bad_at",
    ["20/09/2026 12:00", "2026-09-20T00:00:00", "2026-09-20T00:00:00+02:00", ""],
)
def test_build_rc_record_rejects_bad_published_at(
    rc_mod: types.ModuleType, repo: Path, bad_at: str
) -> None:
    source = _source_sha(repo)
    with pytest.raises(rc_mod.RCRecordError, match="RFC 3339"):
        rc_mod.build_rc_record(repo, source, DIGEST, source, bad_at, None, QUALIFICATION_FACTS)


@pytest.mark.parametrize("bad_run_id", [0, -1, True])
def test_build_rc_record_rejects_bad_run_id(
    rc_mod: types.ModuleType, repo: Path, bad_run_id: object
) -> None:
    with pytest.raises(rc_mod.RCRecordError, match="run_id"):
        source = _source_sha(repo)
        rc_mod.build_rc_record(
            repo, source, DIGEST, source, PUBLISHED_AT, bad_run_id, QUALIFICATION_FACTS
        )


def _mutate_missing_key(c: dict[str, object]) -> None:
    c.pop("client_version")


def _mutate_extra_key(c: dict[str, object]) -> None:
    c["extra"] = "x"


def _mutate_empty_client_version(c: dict[str, object]) -> None:
    c["client_version"] = "  "


def _mutate_short_client_sha(c: dict[str, object]) -> None:
    c["client_sha256"] = "3" * 63


def _mutate_nonhex_client_sha(c: dict[str, object]) -> None:
    c["client_sha256"] = "g" * 64


def _mutate_topology_drift(c: dict[str, object]) -> None:
    c["topology"] = "gateway-signed"


def _mutate_extra_arm(c: dict[str, object]) -> None:
    cast("dict[str, str]", c["arm_verdicts"])["vision2"] = "pass"


def _mutate_missing_arm(c: dict[str, object]) -> None:
    cast("dict[str, str]", c["arm_verdicts"]).pop("both")


def _mutate_bad_arm_verdict(c: dict[str, object]) -> None:
    cast("dict[str, str]", c["arm_verdicts"])["cache"] = "not_run"


def _mutate_bad_direct_control(c: dict[str, object]) -> None:
    c["direct_control"] = "maybe"


def _mutate_bad_evidence_path(c: dict[str, object]) -> None:
    c["evidence_path"] = "oap/evidence/other/002"


def _mutate_short_evidence_number(c: dict[str, object]) -> None:
    c["evidence_path"] = "oap/evidence/testing-ledger/02"


def _mutate_long_client_sha(c: dict[str, object]) -> None:
    c["client_sha256"] = "3" * 65


def test_validate_compatibility_still_closed(rc_mod: types.ModuleType) -> None:
    """The closed compatibility contract itself stays strict (defense in
    depth around the derivation)."""
    import copy as _copy

    base = _copy.deepcopy(COMPATIBILITY)
    assert rc_mod._validate_compatibility(base) == base
    cases: list[tuple[str, Callable[[dict[str, object]], None]]] = [
        ("missing_key", _mutate_missing_key),
        ("extra_key", _mutate_extra_key),
        ("empty_client_version", _mutate_empty_client_version),
        ("short_client_sha", _mutate_short_client_sha),
        ("nonhex_client_sha", _mutate_nonhex_client_sha),
        ("topology_drift", _mutate_topology_drift),
        ("extra_arm", _mutate_extra_arm),
        ("missing_arm", _mutate_missing_arm),
        ("bad_arm_verdict", _mutate_bad_arm_verdict),
        ("bad_direct_control", _mutate_bad_direct_control),
        ("bad_evidence_path", _mutate_bad_evidence_path),
        ("short_evidence_number", _mutate_short_evidence_number),
        ("long_client_sha", _mutate_long_client_sha),
    ]
    for case_id, mutate in cases:
        copy = _copy.deepcopy(COMPATIBILITY)
        mutate(copy)
        with pytest.raises(rc_mod.RCRecordError, match="compatibility"):
            rc_mod._validate_compatibility(copy), case_id


def test_render_handoff_is_deterministic_and_self_contained(
    rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path
) -> None:
    source = _source_sha(repo)
    record = rc_mod.build_rc_record(
        repo, source, DIGEST, source, PUBLISHED_AT, 42, QUALIFICATION_FACTS
    )
    first = rc_mod.render_handoff(record)
    second = rc_mod.render_handoff(record)
    assert first == second, "handoff rendering must be a pure function of the record"
    # Literal verified values are present verbatim.
    for literal in (
        source,
        DIGEST,
        "0.1.0-rc9",
        "linux/amd64",
        WHEEL_SHA,
        "RepoDigests",
        "read:packages",
        CLIENT_VERSION,
        CLIENT_SHA,
        "standalone-loopback-no-gateway",
        EVIDENCE_PATH,
        "rc-candidate-0.1.0-rc9; private; not final release",
    ):
        assert literal in first, f"handoff missing literal fact {literal!r}"
    # Order 013-l, L2: the already-present record facts are rendered.
    for literal in (
        "Build toolchain: backend `hatchling==1.32.0`, python `3.12`, uv `0.12.5`",
        f"- Base image (uv-provider): `{UV_IMAGE}`",
        f"- Base image (build): `{PYTHON_IMAGE}`",
        f"- Base image (runtime): `{PYTHON_IMAGE}`",
        f"https://github.com/ulfe-lmi/slaif-local-coding/blob/{source}/INSTALL.md",
    ):
        assert literal in first, f"handoff missing literal fact {literal!r}"
    # No OAP knowledge, no benchmark procedure, no image rebuild.
    assert "OAP" not in first
    assert "objective" not in first.lower()
    assert "benchmark" in first.lower()  # only the explicit "NOT a benchmark" denial
    assert "uv build" not in first


def test_render_handoff_emits_valid_docker_template_commands(
    rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path
) -> None:
    """Order 013-l, L2: the rendered retrieval commands must be LITERAL valid
    Docker Go-template invocations (the pre-fix renderer emitted quadruple
    braces in the plain RepoDigests format string, making the command
    invalid)."""
    source = _source_sha(repo)
    record = rc_mod.build_rc_record(
        repo, source, DIGEST, source, PUBLISHED_AT, 42, QUALIFICATION_FACTS
    )
    rendered = rc_mod.render_handoff(record)
    lines = rendered.splitlines()
    expected_repodigests = (
        'docker image inspect "ghcr.io/ulfe-lmi/slaif-local-coding:0.1.0-rc9" '
        "--format '{{range .RepoDigests}}{{.}}{{end}}'"
    )
    assert expected_repodigests in lines, (
        f"RepoDigests command not literally rendered; lines near match: "
        f"{[line for line in lines if 'RepoDigests' in line and 'format' in line]}"
    )
    expected_labels = (
        f"docker image inspect "
        f'"ghcr.io/ulfe-lmi/slaif-local-coding@{DIGEST}" '
        "--format '{{json .Config.Labels}}'"
    )
    assert expected_labels in lines, (
        f"label-inspect command not literally rendered; lines near match: "
        f"{[line for line in lines if 'Config.Labels' in line]}"
    )
    # No quadruple-brace artifact may survive anywhere in the handoff.
    assert "{{{{" not in rendered
    # Both template commands use exactly the two-brace Go form.
    assert rendered.count("--format '{{") == 2


def test_frozen_identity_law_record_and_handoff(rc_mod: types.ModuleType, repo: Path) -> None:
    source = _source_sha(repo)
    record = rc_mod.build_rc_record(
        repo, source, DIGEST, source, PUBLISHED_AT, None, QUALIFICATION_FACTS
    )
    emit = repo / "packaging" / "rc_record.json"
    handoff = repo / "packaging" / "rc_handoff.md"
    payload = json.dumps(record, indent=2, sort_keys=True) + "\n"
    rendered = rc_mod.render_handoff(record)
    assert rc_mod._emit_frozen(emit, payload, "RC record") == "written"
    assert rc_mod._emit_frozen(handoff, rendered, "RC handoff") == "written"
    frozen_record = emit.read_bytes()
    frozen_handoff = handoff.read_bytes()
    # Identical rebuilds are accepted no-ops (safe retry law).
    assert rc_mod._emit_frozen(emit, payload, "RC record") == "unchanged"
    assert rc_mod._emit_frozen(handoff, rendered, "RC handoff") == "unchanged"
    # A different frozen identity (a different valid record: another
    # publishing run id) is refused, and the file stays intact.
    other = rc_mod.build_rc_record(
        repo, source, DIGEST, source, PUBLISHED_AT, 99, QUALIFICATION_FACTS
    )
    with pytest.raises(rc_mod.RCRecordError, match="frozen RC record"):
        rc_mod._emit_frozen(emit, json.dumps(other, indent=2, sort_keys=True) + "\n", "RC record")
    with pytest.raises(rc_mod.RCRecordError, match="frozen RC handoff"):
        rc_mod._emit_frozen(handoff, rc_mod.render_handoff(other), "RC handoff")
    assert emit.read_bytes() == frozen_record
    assert handoff.read_bytes() == frozen_handoff


def test_roundtrips_through_strict_loader(
    rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path
) -> None:
    source = _source_sha(repo)
    record = rc_mod.build_rc_record(
        repo, source, DIGEST, source, PUBLISHED_AT, 7, QUALIFICATION_FACTS
    )
    emit = repo / "packaging" / "rc_record.json"
    rc_mod._emit_frozen(emit, json.dumps(record, indent=2, sort_keys=True) + "\n", "RC record")
    # The frozen record must satisfy the provenance generator's closed-key
    # strict loader (24-key v3).
    assert generator.load_rc_record(repo) == record


def test_no_fake_digest_mode(rc_mod: types.ModuleType) -> None:
    # Order 013-i, C12 + order 013-j, J5: there is no mode that records an
    # unpublished image as published; the builder requires a well-formed
    # verified digest AND the workflow run's head SHA, and the
    # compatibility facts arrive ONLY as the manifest-verified facts file
    # (order 014-b, workstream B.3).
    params = inspect.signature(rc_mod.build_rc_record).parameters
    assert set(params) == {
        "repo",
        "source",
        "digest",
        "head_sha",
        "published_at",
        "run_id",
        "qualification_facts",
    }


# ---------------------------------------------------------------------------
# Order 014-b, workstream B.2: companion JSON Schema / record consistency
# ---------------------------------------------------------------------------


def _check_companion_node(node: object, value: object, defs: dict[str, object], path: str) -> None:
    """Minimal structural check of the companion schema's used subset
    (const, enum, type, pattern, minItems/maxItems, additionalProperties,
    required, properties, items, $ref into $defs) — no new dependency."""
    if isinstance(node, list):
        for option in node:
            try:
                _check_companion_node(option, value, defs, path)
                return
            except AssertionError:
                continue
        raise AssertionError(f"{path}: no type branch matches")
    if not isinstance(node, dict):
        return
    if "$ref" in node:
        name = str(node["$ref"]).rsplit("/", 1)[-1]
        _check_companion_node(defs[name], value, defs, path)
        return
    if "const" in node:
        assert value == node["const"], f"{path}: const {node['const']!r} != {value!r}"
    if "enum" in node:
        assert value in node["enum"], f"{path}: {value!r} not in enum"
    types_allowed = node.get("type")
    if types_allowed is not None:
        allowed = {types_allowed} if isinstance(types_allowed, str) else set(types_allowed)
        ok = False
        if "null" in allowed and value is None:
            ok = True
        if "boolean" in allowed and isinstance(value, bool):
            ok = True
        if "integer" in allowed and isinstance(value, int) and not isinstance(value, bool):
            ok = True
        if "number" in allowed and isinstance(value, (int, float)) and not isinstance(value, bool):
            ok = True
        if "string" in allowed and isinstance(value, str):
            ok = True
        if "array" in allowed and isinstance(value, list):
            ok = True
        if "object" in allowed and isinstance(value, dict):
            ok = True
        assert ok, f"{path}: value type not in {sorted(allowed)}"
    if isinstance(value, str) and "pattern" in node:
        assert re.search(str(node["pattern"]), value), f"{path}: pattern {node['pattern']!r}"
    if isinstance(value, list):
        if "minItems" in node:
            assert len(value) >= int(node["minItems"]), f"{path}: minItems"
        if "maxItems" in node:
            assert len(value) <= int(node["maxItems"]), f"{path}: maxItems"
        if "items" in node:
            for index, item in enumerate(value):
                _check_companion_node(node["items"], item, defs, f"{path}[{index}]")
    if isinstance(value, dict):
        for key in node.get("required", []):
            assert key in value, f"{path}: missing required {key!r}"
        props = node.get("properties", {})
        additional = node.get("additionalProperties", True)
        for key, item in value.items():
            if key in props:
                _check_companion_node(props[key], item, defs, f"{path}.{key}")
            elif additional is False:
                raise AssertionError(f"{path}: unexpected key {key!r}")
            elif isinstance(additional, dict):
                _check_companion_node(additional, item, defs, f"{path}.{key}")


def test_companion_schema_identity_is_self_consistent(rc_mod: types.ModuleType) -> None:
    """The advertised schema identity, the generator's emitted identity, and
    the current candidate identity must all agree (order 014-b, B.1/B.2:
    the 014-a defect was $id=v3 with properties.schema.const=v2)."""
    schema = json.loads(COMPANION_SCHEMA.read_text(encoding="utf-8"))
    assert schema["$id"] == schema["properties"]["schema"]["const"]
    assert schema["properties"]["schema"]["const"] == rc_mod.RC_RECORD_SCHEMA
    assert schema["properties"]["rc_identifier"]["const"] == rc_mod.RC_IDENTIFIER
    compat = schema["properties"]["compatibility"]["properties"]
    assert compat["direct_control"]["enum"] == list(rc_mod.DIRECT_CONTROL_VERDICTS)
    for arm in ("vision", "cache", "both"):
        assert compat["arm_verdicts"]["properties"][arm]["enum"] == list(
            rc_mod.COMPATIBILITY_ARM_VERDICTS
        )
    assert compat["topology"]["const"] == rc_mod.COMPATIBILITY_TOPOLOGY
    assert compat["evidence_path"]["pattern"] == rc_mod.EVIDENCE_PATH_PATTERN.pattern
    # Closed-object contract: the required key sets are exactly the
    # property key sets for the record and the compatibility section.
    assert set(schema["required"]) == set(schema["properties"])
    assert set(schema["properties"]["compatibility"]["required"]) == set(
        schema["properties"]["compatibility"]["properties"]
    )


def test_companion_schema_validates_current_record_if_present(
    rc_mod: types.ModuleType,
) -> None:
    """When a current RC record exists in the repository it must validate
    against the companion schema's closed contract (order 014-b, B.2). At
    the pre-publication freeze state the record is absent by design; the
    self-consistency assertions above are the always-run core."""
    schema = json.loads(COMPANION_SCHEMA.read_text(encoding="utf-8"))
    if not REPO_RECORD.is_file():
        pytest.skip("no current rc_record.json at this state (pre-publication)")
    record = json.loads(REPO_RECORD.read_text(encoding="utf-8"))
    _check_companion_node(schema, record, schema.get("$defs", {}), "record")


def test_render_handoff_renders_compatibility_facts(rc_mod: types.ModuleType, repo: Path) -> None:
    # Order 014-b: the deterministic handoff carries the literal qualified
    # client identity, the no-Gateway topology, closed arm verdicts, the
    # contextual DIRECT control, and the sanitized evidence path — all
    # derived from the manifest-verified facts.
    source = _source_sha(repo)
    record = rc_mod.build_rc_record(
        repo, source, DIGEST, source, PUBLISHED_AT, None, QUALIFICATION_FACTS
    )
    rendered = rc_mod.render_handoff(record)
    for literal in (
        f"Codex CLI `{CLIENT_VERSION}`",
        f"binary SHA-256 `{CLIENT_SHA}`",
        "standalone-loopback-no-gateway",
        "NO SLAIF API Gateway",
        "VISION `pass`",
        "CACHE `pass`",
        "BOTH `pass`",
        "DIRECT control: `pass`",
        f"`{EVIDENCE_PATH}`",
        "No benchmark ran",
    ):
        assert literal in rendered, f"handoff missing compatibility literal {literal!r}"
