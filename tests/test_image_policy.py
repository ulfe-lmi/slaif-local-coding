from slaif_local_coding.image_policy import AmbiguousImageShape, apply_retain_newest


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
