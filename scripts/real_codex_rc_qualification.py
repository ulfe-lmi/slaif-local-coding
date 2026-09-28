"""Bounded standalone real-Codex RC qualification (order 014-a, workstream C).

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
expected completion.

Privacy law: only fixed categories, counts, statuses, version/hash, timings,
and boolean verdicts are captured. No prompt, source, tool arguments/output,
request/response body, credential, private URL, or session ID is ever written
to the output, a log, an argv, or a report. Disposable homes, repositories,
venvs, configs, caches, and raw process output are deleted after sanitized
facts are extracted; private temporary files are mode 0600 while they exist.
Credentials reach child processes only through protected environment
variables read from the protected file reference supplied by the caller.

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
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA = "slaif-real-codex-rc-qualification-v1"
MODEL = "qwen3.8-27b"
PRODUCT_ARMS: tuple[str, ...] = ("VISION", "CACHE", "BOTH")
PROMPT = (
    "Use your shell tool to create a file named rc3-smoke.txt in the current "
    "directory. The file must contain exactly the two characters ok followed "
    "by a single newline. After creating the file, reply with exactly the "
    "single word DONE."
)
SENTINEL_NAME = "rc3-smoke.txt"
SENTINEL_SIZE = len("ok\n")
CLIENT_ENV_KEY = "SLAIF_RC3_QUALIFICATION_KEY"
OUTPUT_CAPTURE_CAP = 1_048_576
REQUESTS_METRIC = "slaif_requests_total"
UPSTREAM_FAILURES_METRIC = "slaif_upstream_failures_total"


class QualificationError(RuntimeError):
    """Fail-closed qualification failure with a sanitized class label."""


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


def build_codex_argv(
    codex_bin: str,
    workspace: Path,
    catalog: Path,
    provider: str,
    base_url: str,
) -> list[str]:
    """Build the exact 0.149.0 ``codex exec`` argv.

    The credential is NEVER an argv element: the provider references an
    environment variable name (``env_key``) whose value is supplied only
    through the child process environment.
    """
    provider_spec = (
        f'{{name="SLAIF RC3 smoke",base_url="{base_url}",'
        f'env_key="{CLIENT_ENV_KEY}",wire_api="responses"}}'
    )
    return [
        codex_bin,
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "-C",
        str(workspace),
        "-m",
        MODEL,
        "-c",
        f"model_provider={provider}",
        "-c",
        f"model_providers.{provider}={provider_spec}",
        "-c",
        f'model_catalog_json="{catalog}"',
        PROMPT,
    ]


def render_adapter_config(
    *,
    arm: str,
    upstream_base_url: str,
    upstream_api_key_env: str,
    adapter_port: int,
    cache_root: Path,
) -> str:
    """Render the private loopback adapter config for one arm.

    VISION: one-image retain_newest, observation/constitution off.
    CACHE: image passthrough, observation + constitution on (static
    single-user identity), compiler on.
    BOTH: one-image retain_newest plus observation + constitution on.
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
        'principal = "rc3-smoke-principal"\n'
        'session = "rc3-smoke-session"\n'
        'repository = "rc3-smoke-repository"\n'
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
api_key_env = "{upstream_api_key_env}"
model = "{MODEL}"
connect_timeout_seconds = 10
request_timeout_seconds = 300
write_timeout_seconds = 30
pool_timeout_seconds = 10

[compiler]
enabled = {str(constitution).lower()}
api_key_env = "{upstream_api_key_env}"
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
name = "rc3-smoke-{arm.lower()}"
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


def count_cache_entries(root: Path) -> int:
    if not root.is_dir():
        return 0
    return sum(1 for path in root.rglob("*") if path.is_file())


def validate_facts_record(record: dict[str, Any]) -> None:
    """Closed-schema validation of the sanitized output record.

    Any host path, prompt, body, credential-like value, or unexpected key is
    a generation failure, never a warning.
    """
    expected_top = {
        "schema",
        "created_at",
        "client",
        "wheel",
        "topology",
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
    if wheel["binding"] not in {"equal", "not-verified"}:
        raise QualificationError("facts wheel binding drift")
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
            "upstream_failures",
            "compiler_cache_entries",
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
class ProtectedSnapshot:
    files: dict[str, str] = field(default_factory=dict)
    units: dict[str, str] = field(default_factory=dict)
    ports: dict[int, int] = field(default_factory=dict)


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


def probe_upstream(base_url: str, api_key: str, model: str) -> None:
    origin = base_url.rstrip("/")
    if origin.endswith("/v1"):
        origin = origin[: -len("/v1")]
    health = f"{origin}/health"
    models = f"{origin}/v1/models"
    try:
        with urllib.request.urlopen(health, timeout=10) as response:
            if response.status != 200:
                raise QualificationError("upstream /health is not 200")
        request = urllib.request.Request(models, headers={"Authorization": f"Bearer {api_key}"})
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
    template["description"] = "RC3 smoke qualification model"
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


class AdapterProcess:
    """Foreground repo-owned adapter instance on the loopback port."""

    def __init__(self, venv_python: Path, config: Path, log: Path, api_key: str) -> None:
        log.touch()
        log.chmod(0o600)
        self._log_handle = log.open("wb")
        self._proc = subprocess.Popen(
            [str(venv_python), "-m", "slaif_local_coding", "--config", str(config)],
            stdout=self._log_handle,
            stderr=subprocess.STDOUT,
            env={**os.environ, CLIENT_ENV_KEY: api_key},
            start_new_session=True,
        )

    @property
    def pid(self) -> int:
        return self._proc.pid

    def stop(self) -> None:
        if self._proc.poll() is None:
            os.killpg(os.getpgid(self._proc.pid), signal.SIGTERM)
            try:
                self._proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(self._proc.pid), signal.SIGKILL)
                self._proc.wait(timeout=30)
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
    upstream_failures: int = 0
    compiler_cache_entries: int = 0
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
            "upstream_failures": self.upstream_failures,
            "compiler_cache_entries": self.compiler_cache_entries,
            "stdout_bytes": self.stdout_bytes,
            "stderr_bytes": self.stderr_bytes,
            "verdict": self.verdict,
            "failure_class": self.failure_class,
        }


def _prepare_workspace(root: Path, workspace: Path) -> None:
    workspace.mkdir(parents=True, mode=0o700)
    (workspace / "README.md").write_text("rc3 smoke workspace\n")
    subprocess.run(["git", "init", "-q", str(workspace)], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(workspace),
            "-c",
            "user.name=RC3 Smoke",
            "-c",
            "user.email=rc3-smoke@example.invalid",
            "add",
            "README.md",
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
            "user.name=RC3 Smoke",
            "-c",
            "user.email=rc3-smoke@example.invalid",
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
    api_key: str,
    facts: dict[str, Any],
) -> None:
    """Serial arm runner with the fail-closed crash boundary.

    An unexpected tooling failure inside an arm is recorded as a sanitized
    exception class (privacy law: never raw output) and stops the serial
    sequence at the first failed required product arm; the closed-schema
    facts dictionary stays the single evidence channel."""
    for arm in required:
        arm_facts = ArmFacts(arm=arm)
        try:
            run_arm(args, arm, api_key, arm_facts)
        except Exception as exc:  # noqa: BLE001 - fail-closed gate boundary
            arm_facts.verdict = "FAIL"
            arm_facts.failure_class = f"gate-crash ({type(exc).__name__})"
        facts["arms"][arm] = arm_facts.as_dict()
        if arm in PRODUCT_ARMS and arm_facts.verdict != "PASS":
            break


def run_arm(args: argparse.Namespace, arm: str, api_key: str, facts_out: ArmFacts) -> None:
    provider = f"slaif_rc3_{arm.lower()}"
    base_url = (
        f"http://127.0.0.1:{args.adapter_port}/v1"
        if arm in PRODUCT_ARMS
        else args.upstream_base_url
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

    argv = build_codex_argv(str(args.codex_bin), workspace, catalog, provider, base_url)
    env = {**os.environ, "CODEX_HOME": str(home), CLIENT_ENV_KEY: api_key}
    for attempt in range(1, args.max_attempts + 1):
        facts_out.attempts = attempt
        sentinel = workspace / SENTINEL_NAME
        sentinel.unlink(missing_ok=True)
        adapter: AdapterProcess | None = None
        try:
            if arm in PRODUCT_ARMS and venv is not None:
                check_port_free(args.adapter_port)
                config = root / f"adapter-attempt-{attempt}.toml"
                config.write_text(
                    render_adapter_config(
                        arm=arm,
                        upstream_base_url=args.upstream_base_url,
                        upstream_api_key_env=CLIENT_ENV_KEY,
                        adapter_port=args.adapter_port,
                        cache_root=cache_root,
                    )
                )
                config.chmod(0o600)
                log = root / f"adapter-attempt-{attempt}.log"
                adapter = AdapterProcess(venv / "bin" / "python", config, log, api_key)
                wait_http(f"http://127.0.0.1:{args.adapter_port}/healthz", args.ready_timeout)
                wait_http(f"http://127.0.0.1:{args.adapter_port}/readyz", args.ready_timeout)

            started = time.monotonic()
            proc = subprocess.run(argv, env=env, capture_output=True, timeout=args.attempt_timeout)
            facts_out.exit_status = proc.returncode
            facts_out.duration_seconds = int(time.monotonic() - started)
            facts_out.stdout_bytes = min(len(proc.stdout), OUTPUT_CAPTURE_CAP)
            facts_out.stderr_bytes = min(len(proc.stderr), OUTPUT_CAPTURE_CAP)
            facts_out.sentinel_present = sentinel.is_file()
            facts_out.sentinel_size_bytes = (
                sentinel.stat().st_size if facts_out.sentinel_present else 0
            )
            if facts_out.sentinel_present and facts_out.sentinel_size_bytes != SENTINEL_SIZE:
                facts_out.sentinel_present = False

            route = f"rc3-smoke-{arm.lower()}"
            if arm in PRODUCT_ARMS and adapter is not None:
                metrics = http_get(f"http://127.0.0.1:{args.adapter_port}/metrics").decode()
                counts = request_status_counts(metrics, "/v1/responses", route)
                facts_out.adapter_requests_ok = counts.get("200", 0)
                facts_out.adapter_requests_500 = counts.get("500", 0)
                facts_out.adapter_requests_422 = counts.get("422", 0)
                # The adapter process is fresh per attempt, so absolute
                # counter values are arm-attempt scoped.
                facts_out.upstream_failures = int(
                    sum(parse_counter_lines(metrics, UPSTREAM_FAILURES_METRIC).values())
                )
                if arm in ("CACHE", "BOTH"):
                    facts_out.compiler_cache_entries = count_cache_entries(cache_root)
        except (QualificationError, subprocess.TimeoutExpired) as exc:
            facts_out.exit_status = None
            facts_out.verdict = "FAIL"
            facts_out.failure_class = f"qualification-error ({type(exc).__name__})"
            return
        finally:
            if adapter is not None:
                adapter.stop()
                check_port_free(args.adapter_port)

        failure: str | None = None
        if facts_out.exit_status != 0:
            failure = "codex-exit"
        elif not facts_out.sentinel_present:
            failure = "sentinel-missing"
        elif arm in PRODUCT_ARMS:
            if facts_out.adapter_requests_ok < 1:
                failure = "adapter-request-missing"
            elif facts_out.adapter_requests_500 > 0:
                failure = "internal-500"
            elif facts_out.adapter_requests_422 > 0:
                failure = "image-policy-422"
            elif facts_out.upstream_failures > 0:
                failure = "upstream-failure"
            elif arm in ("CACHE", "BOTH") and facts_out.compiler_cache_entries < 1:
                failure = "compiler-evidence-missing"
        if failure is None:
            facts_out.verdict = "PASS"
            facts_out.failure_class = "none"
            return
        facts_out.verdict = "FAIL"
        facts_out.failure_class = failure


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-bin", required=True)
    parser.add_argument("--adapter-wheel", required=True, type=Path)
    parser.add_argument("--upstream-base-url", required=True)
    parser.add_argument("--upstream-api-key-file", required=True, type=Path)
    parser.add_argument("--expected-codex-version", required=True)
    parser.add_argument("--expected-codex-sha256", required=True)
    parser.add_argument("--expected-wheel-sha256", required=True)
    parser.add_argument("--adapter-port", type=int, default=18031)
    parser.add_argument("--workdir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--arms", default=",".join(PRODUCT_ARMS))
    parser.add_argument("--include-direct", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--attempt-timeout", type=float, default=600.0)
    parser.add_argument("--ready-timeout", type=float, default=120.0)
    parser.add_argument("--uv-bin", default="uv")
    parser.add_argument("--protect-file", action="append", default=[])
    parser.add_argument("--protect-unit", action="append", default=[])
    parser.add_argument("--protect-port", action="append", default=[])
    args = parser.parse_args()

    arms = tuple(entry.strip().upper() for entry in args.arms.split(",") if entry.strip())
    unknown = set(arms) - set(PRODUCT_ARMS)
    if unknown:
        parser.error(f"unknown arms: {sorted(unknown)}")
    required = list(arms)
    if args.include_direct:
        required.append("DIRECT")

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
        "topology": (
            "disposable-codex-home;loopback-adapter;"
            f"port-{args.adapter_port};existing-backend;gateway-ingress-disabled"
        ),
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
        api_key = args.upstream_api_key_file.read_text().strip()
        if not api_key:
            raise QualificationError("upstream key file empty")

        check_port_free(args.adapter_port)
        probe_upstream(args.upstream_base_url, api_key, MODEL)

        before = snapshot_protected(args)
        facts["protected_state"]["files_checked"] = len(before.files)
        facts["protected_state"]["units"] = dict(before.units)
        facts["protected_state"]["ports"] = {str(key): value for key, value in before.ports.items()}

        # --- Arms (serial) ------------------------------------------------
        _run_arms(args, required, api_key, facts)

        # --- Protected state after ----------------------------------------
        after = snapshot_protected(args)
        diff = diff_protected(before, after)
        facts["protected_state"]["files_changed"] = diff["files_changed"]
        facts["protected_state_unchanged"] = (
            diff["files_changed"] == 0 and diff["units_changed"] == 0 and diff["ports_changed"] == 0
        )
        required_ok = all(facts["arms"][arm]["verdict"] == "PASS" for arm in PRODUCT_ARMS)
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
