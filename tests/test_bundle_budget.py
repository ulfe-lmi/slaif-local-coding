"""Permanent 021 budget matrix (contract
``docs/CACHE-TOKEN-COMPILER-CONTRACT.md``, budget half).

The explicit validated context budget: the effective ``C`` is
CONFIGURED (never inferred); base slot ``floor(C/32)``; bundle
width the DISTINCT represented file count (repeated operands
never inflate it); allowance ``width x slot``; aggregate
``floor(C/4)``; generation ``max(4096, floor(C/8))``; tools
2048; uncertainty/template 1024.  The final rendered compiled
text and the remaining request content are counted with the
REAL pinned tokenizer (no padding, no silent truncation); the
fixed template framing is charged with the closed conservative
numeric overheads; byte limits stay INDEPENDENT of tokens; the
caller-requested generation is respected, never lowered; the
per-retained-image reserve requires the explicit vision
contract (a positive image count on a nonvision config
rejects).

INERT component: no request-pipeline wiring, no v1 runtime.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

from slaif_local_coding.constitution.bundles.bundle_budget import (
    BUDGET_AGGREGATE_DIVISOR,
    BUDGET_GENERATION_DIVISOR,
    BUDGET_GENERATION_FLOOR,
    BUDGET_SLOT_DIVISOR,
    BUDGET_TOOLS_RESERVE_DEFAULT,
    BUDGET_UNCERTAINTY_RESERVE_DEFAULT,
    ENVELOPE_THINK_FRAMING_BOUND_TOKENS,
    ENVELOPE_TOOL_REMINDER_BOUND_TOKENS,
    ENVELOPE_TOOLS_PREFIX_BOUND_TOKENS,
    ENVELOPE_TOOLS_SUFFIX_BOUND_TOKENS,
    BudgetEntry,
    BudgetMessage,
    BudgetOutcome,
    BudgetToolCall,
    BudgetToolSpec,
    BundleBudgetConfig,
    BundleBudgetError,
    BundleBudgetPlan,
    BundleBudgetReason,
)
from slaif_local_coding.constitution.bundles.bundle_tokenizer import (
    _IM_END,
    _IM_START,
    BundleTokenizer,
    get_bundle_tokenizer,
)

C_VALUES = (262_144, 32_768, 40_000)


def _config(**overrides: Any) -> BundleBudgetConfig:
    fields: dict[str, Any] = {"context_tokens": 32_768}
    fields.update(overrides)
    return BundleBudgetConfig(**fields)


@pytest.fixture(scope="module")
def tokenizer() -> BundleTokenizer:
    return get_bundle_tokenizer()


def _plan(config: BundleBudgetConfig, tokenizer: BundleTokenizer) -> BundleBudgetPlan:
    return BundleBudgetPlan(tokenizer, config)


def _entry(
    label: str,
    body: str,
    *,
    required: bool = True,
    files: int = 1,
) -> BudgetEntry:
    return BudgetEntry(
        label=label,
        required=required,
        distinct_files=files,
        rendered_block=body,
    )


def _body_at_least_tokens(tokenizer: BundleTokenizer, target: int) -> str:
    """A deterministic body whose REAL whole-string token count >= target.

    BPE is not additive over chunks, so the count is measured on the
    WHOLE growing body (appended in bounded blocks), never on the
    per-chunk sum.
    """
    chunks: list[str] = []
    i = 0
    while True:
        for _ in range(64):
            chunks.append(f"filler-{i:06d} ")
            i += 1
        body = "".join(chunks)
        if i >= 8_192:
            raise AssertionError("body fill did not converge")
        if tokenizer.count_tokens(body) >= target:
            return body


# -- explicit C: the ordered formulas -----------------------------------


@pytest.mark.parametrize("c", C_VALUES)
def test_explicit_c_formulas(tokenizer: BundleTokenizer, c: int) -> None:
    cfg = _config(context_tokens=c)
    assert cfg.slot == c // BUDGET_SLOT_DIVISOR
    assert cfg.aggregate == c // BUDGET_AGGREGATE_DIVISOR
    assert cfg.default_generation == max(BUDGET_GENERATION_FLOOR, c // BUDGET_GENERATION_DIVISOR)
    assert cfg.effective_generation == cfg.default_generation
    assert cfg.effective_tools == BUDGET_TOOLS_RESERVE_DEFAULT
    assert cfg.effective_uncertainty == BUDGET_UNCERTAINTY_RESERVE_DEFAULT


def test_explicit_c_rejects_out_of_range() -> None:
    with pytest.raises(ValidationError):
        _config(context_tokens=4_096)
    with pytest.raises(ValidationError):
        _config(context_tokens=2_097_152)


def test_reserves_validated_against_c() -> None:
    with pytest.raises(ValidationError):
        _config(generation_reserve=999_999_999)
    with pytest.raises(ValidationError):
        # the three reserves together exceed the context
        _config(generation_reserve=20_000, tools_reserve=10_000, uncertainty_reserve=5_000)


# -- allowance: width x slot over DISTINCT files --------------------------


def test_allowance_is_width_times_slot(tokenizer: BundleTokenizer) -> None:
    plan = _plan(_config(), tokenizer)
    assert plan.entry_allowance(1) == plan.slot
    assert plan.entry_allowance(2) == 2 * plan.slot
    assert plan.entry_allowance(7) == 7 * plan.slot
    # repeated operands never inflate width: the allowance is a
    # pure function of the DISTINCT represented file count
    for _ in range(10):
        assert plan.entry_allowance(1) == plan.slot


def test_allowance_bounds(tokenizer: BundleTokenizer) -> None:
    plan = _plan(_config(max_distinct_files=2), tokenizer)
    with pytest.raises(BundleBudgetError) as exc:
        plan.entry_allowance(0)
    assert exc.value.reason is BundleBudgetReason.ITEM_LIMIT_EXCEEDED
    with pytest.raises(BundleBudgetError) as exc:
        plan.entry_allowance(3)
    assert exc.value.reason is BundleBudgetReason.ITEM_LIMIT_EXCEEDED
    with pytest.raises(BundleBudgetError) as exc:
        plan.entry_allowance(True)
    assert exc.value.reason is BundleBudgetReason.BAD_INPUT


# -- real tokenizer over the final rendered text --------------------------


def test_compiled_block_counted_exactly_no_padding(
    tokenizer: BundleTokenizer,
) -> None:
    plan = _plan(_config(), tokenizer)
    block = (
        "<slaif-compiled-block render=bundle-render-policy/v1 entry=root>\n"
        "MUST keep the bounds. \u4f60\u597d \u2014\n"
        "<references>\nAGENTS.md\n</references>\n"
        "</slaif-compiled-block>"
    )
    assert plan.count_compiled_block(block) == tokenizer.count_tokens(block)
    # empty / non-string input rejects
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_compiled_block("")
    assert exc.value.reason is BundleBudgetReason.BAD_INPUT


def test_byte_limits_independent_of_tokens(tokenizer: BundleTokenizer) -> None:
    # a byte-heavy but token-light block is refused at the INDEPENDENT
    # byte bound although its real token count is far below any
    # allowance:
    plan = _plan(_config(max_compiled_block_bytes=2_000), tokenizer)
    heavy = "a" * 3_000
    assert tokenizer.count_tokens(heavy) < plan.entry_allowance(1)
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_compiled_block(heavy)
    assert exc.value.reason is BundleBudgetReason.BYTE_LIMIT_EXCEEDED
    # and a message whose UTF-8 bytes exceed the bound:
    plan2 = _plan(_config(max_message_bytes=1_000), tokenizer)
    msg = BudgetMessage(role="user", content="x" * 2_000)
    with pytest.raises(BundleBudgetError) as exc:
        plan2.count_request_envelope((msg,), (), enable_thinking=False)
    assert exc.value.reason is BundleBudgetReason.BYTE_LIMIT_EXCEEDED


def test_entry_over_allowance_typed_never_truncated(
    tokenizer: BundleTokenizer,
) -> None:
    plan = _plan(_config(), tokenizer)
    body = _body_at_least_tokens(tokenizer, plan.entry_allowance(1) + 10)
    decision = plan.decide((_entry("root", body, required=True, files=1),))
    assert decision.outcome.value == "entry_invalid"
    assert decision.entries == ()
    assert any("allowance" in g for g in decision.guidance)


def test_required_overflow_typed(
    tokenizer: BundleTokenizer,
) -> None:
    plan = _plan(_config(context_tokens=32_768), tokenizer)
    body = _body_at_least_tokens(tokenizer, plan.aggregate + 10)
    # widen the allowance (more distinct files) so the AGGREGATE is
    # the binding limit, not the per-entry allowance:
    tokens = tokenizer.count_tokens(body)
    files = -(-tokens // plan.slot)
    assert files <= 128
    assert tokens <= plan.entry_allowance(files)
    assert tokens > plan.aggregate
    decision = plan.decide((_entry("root", body, required=True, files=files),))
    assert decision.outcome.value == "required_overflow"
    assert any("aggregate" in g for g in decision.guidance)


def test_optional_whole_entry_omission_deterministic(
    tokenizer: BundleTokenizer,
) -> None:
    plan = _plan(_config(context_tokens=32_768), tokenizer)
    small = _body_at_least_tokens(tokenizer, 100)
    mid = _body_at_least_tokens(tokenizer, 150)
    # opt-b fits its own WIDE allowance but cannot fit the AGGREGATE
    # after opt-a: it must be omitted as a whole entry.
    big_files = 16
    big = _body_at_least_tokens(
        tokenizer,
        plan.aggregate + 1 - tokenizer.count_tokens(small),
    )
    big_tokens = tokenizer.count_tokens(big)
    assert big_tokens <= plan.entry_allowance(big_files)
    assert big_tokens + tokenizer.count_tokens(small) > plan.aggregate
    entries = (
        _entry("opt-a", small, required=False, files=1),
        _entry("opt-b", big, required=False, files=big_files),
        _entry("opt-c", mid, required=False, files=1),
    )
    d1 = plan.decide(entries)
    d2 = plan.decide(entries)
    assert d1.model_dump() == d2.model_dump()
    labels = [d.label for d in d1.entries]
    assert "opt-a" in labels and "opt-c" in labels and "opt-b" not in labels
    assert d1.omitted_optional == ("opt-b",)
    assert d1.outcome.value == "ok"
    # whole-entry omission: the omitted entry contributes ZERO tokens
    assert d1.total_injected_tokens == (tokenizer.count_tokens(small) + tokenizer.count_tokens(mid))


def test_decide_request_overflow_outcome(tokenizer: BundleTokenizer) -> None:
    plan = _plan(_config(), tokenizer)
    capacity = plan.request_capacity(plan.generation_effective(None), 0)
    decision = plan.decide((), request_envelope_tokens=capacity + 1)
    assert decision.outcome.value == "request_overflow"
    assert decision.request_capacity == capacity


# -- requested generation: respected, never lowered ------------------------


def test_generation_respected_never_lowered(tokenizer: BundleTokenizer) -> None:
    plan = _plan(_config(context_tokens=32_768), tokenizer)
    default = plan.generation_effective(None)
    assert default == 4_096
    # a caller request ABOVE the default is respected, not clamped:
    assert plan.generation_effective(30_000) == 30_000
    # the boundary of the context is legal:
    assert plan.generation_effective(32_768) == 32_768
    # beyond the context / non-positive / bool reject:
    for bad in (32_769, 0, -1, True):
        with pytest.raises(BundleBudgetError) as exc:
            plan.generation_effective(bad)
        assert exc.value.reason is BundleBudgetReason.BAD_INPUT


def test_large_requested_output_is_typed_failure(
    tokenizer: BundleTokenizer,
) -> None:
    plan = _plan(_config(context_tokens=32_768), tokenizer)
    # 30000 requested + the reserves cannot fit C=32768: a typed
    # refusal, never a silent shrink of the requested output:
    with pytest.raises(BundleBudgetError) as exc:
        plan.request_capacity(plan.generation_effective(30_000), 0)
    assert exc.value.reason is BundleBudgetReason.CONTEXT_OVERSUBSCRIBED


# -- image reserves: explicit vision contract ------------------------------


def test_image_reserve_consumes_capacity(tokenizer: BundleTokenizer) -> None:
    cfg = _config(vision_enabled=True, per_image_reserve=1_000)
    plan = _plan(cfg, tokenizer)
    gen = plan.generation_effective(None)
    cap0 = plan.request_capacity(gen, 0)
    cap2 = plan.request_capacity(gen, 2)
    assert cap2 == cap0 - 2 * 1_000


def test_nonvision_positive_image_count_rejects(
    tokenizer: BundleTokenizer,
) -> None:
    plan = _plan(_config(), tokenizer)
    with pytest.raises(BundleBudgetError) as exc:
        plan.request_capacity(4_096, 1)
    assert exc.value.reason is BundleBudgetReason.VISION_CONTRACT_MISMATCH
    msg = BudgetMessage(role="user", content="hello")
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_request_envelope((msg,), (), enable_thinking=False, retained_images=1)
    assert exc.value.reason is BundleBudgetReason.VISION_CONTRACT_MISMATCH
    with pytest.raises(BundleBudgetError) as exc:
        plan.decide((), retained_images=3)
    assert exc.value.reason is BundleBudgetReason.VISION_CONTRACT_MISMATCH


def test_image_contract_config_validation() -> None:
    with pytest.raises(ValidationError):
        # reserve without the vision contract
        _config(per_image_reserve=512)
    with pytest.raises(ValidationError):
        # vision contract without retained capacity
        _config(vision_enabled=True, per_image_reserve=512, max_retained_images=0)


# -- envelope accounting: real data counts + closed fixed overheads --------


def test_envelope_exact_accounting(tokenizer: BundleTokenizer) -> None:
    plan = _plan(_config(), tokenizer)
    content = "probe \u4f60\u597d content"
    msg = BudgetMessage(role="user", content=content)
    frame = tokenizer.count_tokens(_IM_START + "user\n" + _IM_END + "\n")
    gen_open = tokenizer.count_tokens(_IM_START + "assistant\n")
    expected = frame + tokenizer.count_tokens(content) + gen_open
    expected += ENVELOPE_THINK_FRAMING_BOUND_TOKENS
    assert plan.count_request_envelope((msg,), (), enable_thinking=True) == expected
    # the think framing overhead is charged on BOTH settings:
    assert plan.count_request_envelope((msg,), (), enable_thinking=False) == expected
    # many messages: the per-message real counts add up exactly:
    many = tuple(BudgetMessage(role="user", content=f"m{i:04d}") for i in range(200))
    exp_many = 0
    for m in many:
        exp_many += frame + tokenizer.count_tokens(m.content)
    exp_many += gen_open + ENVELOPE_THINK_FRAMING_BOUND_TOKENS
    assert plan.count_request_envelope(many, (), enable_thinking=True) == exp_many


def test_tool_preamble_serialized_data_real_counted(
    tokenizer: BundleTokenizer,
) -> None:
    plan = _plan(_config(), tokenizer)
    assert plan.count_tool_preamble((), enable_thinking=False) == 0
    params = {"type": "object", "properties": {"q": {"type": "string"}}}
    tool = BudgetToolSpec(name="lookup", description="Look up.", parameters=params)
    # the pinned template's OWN JSON serialization (its tojson form:
    # sorted keys, compact commas, a space after each colon) -- the
    # minified form would render fewer bytes / tokens:
    serialized = json.dumps(
        {
            "type": "function",
            "function": {
                "name": "lookup",
                "description": "Look up.",
                "parameters": params,
            },
        },
        sort_keys=True,
        separators=(",", ": "),
    )
    expected = (
        ENVELOPE_TOOLS_PREFIX_BOUND_TOKENS
        + ENVELOPE_TOOLS_SUFFIX_BOUND_TOKENS
        + ENVELOPE_TOOL_REMINDER_BOUND_TOKENS
        + 1
        + tokenizer.count_tokens(serialized)
    )
    assert plan.count_tool_preamble((tool,), enable_thinking=False) == expected
    # a second tool adds its serialized data + the per-tool separator:
    tool2 = BudgetToolSpec(name="second", description="d2", parameters=params)
    # the second tool: the same pinned template form:
    serialized2 = json.dumps(
        {
            "type": "function",
            "function": {
                "name": "second",
                "description": "d2",
                "parameters": params,
            },
        },
        sort_keys=True,
        separators=(",", ": "),
    )
    expected2 = expected + 1 + tokenizer.count_tokens(serialized2)
    assert plan.count_tool_preamble((tool, tool2), enable_thinking=False) == expected2


def test_tool_serialization_is_the_pinned_template_form(
    tokenizer: BundleTokenizer,
) -> None:
    """The serialized tool data is the pinned template's own JSON
    render (tojson form), never the minified form: for a nested
    spec the template form is EXACTLY one byte longer per JSON
    colon (the space after each colon), so minified counting
    undercounts."""
    plan = _plan(_config(), tokenizer)
    params = {"type": "object", "properties": {"a": {"type": "string"}, "b": {"type": "integer"}}}
    tool = BudgetToolSpec(name="lookup", description="d", parameters=params)
    got = plan._serialized_tool(tool)
    minified = json.dumps(
        {
            "type": "function",
            "function": {
                "name": "lookup",
                "description": "d",
                "parameters": params,
            },
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    template_form = json.dumps(
        {
            "type": "function",
            "function": {
                "name": "lookup",
                "description": "d",
                "parameters": params,
            },
        },
        sort_keys=True,
        separators=(",", ": "),
    )
    assert got == template_form
    # one extra byte (the space) per colon:
    assert len(got) == len(minified) + minified.count(":")
    # and the preamble count follows the template form:
    expected = (
        ENVELOPE_TOOLS_PREFIX_BOUND_TOKENS
        + ENVELOPE_TOOLS_SUFFIX_BOUND_TOKENS
        + ENVELOPE_TOOL_REMINDER_BOUND_TOKENS
        + 1
        + tokenizer.count_tokens(template_form)
    )
    assert plan.count_tool_preamble((tool,), enable_thinking=False) == expected


def test_envelope_tool_limit_preflight(tokenizer: BundleTokenizer) -> None:
    """count_request_envelope enforces the SAME max_tools law as
    count_tool_preamble -- BEFORE any token work (the old
    _count_preamble_actual path bypassed the guard)."""
    plan = _plan(_config(max_tools=2), tokenizer)
    tools = tuple(BudgetToolSpec(name=f"t{i}", description="d") for i in range(3))
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_request_envelope(
            (BudgetMessage(role="user", content="x"),),
            tools,
            enable_thinking=False,
        )
    assert exc.value.reason is BundleBudgetReason.ITEM_LIMIT_EXCEEDED
    assert exc.value.detail == "tools"
    # the dedicated entry point's own limit still applies:
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_tool_preamble(tools, enable_thinking=False)
    assert exc.value.reason is BundleBudgetReason.ITEM_LIMIT_EXCEEDED
    # exactly at the limit the envelope counts normally:
    assert (
        plan.count_request_envelope(
            (BudgetMessage(role="user", content="x"),),
            tools[:2],
            enable_thinking=False,
        )
        > 0
    )


def test_request_byte_fence_preflight(tokenizer: BundleTokenizer) -> None:
    """max_request_bytes is enforced at the normal entry point
    BEFORE any token work, independent of token fit: the content
    below is tiny in tokens (fits any capacity) yet its
    conservative byte total crosses the fence."""
    plan = _plan(_config(max_request_bytes=512), tokenizer)
    # the fixed framing costs 71 bytes (33 user frame + 19
    # assistant open + 19 think bound): 450 + 71 = 521 > 512:
    content = "x" * 450
    assert tokenizer.count_tokens(content) < plan.aggregate
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_request_envelope(
            (BudgetMessage(role="user", content=content),),
            (),
            enable_thinking=False,
        )
    assert exc.value.reason is BundleBudgetReason.BYTE_LIMIT_EXCEEDED
    assert exc.value.detail == "request"
    # the fence is a UTF-8 BYTE fence (not a char / token fence):
    # 200 CJK chars = 600 bytes, tiny in tokens, crosses 512:
    cjk = BudgetMessage(role="user", content="\u4f60" * 200)
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_request_envelope((cjk,), (), enable_thinking=False)
    assert exc.value.reason is BundleBudgetReason.BYTE_LIMIT_EXCEEDED
    # and a request whose conservative byte total stays under the
    # fence counts normally (no false positive):
    small = BudgetMessage(role="user", content="x" * 100)
    assert plan.count_request_envelope((small,), (), enable_thinking=False) > 0


def test_request_byte_fence_counts_serialized_tool_form(
    tokenizer: BundleTokenizer,
) -> None:
    """The byte fence measures the tool data in the pinned
    template's JSON form: a spec that fits under the fence in
    minified bytes but not in the template form is refused."""
    plan = _plan(_config(max_request_bytes=700), tokenizer)
    # one key per colon adds one template byte over the minified
    # form; size the spec so the template form crosses 700 while
    # the minified form would fit:
    props = {f"k{i:02d}": {"type": "string"} for i in range(24)}
    tool = BudgetToolSpec(name="lookup", description="d", parameters={"properties": props})
    template_form = plan._serialized_tool(tool)
    minified = template_form.replace(": ", ":")
    assert len(minified) < 700 <= len(template_form) + 300
    msg = BudgetMessage(role="user", content="x")
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_request_envelope((msg,), (tool,), enable_thinking=False)
    assert exc.value.reason is BundleBudgetReason.BYTE_LIMIT_EXCEEDED


def test_tool_call_data_real_counted(tokenizer: BundleTokenizer) -> None:
    plan = _plan(_config(), tokenizer)
    L, R = chr(60), chr(62)

    def expected(name: str, args: tuple[tuple[str, str], ...]) -> int:
        total = plan._call_open_tokens + 2
        total += tokenizer.count_tokens(f"{L}function={name}{R}\n")
        for key, value in args:
            total += tokenizer.count_tokens(f"{L}parameter={key}{R}\n")
            total += tokenizer.count_tokens(value)
            total += tokenizer.count_tokens(f"{L}{R}\n")
        total += tokenizer.count_tokens(f"{L}{R}\n")
        total += plan._call_close_tokens
        return total

    # the FULL accounting is the closed fixed overheads plus the real
    # tokenizer over the data (names, values) in the pinned wrappers:
    call = BudgetToolCall(
        name="lookup",
        arguments=(("q", "a"), ("n", "\u4f60\u597d"), ("empty", "")),
    )
    assert plan.count_tool_call(call) == expected(
        "lookup", (("q", "a"), ("n", "\u4f60\u597d"), ("empty", ""))
    )
    # the argument VALUE is counted standalone with the real
    # tokenizer: the diff between two calls differing only in ONE
    # value is exactly the real-tokenizer diff of that value:
    call_a = BudgetToolCall(name="lookup", arguments=(("q", "a"),))
    call_b = BudgetToolCall(name="lookup", arguments=(("q", "a" * 5_000),))
    diff = plan.count_tool_call(call_b) - plan.count_tool_call(call_a)
    assert diff == tokenizer.count_tokens("a" * 5_000) - tokenizer.count_tokens("a")


def test_envelope_overflow_typed_on_real_count(tokenizer: BundleTokenizer) -> None:
    plan = _plan(_config(context_tokens=32_768), tokenizer)
    capacity = plan.request_capacity(plan.generation_effective(None), 0)
    # build content whose REAL whole-string token count exceeds the
    # capacity (measured on the whole, BPE is not additive):
    content = _body_at_least_tokens(tokenizer, capacity + 1)
    assert tokenizer.count_tokens(content) > capacity
    msg = BudgetMessage(role="user", content=content)
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_request_envelope((msg,), (), enable_thinking=True)
    assert exc.value.reason is BundleBudgetReason.REQUEST_OVERFLOW


def test_item_limits(tokenizer: BundleTokenizer) -> None:
    plan = _plan(
        _config(max_messages=2, max_tool_calls=1, max_tool_args=2, max_tools=1),
        tokenizer,
    )
    three = tuple(BudgetMessage(role="user", content="x") for _ in range(3))
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_request_envelope(three, (), enable_thinking=False)
    assert exc.value.reason is BundleBudgetReason.ITEM_LIMIT_EXCEEDED
    one = (BudgetMessage(role="user", content="x"),)
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_request_envelope(
            one,
            (),
            tool_calls=(BudgetToolCall(name="a", arguments=()),) * 2,
            enable_thinking=False,
        )
    assert exc.value.reason is BundleBudgetReason.ITEM_LIMIT_EXCEEDED
    # the per-call argument limit is prefetched at the SAME entry
    # point, before any token work or byte walk:
    over_args = (BudgetToolCall(name="a", arguments=(("a", "1"), ("b", "2"), ("c", "3"))),)
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_request_envelope(
            one,
            (),
            tool_calls=over_args,
            enable_thinking=False,
        )
    assert exc.value.reason is BundleBudgetReason.ITEM_LIMIT_EXCEEDED
    assert exc.value.detail == "tool args"
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_tool_call(
            BudgetToolCall(
                name="a",
                arguments=(("k", "v"), ("k", "v"), ("k", "v")),
            )
        )
    assert exc.value.reason is BundleBudgetReason.ITEM_LIMIT_EXCEEDED
    tools = (BudgetToolSpec(name="a"), BudgetToolSpec(name="b"))
    with pytest.raises(BundleBudgetError) as exc:
        plan.count_tool_preamble(tools, enable_thinking=False)
    assert exc.value.reason is BundleBudgetReason.ITEM_LIMIT_EXCEEDED


# -- identity binding -------------------------------------------------------


def test_plan_identity_binds_config_and_tokenizer(
    tokenizer: BundleTokenizer,
) -> None:
    p1 = _plan(_config(context_tokens=32_768), tokenizer)
    p2 = _plan(_config(context_tokens=40_000), tokenizer)
    p3 = _plan(_config(context_tokens=32_768, generation_reserve=5_000), tokenizer)
    assert p1.tokenizer_identity == tokenizer.binding.identity
    assert p1.plan_identity() != p2.plan_identity()
    assert p1.plan_identity() != p3.plan_identity()
    assert p1.config.budget_identity != p2.config.budget_identity


# -- the exact COMBINED final-injected-text aggregate law ---------------


def _trim_to_tokens(tokenizer: BundleTokenizer, text: str, target: int) -> str:
    """A deterministic (pinned-tokenizer) prefix of ``text`` with
    EXACTLY ``target`` real tokens (token count is monotone over
    appended characters, so the binary trim is exact)."""
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if tokenizer.count_tokens(text[:mid]) <= target:
            lo = mid
        else:
            hi = mid - 1
    body = text[:lo]
    assert tokenizer.count_tokens(body) == target
    return body


def test_combined_exact_count_not_sum(tokenizer: BundleTokenizer) -> None:
    """The AGGREGATE decision counts the EXACT COMBINED final
    injected text -- the included blocks joined by the separator
    plus the emitted extras -- with the REAL pinned tokenizer,
    never the SUM of the individual counts (the separator and
    boundary effects are counted too)."""
    plan = _plan(_config(context_tokens=32_768), tokenizer)
    b1 = "The protected fixture must never be mutated."
    b2 = "always log the mutation."
    extra = "read C.md with ordinary local tools before substantive mutation"
    entries = (
        _entry("e1", b1, required=False, files=1),
        _entry("e2", b2, required=False, files=1),
    )
    d = plan.decide(entries, join_separator="\n\n", final_extras=(extra,))
    assert d.outcome is BudgetOutcome.OK
    expected = tokenizer.count_tokens(b1 + "\n\n" + b2 + "\n\n" + extra)
    assert d.total_injected_tokens == expected
    # The SUM of the individual counts is NOT the combined count
    # for this pinned vocabulary: the decision was not made over
    # it.
    summed = tokenizer.count_tokens(b1) + tokenizer.count_tokens(b2) + tokenizer.count_tokens(extra)
    assert expected != summed


def test_combined_aggregate_knife_edge_diverges_from_sum(
    tokenizer: BundleTokenizer,
) -> None:
    """The knife edge (C=32768: aggregate 8192, slot 1024): two
    OPTIONAL entries whose individual SUM exactly equals the
    aggregate (the SUM law includes the second) but whose EXACT
    COMBINED count exceeds it (the combined law omits it WHOLE):
    the first block exactly 8191 tokens under width 8 (allowance
    8192), the second one token; the combined count is 8193."""
    plan = _plan(_config(context_tokens=32_768), tokenizer)
    assert plan.aggregate == 8192
    text = "The protected fixture must never be mutated. " * 2000
    b1 = _trim_to_tokens(tokenizer, text, 8191)
    e1 = _entry("e1", b1, required=False, files=8)
    e2 = _entry("e2", "z", required=False, files=1)
    # The SUM law (no combined arguments): 8191 + 1 = 8192 =
    # aggregate -- the second is included.
    d_sum = plan.decide((e1, e2))
    assert d_sum.outcome is BudgetOutcome.OK
    assert [row.label for row in d_sum.entries if row.included] == ["e1", "e2"]
    assert d_sum.total_injected_tokens == 8192
    # The EXACT COMBINED law: 8193 > 8192 -- the second is
    # omitted WHOLE, the outcome stays OK, and the total is the
    # exact combined count of the included set.
    d = plan.decide((e1, e2), join_separator="\n\n")
    assert d.outcome is BudgetOutcome.OK
    assert [row.label for row in d.entries if row.included] == ["e1"]
    assert d.omitted_optional == ("e2",)
    assert d.total_injected_tokens == tokenizer.count_tokens(b1) == 8191


def test_combined_required_overflow_typed(tokenizer: BundleTokenizer) -> None:
    """A REQUIRED second entry whose EXACT COMBINED count leaves
    the aggregate is TYPED REQUIRED_OVERFLOW (the individual
    sum would have fit) -- never truncated, never silently
    dropped."""
    plan = _plan(_config(context_tokens=32_768), tokenizer)
    text = "The protected fixture must never be mutated. " * 2000
    b1 = _trim_to_tokens(tokenizer, text, 8191)
    e1 = _entry("e1", b1, required=True, files=8)
    e2 = _entry("e2", "z", required=True, files=1)
    d = plan.decide((e1, e2), join_separator="\n\n")
    assert d.outcome is BudgetOutcome.REQUIRED_OVERFLOW
    assert [row.label for row in d.entries if row.included] == ["e1"]
    assert d.total_injected_tokens == 8191


def test_combined_extras_alone_oversubscribed_typed(
    tokenizer: BundleTokenizer,
) -> None:
    """The caller's EMITTED extras alone exceeding the entire
    aggregate limit is a typed CONTEXT_OVERSUBSCRIBED error
    (never a silent pass)."""
    plan = _plan(_config(context_tokens=32_768), tokenizer)
    assert plan.aggregate == 8192
    extra = _body_at_least_tokens(tokenizer, 8193)
    with pytest.raises(BundleBudgetError) as exc:
        plan.decide((), join_separator="\n\n", final_extras=(extra,))
    assert exc.value.reason is BundleBudgetReason.CONTEXT_OVERSUBSCRIBED
