#!/usr/bin/env python3
"""Run the bounded no-model Codex/gateway tool-envelope differential.

Only validated top-level tool type labels and fixed policy facts leave the
process.  The pinned gateway checkout is imported for request-policy and route
capability validation; no gateway application, database, adapter, or model is
started.
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.dont_write_bytecode = True

from tests.helpers.capture_codex_tool_types import (  # noqa: E402
    CodexToolCapture,
    capture_codex_request,
)
from tests.helpers.path_safety import assert_allowlisted_diagnostic_argv  # noqa: E402
from tests.helpers.vision_e2e_support import VISION_MODEL  # noqa: E402

GATEWAY_MAIN_SHA = "2527030f5bbb90a7f0f354eb5347caee333ce4a7"
CODEX_VERSION = "0.149.0"
ROUTE_CAPABILITIES: dict[str, object] = {
    "responses": {
        "text": True,
        "stateless": True,
        "streaming": True,
        "function_tools": True,
        "custom_tools": True,
        "image_input": True,
        "codex_request_envelope": True,
        "codex_client_tools": True,
        "codex_streaming_tool_events": True,
    },
    "codex_limits": {
        "context_window_tokens": 100_000,
        "default_max_output_tokens": 4096,
        "max_output_tokens": 8192,
    },
}


@dataclass(frozen=True)
class PolicyObservation:
    """Content-free result from the actual pinned gateway policy."""

    accepted: bool
    error_code: str | None
    error_field: str | None
    error_type: str | None
    rejection_before_reservation: bool


@dataclass(frozen=True)
class DifferentialVariant:
    name: str
    feature_flags: tuple[str, ...]
    ignore_user_config: bool
    catalog_search_disabled: bool = False


@dataclass(frozen=True)
class VariantResult:
    name: str
    feature_flags: tuple[str, ...]
    ignore_user_config: bool
    catalog_search_disabled: bool
    codex_exit_status: int | None
    timed_out: bool
    request_received: bool
    tool_type_counts: tuple[tuple[str, int], ...]
    ordinary_function_or_custom_remains: bool
    tool_search_remains: bool
    web_search_remains: bool
    policy: PolicyObservation


VARIANTS: tuple[DifferentialVariant, ...] = (
    DifferentialVariant("baseline", (), False),
    DifferentialVariant(
        "ignore-config-disable-client-hosted-features",
        ("apps", "browser_use", "computer_use"),
        True,
    ),
    DifferentialVariant(
        "ignore-config-disable-client-and-standalone-search",
        ("apps", "browser_use", "computer_use", "standalone_web_search"),
        True,
    ),
    DifferentialVariant(
        "ignore-config-catalog-search-disabled",
        (),
        True,
        catalog_search_disabled=True,
    ),
)


def _pinned_checkout_facts(gateway_root: Path) -> tuple[bool, bool]:
    root = gateway_root.resolve(strict=True)
    revision_argv = ["git", "-C", str(root), "rev-parse", "HEAD"]
    assert_allowlisted_diagnostic_argv(
        revision_argv,
        allowed_commands={"git"},
        disposable_root=root.parent,
        path_arguments=(root,),
    )
    result = subprocess.run(
        revision_argv,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    sha_ok = result.returncode == 0 and result.stdout.strip() == GATEWAY_MAIN_SHA
    status_argv = ["git", "-C", str(root), "status", "--short"]
    assert_allowlisted_diagnostic_argv(
        status_argv,
        allowed_commands={"git"},
        disposable_root=root.parent,
        path_arguments=(root,),
    )
    status = subprocess.run(
        status_argv,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    clean = status.returncode == 0 and not status.stdout.strip()
    return sha_ok, clean


def _source_proves_policy_precedes_reservation(gateway_root: Path) -> bool:
    source_path = gateway_root / "app" / "slaif_gateway" / "services" / "responses_gateway.py"
    source = source_path.read_text(encoding="utf-8")
    policy = source.index("policy_result = policy.apply(")
    route = source.index("route = await _resolve_responses_route(", policy)
    reservation = source.index("rate_limit_reservation = await _reserve_redis_rate_limit(", route)
    quota = source.index("quota = await _reserve_responses_quota(", reservation)
    return policy < route < reservation < quota


def _policy_reducer(gateway_root: Path) -> Any:
    sys.path.insert(0, str(gateway_root / "app"))
    from slaif_gateway.config import Settings
    from slaif_gateway.modules.clients.codex_0149 import (
        CODEX_0149_ADAPTER_MANAGED_CANDIDATE_SHAPES,
        CODEX_0149_ADAPTER_MANAGED_CANDIDATE_TYPES,
        CODEX_0149_POLICY_SPEC,
    )
    from slaif_gateway.modules.clients.registry import CODEX_0149_CLIENT_MODULE
    from slaif_gateway.services.policy_errors import RequestPolicyError
    from slaif_gateway.services.responses_request_policy import (
        ResponsesRequestPolicy,
        conversation_requested,
        previous_response_id_requested,
        responses_codex_client_tools_requested,
        responses_codex_compaction_replay_requested,
        responses_codex_encrypted_reasoning_output_requested,
        responses_codex_encrypted_reasoning_replay_requested,
        responses_codex_request_envelope_requested,
        responses_codex_streaming_tool_events_requested,
        responses_custom_tools_requested,
        responses_file_input_requested,
        responses_function_tools_requested,
        responses_image_input_requested,
        responses_text_format_type,
    )
    from slaif_gateway.services.responses_route_capabilities import (
        enforce_responses_route_capabilities,
    )

    encryption_key = base64.urlsafe_b64encode(b"x" * 32).decode("ascii").rstrip("=")
    settings = Settings(
        APP_ENV="test",
        DATABASE_URL="postgresql+asyncpg://synthetic:synthetic@127.0.0.1:1/synthetic",
        TOKEN_HMAC_SECRET_V1="synthetic-005d-policy-secret",
        ACTIVE_HMAC_KEY_VERSION="1",
        ONE_TIME_SECRET_ENCRYPTION_KEY=encryption_key,
        ENABLE_REDIS_RATE_LIMITS=False,
    )
    policy = ResponsesRequestPolicy(settings=settings, client_spec=CODEX_0149_POLICY_SPEC)
    source_order_ok = _source_proves_policy_precedes_reservation(gateway_root)

    def reduce(payload: object) -> PolicyObservation:
        if not isinstance(payload, dict):
            return PolicyObservation(
                False,
                "responses_field_invalid_type",
                "body",
                "invalid_request_error",
                source_order_ok,
            )
        try:
            captured_types = {
                item.get("type")
                for item in payload.get("tools", [])
                if isinstance(item, dict) and isinstance(item.get("type"), str)
            }
            conformance_tools: list[dict[str, object]] = [
                {
                    "type": "function",
                    "name": "synthetic_local",
                    "description": "synthetic local function",
                    "parameters": {"type": "object", "properties": {}},
                },
                {
                    "type": "custom",
                    "name": "synthetic_custom",
                    "description": "synthetic local custom",
                    "format": {"type": "text"},
                },
            ]
            if "tool_search" in captured_types:
                conformance_tools.append(
                    {
                        "type": "tool_search",
                        "description": "synthetic adapter candidate",
                        "execution": "client",
                        "parameters": {},
                    }
                )
            if "web_search" in captured_types:
                conformance_tools.append(
                    {
                        "type": "web_search",
                        "external_web_access": False,
                        "search_content_types": ["text"],
                    }
                )
            conformance_payload = {
                "model": "synthetic-capture-model",
                "input": [
                    {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "synthetic"}],
                    }
                ],
                "tools": conformance_tools,
                "tool_choice": "auto",
            }
            normalized = CODEX_0149_CLIENT_MODULE.normalize_responses(conformance_payload)
            effective_payload = dict(normalized.body)
            codex_client_tools = responses_codex_client_tools_requested(effective_payload)
            codex_envelope = (
                responses_codex_request_envelope_requested(effective_payload) or codex_client_tools
            )
            streaming_tools = responses_codex_streaming_tool_events_requested(effective_payload)
            encrypted_replay = responses_codex_encrypted_reasoning_replay_requested(
                effective_payload
            )
            compact_replay = responses_codex_compaction_replay_requested(effective_payload)
            policy_result = policy.apply(
                effective_payload,
                allow_store=True,
                allow_codex_request_envelope=True,
                allow_codex_client_tools=True,
                allow_codex_streaming_tool_events=True,
                allow_codex_encrypted_reasoning_replay=True,
                allow_codex_extended_limits=codex_envelope,
                allow_codex_compaction_replay=True,
                codex_client_tool_taxonomy="codex_0_148",
                allow_external_tool_request=False,
                adapter_managed_declaration_candidates=frozenset(
                    CODEX_0149_ADAPTER_MANAGED_CANDIDATE_TYPES
                ),
                adapter_managed_declaration_shapes=CODEX_0149_ADAPTER_MANAGED_CANDIDATE_SHAPES,
            )
            effective = policy_result.effective_body
            format_type = responses_text_format_type(effective)
            encrypted_event = (
                encrypted_replay or responses_codex_encrypted_reasoning_output_requested(effective)
            )
            enforce_responses_route_capabilities(
                route_capabilities=ROUTE_CAPABILITIES,
                streaming_requested=effective.get("stream") is True,
                route_supports_streaming=True,
                json_mode_requested=format_type == "json_object",
                structured_output_requested=format_type == "json_schema",
                function_tools_requested=responses_function_tools_requested(effective),
                custom_tools_requested=responses_custom_tools_requested(effective),
                image_input_requested=responses_image_input_requested(effective),
                file_input_requested=responses_file_input_requested(effective),
                stored_responses_requested=effective.get("store") is True,
                previous_response_id_requested=previous_response_id_requested(effective),
                conversations_requested=conversation_requested(effective),
                codex_request_envelope_requested=codex_envelope,
                codex_client_tools_requested=codex_client_tools,
                codex_streaming_tool_events_requested=streaming_tools,
                codex_encrypted_reasoning_replay_requested=encrypted_event,
                codex_extended_limits_requested=codex_envelope,
                codex_compaction_requested=compact_replay,
            )
        except RequestPolicyError as exc:
            code = getattr(exc, "error_code", None)
            field = getattr(exc, "param", None)
            return PolicyObservation(
                False,
                code if isinstance(code, str) else "responses_policy_rejected",
                field if isinstance(field, str) else None,
                "invalid_request_error",
                source_order_ok,
            )
        return PolicyObservation(True, None, None, None, source_order_ok)

    return reduce


def _disable_catalog_search_tools(path: Path) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    models = document.get("models")
    selected = next(item for item in models if item.get("slug") == VISION_MODEL)
    selected["experimental_supported_tools"] = []
    selected["supports_search_tool"] = False
    selected["web_search_tool_type"] = "text"
    path.write_text(json.dumps(document, separators=(",", ":")), encoding="utf-8")
    path.chmod(0o600)


def _result_for_capture(capture: CodexToolCapture, variant: DifferentialVariant) -> VariantResult:
    markers = dict(capture.tool_type_counts)
    policy = capture.policy_observation
    if not isinstance(policy, PolicyObservation):
        raise RuntimeError("policy_observation_missing")
    return VariantResult(
        name=variant.name,
        feature_flags=variant.feature_flags,
        ignore_user_config=variant.ignore_user_config,
        catalog_search_disabled=variant.catalog_search_disabled,
        codex_exit_status=capture.codex_exit_status,
        timed_out=capture.timed_out,
        request_received=capture.request_received,
        tool_type_counts=capture.tool_type_counts,
        ordinary_function_or_custom_remains=any(
            markers.get(marker, 0) > 0 for marker in ("function", "custom")
        ),
        tool_search_remains=markers.get("tool_search", 0) > 0,
        web_search_remains=markers.get("web_search", 0) > 0,
        policy=policy,
    )


def run_differential(gateway_root: Path, codex_bin: Path | str) -> tuple[VariantResult, ...]:
    sha_ok, clean = _pinned_checkout_facts(gateway_root)
    if not sha_ok:
        raise RuntimeError("gateway_sha_mismatch")
    if not clean:
        raise RuntimeError("gateway_checkout_dirty")
    reducer = _policy_reducer(gateway_root)
    results: list[VariantResult] = []
    for variant in VARIANTS:
        capture = capture_codex_request(
            codex_bin,
            feature_flags=variant.feature_flags,
            ignore_user_config=variant.ignore_user_config,
            catalog_mutator=_disable_catalog_search_tools
            if variant.catalog_search_disabled
            else None,
            request_reducer=reducer,
        )
        results.append(_result_for_capture(capture, variant))
    return tuple(results)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gateway-root", type=Path, required=True)
    parser.add_argument("--codex", type=Path, default="codex")
    args = parser.parse_args()
    try:
        results = run_differential(args.gateway_root, args.codex)
    except Exception as exc:  # pragma: no cover - bounded external process boundary
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__}, sort_keys=True))
        return 1
    print(
        json.dumps(
            {
                "status": "PASSED",
                "codex_version": CODEX_VERSION,
                "variants": [asdict(item) for item in results],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
