#!/usr/bin/env python3
"""Run one disposable pinned-gateway/PostgreSQL/Local-Coding rehearsal.

This file is repository-only support.  It is intentionally outside the wheel,
uses a detached gateway checkout supplied by the caller, and emits only fixed
facts.  Every service, database, container, cache, Codex home, and log lives in
temporary state owned by this one process.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, replace
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
from openai import APIStatusError, OpenAI
from prometheus_client.parser import text_string_to_metric_families

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.dont_write_bytecode = True

from tests.helpers.e2e_support import governed_prompt, run_codex_once  # noqa: E402
from tests.helpers.gateway_accounting_rehearsal import (  # noqa: E402
    GATEWAY_MAIN_SHA,
    PROVIDER,
    PUBLIC_MODEL,
    RESPONSES_ENDPOINT,
    UPSTREAM_MODEL,
    GatewayRehearsalFacts,
    assert_gateway_rehearsal_facts,
)
from tests.helpers.vision_e2e_support import (  # noqa: E402
    VISION_MODEL,
    write_vision_fixture,
    write_vision_model_catalog,
)

SERVICE_TOKEN_ENV = "SLAIF_REHEARSAL_ADAPTER_TOKEN"
QWEN_KEY_ENV = "QWEN3090_API_KEY"
PUBLIC_KEY_ENV = "SLAIF_REHEARSAL_PUBLIC_KEY"
DATABASE_USER = "slaif005c"
DATABASE_NAME = "slaif005c"
DATABASE_PASSWORD = "synthetic-005c-postgres-password"
IMAGE_NAME = "postgres:16"
CODEX_VERSION = "0.149.0"
MAX_REHEARSAL_SECONDS = 900.0


def _free_loopback_port(preferred: int | None = None) -> int:
    candidates = [preferred] if preferred is not None else []
    candidates.append(0)
    for candidate in candidates:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind(("127.0.0.1", candidate or 0))
            except OSError:
                continue
            return int(probe.getsockname()[1])
    raise RuntimeError("no_free_loopback_port")


def _run_command(
    argv: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def _docker(*args: str, timeout: float = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sudo", "-n", "docker", *args],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _docker_ok(*args: str, timeout: float = 120) -> str:
    result = _docker(*args, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError("docker_command_failed")
    return result.stdout.strip()


def _image_fingerprint() -> tuple[bool, str | None, str | None]:
    result = _docker("image", "inspect", IMAGE_NAME, "--format", "{{.Id}} {{.RepoDigests}}")
    if result.returncode != 0:
        return False, None, None
    fields = result.stdout.strip().split(maxsplit=1)
    image_id = fields[0] if fields else None
    digest = None
    if len(fields) == 2:
        match = re.search(r"sha256:[0-9a-f]{64}", fields[1])
        digest = match.group(0) if match else None
    return True, image_id, digest


def _running_container_facts() -> tuple[str, ...]:
    result = _docker("ps", "--format", "{{.ID}} {{.Names}} {{.Image}}")
    if result.returncode != 0:
        return ()
    return tuple(line for line in result.stdout.splitlines() if line.strip())


def _protected_snapshot() -> dict[str, object]:
    unit = _run_command(
        [
            "systemctl",
            "--user",
            "show",
            "qwen-serving-vision.service",
            "--property=ActiveState,SubState,MainPID,ExecMainStartTimestampMonotonic",
            "--no-pager",
        ]
    )
    text_unit = _run_command(
        [
            "systemctl",
            "--user",
            "show",
            "qwen-serving.service",
            "--property=ActiveState,MainPID",
            "--no-pager",
        ]
    )
    listeners = _run_command(["ss", "-ltnp"])
    values: dict[str, str] = {}
    for line in unit.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    text_values: dict[str, str] = {}
    for line in text_unit.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            text_values[key] = value
    listener_text = listeners.stdout
    return {
        "vision_active": values.get("ActiveState") == "active"
        and values.get("SubState") == "running",
        "vision_pid": values.get("MainPID"),
        "vision_start": values.get("ExecMainStartTimestampMonotonic"),
        "text_inactive": text_values.get("ActiveState") == "inactive"
        and text_values.get("MainPID") == "0",
        "has_18020": bool(re.search(r":18020\b", listener_text)),
        "has_18021": bool(re.search(r":18021\b", listener_text)),
        "has_18031": bool(re.search(r":18031\b", listener_text)),
    }


def _minimal_environment() -> dict[str, str]:
    return {
        name: os.environ[name]
        for name in ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "TERM")
        if name in os.environ
    }


def _gateway_environment(
    *,
    gateway_root: Path,
    database_url: str,
    gateway_port: int,
    hmac_secret: str,
    encryption_key: str,
    service_token: str,
) -> dict[str, str]:
    environment = _minimal_environment()
    environment.update(
        {
            "PYTHONPATH": str(gateway_root / "app"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "APP_ENV": "test",
            "APP_BASE_URL": f"http://127.0.0.1:{gateway_port}",
            "PUBLIC_BASE_URL": f"http://127.0.0.1:{gateway_port}/v1",
            "DATABASE_URL": database_url,
            "DATABASE_POOL_SIZE": "2",
            "DATABASE_MAX_OVERFLOW": "0",
            "DATABASE_CONNECT_TIMEOUT_SECONDS": "5",
            "TOKEN_HMAC_SECRET_V1": hmac_secret,
            "ACTIVE_HMAC_KEY_VERSION": "1",
            "ONE_TIME_SECRET_ENCRYPTION_KEY": encryption_key,
            "GATEWAY_KEY_PREFIX": "sk-slaif-",
            "GATEWAY_KEY_ACCEPTED_PREFIXES": "sk-slaif-",
            "ENABLE_REDIS_RATE_LIMITS": "false",
            "ENABLE_ADMIN_DASHBOARD": "false",
            "ENABLE_EMAIL_DELIVERY": "false",
            "ENABLE_METRICS": "true",
            "METRICS_REQUIRE_AUTH": "false",
            "LOG_LEVEL": "WARNING",
            "STRUCTURED_LOGS": "true",
            SERVICE_TOKEN_ENV: service_token,
            "UVICORN_ACCESS_LOG": "false",
        }
    )
    return environment


def _candidate_environment(service_token: str, qwen_key: str) -> dict[str, str]:
    environment = _minimal_environment()
    environment.update(
        {
            "PYTHONPATH": f"{REPO_ROOT / 'src'}:{REPO_ROOT}",
            "PYTHONDONTWRITEBYTECODE": "1",
            SERVICE_TOKEN_ENV: service_token,
            QWEN_KEY_ENV: qwen_key,
        }
    )
    return environment


def _gateway_settings(gateway_url: str) -> dict[str, str]:
    _ = gateway_url
    hmac_secret = "synthetic-005c-hmac-secret-for-disposable-run"
    encoded_key = base64.urlsafe_b64encode(b"x" * 32).decode("ascii").rstrip("=")
    return {"hmac_secret": hmac_secret, "encryption_key": encoded_key}


async def _seed_database(
    gateway_root: Path,
    database_url: str,
    *,
    adapter_port: int,
    hmac_secret: str,
    encryption_key: str,
) -> dict[str, str]:
    sys.path.insert(0, str(gateway_root / "app"))
    from slaif_gateway.config import Settings
    from slaif_gateway.db.repositories.audit import AuditRepository
    from slaif_gateway.db.repositories.institutions import InstitutionsRepository
    from slaif_gateway.db.repositories.keys import GatewayKeysRepository
    from slaif_gateway.db.repositories.one_time_secrets import OneTimeSecretsRepository
    from slaif_gateway.db.repositories.owners import OwnersRepository
    from slaif_gateway.db.repositories.pricing import PricingRulesRepository
    from slaif_gateway.db.repositories.provider_configs import ProviderConfigsRepository
    from slaif_gateway.db.repositories.routing import ModelRoutesRepository
    from slaif_gateway.schemas.keys import CreateGatewayKeyInput
    from slaif_gateway.services.key_service import KeyService
    from slaif_gateway.services.responses_route_capabilities import default_responses_capabilities
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    settings = Settings(
        APP_ENV="test",
        DATABASE_URL=database_url,
        TOKEN_HMAC_SECRET_V1=hmac_secret,
        ACTIVE_HMAC_KEY_VERSION="1",
        ONE_TIME_SECRET_ENCRYPTION_KEY=encryption_key,
        ENABLE_REDIS_RATE_LIMITS=False,
        ENABLE_ADMIN_DASHBOARD=False,
        ENABLE_EMAIL_DELIVERY=False,
    )
    engine = create_async_engine(database_url, future=True, pool_size=2, max_overflow=0)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            institution = await InstitutionsRepository(session).create_institution(
                name="Objective 005-c Disposable Institute", country="SI", notes="temporary"
            )
            owner = await OwnersRepository(session).create_owner(
                name="Disposable",
                surname="Rehearsal",
                email="objective-005c@example.invalid",
                institution_id=institution.id,
            )
            provider = await ProviderConfigsRepository(session).create_provider_config(
                provider=PROVIDER,
                display_name="Disposable Local Coding",
                base_url=f"http://127.0.0.1:{adapter_port}/v1",
                api_key_env_var=SERVICE_TOKEN_ENV,
                kind="openai_compatible",
                enabled=True,
                timeout_seconds=300,
                max_retries=0,
                notes="temporary 005-c rehearsal provider",
            )
            capabilities = default_responses_capabilities()
            capabilities.update(
                {
                    "streaming": True,
                    "function_tools": True,
                    "custom_tools": True,
                    "image_input": True,
                    "codex_request_envelope": True,
                    "codex_client_tools": True,
                    "codex_streaming_tool_events": True,
                }
            )
            route = await ModelRoutesRepository(session).create_model_route(
                requested_model=PUBLIC_MODEL,
                provider=PROVIDER,
                upstream_model=UPSTREAM_MODEL,
                endpoint=RESPONSES_ENDPOINT,
                priority=1,
                enabled=True,
                visible_in_models=True,
                supports_streaming=True,
                capabilities={
                    "responses": capabilities,
                    "codex_limits": {
                        "context_window_tokens": 100_000,
                        "default_max_output_tokens": 4096,
                        "max_output_tokens": 8192,
                    },
                },
                notes="temporary 005-c public-to-local vision route",
            )
            now = __import__("datetime").datetime.now(__import__("datetime").UTC)
            await PricingRulesRepository(session).create_pricing_rule(
                provider=PROVIDER,
                upstream_model=UPSTREAM_MODEL,
                endpoint=RESPONSES_ENDPOINT,
                valid_from=now,
                currency="EUR",
                input_price_per_1m=Decimal("1.000000000"),
                output_price_per_1m=Decimal("2.000000000"),
                request_price=Decimal("0.001000000"),
                notes="temporary operator-confirmed local EUR price",
            )
            key_policy = {
                "version": 1,
                "codex_client_tool_taxonomy": "codex_0_148",
                "allowed_capabilities": [
                    "text",
                    "stateless",
                    "streaming",
                    "function_tools",
                    "custom_tools",
                    "image_input",
                    "codex_request_envelope",
                    "codex_client_tools",
                    "codex_streaming_tool_events",
                ],
            }
            key = await KeyService(
                settings=settings,
                gateway_keys_repository=GatewayKeysRepository(session),
                one_time_secrets_repository=OneTimeSecretsRepository(session),
                audit_repository=AuditRepository(session),
                model_routes_repository=ModelRoutesRepository(session),
            ).create_gateway_key(
                CreateGatewayKeyInput(
                    owner_id=owner.id,
                    valid_from=now,
                    valid_until=now + __import__("datetime").timedelta(hours=1),
                    cost_limit_eur=Decimal("5.000000000"),
                    token_limit_total=1_000_000,
                    request_limit_total=6,
                    allowed_models=[PUBLIC_MODEL],
                    allowed_endpoints=["/v1/models", RESPONSES_ENDPOINT],
                    allowed_providers=[PROVIDER],
                    responses_policy=key_policy,
                    note="temporary 005-c synthetic public key",
                )
            )
            await session.commit()
            return {
                "plaintext_key": key.plaintext_key,
                "gateway_key_id": str(key.gateway_key_id),
                "route_id": str(route.id),
                "provider": provider.provider,
            }
    finally:
        await engine.dispose()


async def _db_snapshot(
    gateway_root: Path, database_url: str, gateway_key_id: str
) -> dict[str, Any]:
    sys.path.insert(0, str(gateway_root / "app"))
    from slaif_gateway.db.models import GatewayKey, ModelRoute, QuotaReservation, UsageLedger
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    engine = create_async_engine(database_url, future=True, pool_size=2, max_overflow=0)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            key = await session.get(GatewayKey, gateway_key_id)
            reservations = list(
                (
                    await session.scalars(
                        select(QuotaReservation).where(
                            QuotaReservation.gateway_key_id == gateway_key_id
                        )
                    )
                ).all()
            )
            ledgers = list(
                (
                    await session.scalars(
                        select(UsageLedger).where(UsageLedger.gateway_key_id == gateway_key_id)
                    )
                ).all()
            )
            route = (
                await session.scalars(
                    select(ModelRoute).where(ModelRoute.requested_model == PUBLIC_MODEL)
                )
            ).first()
            request_ids = [row.request_id for row in ledgers]
            usage_rows = [
                row
                for row in ledgers
                if row.total_tokens > 0
                and row.prompt_tokens + row.completion_tokens == row.total_tokens
                and bool(row.usage_raw)
            ]
            total_tokens = sum(int(row.total_tokens) for row in ledgers)
            total_cost = sum((row.actual_cost_eur or Decimal("0")) for row in ledgers)
            return {
                "reservation_count": len(reservations),
                "finalized_reservation_count": sum(
                    row.status == "finalized" for row in reservations
                ),
                "pending_reservation_count": sum(row.status == "pending" for row in reservations),
                "ledger_count": len(ledgers),
                "finalized_ledger_count": sum(
                    row.accounting_status == "finalized" and row.success is True for row in ledgers
                ),
                "failed_ledger_count": sum(row.accounting_status == "failed" for row in ledgers),
                "duplicate_request_id_count": len(request_ids) - len(set(request_ids)),
                "provider_usage_rows": len(usage_rows),
                "key_requests_used": int(key.requests_used_total) if key is not None else -1,
                "key_requests_reserved": int(key.requests_reserved_total)
                if key is not None
                else -1,
                "key_tokens_used": int(key.tokens_used_total) if key is not None else -1,
                "key_tokens_reserved": int(key.tokens_reserved_total) if key is not None else -1,
                "key_cost_used_eur": _decimal_text(key.cost_used_eur if key is not None else None),
                "key_cost_reserved_eur": _decimal_text(
                    key.cost_reserved_eur if key is not None else None
                ),
                "ledger_total_tokens": total_tokens,
                "ledger_total_cost_eur": _decimal_text(total_cost),
                "route_metadata_ok": bool(
                    route is not None
                    and route.provider == PROVIDER
                    and route.upstream_model == UPSTREAM_MODEL
                    and route.endpoint == RESPONSES_ENDPOINT
                    and route.enabled
                    and route.visible_in_models
                ),
            }
    finally:
        await engine.dispose()


async def _tighten_request_limit(
    gateway_root: Path, database_url: str, gateway_key_id: str
) -> None:
    sys.path.insert(0, str(gateway_root / "app"))
    from slaif_gateway.db.models import GatewayKey
    from slaif_gateway.db.repositories.keys import GatewayKeysRepository
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    engine = create_async_engine(database_url, future=True, pool_size=1, max_overflow=0)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            key = await session.get(GatewayKey, gateway_key_id)
            if key is None:
                raise RuntimeError("seed_gateway_key_missing")
            updated = await GatewayKeysRepository(session).update_gateway_key_limits(
                key.id, request_limit_total=int(key.requests_used_total)
            )
            if not updated:
                raise RuntimeError("request_quota_tighten_failed")
            await session.commit()
    finally:
        await engine.dispose()


def _decimal_text(value: Decimal | None) -> str:
    if value is None:
        return "missing"
    return format(value.normalize(), "f")


def _metric_sum(metrics: str, name: str, labels: dict[str, str] | None = None) -> int:
    wanted = labels or {}
    total = 0.0
    for family in text_string_to_metric_families(metrics):
        for sample in family.samples:
            if sample.name != name or any(
                sample.labels.get(key) != value for key, value in wanted.items()
            ):
                continue
            total += float(sample.value)
    return int(total)


def _adapter_metrics(client: httpx.Client, adapter_port: int) -> str:
    response = client.get(f"http://127.0.0.1:{adapter_port}/metrics")
    if response.status_code != 200:
        raise RuntimeError("candidate_metrics_unavailable")
    return response.text


def _wait_status(client: httpx.Client, url: str, *, headers: dict[str, str] | None = None) -> int:
    deadline = time.monotonic() + 45
    last_status = 0
    while time.monotonic() < deadline:
        try:
            response = client.get(url, headers=headers)
            last_status = response.status_code
            if response.status_code < 500:
                return response.status_code
        except httpx.HTTPError:
            pass
        time.sleep(0.25)
    return last_status


def _stop_process(process: subprocess.Popen[bytes] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=15)


def _secret_free_logs(paths: tuple[Path, ...], values: tuple[str, ...]) -> bool:
    needles = tuple(value.encode("utf-8") for value in values if value)
    try:
        for path in paths:
            data = path.read_bytes()
            if any(needle in data for needle in needles):
                return False
    except OSError:
        return False
    return True


def _codex_version(codex: Path) -> str:
    result = _run_command([str(codex), "--version"])
    match = re.search(r"\b(\d+\.\d+\.\d+)\b", result.stdout + result.stderr)
    return match.group(1) if match else "unavailable"


def _public_model_catalog_ok(path: Path) -> bool:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        models = document.get("models")
        selected = next(item for item in models if item.get("slug") == PUBLIC_MODEL)
        return (
            selected.get("input_modalities") == ["text", "image"]
            and selected.get("supports_image_detail_original") is False
            and selected.get("context_window") == 100_000
            and selected.get("supports_parallel_tool_calls") is False
        )
    except (OSError, TypeError, ValueError, StopIteration):
        return False


def _disable_catalog_search_tools(path: Path) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    models = document.get("models")
    selected = next(item for item in models if item.get("slug") == PUBLIC_MODEL)
    selected["experimental_supported_tools"] = []
    selected["supports_search_tool"] = False
    selected["web_search_tool_type"] = "text"
    path.write_text(json.dumps(document, separators=(",", ":")), encoding="utf-8")
    os.chmod(path, 0o600)


def _build_gateway_process(
    gateway_python: Path,
    gateway_root: Path,
    gateway_port: int,
    environment: dict[str, str],
    log_path: Path,
) -> subprocess.Popen[bytes]:
    log = log_path.open("wb")
    try:
        return subprocess.Popen(
            [
                str(gateway_python),
                "-m",
                "uvicorn",
                "slaif_gateway.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(gateway_port),
                "--no-access-log",
                "--log-level",
                "warning",
            ],
            cwd=gateway_root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
        )
    except BaseException:
        log.close()
        raise


def _build_candidate_process(
    gateway_python: Path,
    config_path: Path,
    environment: dict[str, str],
    log_path: Path,
) -> subprocess.Popen[bytes]:
    log = log_path.open("wb")
    try:
        return subprocess.Popen(
            [str(gateway_python), "-m", "slaif_local_coding", "--config", str(config_path)],
            cwd=REPO_ROOT,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
        )
    except BaseException:
        log.close()
        raise


def _docker_start_postgres() -> tuple[str, int, bool, bool, str | None, str | None]:
    running_before = _running_container_facts()
    image_before, image_id_before, digest_before = _image_fingerprint()
    if not image_before:
        pulled = _docker("pull", IMAGE_NAME, timeout=180)
        if pulled.returncode != 0:
            raise RuntimeError("postgres_image_pull_failed")
    name = f"slaif-005c-postgres-{secrets.token_hex(4)}"
    run = _docker(
        "run",
        "-d",
        "--rm",
        "--name",
        name,
        "--tmpfs",
        "/var/lib/postgresql/data:rw,nosuid,nodev,noexec,size=1g",
        "--shm-size",
        "64m",
        "-e",
        f"POSTGRES_DB={DATABASE_NAME}",
        "-e",
        f"POSTGRES_USER={DATABASE_USER}",
        "-e",
        f"POSTGRES_PASSWORD={DATABASE_PASSWORD}",
        "-p",
        "127.0.0.1::5432",
        IMAGE_NAME,
        timeout=60,
    )
    if run.returncode != 0:
        raise RuntimeError("postgres_container_start_failed")
    port_text = _docker_ok("port", name, "5432/tcp")
    match = re.search(r":(\d+)\s*$", port_text)
    if match is None:
        raise RuntimeError("postgres_host_port_unavailable")
    port = int(match.group(1))
    for _ in range(60):
        ready = _docker("exec", name, "pg_isready", "-U", DATABASE_USER, "-d", DATABASE_NAME)
        if ready.returncode == 0:
            tmpfs_config = json.loads(
                _docker_ok("inspect", name, "--format", "{{json .HostConfig.Tmpfs}}")
            )
            tmpfs_only = isinstance(tmpfs_config, dict) and set(tmpfs_config) == {
                "/var/lib/postgresql/data"
            }
            image_after, image_id_after, digest_after = _image_fingerprint()
            if not image_after or image_id_after is None or digest_after is None:
                raise RuntimeError("postgres_image_fingerprint_missing")
            _ = running_before
            return name, port, tmpfs_only, not image_before, image_id_after, digest_after
        time.sleep(1)
    raise RuntimeError("postgres_readiness_timeout")


def _docker_cleanup(name: str | None, image_was_absent: bool) -> tuple[bool, bool]:
    container_removed = False
    if name:
        stopped = _docker("stop", name, timeout=30)
        if stopped.returncode != 0:
            _docker("rm", "-f", name, timeout=30)
        container_removed = _docker("inspect", name).returncode != 0
    image_removed = True
    if image_was_absent:
        concurrent = _docker("ps", "--filter", "ancestor=" + IMAGE_NAME, "--format", "{{.ID}}")
        if concurrent.returncode != 0 or concurrent.stdout.strip():
            image_removed = False
        else:
            image_removed = _docker("image", "rm", IMAGE_NAME, timeout=60).returncode == 0
    return container_removed, image_removed


def _run_rehearsal(args: argparse.Namespace) -> GatewayRehearsalFacts:
    started = time.monotonic()
    gateway_root = args.gateway_root.resolve()
    # Keep the venv launcher path itself; resolving its symlink would bypass
    # the disposable venv and execute the system interpreter.
    gateway_python = Path(args.gateway_python).absolute()
    if (
        _run_command(["git", "-C", str(gateway_root), "rev-parse", "HEAD"]).stdout.strip()
        != GATEWAY_MAIN_SHA
    ):
        raise RuntimeError("gateway_sha_mismatch")
    checkout_clean_before = not bool(
        _run_command(["git", "-C", str(gateway_root), "status", "--short"]).stdout.strip()
    )
    if not checkout_clean_before:
        raise RuntimeError("gateway_checkout_dirty")
    codex = Path(args.codex).resolve()
    codex_version = _codex_version(codex)
    if codex_version != CODEX_VERSION:
        raise RuntimeError("codex_version_mismatch")
    qwen_key = os.environ.get(QWEN_KEY_ENV)
    if not qwen_key:
        raise RuntimeError("protected_qwen_key_unavailable")
    before_protected = _protected_snapshot()
    if not before_protected["vision_active"] or not before_protected["has_18020"]:
        raise RuntimeError("protected_vision_fixture_not_active")
    if not before_protected["text_inactive"] or before_protected["has_18021"]:
        raise RuntimeError("protected_fixture_precondition_failed")
    gateway_port = _free_loopback_port()
    adapter_port = _free_loopback_port(18031)
    if adapter_port != 18031:
        raise RuntimeError("candidate_port_18031_not_free")
    gateway_url = f"http://127.0.0.1:{gateway_port}"
    synthetic = _gateway_settings(gateway_url)
    service_token = "synthetic-005c-adapter-service-token"
    gateway_key: str | None = None
    gateway_process: subprocess.Popen[bytes] | None = None
    candidate_process: subprocess.Popen[bytes] | None = None
    postgres_name: str | None = None
    postgres_image_was_absent = False
    postgres_image_id: str | None = None
    postgres_image_digest: str | None = None
    container_removed = False
    image_removed = False
    logs: tuple[Path, ...] = ()
    temporary_name: str | None = None
    fact: GatewayRehearsalFacts | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="slaif-005c-rehearsal-") as temporary:
            temporary_name = temporary
            temp_root = Path(temporary)
            gateway_log_path = temp_root / "gateway.log"
            candidate_log_path = temp_root / "candidate.log"
            logs = (gateway_log_path, candidate_log_path)
            fixture = write_vision_fixture(temp_root / "fixture", gateway_url + "/v1", QWEN_KEY_ENV)
            adapter_config_text = fixture.adapter_config.read_text(encoding="utf-8")
            adapter_config_text = adapter_config_text.replace(
                "[upstream]\n",
                '[gateway_ingress]\nmode = "service_bearer_static_identity"\n'
                f'service_token_env = "{SERVICE_TOKEN_ENV}"\n\n[upstream]\n',
                1,
            )
            fixture.adapter_config.write_text(adapter_config_text, encoding="utf-8")
            os.chmod(fixture.adapter_config, 0o600)
            codex_config_text = fixture.codex_config.read_text(encoding="utf-8")
            codex_config_text = codex_config_text.replace(
                f'model = "{VISION_MODEL}"', f'model = "{PUBLIC_MODEL}"', 1
            ).replace(f'env_key = "{QWEN_KEY_ENV}"', f'env_key = "{PUBLIC_KEY_ENV}"', 1)
            fixture.codex_config.write_text(codex_config_text, encoding="utf-8")
            os.chmod(fixture.codex_config, 0o600)
            fixture = replace(fixture, api_key_env=PUBLIC_KEY_ENV)
            write_vision_model_catalog(codex, fixture.model_catalog, model=PUBLIC_MODEL)
            _disable_catalog_search_tools(fixture.model_catalog)
            if not _public_model_catalog_ok(fixture.model_catalog):
                raise RuntimeError("codex_catalog_contract_failed")

            (
                postgres_name,
                postgres_port,
                tmpfs_only,
                postgres_image_was_absent,
                postgres_image_id,
                postgres_image_digest,
            ) = _docker_start_postgres()
            database_url = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@127.0.0.1:{postgres_port}/{DATABASE_NAME}"
            gateway_env = _gateway_environment(
                gateway_root=gateway_root,
                database_url=database_url,
                gateway_port=gateway_port,
                hmac_secret=synthetic["hmac_secret"],
                encryption_key=synthetic["encryption_key"],
                service_token=service_token,
            )
            migrate_env = dict(gateway_env)
            migration_succeeded = False
            for _ in range(3):
                migration = _run_command(
                    [str(gateway_python), "-m", "alembic", "upgrade", "head"],
                    cwd=gateway_root,
                    env=migrate_env,
                )
                if migration.returncode == 0:
                    migration_succeeded = True
                    break
                time.sleep(1)
            if not migration_succeeded:
                raise RuntimeError("gateway_migration_failed")
            seeded = asyncio.run(
                _seed_database(
                    gateway_root,
                    database_url,
                    adapter_port=adapter_port,
                    hmac_secret=synthetic["hmac_secret"],
                    encryption_key=synthetic["encryption_key"],
                )
            )
            gateway_key = seeded["plaintext_key"]
            seeded_key_id = seeded["gateway_key_id"]
            candidate_process = _build_candidate_process(
                gateway_python,
                fixture.adapter_config,
                _candidate_environment(service_token, qwen_key),
                candidate_log_path,
            )
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                candidate_health = _wait_status(
                    http,
                    f"http://127.0.0.1:{adapter_port}/health",
                    headers={"Authorization": f"Bearer {service_token}"},
                )
                candidate_ready = _wait_status(http, f"http://127.0.0.1:{adapter_port}/readyz")
                if candidate_health != 200 or candidate_ready != 200:
                    raise RuntimeError("candidate_not_ready")
            gateway_process = _build_gateway_process(
                gateway_python, gateway_root, gateway_port, gateway_env, gateway_log_path
            )
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                gateway_health = _wait_status(http, f"{gateway_url}/healthz")
                gateway_ready = _wait_status(http, f"{gateway_url}/readyz")
            if gateway_health != 200 or gateway_ready != 200:
                raise RuntimeError("gateway_not_ready")
            if not gateway_key:
                raise RuntimeError("seed_key_unavailable")
            client = OpenAI(
                api_key=gateway_key,
                base_url=gateway_url + "/v1",
                timeout=120,
                max_retries=0,
            )
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                before_unauthorized = _metric_sum(
                    _adapter_metrics(http, adapter_port), "slaif_requests_total"
                )
                unauthorized = http.get(
                    f"{gateway_url}/v1/models",
                    headers={"Authorization": "Bearer sk-slaif-invalid." + "a" * 43},
                )
                after_unauthorized = _metric_sum(
                    _adapter_metrics(http, adapter_port), "slaif_requests_total"
                )
                unauthorized_status = unauthorized.status_code
            models = client.models.list()
            model_ids = tuple(str(item.id) for item in models.data)
            text_response = client.responses.create(
                model=PUBLIC_MODEL,
                input="Return a short acknowledgment.",
                max_output_tokens=32,
                store=False,
            )
            text_usage = getattr(getattr(text_response, "usage", None), "total_tokens", None)
            if not isinstance(text_usage, int):
                raise RuntimeError("text_usage_missing")
            stream_types: list[str] = []
            stream_completed_usage = False
            stream = client.responses.create(
                model=PUBLIC_MODEL,
                input="Return one short streamed acknowledgment.",
                max_output_tokens=32,
                tools=[
                    {
                        "type": "namespace",
                        "name": "functions",
                        "tools": [
                            {
                                "type": "function",
                                "name": "rehearsal_noop",
                                "description": (
                                    "A bounded no-op tool that must not be called in this turn."
                                ),
                                "parameters": {
                                    "type": "object",
                                    "properties": {},
                                    "additionalProperties": False,
                                },
                            }
                        ],
                    }
                ],
                tool_choice="none",
                stream=True,
            )
            for event in stream:
                event_type = getattr(event, "type", None)
                if isinstance(event_type, str):
                    stream_types.append(event_type)
                if event_type == "response.completed":
                    usage = getattr(getattr(event, "response", None), "usage", None)
                    stream_completed_usage = isinstance(getattr(usage, "total_tokens", None), int)
            data_url = "data:image/png;base64," + base64.b64encode(
                fixture.full_image.path.read_bytes()
            ).decode("ascii")
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                before_image = _adapter_metrics(http, adapter_port)
            image_response = client.responses.create(
                model=PUBLIC_MODEL,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "Describe this synthetic image briefly.",
                            },
                            {"type": "input_image", "image_url": data_url, "detail": "auto"},
                        ],
                    }
                ],
                max_output_tokens=32,
                store=False,
            )
            if getattr(image_response, "usage", None) is None:
                raise RuntimeError("image_usage_missing")
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                after_image = _adapter_metrics(http, adapter_port)
                before_codex_metrics = _adapter_metrics(http, adapter_port)
            before_codex_rows = asyncio.run(_db_snapshot(gateway_root, database_url, seeded_key_id))
            public_key_previous = os.environ.get(PUBLIC_KEY_ENV)
            os.environ[PUBLIC_KEY_ENV] = gateway_key
            try:
                codex_run = run_codex_once(
                    codex,
                    fixture,
                    governed_prompt(),
                    timeout_seconds=300,
                    expected_command="cat GOVERNANCE-DEPENDENCY.md",
                )
            finally:
                if public_key_previous is None:
                    os.environ.pop(PUBLIC_KEY_ENV, None)
                else:
                    os.environ[PUBLIC_KEY_ENV] = public_key_previous
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                after_codex_metrics = _adapter_metrics(http, adapter_port)
            after_codex_rows = asyncio.run(_db_snapshot(gateway_root, database_url, seeded_key_id))
            asyncio.run(_tighten_request_limit(gateway_root, database_url, seeded_key_id))
            codex_request_count = int(codex_run.event_type_counts.get("response.created", 0))
            compiler_attempt_delta = _metric_sum(
                after_codex_metrics, "slaif_constitution_compiler_attempts_total"
            ) - _metric_sum(before_codex_metrics, "slaif_constitution_compiler_attempts_total")
            compiler_success_delta = _metric_sum(
                after_codex_metrics, "slaif_constitution_compiler_successes_total"
            ) - _metric_sum(before_codex_metrics, "slaif_constitution_compiler_successes_total")
            over_quota_status = 0
            over_quota_candidate_delta = 0
            for _ in range(3):
                with httpx.Client(timeout=30, follow_redirects=False) as http:
                    before_quota = _metric_sum(
                        _adapter_metrics(http, adapter_port), "slaif_requests_total"
                    )
                try:
                    client.responses.create(
                        model=PUBLIC_MODEL,
                        input="quota probe",
                        max_output_tokens=8,
                        store=False,
                    )
                except APIStatusError as exc:
                    if exc.status_code not in {402, 429}:
                        raise RuntimeError("unexpected_quota_probe_failure") from None
                    over_quota_status = int(exc.status_code)
                    with httpx.Client(timeout=30, follow_redirects=False) as http:
                        over_quota_candidate_delta = (
                            _metric_sum(
                                _adapter_metrics(http, adapter_port), "slaif_requests_total"
                            )
                            - before_quota
                        )
                    break
            if over_quota_status == 0:
                raise RuntimeError("quota_rejection_not_observed")
            final_rows = asyncio.run(_db_snapshot(gateway_root, database_url, seeded_key_id))
            with httpx.Client(timeout=30, follow_redirects=False) as http:
                image_seen_delta = _metric_sum(
                    after_image,
                    "slaif_image_items_total",
                    {"route": "qwen38-vision-codex", "result": "seen"},
                ) - _metric_sum(
                    before_image,
                    "slaif_image_items_total",
                    {"route": "qwen38-vision-codex", "result": "seen"},
                )
                image_removed_delta = _metric_sum(
                    after_image,
                    "slaif_image_items_total",
                    {"route": "qwen38-vision-codex", "result": "removed"},
                ) - _metric_sum(
                    before_image,
                    "slaif_image_items_total",
                    {"route": "qwen38-vision-codex", "result": "removed"},
                )
            safe_log_values = (
                service_token,
                qwen_key,
                gateway_key,
                fixture.sentinel_token,
                "GOVERNANCE-DEPENDENCY.md",
            )
            logs_clean = _secret_free_logs(logs, safe_log_values)
            before_codex_request_count = before_codex_rows["ledger_count"]
            after_codex_request_count = after_codex_rows["ledger_count"]
            fact = GatewayRehearsalFacts(
                gateway_sha=GATEWAY_MAIN_SHA,
                gateway_checkout_clean_before=checkout_clean_before,
                gateway_checkout_clean_after=False,
                postgres_image_preexisted=not postgres_image_was_absent,
                postgres_image_pulled=postgres_image_was_absent,
                postgres_image_removed=False,
                postgres_tmpfs_only=tmpfs_only,
                gateway_health_status=gateway_health,
                gateway_ready_status=gateway_ready,
                candidate_health_status=candidate_health,
                candidate_ready_status=candidate_ready,
                models_status=200,
                models_visible_count=len(model_ids),
                models_visible_expected=model_ids == (PUBLIC_MODEL,),
                text_status=200,
                text_usage_total=int(text_usage),
                stream_status=200,
                stream_event_types=tuple(stream_types),
                stream_completed_usage=stream_completed_usage,
                image_status=200,
                image_seen_delta=image_seen_delta,
                image_removed_delta=image_removed_delta,
                codex_version=codex_version,
                codex_exit_status=codex_run.exit_status,
                codex_tool_calls=codex_run.tool_calls,
                codex_dependency_reads=codex_run.dependency_observation.successful_dependency_reads,
                codex_sentinel_passed=codex_run.sentinel_passed,
                codex_effective_governance=codex_run.failure_reason == "success"
                and codex_run.dependency_observation.lifecycle == "success",
                codex_public_request_count=codex_request_count,
                compiler_attempt_delta=compiler_attempt_delta,
                compiler_success_delta=compiler_success_delta,
                compiler_added_gateway_rows=after_codex_request_count
                - before_codex_request_count
                - codex_request_count,
                unauthorized_status=unauthorized_status,
                unauthorized_candidate_request_delta=after_unauthorized - before_unauthorized,
                over_quota_status=over_quota_status,
                over_quota_candidate_request_delta=over_quota_candidate_delta,
                reservation_count=final_rows["reservation_count"],
                finalized_reservation_count=final_rows["finalized_reservation_count"],
                pending_reservation_count=final_rows["pending_reservation_count"],
                ledger_count=final_rows["ledger_count"],
                finalized_ledger_count=final_rows["finalized_ledger_count"],
                failed_ledger_count=final_rows["failed_ledger_count"],
                duplicate_request_id_count=final_rows["duplicate_request_id_count"],
                provider_usage_rows=final_rows["provider_usage_rows"],
                key_requests_used=final_rows["key_requests_used"],
                key_requests_reserved=final_rows["key_requests_reserved"],
                key_tokens_used=final_rows["key_tokens_used"],
                key_tokens_reserved=final_rows["key_tokens_reserved"],
                key_cost_used_eur=final_rows["key_cost_used_eur"],
                key_cost_reserved_eur=final_rows["key_cost_reserved_eur"],
                ledger_total_tokens=final_rows["ledger_total_tokens"],
                ledger_total_cost_eur=final_rows["ledger_total_cost_eur"],
                route_metadata_ok=final_rows["route_metadata_ok"],
                gateway_key_not_forwarded=logs_clean and candidate_health == 200,
                adapter_service_token_not_forwarded=logs_clean and candidate_ready == 200,
                qwen_credential_boundary_ok=candidate_ready == 200
                and QWEN_KEY_ENV not in gateway_env,
                compiler_not_accounted_as_public=(
                    compiler_attempt_delta > 0
                    and after_codex_request_count - before_codex_request_count
                    == codex_request_count
                ),
                gateway_logs_secret_free=logs_clean,
                candidate_logs_secret_free=logs_clean,
                candidate_listener_removed=False,
                gateway_listener_removed=False,
                postgres_container_removed=False,
                temporary_state_removed=False,
                protected_vision_pid_unchanged=False,
                protected_vision_start_unchanged=False,
                protected_vision_listener_unchanged=False,
                text_service_still_inactive=False,
                no_18021_listener=False,
                no_18031_listener=False,
            )
    finally:
        _stop_process(gateway_process)
        _stop_process(candidate_process)
        container_removed, image_removed = _docker_cleanup(postgres_name, postgres_image_was_absent)
        after_protected = _protected_snapshot()
        checkout_clean_after = not bool(
            _run_command(["git", "-C", str(gateway_root), "status", "--short"]).stdout.strip()
        )
        if fact is not None:
            gateway_listener_removed = not bool(
                _run_command(["ss", "-ltnp"]).stdout
                and re.search(rf":{gateway_port}\b", _run_command(["ss", "-ltnp"]).stdout)
            )
            candidate_listener_removed = not bool(
                re.search(r":18031\b", _run_command(["ss", "-ltnp"]).stdout)
            )
            fact = replace(
                fact,
                gateway_checkout_clean_after=checkout_clean_after,
                postgres_image_removed=image_removed,
                candidate_listener_removed=candidate_listener_removed,
                gateway_listener_removed=gateway_listener_removed,
                postgres_container_removed=container_removed,
                protected_vision_pid_unchanged=before_protected["vision_pid"]
                == after_protected["vision_pid"],
                protected_vision_start_unchanged=before_protected["vision_start"]
                == after_protected["vision_start"],
                protected_vision_listener_unchanged=before_protected["has_18020"]
                == after_protected["has_18020"],
                text_service_still_inactive=bool(after_protected["text_inactive"]),
                no_18021_listener=not bool(after_protected["has_18021"]),
                no_18031_listener=not bool(after_protected["has_18031"]),
            )
    if fact is None:
        raise RuntimeError("rehearsal_did_not_produce_facts")
    if temporary_name is not None:
        fact = replace(fact, temporary_state_removed=not Path(temporary_name).exists())
    assert_gateway_rehearsal_facts(fact)
    if time.monotonic() - started > MAX_REHEARSAL_SECONDS:
        raise RuntimeError("rehearsal_time_budget_exceeded")
    return fact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gateway-root", type=Path, required=True)
    parser.add_argument("--gateway-python", type=Path, required=True)
    parser.add_argument("--codex", type=Path, default=shutil.which("codex") or "codex")
    args = parser.parse_args()
    try:
        facts = _run_rehearsal(args)
    except Exception as exc:  # pragma: no cover - bounded live process boundary
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__}, sort_keys=True))
        return 1
    print(json.dumps({"status": "PASSED", **asdict(facts)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
