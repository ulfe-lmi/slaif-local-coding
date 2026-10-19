"""Typed pure-observation contracts for dependency-bundle cache stage 017.

These models belong to the planned ``dependency-bundles-v1`` profile (see
``docs/CACHE-OBSERVATION-CONTRACT.md``).  They are **inert**: nothing in this
package is wired into the legacy request execution path, and no model here may
establish an authenticated principal from untrusted text.

Coordinate law: every span is a pair of character offsets into the exact
decoded JSON string that carried the source.  ``CharSpan.to_byte_span``
converts those offsets to UTF-8 byte offsets over the same string; the two
domains are never mixed.  Digests are computed over the exact observed bytes
(``str.encode("utf-8")``) and never assert anything about the original
filesystem encoding.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import core_schema

#: Identity of this pure observation implementation.
OBSERVER_VERSION = "cache-bundle-observation/1"

#: Versioned root-envelope delimiter contract (see the observation contract).
ENVELOPE_FORMAT = "codex-project-instructions/v1"

#: Versioned literal shell-read grammar.
READ_GRAMMAR = "literal-shell-read/v1"

#: Versioned observed Codex exec wrapper format.
TOOL_WRAPPER_FORMAT = "codex-exec-wrapper/v1"

#: SHA-256 of the empty source; a proven zero-byte read is a complete empty
#: version carrying exactly this digest.
EMPTY_SOURCE_SHA256 = hashlib.sha256(b"").hexdigest()


def sha256_hex(text: str) -> str:
    """Digest the exact observed UTF-8 bytes of *text*.

    Raises ``UnicodeEncodeError`` for malformed (lone surrogate) input; callers
    are expected to pre-validate and return a typed limitation instead of a
    crash.
    """

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def contains_lone_surrogates(text: str) -> bool:
    """True when *text* cannot be encoded as valid UTF-8 (lone surrogates)."""

    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return True
    return False


def utf8_byte_span(text: str, start: int, end: int) -> tuple[int, int]:
    """Convert character offsets to UTF-8 byte offsets over *text*."""

    if not 0 <= start <= end <= len(text):
        raise ValueError("span offsets out of range")
    return (
        len(text[:start].encode("utf-8")),
        len(text[:end].encode("utf-8")),
    )


def canonical_payload_fingerprint(payload: object) -> str:
    """Deterministic fingerprint of the exact observed decoded payload.

    Canonical JSON (sorted keys, compact separators, ASCII escapes) makes the
    fingerprint stable across processes without depending on dict ordering.
    """

    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


class OccurrenceKind(StrEnum):
    ROOT = "root"
    ENVIRONMENT = "environment"
    MARKER_PROSE = "marker_prose"
    NON_ROOT = "non_root"


class RootStatus(StrEnum):
    OK = "ok"
    NO_ROOT = "no_root"
    VERSION_CANDIDATES = "version_candidates"
    CONFLICT = "conflict"
    UNSUPPORTED = "unsupported"


class ReadOutcome(StrEnum):
    COMPLETE = "complete"
    NONZERO_EXIT = "nonzero_exit"
    TRUNCATED = "truncated"
    PARTIAL = "partial"
    MISSING_BODY = "missing_body"
    UNSUPPORTED = "unsupported"


class PathForm(StrEnum):
    ABSOLUTE = "absolute"
    RELATIVE = "relative"


class ExitStatus(StrEnum):
    ZERO = "zero"
    NONZERO = "nonzero"
    UNKNOWN = "unknown"


class TruncationStatus(StrEnum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


class Limitation(StrEnum):
    """Fixed limitation vocabulary.

    Values are stable identifiers that never echo payload text; operational
    consumers may log them safely.
    """

    # Root envelope (D01/D02)
    MARKER_MISPLACED = "marker_misplaced"
    MALFORMED_DELIMITERS = "malformed_delimiters"
    DUPLICATE_MARKER = "duplicate_marker"
    UNCLOSED_TAIL = "unclosed_tail"
    UNSUPPORTED_SHAPE = "unsupported_shape"
    OVER_BOUND = "over_bound"
    INVALID_SCOPE_LABEL = "invalid_scope_label"
    COMPETING_ROOT_SCOPES = "competing_root_scopes"
    MALFORMED_UNICODE = "malformed_unicode"
    MALFORMED_ENVIRONMENT = "malformed_environment"
    UNSUPPORTED_ENDPOINT = "unsupported_endpoint"
    # Client paths (D03/D04)
    OUTSIDE_WORKSPACE = "outside_workspace"
    UNKNOWN_WORKSPACE = "unknown_workspace"
    UNPROVEN_CWD = "unproven_cwd"
    TRAVERSAL = "traversal"
    UNSUPPORTED_PATH_FORM = "unsupported_path_form"
    AMBIGUOUS_PATH = "ambiguous_path"
    PATH_TOO_LONG = "path_too_long"
    NON_LITERAL_OPERAND = "non_literal_operand"
    EMPTY_OPERAND = "empty_operand"
    # Read command grammar (D03/D04)
    COMMAND_UNSUPPORTED = "command_unsupported"
    COMMAND_EMPTY = "command_empty"
    COMMAND_OVER_BOUND = "command_over_bound"
    COMMAND_SUBSTITUTION = "command_substitution"
    SHELL_ESCAPE = "shell_escape"
    GLOB_UNPROVEN = "glob_unproven"
    REDIRECTION = "redirection"
    PIPE = "pipe"
    MULTIPLE_COMMANDS = "multiple_commands"
    HEREDOC = "heredoc"
    FRAGMENT_COMMAND = "fragment_command"
    COMMENT_PRESENT = "comment_present"
    QUOTED_OPERAND = "quoted_operand"
    TILDE_UNPROVEN = "tilde_unproven"
    # Tool call/result pairing and wrapper (D05)
    UNSUPPORTED_TOOL = "unsupported_tool"
    NAMESPACE_TOOL_UNPROVEN = "namespace_tool_unproven"
    DUPLICATE_CALL_ID = "duplicate_call_id"
    MISSING_CALL_RESULT = "missing_call_result"
    MISMATCHED_CALL_ID = "mismatched_call_id"
    NONZERO_EXIT = "nonzero_exit"
    UNKNOWN_COMPLETION = "unknown_completion"
    TRUNCATED_OUTPUT = "truncated_output"
    PROCESS_RUNNING = "process_running"
    WRITE_STDIN_CHUNK = "write_stdin_chunk"
    MULTI_CHUNK_DEFERRED = "multi_chunk_deferred"
    MISSING_OUTPUT_BODY = "missing_output_body"
    MALFORMED_WRAPPER = "malformed_wrapper"
    OUTPUT_OVER_BOUND = "output_over_bound"
    # Shared
    ENDPOINT_UNSUPPORTED = "endpoint_unsupported"


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class CharSpan(_Frozen):
    """Half-open character offsets into one exact decoded JSON string."""

    start: int = Field(ge=0)
    end: int = Field(ge=0)

    @field_validator("end")
    @classmethod
    def _check_order(cls, value: int, info: core_schema.FieldValidationInfo) -> int:
        start = info.data.get("start", 0)
        if value < start:
            raise ValueError("span end must not precede start")
        return value

    @property
    def length(self) -> int:
        return self.end - self.start

    def to_byte_span(self, text: str) -> tuple[int, int]:
        """Exact UTF-8 byte offsets of this character span over *text*."""

        return utf8_byte_span(text, self.start, self.end)

    def slice(self, text: str) -> str:
        if self.end > len(text):
            raise ValueError("span extends beyond source string")
        return text[self.start : self.end]


class RootOccurrence(_Frozen):
    """One classified occurrence of envelope-like text in the payload."""

    kind: OccurrenceKind
    location: str
    status: RootStatus
    scope_label: str | None = None
    content_span: CharSpan | None = None
    envelope_span: CharSpan | None = None
    digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    byte_length: int | None = Field(default=None, ge=0)
    reasons: tuple[Limitation, ...] = ()


class VersionCandidate(_Frozen):
    """Same-scope differing root content, attributable for later resolution."""

    scope_label: str
    digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    occurrences: tuple[str, ...] = Field(min_length=1)


class RootScanResult(_Frozen):
    """D01/D02 result: evidenced roots, candidates, conflicts, limitations."""

    envelope_format: str = ENVELOPE_FORMAT
    status: RootStatus
    occurrences: tuple[RootOccurrence, ...] = ()
    version_candidates: tuple[VersionCandidate, ...] = ()
    conflicts: tuple[Limitation, ...] = ()
    scanned_items: int = Field(default=0, ge=0)

    @property
    def roots(self) -> tuple[RootOccurrence, ...]:
        """Valid (status-ok) root occurrences only; malformed stays observable."""

        return tuple(
            o
            for o in self.occurrences
            if o.kind is OccurrenceKind.ROOT and o.status is RootStatus.OK
        )


class PathContext(_Frozen):
    """Evidenced client-workspace context; never inferred from prose.

    ``workspace`` is the evidenced default client cwd (an explicit validated
    client-workspace context, e.g. the POSIX absolute scope of an evidenced
    root).  A logical (non-POSIX) scope yields no path normalization.  An
    adapter-host cwd is never a valid value.
    """

    workspace: str | None = None
    workdir: str | None = None

    @field_validator("workspace", "workdir")
    @classmethod
    def _no_control(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if any(ord(c) < 0x20 for c in value):
            raise ValueError("context path contains control characters")
        return value


class NormalizedPath(_Frozen):
    """Lexical normalization result for one literal read operand."""

    raw: str
    form: PathForm
    quoted: bool = False
    normalized: str | None = None
    limitation: Limitation | None = None


class ReadCommandParse(_Frozen):
    """Bounded literal ``cat`` grammar result; command syntax is data.

    ``command_digest`` is the SHA-256 of the exact observed command bytes and
    is explicitly absent (``None``) only under the typed
    ``MALFORMED_UNICODE`` / non-string contract — never a placeholder digest
    treated as valid.
    """

    grammar: str = READ_GRAMMAR
    command_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    command_length: int = Field(ge=0)
    complete: bool
    operands: tuple[NormalizedPath, ...] = ()
    reasons: tuple[Limitation, ...] = ()

    @property
    def distinct_operands(self) -> int:
        return len({o.normalized for o in self.operands if o.normalized is not None})


class WrapperFacts(_Frozen):
    """Parsed exec-wrapper metadata; source after ``Output:`` is never this."""

    wrapper_format: str = TOOL_WRAPPER_FORMAT
    exit_status: ExitStatus
    exit_code: int | None = Field(default=None, ge=0, le=255)
    truncation: TruncationStatus
    output_present: bool
    header_span: CharSpan | None = None
    output_span: CharSpan | None = None
    reasons: tuple[Limitation, ...] = ()


class ReadObservation(_Frozen):
    """One paired call/result read observation (D03-D05).

    Requested members and proven-executed members are distinct.  Individual
    member digests stay ``None`` unless boundaries are actually proven; the
    bundle digest is never a per-file hash.
    """

    read_grammar: str = READ_GRAMMAR
    wrapper_format: str = TOOL_WRAPPER_FORMAT
    call_id: str
    endpoint: str
    call_location: str
    result_location: str
    requested_members: tuple[NormalizedPath, ...] = ()
    proven_executed: tuple[str, ...] = ()
    distinct_member_count: int | None = Field(default=None, ge=0)
    slot_width: int | None = Field(default=None, ge=0)
    outcome: ReadOutcome
    completeness: ReadOutcome
    wrapper: WrapperFacts
    content_span: CharSpan | None = None
    removable: bool = False
    bundle_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    member_digests: tuple[str | None, ...] = ()
    reasons: tuple[Limitation, ...] = ()


class UnpairedRecord(_Frozen):
    location: str
    call_id: str
    limitation: Limitation


class ObservationReport(_Frozen):
    """Pure observation result for one decoded request payload.

    The report carries spans, digests, counts and fixed reasons only; it never
    carries raw source content, and it never derives identity from text.
    """

    observer_version: str = OBSERVER_VERSION
    endpoint: str
    input_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    roots: RootScanResult
    reads: tuple[ReadObservation, ...] = ()
    unpaired: tuple[UnpairedRecord, ...] = ()


class ObservationBounds(_Frozen):
    """Finite parser/request bounds; adversarial input must terminate."""

    max_items: int = Field(default=1024, ge=1, le=100_000)
    max_item_chars: int = Field(default=1_000_000, ge=1, le=10_000_000)
    max_label_bytes: int = Field(default=512, ge=1, le=4096)
    max_environment_chars: int = Field(default=100_000, ge=1, le=1_000_000)
    max_commands: int = Field(default=128, ge=1, le=10_000)
    max_command_chars: int = Field(default=4096, ge=1, le=100_000)
    max_operands: int = Field(default=32, ge=1, le=1024)
    max_path_bytes: int = Field(default=256, ge=1, le=4096)
    max_outputs: int = Field(default=128, ge=1, le=10_000)
    max_output_chars: int = Field(default=1_000_000, ge=1, le=10_000_000)
    max_wrapper_header_lines: int = Field(default=8, ge=1, le=64)
    max_tools: int = Field(default=128, ge=1, le=10_000)
