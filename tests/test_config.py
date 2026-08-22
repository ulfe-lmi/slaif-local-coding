import tomllib
from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import ValidationError

from slaif_local_coding.config import (
    CacheConfig,
    CompilerConfig,
    ConstitutionIntegrationConfig,
    ObservationPolicy,
    RouteConfig,
    ServerConfig,
    Settings,
    UpstreamConfig,
    load_settings,
)


def test_non_loopback_and_unknown_policy_fail_closed() -> None:
    with pytest.raises(ValidationError):
        ServerConfig(listen_host="0.0.0.0")
    with pytest.raises(ValidationError):
        RouteConfig(name="x", model="m", image_overflow_policy="guess")  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        ServerConfig(json_max_nesting_depth=257)
    with pytest.raises(ValidationError):
        ObservationPolicy(max_roots=0)


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
    for unsafe in "[observability]\nlog_raw_payloads = true\n":
        path = tmp_path / "unsafe.toml"
        path.write_text(base + unsafe)
        with pytest.raises(ValueError):
            load_settings(path)


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


def test_current_host_capability_is_text_only_with_historical_vision_provenance() -> None:
    live_document = Path("docs/LIVE-TEST-ENVIRONMENT.md").read_text()
    architecture = Path("ARCHITECTURE.md").read_text()
    readme = Path("README.md").read_text()
    assert "Verified image capacity: zero images per request" in live_document
    assert "text-only" in live_document.lower()
    assert "language-model-only" in live_document
    assert "Qwen/vLLM vision service" not in architecture
    assert "Qwen/vLLM text-only service" in architecture
    assert "http://10.8.132.75:18020/v1" in live_document
    assert "10.8.132.76" in live_document
    assert "prior vision deployment" in live_document
    assert "historical provenance" in live_document
    assert "accepts zero images" in architecture
    assert "not live-vision" in readme
    assert "readiness" in readme
    assert "prior vision deployment" in live_document
    assert "historical provenance" in live_document


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
