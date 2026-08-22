"""Focused tests for disposable real-Codex E2E support."""

from __future__ import annotations

import io
import subprocess
import tempfile
import tomllib
from collections import Counter
from pathlib import Path

import pytest

from slaif_local_coding.e2e import (
    GovernedFixturePaths,
    _final_agent_message_has_ack,
    metric_value,
    parse_codex_events,
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
        assert len(agents) >= 8_000
        assert "[GOVERNANCE-DEPENDENCY.md](GOVERNANCE-DEPENDENCY.md)" in agents
        assert f"SENTINEL-ACK:{fixture.sentinel_token}" in dependency
        status = subprocess.run(
            ["git", "-C", str(fixture.repository), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
        assert status.stdout == ""


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
