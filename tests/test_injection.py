"""Focused endpoint-scoped idempotent injection tests."""

from __future__ import annotations

import copy
from typing import Any

import pytest

from slaif_local_coding.constitution.injection import (
    ConstitutionInjectionError,
    InjectionOutcome,
    inject_chat_completions,
    inject_responses,
)
from slaif_local_coding.constitution.working_set import (
    WorkingSetMetadata,
    WorkingSetPolicy,
    select_working_set,
)
from tests.test_working_set import acquired, base_root


def working_set() -> Any:
    return select_working_set(
        base_root(), acquired(), policy=WorkingSetPolicy(), metadata=WorkingSetMetadata()
    )


def responses_payload() -> dict[str, Any]:
    return {
        "model": "qwen",
        "metadata": {"opaque": "value"},
        "input": [
            {"role": "user", "content": [{"type": "input_text", "text": "private"}]},
            {"type": "input_image", "image_url": "older-image"},
            {"type": "input_image", "image_url": "newest-image"},
        ],
        "stream": False,
    }


def chat_payload() -> dict[str, Any]:
    return {
        "model": "qwen",
        "tools": [{"type": "function"}],
        "messages": [
            {"role": "system", "content": "existing"},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": "old"}}]},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": "new"}}]},
        ],
    }


def test_responses_insert_combine_preserves_images_and_envelope() -> None:
    original = responses_payload()
    snapshot = copy.deepcopy(original)
    transformed, result = inject_responses(original, working_set(), max_depth=64, max_nodes=10_000)
    assert original == snapshot
    assert result.endpoint == "/v1/responses"
    assert result.outcome == InjectionOutcome.INSERTED
    assert result.included_dependencies == 4
    assert result.missing_dependencies == 1
    assert result.omitted_dependencies == 1
    assert transformed["model"] == "qwen"
    assert transformed["metadata"] == snapshot["metadata"]
    assert transformed["input"] == snapshot["input"]
    assert transformed["instructions"].startswith("<SLAIF_RECONSTRUCTED_CONSTITUTION ")
    assert transformed["instructions"].endswith("</SLAIF_RECONSTRUCTED_CONSTITUTION>")

    combined, combined_result = inject_responses(
        {**snapshot, "instructions": "client instructions"},
        working_set(),
        max_depth=64,
        max_nodes=10_000,
    )
    assert combined_result.outcome == InjectionOutcome.UPDATED
    assert combined["instructions"].endswith("\n\nclient instructions")


def test_responses_repeated_injection_is_idempotent() -> None:
    first, first_result = inject_responses(
        responses_payload(), working_set(), max_depth=64, max_nodes=10_000
    )
    second, second_result = inject_responses(first, working_set(), max_depth=64, max_nodes=10_000)
    assert second_result.outcome == InjectionOutcome.IDEMPOTENT
    assert second == first
    assert first_result.outcome != InjectionOutcome.IDEMPOTENT


def test_chat_inserts_earliest_system_without_message_mutation() -> None:
    original = chat_payload()
    snapshot = copy.deepcopy(original)
    transformed, result = inject_chat_completions(
        original, working_set(), max_depth=64, max_nodes=10_000
    )
    assert original == snapshot
    assert result.endpoint == "/v1/chat/completions"
    assert result.outcome == InjectionOutcome.INSERTED
    assert len(transformed["messages"]) == len(snapshot["messages"]) + 1
    assert transformed["messages"][0]["role"] == "system"
    assert transformed["messages"][1:] == snapshot["messages"]
    assert transformed["tools"] == snapshot["tools"]
    images = [
        item
        for message in transformed["messages"]
        if isinstance(message.get("content"), list)
        for item in message["content"]
        if item.get("type") == "image_url"
    ]
    assert [item["image_url"]["url"] for item in images] == ["old", "new"]

    repeated, repeated_result = inject_chat_completions(
        transformed, working_set(), max_depth=64, max_nodes=10_000
    )
    assert repeated_result.outcome == InjectionOutcome.IDEMPOTENT
    assert repeated == transformed


def test_conflicting_duplicate_malformed_markers_fail_closed() -> None:
    ws = working_set()
    changed_ws = working_set().model_copy(
        update={"rendered_text": ws.rendered_text.replace("MUST", "SHOULD")}
    )
    injected, _ = inject_responses(responses_payload(), ws, max_depth=64, max_nodes=10_000)
    with pytest.raises(ConstitutionInjectionError) as conflicting:
        inject_responses(injected, changed_ws, max_depth=64, max_nodes=10_000)
    assert conflicting.value.reason.value == "conflicting_marker"

    duplicated = copy.deepcopy(injected)
    duplicated["input"].append({"text": ws.rendered_text})
    with pytest.raises(ConstitutionInjectionError) as duplicate:
        inject_responses(duplicated, ws, max_depth=64, max_nodes=10_000)
    assert duplicate.value.reason.value == "duplicate_marker"

    with pytest.raises(ConstitutionInjectionError) as malformed:
        inject_responses(
            {"input": [{"text": "<SLAIF_RECONSTRUCTED_CONSTITUTION"}]},
            ws,
            max_depth=64,
            max_nodes=10_000,
        )
    assert malformed.value.reason.value == "malformed_marker"

    shifted_chat = chat_payload()
    shifted_chat["messages"].insert(0, {"role": "system", "content": "newer"})
    shifted_chat["messages"][1]["content"] = ws.rendered_text
    with pytest.raises(ConstitutionInjectionError) as unexpected:
        inject_chat_completions(shifted_chat, ws, max_depth=64, max_nodes=10_000)
    assert unexpected.value.reason.value == "conflicting_marker"


@pytest.mark.parametrize(
    ("transform", "payload"),
    [
        (inject_responses, {"instructions": []}),
        (inject_chat_completions, {"messages": "ambiguous"}),
        (inject_chat_completions, {"messages": [{"role": "user"}, "ambiguous"]}),
    ],
)
def test_unsupported_shapes_fail_closed(transform: Any, payload: dict[str, Any]) -> None:
    with pytest.raises(ConstitutionInjectionError) as exc_info:
        transform(payload, working_set(), max_depth=64, max_nodes=10_000)
    assert exc_info.value.reason.value == "unsupported_shape"


def test_injection_bounds_are_enforced() -> None:
    with pytest.raises(ConstitutionInjectionError) as depth:
        inject_responses(responses_payload(), working_set(), max_depth=1, max_nodes=10_000)
    assert depth.value.reason.value == "bounds_exceeded"
    with pytest.raises(ConstitutionInjectionError) as nodes:
        inject_responses(responses_payload(), working_set(), max_depth=64, max_nodes=1)
    assert nodes.value.reason.value == "bounds_exceeded"
