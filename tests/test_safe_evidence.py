"""Synthetic-only regression tests for the Objective-008-a safe-evidence path.

Every fixture is built from :func:`contracts.materialize_sample` (synthetic
values drawn from the closed vocabularies of the committed source
contracts) or from hand-written bytes in this file.  The suite never reads
historical artifacts, opens a network socket, spawns a process, stages Git,
or calls any model/provider; those surfaces are actively guarded in
``test_export_performs_no_external_activity``.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import stat
import subprocess
import tomllib
from pathlib import Path
from typing import Any

import pytest

from tests.helpers import safe_evidence_contracts as contracts
from tests.helpers.safe_evidence import (
    MAX_SAFE_EVIDENCE_BYTES,
    DictSpec,
    ListSpec,
    OpenDictSpec,
    OpenValueSpec,
    ProvenanceRecord,
    StrSpec,
    UnionSpec,
    UnsafeEvidenceError,
    accept_evidence_bytes,
    atomic_write_bounded,
    export_safe_result,
    privacy_scan,
    read_existing_evidence_destination_bounded,
    remove_verified_evidence_destination,
    resolve_evidence_destination,
    safe_read_bounded,
    validate_value,
    verify_existing_evidence_destination,
)

# --------------------------------------------------------------------------
# Synthetic fixture builders
# --------------------------------------------------------------------------


def materialize_raw(role: str) -> bytes:
    """Deterministic JSONL bytes for one closed role (result + preflight)."""
    doc, preflight = contracts.materialize_sample(role)
    raw = b""
    if preflight is not None:
        raw += (json.dumps(preflight, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    raw += (json.dumps(doc, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    return raw


def raw_from(doc: dict[str, object], preflight: dict[str, object] | None) -> bytes:
    raw = b""
    if preflight is not None:
        raw += (json.dumps(preflight, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    raw += (json.dumps(doc, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    return raw


def swap_bytes(raw: bytes, needle: bytes, replacement: bytes) -> bytes:
    assert raw.count(needle) == 1, f"fixture drift: needle not unique: {needle!r}"
    return raw.replace(needle, replacement)


def export(
    repo_root: Path,
    role: str,
    relative_path: str,
    *,
    mode: str = "deterministic",
    raw: bytes | None = None,
) -> ProvenanceRecord:
    return export_safe_result(
        repo_root,
        role=role,
        schema=contracts.ROLE_SCHEMAS[role],
        raw=materialize_raw(role) if raw is None else raw,
        result_spec=contracts.result_spec_for_role(role),
        preflight_spec=contracts.preflight_spec_for_role(role),
        relative_path=relative_path,
        mode=mode,
    )


def destination(repo_root: Path, relative_path: str) -> Path:
    return repo_root / "oap" / "evidence" / relative_path


def current_fds() -> frozenset[int]:
    return frozenset(int(name) for name in os.listdir("/proc/self/fd"))


def all_files(root: Path) -> set[Path]:
    return {path for path in root.rglob("*") if path.is_file()}


def write_source(path: Path, data: bytes) -> None:
    path.write_bytes(data)
    os.chmod(path, 0o600)


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "oap" / "evidence").mkdir(parents=True)
    os.chmod(root / "oap", 0o700)
    os.chmod(root / "oap" / "evidence", 0o700)
    return root


# --------------------------------------------------------------------------
# Closed roles and deterministic synthetic materialization
# --------------------------------------------------------------------------


def test_role_schemas_are_closed_and_distinct() -> None:
    assert contracts.ROLES == frozenset(
        {"protected_target", "fake_target", "full_fake_gate", "manifest"}
    )
    assert contracts.ROLE_SCHEMAS == {
        "protected_target": contracts.TARGET_RESULT_SCHEMA_NAME,
        "fake_target": contracts.TARGET_RESULT_SCHEMA_NAME,
        "full_fake_gate": contracts.FULL_GATE_RESULT_SCHEMA_NAME,
        "manifest": contracts.MANIFEST_SCHEMA,
    }
    specs = {role: contracts.result_spec_for_role(role) for role in sorted(contracts.ROLES)}
    assert len({id(spec) for spec in specs.values()}) == len(specs)
    # Cross-rejection: a manifest document is not a target document and
    # vice versa; the schemas are explicit, not one arbitrary JSON mapping.
    manifest_doc, _ = contracts.materialize_sample("manifest")
    with pytest.raises(UnsafeEvidenceError):
        validate_value(specs["fake_target"], manifest_doc)
    fake_doc, _ = contracts.materialize_sample("fake_target")
    with pytest.raises(UnsafeEvidenceError):
        validate_value(specs["manifest"], fake_doc)
    # The AP37 full-gate family is a supported closed export role: the
    # exact full machine-gate document shape, no arbitrary JSON.
    gate_doc, gate_preflight = contracts.materialize_sample("full_fake_gate")
    with pytest.raises(UnsafeEvidenceError):
        validate_value(specs["manifest"], gate_doc)
    with pytest.raises(UnsafeEvidenceError):
        validate_value(specs["full_fake_gate"], fake_doc)
    assert gate_preflight is not None
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        contracts.result_spec_for_role("nope")
    assert exc_info.value.rejection_class == "role_unknown"
    with pytest.raises(UnsafeEvidenceError):
        contracts.preflight_spec_for_role("nope")
    assert contracts.preflight_spec_for_role("manifest") is None
    assert contracts.preflight_spec_for_role("full_fake_gate") is not None


def test_materialize_samples_are_deterministic_and_valid() -> None:
    for role in sorted(contracts.ROLES):
        first, first_preflight = contracts.materialize_sample(role)
        second, second_preflight = contracts.materialize_sample(role)
        assert first == second
        assert first_preflight == second_preflight
        raw = raw_from(first, first_preflight)
        document, sha256 = accept_evidence_bytes(
            raw,
            contracts.result_spec_for_role(role),
            preflight_spec=contracts.preflight_spec_for_role(role),
        )
        assert document == first
        assert sha256 == hashlib.sha256(raw).hexdigest()


# --------------------------------------------------------------------------
# Valid protected / fake / manifest materialization and export
# --------------------------------------------------------------------------


def test_export_protected_role_exact_mode(repo_root: Path) -> None:
    raw = materialize_raw("protected_target")
    prov = export(
        repo_root,
        "protected_target",
        "005-ar/protected-final-1024-success.json",
        mode="exact",
        raw=raw,
    )
    dest = destination(repo_root, "005-ar/protected-final-1024-success.json")
    data = dest.read_bytes()
    assert data == raw
    assert prov.role == "protected_target"
    assert prov.schema == contracts.TARGET_RESULT_SCHEMA_NAME
    assert prov.relative_path == "005-ar/protected-final-1024-success.json"
    assert prov.byte_count == len(data)
    assert prov.mode == "exact"
    assert prov.original_sha256 == hashlib.sha256(raw).hexdigest()
    assert prov.committed_sha256 == hashlib.sha256(data).hexdigest()
    assert prov.original_sha256 == prov.committed_sha256
    st = dest.stat()
    assert stat.S_IMODE(st.st_mode) == 0o600
    assert st.st_uid == os.getuid()


def test_export_fake_role_deterministic_mode(repo_root: Path) -> None:
    raw = materialize_raw("fake_target")
    prov = export(
        repo_root,
        "fake_target",
        "005-ar/fake-isolated-target.json",
        mode="deterministic",
        raw=raw,
    )
    doc, _ = contracts.materialize_sample("fake_target")
    expected = (json.dumps(doc, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    data = destination(repo_root, "005-ar/fake-isolated-target.json").read_bytes()
    assert data == expected
    assert prov.original_sha256 == hashlib.sha256(raw).hexdigest()
    assert prov.committed_sha256 == hashlib.sha256(expected).hexdigest()


def test_manifest_role_exports_without_preflight(repo_root: Path) -> None:
    raw = materialize_raw("manifest")
    assert b"PREFLIGHT" not in raw
    prov = export(
        repo_root,
        "manifest",
        "005-ar/manifest.json",
        mode="deterministic",
        raw=raw,
    )
    assert prov.schema == contracts.MANIFEST_SCHEMA
    data = destination(repo_root, "005-ar/manifest.json").read_bytes()
    assert prov.committed_sha256 == hashlib.sha256(data).hexdigest()


def test_export_bytes_and_hash_are_deterministic(repo_root: Path) -> None:
    raw = materialize_raw("protected_target")
    prov_a = export(repo_root, "protected_target", "005-ar/protected-final-success.json", raw=raw)
    prov_b = export(repo_root, "protected_target", "005-ar/protected-final-success-copy.json")
    data_a = destination(repo_root, "005-ar/protected-final-success.json").read_bytes()
    data_b = destination(repo_root, "005-ar/protected-final-success-copy.json").read_bytes()
    assert data_a == data_b
    assert prov_a.committed_sha256 == prov_b.committed_sha256
    assert prov_a.committed_sha256 == hashlib.sha256(data_a).hexdigest()
    assert prov_a.original_sha256 == prov_b.original_sha256
    assert prov_a.original_sha256 == hashlib.sha256(raw).hexdigest()


# --------------------------------------------------------------------------
# Fail-closed schema rejections (unknown / missing top-level and nested)
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mutate", "expected_class", "expected_path"),
    [
        (
            lambda doc: doc.update({"unexpected_top_level": {"nested": "x"}}),
            "shape_key_unknown",
            "<root>",
        ),
        (
            lambda doc: doc["candidate_provenance"].update({"injected": "x"}),
            "shape_key_unknown",
            "<root>.candidate_provenance",
        ),
        (
            lambda doc: doc.pop("phase_checkpoints"),
            "shape_key_missing",
            "<root>.phase_checkpoints",
        ),
        (
            lambda doc: doc["target_dispatch_counts"].pop("inference_attempted"),
            "shape_key_missing",
            "<root>.target_dispatch_counts.inference_attempted",
        ),
    ],
)
def test_unknown_and_missing_fields_are_rejected(
    repo_root: Path,
    mutate: Any,
    expected_class: str,
    expected_path: str,
) -> None:
    doc, preflight = contracts.materialize_sample("fake_target")
    mutate(doc)
    raw = raw_from(doc, preflight)
    spec = contracts.result_spec_for_role("fake_target")
    preflight_spec = contracts.preflight_spec_for_role("fake_target")
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        accept_evidence_bytes(raw, spec, preflight_spec=preflight_spec)
    assert exc_info.value.rejection_class == expected_class
    assert exc_info.value.path == expected_path
    # The export entry point fails closed as well and writes nothing.
    with pytest.raises(UnsafeEvidenceError):
        export(repo_root, "fake_target", "005-ar/never-written.json", raw=raw)
    assert not destination(repo_root, "005-ar/never-written.json").exists()
    assert all_files(repo_root) == set()


# --------------------------------------------------------------------------
# Privacy rejections: unsafe content is rejected, never stripped
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("needle", "replacement", "expected_class"),
    [
        # Bearer credential in an identifier-shaped slot.
        (
            b'"run_id":"' + b"0" * 32 + b'"',
            b'"run_id":"Bearer abcdef123456"',
            "privacy_pattern_bearer",
        ),
        # Raw image payload as a data URL.
        (
            b'"route_policy":"qwen38-vision-codex/retain_newest/signed_identity_v1"',
            b'"route_policy":"data:image/png;base64,QUJDREFG"',
            "privacy_pattern_data_url",
        ),
        # Historically-private loopback URL.
        (
            b'"codex_version":"0.149.0"',
            b'"codex_version":"http://10.8.132.76:18020/v1"',
            "privacy_pattern_private_url",
        ),
        # Raw body / model-output blob: a long base64-style payload in a
        # provenance slot.
        (
            b'"harness_source":"scripts/gateway_accounting_rehearsal.py"',
            b'"harness_source":"' + b"A" * 320 + b'"',
            "privacy_pattern_long_base64",
        ),
    ],
)
def test_unsafe_content_is_rejected_not_stripped(
    repo_root: Path,
    needle: bytes,
    replacement: bytes,
    expected_class: str,
) -> None:
    raw = swap_bytes(materialize_raw("fake_target"), needle, replacement)
    spec = contracts.result_spec_for_role("fake_target")
    preflight_spec = contracts.preflight_spec_for_role("fake_target")
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        accept_evidence_bytes(raw, spec, preflight_spec=preflight_spec)
    assert exc_info.value.rejection_class == expected_class
    with pytest.raises(UnsafeEvidenceError):
        export(repo_root, "fake_target", "005-ar/unsafe.json", raw=raw)
    assert all_files(repo_root) == set()


@pytest.mark.parametrize(
    ("key", "value", "expected_class"),
    [
        ("api_key", "sk-abcdef1234567890abcd", "privacy_pattern_api_key_prefix"),
        ("service_token", "abcdef1234567890", "privacy_pattern_secret_field"),
        ("authorization", "abcdef123456", "privacy_pattern_authorization"),
        ("signature", "abcdef1234567890ab", "privacy_pattern_signature_nonce"),
        ("nonce", "abcdef1234567890ab", "privacy_pattern_signature_nonce"),
    ],
)
def test_credentials_signature_and_nonce_are_rejected(
    repo_root: Path,
    key: str,
    value: str,
    expected_class: str,
) -> None:
    doc, preflight = contracts.materialize_sample("fake_target")
    doc[key] = value
    raw = raw_from(doc, preflight)
    spec = contracts.result_spec_for_role("fake_target")
    preflight_spec = contracts.preflight_spec_for_role("fake_target")
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        accept_evidence_bytes(raw, spec, preflight_spec=preflight_spec)
    assert exc_info.value.rejection_class == expected_class
    with pytest.raises(UnsafeEvidenceError):
        export(repo_root, "fake_target", "005-ar/cred.json", raw=raw)
    assert all_files(repo_root) == set()


def test_privacy_scan_classes_cover_required_patterns() -> None:
    assert privacy_scan(b'{"ok": true}') is None
    assert privacy_scan(b"Bearer abcdef1234") == "privacy_pattern_bearer"
    assert (
        privacy_scan(b'"api_key":"sk-abcdef1234567890abcdef"') == "privacy_pattern_api_key_prefix"
    )
    assert privacy_scan(b'"gateway_key": "abcdef123456"') == "privacy_pattern_secret_field"
    assert privacy_scan(b"data:image/jpeg;base64,AAA") == "privacy_pattern_data_url"
    assert privacy_scan(b"ftp://192.168.1.9/data") == "privacy_pattern_private_url"
    assert privacy_scan(b"172.16.0.5:18020") == "privacy_pattern_private_ip"
    assert privacy_scan(b"A" * 320) == "privacy_pattern_long_base64"
    assert privacy_scan(b'"hmac":"abcdef1234567890"') == "privacy_pattern_signature_nonce"


# --------------------------------------------------------------------------
# Destination resolution: traversal, component, and symlink rejections
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("relative_path", "expected_class"),
    [
        ("", "destination_empty"),
        ("/abs.json", "destination_absolute"),
        ("../escape.json", "destination_traversal"),
        ("a/../../escape.json", "destination_traversal"),
        ("a/b/../c.json", "destination_traversal"),
        ("a b.json", "destination_component_name"),
        ("a/b/c/d/e/f/g.json", "destination_component_count"),
    ],
)
def test_traversal_and_component_rejections(
    repo_root: Path, relative_path: str, expected_class: str
) -> None:
    before = all_files(repo_root)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        resolve_evidence_destination(repo_root, relative_path)
    assert exc_info.value.rejection_class == expected_class
    with pytest.raises(UnsafeEvidenceError):
        export(repo_root, "fake_target", relative_path)
    assert all_files(repo_root) == before


def test_source_path_traversal_and_shape_rejections(tmp_path: Path) -> None:
    good = tmp_path / "good.json"
    write_source(good, b"{}")
    assert safe_read_bounded(good) == b"{}"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        safe_read_bounded(Path("relative.json"))
    assert exc_info.value.rejection_class == "unsafe_path_relative"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        safe_read_bounded(Path("/no/such/file.json"))
    assert exc_info.value.rejection_class == "unsafe_path_missing"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        safe_read_bounded(tmp_path / ".." / "escape.json")
    assert exc_info.value.rejection_class == "unsafe_path_lexical"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        safe_read_bounded(tmp_path)
    assert exc_info.value.rejection_class == "unsafe_path_not_regular"
    wrong_mode = tmp_path / "mode.json"
    write_source(wrong_mode, b"{}")
    os.chmod(wrong_mode, 0o644)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        safe_read_bounded(wrong_mode)
    assert exc_info.value.rejection_class == "unsafe_path_mode"
    hard = tmp_path / "hard.json"
    os.link(good, hard)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        safe_read_bounded(hard)
    assert exc_info.value.rejection_class == "unsafe_path_nlink"
    oversized = tmp_path / "big.json"
    write_source(oversized, b"0" * (MAX_SAFE_EVIDENCE_BYTES + 1))
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        safe_read_bounded(oversized)
    assert exc_info.value.rejection_class == "unsafe_path_size"


def test_symlink_source_and_destination_rejections(repo_root: Path, tmp_path: Path) -> None:
    real = tmp_path / "real.json"
    write_source(real, b"{}")
    link = tmp_path / "link.json"
    os.symlink(real, link)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        safe_read_bounded(link)
    assert exc_info.value.rejection_class == "unsafe_path_symlink"
    real_dir = tmp_path / "real-dir"
    real_dir.mkdir()
    dir_link = tmp_path / "dir-link"
    os.symlink(real_dir, dir_link)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        safe_read_bounded(dir_link / "real.json")
    assert exc_info.value.rejection_class == "unsafe_path_symlink"

    # Symlink final destination name.
    subdir = repo_root / "oap" / "evidence" / "005-ar"
    subdir.mkdir(parents=True)
    os.symlink(real, subdir / "target.json")
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        resolve_evidence_destination(repo_root, "005-ar/target.json")
    assert exc_info.value.rejection_class == "destination_symlink"

    # Symlink intermediate component under the evidence root.
    outside = tmp_path / "outside"
    outside.mkdir()
    (repo_root / "oap" / "evidence").rename(repo_root / "oap" / "evidence-real")
    os.symlink(repo_root / "oap" / "evidence-real", repo_root / "oap" / "evidence")
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        resolve_evidence_destination(repo_root, "005-ar/other.json")
    assert exc_info.value.rejection_class == "destination_component_symlink"
    (repo_root / "oap" / "evidence").unlink()
    (repo_root / "oap" / "evidence-real").rename(repo_root / "oap" / "evidence")

    # A directory component below the evidence anchor that is a symlink is
    # refused at write time even though a resolver ran earlier.
    real_dir = tmp_path / "real-write-dir"
    real_dir.mkdir()
    link_name = "005-link"
    evidence_dir = repo_root / "oap" / "evidence"
    os.symlink(real_dir, evidence_dir / link_name)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        atomic_write_bounded(repo_root, "005-link/f.json", b"{}")
    assert exc_info.value.rejection_class == "destination_component_symlink"
    assert not (real_dir / "f.json").exists()
    (evidence_dir / link_name).unlink()

    # A destination escaping the oap/evidence anchor is refused outright:
    # the writer only accepts relative destinations below the anchor.
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        atomic_write_bounded(repo_root, "../outside/f.json", b"{}")
    assert exc_info.value.rejection_class == "destination_traversal"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        atomic_write_bounded(repo_root, "/etc/slaif-escape.json", b"{}")
    assert exc_info.value.rejection_class == "destination_absolute"


# --------------------------------------------------------------------------
# Descriptor discipline and destination lifecycle
# --------------------------------------------------------------------------


def test_descriptors_close_on_success_and_failure(repo_root: Path) -> None:
    base = current_fds()
    export(repo_root, "fake_target", "005-ar/fake-isolated-target.json")
    assert current_fds() == base
    with pytest.raises(UnsafeEvidenceError):
        export(repo_root, "fake_target", "005-ar/fake-isolated-target.json")
    assert current_fds() == base
    with pytest.raises(UnsafeEvidenceError):
        resolve_evidence_destination(repo_root, "../x.json")
    assert current_fds() == base
    source = repo_root / "source.json"
    write_source(source, materialize_raw("fake_target"))
    assert safe_read_bounded(source) == materialize_raw("fake_target")
    assert current_fds() == base
    with pytest.raises(UnsafeEvidenceError):
        safe_read_bounded(repo_root / "absent.json")
    assert current_fds() == base


def test_missing_intermediate_directories_created_0700(repo_root: Path) -> None:
    export(repo_root, "fake_target", "a/b/fake-ap37-gate-authority.json")
    for relative in ("oap/evidence", "oap/evidence/a", "oap/evidence/a/b"):
        st = (repo_root / relative).stat()
        assert stat.S_IMODE(st.st_mode) == 0o700, relative
        assert st.st_uid == os.getuid(), relative


def test_existing_destination_refused_and_preserved(repo_root: Path) -> None:
    dest = destination(repo_root, "005-ar/existing.json")
    dest.parent.mkdir(parents=True)
    sentinel = b"pre-existing sentinel bytes\n"
    dest.write_bytes(sentinel)
    os.chmod(dest, 0o600)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        export(repo_root, "fake_target", "005-ar/existing.json")
    assert exc_info.value.rejection_class == "destination_exists"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        resolve_evidence_destination(repo_root, "005-ar/existing.json")
    assert exc_info.value.rejection_class == "destination_exists"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        atomic_write_bounded(repo_root, "005-ar/existing.json", b"new content")
    assert exc_info.value.rejection_class == "destination_exists"
    assert dest.read_bytes() == sentinel
    assert stat.S_IMODE(dest.stat().st_mode) == 0o600


@pytest.mark.parametrize("failure", ["temp", "fsync", "rename", "verify"])
def test_write_pipeline_failures_leave_no_artifact(
    repo_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    sub = repo_root / "oap" / "evidence" / "005-ar"
    sub.mkdir(parents=True)
    sentinel = sub / "pre-existing.json"
    sentinel.write_bytes(b"keep me")
    os.chmod(sentinel, 0o600)
    base = current_fds()

    if failure == "temp":
        real_open = os.open

        def failing_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
            if (
                isinstance(path, str)
                and path.startswith(".")
                and (flags & os.O_CREAT)
                and (flags & os.O_EXCL)
            ):
                raise PermissionError("injected temporary-file creation failure")
            return real_open(path, flags, *args, **kwargs)

        monkeypatch.setattr(os, "open", failing_open)
    elif failure == "fsync":

        def failing_fsync(fd: int, *args: Any, **kwargs: Any) -> None:
            raise OSError("injected fsync failure")

        monkeypatch.setattr(os, "fsync", failing_fsync)
    elif failure == "rename":

        def failing_replace(src: str, dst: str, *args: Any, **kwargs: Any) -> None:
            raise OSError("injected rename failure")

        monkeypatch.setattr(os, "replace", failing_replace)
    else:
        real_fstat = os.fstat

        def failing_fstat(fd: int) -> os.stat_result:
            seq = tuple(real_fstat(fd))
            return os.stat_result(seq[:6] + (seq[6] + 1,) + seq[7:])

        monkeypatch.setattr(os, "fstat", failing_fstat)

    dest = destination(repo_root, "005-ar/failure.json")
    expected_class = "write_verification_failed" if failure == "verify" else "write_failed"
    if failure == "temp":
        expected_class = "destination_temp_failed"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        export(repo_root, "fake_target", "005-ar/failure.json")
    assert exc_info.value.rejection_class == expected_class
    # No apparently complete result, no temporary residue, and the
    # pre-existing destination is untouched.
    assert not dest.exists()
    assert os.listdir(sub) == ["pre-existing.json"]
    assert sentinel.read_bytes() == b"keep me"
    assert current_fds() == base


# --------------------------------------------------------------------------
# JSONL strictness: line counts and preflight validation
# --------------------------------------------------------------------------


def test_jsonl_line_and_preflight_rejections() -> None:
    role = "fake_target"
    spec = contracts.result_spec_for_role(role)
    preflight_spec = contracts.preflight_spec_for_role(role)
    good_preflight = json.dumps(
        contracts.materialize_sample(role)[1], sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    result_line = (
        json.dumps(contracts.materialize_sample(role)[0], sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        accept_evidence_bytes(b"", spec, preflight_spec=preflight_spec)
    assert exc_info.value.rejection_class == "decode_empty"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        accept_evidence_bytes(b"\n \n", spec, preflight_spec=preflight_spec)
    assert exc_info.value.rejection_class == "decode_empty"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        accept_evidence_bytes(
            good_preflight + b"\n" + result_line + b'{"extra": 1}\n',
            spec,
            preflight_spec=preflight_spec,
        )
    assert exc_info.value.rejection_class == "decode_extra_lines"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        accept_evidence_bytes(b"not json\n" + result_line, spec, preflight_spec=preflight_spec)
    assert exc_info.value.rejection_class == "decode_invalid_json"
    preflight_sample = contracts.materialize_sample(role)[1]
    assert preflight_sample is not None
    bad_preflight = dict(preflight_sample)
    bad_preflight["status"] = "WRONG"
    bad_line = (json.dumps(bad_preflight, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        accept_evidence_bytes(bad_line + result_line, spec, preflight_spec=preflight_spec)
    assert exc_info.value.rejection_class == "shape_string_value"
    assert exc_info.value.path == "preflight.status"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        accept_evidence_bytes(good_preflight + b"\n" + result_line, spec, preflight_spec=None)
    assert exc_info.value.rejection_class == "decode_unvalidated_preflight_line"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        accept_evidence_bytes(
            b'{"status": "COMPLETE", "status": "COMPLETE"}\n', spec, preflight_spec=preflight_spec
        )
    assert exc_info.value.rejection_class == "decode_duplicate_key"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        accept_evidence_bytes(b'{"status": NaN}\n', spec, preflight_spec=preflight_spec)
    assert exc_info.value.rejection_class == "decode_non_finite"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        accept_evidence_bytes(b"[1, 2]\n", spec, preflight_spec=preflight_spec)
    assert exc_info.value.rejection_class == "decode_not_object"


# --------------------------------------------------------------------------
# Bounded open values: depth, cardinality, ranges, and string grammar
# --------------------------------------------------------------------------


def test_open_value_bounds_and_string_grammar() -> None:
    spec = OpenValueSpec()
    valid = {
        "status": "PASSED",
        "count": 5,
        "ratio": 1.5,
        "nothing": None,
        "flag": True,
        "nested": {"a": {"b": {"c": "x"}}},
    }
    validate_value(spec, valid)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        validate_value(spec, {"l0": {"l1": {"l2": {"l3": {"l4": {"l5": 1}}}}}})
    assert exc_info.value.rejection_class == "open_depth"
    validate_value(spec, {"edge": "x" * 128})
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        validate_value(spec, {"long": "x" * 129})
    assert exc_info.value.rejection_class == "open_string_length"
    for unsafe in ("raw prompt text", "line1\nline2", "caf\u00e9", '"quoted"'):
        with pytest.raises(UnsafeEvidenceError) as exc_info:
            validate_value(spec, {"safe_key": unsafe})
        assert exc_info.value.rejection_class == "open_string_grammar"
    # Unsafe key classes are rejected at the key level, before any value
    # inspection, and are never stripped.
    for denied_key in (
        "prompt",
        "raw_body",
        "model_output",
        "tool_output",
        "api_key",
        "authorization",
        "signature",
        "nonce",
        "request_id",
        "image_url",
        "private_path",
        "user_message",
        "response_text",
    ):
        with pytest.raises(UnsafeEvidenceError) as exc_info:
            validate_value(spec, {denied_key: "token-like-value"})
        assert exc_info.value.rejection_class == "open_key_class_denied"
    # The deny policy applies at every open nesting level.
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        validate_value(spec, {"a": {"b": {"c": {"model_output": "x"}}}})
    assert exc_info.value.rejection_class == "open_key_class_denied"
    # Legitimate closed-class fact keys (counters/flags) remain admissible.
    validate_value(spec, {"status": "PASSED", "count": 3, "flag": True})
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        validate_value(spec, {"bad key": 1})
    assert exc_info.value.rejection_class == "open_dict_key"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        validate_value(spec, {"k" * 65: 1})
    assert exc_info.value.rejection_class == "open_dict_key"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        validate_value(spec, {f"k{i}": 0 for i in range(65)})
    assert exc_info.value.rejection_class == "open_dict_keys"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        validate_value(spec, {"list": list(range(65))})
    assert exc_info.value.rejection_class == "open_list_length"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        validate_value(spec, {"big": 1_000_001})
    assert exc_info.value.rejection_class == "open_int_range"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        validate_value(spec, {"negative": -1})
    assert exc_info.value.rejection_class == "open_int_range"
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        validate_value(spec, {"big_float": 2_000_000.0})
    assert exc_info.value.rejection_class == "open_float_range"
    # Unsafe content cannot ride into checkpoints through phase_facts,
    # whether the facts are closed (unknown key) or the value is an open
    # structure (denied key class / unsafe grammar).
    base_checkpoint: dict[str, object] = {
        "lifetime_id": "identity",
        "phase": "codex",
        "ordinal": 5,
        "completed": True,
        "ready": True,
        "failure_class": None,
        "counts": {},
        "response_count": 0,
    }
    for denied_fact in (
        {"prompt": "hello world"},
        {"codex": {"model_output": "x"}},
        {"raw_body": 1},
        {"accounting": {"request": "sk-abcdef123456"}},
        {"provider_observation": {"nonce": "abcdef0123456789"}},
        {"governance": {"tool_output": "x"}},
    ):
        with pytest.raises(UnsafeEvidenceError):
            validate_value(
                contracts.CHECKPOINT_SPEC,
                {**base_checkpoint, "phase_facts": denied_fact},
            )
    # A fully closed valid phase fact set still passes.
    valid_facts = {
        "evidence_kind": "semantic",
        "codex": {
            "status": "PASSED",
            "client_verification": {"status": "PASSED", "sentinel_passed": True},
            "provider_inference_call_count": 2,
            "provider_turns_expected": 2,
            "exit_status": 0,
            "command_lifecycle": "success",
            "sentinel_passed": True,
            "tool_call_count_class": "1",
            "dependency_hash_equal": True,
            "dependency_length_equal": True,
            "call_id_same_hmac": True,
            "scope_no_downgrade": True,
        },
        "provider_observation": {
            "provider_boundary": {"lifecycle_valid": True, "terminal": True},
            "source": "direct_transport_observer",
            "fake_oracle": "unavailable",
        },
        "transport_observation": {
            "provider_boundary_observed": True,
            "matches_fake_provider": True,
        },
        "accounting": {
            "two_terminal_reservations": True,
            "zero_pending": True,
            "zero_duplicate_request_ids": True,
            "request": True,
            "usage": True,
            "tokens": True,
            "cost": True,
        },
        "governance": {"dependency_one_equal": True, "acquisition_before_completion": True},
    }
    validate_value(contracts.CHECKPOINT_SPEC, {**base_checkpoint, "phase_facts": valid_facts})


# --------------------------------------------------------------------------
# Durable export survives deletion of the temporary source
# --------------------------------------------------------------------------


def test_durable_export_survives_temp_source_deletion(repo_root: Path, tmp_path: Path) -> None:
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    source = src_dir / "protected-result.json"
    raw = materialize_raw("protected_target")
    write_source(source, raw)
    data = safe_read_bounded(source)
    assert data == raw
    prov = export(
        repo_root,
        "protected_target",
        "005-ar/protected-final-1024-success.json",
        mode="exact",
        raw=data,
    )
    os.unlink(source)
    src_dir.rmdir()
    dest = destination(repo_root, "005-ar/protected-final-1024-success.json")
    assert dest.exists()
    assert dest.read_bytes() == raw
    assert hashlib.sha256(dest.read_bytes()).hexdigest() == prov.committed_sha256


# --------------------------------------------------------------------------
# Full fake gate (AP37) role: closed export and nested fail-closed shapes
# --------------------------------------------------------------------------


def test_full_fake_gate_role_exports_exact_and_deterministic(repo_root: Path) -> None:
    raw = materialize_raw("full_fake_gate")
    prov = export(
        repo_root,
        "full_fake_gate",
        "005-ar/reused_ap37_fake_gate.json",
        mode="exact",
        raw=raw,
    )
    data = destination(repo_root, "005-ar/reused_ap37_fake_gate.json").read_bytes()
    assert data == raw
    assert prov.schema == contracts.FULL_GATE_RESULT_SCHEMA_NAME
    assert prov.committed_sha256 == prov.original_sha256 == hashlib.sha256(raw).hexdigest()
    assert prov.byte_count == len(raw)
    prov_det = export(
        repo_root, "full_fake_gate", "005-ar/ap37-deterministic.json", mode="deterministic"
    )
    det_data = destination(repo_root, "005-ar/ap37-deterministic.json").read_bytes()
    assert prov_det.committed_sha256 == hashlib.sha256(det_data).hexdigest()
    assert prov_det.original_sha256 == hashlib.sha256(raw).hexdigest()
    # The deterministic document validates against the closed role spec.
    validate_value(contracts.result_spec_for_role("full_fake_gate"), json.loads(det_data), "result")


def test_full_fake_gate_nested_mutations_rejected_not_stripped(repo_root: Path) -> None:
    def add_unknown_case_key(doc: dict[str, object]) -> None:
        cases = doc["protected_mode_synthetic_cases"]
        assert isinstance(cases, dict)
        case = cases["observer_failure_after_dispatch"]
        assert isinstance(case, dict)
        case["injected_nested_key"] = {"x": 1}

    def drop_case_key(doc: dict[str, object]) -> None:
        cases = doc["protected_mode_synthetic_cases"]
        assert isinstance(cases, dict)
        case = cases["vision_failure_after_codex"]
        assert isinstance(case, dict)
        del case["status"]

    def unsafe_nested_value(doc: dict[str, object]) -> None:
        synthetic = doc["protected_mode_synthetic"]
        assert isinstance(synthetic, dict)
        conformance = synthetic["protected_conformance"]
        assert isinstance(conformance, dict)
        identities = conformance["source_identities"]
        assert isinstance(identities, dict)
        identities["runner"] = "other/module"

    for mutate, expected in (
        (add_unknown_case_key, "shape_key_unknown"),
        (drop_case_key, "shape_key_missing"),
        (unsafe_nested_value, "shape_string_value"),
    ):
        doc, preflight = contracts.materialize_sample("full_fake_gate")
        mutate(doc)
        raw = raw_from(doc, preflight)
        spec = contracts.result_spec_for_role("full_fake_gate")
        preflight_spec = contracts.preflight_spec_for_role("full_fake_gate")
        with pytest.raises(UnsafeEvidenceError) as exc_info:
            accept_evidence_bytes(raw, spec, preflight_spec=preflight_spec)
        assert exc_info.value.rejection_class == expected
        with pytest.raises(UnsafeEvidenceError):
            export(repo_root, "full_fake_gate", "005-ar/never-written.json", raw=raw)
    assert all_files(repo_root) == set()


def test_full_fake_gate_durable_export_survives_temp_source_deletion(
    repo_root: Path, tmp_path: Path
) -> None:
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    source = src_dir / "fake-gate.json"
    raw = materialize_raw("full_fake_gate")
    write_source(source, raw)
    data = safe_read_bounded(source)
    assert data == raw
    prov = export(
        repo_root,
        "full_fake_gate",
        "005-ar/reused_ap37_fake_gate.json",
        mode="exact",
        raw=data,
    )
    os.unlink(source)
    src_dir.rmdir()
    dest = destination(repo_root, "005-ar/reused_ap37_fake_gate.json")
    assert dest.exists()
    assert dest.read_bytes() == raw
    assert hashlib.sha256(dest.read_bytes()).hexdigest() == prov.committed_sha256


def test_verify_existing_evidence_destination_classes(repo_root: Path, tmp_path: Path) -> None:
    raw = materialize_raw("full_fake_gate")
    source = tmp_path / "gate.json"
    write_source(source, raw)
    prov = export(repo_root, "full_fake_gate", "005-ar/ap37-verify.json", mode="exact", raw=raw)
    count = verify_existing_evidence_destination(
        repo_root, "005-ar/ap37-verify.json", prov.committed_sha256
    )
    assert count == len(raw)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        verify_existing_evidence_destination(repo_root, "005-ar/ap37-verify.json", "0" * 64)
    assert exc_info.value.rejection_class == "destination_bytes_mismatch"
    assert destination(repo_root, "005-ar/ap37-verify.json").read_bytes() == raw
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        verify_existing_evidence_destination(repo_root, "005-ar/absent.json", "0" * 64)
    assert exc_info.value.rejection_class == "destination_missing"


def test_destination_readback_works_below_execute_only_ancestor(
    tmp_path: Path,
) -> None:
    """Anchored destination read-back must work under execute-only mounts.

    On hosts where the repository sits below a directory that grants
    search (``x``) but not read (``r``) permission (for example NFS home
    mounts), the root-anchored source reader cannot traverse the barrier
    at all, while the anchored destination reader must still verify
    byte-identical read-backs through the repository-root anchor.
    """
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("mode-bit barriers do not bind the root user")
    barrier = tmp_path / "barrier"
    barrier.mkdir()
    try:
        repo = barrier / "repo"
        (repo / "oap" / "evidence" / "005-ar").mkdir(parents=True)
        os.chmod(repo / "oap", 0o700)
        os.chmod(repo / "oap" / "evidence", 0o700)
        barrier.chmod(0o111)
        payload = b'{"execute_only_ancestor": true}\n'
        dest = repo / "oap" / "evidence" / "005-ar" / "exec-only.json"
        dest.write_bytes(payload)
        os.chmod(dest, 0o600)
        # Root-anchored source reader: fixed rejection at the barrier.
        with pytest.raises(UnsafeEvidenceError) as exc_info:
            safe_read_bounded(dest)
        assert exc_info.value.rejection_class == "unsafe_path_unreadable"
        # Anchored destination reader: byte-identical read-back succeeds.
        raw = read_existing_evidence_destination_bounded(repo, "005-ar/exec-only.json")
        assert raw == payload
        count = verify_existing_evidence_destination(
            repo, "005-ar/exec-only.json", hashlib.sha256(payload).hexdigest()
        )
        assert count == len(payload)
    finally:
        barrier.chmod(0o700)


def test_remove_verified_evidence_destination(repo_root: Path) -> None:
    raw = materialize_raw("full_fake_gate")
    prov = export(repo_root, "full_fake_gate", "005-ar/ap37-remove.json", mode="exact", raw=raw)
    dest = destination(repo_root, "005-ar/ap37-remove.json")
    remove_verified_evidence_destination(repo_root, "005-ar/ap37-remove.json")
    assert not dest.exists()
    assert prov.committed_sha256
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        remove_verified_evidence_destination(repo_root, "005-ar/ap37-remove.json")
    assert exc_info.value.rejection_class == "destination_missing"
    # A non-0600 final node is refused, never removed.
    export(repo_root, "full_fake_gate", "005-ar/ap37-remove-mode.json", mode="exact", raw=raw)
    dest_mode = destination(repo_root, "005-ar/ap37-remove-mode.json")
    os.chmod(dest_mode, 0o644)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        remove_verified_evidence_destination(repo_root, "005-ar/ap37-remove-mode.json")
    assert exc_info.value.rejection_class == "destination_unsafe"
    assert dest_mode.exists()
    # A hard-linked final node (nlink > 1) is refused, never removed.
    export(repo_root, "full_fake_gate", "005-ar/ap37-remove-link.json", mode="exact", raw=raw)
    dest_link = destination(repo_root, "005-ar/ap37-remove-link.json")
    os.link(dest_link, repo_root / "oap" / "evidence" / "005-ar" / "hardlink.json")
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        remove_verified_evidence_destination(repo_root, "005-ar/ap37-remove-link.json")
    assert exc_info.value.rejection_class == "destination_unsafe"
    assert dest_link.exists()


# --------------------------------------------------------------------------
# Zero external activity: no socket, subprocess, Git, or model/provider call
# --------------------------------------------------------------------------


def test_export_performs_no_external_activity(
    repo_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def explode(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("external activity attempted")

    for name in ("socket", "create_connection", "getaddrinfo", "socketpair"):
        monkeypatch.setattr(socket, name, explode)
    for name in ("Popen", "run", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, explode)
    monkeypatch.setattr(os, "system", explode)
    monkeypatch.setattr(os, "execve", explode)

    before = all_files(repo_root)
    for role in sorted(contracts.ROLES):
        export(repo_root, role, f"005-ar/{role}-evidence.json")
    assert not (repo_root / ".git").exists()
    added = all_files(repo_root) - before
    expected = {
        destination(repo_root, f"005-ar/{role}-evidence.json") for role in sorted(contracts.ROLES)
    }
    assert added == expected


# --------------------------------------------------------------------------
# Provenance: closed record that matches the exact committed bytes
# --------------------------------------------------------------------------


def test_provenance_record_is_closed_and_matches_committed_bytes(repo_root: Path) -> None:
    prov = export(
        repo_root, "fake_target", "005-ar/fake-isolated-target.json", mode="deterministic"
    )
    data = destination(repo_root, "005-ar/fake-isolated-target.json").read_bytes()
    assert prov.byte_count == len(data)
    assert prov.committed_sha256 == hashlib.sha256(data).hexdigest()
    assert prov.original_sha256 == hashlib.sha256(materialize_raw("fake_target")).hexdigest()
    payload: dict[str, Any] = json.loads(prov.to_json())
    assert set(payload) == {
        "role",
        "schema",
        "relative_path",
        "byte_count",
        "original_sha256",
        "committed_sha256",
        "mode",
    }
    assert payload["committed_sha256"] == prov.committed_sha256
    assert payload["original_sha256"] == prov.original_sha256


@pytest.mark.parametrize(
    ("kwargs", "expected_class"),
    [
        ({"role": "bogus_role"}, "role_unknown"),
        ({"schema": "oap-something-else-v1"}, "export_schema_mismatch"),
        ({"mode": "weird"}, "export_mode_unknown"),
    ],
)
def test_export_role_schema_mode_are_closed(
    repo_root: Path, kwargs: dict[str, str], expected_class: str
) -> None:
    base = {
        "role": "fake_target",
        "schema": contracts.TARGET_RESULT_SCHEMA_NAME,
        "raw": materialize_raw("fake_target"),
        "result_spec": contracts.result_spec_for_role("fake_target"),
        "preflight_spec": contracts.preflight_spec_for_role("fake_target"),
        "relative_path": "005-ar/closed.json",
        "mode": "exact",
    }
    base.update(kwargs)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        export_safe_result(repo_root, **base)  # type: ignore[arg-type]
    assert exc_info.value.rejection_class == expected_class


def test_export_refuses_substituted_specs(repo_root: Path) -> None:
    raw = materialize_raw("fake_target")
    # A different role's result spec is not interchangeable.
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        export_safe_result(
            repo_root,
            role="fake_target",
            schema=contracts.TARGET_RESULT_SCHEMA_NAME,
            raw=raw,
            result_spec=contracts.result_spec_for_role("protected_target"),
            preflight_spec=contracts.preflight_spec_for_role("fake_target"),
            relative_path="005-ar/spec.json",
            mode="exact",
        )
    assert exc_info.value.rejection_class == "export_spec_mismatch"
    # Manifest carries no preflight line; a preflight spec is a mismatch.
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        export_safe_result(
            repo_root,
            role="manifest",
            schema=contracts.MANIFEST_SCHEMA,
            raw=materialize_raw("manifest"),
            result_spec=contracts.result_spec_for_role("manifest"),
            preflight_spec=contracts.PREFLIGHT_SPEC,
            relative_path="005-ar/preflight.json",
            mode="exact",
        )
    assert exc_info.value.rejection_class == "export_preflight_mismatch"
    # Non-manifest roles require the exact closed preflight spec.
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        export_safe_result(
            repo_root,
            role="fake_target",
            schema=contracts.TARGET_RESULT_SCHEMA_NAME,
            raw=raw,
            result_spec=contracts.result_spec_for_role("fake_target"),
            preflight_spec=None,
            relative_path="005-ar/preflight.json",
            mode="exact",
        )
    assert exc_info.value.rejection_class == "export_preflight_mismatch"


# --------------------------------------------------------------------------
# dir_fd anchoring: CWD-relative open regressions and no-fchdir writes
# --------------------------------------------------------------------------


def test_safe_read_is_anchored_to_dir_fd_not_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A CWD-relative open (dir_fd passed as positional mode) must fail.

    The real tree is ``tmp_path/tree/leaf/result.json``.  The shadow CWD
    contains ``tree/leaf/result.json`` as a symlink to a different 0600
    file.  A walk that opens any component relative to the process CWD
    instead of the parent directory descriptor either misses the tree or
    follows the symlink and is rejected; only a dir_fd-anchored walk reads
    the real bytes.
    """
    leaf = tmp_path / "tree" / "leaf"
    leaf.mkdir(parents=True)
    real_file = leaf / "result.json"
    write_source(real_file, b'{"real": true}\n')

    shadow = tmp_path / "shadow"
    (shadow / "tree" / "leaf").mkdir(parents=True)
    evil = tmp_path / "evil.json"
    write_source(evil, b'{"evil": true}\n')
    os.symlink(evil, shadow / "tree" / "leaf" / "result.json")
    monkeypatch.chdir(shadow)

    # A mid-chain symlink shadow as well: a CWD-relative walk would follow
    # it and read the evil file.
    shadow2 = tmp_path / "shadow2"
    shadow2.mkdir()
    (tmp_path / "evil-dir" / "leaf").mkdir(parents=True)
    write_source(tmp_path / "evil-dir" / "leaf" / "result.json", b'{"evil": true}\n')
    os.symlink(tmp_path / "evil-dir", shadow2 / "tree")
    monkeypatch.chdir(shadow2)
    assert safe_read_bounded(real_file) == b'{"real": true}\n'

    # And from an unrelated CWD with a same-named regular file shadow.
    shadow3 = tmp_path / "shadow3"
    shadow3.mkdir()
    write_source(shadow3 / "result.json", b'{"evil": true}\n')
    monkeypatch.chdir(shadow3)
    assert safe_read_bounded(real_file) == b'{"real": true}\n'


def test_export_uses_no_fchdir_and_no_cwd_reliance(
    repo_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The anchored writer must not use process-wide fchdir or chdir."""

    # Move the process CWD away from the repository: the write must still
    # land at the absolute, anchored destination.
    else_dir = repo_root / "elsewhere"
    else_dir.mkdir()
    monkeypatch.chdir(else_dir)

    def explode(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("process-wide CWD mutation attempted")

    monkeypatch.setattr(os, "fchdir", explode)
    monkeypatch.setattr(os, "chdir", explode)
    prov = export(repo_root, "fake_target", "005-ar/fake-isolated-target.json", mode="exact")
    data = destination(repo_root, "005-ar/fake-isolated-target.json").read_bytes()
    assert hashlib.sha256(data).hexdigest() == prov.committed_sha256
    assert else_dir.exists() and not list(else_dir.iterdir())


def test_intermediate_components_reverified_at_write_time(
    repo_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Resolution and writing are separate calls: the writer re-walks.

    A resolver runs first (success).  Before the write, an intermediate
    component below the evidence root is replaced by a symlink to an
    unrelated directory.  A writer that trusted the earlier resolution
    (path re-traversal outside the anchor) would follow it; the anchored
    writer must reject at write time and leave no artifact.
    """
    relative = "005-ar/real-target.json"
    resolve_evidence_destination(repo_root, relative)
    sub = repo_root / "oap" / "evidence" / "005-ar"
    real_sub = tmp_path / "real-sub"
    real_sub.mkdir()
    sub.rename(tmp_path / "005-ar-real")
    os.symlink(real_sub, sub)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        export(repo_root, "fake_target", relative)
    assert exc_info.value.rejection_class == "destination_component_symlink"
    assert not (real_sub / "real-target.json").exists()
    assert list(real_sub.iterdir()) == []


def test_readback_mismatch_leaves_no_artifact(
    repo_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If bytes at the anchored destination differ after the rename, the
    write fails closed and removes its own unverified artifact."""
    raw = materialize_raw("fake_target")
    dest = destination(repo_root, "005-ar/corrupt.json")
    dest.parent.mkdir(parents=True)
    real_replace = os.replace

    def corrupting_replace(src: Any, dst: Any, *args: Any, **kwargs: Any) -> None:
        real_replace(src, dst, *args, **kwargs)
        # Same-user rewrite between rename and read-back verification,
        # keeping the exact size so only the hash check can catch it.
        with open(dest, "rb+") as handle:
            handle.write(b"XXXX")

    monkeypatch.setattr(os, "replace", corrupting_replace)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        export_safe_result(
            repo_root,
            role="fake_target",
            schema=contracts.ROLE_SCHEMAS["fake_target"],
            raw=raw,
            result_spec=contracts.result_spec_for_role("fake_target"),
            preflight_spec=contracts.preflight_spec_for_role("fake_target"),
            relative_path="005-ar/corrupt.json",
            mode="exact",
        )
    assert exc_info.value.rejection_class == "write_verification_failed"
    assert not dest.exists()
    assert os.listdir(dest.parent) == []


def test_pattern_materializer_matches_every_closed_pattern() -> None:
    """Every identifier pattern in the closed schemas materializes to a
    string that matches it (guards future spec additions)."""
    patterns: set[str] = set()

    def walk(spec: Any) -> None:
        if isinstance(spec, StrSpec):
            if spec.pattern is not None:
                patterns.add(spec.pattern)
        elif isinstance(spec, DictSpec):
            for _, child in spec.required + spec.optional:
                walk(child)
        elif isinstance(spec, ListSpec):
            walk(spec.element)
        elif isinstance(spec, UnionSpec):
            for alternative in spec.alternatives:
                walk(alternative)
        elif isinstance(spec, OpenDictSpec):
            walk(spec.value)

    for role in sorted(contracts.ROLES):
        walk(contracts.result_spec_for_role(role))
        preflight = contracts.preflight_spec_for_role(role)
        if preflight is not None:
            walk(preflight)
    assert patterns
    for pattern in sorted(patterns):
        token = contracts._pattern_token(pattern)
        assert re.fullmatch(pattern, token) is not None, pattern


# --------------------------------------------------------------------------
# Packaging: the runtime wheel excludes exporter, evidence, and tests
# --------------------------------------------------------------------------


def test_wheel_excludes_exporter_and_evidence() -> None:
    root = Path(__file__).resolve().parents[1]
    pyproject: dict[str, Any] = tomllib.loads((root / "pyproject.toml").read_text("utf-8"))
    wheel: dict[str, Any] = pyproject["tool"]["hatch"]["build"]["targets"]["wheel"]
    assert wheel["packages"] == ["src/slaif_local_coding"]
    # The wheel target must not reference tests, oap, or the exporter.
    wheel_blob = json.dumps(wheel)
    assert "tests" not in wheel_blob
    assert "oap" not in wheel_blob
    assert "safe_evidence" not in wheel_blob
    # Order 009-a deliberate build policy (docs/RELEASE-ARTIFACT-POLICY.md):
    # the top-level exclude keeps orchestration transcripts, OAP runtime state,
    # harness scripts, references, and placeholder files out of every artifact;
    # the sdist is an explicit developer-only whitelist that never includes
    # oap/ or runtime state.
    top_exclude: list[Any] = pyproject["tool"]["hatch"]["build"]["exclude"]
    for forbidden in ("oap", "scripts", "references", "runtime.env", "Local", "clean", "unchanged"):
        assert forbidden in top_exclude
    sdist_include: list[Any] = pyproject["tool"]["hatch"]["build"]["targets"]["sdist"]["include"]
    assert "oap" not in sdist_include
    assert "scripts" not in sdist_include
    # The exporter and its fixtures live under tests/, outside the wheel
    # package root.
    assert "tests" in Path(__file__).resolve().parent.parts
    src_package = root / "src" / "slaif_local_coding"
    assert src_package.is_dir()
    assert not (src_package / "safe_evidence.py").exists()
    dependencies: list[Any] = pyproject["project"]["dependencies"]
    assert {dep.split(">=")[0].strip() for dep in dependencies} == {
        "fastapi",
        "httpx",
        "prometheus-client",
        "pydantic",
        "uvicorn",
    }
