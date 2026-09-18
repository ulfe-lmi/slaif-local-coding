"""GHCR tag -> digest resolution via the registry v2 API (stdlib only).

Order 013-a: mechanical registry truth used by the release workflow (with
GITHUB_TOKEN) and by the CI `docker-published` job (anonymous pull — the
repository is public, so anonymous GHCR pull is available). Prints exactly
one line: the resolved `sha256:<64-hex>` digest, or `absent` when the tag
does not exist. Exits 0 in both cases; nonzero only on transport/registry
errors (a missing tag is NOT an error).

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


def tag_digest(repo: str, tag: str, token: str | None = None) -> str | None:
    url = f"https://ghcr.io/v2/{repo}/manifests/{urllib.parse.quote(tag)}"
    try:
        return _manifest_digest(url, None)
    except _ChallengeError as challenge_exc:
        challenge = challenge_exc.challenge
    # Exchange with the provided credential first (private-package access),
    # then fall back to anonymous (public packages). If every exchange is
    # denied, the package is absent or unreachable: report `absent`.
    credentials: tuple[str | None, ...] = (token, None) if token else (None,)
    for credential in credentials:
        try:
            issued = _token_from_challenge(challenge, credential)
        except _ExchangeDenied:
            continue
        return _manifest_digest(url, issued)
    return None


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="ulfe-lmi/slaif-local-coding")
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    token = os.environ.get("SLAIF_GHCR_TOKEN") or None
    digest = tag_digest(args.repo, args.tag, token)
    print(digest if digest is not None else "absent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
