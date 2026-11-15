"""Current graph closure and version-owned withdrawal scope, bounds,
records and the strict current-graph identity recipe
(objective 018-f, slice f; INERT).

``CURRENT_GRAPH_CONTRACT_VERSION = "cache-current-graph/v1"``;
``CURRENT_GRAPH_POLICY_VERSION = "current-graph-policy/v1"``.

This module binds the derived current graph's OWN scope identity
(the ACTUAL accepted 018-d history scope plus the ACTUAL root
anchor facts, the inherited graph/reference/proof/currentness
versions, the ACTUAL 018-e bounds and bounds snapshot, and EVERY
new current-graph bound), defines the typed immutable output
records (selected current source suppliers, nodes, version-owned
ordinary/group edges, group certificates, retained candidate
evidence) and the ONE versioned current-graph scope-key recipe.
It is pure and inert: no pipeline activation, no RAM service/
locks, no compiler, no disk, no HTTP/SSE observer and no new
metrics.  The derivation itself lives in ``current_graph.py``.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from .causal_history_models import MAX_REVISION, CausalHistoryState
from .currentness_models import (
    CURRENTNESS_CONTRACT_VERSION,
    CURRENTNESS_POLICY_VERSION,
    OPAQUE_GROUP_RECIPE_VERSION,
    CurrentnessBounds,
)
from .graph_models import (
    ROOT_FILENAME,
    GraphBounds,
    ReferenceCandidate,
    _check_hex64,
    _check_rel_path,
    _check_text,
    _fixed,
    _GraphFrozen,
)
from .observation_models import EMPTY_SOURCE_SHA256, PRIVATE_ID_PLACEHOLDER

CURRENT_GRAPH_CONTRACT_VERSION = "cache-current-graph/v1"
CURRENT_GRAPH_POLICY_VERSION = "current-graph-policy/v1"

#: Closed owner label for the root node/edges (the RootAnchor is
#: the ONLY root-text supplier; the anchor is scope, not a file
#: supplier with occurrence witnesses).
ROOT_OWNER = "root-anchor/v1"


_SOURCE_OWNER_PREFIX = b"current-graph-source/v1\0"
_GROUP_OWNER_PREFIX = b"current-graph-group/v1\0"

#: Fixed placeholder for workspace path VALUES in operational
#: representations (the 018-f fixed enums/counts/private-repr law:
#: path values are private; counts and the presence flag stay
#: observable; the actual internal path fields are unchanged).
PRIVATE_PATH_PLACEHOLDER = "<private-path>"


def _owner_source(path: str, digest: str) -> str:
    """The bounded version-owned identity of a CURRENT proven source.

    The sha256 of the domain-separated canonical ``(path, digest)``
    payload: a 64-hex identity, observable like a digest, with NO
    path embedding (no arbitrary text cap, no control characters) —
    consistent with the inherited path/digest units.  Recomputed on
    every node construction; the private inputs hashing into it are
    the actual current member path and granted digest (both already
    retained observably on the record itself).
    """
    return hashlib.sha256(
        _SOURCE_OWNER_PREFIX + path.encode("utf-8") + b"\0" + digest.encode("ascii")
    ).hexdigest()


def _owner_group(identity: str, group_digest: str) -> str:
    """The bounded version-owned identity of a CURRENT opaque group.

    The sha256 of the domain-separated canonical
    ``(opaque identity, group digest)`` payload: a 64-hex identity,
    observable like a digest (no path embedding, no control
    characters).  The opaque identity already binds the group-local
    semantic ownership shape and the bound version identities.
    """
    return hashlib.sha256(
        _GROUP_OWNER_PREFIX + identity.encode("ascii") + b"\0" + group_digest.encode("ascii")
    ).hexdigest()


def _check_owner(value: str, field: str) -> str:
    """Owner shape law: the closed root-anchor label or a bounded
    64-hex version-owned identity (never free text)."""
    if value == ROOT_OWNER:
        return value
    return _check_hex64(value, field)


def _candidate_facts(candidate: ReferenceCandidate) -> str:
    """Fixed-vocabulary summary of one retained candidate for
    operational representations: closed enums, counts and spans
    only.  The accepted ``ReferenceCandidate`` repr prints path
    values, so 018-f records never interpolate it directly; the
    raw target and all path values stay private."""
    return (
        f"candidate=syntax={candidate.syntax.value!r}, "
        f"status={candidate.status.value!r}, occurrence_index={candidate.occurrence_index}, "
        f"target_length={len(candidate.target_chars)}, "
        f"target_char_span={candidate.target_char_span!r}, "
        f"reasons={[r.value for r in candidate.reasons]!r}"
    )


class CurrentGraphBounds(_GraphFrozen):
    """New finite per-DERIVATION current-graph bounds
    (objective 018-f).

    The order fixes the defaults AND the hard ceilings exactly:
    stricter positive values are permitted and ANY wider direct
    construction is refused.  These are DERIVED units over one
    pure derivation, never token budgets or total process RSS.
    The accepted 017/018-a/b/c/d/e bound sets retain their exact
    scope/units and are not reinterpreted or globally minimized.
    """

    #: ONE OUTER work ledger over the ENTIRE operation: actual
    #: currentness/history-validation work, group selection/
    #: interning, source/reference work, closure relaxations and
    #: output, all charged BEFORE the crossing operation.
    max_total_work_units: int = Field(default=1048576, ge=1, le=1048576)
    #: TOTAL newly emitted graph closed limitation/reason entries
    #: across stage/per-record diagnostics (node blocked reasons,
    #: certificate usability reasons, stage-level refusals),
    #: charged before each actual emission attempt; duplicates
    #: count before output dedup.  Retained input-state
    #: diagnostics are not new emissions, and the nested 018-e
    #: overlay is not re-exposed as output (its validated scope/
    #: revision and the selected supplier facts are carried
    #: instead), so its emitted reasons are not re-emitted here.
    max_diagnostics: int = Field(default=64, ge=1, le=64)


class CurrentGraphOutcome(StrEnum):
    """Closed derivation outcomes.

    ``ok`` carries the derived current graph; every ``refused_*``
    carries the EXACT input state and NO partial graph.  A
    derivation never advances any revision: the graph describes
    the input state and is not a fresh persistent revision or
    clock.
    """

    OK = "ok"
    REFUSED_FOREIGN_SCOPE = "refused_foreign_scope"
    REFUSED_VERSION_CONFLICT = "refused_version_conflict"
    REFUSED_STATE_MALFORMED = "refused_state_malformed"
    REFUSED_NO_ROOT = "refused_no_root"
    REFUSED_OVER_BOUND = "refused_over_bound"


class CurrentGraphStatus(StrEnum):
    """Closed node statuses (honest source availability)."""

    #: Possessed CURRENT known source with its exact digest;
    #: scannable for outgoing references.
    CURRENT_KNOWN = "current_known"
    #: Possessed CURRENT source with the earned empty digest; it
    #: acquires NO outgoing edges.
    CURRENT_EMPTY = "current_empty"
    #: Referenced by an accepted derivation but not possessed as a
    #: current source: an honest unavailable state (reference
    #: establishes eligibility, not possession).
    DISCOVERED_UNACQUIRED = "discovered_unacquired"
    #: Referenced, but the path currentness is a known-content
    #: conflict: no single current content, no acquisition.
    BLOCKED_CONFLICT = "blocked_conflict"
    #: Referenced, but the path currentness is ownership
    #: ambiguity: no single current content, no acquisition.
    BLOCKED_AMBIGUITY = "blocked_ambiguity"


class CurrentGraphReason(StrEnum):
    """Closed fixed certificate-unavailability reasons.

    Free-form strings and arbitrary text are rejected; no value
    echoes payload content.  A certificate may carry several
    reasons at once (every closed blocker that applies).
    """

    #: At least one non-root possible supplier was not
    #: independently current AND reachable in the joint fixed
    #: point (no self-bootstrap).
    NOT_INDEPENDENTLY_REACHABLE = "not_independently_reachable"
    #: The non-root possible suppliers do not share the SAME
    #: canonical lexical directory (the accepted common base;
    #: convergent absolute references never compensate).
    NO_COMMON_DIRECTORY = "no_common_directory"
    #: The group contains a ROOT member: its unattributed root
    #: bytes are never certified against the anchor, so the
    #: certificate stays unresolved evidence (strict).
    ROOT_MEMBER_UNATTRIBUTED = "root_member_unattributed"
    #: No non-root possible supplier exists (root-only group).
    NO_SUPPLIER = "no_supplier"


class CurrentGraphLimitation(StrEnum):
    """Closed fixed diagnostic vocabulary for derivation
    refusals (exact per-domain names; a refusal carries the ONE
    crossed domain's limitation)."""

    FOREIGN_SCOPE = "foreign_scope"
    VERSION_UNSUPPORTED = "version_unsupported"
    STATE_MALFORMED = "state_malformed"
    ROOT_MISSING = "root_missing"
    ROOT_MALFORMED = "root_malformed"
    # Outer current-graph domains (this slice).
    TOTAL_WORK_UNITS_OVER_BOUND = "total_work_units_over_bound"
    DIAGNOSTICS_FULL = "diagnostics_full"
    # Graph-stage domains (the ACTUAL inherited GraphBounds).
    GRAPH_NODES_OVER_BOUND = "graph_nodes_over_bound"
    GRAPH_EDGES_OVER_BOUND = "graph_edges_over_bound"
    GRAPH_CANDIDATES_OVER_BOUND = "graph_candidates_over_bound"
    GRAPH_DOCUMENTS_OVER_BOUND = "graph_documents_over_bound"
    GRAPH_SOURCE_BYTES_OVER_BOUND = "graph_source_bytes_over_bound"
    GRAPH_DEPTH_OVER_BOUND = "graph_depth_over_bound"
    GRAPH_WORK_UNITS_OVER_BOUND = "graph_work_units_over_bound"
    GRAPH_DIAGNOSTICS_OVER_BOUND = "graph_diagnostics_over_bound"
    # 018-e currentness domains (surfaced through the private
    # shared-derivation seam; the 018-e limits keep their scope).
    PATHS_OVER_BOUND = "paths_over_bound"
    GROUPS_OVER_BOUND = "groups_over_bound"
    WITNESS_MEMBERSHIPS_OVER_BOUND = "witness_memberships_over_bound"
    RELATION_PAIRS_OVER_BOUND = "relation_pairs_over_bound"
    CURRENTNESS_WORK_UNITS_OVER_BOUND = "currentness_work_units_over_bound"
    CURRENTNESS_DIAGNOSTICS_OVER_BOUND = "currentness_diagnostics_over_bound"
    # 018-d history domains.
    HISTORY_WORK_UNITS_OVER_BOUND = "history_work_units_over_bound"


class CurrentGraphSupplierKind(StrEnum):
    """Closed supplier kinds (selected BEFORE scanning)."""

    #: The RootAnchor: the ONLY root-text supplier.
    ROOT = "root"
    #: A CURRENT proven singleton group (its exact member bytes).
    SOURCE = "source"
    #: A CURRENT boundaryless opaque group (its exact aggregate
    #: segment bytes; indivisible, no per-file supply).
    GROUP = "group"


class CurrentGraphEdgeKind(StrEnum):
    """Closed edge kinds (separately typed facts, ONE shared
    GraphBounds.max_edges bound for their COMBINED count)."""

    ORDINARY = "ordinary"
    GROUP = "group"


class CurrentGraphOrigin(_GraphFrozen):
    """One retained ORIGINAL proof/group coordinate of a selected
    supplier (provenance only; never a clock, never identity
    material)."""

    occurrence_id: str
    group_index: int = Field(ge=0)
    request_index: int = Field(ge=0)
    call_position: int = Field(ge=0)
    result_position: int = Field(ge=0)

    @field_validator("occurrence_id")
    @classmethod
    def _v_occurrence(cls, value: str) -> str:
        return _check_hex64(value, "occurrence id")

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CurrentGraphOrigin(occurrence_id={self.occurrence_id!r}, "
            f"group_index={self.group_index}, request_index={self.request_index}, "
            f"call_position={self.call_position}, result_position={self.result_position})"
        )

    __str__ = __repr__


class CurrentGraphSupplier(_GraphFrozen):
    """One selected CURRENT source supplier (before any scan).

    ``path``/``digest`` identify a ROOT or SOURCE supplier (the
    root anchor facts, or the proven member with its granted
    digest); a GROUP supplier has ``path``/``digest`` exact-None
    (no per-file supply or hash) and carries the versioned opaque
    identity plus the exact aggregate group digest.  ``members``
    retain the ordered normalized member occurrences (repeats
    kept); ``witnesses`` ALL supporting occurrence IDs (first
    provenance, never relabeled); ``coordinates`` the ORIGINAL
    proof/group coordinates per contributing group.
    """

    kind: CurrentGraphSupplierKind
    path: str | None = None
    digest: str | None = None
    identity: str | None = None
    group_digest: str | None = None
    members: tuple[str, ...] = ()
    witnesses: tuple[str, ...] = ()
    coordinates: tuple[CurrentGraphOrigin, ...] = ()

    @field_validator("path")
    @classmethod
    def _v_path(cls, value: str | None) -> str | None:
        return None if value is None else _check_rel_path(value)

    @field_validator("digest", "identity", "group_digest")
    @classmethod
    def _v_hex(cls, value: str | None, info: object) -> str | None:
        return (
            None
            if value is None
            else _check_hex64(value, getattr(info, "field_name", "digest") or "digest")
        )

    @field_validator("members")
    @classmethod
    def _v_members(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for member in value:
            _check_rel_path(member)
        return value

    @field_validator("witnesses")
    @classmethod
    def _v_witnesses(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for witness in value:
            _check_hex64(witness, "witness occurrence")
        if tuple(sorted(set(value))) != value:
            raise _fixed("witnesses must be sorted and deduplicated")
        return value

    @model_validator(mode="after")
    def _v_supplier(self) -> CurrentGraphSupplier:
        if self.kind is CurrentGraphSupplierKind.ROOT:
            if self.path != ROOT_FILENAME or self.digest is None:
                raise _fixed("a root supplier is the root anchor at its exact digest")
            if self.identity or self.group_digest or self.members or self.witnesses:
                raise _fixed("a root supplier carries anchor facts only")
            return self
        if self.kind is CurrentGraphSupplierKind.SOURCE:
            if self.path is None or self.digest is None:
                raise _fixed("a source supplier names its member and granted digest")
            if self.path == ROOT_FILENAME:
                raise _fixed("the root anchor is the ONLY root-text supplier")
            if self.identity or self.group_digest:
                raise _fixed("a source supplier carries no group identity")
            if self.members != (self.path,):
                raise _fixed("a proven source supplier owns exactly one member occurrence")
            if not self.witnesses or not self.coordinates:
                raise _fixed("a source supplier retains its witnesses and origin")
            return self
        if self.path is not None or self.digest is not None:
            raise _fixed("an opaque group supplier supplies no per-file path or hash")
        if self.identity is None or self.group_digest is None:
            raise _fixed("an opaque group supplier carries its exact identity and digest")
        if len(self.members) < 2:
            raise _fixed("an opaque group supplier has at least two ordered members")
        if all(member == ROOT_FILENAME for member in self.members):
            raise _fixed("a root-only group supplies nothing and is never a supplier")
        if not self.witnesses or not self.coordinates:
            raise _fixed("an opaque group supplier retains its witnesses and origin")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CurrentGraphSupplier(kind={self.kind.value!r}, "
            f"path={PRIVATE_PATH_PLACEHOLDER if self.path is not None else 'None'}, "
            f"digest={self.digest!r}, identity={self.identity!r}, "
            f"group_digest={self.group_digest!r}, members={len(self.members)}, "
            f"witnesses={len(self.witnesses)}, coordinates={len(self.coordinates)})"
        )

    __str__ = __repr__


class CurrentGraphNode(_GraphFrozen):
    """One current-graph node for one represented workspace path.

    ``status`` is the honest availability state (see
    ``CurrentGraphStatus``); only CURRENT_KNOWN nodes are
    scannable (CURRENT_EMPTY acquires no outgoing edges).
    ``owner`` is the version-owned identity of the ACTUAL current
    source that acquires the node (the root anchor for the root;
    a current proven source for a current node); unavailable/
    blocked nodes carry owner exact-None.  ``depth`` is the
    target's LEAST complete derivation depth after the bounded
    fixed point (root 0; a shallower re-visit never deepens a
    walk; root self/back-cycle targets stay 0).
    """

    path: str
    status: CurrentGraphStatus
    digest: str | None = None
    owner: str | None = None
    witnesses: tuple[str, ...] = ()
    depth: int = Field(ge=0)

    @field_validator("path")
    @classmethod
    def _v_path(cls, value: str) -> str:
        return _check_rel_path(value)

    @field_validator("digest")
    @classmethod
    def _v_digest(cls, value: str | None) -> str | None:
        return None if value is None else _check_hex64(value, "node digest")

    @field_validator("owner")
    @classmethod
    def _v_owner(cls, value: str | None) -> str | None:
        return None if value is None else _check_owner(value, "owner")

    @field_validator("witnesses")
    @classmethod
    def _v_witnesses(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for witness in value:
            _check_hex64(witness, "witness occurrence")
        if tuple(sorted(set(value))) != value:
            raise _fixed("witnesses must be sorted and deduplicated")
        return value

    @model_validator(mode="after")
    def _v_node(self) -> CurrentGraphNode:
        if self.path == ROOT_FILENAME:
            if self.status is not CurrentGraphStatus.CURRENT_KNOWN:
                raise _fixed("the root node is the current root anchor only")
            if self.owner != ROOT_OWNER or self.digest is None:
                raise _fixed("the root node carries its anchor owner and digest")
            if self.depth != 0:
                raise _fixed("the root node depth stays 0")
            return self
        if self.status is CurrentGraphStatus.CURRENT_KNOWN:
            if self.digest is None or self.digest == EMPTY_SOURCE_SHA256:
                raise _fixed("a current-known node carries its nonempty digest")
            if not self.owner or self.owner == ROOT_OWNER:
                raise _fixed("a nonroot current node names its current source owner")
            if not self.witnesses:
                raise _fixed("a current node retains its witness occurrences")
            if self.owner != _owner_source(self.path, self.digest):
                raise _fixed("a current-known node owner binds its exact path and digest")
            return self
        if self.status is CurrentGraphStatus.CURRENT_EMPTY:
            if self.digest != EMPTY_SOURCE_SHA256:
                raise _fixed("a current-empty node carries the exact empty digest")
            if not self.owner or self.owner == ROOT_OWNER:
                raise _fixed("a current-empty node names its source owner")
            if not self.witnesses:
                raise _fixed("a current-empty node retains its witness provenance")
            if self.owner != _owner_source(self.path, self.digest):
                raise _fixed("a current-empty node owner binds its exact path and digest")
            return self
        if self.digest is not None or self.owner is not None or self.witnesses:
            raise _fixed("an unavailable node asserts no current content or owner")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CurrentGraphNode(path={PRIVATE_PATH_PLACEHOLDER}, "
            f"status={self.status.value!r}, digest={self.digest!r}, "
            f"owner={self.owner!r}, witnesses={len(self.witnesses)}, depth={self.depth})"
        )

    __str__ = __repr__


class CurrentGraphEdge(_GraphFrozen):
    """One version-owned ordinary or group derivation.

    ``owner`` ties the derivation to the ACTUAL current semantic
    source/group digest/shape that supplies it plus the original
    witness provenance (``witnesses``); removing an owner removes
    ONLY its derivation — a complete surviving alternate keeps
    the target.  ``depth`` is the DERIVATION depth contributed by
    this edge (ordinary: depth(source)+1; group: 1 + MAX over ALL
    independently eligible possible suppliers) at the final
    relaxed fixed point — NOT the target's least complete depth
    (that is the node's).  The COMBINED count of ordinary edges
    and usable certificates is bounded by the ACTUAL inherited
    GraphBounds.max_edges.
    """

    source: str
    target: str
    kind: CurrentGraphEdgeKind
    owner: str
    witnesses: tuple[str, ...] = ()
    depth: int = Field(ge=0)

    @field_validator("source", "target")
    @classmethod
    def _v_path(cls, value: str, info: object) -> str:
        return _check_rel_path(value)

    @field_validator("owner")
    @classmethod
    def _v_owner(cls, value: str) -> str:
        return _check_owner(value, "owner")

    @field_validator("witnesses")
    @classmethod
    def _v_witnesses(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for witness in value:
            _check_hex64(witness, "witness occurrence")
        if tuple(sorted(set(value))) != value:
            raise _fixed("witnesses must be sorted and deduplicated")
        return value

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CurrentGraphEdge(source={PRIVATE_PATH_PLACEHOLDER}, "
            f"target={PRIVATE_PATH_PLACEHOLDER}, kind={self.kind.value!r}, "
            f"owner={self.owner!r}, witnesses={len(self.witnesses)}, depth={self.depth})"
        )

    __str__ = __repr__


class CurrentGraphCertificate(_GraphFrozen):
    """One GROUP-OWNED certificate or unresolved-origin record for
    one candidate of one current opaque group.

    ``candidate`` is the ACTUAL accepted reference evidence (the
    typed record with its spans/status/target-law reasons; the
    raw target never echoes operationally).  ``possible_origins``
    retain the COMPLETE member origin set (root members included
    for evidence); ``suppliers`` the non-root possible suppliers.
    ``usable`` certificates bind the resolved target, the
    derivation depth (1 + MAX supplier least depth) and the
    version-owned group identity; unusable ones retain their
    closed reasons and are NEVER an ordinary file edge.
    """

    group_identity: str
    group_digest: str
    members: tuple[str, ...]
    candidate: ReferenceCandidate
    possible_origins: tuple[str, ...]
    suppliers: tuple[str, ...]
    resolved_target: str | None = None
    depth: int | None = None
    usable: bool = False
    reasons: tuple[CurrentGraphReason, ...] = ()
    witnesses: tuple[str, ...] = ()

    @field_validator("group_identity", "group_digest")
    @classmethod
    def _v_hex(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "digest") or "digest")

    @field_validator("members", "possible_origins", "suppliers")
    @classmethod
    def _v_paths(cls, value: tuple[str, ...], info: object) -> tuple[str, ...]:
        name = getattr(info, "field_name", "paths") or "paths"
        for item in value:
            _check_rel_path(item)
        if name == "members":
            return value
        if tuple(sorted(set(value))) != value:
            raise _fixed(f"{name} must be sorted and deduplicated")
        return value

    @field_validator("resolved_target")
    @classmethod
    def _v_target(cls, value: str | None) -> str | None:
        return None if value is None else _check_rel_path(value)

    @field_validator("reasons")
    @classmethod
    def _v_reasons(cls, value: tuple[CurrentGraphReason, ...]) -> tuple[CurrentGraphReason, ...]:
        if tuple(sorted(set(value), key=lambda r: r.value)) != value:
            raise _fixed("reasons must be sorted and deduplicated")
        return value

    @field_validator("witnesses")
    @classmethod
    def _v_witnesses(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for witness in value:
            _check_hex64(witness, "witness occurrence")
        if tuple(sorted(set(value))) != value:
            raise _fixed("witnesses must be sorted and deduplicated")
        return value

    @model_validator(mode="after")
    def _v_certificate(self) -> CurrentGraphCertificate:
        if set(self.suppliers) - set(self.possible_origins):
            raise _fixed("suppliers are a subset of the possible origins")
        if any(origin == ROOT_FILENAME for origin in self.suppliers):
            raise _fixed("a root member is never a certificate supplier")
        if self.usable:
            if self.reasons or self.resolved_target is None or self.depth is None:
                raise _fixed("a usable certificate carries its target, depth, no reasons")
            if not self.suppliers:
                raise _fixed("a usable certificate retains its supplier set")
            return self
        if self.resolved_target is not None and not self.reasons:
            # A resolved target without usability still needs the
            # closed reasons that withhold it.
            raise _fixed("an unusable certificate with a resolved target carries reasons")
        if self.depth is not None:
            raise _fixed("an unusable certificate carries no derivation depth")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CurrentGraphCertificate(group_identity={self.group_identity!r}, "
            f"group_digest={self.group_digest!r}, members={len(self.members)}, "
            f"{_candidate_facts(self.candidate)}, "
            f"possible_origins={len(self.possible_origins)}, "
            f"suppliers={len(self.suppliers)}, "
            f"resolved_target="
            f"{PRIVATE_PATH_PLACEHOLDER if self.resolved_target is not None else 'None'}, "
            f"depth={self.depth}, usable={self.usable}, "
            f"reasons={[r.value for r in self.reasons]}, "
            f"witnesses={len(self.witnesses)})"
        )

    __str__ = __repr__


class CurrentGraphCandidate(_GraphFrozen):
    """One retained reference candidate of a selected current
    source (root/source/group) that did not become an edge or a
    path-target certificate (typed target-law limitation or
    non-path target).  The candidate record is the ACTUAL
    accepted evidence; ``owner`` names the supplying current
    source; group scans carry referring_path exact-None (the
    accepted boundaryless meaning)."""

    candidate: ReferenceCandidate
    owner: str

    @field_validator("owner")
    @classmethod
    def _v_owner(cls, value: str) -> str:
        return _check_owner(value, "owner")

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return f"CurrentGraphCandidate(owner={self.owner!r}, {_candidate_facts(self.candidate)})"

    __str__ = __repr__


def current_graph_scope_key(
    history_key: str,
    workspace: str,
    root_digest: str,
    contract_version: str,
    policy_version: str,
    graph_version: str,
    reference_version: str,
    proof_version: str,
    currentness_contract_version: str,
    currentness_policy_version: str,
    currentness_recipe_version: str,
    currentness_scope_key: str,
    bounds: CurrentGraphBounds,
    currentness_bounds: CurrentnessBounds,
    graph_bounds: GraphBounds,
) -> str:
    """The derived current graph's output scope identity.

    Binds the ACTUAL 018-d history scope, the workspace, the
    ACTUAL root digest, the record's ACTUAL current-graph
    contract/policy version fields, the inherited
    graph/reference/proof and currentness contract/policy/recipe
    versions, the validated 018-e scope key, the ACTUAL inherited
    graph bounds and EVERY new current-graph bound — so a caller
    tag alone cannot establish identity and a forged/stale key
    cannot hide different actual version fields.  Recomputed on
    every overlay construction; the key function binds the
    supplied validated facts (the derivation revalidates the
    actual fields first and emits only the supported constants).
    """
    payload = [
        contract_version,
        policy_version,
        graph_version,
        reference_version,
        proof_version,
        currentness_contract_version,
        currentness_policy_version,
        currentness_recipe_version,
        history_key,
        workspace,
        root_digest,
        currentness_scope_key,
        json.dumps(bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
        json.dumps(
            currentness_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        ),
        json.dumps(graph_bounds.model_dump(mode="json"), sort_keys=True, separators=(",", ":")),
    ]
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


class CurrentGraph(_GraphFrozen):
    """One derived current graph for the EXACT input history
    scope/revision it describes.

    The graph is a pure derivation output: it is not a fresh
    persistent revision or clock, it never mutates the input
    state, and it confers no compiler-semantic key on any
    unchanged source.  ``scope_key`` binds the actual history
    scope, the actual root facts, the inherited versions, the
    validated 018-e scope and every effective bound (recomputed
    on every construction; a caller tag alone cannot establish
    identity).  ``emitted_reasons`` is the TOTAL newly emitted
    closed-enum reason entries (node blocked reasons, certificate
    usability reasons, stage-level refusals) and never exceeds
    the hard diagnostic ceiling.
    """

    history_key: str
    revision: int = Field(ge=0, le=MAX_REVISION)
    workspace: str
    root_path: str = ROOT_FILENAME
    root_digest: str
    graph_version: str
    reference_version: str
    proof_version: str
    currentness_contract_version: str = CURRENTNESS_CONTRACT_VERSION
    currentness_policy_version: str = CURRENTNESS_POLICY_VERSION
    currentness_recipe_version: str = OPAQUE_GROUP_RECIPE_VERSION
    contract_version: str = CURRENT_GRAPH_CONTRACT_VERSION
    policy_version: str = CURRENT_GRAPH_POLICY_VERSION
    bounds: CurrentGraphBounds = Field(default_factory=CurrentGraphBounds)
    currentness_bounds: CurrentnessBounds = Field(default_factory=CurrentnessBounds)
    graph_bounds: GraphBounds = Field(default_factory=GraphBounds)
    currentness_scope_key: str
    scope_key: str
    suppliers: tuple[CurrentGraphSupplier, ...] = ()
    nodes: tuple[CurrentGraphNode, ...] = ()
    edges: tuple[CurrentGraphEdge, ...] = ()
    certificates: tuple[CurrentGraphCertificate, ...] = ()
    candidates: tuple[CurrentGraphCandidate, ...] = ()
    unreachable_current_paths: tuple[str, ...] = ()
    emitted_reasons: int = Field(ge=0, le=64)

    @field_validator("history_key", "root_digest", "currentness_scope_key", "scope_key")
    @classmethod
    def _v_hex(cls, value: str, info: object) -> str:
        return _check_hex64(value, getattr(info, "field_name", "key") or "key")

    @field_validator("workspace")
    @classmethod
    def _v_workspace(cls, value: str) -> str:
        return _check_text(value, "workspace", 1024)

    @field_validator(
        "graph_version",
        "reference_version",
        "proof_version",
        "currentness_contract_version",
        "currentness_policy_version",
        "currentness_recipe_version",
        "contract_version",
        "policy_version",
    )
    @classmethod
    def _v_version(cls, value: str, info: object) -> str:
        return _check_text(value, getattr(info, "field_name", "version") or "version", 128)

    @field_validator("root_path")
    @classmethod
    def _v_root_path(cls, value: str) -> str:
        return _check_rel_path(value)

    @field_validator("suppliers")
    @classmethod
    def _v_suppliers(
        cls, value: tuple[CurrentGraphSupplier, ...]
    ) -> tuple[CurrentGraphSupplier, ...]:
        owners = [supplier for supplier in value if supplier.kind is CurrentGraphSupplierKind.ROOT]
        if len(owners) > 1:
            raise _fixed("at most one root supplier (the anchor)")
        return value

    @field_validator("nodes")
    @classmethod
    def _v_nodes(cls, value: tuple[CurrentGraphNode, ...]) -> tuple[CurrentGraphNode, ...]:
        paths = tuple(node.path for node in value)
        if paths != tuple(sorted(set(paths))):
            raise _fixed("nodes must be sorted and deduplicated by path")
        return value

    @field_validator("edges")
    @classmethod
    def _v_edges(cls, value: tuple[CurrentGraphEdge, ...]) -> tuple[CurrentGraphEdge, ...]:
        keys = [(edge.source, edge.target, edge.kind.value, edge.owner) for edge in value]
        if keys != sorted(keys) or len(set(keys)) != len(keys):
            raise _fixed("edges must be sorted and deduplicated by (source, target, kind, owner)")
        return value

    @field_validator("certificates")
    @classmethod
    def _v_certificates(
        cls, value: tuple[CurrentGraphCertificate, ...]
    ) -> tuple[CurrentGraphCertificate, ...]:
        keys = [
            (
                certificate.group_identity,
                certificate.candidate.occurrence_index,
                certificate.candidate.target_char_span.start,
                certificate.candidate.target_char_span.end,
            )
            for certificate in value
        ]
        if keys != sorted(keys) or len(set(keys)) != len(keys):
            raise _fixed("certificates must be sorted and deduplicated per group candidate")
        return value

    @field_validator("candidates")
    @classmethod
    def _v_candidates(
        cls, value: tuple[CurrentGraphCandidate, ...]
    ) -> tuple[CurrentGraphCandidate, ...]:
        keys = [
            (
                entry.owner,
                entry.candidate.occurrence_index,
                entry.candidate.target_char_span.start,
                entry.candidate.target_char_span.end,
            )
            for entry in value
        ]
        if keys != sorted(keys) or len(set(keys)) != len(keys):
            raise _fixed("candidates must be sorted and deduplicated per source candidate")
        return value

    @field_validator("unreachable_current_paths")
    @classmethod
    def _v_unreachable(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for path in value:
            _check_rel_path(path)
        if tuple(sorted(set(value))) != value:
            raise _fixed("unreachable current paths must be sorted and deduplicated")
        return value

    @model_validator(mode="after")
    def _v_graph(self) -> CurrentGraph:
        if self.root_path != ROOT_FILENAME:
            raise _fixed("the root node is the evidenced root filename")
        root_nodes = [node for node in self.nodes if node.path == ROOT_FILENAME]
        if len(root_nodes) != 1:
            raise _fixed("the graph carries exactly one root node")
        if root_nodes[0].digest != self.root_digest:
            raise _fixed("the root node carries the exact anchor digest")
        node_paths = {node.path for node in self.nodes}
        for edge in self.edges:
            if edge.source not in node_paths or edge.target not in node_paths:
                raise _fixed("edge endpoints are graph nodes")
        combined = len(self.edges) + sum(1 for c in self.certificates if c.usable)
        if combined > self.graph_bounds.max_edges:
            raise _fixed("ordinary edges and usable certificates share the edge ceiling")
        if len(self.nodes) > self.graph_bounds.max_nodes:
            raise _fixed("nodes exceed the bound node ceiling")
        emitted = 0
        for node in self.nodes:
            if node.status in (
                CurrentGraphStatus.BLOCKED_CONFLICT,
                CurrentGraphStatus.BLOCKED_AMBIGUITY,
            ):
                emitted += 1
        for certificate in self.certificates:
            emitted += len(certificate.reasons)
        if emitted != self.emitted_reasons:
            raise _fixed("emitted reasons must equal the actual emitted total")
        if emitted > self.bounds.max_diagnostics:
            raise _fixed("emitted reasons exceed the hard diagnostic ceiling")
        expected = current_graph_scope_key(
            self.history_key,
            self.workspace,
            self.root_digest,
            self.contract_version,
            self.policy_version,
            self.graph_version,
            self.reference_version,
            self.proof_version,
            self.currentness_contract_version,
            self.currentness_policy_version,
            self.currentness_recipe_version,
            self.currentness_scope_key,
            self.bounds,
            self.currentness_bounds,
            self.graph_bounds,
        )
        if self.scope_key != expected:
            raise _fixed("scope key does not match the actual scope fields")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CurrentGraph(history_key={self.history_key!r}, revision={self.revision}, "
            f"workspace={PRIVATE_ID_PLACEHOLDER}, root_digest={self.root_digest!r}, "
            f"scope_key={self.scope_key!r}, suppliers={len(self.suppliers)}, "
            f"nodes={len(self.nodes)}, edges={len(self.edges)}, "
            f"certificates={len(self.certificates)}, candidates={len(self.candidates)}, "
            f"unreachable_current_paths={len(self.unreachable_current_paths)}, "
            f"emitted_reasons={self.emitted_reasons})"
        )

    __str__ = __repr__


class CurrentGraphResult(_GraphFrozen):
    """One bounded current-graph derivation result.

    ``state`` is ALWAYS the EXACT input state object (identity
    preserved on every outcome; the input is immutable and the
    derivation never mutates or re-orders it).  ``ok`` carries the
    derived graph and no diagnostics; every refusal carries no
    partial graph and its closed diagnostic reasons.
    """

    outcome: CurrentGraphOutcome
    state: CausalHistoryState
    overlay: CurrentGraph | None = None
    diagnostics: tuple[CurrentGraphLimitation, ...] = ()

    @field_validator("diagnostics")
    @classmethod
    def _v_diagnostics(
        cls, value: tuple[CurrentGraphLimitation, ...]
    ) -> tuple[CurrentGraphLimitation, ...]:
        if tuple(sorted(set(value), key=lambda r: r.value)) != value:
            raise _fixed("diagnostics must be sorted and deduplicated")
        return value

    @model_validator(mode="after")
    def _v_result(self) -> CurrentGraphResult:
        if self.outcome is CurrentGraphOutcome.OK:
            if self.overlay is None or self.diagnostics:
                raise _fixed("an ok result carries its overlay and no diagnostics")
            return self
        if self.overlay is not None or not self.diagnostics:
            raise _fixed("a refusal carries no partial overlay and its closed reasons")
        return self

    def __repr__(self) -> str:  # noqa: D105 - privacy law
        return (
            f"CurrentGraphResult(outcome={self.outcome.value!r}, "
            f"overlay={'yes' if self.overlay is not None else 'no'}, "
            f"diagnostics={list(self.diagnostics)})"
        )

    __str__ = __repr__
