"""Order 016-b: current-development provenance contract tests.

After the frozen ``0.1.0-rc10`` publication the repository keeps
developing. The frozen RC10 record/manifest/handoff bytes remain immutable,
but the working tree diverges from the frozen RC10 source-input map. This
suite proves the separate development provenance contract:

1. synthetic temporary git repositories (run UNCONDITIONALLY): a clean
   development source commit A binds to a derived-metadata child B that adds
   the development manifest; the happy path verifies; tamper negatives fail
   closed — missing manifest in a diverged tree, stale source (source moved
   after A without refresh), omitted mapped input, altered built wheel,
   source moved under a derived-metadata commit, frozen release metadata
   touched by a development diff, frozen manifest rebound to a later tree,
   and the frozen RC record authorizing the altered development source;
2. the real repository gate: the frozen RC10 source-input binding is
   re-proved against its exact frozen source commit, and — whenever the
   current source differs from the frozen publication — the development
   manifest exists and verifies at HEAD (map at A, map at HEAD, working
   tree, derived-only A..HEAD diff, self-reference exclusion, frozen
   publication cross-check). A development manifest is never required in
   the frozen state.

Stdlib + git + uv (synthetic builds) only; no network beyond the uv build
cache, no host state.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DEV_SCRIPT = REPO_ROOT / "scripts" / "dev_provenance_manifest.py"
DEV_MANIFEST = REPO_ROOT / "packaging" / "dev_provenance_manifest.json"
DEV_SCHEMA = REPO_ROOT / "packaging" / "dev_provenance_manifest.schema.json"
FROZEN_MANIFEST = REPO_ROOT / "packaging" / "release_provenance_manifest.json"

# Hermetic fixture: a minimal real hatchling project whose policy mirrors the
# repository law — the development manifest and its schema are explicit
# build-policy exclusions (self-reference exclusion), and the packaging
# directory is an sdist input so the exclusion is load-bearing.
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
  "artifacts": {
    "wheel": {"name": "w.whl", "sha256": "WHEEL_SHA", "size_bytes": 1, "entry_count": 1},
    "sdist": {"name": "s.tar.gz", "sha256": "SDIST_SHA", "size_bytes": 1, "entry_count": 1}
  },
  "source_inputs": SOURCE_INPUTS
}
"""


def _load_dev_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("dev_provenance", DEV_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load development provenance module")
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


@pytest.fixture()
def dev_repo(dev: types.ModuleType, tmp_path: Path) -> tuple[Path, str, str]:
    """Synthetic repository: frozen source F (the frozen manifest is
    generated from F at F), development source A (identical inputs, an
    extra document input proving divergence from the frozen map), and a
    derived-metadata child B that carries the generated development
    manifest. Returns (repo, A, B) with the checkout at B."""
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
    _commit(repo, "base: build policy")

    # Frozen source F: the frozen manifest is recorded from F's inputs.
    _write(repo, "docs/frozen.md", "# frozen doc\n")
    frozen_source = _commit(repo, "F: frozen source")
    frozen_map = dev.map_from_git_commit(repo, frozen_source)
    frozen_manifest = json.loads(
        FROZEN_MANIFEST_TEMPLATE.replace("GIT_COMMIT", frozen_source)
        .replace("WHEEL_SHA", "0" * 64)
        .replace("SDIST_SHA", "1" * 64)
        .replace("SOURCE_INPUTS", json.dumps(frozen_map, sort_keys=True))
    )
    _write(
        repo,
        "packaging/release_provenance_manifest.json",
        json.dumps(frozen_manifest, indent=2, sort_keys=True) + "\n",
    )
    _commit(repo, "F2: frozen derived metadata")
    # F2 is a derived-metadata-only child of F: the frozen state at F2 has
    # the frozen map (the manifest is excluded from inputs).

    # Development source A: a new document input (sdist input) diverges
    # from the frozen map.
    _write(repo, "docs/dev.md", "# development doc\n")
    dev_source = _commit(repo, "A: development source")

    # Generate the development manifest at A, then commit it as B.
    manifest = dev.generate(repo, dev_source)
    assert manifest["source_commit"] == dev_source
    assert set(manifest["source_inputs"]) == set(dev.map_from_git_commit(repo, dev_source))
    _write(repo, "oap/active", "016-b\n")
    derived = _commit(repo, "B: development derived metadata")
    return repo, dev_source, derived


def test_dev_happy_path(dev: types.ModuleType, dev_repo: tuple[Path, str, str]) -> None:
    repo, a, b = dev_repo
    assert _git(repo, "rev-parse", "HEAD") == b
    facts = dev.verify(repo, b)
    assert facts["state"] == "development"
    assert facts["development"]["source_commit"] == a


def test_dev_state_frozen_without_manifest(
    dev: types.ModuleType, dev_repo: tuple[Path, str, str]
) -> None:
    """At the frozen derived-metadata head (inputs identical to the frozen
    map) the state is frozen and no development manifest is required."""
    repo, _a, _b = dev_repo
    # Rebuild the frozen head in a scratch clone of this fixture's history:
    # F2 is the last commit before the development source change.
    frozen_head = _git(repo, "rev-parse", "HEAD~2")
    work = repo.parent / "scratch"
    subprocess.run(["git", "clone", "--quiet", str(repo), str(work)], check=True)
    _git(work, "checkout", "--quiet", "--detach", frozen_head)
    assert not (work / "packaging" / "dev_provenance_manifest.json").is_file()
    facts = dev.verify(work, frozen_head)
    assert facts["state"] == "frozen"


def test_dev_missing_manifest_fails(dev: types.ModuleType, dev_repo: tuple[Path, str, str]) -> None:
    repo, _a, b = dev_repo
    (repo / "packaging" / "dev_provenance_manifest.json").unlink()
    with pytest.raises(dev.DevProvenanceError, match="no development manifest"):
        dev.verify(repo, b)


def test_dev_stale_source_fails(dev: types.ModuleType, dev_repo: tuple[Path, str, str]) -> None:
    """A later source change without a refreshed manifest fails closed."""
    repo, _a, b = dev_repo
    _write(repo, "docs/dev.md", "# development doc\n# altered\n")
    c = _commit(repo, "C: source drifted after A")
    with pytest.raises(dev.DevProvenanceError, match="refreshed development manifest"):
        dev.verify(repo, c)
    # Even at the manifest commit itself the frozen binding is intact, so
    # the failure is precisely the stale-source condition (not frozen drift).
    _git(repo, "checkout", "--quiet", "--detach", b)


def test_dev_omitted_input_fails(dev: types.ModuleType, dev_repo: tuple[Path, str, str]) -> None:
    """Removing a mapped input after A is an omitted-input failure."""
    repo, _a, b = dev_repo
    (repo / "config" / "adapter.example.toml").unlink()
    c = _commit(repo, "C: mapped input removed")
    with pytest.raises(
        dev.DevProvenanceError, match=r"missing=\['config/adapter\.example\.toml'\]"
    ):
        dev.verify(repo, c)
    _git(repo, "checkout", "--quiet", "--detach", b)


def test_dev_non_mapped_path_under_derived_metadata_fails(
    dev: types.ModuleType, dev_repo: tuple[Path, str, str]
) -> None:
    """A..HEAD may never carry non-derived changes: even a path that is NOT
    an input map (a script) moved under the derived-metadata commit fails,
    because the input map alone cannot see it (the A/B derived-only law)."""
    repo, _a, b = dev_repo
    _git(repo, "checkout", "--quiet", "--detach", b)
    _write(repo, "scripts/helper.py", "x = 1\n")
    _write(repo, "oap/active", "016-c\n")
    bad = _commit(repo, "bad: non-mapped path moved under B")
    with pytest.raises(dev.DevProvenanceError, match="non-derived development paths"):
        dev.verify(repo, bad)
    _git(repo, "checkout", "--quiet", "--detach", b)


def test_dev_altered_wheel_fails(dev: types.ModuleType, dev_repo: tuple[Path, str, str]) -> None:
    """A built wheel that does not reproduce the development source's
    recorded hash is an altered-artifact failure (bound to dist)."""
    repo, a, b = dev_repo
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
    (build / "README.md").write_text("# altered\n", encoding="utf-8")
    dist = build / "dist"
    dist.mkdir()
    uv = subprocess.run(["uv", "build", "--out-dir", str(dist)], cwd=build, capture_output=True)
    assert uv.returncode == 0, uv.stderr.decode()
    with pytest.raises(dev.DevProvenanceError, match="altered artifact"):
        dev.verify_artifacts(repo, manifest, dist)
    _git(repo, "checkout", "--quiet", "--detach", b)


def test_dev_frozen_metadata_touched_fails(
    dev: types.ModuleType, dev_repo: tuple[Path, str, str]
) -> None:
    """A development diff touching the frozen release metadata fails
    closed (the RC10 publication must stay byte-identical)."""
    repo, a, _b = dev_repo
    frozen_path = repo / "packaging" / "release_provenance_manifest.json"
    frozen = json.loads(frozen_path.read_text())
    frozen["artifacts"]["wheel"]["sha256"] = "f" * 64
    frozen_path.write_text(json.dumps(frozen, indent=2, sort_keys=True) + "\n")
    bad = _commit(repo, "bad: frozen metadata touched")
    with pytest.raises(dev.DevProvenanceError, match="frozen release metadata"):
        dev.verify(repo, bad)
    _git(repo, "checkout", "--quiet", "--detach", a)


def test_dev_frozen_manifest_rebound_fails(
    dev: types.ModuleType, dev_repo: tuple[Path, str, str]
) -> None:
    """A frozen manifest rebound to a later tree's map fails the frozen
    binding re-proof (the later-tree-map escape, frozen side)."""
    repo, _a, _b = dev_repo
    frozen_path = repo / "packaging" / "release_provenance_manifest.json"
    frozen = json.loads(frozen_path.read_text())
    frozen["source_inputs"] = dict(dev.map_from_directory(repo))
    frozen_path.write_text(json.dumps(frozen, indent=2, sort_keys=True) + "\n")
    bad = _commit(repo, "bad: frozen manifest rebound to a later tree")
    with pytest.raises(dev.DevProvenanceError, match="frozen RC10 source-input binding broken"):
        dev.verify(repo, bad)
    _git(repo, "checkout", "--quiet", "--detach", _b)


def test_dev_stale_rc_record_cannot_authorize(
    dev: types.ModuleType, dev_repo: tuple[Path, str, str]
) -> None:
    """The frozen record/qualification can never authorize publication of
    the altered development source: the frozen A/B binding at the current
    head fails closed (non-derived source paths moved since F)."""
    repo, _a, b = dev_repo
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


def test_dev_self_reference_excluded(
    dev: types.ModuleType, dev_repo: tuple[Path, str, str]
) -> None:
    """The development manifest and schema are deliberately excluded from
    the input map (self-referential metadata)."""
    repo, _a, _b = dev_repo
    tree_map = dev.map_from_directory(repo)
    assert "packaging/dev_provenance_manifest.json" not in tree_map
    assert "packaging/dev_provenance_manifest.schema.json" not in tree_map
    manifest = dev.load_dev_manifest(repo)
    assert manifest is not None
    for self_path in dev.DEV_DERIVED_METADATA_PATHS:
        assert self_path not in manifest["source_inputs"]
    assert manifest["self_referential_exclusions"] == sorted(dev.DEV_DERIVED_METADATA_PATHS)


def test_dev_label_law(dev: types.ModuleType, dev_repo: tuple[Path, str, str]) -> None:
    """Development images identify the development/source state and can
    never claim RC10 qualification."""
    repo, a, _b = dev_repo
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
    committed frozen manifest (independent cross-pin)."""
    dev = _load_dev_module()
    schema = json.loads(DEV_SCHEMA.read_text(encoding="utf-8"))
    frozen = json.loads(FROZEN_MANIFEST.read_text(encoding="utf-8"))
    fp = schema["properties"]["frozen_publication"]["properties"]
    assert fp["rc_identifier"]["const"] == frozen["candidate"]["rc_identifier"]
    assert fp["source_commit"]["const"] == frozen["generated_from"]["git_commit"]
    assert fp["wheel_sha256"]["const"] == frozen["artifacts"]["wheel"]["sha256"]
    assert fp["sdist_sha256"]["const"] == frozen["artifacts"]["sdist"]["sha256"]
    assert schema["$id"] == dev.SCHEMA_NAME
