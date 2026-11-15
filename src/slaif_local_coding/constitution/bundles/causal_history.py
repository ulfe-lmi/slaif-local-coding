"""Objective 018-d: the inert causal-occurrence ledger kernel.

``CAUSAL_HISTORY_CONTRACT_VERSION = "cache-causal-history/v1"`` and
``CAUSAL_ARGUMENTS_JSON_VERSION = "causal-arguments-json/v1"`` (both
defined in ``causal_history_models``).

This module is the ONE pure state machine over the immutable
``CausalHistoryState`` records: the original-payload observation
transition, the trusted issuance registration, the late trusted
receipt and the bounded occurrence-relation query.  It is INERT:
never active in the adapter request path, no RAM service, locks,
tasks, compiler, disk checkpoint, source replacement, HTTP/SSE
observer or new metrics; no host IO, no observed command is ever
executed and no client repository filesystem is touched.

Product law (order 018-d):

- A semantic source/content key is not an occurrence ID; a local
  revision is a CAS/serialization fence, NEVER a clock.  A new call
  ID, HTTP arrival, shifted compacted position, equal/different
  digest, lexical sort, receipt arrival or compiler completion
  NEVER establishes source freshness.
- Issuance is NOT source acquisition or success: only a
  subsequently paired complete original read proof (through the
  accepted 017 + 018-b private ``_proof_collect`` core, reusing the
  validated root facts and the same shared source-ledger state)
  creates a completed read occurrence.  The old per-path
  conflict policy is NOT applied: every distinct complete
  nonroot occurrence (including multiple versions of a file from
  different real calls) is retained as evidence.
- Caller-supplied positive proofs/digests/snapshots/flags are never
  acquisition; a root is established only by a legitimate
  effective Responses envelope (or the SAME lineage's previously
  acquired immutable anchor for later rootless observations);
  header/body receipt spoofing cannot anchor anything.
- ONE shared PER-TRANSITION work ledger: one unit is charged
  BEFORE every identity/result comparison attempt, frontier-member
  validation, parent-link/ancestry edge visit, retained proof
  member/piece association and canonical argument node/key visit
  (the last through the shared recipe callbacks); duplicate and
  unsupported attempts that reach the stage count; there is no
  reset within a transition and a crossing is refused BEFORE the
  crossing operation.  Retention caps are CUMULATIVE over the
  lineage state (prior + this transition), checked before any
  copy/retention; ``max_retained_source_bytes`` counts the root
  anchor once plus the exact UTF-8 proof-source bytes per newly
  retained occurrence.
- Diagnostics are BOUNDED TRANSITION RESULT output (the TOTAL
  final closed-enum cap is ``max_diagnostics`` across both
  emitted lists); they are never a lifetime-growing state log.
  Inherited 017/018-b stage diagnostics are carried under their
  EXACT fixed names (propagated, never relabeled); the shared
  017 observation limitations keep their own closed vocabulary.
- An accepted state-changing transition increments the revision
  exactly once; replay and every refusal preserve the EXACT prior
  state (early CAS/scope refusals scan nothing of the old state).

Public entries (all return ``CausalHistoryTransition`` and take an
EXPLICIT ``expected_revision``):

- ``observe_causal_history(requests, ns, state, expected_revision)``
- ``register_issuance(state, ns, call_id, endpoint, tool_name,
  arguments, parent_frontier, expected_revision)``
- ``register_receipt(state, ns, call_id, endpoint, tool_name,
  arguments, parent_frontier, expected_revision)``
- ``relation(state, ns, a, b) -> CausalRelation``
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from ..cache import RequestIdentity
from .bundle_admission_models import ADMISSION_CONTRACT_VERSION
from .bundle_proof import (
    _BridgeSourceLedger,
    _BudgetState,
    _proof_collect,
    _SearchLedger,
)
from .bundle_proof_models import (
    BUNDLE_PROOF_CONTRACT_VERSION,
    BundleLimitation,
    BundleProof,
    BundleProofOutcome,
    BundleSurface,
    make_bundle_proof_namespace,
)
from .causal_history_models import (
    CAUSAL_ARGUMENTS_JSON_VERSION,
    CAUSAL_HISTORY_CONTRACT_VERSION,
    CAUSAL_ROOT_FACT,
    MAX_REVISION,
    CausalHistoryLimitation,
    CausalHistoryNamespace,
    CausalHistoryOutcome,
    CausalHistoryState,
    CausalHistoryTransition,
    CausalRelation,
    CompletedReadOccurrence,
    HistoryBounds,
    IssuedCall,
    ParentLink,
    ResultFingerprintRecord,
    RootAnchor,
    canonicalize_tool_arguments,
    validate_causal_history_state,
)
from .client_paths import validate_workspace
from .graph_models import (
    GRAPH_CONTRACT_VERSION,
    REFERENCE_GRAMMAR,
    _fixed,
    _sha256_hex,
)
from .graph_observation import GraphRequest, _carrier_string
from .observation_models import (
    OBSERVER_VERSION,
    CharSpan,
    Limitation,
    ObservationBounds,
    ObservationReport,
    PathContext,
    ProcessOutcome,
    ProcessPoll,
    RootOccurrence,
    sha256_hex,
)
from .observe import observe_request
from .process_chunks import _utf8_byte_length_range
from .tool_results import _call_records, _inventory_totals

_OCCURRENCE_ENCODING_PREFIX = b"causal-history-occurrence/v1\x00"
_RESULT_ENCODING_PREFIX = b"causal-history-result/v1\x00"
_SESSION_ENCODING_PREFIX = b"causal-history-session/v1\x00"
#: The selected immutable no-session marker (the legacy read surface
#: and the already-exited single-final shape carry no chain session).
_NO_SESSION_DIGEST = _sha256_hex(_SESSION_ENCODING_PREFIX + b"none")

#: The accepted 018-b proof-pass outcomes mapped onto the kernel's
#: closed transition outcomes (the exact fixed reason is carried in
#: the transition diagnostics, never relabeled).
_PROOF_OUTCOME_MAP: dict[BundleProofOutcome, CausalHistoryOutcome] = {
    BundleProofOutcome.NO_ROOT: CausalHistoryOutcome.REFUSED_NO_ROOT,
    BundleProofOutcome.WORKSPACE_UNPROVEN: CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
    BundleProofOutcome.ROOT_CONFLICT: CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
    BundleProofOutcome.VERSION_CONFLICT: CausalHistoryOutcome.REFUSED_VERSION_CONFLICT,
    BundleProofOutcome.OVER_BOUND: CausalHistoryOutcome.REFUSED_OVER_BOUND,
}

#: Inherited scoped diagnostics of the accepted 017/018-b stages,
#: carried under their EXACT fixed names (propagated, never
#: relabeled; the same 018-c admission pattern).
_INHERITED_DIAGNOSTIC_MAP: dict[BundleLimitation, CausalHistoryLimitation] = {
    BundleLimitation.NO_ROOT: CausalHistoryLimitation.NO_ROOT,
    BundleLimitation.COMPETING_ROOTS: CausalHistoryLimitation.COMPETING_ROOTS,
    BundleLimitation.WORKSPACE_UNPROVEN: CausalHistoryLimitation.WORKSPACE_UNPROVEN,
    BundleLimitation.WORKSPACE_MISMATCH: CausalHistoryLimitation.WORKSPACE_MISMATCH,
    BundleLimitation.ROOT_CONTEXT_MISMATCH: CausalHistoryLimitation.ROOT_CONTEXT_MISMATCH,
    BundleLimitation.VERSION_UNSUPPORTED: CausalHistoryLimitation.VERSION_UNSUPPORTED,
    BundleLimitation.BATCH_OVER_BOUND: CausalHistoryLimitation.BATCH_OVER_BOUND,
    BundleLimitation.BUNDLES_OVER_BOUND: CausalHistoryLimitation.BUNDLES_OVER_BOUND,
    BundleLimitation.SOURCE_OVER_BOUND: CausalHistoryLimitation.SOURCE_OVER_BOUND,
    BundleLimitation.TOTAL_SOURCE_OVER_BOUND: CausalHistoryLimitation.TOTAL_SOURCE_OVER_BOUND,
    BundleLimitation.MEMBERS_OVER_BOUND: CausalHistoryLimitation.MEMBERS_OVER_BOUND,
    BundleLimitation.SEGMENTS_OVER_BOUND: CausalHistoryLimitation.SEGMENTS_OVER_BOUND,
    BundleLimitation.MARKER_OVER_BOUND: CausalHistoryLimitation.MARKER_OVER_BOUND,
    BundleLimitation.MARKER_SEARCH_OVER_BOUND: CausalHistoryLimitation.MARKER_SEARCH_OVER_BOUND,
    BundleLimitation.MARKER_EMPTY: CausalHistoryLimitation.MARKER_EMPTY,
    BundleLimitation.MARKER_MISSING: CausalHistoryLimitation.MARKER_MISSING,
    BundleLimitation.MARKER_DUPLICATE: CausalHistoryLimitation.MARKER_DUPLICATE,
    BundleLimitation.MARKER_ORDER: CausalHistoryLimitation.MARKER_ORDER,
    BundleLimitation.MARKER_OVERLAP: CausalHistoryLimitation.MARKER_OVERLAP,
    BundleLimitation.PLAN_UNSUPPORTED: CausalHistoryLimitation.PLAN_UNSUPPORTED,
    BundleLimitation.MEMBER_UNRESOLVED: CausalHistoryLimitation.MEMBER_UNRESOLVED,
    BundleLimitation.MEMBER_PATH_OVER_BOUND: CausalHistoryLimitation.MEMBER_PATH_OVER_BOUND,
    BundleLimitation.SEGMENT_UNEXPLAINED: CausalHistoryLimitation.SEGMENT_UNEXPLAINED,
    BundleLimitation.OUTPUT_INCONSISTENT: CausalHistoryLimitation.OUTPUT_INCONSISTENT,
    BundleLimitation.SOURCE_CONFLICT: CausalHistoryLimitation.SOURCE_CONFLICT,
    BundleLimitation.SEAM_CONFLICT: CausalHistoryLimitation.SEAM_CONFLICT,
    BundleLimitation.DIAGNOSTICS_FULL: CausalHistoryLimitation.DIAGNOSTICS_FULL,
}

#: Non-complete native process outcomes that evidence a PENDING (or
#: honestly terminal non-complete) per-call result record.  A clean
#: chain only: a typed non-acquiring record (nonempty reasons)
#: keeps its evidence in the observation limitations instead.
_PENDING_OUTCOMES = frozenset(
    {ProcessOutcome.RUNNING, ProcessOutcome.NONZERO_EXIT, ProcessOutcome.TRUNCATED}
)


# --- The ONE shared per-transition ledgers ----------------------------


class _UnitLedger(Protocol):
    """The minimal work-unit charging surface shared by the D
    transition ledger and the 018-h H-coupled adapter (H-D3)."""

    def unit(self) -> bool: ...


class _HistoryWorkLedger:
    """The ONE shared PER-TRANSITION work-unit ledger (order law).

    ``unit`` charges ONE unit BEFORE the work it gates and reports
    whether the charge is allowed: a charge that would cross the
    ACTUAL ``HistoryBounds.max_work_units`` is refused BEFORE the
    crossing operation runs.  Cumulative and NEVER reset within the
    transition; the canonical argument recipe receives it as its
    ``work`` callback so every argument node/key visit counts here.
    """

    __slots__ = ("_limit", "units", "refused")

    def __init__(self, limit: int) -> None:
        self._limit = limit
        self.units = 0
        self.refused: CausalHistoryLimitation | None = None

    def unit(self) -> bool:
        if self.refused is not None:
            return False
        if self.units + 1 > self._limit:
            self.refused = CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
            return False
        self.units += 1
        return True


class _RootLineageContext:
    """Narrow validated PRIVATE context for the 018-h root-lineage
    composition (design-018h-v2 resolutions of H-D1/D2/D3 + v2.1).

    Only the H composition constructs one:

    - ``known_root_digests``: the PRE-BATCH known root-body digests
      ({bootstrap} union retained root-fact digests) for the relaxed
      ENVELOPE law;
    - ``relaxed_envelope_law``: a changed same-scope envelope digest
      is context evidence when pre-batch known, otherwise DEFERRED to
      the composition's atomic same-batch verification (the envelope
      grants no ordering and no authority here);
    - ``root_read_acquisition``: a proven SINGLETON root-path member
      read with a foreign digest is a refresh SOURCE candidate,
      retained instead of the old whole-pass COMPETING_ROOTS refusal
      (authority is decided only by the composition);
    - ``mixed_root_acquisition`` (018-o, the new mixed-observation
      operation ONLY): a proven SINGLE root-path segment of a
      MULTI-MEMBER (mixed) proof whose member digest is an
      independently authoritative known root version is ordinary
      source evidence retained instead of the old COMPETING_ROOTS
      refusal; an initially unknown digest is provisionally retained
      and recorded in ``deferred_mixed_digests`` for the
      composition's atomic same-batch verification (a mixed read
      never mints authority; repeated root operands and every
      no-context / no-flag run keep the exact old refusal);
    - ``region_root_acquisition`` (018-p, the NEW root-region
      producer operation ONLY): a proven SINGLE root-path segment
      of a MULTI-MEMBER (mixed) proof is retained SOURCE evidence
      whether or not its member digest is a known root version --
      an unknown mixed root needs NO independent singleton in the
      NEW contract (it is retained unproven; authority is decided
      only by the region composition); repeated root operands and
      every no-context / no-flag run keep the exact old refusal;
    - ``outer_charge``: the ONE H outer work-charge callback (raises
      nothing; returns False exactly when the H outer is exhausted,
      recorded on ``outer_exhausted``).

    The context NEVER grants authority and NEVER modifies requests:
    the old public APIs (no context) keep their exact refusal laws.
    Fixed private repr (no digests, no callback).
    """

    __slots__ = (
        "known_root_digests",
        "relaxed_envelope_law",
        "root_read_acquisition",
        "mixed_root_acquisition",
        "region_root_acquisition",
        "deferred_mixed_digests",
        "outer_charge",
        "outer_exhausted",
    )

    def __init__(
        self,
        known_root_digests: frozenset[str],
        relaxed_envelope_law: bool,
        root_read_acquisition: bool,
        outer_charge: Callable[[], bool],
        mixed_root_acquisition: bool = False,
        region_root_acquisition: bool = False,
    ) -> None:
        self.known_root_digests = known_root_digests
        self.relaxed_envelope_law = relaxed_envelope_law
        self.root_read_acquisition = root_read_acquisition
        self.mixed_root_acquisition = mixed_root_acquisition
        self.region_root_acquisition = region_root_acquisition
        self.deferred_mixed_digests: set[str] = set()
        self.outer_charge = outer_charge
        self.outer_exhausted = False

    def __repr__(self) -> str:
        return "_RootLineageContext(<private>)"


class _CoupledHistoryWorkLedger:
    """H-D3 coupling adapter over the ACTUAL D work ledger.

    Every ``work.unit()`` debit first debits the ONE H outer through
    the context callback, then the ACTUAL D ledger.  The D ceiling
    keeps its exact domain and semantics (a D crossing still maps to
    the D ``WORK_UNITS_OVER_BOUND`` path); an H outer crossing is
    recorded on ``context.outer_exhausted`` so the H composition can
    emit its own fixed over-bound refusal with the EXACT prior H
    state.  No global minimum, no resets; both ceilings stay
    independent.
    """

    __slots__ = ("_inner", "_context")

    def __init__(
        self,
        inner: _HistoryWorkLedger,
        context: _RootLineageContext,
    ) -> None:
        self._inner = inner
        self._context = context

    @property
    def units(self) -> int:
        return self._inner.units

    @property
    def refused(self) -> CausalHistoryLimitation | None:
        return self._inner.refused

    def unit(self) -> bool:
        if self._inner.refused is not None or self._context.outer_exhausted:
            return False
        if not self._context.outer_charge():
            self._context.outer_exhausted = True
            self._inner.refused = CausalHistoryLimitation.WORK_UNITS_OVER_BOUND
            return False
        return self._inner.unit()


class _ArgumentByteLedger:
    """Cumulative per-transition input + canonical argument
    representation bytes (the ``max_total_argument_bytes`` law).

    Charged BEFORE copies by the shared canonical recipe: the raw
    input bytes before the parse and every canonical byte piece as
    it is constructed.  Cumulative over the whole transition
    (observe AND the receipt/issuance canonicalization in it),
    never reset per call.
    """

    __slots__ = ("_limit", "total")

    def __init__(self, limit: int) -> None:
        self._limit = limit
        self.total = 0

    def charge(self, n: int) -> bool:
        if self.total + n > self._limit:
            return False
        self.total += n
        return True


# --- Bounded transition construction ----------------------------------


@dataclass(frozen=True)
class _CollectRefusal:
    """A typed collection-phase refusal (exact prior state kept)."""

    outcome: CausalHistoryOutcome
    diagnostics: tuple[CausalHistoryLimitation, ...]
    limitations: tuple[Limitation, ...]


def _transition(
    state: CausalHistoryState,
    outcome: CausalHistoryOutcome,
    diagnostics: tuple[CausalHistoryLimitation, ...] = (),
    limitations: tuple[Limitation, ...] = (),
    new_occurrences: tuple[CompletedReadOccurrence, ...] = (),
    replayed_occurrences: tuple[CompletedReadOccurrence, ...] = (),
    revision_after: int | None = None,
    revision_before: int | None = None,
) -> CausalHistoryTransition:
    """One bounded transition record.

    Refusals and replays pass the EXACT prior state and never list
    occurrences; an accepted transition lists only occurrences it
    retained (the charged kernel membership law -- the transition
    model itself no longer scans the old state, so an early
    CAS/scope/resource refusal cannot iterate an overbound old
    state).

    ``revision_before`` defaults to the passed state's revision
    (correct for refusals/replays, which preserve the EXACT prior
    state); an accepted transition passes the ACTUAL prior revision
    explicitly, because its state is the already-advanced candidate.
    """
    return CausalHistoryTransition(
        state=state,
        outcome=outcome,
        diagnostics=tuple(sorted(set(diagnostics))),
        observation_limitations=tuple(sorted(set(limitations))),
        new_occurrences=new_occurrences,
        replayed_occurrences=replayed_occurrences,
        revision_before=state.revision if revision_before is None else revision_before,
        revision_after=state.revision if revision_after is None else revision_after,
    )


def _bounded_refusal(
    state: CausalHistoryState,
    outcome: CausalHistoryOutcome,
    diagnostics: tuple[CausalHistoryLimitation, ...],
    limitations: tuple[Limitation, ...],
    cap: int,
) -> CausalHistoryTransition:
    """A typed whole-empty refusal under the ACTUAL total cap.

    The TOTAL emitted diagnostics (both closed lists) are bounded
    BEFORE retention: a crossing normalizes to the ONE fixed
    ``DIAGNOSTICS_FULL`` refusal with NO copied limitations (no
    silent truncation, no governance loss).  At-limit keeps the
    original reasons.  The EXACT prior state is preserved.
    """
    if len(set(diagnostics)) + len(set(limitations)) > cap:
        return _transition(
            state,
            CausalHistoryOutcome.REFUSED_OVER_BOUND,
            (CausalHistoryLimitation.DIAGNOSTICS_FULL,),
        )
    return _transition(state, outcome, diagnostics, limitations)


def _supported_version_pairs(
    ns: CausalHistoryNamespace,
) -> tuple[tuple[str, str], ...]:
    """The SEVEN actual version identities bound into the namespace
    paired with the supported constants.  All O(1) field reads,
    shared by the transition gate and the relation query: a coherent
    direct construction with an unsupported ACTUAL version recomputes
    its keys correctly and must still refuse (fail-closed), never
    interpreted as positive evidence."""
    return (
        (ns.history_version, CAUSAL_HISTORY_CONTRACT_VERSION),
        (ns.arguments_version, CAUSAL_ARGUMENTS_JSON_VERSION),
        (ns.admission_version, ADMISSION_CONTRACT_VERSION),
        (ns.observation_version, OBSERVER_VERSION),
        (ns.graph_version, GRAPH_CONTRACT_VERSION),
        (ns.reference_version, REFERENCE_GRAMMAR),
        (ns.proof_version, BUNDLE_PROOF_CONTRACT_VERSION),
    )


def _gate(
    state: CausalHistoryState,
    ns: CausalHistoryNamespace,
    expected_revision: int,
) -> CausalHistoryTransition | None:
    """The shared early gates: scope, CAS and actual versions.

    All O(1) field reads -- no scan of the (potentially overbound)
    old state before any work ledger exists.  A state from another
    history scope/lineage is refused explicitly; a CAS mismatch is
    refused BEFORE any observation/argument/retention work; and all
    SEVEN actual version identities are compared against the
    supported constants (a coherent direct construction with an
    unsupported version recomputes its keys correctly and must
    still refuse).
    """
    if state.history_key != ns.history_key:
        return _transition(state, CausalHistoryOutcome.REFUSED_FOREIGN_SCOPE)
    if state.revision != expected_revision:
        return _transition(state, CausalHistoryOutcome.REFUSED_CAS_MISMATCH)
    for actual, supported in _supported_version_pairs(ns):
        if actual != supported:
            return _transition(
                state,
                CausalHistoryOutcome.REFUSED_VERSION_CONFLICT,
                (CausalHistoryLimitation.VERSION_UNSUPPORTED,),
            )
    return None


def _validator_outcome(refusal: CausalHistoryLimitation) -> CausalHistoryOutcome:
    """Map one bounded charged state-validation refusal onto the
    closed transition outcomes."""
    if refusal is CausalHistoryLimitation.WORK_UNITS_OVER_BOUND:
        return CausalHistoryOutcome.REFUSED_OVER_BOUND
    if refusal is CausalHistoryLimitation.RECEIPT_CYCLE:
        return CausalHistoryOutcome.REFUSED_CYCLE
    return CausalHistoryOutcome.REFUSED_CONFLICT


# --- Original call binding (strict walker, no invention) ---------------


def _valid_call_id(value: str) -> bool:
    if not 1 <= len(value) <= 256 or any(c.isspace() for c in value):
        return False
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _valid_tool_name(value: str) -> bool:
    if not 1 <= len(value) <= 256 or any(c.isspace() for c in value):
        return False
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _call_name_arguments(payload: dict[str, Any], location: str) -> tuple[str, str] | None:
    """The exact (tool name, raw argument string) at one 017 call
    location in the ORIGINAL payload.

    Strict walker over the two 017 call-location shapes (Responses
    ``$.input[i]`` function_call item; Chat
    ``$.messages[i].tool_calls[j]`` function entry).  Any deviation
    from the schema-evidenced shape returns ``None`` (a defensive
    payload/observation mismatch -- typed by the caller, never a
    guess, never an invention).  The raw arguments are used ONLY to
    run the bounded canonical recipe; they are never retained.
    """
    if location.startswith("$.input["):
        index_s, sep, tail = location[len("$.input[") :].partition("]")
        if tail != "" or not sep or not index_s.isdigit():
            return None
        index = int(index_s)
        items = payload.get("input")
        if not isinstance(items, list) or index >= len(items):
            return None
        item = items[index]
        if not isinstance(item, dict) or item.get("type") != "function_call":
            return None
        name = item.get("name")
        arguments = item.get("arguments")
        if not isinstance(name, str) or not isinstance(arguments, str):
            return None
        return name, arguments
    if location.startswith("$.messages["):
        index_s, sep, tail = location[len("$.messages[") :].partition("]")
        if tail == "" or not sep or not index_s.isdigit():
            return None
        index = int(index_s)
        messages = payload.get("messages")
        if not isinstance(messages, list) or index >= len(messages):
            return None
        message = messages[index]
        if not isinstance(message, dict) or message.get("role") != "assistant":
            return None
        if not tail.startswith(".tool_calls["):
            return None
        tool_index_s, sep2, tail2 = tail[len(".tool_calls[") :].partition("]")
        if tail2 != "" or not sep2 or not tool_index_s.isdigit():
            return None
        tool_index = int(tool_index_s)
        tool_calls = message.get("tool_calls")
        if not isinstance(tool_calls, list) or tool_index >= len(tool_calls):
            return None
        tool = tool_calls[tool_index]
        if not isinstance(tool, dict) or tool.get("type") != "function":
            return None
        function = tool.get("function")
        if not isinstance(function, dict):
            return None
        name = function.get("name")
        arguments = function.get("arguments")
        if not isinstance(name, str) or not isinstance(arguments, str):
            return None
        return name, arguments
    return None


def _occurrence_id(
    call_id: str,
    endpoint: str,
    tool_name: str,
    argument_fingerprint: str,
    source_digest: str,
    root_digest: str,
) -> str:
    """The stable exact occurrence identity (64-hex).

    Binds the immutable call binding (call ID + endpoint family +
    tool name + canonical argument digest) to the EXACT source of
    that read and the root scope.  Carrier/request positions are
    original provenance and are deliberately NOT identity
    material: an exact replay at shifted compacted positions keeps
    the same ID, while a genuinely new call (even over identical
    bytes) is a genuinely new completed occurrence.
    """
    payload = "\x00".join(
        (call_id, endpoint, tool_name, argument_fingerprint, source_digest, root_digest)
    )
    return _sha256_hex(_OCCURRENCE_ENCODING_PREFIX + payload.encode("utf-8"))


def _session_association_digest(session_id: int | None) -> str:
    """The selected immutable session-association fact: the sha256 of
    the EXACT observed chain session ID, or the fixed no-session
    marker.  The raw session value is never retained (the digest is
    the selected evidenced association, like the exact span digests)."""
    if session_id is None:
        return _NO_SESSION_DIGEST
    return _sha256_hex(_SESSION_ENCODING_PREFIX + str(session_id).encode("utf-8"))


def _producer_call_binding(
    payload: dict[str, Any],
    call_location: str,
    hb: HistoryBounds,
    arg_bytes: _ArgumentByteLedger,
    work: _UnitLedger,
) -> tuple[tuple[str, str] | None, CausalHistoryLimitation | None]:
    """The ACTUAL observed producing call's immutable binding
    ``(tool_name, argument_fingerprint)`` at its EXACT original call
    location, under the SAME canonical argument recipe as every other
    binding (the shared argument-byte ledger and work ledger are
    charged by the recipe; raw arguments are never retained).

    Returns ``(binding, None)`` on success, ``(None, reason)`` when
    the shared recipe budget is crossed (a bound crossing of the
    cumulative allowance, never content), and ``(None, None)`` for a
    017 integrity defect (the retained piece's producing call is
    unresolvable, misnamed or its arguments not strict supported
    JSON): the association is refused, NEVER guessed or replaced by
    a placeholder fingerprint.
    """
    name_args = _call_name_arguments(payload, call_location)
    if name_args is None:
        return (None, None)
    name, arguments = name_args
    if not _valid_tool_name(name):
        return (None, None)
    result = canonicalize_tool_arguments(
        name,
        arguments,
        max_argument_bytes=hb.max_argument_bytes,
        max_total_argument_bytes=hb.max_total_argument_bytes,
        max_argument_nodes=hb.max_argument_nodes,
        max_argument_depth=hb.max_argument_depth,
        charge_total=arg_bytes.charge,
        work=work.unit,
    )
    if not result.ok:
        reason = result.reason
        if reason in (
            CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,
            CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,
        ):
            return (None, reason)
        return (None, None)
    fingerprint = result.fingerprint
    if fingerprint is None:
        raise _fixed("a successful recipe carries its fingerprint")
    return ((name, fingerprint), None)


def _complete_result_fingerprint(
    argument_fingerprint: str,
    source_digest: str,
    source_byte_length: int,
    piece_facts: tuple[tuple[int, int, int, str], ...],
    completion: tuple[int | None, ...],
    session_digest: str,
) -> str:
    """The immutable per-call result fingerprint for a COMPLETED
    original read: the selected evidenced result values (the exact
    source digest and length, the EXACT original per-frame piece
    facts, the selected session association) plus the completion
    fact -- never a credential-bearing wrapper.  Aggregate
    source-digest equality alone is NOT per-call result identity: a
    frame resegmentation with the same whole-source bytes changes
    the retained per-frame facts, and a changed per-frame completion
    status under unchanged slice bytes changes the selected
    completion facts -- either changes the fingerprint."""
    if len(completion) != len(piece_facts):
        raise _fixed("piece completion facts align with the piece facts")
    piece_facts_str = ",".join(
        f"{piece_index}:{char_length}:{byte_length}:{digest}"
        for piece_index, char_length, byte_length, digest in piece_facts
    )
    completion_facts_str = ",".join("r" if c is None else str(c) for c in completion)
    payload = "\x00".join(
        (
            argument_fingerprint,
            source_digest,
            str(source_byte_length),
            piece_facts_str,
            completion_facts_str,
            session_digest,
            "complete",
        )
    )
    return _sha256_hex(_RESULT_ENCODING_PREFIX + payload.encode("utf-8"))


def _pending_result_fingerprint(
    argument_fingerprint: str,
    outcome: ProcessOutcome,
    pieces: tuple[tuple[int, int, int, str], ...],
    completion: tuple[int | None, ...],
    total_byte_length: int,
    session_digest: str,
) -> str:
    """The immutable per-call result fingerprint for a PENDING or
    honestly terminal non-complete native process result: the
    selected evidenced result values (the exact outcome, the exact
    original output-slice facts per piece, the total observed bytes)
    plus the non-completion fact -- never a credential-bearing
    wrapper and never a guessed value.  The selected session
    association is identity material (a changed session under the
    same identity is a conflict, never an idempotent replay).  Piece
    positions are original provenance and, like the occurrence law,
    NOT identity material; the immutable slice facts (index/char
    length/byte length/exact original span digest) and the selected
    per-frame completion status are.  Lengths alone are NOT byte
    identity: the digest binds the exact original bytes of each
    slice, and the exit-code fact binds the frame's terminal status
    (a same-length body under a changed frame status is a different
    immutable result)."""
    if len(completion) != len(pieces):
        raise _fixed("piece completion facts align with the piece facts")
    piece_facts = ",".join(
        f"{piece_index}:{char_length}:{byte_length}:{digest}"
        for piece_index, char_length, byte_length, digest in pieces
    )
    completion_facts = ",".join("r" if c is None else str(c) for c in completion)
    payload = "\x00".join(
        (
            argument_fingerprint,
            outcome.value,
            "incomplete",
            str(total_byte_length),
            piece_facts,
            completion_facts,
            session_digest,
        )
    )
    return _sha256_hex(_RESULT_ENCODING_PREFIX + payload.encode("utf-8"))


def _is_fact_prefix[Fact: object](prefix: tuple[Fact, ...], whole: tuple[Fact, ...]) -> bool:
    """True iff ``prefix`` is an EXACT prefix of ``whole`` (element
    equality, including the exact original span digest).

    Used in BOTH directions by the per-call result law: a pending
    extension requires the retained facts to be a prefix of the new
    ones (already-seen bytes unchanged, new polls append); an old-
    prefix re-observation after completion requires the re-observed
    frame's facts to be a prefix of the retained complete facts.
    Any changed already-seen slice is a mutation, never a match."""
    if len(prefix) > len(whole):
        return False
    return all(p == w for p, w in zip(prefix, whole, strict=False))


def _selected_piece_fact(
    payload: dict[str, Any],
    location: str,
    span: CharSpan,
    piece_index: int,
    char_length: int,
    byte_length: int,
) -> tuple[int, int, int, str]:
    """One selected immutable output-slice fact, measured from the
    EXACT original carrier span (bounded copy; the sha256 of the
    exact original span bytes is the retained byte identity, raw
    text never retained).  Defensive 017 integrity defects refuse
    with a fixed error, never a guess."""
    carrier = _carrier_string(payload, location)
    if carrier is None:
        raise _fixed("a retained output slice carries its original carrier")
    if span.start < 0 or span.end > len(carrier):
        raise _fixed("an output slice span must lie within its carrier")
    text = carrier[span.start : span.end]
    if len(text) != char_length:
        raise _fixed("an output slice's measured chars must match the observed fact")
    n_bytes = _utf8_byte_length_range(carrier, span.start, span.end)
    if n_bytes is None or n_bytes != byte_length:
        raise _fixed("an output slice's measured bytes must match the observed fact")
    return (piece_index, char_length, byte_length, sha256_hex(text))


def _proof_piece_facts(
    payload: dict[str, Any],
    proof: BundleProof,
    work: _UnitLedger,
) -> tuple[tuple[int, int, int, str], ...] | None:
    """The selected immutable piece facts of one retained proof,
    measured from the EXACT original carriers (each slice charges the
    ONE shared ledger BEFORE its bounded copy/hash).  ``None`` when
    the shared work ledger is exhausted before a crossing."""
    facts_list: list[tuple[int, int, int, str]] = []
    for piece in proof.pieces:
        if not work.unit():
            return None
        facts_list.append(
            _selected_piece_fact(
                payload,
                piece.carrier_location,
                piece.char_span,
                piece.piece_index,
                piece.char_length,
                piece.byte_length,
            )
        )
    return tuple(facts_list)


# --- The original-input collection phase --------------------------------


@dataclass
class _CollectFacts:
    """Private validated facts after the original-input collection
    phase (the 018-d reuse of the accepted 017 pass, the 018-a
    root/workspace binding law and the shared 018-b ``_proof_collect``
    core -- no weaker observer, no re-implemented read parser)."""

    reports: list[ObservationReport]
    contexts: list[PathContext]
    ordered_limitations: tuple[Limitation, ...]
    root_digest: str
    root_text: str
    root_occurrences: tuple[tuple[int, RootOccurrence], ...]
    #: The (request index, root occurrence) that SUPPLIED the copied
    #: root content (its exact original provenance for the bootstrap
    #: anchor); ``None`` exactly when the root fact was reused from
    #: the SAME lineage's previously retained immutable anchor
    #: (a rootless observation -- the anchor itself retains the
    #: original provenance in the state).
    root_provenance: tuple[int, RootOccurrence] | None
    candidate_diagnostics: tuple[BundleLimitation, ...]
    bundles: tuple[BundleProof, ...]
    #: 018-h relaxed envelope law (H context runs only): the changed
    #: same-scope envelope digests DEFERRED to the composition's atomic
    #: same-batch known-authoritative-source verification.  Every
    #: old-law run (no context) keeps this empty and its exact refusals.
    envelope_deferred_digests: frozenset[str] = frozenset()


def _sort_comparison_reservation(n: int) -> int:
    """Conservative comparison reservation for the canonical key
    sort of ONE dict with ``n`` keys in the inherited full-payload
    fingerprint (018-h, H-C2 measurement follow-up; supersedes the
    rejected n*(ceil(log2 n)+1) upper claim).

    ``json.dumps(sort_keys=True)`` sorts every dict's keys with the
    interpreter's built-in list sort (pinned CPython 3.12 Timsort).
    Its comparisons come from three bounded phases: the adjacent run
    scan compares each adjacent pair once; the interval-halving
    binary insertion compares each inserted element against DISTINCT
    midpoints of a shrinking interval; and the binary/galloping
    merges retire one of the two compared elements from the run being
    merged on every comparison, so two elements that have merged can
    never be re-compared against each other in any later merge (they
    stay in the same run).  Each unordered pair of elements is
    therefore compared at most twice per sort (run-scan/insertion
    handoff plus at most one merge meeting), so the comparison count
    is bounded by ``2 * C(n, 2) = n * (n - 1)`` -- the number of
    ORDERED pairs of distinct elements.  That is the reservation
    charged before serialization: a conservative upper bound derived
    for the actual pinned sort implementation, without asserting a
    tight Timsort worst case (a decision-tree lower bound or an
    unproven n*log2(n) upper is never relabelled as reservation law).
    The measured 512-key ignored-dict control sorted with 3943
    comparisons versus 261120 reserved here; the exhaustion sentinel
    targets this reservation, not the raw sort.  Single-key dicts
    sort trivially.
    """
    if n < 2:
        return 0
    return n * (n - 1)


def _payload_tree_preflight(payload: dict[str, Any], outer_charge: Callable[[], bool]) -> bool:
    """H-private bounded preflight over the ACTUAL decoded payload
    tree (018-h, H-C2 law; H context runs only).

    The inherited full-payload canonical fingerprint
    (``canonical_payload_fingerprint``) serializes the ENTIRE
    decoded payload -- including unknown/ignored nested fields that
    the 017 collectors never visit -- so the container lengths and
    declared 017 ceilings alone do not bound that work.  Before any
    inherited observation runs, this pre-walk visits the actual
    tree ONCE, charging the ONE H outer BEFORE each container
    entry, each scalar value, each 64-character chunk of every
    string key/value (strings charged by ACTUAL length, so
    arbitrary nested/ignored body content is accounted, never a
    renamed unbounded primitive) and -- before visiting each dict's
    entries -- the honest upper comparison reservation for that
    dict's canonical key sort (``_sort_comparison_reservation``;
    the measured 512-key ignored dict alone sorts with 3943
    comparisons, which a single tree walk does not cover).  A crossing
    returns False BEFORE any observer/fingerprint work; the old 017
    public path never runs this preflight (byte-identical).
    """
    stack: list[Any] = [payload]
    while stack:
        value = stack.pop()
        if isinstance(value, dict):
            for _comparison in range(_sort_comparison_reservation(len(value))):
                if not outer_charge():
                    return False
            items = value.items()
            for key, item in items:
                if not outer_charge():
                    return False
                if isinstance(key, str):
                    for _chunk in range((len(key) + 63) // 64 or 1):
                        if not outer_charge():
                            return False
                if isinstance(item, (dict, list)):
                    stack.append(item)
                else:
                    if not outer_charge():
                        return False
                    if isinstance(item, str):
                        for _chunk in range((len(item) + 63) // 64 or 1):
                            if not outer_charge():
                                return False
        elif isinstance(value, list):
            for item in value:
                if not outer_charge():
                    return False
                if isinstance(item, (dict, list)):
                    stack.append(item)
                else:
                    if not outer_charge():
                        return False
                    if isinstance(item, str):
                        for _chunk in range((len(item) + 63) // 64 or 1):
                            if not outer_charge():
                                return False
        else:
            if not outer_charge():
                return False
            if isinstance(value, str):
                for _chunk in range((len(value) + 63) // 64 or 1):
                    if not outer_charge():
                        return False
    return True


def _observation_reservation(payload: dict[str, Any], ob: ObservationBounds) -> int:
    """The honest conservative H-outer reservation for ONE inherited
    017 pass over ONE decoded payload (018-h, H-V2-4 law).

    The accepted 017 collectors (root scan, read inventory/pairing,
    process chunks) visit a number of structural elements bounded by
    the ACTUAL O(1) container lengths plus the DECLARED 017 ceilings
    they themselves enforce before any retention.  One H work unit is
    reserved per structural element visit (item, call record, output
    record, poll/piece, parse op); linear text scans inside those
    elements stay in the char/byte domain under their declared 017
    preflights.  The full-payload canonical fingerprint traversal is
    covered by the H-private ``_payload_tree_preflight`` pre-walk
    (charged before this reservation, H context only).  The
    reservation is charged in full BEFORE the pass runs: an upper
    reservation, never a lower bound, never a flat unbounded pass.
    """
    input_items = payload.get("input")
    input_len = len(input_items) if isinstance(input_items, list) else 0
    messages = payload.get("messages")
    messages_len = len(messages) if isinstance(messages, list) else 0
    input_bound = min(input_len, ob.max_items) + 1
    messages_bound = min(messages_len, ob.max_items) + 1
    return (
        1  # endpoint selection
        + 1  # root-scan container enumeration
        + input_bound  # per user input item classification
        + 1  # read inventory preflight stream
        + input_bound  # per input item inventory visit
        + 1
        + messages_bound  # per chat message inventory visit
        + ob.max_commands  # per call record (preflight + collection)
        + ob.max_outputs  # per output record (preflight + collection)
        + 1  # collection pass container visit
        + ob.max_commands  # per command parse op
        + ob.max_outputs  # per output wrapper parse op
        + 1  # process pass preflight
        + ob.max_process_sessions  # per session structural op
        + ob.max_process_polls  # per poll/piece structural op
        + 1  # report construction
    )


def _proof_budget_reason(refusal: BundleLimitation | None) -> CausalHistoryLimitation:
    if refusal is None:
        raise _fixed("a budget refusal was recorded without a reason")
    return _INHERITED_DIAGNOSTIC_MAP[refusal]


def _collect(
    requests: tuple[GraphRequest, ...],
    ns: CausalHistoryNamespace,
    prior: CausalHistoryState,
    *,
    context: _RootLineageContext | None = None,
) -> tuple[_CollectFacts | None, _CollectRefusal | None]:
    """The bounded original-input collection phase.

    The accepted 017 observation pass runs under the namespace's
    ACTUAL effective ``ObservationBounds``; the 018-a root /
    workspace binding law is applied exactly (a legitimate
    effective Responses envelope, or the SAME lineage's previously
    acquired immutable anchor for a later rootless observation);
    the SHARED cumulative source ledger, marker-search ledger and
    member budget are created ONCE per transition and the accepted
    018-b ``_proof_collect`` core runs over the already-collected
    facts with that SAME ledger state (no reset per request/pass,
    no full public proof wrapper, no upfront graph-batch depth
    gate).  The OLD per-path conflict policy is NOT applied:
    ``bundles`` retains every distinct complete post-seam
    occurrence, including multiple versions of a nonroot file.
    """
    graph_bounds = ns.graph_bounds
    proof_bounds = ns.proof_bounds

    # --- Batch preflight (before any observation work) ----------------
    if len(requests) > graph_bounds.max_requests:
        return (
            None,
            _CollectRefusal(
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.BATCH_OVER_BOUND,),
                (),
            ),
        )

    # --- 017 observation pass (actual effective 017 ceilings) ---------
    if context is None:
        reports = [
            observe_request(
                request.payload, request.context, ns.observation_bounds, request.endpoint
            )
            for request in requests
        ]
    else:
        # 018-h (H-V2-4): the inherited 017 pass work is reserved
        # into the ONE H outer BEFORE any observation runs (per
        # request, the honest conservative reservation from actual
        # O(1) container lengths + declared 017 ceilings).
        outer_charge = context.outer_charge
        reports = []
        for request in requests:
            # 018-h (H-C2): the H-private bounded payload pre-walk
            # charges the actual tree BEFORE any inherited
            # observation/fingerprint runs.
            if not _payload_tree_preflight(request.payload, outer_charge):
                return (
                    None,
                    _CollectRefusal(
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                        (),
                    ),
                )
            for _reserved in range(
                _observation_reservation(request.payload, ns.observation_bounds)
            ):
                if not outer_charge():
                    return (
                        None,
                        _CollectRefusal(
                            CausalHistoryOutcome.REFUSED_OVER_BOUND,
                            (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                            (),
                        ),
                    )
            reports.append(
                observe_request(
                    request.payload,
                    request.context,
                    ns.observation_bounds,
                    request.endpoint,
                )
            )

    def _limitations() -> tuple[Limitation, ...]:
        collected: set[Limitation] = set()
        for report in reports:
            collected.update(report.roots.conflicts)
            collected.update(reason for read in report.reads for reason in read.reasons)
            collected.update(reason for proc in report.processes for reason in proc.reasons)
            collected.update(record.limitation for record in report.unpaired)
        return tuple(sorted(collected))

    ordered_limitations = _limitations()

    # --- Root / workspace binding (the 018-a law) ----------------------
    authoritative: list[tuple[int, RootOccurrence]] = [
        (request_index, root_occ)
        for request_index, report in enumerate(reports)
        for root_occ in report.roots.roots
    ]
    root_content: str | None = None
    root_provenance: tuple[int, RootOccurrence] | None = None
    envelope_deferred_digests: frozenset[str] = frozenset()
    if authoritative:
        # 018-h: every root-inventory visit charges the ONE H outer
        # BEFORE it (context runs only; old-law runs are unchanged).
        if context is not None:
            for _request_index, _root_occ in authoritative:
                if not context.outer_charge():
                    return (
                        None,
                        _CollectRefusal(
                            CausalHistoryOutcome.REFUSED_OVER_BOUND,
                            (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                            (),
                        ),
                    )
        identities: set[tuple[str | None, str | None]] = set()
        for _request_index, root_occ in authoritative:
            identities.add((root_occ.scope_label, root_occ.digest))
        scope_label: str | None
        root_digest: str | None
        if len(identities) > 1:
            scopes = {scope for scope, _digest in identities}
            digests = {digest for _scope, digest in identities}
            if (
                len(scopes) > 1
                or None in scopes
                or any(digest is None for digest in digests)
                or context is None
                or not context.relaxed_envelope_law
                or prior.root is None
            ):
                return (
                    None,
                    _CollectRefusal(
                        CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
                        (CausalHistoryLimitation.COMPETING_ROOTS,),
                        ordered_limitations,
                    ),
                )
            # 018-h relaxed multi-envelope batch: every distinct
            # SAME-SCOPE envelope must be a validated known source
            # (pre-batch) or be atomically verified by the
            # composition after the actual source facts are earned.
            # H-C1: the ACTUAL observed scope is validated against
            # the actual ns workspace BEFORE the immutable
            # acquisition context is substituted (a same-foreign-
            # scope multi-envelope batch keeps the exact old
            # workspace refusals; no latest-root-by-position).
            actual_scope = next(iter(scopes))
            if actual_scope is None:
                raise _fixed("a None envelope scope was refused above the multi branch")
            actual_workspace = validate_workspace(actual_scope, graph_bounds.max_path_bytes)
            if actual_workspace is None or actual_workspace != actual_scope:
                return (
                    None,
                    _CollectRefusal(
                        CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
                        (CausalHistoryLimitation.WORKSPACE_UNPROVEN,),
                        ordered_limitations,
                    ),
                )
            if actual_workspace != ns.workspace:
                return (
                    None,
                    _CollectRefusal(
                        CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
                        (CausalHistoryLimitation.WORKSPACE_MISMATCH,),
                        ordered_limitations,
                    ),
                )
            # The acquisition binding is the IMMUTABLE bootstrap
            # anchor context (no positional winner; envelopes are
            # context evidence only, never a latest-root choice).
            envelope_deferred_digests = frozenset(
                digest
                for digest in digests
                if digest is not None and digest not in context.known_root_digests
            )
            scope_label = actual_scope
            root_digest = prior.root.root_digest
        else:
            scope_label, root_digest = next(iter(identities))
        if scope_label is None or root_digest is None:
            return (
                None,
                _CollectRefusal(
                    CausalHistoryOutcome.REFUSED_NO_ROOT,
                    (CausalHistoryLimitation.NO_ROOT,),
                    ordered_limitations,
                ),
            )
        workspace = validate_workspace(scope_label, graph_bounds.max_path_bytes)
        if workspace is None or workspace != scope_label:
            return (
                None,
                _CollectRefusal(
                    CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
                    (CausalHistoryLimitation.WORKSPACE_UNPROVEN,),
                    ordered_limitations,
                ),
            )
        if workspace != ns.workspace:
            return (
                None,
                _CollectRefusal(
                    CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
                    (CausalHistoryLimitation.WORKSPACE_MISMATCH,),
                    ordered_limitations,
                ),
            )
        for request in requests:
            request_context = request.context
            if (
                request_context is not None
                and request_context.workspace is not None
                and request_context.workspace != workspace
            ):
                return (
                    None,
                    _CollectRefusal(
                        CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
                        (CausalHistoryLimitation.ROOT_CONTEXT_MISMATCH,),
                        ordered_limitations,
                    ),
                )
        prior_root = prior.root
        if prior_root is not None:
            # A later batch's root must be the SAME root: competing
            # digests or a scope change keep the existing explicit
            # refusal (no reset, no supersession).  018-h relaxed
            # law (H context only): a changed same-scope envelope is
            # known-source context evidence when its digest is
            # pre-batch known, otherwise it is DEFERRED to the
            # composition's atomic same-batch verification (the
            # envelope grants no ordering; no new event is minted
            # here, and the collector never mints authority).
            if prior_root.root_digest != root_digest:
                if context is not None and context.relaxed_envelope_law and prior.root is not None:
                    if root_digest not in context.known_root_digests:
                        envelope_deferred_digests = frozenset(
                            set(envelope_deferred_digests) | {root_digest}
                        )
                    # The changed same-scope envelope (known
                    # historical source or deferred new source) is
                    # context/source evidence only: the acquisition
                    # binding stays the ACTUAL immutable bootstrap
                    # anchor context BEFORE proof/ID creation
                    # (envelopes grant no ordering, mint no events
                    # and never rebind retained root identity -- an
                    # already observed original read must replay
                    # with its original identity, and a same-batch
                    # read keeps the bootstrap root binding while
                    # its earned source verifies the deferred
                    # envelope atomically in the composition).
                    scope_label = prior_root.workspace
                    root_digest = prior_root.root_digest
                    workspace = prior_root.workspace
                else:
                    return (
                        None,
                        _CollectRefusal(
                            CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
                            (CausalHistoryLimitation.COMPETING_ROOTS,),
                            ordered_limitations,
                        ),
                    )
            if prior_root.workspace != workspace:
                return (
                    None,
                    _CollectRefusal(
                        CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
                        (CausalHistoryLimitation.WORKSPACE_MISMATCH,),
                        ordered_limitations,
                    ),
                )
    else:
        prior_root = prior.root
        if prior_root is None:
            # Rootless input plus the exact empty prior state cannot
            # bootstrap authority.
            return (
                None,
                _CollectRefusal(
                    CausalHistoryOutcome.REFUSED_NO_ROOT,
                    (CausalHistoryLimitation.NO_ROOT,),
                    ordered_limitations,
                ),
            )
        # A later rootless observation of the SAME lineage reuses the
        # previously acquired immutable anchor/context: the exact
        # retained anchor text is the root fact for this batch (the
        # original origin evidence stays in the anchor; no synthetic
        # root request is inserted, no re-inspection and no second
        # charge -- the anchor bytes are counted once in the state,
        # and no claim that cached root bytes were observed in this
        # batch).
        if prior_root.workspace != ns.workspace:
            # A forged prior anchor from another root scope cannot be
            # reused within this lineage (the history scope key binds
            # the workspace; this is the explicit O(1) defense).
            return (
                None,
                _CollectRefusal(
                    CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
                    (CausalHistoryLimitation.WORKSPACE_MISMATCH,),
                    ordered_limitations,
                ),
            )
        workspace = prior_root.workspace
        root_digest = prior_root.root_digest
        root_content = prior_root.root_text
        for request in requests:
            request_context = request.context
            if (
                request_context is not None
                and request_context.workspace is not None
                and request_context.workspace != workspace
            ):
                return (
                    None,
                    _CollectRefusal(
                        CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
                        (CausalHistoryLimitation.ROOT_CONTEXT_MISMATCH,),
                        ordered_limitations,
                    ),
                )

    # --- Derived-workspace re-observation (the 018-a law) --------------
    # (the per-request original context local is named
    # ``request_context``: the ``context`` parameter is the 018-h
    # private lineage context and must stay unshadowed).
    contexts: list[PathContext] = []
    for index, request in enumerate(requests):
        request_context = request.context
        if request_context is not None and request_context.workspace is not None:
            contexts.append(request_context)
            continue
        if context is not None:
            if not _payload_tree_preflight(request.payload, context.outer_charge):
                return (
                    None,
                    _CollectRefusal(
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                        (),
                    ),
                )
            for _reserved in range(
                _observation_reservation(request.payload, ns.observation_bounds)
            ):
                if not context.outer_charge():
                    return (
                        None,
                        _CollectRefusal(
                            CausalHistoryOutcome.REFUSED_OVER_BOUND,
                            (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                            (),
                        ),
                    )
        derived = PathContext(
            workspace=workspace,
            workdir=request_context.workdir if request_context is not None else None,
        )
        reports[index] = observe_request(
            request.payload, derived, ns.observation_bounds, request.endpoint
        )
        contexts.append(derived)
    authoritative = [
        (request_index, root_occ)
        for request_index, report in enumerate(reports)
        for root_occ in report.roots.roots
    ]
    ordered_limitations = _limitations()

    # --- Shared cumulative ledgers (before any copy/retention) --------
    ledger = _BridgeSourceLedger(graph_bounds)
    search = _SearchLedger(proof_bounds.max_marker_search)
    budget = _BudgetState(proof_bounds)
    # The known observation/global limitations are the shared early
    # output of the transition itself: if they alone exceed the
    # ACTUAL total final cap the whole transition is refused BEFORE
    # any source work (no root fetch, no proof body fetch, no
    # appended diagnostic) with the one bounded fixed reason.
    if len(ordered_limitations) > ns.history_bounds.max_diagnostics:
        return (
            None,
            _CollectRefusal(
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.DIAGNOSTICS_FULL,),
                (),
            ),
        )

    # Every root occurrence (duplicates included) is an inspected
    # source body: measured and accounted BEFORE any owned copy;
    # only the first occurrence is copied (its digest is already
    # bound by the single (scope_label, digest) identity).
    for request_index, root_occ in authoritative:
        if context is not None:
            if not context.outer_charge():
                return (
                    None,
                    _CollectRefusal(
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                        (),
                    ),
                )
        carrier = _carrier_string(requests[request_index].payload, root_occ.location)
        span = root_occ.content_span
        if carrier is None or span is None or span.end > len(carrier):
            continue
        n_bytes = _utf8_byte_length_range(carrier, span.start, span.end)
        if n_bytes is None:
            return (
                None,
                _CollectRefusal(
                    CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
                    (CausalHistoryLimitation.WORKSPACE_UNPROVEN,),
                    ordered_limitations,
                ),
            )
        ledger.account(n_bytes)
        if ledger.refusal is not None:
            return (
                None,
                _CollectRefusal(
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (_proof_budget_reason(ledger.refusal),),
                    ordered_limitations,
                ),
            )
        if root_content is None:
            root_content = carrier[span.start : span.end]
            root_provenance = (request_index, root_occ)
            # 017 self-integrity: the copied bytes must match the
            # 017-computed digest of THIS occurrence (in every old-law
            # run the single-identity law makes it identical to the
            # binding-digest check; the relaxed multi-envelope batch
            # binds copies to their own occurrence digests).
            expected_digest = root_occ.digest if root_occ.digest is not None else root_digest
            if sha256_hex(root_content) != expected_digest:
                # Defensive 017 integrity defect: the root is not
                # acquired (no echo of the content).
                return (
                    None,
                    _CollectRefusal(
                        CausalHistoryOutcome.REFUSED_ROOT_CONFLICT,
                        (CausalHistoryLimitation.WORKSPACE_UNPROVEN,),
                        ordered_limitations,
                    ),
                )
    if root_content is None:
        return (
            None,
            _CollectRefusal(
                CausalHistoryOutcome.REFUSED_NO_ROOT,
                (CausalHistoryLimitation.NO_ROOT,),
                ordered_limitations,
            ),
        )

    # --- The proof namespace for the shared 018-b core -----------------
    proof_namespace = make_bundle_proof_namespace(
        RequestIdentity(
            principal=ns.principal,
            session=ns.session,
            repository=ns.repository,
            route=ns.route,
        ),
        model_identity=ns.model_identity,
        config_fingerprint=ns.config_fingerprint,
        workspace=workspace,
        bounds=proof_bounds,
        graph_bounds=graph_bounds,
        observation_bounds=ns.observation_bounds,
    )

    diagnostics: list[BundleLimitation] = []

    def _note_diagnostic(reason: BundleLimitation) -> bool:
        """Retain one candidate-level fixed diagnostic only while
        the TOTAL emitted diagnostics (candidate reasons + the
        shared observation limitations) stay at BOTH the ACTUAL
        proof-stage bound and the ACTUAL history total bound.  The
        bound is enforced BEFORE retention/append: overflow is the
        bounded ``DIAGNOSTICS_FULL`` refusal, never a truncated or
        unbounded reason list."""
        total_if_retained = len(diagnostics) + len(ordered_limitations) + 1
        if (
            total_if_retained > proof_bounds.max_diagnostics
            or total_if_retained > ns.history_bounds.max_diagnostics
        ):
            return False
        diagnostics.append(reason)
        return True

    result = _proof_collect(
        requests,
        contexts,
        reports,
        proof_namespace,
        proof_bounds,
        root_digest,
        ledger,
        search,
        budget,
        diagnostics,
        _note_diagnostic,
        lineage_context=context,
    )
    if result.refusal_outcome is not None:
        if result.refusal_outcome not in _PROOF_OUTCOME_MAP or result.refusal_reason is None:
            raise _fixed("a proof pass refusal carries its outcome and reason")
        reason = _INHERITED_DIAGNOSTIC_MAP[result.refusal_reason]
        limitations: tuple[Limitation, ...] = (
            () if reason is CausalHistoryLimitation.DIAGNOSTICS_FULL else ordered_limitations
        )
        return (
            None,
            _CollectRefusal(
                _PROOF_OUTCOME_MAP[result.refusal_outcome],
                (reason,),
                limitations,
            ),
        )
    if result.seam_conflict:
        # The same-occurrence seam law is preserved exactly: a
        # mismatched double-positive acquires NOTHING from that
        # occurrence and the transition refuses ready (the accepted
        # 018-b ``version_conflict`` mapping).
        return (
            None,
            _CollectRefusal(
                CausalHistoryOutcome.REFUSED_VERSION_CONFLICT,
                (CausalHistoryLimitation.SEAM_CONFLICT,),
                ordered_limitations,
            ),
        )
    return (
        _CollectFacts(
            reports=reports,
            contexts=contexts,
            ordered_limitations=ordered_limitations,
            root_digest=root_digest,
            root_text=root_content,
            root_occurrences=tuple(authoritative),
            root_provenance=root_provenance,
            candidate_diagnostics=tuple(diagnostics),
            bundles=tuple(result.bundles),
            envelope_deferred_digests=envelope_deferred_digests,
        ),
        None,
    )


# --- The original-payload observation transition -------------------------


def observe_causal_history(
    requests: tuple[GraphRequest, ...],
    ns: CausalHistoryNamespace,
    state: CausalHistoryState,
    expected_revision: int,
) -> CausalHistoryTransition:
    """The original-payload observation transition.

    A bounded ORIGINAL ``GraphRequest`` batch is re-observed through
    the accepted 017 pass and the shared 018-b ``_proof_collect``
    core (same validated root facts, same shared source-ledger
    state).  Every distinct complete post-seam occurrence is a
    completed read occurrence candidate: exact replays (including
    shifted compacted positions) are idempotent (FIRST original
    provenance kept, shifted positions only a bounded transient
    diagnostic); a new call is a genuinely new occurrence; an
    existing call with a changed immutable binding or result is a
    typed conflict.  A new occurrence of a retained issued call is
    anchored under that issuance's COMPLETE frozen frontier (root-
    parent edges included); an unissued call stays UNANCHORED
    evidence with NO temporal edge.  The revision advances exactly
    once per accepted state-changing transition and the EXACT prior
    state is preserved on every refusal and on replay.
    """
    return _observe_causal_history_core(requests, ns, state, expected_revision)


def _observe_causal_history_core(
    requests: tuple[GraphRequest, ...],
    ns: CausalHistoryNamespace,
    state: CausalHistoryState,
    expected_revision: int,
    *,
    context: _RootLineageContext | None = None,
    deferred_sink: list[frozenset[str]] | None = None,
) -> CausalHistoryTransition:
    """The exact observation transition body, factored for the 018-h
    private seam: an optional root-lineage context couples the ONE H
    outer into the inherited collection/scan work (H-D3) and carries
    the relaxed envelope / read-acquisition law (H-D1).  The public
    wrapper runs it with NO context: byte-identical old law.  When a
    deferral sink is supplied and the transition is ACCEPTED, the
    batch's deferred envelope digests are appended to it (the
    composition's atomic verification input).
    """
    gated = _gate(state, ns, expected_revision)
    if gated is not None:
        return gated
    hb: HistoryBounds = ns.history_bounds
    inner = _HistoryWorkLedger(hb.max_work_units)
    work: _UnitLedger = _CoupledHistoryWorkLedger(inner, context) if context is not None else inner
    arg_bytes = _ArgumentByteLedger(hb.max_total_argument_bytes)
    cap = hb.max_diagnostics

    facts, refusal = _collect(requests, ns, state, context=context)
    if refusal is not None:
        return _bounded_refusal(
            state, refusal.outcome, refusal.diagnostics, refusal.limitations, cap
        )
    if facts is None:
        raise _fixed("a non-refusal collection carries its validated facts")

    root_digest = facts.root_digest

    # --- Charged scan of the prior state (IDs, bindings, retained
    # counts) -- every visit, member association and piece
    # association charges the ONE shared transition ledger BEFORE
    # the work; there is no uncharged full-state walk.
    occurrence_ids: set[str] = set()
    prior_by_id: dict[str, CompletedReadOccurrence] = {}
    prior_by_call: dict[str, CompletedReadOccurrence] = {}
    prior_issuances: dict[str, IssuedCall] = {}
    prior_results: dict[str, ResultFingerprintRecord] = {}
    observed_bindings: dict[str, tuple[str, str, str]] = {}
    # The selected immutable per-producing-call RESULT facts
    # (completion status + exact original span byte identity + the
    # evidenced initial-EXEC owner) of every retained chain, keyed
    # by the producing call ID: a producing ID's retained result is
    # immutable across EVERY chain and its completion cannot be
    # reassigned to a different initial EXEC (the proof-local piece
    # coordinate is provenance, never a global identity; the exact
    # empty no-ID state never matches).
    producer_facts: dict[str, tuple[int | None, int, int, str, str]] = {}
    prior_members = 0
    prior_pieces = 0
    prior_pending_pieces = 0
    prior_source_bytes = len(state.root.root_text.encode("utf-8")) if state.root is not None else 0
    for occ in state.occurrences:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        occurrence_ids.add(occ.occurrence_id)
        prior_by_id[occ.occurrence_id] = occ
        prior_by_call.setdefault(occ.call_id, occ)
        observed_bindings.setdefault(
            occ.call_id, (occ.endpoint, occ.tool_name, occ.argument_fingerprint)
        )
        for _member in occ.proof.requested_members:
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
            prior_members += 1
        for _piece in occ.proof.pieces:
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
            prior_pieces += 1
        prior_source_bytes += occ.proof.source_byte_length
    for issuance in state.issuances:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        prior_issuances.setdefault(
            issuance.call_id,
            issuance,
        )
        observed_bindings.setdefault(
            issuance.call_id,
            (issuance.endpoint, issuance.tool_name, issuance.argument_fingerprint),
        )
    for result_record in state.results:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        prior_results[result_record.call_id] = result_record
        observed_bindings.setdefault(
            result_record.call_id,
            (
                result_record.endpoint,
                result_record.tool_name,
                result_record.argument_fingerprint,
            ),
        )
        # The retained piece-producing associations (poll IDs
        # included) are OBSERVED binding evidence: each is registered
        # against the SAME known-binding index, the ONE shared ledger
        # charged before each visit (a reused producing ID under a
        # different binding is refused downstream, never re-bound).
        for bind_index, (
            piece_call_id,
            piece_endpoint,
            piece_tool,
            piece_fp,
        ) in enumerate(result_record.piece_call_bindings):
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
            observed_bindings.setdefault(piece_call_id, (piece_endpoint, piece_tool, piece_fp))
            if piece_call_id:
                producer_facts.setdefault(
                    piece_call_id,
                    (
                        result_record.piece_completion[bind_index],
                        *result_record.piece_facts[bind_index][1:],
                        result_record.call_id,
                    ),
                )
        if not result_record.complete:
            prior_pending_pieces += len(result_record.piece_facts)

    # The CUMULATIVE retained-piece accounting (the existing scoped
    # ceiling): prior occurrence pieces PLUS prior pending-record
    # slices, charged forward as this transition retains new pieces
    # (occurrence proofs, pending slices and completed replacements)
    # BEFORE each retention.
    retained_pieces = prior_pieces + prior_pending_pieces
    new_occurrences: list[CompletedReadOccurrence] = []
    replayed: list[CompletedReadOccurrence] = []
    #: Occurrence IDs created (staged) by THIS transition.  A within-
    #: batch duplicate of a staged occurrence still charges its
    #: duplicate attempts, but the occurrence stays classified NEW
    #: exactly once: the transition's replayed list only carries
    #: facts that existed BEFORE the transition (disjoint law).
    staged_ids: set[str] = set()
    #: Result records CREATED by THIS transition (FIRST original
    #: result provenance may be refined by an earlier request of the
    #: SAME batch; records from an earlier transition keep theirs).
    new_result_ids: set[str] = set()
    new_links: list[ParentLink] = []
    new_results: list[ResultFingerprintRecord] = []
    updated_results: dict[str, ResultFingerprintRecord] = {}
    replay_shifted = False
    new_members = 0
    new_source_bytes = 0
    result_retained = len(state.results)

    # --- Bootstrap root anchor (exact empty prior state only) --------
    # The evidenced root is retained ONCE per state (its exact UTF-8
    # bytes counted against the cumulative retention bound BEFORE
    # retention; later identical roots replay idempotently and
    # competing roots keep the existing refusal in _collect).
    new_root: RootAnchor | None = None
    new_root_bytes = 0
    if state.root is None and facts.root_provenance is not None:
        root_first_index, root_first_occ = facts.root_provenance
        new_root_bytes = len(facts.root_text.encode("utf-8"))
        if new_root_bytes > hb.max_retained_source_bytes:
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.RETAINED_SOURCE_BYTES_OVER_BOUND,),
                facts.ordered_limitations,
                cap,
            )
        span = root_first_occ.content_span
        if span is None:
            raise _fixed("a copied root occurrence carries its content span")
        new_root = RootAnchor(
            root_text=facts.root_text,
            root_digest=root_digest,
            workspace=ns.workspace,
            first_request_index=root_first_index,
            source_byte_length=new_root_bytes,
            location=root_first_occ.location,
            content_span=span,
            envelope_span=root_first_occ.envelope_span,
        )

    # --- Every distinct complete post-seam occurrence ------------------
    for proof in facts.bundles:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        payload = requests[proof.request_index].payload
        name_args = _call_name_arguments(payload, proof.call_location)
        if name_args is None:
            # Defensive payload/observation mismatch: the retained
            # proof cannot be bound to its original call -- typed
            # refusal, never a guess.
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_CONFLICT,
                (CausalHistoryLimitation.OUTPUT_INCONSISTENT,),
                facts.ordered_limitations,
                cap,
            )
        tool_name, arguments = name_args
        if not _valid_tool_name(tool_name):
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_CONFLICT,
                (CausalHistoryLimitation.MALFORMED_BINDING,),
                facts.ordered_limitations,
                cap,
            )
        call_id = proof.call_id
        if call_id == "":
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_CONFLICT,
                (CausalHistoryLimitation.CALL_ID_MISSING,),
                facts.ordered_limitations,
                cap,
            )
        if not _valid_call_id(call_id):
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_CONFLICT,
                (CausalHistoryLimitation.CALL_ID_MALFORMED,),
                facts.ordered_limitations,
                cap,
            )
        endpoint = proof.endpoint
        arg_result = canonicalize_tool_arguments(
            tool_name,
            arguments,
            max_argument_bytes=hb.max_argument_bytes,
            max_total_argument_bytes=hb.max_total_argument_bytes,
            max_argument_nodes=hb.max_argument_nodes,
            max_argument_depth=hb.max_argument_depth,
            charge_total=arg_bytes.charge,
            work=work.unit,
        )
        if not arg_result.ok:
            if arg_result.reason in (
                CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,
                CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,
            ):
                # A bound crossing is a resource fact, never a
                # content conflict: atomic typed resource refusal.
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (arg_result.reason,),
                    facts.ordered_limitations,
                    cap,
                )
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_CONFLICT,
                (arg_result.reason or CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED,),
                facts.ordered_limitations,
                cap,
            )
        arg_fp = arg_result.fingerprint
        if arg_fp is None:
            raise _fixed("a successful recipe carries its fingerprint")
        binding = (endpoint, tool_name, arg_fp)
        prev_binding = observed_bindings.get(call_id)
        if prev_binding is not None:
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
            if prev_binding != binding:
                # A reused ID with a different immutable binding is
                # a fixed conflict, never a new event.
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.ISSUANCE_CONFLICT,),
                    facts.ordered_limitations,
                    cap,
                )
        else:
            observed_bindings[call_id] = binding
        prior_occ = prior_by_call.get(call_id)
        if prior_occ is not None:
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
            if prior_occ.proof.source_digest != proof.source_digest:
                # The same identity with a changed result is a typed
                # conflict (deliberate reverts require a GENUINELY NEW
                # call, never a resold old identity) -- decided against
                # prior PLUS this batch's staged facts, atomically.
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.RESULT_CONFLICT,),
                    facts.ordered_limitations,
                    cap,
                )
        # --- Selected immutable per-frame result facts (each piece
        # charges the ONE shared ledger BEFORE its bounded
        # copy/hash; the session join visit charges per observation)
        # -- validated BEFORE the aggregate occurrence/source replay
        # shortcut below: whole-source digest equality alone cannot
        # prove per-call result equality (a frame resegmentation
        # keeps the aggregate bytes but changes the retained
        # per-frame facts; a session change keeps the body but
        # changes the selected association).
        proof_facts = _proof_piece_facts(payload, proof, work)
        if proof_facts is None:
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        if proof.surface is BundleSurface.PROCESS:
            session_digest: str | None = None
            poll_exit: dict[int, int | None] = {}
            exec_exit: int | None = None
            for proc in facts.reports[proof.request_index].processes:
                if not work.unit():
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                        (),
                        cap,
                    )
                if proc.exec_call_id != proof.call_id:
                    continue
                if session_digest is not None:
                    # Defensive 017 integrity defect: two process
                    # chains claim the same exec call in one request
                    # (never guessed, never first-match).
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_CONFLICT,
                        (CausalHistoryLimitation.OUTPUT_INCONSISTENT,),
                        facts.ordered_limitations,
                        cap,
                    )
                session_digest = _session_association_digest(proc.initial_wrapper.session_id)
                exec_exit = proc.initial_wrapper.exit_code
                # The selected per-poll COMPLETION facts (each poll
                # frame's exact terminal status), charged before
                # each visit: the wrapper's exit code is retained,
                # never the raw wrapper.
                for poll in proc.polls:
                    if not work.unit():
                        return _bounded_refusal(
                            state,
                            CausalHistoryOutcome.REFUSED_OVER_BOUND,
                            (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                            (),
                            cap,
                        )
                    poll_exit[poll.piece.piece_index] = poll.wrapper.exit_code
            if session_digest is None:
                # Defensive 017 integrity defect: a process-surface
                # proof without its process observation in the same
                # request (no invented session, no guess).
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.OUTPUT_INCONSISTENT,),
                    facts.ordered_limitations,
                    cap,
                )
        else:
            session_digest = _NO_SESSION_DIGEST
            poll_exit = {}
            exec_exit = None
        # The ACTUAL observed producing-call association of EVERY
        # retained piece (the read's own call for its own piece, the
        # causally associated poll for each poll piece): resolved at
        # the piece's EXACT original call location under the SAME
        # canonical recipe and charged to the ONE shared ledgers
        # BEFORE any retention or aggregate replay shortcut -- a
        # changed producing binding under equal aggregate facts is a
        # typed conflict, never a rebind, never a placeholder.
        piece_bindings: list[tuple[str, str, str, str]] = []
        piece_completions: list[int | None] = []
        producer_seen: dict[str, tuple[str, str, str]] = {}
        for piece_index, piece in enumerate(proof.pieces):
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
            if piece.call_id == call_id:
                producer_binding: tuple[str, str, str] = (
                    endpoint,
                    tool_name,
                    arg_fp,
                )
                piece_completion: int | None = exec_exit
            else:
                producer, producer_reason = _producer_call_binding(
                    payload, piece.call_location, hb, arg_bytes, work
                )
                if producer is None:
                    if producer_reason in (
                        CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,
                        CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,
                    ):
                        return _bounded_refusal(
                            state,
                            CausalHistoryOutcome.REFUSED_OVER_BOUND,
                            (producer_reason,),
                            facts.ordered_limitations,
                            cap,
                        )
                    # Defensive 017 integrity defect: the retained
                    # piece's producing call is unresolvable in its
                    # EXACT original request -- refused, never a
                    # guessed or placeholder binding.
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_CONFLICT,
                        (CausalHistoryLimitation.OUTPUT_INCONSISTENT,),
                        facts.ordered_limitations,
                        cap,
                    )
                producer_binding = (endpoint, producer[0], producer[1])
                if piece.piece_index not in poll_exit:
                    # Defensive 017 integrity defect: a process-
                    # surface poll piece without its poll observation
                    # in the same request (no invented status, no
                    # guess).
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_CONFLICT,
                        (CausalHistoryLimitation.OUTPUT_INCONSISTENT,),
                        facts.ordered_limitations,
                        cap,
                    )
                piece_completion = poll_exit[piece.piece_index]
            previous = producer_seen.get(piece.call_id)
            if previous is not None and previous != producer_binding:
                # The same producing ID under two different immutable
                # bindings in ONE retained proof: a fixed conflict.
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.OUTPUT_INCONSISTENT,),
                    facts.ordered_limitations,
                    cap,
                )
            producer_seen.setdefault(piece.call_id, producer_binding)
            piece_bindings.append((piece.call_id, *producer_binding))
            piece_completions.append(piece_completion)
            # The selected immutable per-producing-call RESULT fact
            # (completion status + exact original span bytes + the
            # evidenced initial-EXEC owner) is validated GLOBALLY
            # across every chain (prior PLUS staged same-batch
            # facts) under the ONE shared ledger: a producing ID's
            # retained result is immutable and its completion cannot
            # be reassigned to another initial EXEC, even when the
            # bytes/status/session all match; the proof-local piece
            # coordinate is provenance, never a global identity.
            if piece.call_id != call_id and piece.call_id:
                piece_fact = (piece_completion, *proof_facts[piece_index][1:], call_id)
                previous_fact = producer_facts.get(piece.call_id)
                if previous_fact is not None:
                    if not work.unit():
                        return _bounded_refusal(
                            state,
                            CausalHistoryOutcome.REFUSED_OVER_BOUND,
                            (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                            (),
                            cap,
                        )
                    if previous_fact != piece_fact:
                        return _bounded_refusal(
                            state,
                            CausalHistoryOutcome.REFUSED_CONFLICT,
                            (CausalHistoryLimitation.RESULT_CONFLICT,),
                            facts.ordered_limitations,
                            cap,
                        )
                else:
                    producer_facts[piece.call_id] = piece_fact
        complete_fp = _complete_result_fingerprint(
            arg_fp,
            proof.source_digest,
            proof.source_byte_length,
            proof_facts,
            tuple(piece_completions),
            session_digest,
        )
        occurrence_id = _occurrence_id(
            call_id, endpoint, tool_name, arg_fp, proof.source_digest, root_digest
        )
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        if occurrence_id in occurrence_ids:
            # An exact duplicate of retained evidence (including an
            # acceptance staged earlier in THIS batch): idempotent
            # replay, the FIRST original provenance is kept.
            # The retained per-frame result facts are validated
            # BEFORE this aggregate shortcut: a changed frame (bytes,
            # completion or session association) under an equal
            # occurrence/source identity is a typed conflict, never
            # a replay.
            retained = prior_by_id[occurrence_id]
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
            prior_result = prior_results.get(call_id)
            if (
                prior_result is None
                or not prior_result.complete
                or prior_result.result_fingerprint != complete_fp
                or prior_result.piece_call_bindings != tuple(piece_bindings)
            ):
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.RESULT_CONFLICT,),
                    facts.ordered_limitations,
                    cap,
                )
            if (
                proof.request_index,
                proof.call_position,
                proof.result_position,
            ) != (
                retained.proof.request_index,
                retained.proof.call_position,
                retained.proof.result_position,
            ):
                replay_shifted = True
            replayed.append(retained)
            continue

        # --- A genuinely new completed occurrence: cumulative
        # retention preflights BEFORE any copy/retention --------
        n_members = len(proof.requested_members)
        n_pieces = len(proof.pieces)
        n_bytes = proof.source_byte_length
        # The retained pending slices of the record this proof
        # upgrades are REPLACED by the proof pieces (the final state
        # retains the proof pieces, never both): the net retention
        # is proof pieces minus the replaced pending slices, so an
        # at-limit completion of a pending chain is never path-
        # dependent.
        prior_pending = prior_results.get(call_id)
        replaced_pending_pieces = 0
        if prior_pending is not None and not prior_pending.complete:
            replaced_pending_pieces = len(prior_pending.piece_facts)
        net_new_pieces = n_pieces - replaced_pending_pieces
        if len(state.occurrences) + len(new_occurrences) + 1 > hb.max_occurrences:
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.OCCURRENCES_OVER_BOUND,),
                facts.ordered_limitations,
                cap,
            )
        if prior_members + new_members + n_members > hb.max_retained_members:
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.RETAINED_MEMBERS_OVER_BOUND,),
                facts.ordered_limitations,
                cap,
            )
        if retained_pieces + net_new_pieces > hb.max_retained_pieces:
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.RETAINED_PIECES_OVER_BOUND,),
                facts.ordered_limitations,
                cap,
            )
        if (
            prior_source_bytes + new_root_bytes + new_source_bytes + n_bytes
            > hb.max_retained_source_bytes
        ):
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.RETAINED_SOURCE_BYTES_OVER_BOUND,),
                facts.ordered_limitations,
                cap,
            )
        # --- Charged retention associations: EVERY retained proof
        # member occurrence and piece/span record of a NEW occurrence
        # charges ONE unit of the ONE shared ledger BEFORE it is
        # retained (duplicate operands count even though slot width
        # dedups later; no reset within the transition); a crossing
        # refuses atomically BEFORE any retention.
        for _member in proof.requested_members:
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
        for _piece in proof.pieces:
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
        anchored_issuance = prior_issuances.get(call_id)
        anchored = anchored_issuance is not None
        # A complete proof for a retained issued call anchors under
        # that issuance's COMPLETE frozen frontier (root-parent
        # edges included, charged per edge); an unissued call stays
        # UNANCHORED evidence with NO temporal edge.
        if anchored and anchored_issuance is not None:
            for member in anchored_issuance.parent_frontier:
                if not work.unit():
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                        (),
                        cap,
                    )
                if len(state.parent_links) + len(new_links) + 1 > hb.max_causal_links:
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (CausalHistoryLimitation.CAUSAL_LINKS_OVER_BOUND,),
                        facts.ordered_limitations,
                        cap,
                    )
                new_links.append(ParentLink(child=occurrence_id, parent=member))
        new_occ = CompletedReadOccurrence(
            occurrence_id=occurrence_id,
            call_id=call_id,
            endpoint=endpoint,
            tool_name=tool_name,
            argument_fingerprint=arg_fp,
            proof=proof,
            anchored=anchored,
        )
        new_occurrences.append(new_occ)
        # Staged facts: later evidence in THIS batch deduplicates
        # against prior PLUS staged facts (FIRST provenance kept).
        occurrence_ids.add(occurrence_id)
        staged_ids.add(occurrence_id)
        prior_by_id[occurrence_id] = new_occ
        prior_by_call[call_id] = new_occ
        new_members += n_members
        retained_pieces += net_new_pieces
        new_source_bytes += n_bytes
        # The immutable per-call result record (the selected
        # evidenced result values plus the completion fact):
        # created with the occurrence, idempotent on exact replay,
        # extended when a pending record completes, and a typed
        # conflict when a completed result would change.
        # (``complete_fp`` / ``proof_facts`` / ``session_digest``
        # were computed and charged once above, before the aggregate
        # replay shortcut; the validated immutable facts are reused
        # here, never re-measured.)
        prior_result = prior_results.get(call_id)
        if prior_result is None:
            if result_retained + 1 > hb.max_observed_results:
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.RESULTS_OVER_BOUND,),
                    facts.ordered_limitations,
                    cap,
                )
            result_retained += 1
            complete_record = ResultFingerprintRecord(
                call_id=call_id,
                endpoint=endpoint,
                tool_name=tool_name,
                argument_fingerprint=arg_fp,
                result_fingerprint=complete_fp,
                complete=True,
                first_request_index=proof.request_index,
                session_digest=session_digest,
                piece_facts=proof_facts,
                piece_call_bindings=tuple(piece_bindings),
                piece_completion=tuple(piece_completions),
            )
            new_results.append(complete_record)
            prior_results[call_id] = complete_record
            new_result_ids.add(call_id)
            # The retained piece-producing IDs (polls included) are
            # staged known bindings for the REST of this batch (a
            # within-batch reuse is a typed conflict, not a rebind).
            for (
                piece_call_id,
                piece_endpoint,
                piece_tool,
                piece_fp,
            ) in complete_record.piece_call_bindings:
                if not work.unit():
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                        (),
                        cap,
                    )
                observed_bindings.setdefault(piece_call_id, (piece_endpoint, piece_tool, piece_fp))
        elif prior_result.complete:
            if (
                prior_result.result_fingerprint != complete_fp
                or prior_result.piece_call_bindings != tuple(piece_bindings)
            ):
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.RESULT_CONFLICT,),
                    facts.ordered_limitations,
                    cap,
                )
        elif prior_result.pending_outcome is not ProcessOutcome.RUNNING:
            # A terminal non-complete fact (NONZERO_EXIT/TRUNCATED)
            # never completes: partial/truncated/unsupported output
            # never becomes a completed source (a completed result on
            # the same identity is a typed conflict).
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_CONFLICT,
                (CausalHistoryLimitation.RESULT_CONFLICT,),
                facts.ordered_limitations,
                cap,
            )
        else:
            # A still-running pending process record legitimately
            # extends to completion with new polls (accepted 017
            # rules) ONLY when the already-seen pending bytes AND
            # the selected session association are immutable: the
            # retained selected piece facts must be an exact prefix
            # of the complete proof's piece facts under the same
            # chain session.  The FIRST original provenance
            # (first_request_index) is kept, the record is replaced
            # by the complete record with the proof's exact original
            # piece facts, and the extended record is staged for the
            # rest of this batch.
            if session_digest != prior_result.session_digest:
                # A changed session association under the same
                # identity can never complete the pending evidence:
                # a typed conflict.
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.RESULT_CONFLICT,),
                    facts.ordered_limitations,
                    cap,
                )
            if not _is_fact_prefix(prior_result.piece_facts, proof_facts):
                # Mutated or non-extending already-seen bytes can
                # never be completed by a later proof: a typed
                # conflict.
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.RESULT_CONFLICT,),
                    facts.ordered_limitations,
                    cap,
                )
            if not _is_fact_prefix(prior_result.piece_call_bindings, tuple(piece_bindings)):
                # A changed producing-call association for an
                # already-seen slice can never complete the pending
                # evidence: a typed conflict.
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.RESULT_CONFLICT,),
                    facts.ordered_limitations,
                    cap,
                )
            if not _is_fact_prefix(prior_result.piece_completion, tuple(piece_completions)):
                # A changed per-frame completion status for an
                # already-seen slice (a same-length body under a
                # changed frame status) can never complete the
                # pending evidence: a typed conflict.
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.RESULT_CONFLICT,),
                    facts.ordered_limitations,
                    cap,
                )
            # The piece RETENTION net of this upgrade (proof pieces
            # minus the replaced pending slices) was already
            # accounted in the new-occurrence preflight above: no
            # second charge here (the prefix/session/completion
            # checks above are the semantic law).
            updated_record = prior_result.model_copy(
                update={
                    "result_fingerprint": complete_fp,
                    "complete": True,
                    "pending_outcome": None,
                    "piece_facts": proof_facts,
                    "piece_call_bindings": tuple(piece_bindings),
                    "piece_completion": tuple(piece_completions),
                }
            )
            updated_results[call_id] = updated_record
            prior_results[call_id] = updated_record

    # --- Pending / non-complete native process result records --------
    # A clean paired native process chain that is not complete is
    # pending evidence (RUNNING) or an honestly terminal non-complete
    # result (NONZERO_EXIT / TRUNCATED): a complete=False record
    # under the same immutable binding, binding the SELECTED immutable
    # result/piece facts.  The expected 017 process state label is
    # part of the accepted observation shape (RUNNING/TRUNCATED carry
    # their fixed limitation); any OTHER limitation is typed
    # non-acquisition evidence that keeps living in the observation
    # limitations (no invented binding, no guessed value).  A genuine
    # 017-accepted poll extension may extend ONE record (already-seen
    # bytes unchanged, new polls appended); mutated already-seen
    # pending bytes refuse.  Partial/truncated/unsupported output
    # never becomes a completed source.
    for request_index, report in enumerate(facts.reports):
        for proc in report.processes:
            if proc.outcome not in _PENDING_OUTCOMES:
                continue
            expected_reasons: tuple[Limitation, ...]
            if proc.outcome is ProcessOutcome.RUNNING:
                expected_reasons = (Limitation.PROCESS_RUNNING,)
            elif proc.outcome is ProcessOutcome.TRUNCATED:
                expected_reasons = (Limitation.PROCESS_TRUNCATED,)
            else:
                expected_reasons = ()
            if proc.reasons != expected_reasons:
                continue
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
            proc_call_id = proc.exec_call_id
            if not _valid_call_id(proc_call_id):
                continue
            name_args = _call_name_arguments(
                requests[request_index].payload, proc.exec_call_location
            )
            if name_args is None:
                continue
            proc_tool, proc_arguments = name_args
            if not _valid_tool_name(proc_tool):
                continue
            proc_arg = canonicalize_tool_arguments(
                proc_tool,
                proc_arguments,
                max_argument_bytes=hb.max_argument_bytes,
                max_total_argument_bytes=hb.max_total_argument_bytes,
                max_argument_nodes=hb.max_argument_nodes,
                max_argument_depth=hb.max_argument_depth,
                charge_total=arg_bytes.charge,
                work=work.unit,
            )
            if not proc_arg.ok:
                if proc_arg.reason in (
                    CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,
                    CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,
                ):
                    # A shared-budget crossing is a resource fact:
                    # atomic typed resource refusal, never a silent
                    # skip (the ledger is crossed, the transition is
                    # not).
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (proc_arg.reason,),
                        facts.ordered_limitations,
                        cap,
                    )
                # Unsupported or non-strict exec-call arguments: no
                # binding can be established and no record is
                # retained (fail-closed non-acquisition, never a
                # guess).
                continue
            proc_fp = proc_arg.fingerprint
            if proc_fp is None:
                raise _fixed("a successful recipe carries its fingerprint")
            proc_binding = (proc.endpoint, proc_tool, proc_fp)
            prev_binding = observed_bindings.get(proc_call_id)
            if prev_binding is not None:
                if not work.unit():
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                        (),
                        cap,
                    )
                if prev_binding != proc_binding:
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_CONFLICT,
                        (CausalHistoryLimitation.RESULT_CONFLICT,),
                        facts.ordered_limitations,
                        cap,
                    )
            else:
                observed_bindings[proc_call_id] = proc_binding
            # The selected immutable pending output-slice facts are
            # measured from the EXACT original carriers BEFORE
            # retention: each slice charges the ONE shared ledger
            # before its bounded copy/hash (the exact original span
            # digest is the retained byte identity; lengths alone
            # are NOT byte identity).
            pending_facts: list[tuple[int, int, int, str]] = []
            pending_bindings: list[tuple[str, str, str, str]] = []
            pending_completion: list[int | None] = []
            poll_by_piece_index: dict[int, ProcessPoll] = {}
            for poll in proc.polls:
                if poll.piece.piece_index in poll_by_piece_index:
                    # Defensive 017 integrity defect: two polls claim
                    # the same output slice.
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_CONFLICT,
                        (CausalHistoryLimitation.OUTPUT_INCONSISTENT,),
                        facts.ordered_limitations,
                        cap,
                    )
                poll_by_piece_index[poll.piece.piece_index] = poll
            exec_piece_bound = False
            seen_bindings: dict[str, tuple[str, str, str]] = {}
            for slice_piece in proc.pieces:
                if not work.unit():
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                        (),
                        cap,
                    )
                pending_facts.append(
                    _selected_piece_fact(
                        requests[request_index].payload,
                        slice_piece.result_location,
                        slice_piece.char_span,
                        slice_piece.piece_index,
                        slice_piece.char_length,
                        slice_piece.byte_length,
                    )
                )
                # The ACTUAL observed producing-call association of
                # THIS slice (the exec call for its own slice, the
                # causally associated poll for a poll slice) at the
                # EXACT original call location, under the SAME
                # canonical recipe: observed evidence, never a
                # fabricated issuance or placeholder.
                slice_poll = poll_by_piece_index.get(slice_piece.piece_index)
                if slice_poll is not None:
                    producer, producer_reason = _producer_call_binding(
                        requests[request_index].payload,
                        slice_poll.poll_call_location,
                        hb,
                        arg_bytes,
                        work,
                    )
                    if producer is None:
                        if producer_reason in (
                            CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,
                            CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,
                        ):
                            return _bounded_refusal(
                                state,
                                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                                (producer_reason,),
                                facts.ordered_limitations,
                                cap,
                            )
                        return _bounded_refusal(
                            state,
                            CausalHistoryOutcome.REFUSED_CONFLICT,
                            (CausalHistoryLimitation.OUTPUT_INCONSISTENT,),
                            facts.ordered_limitations,
                            cap,
                        )
                    piece_binding = (proc.endpoint, producer[0], producer[1])
                    poll_id = slice_poll.poll_call_id
                    pending_completion.append(slice_poll.wrapper.exit_code)
                else:
                    if exec_piece_bound:
                        # A second non-poll slice: no such 017 shape
                        # exists (defensive, never a guess).
                        return _bounded_refusal(
                            state,
                            CausalHistoryOutcome.REFUSED_CONFLICT,
                            (CausalHistoryLimitation.OUTPUT_INCONSISTENT,),
                            facts.ordered_limitations,
                            cap,
                        )
                    exec_piece_bound = True
                    piece_binding = (proc.endpoint, proc_tool, proc_fp)
                    poll_id = proc_call_id
                    pending_completion.append(proc.initial_wrapper.exit_code)
                previous = seen_bindings.get(poll_id)
                if previous is not None and previous != piece_binding:
                    # The same producing ID under two different
                    # immutable bindings in ONE observed chain: a
                    # fixed conflict (never re-bound, never guessed).
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_CONFLICT,
                        (CausalHistoryLimitation.OUTPUT_INCONSISTENT,),
                        facts.ordered_limitations,
                        cap,
                    )
                seen_bindings.setdefault(poll_id, piece_binding)
                pending_bindings.append((poll_id, *piece_binding))
                # The selected immutable per-producing-call RESULT
                # fact (completion status + exact original span
                # bytes + the evidenced initial-EXEC owner) validated
                # GLOBALLY across every chain (prior PLUS staged
                # same-batch facts) under the ONE shared ledger; the
                # proof-local piece coordinate is provenance, never
                # a global identity, and a poll's owner cannot be
                # reassigned to another initial EXEC.
                if slice_poll is not None and poll_id:
                    slice_fact = (
                        slice_poll.wrapper.exit_code,
                        *pending_facts[-1][1:],
                        proc_call_id,
                    )
                    previous_fact = producer_facts.get(poll_id)
                    if previous_fact is not None:
                        if not work.unit():
                            return _bounded_refusal(
                                state,
                                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                                (),
                                cap,
                            )
                        if previous_fact != slice_fact:
                            return _bounded_refusal(
                                state,
                                CausalHistoryOutcome.REFUSED_CONFLICT,
                                (CausalHistoryLimitation.RESULT_CONFLICT,),
                                facts.ordered_limitations,
                                cap,
                            )
                    else:
                        producer_facts[poll_id] = slice_fact
            pending_pieces = tuple(pending_facts)
            # The selected immutable session-association fact of
            # THIS chain (the session established by the initial
            # running frame; the already-exited single-final shape
            # carries none): identity material like the exact span
            # digests, never a raw retained value.
            pending_session = _session_association_digest(proc.initial_wrapper.session_id)
            pending_fp = _pending_result_fingerprint(
                proc_fp,
                proc.outcome,
                pending_pieces,
                tuple(pending_completion),
                proc.total_byte_length,
                pending_session,
            )
            prior_result = prior_results.get(proc_call_id)
            if prior_result is None:
                if result_retained + 1 > hb.max_observed_results:
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (CausalHistoryLimitation.RESULTS_OVER_BOUND,),
                        facts.ordered_limitations,
                        cap,
                    )
                if retained_pieces + len(pending_pieces) > hb.max_retained_pieces:
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (CausalHistoryLimitation.RETAINED_PIECES_OVER_BOUND,),
                        facts.ordered_limitations,
                        cap,
                    )
                result_retained += 1
                retained_pieces += len(pending_pieces)
                pending_record = ResultFingerprintRecord(
                    call_id=proc_call_id,
                    endpoint=proc.endpoint,
                    tool_name=proc_tool,
                    argument_fingerprint=proc_fp,
                    result_fingerprint=pending_fp,
                    complete=False,
                    first_request_index=request_index,
                    session_digest=pending_session,
                    pending_outcome=proc.outcome,
                    piece_facts=pending_pieces,
                    piece_call_bindings=tuple(pending_bindings),
                    piece_completion=tuple(pending_completion),
                )
                new_results.append(pending_record)
                prior_results[proc_call_id] = pending_record
                new_result_ids.add(proc_call_id)
                # The retained producing IDs (polls included) are
                # staged known bindings for the REST of this batch.
                for (
                    piece_call_id,
                    piece_endpoint,
                    piece_tool,
                    piece_fp,
                ) in pending_record.piece_call_bindings:
                    if not work.unit():
                        return _bounded_refusal(
                            state,
                            CausalHistoryOutcome.REFUSED_OVER_BOUND,
                            (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                            (),
                            cap,
                        )
                    observed_bindings.setdefault(
                        piece_call_id, (piece_endpoint, piece_tool, piece_fp)
                    )
            elif prior_result.complete:
                # The completed record retains the EXACT original
                # piece facts of the complete proof.  Immutable
                # result frames are distinguished from the aggregate
                # completion: the initial running result never
                # changes, so a re-observed frame is an idempotent
                # no-op ONLY when it is the STRICTLY OLD prefix of
                # the retained facts under the SAME selected session
                # association (the completed state is preserved,
                # never regressed); a terminal frame, a changed
                # session, a same-frame-count status change, or
                # changed or extended already-seen bytes, contradict
                # the completed source.
                if (
                    proc.outcome is not ProcessOutcome.RUNNING
                    or len(pending_pieces) >= len(prior_result.piece_facts)
                    or not _is_fact_prefix(pending_pieces, prior_result.piece_facts)
                    or not _is_fact_prefix(tuple(pending_completion), prior_result.piece_completion)
                    or pending_session != prior_result.session_digest
                    or not _is_fact_prefix(
                        tuple(pending_bindings), prior_result.piece_call_bindings
                    )
                ):
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_CONFLICT,
                        (CausalHistoryLimitation.RESULT_CONFLICT,),
                        facts.ordered_limitations,
                        cap,
                    )
                # Exact old prefix re-observed: no state change.
                # FIRST original RESULT provenance: the completed
                # path may have created this record EARLIER in the
                # same batch (stamped with the first COMPLETE
                # SOURCE's request index); an earlier pending
                # snapshot of the same call in this batch is the
                # first observed result, and the record keeps that
                # provenance.  The occurrence's proof keeps the
                # first complete source index (list order invents
                # no completion or causality; earlier-transition
                # provenance is never re-stamped).
                if (
                    proc_call_id in new_result_ids
                    and request_index < prior_result.first_request_index
                ):
                    restamped = prior_result.model_copy(
                        update={"first_request_index": request_index}
                    )
                    updated_results[proc_call_id] = restamped
                    prior_results[proc_call_id] = restamped
            elif prior_result.result_fingerprint == pending_fp:
                if tuple(pending_bindings) != prior_result.piece_call_bindings:
                    # Equal aggregate fingerprint with a changed
                    # producing-call association: a typed conflict,
                    # never an idempotent no-op.
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_CONFLICT,
                        (CausalHistoryLimitation.RESULT_CONFLICT,),
                        facts.ordered_limitations,
                        cap,
                    )
                # Exact idempotent re-observation (the unchanged chain
                # or a repeated terminal frame): no state change.
                pass
            elif (
                prior_result.pending_outcome is ProcessOutcome.RUNNING
                and _is_fact_prefix(prior_result.piece_facts, pending_pieces)
                and _is_fact_prefix(prior_result.piece_completion, tuple(pending_completion))
                and pending_session == prior_result.session_digest
                and _is_fact_prefix(prior_result.piece_call_bindings, tuple(pending_bindings))
            ):
                # A genuine 017-accepted poll extension: the selected
                # facts so far are an exact prefix (already-seen bytes
                # unchanged; new polls append).  ONE record is extended
                # with the new immutable facts; the FIRST original
                # provenance (first_request_index) is kept and the
                # extended record is staged for the rest of this batch.
                extension_delta = len(pending_pieces) - len(prior_result.piece_facts)
                if retained_pieces + extension_delta > hb.max_retained_pieces:
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (CausalHistoryLimitation.RETAINED_PIECES_OVER_BOUND,),
                        facts.ordered_limitations,
                        cap,
                    )
                retained_pieces += extension_delta
                extended_record = prior_result.model_copy(
                    update={
                        "result_fingerprint": pending_fp,
                        "pending_outcome": proc.outcome,
                        "piece_facts": pending_pieces,
                        "piece_call_bindings": tuple(pending_bindings),
                        "piece_completion": tuple(pending_completion),
                    }
                )
                updated_results[proc_call_id] = extended_record
                prior_results[proc_call_id] = extended_record
                # The NEWLY retained producing IDs (the appended
                # polls) are staged known bindings for the REST of
                # this batch (already-known entries setdefault no-op).
                for (
                    piece_call_id,
                    piece_endpoint,
                    piece_tool,
                    piece_fp,
                ) in extended_record.piece_call_bindings:
                    if not work.unit():
                        return _bounded_refusal(
                            state,
                            CausalHistoryOutcome.REFUSED_OVER_BOUND,
                            (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                            (),
                            cap,
                        )
                    observed_bindings.setdefault(
                        piece_call_id, (piece_endpoint, piece_tool, piece_fp)
                    )
            elif (
                proc.outcome is ProcessOutcome.RUNNING
                and prior_result.pending_outcome is ProcessOutcome.RUNNING
                and len(pending_pieces) < len(prior_result.piece_facts)
                and _is_fact_prefix(pending_pieces, prior_result.piece_facts)
                and _is_fact_prefix(tuple(pending_completion), prior_result.piece_completion)
                and pending_session == prior_result.session_digest
                and _is_fact_prefix(tuple(pending_bindings), prior_result.piece_call_bindings)
            ):
                # The EXACT old pending prefix re-observed while the
                # retained chain is still RUNNING with more known
                # polls: an idempotent no-op (the extended retained
                # facts are preserved, never regressed or re-stamped).
                pass
            else:
                # Mutated already-seen pending bytes, or an illegal
                # pending outcome transition (a terminal non-complete
                # fact never changes or reopens): a typed conflict.
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.RESULT_CONFLICT,),
                    facts.ordered_limitations,
                    cap,
                )

    # --- Same-ID immutability over the COMPLETE schema-evidenced
    # call inventory (the accepted 017 D05 law, before any
    # read-eligibility filtering): a call record whose ID matches a
    # RETAINED or STAGED known binding must carry the identical
    # endpoint/schema-family/tool-name/canonical-argument binding --
    # even when the call is read-INELIGIBLE (an unknown name or an
    # opaque custom family cannot bypass same-ID immutability by
    # becoming ineligible).  A unique unrelated unknown ID stays
    # harmless: neither recorded nor allowed to poison separate
    # valid chains.  Missing/empty/malformed IDs stay typed
    # limitations of the accepted inventory: never invented, never
    # matching.  No source acquisition follows from unsupported
    # calls.  Every membership/comparison attempt charges the ONE
    # shared ledger BEFORE it; a crossing refuses atomically.
    obsb = ns.observation_bounds
    for request in requests:
        payload = request.payload
        if request.endpoint == "responses":
            input_items = payload.get("input")
            input_list = input_items if isinstance(input_items, list) else None
            msg_list = None
        else:
            input_list = None
            messages = payload.get("messages")
            msg_list = messages if isinstance(messages, list) else None
        # The accepted 017 complete-inventory preflight, re-applied
        # BEFORE any record tuple is built: the per-container O(1)
        # length tests (outer list AND each assistant tool_calls
        # list against max_items, before any iteration) plus the
        # bounded no-retention totals against the ACTUAL 017
        # ceilings.  An over-bound request is the fixed non-acquiring
        # OVER_BOUND (already retained as an observation limitation
        # by the accepted 017 pass); its record inventory is never
        # constructed or retained here either.
        over = (input_list is not None and len(input_list) > obsb.max_items) or (
            msg_list is not None and len(msg_list) > obsb.max_items
        )
        if not over:
            for message in msg_list or ():
                if isinstance(message, dict) and message.get("role") == "assistant":
                    tool_calls = message.get("tool_calls")
                    if isinstance(tool_calls, list) and len(tool_calls) > obsb.max_items:
                        over = True
                        break
        if over:
            continue
        command_total, output_total = _inventory_totals(
            input_list, msg_list, obsb.max_commands, obsb.max_outputs
        )
        if command_total > obsb.max_commands or output_total > obsb.max_outputs:
            continue
        record_pair = _call_records(input_list, msg_list)
        records = record_pair[0] if request.endpoint == "responses" else record_pair[1]
        for call_record in records:
            wire_family, _position, _location, raw_id, raw_name, raw_arguments = call_record
            if not isinstance(raw_id, str) or not _valid_call_id(raw_id):
                continue
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
            known_binding = observed_bindings.get(raw_id)
            if known_binding is None:
                continue
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
            known_endpoint, known_name, known_fp = known_binding
            # The immutable binding includes the ACTUAL schema
            # family: the acquirable family is fixed by the endpoint
            # (the opaque custom family never carries a function-call
            # binding, whatever its name).
            expected_family = "function_call" if known_endpoint == "responses" else "function"
            if (
                wire_family != expected_family
                or not isinstance(raw_name, str)
                or not _valid_tool_name(raw_name)
                or raw_name != known_name
                or not isinstance(raw_arguments, str)
            ):
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.ISSUANCE_CONFLICT,),
                    facts.ordered_limitations,
                    cap,
                )
            inv_args = canonicalize_tool_arguments(
                raw_name,
                raw_arguments,
                max_argument_bytes=hb.max_argument_bytes,
                max_total_argument_bytes=hb.max_total_argument_bytes,
                max_argument_nodes=hb.max_argument_nodes,
                max_argument_depth=hb.max_argument_depth,
                charge_total=arg_bytes.charge,
                work=work.unit,
            )
            if not inv_args.ok:
                if inv_args.reason in (
                    CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,
                    CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,
                ):
                    # A shared-budget crossing is a resource fact:
                    # atomic typed resource refusal, never a content
                    # conflict.
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_OVER_BOUND,
                        (inv_args.reason,),
                        facts.ordered_limitations,
                        cap,
                    )
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (
                        inv_args.reason
                        if inv_args.reason is not None
                        else CausalHistoryLimitation.ISSUANCE_CONFLICT,
                    ),
                    facts.ordered_limitations,
                    cap,
                )
            if inv_args.fingerprint is None or inv_args.fingerprint != known_fp:
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.ISSUANCE_CONFLICT,),
                    facts.ordered_limitations,
                    cap,
                )

    # --- Bounded transient diagnostics + the final total cap ---------
    diagnostic_set: set[CausalHistoryLimitation] = {
        _INHERITED_DIAGNOSTIC_MAP[reason] for reason in facts.candidate_diagnostics
    }
    if replay_shifted:
        diagnostic_set.add(CausalHistoryLimitation.REPLAY_POSITION_SHIFTED)
    final_diagnostics = tuple(sorted(diagnostic_set))
    final_limitations = tuple(sorted(set(facts.ordered_limitations)))
    if len(final_diagnostics) + len(final_limitations) > cap:
        # A crossing normalizes to the ONE fixed whole-empty refusal
        # with NO copied observations (the accepted 018-c law).
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_OVER_BOUND,
            (CausalHistoryLimitation.DIAGNOSTICS_FULL,),
            (),
            cap,
        )

    # --- The after state ---------------------------------------------
    # The same retained occurrence may be observed by several requests
    # of ONE batch (an exact within-batch replay); the transition lists
    # each retained occurrence at most once (FIRST provenance kept).
    # Occurrences staged by THIS transition stay classified NEW
    # exactly once: their within-batch duplicates charged their
    # attempts but are not replay facts (the replayed list carries
    # only evidence retained BEFORE the transition, disjoint from
    # new_occurrences).
    replayed_unique = tuple(
        sorted(
            (
                o
                for o in {o.occurrence_id: o for o in replayed}.values()
                if o.occurrence_id not in staged_ids
            ),
            key=lambda o: o.occurrence_id,
        )
    )
    if (
        new_root is None
        and not new_occurrences
        and not new_links
        and not new_results
        and not updated_results
    ):
        # A pure idempotent transition (exact replays only, no new
        # evidence and no root acquisition): no revision advance, no
        # state mutation.  A legitimate root-only bootstrap IS a
        # state change (the anchor is retained) and advances the
        # revision exactly once.  018-h (H-C3): a DEFERRED unknown
        # changed envelope must reach the composition's atomic check
        # on this arm too -- a replay cannot verify it (replays earn
        # no new facts), so the composition refuses the whole
        # transition with the EXACT prior H state.
        if deferred_sink is not None:
            deferred_sink.append(facts.envelope_deferred_digests)
        return _transition(
            state,
            CausalHistoryOutcome.REPLAYED,
            final_diagnostics,
            final_limitations,
            replayed_occurrences=replayed_unique,
        )

    # Revision overflow refuses BEFORE any mutation.
    if state.revision >= MAX_REVISION:
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_OVER_BOUND,
            (CausalHistoryLimitation.REVISION_OVERFLOW,),
            (),
            cap,
        )

    results_list = list(state.results)
    for index, existing in enumerate(results_list):
        updated = updated_results.get(existing.call_id)
        if updated is not None:
            results_list[index] = updated
    # For calls ADDED by THIS batch, commit the LATEST staged record:
    # a same-batch poll extension supersedes the first staged pending
    # record (the extension keeps the FIRST original provenance via
    # model_copy), so the stale earlier record is never retained.
    for record in new_results:
        results_list.append(updated_results.get(record.call_id, record))
    new_links_tuple = tuple(new_links)
    candidate = CausalHistoryState(
        history_key=state.history_key,
        revision=state.revision + 1,
        root=new_root if new_root is not None else state.root,
        issuances=state.issuances,
        occurrences=state.occurrences + tuple(new_occurrences),
        results=tuple(results_list),
        parent_links=state.parent_links + new_links_tuple,
    )
    # The ONE bounded charged cross-record law over the candidate,
    # under the SAME shared transition ledger (no reset).
    if not work.unit():
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_OVER_BOUND,
            (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
            (),
            cap,
        )
    validation = validate_causal_history_state(candidate, bounds=hb, work=work.unit)
    if validation is not None:
        return _bounded_refusal(state, _validator_outcome(validation), (validation,), (), cap)
    if deferred_sink is not None:
        deferred_sink.append(facts.envelope_deferred_digests)
    return _transition(
        candidate,
        CausalHistoryOutcome.ACCEPTED,
        final_diagnostics,
        final_limitations,
        new_occurrences=tuple(sorted(new_occurrences, key=lambda o: o.occurrence_id)),
        replayed_occurrences=replayed_unique,
        revision_before=state.revision,
        revision_after=state.revision + 1,
    )


# --- Trusted issuance / late receipt / relation (018-d) -------------------

_HEX_DIGITS = frozenset("0123456789abcdef")


def _hex64(value: object) -> bool:
    """Strict 64-lowercase-hex fact-ID shape (no sign, no case fold)."""
    return isinstance(value, str) and len(value) == 64 and all(c in _HEX_DIGITS for c in value)


def _valid_endpoint_value(value: object) -> bool:
    return value in ("responses", "chat")


def _trusted_shape_refusal(
    state: CausalHistoryState,
    call_id: object,
    endpoint: object,
    tool_name: object,
    arguments: object,
    parent_frontier: object,
    cap: int,
) -> CausalHistoryTransition | None:
    """The immutable binding SHAPE law for trusted inputs (O(1) reads,
    no state scan): every field keeps its bounded closed shape.  A
    malformed field is a typed conflict, never a guess or a strip."""
    if not isinstance(call_id, str) or not _valid_call_id(call_id):
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_CONFLICT,
            (CausalHistoryLimitation.CALL_ID_MALFORMED,),
            (),
            cap,
        )
    if (
        not isinstance(endpoint, str)
        or not _valid_endpoint_value(endpoint)
        or not isinstance(tool_name, str)
        or not _valid_tool_name(tool_name)
        or not isinstance(arguments, str)
        or not isinstance(parent_frontier, (tuple, list))
    ):
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_CONFLICT,
            (CausalHistoryLimitation.MALFORMED_BINDING,),
            (),
            cap,
        )
    return None


def _frontier_preflight(
    parent_frontier: tuple[str, ...],
    hb: HistoryBounds,
    work: _UnitLedger,
) -> tuple[tuple[str, ...] | None, CausalHistoryLimitation | None]:
    """The frozen-frontier preflight: the ACTUAL length is checked
    BEFORE any dedup/validation/work, then EVERY member charges the
    ONE shared ledger before its shape validation (root fact or
    64-hex), and the canonical (sorted, deduplicated) form is built
    only AFTER the charges.  Returns (frontier, None) or
    (None, reason)."""
    if not parent_frontier:
        # The frozen frontier is never empty (a call is issued under
        # at least one known fact): a malformed shape, not a bound
        # crossing.
        return (None, CausalHistoryLimitation.MALFORMED_BINDING)
    if len(parent_frontier) > hb.max_frontier_members:
        return (None, CausalHistoryLimitation.FRONTIER_OVER_BOUND)
    for member in parent_frontier:
        if not work.unit():
            return (None, CausalHistoryLimitation.WORK_UNITS_OVER_BOUND)
        if member != CAUSAL_ROOT_FACT and not _hex64(member):
            return (None, CausalHistoryLimitation.FRONTIER_CONFLICT)
    return (tuple(sorted(set(parent_frontier))), None)


def _canonical_trusted_binding(
    tool_name: str,
    arguments: str,
    hb: HistoryBounds,
    arg_bytes: _ArgumentByteLedger,
    work: _UnitLedger,
) -> tuple[str | None, CausalHistoryLimitation | None, CausalHistoryOutcome | None]:
    """The SAME canonical argument recipe over the trusted binding
    (shared argument-byte and work ledgers, never reset).  Returns
    (fingerprint, None, None), or (None, reason, outcome) where a
    budget crossing is a bound refusal and a content refusal is a
    typed conflict."""
    result = canonicalize_tool_arguments(
        tool_name,
        arguments,
        max_argument_bytes=hb.max_argument_bytes,
        max_total_argument_bytes=hb.max_total_argument_bytes,
        max_argument_nodes=hb.max_argument_nodes,
        max_argument_depth=hb.max_argument_depth,
        charge_total=arg_bytes.charge,
        work=work.unit,
    )
    if not result.ok:
        reason = result.reason
        if reason is None:
            reason = CausalHistoryLimitation.ARGUMENTS_UNSUPPORTED
        if reason in (
            CausalHistoryLimitation.ARGUMENTS_OVER_BOUND,
            CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,
        ):
            return (None, reason, CausalHistoryOutcome.REFUSED_OVER_BOUND)
        return (None, reason, CausalHistoryOutcome.REFUSED_CONFLICT)
    fingerprint = result.fingerprint
    if fingerprint is None:
        raise _fixed("a successful recipe carries its fingerprint")
    return (fingerprint, None, None)


class _WorkOverflowError(ValueError):
    """The shared bounded work ledger was crossed during a charged
    closure walk: a RESOURCE fact, not a content conflict.  Query
    callers keep their documented fixed-error (ValueError) contract;
    transition callers map it to the typed atomic resource refusal
    preserving the EXACT prior state."""


def _ancestors_of(
    start: str,
    parent_map: dict[str, list[str]],
    work: _UnitLedger,
) -> set[str]:
    """Bounded iterative ancestor closure over the frozen parent
    evidence (child -> parent direction: every parent is an EARLIER
    fact).  Every edge traversal charges the ONE shared ledger; a
    crossing raises the fixed over-bound error (the caller's bounds
    are the query's contract)."""
    seen: set[str] = {start}
    stack: list[str] = [start]
    while stack:
        node = stack.pop()
        for parent in parent_map.get(node, ()):
            if not work.unit():
                raise _WorkOverflowError(
                    "a bounded relation/acyclicity walk crossed its work ceiling"
                )
            if parent not in seen:
                seen.add(parent)
                stack.append(parent)
    return seen


def register_issuance(
    state: CausalHistoryState,
    ns: CausalHistoryNamespace,
    call_id: str,
    endpoint: str,
    tool_name: str,
    arguments: str,
    parent_frontier: tuple[str, ...] | list[str],
    expected_revision: int,
) -> CausalHistoryTransition:
    """Trusted INTERNAL issuance registration (018-d).

    Issuance is NOT source acquisition or success: it records the
    EXACT call binding (endpoint family, tool name, canonical
    argument fingerprint -- raw arguments never retained) plus the
    FROZEN parent frontier of known facts (the root-anchor fact
    when the anchor is retained, and/or completed occurrence IDs)
    the call was issued under.  A reused ID with a different
    immutable binding is a typed conflict; an exact same-issued-call
    replay (same binding AND same frozen frontier) is a pure
    REPLAYED no-op; a changed frontier under the same call is a
    typed conflict.  The frontier is length-preflighted before any
    dedup/validation, every member is charged before validation,
    unknown/malformed members refuse via the bounded final state
    validation, the retention caps are cumulative and checked before
    any copy/retention, the revision overflow refuses first, and
    every refusal/replay preserves the EXACT prior state."""
    return _register_issuance_core(
        state,
        ns,
        call_id,
        endpoint,
        tool_name,
        arguments,
        parent_frontier,
        expected_revision,
    )


def _register_issuance_core(
    state: CausalHistoryState,
    ns: CausalHistoryNamespace,
    call_id: str,
    endpoint: str,
    tool_name: str,
    arguments: str,
    parent_frontier: tuple[str, ...] | list[str],
    expected_revision: int,
    *,
    context: _RootLineageContext | None = None,
) -> CausalHistoryTransition:
    """The exact registration body, factored for the 018-h private
    seam (H-D3): an optional root-lineage context couples the ONE H
    outer into the ACTUAL D work ledger.  The public wrapper runs
    it with NO context: byte-identical old law.
    """
    gated = _gate(state, ns, expected_revision)
    if gated is not None:
        return gated
    hb: HistoryBounds = ns.history_bounds
    inner = _HistoryWorkLedger(hb.max_work_units)
    work: _UnitLedger = _CoupledHistoryWorkLedger(inner, context) if context is not None else inner
    arg_bytes = _ArgumentByteLedger(hb.max_total_argument_bytes)
    cap = hb.max_diagnostics
    shape = _trusted_shape_refusal(
        state, call_id, endpoint, tool_name, arguments, parent_frontier, cap
    )
    if shape is not None:
        return shape
    # The raw supplied length is checked BEFORE any tuple conversion,
    # copy or dedup (a list/tuple length is an O(1) read; the shape
    # refusal above guarantees a sequence).
    if len(parent_frontier) > hb.max_frontier_members:
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_OVER_BOUND,
            (CausalHistoryLimitation.FRONTIER_OVER_BOUND,),
            (),
            cap,
        )
    frontier, frontier_reason = _frontier_preflight(tuple(parent_frontier), hb, work)
    if frontier is None:
        assert frontier_reason is not None
        outcome = (
            CausalHistoryOutcome.REFUSED_OVER_BOUND
            if frontier_reason
            in (
                CausalHistoryLimitation.FRONTIER_OVER_BOUND,
                CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,
            )
            else CausalHistoryOutcome.REFUSED_CONFLICT
        )
        return _bounded_refusal(state, outcome, (frontier_reason,), (), cap)
    arg_fp, arg_reason, arg_outcome = _canonical_trusted_binding(
        tool_name, arguments, hb, arg_bytes, work
    )
    if arg_fp is None:
        assert arg_reason is not None and arg_outcome is not None
        return _bounded_refusal(state, arg_outcome, (arg_reason,), (), cap)
    # --- Charged scan of prior trusted/observed identities for THIS
    # call (one unit per record visited; no uncharged full walk) ----
    prior_issuance: IssuedCall | None = None
    observed_binding: tuple[str, str, str] | None = None
    for issuance in state.issuances:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        if issuance.call_id == call_id:
            if prior_issuance is not None:
                # A duplicate retained issuance is a state invariant
                # violation (defensive; the validator also refuses).
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.ISSUANCE_CONFLICT,),
                    (),
                    cap,
                )
            prior_issuance = issuance
    for occurrence in state.occurrences:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        if occurrence.call_id == call_id:
            binding = (
                occurrence.endpoint,
                occurrence.tool_name,
                occurrence.argument_fingerprint,
            )
            if observed_binding is not None and observed_binding != binding:
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.ISSUANCE_CONFLICT,),
                    (),
                    cap,
                )
            observed_binding = binding
    for result in state.results:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        if result.call_id == call_id:
            binding = (
                result.endpoint,
                result.tool_name,
                result.argument_fingerprint,
            )
            if observed_binding is not None and observed_binding != binding:
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.ISSUANCE_CONFLICT,),
                    (),
                    cap,
                )
            observed_binding = binding
        # The per-piece observed bindings of a retained chain (the
        # poll calls) are the same immutable ID evidence: an observed
        # poll ID may never be re-issued under a different binding.
        for pcid, pendpoint, ptool, pfp in result.piece_call_bindings:
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
            if pcid == call_id:
                piece_binding = (pendpoint, ptool, pfp)
                if observed_binding is not None and observed_binding != piece_binding:
                    return _bounded_refusal(
                        state,
                        CausalHistoryOutcome.REFUSED_CONFLICT,
                        (CausalHistoryLimitation.ISSUANCE_CONFLICT,),
                        (),
                        cap,
                    )
                observed_binding = piece_binding
    binding = (endpoint, tool_name, arg_fp)
    # --- Same-ID immutability (trusted replay / conflict law) --------
    if prior_issuance is not None:
        same_binding = (
            prior_issuance.endpoint,
            prior_issuance.tool_name,
            prior_issuance.argument_fingerprint,
        ) == binding
        if same_binding and prior_issuance.parent_frontier == frontier:
            # The exact same issued call replayed under its original
            # frozen frontier: a pure idempotent no-op.
            return _transition(state, CausalHistoryOutcome.REPLAYED)
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_CONFLICT,
            (CausalHistoryLimitation.ISSUANCE_CONFLICT,),
            (),
            cap,
        )
    if observed_binding is not None and observed_binding != binding:
        # The ID already carries OBSERVED evidence under a different
        # immutable binding: a trusted issuance can never re-bind it.
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_CONFLICT,
            (CausalHistoryLimitation.ISSUANCE_CONFLICT,),
            (),
            cap,
        )
    # --- Retention caps (cumulative) + revision overflow FIRST ------
    if len(state.issuances) + 1 > hb.max_issuances:
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_OVER_BOUND,
            (CausalHistoryLimitation.ISSUANCES_OVER_BOUND,),
            (),
            cap,
        )
    if state.revision >= MAX_REVISION:
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_OVER_BOUND,
            (CausalHistoryLimitation.REVISION_OVERFLOW,),
            (),
            cap,
        )
    issuance = IssuedCall(
        call_id=call_id,
        endpoint=endpoint,
        tool_name=tool_name,
        argument_fingerprint=arg_fp,
        parent_frontier=frontier,
    )
    candidate = state.model_copy(
        update={
            "issuances": state.issuances + (issuance,),
            "revision": state.revision + 1,
        }
    )
    # The bounded final validation re-proves the frontier known-fact
    # law (root fact only when the anchor is retained; occurrence IDs
    # only when retained), binding consistency and all retention
    # ceilings -- charged on the SAME ledger.
    validation = validate_causal_history_state(candidate, bounds=hb, work=work.unit)
    if validation is not None:
        return _bounded_refusal(state, _validator_outcome(validation), (validation,), (), cap)
    return _transition(
        candidate,
        CausalHistoryOutcome.ACCEPTED,
        (),
        (),
        revision_before=state.revision,
        revision_after=state.revision + 1,
    )


def register_receipt(
    state: CausalHistoryState,
    ns: CausalHistoryNamespace,
    call_id: str,
    endpoint: str,
    tool_name: str,
    arguments: str,
    parent_frontier: tuple[str, ...] | list[str],
    expected_revision: int,
) -> CausalHistoryTransition:
    """Late trusted receipt: anchors an UNANCHORED completed read
    occurrence under the trusted issuance frontier (018-d).

    The receipt is honored ONLY when the retained occurrence exists
    and its immutable binding matches the receipt's (endpoint
    family, tool name, canonical argument fingerprint), the frozen
    frontier matches any existing issuance for the same call (a
    changed frontier under the same call is a typed conflict), every
    frontier member is a known fact (the root-anchor fact only when
    the anchor is retained) and the added edges keep the DAG
    acyclic (a cycle is a typed REFUSED_CYCLE).  An unanchored
    occurrence with no retained issuance is anchored by THIS
    receipt's issuance; an already-anchored occurrence under the
    exact same binding and frozen frontier is a pure REPLAYED
    no-op.  The stored edges of the anchored child are exactly the
    COMPLETE frozen frontier (no silently omitted incomparable
    parents).  A per-call result record is created ONLY when the
    retained immutable facts fully determine it (the legacy
    single-piece READ surface under the fixed no-session marker);
    native chain session associations are never re-derived.  All
    retention caps are cumulative and checked before any
    copy/retention, the revision overflow refuses first, and every
    refusal/replay preserves the EXACT prior state."""
    return _register_receipt_core(
        state,
        ns,
        call_id,
        endpoint,
        tool_name,
        arguments,
        parent_frontier,
        expected_revision,
    )


def _register_receipt_core(
    state: CausalHistoryState,
    ns: CausalHistoryNamespace,
    call_id: str,
    endpoint: str,
    tool_name: str,
    arguments: str,
    parent_frontier: tuple[str, ...] | list[str],
    expected_revision: int,
    *,
    context: _RootLineageContext | None = None,
) -> CausalHistoryTransition:
    """The exact registration body, factored for the 018-h private
    seam (H-D3): an optional root-lineage context couples the ONE H
    outer into the ACTUAL D work ledger.  The public wrapper runs
    it with NO context: byte-identical old law.
    """
    gated = _gate(state, ns, expected_revision)
    if gated is not None:
        return gated
    hb: HistoryBounds = ns.history_bounds
    inner = _HistoryWorkLedger(hb.max_work_units)
    work: _UnitLedger = _CoupledHistoryWorkLedger(inner, context) if context is not None else inner
    arg_bytes = _ArgumentByteLedger(hb.max_total_argument_bytes)
    cap = hb.max_diagnostics
    shape = _trusted_shape_refusal(
        state, call_id, endpoint, tool_name, arguments, parent_frontier, cap
    )
    if shape is not None:
        return shape
    # The raw supplied length is checked BEFORE any tuple conversion,
    # copy or dedup (a list/tuple length is an O(1) read; the shape
    # refusal above guarantees a sequence).
    if len(parent_frontier) > hb.max_frontier_members:
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_OVER_BOUND,
            (CausalHistoryLimitation.FRONTIER_OVER_BOUND,),
            (),
            cap,
        )
    frontier, frontier_reason = _frontier_preflight(tuple(parent_frontier), hb, work)
    if frontier is None:
        assert frontier_reason is not None
        outcome = (
            CausalHistoryOutcome.REFUSED_OVER_BOUND
            if frontier_reason
            in (
                CausalHistoryLimitation.FRONTIER_OVER_BOUND,
                CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,
            )
            else CausalHistoryOutcome.REFUSED_CONFLICT
        )
        return _bounded_refusal(state, outcome, (frontier_reason,), (), cap)
    arg_fp, arg_reason, arg_outcome = _canonical_trusted_binding(
        tool_name, arguments, hb, arg_bytes, work
    )
    if arg_fp is None:
        assert arg_reason is not None and arg_outcome is not None
        return _bounded_refusal(state, arg_outcome, (arg_reason,), (), cap)
    # --- Charged scan of the retained evidence for THIS call --------
    binding = (endpoint, tool_name, arg_fp)
    prior_occ: CompletedReadOccurrence | None = None
    prior_issuance: IssuedCall | None = None
    prior_result: ResultFingerprintRecord | None = None
    occurrence_ids: set[str] = set()
    for occurrence in state.occurrences:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        occurrence_ids.add(occurrence.occurrence_id)
        if occurrence.call_id == call_id:
            if prior_occ is not None:
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.ISSUANCE_CONFLICT,),
                    (),
                    cap,
                )
            prior_occ = occurrence
    for issuance in state.issuances:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        if issuance.call_id == call_id:
            prior_issuance = issuance
    for result in state.results:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        if result.call_id == call_id:
            prior_result = result
        # A retained per-piece observed binding under the SAME ID is
        # immutable evidence: a receipt whose binding differs from it
        # is a typed mismatch, never an anchor.
        for pcid, pendpoint, ptool, pfp in result.piece_call_bindings:
            if not work.unit():
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                    (),
                    cap,
                )
            if pcid == call_id and (pendpoint, ptool, pfp) != binding:
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.RECEIPT_BINDING_MISMATCH,),
                    (),
                    cap,
                )
    if prior_occ is None:
        # A receipt with no retained completed occurrence is a
        # spoofed/mismatched binding: typed refusal, never anchoring.
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_CONFLICT,
            (CausalHistoryLimitation.RECEIPT_BINDING_MISMATCH,),
            (),
            cap,
        )
    if (
        prior_occ.endpoint,
        prior_occ.tool_name,
        prior_occ.argument_fingerprint,
    ) != binding:
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_CONFLICT,
            (CausalHistoryLimitation.RECEIPT_BINDING_MISMATCH,),
            (),
            cap,
        )
    occ_id = prior_occ.occurrence_id
    if prior_issuance is not None:
        same_binding = (
            prior_issuance.endpoint,
            prior_issuance.tool_name,
            prior_issuance.argument_fingerprint,
        ) == binding
        if not same_binding or prior_issuance.parent_frontier != frontier:
            # A changed binding or frontier under the same call is a
            # typed conflict (the frozen frontier is immutable).
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_CONFLICT,
                (CausalHistoryLimitation.RECEIPT_BINDING_MISMATCH,),
                (),
                cap,
            )
        if prior_occ.anchored:
            # Already anchored under exactly this frozen frontier:
            # a pure idempotent no-op (the edges already exist).
            return _transition(state, CausalHistoryOutcome.REPLAYED)
    # --- Frontier members are known facts (charged per member) ------
    for member in frontier:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        if member == CAUSAL_ROOT_FACT:
            if state.root is None:
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_CONFLICT,
                    (CausalHistoryLimitation.RECEIPT_UNKNOWN_PARENT,),
                    (),
                    cap,
                )
            continue
        if member not in occurrence_ids:
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_CONFLICT,
                (CausalHistoryLimitation.RECEIPT_UNKNOWN_PARENT,),
                (),
                cap,
            )
    # --- Acyclicity: adding the edges (child <- member) creates a
    # cycle exactly when the CHILD already lies in the ancestor
    # closure of a frontier member (member -> ... -> child through
    # existing parent edges; self-membership included).  ONE charged
    # closure per member; a crossing raises the fixed over-bound
    # error.
    parent_map: dict[str, list[str]] = {}
    for link in state.parent_links:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        parent_map.setdefault(link.child, []).append(link.parent)
    for member in frontier:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        try:
            reachable = _ancestors_of(member, parent_map, work)
        except _WorkOverflowError:
            # The charged closure crossed the ONE shared
            # per-transition ledger: an atomic typed resource
            # refusal (the EXACT old state is preserved), never an
            # uncaught error.
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        if occ_id in reachable:
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_CYCLE,
                (CausalHistoryLimitation.RECEIPT_CYCLE,),
                (),
                cap,
            )
    # --- Retention caps (cumulative) + revision overflow FIRST ------
    if len(state.parent_links) + len(frontier) > hb.max_causal_links:
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_OVER_BOUND,
            (CausalHistoryLimitation.CAUSAL_LINKS_OVER_BOUND,),
            (),
            cap,
        )
    new_issuance = False
    if prior_issuance is None:
        if len(state.issuances) + 1 > hb.max_issuances:
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.ISSUANCES_OVER_BOUND,),
                (),
                cap,
            )
        new_issuance = True
    if state.revision >= MAX_REVISION:
        return _bounded_refusal(
            state,
            CausalHistoryOutcome.REFUSED_OVER_BOUND,
            (CausalHistoryLimitation.REVISION_OVERFLOW,),
            (),
            cap,
        )
    # --- Result record ONLY when the retained facts determine it ----
    new_result: ResultFingerprintRecord | None = None
    if prior_result is None:
        proof = prior_occ.proof
        if (
            proof.surface is BundleSurface.READ
            and len(proof.pieces) == 1
            and proof.pieces[0].char_length == proof.source_char_length
            and proof.pieces[0].call_id == call_id
        ):
            piece = proof.pieces[0]
            piece_facts = ((0, piece.char_length, piece.byte_length, proof.source_digest),)
            # The legacy read surface carries no completion fact
            # (the immediate result is the whole read).
            piece_completion: tuple[int | None, ...] = (None,)
            new_result = ResultFingerprintRecord(
                call_id=call_id,
                endpoint=endpoint,
                tool_name=tool_name,
                argument_fingerprint=arg_fp,
                result_fingerprint=_complete_result_fingerprint(
                    arg_fp,
                    proof.source_digest,
                    proof.source_byte_length,
                    piece_facts,
                    piece_completion,
                    _NO_SESSION_DIGEST,
                ),
                complete=True,
                first_request_index=proof.request_index,
                session_digest=_NO_SESSION_DIGEST,
                piece_facts=piece_facts,
                piece_call_bindings=((call_id, endpoint, tool_name, arg_fp),),
                piece_completion=piece_completion,
            )
            if len(state.results) + 1 > hb.max_observed_results:
                return _bounded_refusal(
                    state,
                    CausalHistoryOutcome.REFUSED_OVER_BOUND,
                    (CausalHistoryLimitation.RESULTS_OVER_BOUND,),
                    (),
                    cap,
                )
    # --- Compose the candidate (charged occurrence walk) ------------
    anchored_occ = prior_occ.model_copy(update={"anchored": True})
    new_occ_list: list[CompletedReadOccurrence] = []
    for occurrence in state.occurrences:
        if not work.unit():
            return _bounded_refusal(
                state,
                CausalHistoryOutcome.REFUSED_OVER_BOUND,
                (CausalHistoryLimitation.WORK_UNITS_OVER_BOUND,),
                (),
                cap,
            )
        new_occ_list.append(anchored_occ if occurrence.occurrence_id == occ_id else occurrence)
    update: dict[str, object] = {
        "occurrences": tuple(new_occ_list),
        "parent_links": state.parent_links
        + tuple(ParentLink(child=occ_id, parent=member) for member in frontier),
        "revision": state.revision + 1,
    }
    if new_issuance:
        update["issuances"] = state.issuances + (
            IssuedCall(
                call_id=call_id,
                endpoint=endpoint,
                tool_name=tool_name,
                argument_fingerprint=arg_fp,
                parent_frontier=frontier,
            ),
        )
    if new_result is not None:
        update["results"] = state.results + (new_result,)
    candidate = state.model_copy(update=update)
    # The bounded final validation re-proves edges == COMPLETE frozen
    # frontier, anchored semantics and acyclicity -- charged on the
    # SAME ledger.
    validation = validate_causal_history_state(candidate, bounds=hb, work=work.unit)
    if validation is not None:
        return _bounded_refusal(state, _validator_outcome(validation), (validation,), (), cap)
    return _transition(
        candidate,
        CausalHistoryOutcome.ACCEPTED,
        (),
        (),
        revision_before=state.revision,
        revision_after=state.revision + 1,
    )


def relation(
    state: CausalHistoryState,
    ns: CausalHistoryNamespace,
    a: str,
    b: str,
) -> CausalRelation:
    """Bounded occurrence-relation query over the frozen parent
    evidence (018-d).

    A pure query: no revision advance, no state mutation, its OWN
    per-query work ledger (the shared transition ledger is never
    consulted).  Foreign scope/lineage and malformed endpoint IDs
    refuse with an explicit fixed error (caller contract violations,
    not transition results).  ``same`` holds only for the same
    KNOWN completed occurrence ID; unknown or incomplete IDs are
    ``unknown`` (even equal unknown IDs); ``before``/``after`` hold
    ONLY through bounded transitive reachability over the actual
    frozen parent edges (every traversal charged; a crossing of the
    query's work ceiling raises the fixed over-bound error); two
    known unconnected events are ``incomparable`` -- siblings are
    never ordered from list, registration or receipt order."""
    if state.history_key != ns.history_key:
        raise _fixed("a relation query requires the state's own history scope")
    for actual, supported in _supported_version_pairs(ns):
        if actual != supported:
            # The SAME fail-closed actual-version law as the
            # transitions: an unsupported policy/version must refuse
            # BEFORE any positive interpretation (no false SAME/
            # UNKNOWN over acquired source).
            raise _fixed("a relation query requires the state's supported actual versions")
    if not _hex64(a) or not _hex64(b):
        raise _fixed("relation endpoints are bounded 64-hex occurrence IDs")
    work = _HistoryWorkLedger(ns.history_bounds.max_work_units)
    known: set[str] = set()
    for occurrence in state.occurrences:
        if not work.unit():
            raise _fixed("the relation query crossed its bounded work ceiling")
        known.add(occurrence.occurrence_id)
    if a == b:
        return CausalRelation.SAME if a in known else CausalRelation.UNKNOWN
    if a not in known or b not in known:
        return CausalRelation.UNKNOWN
    parent_map: dict[str, list[str]] = {}
    for link in state.parent_links:
        if not work.unit():
            raise _fixed("the relation query crossed its bounded work ceiling")
        parent_map.setdefault(link.child, []).append(link.parent)
    # Every parent is an EARLIER fact: a before b iff a lies in the
    # ancestor closure of b (a is an earlier known fact of b).
    if a in _ancestors_of(b, parent_map, work):
        return CausalRelation.BEFORE
    if b in _ancestors_of(a, parent_map, work):
        return CausalRelation.AFTER
    return CausalRelation.INCOMPARABLE
