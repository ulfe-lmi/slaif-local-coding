import pytest

from slaif_local_coding.json_structure import JsonNestingTooDeep, enforce_json_nesting


@pytest.mark.parametrize(
    ("raw", "maximum"),
    [
        (b"{}", 1),
        (b"[]", 1),
        (b'{"a":[]}', 2),
        (b'[{"a":[{}]}]', 4),
        (rb'{"text":"[{\\\"quoted\\\": \"} ]\"}"}', 1),
        (b'{"empty":{"array":[],"object":{}}}', 3),
    ],
)
def test_nesting_measurement_accepts_exact_depth(raw: bytes, maximum: int) -> None:
    enforce_json_nesting(raw, maximum)


@pytest.mark.parametrize("raw", [b"[[]]", b'{"a":{}}', b'[{"a":[]}]'])
def test_nesting_measurement_rejects_depth_plus_one(raw: bytes) -> None:
    with pytest.raises(JsonNestingTooDeep):
        enforce_json_nesting(raw, 1)
