"""021 pinned tokenizer / bundle compiler / selection: the
fake-upstream compiler controls.

FIRST INCREMENT (saved): the authenticated TOOL-FREE direct
compiler request shape over ACTUAL P/T records and the validated
success path counted with the REAL pinned tokenizer (the root
entry with its deterministic candidate and the 1:1 attributable
file entry; the credential is a protected environment reference
that never enters the prompt; exactly one upstream call per
compile; the retained payload round-trips the strict schema).
The ordered error / truncation / attribution-fence /
empty-source / no-retry / single-flight / recovery / selection
cases follow in this same file for the same active order.

The stage stays inert: no adapter wiring, no configuration key,
no v1 runtime activation.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest

from slaif_local_coding.constitution.bundles.bundle_admission_models import (
    AdmissionMode,
)
from slaif_local_coding.constitution.bundles.bundle_budget import (
    BundleBudgetConfig,
    BundleBudgetPlan,
)
from slaif_local_coding.constitution.bundles.bundle_compiler import (
    BUNDLE_COMPILER_PROMPT_POLICY_VERSION,
    BUNDLE_COMPILER_SCHEMA_VERSION,
    BUNDLE_COMPILER_VERSION,
    BundleCompiledDependency,
    BundleCompiledIndex,
    BundleCompiledRule,
    BundleCompiler,
    BundleCompilerAccount,
    BundleCompilerConfig,
    BundleCompilerOutcome,
    derive_compile_key,
    deserialize_compiled_index,
    entry_source,
    render_compiled_index,
    serialize_compiled_index,
)
from slaif_local_coding.constitution.bundles.bundle_tokenizer import (
    PINNED_TOKENIZER_REVISION,
    get_bundle_tokenizer,
)
from slaif_local_coding.constitution.bundles.causal_history_models import (
    CAUSAL_ROOT_FACT,
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
from tests.test_causal_history import (
    ENDPOINTS,
    MODES,
    read_request,
)
from tests.test_root_region_lineage import r_bootstrap, r_issue, r_observe

COMPILER_MODEL = "Qwen3.8-27B"
COMPILER_BASE_URL = "http://127.0.0.1:18031/v1"
COMPILER_KEY_ENV = "SLAIF_021_TEST_COMPILER_KEY"
COMPILER_KEY_VALUE = "test-compiler-credential"
# The declared immutable revision the serving model is declared to
# run at (the pinned upstream revision) and the opaque configured
# upstream-compatibility identity: the declared compatibility facts.
COMPILER_MODEL_REVISION = PINNED_TOKENIZER_REVISION
COMPILER_COMPATIBILITY_IDENTITY = "qwen38-27b-rtx3090-ref"
ROOT_BODY = "Follow `A.md` before mutation.\n"
A_BODY = "NEVER mutate the protected fixture.\n"


def _dep_read(state: Any, ns: Any, cid: str, endpoint: str, path: str, body: str) -> Any:
    issued = r_issue(state, ns, cid, endpoint, (CAUSAL_ROOT_FACT,), f"cat {path}")
    assert issued.outcome is RootLineageOutcome.ACCEPTED, issued.diagnostics
    obs = r_observe(issued.state, ns, (read_request(endpoint, cid, body, f"cat {path}"),))
    assert obs.outcome is RootLineageOutcome.ACCEPTED, obs.diagnostics
    return obs.state


def _mini_states(mode: AdmissionMode, endpoint: str, lineage: str) -> Any:
    """The ACTUAL P/T fixture: the root referencing ``A.md`` and
    the genuinely issued ``cat A.md`` read (both admitted under
    the accepted T law)."""
    ns, s0 = r_bootstrap(mode, lineage, root_body=ROOT_BODY)
    state = _dep_read(s0, ns, "a", endpoint, "A.md", A_BODY)
    t = derive_root_region_admission(state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    return ns, state, t


def _entry_for(t: Any, path: str) -> Any:
    adm = t.admission
    assert adm is not None
    rows = [row for row in adm.path_associations if row.path == path]
    assert len(rows) == 1 and len(rows[0].content_keys) == 1
    key = rows[0].content_keys[0]
    if adm.root_entry.content_key == key:
        return adm.root_entry
    for entry in adm.entries:
        if entry.content_key == key:
            return entry
    raise AssertionError("the admitted entry for the path is missing")


def _completion_bytes(content: str, finish_reason: str = "stop") -> bytes:
    return json.dumps(
        {
            "id": "chatcmpl-021",
            "object": "chat.completion",
            "model": COMPILER_MODEL,
            "choices": (
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": finish_reason,
                },
            ),
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }
    ).encode("utf-8")


def _expected_index(
    *,
    entry: Any,
    source_digest: str,
    source_byte_length: int,
    compile_key: str,
    candidates: tuple[str, ...],
    rules: tuple[BundleCompiledRule, ...],
    scopes: tuple[str, ...],
    authorities: tuple[str, ...],
    boundaries: tuple[str, ...],
    triggers: tuple[str, ...],
) -> BundleCompiledIndex:
    return BundleCompiledIndex(
        schema_version=BUNDLE_COMPILER_SCHEMA_VERSION,
        compiler_version=BUNDLE_COMPILER_VERSION,
        prompt_policy_version=BUNDLE_COMPILER_PROMPT_POLICY_VERSION,
        model=COMPILER_MODEL,
        entry_class=entry.entry_class,
        content_key=entry.content_key,
        compile_key=compile_key,
        source_sha256=source_digest,
        source_byte_length=source_byte_length,
        summary="Bounded synthetic summary.",
        rules=rules,
        scopes=scopes,
        authorities=authorities,
        source_of_truth_boundaries=boundaries,
        dependencies=tuple(
            BundleCompiledDependency(
                path=path,
                reference_confidence=0.9,
                constitutional_priority=80,
                classification="P1",
                relationship="root-referenced",
                evidence="referenced by the governing root",
                acquisition_urgency="immediate",
            )
            for path in candidates
        ),
        reread_triggers=triggers,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_happy_path_request_shape_and_validated_output(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The ACTUAL direct compiler demand over the real P/T
    records: the authenticated tool-free request shape (exact
    JSON body, protected credential reference, no tools, no
    recursion), exactly ONE upstream call, the structured output
    validated against the ACTUAL source and FULL key, the final
    rendered block counted with the REAL pinned tokenizer against
    the ACTUAL width x slot allowance, and the retained payload's
    strict round-trip."""
    ns, _state, t = _mini_states(mode, endpoint, f"compiler021-happy-{mode.value}-{endpoint}")
    root_entry = t.admission.root_entry
    file_entry = _entry_for(t, "A.md")

    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    config = BundleCompilerConfig(
        model=COMPILER_MODEL,
        base_url=COMPILER_BASE_URL,
        model_revision=COMPILER_MODEL_REVISION,
        compatibility_identity=COMPILER_COMPATIBILITY_IDENTITY,
        api_key_env=COMPILER_KEY_ENV,
    )
    tokenizer = get_bundle_tokenizer()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=262_144))

    demands: list[tuple[Any, tuple[str, ...], BundleCompiledIndex]] = []
    for entry, candidates in (
        (root_entry, ("A.md",)),
        (file_entry, ()),
    ):
        source_text, source_digest, source_byte_length = entry_source(entry)
        if entry is root_entry:
            assert source_text == ROOT_BODY
        else:
            assert source_text == A_BODY
        compile_key = derive_compile_key(
            entry_class=entry.entry_class,
            content_key=entry.content_key,
            source_sha256=source_digest,
            source_byte_length=source_byte_length,
            candidate_paths=candidates,
            config_identity=config.config_identity,
            tokenizer_identity=tokenizer.binding.identity,
            budget_identity=plan.plan_identity(),
            render_policy_version=tokenizer.binding.render_policy_version,
        )
        if entry is root_entry:
            index = _expected_index(
                entry=entry,
                source_digest=source_digest,
                source_byte_length=source_byte_length,
                compile_key=compile_key,
                candidates=candidates,
                rules=(
                    BundleCompiledRule(
                        rule_id="follow-a-before-mutation",
                        strength="must",
                        statement="Follow A.md before mutation.",
                        location="root line 1",
                        evidence="Follow `A.md` before mutation.",
                    ),
                ),
                scopes=("workspace root",),
                authorities=("governing root",),
                boundaries=("repository source files",),
                triggers=("root source change",),
            )
        else:
            index = _expected_index(
                entry=entry,
                source_digest=source_digest,
                source_byte_length=source_byte_length,
                compile_key=compile_key,
                candidates=candidates,
                rules=(
                    BundleCompiledRule(
                        rule_id="never-mutate-fixture",
                        strength="never",
                        statement="NEVER mutate the protected fixture.",
                        location="A.md",
                        evidence="NEVER mutate the protected fixture.",
                    ),
                ),
                scopes=("file A.md content",),
                authorities=("file A.md provenance",),
                boundaries=("repository source files",),
                triggers=("A.md source change",),
            )
        demands.append((entry, candidates, index))

    captured: list[httpx.Request] = []
    payloads = {
        index.content_key: serialize_compiled_index(index).decode("utf-8")
        for _entry, _candidates, index in demands
    }

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        body = json.loads(request.content)
        user = body["messages"][1]["content"]
        for content_key, payload in payloads.items():
            if f"content_key={content_key!r}" in user:
                return httpx.Response(200, content=_completion_bytes(payload))
        raise AssertionError("the fake upstream received an unknown demand")

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    compiler = BundleCompiler(config, client=client)
    account = BundleCompilerAccount()
    try:
        for position, (entry, demand_candidates, expected) in enumerate(demands, start=1):
            result = await compiler.compile_entry(
                entry=entry,
                candidate_paths=demand_candidates,
                tokenizer=tokenizer,
                budget_identity=plan.plan_identity(),
                rendered_allowance=plan.entry_allowance(entry.width),
                account=account,
            )
            assert result.outcome is BundleCompilerOutcome.COMPLETED, result.detail
            assert result.attempts == 1
            assert result.index == expected
            # Exactly one upstream call per compile so far:
            assert len(captured) == position
            request = captured[-1]
            assert request.method == "POST"
            assert request.url == f"{COMPILER_BASE_URL}/chat/completions"
            assert request.headers["authorization"] == f"Bearer {COMPILER_KEY_VALUE}"
            assert request.headers["content-type"] == "application/json"
            body = json.loads(request.content)
            assert body["model"] == COMPILER_MODEL
            assert body["stream"] is False
            assert body["temperature"] == 0
            assert body["max_tokens"] == config.max_output_tokens
            assert body["reasoning_effort"] == "low"
            # Tool-free, nonrecursive, no Gateway credential:
            assert "tools" not in body
            assert [m["role"] for m in body["messages"]] == ["system", "user"]
            system_text = body["messages"][0]["content"]
            user_text = body["messages"][1]["content"]
            # Identity-bound prompt: the ACTUAL source digest, the
            # FULL compile key, the exact source text and the
            # deterministic candidates:
            assert f"sha256={expected.source_sha256}" in user_text
            assert f"compile_key={expected.compile_key!r}" in user_text
            assert expected.source_sha256 and expected.source_byte_length >= 0
            assert f"byte_length={expected.source_byte_length}" in user_text
            assert (ROOT_BODY if entry is root_entry else A_BODY) in user_text
            for path in demand_candidates:
                assert f'"path":"{path}"' in user_text
            # The protected credential never enters the prompt:
            assert COMPILER_KEY_VALUE not in system_text + user_text
            # The REAL pinned tokenizer counts the final rendered
            # block (references, metadata and separators included)
            # against the ACTUAL width x slot allowance:
            block = tokenizer.render_compiled_block(
                entry_label=f"entry-{entry.content_key[:16]}",
                body=render_compiled_index(expected),
                references=demand_candidates,
            )
            allowance = plan.entry_allowance(entry.width)
            assert 0 < tokenizer.count_tokens(block) <= allowance
            # The retained payload round-trips the strict schema:
            assert (
                deserialize_compiled_index(
                    serialize_compiled_index(expected),
                    max_json_depth=config.max_json_depth,
                )
                == expected
            )
    finally:
        await compiler.aclose()
        await client.aclose()

    facts = account.as_dict()
    assert facts["upstream_calls"] == 2
    assert facts["outcome_counts"] == {"completed": 2}
    assert facts["prompt_bytes"] > 0
    assert facts["output_bytes"] > 0


# -- second increment: the ordered error battery, the P/T ownership
# attribution fence and the truthful empty-source output -----------


async def _compile_once(
    *,
    config: BundleCompilerConfig,
    entry: Any,
    candidates: tuple[str, ...],
    tokenizer: Any,
    plan: Any,
    responder: Callable[[httpx.Request, list[Any]], httpx.Response],
    rendered_allowance: int | None = None,
) -> tuple[Any, list[Any]]:
    """One bounded compile against a canned fake-upstream responder
    (the responder sees the actual request and returns a canned
    completion); returns (result, captured requests)."""
    captured: list[Any] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return responder(request, captured)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    compiler = BundleCompiler(config, client=client)
    try:
        result = await compiler.compile_entry(
            entry=entry,
            candidate_paths=candidates,
            tokenizer=tokenizer,
            budget_identity=plan.plan_identity(),
            rendered_allowance=(
                rendered_allowance
                if rendered_allowance is not None
                else plan.entry_allowance(entry.width)
            ),
        )
    finally:
        await compiler.aclose()
        await client.aclose()
    return result, captured


def _valid_payload(
    *,
    entry: Any,
    candidates: tuple[str, ...],
    config: BundleCompilerConfig,
    tokenizer: Any,
    plan: Any,
    overrides: dict[str, Any] | None = None,
    finish_reason: str = "stop",
    content: str | None = None,
) -> bytes:
    """The canned completion over the ACTUAL demand facts (or the
    canned raw ``content`` when a malformed output is the point)."""
    if content is not None:
        return _completion_bytes(content, finish_reason=finish_reason)
    source_text, source_digest, source_byte_length = entry_source(entry)
    compile_key = derive_compile_key(
        entry_class=entry.entry_class,
        content_key=entry.content_key,
        source_sha256=source_digest,
        source_byte_length=source_byte_length,
        candidate_paths=candidates,
        config_identity=config.config_identity,
        tokenizer_identity=tokenizer.binding.identity,
        budget_identity=plan.plan_identity(),
        render_policy_version=tokenizer.binding.render_policy_version,
    )
    empty = source_byte_length == 0
    index = BundleCompiledIndex(
        schema_version=BUNDLE_COMPILER_SCHEMA_VERSION,
        compiler_version=BUNDLE_COMPILER_VERSION,
        prompt_policy_version=BUNDLE_COMPILER_PROMPT_POLICY_VERSION,
        model=config.model,
        entry_class=entry.entry_class,
        content_key=entry.content_key,
        compile_key=compile_key,
        source_sha256=source_digest,
        source_byte_length=source_byte_length,
        summary=overrides.get("summary", "")
        if overrides and empty
        else ("Bounded synthetic summary." if not empty else ""),
        rules=()
        if empty
        else (
            BundleCompiledRule(
                rule_id="synthetic-rule",
                strength="never",
                statement="NEVER skip the synthetic governance.",
                location="A.md" if entry.entry_class.value == "file_bundle_entry" else "",
                evidence="synthetic source evidence",
            ),
        ),
        scopes=() if empty else ("synthetic scope",),
        authorities=() if empty else ("synthetic provenance",),
        source_of_truth_boundaries=() if empty else ("repository source files",),
        dependencies=()
        if empty
        else tuple(
            BundleCompiledDependency(
                path=path,
                reference_confidence=0.9,
                constitutional_priority=80,
                classification="P1",
                relationship="root-referenced",
                evidence="referenced by the governing root",
                acquisition_urgency="immediate",
            )
            for path in candidates
        ),
        reread_triggers=() if empty else ("source change",),
    )
    if overrides:
        fields = index.model_dump(mode="json")
        fields.update(overrides)
        index = BundleCompiledIndex.model_validate(fields)
    return _completion_bytes(json.dumps(index.model_dump(mode="json"), separators=(",", ":")))


def _config(**overrides: Any) -> BundleCompilerConfig:
    fields: dict[str, Any] = {
        "model": COMPILER_MODEL,
        "base_url": COMPILER_BASE_URL,
        "model_revision": COMPILER_MODEL_REVISION,
        "compatibility_identity": COMPILER_COMPATIBILITY_IDENTITY,
        "api_key_env": COMPILER_KEY_ENV,
    }
    fields.update(overrides)
    return BundleCompilerConfig(**fields)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_zero_upstream_refusals(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The zero-upstream-work refusals (closed vocabulary, exact
    reasons, zero calls): a detached demand, the exact empty source
    carrying deterministic candidates, the oversize prompt and the
    missing protected credential."""
    ns, _state, t = _mini_states(mode, endpoint, f"compiler021-refuse-{mode.value}-{endpoint}")
    root_entry = t.admission.root_entry
    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    config = _config()
    tokenizer = get_bundle_tokenizer()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=262_144))

    result, captured = await _compile_once(
        config=config,
        entry=object(),
        candidates=(),
        tokenizer=tokenizer,
        plan=plan,
        rendered_allowance=plan.entry_allowance(root_entry.width),
        responder=lambda request, _seen: httpx.Response(200, content=_completion_bytes("{}")),
    )
    assert result.outcome is BundleCompilerOutcome.INPUT_INVALID
    assert result.attempts == 0 and captured == []

    # The EXACT empty source (zero bytes) carrying deterministic
    # candidates is refused before any upstream work:
    ns_empty, s_empty = r_bootstrap(
        mode,
        f"compiler021-refuse-empty-{mode.value}-{endpoint}",
        root_body="",
    )
    t_empty = derive_root_region_admission(s_empty, ns_empty)
    assert t_empty.outcome is RootRegionAdmissionOutcome.READY, t_empty.diagnostics
    assert t_empty.admission is not None
    empty_root_entry = t_empty.admission.root_entry
    result, captured = await _compile_once(
        config=config,
        entry=empty_root_entry,
        candidates=("A.md",),
        tokenizer=tokenizer,
        plan=plan,
        responder=lambda request, _seen: httpx.Response(200, content=_completion_bytes("{}")),
    )
    assert result.outcome is BundleCompilerOutcome.INPUT_INVALID
    assert result.attempts == 0 and captured == []

    small = _config(max_prompt_bytes=1_024)
    result, captured = await _compile_once(
        config=small,
        entry=root_entry,
        candidates=(),
        tokenizer=tokenizer,
        plan=plan,
        responder=lambda request, _seen: httpx.Response(200, content=_completion_bytes("{}")),
    )
    assert result.outcome is BundleCompilerOutcome.INPUT_TOO_LARGE
    assert result.attempts == 0 and captured == []
    assert result.prompt_bytes > 1_024

    no_key = _config(api_key_env="SLAIF_021_UNSET_COMPILER_KEY")
    monkeypatch.delenv("SLAIF_021_UNSET_COMPILER_KEY", raising=False)
    result, captured = await _compile_once(
        config=no_key,
        entry=root_entry,
        candidates=(),
        tokenizer=tokenizer,
        plan=plan,
        responder=lambda request, _seen: httpx.Response(200, content=_completion_bytes("{}")),
    )
    assert result.outcome is BundleCompilerOutcome.AUTH_UNAVAILABLE
    assert result.attempts == 0 and captured == []


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_upstream_failure_battery(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The ACTUAL upstream failure states over the real channel:
    non-2xx status, timeout, transport error and over-bound output
    -- each exactly ONE attempt, none an entry or a hit."""
    ns, _state, t = _mini_states(mode, endpoint, f"compiler021-upstream-{mode.value}-{endpoint}")
    root_entry = t.admission.root_entry
    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    config = _config()
    tokenizer = get_bundle_tokenizer()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=262_144))

    result, captured = await _compile_once(
        config=config,
        entry=root_entry,
        candidates=(),
        tokenizer=tokenizer,
        plan=plan,
        responder=lambda request, _seen: httpx.Response(500, content=b"boom"),
    )
    assert result.outcome is BundleCompilerOutcome.UPSTREAM_STATUS
    assert result.attempts == 1 and len(captured) == 1
    assert "500" in result.detail

    async def slow_handler(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(0.25)
        return httpx.Response(200, content=_completion_bytes("{}"))

    captured_slow: list[Any] = []

    def slow_wrap(request: httpx.Request) -> httpx.Response:
        captured_slow.append(request)
        raise AssertionError("the slow handler must be async")

    client = httpx.AsyncClient(transport=httpx.MockTransport(slow_handler))
    compiler = BundleCompiler(_config(timeout_seconds=0.05), client=client)
    try:
        result = await compiler.compile_entry(
            entry=root_entry,
            candidate_paths=(),
            tokenizer=tokenizer,
            budget_identity=plan.plan_identity(),
            rendered_allowance=plan.entry_allowance(root_entry.width),
        )
    finally:
        await compiler.aclose()
        await client.aclose()
    assert result.outcome is BundleCompilerOutcome.UPSTREAM_TIMEOUT
    assert result.attempts == 1
    assert captured_slow == []

    def broken(request: httpx.Request, _seen: list[Any]) -> httpx.Response:
        raise httpx.ConnectError("synthetic transport failure")

    result, captured = await _compile_once(
        config=config,
        entry=root_entry,
        candidates=(),
        tokenizer=tokenizer,
        plan=plan,
        responder=broken,
    )
    assert result.outcome is BundleCompilerOutcome.UPSTREAM_TRANSPORT
    assert result.attempts == 1 and len(captured) == 1

    oversized = _config(max_output_bytes=1_024)
    big = json.dumps({"pad": "x" * 2_048}).encode("utf-8")
    result, captured = await _compile_once(
        config=oversized,
        entry=root_entry,
        candidates=(),
        tokenizer=tokenizer,
        plan=plan,
        responder=lambda request, _seen: httpx.Response(200, content=big),
    )
    assert result.outcome is BundleCompilerOutcome.OUTPUT_TOO_LARGE
    assert result.attempts == 1 and len(captured) == 1


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_output_validation_battery(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The closed output states over the ACTUAL validated channel:
    provider truncation typed BEFORE content validation, invalid
    JSON, nesting over the bound, identity / digest / candidate-set
    mismatches, the two-score contradiction, the closed schema and
    the over-allowance typed refusal (never a truncation)."""
    ns, _state, t = _mini_states(mode, endpoint, f"compiler021-output-{mode.value}-{endpoint}")
    root_entry = t.admission.root_entry
    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    tokenizer = get_bundle_tokenizer()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=262_144))

    def responder_for(payload: bytes) -> Callable[[httpx.Request, list[Any]], httpx.Response]:
        return lambda request, _seen: httpx.Response(200, content=payload)

    base = dict(
        entry=root_entry,
        candidates=(),
        tokenizer=tokenizer,
        plan=plan,
    )

    # Truncation: a FINISH_REASONS=length with perfectly valid JSON
    # content is typed BEFORE any content validation.
    valid = _valid_payload(
        entry=root_entry,
        candidates=(),
        config=_config(),
        tokenizer=tokenizer,
        plan=plan,
    )
    truncated = _completion_bytes(
        json.loads(valid.decode("utf-8"))["choices"][0]["message"]["content"],
        finish_reason="length",
    )
    result, _captured = await _compile_once(
        config=_config(), responder=responder_for(truncated), **base
    )
    assert result.outcome is BundleCompilerOutcome.OUTPUT_TRUNCATED
    assert result.attempts == 1 and result.index is None

    # Invalid JSON content:
    result, _ = await _compile_once(
        config=_config(),
        responder=responder_for(_completion_bytes("this is not json")),
        **base,
    )
    assert result.outcome is BundleCompilerOutcome.INVALID_JSON
    assert result.attempts == 1

    # Nesting over the bound (the envelope stays shallow; the content
    # JSON is deep):
    deep_value: dict[str, Any] = {"leaf": 1}
    for _ in range(12):
        deep_value = {"stack": deep_value}
    deep = json.dumps(deep_value)
    result, _ = await _compile_once(
        config=_config(max_json_depth=6),
        responder=responder_for(_completion_bytes(deep)),
        **base,
    )
    assert result.outcome is BundleCompilerOutcome.NESTING_TOO_DEEP
    assert result.attempts == 1

    # The forbidden combined score key:
    combined = '{"combined_score":0.9,"schema_version":"' + BUNDLE_COMPILER_SCHEMA_VERSION + '"}'
    result, _ = await _compile_once(
        config=_config(),
        responder=responder_for(_completion_bytes(combined)),
        **base,
    )
    assert result.outcome is BundleCompilerOutcome.CONTRADICTORY_OUTPUT

    # Identity mismatch: the wrong content key:
    result, _ = await _compile_once(
        config=_config(),
        responder=responder_for(
            _valid_payload(
                entry=root_entry,
                candidates=(),
                config=_config(),
                tokenizer=tokenizer,
                plan=plan,
                overrides={"content_key": "f" * 64},
            )
        ),
        **base,
    )
    assert result.outcome is BundleCompilerOutcome.IDENTITY_MISMATCH

    # Source digest mismatch:
    result, _ = await _compile_once(
        config=_config(),
        responder=responder_for(
            _valid_payload(
                entry=root_entry,
                candidates=(),
                config=_config(),
                tokenizer=tokenizer,
                plan=plan,
                overrides={"source_sha256": "e" * 64},
            )
        ),
        **base,
    )
    assert result.outcome is BundleCompilerOutcome.SOURCE_HASH_MISMATCH

    # Candidate-set mismatch: the demand carries A.md, the output
    # carries A.md plus an invented B.md:
    with_candidate = _valid_payload(
        entry=root_entry,
        candidates=("A.md",),
        config=_config(),
        tokenizer=tokenizer,
        plan=plan,
        overrides={"dependencies": []},
    )
    result, _ = await _compile_once(
        config=_config(),
        responder=responder_for(with_candidate),
        **{**base, "candidates": ("A.md",)},
    )
    assert result.outcome is BundleCompilerOutcome.CANDIDATE_SET_MISMATCH

    # The two-score contradiction: an authoritative P1 with low
    # reference confidence:
    contradiction = _valid_payload(
        entry=root_entry,
        candidates=("A.md",),
        config=_config(),
        tokenizer=tokenizer,
        plan=plan,
        overrides={
            "dependencies": [
                {
                    "path": "A.md",
                    "reference_confidence": 0.4,
                    "constitutional_priority": 80,
                    "classification": "P1",
                    "relationship": "root-referenced",
                    "evidence": "referenced by the governing root",
                    "acquisition_urgency": "immediate",
                }
            ]
        },
    )
    result, _ = await _compile_once(
        config=_config(),
        responder=responder_for(contradiction),
        **{**base, "candidates": ("A.md",)},
    )
    assert result.outcome is BundleCompilerOutcome.CONTRADICTORY_OUTPUT

    # Closed schema: a non-empty source compiled with zero rules is
    # a silent governance wipe.  The closed model refuses to
    # construct such an index, so the payload is built by mutating
    # the dumped dict of a valid payload WITHOUT schema
    # revalidation; the compiler must type it SCHEMA_INVALID over
    # the real channel:
    wipe_base = _valid_payload(
        entry=root_entry,
        candidates=(),
        config=_config(),
        tokenizer=tokenizer,
        plan=plan,
    )
    wipe_fields = json.loads(
        json.loads(wipe_base.decode("utf-8"))["choices"][0]["message"]["content"]
    )
    wipe_fields.update(
        {
            "rules": [],
            "scopes": [],
            "authorities": [],
            "source_of_truth_boundaries": [],
            "reread_triggers": [],
            "summary": "",
        }
    )
    wipe = _completion_bytes(json.dumps(wipe_fields, separators=(",", ":")))
    result, _ = await _compile_once(config=_config(), responder=responder_for(wipe), **base)
    assert result.outcome is BundleCompilerOutcome.SCHEMA_INVALID

    # Over-allowance: the rendered block is typed invalid, never
    # truncated:
    result, _ = await _compile_once(
        config=_config(),
        responder=responder_for(
            _valid_payload(
                entry=root_entry,
                candidates=(),
                config=_config(),
                tokenizer=tokenizer,
                plan=plan,
            )
        ),
        rendered_allowance=1,
        **base,
    )
    assert result.outcome is BundleCompilerOutcome.OVER_ALLOWANCE
    assert result.index is None
