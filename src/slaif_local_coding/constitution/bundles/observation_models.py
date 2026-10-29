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

Version law: ``cache-bundle-observation/2`` (round 017-al) extends the
``/1`` contract additively for the D09 process/chunk collector: the pinned
native exec-wrapper format identity ``codex-native-exec-wrapper/v1``, the
process grammar ``process-chunk/v1``, the ``NativeWrapperFacts`` /
``ProcessPiece`` / ``ProcessPoll`` / ``ProcessObservation`` models, the
``ProcessOutcome`` enum, the four new ``process_*``
limitations plus ``wrapper_header_over_bound``, the new
``ObservationReport.processes`` field (default empty) and five
new ``ObservationBounds`` fields with fixed defaults.  Every ``/1`` field keeps
its exact meaning and single-result behavior, and old ``/1`` reports remain
loadable (the new fields take their empty defaults).  A ``/2`` report
requires a ``/2`` consumer because it carries the additive ``processes``
field: raw ``/1`` and ``/2`` reports differ by exactly the additive fields
and the ``observer_version`` string — the additive-field projection (drop
``processes``) is the accurate comparison, not equality modulo
``observer_version`` alone.  The legacy ``codex-exec-wrapper/v1`` grammar
keeps its exact law (including source-is-source).
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import core_schema

#: Identity of this pure observation implementation.
OBSERVER_VERSION = "cache-bundle-observation/2"

#: Versioned root-envelope delimiter contract (see the observation contract).
ENVELOPE_FORMAT = "codex-project-instructions/v1"

#: Versioned literal shell-read grammar.
READ_GRAMMAR = "literal-shell-read/v1"

#: Versioned observed Codex exec wrapper format.
TOOL_WRAPPER_FORMAT = "codex-exec-wrapper/v1"

#: Versioned pinned-native exec wrapper format (objective 017-al, D09): the
#: pinned 0.164.0 function_tool_response text wrapper.  Distinct from the
#: legacy ``codex-exec-wrapper/v1`` grammar; the two formats never mix.
NATIVE_TOOL_WRAPPER_FORMAT = "codex-native-exec-wrapper/v1"

#: Versioned D09 process/chunk association grammar (objective 017-al).
PROCESS_CHUNK_GRAMMAR = "process-chunk/v1"

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


#: Fixed placeholder for private call/result ID values in operational
#: representations: a private value is never echoed, invented, hashed
#: or re-serialized into a representation.
PRIVATE_ID_PLACEHOLDER = "<private-id>"


def _redact_private_ids(value: object) -> object:
    """Redact private ID values in a dumped model structure.

    Observed private ID values are replaced by the fixed placeholder:
    non-empty ``call_id`` / ``exec_call_id`` / ``poll_call_id`` string
    values and every observed ``session_id`` value (exact process
    identity, never echoed).  The observable no-ID state (``""``) is
    preserved, and every other field, enum, count, location, span and
    digest is unchanged.
    """

    _PRIVATE_ID_KEYS = ("call_id", "exec_call_id", "poll_call_id", "session_id")

    if isinstance(value, dict):
        redacted: dict[str, object] = {}
        for key, item in value.items():
            if key in _PRIVATE_ID_KEYS and (
                (isinstance(item, str) and item != "") or (key == "session_id" and item is not None)
            ):
                redacted[key] = PRIVATE_ID_PLACEHOLDER
            else:
                redacted[key] = _redact_private_ids(item)
        return redacted
    if isinstance(value, (list, tuple)):
        return [_redact_private_ids(item) for item in value]
    return value


def operational_repr(model: BaseModel) -> str:
    """Operational representation for observation models.

    Fixed enums, counts, locations, spans and digests remain
    observable; private call/result ID values never do.  The internal
    typed fields are untouched — only their representation is
    suppressed.
    """

    data = _redact_private_ids(model.model_dump(mode="json"))
    return f"{type(model).__name__}({json.dumps(data, sort_keys=True, separators=(',', ':'))})"


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


class ProcessOutcome(StrEnum):
    """D09 process-chain completion state (objective 017-al).

    Each state is distinct and never conflated: ``COMPLETE`` requires
    every associated observed piece to be present, coherent,
    untruncated, within bounds and a proven final success; a prior
    truncation invalidates whole-source completion even on final
    exit zero.  ``RUNNING`` means no frame in this request proved
    completion (never a completion claim).  ``TRUNCATED`` and
    ``NONZERO_EXIT`` preserve the honest terminal-frame facts.
    ``MISSING_BODY`` is the reserved state for a final frame with no
    output section; under the closed native grammar such a frame cannot
    prove completion (a missing body is a closed-wrapper validation
    refusal, not a proven exit fact — the absence of the delimiter does
    not establish that exit text is absent), so the state is never
    emitted: a missing body is surfaced as the frame-level
    ``MISSING_OUTPUT_BODY`` refusal reason inside an ``UNSUPPORTED``
    observation, distinct from a proven empty output (a complete empty
    piece).
    ``UNSUPPORTED`` covers chains whose closed grammar or identity
    was not established; a full source is never fabricated.
    """

    COMPLETE = "complete"
    TRUNCATED = "truncated"
    NONZERO_EXIT = "nonzero_exit"
    RUNNING = "running"
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
    STDIN_OPERAND = "stdin_operand"
    # Tool call/result pairing and wrapper (D05)
    UNSUPPORTED_TOOL = "unsupported_tool"
    NAMESPACE_TOOL_UNPROVEN = "namespace_tool_unproven"
    DUPLICATE_CALL_ID = "duplicate_call_id"
    MISSING_CALL_ID = "missing_call_id"
    MALFORMED_CALL_ID = "malformed_call_id"
    MISSING_RESULT_ID = "missing_result_id"
    MALFORMED_RESULT_ID = "malformed_result_id"
    MISSING_CALL_RESULT = "missing_call_result"
    MISMATCHED_CALL_ID = "mismatched_call_id"
    PRE_CALL_RESULT = "pre_call_result"
    NONZERO_EXIT = "nonzero_exit"
    UNKNOWN_COMPLETION = "unknown_completion"
    TRUNCATED_OUTPUT = "truncated_output"
    PROCESS_RUNNING = "process_running"
    WRITE_STDIN_CHUNK = "write_stdin_chunk"
    MULTI_CHUNK_DEFERRED = "multi_chunk_deferred"
    MISSING_OUTPUT_BODY = "missing_output_body"
    MALFORMED_WRAPPER = "malformed_wrapper"
    OUTPUT_OVER_BOUND = "output_over_bound"
    # Process/chunk observation (D09, objective 017-al)
    PROCESS_SESSION_CONFLICT = "process_session_conflict"
    PROCESS_POLL_INVALID = "process_poll_invalid"
    PROCESS_CHAIN_CONFLICT = "process_chain_conflict"
    PROCESS_TRUNCATED = "process_truncated"
    WRAPPER_HEADER_OVER_BOUND = "wrapper_header_over_bound"
    # Read plan grammar (D06/D07/D08)
    CD_TARGET_UNSUPPORTED = "cd_target_unsupported"
    ECHO_TARGET_UNSUPPORTED = "echo_target_unsupported"
    OUTER_BOUNDARY_UNPROVEN = "outer_boundary_unproven"
    # Loop grammar (D07)
    LOOP_FORM_UNSUPPORTED = "loop_form_unsupported"
    LOOP_VARIABLE_UNSUPPORTED = "loop_variable_unsupported"
    LOOP_TEMPLATE_UNSUPPORTED = "loop_template_unsupported"
    LOOP_GUARD_UNSUPPORTED = "loop_guard_unsupported"
    LOOP_ITERATION_UNPROVEN = "loop_iteration_unproven"
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


class NativeWrapperFacts(_Frozen):
    """Parsed pinned-native exec-wrapper metadata (D09, objective 017-al).

    Distinct versioned format identity from the legacy
    ``codex-exec-wrapper/v1`` grammar: the pinned 0.164.0
    function_tool_response text wrapper — header sections in the fixed
    order (optional chunk ID, mandatory wall time, optional exit or
    running section, optional original token count) over the exact
    ``Output:`` delimiter line, which is LF-terminated even when the
    output is empty.  Dispatch is on bounded header evidence only:
    text after the delimiter is the exact output section and is never
    re-parsed as header (the version-bound native truncation fact is
    read from the output section and can only ever mark the frame
    truncated — never complete).  The chunk ID is private transport
    metadata: only its presence is retained, never its value.  The
    session ID is exact process identity, usable internally for
    association while operational ``str``/``repr`` suppress it.
    """

    wrapper_format: str = NATIVE_TOOL_WRAPPER_FORMAT
    chunk_id_present: bool = False
    wall_time_present: bool = False
    exit_code: int | None = Field(default=None, ge=-(2**31), le=2**31 - 1)
    session_id: int | None = Field(default=None, gt=0, le=2**31 - 1)
    original_token_count: int | None = Field(default=None, ge=0)
    output_present: bool
    output_span: CharSpan | None = None
    output_char_length: int | None = Field(default=None, ge=0)
    output_byte_length: int | None = Field(default=None, ge=0)
    #: Version-bound native truncation fact (pinned warning / omission
    #: marker in the output section); never a completeness proof.
    truncated: bool = False
    reasons: tuple[Limitation, ...] = ()

    def __repr__(self) -> str:
        return operational_repr(self)

    def __str__(self) -> str:
        return operational_repr(self)


class ProcessPiece(_Frozen):
    """One exact observed output slice of a process chain (D09).

    ``char_span`` is relative to the exact decoded JSON string that
    carried THIS result's text (the per-result domain; never a
    concatenated string that never existed in the request).  An empty
    piece is exact (a proven empty output retains the delimiter LF)
    and cannot inflate the nonempty-piece proof.  Raw piece text never
    enters the report: spans, lengths and the transient whole-bundle
    digest are the retained facts.
    """

    piece_index: int = Field(ge=0)
    result_location: str
    char_span: CharSpan
    char_length: int = Field(ge=0)
    byte_length: int = Field(ge=0)
    empty: bool


class ProcessPoll(_Frozen):
    """One causally associated empty-stdin poll and its own result (D09).

    Positions are exact numeric structural positions; the poll's
    result follows its own issued call (never a positional guess).
    ``wrapper`` carries the pinned-native facts of the poll's own
    result text and ``piece`` its exact output slice.
    """

    poll_call_id: str
    poll_call_location: str
    poll_position: int = Field(ge=0)
    result_location: str
    result_position: int = Field(ge=0)
    wrapper: NativeWrapperFacts
    piece: ProcessPiece

    def __repr__(self) -> str:
        return operational_repr(self)

    def __str__(self) -> str:
        return operational_repr(self)


class ProcessObservation(_Frozen):
    """D09 per-request process/chunk observation (inert, objective 017-al).

    Models the original exec occurrence, each causally associated
    empty-stdin poll and its own result, the exact original source
    pieces in causal order, and the final process completion.  The
    earned outer attribution is computed on the transient ordered
    concatenation of the exact pieces and mapped back onto the
    original pieces (``region_piece_spans``); ``bundle_digest`` is the
    digest of the exact earned region bytes.  Raw source never enters
    the report, no dummy span over a concatenated string is minted,
    and the occurrence-hash law holds (one attributable occurrence
    may carry its exact member digest; boundaryless multiple
    occurrences stay unknown).  ``proven_executed`` is nonempty only
    when the original exec command is itself a complete all-cat parse
    (the actual sleep-bearing stream command stays unearned);
    ``requested_members`` preserves the exact original command's
    finite parsed data in every outcome.
    """

    process_grammar: str = PROCESS_CHUNK_GRAMMAR
    endpoint: str
    #: Exact observed exec call ID; internal association data stays
    #: exact, operational ``str``/``repr`` suppress it.
    exec_call_id: str
    exec_call_location: str
    exec_call_position: int = Field(ge=0)
    initial_result_location: str
    initial_result_position: int = Field(ge=0)
    initial_wrapper: NativeWrapperFacts
    requested_members: tuple[NormalizedPath, ...] = ()
    proven_executed: tuple[str, ...] = ()
    #: Exact member digest per proven occurrence; the occurrence-hash law
    #: holds — one attributable file occurrence covering a proven region
    #: carries its exact digest, boundaryless multiple occurrences stay
    #: unknown (``None``), and no per-member hash is otherwise invented.
    member_digests: tuple[str | None, ...] = ()
    #: Per-piece sub-spans (aligned with ``pieces``; offsets relative to
    #: the exact decoded JSON string that carried each piece's result
    #: text — ABSOLUTE offsets in the global span law: the output-local
    #: region clip plus the owning piece's ``char_span.start``;
    #: ``None`` = no region overlap for that piece) of the earned outer
    #: region mapped back from the transient joined view onto the
    #: original pieces.  No span over a detached output substring or a
    #: virtual joined string.  Empty when no region is proven.
    region_piece_spans: tuple[CharSpan | None, ...] = ()
    #: Character length of the earned outer region over the transient
    #: joined view (``None`` when no region is proven).
    proven_region_char_length: int | None = Field(default=None, ge=0)
    #: Number of DISTINCT proven members (the earned width; never the
    #: chunk/piece count); ``None`` unless the outcome is earned —
    #: nonacquiring states never invent earned width.
    distinct_member_count: int | None = Field(default=None, ge=0)
    #: Distinct-member slot width (mirrors the read-observation law).
    slot_width: int | None = Field(default=None, ge=0)
    polls: tuple[ProcessPoll, ...] = ()
    final_result_location: str | None = None
    final_result_position: int | None = Field(default=None, ge=0)
    final_wrapper: NativeWrapperFacts | None = None
    pieces: tuple[ProcessPiece, ...] = ()
    piece_count: int = Field(ge=0)
    nonempty_piece_count: int = Field(ge=0)
    total_char_length: int = Field(ge=0)
    total_byte_length: int = Field(ge=0)
    outcome: ProcessOutcome
    bundle_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    reasons: tuple[Limitation, ...] = ()

    def __repr__(self) -> str:
        return operational_repr(self)

    def __str__(self) -> str:
        return operational_repr(self)


class ReadObservation(_Frozen):
    """One paired call/result read observation (D03-D05).

    Requested members and proven-executed members are distinct.  Individual
    member digests stay ``None`` unless boundaries are actually proven; the
    bundle digest is never a per-file hash.
    """

    read_grammar: str = READ_GRAMMAR
    wrapper_format: str = TOOL_WRAPPER_FORMAT
    #: Exact observed call ID; internal pairing/association data stays
    #: exact and usable, while operational ``str``/``repr`` suppress it.
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

    def __repr__(self) -> str:
        return operational_repr(self)

    def __str__(self) -> str:
        return operational_repr(self)


class UnpairedRecord(_Frozen):
    location: str
    #: Exact observed call ID (``""`` is the observable no-ID state);
    #: internal bookkeeping stays exact, operational representations
    #: suppress non-empty private values.
    call_id: str
    limitation: Limitation

    def __repr__(self) -> str:
        return operational_repr(self)

    def __str__(self) -> str:
        return operational_repr(self)


class ObservationReport(_Frozen):
    """Pure observation result for one decoded request payload.

    The report carries spans, digests, counts and fixed reasons only; it never
    carries raw source content, and it never derives identity from text.
    Operational ``str``/``repr`` never echo private call/result ID values
    or process session IDs (fixed enums, counts, locations and digests
    remain observable).
    """

    observer_version: str = OBSERVER_VERSION
    endpoint: str
    input_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    roots: RootScanResult
    reads: tuple[ReadObservation, ...] = ()
    unpaired: tuple[UnpairedRecord, ...] = ()
    #: D09 process/chunk observations (objective 017-al); empty when the
    #: payload carries no qualifying native process chain.  Additive in
    #: ``cache-bundle-observation/2``; every ``/1`` field and behavior is
    #: preserved unchanged.
    processes: tuple[ProcessObservation, ...] = ()

    def __repr__(self) -> str:
        return operational_repr(self)

    def __str__(self) -> str:
        return operational_repr(self)


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
    # D09 process/chunk bounds (objective 017-al): fixed defaults,
    # enforced by a no-retention preflight before any process piece is
    # allocated or retained (observation contract section 5a).
    #: Independent process chains per request.
    max_process_sessions: int = Field(default=4, ge=1, le=10_000)
    #: Empty-stdin polls per chain.
    max_process_polls: int = Field(default=12, ge=1, le=10_000)
    #: Pieces per chain (one initial frame plus the bounded polls).
    max_process_pieces: int = Field(default=13, ge=1, le=10_000)
    #: Cumulative source characters over one chain's ordered pieces.
    max_process_source_chars: int = Field(default=1_000_000, ge=1, le=10_000_000)
    #: Cumulative exact UTF-8 source BYTES over one chain's ordered
    #: pieces; enforced before any piece retention or concatenation copy.
    max_process_source_bytes: int = Field(default=1_000_000, ge=1, le=10_000_000)
