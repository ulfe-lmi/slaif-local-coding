"""Order 014-c, workstream C.3: ordinary CI runs the prepublication
record-present rehearsal at HEAD BEFORE publication.

The RC4 rejection proved that a stale ``0.1.0-rc3`` const in the
record-present state escaped every prepublication gate because ordinary CI
had no ``packaging/rc_record.json`` and the record-present branch ran only
after publication. This hook closes the gap permanently: the deterministic,
network-free rehearsal (``scripts/rc_record_present_rehearsal.py``)
exercises the full record-present/``rc_published`` validation path at the
candidate source on every CI run.

Regression anchor: the rehearsal MUST FAIL at the rejected RC4 image source
``601a7f9fae19869ad8e09f10fa994550368fd87c`` (stale ``candidate.rc_identifier``
const ``0.1.0-rc3`` in the record-present state) — the exact RC4 escape.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
REHEARSAL = REPO_ROOT / "scripts" / "rc_record_present_rehearsal.py"

# The rejected RC4 image source / workflow head (immutable; order 014-c).
RC4_SOURCE = "601a7f9fae19869ad8e09f10fa994550368fd87c"


def _run_rehearsal(source: str | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(REHEARSAL)]
    if source is not None:
        cmd += ["--source", source]
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=2400)


def test_record_present_rehearsal_passes_at_head() -> None:
    """The full record-present/``rc_published`` validation path must pass
    at the current candidate source before publication (order 014-c,
    WS-C.1/WS-C.3): candidate record/handoff/published-state provenance,
    the strict record/provenance/schema/docs/Docker-record gates, the
    candidate label/tag/version branch, and the tamper classes."""
    if shutil.which("uv") is None:
        pytest.fail("uv is required for the record-present rehearsal candidate build")
    proc = _run_rehearsal()
    assert proc.returncode == 0, (
        "record-present rehearsal FAILED at HEAD:\n"
        f"--- stdout ---\n{proc.stdout[-4000:]}\n"
        f"--- stderr ---\n{proc.stderr[-4000:]}"
    )
    assert "record-present rehearsal PASSED" in proc.stdout


def test_rehearsal_catches_rc4_stale_rc3_residue() -> None:
    """The rehearsal must have caught the RC3 hardcode at RC4 source
    ``601a7f9...`` (order 014-c, WS-C.3): the stale prior-RC const in the
    record-present state fails the candidate label/tag/version branch
    closed, before any gate suite or publication."""
    proc = _run_rehearsal(RC4_SOURCE)
    assert proc.returncode == 1, (
        "rehearsal unexpectedly PASSED at the rejected RC4 source "
        f"{RC4_SOURCE}:\n{proc.stdout[-2000:]}"
    )
    assert "record-present rehearsal FAILED" in proc.stderr


# ---------------------------------------------------------------------------
# Order 014-e, workstream B: focused coverage proving the corrected
# POST-mode single qualified source branch (the fd1aeb6 rehearsal fix)
# BEFORE the new candidate freeze.
#
# The branch under test: when the record's image source boundary differs
# from the candidate source (POST mode at a derived-metadata head), the
# rehearsal must prove (a) image_source_commit == workflow_head_sha,
# (b) the boundary is the candidate source or an ANCESTOR of it (a record
# naming an unrelated or later commit fails closed), and (c) no mapped
# input changed after the boundary (candidate-source map equals the
# boundary map). The full rehearsal exercises this end-to-end at the final
# published head; these cases pin each rejection class in isolation,
# deterministically, without uv/network/Docker.
# ---------------------------------------------------------------------------

import importlib.util  # noqa: E402
import json  # noqa: E402
import types  # noqa: E402
from typing import Any  # noqa: E402

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

GENERATOR_STUB = (
    'RC_IDENTIFIER = "0.1.0-rc8"\n'
    'RC_QUALIFICATION_LABEL = "rc-candidate-0.1.0-rc8; private; not final release"\n'
)

SCHEMA_STUB = (
    '{"properties": {"oci": {"properties": {"candidate_tag": {"const": "0.1.0-rc8"}}},'
    ' "candidate": {"properties": {"rc_identifier": {"const": "0.1.0-rc8"}}}}}\n'
)

DIGEST_STUB = "sha256:" + "d" * 64


def _load_rehearsal() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("rc_rehearsal_branch", REHEARSAL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _branch_git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", *args],
        capture_output=True,
        check=True,
    )
    return proc.stdout.decode().strip()


def _branch_write(repo: Path, rel: str, content: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _branch_commit(repo: Path, message: str) -> str:
    _branch_git(repo, "add", "-A")
    _branch_git(repo, "commit", "-q", "-m", message)
    return _branch_git(repo, "rev-parse", "HEAD")


def _boundary_record(repo: Path, map_fn: Any, boundary: str) -> dict[str, object]:
    """A record fully consistent with the named boundary commit."""
    return {
        "rc_identifier": "0.1.0-rc8",
        "image_source_commit": boundary,
        "workflow_head_sha": boundary,
        "oci_tags": ["0.1.0-rc8", f"sha-{boundary}"],
        "oci_image_digest": DIGEST_STUB,
        "source_input_hashes": map_fn(repo, boundary),
    }


def _install_record(repo: Path, record: dict[str, object]) -> None:
    """Materialize the record-present state in the working tree (the map
    functions read the committed trees; the record/manifest are derived
    metadata, excluded from every input map)."""
    manifest = {
        "candidate": {"rc_identifier": "0.1.0-rc8", "state": "rc_published"},
        "oci": {
            "candidate_tag": "0.1.0-rc8",
            "image_digest": DIGEST_STUB,
            "published": True,
            "labels": {
                "slaif-local-coding.qualification": (
                    "rc-candidate-0.1.0-rc8; private; not final release"
                )
            },
        },
        "status": {"rc_published": True},
        "source_inputs": record["source_input_hashes"],
    }
    _branch_write(repo, "packaging/rc_record.json", json.dumps(record, indent=2) + "\n")
    _branch_write(
        repo,
        "packaging/release_provenance_manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )


@pytest.fixture()
def branch_repo(tmp_path: Path) -> tuple[Path, str, str, str, str]:
    """Synthetic record-present repository: source boundary S, a
    derived-metadata-only child D (the POST candidate head), an unrelated
    sibling boundary X (same inputs; oap-only difference), and a later
    descendant L of D."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _branch_git(repo, "init", "-q")
    _branch_write(repo, "pyproject.toml", POLICY_PYPROJECT)
    _branch_write(repo, "README.md", "# fixture\n")
    _branch_write(repo, "uv.lock", "version = 1\n")
    _branch_write(repo, "config/adapter.example.toml", "# config\n")
    _branch_write(repo, "scripts/release_provenance_manifest.py", GENERATOR_STUB)
    _branch_write(repo, "packaging/release_provenance_manifest.schema.json", SCHEMA_STUB)
    source = _branch_commit(repo, "S: source boundary")
    # Derived-metadata-only child (POST candidate head).
    _branch_write(repo, "oap/active", "014-e\n")
    derived = _branch_commit(repo, "D: derived metadata only")
    # Unrelated sibling boundary (same inputs; oap-only difference).
    _branch_git(repo, "checkout", "-q", "-b", "sibling", source)
    _branch_write(repo, "oap/active", "other\n")
    sibling = _branch_commit(repo, "X: unrelated boundary")
    _branch_git(repo, "checkout", "-q", derived)
    # Later descendant of the candidate (a record must never name it).
    _branch_write(repo, "oap/active", "later\n")
    later = _branch_commit(repo, "L: later commit")
    _branch_git(repo, "checkout", "-q", "--detach", derived)
    return repo, source, derived, sibling, later


def test_post_branch_accepts_ancestor_boundary_with_identical_map(
    branch_repo: tuple[Path, str, str, str, str],
) -> None:
    rehearsal = _load_rehearsal()
    repo, source, derived, _sibling, _later = branch_repo
    record = _boundary_record(repo, rehearsal.map_from_git_commit, source)
    _install_record(repo, record)
    # PRE-equivalent: boundary == candidate source.
    rehearsal._assert_candidate_branch(repo, source)
    # POST: derived-metadata head above the boundary, identical map.
    _branch_git(repo, "checkout", "-q", "--detach", derived)
    rehearsal._assert_candidate_branch(repo, derived)


def test_post_branch_rejects_unrelated_boundary(
    branch_repo: tuple[Path, str, str, str, str],
) -> None:
    rehearsal = _load_rehearsal()
    repo, _source, derived, sibling, _later = branch_repo
    record = _boundary_record(repo, rehearsal.map_from_git_commit, sibling)
    _install_record(repo, record)
    _branch_git(repo, "checkout", "-q", "--detach", derived)
    with pytest.raises(rehearsal.RehearsalError):
        rehearsal._assert_candidate_branch(repo, derived)


def test_post_branch_rejects_later_boundary(
    branch_repo: tuple[Path, str, str, str, str],
) -> None:
    rehearsal = _load_rehearsal()
    repo, _source, derived, _sibling, later = branch_repo
    record = _boundary_record(repo, rehearsal.map_from_git_commit, later)
    _install_record(repo, record)
    _branch_git(repo, "checkout", "-q", "--detach", derived)
    with pytest.raises(rehearsal.RehearsalError):
        rehearsal._assert_candidate_branch(repo, derived)


def test_post_branch_rejects_mapped_change_after_boundary(
    branch_repo: tuple[Path, str, str, str, str],
) -> None:
    rehearsal = _load_rehearsal()
    repo, source, _derived, _sibling, _later = branch_repo
    record = _boundary_record(repo, rehearsal.map_from_git_commit, source)
    _install_record(repo, record)
    # A mapped input changes after the boundary (candidate != boundary).
    _branch_write(repo, "README.md", "# fixture\n# altered mapped input\n")
    drift_head = _branch_commit(repo, "drift: mapped input altered")
    with pytest.raises(rehearsal.RehearsalError):
        rehearsal._assert_candidate_branch(repo, drift_head)
