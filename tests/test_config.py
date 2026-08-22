import tomllib
from pathlib import Path

import pytest
from pydantic import ValidationError

from slaif_local_coding.config import (
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
    for unsafe in ("[compiler]\nenabled = true\n", "[observability]\nlog_raw_payloads = true\n"):
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


def test_objective002_configuration_remains_public_integration_disabled(tmp_path: Path) -> None:
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
    assert loaded.cache.max_pinned_bytes <= loaded.cache.max_total_bytes

    for unsafe in (
        base + "[compiler]\nenabled = true\n",
        base + "[constitution]\nenabled = true\n",
        base + "[cache]\nmax_total_bytes = 1000\nmax_entry_bytes = 2000\n",
    ):
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
