"""Bounded disposable real-Codex E2E support.

This module deliberately keeps synthetic fixture material and Codex JSONL inside
caller-owned temporary boundaries. Public results contain only fixed sanitized
facts required by the objective; raw prompts, events, responses, paths, and tool
output are discarded when the caller's ``TemporaryDirectory`` closes.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import os
import subprocess
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from prometheus_client.parser import text_string_to_metric_families

from .constitution.compiler_models import CompiledIndex

DEFAULT_ADAPTER_BASE_URL = "http://127.0.0.1:18031/v1"
DEFAULT_MODEL = "qwen3.8-27b"
DEFAULT_API_KEY_ENV = "QWEN3090_API_KEY"
CODEX_TIMEOUT_SECONDS = 300.0
CODEX_MAX_EVENT_BYTES = 32_000_000
CODEX_MAX_DIAGNOSTIC_BYTES = 1_048_576
CODEX_MAX_ATTEMPTS = 3
CACHE_INVENTORY_MAX_ENTRY_BYTES = 1_048_576


@dataclass(frozen=True)
class SanitizedCodexRun:
    """Non-confidential result of one bounded Codex execution."""

    exit_status: int | None
    timed_out: bool
    duration_seconds: float
    event_bytes: int
    event_type_counts: Mapping[str, int]
    call_item_type_counts: Mapping[str, int]
    tool_names: tuple[str, ...]
    tool_calls: int
    sentinel_passed: bool
    failure_reason: str
    command_event_counts: Mapping[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class GovernedFixturePaths:
    """Locations owned by a caller-provided temporary directory."""

    repository: Path
    codex_home: Path
    cache_root: Path
    codex_config: Path
    model_catalog: Path
    sentinel_token: str


@dataclass(frozen=True)
class GovernedE2EFacts:
    """Sanitized two-invocation result suitable for an OAP report."""

    first_runs: tuple[SanitizedCodexRun, ...]
    second_run: SanitizedCodexRun
    sentinel_token_length: int
    compiler_calls_before_first: float
    compiler_calls_after_first: float
    compiler_calls_after_second: float
    compiler_model_calls_before_first: float
    compiler_model_calls_after_first: float
    compiler_model_calls_after_second: float
    root_observations: float
    dependency_acquisitions: float
    dependency_cache_hits: float
    injected_requests: float

    @property
    def successful(self) -> bool:
        first = self.first_runs[-1] if self.first_runs else None
        return (
            first is not None
            and first.failure_reason == "success"
            and self.second_run.failure_reason == "success"
            and self.compiler_calls_after_first > self.compiler_calls_before_first
            and self.compiler_calls_after_second >= self.compiler_calls_after_first
            and self.compiler_model_calls_after_first > self.compiler_model_calls_before_first
            and self.compiler_model_calls_after_second == self.compiler_model_calls_after_first
            and self.root_observations >= 1
            and self.dependency_acquisitions >= 1
            and self.dependency_cache_hits >= 1
            and self.injected_requests >= 2
        )


CacheOutcomeClassification = Literal[
    "expected_retry_hit",
    "stale_or_cross_content_entry",
    "observation_mismatch",
    "metrics_interpretation_error",
    "unresolved_with_fixed_evidence",
]


@dataclass(frozen=True)
class MetricDelta:
    """Cumulative counter values and their delta for one bounded interval."""

    before: float
    after: float

    @property
    def delta(self) -> float:
        return self.after - self.before


@dataclass(frozen=True)
class ConstitutionMetricsSnapshot:
    """Fixed sanitized counters; no payload, path, identity, or prompt facts."""

    root_observations: float
    dependency_observations: float
    dependency_cache_misses: float
    dependency_cache_hits: float
    dependency_invalid: float
    dependency_budget_exceeded: float
    injected_requests: float
    compiler_attempts: float
    compiler_calls: float
    working_set_included: float
    working_set_missing: float
    working_set_omitted: float

    def subtract(self, before: ConstitutionMetricsSnapshot) -> dict[str, MetricDelta]:
        return {
            field_name: MetricDelta(
                before=getattr(before, field_name), after=getattr(self, field_name)
            )
            for field_name in (
                "root_observations",
                "dependency_observations",
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
            )
        }


@dataclass(frozen=True)
class CacheInventoryEntry:
    """Sanitized persistent-cache metadata approved for bounded diagnostics."""

    logical_key_sha256_prefix: str
    entry_bytes: int
    recency_bucket: Literal["under_1h", "under_24h", "under_7d", "older"]
    relative_order: int
    storage_kind: Literal["filesystem"]
    shard_prefix: str
    index_kind: Literal["root", "dependency", "unknown"]
    stored_source_sha256_prefix: str
    model: str
    schema_version: str
    compiler_version: str
    pinned: bool


@dataclass(frozen=True)
class CacheInventory:
    entries: tuple[CacheInventoryEntry, ...]
    invalid_entries: int


@dataclass(frozen=True)
class DependencyCacheDiagnosticFacts:
    """One-invocation cache diagnostics with only fixed or hash-prefix facts."""

    run: SanitizedCodexRun
    fixture_root_sha256: str
    fixture_dependency_sha256: str
    fixture_hashes_stable_during_run: bool
    inventory_before: CacheInventory
    inventory_after: CacheInventory
    metric_deltas: Mapping[str, MetricDelta]
    cache_hit_same_source_before_call: bool | None
    different_source_entries_present: bool
    cache_miss_stored_source_hash_match: bool | None
    consistency_errors: tuple[str, ...]
    classification: CacheOutcomeClassification

    @property
    def attempt_count(self) -> int:
        return 1


def _private_directory(path: Path) -> Path:
    path.mkdir(mode=0o700, parents=True, exist_ok=False)
    return path


def write_governed_fixture(root: Path, base_url: str, api_key_env: str) -> GovernedFixturePaths:
    """Create one isolated repository/CODEX_HOME/config and persistent cache."""
    repository = _private_directory(root / "repository")
    codex_home = _private_directory(root / "codex-home")
    cache_root = _private_directory(root / "adapter-cache")
    token = f"{os.urandom(12).hex()}"
    filler: list[str] = [
        "# Synthetic governance fixture\n\n",
        "The coding agent MUST read [GOVERNANCE-DEPENDENCY.md](GOVERNANCE-DEPENDENCY.md) "
        "before substantive work.\n",
        "The agent MUST use its ordinary local file tool for that read.\n\n",
    ]
    for section in range(32):
        decoy = hashlib.sha256(f"section-{section}".encode()).hexdigest()[:16]
        filler.extend(
            [
                f"## Synthetic section {section + 1}\n\n",
                f"Background procedure {section + 1} remains binding when applicable. ",
                "Do not use a synthetic DECOY-ACK token as the final response. ",
                f"Section-only decoy acknowledgment is DECOY-ACK:{decoy}.\n",
                "Repository/Git/source files remain authoritative over derived context.\n\n",
            ]
        )
    filler.extend(
        [
            "## Sentinel procedure\n\n",
            "After using a local file tool to read the referenced dependency, ",
            "the final response MUST exactly follow that dependency's "
            "FINAL_RESPONSE_EXACTLY instruction.\n",
            "Treat that instruction literally: reproduce its prescribed final "
            "message as the whole final message, with no explanation.\n",
        ]
    )
    agents = "".join(filler)
    dependency = (
        "# Synthetic dependency\n\n"
        "This delegated procedure is binding after the root instruction.\n"
        "FINAL_RESPONSE_EXACTLY:\n"
        "Make the entire final message exactly this one line:\n"
        f"SENTINEL-ACK:{token}\n"
    )
    (repository / "AGENTS.md").write_text(agents, encoding="utf-8")
    (repository / "GOVERNANCE-DEPENDENCY.md").write_text(dependency, encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(repository)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repository), "add", "AGENTS.md", "GOVERNANCE-DEPENDENCY.md"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "-c",
            "user.name=Synthetic Fixture",
            "-c",
            "user.email=synthetic@example.invalid",
            "commit",
            "-q",
            "-m",
            "Synthetic governed fixture",
        ],
        check=True,
        capture_output=True,
    )
    config = codex_home / "config.toml"
    catalog = codex_home / "model-catalog.json"
    provider = "slaif-local-coding-e2e"
    # JSON string escaping is valid TOML basic-string escaping for these values.
    quoted_base_url = json.dumps(base_url)
    quoted_api_key_env = json.dumps(api_key_env)
    config.write_text(
        f'model = "{DEFAULT_MODEL}"\n'
        'model_reasoning_effort = "low"\n'
        f'model_provider = "{provider}"\n'
        f"model_catalog_json = {json.dumps(str(catalog))}\n\n"
        "[model_providers.slaif-local-coding-e2e]\n"
        'name = "SLAIF Local Coding E2E"\n'
        f"base_url = {quoted_base_url}\n"
        f"env_key = {quoted_api_key_env}\n"
        'wire_api = "responses"\n',
        encoding="utf-8",
    )
    os.chmod(config, 0o600)
    os.chmod(catalog.parent, 0o700)
    return GovernedFixturePaths(
        repository=repository,
        codex_home=codex_home,
        cache_root=cache_root,
        codex_config=config,
        model_catalog=catalog,
        sentinel_token=token,
    )


def write_local_model_catalog(
    codex_bin: Path | str, destination: Path, *, model: str = DEFAULT_MODEL
) -> None:
    """Derive a disposable local-model catalog from the installed CLI's bundled schema."""
    completed = subprocess.run(
        [str(codex_bin), "debug", "models", "--bundled"],
        check=False,
        capture_output=True,
        env={**os.environ, "CODEX_HOME": str(destination.parent)},
        timeout=30,
    )
    if completed.returncode != 0:
        raise RuntimeError("codex_model_catalog_unavailable")
    catalog = json.loads(completed.stdout.decode("utf-8"))
    models = catalog.get("models")
    template = next(
        (model_entry for model_entry in models if model_entry.get("slug") == "gpt-5.4"), None
    )
    if not isinstance(template, dict):
        raise RuntimeError("codex_model_catalog_template_missing")
    local_model = dict(template)
    local_instructions = (
        "Use the provided shell_command function for workspace file reads. "
        "After a required tool result arrives, provide exactly the requested "
        "final answer. If a read file specifies FINAL_RESPONSE_EXACTLY, make "
        "the prescribed content the entire final message."
    )
    local_model.update(
        {
            "slug": model,
            "display_name": model,
            "description": "Disposable local E2E model",
            "input_modalities": ["text"],
            "supports_image_detail_original": False,
            "context_window": 150_000,
            "max_context_window": 150_000,
            "default_reasoning_level": "low",
            "base_instructions": local_instructions,
            "model_messages": {"instructions_template": local_instructions},
        }
    )
    destination.write_text(
        json.dumps({"models": [local_model]}, separators=(",", ":")), encoding="utf-8"
    )
    os.chmod(destination, 0o600)


def parse_codex_events(
    event_stream: Iterable[str],
) -> tuple[Counter[str], Counter[str], tuple[str, ...]]:
    """Count top-level events, safe call-item types, and named built-in tools."""
    counts: Counter[str] = Counter()
    call_items: Counter[str] = Counter()
    tools: Counter[str] = Counter()
    call_item_types = {"command_execution", "function_call", "local_shell_call", "exec_command"}

    def visit(value: object) -> None:
        if isinstance(value, list):
            for child in value:
                visit(child)
            return
        if not isinstance(value, dict):
            return
        value_type = value.get("type")
        name = value.get("name")
        if isinstance(value_type, str) and value_type in call_item_types:
            call_items[value_type] += 1
        if value_type == "command_execution":
            # Codex 0.149 emits this fixed item type for its built-in local
            # command tool when ``unified_exec`` is disabled.
            tools["command_execution"] += 1
        elif (
            isinstance(value_type, str)
            and ("call" in value_type or "command" in value_type)
            and isinstance(name, str)
            and name in {"exec_command", "shell", "local_shell"}
        ):
            tools[name] += 1
        for child in value.values():
            visit(child)

    for line in event_stream:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and isinstance(event.get("type"), str):
            counts[event["type"]] += 1
        visit(event)
    return counts, call_items, tuple(sorted(tools.elements()))


def parse_codex_command_events(event_stream: Iterable[str]) -> Counter[str]:
    """Count ordinary command-tool lifecycle outcomes without retaining output."""
    counts: Counter[str] = Counter()

    def visit(value: object, top_level_type: str | None) -> None:
        if isinstance(value, list):
            for child in value:
                visit(child, top_level_type)
            return
        if not isinstance(value, dict):
            return
        if value.get("type") == "command_execution":
            if top_level_type == "item.started":
                counts["started"] += 1
            elif top_level_type == "item.completed":
                status = value.get("status")
                if status in {"failed", "failure", "error"}:
                    counts["failed"] += 1
                else:
                    counts["completed"] += 1
        for child in value.values():
            visit(child, top_level_type)

    for line in event_stream:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            top_level_type = event.get("type")
            if isinstance(top_level_type, str):
                visit(event, top_level_type)
    return counts


def _final_agent_message_has_ack(event_stream: Iterable[str], sentinel_ack: str) -> bool:
    """Check only the final completed agent message without retaining its text."""
    found = False
    for line in event_stream:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if not isinstance(item, dict) or item.get("type") != "agent_message":
            continue
        text = item.get("text")
        found = isinstance(text, str) and sentinel_ack in text
    return found


def run_codex_once(
    codex_bin: Path | str,
    fixture: GovernedFixturePaths,
    prompt: str,
    *,
    timeout_seconds: float = CODEX_TIMEOUT_SECONDS,
) -> SanitizedCodexRun:
    """Serialize one isolated run; raw stdout/stderr remain in unlinked temp files."""
    started = time.monotonic()
    timed_out = False
    exit_status: int | None = None
    failure_reason = "unknown"
    counts: Counter[str] = Counter()
    call_items: Counter[str] = Counter()
    tools: tuple[str, ...] = ()
    event_bytes = 0
    sentinel_passed = False
    command_event_counts: Counter[str] = Counter()
    output_path = fixture.repository / ".codex-last-message.tmp"
    try:
        with tempfile.TemporaryFile() as events, tempfile.TemporaryFile() as diagnostics:
            process = subprocess.Popen(
                [
                    str(codex_bin),
                    "--ask-for-approval",
                    "never",
                    "exec",
                    "--json",
                    "--strict-config",
                    # Codex 0.149's unified-exec representation is not reliable
                    # for this constrained local Responses provider. Its stable
                    # command-tool path is explicit and disposable here.
                    "--disable",
                    "unified_exec",
                    "--sandbox",
                    "workspace-write",
                    "--cd",
                    str(fixture.repository),
                    "--output-last-message",
                    str(output_path),
                    prompt,
                ],
                cwd=fixture.repository,
                env={**os.environ, "CODEX_HOME": str(fixture.codex_home)},
                stdout=events,
                stderr=diagnostics,
                stdin=subprocess.DEVNULL,
            )
            try:
                exit_status = process.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                exit_status = None
                timed_out = True
            events.seek(0)
            while chunk := events.read(65536):
                event_bytes += len(chunk)
            if event_bytes > CODEX_MAX_EVENT_BYTES:
                raise OverflowError
            events.seek(0)
            readable = io.TextIOWrapper(events, encoding="utf-8", errors="replace")
            counts, call_items, tools = parse_codex_events(readable)
            readable.detach()
            events.seek(0)
            command_reader = io.TextIOWrapper(events, encoding="utf-8", errors="replace")
            command_event_counts = parse_codex_command_events(command_reader)
            command_reader.detach()
            events.seek(0)
            final_event_reader = io.TextIOWrapper(events, encoding="utf-8", errors="replace")
            final_event_ack = _final_agent_message_has_ack(
                final_event_reader, f"SENTINEL-ACK:{fixture.sentinel_token}"
            )
            final_event_reader.detach()
            diagnostics_size = diagnostics.seek(0, os.SEEK_END)
            if diagnostics_size > CODEX_MAX_DIAGNOSTIC_BYTES:
                raise OverflowError
            if timed_out:
                failure_reason = "timeout"
            elif exit_status != 0:
                failure_reason = f"exit_{abs(exit_status or 0)}"
            elif event_bytes == 0:
                failure_reason = "empty_event_stream"
            else:
                # CLI startup warnings are not exposed and do not invalidate a clean run.
                failure_reason = "success"
    except (OverflowError, OSError, subprocess.SubprocessError):
        failure_reason = "process_boundary_error"
        exit_status = None
    finally:
        try:
            output_path.unlink()
        except FileNotFoundError:
            pass
    if failure_reason == "success":
        try:
            output_ack = f"SENTINEL-ACK:{fixture.sentinel_token}" in output_path.read_text(
                encoding="utf-8", errors="ignore"
            )
        except OSError:
            output_ack = False
        # Some sandboxed CLI invocations do not create the output file even when
        # they emit a clean final agent-message event. Either approved channel
        # is sufficient; neither approved channel retains raw text.
        sentinel_passed = output_ack or final_event_ack
        failure_reason = "success" if sentinel_passed else "sentinel_missing"
        if not tools:
            failure_reason = "ordinary_tool_missing"
    duration = time.monotonic() - started
    return SanitizedCodexRun(
        exit_status=exit_status,
        timed_out=timed_out,
        duration_seconds=duration,
        event_bytes=event_bytes,
        event_type_counts=dict(counts),
        call_item_type_counts=dict(call_items),
        tool_names=tools,
        tool_calls=sum(call_items.values()),
        sentinel_passed=sentinel_passed,
        failure_reason=failure_reason,
        command_event_counts=dict(command_event_counts),
    )


def governed_prompt() -> str:
    """Build a bounded prompt that delegates the response token to governance."""
    return (
        "First call shell_command exactly once with command cat GOVERNANCE-DEPENDENCY.md. "
        "Wait for its result, then follow that dependency's "
        "FINAL_RESPONSE_EXACTLY instruction literally as your entire final message."
    )


def metric_value(metrics_text: str, name: str, **labels: str) -> float:
    """Read one Prometheus counter/gauge sample using fixed sanitized labels."""
    wanted = frozenset(labels.items())
    total = 0.0
    matched = False
    for family in text_string_to_metric_families(metrics_text):
        for sample in family.samples:
            if sample.name != name:
                continue
            sample_labels = frozenset(sample.labels.items())
            if wanted <= sample_labels:
                matched = True
                total += float(sample.value)
    return total if matched else 0.0


def constitution_metric_snapshot(
    metrics_text: str, *, route: str = "qwen38-vision-codex"
) -> ConstitutionMetricsSnapshot:
    """Read only fixed counters and labels from a bounded metrics exposition."""

    return ConstitutionMetricsSnapshot(
        root_observations=metric_value(
            metrics_text,
            "slaif_constitution_roots_total",
            evidence_type="project_instructions",
            route=route,
        ),
        dependency_observations=metric_value(
            metrics_text,
            "slaif_constitution_dependency_observations_total",
            state="observed",
            route=route,
        ),
        dependency_cache_misses=metric_value(
            metrics_text,
            "slaif_constitution_dependency_acquisitions_total",
            outcome="cache_miss",
            route=route,
        ),
        dependency_cache_hits=metric_value(
            metrics_text,
            "slaif_constitution_dependency_acquisitions_total",
            outcome="cache_hit",
            route=route,
        ),
        dependency_invalid=metric_value(
            metrics_text,
            "slaif_constitution_dependency_acquisitions_total",
            outcome="invalid",
            route=route,
        ),
        dependency_budget_exceeded=metric_value(
            metrics_text,
            "slaif_constitution_dependency_acquisitions_total",
            outcome="budget_exceeded",
            route=route,
        ),
        injected_requests=metric_value(
            metrics_text,
            "slaif_constitution_injection_total",
            outcome="updated",
            route=route,
        ),
        compiler_attempts=metric_value(metrics_text, "slaif_constitution_compiler_attempts_total"),
        compiler_calls=sum(
            (
                metric_value(
                    metrics_text,
                    "slaif_constitution_compiler_successes_total",
                    cache="miss-persisted",
                ),
                metric_value(
                    metrics_text,
                    "slaif_constitution_compiler_successes_total",
                    cache="hit",
                ),
                metric_value(metrics_text, "slaif_constitution_compiler_timeouts_total"),
                metric_value(
                    metrics_text,
                    "slaif_constitution_compiler_transport_failures_total",
                ),
            )
        ),
        working_set_included=metric_value(
            metrics_text,
            "slaif_constitution_dependency_working_set_total",
            status="included",
            route=route,
        ),
        working_set_missing=metric_value(
            metrics_text,
            "slaif_constitution_dependency_working_set_total",
            status="missing",
            route=route,
        ),
        working_set_omitted=metric_value(
            metrics_text,
            "slaif_constitution_dependency_working_set_total",
            status="omitted",
            route=route,
        ),
    )


def _recency_bucket(age_seconds: float) -> Literal["under_1h", "under_24h", "under_7d", "older"]:
    if age_seconds < 3_600:
        return "under_1h"
    if age_seconds < 86_400:
        return "under_24h"
    if age_seconds < 604_800:
        return "under_7d"
    return "older"


def read_persistent_cache_inventory(
    cache_root: Path, *, now: float | None = None
) -> CacheInventory:
    """Extract bounded metadata; raw paths, source bytes, and indexes are omitted."""

    observed_now = time.time() if now is None else now
    discovered: list[tuple[float, str, CacheInventoryEntry]] = []
    invalid = 0
    if not cache_root.is_dir() or cache_root.is_symlink():
        return CacheInventory(entries=(), invalid_entries=invalid)
    for path in cache_root.glob("*/*.json"):
        try:
            key = path.stem
            shard = path.parent.name
            size = path.stat().st_size
            valid_shape = (
                len(key) == 64
                and all(character in "0123456789abcdef" for character in key)
                and len(shard) == 2
                and all(character in "0123456789abcdef" for character in shard)
                and not path.is_symlink()
                and path.parent.is_dir()
                and not path.parent.is_symlink()
                and 0 < size <= CACHE_INVENTORY_MAX_ENTRY_BYTES
            )
            envelope = json.loads(path.read_text(encoding="utf-8"))
            payload = envelope.get("payload") if isinstance(envelope, dict) else None
            index = CompiledIndex.model_validate(payload)
            created = envelope.get("created_at")
            valid_content = (
                valid_shape
                and isinstance(created, (int, float))
                and not isinstance(created, bool)
                and math.isfinite(float(created))
                and envelope.get("key") == key
            )
            if not valid_content:
                raise ValueError("invalid sanitized cache entry")
            created_float = float(created)
            logical_path = index.source_logical_path
            age = max(0.0, observed_now - created_float)
            entry = CacheInventoryEntry(
                logical_key_sha256_prefix=key[:12],
                entry_bytes=size,
                recency_bucket=_recency_bucket(age),
                relative_order=0,
                storage_kind="filesystem",
                shard_prefix=shard,
                index_kind="root" if logical_path == "AGENTS.md" else "dependency",
                stored_source_sha256_prefix=index.source_sha256[:12],
                model=index.model,
                schema_version=index.schema_version,
                compiler_version=index.compiler_version,
                pinned=index.effective_class().value in {"P0", "P1"},
            )
            discovered.append((created_float, key, entry))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            invalid += 1
    discovered.sort(key=lambda item: (-item[0], item[1]))
    entries = tuple(
        CacheInventoryEntry(
            logical_key_sha256_prefix=entry.logical_key_sha256_prefix,
            entry_bytes=entry.entry_bytes,
            recency_bucket=entry.recency_bucket,
            relative_order=position,
            storage_kind=entry.storage_kind,
            shard_prefix=entry.shard_prefix,
            index_kind=entry.index_kind,
            stored_source_sha256_prefix=entry.stored_source_sha256_prefix,
            model=entry.model,
            schema_version=entry.schema_version,
            compiler_version=entry.compiler_version,
            pinned=entry.pinned,
        )
        for position, (_created, _key, entry) in enumerate(discovered)
    )
    return CacheInventory(entries=entries, invalid_entries=invalid)


def _classify_dependency_cache_outcome(
    *,
    metric_deltas: Mapping[str, MetricDelta],
    inventory_before: CacheInventory,
    inventory_after: CacheInventory,
    dependency_sha256: str,
    consistency_errors: tuple[str, ...],
) -> CacheOutcomeClassification:
    if consistency_errors:
        return "observation_mismatch"
    misses = metric_deltas["dependency_cache_misses"].delta
    hits = metric_deltas["dependency_cache_hits"].delta
    same_source_before = any(
        entry.stored_source_sha256_prefix == dependency_sha256[:12]
        for entry in inventory_before.entries
    )
    different_source_after = any(
        entry.index_kind == "dependency"
        and entry.stored_source_sha256_prefix != dependency_sha256[:12]
        for entry in inventory_after.entries
    )
    matching_after = any(
        entry.stored_source_sha256_prefix == dependency_sha256[:12]
        for entry in inventory_after.entries
    )
    if hits > 0 and misses <= 0 and not same_source_before:
        return "stale_or_cross_content_entry"
    if hits > 0 and different_source_after:
        return "stale_or_cross_content_entry"
    if hits > 0 and not matching_after:
        return "stale_or_cross_content_entry"
    if hits > 0:
        return "expected_retry_hit"
    if misses > 0:
        return "unresolved_with_fixed_evidence"
    return "metrics_interpretation_error"


def _reconcile_dependency_cache(
    *,
    inventory_before: CacheInventory,
    inventory_after: CacheInventory,
    metric_deltas: Mapping[str, MetricDelta],
    fixture_hashes_stable: bool,
    dependency_sha256: str,
) -> tuple[bool | None, bool, bool | None, tuple[str, ...]]:
    """Reconcile counter deltas with sanitized before/after inventories."""

    errors: list[str] = []
    if not fixture_hashes_stable:
        errors.append("fixture_hash_changed")
    hits = metric_deltas["dependency_cache_hits"].delta
    misses = metric_deltas["dependency_cache_misses"].delta
    matching_before = any(
        entry.index_kind == "dependency"
        and entry.stored_source_sha256_prefix == dependency_sha256[:12]
        for entry in inventory_before.entries
    )
    matching_after = any(
        entry.index_kind == "dependency"
        and entry.stored_source_sha256_prefix == dependency_sha256[:12]
        for entry in inventory_after.entries
    )
    different_source = any(
        entry.index_kind == "dependency"
        and entry.stored_source_sha256_prefix != dependency_sha256[:12]
        for entry in inventory_after.entries
    )
    if any(not float(delta.delta).is_integer() for delta in metric_deltas.values()):
        errors.append("non_integer_counter_delta")
    miss_stored_match: bool | None = None
    if misses > 0:
        miss_stored_match = matching_after
        if not matching_after:
            errors.append("cache_miss_stored_source_hash_mismatch")
    return (
        matching_before if hits > 0 else None,
        different_source,
        miss_stored_match,
        tuple(errors),
    )


def run_dependency_cache_diagnostic(
    codex_bin: Path | str,
    *,
    metrics_sampler: Callable[[], str] | None = None,
    base_url: str = DEFAULT_ADAPTER_BASE_URL,
    api_key_env: str = DEFAULT_API_KEY_ENV,
    persistent_cache_root: Path | None = None,
) -> DependencyCacheDiagnosticFacts:
    """Run exactly one fresh governed Codex invocation and sanitize its facts."""

    def sample() -> str:
        return metrics_sampler() if metrics_sampler is not None else ""

    metrics_before = sample()
    with tempfile.TemporaryDirectory(prefix="slaif-codex-cache-diagnostic-") as temporary:
        fixture = write_governed_fixture(Path(temporary), base_url, api_key_env)
        write_local_model_catalog(codex_bin, fixture.model_catalog)
        root_path = fixture.repository / "AGENTS.md"
        dependency_path = fixture.repository / "GOVERNANCE-DEPENDENCY.md"
        root_hash = hashlib.sha256(root_path.read_bytes()).hexdigest()
        dependency_hash = hashlib.sha256(dependency_path.read_bytes()).hexdigest()
        inventory_root = persistent_cache_root or fixture.cache_root
        inventory_before = read_persistent_cache_inventory(inventory_root, now=time.time())
        run = run_codex_once(codex_bin, fixture, governed_prompt())
        root_hash_after = hashlib.sha256(root_path.read_bytes()).hexdigest()
        dependency_hash_after = hashlib.sha256(dependency_path.read_bytes()).hexdigest()
        inventory_after = read_persistent_cache_inventory(inventory_root, now=time.time())

    snapshot_before = constitution_metric_snapshot(metrics_before)
    snapshot_after = constitution_metric_snapshot(sample())
    metric_deltas = snapshot_after.subtract(snapshot_before)

    hashes_stable = root_hash == root_hash_after and dependency_hash == dependency_hash_after
    (
        cache_hit_same_source_before,
        different_source_after,
        cache_miss_stored_match,
        errors,
    ) = _reconcile_dependency_cache(
        inventory_before=inventory_before,
        inventory_after=inventory_after,
        metric_deltas=metric_deltas,
        fixture_hashes_stable=hashes_stable,
        dependency_sha256=dependency_hash,
    )
    classification = _classify_dependency_cache_outcome(
        metric_deltas=metric_deltas,
        inventory_before=inventory_before,
        inventory_after=inventory_after,
        dependency_sha256=dependency_hash,
        consistency_errors=errors,
    )
    return DependencyCacheDiagnosticFacts(
        run=run,
        fixture_root_sha256=root_hash,
        fixture_dependency_sha256=dependency_hash,
        fixture_hashes_stable_during_run=hashes_stable,
        inventory_before=inventory_before,
        inventory_after=inventory_after,
        metric_deltas=metric_deltas,
        cache_hit_same_source_before_call=cache_hit_same_source_before,
        different_source_entries_present=different_source_after,
        cache_miss_stored_source_hash_match=cache_miss_stored_match,
        consistency_errors=errors,
        classification=classification,
    )


def run_governed_e2e(
    codex_bin: Path | str,
    *,
    metrics_sampler: Callable[[], str] | None = None,
    base_url: str = DEFAULT_ADAPTER_BASE_URL,
    api_key_env: str = DEFAULT_API_KEY_ENV,
    max_attempts: int = CODEX_MAX_ATTEMPTS,
) -> GovernedE2EFacts:
    """Run, extract facts, then delete repository/config/event temporary state."""
    if not 1 <= max_attempts <= CODEX_MAX_ATTEMPTS:
        raise ValueError("invalid attempt budget")

    def sample() -> str:
        return metrics_sampler() if metrics_sampler is not None else ""

    metrics_before = sample()
    with tempfile.TemporaryDirectory(prefix="slaif-codex-governed-e2e-") as temporary:
        fixture = write_governed_fixture(Path(temporary), base_url, api_key_env)
        write_local_model_catalog(codex_bin, fixture.model_catalog)
        first_runs: list[SanitizedCodexRun] = []
        for _ in range(max_attempts):
            result = run_codex_once(codex_bin, fixture, governed_prompt())
            first_runs.append(result)
            if result.failure_reason == "success":
                break
        metrics_after_first = sample()
        if first_runs[-1].failure_reason == "success":
            second = run_codex_once(codex_bin, fixture, governed_prompt())
        else:
            second = SanitizedCodexRun(
                exit_status=None,
                timed_out=False,
                duration_seconds=0.0,
                event_bytes=0,
                event_type_counts={},
                call_item_type_counts={},
                tool_names=(),
                tool_calls=0,
                sentinel_passed=False,
                failure_reason="not_run",
            )
        metrics_after_second = sample()
        sentinel_token_length = len(fixture.sentinel_token)

    def compiler_calls(text: str) -> float:
        return sum(
            (
                metric_value(
                    text, "slaif_constitution_compiler_successes_total", cache="miss-persisted"
                ),
                metric_value(text, "slaif_constitution_compiler_successes_total", cache="hit"),
                metric_value(text, "slaif_constitution_compiler_timeouts_total"),
                metric_value(text, "slaif_constitution_compiler_transport_failures_total"),
            )
        )

    route_labels = {"route": "qwen38-vision-codex"}
    return GovernedE2EFacts(
        first_runs=tuple(first_runs),
        second_run=second,
        sentinel_token_length=sentinel_token_length,
        compiler_calls_before_first=compiler_calls(metrics_before),
        compiler_calls_after_first=compiler_calls(metrics_after_first),
        compiler_calls_after_second=compiler_calls(metrics_after_second),
        compiler_model_calls_before_first=metric_value(
            metrics_before, "slaif_constitution_compiler_attempts_total"
        ),
        compiler_model_calls_after_first=metric_value(
            metrics_after_first, "slaif_constitution_compiler_attempts_total"
        ),
        compiler_model_calls_after_second=metric_value(
            metrics_after_second, "slaif_constitution_compiler_attempts_total"
        ),
        root_observations=(
            metric_value(
                metrics_after_second,
                "slaif_constitution_roots_total",
                **{"evidence_type": "project_instructions", **route_labels},
            )
            - metric_value(
                metrics_before,
                "slaif_constitution_roots_total",
                **{"evidence_type": "project_instructions", **route_labels},
            )
        ),
        dependency_acquisitions=(
            metric_value(
                metrics_after_second,
                "slaif_constitution_dependency_acquisitions_total",
                outcome="cache_miss",
                **route_labels,
            )
            - metric_value(
                metrics_before,
                "slaif_constitution_dependency_acquisitions_total",
                outcome="cache_miss",
                **route_labels,
            )
        ),
        dependency_cache_hits=(
            metric_value(
                metrics_after_second,
                "slaif_constitution_dependency_acquisitions_total",
                outcome="cache_hit",
                **route_labels,
            )
            - metric_value(
                metrics_before,
                "slaif_constitution_dependency_acquisitions_total",
                outcome="cache_hit",
                **route_labels,
            )
        ),
        injected_requests=(
            metric_value(
                metrics_after_second,
                "slaif_constitution_injection_total",
                outcome="updated",
                **route_labels,
            )
            - metric_value(
                metrics_before,
                "slaif_constitution_injection_total",
                outcome="updated",
                **route_labels,
            )
        ),
    )
