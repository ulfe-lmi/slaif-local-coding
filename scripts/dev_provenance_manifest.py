"""Current-development provenance contract (order 016-b).

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


class DevProvenanceError(RuntimeError):
    pass


def dev_qualification_label(source_commit: str) -> str:
    """Development image qualification label (order 016-b): identifies the
    development/source state and can never claim RC10 qualification. It
    must contain 'not released' (the ordinary build-qualification label
    class) and must never contain an rc-candidate identity."""
    return f"development-source-{source_commit}; not a release candidate; not released"


def _is_40_hex(value: str) -> bool:
    return re.fullmatch(r"[0-9a-f]{40}", value) is not None


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True)
    return proc.stdout.decode().strip()


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


def load_dev_manifest(repo: Path) -> dict | None:
    """Strict loader. A malformed manifest is an error, never 'absent'."""
    path = repo / DEV_MANIFEST_PATH
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA_NAME:
        raise DevProvenanceError(f"{path} schema is not {SCHEMA_NAME}")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise DevProvenanceError(f"{path} schema_version is not {SCHEMA_VERSION}")
    if data.get("state") != "development":
        raise DevProvenanceError(f"{path} state is not 'development'")
    if data.get("release") is not False:
        raise DevProvenanceError(f"{path} release must be false")
    for key in ("source_commit", "repository", "source_inputs", "artifacts", "toolchain"):
        if key not in data:
            raise DevProvenanceError(f"{path} is missing {key!r}")
    if not _is_40_hex(str(data["source_commit"])):
        raise DevProvenanceError(f"{path} source_commit is not 40-hex")
    # Non-release invariants: a development manifest must never carry an RC
    # or release identity of its own.
    for forbidden in ("rc_identifier", "candidate", "oci", "published"):
        if forbidden in data:
            raise DevProvenanceError(f"{path} carries a forbidden identity key {forbidden!r}")
    return data


def current_state(repo: Path, head: str | None = None) -> tuple[str, dict]:
    """Determine the artifact state at `head` (default: working tree/HEAD).

    Returns (state, frozen_manifest) where state is 'frozen' when the
    current source-input map equals the frozen RC10 recorded map (no
    development manifest required) and 'development' otherwise (a valid
    development manifest is then mandatory).
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
    if map_from_git_commit(repo, head) == recorded:
        return "frozen", frozen
    return "development", frozen


def verify_development(repo: Path, head: str, manifest: dict) -> dict[str, object]:
    """Full development-state verification (fail closed). Returns facts."""
    a = str(manifest["source_commit"])
    if not _git_exists(repo, a):
        raise DevProvenanceError(f"development source commit {a[:12]} missing from repo")
    if not _is_ancestor(repo, a, head):
        raise DevProvenanceError(
            f"development source {a[:12]} is not an ancestor of {head[:12]}; "
            "refresh the development manifest"
        )
    recorded = manifest["source_inputs"]
    if not isinstance(recorded, dict) or not recorded:
        raise DevProvenanceError("development manifest has no usable source_inputs")
    # Self-reference: the manifest and its schema are deliberately excluded
    # from the input map (they are derived metadata, never artifact inputs).
    for self_path in DEV_DERIVED_METADATA_PATHS:
        if self_path in recorded:
            raise DevProvenanceError(
                f"development manifest self-references its own metadata: {self_path}"
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
    map_tree = map_from_directory(repo)
    if map_tree != recorded:
        missing = sorted(set(recorded) - set(map_tree))
        extra = sorted(set(map_tree) - set(recorded))
        altered = sorted(p for p in set(recorded) & set(map_tree) if recorded[p] != map_tree[p])
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
    fp = manifest.get("frozen_publication")
    if not isinstance(fp, dict):
        raise DevProvenanceError("development manifest is missing frozen_publication")
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
    label = str(manifest.get("qualification_label", ""))
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
    return {"source_commit": a, "inputs": len(recorded), "changed_after_a": changed}


def verify_artifacts(repo: Path, manifest: dict, dist: Path) -> None:
    """Bind the freshly built artifacts in `dist` to the development
    manifest's exact recorded hashes (altered-wheel / altered-sdist
    negatives)."""
    recorded = manifest.get("artifacts", {})
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


def verify(repo: Path, head: str | None = None, dist: Path | None = None) -> dict[str, object]:
    """State-aware verification gate (the CI fresh-build binding).

    - frozen state: passes once the frozen RC10 binding is re-proved; when a
      dist is given, the built artifacts must additionally equal the frozen
      manifest's recorded hashes.
    - development state: the full development verification must pass; when a
      dist is given, the built artifacts must equal the development
      manifest's recorded hashes.
    """
    if head is None:
        head = _git(repo, "rev-parse", "HEAD")
    state, frozen = current_state(repo, head)
    result: dict[str, object] = {"state": state, "head": head}
    if state == "frozen":
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
    facts = verify_development(repo, head, manifest)
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


def generate(repo: Path, source: str | None = None, objective: str = "016-b") -> dict:
    """Generate the development manifest at a clean source commit A.

    Requires the working-tree input map to equal A's input map (no uncommitted
    source drift), then writes the manifest (commit B adds it). The manifest
    records A, A's input map, the cleanly built wheel/sdist hashes, the
    toolchain/lock facts, the frozen-publication cross-check facts, the
    self-referential exclusions and the development qualification label.
    """
    if source is None:
        source = _git(repo, "rev-parse", "HEAD")
    if not _is_40_hex(source):
        raise DevProvenanceError("source must be 40-hex")
    if not _git_exists(repo, source):
        raise DevProvenanceError("source does not exist in the repository")
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
        "repository": "ulfe-lmi/slaif-local-coding",
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
    out = repo / DEV_MANIFEST_PATH
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def _uv_version() -> str:
    proc = subprocess.run(["uv", "--version"], capture_output=True, check=True)
    return proc.stdout.decode().split()[1]


def emit_state(repo: Path, out_file: str | Path) -> dict[str, str]:
    """Emit the CI artifact state, failing closed on any bad development
    state (a missing/stale manifest never silently degrades to frozen)."""
    head = _git(repo, "rev-parse", "HEAD")
    state, frozen = current_state(repo, head)
    if state == "frozen":
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
        verify_development(repo, head, manifest)
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
