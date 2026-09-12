"""Focused tests for the pinned Gateway162 validator profile handoff."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, cast

import httpx
import pytest

from scripts.gateway_accounting_rehearsal import (
    _gateway_stream_validator_factory,
    _TerminalValidationDiscriminator,
)

_GATEWAY_ROOT = os.environ.get("SLAIF_GATEWAY_ROOT")
pytestmark = pytest.mark.skipif(
    _GATEWAY_ROOT is None,
    reason="SLAIF_GATEWAY_ROOT is required for the exact Gateway162 focused tests",
)


def _body(*, parameters: dict[str, object], stream: bool = True) -> dict[str, object]:
    return {
        "model": "qwen3.8-27b",
        "stream": stream,
        "tools": [
            {
                "type": "function",
                "name": "local_lookup",
                "description": "bounded focused test function",
                "parameters": parameters,
                "strict": True,
            }
        ],
    }


def _events(*, arguments: str, include_argument_events: bool) -> list[dict[str, object]]:
    events: list[dict[str, object]] = [
        {
            "type": "response.created",
            "sequence_number": 0,
            "response": {
                "id": "response-1",
                "status": "in_progress",
                "model": "qwen3.8-27b",
            },
        },
        {
            "type": "response.in_progress",
            "sequence_number": 1,
            "response": {"id": "response-1", "status": "in_progress"},
        },
        {
            "type": "response.output_item.added",
            "output_index": 0,
            "sequence_number": 2,
            "item": {
                "type": "function_call",
                "id": "item-1",
                "call_id": "call-1",
                "namespace": None,
                "caller": None,
                "name": "local_lookup",
                "arguments": "",
                "status": "in_progress",
            },
        },
    ]
    if include_argument_events:
        events.extend(
            [
                {
                    "type": "response.function_call_arguments.delta",
                    "item_id": "item-1",
                    "output_index": 0,
                    "sequence_number": 3,
                    "delta": arguments,
                },
                {
                    "type": "response.function_call_arguments.done",
                    "item_id": "item-1",
                    "output_index": 0,
                    "sequence_number": 4,
                    "name": "local_lookup",
                    "arguments": arguments,
                },
            ]
        )
    done_sequence = 5 if include_argument_events else 3
    completed_sequence = 6 if include_argument_events else 4
    events.extend(
        [
            {
                "type": "response.output_item.done",
                "output_index": 0,
                "sequence_number": done_sequence,
                "item": {
                    "type": "function_call",
                    "id": "item-1",
                    "call_id": "call-1",
                    "namespace": None,
                    "caller": None,
                    "name": "local_lookup",
                    "arguments": arguments,
                    "status": "completed",
                },
            },
            {
                "type": "response.completed",
                "sequence_number": completed_sequence,
                "response": {
                    "id": "response-1",
                    "status": "completed",
                    "output": [
                        {
                            "type": "function_call",
                            "id": "summary-1",
                            "call_id": "call-1",
                            "namespace": None,
                            "name": "local_lookup",
                            "arguments": arguments,
                            "status": "completed",
                        }
                    ],
                    "usage": {
                        "input_tokens": 1,
                        "input_tokens_details": {
                            "cached_tokens": 0,
                            "input_tokens_per_turn": [1],
                            "cached_tokens_per_turn": [0],
                        },
                        "output_tokens": 1,
                        "output_tokens_details": {
                            "reasoning_tokens": 0,
                            "tool_output_tokens": 0,
                            "output_tokens_per_turn": [1],
                            "tool_output_tokens_per_turn": [0],
                        },
                        "total_tokens": 2,
                    },
                },
            },
        ]
    )
    return events


def _validator(body: dict[str, object]) -> Any:
    assert _GATEWAY_ROOT is not None
    request = httpx.Request(
        "POST",
        "http://gateway.test/v1/responses",
        headers={"content-type": "application/json"},
        content=json.dumps(body, separators=(",", ":")).encode("utf-8"),
    )
    return _gateway_stream_validator_factory(Path(_GATEWAY_ROOT))(request)


def _validated(
    body: dict[str, object], events: list[dict[str, object]]
) -> tuple[tuple[bool, ...], int]:
    validator = _validator(body)
    results = tuple(validator.validate(event) for event in events)
    candidates = validator.take_replay_reference_candidates()
    return results, len(candidates)


def _empty_parameters() -> dict[str, object]:
    return {"type": "object", "properties": {}, "additionalProperties": False}


def test_gateway162_factory_propagates_eligible_zero_argument_names() -> None:
    body = _body(parameters=_empty_parameters())
    validator = _validator(body)
    assert validator.profile.zero_argument_function_names == frozenset({"local_lookup"})

    results, candidate_count = _validated(
        body, _events(arguments="", include_argument_events=False)
    )
    assert all(results)
    assert candidate_count == 1


def test_gateway162_factory_preserves_canonical_argument_lifecycle() -> None:
    body = _body(parameters=_empty_parameters())
    results, candidate_count = _validated(
        body, _events(arguments="{}", include_argument_events=True)
    )
    assert all(results)
    assert candidate_count == 1


@pytest.mark.parametrize(
    "body",
    (
        _body(
            parameters={
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "additionalProperties": False,
                "required": ["value"],
            }
        ),
        _body(parameters=_empty_parameters(), stream=False),
    ),
)
def test_gateway162_factory_rejects_ineligible_omission(body: dict[str, object]) -> None:
    validator = _validator(body)
    assert validator.profile.zero_argument_function_names == frozenset()
    results, candidate_count = _validated(
        body, _events(arguments="", include_argument_events=False)
    )
    assert not all(results)
    assert candidate_count == 0


def test_gateway162_factory_rejects_malformed_request() -> None:
    assert _GATEWAY_ROOT is not None
    factory = _gateway_stream_validator_factory(Path(_GATEWAY_ROOT))
    request = httpx.Request(
        "POST",
        "http://gateway.test/v1/responses",
        headers={"content-type": "application/json"},
        content=b"{",
    )
    with pytest.raises(ValueError, match="validator_profile_request_invalid"):
        factory(request)


def test_terminal_discriminator_traces_exact_positive_and_negative_terminal_cases() -> None:
    assert _GATEWAY_ROOT is not None
    body = _body(parameters=_empty_parameters())
    request = httpx.Request(
        "POST",
        "http://gateway.test/v1/responses",
        headers={"content-type": "application/json"},
        content=json.dumps(body, separators=(",", ":")).encode("utf-8"),
    )

    positive_discriminator = _TerminalValidationDiscriminator()
    positive = _gateway_stream_validator_factory(
        Path(_GATEWAY_ROOT), terminal_discriminator=positive_discriminator
    )(request)
    assert all(
        positive.validate(event) for event in _events(arguments="", include_argument_events=False)
    )
    positive_entry = positive_discriminator.safe_dict()["invocations"][-1]  # type: ignore[index]
    assert positive_entry["validator_result_class"] == "true"  # type: ignore[index]
    positive_trace = positive_entry["return_sites"]  # type: ignore[index]
    positive_functions = {row["function"] for row in positive_trace}  # type: ignore[union-attr]
    assert {
        "validate",
        "_validate_codex_response_event",
        "_validate_response_completed_event",
        "_validate_completed_usage",
        "_validate_codex_completed_output",
        "_validate_codex_completed_output_item",
        "_accept_strict_sequence",
    } <= positive_functions
    assert all(row["return_class"] == "true" for row in positive_trace)  # type: ignore[union-attr]
    assert positive_entry["shape_before"]["sequence_valid_before_call"] is True  # type: ignore[index]
    assert positive_entry["shape_after"]["sequence_valid_before_call"] is False  # type: ignore[index]
    assert positive_entry["shape_before"]["function_arguments"]["class"] == "empty"  # type: ignore[index]

    negative_discriminator = _TerminalValidationDiscriminator()
    negative = _gateway_stream_validator_factory(
        Path(_GATEWAY_ROOT), terminal_discriminator=negative_discriminator
    )(request)
    negative_events = _events(arguments="", include_argument_events=False)
    terminal = cast(dict[str, object], negative_events[-1]["response"])
    negative_events[-1] = {
        **negative_events[-1],
        "response": {
            **terminal,
            "usage": {
                **cast(dict[str, object], terminal["usage"]),
                "total_tokens": 99,
            },
        },
    }
    assert all(negative.validate(event) for event in negative_events[:-1])
    assert negative.validate(negative_events[-1]) is False
    negative_entry = negative_discriminator.safe_dict()["invocations"][-1]  # type: ignore[index]
    assert negative_entry["validator_result_class"] == "false"  # type: ignore[index]
    assert negative_entry["shape_before"]["usage_total_consistent"] is False  # type: ignore[index]
    negative_trace = negative_entry["return_sites"]  # type: ignore[index]
    assert any(
        row["function"] == "_validate_completed_usage" and row["return_class"] == "false"
        for row in negative_trace  # type: ignore[union-attr]
    )


@pytest.mark.parametrize("failure", ("identity", "order", "terminal"))
def test_gateway162_factory_rejects_invalid_lifecycle_identity_and_terminal(
    failure: str,
) -> None:
    body = _body(parameters=_empty_parameters())
    events = _events(arguments="", include_argument_events=False)
    if failure == "identity":
        item = cast(dict[str, object], events[3]["item"])
        events[3] = {**events[3], "item": {**item, "call_id": "wrong-call"}}
    elif failure == "order":
        events[3], events[2] = events[2], events[3]
    else:
        response = cast(dict[str, object], events[4]["response"])
        events[4] = {**events[4], "response": {**response, "id": "wrong-response"}}
    results, candidate_count = _validated(body, events)
    assert not all(results)
    assert candidate_count == (1 if failure == "terminal" else 0)
