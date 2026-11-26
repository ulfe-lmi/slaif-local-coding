"""021 deterministic bundle selection: the selection half of C03.

The ordered selection cases over ACTUAL admitted records (the
018-p/018-t fixture), the REAL pinned tokenizer and the ACTUAL
compiler over a FAKE upstream:

- required governance (the root and the root-scoped P1 binding
  closure, closed through acquired proven P1 entries) is
  selected COMPLETE before any optional entry, in stable
  deterministic order;
- the ACTUAL P2/P3 constitutional priority ranks the optional
  entries (narrower coverage, then stable identity);
- missing-binding guidance is measured against PROVEN usable
  coverage only: an opaque greedy row never satisfies a
  required read and never suppresses its guidance;
- duplicate coverage is omitted whole and observably;
- the ONE final rendered block (versioned render policy with
  references) is what the budget counts;
- typed essential overflow / invalid entry / request overflow
  are the fixed 422, never truncation.

The stage stays inert: no adapter wiring, no configuration key,
no v1 runtime activation.
"""

from __future__ import annotations

import json
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
    BundleCompilerOutcome,
    derive_compile_key,
    entry_source,
    render_compiled_index,
    serialize_compiled_index,
)
from slaif_local_coding.constitution.bundles.bundle_selection import (
    BUNDLE_SELECTION_INJECTION_SEPARATOR,
    SELECTION_PROVENANCE_UNPROVEN_PREFIX,
    SelectionOmissionReason,
    SelectionOutcome,
    SelectionReadyEntry,
    select_working_set,
    selection_http_status,
)
from slaif_local_coding.constitution.bundles.bundle_tokenizer import (
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
from tests.test_bundle_compiler import (
    A_BODY,
    COMPILER_KEY_ENV,
    COMPILER_KEY_VALUE,
    _config,
)
from tests.test_causal_history import (
    ENDPOINTS,
    MODES,
    read_request,
)
from tests.test_root_region_lineage import r_bootstrap, r_issue, r_observe

B_BODY = "ALWAYS log the mutation.\n"
D_BODY = "ALWAYS verify the fixture digest.\n"
ROOT_REQUIRED = "Follow `A.md` before mutation. Then `B.md` and `C.md`.\n"
ROOT_BINDING = "Follow `A.md` before mutation. Then `B.md`.\n"
ROOT_CLOSURE = "Follow `A.md` before mutation.\n"
ROOT_OPTIONAL = "Follow `A.md` then `B.md`.\n"
A_BODY_CLOSURE = "NEVER mutate the protected fixture. Follow `D.md`.\n"
_LONG_STATEMENT = ("The protected fixture must never be mutated, renamed or relocated. " * 30)[
    :4096
]


def _dep(
    path: str,
    cls: str,
    priority: int,
    urgency: str,
    evidence: str = "synthetic root evidence",
) -> BundleCompiledDependency:
    return BundleCompiledDependency(
        path=path,
        reference_confidence=0.9,
        constitutional_priority=priority,
        classification=cls,  # type: ignore[arg-type]
        relationship="root-referenced",
        evidence=evidence,
        acquisition_urgency=urgency,  # type: ignore[arg-type]
    )


def _mk_index(
    entry: Any,
    candidates: tuple[str, ...],
    config: Any,
    tokenizer: Any,
    plan: BundleBudgetPlan,
    *,
    rules: tuple[BundleCompiledRule, ...],
    scopes: tuple[str, ...],
    authorities: tuple[str, ...],
    boundaries: tuple[str, ...],
    triggers: tuple[str, ...],
    dependencies: tuple[BundleCompiledDependency, ...] = (),
) -> BundleCompiledIndex:
    _text, digest, length = entry_source(entry)
    compile_key = derive_compile_key(
        entry_class=entry.entry_class,
        content_key=entry.content_key,
        source_sha256=digest,
        source_byte_length=length,
        candidate_paths=candidates,
        config_identity=config.config_identity,
        tokenizer_identity=tokenizer.binding.identity,
        budget_identity=plan.plan_identity(),
        render_policy_version=tokenizer.binding.render_policy_version,
    )
    return BundleCompiledIndex(
        schema_version=BUNDLE_COMPILER_SCHEMA_VERSION,
        compiler_version=BUNDLE_COMPILER_VERSION,
        prompt_policy_version=BUNDLE_COMPILER_PROMPT_POLICY_VERSION,
        model=config.model,
        entry_class=entry.entry_class,
        content_key=entry.content_key,
        compile_key=compile_key,
        source_sha256=digest,
        source_byte_length=length,
        summary="Bounded synthetic summary.",
        rules=rules,
        scopes=scopes,
        authorities=authorities,
        source_of_truth_boundaries=boundaries,
        reread_triggers=triggers,
        dependencies=dependencies,
    )


def _root_index(
    entry: Any,
    config: Any,
    tokenizer: Any,
    plan: BundleBudgetPlan,
    deps: tuple[BundleCompiledDependency, ...],
) -> BundleCompiledIndex:
    return _mk_index(
        entry,
        tuple(dep.path for dep in deps),
        config,
        tokenizer,
        plan,
        rules=(
            BundleCompiledRule(
                rule_id="follow-dependencies",
                strength="must",
                statement="Follow the declared dependencies before mutation.",
                location="root line 1",
                evidence="Follow `A.md` before mutation.",
            ),
        ),
        scopes=("workspace root",),
        authorities=("governing root",),
        boundaries=("repository source files",),
        triggers=("root source change",),
        dependencies=deps,
    )


def _file_index(
    entry: Any,
    candidates: tuple[str, ...],
    config: Any,
    tokenizer: Any,
    plan: BundleBudgetPlan,
    *,
    rule_id: str,
    statement: str,
    location: str,
    dependencies: tuple[BundleCompiledDependency, ...] = (),
) -> BundleCompiledIndex:
    return _mk_index(
        entry,
        candidates,
        config,
        tokenizer,
        plan,
        rules=(
            BundleCompiledRule(
                rule_id=rule_id,
                strength="must",
                statement=statement,
                location=location,
                evidence=statement,
            ),
        ),
        scopes=("file content",),
        authorities=("file provenance",),
        boundaries=("repository source files",),
        triggers=("source change",),
        dependencies=dependencies,
    )


def _states(
    root_body: str,
    reads: tuple[tuple[str, str, str], ...],
    mode: AdmissionMode,
    endpoint: str,
    lineage: str,
) -> Any:
    """The ACTUAL P/T fixture: the rooted bootstrap plus the
    genuinely issued reads (``(cid, body, cmd)``), admitted under
    the accepted T law."""
    ns, state = r_bootstrap(mode, lineage, root_body=root_body)
    for cid, body, cmd in reads:
        issued = r_issue(state, ns, cid, endpoint, (CAUSAL_ROOT_FACT,), cmd)
        assert issued.outcome is RootLineageOutcome.ACCEPTED, issued.diagnostics
        transition = r_observe(issued.state, ns, (read_request(endpoint, cid, body, cmd),))
        assert transition.outcome is RootLineageOutcome.ACCEPTED, transition.diagnostics
        state = transition.state
    t = derive_root_region_admission(state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    return ns, state, t


DEDUP_MARKER = "OVLMARK"


def _overlap_states(endpoint: str) -> Any:
    """The ACTUAL P/T overlap fixture (the accepted 018-t B5 proven
    marker-partition shape, legitimately co-current): the proven
    segmented ``[A,B]`` read (``cat A.md && echo 'OVLMARK' &&
    cat B.md`` -- a finite unique-marker plan with the per-member
    proven segment digests) plus the SAME-digest proven singletons
    for A.md and B.md.  Every read is genuinely issued against the
    frozen root-fact frontier ONLY: the three occurrences are
    mutually INCOMPARABLE under the accepted 018 causality (no
    parent edge between them, no clock, no invented ordering
    source), so the overlap is a legitimate co-current proven
    same-version overlap -- not an opaque boundaryless bundle.
    BOTH active keys are verified through the ACTUAL P/T
    derivation before any selection: the A.md reverse row carries
    the singleton key AND the co-cached bundle key, and the B.md
    row carries the bundle key AND the singleton key (the
    simultaneously admitted overlap)."""
    ns, s0 = r_bootstrap(
        AdmissionMode.GREEDY,
        f"selection021-dedup-{endpoint}",
        root_body=ROOT_OPTIONAL,
    )
    cmd_ab = f"cat A.md && echo '{DEDUP_MARKER}' && cat B.md"
    body_ab = A_BODY + DEDUP_MARKER + "\n" + B_BODY
    t1 = r_issue(s0, ns, "p1", endpoint, (CAUSAL_ROOT_FACT,), cmd_ab)
    assert t1.outcome is RootLineageOutcome.ACCEPTED, t1.diagnostics
    t2 = r_observe(t1.state, ns, (read_request(endpoint, "p1", body_ab, cmd=cmd_ab),))
    assert t2.outcome is RootLineageOutcome.ACCEPTED, t2.diagnostics
    t3 = r_issue(t2.state, ns, "a1", endpoint, (CAUSAL_ROOT_FACT,), "cat A.md")
    assert t3.outcome is RootLineageOutcome.ACCEPTED, t3.diagnostics
    t4 = r_observe(t3.state, ns, (read_request(endpoint, "a1", A_BODY, "cat A.md"),))
    assert t4.outcome is RootLineageOutcome.ACCEPTED, t4.diagnostics
    t5 = r_issue(t4.state, ns, "b1", endpoint, (CAUSAL_ROOT_FACT,), "cat B.md")
    assert t5.outcome is RootLineageOutcome.ACCEPTED, t5.diagnostics
    t6 = r_observe(t5.state, ns, (read_request(endpoint, "b1", B_BODY, "cat B.md"),))
    assert t6.outcome is RootLineageOutcome.ACCEPTED, t6.diagnostics
    state = t6.state
    t = derive_root_region_admission(state, ns)
    assert t.outcome is RootRegionAdmissionOutcome.READY, t.diagnostics
    admission = t.admission
    assert admission is not None
    a_row = next(row for row in admission.path_associations if row.path == "A.md")
    b_row = next(row for row in admission.path_associations if row.path == "B.md")
    # Both active keys through the actual P/T: the proven singleton
    # and the co-cached proven bundle are SIMULTANEOUSLY admitted
    # for each overlapped path.
    assert len(a_row.content_keys) == 2
    assert len(b_row.content_keys) == 2
    return ns, state, t


def _represented(t: Any, entry: Any) -> tuple[str, ...]:
    rows = [row for row in t.admission.path_associations if entry.content_key in row.content_keys]
    assert rows, "the admitted entry has no represented member path row"
    return tuple(sorted(row.path for row in rows))


def _entry_for(t: Any, path: str) -> Any:
    """The UNIQUE singleton entry representing exactly ``path`` (the
    complete reverse member index may list several content keys for
    the same path: the one-member row is the unambiguous match)."""
    adm = t.admission
    assert adm is not None
    rows = [row for row in adm.path_associations if row.path == path]
    assert rows, f"no admitted entry represents {path}"
    keys = {key for row in rows for key in row.content_keys}
    candidates = [adm.root_entry, *adm.entries]
    matching = [
        entry
        for entry in candidates
        if entry.content_key in keys and _represented(t, entry) == (path,)
    ]
    assert len(matching) == 1, f"no unique singleton entry represents {path}"
    return matching[0]


async def _compile_all(
    config: Any,
    tokenizer: Any,
    plan: BundleBudgetPlan,
    account: BundleCompilerAccount,
    demands: tuple[tuple[Any, tuple[str, ...], BundleCompiledIndex], ...],
    monkeypatch: pytest.MonkeyPatch,
) -> dict[str, BundleCompiledIndex]:
    """Drive the ACTUAL compiler (fake upstream) over every
    demand; the validated indexes come back as the ready-entry
    indexes."""
    monkeypatch.setenv(COMPILER_KEY_ENV, COMPILER_KEY_VALUE)
    payloads = {
        index.content_key: serialize_compiled_index(index).decode("utf-8")
        for _entry, _candidates, index in demands
    }
    captured: list[httpx.Request] = []

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
    results: dict[str, BundleCompiledIndex] = {}
    try:
        for position, (entry, candidates, expected) in enumerate(demands, start=1):
            result = await compiler.compile_entry(
                entry=entry,
                candidate_paths=candidates,
                tokenizer=tokenizer,
                budget_identity=plan.plan_identity(),
                rendered_allowance=plan.entry_allowance(entry.width),
                account=account,
            )
            assert result.outcome is BundleCompilerOutcome.COMPLETED, result.detail
            assert result.attempts == 1
            assert result.index == expected
            assert len(captured) == position
            results[entry.content_key] = result.index
    finally:
        await compiler.aclose()
        await client.aclose()
    return results


def _completion_bytes(content: str) -> bytes:
    return json.dumps(
        {
            "id": "chatcmpl-021",
            "object": "chat.completion",
            "model": "Qwen3.8-27B",
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


def _ready(
    t: Any,
    entry: Any,
    index: BundleCompiledIndex,
    candidates: tuple[str, ...],
    origin_proven: bool = True,
) -> SelectionReadyEntry:
    return SelectionReadyEntry(
        entry=entry,
        index=index,
        represented_paths=_represented(t, entry),
        candidate_paths=candidates,
        origin_proven=origin_proven,
    )


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_selection_required_before_optional_complete(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Required complete before optional: the root, the P1-bound
    A, then the P2-ranked B; the final rendered blocks are
    counted, the authority envelope is carried, the decision is
    deterministic."""
    ns, _state, t = _states(
        ROOT_REQUIRED,
        (("a", A_BODY, "cat A.md"), ("b", B_BODY, "cat B.md")),
        mode,
        endpoint,
        f"selection021-basic-{mode.value}-{endpoint}",
    )
    root_entry = t.admission.root_entry
    entry_a = _entry_for(t, "A.md")
    entry_b = _entry_for(t, "B.md")

    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=262_144))
    account = BundleCompilerAccount()

    root_index = _root_index(
        root_entry,
        config,
        tokenizer,
        plan,
        (
            _dep("A.md", "P1", 90, "immediate"),
            _dep("B.md", "P2", 50, "next_turn"),
            _dep("C.md", "P3", 30, "background"),
        ),
    )
    index_a = _file_index(
        entry_a,
        (),
        config,
        tokenizer,
        plan,
        rule_id="never-mutate-fixture",
        statement="NEVER mutate the protected fixture.",
        location="A.md",
    )
    index_b = _file_index(
        entry_b,
        (),
        config,
        tokenizer,
        plan,
        rule_id="always-log-mutation",
        statement="ALWAYS log the mutation.",
        location="B.md",
    )
    indices = await _compile_all(
        config,
        tokenizer,
        plan,
        account,
        (
            (root_entry, ("A.md", "B.md", "C.md"), root_index),
            (entry_a, (), index_a),
            (entry_b, (), index_b),
        ),
        monkeypatch,
    )
    assert account.upstream_calls == 3

    root = _ready(t, root_entry, indices[root_entry.content_key], ("A.md", "B.md", "C.md"))
    ready_a = _ready(t, entry_a, indices[entry_a.content_key], ())
    ready_b = _ready(t, entry_b, indices[entry_b.content_key], ())

    decision = select_working_set(root, (ready_a, ready_b), plan)
    again = select_working_set(root, (ready_a, ready_b), plan)
    assert decision.selection_key == again.selection_key
    assert decision.outcome is SelectionOutcome.OK
    assert selection_http_status(decision) is None
    assert [row.content_key for row in decision.working_set] == [
        root_entry.content_key,
        entry_a.content_key,
        entry_b.content_key,
    ]
    by_key = {row.content_key: row for row in decision.working_set}
    assert by_key[root_entry.content_key].required is True
    assert by_key[entry_a.content_key].required is True
    assert by_key[entry_b.content_key].required is False
    # The final rendered block is the exact counted text (the
    # versioned wrapper plus the deterministic references):
    root_row = by_key[root_entry.content_key]
    assert root_row.rendered_block.startswith("<slaif-compiled-block")
    assert root_row.rendered_block.endswith("</slaif-compiled-block>")
    assert "A.md" in root_row.rendered_block and "C.md" in root_row.rendered_block
    for row in decision.working_set:
        assert row.tokens == plan.tokenizer.count_tokens(row.rendered_block)
        assert row.tokens <= row.allowance
    # The scoped root/authority envelope is carried:
    assert decision.root_scopes == ("workspace root",)
    assert decision.root_authorities == ("governing root",)
    assert decision.root_boundaries == ("repository source files",)
    assert decision.missing_bindings == ()
    assert decision.omitted == ()
    # The AGGREGATE total is the EXACT COMBINED final injected
    # text -- the final blocks joined by the deterministic
    # separator (no missing bindings emitted here, so no
    # extras) -- counted with the pinned tokenizer, not the SUM
    # of the per-block counts.
    combined = BUNDLE_SELECTION_INJECTION_SEPARATOR.join(
        row.rendered_block for row in decision.working_set
    )
    assert decision.budget.total_injected_tokens == plan.tokenizer.count_tokens(combined)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_selection_missing_binding_guidance_never_suppressed(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A root-bound P1 path with NO proven ready entry emits the
    exact read guidance; the working set never substitutes an
    opaque reference or an unrelated entry for it."""
    ns, _state, t = _states(
        ROOT_REQUIRED,
        (("a", A_BODY, "cat A.md"),),
        mode,
        endpoint,
        f"selection021-missing-{mode.value}-{endpoint}",
    )
    root_entry = t.admission.root_entry
    entry_a = _entry_for(t, "A.md")

    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=262_144))
    account = BundleCompilerAccount()

    root_index = _root_index(
        root_entry,
        config,
        tokenizer,
        plan,
        (
            _dep("A.md", "P1", 90, "immediate"),
            _dep("B.md", "P1", 60, "immediate"),
            _dep("C.md", "P3", 30, "background"),
        ),
    )
    index_a = _file_index(
        entry_a,
        (),
        config,
        tokenizer,
        plan,
        rule_id="never-mutate-fixture",
        statement="NEVER mutate the protected fixture.",
        location="A.md",
    )
    indices = await _compile_all(
        config,
        tokenizer,
        plan,
        account,
        (
            (root_entry, ("A.md", "B.md", "C.md"), root_index),
            (entry_a, (), index_a),
        ),
        monkeypatch,
    )

    root = _ready(t, root_entry, indices[root_entry.content_key], ("A.md", "B.md", "C.md"))
    ready_a = _ready(t, entry_a, indices[entry_a.content_key], ())
    decision = select_working_set(root, (ready_a,), plan)
    assert decision.outcome is SelectionOutcome.OK
    assert [row.content_key for row in decision.working_set] == [
        root_entry.content_key,
        entry_a.content_key,
    ]
    missing = decision.missing_bindings
    assert len(missing) == 1
    assert missing[0].path == "B.md"
    assert missing[0].acquisition_urgency == "immediate"
    assert missing[0].guidance == "read B.md with ordinary local tools before substantive mutation"


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_selection_binding_closure_through_acquired_p1(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The binding closure closes through acquired proven P1
    entries: the root's P1 A carries its own mandatory P1
    candidate D, so D is REQUIRED (ranked by its actual P1
    priority beneath A)."""
    ns, _state, t = _states(
        ROOT_CLOSURE,
        (
            ("a", A_BODY_CLOSURE, "cat A.md"),
            ("d", D_BODY, "cat D.md"),
        ),
        mode,
        endpoint,
        f"selection021-closure-{mode.value}-{endpoint}",
    )
    root_entry = t.admission.root_entry
    entry_a = _entry_for(t, "A.md")
    entry_d = _entry_for(t, "D.md")

    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=262_144))
    account = BundleCompilerAccount()

    root_index = _root_index(
        root_entry, config, tokenizer, plan, (_dep("A.md", "P1", 90, "immediate"),)
    )
    index_a = _file_index(
        entry_a,
        ("D.md",),
        config,
        tokenizer,
        plan,
        rule_id="never-mutate-fixture",
        statement="NEVER mutate the protected fixture.",
        location="A.md",
        dependencies=(_dep("D.md", "P1", 80, "immediate"),),
    )
    index_d = _file_index(
        entry_d,
        (),
        config,
        tokenizer,
        plan,
        rule_id="always-verify-digest",
        statement="ALWAYS verify the fixture digest.",
        location="D.md",
    )
    indices = await _compile_all(
        config,
        tokenizer,
        plan,
        account,
        (
            (root_entry, ("A.md",), root_index),
            (entry_a, ("D.md",), index_a),
            (entry_d, (), index_d),
        ),
        monkeypatch,
    )

    root = _ready(t, root_entry, indices[root_entry.content_key], ("A.md",))
    ready_a = _ready(t, entry_a, indices[entry_a.content_key], ("D.md",))
    ready_d = _ready(t, entry_d, indices[entry_d.content_key], ())
    decision = select_working_set(root, (ready_a, ready_d), plan)
    assert decision.outcome is SelectionOutcome.OK
    # D is REQUIRED via the closure and ordered by its actual
    # P1 priority beneath A:
    assert [row.content_key for row in decision.working_set] == [
        root_entry.content_key,
        entry_a.content_key,
        entry_d.content_key,
    ]
    by_key = {row.content_key: row for row in decision.working_set}
    assert by_key[entry_a.content_key].required is True
    assert by_key[entry_d.content_key].required is True
    assert decision.missing_bindings == ()
    assert decision.omitted == ()


@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_selection_unproven_bundle_never_required(
    endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An opaque boundaryless greedy bundle (unknown per-member
    origin) NEVER classifies required, NEVER extends the binding
    closure and NEVER suppresses the missing-binding guidance for
    a P1 path it merely co-caches."""
    from slaif_local_coding.constitution.bundles.bundle_admission_models import (
        AdmissionMode,
    )

    mode = AdmissionMode.GREEDY
    ns, _state, t = _states(
        ROOT_BINDING,
        (("ab", A_BODY + B_BODY, "cat A.md B.md"),),
        mode,
        endpoint,
        f"selection021-unproven-{endpoint}",
    )
    root_entry = t.admission.root_entry
    assert len(t.admission.entries) == 1, "the boundaryless bundle row is missing"
    bundle = t.admission.entries[0]
    assert set(_represented(t, bundle)) == {"A.md", "B.md"}

    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=262_144))
    account = BundleCompilerAccount()

    root_index = _root_index(
        root_entry,
        config,
        tokenizer,
        plan,
        (_dep("A.md", "P1", 90, "immediate"), _dep("B.md", "P3", 30, "background")),
    )
    index_bundle = _file_index(
        bundle,
        (),
        config,
        tokenizer,
        plan,
        rule_id="bundle-procedure",
        statement="Follow the retained bundle procedure.",
        location="",  # boundaryless: per-file attribution unproven
    )
    indices = await _compile_all(
        config,
        tokenizer,
        plan,
        account,
        (
            (root_entry, ("A.md", "B.md"), root_index),
            (bundle, (), index_bundle),
        ),
        monkeypatch,
    )

    root = _ready(t, root_entry, indices[root_entry.content_key], ("A.md", "B.md"))
    ready_bundle = _ready(t, bundle, indices[bundle.content_key], (), origin_proven=False)
    # The DERIVATION law: the accepted greedy admission cannot be
    # made binding by a caller flag, and the represented set must
    # be the exact distinct key-record member occurrences --
    # both mismatches are refused before any selection work.
    with pytest.raises(ValueError, match="origin provenance"):
        SelectionReadyEntry(
            entry=bundle,
            index=indices[bundle.content_key],
            represented_paths=_represented(t, bundle),
            candidate_paths=(),
            origin_proven=True,
        )
    with pytest.raises(ValueError, match="represented paths"):
        SelectionReadyEntry(
            entry=bundle,
            index=indices[bundle.content_key],
            represented_paths=("A.md", "C.md"),
            candidate_paths=(),
            origin_proven=False,
        )
    decision = select_working_set(root, (ready_bundle,), plan)
    assert decision.outcome is SelectionOutcome.OK
    # The unproven row stays optional background, never required:
    by_key = {row.content_key: row for row in decision.working_set}
    assert by_key[bundle.content_key].required is False
    assert by_key[root_entry.content_key].required is True
    # The unknown mixed origin / greedy-background provenance is
    # EMITTED in the final rendered block (the exact unproven
    # member paths, canonical sorted order) and counted like any
    # other injected byte -- never hidden.
    bundle_block = by_key[bundle.content_key].rendered_block
    assert bundle_block.endswith("\n" + SELECTION_PROVENANCE_UNPROVEN_PREFIX + "A.md,B.md")
    # The AGGREGATE total is the EXACT COMBINED final injected
    # text (the final blocks joined by the deterministic
    # separator plus the EMITTED missing-binding guidance),
    # counted with the real pinned tokenizer.
    combined = BUNDLE_SELECTION_INJECTION_SEPARATOR.join(
        [row.rendered_block for row in decision.working_set]
        + [row.guidance for row in decision.missing_bindings]
    )
    assert decision.budget.total_injected_tokens == tokenizer.count_tokens(combined)
    # The P1 binding A.md has NO proven ready entry: the exact
    # guidance stands even though the bundle co-caches A.md:
    missing = decision.missing_bindings
    assert len(missing) == 1
    assert missing[0].path == "A.md"
    assert missing[0].acquisition_urgency == "immediate"


@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_selection_overlap_coverage_deduplicated(
    endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Whole-entry duplicate coverage over the legitimately
    co-current PROVEN segmented overlap (the accepted 018-t B5
    marker-partition ``[A,B]`` read plus the SAME-digest proven
    singletons, with BOTH active keys verified through the actual
    P/T before selection): the optional singleton B whose only
    path is already covered by the selected entries (the proven
    singleton A plus the co-cached proven bundle) is omitted
    WHOLE, observably, with the deterministic covered-by
    witness."""
    ns, _state, t = _overlap_states(endpoint)
    root_entry = t.admission.root_entry
    entry_a = _entry_for(t, "A.md")
    entry_b = _entry_for(t, "B.md")
    bundle = next(
        entry for entry in t.admission.entries if set(_represented(t, entry)) == {"A.md", "B.md"}
    )

    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=262_144))
    account = BundleCompilerAccount()

    root_index = _root_index(
        root_entry,
        config,
        tokenizer,
        plan,
        (_dep("A.md", "P3", 80, "background"), _dep("B.md", "P3", 60, "background")),
    )
    index_a = _file_index(
        entry_a,
        (),
        config,
        tokenizer,
        plan,
        rule_id="never-mutate-fixture",
        statement="NEVER mutate the protected fixture.",
        location="A.md",
    )
    index_b = _file_index(
        entry_b,
        (),
        config,
        tokenizer,
        plan,
        rule_id="always-log-mutation",
        statement="ALWAYS log the mutation.",
        location="B.md",
    )
    index_bundle = _file_index(
        bundle,
        (),
        config,
        tokenizer,
        plan,
        rule_id="bundle-procedure",
        statement="Follow the retained bundle procedure.",
        location="",
    )
    indices = await _compile_all(
        config,
        tokenizer,
        plan,
        account,
        (
            (root_entry, ("A.md", "B.md"), root_index),
            (entry_a, (), index_a),
            (entry_b, (), index_b),
            (bundle, (), index_bundle),
        ),
        monkeypatch,
    )

    root = _ready(t, root_entry, indices[root_entry.content_key], ("A.md", "B.md"))
    ready_a = _ready(t, entry_a, indices[entry_a.content_key], ())
    ready_b = _ready(t, entry_b, indices[entry_b.content_key], ())
    # The proven segmented bundle: per-member origin IS proven.
    ready_bundle = _ready(t, bundle, indices[bundle.content_key], (), origin_proven=True)
    decision = select_working_set(root, (ready_a, ready_b, ready_bundle), plan)
    assert decision.outcome is SelectionOutcome.OK
    keys = [row.content_key for row in decision.working_set]
    # A (P3 80, narrower) and the bundle (adds B.md) are selected;
    # the singleton B is fully covered and omitted whole:
    assert keys == [root_entry.content_key, entry_a.content_key, bundle.content_key]
    assert not any(row.required for row in decision.working_set[1:])
    omitted_b = [
        omission for omission in decision.omitted if omission.content_key == entry_b.content_key
    ]
    assert len(omitted_b) == 1
    assert omitted_b[0].reason is SelectionOmissionReason.COVERAGE_DEDUPLICATED
    assert omitted_b[0].covered_by == bundle.content_key
    assert omitted_b[0].detail == "B.md"
    assert decision.missing_bindings == ()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_selection_entry_invalid_typed_never_truncated(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A required entry whose final rendered block exceeds its
    width x slot allowance is a TYPED invalid-entry decision (the
    fixed 422): the root still forwards, the over-allowance entry
    is absent ENTIRELY, and no truncated form of it is injected."""
    ns, _state, t = _states(
        ROOT_CLOSURE,
        (("a", A_BODY, "cat A.md"),),
        mode,
        endpoint,
        f"selection021-invalid-{mode.value}-{endpoint}",
    )
    root_entry = t.admission.root_entry
    entry_a = _entry_for(t, "A.md")

    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(
        tokenizer,
        BundleBudgetConfig(
            context_tokens=8_192,
            generation_reserve=1_024,
            tools_reserve=512,
            uncertainty_reserve=256,
        ),
    )
    account = BundleCompilerAccount()

    root_index = _root_index(
        root_entry, config, tokenizer, plan, (_dep("A.md", "P1", 90, "immediate"),)
    )
    indices = await _compile_all(
        config,
        tokenizer,
        plan,
        account,
        ((root_entry, ("A.md",), root_index),),
        monkeypatch,
    )
    # A FORGED retained index for A: model-validated, source- and
    # key-joined, but far beyond the width-1 slot allowance of the
    # configured C (the real compiler would have refused it; the
    # selector's typed fence is the last line of defense).
    index_a = _mk_index(
        entry_a,
        (),
        config,
        tokenizer,
        plan,
        rules=(
            BundleCompiledRule(
                rule_id="forged-long-rule",
                strength="must",
                statement=_LONG_STATEMENT,
                location="A.md",
                evidence=_LONG_STATEMENT,
            ),
        ),
        scopes=("file content",),
        authorities=("file provenance",),
        boundaries=("repository source files",),
        triggers=("source change",),
    )
    assert plan.tokenizer.count_tokens(
        plan.tokenizer.render_compiled_block(
            entry_label=f"entry-{entry_a.content_key[:16]}",
            body=render_compiled_index(index_a),
            references=(),
        )
    ) > plan.entry_allowance(entry_a.width)

    root = _ready(t, root_entry, indices[root_entry.content_key], ("A.md",))
    ready_a = _ready(t, entry_a, index_a, ())
    decision = select_working_set(root, (ready_a,), plan, requested_max_tokens=2_000)
    assert decision.outcome is SelectionOutcome.ENTRY_INVALID
    assert selection_http_status(decision) == 422
    # The required governance that fits (the root) still forwards:
    assert [row.content_key for row in decision.working_set] == [root_entry.content_key]
    # The over-allowance required entry is absent ENTIRELY -- no
    # truncated or partial form of it anywhere in the working set:
    assert all(row.content_key != entry_a.content_key for row in decision.working_set)
    assert decision.budget.guidance
    # The caller-requested generation is respected, never lowered:
    assert decision.budget.generation_effective == 2_000
    assert decision.missing_bindings == ()


@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_selection_request_overflow_typed(
    endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A request envelope already counted over the residual
    capacity is a TYPED request-overflow decision (the fixed
    422): no working set, no truncation, no forwarded dangling
    references."""
    ns, _state, t = _states(
        ROOT_CLOSURE,
        (("a", A_BODY, "cat A.md"),),
        AdmissionMode.LEAN,
        endpoint,
        f"selection021-request-overflow-{endpoint}",
    )
    root_entry = t.admission.root_entry
    entry_a = _entry_for(t, "A.md")

    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=32_768))
    account = BundleCompilerAccount()

    root_index = _root_index(
        root_entry, config, tokenizer, plan, (_dep("A.md", "P1", 90, "immediate"),)
    )
    index_a = _file_index(
        entry_a,
        (),
        config,
        tokenizer,
        plan,
        rule_id="never-mutate-fixture",
        statement="NEVER mutate the protected fixture.",
        location="A.md",
    )
    indices = await _compile_all(
        config,
        tokenizer,
        plan,
        account,
        (
            (root_entry, ("A.md",), root_index),
            (entry_a, (), index_a),
        ),
        monkeypatch,
    )

    root = _ready(t, root_entry, indices[root_entry.content_key], ("A.md",))
    ready_a = _ready(t, entry_a, indices[entry_a.content_key], ())
    capacity = plan.request_capacity(plan.generation_effective(None), 0)
    decision = select_working_set(root, (ready_a,), plan, request_envelope_tokens=capacity + 1)
    assert decision.outcome is SelectionOutcome.REQUEST_OVERFLOW
    assert selection_http_status(decision) == 422
    assert decision.working_set == ()
    assert decision.budget.request_content_tokens == capacity + 1
    assert decision.budget.request_capacity == capacity


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_selection_force_omitted_whole_entry_optional_only(
    mode: AdmissionMode, endpoint: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The deterministic whole-entry OPTIONAL omission channel of
    the application final-request budget gate (order 022-e
    section 2): a named optional content key is omitted whole and
    recorded as a BUDGET omission BEFORE the coverage and
    aggregate law (the coherent replacement/selection re-run, so
    an omitted carrier can only earn the non-resolving evidence
    marker, never a dangling live reference); the decision is
    deterministic; the root and every required binding-closure
    entry are never force-omitted (a forced required key is the
    fixed selection failure, not an omission)."""
    ns, _state, t = _states(
        ROOT_OPTIONAL,
        (("a", A_BODY, "cat A.md"), ("b", B_BODY, "cat B.md")),
        mode,
        endpoint,
        f"selection022e-force-{mode.value}-{endpoint}",
    )
    root_entry = t.admission.root_entry
    entry_a = _entry_for(t, "A.md")
    entry_b = _entry_for(t, "B.md")

    tokenizer = get_bundle_tokenizer()
    config = _config()
    plan = BundleBudgetPlan(tokenizer, BundleBudgetConfig(context_tokens=262_144))
    account = BundleCompilerAccount()

    root_index = _root_index(
        root_entry,
        config,
        tokenizer,
        plan,
        (_dep("A.md", "P1", 90, "immediate"), _dep("B.md", "P2", 50, "next_turn")),
    )
    index_a = _file_index(
        entry_a,
        (),
        config,
        tokenizer,
        plan,
        rule_id="never-mutate-fixture",
        statement="NEVER mutate the protected fixture.",
        location="A.md",
    )
    index_b = _file_index(
        entry_b,
        (),
        config,
        tokenizer,
        plan,
        rule_id="always-log-mutation",
        statement="ALWAYS log the mutation.",
        location="B.md",
    )
    indices = await _compile_all(
        config,
        tokenizer,
        plan,
        account,
        (
            (root_entry, ("A.md", "B.md"), root_index),
            (entry_a, (), index_a),
            (entry_b, (), index_b),
        ),
        monkeypatch,
    )

    root = _ready(t, root_entry, indices[root_entry.content_key], ("A.md", "B.md"))
    ready_a = _ready(t, entry_a, indices[entry_a.content_key], ())
    ready_b = _ready(t, entry_b, indices[entry_b.content_key], ())

    baseline = select_working_set(root, (ready_a, ready_b), plan)
    assert baseline.outcome is SelectionOutcome.OK
    assert [row.content_key for row in baseline.working_set] == [
        root_entry.content_key,
        entry_a.content_key,
        entry_b.content_key,
    ]
    assert baseline.missing_bindings == ()

    # The optional B is force-omitted whole, recorded as a BUDGET
    # omission; the working set stays coherent (root + required A).
    forced = select_working_set(
        root, (ready_a, ready_b), plan, force_omitted=(entry_b.content_key,)
    )
    assert forced.outcome is SelectionOutcome.OK
    assert [row.content_key for row in forced.working_set] == [
        root_entry.content_key,
        entry_a.content_key,
    ]
    omitted = [o for o in forced.omitted if o.content_key == entry_b.content_key]
    assert len(omitted) == 1
    assert omitted[0].reason is SelectionOmissionReason.BUDGET
    assert omitted[0].covered_by is None
    assert omitted[0].detail == "whole-entry budget omission"
    # Deterministic: the same force set re-decides identically.
    again = select_working_set(root, (ready_a, ready_b), plan, force_omitted=(entry_b.content_key,))
    assert again.selection_key == forced.selection_key

    # Required governance is never force-omitted.
    with pytest.raises(ValueError, match="required governance is never force-omitted"):
        select_working_set(root, (ready_a, ready_b), plan, force_omitted=(entry_a.content_key,))
    with pytest.raises(ValueError, match="governing root row is never force-omitted"):
        select_working_set(root, (ready_a, ready_b), plan, force_omitted=(root_entry.content_key,))
