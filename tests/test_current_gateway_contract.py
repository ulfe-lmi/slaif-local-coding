"""Current, fixture-bound pure Local↔Gateway contract tests."""

from __future__ import annotations

import json
import os
import socket
from pathlib import Path
from typing import Any, cast

import httpx
import pytest

from scripts.gateway_contract import (
    ContractGateError,
    NetworkAccessDenied,
    inspect_gateway_contract,
    load_peer_authority,
    network_denial_guard,
    validate_runtime_contract,
)

_GATEWAY_ROOT = os.environ.get("SLAIF_GATEWAY_ROOT")
pytestmark = pytest.mark.skipif(
    _GATEWAY_ROOT is None,
    reason="SLAIF_GATEWAY_ROOT is required for current Gateway contract tests",
)


def _gateway_app() -> Path:
    assert _GATEWAY_ROOT is not None
    return Path(_GATEWAY_ROOT).resolve() / "app"


def _modules() -> tuple[Any, Any, Any, Any, Any, Any]:
    import sys

    app = str(_gateway_app())
    if app not in sys.path:
        sys.path.insert(0, app)
    from slaif_gateway.modules.clients import codex_0149  # type: ignore[import-not-found]
    from slaif_gateway.modules.clients.registry import (  # type: ignore[import-not-found]
        CODEX_0149_CLIENT_MODULE,
    )
    from slaif_gateway.modules.servers import registry  # type: ignore[import-not-found]
    from slaif_gateway.modules.servers.local_coding import (  # type: ignore[import-not-found]
        contract,
    )
    from slaif_gateway.providers.streaming import (  # type: ignore[import-not-found]
        ResponsesStreamEventValidator,
        ResponsesStreamValidationProfile,
    )

    return (
        codex_0149,
        CODEX_0149_CLIENT_MODULE,
        registry,
        contract,
        ResponsesStreamEventValidator,
        ResponsesStreamValidationProfile,
    )


def _request_body(*, parameters: dict[str, object], stream: bool = True) -> dict[str, object]:
    return {
        "model": "qwen3.8-27b",
        "stream": stream,
        "tools": [
            {
                "type": "function",
                "name": "local_lookup",
                "description": "bounded current contract test function",
                "parameters": parameters,
                "strict": True,
            }
        ],
    }


def _request(body: dict[str, object]) -> httpx.Request:
    return httpx.Request(
        "POST",
        "http://gateway.invalid/v1/responses",
        headers={"content-type": "application/json"},
        content=json.dumps(body, separators=(",", ":")).encode("utf-8"),
    )


def test_current_server_metadata_and_fixture_contract() -> None:
    authority = load_peer_authority()
    codex, client_module, registry, contract, _validator, _profile = _modules()
    descriptor = registry.get_server_module(contract.LOCAL_CODING_SERVER_MODULE_ID)
    facts = {
        "server_module_id": descriptor.module_id,
        "server_module_version": descriptor.module_version,
        "replay_mode": contract.LOCAL_CODING_REPLAY_MODE,
        "client_module_id": codex.CODEX_0149_CLIENT_MODULE_ID,
        "client_module_version": client_module.module_version,
        "validator_class": "ResponsesStreamEventValidator",
        "profile_class": "ResponsesStreamValidationProfile",
    }
    validate_runtime_contract(facts, authority)
    assert contract.LOCAL_CODING_SERVER_MODULE_VERSION == authority.server_module_version


def test_gateway_inspection_import_path_is_network_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    import scripts.gateway_contract as runner

    assert _GATEWAY_ROOT is not None
    real_import = runner._import_gateway
    attempted_modules: list[str] = []

    def import_with_network_probe(root: Path, name: str) -> Any:
        attempted_modules.append(name)
        socket.getaddrinfo("gateway.invalid", 443)
        return real_import(root, name)

    monkeypatch.setattr(runner, "_import_gateway", import_with_network_probe)
    with network_denial_guard(), pytest.raises(NetworkAccessDenied, match="network_access_denied"):
        inspect_gateway_contract(Path(_GATEWAY_ROOT))
    assert attempted_modules


def test_signed_mode_requires_skew_and_ttl_and_rejects_stale_metadata() -> None:
    _codex, _client_module, _registry, contract, _validator, _profile = _modules()
    base = {
        "contract_version": contract.LOCAL_CODING_SERVER_MODULE_ID,
        "route_name": "qwen38-vision-codex",
        "tool_policy_version": contract.LOCAL_CODING_TOOL_POLICY_VERSION,
        "identity_mode": "signed_identity_v1",
        "replay_mode": contract.LOCAL_CODING_REPLAY_MODE,
        "deployment_mode": "single_worker",
    }
    with pytest.raises(ValueError):
        contract.parse_local_coding_route_contract({"local_coding": base})
    valid = {
        **base,
        "clock_skew_seconds": 60,
        "replay_ttl_seconds": 60,
    }
    assert contract.parse_local_coding_route_contract({"local_coding": valid}) is not None
    with pytest.raises(ValueError):
        contract.parse_local_coding_route_contract(
            {"local_coding": {**valid, "replay_mode": "legacy"}}
        )


def test_current_client_version_and_request_derived_zero_argument_fact() -> None:
    codex, client_module, _registry, _contract, _validator, _profile = _modules()
    assert client_module.module_id == "codex-0.149-responses-v1"
    assert client_module.module_version == "4"
    body = _request_body(
        parameters={"type": "object", "properties": {}, "additionalProperties": False}
    )
    assert codex.codex_0149_zero_argument_function_names(body) == frozenset({"local_lookup"})
    assert codex.codex_0149_zero_argument_function_names({**body, "stream": False}) == frozenset(
        {"local_lookup"}
    )


def test_responses_validator_profile_accepts_current_lifecycle() -> None:
    from tests.test_gateway162_validator_factory import _body, _events

    codex, _client_module, _registry, _contract, validator_type, profile_type = _modules()
    body = _body(parameters={"type": "object", "properties": {}, "additionalProperties": False})
    profile = profile_type(
        codex_streaming_tool_events=True,
        codex_0149_function_tool_events=True,
        zero_argument_function_names=codex.codex_0149_zero_argument_function_names(body),
        codex_encrypted_reasoning_replay=False,
        declared_client_tools=codex.codex_0149_declared_tool_taxonomy(body),
        codex_reasoning_events=True,
    )
    validator = validator_type(profile)
    results = [
        validator.validate(event) for event in _events(arguments="", include_argument_events=False)
    ]
    assert all(results)
    assert len(validator.take_replay_reference_candidates()) == 1


def test_idless_call_output_requires_call_id_and_allows_optional_item_id() -> None:
    from scripts.gateway_accounting_rehearsal import (
        _identity_companion_tools,
        _idless_companion_continuation_body,
        _idless_companion_initial_body,
    )

    codex, _client_module, _registry, _contract, _validator, _profile = _modules()
    from slaif_gateway.services.responses_request_policy import (  # type: ignore[import-not-found]
        codex_replay_request_candidates,
    )

    tools = _identity_companion_tools()
    initial_body = _idless_companion_initial_body("synthetic-session", tools)
    returned_call = {
        "type": "function_call",
        "id": "synthetic-item",
        "status": "completed",
        "namespace": None,
        "name": "local_lookup",
        "arguments": "",
        "call_id": "synthetic-call",
    }
    body = _idless_companion_continuation_body(
        "synthetic-session",
        returned_call,
        tools=tools,
        initial_body=initial_body,
    )
    candidate = codex_replay_request_candidates(
        body,
        top_level_tool_taxonomy=codex.codex_0149_declared_tool_taxonomy(body),
        allow_idless_tool_call_replay=True,
    )
    assert len(candidate) == 1
    assert candidate[0].call_id == "synthetic-call"
    assert candidate[0].item_id is None
    input_items = cast(list[object], body["input"])
    returned_input = cast(dict[str, object], input_items[-2])
    missing_call_id = {
        **body,
        "input": [
            *input_items[:-2],
            {**returned_input, "call_id": None},
            input_items[-1],
        ],
    }
    assert (
        codex_replay_request_candidates(
            missing_call_id,
            top_level_tool_taxonomy=codex.codex_0149_declared_tool_taxonomy(body),
            allow_idless_tool_call_replay=True,
        )
        == ()
    )


@pytest.mark.parametrize("field", ("module_version", "replay_mode"))
def test_incompatible_current_contract_fact_fails(field: str) -> None:
    authority = load_peer_authority()
    _codex, _client_module, _registry, contract, _validator, _profile = _modules()
    facts = {
        "server_module_id": authority.server_module_id,
        "server_module_version": authority.server_module_version,
        "replay_mode": authority.replay_mode,
        "client_module_id": authority.client_module_id,
        "client_module_version": authority.client_module_version,
        "validator_class": "ResponsesStreamEventValidator",
        "profile_class": "ResponsesStreamValidationProfile",
    }
    facts[field if field != "module_version" else "server_module_version"] = "incompatible"
    with pytest.raises(ContractGateError):
        validate_runtime_contract(facts, authority)
    assert contract.LOCAL_CODING_REPLAY_MODE == authority.replay_mode


def test_invalid_stream_lifecycle_is_not_normalized() -> None:
    from tests.test_gateway162_validator_factory import _body, _events

    codex, _client_module, _registry, _contract, validator_type, profile_type = _modules()
    body = _body(parameters={"type": "object", "properties": {}, "additionalProperties": False})
    profile = profile_type(
        codex_streaming_tool_events=True,
        codex_0149_function_tool_events=True,
        zero_argument_function_names=codex.codex_0149_zero_argument_function_names(body),
        codex_encrypted_reasoning_replay=False,
        declared_client_tools=codex.codex_0149_declared_tool_taxonomy(body),
        codex_reasoning_events=True,
    )
    validator = validator_type(profile)
    events = _events(arguments="", include_argument_events=False)
    events[3], events[2] = events[2], events[3]
    assert not all(validator.validate(event) for event in events)
