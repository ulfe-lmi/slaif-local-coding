"""Pure route-scoped image counting and transformation.

Structural contract (established by order 014-a, workstream A):

- A *supported image item* is a dict that is a direct element of a JSON
  array and whose ``type`` value is a **string** exactly equal to one of
  ``IMAGE_TYPES`` (Responses ``input_image`` or Chat ``image_url``).
- A ``type`` value that is not a string (dict, list, int, float, bool, or
  null) is never an image marker and is never compared against — and thus
  never hashed into — ``IMAGE_TYPES``. Nested JSON Schema values whose
  property happens to be named ``type`` (for example inside Codex
  namespace-tool parameter schemas) are therefore preserved byte-for-byte.
  This is the RC2 compatibility repair: the previous implementation
  evaluated ``node.get("type") in IMAGE_TYPES`` unconditionally and raised
  ``TypeError: unhashable type: 'dict'`` on such envelopes before any
  image or route policy could be applied.
- A supported string marker at a non-list position (top level, or a value
  under a key) is genuinely ambiguous and fails closed with
  ``AmbiguousImageShape`` (the app maps it to HTTP 422), unchanged from
  before the repair.
- A list-element dict carrying a supported string marker is a supported
  image item even when bare (no ``image_url`` payload): that is the
  established counting contract, so zero/one/multiple, newest retention,
  maximum-zero, and passthrough/reject/retain-newest route behavior stay
  identical for every payload the previous implementation could process.
- The walker removes and reorders nothing except explicit image content
  items dropped by an enforcing route policy; every other value, key
  order, and nesting is preserved in the returned deep copy.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

IMAGE_TYPES = frozenset({"input_image", "image_url"})


class AmbiguousImageShape(ValueError):
    """Raised when an image marker cannot be safely treated as a content item."""


@dataclass(frozen=True)
class ImageResult:
    value: Any
    seen: int
    removed: int


def _is_supported_image_marker(node: dict[str, Any]) -> bool:
    """True iff ``node`` carries a supported *string* image marker.

    Only string markers are compared against ``IMAGE_TYPES``; a dict or
    list marker is unhashable, so comparing it would raise ``TypeError``,
    and any other non-string marker is not an image marker by contract.
    """
    marker = node.get("type")
    return isinstance(marker, str) and marker in IMAGE_TYPES


def apply_retain_newest(value: Any, maximum: int) -> ImageResult:
    """Return a copy retaining the newest supported list image item."""
    transformed = copy.deepcopy(value)
    slots: list[tuple[list[Any], int]] = []

    def walk(node: Any, parent: Any = None) -> None:
        if isinstance(node, list):
            for index, item in enumerate(node):
                if isinstance(item, dict) and _is_supported_image_marker(item):
                    slots.append((node, index))
                walk(item, node)
        elif isinstance(node, dict):
            if _is_supported_image_marker(node) and not isinstance(parent, list):
                raise AmbiguousImageShape("supported image marker must be a list content item")
            for item in node.values():
                walk(item, node)

    walk(transformed)
    remove_count = max(0, len(slots) - maximum)
    for parent, index in reversed(slots[:remove_count]):
        del parent[index]
    return ImageResult(transformed, len(slots), remove_count)


def count_images(value: Any) -> int:
    return apply_retain_newest(value, 2**31 - 1).seen
