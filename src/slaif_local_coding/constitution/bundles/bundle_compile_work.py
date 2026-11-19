"""The actual compile-through-RAM composition (objective 021, the
compiler half of C03).

INERT component of the v1 dependency-bundle cache rework
(``docs/CACHE-TOKEN-COMPILER-CONTRACT.md``): ONE bounded
composition operation that resolves ONE actual current admitted
entry through the ACCEPTED 019-b ``RamWorkCoordinator`` work plane
(``resolve``) with the ACTUAL 021 pinned direct compiler
(``bundle_compiler``), the ACTUAL pinned tokenizer
(``bundle_tokenizer``) and a VALIDATED budget plan
(``bundle_budget``).  The injected seam is the ACTUAL
``make_entry_compile_seam`` -- no synthetic payload -- so this is
"one ACTUAL compiler leader": concurrent identical demands join the
ONE shared upstream attempt and a retained valid payload is a
RAM-only hit.

Law (objective 021 items 3-4 + plan policy 9 + accepted 018-p /
019-b / 020):

- ONE demand is ONE actual current admitted entry (018-t) with its
  deterministic candidate paths and ONE validated ``BundleBudgetPlan``.
  The budget identity AND the per-entry rendered allowance are
  DERIVED from the plan (``plan_identity`` and ``width x slot``
  over the entry's ACTUAL admitted width) -- the caller never
  supplies them independently.  The FULL compile key is re-derived
  at this boundary with the exact accepted recipe
  (``derive_compile_key``): entry identity, source digest / length,
  candidate paths, compiler config identity, tokenization identity,
  budget identity and render policy version.  Any changed
  context / tokenizer / compiler policy changes the key.
- CONFIGURED-POLICY FENCE (the B04 / C03 full-key fence at the
  claim boundary, BEFORE any work-plane claim or publication): the
  closed recipe ``derive_compile_policy_fingerprint`` joins the
  configured policy (the compiler config identity and the plan
  identity -- the plan identity already binding the budget
  configuration, the pinned tokenization identity, the render
  policy version and the model envelope version) into ONE 64-hex
  fingerprint that MUST equal the trusted namespace's
  ``config_fingerprint``.  A mismatched demand (compiler /
  tokenizer / budget policy that the namespace does not configure)
  fails with the closed typed ``POLICY_FINGERPRINT_MISMATCH``
  refusal (fixed 409, zero invocations, no work-plane claim, no
  terminal, no payload) BEFORE any claim.  A changed policy is
  therefore a genuinely distinct namespace (a distinct
  ``config_fingerprint`` -> a distinct lineage key -> a distinct
  owner), where it is a genuine miss that earns its own compile --
  never a cross-namespace reuse.
- The work plane is keyed by the entry's ACTUAL stable semantic
  content key (the accepted 019 current-key law is unchanged: a
  payload is resolvable only while that key is current on the owner
  and within the owner's live epoch).  The FULL compile key is
  verified against the EMBEDDED key of every retained payload
  BEFORE the payload may be served: a retained payload whose full
  key differs from the demand's full key (a different
  candidate-set or any identity drift) is NEVER reused -- it is the
  closed typed ``POLICY_STALE`` outcome (zero new invocations,
  nothing is discarded or recompiled inside the epoch; the needed
  rebuild happens only through a needed new epoch: an explicit
  teardown or the 020 authenticated restart / recovery, which
  allocates a strictly higher epoch on a fresh owner).
- Every serving payload (COMPLETED / JOINED / HIT) is STRICTLY
  re-validated (``deserialize_compiled_index``) and the full-key /
  content-key joins are re-run over the returned model before it is
  served.
- The closed outcome vocabulary maps the accepted work-plane
  outcomes (COMPLETED / JOINED / HIT / REFUSED / FAILED)
  one-for-one and adds ``POLICY_STALE``; the work-plane limitation,
  epoch, invocation counts and the fixed typed status are carried
  through unchanged; the composition adds its own closed
  pre-claim limitation vocabulary
  (``BundleCompileWorkLimitation``) for the policy fence and the
  allowance fence, both fixed 409.
- The single-flight law, the no-retry terminal law, the capacity
  fences and the currentness fence are the ACCEPTED 019-b laws
  exercised unchanged through the actual seam: a terminal compiler
  failure (truncated / invalid / over-budget / upstream) is
  re-served with the SAME fixed typed limitation and zero new
  invocations (no retry of any kind).
- Compiler usage is metered SEPARATELY from recovery usage: this
  composition holds ONE ``BundleCompilerAccount`` (content-free
  counts and byte totals only) passed to every seam; recovery-store
  usage remains in the 020 publication records (generation / size)
  and the two are never conflated.
- A RECOVERED owner (020 ``RecoverySessionOwner``) is composed by
  identity: the resume allocates a strictly higher epoch on a fresh
  owner with an EMPTY work plane, so after a needed restart each
  demanded key is compiled exactly once, only when demanded
  (needed-only); the durable recovery record retains the admitted
  P/T record set -- never the compiled payload (the derived cache is
  disposable).
- The component is INERT: no request-pipeline wiring, no v1 runtime
  activation, no configuration key, no model weights, no torch, no
  hosted tokenizer calls.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import Field, model_validator

from .bundle_budget import BundleBudgetError, BundleBudgetPlan
from .bundle_compiler import (
    BundleCompiledIndex,
    BundleCompiler,
    BundleCompilerAccount,
    derive_compile_key,
    deserialize_compiled_index,
    entry_source,
    make_entry_compile_seam,
)
from .bundle_tokenizer import BUNDLE_TOKENIZER_RENDER_POLICY_VERSION, BundleTokenizer
from .graph_models import _fixed, _GraphFrozen
from .ram_state import RamStateOwnerRegistry
from .ram_state_models import RamStateLimitation
from .ram_work import RamWorkCoordinator
from .ram_work_models import (
    RamWorkLimitation,
    RamWorkOutcome,
    RamWorkPayload,
)
from .root_region_admission_models import RootRegionAdmissionEntry
from .root_region_lineage_models import RootRegionLineageNamespace

BUNDLE_COMPILE_WORK_CONTRACT_VERSION = "cache-bundle-compile-work/v1"
BUNDLE_COMPILE_WORK_POLICY_VERSION = "bundle-compile-work-policy/v1"

#: The fixed typed status of the composition's closed fences (the
#: policy-fingerprint mismatch, the allowance out-of-bound and the
#: stale-policy serve fence -- a 409 conflict, never a capacity 503).
COMPILE_WORK_CONFLICT_STATUS = 409


class BundleCompileWorkOutcome(StrEnum):
    """The closed composition outcome vocabulary (021).

    ``COMPLETED`` / ``JOINED`` / ``HIT`` carry the STRICTLY
    re-validated compiled index whose embedded FULL compile key
    equals the demand's full key; ``REFUSED`` / ``FAILED`` carry
    through the accepted work-plane limitation unchanged (or the
    composition's closed pre-claim limitation); ``POLICY_STALE`` is
    the composition-only closed outcome: the retained payload was
    compiled under a different full compile key and is never reused
    (zero new invocations; the needed rebuild only happens in a
    needed new epoch)."""

    COMPLETED = "completed"
    JOINED = "joined"
    HIT = "hit"
    REFUSED = "refused"
    FAILED = "failed"
    POLICY_STALE = "policy_stale"


class BundleCompileWorkLimitation(StrEnum):
    """The closed composition pre-claim limitation vocabulary
    (021): ``POLICY_FINGERPRINT_MISMATCH`` (the demand's configured
    policy does not join the trusted namespace's
    ``config_fingerprint`` -- refused before any work-plane claim)
    and ``ALLOWANCE_OUT_OF_BOUND`` (the entry's ACTUAL admitted
    width leaves the validated plan's closed distinct-file bound).
    Both are fixed 409 conflicts: zero invocations, no attempt, no
    terminal, no payload."""

    POLICY_FINGERPRINT_MISMATCH = "policy_fingerprint_mismatch"
    ALLOWANCE_OUT_OF_BOUND = "allowance_out_of_bound"


class BundleCompileWorkResult(_GraphFrozen):
    """ONE typed composition outcome (content-free)."""

    contract_version: str = BUNDLE_COMPILE_WORK_CONTRACT_VERSION
    outcome: BundleCompileWorkOutcome
    limitation: RamWorkLimitation | RamStateLimitation | BundleCompileWorkLimitation | None = None
    compile_key: str = Field(pattern=r"^[0-9a-f]{64}$")
    index: BundleCompiledIndex | None = None
    payload: RamWorkPayload | None = None
    epoch: int = Field(ge=0)
    invocations: int = Field(ge=0, le=1)
    attempt_invocations: int = Field(ge=0, le=1)
    http_status: int | None = Field(default=None, ge=100, le=599)

    @model_validator(mode="after")
    def _v_closed_join(self) -> BundleCompileWorkResult:
        if self.outcome in (
            BundleCompileWorkOutcome.COMPLETED,
            BundleCompileWorkOutcome.JOINED,
            BundleCompileWorkOutcome.HIT,
        ):
            if self.index is None or self.payload is None:
                raise _fixed("the serving outcome requires the validated index and payload")
            if self.limitation is not None or self.http_status is not None:
                raise _fixed("the serving outcome carries no limitation or status")
        elif self.outcome is BundleCompileWorkOutcome.POLICY_STALE:
            if self.index is not None or self.payload is None:
                raise _fixed("the stale outcome carries no index and the stale payload")
            if self.limitation is not None:
                raise _fixed("the stale outcome carries no work limitation")
            if self.http_status != COMPILE_WORK_CONFLICT_STATUS:
                raise _fixed("the stale outcome carries the fixed 409 status")
        else:
            if self.index is not None or self.payload is not None:
                raise _fixed("the refusal outcome carries no index or payload")
            if self.limitation is None:
                raise _fixed("the refusal outcome requires the carried limitation")
        if self.index is not None and self.index.compile_key != self.compile_key:
            raise _fixed("the served index leaves the demand full key")
        return self


class BundleCompileWorkError(Exception):
    """A closed internal invariant failure of the composition
    (never a typed demand outcome; a retained seam-produced payload
    that fails strict re-validation is an internal invariant
    breach, never a served or silently discarded state)."""


def derive_compile_policy_fingerprint(*, config_identity: str, plan_identity: str) -> str:
    """The closed join of the configured 021 policy into the
    trusted namespace's ``config_fingerprint`` (64-hex).

    The material binds the composition contract / policy versions,
    the compiler CONFIG IDENTITY (the declared model revision plus
    the opaque upstream-compatibility identity and the closed
    compiler bound set -- the transport URL is never identity
    material) and the validated PLAN IDENTITY (the budget
    configuration, the pinned tokenization identity, the render
    policy version and the model envelope version).  A changed
    context / tokenizer / compiler / budget policy changes the
    fingerprint, and with it the namespace lineage key: the changed
    policy is a genuinely distinct namespace, never a cross-
    namespace reuse of a retained payload."""
    material = {
        "contract_version": BUNDLE_COMPILE_WORK_CONTRACT_VERSION,
        "policy_version": BUNDLE_COMPILE_WORK_POLICY_VERSION,
        "config_identity": config_identity,
        "plan_identity": plan_identity,
    }
    return hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


_SERVING_OUTCOMES = {
    RamWorkOutcome.COMPLETED: BundleCompileWorkOutcome.COMPLETED,
    RamWorkOutcome.JOINED: BundleCompileWorkOutcome.JOINED,
    RamWorkOutcome.HIT: BundleCompileWorkOutcome.HIT,
}


class BundleCompileWork:
    """ONE bounded compile-through-RAM composition (021).

    Created explicitly over a WORK-ENABLED registry and bound to
    ONE actual compiler and ONE actual pinned tokenizer (loaded
    and validated once; the hot path never reloads the assets or
    reads recovery originals).  No per-request state is retained
    beyond the separately metered compiler account."""

    __slots__ = ("_registry", "_work", "_compiler", "_tokenizer", "_account")

    def __init__(
        self,
        registry: object,
        *,
        compiler: object,
        tokenizer: object,
    ) -> None:
        if type(registry) is not RamStateOwnerRegistry:
            raise _fixed("the compile work registry must be the actual 019-a registry")
        work = registry.work
        if work is None:
            raise _fixed("the compile work registry must have the 019-b work plane enabled")
        if type(compiler) is not BundleCompiler:
            raise _fixed("the compile work compiler must be the actual 021 compiler")
        if type(tokenizer) is not BundleTokenizer:
            raise _fixed("the compile work tokenizer must be the actual 021 pinned tokenizer")
        self._registry = registry
        self._work = work
        self._compiler = compiler
        self._tokenizer = tokenizer
        self._account = BundleCompilerAccount()

    @property
    def work(self) -> RamWorkCoordinator:
        return self._work

    @property
    def account(self) -> BundleCompilerAccount:
        """The separately metered compiler usage (distinct from
        recovery usage; content-free counts and byte totals
        only)."""
        return self._account

    def full_compile_key(
        self,
        entry: RootRegionAdmissionEntry,
        candidate_paths: tuple[str, ...],
        plan: BundleBudgetPlan,
    ) -> str:
        """The demand's FULL compile key, re-derived at this
        boundary with the exact accepted recipe (the same key the
        compiler binds into one bounded attempt); the budget
        identity is the VALIDATED plan's identity."""
        if type(plan) is not BundleBudgetPlan:
            raise _fixed("the compile work demand requires the actual pinned-tokenizer plan")
        source_text, source_digest, source_byte_length = entry_source(entry)
        return derive_compile_key(
            entry_class=entry.entry_class,
            content_key=entry.content_key,
            source_sha256=source_digest,
            source_byte_length=source_byte_length,
            candidate_paths=candidate_paths,
            config_identity=self._compiler.config.config_identity,
            tokenizer_identity=self._tokenizer.binding.identity,
            budget_identity=plan.plan_identity(),
            render_policy_version=BUNDLE_TOKENIZER_RENDER_POLICY_VERSION,
        )

    async def resolve_entry(
        self,
        namespace: RootRegionLineageNamespace,
        entry: RootRegionAdmissionEntry,
        *,
        candidate_paths: tuple[str, ...],
        plan: BundleBudgetPlan,
    ) -> BundleCompileWorkResult:
        """Resolve ONE demand for ONE actual current admitted
        entry through the accepted work plane with the ACTUAL
        compile seam.

        The budget identity and the per-entry rendered allowance
        are DERIVED from the validated plan (``plan_identity`` and
        ``width x slot`` over the entry's ACTUAL admitted width).
        BEFORE any work-plane claim the configured policy is
        joined to the trusted namespace's ``config_fingerprint``:
        a mismatch fails with the closed typed
        ``POLICY_FINGERPRINT_MISMATCH`` refusal (fixed 409, zero
        invocations, no claim, no terminal, no payload).  A
        retained valid payload of the same epoch whose embedded
        full key equals the demand's full key is a RAM-only HIT
        (zero invocations); otherwise the demand claims (or joins)
        the ONE shared attempt over the direct authenticated
        tool-free upstream channel.  The outcome, limitation,
        epoch, invocation counts and fixed typed status are
        carried through the accepted work plane unchanged; a
        retained payload whose full key differs from the demand's
        full key is never reused (``POLICY_STALE``, zero
        invocations, no retry, no in-epoch rebuild)."""
        if type(plan) is not BundleBudgetPlan:
            raise _fixed("the compile work demand requires the actual pinned-tokenizer plan")
        compile_key = self.full_compile_key(entry, candidate_paths, plan)
        expected_fingerprint = derive_compile_policy_fingerprint(
            config_identity=self._compiler.config.config_identity,
            plan_identity=plan.plan_identity(),
        )
        if namespace.config_fingerprint != expected_fingerprint:
            return BundleCompileWorkResult(
                outcome=BundleCompileWorkOutcome.REFUSED,
                limitation=BundleCompileWorkLimitation.POLICY_FINGERPRINT_MISMATCH,
                compile_key=compile_key,
                epoch=0,
                invocations=0,
                attempt_invocations=0,
                http_status=COMPILE_WORK_CONFLICT_STATUS,
            )
        try:
            rendered_allowance = plan.entry_allowance(entry.width)
        except BundleBudgetError:
            return BundleCompileWorkResult(
                outcome=BundleCompileWorkOutcome.REFUSED,
                limitation=BundleCompileWorkLimitation.ALLOWANCE_OUT_OF_BOUND,
                compile_key=compile_key,
                epoch=0,
                invocations=0,
                attempt_invocations=0,
                http_status=COMPILE_WORK_CONFLICT_STATUS,
            )
        seam = make_entry_compile_seam(
            compiler=self._compiler,
            entry=entry,
            candidate_paths=candidate_paths,
            tokenizer=self._tokenizer,
            budget_identity=plan.plan_identity(),
            rendered_allowance=rendered_allowance,
            account=self._account,
        )
        work_result = await self._work.resolve(namespace, entry.content_key, seam)
        if work_result.outcome in (RamWorkOutcome.REFUSED, RamWorkOutcome.FAILED):
            return BundleCompileWorkResult(
                outcome=(
                    BundleCompileWorkOutcome.REFUSED
                    if work_result.outcome is RamWorkOutcome.REFUSED
                    else BundleCompileWorkOutcome.FAILED
                ),
                limitation=work_result.limitation,
                compile_key=compile_key,
                epoch=work_result.epoch,
                invocations=work_result.invocations,
                attempt_invocations=work_result.attempt_invocations,
                http_status=work_result.http_status,
            )
        serving = _SERVING_OUTCOMES.get(work_result.outcome)
        if serving is None:
            raise BundleCompileWorkError(
                "the work plane returned an outcome the composition cannot serve"
            )
        if work_result.payload is None:
            raise BundleCompileWorkError(
                "the work plane returned a serving outcome without the retained payload"
            )
        try:
            index = deserialize_compiled_index(
                work_result.payload.data,
                max_json_depth=self._compiler.config.max_json_depth,
            )
        except ValueError:
            raise BundleCompileWorkError(
                "the retained compiler payload failed strict re-validation"
            ) from None
        if index.compile_key != compile_key or index.content_key != entry.content_key:
            # The retained payload's FULL key differs from the
            # demand's full key (a different deterministic
            # candidate set or identity drift): never reused.
            # Zero invocations were consumed; the payload stays
            # retained for the epoch; the needed rebuild only
            # happens in a needed new epoch.
            return BundleCompileWorkResult(
                outcome=BundleCompileWorkOutcome.POLICY_STALE,
                limitation=None,
                compile_key=compile_key,
                index=None,
                payload=work_result.payload,
                epoch=work_result.epoch,
                invocations=work_result.invocations,
                attempt_invocations=work_result.attempt_invocations,
                http_status=COMPILE_WORK_CONFLICT_STATUS,
            )
        return BundleCompileWorkResult(
            outcome=serving,
            limitation=None,
            compile_key=compile_key,
            index=index,
            payload=work_result.payload,
            epoch=work_result.epoch,
            invocations=work_result.invocations,
            attempt_invocations=work_result.attempt_invocations,
            http_status=None,
        )
