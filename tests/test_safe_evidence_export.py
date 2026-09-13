"""Synthetic tests for the 008-a safe-evidence export CLI and audit core.

Every fixture is generated from the closed role schemas
(:func:`contracts.materialize_sample`) inside ``tmp_path``; the suite never
reads the historical ``/tmp`` artifacts, never opens a network socket,
never spawns a provider/model/service process, and never stages Git.  The
CLI is exercised through a real subprocess of the repository script; the
audit core is exercised with an injectable authority list.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from tests.helpers import safe_evidence_contracts as contracts
from tests.helpers.safe_evidence import (
    UnsafeEvidenceError,
    accept_evidence_bytes,
    safe_read_bounded,
    validate_value,
)

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "safe_evidence_export.py"


def write_source(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    os.chmod(path, 0o600)


def materialize_raw(role: str) -> bytes:
    doc, preflight = contracts.materialize_sample(role)
    raw = b""
    if preflight is not None:
        raw += (json.dumps(preflight, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    raw += (json.dumps(doc, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    return raw


@pytest.fixture()
def repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "oap" / "evidence").mkdir(parents=True)
    os.chmod(root / "oap", 0o700)
    os.chmod(root / "oap" / "evidence", 0o700)
    return root


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


# --------------------------------------------------------------------------
# CLI: export
# --------------------------------------------------------------------------


def test_cli_export_exact_mode_roundtrip(repo_root: Path, tmp_path: Path) -> None:
    raw = materialize_raw("protected_target")
    source = tmp_path / "src" / "protected-result.json"
    write_source(source, raw)
    result = run_cli(
        [
            "--repo-root",
            str(repo_root),
            "export",
            "--source",
            str(source),
            "--role",
            "protected_target",
            "--destination",
            "005-ar/protected_final_1024_success.json",
            "--mode",
            "exact",
        ]
    )
    assert result.returncode == 0, result.stderr
    record = json.loads(result.stdout)
    assert record["role"] == "protected_target"
    assert record["schema"] == contracts.TARGET_RESULT_SCHEMA_NAME
    assert record["mode"] == "exact"
    assert record["byte_count"] == len(raw)
    assert record["original_sha256"] == hashlib.sha256(raw).hexdigest()
    assert record["committed_sha256"] == record["original_sha256"]
    committed = repo_root / "oap" / "evidence" / "005-ar" / "protected_final_1024_success.json"
    assert committed.read_bytes() == raw
    assert hashlib.sha256(committed.read_bytes()).hexdigest() == record["committed_sha256"]


def test_cli_export_deterministic_mode(repo_root: Path, tmp_path: Path) -> None:
    raw = materialize_raw("fake_target")
    source = tmp_path / "src" / "isolated-fake-target.json"
    write_source(source, raw)
    result = run_cli(
        [
            "--repo-root",
            str(repo_root),
            "export",
            "--source",
            str(source),
            "--role",
            "fake_target",
            "--destination",
            "005-ar/fake_isolated_target_1024.json",
            "--mode",
            "deterministic",
        ]
    )
    assert result.returncode == 0, result.stderr
    record = json.loads(result.stdout)
    doc_line = raw.splitlines()[-1]
    document = json.loads(doc_line)
    expected = (json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    assert record["committed_sha256"] == hashlib.sha256(expected).hexdigest()
    assert record["original_sha256"] == hashlib.sha256(raw).hexdigest()


def test_cli_export_rejection_emits_fixed_class_and_writes_nothing(
    repo_root: Path, tmp_path: Path
) -> None:
    doc, preflight = contracts.materialize_sample("fake_target")
    doc["injected_top_level"] = {"x": 1}
    mutated = (
        (json.dumps(preflight, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        if preflight is not None
        else b""
    ) + (json.dumps(doc, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    source = tmp_path / "src" / "mutated.json"
    write_source(source, mutated)
    result = run_cli(
        [
            "--repo-root",
            str(repo_root),
            "export",
            "--source",
            str(source),
            "--role",
            "fake_target",
            "--destination",
            "005-ar/never-written.json",
            "--mode",
            "exact",
        ]
    )
    assert result.returncode == 2
    assert json.loads(result.stdout) == {"rejected": "shape_key_unknown"}
    assert not (repo_root / "oap" / "evidence" / "005-ar" / "never-written.json").exists()


def test_cli_export_refuses_existing_destination(repo_root: Path, tmp_path: Path) -> None:
    raw = materialize_raw("fake_target")
    source = tmp_path / "src" / "fake.json"
    write_source(source, raw)
    dest = repo_root / "oap" / "evidence" / "005-ar" / "existing.json"
    write_source(dest, b"pre-existing\n")
    result = run_cli(
        [
            "--repo-root",
            str(repo_root),
            "export",
            "--source",
            str(source),
            "--role",
            "fake_target",
            "--destination",
            "005-ar/existing.json",
            "--mode",
            "exact",
        ]
    )
    assert result.returncode == 2
    assert json.loads(result.stdout) == {"rejected": "destination_exists"}
    assert dest.read_bytes() == b"pre-existing\n"


def test_cli_export_rejects_unsafe_source(repo_root: Path, tmp_path: Path) -> None:
    raw = materialize_raw("fake_target")
    source = tmp_path / "src" / "loose.json"
    write_source(source, raw)
    os.chmod(source, 0o644)
    result = run_cli(
        [
            "--repo-root",
            str(repo_root),
            "export",
            "--source",
            str(source),
            "--role",
            "fake_target",
            "--destination",
            "005-ar/loose.json",
            "--mode",
            "exact",
        ]
    )
    assert result.returncode == 2
    assert json.loads(result.stdout) == {"rejected": "unsafe_path_mode"}


# --------------------------------------------------------------------------
# Audit core (synthetic authorities; the four historical paths are never
# required by ordinary CI)
# --------------------------------------------------------------------------


def synthetic_authorities(tmp_path: Path, *, fourth_present: bool = True) -> tuple[Any, ...]:
    """Four closed retained authorities.

    The AP37 authority carries a valid synthetic full-fake-gate document
    (deterministically materialized from the closed role schema); when
    absent, the audit truthfully manifests it as unavailable.
    """
    from scripts import safe_evidence_export as exporter

    raws = {
        "protected_a": materialize_raw("protected_target"),
        "protected_b": materialize_raw("protected_target"),
        "fake_a": materialize_raw("fake_target"),
        "gate_a": materialize_raw("full_fake_gate"),
    }
    for name, data in raws.items():
        if name == "gate_a" and not fourth_present:
            continue
        write_source(tmp_path / "sources" / f"{name}.json", data)
    return (
        exporter.Authority(
            authority_role="protected_final_1024_success",
            role="protected_target",
            source=str(tmp_path / "sources" / "protected_a.json"),
            relative_path="005-ar/protected_final_1024_success.json",
        ),
        exporter.Authority(
            authority_role="protected_32_token_diagnostic",
            role="protected_target",
            source=str(tmp_path / "sources" / "protected_b.json"),
            relative_path="005-ar/protected_32_token_diagnostic.json",
        ),
        exporter.Authority(
            authority_role="fake_isolated_target",
            role="fake_target",
            source=str(tmp_path / "sources" / "fake_a.json"),
            relative_path="005-ar/fake_isolated_target_1024.json",
        ),
        exporter.Authority(
            authority_role="fake_ap37_gate_authority",
            role="full_fake_gate",
            source=str(tmp_path / "sources" / "gate_a.json"),
            relative_path="005-ar/reused_ap37_fake_gate.json",
        ),
    )


def import_exporter() -> ModuleType:
    import sys as _sys

    root = Path(__file__).resolve().parents[1]
    if str(root) not in _sys.path:
        _sys.path.insert(0, str(root))
    from scripts import safe_evidence_export as exporter

    return exporter


def test_audit_accepts_all_four_authorities(repo_root: Path, tmp_path: Path) -> None:
    exporter = import_exporter()
    authorities = synthetic_authorities(tmp_path)
    summary = exporter.run_audit(repo_root, authorities)
    assert [entry["availability"] for entry in summary["authorities"]] == [
        "accepted",
        "accepted",
        "accepted",
        "accepted",
    ]
    # All four entries carry hash/size/path coherence with the exact
    # accepted source bytes.
    for authority, entry in zip(authorities, summary["authorities"], strict=True):
        source_bytes = safe_read_bounded(Path(authority.source))
        committed = repo_root / "oap" / "evidence" / authority.relative_path
        assert committed.read_bytes() == source_bytes
        assert entry["original_sha256"] == hashlib.sha256(source_bytes).hexdigest()
        assert entry["committed_sha256"] == entry["original_sha256"]
        assert entry["byte_count"] == len(source_bytes)
        assert entry["rejection_class"] is None
        assert entry["relative_path"] == authority.relative_path
    # The AP37 authority is durably exported under its stable name.
    ap37 = summary["authorities"][3]
    ap37_dest = repo_root / "oap" / "evidence" / "005-ar" / "reused_ap37_fake_gate.json"
    assert ap37_dest.exists()
    assert ap37["relative_path"] == "005-ar/reused_ap37_fake_gate.json"
    assert ap37["byte_count"] == len(safe_read_bounded(Path(authorities[3].source)))

    manifest_path = repo_root / "oap" / "evidence" / "005-ar" / "manifest.json"
    assert manifest_path.exists()
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    assert summary["manifest"]["sha256"] == hashlib.sha256(manifest_bytes).hexdigest()
    assert summary["manifest"]["byte_count"] == len(manifest_bytes)
    assert manifest["schema"] == contracts.MANIFEST_SCHEMA
    assert manifest["classification"] == "post_hoc_durable_preservation"
    assert manifest["preserved_during_objective_005"] is False
    assert "optional_not_retained" not in manifest
    assert [entry["role"] for entry in manifest["authorities"]] == [
        "protected_final_1024_success",
        "protected_32_token_diagnostic",
        "fake_isolated_target",
        "fake_ap37_gate_authority",
    ]
    assert [entry["availability"] for entry in manifest["authorities"]] == [
        "accepted",
        "accepted",
        "accepted",
        "accepted",
    ]
    ap37_entry = manifest["authorities"][3]
    ap37_source = safe_read_bounded(Path(authorities[3].source))
    assert ap37_entry["relative_path"] == "005-ar/reused_ap37_fake_gate.json"
    assert ap37_entry["original_sha256"] == hashlib.sha256(ap37_source).hexdigest()
    assert ap37_entry["committed_sha256"] == ap37_entry["original_sha256"]
    assert ap37_entry["byte_count"] == len(ap37_source)
    assert manifest["historical_authority"] == {
        "objective_005_merged_local_sha": contracts.OBJECTIVE_005_MERGED_LOCAL_SHA,
        "objective_005_tested_local_sha": contracts.OBJECTIVE_005_TESTED_LOCAL_SHA,
        "objective_005_implementation_parent_sha": (
            contracts.OBJECTIVE_005_IMPLEMENTATION_PARENT_SHA
        ),
        "objective_005_immutable_report_path": contracts.OBJECTIVE_005_IMMUTABLE_REPORT_PATH,
        "objective_005_immutable_report_sha": contracts.OBJECTIVE_005_IMMUTABLE_REPORT_SHA,
        "historical_gateway_sha": contracts.GATEWAY_MAIN_SHA,
    }
    assert manifest["acceptance_relationship"] == {
        "objective_005_acceptance": "accepted",
        "pr7_strategic_correction": "cited_not_rewritten",
    }
    # The committed manifest must itself pass the closed manifest audit.
    validate_value(contracts.MANIFEST_SPEC, manifest, "manifest")


def test_audit_ap37_absent_is_unavailable_with_null_coherence(
    repo_root: Path, tmp_path: Path
) -> None:
    exporter = import_exporter()
    authorities = synthetic_authorities(tmp_path, fourth_present=False)
    summary = exporter.run_audit(repo_root, authorities)
    assert [entry["availability"] for entry in summary["authorities"]] == [
        "accepted",
        "accepted",
        "accepted",
        "unavailable",
    ]
    ap37 = summary["authorities"][3]
    assert ap37["rejection_class"] == ("historical_temp_artifact_unavailable_on_this_host")
    assert ap37["relative_path"] is None
    assert ap37["original_sha256"] is None
    assert ap37["committed_sha256"] is None
    assert ap37["byte_count"] is None
    manifest = json.loads(
        (repo_root / "oap" / "evidence" / "005-ar" / "manifest.json").read_bytes()
    )
    validate_value(contracts.MANIFEST_SPEC, manifest, "manifest")


def test_audit_all_availability_states_are_truthful(repo_root: Path, tmp_path: Path) -> None:
    exporter = import_exporter()
    authorities = synthetic_authorities(tmp_path)
    (repo_root / "oap" / "evidence").mkdir(parents=True, exist_ok=True)
    missing = tmp_path / "sources" / "absent.json"
    bad = tmp_path / "sources" / "bad.json"
    write_source(bad, b'{"status": "COMPLETE", "unknown_key": 1}\n')
    mixed = (
        authorities[0:1]
        + (
            exporter.Authority(
                authority_role="protected_32_token_diagnostic",
                role="protected_target",
                source=str(missing),
                relative_path="005-ar/protected_32_token_diagnostic.json",
            ),
        )
        + (
            exporter.Authority(
                authority_role="fake_isolated_target",
                role="fake_target",
                source=str(bad),
                relative_path="005-ar/fake_isolated_target_1024.json",
            ),
        )
        + (
            exporter.Authority(
                authority_role="fake_ap37_gate_authority",
                role="full_fake_gate",
                source=str(bad),
                relative_path="005-ar/reused_ap37_fake_gate.json",
            ),
        )
    )
    summary = exporter.run_audit(repo_root, mixed)
    by_position = summary["authorities"]
    assert by_position[0]["availability"] == "accepted"
    assert by_position[1]["availability"] == "unavailable"
    assert by_position[1]["rejection_class"] == (
        "historical_temp_artifact_unavailable_on_this_host"
    )
    assert by_position[1]["relative_path"] is None
    assert by_position[1]["original_sha256"] is None
    assert by_position[1]["committed_sha256"] is None
    assert by_position[1]["byte_count"] is None
    # Rejected retained entry: fixed class, null content facts, never written.
    assert by_position[2]["availability"] == "rejected"
    assert by_position[2]["rejection_class"] == "shape_key_unknown"
    assert by_position[2]["relative_path"] is None
    assert by_position[2]["original_sha256"] is None
    assert by_position[2]["committed_sha256"] is None
    assert by_position[2]["byte_count"] is None
    fake_dest = repo_root / "oap" / "evidence" / "005-ar" / "fake_isolated_target_1024.json"
    assert not fake_dest.exists()
    # The AP37 source bytes are invalid for the closed full-fake-gate
    # schema, so the retained authority is rejected under a fixed class
    # with null content facts, and nothing is written for it.
    assert by_position[3]["availability"] == "rejected"
    assert by_position[3]["rejection_class"] == "shape_key_unknown"
    assert by_position[3]["relative_path"] is None
    assert by_position[3]["original_sha256"] is None
    assert by_position[3]["committed_sha256"] is None
    assert by_position[3]["byte_count"] is None
    assert not (repo_root / "oap" / "evidence" / "005-ar" / "reused_ap37_fake_gate.json").exists()
    manifest = json.loads(
        (repo_root / "oap" / "evidence" / "005-ar" / "manifest.json").read_bytes()
    )
    validate_value(contracts.MANIFEST_SPEC, manifest, "manifest")
    assert [entry["availability"] for entry in manifest["authorities"]] == [
        "accepted",
        "unavailable",
        "rejected",
        "rejected",
    ]


def _write_manifest(repo_root: Path, data: bytes) -> Path:
    dest = repo_root / "oap" / "evidence" / "005-ar" / "manifest.json"
    write_source(dest, data)
    return dest


def test_audit_replaces_pinned_008_a_manifest_once(
    repo_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exporter = import_exporter()
    # Synthetic pinned identity: only this exact pre-existing manifest is
    # eligible for the one-shot replacement.
    pinned_bytes = b'{"schema": "oap-008-a-durable-evidence-manifest-v1", "synthetic": true}\n'
    monkeypatch.setattr(
        contracts,
        "OBJECTIVE_008_A_MANIFEST_SHA256",
        hashlib.sha256(pinned_bytes).hexdigest(),
    )
    monkeypatch.setattr(contracts, "OBJECTIVE_008_A_MANIFEST_BYTE_COUNT", len(pinned_bytes))
    _write_manifest(repo_root, pinned_bytes)
    summary = exporter.run_audit(repo_root, synthetic_authorities(tmp_path))
    assert [entry["availability"] for entry in summary["authorities"]] == [
        "accepted",
        "accepted",
        "accepted",
        "accepted",
    ]
    manifest_path = repo_root / "oap" / "evidence" / "005-ar" / "manifest.json"
    assert manifest_path.read_bytes() != pinned_bytes
    validate_value(contracts.MANIFEST_SPEC, json.loads(manifest_path.read_bytes()), "manifest")
    # Second run: the manifest no longer matches the pinned identity, so
    # the audit fails closed and the current manifest is untouched.
    current = manifest_path.read_bytes()
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        exporter.run_audit(repo_root, synthetic_authorities(tmp_path))
    assert exc_info.value.rejection_class == "destination_bytes_mismatch"
    assert manifest_path.read_bytes() == current


def test_audit_refuses_non_pinned_preexisting_manifest(
    repo_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exporter = import_exporter()
    foreign = b'{"unknown": "manifest"}\n'
    monkeypatch.setattr(contracts, "OBJECTIVE_008_A_MANIFEST_SHA256", "f" * 64)
    monkeypatch.setattr(contracts, "OBJECTIVE_008_A_MANIFEST_BYTE_COUNT", len(foreign))
    _write_manifest(repo_root, foreign)
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        exporter.run_audit(repo_root, synthetic_authorities(tmp_path))
    assert exc_info.value.rejection_class == "destination_bytes_mismatch"
    assert (repo_root / "oap" / "evidence" / "005-ar" / "manifest.json").read_bytes() == foreign


def test_audit_rerun_verifies_existing_destinations_without_rewrite(
    repo_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exporter = import_exporter()
    authorities = synthetic_authorities(tmp_path)
    first = exporter.run_audit(repo_root, authorities)
    assert [entry["availability"] for entry in first["authorities"]] == [
        "accepted",
        "accepted",
        "accepted",
        "accepted",
    ]
    manifest_bytes = (repo_root / "oap" / "evidence" / "005-ar" / "manifest.json").read_bytes()
    inodes = {
        authority.relative_path: (repo_root / "oap" / "evidence" / authority.relative_path)
        .stat()
        .st_ino
        for authority in authorities
    }
    # Pin the one-shot replacement to the manifest this run just published,
    # then re-run: every destination must be re-verified byte-identical
    # without any write (same inode), and the manifest replaced.
    monkeypatch.setattr(
        contracts,
        "OBJECTIVE_008_A_MANIFEST_SHA256",
        hashlib.sha256(manifest_bytes).hexdigest(),
    )
    monkeypatch.setattr(contracts, "OBJECTIVE_008_A_MANIFEST_BYTE_COUNT", len(manifest_bytes))
    second = exporter.run_audit(repo_root, authorities)
    assert [entry["availability"] for entry in second["authorities"]] == [
        "accepted",
        "accepted",
        "accepted",
        "accepted",
    ]
    for authority, entry in zip(authorities, second["authorities"], strict=True):
        dest = repo_root / "oap" / "evidence" / authority.relative_path
        assert dest.stat().st_ino == inodes[authority.relative_path]
        assert entry["byte_count"] == dest.stat().st_size
        assert entry["committed_sha256"] == hashlib.sha256(dest.read_bytes()).hexdigest()


def test_audit_destination_bytes_mismatch_refused(repo_root: Path, tmp_path: Path) -> None:
    exporter = import_exporter()
    authorities = synthetic_authorities(tmp_path)
    # A pre-existing destination that does not carry the accepted bytes is
    # a conflict: the audit refuses and the file is never touched.
    first_dest = repo_root / "oap" / "evidence" / authorities[0].relative_path
    write_source(first_dest, b"foreign pre-existing bytes\n")
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        exporter.run_audit(repo_root, authorities)
    assert exc_info.value.rejection_class == "destination_bytes_mismatch"
    assert first_dest.read_bytes() == b"foreign pre-existing bytes\n"


def test_audit_performs_no_external_activity(
    repo_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exporter = import_exporter()

    def explode(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("network, process, or shell activity attempted")

    monkeypatch.setattr(socket, "socket", explode)
    monkeypatch.setattr(socket, "create_connection", explode)
    monkeypatch.setattr(os, "system", explode)
    monkeypatch.setattr(os, "execve", explode)
    summary = exporter.run_audit(repo_root, synthetic_authorities(tmp_path))
    assert [entry["availability"] for entry in summary["authorities"]] == [
        "accepted",
        "accepted",
        "accepted",
        "accepted",
    ]


def test_manifest_rejection_classes_cover_every_helper_class() -> None:
    helper = Path(__file__).resolve().parents[1] / "tests" / "helpers" / "safe_evidence.py"
    source = helper.read_text("utf-8")
    emitted = set(re.findall(r"_reject\(\"([a-z_]+)\"", source))
    privacy = set(re.findall(r"\"(privacy_pattern_[a-z_]+)\"", source))
    expected = emitted | privacy | {"historical_temp_artifact_unavailable_on_this_host"}
    assert expected <= contracts.MANIFEST_REJECTION_CLASSES
    assert "open_key_class_denied" in contracts.MANIFEST_REJECTION_CLASSES


def test_script_imports_are_stdlib_plus_repo_machinery() -> None:
    tree = ast.parse(SCRIPT.read_text("utf-8"))
    allowed_repo = {"tests"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root in allowed_repo or root in sys.stdlib_module_names, alias.name
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            root = (node.module or "").split(".")[0]
            assert root in allowed_repo or root in sys.stdlib_module_names, node.module


def test_historical_authorities_are_the_four_literal_paths() -> None:
    exporter = import_exporter()
    paths = [authority.source for authority in exporter.HISTORICAL_AUTHORITIES]
    assert paths == [
        "/tmp/slaif-005-ar-protected-1024.O7Zsxd/protected-result.json",
        "/tmp/slaif-005-ar-protected.GjMeEO/protected-result.json",
        "/tmp/slaif-005-ar-isolated-fake-1024.aipZdW/isolated-fake-target.json",
        "/tmp/slaif-005-ap-fake-gate.rHO7rQ",
    ]
    roles = [authority.role for authority in exporter.HISTORICAL_AUTHORITIES]
    assert roles == [
        "protected_target",
        "protected_target",
        "fake_target",
        "full_fake_gate",
    ]
    relative_paths = [authority.relative_path for authority in exporter.HISTORICAL_AUTHORITIES]
    assert relative_paths == [
        "005-ar/protected_final_1024_success.json",
        "005-ar/protected_32_token_diagnostic.json",
        "005-ar/fake_isolated_target_1024.json",
        "005-ar/reused_ap37_fake_gate.json",
    ]
    authority_roles = [authority.authority_role for authority in exporter.HISTORICAL_AUTHORITIES]
    assert authority_roles == [
        "protected_final_1024_success",
        "protected_32_token_diagnostic",
        "fake_isolated_target",
        "fake_ap37_gate_authority",
    ]
    for authority in exporter.HISTORICAL_AUTHORITIES:
        assert authority.relative_path.startswith("005-ar/")
        assert re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,255}", authority.relative_path)


def test_cli_export_unknown_role_is_refused(repo_root: Path, tmp_path: Path) -> None:
    raw = materialize_raw("fake_target")
    source = tmp_path / "src" / "fake.json"
    write_source(source, raw)
    result = run_cli(
        [
            "--repo-root",
            str(repo_root),
            "export",
            "--source",
            str(source),
            "--role",
            "manifest",
            "--destination",
            "005-ar/x.json",
            "--mode",
            "exact",
        ]
    )
    # The manifest role is not an exportable source role: argparse refuses.
    assert result.returncode != 0


def test_acceptance_reuse_is_single_meaning() -> None:
    """The audit path and the export path share one validator entry point."""
    raw = materialize_raw("protected_target")
    spec = contracts.result_spec_for_role("protected_target")
    preflight = contracts.preflight_spec_for_role("protected_target")
    document, sha = accept_evidence_bytes(raw, spec, preflight_spec=preflight)
    assert sha == hashlib.sha256(raw).hexdigest()
    assert isinstance(document, dict)
    # Unsafe bytes reject through the same shared entry point.
    with pytest.raises(UnsafeEvidenceError) as exc_info:
        accept_evidence_bytes(raw + b'\n{"extra": "line"}', spec, preflight_spec=preflight)
    assert exc_info.value.rejection_class == "decode_extra_lines"
