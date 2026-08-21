"""Pure route-scoped image counting and transformation."""

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


def apply_retain_newest(value: Any, maximum: int) -> ImageResult:
    """Return a copy retaining the newest supported list image item."""
    transformed = copy.deepcopy(value)
    slots: list[tuple[list[Any], int]] = []

    def walk(node: Any, parent: Any = None) -> None:
        if isinstance(node, list):
            for index, item in enumerate(node):
                if isinstance(item, dict) and item.get("type") in IMAGE_TYPES:
                    slots.append((node, index))
                walk(item, node)
        elif isinstance(node, dict):
            if node.get("type") in IMAGE_TYPES and not isinstance(parent, list):
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
