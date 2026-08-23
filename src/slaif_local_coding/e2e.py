"""Bounded disposable real-Codex E2E support.

This module deliberately keeps synthetic fixture material and Codex JSONL inside
caller-owned temporary boundaries. Public results contain only fixed sanitized
facts required by the objective; raw prompts, events, responses, paths, and tool
output are discarded when the caller's ``TemporaryDirectory`` closes.
"""

from __future__ import annotations

import dataclasses
import hashlib
import io
import json
import math
import os
import platform
import re
import shlex
import shutil
import stat
import subprocess
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from prometheus_client.parser import text_string_to_metric_families

from .constitution.compiler_models import CompiledIndex

DEFAULT_ADAPTER_BASE_URL = "http://127.0.0.1:18031/v1"
DEFAULT_MODEL = "qwen3.8-27b"
DEFAULT_API_KEY_ENV = "QWEN3090_API_KEY"
CODEX_TIMEOUT_SECONDS = 300.0
CODEX_MAX_EVENT_BYTES = 32_000_000
CODEX_MAX_DIAGNOSTIC_BYTES = 1_048_576
CODEX_MAX_ATTEMPTS = 2
CACHE_INVENTORY_MAX_ENTRY_BYTES = 1_048_576
SANDBOX_PREFLIGHT_TIMEOUT_SECONDS = 15.0
SANDBOX_PREFLIGHT_MAX_OUTPUT_BYTES = 1_048_576
SANDBOX_PERMISSION_PROFILE = "workspace-write"
SANDBOX_PLATFORM = "linux"

DependencyCommandState = Literal["success", "failed", "incomplete"]
DependencyProvenanceClassification = Literal[
    "equal",
    "tool_boundary_normalization",
    "observation_mismatch",
    "unavailable",
]
DependencyReadForm = Literal["relative_cat", "absolute_bin_cat"]
DiagnosticFailureClass = Literal[
    "success",
    "not_found",
    "permission_denied",
    "sandbox_denied",
    "schema_invalid",
    "argv_unsupported",
    "signal",
    "timeout",
    "unknown_nonzero",
    "unavailable",
]
ArgvShape = Literal["absent", "single_string", "argv_list", "shell_wrapped_list", "unsupported"]
SandboxDiagnosticSubclass = Literal[
    "empty",
    "bwrap_loopback_bootstrap",
    "bwrap_bootstrap_denied",
    "permission",
    "not_found",
    "argument",
    "schema",
    "timeout",
    "other",
]
SandboxBoundaryClassification = Literal[
    "workspace_sandbox_available",
    "host_sandbox_bootstrap_unsupported",
    "workspace_root_resolution_mismatch",
    "invocation_config_precedence_error",
    "command_event_schema_mismatch",
    "unresolved_with_fixed_evidence",
]
SandboxPolicyResolution = Literal["resolved", "unresolved", "unknown"]


@dataclass(frozen=True)
class DependencyObservationFacts:
    """Bounded command-lifecycle facts without retaining command output."""

    intended_dependency_reads: int = 0
    started_commands: int = 0
    completed_commands: int = 0
    failed_commands: int = 0
    successful_dependency_reads: int = 0
    output_sha256: str | None = None
    output_byte_length: int | None = None
    rstrip_output_sha256: str | None = None

    @property
    def lifecycle(self) -> DependencyCommandState:
        if (
            self.intended_dependency_reads == 1
            and self.successful_dependency_reads == 1
            and self.failed_commands == 0
            and self.output_sha256 is not None
            and self.output_byte_length is not None
        ):
            return "success"
        if self.failed_commands > 0:
            return "failed"
        return "incomplete"


@dataclass(frozen=True)
class DirectDependencyReadControl:
    """Private same-user readability facts with no retained file content."""

    exists: bool
    regular_file: bool
    symlink: bool
    private_mode: bool
    byte_length: int | None
    sha256: str | None
    subprocess_exit_status: int | None
    subprocess_byte_identical: bool | None


@dataclass(frozen=True)
class BinaryStreamFacts:
    """Fixed audit facts for a bounded process stream."""

    byte_length: int
    sha256: str
    first_line_class: DiagnosticFailureClass
    first_line_subclass: SandboxDiagnosticSubclass = "empty"


@dataclass(frozen=True)
class CommandDiagnostics:
    """Bounded process/event diagnostics without retaining diagnostic text."""

    failure_class: DiagnosticFailureClass = "unavailable"
    process_exit_code: int | None = None
    process_status: Literal["success", "failed", "unknown"] = "unknown"
    stdout: BinaryStreamFacts | None = None
    stderr: BinaryStreamFacts | None = None
    command_exit_code: int | None = None
    command_status: Literal["success", "failed", "unknown"] = "unknown"
    command_output_class: DiagnosticFailureClass = "unavailable"
    command_output_sha256: str | None = None
    command_output_byte_length: int | None = None
    requested_argv_shape: ArgvShape = "absent"
    actual_argv_shape: ArgvShape = "absent"
    command_path_inside_repository: bool | None = None


@dataclass(frozen=True)
class SandboxPreflightFacts:
    """Sanitized result of one no-model Codex sandbox-helper read."""

    cli_version: str | None
    platform: str
    kernel_capabilities: tuple[str, ...]
    sandbox_mode: Literal["workspace-write"]
    permission_profile: str
    feature_labels: tuple[str, ...]
    policy_resolution: SandboxPolicyResolution
    working_directory_inside_repository: bool
    target_inside_repository: bool
    target_regular_file: bool
    target_symlink: bool
    target_byte_length: int | None
    target_sha256: str | None
    observed_byte_length: int | None
    observed_sha256: str | None
    byte_identical: bool | None
    process_exit_status: int | None
    process_status: Literal["success", "failed", "unknown"]
    timed_out: bool
    stdout: BinaryStreamFacts
    stderr: BinaryStreamFacts
    raw_output_retained: bool = False
    boundary_classification: SandboxBoundaryClassification = "unresolved_with_fixed_evidence"

    @property
    def successful(self) -> bool:
        return (
            self.process_exit_status == 0
            and self.process_status == "success"
            and not self.timed_out
            and self.working_directory_inside_repository
            and self.target_inside_repository
            and self.target_regular_file
            and not self.target_symlink
            and self.byte_identical is True
        )


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
    dependency_observation: DependencyObservationFacts = field(
        default_factory=lambda: DependencyObservationFacts()
    )
    command_diagnostics: CommandDiagnostics = field(default_factory=CommandDiagnostics)
    sandbox_mode: Literal["workspace-write", "unknown"] = "workspace-write"
    approval_policy: Literal["never", "unknown"] = "never"


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


@dataclass(frozen=True)
class CommandDiagnosticAttempt:
    """One direct-read control plus one fresh bounded Codex attempt."""

    read_form: DependencyReadForm
    direct_read: DirectDependencyReadControl
    run: SanitizedCodexRun


@dataclass(frozen=True)
class CommandFailureDiagnosisFacts:
    """At-most-two-attempt diagnosis with only fixed sanitized facts."""

    attempts: tuple[CommandDiagnosticAttempt, ...]
    fixture_dependency_sha256: str
    fixture_dependency_byte_length: int
    fixture_dependency_stripped_sha256: str
    sandbox_preflight: SandboxPreflightFacts | None = None
    boundary_classification: SandboxBoundaryClassification = "unresolved_with_fixed_evidence"

    @property
    def dependency_provenance(self) -> DependencyProvenanceClassification:
        if not self.attempts:
            return "unavailable"
        run = self.attempts[-1].run
        observed_hash = run.dependency_observation.output_sha256
        observed_length = run.dependency_observation.output_byte_length
        if observed_hash is None or observed_length is None:
            return "unavailable"
        if (
            observed_hash == self.fixture_dependency_sha256
            and observed_length == self.fixture_dependency_byte_length
        ):
            return "equal"
        stripped = run.dependency_observation.rstrip_output_sha256
        if stripped == self.fixture_dependency_stripped_sha256:
            return "tool_boundary_normalization"
        return "observation_mismatch"


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
    stored_source_sha256: str = ""


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
    fixture_dependency_byte_length: int
    observed_dependency_sha256: str | None
    observed_dependency_byte_length: int | None
    repository_observed_hash_equal: bool | None
    repository_observed_length_equal: bool | None
    repository_differs_only_by_terminal_whitespace: bool | None
    dependency_provenance: DependencyProvenanceClassification
    dependency_command_state: DependencyCommandState
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
        "FINAL_RESPONSE_EXACTLY: The entire final message MUST be exactly "
        f"SENTINEL-ACK:{token}\n"
    )
    (repository / "AGENTS.md").write_text(agents, encoding="utf-8")
    (repository / "GOVERNANCE-DEPENDENCY.md").write_text(dependency, encoding="utf-8")
    os.chmod(repository / "AGENTS.md", 0o600)
    os.chmod(repository / "GOVERNANCE-DEPENDENCY.md", 0o600)
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


def verify_direct_dependency_read(fixture: GovernedFixturePaths) -> DirectDependencyReadControl:
    """Prove same-user readability without retaining dependency bytes."""

    dependency_path = fixture.repository / "GOVERNANCE-DEPENDENCY.md"
    try:
        stat_result = dependency_path.lstat()
    except OSError:
        return DirectDependencyReadControl(
            exists=False,
            regular_file=False,
            symlink=False,
            private_mode=False,
            byte_length=None,
            sha256=None,
            subprocess_exit_status=None,
            subprocess_byte_identical=None,
        )
    regular = stat.S_ISREG(stat_result.st_mode)
    symlink = stat.S_ISLNK(stat_result.st_mode)
    private_mode = not stat_result.st_mode & 0o077
    if not regular or symlink:
        return DirectDependencyReadControl(
            exists=True,
            regular_file=regular,
            symlink=symlink,
            private_mode=private_mode,
            byte_length=None,
            sha256=None,
            subprocess_exit_status=None,
            subprocess_byte_identical=None,
        )
    try:
        expected = dependency_path.read_bytes()
    except OSError:
        return DirectDependencyReadControl(
            exists=True,
            regular_file=True,
            symlink=False,
            private_mode=private_mode,
            byte_length=None,
            sha256=None,
            subprocess_exit_status=None,
            subprocess_byte_identical=None,
        )
    try:
        completed = subprocess.run(
            ["cat", str(dependency_path)],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            check=False,
            timeout=5,
        )
        byte_identical = completed.returncode == 0 and completed.stdout == expected
        exit_status = completed.returncode
    except (OSError, subprocess.SubprocessError):
        return DirectDependencyReadControl(
            exists=True,
            regular_file=regular,
            symlink=symlink,
            private_mode=private_mode,
            byte_length=len(expected) if expected is not None else None,
            sha256=(hashlib.sha256(expected).hexdigest() if expected is not None else None),
            subprocess_exit_status=None,
            subprocess_byte_identical=None,
        )
    return DirectDependencyReadControl(
        exists=True,
        regular_file=regular,
        symlink=symlink,
        private_mode=private_mode,
        byte_length=len(expected) if expected is not None else None,
        sha256=hashlib.sha256(expected).hexdigest() if expected is not None else None,
        subprocess_exit_status=exit_status,
        subprocess_byte_identical=byte_identical,
    )


def _sandbox_environment(codex_home: Path) -> dict[str, str]:
    """Build a disposable helper environment without inherited credentials."""

    environment = {
        name: os.environ[name] for name in ("PATH", "LANG", "LC_ALL", "TERM") if name in os.environ
    }
    environment.update(
        {
            "CODEX_HOME": str(codex_home),
            "HOME": str(codex_home.parent),
            "TMPDIR": str(codex_home.parent),
        }
    )
    return environment


def _sanitized_codex_version(codex_bin: Path | str, environment: Mapping[str, str]) -> str | None:
    """Read only a semantic CLI version and discard bounded process text."""

    try:
        result = subprocess.run(
            [str(codex_bin), "--version"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            check=False,
            env=dict(environment),
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    for stream in (result.stdout, result.stderr):
        for line in stream[:4_096].splitlines()[:4]:
            match = re.search(rb"\b(\d+\.\d+\.\d+)\b", line)
            if match is not None:
                return match.group(1).decode("ascii")
    return None


def _sandbox_kernel_capabilities() -> tuple[str, ...]:
    """Return fixed capability labels without retaining host paths or values."""

    labels = [f"platform_{platform.system().lower() or 'unknown'}"]
    labels.append("bwrap_present" if shutil.which("bwrap") else "bwrap_missing")
    labels.append(
        "user_namespace_probe_available"
        if Path("/proc/sys/kernel/unprivileged_userns_clone").is_file()
        else "user_namespace_probe_unavailable"
    )
    labels.append(
        "seccomp_probe_available"
        if Path("/proc/sys/kernel/seccomp/actions_avail").is_file()
        else "seccomp_probe_unavailable"
    )
    return tuple(labels)


def build_sandbox_preflight_argv(
    codex_bin: Path | str, repository: Path, target: Path
) -> tuple[str, ...]:
    """Build the documented Linux helper command with a relative in-root target."""

    repository_resolved = repository.resolve(strict=False)
    target_resolved = target.resolve(strict=False)
    try:
        relative_target = target_resolved.relative_to(repository_resolved).as_posix()
    except ValueError as exc:
        raise ValueError("sandbox preflight target must be inside repository") from exc
    if not relative_target or relative_target == ".":
        raise ValueError("sandbox preflight target must be a file")
    return (
        str(codex_bin),
        "sandbox",
        SANDBOX_PLATFORM,
        "--permission-profile",
        SANDBOX_PERMISSION_PROFILE,
        "--cd",
        str(repository_resolved),
        "--",
        "/bin/cat",
        relative_target,
    )


def _classify_sandbox_preflight(
    *,
    process_exit_status: int | None,
    process_status: Literal["success", "failed", "unknown"],
    timed_out: bool,
    stderr: BinaryStreamFacts,
    working_directory_inside_repository: bool,
    target_inside_repository: bool,
    target_regular_file: bool,
    target_symlink: bool,
    byte_identical: bool | None,
) -> SandboxBoundaryClassification:
    """Classify the direct helper boundary from fixed facts only."""

    if not working_directory_inside_repository or not target_inside_repository:
        return "workspace_root_resolution_mismatch"
    if (
        process_exit_status == 0
        and process_status == "success"
        and not timed_out
        and target_regular_file
        and not target_symlink
        and byte_identical is True
    ):
        return "workspace_sandbox_available"
    if timed_out:
        return "unresolved_with_fixed_evidence"
    if stderr.first_line_subclass in {"bwrap_loopback_bootstrap", "bwrap_bootstrap_denied"}:
        return "host_sandbox_bootstrap_unsupported"
    if stderr.first_line_class in {"sandbox_denied", "permission_denied"}:
        return "host_sandbox_bootstrap_unsupported"
    if stderr.first_line_class == "not_found" and target_regular_file and not target_symlink:
        return "workspace_root_resolution_mismatch"
    if stderr.first_line_class in {"argv_unsupported", "schema_invalid"}:
        return "invocation_config_precedence_error"
    return "unresolved_with_fixed_evidence"


def run_sandbox_preflight(
    codex_bin: Path | str,
    fixture: GovernedFixturePaths,
    *,
    timeout_seconds: float = SANDBOX_PREFLIGHT_TIMEOUT_SECONDS,
) -> SandboxPreflightFacts:
    """Run one no-model sandbox-helper read and discard raw process streams."""

    repository = fixture.repository.resolve(strict=False)
    target = fixture.repository / "GOVERNANCE-DEPENDENCY.md"
    target_inside = False
    target_regular = False
    target_symlink = False
    target_length: int | None = None
    target_hash: str | None = None
    target_bytes: bytes | None = None
    try:
        target_stat = target.lstat()
        target_regular = stat.S_ISREG(target_stat.st_mode)
        target_symlink = stat.S_ISLNK(target_stat.st_mode)
        target_resolved = target.resolve(strict=False)
        target_inside = target_resolved == repository or repository in target_resolved.parents
        if target_regular and not target_symlink:
            target_bytes = target.read_bytes()
            target_length = len(target_bytes)
            target_hash = hashlib.sha256(target_bytes).hexdigest()
    except OSError:
        target_bytes = None

    environment = _sandbox_environment(fixture.codex_home)
    cli_version = _sanitized_codex_version(codex_bin, environment)
    stdout_facts = BinaryStreamFacts(
        byte_length=0,
        sha256=hashlib.sha256(b"").hexdigest(),
        first_line_class="unavailable",
    )
    stderr_facts = stdout_facts
    process_exit_status: int | None = None
    timed_out = False
    process_status: Literal["success", "failed", "unknown"] = "unknown"
    try:
        command = build_sandbox_preflight_argv(codex_bin, fixture.repository, target)
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            process = subprocess.Popen(
                command,
                cwd=repository,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
            )
            try:
                process_exit_status = process.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                timed_out = True
            process_status = (
                "success"
                if process_exit_status == 0 and not timed_out
                else ("failed" if process_exit_status is not None or timed_out else "unknown")
            )
            for stream_name, stream in (("stdout", stdout), ("stderr", stderr)):
                stream_length = stream.seek(0, os.SEEK_END)
                if stream_length > SANDBOX_PREFLIGHT_MAX_OUTPUT_BYTES:
                    raise OverflowError(f"sandbox preflight {stream_name} exceeded bound")
                stream.seek(0)
                facts = _binary_stream_facts(stream)
                if stream_name == "stdout":
                    stdout_facts = facts
                else:
                    stderr_facts = facts
    except (OSError, subprocess.SubprocessError, OverflowError):
        process_exit_status = None
        process_status = "unknown"

    observed_length = stdout_facts.byte_length if stdout_facts.byte_length else None
    observed_hash = stdout_facts.sha256 if observed_length is not None else None
    byte_identical: bool | None = (
        target_hash is not None
        and target_length is not None
        and observed_hash == target_hash
        and observed_length == target_length
    )
    if target_bytes is None or observed_length is None:
        byte_identical = None
    policy_resolution: SandboxPolicyResolution
    if cli_version is None:
        policy_resolution = "unknown"
    elif stderr_facts.first_line_class in {"argv_unsupported", "schema_invalid"}:
        policy_resolution = "unresolved"
    else:
        policy_resolution = "resolved"
    classification = _classify_sandbox_preflight(
        process_exit_status=process_exit_status,
        process_status=process_status,
        timed_out=timed_out,
        stderr=stderr_facts,
        working_directory_inside_repository=repository == fixture.repository.resolve(strict=False),
        target_inside_repository=target_inside,
        target_regular_file=target_regular,
        target_symlink=target_symlink,
        byte_identical=byte_identical,
    )
    return SandboxPreflightFacts(
        cli_version=cli_version,
        platform=SANDBOX_PLATFORM,
        kernel_capabilities=_sandbox_kernel_capabilities(),
        sandbox_mode="workspace-write",
        permission_profile=SANDBOX_PERMISSION_PROFILE,
        feature_labels=("direct_no_model", "workspace_write", "linux_bwrap_seccomp"),
        policy_resolution=policy_resolution,
        working_directory_inside_repository=repository == fixture.repository.resolve(strict=False),
        target_inside_repository=target_inside,
        target_regular_file=target_regular,
        target_symlink=target_symlink,
        target_byte_length=target_length,
        target_sha256=target_hash,
        observed_byte_length=observed_length,
        observed_sha256=observed_hash,
        byte_identical=byte_identical,
        process_exit_status=process_exit_status,
        process_status=process_status,
        timed_out=timed_out,
        stdout=stdout_facts,
        stderr=stderr_facts,
        boundary_classification=classification,
    )


def classify_sandbox_boundary(
    preflight: SandboxPreflightFacts, nested_run: SanitizedCodexRun | None = None
) -> SandboxBoundaryClassification:
    """Compare direct helper facts with a nested Codex lifecycle, if permitted."""

    if not preflight.successful:
        return preflight.boundary_classification
    if nested_run is None:
        return "workspace_sandbox_available"
    if nested_run.command_diagnostics.command_path_inside_repository is False:
        return "workspace_root_resolution_mismatch"
    if (
        nested_run.sandbox_mode != SANDBOX_PERMISSION_PROFILE
        or nested_run.approval_policy != "never"
        or nested_run.command_diagnostics.failure_class in {"argv_unsupported", "schema_invalid"}
        or (
            nested_run.command_diagnostics.actual_argv_shape != "absent"
            and nested_run.command_diagnostics.requested_argv_shape
            != nested_run.command_diagnostics.actual_argv_shape
        )
    ):
        return "invocation_config_precedence_error"
    if (
        nested_run.command_diagnostics.command_status == "unknown"
        and nested_run.tool_calls > 0
        and nested_run.dependency_observation.intended_dependency_reads == 0
    ):
        return "command_event_schema_mismatch"
    if (
        nested_run.failure_reason == "success"
        and nested_run.dependency_observation.lifecycle == "success"
    ):
        return "workspace_sandbox_available"
    return "unresolved_with_fixed_evidence"


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


_DEPENDENCY_READ = re.compile(
    r"^(?:(?:/bin/)?cat|head(?:\s+-n\s+\d+)?|tail(?:\s+-n\s+\d+)?|"
    r"sed\s+-n\s+['\"]?\d+(?:,\d+)?p['\"]?)\s+"
    r"['\"]?(?:\./)?GOVERNANCE-DEPENDENCY\.md['\"]?$"
)


def _parsed_e2e_command(arguments: object) -> str | None:
    """Parse the same bounded read-command shapes accepted by the detector."""
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except (json.JSONDecodeError, RecursionError):
            return None
    if isinstance(arguments, dict):
        arguments = arguments.get("cmd", arguments.get("arguments", arguments.get("command")))
    if isinstance(arguments, str):
        return arguments
    if not isinstance(arguments, list) or not arguments:
        return None
    argv = [part for part in arguments if isinstance(part, str)]
    if len(argv) != len(arguments):
        return None
    if len(argv) == 1:
        return argv[0]
    if len(argv) >= 3 and argv[0] in {"bash", "sh", "zsh"} and argv[1] in {"-c", "-lc"}:
        return argv[2]
    return " ".join(argv)


def _unwrap_shell_string(command: str) -> str:
    """Unwrap one bounded explicit shell invocation without executing it."""
    if len(command) > 1_024:
        return command
    try:
        argv = shlex.split(command)
    except ValueError:
        return command
    if (
        len(argv) >= 3
        and Path(argv[0]).name in {"bash", "sh", "zsh"}
        and argv[1] in {"-c", "-lc", "-cl"}
    ):
        return argv[2]
    return command


def _bounded_item_command(item: Mapping[str, Any]) -> str | None:
    """Read a built-in command or JSON-encoded function arguments without logging."""
    arguments: object = item.get("arguments")
    if arguments is None:
        arguments = item.get("cmd", item.get("command"))
    elif isinstance(arguments, dict):
        arguments = arguments.get("cmd", arguments.get("arguments", arguments.get("command")))
    if isinstance(arguments, str) and item.get("type") == "function_call":
        return _parsed_e2e_command(arguments)
    if isinstance(arguments, str):
        return arguments
    if isinstance(arguments, list):
        return _parsed_e2e_command(arguments)
    return None


def _is_intended_dependency_read(item: Mapping[str, Any]) -> bool:
    command = _bounded_item_command(item)
    if command is None:
        return False
    return _DEPENDENCY_READ.fullmatch(_unwrap_shell_string(command.strip())) is not None


def _first_bounded_text(value: Mapping[str, Any], keys: tuple[str, ...]) -> str | None:
    """Read one approved output field without retaining or logging its value."""
    for key in keys:
        output = value.get(key)
        if isinstance(output, str):
            return output
    return None


def _command_exit_failed(value: Mapping[str, Any]) -> bool:
    """Interpret only the bounded fixed exit-status field."""
    if value.get("status") in {"failed", "failure", "error"}:
        return True
    exit_code = value.get("exit_code")
    return exit_code is not None and not (
        isinstance(exit_code, (int, str))
        and not isinstance(exit_code, bool)
        and str(exit_code) == "0"
    )


def _parsed_exit_code(value: object) -> int | None:
    """Normalize the bounded integer exit-code shapes emitted by Codex."""
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and re.fullmatch(r"-?\d+", value):
        return int(value)
    return None


_DIAGNOSTIC_PATTERNS: tuple[tuple[DiagnosticFailureClass, str], ...] = (
    ("sandbox_denied", r"\b(bwrap|sandbox|blocked by policy|operation not permitted)\b"),
    ("permission_denied", r"\b(permission denied|access denied|eacces|eperm)\b"),
    ("not_found", r"\b(no such file or directory|not found|enoent)\b"),
    ("argv_unsupported", r"\b(unrecognized option|unexpected argument|unknown option)\b"),
    ("schema_invalid", r"\b(schema|invalid (?:request|arguments)|missing required)\b"),
    ("signal", r"\b(signal|killed|terminated)\b"),
)


def _first_diagnostic_line(text: str) -> str:
    """Ignore fixed Codex warning preambles before classifying diagnostics."""

    for line in text.splitlines():
        if line.strip().lower().startswith(("warning:", "warn:")):
            continue
        return line
    return ""


def _classify_diagnostic_text(text: str) -> DiagnosticFailureClass:
    """Map only the first diagnostic line through fixed allowlisted patterns."""

    first_line = _first_diagnostic_line(text)
    for failure_class, pattern in _DIAGNOSTIC_PATTERNS:
        if re.search(pattern, first_line, flags=re.IGNORECASE):
            return failure_class
    return "success" if first_line else "unavailable"


def _classify_sandbox_diagnostic_subclass(text: str) -> SandboxDiagnosticSubclass:
    """Map one first diagnostic line to a fixed privacy-safe subclass."""

    first_line = _first_diagnostic_line(text)
    lowered = first_line.lower()
    if not lowered:
        return "empty"
    if "bwrap" in lowered and "rtm_newaddr" in lowered:
        return "bwrap_loopback_bootstrap"
    if "bwrap" in lowered:
        return "bwrap_bootstrap_denied"
    if "permission denied" in lowered or "access denied" in lowered:
        return "permission"
    if "no such file or directory" in lowered or "not found" in lowered:
        return "not_found"
    if "unrecognized option" in lowered or "unexpected argument" in lowered:
        return "argument"
    if "schema" in lowered or "invalid request" in lowered:
        return "schema"
    if "timeout" in lowered or "timed out" in lowered:
        return "timeout"
    return "other"


def _binary_stream_facts(stream: io.BufferedIOBase) -> BinaryStreamFacts:
    """Hash a bounded stream and classify only its first nonempty line."""

    digest = hashlib.sha256()
    length = 0
    first_line = bytearray()
    first_line_complete = False
    while chunk := stream.read(65_536):
        length += len(chunk)
        digest.update(chunk)
        if not first_line_complete:
            leading, separator, _remainder = chunk.partition(b"\n")
            first_line.extend(leading[: max(0, 4_096 - len(first_line))])
            first_line_complete = bool(separator)
    return BinaryStreamFacts(
        byte_length=length,
        sha256=digest.hexdigest(),
        first_line_class=_classify_diagnostic_text(first_line.decode("utf-8", errors="replace")),
        first_line_subclass=_classify_sandbox_diagnostic_subclass(
            first_line.decode("utf-8", errors="replace")
        ),
    )


def _argv_shape(value: object) -> ArgvShape:
    if value is None:
        return "absent"
    if isinstance(value, str):
        return "single_string"
    if not isinstance(value, list) or not value:
        return "unsupported"
    argv = [part for part in value if isinstance(part, str)]
    if len(argv) != len(value):
        return "unsupported"
    if (
        Path(argv[0]).name in {"bash", "sh", "zsh"}
        and len(argv) >= 3
        and argv[1]
        in {
            "-c",
            "-lc",
            "-cl",
        }
    ):
        return "shell_wrapped_list"
    return "argv_list"


def _command_target_inside_repository(item: Mapping[str, Any], repository: Path) -> bool | None:
    command_value = item.get("command")
    if isinstance(command_value, str):
        unwrapped = _unwrap_shell_string(command_value.strip())
        try:
            parts = shlex.split(unwrapped)
        except ValueError:
            return None
    elif isinstance(command_value, list) and all(isinstance(part, str) for part in command_value):
        parts = command_value
    else:
        return None
    if len(parts) < 2:
        return None
    target = next((part for part in parts[1:] if not part.startswith("-")), None)
    if target is None:
        return False
    try:
        target_path = Path(target)
        resolved = (
            target_path.resolve(strict=False)
            if target_path.is_absolute()
            else (repository / target_path).resolve(strict=False)
        )
        return (
            resolved == repository.resolve(strict=False)
            or repository.resolve(strict=False) in resolved.parents
        )
    except OSError:
        return False


def parse_dependency_observation_events(
    event_stream: Iterable[str],
) -> DependencyObservationFacts:
    """Extract exactly-one-read and successful-lifecycle evidence from JSONL."""
    identities: set[str] = set()
    started: set[str] = set()
    successful: set[str] = set()
    failed: set[str] = set()
    outputs: dict[str, str] = {}

    def visit(value: object, top_level_type: str | None) -> None:
        if isinstance(value, list):
            for child in value:
                visit(child, top_level_type)
            return
        if not isinstance(value, dict) or value.get("type") != "command_execution":
            if isinstance(value, dict):
                for child in value.values():
                    visit(child, top_level_type)
            return
        identity_value = value.get("id", value.get("call_id"))
        identity = (
            identity_value if isinstance(identity_value, str) and identity_value else "command"
        )
        if not (_is_intended_dependency_read(value) or identity in identities):
            return
        identities.add(identity)
        if top_level_type == "item.started":
            started.add(identity)
        elif top_level_type == "item.completed":
            status = value.get("status")
            command_failed = _command_exit_failed(value)
            if command_failed:
                failed.add(identity)
            elif status in {"completed", "success"}:
                successful.add(identity)
                output = _first_bounded_text(
                    value,
                    ("aggregated_output", "aggregate_output", "output", "content", "text"),
                )
                if output is not None:
                    outputs[identity] = output
        for child in value.values():
            visit(child, top_level_type)

    for line in event_stream:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        top_level_type = event.get("type")
        visit(event, top_level_type if isinstance(top_level_type, str) else None)

    selected_output = next(iter(outputs.values())) if len(outputs) == 1 else None
    encoded = selected_output.encode("utf-8") if selected_output is not None else None
    stripped_encoded = (
        selected_output.encode("utf-8").rstrip() if selected_output is not None else None
    )

    return DependencyObservationFacts(
        intended_dependency_reads=len(identities),
        started_commands=len(started),
        completed_commands=len(successful),
        failed_commands=len(failed),
        successful_dependency_reads=len(successful),
        output_sha256=hashlib.sha256(encoded).hexdigest() if encoded is not None else None,
        output_byte_length=len(encoded) if encoded is not None else None,
        rstrip_output_sha256=(
            hashlib.sha256(stripped_encoded).hexdigest() if stripped_encoded is not None else None
        ),
    )


def parse_command_diagnostics_events(
    event_stream: Iterable[str], repository: Path
) -> CommandDiagnostics:
    """Extract bounded command facts without retaining output or argv values."""

    identities: set[str] = set()
    requested_shape: ArgvShape = "absent"
    actual_shape: ArgvShape = "absent"
    path_inside: bool | None = None
    exit_code: int | None = None
    status: Literal["success", "failed", "unknown"] = "unknown"
    output_class: DiagnosticFailureClass = "unavailable"
    output_hash: str | None = None
    output_length: int | None = None

    def visit(value: object, top_level_type: str | None) -> None:
        nonlocal requested_shape, actual_shape, path_inside
        nonlocal exit_code, status, output_class, output_hash, output_length
        if isinstance(value, list):
            for child in value:
                visit(child, top_level_type)
            return
        if not isinstance(value, dict) or value.get("type") != "command_execution":
            if isinstance(value, dict):
                for child in value.values():
                    visit(child, top_level_type)
            return
        identity_value = value.get("id", value.get("call_id"))
        identity = (
            identity_value if isinstance(identity_value, str) and identity_value else "command"
        )
        if not (_is_intended_dependency_read(value) or identity in identities):
            return
        identities.add(identity)
        shape = _argv_shape(value.get("command"))
        inside = _command_target_inside_repository(value, repository)
        if top_level_type == "item.started":
            requested_shape = shape
            path_inside = inside
        elif top_level_type == "item.completed":
            if shape != "absent":
                actual_shape = shape
            path_inside = path_inside if inside is None else inside
            raw_exit = value.get("exit_code")
            parsed_exit = _parsed_exit_code(raw_exit)
            if parsed_exit is not None:
                exit_code = parsed_exit
            if value.get("status") in {"failed", "failure", "error"}:
                status = "failed"
            elif value.get("status") in {"completed", "success"} and (
                parsed_exit is None or parsed_exit == 0
            ):
                status = "success"
            else:
                status = "failed" if _command_exit_failed(value) else "unknown"
            output = _first_bounded_text(
                value,
                ("aggregated_output", "aggregate_output", "output", "content", "text"),
            )
            if output is not None:
                encoded = output.encode("utf-8")[:CODEX_MAX_DIAGNOSTIC_BYTES]
                output_class = _classify_diagnostic_text(output)
                output_hash = hashlib.sha256(encoded).hexdigest()
                output_length = len(output.encode("utf-8"))

    for line in event_stream:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        top_level_type = event.get("type")
        visit(event, top_level_type if isinstance(top_level_type, str) else None)
    return CommandDiagnostics(
        failure_class=(
            "success"
            if status == "success"
            else ("unknown_nonzero" if status == "failed" else "unavailable")
        ),
        process_exit_code=None,
        process_status="unknown",
        stdout=None,
        stderr=None,
        command_exit_code=exit_code,
        command_status=status,
        command_output_class=output_class,
        command_output_sha256=output_hash,
        command_output_byte_length=output_length,
        requested_argv_shape=requested_shape,
        actual_argv_shape=actual_shape,
        command_path_inside_repository=path_inside,
    )


def _sentinel_failure_reason(
    *,
    process_result: str,
    has_tool: bool,
    sentinel_passed: bool,
    observation: DependencyObservationFacts,
) -> str:
    """Gate governance attribution behind one successfully completed read."""
    if process_result != "success":
        return process_result
    if not has_tool:
        return "ordinary_tool_missing"
    if observation.lifecycle != "success":
        return f"command_{observation.lifecycle}"
    if not sentinel_passed:
        return "sentinel_missing"
    return "success"


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


def _normalized_diagnostic_class(
    *,
    exit_status: int | None,
    timed_out: bool,
    stdout: BinaryStreamFacts,
    stderr: BinaryStreamFacts,
    command: CommandDiagnostics,
) -> DiagnosticFailureClass:
    """Combine bounded process and command facts without exposing their text."""

    if timed_out:
        return "timeout"
    if exit_status is None:
        return "unavailable"
    if exit_status < 0:
        return "signal"
    if exit_status == 0 and command.command_status == "success":
        return "success"
    candidates = (
        command.command_output_class,
        stderr.first_line_class,
        stdout.first_line_class,
    )
    for candidate in candidates:
        if candidate not in {"success", "unavailable"}:
            return candidate
    return "unknown_nonzero" if exit_status != 0 else "unknown_nonzero"


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
    dependency_observation = DependencyObservationFacts()
    final_event_ack = False
    stdout_facts = BinaryStreamFacts(0, hashlib.sha256(b"").hexdigest(), "unavailable")
    stderr_facts = BinaryStreamFacts(0, hashlib.sha256(b"").hexdigest(), "unavailable")
    event_command_diagnostics = CommandDiagnostics()
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
            stdout_facts = _binary_stream_facts(events)
            events.seek(0)
            readable = io.TextIOWrapper(events, encoding="utf-8", errors="replace")
            counts, call_items, tools = parse_codex_events(readable)
            readable.detach()
            events.seek(0)
            command_reader = io.TextIOWrapper(events, encoding="utf-8", errors="replace")
            command_event_counts = parse_codex_command_events(command_reader)
            command_reader.detach()
            events.seek(0)
            observation_reader = io.TextIOWrapper(events, encoding="utf-8", errors="replace")
            dependency_observation = parse_dependency_observation_events(observation_reader)
            observation_reader.detach()
            events.seek(0)
            diagnostic_command_reader = io.TextIOWrapper(events, encoding="utf-8", errors="replace")
            event_command_diagnostics = parse_command_diagnostics_events(
                diagnostic_command_reader, fixture.repository
            )
            diagnostic_command_reader.detach()
            events.seek(0)
            final_event_reader = io.TextIOWrapper(events, encoding="utf-8", errors="replace")
            final_event_ack = _final_agent_message_has_ack(
                final_event_reader, f"SENTINEL-ACK:{fixture.sentinel_token}"
            )
            final_event_reader.detach()
            diagnostics_size = diagnostics.seek(0, os.SEEK_END)
            if diagnostics_size > CODEX_MAX_DIAGNOSTIC_BYTES:
                raise OverflowError
            diagnostics.seek(0)
            stderr_facts = _binary_stream_facts(diagnostics)
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
        if not tools:
            failure_reason = "ordinary_tool_missing"
        else:
            failure_reason = _sentinel_failure_reason(
                process_result="success",
                has_tool=True,
                sentinel_passed=sentinel_passed,
                observation=dependency_observation,
            )
    try:
        output_path.unlink()
    except FileNotFoundError:
        pass
    duration = time.monotonic() - started
    command_diagnostics = dataclasses.replace(
        event_command_diagnostics,
        failure_class=_normalized_diagnostic_class(
            exit_status=exit_status,
            timed_out=timed_out,
            stdout=stdout_facts,
            stderr=stderr_facts,
            command=event_command_diagnostics,
        ),
        process_exit_code=exit_status,
        process_status=(
            "success"
            if exit_status == 0 and not timed_out
            else ("failed" if exit_status is not None or timed_out else "unknown")
        ),
        stdout=stdout_facts,
        stderr=stderr_facts,
    )
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
        dependency_observation=dependency_observation,
        command_diagnostics=command_diagnostics,
        sandbox_mode="workspace-write",
        approval_policy="never",
    )


def governed_prompt(*, read_form: DependencyReadForm = "relative_cat") -> str:
    """Build a bounded prompt that delegates the response token to governance."""

    command = (
        "cat GOVERNANCE-DEPENDENCY.md"
        if read_form == "relative_cat"
        else "/bin/cat GOVERNANCE-DEPENDENCY.md"
    )
    return (
        f"First call shell_command exactly once with command {command}. "
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
                stored_source_sha256=index.source_sha256,
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
            stored_source_sha256=entry.stored_source_sha256,
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
    observed_dependency_sha256: str | None,
    consistency_errors: tuple[str, ...],
) -> CacheOutcomeClassification:
    if consistency_errors:
        return "observation_mismatch"
    misses = metric_deltas["dependency_cache_misses"].delta
    hits = metric_deltas["dependency_cache_hits"].delta
    prefix = None if observed_dependency_sha256 is None else observed_dependency_sha256[:12]
    same_source_before = prefix is not None and any(
        entry.index_kind == "dependency" and entry.stored_source_sha256_prefix == prefix
        for entry in inventory_before.entries
    )
    different_source_after = prefix is not None and any(
        entry.index_kind == "dependency" and entry.stored_source_sha256_prefix != prefix
        for entry in inventory_after.entries
    )
    matching_after = prefix is not None and any(
        entry.index_kind == "dependency"
        and entry.stored_source_sha256 == observed_dependency_sha256
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
    observed_dependency_sha256: str | None,
) -> tuple[bool | None, bool, bool | None, tuple[str, ...]]:
    """Reconcile counter deltas with sanitized before/after inventories."""

    errors: list[str] = []
    if not fixture_hashes_stable:
        errors.append("fixture_hash_changed")
    hits = metric_deltas["dependency_cache_hits"].delta
    misses = metric_deltas["dependency_cache_misses"].delta
    observed_prefix = (
        None if observed_dependency_sha256 is None else observed_dependency_sha256[:12]
    )
    matching_before = observed_prefix is not None and any(
        entry.index_kind == "dependency" and entry.stored_source_sha256_prefix == observed_prefix
        for entry in inventory_before.entries
    )
    different_source = any(
        entry.index_kind == "dependency"
        and observed_prefix is not None
        and entry.stored_source_sha256_prefix != observed_prefix
        for entry in inventory_after.entries
    )
    if any(not float(delta.delta).is_integer() for delta in metric_deltas.values()):
        errors.append("non_integer_counter_delta")
    miss_stored_match: bool | None = None
    if misses > 0:
        if observed_dependency_sha256 is None:
            errors.append("observed_dependency_unavailable")
        else:
            miss_stored_match = any(
                entry.index_kind == "dependency"
                and entry.stored_source_sha256 == observed_dependency_sha256
                for entry in inventory_after.entries
            )
            if not miss_stored_match:
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
        dependency_bytes = dependency_path.read_bytes()
        dependency_hash = hashlib.sha256(dependency_bytes).hexdigest()
        dependency_length = len(dependency_bytes)
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
    observation = run.dependency_observation
    observed_hash = observation.output_sha256
    observed_length = observation.output_byte_length
    hash_equal = observed_hash is not None and observed_hash == dependency_hash
    length_equal = observed_length is not None and observed_length == dependency_length
    terminal_whitespace_only = (
        observed_hash is not None
        and observed_length is not None
        and observation.rstrip_output_sha256 is not None
        and hashlib.sha256(dependency_bytes.rstrip()).hexdigest()
        == observation.rstrip_output_sha256
    )
    if observed_hash is None or observed_length is None:
        provenance: DependencyProvenanceClassification = "unavailable"
    elif hash_equal and length_equal:
        provenance = "equal"
    elif terminal_whitespace_only:
        provenance = "tool_boundary_normalization"
    else:
        provenance = "observation_mismatch"
    if terminal_whitespace_only and observed_hash is not None:
        terminal_whitespace_only = True
    else:
        terminal_whitespace_only = False
    command_state = observation.lifecycle
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
        observed_dependency_sha256=observed_hash,
    )
    classification = _classify_dependency_cache_outcome(
        metric_deltas=metric_deltas,
        inventory_before=inventory_before,
        inventory_after=inventory_after,
        observed_dependency_sha256=observed_hash,
        consistency_errors=errors,
    )
    return DependencyCacheDiagnosticFacts(
        run=run,
        fixture_root_sha256=root_hash,
        fixture_dependency_sha256=dependency_hash,
        fixture_dependency_byte_length=dependency_length,
        observed_dependency_sha256=observed_hash,
        observed_dependency_byte_length=observed_length,
        repository_observed_hash_equal=hash_equal,
        repository_observed_length_equal=length_equal,
        repository_differs_only_by_terminal_whitespace=terminal_whitespace_only,
        dependency_provenance=provenance,
        dependency_command_state=command_state,
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


def run_command_failure_diagnostic(
    codex_bin: Path | str,
    *,
    base_url: str = DEFAULT_ADAPTER_BASE_URL,
    api_key_env: str = DEFAULT_API_KEY_ENV,
) -> CommandFailureDiagnosisFacts:
    """Preflight the OS sandbox, then allow at most two governed attempts."""

    with tempfile.TemporaryDirectory(prefix="slaif-codex-command-diagnosis-") as temporary:
        fixture = write_governed_fixture(Path(temporary), base_url, api_key_env)
        dependency_path = fixture.repository / "GOVERNANCE-DEPENDENCY.md"
        dependency_bytes = dependency_path.read_bytes()
        dependency_hash = hashlib.sha256(dependency_bytes).hexdigest()
        stripped_hash = hashlib.sha256(dependency_bytes.rstrip()).hexdigest()
        dependency_length = len(dependency_bytes)
        preflight = run_sandbox_preflight(codex_bin, fixture)

        attempts: list[CommandDiagnosticAttempt] = []
        if preflight.successful:
            write_local_model_catalog(codex_bin, fixture.model_catalog)
            forms: tuple[DependencyReadForm, ...] = ("relative_cat", "absolute_bin_cat")
            for read_form in forms:
                direct_read = verify_direct_dependency_read(fixture)
                run = run_codex_once(codex_bin, fixture, governed_prompt(read_form=read_form))
                attempts.append(
                    CommandDiagnosticAttempt(
                        read_form=read_form,
                        direct_read=direct_read,
                        run=run,
                    )
                )
                if run.failure_reason == "success":
                    break

    boundary_classification = classify_sandbox_boundary(
        preflight, attempts[-1].run if attempts else None
    )
    return CommandFailureDiagnosisFacts(
        attempts=tuple(attempts),
        fixture_dependency_sha256=dependency_hash,
        fixture_dependency_byte_length=dependency_length,
        fixture_dependency_stripped_sha256=stripped_hash,
        sandbox_preflight=preflight,
        boundary_classification=boundary_classification,
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
