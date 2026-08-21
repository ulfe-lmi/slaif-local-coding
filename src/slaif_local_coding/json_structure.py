"""Bounded validation for JSON container nesting before recursive parsing."""

from __future__ import annotations


class JsonNestingTooDeep(ValueError):
    """Raised when raw JSON exceeds the configured container nesting limit."""


def enforce_json_nesting(raw: bytes, maximum: int) -> None:
    """Reject container nesting over ``maximum`` while respecting JSON strings.

    Full syntax validation remains the JSON decoder's responsibility. This bounded,
    iterative pre-scan ensures that decoder and transformation recursion only sees
    structures within the application contract.
    """
    depth = 0
    in_string = False
    escaped = False
    for byte in raw:
        if in_string:
            if escaped:
                escaped = False
            elif byte == 0x5C:  # backslash
                escaped = True
            elif byte == 0x22:  # double quote
                in_string = False
            continue
        if byte == 0x22:
            in_string = True
        elif byte in (0x5B, 0x7B):  # [ {
            depth += 1
            if depth > maximum:
                raise JsonNestingTooDeep
        elif byte in (0x5D, 0x7D) and depth > 0:  # ] }
            depth -= 1
