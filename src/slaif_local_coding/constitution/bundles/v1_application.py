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

import json
import threading
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from ...json_structure import JsonNestingTooDeep, enforce_json_nesting
from ..cache import RequestIdentity
from .bundle_admission_models import AdmissionMode, EntryClass, make_bundle_admission_namespace
from .bundle_compile_work import (
    BundleCompileWorkOutcome,
    derive_compile_policy_fingerprint,
)
from .bundle_compiler import unproven_member_paths
from .bundle_replace import (
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
    RecoveryResumeOutcome,
    RecoverySessionOwner,
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


def establish_v1_session(
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
    namespace = build_v1_namespace(runtime, identity, route, contract, address, workspace)
    owner = runtime.ram_registry.acquire(namespace)
    context = PathContext(workspace=workspace)
    transition = bootstrap_root_region_lineage(
        (GraphRequest(payload=payload, endpoint=endpoint, context=context),), namespace
    )
    if transition.outcome is not RootLineageOutcome.ACCEPTED:
        return _cold_scope_refusal(V1RequestReason.BOOTSTRAP_REFUSED)
    admission = derive_root_region_admission(transition.state, namespace)
    commit = owner.admit(transition.state, admission, namespace, expected_revision=owner.revision)
    if commit.outcome is not RamStateOutcome.ADMITTED:
        return _cold_scope_refusal(V1RequestReason.COLD_ADMIT_REFUSED)
    session = V1Session(namespace=namespace, owner=owner)
    try:
        bare = runtime.recovery_store.open_session(address)
    except Exception:
        return _cold_scope_refusal(V1RequestReason.COLD_PUBLISH_REFUSED)
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
    publish = session.checkpoint()
    if publish.limitation is not RecoveryStoreLimitation.OK:
        bare.close()
        table.discard(address)
        return _cold_scope_refusal(V1RequestReason.COLD_PUBLISH_REFUSED)
    session.last_publish = publish
    snapshot = owner.snapshot
    if snapshot is None:
        bare.close()
        table.discard(address)
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
    if admission.outcome is not RootRegionAdmissionOutcome.READY:
        # A genuine non-READY T is admissible state (negative
        # evidence is retained) but cannot carry a governed
        # transaction: commit the record set and publish, the
        # transaction stage forwards unchanged (no replacement).
        pass
    commit = owner.admit(transition.state, admission, namespace, expected_revision=owner.revision)
    if commit.outcome is not RamStateOutcome.ADMITTED:
        return None, V1RequestRefusal(V1RequestReason.COMMIT_REFUSED)
    publish = session.checkpoint()
    if publish.limitation is not RecoveryStoreLimitation.OK:
        return None, V1RequestRefusal(V1RequestReason.PUBLISH_REFUSED)
    session.last_publish = publish
    new_snapshot = owner.snapshot
    if new_snapshot is None:
        return None, V1RequestRefusal(V1RequestReason.COMMIT_REFUSED)
    # The retained successful pointer is bound to the exact
    # snapshot/epoch it actually published (the newer record set
    # is undurable until the bound moves over it).
    session.last_publish_bound = (new_snapshot.revision, new_snapshot.epoch)
    return PreparedGenerationProof(publish=publish, snapshot=new_snapshot), None


#: The accepted observation carrier bound (the 022-b transaction
#: default; the transaction runs over THIS payload's geometry).
_V1_MAX_TEXT_CHARS = 100_000


@dataclass(frozen=True, slots=True)
class V1TransactionResult:
    """The prepared SINGLE outgoing request of one governed v1
    transaction.

    ``body`` is the EXACT serialized bytes the one main upstream
    forward receives: the transformed payload on ``OK``, the
    unchanged original payload on ``NO_REPLACEMENT`` (no replacement
    was earned for this payload; the request forwards as received,
    with no replacement claim and no dangling reference).  The
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
        # A non-READY T is admissible state (the negative evidence
        # is retained) but establishes no replacement: the request
        # is forwarded unchanged (no replacement claim, no dangling
        # reference, no hidden raw fallback).
        return V1TransactionResult(
            outcome=ReplacementOutcome.NO_REPLACEMENT,
            body=_serialize_payload(payload),
            represented_frontier=represented_frontier(
                snapshot,
                admission=None,
                working_set=(),
                file_edits=(),
                root_observed=bool(observation.roots.roots),
            ),
        )
    admission = t.admission
    if admission is None:
        # Unreachable: the admission parent is present exactly on a
        # READY outcome; fail closed rather than guess.
        return V1RequestRefusal(V1RequestReason.COMMIT_REFUSED)
    compiled = await _compile_and_select(session, runtime, snapshot)
    if isinstance(compiled, V1RequestRefusal):
        return compiled
    ready, decision = compiled
    roots = observation.roots.roots
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
        return V1TransactionResult(
            outcome=result.outcome,
            body=_serialize_payload(result.transformed_payload),
            edits_committed=result.edits_committed,
            markers_emitted=result.markers_emitted,
            markers_replayed=result.markers_replayed,
            selected_content_keys=result.selected_content_keys,
            represented_frontier=represented_frontier(
                snapshot,
                admission=admission,
                working_set=decision.working_set,
                file_edits=result.edits,
                root_observed=bool(roots),
            ),
        )
    if result.outcome is ReplacementOutcome.NO_REPLACEMENT:
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
        commits through the ACTUAL owner admit + protected
        generation (the permitted derived metadata only -- the
        canonical fingerprint, never the raw arguments); a
        REPLAYED or refused registration changes nothing (no
        retry, no invented frontier, no upgraded evidence)."""
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
        commit = self.session.owner.admit(
            transition.state,
            admission,
            self.namespace,
            expected_revision=self.session.owner.revision,
        )
        if commit.outcome is not RamStateOutcome.ADMITTED:
            return
        publish = self.session.checkpoint()
        new_snapshot = self.session.owner.snapshot
        if publish.limitation is RecoveryStoreLimitation.OK and new_snapshot is not None:
            # The retained successful pointer is bound to the exact
            # snapshot/epoch it actually published (a faulted
            # publication keeps the prior bound: the newer record
            # set stays undurable and is refused on replay).
            self.session.last_publish = publish
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
    "represented_frontier",
    "prepare_replay_shadow",
    "prepare_v1_transaction",
]
