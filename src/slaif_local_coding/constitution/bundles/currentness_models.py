"""Nonroot currentness and overlap overlay scope, bounds, records and
the strict opaque-group identity recipe (objective 018-e, slice e;
INERT).

``CURRENTNESS_CONTRACT_VERSION = "cache-currentness/v1"``;
``CURRENTNESS_POLICY_VERSION = "currentness-policy/v1"``;
``OPAQUE_GROUP_RECIPE_VERSION = "currentness-opaque-group/v1"``.

This module binds the derived overlay's own scope identity (the ACTUAL
accepted 018-d history scope plus EVERY new currentness bound and the
ONE versioned currentness policy), defines the typed immutable output
records (per-path frontier records, per-owned-group currentness
records, the overlay) and the ONE versioned opaque-group identity
recipe over GROUP-LOCAL semantic ownership shape.  It is pure and
inert: no pipeline activation, no RAM service/locks, no compiler, no
disk, no HTTP/SSE observer and no new metrics.  The derivation itself
lives in ``currentness.py``.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from .bundle_admission_models import BoundaryClass
from .bundle_proof_models import BUNDLE_PROOF_CONTRACT_VERSION
from .causal_history_models import MAX_REVISION, CausalHistoryState
from .graph_models import (
    _check_hex64,
    _check_rel_path,
    _check_text,
    _fixed,
    _GraphFrozen,
)
from .observation_models import OBSERVER_VERSION, PRIVATE_ID_PLACEHOLDER

CURRENTNESS_CONTRACT_VERSION = "cache-currentness/v1"
CURRENTNESS_POLICY_VERSION = "currentness-policy/v1"
OPAQUE_GROUP_RECIPE_VERSION = "currentness-opaque-group/v1"

#: Fixed unknown-attribution marker inside the opaque recipe payload.
_OPAQUE_UNKNOWN = "opaque-unknown/v1"


_OPAQUE_ENCODING_PREFIX = b"currentness-opaque-group/v1\x00"


class CurrentnessBounds(_GraphFrozen):
    """New finite derived-overlay bounds (objective 018-e).

    The order fixes the defaults AND the hard ceilings exactly:
    stricter positive values are permitted and ANY wider direct
    construction is refused.  These are DERIVED units over one pure
    derivation, never token budgets or total process RSS.  The
    accepted 017/018-a/b/c/d bound sets retain their exact
    scope/units and are not reinterpreted or globally minimized.
    """

    #: Distinct represented NONROOT paths retained in the overlay.
    max_paths: int = Field(default=16384, ge=1, le=16384)
    #: Retained derived ownership-group facts.
    max_groups: int = Field(default=32768, ge=1, le=32768)
    #: Emitted association rows, each charged BEFORE its retention:
    #: one per path claim association (path <- occurrence group
    #: claim), one per DISTINCT (path, occurrence) emitted into the
    #: reverse path index (``overlapping_occurrences``) and into the
    #: frontier ``witnesses``, one per emitted group path row (group
    #: x nonroot path), and one per DISTINCT (group, path, witness)
    #: blocker association.
    max_witness_memberships: int = Field(default=65536, ge=1, le=65536)
    #: Actual attempted occurrence-pair comparisons, duplicates
    #: included before memoization lookup.
    max_relation_pairs: int = Field(default=65536, ge=1, le=65536)
    #: ONE shared work ledger over the ENTIRE derivation.
    max_work_units: int = Field(default=1048576, ge=1, le=1048576)
    #: TOTAL emitted closed-enum reason entries across all records.
    max_diagnostics: int = Field(default=64, ge=1, le=64)


class CurrentnessOutcome(StrEnum):
    """Closed derivation outcomes.

    ``ok`` carries the derived overlay; every ``refused_*`` carries
    the EXACT input state and no partial overlay.  A derivation never
    advances any revision: the overlay describes the input state and
    is not a fresh persistent revision or clock.
    """

    OK = "ok"
    REFUSED_FOREIGN_SCOPE = "refused_foreign_scope"
    REFUSED_VERSION_CONFLICT = "refused_version_conflict"
    REFUSED_STATE_MALFORMED = "refused_state_malformed"
    REFUSED_OVER_BOUND = "refused_over_bound"


class CurrentnessStatus(StrEnum):
    """Closed per-path / per-group currentness statuses."""

    CURRENT_KNOWN = "current_known"
    CURRENT_OPAQUE = "current_opaque"
    STALE = "stale"
    CONTENT_CONFLICT = "content_conflict"
    OWNERSHIP_AMBIGUITY = "ownership_ambiguity"


class CurrentnessReason(StrEnum):
    """Closed fixed blocker-reason vocabulary.

    Free-form strings and arbitrary text are rejected; no value
    echoes payload content.  A path or group may carry BOTH a stale
    and an ambiguity blocker when both are present.
    """

    #: A provably later claim with a KNOWN different digest.
    PROVEN_CHANGE = "proven_change"
    #: A provably later claim without an equality proof (unknown or
    #: differently-partitioned ownership) — conservative, never a
    #: false byte inequality.
    UNPROVEN_OWNERSHIP = "unproven_ownership"
    #: Incomparable claims that are both individually known with
    #: different digests.
    KNOWN_CONTENT_CONFLICT = "known_content_conflict"
    #: Incomparable claims without an equality proof (unknown or
    #: differently-partitioned ownership).
    OWNERSHIP_AMBIGUITY = "ownership_ambiguity"


class CurrentnessLimitation(StrEnum):
    """Closed fixed diagnostic vocabulary for derivation refusals."""

    FOREIGN_SCOPE = "foreign_scope"
    VERSION_UNSUPPORTED = "version_unsupported"
    STATE_MALFORMED = "state_malformed"
    PATHS_OVER_BOUND = "paths_over_bound"
    GROUPS_OVER_BOUND = "groups_over_bound"
    WITNESS_MEMBERSHIPS_OVER_BOUND = "witness_memberships_over_bound"
    RELATION_PAIRS_OVER_BOUND = "relation_pairs_over_bound"
    WORK_UNITS_OVER_BOUND = "work_units_over_bound"
    DIAGNOSTICS_FULL = "diagnostics_full"


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_opaque_payload(
    boundary_class: BoundaryClass,
    members: tuple[str, ...],
    group_digest: str,
    member_digests: tuple[str | None, ...],
    policy_version: str,
    proof_version: str,
    observation_version: str,
) -> bytes:
    """The unambiguous canonical encoding of ONE group's LOCAL
    semantic ownership shape.

    Bound: the boundary class, the ordered normalized member
    occurrences (repeats kept), the exact group bytes digest, the
    aligned per-member granted digests (fixed marker when unknown)
    and the three version identities that interpret the shape.
    NOT bound (provenance, never identity): group/segment index,
    member positions, full-proof digest/kind, request index, call or
    result IDs, endpoint, carrier spans.
    """
    payload = [
        OPAQUE_GROUP_RECIPE_VERSION,
        boundary_class.value,
        policy_version,
        proof_version,
        observation_version,
        group_digest,
        [m for m in members],
        [d if d is not None else _OPAQUE_UNKNOWN for d in member_digests],
    ]
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def opaque_group_identity(
    boundary_class: BoundaryClass,
    members: tuple[str, ...],
    group_digest: str,
    member_digests: tuple[str | None, ...],
    *,
    policy_version: str = CURRENTNESS_POLICY_VERSION,
    proof_version: str = BUNDLE_PROOF_CONTRACT_VERSION,
    observation_version: str = OBSERVER_VERSION,
) -> str:
    """The versioned opaque-group identity recipe
    (``currentness-opaque-group/v1``): the sha256 of the
    domain-separated encoding
    ``b"currentness-opaque-group/v1\\0"`` + canonical shape payload.

    Pure and uncharged: the caller charges the actual derivation
    work BEFORE invoking it and retains the result only within its
    bound ledger.
    """
    return _sha256_hex(
        _OPAQUE_ENCODING_PREFIX
        + _canonical_opaque_payload(
            boundary_class,
            members,
            group_digest,
            member_digests,
            policy_version,
            proof_version,
            observation_version,
        )
    )


def currentness_scope_key(
    history_key: str,
    workspace: str,
    policy_version: str,
    bounds: CurrentnessBounds,
) -> str:
    """The derived overlay's output scope identity.

    Binds the ACTUAL 018-d history scope, the workspace, the ONE
    versioned currentness policy, the ONE versioned opaque-group
    recipe and EVERY new currentness bound, so a caller tag alone
    cannot establish identity.  Recomputed on every overlay
    construction.
    """
    payload = [
        CURRENTNESS_CONTRACT_VERSION,
        policy_version,
        OPAQUE_GROUP_RECIPE_VERSION,
        history_key,
        workspace,
        json.dumps(bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
    ]
    return _sha256_hex(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))


class OpaqueGroupFacts(_GraphFrozen):
    """One retained derived ownership-group fact (group-local).

    ``identity`` is the versioned opaque recipe output over the
    GROUP-LOCAL semantic ownership shape and is recomputed and
    verified on every construction.  The original proof coordinates
    (segment index, member positions, full-proof digest/kind) are
    provenance and are deliberately NOT part of this fact.
    """

    boundary_class: BoundaryClass
    members: tuple[str, ...] = Field(min_length=1)
    group_digest: str
    member_digests: tuple[str | None, ...]
    policy_version: str = CURRENTNESS_POLICY_VERSION
    proof_version: str = BUNDLE_PROOF_CONTRACT_VERSION
    observation_version: str = OBSERVER_VERSION
    identity: str

    @field_validator("members")
    @classmethod
    def _v_members(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for member in value:
            _check_rel_path(member)
        return value

    @field_validator("group_digest", "identity")
    @classmethod
    def _v_hex(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "digest") or "digest")

    @field_validator("policy_version", "proof_version", "observation_version")
    @classmethod
    def _v_version(cls, value: str, info: object) -> str:
        return _check_text(value, getattr(info, "field_name", "version") or "version", 128)

    @field_validator("member_digests")
    @classmethod
    def _v_member_digests(cls, value: tuple[str | None, ...]) -> tuple[str | None, ...]:
        for digest in value:
            if digest is not None:
                _check_hex64(digest, "member digest")
        return value

    @model_validator(mode="after")
    def _v_shape(self) -> OpaqueGroupFacts:
        if len(self.member_digests) != len(self.members):
            raise _fixed("member digests align with the ordered member occurrences")
        if self.boundary_class is BoundaryClass.BOUNDARYLESS:
            if len(self.members) < 2:
                raise _fixed("a boundaryless group has no proven singleton form")
            if any(d is not None for d in self.member_digests):
                raise _fixed("a boundaryless group never carries a per-file digest")
        else:
            # The accepted boundary law: PROVEN exists ONLY in the
            # singleton form (a segment that actually attributes
            # exactly one member with its granted digest); EVERY
            # multi-member segment — partitioned or whole — is
            # BOUNDARYLESS with unknown per-member attribution.
            # A proven singleton's group digest IS the member's own
            # granted digest.
            if len(self.members) != 1:
                raise _fixed("a proven group has exactly one attributable member")
            if self.member_digests[0] is None:
                raise _fixed("a proven singleton grants its exact member digest")
            if self.group_digest != self.member_digests[0]:
                raise _fixed("a proven singleton group digest is the granted member digest")
        expected = opaque_group_identity(
            self.boundary_class,
            self.members,
            self.group_digest,
            self.member_digests,
            policy_version=self.policy_version,
            proof_version=self.proof_version,
            observation_version=self.observation_version,
        )
        if self.identity != expected:
            raise _fixed("opaque group identity does not match the actual group shape")
        return self


_STATUS_RANK = {
    CurrentnessStatus.STALE: 3,
    CurrentnessStatus.CONTENT_CONFLICT: 2,
    CurrentnessStatus.OWNERSHIP_AMBIGUITY: 1,
    CurrentnessStatus.CURRENT_KNOWN: 0,
    CurrentnessStatus.CURRENT_OPAQUE: 0,
}

_STALE_REASONS = (
    CurrentnessReason.PROVEN_CHANGE,
    CurrentnessReason.UNPROVEN_OWNERSHIP,
)


def _sorted_dedup(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


class GroupPathRow(_GraphFrozen):
    """One group-relative per-path currentness row.

    The status is computed against THIS group's own claim for the
    path (its relevant claim); ``reasons`` retain EVERY closed
    blocker that fired against distinct newer or incomparable
    witnesses — a content-conflict row may therefore carry BOTH
    KNOWN_CONTENT_CONFLICT and OWNERSHIP_AMBIGUITY at once, while
    stale reasons always force the stale status by worst priority —
    and ``witnesses`` name the occurrence IDs whose maximal claims
    produced them.
    """

    path: str
    status: CurrentnessStatus
    reasons: tuple[CurrentnessReason, ...] = ()
    witnesses: tuple[str, ...] = ()

    @field_validator("path")
    @classmethod
    def _v_path(cls, value: str) -> str:
        return _check_rel_path(value)

    @field_validator("witnesses")
    @classmethod
    def _v_witnesses(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for witness in value:
            _check_hex64(witness, "witness")
        if tuple(sorted(set(value))) != value:
            raise _fixed("witnesses must be sorted and deduplicated")
        return value

    @field_validator("reasons")
    @classmethod
    def _v_reasons(cls, value: tuple[CurrentnessReason, ...]) -> tuple[CurrentnessReason, ...]:
        if tuple(sorted(set(value), key=lambda r: r.value)) != value:
            raise _fixed("reasons must be sorted and deduplicated")
        return value

    @model_validator(mode="after")
    def _v_consistency(self) -> GroupPathRow:
        if self.status is CurrentnessStatus.CURRENT_KNOWN:
            if self.reasons or self.witnesses:
                raise _fixed("a current-known row carries no blockers or witnesses")
            return self
        if self.status is CurrentnessStatus.CURRENT_OPAQUE:
            if self.reasons:
                raise _fixed("a current-opaque row carries no blockers")
            return self
        if not self.reasons:
            raise _fixed("a blocked row carries its closed blocker reasons")
        has_stale = any(r in _STALE_REASONS for r in self.reasons)
        if has_stale and self.status is not CurrentnessStatus.STALE:
            raise _fixed("stale blocker reasons force a stale row by worst priority")
        if self.status is CurrentnessStatus.STALE:
            if not has_stale:
                raise _fixed("a stale row carries a stale blocker reason")
            return self
        if self.status is CurrentnessStatus.CONTENT_CONFLICT:
            if CurrentnessReason.KNOWN_CONTENT_CONFLICT not in self.reasons:
                raise _fixed("a content-conflict row carries its known-content blocker")
            return self
        if self.status is CurrentnessStatus.OWNERSHIP_AMBIGUITY:
            if tuple(self.reasons) != (CurrentnessReason.OWNERSHIP_AMBIGUITY,):
                raise _fixed("an ambiguity row cannot carry the known-conflict priority")
        return self


class CurrentnessGroupRecord(_GraphFrozen):
    """One owned-group currentness record for one retained
    occurrence.

    ``group_index`` is the occurrence-local group order (segment
    order; the whole-proof single group is index 0) — provenance for
    identification, never a clock.  ``opaque_identity`` is the
    versioned group-LOCAL recipe output; the original proof
    coordinates stay in the retained verbatim proof, unchanged.
    ``group_status`` is the worst of its per-path rows: a stale
    group never stales an unrelated group.
    """

    occurrence_id: str
    group_index: int = Field(ge=0)
    boundary_class: BoundaryClass
    members: tuple[str, ...] = Field(min_length=1)
    member_digests: tuple[str | None, ...]
    #: The proven root path that scopes this occurrence's proof
    #: (scope context only; its member occurrences are never nonroot
    #: contenders and therefore carry no path row).
    root_path: str | None = None
    opaque_identity: str
    path_rows: tuple[GroupPathRow, ...]
    group_status: CurrentnessStatus

    @field_validator("occurrence_id", "opaque_identity")
    @classmethod
    def _v_hex(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "id") or "id")

    @field_validator("members")
    @classmethod
    def _v_members(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for member in value:
            _check_rel_path(member)
        return value

    @field_validator("root_path")
    @classmethod
    def _v_root_path(cls, value: str | None) -> str | None:
        return None if value is None else _check_rel_path(value)

    @field_validator("member_digests")
    @classmethod
    def _v_member_digests(cls, value: tuple[str | None, ...]) -> tuple[str | None, ...]:
        for digest in value:
            if digest is not None:
                _check_hex64(digest, "member digest")
        return value

    @model_validator(mode="after")
    def _v_group(self) -> CurrentnessGroupRecord:
        if len(self.member_digests) != len(self.members):
            raise _fixed("member digests align with the ordered member occurrences")
        paths = tuple(row.path for row in self.path_rows)
        if paths != tuple(sorted(set(paths))):
            raise _fixed("path rows must be sorted and deduplicated by path")
        expected = {member for member in self.members if member != self.root_path}
        if set(paths) != expected:
            raise _fixed("path rows cover exactly the group's represented nonroot paths")
        if not self.path_rows and self.group_status is not CurrentnessStatus.CURRENT_OPAQUE:
            raise _fixed("a group without nonroot paths is current-opaque only")
        if not self.path_rows:
            return self
        if any(row.status is CurrentnessStatus.STALE for row in self.path_rows):
            expected_status = CurrentnessStatus.STALE
        elif any(row.status is CurrentnessStatus.CONTENT_CONFLICT for row in self.path_rows):
            expected_status = CurrentnessStatus.CONTENT_CONFLICT
        elif any(row.status is CurrentnessStatus.OWNERSHIP_AMBIGUITY for row in self.path_rows):
            expected_status = CurrentnessStatus.OWNERSHIP_AMBIGUITY
        elif all(row.status is CurrentnessStatus.CURRENT_KNOWN for row in self.path_rows):
            expected_status = CurrentnessStatus.CURRENT_KNOWN
        else:
            # All rows current with at least one unattributed (opaque)
            # row: the group as a whole is NOT individually known.
            expected_status = CurrentnessStatus.CURRENT_OPAQUE
        if expected_status is not self.group_status:
            raise _fixed("group status must be the exact worst of its path rows")
        return self


class CurrentnessPathRecord(_GraphFrozen):
    """One GLOBAL maximal-frontier summary for one represented
    NONROOT path.

    The status aggregates the path's MAXIMAL completed-occurrence
    claims (all retained; equality never manufactures an edge;
    siblings are never ordered): all maximal claims known with the
    same single digest -> CURRENT_KNOWN with that digest; all maximal
    claims unattributed within the same single opaque group ->
    CURRENT_OPAQUE with that identity; any two maximal claims both
    individually known with different digests (including repeated
    same-occurrence claims) -> CONTENT_CONFLICT; any known-versus-
    unattributed mix or different opaque identities ->
    OWNERSHIP_AMBIGUITY.  A maximal frontier is an antichain, so
    STALE never occurs at this level: staleness is a historical
    CANDIDATE fact, carried per group record (an old group may be
    STALE while this path is CURRENT_KNOWN at the new version).
    ``witnesses`` retain ALL maximal occurrence IDs (frontier
    evidence, not a last-writer selection).  Blocked paths assert no
    single current content (both content fields stay exact-None; the
    witnesses' verbatim retained proofs carry the exact bytes).
    """

    path: str
    status: CurrentnessStatus
    known_digest: str | None = None
    opaque_identity: str | None = None
    reasons: tuple[CurrentnessReason, ...] = ()
    witnesses: tuple[str, ...]
    #: The reverse path index entry: EVERY retained occurrence that
    #: represents this path (ALL group overlaps, dominated witnesses
    #: included) — not only the maximal frontier witnesses.
    overlapping_occurrences: tuple[str, ...]

    @field_validator("path")
    @classmethod
    def _v_path(cls, value: str) -> str:
        return _check_rel_path(value)

    @field_validator("known_digest")
    @classmethod
    def _v_known(cls, value: str | None) -> str | None:
        return None if value is None else _check_hex64(value, "known digest")

    @field_validator("opaque_identity")
    @classmethod
    def _v_opaque(cls, value: str | None) -> str | None:
        return None if value is None else _check_hex64(value, "opaque identity")

    @field_validator("witnesses", "overlapping_occurrences")
    @classmethod
    def _v_occurrence_lists(cls, value: tuple[str, ...], info: object) -> tuple[str, ...]:
        name = getattr(info, "field_name", "list") or "list"
        if not value:
            raise _fixed(f"a represented path retains its {name}")
        for item in value:
            _check_hex64(item, f"{name} occurrence")
        if tuple(sorted(set(value))) != value:
            raise _fixed(f"{name} must be sorted and deduplicated")
        return value

    @field_validator("reasons")
    @classmethod
    def _v_reasons(cls, value: tuple[CurrentnessReason, ...]) -> tuple[CurrentnessReason, ...]:
        if tuple(sorted(set(value), key=lambda r: r.value)) != value:
            raise _fixed("reasons must be sorted and deduplicated")
        return value

    @model_validator(mode="after")
    def _v_consistency(self) -> CurrentnessPathRecord:
        if set(self.witnesses) - set(self.overlapping_occurrences):
            raise _fixed("maximal witnesses are a subset of all overlapping occurrences")
        if self.status is CurrentnessStatus.CURRENT_KNOWN:
            if self.known_digest is None or self.opaque_identity is not None:
                raise _fixed("a current-known path carries its exact digest only")
            if self.reasons:
                raise _fixed("a current-known path carries no blockers")
            return self
        if self.status is CurrentnessStatus.CURRENT_OPAQUE:
            if self.opaque_identity is None or self.known_digest is not None:
                raise _fixed("a current-opaque path carries its exact identity only")
            if self.reasons:
                raise _fixed("a current-opaque path carries no blockers")
            return self
        if self.status is CurrentnessStatus.STALE:
            # A maximal frontier is an antichain: STALE is a
            # historical CANDIDATE fact carried per group record,
            # never a global path summary.
            raise _fixed("a global maximal-frontier path can never be stale")
        if self.known_digest is not None or self.opaque_identity is not None or not self.reasons:
            raise _fixed("a blocked path asserts no single current content")
        if self.status is CurrentnessStatus.CONTENT_CONFLICT:
            if tuple(self.reasons) != (CurrentnessReason.KNOWN_CONTENT_CONFLICT,):
                raise _fixed("a content-conflict path carries only its known-content blocker")
            return self
        if tuple(self.reasons) != (CurrentnessReason.OWNERSHIP_AMBIGUITY,):
            raise _fixed("an ambiguous path carries only its ownership-ambiguity blocker")
        return self


class CurrentnessOverlay(_GraphFrozen):
    """One derived nonroot currentness overlay for the EXACT input
    history scope/revision it describes.

    The overlay is a pure derivation output: it is not a fresh
    persistent revision or clock, it never mutates the input state,
    and it confers no compiler-semantic key on any unchanged source.
    ``scope_key`` binds the actual history scope, the workspace, the
    ONE versioned currentness policy and EVERY new currentness bound
    (recomputed on every construction; a caller tag alone cannot
    establish identity).  ``emitted_reasons`` is the TOTAL closed-
    enum reason entries across every path and group row and never
    exceeds the hard diagnostic ceiling.
    """

    history_key: str
    revision: int = Field(ge=0, le=MAX_REVISION)
    workspace: str
    policy_version: str = CURRENTNESS_POLICY_VERSION
    bounds: CurrentnessBounds = Field(default_factory=CurrentnessBounds)
    scope_key: str
    paths: tuple[CurrentnessPathRecord, ...] = ()
    groups: tuple[CurrentnessGroupRecord, ...] = ()
    usable_occurrences: tuple[str, ...] = ()
    emitted_reasons: int = Field(ge=0, le=64)

    @field_validator("history_key", "scope_key")
    @classmethod
    def _v_hex(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "key") or "key")

    @field_validator("workspace")
    @classmethod
    def _v_workspace(cls, value: str) -> str:
        return _check_text(value, "workspace", 1024)

    @field_validator("policy_version")
    @classmethod
    def _v_policy(cls, value: str) -> str:
        return _check_text(value, "policy_version", 128)

    @field_validator("paths")
    @classmethod
    def _v_paths(
        cls, value: tuple[CurrentnessPathRecord, ...]
    ) -> tuple[CurrentnessPathRecord, ...]:
        paths = tuple(record.path for record in value)
        if paths != tuple(sorted(set(paths))):
            raise _fixed("path records must be sorted and deduplicated by path")
        return value

    @field_validator("groups")
    @classmethod
    def _v_groups(
        cls, value: tuple[CurrentnessGroupRecord, ...]
    ) -> tuple[CurrentnessGroupRecord, ...]:
        keys = [(record.occurrence_id, record.group_index) for record in value]
        if keys != sorted(keys) or len(set(keys)) != len(keys):
            raise _fixed("group records must be sorted and deduplicated")
        return value

    @field_validator("usable_occurrences")
    @classmethod
    def _v_usable(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for occurrence_id in value:
            _check_hex64(occurrence_id, "usable occurrence")
        if tuple(sorted(set(value))) != value:
            raise _fixed("usable occurrences must be sorted and deduplicated")
        return value

    @model_validator(mode="after")
    def _v_overlay(self) -> CurrentnessOverlay:
        if len(self.paths) > self.bounds.max_paths:
            raise _fixed("path records exceed the bound path ceiling")
        if len(self.groups) > self.bounds.max_groups:
            raise _fixed("group records exceed the bound group ceiling")
        total = sum(len(record.reasons) for record in self.paths)
        for group in self.groups:
            for row in group.path_rows:
                total += len(row.reasons)
        if total != self.emitted_reasons:
            raise _fixed("emitted reasons must equal the actual emitted total")
        if total > self.bounds.max_diagnostics:
            raise _fixed("emitted reasons exceed the hard diagnostic ceiling")
        expected = currentness_scope_key(
            self.history_key, self.workspace, self.policy_version, self.bounds
        )
        if self.scope_key != expected:
            raise _fixed("scope key does not match the actual scope fields")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CurrentnessOverlay(history_key={self.history_key!r}, "
            f"revision={self.revision}, workspace={PRIVATE_ID_PLACEHOLDER}, "
            f"policy_version={self.policy_version!r}, "
            f"scope_key={self.scope_key!r}, paths={len(self.paths)}, "
            f"groups={len(self.groups)}, "
            f"usable_occurrences={len(self.usable_occurrences)}, "
            f"emitted_reasons={self.emitted_reasons})"
        )

    __str__ = __repr__


class CurrentnessResult(_GraphFrozen):
    """One bounded currentness derivation result.

    ``state`` is ALWAYS the EXACT input state object (identity
    preserved on every outcome; the input is immutable and the
    derivation never mutates or re-orders it).  ``ok`` carries the
    derived overlay and no diagnostics; every refusal carries no
    partial overlay and its closed diagnostic reasons.
    """

    outcome: CurrentnessOutcome
    state: CausalHistoryState
    overlay: CurrentnessOverlay | None = None
    diagnostics: tuple[CurrentnessLimitation, ...] = ()

    @field_validator("diagnostics")
    @classmethod
    def _v_diagnostics(
        cls, value: tuple[CurrentnessLimitation, ...]
    ) -> tuple[CurrentnessLimitation, ...]:
        if tuple(sorted(set(value), key=lambda r: r.value)) != value:
            raise _fixed("diagnostics must be sorted and deduplicated")
        return value

    @model_validator(mode="after")
    def _v_result(self) -> CurrentnessResult:
        if self.outcome is CurrentnessOutcome.OK:
            if self.overlay is None or self.diagnostics:
                raise _fixed("an ok result carries its overlay and no diagnostics")
            return self
        if self.overlay is not None or not self.diagnostics:
            raise _fixed("a refusal carries no partial overlay and its closed reasons")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CurrentnessResult(outcome={self.outcome.value!r}, "
            f"overlay={'yes' if self.overlay is not None else 'no'}, "
            f"diagnostics={list(self.diagnostics)})"
        )

    __str__ = __repr__
