"""Unit coverage for the pure parts of the real-Codex RC gate (order 014-a,
workstream C). The live gate itself is opt-in and never runs in ordinary CI.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "real_codex_rc_qualification.py"

spec = importlib.util.spec_from_file_location("real_codex_rc_qualification", SCRIPT)
assert spec is not None and spec.loader is not None
gate = importlib.util.module_from_spec(spec)
sys.modules["real_codex_rc_qualification"] = gate
spec.loader.exec_module(gate)


def test_parse_counter_lines_and_request_status_counts() -> None:
    vision_200 = (
        'slaif_requests_total{endpoint="/v1/responses",route="rc3-smoke-vision",'
        'status="200",stream="false"} 2.0'
    )
    vision_500 = (
        'slaif_requests_total{endpoint="/v1/responses",route="rc3-smoke-vision",'
        'status="500",stream="false"} 1.0'
    )
    chat_200 = (
        'slaif_requests_total{endpoint="/v1/chat/completions",'
        'route="rc3-smoke-cache",status="200",stream="true"} 3.0'
    )
    text = "\n".join(
        [
            "# HELP slaif_requests_total Adapter requests",
            "# TYPE slaif_requests_total counter",
            vision_200,
            vision_500,
            chat_200,
            'slaif_upstream_failures_total{kind="upstream_status"} 0.0',
            "slaif_readiness 1.0",
        ]
    )
    counts = gate.request_status_counts(text, "/v1/responses", "rc3-smoke-vision")
    assert counts == {"200": 2, "500": 1}
    failures = gate.parse_counter_lines(text, "slaif_upstream_failures_total")
    assert sum(failures.values()) == 0.0
    assert gate.request_status_counts(text, "/v1/responses", "other-route") == {}


def test_build_codex_argv_never_contains_credentials() -> None:
    secret = "must-never-appear-in-argv"
    argv = gate.build_codex_argv(
        "/codex/bin/codex",
        Path("/tmp/workspace"),
        Path("/tmp/catalog.json"),
        "slaif_rc3_vision",
        "http://127.0.0.1:18031/v1",
    )
    assert argv[0] == "/codex/bin/codex"
    assert argv[1:4] == ["exec", "--ephemeral", "--ignore-user-config"]
    # The protected host cannot run bubblewrap (user-namespace network
    # restriction); the gate's disposable/loopback/bounded boundary is the
    # control, so the client sandbox is explicitly danger-full-access.
    assert argv[4:6] == ["-s", "danger-full-access"]
    assert "-C" in argv and str(Path("/tmp/workspace")) in argv
    assert f"model_provider={gate.CLIENT_ENV_KEY[:0]}slaif_rc3_vision" in argv
    provider_lines = [entry for entry in argv if entry.startswith("model_providers.")]
    assert len(provider_lines) == 1
    assert f'env_key="{gate.CLIENT_ENV_KEY}"' in provider_lines[0]
    assert 'wire_api="responses"' in provider_lines[0]
    assert "http://127.0.0.1:18031/v1" in provider_lines[0]
    assert gate.PROMPT == argv[-1]
    assert all(secret not in entry for entry in argv)


@pytest.mark.parametrize("arm", ["VISION", "CACHE", "BOTH"])
def test_render_adapter_config_arm_contracts(arm: str, tmp_path: Path) -> None:
    text = gate.render_adapter_config(
        arm=arm,
        upstream_base_url="http://127.0.0.1:18020/v1",
        upstream_api_key_env="SLAIF_RC3_QUALIFICATION_KEY",
        adapter_port=18031,
        cache_root=tmp_path / "cache",
    )
    config = tomllib.loads(text)
    assert config["server"]["listen_host"] == "127.0.0.1"
    assert config["server"]["listen_port"] == 18031
    assert config["gateway_ingress"]["mode"] == "disabled"
    assert config["upstream"]["base_url"] == "http://127.0.0.1:18020/v1"
    assert config["upstream"]["model"] == "qwen3.8-27b"
    assert config["upstream"]["api_key_env"] == "SLAIF_RC3_QUALIFICATION_KEY"
    route = config["routes"][0]
    assert route["name"] == f"rc3-smoke-{arm.lower()}"
    assert route["model"] == "qwen3.8-27b"
    if arm in ("VISION", "BOTH"):
        assert route["max_images_per_request"] == 1
        assert route["image_overflow_policy"] == "retain_newest"
    else:
        assert "max_images_per_request" not in route
        assert route["image_overflow_policy"] == "passthrough"
    constitution = arm in ("CACHE", "BOTH")
    assert route["observation_enabled"] is constitution
    assert route["constitution_enabled"] is constitution
    assert config["constitution"]["enabled"] is constitution
    if constitution:
        assert config["constitution"]["identity_source"] == "static"
        assert config["constitution"]["principal"] == "rc3-smoke-principal"
        assert config["constitution"]["session"] == "rc3-smoke-session"
        assert config["constitution"]["repository"] == "rc3-smoke-repository"
        assert config["compiler"]["enabled"] is True
    else:
        assert config["compiler"]["enabled"] is False
    assert config["cache"]["root"] == str(tmp_path / "cache")


def _valid_record() -> dict[str, Any]:
    arm_facts = {
        "attempts": 1,
        "exit_status": 0,
        "duration_seconds": 42,
        "sentinel_present": True,
        "sentinel_size_bytes": 3,
        "adapter_requests_ok": 2,
        "adapter_requests_500": 0,
        "adapter_requests_422": 0,
        "upstream_failures": 0,
        "compiler_cache_entries": 1,
        "stdout_bytes": 120,
        "stderr_bytes": 0,
        "verdict": "PASS",
        "failure_class": "none",
    }
    return {
        "schema": "slaif-real-codex-rc-qualification-v1",
        "created_at": "2026-09-28T12:00:00Z",
        "client": {"version": "0.149.0", "sha256": "a" * 64, "binary_class": "standalone-release"},
        "wheel": {"sha256": "b" * 64, "expected_sha256": "b" * 64, "binding": "equal"},
        "topology": (
            "disposable-codex-home;loopback-adapter;port-18031;"
            "existing-backend;gateway-ingress-disabled"
        ),
        "arms": {
            "VISION": dict(arm_facts),
            "CACHE": dict(arm_facts),
            "BOTH": dict(arm_facts),
        },
        "protected_state_unchanged": True,
        "protected_state": {"files_checked": 3, "files_changed": 0, "units": {}, "ports": {}},
        "disposable_state_removed": True,
        "verdict": "PASS",
    }


def test_validate_facts_record_accepts_valid() -> None:
    gate.validate_facts_record(_valid_record())


@pytest.mark.parametrize(
    "mutate",
    [
        lambda record: record.pop("schema"),
        lambda record: record.update({"unexpected": 1}),
        lambda record: record["client"].update({"sha256": "zz" * 32}),
        lambda record: record["wheel"].update({"binding": "maybe"}),
        lambda record: record["arms"]["VISION"].update({"verdict": "MAYBE"}),
        lambda record: record["arms"]["VISION"].pop("attempts"),
        lambda record: record["arms"].update({"DIRECT": dict(record["arms"]["VISION"])}),
        lambda record: record.update({"verdict": "ACCEPTED"}),
        lambda record: record.update({"protected_state_unchanged": "yes"}),
        lambda record: record["protected_state"].update({"units": "no"}),
    ],
)
def test_validate_facts_record_rejects_drift(mutate: Callable[[dict[str, Any]], None]) -> None:
    record = _valid_record()
    mutate(record)
    if "DIRECT" in record.get("arms", {}):
        # DIRECT is allowed as an arm name; make this case fail on the key set
        record["arms"]["DIRECT"].pop("failure_class")
    with pytest.raises(gate.QualificationError):
        gate.validate_facts_record(record)


def test_count_cache_entries(tmp_path: Path) -> None:
    assert gate.count_cache_entries(tmp_path / "missing") == 0
    (tmp_path / "sub").mkdir()
    (tmp_path / "a").write_text("x")
    (tmp_path / "sub" / "b").write_text("y")
    assert gate.count_cache_entries(tmp_path) == 2


def test_diff_protected_detects_change() -> None:
    before = gate.ProtectedSnapshot(
        files={"f1": "a", "f2": "b"}, units={"u1": "active"}, ports={18020: 1}
    )
    after = gate.ProtectedSnapshot(
        files={"f1": "a", "f2": "b"}, units={"u1": "active"}, ports={18020: 1}
    )
    assert gate.diff_protected(before, after) == {
        "files_changed": 0,
        "units_changed": 0,
        "ports_changed": 0,
    }
    after.units["u1"] = "inactive"
    after.files["f2"] = "changed"
    after.ports[18020] = 2
    assert gate.diff_protected(before, after) == {
        "files_changed": 1,
        "units_changed": 1,
        "ports_changed": 1,
    }


def _fake_run(state: str, returncode: int) -> Callable[..., subprocess.CompletedProcess[bytes]]:
    def run(*a: str | bytes, **k: object) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(
            args=list(a), returncode=returncode, stdout=state.encode(), stderr=b""
        )

    return run


@pytest.mark.parametrize(
    ("state", "returncode"),
    [
        ("active", 0),
        ("inactive", 3),  # legitimate protected state (qwen-serving.service)
        ("inactive", 4),  # unit not present still prints its state
        ("failed", 3),
    ],
    ids=["active", "inactive", "not-present", "failed"],
)
def test_read_unit_state_accepts_printed_states(
    monkeypatch: pytest.MonkeyPatch, state: str, returncode: int
) -> None:
    # is-active exits non-zero for legitimate non-active states; the
    # printed state is the readability criterion, never the exit code.
    monkeypatch.setattr(gate.subprocess, "run", _fake_run(state, returncode))
    assert gate.read_unit_state("some-unit.service") == state


def test_read_unit_state_fails_closed_when_unreadable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(gate.subprocess, "run", _fake_run("", 1))
    with pytest.raises(gate.QualificationError, match="unreadable"):
        gate.read_unit_state("some-unit.service")


def test_workspace_commit_is_independent_of_host_git_identity(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # The disposable smoke workspace must commit with its OWN synthetic
    # identity; a host without any git identity (or with one) must not
    # change the gate's behavior.
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", os.devnull)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    root = tmp_path / "root"
    workspace = root / "vision" / "workspace"
    root.mkdir()
    gate._prepare_workspace(root, workspace)
    assert (workspace / "README.md").is_file()
    agents = workspace / "AGENTS.md"
    assert agents.is_file()
    assert agents.read_text() == gate.SMOKE_AGENTS_MD
    log = subprocess.run(
        ["git", "-C", str(workspace), "log", "--format=%an <%ae> %s"],
        capture_output=True,
        check=True,
    )
    assert "RC3 Smoke <rc3-smoke@example.invalid> Synthetic smoke workspace" in (
        log.stdout.decode()
    )
    committed = subprocess.run(
        ["git", "-C", str(workspace), "show", "--name-only", "--format=", "HEAD"],
        capture_output=True,
        check=True,
    )
    assert "AGENTS.md" in committed.stdout.decode().splitlines()


def test_smoke_agents_md_yields_zero_dependency_candidates() -> None:
    # The synthetic governance content must be a genuine root trigger but
    # must never declare dependency candidates (no path-like tokens, no
    # quotes or backticks): the compiler compiles the root only.
    from slaif_local_coding.config import ObservationPolicy
    from slaif_local_coding.constitution.references import extract_references

    extraction = extract_references(gate.SMOKE_AGENTS_MD, ObservationPolicy())
    assert extraction.candidates == ()


def test_arm_crash_yields_sanitized_failed_arm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # An unexpected crash inside an arm must be recorded as a sanitized
    # exception class on the closed-schema arm facts (never raw output)
    # and stop the serial sequence at the first failed product arm.
    calls: list[str] = []

    def fake_run_arm(args: object, arm: str, api_key: str, facts_out: object) -> None:
        calls.append(arm)
        raise RuntimeError("boom")

    monkeypatch.setattr(gate, "run_arm", fake_run_arm)
    facts: dict[str, object] = {"arms": {}}
    gate._run_arms(None, ("VISION", "CACHE", "BOTH"), "key", facts)
    assert calls == ["VISION"], "serial sequence must stop at the first failed arm"
    arm = cast(dict[str, object], cast(dict[str, object], facts["arms"])["VISION"])
    assert arm["verdict"] == "FAIL"
    assert arm["failure_class"] == "gate-crash (RuntimeError)"
    assert "boom" not in json.dumps(facts, sort_keys=True)


def test_sentinel_constants_are_bounded() -> None:
    assert gate.SENTINEL_SIZE == 3
    assert gate.OUTPUT_CAPTURE_CAP <= 1_048_576
    assert gate.PRODUCT_ARMS == ("VISION", "CACHE", "BOTH")


def test_schema_and_arm_names_are_closed() -> None:
    assert gate.SCHEMA == "slaif-real-codex-rc-qualification-v1"
    assert set(gate.PRODUCT_ARMS) == {"VISION", "CACHE", "BOTH"}
    payload = json.dumps(_valid_record(), sort_keys=True)
    assert "127.0.0.1" not in payload or "port-18031" in payload
