"""The v1 governed request path (objective 022-c, slice 2).

Law (order section 2, first increments): the v1 governed route
request composes, in this fixed order,

1. the trusted session ADDRESS from the verified identity (the
   existing static or signed identity -- no caller assertions of
   scope / session / compiler bypass / trusted issuance), the
   governed route and the explicit route model contract joined to
   the configured compiler policy and the actual validated budget
   plan (the closed ``derive_compile_policy_fingerprint`` recipe:
   the configured policy fingerprint is the namespace's
   ``config_fingerprint``);
2. EXACTLY ONE owner for that address: the process-live owner is
   joined by the actual registered namespace record (steady state),
   the persisted record is resumed through the actual resume
   boundary (a distinct live epoch strictly above the record's
   prior epoch, the retained writer session for the owner's live
   lifetime), or a COLD owner is established from legitimate root
   evidence (the observed root's evidenced scope as the workspace
   -- never adapter filesystem access);
3. the ACTUAL P/D observation: the region lineage transition over
   THIS payload at the retained revision (the accepted D law runs
   inside the transition), then the SAME-run T admission;
3a. the marker-shaped source replay pre-check (before the
    transition's raw acquisition is committed): a marker-like
    candidate in the decoded payload triggers the pure pre-check
    over the retained protected generation (the ACTUAL compile and
    selection under the retained snapshot plus the pure unsplice
    seam): a stale / forged / malformed / unknown-kind / moved
    marker is the fixed typed refusal with NO raw acquisition
    committed, and every exactly-verified replay is unspliced to
    its retained original -- the transition observes the SHADOW
    (the originals), never marker bytes as source; ordinary
    non-source text stays data (the closed-location scan never
    reads it);
4. the RAM commit-CAS: the new ``(state, result)`` record set is
   admitted under the snapshot revision (an update computed from a
   retained snapshot binds that revision; the empty owner binds
   zero), and the PROTECTED GENERATION: the durable publication of
   the exact retained record set the edits rely on (a real
   successful publish under the bound-generation CAS); the
   narrow durable-generation handoff (``PreparedGenerationProof``)
   is prepared from the real publish result and the exact retained
   snapshot by immutable reference;
5. ordinary hits (the idempotent REPLAYED transition) advance no
   revision, commit nothing and publish nothing: they perform NO
   recovery original reads and reuse the retained successful
   publication of the current snapshot.
5a. the final-request budget gate (order 022-e section 2): the
    supported endpoint generation fields are honored as-is (a
    malformed or context-exceeding value is the fixed typed 422
    before any compile or main forward): Responses
    ``max_output_tokens``; Chat the ACTUAL effective field under
    the vLLM Chat protocol, a non-null ``max_completion_tokens``
    taking precedence over ``max_tokens`` (order 022-f section
    1); after the pure
    exact-span transaction and the endpoint-specific stable
    placement (whose prior rendered region is replacement-
    eligible ONLY under the verifying placement-ownership tag --
    literal delimiter-like caller text stays data, order 022-e
    section 1), the REAL final rendered governance (framing,
    guides and metadata) and the remaining text / tools /
    request structure / retained images are each counted ONCE
    with the real pinned tokenizer under the accepted
    ``BundleBudgetPlan`` envelope / capacity / aggregate law:
    the request-level overflow is the fixed typed 422 before
    the single main forward, and the governance overflow omits
    whole OPTIONAL entries deterministically (lowest priority
    first) with a coherent replacement/selection re-run -- no
    silent truncation, no dangling reference, no raw fallback.

Fixed failure/limitation contracts: every refused / negative
transition commits nothing and is refused with the closed typed
v1 request failure (no hidden raw fallback, no automatic replay,
no second owner); a rootless request has NO legitimate scope and
is simply not a governed request (forwarded unchanged by the
caller, with no v1 component touched beyond the observation).
The workspace of a resumed session is the VERIFIED resumed scope
(the loaded record's namespace), never re-observed prose.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import hmac
import json
import threading
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from ...image_policy import AmbiguousImageShape, count_images
from ...json_structure import JsonNestingTooDeep, enforce_json_nesting
from ..cache import RequestIdentity
from .bundle_admission_models import AdmissionMode, EntryClass, make_bundle_admission_namespace
from .bundle_budget import (
    BudgetMessage,
    BudgetToolCall,
    BudgetToolSpec,
    BundleBudgetError,
    BundleBudgetPlan,
)
from .bundle_compile_work import (
    BundleCompileWorkOutcome,
    derive_compile_policy_fingerprint,
)
from .bundle_compiler import unproven_member_paths
from .bundle_replace import (
    MAC_TAG_B64_LENGTH,
    MAC_TAG_BYTES,
    cold_payload_has_marker_sources,
    payload_has_marker_candidates,
    replace_sources,
    unsplice_replayed_markers,
)
from .bundle_replace_models import (
    PreparedGenerationProof,
    ReplacementOutcome,
)
from .bundle_selection import (
    BundleSelectionDecision,
    SelectionOutcome,
    SelectionReadyEntry,
    select_working_set,
)
from .causal_history_models import CAUSAL_ROOT_FACT
from .client_paths import validate_workspace
from .graph_models import CandidateStatus
from .graph_observation import GraphRequest
from .observation_models import ObservationReport, PathContext
from .ram_state import RamStateOwner
from .ram_state_models import RamStateOutcome
from .recovery_models import RecoverySessionAddress
from .recovery_resume import (
    RecoveryAdmitOutcome,
    RecoveryResumeOutcome,
    RecoverySessionOwner,
    RecoveryTeardownOutcome,
    resume_session,
)
from .recovery_store import (
    RecoveryPublishResult,
    RecoverySession,
    RecoveryStoreLimitation,
)
from .root_lineage_models import RootLineageOutcome
from .root_region_admission import derive_root_region_admission
from .root_region_admission_result_models import RootRegionAdmissionOutcome
from .root_region_lineage import (
    bootstrap_root_region_lineage,
    observe_root_region_lineage,
    register_root_region_issuance,
)
from .root_region_lineage_models import make_root_region_lineage_namespace
from .v1_runtime import V1Runtime

if TYPE_CHECKING:
    from ...config import ContextCacheRouteContract, RouteConfig

#: The workspace path bound of the closed graph bounds (the actual
#: configured ``max_path_bytes``; the observed scope label is
#: validated against it before any namespace construction).
_V1_WORKSPACE_MAX_BYTES = 4096


class V1RequestReason(StrEnum):
    """The closed v1 request failure vocabulary (fixed, typed,
    no content / path / identity echo)."""

    SESSION_CONFLICT = "session_conflict"
    RESUME_REFUSED = "resume_refused"
    COLD_NO_SCOPE = "cold_no_scope"
    BOOTSTRAP_REFUSED = "bootstrap_refused"
    COLD_ADMIT_REFUSED = "cold_admit_refused"
    COLD_PUBLISH_REFUSED = "cold_publish_refused"
    TRANSITION_REFUSED = "transition_refused"
    ADMISSION_REFUSED = "admission_refused"
    COMMIT_REFUSED = "commit_refused"
    PUBLISH_REFUSED = "publish_refused"
    WORKSPACE_INVALID = "workspace_invalid"
    COMPILER_REFUSED = "compiler_refused"
    POLICY_STALE = "policy_stale"
    SELECTION_REFUSED = "selection_refused"
    GENERATION_NOT_DURABLE = "generation_not_durable"
    TRANSACTION_CONFLICT = "transaction_conflict"
    TRANSACTION_OVER_BOUND = "transaction_over_bound"


#: The fixed status / code per reason (fail closed: a refused
#: governed transaction is never a raw forward; the closed codes
#: carry no private values).
V1_REQUEST_FAILURES: Mapping[V1RequestReason, tuple[int, str]] = {
    V1RequestReason.SESSION_CONFLICT: (503, "v1_session_conflict"),
    V1RequestReason.RESUME_REFUSED: (503, "v1_resume_refused"),
    V1RequestReason.COLD_NO_SCOPE: (503, "v1_cold_no_scope"),
    V1RequestReason.BOOTSTRAP_REFUSED: (503, "v1_bootstrap_refused"),
    V1RequestReason.COLD_ADMIT_REFUSED: (503, "v1_cold_admit_refused"),
    V1RequestReason.COLD_PUBLISH_REFUSED: (503, "v1_cold_publish_refused"),
    V1RequestReason.TRANSITION_REFUSED: (503, "v1_transition_refused"),
    V1RequestReason.ADMISSION_REFUSED: (503, "v1_admission_refused"),
    V1RequestReason.COMMIT_REFUSED: (503, "v1_commit_refused"),
    V1RequestReason.PUBLISH_REFUSED: (503, "v1_publish_refused"),
    V1RequestReason.WORKSPACE_INVALID: (503, "v1_workspace_invalid"),
    V1RequestReason.COMPILER_REFUSED: (503, "v1_compiler_refused"),
    V1RequestReason.POLICY_STALE: (409, "v1_policy_stale"),
    V1RequestReason.SELECTION_REFUSED: (422, "v1_selection_refused"),
    V1RequestReason.GENERATION_NOT_DURABLE: (503, "v1_generation_not_durable"),
    V1RequestReason.TRANSACTION_CONFLICT: (409, "v1_transaction_conflict"),
    V1RequestReason.TRANSACTION_OVER_BOUND: (422, "v1_transaction_over_bound"),
}


@dataclass(frozen=True, slots=True)
class V1RequestRefusal:
    """One fixed typed v1 request failure (never a raw fallback)."""

    reason: V1RequestReason

    @property
    def status_code(self) -> int:
        return V1_REQUEST_FAILURES[self.reason][0]

    @property
    def code(self) -> str:
        return V1_REQUEST_FAILURES[self.reason][1]


@dataclass(slots=True)
class V1Session:
    """The process-local state of ONE live v1 session.

    ``session_owner`` is the 020 owned fenced checkpoint owner of
    this session's recovery writer (the owner's live lifetime;
    COLD and RESUMED owners alike publish through the accepted
    owned/fenced path -- the exact live-owner join, the owned
    store-IO slot, the bounded transient reservation, the
    credential quarantine law and the bound-generation CAS; no
    raw writer shortcut); ``bare_session`` is the COLD-opened
    writer session (the writer handle itself, held by the
    session owner); ``last_publish`` is the ACTUAL successful
    publication of the owner's retained record set (the
    durable-generation handoff source for ordinary hits), bound
    by ``last_publish_bound`` to the exact (snapshot revision,
    epoch) it ACTUALLY published: a retained publish whose bound
    does not match the current snapshot is an undurable snapshot
    (refused on replay, never forwarded under a stale proof)."""

    namespace: Any  # RootRegionLineageNamespace (the registered record)
    owner: RamStateOwner
    session_owner: RecoverySessionOwner | None = None
    bare_session: RecoverySession | None = None
    last_publish: RecoveryPublishResult | None = None
    #: The exact (snapshot revision, epoch) of the record set
    #: ``last_publish`` actually published (None while no
    #: successful publish is retained).
    last_publish_bound: tuple[int, int] | None = None

    def checkpoint(self) -> RecoveryPublishResult:
        """The protected generation: publish the owner's CURRENT
        retained record set under the bound-generation CAS
        through the accepted 020 owned/fenced checkpoint (the
        cold and resumed owners share the one path; the fenced
        law covers teardown, the owned IO slot, the bounded
        transient reservation and the credential quarantine)."""
        assert self.session_owner is not None
        return self.session_owner.checkpoint_current()


class V1SessionTable:
    """The process-owned live-session table (one worker, one
    process; the single-worker law is enforced by the settings
    closure).  Keyed by the trusted address lineage key; the
    entries are the ACTUAL registered namespace records (the
    registry identity join requires the exact record)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, V1Session] = {}

    def get(self, address: RecoverySessionAddress) -> V1Session | None:
        with self._lock:
            return self._sessions.get(address.lineage_key)

    def put(self, address: RecoverySessionAddress, session: V1Session) -> None:
        with self._lock:
            self._sessions[address.lineage_key] = session

    def discard(self, address: RecoverySessionAddress) -> None:
        with self._lock:
            self._sessions.pop(address.lineage_key, None)

    def sessions(self) -> tuple[V1Session, ...]:
        """The current live sessions (process teardown only)."""
        with self._lock:
            return tuple(self._sessions.values())

    def clear(self) -> None:
        """Drop every live entry (process teardown only)."""
        with self._lock:
            self._sessions.clear()


def build_session_address(
    runtime: V1Runtime,
    identity: RequestIdentity,
    route: RouteConfig,
    contract: ContextCacheRouteContract,
) -> RecoverySessionAddress:
    """The trusted resume lookup ADDRESS (no root / source /
    surviving virtual reference required to locate the session):
    the verified identity's principal / session / repository plus
    the governed route and the configured model / policy context.
    The model identity binds the declared model to the pinned
    tokenizer capability; the config fingerprint is the ACTUAL
    closed policy join (the compile-work fence recipe) so a
    changed compiler / tokenizer / budget policy is a genuinely
    distinct session, never a cross-namespace reuse."""
    model_identity = f"{contract.model}@{contract.tokenizer_revision}"
    config_fingerprint = derive_compile_policy_fingerprint(
        config_identity=runtime.compiler.config.config_identity,
        plan_identity=runtime.budget_plan.plan_identity(),
    )
    return RecoverySessionAddress(
        principal=identity.principal,
        session=identity.session,
        repository=identity.repository,
        route=route.name,
        model_identity=model_identity,
        config_fingerprint=config_fingerprint,
    )


def build_v1_namespace(
    runtime: V1Runtime,
    identity: RequestIdentity,
    route: RouteConfig,
    contract: ContextCacheRouteContract,
    address: RecoverySessionAddress,
    workspace: str,
) -> Any:
    """The COMPLETE trusted namespace for a COLD session (the
    resume validates its namespace from the loaded record; the
    six address fields are the closed join).  The workspace is
    the legitimate observed scope (the evidenced root label),
    already canonicalized and bound-checked by the caller."""
    model_identity = f"{contract.model}@{contract.tokenizer_revision}"
    admission = make_bundle_admission_namespace(
        identity,
        model_identity=model_identity,
        config_fingerprint=address.config_fingerprint,
        workspace=workspace,
        mode=AdmissionMode(runtime.admission_mode),
    )
    return make_root_region_lineage_namespace(admission, f"slaif-v1-{address.lineage_key}")


def _evidenced_workspace(observation: Any) -> str | None:
    """The legitimate observed scope: the ONE valid authoritative
    root occurrence's evidenced scope label (canonical absolute
    POSIX, bound-checked).  No valid root yields NO scope (never
    an adapter-host path, never prose)."""
    root = next(
        (
            occurrence
            for occurrence in observation.roots.occurrences
            if occurrence.kind.value == "root"
            and occurrence.status.value == "ok"
            and occurrence.scope_label
        ),
        None,
    )
    if root is None:
        return None
    workspace = validate_workspace(root.scope_label, _V1_WORKSPACE_MAX_BYTES)
    return workspace


def _cold_scope_refusal(reason: V1RequestReason) -> V1RequestRefusal:
    return V1RequestRefusal(reason)


async def _teardown_v1_session(
    table: V1SessionTable,
    address: RecoverySessionAddress,
    session: V1Session,
) -> None:
    """The explicit teardown exit of ONE live v1 session (the
    durable-quarantine exit, the COLD prepublication-failure
    cleanup and the process teardown share the accepted 020
    composed path: the owned IO drains, the work plane and the
    RAM ownership release in the accepted order, and the
    exclusive writer session closes only after the store owner
    is gone).  The table entry is dropped only on the COMPLETED
    teardown (a refused teardown keeps the session held -- no
    partial release); a quarantined owner keeps its committed
    fence record, so a later restart of this session fails
    closed on it."""
    if session.session_owner is not None:
        result = await session.session_owner.teardown()
        if result.outcome is RecoveryTeardownOutcome.TEARDOWN:
            table.discard(address)
        return
    store = session.owner.teardown(session.namespace)
    if store.outcome is RamStateOutcome.TEARDOWN:
        table.discard(address)


async def establish_v1_session(
    runtime: V1Runtime,
    table: V1SessionTable,
    *,
    address: RecoverySessionAddress,
    identity: RequestIdentity,
    route: RouteConfig,
    contract: ContextCacheRouteContract,
    observation: Any,
    payload: dict[str, Any],
    endpoint: str,
) -> V1Session | V1RequestRefusal | None:
    """Join / resume / cold-establish EXACTLY ONE owner for the
    trusted address.  Returns the live session, the fixed typed
    refusal, or ``None`` when the request carries NO legitimate
    scope (not a governed request: the caller forwards the
    payload unchanged with no v1 component touched)."""
    existing = table.get(address)
    if existing is not None:
        # Steady state: the process-live owner by the ACTUAL
        # registered namespace record (the identity join).
        if runtime.ram_registry.get(existing.namespace) is existing.owner:
            if existing.owner.quarantined:
                # The durable-quarantine law (019-c/020): a
                # quarantined owner can no longer certify
                # currentness from the older retained state; the
                # request is the fixed typed currentness refusal
                # with no main forward, and the explicit teardown
                # is the exit (no retry, no epoch reset, no
                # revival; a restart of this session fails closed
                # on the committed fence).
                await _teardown_v1_session(table, address, existing)
                return _cold_scope_refusal(V1RequestReason.TRANSACTION_CONFLICT)
            return existing
        # A fenced / torn-down owner is replaced ONLY by an
        # explicit re-establishment (the table entry is stale).
        table.discard(address)
    resume = resume_session(runtime.ram_registry, runtime.recovery_store, address)
    if resume.outcome is RecoveryResumeOutcome.RESUMED:
        assert resume.owner is not None and resume.recovery is not None
        session = V1Session(
            namespace=resume.owner.namespace,
            owner=resume.owner,
            session_owner=resume.recovery,
        )
        table.put(address, session)
        return session
    if resume.outcome is RecoveryResumeOutcome.OWNER_ALREADY_LIVE:
        return _cold_scope_refusal(V1RequestReason.SESSION_CONFLICT)
    if resume.outcome is RecoveryResumeOutcome.STORE_REFUSED:
        if (
            isinstance(resume.limitation, RecoveryStoreLimitation)
            and resume.limitation is RecoveryStoreLimitation.MISSING
        ):
            pass  # COLD: no persisted record for this address
        else:
            return _cold_scope_refusal(V1RequestReason.RESUME_REFUSED)
    else:
        return _cold_scope_refusal(V1RequestReason.RESUME_REFUSED)
    # ---- COLD start: legitimate root evidence only -----------
    workspace = _evidenced_workspace(observation)
    if workspace is None:
        return None
    # The closed COLD marker/source-carrier law (order 022-d
    # section 1): a fresh address cannot authenticate a retained
    # source marker, so a marker-like candidate in the ACTUAL
    # cold-recognized root / result source span is the fixed
    # typed marker-side refusal BEFORE any raw acquisition, owner
    # allocation or checkpoint (ordinary non-source text stays
    # data).
    if cold_payload_has_marker_sources(payload, observation, max_text_chars=_V1_MAX_TEXT_CHARS):
        return _cold_scope_refusal(V1RequestReason.TRANSACTION_CONFLICT)
    namespace = build_v1_namespace(runtime, identity, route, contract, address, workspace)
    owner = runtime.ram_registry.acquire(namespace)
    context = PathContext(workspace=workspace)
    transition = bootstrap_root_region_lineage(
        (GraphRequest(payload=payload, endpoint=endpoint, context=context),), namespace
    )
    if transition.outcome is not RootLineageOutcome.ACCEPTED:
        # Safe cleanup of the ACQUIRED cold owner (no writer yet,
        # nothing admitted): the fenced epoch frees the
        # registration so a later request re-establishes cleanly.
        owner.teardown(namespace)
        return _cold_scope_refusal(V1RequestReason.BOOTSTRAP_REFUSED)
    admission = derive_root_region_admission(transition.state, namespace)
    try:
        bare = runtime.recovery_store.open_session(address)
    except Exception:
        owner.teardown(namespace)
        return _cold_scope_refusal(V1RequestReason.COLD_PUBLISH_REFUSED)
    session = V1Session(namespace=namespace, owner=owner)
    session.bare_session = bare
    # The COLD owner joins the SAME accepted 020 owned/fenced
    # checkpoint path as the resumed owner (the live-owner join,
    # the owned store-IO slot, the bounded transient reservation,
    # the quarantine law and the bound-generation CAS): the fresh
    # cold writer has no prior durable record, so its bound
    # generation starts at zero and the first protected
    # generation publishes under the empty-store CAS.
    session.session_owner = RecoverySessionOwner(
        registry=runtime.ram_registry,
        session=bare,
        owner=owner,
        address=address,
        bound_generation=0,
        prior_epoch=0,
        new_epoch=owner.epoch,
    )
    # The COLD transition enters through the SAME accepted 020
    # owned/fenced admit kernel as every later transition (the
    # adverse durable fence law, the owned store-IO slot, the
    # bounded transient reservation and the bound-generation
    # CAS; no raw admit followed by a separate checkpoint).
    fenced = session.session_owner.admit_with_fence(
        transition.state, admission, expected_revision=owner.revision
    )
    if fenced.outcome is not RecoveryAdmitOutcome.ADMITTED:
        # Safe cleanup of the acquired COLD owner/writer on the
        # prepublication failure (the composed teardown keeps a
        # published fence durable: a restart of this session
        # fails closed on it).
        await _teardown_v1_session(table, address, session)
        return _cold_scope_refusal(V1RequestReason.COLD_ADMIT_REFUSED)
    advance = fenced.advance
    if advance is None or advance.limitation is not RecoveryStoreLimitation.OK:
        # The RAM state admitted but the protected generation did
        # not publish: the cold owner/writer is torn down on the
        # prepublication failure (no live owner with an undurable
        # record set; a later request re-establishes).
        await _teardown_v1_session(table, address, session)
        return _cold_scope_refusal(V1RequestReason.COLD_PUBLISH_REFUSED)
    session.last_publish = advance
    snapshot = owner.snapshot
    if snapshot is None:
        await _teardown_v1_session(table, address, session)
        return _cold_scope_refusal(V1RequestReason.COLD_PUBLISH_REFUSED)
    session.last_publish_bound = (snapshot.revision, snapshot.epoch)
    table.put(address, session)
    return session


def advance_v1_session(
    session: V1Session,
    runtime: V1Runtime,
    *,
    payload: dict[str, Any],
    endpoint: str,
    observation: Any,
) -> tuple[PreparedGenerationProof | None, V1RequestRefusal | None]:
    """Advance the retained state over THIS payload (the actual
    P/D region transition at the retained revision, the same-run
    T admission, the RAM commit-CAS and the protected generation)
    and prepare the narrow durable-generation handoff for the
    exact snapshot the edits rely on.

    An idempotent REPLAYED transition commits nothing and
    publishes nothing (the ordinary hit: no recovery original
    reads, the retained publication of the current snapshot)."""
    owner = session.owner
    namespace = session.namespace
    snapshot = owner.snapshot
    if snapshot is None:
        # Unreachable for an established session (bootstrap
        # commits the first record set); fail closed.
        return None, V1RequestRefusal(V1RequestReason.COMMIT_REFUSED)
    context = PathContext(workspace=namespace.workspace)
    transition = observe_root_region_lineage(
        snapshot.state,
        namespace,
        expected_revision=snapshot.state.revision,
        requests=(GraphRequest(payload=payload, endpoint=endpoint, context=context),),
    )
    if transition.outcome is RootLineageOutcome.REPLAYED:
        # Ordinary hit: no commit, no new publication, no recovery
        # original reads; the retained publication of the current
        # snapshot is the durable-generation handoff (a resumed
        # session materializes its restored record set's generation
        # here on its first hit).
        publish = _ensure_retained_publish(session)
        if isinstance(publish, V1RequestRefusal):
            return None, publish
        return PreparedGenerationProof(publish=publish, snapshot=snapshot), None
    if transition.outcome is not RootLineageOutcome.ACCEPTED:
        return None, V1RequestRefusal(V1RequestReason.TRANSITION_REFUSED)
    admission = derive_root_region_admission(transition.state, namespace)
    session_owner = session.session_owner
    # Established sessions (cold establish / resume) always hold
    # the 020 owned fenced checkpoint owner.
    assert session_owner is not None
    # A genuine non-READY T is admissible state (the negative
    # P/Q evidence is retained in the committed record set) but
    # cannot carry a governed transaction: the record set is
    # committed and published through the SAME fenced advance,
    # and the transaction stage refuses with the closed typed
    # currentness / admission family (zero main forward, no
    # bootstrap fallback).
    fenced = session_owner.admit_with_fence(
        transition.state, admission, expected_revision=owner.revision
    )
    if fenced.outcome is not RecoveryAdmitOutcome.ADMITTED:
        # A refused / fence-blocked transition commits nothing
        # (the durable fence could not be published so NO
        # transition was permitted, or the accepted admit law
        # refused the candidate with no quarantine): the prior
        # committed generation stays valid and the request is the
        # fixed typed refusal (a quarantined owner exits at the
        # next request through the steady-state guard).
        return None, V1RequestRefusal(V1RequestReason.TRANSITION_REFUSED)
    advance = fenced.advance
    if advance is None or advance.limitation is not RecoveryStoreLimitation.OK:
        # The RAM state admitted but the protected generation did
        # not publish: the prior bound is RETAINED (the failed
        # publication keeps it) and the newer undurable record
        # set is refused on replay, never forwarded under a stale
        # proof.
        return None, V1RequestRefusal(V1RequestReason.PUBLISH_REFUSED)
    session.last_publish = advance
    new_snapshot = owner.snapshot
    if new_snapshot is None:
        return None, V1RequestRefusal(V1RequestReason.COMMIT_REFUSED)
    # The retained successful pointer is bound to the exact
    # snapshot/epoch it actually published (the newer record set
    # is undurable until the bound moves over it).
    session.last_publish_bound = (new_snapshot.revision, new_snapshot.epoch)
    return PreparedGenerationProof(publish=advance, snapshot=new_snapshot), None


#: The accepted observation carrier bound (the 022-b transaction
#: default; the transaction runs over THIS payload's geometry).
_V1_MAX_TEXT_CHARS = 100_000

#: The stable compiled-context region sentinels (order 022-d
#: section 3): the ACTUAL selected compiled blocks accompany
#: every transformed outgoing body at the endpoint-specific
#: stable placement (top-level Responses ``instructions``; the
#: Chat stable system location) -- an opaque marker alone is
#: never the model's governing content.  The region is ordinary
#: request text: it is never a source carrier, it carries none
#: of the two closed marker kinds, and the re-injection is
#: deterministic and idempotent across resent transformed
#: payloads (the byte-identical fixed point is preserved).
#: The region is the DETERMINISTIC frame (order 022-g section 2):
#: the opening delimiter directly carries a fixed-width claim --
#: the zero-padded body CHARACTER length and the closed canonical
#: opaque under the distinct claim purpose of the placement
#: domain -- so one closing position is located from the length
#: and the exact body is verified by the existing
#: placement-ownership tag (no source digest on the wire).
_COMPILED_OPEN = "[slaif-compiled-context:v1:"
_COMPILED_CLAIM_LEN_DIGITS = 8
#: The closed character set of the claim's zero-padded length
#: field (ASCII digits only; the claim shape is a fixed-width
#: wire form, never an arbitrary integer encoding).
_PO_CLAIM_LEN_CHARS = frozenset("0123456789")
_COMPILED_FOOTER = "[/slaif-compiled-context:v1]"


#: The placement-ownership tag domain (order 022-e section 1):
#: the SAME private per-session key material as the two closed
#: source marker kinds, under a SEPARATE MAC domain, bound to
#: the complete trusted namespace, the endpoint-specific stable
#: placement and the exact rendered region payload (header +
#: blocks + footer, without the tag).  A prior rendered region
#: is eligible for replacement ONLY under a tag that verifies
#: for THIS trusted session and placement (positive application
#: ownership); literal delimiter-like caller text carries no
#: verifying tag and stays ordinary data (never replaced,
#: never lost).  The wire form is content-free (versioned kind
#: + fixed-length canonical base64url MAC) and is invisible to
#: the source-marker pre-check (its kind is distinct from the
#: two closed marker kinds).
_PO_TAG_PREFIX = "[slaif-placement-ownership:v1:"
_PO_DOMAIN = "slaif-placement-ownership/v1"
_PO_CLAIM_DOMAIN = "slaif-placement-ownership/v1:claim"
_PLACEMENT_RESPONSES = "responses:instructions"
_PLACEMENT_CHAT = "chat:system"
_PO_B64_ALPHABET = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")


def _po_placement(endpoint: str) -> str:
    """The closed endpoint-specific stable placement identity."""
    if endpoint == "responses":
        return _PLACEMENT_RESPONSES
    if endpoint == "chat":
        return _PLACEMENT_CHAT
    raise _CompiledInjectionShapeError("endpoint shape")


def _po_field_bytes(*fields: str) -> bytes:
    """The closed MAC-input encoding (the same length-prefixed
    UTF-8 field recipe as the approved private marker material;
    the fields stay INSIDE the HMAC input and are never emitted
    on the wire)."""
    out = bytearray()
    for value in fields:
        raw = value.encode("utf-8")
        out += len(raw).to_bytes(4, "big") + raw
    return bytes(out)


def _po_tag_from_digest(
    key: bytes, namespace_key: str, placement: str, region_payload_digest: str
) -> str:
    """The placement-ownership wire form from a PRE-COMPUTED
    region-payload digest: versioned kind tag + fixed-length
    canonical base64url HMAC over (domain, complete trusted
    namespace, placement, digest).  No private field bytes on
    the wire."""
    mac = hmac.new(
        key,
        _po_field_bytes(_PO_DOMAIN, namespace_key, placement, region_payload_digest),
        hashlib.sha256,
    ).digest()
    opaque = base64.urlsafe_b64encode(mac).decode("ascii").rstrip("=")
    if len(opaque) != MAC_TAG_B64_LENGTH:
        raise AssertionError("the placement-ownership tag is not the fixed length")
    return f"{_PO_TAG_PREFIX}{opaque}]"


def _po_tag(key: bytes, namespace_key: str, placement: str, region_payload: str) -> str:
    """The placement-ownership wire form under the separate MAC
    domain: versioned kind tag + fixed-length canonical
    base64url HMAC over (domain, complete trusted namespace,
    placement, rendered region payload digest).  No private
    field bytes on the wire."""
    digest = hashlib.sha256(region_payload.encode("utf-8")).hexdigest()
    return _po_tag_from_digest(key, namespace_key, placement, digest)


def _po_claim_opaque(key: bytes, namespace_key: str, placement: str, body_len: int) -> str:
    """The deterministic frame's fixed-width claim opaque
    (order 022-g section 2): the closed canonical base64url
    HMAC under the DISTINCT claim purpose of the placement
    domain, bound to (claim domain, complete trusted
    namespace, placement, the zero-padded 8-digit body
    CHARACTER length).  The claim authenticates IN PLACE,
    before any body walk, so the one closing position is
    located from the authenticated length and the exact body
    is verified by the existing placement-ownership tag: the
    SAME protected per-session key material, no source digest
    on the wire."""
    mac = hmac.new(
        key,
        _po_field_bytes(_PO_CLAIM_DOMAIN, namespace_key, placement, f"{body_len:08d}"),
        hashlib.sha256,
    ).digest()
    opaque = base64.urlsafe_b64encode(mac).decode("ascii").rstrip("=")
    if len(opaque) != MAC_TAG_B64_LENGTH:
        raise AssertionError("the placement-ownership claim is not the fixed length")
    return opaque


def _po_tag_valid(opaque: str) -> bool:
    """The closed canonical wire-form check (the same law as the
    source-marker tags: exact length, closed alphabet, zero
    final padding bits, 32-byte MAC)."""
    if len(opaque) != MAC_TAG_B64_LENGTH or any(c not in _PO_B64_ALPHABET for c in opaque):
        return False
    try:
        mac = base64.urlsafe_b64decode(opaque + "=")
    except Exception:
        return False
    if len(mac) != MAC_TAG_BYTES:
        return False
    return base64.urlsafe_b64encode(mac).decode("ascii").rstrip("=") == opaque


class _CompiledInjectionShapeError(Exception):
    """The closed placement-shape failure (the target field of
    the stable placement is present but not the accepted string
    shape): the governed transaction is refused with the typed
    422 invalid-transform family -- never a raw forward, never a
    guessed placement."""


def _compiled_region(
    blocks: tuple[str, ...], *, placement: str, namespace_key: str, key: bytes
) -> str:
    """The ONE stable region of the ACTUAL selected compiled
    blocks in actual injection order (the rendered blocks
    already carry their explicit scopes / authority /
    references; the sentinels delimit the region for the
    deterministic re-injection) plus the closed
    placement-ownership tag on its own line between the content
    and the footer: bound to THIS trusted namespace, THIS
    placement and THIS exact rendered payload, a byte-identical
    working set renders a byte-identical region, so the
    legitimate transformed replay stays the byte-identical
    fixed point (order 022-e section 1).

    The wire form is the DETERMINISTIC frame (order 022-g
    section 2): the opening delimiter directly carries the
    fixed-width claim (the zero-padded body CHARACTER length
    and the closed canonical opaque under the distinct claim
    purpose of the placement domain), then the body, then the
    placement-ownership tag line (the MAC over the exact
    rendered payload: open line + body + footer) and the
    footer.  No source digest is on the wire; the closed
    8-digit claim length bound is the fixed-width claim shape
    (the typed invalid-transform refusal on a crossing,
    unreachable under the accepted budgets)."""
    body = "\n\n".join(blocks)
    if len(body) > 99_999_999:
        raise _CompiledInjectionShapeError("region length")
    open_line = (
        _COMPILED_OPEN
        + f"{len(body):08d}:"
        + _po_claim_opaque(key, namespace_key, placement, len(body))
    )
    region_payload = f"{open_line}\n{body}\n{_COMPILED_FOOTER}"
    tag = _po_tag(key, namespace_key, placement, region_payload)
    return f"{open_line}\n{body}\n{tag}\n{_COMPILED_FOOTER}"


#: The fixed character skeleton of the deterministic frame
#: around the body (the fixed-width open line, the two frame
#: newlines and the footer): the rendered payload of a frame is
#: exactly ``body_chars + _COMPILED_FRAME_SKELETON_CHARS``
#: characters, so the conservative UTF-8 work bound of one
#: frame follows from the authenticated body length alone.
_COMPILED_FRAME_SKELETON_CHARS = (
    len(_COMPILED_OPEN)
    + _COMPILED_CLAIM_LEN_DIGITS
    + 1
    + MAC_TAG_B64_LENGTH
    + 2
    + len(_COMPILED_FOOTER)
)


def _placement_work_cap(render_bytes: int) -> int:
    """The closed total verification work cap (UTF-8 bytes) of
    ONE ownership scan, DERIVED FROM THE ACTUAL CONFIGURED
    COMPILED-RENDER BUDGET (order 022-g section 2): the emitted
    region body is STRICTLY SMALLER than ``render_bytes``
    UTF-8 bytes (``count_compiled_block`` checks the WHOLE
    framed region against the configured compiled-block byte
    limit, so the body plus the fixed framing fits that
    ceiling), the scan's payload view is body + the fixed
    framing skeleton, and each character encodes to at most 4
    UTF-8 bytes -- so the cap is the conservative work bound
    of ONE legitimately emitted frame.  An otherwise-valid
    single emitted frame verifies under the cap by
    construction (never refused by an older carrier-observation
    constant), and a field whose admitted bodies carry more
    than one legitimate frame's worth of verification work is
    the fixed typed over-bound transform refusal (never
    treated as having no owned span, never forwarded raw)."""
    return 4 * (render_bytes + _COMPILED_FRAME_SKELETON_CHARS)


class _PlacementOwnershipWorkExhausted(Exception):
    """The closed placement-ownership verification work cap of
    one scan (derived from the configured compiled-render
    budget: the conservative work bound of ONE legitimately
    emitted frame) is crossed: the placement field's admitted
    candidate bodies (the deterministic frames whose fixed-
    width claim authenticated in place) carry more than one
    legitimate frame's worth of verification work.  The
    governed transaction is the fixed typed over-bound
    transform refusal -- the distinct typed transform refusal
    of order 022-g section 2, never a silent no-ownership
    prepend and never a raw forward."""


def _owned_region_span(
    text: str, *, placement: str, namespace_key: str, key: bytes, work_cap: int
) -> tuple[int, int] | None:
    """The half-open span [start, end) of the FIRST rendered
    region whose deterministic frame verifies for THIS
    placement, THIS complete trusted namespace and THIS exact
    rendered payload (the positive application ownership of
    order 022-e section 1, completed by order 022-f section 2
    and bounded by order 022-g section 2):

    * Discovery is ONE bounded left-to-right pass with a
      monotonic non-overlapping cursor (the opening delimiter
      carries a single bracket, so one occurrence cannot start
      inside another).  A frame truncated at the end of the
      input (claim, body, tag line or footer) is rejected
      BEFORE any boundary byte is indexed and stays caller
      data.
    * At each opening delimiter the fixed-width claim (the
      zero-padded body CHARACTER length, the colon and the
      closed canonical opaque, directly after the delimiter) is
      parsed and authenticated IN PLACE -- O(1) work, no body
      access: the claim MAC under the distinct claim purpose of
      the placement domain.  A failed claim (length, shape or
      authentication under another trusted namespace or
      placement) is caller data and the cursor continues.
    * The ONE closing position is then located from the
      authenticated length: the body is exactly the text
      between the open line's newline and the newline at the
      claimed end, the following line must be the shape-valid
      fixed-length tag line and the line after it the exact
      footer, and EVERY wire separator of the frame (after the
      open line, after the body and after the tag line) is
      verified to be the actual newline of the input -- the
      digest is computed over the ACTUAL wire bytes of the
      frame (open line, body, footer), never over a
      reconstruction with inserted separators.  The exact body
      is verified by the EXISTING placement-ownership tag (the
      MAC over the complete rendered region payload).  Literal
      delimiters anywhere in the rendered content are data and
      cannot bound, split or duplicate the owned span.
    * The total verification of ADMISSION candidate bodies
      (each admitted candidate charged AFTER the fixed-size
      claim and closing-shape validation and BEFORE any body
      copy, at the conservative UTF-8 byte bound of its
      rendered payload computed from the authenticated claim)
      is bounded by the closed cap ``work_cap`` (derived from
      the configured compiled-render budget: the work bound of
      ONE legitimately emitted frame); crossing it raises
      ``_PlacementOwnershipWorkExhausted`` (the distinct typed
      over-bound transform refusal -- never a silent
      no-ownership prepend, never a raw forward).  An ordinary
      caller field without an authenticating frame costs only
      the O(1) in-place claim checks, so any bounded caller
      field with any literal delimiter density passes the
      scan.
    * A valid frame may follow ordinary caller text: the scan
      starts at 0, and an unauthenticated opening delimiter
      inside caller data is just caller data.
    * ``end`` is EXACTLY the footer end: the entire suffix after
      the footer (separator newlines and caller text alike) is
      preserved byte-identical, so a legitimate transformed
      replay stays the byte-identical fixed point whether or
      not the caller had its own instructions/system content.

    ``None`` when no frame verifies (a second session's frame
    fails under this session's own namespace-scoped MAC, and a
    caller's literal delimiters carry no authenticating claim
    at all or never authenticate)."""
    n = len(text)
    open_len = len(_COMPILED_OPEN)
    footer_len = len(_COMPILED_FOOTER)
    claim_len = _COMPILED_CLAIM_LEN_DIGITS + 1 + MAC_TAG_B64_LENGTH
    tag_line_len = len(_PO_TAG_PREFIX) + MAC_TAG_B64_LENGTH + 1
    search = 0
    work = 0
    while True:
        p = text.find(_COMPILED_OPEN, search)
        if p == -1:
            break
        search = p + open_len
        claim_start = p + open_len
        claim_end = claim_start + claim_len
        if claim_end >= n:
            continue
        length_str = text[claim_start : claim_start + _COMPILED_CLAIM_LEN_DIGITS]
        if not all(c in _PO_CLAIM_LEN_CHARS for c in length_str):
            continue
        if text[claim_start + _COMPILED_CLAIM_LEN_DIGITS] != ":":
            continue
        opaque = text[claim_start + _COMPILED_CLAIM_LEN_DIGITS + 1 : claim_end]
        if not _po_tag_valid(opaque):
            continue
        body_len = int(length_str)
        # The claim authenticates IN PLACE, before any body
        # walk: the fixed-width claim binds the length under
        # the distinct claim purpose of the placement domain.
        if not hmac.compare_digest(
            opaque.encode("ascii"),
            _po_claim_opaque(key, namespace_key, placement, body_len).encode("ascii"),
        ):
            continue
        # The candidate is now ADMITTED (the claim
        # authenticated in place).  The ONE closing position,
        # located from the authenticated length: every wire
        # separator of the frame is verified to be the actual
        # newline of the input (never a canonical
        # reconstruction), and the boundary positions reject
        # equality with the end of the input BEFORE any
        # boundary byte is indexed (an incomplete line stays
        # ordinary data).
        body_end = claim_end + 1 + body_len
        if text[claim_end] != "\n":
            continue
        if body_end >= n or text[body_end] != "\n":
            continue
        tag_start = body_end + 1
        tag_end = tag_start + tag_line_len
        if tag_end >= n:
            continue
        if text[tag_end] != "\n":
            continue
        tag_line = text[tag_start:tag_end]
        if not tag_line.startswith(_PO_TAG_PREFIX) or not tag_line.endswith("]"):
            continue
        tag_opaque = tag_line[len(_PO_TAG_PREFIX) : -1]
        if not _po_tag_valid(tag_opaque):
            continue
        footer_start = tag_end + 1
        if (
            footer_start + footer_len > n
            or text[footer_start : footer_start + footer_len] != _COMPILED_FOOTER
        ):
            continue
        # The fixed-size claim and the closing-shape
        # validation are complete.  The pre-copy work charge:
        # the conservative UTF-8 byte bound (4 bytes per code
        # point) of the candidate's rendered payload (open
        # line + body + footer), computed from the
        # authenticated claim BEFORE any body copy or encoded
        # payload is constructed.  The charge upper-bounds the
        # candidate's actual verification bytes, so the closed
        # cap strictly bounds the scan's verification work.
        work += 4 * (body_len + _COMPILED_FRAME_SKELETON_CHARS)
        if work > work_cap:
            raise _PlacementOwnershipWorkExhausted
        # The exact body, verified by the EXISTING
        # placement-ownership tag: the digest is over the
        # ACTUAL wire bytes of the frame (open line, body and
        # footer -- every separator above verified as the
        # input's own newline).
        region_payload = text[p : body_end + 1] + text[footer_start : footer_start + footer_len]
        digest = hashlib.sha256(region_payload.encode("utf-8")).hexdigest()
        if hmac.compare_digest(
            tag_line.encode("ascii"),
            _po_tag_from_digest(key, namespace_key, placement, digest).encode("ascii"),
        ):
            return p, footer_start + footer_len
    return None


def _replace_owned_region(
    text: str,
    region: str,
    *,
    placement: str,
    namespace_key: str,
    key: bytes,
    work_cap: int,
) -> str | None:
    """Replace the positively owned prior-rendered region in
    place; ``None`` when no deterministic frame is owned by
    this trusted session and placement (no frame with an
    authenticating claim and a verifying tag -- every
    delimited span is caller data and the placement falls to
    the prepend law).  A placement field whose admitted
    candidate bodies exhaust the closed verification work
    bound propagates
    ``_PlacementOwnershipWorkExhausted`` (the fixed typed
    over-bound transform refusal at the transaction
    boundary)."""
    span = _owned_region_span(
        text, placement=placement, namespace_key=namespace_key, key=key, work_cap=work_cap
    )
    if span is None:
        return None
    start, end = span
    return text[:start] + region + text[end:]


def _place_region(
    text: str,
    region: str,
    *,
    placement: str,
    namespace_key: str,
    key: bytes,
    work_cap: int,
) -> str:
    """The deterministic placement into ONE string field: the
    positively owned existing region is replaced in place (the
    current compiled working set exactly -- a version change or
    reduced history carries the current set without duplicating
    a verified old region); otherwise the region is prepended
    and the caller's own text stays byte-identical data
    (including literal delimiter-like caller text)."""
    replaced = _replace_owned_region(
        text,
        region,
        placement=placement,
        namespace_key=namespace_key,
        key=key,
        work_cap=work_cap,
    )
    if replaced is not None:
        return replaced
    return region if not text else region + "\n\n" + text


def inject_compiled_context(
    payload: dict[str, Any],
    *,
    endpoint: str,
    blocks: tuple[str, ...],
    namespace_key: str,
    key: bytes,
    work_cap: int,
) -> dict[str, Any]:
    """The endpoint-specific stable compiled-context placement
    of the ACTUAL selected working set (order 022-d section 3;
    the approved rule 6: the stable reference is accompanied by
    the appropriate compiled context; R05: the source-absent
    reconstructed working set is reinjected without original
    source).

    Responses: the top-level ``instructions`` string (created
    when absent; the existing region replaced in place; the
    caller's own instructions preserved after the region).
    Chat: the stable system location (the first message when it
    is a string-content system message, otherwise a new system
    message inserted at the front; the same region law).  The
    region content is the closed concatenation of the rendered
    blocks in actual injection order -- the rendered blocks
    keep every source role / authority explicit, so the stable
    placement promotes nothing: off-graph content stays
    background inside its own rendered block.

    The placement-ownership law (order 022-e section 1): a
    prior rendered region is eligible for replacement ONLY
    under a verifying tag bound to this trusted namespace,
    this placement and the exact rendered payload (the same
    private per-session key material, a separate MAC domain);
    literal delimiter-like caller text is data, preserved
    byte-identical and never replaced.

    A non-empty working set whose placement field has an
    unsupported shape is the closed ``_CompiledInjectionShapeError``
    (the typed 422 refusal); an empty working set changes
    nothing.  The input is never mutated (a deep copy)."""
    if not blocks:
        return payload
    placement = _po_placement(endpoint)
    region = _compiled_region(blocks, placement=placement, namespace_key=namespace_key, key=key)
    copied = copy.deepcopy(payload)
    if endpoint == "responses":
        existing = copied.get("instructions")
        if existing is not None and not isinstance(existing, str):
            raise _CompiledInjectionShapeError("instructions shape")
        copied["instructions"] = (
            _place_region(
                existing,
                region,
                placement=placement,
                namespace_key=namespace_key,
                key=key,
                work_cap=work_cap,
            )
            if isinstance(existing, str)
            else region
        )
        return copied
    if endpoint == "chat":
        messages = copied.get("messages")
        if (
            not isinstance(messages, list)
            or not messages
            or not all(isinstance(item, dict) for item in messages)
        ):
            raise _CompiledInjectionShapeError("messages shape")
        first = messages[0]
        if first.get("role") == "system":
            content = first.get("content")
            if not isinstance(content, str):
                raise _CompiledInjectionShapeError("system content shape")
            first["content"] = _place_region(
                content,
                region,
                placement=placement,
                namespace_key=namespace_key,
                key=key,
                work_cap=work_cap,
            )
        else:
            copied["messages"] = [
                {"role": "system", "content": region},
                *messages,
            ]
        return copied
    raise _CompiledInjectionShapeError("endpoint shape")


@dataclass(frozen=True, slots=True)
class V1TransactionResult:
    """The prepared SINGLE outgoing request of one governed v1
    transaction.

    ``body`` is the EXACT serialized bytes the one main upstream
    forward receives: the transformed payload on ``OK``, the
    unchanged original payload on ``NO_REPLACEMENT`` (no replacement
    was earned for this payload; the request forwards as received,
    with no replacement claim and no dangling reference).  On
    ``OK`` the ACTUAL selected compiled context is additionally
    placed at the endpoint-specific stable location (top-level
    Responses ``instructions``; the Chat stable system message)
    before the single serialization.  The
    counters are the ACTUAL content-free transaction records
    (instrumentation evidence, never counter-only substitutes).
    ``selected_content_keys`` are digests (content-free).
    ``represented_frontier`` is the FROZEN represented completed-
    fact frontier of THIS specific committed request (the trusted
    issuance binding of the one forwarded body: derived from what
    the outgoing body actually represents, reduced over the proven
    ancestor relation only; never rebased on later state)."""

    outcome: ReplacementOutcome
    body: bytes = field(repr=False)
    edits_committed: int = 0
    markers_emitted: int = 0
    markers_replayed: int = 0
    selected_content_keys: tuple[str, ...] = ()
    represented_frontier: tuple[str, ...] = ()


def _serialize_payload(payload: dict[str, Any]) -> bytes:
    """The single outgoing serialization (the app's closed
    canonical form: compact separators, ASCII-escaped UTF-8)."""
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode()


# -- the final-request budget gate (order 022-e section 2) -------
#
# The accepted 021 tokenizer + BundleBudgetPlan envelope,
# capacity and selection semantics composed into the normal v1
# request path: the REAL final rendered governance (framing,
# guides and metadata included) and the REMAINING text / tools /
# request structure / retained images are each counted ONCE with
# the real pinned tokenizer; the supported endpoint generation
# fields are honored as-is (never silently changed); a required
# overflow is the fixed typed 422 BEFORE the one main forward
# (no silent truncation, no padding, no dangling reference).


def _requested_generation(
    payload: dict[str, Any], endpoint: str, plan: BundleBudgetPlan
) -> int | None | V1RequestRefusal:
    """The supported endpoint generation fields, honored as-is:
    Responses ``max_output_tokens``; Chat the ACTUAL effective
    field under the vLLM Chat protocol -- a non-null
    ``max_completion_tokens`` takes precedence over ``max_tokens``
    (an absent or explicit-null ``max_completion_tokens`` falls
    back to ``max_tokens``), so the typed 422 and capacity checks
    run on the effective value (order 022-f section 1): absent ->
    the plan's effective reserve; present -> a positive integer
    within the effective context, else the fixed typed 422 (the
    budget invalid-transform family -- the value is never silently
    changed or dropped, and both Chat fields stay on the wire as
    sent)."""
    if endpoint == "responses":
        value = payload.get("max_output_tokens")
    else:
        value = payload.get("max_completion_tokens")
        if value is None:
            value = payload.get("max_tokens")
    if value is None:
        return None
    if (
        type(value) is not int
        or isinstance(value, bool)
        or not (1 <= value <= plan.config.context_tokens)
    ):
        return V1RequestRefusal(V1RequestReason.SELECTION_REFUSED)
    return value


def _retained_image_count(payload: dict[str, Any]) -> int | V1RequestRefusal:
    """The retained images of the (image-policy-applied) payload
    under the app's own closed count (the per-image reserve
    consumer of the explicit vision contract); an ambiguous or
    over-bound shape is the fixed typed 422 (fail closed)."""
    try:
        return count_images(payload)
    except (AmbiguousImageShape, RecursionError):
        return V1RequestRefusal(V1RequestReason.SELECTION_REFUSED)


def _final_generation_capacity(
    plan: BundleBudgetPlan, requested_max_tokens: int | None, retained_images: int
) -> int | V1RequestRefusal:
    """The accepted residual capacity for ordinary request
    content (C minus the aggregate reservation, the honored
    generation, the tools and uncertainty reserves, and the
    retained-image reserves); an over-subscribed configuration
    or a retained image without the explicit vision contract is
    the fixed typed 422 before any compile or main forward."""
    try:
        return plan.request_capacity(
            plan.generation_effective(requested_max_tokens), retained_images
        )
    except BundleBudgetError:
        return V1RequestRefusal(V1RequestReason.SELECTION_REFUSED)


def _budget_tool_call(name: str, arguments: str) -> BudgetToolCall | None:
    """The closed tool-call arguments mapping for the accepted
    envelope model: the actual JSON object in insertion order,
    string values as-is and every other value in the pinned
    template's own JSON serialization (the same ensure-ASCII-
    false form the template renders); any other shape is
    uncountable (the fail-closed typed 422, never a guess)."""
    try:
        obj = json.loads(arguments)
    except (TypeError, ValueError):
        return None
    if not isinstance(obj, dict):
        return None
    pairs: list[tuple[str, str]] = []
    for arg_name, arg_value in obj.items():
        if not isinstance(arg_name, str):
            return None
        if isinstance(arg_value, str):
            pairs.append((arg_name, arg_value))
        else:
            try:
                pairs.append((arg_name, json.dumps(arg_value, ensure_ascii=False)))
            except (TypeError, ValueError):
                return None
    return BudgetToolCall(name=name, arguments=tuple(pairs))


def _envelope_tools(payload: dict[str, Any]) -> tuple[BudgetToolSpec, ...] | None:
    """The closed ``tools`` mapping: Responses carries the flat
    function spec (``type`` / ``name`` / ``description`` /
    ``parameters``) while Chat carries the same spec nested
    under ``function``; any other shape is uncountable (the
    fail-closed typed 422, never a guess)."""
    tools_field = payload.get("tools")
    if tools_field is None:
        return ()
    if not isinstance(tools_field, list):
        return None
    tools: list[BudgetToolSpec] = []
    for tool in tools_field:
        if not isinstance(tool, dict) or tool.get("type") != "function":
            return None
        spec = tool
        if "function" in tool:
            spec = tool["function"]
            if not isinstance(spec, dict):
                return None
        name = spec.get("name")
        description = spec.get("description", "")
        parameters = spec.get("parameters", {})
        if (
            not isinstance(name, str)
            or not isinstance(description, str)
            or not isinstance(parameters, dict)
        ):
            return None
        tools.append(BudgetToolSpec(name=name, description=description, parameters=parameters))
    return tuple(tools)


def _envelope_structure(
    payload: dict[str, Any], endpoint: str
) -> (
    tuple[tuple[BudgetMessage, ...], tuple[BudgetToolSpec, ...], tuple[BudgetToolCall, ...]] | None
):
    """The CLOSED mapping of the final API payload to the
    accepted model-envelope structure (messages / serialized
    tool data / tool calls) for the real-tokenizer final-request
    count: Responses top-level ``instructions`` as the system
    frame (an explicit null carries none), the ``input`` (a
    plain string or the items: the typed or easy message text
    parts, the bare content parts, function / custom tool calls
    and their outputs, carried reasoning summaries) and the
    ``tools`` list; Chat the ``messages``
    (string or text-part content, assistant tool calls, carried
    reasoning) and the ``tools`` list.  Every element must be a
    closed supported shape; any other shape is uncountable and
    the governed transaction is the fixed typed 422 (unknown
    capability fails closed -- never a guessed or dropped
    count).  Retained images are NOT message content: they are
    capacity consumers under the explicit vision contract
    (counted separately, once, by the accepted reserves)."""
    messages: list[BudgetMessage] = []
    calls: list[BudgetToolCall] = []
    if endpoint == "responses":
        instructions = payload.get("instructions")
        if instructions is not None:
            # An explicit null is the API's no-instructions state
            # (the placement law creates the field when the working
            # set is non-empty); any other non-string is uncountable.
            if not isinstance(instructions, str):
                return None
            messages.append(BudgetMessage(role="system", content=instructions))
        input_items = payload.get("input")
        if input_items is None:
            pass
        elif isinstance(input_items, str):
            # The ordinary Responses string input: one plain user
            # text message.
            messages.append(BudgetMessage(role="user", content=input_items))
        elif not isinstance(input_items, list):
            return None
        if isinstance(input_items, list):
            for item in input_items:
                if not isinstance(item, dict):
                    return None
                kind = item.get("type")
                if kind is None:
                    # The supported easy-message shape: no outer
                    # "type", the closed role and the content (the
                    # established session envelope law); any other
                    # type-less shape is uncountable.
                    if not (
                        isinstance(item.get("role"), str)
                        and item.get("role") in {"user", "assistant", "system", "developer"}
                        and "content" in item
                    ):
                        return None
                    kind = "message"
                if not isinstance(kind, str):
                    # A non-string item marker is never a supported
                    # item type (the closed RC2 law: unhashable
                    # values are never compared into a closed
                    # set): uncountable, the fixed typed 422.
                    return None
                if kind == "message":
                    role = item.get("role")
                    if not isinstance(role, str) or role not in {
                        "user",
                        "assistant",
                        "system",
                        "developer",
                    }:
                        return None
                    budget_role = "system" if role in {"system", "developer"} else role
                    content = item.get("content")
                    if isinstance(content, str):
                        messages.append(BudgetMessage(role=budget_role, content=content))
                    elif isinstance(content, list):
                        text_parts: list[str] = []
                        for part in content:
                            if not isinstance(part, dict):
                                return None
                            part_type = part.get("type")
                            if isinstance(part_type, str) and part_type in {
                                "input_text",
                                "output_text",
                                "text",
                            }:
                                if not isinstance(part.get("text"), str):
                                    return None
                                text_parts.append(part["text"])
                            elif part_type != "input_image":
                                return None
                        messages.append(
                            BudgetMessage(role=budget_role, content="".join(text_parts))
                        )
                    else:
                        return None
                elif kind in {"function_call", "custom_tool_call"}:
                    name = item.get("name")
                    arguments = (
                        item.get("arguments") if kind == "function_call" else item.get("input")
                    )
                    if not isinstance(name, str) or not isinstance(arguments, str):
                        return None
                    call = _budget_tool_call(name, arguments)
                    if call is None:
                        return None
                    messages.append(BudgetMessage(role="assistant", content=""))
                    calls.append(call)
                elif kind in {"function_call_output", "custom_tool_call_output"}:
                    output = item.get("output")
                    if isinstance(output, str):
                        messages.append(BudgetMessage(role="tool", content=output))
                    elif isinstance(output, list):
                        text_parts = []
                        for part in output:
                            if not isinstance(part, dict):
                                return None
                            part_type = part.get("type")
                            if isinstance(part_type, str) and part_type in {
                                "output_text",
                                "text",
                            }:
                                if not isinstance(part.get("text"), str):
                                    return None
                                text_parts.append(part["text"])
                            elif part_type != "input_image":
                                return None
                        messages.append(BudgetMessage(role="tool", content="".join(text_parts)))
                    else:
                        return None
                elif kind == "reasoning":
                    summary = item.get("summary")
                    if not isinstance(summary, list):
                        return None
                    texts: list[str] = []
                    for part in summary:
                        if not isinstance(part, dict) or part.get("type") != "summary_text":
                            return None
                        if not isinstance(part.get("text"), str):
                            return None
                        texts.append(part["text"])
                    messages.append(
                        BudgetMessage(
                            role="assistant",
                            content="",
                            reasoning_content="".join(texts),
                        )
                    )
                elif kind in {"input_text", "output_text", "text"}:
                    # A bare content part as plain user text input
                    # (the supported raw input): counted once as
                    # user text.
                    if not isinstance(item.get("text"), str):
                        return None
                    messages.append(BudgetMessage(role="user", content=item["text"]))
                elif kind == "input_image":
                    # A bare retained image part: a capacity
                    # consumer counted ONCE by the accepted per-
                    # image reserves, never message text.
                    pass
                else:
                    return None
    else:  # endpoint == "chat"
        messages_field = payload.get("messages")
        if not isinstance(messages_field, list) or not messages_field:
            return None
        for message in messages_field:
            if not isinstance(message, dict):
                return None
            role = message.get("role")
            if not isinstance(role, str) or role not in {
                "system",
                "user",
                "assistant",
                "tool",
            }:
                return None
            content = message.get("content")
            if content is None:
                text = ""
            elif isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text_parts = []
                for part in content:
                    if not isinstance(part, dict):
                        return None
                    part_type = part.get("type")
                    if part_type == "text":
                        if not isinstance(part.get("text"), str):
                            return None
                        text_parts.append(part["text"])
                    elif part_type != "image_url":
                        return None
                text = "".join(text_parts)
            else:
                return None
            if role == "assistant":
                reasoning = message.get("reasoning_content")
                if reasoning is not None and not isinstance(reasoning, str):
                    return None
                if reasoning is not None:
                    messages.append(
                        BudgetMessage(role=role, content=text, reasoning_content=reasoning)
                    )
                else:
                    messages.append(BudgetMessage(role=role, content=text))
                tool_calls = message.get("tool_calls")
                if tool_calls is not None:
                    if not isinstance(tool_calls, list):
                        return None
                    for call_obj in tool_calls:
                        if not isinstance(call_obj, dict) or call_obj.get("type") != "function":
                            return None
                        fn = call_obj.get("function")
                        if not isinstance(fn, dict):
                            return None
                        name = fn.get("name")
                        arguments = fn.get("arguments")
                        if not isinstance(name, str) or not isinstance(arguments, str):
                            return None
                        call = _budget_tool_call(name, arguments)
                        if call is None:
                            return None
                        calls.append(call)
            else:
                messages.append(BudgetMessage(role=role, content=text))
    tools = _envelope_tools(payload)
    if tools is None:
        return None
    return tuple(messages), tools, tuple(calls)


def _strip_owned_region(
    payload: dict[str, Any],
    *,
    endpoint: str,
    namespace_key: str,
    key: bytes,
    work_cap: int,
) -> dict[str, Any]:
    """The counting view of the ACTUAL emitted final payload
    (the final outgoing body after the stable compiled-context
    placement; order 022-g section 1) with the ONE verified
    placement-ownership region removed from the placement
    field, and NOTHING else removed.  On a transformed replay
    the old region is governance being replaced in place -- it
    is never ordinary request text, so the remaining request is
    counted once WITHOUT it (the new region is counted
    separately as the actual final rendered governance; nothing
    is double-counted and nothing is lost).  The complete
    system frame and separators survive byte-identical: the
    emitted frame keeps its own message slot in the counted
    envelope (its remainder after the span -- the caller's own
    instructions/system content and separator bytes, possibly
    empty on a generated frame -- stays the ordinary counted
    content of that message).  An unverified delimiter-like
    span is caller data: it is retained and counted as text
    (the over-count is the fail-closed direction -- the request
    is never under-counted).  The input is never mutated."""
    placement = _po_placement(endpoint)
    if endpoint == "responses":
        instructions = payload.get("instructions")
        if not isinstance(instructions, str):
            return payload
        span = _owned_region_span(
            instructions,
            placement=placement,
            namespace_key=namespace_key,
            key=key,
            work_cap=work_cap,
        )
        if span is None:
            return payload
        start, end = span
        return {**payload, "instructions": instructions[:start] + instructions[end:]}
    messages = payload.get("messages")
    if (
        not isinstance(messages, list)
        or not messages
        or not isinstance(messages[0], dict)
        or messages[0].get("role") != "system"
        or not isinstance(messages[0].get("content"), str)
    ):
        return payload
    content = messages[0]["content"]
    span = _owned_region_span(
        content, placement=placement, namespace_key=namespace_key, key=key, work_cap=work_cap
    )
    if span is None:
        return payload
    start, end = span
    first = {**messages[0], "content": content[:start] + content[end:]}
    return {**payload, "messages": [first, *messages[1:]]}


def _count_final_rest(
    payload: dict[str, Any],
    *,
    endpoint: str,
    plan: BundleBudgetPlan,
    requested_max_tokens: int | None,
    retained_images: int,
) -> int | V1RequestRefusal:
    """The REAL pinned-tokenizer count of the final request
    envelope of the given final payload (the caller supplies
    the ``_strip_owned_region`` counting view: the remaining
    text, tools, request structure and retained images, with
    the ONE verified prior placement region removed -- an
    unverified delimiter-like span is caller data and stays
    counted as text): counted ONCE under the accepted
    envelope / capacity semantics.  The accepted count raises
    the typed ``REQUEST_OVERFLOW`` when the content alone
    exceeds the residual capacity -- that is the fixed typed
    422 before any main forward (every other budget error,
    over-bound shape or missing vision contract, refuses the
    same way)."""
    try:
        structure = _envelope_structure(payload, endpoint)
    except ValidationError:
        # The accepted budget model's own closed bounds
        # (message-content / tool-description lengths) are
        # crossed by the over-bound request: the same fixed
        # typed 422, never a raw error.
        structure = None
    if structure is None:
        return V1RequestRefusal(V1RequestReason.SELECTION_REFUSED)
    messages, tools, calls = structure
    try:
        return plan.count_request_envelope(
            messages,
            tools,
            tool_calls=calls,
            enable_thinking=True,
            reasoning_instructions="",
            retained_images=retained_images,
            requested_max_tokens=requested_max_tokens,
        )
    except BundleBudgetError:
        return V1RequestRefusal(V1RequestReason.SELECTION_REFUSED)


def _root_candidate_paths(snapshot: Any, root_entry: Any) -> tuple[str, ...]:
    """The deterministic root-scope resolved candidates of the
    SAME-run F graph (the exact candidate set the root index is
    compiled and re-fenced against); a missing / refused F result
    carries no candidates.  FILE entries compile with none (the
    022-b transaction law)."""
    r_result = snapshot.result.r_result
    if r_result is None:
        return ()
    f_result = r_result.f_result
    if f_result is None or f_result.overlay is None:
        return ()
    seen: set[str] = set()
    paths: list[str] = []
    for record in f_result.overlay.candidates:
        if record.owner != root_entry.content_key:
            continue
        if record.candidate.status is not CandidateStatus.ACCEPTED:
            continue
        resolved = record.candidate.resolved_path
        if resolved is None or resolved in seen:
            continue
        seen.add(resolved)
        paths.append(resolved)
    return tuple(paths)


def _transaction_refusal(outcome: ReplacementOutcome) -> V1RequestRefusal:
    """The closed plan-13 failure family -> the fixed typed v1
    request refusal (503 infrastructure/recovery/resource; 409
    version/scope conflict; 422 budget/invalid transform)."""
    if outcome is ReplacementOutcome.SELECTION_NOT_READY:
        return V1RequestRefusal(V1RequestReason.SELECTION_REFUSED)
    if outcome is ReplacementOutcome.GENERATION_NOT_DURABLE:
        return V1RequestRefusal(V1RequestReason.GENERATION_NOT_DURABLE)
    if outcome is ReplacementOutcome.OVER_BOUND:
        return V1RequestRefusal(V1RequestReason.TRANSACTION_OVER_BOUND)
    return V1RequestRefusal(V1RequestReason.TRANSACTION_CONFLICT)


async def _compile_and_select(
    session: V1Session,
    runtime: V1Runtime,
    snapshot: Any,
) -> tuple[tuple[SelectionReadyEntry, ...], BundleSelectionDecision] | V1RequestRefusal:
    """The shared compile-and-select law of the transaction stage
    and the replay pre-check: compile the ACTUAL current admitted
    entries through the RAM work plane (the configured-policy
    fingerprint fence, single-flight, once per unchanged epoch; the
    internal compiler POST is direct and tool-free) and run the
    ACTUAL tokenizer budgets with required-first selection."""
    admission = snapshot.result.admission
    ready: list[SelectionReadyEntry] = []
    for entry in (admission.root_entry, *admission.entries):
        candidate_paths = (
            _root_candidate_paths(snapshot, entry)
            if entry.entry_class is EntryClass.ROOT_ENTRY
            else ()
        )
        work = await runtime.compile_work.resolve_entry(
            session.namespace,
            entry,
            candidate_paths=candidate_paths,
            plan=runtime.budget_plan,
        )
        if work.outcome is BundleCompileWorkOutcome.POLICY_STALE:
            return V1RequestRefusal(V1RequestReason.POLICY_STALE)
        if (
            work.outcome
            not in (
                BundleCompileWorkOutcome.COMPLETED,
                BundleCompileWorkOutcome.JOINED,
                BundleCompileWorkOutcome.HIT,
            )
            or work.index is None
        ):
            return V1RequestRefusal(V1RequestReason.COMPILER_REFUSED)
        represented = tuple(
            sorted(
                {
                    row.path
                    for row in admission.path_associations
                    if entry.content_key in row.content_keys
                }
            )
        )
        ready.append(
            SelectionReadyEntry(
                entry=entry,
                index=work.index,
                represented_paths=represented,
                candidate_paths=candidate_paths,
                origin_proven=(
                    entry.entry_class is EntryClass.ROOT_ENTRY or not unproven_member_paths(entry)
                ),
            )
        )
    root_ready, *file_readys = ready
    decision = select_working_set(root_ready, tuple(file_readys), runtime.budget_plan)
    if decision.outcome is not SelectionOutcome.OK:
        return V1RequestRefusal(V1RequestReason.SELECTION_REFUSED)
    return tuple(ready), decision


def _ensure_retained_publish(
    session: V1Session,
) -> RecoveryPublishResult | V1RequestRefusal:
    """The retained protected generation of the owner's CURRENT
    record set (the durable-generation handoff source for ordinary
    hits): the ACTUAL successful publication when the session
    already holds one, otherwise the protected checkpoint NOW (a
    resumed session's first ordinary hit materializes its restored
    record set's generation here — the pre-forward durable law: the
    replay pre-check and the fixed-point forward rely on a real
    publish of the exact snapshot the edits rely on)."""
    snapshot = session.owner.snapshot
    if snapshot is None:
        return V1RequestRefusal(V1RequestReason.COMMIT_REFUSED)
    if session.last_publish is not None and session.last_publish_bound == (
        snapshot.revision,
        snapshot.epoch,
    ):
        return session.last_publish
    # The retained pointer does not describe the CURRENT snapshot
    # (never published, or a committed-but-unpublished advance left
    # the newer record set undurable after a fault): materialize
    # the protected generation NOW; a refused or faulted
    # publication is the fixed typed pre-forward refusal -- the
    # newer undurable snapshot is refused on replay, never
    # forwarded under a stale proof.
    publish = session.checkpoint()
    if publish.limitation is not RecoveryStoreLimitation.OK:
        return V1RequestRefusal(V1RequestReason.PUBLISH_REFUSED)
    session.last_publish = publish
    session.last_publish_bound = (snapshot.revision, snapshot.epoch)
    return publish


async def prepare_replay_shadow(
    session: V1Session,
    runtime: V1Runtime,
    *,
    payload: dict[str, Any],
    endpoint: str,
    observation: ObservationReport,
) -> tuple[dict[str, Any] | None, V1RequestRefusal | None]:
    """Detect and authenticate marker-shaped source replays BEFORE
    any raw state acquisition (order 022-c section 1/2: the marker
    pre-check precedes the transition's raw acquisition, including
    the known superseded root-read coordinates the trusted prelude
    joins).

    No marker-like candidate anywhere in the decoded payload: the
    payload is returned by identity (no pre-check, no copy).  A
    candidate triggers the pure pre-check: the retained protected
    generation (checkpointed for a resumed session's first hit), the
    ACTUAL compile and selection under the retained snapshot, and
    the pure unsplice seam over the retained proof — a stale /
    forged / malformed / unknown-kind / moved marker is the fixed
    typed refusal (the marker-side 409 family; the raw acquisition
    is never committed over marker bytes), and every exactly-
    verified replay is unspliced to its retained original.  The
    returned shadow is what the region-lineage transition
    observes; ordinary non-source text stays data (the
    closed-location carrier scan never reads it)."""
    if not payload_has_marker_candidates(payload):
        return payload, None
    publish = _ensure_retained_publish(session)
    if isinstance(publish, V1RequestRefusal):
        return None, publish
    snapshot = session.owner.snapshot
    if snapshot is None:
        return None, V1RequestRefusal(V1RequestReason.COMMIT_REFUSED)
    compiled = await _compile_and_select(session, runtime, snapshot)
    if isinstance(compiled, V1RequestRefusal):
        return None, compiled
    ready, decision = compiled
    roots = observation.roots.roots
    result = unsplice_replayed_markers(
        payload,
        proof=PreparedGenerationProof(publish=publish, snapshot=snapshot),
        current_snapshot=snapshot,
        ready_entries=ready,
        decision=decision,
        observation=observation,
        root_occurrence=roots[0] if roots else None,
        key=runtime.marker_key,
        max_text_chars=_V1_MAX_TEXT_CHARS,
    )
    if result.outcome is not ReplacementOutcome.OK:
        return None, _transaction_refusal(result.outcome)
    assert result.shadow_payload is not None
    return result.shadow_payload, None


async def prepare_v1_transaction(
    session: V1Session,
    runtime: V1Runtime,
    *,
    payload: dict[str, Any],
    endpoint: str,
    observation: ObservationReport,
    proof: PreparedGenerationProof,
) -> V1TransactionResult | V1RequestRefusal:
    """The governed transaction stage over the prepared generation.

    Compiles the ACTUAL current admitted entries through the RAM
    work plane (the configured-policy fingerprint fence,
    single-flight, once per unchanged epoch; the internal compiler
    POST is direct and tool-free), runs the ACTUAL tokenizer
    budgets and required-first selection with final envelope
    accounting, and applies the PURE exact-span source-replacement
    transaction BEFORE the single serialization.  ``observation``
    is the ACTUAL 017 observation of THIS payload under the
    verified workspace -- the geometry observation the final
    replay scan runs over.

    Returns the exact outgoing body (transformed on OK, unchanged
    original on NO_REPLACEMENT) or the fixed typed refusal: a
    refused governed transaction never falls back to a raw
    forward, never double-serializes and never auto-replays."""
    snapshot = session.owner.snapshot
    if snapshot is None or proof.snapshot is not snapshot:
        # The durable-generation handoff binds the EXACT retained
        # snapshot by identity; a drifted handoff is a commit-level
        # refusal, never a guess.
        return V1RequestRefusal(V1RequestReason.COMMIT_REFUSED)
    t = snapshot.result
    if t.outcome is not RootRegionAdmissionOutcome.READY:
        # The ACTUAL same-run T outcome classifies the governed
        # transaction (order 022-d section 2): an established
        # root whose currentness is UNPROVEN or whose authority
        # CONFLICTS is the accepted typed 409 with zero main
        # forward (the negative P/Q evidence is committed and
        # retained, no bootstrap fallback), and a fixed typed T
        # consumer refusal (a T-outer crossing, a mapped R
        # refusal or an actual G-domain refusal) is the typed 503
        # admission refusal.  Both refuse the transaction stage:
        # no replacement, no raw forward, no dangling reference.
        if t.outcome in (
            RootRegionAdmissionOutcome.ROOT_CURRENTNESS_UNPROVEN,
            RootRegionAdmissionOutcome.ROOT_AUTHORITY_CONFLICT,
        ):
            return V1RequestRefusal(V1RequestReason.TRANSACTION_CONFLICT)
        return V1RequestRefusal(V1RequestReason.ADMISSION_REFUSED)
    admission = t.admission
    if admission is None:
        # Unreachable: the admission parent is present exactly on a
        # READY outcome; fail closed rather than guess.
        return V1RequestRefusal(V1RequestReason.COMMIT_REFUSED)
    plan = runtime.budget_plan
    # The closed ownership-scan work cap is DERIVED FROM THE
    # ACTUAL CONFIGURED COMPILED-RENDER BUDGET (order 022-g
    # section 2): count_compiled_block checks the WHOLE framed
    # region against the configured compiled-block byte limit,
    # so an otherwise-valid single emitted frame verifies
    # under the cap by construction (never refused by an older
    # carrier-observation constant).
    work_cap = _placement_work_cap(plan.config.max_compiled_block_bytes)
    # The final-request budget gate runs BEFORE any compile work
    # (order 022-e section 2): the supported endpoint generation
    # field and the retained-image reserves are honored as-is, and
    # an over-subscribed request (generation beyond the effective
    # context, or reserves plus the aggregate exceeding C) is the
    # fixed typed 422 before any compile or main forward -- never
    # a silent value change, never a raw forward.
    req_gen = _requested_generation(payload, endpoint, plan)
    if isinstance(req_gen, V1RequestRefusal):
        return req_gen
    images = _retained_image_count(payload)
    if isinstance(images, V1RequestRefusal):
        return images
    capacity = _final_generation_capacity(plan, req_gen, images)
    if isinstance(capacity, V1RequestRefusal):
        return capacity
    compiled = await _compile_and_select(session, runtime, snapshot)
    if isinstance(compiled, V1RequestRefusal):
        return compiled
    ready, decision = compiled
    roots = observation.roots.roots
    namespace_key = snapshot.namespace.lineage_key
    key = runtime.marker_key
    placement = _po_placement(endpoint)
    result = replace_sources(
        payload,
        proof=proof,
        current_snapshot=snapshot,
        ready_entries=tuple(ready),
        decision=decision,
        observation=observation,
        root_occurrence=roots[0] if roots else None,
        key=runtime.marker_key,
        max_text_chars=_V1_MAX_TEXT_CHARS,
    )
    if result.outcome is ReplacementOutcome.OK:
        assert result.transformed_payload is not None
        decision_now = decision
        result_now = result
        forced: list[str] = []
        while True:
            # The selected compiled context accompanies the
            # transformed body at the endpoint-specific stable
            # placement BEFORE the single serialization (order
            # 022-d section 3: the marker is never the model's
            # only governing content; the source-absent working
            # set is reinjected without original source); the
            # region carries its placement-ownership tag (order
            # 022-e section 1).
            region = _compiled_region(
                result_now.compiled_blocks,
                placement=placement,
                namespace_key=namespace_key,
                key=key,
            )
            assert result_now.transformed_payload is not None
            try:
                final_payload = inject_compiled_context(
                    result_now.transformed_payload,
                    endpoint=endpoint,
                    blocks=result_now.compiled_blocks,
                    namespace_key=namespace_key,
                    key=key,
                    work_cap=work_cap,
                )
            except _CompiledInjectionShapeError:
                # The placement field has an unsupported shape:
                # the typed 422 invalid-transform refusal (never
                # a raw forward, never a guessed placement).
                return V1RequestRefusal(V1RequestReason.SELECTION_REFUSED)
            except _PlacementOwnershipWorkExhausted:
                # The placement field's admitted candidate bodies
                # exhausted the closed verification work cap:
                # the fixed typed over-bound transform refusal
                # (never a silent no-ownership prepend, never a
                # raw forward).
                return V1RequestRefusal(V1RequestReason.TRANSACTION_OVER_BOUND)
            # The REAL final accounting (order 022-g section 1):
            # the remaining request of the ACTUAL emitted payload
            # (the final outgoing body after the stable placement:
            # text, tools, request structure and retained images)
            # counted ONCE, and the actual final rendered
            # governance (framing, guides and metadata included)
            # counted ONCE -- both with the real pinned tokenizer,
            # under the accepted capacity / aggregate law.  The
            # ordinary-content view keeps the complete system
            # frame and its separators (the emitted frame
            # occupies its own message slot; only the exact
            # authenticated governance span is excluded from the
            # ordinary count), so the first request and the
            # replay of the exact emitted body count identically.
            try:
                count_view = _strip_owned_region(
                    final_payload,
                    endpoint=endpoint,
                    namespace_key=namespace_key,
                    key=key,
                    work_cap=work_cap,
                )
            except _PlacementOwnershipWorkExhausted:
                # The counting view's ownership scan exhausted
                # the closed verification work bound: the same
                # fixed typed over-bound transform refusal.
                return V1RequestRefusal(V1RequestReason.TRANSACTION_OVER_BOUND)
            rest = _count_final_rest(
                count_view,
                endpoint=endpoint,
                plan=plan,
                requested_max_tokens=req_gen,
                retained_images=images,
            )
            if isinstance(rest, V1RequestRefusal):
                return rest
            try:
                governance = plan.count_compiled_block(region)
            except BundleBudgetError:
                return V1RequestRefusal(V1RequestReason.SELECTION_REFUSED)
            if governance <= plan.aggregate:
                break
            # The actual final rendered governance (its framing
            # included) does not fit the aggregate: the
            # deterministic whole-entry OPTIONAL omission, lowest
            # priority first -- a coherent replacement/selection
            # re-run (an omitted carrier earns only the
            # non-resolving evidence marker, never a dangling
            # live reference).  Required overflow is the fixed
            # typed 422 (never truncated).
            optionals = [row.content_key for row in decision_now.working_set if not row.required]
            if not optionals:
                return V1RequestRefusal(V1RequestReason.SELECTION_REFUSED)
            forced.append(optionals[-1])
            root_ready, *file_readys = ready
            decision_now = select_working_set(
                root_ready,
                tuple(file_readys),
                plan,
                requested_max_tokens=req_gen,
                retained_images=images,
                force_omitted=tuple(forced),
            )
            if decision_now.outcome is not SelectionOutcome.OK:
                return V1RequestRefusal(V1RequestReason.SELECTION_REFUSED)
            result_now = replace_sources(
                payload,
                proof=proof,
                current_snapshot=snapshot,
                ready_entries=tuple(ready),
                decision=decision_now,
                observation=observation,
                root_occurrence=roots[0] if roots else None,
                key=key,
                max_text_chars=_V1_MAX_TEXT_CHARS,
            )
            if result_now.outcome is not ReplacementOutcome.OK:
                return _transaction_refusal(result_now.outcome)
        return V1TransactionResult(
            outcome=result_now.outcome,
            body=_serialize_payload(final_payload),
            edits_committed=result_now.edits_committed,
            markers_emitted=result_now.markers_emitted,
            markers_replayed=result_now.markers_replayed,
            selected_content_keys=result_now.selected_content_keys,
            represented_frontier=represented_frontier(
                snapshot,
                admission=admission,
                working_set=decision_now.working_set,
                file_edits=result_now.edits,
                root_observed=bool(roots),
            ),
        )
    if result.outcome is ReplacementOutcome.NO_REPLACEMENT:
        # The unchanged original still forwards as the ONE main
        # request: the same final-request budget law applies to
        # it (the honored generation, the retained-image
        # reserves, the remaining text / tools / structure
        # counted once); the request-level overflow is the fixed
        # typed 422 before the main forward.
        rest = _count_final_rest(
            payload,
            endpoint=endpoint,
            plan=plan,
            requested_max_tokens=req_gen,
            retained_images=images,
        )
        if isinstance(rest, V1RequestRefusal):
            return rest
        return V1TransactionResult(
            outcome=result.outcome,
            body=_serialize_payload(payload),
            selected_content_keys=result.selected_content_keys,
            represented_frontier=represented_frontier(
                snapshot,
                admission=admission,
                working_set=(),
                file_edits=(),
                root_observed=bool(roots),
            ),
        )
    return _transaction_refusal(result.outcome)


# -- the trusted issuance binding of the forwarded request (order
# 022-c section 3) -------------------------------------------------

#: The closed bounds of the post-forward issuance observer: the
#: in-flight call count, the per-call argument assembly, the ONE
#: incomplete SSE frame, the total event count and the chat
#: per-choice tool-call slots.  Crossing any bound DISABLES the
#: observer (no further issuance; the response is still passed
#: through unchanged -- a narrow typed limitation, never a buffer
#: of the full stream).
_V1_ISSUANCE_MAX_INFLIGHT_CALLS = 64
_V1_ISSUANCE_MAX_ARGUMENT_BYTES = 262_144
_V1_ISSUANCE_MAX_FRAME_BYTES = 1_048_576
_V1_ISSUANCE_MAX_EVENTS = 8_192
_V1_ISSUANCE_MAX_CHAT_TOOL_CALLS = 128
_V1_ISSUANCE_JSON_MAX_DEPTH = 32


@dataclass(frozen=True, slots=True)
class V1IssuedCallShape:
    """One COMPLETE supported tool call observed in the ACTUAL
    direct main upstream response (the closed extraction shape:
    the raw arguments cross only to the canonical
    ``causal-arguments-json/v1`` recipe at registration; they are
    never retained in any state record)."""

    call_id: str
    tool_name: str
    arguments: str = field(repr=False)


def represented_frontier(
    snapshot: Any,
    *,
    admission: Any | None,
    working_set: tuple[Any, ...],
    file_edits: tuple[Any, ...],
    root_observed: bool,
) -> tuple[str, ...]:
    """The FROZEN represented completed-fact frontier of this
    specific committed main request (order 022-c section 3).

    Membership is derived from what THIS request's single outgoing
    body actually represents -- never from the retained state as a
    whole: the represented root fact (the governing envelope anchor
    or the governing read / read_region occurrence, when the root
    is represented by this request) plus the retained occurrence of
    every file source this request represents (every selected
    compiled entry's witness provenance and every verified
    raw-carrier join of this payload).  Retained history this
    request does NOT represent -- omitted, superseded, absent or
    off-graph occurrences -- adds no member: a retained fact is
    never a parent by arrival, digest, revision or mere retention.
    The members are reduced over the PROVEN frozen-edge ancestor
    relation only: a proven ancestor of another member reduces,
    every relevant incomparable member is kept, and the result is
    the canonical (sorted, deduplicated) form.  The frontier
    freezes at this request's commit; it never rebases on later
    global state, caller assistant items, result arrival, new call
    IDs, contents, revisions or replay metadata."""
    d_state = snapshot.state.d_state
    members: set[str] = set()
    selected_file_keys: set[str] = set()
    root_selected = False
    for row in working_set:
        if row.entry_class is EntryClass.FILE_BUNDLE_ENTRY:
            selected_file_keys.add(row.content_key)
        elif row.entry_class is EntryClass.ROOT_ENTRY:
            root_selected = True
    # The represented root fact of THIS request: the selected root
    # entry's resolved source (the governing read / read_region
    # occurrence when the governing root came from a read; the
    # bootstrap anchor otherwise).
    if root_selected and admission is not None:
        source = admission.root_entry.root_source
        if source is not None and source.occurrence is not None:
            members.add(source.occurrence.occurrence_id)
        elif source is not None and d_state.root is not None:
            members.add(CAUSAL_ROOT_FACT)
    elif root_observed and d_state.root is not None:
        # No working set (the unchanged raw forward): the root is
        # represented when its envelope carrier is in THIS payload.
        members.add(CAUSAL_ROOT_FACT)
    # The selected file entries' retained witness provenance.
    entries_by_key = (
        {entry.content_key: entry for entry in admission.entries} if admission is not None else {}
    )
    for key in selected_file_keys:
        entry = entries_by_key.get(key)
        if entry is not None and entry.witnesses:
            members.add(entry.witnesses[0].occurrence_id)
    # The verified raw-carrier joins of THIS payload (the committed
    # file edits; a subset of the selected provenance by the plan
    # law, kept explicit as the carrier-level representation fact).
    for edit in file_edits:
        if edit.target_entry_class == EntryClass.FILE_BUNDLE_ENTRY.value:
            members.add(edit.occurrence_identity)
    parents: dict[str, tuple[str, ...]] = {}
    for link in d_state.parent_links:
        parents[link.child] = (*parents.get(link.child, ()), link.parent)
    ancestor_cache: dict[str, frozenset[str]] = {}

    def proven_ancestors(node: str) -> frozenset[str]:
        cached = ancestor_cache.get(node)
        if cached is not None:
            return cached
        seen: set[str] = set()
        stack = [node]
        while stack:
            current = stack.pop()
            for parent in parents.get(current, ()):
                if parent not in seen:
                    seen.add(parent)
                    stack.append(parent)
        result = frozenset(seen)
        ancestor_cache[node] = result
        return result

    frozen = set()
    for member in members:
        if not any(member in proven_ancestors(other) for other in members if other != member):
            frozen.add(member)
    return tuple(sorted(frozen))


def _bounded_event_object(body: bytes) -> dict[str, Any] | None:
    """The ONE bounded strict JSON object of an actual direct
    upstream response (nesting-bounded before the single parse
    walk); a malformed object is a plain ``None`` (no issuance,
    never a guess)."""
    try:
        enforce_json_nesting(body, _V1_ISSUANCE_JSON_MAX_DEPTH)
        value = json.loads(body)
    except (JsonNestingTooDeep, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def _responses_complete_calls(body: bytes) -> tuple[V1IssuedCallShape, ...]:
    """The COMPLETE supported function calls of ONE final
    Responses object: a non-``completed`` status is truncated /
    incomplete evidence (no issuance), and a call item is complete
    only with a bounded closed string binding."""
    event = _bounded_event_object(body)
    if event is None or event.get("status") != "completed":
        return ()
    output = event.get("output")
    if not isinstance(output, list):
        return ()
    calls: list[V1IssuedCallShape] = []
    for item in output:
        if (
            isinstance(item, dict)
            and item.get("type") == "function_call"
            and isinstance(item.get("call_id"), str)
            and isinstance(item.get("name"), str)
            and isinstance(item.get("arguments"), str)
        ):
            calls.append(V1IssuedCallShape(item["call_id"], item["name"], item["arguments"]))
    return tuple(calls)


def _chat_complete_calls(body: bytes) -> tuple[V1IssuedCallShape, ...]:
    """The COMPLETE supported tool calls of ONE final Chat object:
    a ``length`` finish reason is explicit truncation (no
    issuance), and a call is complete only with a bounded closed
    string binding on the final message."""
    event = _bounded_event_object(body)
    if event is None:
        return ()
    choices = event.get("choices")
    if not isinstance(choices, list):
        return ()
    calls: list[V1IssuedCallShape] = []
    for choice in choices:
        if not isinstance(choice, dict) or choice.get("finish_reason") == "length":
            continue
        message = choice.get("message")
        if not isinstance(message, dict):
            continue
        tool_calls = message.get("tool_calls")
        if not isinstance(tool_calls, list):
            continue
        for tool_call in tool_calls:
            if not isinstance(tool_call, dict):
                continue
            function = tool_call.get("function")
            if (
                isinstance(tool_call.get("id"), str)
                and isinstance(function, dict)
                and isinstance(function.get("name"), str)
                and isinstance(function.get("arguments"), str)
            ):
                calls.append(
                    V1IssuedCallShape(tool_call["id"], function["name"], function["arguments"])
                )
    return tuple(calls)


@dataclass(slots=True)
class _InflightCall:
    """The bounded incremental assembly of ONE streamed tool call
    (the per-call argument buffer -- the ONLY assembly state; the
    full stream is never buffered)."""

    call_id: str
    tool_name: str
    arguments: str = ""
    argument_bytes: int = 0


@dataclass(slots=True)
class V1IssuanceContext:
    """The frozen post-forward trusted-issuance context of ONE
    committed main request (order 022-c section 3): the committed
    state, the trusted namespace, the FROZEN represented frontier
    (a pure function of the committed snapshot -- never rebased on
    later state, caller items, result arrival, new call IDs,
    revisions or replay metadata) and the endpoint family.

    The observer consumes the ACTUAL direct main upstream response
    (never compiler traffic) incrementally and registers each
    COMPLETE supported tool call under the accepted 018 issuance
    law against the committed-state CAS: a refused or replayed
    registration changes nothing and is never retried; a drifted
    owner (a concurrent request) is a CAS refusal, never a rebase.
    No issuance is earned from malformed / incomplete / truncated
    events: a malformed event is ignored, an incomplete assembly
    is dropped at stream end and a bound crossing disables the
    observer."""

    session: V1Session
    namespace: Any  # RootRegionLineageNamespace (the registered record)
    state: Any  # RootRegionLineageState (the committed snapshot state)
    frontier: tuple[str, ...]
    endpoint: str

    _frame: bytearray = field(default_factory=bytearray, repr=False, compare=False)
    _resp_inflight: dict[str, _InflightCall] = field(
        default_factory=dict, repr=False, compare=False
    )
    _chat_choices: dict[int, dict[int, _InflightCall]] = field(
        default_factory=dict, repr=False, compare=False
    )
    _events: int = field(default=0, repr=False, compare=False)
    _disabled: bool = field(default=False, repr=False, compare=False)

    # -- the response boundary hooks ------------------------------

    def observe_nonstream(self, body: bytes) -> None:
        """The nonstreaming actual direct response: the COMPLETE
        supported tool calls of the final object (both endpoints)
        are registered; a malformed or non-completed object earns
        no issuance (the response is still passed through)."""
        if self._disabled:
            return
        calls = (
            _responses_complete_calls(body)
            if self.endpoint == "responses"
            else _chat_complete_calls(body)
        )
        for call in calls:
            self._register(call)

    def observe_stream_chunk(self, chunk: bytes) -> None:
        """ONE streamed chunk of the actual direct SSE response:
        the bounded incremental assembly (the ONE incomplete frame
        buffer plus the per-call argument buffers) -- a call is
        registered only when COMPLETE (its own done / finish
        evidence), never from a partial event; the full stream is
        never buffered."""
        if self._disabled:
            return
        self._frame.extend(chunk)
        while True:
            frame = self._next_frame()
            if frame is None:
                return
            self._handle_frame(frame)
            if self._disabled:
                return

    # -- the bounded frame / event assembly -----------------------

    def _disable(self) -> None:
        """The narrow typed limitation: a bound crossing stops the
        observation (the response still passes through unchanged)."""
        self._disabled = True
        self._frame = bytearray()
        self._resp_inflight.clear()
        self._chat_choices.clear()

    def _next_frame(self) -> bytes | None:
        """Split ONE complete SSE frame (the LF or CRLF event
        separator) from the bounded frame buffer; ``None`` while
        the buffer holds only an incomplete frame (or after a
        frame-size bound crossing)."""
        buffer = self._frame
        index_lf = buffer.find(b"\n\n")
        index_crlf = buffer.find(b"\r\n\r\n")
        candidates = [i for i in (index_lf, index_crlf) if i >= 0]
        if not candidates:
            if len(buffer) > _V1_ISSUANCE_MAX_FRAME_BYTES:
                self._disable()
                return None
            return None
        index = min(candidates)
        separator = 4 if buffer[index : index + 2] == b"\r\n" else 2
        frame = buffer[:index]
        del buffer[: index + separator]
        if frame.endswith(b"\r"):
            frame = frame[:-1]
        if len(frame) > _V1_ISSUANCE_MAX_FRAME_BYTES:
            self._disable()
            return None
        return bytes(frame)

    def _handle_frame(self, frame: bytes) -> None:
        """One complete SSE frame: the ``data:`` payload of the
        event (a comment / keep-alive frame carries no event); a
        malformed event earns no issuance."""
        self._events += 1
        if self._events > _V1_ISSUANCE_MAX_EVENTS:
            self._disable()
            return
        data_lines: list[bytes] = []
        for line in frame.split(b"\n"):
            line = line.rstrip(b"\r")
            if line.startswith(b"data:"):
                data_lines.append(line[5:].lstrip(b" "))
        if not data_lines:
            return
        payload = b"\n".join(data_lines)
        if payload == b"[DONE]":
            self._finish_stream()
            return
        try:
            enforce_json_nesting(payload, _V1_ISSUANCE_JSON_MAX_DEPTH)
            event = json.loads(payload)
        except (JsonNestingTooDeep, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            return
        if not isinstance(event, dict):
            return
        if self.endpoint == "responses":
            self._handle_responses_event(event)
        else:
            self._handle_chat_event(event)

    def _finish_stream(self) -> None:
        """Stream end (``[DONE]`` / the terminal Responses event):
        every still-incomplete assembly is dropped -- no issuance
        from an incomplete call."""
        self._resp_inflight.clear()
        self._chat_choices.clear()

    def _append_arguments(self, call: _InflightCall, fragment: str) -> bool:
        """Append ONE bounded argument fragment (a crossing
        disables the observer)."""
        piece = len(fragment.encode("utf-8"))
        if call.argument_bytes + piece > _V1_ISSUANCE_MAX_ARGUMENT_BYTES:
            self._disable()
            return False
        call.arguments += fragment
        call.argument_bytes += piece
        return True

    # -- the Responses SSE assembly --------------------------------

    def _handle_responses_event(self, event: dict[str, Any]) -> None:
        kind = event.get("type")
        if kind == "response.output_item.added":
            item = event.get("item")
            if (
                isinstance(item, dict)
                and item.get("type") == "function_call"
                and isinstance(item.get("call_id"), str)
                and isinstance(item.get("name"), str)
                and len(self._resp_inflight) < _V1_ISSUANCE_MAX_INFLIGHT_CALLS
            ):
                self._resp_inflight[item["call_id"]] = _InflightCall(
                    call_id=item["call_id"], tool_name=item["name"]
                )
        elif kind == "response.function_call_arguments.delta":
            item_id = event.get("item_id")
            delta = event.get("delta")
            call = self._resp_inflight.get(item_id) if isinstance(item_id, str) else None
            if call is not None and isinstance(delta, str):
                self._append_arguments(call, delta)
        elif kind in ("response.function_call_arguments.completed", "response.output_item.done"):
            item_id = event.get("item_id")
            item = event.get("item")
            call_id = None
            if isinstance(item_id, str):
                call_id = item_id
            elif isinstance(item, dict) and isinstance(item.get("call_id"), str):
                call_id = item["call_id"]
            call = self._resp_inflight.pop(call_id, None) if call_id is not None else None
            if call is not None:
                # The authoritative complete arguments when the
                # event carries them (the accumulated deltas
                # otherwise -- the split assembly law).
                arguments = (
                    event.get("arguments")
                    if kind == "response.function_call_arguments.completed"
                    else (item.get("arguments") if isinstance(item, dict) else None)
                )
                if isinstance(arguments, str):
                    call.arguments = arguments
                self._register(V1IssuedCallShape(call.call_id, call.tool_name, call.arguments))
        elif kind in ("response.completed", "response.failed", "response.incomplete"):
            self._finish_stream()

    # -- the Chat SSE assembly --------------------------------------

    def _handle_chat_event(self, event: dict[str, Any]) -> None:
        choices = event.get("choices")
        if not isinstance(choices, list):
            return
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            index = choice.get("index")
            if not isinstance(index, int):
                continue
            delta = choice.get("delta")
            if isinstance(delta, dict) and isinstance(delta.get("tool_calls"), list):
                for tool_call in delta["tool_calls"]:
                    if not isinstance(tool_call, dict):
                        continue
                    slot = tool_call.get("index")
                    if not isinstance(slot, int):
                        continue
                    slot_map = self._chat_choices.setdefault(index, {})
                    call = slot_map.get(slot)
                    if call is None:
                        if len(slot_map) >= _V1_ISSUANCE_MAX_CHAT_TOOL_CALLS:
                            self._disable()
                            return
                        call = _InflightCall(call_id="", tool_name="")
                        slot_map[slot] = call
                    call_id = tool_call.get("id")
                    if isinstance(call_id, str) and call_id and not call.call_id:
                        call.call_id = call_id
                    function = tool_call.get("function")
                    if isinstance(function, dict):
                        name = function.get("name")
                        if isinstance(name, str) and name and not call.tool_name:
                            call.tool_name = name
                        arguments = function.get("arguments")
                        if isinstance(arguments, str):
                            if not self._append_arguments(call, arguments):
                                return
            if choice.get("finish_reason") is not None:
                # The choice is complete: the calls with a complete
                # closed binding are registered; the rest is
                # dropped (never a partial issuance).
                slot_map = self._chat_choices.pop(index, {})
                for call in slot_map.values():
                    if call.call_id and call.tool_name:
                        self._register(
                            V1IssuedCallShape(call.call_id, call.tool_name, call.arguments)
                        )

    # -- the trusted registration ----------------------------------

    def _register(self, call: V1IssuedCallShape) -> None:
        """Register ONE complete supported call under the accepted
        018 issuance law against the committed-state CAS: the
        FROZEN frontier is never rebased; an ACCEPTED registration
        commits through the ACTUAL 020 owned/fenced admit (the
        adverse durable fence law, the owned store-IO slot, the
        bounded transient reservation and the bound-generation
        CAS -- the permitted derived metadata only, the canonical
        fingerprint, never the raw arguments); a REPLAYED or
        refused registration changes nothing (no retry, no
        invented frontier, no upgraded evidence); a quarantined
        owner is torn down at the next request through the
        steady-state guard (the durable-quarantine exit)."""
        transition = register_root_region_issuance(
            self.state,
            self.namespace,
            call.call_id,
            self.endpoint,
            call.tool_name,
            call.arguments,
            self.frontier,
            self.state.revision,
        )
        if transition.outcome is not RootLineageOutcome.ACCEPTED:
            return
        admission = derive_root_region_admission(transition.state, self.namespace)
        session_owner = self.session.session_owner
        assert session_owner is not None
        fenced = session_owner.admit_with_fence(
            transition.state,
            admission,
            expected_revision=self.session.owner.revision,
        )
        if fenced.outcome is not RecoveryAdmitOutcome.ADMITTED:
            # A refused / fence-blocked registration commits
            # nothing and is never retried (the prior committed
            # generation stays valid; a quarantined owner exits
            # at the next request through the steady-state
            # guard).
            return
        new_snapshot = self.session.owner.snapshot
        if (
            fenced.advance is not None
            and fenced.advance.limitation is RecoveryStoreLimitation.OK
            and new_snapshot is not None
        ):
            # The retained successful pointer is bound to the exact
            # snapshot/epoch it actually published (a faulted
            # publication keeps the prior bound: the newer record
            # set stays undurable and is refused on replay).
            self.session.last_publish = fenced.advance
            self.session.last_publish_bound = (
                new_snapshot.revision,
                new_snapshot.epoch,
            )
        if new_snapshot is not None:
            # The context moves to the new committed state (the
            # next call of the same response registers under it);
            # the frozen frontier itself never changes.
            self.state = new_snapshot.state


__all__ = [
    "V1RequestReason",
    "V1RequestRefusal",
    "V1_REQUEST_FAILURES",
    "V1TransactionResult",
    "V1Session",
    "V1SessionTable",
    "V1IssuanceContext",
    "V1IssuedCallShape",
    "build_session_address",
    "build_v1_namespace",
    "establish_v1_session",
    "advance_v1_session",
    "inject_compiled_context",
    "represented_frontier",
    "prepare_replay_shadow",
    "prepare_v1_transaction",
]
