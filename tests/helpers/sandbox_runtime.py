"""Bounded native Codex workspace-write checks for repository tests.

This support is intentionally outside the installed package. It records only
allowlisted facts and uses disposable, caller-owned temporary state.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from tests.helpers.e2e_support import (
    DEFAULT_ADAPTER_BASE_URL,
    DEFAULT_API_KEY_ENV,
    BinaryStreamFacts,
    GovernedFixturePaths,
    SanitizedCodexRun,
    _binary_stream_facts,
    _sandbox_environment,
    governed_prompt,
    run_codex_once,
    write_governed_fixture,
    write_local_model_catalog,
)

SANDBOX_PREFLIGHT_TIMEOUT_SECONDS = 15.0
SANDBOX_PREFLIGHT_MAX_OUTPUT_BYTES = 1_048_576
SANDBOX_PERMISSION_PROFILE = ":workspace"
SANDBOX_MODE: Literal["workspace-write"] = "workspace-write"
SANDBOX_PLATFORM = "linux"

SandboxPolicyResolution = Literal["resolved", "unresolved", "unknown"]
SandboxProbeCommand = Literal["true", "pwd", "cat"]
SandboxRootClass = Literal["system_tmp", "repo_owned_scratch", "other"]
SandboxResolvedBasenameClass = Literal["expected", "other", "unavailable"]
SandboxRuntimeOutcome = Literal[
    "native_true_failed",
    "native_cat_failed",
    "native_preflight_succeeded",
    "governed_e2e_failed",
    "governed_e2e_succeeded",
]
SandboxRuntimePathKind = Literal["relative", "resolved_absolute", "original_absolute"]


@dataclass(frozen=True)
class SanitizedExecutableFacts:
    """Allowlisted local facts for one fixed absolute helper executable."""

    command: SandboxProbeCommand
    exists: bool
    regular_file: bool
    executable: bool
    symlink: bool
    resolved_basename_class: SandboxResolvedBasenameClass


@dataclass(frozen=True)
class SandboxProbeFacts:
    """Sanitized result of one no-model differential helper call."""

    command: SandboxProbeCommand
    root_class: SandboxRootClass
    executable: SanitizedExecutableFacts
    working_directory_inside_repository: bool
    target_inside_repository: bool | None
    target_regular_file: bool | None
    target_symlink: bool | None
    target_private_mode: bool | None
    target_byte_length: int | None
    target_sha256: str | None
    observed_byte_length: int
    observed_sha256: str
    expected_output_byte_length: int | None
    expected_output_sha256: str | None
    byte_identical: bool | None
    process_exit_status: int | None
    process_status: Literal["success", "failed", "unknown"]
    timed_out: bool
    stdout: BinaryStreamFacts
    stderr: BinaryStreamFacts
    policy_resolution: SandboxPolicyResolution

    @property
    def successful(self) -> bool:
        return (
            self.process_exit_status == 0
            and self.process_status == "success"
            and not self.timed_out
            and self.byte_identical is True
        )


@dataclass(frozen=True)
class InstalledPathFacts:
    """Allowlisted facts for one installed executable candidate."""

    label: str
    exists: bool
    regular_file: bool
    executable: bool
    symlink: bool
    resolved_basename_class: SandboxResolvedBasenameClass
    sha256: str | None = None
    version: str | None = None


@dataclass(frozen=True)
class InstalledDirectoryFacts:
    """Sanitized facts for the resolved Codex binary directory."""

    exists: bool
    directory: bool
    symlink: bool
    resolved_basename_class: SandboxResolvedBasenameClass
    companion_presence: tuple[tuple[str, bool], ...]


@dataclass(frozen=True)
class SandboxInstallationLayoutFacts:
    """Fixed, hashed installation-layout facts without retaining paths."""

    codex_launcher: InstalledPathFacts
    codex_binary_directory: InstalledDirectoryFacts
    true_bin: InstalledPathFacts
    true_usr_bin: InstalledPathFacts
    cat_bin: InstalledPathFacts
    cat_usr_bin: InstalledPathFacts
    true_bin_usr_same_file: bool | None
    cat_bin_usr_same_file: bool | None


@dataclass(frozen=True)
class SandboxRuntimeBoundaryFacts:
    """Final bounded native preflight and optional governed proof."""

    layout: SandboxInstallationLayoutFacts
    corrected_true_probe: SandboxProbeFacts | None
    corrected_cat_probe: SandboxProbeFacts | None
    corrected_true_path_kind: SandboxRuntimePathKind
    helper_calls: int
    classification: SandboxRuntimeOutcome
    fixture_dependency_sha256: str
    fixture_dependency_byte_length: int
    governed_attempts: tuple[SanitizedCodexRun, ...]

    @property
    def governed_gate_allowed(self) -> bool:
        return bool(self.corrected_cat_probe is not None and self.corrected_cat_probe.successful)


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


def _sandbox_root_class(path: Path, product_checkout: Path) -> SandboxRootClass:
    """Classify a disposable root without returning its path."""

    resolved = path.resolve(strict=False)
    system_tmp = Path(tempfile.gettempdir()).resolve()
    checkout = product_checkout.resolve(strict=False)
    if resolved != checkout and checkout in resolved.parents:
        return "repo_owned_scratch"
    if resolved == system_tmp or system_tmp in resolved.parents:
        return "system_tmp"
    return "other"


def _sanitized_executable_facts(command: SandboxProbeCommand) -> SanitizedExecutableFacts:
    """Inspect only fixed /bin helpers and return allowlisted facts."""

    expected_name = command
    executable_path = Path("/bin") / expected_name
    try:
        path_stat = executable_path.lstat()
        resolved = executable_path.resolve(strict=True)
        return SanitizedExecutableFacts(
            command=command,
            exists=True,
            regular_file=stat.S_ISREG(path_stat.st_mode),
            executable=bool(path_stat.st_mode & 0o111),
            symlink=stat.S_ISLNK(path_stat.st_mode),
            resolved_basename_class=("expected" if resolved.name == expected_name else "other"),
        )
    except OSError:
        return SanitizedExecutableFacts(
            command=command,
            exists=False,
            regular_file=False,
            executable=False,
            symlink=False,
            resolved_basename_class="unavailable",
        )


def _bounded_path_sha256(path: Path) -> str | None:
    """Hash one fixed installed file only when its size is within the bound."""

    try:
        path_stat = path.stat()
        if (
            not stat.S_ISREG(path_stat.st_mode)
            or path_stat.st_size > SANDBOX_PREFLIGHT_MAX_OUTPUT_BYTES
        ):
            return None
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(65_536), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def _installed_path_facts(
    label: str, path: Path, expected_basename: str, *, version: str | None = None
) -> InstalledPathFacts:
    """Inspect a fixed candidate without exposing its path."""

    try:
        link_stat = path.lstat()
        target_stat = path.stat()
        resolved = path.resolve(strict=True)
        return InstalledPathFacts(
            label=label,
            exists=True,
            regular_file=stat.S_ISREG(target_stat.st_mode),
            executable=bool(target_stat.st_mode & 0o111),
            symlink=stat.S_ISLNK(link_stat.st_mode),
            resolved_basename_class=("expected" if resolved.name == expected_basename else "other"),
            sha256=_bounded_path_sha256(path),
            version=version,
        )
    except OSError:
        return InstalledPathFacts(
            label=label,
            exists=False,
            regular_file=False,
            executable=False,
            symlink=False,
            resolved_basename_class="unavailable",
            version=version,
        )


def _installed_directory_facts(path: Path) -> InstalledDirectoryFacts:
    """Inspect only fixed companion-name candidates in one resolved directory."""

    companion_candidates = (
        ("native_linux_x86_64", "codex-x86_64-unknown-linux-gnu"),
        ("native_linux_x86_64_gnu", "codex-linux-x86_64"),
        ("native_linux_x86_64_musl", "codex-x86_64-unknown-linux-musl"),
    )
    try:
        link_stat = path.lstat()
        target = path.resolve(strict=True)
        directory = path.is_dir()
        presence = tuple(
            (label, (target / candidate).exists()) for label, candidate in companion_candidates
        )
        return InstalledDirectoryFacts(
            exists=True,
            directory=directory,
            symlink=stat.S_ISLNK(link_stat.st_mode),
            resolved_basename_class=("expected" if "codex" in target.name else "other"),
            companion_presence=presence,
        )
    except OSError:
        return InstalledDirectoryFacts(
            exists=False,
            directory=False,
            symlink=False,
            resolved_basename_class="unavailable",
            companion_presence=tuple((label, False) for label, _ in companion_candidates),
        )


def _resolve_installed_command(command: str, supplied: Path | str | None = None) -> Path | None:
    """Resolve a launcher by name or accept an existing absolute path."""

    candidate = Path(supplied) if supplied is not None else Path(command)
    if candidate.is_absolute() and candidate.exists():
        return candidate
    resolved = shutil.which(str(candidate) if supplied is not None else command)
    return Path(resolved) if resolved is not None else None


def inspect_sandbox_installation_layout(
    codex_bin: Path | str | None = None,
) -> SandboxInstallationLayoutFacts:
    """Collect fixed executable/layout facts with no directory listing."""

    codex_path = _resolve_installed_command("codex", codex_bin)
    codex_facts = _installed_path_facts(
        "codex_launcher", codex_path or Path("/nonexistent"), "codex"
    )
    if codex_path is None:
        directory_facts = _installed_directory_facts(Path("/nonexistent"))
        version = None
    else:
        try:
            resolved_codex = codex_path.resolve(strict=True)
            directory_facts = _installed_directory_facts(resolved_codex.parent)
        except OSError:
            directory_facts = _installed_directory_facts(Path("/nonexistent"))
        version = _sanitized_codex_version(
            codex_path,
            {
                name: os.environ[name]
                for name in ("PATH", "LANG", "LC_ALL", "TERM")
                if name in os.environ
            },
        )
    codex_facts = dataclasses.replace(codex_facts, version=version)
    return SandboxInstallationLayoutFacts(
        codex_launcher=codex_facts,
        codex_binary_directory=directory_facts,
        true_bin=_installed_path_facts("true_bin", Path("/bin/true"), "true"),
        true_usr_bin=_installed_path_facts("true_usr_bin", Path("/usr/bin/true"), "true"),
        cat_bin=_installed_path_facts("cat_bin", Path("/bin/cat"), "cat"),
        cat_usr_bin=_installed_path_facts("cat_usr_bin", Path("/usr/bin/cat"), "cat"),
        true_bin_usr_same_file=_same_file_or_none(Path("/bin/true"), Path("/usr/bin/true")),
        cat_bin_usr_same_file=_same_file_or_none(Path("/bin/cat"), Path("/usr/bin/cat")),
    )


def _same_file_or_none(first: Path, second: Path) -> bool | None:
    try:
        return os.path.samefile(first, second)
    except OSError:
        return None


def _corrected_sandbox_executable(
    command: SandboxProbeCommand,
) -> tuple[str, SandboxRuntimePathKind]:
    """Select the real fixed candidate, or the relative spelling if unchanged."""

    candidate = Path("/bin") / command
    try:
        resolved = candidate.resolve(strict=True)
    except OSError:
        return command, "relative"
    if resolved != candidate:
        return str(resolved), "resolved_absolute"
    return command, "relative"


def _build_sandbox_probe_argv(
    codex_bin: Path | str,
    repository: Path,
    command: SandboxProbeCommand,
    target: Path | None = None,
    *,
    executable_path: str | None = None,
) -> tuple[str, ...]:
    """Build one direct, non-shell helper invocation."""

    repository_resolved = repository.resolve(strict=False)
    helper_path = f"/bin/{command}" if executable_path is None else executable_path
    if helper_path != command:
        allowed_resolutions = {
            (Path("/bin") / command).resolve(strict=False),
            (Path("/usr/bin") / command).resolve(strict=False),
        }
        try:
            if Path(helper_path).resolve(strict=False) not in allowed_resolutions:
                raise ValueError("sandbox probe executable must be a fixed system candidate")
        except OSError as exc:
            raise ValueError("sandbox probe executable must be a fixed system candidate") from exc
    argv = (
        str(codex_bin),
        "sandbox",
        "--permission-profile",
        SANDBOX_PERMISSION_PROFILE,
        "--cd",
        str(repository_resolved),
        "--",
        helper_path,
    )
    if command == "cat":
        if target is None:
            raise ValueError("cat sandbox probe requires a target")
        try:
            relative_target = (
                target.resolve(strict=False).relative_to(repository_resolved).as_posix()
            )
        except ValueError as exc:
            raise ValueError("sandbox probe target must be inside repository") from exc
        if not relative_target or relative_target == ".":
            raise ValueError("sandbox probe target must be a file")
        return (*argv, relative_target)
    if target is not None:
        raise ValueError("non-cat sandbox probe cannot have a target")
    return argv


def _sandbox_target_facts(
    repository: Path, target: Path | None
) -> tuple[
    bool | None,
    bool | None,
    bool | None,
    bool | None,
    int | None,
    str | None,
    bytes | None,
]:
    if target is None:
        return None, None, None, None, None, None, None
    repository_resolved = repository.resolve(strict=False)
    target_inside = False
    target_regular = False
    target_symlink = False
    target_private = False
    target_length: int | None = None
    target_hash: str | None = None
    target_bytes: bytes | None = None
    try:
        target_stat = target.lstat()
        target_regular = stat.S_ISREG(target_stat.st_mode)
        target_symlink = stat.S_ISLNK(target_stat.st_mode)
        target_private = not bool(target_stat.st_mode & 0o077)
        target_resolved = target.resolve(strict=False)
        target_inside = target_resolved == repository_resolved or repository_resolved in (
            target_resolved.parents
        )
        if target_regular and not target_symlink:
            target_bytes = target.read_bytes()
            target_length = len(target_bytes)
            target_hash = hashlib.sha256(target_bytes).hexdigest()
    except OSError:
        pass
    return (
        target_inside,
        target_regular,
        target_symlink,
        target_private,
        target_length,
        target_hash,
        target_bytes,
    )


def _run_sandbox_probe(
    codex_bin: Path | str,
    fixture: GovernedFixturePaths,
    command: SandboxProbeCommand,
    product_checkout: Path,
    *,
    executable_path: str | None = None,
) -> SandboxProbeFacts:
    """Run one bounded helper call and discard all raw process streams."""

    repository = fixture.repository.resolve(strict=False)
    target = fixture.repository / "GOVERNANCE-DEPENDENCY.md" if command == "cat" else None
    (
        target_inside,
        target_regular,
        target_symlink,
        target_private,
        target_length,
        target_hash,
        target_bytes,
    ) = _sandbox_target_facts(repository, target)
    expected_output: bytes | None
    if command == "true":
        expected_output = b""
    elif command == "pwd":
        expected_output = f"{repository}\n".encode()
    else:
        expected_output = target_bytes

    stdout_facts = BinaryStreamFacts(0, hashlib.sha256(b"").hexdigest(), "unavailable")
    stderr_facts = stdout_facts
    process_exit_status: int | None = None
    process_status: Literal["success", "failed", "unknown"] = "unknown"
    timed_out = False
    environment = _sandbox_environment(fixture.codex_home)
    try:
        command_argv = _build_sandbox_probe_argv(
            codex_bin,
            repository,
            command,
            target,
            executable_path=executable_path,
        )
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            process = subprocess.Popen(
                command_argv,
                cwd=repository,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
            )
            try:
                process_exit_status = process.wait(timeout=SANDBOX_PREFLIGHT_TIMEOUT_SECONDS)
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
                    raise OverflowError("sandbox probe output exceeded bound")
                stream.seek(0)
                facts = _binary_stream_facts(stream)
                if stream_name == "stdout":
                    stdout_facts = facts
                else:
                    stderr_facts = facts
    except (OSError, subprocess.SubprocessError, OverflowError):
        process_exit_status = None
        process_status = "unknown"

    observed_length = stdout_facts.byte_length
    observed_hash = stdout_facts.sha256
    byte_identical: bool | None = None
    if expected_output is not None:
        byte_identical = (
            process_exit_status == 0
            and process_status == "success"
            and not timed_out
            and observed_length == len(expected_output)
            and observed_hash == hashlib.sha256(expected_output).hexdigest()
        )
    if _sandbox_root_class(repository, product_checkout) == "other":
        root_class: SandboxRootClass = "other"
    else:
        root_class = _sandbox_root_class(repository, product_checkout)
    if command == "cat":
        policy_resolution: SandboxPolicyResolution = (
            "unresolved"
            if stderr_facts.first_line_class in {"argv_unsupported", "schema_invalid"}
            else "resolved"
        )
    else:
        policy_resolution = (
            "unresolved"
            if stderr_facts.first_line_class in {"argv_unsupported", "schema_invalid"}
            else "resolved"
        )
    return SandboxProbeFacts(
        command=command,
        root_class=root_class,
        executable=_sanitized_executable_facts(command),
        working_directory_inside_repository=repository == fixture.repository.resolve(strict=False),
        target_inside_repository=target_inside,
        target_regular_file=target_regular,
        target_symlink=target_symlink,
        target_private_mode=target_private,
        target_byte_length=target_length,
        target_sha256=target_hash,
        observed_byte_length=observed_length,
        observed_sha256=observed_hash,
        expected_output_byte_length=(len(expected_output) if expected_output is not None else None),
        expected_output_sha256=(
            hashlib.sha256(expected_output).hexdigest() if expected_output is not None else None
        ),
        byte_identical=byte_identical,
        process_exit_status=process_exit_status,
        process_status=process_status,
        timed_out=timed_out,
        stdout=stdout_facts,
        stderr=stderr_facts,
        policy_resolution=policy_resolution,
    )


def classify_sandbox_runtime_boundary(
    layout: SandboxInstallationLayoutFacts,
    corrected_true_probe: SandboxProbeFacts | None,
    corrected_cat_probe: SandboxProbeFacts | None,
    *,
    governed_attempts: tuple[SanitizedCodexRun, ...] = (),
) -> SandboxRuntimeOutcome:
    """Apply the native preflight and governed-E2E gate in order."""

    if corrected_true_probe is None:
        return "native_true_failed"
    if not corrected_true_probe.successful:
        return "native_true_failed"
    if corrected_cat_probe is None or not corrected_cat_probe.successful:
        return "native_cat_failed"
    if not governed_attempts:
        return "native_preflight_succeeded"
    return (
        "governed_e2e_succeeded"
        if len(governed_attempts) == 2
        and all(run.failure_reason == "success" for run in governed_attempts)
        else "governed_e2e_failed"
    )


def run_native_workspace_preflight(
    codex_bin: Path | str,
    *,
    product_checkout: Path | None = None,
) -> SandboxRuntimeBoundaryFacts:
    """Run native ``true`` then exact dependency ``cat`` without model calls."""

    layout = inspect_sandbox_installation_layout(codex_bin)
    checkout = (product_checkout or Path.cwd()).resolve(strict=False)
    corrected_true, true_path_kind = _corrected_sandbox_executable("true")
    corrected_cat, _ = _corrected_sandbox_executable("cat")
    true_probe: SandboxProbeFacts | None = None
    cat_probe: SandboxProbeFacts | None = None
    helper_calls = 0
    fixture_hash = "0" * 64
    fixture_length = 0

    with tempfile.TemporaryDirectory(prefix="slaif-codex-native-preflight-") as root_text:
        fixture = write_governed_fixture(Path(root_text), "", DEFAULT_API_KEY_ENV)
        dependency = (fixture.repository / "GOVERNANCE-DEPENDENCY.md").read_bytes()
        fixture_hash = hashlib.sha256(dependency).hexdigest()
        fixture_length = len(dependency)
        true_probe = _run_sandbox_probe(
            codex_bin,
            fixture,
            "true",
            checkout,
            executable_path=corrected_true,
        )
        helper_calls += 1
        if true_probe.successful:
            cat_probe = _run_sandbox_probe(
                codex_bin,
                fixture,
                "cat",
                checkout,
                executable_path=corrected_cat,
            )
            helper_calls += 1

    return SandboxRuntimeBoundaryFacts(
        layout=layout,
        corrected_true_probe=true_probe,
        corrected_cat_probe=cat_probe,
        corrected_true_path_kind=true_path_kind,
        helper_calls=helper_calls,
        classification=classify_sandbox_runtime_boundary(layout, true_probe, cat_probe),
        fixture_dependency_sha256=fixture_hash,
        fixture_dependency_byte_length=fixture_length,
        governed_attempts=(),
    )


def run_sandbox_runtime_boundary_diagnostic(
    codex_bin: Path | str,
    *,
    product_checkout: Path | None = None,
    base_url: str = DEFAULT_ADAPTER_BASE_URL,
    api_key_env: str = DEFAULT_API_KEY_ENV,
) -> SandboxRuntimeBoundaryFacts:
    """Run native true/cat, then exactly two governed calls after cat success."""

    layout = inspect_sandbox_installation_layout(codex_bin)
    checkout = (product_checkout or Path.cwd()).resolve(strict=False)
    corrected_true, true_path_kind = _corrected_sandbox_executable("true")
    corrected_cat, _ = _corrected_sandbox_executable("cat")
    true_probe: SandboxProbeFacts | None = None
    cat_probe: SandboxProbeFacts | None = None
    helper_calls = 0
    governed_attempts: list[SanitizedCodexRun] = []
    fixture_hash = "0" * 64
    fixture_length = 0

    with tempfile.TemporaryDirectory(prefix="slaif-codex-sandbox-final-") as root_text:
        fixture = write_governed_fixture(Path(root_text), base_url, api_key_env)
        dependency = (fixture.repository / "GOVERNANCE-DEPENDENCY.md").read_bytes()
        fixture_hash = hashlib.sha256(dependency).hexdigest()
        fixture_length = len(dependency)
        true_probe = _run_sandbox_probe(
            codex_bin,
            fixture,
            "true",
            checkout,
            executable_path=corrected_true,
        )
        helper_calls += 1
        if true_probe.successful:
            cat_probe = _run_sandbox_probe(
                codex_bin,
                fixture,
                "cat",
                checkout,
                executable_path=corrected_cat,
            )
            helper_calls += 1
            if cat_probe.successful:
                try:
                    write_local_model_catalog(codex_bin, fixture.model_catalog)
                except (OSError, RuntimeError, subprocess.SubprocessError, json.JSONDecodeError):
                    pass
                else:
                    governed_attempts.extend(
                        run_codex_once(codex_bin, fixture, governed_prompt()) for _ in range(2)
                    )

    classification = classify_sandbox_runtime_boundary(
        layout,
        true_probe,
        cat_probe,
        governed_attempts=tuple(governed_attempts),
    )
    return SandboxRuntimeBoundaryFacts(
        layout=layout,
        corrected_true_probe=true_probe,
        corrected_cat_probe=cat_probe,
        corrected_true_path_kind=true_path_kind,
        helper_calls=helper_calls,
        classification=classification,
        fixture_dependency_sha256=fixture_hash,
        fixture_dependency_byte_length=fixture_length,
        governed_attempts=tuple(governed_attempts),
    )
