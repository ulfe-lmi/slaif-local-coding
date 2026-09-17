import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from slaif_local_coding.config import (
    CacheConfig,
    CompilerConfig,
    ConstitutionIntegrationConfig,
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
    assert "accepted 004-al human-gated vision fixture" in architecture
    assert "selected protected Qwen/vLLM fixture" in architecture
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
