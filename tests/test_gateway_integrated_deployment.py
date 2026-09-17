"""Gateway-integrated deployment configuration contract (order 010-a, C/H).

Covers: the final signed deployment configuration parses and enables the
accepted contract; the signed deployment fails readiness without the
service credential and without the signing secret; static identity cannot
coexist with signed-request identity; the three Local-side secret roles
cannot share one env name; development and gateway-integrated templates
carry truthful mechanical labels; and no public/non-authorized Local
binding appears in any new deployment asset.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

import httpx
import pytest
from pydantic import ValidationError

from slaif_local_coding.app import create_app
from slaif_local_coding.config import (
    CacheConfig,
    CompilerConfig,
    ConstitutionIntegrationConfig,
    GatewayIngressConfig,
    RouteConfig,
    ServerConfig,
    Settings,
    UpstreamConfig,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
GATEWAY_TEMPLATE = REPO_ROOT / "config" / "adapter.gateway-integrated.template.toml"
DEVELOPMENT_TEMPLATE = REPO_ROOT / "config" / "adapter.deployment.template.toml"
TOPOLOGY_DOC = REPO_ROOT / "docs" / "TOPOLOGY.md"
TOPOLOGY_MANIFEST = REPO_ROOT / "docs" / "topology.manifest.json"
SERVICE_UNIT = REPO_ROOT / "packaging" / "slaif-local-coding.service"
CUTOVER_RUNBOOK = REPO_ROOT / "docs" / "RELEASE-CUTOVER-RUNBOOK.md"


def _render_gateway_template(listen_host: str = "127.0.0.1") -> str:
    text = GATEWAY_TEMPLATE.read_text(encoding="utf-8")
    rendered = (
        text.replace("__LISTEN_HOST__", listen_host)
        .replace("__UPSTREAM_BASE_URL__", "http://127.0.0.1:18020/v1")
        .replace("__UPSTREAM_MODEL__", "qwen3.8-27b")
    )
    return rendered


def test_gateway_integrated_template_uses_only_documented_placeholders() -> None:
    text = GATEWAY_TEMPLATE.read_text(encoding="utf-8")
    tokens = sorted(set(re.findall(r"__[A-Z0-9_]+__", text)))
    assert tokens == ["__LISTEN_HOST__", "__UPSTREAM_BASE_URL__", "__UPSTREAM_MODEL__"]


def test_gateway_integrated_config_parses_and_enables_accepted_contract() -> None:
    rendered = _render_gateway_template("127.0.0.1")
    assert "__" not in rendered
    config = tomllib.loads(rendered)
    assert config["server"]["listen_host"] == "127.0.0.1"
    assert config["server"]["listen_port"] == 18031
    assert config["gateway_ingress"]["mode"] == "service_bearer_signed_identity_v1"
    assert config["gateway_ingress"]["identity_version"] == "v1"
    assert config["gateway_ingress"]["policy_version"] == "signed-identity-v1"
    assert config["gateway_ingress"]["clock_skew_seconds"] == 60
    assert config["gateway_ingress"]["replay_ttl_seconds"] == 60
    assert config["compiler"]["enabled"] is True
    assert config["constitution"]["enabled"] is True
    assert config["constitution"]["identity_source"] == "signed_request"
    for static_label in ("principal", "session", "repository"):
        assert static_label not in config["constitution"]
    route = config["routes"][0]
    assert route["observation_enabled"] is True
    assert route["constitution_enabled"] is True

    from slaif_local_coding.config import load_settings

    path = REPO_ROOT / ".tmp-gateway-integrated-rendered.toml"
    path.write_text(rendered, encoding="utf-8")
    try:
        settings = load_settings(path)
    finally:
        path.unlink()
    assert settings.gateway_ingress.signed is True
    assert settings.constitution.identity_source == "signed_request"
    assert settings.compiler.enabled is True
    assert settings.routes[0].constitution_enabled is True


def _signed_settings(tmp_path: Path) -> Settings:
    return Settings(
        server=ServerConfig(),
        gateway_ingress=GatewayIngressConfig(
            mode="service_bearer_signed_identity_v1",
            service_token_env="TEST_GATEWAY_SERVICE_TOKEN",
            signing_secret_env="TEST_GATEWAY_SIGNING_SECRET",
        ),
        upstream=UpstreamConfig(
            base_url="http://upstream.test/v1",
            api_key_env="TEST_UPSTREAM_KEY",
            model="qwen",
        ),
        routes=[
            RouteConfig(
                name="vision",
                model="qwen",
                max_images_per_request=1,
                image_overflow_policy="retain_newest",
                observation_enabled=True,
                constitution_enabled=True,
            )
        ],
        compiler=CompilerConfig(enabled=True, api_key_env="TEST_COMPILER_KEY"),
        cache=CacheConfig(root=tmp_path / "cache", fallback_root=tmp_path / "fallback-cache"),
        constitution=ConstitutionIntegrationConfig(enabled=True, identity_source="signed_request"),
    )


def _healthy_upstream_handler() -> Any:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/health"
        return httpx.Response(200, json={})

    return handler


@pytest.mark.asyncio
async def test_signed_deployment_cannot_become_ready_without_service_credential(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("TEST_GATEWAY_SERVICE_TOKEN", raising=False)
    monkeypatch.setenv("TEST_GATEWAY_SIGNING_SECRET", "synthetic-signing-secret-value-0123456789")
    monkeypatch.setenv("TEST_UPSTREAM_KEY", "test-only-secret")
    monkeypatch.setenv("TEST_COMPILER_KEY", "compiler-only-synthetic-token")
    settings = _signed_settings(tmp_path)
    app = create_app(settings, httpx.MockTransport(_healthy_upstream_handler()))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        ready = await client.get("/readyz")
    assert ready.status_code == 503
    assert ready.json()["gateway_ingress"] == "unavailable"


@pytest.mark.asyncio
async def test_signed_deployment_cannot_become_ready_without_signing_secret(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_GATEWAY_SERVICE_TOKEN", "synthetic-service-token-value-0123456789")
    monkeypatch.delenv("TEST_GATEWAY_SIGNING_SECRET", raising=False)
    monkeypatch.setenv("TEST_UPSTREAM_KEY", "test-only-secret")
    monkeypatch.setenv("TEST_COMPILER_KEY", "compiler-only-synthetic-token")
    settings = _signed_settings(tmp_path)
    app = create_app(settings, httpx.MockTransport(_healthy_upstream_handler()))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://adapter.test"
    ) as client:
        ready = await client.get("/readyz")
    assert ready.status_code == 503
    assert ready.json()["gateway_ingress"] == "unavailable"


def test_static_identity_cannot_coexist_with_signed_request_identity() -> None:
    with pytest.raises(ValidationError, match="forbids static identity"):
        ConstitutionIntegrationConfig(
            enabled=True,
            identity_source="signed_request",
            principal="local-appliance-principal",
        )
    with pytest.raises(ValidationError, match="forbids static identity"):
        Settings(
            server=ServerConfig(),
            gateway_ingress=GatewayIngressConfig(
                mode="service_bearer_signed_identity_v1",
                service_token_env="TEST_GATEWAY_SERVICE_TOKEN",
                signing_secret_env="TEST_GATEWAY_SIGNING_SECRET",
            ),
            upstream=UpstreamConfig(
                base_url="http://upstream.test/v1",
                api_key_env="TEST_UPSTREAM_KEY",
                model="qwen",
            ),
            routes=[
                RouteConfig(
                    name="vision",
                    model="qwen",
                    max_images_per_request=1,
                    image_overflow_policy="retain_newest",
                    observation_enabled=True,
                    constitution_enabled=True,
                )
            ],
            compiler=CompilerConfig(enabled=True, api_key_env="TEST_COMPILER_KEY"),
            constitution=ConstitutionIntegrationConfig(
                enabled=True,
                identity_source="signed_request",
                session="leaked-static-session",
            ),
        )
    with pytest.raises(ValidationError, match="requires enabled constitution integration"):
        Settings(
            server=ServerConfig(),
            upstream=UpstreamConfig(
                base_url="http://upstream.test/v1",
                api_key_env="TEST_UPSTREAM_KEY",
                model="qwen",
            ),
            routes=[RouteConfig(name="r", model="qwen", image_overflow_policy="passthrough")],
            constitution=ConstitutionIntegrationConfig(identity_source="signed_request"),
        )


@pytest.mark.parametrize(
    "shared_env",
    ["TEST_SHARED_ONE", "TEST_SHARED_TWO", "TEST_SHARED_THREE"],
)
def test_secret_roles_cannot_share_one_env_name(shared_env: str) -> None:
    upstream = UpstreamConfig(
        base_url="http://upstream.test/v1", api_key_env=shared_env, model="qwen"
    )
    route = RouteConfig(
        name="vision",
        model="qwen",
        max_images_per_request=1,
        image_overflow_policy="retain_newest",
        observation_enabled=True,
        constitution_enabled=True,
    )
    for ingress in (
        GatewayIngressConfig(
            mode="service_bearer_signed_identity_v1",
            service_token_env=shared_env,
            signing_secret_env="TEST_DISTINCT_SIGNING",
        ),
        GatewayIngressConfig(
            mode="service_bearer_signed_identity_v1",
            service_token_env="TEST_DISTINCT_SERVICE",
            signing_secret_env=shared_env,
        ),
    ):
        with pytest.raises(ValidationError, match="cannot share one environment name"):
            Settings(
                server=ServerConfig(),
                gateway_ingress=ingress,
                upstream=upstream,
                routes=[route],
                compiler=CompilerConfig(enabled=True, api_key_env=shared_env),
                constitution=ConstitutionIntegrationConfig(
                    enabled=True, identity_source="signed_request"
                ),
            )


def test_development_template_is_labeled_development_not_production() -> None:
    text = DEVELOPMENT_TEMPLATE.read_text(encoding="utf-8")
    header = text.splitlines()[:12]
    joined = "\n".join(header)
    assert "development" in joined.lower()
    rendered = tomllib.loads(
        text.replace("__UPSTREAM_BASE_URL__", "http://127.0.0.1:18020/v1").replace(
            "__UPSTREAM_MODEL__", "qwen3.8-27b"
        )
    )
    assert rendered["gateway_ingress"]["mode"] == "disabled"
    # The development template must not claim to be the final production path.
    assert "FINAL Gateway-integrated" not in text


def test_gateway_integrated_template_is_labeled_final_gateway_integrated() -> None:
    text = GATEWAY_TEMPLATE.read_text(encoding="utf-8")
    header = text.splitlines()[:12]
    assert any("FINAL Gateway-integrated" in line for line in header)
    rendered = tomllib.loads(_render_gateway_template())
    assert rendered["gateway_ingress"]["mode"] == "service_bearer_signed_identity_v1"


PUBLIC_BINDING_LITERALS = ("0.0.0.0", "[::]:")


def test_no_public_binding_in_deployment_assets() -> None:
    assets = [
        GATEWAY_TEMPLATE,
        DEVELOPMENT_TEMPLATE,
        TOPOLOGY_DOC,
        TOPOLOGY_MANIFEST,
        SERVICE_UNIT,
        CUTOVER_RUNBOOK,
    ]
    for asset in assets:
        text = asset.read_text(encoding="utf-8")
        # The unit and runbook legitimately document the protected fixture's
        # pre-existing 0.0.0.0:18020 listener fact only as a class in the
        # topology document; no Local adapter binding may be public.
        for line in text.splitlines():
            if "listen_host" in line or "IPAddressAllow" in line or "endpoint" in line.lower():
                for literal in PUBLIC_BINDING_LITERALS:
                    assert literal not in line, (asset, line)
    unit = SERVICE_UNIT.read_text(encoding="utf-8")
    assert "IPAddressDeny=any" in unit
    assert "IPAddressAllow=127.0.0.0/8" in unit
    assert "IPAddressAllow=::1/128" in unit
    gateway_config = tomllib.loads(_render_gateway_template())
    assert gateway_config["server"]["listen_host"] == "127.0.0.1"
    assert gateway_config["observability"]["metrics_host"] == "127.0.0.1"


# ---------------------------------------------------------------------------
# Objective 011-a workstream A4: exactly three documented placeholders; the
# substituted loopback variant and the substituted non-loopback variant both
# parse; the non-loopback variant is rejected by the validators when
# gateway_ingress is disabled or static (fail closed).
# ---------------------------------------------------------------------------


def test_gateway_integrated_non_loopback_variant_parses_under_full_signed_ingress() -> None:
    rendered = _render_gateway_template("172.17.0.1")
    assert "__" not in rendered
    config = tomllib.loads(rendered)
    assert config["server"]["listen_host"] == "172.17.0.1"
    assert config["gateway_ingress"]["mode"] == "service_bearer_signed_identity_v1"

    from slaif_local_coding.config import load_settings

    path = REPO_ROOT / ".tmp-gateway-integrated-nonloopback.toml"
    path.write_text(rendered, encoding="utf-8")
    try:
        settings = load_settings(path)
    finally:
        path.unlink()
    assert settings.server.listen_host == "172.17.0.1"
    assert settings.gateway_ingress.signed is True


@pytest.mark.parametrize("mode", ["disabled", "service_bearer_static_identity"])
def test_gateway_integrated_non_loopback_variant_fails_closed_without_full_signed_ingress(
    mode: str,
) -> None:
    rendered = _render_gateway_template("172.17.0.1")
    # Rewrite the rendered final template into a non-loopback variant WITHOUT
    # the full signed ingress contract. The rewrite keeps the variant
    # otherwise validator-valid (mode-appropriate identity) so that the D1
    # binding law is the first-class contract under test.
    rendered = rendered.replace(
        'mode = "service_bearer_signed_identity_v1"',
        f'mode = "{mode}"',
    )
    rendered = rendered.replace('signing_secret_env = "SLAIF_ADAPTER_SIGNING_SECRET"\n', "")
    if mode == "disabled":
        # disabled ingress cannot keep the service token env either.
        rendered = rendered.replace('service_token_env = "SLAIF_ADAPTER_SERVICE_TOKEN"\n', "")
    rendered = rendered.replace(
        'identity_source = "signed_request"',
        'identity_source = "static"\nprincipal = "a"\nsession = "b"\nrepository = "c"',
    )

    from slaif_local_coding.config import load_settings

    path = REPO_ROOT / ".tmp-gateway-integrated-nonloopback-nomode.toml"
    path.write_text(rendered, encoding="utf-8")
    try:
        with pytest.raises(ValidationError, match="service_bearer_signed_identity_v1"):
            load_settings(path)
    finally:
        path.unlink()


def test_gateway_integrated_all_interfaces_variant_parses_under_full_signed_ingress() -> None:
    rendered = _render_gateway_template("0.0.0.0")
    assert "__" not in rendered
    from slaif_local_coding.config import load_settings

    path = REPO_ROOT / ".tmp-gateway-integrated-allif.toml"
    path.write_text(rendered, encoding="utf-8")
    try:
        settings = load_settings(path)
    finally:
        path.unlink()
    assert settings.server.listen_host == "0.0.0.0"
    assert settings.gateway_ingress.signed is True


# ---------------------------------------------------------------------------
# Objective 011-a workstream B7: the canonical compose is the production
# Docker MVP path; the documented development variant (ingress disabled,
# loopback) is a separate clearly-labeled example that is never production.
# ---------------------------------------------------------------------------

COMPOSE_FILE = REPO_ROOT / "compose.yaml"
DOCKER_INSTALL_DOC = REPO_ROOT / "docs" / "DOCKER-INSTALL.md"


def test_compose_is_labeled_canonical_production_docker_path() -> None:
    text = COMPOSE_FILE.read_text(encoding="utf-8")
    header = text.splitlines()[:16]
    assert any("canonical" in line.lower() for line in header)
    assert any("production" in line.lower() for line in header)
    # host networking law (D2), no published ports, no secret interpolation.
    assert "network_mode: host" in text
    assert "ports:" not in text
    assert "privileged" not in text
    for secret_env in (
        "SLAIF_ADAPTER_SERVICE_TOKEN=",
        "SLAIF_ADAPTER_SIGNING_SECRET=",
        "QWEN3090_API_KEY=",
    ):
        assert secret_env not in text


def test_development_docker_variant_is_labeled_development_not_production() -> None:
    text = DOCKER_INSTALL_DOC.read_text(encoding="utf-8")
    assert "development" in text.lower()
    # The development variant must be labeled as NOT production.
    lowered = text.lower()
    dev_positions = [m.start() for m in re.finditer(r"development variant", lowered)]
    assert dev_positions, "the development variant section must exist"
    tail = text[dev_positions[0] : dev_positions[0] + 2000].lower()
    assert "not production" in tail or "development only" in tail
