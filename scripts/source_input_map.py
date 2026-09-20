"""Artifact source-input map (order 013-j, J4/J5).

Mechanical ``path -> sha256`` identity map of EVERY file that is an input to
the wheel, the sdist, the OCI image build, or the runtime configuration.
Purpose: provenance must bind the recorded artifacts to the ACTUAL source
inputs, not to a merely-ancestor commit whose inputs may differ.

The map is derived deterministically from (tree listing, pyproject build
policy, Dockerfile). It is:

1. recorded in the provenance manifest ``source_inputs`` section at
   generation time (from the recorded source commit A);
2. re-proved at the derived-metadata commit B: the inputs at A and B must be
   identical, and the A..B diff may only touch derived/excluded files
   (``verify_ab``);
3. re-proved at the image source S before any registry publication: the
   inputs at S must equal the recorded map (``verify_ref_inputs``).

Exclusions (self-reference and non-artifact surfaces) are explicit: the
provenance manifest and its schema, post-publication records
(``rc_record.json``, ``rc_handoff.md``, ``release_record.json``), the OAP
transcript, ``scripts/``, ``references/``, the agent documents, caches, build
outputs, and placeholder files. Exclusions come from the pyproject
``[tool.hatch.build]`` policy (the same policy hatchling applies) plus the
derived-metadata set below, so a policy change moves the map mechanically.

Stdlib + git (subprocess) only; no new dependencies.

Usage:

    # Prove the A/B source-binding (A = source inputs commit, B = the
    # derived-metadata child): inputs identical, diff confined to
    # derived/excluded paths, and (when given) equal to the recorded map.
    python scripts/source_input_map.py --ab A B \
        [--manifest packaging/release_provenance_manifest.json]

    # Prove that a ref (e.g. the image source S at publication) carries
    # exactly the recorded input map.
    python scripts/source_input_map.py --ref S \
        --manifest packaging/release_provenance_manifest.json
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import subprocess
import sys
from pathlib import Path

# Post-publication generated metadata and self-referential files that must
# never be artifact inputs (order 013-j, J4 self-reference exclusion).
DERIVED_METADATA_PATHS: frozenset[str] = frozenset(
    {
        "packaging/release_provenance_manifest.json",
        "packaging/release_provenance_manifest.schema.json",
        "packaging/rc_record.json",
        "packaging/rc_handoff.md",
        "packaging/release_record.json",
    }
)


# The A..B (source -> derived metadata) diff may touch only these paths:
# derived metadata plus the OAP transcript (oap/ is excluded from every
# artifact by the pyproject policy and is orchestration, not source).
def _is_derived_diff_path(path: str) -> bool:
    return path in DERIVED_METADATA_PATHS or path.startswith("oap/")


class InputMapError(RuntimeError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_build_policy(pyproject_path: Path) -> tuple[list[str], list[str]]:
    import tomllib

    with pyproject_path.open("rb") as stream:
        pyproject = tomllib.load(stream)
    hatch = pyproject["tool"]["hatch"]["build"]
    exclude = [str(entry) for entry in hatch["exclude"]]
    sdist_include = [str(entry) for entry in hatch["targets"]["sdist"]["include"]]
    return sdist_include, exclude


def _excluded(rel: str, exclude_patterns: list[str]) -> bool:
    for pattern in exclude_patterns:
        if rel == pattern or rel.startswith(pattern + "/"):
            return True
        if fnmatch.fnmatch(rel, pattern):
            return True
    return False


def input_paths_from_listing(
    paths: list[str],
    sdist_include: list[str],
    exclude: list[str],
) -> list[str]:
    """Pure policy step: which of the existing paths are artifact inputs.

    Union of (a) the sdist include policy (the deliberate developer-only
    whitelist, directories walked to files), (b) the wheel inputs (the
    runtime package plus the README metadata and the license file), and
    (c) the OCI build-context configuration files (Dockerfile, both compose
    files, .dockerignore). The pyproject top-level exclusions apply to all.
    """
    sdist: set[str] = set()
    existing = set(paths)
    for entry in sdist_include:
        if entry in existing:
            sdist.add(entry)
        elif entry + "/" in {p + "/" for p in paths}:
            continue  # handled below by prefix walk
        prefix = entry if entry.endswith("/") else entry + "/"
        for p in paths:
            if p.startswith(prefix):
                sdist.add(p)
    wheel = {"src/slaif_local_coding", "README.md", "LICENSE"}
    oci = {"Dockerfile", "compose.yaml", "compose.build.yaml", ".dockerignore"}
    candidate: set[str] = set()
    for base in sdist:
        if base in existing:
            candidate.add(base)
        else:
            candidate.update(p for p in paths if p.startswith(base + "/"))
    for base in wheel:
        if base in existing:
            candidate.add(base)
        else:
            candidate.update(p for p in paths if p.startswith(base + "/"))
    candidate.update(p for p in oci if p in existing)
    out = sorted(p for p in candidate if not _excluded(p, exclude))
    return out


def map_for_listing(
    paths: list[str],
    read_bytes,
    sdist_include: list[str],
    exclude: list[str],
) -> dict[str, str]:
    """Pure mapping step: path -> sha256 over the policy-selected inputs."""
    selected = input_paths_from_listing(paths, sdist_include, exclude)
    return {path: _sha256_bytes(read_bytes(path)) for path in selected}


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True)
    return proc.stdout.decode().strip()


def _git_blob_paths(repo: Path, commit: str) -> list[str]:
    out = _git(repo, "ls-tree", "-r", "--name-only", commit)
    return [line for line in out.splitlines() if line]


def map_from_git_commit(repo: Path, commit: str) -> dict[str, str]:
    """Input map of a commit's tree (blobs read via `git show`)."""
    paths = _git_blob_paths(repo, commit)
    sdist_include, exclude = _load_build_policy(repo / "pyproject.toml")

    def read(path: str) -> bytes:
        proc = subprocess.run(
            ["git", "-C", str(repo), "show", f"{commit}:{path}"],
            capture_output=True,
            check=True,
        )
        return proc.stdout

    return map_for_listing(paths, read, sdist_include, exclude)


def map_from_directory(root: Path) -> dict[str, str]:
    """Input map of a directory tree (the working-tree variant)."""
    paths: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.split("/", 1)[0] in (".git", ".venv", "node_modules"):
            continue
        paths.append(rel)
    sdist_include, exclude = _load_build_policy(root / "pyproject.toml")
    selected = input_paths_from_listing(paths, sdist_include, exclude)
    return {rel: _sha256_bytes((root / rel).read_bytes()) for rel in selected}


def verify_ab(
    repo: Path,
    commit_a: str,
    commit_b: str,
    recorded_map: dict[str, str] | None = None,
) -> dict[str, str]:
    """Mechanically prove the A/B source binding (order 013-j, J4).

    1. A is an ancestor of B (or equal);
    2. every changed path in A..B is derived/excluded metadata or oap/
       (no source input moves under a derived-metadata commit);
    3. the input map at A equals the input map at B (and, when given, the
       recorded map).

    Returns the proven input map. Raises InputMapError on any violation —
    a valid-shaped but wrong old source, an altered dependency lock, or a
    missing/altered config or compose file all fail here.
    """
    for commit in (commit_a, commit_b):
        if not _is_40_hex(commit):
            raise InputMapError(f"commit must be 40-hex: {commit!r}")
    _git(repo, "cat-file", "-e", commit_a)
    _git(repo, "cat-file", "-e", commit_b)
    is_ancestor = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", commit_a, commit_b],
        capture_output=True,
    )
    if is_ancestor.returncode != 0:
        raise InputMapError(
            f"{commit_a[:12]} is not an ancestor of {commit_b[:12]}; the "
            "derived-metadata commit must be a child of the source commit"
        )
    diff = _git(repo, "diff", "--name-only", commit_a, commit_b)
    changed = [line for line in diff.splitlines() if line]
    bad = [path for path in changed if not _is_derived_diff_path(path)]
    if bad:
        raise InputMapError(
            "A..B diff touches non-derived paths (source moved under a "
            f"derived-metadata commit): {sorted(bad)}"
        )
    map_a = map_from_git_commit(repo, commit_a)
    map_b = map_from_git_commit(repo, commit_b)
    if map_a != map_b:
        only_a = sorted(set(map_a) - set(map_b))
        only_b = sorted(set(map_b) - set(map_a))
        drifted = sorted(p for p in set(map_a) & set(map_b) if map_a[p] != map_b[p])
        raise InputMapError(
            "source inputs differ between A and B: "
            f"missing_at_b={only_a} missing_at_a={only_b} altered={drifted}"
        )
    if recorded_map is not None and map_a != recorded_map:
        raise InputMapError("input map at A differs from the recorded map")
    return map_a


def verify_ref_inputs(repo: Path, ref: str, recorded_map: dict[str, str]) -> None:
    """Prove that `ref` (e.g. the image source S at publication) carries
    exactly the recorded input map — no missing, added, or altered input.
    An ancestor relationship is NOT sufficient (order 013-j, J4)."""
    if not _is_40_hex(ref):
        raise InputMapError(f"ref must be 40-hex: {ref!r}")
    _git(repo, "cat-file", "-e", ref)
    actual = map_from_git_commit(repo, ref)
    if actual != recorded_map:
        missing = sorted(set(recorded_map) - set(actual))
        extra = sorted(set(actual) - set(recorded_map))
        altered = sorted(p for p in set(recorded_map) & set(actual) if recorded_map[p] != actual[p])
        raise InputMapError(
            f"ref {ref[:12]} input map differs from the recorded map: "
            f"missing={missing} extra={extra} altered={altered}"
        )


def _is_40_hex(value: str) -> bool:
    import re

    return re.fullmatch(r"[0-9a-f]{40}", value) is not None


def _recorded_map(manifest_path: Path) -> dict[str, str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    data = manifest.get("source_inputs")
    if not isinstance(data, dict) or not data:
        raise InputMapError(f"{manifest_path} has no usable source_inputs section")
    return {str(k): str(v) for k, v in data.items()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--ab",
        nargs=2,
        metavar=("A", "B"),
        help="prove the A/B source binding (A = source inputs, B = derived metadata)",
    )
    group.add_argument("--ref", help="prove a ref carries the recorded input map")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="committed manifest carrying the recorded source_inputs (optional for --ab)",
    )
    args = parser.parse_args(argv)
    repo = Path(__file__).resolve().parents[1]
    recorded = _recorded_map(args.manifest) if args.manifest else None
    try:
        if args.ab is not None:
            commit_a, commit_b = args.ab
            proven = verify_ab(repo, commit_a, commit_b, recorded)
            print(
                f"input-map A/B binding OK: {commit_a[:12]} == {commit_b[:12]} "
                f"({len(proven)} input files)"
            )
        else:
            verify_ref_inputs(repo, args.ref, recorded)
            print(f"input-map ref OK: {args.ref[:12]} matches the recorded map")
    except InputMapError as exc:
        print(f"input-map FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
