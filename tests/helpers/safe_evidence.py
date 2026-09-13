"""Fail-closed safe-evidence machinery for durable OAP acceptance evidence.

Objective 008 requires that sanitized acceptance results stop being
authoritative only in disposable temporary storage.  This module is the
repository-owned export path.  It is stdlib-only, performs zero network,
provider, model, service, credential, or Git operations, and is deliberately
content-free: every failure carries exactly one fixed rejection class and a
schema path (a location in the closed schema, never candidate content).

Guarantees implemented here:

* bounded reads (and a stat-only preflight variant) of one exact source
  path, opened through a directory-fd walk with ``O_NOFOLLOW`` on every
  component so no symlink in the lexical parent chain can redirect the read;
  the final node must be a regular file, owned by the current user,
  single-link, mode ``0600``, within the explicit size bound; every opened
  descriptor is tracked and closed exactly once;
* strict JSONL decoding: at most two non-empty lines, the last of which is
  the result document; duplicate-key and non-finite rejection matching the
  acceptance runner's ``_decode_fake_gate`` semantics; a pre-existing second
  line must itself validate against the role's closed preflight spec;
* recursive validation against explicit closed schema objects defined by
  :mod:`tests.helpers.safe_evidence_contracts`; open structures are guarded
  in addition by a closed key-class deny policy so raw-content, credential,
  signature, nonce, and private-identifier fields are rejected at every
  nesting level, never stripped;
* a privacy byte scan using fixed pattern classes only;
* destination resolution and writes confined to the repository
  ``oap/evidence`` root: the repository root itself is the trusted anchor,
  opened exactly once as that exact final directory with
  ``O_DIRECTORY | O_NOFOLLOW`` — a symlinked root is refused, never
  followed, and no parent component of the repository root is inspected,
  opened, or required to be readable, so the anchor works on hosts where
  the repository sits below execute-only mount points; below the anchor
  only the repository-owned ``oap/evidence`` components and their
  descendants are no-follow/openat-walked, every component must be a
  current-user-owned directory without group/other write bits, missing
  intermediate directories are created ``0700`` only at positions strictly
  below the existing evidence root (position-scoped, never
  name-membership-based), and the destination file must not exist yet;
* atomic same-directory writes re-walk the entire ``oap/evidence`` chain
  and every created descendant at write time (no process-wide ``fchdir``,
  no path re-traversal outside the anchor): an exclusive reservation of the
  final name, a restrictive ``0600`` temporary file created through the
  same directory descriptor, ``fsync``, ``os.replace`` with both names
  resolved inside that directory via ``src_dir_fd``/``dst_dir_fd``,
  directory ``fsync``, and a post-rename re-open plus full byte read-back
  with SHA-256 comparison against the accepted payload; an existing
  destination is never touched (the exclusive reservation fails first),
  any failure removes only this invocation's temporary file, reservation,
  or unverified final file, leaving no apparently complete result;
* every opened descriptor — anchor, walk components, reservation,
  temporary file, verification re-open — is closed exactly once, on every
  path including failures;
* closed export contract: only the exact role, schema, mode, and role
  result/preflight specs defined by
  :mod:`tests.helpers.safe_evidence_contracts` are accepted, and the
  returned provenance record carries both the original (accepted source
  bytes) and committed (written bytes) SHA-256.
"""

from __future__ import annotations

import errno
import hashlib
import itertools
import json
import math
import os
import re
import stat
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, NoReturn

__all__ = [
    "EVIDENCE_ROOT",
    "MAX_DESTINATION_COMPONENTS",
    "MAX_SAFE_EVIDENCE_BYTES",
    "ProvenanceRecord",
    "Spec",
    "BoolSpec",
    "DictSpec",
    "FloatSpec",
    "IntSpec",
    "ListSpec",
    "NullSpec",
    "PositionalListSpec",
    "OpenDictSpec",
    "OpenValueSpec",
    "StrSpec",
    "UnionSpec",
    "UNSAFE_OPEN_KEY_TOKENS",
    "UnsafeEvidenceError",
    "accept_evidence_bytes",
    "atomic_write_bounded",
    "dict_spec",
    "export_safe_result",
    "privacy_scan",
    "read_existing_evidence_destination_bounded",
    "remove_verified_evidence_destination",
    "resolve_evidence_destination",
    "safe_read_bounded",
    "safe_stat_bounded",
    "strict_decode_result_lines",
    "validate_value",
    "verify_existing_evidence_destination",
]

#: Explicit bounded size covering the known Objective-005 sanitized results
#: (largest known artifact: 685,832 bytes) with headroom for the runner's
#: own evidence projection growth.
MAX_SAFE_EVIDENCE_BYTES: Final[int] = 1 * 1024 * 1024

#: The only repository sub-root that may receive durable evidence.
EVIDENCE_ROOT: Final[str] = "oap/evidence"

MAX_DESTINATION_COMPONENTS: Final[int] = 6

_DESTINATION_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")

#: Monotonic suffix for anchored temporary-file reservations.
_TEMP_COUNTER: Final[itertools.count[int]] = itertools.count(1)

#: Fixed safe character set for open scalar strings and open dictionary
#: keys: printable fact tokens only.  Control characters, non-ASCII text,
#: quoting, and other payload material are rejected, never rewritten.
_OPEN_VALUE_SAFE_CHARS: Final[frozenset[int]] = frozenset(
    set(range(ord("a"), ord("z") + 1))
    | set(range(ord("A"), ord("Z") + 1))
    | set(range(ord("0"), ord("9") + 1))
    | {ord(character) for character in "._:@/+-"}
)

#: Closed deny policy for dictionary keys inside open evidence structures.
#:
#: A key matching any token (case-insensitively) indicates a raw-content,
#: credential, signature/nonce, or historically-private-identifier field.
#: Open facts may only carry fixed-class counters/flags/vocabulary tokens,
#: so such keys are rejected with one fixed class, never stripped or
#: rewritten.  The check applies at every nesting level of open values and
#: to every key of open dictionaries.  Tokens are conservative: they target
#: content-bearing names (``prompt``, ``raw``, ``model output``-style names,
#: ``tool_output``/``tool_result``), credential/identity material
#: (``secret``, ``api_key``, ``authorization``, ``bearer``, ``session``),
#: signature/nonce material (``signature``, ``hmac``, ``nonce``), and
#: historically private identifiers (``request_id``, ``call_id``,
#: ``item_id``, ``run_id``).  Closed explicit specs are the only place raw-
#: free fact names may be extended; they are exempt from this policy.
UNSAFE_OPEN_KEY_TOKENS: Final[frozenset[str]] = frozenset(
    {
        # raw prompt / request / response / model / tool content classes
        "prompt",
        "query",
        "message",
        "transcript",
        "body",
        "raw",
        "payload",
        "output",
        "response",
        "request",
        "image",
        "source",
        "source_code",
        "text",
        "content",
        "history",
        "chat",
        "token",
        "env",
        "dump",
        # credential / identity material
        "secret",
        "credential",
        "apikey",
        "api_key",
        "auth",
        "bearer",
        "cookie",
        "session",
        "private",
        "url",
        "uri",
        "file",
        "path",
        # signature / hmac / nonce material
        "signature",
        "sig",
        "hmac",
        "nonce",
        # historically private request / call / item identifiers
        "request_id",
        "call_id",
        "item_id",
        "response_id",
        "run_id",
        "session_id",
        "key_id",
    }
)


class UnsafeEvidenceError(Exception):
    """Fail-closed rejection.

    ``rejection_class`` is a fixed class name and ``path`` is a schema
    location.  Neither carries candidate content, so the error is safe to
    log, print, or record in a manifest.
    """

    def __init__(self, rejection_class: str, path: str = "<root>") -> None:
        super().__init__(f"{rejection_class} at {path}")
        self.rejection_class = rejection_class
        self.path = path


def _reject(rejection_class: str, path: str = "<root>") -> NoReturn:
    raise UnsafeEvidenceError(rejection_class, path)


def _check_open_key(key: str, path: str) -> None:
    """Apply the closed key-class deny policy to one open-structure key."""
    lowered = key.lower()
    if any(token in lowered for token in UNSAFE_OPEN_KEY_TOKENS):
        _reject("open_key_class_denied", path)


# --------------------------------------------------------------------------
# Closed schema objects
# --------------------------------------------------------------------------


class Spec:
    """Base class for one node of an explicit closed schema."""

    __slots__ = ()


@dataclass(frozen=True)
class BoolSpec(Spec):
    """Boolean node, optionally pinned to one exact value.

    ``value=None`` accepts either boolean; a pinned value closes the node
    to exactly that value (for example the runner's invariant
    ``full_manifest_executed: false`` or the manifest's
    ``preserved_during_objective_005: false``).
    """

    value: bool | None = None


@dataclass(frozen=True)
class NullSpec(Spec):
    __slots__ = ()


@dataclass(frozen=True)
class IntSpec(Spec):
    minimum: int = 0
    maximum: int = 1_000_000


@dataclass(frozen=True)
class FloatSpec(Spec):
    """Finite JSON number with optional closed bounds."""

    minimum: float | None = None
    maximum: float | None = None


@dataclass(frozen=True)
class StrSpec(Spec):
    """Either a closed vocabulary or a fixed identifier pattern."""

    vocabulary: frozenset[str] = frozenset()
    pattern: str | None = None

    def __post_init__(self) -> None:
        if (self.vocabulary == frozenset()) == (self.pattern is None):
            raise ValueError("string_spec_requires_exactly_one_source")


@dataclass(frozen=True)
class DictSpec(Spec):
    required: tuple[tuple[str, Spec], ...]
    optional: tuple[tuple[str, Spec], ...] = ()


@dataclass(frozen=True)
class ListSpec(Spec):
    element: Spec
    maximum_length: int


@dataclass(frozen=True)
class PositionalListSpec(Spec):
    """A list with exactly ``len(positions)`` elements.

    The ``i``-th element must validate against ``positions[i]``.  Used only
    where the producer emits a fixed-length, fixed-order sequence of
    distinct entries (for example the four closed manifest authority roles
    or the ten fixed offline-replay preparation cases).
    """

    positions: tuple[Spec, ...]


@dataclass(frozen=True)
class UnionSpec(Spec):
    alternatives: tuple[Spec, ...]


@dataclass(frozen=True)
class OpenDictSpec(Spec):
    """Bounded open dict with a closed key pattern and closed value schema.

    Used only where the source defines a key-open but type-closed structure
    (for example accumulator lifetime tables).  Keys are pattern-checked,
    checked against the closed key-class deny policy, length-checked, and
    bounded in count; every value must validate against the closed
    ``value`` schema.
    """

    key_pattern: str
    value: Spec
    maximum_keys: int
    maximum_key_length: int = 64


@dataclass(frozen=True)
class OpenValueSpec(Spec):
    """Bounded recursive open structure for checkpoint fact values.

    Mirrors the runner's ``_safe_checkpoint_value`` closure: bounded depth,
    integer range, string/key length, and container cardinality, plus the
    closed key-class deny policy on every dictionary key at every nesting
    level.  This is the only open value structure in the safe-evidence
    machinery and it is used only where the source itself defines such a
    bounded closure.
    """

    maximum_depth: int = 4
    maximum_string_length: int = 128
    maximum_key_length: int = 64
    maximum_dict_keys: int = 64
    maximum_list_items: int = 64
    maximum_int: int = 1_000_000


def dict_spec(
    required: Sequence[tuple[str, Spec]],
    optional: Sequence[tuple[str, Spec]] = (),
) -> DictSpec:
    names = [name for name, _ in required]
    if len(names) != len(set(names)):
        raise ValueError("duplicate_required_key")
    for name, _ in optional:
        if name in names:
            raise ValueError("duplicate_optional_key")
    return DictSpec(tuple(required), tuple(optional))


def _validate_open(spec: OpenValueSpec, value: Any, path: str, depth: int) -> None:
    if depth > spec.maximum_depth:
        _reject("open_depth", path)
    if value is None or isinstance(value, bool):
        return
    if type(value) is int:
        if not 0 <= value <= spec.maximum_int:
            _reject("open_int_range", path)
        return
    if type(value) is float:
        if not math.isfinite(value) or not 0 <= value <= spec.maximum_int:
            _reject("open_float_range", path)
        return
    if isinstance(value, str):
        if len(value) > spec.maximum_string_length:
            _reject("open_string_length", path)
        if not all(ord(character) in _OPEN_VALUE_SAFE_CHARS for character in value):
            _reject("open_string_grammar", path)
        return
    if isinstance(value, list):
        if len(value) > spec.maximum_list_items:
            _reject("open_list_length", path)
        for index, item in enumerate(value):
            _validate_open(spec, item, f"{path}[{index}]", depth + 1)
        return
    if isinstance(value, Mapping):
        if len(value) > spec.maximum_dict_keys:
            _reject("open_dict_keys", path)
        for key, item in value.items():
            if (
                not isinstance(key, str)
                or len(key) > spec.maximum_key_length
                or not all(ord(character) in _OPEN_VALUE_SAFE_CHARS for character in key)
            ):
                _reject("open_dict_key", path)
            _check_open_key(key, path)
            _validate_open(spec, item, f"{path}.{key}", depth + 1)
        return
    _reject("open_type", path)


def validate_value(spec: Spec, value: Any, path: str = "<root>") -> None:
    """Validate one value against one closed schema node, failing closed."""
    if isinstance(spec, BoolSpec):
        if type(value) is not bool:
            _reject("shape_type", path)
        if spec.value is not None and value is not spec.value:
            _reject("shape_bool_value", path)
    elif isinstance(spec, NullSpec):
        if value is not None:
            _reject("shape_type", path)
    elif isinstance(spec, IntSpec):
        if type(value) is not int or not spec.minimum <= value <= spec.maximum:
            _reject("shape_int_range" if type(value) is int else "shape_type", path)
    elif isinstance(spec, FloatSpec):
        if type(value) is not float:
            _reject("shape_type", path)
        if not math.isfinite(value):
            _reject("shape_float_finite", path)
        if spec.minimum is not None and value < spec.minimum:
            _reject("shape_float_range", path)
        if spec.maximum is not None and value > spec.maximum:
            _reject("shape_float_range", path)
    elif isinstance(spec, StrSpec):
        if not isinstance(value, str):
            _reject("shape_type", path)
        if spec.vocabulary and value not in spec.vocabulary:
            _reject("shape_string_value", path)
        if spec.pattern is not None and re.fullmatch(spec.pattern, value) is None:
            _reject("shape_string_value", path)
    elif isinstance(spec, DictSpec):
        if not isinstance(value, Mapping):
            _reject("shape_type", path)
        known = {name for name, _ in spec.required} | {name for name, _ in spec.optional}
        if any(name not in known for name in value):
            _reject("shape_key_unknown", path)
        for name, _ in spec.required:
            if name not in value:
                _reject("shape_key_missing", f"{path}.{name}")
        for name, child in list(spec.required) + list(spec.optional):
            if name in value:
                validate_value(child, value[name], f"{path}.{name}")
    elif isinstance(spec, ListSpec):
        if not isinstance(value, list):
            _reject("shape_type", path)
        if len(value) > spec.maximum_length:
            _reject("shape_list_length", path)
        for index, item in enumerate(value):
            validate_value(spec.element, item, f"{path}[{index}]")
    elif isinstance(spec, PositionalListSpec):
        if not isinstance(value, list):
            _reject("shape_type", path)
        if len(value) != len(spec.positions):
            _reject("shape_list_length", path)
        for index, (position, item) in enumerate(zip(spec.positions, value, strict=True)):
            validate_value(position, item, f"{path}[{index}]")
    elif isinstance(spec, UnionSpec):
        for alternative in spec.alternatives:
            try:
                validate_value(alternative, value, path)
                return
            except UnsafeEvidenceError:
                continue
        _reject("shape_union", path)
    elif isinstance(spec, OpenDictSpec):
        if not isinstance(value, Mapping):
            _reject("shape_type", path)
        if len(value) > spec.maximum_keys:
            _reject("open_dict_keys", path)
        for key, item in value.items():
            if (
                not isinstance(key, str)
                or len(key) > spec.maximum_key_length
                or re.fullmatch(spec.key_pattern, key) is None
            ):
                _reject("open_dict_key", path)
            _check_open_key(key, path)
            validate_value(spec.value, item, f"{path}.{key}")
    elif isinstance(spec, OpenValueSpec):
        _validate_open(spec, value, path, 0)
    else:  # pragma: no cover - the module constructs only known specs
        _reject("shape_unsupported_spec", path)


# --------------------------------------------------------------------------
# Bounded source read
# --------------------------------------------------------------------------


def _open_source_final(path: Path, max_bytes: int) -> int:
    """Walk one exact path with symlink-proof directory-fd walking.

    Every lexical component is opened with ``O_NOFOLLOW`` through the
    parent directory descriptor, so a symlink anywhere in the chain is
    refused instead of followed.  The final node must be a regular file,
    owned by the current user, single-link, mode ``0600``, and no larger
    than ``max_bytes``.  Every descriptor opened along the walk is closed
    exactly once by this function, on every path including failures.  The
    returned final-node descriptor is owned by the caller and must be
    closed exactly once.  All failures map to fixed rejection classes.
    """
    if not path.is_absolute():
        _reject("unsafe_path_relative")
    parts = tuple(part for part in path.parts if part not in ("", "/"))
    if not parts or any(part in (".", "..") for part in parts):
        _reject("unsafe_path_lexical")
    open_fds: list[int] = []
    try:
        root_fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        open_fds.append(root_fd)
        dir_fd = root_fd
        for index, part in enumerate(parts):
            is_last = index == len(parts) - 1
            try:
                node_st = os.lstat(part, dir_fd=dir_fd)
            except FileNotFoundError:
                _reject("unsafe_path_missing")
            except OSError:
                _reject("unsafe_path_unreadable")
            if stat.S_ISLNK(node_st.st_mode):
                _reject("unsafe_path_symlink")
            flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
            if not is_last:
                flags |= os.O_DIRECTORY
            try:
                child = os.open(part, flags, dir_fd=dir_fd)
            except FileNotFoundError:
                _reject("unsafe_path_missing")
            except OSError:
                _reject("unsafe_path_unreadable")
            open_fds.append(child)
            st = os.fstat(child)
            if is_last:
                if not stat.S_ISREG(st.st_mode):
                    _reject("unsafe_path_not_regular")
                if st.st_uid != os.getuid():
                    _reject("unsafe_path_foreign_owner")
                if st.st_nlink != 1:
                    _reject("unsafe_path_nlink")
                if st.st_mode & 0o777 != 0o600:
                    _reject("unsafe_path_mode")
                if st.st_size > max_bytes:
                    _reject("unsafe_path_size")
                open_fds.remove(child)
                return child
            if not stat.S_ISDIR(st.st_mode):
                _reject("unsafe_path_component_type")
            os.close(dir_fd)
            open_fds.remove(dir_fd)
            dir_fd = child
        _reject("unsafe_path_lexical")
    except UnsafeEvidenceError:
        raise
    except OSError:
        _reject("unsafe_path_unreadable")
    finally:
        for fd in open_fds:
            try:
                os.close(fd)
            except OSError:
                pass


def safe_read_bounded(path: Path, max_bytes: int = MAX_SAFE_EVIDENCE_BYTES) -> bytes:
    """Read one exact path with symlink-proof directory-fd walking.

    Delegates the shared lexical, symlink, ownership, mode, nlink, and
    size invariants to :func:`_open_source_final`, then reads the complete
    bounded payload.  Every opened descriptor is closed exactly once, on
    every path including failures.  All failures map to fixed rejection
    classes.
    """
    final_fd = _open_source_final(path, max_bytes)
    chunks: list[bytes] = []
    total = 0
    try:
        while True:
            chunk = os.read(final_fd, 65536)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                _reject("unsafe_path_size")
            chunks.append(chunk)
    except OSError:
        _reject("unsafe_path_unreadable")
    finally:
        _close_once(final_fd)
    return b"".join(chunks)


def safe_stat_bounded(path: Path, max_bytes: int = MAX_SAFE_EVIDENCE_BYTES) -> None:
    """Bounded stat-only preflight of one exact path.

    Enforces exactly the lexical, symlink, ownership, nlink, mode, and
    size invariants of :func:`safe_read_bounded` without reading any
    content: the final node is opened and immediately closed.  Used for
    historical authorities whose presence is recorded but whose content is
    never retained, so their availability can be classified truthfully
    without producing content, size, or hash facts.  Every opened
    descriptor is closed exactly once.
    """
    final_fd = _open_source_final(path, max_bytes)
    _close_once(final_fd)


# --------------------------------------------------------------------------
# Strict decoding
# --------------------------------------------------------------------------


def _strict_json_object(line: bytes, where: str) -> dict[str, Any]:
    def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                _reject("decode_duplicate_key", where)
            result[key] = value
        return result

    def reject_constant(_value: str) -> NoReturn:
        _reject("decode_non_finite", where)

    try:
        payload = json.loads(
            line,
            object_pairs_hook=reject_duplicate_pairs,
            parse_constant=reject_constant,
        )
    except UnsafeEvidenceError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        _reject("decode_invalid_json", where)
    if not isinstance(payload, dict):
        _reject("decode_not_object", where)
    return payload


def strict_decode_result_lines(raw: bytes) -> tuple[dict[str, Any], bytes | None]:
    """Decode the final non-empty line as the result document.

    The accepted result files are JSONL with at most two non-empty lines:
    the final result document and, when present, exactly one preceding
    ``PREFLIGHT`` line.  Three or more non-empty lines are rejected rather
    than silently dropped.  Returns the result document and, when a
    preceding line exists, its raw bytes; callers must provide a closed
    preflight spec for such files.
    """
    lines = [line for line in raw.splitlines() if line.strip()]
    if not lines:
        _reject("decode_empty")
    if len(lines) > 2:
        _reject("decode_extra_lines")
    result = _strict_json_object(lines[-1], "result")
    preflight_line = lines[0] if len(lines) == 2 else None
    return result, preflight_line


# --------------------------------------------------------------------------
# Privacy scan (fixed pattern classes only)
# --------------------------------------------------------------------------

#: Fixed rejection classes emitted by :func:`privacy_scan`.
PRIVACY_REJECTION_CLASSES: Final[tuple[str, ...]] = (
    "privacy_pattern_bearer",
    "privacy_pattern_authorization",
    "privacy_pattern_api_key_prefix",
    "privacy_pattern_secret_field",
    "privacy_pattern_data_url",
    "privacy_pattern_private_url",
    "privacy_pattern_private_ip",
    "privacy_pattern_long_base64",
    "privacy_pattern_env_dump",
    "privacy_pattern_signature_nonce",
)

_PRIVACY_PATTERNS: Final[tuple[tuple[str, re.Pattern[bytes]], ...]] = (
    (
        "privacy_pattern_bearer",
        re.compile(rb"bearer\s+[a-z0-9._~+/=-]{8,}", re.IGNORECASE),
    ),
    (
        "privacy_pattern_authorization",
        re.compile(rb"authorization[\"']?\s*[:=]\s*[\"']?[a-z0-9._~+/=-]{8,}", re.IGNORECASE),
    ),
    ("privacy_pattern_api_key_prefix", re.compile(rb"sk-[a-z0-9_-]{16,}", re.IGNORECASE)),
    (
        "privacy_pattern_secret_field",
        re.compile(
            rb"""["'](authorization|api[_-]?key|gateway[_-]?key|service[_-]?token|"""
            rb"""signing[_-]?secret|derivation[_-]?secret|encryption[_-]?key|"""
            rb"""hmac[_-]?secret|client[_-]?secret|private[_-]?key|qwen[_-]?key)"""
            rb"""["']\s*:\s*["'][^"']{8,}""",
            re.IGNORECASE,
        ),
    ),
    (
        "privacy_pattern_data_url",
        re.compile(rb"data:[a-z0-9.+/=-]{1,64};base64,", re.IGNORECASE),
    ),
    (
        "privacy_pattern_private_url",
        re.compile(
            rb"(?:https?|ftp)://(?!127\.0\.0\.1\b|localhost\b)[a-z0-9]"
            rb"(?:[a-z0-9.-]*[a-z0-9])?",
            re.IGNORECASE,
        ),
    ),
    (
        "privacy_pattern_private_ip",
        re.compile(
            rb"\b(?:10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
            rb"|192\.168\.[0-9]{1,3}\.[0-9]{1,3}"
            rb"|172\.(?:1[6-9]|2[0-9]|3[01])\.[0-9]{1,3}\.[0-9]{1,3})\b"
        ),
    ),
    ("privacy_pattern_long_base64", re.compile(rb"[a-z0-9+/]{300,}={0,2}", re.IGNORECASE)),
    (
        "privacy_pattern_env_dump",
        re.compile(rb"^[A-Z][A-Z0-9_]{9,}=[^\s,;}]{8,}$", re.MULTILINE),
    ),
    (
        "privacy_pattern_signature_nonce",
        re.compile(
            rb"""["'](signature|nonce|hmac)["']\s*:\s*["']?[a-z0-9+/=_-]{16,}""",
            re.IGNORECASE,
        ),
    ),
)


def privacy_scan(raw: bytes) -> str | None:
    """Scan raw bytes with the fixed pattern classes; return the first hit."""
    for rejection_class, pattern in _PRIVACY_PATTERNS:
        if pattern.search(raw) is not None:
            return rejection_class
    return None


# --------------------------------------------------------------------------
# Acceptance pipeline
# --------------------------------------------------------------------------


def accept_evidence_bytes(
    raw: bytes,
    result_spec: Spec,
    *,
    preflight_spec: Spec | None = None,
    max_bytes: int = MAX_SAFE_EVIDENCE_BYTES,
) -> tuple[dict[str, Any], str]:
    """Validate complete evidence bytes; return the document and SHA-256.

    The SHA-256 is computed only after the complete artifact has been
    accepted, per the order.  Raises :class:`UnsafeEvidenceError` with a
    fixed class on any violation.
    """
    if len(raw) > max_bytes:
        _reject("evidence_size_exceeded")
    result, preflight_line = strict_decode_result_lines(raw)
    if preflight_line is not None:
        if preflight_spec is None:
            _reject("decode_unvalidated_preflight_line")
        validate_value(
            preflight_spec, _strict_json_object(preflight_line, "preflight"), "preflight"
        )
    privacy_hit = privacy_scan(raw)
    if privacy_hit is not None:
        _reject(privacy_hit)
    validate_value(result_spec, result)
    return result, hashlib.sha256(raw).hexdigest()


# --------------------------------------------------------------------------
# Anchored destination walks (repository root as trusted anchor)
# --------------------------------------------------------------------------


def _close_once(fd: int) -> None:
    """Close one descriptor; close errors must not replace rejections.

    Every caller tracks its own exactly-once accounting: each descriptor
    that is opened is handed to exactly one closer.  Swallowing
    ``OSError`` keeps teardown paths from masking the original failure.
    """
    try:
        os.close(fd)
    except OSError:
        pass


def _close_each(open_fds: list[int]) -> None:
    """Close a private descriptor list; each descriptor is closed once."""
    for fd in open_fds:
        _close_once(fd)


def _open_repo_anchor(repo_root: Path) -> int:
    """Open the exact repository root directory as the trusted anchor.

    Only the final component (the repository root itself) is opened, with
    ``O_DIRECTORY | O_NOFOLLOW``: a symlinked root is refused, never
    followed, and no parent component of the repository root is
    inspected, opened, or required to be readable.  This keeps the
    destination path working on hosts where the repository sits below
    execute-only mount points (for example NFS home directories), while
    every component below the anchor remains fully validated.
    """
    try:
        return os.open(
            str(repo_root),
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
        )
    except FileNotFoundError:
        _reject("destination_root_missing")
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            _reject("destination_component_symlink")
        _reject("destination_unreadable")


def _walk_evidence_tail(
    anchor_fd: int,
    tail: tuple[str, ...],
    *,
    creatable_from: int,
) -> tuple[int, list[int]]:
    """Open every directory component of ``tail`` below an open anchor.

    Each component is ``lstat``/``open``-ed relative to its parent
    directory descriptor with ``O_NOFOLLOW``, so a symlink at any
    component is refused instead of followed.  Existing components must
    be directories owned by the current user without group/other write
    bits.  A missing component is created (mode ``0700``) only at
    positions ``>= creatable_from`` — position-scoped below the existing
    evidence root, never name-membership-based — and is re-opened and
    re-validated after creation.

    Returns ``(final_dir_fd, opened_fds)`` where ``opened_fds`` lists
    every descriptor the walk opened, including ``final_dir_fd``.  The
    caller must close each descriptor in ``opened_fds`` exactly once.
    On any failure the walk closes every descriptor it opened itself and
    raises.
    """
    if not tail or any(part in ("", ".", "..") for part in tail):
        _reject("destination_traversal")
    if creatable_from < 0:
        _reject("destination_traversal")
    dir_fd = anchor_fd
    owned: list[int] = []
    try:
        for index, part in enumerate(tail):
            creatable = index >= creatable_from
            try:
                node_st = os.lstat(part, dir_fd=dir_fd)
            except FileNotFoundError:
                node_st = None
            except OSError:
                _reject("destination_unreadable")
            if node_st is not None:
                if stat.S_ISLNK(node_st.st_mode):
                    _reject("destination_component_symlink")
                if not stat.S_ISDIR(node_st.st_mode):
                    _reject("destination_component_type")
                if node_st.st_uid != os.getuid():
                    _reject("destination_component_owner")
                if node_st.st_mode & 0o022:
                    _reject("destination_component_writable")
            elif not creatable:
                _reject("destination_root_missing" if index < 2 else "destination_missing")
            try:
                child = os.open(
                    part,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                    dir_fd=dir_fd,
                )
            except FileNotFoundError:
                # Concurrent removal between lstat and open: only a
                # position-creatable component may be (re)created here.
                if not creatable:
                    _reject("destination_root_missing" if index < 2 else "destination_missing")
                try:
                    os.mkdir(part, 0o700, dir_fd=dir_fd)
                except FileExistsError:
                    pass  # concurrent creation; re-open and re-validate below
                except OSError:
                    _reject("destination_unreadable")
                try:
                    child = os.open(
                        part,
                        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                        dir_fd=dir_fd,
                    )
                except OSError as exc:
                    if exc.errno == errno.ELOOP:
                        _reject("destination_component_symlink")
                    _reject("destination_unreadable")
            except OSError as exc:
                if exc.errno == errno.ELOOP:
                    _reject("destination_component_symlink")
                _reject("destination_unreadable")
            owned.append(child)
            st = os.fstat(child)
            if not stat.S_ISDIR(st.st_mode):
                _reject("destination_component_type")
            if st.st_uid != os.getuid():
                _reject("destination_component_owner")
            if st.st_mode & 0o022:
                _reject("destination_component_writable")
            dir_fd = child
        # Success: the caller owns every descriptor in ``owned`` (which
        # includes the final directory descriptor) and closes each once.
        return dir_fd, owned
    except BaseException:
        _close_each(owned)
        raise


# --------------------------------------------------------------------------
# Destination resolution and atomic write (bound to the repository root)
# --------------------------------------------------------------------------


def _validate_destination_relative(relative: str) -> tuple[str, ...]:
    """Lexical checks for one relative destination; closed component set."""
    if not relative:
        _reject("destination_empty")
    if relative.startswith("/"):
        _reject("destination_absolute")
    parts = tuple(relative.split("/"))
    if any(part in ("", ".", "..") for part in parts):
        _reject("destination_traversal")
    if len(parts) > MAX_DESTINATION_COMPONENTS:
        _reject("destination_component_count")
    if any(_DESTINATION_NAME.fullmatch(part) is None for part in parts):
        _reject("destination_component_name")
    return parts


def resolve_evidence_destination(repo_root: Path, relative: str) -> Path:
    """Resolve one relative destination inside ``oap/evidence``.

    The destination must be a relative path of plain identifier components
    (no leading slash, no empty/``.``/``..`` components).  The repository
    root is opened once as the trusted anchor (exact final directory,
    ``O_DIRECTORY | O_NOFOLLOW``; no parent component is inspected), and
    only the repository-owned ``oap/evidence`` components and their
    descendants are walked below it with ``O_NOFOLLOW`` through parent
    directory descriptors: every component must be a directory owned by
    the current user without group/other write bits, and a symlink
    component is refused, never followed.  Missing intermediate
    directories strictly below the existing ``oap/evidence`` root are
    created ``0700`` (position-scoped).  The final name is probed with
    ``lstat`` through the directory descriptor: a symlink or any existing
    final name is refused rather than overwritten.  Every descriptor is
    closed exactly once.
    """
    parts = _validate_destination_relative(relative)
    anchor_fd = _open_repo_anchor(repo_root)
    opened_fds: list[int] = []
    try:
        directory_fd, opened_fds = _walk_evidence_tail(
            anchor_fd,
            ("oap", "evidence", *parts[:-1]),
            creatable_from=2,
        )
        try:
            final_st = os.lstat(parts[-1], dir_fd=directory_fd)
        except FileNotFoundError:
            final_st = None
        except OSError:
            _reject("destination_unreadable")
        if final_st is not None:
            if stat.S_ISLNK(final_st.st_mode):
                _reject("destination_symlink")
            _reject("destination_exists")
    finally:
        _close_each(opened_fds)
        _close_once(anchor_fd)
    return repo_root / EVIDENCE_ROOT / relative


def atomic_write_bounded(repo_root: Path, relative: str, data: bytes) -> None:
    """Atomically write ``data`` to the destination bound to ``repo_root``.

    The write is bound to the exact repository root and one relative
    destination inside ``oap/evidence``; arbitrary absolute paths are not
    accepted.  At write time the anchor is re-opened (exact repository
    root, ``O_DIRECTORY | O_NOFOLLOW``; no parent component is
    inspected) and the entire ``oap/evidence`` chain plus every created
    descendant is re-walked with ``O_NOFOLLOW`` through parent directory
    descriptors.  The final name is reserved exclusively (``O_CREAT |
    O_EXCL | O_NOFOLLOW``, mode ``0600``), the payload goes to a
    restrictive ``0600`` temporary file created through the same
    directory descriptor, fsynced, and renamed over the reservation with
    ``os.replace(src, dst, src_dir_fd=dir, dst_dir_fd=dir)`` so both
    names resolve inside that directory only.  No process-wide
    ``fchdir`` is used.  The directory is fsynced, then the final file is
    re-opened through the directory descriptor with ``O_NOFOLLOW``,
    ``fstat``-checked (regular, current-user-owned, mode ``0600``, exact
    size), and fully read back with its SHA-256 compared against the
    accepted payload.

    A destination that already exists is never touched: the exclusive
    reservation fails first, and the pre-existing file is refused, not
    overwritten.  Any failure (temporary-file creation, write, rename, or
    verification) removes only this invocation's temporary file,
    reservation, or unverified final file, leaving no apparently complete
    result.  Every opened descriptor is closed exactly once.
    """
    parts = _validate_destination_relative(relative)
    final_name = parts[-1]
    anchor_fd = _open_repo_anchor(repo_root)
    opened_fds: list[int] = []
    directory_fd: int | None = None
    reservation_fd: int | None = None
    temp_fd: int | None = None
    check_fd: int | None = None
    temp_name: str | None = None
    verified = False
    try:
        directory_fd, opened_fds = _walk_evidence_tail(
            anchor_fd,
            ("oap", "evidence", *parts[:-1]),
            creatable_from=2,
        )
        try:
            final_st = os.lstat(final_name, dir_fd=directory_fd)
        except FileNotFoundError:
            final_st = None
        except OSError:
            _reject("destination_unreadable")
        if final_st is not None:
            if stat.S_ISLNK(final_st.st_mode):
                _reject("destination_symlink")
            _reject("destination_exists")
        try:
            reservation_fd = os.open(
                final_name,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                0o600,
                dir_fd=directory_fd,
            )
        except FileExistsError:
            _reject("destination_exists")
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                _reject("destination_symlink")
            _reject("destination_reservation_failed")
        for _attempt in range(8):
            candidate = f".{final_name}.{os.getpid()}.{next(_TEMP_COUNTER)}"
            try:
                temp_fd = os.open(
                    candidate,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                    0o600,
                    dir_fd=directory_fd,
                )
                break
            except FileExistsError:
                temp_fd = None
            except OSError:
                _reject("destination_temp_failed")
        if temp_fd is None:
            _reject("destination_temp_failed")
        temp_name = candidate
        view = memoryview(data)
        written = 0
        while written < len(view):
            advanced = os.write(temp_fd, view[written:])
            if advanced <= 0:
                raise OSError(errno.EIO, "bounded write made no progress")
            written += advanced
        os.fsync(temp_fd)
        _close_once(temp_fd)
        temp_fd = None
        try:
            os.replace(temp_name, final_name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        except OSError:
            _reject("write_failed")
        temp_name = None  # renamed over the reservation; no temp name left
        os.fsync(directory_fd)
        try:
            check_fd = os.open(
                final_name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory_fd
            )
        except OSError:
            _reject("write_verification_failed")
        st = os.fstat(check_fd)
        if (
            not stat.S_ISREG(st.st_mode)
            or st.st_uid != os.getuid()
            or (st.st_mode & 0o777) != 0o600
            or st.st_size != len(data)
        ):
            _reject("write_verification_failed")
        # Full byte read-back: the durable bytes at the anchored
        # destination must equal the accepted payload, not merely match
        # its size.
        digest = hashlib.sha256()
        remaining = len(data)
        while remaining > 0:
            chunk = os.read(check_fd, min(65536, remaining))
            if not chunk:
                break
            digest.update(chunk)
            remaining -= len(chunk)
        _close_once(check_fd)
        check_fd = None
        if remaining != 0 or digest.hexdigest() != hashlib.sha256(data).hexdigest():
            _reject("write_verification_failed")
        verified = True
    except UnsafeEvidenceError:
        raise
    except OSError:
        _reject("write_failed")
    finally:
        if not verified:
            if temp_name is not None:
                try:
                    os.unlink(temp_name, dir_fd=directory_fd)
                except OSError:
                    pass
            if reservation_fd is not None:
                # We created the reservation (or renamed over it), so
                # remove the reservation (or the unverified final
                # artifact).  A destination we never reserved is never
                # touched.
                try:
                    os.unlink(final_name, dir_fd=directory_fd)
                except OSError:
                    pass
        if temp_fd is not None:
            _close_once(temp_fd)
        if check_fd is not None:
            _close_once(check_fd)
        if reservation_fd is not None:
            _close_once(reservation_fd)
        if directory_fd is not None:
            _close_each(opened_fds)  # includes directory_fd exactly once
        _close_once(anchor_fd)


def read_existing_evidence_destination_bounded(
    repo_root: Path, relative: str, max_bytes: int = MAX_SAFE_EVIDENCE_BYTES
) -> bytes:
    """Read back one existing evidence destination through the anchored walk.

    Unlike the bounded source reader (which walks from the filesystem
    root), this reader anchors at the repository root, so it works on
    hosts where the repository sits below execute-only mount points
    (for example NFS home directories).  The anchor is the exact
    repository root opened with ``O_DIRECTORY | O_NOFOLLOW``; every
    component below it is re-walked with ``O_NOFOLLOW`` through the
    parent directory descriptor and re-validated.  The final node must
    be a regular file owned by the current user, single-linked, mode
    ``0600``, and at most ``max_bytes``; it is opened with ``O_NOFOLLOW``
    through the directory descriptor and fully read back within the
    bound.  A missing destination or any deviation is refused under a
    fixed class; nothing is created, followed, or overwritten.
    """
    parts = _validate_destination_relative(relative)
    tail = (EVIDENCE_ROOT.split("/", 1)[0], EVIDENCE_ROOT.split("/", 1)[1], *parts[:-1])
    anchor_fd = _open_repo_anchor(repo_root)
    opened_fds: list[int] = []
    check_fd: int | None = None
    try:
        directory_fd, opened_fds = _walk_evidence_tail(anchor_fd, tail, creatable_from=len(tail))
        try:
            final_st = os.lstat(parts[-1], dir_fd=directory_fd)
        except FileNotFoundError:
            _reject("destination_missing", relative)
        except OSError:
            _reject("destination_unreadable", relative)
        if (
            not stat.S_ISREG(final_st.st_mode)
            or final_st.st_uid != os.getuid()
            or final_st.st_nlink != 1
            or (final_st.st_mode & 0o777) != 0o600
            or final_st.st_size > max_bytes
        ):
            _reject("destination_unsafe", relative)
        try:
            check_fd = os.open(
                parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory_fd
            )
        except FileNotFoundError:
            _reject("destination_missing", relative)
        except OSError:
            _reject("destination_unreadable", relative)
        st = os.fstat(check_fd)
        if (
            not stat.S_ISREG(st.st_mode)
            or st.st_uid != os.getuid()
            or (st.st_mode & 0o777) != 0o600
            or st.st_size > max_bytes
        ):
            _reject("destination_unsafe", relative)
        chunks: list[bytes] = []
        total = 0
        try:
            while True:
                chunk = os.read(check_fd, 65536)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    _reject("evidence_size_exceeded", relative)
                chunks.append(chunk)
        except OSError:
            _reject("destination_unreadable", relative)
        return b"".join(chunks)
    finally:
        if check_fd is not None:
            _close_once(check_fd)
        _close_each(opened_fds)
        _close_once(anchor_fd)


def verify_existing_evidence_destination(
    repo_root: Path, relative: str, expected_sha256: str
) -> int:
    """Read back and hash-verify one existing evidence destination.

    The destination is resolved inside the repository ``oap/evidence``
    root and read back through the anchored, symlink-proof, bounded
    reader (final node: regular, current-user-owned, single-linked,
    mode ``0600``, at most one MiB) so verification works even on hosts
    where the repository sits below execute-only mount points.  The
    read-back SHA-256 must equal ``expected_sha256``; any deviation is
    refused under the fixed class ``destination_bytes_mismatch``.
    Returns the verified byte count; raises :class:`UnsafeEvidenceError`
    with the fixed bounded classes on path or property violations.
    """
    raw = read_existing_evidence_destination_bounded(repo_root, relative)
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        _reject("destination_bytes_mismatch", relative)
    return len(raw)


def remove_verified_evidence_destination(repo_root: Path, relative: str) -> None:
    """Remove one evidence destination through the anchored walk.

    Used only by the Objective-008-b one-shot manifest replacement, after
    the caller has verified the exact pinned byte identity.  The walk is
    the same anchored, ``O_NOFOLLOW`` directory-descriptor discipline as
    the writer: every component re-validated, nothing is created, and the
    final node is re-checked through the directory descriptor immediately
    before ``unlinkat`` (regular, current-user-owned, single-linked, mode
    ``0600``); any deviation is refused under the fixed class
    ``destination_unsafe``, never followed or overwritten.
    """
    parts = _validate_destination_relative(relative)
    tail = (EVIDENCE_ROOT.split("/", 1)[0], EVIDENCE_ROOT.split("/", 1)[1], *parts[:-1])
    anchor_fd = _open_repo_anchor(repo_root)
    opened_fds: list[int] = []
    try:
        directory_fd, opened_fds = _walk_evidence_tail(anchor_fd, tail, creatable_from=len(tail))
        try:
            final_st = os.lstat(parts[-1], dir_fd=directory_fd)
        except FileNotFoundError:
            _reject("destination_missing", relative)
        except OSError:
            _reject("destination_unreadable", relative)
        if (
            not stat.S_ISREG(final_st.st_mode)
            or final_st.st_uid != os.getuid()
            or final_st.st_nlink != 1
            or (final_st.st_mode & 0o777) != 0o600
        ):
            _reject("destination_unsafe", relative)
        try:
            os.unlink(parts[-1], dir_fd=directory_fd)
        except FileNotFoundError:
            _reject("destination_missing", relative)
        except OSError:
            _reject("destination_unsafe", relative)
    finally:
        _close_each(opened_fds)
        _close_once(anchor_fd)


@dataclass(frozen=True)
class ProvenanceRecord:
    """Bounded machine-readable provenance for one successful export.

    ``original_sha256`` hashes the accepted source bytes and
    ``committed_sha256`` hashes the exact bytes written to the durable
    destination.  In ``exact`` mode the two are equal; in
    ``deterministic`` mode the committed value hashes the re-serialized
    document.  No candidate content, secret, secret hash, or exception
    detail is ever carried.
    """

    role: str
    schema: str
    relative_path: str
    byte_count: int
    original_sha256: str
    committed_sha256: str
    mode: str

    def to_json(self) -> str:
        return json.dumps(
            {
                "role": self.role,
                "schema": self.schema,
                "relative_path": self.relative_path,
                "byte_count": self.byte_count,
                "original_sha256": self.original_sha256,
                "committed_sha256": self.committed_sha256,
                "mode": self.mode,
            },
            sort_keys=True,
            separators=(",", ":"),
        )


def export_safe_result(
    repo_root: Path,
    *,
    role: str,
    schema: str,
    raw: bytes,
    result_spec: Spec,
    preflight_spec: Spec | None,
    relative_path: str,
    mode: str,
) -> ProvenanceRecord:
    """Validate and durably export one sanitized result.

    The role, schema, mode, and the role's closed result/preflight specs
    are all fail-closed: only the exact role schemas defined by
    :mod:`tests.helpers.safe_evidence_contracts` are accepted, so a caller
    cannot export an arbitrary mapping under a borrowed role name.
    ``mode`` is ``"exact"`` (commit the accepted original bytes) or
    ``"deterministic"`` (re-serialize the accepted document with sorted
    keys and compact separators).  Returns a bounded provenance record
    carrying both the original and committed SHA-256; never returns
    candidate content.
    """
    # Imported here (not at module top) to avoid an import cycle: the
    # contracts module imports the spec classes from this module.
    from tests.helpers import safe_evidence_contracts as contracts

    if role not in contracts.ROLES:
        _reject("role_unknown")
    if schema != contracts.ROLE_SCHEMAS[role]:
        _reject("export_schema_mismatch")
    if mode not in {"exact", "deterministic"}:
        _reject("export_mode_unknown")
    if result_spec is not contracts.result_spec_for_role(role):
        _reject("export_spec_mismatch")
    if preflight_spec is not contracts.preflight_spec_for_role(role):
        _reject("export_preflight_mismatch")
    document, original_sha = accept_evidence_bytes(raw, result_spec, preflight_spec=preflight_spec)
    payload: bytes
    committed_sha: str
    if mode == "exact":
        payload = raw
        committed_sha = original_sha
    else:
        payload = (json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n").encode(
            "utf-8"
        )
        committed_sha = hashlib.sha256(payload).hexdigest()
    atomic_write_bounded(repo_root, relative_path, payload)
    return ProvenanceRecord(
        role=role,
        schema=schema,
        relative_path=relative_path,
        byte_count=len(payload),
        original_sha256=original_sha,
        committed_sha256=committed_sha,
        mode=mode,
    )
