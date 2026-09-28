"""Deterministic prepublication record-present rehearsal (order 014-c,
workstream C).

The RC4 rejection showed that the record-present / ``rc_published``
validation path only executed AFTER publication, so a stale RC3 identity
residue in the record-present state escaped every prepublication gate.
This rehearsal closes that gap permanently, BEFORE any publication:

- it builds a DISPOSABLE git clone of the candidate source (local clone,
  no network, no registry, no secret backend, no model, no Docker);
- PRE-PUBLICATION mode (no ``packaging/rc_record.json`` at the source):
  it cleanly builds the candidate wheel/sdist from ``git archive <source>``,
  synthesizes well-formed digest/run/time facts and a sanitized PASSING
  qualification ledger (synthetic ledger number 900, bound to the
  candidate source/wheel), generates the candidate provenance
  (pre-freeze state), runs the corrected source-ref-bound RC record
  builder, regenerates the rc-published provenance state, and runs the
  strict record / provenance / schema / docs / Docker-record gate set in
  the disposable tree;
- POST-PUBLICATION mode (a record already exists at the source): it runs
  the same gate set against the REAL record and proves the identity
  bindings;
- in both modes it proves the candidate label/tag/version branch (the
  generator's own RC identifier, qualification label, candidate tag,
  schema consts, record tag pair, and the single qualified source
  boundary), proves the record's evidence binding (the named ledger must
  re-derive the record's compatibility block, and the frozen handoff must
  be the deterministic render of the record), and exercises the tamper
  classes: stale prior-RC label/tag, source mismatch, changed mapped test
  input, wrong workflow head, wrong source alias, and later-tree map.

Exit code 0: every rehearsal gate passed. 1: a rehearsal gate failed.
2: usage/environment error. Stdlib + git + uv (build cache) only.

Usage:

    python scripts/rc_record_present_rehearsal.py \
        [--source <40-hex candidate source, default: repo HEAD>] \
        [--repo <repo root, default: this repository>] \
        [--workdir <disposable dir, default: mktemp>] \
        [--keep]
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from source_input_map import map_from_directory, map_from_git_commit  # noqa: E402

# Synthetic, clearly non-registry rehearsal facts (deterministic constants;
# never a real digest, run, or timestamp).
REHEARSAL_LEDGER = "900"
REHEARSAL_DIGEST = "sha256:" + "9" * 64
REHEARSAL_RUN_ID = 900000000
REHEARSAL_PUBLISHED_AT = "2026-01-01T00:00:00Z"
REHEARSAL_FACTS_CREATED_AT = "2026-01-01T00:00:00Z"

# Real, committed qualification ledgers usable as stale prior-RC evidence
# targets (the rehearsal repo always carries them).
REAL_LEDGER_NUMBERS = ("003", "002", "001")

# The focused record-present gate set (the strict record/provenance/schema/
# docs/Docker-record gates; no Docker, no network, no registry).
REHEARSAL_TEST_FILES = (
    "tests/test_rc_record.py",
    "tests/test_release_provenance_manifest.py",
    "tests/test_source_input_binding.py",
    "tests/test_docker_qualification_record_gate.py",
    "tests/test_docs_consistency.py",
    "tests/test_release_registry_publish_digest.py",
    "tests/test_release_registry_publish_gate.py",
)


class RehearsalError(RuntimeError):
    pass


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RehearsalError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True)
    return proc.stdout.decode().strip()


def _clone_source(repo: Path, source: str, workdir: Path) -> Path:
    """Local disposable clone of the candidate source (no network).

    ``--no-local`` forces the plain file transport (object copy instead of
    the hardlink optimization), which is required when the workdir lives on
    a different filesystem/device than the repository (NAS mounts)."""
    clone = workdir / "clone"
    subprocess.run(
        ["git", "clone", "--no-local", "--quiet", str(repo), str(clone)],
        check=True,
        capture_output=True,
    )
    _git(clone, "checkout", "--quiet", "--detach", source)
    return clone


def _synthetic_facts(rc_mod: Any, wheel_sha256: str) -> dict[str, Any]:
    """A fully valid, sanitized, PASSING closed-schema v2 facts record for
    the synthetic rehearsal ledger (bound to the candidate wheel; the
    retained qualified client identity; fixed deterministic facts)."""
    arms: dict[str, dict[str, Any]] = {}
    for arm, reqs, compiler_calls, cache_entries in (
        ("VISION", 2, 0, 0),
        ("CACHE", 2, 1, 1),
        ("BOTH", 2, 1, 1),
    ):
        arms[arm] = {
            "attempts": 1,
            "exit_status": 0,
            "duration_seconds": 10,
            "sentinel_present": True,
            "sentinel_size_bytes": 3,
            "adapter_requests_ok": reqs,
            "adapter_requests_500": 0,
            "adapter_requests_422": 0,
            "adapter_requests_total": reqs,
            "upstream_failures": 0,
            "compiler_calls": compiler_calls,
            "compiler_cache_entries": cache_entries,
            "tool_interactions": 2,
            "stdout_bytes": 120,
            "stderr_bytes": 300,
            "verdict": "PASS",
            "failure_class": "none",
        }
    arms["DIRECT"] = {
        "attempts": 1,
        "exit_status": 0,
        "duration_seconds": 5,
        "sentinel_present": True,
        "sentinel_size_bytes": 3,
        "adapter_requests_ok": 0,
        "adapter_requests_500": 0,
        "adapter_requests_422": 0,
        "adapter_requests_total": 0,
        "upstream_failures": 0,
        "compiler_calls": 0,
        "compiler_cache_entries": 0,
        "tool_interactions": 1,
        "stdout_bytes": 90,
        "stderr_bytes": 280,
        "verdict": "PASS",
        "failure_class": "none",
    }
    return {
        "schema": "slaif-real-codex-rc-qualification-v2",
        "created_at": REHEARSAL_FACTS_CREATED_AT,
        "client": {
            "version": rc_mod.QUALIFIED_CLIENT_VERSION,
            "sha256": rc_mod.QUALIFIED_CLIENT_SHA256,
            "binary_class": "standalone-release",
        },
        "wheel": {
            "sha256": wheel_sha256,
            "expected_sha256": wheel_sha256,
            "binding": "equal",
        },
        "topology": (
            "disposable-codex-home;loopback-adapter;port-18031;"
            "existing-backend;gateway-ingress-disabled"
        ),
        "limits": {
            "output_cap_bytes": 1048576,
            "max_attempts": 2,
            "attempt_timeout_seconds": 600,
            "total_timeout_seconds": 5400,
            "max_adapter_requests": 64,
            "max_compiler_calls": 4,
            "max_tool_interactions": 8,
            "arm_count": 4,
        },
        "arms": arms,
        "protected_state_unchanged": True,
        "protected_state": {
            "files_checked": 13,
            "files_changed": 0,
            "units": {"qwen-serving-vision.service": "active"},
            "ports": {"18020": 1, "18031": 0},
        },
        "disposable_state_removed": True,
        "verdict": "PASS",
    }


def _write_rehearsal_ledger(clone: Path, rc_mod: Any, wheel_sha256: str) -> str:
    """Write the synthetic closed ledger directory (README + facts +
    MANIFEST.sha256 covering exactly the directory). Returns the
    repo-relative facts path."""
    rc_suffix = str(rc_mod.RC_IDENTIFIER).rsplit("-", 1)[1]
    facts_name = f"real-codex-{rc_suffix}-qualification.json"
    ledger = clone / "oap" / "evidence" / "testing-ledger" / REHEARSAL_LEDGER
    ledger.mkdir(parents=True, exist_ok=True)
    (ledger / "README.md").write_text(
        "synthetic rehearsal ledger entry (order 014-c, workstream C); "
        "not real qualification evidence\n",
        encoding="utf-8",
    )
    facts = _synthetic_facts(rc_mod, wheel_sha256)
    (ledger / facts_name).write_text(
        json.dumps(facts, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    entries = {
        f"oap/evidence/testing-ledger/{REHEARSAL_LEDGER}/README.md": _sha256_file(
            ledger / "README.md"
        ),
        f"oap/evidence/testing-ledger/{REHEARSAL_LEDGER}/{facts_name}": _sha256_file(
            ledger / facts_name
        ),
    }
    (ledger / "MANIFEST.sha256").write_text(
        "\n".join(f"{digest}  {rel}" for rel, digest in sorted(entries.items())) + "\n",
        encoding="utf-8",
    )
    return f"oap/evidence/testing-ledger/{REHEARSAL_LEDGER}/{facts_name}"


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=1800)
    return proc


def _build_candidate_artifacts(clone: Path, source: str, workdir: Path) -> str:
    """Clean build of the candidate source in a disposable tree (uv build;
    build-environment cache; no registry). Returns the built wheel sha256."""
    build_tree = workdir / "build"
    build_tree.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "-C", str(clone), "archive", "--output", str(build_tree / "a.tar"), source],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["tar", "-x", "-f", str(build_tree / "a.tar"), "-C", str(build_tree)],
        check=True,
        capture_output=True,
    )
    dist = workdir / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    uv = shutil.which("uv")
    if uv is None:
        raise RehearsalError("uv is required for the rehearsal candidate build")
    proc = _run([uv, "build", "--out-dir", str(dist)], build_tree)
    if proc.returncode != 0:
        raise RehearsalError("rehearsal candidate build failed: " + proc.stderr.decode()[:4000])
    wheels = sorted(dist.glob("slaif_local_coding-*-py3-none-any.whl"))
    if len(wheels) != 1:
        raise RehearsalError("rehearsal build produced != 1 wheel")
    return _sha256_file(wheels[0])


def _regenerate_manifest(clone: Path, generator: Any, dist: Path, source: str) -> None:
    """Regenerate the disposable tree's provenance manifest exactly as the
    committed flow does (same CLI semantics, same payload format)."""
    manifest = generator.build_manifest(
        clone,
        dist,
        source_commit=source,
        tree=clone,
        observed_build_pythons=[platform.python_version()],
    )
    out = clone / "packaging" / "release_provenance_manifest.json"
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rehearsal_pre_publication(clone: Path, source: str, workdir: Path) -> str:
    """PRE mode: generate the record-present state at the candidate source
    in the disposable tree, using the CLONE's own scripts (the candidate's
    code, not the outer checkout's). Returns the synthesized facts path."""
    rc_mod = _load_module(clone / "scripts" / "rc_artifact_record.py", "rc_mod_rehearsal")
    generator = _load_module(clone / "scripts" / "release_provenance_manifest.py", "gen_rehearsal")
    committed_manifest = json.loads(
        (clone / "packaging" / "release_provenance_manifest.json").read_text()
    )
    dist = workdir / "dist"
    # 1) candidate artifacts: clean build of the candidate source; the
    #    candidate wheel must equal the wheel the committed provenance
    #    records (order 014-c, WS-C.1: evidence bound to the candidate
    #    source/wheel).
    built_wheel = _build_candidate_artifacts(clone, source, workdir)
    committed_wheel = str(committed_manifest["artifacts"]["wheel"]["sha256"])
    if built_wheel != committed_wheel:
        raise RehearsalError(
            "rehearsal candidate wheel does not equal the committed manifest "
            f"wheel ({built_wheel[:12]}... != {committed_wheel[:12]}...)"
        )
    # 2) sanitized passing qualification evidence (synthetic ledger 900),
    #    bound to the candidate wheel and the retained qualified client.
    facts_rel = _write_rehearsal_ledger(clone, rc_mod, built_wheel)
    # 3) pre-freeze provenance state for the candidate source (the record
    #    is not present yet).
    _regenerate_manifest(clone, generator, dist, source)
    # 4) the corrected source-ref-bound builder (order 014-c, WS-B): the
    #    synthetic digest/run/time facts are well-formed by construction;
    #    the builder must accept them only because the source-ref binding
    #    holds in the disposable tree.
    proc = _run(
        [
            sys.executable,
            "scripts/rc_artifact_record.py",
            "--source",
            source,
            "--digest",
            REHEARSAL_DIGEST,
            "--head-sha",
            source,
            "--published-at",
            REHEARSAL_PUBLISHED_AT,
            "--run-id",
            str(REHEARSAL_RUN_ID),
            "--qualification-facts",
            facts_rel,
        ],
        clone,
    )
    if proc.returncode != 0:
        raise RehearsalError(
            "rehearsal record builder failed: "
            + (proc.stderr.decode() or proc.stdout.decode())[:4000]
        )
    # 5) rc-published provenance state: regenerate with the record present.
    _regenerate_manifest(clone, generator, dist, source)
    return facts_rel


def _run_gate_suite(clone: Path) -> None:
    """Run the focused record-present gate set inside the disposable
    clone (the clone's own tests, bound to the clone root)."""
    pytest = _run([sys.executable, "-m", "pytest", "-q", *REHEARSAL_TEST_FILES], clone)
    if pytest.returncode != 0:
        tail = (pytest.stdout.decode() or "")[-2000:]
        err = (pytest.stderr.decode() or "")[-2000:]
        raise RehearsalError(
            f"rehearsal gate suite failed:\n--- stdout ---\n{tail}\n--- stderr ---\n{err}"
        )


def _assert_record_evidence_binding(clone: Path) -> None:
    """Prove the record's evidence binding (fail closed, both modes):

    1. the strict loader accepts the record;
    2. the ledger the record NAMES (``compatibility.evidence_path`` with
       the record's own RC identifier facts naming) must exist, be closed
       and manifest-verified, and RE-DERIVE exactly the record's
       compatibility block — a stale prior-RC ledger that lacks the
       claimed RC's facts fails here (order 014-c, WS-C.5);
    3. the frozen ``rc_handoff.md`` must be the deterministic render of
       the committed record — any in-place record tamper (including a
       stale prior-RC evidence path whose sibling ledgers carry identical
       derived blocks) breaks the record<->handoff binding.
    """
    generator = _load_module(clone / "scripts" / "release_provenance_manifest.py", "gen_evidence")
    rc_mod = _load_module(clone / "scripts" / "rc_artifact_record.py", "rc_mod_evidence")
    record = generator.load_rc_record(clone)
    if record is None:
        raise RehearsalError("no RC record to bind (rehearsal invariant)")
    rc_suffix = str(record["rc_identifier"]).rsplit("-", 1)[1]
    evidence_path = str(record["compatibility"]["evidence_path"])
    facts_rel = f"{evidence_path}/real-codex-{rc_suffix}-qualification.json"
    derived = rc_mod.derive_compatibility(clone, facts_rel)
    if derived != record["compatibility"]:
        raise RehearsalError(
            "record compatibility is not re-derivable from the ledger the "
            "record names (stale or inconsistent evidence path)"
        )
    handoff = (clone / "packaging" / "rc_handoff.md").read_text(encoding="utf-8")
    if rc_mod.render_handoff(record) != handoff:
        raise RehearsalError(
            "rc_handoff.md is not the deterministic render of the committed "
            "rc_record.json (record tampered after handoff freeze)"
        )


def _assert_candidate_branch(clone: Path, source: str) -> None:
    """Prove the candidate label/tag/version branch from the tree's OWN
    generator constants (single source of truth — a stale prior-RC const
    anywhere in the record-present state fails here, the exact RC4
    escape)."""
    generator = _load_module(clone / "scripts" / "release_provenance_manifest.py", "gen_branch")
    schema = json.loads(
        (clone / "packaging" / "release_provenance_manifest.schema.json").read_text()
    )
    manifest = json.loads((clone / "packaging" / "release_provenance_manifest.json").read_text())
    rc_id = str(generator.RC_IDENTIFIER)
    # schema consts must equal the generator's own candidate identity
    if schema["properties"]["oci"]["properties"]["candidate_tag"]["const"] != rc_id:
        raise RehearsalError(
            "schema oci.candidate_tag const is not the generator's RC "
            f"identifier (stale prior-RC residue): {rc_id}"
        )
    if schema["properties"]["candidate"]["properties"]["rc_identifier"]["const"] != rc_id:
        raise RehearsalError(
            "schema candidate.rc_identifier const is not the generator's RC "
            f"identifier (stale prior-RC residue): {rc_id}"
        )
    if manifest["candidate"]["rc_identifier"] != rc_id:
        raise RehearsalError("manifest candidate.rc_identifier drift")
    if manifest["candidate"]["state"] != "rc_published":
        raise RehearsalError("manifest candidate.state is not rc_published")
    if manifest["oci"]["candidate_tag"] != rc_id:
        raise RehearsalError("manifest oci.candidate_tag drift")
    if (
        manifest["oci"]["labels"]["slaif-local-coding.qualification"]
        != generator.RC_QUALIFICATION_LABEL
    ):
        raise RehearsalError("manifest qualification label is not the RC label")
    if manifest["status"]["rc_published"] is not True:
        raise RehearsalError("manifest status.rc_published is not true")
    if manifest["oci"]["published"] is not True:
        raise RehearsalError("manifest oci.published is not true")
    record = json.loads((clone / "packaging" / "rc_record.json").read_text())
    if record["rc_identifier"] != rc_id:
        raise RehearsalError("record rc_identifier is not the candidate identity")
    if record["image_source_commit"] != source:
        raise RehearsalError("record image_source_commit is not the candidate source")
    if record["workflow_head_sha"] != source:
        raise RehearsalError("record workflow_head_sha is not the candidate source")
    if record["oci_tags"] != [rc_id, f"sha-{source}"]:
        raise RehearsalError("record oci_tags are not [RC, sha-<source>]")
    if record["oci_image_digest"] != manifest["oci"]["image_digest"]:
        raise RehearsalError("record digest is not the manifest digest")
    source_ref_map = map_from_git_commit(clone, source)
    if record["source_input_hashes"] != source_ref_map:
        raise RehearsalError("record source_input_hashes is not the source-ref map")
    if manifest["source_inputs"] != source_ref_map:
        raise RehearsalError("manifest source_inputs is not the source-ref map")


def _expect_rejection(mutate: Any, label: str) -> None:
    try:
        mutate()
    except (RehearsalError, RuntimeError, SystemExit):
        return
    raise RehearsalError(f"tamper case accepted (must fail closed): {label}")


def _run_tamper_cases(clone: Path, source: str) -> None:
    """Order 014-c, workstream C.5 tamper classes, each fail-closed. The
    clone is left in the rehearsed (untampered) state afterwards."""
    generator = _load_module(clone / "scripts" / "release_provenance_manifest.py", "gen_tamper")
    rc_id = str(generator.RC_IDENTIFIER)
    record_path = clone / "packaging" / "rc_record.json"
    manifest_path = clone / "packaging" / "release_provenance_manifest.json"
    original_record = record_path.read_text(encoding="utf-8")
    original_manifest = manifest_path.read_text(encoding="utf-8")
    try:
        # 1) stale prior-RC identifier/tag in the record.
        def stale_prior_rc_tag() -> None:
            record = json.loads(original_record)
            prior = "0.1.0-rc4" if rc_id != "0.1.0-rc4" else "0.1.0-rc3"
            record["rc_identifier"] = prior
            record_path.write_text(json.dumps(record), encoding="utf-8")
            generator.load_rc_record(clone)

        _expect_rejection(stale_prior_rc_tag, "stale prior-RC identifier")

        # 2) stale prior-RC evidence path: the record names a different,
        #    real prior qualification ledger.
        current_ledger = str(json.loads(original_record)["compatibility"]["evidence_path"]).rsplit(
            "/", 1
        )[1]
        stale_ledger = next(n for n in REAL_LEDGER_NUMBERS if n != current_ledger)

        def stale_prior_rc_evidence_path() -> None:
            record = json.loads(original_record)
            record["compatibility"]["evidence_path"] = f"oap/evidence/testing-ledger/{stale_ledger}"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            generator.load_rc_record(clone)  # closed pattern: still passes
            _assert_record_evidence_binding(clone)  # the real gate

        _expect_rejection(stale_prior_rc_evidence_path, "stale prior-RC evidence path")

        # 3) source mismatch: record names a different image source.
        def source_mismatch() -> None:
            record = json.loads(original_record)
            other = "f" * 40
            record["image_source_commit"] = other
            record["oci_tags"] = [rc_id, f"sha-{other}"]
            record_path.write_text(json.dumps(record), encoding="utf-8")
            generator.load_rc_record(clone)

        _expect_rejection(source_mismatch, "source mismatch")

        # 4) changed mapped test input in the worktree (the real-repo
        #    source-input binding gate must fail).
        target = clone / "tests" / "test_rc_record.py"

        def changed_mapped_test_input() -> None:
            target.write_text(
                target.read_text(encoding="utf-8") + "# rehearsed drift\n",
                encoding="utf-8",
            )
            proc = _run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "tests/test_source_input_binding.py::test_real_repo_source_inputs_bound_to_committed_source",
                ],
                clone,
            )
            if proc.returncode == 0:
                return  # gate passed: drift undetected (expect_rejection raises)
            raise SystemExit("mapped input drift correctly rejected by the gate")

        _expect_rejection(changed_mapped_test_input, "changed mapped test input")
        _git(clone, "checkout", "--quiet", "--", "tests/test_rc_record.py")

        # 5) wrong workflow head.
        def wrong_workflow_head() -> None:
            record = json.loads(original_record)
            record["workflow_head_sha"] = "e" * 40
            record_path.write_text(json.dumps(record), encoding="utf-8")
            generator.load_rc_record(clone)

        _expect_rejection(wrong_workflow_head, "wrong workflow head")

        # 6) wrong source alias tag.
        def wrong_source_alias() -> None:
            record = json.loads(original_record)
            record["oci_tags"] = [rc_id, "sha-" + "0" * 40]
            record_path.write_text(json.dumps(record), encoding="utf-8")
            generator.load_rc_record(clone)

        _expect_rejection(wrong_source_alias, "wrong source alias")

        # 7) later-tree map: the committed manifest records the input map
        #    of a LATER tree (the RC4 rebind) instead of the map at the
        #    recorded source ref; generated_from still names the source
        #    ref, so only the map-vs-source-ref gate can catch it.
        def later_tree_map() -> None:
            # isolate the variable: drop any record tamper from case 2.
            record_path.write_text(original_record, encoding="utf-8")
            target.write_text(
                target.read_text(encoding="utf-8") + "# later tree\n",
                encoding="utf-8",
            )
            manifest = json.loads(original_manifest)
            manifest["source_inputs"] = dict(map_from_directory(clone))
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            proc = _run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "tests/test_source_input_binding.py::test_real_repo_source_inputs_bound_to_committed_source",
                ],
                clone,
            )
            if proc.returncode == 0:
                return  # gate passed: later-tree map undetected (raises below)
            raise SystemExit("later-tree map correctly rejected by the gate")

        _expect_rejection(later_tree_map, "later-tree map")
    finally:
        # leave the clone in the rehearsed state (tamper cases are atomic)
        try:
            _git(clone, "checkout", "--quiet", "--", "tests")
        except Exception:  # noqa: BLE001 - best-effort cleanup
            pass
        record_path.write_text(original_record, encoding="utf-8")
        manifest_path.write_text(original_manifest, encoding="utf-8")


def run_rehearsal(
    repo: Path, source: str | None = None, workdir: Path | None = None
) -> dict[str, str]:
    """Run the full rehearsal; returns a sanitized summary."""
    if source is None:
        source = _git(repo, "rev-parse", "HEAD")
    if not re.fullmatch(r"[0-9a-f]{40}", source):
        raise RehearsalError("source must be 40-hex")
    if (
        subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", source], capture_output=True
        ).returncode
        != 0
    ):
        raise RehearsalError("source does not exist in the repository")
    keep = workdir is not None
    workdir = workdir or Path(tempfile.mkdtemp(prefix="slaif-rehearsal-"))
    workdir.mkdir(parents=True, exist_ok=True)
    try:
        clone = _clone_source(repo, source, workdir)
        record_present = (clone / "packaging" / "rc_record.json").is_file()
        if record_present:
            mode = "post-publication (real record at source)"
        else:
            mode = "pre-publication (synthetic record synthesized)"
            _rehearsal_pre_publication(clone, source, workdir)
        _assert_candidate_branch(clone, source)
        _assert_record_evidence_binding(clone)
        _run_gate_suite(clone)
        _assert_candidate_branch(clone, source)
        _assert_record_evidence_binding(clone)
        _run_tamper_cases(clone, source)
        return {
            "source": source,
            "mode": mode,
            "digest": REHEARSAL_DIGEST if not record_present else "real-record",
            "status": "PASSED",
        }
    finally:
        if not keep:
            shutil.rmtree(workdir, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=None, help="40-hex candidate source (default: HEAD)")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--workdir", type=Path, default=None, help="keep and reuse this workdir")
    parser.add_argument("--keep", action="store_true", help="keep the disposable workdir")
    args = parser.parse_args(argv)
    try:
        summary = run_rehearsal(args.repo, args.source, args.workdir)
    except RehearsalError as exc:
        print(f"record-present rehearsal FAILED: {exc}", file=sys.stderr)
        return 1
    print(
        "record-present rehearsal PASSED: source="
        f"{summary['source']} mode={summary['mode']} digest={summary['digest']}"
    )
    if args.keep and args.workdir is None:
        print("(workdir regenerated; pass --workdir to keep a specific one)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
