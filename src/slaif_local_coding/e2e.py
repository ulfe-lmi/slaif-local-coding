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
import os
import subprocess
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from prometheus_client.parser import text_string_to_metric_families

DEFAULT_ADAPTER_BASE_URL = "http://127.0.0.1:18031/v1"
DEFAULT_MODEL = "qwen3.8-27b"
DEFAULT_API_KEY_ENV = "QWEN3090_API_KEY"
CODEX_TIMEOUT_SECONDS = 300.0
CODEX_MAX_EVENT_BYTES = 32_000_000
CODEX_MAX_DIAGNOSTIC_BYTES = 1_048_576
CODEX_MAX_ATTEMPTS = 3


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
            and self.injected_requests >= 2
        )


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
        ]
    )
    agents = "".join(filler)
    dependency = (
        "# Synthetic dependency\n\n"
        "This delegated procedure is binding after the root instruction.\n"
        "FINAL_RESPONSE_EXACTLY:\n"
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
        "final answer."
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
    )


def governed_prompt(sentinel_token: str) -> str:
    """Build the bounded disposable prompt without embedding it in source."""
    return (
        "First call shell_command exactly once with command cat GOVERNANCE-DEPENDENCY.md. "
        "Wait for its result. Then your final message must be exactly "
        f"SENTINEL-ACK:{sentinel_token}."
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
            result = run_codex_once(codex_bin, fixture, governed_prompt(fixture.sentinel_token))
            first_runs.append(result)
            if result.failure_reason == "success":
                break
        metrics_after_first = sample()
        if first_runs[-1].failure_reason == "success":
            second = run_codex_once(codex_bin, fixture, governed_prompt(fixture.sentinel_token))
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
