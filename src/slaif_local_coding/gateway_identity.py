"""Versioned, replay-protected gateway identity verification.

This module is deliberately independent of request transformation.  It accepts
only bounded raw request facts, verifies the service credential first in the
caller, and returns one immutable identity for the rest of the request.
"""

from __future__ import annotations

import hashlib
import hmac
import math
import re
import threading
import time
from collections import OrderedDict

from fastapi import Request

from .config import GatewayIngressConfig
from .constitution.cache import RequestIdentity

SIGNED_IDENTITY_HEADERS = (
    "x-slaif-identity-version",
    "x-slaif-principal",
    "x-slaif-session",
    "x-slaif-repository",
    "x-slaif-route",
    "x-slaif-timestamp",
    "x-slaif-nonce",
    "x-slaif-signature",
)
SUPPORTED_SIGNED_METHODS = frozenset({"GET", "POST"})
SUPPORTED_SIGNED_PATHS = frozenset(
    {"/health", "/v1/models", "/v1/responses", "/v1/chat/completions"}
)
_OPAQUE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,255}$")
_TIMESTAMP_RE = re.compile(r"^(?:0|[1-9][0-9]{0,19})$")
_NONCE_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_SIGNATURE_RE = re.compile(r"^v1=[0-9a-f]{64}$")


class SignedIdentityError(Exception):
    """Fixed public failure facts; never contains request identity values."""

    def __init__(self, status_code: int, code: str) -> None:
        super().__init__(code)
        self.status_code = status_code
        self.code = code


class ReplayProtector:
    """Bounded process-local nonce digest TTL/LRU state."""

    def __init__(self, *, ttl_seconds: int, max_entries: int) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._entries: OrderedDict[str, float] = OrderedDict()
        self._lock = threading.Lock()

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._entries)

    def reserve(self, nonce_digest: str, *, now: float) -> bool:
        """Atomically reserve one digest, returning false for an active replay."""
        if not re.fullmatch(r"[0-9a-f]{64}", nonce_digest):
            raise ValueError("nonce digest is invalid")
        if not math.isfinite(now):
            raise ValueError("replay clock is invalid")
        expires_at = now + self.ttl_seconds
        with self._lock:
            expired = [key for key, expiry in self._entries.items() if expiry <= now]
            for key in expired:
                self._entries.pop(key, None)
            if nonce_digest in self._entries:
                self._entries.move_to_end(nonce_digest)
                return False
            while len(self._entries) >= self.max_entries:
                self._entries.popitem(last=False)
            self._entries[nonce_digest] = expires_at
            return True


def _one_header(request: Request, name: str) -> str:
    values = request.headers.getlist(name)
    if len(values) != 1:
        raise SignedIdentityError(422, "signed_identity_headers_invalid")
    return values[0]


def _reject_extra_signed_headers(request: Request) -> None:
    allowed = set(SIGNED_IDENTITY_HEADERS)
    for name in request.headers.keys():
        lowered = name.lower()
        if lowered.startswith("x-slaif-") and lowered not in allowed:
            raise SignedIdentityError(422, "signed_identity_headers_invalid")


def _validate_opaque(value: str) -> str:
    if not _OPAQUE_RE.fullmatch(value):
        raise SignedIdentityError(422, "signed_identity_field_invalid")
    # Dotted-quad addresses are excluded even if a future grammar is widened.
    if re.fullmatch(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}", value):
        raise SignedIdentityError(422, "signed_identity_field_invalid")
    return value


def canonical_identity_bytes(
    *,
    method: str,
    path: str,
    raw_query: bytes,
    body: bytes,
    principal: str,
    session: str,
    repository: str,
    route: str,
    timestamp: str,
    nonce: str,
) -> bytes:
    """Return exact UTF-8 newline-separated v1 signing bytes, no final newline."""
    fields = (
        "slaif-local-coding-identity-v1",
        method,
        path,
        hashlib.sha256(raw_query).hexdigest(),
        hashlib.sha256(body).hexdigest(),
        principal,
        session,
        repository,
        route,
        timestamp,
        nonce,
    )
    return "\n".join(fields).encode("utf-8")


def expected_signature(*, secret: bytes, canonical: bytes) -> str:
    """Return the fixed v1 HMAC header value."""
    return "v1=" + hmac.new(secret, canonical, hashlib.sha256).hexdigest()


def _raw_path(request: Request) -> str:
    path = request.scope.get("path")
    if not isinstance(path, str) or path not in SUPPORTED_SIGNED_PATHS:
        raise SignedIdentityError(422, "signed_identity_path_invalid")
    raw_path = request.scope.get("raw_path")
    if raw_path is not None:
        if not isinstance(raw_path, bytes) or raw_path != path.encode("ascii"):
            raise SignedIdentityError(422, "signed_identity_path_invalid")
    return path


def verify_signed_identity(
    request: Request,
    body: bytes,
    config: GatewayIngressConfig,
    replay: ReplayProtector,
    *,
    now: float | None = None,
) -> RequestIdentity:
    """Verify all signed facts and reserve the nonce digest exactly once."""
    if not config.signed:
        raise ValueError("signed identity verification requires signed mode")
    if request.method not in SUPPORTED_SIGNED_METHODS:
        raise SignedIdentityError(422, "signed_identity_method_invalid")
    path = _raw_path(request)
    _reject_extra_signed_headers(request)
    version = _one_header(request, "x-slaif-identity-version")
    principal = _validate_opaque(_one_header(request, "x-slaif-principal"))
    session = _validate_opaque(_one_header(request, "x-slaif-session"))
    repository = _validate_opaque(_one_header(request, "x-slaif-repository"))
    route = _validate_opaque(_one_header(request, "x-slaif-route"))
    timestamp = _one_header(request, "x-slaif-timestamp")
    nonce = _one_header(request, "x-slaif-nonce")
    signature = _one_header(request, "x-slaif-signature")

    if version != config.identity_version:
        raise SignedIdentityError(422, "signed_identity_version_invalid")
    if not _TIMESTAMP_RE.fullmatch(timestamp):
        raise SignedIdentityError(422, "signed_identity_timestamp_invalid")
    timestamp_value = int(timestamp)
    if not config.nonce_min_length <= len(nonce) <= config.nonce_max_length:
        raise SignedIdentityError(422, "signed_identity_nonce_invalid")
    if not _NONCE_RE.fullmatch(nonce):
        raise SignedIdentityError(422, "signed_identity_nonce_invalid")
    if not _SIGNATURE_RE.fullmatch(signature):
        raise SignedIdentityError(422, "signed_identity_signature_invalid")
    if not math.isfinite(now if now is not None else time.time()):
        raise SignedIdentityError(503, "signed_identity_clock_unavailable")
    current_time = now if now is not None else time.time()
    if abs(current_time - timestamp_value) > config.clock_skew_seconds:
        raise SignedIdentityError(403, "signed_identity_timestamp_out_of_window")
    try:
        secret = config.signing_secret()
    except ValueError as exc:
        raise SignedIdentityError(503, "signed_identity_secret_unavailable") from exc

    canonical = canonical_identity_bytes(
        method=request.method,
        path=path,
        raw_query=request.scope.get("query_string", b""),
        body=body,
        principal=principal,
        session=session,
        repository=repository,
        route=route,
        timestamp=timestamp,
        nonce=nonce,
    )
    expected = expected_signature(secret=secret, canonical=canonical)
    if not hmac.compare_digest(signature, expected):
        raise SignedIdentityError(403, "signed_identity_signature_mismatch")
    nonce_digest = hashlib.sha256(nonce.encode("ascii")).hexdigest()
    if not replay.reserve(nonce_digest, now=current_time):
        raise SignedIdentityError(409, "signed_identity_replayed")
    return RequestIdentity(
        principal=principal,
        session=session,
        repository=repository,
        route=route,
    )
