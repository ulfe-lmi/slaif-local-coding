"""Release/RC provenance manifest generator (order 009-a, workstream E;
order 013-a, workstream A: state-aware schema v3; order 013-i: schema v4
pre-freeze candidate state + recorded build toolchain).

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
  slaif-rc-record-v1, strictly validated); the recorded RC digest,
  `rc_published: true`, `candidate.state: rc_published`, the RC candidate
  qualification label, RC tag convention; `final_public_release` REMAINS
  false.
- final-published: `packaging/release_record.json` present (schema
  slaif-release-record-v1); digest `D`, `published: true`,
  `final_public_release: true`, the published qualification label, plus a
  closed top-level `release` section bound to the record.

Self-reference exclusion: the manifest (and its schema) and the
post-publication RC record are excluded from every wheel/sdist/image build
input (pyproject top-level exclusions). `generated_from.git_commit` records
the source tree the artifacts were built from; the E3 gate mechanically
proves artifact-input equality by regeneration and requires the recorded
commit to be an ancestor of HEAD, so a pre-freeze manifest may reference a
verified ancestor only when that equality is proven.

Usage:

    python scripts/release_provenance_manifest.py --emit packaging/release_provenance_manifest.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import tomllib
from pathlib import Path

SCHEMA_NAME = "slaif-release-provenance-v4"
SCHEMA_VERSION = 4
OBJECTIVE = "013-i"
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
    "private_registry_auth_required",
    "final_public_release",
    "cutover_performed",
    "wheel_sha256",
    "dependency_lock_sha256",
    "gateway_authority_sha",
    "build_toolchain",
    "deployment_assumptions",
}
REPOSITORY = "ulfe-lmi/slaif-local-coding"
GATEWAY_PEER_FIXTURE = Path("tests/fixtures/gateway/current_peer_authority.json")
PACKAGE_NAME = "slaif-local-coding"
CODIX_CLIENT_VERSION = "0.149.0"
CODIX_WIRE_FIXTURE_DIR = "tests/fixtures/codex/0.149.0"

# Order 013-i, C9: deterministic build toolchain identity. The backend pin is
# asserted against pyproject [build-system].requires on every generation;
# the recorded build-environment set is the resolved dependency set of that
# pinned backend (hatchling 1.32.0) in the isolated build environment
# (Python 3.12, uv 0.12.5).
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
    "artifacts regenerated by objective 013-i on explicitly authorized "
    "inputs only (README cleanup embedded in wheel METADATA; deterministic "
    "hatchling==1.32.0 build-backend pin proven to reproduce the "
    "historical wheel from the clean historical source); the historical "
    "wheel 879baa3ad19e0f513090add965d267957d27f7bcd904d1e225586d76126f8b19 "
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

    Closed key set (slaif-rc-record-v1). The RC record is post-publication
    metadata: it is excluded from every artifact input, keeps
    final_public_release/cutover_performed false by construction, and binds
    the wheel, dependency lock, frozen Gateway authority, and the pinned
    build toolchain. Any deviation is a generation failure, never a
    warning.
    """
    path = repo / RC_RECORD_PATH
    if not path.is_file():
        return None
    record = json.loads(path.read_text(encoding="utf-8"))
    if set(record) != RC_RECORD_KEYS:
        raise RuntimeError(f"rc record key set drift: {sorted(record)}")
    if record["schema"] != "slaif-rc-record-v1":
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
        raise RuntimeError(f"rc record oci_tags must be [{RC_IDENTIFIER}, sha-<source>]")
    if not PUBLISHED_AT_PATTERN.fullmatch(str(record["published_at"])):
        raise RuntimeError("rc record published_at is not RFC 3339 UTC")
    if record["publication_workflow"] != PUBLICATION_WORKFLOW:
        raise RuntimeError("rc record publication_workflow drift")
    run_id = record["publication_workflow_run_id"]
    if run_id is not None and not (
        isinstance(run_id, int) and not isinstance(run_id, bool) and run_id > 0
    ):
        raise RuntimeError("rc record publication_workflow_run_id invalid")
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
    toolchain = record["build_toolchain"]
    if not isinstance(toolchain, dict) or set(toolchain) != {"backend", "uv", "python"}:
        raise RuntimeError("rc record build_toolchain key set drift")
    if toolchain["backend"] != f"{BUILD_BACKEND_NAME}=={BUILD_BACKEND_VERSION}":
        raise RuntimeError("rc record build_toolchain backend drift")
    if toolchain["uv"] != UV_VERSION or toolchain["python"] != "3.12":
        raise RuntimeError("rc record build_toolchain uv/python drift")
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


def _dockerfile_base_images(root: Path) -> tuple[dict, dict]:
    """Return (build_base_image, base_image) parsed from the Dockerfile.

    All three FROM lines must be digest-pinned (B1); any unpinned base is
    a generation failure, never a warning.
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
    return found["uv-provider"], found["build"], found["runtime"]


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


def _assert_build_backend_pin(repo: Path) -> None:
    """Order 013-i, C9: the deterministic build-backend pin must hold.

    The pinned backend is part of the recorded toolchain identity; a drift
    here changes the recorded identity and is a generation failure, never a
    warning.
    """
    with (repo / "pyproject.toml").open("rb") as stream:
        pyproject = tomllib.load(stream)
    requires = pyproject["build-system"]["requires"]
    if requires != [f"{BUILD_BACKEND_NAME}=={BUILD_BACKEND_VERSION}"]:
        raise RuntimeError(
            "build-system requires drift: expected "
            f"[{BUILD_BACKEND_NAME}=={BUILD_BACKEND_VERSION}], got {requires!r}"
        )
    if pyproject["build-system"]["build-backend"] != f"{BUILD_BACKEND_NAME}.build":
        raise RuntimeError("build-backend drift")


def build_manifest(repo: Path, dist_dir: Path) -> dict:
    with (repo / "pyproject.toml").open("rb") as stream:
        pyproject = tomllib.load(stream)
    package_version = pyproject["project"]["version"]
    _assert_build_backend_pin(repo)

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

    peer = json.loads((repo / GATEWAY_PEER_FIXTURE).read_text(encoding="utf-8"))

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
            "git_commit": _git_commit(repo),
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
            "uv_lock_sha256": _sha256_file(repo / "uv.lock"),
            "pyproject_sha256": _sha256_file(repo / "pyproject.toml"),
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
            "python": major_minor,
        },
        "candidate": {
            "rc_identifier": RC_IDENTIFIER,
            "state": "rc_published" if rc_published else "pre_freeze",
            "private_registry_auth_required": True,
            "final_public_release": False,
            "cutover_performed": False,
        },
        "templates": {
            "config_example_sha256": _sha256_file(repo / "config/adapter.example.toml"),
            "deployment_config_template_sha256": _sha256_file(
                repo / "config/adapter.deployment.template.toml"
            ),
            "gateway_integrated_config_template_sha256": _sha256_file(
                repo / "config/adapter.gateway-integrated.template.toml"
            ),
            "service_unit_sha256": _sha256_file(repo / "packaging/slaif-local-coding.service"),
            "service_unit_example_sha256": _sha256_file(
                repo / "packaging/slaif-local-coding.service.example"
            ),
            "readyz_wait_sha256": _sha256_file(repo / "packaging/readyz-wait.sh"),
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

    build_tool_image, build_base_image, base_image = _dockerfile_base_images(repo)
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
        "dockerfile_sha256": _sha256_file(repo / "Dockerfile"),
        "compose_sha256": _sha256_file(repo / "compose.yaml"),
        "dockerignore_sha256": _sha256_file(repo / ".dockerignore"),
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
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    manifest = build_manifest(repo, args.dist.resolve())
    payload = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    args.emit.parent.mkdir(parents=True, exist_ok=True)
    args.emit.write_text(payload, encoding="utf-8")
    print(f"wrote {args.emit} ({len(payload)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
