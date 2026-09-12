"""Unit coverage for the disposable no-model tool-type capture boundary."""

from __future__ import annotations

import pytest

from tests.helpers.capture_codex_tool_types import _extract_types


def test_capture_accepts_only_bounded_safe_top_level_type_labels() -> None:
    observed = ("function", "function", "custom", "tool_search", "web_search")
    payload = {
        "tools": [
            {"type": marker, "name": "discarded", "parameters": {"secret": "discarded"}}
            for marker in observed
        ]
    }
    assert _extract_types(payload) == observed
    assert "discarded" not in repr(_extract_types(payload))


@pytest.mark.parametrize(
    "payload",
    [
        {"tools": []},
        {"tools": [{"type": "Function"}]},
        {"tools": [{"type": ""}]},
        {"tools": [{"type": "function/extra"}]},
        {"tools": [{"type": 1}]},
        {"tools": [{"type": "function"}, {}]},
        {"tools": {"type": "function"}},
    ],
)
def test_capture_rejects_malformed_or_unbounded_type_shapes(payload: object) -> None:
    with pytest.raises(ValueError):
        _extract_types(payload)


def test_capture_rejects_definition_and_unique_type_bounds() -> None:
    with pytest.raises(ValueError):
        _extract_types({"tools": [{"type": "function"}] * 17})
    too_many_unique = [{"type": f"type_{index}"} for index in range(17)]
    with pytest.raises(ValueError):
        _extract_types({"tools": too_many_unique})


def test_capture_can_record_an_empty_tools_envelope() -> None:
    assert _extract_types({"tools": []}, require_nonempty=False) == ()


def test_capture_does_not_return_tool_data() -> None:
    result = _extract_types(
        {
            "tools": [
                {
                    "type": "custom",
                    "name": "private-name",
                    "description": "private-description",
                    "schema": {"secret": "private-schema"},
                }
            ]
        }
    )
    assert result == ("custom",)
    assert all(
        forbidden not in repr(result)
        for forbidden in ("private-name", "private-description", "private-schema")
    )
