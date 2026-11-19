"""021 deterministic bundle selection (the selection half of C03).

The inert deterministic selection layer over ACTUAL admitted
entries and VALIDATED compiled indexes (021 order item 4):

- the deterministic COMPLETE REQUIRED governance first -- the P0
  root entry plus the FILE entries that represent at least one
  path of the ROOT-SCOPED P1 BINDING CLOSURE: the root index's
  mandatory P1 deterministic candidates, closed through the
  ACQUIRED (ready, proven) P1 entries' own mandatory P1
  candidates to a fixed point;
- then the OPTIONAL entries, ranked by the ACTUAL P2/P3
  constitutional priority declared for the paths they supply
  (P4 background contributes none), then the narrower eligible
  coverage, then the stable identity -- priority affects
  injection only, never graph eligibility or admission;
- the scoped root/authority envelope (scopes / authorities /
  source-of-truth boundaries) carried from the root index;
- missing-binding guidance: a binding-closure path with NO
  PROVEN ready entry emits the exact read guidance (ordinary
  local tools, before substantive mutation) -- an opaque
  reference or an uncertain greedy co-cached row NEVER
  substitutes for the missing required content, and it can
  never suppress that guidance;
- duplicate coverage: an entry whose represented paths are ALL
  already covered is omitted WHOLE, observably; a required
  entry whose binding paths are ALL preserved by an earlier
  selected proven narrower eligible entry is omitted WHOLE,
  observably -- the narrower entry preserves all required
  information;
- the ACTUAL pinned-tokenizer budget plan decides over the ONE
  final rendered block per entry (the versioned render policy:
  the compiled body wrapped with the entry label and its
  deterministic candidate references -- the exact text the
  compiler validated against the rendered allowance):
  whole-entry optional omissions and TYPED essential overflow
  (422), never truncation, never dangling required references.

Pure and INERT: no I/O, no model calls, no recompilation due to
selection alone, no request replacement, no legacy behavior
change, no v1 runtime activation.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from .bundle_admission_models import EntryClass
from .bundle_budget import (
    BudgetDecision,
    BudgetEntry,
    BudgetOutcome,
    BundleBudgetPlan,
)
from .bundle_compiler import (
    BundleCompiledIndex,
    entry_source,
    render_compiled_index,
)
from .graph_models import _GraphFrozen
from .root_region_admission_models import RootRegionAdmissionEntry

BUNDLE_SELECTION_CONTRACT_VERSION = "cache-bundle-selection/v1"
BUNDLE_SELECTION_POLICY_VERSION = "bundle-selection-policy/v1"

#: The deterministic separator between the final rendered blocks
#: and the emitted extras of the ONE final injected text (the
#: exact combined text the aggregate decision counts with the
#: pinned tokenizer).
BUNDLE_SELECTION_INJECTION_SEPARATOR = "\n\n"

#: The closed provenance line EMITTED in the final rendered block
#: of an entry whose member origin is not fully proven (unknown
#: mixed origin / greedy-background members): the unproven
#: member paths in canonical sorted order.
SELECTION_PROVENANCE_UNPROVEN_PREFIX = (
    "provenance: unproven-member-origin boundaryless-mixed; members="
)

MAX_REPRESENTED_PATHS = 512


class SelectionOmissionReason(StrEnum):
    """The closed whole-entry omission vocabulary (observable)."""

    COVERAGE_DEDUPLICATED = "coverage_deduplicated"
    BINDING_COVERED_BY_NARROWER = "binding_covered_by_narrower"
    BUDGET = "budget"


class SelectionOutcome(StrEnum):
    """The closed selection outcome (typed overflow = 422)."""

    OK = "ok"
    REQUIRED_OVERFLOW = "required_overflow"
    ENTRY_INVALID = "entry_invalid"
    REQUEST_OVERFLOW = "request_overflow"


def _fixed(message: str) -> ValueError:
    return ValueError(message)


def _closed_logical_path(value: str) -> bool:
    """The closed logical repository-relative path fence (no
    absolute, traversal, NUL or empty segments)."""
    if not isinstance(value, str) or not value or len(value) > MAX_REPRESENTED_PATHS:
        return False
    if value.startswith("/") or "\\" in value or "\x00" in value:
        return False
    parts = value.split("/")
    return all(part not in {"", ".", ".."} for part in parts)


def _derived_represented_paths(entry: RootRegionAdmissionEntry) -> tuple[str, ...]:
    """The exact represented path set DERIVED from the ACTUAL
    admitted key record: the DISTINCT member occurrences in
    canonical sorted order (the width law is the distinct
    count).  The ROOT row derives its single normalized root
    path occurrence.  A caller-supplied set that leaves this
    derivation is refused, never adjusted."""
    occurrences = entry.key_record.member_occurrences
    if entry.entry_class is EntryClass.ROOT_ENTRY:
        if len(occurrences) != 1:
            raise _fixed("the root key record must carry the single root occurrence")
        return occurrences
    return tuple(sorted(set(occurrences)))


def _proven_member_positions(entry: RootRegionAdmissionEntry) -> frozenset[int]:
    """The member-occurrence positions whose per-member origin is
    ACTUALLY PROVEN by the retained admitted proof: the entry's
    admitted segments (original indices into the retained
    proof) that own EXACTLY ONE member position -- the accepted
    segment law then forces the proven per-member digest.  A
    boundaryless segment covering several positions proves none
    of them (unknown mixed origin); a missing proof proves
    nothing (the root row is lawed separately)."""
    proof = entry.proof
    if proof is None:
        return frozenset()
    proven: set[int] = set()
    for index in entry.admitted_segments:
        segment = proof.segments[index]
        if len(segment.member_positions) == 1 and segment.member_digest is not None:
            proven.add(segment.member_positions[0])
    return frozenset(proven)


def _derived_origin_proven(entry: RootRegionAdmissionEntry) -> bool:
    """The closed origin-attribution fact DERIVED from the actual
    admitted segment / proof and key record: the governing root
    row is always origin-proven; a FILE row is origin-proven
    only when EVERY member occurrence position is covered by a
    proven single-member admitted segment.  The accepted
    admission (and its greedy mode) cannot be made binding by a
    caller flag: a supplied flag that leaves this derivation is
    refused."""
    if entry.entry_class is EntryClass.ROOT_ENTRY:
        return True
    proven = _proven_member_positions(entry)
    return all(position in proven for position in range(len(entry.key_record.member_occurrences)))


def _unproven_member_paths(entry: RootRegionAdmissionEntry) -> tuple[str, ...]:
    """The DISTINCT member paths carrying at least one UNPROVEN
    occurrence position (the exact paths the final rendered
    block must expose as unknown mixed origin /
    greedy-background provenance; empty for a fully proven or
    root row)."""
    if entry.entry_class is EntryClass.ROOT_ENTRY:
        return ()
    proven = _proven_member_positions(entry)
    occurrences = entry.key_record.member_occurrences
    return tuple(
        sorted(
            {
                occurrences[position]
                for position in range(len(occurrences))
                if position not in proven
            }
        )
    )


class SelectionReadyEntry(_GraphFrozen):
    """ONE ready admitted entry with its validated compiled index,
    its ACTUAL represented member paths (the admission
    reverse-member-index rows for this content key; the root row
    carries its own normalized root path) and the DETERMINISTIC
    candidate paths the index was compiled with (bound into the
    full compile key and re-fenced against the index's
    dependency rows in the compiler's exact order).

    ``represented_paths`` and ``origin_proven`` are DERIVED facts,
    not caller assertions: ``represented_paths`` must equal the
    distinct ACTUAL key-record member occurrences (the root row
    its single root path) and ``origin_proven`` must equal the
    segment-derived origin fact (the governing root row is always
    proven; a FILE row is proven only when every member
    occurrence position is covered by a proven single-member
    admitted segment -- a singleton read, a whole proven bundle
    or a proven region join; a boundaryless mixed bundle with
    unknown per-member origin is never).  A supplied field that
    leaves the derivation is refused, so the accepted greedy
    admission cannot be made binding by a caller flag.  The
    law: an entry with unproven member origin is NEVER
    classified required, NEVER extends the binding closure and
    NEVER counts as coverage of a binding path -- an uncertain
    greedy attribution is never a substitute for usable required
    content; it may only be selected as optional background
    provenance.
    """

    entry: RootRegionAdmissionEntry
    index: BundleCompiledIndex
    represented_paths: tuple[str, ...] = Field(min_length=1)
    candidate_paths: tuple[str, ...] = ()
    origin_proven: bool = True

    @field_validator("represented_paths")
    @classmethod
    def _v_represented(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        # A SET of paths: distinct, closed, canonical sorted order.
        if len(set(value)) != len(value):
            raise _fixed("the represented paths must be distinct")
        for path in value:
            if not _closed_logical_path(path):
                raise _fixed("a represented path is not a closed logical path")
        return tuple(sorted(value))

    @field_validator("candidate_paths")
    @classmethod
    def _v_candidates(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        # An ORDERED demand sequence (the compiler's exact
        # candidate order; the index rows must equal it):
        # distinct, closed, order PRESERVED.
        if len(set(value)) != len(value):
            raise _fixed("the candidate paths must be distinct")
        for path in value:
            if not _closed_logical_path(path):
                raise _fixed("a candidate path is not a closed logical path")
        return value

    @model_validator(mode="after")
    def _v_join(self) -> SelectionReadyEntry:
        entry = self.entry
        index = self.index
        if index.entry_class is not entry.entry_class:
            raise _fixed("the compiled index entry class leaves the admitted entry")
        if index.content_key != entry.content_key:
            raise _fixed("the compiled index content key leaves the admitted entry")
        _text, digest, length = entry_source(entry)
        if index.source_sha256 != digest:
            raise _fixed("the compiled index source digest leaves the admitted entry")
        if index.source_byte_length != length:
            raise _fixed("the compiled index source length leaves the admitted entry")
        # The compiler's exact candidate law: the index's
        # dependency rows are the MANDATORY deterministic
        # candidates in the demand's exact order.
        if tuple(dep.path for dep in index.dependencies) != tuple(self.candidate_paths):
            raise _fixed("the candidate rows leave the compiled dependency rows")
        if len(self.represented_paths) != entry.width:
            raise _fixed("the represented path count leaves the admitted entry width")
        # The DERIVATION law: the supplied represented set must
        # be the exact distinct key-record member occurrences and
        # the supplied origin flag the ACTUAL segment-derived
        # proven fact (a mismatch is refused, never adjusted).
        if tuple(self.represented_paths) != _derived_represented_paths(entry):
            raise _fixed("the represented paths leave the admitted key record")
        if self.origin_proven is not _derived_origin_proven(entry):
            raise _fixed("the origin provenance leaves the admitted member proof")
        return self


class SelectionWorkingEntry(_GraphFrozen):
    """One selected working-set row in ACTUAL injection order
    (the final rendered block is the exact counted text)."""

    content_key: str
    entry_class: EntryClass
    required: bool
    distinct_files: int = Field(ge=1)
    tokens: int = Field(ge=0)
    allowance: int = Field(ge=1)
    rendered_block: str


class SelectionOmission(_GraphFrozen):
    """One WHOLE-entry omission (never partial, always
    observable)."""

    content_key: str
    reason: SelectionOmissionReason
    covered_by: str | None = None
    detail: str = Field(default="", max_length=256)


class SelectionMissingBinding(_GraphFrozen):
    """One binding-closure path with NO PROVEN ready entry: the
    exact acquisition guidance (read before substantive
    mutation)."""

    path: str
    acquisition_urgency: str
    guidance: str


class BundleSelectionDecision(_GraphFrozen):
    """The deterministic complete selection decision."""

    contract_version: str = BUNDLE_SELECTION_CONTRACT_VERSION
    policy_version: str = BUNDLE_SELECTION_POLICY_VERSION
    outcome: SelectionOutcome
    working_set: tuple[SelectionWorkingEntry, ...] = ()
    omitted: tuple[SelectionOmission, ...] = ()
    missing_bindings: tuple[SelectionMissingBinding, ...] = ()
    root_scopes: tuple[str, ...] = ()
    root_authorities: tuple[str, ...] = ()
    root_boundaries: tuple[str, ...] = ()
    budget: BudgetDecision
    selection_key: str = Field(pattern=r"^[0-9a-f]{64}$")


def _entry_label(entry: RootRegionAdmissionEntry) -> str:
    """The compiler's exact entry label (identity-bound to the
    content key)."""
    return f"entry-{entry.content_key[:16]}"


def _final_rendered_block(ready: SelectionReadyEntry, plan: BundleBudgetPlan) -> str:
    """The ONE final rendered compiled block for selection and
    injection: the versioned render policy over the compiled
    body plus the deterministic candidate references -- the
    exact text the compiler validated against the rendered
    allowance and the budget counts.  An entry whose member
    origin is not fully proven carries the CLOSED provenance
    line (the unproven member paths, canonical sorted order)
    appended to the block: the unknown mixed origin /
    greedy-background provenance is EMITTED in the final text,
    counted like any other injected byte, never hidden."""
    block = plan.tokenizer.render_compiled_block(
        entry_label=_entry_label(ready.entry),
        body=render_compiled_index(ready.index),
        references=tuple(ready.candidate_paths),
    )
    unproven = _unproven_member_paths(ready.entry)
    if unproven:
        block = block + "\n" + SELECTION_PROVENANCE_UNPROVEN_PREFIX + ",".join(unproven)
    return block


def _binding_closure(
    root: SelectionReadyEntry,
    entries: tuple[SelectionReadyEntry, ...],
) -> tuple[dict[str, tuple[int, str]], dict[str, int]]:
    """The root-scoped P1 BINDING CLOSURE and the ACTUAL P2/P3
    optional ranking priorities.

    Starts at the root (P0) and closes through the ACQUIRED
    proven file entries: a mandatory P1 deterministic candidate
    of any closure entry is a binding path; a proven ready entry
    representing a binding path joins the closure (its own P1
    candidates then extend the closure) to a fixed point.  P2/P3
    candidate rows of closure entries record the ACTUAL
    constitutional priority of the path for optional ranking;
    P4 background contributes none.  Unproven entries never join
    the closure and never contribute rows (no invented
    governing attribution).
    """
    binding: dict[str, tuple[int, str]] = {}
    rank: dict[str, int] = {}
    closure: list[SelectionReadyEntry] = [root]
    closure_keys: set[str] = {root.entry.content_key}
    changed = True
    while changed:
        changed = False
        for ready in closure:
            for dep in ready.index.dependencies:
                if dep.classification == "P1":
                    if dep.path not in binding:
                        binding[dep.path] = (
                            dep.constitutional_priority,
                            dep.acquisition_urgency,
                        )
                        changed = True
                elif dep.classification in ("P2", "P3"):
                    previous = rank.get(dep.path)
                    if previous is None or dep.constitutional_priority > previous:
                        rank[dep.path] = dep.constitutional_priority
        for ready in entries:
            if ready.entry.content_key in closure_keys:
                continue
            if not ready.origin_proven:
                continue
            if frozenset(ready.represented_paths) & frozenset(binding):
                closure.append(ready)
                closure_keys.add(ready.entry.content_key)
                changed = True
    return binding, rank


def _covering_entry(
    selected: tuple[tuple[SelectionReadyEntry, bool, frozenset[str]], ...],
    paths: frozenset[str],
    proven_only: bool = False,
) -> str | None:
    """The FIRST selected entry (selection order) whose
    represented set covers ``paths`` -- the deterministic
    ``covered_by`` witness (binding coverage requires a proven
    witness: unproven member origin never covers a binding)."""
    for ready, _required, covered_set in selected:
        if paths <= covered_set and (ready.origin_proven or not proven_only):
            return ready.entry.content_key
    return None


def select_working_set(
    root: SelectionReadyEntry,
    entries: tuple[SelectionReadyEntry, ...],
    plan: BundleBudgetPlan,
    *,
    requested_max_tokens: int | None = None,
    retained_images: int = 0,
    request_envelope_tokens: int = 0,
) -> BundleSelectionDecision:
    """ONE deterministic complete selection over the ACTUAL
    admitted entries and validated compiled indexes.

    Required governance (the root and every proven entry
    representing a binding-closure path) is selected COMPLETE
    before any optional entry; optional entries are whole-entry
    omissions; the final rendered blocks are counted with the
    REAL pinned tokenizer against the per-entry width x slot
    allowance, and the AGGREGATE floor(C/4) limit is decided
    over the EXACT COMBINED final injected text -- the included
    final blocks joined by the deterministic injection
    separator plus the EMITTED missing-binding guidance lines --
    counted with the real pinned tokenizer (never the SUM of
    the individual block counts); required overflow is TYPED
    (422), never truncated or dangling.
    """
    if type(plan) is not BundleBudgetPlan:
        raise _fixed("the budget plan must be the actual pinned-tokenizer plan")
    if root.entry.entry_class is not EntryClass.ROOT_ENTRY:
        raise _fixed("the selection root must be the admitted ROOT entry")
    if root.entry.root_source is None:
        raise _fixed("the selection root must carry its actual resolved root source")
    if not root.origin_proven:
        raise _fixed("the governing root row is always origin-proven")
    seen: set[str] = set()
    for ready in entries:
        if ready.entry.entry_class is not EntryClass.FILE_BUNDLE_ENTRY:
            raise _fixed("every optional or required file row must be a FILE entry")
        if ready.entry.content_key in seen:
            raise _fixed("two file rows share one admitted content key")
        seen.add(ready.entry.content_key)

    # -- root-scoped deterministic binding law -------------------------
    binding, rank = _binding_closure(root, entries)
    binding_paths = frozenset(binding)

    # Missing bindings are measured against PROVEN usable
    # coverage only: an opaque greedy row never satisfies a
    # required read, and never suppresses its guidance.
    proven_union = frozenset(root.represented_paths)
    for ready in entries:
        if ready.origin_proven:
            proven_union = proven_union | frozenset(ready.represented_paths)
    missing = tuple(
        SelectionMissingBinding(
            path=path,
            acquisition_urgency=binding[path][1],
            guidance=(f"read {path} with ordinary local tools before substantive mutation"),
        )
        for path in sorted(binding_paths - proven_union)
    )

    # -- deterministic classification and ordering ---------------------
    required: list[tuple[SelectionReadyEntry, int]] = []
    optional: list[tuple[SelectionReadyEntry, int]] = []
    for ready in entries:
        paths = frozenset(ready.represented_paths)
        bound = paths & binding_paths
        bound_priority = max((binding[p][0] for p in bound), default=0)
        rank_priority = max((rank[p] for p in paths if p in rank), default=0)
        # An entry with unproven member origin is never required:
        # an uncertain greedy attribution is never a substitute
        # for usable required content (it stays optional).
        if bound and ready.origin_proven:
            required.append((ready, bound_priority))
        else:
            optional.append((ready, rank_priority))
    required.sort(
        key=lambda item: (
            -item[1],
            len(item[0].represented_paths),
            item[0].entry.content_key,
        )
    )
    optional.sort(
        key=lambda item: (
            -item[1],
            len(item[0].represented_paths),
            item[0].entry.content_key,
        )
    )

    # -- coverage law (required complete first, then optional) ---------
    ordered: list[tuple[SelectionReadyEntry, bool]] = []
    omitted: list[SelectionOmission] = []
    selected: list[tuple[SelectionReadyEntry, bool, frozenset[str]]] = []
    covered: frozenset[str] = frozenset()
    covered_proven: frozenset[str] = frozenset()

    def _select(ready: SelectionReadyEntry, is_required: bool) -> None:
        nonlocal covered, covered_proven
        ordered.append((ready, is_required))
        paths = frozenset(ready.represented_paths)
        selected.append((ready, is_required, paths))
        covered = covered | paths
        if ready.origin_proven:
            covered_proven = covered_proven | paths

    _select(root, True)
    for ready, _priority in required:
        paths = frozenset(ready.represented_paths)
        bound = paths & binding_paths
        if bound <= covered_proven:
            omitted.append(
                SelectionOmission(
                    content_key=ready.entry.content_key,
                    reason=SelectionOmissionReason.BINDING_COVERED_BY_NARROWER,
                    covered_by=_covering_entry(tuple(selected), bound, proven_only=True),
                    detail=",".join(sorted(bound)),
                )
            )
        else:
            _select(ready, True)
    for ready, _priority in optional:
        paths = frozenset(ready.represented_paths)
        if paths <= covered:
            omitted.append(
                SelectionOmission(
                    content_key=ready.entry.content_key,
                    reason=SelectionOmissionReason.COVERAGE_DEDUPLICATED,
                    covered_by=_covering_entry(tuple(selected), paths),
                    detail=",".join(sorted(paths)),
                )
            )
        else:
            _select(ready, False)

    # -- the ONE final rendered block per selected entry ----------------
    blocks: dict[str, str] = {}
    for ready, _is_required in ordered:
        blocks[ready.entry.content_key] = _final_rendered_block(ready, plan)

    budget_entries = tuple(
        BudgetEntry(
            label=ready.entry.content_key,
            required=is_required,
            distinct_files=len(ready.represented_paths),
            rendered_block=blocks[ready.entry.content_key],
        )
        for ready, is_required in ordered
    )
    decision = plan.decide(
        budget_entries,
        requested_max_tokens=requested_max_tokens,
        retained_images=retained_images,
        request_envelope_tokens=request_envelope_tokens,
        join_separator=BUNDLE_SELECTION_INJECTION_SEPARATOR,
        final_extras=tuple(row.guidance for row in missing),
    )

    outcome = {
        BudgetOutcome.OK: SelectionOutcome.OK,
        BudgetOutcome.REQUIRED_OVERFLOW: SelectionOutcome.REQUIRED_OVERFLOW,
        BudgetOutcome.ENTRY_INVALID: SelectionOutcome.ENTRY_INVALID,
        BudgetOutcome.REQUEST_OVERFLOW: SelectionOutcome.REQUEST_OVERFLOW,
    }[decision.outcome]

    budget_omitted = tuple(
        SelectionOmission(
            content_key=row.label,
            reason=SelectionOmissionReason.BUDGET,
            covered_by=None,
            detail="whole-entry budget omission",
        )
        for row in decision.entries
        if not row.included
    )

    ordered_by_label = {
        ready.entry.content_key: (ready, is_required) for ready, is_required in ordered
    }
    working_set = tuple(
        SelectionWorkingEntry(
            content_key=row.label,
            entry_class=ordered_by_label[row.label][0].entry.entry_class,
            required=row.required,
            distinct_files=row.distinct_files,
            tokens=row.tokens,
            allowance=row.allowance,
            rendered_block=blocks[row.label],
        )
        for row in decision.entries
        if row.included
    )
    omitted_all = tuple(omitted) + budget_omitted

    material = {
        "contract_version": BUNDLE_SELECTION_CONTRACT_VERSION,
        "policy_version": BUNDLE_SELECTION_POLICY_VERSION,
        "outcome": outcome.value,
        "working_set": [
            [row.content_key, row.entry_class.value, row.required, row.tokens]
            for row in working_set
        ],
        "omitted": [[row.content_key, row.reason.value] for row in omitted_all],
        "missing_bindings": [row.path for row in missing],
        "root_scopes": list(root.index.scopes),
        "root_authorities": list(root.index.authorities),
        "root_boundaries": list(root.index.source_of_truth_boundaries),
    }
    selection_key = hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return BundleSelectionDecision(
        outcome=outcome,
        working_set=working_set,
        omitted=omitted_all,
        missing_bindings=missing,
        root_scopes=root.index.scopes,
        root_authorities=root.index.authorities,
        root_boundaries=root.index.source_of_truth_boundaries,
        budget=decision,
        selection_key=selection_key,
    )


def selection_http_status(decision: BundleSelectionDecision) -> int | None:
    """The typed failure contract mapping: every overflow /
    invalid-transform selection outcome is the fixed 422 (no
    silent truncation); a complete working set forwards."""
    if decision.outcome is SelectionOutcome.OK:
        return None
    return 422
