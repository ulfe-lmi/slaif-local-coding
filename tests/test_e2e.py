"""Focused tests for disposable real-Codex E2E support."""

from __future__ import annotations

import hashlib
import io
import json
import subprocess
import tempfile
import time
import tomllib
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Literal

import pytest

from slaif_local_coding.e2e import (
    CacheInventory,
    CacheInventoryEntry,
    GovernedFixturePaths,
    MetricDelta,
    SanitizedCodexRun,
    _classify_dependency_cache_outcome,
    _final_agent_message_has_ack,
    _reconcile_dependency_cache,
    constitution_metric_snapshot,
    governed_prompt,
    metric_value,
    parse_codex_command_events,
    parse_codex_events,
    read_persistent_cache_inventory,
    write_governed_fixture,
)


def test_fixture_is_isolated_private_and_governed() -> None:
    with tempfile.TemporaryDirectory(prefix="slaif-e2e-test-") as temporary:
        root = Path(temporary)
        fixture = write_governed_fixture(
            root, base_url="http://127.0.0.1:18031/v1", api_key_env="QWEN3090_API_KEY"
        )
        assert isinstance(fixture, GovernedFixturePaths)
        assert fixture.repository.is_dir() and fixture.codex_home.is_dir()
        assert oct(fixture.repository.stat().st_mode & 0o777) == "0o700"
        assert oct(fixture.codex_home.stat().st_mode & 0o777) == "0o700"
        assert oct(fixture.codex_config.stat().st_mode & 0o777) == "0o600"
        raw_config = fixture.codex_config.read_text(encoding="utf-8")
        parsed = tomllib.loads(raw_config)
        provider = parsed["model_providers"]["slaif-local-coding-e2e"]
        assert parsed["model_provider"] == "slaif-local-coding-e2e"
        assert parsed["model_catalog_json"] == str(fixture.model_catalog)
        assert provider["base_url"] == "http://127.0.0.1:18031/v1"
        assert provider["env_key"] == "QWEN3090_API_KEY"
        assert provider["wire_api"] == "responses"
        assert "QWEN3090_API_KEY" in raw_config
        agents = (fixture.repository / "AGENTS.md").read_text(encoding="utf-8")
        dependency = (fixture.repository / "GOVERNANCE-DEPENDENCY.md").read_text(encoding="utf-8")
        assert agents.count("# Synthetic governance fixture") == 1
        assert fixture.sentinel_token not in agents
        assert fixture.sentinel_token not in raw_config
        assert len(agents) >= 8_000
        assert "[GOVERNANCE-DEPENDENCY.md](GOVERNANCE-DEPENDENCY.md)" in agents
        assert f"SENTINEL-ACK:{fixture.sentinel_token}" in dependency
        prompt = governed_prompt()
        assert fixture.sentinel_token not in prompt
        assert "GOVERNANCE-DEPENDENCY.md" in prompt
        assert "FINAL_RESPONSE_EXACTLY" in prompt
        for path in (*fixture.repository.rglob("*"), *fixture.codex_home.rglob("*")):
            if not path.is_file() or path.name == "GOVERNANCE-DEPENDENCY.md":
                continue
            assert fixture.sentinel_token not in path.read_text(encoding="utf-8", errors="ignore")
        status = subprocess.run(
            ["git", "-C", str(fixture.repository), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
        assert status.stdout == ""


def test_runner_prompts_never_contain_delegated_sentinel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import slaif_local_coding.e2e as e2e_module

    prompts: list[str] = []
    sentinel_tokens: list[str] = []

    def fake_catalog(_codex_bin: object, _destination: object) -> None:
        return None

    def fake_run(
        _codex_bin: object, fixture: GovernedFixturePaths, prompt: str
    ) -> e2e_module.SanitizedCodexRun:
        prompts.append(prompt)
        sentinel_tokens.append(fixture.sentinel_token)
        return e2e_module.SanitizedCodexRun(
            exit_status=0,
            timed_out=False,
            duration_seconds=0.0,
            event_bytes=1,
            event_type_counts={},
            call_item_type_counts={"command_execution": 1},
            tool_names=("command_execution",),
            tool_calls=1,
            sentinel_passed=True,
            failure_reason="success",
        )

    monkeypatch.setattr(e2e_module, "write_local_model_catalog", fake_catalog)
    monkeypatch.setattr(e2e_module, "run_codex_once", fake_run)
    facts = e2e_module.run_governed_e2e("unused")
    assert facts.first_runs[-1].failure_reason == "success"
    assert facts.second_run.failure_reason == "success"
    assert len(prompts) == 2
    assert all(token not in prompt for token, prompt in zip(sentinel_tokens, prompts, strict=True))
    assert all("FINAL_RESPONSE_EXACTLY" in prompt for prompt in prompts)


def test_event_parser_exposes_only_approved_facts() -> None:
    canned = "\n".join(
        [
            '{"type":"thread.started","thread_id":"synthetic"}',
            '{"type":"item.completed","item":{"type":"function_call","name":"exec_command"}}',
            '{"type":"item.completed","item":{"type":"function_call","name":"shell","command":["secret"]}}',
            '{"type":"item.started","item":{"type":"command_execution"}}',
            '{"type":"item.completed","item":{"type":"command_execution"}}',
            '{"type":"turn.completed","usage":{"input_tokens":1}}',
            "{invalid",
        ]
    )
    counts, call_items, tools = parse_codex_events(io.StringIO(canned))
    assert counts == Counter(
        {"item.started": 1, "item.completed": 3, "thread.started": 1, "turn.completed": 1}
    )
    assert call_items == Counter({"command_execution": 2, "function_call": 2})
    assert tools == ("command_execution", "command_execution", "exec_command", "shell")


def test_final_agent_ack_is_checked_without_retaining_text() -> None:
    canned = "\n".join(
        [
            '{"type":"item.completed","item":{"type":"agent_message","text":"before"}}',
            '{"type":"item.completed","item":{"type":"command_execution"}}',
            '{"type":"item.completed","item":{"type":"agent_message","text":"SENTINEL-ACK:secret"}}',
        ]
    )

    assert _final_agent_message_has_ack(io.StringIO(canned), "SENTINEL-ACK:secret")
    assert not _final_agent_message_has_ack(io.StringIO(canned), "SENTINEL-ACK:other")


def test_governed_runner_rejects_invalid_budget(tmp_path: Path) -> None:
    from slaif_local_coding.e2e import run_governed_e2e

    with pytest.raises(ValueError, match="invalid attempt budget"):
        run_governed_e2e("unused", max_attempts=0)


def test_metric_reader_matches_fixed_labels() -> None:
    text = (
        "# HELP test_total Test\n# TYPE test_total counter\n"
        'test_total{route="e2e",outcome="miss"} 2\n'
        'test_total{route="other",outcome="miss"} 7\n'
    )
    assert metric_value(text, "test_total", route="e2e", outcome="miss") == 2.0
    assert metric_value(text, "test_total") == 9.0


def _write_cache_entry(
    cache_root: Path,
    *,
    logical_path: str,
    source: bytes,
    created_at: float,
) -> str:
    """Write one valid disposable index envelope for inventory-focused tests."""

    from slaif_local_coding.constitution.compiler_models import (
        RuleStrength,
    )

    source_hash = hashlib.sha256(source).hexdigest()
    payload = {
        "schema_version": "constitution-index-v1",
        "compiler_version": "compiler-v2",
        "prompt_policy_version": "constitutional-rank-v2",
        "model": "sanitized-model",
        "source_logical_path": logical_path,
        "source_sha256": source_hash,
        "source_byte_length": len(source),
        "summary": "Bounded synthetic summary.",
        "rules": (
            {
                "rule_id": "synthetic-rule",
                "strength": RuleStrength.MUST.value,
                "statement": "Remain bounded.",
                "location": "synthetic location",
                "evidence": "synthetic MUST",
            },
        ),
        "roles": ("coding agent",),
        "authorities": ("source",),
        "source_of_truth_boundaries": ("source overrides derived context",),
        "ordering_constraints": (),
        "exceptions": (),
        "dependencies": (),
        "reread_triggers": ("source hash changes",),
        "status": "success",
    }
    key = hashlib.sha256(f"{logical_path}:{source_hash}".encode()).hexdigest()
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    envelope = {
        "created_at": created_at,
        "key": key,
        "payload": payload,
        "payload_sha256": hashlib.sha256(payload_bytes).hexdigest(),
    }
    destination = cache_root / key[:2]
    destination.mkdir(parents=True, exist_ok=True)
    (destination / f"{key}.json").write_text(json.dumps(envelope), encoding="utf-8")
    return key


def test_command_event_lifecycle_counts_are_sanitized() -> None:
    canned = "\n".join(
        [
            '{"type":"item.started","item":{"type":"command_execution","command":"raw"}}',
            '{"type":"item.completed","item":{"type":"command_execution","status":"completed"}}',
            '{"type":"item.completed","item":{"type":"command_execution","status":"failed"}}',
            '{"type":"item.completed","item":{"type":"agent_message","text":"raw output"}}',
        ]
    )
    counts = parse_codex_command_events(io.StringIO(canned))
    assert counts == Counter({"started": 1, "completed": 1, "failed": 1})


def test_constitution_metric_snapshot_exposes_fixed_counter_deltas() -> None:
    before = constitution_metric_snapshot("")
    acquisitions = "slaif_constitution_dependency_acquisitions_total"
    canned = "\n".join(
        [
            "# HELP synthetic sanitized\n# TYPE synthetic counter",
            'slaif_constitution_roots_total{evidence_type="project_instructions",route="route"} 2',
            f'{acquisitions}{{route="route",outcome="cache_miss"}} 3',
            f'{acquisitions}{{route="route",outcome="cache_hit"}} 5',
            f'{acquisitions}{{route="route",outcome="invalid"}} 0.5',
            f'{acquisitions}{{route="route",outcome="budget_exceeded"}} 1',
            'slaif_constitution_injection_total{route="route",outcome="updated"} 7',
            "slaif_constitution_compiler_attempts_total 8",
            'slaif_constitution_compiler_successes_total{cache="miss-persisted"} 4',
            'slaif_constitution_dependency_working_set_total{route="route",status="included"} 6',
            'slaif_constitution_dependency_working_set_total{route="route",status="missing"} 1',
            'slaif_constitution_dependency_working_set_total{route="route",status="omitted"} 2',
        ]
    )
    after = constitution_metric_snapshot(canned, route="route")
    deltas = after.subtract(before)
    assert deltas["root_observations"].before == 0
    assert deltas["dependency_cache_misses"].delta == 3
    assert deltas["dependency_invalid"].after == 0.5
    assert deltas["injected_requests"].delta == 7
    assert deltas["compiler_calls"].delta == 4
    assert deltas["working_set_included"].delta == 6
    assert set(deltas) == {
        "root_observations",
        "dependency_cache_misses",
        "dependency_cache_hits",
        "dependency_invalid",
        "dependency_budget_exceeded",
        "injected_requests",
        "compiler_attempts",
        "compiler_calls",
        "working_set_included",
        "working_set_missing",
        "working_set_omitted",
    }


def test_cache_inventory_is_bounded_ordered_and_sanitized(tmp_path: Path) -> None:
    raw_marker = b"UNIQUE-RAW-SOURCE-MARKER"
    cache_root = tmp_path / "cache"
    cache_root.mkdir(mode=0o700)
    _write_cache_entry(
        cache_root,
        logical_path="AGENTS.md",
        source=b"# Synthetic root\n" + raw_marker,
        created_at=200.0,
    )
    _write_cache_entry(
        cache_root,
        logical_path="GOVERNANCE.md",
        source=b"Synthetic dependency\n" + raw_marker,
        created_at=100.0,
    )
    invalid = cache_root / "zz" / "invalid.json"
    invalid.parent.mkdir()
    invalid.write_text("{invalid}", encoding="utf-8")

    inventory = read_persistent_cache_inventory(cache_root, now=300.0)
    assert [entry.relative_order for entry in inventory.entries] == [0, 1]
    assert [entry.index_kind for entry in inventory.entries] == ["root", "dependency"]
    assert [entry.stored_source_sha256_prefix for entry in inventory.entries] == [
        hashlib.sha256(b"# Synthetic root\n" + raw_marker).hexdigest()[:12],
        hashlib.sha256(b"Synthetic dependency\n" + raw_marker).hexdigest()[:12],
    ]
    assert [entry.recency_bucket for entry in inventory.entries] == ["under_1h", "under_1h"]
    assert inventory.invalid_entries == 1
    serialized = json.dumps(asdict(inventory))
    assert raw_marker.decode() not in serialized
    assert "Bounded synthetic summary." not in serialized
    approved_fields = {
        "logical_key_sha256_prefix",
        "entry_bytes",
        "recency_bucket",
        "relative_order",
        "storage_kind",
        "shard_prefix",
        "index_kind",
        "stored_source_sha256_prefix",
        "model",
        "schema_version",
        "compiler_version",
        "pinned",
    }
    assert all(set(entry) == approved_fields for entry in asdict(inventory)["entries"])


def test_dependency_cache_reconciliation_detects_hits_misses_and_mismatches() -> None:
    def entry(source_prefix: str) -> CacheInventoryEntry:
        return CacheInventoryEntry(
            logical_key_sha256_prefix="0" * 12,
            entry_bytes=128,
            recency_bucket="under_1h",
            relative_order=0,
            storage_kind="filesystem",
            shard_prefix="ab",
            index_kind="dependency",
            stored_source_sha256_prefix=source_prefix,
            model="sanitized-model",
            schema_version="constitution-index-v1",
            compiler_version="compiler-v2",
            pinned=False,
        )

    matching = "a" * 12
    metrics = {
        "dependency_cache_hits": MetricDelta(1, 2),
        "dependency_cache_misses": MetricDelta(3, 3),
    }
    empty_before = CacheInventory(entries=(), invalid_entries=0)
    same_after = CacheInventory(entries=(entry(matching),), invalid_entries=0)

    hit_match, different_source, _, errors = _reconcile_dependency_cache(
        inventory_before=empty_before,
        inventory_after=same_after,
        metric_deltas=metrics,
        fixture_hashes_stable=True,
        dependency_sha256=f"{matching}{'0' * 52}",
    )
    assert hit_match is False and not different_source and errors == ()

    known_hit, _, _, _ = _reconcile_dependency_cache(
        inventory_before=same_after,
        inventory_after=same_after,
        metric_deltas=metrics,
        fixture_hashes_stable=True,
        dependency_sha256=f"{matching}{'0' * 52}",
    )
    assert known_hit is True

    mismatch_metrics = {
        "dependency_cache_hits": MetricDelta(0, 0),
        "dependency_cache_misses": MetricDelta(1, 2),
    }
    _, _, miss_match, mismatch_errors = _reconcile_dependency_cache(
        inventory_before=empty_before,
        inventory_after=empty_before,
        metric_deltas=mismatch_metrics,
        fixture_hashes_stable=False,
        dependency_sha256=f"{matching}{'0' * 52}",
    )
    assert miss_match is False
    assert mismatch_errors == ("fixture_hash_changed", "cache_miss_stored_source_hash_mismatch")


@pytest.mark.parametrize(
    ("metrics", "before_sources", "after_sources", "expected"),
    [
        (
            {"dependency_cache_hits": 1, "dependency_cache_misses": 0},
            ("a" * 12,),
            ("a" * 12,),
            "expected_retry_hit",
        ),
        (
            {"dependency_cache_hits": 1, "dependency_cache_misses": 0},
            (),
            ("b" * 12,),
            "stale_or_cross_content_entry",
        ),
        (
            {"dependency_cache_hits": 0, "dependency_cache_misses": 1},
            (),
            (),
            "observation_mismatch",
        ),
        (
            {"dependency_cache_hits": 1, "dependency_cache_misses": 0},
            ("b" * 12,),
            ("a" * 12, "b" * 12),
            "stale_or_cross_content_entry",
        ),
        (
            {"dependency_cache_hits": 0, "dependency_cache_misses": 1},
            (),
            ("a" * 12,),
            "unresolved_with_fixed_evidence",
        ),
        (
            {"dependency_cache_hits": 0, "dependency_cache_misses": 0},
            (),
            (),
            "metrics_interpretation_error",
        ),
    ],
)
def test_dependency_cache_outcomes_are_classified_from_fixed_facts(
    metrics: dict[str, int],
    before_sources: tuple[str, ...],
    after_sources: tuple[str, ...],
    expected: str,
) -> None:
    def inventory(prefixes: tuple[str, ...]) -> CacheInventory:
        entries = tuple(
            CacheInventoryEntry(
                logical_key_sha256_prefix=str(position).zfill(12)[:12],
                entry_bytes=128,
                recency_bucket="under_1h",
                relative_order=position,
                storage_kind="filesystem",
                shard_prefix="ab",
                index_kind="dependency",
                stored_source_sha256_prefix=prefix,
                model="sanitized-model",
                schema_version="constitution-index-v1",
                compiler_version="compiler-v2",
                pinned=False,
            )
            for position, prefix in enumerate(prefixes)
        )
        return CacheInventory(entries=entries, invalid_entries=0)

    classification = _classify_dependency_cache_outcome(
        metric_deltas={name: MetricDelta(0, value) for name, value in metrics.items()},
        inventory_before=inventory(before_sources),
        inventory_after=inventory(after_sources),
        dependency_sha256=f"{'a' * 12}{'0' * 52}",
        consistency_errors=("cache_miss_stored_source_hash_mismatch",)
        if expected == "observation_mismatch"
        else (),
    )
    assert classification == expected


def test_dependency_reconciliation_ignores_expected_different_source_root() -> None:
    def entry(kind: Literal["root", "dependency"], source_prefix: str) -> CacheInventoryEntry:
        return CacheInventoryEntry(
            logical_key_sha256_prefix="0" * 12,
            entry_bytes=128,
            recency_bucket="under_1h",
            relative_order=0,
            storage_kind="filesystem",
            shard_prefix="ab",
            index_kind=kind,
            stored_source_sha256_prefix=source_prefix,
            model="sanitized-model",
            schema_version="constitution-index-v1",
            compiler_version="compiler-v2",
            pinned=False,
        )

    before = CacheInventory(entries=(), invalid_entries=0)
    after = CacheInventory(
        entries=(entry("root", "b" * 12), entry("dependency", "a" * 12)),
        invalid_entries=0,
    )
    hit_before, different, miss_match, errors = _reconcile_dependency_cache(
        inventory_before=before,
        inventory_after=after,
        metric_deltas={
            "dependency_cache_hits": MetricDelta(0, 0),
            "dependency_cache_misses": MetricDelta(0, 1),
        },
        fixture_hashes_stable=True,
        dependency_sha256=f"{'a' * 12}{'0' * 52}",
    )
    assert hit_before is None and different is False and miss_match is True and errors == ()


def test_one_invocation_diagnostic_reconciles_a_real_cache_miss(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import slaif_local_coding.e2e as e2e_module

    fixture = write_governed_fixture(
        tmp_path, base_url="http://127.0.0.1:18031/v1", api_key_env="QWEN3090_API_KEY"
    )

    def fake_catalog(_codex_bin: object, _destination: object) -> None:
        return None

    def fake_run(
        _codex_bin: object, called_fixture: GovernedFixturePaths, prompt: str
    ) -> SanitizedCodexRun:
        assert called_fixture is fixture
        dependency = (called_fixture.repository / "GOVERNANCE-DEPENDENCY.md").read_bytes()
        _write_cache_entry(
            persistent_root,
            logical_path="AGENTS.md",
            source=(called_fixture.repository / "AGENTS.md").read_bytes(),
            created_at=time.time(),
        )
        _write_cache_entry(
            persistent_root,
            logical_path="GOVERNANCE-DEPENDENCY.md",
            source=dependency,
            created_at=time.time(),
        )
        return SanitizedCodexRun(
            exit_status=0,
            timed_out=False,
            duration_seconds=1.0,
            event_bytes=128,
            event_type_counts={"item.started": 1, "item.completed": 2},
            call_item_type_counts={"command_execution": 1},
            tool_names=("command_execution",),
            tool_calls=1,
            sentinel_passed=False,
            failure_reason="sentinel_missing",
            command_event_counts={"started": 1, "completed": 1},
        )

    metrics_samples = [
        "",
        "\n".join(
            [
                'slaif_constitution_roots_total{evidence_type="project_instructions",'
                'route="qwen38-vision-codex"} 1',
                "slaif_constitution_dependency_acquisitions_total"
                '{route="qwen38-vision-codex",outcome="cache_miss"} 1',
                "slaif_constitution_injection_total"
                '{route="qwen38-vision-codex",outcome="updated"} 1',
                "slaif_constitution_compiler_attempts_total 1",
                'slaif_constitution_compiler_successes_total{cache="miss-persisted"} 1',
                "slaif_constitution_dependency_working_set_total"
                '{route="qwen38-vision-codex",status="included"} 1',
            ]
        ),
    ]

    monkeypatch.setattr(e2e_module, "write_local_model_catalog", fake_catalog)
    monkeypatch.setattr(e2e_module, "run_codex_once", fake_run)
    monkeypatch.setattr(e2e_module, "write_governed_fixture", lambda *_args, **_kwargs: fixture)
    persistent_root = tmp_path / "configured-adapter-cache"
    persistent_root.mkdir(mode=0o700)
    facts = e2e_module.run_dependency_cache_diagnostic(
        "unused",
        metrics_sampler=lambda: metrics_samples.pop(0),
        persistent_cache_root=persistent_root,
    )

    assert facts.attempt_count == 1
    assert facts.run.failure_reason == "sentinel_missing"
    assert facts.run.command_event_counts == {"started": 1, "completed": 1}
    assert facts.fixture_hashes_stable_during_run
    assert facts.metric_deltas["dependency_cache_misses"].delta == 1
    assert facts.metric_deltas["working_set_included"].delta == 1
    assert len(facts.inventory_before.entries) == 0
    assert len(facts.inventory_after.entries) == 2
    dependency_hash = hashlib.sha256(
        (fixture.repository / "GOVERNANCE-DEPENDENCY.md").read_bytes()
    ).hexdigest()
    assert facts.fixture_dependency_sha256 == dependency_hash
    assert facts.cache_miss_stored_source_hash_match is True
    assert facts.consistency_errors == ()
    assert facts.classification == "unresolved_with_fixed_evidence"
    public = json.dumps(asdict(facts), sort_keys=True)
    assert fixture.sentinel_token not in public
