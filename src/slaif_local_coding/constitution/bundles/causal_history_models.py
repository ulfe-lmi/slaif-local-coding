"""Causal-history scope, bounds, records and the strict argument
fingerprint recipe (objective 018-d, slice d; INERT).

``CAUSAL_HISTORY_CONTRACT_VERSION = "cache-causal-history/v1"``;
``CAUSAL_ARGUMENTS_JSON_VERSION = "causal-arguments-json/v1"``.

This module binds the ACTUAL accepted 018-c bundle-admission
namespace (its actual fields and BOTH 64-hex scope keys, revalidated),
an explicit opaque history-lineage ID, the NEW history bounds and the
two history versions into a recompute-and-verify scope; it defines the
typed immutable state records (root anchor, issued calls, completed
read occurrences, per-call result fingerprints, unique immediate
parent links) and the ONE bounded canonical argument-fingerprint
recipe reusable by future 022.

It is pure and inert: no pipeline activation, no RAM service/locks,
no compiler, no disk, no HTTP/SSE observer and no new metrics.  The
state machine itself lives in ``causal_history.py``.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from .bundle_admission_models import (
    ADMISSION_CONTRACT_VERSION,
    AdmissionMode,
    BundleAdmissionBounds,
    BundleAdmissionNamespace,
    _canonical_namespace_fields,
)
from .bundle_proof_models import (
    BUNDLE_PROOF_CONTRACT_VERSION,
    BundleProof,
    BundleProofBounds,
)
from .client_paths import validate_workspace
from .graph_models import (
    GRAPH_CONTRACT_VERSION,
    REFERENCE_GRAMMAR,
    GraphBounds,
    _check_hex64,
    _check_text,
    _fixed,
    _GraphFrozen,
)
from .observation_models import (
    OBSERVER_VERSION,
    PRIVATE_ID_PLACEHOLDER,
    CharSpan,
    Limitation,
    ObservationBounds,
    ProcessOutcome,
)

CAUSAL_HISTORY_CONTRACT_VERSION = "cache-causal-history/v1"
CAUSAL_ARGUMENTS_JSON_VERSION = "causal-arguments-json/v1"

#: Reserved fact ID of the evidenced root anchor inside a frontier.
CAUSAL_ROOT_FACT = "causal-root-anchor/v1"

MAX_REVISION = 2**63 - 1

_ARGUMENTS_ENCODING_PREFIX = b"causal-arguments-json/v1\x00"


class HistoryBounds(_GraphFrozen):
    """New finite causal-history bounds (objective 018-d).

    The order fixes the defaults AND the hard ceilings exactly:
    stricter positive values are permitted and ANY wider direct or
    factory construction is refused.  ``max_work_units`` is the shared
    PER-TRANSITION work ledger; ``max_diagnostics`` is the TOTAL final
    closed-enum diagnostic cap across the emitted lists.  Source and
    argument budgets are bytes, never tokens, product effective
    context ``C`` or physical RSS.
    """

    #: Retained issued-call bindings.
    max_issuances: int = Field(default=4096, ge=1, le=4096)
    #: Retained completed read occurrences.
    max_occurrences: int = Field(default=4096, ge=1, le=4096)
    #: Retained unique immediate parent links.
    max_causal_links: int = Field(default=65536, ge=1, le=65536)
    #: Input members per supplied frontier BEFORE dedup.
    max_frontier_members: int = Field(default=1024, ge=1, le=1024)
    #: Retained immutable call-result fingerprint records.
    max_observed_results: int = Field(default=8192, ge=1, le=8192)
    #: Retained proof member occurrences BEFORE distinct-path width.
    max_retained_members: int = Field(default=16384, ge=1, le=16384)
    #: Retained proof piece/span records.
    max_retained_pieces: int = Field(default=32768, ge=1, le=32768)
    #: Root anchor once plus exact UTF-8 proof-source bytes per newly
    #: retained occurrence (conservative represented-source units, not
    #: physical RSS).
    max_retained_source_bytes: int = Field(default=16777216, ge=1, le=16777216)
    #: Actual argument fingerprint input/canonical representation
    #: bytes.
    max_argument_bytes: int = Field(default=65536, ge=1, le=65536)
    #: Cumulative input + canonical argument representation bytes
    #: inspected/constructed per transition, before copies.
    max_total_argument_bytes: int = Field(default=4194304, ge=1, le=4194304)
    #: Per-argument JSON value/container/key units; each
    #: value/container and each object key counts 1.
    max_argument_nodes: int = Field(default=4096, ge=1, le=4096)
    #: JSON nesting depth, scalar depth 0.
    max_argument_depth: int = Field(default=32, ge=1, le=32)
    #: Shared PER-TRANSITION work ledger.
    max_work_units: int = Field(default=65536, ge=1, le=65536)
    #: TOTAL final closed-enum diagnostics across lists.
    max_diagnostics: int = Field(default=64, ge=1, le=64)


class CausalHistoryOutcome(StrEnum):
    """Closed transition outcomes.

    ``accepted`` advances the revision exactly once; ``replayed`` is a
    pure idempotent transition (no revision advance, no state
    mutation); every ``refused_*`` preserves the EXACT prior state.
    """

    ACCEPTED = "accepted"
    REPLAYED = "replayed"
    REFUSED_CAS_MISMATCH = "refused_cas_mismatch"
    REFUSED_FOREIGN_SCOPE = "refused_foreign_scope"
    REFUSED_NO_ROOT = "refused_no_root"
    REFUSED_ROOT_CONFLICT = "refused_root_conflict"
    REFUSED_VERSION_CONFLICT = "refused_version_conflict"
    REFUSED_CONFLICT = "refused_conflict"
    REFUSED_UNKNOWN_PARENT = "refused_unknown_parent"
    REFUSED_CYCLE = "refused_cycle"
    REFUSED_OVER_BOUND = "refused_over_bound"


class CausalHistoryLimitation(StrEnum):
    """Closed fixed diagnostic vocabulary for history transitions.

    Free-form strings and arbitrary text are rejected; no value echoes
    payload content.  The shared 017 observation limitations are a
    SEPARATE closed vocabulary (``observation_models.Limitation``)
    carried alongside in the transition.
    """

    # Shared early root/binding refusals (inherited 018-a/017 laws).
    NO_ROOT = "no_root"
    COMPETING_ROOTS = "competing_roots"
    WORKSPACE_MISMATCH = "workspace_mismatch"
    ROOT_CONTEXT_MISMATCH = "root_context_mismatch"
    WORKSPACE_UNPROVEN = "workspace_unproven"
    VERSION_UNSUPPORTED = "version_unsupported"
    BATCH_OVER_BOUND = "batch_over_bound"
    DIAGNOSTICS_FULL = "diagnostics_full"
    # Canonical argument recipe (causal-arguments-json/v1).
    ARGUMENTS_UNSUPPORTED = "arguments_unsupported"
    ARGUMENTS_MALFORMED_UNICODE = "arguments_malformed_unicode"
    ARGUMENTS_OVER_BOUND = "arguments_over_bound"
    # Call identity bookkeeping (typed, never invented).
    CALL_ID_MISSING = "call_id_missing"
    CALL_ID_MALFORMED = "call_id_malformed"
    # Issuance / frontier / result conflicts.
    FRONTIER_OVER_BOUND = "frontier_over_bound"
    FRONTIER_CONFLICT = "frontier_conflict"
    ISSUANCE_CONFLICT = "issuance_conflict"
    RESULT_CONFLICT = "result_conflict"
    # Late trusted receipts.
    RECEIPT_BINDING_MISMATCH = "receipt_binding_mismatch"
    RECEIPT_UNKNOWN_PARENT = "receipt_unknown_parent"
    RECEIPT_CYCLE = "receipt_cycle"
    # Inherited scoped diagnostics of the accepted 017/018-b stages,
    # carried under their EXACT fixed names (propagated, never
    # relabeled; the same 018-c admission pattern).
    SEAM_CONFLICT = "seam_conflict"
    BUNDLES_OVER_BOUND = "bundles_over_bound"
    SOURCE_OVER_BOUND = "source_over_bound"
    TOTAL_SOURCE_OVER_BOUND = "total_source_over_bound"
    MEMBERS_OVER_BOUND = "members_over_bound"
    SEGMENTS_OVER_BOUND = "segments_over_bound"
    MARKER_OVER_BOUND = "marker_over_bound"
    MARKER_SEARCH_OVER_BOUND = "marker_search_over_bound"
    MARKER_EMPTY = "marker_empty"
    MARKER_MISSING = "marker_missing"
    MARKER_DUPLICATE = "marker_duplicate"
    MARKER_ORDER = "marker_order"
    MARKER_OVERLAP = "marker_overlap"
    PLAN_UNSUPPORTED = "plan_unsupported"
    MEMBER_UNRESOLVED = "member_unresolved"
    MEMBER_PATH_OVER_BOUND = "member_path_over_bound"
    SEGMENT_UNEXPLAINED = "segment_unexplained"
    OUTPUT_INCONSISTENT = "output_inconsistent"
    SOURCE_CONFLICT = "source_conflict"
    # Trusted-binding shape (a malformed immutable binding field).
    MALFORMED_BINDING = "malformed_binding"
    # Retention / work bound crossings.
    ISSUANCES_OVER_BOUND = "issuances_over_bound"
    OCCURRENCES_OVER_BOUND = "occurrences_over_bound"
    CAUSAL_LINKS_OVER_BOUND = "causal_links_over_bound"
    RESULTS_OVER_BOUND = "results_over_bound"
    RETAINED_MEMBERS_OVER_BOUND = "retained_members_over_bound"
    RETAINED_PIECES_OVER_BOUND = "retained_pieces_over_bound"
    RETAINED_SOURCE_BYTES_OVER_BOUND = "retained_source_bytes_over_bound"
    WORK_UNITS_OVER_BOUND = "work_units_over_bound"
    REVISION_OVERFLOW = "revision_overflow"
    # Bounded transient replay evidence.
    REPLAY_POSITION_SHIFTED = "replay_position_shifted"


class CausalRelation(StrEnum):
    """Closed occurrence-relation vocabulary.

    ``before``/``after`` hold only through bounded transitive
    reachability over the frozen parent evidence; ``same`` holds only
    for the same KNOWN completed occurrence; unknown or incomplete
    IDs are ``unknown`` (even equal unknown IDs); two known complete
    unconnected events are ``incomparable``.
    """

    SAME = "same"
    BEFORE = "before"
    AFTER = "after"
    INCOMPARABLE = "incomparable"
    UNKNOWN = "unknown"


# --- The canonical argument-fingerprint recipe ---------------------------


class ArgumentFingerprintResult(_GraphFrozen):
    """One strict argument-recipe outcome.

    On success ``fingerprint`` is the 64-hex sha256 over the
    domain-separated encoding ``causal-arguments-json/v1\\0`` + tool
    name UTF-8 + ``\\0`` + canonical JSON bytes; on refusal it is
    ``None`` with the fixed closed reason.  Raw arguments are never
    retained in any state record.
    """

    fingerprint: str | None = None
    reason: CausalHistoryLimitation | None = None
    input_bytes: int = Field(default=0, ge=0)
    canonical_bytes: int = Field(default=0, ge=0)
    node_count: int = Field(default=0, ge=0)
    max_depth: int = Field(default=0, ge=0)

    @field_validator("fingerprint")
    @classmethod
    def _v_fingerprint(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _check_hex64(value, "fingerprint")

    @property
    def ok(self) -> bool:
        return self.fingerprint is not None


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class _ArgWalk:
    """The single strict parse/canonical walk.

    Every value/container and every object key is charged (one work
    unit BEFORE the visit, one node unit) with the node/depth bounds
    enforced at the visit; duplicate object keys, nonfinite numbers,
    malformed Unicode and any non-strict JSON are fixed typed
    limitations, never guessed matching.
    """

    def __init__(
        self,
        text: str,
        *,
        max_nodes: int,
        max_depth: int,
        max_canonical: int,
        charge_total: Callable[[int], bool],
        work: Callable[[], bool],
    ) -> None:
        self._text = text
        self._pos = 0
        self._max_nodes = max_nodes
        self._max_depth = max_depth
        self._max_canonical = max_canonical
        self._charge = charge_total
        self._work = work
        self._nodes = 0
        self._max_depth_seen = 0
        self._canonical_used = 0
        self._error: CausalHistoryLimitation | None = None
        self._key_text = ""

    # -- bookkeeping ----------------------------------------------------

    def _charge_canonical(self, n: int) -> bool:
        """Charge ``n`` canonical bytes BEFORE they are retained.

        The PER-ARGUMENT running canonical-byte cap is enforced FIRST
        (against ``self._max_canonical``); only bytes the argument cap
        admits are then charged to the SHARED cumulative ledger, so a
        per-argument refusal never pollutes the transition budget with
        crossing bytes.  Either refusal is a fixed over-bound outcome
        (no crossing copy).
        """
        if n:
            if self._canonical_used + n > self._max_canonical:
                self._error = CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
                return False
            if not self._charge(n):
                self._error = CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
                return False
            self._canonical_used += n
        return True

    def _unit(self) -> None:
        if self._error is not None:
            return
        if not self._work():
            self._error = CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
            return
        self._nodes += 1
        if self._nodes > self._max_nodes:
            self._error = CausalHistoryLimitation.ARGUMENTS_OVER_BOUND

    def _skip_ws(self) -> None:
        text = self._text
        n = len(text)
        while self._pos < n and text[self._pos] in " \t\r\n":
            self._pos += 1

    def _peek(self) -> str | None:
        if self._pos < len(self._text):
            return self._text[self._pos]
        return None

    # -- values ---------------------------------------------------------

    def value(self, enclosing: int) -> bytes | None:
        """Parse one value at ``enclosing`` container depth; return its
        canonical bytes (the caller keeps them)."""
        if self._error is not None:
            return None
        if enclosing > self._max_depth:
            self._error = CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
            return None
        self._max_depth_seen = max(self._max_depth_seen, enclosing)
        self._unit()
        if self._error is not None:
            return None
        self._skip_ws()
        ch = self._peek()
        if ch is None:
            self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
            return None
        if ch == "{":
            return self._object(enclosing)
        if ch == "[":
            return self._array(enclosing)
        if ch == '"':
            # _string charges its own canonical bytes BEFORE the
            # canonical construction (no crossing copy).
            return self._string()
        # _literal_or_number charges its own canonical bytes BEFORE
        # encode and retention (no crossing copy).
        return self._literal_or_number()

    def _object(self, enclosing: int) -> bytes | None:
        self._pos += 1  # consume '{'
        if not self._charge_canonical(1):  # the opening brace
            return None
        entries: list[tuple[str, bytes, bytes]] = []
        seen: set[str] = set()
        used = 2  # the object braces of the canonical form
        self._skip_ws()
        if self._peek() == "}":
            self._pos += 1
            if not self._charge_canonical(1):  # the closing brace
                return None
            return b"{}"
        while True:
            if self._error is not None:
                return None
            self._skip_ws()
            if self._peek() != '"':
                self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
                return None
            # Every object KEY is a charged node BEFORE its parse and
            # retention (node/work bounds are enforced at the visit).
            self._unit()
            if self._error is not None:
                return None
            encoded_key = self._string()
            if encoded_key is None:
                return None
            key_text = self._key_text
            if key_text in seen:
                self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
                return None
            seen.add(key_text)
            self._skip_ws()
            if self._peek() != ":":
                self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
                return None
            self._pos += 1
            val = self.value(enclosing + 1)
            if val is None:
                return None
            # The canonical contribution of this entry INCLUDING the
            # separating comma is bounded BEFORE retention: the
            # per-argument cap and the shared cumulative budget are
            # both enforced before any crossing copy.
            comma = 1 if entries else 0
            if used + comma + len(encoded_key) + 1 + len(val) > self._max_canonical:
                self._error = CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
                return None
            if not self._charge_canonical(comma + 1):  # comma + colon
                return None
            entries.append((key_text, encoded_key, val))
            used += comma + len(encoded_key) + 1 + len(val)
            self._skip_ws()
            ch = self._peek()
            if ch == ",":
                self._pos += 1
                continue
            if ch == "}":
                self._pos += 1
                break
            self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
            return None
        entries.sort(key=lambda item: item[0])
        body = b",".join(k + b":" + v for _, k, v in entries)
        if not self._charge_canonical(1):  # the closing brace
            return None
        return b"{" + body + b"}"

    def _array(self, enclosing: int) -> bytes | None:
        self._pos += 1  # consume '['
        if not self._charge_canonical(1):  # the opening bracket
            return None
        parts: list[bytes] = []
        used = 2  # the array brackets of the canonical form
        self._skip_ws()
        if self._peek() == "]":
            self._pos += 1
            if not self._charge_canonical(1):  # the closing bracket
                return None
            return b"[]"
        while True:
            item = self.value(enclosing + 1)
            if item is None:
                return None
            # The canonical contribution INCLUDING the separating
            # comma is bounded BEFORE retention (per-argument cap and
            # shared cumulative budget, before any crossing copy).
            comma = 1 if parts else 0
            if used + comma + len(item) > self._max_canonical:
                self._error = CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
                return None
            if not self._charge_canonical(comma):
                return None
            parts.append(item)
            used += comma + len(item)
            self._skip_ws()
            ch = self._peek()
            if ch == ",":
                self._pos += 1
                continue
            if ch == "]":
                self._pos += 1
                break
            self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
            return None
        if not self._charge_canonical(1):  # the closing bracket
            return None
        return b"[" + b",".join(parts) + b"]"

    @staticmethod
    def _escaped_codepoint(text: str, pos: int) -> int | None:
        """EXACTLY four ASCII hex digits at ``pos``.

        Sign, whitespace and underscore are not hex digits: the strict
        escape grammar refuses them (``int(..., 16)`` would accept
        ``+041``, `` 041`` and ``0_41``).
        """
        chunk = text[pos : pos + 4]
        code = 0
        for ch in chunk:
            if "0" <= ch <= "9":
                digit = ord(ch) - 48
            elif "a" <= ch <= "f":
                digit = ord(ch) - 87
            elif "A" <= ch <= "F":
                digit = ord(ch) - 55
            else:
                return None
            code = (code << 4) | digit
        return code

    def _string(self) -> bytes | None:
        self._pos += 1  # consume opening quote
        out: list[str] = []
        text = self._text
        n = len(text)
        while True:
            if self._pos >= n:
                self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
                return None
            ch = text[self._pos]
            if ch == '"':
                self._pos += 1
                break
            if ch == "\\":
                self._pos += 1
                if self._pos >= n:
                    self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
                    return None
                esc = text[self._pos]
                if esc == '"':
                    out.append('"')
                    self._pos += 1
                elif esc == "\\":
                    out.append("\\")
                    self._pos += 1
                elif esc == "/":
                    out.append("/")
                    self._pos += 1
                elif esc == "b":
                    out.append("\b")
                    self._pos += 1
                elif esc == "f":
                    out.append("\f")
                    self._pos += 1
                elif esc == "n":
                    out.append("\n")
                    self._pos += 1
                elif esc == "r":
                    out.append("\r")
                    self._pos += 1
                elif esc == "t":
                    out.append("\t")
                    self._pos += 1
                elif esc == "u":
                    self._pos += 1
                    code = self._escaped_codepoint(text, self._pos)
                    if code is None:
                        self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
                        return None
                    self._pos += 4
                    if 0xD800 <= code <= 0xDBFF:
                        # A high surrogate must be immediately paired
                        # with a low surrogate escape.
                        if self._pos + 6 <= n and text[self._pos : self._pos + 2] == "\\u":
                            low = self._escaped_codepoint(text, self._pos + 2)
                            if low is None:
                                self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
                                return None
                            if not 0xDC00 <= low <= 0xDFFF:
                                self._error = CausalHistoryLimitation.ARGUMENTS_MALFORMED_UNICODE
                                return None
                            out.append(chr(0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)))
                            self._pos += 6
                        else:
                            self._error = CausalHistoryLimitation.ARGUMENTS_MALFORMED_UNICODE
                            return None
                    elif 0xDC00 <= code <= 0xDFFF:
                        self._error = CausalHistoryLimitation.ARGUMENTS_MALFORMED_UNICODE
                        return None
                    else:
                        out.append(chr(code))
                else:
                    self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
                    return None
            else:
                # Strict JSON: raw U+0000..U+001F must be escaped.
                if ord(ch) < 0x20:
                    self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
                    return None
                out.append(ch)
                self._pos += 1
        decoded = "".join(out)
        # The exact canonical byte length is known BEFORE any
        # canonical construction: the per-argument cap and the shared
        # cumulative budget are both enforced before the copy.
        canon_len = self._canonical_length(decoded)
        if canon_len > self._max_canonical:
            self._error = CausalHistoryLimitation.ARGUMENTS_OVER_BOUND
            return None
        if not self._charge_canonical(canon_len):
            return None
        try:
            encoded = self._canonical_string(decoded)
        except (UnicodeEncodeError, ValueError):
            self._error = CausalHistoryLimitation.ARGUMENTS_MALFORMED_UNICODE
            return None
        self._key_text = decoded
        return encoded

    @staticmethod
    def _canonical_length(text: str) -> int:
        """Exact canonical byte length WITHOUT constructing the bytes
        (mirrors ``_canonical_string`` per character)."""
        total = 2  # the surrounding quotes
        for ch in text:
            code = ord(ch)
            if ch == '"' or ch == "\\" or code in (0x08, 0x0A, 0x0C, 0x0D, 0x09):
                total += 2
            elif code < 0x20:
                total += 6
            elif code < 0x80:
                total += 1
            elif code < 0x800:
                total += 2
            elif code < 0x10000:
                total += 3
            else:
                total += 4
        return total

    @staticmethod
    def _canonical_string(text: str) -> bytes:
        out = bytearray(b'"')
        for ch in text:
            code = ord(ch)
            if ch == '"':
                out += b'\\"'
            elif ch == "\\":
                out += b"\\\\"
            elif ch == "\b":
                out += b"\\b"
            elif ch == "\f":
                out += b"\\f"
            elif ch == "\n":
                out += b"\\n"
            elif ch == "\r":
                out += b"\\r"
            elif ch == "\t":
                out += b"\\t"
            elif code < 0x20:
                out += b"\\u%04x" % code
            else:
                out += ch.encode("utf-8")
        out += b'"'
        return bytes(out)

    def _literal_or_number(self) -> bytes | None:
        text = self._text
        n = len(text)
        start = self._pos
        if text.startswith("true", start):
            # Each literal's canonical bytes are charged exactly once
            # BEFORE retention (immutable constants are represented
            # canonical bytes too, not an accounting exemption).
            if not self._charge_canonical(4):
                return None
            self._pos = start + 4
            return b"true"
        if text.startswith("false", start):
            if not self._charge_canonical(5):
                return None
            self._pos = start + 5
            return b"false"
        if text.startswith("null", start):
            if not self._charge_canonical(4):
                return None
            self._pos = start + 4
            return b"null"
        # Strict JSON number grammar (no NaN/Infinity, no leading
        # zeros, no empty or lone-minus forms).
        pos = start
        if pos < n and text[pos] == "-":
            pos += 1
        if pos >= n or not (text[pos].isascii() and text[pos].isdigit()):
            self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
            return None
        if text[pos] == "0":
            pos += 1
        else:
            while pos < n and text[pos].isascii() and text[pos].isdigit():
                pos += 1
        is_float = False
        if pos < n and text[pos] == ".":
            is_float = True
            pos += 1
            if pos >= n or not (text[pos].isascii() and text[pos].isdigit()):
                self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
                return None
            while pos < n and text[pos].isascii() and text[pos].isdigit():
                pos += 1
        if pos < n and text[pos] in "eE":
            is_float = True
            pos += 1
            if pos < n and text[pos] in "+-":
                pos += 1
            if pos >= n or not (text[pos].isascii() and text[pos].isdigit()):
                self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
                return None
            while pos < n and text[pos].isascii() and text[pos].isdigit():
                pos += 1
        token = text[start:pos]
        if is_float:
            number = float(token)
            # JSON has no infinity/NaN: a finite lexeme that does not
            # convert to a finite float (e.g. 1e99999 -> inf) is
            # malformed, never canonically rendered.
            if not math.isfinite(number):
                self._error = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
                return None
            # A finite double repr is a fixed bounded ASCII constant
            # (at most 25 bytes), not a crossing copy.
            canonical_text = repr(number)
        else:
            # The strict integer grammar is already canonical (no
            # leading zeros, no plus sign); the lone lexeme "-0" is
            # the only non-canonical spelling.
            if token == "-0":
                token = "0"
            canonical_text = token
        # The numeric canonical bytes are charged BEFORE encode and
        # retention (per-argument cap first, then the shared ledger).
        if not self._charge_canonical(len(canonical_text)):
            return None
        self._pos = pos
        return canonical_text.encode("ascii")


def _utf8_byte_length(text: str) -> int:
    """Exact UTF-8 byte length WITHOUT allocating the encoding.

    A lone surrogate is counted as its 3-byte would-be encoding here;
    callers refuse lone surrogates separately (they are not valid
    UTF-8), so no encoding allocation is ever made.
    """
    total = 0
    for ch in text:
        code = ord(ch)
        if code < 0x80:
            total += 1
        elif code < 0x800:
            total += 2
        elif code < 0x10000:
            total += 3
        else:
            total += 4
    return total


def canonicalize_tool_arguments(
    tool_name: str,
    arguments: str,
    *,
    max_argument_bytes: int,
    max_total_argument_bytes: int,
    max_argument_nodes: int,
    max_argument_depth: int,
    charge_total: Callable[[int], bool],
    work: Callable[[], bool],
) -> ArgumentFingerprintResult:
    """The ONE bounded canonical argument-fingerprint recipe.

    Strict supported JSON OBJECT arguments; canonical sorted-key
    serialization; normal JSON whitespace and escape equivalence;
    EXACT string values (no shell normalization).  The input bytes are
    bounded BEFORE the parse; node/depth bounds are enforced during
    the single parse walk; the canonical bytes are bounded BEFORE any
    hash or copy.  ``charge_total`` is called with the input bytes
    (before the parse) and with EVERY canonical byte piece as it is
    constructed (before each crossing copy, before the hash) against
    the cumulative per-transition allowance; ``work`` is charged
    before every node/key visit.  Duplicate object keys, nonfinite
    numbers, malformed Unicode and any other non-strict JSON are fixed
    limitations, never guessed matching.  The raw arguments are never
    encoded nor retained.
    """
    # Preflight the raw input length BEFORE any encoding allocation:
    # every UTF-8 character is at least one byte, so an over-bound
    # character count is an over-bound byte count (the raw input is
    # neither encoded nor retained on this refusal).
    if len(arguments) > max_argument_bytes:
        return ArgumentFingerprintResult(
            reason=CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,
            input_bytes=0,
        )
    # Lone surrogates are not valid UTF-8: refused BEFORE any
    # encoding allocation (the raw input is neither encoded nor
    # retained).
    if any(0xD800 <= ord(ch) <= 0xDFFF for ch in arguments):
        return ArgumentFingerprintResult(
            reason=CausalHistoryLimitation.ARGUMENTS_MALFORMED_UNICODE,
            input_bytes=0,
        )
    # Exact UTF-8 byte length WITHOUT allocating the encoding: a
    # multibyte input whose character count fits can still exceed the
    # byte cap, and the crossing copy is never made.
    input_bytes = _utf8_byte_length(arguments)
    if input_bytes > max_argument_bytes:
        return ArgumentFingerprintResult(
            reason=CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,
            input_bytes=input_bytes,
        )
    if not charge_total(input_bytes):
        return ArgumentFingerprintResult(
            reason=CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,
            input_bytes=input_bytes,
        )
    walk = _ArgWalk(
        arguments,
        max_nodes=max_argument_nodes,
        max_depth=max_argument_depth,
        max_canonical=max_argument_bytes,
        charge_total=charge_total,
        work=work,
    )
    canonical = walk.value(0)
    if walk._error is not None or canonical is None:
        return ArgumentFingerprintResult(
            reason=(
                walk._error
                if walk._error is not None
                else CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
            ),
            input_bytes=input_bytes,
            node_count=walk._nodes,
            max_depth=walk._max_depth_seen,
        )
    # The top level must be a strict JSON object.
    if not canonical.startswith(b"{"):
        return ArgumentFingerprintResult(
            reason=CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED,
            input_bytes=input_bytes,
            node_count=walk._nodes,
            max_depth=walk._max_depth_seen,
        )
    walk._skip_ws()
    if walk._pos != len(walk._text):
        return ArgumentFingerprintResult(
            reason=CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED,
            input_bytes=input_bytes,
            node_count=walk._nodes,
            max_depth=walk._max_depth_seen,
        )
    # The canonical bytes were charged to the shared cumulative
    # ledger incrementally during the walk (before each crossing
    # copy); the final length check is a retained invariant.
    canonical_bytes = len(canonical)
    if canonical_bytes > max_argument_bytes:
        return ArgumentFingerprintResult(
            reason=CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,
            input_bytes=input_bytes,
            canonical_bytes=canonical_bytes,
            node_count=walk._nodes,
            max_depth=walk._max_depth_seen,
        )
    fingerprint = _sha256_hex(
        _ARGUMENTS_ENCODING_PREFIX + tool_name.encode("utf-8") + b"\x00" + canonical
    )
    return ArgumentFingerprintResult(
        fingerprint=fingerprint,
        input_bytes=input_bytes,
        canonical_bytes=canonical_bytes,
        node_count=walk._nodes,
        max_depth=walk._max_depth_seen,
    )


def tool_argument_fingerprint(
    tool_name: str, arguments: str, result: ArgumentFingerprintResult
) -> str | None:
    """The retained fingerprint for a successful recipe outcome.

    Only the digest is retained in state records; the raw arguments
    and the canonical bytes are not.
    """
    if not result.ok:
        return None
    return result.fingerprint


# --- The history scope (namespace) ---------------------------------------


def _canonical_history_fields(
    principal: str,
    session: str,
    repository: str,
    route: str,
    model_identity: str,
    config_fingerprint: str,
    workspace: str,
    mode: str,
    admission_version: str,
    observation_version: str,
    graph_version: str,
    reference_version: str,
    proof_version: str,
    admission_namespace_key: str,
    admission_scoped_key: str,
    lineage_id: str,
    history_version: str,
    arguments_version: str,
    history_bounds: HistoryBounds,
    bounds: BundleAdmissionBounds,
    proof_bounds: BundleProofBounds,
    graph_bounds: GraphBounds,
    observation_bounds: ObservationBounds,
) -> bytes:
    payload = [
        principal,
        session,
        repository,
        route,
        model_identity,
        config_fingerprint,
        workspace,
        mode,
        admission_version,
        observation_version,
        graph_version,
        reference_version,
        proof_version,
        admission_namespace_key,
        admission_scoped_key,
        lineage_id,
        history_version,
        arguments_version,
        json.dumps(history_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(proof_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(graph_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(
            observation_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        ),
    ]
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


class CausalHistoryNamespace(_GraphFrozen):
    """Explicit trusted INTERNAL causal-history scope.

    The scope binds the ACTUAL accepted 018-c bundle-admission
    namespace: its actual identity/config/bounds/versions fields AND
    its BOTH 64-hex scope keys (revalidated against the actual fields
    -- the opaque keys alone are not enough), plus the explicit opaque
    history-lineage ID, the NEW history bounds and the two history
    versions.  ``history_key`` is recomputed from every actual field on
    every construction (factory and direct) and a mismatch is refused;
    ``state_scoped_key = sha256(history_key + "\\0" + workspace)``
    binds the evidenced root scope.

    Object construction is NOT authentication: this is an internal
    trusted boundary, never a public body/header authority path.  No
    anonymous fallback and no cross-scope reuse.  Errors and
    operational reprs suppress all private ID/source/marker/identity
    values.
    """

    principal: str = Field(min_length=1, max_length=256)
    session: str = Field(min_length=1, max_length=256)
    repository: str = Field(min_length=1, max_length=256)
    route: str = Field(min_length=1, max_length=64)
    model_identity: str = Field(min_length=1, max_length=256)
    config_fingerprint: str
    workspace: str
    mode: AdmissionMode
    admission_version: str = ADMISSION_CONTRACT_VERSION
    observation_version: str = OBSERVER_VERSION
    graph_version: str = GRAPH_CONTRACT_VERSION
    reference_version: str = REFERENCE_GRAMMAR
    proof_version: str = BUNDLE_PROOF_CONTRACT_VERSION
    bounds: BundleAdmissionBounds = Field(default_factory=BundleAdmissionBounds)
    proof_bounds: BundleProofBounds = Field(default_factory=BundleProofBounds)
    graph_bounds: GraphBounds = Field(default_factory=GraphBounds)
    observation_bounds: ObservationBounds = Field(default_factory=ObservationBounds)
    admission_namespace_key: str
    admission_scoped_key: str
    lineage_id: str = Field(min_length=1, max_length=128)
    history_version: str = CAUSAL_HISTORY_CONTRACT_VERSION
    arguments_version: str = CAUSAL_ARGUMENTS_JSON_VERSION
    history_bounds: HistoryBounds = Field(default_factory=HistoryBounds)
    history_key: str
    state_scoped_key: str

    @field_validator("principal", "session", "repository", "route", "model_identity")
    @classmethod
    def _v_identity_text(cls, value: str, info: object) -> str:
        field_name = getattr(info, "field_name", "field") or "field"
        limit = 64 if field_name == "route" else 256
        if not 1 <= len(value) <= limit:
            raise _fixed(f"{field_name} must be 1..{limit} characters")
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise _fixed(f"{field_name} must be valid UTF-8") from None
        return value

    @field_validator("config_fingerprint", "workspace")
    @classmethod
    def _v_text(cls, value: str, info: object) -> str:
        field_name = getattr(info, "field_name", "field") or "field"
        if not 1 <= len(value) <= 1024:
            raise _fixed(f"{field_name} must be 1..1024 characters")
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise _fixed(f"{field_name} must be valid UTF-8") from None
        return value

    @field_validator(
        "admission_namespace_key",
        "admission_scoped_key",
        "history_key",
        "state_scoped_key",
    )
    @classmethod
    def _v_hex64(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "key") or "key")

    @field_validator(
        "admission_version",
        "observation_version",
        "graph_version",
        "reference_version",
        "proof_version",
        "history_version",
        "arguments_version",
    )
    @classmethod
    def _v_version(cls, value: str, info: object) -> str:
        field_name = getattr(info, "field_name", "version") or "version"
        if not 1 <= len(value) <= 128 or any(c.isspace() for c in value):
            raise _fixed(f"{field_name} must be 1..128 non-space characters")
        return value

    @model_validator(mode="after")
    def _v_scope_keys(self) -> CausalHistoryNamespace:
        # Revalidate the ACTUAL accepted 018-c scope on EVERY
        # construction (factory and direct): the actual admission
        # field constraints and every nested bound set are rerun
        # through the real field/model validators -- a forged nested
        # model copy carries no acquired authority and the opaque
        # 64-hex keys alone are not enough.
        try:
            BundleAdmissionNamespace.model_validate(
                {
                    "principal": self.principal,
                    "session": self.session,
                    "repository": self.repository,
                    "route": self.route,
                    "model_identity": self.model_identity,
                    "config_fingerprint": self.config_fingerprint,
                    "workspace": self.workspace,
                    "mode": self.mode.value,
                    "admission_version": self.admission_version,
                    "observation_version": self.observation_version,
                    "graph_version": self.graph_version,
                    "reference_version": self.reference_version,
                    "proof_version": self.proof_version,
                    "bounds": self.bounds.model_dump(),
                    "proof_bounds": self.proof_bounds.model_dump(),
                    "graph_bounds": self.graph_bounds.model_dump(),
                    "observation_bounds": self.observation_bounds.model_dump(),
                    "namespace_key": self.admission_namespace_key,
                    "scoped_key": self.admission_scoped_key,
                }
            )
            HistoryBounds.model_validate(self.history_bounds.model_dump())
        except Exception:
            raise _fixed(
                "admission scope or history bounds failed the actual accepted validation"
            ) from None
        # Then: its two 64-hex keys must equal the recomputation from
        # its actual fields.
        try:
            expected_admission = _canonical_namespace_fields(
                self.principal,
                self.session,
                self.repository,
                self.route,
                self.model_identity,
                self.config_fingerprint,
                self.admission_version,
                self.graph_version,
                self.reference_version,
                self.proof_version,
                self.observation_version,
                str(self.mode),
                self.bounds,
                self.proof_bounds,
                self.graph_bounds,
                self.observation_bounds,
            )
        except Exception:
            raise _fixed("admission scope fields are not canonical") from None
        expected_ns_key = _sha256_hex(expected_admission)
        expected_scoped_key = _sha256_hex((expected_ns_key + "\0" + self.workspace).encode("utf-8"))
        if (
            self.admission_namespace_key != expected_ns_key
            or self.admission_scoped_key != expected_scoped_key
        ):
            raise _fixed("admission scope keys do not match the actual fields")
        # The workspace must be the evidenced canonical root scope.
        workspace = validate_workspace(self.workspace, self.graph_bounds.max_path_bytes)
        if workspace is None or workspace != self.workspace:
            raise _fixed("workspace is not the evidenced canonical root scope")
        expected_history = _sha256_hex(
            _canonical_history_fields(
                self.principal,
                self.session,
                self.repository,
                self.route,
                self.model_identity,
                self.config_fingerprint,
                self.workspace,
                str(self.mode),
                self.admission_version,
                self.observation_version,
                self.graph_version,
                self.reference_version,
                self.proof_version,
                self.admission_namespace_key,
                self.admission_scoped_key,
                self.lineage_id,
                self.history_version,
                self.arguments_version,
                self.history_bounds,
                self.bounds,
                self.proof_bounds,
                self.graph_bounds,
                self.observation_bounds,
            )
        )
        if self.history_key != expected_history:
            raise _fixed("history_key does not match the actual scope fields")
        expected_state_scoped = _sha256_hex(
            (self.history_key + "\0" + self.workspace).encode("utf-8")
        )
        if self.state_scoped_key != expected_state_scoped:
            raise _fixed("state_scoped_key does not match history_key + workspace")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CausalHistoryNamespace(principal={PRIVATE_ID_PLACEHOLDER}, "
            f"session={PRIVATE_ID_PLACEHOLDER}, "
            f"repository={PRIVATE_ID_PLACEHOLDER}, "
            f"route={PRIVATE_ID_PLACEHOLDER}, "
            f"model_identity={PRIVATE_ID_PLACEHOLDER}, "
            f"config_fingerprint={PRIVATE_ID_PLACEHOLDER}, "
            f"workspace={PRIVATE_ID_PLACEHOLDER}, "
            f"mode={self.mode!r}, "
            f"lineage_id={PRIVATE_ID_PLACEHOLDER}, "
            f"history_version={self.history_version!r}, "
            f"arguments_version={self.arguments_version!r}, "
            f"history_bounds={self.history_bounds!r}, "
            f"bounds={self.bounds!r}, "
            f"proof_bounds={self.proof_bounds!r}, "
            f"graph_bounds={self.graph_bounds!r}, "
            f"observation_bounds={self.observation_bounds!r}, "
            f"admission_namespace_key={self.admission_namespace_key!r}, "
            f"admission_scoped_key={self.admission_scoped_key!r}, "
            f"history_key={self.history_key!r}, "
            f"state_scoped_key={self.state_scoped_key!r})"
        )

    __str__ = __repr__


def _revalidate_admission(
    admission: BundleAdmissionNamespace,
) -> BundleAdmissionNamespace:
    """Re-run the ACTUAL accepted 018-c admission validators.

    A forged nested model copy (``model_copy``/``model_construct``)
    carries no acquired authority: its field values and nested bound
    sets are revalidated through the real field/model validators, and
    the opaque 64-hex keys alone are not enough.
    """
    try:
        return BundleAdmissionNamespace.model_validate(admission.model_dump())
    except Exception:
        raise _fixed(
            "admission namespace failed the actual accepted admission validation"
        ) from None


def _revalidate_history_bounds(bounds: HistoryBounds) -> HistoryBounds:
    try:
        return HistoryBounds.model_validate(bounds.model_dump())
    except Exception:
        raise _fixed("history bounds failed the actual history-bounds validation") from None


def make_causal_history_namespace(
    admission: BundleAdmissionNamespace,
    lineage_id: str,
    *,
    bounds: HistoryBounds | None = None,
) -> CausalHistoryNamespace:
    """Factory for a causal-history scope over the ACTUAL accepted
    018-c admission namespace.

    The admission namespace's actual fields AND both 64-hex keys are
    bound into the recomputed history scope keys; a forged, stale or
    borrowed key pair is refused.  ``lineage_id`` is the explicit
    opaque history-lineage ID (distinct from any future
    compiler/cache epoch).  Not authentication.
    """
    if not 1 <= len(lineage_id) <= 128 or any(c.isspace() for c in lineage_id):
        raise _fixed("lineage_id must be 1..128 non-space characters")
    try:
        lineage_id.encode("utf-8")
    except UnicodeEncodeError:
        raise _fixed("lineage_id must be valid UTF-8") from None
    # The ACTUAL accepted admission scope and the NEW history bounds
    # are revalidated BEFORE any key computation (forged nested model
    # copies are refused; the opaque keys alone are not enough).
    admission = _revalidate_admission(admission)
    effective_bounds = _revalidate_history_bounds(HistoryBounds() if bounds is None else bounds)
    history_key = _sha256_hex(
        _canonical_history_fields(
            admission.principal,
            admission.session,
            admission.repository,
            admission.route,
            admission.model_identity,
            admission.config_fingerprint,
            admission.workspace,
            admission.mode.value,
            admission.admission_version,
            admission.observation_version,
            admission.graph_version,
            admission.reference_version,
            admission.proof_version,
            admission.namespace_key,
            admission.scoped_key,
            lineage_id,
            CAUSAL_HISTORY_CONTRACT_VERSION,
            CAUSAL_ARGUMENTS_JSON_VERSION,
            effective_bounds,
            admission.bounds,
            admission.proof_bounds,
            admission.graph_bounds,
            admission.observation_bounds,
        )
    )
    state_scoped_key = _sha256_hex((history_key + "\0" + admission.workspace).encode("utf-8"))
    return CausalHistoryNamespace(
        principal=admission.principal,
        session=admission.session,
        repository=admission.repository,
        route=admission.route,
        model_identity=admission.model_identity,
        config_fingerprint=admission.config_fingerprint,
        workspace=admission.workspace,
        mode=admission.mode,
        admission_version=admission.admission_version,
        observation_version=admission.observation_version,
        graph_version=admission.graph_version,
        reference_version=admission.reference_version,
        proof_version=admission.proof_version,
        bounds=admission.bounds,
        proof_bounds=admission.proof_bounds,
        graph_bounds=admission.graph_bounds,
        observation_bounds=admission.observation_bounds,
        admission_namespace_key=admission.namespace_key,
        admission_scoped_key=admission.scoped_key,
        lineage_id=lineage_id,
        history_bounds=effective_bounds,
        history_key=history_key,
        state_scoped_key=state_scoped_key,
    )


# --- Immutable state records (018-d kernel) ---------------------------------


def _validate_call_id(value: str) -> str:
    if not 1 <= len(value) <= 256 or any(c.isspace() for c in value):
        raise _fixed("call_id must be 1..256 non-space characters")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise _fixed("call_id must be valid UTF-8") from None
    return value


def _validate_tool_name(value: str) -> str:
    if not 1 <= len(value) <= 256 or any(c.isspace() for c in value):
        raise _fixed("tool_name must be 1..256 non-space characters")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise _fixed("tool_name must be valid UTF-8") from None
    return value


def _validate_endpoint(value: str) -> str:
    if value not in ("responses", "chat"):
        raise _fixed("endpoint must be an explicit validated endpoint")
    return value


def _validate_frontier_member(value: str) -> str:
    if value == CAUSAL_ROOT_FACT:
        return value
    return _check_hex64(value, "frontier member")


def _validate_workspace_label(value: str) -> str:
    if not 1 <= len(value) <= 1024 or not value.startswith("/"):
        raise _fixed("workspace must be a 1..1024 absolute POSIX path")
    if any(ord(c) < 0x20 or ord(c) == 0x7F or c.isspace() for c in value):
        raise _fixed("workspace must not contain control characters")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise _fixed("workspace must be valid UTF-8") from None
    return value


class RootAnchor(_GraphFrozen):
    """Evidenced root anchor, retained once per state.

    ``root_text`` is the NARROWLY EXTRACTED exact root source body
    (no transport envelope or env tail); ``root_digest`` and
    ``source_byte_length`` are derived from it and must match
    exactly.  ``workspace`` is the normalized absolute POSIX scope
    root; ``first_request_index`` is the original position of the
    request that first evidenced the root.  ``location`` plus the
    half-open character spans retain the ORIGINAL RootOccurrence
    provenance (where the exact bytes were extracted from, into the
    exact decoded carrier string) -- provenance, not envelope
    content.
    """

    root_text: str
    root_digest: str
    workspace: str
    first_request_index: int = Field(ge=0)
    source_byte_length: int = Field(ge=0)
    location: str
    content_span: CharSpan
    envelope_span: CharSpan | None = None

    @field_validator("root_digest")
    @classmethod
    def _v_root_digest(cls, value: str) -> str:
        return _check_hex64(value, "root_digest")

    @field_validator("workspace")
    @classmethod
    def _v_workspace(cls, value: str) -> str:
        return _validate_workspace_label(value)

    @field_validator("location")
    @classmethod
    def _v_location(cls, value: str) -> str:
        return _check_text(value, "location", 1024)

    @model_validator(mode="after")
    def _v_root_consistency(self) -> RootAnchor:
        if _sha256_hex(self.root_text.encode("utf-8")) != self.root_digest:
            raise _fixed("root_digest must equal the exact root text digest")
        if self.source_byte_length != len(self.root_text.encode("utf-8")):
            raise _fixed("source_byte_length must equal the exact root text bytes")
        if self.content_span.length != len(self.root_text):
            raise _fixed("content_span must cover the exact root text")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"RootAnchor(root_digest={self.root_digest!r}, "
            f"root_text='<protected {len(self.root_text)} chars>', "
            f"workspace={PRIVATE_ID_PLACEHOLDER}, "
            f"first_request_index={self.first_request_index}, "
            f"source_byte_length={self.source_byte_length}, "
            f"location={self.location!r}, "
            f"content_span={self.content_span!r}, "
            f"envelope_span={self.envelope_span!r})"
        )

    __str__ = __repr__


class IssuedCall(_GraphFrozen):
    """Immutable trusted INTERNAL issuance binding.

    Issuance is NOT acquisition or success: only a subsequently
    paired complete original read proof creates a completed read
    occurrence.  The binding is the endpoint family, tool name and
    canonical argument fingerprint (raw arguments are never
    retained); ``parent_frontier`` is the frozen canonical (sorted,
    deduplicated) set of known facts the call was issued under --
    the root-anchor fact and/or completed occurrence IDs (redundant
    ancestors allowed; reduction removes only proven ancestors).
    """

    call_id: str
    endpoint: str
    tool_name: str
    argument_fingerprint: str
    parent_frontier: tuple[str, ...] = Field(min_length=1)

    @field_validator("call_id")
    @classmethod
    def _v_call_id(cls, value: str) -> str:
        return _validate_call_id(value)

    @field_validator("endpoint")
    @classmethod
    def _v_endpoint(cls, value: str) -> str:
        return _validate_endpoint(value)

    @field_validator("tool_name")
    @classmethod
    def _v_tool_name(cls, value: str) -> str:
        return _validate_tool_name(value)

    @field_validator("argument_fingerprint")
    @classmethod
    def _v_argument_fingerprint(cls, value: str) -> str:
        return _check_hex64(value, "argument_fingerprint")

    @field_validator("parent_frontier")
    @classmethod
    def _v_parent_frontier(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        members = tuple(_validate_frontier_member(m) for m in value)
        if tuple(sorted(set(members))) != members:
            raise _fixed("parent_frontier must be canonical sorted-deduplicated")
        return members

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"IssuedCall(call_id={PRIVATE_ID_PLACEHOLDER}, "
            f"endpoint={self.endpoint!r}, tool_name={self.tool_name!r}, "
            f"argument_fingerprint={self.argument_fingerprint!r}, "
            f"parent_frontier={len(self.parent_frontier)} members)"
        )

    __str__ = __repr__


class CompletedReadOccurrence(_GraphFrozen):
    """One retained completed original read occurrence.

    The original ``BundleProof`` is retained VERBATIM (its own
    operational repr is privacy-safe); the binding fields duplicate
    the issuance identity for cross-checking.  ``anchored`` marks
    whether the immutable call binding has been evidenced through a
    trusted receipt; an unanchored complete occurrence is evidence
    only and carries NO temporal edge.
    """

    occurrence_id: str
    call_id: str
    endpoint: str
    tool_name: str
    argument_fingerprint: str
    proof: BundleProof
    anchored: bool = False

    @field_validator("occurrence_id")
    @classmethod
    def _v_occurrence_id(cls, value: str) -> str:
        return _check_hex64(value, "occurrence_id")

    @field_validator("call_id")
    @classmethod
    def _v_call_id(cls, value: str) -> str:
        return _validate_call_id(value)

    @field_validator("endpoint")
    @classmethod
    def _v_endpoint(cls, value: str) -> str:
        return _validate_endpoint(value)

    @field_validator("tool_name")
    @classmethod
    def _v_tool_name(cls, value: str) -> str:
        return _validate_tool_name(value)

    @field_validator("argument_fingerprint")
    @classmethod
    def _v_argument_fingerprint(cls, value: str) -> str:
        return _check_hex64(value, "argument_fingerprint")

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CompletedReadOccurrence(occurrence_id={self.occurrence_id!r}, "
            f"call_id={PRIVATE_ID_PLACEHOLDER}, "
            f"endpoint={self.endpoint!r}, tool_name={self.tool_name!r}, "
            f"argument_fingerprint={self.argument_fingerprint!r}, "
            f"proof=BundleProof(kind={self.proof.kind!r}, "
            f"source_digest={self.proof.source_digest!r}, "
            f"source_byte_length={self.proof.source_byte_length}), "
            f"anchored={self.anchored})"
        )

    __str__ = __repr__


class ResultFingerprintRecord(_GraphFrozen):
    """One immutable per-call result fingerprint record.

    Selected evidenced result values plus completion facts -- never
    credential-bearing wrappers.  Unique per call identity: the same
    call identity with a changed result fingerprint is a typed
    conflict in the state machine, not a second record.  A pending
    process is tracked by ``complete=False`` records.

    A pending (incomplete) record additionally binds the SELECTED
    immutable pending result/piece facts: the exact non-complete
    ``ProcessOutcome`` and, per observed piece in causal order, the
    exact original output-slice fact ``(piece_index, char_length,
    byte_length, digest)`` where ``digest`` is the sha256 of the EXACT
    original carrier-span bytes (measured/hashed from the original
    span before retention; raw piece text and whole
    credential-bearing wrappers are never retained -- lengths alone
    are NOT byte identity).  A genuine 017-accepted poll
    extension (the selected facts so far unchanged, new polls
    appended) may extend ONE record; mutated already-seen pending
    bytes are a typed conflict in the state machine.

    A COMPLETED record retains the same selected per-call/piece
    facts for its complete proof (the exact original piece carriers).
    Immutable result frames are distinguished from the aggregate
    completion: the initial running result never changes, and a
    later final result belongs to its own poll call -- so a re-
    observed frame that is the EXACT old prefix of the retained
    facts is an idempotent no-op (the completed state is preserved),
    while changed or extended already-seen bytes are a typed
    conflict.

    The selected immutable process-session association fact is
    retained as ``session_digest``: the sha256 of the exact observed
    chain session ID (a native process chain established by its
    initial running frame) or the fixed no-session marker (the
    legacy read surface and the already-exited single-final shape,
    which carries no session).  Whole-body or source-digest equality
    alone cannot prove per-call result equality: a changed session
    association under the same call identity is a typed conflict in
    the state machine.  The raw session value is never retained.

    Every retained piece additionally binds its ACTUAL producing
    call's observed immutable association (``piece_call_bindings``:
    the piece's call ID plus the call's endpoint, tool name and
    canonical argument fingerprint, aligned by piece index with the
    piece facts).  A poll's ID is therefore retained observed
    binding evidence, not a fabricated issuance: reusing an observed
    poll ID for a different call is a typed conflict, while the
    association never confers frontier, success or source
    acquisition.
    """

    call_id: str
    endpoint: str
    tool_name: str
    argument_fingerprint: str
    result_fingerprint: str
    complete: bool
    first_request_index: int = Field(ge=0)
    #: The selected immutable session-association fact (hex64): the
    #: digest of the exact observed chain session ID, or the fixed
    #: no-session marker for surfaces/shapes that carry no session.
    session_digest: str
    #: The exact non-complete process outcome; non-None iff
    #: ``complete is False``.
    pending_outcome: ProcessOutcome | None = None
    #: The selected immutable per-call output-slice facts
    #: ``(piece_index, char_length, byte_length, exact original span
    #: digest)`` in causal order: the observed pending slices while
    #: incomplete, and the complete proof's exact original piece
    #: facts once complete (the retained facts that an old-prefix
    #: re-observation must match).
    piece_facts: tuple[tuple[int, int, int, str], ...] = ()
    #: The selected immutable producing-call association fact for
    #: EVERY retained piece, aligned by piece index with
    #: ``piece_facts``: ``(call_id, endpoint, tool_name,
    #: argument_fingerprint)`` of the actual observed call that
    #: produced that original carrier (the read's own call for its
    #: own piece, the causally associated poll for a poll piece)
    #: under the SAME canonical argument recipe.  These are OBSERVED
    #: facts, never a fabricated issuance or placeholder: raw
    #: arguments are never retained (the canonical digest only).  A
    #: reused piece-producing call ID under a different immutable
    #: binding is a typed conflict in the state machine.
    piece_call_bindings: tuple[tuple[str, str, str, str], ...] = ()
    #: The selected immutable per-piece COMPLETION fact, aligned by
    #: piece index with ``piece_facts``: the producing frame's
    #: terminal status (its wrapper's exact exit code; ``None`` when
    #: the frame is a running/non-terminal frame or carries no
    #: completion fact, as on the legacy read surface).  A producing
    #: call's result bytes AND completion status are both immutable
    #: under its identity: a same-length body with a changed frame
    #: status is a typed conflict.  The status is compared without
    #: the raw wrapper and without the proof-local piece coordinate
    #: (which is provenance, never a global identity).
    piece_completion: tuple[int | None, ...] = ()

    @field_validator("call_id")
    @classmethod
    def _v_call_id(cls, value: str) -> str:
        return _validate_call_id(value)

    @field_validator("endpoint")
    @classmethod
    def _v_endpoint(cls, value: str) -> str:
        return _validate_endpoint(value)

    @field_validator("tool_name")
    @classmethod
    def _v_tool_name(cls, value: str) -> str:
        return _validate_tool_name(value)

    @field_validator("argument_fingerprint")
    @classmethod
    def _v_argument_fingerprint(cls, value: str) -> str:
        return _check_hex64(value, "argument_fingerprint")

    @field_validator("result_fingerprint")
    @classmethod
    def _v_result_fingerprint(cls, value: str) -> str:
        return _check_hex64(value, "result_fingerprint")

    @field_validator("session_digest")
    @classmethod
    def _v_session_digest(cls, value: str) -> str:
        return _check_hex64(value, "session_digest")

    @field_validator("piece_facts")
    @classmethod
    def _v_piece_facts(
        cls, value: tuple[tuple[int, int, int, str], ...]
    ) -> tuple[tuple[int, int, int, str], ...]:
        for index, (piece_index, char_length, byte_length, digest) in enumerate(value):
            if piece_index != index:
                raise _fixed("pending piece facts keep causal piece order")
            if char_length < 0 or byte_length < 0:
                raise _fixed("pending piece lengths must be nonnegative")
            _check_hex64(digest, "pending piece digest")
        return value

    @field_validator("piece_call_bindings")
    @classmethod
    def _v_piece_call_bindings(
        cls, value: tuple[tuple[str, str, str, str], ...]
    ) -> tuple[tuple[str, str, str, str], ...]:
        for call_id, endpoint, tool_name, argument_fingerprint in value:
            # A piece-producing call may carry the exact empty no-ID
            # state (it never matches anything); non-empty IDs keep
            # the bounded non-space law.
            if not 0 <= len(call_id) <= 256 or any(c.isspace() for c in call_id):
                raise _fixed("a piece call binding carries a bounded call ID")
            _validate_endpoint(endpoint)
            _validate_tool_name(tool_name)
            _check_hex64(argument_fingerprint, "piece call binding fingerprint")
        return value

    @field_validator("piece_completion")
    @classmethod
    def _v_piece_completion(
        cls, value: tuple[int | None, ...]
    ) -> tuple[int | None, ...]:
        for exit_code in value:
            if exit_code is None:
                continue
            if isinstance(exit_code, bool) or not isinstance(exit_code, int):
                raise _fixed("a piece completion fact is an exact exit code")
            if not -(2**31) <= exit_code <= 2**31 - 1:
                raise _fixed("a piece completion fact is a bounded exit code")
        return value

    @model_validator(mode="after")
    def _v_pending_consistency(self) -> ResultFingerprintRecord:
        if len(self.piece_call_bindings) != len(self.piece_facts):
            raise _fixed("piece call bindings align with the retained piece facts")
        if len(self.piece_completion) != len(self.piece_facts):
            raise _fixed("piece completion facts align with the retained piece facts")
        if self.complete:
            if self.pending_outcome is not None:
                raise _fixed("a complete record carries no pending facts")
            return self
        if self.pending_outcome not in (
            ProcessOutcome.RUNNING,
            ProcessOutcome.NONZERO_EXIT,
            ProcessOutcome.TRUNCATED,
        ):
            raise _fixed("an incomplete record carries its selected pending outcome")
        if not self.piece_facts:
            raise _fixed("an incomplete record retains its selected piece facts")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        pending_outcome = self.pending_outcome.value if self.pending_outcome is not None else None
        return (
            f"ResultFingerprintRecord(call_id={PRIVATE_ID_PLACEHOLDER}, "
            f"endpoint={self.endpoint!r}, tool_name={self.tool_name!r}, "
            f"argument_fingerprint={self.argument_fingerprint!r}, "
            f"result_fingerprint={self.result_fingerprint!r}, "
            f"complete={self.complete}, "
            f"first_request_index={self.first_request_index}, "
            f"session_digest={self.session_digest!r}, "
            f"pending_outcome={pending_outcome!r}, "
            f"piece_facts={len(self.piece_facts)}, "
            f"piece_call_bindings={len(self.piece_call_bindings)}, "
            f"piece_completion={len(self.piece_completion)})"
        )

    __str__ = __repr__


class ParentLink(_GraphFrozen):
    """One unique immediate parent edge over frozen completed
    occurrence evidence (``child`` <- ``parent``).

    ``parent`` is a completed occurrence ID or the root-anchor fact
    (root-parent evidence is retained and counted like any other
    frozen edge).  ``child`` is always a completed occurrence (the
    root anchor is never a child of a frozen edge).  Edges must
    follow the exact frozen issuance frontier of the child; that
    law is enforced by the bounded charged state validation.

    Siblings are never ordered from list or registration order;
    BEFORE/AFTER hold only through these frozen edges
    transitively, never from receipt or revision order.
    """

    child: str
    parent: str

    @field_validator("child")
    @classmethod
    def _v_child(cls, value: str) -> str:
        return _check_hex64(value, "child")

    @field_validator("parent")
    @classmethod
    def _v_parent(cls, value: str) -> str:
        if value == CAUSAL_ROOT_FACT:
            return value
        return _check_hex64(value, "parent")

    @model_validator(mode="after")
    def _v_self_link(self) -> ParentLink:
        # child is 64-hex and parent is 64-hex or the root fact, so
        # equality is exactly the impossible self-reference.
        if self.parent == self.child:
            raise _fixed("a parent link must not be self-referential")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return f"ParentLink(child={self.child!r}, parent={self.parent!r})"

    __str__ = __repr__


class CausalHistoryState(_GraphFrozen):
    """Immutable causal-history state for one history scope.

    ``revision`` is 0..MAX_REVISION; diagnostics are BOUNDED
    transition-result output, never a lifetime-growing state log.

    ``root=None`` IS the exact empty prior state (the typed
    bootstrap NO_ROOT refusal represents it verbatim; no anchor is
    ever fabricated to satisfy a nonoptional root).  Field-level
    shape is the record models' job; cross-record integrity
    (identities, binding matches against retained issuances,
    frozen-frontier edges, retention lengths, acyclicity) is
    enforced ONLY by the bounded charged
    ``validate_causal_history_state`` under the shared per-
    transition work ledger.
    """

    history_key: str
    revision: int = Field(ge=0, le=MAX_REVISION)
    root: RootAnchor | None = None
    issuances: tuple[IssuedCall, ...] = ()
    occurrences: tuple[CompletedReadOccurrence, ...] = ()
    results: tuple[ResultFingerprintRecord, ...] = ()
    parent_links: tuple[ParentLink, ...] = ()

    @field_validator("history_key")
    @classmethod
    def _v_history_key(cls, value: str) -> str:
        return _check_hex64(value, "history_key")

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CausalHistoryState(history_key={self.history_key!r}, "
            f"revision={self.revision}, root={self.root!r}, "
            f"issuances={len(self.issuances)}, "
            f"occurrences={len(self.occurrences)}, "
            f"results={len(self.results)}, "
            f"parent_links={len(self.parent_links)})"
        )

    __str__ = __repr__


def validate_causal_history_state(
    state: CausalHistoryState,
    bounds: HistoryBounds | None = None,
    work: Callable[[], bool] | None = None,
) -> CausalHistoryLimitation | None:
    """Bounded, charged cross-record integrity for one state.

    The ONE cross-record validation law: record models enforce
    field-level shape only; this function enforces retention and
    frontier lengths, identity uniqueness, observed-binding
    consistency (trusted AND unissued identities must stay mutually
    consistent -- a completed occurrence of an unknown call is
    retained evidence, never a reason to invent an issuance),
    anchored semantics (``anchored=True`` requires a matching
    trusted issuance; unanchored occurrences carry NO temporal
    edges; the stored edges of an anchored child are exactly the
    known-fact content of its complete frozen frontier -- no
    silently omitted incomparable parents), and acyclicity with ONE
    iterative whole-DAG pass.

    Length preflights run BEFORE any map/iteration/copy.  Every
    identity comparison, frontier-member validation and
    parent-link/ancestry edge visit charges ONE work unit BEFORE
    the visit: the supplied shared per-transition ``work`` ledger
    when present, and ALWAYS the local ``max_work_units`` ceiling
    (standalone use is never unbounded).  A refused charge stops
    with WORK_UNITS_OVER_BOUND before the crossing operation.
    Returns ``None`` when coherent, else the ONE fixed closed
    limitation (first refusal wins).
    """
    effective = HistoryBounds() if bounds is None else bounds
    # --- length preflight (before any map/iteration/copy) ---
    if len(state.issuances) > effective.max_issuances:
        return CausalHistoryLimitation.ISSUANCES_OVER_BOUND
    if len(state.occurrences) > effective.max_occurrences:
        return CausalHistoryLimitation.OCCURRENCES_OVER_BOUND
    if len(state.results) > effective.max_observed_results:
        return CausalHistoryLimitation.RESULTS_OVER_BOUND
    if len(state.parent_links) > effective.max_causal_links:
        return CausalHistoryLimitation.CAUSAL_LINKS_OVER_BOUND
    for issuance in state.issuances:
        if len(issuance.parent_frontier) > effective.max_frontier_members:
            return CausalHistoryLimitation.FRONTIER_OVER_BOUND

    # Local ceiling: standalone use is bounded even without a shared
    # ledger; the shared transition ledger (when supplied) is charged
    # for the same units.
    local_budget = effective.max_work_units
    local_spent = 0

    def unit() -> bool:
        nonlocal local_spent
        if local_spent + 1 > local_budget:
            return False
        local_spent += 1
        if work is None:
            return True
        return work()

    root_present = state.root is not None
    # --- issuance identities (charged per comparison attempt) ---
    issuance_bindings: dict[str, tuple[str, str, str, tuple[str, ...]]] = {}
    observed_bindings: dict[str, tuple[str, str, str]] = {}
    for issuance in state.issuances:
        if not unit():
            return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
        if issuance.call_id in issuance_bindings:
            return CausalHistoryLimitation.ISSUANCE_CONFLICT
        issuance_bindings[issuance.call_id] = (
            issuance.endpoint,
            issuance.tool_name,
            issuance.argument_fingerprint,
            issuance.parent_frontier,
        )
        observed_bindings[issuance.call_id] = (
            issuance.endpoint,
            issuance.tool_name,
            issuance.argument_fingerprint,
        )
    # --- occurrence identities, observed bindings, anchored law ---
    occurrence_ids: set[str] = set()
    occurrence_anchored: dict[str, bool] = {}
    for occurrence in state.occurrences:
        if not unit():
            return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
        if occurrence.occurrence_id in occurrence_ids:
            return CausalHistoryLimitation.ISSUANCE_CONFLICT
        occurrence_ids.add(occurrence.occurrence_id)
        occurrence_anchored[occurrence.occurrence_id] = occurrence.anchored
        binding = (
            occurrence.endpoint,
            occurrence.tool_name,
            occurrence.argument_fingerprint,
        )
        prev = observed_bindings.get(occurrence.call_id)
        if prev is not None:
            if not unit():
                return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
            if prev != binding:
                return CausalHistoryLimitation.ISSUANCE_CONFLICT
        else:
            observed_bindings[occurrence.call_id] = binding
        if occurrence.anchored:
            if not unit():
                return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
            if issuance_bindings.get(occurrence.call_id) is None:
                # a forged anchored flag: no trusted issuance to pair
                return CausalHistoryLimitation.RECEIPT_BINDING_MISMATCH
    # --- result identities + observed binding consistency ---
    result_calls: set[str] = set()
    producer_facts: dict[str, tuple[int | None, int, int, str, str]] = {}
    for result in state.results:
        if not unit():
            return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
        if result.call_id in result_calls:
            return CausalHistoryLimitation.RESULT_CONFLICT
        result_calls.add(result.call_id)
        binding = (
            result.endpoint,
            result.tool_name,
            result.argument_fingerprint,
        )
        prev = observed_bindings.get(result.call_id)
        if prev is not None:
            if not unit():
                return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
            if prev != binding:
                return CausalHistoryLimitation.RESULT_CONFLICT
        else:
            observed_bindings[result.call_id] = binding
        # Per-piece observed bindings (the poll calls of a retained
        # chain): the same immutable same-ID law, charged per binding.
        for bind_index, (pcid, pendpoint, ptool, pfp) in enumerate(
            result.piece_call_bindings
        ):
            if not unit():
                return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
            piece_binding = (pendpoint, ptool, pfp)
            prev = observed_bindings.get(pcid)
            if prev is not None:
                if not unit():
                    return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
                if prev != piece_binding:
                    return CausalHistoryLimitation.RESULT_CONFLICT
            else:
                observed_bindings[pcid] = piece_binding
            # The producing call's retained RESULT fact (the selected
            # completion status plus the exact original span byte
            # identity plus the evidenced initial-EXEC owner; the
            # proof-local piece coordinate is provenance, never a
            # global identity) is immutable across EVERY retained
            # chain of the state: the same poll ID under a different
            # initial EXEC is a conflict even when every byte,
            # status and session fact matches.
            if pcid:
                if not unit():
                    return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
                piece_fact = (
                    result.piece_completion[bind_index],
                    *result.piece_facts[bind_index][1:],
                    result.call_id,
                )
                prev_fact = producer_facts.get(pcid)
                if prev_fact is not None:
                    if prev_fact != piece_fact:
                        return CausalHistoryLimitation.RESULT_CONFLICT
                else:
                    producer_facts[pcid] = piece_fact
    # --- frontier members are known facts (charged per member) ---
    for issuance in state.issuances:
        for member in issuance.parent_frontier:
            if not unit():
                return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
            if member == CAUSAL_ROOT_FACT:
                if not root_present:
                    return CausalHistoryLimitation.FRONTIER_CONFLICT
                continue
            if member not in occurrence_ids:
                return CausalHistoryLimitation.FRONTIER_CONFLICT
    # --- parent edges follow the exact frozen issuance frontiers ---
    frontier_by_occurrence: dict[str, tuple[str, ...]] = {}
    for occurrence in state.occurrences:
        bound = issuance_bindings.get(occurrence.call_id)
        if bound is not None:
            frontier_by_occurrence[occurrence.occurrence_id] = bound[3]
    seen_pairs: set[tuple[str, str]] = set()
    stored_parents: dict[str, set[str]] = {}
    for link in state.parent_links:
        if not unit():
            return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
        if link.child not in occurrence_ids:
            return CausalHistoryLimitation.FRONTIER_CONFLICT
        if not unit():
            return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
        if link.parent != CAUSAL_ROOT_FACT:
            if link.parent not in occurrence_ids:
                return CausalHistoryLimitation.FRONTIER_CONFLICT
        elif not root_present:
            return CausalHistoryLimitation.FRONTIER_CONFLICT
        if not unit():
            return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
        # unanchored occurrences carry NO temporal edges
        if not occurrence_anchored.get(link.child, False):
            return CausalHistoryLimitation.FRONTIER_CONFLICT
        frontier = frontier_by_occurrence.get(link.child)
        if frontier is None:
            # a child without a retained issuance has no frozen frontier
            return CausalHistoryLimitation.FRONTIER_CONFLICT
        # charged per ACTUAL comparison, not per tuple scan
        parent_in_frontier = False
        for member in frontier:
            if not unit():
                return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
            if member == link.parent:
                parent_in_frontier = True
                break
        if not parent_in_frontier:
            return CausalHistoryLimitation.FRONTIER_CONFLICT
        if not unit():
            return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
        pair = (link.child, link.parent)
        if pair in seen_pairs:
            return CausalHistoryLimitation.FRONTIER_CONFLICT
        seen_pairs.add(pair)
        stored_parents.setdefault(link.child, set()).add(link.parent)
    # --- anchored children retain the COMPLETE frozen frontier ---
    # (every frontier member is already a known fact here, so every
    # member must be a stored edge; no silent incomparability)
    for occurrence in state.occurrences:
        if not occurrence.anchored:
            continue
        bound = issuance_bindings.get(occurrence.call_id)
        if bound is None:
            continue  # already refused as a forged anchored flag
        stored = stored_parents.get(occurrence.occurrence_id)
        for member in bound[3]:
            if not unit():
                return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
            if stored is None or member not in stored:
                return CausalHistoryLimitation.FRONTIER_CONFLICT
    # --- ONE iterative whole-DAG acyclicity pass (Kahn, charged) ---
    in_degree: dict[str, int] = {}
    children_of: dict[str, list[str]] = {}
    nodes: set[str] = set()
    for link in state.parent_links:
        if not unit():
            return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
        nodes.add(link.child)
        nodes.add(link.parent)
        in_degree[link.child] = in_degree.get(link.child, 0) + 1
        children_of.setdefault(link.parent, []).append(link.child)
    for node in nodes:
        in_degree.setdefault(node, 0)
    queue: list[str] = [node for node, degree in in_degree.items() if degree == 0]
    processed = 0
    while queue:
        node = queue.pop()
        processed += 1
        for child in children_of.get(node, ()):
            if not unit():
                return CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
            degree = in_degree[child] - 1
            in_degree[child] = degree
            if degree == 0:
                queue.append(child)
    if processed != len(in_degree):
        return CausalHistoryLimitation.RECEIPT_CYCLE
    return None


class CausalHistoryTransition(_GraphFrozen):
    """One bounded causal-history transition result.

    ``state`` is the state AFTER the transition (the EXACT prior
    state on every refusal and on replay); ``outcome`` is closed;
    ``diagnostics`` and ``observation_limitations`` are sorted,
    deduplicated closed-enum tuples whose TOTAL never exceeds the
    hard diagnostic ceiling (the effective namespace cap is
    enforced by the state machine).  An accepted transition
    advances the revision exactly once; replay and every refusal
    never do.

    Model shape here is SMALL AND CLOSED: sorted/deduplicated
    diagnostic and transition-local occurrence lists, the revision
    arithmetic and the hard diagnostic ceiling.  Cross-state
    membership (every listed new/replayed occurrence is retained in
    the transition state) is a CHARGED KERNEL law, not a model
    shape check: an early CAS/scope/resource refusal must preserve
    the EXACT old state without scanning or copying an overbound
    old state outside the shared per-transition ledger.
    """

    state: CausalHistoryState
    outcome: CausalHistoryOutcome
    diagnostics: tuple[CausalHistoryLimitation, ...] = ()
    observation_limitations: tuple[Limitation, ...] = ()
    new_occurrences: tuple[CompletedReadOccurrence, ...] = ()
    replayed_occurrences: tuple[CompletedReadOccurrence, ...] = ()
    revision_before: int = Field(ge=0)
    revision_after: int = Field(ge=0)

    @model_validator(mode="after")
    def _v_transition(self) -> CausalHistoryTransition:
        if tuple(sorted(set(self.diagnostics))) != self.diagnostics:
            raise _fixed("diagnostics must be sorted and deduplicated")
        if tuple(sorted(set(self.observation_limitations))) != self.observation_limitations:
            raise _fixed("observation limitations must be sorted and deduplicated")
        # Transition-local closed lists (small, bounded by one
        # transition's retained additions -- never the whole state):
        # sorted by occurrence ID, deduplicated, new/replayed disjoint.
        new_ids = [o.occurrence_id for o in self.new_occurrences]
        if new_ids != sorted(new_ids) or len(set(new_ids)) != len(new_ids):
            raise _fixed("new occurrences must be sorted and deduplicated")
        replayed_ids = [o.occurrence_id for o in self.replayed_occurrences]
        if replayed_ids != sorted(replayed_ids) or len(set(replayed_ids)) != len(replayed_ids):
            raise _fixed("replayed occurrences must be sorted and deduplicated")
        if set(new_ids) & set(replayed_ids):
            raise _fixed("an occurrence cannot be both new and replayed")
        # 64 = the HistoryBounds.max_diagnostics hard ceiling.
        if len(self.diagnostics) + len(self.observation_limitations) > 64:
            raise _fixed("total diagnostics exceed the hard ceiling")
        if self.state.revision != self.revision_after:
            raise _fixed("the transition state must carry the after revision")
        if self.outcome is CausalHistoryOutcome.ACCEPTED:
            if self.revision_after != self.revision_before + 1:
                raise _fixed("an accepted transition advances the revision exactly once")
        elif self.revision_after != self.revision_before:
            raise _fixed("a non-accepted transition never advances the revision")
        if self.outcome is CausalHistoryOutcome.REPLAYED and self.new_occurrences:
            raise _fixed("a replay never retains new occurrences")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CausalHistoryTransition(outcome={self.outcome.value!r}, "
            f"revision_before={self.revision_before}, "
            f"revision_after={self.revision_after}, "
            f"diagnostics={list(self.diagnostics)}, "
            f"observation_limitations={list(self.observation_limitations)}, "
            f"new_occurrences={len(self.new_occurrences)}, "
            f"replayed_occurrences={len(self.replayed_occurrences)}, "
            f"state={self.state!r})"
        )

    __str__ = __repr__
