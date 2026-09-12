"""Tests for the repository-only diagnostic boundary."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.helpers.path_safety import (
    UnsafeDiagnosticPath,
    assert_allowlisted_diagnostic_argv,
    require_driver_path,
)


def test_driver_path_accepts_only_disposable_descendants(tmp_path: Path) -> None:
    disposable = tmp_path / "driver"
    disposable.mkdir()
    owned_file = disposable / "codex-home" / "config.toml"
    owned_file.parent.mkdir()
    assert require_driver_path(owned_file, disposable_root=disposable) == owned_file

    for unsafe in ("/", "~", "$HOME/.codex", "${CODEX_HOME}/sessions", "../outside"):
        with pytest.raises(UnsafeDiagnosticPath):
            require_driver_path(unsafe, disposable_root=disposable)


def test_diagnostic_command_must_be_explicitly_allowlisted(tmp_path: Path) -> None:
    disposable = tmp_path / "driver"
    disposable.mkdir()
    owned = disposable / "request.json"
    owned.write_text("{}", encoding="utf-8")

    assert_allowlisted_diagnostic_argv(
        ["python3.12", "-c", "pass"],
        allowed_commands={"python3.12"},
        disposable_root=disposable,
        path_arguments=(owned,),
    )
    with pytest.raises(UnsafeDiagnosticPath):
        assert_allowlisted_diagnostic_argv(
            ["host-diagnostic", "-n", "state", "/"],
            allowed_commands={"python3.12"},
            disposable_root=disposable,
            path_arguments=(Path("/"),),
        )


def test_host_codex_state_cannot_become_a_disposable_path(tmp_path: Path) -> None:
    disposable = tmp_path / "driver"
    disposable.mkdir()
    host_state = Path.home() / ".codex" / "sessions"
    with pytest.raises(UnsafeDiagnosticPath):
        require_driver_path(host_state, disposable_root=disposable)


def test_repository_diagnostics_do_not_construct_host_cache_searches() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    diagnostic_files = (
        repository_root / "scripts" / "gateway_accounting_rehearsal.py",
        repository_root / "scripts" / "codex_tool_envelope_differential.py",
        repository_root / "tests" / "helpers" / "capture_codex_tool_types.py",
    )
    search_commands = ("r" + "g", "grep", "find", "sed")
    host_markers = ("CODEX_" + "HOME", "." + "codex", "session", "history", "cache")
    forbidden = re.compile(
        rf"\b(?:{'|'.join(search_commands)})\b[^\n]*(?:{'|'.join(host_markers)})",
        re.IGNORECASE,
    )
    for path in diagnostic_files:
        assert forbidden.search(path.read_text(encoding="utf-8")) is None
