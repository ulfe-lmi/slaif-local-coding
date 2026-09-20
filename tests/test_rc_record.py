"""Order 013-i, C12 (completed by order 013-j, J5): RC artifact record
generator, handoff renderer, and strict loader tests.

Covers the strict builder (``scripts/rc_artifact_record.build_rc_record`` —
slaif-rc-record-v2: the direct source-input hash map, build-environment
pins, base-image identities, supported platform, and the publishing
workflow run's head SHA), the deterministic handoff renderer
(``render_handoff``), the frozen-identity emitters
(``_emit_frozen``), and the round-trip through the provenance generator's
closed-key strict loader (``release_provenance_manifest.load_rc_record``).
Deterministic: temporary repo fixtures, no network, no registry, no docker,
no fake digest mode.
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RC_SCRIPT = REPO_ROOT / "scripts" / "rc_artifact_record.py"
GENERATOR = REPO_ROOT / "scripts" / "release_provenance_manifest.py"

WHEEL_SHA = "d" * 64
GATEWAY_SHA = "f" * 40
SOURCE = "a" * 40
HEAD_SHA = "e" * 40
DIGEST = "sha256:" + "b" * 64
PUBLISHED_AT = "2026-09-20T00:00:00Z"
LOCK_CONTENT = b"version = 1\n# fixture lock\n"
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
# determined inside the fixture (no real build backend required).
FIXTURE_PYPROJECT = (
    "[project]\n"
    'name = "fixture"\n'
    'version = "0.1.0"\n'
    "\n"
    "[tool.hatch.build]\n"
    "exclude = []\n"
    "\n"
    "[tool.hatch.build.targets.sdist]\n"
    'include = ["pyproject.toml", "README.md", "LICENSE", "uv.lock", "Dockerfile"]\n'
)

V2_KEYS = {
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


@pytest.fixture()
def repo(rc_mod: types.ModuleType, generator: types.ModuleType, tmp_path: Path) -> Path:
    (tmp_path / "packaging").mkdir()
    (tmp_path / "pyproject.toml").write_text(FIXTURE_PYPROJECT, encoding="utf-8")
    (tmp_path / "README.md").write_text("# fixture\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("Apache-2.0\n", encoding="utf-8")
    (tmp_path / "uv.lock").write_bytes(LOCK_CONTENT)
    (tmp_path / "Dockerfile").write_text(FIXTURE_DOCKERFILE, encoding="utf-8")
    # The manifest must record the working tree's exact input map (J4 law:
    # the record is built only where the inputs equal the recorded map).
    input_map = rc_mod.map_from_directory(tmp_path)
    manifest = {
        "schema": "slaif-release-provenance-v5",
        "artifacts": {"wheel": {"sha256": WHEEL_SHA}},
        "gateway_peer": {"commit": GATEWAY_SHA},
        "build": {"build_environment": dict(generator.BUILD_ENVIRONMENT)},
        "source_inputs": dict(input_map),
    }
    (tmp_path / "packaging" / "release_provenance_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    return tmp_path


def _lock_sha() -> str:
    return hashlib.sha256(LOCK_CONTENT).hexdigest()


def _fixture_base_images(generator: types.ModuleType, repo: Path) -> dict[str, dict[str, str]]:
    return {
        stage: {"name": fact["name"], "digest": fact["digest"]}
        for stage, fact in generator._dockerfile_base_images(repo).items()
    }


def test_build_rc_record_happy_path(
    rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path
) -> None:
    record = rc_mod.build_rc_record(repo, SOURCE, DIGEST, HEAD_SHA, PUBLISHED_AT, None)
    assert set(record) == V2_KEYS
    assert record["schema"] == "slaif-rc-record-v2"
    assert record["rc_identifier"] == "0.1.0-rc1"
    assert record["product_version"] == "0.1.0"
    assert record["image_source_commit"] == SOURCE
    assert record["oci_image_reference"] == "ghcr.io/ulfe-lmi/slaif-local-coding"
    assert record["oci_image_digest"] == DIGEST
    assert record["oci_tags"] == ["0.1.0-rc1", f"sha-{SOURCE}"]
    assert record["published_at"] == PUBLISHED_AT
    assert record["publication_workflow"] == "release-image.yml"
    assert record["publication_workflow_run_id"] is None
    # Order 013-j, J5: the publication is bound to the workflow run's head.
    assert record["workflow_head_sha"] == HEAD_SHA
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
    record = rc_mod.build_rc_record(repo, SOURCE, DIGEST, HEAD_SHA, PUBLISHED_AT, 42)
    assert record["wheel_sha256"] == WHEEL_SHA
    assert record["dependency_lock_sha256"] == _lock_sha()
    assert record["gateway_authority_sha"] == GATEWAY_SHA
    assert record["publication_workflow_run_id"] == 42
    # The DIRECT source-input hash map (config/compose/packaging/build
    # inputs) is carried in the record itself, equal to the working tree.
    assert record["source_input_hashes"] == rc_mod.map_from_directory(repo)


def test_build_rc_record_refuses_drifted_working_tree(rc_mod: types.ModuleType, repo: Path) -> None:
    # J4: an ancestor relationship is NOT sufficient — the working tree's
    # inputs must equal the recorded map. Alter one input.
    (repo / "README.md").write_text("# altered\n", encoding="utf-8")
    with pytest.raises(rc_mod.RCRecordError, match="source inputs differ"):
        rc_mod.build_rc_record(repo, SOURCE, DIGEST, HEAD_SHA, PUBLISHED_AT, None)


@pytest.mark.parametrize("bad_source", ["a" * 39, "a" * 41, "g" * 40, "ABCDEF" * 7 + "ab"])
def test_build_rc_record_rejects_bad_source(
    rc_mod: types.ModuleType, repo: Path, bad_source: str
) -> None:
    with pytest.raises(rc_mod.RCRecordError, match="40-hex"):
        rc_mod.build_rc_record(repo, bad_source, DIGEST, HEAD_SHA, PUBLISHED_AT, None)


@pytest.mark.parametrize("bad_head", ["e" * 39, "e" * 41, "g" * 40, ""])
def test_build_rc_record_rejects_bad_head_sha(
    rc_mod: types.ModuleType, repo: Path, bad_head: str
) -> None:
    with pytest.raises(rc_mod.RCRecordError, match="head_sha"):
        rc_mod.build_rc_record(repo, SOURCE, DIGEST, bad_head, PUBLISHED_AT, None)


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
        rc_mod.build_rc_record(repo, SOURCE, bad_digest, HEAD_SHA, PUBLISHED_AT, None)


@pytest.mark.parametrize(
    "bad_at",
    ["20/09/2026 12:00", "2026-09-20T00:00:00", "2026-09-20T00:00:00+02:00", ""],
)
def test_build_rc_record_rejects_bad_published_at(
    rc_mod: types.ModuleType, repo: Path, bad_at: str
) -> None:
    with pytest.raises(rc_mod.RCRecordError, match="RFC 3339"):
        rc_mod.build_rc_record(repo, SOURCE, DIGEST, HEAD_SHA, bad_at, None)


@pytest.mark.parametrize("bad_run_id", [0, -1, True])
def test_build_rc_record_rejects_bad_run_id(
    rc_mod: types.ModuleType, repo: Path, bad_run_id: object
) -> None:
    with pytest.raises(rc_mod.RCRecordError, match="run_id"):
        rc_mod.build_rc_record(repo, SOURCE, DIGEST, HEAD_SHA, PUBLISHED_AT, bad_run_id)


def test_render_handoff_is_deterministic_and_self_contained(
    rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path
) -> None:
    record = rc_mod.build_rc_record(repo, SOURCE, DIGEST, HEAD_SHA, PUBLISHED_AT, 42)
    first = rc_mod.render_handoff(record)
    second = rc_mod.render_handoff(record)
    assert first == second, "handoff rendering must be a pure function of the record"
    # Literal verified values are present verbatim.
    for literal in (
        SOURCE,
        DIGEST,
        HEAD_SHA,
        "0.1.0-rc1",
        "linux/amd64",
        WHEEL_SHA,
        "RepoDigests",
        "read:packages",
    ):
        assert literal in first, f"handoff missing literal fact {literal!r}"
    # No OAP knowledge, no benchmark procedure, no image rebuild.
    assert "OAP" not in first
    assert "objective" not in first.lower()
    assert "benchmark" in first.lower()  # only the explicit "NOT a benchmark" denial
    assert "uv build" not in first


def test_frozen_identity_law_record_and_handoff(rc_mod: types.ModuleType, repo: Path) -> None:
    record = rc_mod.build_rc_record(repo, SOURCE, DIGEST, HEAD_SHA, PUBLISHED_AT, None)
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
    # A different frozen identity is refused, and the file stays intact.
    other = rc_mod.build_rc_record(repo, "1" * 40, DIGEST, HEAD_SHA, PUBLISHED_AT, None)
    with pytest.raises(rc_mod.RCRecordError, match="frozen RC record"):
        rc_mod._emit_frozen(emit, json.dumps(other, indent=2, sort_keys=True) + "\n", "RC record")
    with pytest.raises(rc_mod.RCRecordError, match="frozen RC handoff"):
        rc_mod._emit_frozen(handoff, rc_mod.render_handoff(other), "RC handoff")
    assert emit.read_bytes() == frozen_record
    assert handoff.read_bytes() == frozen_handoff


def test_roundtrips_through_strict_loader(
    rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path
) -> None:
    record = rc_mod.build_rc_record(repo, SOURCE, DIGEST, HEAD_SHA, PUBLISHED_AT, 7)
    emit = repo / "packaging" / "rc_record.json"
    rc_mod._emit_frozen(emit, json.dumps(record, indent=2, sort_keys=True) + "\n", "RC record")
    # The frozen record must satisfy the provenance generator's closed-key
    # strict loader (23-key v2).
    assert generator.load_rc_record(repo) == record


def test_no_fake_digest_mode(rc_mod: types.ModuleType) -> None:
    # Order 013-i, C12 + order 013-j, J5: there is no mode that records an
    # unpublished image as published; the builder requires a well-formed
    # verified digest AND the workflow run's head SHA.
    params = inspect.signature(rc_mod.build_rc_record).parameters
    assert set(params) == {"repo", "source", "digest", "head_sha", "published_at", "run_id"}
