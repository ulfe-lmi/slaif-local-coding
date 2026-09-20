"""Order 013-j, J4: mechanical source-input binding tests.

Proves the A/B source-binding law and the real-repository gate:

1. synthetic temporary git repositories (run UNCONDITIONALLY — no RC
   record required): the A/B happy path (derived-metadata-only child)
   passes; altered README, altered uv.lock, missing config file, altered
   compose, a sibling non-ancestor, a valid-shaped but wrong old recorded
   map, and a `generated_from` commit other than A all fail;
2. the real repository gate: the committed manifest's `source_inputs`
   equal the input map at the recorded source commit A AND the input map
   of the working tree, A is an ancestor of HEAD, and the A..HEAD diff
   touches only derived metadata or the OAP transcript.

Stdlib + git only; no network, no host state.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_MAP = REPO_ROOT / "scripts" / "source_input_map.py"
MANIFEST = REPO_ROOT / "packaging" / "release_provenance_manifest.json"

POLICY_PYPROJECT = (
    "[project]\n"
    'name = "fixture"\n'
    'version = "0.1.0"\n'
    "\n"
    "[tool.hatch.build]\n"
    'exclude = ["packaging/release_provenance_manifest.json", "oap/"]\n'
    "\n"
    "[tool.hatch.build.targets.sdist]\n"
    "include = [\n"
    '  "pyproject.toml",\n'
    '  "uv.lock",\n'
    '  "README.md",\n'
    '  "config/adapter.example.toml",\n'
    "]\n"
)


def _load_source_map() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("source_input_map", SOURCE_MAP)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load source input map module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def sim() -> types.ModuleType:
    return _load_source_map()


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
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture()
def ab_repo(sim: types.ModuleType, tmp_path: Path) -> tuple[Path, str, str]:
    """Synthetic repository with source commit A and a derived-metadata
    child B (the truthful A/B sequence)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _write(repo, "pyproject.toml", POLICY_PYPROJECT)
    _commit(repo, "base: build policy")
    _write(repo, "README.md", "# fixture\n")
    _write(repo, "uv.lock", "version = 1\n# lock A\n")
    _write(repo, "config/adapter.example.toml", "# config A\n")
    _write(repo, "compose.yaml", "name: fixture\n")
    commit_a = _commit(repo, "A: source inputs")
    # B: derived metadata + OAP transcript only.
    _write(repo, "packaging/release_provenance_manifest.json", '{"schema": "x"}\n')
    _write(repo, "oap/active", "013-j\n")
    commit_b = _commit(repo, "B: derived metadata")
    return repo, commit_a, commit_b


def test_ab_happy_path(sim: types.ModuleType, ab_repo: tuple[Path, str, str]) -> None:
    repo, a, b = ab_repo
    proven = sim.verify_ab(repo, a, b)
    # The five policy-selected inputs are bound at both commits.
    assert set(proven) == {
        "pyproject.toml",
        "uv.lock",
        "README.md",
        "config/adapter.example.toml",
        "compose.yaml",
    }
    # The working-tree variant of the map agrees at B.
    assert sim.map_from_directory(repo) == proven


def test_ab_rejects_altered_readme(sim: types.ModuleType, ab_repo: tuple[Path, str, str]) -> None:
    repo, a, _ = ab_repo
    _write(repo, "README.md", "# altered\n")
    b = _commit(repo, "bad: source moved under B")
    with pytest.raises(sim.InputMapError, match="non-derived paths"):
        sim.verify_ab(repo, a, b)


def test_ab_rejects_altered_uv_lock(sim: types.ModuleType, ab_repo: tuple[Path, str, str]) -> None:
    repo, a, _ = ab_repo
    _write(repo, "uv.lock", "version = 1\n# lock B (drifted)\n")
    b = _commit(repo, "bad: dependency lock drifted")
    with pytest.raises(sim.InputMapError):
        sim.verify_ab(repo, a, b)


def test_ab_rejects_missing_config(sim: types.ModuleType, ab_repo: tuple[Path, str, str]) -> None:
    repo, a, _ = ab_repo
    (repo / "config" / "adapter.example.toml").unlink()
    b = _commit(repo, "bad: config file removed")
    with pytest.raises(sim.InputMapError):
        sim.verify_ab(repo, a, b)


def test_ab_rejects_altered_compose(sim: types.ModuleType, ab_repo: tuple[Path, str, str]) -> None:
    repo, a, _ = ab_repo
    _write(repo, "compose.yaml", "name: altered\n")
    b = _commit(repo, "bad: compose drifted")
    with pytest.raises(sim.InputMapError):
        sim.verify_ab(repo, a, b)


def test_ab_rejects_sibling_non_ancestor(
    sim: types.ModuleType, ab_repo: tuple[Path, str, str]
) -> None:
    repo, a, _ = ab_repo
    # Sibling branch from the parent of A: A is NOT an ancestor of S.
    parent = _git(repo, "rev-parse", a + "^")
    _git(repo, "checkout", "-q", "-b", "sibling", parent)
    _write(repo, "oap/active", "sibling\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "sibling S")
    sibling = _git(repo, "rev-parse", "HEAD")
    with pytest.raises(sim.InputMapError, match="not an ancestor"):
        sim.verify_ab(repo, a, sibling)


def test_ab_rejects_valid_shaped_wrong_old_map(
    sim: types.ModuleType, ab_repo: tuple[Path, str, str]
) -> None:
    # A valid-shaped map from an OLD source (before the README change) is
    # wrong for A: the recorded map must equal A's inputs, not an ancestor's.
    repo, a, b = ab_repo
    # Build the wrong map: the parent commit's inputs (README differs? no —
    # use a map where one hash is altered: valid shape, wrong content).
    correct = sim.map_from_git_commit(repo, a)
    wrong = dict(correct)
    path = "README.md"
    body = correct[path]
    wrong[path] = "0" if body[0] != "0" else "1" + body[1:]
    with pytest.raises(sim.InputMapError, match="recorded map"):
        sim.verify_ab(repo, a, b, recorded_map=wrong)


def test_ab_rejects_generated_from_other_than_a(
    sim: types.ModuleType, ab_repo: tuple[Path, str, str]
) -> None:
    # The manifest's generated_from must be exactly A: a valid-shaped map
    # recorded at a DIFFERENT source commit (C, whose inputs drifted after
    # B) is wrong for A and must fail.
    repo, a, b = ab_repo
    _write(repo, "uv.lock", "version = 1\n# lock C (drifted)\n")
    c = _commit(repo, "C: drifted source")
    map_c = sim.map_from_git_commit(repo, c)
    with pytest.raises(sim.InputMapError, match="recorded map"):
        sim.verify_ab(repo, a, b, recorded_map=map_c)


def test_verify_ref_inputs_rejects_drifted_ref(
    sim: types.ModuleType, ab_repo: tuple[Path, str, str]
) -> None:
    repo, a, b = ab_repo
    recorded = sim.map_from_git_commit(repo, a)
    # B carries the same inputs (happy path).
    sim.verify_ref_inputs(repo, b, recorded)
    # A drifted ref (source moved) is rejected even though it is an
    # ancestor-or-equal relationship.
    _write(repo, "uv.lock", "version = 1\n# drifted at R\n")
    r = _commit(repo, "R: drifted lock")
    with pytest.raises(sim.InputMapError, match="input map differs"):
        sim.verify_ref_inputs(repo, r, recorded)


def test_real_repo_source_inputs_bound_to_committed_source(
    sim: types.ModuleType,
) -> None:
    """Real-repository unconditional gate (order 013-j, J4): the committed
    `source_inputs` equal the map at the recorded source A AND the map of
    the working tree; A..HEAD touches only derived metadata or oap/."""
    committed = json.loads(MANIFEST.read_text(encoding="utf-8"))
    recorded = committed.get("source_inputs")
    assert isinstance(recorded, dict) and recorded, (
        "committed manifest must carry a non-empty source_inputs map"
    )
    a = str(committed["generated_from"]["git_commit"])
    assert sim.map_from_git_commit(REPO_ROOT, a) == recorded
    assert sim.map_from_directory(REPO_ROOT) == recorded
    head = (
        subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            check=True,
        )
        .stdout.decode()
        .strip()
    )
    if a != head:
        is_ancestor = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", a, head],
            capture_output=True,
        )
        assert is_ancestor.returncode == 0, "source commit A is not an ancestor of HEAD"
    diff = (
        subprocess.run(
            ["git", "-C", str(REPO_ROOT), "diff", "--name-only", a, head],
            capture_output=True,
            check=True,
        )
        .stdout.decode()
        .splitlines()
    )
    for path in diff:
        assert path in sim.DERIVED_METADATA_PATHS or path.startswith("oap/"), (
            f"A..HEAD diff touches a non-derived path: {path}"
        )


def test_rc1_archive_is_immutable_and_excluded_from_artifact_inputs(
    sim: types.ModuleType,
) -> None:
    import hashlib

    archived = REPO_ROOT / "packaging/releases/0.1.0-rc1"
    expected = {
        "rc_record.json": "342ebbe122febfbc9122e7ffa90d436758ded1ce59a071312f57d8b0bce9e844",
        "rc_handoff.md": "01a8fe2ea058621ef7c949d4ed2b516596120eca29e3d08b3fdad22dc09a5553",
        "release_provenance_manifest.json": (
            "91934fdde7549775c806501a77538b8d17e8189d0b5d0583a6748cf20936003d"
        ),
    }
    for name, digest in expected.items():
        assert hashlib.sha256((archived / name).read_bytes()).hexdigest() == digest
    inputs = sim.map_from_directory(REPO_ROOT)
    assert not any(path.startswith("packaging/releases/") for path in inputs)
