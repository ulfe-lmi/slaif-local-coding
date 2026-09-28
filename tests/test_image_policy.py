from pathlib import Path

from slaif_local_coding.image_policy import (
    IMAGE_TYPES,
    AmbiguousImageShape,
    apply_retain_newest,
    count_images,
)


def test_zero_and_one_are_equal_but_copied() -> None:
    for value in (
        {"input": [{"type": "text", "text": "x"}]},
        {"input": [{"type": "input_image", "image_url": "safe"}]},
    ):
        result = apply_retain_newest(value, 1)
        assert result.value == value
        assert result.removed == 0


def test_nested_responses_retains_newest_and_order() -> None:
    value = {
        "input": [
            {
                "content": [
                    {"type": "input_image", "image_url": "old"},
                    {"type": "input_text", "text": "between"},
                ]
            },
            {
                "content": [
                    {"type": "input_image", "image_url": "new"},
                    {"type": "input_text", "text": "after"},
                ]
            },
        ]
    }
    result = apply_retain_newest(value, 1)
    assert result.seen == 2 and result.removed == 1
    assert result.value["input"][0]["content"] == [{"type": "input_text", "text": "between"}]
    assert result.value["input"][1]["content"][0]["image_url"] == "new"


def test_chat_shape_and_ambiguous_marker() -> None:
    value = {
        "messages": [
            {
                "content": [
                    {"type": "image_url", "image_url": {"url": "old"}},
                    "text",
                    {"type": "image_url", "image_url": {"url": "new"}},
                ]
            }
        ]
    }
    assert (
        apply_retain_newest(value, 1).value["messages"][0]["content"][1]["image_url"]["url"]
        == "new"
    )
    try:
        apply_retain_newest({"type": "input_image", "image_url": "x"}, 1)
    except AmbiguousImageShape:
        pass
    else:
        raise AssertionError("ambiguous image marker accepted")


# --- Order 014-a: RC2 real-Codex namespace-tool compatibility regression ---

import json  # noqa: E402  (kept with the regression section for locality)
from typing import Any  # noqa: E402  (kept with the regression section for locality)

NAMESPACE_FIXTURE = (
    Path(__file__).parent / "fixtures" / "codex" / "0.149.0" / "namespace_tool_responses.json"
)


def namespace_fixture() -> dict[str, Any]:
    return json.loads(NAMESPACE_FIXTURE.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def _order_preserved(before: object, after: object) -> bool:
    return json.dumps(before, sort_keys=False) == json.dumps(after, sort_keys=False)


def test_rc2_ledger_reproducer_is_accepted_and_preserved() -> None:
    payload = namespace_fixture()
    assert count_images(payload) == 0
    result = apply_retain_newest(payload, 1)
    assert (result.seen, result.removed) == (0, 0)
    assert result.value == payload
    assert _order_preserved(payload, result.value)


def test_rc2_ledger_reproducer_tools_survive_enforcement() -> None:
    payload = namespace_fixture()
    payload["input"].extend(
        [
            {"type": "input_image", "image_url": "older-synthetic"},
            {"type": "input_image", "image_url": "newest-synthetic"},
        ]
    )
    result = apply_retain_newest(payload, 1)
    assert (result.seen, result.removed) == (2, 1)
    kept = [item for item in result.value["input"] if item.get("type") == "input_image"]
    assert kept == [{"type": "input_image", "image_url": "newest-synthetic"}]
    assert result.value["tools"] == namespace_fixture()["tools"]
    assert _order_preserved([t for t in namespace_fixture()["tools"]], result.value["tools"])


def test_non_string_nested_type_values_never_crash_or_mutate() -> None:
    for marker in (
        {"description": "entry classification marker", "type": "string"},
        ["string", "null"],
        None,
        True,
        False,
        0,
        3,
        0.5,
        1e3,
    ):
        value = {
            "tools": [
                {
                    "type": "namespace",
                    "name": "ns",
                    "tools": [
                        {
                            "type": "function",
                            "name": "fn",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "items": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {"type": marker},
                                        },
                                    }
                                },
                            },
                        }
                    ],
                }
            ]
        }
        assert count_images(value) == 0
        result = apply_retain_newest(value, 0)
        assert (result.seen, result.removed) == (0, 0)
        assert result.value == value
        assert _order_preserved(value, result.value)


def test_only_exact_supported_string_markers_are_image_markers() -> None:
    for marker in ("Input_Image", "input_image ", " image_url", "image-URL", "input_image0"):
        value = {"input": [{"type": marker, "image_url": "x"}]}
        assert count_images(value) == 0
        assert apply_retain_newest(value, 0).value == value
    for marker in sorted(IMAGE_TYPES):
        assert count_images({"input": [{"type": marker}]}) == 1


def test_realistic_nested_json_schema_is_preserved_including_order() -> None:
    payload = namespace_fixture()
    result = apply_retain_newest(payload, 0)
    assert result.seen == 0
    assert _order_preserved(payload, result.value)
    ns = result.value["tools"][5]
    for index in (2, 3):
        schema_type = ns["tools"][index]["parameters"]["properties"]["items"]["items"][
            "properties"
        ]["type"]
        assert (
            schema_type
            == payload["tools"][5]["tools"][index]["parameters"]["properties"]["items"]["items"][
                "properties"
            ]["type"]
        )


def test_maximum_zero_removes_all_images_and_preserves_everything_else() -> None:
    value = {
        "input": [
            {"type": "input_text", "text": "keep"},
            {"type": "input_image", "image_url": "one"},
            {"type": "input_image", "image_url": "two"},
            {"type": "function_call", "call_id": "c", "name": "f", "arguments": "{}"},
        ]
    }
    result = apply_retain_newest(value, 0)
    assert (result.seen, result.removed) == (2, 2)
    assert result.value["input"] == [
        {"type": "input_text", "text": "keep"},
        {"type": "function_call", "call_id": "c", "name": "f", "arguments": "{}"},
    ]
