"""Publish the release image to GHCR and registry-verify a single digest.

Order 013-a, workstream D (R11/R12); order 013-c, workstream C1 (fully
qualified push references); order 013-d, workstream C2 (credential
correction). Runs ONLY from the activated
`.github/workflows/release-image.yml` (workflow_dispatch-only).
Procedure:

1. push the built image as `ghcr.io/<repo>:sha-<S>` UNCONDITIONALLY
   (content-addressed by the full image-source commit);
2. capture the pushed digest `D` from the push output and re-verify it
   against the registry API;
3. query the registry for the pre-existing `0.1.0` tag: absent -> publish;
   already at `D` -> idempotent no-op; ANY other digest -> FAIL (no silent
   repoint of the release tag);
4. push `0.1.0` and registry-verify BOTH tags resolve to `D`;
5. emit `SLAIF_PUBLISHED_DIGEST=D` (run log + GITHUB_OUTPUT when set).

The registry credential is the workflow `GITHUB_TOKEN` (declared
`packages: write`), passed to the script via the `SLAIF_GHCR_TOKEN`
environment variable, and is never printed, logged, or placed on a command
line. Stdlib + docker CLI only; no new dependencies.
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
RELEASE_TAG = "0.1.0"
REGISTRY = "ghcr.io"


class PublishError(RuntimeError):
    pass


def _docker(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    proc = subprocess.run(["docker", *args], capture_output=True, timeout=1800)
    if check and proc.returncode != 0:
        raise PublishError(f"docker {' '.join(args[:4])} failed: {proc.stderr.decode()[:2000]}")
    return proc


PUSH_DIGEST_LINE_RE = re.compile(
    r"^(?:[^ ]+:\s+)?digest:\s?sha256:([0-9a-f]{64})(?:\s+size:\s?\d+)?\s*$"
)


def extract_push_digest(output: str) -> str | None:
    """Return the sha256 digest from docker push output, or None.

    Accepts the final digest line in the two observed docker-CLI forms:
    '<ref>: digest:sha256:<64-hex> size:<n>' (current CLI, non-TTY; the CLI
    prints the size suffix with or without a space after the colon) and the
    legacy bare 'digest: sha256:<64-hex>' / 'digest:sha256:<64-hex>'. Scans
    all lines (str.splitlines); returns the LAST match's digest.
    """
    digest: str | None = None
    for line in output.splitlines():
        match = PUSH_DIGEST_LINE_RE.match(line.strip())
        if match:
            digest = "sha256:" + match.group(1)
    return digest


def _push_digest(ref: str) -> str:
    """Push `ref` and return the `sha256:<64-hex>` digest from the push log.

    Order 013-e, D1: the docker CLI (non-TTY) emits push progress — including
    the final digest line — on stderr, so the digest is extracted from the
    joined stdout+stderr output (stdout first) via `extract_push_digest`.
    """
    proc = _docker("push", ref)
    combined = proc.stdout.decode() + proc.stderr.decode()
    digest = extract_push_digest(combined)
    if digest is not None:
        return digest
    token = os.environ.get("SLAIF_GHCR_TOKEN") or ""
    non_empty = [line for line in combined.splitlines() if line.strip()]
    tail = non_empty[-25:]
    if token:
        tail = [line.replace(token, "***") for line in tail]
    raise PublishError(f"no digest line in push output for {ref}; tail:\n" + "\n".join(tail))


def build_push_references(repo: str, git_sha: str) -> tuple[str, str]:
    """Return the fully qualified (sha-tag, release-tag) push references.

    Order 013-c, C1: both references are qualified against `ghcr.io` so the
    docker CLI resolves them against the GHCR registry instead of letting
    the unqualified `<repo>:<tag>` form resolve against Docker Hub. Pure
    transformation: no docker, network, or I/O.
    """
    sha_tag = f"sha-{git_sha}"
    return (f"{REGISTRY}/{repo}:{sha_tag}", f"{REGISTRY}/{repo}:{RELEASE_TAG}")


def self_check_references() -> int:
    """Deterministic local proof (order 013-c, C1; NO host push).

    Asserts the exact qualified reference strings the script builds for a
    fixture git-sha; exits nonzero on any deviation.
    """
    fixture_sha = "0" * 40
    expected = (
        f"{REGISTRY}/{REPO_DEFAULT}:sha-{fixture_sha}",
        f"{REGISTRY}/{REPO_DEFAULT}:{RELEASE_TAG}",
    )
    built = build_push_references(REPO_DEFAULT, fixture_sha)
    if built != expected:
        message = f"reference self-check FAILED: built={built!r} expected={expected!r}"
        print(message, file=sys.stderr)
        return 1
    print(f"reference self-check OK: sha-tag {built[0]}; release-tag {built[1]}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-image", help="locally built image tag")
    parser.add_argument("--git-sha", help="full image-source commit S")
    parser.add_argument("--repo", default=REPO_DEFAULT)
    parser.add_argument(
        "--self-check-refs",
        action="store_true",
        help="local proof that the built push references are qualified (no docker, no push)",
    )
    args = parser.parse_args()

    if args.self_check_refs:
        return self_check_references()
    if not args.local_image or not args.git_sha:
        parser.error("--local-image and --git-sha are required for publication")

    if not re.fullmatch(r"[0-9a-f]{40}", args.git_sha):
        raise PublishError("git-sha must be 40-hex")
    token = os.environ.get("SLAIF_GHCR_TOKEN") or None
    sha_tag = f"sha-{args.git_sha}"
    sha_ref, release_ref = build_push_references(args.repo, args.git_sha)

    print(f"publishing {args.local_image} as {sha_ref}", flush=True)
    _docker("tag", args.local_image, sha_ref)
    push_digest = _push_digest(sha_ref)
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

    _docker("tag", args.local_image, release_ref)
    release_push_digest = _push_digest(release_ref)
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
