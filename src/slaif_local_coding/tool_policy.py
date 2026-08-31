"""Bounded route-scoped Responses tool declaration policies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

DISABLED_CODEX_TOOL_TYPES = frozenset({"tool_search", "web_search"})
RESPONSES_TOOL_POLICY_VERSION = "responses-tool-policy-v1"
MAX_RESPONSES_TOOL_DECLARATIONS = 128
MAX_TOOL_TYPE_BYTES = 256
MAX_TOOL_CHOICE_NODES = 512
MAX_TOOL_CHOICE_STRING_BYTES = 4096

ToolPolicyOutcome = Literal["passthrough", "unchanged", "transformed"]


@dataclass(frozen=True)
class ToolPolicyResult:
    """Safe result and fixed telemetry facts for one route policy application."""

    payload: dict[str, Any]
    observed_count: int
    removed_count: int
    outcome: ToolPolicyOutcome
    reason: str
    changed: bool


class ResponsesToolPolicyError(ValueError):
    """A malformed or semantically unsafe request for the selected policy."""

    def __init__(self, *, code: str, reason: str, message: str, observed_count: int = 0) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.message = message
        self.observed_count = observed_count


def _bounded_string(value: object, *, maximum: int) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        return len(value.encode("utf-8")) <= maximum
    except UnicodeEncodeError:
        return False


def _choice_references_disabled_tool(choice: object, *, disabled_names: frozenset[str]) -> bool:
    """Find only explicit type/name references in a bounded tool-choice object."""
    if isinstance(choice, str):
        return choice in DISABLED_CODEX_TOOL_TYPES or choice in disabled_names
    pending: list[object] = [choice]
    visited = 0
    while pending:
        current = pending.pop()
        visited += 1
        if visited > MAX_TOOL_CHOICE_NODES:
            raise ResponsesToolPolicyError(
                code="responses_tool_policy_invalid",
                reason="tool_choice_too_large",
                message="tool_choice exceeds the configured policy bound",
            )
        if isinstance(current, dict):
            for key, value in current.items():
                if not isinstance(key, str):
                    raise ResponsesToolPolicyError(
                        code="responses_tool_policy_invalid",
                        reason="tool_choice_malformed",
                        message="tool_choice must be a bounded object",
                    )
                if key in {"type", "name", "tool"} and isinstance(value, str):
                    if value in DISABLED_CODEX_TOOL_TYPES or value in disabled_names:
                        return True
                if isinstance(value, (dict, list)):
                    pending.append(value)
                elif isinstance(value, str) and not _bounded_string(
                    value, maximum=MAX_TOOL_CHOICE_STRING_BYTES
                ):
                    raise ResponsesToolPolicyError(
                        code="responses_tool_policy_invalid",
                        reason="tool_choice_malformed",
                        message="tool_choice contains an oversized string",
                    )
        elif isinstance(current, list):
            pending.extend(reversed(current))
        elif isinstance(current, str) and not _bounded_string(
            current, maximum=MAX_TOOL_CHOICE_STRING_BYTES
        ):
            raise ResponsesToolPolicyError(
                code="responses_tool_policy_invalid",
                reason="tool_choice_malformed",
                message="tool_choice contains an oversized string",
            )
    return False


def _choice_is_automatic(choice: object) -> bool:
    if isinstance(choice, str) and choice in {"auto", "none"}:
        return True
    if not isinstance(choice, dict):
        return False
    choice_type = choice.get("type")
    mode = choice.get("mode")
    automatic_mode = isinstance(mode, str) and mode in {"auto", "none"}
    automatic_type = isinstance(choice_type, str) and choice_type in {"auto", "none"}
    return (choice_type == "allowed_tools" and automatic_mode) or automatic_type


def apply_responses_tool_policy(
    payload: dict[str, Any], policy: Literal["passthrough", "drop_disabled_codex_search"]
) -> ToolPolicyResult:
    """Apply one explicit, bounded Responses top-level tool policy.

    The function does not mutate payload. A passthrough or no-op result
    intentionally returns the original object so callers can retain exact
    request bytes.
    """
    if policy == "passthrough":
        return ToolPolicyResult(payload, 0, 0, "passthrough", "policy_passthrough", False)

    if "tools" not in payload:
        return ToolPolicyResult(payload, 0, 0, "unchanged", "no_tools", False)
    raw_tools = payload["tools"]
    if not isinstance(raw_tools, list):
        raise ResponsesToolPolicyError(
            code="responses_tool_policy_invalid",
            reason="tools_not_list",
            message="tools must be a bounded list",
        )
    if len(raw_tools) > MAX_RESPONSES_TOOL_DECLARATIONS:
        raise ResponsesToolPolicyError(
            code="responses_tool_policy_invalid",
            reason="tools_too_large",
            message="tools exceeds the configured policy bound",
        )

    kept: list[object] = []
    disabled_names: set[str] = set()
    removed_count = 0
    for tool in raw_tools:
        if not isinstance(tool, dict):
            raise ResponsesToolPolicyError(
                code="responses_tool_policy_invalid",
                reason="tool_declaration_malformed",
                message="each tool declaration must be a bounded object",
                observed_count=len(raw_tools),
            )
        tool_type = tool.get("type")
        if not _bounded_string(tool_type, maximum=MAX_TOOL_TYPE_BYTES):
            raise ResponsesToolPolicyError(
                code="responses_tool_policy_invalid",
                reason="tool_declaration_malformed",
                message="each tool declaration needs a bounded type",
                observed_count=len(raw_tools),
            )
        if tool_type in DISABLED_CODEX_TOOL_TYPES:
            removed_count += 1
            name = tool.get("name")
            if isinstance(name, str) and _bounded_string(name, maximum=MAX_TOOL_TYPE_BYTES):
                disabled_names.add(name)
        else:
            kept.append(tool)

    observed_count = len(raw_tools)
    if removed_count == 0:
        return ToolPolicyResult(payload, observed_count, 0, "unchanged", "no_disabled_tools", False)

    if "tool_choice" in payload:
        choice = payload["tool_choice"]
        if not isinstance(choice, (str, dict)):
            raise ResponsesToolPolicyError(
                code="responses_tool_policy_invalid",
                reason="tool_choice_malformed",
                message="tool_choice must be a bounded string or object",
                observed_count=observed_count,
            )
        if isinstance(choice, str) and not _bounded_string(
            choice, maximum=MAX_TOOL_CHOICE_STRING_BYTES
        ):
            raise ResponsesToolPolicyError(
                code="responses_tool_policy_invalid",
                reason="tool_choice_malformed",
                message="tool_choice must be a bounded string",
                observed_count=observed_count,
            )
        if _choice_references_disabled_tool(choice, disabled_names=frozenset(disabled_names)):
            raise ResponsesToolPolicyError(
                code="responses_disabled_tool_choice",
                reason="explicit_disabled_tool_choice",
                message="tool_choice selects a disabled Responses tool",
                observed_count=observed_count,
            )
        if not kept and not _choice_is_automatic(choice):
            raise ResponsesToolPolicyError(
                code="responses_disabled_tool_choice",
                reason="required_tool_choice_after_removal",
                message="tool_choice cannot be satisfied after disabled tools are removed",
                observed_count=observed_count,
            )

    transformed = dict(payload)
    if kept:
        transformed["tools"] = kept
    else:
        # Automatic/no-choice requests with no remaining declarations omit tools.
        transformed.pop("tools", None)
    return ToolPolicyResult(
        transformed,
        observed_count,
        removed_count,
        "transformed",
        "disabled_codex_search_removed",
        True,
    )
