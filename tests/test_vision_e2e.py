"""Focused, fake-upstream tests for the repository-only vision acceptance support."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import httpx
import pytest

from tests.helpers import vision_e2e_support as vision


def _catalog(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "models": [
                    {
                        "slug": vision.VISION_MODEL,
                        "input_modalities": ["text", "image"],
                        "supports_image_detail_original": False,
                        "context_window": 100_000,
                        "max_context_window": 100_000,
                        "supports_parallel_tool_calls": False,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def _fake_codex(path: Path, fixture: vision.VisionFixturePaths) -> Path:
    token = fixture.sentinel_token
    argv_log = fixture.codex_home / "argv-log.jsonl"
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import pathlib\n"
        "import sys\n"
        f"log = pathlib.Path({str(argv_log)!r})\n"
        "if '--version' in sys.argv:\n"
        "    print('codex-cli 0.149.0')\n"
        "    raise SystemExit(0)\n"
        "args = sys.argv[1:]\n"
        "log.open('a', encoding='utf-8').write(json.dumps(args) + '\\n')\n"
        "if '--dangerously-bypass-approvals-and-sandbox' not in args:\n"
        "    raise SystemExit(21)\n"
        "if 'resume' in args:\n"
        "    if '--last' not in args or '--image' not in args:\n"
        "        raise SystemExit(22)\n"
        f"    marker = 'CROP-PROCESSED'\n"
        "else:\n"
        "    if args[args.index('--image') + 1] != "
        f"{str(fixture.full_image.path)!r}:\n"
        "        raise SystemExit(23)\n"
        f"    marker = 'FULL-SCENE-PROCESSED'\n"
        "events = [\n"
        " {'type': 'thread.started', 'thread_id': 'synthetic-session'},\n"
        " {'type': 'item.completed', 'item': {'type': 'command_execution'}},\n"
        " {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': marker}},\n"
        f" {{'type': 'item.completed', 'item': {{'type': 'agent_message', "
        f"'text': 'SENTINEL-ACK:{token}'}}}},\n"
        "]\n"
        "for event in events:\n"
        "    print(json.dumps(event))\n",
        encoding="utf-8",
    )
    path.chmod(0o700)
    return path


def test_vision_fixture_is_deterministic_private_and_catalog_contract_is_exact(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    fixture = vision.write_vision_fixture(
        tmp_path, base_url="http://127.0.0.1:18031/v1", api_key_env="UNUSED"
    )
    assert fixture.full_image.sha256 != fixture.crop_image.sha256
    assert fixture.full_image.path.stat().st_mode & 0o777 == 0o600
    assert fixture.crop_image.path.stat().st_mode & 0o777 == 0o600
    assert fixture.adapter_config.stat().st_mode & 0o777 == 0o600

    def fake_catalog(_codex_bin: object, destination: Path, *, model: str) -> None:
        assert model == vision.VISION_MODEL
        destination.write_text(
            json.dumps({"models": [{"slug": model, "input_modalities": ["text"]}]}),
            encoding="utf-8",
        )

    monkeypatch.setattr(vision, "write_local_model_catalog", fake_catalog)
    vision.write_vision_model_catalog("unused", fixture.model_catalog)
    assert vision._catalog_facts(fixture.model_catalog) == (True, True, 100_000, True)
    assert fixture.sentinel_token not in fixture.codex_config.read_text(encoding="utf-8")


def test_outgoing_recorder_proves_newest_crop_and_preserves_other_content(tmp_path: Path) -> None:
    fixture = vision.write_vision_fixture(
        tmp_path, base_url="http://127.0.0.1:18031/v1", api_key_env="UNUSED"
    )
    full = vision._data_url(fixture.full_image.path)
    crop = vision._data_url(fixture.crop_image.path)
    governance = {
        "type": "input_text",
        "text": "GOVERNANCE-DEPENDENCY.md FINAL_RESPONSE_EXACTLY",
    }
    tool_call = {"type": "function_call", "call_id": "fixed", "name": "read"}
    tool_output = {"type": "function_call_output", "call_id": "fixed", "output": "fixed"}
    turn_one = {
        "model": vision.VISION_MODEL,
        "input": [
            {
                "role": "user",
                "content": [governance, {"type": "input_image", "image_url": full}],
            }
        ],
        "tools": [tool_call],
    }
    turn_two = {
        "model": vision.VISION_MODEL,
        "input": [
            {"role": "user", "content": [governance, {"type": "input_image", "image_url": full}]},
            {"role": "user", "content": [{"type": "input_image", "image_url": crop}]},
            tool_output,
        ],
        "tools": [tool_call],
    }
    outgoing_one = json.loads(json.dumps(turn_one))
    outgoing_two = json.loads(json.dumps(turn_two))
    outgoing_two["input"][0]["content"] = [governance]

    first = vision.capture_outgoing_vision_payload(
        turn=1, incoming=turn_one, outgoing=outgoing_one, fixture=fixture
    )
    second = vision.capture_outgoing_vision_payload(
        turn=2, incoming=turn_two, outgoing=outgoing_two, fixture=fixture
    )
    assert first.input_images_seen == 1
    assert first.outgoing_images_seen == 1
    assert first.images_removed == 0
    assert first.forwarded_labels == ("full_scene",)
    assert second.input_images_seen == 2
    assert second.outgoing_images_seen == 1
    assert second.images_removed == 1
    assert second.forwarded_labels == ("right_crop",)
    assert second.forwarded_lengths == (fixture.crop_image.byte_length,)
    assert second.forwarded_sha256 == (fixture.crop_image.sha256,)
    assert first.non_image_content_preserved
    assert second.non_image_content_preserved
    assert first.governance_content_preserved and second.governance_content_preserved
    assert first.tool_content_preserved and second.tool_content_preserved
    assert "data:image/png" not in json.dumps(asdict(second))


def test_vision_runner_uses_global_yolo_exec_resume_and_exact_model_facts(tmp_path: Path) -> None:
    fixture = vision.write_vision_fixture(
        tmp_path, base_url="http://127.0.0.1:18031/v1", api_key_env="UNUSED"
    )
    _catalog(fixture.model_catalog)
    codex = _fake_codex(tmp_path / "codex", fixture)
    metrics = iter(
        [
            "# TYPE slaif_image_items_total counter\n"
            'slaif_image_items_total{route="qwen38-vision-codex",result="seen"} 0\n'
            'slaif_image_items_total{route="qwen38-vision-codex",result="removed"} 0\n',
            "# TYPE slaif_image_items_total counter\n"
            'slaif_image_items_total{route="qwen38-vision-codex",result="seen"} 1\n'
            'slaif_image_items_total{route="qwen38-vision-codex",result="removed"} 0\n',
            "# TYPE slaif_image_items_total counter\n"
            'slaif_image_items_total{route="qwen38-vision-codex",result="seen"} 3\n'
            'slaif_image_items_total{route="qwen38-vision-codex",result="removed"} 1\n',
        ]
    )
    facts = vision.run_vision_e2e(codex, fixture, metrics_sampler=lambda: next(metrics))
    assert facts.successful
    assert facts.same_session
    assert facts.first.resumed_command is False
    assert facts.second.resumed_command is True
    assert facts.first.normalized_argv[:3] == (
        "<codex>",
        "--dangerously-bypass-approvals-and-sandbox",
        "exec",
    )
    assert facts.second.normalized_argv[3:6] == ("resume", "--last", "--json")
    assert "--ephemeral" not in facts.first.normalized_argv
    assert "--ephemeral" not in facts.second.normalized_argv
    assert facts.metric_deltas is not None and facts.metric_deltas.exact
    assert fixture.sentinel_token not in json.dumps(asdict(facts))
    log = (fixture.codex_home / "argv-log.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(log) == 2
    assert "resume" in log[1] and "--last" in log[1]


def test_vision_metric_deltas_are_exact_and_bounded() -> None:
    before = (
        "# TYPE slaif_image_items_total counter\n"
        'slaif_image_items_total{route="qwen38-vision-codex",result="seen"} 4\n'
        'slaif_image_items_total{route="qwen38-vision-codex",result="removed"} 2\n'
    )
    between = before.replace('result="seen"} 4', 'result="seen"} 5')
    after = between.replace('result="seen"} 5', 'result="seen"} 7').replace(
        'result="removed"} 2', 'result="removed"} 3'
    )
    deltas = vision.vision_metric_deltas(before, between, after)
    assert deltas.exact


@pytest.mark.skipif(
    os.getenv("SLAIF_VISION_ACCEPTANCE") != "1",
    reason="human must activate the mutually exclusive protected vision fixture",
)
def test_live_vision_exec_resume_acceptance() -> None:
    """Run only after the human-approved vision unit is active on protected 18020."""
    codex_bin = os.environ.get("CODEX_BIN", "codex")
    with tempfile.TemporaryDirectory(prefix="slaif-vision-acceptance-") as temporary:
        fixture = vision.write_vision_fixture(
            Path(temporary), base_url="http://127.0.0.1:18031/v1", api_key_env="QWEN3090_API_KEY"
        )
        vision.write_vision_model_catalog(codex_bin, fixture.model_catalog)
        environment = vision.vision_subprocess_environment(fixture)
        log_path = fixture.codex_home / "candidate.log"
        log_handle = log_path.open("wb")
        candidate = subprocess.Popen(
            [
                "uv",
                "run",
                "--frozen",
                "slaif-local-coding",
                f"--config={fixture.adapter_config}",
            ],
            cwd=Path(__file__).resolve().parents[1],
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
        )
        try:
            with httpx.Client(base_url="http://127.0.0.1:18031", timeout=5) as client:
                for _ in range(60):
                    if candidate.poll() is not None:
                        raise AssertionError("candidate_adapter_exited")
                    try:
                        if client.get("/healthz").status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.25)
                else:
                    raise AssertionError("candidate_adapter_not_ready")
                facts = vision.run_vision_e2e(
                    codex_bin,
                    fixture,
                    metrics_sampler=lambda: client.get("/metrics").text,
                )
            assert facts.successful
        finally:
            candidate.terminate()
            try:
                candidate.wait(timeout=15)
            except subprocess.TimeoutExpired:
                candidate.kill()
                candidate.wait(timeout=5)
            log_handle.close()
        assert candidate.poll() is not None
        log_bytes = log_path.read_bytes()
        assert fixture.sentinel_token.encode() not in log_bytes
        assert b"data:image" not in log_bytes
        with httpx.Client(base_url="http://127.0.0.1:18031", timeout=1) as client:
            with pytest.raises(httpx.HTTPError):
                client.get("/healthz")
