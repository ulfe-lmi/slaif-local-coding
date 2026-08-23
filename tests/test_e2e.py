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
from dataclasses import asdict, replace
from pathlib import Path
from typing import Literal

import pytest

from slaif_local_coding.e2e import (
    BinaryStreamFacts,
    CacheInventory,
    CacheInventoryEntry,
    CommandDiagnostics,
    DependencyObservationFacts,
    GovernedFixturePaths,
    MetricDelta,
    SandboxPreflightFacts,
    SanitizedCodexRun,
    _binary_stream_facts,
    _classify_dependency_cache_outcome,
    _classify_diagnostic_text,
    _classify_sandbox_diagnostic_subclass,
    _final_agent_message_has_ack,
    _normalized_diagnostic_class,
    _reconcile_dependency_cache,
    _sentinel_failure_reason,
    build_sandbox_preflight_argv,
    classify_sandbox_boundary,
    constitution_metric_snapshot,
    governed_prompt,
    metric_value,
    parse_codex_command_events,
    parse_codex_events,
    parse_command_diagnostics_events,
    parse_dependency_observation_events,
    read_persistent_cache_inventory,
    run_codex_once,
    run_command_failure_diagnostic,
    run_sandbox_preflight,
    verify_direct_dependency_read,
    write_governed_fixture,
)


def _successful_sandbox_preflight(fixture: GovernedFixturePaths) -> SandboxPreflightFacts:
    dependency = (fixture.repository / "GOVERNANCE-DEPENDENCY.md").read_bytes()
    dependency_hash = hashlib.sha256(dependency).hexdigest()
    empty_hash = hashlib.sha256(b"").hexdigest()
    return SandboxPreflightFacts(
        cli_version="0.149.0",
        platform="linux",
        kernel_capabilities=("bwrap_present", "seccomp_probe_available"),
        sandbox_mode="workspace-write",
        permission_profile=":workspace",
        feature_labels=("direct_no_model", "workspace_write", "linux_bwrap_seccomp"),
        policy_resolution="resolved",
        working_directory_inside_repository=True,
        target_inside_repository=True,
        target_regular_file=True,
        target_symlink=False,
        target_byte_length=len(dependency),
        target_sha256=dependency_hash,
        observed_byte_length=len(dependency),
        observed_sha256=dependency_hash,
        byte_identical=True,
        process_exit_status=0,
        process_status="success",
        timed_out=False,
        stdout=BinaryStreamFacts(len(dependency), dependency_hash, "success", "other"),
        stderr=BinaryStreamFacts(0, empty_hash, "unavailable"),
        boundary_classification="workspace_sandbox_available",
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


def test_dependency_observation_parses_one_successful_bounded_read() -> None:
    canned = "\n".join(
        [
            '{"type":"item.started","item":{"id":"read","type":"command_execution",'
            '"command":"cat GOVERNANCE-DEPENDENCY.md"}}',
            '{"type":"item.completed","item":{"id":"read","type":"command_execution",'
            '"status":"completed","exit_code":0,"aggregated_output":"raw dependency"}}',
            '{"type":"item.completed","item":{"id":"other","type":"command_execution",'
            '"command":["cat","README.md"],"status":"completed","exit_code":0}}',
        ]
    )
    facts = parse_dependency_observation_events(io.StringIO(canned))
    assert facts.intended_dependency_reads == 1
    assert facts.started_commands == 1
    assert facts.completed_commands == 1
    assert facts.failed_commands == 0
    assert facts.successful_dependency_reads == 1
    assert facts.lifecycle == "success"
    assert facts.output_sha256 == hashlib.sha256(b"raw dependency").hexdigest()
    assert facts.output_byte_length == len(b"raw dependency")
    assert facts.rstrip_output_sha256 == hashlib.sha256(b"raw dependency").hexdigest()


def test_dependency_observation_accepts_string_zero_exit_and_started_identity() -> None:
    canned = "\n".join(
        [
            '{"type":"item.started","item":{"id":"read","type":"command_execution",'
            '"command":"cat GOVERNANCE-DEPENDENCY.md"}}',
            '{"type":"item.completed","item":{"id":"read","type":"command_execution",'
            '"status":"completed","exit_code":"0","aggregate_output":"raw"}}',
        ]
    )
    facts = parse_dependency_observation_events(io.StringIO(canned))
    assert facts.lifecycle == "success"
    assert facts.output_sha256 == hashlib.sha256(b"raw").hexdigest()


def test_dependency_observation_rejects_duplicate_failed_or_wrapper_reads() -> None:
    failed = "\n".join(
        [
            '{"type":"item.started","item":{"id":"failed","type":"command_execution",'
            '"command":"cat GOVERNANCE-DEPENDENCY.md"}}',
            '{"type":"item.completed","item":{"id":"failed","type":"command_execution",'
            '"status":"failed","exit_code":1}}',
        ]
    )
    assert parse_dependency_observation_events(io.StringIO(failed)).lifecycle == "failed"


def test_dependency_observation_recognizes_quoted_shell_wrapper_failure() -> None:
    canned = "\n".join(
        [
            '{"type":"item.started","item":{"id":"wrapped","type":"command_execution",'
            '"command":"bash -lc \\"cat GOVERNANCE-DEPENDENCY.md\\""}}',
            '{"type":"item.completed","item":{"id":"wrapped","type":"command_execution",'
            '"status":"failed","exit_code":1,"aggregated_output":"ignored"}}',
        ]
    )
    facts = parse_dependency_observation_events(io.StringIO(canned))
    assert facts.intended_dependency_reads == 1
    assert facts.started_commands == 1
    assert facts.failed_commands == 1
    assert facts.lifecycle == "failed"
    duplicate = "\n".join(
        [
            '{"type":"item.started","item":{"id":"one","type":"command_execution",'
            '"command":"cat GOVERNANCE-DEPENDENCY.md"}}',
            '{"type":"item.started","item":{"id":"two","type":"command_execution",'
            '"command":["bash","-lc","cat GOVERNANCE-DEPENDENCY.md"]}}',
        ]
    )
    facts = parse_dependency_observation_events(io.StringIO(duplicate))
    assert facts.intended_dependency_reads == 2
    assert facts.lifecycle == "incomplete"


def test_sentinel_failure_is_gated_by_command_lifecycle() -> None:
    success = DependencyObservationFacts(
        intended_dependency_reads=1,
        started_commands=1,
        completed_commands=1,
        successful_dependency_reads=1,
        output_sha256="a" * 64,
        output_byte_length=1,
        rstrip_output_sha256="a" * 64,
    )
    failed = DependencyObservationFacts(
        intended_dependency_reads=1,
        started_commands=1,
        failed_commands=1,
    )
    incomplete = DependencyObservationFacts(intended_dependency_reads=2)
    assert (
        _sentinel_failure_reason(
            process_result="success",
            has_tool=True,
            sentinel_passed=False,
            observation=success,
        )
        == "sentinel_missing"
    )
    assert (
        _sentinel_failure_reason(
            process_result="success",
            has_tool=True,
            sentinel_passed=False,
            observation=failed,
        )
        == "command_failed"
    )
    assert (
        _sentinel_failure_reason(
            process_result="success",
            has_tool=True,
            sentinel_passed=False,
            observation=incomplete,
        )
        == "command_incomplete"
    )


def test_diagnostic_classes_and_stream_audit_do_not_retain_raw_text() -> None:
    assertions = [
        ("No such file or directory", "not_found"),
        ("Permission denied", "permission_denied"),
        ("blocked by sandbox policy", "sandbox_denied"),
        ("unexpected argument", "argv_unsupported"),
    ]
    for text, expected in assertions:
        assert _classify_diagnostic_text(text) == expected

    stdout = BinaryStreamFacts(11, hashlib.sha256(b"SECRET-TEXT").hexdigest(), "success")
    stderr = BinaryStreamFacts(0, hashlib.sha256(b"").hexdigest(), "unavailable")
    command = CommandDiagnostics(command_status="failed")
    assert (
        _normalized_diagnostic_class(
            exit_status=1,
            timed_out=False,
            stdout=stdout,
            stderr=stderr,
            command=command,
        )
        == "unknown_nonzero"
    )
    assert (
        _normalized_diagnostic_class(
            exit_status=0,
            timed_out=True,
            stdout=stdout,
            stderr=stderr,
            command=command,
        )
        == "timeout"
    )

    facts = _binary_stream_facts(io.BytesIO(b"SECRET-FIRST-LINE\nSECOND\n"))
    assert facts.byte_length == 25
    assert facts.sha256 == hashlib.sha256(b"SECRET-FIRST-LINE\nSECOND\n").hexdigest()
    assert facts.first_line_class == "success"
    assert "SECRET-FIRST-LINE" not in asdict(facts).values()


def test_warning_preambles_reveal_first_meaningful_bounded_diagnostic() -> None:
    cases = [
        (b"Warning: startup\nWARN: compatibility\nbwrap: sandbox denied\nRAW", "sandbox_denied"),
        (b"warning: startup\nPermission denied\nRAW", "permission_denied"),
        (b"Warning: startup\nNo such file or directory\nRAW", "not_found"),
        (b"warn: startup\nunexpected argument\nRAW", "argv_unsupported"),
        (b"Warning: startup\ninvalid request schema\nRAW", "schema_invalid"),
    ]
    for payload, expected in cases:
        facts = _binary_stream_facts(io.BytesIO(payload))
        assert facts.first_line_class == expected
        assert facts.diagnostic_lines_scanned <= 8
        assert facts.diagnostic_line_max_bytes <= 4_096
        assert "RAW" not in str(asdict(facts))

    warning_only = _binary_stream_facts(io.BytesIO(b"Warning: one\n\nWARN: two\n"))
    assert warning_only.first_line_class == "unavailable"
    assert warning_only.first_line_subclass == "empty"


def test_diagnostic_line_scan_has_fixed_count_and_length_bounds() -> None:
    import slaif_local_coding.e2e as e2e_module

    after_bound = b"\n".join(
        [b"Warning: preamble"] * e2e_module.SANDBOX_DIAGNOSTIC_MAX_LINES + [b"Permission denied"]
    )
    bounded = _binary_stream_facts(io.BytesIO(after_bound))
    assert bounded.diagnostic_lines_scanned == e2e_module.SANDBOX_DIAGNOSTIC_MAX_LINES
    assert bounded.first_line_class == "unavailable"
    assert bounded.first_line_subclass == "empty"

    long_warning = b"Warning: " + b"x" * (e2e_module.SANDBOX_DIAGNOSTIC_MAX_LINE_BYTES + 100)
    facts = _binary_stream_facts(io.BytesIO(long_warning + b"\nPermission denied\n"))
    assert facts.first_line_class == "permission_denied"
    assert facts.diagnostic_line_max_bytes == e2e_module.SANDBOX_DIAGNOSTIC_MAX_LINE_BYTES
    assert facts.diagnostic_line_truncated is True
    assert facts.byte_length == len(long_warning) + len(b"\nPermission denied\n")


def test_sandbox_preflight_command_is_explicit_and_in_root(tmp_path: Path) -> None:
    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    target = fixture.repository / "GOVERNANCE-DEPENDENCY.md"
    command = build_sandbox_preflight_argv("codex", fixture.repository, target)
    assert command[:4] == (
        "codex",
        "sandbox",
        "--permission-profile",
        ":workspace",
    )
    assert command[4] == "--cd"
    assert command[6:] == ("--", "/bin/cat", "GOVERNANCE-DEPENDENCY.md")
    assert "linux" not in command
    assert all("danger" not in part for part in command)
    with pytest.raises(ValueError, match="inside repository"):
        build_sandbox_preflight_argv("codex", fixture.repository, tmp_path / "outside")


def test_sandbox_preflight_sanitizes_bootstrap_diagnostic_and_bounds_output(
    tmp_path: Path,
) -> None:
    fixture = write_governed_fixture(tmp_path / "fixture", base_url="", api_key_env="UNUSED")
    fake_codex = tmp_path / "fake-codex.py"
    fake_codex.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "if sys.argv[1:] == ['--version']:\n"
        "    print('codex-cli 0.149.0')\n"
        "else:\n"
        "    sys.stderr.write('bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n')\n"
        "    sys.stderr.write('RAW-PRIVATE-DIAGNOSTIC\\n')\n"
        "    raise SystemExit(1)\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o700)

    facts = run_sandbox_preflight(fake_codex, fixture)

    assert facts.cli_version == "0.149.0"
    assert facts.sandbox_mode == "workspace-write"
    assert facts.permission_profile == ":workspace"
    assert facts.policy_resolution == "resolved"
    assert facts.target_inside_repository is True
    assert facts.process_exit_status == 1
    assert facts.stderr.first_line_class == "sandbox_denied"
    assert facts.stderr.first_line_subclass == "bwrap_loopback_bootstrap"
    assert facts.boundary_classification == "host_sandbox_bootstrap_unsupported"
    assert facts.raw_output_retained is False
    assert "RAW-PRIVATE-DIAGNOSTIC" not in str(asdict(facts))


def test_sandbox_preflight_rejecting_builtin_profile_is_config_error(tmp_path: Path) -> None:
    fixture = write_governed_fixture(tmp_path / "fixture", base_url="", api_key_env="UNUSED")
    fake_codex = tmp_path / "fake-codex-profile-rejection.py"
    fake_codex.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "if sys.argv[1:] == ['--version']:\n"
        "    print('codex-cli 0.149.0')\n"
        "else:\n"
        "    sys.stderr.write('Warning: startup preamble\\n')\n"
        "    sys.stderr.write('error: permission profile :workspace is not valid\\n')\n"
        "    sys.stderr.write('RAW-PROFILE-DIAGNOSTIC\\n')\n"
        "    raise SystemExit(2)\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o700)

    facts = run_sandbox_preflight(fake_codex, fixture)

    assert facts.permission_profile == ":workspace"
    assert facts.policy_resolution == "unresolved"
    assert facts.stderr.first_line_class == "argv_unsupported"
    assert facts.stderr.first_line_subclass == "configuration"
    assert facts.boundary_classification == "invocation_config_precedence_error"
    assert "RAW-PROFILE-DIAGNOSTIC" not in str(asdict(facts))


def test_sandbox_preflight_timeout_is_fixed_and_non_successful(tmp_path: Path) -> None:
    fixture = write_governed_fixture(tmp_path / "fixture", base_url="", api_key_env="UNUSED")
    fake_codex = tmp_path / "fake-codex-timeout.py"
    fake_codex.write_text(
        "#!/usr/bin/env python3\n"
        "import sys, time\n"
        "if sys.argv[1:] == ['--version']:\n"
        "    print('codex-cli 0.149.0')\n"
        "else:\n"
        "    time.sleep(2)\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o700)

    facts = run_sandbox_preflight(fake_codex, fixture, timeout_seconds=0.01)

    assert facts.timed_out is True
    assert facts.successful is False
    assert facts.boundary_classification == "unresolved_with_fixed_evidence"


def test_sandbox_preflight_rejects_oversized_output_without_retaining_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import slaif_local_coding.e2e as e2e_module

    fixture = write_governed_fixture(tmp_path / "fixture", base_url="", api_key_env="UNUSED")
    fake_codex = tmp_path / "fake-codex-large-output.py"
    fake_codex.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "if sys.argv[1:] == ['--version']:\n"
        "    print('codex-cli 0.149.0')\n"
        "else:\n"
        "    sys.stderr.write('x' * 32)\n"
        "    raise SystemExit(1)\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o700)
    monkeypatch.setattr(e2e_module, "SANDBOX_PREFLIGHT_MAX_OUTPUT_BYTES", 8)

    facts = run_sandbox_preflight(fake_codex, fixture)

    assert facts.process_status == "unknown"
    assert facts.boundary_classification == "unresolved_with_fixed_evidence"
    assert facts.raw_output_retained is False


def test_sandbox_boundary_classification_is_deterministic(tmp_path: Path) -> None:
    fixture = write_governed_fixture(tmp_path / "fixture", base_url="", api_key_env="UNUSED")
    available = _successful_sandbox_preflight(fixture)
    failed = replace(
        available,
        process_exit_status=1,
        process_status="failed",
        byte_identical=False,
        boundary_classification="host_sandbox_bootstrap_unsupported",
    )
    command_success = DependencyObservationFacts(
        intended_dependency_reads=1,
        started_commands=1,
        completed_commands=1,
        successful_dependency_reads=1,
        output_sha256="a" * 64,
        output_byte_length=1,
    )
    cases = [
        (failed, None, "host_sandbox_bootstrap_unsupported"),
        (
            replace(
                available,
                target_inside_repository=False,
                boundary_classification="workspace_root_resolution_mismatch",
            ),
            None,
            "workspace_root_resolution_mismatch",
        ),
        (
            available,
            SanitizedCodexRun(
                exit_status=0,
                timed_out=False,
                duration_seconds=0,
                event_bytes=1,
                event_type_counts={},
                call_item_type_counts={},
                tool_names=(),
                tool_calls=0,
                sentinel_passed=False,
                failure_reason="unknown",
                sandbox_mode="unknown",
            ),
            "invocation_config_precedence_error",
        ),
        (
            available,
            SanitizedCodexRun(
                exit_status=0,
                timed_out=False,
                duration_seconds=0,
                event_bytes=1,
                event_type_counts={},
                call_item_type_counts={},
                tool_names=("command_execution",),
                tool_calls=1,
                sentinel_passed=False,
                failure_reason="command_incomplete",
                command_diagnostics=CommandDiagnostics(command_status="unknown"),
            ),
            "command_event_schema_mismatch",
        ),
        (
            available,
            SanitizedCodexRun(
                exit_status=0,
                timed_out=False,
                duration_seconds=0,
                event_bytes=1,
                event_type_counts={},
                call_item_type_counts={},
                tool_names=("command_execution",),
                tool_calls=1,
                sentinel_passed=True,
                failure_reason="success",
                dependency_observation=command_success,
                command_diagnostics=CommandDiagnostics(
                    command_status="success", command_path_inside_repository=True
                ),
            ),
            "workspace_sandbox_available",
        ),
        (
            available,
            SanitizedCodexRun(
                exit_status=0,
                timed_out=False,
                duration_seconds=0,
                event_bytes=1,
                event_type_counts={},
                call_item_type_counts={},
                tool_names=(),
                tool_calls=0,
                sentinel_passed=False,
                failure_reason="command_failed",
            ),
            "unresolved_with_fixed_evidence",
        ),
    ]
    for preflight, nested, expected in cases:
        assert classify_sandbox_boundary(preflight, nested) == expected


def test_sandbox_diagnostic_subclasses_are_fixed() -> None:
    assert (
        _classify_sandbox_diagnostic_subclass(
            "bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\nraw"
        )
        == "bwrap_loopback_bootstrap"
    )
    assert _classify_sandbox_diagnostic_subclass("unexpected argument") == "argument"
    assert _classify_sandbox_diagnostic_subclass("") == "empty"


def test_direct_dependency_read_control_is_private_and_byte_accurate(tmp_path: Path) -> None:
    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    dependency = fixture.repository / "GOVERNANCE-DEPENDENCY.md"
    control = verify_direct_dependency_read(fixture)
    expected = dependency.read_bytes()
    assert control.exists is True
    assert control.regular_file is True
    assert control.symlink is False
    assert control.private_mode is True
    assert control.byte_length == len(expected)
    assert control.sha256 == hashlib.sha256(expected).hexdigest()
    assert control.subprocess_exit_status == 0
    assert control.subprocess_byte_identical is True

    dependency.chmod(0o644)
    assert verify_direct_dependency_read(fixture).private_mode is False

    dependency.unlink()
    dependency.symlink_to(fixture.repository / "AGENTS.md")
    symlink_control = verify_direct_dependency_read(fixture)
    assert symlink_control.exists is True
    assert symlink_control.regular_file is False
    assert symlink_control.symlink is True
    assert symlink_control.byte_length is None


def test_command_event_diagnostic_hashes_class_without_retaining_output(
    tmp_path: Path,
) -> None:
    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    canned = "\n".join(
        [
            '{"type":"item.started","item":{"id":"read","type":"command_execution",'
            '"command":"cat GOVERNANCE-DEPENDENCY.md"}}',
            '{"type":"item.completed","item":{"id":"read","type":"command_execution",'
            '"status":"failed","exit_code":1,"command":["cat","GOVERNANCE-DEPENDENCY.md"],'
            '"aggregated_output":"Permission denied\\nRAW-DIAGNOSTIC"}}',
        ]
    )
    facts = parse_command_diagnostics_events(io.StringIO(canned), fixture.repository)
    assert facts.requested_argv_shape == "single_string"
    assert facts.actual_argv_shape == "argv_list"
    assert facts.command_status == "failed"
    assert facts.command_exit_code == 1
    assert facts.command_output_class == "permission_denied"
    assert facts.command_output_byte_length == len("Permission denied\nRAW-DIAGNOSTIC")
    assert (
        facts.command_output_sha256
        == hashlib.sha256(b"Permission denied\nRAW-DIAGNOSTIC").hexdigest()
    )
    assert facts.command_path_inside_repository is True
    assert "RAW-DIAGNOSTIC" not in str(asdict(facts))


def test_command_event_diagnostic_normalizes_string_exit_code(tmp_path: Path) -> None:
    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    canned = "\n".join(
        [
            '{"type":"item.started","item":{"id":"read","type":"command_execution",'
            '"command":"cat GOVERNANCE-DEPENDENCY.md"}}',
            '{"type":"item.completed","item":{"id":"read","type":"command_execution",'
            '"status":"completed","exit_code":"1","command":["cat",'
            '"GOVERNANCE-DEPENDENCY.md"]}}',
        ]
    )
    facts = parse_command_diagnostics_events(io.StringIO(canned), fixture.repository)
    assert facts.command_exit_code == 1
    assert facts.command_status == "failed"
    assert facts.failure_class == "unknown_nonzero"


def test_failed_codex_process_returns_sanitized_unavailable_diagnostics(tmp_path: Path) -> None:
    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    result = run_codex_once(tmp_path / "missing-codex", fixture, governed_prompt())
    assert result.failure_reason == "process_boundary_error"
    assert result.dependency_observation.lifecycle == "incomplete"
    assert result.command_diagnostics.failure_class == "unavailable"
    assert result.command_diagnostics.process_status == "unknown"


def test_failure_diagnosis_uses_one_alternative_then_stops(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import slaif_local_coding.e2e as e2e_module

    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    dependency_bytes = (fixture.repository / "GOVERNANCE-DEPENDENCY.md").read_bytes()
    prompts: list[str] = []

    def fake_catalog(_codex_bin: object, _destination: object) -> None:
        return None

    def fake_run(
        _codex_bin: object, called_fixture: GovernedFixturePaths, prompt: str
    ) -> SanitizedCodexRun:
        assert called_fixture is fixture
        prompts.append(prompt)
        if len(prompts) == 1:
            return SanitizedCodexRun(
                exit_status=0,
                timed_out=False,
                duration_seconds=0.0,
                event_bytes=1,
                event_type_counts={},
                call_item_type_counts={"command_execution": 1},
                tool_names=("command_execution",),
                tool_calls=1,
                sentinel_passed=False,
                failure_reason="command_failed",
                dependency_observation=DependencyObservationFacts(
                    intended_dependency_reads=1,
                    started_commands=1,
                    failed_commands=1,
                ),
                command_diagnostics=CommandDiagnostics(
                    failure_class="not_found",
                    process_exit_code=0,
                    process_status="success",
                    command_exit_code=1,
                    command_status="failed",
                ),
            )
        observed_hash = hashlib.sha256(dependency_bytes).hexdigest()
        return SanitizedCodexRun(
            exit_status=0,
            timed_out=False,
            duration_seconds=0.0,
            event_bytes=1,
            event_type_counts={},
            call_item_type_counts={"command_execution": 1},
            tool_names=("command_execution",),
            tool_calls=1,
            sentinel_passed=True,
            failure_reason="sentinel_missing",
            dependency_observation=DependencyObservationFacts(
                intended_dependency_reads=1,
                started_commands=1,
                completed_commands=1,
                successful_dependency_reads=1,
                output_sha256=observed_hash,
                output_byte_length=len(dependency_bytes),
                rstrip_output_sha256=hashlib.sha256(dependency_bytes.rstrip()).hexdigest(),
            ),
            command_diagnostics=CommandDiagnostics(
                failure_class="success",
                process_exit_code=0,
                process_status="success",
                command_exit_code=0,
                command_status="success",
            ),
        )

    monkeypatch.setattr(e2e_module, "write_local_model_catalog", fake_catalog)
    monkeypatch.setattr(e2e_module, "run_codex_once", fake_run)
    monkeypatch.setattr(e2e_module, "write_governed_fixture", lambda *_: fixture)
    monkeypatch.setattr(
        e2e_module,
        "run_sandbox_preflight",
        lambda *_args, **_kwargs: _successful_sandbox_preflight(fixture),
    )
    facts = run_command_failure_diagnostic("unused")
    assert len(facts.attempts) == 2
    assert [attempt.read_form for attempt in facts.attempts] == [
        "relative_cat",
        "absolute_bin_cat",
    ]
    assert "command cat GOVERNANCE-DEPENDENCY.md" in prompts[0]
    assert "command /bin/cat GOVERNANCE-DEPENDENCY.md" in prompts[1]
    assert all(attempt.direct_read.subprocess_exit_status == 0 for attempt in facts.attempts)
    assert facts.attempts[0].run.command_diagnostics.failure_class == "not_found"
    assert facts.dependency_provenance == "equal"
    # The helper's own lifecycle gate still prevents governance attribution here.
    assert facts.attempts[-1].run.failure_reason == "sentinel_missing"


def test_failure_diagnosis_stops_after_first_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import slaif_local_coding.e2e as e2e_module

    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    prompts: list[str] = []

    def fake_catalog(_codex_bin: object, _destination: object) -> None:
        return None

    def fake_run(
        _codex_bin: object, _called_fixture: GovernedFixturePaths, prompt: str
    ) -> SanitizedCodexRun:
        prompts.append(prompt)
        return SanitizedCodexRun(
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
            dependency_observation=DependencyObservationFacts(
                intended_dependency_reads=1,
                started_commands=1,
                completed_commands=1,
                successful_dependency_reads=1,
                output_sha256="a" * 64,
                output_byte_length=1,
                rstrip_output_sha256="a" * 64,
            ),
            command_diagnostics=CommandDiagnostics(failure_class="success"),
        )

    monkeypatch.setattr(e2e_module, "write_local_model_catalog", fake_catalog)
    monkeypatch.setattr(e2e_module, "run_codex_once", fake_run)
    monkeypatch.setattr(e2e_module, "write_governed_fixture", lambda *_: fixture)
    monkeypatch.setattr(
        e2e_module,
        "run_sandbox_preflight",
        lambda *_args, **_kwargs: _successful_sandbox_preflight(fixture),
    )
    facts = run_command_failure_diagnostic("unused")
    assert len(facts.attempts) == 1
    assert facts.attempts[0].read_form == "relative_cat"
    assert len(prompts) == 1


def test_failure_diagnosis_never_runs_model_after_failed_preflight(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import slaif_local_coding.e2e as e2e_module

    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    failed = replace(
        _successful_sandbox_preflight(fixture),
        process_exit_status=2,
        process_status="failed",
        byte_identical=False,
        boundary_classification="invocation_config_precedence_error",
    )
    monkeypatch.setattr(e2e_module, "write_governed_fixture", lambda *_: fixture)
    monkeypatch.setattr(e2e_module, "run_sandbox_preflight", lambda *_args, **_kwargs: failed)
    monkeypatch.setattr(
        e2e_module,
        "write_local_model_catalog",
        lambda *_args, **_kwargs: pytest.fail("model catalog must remain gated"),
    )
    monkeypatch.setattr(
        e2e_module,
        "run_codex_once",
        lambda *_args, **_kwargs: pytest.fail("governed model run must remain gated"),
    )

    facts = run_command_failure_diagnostic("unused")

    assert facts.attempts == ()
    assert facts.boundary_classification == "invocation_config_precedence_error"


def test_constitution_metric_snapshot_exposes_fixed_counter_deltas() -> None:
    before = constitution_metric_snapshot("")
    acquisitions = "slaif_constitution_dependency_acquisitions_total"
    canned = "\n".join(
        [
            "# HELP synthetic sanitized\n# TYPE synthetic counter",
            'slaif_constitution_roots_total{evidence_type="project_instructions",route="route"} 2',
            'slaif_constitution_dependency_observations_total{route="route",state="observed"} 9',
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
    assert deltas["dependency_observations"].delta == 9
    assert deltas["dependency_invalid"].after == 0.5
    assert deltas["injected_requests"].delta == 7
    assert deltas["compiler_calls"].delta == 4
    assert deltas["working_set_included"].delta == 6
    assert set(deltas) == {
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
        "stored_source_sha256",
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
            stored_source_sha256=f"{source_prefix}{'0' * 52}",
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
        observed_dependency_sha256=f"{matching}{'0' * 52}",
    )
    assert hit_match is False and not different_source and errors == ()

    known_hit, _, _, _ = _reconcile_dependency_cache(
        inventory_before=same_after,
        inventory_after=same_after,
        metric_deltas=metrics,
        fixture_hashes_stable=True,
        observed_dependency_sha256=f"{matching}{'0' * 52}",
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
        observed_dependency_sha256=f"{matching}{'0' * 52}",
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
                stored_source_sha256=f"{prefix}{'0' * 52}",
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
        observed_dependency_sha256=f"{'a' * 12}{'0' * 52}",
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
            stored_source_sha256=f"{source_prefix}{'0' * 52}",
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
        observed_dependency_sha256=f"{'a' * 12}{'0' * 52}",
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
            dependency_observation=DependencyObservationFacts(
                intended_dependency_reads=1,
                started_commands=1,
                completed_commands=1,
                successful_dependency_reads=1,
                output_sha256=hashlib.sha256(dependency).hexdigest(),
                output_byte_length=len(dependency),
                rstrip_output_sha256=hashlib.sha256(dependency.rstrip()).hexdigest(),
            ),
        )

    metrics_samples = [
        "",
        "\n".join(
            [
                'slaif_constitution_roots_total{evidence_type="project_instructions",'
                'route="qwen38-vision-codex"} 1',
                "slaif_constitution_dependency_observations_total"
                '{route="qwen38-vision-codex",state="observed"} 1',
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
    assert facts.dependency_command_state == "success"
    assert facts.dependency_provenance == "equal"
    assert facts.fixture_hashes_stable_during_run
    assert facts.metric_deltas["dependency_cache_misses"].delta == 1
    assert facts.metric_deltas["dependency_observations"].delta == 1
    assert facts.metric_deltas["working_set_included"].delta == 1
    assert len(facts.inventory_before.entries) == 0
    assert len(facts.inventory_after.entries) == 2
    dependency_hash = hashlib.sha256(
        (fixture.repository / "GOVERNANCE-DEPENDENCY.md").read_bytes()
    ).hexdigest()
    assert facts.fixture_dependency_sha256 == dependency_hash
    assert facts.fixture_dependency_byte_length == len(
        (fixture.repository / "GOVERNANCE-DEPENDENCY.md").read_bytes()
    )
    assert facts.observed_dependency_sha256 == dependency_hash
    assert facts.cache_miss_stored_source_hash_match is True
    assert facts.consistency_errors == ()
    assert facts.classification == "unresolved_with_fixed_evidence"
    public = json.dumps(asdict(facts), sort_keys=True)
    assert fixture.sentinel_token not in public


def test_diagnostic_classifies_terminal_whitespace_boundary_normalization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import slaif_local_coding.e2e as e2e_module

    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    observed_bytes = (fixture.repository / "GOVERNANCE-DEPENDENCY.md").read_bytes().rstrip()

    def fake_catalog(_codex_bin: object, _destination: object) -> None:
        return None

    def fake_run(
        _codex_bin: object, called_fixture: GovernedFixturePaths, _prompt: str
    ) -> SanitizedCodexRun:
        assert called_fixture is fixture
        _write_cache_entry(
            persistent_root,
            logical_path="GOVERNANCE-DEPENDENCY.md",
            source=observed_bytes,
            created_at=time.time(),
        )
        return SanitizedCodexRun(
            exit_status=0,
            timed_out=False,
            duration_seconds=0.0,
            event_bytes=1,
            event_type_counts={},
            call_item_type_counts={"command_execution": 1},
            tool_names=("command_execution",),
            tool_calls=1,
            sentinel_passed=False,
            failure_reason="sentinel_missing",
            command_event_counts={"started": 1, "completed": 1},
            dependency_observation=DependencyObservationFacts(
                intended_dependency_reads=1,
                started_commands=1,
                completed_commands=1,
                successful_dependency_reads=1,
                output_sha256=hashlib.sha256(observed_bytes).hexdigest(),
                output_byte_length=len(observed_bytes),
                rstrip_output_sha256=hashlib.sha256(observed_bytes).hexdigest(),
            ),
        )

    monkeypatch.setattr(e2e_module, "write_local_model_catalog", fake_catalog)
    monkeypatch.setattr(e2e_module, "run_codex_once", fake_run)
    monkeypatch.setattr(e2e_module, "write_governed_fixture", lambda *_args, **_kwargs: fixture)
    persistent_root = tmp_path / "cache"
    persistent_root.mkdir(mode=0o700)
    samples = [
        "",
        "slaif_constitution_dependency_acquisitions_total"
        '{route="qwen38-vision-codex",outcome="cache_miss"} 1\n',
    ]
    sample_index = 0

    def sample_metrics() -> str:
        nonlocal sample_index
        result = samples[sample_index]
        sample_index += 1
        return result

    facts = e2e_module.run_dependency_cache_diagnostic(
        "unused", metrics_sampler=sample_metrics, persistent_cache_root=persistent_root
    )
    assert facts.repository_observed_hash_equal is False
    assert facts.repository_observed_length_equal is False
    assert facts.repository_differs_only_by_terminal_whitespace is True
    assert facts.dependency_provenance == "tool_boundary_normalization"
    assert facts.dependency_command_state == "success"
    assert facts.cache_miss_stored_source_hash_match is True
    assert facts.cache_miss_stored_source_hash_match is not False
    assert facts.consistency_errors == ()
    assert facts.classification == "unresolved_with_fixed_evidence"


def test_diagnostic_classifies_non_whitespace_observation_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import slaif_local_coding.e2e as e2e_module

    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    repository_dependency = (fixture.repository / "GOVERNANCE-DEPENDENCY.md").read_bytes()
    observed_bytes = repository_dependency + b"NON-WHITESPACE-BOUNDARY-DELTA"

    def fake_catalog(_codex_bin: object, _destination: object) -> None:
        return None

    def fake_run(
        _codex_bin: object, called_fixture: GovernedFixturePaths, _prompt: str
    ) -> SanitizedCodexRun:
        assert called_fixture is fixture
        _write_cache_entry(
            persistent_root,
            logical_path="GOVERNANCE-DEPENDENCY.md",
            source=observed_bytes,
            created_at=time.time(),
        )
        return SanitizedCodexRun(
            exit_status=0,
            timed_out=False,
            duration_seconds=0.0,
            event_bytes=1,
            event_type_counts={},
            call_item_type_counts={"command_execution": 1},
            tool_names=("command_execution",),
            tool_calls=1,
            sentinel_passed=False,
            failure_reason="sentinel_missing",
            command_event_counts={"started": 1, "completed": 1},
            dependency_observation=DependencyObservationFacts(
                intended_dependency_reads=1,
                started_commands=1,
                completed_commands=1,
                successful_dependency_reads=1,
                output_sha256=hashlib.sha256(observed_bytes).hexdigest(),
                output_byte_length=len(observed_bytes),
                rstrip_output_sha256=hashlib.sha256(observed_bytes.rstrip()).hexdigest(),
            ),
        )

    monkeypatch.setattr(e2e_module, "write_local_model_catalog", fake_catalog)
    monkeypatch.setattr(e2e_module, "run_codex_once", fake_run)
    monkeypatch.setattr(e2e_module, "write_governed_fixture", lambda *_args, **_kwargs: fixture)
    persistent_root = tmp_path / "cache"
    persistent_root.mkdir(mode=0o700)
    samples = [
        "",
        "slaif_constitution_dependency_acquisitions_total"
        '{route="qwen38-vision-codex",outcome="cache_miss"} 1\n',
    ]
    sample_index = 0

    def sample_metrics() -> str:
        nonlocal sample_index
        result = samples[sample_index]
        sample_index += 1
        return result

    facts = e2e_module.run_dependency_cache_diagnostic(
        "unused", metrics_sampler=sample_metrics, persistent_cache_root=persistent_root
    )
    assert facts.dependency_provenance == "observation_mismatch"
    assert facts.repository_differs_only_by_terminal_whitespace is False
    assert facts.cache_miss_stored_source_hash_match is True
    assert facts.classification == "unresolved_with_fixed_evidence"
