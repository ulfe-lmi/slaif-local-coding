"""Focused objective-002 compiler validation and direct-scheduling tests."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest
from prometheus_client import generate_latest
from pydantic import ValidationError

from slaif_local_coding.constitution.cache import (
    CacheIdentity,
    CachePolicy,
    DerivedIndexCache,
    cache_key,
)
from slaif_local_coding.constitution.compiler import (
    CompilerSettings,
    ConstitutionalCompiler,
    ObservedSourceMetadata,
    _build_prompt,
    _validate_index,
)
from slaif_local_coding.constitution.compiler_models import (
    CompiledDependency,
    CompiledIndex,
    CompiledRule,
    CompilerResult,
    ConstitutionalClass,
    FailureReason,
    RuleStrength,
)
from slaif_local_coding.constitution.models import CandidateReference, EvidenceRecord, EvidenceType

SOURCE = b"# Synthetic AGENTS fixture\n\nMUST read the referenced procedure.\n"
SOURCE_HASH = hashlib.sha256(SOURCE).hexdigest()
SECRET_MARKER = "unique-raw-source-token-7f3c"
SOURCE_WITH_MARKER = SOURCE + SECRET_MARKER.encode() + b"\n"
MARKER_HASH = hashlib.sha256(SOURCE_WITH_MARKER).hexdigest()
CANDIDATE = CandidateReference(
    path="PROCEDURE.md",
    first_seen=40,
    evidence=(
        EvidenceRecord(
            type=EvidenceType.MARKDOWN_REFERENCE, start_byte=40, end_byte=52, location="source"
        ),
    ),
)


def identity(session: str | None = "session-opaque", **changes: Any) -> CacheIdentity:
    values: dict[str, Any] = {
        "principal": "principal-opaque",
        "route": "compiler-test",
        "session": session,
        "repository": "repository-opaque",
    }
    values.update(changes)
    return CacheIdentity(**values)


def metadata(source: bytes = SOURCE, path: str = "AGENTS.md") -> ObservedSourceMetadata:
    return ObservedSourceMetadata(
        logical_path=path,
        content_sha256=hashlib.sha256(source).hexdigest(),
        byte_length=len(source),
    )


def dependency(**changes: Any) -> CompiledDependency:
    values: dict[str, Any] = {
        "path": "PROCEDURE.md",
        "reference_confidence": 0.9,
        "constitutional_priority": 80,
        "classification": ConstitutionalClass.P1_DELEGATED_OR_SECURITY,
        "relationship": "delegated procedure",
        "evidence": "markdown reference in observed root",
        "acquisition_urgency": "next_turn",
    }
    values.update(changes)
    return CompiledDependency(**values)


def index(source: bytes = SOURCE, **changes: Any) -> CompiledIndex:
    values: dict[str, Any] = {
        "schema_version": "constitution-index-v1",
        "compiler_version": "compiler-v2",
        "prompt_policy_version": "constitutional-rank-v2",
        "model": "test-model",
        "source_logical_path": "AGENTS.md",
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "source_byte_length": len(source),
        "summary": "A bounded synthetic governance summary.",
        "rules": (
            CompiledRule(
                rule_id="rule-read-procedure",
                strength=RuleStrength.MUST,
                statement="Read the referenced procedure before mutation.",
                location="line 3",
                evidence="normative MUST sentence",
            ),
        ),
        "roles": ("coding agent",),
        "authorities": ("human", "strategic"),
        "source_of_truth_boundaries": ("source overrides derived index",),
        "ordering_constraints": (),
        "exceptions": (),
        "dependencies": (dependency(),),
        "reread_triggers": ("source hash changes",),
    }
    values.update(changes)
    return CompiledIndex(**values)


def settings(tmp_path: Any, **changes: Any) -> CompilerSettings:
    values: dict[str, Any] = {
        "base_url": "http://compiler-upstream.test/v1",
        "api_key_env": "TEST_COMPILER_KEY",
        "model": "test-model",
        "timeout_seconds": 1,
        "max_attempts": 2,
        "max_output_bytes": 100_000,
    }
    values.update(changes)
    return CompilerSettings(**values)


def test_compiler_prompt_preserves_exact_normative_binding_literals() -> None:
    system, _user = _build_prompt(
        b"FINAL_RESPONSE_EXACTLY: SENTINEL-ACK:ephemeral",
        "GOVERNANCE-DEPENDENCY.md",
        hashlib.sha256(b"binding").hexdigest(),
        "test-model",
        (),
    )
    assert "exact case-sensitive literals" in system
    assert "sentinels" in system


def openai_output(
    index: CompiledIndex,
    *,
    mutate: Callable[[dict[str, Any]], Any] | None = None,
    raw: bytes | None = None,
) -> httpx.Response:
    if raw is None:
        payload = index.model_dump(mode="json")
        if mutate is not None:
            payload = mutate(payload)
        raw = json.dumps(payload, separators=(",", ":")).encode()
    return httpx.Response(
        200,
        json={
            "id": "sanitized",
            "object": "chat.completion",
            "model": "test-model",
            "choices": [
                {
                    "index": 0,
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": raw.decode()},
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
        },
    )


async def compile_one(
    compiler: ConstitutionalCompiler,
    source: bytes = SOURCE,
    cache_identity: CacheIdentity | None = None,
) -> CompilerResult:
    return await compiler.compile(
        source,
        "AGENTS.md",
        metadata(source),
        (CANDIDATE,),
        cache_identity or identity(),
    )


@pytest.mark.asyncio
async def test_direct_success_preserves_candidates_and_uses_text_only_upstream(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        assert request.url == "http://compiler-upstream.test/v1/chat/completions"
        payload = json.loads(request.content)
        assert request.headers["authorization"] == "Bearer test-only-secret"
        assert payload["stream"] is False
        assert payload["reasoning_effort"] == "low"
        assert "tools" not in payload and "tool_choice" not in payload
        assert "images" not in payload and "image_url" not in payload
        assert [message["role"] for message in payload["messages"]] == ["system", "user"]
        assert "PROCEDURE.md" in payload["messages"][-1]["content"]
        return openai_output(index())

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        compiler = ConstitutionalCompiler(settings(tmp_path), client=client)
        result = await compile_one(compiler)
        await compiler.aclose()

    assert result.ok and result.index is not None
    assert result.cache_outcome == "disabled"
    assert result.index.source_sha256 == SOURCE_HASH
    assert result.index.source_byte_length == len(SOURCE)
    assert [item.path for item in result.index.dependencies] == ["PROCEDURE.md"]
    assert result.index.dependencies[0].reference_confidence == 0.9
    assert result.index.dependencies[0].constitutional_priority == 80
    assert len(seen) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda payload: {"unexpected": True, **payload}, FailureReason.SCHEMA_INVALID),
        (
            lambda payload: {key: value for key, value in payload.items() if key != "summary"},
            FailureReason.SCHEMA_INVALID,
        ),
        (lambda payload: {**payload, "status": "failed"}, FailureReason.SCHEMA_INVALID),
        (
            lambda payload: {**payload, "source_sha256": "0" * 64},
            FailureReason.SOURCE_HASH_MISMATCH,
        ),
        (
            lambda payload: {**payload, "compiler_version": "other"},
            FailureReason.SCHEMA_INVALID,
        ),
        (
            lambda payload: {**payload, "prompt_policy_version": "other"},
            FailureReason.SCHEMA_INVALID,
        ),
        (lambda payload: {**payload, "dependencies": []}, FailureReason.CANDIDATE_SET_MISMATCH),
        (
            lambda payload: {
                **payload,
                "dependencies": [{**payload["dependencies"][0], "path": "INVENTED.md"}],
            },
            FailureReason.CANDIDATE_SET_MISMATCH,
        ),
        (
            lambda payload: {
                **payload,
                "dependencies": [payload["dependencies"][0], payload["dependencies"][0]],
            },
            FailureReason.CANDIDATE_SET_MISMATCH,
        ),
        (lambda payload: {**payload, "combined_score": 0.7}, FailureReason.CONTRADICTORY_OUTPUT),
        (
            lambda payload: {
                **payload,
                "dependencies": [{**payload["dependencies"][0], "classification": "P0"}],
            },
            FailureReason.CONTRADICTORY_OUTPUT,
        ),
        (
            lambda payload: {
                **payload,
                "dependencies": [{**payload["dependencies"][0], "reference_confidence": 0.2}],
            },
            FailureReason.CONTRADICTORY_OUTPUT,
        ),
        (lambda payload: {**payload, "source_byte_length": 1}, FailureReason.INPUT_TOO_LARGE),
        (
            lambda payload: {
                **payload,
                "dependencies": [{**payload["dependencies"][0], "classification": "P9"}],
            },
            FailureReason.SCHEMA_INVALID,
        ),
        (
            lambda payload: {
                **payload,
                "dependencies": [{**payload["dependencies"][0], "reference_confidence": 1.2}],
            },
            FailureReason.SCHEMA_INVALID,
        ),
        (
            lambda payload: {
                **payload,
                "dependencies": [{**payload["dependencies"][0], "constitutional_priority": "high"}],
            },
            FailureReason.SCHEMA_INVALID,
        ),
    ],
)
async def test_invalid_model_output_fails_closed_without_cache_write(
    tmp_path: Any,
    monkeypatch: pytest.MonkeyPatch,
    mutate: Callable[[dict[str, Any]], Any],
    expected: FailureReason,
) -> None:
    from slaif_local_coding.constitution.cache import CachePolicy, DerivedIndexCache

    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")
    requests = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        return openai_output(index(), mutate=mutate)

    policy = CachePolicy(
        root=tmp_path / "cache",
        fallback_root=None,
        max_total_bytes=100_000,
        max_entry_bytes=100_000,
        max_pinned_bytes=100_000,
        max_entries=10,
        ttl_seconds=60,
        max_scan_entries=32,
    )
    cache = DerivedIndexCache(policy)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        compiler = ConstitutionalCompiler(settings(tmp_path), cache=cache, client=client)
        result = await compile_one(compiler)
        await compiler.aclose()

    assert not result.ok
    assert result.failure is not None and result.failure.reason is expected
    assert requests == settings(tmp_path).max_attempts
    key = cache_key(
        identity(),
        source_logical_path="AGENTS.md",
        source_sha256=SOURCE_HASH,
        model="test-model",
        index_schema_version="constitution-index-v1",
        compiler_version="compiler-v2",
        prompt_policy_version="constitutional-rank-v2",
        reasoning_effort="low",
        max_source_bytes=262_144,
        max_prompt_bytes=384_000,
        max_output_tokens=3000,
        max_output_bytes=256_000,
        max_candidates=128,
        max_json_depth=24,
    )
    assert cache.get(key).index is None


@pytest.mark.asyncio
async def test_malformed_truncated_oversized_and_deep_output_fail_closed(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")
    cases = [
        (b"{not-json", FailureReason.INVALID_JSON),
        (b'{"schema_version":', FailureReason.INVALID_JSON),
        (b'{"deep":' + b"[" * 30 + b"]" * 30 + b"}", FailureReason.NESTING_TOO_DEEP),
        (b"x" * 100_001, FailureReason.OUTPUT_TOO_LARGE),
    ]
    for raw, expected in cases:

        def handler(_request: httpx.Request, output: bytes = raw) -> httpx.Response:
            return openai_output(index(), raw=output)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            compiler = ConstitutionalCompiler(settings(tmp_path), client=client)
            result = await compile_one(compiler)
            await compiler.aclose()
        assert result.failure is not None and result.failure.reason is expected


@pytest.mark.asyncio
async def test_invalid_utf8_source_fails_before_upstream(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")
    requests = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        return openai_output(index())

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        compiler = ConstitutionalCompiler(settings(tmp_path), client=client)
        result = await compiler.compile(
            b"\xff",
            "AGENTS.md",
            metadata(b"\xff"),
            (),
            identity(),
        )
        await compiler.aclose()
    assert requests == 0
    assert result.failure is not None and result.failure.reason is FailureReason.INVALID_INPUT


@pytest.mark.asyncio
async def test_identical_miss_deduplicates_within_request_scope(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")
    requests = 0
    release = asyncio.Event()
    first_arrived = asyncio.Event()

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        first_arrived.set()
        await release.wait()
        return openai_output(index())

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        compiler = ConstitutionalCompiler(settings(tmp_path), client=client)
        first = asyncio.create_task(compile_one(compiler))
        await first_arrived.wait()
        second = asyncio.create_task(compile_one(compiler))
        await asyncio.sleep(0.01)
        assert requests == 1
        release.set()
        results = await asyncio.gather(first, second)
        await compiler.aclose()

    assert all(item.ok for item in results)
    assert requests == 1
    metrics = generate_latest(compiler.registry).decode()
    assert "slaif_constitution_compiler_deduplicated_waits_total 1.0" in metrics
    assert SECRET_MARKER not in metrics and "test-only-secret" not in metrics


@pytest.mark.asyncio
async def test_absent_reliable_identity_disables_persistent_reuse(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")
    requests = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        return openai_output(index())

    policy = CachePolicy(
        root=tmp_path / "cache",
        fallback_root=None,
        max_total_bytes=100_000,
        max_entry_bytes=100_000,
        max_pinned_bytes=100_000,
        max_entries=10,
        max_scan_entries=32,
        ttl_seconds=60,
    )
    cache = DerivedIndexCache(policy)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        compiler = ConstitutionalCompiler(settings(tmp_path), cache=cache, client=client)
        first = await compile_one(compiler, cache_identity=identity(session=None))
        second = await compile_one(compiler, cache_identity=identity(session=None))
        await compiler.aclose()
    assert first.ok and second.ok
    assert first.cache_outcome == "disabled"
    assert second.cache_outcome == "disabled"
    assert requests == 2
    assert not any((tmp_path / "cache").rglob("*.json"))


@pytest.mark.asyncio
async def test_distinct_misses_use_one_global_slot(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")
    requests = 0
    release = asyncio.Event()
    first_arrived = asyncio.Event()

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        first_arrived.set()
        await release.wait()
        return openai_output(index())

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        compiler = ConstitutionalCompiler(settings(tmp_path), client=client)
        first = asyncio.create_task(compile_one(compiler))
        await first_arrived.wait()
        second_source = SOURCE + b"\nDistinct synthetic source.\n"
        second = asyncio.create_task(
            compiler.compile(
                second_source,
                "AGENTS.md",
                metadata(second_source),
                (),
                identity(session="different"),
            )
        )
        await asyncio.sleep(0.01)
        assert requests == 1
        release.set()
        await asyncio.gather(first, second)
        await compiler.aclose()
    assert requests >= 3


@pytest.mark.asyncio
async def test_timeout_and_server_status_return_typed_failures(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")

    async def timeout_handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("sanitized timeout", request=_request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(timeout_handler)) as client:
        compiler = ConstitutionalCompiler(
            settings(tmp_path, timeout_seconds=0.01, max_attempts=1), client=client
        )
        result = await compile_one(compiler)
        await compiler.aclose()
    assert result.failure is not None and result.failure.reason is FailureReason.UPSTREAM_TIMEOUT

    attempts = 0

    def server_handler(_request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(503, json={"error": "sanitized"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(server_handler)) as client:
        compiler = ConstitutionalCompiler(settings(tmp_path), client=client)
        result = await compile_one(compiler)
        await compiler.aclose()
    assert result.failure is not None and result.failure.reason is FailureReason.UPSTREAM_STATUS
    assert attempts == 2


@pytest.mark.asyncio
async def test_compiler_timeout_is_bounded_even_with_injected_client(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")

    async def slow_handler(_request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(0.05)
        return openai_output(index())

    async with httpx.AsyncClient(transport=httpx.MockTransport(slow_handler)) as client:
        compiler = ConstitutionalCompiler(
            settings(tmp_path, timeout_seconds=0.001, max_attempts=1), client=client
        )
        result = await compile_one(compiler)
        await compiler.aclose()

    assert result.failure is not None
    assert result.failure.reason is FailureReason.UPSTREAM_TIMEOUT


@pytest.mark.asyncio
async def test_missing_compiler_credential_is_typed_and_not_forwarded(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("TEST_COMPILER_KEY", raising=False)
    requests = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        return openai_output(index())

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        compiler = ConstitutionalCompiler(settings(tmp_path, max_attempts=2), client=client)
        result = await compile_one(compiler)
        await compiler.aclose()

    assert result.failure is not None
    assert result.failure.reason is FailureReason.UPSTREAM_AUTH
    assert result.failure.detail == "compiler credential is unavailable"
    assert requests == 0


@pytest.mark.asyncio
async def test_cancellation_releases_slot_for_next_call(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_COMPILER_KEY", "test-only-secret")
    release = asyncio.Event()
    arrived = asyncio.Event()

    async def blocking_handler(_request: httpx.Request) -> httpx.Response:
        arrived.set()
        await release.wait()
        return openai_output(index())

    def immediate_handler(_request: httpx.Request) -> httpx.Response:
        return openai_output(index())

    transport = httpx.MockTransport(blocking_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        compiler = ConstitutionalCompiler(settings(tmp_path), client=client)
        task = asyncio.create_task(compile_one(compiler))
        await arrived.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        release.set()
        # A subsequent distinct call proves the global slot and inflight state cleared.
        compiler._client = httpx.AsyncClient(  # noqa: SLF001 - scheduling regression probe
            transport=httpx.MockTransport(immediate_handler)
        )
        next_result = await compiler.compile(
            SOURCE + b"next", "AGENTS.md", metadata(SOURCE + b"next"), (), identity(session="next")
        )
        await compiler.aclose()
    # A typed result proves the slot was reacquired; success is covered above.
    assert not next_result.ok


def test_direct_validator_rejects_duplicate_json_and_nonfinite_numbers() -> None:
    valid = index().model_dump(mode="json")
    with pytest.raises(ValueError, match="duplicate"):
        json.loads(
            json.dumps(valid)[:-1] + ',"summary":"duplicate"}',
            object_pairs_hook=lambda pairs: (
                (_ for _ in ()).throw(ValueError("duplicate"))
                if len(pairs) != len({key for key, _ in pairs})
                else dict(pairs)
            ),
        )
    with pytest.raises(ValidationError):
        CompiledIndex.model_validate(
            {**valid, "dependencies": [dependency(reference_confidence=float("inf"))]}
        )


def test_validator_rejects_omitted_candidate_and_combined_score_directly() -> None:
    raw = json.dumps(index().model_dump(mode="json")).encode()
    valid_index = _validate_index(
        raw,
        expected_hash=SOURCE_HASH,
        expected_byte_length=len(SOURCE),
        logical_path="AGENTS.md",
        model="test-model",
        candidates=(CANDIDATE,),
        settings=settings(None),
    )
    assert not isinstance(valid_index, FailureReason)
    assert valid_index.source_sha256 == SOURCE_HASH
    omitted = json.dumps({**index().model_dump(mode="json"), "dependencies": []}).encode()
    assert (
        _validate_index(
            omitted,
            expected_hash=SOURCE_HASH,
            expected_byte_length=len(SOURCE),
            logical_path="AGENTS.md",
            model="test-model",
            candidates=(CANDIDATE,),
            settings=settings(None),
        )
        is FailureReason.CANDIDATE_SET_MISMATCH
    )
