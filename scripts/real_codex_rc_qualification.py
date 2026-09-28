"""Bounded standalone real-Codex RC qualification (order 014-a; order 014-b
workstream A: qualification-harness gap closure for the RC candidate;
order 014-e, workstream D: RC7 qualification rerun).

Runs a GENUINE Codex CLI (exact pinned version/hash) against the candidate
adapter built from the exact pinned wheel, in the EXACT supported standalone
topology:

    disposable Codex home/repository -> 127.0.0.1:<port> Local Coding
                                      -> existing tested Qwen/vLLM endpoint

No SLAIF API Gateway is involved (gateway ingress mode ``disabled``); no
signed Gateway headers are invented. The candidate adapter runs as a
foreground repo-owned process on the loopback port and is stopped cleanly;
the host Docker engine is never used and no existing backend is touched.

Arms (serial, bounded, fail-closed):

- VISION: explicit one-image ``retain_newest`` route policy; constitution and
  compiler disabled.
- CACHE: image ``passthrough`` route semantics; constitution/compiler enabled
  with supported static single-user principal/session/repository identity.
- BOTH: both mechanisms enabled with the same static identity.
- DIRECT (optional contextual control): the same client/backend bypassing the
  adapter; never substitutes for a product arm.

Each required arm requires a fresh genuine tool-bearing Codex session that
reaches the model, completes at least one ordinary local tool interaction
(create a sentinel file through the shell tool), and exits with a bounded
expected completion. The disposable workspace carries a fixed synthetic
AGENTS.md so that a genuine project-governance envelope crosses the API
boundary; for the constitution-enabled arms this is the deterministic
trigger for the compiler/derived-cache path that must leave measurable
evidence.

Privacy law (order 014-b, workstream A, strengthened):

- The fixed synthetic prompt is delivered over STDIN using Codex 0.149's
  documented stdin mode; NO prompt substring ever appears in any process
  argv.
- NO private upstream URL appears in any process argv, including this gate's
  own invocation: the backend URL is supplied through a protected mode-0600
  caller-owned file reference (a path, not the URL) and the loopback adapter
  URL is derived from the (non-sensitive) loopback port.
- The genuine Codex provider/model/catalog settings live in the DISPOSABLE
  Codex home ``config.toml`` (mode 0600, deleted with the home), never in
  ``-c`` argv overrides.
- The generated adapter and Codex configurations contain only an ENVIRONMENT
  VARIABLE NAME for the credential (``env_key`` / ``api_key_env``) — the
  credential value itself is passed only through the child process
  environment and is never written to any file, log, or argv.
- stdout/stderr are captured with a MECHANICALLY ENFORCED byte ceiling
  WHILE THE PROCESS IS RUNNING: exceeding the cap terminates the whole
  process session (group kill), records only the capped byte COUNT and a
  sanitized failure class, and blocks the arm. Raw output is never retained
  or emitted; at most one event line is held transiently in memory for
  content-free classification and is discarded immediately.
- Tool activity is counted with a content-free event classifier over Codex
  ``--json`` JSONL event types (only ``type``/``item.type`` fields are
  read; arguments and outputs are discarded). An arm below the required
  minimum or above the configured ceiling fails closed.
- Explicit ceilings: per-attempt output bytes, attempts, per-attempt
  duration, total wall-clock, adapter requests, compiler calls, tool
  interactions, and arm count. Exceeding any ceiling fails the arm closed.

Only fixed categories, counts, statuses, version/hash, timings, and boolean
verdicts are captured. No prompt, source, tool arguments/output,
request/response body, credential, private URL, or session ID is ever
written to the output, a log, an argv, or a report. Disposable homes,
repositories, venvs, configs, caches, and raw process output are deleted
after sanitized facts are extracted; private temporary files are mode 0600
while they exist.

Opt-in gate: ordinary CI never runs this script and never depends on the
protected endpoint. The caller supplies every bound explicitly.

Exit codes: 0 all required arms PASS and protected state unchanged;
1 BLOCKED (a required arm failed or preflight failed) — the sanitized output
records the exact failure class; 2 usage error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA = "slaif-real-codex-rc-qualification-v2"
MODEL = "qwen3.8-27b"
PRODUCT_ARMS: tuple[str, ...] = ("VISION", "CACHE", "BOTH")
PROMPT = (
    "Use your shell tool to create a file named rc7-smoke.txt in the current "
    "directory. The file must contain exactly the two characters ok followed "
    "by a single newline. After creating the file, reply with exactly the "
    "single word DONE."
)
SENTINEL_NAME = "rc7-smoke.txt"
SENTINEL_SIZE = len("ok\n")
# Synthetic governance content for the disposable smoke workspace. It is the
# minimal request-side trigger for the deterministic AGENTS.md observation:
# plain prose, no credentials, no real policy, no path-like tokens, no
# quotes/backticks, so the deterministic extraction yields zero dependency
# candidates while a genuine root still crosses the API boundary.
SMOKE_AGENTS_MD = (
    "# Synthetic RC7 smoke governance\n"
    "\n"
    "This file is synthetic governance content created only for the RC7\n"
    "real-Codex qualification smoke run. It carries no repository\n"
    "instructions, no credentials, no real project policy, and no file\n"
    "references. Keep all replies bounded and change nothing except the\n"
    "explicitly requested sentinel file.\n"
)
CLIENT_ENV_KEY = "SLAIF_RC7_QUALIFICATION_KEY"
# Codex ``--json`` item types that represent one genuine model/tool
# interaction (content-free classification: only the item type is read).
TOOL_ITEM_TYPES: frozenset[str] = frozenset(
    {"command_execution", "file_change", "custom_tool_call", "mcp_tool_call"}
)
MAX_EVENT_LINE_BYTES = 8 * 1024 * 1024
OUTPUT_CAPTURE_CAP_DEFAULT = 1_048_576
REQUESTS_METRIC = "slaif_requests_total"
UPSTREAM_FAILURES_METRIC = "slaif_upstream_failures_total"
COMPILER_CALLS_METRIC = "slaif_constitution_compiler_attempts_total"
TOPOLOGY = (
    "disposable-codex-home;loopback-adapter;port-{port};existing-backend;gateway-ingress-disabled"
)
FAILURE_CLASS_PATTERN = re.compile(
    r"^(?=.{1,64}$)[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?: \([A-Za-z][A-Za-z0-9_.]*\))?$"
)


class QualificationError(RuntimeError):
    """Fail-closed qualification failure with a sanitized class label."""


class EventStreamError(ValueError):
    """The JSONL event stream is not the closed expected shape (fail closed)."""


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested in tests/test_real_codex_rc_qualification.py)
# ---------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_counter_lines(text: str, name: str) -> dict[tuple[tuple[str, str], ...], float]:
    """Parse ``name{label="value",...} number`` metric lines into
    label-tuple -> value. Minimal parser for the adapter's private metrics;
    only fixed safe label categories are retained, never content.
    """
    out: dict[tuple[tuple[str, str], ...], float] = {}
    pattern = re.compile(
        r"^(?P<name>" + re.escape(name) + r")"
        r"(?P<labels>\{[^}]*\})?\s+(?P<value>\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*$"
    )
    label_re = re.compile(r'(\w+)="([^"]*)"')
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if match is None:
            continue
        mapping: dict[str, str] = {}
        for label_match in label_re.finditer(match.group("labels") or ""):
            mapping[label_match.group(1)] = label_match.group(2)
        key = tuple((name, mapping[name]) for name in sorted(mapping))
        out[key] = float(match.group("value"))
    return out


def request_status_counts(metrics: str, endpoint: str, route: str) -> dict[str, int]:
    """status label -> total slaif_requests_total for one endpoint/route."""
    counts: dict[str, int] = {}
    for labels, value in parse_counter_lines(metrics, REQUESTS_METRIC).items():
        mapping = dict(labels)
        if mapping.get("endpoint") != endpoint or mapping.get("route") != route:
            continue
        status = str(mapping.get("status"))
        counts[status] = counts.get(status, 0) + int(value)
    return counts


def request_total(counts: dict[str, int]) -> int:
    """Total adapter requests for one endpoint/route (all statuses)."""
    return sum(counts.values())


def classify_event_line(line: str) -> int:
    """Content-free classification of one Codex ``--json`` event line.

    Returns 1 iff the line is an ``item.completed`` event whose item type is
    a genuine tool interaction (shell/file/custom-tool/MCP); 0 otherwise.
    Only the ``type`` and ``item.type`` fields are read — never arguments,
    command text, or output. Any line that is not a valid JSON object is an
    EventStreamError (fail closed): the gate requires the closed ``--json``
    event stream it counts, and unclassifiable output is never passed
    silently.
    """
    try:
        obj = json.loads(line)
    except ValueError as exc:
        raise EventStreamError("event line is not valid JSON") from exc
    if not isinstance(obj, dict):
        raise EventStreamError("event line is not a JSON object")
    if obj.get("type") != "item.completed":
        return 0
    item = obj.get("item")
    if not isinstance(item, dict):
        return 0
    return 1 if item.get("type") in TOOL_ITEM_TYPES else 0


def read_upstream_base_url(path: Path) -> str:
    """Read the backend URL from the caller's PROTECTED file reference.

    The file must be a regular (non-symlink) file, mode 0600, owned by the
    effective user, holding exactly one line: an http(s) URL. The FILE
    REFERENCE (a path) may appear in this gate's argv; the URL itself never
    does. Any deviation fails closed.
    """
    if path.is_symlink():
        raise QualificationError("upstream base-url reference is a symlink (fail closed)")
    if not path.is_file():
        raise QualificationError("upstream base-url file missing (fail closed)")
    stat = path.stat()
    if (stat.st_mode & 0o777) != 0o600:
        raise QualificationError("upstream base-url file is not mode 0600 (fail closed)")
    if stat.st_uid != os.geteuid():
        raise QualificationError("upstream base-url file is not owned by the gate user")
    lines = [entry.strip() for entry in path.read_text(encoding="utf-8").splitlines()]
    lines = [entry for entry in lines if entry]
    if len(lines) != 1:
        raise QualificationError(
            "upstream base-url file must hold exactly one non-empty line (fail closed)"
        )
    url = lines[0]
    if not re.fullmatch(r"https?://[^\s]+", url):
        raise QualificationError("upstream base-url file line is not an http(s) URL")
    return url


def build_codex_argv(codex_bin: str) -> list[str]:
    """Build the exact 0.149.0 ``codex exec`` argv (order 014-b, WS-A).

    The argv carries NO prompt (the fixed synthetic prompt is delivered over
    stdin via Codex 0.149's documented stdin mode), NO model provider, NO
    base URL, NO credential, and NO catalog reference: the provider/model/
    catalog configuration lives in the disposable Codex home ``config.toml``
    (mode 0600) and the working directory is passed through the subprocess
    ``cwd``. The only argv elements are the binary, the fixed non-sensitive
    flags, and nothing else.

    The client-side sandbox is set to ``danger-full-access`` because the
    protected host forbids the unprivileged user-namespace network setup
    that bubblewrap requires (``RTM_NEWADDR: Operation not permitted``),
    a host-level state this gate must never change. The gate's own
    boundary is the control instead: fresh disposable workspace and
    Codex home, loopback-only adapter, fixed synthetic prompt over stdin,
    no credentials or private URLs in argv, bounded attempts/timeouts,
    enforced byte ceilings, and sanitized facts only.
    """
    return [
        codex_bin,
        "exec",
        "--ephemeral",
        "-s",
        "danger-full-access",
        "--json",
    ]


def render_codex_home_config(*, provider: str, base_url: str, catalog: Path, model: str) -> str:
    """Render the disposable Codex home ``config.toml`` for one arm.

    The provider entry references the credential ONLY through an
    environment variable name (``env_key``); the credential value itself is
    supplied through the child process environment and never written here.
    ``base_url`` is the loopback adapter for product arms (non-sensitive)
    or the caller-supplied backend URL for the contextual DIRECT arm
    (loopback on the supported same-host fixture; the file is mode 0600 and
    deleted with the disposable home).
    """
    return (
        f'model = "{model}"\n'
        f'model_provider = "{provider}"\n'
        f'model_catalog_json = "{catalog}"\n'
        "\n"
        f"[model_providers.{provider}]\n"
        f'name = "SLAIF RC7 smoke"\n'
        f'base_url = "{base_url}"\n'
        f'env_key = "{CLIENT_ENV_KEY}"\n'
        'wire_api = "responses"\n'
    )


def write_codex_home_config(home: Path, text: str) -> Path:
    """Write the disposable home config atomically as mode 0600."""
    config = home / "config.toml"
    config.write_text(text, encoding="utf-8")
    config.chmod(0o600)
    return config


def render_adapter_config(
    *,
    arm: str,
    upstream_base_url: str,
    credential_env_name: str,
    adapter_port: int,
    cache_root: Path,
) -> str:
    """Render the private loopback adapter config for one arm.

    VISION: one-image retain_newest, observation/constitution off.
    CACHE: image passthrough, observation + constitution on (static
    single-user identity), compiler on.
    BOTH: one-image retain_newest plus observation + constitution on.

    The upstream credential is referenced ONLY by the environment variable
    NAME (``credential_env_name``): the rendered config contains no
    credential value, never a URL-derived secret, and the parameter is
    deliberately named for what it is — an env var name (order 014-b,
    WS-A: resolves the CodeQL clear-text-storage finding soundly by making
    the code's naming match the data, with no suppression).
    """
    if arm not in PRODUCT_ARMS:
        raise QualificationError(f"no adapter config for arm {arm!r}")
    constitution = arm in ("CACHE", "BOTH")
    image_block = (
        'max_images_per_request = 1\nimage_overflow_policy = "retain_newest"\n'
        if arm in ("VISION", "BOTH")
        else 'image_overflow_policy = "passthrough"\n'
    )
    route_flags = (
        "observation_enabled = true\nconstitution_enabled = true\n"
        if constitution
        else "observation_enabled = false\nconstitution_enabled = false\n"
    )
    identity = (
        'identity_source = "static"\n'
        'principal = "rc7-smoke-principal"\n'
        'session = "rc7-smoke-session"\n'
        'repository = "rc7-smoke-repository"\n'
        if constitution
        else ""
    )
    return f"""[server]
listen_host = "127.0.0.1"
listen_port = {adapter_port}
request_body_max_bytes = 67108864
response_body_max_bytes = 67108864
json_max_nesting_depth = 128

[gateway_ingress]
mode = "disabled"

[upstream]
base_url = "{upstream_base_url}"
api_key_env = "{credential_env_name}"
model = "{MODEL}"
connect_timeout_seconds = 10
request_timeout_seconds = 300
write_timeout_seconds = 30
pool_timeout_seconds = 10

[compiler]
enabled = {str(constitution).lower()}
api_key_env = "{credential_env_name}"
schema_version = "constitution-index-v1"
prompt_policy_version = "constitutional-rank-v2"
reasoning_effort = "low"
timeout_seconds = 120
max_attempts = 2
max_parallel_calls = 1
max_output_tokens = 3000

[cache]
backend = "filesystem"
root = "{cache_root}"
max_total_bytes = 67108864
max_entry_bytes = 65536
max_pinned_bytes = 8388608
max_entries = 4096
ttl_seconds = 3600
max_scan_entries = 4096

[constitution]
enabled = {str(constitution).lower()}
{identity}max_injected_bytes = 16384

[observation]
schema_version = "observation-v1"
policy_version = "references-v1"

[[routes]]
name = "rc7-smoke-{arm.lower()}"
model = "{MODEL}"
{image_block}{route_flags}enable_responses = true
enable_chat_completions = true
responses_tool_policy = "passthrough"

[observability]
log_level = "INFO"
log_raw_payloads = false
metrics_enabled = true
metrics_host = "127.0.0.1"
"""


def write_adapter_config(root: Path, attempt: int, text: str) -> Path:
    """Write the per-attempt adapter config atomically as mode 0600."""
    config = root / f"adapter-attempt-{attempt}.toml"
    config.write_text(text, encoding="utf-8")
    config.chmod(0o600)
    return config


def count_cache_entries(root: Path) -> int:
    if not root.is_dir():
        return 0
    return sum(1 for path in root.rglob("*") if path.is_file())


def evaluate_arm_failure(arm: str, facts: ArmFacts, limits: Limits) -> str | None:
    """Closed fail-closed arm verdict decision (pure; order 014-b, WS-A).

    Returns None (PASS) or the exact sanitized failure class. An arm below
    the required minimum tool interaction OR above ANY ceiling fails closed.
    """
    if facts.exit_status != 0:
        return "codex-exit"
    if not facts.sentinel_present or facts.sentinel_size_bytes != SENTINEL_SIZE:
        return "sentinel-missing"
    if facts.tool_interactions < 1:
        return "tool-interaction-missing"
    if facts.tool_interactions > limits.max_tool_interactions:
        return "tool-ceiling"
    if arm in PRODUCT_ARMS:
        if facts.adapter_requests_ok < 1:
            return "adapter-request-missing"
        if facts.adapter_requests_500 > 0:
            return "internal-500"
        if facts.adapter_requests_422 > 0:
            return "image-policy-422"
        if facts.upstream_failures > 0:
            return "upstream-failure"
        if facts.adapter_requests_total > limits.max_adapter_requests:
            return "requests-ceiling"
        if facts.compiler_calls > limits.max_compiler_calls:
            return "compiler-ceiling"
        if arm in ("CACHE", "BOTH") and facts.compiler_cache_entries < 1:
            return "compiler-evidence-missing"
    return None


def validate_facts_record(record: dict[str, Any]) -> None:
    """Closed-schema validation of the sanitized output record (v2).

    Any host path, prompt, body, credential-like value, or unexpected key is
    a generation failure, never a warning.
    """
    expected_top = {
        "schema",
        "created_at",
        "client",
        "wheel",
        "topology",
        "limits",
        "arms",
        "protected_state_unchanged",
        "protected_state",
        "disposable_state_removed",
        "verdict",
    }
    if set(record) != expected_top:
        raise QualificationError(f"facts record key set drift: {sorted(record)}")
    if record["schema"] != SCHEMA:
        raise QualificationError("facts record schema drift")
    if not re.fullmatch(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", str(record["created_at"])):
        raise QualificationError("facts record created_at is not RFC 3339 UTC Z")
    client = record["client"]
    if set(client) != {"version", "sha256", "binary_class"}:
        raise QualificationError("facts client key set drift")
    if not re.fullmatch(r"[0-9a-f]{64}", str(client["sha256"])):
        raise QualificationError("facts client sha256 drift")
    wheel = record["wheel"]
    if set(wheel) != {"sha256", "expected_sha256", "binding"}:
        raise QualificationError("facts wheel key set drift")
    if not re.fullmatch(r"[0-9a-f]{64}", str(wheel["sha256"])):
        raise QualificationError("facts wheel sha256 drift")
    if not re.fullmatch(r"[0-9a-f]{64}", str(wheel["expected_sha256"])):
        raise QualificationError("facts wheel expected_sha256 drift")
    if wheel["binding"] not in {"equal", "not-verified"}:
        raise QualificationError("facts wheel binding drift")
    limits = record["limits"]
    if set(limits) != {
        "output_cap_bytes",
        "max_attempts",
        "attempt_timeout_seconds",
        "total_timeout_seconds",
        "max_adapter_requests",
        "max_compiler_calls",
        "max_tool_interactions",
        "arm_count",
    }:
        raise QualificationError(f"facts limits key set drift: {sorted(limits)}")
    for key in (
        "output_cap_bytes",
        "max_attempts",
        "attempt_timeout_seconds",
        "total_timeout_seconds",
        "max_adapter_requests",
        "max_compiler_calls",
        "max_tool_interactions",
        "arm_count",
    ):
        value = limits[key]
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise QualificationError(f"facts limits {key} must be a positive integer")
    if limits["max_attempts"] > 5:
        raise QualificationError("facts limits max_attempts exceeds the 5 ceiling")
    if limits["arm_count"] > 4:
        raise QualificationError("facts limits arm_count exceeds the 4 ceiling")
    for arm, facts in record["arms"].items():
        if arm not in (*PRODUCT_ARMS, "DIRECT"):
            raise QualificationError(f"unknown arm {arm!r}")
        allowed = {
            "attempts",
            "exit_status",
            "duration_seconds",
            "sentinel_present",
            "sentinel_size_bytes",
            "adapter_requests_ok",
            "adapter_requests_500",
            "adapter_requests_422",
            "adapter_requests_total",
            "upstream_failures",
            "compiler_calls",
            "compiler_cache_entries",
            "tool_interactions",
            "stdout_bytes",
            "stderr_bytes",
            "verdict",
            "failure_class",
        }
        if set(facts) != allowed:
            raise QualificationError(f"facts {arm} key set drift: {sorted(facts)}")
        if facts["verdict"] not in {"PASS", "FAIL"}:
            raise QualificationError(f"facts {arm} verdict drift")
        if not isinstance(facts["sentinel_present"], bool):
            raise QualificationError(f"facts {arm} sentinel_present must be boolean")
        if not isinstance(facts["failure_class"], str) or not FAILURE_CLASS_PATTERN.fullmatch(
            str(facts["failure_class"])
        ):
            raise QualificationError(f"facts {arm} failure_class is not a sanitized class")
        for key in (
            "attempts",
            "duration_seconds",
            "sentinel_size_bytes",
            "adapter_requests_ok",
            "adapter_requests_500",
            "adapter_requests_422",
            "adapter_requests_total",
            "upstream_failures",
            "compiler_calls",
            "compiler_cache_entries",
            "tool_interactions",
            "stdout_bytes",
            "stderr_bytes",
        ):
            value = facts[key]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise QualificationError(f"facts {arm} {key} must be a non-negative integer")
    protected = record["protected_state"]
    if set(protected) != {"files_checked", "files_changed", "units", "ports"}:
        raise QualificationError("facts protected_state key set drift")
    if not isinstance(protected["files_checked"], int):
        raise QualificationError("facts protected_state files_checked must be integer")
    if not isinstance(protected["files_changed"], int):
        raise QualificationError("facts protected_state files_changed must be integer")
    if not isinstance(protected["units"], dict) or not isinstance(protected["ports"], dict):
        raise QualificationError("facts protected_state units/ports must be mappings")
    for key, value in protected["ports"].items():
        if not re.fullmatch(r"\d+", str(key)) or not isinstance(value, int):
            raise QualificationError("facts protected_state ports entry drift")
    if not isinstance(record["protected_state_unchanged"], bool):
        raise QualificationError("protected_state_unchanged must be boolean")
    if not isinstance(record["disposable_state_removed"], bool):
        raise QualificationError("disposable_state_removed must be boolean")
    if record["verdict"] not in {"PASS", "BLOCKED"}:
        raise QualificationError("facts verdict drift")


# ---------------------------------------------------------------------------
# Live machinery
# ---------------------------------------------------------------------------


@dataclass
class Limits:
    """Explicit mechanical ceilings (order 014-b, WS-A.5). Every value is
    enforced; exceeding any ceiling fails the affected arm closed."""

    output_cap_bytes: int
    max_attempts: int
    attempt_timeout_seconds: int
    total_timeout_seconds: int
    max_adapter_requests: int
    max_compiler_calls: int
    max_tool_interactions: int
    arm_count: int

    def as_dict(self) -> dict[str, int]:
        return {
            "output_cap_bytes": self.output_cap_bytes,
            "max_attempts": self.max_attempts,
            "attempt_timeout_seconds": self.attempt_timeout_seconds,
            "total_timeout_seconds": self.total_timeout_seconds,
            "max_adapter_requests": self.max_adapter_requests,
            "max_compiler_calls": self.max_compiler_calls,
            "max_tool_interactions": self.max_tool_interactions,
            "arm_count": self.arm_count,
        }


@dataclass
class ProtectedSnapshot:
    files: dict[str, str] = field(default_factory=dict)
    units: dict[str, str] = field(default_factory=dict)
    ports: dict[int, int] = field(default_factory=dict)


@dataclass
class CappedRunResult:
    """Bounded run outcome. Byte COUNTS only — never content."""

    returncode: int | None
    stdout_bytes: int
    stderr_bytes: int
    cap_exceeded: bool
    timed_out: bool
    event_stream_ok: bool
    tool_interactions: int


def count_listeners(port: int) -> int:
    proc = subprocess.run(
        ["ss", "-tlnH"],
        capture_output=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise QualificationError("port listener probe unavailable (fail closed)")
    count = 0
    for line in proc.stdout.decode().splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[3].rsplit(":", 1)[-1] == str(port):
            count += 1
    return count


def snapshot_protected(args: argparse.Namespace) -> ProtectedSnapshot:
    snap = ProtectedSnapshot()
    for raw in args.protect_file:
        path = Path(raw)
        if not path.is_file():
            raise QualificationError("protected file is missing (fail closed)")
        snap.files[raw] = sha256_file(path)
    for unit in args.protect_unit:
        snap.units[unit] = read_unit_state(unit)
    for port in args.protect_port:
        snap.ports[int(port)] = count_listeners(int(port))
    return snap


def diff_protected(before: ProtectedSnapshot, after: ProtectedSnapshot) -> dict[str, int]:
    files_changed = sum(1 for key, value in before.files.items() if after.files.get(key) != value)
    units_changed = sum(1 for key, value in before.units.items() if after.units.get(key) != value)
    ports_changed = sum(1 for key, value in before.ports.items() if after.ports.get(key) != value)
    return {
        "files_changed": files_changed,
        "units_changed": units_changed,
        "ports_changed": ports_changed,
    }


def read_unit_state(unit: str) -> str:
    """Return the exact ``systemctl --user is-active`` state string.

    ``is-active`` exits non-zero for LEGITIMATE non-active states (3 =
    inactive/failed, 4 = unit not present — both still print their
    state), so the non-empty state string is the readability criterion;
    empty output (missing user bus, malformed query) fails closed.
    """
    proc = subprocess.run(
        ["systemctl", "--user", "is-active", unit],
        capture_output=True,
        timeout=30,
    )
    state = proc.stdout.decode().strip()
    if not state:
        raise QualificationError(f"protected unit state unreadable: {unit}")
    return state


def check_port_free(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(2.0)
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            raise QualificationError(f"adapter port {port} is not free (fail closed)")


def probe_upstream(base_url: str, credential: str, model: str) -> None:
    origin = base_url.rstrip("/")
    if origin.endswith("/v1"):
        origin = origin[: -len("/v1")]
    health = f"{origin}/health"
    models = f"{origin}/v1/models"
    try:
        with urllib.request.urlopen(health, timeout=10) as response:
            if response.status != 200:
                raise QualificationError("upstream /health is not 200")
        request = urllib.request.Request(models, headers={"Authorization": f"Bearer {credential}"})
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status != 200:
                raise QualificationError("upstream /v1/models is not 200")
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        raise QualificationError(f"upstream probe failed (HTTP {exc.code})") from None
    except Exception as exc:  # noqa: BLE001 - sanitized fail-closed class
        raise QualificationError(f"upstream probe failed ({type(exc).__name__})") from None
    names = [entry.get("id") for entry in payload.get("data", [])]
    if model not in names:
        raise QualificationError("upstream does not serve the expected model")


def build_model_catalog(codex_bin: str, home: Path, out: Path) -> None:
    proc = subprocess.run(
        [codex_bin, "debug", "models", "--bundled"],
        env={**os.environ, "CODEX_HOME": str(home)},
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise QualificationError("bundled model catalog unavailable")
    catalog = json.loads(proc.stdout.decode())
    models = catalog.get("models")
    if not isinstance(models, list) or not models:
        raise QualificationError("bundled model catalog is empty")
    template = next((entry for entry in models if entry.get("slug") == "gpt-5.4"), None)
    if template is None:
        template = models[0]
    template["slug"] = MODEL
    template["display_name"] = MODEL
    template["description"] = "RC7 smoke qualification model"
    out.write_text(json.dumps({"models": [template]}))
    out.chmod(0o600)


def http_get(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=10) as response:
        return bytes(response.read(1_048_576))


def wait_http(url: str, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    last_error = "timeout"
    while time.monotonic() < deadline:
        try:
            http_get(url)
            return
        except Exception as exc:  # noqa: BLE001 - retry loop
            last_error = type(exc).__name__
            time.sleep(0.5)
    raise QualificationError(f"adapter did not become ready ({last_error})")


def _kill_process_group(proc: subprocess.Popen[bytes], grace_seconds: float = 5.0) -> None:
    """Terminate the whole process session (the gate always start_new_session)."""
    if proc.poll() is not None:
        return
    try:
        pgid = os.getpgid(proc.pid)
    except OSError:
        return
    try:
        os.killpg(pgid, signal.SIGTERM)
    except OSError:
        return
    deadline = time.monotonic() + grace_seconds
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            return
        time.sleep(0.05)
    if proc.poll() is None:
        try:
            os.killpg(pgid, signal.SIGKILL)
        except OSError:
            pass


def run_capped_process(
    *,
    argv: list[str],
    env: dict[str, str],
    stdin_text: str,
    cwd: Path,
    output_cap_bytes: int,
    timeout_seconds: float,
) -> CappedRunResult:
    """Run a child process with a MECHANICALLY ENFORCED live byte ceiling
    (order 014-b, WS-A.4) and content-free event counting (WS-A.5).

    - stdout+stderr bytes are counted as they stream; the FIRST byte beyond
      ``output_cap_bytes`` terminates the entire process session (group
      SIGTERM, then SIGKILL) and the recorded byte counts are the capped
      values. No output content is retained or emitted.
    - stdout lines are classified content-free (event type only) for tool
      interaction counting; a line over MAX_EVENT_LINE_BYTES, or a line that
      is not a valid JSON object, marks the event stream failed (fail
      closed) and also terminates the session.
    - ``timeout_seconds`` bounds the attempt; expiry terminates the session.
    """
    proc = subprocess.Popen(
        argv,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=str(cwd),
        start_new_session=True,
    )
    assert proc.stdin is not None
    assert proc.stdout is not None
    assert proc.stderr is not None
    state: dict[str, Any] = {
        "total": 0,
        "stdout": 0,
        "stderr": 0,
        "tool_interactions": 0,
        "cap": False,
        "event_ok": True,
        "killer_armed": False,
        "killed": False,
    }
    state_lock = threading.Lock()

    def kill_session() -> None:
        with state_lock:
            if state["killer_armed"]:
                return
            state["killer_armed"] = True
            state["killed"] = True
        _kill_process_group(proc)

    def read_stream(stream: Any, counter_key: str, classify: bool) -> None:
        partial = b""
        while True:
            try:
                chunk = stream.read(65536)
            except (OSError, ValueError):
                break
            if not chunk:
                break
            with state_lock:
                state[counter_key] += len(chunk)
                state["total"] += len(chunk)
                exceeded = state["total"] > output_cap_bytes
                if exceeded:
                    state["cap"] = True
            if exceeded:
                kill_session()
            if classify and not state["cap"]:
                partial += chunk
                while b"\n" in partial:
                    line, partial = partial.split(b"\n", 1)
                    if len(line) > MAX_EVENT_LINE_BYTES:
                        state["event_ok"] = False
                        kill_session()
                        break
                    try:
                        state["tool_interactions"] += classify_event_line(line.decode("utf-8"))
                    except EventStreamError:
                        state["event_ok"] = False
                        kill_session()
                        break
        if classify and partial and not state["killed"]:
            # A normally terminated JSONL stream ends on a newline;
            # unterminated trailing bytes from a GATE-TERMINATED session are
            # a kill artifact and are discarded, never classified.
            if len(partial) > MAX_EVENT_LINE_BYTES:
                state["event_ok"] = False
            else:
                try:
                    state["tool_interactions"] += classify_event_line(partial.decode("utf-8"))
                except EventStreamError:
                    state["event_ok"] = False

    stdout_thread = threading.Thread(
        target=read_stream, args=(proc.stdout, "stdout", True), daemon=True
    )
    stderr_thread = threading.Thread(
        target=read_stream, args=(proc.stderr, "stderr", False), daemon=True
    )
    stdout_thread.start()
    stderr_thread.start()
    timed_out = False
    try:
        proc.stdin.write(stdin_text.encode("utf-8"))
        proc.stdin.close()
    except (BrokenPipeError, OSError):
        pass
    try:
        proc.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        with state_lock:
            state["killed"] = True
        kill_session()
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            pass
    stdout_thread.join(timeout=30)
    stderr_thread.join(timeout=30)
    with state_lock:
        stdout_bytes = min(state["stdout"], output_cap_bytes)
        stderr_bytes = min(state["stderr"], output_cap_bytes)
        cap = state["cap"]
        event_ok = state["event_ok"]
        tool_interactions = int(state["tool_interactions"])
    return CappedRunResult(
        returncode=proc.returncode,
        stdout_bytes=stdout_bytes,
        stderr_bytes=stderr_bytes,
        cap_exceeded=cap,
        timed_out=timed_out,
        event_stream_ok=event_ok,
        tool_interactions=tool_interactions,
    )


class AdapterProcess:
    """Foreground repo-owned adapter instance on the loopback port."""

    def __init__(self, venv_python: Path, config: Path, log: Path, credential: str) -> None:
        log.touch()
        log.chmod(0o600)
        self._log_handle = log.open("wb")
        self._proc = subprocess.Popen(
            [str(venv_python), "-m", "slaif_local_coding", "--config", str(config)],
            stdout=self._log_handle,
            stderr=subprocess.STDOUT,
            env={**os.environ, CLIENT_ENV_KEY: credential},
            start_new_session=True,
        )

    @property
    def pid(self) -> int:
        return self._proc.pid

    def stop(self) -> None:
        _kill_process_group(self._proc)
        try:
            self._proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            pass
        self._log_handle.close()


@dataclass
class ArmFacts:
    arm: str
    attempts: int = 0
    exit_status: int | None = None
    duration_seconds: int = 0
    sentinel_present: bool = False
    sentinel_size_bytes: int = 0
    adapter_requests_ok: int = 0
    adapter_requests_500: int = 0
    adapter_requests_422: int = 0
    adapter_requests_total: int = 0
    upstream_failures: int = 0
    compiler_calls: int = 0
    compiler_cache_entries: int = 0
    tool_interactions: int = 0
    stdout_bytes: int = 0
    stderr_bytes: int = 0
    verdict: str = "FAIL"
    failure_class: str = "not-run"

    def as_dict(self) -> dict[str, Any]:
        return {
            "attempts": self.attempts,
            "exit_status": self.exit_status,
            "duration_seconds": self.duration_seconds,
            "sentinel_present": self.sentinel_present,
            "sentinel_size_bytes": self.sentinel_size_bytes,
            "adapter_requests_ok": self.adapter_requests_ok,
            "adapter_requests_500": self.adapter_requests_500,
            "adapter_requests_422": self.adapter_requests_422,
            "adapter_requests_total": self.adapter_requests_total,
            "upstream_failures": self.upstream_failures,
            "compiler_calls": self.compiler_calls,
            "compiler_cache_entries": self.compiler_cache_entries,
            "tool_interactions": self.tool_interactions,
            "stdout_bytes": self.stdout_bytes,
            "stderr_bytes": self.stderr_bytes,
            "verdict": self.verdict,
            "failure_class": self.failure_class,
        }


def _prepare_workspace(root: Path, workspace: Path) -> None:
    workspace.mkdir(parents=True, mode=0o700)
    (workspace / "README.md").write_text("rc7 smoke workspace\n")
    (workspace / "AGENTS.md").write_text(SMOKE_AGENTS_MD)
    subprocess.run(["git", "init", "-q", str(workspace)], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(workspace),
            "-c",
            "user.name=RC7 Smoke",
            "-c",
            "user.email=rc7-smoke@example.invalid",
            "add",
            "README.md",
            "AGENTS.md",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(workspace),
            "-c",
            "user.name=RC7 Smoke",
            "-c",
            "user.email=rc7-smoke@example.invalid",
            "commit",
            "-q",
            "-m",
            "Synthetic smoke workspace",
        ],
        check=True,
        capture_output=True,
    )


def _run_arms(
    args: argparse.Namespace,
    required: tuple[str, ...],
    credential: str,
    upstream_base_url: str,
    limits: Limits,
    deadline: float,
    facts: dict[str, Any],
) -> None:
    """Serial arm runner with the fail-closed crash boundary.

    An unexpected tooling failure inside an arm is recorded as a sanitized
    exception class (privacy law: never raw output) and stops the serial
    sequence at the first failed required product arm; the closed-schema
    facts dictionary stays the single evidence channel. The total wall-clock
    ceiling is enforced between attempts: once the deadline is reached, the
    remaining arms fail closed with the ``total-timeout`` class.
    """
    for arm in required:
        arm_facts = ArmFacts(arm=arm)
        if time.monotonic() >= deadline:
            arm_facts.verdict = "FAIL"
            arm_facts.failure_class = "total-timeout"
            facts["arms"][arm] = arm_facts.as_dict()
            if arm in PRODUCT_ARMS:
                break
            continue
        try:
            run_arm(args, arm, credential, upstream_base_url, limits, arm_facts)
        except Exception as exc:  # noqa: BLE001 - fail-closed gate boundary
            arm_facts.verdict = "FAIL"
            arm_facts.failure_class = f"gate-crash ({type(exc).__name__})"
        facts["arms"][arm] = arm_facts.as_dict()
        if arm in PRODUCT_ARMS and arm_facts.verdict != "PASS":
            break


# Failure classes that are deterministic (a ceiling was hit or the stream was
# malformed): retrying the attempt cannot succeed, so the attempt loop stops.
NON_RETRIABLE = frozenset(
    {
        "output-cap-exceeded",
        "attempt-timeout",
        "event-stream",
        "tool-ceiling",
        "requests-ceiling",
        "compiler-ceiling",
        "total-timeout",
        "gate-timeout",
    }
)


def run_arm(
    args: argparse.Namespace,
    arm: str,
    credential: str,
    upstream_base_url: str,
    limits: Limits,
    facts_out: ArmFacts,
) -> None:
    provider = f"slaif_rc7_{arm.lower()}"
    base_url = (
        f"http://127.0.0.1:{args.adapter_port}/v1" if arm in PRODUCT_ARMS else upstream_base_url
    )
    root = Path(args.workdir) / arm.lower()
    workspace = root / "workspace"
    home = root / "codex-home"
    cache_root = root / "cache"
    for path in (home, cache_root):
        path.mkdir(parents=True, mode=0o700)
    _prepare_workspace(root, workspace)
    catalog = root / "model-catalog.json"
    build_model_catalog(args.codex_bin, home, catalog)
    # Order 014-b, WS-A.3: the provider/model/catalog configuration lives in
    # the disposable Codex home (mode 0600, deleted with the home), never in
    # argv.
    write_codex_home_config(
        home,
        render_codex_home_config(
            provider=provider, base_url=base_url, catalog=catalog, model=MODEL
        ),
    )

    venv: Path | None = None
    if arm in PRODUCT_ARMS:
        venv = root / "venv"
        proc = subprocess.run(
            [args.uv_bin, "venv", "--python", "3.12", "--allow-existing", str(venv)],
            capture_output=True,
            timeout=600,
        )
        if proc.returncode != 0:
            facts_out.failure_class = "venv-creation"
            return
        install = subprocess.run(
            [
                args.uv_bin,
                "pip",
                "install",
                "--python",
                str(venv / "bin" / "python"),
                "--no-cache",
                str(args.adapter_wheel),
            ],
            capture_output=True,
            timeout=600,
        )
        if install.returncode != 0:
            facts_out.failure_class = "wheel-install"
            return

    argv = build_codex_argv(str(args.codex_bin))
    env = {**os.environ, "CODEX_HOME": str(home), CLIENT_ENV_KEY: credential}
    last_failure = "codex-exit"
    for attempt in range(1, limits.max_attempts + 1):
        facts_out.attempts = attempt
        sentinel = workspace / SENTINEL_NAME
        sentinel.unlink(missing_ok=True)
        adapter: AdapterProcess | None = None
        try:
            if arm in PRODUCT_ARMS and venv is not None:
                check_port_free(args.adapter_port)
                config = write_adapter_config(
                    root,
                    attempt,
                    render_adapter_config(
                        arm=arm,
                        upstream_base_url=upstream_base_url,
                        credential_env_name=CLIENT_ENV_KEY,
                        adapter_port=args.adapter_port,
                        cache_root=cache_root,
                    ),
                )
                log = root / f"adapter-attempt-{attempt}.log"
                adapter = AdapterProcess(venv / "bin/python", config, log, credential)
                wait_http(f"http://127.0.0.1:{args.adapter_port}/healthz", args.ready_timeout)
                wait_http(f"http://127.0.0.1:{args.adapter_port}/readyz", args.ready_timeout)

            started = time.monotonic()
            result = run_capped_process(
                argv=argv,
                env=env,
                stdin_text=PROMPT,
                cwd=workspace,
                output_cap_bytes=limits.output_cap_bytes,
                timeout_seconds=limits.attempt_timeout_seconds,
            )
            facts_out.exit_status = result.returncode
            facts_out.duration_seconds = int(time.monotonic() - started)
            facts_out.stdout_bytes = result.stdout_bytes
            facts_out.stderr_bytes = result.stderr_bytes
            facts_out.tool_interactions = result.tool_interactions
            facts_out.sentinel_present = sentinel.is_file()
            facts_out.sentinel_size_bytes = (
                sentinel.stat().st_size if facts_out.sentinel_present else 0
            )
            if facts_out.sentinel_present and facts_out.sentinel_size_bytes != SENTINEL_SIZE:
                facts_out.sentinel_present = False

            route = f"rc7-smoke-{arm.lower()}"
            if arm in PRODUCT_ARMS and adapter is not None:
                metrics = http_get(f"http://127.0.0.1:{args.adapter_port}/metrics").decode()
                counts = request_status_counts(metrics, "/v1/responses", route)
                facts_out.adapter_requests_ok = counts.get("200", 0)
                facts_out.adapter_requests_500 = counts.get("500", 0)
                facts_out.adapter_requests_422 = counts.get("422", 0)
                facts_out.adapter_requests_total = request_total(counts)
                # The adapter process is fresh per attempt, so absolute
                # counter values are arm-attempt scoped.
                facts_out.upstream_failures = int(
                    sum(parse_counter_lines(metrics, UPSTREAM_FAILURES_METRIC).values())
                )
                facts_out.compiler_calls = int(
                    sum(parse_counter_lines(metrics, COMPILER_CALLS_METRIC).values())
                )
                if arm in ("CACHE", "BOTH"):
                    facts_out.compiler_cache_entries = count_cache_entries(cache_root)
        except subprocess.TimeoutExpired:
            facts_out.exit_status = None
            facts_out.verdict = "FAIL"
            facts_out.failure_class = "gate-timeout"
            return
        except QualificationError:
            facts_out.exit_status = None
            facts_out.verdict = "FAIL"
            facts_out.failure_class = "qualification-error"
            return
        finally:
            if adapter is not None:
                adapter.stop()
                check_port_free(args.adapter_port)

        # Mechanical enforcement failures are recorded with their exact
        # sanitized class and stop the attempt loop (no retry can succeed).
        if result.cap_exceeded:
            facts_out.verdict = "FAIL"
            facts_out.failure_class = "output-cap-exceeded"
            last_failure = facts_out.failure_class
            break
        if result.timed_out:
            facts_out.verdict = "FAIL"
            facts_out.failure_class = "attempt-timeout"
            last_failure = facts_out.failure_class
            break
        if not result.event_stream_ok:
            facts_out.verdict = "FAIL"
            facts_out.failure_class = "event-stream"
            last_failure = facts_out.failure_class
            break

        failure = evaluate_arm_failure(arm, facts_out, limits)
        if failure is None:
            facts_out.verdict = "PASS"
            facts_out.failure_class = "none"
            return
        facts_out.verdict = "FAIL"
        facts_out.failure_class = failure
        last_failure = failure
        if failure in NON_RETRIABLE:
            break
    if facts_out.verdict != "PASS":
        facts_out.failure_class = last_failure


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-bin", required=True)
    parser.add_argument("--adapter-wheel", required=True, type=Path)
    parser.add_argument(
        "--upstream-base-url-file",
        required=True,
        type=Path,
        help=(
            "protected mode-0600 caller-owned file holding exactly one line: "
            "the backend URL. The file reference (path) is in this argv; the "
            "URL itself never is (order 014-b, WS-A.3)."
        ),
    )
    parser.add_argument("--upstream-api-key-file", required=True, type=Path)
    parser.add_argument("--expected-codex-version", required=True)
    parser.add_argument("--expected-codex-sha256", required=True)
    parser.add_argument("--expected-wheel-sha256", required=True)
    parser.add_argument("--adapter-port", type=int, default=18031)
    parser.add_argument("--workdir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--arms", default=",".join(PRODUCT_ARMS))
    parser.add_argument("--include-direct", action="store_true")
    # Order 014-b, WS-A.5: explicit mechanical ceilings (all enforced).
    parser.add_argument(
        "--max-attempts", type=int, default=2, help="per-arm attempt ceiling (1..5)"
    )
    parser.add_argument(
        "--attempt-timeout",
        type=float,
        default=600.0,
        help="per-attempt wall-clock ceiling in seconds (30..3600)",
    )
    parser.add_argument(
        "--total-timeout",
        type=float,
        default=5400.0,
        help="total wall-clock ceiling for all arms in seconds",
    )
    parser.add_argument(
        "--output-cap",
        type=int,
        default=OUTPUT_CAPTURE_CAP_DEFAULT,
        help="live stdout+stderr byte ceiling per attempt (1..16 MiB)",
    )
    parser.add_argument(
        "--max-adapter-requests",
        type=int,
        default=64,
        help="per-arm adapter request ceiling, all statuses (1..1024)",
    )
    parser.add_argument(
        "--max-compiler-calls",
        type=int,
        default=4,
        help="per-arm compiler attempt ceiling (1..64)",
    )
    parser.add_argument(
        "--max-tool-interactions",
        type=int,
        default=8,
        help="per-arm genuine tool interaction ceiling, >=1 required (1..256)",
    )
    parser.add_argument("--ready-timeout", type=float, default=120.0)
    parser.add_argument("--uv-bin", default="uv")
    parser.add_argument("--protect-file", action="append", default=[])
    parser.add_argument("--protect-unit", action="append", default=[])
    parser.add_argument("--protect-port", action="append", default=[])
    args = parser.parse_args()

    arms = tuple(entry.strip().upper() for entry in args.arms.split(",") if entry.strip())
    if not arms:
        parser.error("no arms selected")
    unknown = set(arms) - set(PRODUCT_ARMS)
    if unknown:
        parser.error(f"unknown arms: {sorted(unknown)}")
    if len(arms) != len(set(arms)):
        parser.error("duplicate arms")
    required = arms + (("DIRECT",) if args.include_direct else ())
    if len(required) > 4:
        parser.error("arm ceiling exceeded (max 4: three product arms + DIRECT)")

    # Explicit ceiling validation (fail closed on any out-of-range bound).
    if not 1 <= args.max_attempts <= 5:
        parser.error("--max-attempts must be within 1..5")
    if not 30 <= args.attempt_timeout <= 3600:
        parser.error("--attempt-timeout must be within 30..3600 seconds")
    if not 60 <= args.total_timeout <= 21600:
        parser.error("--total-timeout must be within 60..21600 seconds")
    if args.total_timeout < args.attempt_timeout:
        parser.error("--total-timeout must be >= --attempt-timeout")
    if not 1 <= args.output_cap <= 16 * 1024 * 1024:
        parser.error("--output-cap must be within 1..16 MiB")
    if not 1 <= args.max_adapter_requests <= 1024:
        parser.error("--max-adapter-requests must be within 1..1024")
    if not 1 <= args.max_compiler_calls <= 64:
        parser.error("--max-compiler-calls must be within 1..64")
    if not 1 <= args.max_tool_interactions <= 256:
        parser.error("--max-tool-interactions must be within 1..256")

    limits = Limits(
        output_cap_bytes=args.output_cap,
        max_attempts=args.max_attempts,
        attempt_timeout_seconds=int(args.attempt_timeout),
        total_timeout_seconds=int(args.total_timeout),
        max_adapter_requests=args.max_adapter_requests,
        max_compiler_calls=args.max_compiler_calls,
        max_tool_interactions=args.max_tool_interactions,
        arm_count=len(required),
    )

    workdir = args.workdir
    if workdir.exists():
        parser.error("workdir must not exist (fresh disposable boundary)")
    workdir.mkdir(parents=True, mode=0o700)

    facts: dict[str, Any] = {
        "schema": SCHEMA,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "client": {
            "version": "unknown",
            "sha256": "0" * 64,
            "binary_class": "standalone-release",
        },
        "wheel": {
            "sha256": "0" * 64,
            "expected_sha256": args.expected_wheel_sha256,
            "binding": "not-verified",
        },
        "topology": TOPOLOGY.format(port=args.adapter_port),
        "limits": limits.as_dict(),
        "arms": {},
        "protected_state_unchanged": False,
        "protected_state": {"files_checked": 0, "files_changed": 0, "units": {}, "ports": {}},
        "disposable_state_removed": False,
        "verdict": "BLOCKED",
    }
    verdict = "BLOCKED"
    try:
        # --- Preflight (fail closed) -------------------------------------
        codex_bin = Path(args.codex_bin)
        if not codex_bin.is_file():
            raise QualificationError("codex binary missing")
        codex_sha = sha256_file(codex_bin)
        if codex_sha != args.expected_codex_sha256:
            raise QualificationError("codex binary hash mismatch")
        version = subprocess.run([str(codex_bin), "--version"], capture_output=True, timeout=60)
        version_text = version.stdout.decode() + version.stderr.decode()
        if args.expected_codex_version not in version_text:
            raise QualificationError("codex version mismatch")
        facts["client"]["version"] = args.expected_codex_version
        facts["client"]["sha256"] = codex_sha

        if not args.adapter_wheel.is_file():
            raise QualificationError("adapter wheel missing")
        wheel_sha = sha256_file(args.adapter_wheel)
        facts["wheel"]["sha256"] = wheel_sha
        if wheel_sha != args.expected_wheel_sha256:
            raise QualificationError("wheel hash does not equal the expected RC wheel")
        facts["wheel"]["binding"] = "equal"

        if not args.upstream_api_key_file.is_file():
            raise QualificationError("upstream key file missing")
        credential = args.upstream_api_key_file.read_text().strip()
        if not credential:
            raise QualificationError("upstream key file empty")

        # Order 014-b, WS-A.3: the backend URL arrives through the protected
        # 0600 file reference — never through this gate's argv.
        upstream_base_url = read_upstream_base_url(args.upstream_base_url_file)

        check_port_free(args.adapter_port)
        probe_upstream(upstream_base_url, credential, MODEL)

        before = snapshot_protected(args)
        facts["protected_state"]["files_checked"] = len(before.files)
        facts["protected_state"]["units"] = dict(before.units)
        facts["protected_state"]["ports"] = {str(key): value for key, value in before.ports.items()}

        # --- Arms (serial, total wall-clock ceiling enforced) -------------
        deadline = time.monotonic() + limits.total_timeout_seconds
        _run_arms(args, required, credential, upstream_base_url, limits, deadline, facts)

        # --- Protected state after ----------------------------------------
        after = snapshot_protected(args)
        diff = diff_protected(before, after)
        facts["protected_state"]["files_changed"] = diff["files_changed"]
        facts["protected_state_unchanged"] = (
            diff["files_changed"] == 0 and diff["units_changed"] == 0 and diff["ports_changed"] == 0
        )
        # Required product arms only: a contextual DIRECT control is
        # recorded but never blocks the verdict, and subset runs must not
        # reference arms they deliberately did not run.
        required_ok = all(facts["arms"][arm]["verdict"] == "PASS" for arm in arms)
        verdict = "PASS" if required_ok and facts["protected_state_unchanged"] else "BLOCKED"
    except QualificationError:
        verdict = "BLOCKED"
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        facts["disposable_state_removed"] = not workdir.exists()

    facts["verdict"] = verdict
    validate_facts_record(facts)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(facts, indent=2, sort_keys=True) + "\n")
    args.out.chmod(0o600)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
