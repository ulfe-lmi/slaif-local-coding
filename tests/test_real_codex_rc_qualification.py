"""Unit coverage for the pure parts of the real-Codex RC gate (order 014-a,
workstream C; order 014-b, workstream A: qualification-harness gap closure).

The live gate itself is opt-in and never runs in ordinary CI. These tests
cover: stdin prompt delivery, argv secrecy (no prompt/URL/credential),
disposable-config permissions, protected upstream-URL file reference,
mechanically enforced live byte-cap termination, content-free event
classification, every activity ceiling decision, sanitized failure output,
and unexpected-process (group) cleanup. No live backend is required.
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import os
import stat
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

# Typed aliases for the gate's dataclasses (the module is loaded dynamically,
# so mypy cannot attribute-resolve them through the module object).
Limits = cast(type, gate.Limits)
ArmFacts = cast(type, gate.ArmFacts)

UPSTREAM_URL = "http://127.0.0.1:18020/v1"
SECRET = "must-never-appear-anywhere-in-argv"


def test_parse_counter_lines_and_request_status_counts() -> None:
    vision_200 = (
        'slaif_requests_total{endpoint="/v1/responses",route="rc8-smoke-vision",'
        'status="200",stream="false"} 2.0'
    )
    vision_500 = (
        'slaif_requests_total{endpoint="/v1/responses",route="rc8-smoke-vision",'
        'status="500",stream="false"} 1.0'
    )
    vision_422 = (
        'slaif_requests_total{endpoint="/v1/responses",route="rc8-smoke-vision",'
        'status="422",stream="false"} 1.0'
    )
    chat_200 = (
        'slaif_requests_total{endpoint="/v1/chat/completions",'
        'route="rc8-smoke-cache",status="200",stream="true"} 3.0'
    )
    compiler = "slaif_constitution_compiler_attempts_total 2.0"
    text = "\n".join(
        [
            "# HELP slaif_requests_total Adapter requests",
            "# TYPE slaif_requests_total counter",
            vision_200,
            vision_500,
            vision_422,
            chat_200,
            'slaif_upstream_failures_total{kind="upstream_status"} 0.0',
            compiler,
            "slaif_readiness 1.0",
        ]
    )
    counts = gate.request_status_counts(text, "/v1/responses", "rc8-smoke-vision")
    assert counts == {"200": 2, "500": 1, "422": 1}
    assert gate.request_total(counts) == 4
    assert gate.request_status_counts(text, "/v1/responses", "other-route") == {}
    failures = gate.parse_counter_lines(text, "slaif_upstream_failures_total")
    assert sum(failures.values()) == 0.0
    compiler_calls = gate.parse_counter_lines(text, "slaif_constitution_compiler_attempts_total")
    assert sum(compiler_calls.values()) == 2.0


def test_build_codex_argv_is_secret_free_and_prompt_free() -> None:
    # Order 014-b, WS-A.2/.3: the argv carries the fixed non-sensitive flags
    # ONLY. No prompt substring, no model provider, no base URL, no
    # credential, no catalog path, no -c override.
    argv = gate.build_codex_argv("/codex/bin/codex")
    assert argv == ["/codex/bin/codex", "exec", "--ephemeral", "-s", "danger-full-access", "--json"]
    assert "-c" not in argv
    assert "-m" not in argv
    assert "-C" not in argv
    assert UPSTREAM_URL not in " ".join(argv)
    assert "http://127.0.0.1:18031/v1" not in " ".join(argv)
    # No prompt substring (use a long prefix and a long suffix).
    for fragment in (gate.PROMPT[:24], gate.PROMPT[24:48], gate.PROMPT[-24:]):
        assert fragment not in " ".join(argv)
    assert SECRET not in " ".join(argv)
    # The provider/model/catalog configuration surface is the home config
    # renderer, not the argv builder.
    assert "base_url" not in " ".join(argv)
    assert "env_key" not in " ".join(argv)


def test_render_codex_home_config_is_env_name_only() -> None:
    catalog = Path("/tmp/catalog.json")
    text = gate.render_codex_home_config(
        provider="slaif_rc8_vision",
        base_url="http://127.0.0.1:18031/v1",
        catalog=catalog,
        model=gate.MODEL,
    )
    config = tomllib.loads(text)
    assert config["model"] == gate.MODEL
    assert config["model_provider"] == "slaif_rc8_vision"
    assert config["model_catalog_json"] == str(catalog)
    provider = config["model_providers"]["slaif_rc8_vision"]
    assert provider["base_url"] == "http://127.0.0.1:18031/v1"
    # The credential is referenced ONLY by the environment variable name.
    assert provider["env_key"] == gate.CLIENT_ENV_KEY
    assert provider["wire_api"] == "responses"
    assert SECRET not in text
    # The renderer cannot even receive a credential value.
    params = set(inspect.signature(gate.render_codex_home_config).parameters)
    assert params == {"provider", "base_url", "catalog", "model"}


def test_write_codex_home_config_is_mode_0600(tmp_path: Path) -> None:
    home = tmp_path / "codex-home"
    home.mkdir(mode=0o700)
    config = gate.write_codex_home_config(
        home,
        gate.render_codex_home_config(
            provider="p", base_url="http://127.0.0.1:18031/v1", catalog=home / "c.json", model="m"
        ),
    )
    assert config == home / "config.toml"
    assert stat.S_IMODE(config.stat().st_mode) == 0o600


def test_write_adapter_config_is_mode_0600(tmp_path: Path) -> None:
    config = gate.write_adapter_config(
        tmp_path,
        1,
        gate.render_adapter_config(
            arm="VISION",
            upstream_base_url=UPSTREAM_URL,
            credential_env_name=gate.CLIENT_ENV_KEY,
            adapter_port=18031,
            cache_root=tmp_path / "cache",
        ),
    )
    assert stat.S_IMODE(config.stat().st_mode) == 0o600
    assert config.name == "adapter-attempt-1.toml"


@pytest.mark.parametrize("arm", ["VISION", "CACHE", "BOTH"])
def test_render_adapter_config_arm_contracts(arm: str, tmp_path: Path) -> None:
    text = gate.render_adapter_config(
        arm=arm,
        upstream_base_url=UPSTREAM_URL,
        credential_env_name="SLAIF_RC8_QUALIFICATION_KEY",
        adapter_port=18031,
        cache_root=tmp_path / "cache",
    )
    config = tomllib.loads(text)
    assert config["server"]["listen_host"] == "127.0.0.1"
    assert config["server"]["listen_port"] == 18031
    assert config["gateway_ingress"]["mode"] == "disabled"
    assert config["upstream"]["base_url"] == UPSTREAM_URL
    assert config["upstream"]["model"] == "qwen3.8-27b"
    # The adapter config carries only the environment variable NAME.
    assert config["upstream"]["api_key_env"] == "SLAIF_RC8_QUALIFICATION_KEY"
    assert config["compiler"]["api_key_env"] == "SLAIF_RC8_QUALIFICATION_KEY"
    assert SECRET not in text
    route = config["routes"][0]
    assert route["name"] == f"rc8-smoke-{arm.lower()}"
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
        assert config["constitution"]["principal"] == "rc8-smoke-principal"
        assert config["constitution"]["session"] == "rc8-smoke-session"
        assert config["constitution"]["repository"] == "rc8-smoke-repository"
        assert config["compiler"]["enabled"] is True
    else:
        assert config["compiler"]["enabled"] is False
    assert config["cache"]["root"] == str(tmp_path / "cache")


def _write_url_file(tmp_path: Path, content: str, mode: int = 0o600) -> Path:
    path = tmp_path / "upstream-base-url"
    path.write_text(content, encoding="utf-8")
    path.chmod(mode)
    return path


def test_read_upstream_base_url_accepts_protected_file(tmp_path: Path) -> None:
    path = _write_url_file(tmp_path, UPSTREAM_URL + "\n")
    assert gate.read_upstream_base_url(path) == UPSTREAM_URL


@pytest.mark.parametrize(
    ("content", "mode", "match"),
    [
        ("http://127.0.0.1:18020/v1\n", 0o644, "mode 0600"),
        ("http://127.0.0.1:18020/v1\nhttp://10.0.0.1:1/v1\n", 0o600, "exactly one"),
        ("\n\n", 0o600, "exactly one"),
        ("not a url\n", 0o600, "http"),
        ("ftp://127.0.0.1:1/v1\n", 0o600, "http"),
    ],
    ids=["mode-0644", "two-lines", "empty", "non-url", "wrong-scheme"],
)
def test_read_upstream_base_url_rejects_unprotected_or_malformed(
    tmp_path: Path, content: str, mode: int, match: str
) -> None:
    path = _write_url_file(tmp_path, content, mode)
    with pytest.raises(gate.QualificationError, match=match):
        gate.read_upstream_base_url(path)


def test_read_upstream_base_url_rejects_symlink(tmp_path: Path) -> None:
    real = _write_url_file(tmp_path, UPSTREAM_URL + "\n")
    link = tmp_path / "link"
    os.symlink(real, link)
    with pytest.raises(gate.QualificationError, match="symlink"):
        gate.read_upstream_base_url(link)


# ---------------------------------------------------------------------------
# Content-free event classification (order 014-b, WS-A.5)
# ---------------------------------------------------------------------------


def test_classify_event_line_counts_only_tool_completions() -> None:
    assert gate.classify_event_line('{"type": "thread.started"}') == 0
    assert gate.classify_event_line('{"type": "turn.started"}') == 0
    assert (
        gate.classify_event_line('{"type": "item.created", "item": {"type": "command_execution"}}')
        == 0
    )
    assert (
        gate.classify_event_line(
            '{"type": "item.completed", "item": {'
            '"type": "command_execution", "command": "rm -rf /"}}'
        )
        == 1
    )
    assert (
        gate.classify_event_line('{"type": "item.completed", "item": {"type": "file_change"}}') == 1
    )
    assert (
        gate.classify_event_line('{"type": "item.completed", "item": {"type": "agent_message"}}')
        == 0
    )
    assert (
        gate.classify_event_line('{"type": "item.completed", "item": {"type": "mcp_tool_call"}}')
        == 1
    )
    assert (
        gate.classify_event_line('{"type": "item.completed", "item": {"type": "unknown_tool"}}')
        == 0
    )


@pytest.mark.parametrize(
    "line",
    [
        "not json at all",
        '{"type": "item.completed"',  # truncated
        '["list", "not", "object"]',
        "null",
    ],
    ids=["plain-text", "truncated", "non-object", "null"],
)
def test_classify_event_line_fails_closed_on_unclassifiable_lines(line: str) -> None:
    with pytest.raises(gate.EventStreamError):
        gate.classify_event_line(line)


# ---------------------------------------------------------------------------
# Ceiling decision law (order 014-b, WS-A.5): pure, closed, fail-closed
# ---------------------------------------------------------------------------


def _limits(**overrides: int) -> Any:
    base = dict(
        output_cap_bytes=1024,
        max_attempts=2,
        attempt_timeout_seconds=60,
        total_timeout_seconds=120,
        max_adapter_requests=8,
        max_compiler_calls=4,
        max_tool_interactions=3,
        arm_count=3,
    )
    base.update(overrides)
    return gate.Limits(**base)


def _passing_facts(arm: str = "VISION") -> Any:
    facts = gate.ArmFacts(arm=arm)
    facts.exit_status = 0
    facts.sentinel_present = True
    facts.sentinel_size_bytes = gate.SENTINEL_SIZE
    facts.tool_interactions = 1
    if arm in gate.PRODUCT_ARMS:
        facts.adapter_requests_ok = 2
        facts.adapter_requests_total = 2
        if arm in ("CACHE", "BOTH"):
            facts.compiler_cache_entries = 1
    return facts


def test_evaluate_arm_failure_passes_within_ceilings() -> None:
    for arm in ("VISION", "CACHE", "BOTH", "DIRECT"):
        assert gate.evaluate_arm_failure(arm, _passing_facts(arm), _limits()) is None


@pytest.mark.parametrize(
    ("arm", "mutate", "expected"),
    [
        ("VISION", lambda f: setattr(f, "exit_status", 1), "codex-exit"),
        ("VISION", lambda f: setattr(f, "sentinel_present", False), "sentinel-missing"),
        ("VISION", lambda f: setattr(f, "sentinel_size_bytes", 99), "sentinel-missing"),
        ("VISION", lambda f: setattr(f, "tool_interactions", 0), "tool-interaction-missing"),
        ("VISION", lambda f: setattr(f, "tool_interactions", 99), "tool-ceiling"),
        ("CACHE", lambda f: setattr(f, "adapter_requests_ok", 0), "adapter-request-missing"),
        ("CACHE", lambda f: setattr(f, "adapter_requests_500", 1), "internal-500"),
        ("CACHE", lambda f: setattr(f, "adapter_requests_422", 1), "image-policy-422"),
        ("CACHE", lambda f: setattr(f, "upstream_failures", 1), "upstream-failure"),
        ("CACHE", lambda f: setattr(f, "adapter_requests_total", 99), "requests-ceiling"),
        ("CACHE", lambda f: setattr(f, "compiler_calls", 99), "compiler-ceiling"),
        ("CACHE", lambda f: setattr(f, "compiler_cache_entries", 0), "compiler-evidence-missing"),
        ("BOTH", lambda f: setattr(f, "compiler_cache_entries", 0), "compiler-evidence-missing"),
    ],
    ids=[
        "nonzero-exit",
        "sentinel-missing",
        "sentinel-wrong-size",
        "no-tool-interaction",
        "tool-ceiling",
        "no-adapter-request",
        "internal-500",
        "image-policy-422",
        "upstream-failure",
        "requests-ceiling",
        "compiler-ceiling",
        "compiler-evidence-missing-cache",
        "compiler-evidence-missing-both",
    ],
)
def test_evaluate_arm_failure_classes(
    arm: str, mutate: Callable[[Any], None], expected: str
) -> None:
    facts = _passing_facts(arm)
    mutate(facts)
    assert gate.evaluate_arm_failure(arm, facts, _limits()) == expected


def test_evaluate_arm_failure_direct_never_checks_adapter_metrics() -> None:
    facts = _passing_facts("DIRECT")
    facts.adapter_requests_ok = 0  # no adapter in the DIRECT path
    assert gate.evaluate_arm_failure("DIRECT", facts, _limits()) is None


# ---------------------------------------------------------------------------
# Closed-schema facts record (v2)
# ---------------------------------------------------------------------------


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
        "adapter_requests_total": 2,
        "upstream_failures": 0,
        "compiler_calls": 1,
        "compiler_cache_entries": 1,
        "tool_interactions": 1,
        "stdout_bytes": 120,
        "stderr_bytes": 0,
        "verdict": "PASS",
        "failure_class": "none",
    }
    return {
        "schema": "slaif-real-codex-rc-qualification-v2",
        "created_at": "2026-09-28T12:00:00Z",
        "client": {"version": "0.149.0", "sha256": "a" * 64, "binary_class": "standalone-release"},
        "wheel": {"sha256": "b" * 64, "expected_sha256": "b" * 64, "binding": "equal"},
        "topology": (
            "disposable-codex-home;loopback-adapter;port-18031;"
            "existing-backend;gateway-ingress-disabled"
        ),
        "limits": {
            "output_cap_bytes": 1048576,
            "max_attempts": 2,
            "attempt_timeout_seconds": 600,
            "total_timeout_seconds": 5400,
            "max_adapter_requests": 64,
            "max_compiler_calls": 4,
            "max_tool_interactions": 8,
            "arm_count": 3,
        },
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
        lambda record: record.pop("limits"),
        lambda record: record.update({"unexpected": 1}),
        lambda record: record["limits"].pop("max_tool_interactions"),
        lambda record: record["limits"].update({"max_attempts": 9}),
        lambda record: record["limits"].update({"arm_count": 5}),
        lambda record: record["client"].update({"sha256": "zz" * 32}),
        lambda record: record["wheel"].update({"binding": "maybe"}),
        lambda record: record["wheel"].update({"expected_sha256": "0" * 63}),
        lambda record: record["arms"]["VISION"].update({"verdict": "MAYBE"}),
        lambda record: record["arms"]["VISION"].pop("tool_interactions"),
        lambda record: record["arms"]["VISION"].update({"tool_interactions": -1}),
        lambda record: record["arms"]["VISION"].update({"failure_class": "raw output: rm -rf /"}),
        lambda record: record["arms"]["VISION"].pop("adapter_requests_total"),
        lambda record: record.update({"verdict": "ACCEPTED"}),
        lambda record: record.update({"protected_state_unchanged": "yes"}),
        lambda record: record["protected_state"].update({"units": "no"}),
    ],
)
def test_validate_facts_record_rejects_drift(mutate: Callable[[dict[str, Any]], None]) -> None:
    record = _valid_record()
    mutate(record)
    with pytest.raises(gate.QualificationError):
        gate.validate_facts_record(record)


def test_failure_class_pattern_is_sanitized() -> None:
    for good in ("none", "codex-exit", "output-cap-exceeded", "gate-crash (RuntimeError)"):
        assert gate.FAILURE_CLASS_PATTERN.fullmatch(good)
    for bad in (
        "",
        "raw: rm -rf /",
        "has space",
        "Upper-Case",
        "injection\nnewline",
        "x" * 65,
        "-leading-hyphen",
    ):
        assert not gate.FAILURE_CLASS_PATTERN.fullmatch(bad)


# ---------------------------------------------------------------------------
# Live bounded subprocess law (no backend required: local child processes)
# ---------------------------------------------------------------------------


def _stdin_probe_cwd(tmp_path: Path) -> Path:
    cwd = tmp_path / "probe"
    cwd.mkdir()
    return cwd


def test_run_capped_process_delivers_prompt_over_stdin(tmp_path: Path) -> None:
    # The child reads stdin and reports ONLY the byte count on stderr:
    # the prompt bytes reached stdin and no content was retained.
    cmd = [
        sys.executable,
        "-c",
        "import sys\n"
        "data = sys.stdin.buffer.read()\n"
        "sys.stderr.buffer.write(str(len(data)).encode())",
    ]
    result = gate.run_capped_process(
        argv=cmd,
        env=dict(os.environ),
        stdin_text=gate.PROMPT,
        cwd=_stdin_probe_cwd(tmp_path),
        output_cap_bytes=gate.OUTPUT_CAPTURE_CAP_DEFAULT,
        timeout_seconds=60,
    )
    assert result.returncode == 0
    assert result.stdout_bytes == 0
    # The stderr payload is exactly the decimal byte count of the prompt.
    assert result.stderr_bytes == len(str(len(gate.PROMPT)))
    assert not result.cap_exceeded
    assert not result.timed_out
    assert result.event_stream_ok
    assert result.tool_interactions == 0


def test_run_capped_process_enforces_live_byte_cap_and_terminates(tmp_path: Path) -> None:
    cmd = [
        sys.executable,
        "-c",
        "import sys\nsys.stdout.write('x' * 100000)\nsys.stdout.flush()",
    ]
    result = gate.run_capped_process(
        argv=cmd,
        env=dict(os.environ),
        stdin_text="hi",
        cwd=_stdin_probe_cwd(tmp_path),
        output_cap_bytes=1000,
        timeout_seconds=60,
    )
    assert result.cap_exceeded is True
    # Recorded byte counts are the CAPPED values — never the raw total.
    assert result.stdout_bytes == 1000
    assert result.stderr_bytes == 0
    assert result.returncode is not None
    assert result.returncode != 0
    assert not result.timed_out
    assert result.event_stream_ok


def test_run_capped_process_times_out_and_terminates(tmp_path: Path) -> None:
    cmd = [sys.executable, "-c", "import time\ntime.sleep(30)"]
    result = gate.run_capped_process(
        argv=cmd,
        env=dict(os.environ),
        stdin_text="hi",
        cwd=_stdin_probe_cwd(tmp_path),
        output_cap_bytes=1024,
        timeout_seconds=1,
    )
    assert result.timed_out is True
    assert result.returncode is not None
    assert not result.cap_exceeded


def test_run_capped_process_fails_closed_on_non_json_stdout(tmp_path: Path) -> None:
    cmd = [
        sys.executable,
        "-c",
        "import sys\nsys.stdout.write('definitely not json\\n')\nsys.stdout.flush()",
    ]
    result = gate.run_capped_process(
        argv=cmd,
        env=dict(os.environ),
        stdin_text="hi",
        cwd=_stdin_probe_cwd(tmp_path),
        output_cap_bytes=1024,
        timeout_seconds=60,
    )
    assert result.event_stream_ok is False
    assert result.tool_interactions == 0


def test_run_capped_process_counts_tool_events_content_free(tmp_path: Path) -> None:
    events = (
        '{"type": "thread.started"}\n'
        '{"type": "item.completed", "item": {"type": "command_execution", '
        '"command": "echo secret-tool-argument"}}\n'
        '{"type": "item.completed", "item": {"type": "agent_message", "text": "secret text"}}\n'
        '{"type": "item.completed", "item": {"type": "file_change"}}\n'
        '{"type": "turn.completed"}\n'
    )
    cmd = [
        sys.executable,
        "-c",
        "import sys\nsys.stdout.write(sys.stdin.buffer.read().decode())",
    ]
    result = gate.run_capped_process(
        argv=cmd,
        env=dict(os.environ),
        stdin_text=events,
        cwd=_stdin_probe_cwd(tmp_path),
        output_cap_bytes=gate.OUTPUT_CAPTURE_CAP_DEFAULT,
        timeout_seconds=60,
    )
    assert result.returncode == 0
    assert result.event_stream_ok is True
    # Exactly the two tool-completion events are counted; arguments and
    # message text are content, never retained or counted.
    assert result.tool_interactions == 2


def test_run_capped_process_kills_the_whole_session(tmp_path: Path) -> None:
    # A background child (same session) must die with the capped session:
    # the gate never leaves an unbounded process behind.
    pidfile = tmp_path / "child.pid"
    spawn = (
        "import os, sys, time\n"
        "pid = os.fork()\n"
        "if pid == 0:\n"
        "    time.sleep(30)\n"
        "    os._exit(0)\n"
        "with open(sys.argv[1], 'w') as handle:\n"
        "    handle.write(str(pid))\n"
        "sys.stdout.write('x' * 10000)\n"
        "sys.stdout.flush()\n"
    )
    result = gate.run_capped_process(
        argv=[sys.executable, "-c", spawn, str(pidfile)],
        env=dict(os.environ),
        stdin_text="hi",
        cwd=_stdin_probe_cwd(tmp_path),
        output_cap_bytes=100,
        timeout_seconds=30,
    )
    assert result.cap_exceeded is True
    child_pid = int(pidfile.read_text())
    # Allow the kill to propagate; then the child must be gone.
    import time as _time

    for _ in range(50):
        try:
            os.kill(child_pid, 0)
        except ProcessLookupError:
            break
        except PermissionError:
            break  # zombie reparented; still not alive as a session member
        _time.sleep(0.1)
    else:
        pytest.fail("session child survived the capped kill (cleanup failure)")


# ---------------------------------------------------------------------------
# Protected snapshot, unit state, workspace, crash boundary (retained from
# order 014-a)
# ---------------------------------------------------------------------------


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
    assert "RC8 Smoke <rc8-smoke@example.invalid> Synthetic smoke workspace" in (
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

    def fake_run_arm(
        args: object,
        arm: str,
        credential: str,
        upstream_base_url: str,
        limits: object,
        facts_out: object,
    ) -> None:
        calls.append(arm)
        raise RuntimeError("boom")

    monkeypatch.setattr(gate, "run_arm", fake_run_arm)
    facts: dict[str, object] = {"arms": {}}
    import time as _time

    deadline = _time.monotonic() + 3600
    gate._run_arms(
        None, ("VISION", "CACHE", "BOTH"), "key", UPSTREAM_URL, _limits(), deadline, facts
    )
    assert calls == ["VISION"], "serial sequence must stop at the first failed arm"
    arm = cast(dict[str, object], cast(dict[str, object], facts["arms"])["VISION"])
    assert arm["verdict"] == "FAIL"
    assert arm["failure_class"] == "gate-crash (RuntimeError)"
    assert "boom" not in json.dumps(facts, sort_keys=True)


def test_run_arms_total_timeout_fails_remaining_arms_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def fake_run_arm(
        args: object,
        arm: str,
        credential: str,
        upstream_base_url: str,
        limits: object,
        facts_out: Any,
    ) -> None:
        calls.append(arm)
        facts_out.verdict = "PASS"
        facts_out.failure_class = "none"

    monkeypatch.setattr(gate, "run_arm", fake_run_arm)
    facts: dict[str, object] = {"arms": {}}
    import time as _time

    # Deadline already in the past: VISION is marked total-timeout without
    # running, and the serial sequence stops there.
    deadline = _time.monotonic() - 1
    gate._run_arms(None, ("VISION", "CACHE"), "key", UPSTREAM_URL, _limits(), deadline, facts)
    assert calls == []
    arms = cast(dict[str, dict[str, object]], facts["arms"])
    assert arms["VISION"]["failure_class"] == "total-timeout"
    assert "CACHE" not in arms


def test_sentinel_constants_are_bounded() -> None:
    assert gate.SENTINEL_SIZE == 3
    assert gate.SENTINEL_NAME == "rc8-smoke.txt"
    assert gate.OUTPUT_CAPTURE_CAP_DEFAULT <= 1_048_576
    assert gate.PRODUCT_ARMS == ("VISION", "CACHE", "BOTH")
    assert gate.MAX_EVENT_LINE_BYTES == 8 * 1024 * 1024


def test_schema_and_arm_names_are_closed() -> None:
    assert gate.SCHEMA == "slaif-real-codex-rc-qualification-v2"
    assert set(gate.PRODUCT_ARMS) == {"VISION", "CACHE", "BOTH"}
    assert gate.TOOL_ITEM_TYPES == frozenset(
        {"command_execution", "file_change", "custom_tool_call", "mcp_tool_call"}
    )
    payload = json.dumps(_valid_record(), sort_keys=True)
    assert "http://" not in payload, "facts record must carry no URLs"
    assert "127.0.0.1" not in payload or "port-18031" in payload


def test_cli_rejects_out_of_range_ceilings(tmp_path: Path) -> None:
    # The gate's own invocation must refuse out-of-range bounds (fail
    # closed) before any workdir is created.
    base = [
        sys.executable,
        str(SCRIPT),
        "--codex-bin",
        "/bin/true",
        "--adapter-wheel",
        str(tmp_path / "w.whl"),
        "--upstream-base-url-file",
        str(tmp_path / "url"),
        "--upstream-api-key-file",
        str(tmp_path / "key"),
        "--expected-codex-version",
        "0.149.0",
        "--expected-codex-sha256",
        "a" * 64,
        "--expected-wheel-sha256",
        "b" * 64,
        "--workdir",
        str(tmp_path / "fresh-workdir"),
        "--out",
        str(tmp_path / "out.json"),
    ]
    for flag, value, match in (
        ("--max-attempts", "9", "max-attempts"),
        ("--attempt-timeout", "1", "attempt-timeout"),
        ("--total-timeout", "1", "total-timeout"),
        ("--output-cap", "0", "output-cap"),
        ("--max-adapter-requests", "0", "max-adapter-requests"),
        ("--max-compiler-calls", "999", "max-compiler-calls"),
        ("--max-tool-interactions", "0", "max-tool-interactions"),
    ):
        proc = subprocess.run(
            [*base, flag, value],
            capture_output=True,
            timeout=60,
        )
        assert proc.returncode == 2, (flag, proc.stderr.decode())
        assert match in proc.stderr.decode()
    # total-timeout below attempt-timeout is refused as well.
    proc = subprocess.run(
        [*base, "--attempt-timeout", "600", "--total-timeout", "120"],
        capture_output=True,
        timeout=60,
    )
    assert proc.returncode == 2
    assert "total-timeout" in proc.stderr.decode()
    assert not (tmp_path / "fresh-workdir").exists()


def test_cli_rejects_duplicate_and_over_ceiling_arms(tmp_path: Path) -> None:
    base = [
        sys.executable,
        str(SCRIPT),
        "--codex-bin",
        "/bin/true",
        "--adapter-wheel",
        str(tmp_path / "w.whl"),
        "--upstream-base-url-file",
        str(tmp_path / "url"),
        "--upstream-api-key-file",
        str(tmp_path / "key"),
        "--expected-codex-version",
        "0.149.0",
        "--expected-codex-sha256",
        "a" * 64,
        "--expected-wheel-sha256",
        "b" * 64,
        "--workdir",
        str(tmp_path / "fresh-workdir"),
        "--out",
        str(tmp_path / "out.json"),
    ]
    for arms_arg, match in (
        ("VISION,VISION", "duplicate arms"),
        ("BOGUS", "unknown arms"),
    ):
        proc = subprocess.run(
            [*base, "--arms", arms_arg],
            capture_output=True,
            timeout=60,
        )
        assert proc.returncode == 2, (arms_arg, proc.stderr.decode())
        assert match in proc.stderr.decode()
