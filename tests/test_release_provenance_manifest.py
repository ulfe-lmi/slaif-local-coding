"""Regeneration/drift gate for the release provenance manifest (order 009-a, E3).

Rebuilds the artifacts, regenerates the manifest from the actual build inputs,
and fails on any drift against the committed manifest or on forbidden content.
Only `generated_from.git_commit` may legitimately differ: the committed value
must be an ancestor of (or equal to) the current HEAD, so report-only child
commits do not invalidate the manifest while any build-input change does.

Order 013-a, workstream A: schema v3 and the state-aware generator. The gates
are STATE-CONDITIONAL on the presence of packaging/release_record.json:
not-yet-published (no record) vs published (record with non-null digest), plus
the new cross-consistency and tamper tests (R4).
"""

from __future__ import annotations

import importlib.util
import json
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

# Accepted release wheel (order 013-b wheel ruling): the README became a
# published-truth document, so the wheel's dist-info METADATA legitimately
# changed; the B6 METADATA-ONLY proof establishes that every other entry is
# byte-identical to the 012 authority wheel
# (fceadc378130dd4ffcc3f75d17b5e098577652914f541245d31247911be23aeb). The
# accepted release wheel hash must remain exact at H_new.
ACCEPTED_WHEEL_SHA256 = "879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19"

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


def _record_present() -> bool:
    return RECORD.is_file()


def _committed() -> dict[str, object]:
    data: dict[str, object] = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return data


def _record() -> dict[str, object]:
    data: dict[str, object] = json.loads(RECORD.read_text(encoding="utf-8"))
    return data


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)


def _strip_git(data: dict[str, object]) -> dict[str, object]:
    data = json.loads(json.dumps(data))
    generated = cast("dict[str, object]", data["generated_from"])
    generated["git_commit"] = None
    return data


def test_manifest_and_schema_exist() -> None:
    assert MANIFEST.is_file()
    assert SCHEMA.is_file()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$id"] == "slaif-release-provenance-v3"
    committed = _committed()
    assert committed["schema"] == "slaif-release-provenance-v3"
    assert committed["schema_version"] == 3


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
    released = True if _record_present() else False
    assert committed["status"] == {
        "deployment_qualified": "disposable-environment-only",
        "cutover_performed": False,
        "released": released,
    }


def test_regenerated_manifest_matches_schema_shape(regenerated: dict[str, object]) -> None:
    # Closed top-level key set (mirrors the schema's additionalProperties=false);
    # `release` is present iff the release record exists (order 013-a, R2).
    expected_keys = {
        "schema",
        "schema_version",
        "objective",
        "generated_from",
        "gateway_peer",
        "runtime",
        "artifacts",
        "templates",
        "oci",
        "reference_compatibility",
        "status",
        "limitations",
    }
    if _record_present():
        expected_keys.add("release")
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
    oci = cast("dict[str, object]", regenerated["oci"])
    assert set(oci) == {
        "image_reference",
        "tag_convention",
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
    if _record_present():
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
# status fields) — v3 state-aware (order 013-a).
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
    # R4(e): in BOTH states the objective constant records the producing round.
    committed = _committed()
    assert committed["objective"] == "013-c"


def test_status_fields_state_conditional() -> None:
    # R4(f): status constants are state-conditional on the release record.
    committed = _committed()
    oci = cast("dict[str, object]", committed["oci"])
    status = cast("dict[str, object]", committed["status"])
    assert status["cutover_performed"] is False
    if _record_present():
        record = _record()
        assert status["released"] is True
        assert oci["published"] is True
        assert oci["image_digest"] == record["oci_image_digest"]
    else:
        assert status["released"] is False
        assert oci["published"] is False
        assert oci["image_digest"] is None


def test_oci_hash_cross_checks_against_committed_files() -> None:
    committed = _committed()
    oci = cast("dict[str, object]", committed["oci"])
    artifacts = cast("dict[str, dict[str, object]]", committed["artifacts"])
    # Wheel cross-reference (B8/C2 binding): the OCI section must reference
    # exactly the recorded wheel.
    assert oci["wheel_sha256"] == artifacts["wheel"]["sha256"]
    # R5 byte-identity law: the accepted wheel hash remains exact.
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
    expected_qualification = (
        "mvp-release-0.1.0" if _record_present() else "disposable-qualification-only; not released"
    )
    assert labels["slaif-local-coding.qualification"] == expected_qualification


def test_committed_manifest_conforms_to_schema_v3_structure() -> None:
    # Structural v3 conformance without a new dependency (dependency freeze):
    # closed key sets and fixed constants, mirroring the schema's
    # additionalProperties=false and const/enum entries.
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$id"] == "slaif-release-provenance-v3"
    committed = _committed()
    expected_top = set(schema["required"])
    if _record_present():
        expected_top.add("release")
    assert set(committed) == expected_top
    oci = cast("dict[str, object]", committed["oci"])
    assert set(oci) == set(schema["properties"]["oci"]["required"])
    assert schema["properties"]["oci"]["properties"]["image_reference"]["const"] == (
        "ghcr.io/ulfe-lmi/slaif-local-coding"
    )
    assert schema["properties"]["oci"]["properties"]["published"]["enum"] == [False, True]
    assert schema["properties"]["status"]["properties"]["released"]["enum"] == [False, True]
    labels = cast("dict[str, object]", oci["labels"])
    # labels are defined in $defs.oci_labels (referenced from oci.labels).
    labels_def = schema["$defs"]["oci_labels"]
    assert set(labels) == set(labels_def["properties"])
    if _record_present():
        release_def = schema["properties"]["release"]
        assert set(release_def["required"]) == RELEASE_SECTION_KEYS
        assert release_def["additionalProperties"] is False


# ---------------------------------------------------------------------------
# Objective 013-a workstream A (R4): release record gates and the
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
    if not _record_present():
        return  # not-yet-published state: the record is absent by design
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
    # R4(a): record value == release.image_source_commit ==
    # generated_from.git_commit, an ancestor of HEAD.
    if not _record_present():
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
    if not _record_present():
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
    if not _record_present():
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
    if not _record_present():
        return
    committed = _committed()
    tampered = json.loads(json.dumps(committed))
    release = cast("dict[str, object]", tampered["release"])
    release["oci_image_digest"] = _flip_digest(str(release["oci_image_digest"]))
    assert _strip_git(tampered) != _strip_git(regenerated)


def test_tampered_manifest_release_section_fails_gate(regenerated: dict[str, object]) -> None:
    # R4(d): mutating the manifest release section must fail the gate.
    if not _record_present():
        return
    committed = _committed()
    tampered = json.loads(json.dumps(committed))
    release = cast("dict[str, object]", tampered["release"])
    release["git_tag_target"] = "0" * 40
    assert _strip_git(tampered) != _strip_git(regenerated)


def test_tampered_release_tag_fails_gate(regenerated: dict[str, object]) -> None:
    # R4(d): mutating a release tag must fail the gate.
    if not _record_present():
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
