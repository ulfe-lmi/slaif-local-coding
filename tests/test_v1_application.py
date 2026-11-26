"""Objective 022-c: the v1 governed request path -- the session and
commit core, plus the governed transaction seam (the marker-shaped
source replay pre-check and the byte-identical transformed-round
fixed point) over a fake store root, the pinned packaged tokenizer
and synthetic identity and environment names; no real secrets, no
live upstream (the compiler is a bounded fake over the mock
transport, never the protected live port).

The cases prove the ACTUAL components: the operator-prepared
protected recovery store, the process RAM owner registry with the
work plane, the pinned tokenizer plan, the actual region lineage /
same-run T / commit-CAS / protected-generation law and the actual
compile-and-select seam under the retained protected generation.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx
import pytest

from slaif_local_coding.config import (
    ContextCacheRouteContract,
    RouteConfig,
)
from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    EntryClass,
)
from slaif_local_coding.constitution.bundles.bundle_budget import (
    BundleBudgetConfig,
    BundleBudgetPlan,
)
from slaif_local_coding.constitution.bundles.bundle_compile_work import (
    BundleCompileWork,
    BundleCompileWorkOutcome,
    BundleCompileWorkResult,
)
from slaif_local_coding.constitution.bundles.bundle_compiler import (
    BUNDLE_COMPILER_PROMPT_POLICY_VERSION,
    BUNDLE_COMPILER_SCHEMA_VERSION,
    BUNDLE_COMPILER_VERSION,
    BundleCompiledDependency,
    BundleCompiledIndex,
    BundleCompiledRule,
    BundleCompiler,
    BundleCompilerConfig,
    serialize_compiled_index,
)
from slaif_local_coding.constitution.bundles.bundle_replace_models import (
    PreparedGenerationProof,
    ReplacementOutcome,
)
from slaif_local_coding.constitution.bundles.bundle_tokenizer import (
    get_bundle_tokenizer,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
)
from slaif_local_coding.constitution.bundles.observation_models import PathContext
from slaif_local_coding.constitution.bundles.observe import observe_request
from slaif_local_coding.constitution.bundles.ram_state import RamStateOwnerRegistry
from slaif_local_coding.constitution.bundles.ram_state_models import RamStateBounds
from slaif_local_coding.constitution.bundles.ram_work_models import RamWorkBounds
from slaif_local_coding.constitution.bundles.recovery_store import (
    RecoveryStore,
    RecoveryStoreLimitation,
)
from slaif_local_coding.constitution.bundles.root_region_admission_models import (
    RootRegionAdmissionEntry,
)
from slaif_local_coding.constitution.bundles.root_region_lineage_models import (
    RootRegionLineageNamespace,
)
from slaif_local_coding.constitution.bundles.v1_application import (
    V1IssuanceContext,
    V1RequestReason,
    V1RequestRefusal,
    V1Session,
    V1SessionTable,
    advance_v1_session,
    build_session_address,
    establish_v1_session,
    prepare_replay_shadow,
    prepare_v1_transaction,
)
from slaif_local_coding.constitution.bundles.v1_runtime import V1Runtime
from slaif_local_coding.constitution.bundles.v1_telemetry import (
    V1_STAGE_OUTCOMES,
    V1ReuseClass,
    V1Stage,
    V1StageRecorder,
)
from slaif_local_coding.constitution.cache import RequestIdentity
from tests.test_causal_history import (
    WORKSPACE,
    exec_call,
    frame,
    out_item,
    root_item,
)

AGENTS_BODY = "Follow the workspace protocol.\n"


#: The protected environment reference of the bounded fake compiler
#: credential (a test-only value; never a real secret).
COMPILER_KEY_ENV = "TEST_V1_APPLICATION_COMPILER_KEY"
COMPILER_KEY_VALUE = "test-only-compiler"
#: The private transport URL of the bounded fake (the development
#: port; the mock transport never opens a socket).
COMPILER_BASE_URL = "http://127.0.0.1:18031/v1"
COMPILER_MODEL_REVISION = "a" * 40
COMPILER_COMPATIBILITY_IDENTITY = "slaif-rtx3090-compat-1"


def _completion_bytes(content: str) -> bytes:
    """The canned chat completion envelope (the closed bounded
    envelope shape the actual compiler parser consumes)."""
    return json.dumps(
        {
            "id": "chatcmpl-022c",
            "object": "chat.completion",
            "model": "qwen38-27b",
            "choices": (
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                },
            ),
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }
    ).encode("utf-8")


def _index_for_demand(user: str, model: str) -> BundleCompiledIndex:
    """One valid compiled index bound to the ACTUAL demand carried in
    the compiler prompt (the echo responder: the compiler's real
    validation -- full-key identity, the exact candidate set, the
    truthful-content law and the rendered allowance -- still runs in
    the actual code over this response)."""
    match = re.search(
        r"entry_class='([a-z_]+)' sha256=([0-9a-f]{64}) byte_length=(\d+).*?"
        r"content_key='([0-9a-f]{64})' compile_key='([0-9a-f]{64})'",
        user,
        re.DOTALL,
    )
    assert match is not None
    entry_class, source_digest, byte_length, content_key, compile_key = (
        match.group(1),
        match.group(2),
        int(match.group(3)),
        match.group(4),
        match.group(5),
    )
    candidate_block = user.split("<deterministic_candidates>\n", 1)[1]
    candidates = json.loads(candidate_block.split("\n</deterministic_candidates>", 1)[0])
    identity: dict[str, Any] = {
        "schema_version": BUNDLE_COMPILER_SCHEMA_VERSION,
        "compiler_version": BUNDLE_COMPILER_VERSION,
        "prompt_policy_version": BUNDLE_COMPILER_PROMPT_POLICY_VERSION,
        "model": model,
        "entry_class": entry_class,
        "content_key": content_key,
        "compile_key": compile_key,
        "source_sha256": source_digest,
        "source_byte_length": byte_length,
    }
    if byte_length == 0:
        # The exact empty source law: zero compiled content.
        return BundleCompiledIndex.model_validate(identity)
    identity.update(
        {
            "summary": "Bounded echo summary.",
            "rules": (
                BundleCompiledRule(
                    rule_id="v1-echo-rule",
                    strength="must",
                    statement="Observe the bounded echo rule.",
                    location="",
                    evidence="Bounded echo evidence.",
                ),
            ),
            "scopes": ("observed bounded scope",),
            "authorities": ("observed bounded authority",),
            "source_of_truth_boundaries": ("adapter request boundary",),
            "dependencies": tuple(
                BundleCompiledDependency(
                    path=path,
                    reference_confidence=0.5,
                    constitutional_priority=0,
                    classification="P4",
                    relationship="candidate",
                    evidence="Supplied deterministic candidate.",
                    acquisition_urgency="none",
                )
                for path in (entry["path"] for entry in candidates)
            ),
            "reread_triggers": ("source change",),
        }
    )
    return BundleCompiledIndex.model_validate(identity)


def _echo_compiler_handler(
    captured: list[httpx.Request],
) -> Callable[[httpx.Request], httpx.Response]:
    """The bounded fake compiler upstream: exactly one valid
    completion per actual demand, bound to the demand's own prompt
    (an unknown demand shape is a test failure, never a guess)."""

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        body = json.loads(request.content)
        user = body["messages"][1]["content"]
        index = _index_for_demand(user, body["model"])
        return httpx.Response(
            200,
            content=_completion_bytes(serialize_compiled_index(index).decode("utf-8")),
        )

    return handler


def _identity() -> RequestIdentity:
    return RequestIdentity(
        principal="principal-1", session="session-1", repository="repo-1", route="text"
    )


def _route() -> RouteConfig:
    return RouteConfig(
        name="text",
        model="qwen38-27b",
        max_images_per_request=0,
        image_overflow_policy="reject",
    )


def _contract() -> ContextCacheRouteContract:
    return ContextCacheRouteContract(model="qwen38-27b", context_tokens=32_768)


def _runtime(
    tmp_path: Path,
    captured: list[httpx.Request] | None = None,
    *,
    compiler_handler: Callable[[httpx.Request], httpx.Response] | None = None,
    session_max_owned_bytes: int = 128 * 1024 * 1024,
) -> V1Runtime:
    """A process v1 runtime over ONE operator-prepared store root
    (a fresh registry per call simulates a fresh process); the
    compiler upstream is the bounded fake over the mock transport
    (the protected live port is never touched); the closed bounds
    and the compiler handler are test seams (the actual law runs
    over them)."""
    root = tmp_path / "recovery-root"
    if not root.exists():
        root.mkdir(mode=0o700)
    root.chmod(0o700)
    store = RecoveryStore(root)
    tokenizer = get_bundle_tokenizer()
    budget = BundleBudgetConfig(context_tokens=32_768)
    plan = BundleBudgetPlan(tokenizer, budget)
    os.environ.setdefault(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    calls = captured if captured is not None else []
    handler = compiler_handler if compiler_handler is not None else _echo_compiler_handler(calls)
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    compiler = BundleCompiler(
        BundleCompilerConfig(
            model="qwen38-27b",
            base_url=COMPILER_BASE_URL,
            model_revision=COMPILER_MODEL_REVISION,
            compatibility_identity=COMPILER_COMPATIBILITY_IDENTITY,
            api_key_env=COMPILER_KEY_ENV,
        ),
        client=client,
    )
    registry = RamStateOwnerRegistry(
        RamStateBounds(
            session_max_owned_bytes=session_max_owned_bytes,
            process_max_owned_bytes=512 * 1024 * 1024,
        ),
        work_bounds=RamWorkBounds(),
    )
    return V1Runtime(
        ram_registry=registry,
        recovery_store=store,
        tokenizer=tokenizer,
        budget=budget,
        budget_plan=plan,
        marker_key=b"test-marker-key-material-0123456789",
        compiler=compiler,
        compile_work=BundleCompileWork(registry, compiler=compiler, tokenizer=tokenizer),
        admission_mode="lean",
        governed_routes={},
    )


def _root_payload(*reads: tuple[str, str]) -> dict[str, Any]:
    """One decoded Responses request: the legitimate root envelope
    plus complete read pairs, exactly as the D law observes them."""
    items: list[dict[str, Any]] = [root_item(AGENTS_BODY)]
    for cid, body in reads:
        items.append(exec_call(cid, f"cat {cid}.md"))
        items.append(out_item(cid, frame(body)))
    return {"model": "qwen38-27b", "input": items}


async def test_cold_bootstrap_commits_and_publishes(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    table = V1SessionTable()
    identity, route, contract = _identity(), _route(), _contract()
    address = build_session_address(runtime, identity, route, contract)
    payload = _root_payload()
    observation = observe_request(payload, endpoint="responses")
    session = await establish_v1_session(
        runtime,
        table,
        address=address,
        identity=identity,
        route=route,
        contract=contract,
        observation=observation,
        payload=payload,
        endpoint="responses",
    )
    assert session is not None and not isinstance(session, V1RequestRefusal)
    assert table.get(address) is session
    # The COLD owner: the legitimate observed scope as workspace, the
    # first record set committed under the empty-owner revision zero.
    assert session.namespace.workspace == WORKSPACE
    assert session.owner.revision == 1
    assert session.owner.quarantined is False
    assert session.bare_session is not None
    # The COLD owner joins the SAME accepted 020 owned/fenced
    # checkpoint path as the resumed owner: the live session owner
    # is present, bound to the first published generation.
    assert session.session_owner is not None
    assert session.session_owner.bound_generation == 1
    # The protected generation: the exact record set is durably
    # published at generation one.
    assert session.last_publish is not None
    assert session.last_publish.limitation is RecoveryStoreLimitation.OK
    assert session.last_publish.generation == 1
    assert session.bare_session.current_generation() == 1
    # An idempotent replay of the SAME payload: no revision advance,
    # no new publication, no recovery original reads -- the ordinary
    # hit reuses the retained publication of the current snapshot.
    obs = observe_request(payload, context=PathContext(workspace=WORKSPACE), endpoint="responses")
    proof, refusal = advance_v1_session(
        session, runtime, payload=payload, endpoint="responses", observation=obs
    )
    assert refusal is None
    assert proof is not None
    assert isinstance(proof, PreparedGenerationProof)
    assert proof.publish.generation == 1
    assert proof.snapshot.revision == 1
    assert session.owner.revision == 1
    assert session.bare_session.current_generation() == 1


async def test_new_read_advances_generation_then_replays(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    table = V1SessionTable()
    identity, route, contract = _identity(), _route(), _contract()
    address = build_session_address(runtime, identity, route, contract)
    bootstrap = _root_payload()
    session = await establish_v1_session(
        runtime,
        table,
        address=address,
        identity=identity,
        route=route,
        contract=contract,
        observation=observe_request(bootstrap, endpoint="responses"),
        payload=bootstrap,
        endpoint="responses",
    )
    assert session is not None and not isinstance(session, V1RequestRefusal)
    # A NEW complete read: the accepted transition commits revision
    # two and the protected generation publishes it durably.
    payload2 = _root_payload(("c1", "A body.\n"))
    proof, refusal = advance_v1_session(
        session,
        runtime,
        payload=payload2,
        endpoint="responses",
        observation=observe_request(
            payload2, context=PathContext(workspace=WORKSPACE), endpoint="responses"
        ),
    )
    assert refusal is None
    assert proof is not None
    assert proof.snapshot.revision == 2
    assert proof.publish.generation == 2
    assert session.owner.revision == 2
    # The replay of the NEW payload is idempotent at the new state.
    proof_replay, refusal_replay = advance_v1_session(
        session,
        runtime,
        payload=payload2,
        endpoint="responses",
        observation=observe_request(
            payload2, context=PathContext(workspace=WORKSPACE), endpoint="responses"
        ),
    )
    assert refusal_replay is None
    assert proof_replay is not None
    assert proof_replay.snapshot.revision == 2
    assert proof_replay.publish.generation == 2
    assert session.owner.revision == 2
    assert session.bare_session is not None
    assert session.bare_session.current_generation() == 2


async def test_resume_restores_state_in_a_higher_epoch(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    table = V1SessionTable()
    identity, route, contract = _identity(), _route(), _contract()
    address = build_session_address(runtime, identity, route, contract)
    bootstrap = _root_payload()
    session = await establish_v1_session(
        runtime,
        table,
        address=address,
        identity=identity,
        route=route,
        contract=contract,
        observation=observe_request(bootstrap, endpoint="responses"),
        payload=bootstrap,
        endpoint="responses",
    )
    assert session is not None and not isinstance(session, V1RequestRefusal)
    advance_payload = _root_payload(("c1", "A body.\n"))
    proof, refusal = advance_v1_session(
        session,
        runtime,
        payload=advance_payload,
        endpoint="responses",
        observation=observe_request(
            advance_payload,
            context=PathContext(workspace=WORKSPACE),
            endpoint="responses",
        ),
    )
    assert refusal is None
    assert proof is not None
    assert proof.publish.generation == 2
    assert session.owner.revision == 2
    prior_epoch = session.owner.epoch
    # The process restart: the writer session is released and a FRESH
    # process runtime (a new registry) resumes the SAME address from
    # the protected store.
    assert session.bare_session is not None
    session.bare_session.close()
    runtime2 = _runtime(tmp_path)
    table2 = V1SessionTable()
    resumed = await establish_v1_session(
        runtime2,
        table2,
        address=address,
        identity=identity,
        route=route,
        contract=contract,
        observation=observe_request(bootstrap, endpoint="responses"),
        payload=bootstrap,
        endpoint="responses",
    )
    assert resumed is not None and not isinstance(resumed, V1RequestRefusal)
    assert table2.get(address) is resumed
    # The resumed owner: the retained record set (the P-state region
    # revision persists through the restart), a distinct live epoch
    # STRICTLY above the record's prior epoch, the retained resume
    # writer session, and the fresh owner's own commit counter
    # restarted at the restored record set (the snapshot's revision
    # field is the owner commit fence, distinct from the P-state
    # region revision).
    resumed_snapshot = resumed.owner.snapshot
    assert resumed_snapshot is not None
    assert resumed_snapshot.revision == 1
    assert resumed_snapshot.state.revision == 2
    assert resumed.owner.revision == 1
    assert resumed.owner.epoch > prior_epoch
    assert resumed.session_owner is not None
    assert resumed.bare_session is None
    # The verified resumed scope is the workspace of the transaction.
    assert resumed.namespace.workspace == WORKSPACE
    # A further accepted transition publishes under the resumed
    # session's bound generation (the next durable generation).
    proof, refusal = advance_v1_session(
        resumed,
        runtime2,
        payload=_root_payload(("c1", "A body.\n"), ("c2", "B body.\n")),
        endpoint="responses",
        observation=observe_request(
            bootstrap, context=PathContext(workspace=WORKSPACE), endpoint="responses"
        ),
    )
    # The resume's durable epoch binding moved the bound generation
    # to three; the new protected generation publishes at four over
    # the P-state region revision three.
    assert refusal is None
    assert proof is not None
    assert proof.snapshot.revision == 2
    assert proof.snapshot.state.revision == 3
    assert proof.publish.generation == 4
    assert resumed.owner.revision == 2


async def test_rootless_request_is_not_governed(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    table = V1SessionTable()
    identity, route, contract = _identity(), _route(), _contract()
    address = build_session_address(runtime, identity, route, contract)
    payload = {
        "model": "qwen38-27b",
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": "Hello"}],
            }
        ],
    }
    result = await establish_v1_session(
        runtime,
        table,
        address=address,
        identity=identity,
        route=route,
        contract=contract,
        observation=observe_request(payload, endpoint="responses"),
        payload=payload,
        endpoint="responses",
    )
    # No legitimate scope: not a governed request (the caller
    # forwards the payload unchanged); no owner and no committed
    # generation exist for the address.
    assert result is None
    assert table.get(address) is None
    session = runtime.recovery_store.open_session(address)
    try:
        assert session.current_generation() == 0
    finally:
        session.close()


async def test_distinct_sessions_are_distinct_addresses(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    table = V1SessionTable()
    route, contract = _route(), _contract()
    identity_a = _identity()
    identity_b = RequestIdentity(
        principal="principal-2", session="session-2", repository="repo-2", route="text"
    )
    address_a = build_session_address(runtime, identity_a, route, contract)
    address_b = build_session_address(runtime, identity_b, route, contract)
    assert address_a.lineage_key != address_b.lineage_key
    bootstrap = _root_payload()
    session_a = await establish_v1_session(
        runtime,
        table,
        address=address_a,
        identity=identity_a,
        route=route,
        contract=contract,
        observation=observe_request(bootstrap, endpoint="responses"),
        payload=bootstrap,
        endpoint="responses",
    )
    session_b = await establish_v1_session(
        runtime,
        table,
        address=address_b,
        identity=identity_b,
        route=route,
        contract=contract,
        observation=observe_request(bootstrap, endpoint="responses"),
        payload=bootstrap,
        endpoint="responses",
    )
    assert session_a is not None and not isinstance(session_a, V1RequestRefusal)
    assert session_b is not None and not isinstance(session_b, V1RequestRefusal)
    assert session_a.owner is not session_b.owner
    assert session_a.owner.namespace is not session_b.owner.namespace
    # Same observed scope, distinct trusted namespaces (the identity
    # fields bind into the namespace key).
    assert session_a.owner.namespace.workspace == session_b.owner.namespace.workspace
    assert session_a.owner.namespace.lineage_key != session_b.owner.namespace.lineage_key


# -- the governed transaction seam: the marker pre-check, the
# byte-identical transformed-round fixed point, the stale-marker
# refusal and the resumed-session materialized publish -----------


async def test_round_one_transforms_and_round_two_is_the_fixed_point(tmp_path: Path) -> None:
    captured: list[httpx.Request] = []
    runtime = _runtime(tmp_path, captured=captured)
    table = V1SessionTable()
    identity, route, contract = _identity(), _route(), _contract()
    address = build_session_address(runtime, identity, route, contract)
    bootstrap = _root_payload()
    session = await establish_v1_session(
        runtime,
        table,
        address=address,
        identity=identity,
        route=route,
        contract=contract,
        observation=observe_request(bootstrap, endpoint="responses"),
        payload=bootstrap,
        endpoint="responses",
    )
    assert session is not None and not isinstance(session, V1RequestRefusal)
    payload2 = _root_payload(("c1", "A body.\n"))
    context = PathContext(workspace=WORKSPACE)
    obs = observe_request(payload2, context=context, endpoint="responses")
    # The app seam order: the marker pre-check FIRST.  The ORIGINAL
    # payload carries no marker candidate: returned by identity, no
    # pre-check work.  The c1 read is recognized but NOT acquired at
    # this stage (trusted issuance is the order section 3 wiring):
    # its carrier stays raw -- the transaction edits ADMISSION
    # entries only, so round one commits the root LIVE edit alone.
    shadow, pre = await prepare_replay_shadow(
        session, runtime, payload=payload2, endpoint="responses", observation=obs
    )
    assert pre is None
    assert shadow is payload2
    proof, refusal = advance_v1_session(
        session, runtime, payload=shadow, endpoint="responses", observation=obs
    )
    assert refusal is None and proof is not None
    assert proof.publish.generation == 2
    # Round one: the actual transaction compiles the ACTUAL admitted
    # entries through the work plane (the bounded fake upstream) and
    # commits the root LIVE edit under the protected generation.
    tx1 = await prepare_v1_transaction(
        session, runtime, payload=payload2, endpoint="responses", observation=obs, proof=proof
    )
    assert not isinstance(tx1, V1RequestRefusal)
    assert tx1.outcome is ReplacementOutcome.OK
    assert tx1.edits_committed == 1 and tx1.markers_emitted == 1
    assert len(tx1.selected_content_keys) == 1
    assert len(captured) == 1  # exactly one upstream call per admitted entry
    round1_body = tx1.body
    # One marker in the whole outgoing body (the root LIVE tag); the
    # unacquired read carrier is preserved raw.
    assert round1_body.count(b"[slaif-live:v") == 1
    assert round1_body.count(b"[slaif-evidence:v") == 0
    assert b"A body." in round1_body
    transformed = json.loads(round1_body)
    # The client resends its OWN transformed payload: the ONE scoped
    # observation of the actual payload feeds the whole seam (as the
    # app does).
    obs_t = observe_request(transformed, context=context, endpoint="responses")
    shadow2, pre2 = await prepare_replay_shadow(
        session, runtime, payload=transformed, endpoint="responses", observation=obs_t
    )
    assert pre2 is None
    assert shadow2 is not None and shadow2 is not transformed
    # Unspliced to the retained originals at the source spans; the
    # stable compiled-context region the round-one outgoing body
    # carries is ordinary request text and passes the shadow
    # through unchanged (order 022-d section 3).
    expected_shadow2 = json.loads(json.dumps(payload2))
    expected_shadow2["instructions"] = transformed["instructions"]
    assert shadow2 == expected_shadow2
    proof2, refusal2 = advance_v1_session(
        session, runtime, payload=shadow2, endpoint="responses", observation=obs_t
    )
    assert refusal2 is None and proof2 is not None
    # The ordinary hit: no revision advance, no new publication.
    assert proof2.publish.generation == 2
    assert proof2.snapshot.revision == 2
    assert session.owner.revision == 2
    # The transaction re-runs over the ACTUAL payload under the
    # retained proof: the marker replays in place, zero new edits,
    # and the outgoing body is byte-identical (the fixed point).
    tx2 = await prepare_v1_transaction(
        session,
        runtime,
        payload=transformed,
        endpoint="responses",
        observation=obs_t,
        proof=proof2,
    )
    assert not isinstance(tx2, V1RequestRefusal)
    assert tx2.outcome is ReplacementOutcome.OK
    assert tx2.edits_committed == 0
    assert tx2.markers_replayed == 1
    assert tx2.body == round1_body


async def test_reuse_class_is_bound_to_the_closed_across_request_hit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The four-way reuse fact at the owning transaction stage
    (objective 023-a) is bound to the closed compiler outcome
    labels, not to the zero-dispatch count alone: the same
    committed replacement with no compile work dispatched anywhere
    in the request earns original-present RAM reuse ONLY when the
    committing run served EVERY represented entry from retained
    RAM (the closed ``hit`` label of an actual across-request
    hit); the single-flight follower label (``joined``) carries
    the same zero-dispatch shape and earns no reuse fact, and the
    first compile (dispatched work) earns no reuse fact either.
    The actual single-flight join semantics are proven in the
    019-b work-plane suite; this test drives the owning stage
    with the closed labels."""
    captured: list[httpx.Request] = []
    runtime = _runtime(tmp_path, captured=captured)
    table = V1SessionTable()
    identity, route, contract = _identity(), _route(), _contract()
    address = build_session_address(runtime, identity, route, contract)
    bootstrap = _root_payload()
    session = await establish_v1_session(
        runtime,
        table,
        address=address,
        identity=identity,
        route=route,
        contract=contract,
        observation=observe_request(bootstrap, endpoint="responses"),
        payload=bootstrap,
        endpoint="responses",
    )
    assert session is not None and not isinstance(session, V1RequestRefusal)
    payload2 = _root_payload(("c1", "A body.\n"))
    context = PathContext(workspace=WORKSPACE)
    obs = observe_request(payload2, context=context, endpoint="responses")
    shadow, pre = await prepare_replay_shadow(
        session, runtime, payload=payload2, endpoint="responses", observation=obs
    )
    assert pre is None and shadow is payload2
    proof, refusal = advance_v1_session(
        session, runtime, payload=shadow, endpoint="responses", observation=obs
    )
    assert refusal is None and proof is not None
    # -- arm 1: the FIRST compile dispatches; no reuse fact --------
    recorder1 = V1StageRecorder(route="text", endpoint="responses")
    tx1 = await prepare_v1_transaction(
        session,
        runtime,
        payload=payload2,
        endpoint="responses",
        observation=obs,
        proof=proof,
        telemetry=recorder1,
    )
    assert not isinstance(tx1, V1RequestRefusal)
    assert tx1.outcome is ReplacementOutcome.OK
    assert tx1.edits_committed == 1 and len(captured) == 1
    assert [e for e in recorder1.events if e.stage is V1Stage.REUSE_CLASS] == []
    # -- arm 2: the raw resend is the ACTUAL across-request hit ----
    obs2 = observe_request(payload2, context=context, endpoint="responses")
    shadow2, pre2 = await prepare_replay_shadow(
        session, runtime, payload=payload2, endpoint="responses", observation=obs2
    )
    assert pre2 is None and shadow2 is payload2
    proof2, refusal2 = advance_v1_session(
        session, runtime, payload=shadow2, endpoint="responses", observation=obs2
    )
    assert refusal2 is None and proof2 is not None
    recorder2 = V1StageRecorder(route="text", endpoint="responses")
    tx2 = await prepare_v1_transaction(
        session,
        runtime,
        payload=payload2,
        endpoint="responses",
        observation=obs2,
        proof=proof2,
        telemetry=recorder2,
    )
    assert not isinstance(tx2, V1RequestRefusal)
    assert tx2.outcome is ReplacementOutcome.OK
    assert tx2.edits_committed == 1
    assert len(captured) == 1  # zero new dispatch anywhere in the request
    reuse2 = [e for e in recorder2.events if e.stage is V1Stage.REUSE_CLASS]
    assert [e.outcome for e in reuse2] == [V1ReuseClass.ORIGINAL_PRESENT_RAM_REUSE.value]

    # -- arm 3: the closed follower label earns no reuse fact ------
    real_resolve = BundleCompileWork.resolve_entry

    async def _follower_resolve(
        self: BundleCompileWork,
        namespace: RootRegionLineageNamespace,
        entry: RootRegionAdmissionEntry,
        *,
        candidate_paths: tuple[str, ...],
        plan: BundleBudgetPlan,
    ) -> BundleCompileWorkResult:
        result = await real_resolve(
            self, namespace, entry, candidate_paths=candidate_paths, plan=plan
        )
        return result.model_copy(update={"outcome": BundleCompileWorkOutcome.JOINED})

    monkeypatch.setattr(BundleCompileWork, "resolve_entry", _follower_resolve)
    obs3 = observe_request(payload2, context=context, endpoint="responses")
    shadow3, pre3 = await prepare_replay_shadow(
        session, runtime, payload=payload2, endpoint="responses", observation=obs3
    )
    assert pre3 is None and shadow3 is payload2
    proof3, refusal3 = advance_v1_session(
        session, runtime, payload=shadow3, endpoint="responses", observation=obs3
    )
    assert refusal3 is None and proof3 is not None
    recorder3 = V1StageRecorder(route="text", endpoint="responses")
    tx3 = await prepare_v1_transaction(
        session,
        runtime,
        payload=payload2,
        endpoint="responses",
        observation=obs3,
        proof=proof3,
        telemetry=recorder3,
    )
    assert not isinstance(tx3, V1RequestRefusal)
    assert tx3.outcome is ReplacementOutcome.OK
    assert tx3.edits_committed == 1 and len(captured) == 1
    assert [e for e in recorder3.events if e.stage is V1Stage.REUSE_CLASS] == []
    # The closed vocabulary never records the unearned value.
    assert V1ReuseClass.CLIENT_COMPACTION.value not in V1_STAGE_OUTCOMES[V1Stage.REUSE_CLASS]


async def test_pre_forward_compiler_refusal_is_typed_and_retries_nothing(
    tmp_path: Path,
) -> None:
    """A compiler failure at the transaction stage is the fixed
    typed 503 pre-forward refusal: the main request is never
    forwarded, exactly ONE compile attempt is made (no retry), and
    no state changes (the actual accepted compiler contract runs --
    the bounded fake returns an upstream error)."""
    captured: list[httpx.Request] = []

    def failing_compiler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            500,
            json={"error": {"message": "upstream unavailable", "type": "upstream_error"}},
        )

    runtime, table, session, context, proof, tx0 = await _bootstrap_ref_session_with(
        tmp_path,
        captured,
        compiler_handler=failing_compiler,
    )
    payload = _ref_payload()
    obs = observe_request(payload, context=context, endpoint="responses")
    shadow, pre = await prepare_replay_shadow(
        session, runtime, payload=payload, endpoint="responses", observation=obs
    )
    assert pre is None
    assert shadow is not None
    proof1, refusal = advance_v1_session(
        session, runtime, payload=shadow, endpoint="responses", observation=obs
    )
    assert refusal is None and proof1 is not None
    tx = await prepare_v1_transaction(
        session, runtime, payload=payload, endpoint="responses", observation=obs, proof=proof1
    )
    assert isinstance(tx, V1RequestRefusal)
    assert tx.reason is V1RequestReason.COMPILER_REFUSED
    assert tx.status_code == 503
    assert tx.code == "v1_compiler_refused"
    assert len(captured) == 1  # one attempt, no retry
    assert session.owner.revision == 1  # nothing new committed


async def test_pre_forward_publish_refusal_when_the_checkpoint_fails(
    tmp_path: Path,
) -> None:
    """A checkpoint (protected-generation) failure at the commit
    stage is the fixed typed 503 pre-forward refusal: the RAM
    commit-CAS may have applied, but the request is never forwarded
    without the durable-generation proof (the actual store contract
    -- the closed session writer refuses publication)."""
    runtime, table, session, context, proof, tx0 = await _bootstrap_ref_session(tmp_path, [])
    assert session.bare_session is not None
    assert session.session_owner is not None
    session.bare_session.close()
    payload = _ref_payload(("c1", "cat c1.md", "A body.\n"))
    obs = observe_request(payload, context=context, endpoint="responses")
    shadow, pre = await prepare_replay_shadow(
        session, runtime, payload=payload, endpoint="responses", observation=obs
    )
    assert pre is None
    assert shadow is not None
    proof2, refusal2 = advance_v1_session(
        session, runtime, payload=shadow, endpoint="responses", observation=obs
    )
    assert refusal2 is not None
    assert refusal2.reason is V1RequestReason.PUBLISH_REFUSED
    assert refusal2.status_code == 503
    assert refusal2.code == "v1_publish_refused"
    # The commit-CAS applied but the protected generation did not
    # publish (the closed writer's typed session_closed refusal; no
    # durable handoff, nothing forwarded); the bound generation
    # stays at the bootstrap's one.
    assert session.owner.revision == 2
    assert session.session_owner is not None
    assert session.session_owner.bound_generation == 1


async def test_pre_forward_budget_refusal_keeps_the_exact_prior_state(
    tmp_path: Path,
) -> None:
    """The RAM session budget is a pre-forward typed refusal: a
    record set whose fenced protected publication cannot be reserved
    within the bound is refused at the cold establish (503) -- the
    session is discarded, nothing is committed, and the exact prior
    state (no live session, no durable generation) is retained."""
    captured: list[httpx.Request] = []
    runtime = _runtime(tmp_path, captured, session_max_owned_bytes=65536)
    table = V1SessionTable()
    identity, route, contract = _identity(), _route(), _contract()
    address = build_session_address(runtime, identity, route, contract)
    bootstrap = _ref_payload()
    session = await establish_v1_session(
        runtime,
        table,
        address=address,
        identity=identity,
        route=route,
        contract=contract,
        observation=observe_request(bootstrap, endpoint="responses"),
        payload=bootstrap,
        endpoint="responses",
    )
    assert isinstance(session, V1RequestRefusal)
    assert session.reason is V1RequestReason.COLD_PUBLISH_REFUSED
    assert session.status_code == 503
    assert session.code == "v1_cold_publish_refused"
    # The session was discarded: no live owner, no durable state.
    assert table.get(address) is None
    assert len(captured) == 0  # the refusal is pre-forward


# ------------------------------------------------------------------
# Order 022-c section 3: the post-forward trusted issuance -- the
# ACTUAL direct main upstream response (never compiler traffic)
# observed through the per-request frozen V1IssuanceContext and
# registered under the committed-state CAS -- and the read it
# acquires (the issued call's subsequent matching read pair earns
# the FILE entry, the LIVE marker and the fixed point).
# ------------------------------------------------------------------

#: The legitimate root envelope: the backtick references are the
#: F-graph candidate law (a read's member is an eligible admission
#: candidate only when the root evidence references that path).
AGENTS_BODY_REF = "Follow `c1.md` and `c3.md` before acting.\n"


def _ref_payload(*reads: tuple[str, str, str]) -> dict[str, Any]:
    """One decoded Responses request: the referencing root envelope
    plus complete read pairs (call_id, cmd, body)."""
    items: list[dict[str, Any]] = [root_item(AGENTS_BODY_REF)]
    for cid, cmd, body in reads:
        items.append(exec_call(cid, cmd))
        items.append(out_item(cid, frame(body)))
    return {"model": "qwen38-27b", "input": items}


def _responses_issue_body(call_id: str, cmd: str) -> bytes:
    """One final ``completed`` Responses object carrying the ONE
    complete supported function call (the actual wire shape the
    nonstreaming observer consumes)."""
    return json.dumps(
        {
            "id": f"resp-{call_id}",
            "status": "completed",
            "output": (
                {
                    "type": "function_call",
                    "id": f"fc-{call_id}",
                    "call_id": call_id,
                    "name": "exec_command",
                    "arguments": json.dumps({"cmd": cmd}),
                },
            ),
        }
    ).encode("utf-8")


def _sse_frame(payload: dict[str, Any]) -> bytes:
    """One SSE frame of the actual direct Responses stream."""
    return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n".encode()


async def _bootstrap_ref_session(
    tmp_path: Path, captured: list[httpx.Request]
) -> tuple[V1Runtime, V1SessionTable, V1Session, PathContext, PreparedGenerationProof, Any]:
    """The COLD root bootstrap over the referencing envelope with
    the round-one proof and transaction committed (``tx0`` is the
    bootstrap request's transaction result: its represented frontier
    is the round-one frozen frontier the app builds the issuance
    context from)."""
    return await _bootstrap_ref_session_with(tmp_path, captured)


async def _bootstrap_ref_session_with(
    tmp_path: Path,
    captured: list[httpx.Request],
    *,
    compiler_handler: Callable[[httpx.Request], httpx.Response] | None = None,
    session_max_owned_bytes: int = 128 * 1024 * 1024,
) -> tuple[V1Runtime, V1SessionTable, V1Session, PathContext, PreparedGenerationProof, Any]:
    """The COLD root bootstrap over the referencing envelope with
    the round-one proof and transaction committed (``tx0`` is the
    bootstrap request's transaction result); the compiler handler
    and the RAM session bound are the closed test seams."""
    runtime = _runtime(
        tmp_path,
        captured=captured,
        compiler_handler=compiler_handler,
        session_max_owned_bytes=session_max_owned_bytes,
    )
    table = V1SessionTable()
    identity, route, contract = _identity(), _route(), _contract()
    address = build_session_address(runtime, identity, route, contract)
    bootstrap = _ref_payload()
    session = await establish_v1_session(
        runtime,
        table,
        address=address,
        identity=identity,
        route=route,
        contract=contract,
        observation=observe_request(bootstrap, endpoint="responses"),
        payload=bootstrap,
        endpoint="responses",
    )
    assert session is not None and not isinstance(session, V1RequestRefusal)
    context = PathContext(workspace=WORKSPACE)
    obs = observe_request(bootstrap, context=context, endpoint="responses")
    shadow, pre = await prepare_replay_shadow(
        session, runtime, payload=bootstrap, endpoint="responses", observation=obs
    )
    assert pre is None
    assert shadow is not None
    proof, refusal = advance_v1_session(
        session, runtime, payload=shadow, endpoint="responses", observation=obs
    )
    assert refusal is None and proof is not None
    tx0 = await prepare_v1_transaction(
        session, runtime, payload=bootstrap, endpoint="responses", observation=obs, proof=proof
    )
    return runtime, table, session, context, proof, tx0


async def test_represented_frontier_is_per_request_and_reduces_proven_ancestors(
    tmp_path: Path,
) -> None:
    """The represented frontier is PER REQUEST: the bootstrap request
    represents only the root fact; the request that reads both issued
    files represents the root and both occurrences (each anchored
    under the bootstrap frontier, the proven root ancestor reduces,
    the two occurrences are incomparable and BOTH are kept); a
    retained occurrence this request does NOT represent is no member
    (retention alone never establishes a parent).  The FROZEN
    per-request frontier never rebases on later committed state."""
    captured: list[httpx.Request] = []
    runtime, table, session, context, proof, tx0 = await _bootstrap_ref_session(tmp_path, captured)
    # The bootstrap request represents only the root fact.
    assert tx0.represented_frontier == (CAUSAL_ROOT_FACT,)
    ctx = V1IssuanceContext(
        session=session,
        namespace=session.namespace,
        state=proof.snapshot.state,
        frontier=tx0.represented_frontier,
        endpoint="responses",
    )
    # Both issuances register from the SAME frozen context under the
    # committed-state CAS (the protected generation commits each:
    # revision one to two to three).
    ctx.observe_nonstream(_responses_issue_body("c1", "cat c1.md"))
    ctx.observe_nonstream(_responses_issue_body("c3", "cat c3.md"))
    assert session.owner.revision == 3
    snapshot = session.owner.snapshot
    assert snapshot is not None
    d = snapshot.state.d_state
    assert [i.call_id for i in d.issuances] == ["c1", "c3"]
    assert all(i.parent_frontier == (CAUSAL_ROOT_FACT,) for i in d.issuances)
    # The request that reads BOTH issued files: each occurrence is
    # anchored under its issuance's frozen frontier (the proven
    # root-parent edge); the request represents the root and both
    # occurrences -- the proven root ancestor reduces, the two
    # occurrences are incomparable (both kept, canonical order).
    payload = _ref_payload(("c1", "cat c1.md", "A body.\n"), ("c3", "cat c3.md", "C body.\n"))
    obs = observe_request(payload, context=context, endpoint="responses")
    shadow, pre = await prepare_replay_shadow(
        session, runtime, payload=payload, endpoint="responses", observation=obs
    )
    assert pre is None
    assert shadow is not None
    proof_a, refusal = advance_v1_session(
        session, runtime, payload=shadow, endpoint="responses", observation=obs
    )
    assert refusal is None and proof_a is not None
    occs = proof_a.snapshot.state.d_state.occurrences
    by_call = {o.call_id: o for o in occs}
    assert set(by_call) == {"c1", "c3"}
    assert all(o.anchored is True for o in occs)
    tx_a = await prepare_v1_transaction(
        session, runtime, payload=payload, endpoint="responses", observation=obs, proof=proof_a
    )
    assert not isinstance(tx_a, V1RequestRefusal)
    assert tx_a.represented_frontier == tuple(
        sorted((by_call["c1"].occurrence_id, by_call["c3"].occurrence_id))
    )
    # The FROZEN frontier of the FIRST request's context never
    # rebases on any of the later committed state.
    assert ctx.frontier == (CAUSAL_ROOT_FACT,)


async def test_nonstream_issuance_acquires_the_read_and_edits_it_live(
    tmp_path: Path,
) -> None:
    """The big section 3 proof: the round-one ACTUAL direct response
    issues the call; the round-two matching read pair is then
    ACQUIRED (the FILE entry under the same-run evidence) and the
    single outgoing body carries the root LIVE marker and the read
    LIVE marker; resending that body is the byte-identical fixed
    point with zero new edits and zero further upstream calls."""
    captured: list[httpx.Request] = []
    runtime, table, session, context, proof, tx0 = await _bootstrap_ref_session(tmp_path, captured)
    ctx = V1IssuanceContext(
        session=session,
        namespace=session.namespace,
        state=proof.snapshot.state,
        frontier=tx0.represented_frontier,
        endpoint="responses",
    )
    # Round one: the direct response issues c1 (the exact binding
    # the subsequent read will carry); a second observation of the
    # SAME binding is the REPLAYED no-op (no second commit).
    ctx.observe_nonstream(_responses_issue_body("c1", "cat c1.md"))
    assert session.owner.revision == 2
    ctx.observe_nonstream(_responses_issue_body("c1", "cat c1.md"))
    assert session.owner.revision == 2
    # Round two: the client result for the issued call.  The same-run
    # T now carries the c1 FILE entry (no unproven-candidate reason)
    # and the transaction edits BOTH carriers.
    payload = _ref_payload(("c1", "cat c1.md", "A body.\n"))
    obs = observe_request(payload, context=context, endpoint="responses")
    shadow, pre = await prepare_replay_shadow(
        session, runtime, payload=payload, endpoint="responses", observation=obs
    )
    assert pre is None
    assert shadow is not None
    proof2, refusal = advance_v1_session(
        session, runtime, payload=shadow, endpoint="responses", observation=obs
    )
    assert refusal is None and proof2 is not None
    admission = proof2.snapshot.result.admission
    assert admission is not None
    assert admission.admission_reasons == ()
    assert [e.entry_class for e in admission.entries] == [EntryClass.FILE_BUNDLE_ENTRY]
    tx = await prepare_v1_transaction(
        session, runtime, payload=payload, endpoint="responses", observation=obs, proof=proof2
    )
    assert not isinstance(tx, V1RequestRefusal)
    assert tx.outcome is ReplacementOutcome.OK
    assert tx.edits_committed == 2
    assert tx.markers_emitted == 2
    assert len(tx.selected_content_keys) == 2
    assert len(captured) == 2  # one upstream compile per admitted entry
    body = tx.body
    assert body.count(b"[slaif-live:v") == 2
    assert body.count(b"[slaif-evidence:v") == 0
    assert b"A body." not in body
    assert AGENTS_BODY_REF.encode("utf-8") not in body
    # Round three: the client resends its OWN transformed payload:
    # the marker replays in place, zero new edits, byte-identical
    # outgoing body, no further upstream call (the RAM hit).
    transformed = json.loads(body)
    obs_t = observe_request(transformed, context=context, endpoint="responses")
    shadow_t, pre_t = await prepare_replay_shadow(
        session, runtime, payload=transformed, endpoint="responses", observation=obs_t
    )
    assert pre_t is None
    assert shadow_t is not None
    # Unspliced to the retained originals at the source spans; the
    # stable compiled-context region is ordinary request text that
    # passes the shadow through unchanged (order 022-d section 3).
    expected_shadow_t = json.loads(json.dumps(payload))
    expected_shadow_t["instructions"] = transformed["instructions"]
    assert shadow_t == expected_shadow_t
    proof3, refusal3 = advance_v1_session(
        session, runtime, payload=shadow_t, endpoint="responses", observation=obs_t
    )
    assert refusal3 is None and proof3 is not None
    tx3 = await prepare_v1_transaction(
        session,
        runtime,
        payload=transformed,
        endpoint="responses",
        observation=obs_t,
        proof=proof3,
    )
    assert not isinstance(tx3, V1RequestRefusal)
    assert tx3.outcome is ReplacementOutcome.OK
    assert tx3.edits_committed == 0
    assert tx3.markers_replayed == 2
    assert tx3.body == body
    assert len(captured) == 2


async def test_stale_superseded_marker_is_refused(tmp_path: Path) -> None:
    """True stale-marker supersession: after the call is issued,
    acquired and its marker minted, the file is re-read (a NEW
    issued call) with different content; the old occurrence is
    positively superseded.  The request carrying the old LIVE marker
    plus the new read is the fixed typed 409 (no raw fallback), and
    the bare resend of the old transformed payload is the marker-side
    409 BEFORE raw acquisition."""
    captured: list[httpx.Request] = []
    runtime, table, session, context, proof, tx0 = await _bootstrap_ref_session(tmp_path, captured)
    ctx = V1IssuanceContext(
        session=session,
        namespace=session.namespace,
        state=proof.snapshot.state,
        frontier=tx0.represented_frontier,
        endpoint="responses",
    )
    ctx.observe_nonstream(_responses_issue_body("c1", "cat c1.md"))
    payload = _ref_payload(("c1", "cat c1.md", "A body.\n"))
    obs = observe_request(payload, context=context, endpoint="responses")
    shadow, pre = await prepare_replay_shadow(
        session, runtime, payload=payload, endpoint="responses", observation=obs
    )
    assert pre is None
    assert shadow is not None
    proof2, refusal = advance_v1_session(
        session, runtime, payload=shadow, endpoint="responses", observation=obs
    )
    assert refusal is None and proof2 is not None
    tx2 = await prepare_v1_transaction(
        session, runtime, payload=payload, endpoint="responses", observation=obs, proof=proof2
    )
    assert not isinstance(tx2, V1RequestRefusal)
    assert tx2.edits_committed == 2 and tx2.markers_emitted == 2
    round2_body = tx2.body
    # The round-two direct response issues the re-read (a DISTINCT
    # call over the same file).
    ctx2 = V1IssuanceContext(
        session=session,
        namespace=session.namespace,
        state=proof2.snapshot.state,
        frontier=tx2.represented_frontier,
        endpoint="responses",
    )
    ctx2.observe_nonstream(_responses_issue_body("c5", "cat c1.md"))
    assert session.owner.revision == 4
    # The request carrying the OLD transformed c1 carrier (the LIVE
    # marker) plus the NEW read: the transition commits the new
    # evidence, but the transaction's marker replay over the
    # positively superseded occurrence is the fixed 409 -- no raw
    # fallback forward of this request.
    old = json.loads(round2_body)
    stale_items = [
        *old["input"],
        exec_call("c5", "cat c1.md"),
        out_item("c5", frame("A body v2.\n")),
    ]
    stale_payload = {"model": "qwen38-27b", "input": stale_items}
    obs_s = observe_request(stale_payload, context=context, endpoint="responses")
    shadow_s, pre_s = await prepare_replay_shadow(
        session, runtime, payload=stale_payload, endpoint="responses", observation=obs_s
    )
    assert pre_s is None and shadow_s is not None
    proof_s, refusal_s = advance_v1_session(
        session, runtime, payload=shadow_s, endpoint="responses", observation=obs_s
    )
    assert refusal_s is None and proof_s is not None
    tx_s = await prepare_v1_transaction(
        session,
        runtime,
        payload=stale_payload,
        endpoint="responses",
        observation=obs_s,
        proof=proof_s,
    )
    assert isinstance(tx_s, V1RequestRefusal)
    assert tx_s.reason is V1RequestReason.TRANSACTION_CONFLICT
    assert tx_s.status_code == 409
    assert tx_s.code == "v1_transaction_conflict"
    # The bare resend of the old transformed payload is refused at
    # the marker pre-check (before raw acquisition): the old
    # occurrence is superseded in the committed state.
    old_payload = json.loads(round2_body)
    obs_o = observe_request(old_payload, context=context, endpoint="responses")
    shadow_o, pre_o = await prepare_replay_shadow(
        session, runtime, payload=old_payload, endpoint="responses", observation=obs_o
    )
    assert shadow_o is None
    assert pre_o is not None
    assert pre_o.reason is V1RequestReason.TRANSACTION_CONFLICT
    assert pre_o.status_code == 409
    assert pre_o.code == "v1_transaction_conflict"
    # The marker-side refusal committed nothing further.
    revision_after = session.owner.revision
    assert revision_after == proof_s.snapshot.revision


async def test_streamed_issuance_registers_only_complete_calls(
    tmp_path: Path,
) -> None:
    """The bounded incremental SSE assembly: a call is registered
    only on its OWN completion evidence (the split arguments arrive
    across chunk and event boundaries); a stream cut mid-arguments
    and a ``[DONE]`` with an unfinished call drop the assembly
    (never a partial issuance); a terminal ``response.failed``
    discards everything still in flight."""
    captured: list[httpx.Request] = []
    runtime, table, session, context, proof, tx0 = await _bootstrap_ref_session(tmp_path, captured)
    ctx = V1IssuanceContext(
        session=session,
        namespace=session.namespace,
        state=proof.snapshot.state,
        frontier=tx0.represented_frontier,
        endpoint="responses",
    )
    added = _sse_frame(
        {
            "type": "response.output_item.added",
            "item": {
                "id": "fc-c3",
                "type": "function_call",
                "call_id": "c3",
                "name": "exec_command",
            },
        }
    )
    delta1 = _sse_frame(
        {
            "type": "response.function_call_arguments.delta",
            "item_id": "c3",
            "delta": '{"cmd": "cat',
        }
    )
    delta2 = _sse_frame(
        {
            "type": "response.function_call_arguments.delta",
            "item_id": "c3",
            "delta": ' c3.md"}',
        }
    )
    completed = _sse_frame(
        {
            "type": "response.function_call_arguments.completed",
            "item_id": "c3",
            "arguments": json.dumps({"cmd": "cat c3.md"}),
        }
    )
    terminal = _sse_frame({"type": "response.completed"})
    done = b"data: [DONE]\n\n"
    # Split even MID-FRAME across chunks (the frame buffer law).
    head, tail = delta1[:20], delta1[20:]
    ctx.observe_stream_chunk(added)
    assert session.owner.revision == 1  # started: nothing registered
    ctx.observe_stream_chunk(head)
    assert session.owner.revision == 1  # incomplete frame buffered
    ctx.observe_stream_chunk(tail)
    assert session.owner.revision == 1  # one delta: still incomplete
    ctx.observe_stream_chunk(delta2)
    assert session.owner.revision == 1  # accumulated: no completion yet
    ctx.observe_stream_chunk(completed)
    assert session.owner.revision == 2  # the authoritative completion
    snapshot = session.owner.snapshot
    assert snapshot is not None
    d = snapshot.state.d_state
    assert [i.call_id for i in d.issuances] == ["c3"]
    assert d.issuances[0].tool_name == "exec_command"
    ctx.observe_stream_chunk(terminal)
    ctx.observe_stream_chunk(done)
    assert session.owner.revision == 2  # terminal / DONE: no further commit


async def test_streamed_incomplete_and_failed_streams_earn_no_issuance(
    tmp_path: Path,
) -> None:
    captured: list[httpx.Request] = []
    runtime, table, session, context, proof, tx0 = await _bootstrap_ref_session(tmp_path, captured)
    added = _sse_frame(
        {
            "type": "response.output_item.added",
            "item": {
                "id": "fc-c4",
                "type": "function_call",
                "call_id": "c4",
                "name": "exec_command",
            },
        }
    )
    delta = _sse_frame(
        {
            "type": "response.function_call_arguments.delta",
            "item_id": "c4",
            "delta": '{"cmd": "cat c4.md"}',
        }
    )
    # Cut mid-arguments (no completion event): the [DONE] drops the
    # still-incomplete assembly.
    ctx = V1IssuanceContext(
        session=session,
        namespace=session.namespace,
        state=proof.snapshot.state,
        frontier=tx0.represented_frontier,
        endpoint="responses",
    )
    ctx.observe_stream_chunk(added)
    ctx.observe_stream_chunk(delta)
    ctx.observe_stream_chunk(b"data: [DONE]\n\n")
    assert session.owner.revision == 1
    snapshot = session.owner.snapshot
    assert snapshot is not None
    assert snapshot.state.d_state.issuances == ()
    # A terminal response.failed discards everything still in flight.
    ctx2 = V1IssuanceContext(
        session=session,
        namespace=session.namespace,
        state=proof.snapshot.state,
        frontier=tx0.represented_frontier,
        endpoint="responses",
    )
    ctx2.observe_stream_chunk(added)
    ctx2.observe_stream_chunk(delta)
    ctx2.observe_stream_chunk(_sse_frame({"type": "response.failed"}))
    assert session.owner.revision == 1
    snapshot = session.owner.snapshot
    assert snapshot is not None
    assert snapshot.state.d_state.issuances == ()


async def test_nonstream_issuance_negatives(tmp_path: Path) -> None:
    """No issuance from truncated / malformed / non-completed
    evidence on either endpoint family; the Chat ``length`` finish
    reason is explicit truncation; a complete Chat tool call on the
    ``stop`` finish IS the issuance (the positive control)."""
    captured: list[httpx.Request] = []
    runtime, table, session, context, proof, tx0 = await _bootstrap_ref_session(tmp_path, captured)

    def ctx_now() -> V1IssuanceContext:
        return V1IssuanceContext(
            session=session,
            namespace=session.namespace,
            state=proof.snapshot.state,
            frontier=tx0.represented_frontier,
            endpoint="responses",
        )

    # A non-completed Responses object is truncated / incomplete
    # evidence (no issuance, never a guess).
    ctx = ctx_now()
    ctx.observe_nonstream(
        json.dumps(
            {
                "id": "resp-p",
                "status": "in_progress",
                "output": (
                    {
                        "type": "function_call",
                        "id": "fc-p",
                        "call_id": "cp",
                        "name": "exec_command",
                        "arguments": json.dumps({"cmd": "cat cp.md"}),
                    },
                ),
            }
        ).encode("utf-8")
    )
    assert session.owner.revision == 1
    # A function_call whose arguments are not a closed string
    # (a dict) is not a complete binding.
    ctx = ctx_now()
    ctx.observe_nonstream(
        json.dumps(
            {
                "id": "resp-d",
                "status": "completed",
                "output": (
                    {
                        "type": "function_call",
                        "id": "fc-d",
                        "call_id": "cd",
                        "name": "exec_command",
                        "arguments": {"cmd": "cat cd.md"},
                    },
                ),
            }
        ).encode("utf-8")
    )
    assert session.owner.revision == 1
    # A malformed object earns no issuance (and never raises).
    ctx = ctx_now()
    ctx.observe_nonstream(b'{"id": "resp-m", "status": "completed",')
    assert session.owner.revision == 1
    # Chat: the length finish reason is explicit truncation (no
    # issuance even for a well-formed tool call).
    chat_ctx = V1IssuanceContext(
        session=session,
        namespace=session.namespace,
        state=proof.snapshot.state,
        frontier=tx0.represented_frontier,
        endpoint="chat",
    )
    chat_ctx.observe_nonstream(
        json.dumps(
            {
                "id": "chat-l",
                "choices": (
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "tool_calls": (
                                {
                                    "id": "cl",
                                    "type": "function",
                                    "function": {
                                        "name": "exec_command",
                                        "arguments": json.dumps({"cmd": "cat cl.md"}),
                                    },
                                },
                            ),
                        },
                        "finish_reason": "length",
                    },
                ),
            }
        ).encode("utf-8")
    )
    assert session.owner.revision == 1
    # Chat: the complete stop-finished tool call IS the issuance.
    chat_ctx = V1IssuanceContext(
        session=session,
        namespace=session.namespace,
        state=proof.snapshot.state,
        frontier=tx0.represented_frontier,
        endpoint="chat",
    )
    chat_ctx.observe_nonstream(
        json.dumps(
            {
                "id": "chat-s",
                "choices": (
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "tool_calls": (
                                {
                                    "id": "cs",
                                    "type": "function",
                                    "function": {
                                        "name": "exec_command",
                                        "arguments": json.dumps({"cmd": "cat cs.md"}),
                                    },
                                },
                            ),
                        },
                        "finish_reason": "stop",
                    },
                ),
            }
        ).encode("utf-8")
    )
    assert session.owner.revision == 2
    snapshot = session.owner.snapshot
    assert snapshot is not None
    d = snapshot.state.d_state
    assert [(i.call_id, i.endpoint) for i in d.issuances] == [("cs", "chat")]


async def test_issuance_cas_refusal_when_the_owner_drifted(
    tmp_path: Path,
) -> None:
    """The per-request context registers against the COMMITTED-state
    CAS: a drifted owner (a concurrent request committed after this
    request's snapshot) is a fixed refusal -- the observation
    changes nothing and is never retried or rebased."""
    captured: list[httpx.Request] = []
    runtime, table, session, context, proof, tx0 = await _bootstrap_ref_session(tmp_path, captured)
    frozen_frontier = tx0.represented_frontier
    ctx = V1IssuanceContext(
        session=session,
        namespace=session.namespace,
        state=proof.snapshot.state,
        frontier=frozen_frontier,
        endpoint="responses",
    )
    # A concurrent legitimate advance drifts the owner over the
    # context's committed state (an unissued read observation).
    payload = _ref_payload(("c8", "cat c8.md", "D body.\n"))
    obs = observe_request(payload, context=context, endpoint="responses")
    shadow, pre = await prepare_replay_shadow(
        session, runtime, payload=payload, endpoint="responses", observation=obs
    )
    assert pre is None
    assert shadow is not None
    proof_d, refusal = advance_v1_session(
        session, runtime, payload=shadow, endpoint="responses", observation=obs
    )
    assert refusal is None and proof_d is not None
    assert session.owner.revision == 2
    # The drifted context's registration is refused by the CAS: the
    # owner state is unchanged and the context is not rebased.
    ctx.observe_nonstream(_responses_issue_body("c7", "cat c7.md"))
    assert session.owner.revision == 2
    snapshot = session.owner.snapshot
    assert snapshot is not None
    assert snapshot.state.d_state.issuances == ()
    assert ctx.frontier == frozen_frontier
    # The drift advance committed the protected generation; the
    # refused observation added nothing further.
    assert session.bare_session is not None
    assert session.bare_session.current_generation() == 2


async def test_tampered_marker_is_refused_before_raw_acquisition(tmp_path: Path) -> None:
    """The marker-side atomicity at the app seam: a tampered tag in
    the resent transformed payload is the fixed typed 409 refusal
    with NO raw acquisition committed (the same law the stale
    superseded-marker case exercises once the order section 3
    issuance wiring admits the read)."""
    runtime = _runtime(tmp_path)
    table = V1SessionTable()
    identity, route, contract = _identity(), _route(), _contract()
    address = build_session_address(runtime, identity, route, contract)
    bootstrap = _root_payload()
    session = await establish_v1_session(
        runtime,
        table,
        address=address,
        identity=identity,
        route=route,
        contract=contract,
        observation=observe_request(bootstrap, endpoint="responses"),
        payload=bootstrap,
        endpoint="responses",
    )
    assert session is not None and not isinstance(session, V1RequestRefusal)
    context = PathContext(workspace=WORKSPACE)
    payload2 = _root_payload(("c1", "A body.\n"))
    obs2 = observe_request(payload2, context=context, endpoint="responses")
    proof, refusal = advance_v1_session(
        session, runtime, payload=payload2, endpoint="responses", observation=obs2
    )
    assert refusal is None and proof is not None
    tx1 = await prepare_v1_transaction(
        session, runtime, payload=payload2, endpoint="responses", observation=obs2, proof=proof
    )
    assert not isinstance(tx1, V1RequestRefusal)
    round1_body = tx1.body
    # Flip ONE character inside the root LIVE tag: the tag no longer
    # authenticates under the application marker key (forged /
    # tampered replay).
    tag_start = round1_body.find(b"[slaif-live:v")
    assert tag_start != -1
    flip = tag_start + 20  # well inside the base64url tag body
    assert round1_body[flip : flip + 1] not in b"[]"
    flipped = b"A" if round1_body[flip : flip + 1] != b"A" else b"B"
    tampered = json.loads(round1_body[:flip] + flipped + round1_body[flip + 1 :])
    obs_t = observe_request(tampered, context=context, endpoint="responses")
    shadow, pre = await prepare_replay_shadow(
        session, runtime, payload=tampered, endpoint="responses", observation=obs_t
    )
    assert shadow is None
    assert pre is not None
    assert pre.reason is V1RequestReason.TRANSACTION_CONFLICT
    assert pre.status_code == 409
    assert pre.code == "v1_transaction_conflict"
    # The tampered payload's raw acquisition was never committed.
    assert session.owner.revision == 2
    assert session.bare_session is not None
    assert session.bare_session.current_generation() == 2


async def test_resumed_session_materializes_publish_and_replays_the_fixed_point(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path)
    table = V1SessionTable()
    identity, route, contract = _identity(), _route(), _contract()
    address = build_session_address(runtime, identity, route, contract)
    bootstrap = _root_payload()
    session = await establish_v1_session(
        runtime,
        table,
        address=address,
        identity=identity,
        route=route,
        contract=contract,
        observation=observe_request(bootstrap, endpoint="responses"),
        payload=bootstrap,
        endpoint="responses",
    )
    assert session is not None and not isinstance(session, V1RequestRefusal)
    context = PathContext(workspace=WORKSPACE)
    payload2 = _root_payload(("c1", "A body.\n"))
    obs2 = observe_request(payload2, context=context, endpoint="responses")
    proof, refusal = advance_v1_session(
        session, runtime, payload=payload2, endpoint="responses", observation=obs2
    )
    assert refusal is None and proof is not None
    tx1 = await prepare_v1_transaction(
        session, runtime, payload=payload2, endpoint="responses", observation=obs2, proof=proof
    )
    assert not isinstance(tx1, V1RequestRefusal)
    round1_body = tx1.body
    transformed = json.loads(round1_body)
    # The process restart: the writer is released and a FRESH process
    # runtime resumes the SAME address from the protected store.
    assert session.bare_session is not None
    session.bare_session.close()
    runtime2 = _runtime(tmp_path)
    table2 = V1SessionTable()
    resumed = await establish_v1_session(
        runtime2,
        table2,
        address=address,
        identity=identity,
        route=route,
        contract=contract,
        observation=observe_request(bootstrap, endpoint="responses"),
        payload=bootstrap,
        endpoint="responses",
    )
    assert resumed is not None and not isinstance(resumed, V1RequestRefusal)
    assert resumed.last_publish is None
    assert resumed.session_owner is not None
    # The client resends the transformed round: the pre-check
    # materializes the retained protected generation NOW (the resumed
    # session's first hit) and unsplices the shadow.
    obs_t = observe_request(transformed, context=context, endpoint="responses")
    shadow, pre = await prepare_replay_shadow(
        resumed, runtime2, payload=transformed, endpoint="responses", observation=obs_t
    )
    assert pre is None
    assert shadow is not None
    # Unspliced to the retained originals at the source spans; the
    # stable compiled-context region is ordinary request text that
    # passes the shadow through unchanged (order 022-d section 3).
    expected_shadow = json.loads(json.dumps(payload2))
    expected_shadow["instructions"] = transformed["instructions"]
    assert shadow == expected_shadow
    assert resumed.last_publish is not None
    assert resumed.last_publish.limitation is RecoveryStoreLimitation.OK
    # The resume's durable epoch binding moved the bound generation
    # to three; the materialized checkpoint publishes the restored
    # record set at four.
    assert resumed.last_publish.generation == 4
    proof2, refusal2 = advance_v1_session(
        resumed, runtime2, payload=shadow, endpoint="responses", observation=obs_t
    )
    assert refusal2 is None and proof2 is not None
    # The ordinary hit reuses the materialized publication: the
    # restored record set (the owner commit fence restarted at one
    # over the P-state region revision two).
    assert proof2.publish.generation == 4
    assert proof2.snapshot.revision == 1
    assert proof2.snapshot.state.revision == 2
    # The transaction over the ACTUAL payload under the materialized
    # retained proof: the fixed point holds across the restart.
    tx2 = await prepare_v1_transaction(
        resumed,
        runtime2,
        payload=transformed,
        endpoint="responses",
        observation=obs_t,
        proof=proof2,
    )
    assert not isinstance(tx2, V1RequestRefusal)
    assert tx2.outcome is ReplacementOutcome.OK
    assert tx2.edits_committed == 0
    assert tx2.markers_replayed == 1
    assert tx2.body == round1_body
