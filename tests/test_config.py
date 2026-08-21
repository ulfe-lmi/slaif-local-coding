from pathlib import Path

import pytest
from pydantic import ValidationError

from slaif_local_coding.config import RouteConfig, ServerConfig, load_settings


def test_non_loopback_and_unknown_policy_fail_closed() -> None:
    with pytest.raises(ValidationError):
        ServerConfig(listen_host="0.0.0.0")
    with pytest.raises(ValidationError):
        RouteConfig(name="x", model="m", image_overflow_policy="guess")  # type: ignore[arg-type]


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
