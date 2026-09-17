"""Publish the release image to GHCR and registry-verify a single digest.

Order 013-a, workstream D (R11/R12). Runs ONLY from the activated
`.github/workflows/release-image.yml` (workflow_dispatch-only, GITHUB_TOKEN
only). Procedure:

1. push the built image as `ghcr.io/<repo>:sha-<S>` UNCONDITIONALLY
   (content-addressed by the full image-source commit);
2. capture the pushed digest `D` from the push output and re-verify it
   against the registry API;
3. query the registry for the pre-existing `0.1.0` tag: absent -> publish;
   already at `D` -> idempotent no-op; ANY other digest -> FAIL (no silent
   repoint of the release tag);
4. push `0.1.0` and registry-verify BOTH tags resolve to `D`;
5. emit `SLAIF_PUBLISHED_DIGEST=D` (run log + GITHUB_OUTPUT when set).

The registry credential is read from the environment (SLAIF_GHCR_TOKEN) and
is never printed, logged, or placed on a command line. Stdlib + docker CLI
only; no new dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ghcr_tag_check import tag_digest  # noqa: E402

REPO_DEFAULT = "ulfe-lmi/slaif-local-coding"


class PublishError(RuntimeError):
    pass


def _docker(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    proc = subprocess.run(["docker", *args], capture_output=True, timeout=1800)
    if check and proc.returncode != 0:
        raise PublishError(f"docker {' '.join(args[:4])} failed: {proc.stderr.decode()[:2000]}")
    return proc


def _push_digest(ref: str) -> str:
    """Push `ref` and return the `sha256:<64-hex>` digest from the push log."""
    proc = _docker("push", ref)
    stdout = proc.stdout.decode()
    for line in reversed(stdout.splitlines()):
        m = re.match(r"^digest:\s*(sha256:[0-9a-f]{64})\s*$", line.strip())
        if m:
            return m.group(1)
    raise PublishError(f"no digest line in push output for {ref}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-image", required=True, help="locally built image tag")
    parser.add_argument("--git-sha", required=True, help="full image-source commit S")
    parser.add_argument("--repo", default=REPO_DEFAULT)
    args = parser.parse_args()

    if not re.fullmatch(r"[0-9a-f]{40}", args.git_sha):
        raise PublishError("git-sha must be 40-hex")
    token = os.environ.get("SLAIF_GHCR_TOKEN") or None
    sha_tag = f"sha-{args.git_sha}"

    print(f"publishing {args.local_image} as {args.repo}:{sha_tag}", flush=True)
    _docker("tag", args.local_image, f"{args.repo}:{sha_tag}")
    push_digest = _push_digest(f"{args.repo}:{sha_tag}")
    api_digest = tag_digest(args.repo, sha_tag, token)
    if api_digest != push_digest:
        raise PublishError(f"registry/api digest mismatch: push={push_digest} api={api_digest}")
    print(f"registry tag {sha_tag} -> {api_digest}", flush=True)

    existing = tag_digest(args.repo, "0.1.0", token)
    if existing is not None and existing != api_digest:
        raise PublishError(
            "pre-existing 0.1.0 tag points at a DIFFERENT digest "
            f"({existing}); refusing to silently repoint the release tag"
        )
    if existing is not None:
        print("0.1.0 already present at the same digest (idempotent republish)", flush=True)

    _docker("tag", args.local_image, f"{args.repo}:0.1.0")
    release_push_digest = _push_digest(f"{args.repo}:0.1.0")
    if release_push_digest != api_digest:
        raise PublishError(
            f"0.1.0 push digest differs from sha-<S> digest: {release_push_digest} vs {api_digest}"
        )
    verify_010 = tag_digest(args.repo, "0.1.0", token)
    verify_sha = tag_digest(args.repo, sha_tag, token)
    if verify_010 != api_digest or verify_sha != api_digest:
        raise PublishError(
            f"final registry verification failed: 0.1.0={verify_010} "
            f"{sha_tag}={verify_sha} expected={api_digest}"
        )

    digest = api_digest
    print(f"SLAIF_PUBLISHED_DIGEST={digest}", flush=True)
    print(json.dumps({"tag": "0.1.0", "digest": digest}, sort_keys=True), flush=True)
    print(json.dumps({"tag": sha_tag, "digest": digest}, sort_keys=True), flush=True)
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"published_digest={digest}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
