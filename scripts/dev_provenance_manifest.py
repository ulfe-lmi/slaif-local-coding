"""Current-development provenance contract (orders 016-b / 016-c).

After the frozen ``0.1.0-rc10`` publication, the repository continues
development. The frozen RC10 record/manifest/handoff bytes are immutable and
continue to be validated against their exact frozen source, but the working
tree inevitably diverges from the frozen RC10 source-input map the moment a
document, script, test or workflow input changes.

This module defines the SEPARATE current-development provenance contract that
keeps that divergence honest without touching the frozen publication:

- ``packaging/dev_provenance_manifest.json`` (schema
  ``slaif-dev-provenance-v1``) records, for one exact source commit A:
  the mechanical source-input map at A, the hashes of the wheel and sdist
  cleanly built from A, the toolchain/lock facts, the non-release state,
  the deliberately excluded self-referential metadata, and the development
  qualification label for development images.
- A is bound to the derived-metadata commit B that adds the manifest: the
  A..B (and A..HEAD) diff may touch only the development manifest paths and
  the OAP transcript, and the input map must remain identical (the same
  A/B law as the frozen contract, with the development derived set).
- Every later source change requires a refreshed development manifest; a
  missing/invalid/stale manifest FAILS when the current source differs from
  the frozen publication (it never returns early, skips a failure, relaxes
  an exact hash, or replaces an accepted historical hash).
- The frozen RC10 binding is re-proved on every verification: the recorded
  frozen source commit's map must still equal the frozen manifest's
  ``source_inputs``, and no development diff may touch the frozen release
  metadata. The frozen RC10 record can therefore never authorize publication
  of altered development source.

Order 016-c verifier guards:

- State classification and CI state emission bind the committed map AND the
  actual working-tree map: dirty or untracked mapped inputs never acquire
  frozen or development authority (a clean frozen tree remains supported
  without a development manifest).
- The closed development contract is enforced on every public consumption
  path, including callers of :func:`verify_development` that bypass
  :func:`load_dev_manifest` (e.g. the record-present rehearsal): exact
  keys/types/values, safe artifact basenames, valid hashes, non-negative
  sizes/counts (booleans are not integers), source-input path/hash records
  without path escape, toolchain facts, the exact current ``uv.lock``
  binding, frozen-publication constants and the declared self-exclusions.
  The executable validation and the JSON schema agree.
- Freeze immutability has an independent baseline: every existing top-level
  and archived publication record/manifest/handoff at the pinned pre-rework
  baseline must still exist (head tree and working tree) byte-identical,
  and no new top-level or archived publication record may appear. The
  development manifest never chooses the freeze authority; the production
  CLI uses the pinned repository baseline (typed helper arguments exist for
  hermetic fixtures only).

The development manifest is excluded from every artifact input (pyproject
build policy) and self-referentially from its own input map; the wheel/sdist
it records are built from ``git archive A`` exactly like the rehearsal
candidate build, so the hash is a source proof, not an arbitrary
working-copy hash.

Stdlib + git + uv (for --generate builds) only; no new dependencies.

Usage:

    # Generate the development manifest at the current clean source commit
    # (default: HEAD). Writes packaging/dev_provenance_manifest.json.
    python scripts/dev_provenance_manifest.py --generate [--source <40-hex>]

    # Verify the current state at HEAD (frozen or development); with
    # --dist, also bind the freshly built artifacts in that directory.
    python scripts/dev_provenance_manifest.py --verify [--head <40-hex>]
        [--dist <dir>]

    # Emit the CI artifact state (frozen|development, expected wheel
    # sha256, qualification label) to a file, failing closed on any
    # invalid/stale development state.
    python scripts/dev_provenance_manifest.py --emit-state <output-file>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from source_input_map import (  # noqa: E402
    DERIVED_METADATA_PATHS,
    InputMapError,
    map_from_directory,
    map_from_git_commit,
    verify_ab,  # noqa: F401  (re-exported for the frozen-side binding tests)
)

SCHEMA_NAME = "slaif-dev-provenance-v1"
SCHEMA_VERSION = 1
DEV_MANIFEST_PATH = Path("packaging/dev_provenance_manifest.json")
DEV_SCHEMA_PATH = Path("packaging/dev_provenance_manifest.schema.json")
FROZEN_MANIFEST_PATH = Path("packaging/release_provenance_manifest.json")

# Order 016-c: the independently verified pre-rework freeze baseline — the
# remote main HEAD from which objective 016 began. The pinned constant is
# the production freeze authority: the development manifest (untrusted
# derived metadata) never chooses it, and the production CLI never accepts
# a caller-supplied alternative. Typed helper arguments exist solely so
# hermetic test fixtures can model their own explicit baseline.
PRE_REWORK_BASELINE_COMMIT = "f3793af9e5f05bdfba19ef800eeaf57177d0ed2b"

# Candidate top-level publication records/manifests/handoffs. The freeze
# set is whatever of these EXISTS at the pre-rework baseline plus the whole
# archived publication tree (``packaging/releases/``) at that baseline. A
# candidate absent at the baseline must not appear later (a new top-level
# publication record would be new freeze authority, not development).
FROZEN_TOP_LEVEL_PUBLICATION_PATHS: tuple[str, ...] = (
    "packaging/rc_artifact_record.schema.json",
    "packaging/rc_handoff.md",
    "packaging/rc_record.json",
    "packaging/release_provenance_manifest.json",
    "packaging/release_provenance_manifest.schema.json",
    "packaging/release_record.json",
)

# Development-state derived metadata: the only non-OAP paths that may appear
# in a diff between the development source commit A and any later commit
# (manifest commit B, report-only commits, ...). The OAP transcript (oap/)
# is orchestration, not source, and is allowed exactly as in the frozen
# A/B law (source_input_map._is_derived_diff_path).
DEV_DERIVED_METADATA_PATHS: frozenset[str] = frozenset(
    {
        "packaging/dev_provenance_manifest.json",
        "packaging/dev_provenance_manifest.schema.json",
    }
)

# Release metadata that a development diff must never touch: rebinding or
# altering the frozen publication is not development.
FROZEN_RELEASE_METADATA_PATHS: frozenset[str] = frozenset(DERIVED_METADATA_PATHS) | {
    "packaging/releases",
}

_OBJECTIVE_RE = re.compile(r"^[0-9]{3}-[a-z]{1,2}$")
_HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_PYTHON_RE = re.compile(r"^3\.12\.[0-9]+$")
_UV_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
_LABEL_RE = re.compile(r"^development-source-[0-9a-f]{40}; not a release candidate; not released$")
_ARTIFACT_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,254}$")

# Closed-contract key sets (mirrors packaging/dev_provenance_manifest.
# schema.json: additionalProperties false at every level).
_TOP_LEVEL_KEYS: frozenset[str] = frozenset(
    {
        "schema",
        "schema_version",
        "state",
        "release",
        "objective",
        "repository",
        "source_commit",
        "frozen_publication",
        "source_inputs",
        "artifacts",
        "toolchain",
        "self_referential_exclusions",
        "qualification_label",
    }
)
_FROZEN_PUBLICATION_KEYS: frozenset[str] = frozenset(
    {
        "manifest_path",
        "schema",
        "rc_identifier",
        "source_commit",
        "wheel_sha256",
        "sdist_sha256",
    }
)
_ARTIFACT_KEYS: frozenset[str] = frozenset({"name", "sha256", "size_bytes", "entry_count"})
_TOOLCHAIN_KEYS: frozenset[str] = frozenset({"python", "uv_version", "uv_lock_sha256"})

REPOSITORY_IDENTITY = "ulfe-lmi/slaif-local-coding"
FROZEN_SCHEMA_NAME = "slaif-release-provenance-v5"
FROZEN_RC_IDENTIFIER = "0.1.0-rc10"

# The schema pins minProperties 100 on the source-input map (the real
# repository's scale fact); the executable validation enforces the same
# minimum so the two never diverge.
MIN_SOURCE_INPUTS = 100


class DevProvenanceError(RuntimeError):
    pass


def dev_qualification_label(source_commit: str) -> str:
    """Development image qualification label (order 016-b): identifies the
    development/source state and can never claim RC10 qualification. It
    must contain 'not released' (the ordinary build-qualification label
    class) and must never contain an rc-candidate identity."""
    return f"development-source-{source_commit}; not a release candidate; not released"


def _is_40_hex(value: str) -> bool:
    return _HEX40_RE.fullmatch(value) is not None


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True)
    return proc.stdout.decode().strip()


def _git_show(repo: Path, ref: str) -> bytes:
    proc = subprocess.run(["git", "-C", str(repo), "show", ref], capture_output=True, check=True)
    return proc.stdout


def _is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    if ancestor == descendant:
        return True
    proc = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", ancestor, descendant],
        capture_output=True,
    )
    return proc.returncode == 0


def _diff_paths(repo: Path, a: str, b: str) -> list[str]:
    out = _git(repo, "diff", "--name-only", a, b)
    return [line for line in out.splitlines() if line]


def _is_safe_source_path(value: object) -> bool:
    """A repository-relative POSIX source path: no absolute path, no
    backslashes, no traversal, no empty components, no control bytes."""
    if not isinstance(value, str) or not value or value in (".", ".."):
        return False
    if "\\" in value or value.startswith("/"):
        return False
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in value):
        return False
    return all(part and part != ".." for part in value.split("/"))


def _is_safe_artifact_name(value: object) -> bool:
    """A safe artifact basename: plain filename characters only, no path
    separator, no traversal, bounded length."""
    if not isinstance(value, str) or not _ARTIFACT_NAME_RE.fullmatch(value):
        return False
    return value not in (".", "..")


def _is_real_int(value: object, minimum: int) -> bool:
    """JSON booleans parse as Python ints; they are never valid counts."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= minimum


def _exact_keys(data: object, keys: frozenset[str], where: str) -> dict:
    if not isinstance(data, dict):
        raise DevProvenanceError(f"{where} must be a JSON object")
    if any(not isinstance(k, str) for k in data):
        raise DevProvenanceError(f"{where} carries a non-string key")
    missing = sorted(keys - data.keys())
    if missing:
        raise DevProvenanceError(f"{where} is missing required keys: {missing}")
    unexpected = sorted(set(data) - keys)
    if unexpected:
        raise DevProvenanceError(f"{where} carries unexpected keys: {unexpected}")
    return data


def _validate_dev_manifest(data: object) -> dict:
    """Strict closed-contract validation (order 016-c).

    Mirrors ``packaging/dev_provenance_manifest.schema.json``: exact key
    sets at every level (additionalProperties false), const values,
    patterns, and type exactness (a boolean used where an integer is
    required is rejected; malformed nested objects are rejected).
    Repository-dependent cross-checks (frozen manifest facts, the current
    ``uv.lock`` binding, input maps, the pre-rework freeze baseline) run in
    :func:`verify_development`.
    """
    doc = _exact_keys(data, _TOP_LEVEL_KEYS, "development manifest")
    if doc["schema"] != SCHEMA_NAME:
        raise DevProvenanceError(f"development manifest schema is not {SCHEMA_NAME!r}")
    if not _is_real_int(doc["schema_version"], 0) or doc["schema_version"] != SCHEMA_VERSION:
        raise DevProvenanceError("development manifest schema_version is not 1")
    if doc["state"] != "development":
        raise DevProvenanceError("development manifest state is not 'development'")
    if doc["release"] is not False:
        raise DevProvenanceError("development manifest release must be false")
    if not isinstance(doc["objective"], str) or not _OBJECTIVE_RE.fullmatch(doc["objective"]):
        raise DevProvenanceError("development manifest objective is not NNN-L")
    if doc["repository"] != REPOSITORY_IDENTITY:
        raise DevProvenanceError(f"development manifest repository is not {REPOSITORY_IDENTITY!r}")
    if not isinstance(doc["source_commit"], str) or not _is_40_hex(doc["source_commit"]):
        raise DevProvenanceError("development manifest source_commit is not 40-hex")

    fp = _exact_keys(doc["frozen_publication"], _FROZEN_PUBLICATION_KEYS, "frozen_publication")
    if fp["manifest_path"] != str(FROZEN_MANIFEST_PATH):
        raise DevProvenanceError("frozen_publication.manifest_path is not the frozen manifest")
    if fp["schema"] != FROZEN_SCHEMA_NAME:
        raise DevProvenanceError(f"frozen_publication.schema is not {FROZEN_SCHEMA_NAME!r}")
    if fp["rc_identifier"] != FROZEN_RC_IDENTIFIER:
        raise DevProvenanceError(
            f"frozen_publication.rc_identifier is not {FROZEN_RC_IDENTIFIER!r}"
        )
    if not isinstance(fp["source_commit"], str) or not _is_40_hex(fp["source_commit"]):
        raise DevProvenanceError("frozen_publication.source_commit is not 40-hex")
    for kind in ("wheel", "sdist"):
        value = fp[f"{kind}_sha256"]
        if not isinstance(value, str) or not _HEX64_RE.fullmatch(value):
            raise DevProvenanceError(f"frozen_publication.{kind}_sha256 is not 64-hex")

    inputs = doc["source_inputs"]
    if not isinstance(inputs, dict) or not inputs:
        raise DevProvenanceError("development manifest source_inputs is not an object")
    if any(not _is_safe_source_path(k) for k in inputs):
        bad = sorted(k for k in inputs if not _is_safe_source_path(k))
        raise DevProvenanceError(
            f"development manifest source_inputs carries an unsafe or escaping path: {bad[:5]}"
        )
    if any(not isinstance(v, str) or not _HEX64_RE.fullmatch(v) for v in inputs.values()):
        raise DevProvenanceError(
            "development manifest source_inputs carries a non-64-hex sha256 value"
        )
    if len(inputs) < MIN_SOURCE_INPUTS:
        raise DevProvenanceError(
            "development manifest source_inputs has fewer than the schema's "
            f"minimum of {MIN_SOURCE_INPUTS} records"
        )

    artifacts = _exact_keys(doc["artifacts"], frozenset({"wheel", "sdist"}), "artifacts")
    for kind in ("wheel", "sdist"):
        spec = _exact_keys(artifacts[kind], _ARTIFACT_KEYS, f"artifacts.{kind}")
        if not _is_safe_artifact_name(spec["name"]):
            raise DevProvenanceError(f"artifacts.{kind}.name is not a safe basename")
        if not isinstance(spec["sha256"], str) or not _HEX64_RE.fullmatch(spec["sha256"]):
            raise DevProvenanceError(f"artifacts.{kind}.sha256 is not 64-hex")
        if not _is_real_int(spec["size_bytes"], 1):
            raise DevProvenanceError(
                f"artifacts.{kind}.size_bytes must be an integer of at least 1"
            )
        if not _is_real_int(spec["entry_count"], 1):
            raise DevProvenanceError(
                f"artifacts.{kind}.entry_count must be an integer of at least 1"
            )

    toolchain = _exact_keys(doc["toolchain"], _TOOLCHAIN_KEYS, "toolchain")
    if not isinstance(toolchain["python"], str) or not _PYTHON_RE.fullmatch(toolchain["python"]):
        raise DevProvenanceError("toolchain.python is not a pinned 3.12.x version")
    if not isinstance(toolchain["uv_version"], str) or not _UV_VERSION_RE.fullmatch(
        toolchain["uv_version"]
    ):
        raise DevProvenanceError("toolchain.uv_version is not major.minor.patch")
    if not isinstance(toolchain["uv_lock_sha256"], str) or not _HEX64_RE.fullmatch(
        toolchain["uv_lock_sha256"]
    ):
        raise DevProvenanceError("toolchain.uv_lock_sha256 is not 64-hex")

    exclusions = doc["self_referential_exclusions"]
    if (
        not isinstance(exclusions, list)
        or len(exclusions) != 2
        or len(set(exclusions)) != 2
        or sorted(exclusions) != sorted(DEV_DERIVED_METADATA_PATHS)
    ):
        raise DevProvenanceError(
            "self_referential_exclusions is not exactly the development metadata path set"
        )

    label = doc["qualification_label"]
    if not isinstance(label, str) or not _LABEL_RE.fullmatch(label):
        raise DevProvenanceError(
            "qualification_label is not the deterministic development-source label"
        )
    return doc


def load_dev_manifest(repo: Path) -> dict | None:
    """Strict loader. A malformed manifest is an error, never 'absent'."""
    path = repo / DEV_MANIFEST_PATH
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    _validate_dev_manifest(data)
    return data


def frozen_publication_paths(repo: Path, baseline_commit: str) -> set[str]:
    """The independent freeze set (order 016-c): the existing top-level
    publication records/manifests/handoffs at the pre-rework baseline plus
    every archived publication record under ``packaging/releases/``."""
    if not _is_40_hex(baseline_commit):
        raise DevProvenanceError("freeze baseline must be 40-hex")
    tree = _git(repo, "ls-tree", "-r", "--name-only", baseline_commit)
    baseline_files = {line for line in tree.splitlines() if line}
    top = {p for p in FROZEN_TOP_LEVEL_PUBLICATION_PATHS if p in baseline_files}
    archived = {p for p in baseline_files if p.startswith("packaging/releases/")}
    return top | archived


def verify_frozen_publication_baseline(
    repo: Path, baseline_commit: str, head: str | None = None
) -> int:
    """Independent freeze-immutability guard (order 016-c).

    Every existing top-level and archived publication record/manifest/
    handoff at the pre-rework baseline must still exist — in the verified
    head's tree AND in the working tree — with byte-identical content, and
    no new top-level or archived publication record may have appeared.
    The baseline is the pinned repository authority (or the typed fixture
    argument); the development manifest never chooses it.
    """
    if not _is_40_hex(baseline_commit):
        raise DevProvenanceError("freeze baseline must be 40-hex")
    if not _git_exists(repo, baseline_commit):
        raise DevProvenanceError(
            f"freeze baseline {baseline_commit[:12]} is missing from the repository"
        )
    if head is None:
        head = _git(repo, "rev-parse", "HEAD")
    if not _is_ancestor(repo, baseline_commit, head):
        raise DevProvenanceError("freeze baseline is not an ancestor of the verified head")
    baseline_paths = frozen_publication_paths(repo, baseline_commit)
    head_tree = {
        line for line in _git(repo, "ls-tree", "-r", "--name-only", head).splitlines() if line
    }
    missing = sorted(p for p in baseline_paths if p not in head_tree)
    if missing:
        raise DevProvenanceError(
            f"frozen publication paths deleted after the pre-rework baseline: {missing[:10]}"
        )
    current_top = {p for p in FROZEN_TOP_LEVEL_PUBLICATION_PATHS if p in head_tree}
    baseline_top = {p for p in FROZEN_TOP_LEVEL_PUBLICATION_PATHS if p in baseline_paths}
    extra_top = sorted(current_top - baseline_top)
    if extra_top:
        raise DevProvenanceError(
            "new top-level publication record(s) appeared after the pre-rework "
            f"baseline (new freeze authority is not development): {extra_top}"
        )
    current_archived = {p for p in head_tree if p.startswith("packaging/releases/")}
    extra_archived = sorted(current_archived - baseline_paths)
    if extra_archived:
        raise DevProvenanceError(
            "new archived publication record(s) appeared after the pre-rework "
            f"baseline: {extra_archived[:10]}"
        )
    for path in sorted(baseline_paths):
        baseline_bytes = _git_show(repo, f"{baseline_commit}:{path}")
        head_bytes = _git_show(repo, f"{head}:{path}")
        if baseline_bytes != head_bytes:
            raise DevProvenanceError(
                "frozen publication bytes differ from the pre-rework baseline "
                f"(committed at {head[:12]}): {path}"
            )
        work = repo / path
        if not work.is_file():
            raise DevProvenanceError(
                f"frozen publication path missing from the working tree: {path}"
            )
        if work.read_bytes() != baseline_bytes:
            raise DevProvenanceError(
                "frozen publication bytes differ from the pre-rework baseline "
                f"(working tree): {path}"
            )
    return len(baseline_paths)


def current_state(
    repo: Path,
    head: str | None = None,
    tree_map: dict[str, str] | None = None,
) -> tuple[str, dict]:
    """Determine the artifact state at `head` (default: HEAD).

    Returns (state, frozen_manifest) where state is 'frozen' when the
    current source-input map equals the frozen RC10 recorded map (no
    development manifest required) and 'development' otherwise (a valid
    development manifest is then mandatory).

    Order 016-c: when `tree_map` (the ACTUAL working-tree input map) is
    given, the committed map at `head` must equal it as well — dirty or
    untracked mapped inputs never acquire frozen or development authority.
    A clean frozen tree remains supported without a development manifest.
    """
    if head is None:
        head = _git(repo, "rev-parse", "HEAD")
    frozen = json.loads((repo / FROZEN_MANIFEST_PATH).read_text(encoding="utf-8"))
    recorded = frozen.get("source_inputs")
    if not isinstance(recorded, dict) or not recorded:
        raise DevProvenanceError(f"{FROZEN_MANIFEST_PATH} has no usable source_inputs")
    a_frozen = str(frozen["generated_from"]["git_commit"])
    if not _is_ancestor(repo, a_frozen, head):
        raise DevProvenanceError(
            f"frozen source commit {a_frozen[:12]} is not an ancestor of {head[:12]}"
        )
    # Frozen binding re-proof: the frozen map must still equal the map at the
    # exact frozen source commit (the record can never be quietly rebound).
    if map_from_git_commit(repo, a_frozen) != recorded:
        raise DevProvenanceError(
            "frozen RC10 source-input binding broken: the map at the recorded "
            "frozen source commit differs from the committed frozen manifest"
        )
    map_head = map_from_git_commit(repo, head)
    if tree_map is not None and tree_map != map_head:
        missing = sorted(set(map_head) - set(tree_map))
        extra = sorted(set(tree_map) - set(map_head))
        altered = sorted(p for p in set(map_head) & set(tree_map) if map_head[p] != tree_map[p])
        raise DevProvenanceError(
            "working tree differs from the committed source at the verified "
            "head: dirty or untracked mapped inputs do not acquire artifact "
            f"authority (missing={missing[:5]} extra={extra[:5]} altered={altered[:5]})"
        )
    if map_head == recorded:
        return "frozen", frozen
    return "development", frozen


def verify_development(
    repo: Path,
    head: str,
    manifest: dict,
    tree_map: dict[str, str] | None = None,
    baseline_commit: str | None = None,
) -> dict[str, object]:
    """Full development-state verification (fail closed). Returns facts.

    Order 016-c: this function validates the closed development contract
    itself (callers may bypass :func:`load_dev_manifest`, e.g. the
    record-present rehearsal), binds the actual working tree to the
    committed source, binds the recorded lock to the current ``uv.lock``,
    and enforces the independent pre-rework freeze baseline (never chosen
    by the manifest).
    """
    doc = _validate_dev_manifest(manifest)
    a = str(doc["source_commit"])
    if not _git_exists(repo, a):
        raise DevProvenanceError(f"development source commit {a[:12]} missing from repo")
    if not _is_ancestor(repo, a, head):
        raise DevProvenanceError(
            f"development source {a[:12]} is not an ancestor of {head[:12]}; "
            "refresh the development manifest"
        )
    recorded = doc["source_inputs"]
    # Self-reference: the manifest and its schema are deliberately excluded
    # from the input map (they are derived metadata, never artifact inputs).
    for self_path in DEV_DERIVED_METADATA_PATHS:
        if self_path in recorded:
            raise DevProvenanceError(
                f"development manifest self-references its own metadata: {self_path}"
            )
    # Order 016-c: the independent pre-rework freeze baseline (the pinned
    # repository authority by default; the typed argument exists for
    # hermetic fixtures only). The development manifest never chooses it.
    baseline = str(baseline_commit) if baseline_commit is not None else PRE_REWORK_BASELINE_COMMIT
    freeze_paths = verify_frozen_publication_baseline(repo, baseline, head)
    # Order 016-c: exact current lock binding — the recorded lock hash must
    # equal the actual uv.lock bytes (a zeroed or stale lock hash fails).
    lock_path = repo / "uv.lock"
    if not lock_path.is_file():
        raise DevProvenanceError("uv.lock is missing; the lock cannot be bound")
    if doc["toolchain"]["uv_lock_sha256"] != hashlib.sha256(lock_path.read_bytes()).hexdigest():
        raise DevProvenanceError(
            "development manifest toolchain.uv_lock_sha256 does not bind the current uv.lock"
        )
    # Stale-source / omitted-input / altered-input detection, in three
    # independent comparisons (recorded commit, head commit, working tree).
    map_a = map_from_git_commit(repo, a)
    if map_a != recorded:
        raise DevProvenanceError(
            "development manifest is stale for its own source commit: the "
            f"recorded input map differs from the map at {a[:12]}"
        )
    map_head = map_from_git_commit(repo, head)
    if map_head != recorded:
        missing = sorted(set(recorded) - set(map_head))
        extra = sorted(set(map_head) - set(recorded))
        altered = sorted(p for p in set(recorded) & set(map_head) if recorded[p] != map_head[p])
        raise DevProvenanceError(
            "current source differs from the development source commit "
            f"(missing={missing[:5]} extra={extra[:5]} altered={altered[:5]}); "
            "every later source change requires a refreshed development manifest"
        )
    if tree_map is None:
        tree_map = map_from_directory(repo)
    if tree_map != recorded:
        missing = sorted(set(recorded) - set(tree_map))
        extra = sorted(set(tree_map) - set(recorded))
        altered = sorted(p for p in set(recorded) & set(tree_map) if tree_map[p] != recorded[p])
        raise DevProvenanceError(
            "working tree differs from the development source commit "
            f"(missing={missing[:5]} extra={extra[:5]} altered={altered[:5]})"
        )
    # The A..head diff may touch only development derived metadata and the
    # OAP transcript; it must never touch source inputs or frozen release
    # metadata.
    changed = _diff_paths(repo, a, head)
    frozen_touched = sorted(
        {path for path in changed if path in FROZEN_RELEASE_METADATA_PATHS}
        | {path for path in changed if path.startswith("packaging/releases/")}
    )
    if frozen_touched:
        raise DevProvenanceError(
            "development diff touches frozen release metadata (the RC10 "
            f"publication must stay byte-identical): {frozen_touched[:10]}"
        )
    bad = [
        path
        for path in changed
        if path not in DEV_DERIVED_METADATA_PATHS and not path.startswith("oap/")
    ]
    if bad:
        raise DevProvenanceError(
            "A..HEAD diff touches non-derived development paths (source moved "
            f"under a derived-metadata commit): {sorted(bad)[:10]}"
        )
    # Frozen publication facts recorded in the development manifest must
    # still match the committed frozen manifest (tamper cross-check).
    frozen = json.loads((repo / FROZEN_MANIFEST_PATH).read_text(encoding="utf-8"))
    fp = doc["frozen_publication"]
    if fp.get("manifest_path") != str(FROZEN_MANIFEST_PATH):
        raise DevProvenanceError("development manifest names the wrong frozen manifest")
    if fp.get("rc_identifier") != frozen["candidate"]["rc_identifier"]:
        raise DevProvenanceError("development manifest frozen rc_identifier drifted")
    if fp.get("source_commit") != frozen["generated_from"]["git_commit"]:
        raise DevProvenanceError("development manifest frozen source_commit drifted")
    for kind in ("wheel", "sdist"):
        if fp.get(f"{kind}_sha256") != frozen["artifacts"][kind]["sha256"]:
            raise DevProvenanceError(f"development manifest frozen {kind}_sha256 drifted")
    # Non-release label law.
    label = str(doc.get("qualification_label", ""))
    if label != dev_qualification_label(a):
        raise DevProvenanceError(
            "development qualification label is not the deterministic "
            f"development-source label for {a[:12]}"
        )
    if "not released" not in label or "rc-candidate" in label:
        raise DevProvenanceError(
            "development qualification label must state 'not released' and "
            "never carry an rc-candidate identity"
        )
    return {
        "source_commit": a,
        "inputs": len(recorded),
        "changed_after_a": changed,
        "freeze_baseline": baseline,
        "freeze_baseline_paths": freeze_paths,
    }


def verify_artifacts(repo: Path, manifest: dict, dist: Path) -> None:
    """Bind the freshly built artifacts in `dist` to the development
    manifest's exact recorded hashes (altered-wheel / altered-sdist
    negatives)."""
    doc = _validate_dev_manifest(manifest)
    recorded = doc.get("artifacts", {})
    for kind in ("wheel", "sdist"):
        spec = recorded.get(kind)
        if not isinstance(spec, dict) or not all(
            k in spec for k in ("name", "sha256", "size_bytes", "entry_count")
        ):
            raise DevProvenanceError(f"development manifest artifacts.{kind} is malformed")
        path = dist / str(spec["name"])
        if not path.is_file():
            raise DevProvenanceError(f"built artifact missing from dist: {path.name}")
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != spec["sha256"]:
            raise DevProvenanceError(
                f"built {kind} hash {digest[:12]}... != development manifest "
                f"{spec['sha256'][:12]}... (altered artifact for the development source)"
            )
        if len(data) != int(spec["size_bytes"]):
            raise DevProvenanceError(f"built {kind} size differs from the development manifest")
        if _entry_count(path, kind) != int(spec["entry_count"]):
            raise DevProvenanceError(f"built {kind} entry count differs")


def verify(
    repo: Path,
    head: str | None = None,
    dist: Path | None = None,
    baseline_commit: str | None = None,
) -> dict[str, object]:
    """State-aware verification gate (the CI fresh-build binding).

    - frozen state: passes once the frozen RC10 binding is re-proved, the
      working tree is bound to the committed map, and the independent
      pre-rework freeze baseline holds; when a dist is given, the built
      artifacts must additionally equal the frozen manifest's recorded
      hashes.
    - development state: the full development verification must pass; when
      a dist is given, the built artifacts must equal the development
      manifest's recorded hashes.

    ``baseline_commit`` is the typed hermetic-fixture argument (order
    016-c); the production CLI never supplies it, so the pinned repository
    baseline remains the freeze authority.
    """
    if head is None:
        head = _git(repo, "rev-parse", "HEAD")
    tree_map = map_from_directory(repo)
    state, frozen = current_state(repo, head, tree_map=tree_map)
    result: dict[str, object] = {"state": state, "head": head}
    if state == "frozen":
        baseline = (
            str(baseline_commit) if baseline_commit is not None else PRE_REWORK_BASELINE_COMMIT
        )
        result["freeze_baseline_paths"] = verify_frozen_publication_baseline(repo, baseline, head)
        if dist is not None:
            _verify_frozen_artifacts(frozen, dist)
        return result
    manifest = load_dev_manifest(repo)
    if manifest is None:
        raise DevProvenanceError(
            "current source differs from the frozen RC10 publication but no "
            "development manifest exists; every later source change requires "
            "a refreshed development manifest"
        )
    facts = verify_development(
        repo, head, manifest, tree_map=tree_map, baseline_commit=baseline_commit
    )
    result["development"] = facts
    if dist is not None:
        verify_artifacts(repo, manifest, dist)
    return result


def _verify_frozen_artifacts(frozen: dict, dist: Path) -> None:
    for kind in ("wheel", "sdist"):
        spec = frozen["artifacts"][kind]
        path = dist / str(spec["name"])
        if not path.is_file():
            raise DevProvenanceError(f"built artifact missing from dist: {path.name}")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != spec["sha256"]:
            raise DevProvenanceError(
                f"built {kind} hash differs from the frozen manifest "
                "(current source must equal the frozen publication to claim it)"
            )
        if len(data) != int(spec["size_bytes"]):
            raise DevProvenanceError(f"built {kind} size differs from the frozen manifest")


def _entry_count(path: Path, kind: str) -> int:
    if kind == "wheel":
        with zipfile.ZipFile(path) as zf:
            return len(zf.namelist())
    with tarfile.open(path) as tf:
        return len(tf.getnames())


def _git_exists(repo: Path, commit: str) -> bool:
    return (
        subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", commit], capture_output=True
        ).returncode
        == 0
    )


def _artifact_facts(path: Path, kind: str) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "name": path.name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
        "entry_count": _entry_count(path, kind),
    }


def _build_from_source(repo: Path, source: str, workdir: Path) -> tuple[Path, str]:
    """Clean build of the exact source commit (git archive + uv build; the
    same mechanism as the record-present rehearsal). Returns the (dist dir,
    normalized project name) for artifact discovery."""
    import tomllib

    build_tree = workdir / "build"
    build_tree.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "-C", str(repo), "archive", "--output", str(workdir / "a.tar"), source],
        check=True,
        capture_output=True,
    )
    subprocess.run(["tar", "-x", "-f", str(workdir / "a.tar"), "-C", str(build_tree)], check=True)
    with (build_tree / "pyproject.toml").open("rb") as stream:
        project_name = str(tomllib.load(stream)["project"]["name"])
    dist = workdir / "dist"
    dist.mkdir()
    uv = shutil.which("uv")
    if uv is None:
        raise DevProvenanceError("uv is required for the development manifest build")
    proc = subprocess.run(
        [uv, "build", "--out-dir", str(dist)], cwd=build_tree, capture_output=True
    )
    if proc.returncode != 0:
        raise DevProvenanceError(
            "development candidate build failed: " + proc.stderr.decode()[:4000]
        )
    return dist, project_name.replace("-", "_")


def generate(
    repo: Path,
    source: str | None = None,
    objective: str = "016-b",
    baseline_commit: str | None = None,
) -> dict:
    """Generate the development manifest at a clean source commit A.

    Requires the working-tree input map to equal A's input map (no
    uncommitted source drift) and the independent pre-rework freeze
    baseline to hold, then writes the manifest (commit B adds it). The
    manifest records A, A's input map, the cleanly built wheel/sdist
    hashes, the toolchain/lock facts, the frozen-publication cross-check
    facts, the self-referential exclusions and the development
    qualification label.
    """
    if source is None:
        source = _git(repo, "rev-parse", "HEAD")
    if not _is_40_hex(source):
        raise DevProvenanceError("source must be 40-hex")
    if not _git_exists(repo, source):
        raise DevProvenanceError("source does not exist in the repository")
    baseline = str(baseline_commit) if baseline_commit is not None else PRE_REWORK_BASELINE_COMMIT
    verify_frozen_publication_baseline(repo, baseline, source)
    map_a = map_from_git_commit(repo, source)
    map_tree = map_from_directory(repo)
    if map_a != map_tree:
        missing = sorted(set(map_a) - set(map_tree))
        extra = sorted(set(map_tree) - set(map_a))
        altered = sorted(p for p in set(map_a) & set(map_tree) if map_a[p] != map_tree[p])
        raise DevProvenanceError(
            "working tree differs from the development source commit; commit "
            f"all source first (missing={missing[:5]} extra={extra[:5]} "
            f"altered={altered[:5]})"
        )
    for self_path in DEV_DERIVED_METADATA_PATHS:
        if self_path in map_a:
            raise DevProvenanceError(
                f"development metadata is not excluded from the build policy: {self_path}"
            )
    with tempfile.TemporaryDirectory(prefix="slaif-dev-provenance-") as tmp:
        dist, project = _build_from_source(repo, source, Path(tmp))
        wheels = sorted(dist.glob(f"{project}-*.whl"))
        sdists = sorted(dist.glob(f"{project}-*.tar.gz"))
        if len(wheels) != 1 or len(sdists) != 1:
            raise DevProvenanceError(
                "development build must produce exactly one wheel and one "
                f"sdist (got wheels={[w.name for w in wheels]} "
                f"sdists={[s.name for s in sdists]})"
            )
        wheel_facts = _artifact_facts(wheels[0], "wheel")
        sdist_facts = _artifact_facts(sdists[0], "sdist")

    frozen = json.loads((repo / FROZEN_MANIFEST_PATH).read_text(encoding="utf-8"))
    lock = (repo / "uv.lock").read_bytes()
    manifest = {
        "schema": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "state": "development",
        "release": False,
        "objective": objective,
        "repository": REPOSITORY_IDENTITY,
        "source_commit": source,
        "frozen_publication": {
            "manifest_path": str(FROZEN_MANIFEST_PATH),
            "schema": frozen["schema"],
            "rc_identifier": frozen["candidate"]["rc_identifier"],
            "source_commit": frozen["generated_from"]["git_commit"],
            "wheel_sha256": frozen["artifacts"]["wheel"]["sha256"],
            "sdist_sha256": frozen["artifacts"]["sdist"]["sha256"],
        },
        "source_inputs": map_a,
        "artifacts": {
            "wheel": wheel_facts,
            "sdist": sdist_facts,
        },
        "toolchain": {
            "python": platform.python_version(),
            "uv_version": _uv_version(),
            "uv_lock_sha256": hashlib.sha256(lock).hexdigest(),
        },
        "self_referential_exclusions": sorted(DEV_DERIVED_METADATA_PATHS),
        "qualification_label": dev_qualification_label(source),
    }
    _validate_dev_manifest(manifest)
    out = repo / DEV_MANIFEST_PATH
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def _uv_version() -> str:
    proc = subprocess.run(["uv", "--version"], capture_output=True, check=True)
    return proc.stdout.decode().split()[1]


def emit_state(
    repo: Path, out_file: str | Path, baseline_commit: str | None = None
) -> dict[str, str]:
    """Emit the CI artifact state, failing closed on any bad development
    state (a missing/stale manifest never silently degrades to frozen).

    Order 016-c: the working tree is bound to the committed map before any
    state is emitted, the full closed contract is verified in the
    development state, and the independent pre-rework freeze baseline is
    enforced in both states. Nothing usable is written on invalid state.
    ``baseline_commit`` is the typed hermetic-fixture argument; the
    production CLI never supplies it.
    """
    head = _git(repo, "rev-parse", "HEAD")
    tree_map = map_from_directory(repo)
    state, frozen = current_state(repo, head, tree_map=tree_map)
    if state == "frozen":
        baseline = (
            str(baseline_commit) if baseline_commit is not None else PRE_REWORK_BASELINE_COMMIT
        )
        verify_frozen_publication_baseline(repo, baseline, head)
        values = {
            "state": "frozen",
            "expected_wheel_sha256": frozen["artifacts"]["wheel"]["sha256"],
            "qualification_label": frozen["oci"]["labels"]["slaif-local-coding.qualification"],
            "source_commit": frozen["generated_from"]["git_commit"],
        }
    else:
        manifest = load_dev_manifest(repo)
        if manifest is None:
            raise DevProvenanceError("development state without a development manifest at HEAD")
        verify_development(repo, head, manifest, tree_map=tree_map, baseline_commit=baseline_commit)
        values = {
            "state": "development",
            "expected_wheel_sha256": manifest["artifacts"]["wheel"]["sha256"],
            "qualification_label": str(manifest["qualification_label"]),
            "source_commit": str(manifest["source_commit"]),
        }
    # Shell-sourceable (values quoted) so CI can bind the emitted state
    # directly: `state`, `expected_wheel_sha256`, `qualification_label`,
    # `source_commit`.
    Path(out_file).write_text(
        "\n".join(f"{k}={shlex.quote(v)}" for k, v in values.items()) + "\n",
        encoding="utf-8",
    )
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--verify", action="store_true", help="verify the current state at HEAD")
    group.add_argument("--generate", action="store_true", help="generate the development manifest")
    group.add_argument("--emit-state", metavar="FILE", help="emit the CI artifact state to FILE")
    parser.add_argument("--head", default=None, help="40-hex verification head (default: HEAD)")
    parser.add_argument("--source", default=None, help="40-hex development source (generate)")
    parser.add_argument(
        "--objective",
        default="016-b",
        help="objective identifier recorded for provenance (generate)",
    )
    parser.add_argument("--dist", type=Path, default=None, help="built artifacts dir to bind")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        if args.generate:
            manifest = generate(args.repo, args.source, args.objective)
            print(
                "development manifest written: source="
                f"{manifest['source_commit'][:12]} inputs="
                f"{len(manifest['source_inputs'])} wheel="
                f"{manifest['artifacts']['wheel']['sha256'][:12]}... sdist="
                f"{manifest['artifacts']['sdist']['sha256'][:12]}..."
            )
        elif args.verify:
            if not _is_40_hex(args.head or "") and args.head:
                raise DevProvenanceError("--head must be 40-hex")
            facts = verify(args.repo, args.head, args.dist)
            print(
                f"development provenance OK: state={facts['state']} head={str(facts['head'])[:12]}"
            )
        else:
            values = emit_state(args.repo, args.emit_state)
            print(f"artifact state: {values['state']} source={values['source_commit'][:12]}")
    except (DevProvenanceError, InputMapError) as exc:
        print(f"development provenance FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
