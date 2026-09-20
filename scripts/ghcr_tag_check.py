"""GHCR tag -> digest resolution via the registry v2 API (stdlib only).

Order 013-a: mechanical registry truth used by the release workflow (with
GITHUB_TOKEN) and by the CI `docker-published` job. Order 013-i, D13/D15:
the package is PRIVATE, so the strict resolver distinguishes three
outcomes — `digest:<sha256:<64-hex>>`, `absent` (verified: the credentials
resolve the package and the manifest 404s), and `unauthorized` (the
credentials cannot resolve the package: the tag may exist but its state is
inaccessible; fail closed, never report absent).

CLI: one line is printed. Default (legacy) mode prints the digest or
`absent` (an inaccessible package prints `absent` — kept for backward
compatibility with the historical anonymous CI path). `--strict` prints
`digest:<d>` | `absent` | `unauthorized`. Exits 0 for all three outcomes;
nonzero only on transport/registry errors.

Registry access follows the standard distribution v2 client flow (the raw
repository token is NOT accepted directly by the registry API): an
unauthenticated manifest probe, then, on a Bearer challenge, a token
exchange using the provided token as the exchange credential (when any)
and falling back to an anonymous exchange, then one retry with the issued
token. When every exchange is denied (the package does not exist or is not
reachable with the given credentials), the tag is reported as `absent`:
it cannot be resolved with the credentials at hand. The token, when used,
is read from the environment (SLAIF_GHCR_TOKEN) and is never printed,
logged, or placed on a command line.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ACCEPTS = (
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
)


class _ChallengeError(Exception):
    """A Bearer challenge was returned; a token exchange is required."""

    def __init__(self, challenge: str) -> None:
        super().__init__("registry bearer challenge")
        self.challenge = challenge


class _ExchangeDenied(Exception):
    """The token endpoint denied the exchange (401/403)."""


def _challenge_param(challenge: str, name: str) -> str:
    match = re.search(rf'{name}="([^"]*)"', challenge)
    if not match:
        raise RuntimeError(f"registry challenge missing {name}")
    return match.group(1)


def _token_from_challenge(challenge: str, credential: str | None) -> str:
    """Exchange a challenge for an issued Bearer token.

    `credential` (a GitHub token) is sent as the token endpoint's Basic
    credential when provided; otherwise the exchange is anonymous (valid
    for public packages). Raises `_ExchangeDenied` on a 401/403 answer.
    """
    params = [
        ("service", _challenge_param(challenge, "service")),
        ("scope", _challenge_param(challenge, "scope")),
    ]
    token_url = f"{_challenge_param(challenge, 'realm')}?{urllib.parse.urlencode(params)}"
    headers: dict[str, str] = {}
    if credential:
        basic = base64.b64encode(f"x-access-token:{credential}".encode()).decode("ascii")
        headers["Authorization"] = f"Basic {basic}"
    request = urllib.request.Request(token_url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise _ExchangeDenied() from None
        raise
    for key in ("token", "access_token"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    raise RuntimeError("registry token endpoint returned no token")


def _manifest_digest(url: str, bearer: str | None) -> str | None:
    headers = {"Accept": ", ".join(ACCEPTS)}
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    last_status: int | None = None
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                digest_value = response.headers.get("Docker-Content-Digest")
                if isinstance(digest_value, str) and digest_value:
                    return digest_value
                if method == "GET":
                    # 200 without a digest header: hash the exact manifest bytes.
                    return "sha256:" + hashlib.sha256(response.read()).hexdigest()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            last_status = exc.code
            if exc.code in (405, 411):
                continue  # HEAD unsupported -> single GET fallback
            if exc.code in (401, 403):
                challenge = exc.headers.get("WWW-Authenticate", "")
                if challenge.startswith("Bearer"):
                    raise _ChallengeError(challenge) from None
            raise
    raise RuntimeError(f"manifest request unresolved (last status {last_status})")


TAG_STATUS_DIGEST = "digest"
TAG_STATUS_ABSENT = "absent"
TAG_STATUS_UNAUTHORIZED = "unauthorized"


def tag_digest_strict(repo: str, tag: str, token: str | None = None) -> tuple[str, str | None]:
    """Strict registry resolution (order 013-i, D13): a tri-state outcome.

    Returns `(status, digest)`:
    - (`digest`, `sha256:<64-hex>`) — the tag resolves to a manifest;
    - (`absent`, None) — VERIFIED absent: the credentials at hand resolve
      the package and the manifest request 404s;
    - (`unauthorized`, None) — the package cannot be resolved with the
      credentials at hand (token exchange denied, or the manifest request
      401/403s with an issued token). The tag may exist; its state is
      inaccessible. Callers MUST fail closed on this outcome; it must
      never be reported as absent.

    With a token, ONLY the token credential is used (no anonymous
    fallback: against a private package an anonymous answer would be
    indistinguishable from absence). Without a token, the anonymous
    exchange is used (public packages).
    """
    url = f"https://ghcr.io/v2/{repo}/manifests/{urllib.parse.quote(tag)}"
    try:
        value = _manifest_digest(url, None)
        if value is None:
            return (TAG_STATUS_ABSENT, None)
        return (TAG_STATUS_DIGEST, value)
    except _ChallengeError as challenge_exc:
        challenge = challenge_exc.challenge
    credentials: tuple[str | None, ...] = (token,) if token else (None,)
    for credential in credentials:
        try:
            issued = _token_from_challenge(challenge, credential)
        except _ExchangeDenied:
            return (TAG_STATUS_UNAUTHORIZED, None)
        try:
            value = _manifest_digest(url, issued)
        except RuntimeError as exc:
            message = str(exc)
            if "403" in message or "401" in message:
                return (TAG_STATUS_UNAUTHORIZED, None)
            raise
        if value is None:
            return (TAG_STATUS_ABSENT, None)
        return (TAG_STATUS_DIGEST, value)
    return (TAG_STATUS_UNAUTHORIZED, None)


def tag_digest(repo: str, tag: str, token: str | None = None) -> str | None:
    """Legacy conflation (order 013-a): the resolved digest, or None when
    the tag is absent OR inaccessible. Kept for backward compatibility; new
    code must use `tag_digest_strict` and fail closed on unauthorized."""
    status, digest = tag_digest_strict(repo, tag, token)
    return digest if status == TAG_STATUS_DIGEST else None


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="ulfe-lmi/slaif-local-coding")
    parser.add_argument("--tag", required=True)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="tri-state output: digest:<d> | absent | unauthorized",
    )
    args = parser.parse_args()
    token = os.environ.get("SLAIF_GHCR_TOKEN") or None
    if args.strict:
        status, digest = tag_digest_strict(args.repo, args.tag, token)
        if status == TAG_STATUS_DIGEST:
            print(f"digest:{digest}")
        else:
            print(status)
        return 0
    digest = tag_digest(args.repo, args.tag, token)
    print(digest if digest is not None else "absent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
