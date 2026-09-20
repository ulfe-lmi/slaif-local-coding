"""Order 013-l, L1: consumer-integration coverage for the pulled-image
publication record gate (scripts/docker_qualification_ci.py).

The generator emits schema slaif-rc-record-v2; the published-mode loader and
the published-mode constructor of the real qualification orchestrator must
accept a GENERATED v2 record (a temporary fixture, never a fake record in
packaging/) through the existing strict v2 loader, and malformed data —
including the superseded slaif-rc-record-v1 key set — must be rejected. No
Docker, no network, no registry: loader/constructor only.

Fixtures and constants are reused from tests/test_rc_record.py.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import types
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.test_rc_record import (
    DIGEST,
    FIXTURE_DOCKERFILE,
    FIXTURE_PYPROJECT,
    GATEWAY_SHA,
    HEAD_SHA,
    LOCK_CONTENT,
    PUBLISHED_AT,
    SOURCE,
    WHEEL_SHA,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
QUAL_SCRIPT = REPO_ROOT / "scripts" / "docker_qualification_ci.py"
RC_SCRIPT = REPO_ROOT / "scripts" / "rc_artifact_record.py"
GENERATOR = REPO_ROOT / "scripts" / "release_provenance_manifest.py"


def _load_module(path: Path, name: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def dqc() -> types.ModuleType:
    return _load_module(QUAL_SCRIPT, "docker_qualification_ci_for_gate_tests")


@pytest.fixture(scope="module")
def rc_mod() -> types.ModuleType:
    return _load_module(RC_SCRIPT, "rc_artifact_record_for_gate_tests")


@pytest.fixture(scope="module")
def generator() -> types.ModuleType:
    return _load_module(GENERATOR, "release_provenance_manifest_for_gate_tests")


@pytest.fixture()
def repo(rc_mod: types.ModuleType, generator: types.ModuleType, tmp_path: Path) -> Path:
    """Temporary repository with a valid committed v5 manifest (reuses the
    test_rc_record fixture layout; no packaging/rc_record.json yet)."""
    (tmp_path / "packaging").mkdir()
    (tmp_path / "pyproject.toml").write_text(FIXTURE_PYPROJECT, encoding="utf-8")
    (tmp_path / "README.md").write_text("# fixture\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("Apache-2.0\n", encoding="utf-8")
    (tmp_path / "uv.lock").write_bytes(LOCK_CONTENT)
    (tmp_path / "Dockerfile").write_text(FIXTURE_DOCKERFILE, encoding="utf-8")
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


@pytest.fixture()
def wired(dqc: types.ModuleType, repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Point the real orchestrator at the temporary repository's records."""
    monkeypatch.setattr(dqc, "RC_RECORD", repo / "packaging" / "rc_record.json")
    monkeypatch.setattr(dqc, "RELEASE_RECORD", repo / "packaging" / "release_record.json")
    monkeypatch.setattr(dqc, "REPO_ROOT", repo)


def _write_record(path: Path, record: dict[str, object]) -> None:
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _final_record() -> dict[str, object]:
    return {
        "schema": "slaif-release-record-v1",
        "version": "0.1.0",
        "git_tag": "v0.1.0",
        "image_source_commit": SOURCE,
        "oci_image_reference": "ghcr.io/ulfe-lmi/slaif-local-coding",
        "oci_image_digest": DIGEST,
        "oci_tags": ["0.1.0", f"sha-{SOURCE}"],
        "published_at": PUBLISHED_AT,
        "publication_workflow": "release-image.yml",
        "publication_workflow_run_id": 7,
    }


def test_generated_v2_record_accepted_by_real_published_mode_loader(
    dqc: types.ModuleType,
    rc_mod: types.ModuleType,
    repo: Path,
    wired: None,
) -> None:
    """A generated v2 temporary fixture is accepted by the real published-mode
    loader (the existing strict v2 loader — not a second schema
    implementation)."""
    record = rc_mod.build_rc_record(repo, SOURCE, DIGEST, HEAD_SHA, PUBLISHED_AT, 42)
    _write_record(repo / "packaging" / "rc_record.json", record)
    assert dqc._load_publication_record() == record


def test_published_mode_constructor_consumes_v2_record(
    dqc: types.ModuleType,
    rc_mod: types.ModuleType,
    repo: Path,
    wired: None,
) -> None:
    """The real published-mode constructor binds the pulled image reference
    and source commit from the generated v2 record."""
    record = rc_mod.build_rc_record(repo, SOURCE, DIGEST, HEAD_SHA, PUBLISHED_AT, None)
    _write_record(repo / "packaging" / "rc_record.json", record)
    args = argparse.Namespace(
        published=True,
        image=None,
        wheel_sha256=WHEEL_SHA,
        tag_sha=None,
        full_sha=None,
        adapter_port=18031,
        fake_port=18033,
        failclosed_port=18034,
    )
    qual = dqc.Qualification(args)
    assert qual.mode == "published"
    assert qual.record == record
    assert qual.source_commit == SOURCE
    assert qual.image_ref == f"{record['oci_image_reference']}@{record['oci_image_digest']}"
    assert qual.compose_files == (dqc.COMPOSE_PRIMARY,)


def test_record_missing_when_no_publication_record(
    dqc: types.ModuleType, repo: Path, wired: None
) -> None:
    with pytest.raises(dqc.QualificationError) as exc:
        dqc._load_publication_record()
    assert (exc.value.phase, exc.value.code) == ("release_record", "record_missing")


@pytest.mark.parametrize(
    "mutate",
    [
        lambda rec: rec.update(final_public_release=True),
        lambda rec: rec.update(cutover_performed=True),
        lambda rec: rec.update(private_registry_auth_required=False),
        lambda rec: rec.update(oci_image_digest="sha256:" + "b" * 63),
        lambda rec: rec.update(oci_tags=["0.1.0-rc2", "wrong-tag"]),
        lambda rec: rec.update(image_source_commit="a" * 39),
        lambda rec: rec.update(workflow_head_sha="g" * 40),
        lambda rec: rec.update(wheel_sha256="d" * 64 + "d"),
        lambda rec: rec.__setitem__("extra_key", "drift"),
        lambda rec: rec.update(schema="slaif-rc-record-v3"),
    ],
    ids=[
        "final_release_true",
        "cutover_true",
        "private_auth_false",
        "short_digest",
        "tag_drift",
        "short_source",
        "bad_head_sha",
        "long_wheel",
        "extra_key",
        "wrong_schema",
    ],
)
def test_malformed_v2_record_rejected(
    dqc: types.ModuleType,
    rc_mod: types.ModuleType,
    repo: Path,
    wired: None,
    mutate: Callable[[dict[str, object]], None],
) -> None:
    """Malformed v2 data is a qualification failure, never a warning."""
    record = rc_mod.build_rc_record(repo, SOURCE, DIGEST, HEAD_SHA, PUBLISHED_AT, None)
    mutate(record)
    _write_record(repo / "packaging" / "rc_record.json", record)
    with pytest.raises(dqc.QualificationError) as exc:
        dqc._load_publication_record()
    assert (exc.value.phase, exc.value.code) == ("release_record", "record_invalid")


def test_superseded_v1_rc_record_rejected(dqc: types.ModuleType, repo: Path, wired: None) -> None:
    """The superseded slaif-rc-record-v1 key set is malformed for the gate
    (the generator emits v2; the strict v2 loader is the only RC schema)."""
    v1: dict[str, object] = {
        "schema": "slaif-rc-record-v1",
        "rc_identifier": "0.1.0-rc2",
        "product_version": "0.1.0",
        "image_source_commit": SOURCE,
        "oci_image_reference": "ghcr.io/ulfe-lmi/slaif-local-coding",
        "oci_image_digest": DIGEST,
        "oci_tags": ["0.1.0-rc2", f"sha-{SOURCE}"],
        "published_at": PUBLISHED_AT,
        "publication_workflow": "release-image.yml",
        "publication_workflow_run_id": None,
        "private_registry_auth_required": True,
        "final_public_release": False,
        "cutover_performed": False,
        "wheel_sha256": WHEEL_SHA,
        "build_toolchain": {"backend": "hatchling==1.32.0", "uv": "0.12.5", "python": "3.12"},
        "deployment_assumptions": "fixture",
    }
    _write_record(repo / "packaging" / "rc_record.json", v1)
    with pytest.raises(dqc.QualificationError) as exc:
        dqc._load_publication_record()
    assert (exc.value.phase, exc.value.code) == ("release_record", "record_invalid")


def test_rc_record_authoritative_when_both_exist(
    dqc: types.ModuleType,
    rc_mod: types.ModuleType,
    repo: Path,
    wired: None,
) -> None:
    record = rc_mod.build_rc_record(repo, SOURCE, DIGEST, HEAD_SHA, PUBLISHED_AT, None)
    _write_record(repo / "packaging" / "rc_record.json", record)
    _write_record(repo / "packaging" / "release_record.json", _final_record())
    assert dqc._load_publication_record() == record


def test_final_record_still_accepted_alone(dqc: types.ModuleType, repo: Path, wired: None) -> None:
    """RC/final distinction: without an RC record the final release record
    (slaif-release-record-v1) remains the validated path for the later
    separately authorized final release."""
    final = _final_record()
    _write_record(repo / "packaging" / "release_record.json", final)
    assert dqc._load_publication_record() == final


def test_final_record_malformed_rejected(dqc: types.ModuleType, repo: Path, wired: None) -> None:
    final = _final_record()
    final["oci_tags"] = ["0.1.0", "wrong-tag"]
    _write_record(repo / "packaging" / "release_record.json", final)
    with pytest.raises(dqc.QualificationError) as exc:
        dqc._load_publication_record()
    assert (exc.value.phase, exc.value.code) == ("release_record", "record_tags")
