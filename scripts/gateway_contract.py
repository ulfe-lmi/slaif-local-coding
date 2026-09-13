#!/usr/bin/env python3
"""Validate and run the repository-only current Gateway contract gate."""

from __future__ import annotations

import argparse
import contextlib
import contextvars
import importlib
import io
import json
import os
import re
import socket
import subprocess
import sys
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, cast
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parents[1]
CURRENT_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "gateway" / "current_peer_authority.json"
GATEWAY_ROOT_ENV = "SLAIF_GATEWAY_ROOT"
SCHEMA = "slaif-local-gateway-peer-authority-v1"
PURPOSE = "current_ci_compatibility_authority"
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SAFE_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
SAFE_VERSION_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,31}$")
EXPECTED_SERVER_FIELDS = frozenset({"module_id", "module_version", "replay_mode"})
EXPECTED_CLIENT_FIELDS = frozenset({"module_id", "module_version"})
EXPECTED_TOP_LEVEL_FIELDS = frozenset(
    {"schema", "version", "repository", "commit", "server", "client", "purpose"}
)
EXPECTED_SOURCE_PATHS = (
    "app/slaif_gateway/modules/servers/local_coding/contract.py",
    "app/slaif_gateway/modules/clients/codex_0149.py",
    "app/slaif_gateway/providers/streaming.py",
)
STRICT_TEST_FILES = (
    "tests/test_gateway162_validator_factory.py",
    "tests/test_current_gateway_contract.py",
)
STRICT_EXPECTED_TESTS = 18
_NETWORK_GUARD_DEPTH: contextvars.ContextVar[int] = contextvars.ContextVar(
    "gateway_contract_network_guard_depth", default=0
)


class ContractGateError(RuntimeError):
    """A fixed, safe contract-gate failure."""


class NetworkAccessDenied(RuntimeError):
    """Raised when a compatibility test attempts network access."""


@dataclass(frozen=True, slots=True)
class PeerAuthority:
    schema: str
    version: int
    repository: str
    commit: str
    server_module_id: str
    server_module_version: str
    replay_mode: str
    client_module_id: str
    client_module_version: str
    purpose: str


@dataclass(frozen=True, slots=True)
class CheckoutFacts:
    root: Path
    head: str
    origin: str
    expected_paths: tuple[str, ...]
    clean: bool


@dataclass(frozen=True, slots=True)
class TestRunResult:
    collected: int
    passed: int
    skipped: int
    failed: int
    errors: int


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ContractGateError("fixture_duplicate_key")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ContractGateError("fixture_non_finite_number")


def _bounded_string(value: object, field: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise ContractGateError(f"fixture_{field}_invalid")
    return value


def load_peer_authority(path: Path = CURRENT_FIXTURE) -> PeerAuthority:
    """Load the one exact current peer fixture and reject every deviation."""
    try:
        raw = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_json_constant,
        )
    except ContractGateError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ContractGateError("fixture_unreadable") from None
    if not isinstance(raw, dict) or set(raw) != EXPECTED_TOP_LEVEL_FIELDS:
        raise ContractGateError("fixture_fields_invalid")
    if raw.get("schema") != SCHEMA or type(raw.get("version")) is not int or raw["version"] != 1:
        raise ContractGateError("fixture_schema_invalid")
    repository = _bounded_string(raw.get("repository"), "repository", REPOSITORY_PATTERN)
    commit = _bounded_string(raw.get("commit"), "commit", COMMIT_PATTERN)
    server = raw.get("server")
    client = raw.get("client")
    if not isinstance(server, dict) or set(server) != EXPECTED_SERVER_FIELDS:
        raise ContractGateError("fixture_server_fields_invalid")
    if not isinstance(client, dict) or set(client) != EXPECTED_CLIENT_FIELDS:
        raise ContractGateError("fixture_client_fields_invalid")
    purpose = _bounded_string(raw.get("purpose"), "purpose", SAFE_TOKEN_PATTERN)
    if purpose != PURPOSE:
        raise ContractGateError("fixture_purpose_invalid")
    return PeerAuthority(
        schema=SCHEMA,
        version=1,
        repository=repository,
        commit=commit,
        server_module_id=_bounded_string(
            server.get("module_id"), "server_module_id", SAFE_TOKEN_PATTERN
        ),
        server_module_version=_bounded_string(
            server.get("module_version"), "server_module_version", SAFE_VERSION_PATTERN
        ),
        replay_mode=_bounded_string(server.get("replay_mode"), "replay_mode", SAFE_TOKEN_PATTERN),
        client_module_id=_bounded_string(
            client.get("module_id"), "client_module_id", SAFE_TOKEN_PATTERN
        ),
        client_module_version=_bounded_string(
            client.get("module_version"), "client_module_version", SAFE_VERSION_PATTERN
        ),
        purpose=purpose,
    )


def _normalized_origin(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        raise ContractGateError("gateway_origin_credentials_present")
    if candidate.startswith("git@"):
        prefix, separator, path = candidate.partition(":")
        if prefix != "git@github.com" or not separator:
            raise ContractGateError("gateway_origin_invalid")
        normalized_path = path
    else:
        parsed = urlsplit(candidate)
        if parsed.scheme not in {"http", "https"} or parsed.hostname != "github.com":
            raise ContractGateError("gateway_origin_invalid")
        if parsed.username is not None or parsed.password is not None:
            raise ContractGateError("gateway_origin_credentials_present")
        if parsed.query or parsed.fragment:
            raise ContractGateError("gateway_origin_invalid")
        normalized_path = parsed.path.lstrip("/")
    normalized_path = normalized_path.rstrip("/")
    if normalized_path.endswith(".git"):
        normalized_path = normalized_path[:-4]
    if REPOSITORY_PATTERN.fullmatch(normalized_path) is None:
        raise ContractGateError("gateway_origin_invalid")
    return normalized_path


def validate_checkout_facts(facts: CheckoutFacts, authority: PeerAuthority) -> None:
    """Apply strict, pure checkout predicates used by the real verifier."""
    if facts.root != facts.root.resolve() or not facts.root.is_dir():
        raise ContractGateError("gateway_root_invalid")
    if facts.head != authority.commit:
        raise ContractGateError("gateway_sha_mismatch")
    if _normalized_origin(facts.origin) != authority.repository:
        raise ContractGateError("gateway_repository_mismatch")
    if tuple(facts.expected_paths) != EXPECTED_SOURCE_PATHS:
        raise ContractGateError("gateway_source_paths_invalid")
    if not all((facts.root / relative).is_file() for relative in facts.expected_paths):
        raise ContractGateError("gateway_source_paths_missing")
    if not facts.clean:
        raise ContractGateError("gateway_checkout_dirty")


def _git(root: Path, *arguments: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        raise ContractGateError("gateway_git_probe_failed") from None
    return completed.stdout.strip()


def validate_gateway_checkout(root: Path, authority: PeerAuthority) -> CheckoutFacts:
    """Prove an explicit real checkout is the exact public peer source."""
    resolved = root.resolve(strict=True)
    if not resolved.is_dir():
        raise ContractGateError("gateway_root_invalid")
    actual_root = Path(_git(resolved, "rev-parse", "--show-toplevel")).resolve()
    facts = CheckoutFacts(
        root=resolved,
        head=_git(resolved, "rev-parse", "HEAD"),
        origin=_git(resolved, "remote", "get-url", "origin"),
        expected_paths=EXPECTED_SOURCE_PATHS,
        clean=not bool(_git(resolved, "status", "--short")),
    )
    if actual_root != resolved:
        raise ContractGateError("gateway_root_mismatch")
    validate_checkout_facts(facts, authority)
    return facts


def _import_gateway(root: Path, module_name: str) -> ModuleType:
    app_root = str(root.resolve(strict=True) / "app")
    if app_root not in sys.path:
        sys.path.insert(0, app_root)
    return importlib.import_module(module_name)


def inspect_gateway_contract(root: Path) -> dict[str, str]:
    """Import only pure Gateway contract modules and return safe facts."""
    server_contract = _import_gateway(root, "slaif_gateway.modules.servers.local_coding.contract")
    server_registry = _import_gateway(root, "slaif_gateway.modules.servers.registry")
    client = _import_gateway(root, "slaif_gateway.modules.clients.codex_0149")
    streaming = _import_gateway(root, "slaif_gateway.providers.streaming")
    descriptor = server_registry.get_server_module(server_contract.LOCAL_CODING_SERVER_MODULE_ID)
    client_module = _import_gateway(
        root, "slaif_gateway.modules.clients.registry"
    ).CODEX_0149_CLIENT_MODULE
    facts = {
        "server_module_id": cast(str, descriptor.module_id),
        "server_module_version": cast(str, descriptor.module_version),
        "replay_mode": cast(str, server_contract.LOCAL_CODING_REPLAY_MODE),
        "client_module_id": cast(str, client.CODEX_0149_CLIENT_MODULE_ID),
        "client_module_version": cast(str, client_module.module_version),
        "validator_class": cast(str, streaming.ResponsesStreamEventValidator.__name__),
        "profile_class": cast(str, streaming.ResponsesStreamValidationProfile.__name__),
    }
    return facts


def validate_runtime_contract(facts: Mapping[str, object], authority: PeerAuthority) -> None:
    expected = {
        "server_module_id": authority.server_module_id,
        "server_module_version": authority.server_module_version,
        "replay_mode": authority.replay_mode,
        "client_module_id": authority.client_module_id,
        "client_module_version": authority.client_module_version,
        "validator_class": "ResponsesStreamEventValidator",
        "profile_class": "ResponsesStreamValidationProfile",
    }
    if set(facts) != set(expected) or any(
        facts.get(key) != value for key, value in expected.items()
    ):
        raise ContractGateError("gateway_runtime_contract_mismatch")


def _deny_network(*_args: object, **_kwargs: object) -> object:
    raise NetworkAccessDenied("network_access_denied")


@contextlib.contextmanager
def network_denial_guard() -> Iterator[None]:
    """Deny TCP/DNS access; nested uses share the already-installed guard."""
    depth = _NETWORK_GUARD_DEPTH.get()
    token = _NETWORK_GUARD_DEPTH.set(depth + 1)
    if depth:
        try:
            yield
        finally:
            _NETWORK_GUARD_DEPTH.reset(token)
        return

    original_socket = socket.socket
    original_create_connection = socket.create_connection
    original_getaddrinfo = socket.getaddrinfo

    class GuardedSocket(original_socket):  # type: ignore[misc,valid-type]
        def connect(self, address: object) -> None:
            _ = address
            raise NetworkAccessDenied("network_access_denied")

        def connect_ex(self, address: object) -> int:
            _ = address
            raise NetworkAccessDenied("network_access_denied")

    setattr(socket, "socket", GuardedSocket)  # noqa: B010
    socket.create_connection = _deny_network  # type: ignore[assignment]
    socket.getaddrinfo = _deny_network  # type: ignore[assignment]
    try:
        yield
    finally:
        setattr(socket, "socket", original_socket)  # noqa: B010
        socket.create_connection = original_create_connection
        socket.getaddrinfo = original_getaddrinfo
        _NETWORK_GUARD_DEPTH.reset(token)


class _PytestResultCollector:
    def __init__(self) -> None:
        self.collected = 0
        self.passed = 0
        self.skipped = 0
        self.failed = 0
        self.errors = 0

    def pytest_sessionfinish(self, session: Any, exitstatus: object) -> None:
        _ = exitstatus
        self.collected = int(session.testscollected)

    def pytest_runtest_logreport(self, report: Any) -> None:
        if report.outcome == "passed" and report.when == "call":
            self.passed += 1
        elif report.outcome == "skipped":
            self.skipped += 1
        elif report.outcome == "failed":
            self.failed += 1

    def pytest_collectreport(self, report: Any) -> None:
        if report.failed:
            self.errors += 1


def enforce_test_result(result: TestRunResult) -> None:
    if result.collected <= 0 or result.skipped != 0 or result.failed != 0 or result.errors != 0:
        raise ContractGateError("strict_test_result_rejected")
    if result.passed != result.collected:
        raise ContractGateError("strict_test_result_incomplete")


def run_strict_tests(*, network_guarded: bool = False) -> TestRunResult:
    """Run only the current contract tests under the network denial guard."""
    os.environ[GATEWAY_ROOT_ENV] = str(Path(os.environ[GATEWAY_ROOT_ENV]).resolve(strict=True))
    collector = _PytestResultCollector()
    output = io.StringIO()
    try:
        import pytest

        guard = contextlib.nullcontext() if network_guarded else network_denial_guard()
        with (
            guard,
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(output),
        ):
            pytest.main([*STRICT_TEST_FILES, "-q"], plugins=[collector])
    except BaseException:
        raise ContractGateError("strict_test_runner_failed") from None
    result = TestRunResult(
        collected=collector.collected,
        passed=collector.passed,
        skipped=collector.skipped,
        failed=collector.failed,
        errors=collector.errors,
    )
    enforce_test_result(result)
    if result.collected != STRICT_EXPECTED_TESTS:
        raise ContractGateError("strict_test_selection_changed")
    return result


def _write_github_outputs(path: Path, authority: PeerAuthority) -> None:
    output_values = (
        ("repository", authority.repository, REPOSITORY_PATTERN),
        ("commit", authority.commit, COMMIT_PATTERN),
        ("server_module_id", authority.server_module_id, SAFE_TOKEN_PATTERN),
        ("server_module_version", authority.server_module_version, SAFE_VERSION_PATTERN),
        ("server_replay_mode", authority.replay_mode, SAFE_TOKEN_PATTERN),
        ("client_module_id", authority.client_module_id, SAFE_TOKEN_PATTERN),
        ("client_module_version", authority.client_module_version, SAFE_VERSION_PATTERN),
    )
    for field, value, pattern in output_values:
        if pattern.fullmatch(value) is None:
            raise ContractGateError(f"github_output_{field}_invalid")
    lines = (
        f"gateway_repository={authority.repository}",
        f"gateway_commit={authority.commit}",
        f"gateway_server_module_id={authority.server_module_id}",
        f"gateway_server_module_version={authority.server_module_version}",
        f"gateway_server_replay_mode={authority.replay_mode}",
        f"gateway_client_module_id={authority.client_module_id}",
        f"gateway_client_module_version={authority.client_module_version}",
    )
    try:
        with path.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
    except OSError:
        raise ContractGateError("github_output_unwritable") from None


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=CURRENT_FIXTURE)
    parser.add_argument("--gateway-root", type=Path)
    parser.add_argument("--emit-github-output", type=Path)
    parser.add_argument("--run-tests", action="store_true")
    args = parser.parse_args(argv)
    if args.emit_github_output is not None and args.gateway_root is not None:
        parser.error("fixture output and gateway verification are separate phases")
    if args.run_tests and args.gateway_root is None:
        parser.error("--run-tests requires --gateway-root")
    if args.gateway_root is None and args.emit_github_output is None:
        parser.error("one operation is required")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    authority = load_peer_authority(args.fixture)
    if args.emit_github_output is not None:
        _write_github_outputs(args.emit_github_output, authority)
        print(json.dumps({"fixture": "valid", "fields": len(EXPECTED_TOP_LEVEL_FIELDS)}))
        return 0
    assert args.gateway_root is not None
    facts = validate_gateway_checkout(args.gateway_root, authority)
    os.environ[GATEWAY_ROOT_ENV] = str(args.gateway_root.resolve(strict=True))
    with network_denial_guard():
        validate_runtime_contract(inspect_gateway_contract(args.gateway_root), authority)
        result = run_strict_tests(network_guarded=True) if args.run_tests else None
    output = {
        "repository": authority.repository,
        "commit": authority.commit,
        "server_module": authority.server_module_id,
        "client_module": authority.client_module_id,
        "checkout_clean": facts.clean,
    }
    if result is not None:
        output.update(
            {
                "tests_collected": result.collected,
                "tests_passed": result.passed,
                "tests_skipped": result.skipped,
                "tests_failed": result.failed,
                "tests_errors": result.errors,
                "network_guard": "enabled",
            }
        )
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractGateError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from None
