"""Order 016-b/016-c: current-development provenance contract tests.

After the frozen ``0.1.0-rc10`` publication the repository keeps
developing. The frozen RC10 record/manifest/handoff bytes remain immutable,
but the working tree diverges from the frozen RC10 source-input map. This
suite proves the separate development provenance contract and the order
016-c verifier guards:

1. synthetic temporary git repositories (run UNCONDITIONALLY): a clean
   development source commit A binds to a derived-metadata child B that
   adds the development manifest; the happy path verifies; tamper
   negatives fail closed — missing manifest in a diverged tree, stale
   source (source moved after A without refresh), omitted mapped input,
   altered built wheel, source moved under a derived-metadata commit,
   frozen release metadata touched by a development diff, frozen manifest
   rebound to a later tree, the frozen RC record authorizing the altered
   development source, and — order 016-c — dirty/untracked mapped inputs
   at the frozen head, dirty frozen metadata in the development state,
   closed-contract violations (wrong repository, zeroed lock hash,
   unexpected keys, booleans as integers, malformed nested objects,
   path-escaping records, unsafe artifact basenames), and frozen
   publication mutations committed inside a newly authored source A
   (valid-JSON mutation and deleted archived record) rejected at the
   independent pre-rework freeze baseline guard;
2. the state-aware artifact binding shared with the operator session
   (order 016-c): the state is selected and fully validated BEFORE the
   wheel comparison, with a genuine changed-runtime-source development
   fixture whose freshly built wheel differs from the frozen wheel;
3. the real repository gates: the frozen RC10 source-input binding is
   re-proved against its exact frozen source commit, the independent
   pre-rework freeze baseline holds at the pinned repository authority,
   and — whenever the current source differs from the frozen publication
   — the development manifest exists and verifies at HEAD (map at A, map
   at HEAD, working tree, derived-only A..HEAD diff, self-reference
   exclusion, frozen publication cross-check). A development manifest is
   never required in the frozen state.

Stdlib + git + uv (synthetic builds) only; no network beyond the uv build
cache, no host state.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import shlex
import subprocess
import types
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DEV_SCRIPT = REPO_ROOT / "scripts" / "dev_provenance_manifest.py"
OPERATOR_SCRIPT = REPO_ROOT / "scripts" / "operator_session_ci.py"
DEV_MANIFEST = REPO_ROOT / "packaging" / "dev_provenance_manifest.json"
DEV_SCHEMA = REPO_ROOT / "packaging" / "dev_provenance_manifest.schema.json"
FROZEN_MANIFEST = REPO_ROOT / "packaging" / "release_provenance_manifest.json"

# Hermetic fixture: a minimal real hatchling project whose policy mirrors
# the repository law — the development manifest and its schema are explicit
# build-policy exclusions (self-reference exclusion), the frozen
# publication records are derived metadata (excluded from the map exactly
# as in the real pyproject policy), and the docs/packaging directories are
# sdist inputs so the exclusions are load-bearing. The 100 fixture
# documents bring the input map above the schema's minimum of 100 records
# (the real repository's scale fact, mirrored by the executable
# validation).
POLICY_PYPROJECT = (
    "[project]\n"
    'name = "fixture"\n'
    'version = "0.1.0"\n'
    'requires-python = ">=3.12"\n'
    "\n"
    "[build-system]\n"
    'requires = ["hatchling"]\n'
    'build-backend = "hatchling.build"\n'
    "\n"
    "[tool.hatch.build]\n"
    "exclude = [\n"
    '  "packaging/dev_provenance_manifest.json",\n'
    '  "packaging/dev_provenance_manifest.schema.json",\n'
    '  "packaging/release_provenance_manifest.json",\n'
    '  "packaging/rc_record.json",\n'
    '  "packaging/rc_handoff.md",\n'
    '  "packaging/releases",\n'
    '  "oap/",\n'
    "]\n"
    "\n"
    "[tool.hatch.build.targets.sdist]\n"
    "include = [\n"
    '  "pyproject.toml",\n'
    '  "uv.lock",\n'
    '  "README.md",\n'
    '  "config/adapter.example.toml",\n'
    '  "src",\n'
    '  "docs",\n'
    '  "packaging",\n'
    "]\n"
    "\n"
    "[tool.hatch.build.targets.wheel]\n"
    'packages = ["src/fixture"]\n'
)

FROZEN_MANIFEST_TEMPLATE = """{
  "schema": "slaif-release-provenance-v5",
  "schema_version": 5,
  "generated_from": {
    "repository": "ulfe-lmi/slaif-local-coding",
    "git_commit": "GIT_COMMIT"
  },
  "candidate": {
    "rc_identifier": "0.1.0-rc10"
  },
  "oci": {
    "labels": {
      "slaif-local-coding.qualification": "rc-candidate-0.1.0-rc10"
    }
  },
  "artifacts": {
    "wheel": {
      "name": "WHEEL_NAME",
      "sha256": "WHEEL_SHA",
      "size_bytes": WHEEL_SIZE,
      "entry_count": WHEEL_ENTRIES
    },
    "sdist": {
      "name": "SDIST_NAME",
      "sha256": "SDIST_SHA",
      "size_bytes": SDIST_SIZE,
      "entry_count": SDIST_ENTRIES
    }
  },
  "source_inputs": SOURCE_INPUTS
}
"""

FIXTURE_DOC_COUNT = 100

DevRepo = tuple[Path, str, str, str]


def _load_dev_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("dev_provenance", DEV_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load development provenance module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_operator_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("operator_session_ci", OPERATOR_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load operator session module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def dev() -> types.ModuleType:
    return _load_dev_module()


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", *args],
        capture_output=True,
        check=True,
    )
    return proc.stdout.decode().strip()


def _write(repo: Path, rel: str, content: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


ArtifactFacts = dict[str, object]


def _frozen_build_facts(repo: Path, source: str, tmp: Path) -> tuple[ArtifactFacts, ArtifactFacts]:
    """Clean-build the frozen source (git archive + uv build) so the
    fixture's frozen manifest carries REAL artifact facts — the same
    mechanism the real repository uses."""
    dev = _load_dev_module()
    dist, project = dev._build_from_source(repo, source, tmp / "frozen-build")
    wheels = sorted(dist.glob(f"{project}-*.whl"))
    sdists = sorted(dist.glob(f"{project}-*.tar.gz"))
    assert len(wheels) == 1 and len(sdists) == 1
    return dev._artifact_facts(wheels[0], "wheel"), dev._artifact_facts(sdists[0], "sdist")


@pytest.fixture()
def dev_repo(dev: types.ModuleType, tmp_path: Path) -> tuple[Path, str, str, str]:
    """Synthetic repository: frozen source F (the frozen publication is
    recorded from F at F2, which is also the fixture's pre-rework freeze
    baseline), development source A (an extra document input proving
    divergence from the frozen map), and a derived-metadata child B that
    carries the generated development manifest. Returns (repo, A, B,
    baseline) with the checkout at B."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _write(repo, "pyproject.toml", POLICY_PYPROJECT)
    _write(repo, "uv.lock", "version = 1\n")
    _write(repo, "README.md", "# fixture\n")
    _write(repo, "config/adapter.example.toml", "# config\n")
    _write(repo, "src/fixture/__init__.py", '__version__ = "0.1.0"\n')
    (repo / "packaging").mkdir()
    (repo / "oap").mkdir()
    (repo / "oap" / ".gitkeep").write_text("", encoding="utf-8")
    for i in range(FIXTURE_DOC_COUNT):
        _write(repo, f"docs/fixture/{i:03d}.md", f"# fixture document {i}\n")
    # The frozen publication's record/handoff and one archived record set
    # predate the frozen source (mirroring the real repository, where the
    # archived RC record sets were committed before the RC10 source
    # freeze). They are derived metadata: excluded from the input map and
    # bound by the independent freeze baseline instead.
    _write(
        repo,
        "packaging/rc_record.json",
        json.dumps({"rc_identifier": "0.1.0-rc10"}, indent=2) + "\n",
    )
    _write(repo, "packaging/rc_handoff.md", "# rc handoff (fixture)\n")
    _write(
        repo,
        "packaging/releases/0.1.0-rc1/rc_record.json",
        json.dumps({"rc_identifier": "0.1.0-rc1"}, indent=2) + "\n",
    )
    _write(repo, "packaging/releases/0.1.0-rc1/rc_handoff.md", "# rc1 handoff (fixture)\n")
    _write(repo, "packaging/releases/0.1.0-rc1/release_provenance_manifest.json", "{}\n")
    _commit(repo, "base: build policy + pre-freeze publication records")

    # Frozen source F: the frozen manifest is recorded from F's inputs.
    _write(repo, "docs/frozen.md", "# frozen doc\n")
    frozen_source = _commit(repo, "F: frozen source")
    frozen_map = dev.map_from_git_commit(repo, frozen_source)
    wheel_facts, sdist_facts = _frozen_build_facts(repo, frozen_source, tmp_path)
    frozen_manifest = json.loads(
        FROZEN_MANIFEST_TEMPLATE.replace("GIT_COMMIT", frozen_source)
        .replace("WHEEL_NAME", str(wheel_facts["name"]))
        .replace("WHEEL_SHA", str(wheel_facts["sha256"]))
        .replace("WHEEL_SIZE", str(wheel_facts["size_bytes"]))
        .replace("WHEEL_ENTRIES", str(wheel_facts["entry_count"]))
        .replace("SDIST_NAME", str(sdist_facts["name"]))
        .replace("SDIST_SHA", str(sdist_facts["sha256"]))
        .replace("SDIST_SIZE", str(sdist_facts["size_bytes"]))
        .replace("SDIST_ENTRIES", str(sdist_facts["entry_count"]))
        .replace("SOURCE_INPUTS", json.dumps(frozen_map, sort_keys=True))
    )
    _write(
        repo,
        "packaging/release_provenance_manifest.json",
        json.dumps(frozen_manifest, indent=2, sort_keys=True) + "\n",
    )
    _commit(repo, "F2: frozen derived metadata (pre-rework baseline)")
    baseline = _git(repo, "rev-parse", "HEAD")

    # Development source A: a new document input (sdist input) diverges
    # from the frozen map.
    _write(repo, "docs/dev.md", "# development doc\n")
    dev_source = _commit(repo, "A: development source")

    # Generate the development manifest at A, then commit it as B.
    manifest = dev.generate(repo, dev_source, baseline_commit=baseline)
    assert manifest["source_commit"] == dev_source
    assert set(manifest["source_inputs"]) == set(dev.map_from_git_commit(repo, dev_source))
    # A docs-only development change keeps the wheel identical to the
    # frozen wheel (the real repository's current situation).
    assert manifest["artifacts"]["wheel"]["sha256"] == wheel_facts["sha256"]
    _write(repo, "oap/active", "016-b\n")
    derived = _commit(repo, "B: development derived metadata")
    return repo, dev_source, derived, baseline


def _frozen_scratch(repo: Path, parent: Path) -> tuple[Path, str]:
    """A detached scratch clone at the fixture's frozen head (F2)."""
    frozen_head = _git(repo, "rev-parse", "HEAD~2")
    work = parent / "scratch"
    subprocess.run(["git", "clone", "--quiet", str(repo), str(work)], check=True)
    _git(work, "checkout", "--quiet", "--detach", frozen_head)
    return work, frozen_head


# ---------------------------------------------------------------------------
# Happy path and state law
# ---------------------------------------------------------------------------


def test_dev_happy_path(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    repo, a, b, baseline = dev_repo
    assert _git(repo, "rev-parse", "HEAD") == b
    facts = dev.verify(repo, b, baseline_commit=baseline)
    assert facts["state"] == "development"
    assert facts["development"]["source_commit"] == a
    assert facts["development"]["freeze_baseline"] == baseline
    assert facts["development"]["freeze_baseline_paths"] == 6


def test_dev_state_frozen_without_manifest(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """At the frozen head (inputs identical to the frozen map, clean
    tree) the state is frozen and no development manifest is required."""
    repo, _a, _b, baseline = dev_repo
    work, frozen_head = _frozen_scratch(repo, repo.parent)
    assert not (work / "packaging" / "dev_provenance_manifest.json").is_file()
    facts = dev.verify(work, frozen_head, baseline_commit=baseline)
    assert facts["state"] == "frozen"
    assert facts["freeze_baseline_paths"] == 6


def test_dev_missing_manifest_fails(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    repo, _a, b, baseline = dev_repo
    (repo / "packaging" / "dev_provenance_manifest.json").unlink()
    with pytest.raises(dev.DevProvenanceError, match="no development manifest"):
        dev.verify(repo, b, baseline_commit=baseline)


# ---------------------------------------------------------------------------
# Order 016-c, item 1: committed-map AND actual-working-tree-map binding
# ---------------------------------------------------------------------------


def test_dirty_mapped_input_at_frozen_head_fails(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """A dirty mapped input at the frozen head must NOT acquire frozen
    authority (the independent probe's first case)."""
    repo, _a, _b, baseline = dev_repo
    work, frozen_head = _frozen_scratch(repo, repo.parent)
    doc = work / "docs" / "frozen.md"
    original = doc.read_text(encoding="utf-8")
    doc.write_text(original + "Changed mapped input.\n", encoding="utf-8")
    with pytest.raises(
        dev.DevProvenanceError, match="working tree differs from the committed source"
    ):
        dev.verify(work, frozen_head, baseline_commit=baseline)


def test_untracked_mapped_input_at_frozen_head_fails(
    dev: types.ModuleType, dev_repo: DevRepo
) -> None:
    """A new untracked mapped input at the frozen head must NOT acquire
    frozen authority (the independent probe's second case)."""
    repo, _a, _b, baseline = dev_repo
    work, frozen_head = _frozen_scratch(repo, repo.parent)
    (work / "docs" / "untracked.md").write_text("# New untracked mapped input\n", encoding="utf-8")
    with pytest.raises(dev.DevProvenanceError, match=r"extra=\['docs/untracked\.md'\]"):
        dev.verify(work, frozen_head, baseline_commit=baseline)


def test_dirty_frozen_metadata_in_development_fails(
    dev: types.ModuleType, dev_repo: DevRepo
) -> None:
    """Dirty (uncommitted) frozen publication metadata in the development
    state is invisible to the input map (derived exclusion) and must be
    caught by the independent freeze baseline's working-tree binding."""
    repo, _a, b, baseline = dev_repo
    record = repo / "packaging" / "rc_record.json"
    original = record.read_text(encoding="utf-8")
    try:
        record.write_text(original + "# tampered\n", encoding="utf-8")
        with pytest.raises(dev.DevProvenanceError, match="pre-rework baseline \\(working tree\\)"):
            dev.verify(repo, b, baseline_commit=baseline)
    finally:
        record.write_text(original, encoding="utf-8")


# ---------------------------------------------------------------------------
# Stale / omitted / altered source and artifacts
# ---------------------------------------------------------------------------


def test_dev_stale_source_fails(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """A later source change without a refreshed manifest fails closed."""
    repo, _a, b, baseline = dev_repo
    _write(repo, "docs/dev.md", "# development doc\n# altered\n")
    c = _commit(repo, "C: source drifted after A")
    with pytest.raises(dev.DevProvenanceError, match="refreshed development manifest"):
        dev.verify(repo, c, baseline_commit=baseline)
    # Even at the manifest commit itself the frozen binding is intact, so
    # the failure is precisely the stale-source condition (not frozen drift).
    _git(repo, "checkout", "--quiet", "--detach", b)


def test_dev_omitted_input_fails(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """Removing a mapped input after A is an omitted-input failure."""
    repo, _a, b, baseline = dev_repo
    (repo / "config" / "adapter.example.toml").unlink()
    c = _commit(repo, "C: mapped input removed")
    with pytest.raises(
        dev.DevProvenanceError, match=r"missing=\['config/adapter\.example\.toml'\]"
    ):
        dev.verify(repo, c, baseline_commit=baseline)
    _git(repo, "checkout", "--quiet", "--detach", b)


def test_dev_non_mapped_path_under_derived_metadata_fails(
    dev: types.ModuleType, dev_repo: DevRepo
) -> None:
    """A..HEAD may never carry non-derived changes: even a path that is NOT
    an input map (a script) moved under the derived-metadata commit fails,
    because the input map alone cannot see it (the A/B derived-only law)."""
    repo, _a, b, baseline = dev_repo
    _git(repo, "checkout", "--quiet", "--detach", b)
    _write(repo, "scripts/helper.py", "x = 1\n")
    _write(repo, "oap/active", "016-c\n")
    bad = _commit(repo, "bad: non-mapped path moved under B")
    with pytest.raises(dev.DevProvenanceError, match="non-derived development paths"):
        dev.verify(repo, bad, baseline_commit=baseline)
    _git(repo, "checkout", "--quiet", "--detach", b)


def test_dev_altered_wheel_fails(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """A built wheel that does not reproduce the development source's
    recorded hash is an altered-artifact failure (bound to dist)."""
    repo, a, b, baseline = dev_repo
    manifest = dev.load_dev_manifest(repo)
    assert manifest is not None
    # Build from the SAME source commit but with a locally altered input:
    # the input map at A is unchanged for verification purposes, so the
    # artifact binding is the only gate that can catch this.
    build = repo.parent / "altered-build"
    build.mkdir()
    subprocess.run(
        ["git", "-C", str(repo), "archive", "--output", str(build / "a.tar"), a],
        check=True,
        capture_output=True,
    )
    subprocess.run(["tar", "-x", "-f", str(build / "a.tar"), "-C", str(build)], check=True)
    # The fixture wheel contains the runtime package (and only the
    # build-policy wheel inputs): alter a real wheel input.
    (build / "src" / "fixture" / "__init__.py").write_text(
        '__version__ = "altered"\n', encoding="utf-8"
    )
    dist = build / "dist"
    dist.mkdir()
    uv = subprocess.run(["uv", "build", "--out-dir", str(dist)], cwd=build, capture_output=True)
    assert uv.returncode == 0, uv.stderr.decode()
    with pytest.raises(dev.DevProvenanceError, match="altered artifact"):
        dev.verify_artifacts(repo, manifest, dist)
    _git(repo, "checkout", "--quiet", "--detach", b)


# ---------------------------------------------------------------------------
# Order 016-c, item 4: independent pre-rework freeze baseline
# ---------------------------------------------------------------------------


def test_dev_frozen_metadata_touched_fails(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """A development diff touching the frozen release metadata fails
    closed at the intended freeze guard (order 016-c: the independent
    pre-rework baseline, not the A..head diff alone)."""
    repo, a, _b, baseline = dev_repo
    frozen_path = repo / "packaging" / "release_provenance_manifest.json"
    frozen = json.loads(frozen_path.read_text())
    frozen["artifacts"]["wheel"]["sha256"] = "f" * 64
    frozen_path.write_text(json.dumps(frozen, indent=2, sort_keys=True) + "\n")
    bad = _commit(repo, "bad: frozen metadata touched")
    with pytest.raises(dev.DevProvenanceError, match="pre-rework baseline \\(committed"):
        dev.verify(repo, bad, baseline_commit=baseline)
    _git(repo, "checkout", "--quiet", "--detach", a)


def test_dev_frozen_manifest_rebound_fails(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """A frozen manifest rebound to a later tree's map fails the frozen
    binding re-proof (the later-tree-map escape, frozen side)."""
    repo, _a, b, baseline = dev_repo
    frozen_path = repo / "packaging" / "release_provenance_manifest.json"
    frozen = json.loads(frozen_path.read_text())
    frozen["source_inputs"] = dict(dev.map_from_directory(repo))
    frozen_path.write_text(json.dumps(frozen, indent=2, sort_keys=True) + "\n")
    bad = _commit(repo, "bad: frozen manifest rebound to a later tree")
    with pytest.raises(dev.DevProvenanceError, match="frozen RC10 source-input binding broken"):
        dev.verify(repo, bad, baseline_commit=baseline)
    _git(repo, "checkout", "--quiet", "--detach", b)


def _refreshed_manifest_for_source(
    dev: types.ModuleType, repo: Path, source: str
) -> dict[str, object]:
    """Copy of the committed development manifest re-pointed at a new
    source commit whose input map and artifacts are unchanged (frozen
    publication metadata is map-excluded derived metadata, so moving the
    source never changes the input map or the built artifacts)."""
    manifest = dev.load_dev_manifest(repo)
    assert manifest is not None
    updated: dict[str, object] = copy.deepcopy(manifest)
    updated["source_commit"] = source
    updated["objective"] = "016-c"
    updated["qualification_label"] = dev.dev_qualification_label(source)
    return updated


def test_dev_frozen_metadata_mutated_in_new_source_fails(
    dev: types.ModuleType, dev_repo: DevRepo
) -> None:
    """Order 016-c: a valid-JSON frozen metadata mutation committed inside
    a newly authored source A is rejected at the intended freeze guard
    (independent baseline byte comparison — not merely malformed JSON).
    The mutation is map-invisible (derived exclusion), so the manifest
    regenerated at the new source is otherwise internally consistent."""
    repo, _a, b, baseline = dev_repo
    record_path = repo / "packaging" / "rc_record.json"
    original = record_path.read_text(encoding="utf-8")
    record = json.loads(original)
    record["post_freeze_note"] = "mutation committed inside new source A"
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    a2 = _commit(repo, "A2: frozen metadata mutated inside new source")
    # generate fails early at the same intended freeze guard...
    with pytest.raises(dev.DevProvenanceError, match="pre-rework baseline"):
        dev.generate(repo, a2, "016-c", baseline_commit=baseline)
    # ...and the (otherwise consistent) refreshed manifest fails verify at
    # the committed baseline comparison.
    manifest = _refreshed_manifest_for_source(dev, repo, a2)
    (repo / "packaging" / "dev_provenance_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write(repo, "oap/active", "016-c\n")
    b2 = _commit(repo, "B2: refreshed manifest at mutated source")
    with pytest.raises(dev.DevProvenanceError, match="pre-rework baseline \\(committed"):
        dev.verify(repo, b2, baseline_commit=baseline)
    _git(repo, "checkout", "--quiet", "--detach", b)
    assert record_path.read_text(encoding="utf-8") == original


def test_dev_deleted_archived_record_in_new_source_fails(
    dev: types.ModuleType, dev_repo: DevRepo
) -> None:
    """Order 016-c: a deleted archived publication file committed inside a
    newly authored source A is rejected at the intended freeze guard
    (path presence is part of the independent baseline law)."""
    repo, _a, b, baseline = dev_repo
    victim = repo / "packaging" / "releases" / "0.1.0-rc1" / "rc_handoff.md"
    victim.unlink()
    a2 = _commit(repo, "A2: archived record deleted inside new source")
    with pytest.raises(dev.DevProvenanceError, match="frozen publication paths deleted"):
        dev.generate(repo, a2, "016-c", baseline_commit=baseline)
    manifest = _refreshed_manifest_for_source(dev, repo, a2)
    (repo / "packaging" / "dev_provenance_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write(repo, "oap/active", "016-c\n")
    b2 = _commit(repo, "B2: refreshed manifest at deletion source")
    with pytest.raises(dev.DevProvenanceError, match="frozen publication paths deleted"):
        dev.verify(repo, b2, baseline_commit=baseline)
    _git(repo, "checkout", "--quiet", "--detach", b)
    assert victim.is_file()


def test_dev_new_publication_record_in_new_source_fails(
    dev: types.ModuleType, dev_repo: DevRepo
) -> None:
    """Order 016-c: a NEW top-level publication record committed inside a
    newly authored source A is new freeze authority, not development —
    rejected at the independent baseline guard."""
    repo, _a, b, baseline = dev_repo
    _write(
        repo,
        "packaging/release_record.json",
        json.dumps({"release_identifier": "0.1.0"}, indent=2) + "\n",
    )
    a2 = _commit(repo, "A2: new top-level publication record inside new source")
    with pytest.raises(dev.DevProvenanceError, match="new top-level publication record"):
        dev.generate(repo, a2, "016-c", baseline_commit=baseline)
    _git(repo, "checkout", "--quiet", "--detach", b)
    assert not (repo / "packaging" / "release_record.json").exists()


def test_dev_baseline_is_never_chosen_by_the_manifest(
    dev: types.ModuleType, dev_repo: DevRepo
) -> None:
    """Order 016-c: the freeze authority is the pinned repository
    baseline (or the typed fixture argument) — a manifest carrying a
    self-declared baseline fact has no such key and cannot name one."""
    repo, _a, b, baseline = dev_repo
    manifest = dev.load_dev_manifest(repo)
    assert manifest is not None
    assert "baseline" not in json.dumps(manifest)
    # An untrusted/unknown baseline commit is refused outright.
    with pytest.raises(dev.DevProvenanceError, match="missing from the repository"):
        dev.verify_frozen_publication_baseline(repo, "f" * 40, b)


# ---------------------------------------------------------------------------
# Order 016-c, item 2: closed development contract enforcement
# ---------------------------------------------------------------------------


def test_closed_contract_negatives_fail(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """Every closed-contract violation is rejected on the public
    consumption path that BYPASSES load_dev_manifest (the rehearsal's
    direct verify_development call), and the loader rejects the same
    bytes when persisted."""
    repo, _a, b, baseline = dev_repo
    manifest = dev.load_dev_manifest(repo)
    assert manifest is not None

    def expect_reject(mutate: Any, match: str, persisted: bool = True) -> None:
        bad = copy.deepcopy(manifest)
        mutate(bad)
        with pytest.raises(dev.DevProvenanceError, match=match):
            dev.verify_development(repo, b, bad, baseline_commit=baseline)
        if not persisted:
            return
        # The persisted loader rejects the same bytes too (structural
        # violations only; repo-dependent cross-checks need the repository).
        path = repo / "packaging" / "dev_provenance_manifest.json"
        original = path.read_text(encoding="utf-8")
        try:
            path.write_text(json.dumps(bad, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            with pytest.raises(dev.DevProvenanceError):
                dev.load_dev_manifest(repo)
        finally:
            path.write_text(original, encoding="utf-8")

    expect_reject(
        lambda m: m.update({"repository": "synthetic/wrong-repository"}),
        "repository is not",
    )
    expect_reject(
        lambda m: m["toolchain"].update({"uv_lock_sha256": "0" * 64}),
        "does not bind the current uv.lock",
        persisted=False,  # repo-dependent: the loader cannot see uv.lock
    )
    expect_reject(
        lambda m: m.update({"unexpected_root_key": True}),
        "carries unexpected keys",
    )
    expect_reject(
        lambda m: m["artifacts"]["wheel"].update({"size_bytes": True}),
        "size_bytes must be an integer",
    )
    expect_reject(
        lambda m: m["artifacts"]["sdist"].update({"entry_count": False}),
        "entry_count must be an integer",
    )
    expect_reject(
        lambda m: m.update({"toolchain": "not-an-object"}),
        "toolchain must be a JSON object",
    )
    expect_reject(
        lambda m: m.update({"frozen_publication": ["list-not-object"]}),
        "frozen_publication must be a JSON object",
    )
    expect_reject(
        lambda m: m["source_inputs"].update({"../evil.md": "0" * 64}),
        "unsafe or escaping path",
    )
    expect_reject(
        lambda m: m["source_inputs"].update({"/etc/passwd": "0" * 64}),
        "unsafe or escaping path",
    )
    expect_reject(
        lambda m: m["source_inputs"].update({"docs/bad\\path.md": "0" * 64}),
        "unsafe or escaping path",
    )
    expect_reject(
        lambda m: m["artifacts"]["sdist"].update({"name": "../../evil.whl"}),
        "not a safe basename",
    )
    expect_reject(
        lambda m: m.update({"state": "frozen"}),
        "state is not 'development'",
    )
    expect_reject(
        lambda m: m.update({"release": True}),
        "release must be false",
    )
    expect_reject(
        lambda m: m.update({"schema": "slaif-dev-provenance-v2"}),
        "schema is not",
    )
    expect_reject(
        lambda m: m.update({"schema_version": 2}),
        "schema_version is not 1",
    )
    expect_reject(
        lambda m: m.update({"objective": "16-c"}),
        "objective is not NNN-L",
    )
    expect_reject(
        lambda m: m.update({"source_commit": "g" * 40}),
        "source_commit is not 40-hex",
    )
    expect_reject(
        lambda m: m["frozen_publication"].update({"rc_identifier": "0.1.0-rc9"}),
        "rc_identifier is not",
    )
    expect_reject(
        lambda m: m["frozen_publication"].update({"wheel_sha256": "z" * 64}),
        "wheel_sha256 is not 64-hex",
    )
    expect_reject(
        lambda m: m.update(
            {"self_referential_exclusions": ["packaging/dev_provenance_manifest.json"]}
        ),
        "self_referential_exclusions",
    )
    expect_reject(
        lambda m: m.update({"qualification_label": "not a development label"}),
        "deterministic development-source label",
    )
    expect_reject(
        lambda m: m["source_inputs"].update({"docs/dev.md": "zz" * 32}),
        "non-64-hex sha256",
    )
    expect_reject(
        lambda m: m.update({"artifacts": {"wheel": m["artifacts"]["wheel"]}}),
        "artifacts is missing required keys",
    )
    expect_reject(
        lambda m: m["toolchain"].update({"python": "3.11.9"}),
        "python is not a pinned 3.12.x version",
    )
    expect_reject(
        lambda m: m["toolchain"].update({"uv_version": "0.12"}),
        "uv_version is not major.minor.patch",
    )
    expect_reject(
        lambda m: m.update({"frozen_publication": m["frozen_publication"] | {"extra": 1}}),
        "frozen_publication carries unexpected keys",
    )
    slim = copy.deepcopy(manifest)
    for key in list(slim["source_inputs"]):
        if len(slim["source_inputs"]) <= dev.MIN_SOURCE_INPUTS - 1:
            break
        del slim["source_inputs"][key]
    assert len(slim["source_inputs"]) == dev.MIN_SOURCE_INPUTS - 1
    slim_inputs = slim["source_inputs"]
    expect_reject(
        lambda m: m.update({"source_inputs": slim_inputs}),
        "fewer than the schema's minimum",
    )


# ---------------------------------------------------------------------------
# Order 016-c, item 3: state selected before the expected wheel
# ---------------------------------------------------------------------------


def test_operator_binding_changed_runtime_source(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """Genuine changed-runtime-source development fixture: a freshly
    built wheel whose hash differs from the frozen wheel. The same
    operator binding logic selects and fully validates the state FIRST,
    then compares against exactly that state's expected wheel: the
    development hash passes; the frozen hash and another wrong hash
    fail."""
    repo, _a, _b, baseline = dev_repo
    op = _load_operator_module()
    frozen = json.loads((repo / "packaging" / "release_provenance_manifest.json").read_text())
    frozen_wheel = str(frozen["artifacts"]["wheel"]["sha256"])

    # 1) Docs-only development state at B: the dev wheel equals the frozen
    #    wheel (no runtime change yet) — the current real-repo situation.
    state, expected = op.select_artifact_state(repo, baseline)
    assert state == "development"
    manifest = dev.load_dev_manifest(repo)
    assert manifest is not None
    assert expected == str(manifest["artifacts"]["wheel"]["sha256"]) == frozen_wheel
    op.bind_wheel_sha256(expected, expected, state)  # correct hash passes

    # 2) A genuinely changed runtime source: new source A2 with an altered
    #    runtime package; the refreshed development manifest's freshly
    #    built wheel differs from the frozen wheel.
    _write(repo, "src/fixture/__init__.py", '__version__ = "0.2.0"\n')
    a2 = _commit(repo, "A2: changed runtime source")
    manifest2 = dev.generate(repo, a2, "016-c", baseline_commit=baseline)
    _write(repo, "oap/active", "016-c\n")
    _commit(repo, "B2: refreshed development manifest")
    dev_wheel = str(manifest2["artifacts"]["wheel"]["sha256"])
    assert dev_wheel != frozen_wheel, "fixture must change the wheel hash"

    # 3) State selection + full validation happens FIRST, and names the
    #    development wheel (not the frozen one).
    state2, expected2 = op.select_artifact_state(repo, baseline)
    assert state2 == "development"
    assert expected2 == dev_wheel
    # The correct development hash passes...
    op.bind_wheel_sha256(expected2, expected2, state2)
    # ...the frozen hash fails...
    with pytest.raises(op.SessionError, match="development manifest wheel"):
        op.bind_wheel_sha256(frozen_wheel, expected2, state2)
    # ...and another wrong hash fails.
    with pytest.raises(op.SessionError, match="development manifest wheel"):
        op.bind_wheel_sha256("f" * 64, expected2, state2)
    _git(repo, "checkout", "--quiet", "--detach", _b)
    assert _git(repo, "rev-parse", "HEAD") == _b


def test_operator_binding_frozen_state(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """Frozen positives and mismatched-wheel negatives at the frozen head:
    the frozen hash passes, a development (different) hash fails."""
    repo, _a, _b, baseline = dev_repo
    op = _load_operator_module()
    work, _ = _frozen_scratch(repo, repo.parent)
    frozen = json.loads((work / "packaging" / "release_provenance_manifest.json").read_text())
    frozen_wheel = str(frozen["artifacts"]["wheel"]["sha256"])
    state, expected = op.select_artifact_state(work, baseline)
    assert state == "frozen"
    assert expected == frozen_wheel
    op.bind_wheel_sha256(frozen_wheel, expected, state)  # frozen positive
    with pytest.raises(op.SessionError, match="frozen manifest wheel"):
        op.bind_wheel_sha256("f" * 64, expected, state)  # mismatched wheel negative


# ---------------------------------------------------------------------------
# Emit-state: fail closed, shell round-trip without execution
# ---------------------------------------------------------------------------


def _parse_state_file(path: Path) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, quoted = line.split("=", 1)
        values = shlex.split(quoted)
        assert len(values) == 1
        parsed[key] = values[0]
    return parsed


def test_emit_state_round_trip(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """Ordinary frozen and development emitted labels round-trip through
    the shell-quoted file without execution; nothing is written on
    invalid state."""
    repo, _a, b, baseline = dev_repo
    out_dev = repo.parent / "state-dev.env"
    values = dev.emit_state(repo, out_dev, baseline_commit=baseline)
    assert values["state"] == "development"
    assert _parse_state_file(out_dev) == values

    work, _frozen_head = _frozen_scratch(repo, repo.parent)
    out_frozen = repo.parent / "state-frozen.env"
    values_frozen = dev.emit_state(work, out_frozen, baseline_commit=baseline)
    assert values_frozen["state"] == "frozen"
    assert _parse_state_file(out_frozen) == values_frozen

    # Invalid state emits nothing usable: the output path must not exist.
    out_bad = repo.parent / "state-bad.env"
    (repo / "packaging" / "dev_provenance_manifest.json").unlink()
    with pytest.raises(dev.DevProvenanceError):
        dev.emit_state(repo, out_bad, baseline_commit=baseline)
    assert not out_bad.exists()


# ---------------------------------------------------------------------------
# Frozen record authorization and self-reference / label laws
# ---------------------------------------------------------------------------


def test_dev_stale_rc_record_cannot_authorize(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """The frozen record/qualification can never authorize publication of
    the altered development source: the frozen A/B binding at the current
    head fails closed (non-derived source paths moved since F)."""
    repo, _a, b, _baseline = dev_repo
    frozen = json.loads((repo / "packaging" / "release_provenance_manifest.json").read_text())
    frozen_source = str(frozen["generated_from"]["git_commit"])
    # The frozen manifest at F2 (its own derived head) is still valid...
    dev.verify_ab(
        repo,
        frozen_source,
        _git(repo, "rev-parse", "HEAD~2"),
        recorded_map=frozen["source_inputs"],
    )
    # ...but the same frozen binding cannot be stretched to the development
    # head: source inputs moved, so a publication claim from this source
    # under the frozen record is rejected.
    with pytest.raises(dev.InputMapError):
        dev.verify_ab(repo, frozen_source, b, recorded_map=frozen["source_inputs"])


def test_dev_self_reference_excluded(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """The development manifest and schema are deliberately excluded from
    the input map (self-referential metadata)."""
    repo, _a, _b, _baseline = dev_repo
    tree_map = dev.map_from_directory(repo)
    assert "packaging/dev_provenance_manifest.json" not in tree_map
    assert "packaging/dev_provenance_manifest.schema.json" not in tree_map
    manifest = dev.load_dev_manifest(repo)
    assert manifest is not None
    for self_path in dev.DEV_DERIVED_METADATA_PATHS:
        assert self_path not in manifest["source_inputs"]
    assert manifest["self_referential_exclusions"] == sorted(dev.DEV_DERIVED_METADATA_PATHS)


def test_dev_label_law(dev: types.ModuleType, dev_repo: DevRepo) -> None:
    """Development images identify the development/source state and can
    never claim RC10 qualification."""
    repo, a, _b, _baseline = dev_repo
    manifest = dev.load_dev_manifest(repo)
    assert manifest is not None
    label = str(manifest["qualification_label"])
    assert label == dev.dev_qualification_label(a)
    assert "not released" in label
    assert "rc-candidate" not in label
    assert "0.1.0-rc10" not in label
    assert a in label


# ---------------------------------------------------------------------------
# Real-repository gates
# ---------------------------------------------------------------------------


def test_real_frozen_rc10_binding_reproved() -> None:
    """The frozen RC10 source-input binding holds at the current HEAD
    (map at the exact frozen source commit == committed frozen map; A is an
    ancestor of HEAD)."""
    dev = _load_dev_module()
    committed = json.loads(FROZEN_MANIFEST.read_text(encoding="utf-8"))
    recorded = committed["source_inputs"]
    a = str(committed["generated_from"]["git_commit"])
    assert dev.map_from_git_commit(REPO_ROOT, a) == recorded
    head = _git(REPO_ROOT, "rev-parse", "HEAD")
    if a != head:
        assert dev._is_ancestor(REPO_ROOT, a, head)


def test_real_frozen_publication_baseline_holds() -> None:
    """Order 016-c: at the pinned pre-rework baseline, every existing
    top-level and archived publication record/manifest/handoff is
    byte-identical at HEAD and in the working tree, with path presence
    preserved (no deletion, no new top-level or archived record)."""
    dev = _load_dev_module()
    count = dev.verify_frozen_publication_baseline(REPO_ROOT, dev.PRE_REWORK_BASELINE_COMMIT)
    paths = dev.frozen_publication_paths(REPO_ROOT, dev.PRE_REWORK_BASELINE_COMMIT)
    assert count == len(paths)
    assert count == 29  # 5 top-level records/manifests/handoff + 24 archived
    for top in (
        "packaging/rc_artifact_record.schema.json",
        "packaging/rc_handoff.md",
        "packaging/rc_record.json",
        "packaging/release_provenance_manifest.json",
        "packaging/release_provenance_manifest.schema.json",
    ):
        assert top in paths
    assert "packaging/release_record.json" not in paths  # absent at baseline
    assert all(
        p.startswith("packaging/releases/")
        for p in paths
        - {
            "packaging/rc_artifact_record.schema.json",
            "packaging/rc_handoff.md",
            "packaging/rc_record.json",
            "packaging/release_provenance_manifest.json",
            "packaging/release_provenance_manifest.schema.json",
        }
    )


def test_real_development_state_consistent() -> None:
    """State-aware real-repository gate: in the frozen state nothing extra
    is required; in the development state the development manifest exists
    and verifies at HEAD (and in the working tree)."""
    dev = _load_dev_module()
    head = _git(REPO_ROOT, "rev-parse", "HEAD")
    state, _frozen = dev.current_state(REPO_ROOT, head)
    facts = dev.verify(REPO_ROOT)
    assert facts["state"] == state
    if state == "development":
        assert DEV_MANIFEST.is_file()
        manifest = dev.load_dev_manifest(REPO_ROOT)
        assert manifest is not None
        assert facts["development"]["source_commit"] == manifest["source_commit"]
        assert facts["development"]["freeze_baseline"] == dev.PRE_REWORK_BASELINE_COMMIT
    else:
        # Frozen state: the development manifest is never required.
        assert facts["state"] == "frozen"


def test_real_dev_manifest_not_an_input() -> None:
    """Self-reference exclusion in the real repository: the development
    manifest and schema are not artifact inputs."""
    dev = _load_dev_module()
    tree_map = dev.map_from_directory(REPO_ROOT)
    assert "packaging/dev_provenance_manifest.json" not in tree_map
    assert "packaging/dev_provenance_manifest.schema.json" not in tree_map


def test_real_dev_schema_pins_frozen_publication() -> None:
    """The development schema's frozen-publication consts must match the
    committed frozen manifest (independent cross-pin), and the schema's
    closed-contract constants must match the executable validation."""
    dev = _load_dev_module()
    schema = json.loads(DEV_SCHEMA.read_text(encoding="utf-8"))
    frozen = json.loads(FROZEN_MANIFEST.read_text(encoding="utf-8"))
    fp = schema["properties"]["frozen_publication"]["properties"]
    assert fp["rc_identifier"]["const"] == frozen["candidate"]["rc_identifier"]
    assert fp["source_commit"]["const"] == frozen["generated_from"]["git_commit"]
    assert fp["wheel_sha256"]["const"] == frozen["artifacts"]["wheel"]["sha256"]
    assert fp["sdist_sha256"]["const"] == frozen["artifacts"]["sdist"]["sha256"]
    assert schema["$id"] == dev.SCHEMA_NAME
    # Schema <-> executable agreement on the closed-contract constants.
    props = schema["properties"]
    assert props["schema"]["const"] == dev.SCHEMA_NAME
    assert props["schema_version"]["const"] == dev.SCHEMA_VERSION
    assert props["state"]["const"] == "development"
    assert props["release"]["const"] is False
    assert props["repository"]["const"] == dev.REPOSITORY_IDENTITY
    assert props["frozen_publication"]["properties"]["manifest_path"]["const"] == str(
        dev.FROZEN_MANIFEST_PATH
    )
    assert props["frozen_publication"]["properties"]["schema"]["const"] == dev.FROZEN_SCHEMA_NAME
    assert props["source_inputs"]["minProperties"] == dev.MIN_SOURCE_INPUTS
    assert props["qualification_label"]["pattern"] == dev._LABEL_RE.pattern
    assert props["source_commit"]["pattern"] == dev._HEX40_RE.pattern
    assert props["toolchain"]["properties"]["uv_lock_sha256"]["pattern"] == dev._HEX64_RE.pattern
    assert props["toolchain"]["properties"]["python"]["pattern"] == dev._PYTHON_RE.pattern
    assert props["toolchain"]["properties"]["uv_version"]["pattern"] == dev._UV_VERSION_RE.pattern
    assert props["objective"]["pattern"] == dev._OBJECTIVE_RE.pattern
    # additionalProperties false at every level == the executable's exact
    # key sets.
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(dev._TOP_LEVEL_KEYS)
    assert schema["properties"]["artifacts"]["additionalProperties"] is False
    assert set(schema["properties"]["artifacts"]["required"]) == {"wheel", "sdist"}
    assert schema["$defs"]["artifact"]["additionalProperties"] is False and set(
        schema["$defs"]["artifact"]["required"]
    ) == set(dev._ARTIFACT_KEYS)
    assert schema["properties"]["toolchain"]["additionalProperties"] is False
    assert set(schema["properties"]["toolchain"]["required"]) == set(dev._TOOLCHAIN_KEYS)
    assert schema["properties"]["frozen_publication"]["additionalProperties"] is False
    assert set(schema["properties"]["frozen_publication"]["required"]) == set(
        dev._FROZEN_PUBLICATION_KEYS
    )
