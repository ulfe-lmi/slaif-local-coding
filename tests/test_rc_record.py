"""Order 013-i, C12: RC artifact record generator/loader tests.

Covers the strict builder (``scripts/rc_artifact_record.build_rc_record``),
the frozen-identity emitter (``emit_rc_record``), and the round-trip through
the provenance generator's closed-key strict loader
(``release_provenance_manifest.load_rc_record``). Deterministic: temporary
repo fixtures, no network, no registry, no docker, no fake digest mode.
"""

from __future__ import annotations

import hashlib
import importlib.util
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
DIGEST = "sha256:" + "b" * 64
PUBLISHED_AT = "2026-09-20T00:00:00Z"
LOCK_CONTENT = b"version = 1\n# fixture lock\n"


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
def repo(tmp_path: Path) -> Path:
    (tmp_path / "packaging").mkdir()
    manifest = {
        "artifacts": {"wheel": {"sha256": WHEEL_SHA}},
        "gateway_peer": {"commit": GATEWAY_SHA},
    }
    (tmp_path / "packaging" / "release_provenance_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    (tmp_path / "uv.lock").write_bytes(LOCK_CONTENT)
    return tmp_path


def _lock_sha() -> str:
    return hashlib.sha256(LOCK_CONTENT).hexdigest()


def test_build_rc_record_happy_path(rc_mod: types.ModuleType, repo: Path) -> None:
    record = rc_mod.build_rc_record(repo, SOURCE, DIGEST, PUBLISHED_AT, None)
    assert set(record) == {
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
        "private_registry_auth_required",
        "final_public_release",
        "cutover_performed",
        "wheel_sha256",
        "dependency_lock_sha256",
        "gateway_authority_sha",
        "build_toolchain",
        "deployment_assumptions",
    }
    assert record["schema"] == "slaif-rc-record-v1"
    assert record["rc_identifier"] == "0.1.0-rc1"
    assert record["product_version"] == "0.1.0"
    assert record["image_source_commit"] == SOURCE
    assert record["oci_image_reference"] == "ghcr.io/ulfe-lmi/slaif-local-coding"
    assert record["oci_image_digest"] == DIGEST
    assert record["oci_tags"] == ["0.1.0-rc1", f"sha-{SOURCE}"]
    assert record["published_at"] == PUBLISHED_AT
    assert record["publication_workflow"] == "release-image.yml"
    assert record["publication_workflow_run_id"] is None
    # A published RC must never imply a final release or a cutover.
    assert record["private_registry_auth_required"] is True
    assert record["final_public_release"] is False
    assert record["cutover_performed"] is False
    assert record["build_toolchain"] == {
        "backend": "hatchling==1.32.0",
        "uv": "0.12.5",
        "python": "3.12",
    }


def test_build_rc_record_binds_manifest_and_lock_facts(
    rc_mod: types.ModuleType, repo: Path
) -> None:
    record = rc_mod.build_rc_record(repo, SOURCE, DIGEST, PUBLISHED_AT, 42)
    assert record["wheel_sha256"] == WHEEL_SHA
    assert record["dependency_lock_sha256"] == _lock_sha()
    assert record["gateway_authority_sha"] == GATEWAY_SHA
    assert record["publication_workflow_run_id"] == 42


@pytest.mark.parametrize("bad_source", ["a" * 39, "a" * 41, "g" * 40, "ABCDEF" * 7 + "ab"])
def test_build_rc_record_rejects_bad_source(
    rc_mod: types.ModuleType, repo: Path, bad_source: str
) -> None:
    with pytest.raises(rc_mod.RCRecordError, match="40-hex"):
        rc_mod.build_rc_record(repo, bad_source, DIGEST, PUBLISHED_AT, None)


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
        rc_mod.build_rc_record(repo, SOURCE, bad_digest, PUBLISHED_AT, None)


@pytest.mark.parametrize(
    "bad_at",
    ["20/09/2026 12:00", "2026-09-20T00:00:00", "2026-09-20T00:00:00+02:00", ""],
)
def test_build_rc_record_rejects_bad_published_at(
    rc_mod: types.ModuleType, repo: Path, bad_at: str
) -> None:
    with pytest.raises(rc_mod.RCRecordError, match="RFC 3339"):
        rc_mod.build_rc_record(repo, SOURCE, DIGEST, bad_at, None)


@pytest.mark.parametrize("bad_run_id", [0, -1, True])
def test_build_rc_record_rejects_bad_run_id(
    rc_mod: types.ModuleType, repo: Path, bad_run_id: object
) -> None:
    with pytest.raises(rc_mod.RCRecordError, match="run_id"):
        rc_mod.build_rc_record(repo, SOURCE, DIGEST, PUBLISHED_AT, bad_run_id)


def test_emit_rc_record_roundtrips_through_strict_loader(
    rc_mod: types.ModuleType, generator: types.ModuleType, repo: Path
) -> None:
    record = rc_mod.build_rc_record(repo, SOURCE, DIGEST, PUBLISHED_AT, 7)
    emit = repo / "packaging" / "rc_record.json"
    assert rc_mod.emit_rc_record(repo, emit, record) == "written"
    payload = emit.read_text(encoding="utf-8")
    assert payload == json.dumps(record, indent=2, sort_keys=True) + "\n"
    # The frozen record must satisfy the provenance generator's closed-key
    # strict loader.
    assert generator.load_rc_record(repo) == record


def test_emit_rc_record_refuses_non_identical_overwrite(
    rc_mod: types.ModuleType, repo: Path
) -> None:
    emit = repo / "packaging" / "rc_record.json"
    record_a = rc_mod.build_rc_record(repo, SOURCE, DIGEST, PUBLISHED_AT, None)
    rc_mod.emit_rc_record(repo, emit, record_a)
    frozen_bytes = emit.read_bytes()
    # Identical rebuild is an accepted no-op (safe retry law).
    record_again = rc_mod.build_rc_record(repo, SOURCE, DIGEST, PUBLISHED_AT, None)
    assert rc_mod.emit_rc_record(repo, emit, record_again) == "unchanged"
    assert emit.read_bytes() == frozen_bytes
    # A different frozen identity is refused, and the file stays intact.
    other_source = "1" * 40
    record_b = rc_mod.build_rc_record(repo, other_source, DIGEST, PUBLISHED_AT, None)
    with pytest.raises(rc_mod.RCRecordError, match="frozen RC record"):
        rc_mod.emit_rc_record(repo, emit, record_b)
    assert emit.read_bytes() == frozen_bytes


def test_no_fake_digest_mode(rc_mod: types.ModuleType) -> None:
    # Order 013-i, C12: there is no mode that records an unpublished image
    # as published; the builder requires a well-formed verified digest.
    builder_params = __import__("inspect").signature(rc_mod.build_rc_record).parameters
    assert set(builder_params) == {"repo", "source", "digest", "published_at", "run_id"}
