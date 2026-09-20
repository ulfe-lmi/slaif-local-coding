"""Release/RC provenance manifest generator (order 009-a, workstream E;
order 013-a, workstream A: state-aware schema v3; order 013-i: schema v4
pre-freeze candidate state + recorded build toolchain; order 013-j: schema
v5 — hermetic build-environment binding, exact Python identity scope, and
the mechanically verified source-input map).

Produces a content-free, machine-readable, schema-versioned provenance
manifest. "Content-free" means the manifest carries only hashes, versions,
counts, and fixed status facts — never host paths, credentials, provider
keys, private identifiers, prompts, model output, or raw acceptance payloads
(enforced by the forbidden-content scan shared with the artifact policy
check and by tests/test_release_provenance_manifest.py).

The manifest is generated from actual build inputs (git HEAD, the locked
files, the built artifacts, the deployment templates, and the current
Gateway peer fixture) and is committed under packaging/. The E3 test
regenerates it and fails on any drift or forbidden content.

State model (order 013-i, C11): THREE explicit states, separate from the
final release — a published RC must never imply final_public_release=true:

- pre-freeze candidate: no publication record; null digest,
  `published: false`, `rc_published: false`, `final_public_release: false`,
  `candidate.state: pre_freeze`, reserved RC tag convention.
- RC-published: `packaging/rc_record.json` present (schema
  slaif-rc-record-v2, strictly validated); the recorded RC digest,
  `rc_published: true`, `candidate.state: rc_published`, the RC candidate
  qualification label, RC tag convention; `final_public_release` REMAINS
  false.
- final-published: `packaging/release_record.json` present (schema
  slaif-release-record-v1); digest `D`, `published: true`,
  `final_public_release: true`, the published qualification label, plus a
  closed top-level `release` section bound to the record.

Self-reference exclusion: the manifest (and its schema) and the
post-publication RC record / rendered handoff are excluded from every
wheel/sdist/image build input (pyproject top-level exclusions).

Order 013-j, J3/J4: `generated_from.git_commit` is the EXACT source commit
A the artifacts were cleanly built from (the truthful A/B sequence: source
inputs committed as A, clean build of A, manifest generated from A, only
the derived metadata committed as B). The `source_inputs` section is the
mechanical path->sha256 map of every wheel/sdist/OCI/configuration input at
A (derived from the pyproject build policy and the Dockerfile); the E3 gate
rebuilds A from `git archive` and regenerates the manifest, so any input
drift — even at a valid ancestor — fails. The recorded build environment
must equal the `[build-system].requires` pins (fully pinned; enforcement is
mechanical on every generation). The recorded Python identity is the exact
interpreter scope the artifacts were observed on (patch-independence only
when observed on two or more distinct patch versions), never a bare
"3.12" presented as an exact runtime version.

Usage:

    python scripts/release_provenance_manifest.py \
        --emit packaging/release_provenance_manifest.json \
        --source-commit <40-hex A> \
        --observed-build-python 3.12.14 [--observed-build-python 3.12.3]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from source_input_map import map_from_directory, map_from_git_commit  # noqa: E402

SCHEMA_NAME = "slaif-release-provenance-v5"
SCHEMA_VERSION = 5
OBJECTIVE = "013-l"
RELEASE_RECORD_PATH = Path("packaging/release_record.json")
RC_RECORD_PATH = Path("packaging/rc_record.json")
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
RC_RECORD_SCHEMA = "slaif-rc-record-v2"
IMAGE_PLATFORM = "linux/amd64"
REPOSITORY = "ulfe-lmi/slaif-local-coding"
GATEWAY_PEER_FIXTURE = Path("tests/fixtures/gateway/current_peer_authority.json")
PACKAGE_NAME = "slaif-local-coding"
CODIX_CLIENT_VERSION = "0.149.0"
CODIX_WIRE_FIXTURE_DIR = "tests/fixtures/codex/0.149.0"

# Order 013-i, C9 + order 013-j, J3: deterministic build toolchain identity.
# EVERY build dependency is pinned in pyproject [build-system].requires
# (hermetic build environment); the recorded set is asserted to equal those
# pins on every generation (mechanical binding; drift fails generation).
# The recorded set was observed as the resolved build environment on
# isolated clean builds (uv 0.12.5).
BUILD_BACKEND_NAME = "hatchling"
BUILD_BACKEND_VERSION = "1.32.0"
BUILD_ENVIRONMENT = {
    "hatchling": "1.32.0",
    "packaging": "26.3",
    "pathspec": "1.1.1",
    "pluggy": "1.6.0",
    "tomlkit": "0.15.1",
    "trove-classifiers": "2026.6.1.19",
}
UV_VERSION = "0.12.5"
PYTHON_RUNTIME_REQUIREMENT = ">=3.12"

# Order 013-i, C12/D13: explicit RC candidate identity.
RC_IDENTIFIER = "0.1.0-rc1"
RC_QUALIFICATION_LABEL = "rc-candidate-0.1.0-rc1; private; not final release"
RC_DEPLOYMENT_ASSUMPTIONS = (
    "linux-docker-engine-compose-v2;host-network-mode;"
    "private-same-host-upstream;separate-gateway;loopback-default-bind"
)

# The two bullets replaced (and only those two) in the published states by
# _published_limitations(); every other bullet is preserved verbatim.
LIMITATION_NOT_RELEASED = (
    "not released: RC candidate state (pre-freeze) — no final public "
    "release; the historical private 0.1.0 tag is legacy unpublished-to-"
    "users output and is NOT the RC benchmark target"
)
LIMITATION_OCI_UNPUBLISHED = (
    "OCI RC image not published yet (oci.image_digest null, oci.published "
    "false, status.rc_published false); the RC container publication path "
    "is documented (workflow_dispatch-only, inert this round) and will be "
    "executed from the exact reviewed source commit in a separate later "
    "round"
)
LIMITATIONS: list[str] = [
    "two supported deployment paths: Docker (canonical installation path) "
    "and systemd user service on the local host (secondary direct-host "
    "path, including the protected-host cutover path)",
    "Docker qualified in CI and disposable environments only; "
    "deployment-qualified (disposable/CI environments only), not "
    "release-qualified",
    "LAN-visible binding law in force (D1): a non-loopback adapter bind is "
    "legal only under the full signed ingress contract "
    "(service_bearer_signed_identity_v1); loopback remains the default",
    "cutover not performed",
    LIMITATION_NOT_RELEASED,
    LIMITATION_OCI_UNPUBLISHED,
    "sdist is a developer-only source archive, not a supported release artifact",
    "no multi-user, production-certification, compliance, or frontier-equivalence claim",
    "single RTX 3090 fixture evidence is fixture-scoped, not generic production equivalence",
    "artifacts regenerated by objective 013-k (superseding objective "
    "013-j's regeneration) on explicitly authorized inputs only (RC "
    "source-review corrections plus the 013-k K1-K3 corrections: release-"
    "workflow build selection, transient README paragraph removal, publisher "
    "unknown-status guard; README cleanup remains embedded in wheel "
    "METADATA; fully pinned hermetic build environment enforced by "
    "[build-system].requires; deterministic hatchling==1.32.0 backend proven "
    "to reproduce the historical wheel from the clean historical source); "
    "the historical wheel "
    "879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19 "
    "and the historical private 0.1.0 registry digest are NOT reused for "
    "the RC; objective-010-a wheel hash "
    "8678e16b41bd9d73849a956c9d1f25235532eaf52c772fc695718b2063b54472 "
    "remains the accepted 010 record only, not any current authority",
]

TAG_CONVENTION = (
    "0.1.0-<short-sha> (and full-sha form) locally; reserved RC publication "
    "reference ghcr.io/ulfe-lmi/slaif-local-coding with tags 0.1.0-rc1 + "
    "sha-<full-sha> (private registry; the immutable digest is the "
    "authoritative identity, tags are aliases) after the RC publication "
    "round; the historical private 0.1.0 tag is legacy unpublished-to-users "
    "output and is never a default"
)
TOPOLOGY_MODE_LABEL = (
    "linux-docker-host-network;loopback-default;lan-visible-only-with-full-signed-ingress"
)
QUALIFICATION_LABEL = "disposable-qualification-only; not released"
PUBLISHED_QUALIFICATION_LABEL = "mvp-release-0.1.0"
IMAGE_REFERENCE = "ghcr.io/ulfe-lmi/slaif-local-coding"
PUBLISHED_VERSION = "0.1.0"
PUBLISHED_GIT_TAG = "v0.1.0"
PUBLICATION_WORKFLOW = "release-image.yml"
PUBLISHED_AT_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


def load_release_record(repo: Path) -> dict | None:
    """Load and strictly validate the final-release record, if present.

    Closed key set (slaif-release-record-v1): schema, version, git_tag,
    image_source_commit, oci_image_reference, oci_image_digest, oci_tags,
    published_at, publication_workflow, publication_workflow_run_id. No host
    paths, no URLs beyond the fixed repository/registry references, no
    secret-like content. Any deviation is a generation failure, never a
    warning.
    """
    path = repo / RELEASE_RECORD_PATH
    if not path.is_file():
        return None
    record = json.loads(path.read_text(encoding="utf-8"))
    if set(record) != RELEASE_RECORD_KEYS:
        raise RuntimeError(f"release record key set drift: {sorted(record)}")
    if record["schema"] != "slaif-release-record-v1":
        raise RuntimeError("release record schema drift")
    if record["version"] != PUBLISHED_VERSION:
        raise RuntimeError("release record version drift")
    if record["git_tag"] != PUBLISHED_GIT_TAG:
        raise RuntimeError("release record git_tag drift")
    if not re.fullmatch(r"[0-9a-f]{40}", str(record["image_source_commit"])):
        raise RuntimeError("release record image_source_commit is not 40-hex")
    if record["oci_image_reference"] != IMAGE_REFERENCE:
        raise RuntimeError("release record oci_image_reference drift")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(record["oci_image_digest"])):
        raise RuntimeError("release record oci_image_digest is not sha256:<64-hex>")
    source = str(record["image_source_commit"])
    if record["oci_tags"] != [PUBLISHED_VERSION, f"sha-{source}"]:
        raise RuntimeError("release record oci_tags must be [0.1.0, sha-<source>]")
    if not PUBLISHED_AT_PATTERN.fullmatch(str(record["published_at"])):
        raise RuntimeError("release record published_at is not RFC 3339 UTC")
    if record["publication_workflow"] != PUBLICATION_WORKFLOW:
        raise RuntimeError("release record publication_workflow drift")
    run_id = record["publication_workflow_run_id"]
    if run_id is not None and not (
        isinstance(run_id, int) and not isinstance(run_id, bool) and run_id > 0
    ):
        raise RuntimeError("release record publication_workflow_run_id invalid")
    return record


def load_rc_record(repo: Path) -> dict | None:
    """Load and strictly validate the RC artifact record, if present.

    Closed key set (slaif-rc-record-v2, order 013-j, J5). The RC record is
    self-contained post-publication metadata: it is excluded from every
    artifact input, keeps final_public_release/cutover_performed false by
    construction, and carries the exact path->hash source-input map
    DIRECTLY (config templates, compose files, packaging inputs — not
    cross-bound by unrelated wheel/lock/peer facts), the full pinned build
    environment, the digest-pinned base images, the supported image
    platform, and the publishing workflow run's head SHA. Any deviation is
    a generation failure, never a warning.
    """
    path = repo / RC_RECORD_PATH
    if not path.is_file():
        return None
    record = json.loads(path.read_text(encoding="utf-8"))
    if set(record) != RC_RECORD_KEYS:
        raise RuntimeError(f"rc record key set drift: {sorted(record)}")
    if record["schema"] != RC_RECORD_SCHEMA:
        raise RuntimeError("rc record schema drift")
    if record["rc_identifier"] != RC_IDENTIFIER:
        raise RuntimeError("rc record rc_identifier drift")
    if record["product_version"] != PUBLISHED_VERSION:
        raise RuntimeError("rc record product_version drift")
    if not re.fullmatch(r"[0-9a-f]{40}", str(record["image_source_commit"])):
        raise RuntimeError("rc record image_source_commit is not 40-hex")
    if record["oci_image_reference"] != IMAGE_REFERENCE:
        raise RuntimeError("rc record oci_image_reference drift")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(record["oci_image_digest"])):
        raise RuntimeError("rc record oci_image_digest is not sha256:<64-hex>")
    source = str(record["image_source_commit"])
    if record["oci_tags"] != [RC_IDENTIFIER, f"sha-{source}"]:
        raise RuntimeError(f"rc record oci_tags must be [{RC_IDENTIFIER}, sha-{source}]")
    if not PUBLISHED_AT_PATTERN.fullmatch(str(record["published_at"])):
        raise RuntimeError("rc record published_at is not RFC 3339 UTC")
    if record["publication_workflow"] != PUBLICATION_WORKFLOW:
        raise RuntimeError("rc record publication_workflow drift")
    run_id = record["publication_workflow_run_id"]
    if run_id is not None and not (
        isinstance(run_id, int) and not isinstance(run_id, bool) and run_id > 0
    ):
        raise RuntimeError("rc record publication_workflow_run_id invalid")
    if not re.fullmatch(r"[0-9a-f]{40}", str(record["workflow_head_sha"])):
        raise RuntimeError("rc record workflow_head_sha is not 40-hex")
    if record["private_registry_auth_required"] is not True:
        raise RuntimeError("rc record private_registry_auth_required must be true")
    if record["final_public_release"] is not False:
        raise RuntimeError("rc record final_public_release must be false")
    if record["cutover_performed"] is not False:
        raise RuntimeError("rc record cutover_performed must be false")
    if not re.fullmatch(r"[0-9a-f]{64}", str(record["wheel_sha256"])):
        raise RuntimeError("rc record wheel_sha256 is not 64-hex")
    if not re.fullmatch(r"[0-9a-f]{64}", str(record["dependency_lock_sha256"])):
        raise RuntimeError("rc record dependency_lock_sha256 is not 64-hex")
    if not re.fullmatch(r"[0-9a-f]{40}", str(record["gateway_authority_sha"])):
        raise RuntimeError("rc record gateway_authority_sha is not 40-hex")
    environment = record["build_environment"]
    if not isinstance(environment, dict) or environment != dict(BUILD_ENVIRONMENT):
        raise RuntimeError("rc record build_environment drift vs enforced pins")
    toolchain = record["build_toolchain"]
    if not isinstance(toolchain, dict) or set(toolchain) != {"backend", "uv", "python"}:
        raise RuntimeError("rc record build_toolchain key set drift")
    if toolchain["backend"] != f"{BUILD_BACKEND_NAME}=={BUILD_BACKEND_VERSION}":
        raise RuntimeError("rc record build_toolchain backend drift")
    if toolchain["uv"] != UV_VERSION or toolchain["python"] != "3.12":
        raise RuntimeError("rc record build_toolchain uv/python drift")
    base_images = record["base_images"]
    expected_bases = {
        stage: {"name": fact["name"], "digest": fact["digest"]}
        for stage, fact in _dockerfile_base_images(repo).items()
    }
    if not isinstance(base_images, dict) or base_images != expected_bases:
        raise RuntimeError("rc record base_images drift vs Dockerfile")
    if record["image_platform"] != IMAGE_PLATFORM:
        raise RuntimeError("rc record image_platform drift")
    inputs = record["source_input_hashes"]
    if not isinstance(inputs, dict) or not inputs:
        raise RuntimeError("rc record source_input_hashes must be a non-empty map")
    for value in inputs.values():
        if not re.fullmatch(r"[0-9a-f]{64}", str(value)):
            raise RuntimeError("rc record source_input_hashes value not sha256")
    if record["deployment_assumptions"] != RC_DEPLOYMENT_ASSUMPTIONS:
        raise RuntimeError("rc record deployment_assumptions drift")
    return record


def _published_limitations(digest: str, source: str, rc: bool) -> list[str]:
    """Published-state limitations: replace EXACTLY the two not-yet-published
    bullets with truthful published-state bullets; all other bullets are
    preserved verbatim in order."""
    if rc:
        published_bullet_1 = (
            f"RC {RC_IDENTIFIER} (product {PUBLISHED_VERSION}) published to "
            f"{IMAGE_REFERENCE} (PRIVATE registry; private-auth required) at "
            f"digest {digest} with tags {RC_IDENTIFIER} and sha-{source}; "
            f"image source commit {source}; the digest is the authoritative "
            "identity and tags are aliases; final_public_release remains "
            "false — a final public release is a separate later decision"
        )
    else:
        published_bullet_1 = (
            f"final {PUBLISHED_VERSION} published to {IMAGE_REFERENCE} at "
            f"digest {digest} with tags {PUBLISHED_VERSION} and sha-{source}; "
            f"image source commit {source}; the git tag {PUBLISHED_GIT_TAG} "
            f"targets {source} as the release reference (created by strategy "
            "post-merge; the GitHub Release follows that tag)"
        )
    published_bullet_2 = (
        "publication is registry-only: no protected-host cutover, no real "
        "deployment yet evidenced; the protected-host cutover remains a "
        "separate human-authorized act"
    )
    out: list[str] = []
    for bullet in LIMITATIONS:
        if bullet == LIMITATION_NOT_RELEASED:
            out.append(published_bullet_1)
        elif bullet == LIMITATION_OCI_UNPUBLISHED:
            out.append(published_bullet_2)
        else:
            out.append(bullet)
    return out


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_facts(path: Path, kind: str) -> dict:
    import tarfile
    import zipfile

    if kind == "wheel":
        with zipfile.ZipFile(path) as wheel:
            entries = [i.filename for i in wheel.infolist() if not i.is_dir()]
    else:
        with tarfile.open(path, "r:gz") as sdist:
            entries = []
            for member in sdist.getmembers():
                if member.isfile():
                    entries.append(member.name)
    return {
        "name": path.name,
        "sha256": _sha256_file(path),
        "size_bytes": path.stat().st_size,
        "entry_count": len(entries),
    }


def _dockerfile_base_images(root: Path) -> dict[str, dict[str, str]]:
    """Return the stage-keyed base-image map parsed from the Dockerfile.

    Stages: ``uv-provider``, ``build``, ``runtime`` — each with
    ``name`` and ``digest`` (``sha256:<64-hex>``). All three FROM lines
    must be digest-pinned (B1); any unpinned base is a generation
    failure, never a warning.
    """
    dockerfile = (root / "Dockerfile").read_text(encoding="utf-8")
    found: dict[str, dict] = {}
    for line in dockerfile.splitlines():
        m = re.match(r"^FROM\s+(\S+?)@sha256:([0-9a-f]{64})\s+AS\s+([A-Za-z0-9_-]+)\s*$", line)
        if m:
            found[m.group(3)] = {
                "name": m.group(1),
                "digest": "sha256:" + m.group(2),
            }
    if set(found) != {"uv-provider", "build", "runtime"}:
        raise RuntimeError(
            "Dockerfile must pin exactly the uv-provider, build, and runtime "
            f"images by digest; found: {sorted(found)}"
        )
    return found


def _git_commit(root: Path) -> str:
    out = (
        subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            check=True,
        )
        .stdout.decode()
        .strip()
    )
    if not re.fullmatch(r"[0-9a-f]{40}", out):
        raise RuntimeError("git rev-parse HEAD did not return a 40-hex SHA")
    return out


def _assert_build_environment_pins(repo: Path) -> None:
    """Order 013-i, C9 + order 013-j, J3: the hermetic build-environment pin
    set must hold.

    Every ``[build-system].requires`` entry must be an exact ``name==version``
    pin (no ranges), and the pinned set must EXACTLY equal the recorded
    ``BUILD_ENVIRONMENT`` — the dependency set observed on the isolated
    clean builds. Any drift changes the recorded toolchain identity and is
    a generation failure, never a warning.
    """
    with (repo / "pyproject.toml").open("rb") as stream:
        pyproject = tomllib.load(stream)
    requires = pyproject["build-system"]["requires"]
    if not isinstance(requires, list) or not requires:
        raise RuntimeError("build-system requires must be a non-empty pin list")
    pinned: dict[str, str] = {}
    for entry in requires:
        match = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9._-]*)==([0-9][0-9a-zA-Z.]*)", str(entry))
        if match is None:
            raise RuntimeError(
                f"build-system requires entry is not an exact name==version pin: {entry!r}"
            )
        name = re.sub(r"[-_.]+", "-", match.group(1)).lower()
        pinned[name] = match.group(2)
    expected = {
        re.sub(r"[-_.]+", "-", name).lower(): version for name, version in BUILD_ENVIRONMENT.items()
    }
    if pinned != expected:
        raise RuntimeError(
            "build-environment pin drift: [build-system].requires "
            f"{dict(sorted(pinned.items()))} != recorded {dict(sorted(expected.items()))}"
        )
    if pyproject["build-system"]["build-backend"] != f"{BUILD_BACKEND_NAME}.build":
        raise RuntimeError("build-backend drift")
    if pinned[BUILD_BACKEND_NAME] != BUILD_BACKEND_VERSION:
        raise RuntimeError(f"build-backend pin drift: expected {BUILD_BACKEND_VERSION}")


def build_manifest(
    repo: Path,
    dist_dir: Path,
    source_commit: str | None = None,
    tree: Path | None = None,
    observed_build_pythons: list[str] | None = None,
) -> dict:
    """Build the manifest from verified facts.

    Order 013-j, J3/J4: ``source_commit`` is the EXACT source commit A the
    artifacts were cleanly built from (defaults to HEAD for legacy calls).
    ``tree`` is the directory whose files provide the policy, templates,
    Dockerfile, and lock facts (defaults to ``repo``); its input files must
    be byte-identical to commit A's input files, so a changed source staged
    under an old HEAD fails generation. ``observed_build_pythons`` are the
    exact CPython interpreter versions on which the recorded artifacts were
    observed built (patch-independence is recorded only when two or more
    distinct patch versions are listed).
    """
    if tree is None:
        tree = repo
    if source_commit is None:
        source_commit = _git_commit(repo)
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise RuntimeError("source_commit must be 40-hex")
    head = _git_commit(repo)
    if source_commit != head:
        proc = subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", source_commit, head],
            capture_output=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                "source_commit is not an ancestor of HEAD; the manifest must "
                "reference the exact committed source tree it was built from"
            )
    if observed_build_pythons is None:
        observed_build_pythons = []
    observed = sorted({v for v in observed_build_pythons})
    for value in observed:
        if not re.fullmatch(r"\d+\.\d+\.\d+", value):
            raise RuntimeError(f"observed build python must be exact X.Y.Z: {value!r}")

    # Order 013-j, J4: mechanical input-map binding to the exact source A.
    recorded_inputs = map_from_git_commit(repo, source_commit)
    tree_inputs = map_from_directory(tree)
    if tree_inputs != recorded_inputs:
        missing = sorted(set(recorded_inputs) - set(tree_inputs))
        extra = sorted(set(tree_inputs) - set(recorded_inputs))
        altered = sorted(
            path
            for path in set(recorded_inputs) & set(tree_inputs)
            if recorded_inputs[path] != tree_inputs[path]
        )
        raise RuntimeError(
            "source input drift: the build tree differs from source commit "
            f"{source_commit[:12]} (missing={missing[:5]} extra={extra[:5]} "
            f"altered={altered[:5]}); never stage changed source under an "
            "old HEAD and present that commit as the built tree"
        )

    with (tree / "pyproject.toml").open("rb") as stream:
        pyproject = tomllib.load(stream)
    package_version = pyproject["project"]["version"]
    _assert_build_environment_pins(tree)

    rc_record = load_rc_record(repo)
    release_record = load_release_record(repo)
    rc_published = rc_record is not None
    final_published = release_record is not None
    if rc_published:
        assert rc_record is not None
        digest = str(rc_record["oci_image_digest"])
        source = str(rc_record["image_source_commit"])
    elif final_published:
        assert release_record is not None
        digest = str(release_record["oci_image_digest"])
        source = str(release_record["image_source_commit"])
    else:
        digest = ""
        source = ""

    peer = json.loads((tree / GATEWAY_PEER_FIXTURE).read_text(encoding="utf-8"))

    wheels = sorted(
        set(dist_dir.glob(f"{PACKAGE_NAME.replace('-', '_')}-*.whl"))
        | set(dist_dir.glob(f"{PACKAGE_NAME}-*.whl"))
    )
    sdists = sorted(
        set(dist_dir.glob(f"{PACKAGE_NAME.replace('-', '_')}-*.tar.gz"))
        | set(dist_dir.glob(f"{PACKAGE_NAME}-*.tar.gz"))
    )
    if len(wheels) != 1 or len(sdists) != 1:
        raise RuntimeError("expected exactly one wheel and one sdist in dist dir")

    python_version = platform.python_version()
    major_minor = ".".join(python_version.split(".")[:2])

    if rc_published:
        qualification_label = RC_QUALIFICATION_LABEL
    elif final_published:
        qualification_label = PUBLISHED_QUALIFICATION_LABEL
    else:
        qualification_label = QUALIFICATION_LABEL

    manifest = {
        "schema": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "objective": OBJECTIVE,
        "generated_from": {
            "repository": REPOSITORY,
            "git_commit": source_commit,
        },
        "gateway_peer": {
            "repository": peer["repository"],
            "commit": peer["commit"],
            "server_module": {
                "module_id": peer["server"]["module_id"],
                "module_version": peer["server"]["module_version"],
                "replay_mode": peer["server"]["replay_mode"],
            },
            "client_module": {
                "module_id": peer["client"]["module_id"],
                "module_version": peer["client"]["module_version"],
            },
        },
        "runtime": {
            "python": major_minor,
            "package_name": PACKAGE_NAME,
            "package_version": package_version,
            "uv_lock_sha256": _sha256_file(tree / "uv.lock"),
            "pyproject_sha256": _sha256_file(tree / "pyproject.toml"),
        },
        "artifacts": {
            "wheel": _artifact_facts(wheels[0], "wheel"),
            "sdist": _artifact_facts(sdists[0], "sdist"),
        },
        "build": {
            "backend": {
                "name": BUILD_BACKEND_NAME,
                "version": BUILD_BACKEND_VERSION,
            },
            "build_environment": dict(BUILD_ENVIRONMENT),
            "uv_version": UV_VERSION,
            "python": {
                "runtime_requirement": PYTHON_RUNTIME_REQUIREMENT,
                "observed_exact": observed,
                "wheel_patch_independent": len(observed) >= 2,
            },
        },
        "source_inputs": recorded_inputs,
        "candidate": {
            "rc_identifier": RC_IDENTIFIER,
            "state": "rc_published" if rc_published else "pre_freeze",
            "private_registry_auth_required": True,
            "final_public_release": False,
            "cutover_performed": False,
        },
        "templates": {
            "config_example_sha256": _sha256_file(tree / "config/adapter.example.toml"),
            "deployment_config_template_sha256": _sha256_file(
                tree / "config/adapter.deployment.template.toml"
            ),
            "gateway_integrated_config_template_sha256": _sha256_file(
                tree / "config/adapter.gateway-integrated.template.toml"
            ),
            "service_unit_sha256": _sha256_file(tree / "packaging/slaif-local-coding.service"),
            "service_unit_example_sha256": _sha256_file(
                tree / "packaging/slaif-local-coding.service.example"
            ),
            "readyz_wait_sha256": _sha256_file(tree / "packaging/readyz-wait.sh"),
        },
        "reference_compatibility": {
            "model_name": "qwen3.8-27b",
            "upstream_interface": "vllm-openai-compat-v1",
            "codex_client": {
                "version": CODIX_CLIENT_VERSION,
                "wire_fixture_dir": CODIX_WIRE_FIXTURE_DIR,
            },
        },
        "status": {
            "deployment_qualified": "disposable-environment-only",
            "cutover_performed": False,
            "rc_published": rc_published,
            "final_public_release": final_published,
        },
        "limitations": (
            _published_limitations(digest, source, rc=rc_published)
            if (rc_published or final_published)
            else list(LIMITATIONS)
        ),
    }
    if final_published:
        assert release_record is not None
        manifest["release"] = {
            "version": str(release_record["version"]),
            "git_tag": str(release_record["git_tag"]),
            "git_tag_target": source,
            "image_source_commit": source,
            "oci_image_digest": digest,
            "oci_tags": list(release_record["oci_tags"]),
            "published_at": str(release_record["published_at"]),
            "publication_workflow_run_id": release_record["publication_workflow_run_id"],
        }

    base_images_by_stage = _dockerfile_base_images(tree)
    build_tool_image = base_images_by_stage["uv-provider"]
    build_base_image = base_images_by_stage["build"]
    base_image = base_images_by_stage["runtime"]
    if rc_published:
        tag_convention = (
            f"published RC reference {IMAGE_REFERENCE} tags {RC_IDENTIFIER} + "
            f"sha-<full image-source SHA> (private registry; digest {digest} "
            "recorded in packaging/rc_record.json and this manifest; the "
            "digest is the authoritative identity, tags are aliases); local "
            "qualification tags slaif-local-coding:0.1.0-<sha> via "
            "compose.build.yaml"
        )
    elif final_published:
        tag_convention = (
            f"published reference {IMAGE_REFERENCE} tags {PUBLISHED_VERSION} + "
            f"sha-<full image-source SHA> (digest {digest} recorded in this "
            "manifest); local qualification tags slaif-local-coding:0.1.0-<sha> "
            "via compose.build.yaml"
        )
    else:
        tag_convention = TAG_CONVENTION
    manifest["oci"] = {
        "image_reference": IMAGE_REFERENCE,
        "tag_convention": tag_convention,
        "candidate_tag": RC_IDENTIFIER,
        "base_image": base_image,
        "build_base_image": build_base_image,
        "build_tool_image": build_tool_image,
        "dockerfile_sha256": _sha256_file(tree / "Dockerfile"),
        "compose_sha256": _sha256_file(tree / "compose.yaml"),
        "dockerignore_sha256": _sha256_file(tree / ".dockerignore"),
        "wheel_sha256": manifest["artifacts"]["wheel"]["sha256"],
        "image_digest": digest if (rc_published or final_published) else None,
        "published": rc_published or final_published,
        "labels": {
            "org.opencontainers.image.source": ("https://github.com/ulfe-lmi/slaif-local-coding"),
            "org.opencontainers.image.version": package_version,
            "slaif-local-coding.package.version": package_version,
            "slaif-local-coding.gateway.peer.sha": manifest["gateway_peer"]["commit"],
            "slaif-local-coding.topology.mode": TOPOLOGY_MODE_LABEL,
            "slaif-local-coding.qualification": qualification_label,
            "slaif-local-coding.wheel.sha256": manifest["artifacts"]["wheel"]["sha256"],
        },
    }
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit",
        type=Path,
        default=Path("packaging/release_provenance_manifest.json"),
    )
    parser.add_argument("--dist", type=Path, default=Path("dist"))
    parser.add_argument(
        "--source-commit",
        required=True,
        help="exact 40-hex source commit A the artifacts were cleanly built from",
    )
    parser.add_argument(
        "--tree",
        type=Path,
        default=None,
        help="directory holding the source files (default: the repository checkout)",
    )
    parser.add_argument(
        "--observed-build-python",
        action="append",
        default=[],
        help="exact CPython X.Y.Z on which the recorded artifacts were observed "
        "built (repeatable; >=2 distinct patch versions => wheel_patch_independent)",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    manifest = build_manifest(
        repo,
        args.dist.resolve(),
        source_commit=args.source_commit,
        tree=(args.tree.resolve() if args.tree else repo),
        observed_build_pythons=args.observed_build_python,
    )
    payload = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    args.emit.parent.mkdir(parents=True, exist_ok=True)
    args.emit.write_text(payload, encoding="utf-8")
    print(f"wrote {args.emit} ({len(payload)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
