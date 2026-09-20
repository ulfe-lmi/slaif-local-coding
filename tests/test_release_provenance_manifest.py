"""Regeneration/drift gate for the release provenance manifest (order 009-a,
E3; order 013-a, workstream A: state-aware schema v3; order 013-i: schema
v4 pre-freeze candidate state + recorded build toolchain; order 013-j:
schema v5 — exact source-commit binding with the mechanical source-input
map, hermetic build-environment pins, and exact Python identity scope).

Rebuilds the CLEAN RECORDED SOURCE COMMIT A (`git archive A`), regenerates
the manifest from those inputs, and fails on any drift against the committed
manifest or on forbidden content. `generated_from.git_commit` is the exact
source commit A the artifacts were built from (order 013-j, J4): the
regeneration proves the committed manifest is a fixed point of the recorded
source, and `source_inputs` binds the wheel/sdist/OCI/configuration inputs
mechanically. The recorded `build.python` observed scope (exact
interpreters the artifacts were observed on) is a generation-time fact and
is normalized away from the equality check, like `generated_from.git_commit`.

Order 013-i, C11 (state law retained): the gates are STATE-CONDITIONAL on
the publication records: pre-freeze (neither record) vs RC-published
(packaging/rc_record.json, schema slaif-rc-record-v2 — order 013-j, J5) vs
final-published (packaging/release_record.json, schema
slaif-release-record-v1). A published RC must never imply
final_public_release=true.
"""

from __future__ import annotations

import importlib.util
import json
import platform
import re
import shutil
import subprocess
import types
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "release_provenance_manifest.py"
MANIFEST = REPO_ROOT / "packaging" / "release_provenance_manifest.json"
SCHEMA = REPO_ROOT / "packaging" / "release_provenance_manifest.schema.json"
RECORD = REPO_ROOT / "packaging" / "release_record.json"
RC_RECORD = REPO_ROOT / "packaging" / "rc_record.json"

# Order 013-i, C10 + order 013-j, J3 + order 013-k, K2: the input set
# (RC source-review documentation, hermetic six-pin build environment,
# rendered handoff exclusion, and the 013-k K1-K3 source corrections whose
# README change moves the wheel METADATA) is an explicitly authorized input
# change, so the accepted wheel hash moves to the 013-k identity. The
# historical wheel 879baa3a... is NOT reused for the RC.
ACCEPTED_WHEEL_SHA256 = "2f1b7fa1afb7845059e150b6400977df2e957506da4228dbaa6454dff97db935"

RELEASE_RECORD_KEYS = {
    "schema",
    "version",
    "git_tag",
    "image_source_commit",
    "oci_image_reference",
    "oci_image_digest",
    "oci_tags",
    "published_at",
    "publication_workflow",
    "publication_workflow_run_id",
}
RC_RECORD_KEYS = {
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
RELEASE_SECTION_KEYS = {
    "version",
    "git_tag",
    "git_tag_target",
    "image_source_commit",
    "oci_image_digest",
    "oci_tags",
    "published_at",
    "publication_workflow_run_id",
}


def _load_generator() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("release_provenance_manifest", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load manifest generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def generator() -> types.ModuleType:
    return _load_generator()


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
def source_commit_a() -> str:
    """The EXACT recorded source commit A (order 013-j, J4)."""
    committed = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return str(committed["generated_from"]["git_commit"])


@pytest.fixture(scope="module")
def regenerated(
    tmp_path_factory: pytest.TempPathFactory, source_commit_a: str
) -> dict[str, object]:
    if shutil.which("uv") is None:
        pytest.fail("uv is required to build artifacts for the manifest gate")
    # Order 013-j, J4: rebuild the CLEAN RECORDED SOURCE COMMIT A, not the
    # working tree: git archive A -> extract -> uv build -> regenerate.
    work = tmp_path_factory.mktemp("clean-A")
    tree = work / "tree"
    tree.mkdir()
    archive_path = work / "archive.tar"
    archive = subprocess.run(
        ["git", "archive", "--output", str(archive_path), source_commit_a],
        cwd=REPO_ROOT,
        capture_output=True,
        timeout=300,
    )
    assert archive.returncode == 0, archive.stderr.decode()
    tarfile = subprocess.run(
        ["tar", "-x", "-f", str(archive_path), "-C", str(tree)],
        capture_output=True,
        timeout=300,
    )
    assert tarfile.returncode == 0, tarfile.stderr.decode()
    dist = tmp_path_factory.mktemp("dist")
    result = subprocess.run(
        ["uv", "build", "--out-dir", str(dist)],
        cwd=tree,
        capture_output=True,
        timeout=600,
    )
    assert result.returncode == 0, result.stderr.decode()
    module = _load_generator()
    # The regeneration is observed on the exact running interpreter: the
    # recorded observed scope is a generation-time fact (normalized away by
    # _strip_git for the equality gate) and must be non-empty per schema v5.
    built: dict[str, object] = module.build_manifest(
        REPO_ROOT,
        dist,
        source_commit=source_commit_a,
        tree=tree,
        observed_build_pythons=[platform.python_version()],
    )
    return built


def _rc_record_present() -> bool:
    return RC_RECORD.is_file()


def _final_record_present() -> bool:
    return RECORD.is_file()


def _state() -> str:
    if _rc_record_present():
        return "rc"
    if _final_record_present():
        return "final"
    return "pre_freeze"


def _committed() -> dict[str, object]:
    data: dict[str, object] = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return data


def _record() -> dict[str, object]:
    data: dict[str, object] = json.loads(RECORD.read_text(encoding="utf-8"))
    return data


def _rc_record() -> dict[str, object]:
    data: dict[str, object] = json.loads(RC_RECORD.read_text(encoding="utf-8"))
    return data


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)


def _strip_git(data: dict[str, object]) -> dict[str, object]:
    """Normalize the generation-time facts away from the equality check.

    `generated_from.git_commit` is the recorded source A (exact by
    construction; the regeneration rebuilds from it). The
    `build.python` OBSERVED SCOPE (exact interpreters the recorded
    artifacts were observed on) is likewise a generation-time fact, not a
    build-input fact: the regenerated artifacts are compared on every
    input-derived value, and the wheel bytes themselves (the
    patch-independence claim) are proven by the clean-build equality.
    """
    data = json.loads(json.dumps(data))
    generated = cast("dict[str, object]", data["generated_from"])
    generated["git_commit"] = None
    python = cast("dict[str, object]", cast("dict[str, object]", data["build"])["python"])
    python["observed_exact"] = None
    python["wheel_patch_independent"] = None
    return data


def test_manifest_and_schema_exist() -> None:
    assert MANIFEST.is_file()
    assert SCHEMA.is_file()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$id"] == "slaif-release-provenance-v5"
    committed = _committed()
    assert committed["schema"] == "slaif-release-provenance-v5"
    assert committed["schema_version"] == 5


def test_committed_manifest_matches_regenerated(regenerated: dict[str, object]) -> None:
    assert _strip_git(_committed()) == _strip_git(regenerated)


def test_committed_git_commit_is_ancestor_of_head() -> None:
    committed = _committed()
    generated = cast("dict[str, object]", committed["generated_from"])
    git_commit = str(generated["git_commit"])
    assert re.fullmatch(r"[0-9a-f]{40}", git_commit)
    exists = _git("cat-file", "-e", git_commit)
    if exists.returncode != 0:
        pytest.fail("committed manifest git_commit is not resolvable in this checkout")
    head = _git("rev-parse", "HEAD").stdout.strip()
    if git_commit == head:
        return
    is_ancestor = _git("merge-base", "--is-ancestor", git_commit, head)
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
    committed = _committed()
    assert committed["status"] == {
        "deployment_qualified": "disposable-environment-only",
        "cutover_performed": False,
        "rc_published": _rc_record_present(),
        "final_public_release": _final_record_present(),
    }
    # Order 013-i, C11: an RC record must never imply a final release.
    if _rc_record_present():
        assert committed["status"]["final_public_release"] is False
        assert "release" not in committed


def test_regenerated_manifest_matches_schema_shape(regenerated: dict[str, object]) -> None:
    # Closed top-level key set (mirrors the schema's additionalProperties=false);
    # `release` is present iff the FINAL release record exists (order 013-a, R2;
    # order 013-i: the RC state has no release section).
    expected_keys = {
        "schema",
        "schema_version",
        "objective",
        "generated_from",
        "gateway_peer",
        "runtime",
        "artifacts",
        "build",
        "source_inputs",
        "candidate",
        "templates",
        "oci",
        "reference_compatibility",
        "status",
        "limitations",
    }
    if _final_record_present():
        expected_keys.add("release")
    assert set(regenerated) == expected_keys
    artifacts = cast("dict[str, dict[str, object]]", regenerated["artifacts"])
    assert set(artifacts) == {"wheel", "sdist"}
    for artifact in artifacts.values():
        assert set(artifact) == {"name", "sha256", "size_bytes", "entry_count"}
        assert re.fullmatch(r"[0-9a-f]{64}", str(artifact["sha256"]))
    # Order 013-i, C9: the recorded build toolchain is the pinned identity.
    build = cast("dict[str, object]", regenerated["build"])
    assert set(build) == {"backend", "build_environment", "uv_version", "python"}
    backend = cast("dict[str, object]", build["backend"])
    assert backend == {"name": "hatchling", "version": "1.32.0"}
    assert set(cast("dict[str, object]", build["build_environment"])) == {
        "hatchling",
        "packaging",
        "pathspec",
        "pluggy",
        "tomlkit",
        "trove-classifiers",
    }
    assert build["uv_version"] == "0.12.5"
    # Order 013-j, J3: exact Python identity scope (never a bare "3.12").
    python = cast("dict[str, object]", build["python"])
    assert set(python) == {"runtime_requirement", "observed_exact", "wheel_patch_independent"}
    assert python["runtime_requirement"] == ">=3.12"
    observed = cast("list[str]", python["observed_exact"])
    assert observed and all(re.fullmatch(r"\d+\.\d+\.\d+", v) for v in observed)
    assert python["wheel_patch_independent"] is (len(set(observed)) >= 2)
    # Order 013-j, J4: the mechanical source-input map is present.
    source_inputs = cast("dict[str, object]", regenerated["source_inputs"])
    assert source_inputs
    for value in source_inputs.values():
        assert re.fullmatch(r"[0-9a-f]{64}", str(value))
    # Order 013-i, C11/D13: explicit RC candidate identity, separate from
    # the final release.
    candidate = cast("dict[str, object]", regenerated["candidate"])
    assert set(candidate) == {
        "rc_identifier",
        "state",
        "private_registry_auth_required",
        "final_public_release",
        "cutover_performed",
    }
    assert candidate["rc_identifier"] == "0.1.0-rc2"
    assert candidate["private_registry_auth_required"] is True
    assert candidate["final_public_release"] is False
    assert candidate["cutover_performed"] is False
    assert candidate["state"] == ("rc_published" if _rc_record_present() else "pre_freeze")
    peer = cast("dict[str, object]", regenerated["gateway_peer"])
    assert set(peer) == {"repository", "commit", "server_module", "client_module"}
    assert peer["repository"] == "ulfe-lmi/slaif-api-gateway"
    assert re.fullmatch(r"[0-9a-f]{40}", str(peer["commit"]))
    compat = cast("dict[str, object]", regenerated["reference_compatibility"])
    client = cast("dict[str, object]", compat["codex_client"])
    assert compat["model_name"] == "qwen3.8-27b"
    assert client["version"] == "0.149.0"
    assert regenerated["limitations"], "limitations must not be empty"
    oci = cast("dict[str, object]", regenerated["oci"])
    assert set(oci) == {
        "image_reference",
        "tag_convention",
        "candidate_tag",
        "base_image",
        "build_base_image",
        "build_tool_image",
        "dockerfile_sha256",
        "compose_sha256",
        "dockerignore_sha256",
        "wheel_sha256",
        "image_digest",
        "published",
        "labels",
    }
    assert oci["image_reference"] == "ghcr.io/ulfe-lmi/slaif-local-coding"
    assert oci["candidate_tag"] == "0.1.0-rc2"
    if _rc_record_present():
        rc = _rc_record()
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", str(oci["image_digest"]))
        assert oci["image_digest"] == rc["oci_image_digest"]
        assert oci["published"] is True
        assert "release" not in regenerated
    elif _final_record_present():
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", str(oci["image_digest"]))
        assert oci["published"] is True
        release = cast("dict[str, object]", regenerated["release"])
        assert set(release) == RELEASE_SECTION_KEYS
    else:
        assert oci["image_digest"] is None
        assert oci["published"] is False


def test_manifest_fails_on_injected_drift(regenerated: dict[str, object]) -> None:
    committed = _committed()
    drifted = json.loads(json.dumps(regenerated))
    wheel = cast("dict[str, object]", cast("dict[str, object]", drifted["artifacts"])["wheel"])
    wheel["sha256"] = "0" * 64
    assert drifted != committed


# ---------------------------------------------------------------------------
# Objective 011-a workstream E3 (schema/hash cross-checks, objective field,
# status fields) — v4 state-aware (order 013-i).
# ---------------------------------------------------------------------------


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dockerfile_from_lines() -> dict[str, tuple[str, str]]:
    """stage -> (name, sha256:<digest>) parsed from the Dockerfile."""
    found: dict[str, tuple[str, str]] = {}
    for line in (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^FROM\s+(\S+?)@sha256:([0-9a-f]{64})\s+AS\s+([A-Za-z0-9_-]+)\s*$", line)
        if m:
            found[m.group(3)] = (m.group(1), "sha256:" + m.group(2))
    return found


def test_objective_field_records_producing_objective() -> None:
    # In ALL states the objective constant records the producing round.
    committed = _committed()
    assert committed["objective"] == "013-m"


def test_status_fields_state_conditional() -> None:
    # v4: status constants are state-conditional on the publication records.
    committed = _committed()
    oci = cast("dict[str, object]", committed["oci"])
    status = cast("dict[str, object]", committed["status"])
    assert status["deployment_qualified"] == "disposable-environment-only"
    assert status["cutover_performed"] is False
    state = _state()
    assert status["rc_published"] is (state == "rc")
    assert status["final_public_release"] is (state == "final")
    if state == "rc":
        record = _rc_record()
        assert oci["published"] is True
        assert oci["image_digest"] == record["oci_image_digest"]
    elif state == "final":
        record = _record()
        assert oci["published"] is True
        assert oci["image_digest"] == record["oci_image_digest"]
    else:
        assert oci["published"] is False
        assert oci["image_digest"] is None


def test_oci_hash_cross_checks_against_committed_files() -> None:
    committed = _committed()
    oci = cast("dict[str, object]", committed["oci"])
    artifacts = cast("dict[str, dict[str, object]]", committed["artifacts"])
    # Wheel cross-reference (B8/C2 binding): the OCI section must reference
    # exactly the recorded wheel.
    assert oci["wheel_sha256"] == artifacts["wheel"]["sha256"]
    # R5 byte-identity law: the accepted wheel hash remains exact
    # (order 013-i: explicitly authorized new identity).
    assert artifacts["wheel"]["sha256"] == ACCEPTED_WHEEL_SHA256
    # OCI build inputs must match the committed files byte-for-byte.
    assert oci["dockerfile_sha256"] == _sha256_file(REPO_ROOT / "Dockerfile")
    assert oci["compose_sha256"] == _sha256_file(REPO_ROOT / "compose.yaml")
    assert oci["dockerignore_sha256"] == _sha256_file(REPO_ROOT / ".dockerignore")
    # Base images pinned by digest and consistent with the Dockerfile.
    from_lines = _dockerfile_from_lines()
    base = cast("dict[str, object]", oci["base_image"])
    build_base = cast("dict[str, object]", oci["build_base_image"])
    build_tool = cast("dict[str, object]", oci["build_tool_image"])
    assert (base["name"], base["digest"]) == from_lines["runtime"]
    assert (build_base["name"], build_base["digest"]) == from_lines["build"]
    assert (build_tool["name"], build_tool["digest"]) == from_lines["uv-provider"]
    # Label set bound to the same facts.
    labels = cast("dict[str, object]", oci["labels"])
    assert labels["slaif-local-coding.wheel.sha256"] == artifacts["wheel"]["sha256"]
    runtime = cast("dict[str, object]", committed["runtime"])
    assert labels["slaif-local-coding.package.version"] == runtime["package_version"]
    assert labels["org.opencontainers.image.version"] == runtime["package_version"]
    peer = cast("dict[str, object]", committed["gateway_peer"])
    assert labels["slaif-local-coding.gateway.peer.sha"] == peer["commit"]
    state = _state()
    if state == "rc":
        expected_qualification = "rc-candidate-0.1.0-rc2; private; not final release"
    elif state == "final":
        expected_qualification = "mvp-release-0.1.0"
    else:
        expected_qualification = "disposable-qualification-only; not released"
    assert labels["slaif-local-coding.qualification"] == expected_qualification


def test_committed_manifest_conforms_to_schema_v5_structure() -> None:
    # Structural v5 conformance without a new dependency (dependency freeze):
    # closed key sets and fixed constants, mirroring the schema's
    # additionalProperties=false and const/enum entries.
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$id"] == "slaif-release-provenance-v5"
    committed = _committed()
    expected_top = set(schema["required"])
    if _final_record_present():
        expected_top.add("release")
    assert set(committed) == expected_top
    oci = cast("dict[str, object]", committed["oci"])
    assert set(oci) == set(schema["properties"]["oci"]["required"])
    assert schema["properties"]["oci"]["properties"]["image_reference"]["const"] == (
        "ghcr.io/ulfe-lmi/slaif-local-coding"
    )
    assert schema["properties"]["oci"]["properties"]["candidate_tag"]["const"] == "0.1.0-rc2"
    assert schema["properties"]["oci"]["properties"]["published"]["enum"] == [False, True]
    assert schema["properties"]["status"]["properties"]["rc_published"]["enum"] == [False, True]
    assert schema["properties"]["status"]["properties"]["final_public_release"]["enum"] == [
        False,
        True,
    ]
    assert schema["properties"]["candidate"]["properties"]["final_public_release"]["const"] is False
    assert (
        schema["properties"]["build"]["properties"]["backend"]["properties"]["version"]["const"]
        == "1.32.0"
    )
    assert "source_inputs" in schema["required"]
    python_def = schema["properties"]["build"]["properties"]["python"]
    assert python_def["type"] == "object"
    assert python_def["properties"]["runtime_requirement"]["const"] == ">=3.12"
    labels = cast("dict[str, object]", oci["labels"])
    # labels are defined in $defs.oci_labels (referenced from oci.labels).
    labels_def = schema["$defs"]["oci_labels"]
    assert set(labels) == set(labels_def["properties"])
    if _final_record_present():
        release_def = schema["properties"]["release"]
        assert set(release_def["required"]) == RELEASE_SECTION_KEYS
        assert release_def["additionalProperties"] is False


# ---------------------------------------------------------------------------
# Objective 013-a workstream A (R4): final release record gates and the
# published-state cross-consistency / tamper tests.
# ---------------------------------------------------------------------------


def _valid_record_template() -> dict[str, object]:
    if RECORD.is_file():
        data: dict[str, object] = json.loads(json.dumps(_record()))
        return data
    source = "a" * 40
    return {
        "schema": "slaif-release-record-v1",
        "version": "0.1.0",
        "git_tag": "v0.1.0",
        "image_source_commit": source,
        "oci_image_reference": "ghcr.io/ulfe-lmi/slaif-local-coding",
        "oci_image_digest": "sha256:" + "b" * 64,
        "oci_tags": ["0.1.0", f"sha-{source}"],
        "published_at": "2026-09-17T00:00:00Z",
        "publication_workflow": "release-image.yml",
        "publication_workflow_run_id": 1,
    }


def test_release_record_closed_key_set_and_value_classes() -> None:
    if not _final_record_present():
        return  # pre-final state: the final record is absent by design
    record = _record()
    assert set(record) == RELEASE_RECORD_KEYS
    assert record["schema"] == "slaif-release-record-v1"
    assert record["version"] == "0.1.0"
    assert record["git_tag"] == "v0.1.0"
    assert re.fullmatch(r"[0-9a-f]{40}", str(record["image_source_commit"]))
    assert record["oci_image_reference"] == "ghcr.io/ulfe-lmi/slaif-local-coding"
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", str(record["oci_image_digest"]))
    source = str(record["image_source_commit"])
    assert record["oci_tags"] == ["0.1.0", f"sha-{source}"]
    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", str(record["published_at"])
    )
    assert record["publication_workflow"] == "release-image.yml"
    run_id = record["publication_workflow_run_id"]
    assert run_id is None or (
        isinstance(run_id, int) and not isinstance(run_id, bool) and run_id > 0
    )


def test_publish_state_source_commit_binding() -> None:
    # R4(a): final record value == release.image_source_commit ==
    # generated_from.git_commit, an ancestor of HEAD.
    if not _final_record_present():
        return
    committed = _committed()
    record = _record()
    release = cast("dict[str, object]", committed["release"])
    source = str(record["image_source_commit"])
    assert release["image_source_commit"] == source
    assert release["git_tag_target"] == source
    generated = cast("dict[str, object]", committed["generated_from"])
    assert generated["git_commit"] == source
    head = _git("rev-parse", "HEAD").stdout.strip()
    if source != head:
        is_ancestor = _git("merge-base", "--is-ancestor", source, head)
        assert is_ancestor.returncode == 0, "release image_source_commit is not an ancestor of HEAD"


def test_publish_state_build_inputs_unchanged_since_source() -> None:
    # R4(b): for every OCI build input, the Git blob at the image source
    # commit equals the blob at HEAD (the recorded image really corresponds
    # to the recorded manifest's build inputs).
    if not _final_record_present():
        return
    record = _record()
    source = str(record["image_source_commit"])
    head = _git("rev-parse", "HEAD").stdout.strip()
    for path in ("Dockerfile", "compose.yaml", "compose.build.yaml", ".dockerignore"):
        at_source = _git("rev-parse", f"{source}:{path}").stdout.strip()
        at_head = _git("rev-parse", f"HEAD:{path}").stdout.strip()
        assert at_source, f"build input {path} missing at {source}"
        assert at_source == at_head, f"build input {path} changed between S and HEAD"
    assert head != ""


def test_publish_state_digest_tag_label_binding() -> None:
    # R4(c): digest, tag pair, and the wheel/qualification label bindings.
    if not _final_record_present():
        return
    committed = _committed()
    record = _record()
    release = cast("dict[str, object]", committed["release"])
    oci = cast("dict[str, object]", committed["oci"])
    artifacts = cast("dict[str, dict[str, object]]", committed["artifacts"])
    labels = cast("dict[str, object]", oci["labels"])
    digest = str(record["oci_image_digest"])
    source = str(record["image_source_commit"])
    assert oci["image_digest"] == digest
    assert release["oci_image_digest"] == digest
    assert release["oci_tags"] == ["0.1.0", f"sha-{source}"]
    assert labels["slaif-local-coding.qualification"] == "mvp-release-0.1.0"
    assert artifacts["wheel"]["sha256"] == ACCEPTED_WHEEL_SHA256
    assert labels["slaif-local-coding.wheel.sha256"] == artifacts["wheel"]["sha256"]


def _flip_digest(digest: str) -> str:
    body = digest.removeprefix("sha256:")
    last = "1" if body[-1] != "1" else "0"
    return "sha256:" + body[:-1] + last


def test_tampered_record_digest_fails_gate(regenerated: dict[str, object]) -> None:
    # R4(d): mutating the recorded digest must fail the gate.
    if not _final_record_present():
        return
    committed = _committed()
    tampered = json.loads(json.dumps(committed))
    release = cast("dict[str, object]", tampered["release"])
    release["oci_image_digest"] = _flip_digest(str(release["oci_image_digest"]))
    assert _strip_git(tampered) != _strip_git(regenerated)


def test_tampered_manifest_release_section_fails_gate(regenerated: dict[str, object]) -> None:
    # R4(d): mutating the manifest release section must fail the gate.
    if not _final_record_present():
        return
    committed = _committed()
    tampered = json.loads(json.dumps(committed))
    release = cast("dict[str, object]", tampered["release"])
    release["git_tag_target"] = "0" * 40
    assert _strip_git(tampered) != _strip_git(regenerated)


def test_tampered_release_tag_fails_gate(regenerated: dict[str, object]) -> None:
    # R4(d): mutating a release tag must fail the gate.
    if not _final_record_present():
        return
    committed = _committed()
    tampered = json.loads(json.dumps(committed))
    release = cast("dict[str, object]", tampered["release"])
    tags = cast("list[str]", release["oci_tags"])
    tags[0] = "0.1.1"
    assert _strip_git(tampered) != _strip_git(regenerated)


def test_record_loader_rejects_drift(generator: types.ModuleType, tmp_path: Path) -> None:
    # R4(d) at the record level: the generator's strict loader rejects any
    # tampered record (extra keys, wrong schema, malformed values).
    base = _valid_record_template()

    def expect_error(mutate: Callable[[dict[str, object]], None], index: int) -> None:
        fake = tmp_path / f"repo-{index}"
        (fake / "packaging").mkdir(parents=True)
        record = json.loads(json.dumps(base))
        mutate(record)
        (fake / "packaging" / "release_record.json").write_text(
            json.dumps(record), encoding="utf-8"
        )
        with pytest.raises(RuntimeError):
            generator.load_release_record(fake)

    def add_key(record: dict[str, object]) -> None:
        record["extra"] = "x"

    def wrong_schema(record: dict[str, object]) -> None:
        record["schema"] = "slaif-release-record-v0"

    def bad_digest(record: dict[str, object]) -> None:
        record["oci_image_digest"] = "sha256:zzz"

    def bad_tags(record: dict[str, object]) -> None:
        tags = cast(list[str], record["oci_tags"])
        tags[1] = "sha-deadbeef"

    def bad_published_at(record: dict[str, object]) -> None:
        record["published_at"] = "17/09/2026 12:00"

    def bad_workflow(record: dict[str, object]) -> None:
        record["publication_workflow"] = "ci.yml"

    def bad_run_id(record: dict[str, object]) -> None:
        record["publication_workflow_run_id"] = -1

    def bool_run_id(record: dict[str, object]) -> None:
        record["publication_workflow_run_id"] = True

    for index, mutate in enumerate(
        (
            add_key,
            wrong_schema,
            bad_digest,
            bad_tags,
            bad_published_at,
            bad_workflow,
            bad_run_id,
            bool_run_id,
        )
    ):
        expect_error(mutate, index)
    # The unmutated template must load cleanly.
    fake = tmp_path / "repo-ok"
    (fake / "packaging").mkdir(parents=True)
    (fake / "packaging" / "release_record.json").write_text(json.dumps(base), encoding="utf-8")
    loaded = generator.load_release_record(fake)
    assert loaded == base


# ---------------------------------------------------------------------------
# Order 013-i, C11/C12: RC record gates (strict loader + tamper tests).
# ---------------------------------------------------------------------------


FIXTURE_DOCKERFILE = (
    "FROM ghcr.io/astral-sh/uv:0.12.5@sha256:"
    "e85be844203885286c60ffad8a858d48afb6c5a5c237ca0e67f12e74b8f174b1 AS uv-provider\n"
    "FROM python:3.12-slim-bookworm@sha256:"
    "782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254 AS build\n"
    "FROM python:3.12-slim-bookworm@sha256:"
    "782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254 AS runtime\n"
)


def _fixture_base_images() -> dict[str, dict[str, str]]:
    import tempfile
    from pathlib import Path as _Path

    with tempfile.TemporaryDirectory() as tmp:
        repo = _Path(tmp)
        (repo / "Dockerfile").write_text(FIXTURE_DOCKERFILE, encoding="utf-8")
        return {
            stage: {"name": fact["name"], "digest": fact["digest"]}
            for stage, fact in _load_generator()._dockerfile_base_images(repo).items()
        }


def _valid_rc_record_template() -> dict[str, object]:
    if RC_RECORD.is_file():
        data: dict[str, object] = json.loads(json.dumps(_rc_record()))
        return data
    source = "a" * 40
    return {
        "schema": "slaif-rc-record-v2",
        "rc_identifier": "0.1.0-rc2",
        "product_version": "0.1.0",
        "image_source_commit": source,
        "oci_image_reference": "ghcr.io/ulfe-lmi/slaif-local-coding",
        "oci_image_digest": "sha256:" + "c" * 64,
        "oci_tags": ["0.1.0-rc2", f"sha-{source}"],
        "published_at": "2026-09-20T00:00:00Z",
        "publication_workflow": "release-image.yml",
        "publication_workflow_run_id": 1,
        "workflow_head_sha": "e" * 40,
        "private_registry_auth_required": True,
        "final_public_release": False,
        "cutover_performed": False,
        "wheel_sha256": "d" * 64,
        "dependency_lock_sha256": "e" * 64,
        "gateway_authority_sha": "f" * 40,
        "build_environment": {
            "hatchling": "1.32.0",
            "packaging": "26.3",
            "pathspec": "1.1.1",
            "pluggy": "1.6.0",
            "tomlkit": "0.15.1",
            "trove-classifiers": "2026.6.1.19",
        },
        "build_toolchain": {
            "backend": "hatchling==1.32.0",
            "uv": "0.12.5",
            "python": "3.12",
        },
        "base_images": _fixture_base_images(),
        "image_platform": "linux/amd64",
        "source_input_hashes": {"README.md": "1" * 64},
        "deployment_assumptions": (
            "linux-docker-engine-compose-v2;host-network-mode;"
            "private-same-host-upstream;separate-gateway;loopback-default-bind"
        ),
    }


def test_rc_record_closed_key_set_and_value_classes() -> None:
    if not _rc_record_present():
        return  # pre-RC state: the RC record is absent by design
    record = _rc_record()
    assert set(record) == RC_RECORD_KEYS
    assert record["schema"] == "slaif-rc-record-v2"
    assert record["rc_identifier"] == "0.1.0-rc2"
    assert record["product_version"] == "0.1.0"
    assert re.fullmatch(r"[0-9a-f]{40}", str(record["image_source_commit"]))
    assert record["oci_image_reference"] == "ghcr.io/ulfe-lmi/slaif-local-coding"
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", str(record["oci_image_digest"]))
    source = str(record["image_source_commit"])
    assert record["oci_tags"] == ["0.1.0-rc2", f"sha-{source}"]
    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", str(record["published_at"])
    )
    assert record["publication_workflow"] == "release-image.yml"
    run_id = record["publication_workflow_run_id"]
    assert run_id is None or (
        isinstance(run_id, int) and not isinstance(run_id, bool) and run_id > 0
    )
    assert record["private_registry_auth_required"] is True
    # A published RC must never imply a final release or a cutover.
    assert record["final_public_release"] is False
    assert record["cutover_performed"] is False
    assert re.fullmatch(r"[0-9a-f]{64}", str(record["wheel_sha256"]))
    assert re.fullmatch(r"[0-9a-f]{64}", str(record["dependency_lock_sha256"]))
    assert re.fullmatch(r"[0-9a-f]{40}", str(record["gateway_authority_sha"]))
    assert record["build_toolchain"] == {
        "backend": "hatchling==1.32.0",
        "uv": "0.12.5",
        "python": "3.12",
    }
    assert re.fullmatch(r"[0-9a-f]{40}", str(record["workflow_head_sha"]))
    assert record["build_environment"] == {
        "hatchling": "1.32.0",
        "packaging": "26.3",
        "pathspec": "1.1.1",
        "pluggy": "1.6.0",
        "tomlkit": "0.15.1",
        "trove-classifiers": "2026.6.1.19",
    }
    assert record["image_platform"] == "linux/amd64"
    assert record["source_input_hashes"]
    for value in cast("dict[str, object]", record["source_input_hashes"]).values():
        assert re.fullmatch(r"[0-9a-f]{64}", str(value))


def test_rc_state_source_commit_binding() -> None:
    # Order 013-i, C11: the RC record's source commit must be an ancestor of
    # HEAD and the manifest must carry the recorded digest (no release
    # section in the RC state).
    if not _rc_record_present():
        return
    committed = _committed()
    record = _rc_record()
    source = str(record["image_source_commit"])
    head = _git("rev-parse", "HEAD").stdout.strip()
    if source != head:
        is_ancestor = _git("merge-base", "--is-ancestor", source, head)
        assert is_ancestor.returncode == 0, "RC image_source_commit is not an ancestor of HEAD"
    oci = cast("dict[str, object]", committed["oci"])
    assert oci["image_digest"] == record["oci_image_digest"]
    assert oci["published"] is True
    assert "release" not in committed
    status = cast("dict[str, object]", committed["status"])
    assert status["rc_published"] is True
    assert status["final_public_release"] is False
    candidate = cast("dict[str, object]", committed["candidate"])
    assert candidate["state"] == "rc_published"
    # The RC record binds the manifest's wheel hash.
    artifacts = cast("dict[str, dict[str, object]]", committed["artifacts"])
    assert record["wheel_sha256"] == artifacts["wheel"]["sha256"]
    peer = cast("dict[str, object]", committed["gateway_peer"])
    assert record["gateway_authority_sha"] == peer["commit"]


def test_rc_record_loader_rejects_drift(generator: types.ModuleType, tmp_path: Path) -> None:
    # Order 013-i, C11/C12: the generator's strict RC loader rejects any
    # tampered record (extra keys, wrong schema, final/cutover flips, bad
    # toolchain, wrong tags, malformed values).
    base = _valid_rc_record_template()

    def expect_error(mutate: Callable[[dict[str, object]], None], index: int) -> None:
        fake = tmp_path / f"rc-repo-{index}"
        (fake / "packaging").mkdir(parents=True)
        (fake / "Dockerfile").write_text(FIXTURE_DOCKERFILE, encoding="utf-8")
        record = json.loads(json.dumps(base))
        mutate(record)
        (fake / "packaging" / "rc_record.json").write_text(json.dumps(record), encoding="utf-8")
        with pytest.raises(RuntimeError):
            generator.load_rc_record(fake)

    def add_key(record: dict[str, object]) -> None:
        record["extra"] = "x"

    def wrong_schema(record: dict[str, object]) -> None:
        record["schema"] = "slaif-rc-record-v0"

    def wrong_identifier(record: dict[str, object]) -> None:
        record["rc_identifier"] = "0.2.0-rc1"

    def bad_digest(record: dict[str, object]) -> None:
        record["oci_image_digest"] = "sha256:zzz"

    def bad_tags(record: dict[str, object]) -> None:
        tags = cast(list[str], record["oci_tags"])
        tags[0] = "0.1.0"

    def final_release_true(record: dict[str, object]) -> None:
        record["final_public_release"] = True

    def cutover_true(record: dict[str, object]) -> None:
        record["cutover_performed"] = True

    def private_auth_false(record: dict[str, object]) -> None:
        record["private_registry_auth_required"] = False

    def bad_wheel(record: dict[str, object]) -> None:
        record["wheel_sha256"] = "g" * 64

    def bad_toolchain(record: dict[str, object]) -> None:
        toolchain = cast(dict[str, object], record["build_toolchain"])
        toolchain["backend"] = "hatchling==1.99.9"

    def bad_head_sha(record: dict[str, object]) -> None:
        record["workflow_head_sha"] = "e" * 39

    def bad_build_environment(record: dict[str, object]) -> None:
        environment = cast(dict[str, object], record["build_environment"])
        environment["hatchling"] = "1.99.9"

    def bad_base_images(record: dict[str, object]) -> None:
        bases = cast(dict[str, object], record["base_images"])
        runtime = cast(dict[str, object], bases["runtime"])
        runtime["digest"] = "sha256:" + "0" * 64

    def bad_platform(record: dict[str, object]) -> None:
        record["image_platform"] = "linux/arm64"

    def bad_input_hashes(record: dict[str, object]) -> None:
        record["source_input_hashes"] = {"README.md": "g" * 64}

    def bad_published_at(record: dict[str, object]) -> None:
        record["published_at"] = "20/09/2026 12:00"

    def bad_workflow(record: dict[str, object]) -> None:
        record["publication_workflow"] = "ci.yml"

    def bool_run_id(record: dict[str, object]) -> None:
        record["publication_workflow_run_id"] = True

    for index, mutate in enumerate(
        (
            add_key,
            wrong_schema,
            wrong_identifier,
            bad_digest,
            bad_tags,
            final_release_true,
            cutover_true,
            private_auth_false,
            bad_wheel,
            bad_toolchain,
            bad_head_sha,
            bad_build_environment,
            bad_base_images,
            bad_platform,
            bad_input_hashes,
            bad_published_at,
            bad_workflow,
            bool_run_id,
        )
    ):
        expect_error(mutate, index)
    # The unmutated template must load cleanly.
    fake = tmp_path / "rc-repo-ok"
    (fake / "packaging").mkdir(parents=True)
    (fake / "Dockerfile").write_text(FIXTURE_DOCKERFILE, encoding="utf-8")
    (fake / "packaging" / "rc_record.json").write_text(json.dumps(base), encoding="utf-8")
    loaded = generator.load_rc_record(fake)
    assert loaded == base
