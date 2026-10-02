"""Order 015-a (P02): typed output truncation and bounded adaptive retry.

Deterministic fake-upstream regressions for the length-completion contract:
explicit ``finish_reason == "length"`` yields the typed ``OUTPUT_TRUNCATED``
outcome before any content JSON/schema validation, the token allowance
doubles deterministically up to the configured ceiling, no known-insufficient
allowance is ever repeated, no partial output is validated or persisted, and
the metric/pipeline surface reports the typed reason without any
source/path/identity/content in labels.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from typing import Any

import httpx
import pytest
from prometheus_client import generate_latest
from pydantic import ValidationError

from slaif_local_coding.constitution.cache import (
    CachePolicy,
    DerivedIndexCache,
    cache_key,
)
from slaif_local_coding.constitution.compiler import (
    CompilerSettings,
    ConstitutionalCompiler,
)
from slaif_local_coding.constitution.compiler_models import (
    COMPILER_VERSION,
    AcquisitionUrgency,
    CompiledDependency,
    CompiledIndex,
    CompiledRule,
    ConstitutionalClass,
    FailureReason,
    RuleStrength,
)
from slaif_local_coding.constitution.models import CandidateReference, EvidenceRecord, EvidenceType
from tests.test_compiler import (
    CANDIDATE,
    SOURCE_HASH,
    compile_one,
    identity,
    index,
    metadata,
    openai_output,
)
from tests.test_compiler import (
    settings as compiler_settings,
)

# The behavior bump: old and new compilation policies must not be confused.
assert COMPILER_VERSION == "compiler-v3"


def cache_for(tmp_path: Any) -> DerivedIndexCache:
    return DerivedIndexCache(
        CachePolicy(
            root=tmp_path / "cache",
            fallback_root=None,
            max_total_bytes=100_000,
            max_entry_bytes=100_000,
            max_pinned_bytes=100_000,
            max_entries=10,
            ttl_seconds=60,
            max_scan_entries=32,
        )
    )


def truncated_envelope(*, content: str) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "id": "sanitized",
            "object": "chat.completion",
            "model": "test-model",
            "choices": [
                {
                    "index": 0,
                    "finish_reason": "length",
                    "message": {"role": "assistant", "content": content},
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 3000, "total_tokens": 3010},
        },
    )


def envelope(
    *,
    content: str,
    finish_reason: str = "stop",
    mutate_choice: Any = None,
) -> httpx.Response:
    choice = {
        "index": 0,
        "finish_reason": finish_reason,
        "message": {"role": "assistant", "content": content},
    }
    if mutate_choice is not None:
        mutate_choice(choice)
    return httpx.Response(
        200,
        json={
            "id": "sanitized",
            "object": "chat.completion",
            "model": "test-model",
            "choices": [choice],
            "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
        },
    )


async def run_with(
    tmp_path: Any,
    monkeypatch: pytest.MonkeyPatch,
    responses: list[httpx.Response],
    *,
    cache: DerivedIndexCache | None = None,
    **settings_changes: Any,
) -> tuple[Any, list[int], str]:
    """Run one compilation against queued fake responses.

    Returns (result, max_tokens per attempt, prometheus registry text).
    """
    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")
    seen_max_tokens: list[int] = []
    queued = list(responses)
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_max_tokens.append(json.loads(request.content)["max_tokens"])
        choice = queued[min(calls["n"], len(queued) - 1)]
        calls["n"] += 1
        return choice

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        compiler = ConstitutionalCompiler(
            compiler_settings(tmp_path, **settings_changes), cache=cache, client=client
        )
        result = await compile_one(compiler)
        registry_text = generate_latest(compiler.registry).decode()
        await compiler.aclose()
    return result, seen_max_tokens, registry_text


# ---------------------------------------------------------------------------
# Typed truncation before content validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_length_finished_incomplete_content_is_truncated_never_invalid_json(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    incomplete = '{"schema_version":"constitution-index-v1","rules":['  # syntactically incomplete
    result, seen, registry_text = await run_with(
        tmp_path,
        monkeypatch,
        [truncated_envelope(content=incomplete)] * 2,
        max_attempts=2,
    )
    assert not result.ok
    assert result.failure is not None
    assert result.failure.reason is FailureReason.OUTPUT_TRUNCATED
    assert result.failure.attempts == 2
    assert seen == [3000, 6000]  # doubled below the 8000 ceiling
    assert "slaif_constitution_compiler_truncations_total 2.0" in registry_text
    assert 'reason="invalid_json"' not in registry_text


@pytest.mark.asyncio
async def test_length_finished_valid_json_still_truncates_and_never_caches(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Even a coincidentally complete-looking body with finish_reason=length is
    truncation: it must never be validated, cached, or returned."""
    full = json.dumps(index().model_dump(mode="json"), separators=(",", ":"))
    cache = cache_for(tmp_path)
    result, _seen, _registry_text = await run_with(
        tmp_path,
        monkeypatch,
        [truncated_envelope(content=full), truncated_envelope(content=full)],
        max_attempts=2,
        cache=cache,
    )
    assert not result.ok
    assert result.failure is not None
    assert result.failure.reason is FailureReason.OUTPUT_TRUNCATED
    key = cache_key(
        identity(),
        source_logical_path="AGENTS.md",
        source_sha256=SOURCE_HASH,
        model="test-model",
        index_schema_version="constitution-index-v1",
        compiler_version=COMPILER_VERSION,
        prompt_policy_version="constitutional-rank-v2",
        reasoning_effort="low",
        max_source_bytes=262_144,
        max_prompt_bytes=384_000,
        max_output_tokens=3000,
        max_output_tokens_ceiling=8000,
        max_output_bytes=100_000,
        max_candidates=128,
        max_json_depth=24,
    )
    assert cache.get(key).index is None


@pytest.mark.asyncio
async def test_malformed_json_with_normal_completion_remains_invalid_json(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    result, seen, _registry_text = await run_with(
        tmp_path,
        monkeypatch,
        [envelope(content="{not json"), envelope(content="{still not json")],
        max_attempts=2,
    )
    assert not result.ok
    assert result.failure is not None
    assert result.failure.reason is FailureReason.INVALID_JSON
    assert result.failure.attempts == 2
    assert seen == [3000, 3000]  # non-truncation failures keep current retry semantics


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mutate_choice",
    [
        lambda choice: choice.pop("finish_reason"),  # missing finish_reason
        lambda choice: choice.update({"finish_reason": 42}),  # non-string
        lambda choice: choice.update({"finish_reason": "tool_calls"}),  # other reason, bad content
    ],
)
async def test_unsupported_envelopes_fail_closed_as_invalid_json(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch, mutate_choice: Any
) -> None:
    result, _seen, _registry_text = await run_with(
        tmp_path,
        monkeypatch,
        [envelope(content="{incomplete", mutate_choice=mutate_choice)] * 2,
        max_attempts=2,
    )
    assert not result.ok
    assert result.failure is not None
    assert result.failure.reason is FailureReason.INVALID_JSON


# ---------------------------------------------------------------------------
# Adaptive allowance policy
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_adaptive_success_at_doubled_allowance_caches(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    cache = cache_for(tmp_path)
    valid = openai_output(index())
    result, seen, _registry_text = await run_with(
        tmp_path,
        monkeypatch,
        [truncated_envelope(content='{"partial":'), valid],
        max_attempts=3,
        cache=cache,
    )
    assert result.ok and result.index is not None
    assert result.cache_outcome == "miss-persisted"
    assert seen == [3000, 6000]
    assert max(seen) < 8000  # remains below the default ceiling

    # A subsequent identical miss is a cache hit with zero attempts.
    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")

    def hit_handler(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("cache hit must not call upstream")

    async with httpx.AsyncClient(transport=httpx.MockTransport(hit_handler)) as client:
        compiler = ConstitutionalCompiler(compiler_settings(tmp_path), cache=cache, client=client)
        result_two = await compile_one(compiler)
        await compiler.aclose()
    assert result_two.ok
    assert result_two.cache_outcome == "hit"


@pytest.mark.asyncio
async def test_repeated_truncation_terminates_explicitly_within_bounds(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    result, seen, _registry_text = await run_with(
        tmp_path,
        monkeypatch,
        [truncated_envelope(content="{")] * 4,
        max_attempts=4,
        max_output_tokens_ceiling=16_000,
    )
    assert not result.ok
    assert result.failure is not None
    assert result.failure.reason is FailureReason.OUTPUT_TRUNCATED
    assert result.failure.attempts == 4
    # Strictly increasing allowances, capped at the ceiling, never repeated.
    assert seen == [3000, 6000, 12000, 16000]
    assert len(set(seen)) == len(seen)


@pytest.mark.asyncio
async def test_truncation_at_ceiling_stops_without_identical_retry(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    result, seen, _registry_text = await run_with(
        tmp_path,
        monkeypatch,
        [truncated_envelope(content="{")] * 4,
        max_attempts=4,
        max_output_tokens=8_000,
        max_output_tokens_ceiling=8_000,
    )
    assert not result.ok
    assert result.failure is not None
    assert result.failure.reason is FailureReason.OUTPUT_TRUNCATED
    assert result.failure.attempts == 1
    assert seen == [8000]


@pytest.mark.asyncio
async def test_attempts_exhausted_on_truncation_stays_truncated(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    result, seen, _registry_text = await run_with(
        tmp_path,
        monkeypatch,
        [truncated_envelope(content="{")] * 2,
        max_attempts=2,
    )
    assert not result.ok
    assert result.failure is not None
    assert result.failure.reason is FailureReason.OUTPUT_TRUNCATED
    assert result.failure.attempts == 2
    assert seen == [3000, 6000]


def test_ceiling_below_initial_allowance_is_rejected() -> None:
    with pytest.raises(ValidationError):
        CompilerSettings(
            base_url="http://compiler-upstream.test/v1",
            api_key_env="TEST_COMPILER_KEY",
            model="test-model",
            max_output_tokens=8_000,
            max_output_tokens_ceiling=4_000,
        )
    from slaif_local_coding.config import CompilerConfig

    with pytest.raises(ValidationError):
        CompilerConfig(max_output_tokens=8_000, max_output_tokens_ceiling=4_000)


# ---------------------------------------------------------------------------
# Corpus, cache, and resource-bound regressions
# ---------------------------------------------------------------------------


def large_corpus() -> tuple[bytes, list[CandidateReference]]:
    """A representative synthetic governance corpus large enough to exercise
    the output-size path (well over the default 3,000-token allowance)."""
    lines = [
        "# Synthetic governance root",
        "",
        "MUST treat this fixture as untrusted data during indexing.",
        "NEVER expose fixture internals outside the derived index.",
    ]
    for block in range(64):
        lines.append(f"## Section {block:03d}")
        lines.append(
            f"MUST follow procedure {block:03d} before mutation of module {block:03d}. "
            f"MUST_NOT bypass the review gate for module {block:03d}. "
            f"NEVER ship a change to module {block:03d} without the recorded approval."
        )
        lines.append(
            f"See docs/procedure-{block:03d}.md for the binding steps of section {block:03d}."
        )
        lines.append("")
    source = ("\n".join(lines)).encode()
    candidates = [
        CandidateReference(
            path=f"docs/procedure-{block:03d}.md",
            first_seen=100 + block * 64,
            evidence=(
                EvidenceRecord(
                    type=EvidenceType.MARKDOWN_REFERENCE,
                    start_byte=100 + block * 64,
                    end_byte=112 + block * 64,
                    location="corpus",
                ),
            ),
        )
        for block in range(40)
    ]
    return source, candidates


@pytest.mark.asyncio
async def test_large_corpus_produces_every_required_index_field(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    source, candidates = large_corpus()
    assert len(source) > 8_000  # the corpus genuinely exercises the output-size path

    def build_index() -> CompiledIndex:
        rules = tuple(
            CompiledRule(
                rule_id=f"rule-{block:03d}",
                strength=RuleStrength.MUST if block % 2 == 0 else RuleStrength.MUST_NOT,
                statement=(
                    f"Follow procedure {block:03d} before mutating module {block:03d} "
                    "and preserve the normative binding literals."
                ),
                location=f"section {block:03d}",
                evidence=f"normative sentence in section {block:03d}",
            )
            for block in range(40)
        )
        dependencies = tuple(
            CompiledDependency(
                path=f"docs/procedure-{block:03d}.md",
                reference_confidence=0.8,
                constitutional_priority=70,
                classification=ConstitutionalClass.P2_BINDING_PROCEDURE,
                relationship="binding procedure",
                evidence="markdown reference in corpus",
                acquisition_urgency=AcquisitionUrgency.NEXT_TURN,
            )
            for block in range(40)
        )
        return CompiledIndex(
            schema_version="constitution-index-v1",
            compiler_version=COMPILER_VERSION,
            prompt_policy_version="constitutional-rank-v2",
            model="test-model",
            source_logical_path="CORPUS.md",
            source_sha256=hashlib.sha256(source).hexdigest(),
            source_byte_length=len(source),
            summary="Bounded synthetic governance corpus summary.",
            rules=rules,
            roles=("coding agent", "strategic agent", "human"),
            authorities=("human", "strategic"),
            source_of_truth_boundaries=("repository truth overrides derived index",),
            ordering_constraints=("P0 before P1",),
            exceptions=("explicit human override",),
            dependencies=dependencies,
            reread_triggers=("corpus hash changes", "procedure file changes"),
        )

    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")
    valid = openai_output(build_index())

    state = {"calls": 0}

    def stateful_handler(request: httpx.Request) -> httpx.Response:
        state["calls"] += 1
        if state["calls"] == 1:
            return truncated_envelope(content='{"partial":')
        return valid

    async with httpx.AsyncClient(transport=httpx.MockTransport(stateful_handler)) as client:
        compiler = ConstitutionalCompiler(
            compiler_settings(tmp_path, max_attempts=3), client=client
        )
        result = await compiler.compile(
            source,
            "CORPUS.md",
            metadata(source, path="CORPUS.md"),
            candidates,
            identity(),
        )
        await compiler.aclose()

    assert result.ok and result.index is not None
    index_fields = result.index
    assert len(index_fields.rules) == 40
    assert len(index_fields.dependencies) == 40
    assert [item.path for item in index_fields.dependencies] == [item.path for item in candidates]
    assert index_fields.source_byte_length == len(source)
    assert len(index_fields.roles) == 3
    assert len(index_fields.authorities) == 2
    assert len(index_fields.source_of_truth_boundaries) == 1
    assert len(index_fields.ordering_constraints) == 1
    assert len(index_fields.exceptions) == 1
    assert len(index_fields.reread_triggers) == 2


@pytest.mark.asyncio
async def test_failed_compilations_write_no_cache_entry(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")
    cache = cache_for(tmp_path)
    key = cache_key(
        identity(),
        source_logical_path="AGENTS.md",
        source_sha256=SOURCE_HASH,
        model="test-model",
        index_schema_version="constitution-index-v1",
        compiler_version=COMPILER_VERSION,
        prompt_policy_version="constitutional-rank-v2",
        reasoning_effort="low",
        max_source_bytes=262_144,
        max_prompt_bytes=384_000,
        max_output_tokens=3000,
        max_output_tokens_ceiling=8000,
        max_output_bytes=1024,
        max_candidates=128,
        max_json_depth=24,
    )

    # 1. truncation exhaustion
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _r: truncated_envelope(content="{"))
    ) as client:
        compiler = ConstitutionalCompiler(
            compiler_settings(tmp_path, max_attempts=2, max_output_bytes=1024),
            cache=cache,
            client=client,
        )
        result = await compile_one(compiler)
        await compiler.aclose()
    assert result.failure is not None
    assert result.failure.reason is FailureReason.OUTPUT_TRUNCATED
    assert cache.get(key).index is None

    # 2. completed invalid JSON
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _r: envelope(content="{nope"))
    ) as client:
        compiler = ConstitutionalCompiler(
            compiler_settings(tmp_path, max_attempts=2, max_output_bytes=1024),
            cache=cache,
            client=client,
        )
        result = await compile_one(compiler)
        await compiler.aclose()
    assert result.failure is not None
    assert result.failure.reason is FailureReason.INVALID_JSON
    assert cache.get(key).index is None

    # 3. local output overflow (response byte bound)
    big = json.dumps(index().model_dump(mode="json"), separators=(",", ":")) * 30
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _r: envelope(content=big))
    ) as client:
        compiler = ConstitutionalCompiler(
            compiler_settings(tmp_path, max_attempts=2, max_output_bytes=1024),
            cache=cache,
            client=client,
        )
        result = await compile_one(compiler)
        await compiler.aclose()
    assert result.failure is not None
    assert result.failure.reason is FailureReason.OUTPUT_TOO_LARGE
    assert cache.get(key).index is None


@pytest.mark.asyncio
async def test_json_depth_bound_still_enforced_for_completed_output(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    deep = "[" * 30 + "]" * 30  # deeper than max_json_depth=24
    result, _seen, _registry_text = await run_with(
        tmp_path,
        monkeypatch,
        [envelope(content=deep)] * 2,
        max_attempts=2,
    )
    assert not result.ok
    assert result.failure is not None
    assert result.failure.reason is FailureReason.NESTING_TOO_DEEP


@pytest.mark.asyncio
async def test_timeout_bound_still_enforced(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    async def slow_handler(_request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(5.0)
        return openai_output(index())

    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(slow_handler), timeout=None
    ) as client:
        compiler = ConstitutionalCompiler(
            compiler_settings(tmp_path, timeout_seconds=0.2, max_attempts=2), client=client
        )
        result = await compile_one(compiler)
        await compiler.aclose()
    assert not result.ok
    assert result.failure is not None
    assert result.failure.reason is FailureReason.UPSTREAM_TIMEOUT


@pytest.mark.asyncio
async def test_cancellation_during_adaptive_retry_releases_slot(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    released = asyncio.Event()

    async def gated_handler(request: httpx.Request) -> httpx.Response:
        await released.wait()
        return truncated_envelope(content="{")

    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(gated_handler), timeout=None
    ) as client:
        compiler = ConstitutionalCompiler(
            compiler_settings(tmp_path, max_attempts=2), client=client
        )
        task = asyncio.create_task(compile_one(compiler))
        await asyncio.sleep(0.05)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        released.set()
        # The global slot is released: a second compilation can now run.
        import httpx as _httpx

        second = openai_output(index())

        async def ok_handler(_request: _httpx.Request) -> _httpx.Response:
            return second

        async with _httpx.AsyncClient(transport=_httpx.MockTransport(ok_handler)) as client_two:
            compiler_two = ConstitutionalCompiler(compiler_settings(tmp_path), client=client_two)
            result = await compile_one(compiler_two)
            await compiler_two.aclose()
        assert result.ok
    await compiler.aclose()


# ---------------------------------------------------------------------------
# Identity binding: fingerprints and cache keys bind both allowances
# ---------------------------------------------------------------------------


def test_fingerprint_and_cache_key_bind_initial_and_ceiling(
    tmp_path: Any,
) -> None:
    def make(ceiling: int) -> ConstitutionalCompiler:
        return ConstitutionalCompiler(
            CompilerSettings(
                base_url="http://compiler-upstream.test/v1",
                api_key_env="TEST_COMPILER_KEY",
                model="test-model",
                max_output_tokens_ceiling=ceiling,
            )
        )

    compiler_a = make(8_000)
    compiler_b = make(16_000)
    ident = identity()
    fingerprint_a = compiler_a._request_fingerprint(
        ident, source_hash=SOURCE_HASH, logical_path="AGENTS.md", candidates=(CANDIDATE,)
    )
    fingerprint_b = compiler_b._request_fingerprint(
        ident, source_hash=SOURCE_HASH, logical_path="AGENTS.md", candidates=(CANDIDATE,)
    )
    assert fingerprint_a != fingerprint_b

    key_a = cache_key(
        ident,
        source_logical_path="AGENTS.md",
        source_sha256=SOURCE_HASH,
        model="test-model",
        index_schema_version="constitution-index-v1",
        compiler_version=COMPILER_VERSION,
        prompt_policy_version="constitutional-rank-v2",
        reasoning_effort="low",
        max_source_bytes=262_144,
        max_prompt_bytes=384_000,
        max_output_tokens=3000,
        max_output_tokens_ceiling=8000,
        max_output_bytes=100_000,
        max_candidates=128,
        max_json_depth=24,
    )
    key_b = cache_key(
        ident,
        source_logical_path="AGENTS.md",
        source_sha256=SOURCE_HASH,
        model="test-model",
        index_schema_version="constitution-index-v1",
        compiler_version=COMPILER_VERSION,
        prompt_policy_version="constitutional-rank-v2",
        reasoning_effort="low",
        max_source_bytes=262_144,
        max_prompt_bytes=384_000,
        max_output_tokens=3000,
        max_output_tokens_ceiling=16_000,
        max_output_bytes=100_000,
        max_candidates=128,
        max_json_depth=24,
    )
    assert key_a != key_b


def test_version_bump_separates_old_and_new_policies() -> None:
    old_version_key = cache_key(
        identity(),
        source_logical_path="AGENTS.md",
        source_sha256=SOURCE_HASH,
        model="test-model",
        index_schema_version="constitution-index-v1",
        compiler_version="compiler-v2",  # the pre-015-a compiler policy
        prompt_policy_version="constitutional-rank-v2",
        reasoning_effort="low",
        max_source_bytes=262_144,
        max_prompt_bytes=384_000,
        max_output_tokens=3000,
        max_output_tokens_ceiling=8000,
        max_output_bytes=100_000,
        max_candidates=128,
        max_json_depth=24,
    )
    new_version_key = cache_key(
        identity(),
        source_logical_path="AGENTS.md",
        source_sha256=SOURCE_HASH,
        model="test-model",
        index_schema_version="constitution-index-v1",
        compiler_version=COMPILER_VERSION,
        prompt_policy_version="constitutional-rank-v2",
        reasoning_effort="low",
        max_source_bytes=262_144,
        max_prompt_bytes=384_000,
        max_output_tokens=3000,
        max_output_tokens_ceiling=8000,
        max_output_bytes=100_000,
        max_candidates=128,
        max_json_depth=24,
    )
    assert old_version_key != new_version_key


# ---------------------------------------------------------------------------
# Pipeline-level: typed degradation and adaptive recovery with injection
# ---------------------------------------------------------------------------


def _pipeline_settings(tmp_path: Any) -> Any:
    from slaif_local_coding.config import (
        CacheConfig,
        CompilerConfig,
        ConstitutionIntegrationConfig,
        RouteConfig,
        ServerConfig,
        Settings,
        UpstreamConfig,
    )

    return Settings(
        server=ServerConfig(request_body_max_bytes=8192),
        upstream=UpstreamConfig(
            base_url="http://upstream.test/v1",
            api_key_env="TEST_PIPELINE_KEY",
            model="test-model",
        ),
        routes=[
            RouteConfig(
                name="constitution-route",
                model="test-model",
                max_images_per_request=1,
                image_overflow_policy="retain_newest",
                observation_enabled=True,
                constitution_enabled=True,
            )
        ],
        compiler=CompilerConfig(enabled=True, api_key_env="TEST_PIPELINE_KEY", max_attempts=2),
        cache=CacheConfig(
            root=tmp_path / "cache",
            fallback_root=None,
            max_total_bytes=1024 * 1024,
            max_entry_bytes=256 * 1024,
            max_pinned_bytes=256 * 1024,
            max_entries=16,
            ttl_seconds=300,
            max_scan_entries=64,
        ),
        constitution=ConstitutionIntegrationConfig(
            enabled=True,
            principal="local-principal",
            session="local-session",
            repository="local-repository",
        ),
    )


async def _pipeline_exchange(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch, compiler_responses: list[httpx.Response]
) -> tuple[httpx.Response, bytes, str]:
    from tests.test_pipeline import SOURCE_TEXT

    monkeypatch.setenv("TEST_PIPELINE_KEY", "test-only-secret")
    settings = _pipeline_settings(tmp_path)
    queued = list(compiler_responses)
    calls = {"n": 0}
    proxy_body: dict[str, bytes] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            choice = queued[min(calls["n"], len(queued) - 1)]
            calls["n"] += 1
            return choice
        assert request.url.path == "/v1/responses"
        proxy_body["raw"] = await request.aread()
        return httpx.Response(200, json={"id": "sanitized"})

    from slaif_local_coding.app import create_app

    app = create_app(settings, httpx.MockTransport(handler))
    payload = {
        "model": "test-model",
        "input": [{"type": "input_file", "filename": "AGENTS.md", "content": SOURCE_TEXT}],
    }
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        response = await client.post("/v1/responses", json=payload)
        metrics = (await client.get("/metrics")).text
    return response, proxy_body["raw"], metrics


@pytest.mark.asyncio
async def test_pipeline_degrades_with_typed_truncation_reason(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    truncated = truncated_envelope(content='{"schema_version":"constitution-index-v1","rules":[')
    response, proxy_body, metrics = await _pipeline_exchange(
        tmp_path, monkeypatch, [truncated, truncated]
    )
    assert response.status_code == 200
    # The governance-bearing original request is preserved, not deleted.
    forwarded = json.loads(proxy_body)
    assert forwarded["input"][0]["content"]
    assert (
        'reason="compiler_output_truncated",route="constitution-route",state="degraded"' in metrics
    )
    assert "slaif_constitution_compiler_truncations_total 2.0" in metrics
    # No source/path/identity/content in any metric label.
    assert "AGENTS.md" not in metrics
    assert "local-session" not in metrics
    assert "constitution-index-v1" not in metrics


@pytest.mark.asyncio
async def test_pipeline_injects_after_adaptive_truncation_recovery(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    from tests.test_pipeline import index as pipeline_index

    truncated = truncated_envelope(content='{"schema_version":"constitution-index-v1","rules":[')
    valid = httpx.Response(
        200,
        json={
            "id": "sanitized",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": json.dumps(
                            pipeline_index().model_dump(mode="json"), separators=(",", ":")
                        ),
                    },
                }
            ],
        },
    )
    response, proxy_body, metrics = await _pipeline_exchange(
        tmp_path, monkeypatch, [truncated, valid]
    )
    assert response.status_code == 200
    forwarded = json.loads(proxy_body)
    # Successful treatment delivery: the injected constitution is present in
    # the forwarded request's stable injection location and the pipeline
    # reports an injected state.
    instructions = forwarded.get("instructions", "")
    assert "SLAIF_RECONSTRUCTED_CONSTITUTION" in instructions
    assert 'state="injected"' in metrics
    assert "slaif_constitution_compiler_truncations_total 1.0" in metrics
    # The request finished injected, not degraded: no compiler-truncation
    # reason appears on the pipeline request outcome.
    assert 'state="degraded"' not in metrics
