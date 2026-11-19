import re
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from slaif_local_coding.config import (
    V1_CAPABILITY_NOT_PINNED,
    V1_LEGACY_CACHE_CONFLICT,
    V1_LEGACY_COMPILER_CONFLICT,
    V1_LEGACY_POLICY_CONFLICT,
    V1_LEGACY_REHYDRATION_CONFLICT,
    V1_ROUTE_CONTRACT_CONTEXT_MISMATCH,
    V1_ROUTE_CONTRACT_MISSING,
    V1_ROUTE_CONTRACT_MODEL_MISMATCH,
    V1_ROUTE_CONTRACT_ORPHAN,
    CacheConfig,
    CompilerConfig,
    ConstitutionIntegrationConfig,
    ContextCacheConfig,
    GatewayIngressConfig,
    ObservationPolicy,
    RehydrationConfig,
    RouteConfig,
    ServerConfig,
    Settings,
    UpstreamConfig,
    load_settings,
    validate_service_token,
)
from slaif_local_coding.constitution.bundles.bundle_admission_models import EntryClass
from slaif_local_coding.constitution.bundles.bundle_budget import BundleBudgetConfig
from slaif_local_coding.constitution.bundles.bundle_compiler import (
    BundleCompilerConfig,
    derive_compile_key,
)
from slaif_local_coding.constitution.bundles.ram_state_models import RamStateBounds


@pytest.mark.parametrize(
    "character",
    [*(chr(code) for code in range(0x00, 0x21)), chr(0x7F), "\u00a0", "\u2003", "é"],
)
def test_service_token_validator_rejects_non_visible_ascii(character: str) -> None:
    with pytest.raises(ValueError, match="credential is invalid"):
        validate_service_token(f"x{character}x")


@pytest.mark.parametrize("token", [" leading", "trailing ", "two words", ""])
def test_service_token_validator_rejects_empty_or_embedded_whitespace(token: str) -> None:
    with pytest.raises(ValueError, match="credential is invalid"):
        validate_service_token(token)


def test_service_token_validator_uses_encoded_byte_boundaries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from slaif_local_coding.config import MAX_SERVICE_TOKEN_BYTES

    one = "x"
    maximum = "x" * MAX_SERVICE_TOKEN_BYTES
    over = "x" * (MAX_SERVICE_TOKEN_BYTES + 1)
    assert validate_service_token(one) == one
    assert validate_service_token(maximum) == maximum
    with pytest.raises(ValueError, match="credential is invalid"):
        validate_service_token(over)

    config = GatewayIngressConfig(
        mode="service_bearer_static_identity", service_token_env="TEST_ADAPTER_TOKEN"
    )
    monkeypatch.setenv("TEST_ADAPTER_TOKEN", maximum)
    assert config.service_token() == maximum
    monkeypatch.setenv("TEST_ADAPTER_TOKEN", over)
    with pytest.raises(ValueError, match="credential is invalid"):
        config.service_token()


def test_gateway_ingress_contract_is_strict_and_disabled_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert GatewayIngressConfig().mode == "disabled"
    with pytest.raises(ValidationError):
        GatewayIngressConfig(mode="service_bearer_static_identity")
    with pytest.raises(ValidationError):
        GatewayIngressConfig(mode="disabled", service_token_env="TEST_TOKEN")
    with pytest.raises(ValidationError):
        GatewayIngressConfig(
            mode="service_bearer_static_identity", service_token_env="not-valid-name"
        )

    enabled = GatewayIngressConfig(
        mode="service_bearer_static_identity", service_token_env="TEST_ADAPTER_TOKEN"
    )
    monkeypatch.setenv("TEST_ADAPTER_TOKEN", "adapter-only-synthetic-token")
    assert enabled.service_token() == "adapter-only-synthetic-token"
    monkeypatch.setenv("TEST_ADAPTER_TOKEN", "invalid\nvalue")
    with pytest.raises(ValueError, match="credential is invalid"):
        enabled.service_token()


def test_signed_replay_bounds_are_strict_and_request_horizon_preserves_ttl_relation() -> None:
    defaults = GatewayIngressConfig()
    assert defaults.clock_skew_seconds == 60
    assert defaults.replay_ttl_seconds == 60
    assert defaults.max_replay_entries == 4096

    signed: dict[str, Any] = {
        "mode": "service_bearer_signed_identity_v1",
        "service_token_env": "TEST_ADAPTER_TOKEN",
        "signing_secret_env": "TEST_SIGNING_SECRET",
    }
    invalid_bounds = (
        {"clock_skew_seconds": 0},
        {"clock_skew_seconds": 301},
        {"replay_ttl_seconds": 0},
        {"replay_ttl_seconds": 86_401},
        {"max_replay_entries": 0},
        {"max_replay_entries": 1_000_001},
        {"clock_skew_seconds": True},
        {"replay_ttl_seconds": 60.0},
        {"max_replay_entries": "4096"},
    )
    for update in invalid_bounds:
        with pytest.raises(ValidationError):
            GatewayIngressConfig(**signed, **update)
    with pytest.raises(ValidationError, match="replay TTL must cover clock skew"):
        GatewayIngressConfig(**signed, clock_skew_seconds=60, replay_ttl_seconds=59)

    valid = GatewayIngressConfig(
        **signed,
        clock_skew_seconds=300,
        replay_ttl_seconds=300,
        max_replay_entries=1_000_000,
    )
    assert valid.signed


def test_gateway_ingress_requires_complete_static_identity() -> None:
    upstream = UpstreamConfig(base_url="http://upstream.test/v1", api_key_env="KEY", model="m")
    route = RouteConfig(name="r", model="m", image_overflow_policy="passthrough")
    with pytest.raises(ValidationError, match="complete enabled static constitution identity"):
        Settings(
            server=ServerConfig(),
            gateway_ingress=GatewayIngressConfig(
                mode="service_bearer_static_identity", service_token_env="TEST_ADAPTER_TOKEN"
            ),
            upstream=upstream,
            routes=[route],
        )


def test_non_loopback_and_unknown_policy_fail_closed() -> None:
    with pytest.raises(ValidationError):
        ServerConfig(listen_host="hostname.example")
    with pytest.raises(ValidationError):
        ServerConfig(listen_host="127.0.0.1:8000")
    with pytest.raises(ValidationError):
        RouteConfig(name="x", model="m", image_overflow_policy="guess")  # type: ignore[arg-type]
    assert (
        RouteConfig(name="x", model="m", image_overflow_policy="passthrough").responses_tool_policy
        == "passthrough"
    )
    with pytest.raises(ValidationError):
        RouteConfig(
            name="x",
            model="m",
            image_overflow_policy="passthrough",
            responses_tool_policy="guess",  # type: ignore[arg-type]
        )
    with pytest.raises(ValidationError):
        ServerConfig(json_max_nesting_depth=257)
    with pytest.raises(ValidationError):
        ObservationPolicy(max_roots=0)
    with pytest.raises(ValidationError):
        RouteConfig(name="x", model="m", image_overflow_policy="reject")
    with pytest.raises(ValidationError):
        RouteConfig(
            name="x", model="m", max_images_per_request=1, image_overflow_policy="passthrough"
        )
    with pytest.raises(ValidationError):
        CacheConfig(root=Path("relative-cache"))
    with pytest.raises(ValidationError):
        UpstreamConfig(
            base_url="http://user:password@upstream.test/v1", api_key_env="KEY", model="m"
        )
    with pytest.raises(ValidationError):
        UpstreamConfig(base_url="http://upstream.test:bad/v1", api_key_env="KEY", model="m")


def test_future_feature_and_raw_logging_configuration_fail_closed(tmp_path: Path) -> None:
    base = """
[server]
[upstream]
base_url = "http://upstream.test/v1"
api_key_env = "TEST_KEY"
model = "m"
[[routes]]
name = "r"
model = "m"
image_overflow_policy = "passthrough"
"""
    for unsafe in ("[observability]\nlog_raw_payloads = true\n",):
        path = tmp_path / "unsafe.toml"
        path.write_text(base + unsafe)
        with pytest.raises(ValueError):
            load_settings(path)
    unknown = tmp_path / "unknown.toml"
    unknown.write_text(base + '[observability]\nfuture_label = "private"\n')
    with pytest.raises(ValueError):
        load_settings(unknown)


def test_route_matches_must_be_unique_per_model_and_endpoint() -> None:
    upstream = UpstreamConfig(base_url="http://upstream.test", api_key_env="KEY", model="m")
    first = RouteConfig(name="first", model="m", image_overflow_policy="passthrough")
    with pytest.raises(ValidationError, match="uniquely match"):
        Settings(
            server=ServerConfig(),
            upstream=upstream,
            routes=[first, first.model_copy(update={"name": "second"})],
        )

    responses = first.model_copy(update={"enable_chat_completions": False})
    chat = first.model_copy(
        update={"name": "chat", "enable_responses": False, "enable_chat_completions": True}
    )
    assert (
        len(Settings(server=ServerConfig(), upstream=upstream, routes=[responses, chat]).routes)
        == 2
    )


def test_objective003b_configuration_defaults_and_safe_enablement(tmp_path: Path) -> None:
    base = """
[server]
[upstream]
base_url = "http://127.0.0.1:18020/v1"
api_key_env = "TEST_KEY"
model = "m"
[[routes]]
name = "r"
model = "m"
image_overflow_policy = "passthrough"
"""
    path = tmp_path / "adapter.toml"
    path.write_text(
        base
        + """
[compiler]
enabled = false
max_parallel_calls = 1
max_output_tokens = 3000
[cache]
root = "/dev/shm/slaif-local-coding-test"
fallback_root = "/tmp/slaif-local-coding-fallback-test"
max_entry_bytes = 65536
max_pinned_bytes = 8388608
[constitution]
enabled = false
compile_failure_policy = "preserve_original"
[observability]
log_raw_payloads = false
"""
    )
    loaded = load_settings(path)
    assert loaded.compiler.enabled is False
    assert loaded.constitution.enabled is False
    assert loaded.routes[0].constitution_enabled is False
    assert loaded.cache.max_pinned_bytes <= loaded.cache.max_total_bytes

    safe = (
        base
        + """
[compiler]
enabled = true
max_parallel_calls = 1
max_output_tokens = 3000
[cache]
root = "/dev/shm/slaif-local-coding-test"
fallback_root = "/tmp/slaif-local-coding-fallback-test"
[constitution]
enabled = true
principal = "local-principal"
session = "local-session"
repository = "local-repository"
[[routes]]
name = "enabled"
model = "m2"
image_overflow_policy = "passthrough"
observation_enabled = true
constitution_enabled = true
[observability]
log_raw_payloads = false
"""
    )
    enabled_path = tmp_path / "enabled.toml"
    enabled_path.write_text(safe)
    enabled = load_settings(enabled_path)
    assert enabled.constitution.principal == "local-principal"
    assert enabled.routes[-1].constitution_enabled is True

    unsafe_combinations = [
        base + "[constitution]\nenabled = true\n[observability]\nlog_raw_payloads = false\n",
        base
        + "[compiler]\nenabled = true\n[constitution]\nenabled = true\n"
        + 'principal = "p"\nsession = "s"\nrepository = "r"\n'
        + "[observability]\nlog_raw_payloads = false\n",
        base
        + "[compiler]\nenabled = true\n[constitution]\nenabled = true\n"
        + 'principal = "p"\nsession = "s"\nrepository = "r"\n'
        + '[[routes]]\nname = "bad-route"\nmodel = "m"\n'
        + 'image_overflow_policy = "passthrough"\nenable_responses = false\n'
        + "constitution_enabled = true\n[observability]\nlog_raw_payloads = false\n",
        base
        + "[cache]\nmax_total_bytes = 1000\nmax_entry_bytes = 2000\n"
        + "[observability]\nlog_raw_payloads = false\n",
    ]
    for unsafe in unsafe_combinations:
        (tmp_path / "unsafe.toml").write_text(unsafe)
        with pytest.raises(ValidationError):
            load_settings(tmp_path / "unsafe.toml")


def test_current_endpoint_migration_and_historical_provenance() -> None:
    with Path("config/adapter.example.toml").open("rb") as stream:
        example = tomllib.load(stream)
    assert example["upstream"]["base_url"] == "http://127.0.0.1:18020/v1"
    assert example["server"]["listen_port"] == 18031
    assert example["compiler"]["enabled"] is False
    assert example["compiler"]["schema_version"] == "constitution-index-v1"
    assert example["constitution"]["enabled"] is False

    live_document = Path("docs/LIVE-TEST-ENVIRONMENT.md").read_text()
    assert "http://127.0.0.1:18020/v1" in live_document
    assert "http://10.8.132.75:18020/v1" in live_document
    assert "Historical upstream" in live_document
    # This value is intentionally retained in the immutable reference prototype.
    reference = Path("references/qwen38_vision_image_cap_proxy.py").read_text()
    assert "10.8.132.76" in reference


def test_current_host_capability_records_fixture_scoped_vision_acceptance() -> None:
    live_document = Path("docs/LIVE-TEST-ENVIRONMENT.md").read_text()
    architecture = Path("ARCHITECTURE.md").read_text()
    readme = Path("README.md").read_text()
    assert "Accepted image capacity: one image per request" in live_document
    assert "text-only" in live_document.lower()
    assert "vision-enabled human-gated fixture" in live_document
    assert "Vision acceptance" in architecture
    assert "docs/VISION-ACCEPTANCE.md" in architecture
    assert "Qwen3.8-27B/vLLM on one RTX 3090" in architecture
    assert "Qwen/vLLM text-only service" not in architecture
    assert "http://10.8.132.75:18020/v1" in live_document
    assert "10.8.132.76" in live_document
    assert "generic or production" in live_document
    assert "one image per request" in readme
    assert "fixture-scoped" in readme


def test_cache_and_compiler_bounds_have_safe_defaults_and_finite_ranges(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg-cache"))
    cache = CacheConfig()
    compiler = CompilerConfig()
    assert cache.fallback_root == tmp_path / "xdg-cache" / "slaif-local-coding"
    assert cache.fallback_root != Path("/tmp/slaif-local-coding-cache")
    assert cache.fallback_root.is_relative_to(tmp_path / "xdg-cache")
    assert cache.max_scan_entries == 4096
    assert compiler.max_source_bytes == 262_144
    assert compiler.max_candidates == 128
    assert compiler.max_json_depth == 24

    invalid_cache_calls: list[Callable[[], CacheConfig]] = [
        lambda: CacheConfig(max_scan_entries=0),
        lambda: CacheConfig(max_scan_entries=1_000_001),
        lambda: CacheConfig(max_entry_bytes=0),
        lambda: CacheConfig(max_total_bytes=1023),
    ]
    for invalid_call in invalid_cache_calls:
        with pytest.raises(ValidationError):
            invalid_call()

    constitution = ConstitutionIntegrationConfig()
    assert constitution.enabled is False
    assert constitution.selector_schema_version == "working-set-v1"
    assert constitution.render_version == "constitution-render-v1"
    assert constitution.working_set_max_entries == 128
    assert constitution.acquisition_max_count == 128
    assert constitution.entry_render_max_bytes == 8192
    assert constitution.injection_max_depth == 64
    assert constitution.injection_max_nodes == 16384

    invalid_constitution_calls: list[Callable[[], ConstitutionIntegrationConfig]] = [
        lambda: ConstitutionIntegrationConfig(enabled=True),
        lambda: ConstitutionIntegrationConfig(entry_render_max_bytes=16385),
        lambda: ConstitutionIntegrationConfig(working_set_max_entries=129),
        lambda: ConstitutionIntegrationConfig(acquisition_max_count=129),
        lambda: ConstitutionIntegrationConfig(injection_max_depth=257),
        lambda: ConstitutionIntegrationConfig(injection_max_nodes=0),
    ]
    for invalid_constitution_call in invalid_constitution_calls:
        with pytest.raises(ValidationError):
            invalid_constitution_call()

    invalid_compiler_calls: list[Callable[[], CompilerConfig]] = [
        lambda: CompilerConfig(max_source_bytes=0),
        lambda: CompilerConfig(max_candidates=0),
        lambda: CompilerConfig(max_json_depth=0),
        lambda: CompilerConfig(max_output_tokens=127),
        lambda: CompilerConfig(timeout_seconds=0),
    ]
    for invalid_compiler_call in invalid_compiler_calls:
        with pytest.raises(ValidationError):
            invalid_compiler_call()


def test_rehydration_bounds_fail_closed() -> None:
    with pytest.raises(ValidationError):
        ConstitutionIntegrationConfig(
            enabled=False,
            rehydration=RehydrationConfig(max_entry_bytes=2000, max_total_bytes=1000),
        )
    valid = ConstitutionIntegrationConfig(
        rehydration=RehydrationConfig(
            ttl_seconds=1,
            max_entries=1,
            max_entry_bytes=1024,
            max_total_bytes=1024,
        )
    )
    assert valid.rehydration.max_total_bytes == 1024


# ---------------------------------------------------------------------------
# Objective 011-a workstream A2: LAN-visible binding law configuration matrix
# (pure unit, no network). Loopback x {disabled, static, signed} valid;
# non-loopback literal x {disabled, static} rejected; non-loopback literal x
# signed valid; 0.0.0.0/:: x signed valid; hostname rejected in every mode;
# the three distinct secret-role names remain enforced (010 C2 invariant).
# ---------------------------------------------------------------------------


def _matrix_settings(
    listen_host: str,
    mode: str,
) -> Settings:
    observation_enabled = True
    constitution_enabled = True
    if mode == "service_bearer_static_identity":
        ingress = GatewayIngressConfig(
            mode="service_bearer_static_identity",
            service_token_env="MATRIX_SERVICE_TOKEN",
        )
        constitution = ConstitutionIntegrationConfig(
            enabled=True,
            identity_source="static",
            principal="matrix-principal",
            session="matrix-session",
            repository="matrix-repository",
        )
    elif mode == "service_bearer_signed_identity_v1":
        ingress = GatewayIngressConfig(
            mode="service_bearer_signed_identity_v1",
            service_token_env="MATRIX_SERVICE_TOKEN",
            signing_secret_env="MATRIX_SIGNING_SECRET",
        )
        constitution = ConstitutionIntegrationConfig(enabled=True, identity_source="signed_request")
    else:
        ingress = GatewayIngressConfig()
        constitution = ConstitutionIntegrationConfig()
        observation_enabled = False
        constitution_enabled = False
    return Settings(
        server=ServerConfig(listen_host=listen_host),
        gateway_ingress=ingress,
        upstream=UpstreamConfig(
            base_url="http://upstream.test/v1", api_key_env="MATRIX_KEY", model="qwen"
        ),
        routes=[
            RouteConfig(
                name="matrix-route",
                model="qwen",
                max_images_per_request=1,
                image_overflow_policy="retain_newest",
                observation_enabled=observation_enabled,
                constitution_enabled=constitution_enabled,
            )
        ],
        compiler=CompilerConfig(enabled=True, api_key_env="MATRIX_COMPILER_KEY"),
        constitution=constitution,
    )


@pytest.mark.parametrize(
    ("listen_host", "mode"),
    [
        # loopback x every mode: valid
        ("127.0.0.1", "disabled"),
        ("::1", "disabled"),
        ("localhost", "disabled"),
        ("127.0.0.1", "service_bearer_static_identity"),
        ("::1", "service_bearer_static_identity"),
        ("localhost", "service_bearer_static_identity"),
        ("127.0.0.1", "service_bearer_signed_identity_v1"),
        ("::1", "service_bearer_signed_identity_v1"),
        ("localhost", "service_bearer_signed_identity_v1"),
        # non-loopback bare literal x signed: valid
        ("172.17.0.1", "service_bearer_signed_identity_v1"),
        ("10.88.0.9", "service_bearer_signed_identity_v1"),
        ("fe80::1", "service_bearer_signed_identity_v1"),
        # all-interfaces literals x signed: valid
        ("0.0.0.0", "service_bearer_signed_identity_v1"),
        ("::", "service_bearer_signed_identity_v1"),
    ],
)
def test_binding_law_matrix_accepts(listen_host: str, mode: str) -> None:
    settings = _matrix_settings(listen_host, mode)
    assert settings.server.listen_host == listen_host
    assert settings.gateway_ingress.mode == mode


@pytest.mark.parametrize(
    ("listen_host", "mode"),
    [
        # non-loopback literal x {disabled, static}: rejected
        ("172.17.0.1", "disabled"),
        ("10.88.0.9", "disabled"),
        ("fe80::1", "disabled"),
        ("0.0.0.0", "disabled"),
        ("::", "disabled"),
        ("172.17.0.1", "service_bearer_static_identity"),
        ("0.0.0.0", "service_bearer_static_identity"),
        ("::", "service_bearer_static_identity"),
    ],
)
def test_binding_law_matrix_rejects_non_loopback_without_full_signed_ingress(
    listen_host: str, mode: str
) -> None:
    with pytest.raises(ValidationError, match="service_bearer_signed_identity_v1"):
        _matrix_settings(listen_host, mode)


@pytest.mark.parametrize(
    "host",
    ["hostname.example", "myhost", "http://127.0.0.1", "127.0.0.1:8000", "256.0.0.1"],
)
@pytest.mark.parametrize(
    "mode",
    [
        "disabled",
        "service_bearer_static_identity",
        "service_bearer_signed_identity_v1",
    ],
)
def test_binding_law_matrix_rejects_hostname_in_every_mode(host: str, mode: str) -> None:
    with pytest.raises(ValidationError):
        _matrix_settings(host, mode)


def test_binding_law_default_is_unchanged_loopback() -> None:
    settings = _matrix_settings("127.0.0.1", "disabled")
    assert settings.server.listen_host == "127.0.0.1"
    assert ServerConfig().listen_host == "127.0.0.1"


def test_binding_law_keeps_distinct_secret_role_names_enforced() -> None:
    # 010 C2 invariant: shared env names across the three Local-side secret
    # roles still fail closed, including on a signed non-loopback bind.
    with pytest.raises(ValidationError, match="cannot share one environment name"):
        Settings(
            server=ServerConfig(listen_host="0.0.0.0"),
            gateway_ingress=GatewayIngressConfig(
                mode="service_bearer_signed_identity_v1",
                service_token_env="SHARED_ROLE_NAME",
                signing_secret_env="MATRIX_SIGNING_SECRET",
            ),
            upstream=UpstreamConfig(
                base_url="http://upstream.test/v1", api_key_env="SHARED_ROLE_NAME", model="qwen"
            ),
            routes=[
                RouteConfig(
                    name="matrix-route",
                    model="qwen",
                    max_images_per_request=1,
                    image_overflow_policy="retain_newest",
                    observation_enabled=True,
                    constitution_enabled=True,
                )
            ],
            compiler=CompilerConfig(enabled=True, api_key_env="SHARED_ROLE_NAME"),
            constitution=ConstitutionIntegrationConfig(
                enabled=True, identity_source="signed_request"
            ),
        )


# ---------------------------------------------------------------------------
# 022-a: the [context_cache] profile selector, the closed v1 configuration,
# the legacy/v1 migration law, and the existing 021 identity recipe
# (pure configuration unit tests; no store IO, no upstream calls).
# ---------------------------------------------------------------------------

V1_REVISION_A = "a" * 40
V1_REVISION_B = "b" * 40
V1_COMPAT_A = "slaif-rtx3090-compat-1"
V1_COMPAT_B = "slaif-rtx3090-compat-2"
V1_UPSTREAM_KEY_ENV = "TEST_V1_UPSTREAM_KEY"
V1_COMPILER_KEY_ENV = "TEST_V1_COMPILER_KEY"
V1_EFFECTIVE_C = 32_768


def _v1_route_contract(route_model: str, context_tokens: int = V1_EFFECTIVE_C) -> dict[str, Any]:
    return {"model": route_model, "context_tokens": context_tokens}


def _v1_route_contracts(
    routes: list[dict[str, Any]], context_tokens: int = V1_EFFECTIVE_C
) -> dict[str, Any]:
    return {
        route["name"]: _v1_route_contract(route["model"], context_tokens)
        for route in routes
        if route.get("constitution_enabled")
    }


def _v1_budget(**over: Any) -> dict[str, Any]:
    value: dict[str, Any] = {"context_tokens": V1_EFFECTIVE_C, "vision_enabled": False}
    value.update(over)
    return value


def _v1_compiler(**over: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "model": "qwen38-27b",
        "base_url": "http://127.0.0.1:18020/v1",
        "model_revision": V1_REVISION_A,
        "compatibility_identity": V1_COMPAT_A,
        "api_key_env": V1_COMPILER_KEY_ENV,
    }
    value.update(over)
    return value


def _v1_ram(**over: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "session_max_owned_bytes": 128 * 1024 * 1024,
        "process_max_owned_bytes": 512 * 1024 * 1024,
    }
    value.update(over)
    return value


def _v1_recovery(**over: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "enabled": True,
        "root": "/dev/shm/slaif-v1-recovery-test",
    }
    value.update(over)
    return value


def _v1_context_cache(**over: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "profile": "dependency-bundles-v1",
        "budget": _v1_budget(),
        "compiler": _v1_compiler(),
        "ram": _v1_ram(),
        "recovery": _v1_recovery(),
        "route_contracts": {"text": _v1_route_contract("qwen38-27b")},
    }
    value.update(over)
    return value


def _v1_route(**over: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "name": "text",
        "model": "qwen38-27b",
        "image_overflow_policy": "reject",
        "max_images_per_request": 0,
        "observation_enabled": True,
        "constitution_enabled": True,
    }
    value.update(over)
    return value


def _v1_settings_dict(**over: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "server": {"listen_host": "127.0.0.1"},
        "upstream": {
            "base_url": "http://127.0.0.1:18020/v1",
            "api_key_env": V1_UPSTREAM_KEY_ENV,
            "model": "qwen38-27b",
        },
        "routes": [_v1_route()],
        "constitution": {
            "enabled": True,
            "identity_source": "static",
            "principal": "local-principal",
            "session": "local-session",
            "repository": "local-repository",
        },
        "context_cache": _v1_context_cache(),
    }
    value.update(over)
    # Keep the route model contracts in sync with the governed routes
    # unless the caller supplied an explicit context_cache declaration.
    if "context_cache" not in over:
        value["context_cache"]["route_contracts"] = _v1_route_contracts(value["routes"])
    return value


def _legacy_route(**over: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "name": "text",
        "model": "qwen38-27b",
        "image_overflow_policy": "reject",
        "max_images_per_request": 0,
    }
    value.update(over)
    return value


def test_context_cache_profile_defaults_to_legacy_and_keeps_legacy_parity() -> None:
    base: dict[str, Any] = {
        "server": {"listen_host": "127.0.0.1"},
        "upstream": {
            "base_url": "http://127.0.0.1:18020/v1",
            "api_key_env": V1_UPSTREAM_KEY_ENV,
            "model": "qwen38-27b",
        },
        "routes": [_legacy_route()],
    }
    omitted = Settings.model_validate(dict(base))
    explicit = Settings.model_validate({**base, "context_cache": {"profile": "legacy"}})
    assert omitted.context_cache.profile == "legacy"
    assert explicit.context_cache.profile == "legacy"
    omitted_dump = omitted.model_dump()
    explicit_dump = explicit.model_dump()
    omitted_dump.pop("context_cache")
    explicit_dump.pop("context_cache")
    assert omitted_dump == explicit_dump
    assert ContextCacheConfig().profile == "legacy"
    assert ContextCacheConfig().admission_mode == "lean"
    assert ContextCacheConfig().workers == 1
    assert ContextCacheConfig().budget is None
    assert ContextCacheConfig().recovery.enabled is False


def test_context_cache_toml_loading_and_legacy_parity(tmp_path: Path) -> None:
    path = tmp_path / "legacy.toml"
    path.write_text(
        """
[server]
[upstream]
base_url = "http://127.0.0.1:18020/v1"
api_key_env = "TEST_KEY"
model = "qwen38-27b"
[[routes]]
name = "text"
model = "qwen38-27b"
image_overflow_policy = "reject"
max_images_per_request = 0
[compiler]
enabled = false
[cache]
root = "/dev/shm/slaif-local-coding-test"
"""
    )
    loaded = load_settings(path)
    assert loaded.context_cache.profile == "legacy"
    assert loaded.context_cache.budget is None
    assert loaded.context_cache.compiler is None
    assert loaded.context_cache.ram is None
    assert loaded.context_cache.recovery.enabled is False
    assert loaded.context_cache.recovery.root is None
    assert loaded.compiler.enabled is False
    assert loaded.cache.root == Path("/dev/shm/slaif-local-coding-test")


def test_context_cache_unknown_profile_and_unknown_fields_fail_closed() -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate(_v1_settings_dict(context_cache={"profile": "memory"}))
    with pytest.raises(ValidationError):
        Settings.model_validate(
            {
                **_v1_settings_dict(),
                "context_cache": {
                    **_v1_context_cache(),
                    "working_storage": "memory",
                },
            }
        )


@pytest.mark.parametrize(
    "override",
    [
        {"budget": _v1_budget()},
        {"compiler": _v1_compiler()},
        {"ram": _v1_ram()},
        {"recovery": _v1_recovery()},
        {"recovery": {"enabled": True}},
        {"admission_mode": "greedy"},
        {"route_contracts": {"text": _v1_route_contract("qwen38-27b")}},
    ],
    ids=[
        "budget",
        "compiler",
        "ram",
        "recovery",
        "recovery-rootless",
        "greedy",
        "route-contracts",
    ],
)
def test_context_cache_v1_fields_under_legacy_profile_fail_closed(
    override: dict[str, Any],
) -> None:
    context_cache = _v1_context_cache()
    context_cache.update(override)
    context_cache["profile"] = "legacy"
    with pytest.raises(
        ValidationError,
        match="the v1 context-cache settings require the dependency-bundles-v1 profile",
    ):
        Settings.model_validate(_v1_settings_dict(context_cache=context_cache))


def test_context_cache_empty_blocks_do_not_select_v1_fields() -> None:
    # An empty policy block alone is not a supplied setting (022-a law): a
    # legacy profile with an empty [context_cache.recovery] block (and no
    # other supplied v1 field) stays valid.
    settings = Settings.model_validate(
        _v1_settings_dict(
            constitution={"enabled": False},
            context_cache={"profile": "legacy", "recovery": {}},
            routes=[_legacy_route(observation_enabled=False, constitution_enabled=False)],
        )
    )
    assert settings.context_cache.profile == "legacy"
    assert settings.context_cache.recovery.enabled is False


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"budget": None}, "requires the explicit effective-context budget"),
        ({"compiler": None}, "requires the explicit bounded compiler policy"),
        ({"ram": None}, "requires the explicit RAM ownership bounds"),
        (
            {"recovery": {"enabled": False, "root": "/dev/shm/slaif-v1-recovery-test"}},
            "requires the explicit protected-recovery opt-in",
        ),
        (
            {"recovery": {"root": "/dev/shm/slaif-v1-recovery-test"}},
            "requires the explicit protected-recovery opt-in",
        ),
        ({"recovery": {"enabled": True}}, "requires the configured recovery root"),
    ],
)
def test_v1_profile_requires_closed_configuration(override: dict[str, Any], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        Settings.model_validate(_v1_settings_dict(context_cache=_v1_context_cache(**override)))


def test_v1_profile_accepts_closed_configuration_and_admission_modes() -> None:
    settings = Settings.model_validate(_v1_settings_dict())
    assert settings.context_cache.profile == "dependency-bundles-v1"
    assert settings.context_cache.admission_mode == "lean"
    assert settings.context_cache.workers == 1
    assert settings.context_cache.budget is not None
    assert settings.context_cache.budget.context_tokens == 32_768
    assert settings.context_cache.compiler is not None
    assert settings.context_cache.compiler.model_revision == V1_REVISION_A
    assert settings.context_cache.compiler.compatibility_identity == V1_COMPAT_A
    assert settings.context_cache.ram is not None
    assert settings.context_cache.recovery.enabled is True
    greedy = Settings.model_validate(
        _v1_settings_dict(context_cache=_v1_context_cache(admission_mode="greedy"))
    )
    assert greedy.context_cache.admission_mode == "greedy"
    contract = settings.context_cache.route_contracts["text"]
    assert contract.model == "qwen38-27b"
    assert contract.context_tokens == V1_EFFECTIVE_C


def _v1_base_toml() -> str:
    return """
[server]
[upstream]
base_url = "http://127.0.0.1:18020/v1"
api_key_env = "TEST_KEY"
model = "qwen38-27b"
[[routes]]
name = "text"
model = "qwen38-27b"
image_overflow_policy = "reject"
max_images_per_request = 0
observation_enabled = true
constitution_enabled = true
[constitution]
enabled = true
identity_source = "static"
principal = "local-principal"
session = "local-session"
repository = "local-repository"
[context_cache]
profile = "dependency-bundles-v1"
[context_cache.route_contracts.text]
model = "qwen38-27b"
context_tokens = 32768
[context_cache.budget]
context_tokens = 32768
[context_cache.compiler]
model = "qwen38-27b"
base_url = "http://127.0.0.1:18020/v1"
model_revision = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
compatibility_identity = "slaif-rtx3090-compat-1"
api_key_env = "TEST_V1_COMPILER_KEY"
[context_cache.ram]
session_max_owned_bytes = 134217728
process_max_owned_bytes = 536870912
[context_cache.recovery]
enabled = true
root = "/dev/shm/slaif-v1-recovery-test"
"""


def test_v1_toml_loading_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "v1.toml"
    path.write_text(_v1_base_toml())
    loaded = load_settings(path)
    assert loaded.context_cache.profile == "dependency-bundles-v1"
    assert loaded.context_cache.admission_mode == "lean"
    assert loaded.context_cache.budget is not None
    assert loaded.context_cache.budget.context_tokens == 32_768
    assert loaded.context_cache.compiler is not None
    assert loaded.context_cache.compiler.model_revision == V1_REVISION_A
    assert loaded.context_cache.ram is not None
    assert loaded.context_cache.ram.session_max_owned_bytes == 128 * 1024 * 1024
    assert loaded.context_cache.ram.process_max_owned_bytes == 512 * 1024 * 1024
    assert loaded.context_cache.recovery.enabled is True
    assert loaded.context_cache.recovery.root == Path("/dev/shm/slaif-v1-recovery-test")
    contract = loaded.context_cache.route_contracts["text"]
    assert contract.model == "qwen38-27b"
    assert contract.context_tokens == 32_768
    assert contract.render_policy_version == "bundle-render-policy/v1"


@pytest.mark.parametrize(
    ("section", "message"),
    [
        ('[cache]\nroot = "/dev/shm/slaif-local-coding-test"\n', V1_LEGACY_CACHE_CONFLICT),
        ("[cache]\nttl_seconds = 604800\n", V1_LEGACY_CACHE_CONFLICT),
        ("[compiler]\nenabled = false\n", V1_LEGACY_COMPILER_CONFLICT),
        ("max_injected_bytes = 16384\n", V1_LEGACY_POLICY_CONFLICT),
        ("[constitution.rehydration]\nttl_seconds = 3600\n", V1_LEGACY_REHYDRATION_CONFLICT),
    ],
    ids=["cache", "cache-at-default", "compiler", "constitution-policy", "rehydration"],
)
def test_v1_rejects_explicitly_supplied_legacy_policies(
    tmp_path: Path, section: str, message: str
) -> None:
    # An operator supplying an old setting at its default value still
    # supplied a setting (022-a migration law).
    base = _v1_base_toml()
    if section.startswith("max_injected_bytes"):
        # The base document already declares [constitution]; the legacy
        # byte-injection key joins that section explicitly.
        toml = base.replace(
            'repository = "local-repository"\n',
            'repository = "local-repository"\n' + section,
        )
    else:
        toml = base + section
    path = tmp_path / "v1-conflict.toml"
    path.write_text(toml)
    with pytest.raises(ValidationError, match=re.escape(message)):
        load_settings(path)


def test_v1_allows_common_fields_empty_blocks_and_materialized_defaults(
    tmp_path: Path,
) -> None:
    # Common enablement/identity fields are shared by both profiles, and a
    # materialized default or an empty policy block alone does not conflict.
    toml = _v1_base_toml()
    toml = toml.replace(
        """[constitution]
enabled = true
identity_source = "static"
principal = "local-principal"
session = "local-session"
repository = "local-repository"
""",
        """[constitution]
enabled = true
identity_source = "static"
principal = "local-principal"
session = "local-session"
repository = "local-repository"

[cache]

[constitution.rehydration]
""",
    )
    path = tmp_path / "v1-common.toml"
    path.write_text(toml)
    loaded = load_settings(path)
    assert loaded.context_cache.profile == "dependency-bundles-v1"
    assert loaded.constitution.enabled is True
    assert loaded.constitution.principal == "local-principal"


def test_v1_conflict_law_uses_explicit_fields_not_value_equality() -> None:
    # A materialized default constitution instance supplies nothing.
    with pytest.raises(
        ValidationError,
        match="requires enabled constitution integration",
    ):
        Settings.model_validate(
            _v1_settings_dict(
                constitution=ConstitutionIntegrationConfig(),
                routes=[_v1_route(observation_enabled=False, constitution_enabled=False)],
            )
        )
    # An explicitly supplied legacy byte-injection field at its exact default
    # value still counts as supplied.
    with pytest.raises(ValidationError, match=re.escape(V1_LEGACY_POLICY_CONFLICT)):
        Settings.model_validate(
            _v1_settings_dict(
                constitution=ConstitutionIntegrationConfig(
                    enabled=True,
                    identity_source="static",
                    principal="p",
                    session="s",
                    repository="r",
                    max_injected_bytes=16_384,
                )
            )
        )


def test_v1_rehydration_conflict_distinguishes_explicit_defaults() -> None:
    # One actual legacy field explicitly equal to its default: supplied.
    with pytest.raises(ValidationError, match=re.escape(V1_LEGACY_REHYDRATION_CONFLICT)):
        Settings.model_validate(
            _v1_settings_dict(
                constitution=ConstitutionIntegrationConfig(
                    enabled=True,
                    identity_source="static",
                    principal="p",
                    session="s",
                    repository="r",
                    rehydration=RehydrationConfig(ttl_seconds=3600),
                )
            )
        )
    # No field supplied (equivalent to an empty policy block): the conflict
    # law stays silent and the later profile law applies instead.
    with pytest.raises(
        ValidationError,
        match="requires enabled constitution integration",
    ):
        Settings.model_validate(
            _v1_settings_dict(
                constitution=ConstitutionIntegrationConfig(rehydration=RehydrationConfig()),
                routes=[_v1_route(observation_enabled=False, constitution_enabled=False)],
            )
        )


def test_v1_vision_contract_matches_enabled_route_declarations() -> None:
    vision_budget = _v1_budget(vision_enabled=True, per_image_reserve=4_096, max_retained_images=4)
    vision_route = _v1_route(image_overflow_policy="retain_newest", max_images_per_request=1)
    ok = Settings.model_validate(
        _v1_settings_dict(
            routes=[vision_route], context_cache=_v1_context_cache(budget=vision_budget)
        )
    )
    budget = ok.context_cache.budget
    assert budget is not None and budget.vision_enabled is True
    # The explicitly zero-capped route is the text-only control.
    ok_text = Settings.model_validate(_v1_settings_dict())
    budget = ok_text.context_cache.budget
    assert budget is not None and budget.vision_enabled is False
    with pytest.raises(
        ValidationError,
        match="the v1 budget vision contract does not match the enabled route image policy",
    ):
        Settings.model_validate(
            _v1_settings_dict(context_cache=_v1_context_cache(budget=vision_budget))
        )
    with pytest.raises(
        ValidationError,
        match="one v1 context contract cannot serve both vision and text-only routes",
    ):
        Settings.model_validate(
            _v1_settings_dict(
                routes=[
                    vision_route,
                    _v1_route(name="alt-text", model="qwen38-27b-alt"),
                ],
                context_cache=_v1_context_cache(
                    budget=vision_budget,
                    route_contracts={
                        "text": _v1_route_contract("qwen38-27b"),
                        "alt-text": _v1_route_contract("qwen38-27b-alt"),
                    },
                ),
            )
        )
    with pytest.raises(
        ValidationError,
        match="the v1 budget retained-image capacity cannot cover the route image limit",
    ):
        Settings.model_validate(
            _v1_settings_dict(
                routes=[_v1_route(image_overflow_policy="retain_newest", max_images_per_request=2)],
                context_cache=_v1_context_cache(
                    budget=_v1_budget(
                        vision_enabled=True,
                        per_image_reserve=4_096,
                        max_retained_images=1,
                    )
                ),
            )
        )


def test_v1_passthrough_route_may_use_declared_vision_contract() -> None:
    # A passthrough route declares no enforced image limit; it may use the
    # explicitly declared v1 vision contract (and a text contract).
    vision_budget = _v1_budget(vision_enabled=True, per_image_reserve=4_096, max_retained_images=4)
    passthrough = _v1_route(image_overflow_policy="passthrough", max_images_per_request=None)
    ok_vision = Settings.model_validate(
        _v1_settings_dict(
            routes=[passthrough], context_cache=_v1_context_cache(budget=vision_budget)
        )
    )
    assert ok_vision.routes[0].image_overflow_policy == "passthrough"
    budget = ok_vision.context_cache.budget
    assert budget is not None and budget.vision_enabled is True
    ok_text = Settings.model_validate(
        _v1_settings_dict(routes=[passthrough], context_cache=_v1_context_cache())
    )
    budget = ok_text.context_cache.budget
    assert budget is not None and budget.vision_enabled is False
    # Compatible routes that explicitly share one contract: a capped vision
    # alias and a passthrough alias under the same declared capability,
    # each binding its own explicit route model contract.
    shared = Settings.model_validate(
        _v1_settings_dict(
            routes=[
                _v1_route(image_overflow_policy="retain_newest", max_images_per_request=1),
                {**passthrough, "name": "alt-passthrough", "model": "qwen38-27b-alt"},
            ],
            context_cache=_v1_context_cache(
                budget=vision_budget,
                route_contracts={
                    "text": _v1_route_contract("qwen38-27b"),
                    "alt-passthrough": _v1_route_contract("qwen38-27b-alt"),
                },
            ),
        )
    )
    budget = shared.context_cache.budget
    assert budget is not None and budget.vision_enabled is True


def test_v1_reuses_021_vision_reserve_law() -> None:
    with pytest.raises(
        ValidationError,
        match="the per-retained-image reserve requires the explicit vision contract",
    ):
        BundleBudgetConfig(context_tokens=32_768, vision_enabled=True)
    with pytest.raises(
        ValidationError,
        match="the explicit vision contract requires retained capacity",
    ):
        BundleBudgetConfig(
            context_tokens=32_768,
            vision_enabled=True,
            per_image_reserve=4_096,
            max_retained_images=0,
        )


def test_v1_requires_enabled_constitution_and_enabled_route() -> None:
    with pytest.raises(
        ValidationError,
        match="requires enabled constitution integration",
    ):
        Settings.model_validate(
            _v1_settings_dict(
                constitution={
                    "enabled": False,
                    "identity_source": "static",
                    "principal": "local-principal",
                    "session": "local-session",
                    "repository": "local-repository",
                },
                routes=[_v1_route(observation_enabled=False, constitution_enabled=False)],
            )
        )
    with pytest.raises(
        ValidationError,
        match="requires an enabled route",
    ):
        Settings.model_validate(
            _v1_settings_dict(
                routes=[_v1_route(observation_enabled=False, constitution_enabled=False)]
            )
        )


def test_v1_route_model_contract_binds_route_capability_and_context() -> None:
    from slaif_local_coding.constitution.bundles.bundle_tokenizer import (
        BUNDLE_TOKENIZER_RENDER_POLICY_VERSION,
        PINNED_TOKENIZER_REVISION,
        PINNED_TOKENIZER_UPSTREAM,
    )

    settings = Settings.model_validate(_v1_settings_dict())
    contract = settings.context_cache.route_contracts["text"]
    assert contract.model == "qwen38-27b"
    assert contract.context_tokens == V1_EFFECTIVE_C
    assert contract.tokenizer_upstream == PINNED_TOKENIZER_UPSTREAM
    assert contract.tokenizer_revision == PINNED_TOKENIZER_REVISION
    assert contract.render_policy_version == BUNDLE_TOKENIZER_RENDER_POLICY_VERSION


@pytest.mark.parametrize(
    ("context_cache", "message"),
    [
        (
            _v1_context_cache(route_contracts={}),
            V1_ROUTE_CONTRACT_MISSING,
        ),
        (
            _v1_context_cache(route_contracts={"missing": _v1_route_contract("qwen38-27b")}),
            V1_ROUTE_CONTRACT_ORPHAN,
        ),
        (
            _v1_context_cache(route_contracts={"text": _v1_route_contract("some-other-model")}),
            V1_ROUTE_CONTRACT_MODEL_MISMATCH,
        ),
        (
            _v1_context_cache(budget=_v1_budget(context_tokens=40_960)),
            V1_ROUTE_CONTRACT_CONTEXT_MISMATCH,
        ),
        (
            _v1_context_cache(
                route_contracts={
                    "text": {
                        "model": "qwen38-27b",
                        "context_tokens": V1_EFFECTIVE_C,
                        "render_policy_version": "render-policy-v2",
                    }
                }
            ),
            V1_CAPABILITY_NOT_PINNED,
        ),
        (
            _v1_context_cache(
                route_contracts={
                    "text": {
                        "model": "qwen38-27b",
                        "context_tokens": V1_EFFECTIVE_C,
                        "tokenizer_revision": "c" * 40,
                    }
                }
            ),
            V1_CAPABILITY_NOT_PINNED,
        ),
        (
            _v1_context_cache(
                route_contracts={
                    "text": {
                        "model": "qwen38-27b",
                        "context_tokens": V1_EFFECTIVE_C,
                        "tokenizer_upstream": "Qwen/Qwen3.9-27B",
                    }
                }
            ),
            V1_CAPABILITY_NOT_PINNED,
        ),
    ],
    ids=[
        "missing",
        "orphan-unknown-route",
        "model-mismatch",
        "context-mismatch",
        "render-not-pinned",
        "revision-not-pinned",
        "upstream-not-pinned",
    ],
)
def test_v1_route_model_contract_fails_closed_on_mismatches(
    context_cache: dict[str, Any], message: str
) -> None:
    with pytest.raises(ValidationError, match=re.escape(message)):
        Settings.model_validate(_v1_settings_dict(context_cache=context_cache))


def test_v1_non_governed_route_cannot_carry_a_contract() -> None:
    with pytest.raises(ValidationError, match=re.escape(V1_ROUTE_CONTRACT_ORPHAN)):
        Settings.model_validate(
            _v1_settings_dict(
                routes=[
                    _v1_route(observation_enabled=False, constitution_enabled=False),
                ],
                context_cache=_v1_context_cache(
                    route_contracts={"text": _v1_route_contract("qwen38-27b")}
                ),
            )
        )


def test_v1_keeps_route_image_and_tool_parsing_unchanged() -> None:
    # The v1 profile selector changes nothing about route image/tool policy
    # parsing: the same declaration yields the same image/tool behavior on
    # both profiles (only the governance flags differ, as the profiles
    # require).
    image_tool_fields = (
        "max_images_per_request",
        "image_overflow_policy",
        "responses_tool_policy",
        "enable_responses",
        "enable_chat_completions",
    )
    base_route: dict[str, Any] = {
        "name": "text",
        "model": "qwen38-27b",
        "max_images_per_request": 1,
        "image_overflow_policy": "retain_newest",
        "responses_tool_policy": "drop_disabled_codex_search",
        "enable_responses": False,
    }
    legacy = Settings.model_validate(
        {
            "server": {"listen_host": "127.0.0.1"},
            "upstream": {
                "base_url": "http://127.0.0.1:18020/v1",
                "api_key_env": V1_UPSTREAM_KEY_ENV,
                "model": "qwen38-27b",
            },
            "routes": [{**base_route, "observation_enabled": False, "constitution_enabled": False}],
        }
    )
    # The v1 side declares the same 1-image route; its v1 budget therefore
    # carries the matching explicit vision contract (the profile law, not
    # the route parsing, is what keeps the two sides comparable).
    v1 = Settings.model_validate(
        _v1_settings_dict(
            routes=[{**base_route, "observation_enabled": True, "constitution_enabled": True}],
            context_cache=_v1_context_cache(
                budget=_v1_budget(
                    vision_enabled=True,
                    per_image_reserve=4_096,
                    max_retained_images=1,
                )
            ),
        )
    )
    for field in image_tool_fields:
        assert getattr(legacy.routes[0], field) == getattr(v1.routes[0], field)


def test_v1_one_worker_policy_and_ram_ownership() -> None:
    # Strict one-worker policy: any non-one count fails closed, and the
    # strict integer type gate rejects booleans, floats (even whole-valued)
    # and strings rather than coercing them.
    for workers, message in (
        (2, "Input should be less than or equal to 1"),
        (0, "Input should be greater than or equal to 1"),
        (True, "Input should be a valid integer"),
        (1.0, "Input should be a valid integer"),
        ("1", "Input should be a valid integer"),
    ):
        with pytest.raises(ValidationError, match=message):
            Settings.model_validate(
                _v1_settings_dict(context_cache=_v1_context_cache(workers=workers))
            )
    settings = Settings.model_validate(_v1_settings_dict())
    assert settings.context_cache.workers == 1
    # Explicit bounded process/session RAM ownership reuses the accepted
    # 019 types: the session ceiling can never exceed the process ceiling.
    with pytest.raises(ValidationError):
        RamStateBounds(
            session_max_owned_bytes=512 * 1024 * 1024,
            process_max_owned_bytes=128 * 1024 * 1024,
        )
    with pytest.raises(ValidationError):
        Settings.model_validate(
            _v1_settings_dict(
                context_cache=_v1_context_cache(
                    ram=_v1_ram(
                        session_max_owned_bytes=512 * 1024 * 1024,
                        process_max_owned_bytes=128 * 1024 * 1024,
                    )
                )
            )
        )


def test_v1_recovery_root_validated_without_io(tmp_path: Path) -> None:
    missing = tmp_path / "owner-21001" / "v1-recovery"
    settings = Settings.model_validate(
        _v1_settings_dict(context_cache=_v1_context_cache(recovery=_v1_recovery(root=str(missing))))
    )
    assert settings.context_cache.recovery.root == missing
    # Configuration validation never opens, creates, enumerates or probes
    # the recovery store.
    assert not missing.exists()
    assert not missing.parent.exists()
    with pytest.raises(
        ValidationError, match="v1 recovery root must be an absolute normalized path"
    ):
        Settings.model_validate(
            _v1_settings_dict(
                context_cache=_v1_context_cache(recovery=_v1_recovery(root="relative/recovery"))
            )
        )
    with pytest.raises(
        ValidationError, match="v1 recovery root must be an absolute normalized path"
    ):
        Settings.model_validate(
            _v1_settings_dict(
                context_cache=_v1_context_cache(
                    recovery=_v1_recovery(root=str(tmp_path / "a" / ".." / "b"))
                )
            )
        )


def test_v1_error_messages_are_fixed_and_content_free(tmp_path: Path) -> None:
    private = f"relative/{tmp_path.name}/owner-secret-21001/recovery"
    with pytest.raises(ValidationError) as excinfo:
        Settings.model_validate(
            _v1_settings_dict(context_cache=_v1_context_cache(recovery=_v1_recovery(root=private)))
        )
    rendered = str(excinfo.value)
    assert "v1 recovery root must be an absolute normalized path" in rendered
    assert "owner-secret-21001" not in rendered
    assert tmp_path.name not in rendered
    for fixed in (
        V1_LEGACY_CACHE_CONFLICT,
        V1_LEGACY_COMPILER_CONFLICT,
        V1_LEGACY_REHYDRATION_CONFLICT,
        V1_LEGACY_POLICY_CONFLICT,
    ):
        assert "{" not in fixed
        assert "$" not in fixed


def test_changed_effective_context_is_distinct_budget_policy() -> None:
    a = BundleBudgetConfig(context_tokens=32_768)
    b = BundleBudgetConfig(context_tokens=40_960)
    c = BundleBudgetConfig(context_tokens=32_768, generation_reserve=4_500)
    assert a.budget_identity == BundleBudgetConfig(context_tokens=32_768).budget_identity
    assert a.budget_identity != b.budget_identity
    assert a.budget_identity != c.budget_identity


def test_changed_compiler_compatibility_is_distinct_compile_policy() -> None:
    base = _v1_compiler()
    declared = BundleCompilerConfig(**base)
    other_revision = BundleCompilerConfig(**{**base, "model_revision": V1_REVISION_B})
    other_compatibility = BundleCompilerConfig(**{**base, "compatibility_identity": V1_COMPAT_B})
    # The transport URL is identity-free: the same declared model at a
    # different private endpoint keeps the same config identity.
    transport_only = BundleCompilerConfig(**{**base, "base_url": "http://other.test/v1"})
    # The declared model is policy material: a different model declaration
    # is a different compile policy.
    other_model = BundleCompilerConfig(**{**base, "model": "qwen38-27b-alt"})
    assert declared.config_identity != other_revision.config_identity
    assert declared.config_identity != other_compatibility.config_identity
    assert declared.config_identity == transport_only.config_identity
    assert declared.config_identity != other_model.config_identity


def test_full_compile_key_binds_budget_and_compiler_identities() -> None:
    def key(budget: str, compiler: str, render_policy_version: str = "render-policy-v1") -> str:
        return derive_compile_key(
            entry_class=EntryClass.ROOT_ENTRY,
            content_key="root",
            source_sha256="d" * 64,
            source_byte_length=16,
            candidate_paths=(),
            config_identity=compiler,
            tokenizer_identity="t" * 64,
            budget_identity=budget,
            render_policy_version=render_policy_version,
        )

    base_budget = BundleBudgetConfig(context_tokens=32_768).budget_identity
    alt_budget = BundleBudgetConfig(context_tokens=40_960).budget_identity
    base_compiler = BundleCompilerConfig(**_v1_compiler()).config_identity
    alt_compiler = BundleCompilerConfig(
        **{**_v1_compiler(), "compatibility_identity": V1_COMPAT_B}
    ).config_identity
    k0 = key(base_budget, base_compiler)
    assert k0 == key(base_budget, base_compiler)
    distinct = {
        k0,
        key(alt_budget, base_compiler),
        key(base_budget, alt_compiler),
        key(base_budget, base_compiler, render_policy_version="render-policy-v2"),
    }
    assert len(distinct) == 4


def test_v1_compiler_may_share_upstream_env_but_never_gateway_envs() -> None:
    # The compiler authenticates the same private upstream channel: sharing
    # the private upstream credential environment name is permitted.
    shared = Settings.model_validate(
        _v1_settings_dict(
            upstream={
                "base_url": "http://127.0.0.1:18020/v1",
                "api_key_env": V1_COMPILER_KEY_ENV,
                "model": "qwen38-27b",
            }
        )
    )
    compiler = shared.context_cache.compiler
    assert compiler is not None
    assert shared.upstream.api_key_env == compiler.api_key_env
    # A Gateway service credential is never a compiler credential.
    with pytest.raises(ValidationError, match="v1_compiler and gateway_service"):
        Settings.model_validate(
            _v1_settings_dict(
                gateway_ingress={
                    "mode": "service_bearer_static_identity",
                    "service_token_env": V1_COMPILER_KEY_ENV,
                }
            )
        )
    # A Gateway signing secret is never a compiler credential.
    with pytest.raises(ValidationError, match="v1_compiler and gateway_signing"):
        Settings.model_validate(
            _v1_settings_dict(
                constitution={"enabled": True, "identity_source": "signed_request"},
                gateway_ingress={
                    "mode": "service_bearer_signed_identity_v1",
                    "service_token_env": "TEST_V1_SERVICE_TOKEN",
                    "signing_secret_env": V1_COMPILER_KEY_ENV,
                },
            )
        )
