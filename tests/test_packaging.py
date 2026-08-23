"""Static checks for the uninstalled user-systemd candidate example."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SERVICE_EXAMPLE = REPO_ROOT / "packaging" / "slaif-local-coding.service.example"
CONFIG_EXAMPLE = REPO_ROOT / "config" / "adapter.example.toml"


def test_candidate_unit_uses_external_secret_and_explicit_repo_config() -> None:
    unit = SERVICE_EXAMPLE.read_text(encoding="utf-8")

    assert re.search(r"^Environment=", unit, flags=re.MULTILINE) is None
    assert "EnvironmentFile=%h/.config/slaif-local-coding/adapter.env" in unit
    assert (
        "ExecStart=%h/codex-work/slaif-local-coding/.venv/bin/"
        "slaif-local-coding --config=%h/codex-work/slaif-local-coding/"
        "config/adapter.example.toml"
    ) in unit
    assert "--api-key" not in unit
    assert "QWEN3090_API_KEY=" not in unit


def test_candidate_unit_declares_private_bounded_lifecycle() -> None:
    unit = SERVICE_EXAMPLE.read_text(encoding="utf-8")

    required_lines = {
        "Type=exec",
        "Restart=on-failure",
        "TimeoutStartSec=30s",
        "TimeoutStopSec=15s",
        "KillMode=mixed",
        "KillSignal=SIGTERM",
        "NoNewPrivileges=true",
        "PrivateTmp=true",
        "ProtectSystem=strict",
        "ProtectHome=read-only",
        "RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6",
        "IPAddressDeny=any",
        "IPAddressAllow=127.0.0.0/8",
        "IPAddressAllow=::1/128",
        "UMask=0077",
        "LimitNOFILE=4096",
        "TasksMax=128",
        "MemoryMax=1G",
        "StandardOutput=journal",
        "StandardError=journal",
    }
    assert required_lines <= set(unit.splitlines())
    assert "0.0.0.0" not in unit
    assert "Environment=" not in unit


def test_example_config_is_loopback_candidate_on_18031() -> None:
    with CONFIG_EXAMPLE.open("rb") as stream:
        config = tomllib.load(stream)

    assert config["server"]["listen_host"] == "127.0.0.1"
    assert config["server"]["listen_port"] == 18031
    assert config["upstream"]["base_url"].endswith(":18020/v1")
    assert config["routes"][0]["max_images_per_request"] == 1
