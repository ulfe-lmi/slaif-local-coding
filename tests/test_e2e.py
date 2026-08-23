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

from tests.helpers.e2e_support import (
    BinaryStreamFacts,
    CacheInventory,
    CacheInventoryEntry,
    CommandDiagnostics,
    DependencyObservationFacts,
    GovernedFixturePaths,
    MetricDelta,
    SanitizedCodexRun,
    _binary_stream_facts,
    _classify_dependency_cache_outcome,
    _classify_diagnostic_text,
    _classify_sandbox_diagnostic_subclass,
    _final_agent_message_has_ack,
    _normalized_diagnostic_class,
    _reconcile_dependency_cache,
    _sentinel_failure_reason,
    constitution_metric_snapshot,
    governed_prompt,
    metric_value,
    parse_codex_command_events,
    parse_codex_events,
    parse_command_diagnostics_events,
    parse_dependency_observation_events,
    parse_event_parser_counts,
    read_persistent_cache_inventory,
    run_codex_once,
    run_ordinary_command_pair,
    write_governed_fixture,
)
from tests.helpers.sandbox_runtime import (
    EffectiveCodexConfigFacts,
    InstalledDirectoryFacts,
    InstalledPathFacts,
    NativeWorkspaceDecisionFacts,
    SandboxInstallationLayoutFacts,
    SandboxProbeFacts,
    SanitizedExecutableFacts,
    _build_sandbox_probe_argv,
    _effective_codex_config_facts,
    classify_sandbox_runtime_boundary,
    run_native_workspace_decision_tree,
    run_native_workspace_preflight,
    run_sandbox_runtime_boundary_diagnostic,
)


def _differential_probe(
    command: Literal["true", "cat"],
    *,
    success: bool,
    failure_class: Literal["not_found", "sandbox_denied"] = "not_found",
) -> SandboxProbeFacts:
    empty_hash = hashlib.sha256(b"").hexdigest()
    executable = SanitizedExecutableFacts(
        command=command,
        exists=True,
        regular_file=True,
        executable=True,
        symlink=False,
        resolved_basename_class="expected",
    )
    return SandboxProbeFacts(
        command=command,
        root_class="system_tmp",
        executable=executable,
        working_directory_inside_repository=True,
        target_inside_repository=True if command == "cat" else None,
        target_regular_file=True if command == "cat" else None,
        target_symlink=False if command == "cat" else None,
        target_private_mode=True if command == "cat" else None,
        target_byte_length=1 if command == "cat" else None,
        target_sha256="a" * 64 if command == "cat" else None,
        observed_byte_length=1 if success and command == "cat" else 0,
        observed_sha256="a" * 64 if success and command == "cat" else empty_hash,
        expected_output_byte_length=1 if command == "cat" else 0,
        expected_output_sha256="a" * 64 if command == "cat" else empty_hash,
        byte_identical=True if success else False,
        process_exit_status=0 if success else 1,
        process_status="success" if success else "failed",
        timed_out=False,
        stdout=BinaryStreamFacts(0, empty_hash, "unavailable"),
        stderr=BinaryStreamFacts(
            0 if success else 1,
            empty_hash,
            "unavailable" if success else failure_class,
            "empty" if success else "not_found",
        ),
        policy_resolution="resolved",
    )


def _fake_ordinary_codex(path: Path, *, fail_danger: bool = False) -> Path:
    failure = (
        "\nif mode == 'danger-full-access':\n"
        "    sys.stderr.write('startup failure\\n')\n"
        "    raise SystemExit(1)\n"
        if fail_danger
        else ""
    )
    started = (
        " {'type':'item.started','item':{"
        "'id':'cmd','type':'command_execution','command':command}},\n"
    )
    completed = (
        " {'type':'item.completed','item':{"
        "'id':'cmd','type':'command_execution','command':command,"
        "'status':'completed','exit_code':0}},\n"
    )
    message = (
        " {'type':'item.completed','item':{"
        "'type':'agent_message','text':'ORDINARY-COMMAND-ACK'}},\n"
    )
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import json\nimport sys\n"
        "if '--version' in sys.argv:\n    print('codex-cli 0.149.0')\n    raise SystemExit(0)\n"
        "mode = sys.argv[sys.argv.index('--sandbox') + 1]\n"
        + failure
        + "command = '/usr/bin/true'\n"
        + "events = [\n"
        + started
        + completed
        + message
        + "]\n"
        + "for event in events: print(json.dumps(event))\n",
        encoding="utf-8",
    )
    path.chmod(0o700)
    return path


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


def test_subprocess_environment_preserves_host_home_tmpdir_and_named_credential(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tests.helpers.e2e_support as e2e_module

    host_home = tmp_path / "host-home"
    host_tmpdir = tmp_path / "host-tmpdir"
    monkeypatch.setenv("HOME", str(host_home))
    monkeypatch.setenv("TMPDIR", str(host_tmpdir))
    monkeypatch.setenv("QWEN3090_API_KEY", "unit-test-secret")
    monkeypatch.setenv("UNRELATED_SECRET", "must-not-cross-boundary")
    environment = e2e_module._sandbox_environment(tmp_path, "QWEN3090_API_KEY")

    assert environment["CODEX_HOME"] == str(tmp_path)
    assert environment["HOME"] == str(host_home)
    assert environment["TMPDIR"] == str(host_tmpdir)
    assert str(tmp_path.parent) not in {environment["HOME"], environment["TMPDIR"]}
    assert environment["QWEN3090_API_KEY"] == "unit-test-secret"
    assert "UNRELATED_SECRET" not in environment
    assert set(environment) <= {
        "PATH",
        "HOME",
        "TMPDIR",
        "LANG",
        "LC_ALL",
        "TERM",
        "CODEX_HOME",
        "QWEN3090_API_KEY",
    }
    with pytest.raises(ValueError, match="environment variable name"):
        e2e_module._sandbox_environment(tmp_path, "bad-name=value")


def test_subprocess_environment_omits_unset_tmpdir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tests.helpers.e2e_support as e2e_module

    monkeypatch.delenv("TMPDIR", raising=False)
    environment = e2e_module._sandbox_environment(tmp_path)

    assert environment["CODEX_HOME"] == str(tmp_path)
    assert "TMPDIR" not in environment


def test_effective_config_facts_are_allowlisted_and_hashed(tmp_path: Path) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    (codex_home / "config.toml").write_text(
        'profile = "oap-test"\nsandbox_mode = "workspace-write"\n'
        'approval_policy = "never"\nprovider_url = "https://private.invalid"\n',
        encoding="utf-8",
    )

    facts = _effective_codex_config_facts(codex_home)

    assert facts.config_present is True
    assert (
        facts.config_sha256 == hashlib.sha256((codex_home / "config.toml").read_bytes()).hexdigest()
    )
    assert facts.selected_profile == "oap-test"
    assert facts.sandbox_mode == "workspace-write"
    assert facts.approval_policy == "never"
    assert "private.invalid" not in str(asdict(facts))


def test_probe_facts_capture_profile_source_and_normalized_argv(
    tmp_path: Path,
) -> None:
    import tests.helpers.sandbox_runtime as e2e_module

    codex_bin = tmp_path / "codex"
    codex_bin.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    codex_bin.chmod(0o700)
    fixture = write_governed_fixture(tmp_path, "", "UNUSED")

    facts = e2e_module._run_sandbox_probe(
        codex_bin,
        fixture,
        "true",
        tmp_path,
        permission_profile=":danger-full-access",
        config_source="host_user",
    )

    assert facts.successful is True
    assert facts.permission_profile == ":danger-full-access"
    assert facts.semantic_mode == "danger-full-access-control"
    assert facts.config_source == "host_user"
    assert facts.environment_names == tuple(sorted(facts.environment_names))
    assert "<fixture>" in facts.normalized_argv
    assert str(codex_bin) not in facts.normalized_argv
    assert len(facts.argv_sha256) == 64


def test_model_catalog_subprocess_output_is_bounded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tests.helpers.e2e_support as e2e_module

    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    fake_codex = tmp_path / "fake-codex.py"
    fake_codex.write_text(
        "#!/usr/bin/env python3\nimport sys\nsys.stdout.write('x' * 32)\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o700)
    monkeypatch.setattr(e2e_module, "CODEX_MAX_DIAGNOSTIC_BYTES", 8)

    with pytest.raises(RuntimeError, match="output_exceeded"):
        e2e_module.write_local_model_catalog(fake_codex, fixture.model_catalog)


def test_runner_prompts_never_contain_delegated_sentinel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tests.helpers.e2e_support as e2e_module

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


def test_ordinary_command_parser_records_exactness_origin_and_rejections(
    tmp_path: Path,
) -> None:
    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    canned = "\n".join(
        [
            '{"type":"item.started","item":{"id":"cmd","type":"command_execution",'
            '"command":"/usr/bin/false"}}',
            '{"type":"item.completed","item":{"id":"cmd","type":"command_execution",'
            '"command":"/usr/bin/false","status":"completed","exit_code":1}}',
        ]
    )
    facts = parse_command_diagnostics_events(
        io.StringIO(canned), fixture.repository, expected_command="/usr/bin/true"
    )
    assert facts.actual_command_count == 1
    assert facts.actual_command_equal is False
    assert facts.command_status == "failed"
    assert facts.actual_command_sha256 == hashlib.sha256(b"/usr/bin/false").hexdigest()
    assert parse_event_parser_counts(io.StringIO(canned + "\n{invalid")) == (2, 1)
    assert "/usr/bin/false" not in str(asdict(facts))


def test_ordinary_pair_fingerprint_matches_except_sandbox_and_gates_a(
    tmp_path: Path,
) -> None:
    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    codex = _fake_ordinary_codex(tmp_path / "codex")
    danger, workspace, equivalent = run_ordinary_command_pair(codex, fixture)
    assert workspace is not None
    assert equivalent is True
    assert danger.sandbox_mode == "danger-full-access"
    assert workspace.sandbox_mode == "workspace-write"
    assert danger.invocation_fingerprint == workspace.invocation_fingerprint
    assert danger.command_diagnostics.actual_command_equal is True
    assert danger.failure_origin == "success"
    normalized_argv = dict(danger.invocation_fingerprint)["normalized_argv_template"].split("\0")
    assert normalized_argv.index("--ask-for-approval") < normalized_argv.index("exec")


def test_ordinary_pair_stops_before_workspace_on_control_failure(tmp_path: Path) -> None:
    fixture = write_governed_fixture(tmp_path, base_url="", api_key_env="UNUSED")
    codex = _fake_ordinary_codex(tmp_path / "codex", fail_danger=True)
    danger, workspace, equivalent = run_ordinary_command_pair(codex, fixture)
    assert danger.exit_status == 1
    assert danger.failure_origin == "codex_startup"
    assert workspace is None
    assert equivalent is None


def test_governed_runner_rejects_invalid_budget(tmp_path: Path) -> None:
    from tests.helpers.e2e_support import run_governed_e2e

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
        (b"Warning: startup\nWARN: compatibility\nsandbox denied\nRAW", "sandbox_denied"),
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
    import tests.helpers.e2e_support as e2e_module

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


def _runtime_layout() -> SandboxInstallationLayoutFacts:
    executable = InstalledPathFacts(
        label="fixed",
        exists=True,
        regular_file=True,
        executable=True,
        symlink=False,
        resolved_basename_class="expected",
    )
    directory = InstalledDirectoryFacts(
        exists=True,
        directory=True,
        symlink=False,
        resolved_basename_class="expected",
        companion_presence=(),
    )
    return SandboxInstallationLayoutFacts(
        codex_launcher=executable,
        codex_binary_directory=directory,
        true_bin=executable,
        true_usr_bin=executable,
        cat_bin=executable,
        cat_usr_bin=executable,
        true_bin_usr_same_file=True,
        cat_bin_usr_same_file=True,
    )


def test_sandbox_runtime_decision_table_and_ambiguity_are_fixed() -> None:
    layout = _runtime_layout()
    successful_true = _differential_probe("true", success=True)
    successful_cat = _differential_probe("cat", success=True)
    failed_true = _differential_probe("true", success=False, failure_class="not_found")
    failed_cat = _differential_probe("cat", success=False, failure_class="not_found")

    assert (
        classify_sandbox_runtime_boundary(layout, successful_true, successful_cat)
        == "native_preflight_succeeded"
    )
    assert classify_sandbox_runtime_boundary(layout, failed_true, None) == "native_true_failed"
    assert (
        classify_sandbox_runtime_boundary(
            layout,
            successful_true,
            failed_cat,
        )
        == "native_cat_failed"
    )


def test_sandbox_runtime_probe_argv_allows_only_fixed_executable_spellings(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    assert (
        _build_sandbox_probe_argv("codex", repository, "true", executable_path="true")[-1] == "true"
    )
    assert _build_sandbox_probe_argv(
        "codex", repository, "cat", repository / "dependency", executable_path="cat"
    )[-2:] == ("cat", "dependency")
    argv = _build_sandbox_probe_argv("codex", repository, "true", executable_path="true")
    assert argv[1:5] == ("sandbox", "--permission-profile", ":workspace", "--cd")
    control_argv = _build_sandbox_probe_argv(
        "codex",
        repository,
        "true",
        executable_path="true",
        permission_profile=":danger-full-access",
    )
    assert control_argv[1:5] == (
        "sandbox",
        "--permission-profile",
        ":danger-full-access",
        "--cd",
    )
    with pytest.raises(ValueError):
        _build_sandbox_probe_argv("codex", repository, "true", executable_path="unsupported")
    with pytest.raises(ValueError):
        _build_sandbox_probe_argv("codex", repository, "true", executable_path="true;id")


def test_decision_tree_stops_after_failed_native_control(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tests.helpers.sandbox_runtime as e2e_module

    layout = _runtime_layout()
    failed_workspace = _differential_probe("true", success=False, failure_class="not_found")
    failed_control = replace(
        failed_workspace,
        permission_profile=":danger-full-access",
        semantic_mode="danger-full-access-control",
    )
    calls: list[tuple[str, str, str]] = []

    def fake_probe(
        _codex_bin: object,
        fixture: GovernedFixturePaths,
        _command: str,
        _checkout: Path,
        *,
        permission_profile: str,
        config_source: str,
        **_kwargs: object,
    ) -> SandboxProbeFacts:
        calls.append((str(fixture.repository), permission_profile, config_source))
        return failed_control if permission_profile == ":danger-full-access" else failed_workspace

    monkeypatch.setattr(e2e_module, "inspect_sandbox_installation_layout", lambda *_: layout)
    monkeypatch.setattr(e2e_module, "_run_sandbox_probe", fake_probe)

    facts = run_native_workspace_decision_tree("unused", product_checkout=tmp_path)

    assert isinstance(facts, NativeWorkspaceDecisionFacts)
    assert facts.classification == "codex_binary_or_native_helper_control_failure"
    assert facts.helper_calls == 2
    assert facts.host_workspace_probe is None
    assert facts.dependency_cat_probe is None
    assert calls[0][0] == calls[1][0]
    assert [call[1:] for call in calls] == [
        (":workspace", "disposable"),
        (":danger-full-access", "disposable"),
    ]


def test_decision_tree_uses_host_config_only_after_control_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tests.helpers.sandbox_runtime as e2e_module

    layout = _runtime_layout()
    failed_workspace = _differential_probe("true", success=False, failure_class="not_found")
    successful_control = replace(
        _differential_probe("true", success=True),
        permission_profile=":danger-full-access",
        semantic_mode="danger-full-access-control",
    )
    failed_host = _differential_probe("true", success=False, failure_class="not_found")
    calls: list[tuple[str, str]] = []

    def fake_probe(
        _codex_bin: object,
        _fixture: object,
        _command: str,
        _checkout: Path,
        *,
        permission_profile: str,
        config_source: str,
        **_kwargs: object,
    ) -> SandboxProbeFacts:
        calls.append((permission_profile, config_source))
        if permission_profile == ":danger-full-access":
            return successful_control
        if config_source == "host_user":
            return failed_host
        return failed_workspace

    monkeypatch.setattr(e2e_module, "inspect_sandbox_installation_layout", lambda *_: layout)
    monkeypatch.setattr(e2e_module, "_run_sandbox_probe", fake_probe)
    monkeypatch.setattr(
        e2e_module,
        "_effective_codex_config_facts",
        lambda _home: EffectiveCodexConfigFacts(
            True, "a" * 64, "oap-test", "workspace-write", None, None, "never"
        ),
    )

    facts = run_native_workspace_decision_tree("unused", product_checkout=tmp_path)

    assert facts.classification == "no_known_working_workspace_write_baseline"
    assert facts.helper_calls == 3
    assert calls == [
        (":workspace", "disposable"),
        (":danger-full-access", "disposable"),
        (":workspace", "host_user"),
    ]


def test_sandbox_runtime_failure_gates_models_and_stops_at_two_probes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tests.helpers.sandbox_runtime as e2e_module

    layout = _runtime_layout()
    failed_true = _differential_probe("true", success=False, failure_class="not_found")
    monkeypatch.setattr(e2e_module, "inspect_sandbox_installation_layout", lambda *_: layout)
    monkeypatch.setattr(e2e_module, "_run_sandbox_probe", lambda *_args, **_kwargs: failed_true)
    monkeypatch.setattr(
        e2e_module,
        "write_local_model_catalog",
        lambda *_args, **_kwargs: pytest.fail("catalog must remain gated"),
    )
    monkeypatch.setattr(
        e2e_module,
        "run_codex_once",
        lambda *_args, **_kwargs: pytest.fail("model must remain gated"),
    )

    facts = run_sandbox_runtime_boundary_diagnostic(
        "unused", product_checkout=tmp_path, base_url="", api_key_env="UNUSED"
    )

    assert facts.helper_calls == 1
    assert facts.classification == "native_true_failed"
    assert facts.governed_attempts == ()
    assert facts.governed_gate_allowed is False


def test_native_preflight_stops_at_first_failed_probe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tests.helpers.sandbox_runtime as e2e_module

    layout = _runtime_layout()
    failed_true = _differential_probe("true", success=False, failure_class="not_found")
    calls: list[str] = []

    def fake_probe(*args: object, **_kwargs: object) -> SandboxProbeFacts:
        calls.append(str(args[2]))
        return failed_true

    monkeypatch.setattr(e2e_module, "inspect_sandbox_installation_layout", lambda *_: layout)
    monkeypatch.setattr(e2e_module, "_run_sandbox_probe", fake_probe)
    monkeypatch.setattr(
        e2e_module,
        "write_local_model_catalog",
        lambda *_args, **_kwargs: pytest.fail("catalog must remain gated"),
    )
    facts = run_native_workspace_preflight("unused", product_checkout=tmp_path)

    assert calls == ["true"]
    assert facts.helper_calls == 1
    assert facts.classification == "native_true_failed"
    assert facts.corrected_cat_probe is None
    assert facts.governed_attempts == ()


def test_sandbox_runtime_success_allows_at_most_two_governed_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tests.helpers.sandbox_runtime as e2e_module

    fixture_holder: list[GovernedFixturePaths] = []
    successful_true = _differential_probe("true", success=True)
    successful_cat = _differential_probe("cat", success=True)
    layout = _runtime_layout()
    model_calls = 0

    def fake_probe(*args: object, **_kwargs: object) -> SandboxProbeFacts:
        command = args[2]
        return successful_true if command == "true" else successful_cat

    def fake_fixture(root: Path, base_url: str, api_key_env: str) -> GovernedFixturePaths:
        fixture = write_governed_fixture(root, base_url, api_key_env)
        fixture_holder.append(fixture)
        return fixture

    def fake_run(
        _codex_bin: object, fixture: GovernedFixturePaths, _prompt: str
    ) -> SanitizedCodexRun:
        nonlocal model_calls
        model_calls += 1
        dependency = (fixture.repository / "GOVERNANCE-DEPENDENCY.md").read_bytes()
        digest = hashlib.sha256(dependency).hexdigest()
        return SanitizedCodexRun(
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
            dependency_observation=DependencyObservationFacts(
                intended_dependency_reads=1,
                started_commands=1,
                completed_commands=1,
                successful_dependency_reads=1,
                output_sha256=digest,
                output_byte_length=len(dependency),
                rstrip_output_sha256=hashlib.sha256(dependency.rstrip()).hexdigest(),
            ),
        )

    monkeypatch.setattr(e2e_module, "inspect_sandbox_installation_layout", lambda *_: layout)
    monkeypatch.setattr(e2e_module, "write_governed_fixture", fake_fixture)
    monkeypatch.setattr(e2e_module, "_run_sandbox_probe", fake_probe)
    monkeypatch.setattr(e2e_module, "write_local_model_catalog", lambda *_args: None)
    monkeypatch.setattr(e2e_module, "run_codex_once", fake_run)

    facts = run_sandbox_runtime_boundary_diagnostic(
        "unused", product_checkout=tmp_path, base_url="", api_key_env="UNUSED"
    )

    assert facts.helper_calls == 2
    assert facts.classification == "governed_e2e_failed"
    assert len(facts.governed_attempts) == 2
    assert model_calls == 2


def test_sandbox_diagnostic_subclasses_are_fixed() -> None:
    assert _classify_sandbox_diagnostic_subclass("Permission denied\nraw") == "permission"
    assert _classify_sandbox_diagnostic_subclass("unexpected argument") == "argument"
    assert _classify_sandbox_diagnostic_subclass("") == "empty"


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
    import tests.helpers.e2e_support as e2e_module

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
    import tests.helpers.e2e_support as e2e_module

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
    import tests.helpers.e2e_support as e2e_module

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
