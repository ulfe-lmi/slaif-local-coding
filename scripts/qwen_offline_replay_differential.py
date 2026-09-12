#!/usr/bin/env python3
"""Run the bounded, metadata-only Qwen Responses replay differential.

This script loads the installed vLLM request/preparation/rendering path and the
installed tokenizer metadata.  It never starts an engine, reads model weights,
resolves credentials, contacts a service, or prints prompt/rendered content.
"""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import logging
import os
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
    sys.path.insert(0, str(REPO_ROOT / "src"))

from scripts.gateway_accounting_rehearsal import (  # noqa: E402
    _identity_companion_tools,
    _idless_companion_continuation_body,
    _idless_companion_initial_body,
)
from slaif_local_coding.tool_policy import apply_responses_tool_policy  # noqa: E402

MODEL_DIR = Path(
    os.environ.get(
        "SLAIF_OFFLINE_QWEN_MODEL_DIR",
        "/synology/homes/janezp/qwen-serving/models/Qwen3.8-27B-W4A16-AutoRound",
    )
)
VLLM_PYTHON = Path(
    os.environ.get(
        "SLAIF_OFFLINE_QWEN_PYTHON",
        "/synology/homes/janezp/qwen-serving/venv/bin/python",
    )
)
TEMPLATE_PATH = MODEL_DIR / "chat_template.jinja"
VLLM_SITE = VLLM_PYTHON.parent / "../lib/python3.12/site-packages/vllm"
VLLM_RESPONSES = VLLM_SITE / "entrypoints/openai/responses"
CHAT_UTILS_PATH = VLLM_SITE / "entrypoints/chat_utils.py"
EXPECTED_SOURCE_SHA256 = {
    "protocol.py": "6aeabf69dbc924b238172b505730a8a8321b50a819891d2a72a690963c970fba",
    "utils.py": "577100edd0951f7f2936d2b37b7b4ec9a03d85088b35e49de6c0e9633a59adc2",
    "serving.py": "628429902ff26b87f86eae1a45297f647f3712d7b421ca9a4866a3fd0f046a5b",
    "chat_template.jinja": "c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041",
}


def _sha256(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(64 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def _returned_call(
    *,
    arguments: str,
    namespace: object = None,
    include_namespace: bool = False,
    include_status: bool = True,
) -> dict[str, object]:
    call: dict[str, object] = {
        "type": "function_call",
        "id": "synthetic-item",
        "call_id": "synthetic-call",
        "name": "local_lookup",
        "arguments": arguments,
    }
    if include_namespace:
        call["namespace"] = namespace
    if include_status:
        call["status"] = "completed"
    return call


def _exact_continuation(
    initial: dict[str, object],
    tools: list[dict[str, object]],
    *,
    arguments: str,
    namespace: object = None,
    include_namespace: bool = False,
) -> dict[str, object]:
    return _idless_companion_continuation_body(
        "synthetic-session",
        _returned_call(
            arguments=arguments,
            namespace=namespace,
            include_namespace=include_namespace,
        ),
        tools=tools,
        initial_body=initial,
    )


def _provider_body(body: Mapping[str, object]) -> dict[str, object]:
    """Apply the exact Local route tool transformation before provider prep."""
    payload = dict(body)
    transformed = apply_responses_tool_policy(payload, "drop_disabled_codex_search")
    return dict(transformed.payload)


def _without_original_user(body: dict[str, object]) -> dict[str, object]:
    result = dict(body)
    history = result["input"]
    assert isinstance(history, list)
    result["input"] = history[1:]
    return result


def _template_has_fixed_no_user_query_predicate(source: bytes) -> bool:
    return (
        b"for message in messages[::-1]" in source
        and b'message.role == "user"' in source
        and b"raise_exception('No user query found in messages.')" in source
    )


def _fixed_preparation_failure(exc: BaseException, template_source: bytes) -> str:
    """Classify only the pinned template failure, never arbitrary ValueError."""
    if (
        type(exc).__name__ == "ValueError"
        and _template_has_fixed_no_user_query_predicate(template_source)
        and str(exc) == "No user query found in messages."
    ):
        return "template_no_user_query"
    if isinstance(exc, (UnicodeDecodeError, json.JSONDecodeError, TypeError)):
        return "request_or_preparation_parse_failure"
    return "request_preparation_failure"


async def _prepare(
    online: Any, body: dict[str, object], template_source: bytes
) -> dict[str, object]:
    from vllm.entrypoints.openai.responses.protocol import (  # type: ignore[import-not-found]
        ResponsesRequest,
    )
    from vllm.entrypoints.openai.responses.utils import (
        construct_input_messages,  # type: ignore[import-not-found]
        construct_tool_dicts,  # type: ignore[import-not-found]
    )

    row: dict[str, object] = {"parsed": False, "prepared": False}
    try:
        request = ResponsesRequest.model_validate(body)
        row["parsed"] = True
        messages = construct_input_messages(request_input=request.input)
        row["message_count"] = len(messages)
        row["message_roles"] = tuple(
            str(message.get("role", "unknown")) for message in messages if isinstance(message, dict)
        )
        tool_dicts = construct_tool_dicts(request.tools, request.tool_choice)
        _conversation, engine_inputs = await online.preprocess_chat(
            request,
            messages,
            default_template=None,
            default_template_content_format="openai",
            default_template_kwargs={},
            tool_dicts=tool_dicts,
            parser=online.parser,
        )
    except BaseException as exc:
        row["failure_class"] = _fixed_preparation_failure(exc, template_source)
        return row
    row["prepared"] = True
    row["engine_input_count"] = len(engine_inputs)
    first = engine_inputs[0]
    row["prompt_token_count"] = len(first["prompt_token_ids"]) if isinstance(first, dict) else None
    return row


async def _run() -> dict[str, object]:
    source_paths = {
        "protocol.py": VLLM_RESPONSES / "protocol.py",
        "utils.py": VLLM_RESPONSES / "utils.py",
        "serving.py": VLLM_RESPONSES / "serving.py",
        "chat_utils.py": CHAT_UTILS_PATH,
        "chat_template.jinja": TEMPLATE_PATH,
    }
    source_hashes = {name: _sha256(path) for name, path in source_paths.items()}
    source_pins_match = all(
        source_hashes.get(name) == expected for name, expected in EXPECTED_SOURCE_SHA256.items()
    )
    result: dict[str, object] = {
        "status": "BLOCKED",
        "execution": "offline_cpu_metadata_only",
        "protected_requests": 0,
        "credential_resolution": False,
        "source_pins_match": source_pins_match,
        "source_hashes": source_hashes,
        "vllm_python": VLLM_PYTHON.name,
        "model_metadata_path_present": MODEL_DIR.is_dir(),
    }
    template_source = b""
    try:
        template_source = TEMPLATE_PATH.read_bytes()
    except OSError:
        pass
    exact_template_predicate = _template_has_fixed_no_user_query_predicate(template_source)
    result["fixed_no_user_query_predicate_present"] = exact_template_predicate
    if (
        not source_pins_match
        or not exact_template_predicate
        or not MODEL_DIR.is_dir()
        or not VLLM_PYTHON.exists()
    ):
        result["reason"] = "offline_dependency_pin_or_path_unavailable"
        return result

    from vllm.config import ModelConfig, VllmConfig  # type: ignore[import-not-found]
    from vllm.renderers import renderer_from_config  # type: ignore[import-not-found]
    from vllm.renderers.online_renderer import OnlineRenderer  # type: ignore[import-not-found]

    zero_tools = _identity_companion_tools()
    raw_initial = _idless_companion_initial_body("synthetic-session", zero_tools)
    initial = _provider_body(raw_initial)
    transformed_tools = cast(list[dict[str, object]], initial["tools"])
    nonzero_tools = copy.deepcopy(zero_tools)
    nonzero_parameters = nonzero_tools[0]["parameters"]
    if not isinstance(nonzero_parameters, dict):
        raise RuntimeError("nonzero_control_schema_unavailable")
    nonzero_parameters["properties"] = {"path": {"type": "string"}}
    nonzero_parameters["required"] = ["path"]
    nonzero_raw_initial = _idless_companion_initial_body("synthetic-session", nonzero_tools)
    nonzero_initial = _provider_body(nonzero_raw_initial)
    nonzero_provider_tools = cast(list[dict[str, object]], nonzero_initial["tools"])
    nonzero_control = _provider_body(
        _exact_continuation(
            nonzero_initial,
            nonzero_provider_tools,
            arguments='{"path":"synthetic"}',
        )
    )
    base = _provider_body(_exact_continuation(initial, transformed_tools, arguments="{}"))
    status_omitted = _provider_body(_exact_continuation(initial, transformed_tools, arguments="{}"))
    status_history = status_omitted.get("input")
    assert isinstance(status_history, list)
    status_call = status_history[-2]
    assert isinstance(status_call, dict)
    status_call.pop("status", None)
    cases: list[tuple[str, dict[str, object]]] = [
        ("current_companion_omits_original_user", _without_original_user(base)),
        ("current_companion_preserves_original_user", base),
        (
            "arguments_empty_preserves_original_user",
            _provider_body(_exact_continuation(initial, transformed_tools, arguments="")),
        ),
        (
            "arguments_object_preserves_original_user",
            _provider_body(_exact_continuation(initial, transformed_tools, arguments="{}")),
        ),
        (
            "namespace_omitted_preserves_original_user",
            _provider_body(_exact_continuation(initial, transformed_tools, arguments="{}")),
        ),
        (
            "namespace_null_preserves_original_user",
            _provider_body(
                _exact_continuation(
                    initial,
                    transformed_tools,
                    arguments="{}",
                    namespace=None,
                    include_namespace=True,
                )
            ),
        ),
        (
            "namespace_legal_preserves_original_user",
            _provider_body(
                _exact_continuation(
                    initial,
                    transformed_tools,
                    arguments="{}",
                    namespace="local",
                    include_namespace=True,
                )
            ),
        ),
        (
            "status_omitted_preserves_original_user",
            status_omitted,
        ),
        (
            "status_completed_preserves_original_user",
            base,
        ),
        # This is a one-variable schema control.  It changes only the exact
        # current local_lookup declaration while keeping the same helper,
        # policy, request options, and original input history.
        ("known_good_nonzero_control", nonzero_control),
    ]
    model_config = ModelConfig(
        model=str(MODEL_DIR),
        tokenizer=str(MODEL_DIR),
        max_model_len=100000,
        trust_remote_code=False,
        limit_mm_per_prompt={"image": 1},
        skip_mm_profiling=True,
    )
    vllm_config = VllmConfig(model_config=model_config)
    renderer = renderer_from_config(vllm_config)
    online = OnlineRenderer(
        model_config,
        renderer,
        request_logger=None,
        chat_template=None,
        chat_template_content_format="openai",
        enable_auto_tools=True,
        tool_parser="qwen3_coder",
        reasoning_parser="qwen3",
    )
    try:
        result["cases"] = [
            {"case": name, **(await _prepare(online, body, template_source))}
            for name, body in cases
        ]
    finally:
        renderer.shutdown()
    initial_tools = initial.get("tools")
    cases_result = result.get("cases")
    first_case = cases_result[0] if isinstance(cases_result, list) and cases_result else {}
    later_cases = cases_result[1:] if isinstance(cases_result, list) else []
    result["zero_argument_schema_exact"] = (
        isinstance(initial_tools, list)
        and bool(initial_tools)
        and isinstance(initial_tools[0], dict)
        and initial_tools[0].get("parameters")
        == {"type": "object", "properties": {}, "additionalProperties": False}
    )
    no_user_query_failure_isolated = (
        isinstance(first_case, dict)
        and first_case.get("prepared") is False
        and first_case.get("failure_class") == "template_no_user_query"
        and all(isinstance(case, dict) and case.get("prepared") is True for case in later_cases)
    )
    result["no_user_query_failure_isolated"] = no_user_query_failure_isolated
    all_cases_prepared = (
        all(
            isinstance(case, dict)
            and (
                case.get("prepared") is True
                or case.get("case") == "current_companion_omits_original_user"
            )
            for case in cases_result
        )
        if isinstance(cases_result, list)
        else False
    )
    corrected_preparation_passed = (
        isinstance(cases_result, list)
        and len(cases_result) == len(cases)
        and no_user_query_failure_isolated
        and all_cases_prepared
    )
    result["corrected_preparation_passed"] = corrected_preparation_passed
    result["status"] = (
        "PASSED"
        if all(
            (
                source_pins_match,
                exact_template_predicate,
                result["model_metadata_path_present"] is True,
                VLLM_PYTHON.exists(),
                result["zero_argument_schema_exact"],
                no_user_query_failure_isolated,
                corrected_preparation_passed,
                result["protected_requests"] == 0,
                result["credential_resolution"] is False,
            )
        )
        else "BLOCKED"
    )
    result["reason"] = (
        "offline_preparation_differential_complete"
        if result["status"] == "PASSED"
        else "offline_preparation_predicate_failed"
    )
    return result


def main() -> int:
    logging.disable(logging.CRITICAL)
    try:
        result = asyncio.run(_run())
    except BaseException:
        result = {
            "status": "FAILED",
            "execution": "offline_cpu_metadata_only",
            "protected_requests": 0,
            "credential_resolution": False,
            "failure_class": "offline_runtime_failure",
        }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result.get("status") == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
