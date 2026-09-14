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


DEPLOYMENT_UNIT = REPO_ROOT / "packaging" / "slaif-local-coding.service"
DEPLOYMENT_TEMPLATE = REPO_ROOT / "config" / "adapter.deployment.template.toml"
READYZ_WAIT = REPO_ROOT / "packaging" / "readyz-wait.sh"
DEPLOYMENT_DOC = REPO_ROOT / "docs" / "DEPLOYMENT.md"
ARTIFACT_POLICY_DOC = REPO_ROOT / "docs" / "RELEASE-ARTIFACT-POLICY.md"
CUTOVER_RUNBOOK = REPO_ROOT / "docs" / "RELEASE-CUTOVER-RUNBOOK.md"

SECRET_VALUE_PATTERNS = [
    re.compile(rb"QWEN3090_API_KEY\s*=\s*[A-Za-z0-9._\-]{8,}"),
    re.compile(rb"VLLM_API_KEY\s*=\s*[A-Za-z0-9._\-]{8,}"),
    re.compile(rb"SLAIF_ADAPTER_SERVICE_TOKEN\s*=\s*[A-Za-z0-9._\-]{8,}"),
    re.compile(rb"SLAIF_ADAPTER_SIGNING_SECRET\s*=\s*[A-Za-z0-9._\-]{8,}"),
    re.compile(rb"sk-slaif-[A-Za-z0-9]"),
    re.compile(rb"/synology/"),
    re.compile(rb"hinton1"),
    re.compile(rb"10\.8\.132\.\d+"),
]


def test_deployment_unit_keeps_hardening_and_external_env_file() -> None:
    unit = DEPLOYMENT_UNIT.read_text(encoding="utf-8")
    assert re.search(r"^Environment=", unit, flags=re.MULTILINE) is None
    assert "EnvironmentFile=%h/.config/slaif-local-coding/adapter.env" in unit
    assert (
        "ExecStart=%h/codex-work/slaif-local-coding/.venv/bin/"
        "slaif-local-coding --config=%h/.config/slaif-local-coding/adapter.toml"
    ) in unit
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
        "ProtectProc=invisible",
        "RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6",
        "IPAddressDeny=any",
        "IPAddressAllow=127.0.0.0/8",
        "IPAddressAllow=::1/128",
        "UMask=0077",
        "LimitNOFILE=4096",
        "TasksMax=128",
        "MemoryMax=1G",
        "ReadWritePaths=/dev/shm/slaif-local-coding",
        "StandardOutput=journal",
        "StandardError=journal",
    }
    assert required_lines <= set(unit.splitlines())
    assert "0.0.0.0" not in unit
    assert "--api-key" not in unit


def test_deployment_config_template_has_only_documented_placeholders() -> None:
    text = DEPLOYMENT_TEMPLATE.read_text(encoding="utf-8")
    tokens = sorted(set(re.findall(r"__[A-Z0-9_]+__", text)))
    assert tokens == ["__UPSTREAM_BASE_URL__", "__UPSTREAM_MODEL__"]
    rendered = text.replace("__UPSTREAM_BASE_URL__", "http://127.0.0.1:18020/v1").replace(
        "__UPSTREAM_MODEL__", "qwen3.8-27b"
    )
    config = tomllib.loads(rendered)
    assert config["server"]["listen_host"] == "127.0.0.1"
    assert config["server"]["listen_port"] == 18031
    assert config["upstream"]["base_url"] == "http://127.0.0.1:18020/v1"
    assert config["upstream"]["model"] == "qwen3.8-27b"
    assert config["routes"][0]["model"] == "qwen3.8-27b"
    assert config["routes"][0]["max_images_per_request"] == 1
    assert config["gateway_ingress"]["mode"] == "disabled"
    # No placeholder may remain after the documented substitutions.
    assert "__" not in rendered


def test_readyz_wait_helper_is_bounded_loopback_and_secret_free() -> None:
    helper = READYZ_WAIT.read_text(encoding="utf-8")
    assert "set -euo pipefail" in helper
    assert "refusing non-loopback base URL" in helper
    assert "http://127.0.0.1:18031" in helper
    for pattern in SECRET_VALUE_PATTERNS:
        assert pattern.search(helper.encode()) is None


def _all_packaging_assets() -> list[Path]:
    assets = sorted((REPO_ROOT / "packaging").rglob("*"))
    assets += [
        DEPLOYMENT_TEMPLATE,
        REPO_ROOT / "config" / "adapter.example.toml",
        DEPLOYMENT_DOC,
        ARTIFACT_POLICY_DOC,
        CUTOVER_RUNBOOK,
    ]
    return [asset for asset in assets if asset.is_file()]


def test_no_secret_in_any_packaging_asset_or_document() -> None:
    assets = _all_packaging_assets()
    assert len(assets) >= 8, "expected the full packaging asset set"
    for asset in assets:
        data = asset.read_bytes()
        for pattern in SECRET_VALUE_PATTERNS:
            assert pattern.search(data) is None, (asset, pattern.pattern)


def test_deployment_doc_covers_operator_contract() -> None:
    doc = DEPLOYMENT_DOC.read_text(encoding="utf-8")
    for required in (
        "systemctl --user start slaif-local-coding.service",
        "systemctl --user stop slaif-local-coding.service",
        "systemctl --user restart slaif-local-coding.service",
        "systemctl --user status slaif-local-coding.service",
        "readyz-wait.sh",
        "mode 0600",
        "Upgrade procedure",
        "Rollback procedure",
        "Uninstall/disable",
        "/dev/shm/slaif-local-coding",
        "no raw prompts",
    ):
        assert required.lower() in doc.lower() or required in doc, required


def test_runbook_marks_authority_classes_and_is_prepare_only() -> None:
    runbook = CUTOVER_RUNBOOK.read_text(encoding="utf-8")
    assert "CODING-SAFE" in runbook
    assert "HUMAN-AUTHORIZED (protected/live/release)" in runbook
    assert "No step above was executed" in runbook
    assert "Rollback triggers" in runbook
    assert "cutover not performed" in runbook
    for required in (
        "Current live configuration capture",
        "Install the exact Local artifact",
        "Start candidate privately on 18031",
        "Verify the candidate",
        "Configure/pin the Gateway route",
        "Representative real Codex text/tool/vision smoke",
        "Verify no unintended direct-vLLM bypass",
        "Rollback proof",
        "Deliberate final switch",
    ):
        assert required in runbook, required


def test_artifact_policy_doc_states_wheel_is_sole_supported_artifact() -> None:
    doc = ARTIFACT_POLICY_DOC.read_text(encoding="utf-8")
    assert "single supported distributable" in doc
    assert "developer-only source archive" in doc
    assert "not a supported release artifact" in doc
    assert "scripts/artifact_policy_check.py" in doc
