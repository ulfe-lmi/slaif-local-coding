"""021 compile-through-RAM composition: the ACTUAL compiler
single-flight over the accepted 019-b work plane (contract
``docs/CACHE-TOKEN-COMPILER-CONTRACT.md``; the compiler half of
C03).

SAVED FIRST INCREMENT: ONE demand for ONE actual current admitted
key resolves through the existing ``RamWorkCoordinator.resolve``
with the bound compiler, the VALIDATED plan-derived identity and
rendered allowance, and the ACTUAL compile seam: the completed
demand, the RAM-only same-key hit, the ONE ACTUAL compiler leader
over concurrent identical misses, the no-retry terminal re-serve
over the actual compiler failures, the configured-policy fence
(a mismatched demand is refused BEFORE any work-plane claim or
publication; a changed policy is a genuinely distinct namespace
that earns its own genuine miss), the compatible-revert reuse of
the retained payload without a third call, and the recovery-owner
extension: the needed-only epoch rebuild over the EXISTING 020
``RecoverySessionOwner`` (the resume compiles nothing, the
checkpoint publishes the admitted P/T record set -- never the
compiled payload -- and the second resume's strictly higher
epoch rebuilds a demanded key exactly once, only when demanded).

The stage stays inert: no adapter wiring, no configuration key,
no v1 runtime activation.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
    make_bundle_admission_namespace,
)
from slaif_local_coding.constitution.bundles.bundle_budget import (
    BundleBudgetConfig,
    BundleBudgetPlan,
)
from slaif_local_coding.constitution.bundles.bundle_compile_work import (
    BundleCompileWork,
    BundleCompileWorkLimitation,
    BundleCompileWorkOutcome,
    derive_compile_policy_fingerprint,
)
from slaif_local_coding.constitution.bundles.bundle_compiler import (
    BundleCompiler,
)
from slaif_local_coding.constitution.bundles.bundle_tokenizer import (
    get_bundle_tokenizer,
)
from slaif_local_coding.constitution.bundles.ram_state import RamStateOwnerRegistry
from slaif_local_coding.constitution.bundles.ram_state_models import (
    RamStateLimitation,
    RamStateOutcome,
)
from slaif_local_coding.constitution.bundles.ram_work_models import (
    RamWorkLimitation,
)
from slaif_local_coding.constitution.bundles.recovery_models import (
    RecoveryRecord,
    RecoverySessionAddress,
    recovery_record_payload_bytes,
)
from slaif_local_coding.constitution.bundles.recovery_resume import (
    RecoveryResumeOutcome,
    RecoveryTeardownOutcome,
    resume_session,
)
from slaif_local_coding.constitution.bundles.recovery_store import (
    RecoveryStore,
    RecoveryStoreLimitation,
)
from slaif_local_coding.constitution.bundles.root_lineage_models import (
    RootLineageOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_admission import (
    derive_root_region_admission,
)
from slaif_local_coding.constitution.bundles.root_region_admission_result_models import (
    RootRegionAdmissionOutcome,
)
from slaif_local_coding.constitution.bundles.root_region_lineage import (
    bootstrap_root_region_lineage,
)
from slaif_local_coding.constitution.bundles.root_region_lineage_models import (
    make_root_region_lineage_namespace,
)
from tests.test_bundle_compiler import (
    A_BODY,
    COMPILER_KEY_ENV,
    COMPILER_KEY_VALUE,
    ROOT_BODY,
    _completion_bytes,
    _config,
    _dep_read,
    _entry_for,
    _valid_payload,
)
from tests.test_bundle_ram_state import ROOT_AB
from tests.test_bundle_ram_work import _genuine_a1_revert, _genuine_a2, _until, _work_registry
from tests.test_bundle_recovery_store import _prepared_root
from tests.test_causal_history import (
    ENDPOINTS,
    FINGERPRINT,
    IDENTITY,
    MODES,
    WORKSPACE,
)
from tests.test_root_lineage import rooted
from tests.test_root_region_lineage import A_TEXT, B_TEXT

CONTEXT_LARGE = 262_144
CONTEXT_SMALL = 32_768


def _policy_ns(mode: AdmissionMode, lineage: str, fingerprint: str) -> Any:
    """A root-region scope whose ``config_fingerprint`` is the
    given (actual 021 recipe) fingerprint, built through the
    genuine accepted D / P scope factories."""
    admission = make_bundle_admission_namespace(
        IDENTITY,
        model_identity="synthetic-history-model",
        config_fingerprint=fingerprint,
        workspace=WORKSPACE,
        mode=mode,
    )
    return make_root_region_lineage_namespace(admission, lineage)


def _policy_states(
    mode: AdmissionMode,
    endpoint: str,
    lineage: str,
    fingerprint: str,
    root_body: str,
) -> tuple[Any, Any, Any]:
    """Genuine bootstrap plus one A.md read under the
    policy-bound scope: (ns, state, READY result)."""
    ns = _policy_ns(mode, lineage, fingerprint)
    t0 = bootstrap_root_region_lineage((rooted(root_body),), ns)
    assert t0.outcome is RootLineageOutcome.ACCEPTED, t0.diagnostics
    state = _dep_read(t0.state, ns, "a", endpoint, "A.md", A_BODY)
    t = derive_root_region_admission(state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    return ns, state, t


def _upstream_handler(
    payloads: dict[str, bytes], calls: list[int], gate: asyncio.Event | None = None
) -> Any:
    """The fake direct upstream: matches the demand by the FULL
    compile key embedded in the identity-bound prompt (the
    compiler's exact request law), counts every call, and holds
    the leader in flight behind the optional deterministic gate."""

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        if gate is not None:
            await gate.wait()
        body = json.loads(request.content)
        user = body["messages"][1]["content"]
        for compile_key, payload in payloads.items():
            if f"compile_key={compile_key!r}" in user:
                return httpx.Response(200, content=payload)
        raise AssertionError("the fake upstream received an unknown demand")

    return handler


def _make_plane(
    registry: Any, config: Any, tokenizer: Any, client: httpx.AsyncClient
) -> BundleCompileWork:
    return BundleCompileWork(
        registry, compiler=BundleCompiler(config, client=client), tokenizer=tokenizer
    )


@pytest.mark.parametrize("mode", MODES)
async def test_single_key_completed_then_ram_hit(
    mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch
) -> None:
    """ONE actual current admitted key through the ACTUAL work
    plane and the ACTUAL compile seam: the completed demand (one
    upstream call, the validated index bound to the demand full
    key), the RAM-only same-key hit (zero new invocations, the
    SAME retained payload) and the separately metered compiler
    account."""
    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    config = _config()
    tokenizer = get_bundle_tokenizer()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=CONTEXT_LARGE))
    fingerprint = derive_compile_policy_fingerprint(
        config_identity=config.config_identity, plan_identity=plan.plan_identity()
    )
    ns, state, t = _policy_states(
        mode, ENDPOINTS[0], f"cw021-t1-{mode.value}", fingerprint, ROOT_BODY
    )
    entry = _entry_for(t, "A.md")
    assert entry.content_key != t.admission.root_entry.content_key
    registry = _work_registry()
    owner = registry.acquire(ns)
    assert owner.admit(state, t, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    calls: list[int] = []
    payloads: dict[str, bytes] = {}
    client = httpx.AsyncClient(transport=httpx.MockTransport(_upstream_handler(payloads, calls)))
    plane = _make_plane(registry, config, tokenizer, client)
    payloads[plane.full_compile_key(entry, (), plan)] = _valid_payload(
        entry=entry, candidates=(), config=config, tokenizer=tokenizer, plan=plan
    )
    try:
        r1 = await plane.resolve_entry(ns, entry, candidate_paths=(), plan=plan)
        assert r1.outcome is BundleCompileWorkOutcome.COMPLETED, r1
        assert r1.invocations == 1
        assert r1.attempt_invocations == 1
        assert r1.index is not None
        assert r1.index.compile_key == plane.full_compile_key(entry, (), plan)
        assert r1.payload is not None
        assert r1.epoch == owner.epoch
        assert r1.http_status is None
        assert len(calls) == 1
        # The SAME full key on the unchanged compatible content:
        # RAM-only hit, zero new invocations, the same payload.
        r2 = await plane.resolve_entry(ns, entry, candidate_paths=(), plan=plan)
        assert r2.outcome is BundleCompileWorkOutcome.HIT, r2
        assert r2.invocations == 0
        assert r2.payload is r1.payload
        assert r2.index is not None
        assert r2.index == r1.index
        assert len(calls) == 1
    finally:
        await client.aclose()
    # The separately metered compiler usage (never conflated with
    # recovery usage).
    assert plane.account.upstream_calls == 1
    assert plane.account.outcome_counts == {"completed": 1}


@pytest.mark.parametrize("mode", MODES)
async def test_concurrent_identical_miss_one_leader(
    mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Simultaneous identical misses over the ACTUAL compiler
    seam: ONE process-wide leader (one ACTUAL upstream call), the
    joining demand re-served the SHARED attempt with zero own
    invocations (JOINED), the SAME retained payload to both, and
    the later same-key demand a RAM-only hit."""
    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    config = _config()
    tokenizer = get_bundle_tokenizer()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=CONTEXT_LARGE))
    fingerprint = derive_compile_policy_fingerprint(
        config_identity=config.config_identity, plan_identity=plan.plan_identity()
    )
    ns, state, t = _policy_states(
        mode, ENDPOINTS[0], f"cw021-t2-{mode.value}", fingerprint, ROOT_BODY
    )
    entry = _entry_for(t, "A.md")
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns)
    assert owner.admit(state, t, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    okey = owner.namespace.lineage_key
    calls: list[int] = []
    gate = asyncio.Event()
    payloads: dict[str, bytes] = {}
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(_upstream_handler(payloads, calls, gate=gate))
    )
    plane = _make_plane(registry, config, tokenizer, client)
    payloads[plane.full_compile_key(entry, (), plan)] = _valid_payload(
        entry=entry, candidates=(), config=config, tokenizer=tokenizer, plan=plan
    )
    try:
        first = asyncio.create_task(plane.resolve_entry(ns, entry, candidate_paths=(), plan=plan))
        await _until(lambda: len(calls) == 1)  # the leader is in flight
        second = asyncio.create_task(plane.resolve_entry(ns, entry, candidate_paths=(), plan=plan))
        await _until(
            lambda: len(work._owners[okey].live[entry.content_key].waiters) == 2
        )  # the follower joined the ONE shared attempt
        gate.set()
        r1 = await first
        r2 = await second
        assert r1.outcome is BundleCompileWorkOutcome.COMPLETED, r1
        assert r1.invocations == 1
        assert r2.outcome is BundleCompileWorkOutcome.JOINED, r2
        assert r2.invocations == 0
        assert r2.attempt_invocations == 1
        assert r2.payload is r1.payload
        assert r2.index is not None
        assert r2.index == r1.index
        assert len(calls) == 1
        r3 = await plane.resolve_entry(ns, entry, candidate_paths=(), plan=plan)
        assert r3.outcome is BundleCompileWorkOutcome.HIT, r3
        assert r3.invocations == 0
        assert r3.payload is r1.payload
        assert len(calls) == 1
    finally:
        await client.aclose()
    assert plane.account.upstream_calls == 1


@pytest.mark.parametrize("mode", MODES)
async def test_terminal_failure_reserved_no_retry(
    mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The actual compiler terminal failures over the work plane:
    an INVALID output and a provider-TRUNCATED output each become
    the SAME fixed typed limitation re-served to a later same-key
    demand with ZERO new invocations (the 019 no-retry attempt
    law through the ACTUAL seam; no retry of any kind)."""
    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    config = _config()
    tokenizer = get_bundle_tokenizer()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=CONTEXT_LARGE))
    fingerprint = derive_compile_policy_fingerprint(
        config_identity=config.config_identity, plan_identity=plan.plan_identity()
    )
    ns, state, t = _policy_states(
        mode, ENDPOINTS[0], f"cw021-t3-{mode.value}", fingerprint, ROOT_BODY
    )
    file_entry = _entry_for(t, "A.md")
    root_entry = t.admission.root_entry
    registry = _work_registry()
    owner = registry.acquire(ns)
    assert owner.admit(state, t, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    calls: list[int] = []
    payloads: dict[str, bytes] = {}
    client = httpx.AsyncClient(transport=httpx.MockTransport(_upstream_handler(payloads, calls)))
    plane = _make_plane(registry, config, tokenizer, client)
    # The file demand's canned output is not strict JSON; the
    # root demand is provider-truncated (finish_reason=length).
    payloads[plane.full_compile_key(file_entry, (), plan)] = _completion_bytes("not json")
    payloads[plane.full_compile_key(root_entry, ("A.md",), plan)] = _completion_bytes(
        "{}", finish_reason="length"
    )
    try:
        r1 = await plane.resolve_entry(ns, file_entry, candidate_paths=(), plan=plan)
        assert r1.outcome is BundleCompileWorkOutcome.FAILED, r1
        assert r1.limitation is RamWorkLimitation.INVALID_OUTPUT
        assert r1.http_status == 422
        assert r1.invocations == 1
        assert len(calls) == 1
        r2 = await plane.resolve_entry(ns, file_entry, candidate_paths=(), plan=plan)
        assert r2.outcome is BundleCompileWorkOutcome.FAILED, r2
        assert r2.limitation is RamWorkLimitation.INVALID_OUTPUT
        assert r2.http_status == 422
        assert r2.invocations == 0
        assert len(calls) == 1
        # The distinct root key earns its OWN terminal (truncated
        # BEFORE any content validation).
        r3 = await plane.resolve_entry(ns, root_entry, candidate_paths=("A.md",), plan=plan)
        assert r3.outcome is BundleCompileWorkOutcome.FAILED, r3
        assert r3.limitation is RamWorkLimitation.TRUNCATED_OUTPUT
        assert r3.invocations == 1
        assert len(calls) == 2
        r4 = await plane.resolve_entry(ns, root_entry, candidate_paths=("A.md",), plan=plan)
        assert r4.outcome is BundleCompileWorkOutcome.FAILED, r4
        assert r4.limitation is RamWorkLimitation.TRUNCATED_OUTPUT
        assert r4.invocations == 0
        assert len(calls) == 2
    finally:
        await client.aclose()
    assert plane.account.upstream_calls == 2
    assert plane.account.outcome_counts == {"invalid_json": 1, "output_truncated": 1}


@pytest.mark.parametrize("mode", MODES)
async def test_changed_policy_distinct_namespace_genuine_miss(
    mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The B04 / C03 full-key fence: the SAME content under a
    changed context policy keeps the SAME stable semantic content
    key but the configured policy changes the namespace
    fingerprint -- a genuinely DISTINCT namespace (a distinct
    lineage key, a distinct owner) where the demand is a genuine
    miss earning its OWN compile (distinct full key, distinct
    payload).  The mismatched demand (the other policy against
    this namespace) is refused BEFORE any claim."""
    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    config = _config()
    tokenizer = get_bundle_tokenizer()
    plan_a = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=CONTEXT_LARGE))
    plan_b = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=CONTEXT_SMALL))
    fingerprint_a = derive_compile_policy_fingerprint(
        config_identity=config.config_identity, plan_identity=plan_a.plan_identity()
    )
    fingerprint_b = derive_compile_policy_fingerprint(
        config_identity=config.config_identity, plan_identity=plan_b.plan_identity()
    )
    assert fingerprint_a != fingerprint_b
    ns_a, state_a, t_a = _policy_states(
        mode, ENDPOINTS[0], f"cw021-t4a-{mode.value}", fingerprint_a, ROOT_BODY
    )
    ns_b, state_b, t_b = _policy_states(
        mode, ENDPOINTS[0], f"cw021-t4b-{mode.value}", fingerprint_b, ROOT_BODY
    )
    assert ns_a.lineage_key != ns_b.lineage_key
    entry_a = _entry_for(t_a, "A.md")
    entry_b = _entry_for(t_b, "A.md")
    # The canonical semantic content key is SCOPED to the trusted
    # namespace (the accepted 018-c / S01 isolation law): the
    # changed policy is a distinct namespace with a distinct key
    # space, so the same content carries distinct keys here and
    # no retained payload can ever cross the namespace boundary.
    assert entry_a.content_key != entry_b.content_key
    registry = _work_registry()
    owner_a = registry.acquire(ns_a)
    owner_b = registry.acquire(ns_b)
    assert (
        owner_a.admit(state_a, t_a, ns_a, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    )
    assert (
        owner_b.admit(state_b, t_b, ns_b, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    )
    calls: list[int] = []
    payloads: dict[str, bytes] = {}
    client = httpx.AsyncClient(transport=httpx.MockTransport(_upstream_handler(payloads, calls)))
    plane = _make_plane(registry, config, tokenizer, client)
    key_a = plane.full_compile_key(entry_a, (), plan_a)
    key_b = plane.full_compile_key(entry_b, (), plan_b)
    assert key_a != key_b
    payloads[key_a] = _valid_payload(
        entry=entry_a, candidates=(), config=config, tokenizer=tokenizer, plan=plan_a
    )
    payloads[key_b] = _valid_payload(
        entry=entry_b, candidates=(), config=config, tokenizer=tokenizer, plan=plan_b
    )
    try:
        r_a = await plane.resolve_entry(ns_a, entry_a, candidate_paths=(), plan=plan_a)
        assert r_a.outcome is BundleCompileWorkOutcome.COMPLETED, r_a
        assert r_a.invocations == 1
        assert len(calls) == 1
        # The changed policy is a genuine miss in its own
        # namespace: one more ACTUAL upstream call, its own
        # retained payload (distinct full key).
        r_b = await plane.resolve_entry(ns_b, entry_b, candidate_paths=(), plan=plan_b)
        assert r_b.outcome is BundleCompileWorkOutcome.COMPLETED, r_b
        assert r_b.invocations == 1
        assert len(calls) == 2
        assert r_b.payload is not None
        assert r_a.payload is not None
        assert r_b.payload.data != r_a.payload.data
        assert r_b.index is not None
        assert r_a.index is not None
        assert r_b.index.compile_key != r_a.index.compile_key
        # Same-key reuse holds within each namespace under its
        # own configured policy.
        hit_a = await plane.resolve_entry(ns_a, entry_a, candidate_paths=(), plan=plan_a)
        assert hit_a.outcome is BundleCompileWorkOutcome.HIT, hit_a
        assert hit_a.payload is r_a.payload
        assert len(calls) == 2
        # The MISMATCHED demand (the other configured policy
        # against this namespace) fails BEFORE any claim.
        bad_a = await plane.resolve_entry(ns_a, entry_a, candidate_paths=(), plan=plan_b)
        assert bad_a.outcome is BundleCompileWorkOutcome.REFUSED, bad_a
        assert bad_a.limitation is BundleCompileWorkLimitation.POLICY_FINGERPRINT_MISMATCH
        assert bad_a.http_status == 409
        assert bad_a.invocations == 0
        assert bad_a.index is None
        assert bad_a.payload is None
        assert len(calls) == 2
        bad_b = await plane.resolve_entry(ns_b, entry_b, candidate_paths=(), plan=plan_a)
        assert bad_b.outcome is BundleCompileWorkOutcome.REFUSED, bad_b
        assert bad_b.limitation is BundleCompileWorkLimitation.POLICY_FINGERPRINT_MISMATCH
        assert len(calls) == 2
    finally:
        await client.aclose()
    assert plane.account.upstream_calls == 2


@pytest.mark.parametrize("mode", MODES)
async def test_mismatched_demand_refused_before_claim(
    mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A demand whose configured policy does not join the
    namespace fingerprint fails BEFORE any work-plane claim:
    zero invocations, no work state, no terminal, no payload, no
    upstream call -- even though the owner and the current key
    exist.  A matching-policy demand against a namespace with no
    live owner still reaches the accepted work-plane fence
    (OWNER_ABSENT) unchanged."""
    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    config = _config()
    tokenizer = get_bundle_tokenizer()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=CONTEXT_LARGE))
    fingerprint = derive_compile_policy_fingerprint(
        config_identity=config.config_identity, plan_identity=plan.plan_identity()
    )
    # A namespace configured with a NON-021 opaque fingerprint
    # (the accepted 018 fixture fingerprint): no 021 policy is
    # configured for it.
    ns_plain, state_plain, t_plain = _policy_states(
        mode,
        ENDPOINTS[0],
        f"cw021-t5p-{mode.value}",
        FINGERPRINT,
        ROOT_BODY,
    )
    entry_plain = _entry_for(t_plain, "A.md")
    # A policy-bound namespace that is NEVER acquired (no owner).
    ns_bound, _state_bound, t_bound = _policy_states(
        mode,
        ENDPOINTS[0],
        f"cw021-t5b-{mode.value}",
        fingerprint,
        ROOT_BODY,
    )
    entry_bound = _entry_for(t_bound, "A.md")
    registry = _work_registry()
    work = registry.work
    assert work is not None
    owner = registry.acquire(ns_plain)
    assert (
        owner.admit(state_plain, t_plain, ns_plain, expected_revision=0).outcome
        is RamStateOutcome.ADMITTED
    )
    assert owner.lookup(entry_plain.content_key, ns_plain).outcome is RamStateOutcome.FOUND
    calls: list[int] = []
    payloads: dict[str, bytes] = {}
    client = httpx.AsyncClient(transport=httpx.MockTransport(_upstream_handler(payloads, calls)))
    plane = _make_plane(registry, config, tokenizer, client)
    payloads[plane.full_compile_key(entry_plain, (), plan)] = _valid_payload(
        entry=entry_plain, candidates=(), config=config, tokenizer=tokenizer, plan=plan
    )
    try:
        r = await plane.resolve_entry(ns_plain, entry_plain, candidate_paths=(), plan=plan)
        assert r.outcome is BundleCompileWorkOutcome.REFUSED, r
        assert r.limitation is BundleCompileWorkLimitation.POLICY_FINGERPRINT_MISMATCH
        assert r.http_status == 409
        assert r.invocations == 0
        assert r.attempt_invocations == 0
        assert r.epoch == 0
        assert r.index is None
        assert r.payload is None
        # BEFORE-CLAIM: no work state, no terminal, no upstream
        # call (a claim would have created the owner work state
        # and consumed exactly one invocation).
        assert len(calls) == 0
        assert work._owners.get(ns_plain.lineage_key) is None
        assert plane.account.upstream_calls == 0
        # The matching-policy demand against a namespace with no
        # live owner carries the accepted work-plane fence
        # through unchanged.
        r2 = await plane.resolve_entry(ns_bound, entry_bound, candidate_paths=(), plan=plan)
        assert r2.outcome is BundleCompileWorkOutcome.REFUSED, r2
        assert r2.limitation is RamWorkLimitation.OWNER_ABSENT
        assert r2.http_status == 409
        assert r2.invocations == 0
        assert len(calls) == 0
    finally:
        await client.aclose()


@pytest.mark.parametrize("mode", MODES)
async def test_compatible_revert_reuses_retained_payload(
    mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The compatible revert through the ACTUAL compiler seam:
    valid A1 (one call) -> A2 supersession (its own genuine
    call) -> an OLD retained P state replayed after A2 cannot
    reactivate A1 (lineage-rollback fence, the stale key
    pre-claim refused) -> the genuinely new old-bytes A1 revert
    reuses the RETAINED A1 payload as a RAM-only HIT -- exactly
    TWO upstream calls total, no third (the 019 same-key/epoch
    law and the 020 no-replay law over the actual seam)."""
    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    config = _config()
    tokenizer = get_bundle_tokenizer()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=CONTEXT_LARGE))
    fingerprint = derive_compile_policy_fingerprint(
        config_identity=config.config_identity, plan_identity=plan.plan_identity()
    )
    endpoint = ENDPOINTS[0]
    ns = _policy_ns(mode, f"cw021-t6-{mode.value}", fingerprint)
    # Genuine P/T chain derived PURELY first (the admits are
    # interleaved around the actual compiles): bootstrap (the
    # root declares A.md and B.md), A1, A2, the genuine A1
    # revert.
    t_boot = bootstrap_root_region_lineage((rooted(ROOT_AB),), ns)
    assert t_boot.outcome is RootLineageOutcome.ACCEPTED, t_boot.diagnostics
    s0 = t_boot.state
    result0 = derive_root_region_admission(s0, ns)
    assert result0.outcome is RootRegionAdmissionOutcome.READY, result0.diagnostics
    # The A read uses the shared helpers' ``b1`` call id (the
    # genuine A2 / A1-revert derivations descend from it).
    s1 = _dep_read(s0, ns, "b1", endpoint, "A.md", A_TEXT)
    result1 = derive_root_region_admission(s1, ns)
    assert result1.outcome is RootRegionAdmissionOutcome.READY, result1.diagnostics
    entry_a1 = _entry_for(result1, "A.md")
    key_a = entry_a1.content_key
    s2, result2, key_a2 = _genuine_a2(s1, ns, endpoint)
    assert key_a2 != key_a
    entry_a2 = _entry_for(result2, "A.md")
    s3, result3, key_revert = _genuine_a1_revert(s2, ns, endpoint)
    assert key_revert == key_a
    registry = _work_registry()
    owner = registry.acquire(ns)
    calls: list[int] = []
    payloads: dict[str, bytes] = {}
    client = httpx.AsyncClient(transport=httpx.MockTransport(_upstream_handler(payloads, calls)))
    plane = _make_plane(registry, config, tokenizer, client)
    payloads[plane.full_compile_key(entry_a1, (), plan)] = _valid_payload(
        entry=entry_a1, candidates=(), config=config, tokenizer=tokenizer, plan=plan
    )
    payloads[plane.full_compile_key(entry_a2, (), plan)] = _valid_payload(
        entry=entry_a2, candidates=(), config=config, tokenizer=tokenizer, plan=plan
    )
    try:
        assert owner.admit(s0, result0, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
        assert owner.admit(s1, result1, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED
        r1 = await plane.resolve_entry(ns, entry_a1, candidate_paths=(), plan=plan)
        assert r1.outcome is BundleCompileWorkOutcome.COMPLETED, r1
        assert r1.invocations == 1
        assert r1.payload is not None
        assert len(calls) == 1
        # Genuine A2 supersession: A1's key ceases to be current
        # but the retained A1 payload survives.
        assert owner.admit(s2, result2, ns, expected_revision=2).outcome is RamStateOutcome.ADMITTED
        r2 = await plane.resolve_entry(ns, entry_a2, candidate_paths=(), plan=plan)
        assert r2.outcome is BundleCompileWorkOutcome.COMPLETED, r2
        assert r2.invocations == 1
        assert r2.payload is not None
        assert len(calls) == 2
        # An OLD retained P state replayed AFTER A2 is the
        # lineage-rollback fence: it re-commits nothing and
        # cannot reactivate A1.
        replay = owner.admit(s1, result1, ns, expected_revision=3)
        assert replay.outcome is RamStateOutcome.REFUSED
        assert replay.limitation is RamStateLimitation.STALE_STATE_REVISION
        assert replay.revision == 3
        r_stale = await plane.resolve_entry(ns, entry_a1, candidate_paths=(), plan=plan)
        assert r_stale.outcome is BundleCompileWorkOutcome.REFUSED, r_stale
        assert r_stale.limitation is RamWorkLimitation.KEY_NOT_CURRENT
        assert r_stale.invocations == 0
        assert len(calls) == 2
        # The genuine old-bytes A1 revert: the A1 canonical key is
        # current again and the RETAINED payload is reused -- no
        # third call.
        assert owner.admit(s3, result3, ns, expected_revision=3).outcome is RamStateOutcome.ADMITTED
        r_hit = await plane.resolve_entry(ns, entry_a1, candidate_paths=(), plan=plan)
        assert r_hit.outcome is BundleCompileWorkOutcome.HIT, r_hit
        assert r_hit.payload is r1.payload
        assert r_hit.invocations == 0
        assert len(calls) == 2
    finally:
        await client.aclose()
    assert plane.account.upstream_calls == 2
    assert plane.account.outcome_counts == {"completed": 2}


@pytest.mark.parametrize("mode", MODES)
async def test_cancelled_compiler_demand_ends_without_payload_or_retry(
    mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch
) -> None:
    """ACTUAL compiler cancellation through the ACTUAL work
    adapter: the fake upstream holds the ONE in-flight demand
    behind the deterministic gate; the ONLY resolve waiter is
    cancelled; the operation ends with the typed CANCELLED
    terminal -- NO valid payload is retained and NO subsequent
    retry occurs: the later same-key demand re-serves the typed
    failure (zero new invocations, the fixed
    ALL_WAITERS_DEPARTED limitation) without re-running the
    compiler, and the separately metered compiler account counts
    the ONE dispatched call and its CANCELLED outcome separately --
    compared against the ONE actual request the fake upstream
    received -- retaining no payload and claiming no unreturned
    provider output."""
    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    config = _config()
    tokenizer = get_bundle_tokenizer()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=CONTEXT_LARGE))
    fingerprint = derive_compile_policy_fingerprint(
        config_identity=config.config_identity, plan_identity=plan.plan_identity()
    )
    ns, state, t = _policy_states(
        mode, ENDPOINTS[0], f"cw021-t9-{mode.value}", fingerprint, ROOT_BODY
    )
    entry = _entry_for(t, "A.md")
    registry = _work_registry()
    owner = registry.acquire(ns)
    assert owner.admit(state, t, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    calls: list[int] = []
    gate = asyncio.Event()
    payloads: dict[str, bytes] = {}
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(_upstream_handler(payloads, calls, gate=gate))
    )
    plane = _make_plane(registry, config, tokenizer, client)
    payloads[plane.full_compile_key(entry, (), plan)] = _valid_payload(
        entry=entry, candidates=(), config=config, tokenizer=tokenizer, plan=plan
    )
    try:
        demand = asyncio.create_task(plane.resolve_entry(ns, entry, candidate_paths=(), plan=plan))
        await _until(lambda: len(calls) == 1)  # the ONE leader in flight, held
        demand.cancel()
        with pytest.raises(asyncio.CancelledError):
            await demand
        assert len(calls) == 1  # the attempt ran exactly once; never again
        # No valid payload, no retry: the SAME key re-serves the
        # typed CANCELLED terminal -- zero new invocations, the
        # fixed ALL_WAITERS_DEPARTED limitation, no payload.
        r2 = await plane.resolve_entry(ns, entry, candidate_paths=(), plan=plan)
        assert r2.outcome is BundleCompileWorkOutcome.FAILED, r2
        assert r2.limitation is RamWorkLimitation.ALL_WAITERS_DEPARTED
        assert r2.invocations == 0
        assert r2.payload is None
        assert r2.index is None
        assert len(calls) == 1
        # Ordered accounting: the separately metered compiler
        # account counts the ONE dispatched call and its CANCELLED
        # outcome separately -- compared against the ONE actual
        # request the fake upstream received -- with no payload and
        # no unreturned provider output claimed.
        assert plane.account.upstream_calls == len(calls) == 1
        assert plane.account.outcome_counts == {"cancelled": 1}
        assert plane.account.prompt_bytes > 0
        assert plane.account.output_bytes == 0
    finally:
        gate.set()
        await client.aclose()


@pytest.mark.parametrize("mode", MODES)
async def test_unrelated_b_admission_and_equivalent_read_keep_a_hit(
    mode: AdmissionMode, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The SAME FULL KEY hits on unchanged compatible content
    through the accepted P/T and the ACTUAL work adapter: an
    UNRELATED B admission (its own independent file read) and a
    PROVEN EQUIVALENT supported read (a genuinely new read of
    A's UNCHANGED content) leave A's full compile key
    unchanged -- the retained A payload is a RAM-only HIT both
    times (zero new invocations, the SAME retained payload),
    while B compiles exactly once on its own demand.  A changed
    context / tokenizer / compiler policy is a genuinely
    distinct namespace that does NOT reuse (the policy-fence
    case); unchanged compatible content DOES."""
    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    config = _config()
    tokenizer = get_bundle_tokenizer()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=CONTEXT_LARGE))
    fingerprint = derive_compile_policy_fingerprint(
        config_identity=config.config_identity, plan_identity=plan.plan_identity()
    )
    endpoint = ENDPOINTS[0]
    ns = _policy_ns(mode, f"cw021-t8-{mode.value}", fingerprint)
    t_boot = bootstrap_root_region_lineage((rooted(ROOT_AB),), ns)
    assert t_boot.outcome is RootLineageOutcome.ACCEPTED, t_boot.diagnostics
    # A's genuine first read, admitted (the demanded key).
    s1 = _dep_read(t_boot.state, ns, "a1", endpoint, "A.md", A_TEXT)
    t1 = derive_root_region_admission(s1, ns)
    assert t1.outcome is RootRegionAdmissionOutcome.READY, t1.diagnostics
    entry_a = _entry_for(t1, "A.md")
    registry = _work_registry()
    owner = registry.acquire(ns)
    assert owner.admit(s1, t1, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    calls: list[int] = []
    payloads: dict[str, bytes] = {}
    client = httpx.AsyncClient(transport=httpx.MockTransport(_upstream_handler(payloads, calls)))
    plane = _make_plane(registry, config, tokenizer, client)
    key_a = plane.full_compile_key(entry_a, (), plan)
    payloads[key_a] = _valid_payload(
        entry=entry_a, candidates=(), config=config, tokenizer=tokenizer, plan=plan
    )
    try:
        r1 = await plane.resolve_entry(ns, entry_a, candidate_paths=(), plan=plan)
        assert r1.outcome is BundleCompileWorkOutcome.COMPLETED, r1
        assert r1.invocations == 1
        assert r1.payload is not None
        assert len(calls) == 1
        # The UNRELATED B admission: its own independent file
        # read (a distinct content key).
        s2 = _dep_read(s1, ns, "b1", endpoint, "B.md", B_TEXT)
        t2 = derive_root_region_admission(s2, ns)
        assert t2.outcome is RootRegionAdmissionOutcome.READY, t2.diagnostics
        entry_b = _entry_for(t2, "B.md")
        assert entry_b.content_key != entry_a.content_key
        assert owner.admit(s2, t2, ns, expected_revision=1).outcome is RamStateOutcome.ADMITTED
        # A's full key is UNCHANGED by the unrelated B admission:
        # the retained A payload is a RAM-only HIT, zero new
        # invocations.
        assert plane.full_compile_key(entry_a, (), plan) == key_a
        r_a = await plane.resolve_entry(ns, entry_a, candidate_paths=(), plan=plan)
        assert r_a.outcome is BundleCompileWorkOutcome.HIT, r_a
        assert r_a.invocations == 0
        assert r_a.payload is r1.payload
        assert len(calls) == 1
        # B compiles exactly once on its own demand.
        key_b = plane.full_compile_key(entry_b, (), plan)
        payloads[key_b] = _valid_payload(
            entry=entry_b, candidates=(), config=config, tokenizer=tokenizer, plan=plan
        )
        r_b = await plane.resolve_entry(ns, entry_b, candidate_paths=(), plan=plan)
        assert r_b.outcome is BundleCompileWorkOutcome.COMPLETED, r_b
        assert r_b.invocations == 1
        assert r_b.payload is not None
        assert len(calls) == 2
        # The PROVEN EQUIVALENT supported read: a genuinely new
        # read of A's UNCHANGED content (a new call id) -- the
        # same current key (entry interning over the unchanged
        # content), the SAME retained A payload, no third call.
        s3 = _dep_read(s2, ns, "a2", endpoint, "A.md", A_TEXT)
        t3 = derive_root_region_admission(s3, ns)
        assert t3.outcome is RootRegionAdmissionOutcome.READY, t3.diagnostics
        entry_a2 = _entry_for(t3, "A.md")
        assert entry_a2.content_key == entry_a.content_key
        assert owner.admit(s3, t3, ns, expected_revision=2).outcome is RamStateOutcome.ADMITTED
        assert plane.full_compile_key(entry_a2, (), plan) == key_a
        r_a2 = await plane.resolve_entry(ns, entry_a2, candidate_paths=(), plan=plan)
        assert r_a2.outcome is BundleCompileWorkOutcome.HIT, r_a2
        assert r_a2.invocations == 0
        assert r_a2.payload is r1.payload
        assert len(calls) == 2
    finally:
        await client.aclose()
    assert plane.account.upstream_calls == 2
    assert plane.account.outcome_counts == {"completed": 2}


@pytest.mark.parametrize("mode", MODES)
async def test_needed_only_epoch_rebuild_over_recovered_owner(
    mode: AdmissionMode, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The needed-only epoch rebuild over the EXISTING 020
    ``RecoverySessionOwner``: the resumed owner (a distinct epoch
    strictly above the durable prior) starts with an EMPTY work
    plane -- the resume itself performs NO compile (no upstream
    client exists yet) and the demanded key compiles exactly
    ONCE, only when demanded; the checkpoint publishes the
    admitted P/T record set and NEVER the compiled payload (the
    derived cache is disposable); and after the explicit composed
    teardown the SECOND resume allocates a strictly higher epoch
    where the demanded key is rebuilt exactly once (needed-only,
    nothing eager, nothing carried across the epoch).  The work
    calls pass each RECOVERED owner's registered namespace record
    itself -- the pre-crash ``ns`` and its entry stay the
    expected-value controls only, because the 019/020 identity
    fence refuses a value-equal foreign copy (the recovery law is
    preserved, not weakened)."""
    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    config = _config()
    tokenizer = get_bundle_tokenizer()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=CONTEXT_LARGE))
    fingerprint = derive_compile_policy_fingerprint(
        config_identity=config.config_identity, plan_identity=plan.plan_identity()
    )
    endpoint = ENDPOINTS[0]
    # -- the pre-crash session: the genuine P/T chain admitted
    # into one owner, published as ONE dormant recovery record:
    ns = _policy_ns(mode, f"cw021-t7-{mode.value}", fingerprint)
    t_boot = bootstrap_root_region_lineage((rooted(ROOT_AB),), ns)
    assert t_boot.outcome is RootLineageOutcome.ACCEPTED, t_boot.diagnostics
    s1 = _dep_read(t_boot.state, ns, "b1", endpoint, "A.md", A_TEXT)
    t1 = derive_root_region_admission(s1, ns)
    assert t1.outcome is RootRegionAdmissionOutcome.READY, t1.diagnostics
    entry_a = _entry_for(t1, "A.md")
    plain = RamStateOwnerRegistry()
    plain_owner = plain.acquire(ns)
    assert plain_owner.admit(s1, t1, ns, expected_revision=0).outcome is RamStateOutcome.ADMITTED
    record = RecoveryRecord.from_owner(plain_owner)
    address = RecoverySessionAddress.from_namespace(ns)
    store = RecoveryStore(_prepared_root(tmp_path))
    sess = store.open_session(address)
    try:
        pub = sess.publish(record, expected_generation=0)
        assert pub.limitation is RecoveryStoreLimitation.OK
        assert pub.generation == 1
    finally:
        sess.close()
    # -- the needed restart: resume into a work-enabled registry
    # (the restored ACTUAL P/T equals the genuine one):
    registry = _work_registry()
    resumed = resume_session(registry, store, address)
    assert resumed.outcome is RecoveryResumeOutcome.RESUMED
    assert resumed.prior_epoch == 1
    assert resumed.new_epoch == 2
    owner = resumed.owner
    assert owner is not None
    assert owner.epoch == resumed.new_epoch
    assert resumed.t_result is not None
    assert resumed.t_result.admission == t1.admission
    rec_owner = resumed.recovery
    assert rec_owner is not None
    assert rec_owner.owner is owner
    assert rec_owner.closed is False
    # The registry's registered trusted namespace record is the
    # RECOVERED owner's restored record (value-equal to the
    # pre-crash ``ns``; a different object).  Work calls and the
    # registry identity join must pass that record itself.
    res_ns = owner.namespace
    assert res_ns == ns
    assert res_ns.lineage_key == ns.lineage_key
    entry_a_res = _entry_for(resumed.t_result, "A.md")
    assert entry_a_res.content_key == entry_a.content_key
    # Needed-only: NO upstream client exists before the first
    # demand -- the resume performed no compile.
    calls: list[int] = []
    payloads: dict[str, bytes] = {}
    client = httpx.AsyncClient(transport=httpx.MockTransport(_upstream_handler(payloads, calls)))
    plane = _make_plane(registry, config, tokenizer, client)
    full_key = plane.full_compile_key(entry_a_res, (), plan)
    payloads[full_key] = _valid_payload(
        entry=entry_a_res, candidates=(), config=config, tokenizer=tokenizer, plan=plan
    )
    try:
        assert calls == []
        r1 = await plane.resolve_entry(res_ns, entry_a_res, candidate_paths=(), plan=plan)
        assert r1.outcome is BundleCompileWorkOutcome.COMPLETED, r1
        assert r1.invocations == 1
        assert r1.payload is not None
        assert len(calls) == 1
        r2 = await plane.resolve_entry(res_ns, entry_a_res, candidate_paths=(), plan=plan)
        assert r2.outcome is BundleCompileWorkOutcome.HIT, r2
        assert r2.invocations == 0
        assert r2.payload is r1.payload
        assert len(calls) == 1
        # The checkpoint publishes the admitted P/T record set:
        # the genuine original source is retained, the compiled
        # payload and its full key are NEVER durable.  The
        # resume's own durable epoch binding already advanced
        # the generation once (restart bookkeeping, never a
        # usage-timestamp rewrite); the explicit checkpoint
        # advances it exactly once more -- the normal same-key
        # hit above consumed no publication at all.
        chk = rec_owner.checkpoint_current()
        assert chk.limitation is RecoveryStoreLimitation.OK
        assert resumed.generation == 2
        assert chk.generation == resumed.generation + 1
        chk_bytes = recovery_record_payload_bytes(RecoveryRecord.from_owner(owner))
        # The checkpoint payload is canonical JSON (the source
        # newline is escaped, never a raw byte): verify the
        # DECODED occurrence proof of the admitted read carries
        # the exact original source text.
        chk_json = json.loads(chk_bytes)
        a_texts = [
            occ["proof"]["source_text"]
            for occ in chk_json["d_state"]["occurrences"]
            if "A.md" in occ["proof"].get("proven_executed", [])
        ]
        assert a_texts == [A_TEXT]
        assert full_key.encode("utf-8") not in chk_bytes
        assert r1.payload.data not in chk_bytes
        # The composed teardown releases the writer only after
        # the store owner is gone (the accepted 020 law).
        td = await rec_owner.teardown()
        assert td.outcome is RecoveryTeardownOutcome.TEARDOWN
        assert rec_owner.closed is True
        # -- the SECOND needed restart: the strictly higher
        # epoch rebuilds the demanded key exactly once.
        resumed2 = resume_session(registry, store, address)
        assert resumed2.outcome is RecoveryResumeOutcome.RESUMED
        assert resumed2.prior_epoch == 2
        assert resumed2.new_epoch == 3
        assert resumed2.generation == chk.generation + 1
        owner2 = resumed2.owner
        assert owner2 is not None
        assert owner2.epoch == resumed2.new_epoch
        assert registry.get(owner2.namespace) is owner2
        res_ns2 = owner2.namespace
        assert res_ns2 == ns
        entry_a_res2 = _entry_for(resumed2.t_result, "A.md")
        assert entry_a_res2.content_key == entry_a.content_key
        calls_before = len(calls)
        r3 = await plane.resolve_entry(res_ns2, entry_a_res2, candidate_paths=(), plan=plan)
        assert r3.outcome is BundleCompileWorkOutcome.COMPLETED, r3
        assert r3.invocations == 1
        assert len(calls) == calls_before + 1
        assert r3.payload is not None
        assert r3.payload is not r1.payload
        # The second owner's writer is released at the end.
        rec_owner2 = resumed2.recovery
        assert rec_owner2 is not None
        td2 = await rec_owner2.teardown()
        assert td2.outcome is RecoveryTeardownOutcome.TEARDOWN
    finally:
        await client.aclose()
    assert plane.account.upstream_calls == 2
    assert plane.account.outcome_counts == {"completed": 2}
