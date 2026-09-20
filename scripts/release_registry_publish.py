"""Publish the RC candidate image to GHCR and registry-verify one digest.

Order 013-a, workstream D (R11/R12); order 013-c, workstream C1 (fully
qualified push references); order 013-d, workstream C2 (credential
correction); ORDER 013-I, D13/D14 (explicit RC candidate identity on the
PRIVATE package); ORDER 013-J, J1 (verified-absent-for-both write
precondition: no occupied/unresolved identity is ever written over).

Runs ONLY from the activated `.github/workflows/release-image.yml`
(workflow_dispatch-only).

RC publication contract (order 013-j, J1 — simple safe RC policy):

1. EXPLICIT IDENTITY BEFORE ANY DOCKER OR REGISTRY MUTATION: the release
   tag must be EXACTLY the expected RC identity `0.1.0-rc1` (no silently
   allocated new RC number), the repository must be the expected
   `ulfe-lmi/slaif-local-coding`, the git sha must be 40-hex, and any
   final/stable tag (`0.1.0`, `latest`, `stable`, `v0.1.0`) is rejected
   hard. A later final release is a separate later human-authorized act
   with its own explicit order.
2. BEFORE ANY MUTATION, both target tags are checked with authenticated
   registry access via `ghcr_tag_check.tag_digest_strict`, distinguishing
   verified-absent from unauthorized/inaccessible, and any digest the
   registry reports must be well-formed (`sha256:<64-hex>`).
3. THE WRITE PRECONDITION: authenticated verified-absent for BOTH tags is
   the ONLY write precondition. If EITHER the source-SHA tag or the
   candidate tag is occupied, unauthorized/inaccessible, malformed, or
   unresolved, the run STOPS BEFORE ANY registry mutation (no `docker
   tag`, no push). The existing digests are reported for strategy
   adjudication; the publisher never repushes, rebuilds, or re-points an
   already frozen identity. A crash between the two pushes leaves a
   partial state (source tag present, candidate absent) that is REPORTED,
   never silently completed.
4. The target state is RECHECKED (authenticated) immediately before each
   write: once before the source-tag push (both tags) and once before the
   candidate-tag push (the candidate tag). A race-induced occupation fails
   the run with zero further mutation.
5. `sha-<S>` is the SOURCE ALIAS TAG naming the full image-source commit S:
   it is a MUTABLE tag, not a content-addressed identity. The
   content-addressed identity is the immutable registry digest `D`. After
   each push the registry API digest is verified to equal the pushed
   digest; the final verification requires BOTH tags to resolve to the ONE
   digest `D`. Before/after registry states are emitted (D14).
6. emit `SLAIF_PUBLISHED_DIGEST=D` (run log + GITHUB_OUTPUT when set).

Publication runs are serialized by the workflow's `concurrency` group
(`cancel-in-progress: false`: an in-progress publisher is never cancelled),
so the immediate pre-write recheck closes the remaining in-repository race
window. Package visibility is never changed by this script.

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

from ghcr_tag_check import (  # noqa: E402
    TAG_STATUS_ABSENT,
    TAG_STATUS_DIGEST,
    TAG_STATUS_UNAUTHORIZED,
    tag_digest_strict,
)

REPO_DEFAULT = "ulfe-lmi/slaif-local-coding"
RC_TAG_DEFAULT = "0.1.0-rc1"
REGISTRY = "ghcr.io"
# Order 013-i, D13 + order 013-j, J1: this RC workflow must never write a
# final/stable tag, and it publishes EXACTLY the expected RC identity —
# a different tag is not a silent new RC number.
FORBIDDEN_FINAL_TAGS = frozenset({"0.1.0", "latest", "stable", "v0.1.0"})
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


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


def build_push_references(repo: str, git_sha: str, release_tag: str) -> tuple[str, str]:
    """Return the fully qualified (source-alias-tag, candidate-tag) push
    references.

    Order 013-c, C1: both references are qualified against `ghcr.io` so the
    docker CLI resolves them against the GHCR registry instead of letting
    the unqualified `<repo>:<tag>` form resolve against Docker Hub. Pure
    transformation: no docker, network, or I/O.
    """
    sha_tag = f"sha-{git_sha}"
    return (f"{REGISTRY}/{repo}:{sha_tag}", f"{REGISTRY}/{repo}:{release_tag}")


def _state_label(status: str, digest: str | None) -> str:
    if status == TAG_STATUS_DIGEST:
        return f"present at {digest}"
    if status == TAG_STATUS_ABSENT:
        return "verified absent"
    return "unauthorized/inaccessible"


def is_well_formed_digest(digest: str | None) -> bool:
    """Order 013-j, J1: a registry-reported digest must be well-formed;
    anything else is an unresolved identity and fails closed."""
    return digest is not None and DIGEST_PATTERN.fullmatch(digest) is not None


def plan_pre_write(
    sha_tag: str,
    sha_state: tuple[str, str | None],
    rc_tag: str,
    rc_state: tuple[str, str | None],
) -> str:
    """Order 013-j, J1: the verified-absent-for-both write precondition.

    Pure decision over the two authenticated strict tag states. Returns
    ``"proceed"`` ONLY when both tags are authenticated verified-absent.
    Any other combination raises PublishError with the existing digests
    reported for strategy adjudication — the caller must then perform NO
    registry mutation at all (occupied, unauthorized/inaccessible,
    malformed, or unresolved identities are never written over).
    """
    sha_status, sha_pre = sha_state
    rc_status, rc_pre = rc_state

    unverifiable = []
    if sha_status == TAG_STATUS_UNAUTHORIZED:
        unverifiable.append(f"source tag {sha_tag}")
    if rc_status == TAG_STATUS_UNAUTHORIZED:
        unverifiable.append(f"candidate tag {rc_tag}")
    if unverifiable:
        raise PublishError(
            "pre-write tag check could not be verified with the credentials "
            f"at hand ({'; '.join(unverifiable)}); failing closed BEFORE any "
            "registry mutation (order 013-j, J1)"
        )
    malformed = []
    if sha_status == TAG_STATUS_DIGEST and not is_well_formed_digest(sha_pre):
        malformed.append(f"{sha_tag}={sha_pre!r}")
    if rc_status == TAG_STATUS_DIGEST and not is_well_formed_digest(rc_pre):
        malformed.append(f"{rc_tag}={rc_pre!r}")
    if malformed:
        raise PublishError(
            "registry reported a malformed digest for "
            f"{'; '.join(malformed)}; the identity is unresolved, failing "
            "closed BEFORE any registry mutation (order 013-j, J1)"
        )
    if sha_status == TAG_STATUS_DIGEST:
        hint = ""
        if rc_status == TAG_STATUS_DIGEST and rc_pre == sha_pre:
            hint = (
                " The candidate tag is at the SAME digest: the state "
                "indicates a prior completed publication of this identity."
            )
        elif rc_status == TAG_STATUS_ABSENT:
            hint = (
                " The candidate tag is verified absent: this is a PARTIAL "
                "prior publication state (source pushed, candidate not "
                "pushed). No registry mutation was performed; recovery "
                "requires an explicit strategy decision — this publisher "
                "never re-pushes or auto-completes."
            )
        raise PublishError(
            f"source tag {sha_tag} is OCCUPIED at {sha_pre}; STOPPING BEFORE "
            "ANY registry mutation. Existing digests for strategy "
            f"adjudication: {sha_tag}={sha_pre}, {rc_tag}="
            f"{rc_pre if rc_status == TAG_STATUS_DIGEST else 'verified absent'}. "
            "An already frozen identity is never repushed or rebuilt."
            f"{hint} (order 013-j, J1)"
        )
    if rc_status == TAG_STATUS_DIGEST:
        raise PublishError(
            f"candidate tag {rc_tag} is OCCUPIED at {rc_pre} (source tag "
            f"{sha_tag} verified absent); STOPPING BEFORE ANY registry "
            "mutation. Existing digests for strategy adjudication: "
            f"{rc_tag}={rc_pre}. Possible partial prior publication; this "
            "publisher never overwrites an occupied RC identity "
            "(order 013-j, J1)"
        )
    return "proceed"


def _strict_both(
    repo: str, sha_tag: str, rc_tag: str, token: str
) -> tuple[tuple[str, str | None], tuple[str, str | None]]:
    """Authenticated strict checks of both target tags; an unresolved
    registry/transport error fails closed (never treated as absent)."""
    try:
        sha_state = tag_digest_strict(repo, sha_tag, token)
        rc_state = tag_digest_strict(repo, rc_tag, token)
    except Exception as exc:  # noqa: BLE001 - fail-closed law at the boundary
        raise PublishError(
            f"pre-write tag check unresolved (registry/transport error: "
            f"{exc.__class__.__name__}); failing closed BEFORE any registry "
            "mutation (order 013-j, J1)"
        ) from None
    return sha_state, rc_state


def self_check_references() -> int:
    """Deterministic local proof (order 013-c, C1; order 013-i D13; order
    013-j J1; NO host push). Asserts the exact qualified reference strings
    the script builds for a fixture git-sha, the RC default tag, and the
    final-tag guard."""
    fixture_sha = "0" * 40
    expected = (
        f"{REGISTRY}/{REPO_DEFAULT}:sha-{fixture_sha}",
        f"{REGISTRY}/{REPO_DEFAULT}:{RC_TAG_DEFAULT}",
    )
    built = build_push_references(REPO_DEFAULT, fixture_sha, RC_TAG_DEFAULT)
    if built != expected:
        message = f"reference self-check FAILED: built={built!r} expected={expected!r}"
        print(message, file=sys.stderr)
        return 1
    for forbidden in sorted(FORBIDDEN_FINAL_TAGS):
        if forbidden not in FORBIDDEN_FINAL_TAGS:
            print(f"final-tag guard self-check FAILED for {forbidden}", file=sys.stderr)
            return 1
    print(
        f"reference self-check OK: source-alias {built[0]}; candidate-tag {built[1]}; "
        f"forbidden final tags {sorted(FORBIDDEN_FINAL_TAGS)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-image", help="locally built image tag")
    parser.add_argument("--git-sha", help="full image-source commit S")
    parser.add_argument("--repo", default=REPO_DEFAULT)
    parser.add_argument(
        "--release-tag",
        default=RC_TAG_DEFAULT,
        help="candidate tag to publish; EXACTLY 0.1.0-rc1 is the only "
        "accepted value for this RC publisher (default)",
    )
    parser.add_argument(
        "--self-check-refs",
        action="store_true",
        help="local proof that the built push references are qualified and "
        "the final-tag guard holds (no docker, no push)",
    )
    args = parser.parse_args()

    if args.self_check_refs:
        return self_check_references()
    if not args.local_image or not args.git_sha:
        parser.error("--local-image and --git-sha are required for publication")

    # --- Explicit expected identity BEFORE any docker/registry access ----
    if args.release_tag in FORBIDDEN_FINAL_TAGS:
        raise PublishError(
            f"refusing to publish final/stable tag {args.release_tag!r} from "
            "the RC workflow: a later final release is a separate later "
            "human-authorized act (order 013-i, D13)"
        )
    if args.release_tag != RC_TAG_DEFAULT:
        raise PublishError(
            f"release tag {args.release_tag!r} is not the expected RC "
            f"identity {RC_TAG_DEFAULT!r}: this RC publisher publishes "
            "exactly the explicit RC1 identity and never silently "
            "allocates a new RC number (order 013-j, J1)"
        )
    if args.repo != REPO_DEFAULT:
        raise PublishError(
            f"repository {args.repo!r} is not the expected "
            f"{REPO_DEFAULT!r}; the expected repository is validated before "
            "any Docker mutation (order 013-j, J1)"
        )
    if not re.fullmatch(r"[0-9a-f]{40}", args.git_sha):
        raise PublishError("git-sha must be 40-hex")

    token = os.environ.get("SLAIF_GHCR_TOKEN") or None
    if token is None:
        raise PublishError(
            "SLAIF_GHCR_TOKEN is required: the RC package is private and its "
            "tag state cannot be verified anonymously (fail closed)"
        )
    sha_tag = f"sha-{args.git_sha}"
    sha_ref, release_ref = build_push_references(args.repo, args.git_sha, args.release_tag)

    # --- Pre-mutation: authenticated tri-state checks (D13/J1) ------------
    sha_state, rc_state = _strict_both(args.repo, sha_tag, args.release_tag, token)
    print(
        f"registry before: {sha_tag} = {_state_label(sha_state[0], sha_state[1])}; "
        f"{args.release_tag} = {_state_label(rc_state[0], rc_state[1])}",
        flush=True,
    )
    plan_pre_write(sha_tag, sha_state, args.release_tag, rc_state)

    # --- Immediate pre-write recheck (J1: recheck before the write) -------
    sha_state2, rc_state2 = _strict_both(args.repo, sha_tag, args.release_tag, token)
    plan_pre_write(sha_tag, sha_state2, args.release_tag, rc_state2)

    # --- Push the source-alias tag sha-<S> (mutable alias, not a digest) --
    print(f"publishing {args.local_image} as source alias {sha_ref}", flush=True)
    _docker("tag", args.local_image, sha_ref)
    push_digest = _push_digest(sha_ref)
    if not is_well_formed_digest(push_digest):
        raise PublishError(f"push digest malformed: {push_digest!r}")
    api_status, api_digest = tag_digest_strict(args.repo, sha_tag, token)
    if api_status != TAG_STATUS_DIGEST or not is_well_formed_digest(api_digest):
        raise PublishError(
            f"post-push registry state unresolved for {sha_tag}: "
            f"{_state_label(api_status, api_digest)}; failing closed"
        )
    if api_digest != push_digest:
        raise PublishError(f"registry/api digest mismatch: push={push_digest} api={api_digest}")
    print(f"registry source alias {sha_tag} -> {api_digest}", flush=True)

    # --- Candidate tag: recheck immediately before its write (J1) ---------
    rc_status3, rc_pre3 = tag_digest_strict(args.repo, args.release_tag, token)
    if rc_status3 != TAG_STATUS_ABSENT:
        raise PublishError(
            f"candidate tag {args.release_tag} recheck immediately before its "
            f"write reports {_state_label(rc_status3, rc_pre3)} (source alias "
            f"{sha_tag} was just written at {api_digest}); PARTIAL prior "
            "publication state — NO further registry mutation performed; "
            "report for strategy adjudication (order 013-j, J1)"
        )

    _docker("tag", args.local_image, release_ref)
    release_push_digest = _push_digest(release_ref)
    if release_push_digest != api_digest:
        raise PublishError(
            f"{args.release_tag} push digest differs from source-alias "
            f"digest: {release_push_digest} vs {api_digest}"
        )

    # --- Final registry verification: both tags -> one digest -------------
    verify_rc_status, verify_rc = tag_digest_strict(args.repo, args.release_tag, token)
    verify_sha_status, verify_sha = tag_digest_strict(args.repo, sha_tag, token)
    if (
        verify_rc_status != TAG_STATUS_DIGEST
        or verify_sha_status != TAG_STATUS_DIGEST
        or verify_rc != api_digest
        or verify_sha != api_digest
    ):
        raise PublishError(
            f"final registry verification failed: {args.release_tag}="
            f"{_state_label(verify_rc_status, verify_rc)} {sha_tag}="
            f"{_state_label(verify_sha_status, verify_sha)} expected={api_digest}"
        )

    digest = api_digest
    print(
        f"registry after: {sha_tag} = present at {digest}; "
        f"{args.release_tag} = present at {digest}",
        flush=True,
    )
    print(f"SLAIF_PUBLISHED_DIGEST={digest}", flush=True)
    print(json.dumps({"tag": args.release_tag, "digest": digest}, sort_keys=True), flush=True)
    print(json.dumps({"tag": sha_tag, "digest": digest}, sort_keys=True), flush=True)
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"published_digest={digest}\n")
            handle.write(f"published_tag={args.release_tag}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
