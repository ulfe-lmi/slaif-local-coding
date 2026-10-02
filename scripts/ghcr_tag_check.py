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
from pathlib import Path

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


# ---------------------------------------------------------------------------
# Order 015-b, workstream C: the immutable historical registry identities.
#
# The docker-published job's READ-ONLY registry baseline
# (.github/workflows/ci.yml) must assert that, for EVERY archived RC
# candidate, BOTH of its aliases (the candidate tag and the
# sha-<image-source-commit> tag) remain resolvable at the EXACT digest
# recorded in the archived strict record
# (packaging/releases/<rc>/rc_record.json). This module is the single
# source of truth for that set, so the workflow and the deterministic
# regression (tests/test_registry_history_baseline.py) cannot drift:
#
# - every packaging/releases/<rc>/rc_record.json is strictly loaded
#   (schema name, directory/identifier agreement, 40-hex source commit,
#   well-formed sha256 digest, exact [candidate, sha-<source>] tag pair);
#   any structural violation fails closed;
# - each archived record contributes its two aliases bound to its
#   recorded digest (digest-asserted, fail closed on absent,
#   unauthorized, ambiguous, or changed registry state);
# - the pre-RC singletons (the historical private 0.1.0 tag and the two
#   recorded orphan sha- tags, order 013-a/013-n era) have no archived
#   record and therefore remain record-only (expected digest None), per
#   the original order 013-l convention;
# - no RC6 identity was ever created (the 014-d attempt was abandoned
#   before any push, tag, or publication), and no code path here may
#   create or reserve one.
#
# Read-only: nothing below mutates the registry or the repository.
# ---------------------------------------------------------------------------

PRE_RC_SINGLETON_TAGS: tuple[str, ...] = (
    "0.1.0",
    "sha-fe334e87c9f0fc65d1826cf9af7dad7e9f70a94a",
    "sha-be3c78b2016d5d40ce9155df8f94d14525c43d39",
)

RC_ARCHIVE_DIR = "packaging/releases"
# The closed set of strict record schemas that archived candidates may
# carry: v2 (RC1/RC2, order 013-n era) and v3 (RC3 onward). Any other
# schema fails closed.
RC_RECORD_SCHEMAS: frozenset[str] = frozenset({"slaif-rc-record-v2", "slaif-rc-record-v3"})
RC_IDENTIFIER_PATTERN = re.compile(r"^0\.1\.0-rc(\d+)$")


class RegistryHistoryError(RuntimeError):
    """The archived record set is structurally invalid (fail closed)."""


def load_archived_rc_records(repo_root: Path | str) -> dict[str, dict]:
    """Strictly load every archived strict RC record under the repository
    convention ``packaging/releases/<rc>/rc_record.json``.

    Returns ``{rc_identifier: record}`` in ascending RC order. Fails
    closed (``RegistryHistoryError``) when an ``0.1.0-rc<N>`` directory
    lacks its record, when a record is unreadable or malformed, when the
    directory name disagrees with the record's ``rc_identifier``, when
    the schema is not one of the closed historical strict schemas
    (``slaif-rc-record-v2`` / ``slaif-rc-record-v3``), when the source
    commit is not 40-hex, when the digest is not ``sha256:<64-hex>``, or
    when the tag pair is not exactly
    ``[rc_identifier, sha-<source_commit>]``.
    """
    root = Path(repo_root) / RC_ARCHIVE_DIR
    records: dict[str, dict] = {}
    if not root.is_dir():
        return records
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        if RC_IDENTIFIER_PATTERN.fullmatch(entry.name) is None:
            continue  # non-RC directories are not archive records
        path = entry / "rc_record.json"
        if not path.is_file():
            raise RegistryHistoryError(
                f"archived directory {entry.name}/ lacks its strict record "
                "(fail closed: an archived RC identity must carry the "
                "record that binds its alias pair)"
            )
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise RegistryHistoryError(
                f"archived record for {entry.name} is unreadable "
                f"({type(exc).__name__}) (fail closed)"
            ) from None
        if not isinstance(record, dict):
            raise RegistryHistoryError(
                f"archived record for {entry.name} is not an object (fail closed)"
            )
        if record.get("schema") not in RC_RECORD_SCHEMAS:
            raise RegistryHistoryError(
                f"archived record for {entry.name} has schema "
                f"{record.get('schema')!r}, expected one of "
                f"{sorted(RC_RECORD_SCHEMAS)} (fail closed)"
            )
        if record.get("rc_identifier") != entry.name:
            raise RegistryHistoryError(
                f"archived record for {entry.name} names rc_identifier "
                f"{record.get('rc_identifier')!r} (fail closed)"
            )
        source = record.get("image_source_commit")
        if not isinstance(source, str) or not re.fullmatch(r"[0-9a-f]{40}", source):
            raise RegistryHistoryError(
                f"archived record for {entry.name} has a malformed "
                "image_source_commit (fail closed)"
            )
        digest = record.get("oci_image_digest")
        if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise RegistryHistoryError(
                f"archived record for {entry.name} has a malformed oci_image_digest (fail closed)"
            )
        tags = record.get("oci_tags")
        expected_tags = [entry.name, f"sha-{source}"]
        if not isinstance(tags, list) or [str(t) for t in tags] != expected_tags:
            raise RegistryHistoryError(
                f"archived record for {entry.name} has tag pair {tags!r}, "
                f"expected {expected_tags!r} (fail closed)"
            )
        records[entry.name] = record
    return records


def immutable_historical_baseline(repo_root: Path | str) -> tuple[tuple[str, str | None], ...]:
    """The ordered ``(tag, expected_digest)`` set for the read-only
    registry baseline (single source of truth, order 015-b, workstream C):

    - the pre-RC singleton tags first (record-only: ``expected_digest``
      is None, per the order 013-l convention);
    - then, for every archived strict RC record in ascending RC order,
      its candidate tag followed by its ``sha-<source>`` tag, each bound
      to the record's ``oci_image_digest`` (digest-asserted).

    The intentional RC6 absence is structural: no ``0.1.0-rc6`` archive
    contributes anything, and nothing here may ever create or reserve an
    RC6 identity.
    """
    entries: list[tuple[str, str | None]] = [(tag, None) for tag in PRE_RC_SINGLETON_TAGS]
    records = load_archived_rc_records(repo_root)
    for rc_id in sorted(records, key=lambda rc: int(RC_IDENTIFIER_PATTERN.fullmatch(rc).group(1))):
        record = records[rc_id]
        for tag in (rc_id, f"sha-{record['image_source_commit']}"):
            entries.append((tag, str(record["oci_image_digest"])))
    return tuple(entries)


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
