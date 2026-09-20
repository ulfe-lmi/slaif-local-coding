"""RC artifact record generator (order 013-i, C12).

Prepares the machine-readable RC artifact record
(`packaging/rc_record.json`, schema `slaif-rc-record-v1`). The record is
populated from VERIFIED FACTS during the publication round only:

- the exact image source commit `S` the image was built from;
- the OCI registry digest `D` verified against the registry (authenticity
  proven by the publishing run; a fake digest or a claimed publication is
  rejected — there is no mode that records an unpublished image as
  published);
- the provenance-manifest wheel SHA-256, the dependency-lock (uv.lock)
  SHA-256, and the frozen Gateway compatibility authority commit;
- the pinned build toolchain (backend/uv/python) and the supported
  deployment assumptions (fixed const strings).

The record keeps `final_public_release: false` and `cutover_performed:
false` BY CONSTRUCTION (the schema also const-pins them): a published RC
must never imply final release. The record is post-publication metadata:
it is excluded from every wheel/sdist/image build input (pyproject
top-level exclusions) and is never a self-reference input to the
provenance manifest (the manifest cross-checks the record's facts; the
record does not hash the manifest).

Safety law: an existing `packaging/rc_record.json` is a frozen identity —
this generator refuses to overwrite it unless the freshly built record is
byte-identical (same source + digest facts). No other partial update is
possible.

Usage (publication round only):

    python scripts/rc_artifact_record.py \\
        --source <40-hex image source commit> \\
        --digest sha256:<64-hex verified registry digest> \\
        --published-at 2026-01-01T00:00:00Z \\
        [--run-id <int>] \\
        [--emit packaging/rc_record.json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

MANIFEST_PATH = Path("packaging/release_provenance_manifest.json")
UV_LOCK_PATH = Path("uv.lock")

RC_IDENTIFIER = "0.1.0-rc1"
PRODUCT_VERSION = "0.1.0"
IMAGE_REFERENCE = "ghcr.io/ulfe-lmi/slaif-local-coding"
PUBLICATION_WORKFLOW = "release-image.yml"
BUILD_BACKEND = "hatchling==1.32.0"
UV_VERSION = "0.12.5"
PYTHON = "3.12"
DEPLOYMENT_ASSUMPTIONS = (
    "linux-docker-engine-compose-v2;host-network-mode;"
    "private-same-host-upstream;separate-gateway;loopback-default-bind"
)
PUBLISHED_AT_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


class RCRecordError(RuntimeError):
    pass


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_rc_record(
    repo: Path,
    source: str,
    digest: str,
    published_at: str,
    run_id: int | None,
) -> dict:
    """Build the RC record from verified facts. Pure transformation: no
    network, no registry access, no docker; the caller must supply the
    registry-verified digest of the pushed image."""
    if not re.fullmatch(r"[0-9a-f]{40}", source):
        raise RCRecordError("source commit must be 40-hex")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise RCRecordError("digest must be sha256:<64-hex>")
    if not PUBLISHED_AT_PATTERN.fullmatch(published_at):
        raise RCRecordError("published_at must be RFC 3339 UTC (Z)")
    if run_id is not None and not (
        isinstance(run_id, int) and not isinstance(run_id, bool) and run_id > 0
    ):
        raise RCRecordError("run_id must be a positive integer or null")

    manifest = json.loads((repo / MANIFEST_PATH).read_text(encoding="utf-8"))
    wheel_sha256 = str(manifest["artifacts"]["wheel"]["sha256"])
    if not re.fullmatch(r"[0-9a-f]{64}", wheel_sha256):
        raise RCRecordError("manifest wheel sha256 is not 64-hex")
    gateway_authority_sha = str(manifest["gateway_peer"]["commit"])
    if not re.fullmatch(r"[0-9a-f]{40}", gateway_authority_sha):
        raise RCRecordError("manifest gateway peer commit is not 40-hex")
    dependency_lock_sha256 = _sha256_file(repo / UV_LOCK_PATH)

    return {
        "schema": "slaif-rc-record-v1",
        "rc_identifier": RC_IDENTIFIER,
        "product_version": PRODUCT_VERSION,
        "image_source_commit": source,
        "oci_image_reference": IMAGE_REFERENCE,
        "oci_image_digest": digest,
        "oci_tags": [RC_IDENTIFIER, f"sha-{source}"],
        "published_at": published_at,
        "publication_workflow": PUBLICATION_WORKFLOW,
        "publication_workflow_run_id": run_id,
        "private_registry_auth_required": True,
        "final_public_release": False,
        "cutover_performed": False,
        "wheel_sha256": wheel_sha256,
        "dependency_lock_sha256": dependency_lock_sha256,
        "gateway_authority_sha": gateway_authority_sha,
        "build_toolchain": {
            "backend": BUILD_BACKEND,
            "uv": UV_VERSION,
            "python": PYTHON,
        },
        "deployment_assumptions": DEPLOYMENT_ASSUMPTIONS,
    }


def emit_rc_record(repo: Path, emit: Path, record: dict) -> str:
    """Atomically write the record; refuse to overwrite a frozen identity
    that is not byte-identical."""
    if emit.is_file():
        existing = emit.read_text(encoding="utf-8")
        payload = json.dumps(record, indent=2, sort_keys=True) + "\n"
        if existing != payload:
            raise RCRecordError(
                f"refusing to overwrite frozen RC record {emit}: the freshly "
                "built record differs; an already frozen identity must not "
                "be rewritten"
            )
        return "unchanged"
    emit.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{emit.name}.", dir=emit.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, emit)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    return "written"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="40-hex image source commit")
    parser.add_argument("--digest", required=True, help="verified registry digest sha256:<64-hex>")
    parser.add_argument("--published-at", required=True, help="RFC 3339 UTC timestamp")
    parser.add_argument("--run-id", type=int, default=None, help="workflow run id (optional)")
    parser.add_argument(
        "--emit",
        type=Path,
        default=Path("packaging/rc_record.json"),
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    record = build_rc_record(repo, args.source, args.digest, args.published_at, args.run_id)
    state = emit_rc_record(repo, args.emit.resolve(), record)
    print(f"rc record {state}: {args.emit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
